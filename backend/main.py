from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime
import os
from strategy import TradingStrategy

app = FastAPI(title="Trading Strategy Simulator", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

class SimulationRequest(BaseModel):
    symbol: str
    start_date: str
    end_date: str
    ma1_window: int
    ma2_window: int

class SimulationResponse(BaseModel):
    success: bool
    data: dict = None
    error: str = None

@app.get("/")
async def root():
    return FileResponse("frontend/index.html")

@app.get("/result")
async def result_page():
    return FileResponse("frontend/result.html")

@app.post("/simulate", response_model=SimulationResponse)
async def simulate_strategy(request: SimulationRequest):
    try:
        # Validate inputs
        if request.ma1_window <= 0 or request.ma2_window <= 0:
            raise ValueError("Moving average windows must be positive")
        
        if request.ma1_window >= request.ma2_window:
            raise ValueError("MA1 window should be smaller than MA2 window")
        
        # Parse dates
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d")
        
        if start_date >= end_date:
            raise ValueError("Start date must be before end date")
        
        # Initialize strategy
        strategy = TradingStrategy(
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
            ma1_window=request.ma1_window,
            ma2_window=request.ma2_window
        )
        
        # Run simulation
        results = strategy.run_simulation()
        
        return SimulationResponse(success=True, data=results)
        
    except ValueError as e:
        return SimulationResponse(success=False, error=str(e))
    except Exception as e:
        return SimulationResponse(success=False, error=f"Simulation failed: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Trading Strategy Simulator API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
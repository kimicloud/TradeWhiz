📈 Moving Average Crossover Trading Simulator
A full-stack web application that simulates a moving average crossover trading strategy using historical stock data. Built with FastAPI, pandas, Plotly.js, and Tailwind CSS. Deployed via Vercel using GitHub integration.

🚀 Live Demo
https://tradewhizz.vercel.app


🧠 Features
🔎 Search stocks by symbol (e.g., TCS.NS, AAPL, INFY.NS)
📆 Choose date range
🔢 Input two moving average windows (e.g., 10, 50)
📈 Visualize crossover points on a candlestick chart
📊 Performance metrics:
Total Return
Sharpe Ratio
Max Drawdown
Win Rate
🛠 Tech Stack
| Layer       | Tool                  |
| ----------- | --------------------- |
| Backend     | FastAPI               |
| Strategy    | pandas + NumPy        |
| Data Source | yfinance              |
| Frontend    | HTML + Tailwind CSS   |
| Charting    | Plotly.js             |
| Deployment  | Vercel (GitHub CI/CD) |



Installation (Local)
1. Clone the repo
git clone https://github.com/yourusername/trading-simulator.git
cd trading-simulator
2. Set up virtual environment
python3 -m venv venv
source venv/bin/activate
3. Install dependencies
pip install -r requirements.txt
4. Run FastAPI server
uvicorn backend.main:app --reload




📈 Strategy Explanation
Moving Average Crossover involves two lines:
MA1: Short-term (e.g., 10-day)
MA2: Long-term (e.g., 50-day)
📌 Buy Signal: when MA1 crosses above MA2
📌 Sell Signal: when MA1 crosses below MA2
📊 Performance Metrics
| Metric       | Description                       |
| ------------ | --------------------------------- |
| Sharpe Ratio | Risk-adjusted return              |
| Max Drawdown | Maximum observed loss from a peak |
| Win Rate     | % of profitable trades            |
| Total Return | Cumulative return from strategy   |

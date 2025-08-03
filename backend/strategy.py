import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime

class TradingStrategy:
    def __init__(self, symbol: str, start_date: str, end_date: str, ma1_window: int, ma2_window: int):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.ma1_window = ma1_window
        self.ma2_window = ma2_window
        self.data = None
        self.signals = None
        
    def fetch_data(self) -> pd.DataFrame:
        """Fetch historical stock data using yfinance"""
        try:
            ticker = yf.Ticker(self.symbol)
            data = ticker.history(start=self.start_date, end=self.end_date)
            
            if data.empty:
                raise ValueError(f"No data found for symbol {self.symbol}")
            
            return data
        except Exception as e:
            raise ValueError(f"Failed to fetch data for {self.symbol}: {str(e)}")
    
    def calculate_moving_averages(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate moving averages and generate signals"""
        df = data.copy()
        
        # Calculate moving averages
        df[f'MA{self.ma1_window}'] = df['Close'].rolling(window=self.ma1_window).mean()
        df[f'MA{self.ma2_window}'] = df['Close'].rolling(window=self.ma2_window).mean()
        
        # Generate signals (1 for buy, -1 for sell, 0 for hold)
        df['Signal'] = 0
        df['Signal'][self.ma1_window:] = np.where(
            df[f'MA{self.ma1_window}'][self.ma1_window:] > df[f'MA{self.ma2_window}'][self.ma1_window:], 1, -1
        )
        
        # Find crossover points
        df['Position'] = df['Signal'].diff()
        
        return df
    
    def identify_trades(self, data: pd.DataFrame) -> List[Dict]:
        """Identify buy and sell points"""
        trades = []
        buy_signals = data[data['Position'] == 2]  # Buy signals (1 - (-1) = 2)
        sell_signals = data[data['Position'] == -2]  # Sell signals (-1 - 1 = -2)
        
        # Buy signals
        for idx, row in buy_signals.iterrows():
            trades.append({
                'date': idx.strftime('%Y-%m-%d'),
                'price': round(row['Close'], 2),
                'type': 'buy',
                'ma1': round(row[f'MA{self.ma1_window}'], 2),
                'ma2': round(row[f'MA{self.ma2_window}'], 2)
            })
        
        # Sell signals
        for idx, row in sell_signals.iterrows():
            trades.append({
                'date': idx.strftime('%Y-%m-%d'),
                'price': round(row['Close'], 2),
                'type': 'sell',
                'ma1': round(row[f'MA{self.ma1_window}'], 2),
                'ma2': round(row[f'MA{self.ma2_window}'], 2)
            })
        
        return sorted(trades, key=lambda x: x['date'])
    
    def calculate_metrics(self, data: pd.DataFrame) -> Dict:
        """Calculate trading performance metrics"""
        # Calculate returns
        data['Returns'] = data['Close'].pct_change()
        data['Strategy_Returns'] = data['Returns'] * data['Signal'].shift(1)
        
        # Remove NaN values
        strategy_returns = data['Strategy_Returns'].dropna()
        buy_and_hold_returns = data['Returns'].dropna()
        
        if len(strategy_returns) == 0:
            return {
                'total_return': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'win_rate': 0.0,
                'total_trades': 0
            }
        
        # Total return
        total_return = (1 + strategy_returns).prod() - 1
        buy_hold_return = (1 + buy_and_hold_returns).prod() - 1
        
        # Sharpe ratio (assuming 252 trading days per year)
        if strategy_returns.std() != 0:
            sharpe_ratio = (strategy_returns.mean() / strategy_returns.std()) * np.sqrt(252)
        else:
            sharpe_ratio = 0.0
        
        # Maximum drawdown
        cumulative_returns = (1 + strategy_returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Win rate
        positive_returns = strategy_returns[strategy_returns > 0]
        win_rate = len(positive_returns) / len(strategy_returns) if len(strategy_returns) > 0 else 0
        
        # Count trades
        total_trades = len(data[data['Position'].abs() == 2])
        
        return {
            'total_return': round(total_return * 100, 2),
            'buy_hold_return': round(buy_hold_return * 100, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'max_drawdown': round(abs(max_drawdown) * 100, 2),
            'win_rate': round(win_rate * 100, 2),
            'total_trades': total_trades
        }


    def prepare_chart_data(self, data: pd.DataFrame) -> Dict:
        """Prepare data for Plotly chart (sanitize NaNs)"""
        df = data.copy()

        # Fill NaNs and Infs
        df = df.replace([np.inf, -np.inf], np.nan).fillna(0)

        chart_data = {
            'dates': [d.strftime('%Y-%m-%d') for d in df.index],
            'prices': df['Close'].round(2).tolist(),
            'ma1': df[f'MA{self.ma1_window}'].round(2).tolist(),
            'ma2': df[f'MA{self.ma2_window}'].round(2).tolist(),
            'volume': df['Volume'].astype(float).round(2).tolist()
        }

        return chart_data

    
    def run_simulation(self) -> Dict:
        """Run the complete trading simulation"""
        # Fetch data
        self.data = self.fetch_data()
        
        # Calculate moving averages and signals
        self.data = self.calculate_moving_averages(self.data)
        
        # Identify trades
        trades = self.identify_trades(self.data)
        
        # Calculate metrics
        raw_metrics = self.calculate_metrics(self.data)

        # Sanitize all metric values (ensure no NaN or inf)
        sanitized_metrics = {
            key: float(np.nan_to_num(val, nan=0.0, posinf=0.0, neginf=0.0))
            if isinstance(val, (float, int)) else val
            for key, val in raw_metrics.items()
        }
        
        # Prepare chart data
        chart_data = self.prepare_chart_data(self.data)
        
        return {
            'symbol': self.symbol,
            'period': f"{self.start_date} to {self.end_date}",
            'ma_windows': f"MA{self.ma1_window} / MA{self.ma2_window}",
            'chart_data': chart_data,
            'trades': trades,
            'metrics': sanitized_metrics
        }

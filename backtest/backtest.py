from backtest.utils.position import Position
from backtest.utils.dataretriever import YahooDataRetriever
from backtest.core.strategy import Strategy

import pandas as pd
import numpy as np

class Backtest:
    def __init__(self, tickers, initial_capital=10000, commission=0.001, slippage=0.0, stop_loss_pct=0.02):


        self.data = None
        self.tickers = tickers  # List of tickers or sectors
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.stop_loss_pct = stop_loss_pct  # Percentage for stop loss (default 2%)
        self.positions = {ticker: Position() for ticker in tickers}  # Dictionary of positions for each ticker
        self.orders = []  # Orders executed during the backtest
        self.results = pd.DataFrame(columns=["Date", "Capital", "Cash", "Equity", "Portfolio Value"])

    def execute_order(self, order_type, price, amount, ticker):

        slippage_adjustment = price * self.slippage
        if order_type == 'buy':
            price += slippage_adjustment  # Apply slippage to buy price
            if self.capital >= price * amount:
                stop_loss_price = price * (1 - self.stop_loss_pct)
                self.positions[ticker].buy(price, amount, self.commission, stop_loss=stop_loss_price)
                self.capital -= price * amount * (1 + self.commission)
                self.orders.append({'type': 'buy', 'price': price, 'amount': amount, 'ticker': ticker, 'stop_loss': stop_loss_price})
        elif order_type == 'sell':
            price -= slippage_adjustment  # Apply slippage to sell price
            if self.positions[ticker].size >= amount:
                proceeds = self.positions[ticker].sell(price, amount, self.commission)
                self.capital += proceeds
                self.orders.append({'type': 'sell', 'price': price, 'amount': amount, 'ticker': ticker})

    def run_backtest(self,strategy:Strategy):


        for idx, row in self.data.iterrows():
            # Check for stop loss violation for each ticker
            for ticker in self.tickers:
                if self.positions[ticker].is_open():
                    # Check if the current price hits the stop loss
                    if row[ticker] <= self.positions[ticker].stop_loss:
                        print(f"Stop loss hit for {ticker} at {row['Date']} for price {row[ticker]}")
                        self.execute_order('sell', row[ticker], self.positions[ticker].size, ticker)  # Close the position
                    self.positions[ticker].update_trailing_stop(row[ticker], trailing_stop_pct=0.05)  # 5% trailing stop

            for ticker in self.tickers:
                action = strategy.get_action(row, ticker)  # Get strategy action for each ticker
                if action == 'buy':
                    self.execute_order('buy', row[ticker], amount=1, ticker=ticker)  # Buying 1 unit
                elif action == 'sell':
                    self.execute_order('sell', row[ticker], amount=1, ticker=ticker)  # Selling 1 unit
            
            # Track portfolio status (total capital + value of all positions)
            total_value = sum([self.positions[ticker].get_value(row[ticker]) for ticker in self.tickers])
            equity = self.capital + total_value

            result_entry = {
                "Date": row['Date'],
                "Capital": self.initial_capital,
                "Cash": self.capital,
                "Equity": equity,
                "Portfolio Value": equity
            }

            self.results = self.results.append(result_entry, ignore_index=True)

            yield result_entry

    
    def get_data(self, data):
        self.data = data




    def performance_metrics(self):
        """
        Compute performance metrics like total return, Sharpe ratio, etc.
        """
        total_return = (self.results['Portfolio Value'].iloc[-1] / self.results['Portfolio Value'].iloc[0]) - 1
        print(f"Total Return: {total_return * 100:.2f}%")
        
        # More metrics can be added here (Sharpe, Sortino, etc.)

    
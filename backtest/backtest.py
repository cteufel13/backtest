from backtest.utils.position import Position
from backtest.utils.dataretriever import DataRetriever
from backtest.utils.indicators import *
from backtest.utils.performance import get_performance_metrics,calculate_metrics

from backtest.core.strategy_base import Strategy
from backtest.core.indicator_base import Indicator
from backtest.core.action_base import Action

from backtest.frontend import Frontend

import threading
import time

import pandas as pd
import numpy as np
from typing import Union, List
import webbrowser

class Backtest:
    def __init__(self, initial_capital=10000, commission=0.001, slippage=0.0, stop_loss_pct=0.02,duration=365*10, start_date=None, end_date=None, interval='1h'):

        self.datatretriever = DataRetriever(duration=duration, start_date=start_date, end_date=end_date, interval=interval)
        self.visualizer = Frontend()
      

        self.tickers = None  # List of tickers or sectors

        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.stop_loss_pct = stop_loss_pct  # Percentage for stop loss (default 2%)

        self.positions = None
        self.data = None
        self.orders = []  # Orders executed during the backtest

        self.results = pd.DataFrame(columns=["Date", "Capital", "Cash", "Equity", "Portfolio Value"])
        self.actions = pd.DataFrame(columns=["Date","Ticker" ,"Type", "Amount", "Price", "Stop Loss"])
        self.position_history = pd.DataFrame(columns=["Date","Ticker","Size","Entry Price","Stop Loss"])

        self.performance = pd.DataFrame(columns=["Date"]+get_performance_metrics())
        

        self.ta_indicators = [cls() for cls in Indicator.__subclasses__()]

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

    def run_backtest(self, strategy: Strategy, tickers: Union[str, List[str]], sector: str = None):

        all_dates = self.data[tickers[0]].index

        for ticker in self.tickers:
            all_dates = all_dates.intersection(self.data[ticker].index)

        for i,date in enumerate(all_dates):

            total_value = 0
            actions = {}

            for ticker in self.tickers:
                row = self.data[ticker].loc[date]
                current_price = row['Close']
                if self.positions[ticker].is_open():
                    if current_price <= self.positions[ticker].stop_loss:
                        self.execute_order('sell', current_price, self.positions[ticker].size, ticker)
                    self.positions[ticker].update_stop_loss(current_price, trailing_stop_pct=0.05)

                action = strategy.get_action(row, ticker, self.positions)
                actions[ticker] = action
                if action.type == 'buy':
                    self.execute_order('buy', current_price, action.amount, ticker)
                elif action.type == 'sell':
                    self.execute_order('sell', current_price, action.amount, ticker)

                total_value += self.positions[ticker].get_value(current_price)

                action_entry = {
                "Date": date,
                "Ticker": ticker,
                "Type": action.type,
                "Amount": action.amount,
                "Price": current_price,
                "Stop Loss": self.positions[ticker].stop_loss
                }
                Position_entry = {
                    "Date": date,
                    "Ticker": ticker,
                    "Size": self.positions[ticker].size,
                    "Entry Price": self.positions[ticker].entry_price,
                    "Stop Loss": self.positions[ticker].stop_loss
                }
                self.actions = pd.concat([self.actions, pd.DataFrame([action_entry])], ignore_index=True)
                self.position_history = pd.concat([self.position_history, pd.DataFrame([Position_entry])], ignore_index=True)
            if i != 0:
                metrics_entry = calculate_metrics(date,self.results,self.actions)
            else:
                metrics_entry = dict([('Date', date)] + [(metric, 0) for metric in get_performance_metrics()])
            self.performance = pd.concat([self.performance, pd.DataFrame([metrics_entry])], ignore_index=True)
            

            equity = self.capital + total_value
            # print(actions)
            result_entry = {
                "Date": date,
                "Capital": self.initial_capital,
                "Cash": self.capital,
                "Equity": equity,
                "Portfolio Value": equity,
                "Action": actions,
                "Stock Info": {ticker: self.data[ticker].loc[date] for ticker in self.tickers}
            }
            


            self.results = pd.concat([self.results, pd.DataFrame([result_entry])], ignore_index=True)

            

            
            # Control update timing
            yield result_entry, self.positions , metrics_entry
        
    def get_data(self):
        self.data = self.datatretriever.get_data(self.tickers)
        self.data = self.apply_ta_indicators()
        return self.data

    def apply_ta_indicators(self):
        for indicator in self.ta_indicators:
            for ticker in self.tickers:
                self.data[ticker] = indicator.apply(self.data[ticker])
        return self.data

    def get_tickers(self,tickers=Union[str,List[str]], sector:str =None):
        if sector is not None:
            self.tickers = self.datatretriever.get_sector_tickers(sector)
        elif tickers is not None and isinstance(tickers, str): 
            self.tickers = [tickers] + ['^GSPC']
        elif tickers is not None and isinstance(tickers, list):
            self.tickers = tickers+ ['^GSPC']
        else:
            ['^GSPC']
    
    def main_thread(self, strategy, tickers, sector):
        for result, _, performance in self.run_backtest(strategy, tickers, sector):
            # print(result)
    
            self.visualizer.update_data(result, performance)
            # print(self.visualizer.performance_data)
            time.sleep(0.5)

    def run(self, strategy, tickers, sector=None,start_visualizer=True):    
        """Runs the backtest and starts the frontend visualization."""
        
        self.get_tickers(tickers=tickers, sector=sector)
        self.positions = {ticker: Position(size=0, entry_price=None, stop_loss=None) for ticker in self.tickers}
        self.get_data()
    
        if start_visualizer:
            self.visualizer.update_info(self.tickers, dict((str(indicator), (indicator.columns,indicator.need_extra_graph)) for indicator in self.ta_indicators))

            webbrowser.open('http://127.0.0.1:8050/')

            time.sleep(1)

            backtest_thread = threading.Thread(target=self.main_thread, args=(strategy, tickers, sector))
            backtest_thread.daemon = True
            backtest_thread.start()

            print('Starting Frontend...')

            self.visualizer.run()

        else:
            for result, _ ,_ in self.run_backtest(strategy, tickers, sector):
                pass

            print(self.actions,self.position_history,self.results)

            

        
        
        
    
        



        
        


 
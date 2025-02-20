from backtest.utils.position import Position
from backtest.utils.dataretriever import DataRetriever
from backtest.utils.indicators import *
from backtest.utils.performance import get_performance_metrics, calculate_metrics

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

from tqdm import tqdm


class Backtest:
    def __init__(
        self,
        initial_capital=10000,
        commission=0.001,
        slippage=0.0,
        stop_loss_pct=0.02,
        duration=365 * 10,
        start_date=None,
        end_date=None,
        interval="1h",
    ):

        self.datatretriever = DataRetriever(
            duration=duration,
            start_date=start_date,
            end_date=end_date,
            interval=interval,
        )
        # self.visualizer = Frontend()

        self.tickers = None  # List of tickers or sectors

        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.stop_loss_pct = stop_loss_pct  # Percentage for stop loss (default 2%)

        self.positions = None
        self.data = None
        self.orders = []  # Orders executed during the backtest

        self.portfolio_history = pd.DataFrame(
            columns=["Date", "Capital", "Cash", "Equity", "Portfolio Value"]
        ).set_index("Date")
        self.action_history = pd.DataFrame(
            columns=["Date", "Ticker", "Type", "Amount", "Price", "Stop Loss"]
        ).set_index("Date")
        self.position_history = pd.DataFrame(
            columns=["Date", "Ticker", "Size", "Entry Price", "Stop Loss"]
        ).set_index("Date")

        self.performance_history = pd.DataFrame(
            columns=["Date"] + get_performance_metrics()
        ).set_index("Date")

        self.ta_indicators = [cls() for cls in Indicator.__subclasses__()]

    def execute_order(self, order_type, price, amount, ticker):
        """Executes an order and updates the portfolio accordingly."""

        slippage_adjustment = price * self.slippage
        if order_type == "buy":
            price += slippage_adjustment  # Apply slippage to buy price

            if self.capital >= price * amount:
                stop_loss_price = price * (1 - self.stop_loss_pct)
                self.positions[ticker].buy(
                    price, amount, self.commission, stop_loss=stop_loss_price
                )

                self.capital -= price * amount * (1 + self.commission)
                self.orders.append(
                    {
                        "type": "buy",
                        "price": price,
                        "amount": amount,
                        "ticker": ticker,
                        "stop_loss": stop_loss_price,
                    }
                )
        elif order_type == "sell":
            price -= slippage_adjustment  # Apply slippage to sell price
            if self.positions[ticker].size >= amount:
                proceeds = self.positions[ticker].sell(price, amount, self.commission)
                self.capital += proceeds
                self.orders.append(
                    {"type": "sell", "price": price, "amount": amount, "ticker": ticker}
                )

    def run_backtest(
        self,
        strategy: Strategy,
        tickers: Union[str, List[str]],
        sector: str = None,
        fast=True,
    ):
        """Runs the backtest with the given strategy and tickers."""

        all_dates = self.data[tickers[0]].index

        for ticker in self.tickers:
            all_dates = all_dates.intersection(self.data[ticker].index)

        for i, date in enumerate(all_dates):
            # print("Date: ", date)
            total_value = 0

            for ticker in self.tickers:
                row = self.data[ticker].loc[date]
                current_price = row["Close"]
                if self.positions[ticker].is_open():
                    if current_price <= self.positions[ticker].stop_loss:
                        self.execute_order(
                            "sell", current_price, self.positions[ticker].size, ticker
                        )
                        action_entry = {
                            "Date": date,
                            "Ticker": ticker,
                            "Type": "sell",
                            "Amount": self.positions[ticker].size,
                            "Price": current_price,
                            "Stop Loss": self.positions[ticker].stop_loss,
                        }
                        self.action_history = pd.concat(
                            [self.action_history, pd.DataFrame([action_entry])],
                            ignore_index=True,
                        )

                    self.positions[ticker].update_stop_loss(
                        current_price, trailing_stop_pct=0.05
                    )

                action = strategy.get_action(row, ticker, self.positions)

                if action.type == "buy":
                    self.execute_order("buy", current_price, action.amount, ticker)
                elif action.type == "sell":
                    self.execute_order("sell", current_price, action.amount, ticker)

                total_value += self.positions[ticker].get_value(current_price)

                action_entry = {
                    "Date": date,
                    "Ticker": ticker,
                    "Type": action.type,
                    "Amount": action.amount,
                    "Price": current_price,
                    "Stop Loss": self.positions[ticker].stop_loss,
                }

                Position_entry = {
                    "Date": date,
                    "Ticker": ticker,
                    "Size": self.positions[ticker].size,
                    "Entry Price": self.positions[ticker].entry_price,
                    "Stop Loss": self.positions[ticker].stop_loss,
                }

                self.action_history = pd.concat(
                    [self.action_history, pd.DataFrame([action_entry])],
                    ignore_index=True,
                )
                self.position_history = pd.concat(
                    [self.position_history, pd.DataFrame([Position_entry])],
                    ignore_index=True,
                )

            equity = self.capital + total_value

            portfolio_entry = {
                "Date": date,
                "Capital": self.initial_capital,
                "Cash": self.capital,
                "Equity": equity,
                "Portfolio Value": equity,
            }

            self.portfolio_history.loc[date] = portfolio_entry

            metrics_entry = calculate_metrics(
                date, self.data, self.portfolio_history, self.action_history
            )

            self.performance_history = pd.concat(
                [self.performance_history, pd.DataFrame([metrics_entry])],
                ignore_index=True,
            )
            if not fast:
                time.sleep(0.5)

    def get_data(self):
        self.data = self.datatretriever.get_data(self.tickers)
        self.data = self.apply_ta_indicators()
        return self.data

    def apply_ta_indicators(self):
        """
        Applies the technical Indicators as found in utils/inidcators.py to the data.
        """

        for indicator in self.ta_indicators:
            for ticker in self.tickers:
                self.data[ticker] = indicator.apply(self.data[ticker])
        return self.data

    def get_tickers(self, tickers=Union[str, List[str]], sector: str = None):
        """
        Sets the tickers attribute based on the given tickers or sector. If none are taking the SP500 is used. (^GSPC)
        """

        if sector is not None:
            self.tickers = self.datatretriever.get_sector_tickers(sector)
        elif tickers is not None and isinstance(tickers, str):
            self.tickers = [tickers] + ["^GSPC"]
        elif tickers is not None and isinstance(tickers, list):
            self.tickers = tickers + ["^GSPC"]
        else:
            ["^GSPC"]

    def run(self, strategy, tickers, sector=None, start_visualizer=True, fast=True):
        """Runs the backtest and starts the frontend visualization."""

        self.get_tickers(tickers=tickers, sector=sector)
        self.positions = {
            ticker: Position(size=0, entry_price=None, stop_loss=None)
            for ticker in self.tickers
        }
        self.get_data()

        if start_visualizer:
            # Create Frontend instance with reference to this Backtest instance
            self.visualizer = Frontend(backtest_instance=self)

            self.visualizer.update_info(
                self.tickers,
                dict(
                    (str(indicator), (indicator.columns, indicator.need_extra_graph))
                    for indicator in self.ta_indicators
                ),
            )

            webbrowser.open("http://127.0.0.1:8050/")

            # Start backtest in a separate thread
            backtest_thread = threading.Thread(
                target=self.run_backtest, args=(strategy, tickers, sector, fast)
            )
            backtest_thread.daemon = True
            backtest_thread.start()

            print("Starting Frontend...")
            self.visualizer.run()

        else:
            print("Starting backtest...")
            self.run_backtest(strategy, tickers, sector, fast)

            print("Backtest completed.")

            print("Portfolio:\n", self.portfolio_history)
            print("Actions:\n", self.action_history)
            print("Positions:\n", self.position_history)
            print("Performance:\n", self.performance_history)

# PyBacktest

This project is a backtesting framework for financial trading strategies. It includes modules for data retrieval, technical analysis indicators, strategy execution, and a frontend for visualizing the results.

## Features
- Retrieve historical stock data using `yfinance`.
- Apply various technical analysis indicators (e.g., SMA, MACD, RSI).
- Execute trading strategies with customizable parameters.
- Visualize stock prices, technical indicators, and trading actions using Dash and Plotly.

## Usage
1. Define your custom trading strategy by extending the `Strategy` class.
2. Initialize the `Backtest` class with your desired parameters.
3. Run the backtest with your strategy and selected tickers or sectors.
4. Visualize the results in the interactive dashboard.

## Next Steps
- Add more features to the frontend, such as predictions and additional statistics.
- Implement utility functions for enhanced strategy development.
- Track stop loss triggers and experiment with different strategies.

## TODO
- Improve visualization by limiting the maximum amount of displayed data.
- Add an overview of all statistics, including Sharpe Ratio and SP500 baselines.
- Enhance backend functionality for better strategy tracking and experimentation.
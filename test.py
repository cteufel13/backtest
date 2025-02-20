from backtest.utils.dataretriever import DataRetriever
from backtest.frontend import Frontend
from backtest.backtest import Backtest
from teststuff.teststrategy import CustomStrategy


backtest = Backtest(
    initial_capital=10000,
    commission=0.001,
    slippage=0.0,
    stop_loss_pct=0.02,
    duration=365 * 10,
    start_date=None,
    end_date=None,
    interval="1d",
)
strat = CustomStrategy()

backtest.run(
    strategy=strat,
    tickers=["AAPL", "GOOG", "MCFT"],
    start_visualizer=True,
    fast=True,
)

# print(backtest.performance.loc[0])
## test if passing whole

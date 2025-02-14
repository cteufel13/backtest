from backtest.core.strategy import Strategy
from backtest.core.action import Action
from backtest.utils.position import Position

class CustomStrategy(Strategy):

    def __init__(self):
        pass


    def get_action(self, data, ticker,positions):
        # Custom strategy to buy if the price is above the 50-day moving average
        if not positions[ticker].is_open():
            return Action(type='buy', amount = 1, stop_loss=data['Close']*0.95)
        else:
            return Action(type='None', amount = 0, stop_loss=None)
            
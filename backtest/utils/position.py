import numpy as np


class Position:

    def __init__(self, size, entry_price, stop_loss):
        self.size = size
        self.entry_price = entry_price
        self.capital_invested = 0.0
        self.highest_price = entry_price
        self.stop_loss = stop_loss

    def buy(self, price, amount, comission, stop_loss=None):
        self.size += amount
        self.entry_price = price
        self.capital_invested = self.size * self.entry_price * (1 + comission)
        self.stop_loss = stop_loss
        if self.highest_price is None:
            self.highest_price = price
        self.highest_price = max(self.highest_price, self.entry_price)

    def sell(self, price, amount, comission):
        if amount > self.size:
            raise ValueError("Cannot sell more than the current position size")

        self.size -= amount

        self.size -= amount
        self.capital_invested -= self.size * self.entry_price * (1 + comission)

        return amount * price * (1 - comission)

    def get_value(self, price):
        return self.size * price

    def get_pnl(self, current_price):
        return self.get_value(current_price) - self.capital_invested

    def is_open(self):
        return self.size > 0

    def update_stop_loss(self, price, trailing_stop_pct=0.95):

        if self.stop_loss is None:
            self.highest_price = max(self.highest_price, price)
            self.stop_loss = self.highest_price * (1 - trailing_stop_pct)

    def __repr__(self):
        return f"Position(size={self.size}, entry_price={self.entry_price}, stop_loss={self.stop_loss})"

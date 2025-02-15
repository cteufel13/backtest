import pandas as pd

class Indicator:

    def __init__(self, name):
        self.name = name
        self.columns = []



    def apply(self, data:pd.DataFrame) ->pd.DataFrame:
        raise NotImplementedError

    def visualize(self, data:pd.DataFrame) ->pd.DataFrame:
        raise NotImplementedError

    def __repr__ ():
        raise NotImplementedError



def check_valid_data(data:pd.DataFrame):
    if data is None:
        raise ValueError("data is None")
    if data.empty:
        raise ValueError("data is empty")
    if not isinstance(data, pd.DataFrame):
        raise ValueError("data is not a DataFrame")
    if 'Close' not in data.columns:
        raise ValueError("data does not contain 'close' column")
    if 'Open' not in data.columns:
        raise ValueError("data does not contain 'open' column")
    if 'High' not in data.columns:
        raise ValueError("data does not contain 'high' column")
    if 'Low' not in data.columns:
        raise ValueError("data does not contain 'low' column")
    if 'Volume' not in data.columns:
        raise ValueError("data does not contain 'volume' column")
    
    return True
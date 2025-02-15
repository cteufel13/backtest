import pandas as pd

class Indicator:
    def __init__(self, name, params):
        self.name = name
        self.params = params

    def apply(self, data:pd.DataFrame) ->pd.DataFrame:
        raise NotImplementedError

    def visualize(self, data:pd.DataFrame) ->pd.DataFrame:
        raise NotImplementedError

    def __str__(self):
        return f"{self.name}({self.params})"

    def __repr__(self):
        return self.__str__()



def check_valid_data(data:pd.DataFrame):
    if data is None:
        raise ValueError("data is None")
    if data.empty:
        raise ValueError("data is empty")
    if not isinstance(data, pd.DataFrame):
        raise ValueError("data is not a DataFrame")
    if 'close' not in data.columns:
        raise ValueError("data does not contain 'close' column")
    if 'open' not in data.columns:
        raise ValueError("data does not contain 'open' column")
    if 'high' not in data.columns:
        raise ValueError("data does not contain 'high' column")
    if 'low' not in data.columns:
        raise ValueError("data does not contain 'low' column")
    if 'volume' not in data.columns:
        raise ValueError("data does not contain 'volume' column")
    
    return True
import pandas_ta as ta
import pandas as pd
from backtest.core.ta_ind import Indicator, check_valid_data
import plotly.graph_objects as go
import plotly.express as px
"""
preset implementation for technical indicators as provided by pandas_ta
"""    

__all__ = ['SMA']




class SMA(Indicator):

    def __init__(self, params):
        super().__init__('SMA', params)

    def apply(self, data:pd.DataFrame) ->pd.DataFrame:
        if check_valid_data(data):
            data['sma'] = ta.sma(data['close'], self.params)
            return data
        else:
            return None


    def visualize(self, data:pd.DataFrame,fig:go.Figure) ->pd.DataFrame:
        fig.add_trace(go.Scatter(x=data.index, y=data['sma'], name='SMA',color='orange',row=1, col=1))
        return fig
    



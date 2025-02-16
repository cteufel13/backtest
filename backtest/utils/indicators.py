import pandas as pd
from backtest.core.indicator_base import Indicator, check_valid_data
import plotly.graph_objects as go
import plotly.express as px
"""
preset implementation for technical indicators as provided by pandas_ta
"""    

__all__ = ['SMA20']




class SMA20(Indicator):

    def __init__(self):
        super().__init__('SMA20')
        self.window = 20
        self.columns = ['SMA20']
        self.need_extra_graph = False

    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        if check_valid_data(data):
            data['SMA20'] = data['Close'].rolling(window=self.window).mean()
            return data
    
    def visualize(self, data: pd.DataFrame,fig:go.Figure) -> go.Figure:
        if check_valid_data(data):
            fig.add_trace(go.Scatter(x=data.index, y=data['SMA20'], mode='lines', name='SMA20'),row=1, col=1)
            return fig
    
    def __repr__(self):
        return 'SMA20'

class SMA50(Indicator):

    def __init__(self):
        super().__init__('SMA50')
        self.window = 50
        self.columns = ['SMA50']
        self.need_extra_graph = False


    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        if check_valid_data(data):
            data['SMA50'] = data['Close'].rolling(window=self.window).mean()
            return data
    
    def visualize(self, data: pd.DataFrame,fig:go.Figure) -> go.Figure:
        if check_valid_data(data):
            fig.add_trace(go.Scatter(x=data.index, y=data['SMA50'], mode='lines', name='SMA50'),row=1, col=1)
            return fig
    
    def __repr__(self):
        return 'SMA50'
    
class SMA200(Indicator):
    
    def __init__(self):
        super().__init__('SMA200')
        self.window = 200
        self.columns = ['SMA200']
        self.need_extra_graph = False


    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        if check_valid_data(data):
            data['SMA200'] = data['Close'].rolling(window=self.window).mean()
            return data
    
    def visualize(self, data: pd.DataFrame,fig:go.Figure) -> go.Figure:
        if check_valid_data(data):
            fig.add_trace(go.Scatter(x=data.index, y=data['SMA200'], mode='lines', name='SMA200'),row=1, col=1)
            return fig
    
    def __repr__(self):
        return 'SMA200'   
    
class MACD(Indicator):
    
    def __init__(self):
        super().__init__('MACD')
        self.window1 = 12
        self.window2 = 26
        self.window3 = 9
        self.columns = ['MACD', 'Signal']
        self.need_extra_graph = True


    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        if check_valid_data(data):
            data['MACD'] = data['Close'].ewm(span=self.window1, adjust=False).mean() - data['Close'].ewm(span=self.window2, adjust=False).mean()
            data['Signal'] = data['MACD'].ewm(span=self.window3, adjust=False).mean()
            return data
    
    def visualize(self, data: pd.DataFrame,fig:go.Figure) -> go.Figure:
        if check_valid_data(data):
            fig.add_trace(go.Scatter(x=data.index, y=data['MACD'], mode='lines', name='MACD'),row=1, col=1)
            fig.add_trace(go.Scatter(x=data.index, y=data['Signal'], mode='lines', name='Signal'),row=1, col=1)
            return fig
    
    def __repr__(self):
        return 'MACD'
    

class RSI(Indicator):

    def __init__(self):
        super().__init__('RSI')
        self.window = 14
        self.columns = ['RSI']
        self.need_extra_graph = True

    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        if check_valid_data(data):
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=self.window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=self.window).mean()
            rs = gain / loss
            data['RSI'] = 100 - (100 / (1 + rs))
            return data
    
    def visualize(self, data: pd.DataFrame,fig:go.Figure) -> go.Figure:
        if check_valid_data(data):
            fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI'),row=1, col=1)
            return fig
    
    def __repr__(self):
        return 'RSI'
    

class BollingerBands(Indicator):

    def __init__(self):
        super().__init__('BollingerBands')
        self.window = 20
        self.columns = [ 'UpperBand', 'LowerBand']
        self.need_extra_graph = False


    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        if check_valid_data(data):
            data['SMA'] = data['Close'].rolling(window=self.window).mean()
            data['STD'] = data['Close'].rolling(window=self.window).std()
            data['UpperBand'] = data['SMA'] + (data['STD'] * 2)
            data['LowerBand'] = data['SMA'] - (data['STD'] * 2)
            return data
        
    def visualize(self, data: pd.DataFrame,fig:go.Figure) -> go.Figure:
        if check_valid_data(data):
            fig.add_trace(go.Scatter(x=data.index, y=data['UpperBand'], mode='lines', name='UpperBand'),row=1, col=1)
            fig.add_trace(go.Scatter(x=data.index, y=data['LowerBand'], mode='lines', name='LowerBand'),row=1, col=1)
            return fig
        
    def __repr__(self):
        return 'BollingerBands'

    
    



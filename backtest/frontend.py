import dash
from dash import dcc, html
import plotly.express as px
from dash.dependencies import Input, Output, State
import pandas as pd
import threading
import time

class Frontend:
    def __init__(self, stocks=None, sectors=None):
        self.stocks = stocks if stocks else ['GOOG']
        self.sectors = sectors if sectors else ['Technology', 'Healthcare', 'Finance']
        self.stock_data = {stock: pd.DataFrame(columns=["Date", "Price"]).set_index("Date") for stock in self.stocks}

        self.app = dash.Dash(__name__, suppress_callback_exceptions=True)
        self.server_thread = None
        self._setup_layout()
        self._setup_callbacks()

    def _setup_callbacks(self):
        
        self.app.callback(
            Output('main-graph', 'figure'),
            Input('dropdown', 'value'),
            Input('interval-update', 'n_intervals')
        ) (self.update_graph)
         

       
    def update_data(self, data_row):
            for stock in self.stocks:
                    self.stock_data[stock].loc[data_row['Date'],'Price'] = data_row['Stock Prices'][stock]
            return self.stock_data

       
    def update_graph(self,selected_stock,n_intervals):
        print('n_intervals:',n_intervals)
        print("update_graph called with:", selected_stock)  # This confirms the callback is executing.
        df = self.stock_data[selected_stock]
        print('DataFrame for', selected_stock, ':', df)
        fig = px.line(df, x=df.index, y='Price', title=f'{selected_stock} Close Price')
        return fig
        
        

    def _setup_layout(self):

        layout = html.Div([
            html.H1('Stock Price Dashboard', className='header-title'),
            html.Div([
                dcc.Dropdown(
                    id='dropdown',
                    options=[{'label': stock, 'value': stock} for stock in self.stocks],
                    value=self.stocks[0],
                    style={'fontFamily': 'Arial'}
                )
            ], className='dropdown-container'),
            html.Div([
                dcc.Graph(id='main-graph'),
                dcc.Interval(
                    id='interval-update',
                    interval=1000, # in milliseconds
                    n_intervals=0)
            ], className='main-graph-container'),
        ])
        self.app.layout = layout

    def run(self):
        print('running server   ---------------')
        self.app.run_server()

    
    def update_stocks(self, stocks):
        self.stocks = stocks
        for stock in self.stocks:
            if stock not in self.stock_data:
                self.stock_data[stock] = pd.DataFrame(columns=["Date", "Price"]).set_index("Date")
        

if __name__ == '__main__':
    frontend = Frontend()
    frontend.run()

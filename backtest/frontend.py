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
        # Each stock's data is a DataFrame indexed by Date with a Price column.
        self.stock_data = {stock: pd.DataFrame(columns=["Date", "Price"]).set_index("Date") for stock in self.stocks}
        self.app = dash.Dash(__name__, suppress_callback_exceptions=True)
        self.server_thread = None


    def _setup_callbacks(self):


        # Callback 4: Update the graph based on the selected stock.
        @self.app.callback(
            Output('main-graph', 'figure'),
            Input('dropdown', 'value'),
        )
        def update_graph(selected_stock):
            df = self.stock_data[selected_stock]
            print('df:',df)

            fig = px.line(df, x=df.index, y='Price', title=f'{selected_stock} Close Price')
            return fig

    def _setup_layout(self):

        layout = html.Div([
            html.H1('Stock Price Dashboard', className='header-title'),
            html.Div([
                dcc.Dropdown(
                    id='dropdown',
                    options=[{'label': stock, 'value': stock} for stock in self.stocks],
                    value=None,
                    style={'fontFamily': 'Arial'}
                )
            ], className='dropdown-container'),
            html.Div([
                dcc.Graph(id='main-graph')
            ], className='main-graph-container'),
            dcc.Interval(id='interval-update', interval=500, n_intervals=0)
        ])
        self.app.layout = layout

        

    def run(self):
        self._setup_layout()
        self._setup_callbacks()
        self.app.run_server()

    
    def update_stocks(self, stocks):
        """Update the list of stocks and initialize their data structures."""
        self.stocks = stocks
        for stock in self.stocks:
            if stock not in self.stock_data:
                self.stock_data[stock] = pd.DataFrame(columns=["Date", "Price"]).set_index("Date")

    def update_data(self, data):
        self.stock_data = data
        print(self.stock_data)
        

if __name__ == '__main__':
    frontend = Frontend()
    frontend.run()

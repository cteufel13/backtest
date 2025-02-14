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
        self.setup()

    def setup(self):
        layout = html.Div([
            html.H1('Stock Price Dashboard', className='header-title'),
            dcc.Store(id='stock-data-store', data={}),
            html.Div([
                dcc.Dropdown(
                    id='dropdown',
                    options=[{'label': stock, 'value': stock} for stock in self.stocks],
                    value=self.stocks[0] if self.stocks else None,
                    style={'fontFamily': 'Arial'}
                )
            ], className='dropdown-container'),
            html.Div([
                dcc.Graph(id='main-graph')
            ], className='main-graph-container'),
            dcc.Interval(id='interval-update', interval=500, n_intervals=0)
        ])
        self.app.layout = layout

        # Callback 1: Update the dropdown options.
        @self.app.callback(
            Output('dropdown', 'options'),
            Input('interval-update', 'n_intervals')
        )
        def update_dropdown_options(n_intervals):
            return [{'label': stock, 'value': stock} for stock in self.stocks]

        # Callback 2: Ensure the dropdown value is valid.
        @self.app.callback(
            Output('dropdown', 'value'),
            Input('dropdown', 'options'),
            State('dropdown', 'value')
        )
        def update_dropdown_value(options, current_value):
            valid_values = [opt['value'] for opt in options]
            return current_value if current_value in valid_values else (valid_values[0] if valid_values else None)

        # Callback 3: Update the stock-data store with data from self.stock_data.
        @self.app.callback(
            Output('stock-data-store', 'data'),
            Input('interval-update', 'n_intervals'),
            State('stock-data-store', 'data')
        )
        def update_store(n_intervals, current_data):
            if current_data is None:
                current_data = {}
            for stock in self.stocks:
                if stock not in self.stock_data:
                    continue
                # Reset the index so that Date becomes a column.
                df = self.stock_data[stock].reset_index()
                current_data[stock] = df.to_dict('records')
            return current_data

        # Callback 4: Update the graph based on the selected stock.
        @self.app.callback(
            Output('main-graph', 'figure'),
            Input('dropdown', 'value'),
            State('stock-data-store', 'data')
        )
        def update_graph(selected_stock, data):
            if not selected_stock or not data or selected_stock not in data:
                return px.line(title='No Stock Selected')
            df = pd.DataFrame(data[selected_stock])
            if df.empty:
                return px.line(title=f'No Data for {selected_stock}')
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
            fig = px.line(df, x=df.index, y='Price', title=f'{selected_stock} Close Price')
            return fig

    def run(self):
        """Runs Dash server in a separate thread."""
        self.server_thread = threading.Thread(target=self.app.run_server, kwargs={
            'debug': False, 
            'use_reloader': False
        })
        self.server_thread.start()

    def update_stocks(self, stocks):
        """Update the list of stocks and initialize their data structures."""
        self.stocks = stocks
        for stock in self.stocks:
            if stock not in self.stock_data:
                self.stock_data[stock] = pd.DataFrame(columns=["Date", "Price"]).set_index("Date")

    def update_data(self, new_row):
        """
        Update stock data with new prices.
        new_row is expected to be a dict with keys:
         - 'Date': a timestamp,
         - 'Stock Prices': a dict mapping stock tickers to their price.
        """
        for stock, price in new_row["Stock Prices"].items():
            if stock not in self.stock_data:
                self.stock_data[stock] = pd.DataFrame(columns=["Date", "Price"]).set_index("Date")
            self.stock_data[stock].loc[new_row['Date']] = price

if __name__ == '__main__':
    frontend = Frontend()
    frontend.run()

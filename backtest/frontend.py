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
        self.portfolio_data = {}

        self.app = None
        self.server_thread = None
        self.setup()

    def setup(self):
        self.app = dash.Dash(__name__, suppress_callback_exceptions=True)
        
        # Create an interval component specifically for stock updates
        self.app.layout = html.Div([
            html.H1('Stock Price Dashboard', className='header-title'),
            
            dcc.Store(id='stock-data-store', data={}),
            dcc.Store(id='stocks-store', data={'stocks': self.stocks}, storage_type='memory'),  # Changed to memory

            html.Div([
                html.Div([
                    html.Div([
                        html.Div([
                            dcc.Dropdown(
                                id='dropdown',
                                options=[{'label': i, 'value': i} for i in self.stocks],
                                value=self.stocks[0] if self.stocks else None,
                                style={'fontFamily': 'Arial'}
                            )
                        ], className='dropdown-container'),

                        html.Div([
                            dcc.Dropdown(
                                id='sector-dropdown',
                                options=[{'label': i, 'value': i} for i in self.sectors],
                                value=self.sectors[0] if self.sectors else None,
                                style={'fontFamily': 'Arial'}
                            )
                        ], className='dropdown-container'),

                    ], className='dropdown-top-container'),

                    html.Div([
                        dcc.Graph(id='main-graph')
                    ], className='main-graph-container'),

                ], className='main-left-container'),

            ], className='main-container'),

            dcc.Interval(id='interval-update', interval=10, n_intervals=0),
            dcc.Interval(id='stocks-update-trigger', interval=10, n_intervals=0)  # New interval for stock updates
        ])

        # Modified callback to update dropdown options
        @self.app.callback(
            [Output('dropdown', 'options'),
             Output('dropdown', 'value')],
            [Input('stocks-update-trigger', 'n_intervals')],
            [State('dropdown', 'value')]
        )
        def update_dropdown_options(n_intervals, current_value):
            options = [{'label': stock, 'value': stock} for stock in self.stocks]
            # Keep current value if it's still in the options, otherwise select first stock
            value = current_value if current_value in self.stocks else (self.stocks[0] if self.stocks else None)
            return options, value

        @self.app.callback(
            Output('stock-data-store', 'data'),
            Input('interval-update', 'n_intervals'),
            State('stock-data-store', 'data')
        )
        def update_stock_data(n_intervals, current_data):
            if current_data is None:
                current_data = {}

            for stock in self.stocks:
                if stock not in self.stock_data:
                    continue
                
                df = self.stock_data[stock].reset_index()
                current_data[stock] = df.to_dict('records')

            return current_data

        @self.app.callback(
            Output('main-graph', 'figure'),
            [Input('dropdown', 'value'),
             Input('stock-data-store', 'data')]
        )
        def update_main_graph(selected_stock, stock_data):
            if not selected_stock or selected_stock not in stock_data:
                return px.line(title='No Stock Selected')

            df = pd.DataFrame(stock_data[selected_stock])
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
            'use_reloader': False, 
            'dev_tools_silence_routes_logging': True
        })
        
        self.server_thread.start()

    def stop(self):
        """Gracefully stop Dash server."""
        if self.server_thread:
            self.server_thread.join(timeout=1)

    def update_stocks(self, stocks):
        """Update the list of stocks and initialize their data structures."""
        self.stocks = stocks
        # Initialize data structures for new stocks
        for stock in self.stocks:
            if stock not in self.stock_data:
                self.stock_data[stock] = pd.DataFrame(columns=["Date", "Price"]).set_index("Date")

    def update_data(self, new_row):
        """Update stock data with new prices."""
        for stock, price in new_row["Stock Prices"].items():
            if stock not in self.stock_data:
                self.stock_data[stock] = pd.DataFrame(columns=["Date", "Price"]).set_index("Date")

            self.stock_data[stock].loc[new_row['Date']] = price
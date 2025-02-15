import dash
from dash import dcc, html
import plotly.express as px
from dash.dependencies import Input, Output, State
import pandas as pd

class Frontend:

    def __init__(self, stocks=None, sectors=None):
        self.stocks = stocks if stocks else ['GOOG']
        self.sectors = sectors if sectors else ['Technology', 'Healthcare', 'Finance']
        self.stock_data = {stock: pd.DataFrame(columns=["Date", "Open","High","Low","Close","Volume","Dividends", "Stock Splits"]).set_index("Date") for stock in self.stocks}
        self.action_data = {stock: pd.DataFrame(columns=["Date", "Action"]).set_index("Date") for stock in self.stocks}
        self.additional_data = pd.DataFrame(columns=["Date", "Capital","Cash","Equity","Portfolio Value"]).set_index("Date")
        
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

        self.app.callback(
            Output('dropdown', 'options'),
            Input('stocks-store', 'data')
        ) (self.update_dropdown_options)

        self.app.callback(
            Output('stocks-store', 'data'),
            Input('once-interval', 'n_intervals'),
            State('stocks-store', 'data')
        )(self.update_store_once)

        self.app.callback(
            Output('additional-graph', 'figure'),
            Input('interval-update', 'n_intervals')
        )(self.update_additional_graph)
         
    def _setup_layout(self):

        layout = html.Div([
            html.H1('Stock Price Dashboard', className='header-title'),
            dcc.Store(id='stocks-store', data=self.stocks),
            dcc.Interval(id='once-interval', interval=1000, max_intervals=1),
            html.Div([
                dcc.Dropdown(
                    id='dropdown',
                    options=[{'label': stock, 'value': stock} for stock in self.stocks],
                    value=self.stocks[0],
                    multi=True,
                    style={'fontFamily': 'Arial'},
                    className='dropdown-menu'
                ),
                dcc.Dropdown(
                    id='dropdown2',
                    options= [
                        {'label': 'Communication Services', 'value': 'XLC'},
                        {'label': 'Consumer Discretionary', 'value': 'XLY'},
                        {'label': 'Consumer Staples', 'value': 'XLP'},
                        {'label': 'Energy', 'value': 'XLE'},
                        {'label': 'Financials', 'value': 'XLF'},
                        {'label': 'Health Care', 'value': 'XLV'},
                        {'label': 'Industrials', 'value': 'XLI'},
                        {'label': 'Information Technology', 'value': 'XLK'},
                        {'label': 'Materials', 'value': 'XLB'},
                        {'label': 'Real Estate', 'value': 'XLRE'},
                        {'label': 'Utilities', 'value': 'XLU'},
                        {'label': None, 'value':None}],
                    value = None,
                    style= {'fontFamily': 'Arial'},
                    className='dropdown-menu'
                )
            ], className='dropdown-container'),

            html.Div([
                html.Div([
                    html.Div([
                        dcc.Graph(id='main-graph',
                                className='main-graph'),
                        dcc.Interval(
                            id='interval-update',
                            interval=220, # in milliseconds
                            n_intervals=0)
                    ], className='main-graph-container'),
                    html.Div([
                        dcc.Graph(id='additional-graph',
                                className='additional-graph'),
                    ], className='additional-graph-container')
                    ], className='left-container'),
                html.Div([
                    html.H2 ('Actions', className='actions-title'),
                ], className='right-container') 
            ], className='main-container')
            

        ])
        self.app.layout = layout

    def run(self):
        print('running server   ---------------')
        self.app.run_server()
   
    def update_stocks(self, stocks):
        self.stocks = stocks
        for stock in self.stocks:
            if stock not in self.stock_data:
                self.stock_data[stock] = pd.DataFrame(columns=["Date", "Open","High","Low","Close","Volume","Dividends", "Stock Splits"]).set_index("Date")
                self.action_data[stock] = pd.DataFrame(columns=["Date", "Action", "IdPrice","StopLoss"]).set_index("Date")
        
    def update_dropdown_options(self,stocks):
        return [{'label': stock, 'value': stock} for stock in stocks]

    def update_store_once(self, n_intervals, current_data):
        return self.stocks
    
    def update_data(self, data_row):
            for stock in self.stocks:
                    self.stock_data[stock].loc[data_row['Date']] = data_row['Stock Info'][stock]
                    action_obj = data_row['Action'][stock]  # This is an Action instance
                    self.action_data[stock].loc[data_row['Date'], 'Action'] = action_obj.type
                    self.action_data[stock].loc[data_row['Date'], 'Amount'] = int(action_obj.amount)
                    self.action_data[stock].loc[data_row['Date'], 'IdPrice'] = data_row['Stock Info'][stock]['Close']
                    if action_obj.stop_loss is not None:
                        self.action_data[stock].loc[data_row['Date'], 'StopLoss'] = float(action_obj.stop_loss)
                    else:
                        self.action_data[stock].loc[data_row['Date'], 'StopLoss'] = None
                                            
            self.additional_data.loc[data_row['Date'], 'Capital'] = data_row['Capital']
            self.additional_data.loc[data_row['Date'], 'Cash'] = data_row['Cash']
            self.additional_data.loc[data_row['Date'], 'Equity'] = data_row['Equity']
            self.additional_data.loc[data_row['Date'], 'Portfolio Value'] = data_row['Portfolio Value']
            
    def update_graph(self,selected_stocks,n_intervals):

        if isinstance(selected_stocks, str):
            selected_stocks = [selected_stocks]

        fig = px.line()
        for selected_stock in selected_stocks:
            df = self.stock_data[selected_stock]
            fig.add_scatter(x=df.index, y=df['Close'], mode='lines', name=selected_stock)
            fig.add_candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name=selected_stock)
            fig.update_layout(
                xaxis_rangeslider_visible=False
            )
            #buy/sell actions

            actions_df = self.action_data[selected_stock]
            buys = actions_df[actions_df['Action'] == 'buy']
            if not buys.empty:
                fig.add_scatter(
                    x=buys.index,
                    y=buys['IdPrice'],
                    mode='markers',
                    marker=dict(symbol='triangle-up', size=10, color='green'),
                    name=f"{selected_stock} Buys",
                    text=[f"Stop Loss: {sl}" for sl in buys['StopLoss']],
                    hovertemplate="%{x}<br>Price: %{y}<br>%{text}<extra></extra>"
                )
            
            # Filter for sell actions.
            sells = actions_df[actions_df['Action'] == 'sell']
            if not sells.empty:
                fig.add_scatter(
                    x=sells.index,
                    y=sells['IdPrice'],
                    mode='markers',
                    marker=dict(symbol='triangle-down', size=10, color='red'),
                    name=f"{selected_stock} Sells",
                    text=[f"Stop Loss: {sl}" for sl in sells['StopLoss']],
                    hovertemplate="%{x}<br>Price: %{y}<br>%{text}<extra></extra>"
                )

        
        return fig

    def update_additional_graph(self,n_intervals):
            fig = px.line()
            df = self.additional_data

            fig.add_scatter(x=df.index, y=df['Capital'], mode='lines', name='Capital')
            fig.add_scatter(x=df.index, y=df['Cash'], mode='lines', name='Cash')
            fig.add_scatter(x=df.index, y=df['Equity'], mode='lines', name='Equity')
            fig.add_scatter(x=df.index, y=df['Portfolio Value'], mode='lines', name='Portfolio Value')

            return fig

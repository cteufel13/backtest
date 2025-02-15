import dash
from dash import dcc, html
import plotly.express as px
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from backtest.utils.ta_indicators import *


class Frontend:

    def __init__(self, stocks=None, sectors=None):
        self.stocks = stocks if stocks else ['GOOG']
        self.sectors = sectors if sectors else ['Technology', 'Healthcare', 'Finance']
        self.stock_data = {stock: pd.DataFrame(columns=["Date", "Open","High","Low","Close","Volume","Dividends", "Stock Splits",]).set_index("Date") for stock in self.stocks}
        self.action_data = {stock: pd.DataFrame(columns=["Date", "Action"]).set_index("Date") for stock in self.stocks}
        self.additional_data = pd.DataFrame(columns=["Date", "Capital","Cash","Equity","Portfolio Value"]).set_index("Date")
        self.ta_indicator_info = []
        self.app = dash.Dash(__name__, suppress_callback_exceptions=True)
        self.server_thread = None
        self._setup_layout()
        self._setup_callbacks()

    def _setup_callbacks(self):
        
        self.app.callback(
            Output('main-graph', 'figure'),
            Input('dropdown', 'value'),
            Input('dropdown3', 'value'),
            Input('dropdown4', 'value'),
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
            Output('dropdown4', 'options'),
            Input('interval-update', 'n_intervals')
        )(self.update_ta_dropdown_options)
         
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
                    multi=False,
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
                ),
                dcc.Dropdown(
                    id='dropdown3',
                    options= [{'label':'Candlestick', 'value': 'candlestick'},
                              {'label':'Line', 'value': 'line'},
                              {'label':'Buy/Sell', 'value': 'buy/sell'},
                              {'label':'Volume', 'value': 'volume'},
                              {'label':'None', 'value': None}],
                    value = 'line',
                    style= {'fontFamily': 'Arial'},
                    multi=True,
                    className='dropdown-menu'
                ),
                dcc.Dropdown(
                    id='dropdown4',
                    options = [{'label': ta_indicator, 'value': ta_indicator} for ta_indicator in self.ta_indicator_info] + [{'label': 'None', 'value': None}],
                    value = None,
                    style= {'fontFamily': 'Arial'},
                    multi=True,
                    className='dropdown-menu'
                ),
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
   
    def update_info(self, stocks,indicators):
        self.stocks = stocks
        self.ta_indicator_info = indicators

        for stock in self.stocks:
                self.stock_data[stock] = pd.DataFrame(columns=["Date", "Open","High","Low","Close","Volume","Dividends", "Stock Splits"]+[col for ta_indicator in self.ta_indicator_info.keys() for col in self.ta_indicator_info[ta_indicator]]).set_index("Date")
                self.action_data[stock] = pd.DataFrame(columns=["Date", "Action", "IdPrice","StopLoss"]).set_index("Date")
        

    def update_dropdown_options(self,stocks):
        return [{'label': stock, 'value': stock} for stock in stocks]

    def update_store_once(self, n_intervals, current_data):
        return self.stocks
    
    def update_ta_dropdown_options(self, n_intervals):
        """
        Update the options for the TA indicators dropdown.
        This callback is triggered on every interval update.
        """
        return [{'label': ta_indicator, 'value': ta_indicator} for ta_indicator in self.ta_indicator_info.keys()] + [{'label': 'None', 'value': None}]

    def update_data(self, data_row):
            # print(data_row)
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

    def update_graph(self, selected_stocks, selected_graphs, selected_indicators , n_intervals):
        # Handle the case where a single string is passed instead of a list
        if isinstance(selected_stocks, str):
            selected_stocks = [selected_stocks]

        # Create a figure with 2 rows, 1 column, sharing the x-axis
        fig = make_subplots(rows=2, 
                            cols=1,
                            shared_xaxes=True, 
                            vertical_spacing=0.03,
                            row_heights=[0.7, 0.3],
                            specs=[[{"secondary_y": True}], [{}]]
                            )

        #
        # 1) TOP SUBPLOT (row=1): Stocks + Candlestick + Buy/Sell
        #
        for selected_stock in selected_stocks:
            df = self.stock_data[selected_stock]

            # If "line" is selected
            if 'line' in selected_graphs:
                fig.add_scatter(
                    x=df.index,
                    y=df['Close'],
                    mode='lines',
                    name=f"{selected_stock} (Close)",
                    row=1,
                    col=1
                )

            # If "candlestick" is selected
            if 'candlestick' in selected_graphs:
                fig.add_candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name=f"{selected_stock} (Candlestick)",
                    row=1,
                    col=1
                )

            # If "buy/sell" is selected
            if 'buy/sell' in selected_graphs:
                actions_df = self.action_data[selected_stock]

                # Buys
                buys = actions_df[actions_df['Action'] == 'buy']
                if not buys.empty:
                    fig.add_scatter(
                        x=buys.index,
                        y=buys['IdPrice'],
                        mode='markers',
                        marker=dict(symbol='triangle-up', size=10, color='green'),
                        name=f"{selected_stock} Buys",
                        text=[f"Stop Loss: {sl}" for sl in buys['StopLoss']],
                        hovertemplate="%{x}<br>Price: %{y}<br>%{text}<extra></extra>",
                        row=1,
                        col=1
                    )

                # Sells
                sells = actions_df[actions_df['Action'] == 'sell']
                if not sells.empty:
                    fig.add_scatter(
                        x=sells.index,
                        y=sells['IdPrice'],
                        mode='markers',
                        marker=dict(symbol='triangle-down', size=10, color='red'),
                        name=f"{selected_stock} Sells",
                        text=[f"Stop Loss: {sl}" for sl in sells['StopLoss']],
                        hovertemplate="%{x}<br>Price: %{y}<br>%{text}<extra></extra>",
                        row=1,
                        col=1
                    )
            if 'volume' in selected_graphs:
                max_volume = df['Volume'].max()
                colors = ['green' if c >= o else 'red' 
                      for c, o in zip(df['Close'], df['Open'])]
                fig.add_bar(
                    x=df.index,
                    y=df['Volume'],
                    name=f"{selected_stock} Volume",
                    opacity=0.9,
                    marker_color=colors,
                    row=1,
                    col=1,
                    secondary_y=True
                )
                fig.update_yaxes(title_text="Volume", secondary_y=True, showgrid=False, rangemode='tozero',range=[0, max_volume * 3])
            
            if selected_indicators is not None:
                for ta_indicator in self.ta_indicator_info.keys():
                    if ta_indicator in selected_indicators:
                        for col in self.ta_indicator_info[ta_indicator]:
                            # print(ta_indicator,selected_indicators,col)
                            fig.add_scatter(
                                x=df.index,
                                y=df[col],
                                mode='lines',
                                name=f"{ta_indicator}",
                                row=1,
                                col=1
                            )
            #
        # 2) BOTTOM SUBPLOT (row=2): Additional Data
        #
        df_add = self.additional_data

        fig.add_scatter(
            x=df_add.index,
            y=df_add['Capital'],
            mode='lines',
            name='Capital',
            row=2,
            col=1
        )
        fig.add_scatter(
            x=df_add.index,
            y=df_add['Cash'],
            mode='lines',
            name='Cash',
            row=2,
            col=1
        )
        fig.add_scatter(
            x=df_add.index,
            y=df_add['Equity'],
            mode='lines',
            name='Equity',
            row=2,
            col=1
        )
        fig.add_scatter(
            x=df_add.index,
            y=df_add['Portfolio Value'],
            mode='lines',
            name='Portfolio Value',
            row=2,
            col=1
        )

        # Update overall figure layout
        fig.update_yaxes(title_text="Price", secondary_y=False)

        fig.update_layout(
            xaxis_rangeslider_visible=False,  # Hide the rangeslider if you don't want it
            legend=dict(
                itemclick=False,
                itemdoubleclick=False
            ),
            height=800,
        )

        return fig

import dash
from dash import dcc, html
import plotly.express as px
from dash.dependencies import Input, Output



class Frontend:

    def __init__(self, stocks = None, sectors=None):
        
        self.stocks = ['AAPL', 'MSFT'] #LIST OF STOCKS
        self.sectors = ['Technology', 'Healthcare', 'Finance'] #LIST OF SECTORS

        self.data = None
        self.app = None
        
    
        self.setup()

                  
        
    def load(self,data):
        self.data = data

    def setup(self):
        self.app = dash.Dash(__name__)
        self.app.layout = html.Div([

            html.H1('Stock Price Dashboard', className='header-title'),


            # Left Container
            html.Div([

                # Dropdowns Container
                html.Div([ 
                    #Dropdown 1 : Stock selection
                    html.Div([
                        dcc.Dropdown(
                            id='dropdown',
                            options=[{'label': i, 'value': i} for i in self.stocks],
                            value='MSFT'
                        )
                    ], 
                    className='dropdown-container',),
                    
                    #Dropdown 2 : Sector selection
                    html.Div([
                        dcc.Dropdown(
                            id='sector-dropdown',
                            options=[{'label': i, 'value': i} for i in self.sectors],
                            value='Technology'
                        )
                    ],
                    className='dropdown-container',),

                ], className='dropdown-top-container'),

                # Main Graph
                html.Div([
                    dcc.Graph(id='main-graph')
                ], className='main-graph-container'),


            ],className='main-left-container'),

            html.Div([ 
                
            ], className='main-right-container'),

            

            # Secondary Graphs
            html.Div([
                dcc.Graph(id='secondary-graphs')
            ], className='secondary-graph-container'),


            #Some Selection on the bottom maybe later news feeds?    

        ])

        @self.app.callback(
            Output('main-graph', 'figure'),
            Input('dropdown', 'value')
        )
        def update_main_graph(selected_stock):
            df = self.data[selected_stock]['Close']
            fig = px.line(df, x=df.index,y='Close', title=f'{selected_stock} Close Price')
            return fig  
     
    def run(self):
        self.app.run_server(debug=True)

    def update_stocks(self, stocks):
        self.stocks = stocks

    def update_sectors(self, sectors):
        self.sectors = sectors

    

import dash
from dash import dcc, html, dash_table
import plotly.express as px
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from backtest.utils.indicators import *
from backtest.utils.performance import get_performance_metrics, calculate_metrics
import time


class Frontend:

    def __init__(self, backtest_instance=None):
        self.backtest_instance = backtest_instance
        self.app = dash.Dash(__name__, suppress_callback_exceptions=False)
        self.app.title = "Backtest Dashboard"
        self.server_thread = None
        self.stocks = ["GOOG"]
        self.ta_indicator_info = []
        self._setup_layout()
        self._setup_callbacks()

    def _setup_callbacks(self):

        self.app.callback(
            Output("main-graph", "figure"),
            Input("dropdown", "value"),
            Input("dropdown3", "value"),
            Input("dropdown4", "value"),
            Input("interval-update", "n_intervals"),
        )(self.update_graph)

        self.app.callback(Output("dropdown", "options"), Input("stocks-store", "data"))(
            self.update_dropdown_options
        )

        self.app.callback(
            Output("stocks-store", "data"),
            Input("once-interval", "n_intervals"),
            State("stocks-store", "data"),
        )(self.update_store_once)

        self.app.callback(
            Output("dropdown4", "options"), Input("interval-update", "n_intervals")
        )(self.update_ta_dropdown_options)

        self.app.callback(
            Output("performance-table", "data"), Input("interval-update", "n_intervals")
        )(self.update_table)

    def _setup_layout(self):

        layout = html.Div(
            [
                html.H1("Stock Price Dashboard", className="header-title"),
                dcc.Store(id="stocks-store", data=self.stocks),
                dcc.Interval(id="once-interval", interval=1000, max_intervals=1),
                html.Div(
                    [
                        dcc.Dropdown(
                            id="dropdown",
                            options=[
                                {"label": stock, "value": stock}
                                for stock in self.stocks
                            ],
                            value=self.stocks[0],
                            multi=False,
                            style={"fontFamily": "Arial"},
                            className="dropdown-menu",
                        ),
                        dcc.Dropdown(
                            id="dropdown2",
                            options=[
                                {"label": "Communication Services", "value": "XLC"},
                                {"label": "Consumer Discretionary", "value": "XLY"},
                                {"label": "Consumer Staples", "value": "XLP"},
                                {"label": "Energy", "value": "XLE"},
                                {"label": "Financials", "value": "XLF"},
                                {"label": "Health Care", "value": "XLV"},
                                {"label": "Industrials", "value": "XLI"},
                                {"label": "Information Technology", "value": "XLK"},
                                {"label": "Materials", "value": "XLB"},
                                {"label": "Real Estate", "value": "XLRE"},
                                {"label": "Utilities", "value": "XLU"},
                                {"label": None, "value": None},
                            ],
                            value=None,
                            style={"fontFamily": "Arial"},
                            className="dropdown-menu",
                        ),
                        dcc.Dropdown(
                            id="dropdown3",
                            options=[
                                {"label": "Candlestick", "value": "candlestick"},
                                {"label": "Line", "value": "line"},
                                {"label": "Buy/Sell", "value": "buy/sell"},
                                {"label": "Volume", "value": "volume"},
                                {"label": "None", "value": None},
                            ],
                            value="line",
                            style={"fontFamily": "Arial"},
                            multi=True,
                            className="dropdown-menu",
                        ),
                        dcc.Dropdown(
                            id="dropdown4",
                            options=[
                                {"label": ta_indicator, "value": ta_indicator}
                                for ta_indicator in self.ta_indicator_info
                            ]
                            + [{"label": "None", "value": None}],
                            value=None,
                            style={"fontFamily": "Arial"},
                            multi=True,
                            className="dropdown-menu",
                        ),
                    ],
                    className="dropdown-container",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        dcc.Graph(
                                            id="main-graph", className="main-graph"
                                        ),
                                        dcc.Interval(
                                            id="interval-update",
                                            interval=500,  # in milliseconds
                                            n_intervals=0,
                                        ),
                                    ],
                                    className="main-graph-container",
                                ),
                            ],
                            className="left-container",
                        ),
                        html.Div(
                            [
                                html.H2(
                                    "Additional Information",
                                    className="information-title",
                                ),
                                dash_table.DataTable(
                                    id="performance-table",
                                    columns=[
                                        {"name": "Metric", "id": "Metric"},
                                        {"name": "Value", "id": "Value"},
                                    ],
                                    style_cell={
                                        "minWidth": "150px",  # Minimum width of each cell
                                        "width": "150px",  # Ideal width of each cell
                                        "maxWidth": "150px",  # Maximum width of each cell
                                        "textAlign": "left",
                                    },
                                    data=None,
                                ),
                            ],
                            className="right-container",
                        ),
                    ],
                    className="main-container",
                ),
            ]
        )
        self.app.layout = layout

    def run(self):
        print("running server   ---------------")
        self.app.run_server()

    def update_info(self, stocks, indicators):
        self.stocks = stocks
        self.ta_indicator_info = indicators

    def update_dropdown_options(self, stocks):
        return [{"label": stock, "value": stock} for stock in stocks]

    def update_store_once(self, n_intervals, current_data):
        return self.stocks

    def update_ta_dropdown_options(self, n_intervals):
        """
        Update the options for the TA indicators dropdown.
        This callback is triggered on every interval update.
        """
        return [
            {"label": ta_indicator, "value": ta_indicator}
            for ta_indicator in self.ta_indicator_info.keys()
        ] + [{"label": "None", "value": None}]

    def update_table(self, n_intervals):
        if (
            not self.backtest_instance
            or self.backtest_instance.performance_history.empty
        ):
            return []

        row = self.backtest_instance.performance_history.iloc[-1].round(2)
        data = [{"Metric": metric, "Value": row[metric]} for metric in row.index]
        return data

    def update_graph(
        self, selected_stocks, selected_graphs, selected_indicators, n_intervals
    ):

        if not self.backtest_instance:
            return go.Figure()

        self.stock_data = self.backtest_instance.data
        self.action_data = self.backtest_instance.action_history
        self.additional_data = self.backtest_instance.portfolio_history
        self.performance_data = self.backtest_instance.performance_history

        current_timestamp = self.performance_data.index[-1]

        # print("current_timestamp", current_timestamp)

        if isinstance(selected_stocks, str):
            selected_stocks = [selected_stocks]

        indicators_with_exgraph = False
        if selected_indicators is not None:
            for ta_indicator in self.ta_indicator_info.keys():
                if (
                    ta_indicator in selected_indicators
                    and self.ta_indicator_info[ta_indicator][1]
                ):
                    indicators_with_exgraph = True
                    break

        additional_data_row = 3 if indicators_with_exgraph else 2

        if indicators_with_exgraph:
            num_rows = 3
            row_heights = [0.6, 0.2, 0.2]
            specs = [[{"secondary_y": True}], [{}], [{}]]
        else:
            num_rows = 2
            row_heights = [0.7, 0.3]
            specs = [[{"secondary_y": True}], [{}]]

        fig = make_subplots(
            rows=num_rows,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=row_heights,
            specs=specs,
        )

        for selected_stock in selected_stocks:
            df = self.stock_data[selected_stock].iloc[:current_timestamp]

            if "line" in selected_graphs:
                fig.add_scatter(
                    x=df.index,
                    y=df["Close"],
                    mode="lines",
                    name=f"{selected_stock} (Close)",
                    row=1,
                    col=1,
                )

            if "candlestick" in selected_graphs:
                fig.add_candlestick(
                    x=df.index,
                    open=df["Open"],
                    high=df["High"],
                    low=df["Low"],
                    close=df["Close"],
                    name=f"{selected_stock} (Candlestick)",
                    row=1,
                    col=1,
                )

            if "buy/sell" in selected_graphs:
                actions_df = self.action_data[selected_stock]

                # Filter buy actions
                buys = actions_df[actions_df["Type"] == "buy"]
                if not buys.empty:
                    fig.add_scatter(
                        x=buys.index,
                        y=buys["Price"],  # Changed from IdPrice to Price
                        mode="markers",
                        marker=dict(symbol="triangle-up", size=10, color="green"),
                        name=f"{selected_stock} Buys",
                        text=[f"Stop Loss: {sl}" for sl in buys["Stop Loss"]],
                        hovertemplate="%{x}<br>Price: %{y}<br>%{text}<extra></extra>",
                        row=1,
                        col=1,
                    )

                # Filter sell actions
                sells = actions_df[actions_df["Type"] == "sell"]
                if not sells.empty:
                    fig.add_scatter(
                        x=sells.index,
                        y=sells["Price"],  # Changed from IdPrice to Price
                        mode="markers",
                        marker=dict(symbol="triangle-down", size=10, color="red"),
                        name=f"{selected_stock} Sells",
                        text=[f"Stop Loss: {sl}" for sl in sells["Stop Loss"]],
                        hovertemplate="%{x}<br>Price: %{y}<br>%{text}<extra></extra>",
                        row=1,
                        col=1,
                    )

            if "volume" in selected_graphs:
                max_volume = df["Volume"].max()
                colors = [
                    "green" if c >= o else "red"
                    for c, o in zip(df["Close"], df["Open"])
                ]
                fig.add_bar(
                    x=df.index,
                    y=df["Volume"],
                    name=f"{selected_stock} Volume",
                    opacity=0.9,
                    marker_color=colors,
                    row=1,
                    col=1,
                    secondary_y=True,
                )
                fig.update_yaxes(
                    title_text="Volume",
                    secondary_y=True,
                    showgrid=False,
                    rangemode="tozero",
                    range=[0, max_volume * 3],
                )

            if selected_indicators is not None:
                for ta_indicator in self.ta_indicator_info.keys():
                    if ta_indicator in selected_indicators:
                        if not self.ta_indicator_info[ta_indicator][1]:
                            for col in self.ta_indicator_info[ta_indicator][0]:
                                fig.add_scatter(
                                    x=df.index,
                                    y=df[col],
                                    mode="lines",
                                    name=f"{ta_indicator}",
                                    row=1,
                                    col=1,
                                )
                        else:
                            for col in self.ta_indicator_info[ta_indicator][0]:
                                fig.add_scatter(
                                    x=df.index,
                                    y=df[col],
                                    mode="lines",
                                    name=f"{ta_indicator}",
                                    row=2,
                                    col=1,
                                )

        # Add portfolio data from self.additional_data
        if not self.additional_data.empty:
            fig.add_scatter(
                x=self.additional_data.index,
                y=self.additional_data["Capital"],
                mode="lines",
                name="Capital",
                row=additional_data_row,
                col=1,
            )
            fig.add_scatter(
                x=self.additional_data.index,
                y=self.additional_data["Cash"],
                mode="lines",
                name="Cash",
                row=additional_data_row,
                col=1,
            )
            fig.add_scatter(
                x=self.additional_data.index,
                y=self.additional_data["Equity"],
                mode="lines",
                name="Equity",
                row=additional_data_row,
                col=1,
            )
            fig.add_scatter(
                x=self.additional_data.index,
                y=self.additional_data["Portfolio Value"],
                mode="lines",
                name="Portfolio Value",
                row=additional_data_row,
                col=1,
            )

        fig.update_yaxes(title_text="Price", secondary_y=False)

        fig.update_layout(
            xaxis_rangeslider_visible=False,
            legend=dict(
                itemclick=False,
                itemdoubleclick=False,
                x=0.95,
                y=1,
                xanchor="left",
                yanchor="top",
            ),
            height=800,
            margin=dict(t=50),
        )

        return fig

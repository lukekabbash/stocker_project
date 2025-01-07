import dash_bootstrap_components as dbc
from dash import html, dcc
import datetime

def create_layout():
    indicators = [
        'SMA_20', 'SMA_50', 'EMA_12', 'EMA_26', 'RSI',
        'Bollinger_Bands', 'MACD', 'OBV', 'Stochastic_Oscillator'
    ]
    
    return dbc.Container([
        dbc.Row([
            dbc.Col(
                html.H1("Stocker 4.2.2", className="text-center mt-4 mb-4"),
                width=12
            )
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Input(
                    id="ticker-input",
                    type="text",
                    placeholder="Enter Tickers (comma-separated, e.g., AAPL,MSFT)",
                    className="mb-3"
                ),
                dcc.DatePickerRange(
                    id='date-picker-range',
                    min_date_allowed=datetime.date(2000, 1, 1),
                    max_date_allowed=datetime.date.today(),
                    start_date=(datetime.date.today() - datetime.timedelta(days=30)),
                    end_date=datetime.date.today(),
                    display_format='YYYY-MM-DD',
                    className="mb-3"
                ),
                dbc.Button(
                    "Fetch Data",
                    id="fetch-data-button",
                    n_clicks=0,
                    color="primary",
                    className="mb-3 w-100"
                ),
                dbc.Checklist(
                    options=[{'label': i.replace('_', ' '), 'value': i} for i in indicators],
                    value=['SMA_20', 'SMA_50'],
                    id="indicators-checklist",
                    inline=True,
                    switch=True,
                    className="mb-3 d-flex justify-content-center"
                ),
                dcc.Graph(
                    id="multi-stock-graph",
                    style={"height": "70vh", "backgroundColor": "#f8f9fa", "borderRadius": "10px"},
                    className="mb-3"
                ),
                html.Div(id="error-message", className="text-center text-danger")
            ], width=12)
        ])
    ], fluid=True, className="p-4")
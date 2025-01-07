import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.colors as colors
import pandas as pd
from typing import Dict, List

def plot_multi_stock_chart(dfs: Dict[str, pd.DataFrame], indicators: List[str]) -> go.Figure:
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
        subplot_titles=("Stock Prices and Indicators", "Volume")
    )

    color_cycle = colors.qualitative.Plotly

    for i, (ticker, df) in enumerate(dfs.items()):
        color = color_cycle[i % len(color_cycle)]
        
        # Candlestick chart
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name=ticker,
            increasing_line_color=color,
            decreasing_line_color=color.replace('rgb', 'rgba').replace(')', ', 0.5)'),
            legendgroup=ticker
        ), row=1, col=1)

        # Add indicators
        if 'SMA_20' in indicators:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df["SMA_20"],
                mode="lines",
                name=f"{ticker} SMA (20)",
                line=dict(color=color, width=1.5, dash='dot'),
                legendgroup=ticker
            ), row=1, col=1)
        
        if 'SMA_50' in indicators:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df["SMA_50"],
                mode="lines",
                name=f"{ticker} SMA (50)",
                line=dict(color=color, width=1.5, dash='dash'),
                legendgroup=ticker
            ), row=1, col=1)
        
        if 'EMA_12' in indicators:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df["EMA_12"],
                mode="lines",
                name=f"{ticker} EMA (12)",
                line=dict(color=color, width=1.5, dash='dashdot'),
                legendgroup=ticker
            ), row=1, col=1)
        
        if 'EMA_26' in indicators:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df["EMA_26"],
                mode="lines",
                name=f"{ticker} EMA (26)",
                line=dict(color=color, width=1.5, dash='longdash'),
                legendgroup=ticker
            ), row=1, col=1)
        
        if 'RSI' in indicators:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df["RSI"],
                mode="lines",
                name=f"{ticker} RSI",
                yaxis="y3",
                line=dict(color=color, width=1.5),
                legendgroup=ticker
            ), row=1, col=1)
        
        if 'Bollinger_Bands' in indicators:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df["Upper_BB"],
                mode="lines",
                name=f"{ticker} Upper BB",
                line=dict(color=color, width=1),
                legendgroup=ticker
            ), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df["Lower_BB"],
                mode="lines",
                name=f"{ticker} Lower BB",
                line=dict(color=color, width=1),
                legendgroup=ticker,
                fill='tonexty',
                fillcolor='rgba(173,216,230,0.2)'
            ), row=1, col=1)
        
        if 'MACD' in indicators:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df["MACD"],
                mode="lines",
                name=f"{ticker} MACD",
                yaxis="y4",
                line=dict(color=color, width=1.5),
                legendgroup=ticker
            ), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df["Signal_Line"],
                mode="lines",
                name=f"{ticker} Signal Line",
                yaxis="y4",
                line=dict(color=color, width=1, dash='dash'),
                legendgroup=ticker
            ), row=1, col=1)
        
        if 'OBV' in indicators:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df["OBV"],
                mode="lines",
                name=f"{ticker} OBV",
                yaxis="y5",
                line=dict(color=color, width=1.5),
                legendgroup=ticker
            ), row=1, col=1)
        
        if 'Stochastic_Oscillator' in indicators:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df["%K"],
                mode="lines",
                name=f"{ticker} %K",
                yaxis="y6",
                line=dict(color=color, width=1.5),
                legendgroup=ticker
            ), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df["%D"],
                mode="lines",
                name=f"{ticker} %D",
                yaxis="y6",
                line=dict(color=color, width=1, dash='dash'),
                legendgroup=ticker
            ), row=1, col=1)

        # Volume bar chart
        fig.add_trace(go.Bar(
            x=df.index,
            y=df["Volume"],
            name=f"{ticker} Volume",
            marker_color=color.replace('rgb', 'rgba').replace(')', ', 0.5)'),
            legendgroup=ticker
        ), row=2, col=1)

    # Layout updates for cleaner UI
    fig.update_layout(
        hovermode="x unified",
        dragmode="zoom",
        margin=dict(l=20, r=20, t=40, b=20),
        template="plotly_white",
        legend=dict(
            orientation='h',
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10)
        ),
        font=dict(size=12)
    )

    # Add secondary y-axes for indicators
    fig.update_layout(
        yaxis2=dict(
            title="SMA/EMA",
            overlaying='y',
            side='right'
        ),
        yaxis3=dict(
            title="RSI",
            anchor="free",
            overlaying='y',
            side='right',
            position=1.015
        ),
        yaxis4=dict(
            title="MACD",
            anchor="x",
            overlaying='y',
            side='right',
            position=1.03
        ),
        yaxis5=dict(
            title="OBV",
            anchor="x",
            overlaying='y',
            side='right',
            position=1.045
        ),
        yaxis6=dict(
            title="Stochastic",
            anchor="x",
            overlaying='y',
            side='right',
            position=1.06
        )
    )

    # Range selectors and sliders
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(visible=True),
            type="date"
        )
    )

    return fig
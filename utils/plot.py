import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from utils.utils import prev_day

def k_chart(selected, df):
    df_selected = pd.DataFrame({
        'Open': df['open_price'][selected].values,
        'High': df['high_price'][selected].values,
        'Low': df['low_price'][selected].values,
        'Close': df['close_price'][selected].values,
        'Volume': df['volume'][selected].values/1000,
    })
    df_selected.index = df['open_price'].index
    # df_selected = df_selected.loc[prev_day(20):prev_day(1)]

    # Create a plotly figure
    fig = go.Figure()

    # Add candlestick chart for price data
    fig.add_trace(go.Candlestick(x=df_selected.index,
                    open=df_selected['Open'],
                    high=df_selected['High'],
                    low=df_selected['Low'],
                    close=df_selected['Close'],
                    increasing_line_color= 'red', 
                    decreasing_line_color= 'green'))

    # Add layout details
    fig.update_layout(xaxis_rangeslider_visible=False,
                      # title='Stock Closing Prices',
                      xaxis_title='Date',
                      yaxis_title='Price')

    # Return the figure
    return fig

def institutional_chart (selected, df):
    out_df = pd.DataFrame({
        'foreign_invest': df['foreign_invest'][selected].values/1000,
        'investment_trust': df['investment_trust'][selected].values/1000,
        'dealer_trade': df['dealer_trade'][selected].values/1000,
    })
    out_df.index = df['foreign_invest'].index
    # out_df = out_df.loc[prev_day(14):prev_day(1)]
    close = df['close_price'][selected] #.loc[prev_day(14):prev_day(1)]

    # Create a plotly figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=out_df.index,
        y=close,
        name='收盤價',
        yaxis='y2',
        marker_color='gray'
        
    ))
    # Add traces for each series
    fig.add_trace(go.Bar(
        x=out_df.index,
        y=out_df['foreign_invest'],
        name='外資',
        marker_color='#489FD4'
    ))
    
    fig.add_trace(go.Bar(
        x=out_df.index,
        y=out_df['investment_trust'],
        name='投信',
        marker_color='#8437DF'
    ))

    fig.add_trace(go.Bar(
        x=out_df.index,
        y=out_df['dealer_trade'],
        name='自營商',
        marker_color='#E89849'
    ))

    # Update layout to stack bars and add secondary y-axis
    fig.update_layout(
        barmode='relative',
        yaxis2={'overlaying': 'y', 'side': 'right'},
    )

    # Return the figure
    return fig


def metric (selected, df):
    price = df['close_price'].loc[prev_day(1)][selected]
    price_1 = df['close_price'].loc[prev_day(2)][selected]
    delta = price - price_1
    delta_persent = (price-price_1)/price_1*100
    st.metric(label=selected, value=price, delta=f'{delta:.2f} ({delta_persent:.2f}%)',delta_color="inverse")

def highlight_color(row):
    color_list = ['' for _ in row.index]

    # Check if '現價' is less than '買入'
    if row['現價'] < row['買入']:
        color_list[row.index.get_loc('現價')] = 'color: green'
    else:
        color_list[row.index.get_loc('現價')] = 'color: red'

    # Check if '損益' is less than 8%
    if row['損益'] < -8:
        color_list[row.index.get_loc('損益')] = 'background-color: #5eae76'
    elif row['損益'] > 8:
        color_list[row.index.get_loc('損益')] = 'background-color: #de796e'
        
    return color_list


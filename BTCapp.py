import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import talib as ta
from ta.trend import MACD
from ta.momentum import StochasticOscillator
import streamlit as st


# Plotly theme
pio.templates.default = "plotly_dark"


# Load data
df = pd.read_csv('btc.csv')

# Change 'Date' type object to datetime
df['Date'] = pd.to_datetime(df['Date'])


# Streamlit page 
st.set_page_config(layout='wide')


### Streamlit widgets ###

# SMA options
bool_SMA1 = st.sidebar.toggle('SMA 1')
window_SMA1 = st.sidebar.number_input('', min_value=10, max_value=200, placeholder=100)
bool_SMA2 = st.sidebar.toggle('SMA 2')
window_SMA2 = st.sidebar.number_input('', min_value=10, max_value=200, placeholder=50)

# Boillinger Bands
box_options = []
if bool_SMA1:
    box_options.append('SMA1') 
if bool_SMA2:
    box_options.append('SMA2') 
bool_Boillinger = st.sidebar.toggle('Boillinger Bands')
SMA_boillinger = st.sidebar.selectbox('SMA', box_options)  


### Creating columns with widgets values ###

# moving average
df['SMA1'] = ta.SMA(df['Close'], window_SMA1)

df['SMA2'] = ta.EMA(df['Close'], window_SMA2)

def create_boillinger_bands(SMA):
    df['SMA Boillinger Bands'] = ta.EMA(df['Close'], window_SMA2 if SMA == 'SMA2' else
                                        window_SMA1)
    #std
    df['STD'] = df['Close'].rolling(
        window_SMA2 if SMA == 'SMA2' else window_SMA1).std(ddof = 0)

create_boillinger_bands(SMA_boillinger)


### More indicators ###

# Stochastic Ocillator
stoch = StochasticOscillator(high=df['High'],
                             close=df['Close'],
                             low=df['Low'],
                             window=14,
                             smooth_window=3)

# MACD
macd = MACD(close=df['Close'],
            window_slow=26,
            window_fast=12,
            window_sign=9)


### Streamlit plot ###

col1, col2 = st.columns(2)

fig = make_subplots(rows=4, cols=1, shared_xaxes=True,
                    vertical_spacing=0.01,
                    row_heights=[0.5,0.1,0.2,0.2])

# Candle
fig.add_trace(go.Candlestick(x=df['Date'],
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='BTC'),
              row=1, 
              col=1
              )
fig.update_layout(xaxis_rangeslider_visible=False)

# SMA1
if bool_SMA1:
    fig.add_trace(go.Scatter(x=df['Date'], 
               y=df['SMA1'], 
               mode='lines', 
               name='SMA{}'.format(window_SMA1),
               line= dict(color='#0000b2')),
               row=1, 
               col=1
               )

# SMA2
if bool_SMA2:
    fig.add_trace(go.Scatter(x=df['Date'], 
               y=df['SMA2'], 
               mode='lines', 
               name='SMA{}'.format(window_SMA2),
               line= dict(color='#006600')),
               row=1, 
               col=1
               )

if bool_Boillinger:
    # Upper
    fig.add_trace(go.Scatter(x = df['Date'],
                            y = df['SMA Boillinger Bands'] + (df['STD'] * 2),
                            line_color = 'gray',
                            line = {'dash': 'dash'},
                            name = 'upper band',
                            opacity = 0.5),
                row = 1, col = 1)

    # Lower
    fig.add_trace(go.Scatter(x = df['Date'],
                            y = df['SMA Boillinger Bands'] - (df['STD'] * 2),
                            line_color = 'gray',
                            line = {'dash': 'dash'},
                            fill = 'tonexty',
                            name = 'lower band',
                            opacity = 0.5),
                row = 1, col = 1)

# Volume
colors = ['green' if row['Open'] - row['Close'] >= 0
          else 'red' for index, row in df.iterrows()]

fig.add_trace(go.Bar(x=df['Date'], 
                     y=df['Volume'], 
                     showlegend=False, 
                     marker_color=colors),
              row=2, 
              col=1
              )

# MACD
colors = ['green' if val >= 0
          else 'red' for val in macd.macd_diff()]
fig.add_trace(go.Bar(x=df['Date'],
                     y=macd.macd_diff(),
                     marker_color=colors), 
              row=3, 
              col=1
              )
fig.add_trace(go.Scatter(x=df['Date'],
                         y=macd.macd(),
                         line=dict(color='black', width=2)
                        ), 
              row=3, 
              col=1
              )
fig.add_trace(go.Scatter(x=df['Date'],
                         y=macd.macd_signal(),
                         line=dict(color='blue', width=1)
                        ), 
              row=3, 
              col=1
              )


# Stochastic Ocillator
fig.add_trace(go.Scatter(x=df['Date'],
                         y=stoch.stoch(),
                         line=dict(color='black', width=2)
                        ), row=4, col=1)
fig.add_trace(go.Scatter(x=df['Date'],
                         y=stoch.stoch_signal(),
                         line=dict(color='blue', width=1)
                        ), row=4, col=1)

# Update layout
fig.update_layout(height=900, width=1200,
                  showlegend=False,
                  xaxis_rangeslider_visible=False)

# Update y-axis label
fig.update_yaxes(title_text="BTC", row=1, col=1)
fig.update_yaxes(title_text="Volume", row=2, col=1)
fig.update_yaxes(title_text="MACD", showgrid=False, row=3, col=1)
fig.update_yaxes(title_text="Stoch", row=4, col=1)


col1.plotly_chart(fig)


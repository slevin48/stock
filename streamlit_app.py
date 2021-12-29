import streamlit as st
import pandas as pd
import numpy as np

# for reproducibility of our results
np.random.seed(42)

from datetime import date
from matplotlib import pyplot as plt

from sklearn.preprocessing import StandardScaler
from keras.models import Model
from keras.layers import Dense, LSTM, Input

import tensorflow as tf 
tf.random.set_seed(42)

import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
import urllib.request, json

from helpers import *

api_key = st.secrets["alphavantage_key"]
# stock ticker symbol
# ticker = 'SAF.PA' 
ticker = st.sidebar.text_input("Ticker",value="SAF.PA")

# JSON file with all the stock prices data 
url_string = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=%s&outputsize=full&apikey=%s"%(ticker,api_key)

def search(ticker):
    url_search = "https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=%s&apikey=%s"%(ticker,api_key)
    with urllib.request.urlopen(url_search) as url:
        data = json.loads(url.read().decode())
    return data

keyword = search(ticker)
name = keyword['bestMatches'][0]['2. name']
st.sidebar.text(name)

t = st.sidebar.checkbox("Display Table")
save = st.sidebar.checkbox("Save Table")
sma = st.sidebar.checkbox("Simple Moving Average")
ema = st.sidebar.checkbox("Exponential Moving Average")
# lstm = st.sidebar.checkbox("Long Short-Term Memory")

window_size = 50
window_var = str(window_size) + 'day'


@st.cache(allow_output_mutation=True)
def load_data():
### get the low, high, close, and open prices 
    with urllib.request.urlopen(url_string) as url:
        data = json.loads(url.read().decode())
        # pull stock market data
        data = data['Time Series (Daily)']
        df = pd.DataFrame(columns=['Date','Low','High','Close','Open'])
        for key,val in data.items():
            date = dt.datetime.strptime(key, '%Y-%m-%d')
            data_row = [date.date(),float(val['3. low']),float(val['2. high']),
                        float(val['4. close']),float(val['1. open'])]
            df.loc[-1,:] = data_row
            df.index = df.index + 1
    return df

st.title("📈 "+name)

df = load_data()
stockprices = df.sort_values('Date')

fig, ax = plt.subplots()
ax.plot(df['Date'],df['Close'])
st.pyplot(fig)


if t:    
    st.dataframe(df)
    # st.table(df)


if save:
    # Save data to this file
    fileName = 'stock_market_data-%s.csv'%ticker
    df.to_csv("data/"+fileName)

if sma:
    st.markdown("## Simple Moving Average")
       
    stockprices[window_var] = stockprices['Close'].rolling(window_size).mean()
    ### Include a 200-day SMA for reference 
    stockprices['200day'] = stockprices['Close'].rolling(200).mean()
        
    ### Plot and performance metrics for SMA model
    fig, ax = plt.subplots()
    ax.plot(stockprices['Date'],stockprices[['Close', window_var,'200day']])
    plt.grid(False)
    plt.title('Simple Moving Average - '+name)
    plt.axis('tight')
    plt.ylabel('Stock Price ($)')
    st.pyplot(fig)

if ema:
    st.markdown("## Exponential Moving Average")
        
    ###### Exponential MA
    window_ema_var = window_var+'_EMA'
    # Calculate the 50-day exponentially weighted moving average
    stockprices[window_ema_var] = df['Close'].ewm(span=window_size, adjust=False).mean()
    stockprices['200day'] = df['Close'].rolling(200).mean()
          
    ### Plot and performance metrics for EMA model
    fig, ax = plt.subplots()
    ax.plot(stockprices['Date'],stockprices[['Close', window_ema_var,'200day']])
    plt.grid(False)
    plt.title('Exponential Moving Average - '+name)
    plt.axis('tight')
    plt.ylabel('Stock Price ($)')
    st.pyplot(fig)

# st.markdown("## Long Short-Term Memory")



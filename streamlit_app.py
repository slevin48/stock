import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import urllib.request, json
from helpers import *

api_key = st.secrets["alphavantage_key"]
# stock ticker symbol
# ticker = 'SAF.PA' 
ticker = st.sidebar.text_input("Ticker",value="SAF.PA")

def search(ticker):
    url_search = "https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=%s&apikey=%s"%(ticker,api_key)
    try:
        with urllib.request.urlopen(url_search) as url:
            data = json.loads(url.read().decode())
            name = data['bestMatches'][0]['2. name']
    except:
        name = "Ticker not found"
    return name


def dummy_data():
    data = {
        'Date': ['2020-01-01', '2020-01-02', '2020-01-03', '2020-01-04', '2020-01-05'],
        'Low': [1, 2, 3, 4, 5],
        'High': [2, 3, 4, 5, 6],
        'Close': [3, 4, 5, 6, 7],
        'Open': [4, 5, 6, 7, 8]
    }
    df = pd.DataFrame(data)
    return df


@st.cache_data
def load_data(ticker):
    ### get the low, high, close, and open prices 
    url_string = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=%s&outputsize=full&apikey=%s"%(ticker,api_key)
    try:
        with urllib.request.urlopen(url_string) as url:
            data = json.loads(url.read().decode())
            # pull stock market data
            data = data['Time Series (Daily)']
            df = pd.DataFrame(columns=['Date','Low','High','Close','Open'])
            for key,val in data.items():
                date = datetime.strptime(key, '%Y-%m-%d')
                data_row = [date.date(),float(val['3. low']),float(val['2. high']),
                            float(val['4. close']),float(val['1. open'])]
                df.loc[-1,:] = data_row
                df.index = df.index + 1
    except:
        df = pd.read_csv('data/stock_market_data-%s.csv'%ticker)
    return df

name = search(ticker)
st.sidebar.text(name)

t = st.sidebar.checkbox("Display Table")
sma = st.sidebar.checkbox("Simple Moving Average")
ema = st.sidebar.checkbox("Exponential Moving Average")

window_size = 50
window_var = str(window_size) + 'day'

st.title("📈 "+ ticker)

df = load_data(ticker)
# df = dummy_data()
stockprices = df.sort_values('Date')

fig, ax = plt.subplots()
ax.plot(df['Date'],df['Close'])
st.pyplot(fig)


if t:    
    # df without index
    st.sidebar.dataframe(df)
    # st.table(df)
    st.sidebar.download_button(label="Download data as CSV",data=df.to_csv(),file_name=f'stock_market_data-{ticker}.csv',mime='text/csv')
    # # Save data to this file
    # fileName = 'stock_market_data-%s.csv'%ticker
    # df.to_csv("data/"+fileName)

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



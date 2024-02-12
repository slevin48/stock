import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
# import pandas_datareader.data as pdr
import yfinance as yf
import datetime

param = st.experimental_get_query_params()
# st.sidebar.write(param)

if 'ticker' in param:
    ticker = param['ticker'][0]
    ticker = st.sidebar.text_input("Ticker",value=ticker)
else:
    ticker = st.sidebar.text_input("Ticker",value='AIR.PA')

# st.title(f'{ticker} 📈')

start_date = datetime.datetime(2024, 1, 1)
end_date = datetime.date.today()
start_date = st.sidebar.date_input('Start date', value=start_date)
end_date = st.sidebar.date_input('End date', value=end_date)
df = yf.download(ticker, start=start_date, end=end_date)
# df = pdr.DataReader(ticker, data_source="yahoo", start="2024-01-01", end="2024-01-31")

fig, ax = plt.subplots()
ax.plot(df.index,df['Close'])
st.pyplot(fig)

if st.sidebar.checkbox('Show raw data'):
    st.write(df)

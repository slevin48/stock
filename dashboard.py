import streamlit as st
import pandas as pd
import yfinance as yf
import os

st.title('Stock simulator 📈')

# password = st.sidebar.text_input('Password', type='password')

def load_data():
    # p = os.listdir('positions/')
    # df = pd.read_csv('positions/' + p[0], sep=';')
    df = pd.read_csv('portfolio.csv')
    return df

df = load_data()
# st.dataframe(df)

# retrieve last price for each stock
df['lastPrice'] = df['ticker'].apply(lambda x: yf.Ticker(x).history(period='1d').iloc[-1]['Close'])

# compute quantity x buying price
df['amount'] = df['quantity'] * df['lastPrice']
st.sidebar.write('Total amount: {:.2f}'.format(df['amount'].sum()))

# compute amout variation
df['amountVariation'] = (df['lastPrice'] - df['buyingPrice']) * df['quantity']

# compute variation
df['variation'] = (df['lastPrice'] - df['buyingPrice']) / df['buyingPrice'] * 100

# Compute the total amount variation
st.sidebar.write('Total amount variation: {:.2f}'.format(df['amountVariation'].sum()))

# add a column to the dataframe with a link to the stock page for each stock
df['link'] = df['ticker'].apply(lambda x: f'[view](/stock?ticker={x})')

# Convert the dataframe to markdown
md = df.to_markdown(index=False)
st.write(md)
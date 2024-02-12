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

def buy(ticker, quantity):
    df = load_data()
    try: # Check that the ticker is valid
        new_buying_price = yf.Ticker(ticker).history(period='1d').iloc[-1]['Close']
        if ticker in df['ticker'].values: # Check if the ticker already exists in the DataFrame
            # Update the quantity and recalculate the average buying price
            existing_row_index = df.index[df['ticker'] == ticker][0]
            existing_quantity = df.at[existing_row_index, 'quantity']
            existing_buying_price = df.at[existing_row_index, 'buyingPrice']
            
            new_total_quantity = existing_quantity + quantity
            new_average_buying_price = ((existing_quantity * existing_buying_price) + (quantity * new_buying_price)) / new_total_quantity
            
            # Update the DataFrame with new quantity and average buying price
            df.at[existing_row_index, 'quantity'] = new_total_quantity
            df.at[existing_row_index, 'buyingPrice'] = new_average_buying_price
        else:
            # Add a new row if the ticker doesn't exist
            new_row = {'ticker': ticker, 'quantity': quantity, 'buyingPrice': new_buying_price}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    except:
        st.error('Invalid ticker')

    # append the new position to the dataframe
    df.to_csv('portfolio.csv', index=False)

with st.sidebar.form('Add a new position'):
    ticker = st.text_input('Ticker')
    quantity = st.number_input('Quantity', min_value=1)
    if st.form_submit_button("Buy"):
        buy(ticker, quantity)

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
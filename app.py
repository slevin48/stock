import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from alpha_vantage.timeseries import TimeSeries

def fetch_stock_data(symbol, api_key):
    """
    Fetches daily historical stock data from Alpha Vantage and returns it as a DataFrame.
    """
    ts = TimeSeries(key=api_key, output_format='pandas')
    try:
        data, meta_data = ts.get_daily(symbol=symbol, outputsize='full')
    except Exception as e:
        st.write(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

    if not data.empty:
        data = data.rename(
            columns={
                '1. open': 'Open',
                '2. high': 'High',
                '3. low': 'Low',
                '4. close': 'Close',
                '5. volume': 'Volume'
            }
        )
        data['Date'] = data.index
        data = data.sort_values('Date')
    return data

def main():
    # Streamlit App Title
    st.title("Veolia (VEOEY) Stock Analysis")

    # Alpha Vantage API Key 
    api_key = st.secrets["ALPHAVANTAGE_API_KEY"]

    # Fetch Veolia data
    symbol = "VEOEY"
    data = fetch_stock_data(symbol, api_key)

    if data.empty:
        st.error("No data available for Veolia (VEOEY).")
        return

    # --- Data Preprocessing and Calculations ---
    # Moving Averages
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['MA50'] = data['Close'].rolling(window=50).mean()
    data['MA200'] = data['Close'].rolling(window=200).mean()

    # Calculate daily returns
    data['Daily Return'] = data['Close'].pct_change()

    # Calculate cumulative returns
    data['Cumulative Return'] = (1 + data['Daily Return']).cumprod()

    # --- Display Raw Data (Optional) ---
    st.subheader("Raw Historical Data")
    st.dataframe(data[['Date','Open','High','Low','Close','Volume']].tail(10))

    # --- Plot 1: Price + Moving Averages ---
    st.subheader("Price and Moving Averages")
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(data['Date'], data['Close'], label='Close Price')
    ax1.plot(data['Date'], data['MA20'], label='20-Day MA')
    ax1.plot(data['Date'], data['MA50'], label='50-Day MA')
    ax1.plot(data['Date'], data['MA200'], label='200-Day MA')
    ax1.set_title('Veolia Stock Price and Moving Averages')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Price')
    ax1.legend()
    st.pyplot(fig1)

    # --- Plot 2: Daily Returns ---
    st.subheader("Daily Returns")
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.plot(data['Date'], data['Daily Return'], label='Daily Return')
    ax2.set_title('Veolia Daily Returns')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Daily Return')
    ax2.legend()
    st.pyplot(fig2)

    # --- Plot 3: Cumulative Returns ---
    st.subheader("Cumulative Returns")
    fig3, ax3 = plt.subplots(figsize=(10, 5))
    ax3.plot(data['Date'], data['Cumulative Return'], label='Cumulative Return')
    ax3.set_title('Veolia Cumulative Returns')
    ax3.set_xlabel('Date')
    ax3.set_ylabel('Cumulative Return')
    ax3.legend()
    st.pyplot(fig3)

    # --- Correlation Analysis with Another Stock (e.g., AWK) ---
    st.subheader("Correlation Analysis with AWK (American Water Works)")

    symbol2 = "AWK"
    data2 = fetch_stock_data(symbol2, api_key)

    if data2.empty:
        st.warning("No data available for AWK.")
        return

    # Merge on Date
    merged_data = pd.merge(
        data[['Date', 'Close']], 
        data2[['Date', 'Close']], 
        on='Date', 
        suffixes=('_VEOEY', '_AWK')
    )
    
    # Calculate correlation
    correlation = merged_data['Close_VEOEY'].corr(merged_data['Close_AWK'])
    st.write(f"Correlation between VEOEY and AWK: **{correlation:.4f}**")

    # Plot correlation matrix
    corr_matrix = merged_data[['Close_VEOEY', 'Close_AWK']].corr()

    fig4, ax4 = plt.subplots(figsize=(5, 4))
    cax = ax4.matshow(corr_matrix)
    fig4.colorbar(cax)
    ax4.set_xticks([0,1])
    ax4.set_yticks([0,1])
    ax4.set_xticklabels(['VEOEY','AWK'])
    ax4.set_yticklabels(['VEOEY','AWK'])
    ax4.set_title("Correlation Matrix", pad=20)
    st.pyplot(fig4)

if __name__ == "__main__":
    main()

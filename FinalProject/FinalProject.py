import streamlit as st
from streamlit_lottie import st_lottie
import pandas as pd
import numpy as np
import requests
import alpha_vantage.timeseries as ts
import plotly.graph_objs as go


api_key="AGZF6FYUWEB9KXYS"

#Function to load lottie animation
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()
#Load lottie animation
lottie_url = load_lottieurl("https://lottie.host/ac95cf1d-99bf-427c-a627-0a6210faa989/iFSpdXBs9n.json")

#Function to fetch financial data
def fetch_financial_data(symbol):
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}'
    response = requests.get(url)
    return response.json()

def fetch_stock_data(symbol):
    av = ts.TimeSeries(key=api_key, output_format='pandas')
    data, meta_data = av.get_daily(symbol=symbol, outputsize='full')
    return data

col1, col2= st.columns(2)
with col1:
    st.title("financity")
    st.subheader("all your financial data in one place.")
    st.button('Get Started', type="primary")
    
    # User inputs the stock symbol
    symbol = st.text_input('Ticker Symbol', '')

    # Fetch and display data when a symbol is entered
    if symbol:
        data = fetch_financial_data(symbol)
        if data:
            # Define the keys you are interested in
            keys_of_interest = ['Symbol', 'AssetType', 'Name', 'Sector', 'Industry', 'Country']

            # Extract these keys and values
            filtered_data = {key: data.get(key, 'N/A') for key in keys_of_interest}

            # Convert filtered data to DataFrame
            df = pd.DataFrame([filtered_data])
            st.dataframe(df, hide_index=True)
        else:
            st.error("No data found for the given symbol.")  # Displaying the data as JSON. You can format it as needed.

with col2:
    st_lottie(lottie_url, height=400, width='100%', key="line")

if symbol:
    stock_data = fetch_stock_data(symbol)
    if not stock_data.empty:
        candlestick = go.Candlestick(x=stock_data.index,
                                        open=stock_data['1. open'],
                                        high=stock_data['2. high'],
                                        low=stock_data['3. low'],
                                        close=stock_data['4. close'])
        layout = go.Layout(title=f'Stock Chart for {symbol}',
                            xaxis=dict(title='Date'),
                            yaxis=dict(title='Stock Price'))
        fig = go.Figure(data=[candlestick], layout=layout)
        st.plotly_chart(fig)
    else:
        st.warning("No historical stock data found for the given symbol.")
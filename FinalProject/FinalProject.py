import streamlit as st
from streamlit_lottie import st_lottie
import pandas as pd
import numpy as np
import requests
import alpha_vantage.timeseries as ts
import plotly.graph_objs as go
from datetime import date
from geopy.geocoders import Nominatim
import csv

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

    try:
        data, meta_data = av.get_daily(symbol=symbol, outputsize='full')
        return data
    except ValueError as e:
        if "Invalid API call" in str(e):
            return None
        else:
            return None
st.set_page_config(
    page_title="Financity"
)
        
    
def get_latitude_longitude(location_of_interest):
    geolocator = Nominatim(user_agent="financity")
    location = geolocator.geocode(location_of_interest)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

col1, col2= st.columns(2)

with col1:
    st.title(":blue[financity]")
    st.subheader("all your financial data in one place.")

    st.markdown("Financity makes stock analysis a breeze! Just type in your ticker, and voilà – all the financial insights you need at your fingertips. It's as simple as 1, 2, 3 – :blue[enter, explore, excel!]")



with col2:
    st_lottie(lottie_url, height=400, width='100%', key="line")

st.divider()

# User inputs the stock symbol
st.subheader(":blue[Let's Get Started!]")
symbol = st.text_input('Ticker Symbol', '')

# Fetch and display data when a symbol is entered
if symbol:
    data = fetch_financial_data(symbol)
    if data:
        # Define the keys you are interested in
        keys_of_interest = ['Symbol', 'AssetType', 'Name', 'Sector', 'Industry', 'Country', 'Address']

        # Extract these keys and values
        filtered_data = {key: data.get(key, 'N/A') for key in keys_of_interest}

        # Convert filtered data to DataFrame
        df = pd.DataFrame([filtered_data])
        st.dataframe(df, hide_index=True)
        
        # Get latitude and longitude for the address
        address = data.get('Address', None)
        if address:
            latitude, longitude = get_latitude_longitude(address)
            map_data = pd.DataFrame({'lat': [latitude], 'lon': [longitude]})
            st.map(map_data)
        else:
            st.write("No address available.")

        st.success(f"Successfully fetched data for {symbol.upper()}")
    else:
        st.error(f"No data found for the given symbol: {symbol.upper()}")

if symbol:

    stock_data = fetch_stock_data(symbol)
    
    if stock_data is not None:
        if not stock_data.empty:
            show_line_chart = st.checkbox("Show Line Graph", value=True)

            if show_line_chart:
                line_chart = go.Figure()
                line_chart.add_trace(go.Scatter(x=stock_data.index, y=stock_data['4. close'], mode='lines', name='Closing Price'))
                line_chart.update_layout(title=f'Stock Chart for {symbol.upper()}', xaxis_title='Date', yaxis_title='Stock Price')
                st.plotly_chart(line_chart)

            show_volume_chart = st.checkbox("Show Volume Graph", value=True)
            
            if show_volume_chart:
                    volume_chart = go.Figure()
                    volume_chart.add_trace(go.Bar(x=stock_data.index, y=stock_data['5. volume'], name='Volume'))
                    volume_chart.update_layout(title=f'Volume Chart for {symbol.upper()}', xaxis_title='Date', yaxis_title='Volume')
                    st.plotly_chart(volume_chart)

        
    else:
        st.warning("No historical stock data found for the given symbol.")

def loadSMA():
    url = f'https://www.alphavantage.co/query?function=SMA&symbol={symbol}&interval=weekly&time_period=10&series_type=open&apikey={api_key}'
    r = requests.get(url)

    data = r.json()

    # Extract data
    sma_data = data['Technical Analysis: SMA']
    df = pd.DataFrame(sma_data).transpose()
    df.index = pd.to_datetime(df.index)
    df['SMA'] = df['SMA'].astype(float)
    return df

def loadEMA():
    url = f'https://www.alphavantage.co/query?function=EMA&symbol={symbol}&interval=weekly&time_period=10&series_type=open&apikey={api_key}'
    r = requests.get(url)

    data = r.json()

    # Extract data
    ema_data = data['Technical Analysis: EMA']
    df = pd.DataFrame(ema_data).transpose()
    df.index = pd.to_datetime(df.index)
    df['EMA'] = df['EMA'].astype(float)
    return df


if symbol:
    # Display the option to select technical indicators
    option = st.radio('View technical indicators', ['SMA', 'EMA', 'Disabled'])

    if option == 'SMA':
        df_sma = loadSMA()
        st.line_chart(df_sma['SMA'])
        with st.expander("What is the SMA?"):
            st.write("The Simple Moving Average (SMA) is a widely used technical indicator in financial analysis, particularly in the analysis of stock and other asset prices.")

    elif option == 'EMA':
        df_ema = loadEMA()
        st.line_chart(df_ema['EMA'])
        with st.expander("What is the EMA?"):
            st.write("The Exponential Moving Average (EMA) is another key technical indicator used in financial markets, particularly in the analysis of stock, forex, and other tradable assets' prices.")

st.divider()
st.subheader("Earnings Calendar")
#THIS IS BROKEN, If you wanna try and fix go ahead if not just remove
# if 'tickers' not in st.session_state:
#     st.session_state['tickers'] = []

# # Text input for the ticker symbol
# ticker_symbol = st.text_input("Enter the ticker symbol")

# # Button to add the ticker to the list
# if st.button("Add Ticker"):
#     if ticker_symbol:
#         if ticker_symbol not in st.session_state['tickers']:
#             st.session_state['tickers'].append(ticker_symbol)
#             st.success(f"Ticker {ticker_symbol} added!")
#         else:
#             st.warning(f"Ticker {ticker_symbol} is already in the list.")
#     else:
#         st.error("Please enter a ticker symbol.")

# Concatenate ticker symbols into a string
# tickers_str = ','.join(st.session_state['tickers'])

# def advancedAnalytics(start_date, end_date):
#     url = f'https://alphavantageapi.co/timeseries/analytics?SYMBOLS={tickers_str}&RANGE={start_date}&RANGE={end_date}&INTERVAL=DAILY&OHLC=close&CALCULATIONS=MEAN,STDDEV,CORRELATION&apikey={api_key}'
#     r = requests.get(url)
#     data = r.json()

#     if 'payload' in data and 'RETURNS_CALCULATIONS' in data['payload']:
#         symbolAnalytics = data['payload']['RETURNS_CALCULATIONS']
#         df = pd.DataFrame(symbolAnalytics)
#         return df
#     else:
#         return pd.DataFrame()  # Return an empty DataFrame if no data

# # Date range input
# d = st.date_input("Select the range in which you want to see the company's analytics", value=(date.today(), date.today()), format="YYYY-MM-DD")

# start_date, end_date = d

# if start_date and end_date:
#     analytics_df = advancedAnalytics(start_date, end_date)
#     if not analytics_df.empty:
#         st.table(analytics_df)
#     else:
#         st.error("No analytics data found for the selected date range.")
# else:
#     st.error("Please select a valid date range.")
#End of broken code

horizon = st.selectbox('What horizon would you like to see?', ('3month', '6month', '12month'))

def loadEarningsCalendar():
    url = f'https://www.alphavantage.co/query?function=EARNINGS_CALENDAR&symbol={symbol}&horizon={horizon}&apikey={api_key}'

    with requests.Session() as s:
        download = s.get(url)
        decoded_content = download.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        my_list = list(cr)
        df = pd.DataFrame(my_list[1:], columns=my_list[0])  # Assuming first row is header
        st.dataframe(df)
if symbol:
    loadEarningsCalendar()





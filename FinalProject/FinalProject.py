import streamlit as st
from streamlit_lottie import st_lottie
import pandas as pd
import numpy as np
import requests
import alpha_vantage.timeseries as ts
import plotly.graph_objs as go
from datetime import date, timedelta
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import csv

api_key = "AGZF6FYUWEB9KXYS"

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


lottie_url = load_lottieurl("https://lottie.host/ac95cf1d-99bf-427c-a627-0a6210faa989/iFSpdXBs9n.json")


def fetch_financial_data(symbol):
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}'
    response = requests.get(url)
    return response.json()


def fetch_stock_data(symbol, start_date, end_date):
    av = ts.TimeSeries(key=api_key, output_format='pandas')

    try:
        data, meta_data = av.get_daily(symbol=symbol, outputsize='full')
        
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        data = data[(data.index >= start_date) & (data.index <= end_date)]
        
        return data
    except ValueError as e:
        if "Invalid API call" in str(e):
            return None
        else:
            return None


st.set_page_config(page_title="Financity")


def get_latitude_longitude(location_of_interest):
    geolocator = Nominatim(user_agent="financity", timeout=10)
    try:
        location = geolocator.geocode(location_of_interest)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except GeocoderTimedOut:
        st.error("Geocoding timed out. Please try again later.")
        return None, None
    except GeocoderUnavailable:
        st.error("Geocoding service is unavailable. Please try again later.")
        return None, None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None, None


col1, col2 = st.columns(2)

with col1:
    st.title(":blue[financity]")
    st.subheader("all your financial data in one place.")
    st.markdown("Financity makes stock analysis a breeze! Just type in your ticker, and voilà – all the financial insights you need at your fingertips. It's as simple as 1, 2, 3 – :blue[enter, explore, excel!]")

with col2:
    st_lottie(lottie_url, height=400, width='100%', key="line")

st.divider()

st.subheader(":blue[Let's Get Started!]")
symbol = st.text_input('Ticker Symbol', '')

d = st.date_input("Select the date range", value=(date.today() - timedelta(days=365), date.today()), format="YYYY-MM-DD")
start_date, end_date = d

if symbol and start_date and end_date:
    data = fetch_financial_data(symbol)
    if data:
        keys_of_interest = ['Symbol', 'AssetType', 'Name', 'Sector', 'Industry', 'Country', 'Address']

        filtered_data = {key: data.get(key, 'N/A') for key in keys_of_interest}

        df = pd.DataFrame([filtered_data])
        st.dataframe(df, hide_index=True)

        address = data.get('Address', None)
        if address:
            latitude, longitude = get_latitude_longitude(address)
            if latitude is not None and longitude is not None:
                map_data = pd.DataFrame({'lat': [latitude], 'lon': [longitude]})
                st.map(map_data)
            else:
                st.warning("Unable to find location for the given address.")
        else:
            st.write("No address available.")

        st.success(f"Successfully fetched data for {symbol.upper()}")
    else:
        st.error(f"No data found for the given symbol: {symbol.upper()}")

    stock_data = fetch_stock_data(symbol, start_date, end_date)

    if stock_data is not None:
        if not stock_data.empty:
            show_line_chart = st.checkbox("Show Line Graph", value=True)

            if show_line_chart:
                line_color = st.color_picker("Choose Line Color", value="#1f77b4")
                line_chart = go.Figure()
                line_chart.add_trace(go.Scatter(x=stock_data.index, y=stock_data['4. close'], mode='lines', name='Closing Price', line=dict(color=line_color)))
                line_chart.update_layout(title=f'Stock Chart for {symbol.upper()}', xaxis_title='Date', yaxis_title='Stock Price')
                st.plotly_chart(line_chart)

            show_volume_chart = st.checkbox("Show Volume Graph", value=True)

            if show_volume_chart:
                volume_color = st.color_picker("Choose Volume Bar Color", value="#1f77b4")
                volume_chart = go.Figure()
                volume_chart.add_trace(go.Bar(x=stock_data.index, y=stock_data['5. volume'], name='Volume', marker=dict(color=volume_color)))
                volume_chart.update_layout(title=f'Volume Chart for {symbol.upper()}', xaxis_title='Date', yaxis_title='Volume')
                st.plotly_chart(volume_chart)

        else:
            st.warning("No historical stock data found for the given symbol.")
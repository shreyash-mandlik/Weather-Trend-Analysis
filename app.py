import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import warnings
warnings.filterwarnings('ignore')

# ================================
# Page config
# ================================
st.set_page_config(
    page_title="Weather Trend Analysis",
    page_icon="🌤️",
    layout="wide"
)

# ================================
# City coordinates
# ================================
cities = {
    "Mumbai": (19.0760, 72.8777),
    "Delhi": (28.6139, 77.2090),
    "Pune": (18.5204, 73.8567),
    "Bangalore": (12.9716, 77.5946),
    "Chennai": (13.0827, 80.2707),
    "Kolkata": (22.5726, 88.3639),
    "Hyderabad": (17.3850, 78.4867),
    "Ahmedabad": (23.0225, 72.5714)
}

# ================================
# Load historical weather data
# ================================
@st.cache_resource
def load_weather(city, start, end):
    lat, lon = cities[city]
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "windspeed_10m_max",
            "relative_humidity_2m_max"
        ],
        "timezone": "Asia/Kolkata"
    }
    response = requests.get(url, params=params)
    data = response.json()

    df = pd.DataFrame(data['daily'])
    df['time'] = pd.to_datetime(df['time'])
    df.rename(columns={
        'time': 'Date',
        'temperature_2m_max': 'Max_Temp',
        'temperature_2m_min': 'Min_Temp',
        'precipitation_sum': 'Rainfall',
        'windspeed_10m_max': 'Wind_Speed',
        'relative_humidity_2m_max': 'Humidity'
    }, inplace=True)

    df['Avg_Temp'] = (df['Max_Temp'] + df['Min_Temp']) / 2
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Month_Name'] = df['Date'].dt.strftime('%b')
    df['Season'] = df['Month'].map({
        12: 'Winter', 1: 'Winter', 2: 'Winter',
        3: 'Summer', 4: 'Summer', 5: 'Summer',
        6: 'Monsoon', 7: 'Monsoon', 8: 'Monsoon',
        9: 'Monsoon', 10: 'Autumn', 11: 'Autumn'
    })
    return df

# ================================
# Live weather
# ================================
def get_live_weather(city):
    lat, lon = cities[city]
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "windspeed_10m",
            "precipitation",
            "weathercode"
        ],
        "timezone": "Asia/Kolkata"
    }
    response = requests.get(url, params=params)
    return response.json()['current']

# ================================
# 7 day forecast
# ================================
def get_forecast(city):
    lat, lon = cities[city]
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "windspeed_10m_max"
        ],
        "timezone": "Asia/Kolkata",
        "forecast_days": 7
    }
    response = requests.get(url, params=params)
    data = response.json()['daily']
    df = pd.DataFrame(data)
    df['time'] = pd.to_datetime(df['time'])
    return df

# Weather code to emoji
def weather_emoji(code):
    if code == 0: return "☀️ Clear Sky"
    elif code <= 3: return "⛅ Partly Cloudy"
    elif code <= 49: return "🌫️ Foggy"
    elif code <= 67: return "🌧️ Rainy"
    elif code <= 77: return "❄️ Snowy"
    elif code <= 82: return "🌦️ Showers"
    else: return "⛈️ Thunderstorm"

# ================================
# App UI
# ================================
st.title("🌤️ Weather Trend Analysis")
st.write("Live weather + historical trends + 7 day forecast for Indian cities!")

# Sidebar
st.sidebar.header("Settings")
city = st.sidebar.selectbox("Select City", list(cities.keys()))
start_date = st.sidebar.date_input("History Start Date",
    value=pd.to_datetime("2019-01-01"))
end_date = st.sidebar.date_input("History End Date",
    value=pd.to_datetime("2023-12-31"))

# ================================
# LIVE WEATHER — always shown!
# ================================
st.subheader(f"🔴 Live Weather — {city}")
try:
    live = get_live_weather(city)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("🌡️ Temperature",
                  f"{live['temperature_2m']}°C")
    with col2:
        st.metric("💧 Humidity",
                  f"{live['relative_humidity_2m']}%")
    with col3:
        st.metric("💨 Wind Speed",
                  f"{live['windspeed_10m']} km/h")
    with col4:
        st.metric("🌧️ Precipitation",
                  f"{live['precipitation']} mm")
    with col5:
        st.metric("🌤️ Condition",
                  weather_emoji(live['weathercode']))
except:
    st.warning("Live weather unavailable!")

st.divider()

# ================================
# 7 DAY FORECAST
# ================================
st.subheader(f"📅 7 Day Forecast — {city}")
try:
    forecast = get_forecast(city)
    cols = st.columns(7)
    for i, col in enumerate(cols):
        with col:
            day = forecast.iloc[i]
            st.markdown(f"**{day['time'].strftime('%a %d')}**")
            st.markdown(f"🌡️ {day['temperature_2m_max']:.0f}°C")
            st.markdown(f"❄️ {day['temperature_2m_min']:.0f}°C")
            st.markdown(f"🌧️ {day['precipitation_sum']:.1f}mm")
            st.markdown(f"💨 {day['windspeed_10m_max']:.0f}km/h")

    # Forecast chart
    fig, ax = plt.subplots(figsize=(12, 4))
    days = [d.strftime('%a %d') for d in forecast['time']]
    ax.plot(days, forecast['temperature_2m_max'],
            marker='o', color='#E24B4A',
            linewidth=2, label='Max Temp')
    ax.plot(days, forecast['temperature_2m_min'],
            marker='o', color='#378ADD',
            linewidth=2, label='Min Temp')
    ax.fill_between(days, forecast['temperature_2m_min'],
                    forecast['temperature_2m_max'],
                    alpha=0.2, color='#EF9F27')
    ax.set_title(f'{city} — 7 Day Temperature Forecast')
    ax.set_ylabel('Temperature (°C)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
except:
    st.warning("Forecast unavailable!")

st.divider()

# ================================
# HISTORICAL ANALYSIS
# ================================
if st.button("📊 Analyze Historical Trends", type="primary"):
    with st.spinner(f'Loading historical data for {city}...'):
        df = load_weather(city, str(start_date), str(end_date))

    st.success(f"Historical data loaded! ✅")

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Avg Temperature", f"{df['Avg_Temp'].mean():.1f}°C")
    with col2:
        st.metric("Highest Temp", f"{df['Max_Temp'].max():.1f}°C")
    with col3:
        st.metric("Lowest Temp", f"{df['Min_Temp'].min():.1f}°C")
    with col4:
        st.metric("Total Rainfall", f"{df['Rainfall'].sum():.0f}mm")
    with col5:
        st.metric("Avg Humidity", f"{df['Humidity'].mean():.1f}%")

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs([
        "🌡️ Temperature", "🌧️ Rainfall",
        "📊 Seasonal", "🔥 Correlations"])

    months = ['Jan','Feb','Mar','Apr','May','Jun',
              'Jul','Aug','Sep','Oct','Nov','Dec']

    with tab1:
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        axes[0].plot(df['Date'], df['Max_Temp'],
                     color='#E24B4A', alpha=0.5,
                     linewidth=0.5, label='Max')
        axes[0].plot(df['Date'], df['Min_Temp'],
                     color='#378ADD', alpha=0.5,
                     linewidth=0.5, label='Min')
        axes[0].plot(df['Date'], df['Avg_Temp'],
                     color='#1D9E75', linewidth=1, label='Average')
        axes[0].set_title(f'{city} Temperature Trend')
        axes[0].set_xlabel('Date')
        axes[0].set_ylabel('Temperature (°C)')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)

        monthly_temp = df.groupby('Month')['Avg_Temp'].mean()
        axes[1].bar(months, monthly_temp,
                    color=['#378ADD','#378ADD','#EF9F27',
                           '#EF9F27','#E24B4A','#1D9E75',
                           '#1D9E75','#1D9E75','#1D9E75',
                           '#7F77DD','#7F77DD','#378ADD'])
        axes[1].set_title('Average Temperature by Month')
        axes[1].set_ylabel('Temperature (°C)')
        plt.tight_layout()
        st.pyplot(fig)

    with tab2:
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        monthly_rain = df.groupby('Month')['Rainfall'].mean()
        axes[0].bar(months, monthly_rain,
                    color='#378ADD', alpha=0.8)
        axes[0].set_title('Average Rainfall by Month')
        axes[0].set_ylabel('Rainfall (mm)')

        yearly_rain = df.groupby('Year')['Rainfall'].sum()
        axes[1].bar(yearly_rain.index, yearly_rain,
                    color='#378ADD', alpha=0.8, width=0.5)
        axes[1].set_title('Yearly Total Rainfall')
        axes[1].set_ylabel('Rainfall (mm)')
        plt.tight_layout()
        st.pyplot(fig)

    with tab3:
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        seasons = ['Winter', 'Summer', 'Monsoon', 'Autumn']
        colors = ['#378ADD', '#E24B4A', '#1D9E75', '#EF9F27']

        season_temp = df.groupby('Season')['Avg_Temp'].mean()
        axes[0].bar(seasons,
                    [season_temp.get(s, 0) for s in seasons],
                    color=colors)
        axes[0].set_title('Average Temperature by Season')
        axes[0].set_ylabel('Temperature (°C)')

        season_rain = df.groupby('Season')['Rainfall'].sum()
        axes[1].bar(seasons,
                    [season_rain.get(s, 0) for s in seasons],
                    color=colors)
        axes[1].set_title('Total Rainfall by Season')
        axes[1].set_ylabel('Rainfall (mm)')
        plt.tight_layout()
        st.pyplot(fig)

    with tab4:
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        corr = df[['Max_Temp', 'Min_Temp', 'Avg_Temp',
                   'Rainfall', 'Wind_Speed', 'Humidity']].corr()
        sns.heatmap(corr, annot=True, fmt='.2f',
                    cmap='RdYlGn', ax=axes[0],
                    center=0, square=True)
        axes[0].set_title('Weather Features Correlation')

        axes[1].scatter(df['Avg_Temp'], df['Humidity'],
                        alpha=0.3, color='#378ADD', s=10)
        axes[1].set_xlabel('Average Temperature (°C)')
        axes[1].set_ylabel('Humidity (%)')
        axes[1].set_title('Temperature vs Humidity')
        axes[1].grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)

    st.divider()
    st.subheader("📈 Yearly Weather Summary")
    yearly = df.groupby('Year').agg({
        'Avg_Temp': 'mean',
        'Rainfall': 'sum',
        'Humidity': 'mean',
        'Wind_Speed': 'mean'
    }).round(2)
    yearly.columns = ['Avg Temp (°C)', 'Total Rainfall (mm)',
                       'Avg Humidity (%)', 'Avg Wind Speed (km/h)']
    st.dataframe(yearly, use_container_width=True)


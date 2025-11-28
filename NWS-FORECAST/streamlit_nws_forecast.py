import streamlit as st
import requests
import json
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# CRITICAL: The NWS API requires a User-Agent header for all requests.
USER_AGENT = "NextWeatherStreamlitApp/1.0 (contact@example.com)"
BASE_URL = "https://api.weather.gov"

st.set_page_config(page_title="NWS Forecast Dashboard", layout="wide")

st.title("NWS Forecast Dashboard")

@st.cache_data(ttl=3600)
def get_grid_coordinates(latitude, longitude):
    """Gets NWS grid coordinates for a given lat/lon."""
    point_url = f"{BASE_URL}/points/{latitude},{longitude}"
    headers = {"User-Agent": USER_AGENT}
    st.info(f"Fetching grid coordinates for {latitude},{longitude}...")
    try:
        response = requests.get(point_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        properties = data.get("properties", {})
        grid_id, grid_x, grid_y = properties.get("gridId"), properties.get("gridX"), properties.get("gridY")
        if not all([grid_id, grid_x, grid_y]):
            st.error("Could not extract grid coordinates from API response.")
            return None, None, None
        st.success(f"Grid found: ID={grid_id}, X={grid_x}, Y={grid_y}")
        return grid_id, grid_x, grid_y
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching grid coordinates: {e}")
        return None, None, None

@st.cache_data(ttl=600)
def get_all_forecasts_for_grid(grid_id, grid_x, grid_y):
    """Fetches daily, hourly, and raw forecasts for a given grid."""
    if not all([grid_id, grid_x, grid_y]):
        return None
    grid_url_base = f"{BASE_URL}/gridpoints/{grid_id}/{grid_x},{grid_y}"
    headers = {"User-Agent": USER_AGENT}
    forecast_data = {}
    urls_to_fetch = {
        "daily": f"{grid_url_base}/forecast",
        "hourly": f"{grid_url_base}/forecast/hourly",
        "raw": grid_url_base
    }
    for forecast_type, url in urls_to_fetch.items():
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            forecast_data[forecast_type] = response.json()
        except requests.exceptions.RequestException as e:
            st.warning(f"Could not fetch {forecast_type} forecast: {e}")
    return forecast_data

def create_24hr_forecast_plot(hourly_periods):
    """Creates a multi-axis Plotly chart for the next 24 hours."""
    if not hourly_periods:
        return None
    df = pd.DataFrame(hourly_periods[:24])
    df['temperature'] = pd.to_numeric(df['temperature'])
    df['windSpeed_val'] = pd.to_numeric(df['windSpeed'].str.extract('(\d+)', expand=False), errors='coerce').fillna(0)
    df['precip_val'] = df['probabilityOfPrecipitation'].apply(lambda x: x.get('value', 0) if isinstance(x, dict) else 0)
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=df['startTime'], y=df['temperature'], name="Temperature (°F)", line=dict(color='red')), secondary_y=False)
    fig.add_trace(go.Bar(x=df['startTime'], y=df['precip_val'], name="Precipitation (%)", marker_color='blue', opacity=0.6), secondary_y=True)
    fig.add_trace(go.Scatter(x=df['startTime'], y=df['windSpeed_val'], name="Wind (mph)", line=dict(color='green', dash='dot')), secondary_y=False)
    
    fig.update_layout(title_text="Next 24-Hour Forecast Analysis", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.update_yaxes(title_text="Temperature (°F) / Wind (mph)", secondary_y=False)
    fig.update_yaxes(title_text="Precipitation (%)", secondary_y=True, range=[0, 100])
    return fig

from nws_api_service import get_lat_lon, get_grid_coordinates, get_all_forecasts_for_grid, create_24hr_forecast_plot



# --- UI ---

st.sidebar.header("Location Input")



input_method = st.sidebar.radio("Input Method:", ["Location Name", "Coordinates"])



lat, lon = None, None



if input_method == "Location Name":

    location_name = st.sidebar.text_input("Enter a location name:", "Kansas City, MO")

    # This block now only sets the stage for the button click

else: # Coordinates

    lat_in = st.sidebar.text_input("Latitude", "39.0997")

    lon_in = st.sidebar.text_input("Longitude", "-94.5786")





if st.sidebar.button("Get Forecast"):

    if input_method == "Location Name":

        if location_name:

            with st.spinner(f"Geocoding '{location_name}'..."):

                lat, lon, error_msg = get_lat_lon(location_name)

            if error_msg:

                st.sidebar.error(error_msg)

                lat, lon = None, None # Reset on error

        else:

            st.sidebar.warning("Please enter a location name.")

    else: # Coordinates

        try:

            lat, lon = float(lat_in), float(lon_in)

        except (ValueError, TypeError):

            st.sidebar.error("Please enter valid numerical values for Latitude and Longitude.")

            lat, lon = None, None



    if lat is not None and lon is not None:

        with st.spinner("Fetching NWS grid data..."):

            grid_id, grid_x, grid_y, error = get_grid_coordinates(lat, lon)

        

        if error:

            st.error(f"Failed to get NWS grid coordinates: {error}")

        elif grid_id:

            with st.spinner("Fetching all forecast data..."):

                all_forecasts = get_all_forecasts_for_grid(grid_id, grid_x, grid_y)

            

            if all_forecasts:

                st.header(f"Forecast Dashboard for {lat:.4f}, {lon:.4f}")

                

                # --- Current Temp ---

                current_temp_f = None

                if all_forecasts.get("hourly"):

                    current_temp_f = all_forecasts["hourly"]["properties"]["periods"][0]['temperature']

                if current_temp_f:

                    st.metric(label="Current Temperature", value=f"{current_temp_f}°F")

                

                st.markdown("---")



                # --- Plotly Graph ---

                if all_forecasts.get("hourly"):

                    fig = create_24hr_forecast_plot(all_forecasts["hourly"]["properties"]["periods"])

                    if fig:

                        st.plotly_chart(fig, use_container_width=True)

                

                st.markdown("---")

                

                # --- 7-Day Metrics ---

                st.subheader("7-Day Analytics & Key Metrics")

                high_temp, low_temp, max_wind, max_precip = None, None, None, None

                if all_forecasts.get("daily"):

                    temps = [p['temperature'] for p in all_forecasts["daily"]["properties"]["periods"]]

                    high_temp, low_temp = max(temps), min(temps)

                if all_forecasts.get("hourly"):

                    wind_speeds = [int(p['windSpeed'].split(' ')[0]) for p in all_forecasts["hourly"]["properties"]["periods"] if 'mph' in p['windSpeed']]

                    max_wind = max(wind_speeds) if wind_speeds else None

                    precip_chances = [p.get('probabilityOfPrecipitation', {}).get('value', 0) for p in all_forecasts["hourly"]["properties"]["periods"] if p.get('probabilityOfPrecipitation')]

                    max_precip = max(precip_chances) if precip_chances else 0



                col1, col2, col3 = st.columns(3)

                if high_temp is not None:

                    col1.metric("7-Day Temp Range", f"{low_temp}° - {high_temp}°F")

                if max_wind is not None:

                    col2.metric("Peak Wind (7-Day)", f"{max_wind} mph")

                if max_precip is not None:

                    col3.metric("Peak Precip. Chance", f"{max_precip}%")



                st.markdown("---")



                # --- Data Tables ---

                st.subheader("Data Tables")

                if all_forecasts.get("daily"):

                    st.write("7-Day Forecast Table")

                    st.dataframe(pd.DataFrame(all_forecasts["daily"]["properties"]["periods"]), use_container_width=True)

                if all_forecasts.get("hourly"):

                    st.write("Next 24-Hour Forecast Table")

                    st.dataframe(pd.DataFrame(all_forecasts["hourly"]["properties"]["periods"][:24]), use_container_width=True)

    else:

        st.sidebar.warning("Please provide a valid location to get a forecast.")

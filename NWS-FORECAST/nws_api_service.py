
import requests
import json
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from urllib.error import HTTPError

# CRITICAL: The NWS API requires a User-Agent header for all requests.
NWS_USER_AGENT = "NextWeatherStreamlitApp/1.0 (contact@example.com)"
BASE_URL = "https://api.weather.gov"

# ==============================================================================
# IMPORTANT: USAGE POLICY FOR NOMINATIM (GEOCODING SERVICE)
# ==============================================================================
# PLEASE CHANGE THIS to a unique identifier, like your app's name and your
# email address. For example: "MyWeatherApp/1.0 (your-email@example.com)"
# Failure to do so may result in a 403 Forbidden error.
# ==============================================================================
NOMINATIM_USER_AGENT = "NextWeatherGeocoder/1.0 (Neeraj.Pokala@minfytech.com)"


def get_lat_lon(location_name: str):
    """
    Converts a location name to its latitude and longitude using Nominatim.
    
    Args:
        location_name (str): The name of the location (e.g., "New York", "Minneapolis").
        
    Returns:
        tuple: A tuple containing (latitude, longitude) as floats if found, 
               otherwise (None, None).
        str: An error message if something went wrong, otherwise None.
    """
    geolocator = Nominatim(user_agent=NOMINATIM_USER_AGENT)
    
    try:
        location = geolocator.geocode(location_name, timeout=10) # Increased timeout
        if location:
            return location.latitude, location.longitude, None
        else:
            return None, None, f"Could not find coordinates for '{location_name}'. Please try a more specific name."
    except HTTPError as e:
        if e.code == 403:
            return None, None, f"Geocoding service error: HTTP {e.code} Forbidden. Ensure NOMINATIM_USER_AGENT is unique and descriptive (e.g., 'MyCoolApp/1.0 your-email@domain.com')."
        else:
            return None, None, f"Geocoding service returned an HTTP error: {e}"
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        return None, None, f"Geocoding service error: {e}. Check internet connection."
    except Exception as e:
        return None, None, f"An unexpected error occurred during geocoding: {e}"


def get_grid_coordinates(latitude, longitude):
    """Gets NWS grid coordinates for a given lat/lon."""
    point_url = f"{BASE_URL}/points/{latitude},{longitude}"
    headers = {"User-Agent": NWS_USER_AGENT}
    try:
        response = requests.get(point_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        properties = data.get("properties", {})
        grid_id, grid_x, grid_y = properties.get("gridId"), properties.get("gridX"), properties.get("gridY")
        if not all([grid_id, grid_x, grid_y]):
            return None, None, None, json.dumps(data, indent=2) # Return raw data for debugging
        return grid_id, grid_x, grid_y, None
    except requests.exceptions.RequestException as e:
        return None, None, None, str(e) # Return error string
    except json.JSONDecodeError:
        return None, None, None, "JSONDecodeError"

def get_all_forecasts_for_grid(grid_id, grid_x, grid_y):
    """Fetches daily, hourly, and raw forecasts for a given grid."""
    if not all([grid_id, grid_x, grid_y]):
        return None
    grid_url_base = f"{BASE_URL}/gridpoints/{grid_id}/{grid_x},{grid_y}"
    headers = {"User-Agent": NWS_USER_AGENT}
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
            print(f"Warning: Could not fetch {forecast_type} forecast: {e}")
        except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON for {forecast_type} forecast.")
    return forecast_data

def get_active_alerts_for_point(latitude, longitude):
    """Fetches active alerts for a specific lat/lon point."""
    alerts_url = f"{BASE_URL}/alerts/active?point={latitude},{longitude}"
    headers = {"User-Agent": NWS_USER_AGENT}
    try:
        response = requests.get(alerts_url, headers=headers)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, f"Error fetching alerts: {e}"
    except json.JSONDecodeError:
        return None, "Failed to decode JSON response from the alerts endpoint."

def search_all_alerts(status=None, area=None, severity=None, event=None, limit=50):
    """
    Searches for alerts using various filter criteria.
    
    Args:
        status (str, optional): Alert status (e.g., 'actual').
        area (str, optional): State/area abbreviation (e.g., 'TX', 'CA').
        severity (str, optional): Severity level (e.g., 'Extreme', 'Severe').
        event (str, optional): Event type (e.g., 'Tornado Warning').
        limit (int, optional): Maximum number of alerts to return. Defaults to 50.
        
    Returns:
        dict: The JSON response from the API.
        str: An error message if something went wrong, otherwise None.
    """
    params = {
        "status": status,
        "area": area,
        "severity": severity,
        "event": event,
        "limit": limit
    }
    # Filter out None values so they aren't included in the query
    active_params = {key: value for key, value in params.items() if value}
    
    alerts_url = f"{BASE_URL}/alerts"
    headers = {"User-Agent": NWS_USER_AGENT}
    
    try:
        response = requests.get(alerts_url, headers=headers, params=active_params)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, f"Error searching alerts: {e}"
    except json.JSONDecodeError:
        return None, "Failed to decode JSON response from the alerts endpoint."

def create_24hr_forecast_plot(hourly_periods):
    """Creates a multi-axis Plotly chart for the next 24 hours."""
    if not hourly_periods:
        return None
    df = pd.DataFrame(hourly_periods[:24])
    df['temperature'] = pd.to_numeric(df['temperature'])
    df['windSpeed_val'] = pd.to_numeric(df['windSpeed'].str.extract('(\\d+)', expand=False), errors='coerce').fillna(0)
    df['precip_val'] = df['probabilityOfPrecipitation'].apply(lambda x: x.get('value', 0) if isinstance(x, dict) else 0)
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=df['startTime'], y=df['temperature'], name="Temperature (°F)", line=dict(color='red')), secondary_y=False)
    fig.add_trace(go.Bar(x=df['startTime'], y=df['precip_val'], name="Precipitation (%)", marker_color='blue', opacity=0.6), secondary_y=True)
    fig.add_trace(go.Scatter(x=df['startTime'], y=df['windSpeed_val'], name="Wind (mph)", line=dict(color='green', dash='dot')), secondary_y=False)
    
    fig.update_layout(title_text="Next 24-Hour Forecast Analysis", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.update_yaxes(title_text="Temperature (°F) / Wind (mph)", secondary_y=False)
    fig.update_yaxes(title_text="Precipitation (%)", secondary_y=True, range=[0, 100])
    return fig

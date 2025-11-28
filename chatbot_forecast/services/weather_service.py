import requests
import pandas as pd
import isodate
from datetime import datetime, timezone
import json

class WeatherService:
    def __init__(self, user_agent):
        self.headers = {"User-Agent": user_agent}
        self.cache = {}

    def get_weather_data(self, lat, lon):
        """Fetches weather data from NWS API with basic caching."""
        cache_key = f"{lat},{lon}"
        # In a real app, check timestamp for TTL. For now, simple session cache.
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            points_url = f"https://api.weather.gov/points/{lat},{lon}"
            points_resp = requests.get(points_url, headers=self.headers)
            points_resp.raise_for_status()
            props = points_resp.json()['properties']
            
            data = {
                "forecast": requests.get(props['forecast'], headers=self.headers).json(),
                "hourly": requests.get(props['forecastHourly'], headers=self.headers).json(),
                "grid": requests.get(props['forecastGridData'], headers=self.headers).json()
            }
            self.cache[cache_key] = data
            return data
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return {"error": str(e)}

    def get_current_conditions(self, grid_data):
        """Extracts current conditions from grid data."""
        if 'properties' not in grid_data:
            return "No grid data available."
            
        props = grid_data['properties']
        now = datetime.now(timezone.utc)
        
        conditions = []
        
        # Helper to get value for current time
        def get_val(param_name, label, unit_override=None):
            if param_name not in props: return
            values = props[param_name]['values']
            uom = props[param_name].get('uom', '')
            
            for item in values:
                time_str, duration_str = item['validTime'].split('/')
                start_time = datetime.fromisoformat(time_str)
                duration = isodate.parse_duration(duration_str)
                end_time = start_time + duration
                
                if start_time <= now < end_time:
                    val = item['value']
                    if val is None: return
                    
                    # Formatting
                    if unit_override:
                        unit = unit_override
                    elif 'degC' in uom:
                        val = (val * 9/5) + 32
                        unit = "°F"
                    elif 'percent' in uom:
                        unit = "%"
                    elif 'km_h' in uom:
                        val = val * 0.621371
                        unit = "mph"
                    else:
                        unit = uom
                        
                    conditions.append(f"- {label}: {round(val, 1)} {unit}")
                    return

        get_val('temperature', 'Temperature')
        get_val('relativeHumidity', 'Humidity')
        get_val('windSpeed', 'Wind Speed')
        get_val('windGust', 'Wind Gust')
        get_val('apparentTemperature', 'Feels Like')
        get_val('probabilityOfPrecipitation', 'Precipitation Chance')
        get_val('skyCover', 'Sky Cover')
        
        return "CURRENT CONDITIONS:\n" + "\n".join(conditions) if conditions else "Current conditions unavailable."

    def get_forecast_summary(self, forecast_data):
        """Summarizes the next few periods of the forecast."""
        if 'properties' not in forecast_data:
            return "No forecast data available."
            
        periods = forecast_data['properties']['periods'][:3] # Next 3 periods
        summary = ["FORECAST SUMMARY:"]
        for p in periods:
            summary.append(f"- {p['name']}: {p['detailedForecast']}")
            
        return "\n".join(summary)

    def get_hazards(self, grid_data):
        """Checks for active hazards."""
        if 'properties' not in grid_data:
            return "No hazard data available."
            
        hazards_vals = grid_data['properties'].get('hazards', {}).get('values', [])
        if not hazards_vals:
            return "ACTIVE HAZARDS: None"
            
        active_hazards = []
        for item in hazards_vals:
            vals_list = item['value']
            for val in vals_list:
                label = f"{val.get('phenomenon', 'Unknown')} ({val.get('significance', '')})"
                active_hazards.append(f"- {label}")
        
        return "ACTIVE HAZARDS:\n" + "\n".join(active_hazards) if active_hazards else "ACTIVE HAZARDS: None"

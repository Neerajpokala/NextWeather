# Weather API Endpoints

This document provides a detailed overview of the API endpoints available in the `standard_apis.py` file for accessing weather data from The Weather Company.

## CoreAPI

The `CoreAPI` class provides access to the core weather data APIs.

### get_alerts

**Description:** Get alerts from The Weather Company API.

**Input Parameters:**
- **countryCode** (string): Weather API country code.
- **adminDistrictCode** (string): Admin district code. *NOTE: Attach the country code to the end of this string with a colon (e.g., 'GA:US' [Georgia, USA])*
- **areaId** (string): Area ID code.
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: One and only one of 'countryCode', 'adminDistrictCode', 'areaId', or 'geocode' must be specified.*

**Output:**
- A JSON object containing alert headlines for the specified location.

### get_daily_forecast

**Description:** Get a daily forecast from The Weather Company API.

**Input Parameters:**
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **iataCode** (string): IATA airport code.
- **icaoCode** (string): ICAO airport code.
- **placeid** (string): Place ID.
- **postalKey** (string): Postal zip code.
- **forecast_days** (integer, optional, default=3): Number of days to include in the daily forecast. Valid options are 3, 5, 7, 10, 15.
- **units** (string, optional, default='e'): Units of the retrieved data ('e' for English, 'm' for Metric, 'h' for hybrid).
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: One and only one of 'geocode', 'iataCode', 'icaoCode', 'placeid', or 'postalKey' must be specified.*

**Output:**
- A JSON object containing the daily weather forecast.

### get_hourly_forecast

**Description:** Get an hourly forecast from The Weather Company API.

**Input Parameters:**
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **iataCode** (string): IATA airport code.
- **icaoCode** (string): ICAO airport code.
- **placeid** (string): Place ID.
- **postalKey** (string): Postal zip code.
- **forecast_days** (integer, optional, default=2): Number of days to include in the hourly forecast. Valid options are 2, 15.
- **units** (string, optional, default='e'): Units of the retrieved data ('e' for English, 'm' for Metric, 'h' for hybrid).
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: One and only one of 'geocode', 'iataCode', 'icaoCode', 'placeid', or 'postalKey' must be specified.*

**Output:**
- A JSON object containing the hourly weather forecast.

### get_intraday_forecast

**Description:** Get an intraday forecast from The Weather Company API.

**Input Parameters:**
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **location** (string): TWC proprietary location type (4) with the format: `location/<postal code>:<location type>:<country code>`.
- **forecast_days** (integer, optional, default=3): Number of days for the forecast. Valid options are 3, 5, 7, 10.
- **units** (string, optional, default='e'): Units of the retrieved data ('e' for English, 'm' for Metric, 'h' for hybrid).
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: One and only one of 'geocode' or 'location' must be specified.*

**Output:**
- A JSON object containing the intraday weather forecast.

### get_watch_and_warning_vector_products

**Description:** Returns watch and warning vector products.

**Input Parameters:**
- **productKey** (integer, optional, default=609): The product key.
- **time** (integer): Timestamp.
- **lod** (integer): Level of detail.
- **x** (integer): X index of the tile.
- **y** (integer): Y index of the tile.
- **tile_size** (integer, optional, default=256): Size of the tiles.
- **meta** (boolean, optional, default=True): Return metadata.
- **max_times** (integer, optional, default=12): Maximum number of timesteps to return.

*Note: All four or none of 'time', 'lod', 'x', 'y' must be passed.*

**Output:**
- A JSON object containing vector products or metadata.

### get_current_conditions

**Description:** Get current conditions for a location from The Weather Company API.

**Input Parameters:**
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **location** (string): TWC proprietary location type (4) with the format: `location/<postal code>:<location type>:<country code>`.
- **hours** (integer, optional): Hourly interval for the current conditions.
- **units** (string, optional, default='e'): Units of the retrieved data ('e' for English, 'm' for Metric, 'h' for hybrid).
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: One and only one of 'geocode' or 'location' must be specified.*

**Output:**
- A JSON object containing the current weather conditions.

---

## EnhancedCurrentConditionsAPI

The `EnhancedCurrentConditionsAPI` class provides access to enhanced current conditions data.

### get_current_conditions

**Description:** Get current conditions for a location from The Weather Company API.

**Input Parameters:**
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **iataCode** (string): IATA airport code.
- **icaoCode** (string): ICAO airport code.
- **placeid** (string): Place ID.
- **postalKey** (string): Postal zip code.
- **stationId** (string): Personal weather station ID.
- **units** (string, optional, default='e'): Units of the retrieved data ('e' for English, 'm' for Metric, 'h' for hybrid).
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: One and only one of 'geocode', 'iataCode', 'icaoCode', 'placeid', 'postalKey', or 'stationId' must be specified.*

**Output:**
- A JSON object containing the current weather conditions.

### get_pws_daily_summary

**Description:** Get a 7-day daily summary from a personal weather station.

**Input Parameters:**
- **stationId** (string): Personal weather station ID.
- **units** (string, optional, default='e'): Units of the retrieved data ('e' for English, 'm' for Metric, 'h' for hybrid).

**Output:**
- A JSON object containing the 7-day daily summary.

### get_pws_1day_history

**Description:** Get 1 day of observations from a personal weather station.

**Input Parameters:**
- **stationId** (string): Personal weather station ID.
- **units** (string, optional, default='e'): Units of the retrieved data ('e' for English, 'm' for Metric, 'h' for hybrid).

**Output:**
- A JSON object containing 1 day of observations.

### get_pws_7day_history

**Description:** Get 7 days of hourly observations from a personal weather station.

**Input Parameters:**
- **stationId** (string): Personal weather station ID.
- **units** (string, optional, default='e'): Units of the retrieved data ('e' for English, 'm' for Metric, 'h' for hybrid).

**Output:**
- A JSON object containing 7 days of hourly observations.

---

## EnhancedForecastsAPI

The `EnhancedForecastsAPI` class provides access to enhanced forecast data.

### get_hourly_enterprise_forecast

**Description:** Get hourly enterprise forecasts for a location from The Weather Company API.

**Input Parameters:**
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **iataCode** (string): IATA airport code.
- **icaoCode** (string): ICAO airport code.
- **placeid** (string): Place ID.
- **postalKey** (string): Postal zip code.
- **forecast_period** (string, optional, default='1day'): Forecast period. Options are '6hour', '12hour', '1day', '2day', '3day', '10day', '15day'.
- **units** (string, optional, default='e'): Units of the retrieved data ('e' for English, 'm' for Metric, 'h' for hybrid).
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: One and only one of 'geocode', 'iataCode', 'icaoCode', 'placeid', or 'postalKey' must be specified.*

**Output:**
- A JSON object containing the hourly enterprise forecast.

### get_15min_forecast

**Description:** Get a 7-hour forecast at 15-minute intervals from The Weather Company API.

**Input Parameters:**
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **iataCode** (string): IATA airport code.
- **icaoCode** (string): ICAO airport code.
- **placeid** (string): Place ID.
- **postalKey** (string): Postal zip code.
- **units** (string, optional, default='e'): Units of the retrieved data ('e' for English, 'm' for Metric, 'h' for hybrid).
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: One and only one of 'geocode', 'iataCode', 'icaoCode', 'placeid', or 'postalKey' must be specified.*

**Output:**
- A JSON object containing the 15-minute forecast.

### get_nowcast

**Description:** Get a nowcast for a location from The Weather Company API.

**Input Parameters:**
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **postalKey** (string): Postal zip code.
- **units** (string, optional, default='e'): Units of the retrieved data ('e' for English, 'm' for Metric, 'h' for hybrid).
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: One and only one of 'geocode' or 'postalKey' must be specified.*

**Output:**
- A JSON object containing the nowcast.

### get_precipitation_forecast

**Description:** Get a 7-hour precipitation forecast for a location from The Weather Company API.

**Input Parameters:**
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **postalKey** (string): The Postal Code with TWC proprietary location type (4) format: `location/<postal code>:<location type>:<country code>`.
- **units** (string, optional, default='e'): Units of the retrieved data ('e' for English, 'm' for Metric, 'h' for hybrid).
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: One and only one of 'geocode' or 'postalKey' must be specified.*

**Output:**
- A JSON object containing the precipitation forecast.

### when_will_it_rain

**Description:** Get a 6-hour rain forecast for a location from The Weather Company API.

**Input Parameters:**
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **postalKey** (string): The Postal Code with TWC proprietary location type (4) format: `location/<postal code>:<location type>:<country code>`.
- **units** (string, optional, default='e'): Units of the retrieved data ('e' for English, 'm' for Metric, 'h' for hybrid).
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: One and only one of 'geocode' or 'postalKey' must be specified.*

**Output:**
- A JSON object containing the rain forecast.

### get_analytical_forecast_data

**Description:** Get analytical forecast data from The Weather Company API.

**Input Parameters:**
- **productId** (string): Product ID.
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **postalKey** (string): The Postal Code with TWC proprietary location type (4) format: `location/<postal code>:<location type>:<country code>`.
- **units** (string, optional, default='e'): Units of the retrieved data ('e' for English, 'm' for Metric, 'h' for hybrid).
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: One and only one of 'geocode' or 'postalKey' must be specified.*

**Output:**
- A pandas DataFrame containing the analytical forecast data in CSV format.

---

## LifestyleIndicesAPI

The `LifestyleIndicesAPI` class provides access to various lifestyle-related indices.

### get_air_quality

**Description:** Get air quality data for a location from The Weather Company API.

**Input Parameters:**
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **iataCode** (string): IATA airport code.
- **icaoCode** (string): ICAO airport code.
- **placeid** (string): Place ID.
- **postalKey** (string): Postal zip code.
- **scale** (string, optional, default='EPA'): Air Quality Scale. Valid options: 'EPA', 'HJ6332012', 'ATMO', 'UBA', 'DAQI', 'NAQI', 'IMECA', 'CAQI'.
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: One and only one of 'geocode', 'iataCode', 'icaoCode', 'placeid', or 'postalKey' must be specified.*

**Output:**
- A JSON object containing air quality data.

### get_historical_flu

**Description:** Get historical flu data for a location from The Weather Company API.

**Input Parameters:**
- **yearMonth** (integer): Year and month in YYYYMM format.
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **iataCode** (string): IATA airport code.
- **icaoCode** (string): ICAO airport code.
- **placeid** (string): Place ID.
- **postalKey** (string): Postal zip code.
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: One and only one of 'geocode', 'iataCode', 'icaoCode', 'placeid', or 'postalKey' must be specified.*

**Output:**
- A JSON object containing historical flu data.

### get_historical_pollen

**Description:** Get historical pollen data for a location from The Weather Company API.

**Input Parameters:**
- **yearMonth** (integer): Year and month in YYYYMM format.
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **iataCode** (string): IATA airport code.
- **icaoCode** (string): ICAO airport code.
- **placeid** (string): Place ID.
- **postalKey** (string): Postal zip code.
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: One and only one of 'geocode', 'iataCode', 'icaoCode', 'placeid', or 'postalKey' must be specified.*

**Output:**
- A JSON object containing historical pollen data.

### get_pollen_observations

**Description:** Get pollen observations for a location.

**Input Parameters:**
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **postalKey** (string): Postal zip code.
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: One and only one of 'geocode' or 'postalKey' must be specified.*

**Output:**
- A JSON object containing pollen observations.

### get_tide_predictions

**Description:** Get 12 months of historical tides and 12 months of tidal predictions from The Weather Company API.

**Input Parameters:**
- **startYear** (integer): Start year for daily data.
- **startMonth** (integer): Start month for daily data.
- **startDay** (integer): Start day for daily data.
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **iataCode** (string): IATA airport code.
- **icaoCode** (string): ICAO airport code.
- **placeid** (string): Place ID.
- **postalKey** (string): Postal zip code.
- **tide** (string, optional, default='8670870'): Unique tidal station ID.
- **forecast_days** (integer, optional): Number of days for the forecast. Valid options for daily data: 3, 5, 10, 15. Leave as None for monthly data.
- **units** (string, optional, default='e'): Units of the retrieved data ('e' for English, 'm' for Metric, 'h' for hybrid).

*Note: One and only one of 'geocode', 'iataCode', 'icaoCode', 'placeid', or 'postalKey' must be specified.*

**Output:**
- A JSON object containing tide predictions.

### get_aches_and_pains_index

**Description:** Get the Aches and Pains Index for a location from The Weather Company API.

**Input Parameters:**
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **postalCode** (string): Postal zip code.
- **countryCode** (string): Country code.
- **forecast_days** (integer, optional, default=3): Number of days for the forecast. Valid options: 3, 5, 7, 10, 15.
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: 'geocode' or both 'postalCode' and 'countryCode' must be specified.*

**Output:**
- A JSON object containing the Aches and Pains Index.

### get_breathing_index

**Description:** Get the Breathing Index for a location from The Weather Company API.

**Input Parameters:**
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **postalCode** (string): Postal zip code.
- **countryCode** (string): Country code.
- **forecast_days** (integer, optional, default=3): Number of days for the forecast. Valid options: 3, 5, 7, 10, 15.
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: 'geocode' or both 'postalCode' and 'countryCode' must be specified.*

**Output:**
- A JSON object containing the Breathing Index.

### get_degree_days_index

**Description:** Get the Degree Days Index for a location from The Weather Company API.

**Input Parameters:**
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **postalCode** (string): Postal zip code.
- **countryCode** (string): Country code.
- **forecast_days** (integer, optional, default=3): Number of days for the forecast. Valid options: 3, 5, 7, 10, 15.
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: 'geocode' or both 'postalCode' and 'countryCode' must be specified.*

**Output:**
- A JSON object containing the Degree Days Index.

### get_driving_difficulty_index

**Description:** Get the Driving Difficulty Index for a location from The Weather Company API.

**Input Parameters:**
- **forecast_period** (string): Forecast period. Valid options: 'current', '3day', '5day', '7day', '10day', '15day', '6hour', '24hour', '48hour', '72hour', '120hour', '240hour', '360hour'.
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **postalCode** (string): Postal zip code.
- **countryCode** (string): Country code.
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: 'geocode' or both 'postalCode' and 'countryCode' must be specified.*

**Output:**
- A JSON object containing the Driving Difficulty Index.

### get_dry_skin_index

**Description:** Get the Dry Skin Index for a location from The Weather Company API.

**Input Parameters:**
- **forecast_period** (string): Forecast period. Valid options: '3day', '5day', '7day', '10day', '15day', '24hour', '48hour', '72hour', '120hour', '240hour', '360hour'.
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **postalCode** (string): Postal zip code.
- **countryCode** (string): Country code.
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: 'geocode' or both 'postalCode' and 'countryCode' must be specified.*

**Output:**
- A JSON object containing the Dry Skin Index.

### get_frizz_index

**Description:** Get the Frizz Index for a location from The Weather Company API.

**Input Parameters:**
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **postalCode** (string): Postal zip code.
- **countryCode** (string): Country code.
- **forecast_days** (integer, optional, default=3): Number of days for the forecast. Valid options: 3, 5, 7, 10, 15.
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: 'geocode' or both 'postalCode' and 'countryCode' must be specified.*

**Output:**
- A JSON object containing the Frizz Index.

### get_frost_potential_index

**Description:** Get the Frost Potential Index for a location from The Weather Company API.

**Input Parameters:**
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **postalCode** (string): Postal zip code.
- **countryCode** (string): Country code.
- **forecast_days** (integer, optional, default=3): Number of days for the forecast. Valid options: 3, 5, 7, 10, 15.
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: 'geocode' or both 'postalCode' and 'countryCode' must be specified.*

**Output:**
- A JSON object containing the Frost Potential Index.

### get_golf_index

**Description:** Get the Golf Index for a location from The Weather Company API.

**Input Parameters:**
- **forecast_period** (string): Forecast period. Valid options: '3day', '5day', '7day', '10day', '15day', '24hour', '48hour', '72hour', '120hour', '240hour', '360hour'.
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **postalCode** (string): Postal zip code.
- **countryCode** (string): Country code.
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: 'geocode' or both 'postalCode' and 'countryCode' must be specified.*

**Output:**
- A JSON object containing the Golf Index.

### get_heating_and_cooling_index

**Description:** Get the Heating and Cooling Index for a location from The Weather Company API.

**Input Parameters:**
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **postalCode** (string): Postal zip code.
- **countryCode** (string): Country code.
- **forecast_days** (integer, optional, default=3): Number of days for the forecast. Valid options: 3, 5, 7, 10, 15.
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: 'geocode' or both 'postalCode' and 'countryCode' must be specified.*

**Output:**
- A JSON object containing the Heating and Cooling Index.

### get_leisure_travel_index

**Description:** Get the Leisure Travel Index for a location from The Weather Company API.

**Input Parameters:**
- **forecast_period** (string): Forecast period. Valid options: '3day', '5day', '7day', '10day', '15day', '24hour', '48hour', '72hour', '120hour', '240hour', '360hour'.
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **postalCode** (string): Postal zip code.
- **countryCode** (string): Country code.
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: 'geocode' or both 'postalCode' and 'countryCode' must be specified.*

**Output:**
- A JSON object containing the Leisure Travel Index.

### get_mosquito_activity_index

**Description:** Get the Mosquito Activity Index for a location from The Weather Company API.

**Input Parameters:**
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **postalCode** (string): Postal zip code.
- **countryCode** (string): Country code.
- **forecast_days** (integer, optional, default=3): Number of days for the forecast. Valid options: 3, 5, 7, 10, 15.
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: 'geocode' or both 'postalCode' and 'countryCode' must be specified.*

**Output:**
- A JSON object containing the Mosquito Activity Index.

### get_pollen_index

**Description:** Get the Pollen Index for a location from The Weather Company API.

**Input Parameters:**
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **postalCode** (string): Postal zip code.
- **countryCode** (string): Country code.
- **forecast_days** (integer, optional, default=3): Number of days for the forecast. Valid options: 3, 5, 7, 10, 15.
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: 'geocode' or both 'postalCode' and 'countryCode' must be specified.*

**Output:**
- A JSON object containing the Pollen Index.

### get_running_weather_index

**Description:** Get the Running Weather Index for a location from The Weather Company API.

**Input Parameters:**
- **forecast_period** (string): Forecast period. Valid options: '3day', '5day', '7day', '10day', '15day', '24hour', '48hour', '72hour', '120hour', '240hour', '360hour'.
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **postalCode** (string): Postal zip code.
- **countryCode** (string): Country code.
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: 'geocode' or both 'postalCode' and 'countryCode' must be specified.*

**Output:**
- A JSON object containing the Running Weather Index.

### get_ski_index

**Description:** Get the Ski Index for a location from The Weather Company API.

**Input Parameters:**
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **postalCode** (string): Postal zip code.
- **countryCode** (string): Country code.
- **forecast_days** (integer, optional, default=3): Number of days for the forecast. Valid options: 3, 5, 7, 10, 15.
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: 'geocode' or both 'postalCode' and 'countryCode' must be specified.*

**Output:**
- A JSON object containing the Ski Index.

### get_static_electricity_index

**Description:** Get the Static Electricity Index for a location from The Weather Company API.

**Input Parameters:**
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **postalCode** (string): Postal zip code.
- **countryCode** (string): Country code.
- **forecast_days** (integer, optional, default=3): Number of days for the forecast. Valid options: 3, 5, 7, 10, 15.
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: 'geocode' or both 'postalCode' and 'countryCode' must be specified.*

**Output:**
- A JSON object containing the Static Electricity Index.

### get_uv_index

**Description:** Get the UV Index for a location from The Weather Company API.

**Input Parameters:**
- **forecast_period** (string): Forecast period. Valid options: 'current', '15min', '3day', '5day', '7day', '10day', '15day', '6hour', '24hour', '48hour', '72hour', '120hour', '240hour', '360hour'.
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **postalCode** (string): Postal zip code.
- **countryCode** (string): Country code.
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: 'geocode' or both 'postalCode' and 'countryCode' must be specified.*

**Output:**
- A JSON object containing the UV Index.

### get_watering_needs_index

**Description:** Get the Watering Needs Index for a location from The Weather Company API.

**Input Parameters:**
- **geocode** (string): Latitude and longitude of the location formatted as 'lat,lon'.
- **postalCode** (string): Postal zip code.
- **countryCode** (string): Country code.
- **forecast_days** (integer, optional, default=3): Number of days for the forecast. Valid options: 3, 5, 7, 10, 15.
- **language** (string, optional, default='en-US'): Language of the returned content.

*Note: 'geocode' or both 'postalCode' and 'countryCode' must be specified.*

**Output:**
- A JSON object containing the Watering Needs Index.

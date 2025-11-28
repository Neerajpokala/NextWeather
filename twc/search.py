import requests

api_key = "2f0d3367a95f46be8d3367a95f66be31"
url = "https://api.weather.com/v3/location/search"

params = {
    "query": "Hyderabad",          # City name or location string
    "language": "en-US",           # Language code
    "format": "json",              # Request JSON output
    "apiKey": api_key,             # Your Weather Company API key
    # Optional extras:
    # "proximity": "17.3850,78.4867",    # Bias results near this lat,lon
    # "locationType": "city",            # Restrict to city results
    # "countryCode": "IN",
    # "fuzzyMatch": "true"
}

response = requests.get(url, params=params)
print(response.json())

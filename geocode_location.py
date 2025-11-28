
import sys
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from urllib.error import HTTPError

# ==============================================================================
# IMPORTANT: USAGE POLICY FOR NOMINATIM (GEOCODING SERVICE)
# ==============================================================================
# The Nominatim service used here is a free, public resource. To prevent abuse,
# they REQUIRE a unique User-Agent that identifies your application.
#
# PLEASE CHANGE THIS to a unique identifier, like your app's name and your
# email address. For example: "MyWeatherApp/1.0 (your-email@example.com)"
#
# Failure to do so may result in a 403 Forbidden error.
# ==============================================================================
USER_AGENT = "NextWeatherGeocoder/1.0 (Neeraj.Pokala@minfytech.com)"

def get_lat_lon(location_name: str):
    """
    Converts a location name to its latitude and longitude using Nominatim.
    """
    geolocator = Nominatim(user_agent=USER_AGENT)
    
    print(f"Searching for '{location_name}'...")
    try:
        location = geolocator.geocode(location_name, timeout=10) # Increased timeout
        if location:
            print(f"Found: {location.address}")
            return location.latitude, location.longitude
        else:
            print(f"Could not find coordinates for '{location_name}'. Please try a more specific name.")
            return None, None
    except HTTPError as e:
        if e.code == 403:
            print(f"Geocoding service error: HTTP {e.code} Forbidden.")
            print("This usually means the User-Agent is being blocked for being too generic.")
            print(f"Please ensure the USER_AGENT in this script is unique and descriptive (e.g., 'MyCoolApp/1.0 my-email@domain.com').")
        else:
            print(f"Geocoding service returned an HTTP error: {e}")
        return None, None
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        print(f"Geocoding service error: {e}. Please check your internet connection or try again later.")
        return None, None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None, None

if __name__ == "__main__":
    # Ensure geopy is installed
    try:
        from geopy.geocoders import Nominatim
    except ImportError:
        print("Error: 'geopy' library not found.")
        print("Please install it using: pip install geopy")
        sys.exit(1)

    print("--- Location Geocoder ---")
    print("Enter a location name (e.g., 'New York City', 'Minneapolis, MN'). Type 'exit' to quit.")
    
    while True:
        user_input = input("Location: ")
        if user_input.lower() == 'exit':
            break
        
        latitude, longitude = get_lat_lon(user_input)
        
        if latitude is not None and longitude is not None:
            print(f"Latitude: {latitude}, Longitude: {longitude}\n")
        else:
            print("Failed to retrieve coordinates.\n")
            
    print("--- Geocoder exited ---")

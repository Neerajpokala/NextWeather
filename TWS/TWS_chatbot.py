import os
from standard_apis import CoreAPI, EnhancedCurrentConditionsAPI, EnhancedForecastsAPI, LifestyleIndicesAPI
import re
import pandas as pd 
from datetime import datetime

# --- Configuration ---
# IMPORTANT: Make sure to set your WEATHER_API_KEY in your environment variables.
API_KEY = '2f0d3367a95f46be8d3367a95f66be31'

# --- Intent Recognition ---

def get_intent(query):
    """
    Parses the user's query to determine the intent and extract entities.
    This is a simple rule-based approach. A more advanced solution would use an NLU library.
    """
    query = query.lower()
    
    # Pattern for N-day daily forecast (e.g., "15 day forecast", "daily forecast for 5 days")
    daily_forecast_match = re.search(r'(\d+)\s*day\s*(daily\s*)?forecast', query)
    if daily_forecast_match:
        return {
            "intent": "get_daily_forecast",
            "entities": {"days": int(daily_forecast_match.group(1))}
        }
    if "daily forecast" in query:
        return {"intent": "get_daily_forecast", "entities": {}}

    # Pattern for current conditions
    if "current" in query or "right now" in query:
        return {"intent": "get_current_conditions", "entities": {}}

    # Add more intent patterns here...
    
    return {"intent": None, "entities": {}}


# --- API Interaction Handlers ---

def handle_daily_forecast(entities):
    """Handles the logic for the get_daily_forecast intent."""
    if not API_KEY:
        print("Chatbot: API_KEY is not set. Please set the WEATHER_API_KEY environment variable.")
        return

    try:
        # 1. Get required parameters from the user
        days = entities.get('days')
        if not days:
            days_input = input("Chatbot: For how many days would you like the forecast? (3, 5, 7, 10, 15) ")
            days = int(days_input)

        location = input("Chatbot: Please provide a location (e.g., geocode 'lat,lon', postalKey 'zip:country'): ")

        # 2. Initialize the API and call the function
        print(f"Chatbot: Getting {days}-day daily forecast for {location}...")
        api = CoreAPI(API_KEY)
        
        # This is a simplified location handling. We assume postalKey for non-geocode.
        if ',' in location:
            forecast = api.get_daily_forecast(geocode=location, forecast_days=days)
        else:
            forecast = api.get_daily_forecast(postalKey=location, forecast_days=days)

        # 3. Save the raw JSON result and process for CSV/summary
        if forecast:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save raw JSON
            json_filename = f"daily_forecast_{timestamp}.json"
            with open(json_filename, 'w') as f:
                import json
                json.dump(forecast, f, indent=2)
            print(f"\nChatbot: Successfully saved the raw JSON forecast data to '{json_filename}'.")

            # Convert to CSV and save (using json_normalize for all columns)
            try:
                df = pd.json_normalize(forecast)

                csv_filename = f"daily_forecast_{timestamp}.csv"
                df.to_csv(csv_filename, index=False)
                print(f"Chatbot: Successfully saved the daily forecast data to '{csv_filename}'.\n")

                # Generate summary table for chat (using the same columns as before for now)
                if not df.empty:
                    # Ensure columns exist before trying to display them
                    summary_columns = ['dayOfWeek', 'narrative', 'calendarDayTemperatureMax', 'calendarDayTemperatureMin', 'qpf']
                    available_columns = [col for col in summary_columns if col in df.columns]
                    
                    if available_columns:
                        display_df = df[available_columns]
                        print("Chatbot: Here's a summary of the daily forecast:")
                        print(display_df.to_string(index=False)) # Use to_string for better console output
                        print("\n")
                    else:
                        print("Chatbot: No standard summary columns found in the forecast data.")
                else:
                    print("Chatbot: The forecast data was empty, so no summary table could be generated.")

            except Exception as e:
                print(f"Chatbot: Could not process the forecast data into a CSV or generate a summary. Error: {e}")
                print("Chatbot: Please check the raw JSON file for details.")
        else:
            print("Chatbot: Could not retrieve the forecast. Please check your input and API key.")

    except ValueError:
        print("Chatbot: Invalid input. Number of days must be an integer.")
    except Exception as e:
        print(f"An error occurred: {e}")


def handle_current_conditions():
    """Handles the logic for the get_current_conditions intent."""
    if not API_KEY:
        print("Chatbot: API_KEY is not set. Please set the WEATHER_API_KEY environment variable.")
        return

    try:
        # 1. Get required parameters
        location = input("Chatbot: Please provide a location (e.g., geocode 'lat,lon', postalKey 'zip:country'): ")

        # 2. Initialize the API and call the function
        print(f"Chatbot: Getting current conditions for {location}...")
        api = EnhancedCurrentConditionsAPI(API_KEY) # Using the enhanced API for more location options

        if ',' in location:
            conditions = api.get_current_conditions(geocode=location)
        else:
            conditions = api.get_current_conditions(postalKey=location)

        # 3. Save the raw JSON result
        if conditions:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"current_conditions_{timestamp}.json"
            with open(filename, 'w') as f:
                import json
                json.dump(conditions, f, indent=2)
            print(f"\nChatbot: Successfully saved the raw JSON current conditions to '{filename}'.\n")
            print("Chatbot: Raw JSON response saved. You can analyze it from the file.")
        else:
            print("Chatbot: Could not retrieve the conditions. Please check your input and API key.")

    except Exception as e:
        print(f"An error occurred: {e}")


# --- Main Chat Loop ---

def chatbot():
    """Main function to run the chatbot."""
    print("Weather Chatbot: Hello! How can I help you today?")
    print("Weather Chatbot: You can ask for a 'daily forecast' or 'current conditions'. Type 'exit' to quit.")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Weather Chatbot: Goodbye!")
            break

        parsed_info = get_intent(user_input)
        intent = parsed_info["intent"]
        entities = parsed_info["entities"]

        if intent == "get_daily_forecast":
            handle_daily_forecast(entities)
        elif intent == "get_current_conditions":
            handle_current_conditions()
        else:
            print("Weather Chatbot: I'm sorry, I don't understand that. Please ask about 'daily forecast' or 'current conditions'.")

if __name__ == "__main__":
    chatbot()

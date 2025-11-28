import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from components.chat_ui import create_chat_layout, create_message_bubble
from services.weather_service import WeatherService
from services.llm_service import LLMService
import config
import os

# Initialize App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], title="NextWeather Chatbot")

# Initialize Services
weather_service = WeatherService(config.NWS_USER_AGENT)
try:
    llm_service = LLMService(config.GEMINI_API_KEY)
except ValueError as e:
    print(f"Warning: {e}")
    llm_service = None

# Layout
app.layout = html.Div([
    create_chat_layout()
], style={'backgroundColor': '#f0f2f5', 'minHeight': '100vh', 'padding': '40px'})

# Callbacks
@app.callback(
    [Output('chat-messages', 'children'),
     Output('chat-history', 'data'),
     Output('chat-input', 'value')],
    [Input('chat-send-btn', 'n_clicks'),
     Input('chat-input', 'n_submit')],
    [State('chat-input', 'value'),
     State('chat-location', 'value'),
     State('chat-history', 'data')],
    prevent_initial_call=True
)
def handle_chat(n_clicks, n_submit, message, location, history):
    if not message or not location:
        return dash.no_update, dash.no_update, dash.no_update
    
    # Initialize history if None
    if history is None:
        history = []
        
    # Append User Message
    history.append({'role': 'user', 'content': message})
    
    # Process Response
    if not llm_service:
        response_text = "Error: Gemini API Key is missing. Please configure it in .env file."
    else:
        try:
            lat, lon = map(float, location.split(','))
            
            # 1. Fetch Weather Data
            weather_data = weather_service.get_weather_data(lat, lon)
            
            if "error" in weather_data:
                response_text = f"Error fetching weather data: {weather_data['error']}"
            else:
                # 2. Build Context
                current = weather_service.get_current_conditions(weather_data['grid'])
                forecast = weather_service.get_forecast_summary(weather_data['forecast'])
                hazards = weather_service.get_hazards(weather_data['grid'])
                
                context = f"{current}\n\n{forecast}\n\n{hazards}"
                
                # 3. Generate LLM Response
                response_text = llm_service.generate_response(message, context)
                
        except ValueError:
            response_text = "Invalid location format. Please use 'lat,lon'."
        except Exception as e:
            response_text = f"An unexpected error occurred: {str(e)}"
            
    # Append Assistant Response
    history.append({'role': 'assistant', 'content': response_text})
    
    # Re-render messages
    bubbles = [create_message_bubble(msg['role'], msg['content']) for msg in history]
    
    return bubbles, history, ""

if __name__ == '__main__':
    app.run(debug=config.DEBUG, port=config.PORT)

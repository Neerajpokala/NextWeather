import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import json
import os
from datetime import datetime
import uuid

# -- DUMMY USERS --
USER_DB = {
    "neeraj": "123456",
    "admin": "admin123"
}

CITIES = ["Seattle, WA", "New York, NY"]

# JSON file path for storing chat history
CHAT_HISTORY_DIR = "/home/claude/chat_sessions"
os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)

def get_user_chats_dir(username):
    """Get the directory for a user's chat sessions"""
    user_dir = os.path.join(CHAT_HISTORY_DIR, username)
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

def get_chat_file_path(username, chat_id):
    """Get the JSON file path for a specific chat session"""
    user_dir = get_user_chats_dir(username)
    return os.path.join(user_dir, f"chat_{chat_id}.json")

def create_new_chat(username):
    """Create a new chat session and return its ID"""
    chat_id = str(uuid.uuid4())[:8]  # Short unique ID
    chat_data = {
        "chat_id": chat_id,
        "username": username,
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "title": f"Chat {datetime.now().strftime('%b %d, %I:%M %p')}",
        "messages": [
            {"role": "assistant", "content": "Hi, I am a weather assistant. How can I help you?"}
        ]
    }
    filepath = get_chat_file_path(username, chat_id)
    with open(filepath, 'w') as f:
        json.dump(chat_data, f, indent=2)
    return chat_id

def save_chat_to_json(username, chat_id, messages, title=None):
    """Save chat messages to JSON file"""
    filepath = get_chat_file_path(username, chat_id)
    
    # Load existing data to preserve metadata
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            chat_data = json.load(f)
    else:
        chat_data = {
            "chat_id": chat_id,
            "username": username,
            "created_at": datetime.now().isoformat(),
        }
    
    chat_data["last_updated"] = datetime.now().isoformat()
    chat_data["messages"] = messages
    if title:
        chat_data["title"] = title
    
    with open(filepath, 'w') as f:
        json.dump(chat_data, f, indent=2)

def load_chat_from_json(username, chat_id):
    """Load chat messages from JSON file"""
    filepath = get_chat_file_path(username, chat_id)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            chat_data = json.load(f)
            return chat_data
    return None

def list_user_chats(username):
    """List all chat sessions for a user"""
    user_dir = get_user_chats_dir(username)
    chat_files = [f for f in os.listdir(user_dir) if f.startswith('chat_') and f.endswith('.json')]
    
    chats = []
    for chat_file in chat_files:
        filepath = os.path.join(user_dir, chat_file)
        with open(filepath, 'r') as f:
            chat_data = json.load(f)
            chats.append({
                "chat_id": chat_data.get("chat_id"),
                "title": chat_data.get("title", "Untitled Chat"),
                "last_updated": chat_data.get("last_updated"),
                "created_at": chat_data.get("created_at")
            })
    
    # Sort by last_updated (most recent first)
    chats.sort(key=lambda x: x.get("last_updated", ""), reverse=True)
    return chats

def delete_chat(username, chat_id):
    """Delete a chat session"""
    filepath = get_chat_file_path(username, chat_id)
    if os.path.exists(filepath):
        os.remove(filepath)

def get_lat_lon(location):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={location}"
    headers = {'User-Agent': 'weather-app'}
    resp = requests.get(url, headers=headers)
    data = resp.json()
    if not data:
        raise ValueError(f"Location not found: {location}")
    return float(data[0]['lat']), float(data[0]['lon'])

def get_forecast_hourly(lat, lon):
    points_url = f"https://api.weather.gov/points/{lat},{lon}"
    points_resp = requests.get(points_url)
    forecast_hourly_url = points_resp.json()["properties"]["forecastHourly"]
    forecast_resp = requests.get(forecast_hourly_url)
    forecast_data = forecast_resp.json()["properties"]["periods"]
    df = pd.DataFrame(forecast_data)
    return df

def create_chart_from_config(chart_config):
    """Recreate a Plotly chart from stored configuration"""
    chart_type = chart_config.get("type")
    data = pd.DataFrame(chart_config.get("data", []))
    
    if data.empty:
        return None
    
    x = chart_config.get("x")
    y = chart_config.get("y")
    title = chart_config.get("title")
    
    if chart_type == "line":
        fig = px.line(data, x=x, y=y, title=title)
    elif chart_type == "scatter":
        fig = px.scatter(data, x=x, y=y, title=title)
    else:
        return None
    
    return fig

def logout():
    # Save current chat before logout
    if "username" in st.session_state and "current_chat_id" in st.session_state and "messages" in st.session_state:
        save_chat_to_json(st.session_state.username, st.session_state.current_chat_id, st.session_state.messages)
    
    st.session_state.logged_in = False
    st.session_state.clear()
    st.rerun()

def load_chat_session(chat_id):
    """Load a specific chat session"""
    chat_data = load_chat_from_json(st.session_state.username, chat_id)
    if chat_data:
        st.session_state.current_chat_id = chat_id
        st.session_state.messages = chat_data.get("messages", [])
        st.session_state.chat_title = chat_data.get("title", "Untitled Chat")
        
        # Restore stage based on last message
        if st.session_state.messages:
            last_msg = st.session_state.messages[-1]
            if last_msg.get("type") == "forecast_data":
                st.session_state.stage = "show_forecast"
            elif last_msg.get("type") == "city_select":
                st.session_state.stage = "choose_city"
            elif last_msg.get("type") == "forecast_option":
                st.session_state.stage = "await_forecast"
            else:
                st.session_state.stage = "init"
        else:
            st.session_state.stage = "init"
        
        st.session_state.selected_city = None

def start_new_chat():
    """Start a new chat session"""
    # Save current chat
    if "current_chat_id" in st.session_state and "messages" in st.session_state:
        save_chat_to_json(st.session_state.username, st.session_state.current_chat_id, st.session_state.messages)
    
    # Create new chat
    new_chat_id = create_new_chat(st.session_state.username)
    load_chat_session(new_chat_id)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Login to Weather Assistant")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if USER_DB.get(username) == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            
            # Check if user has existing chats
            user_chats = list_user_chats(username)
            if user_chats:
                # Load the most recent chat
                load_chat_session(user_chats[0]["chat_id"])
            else:
                # Create first chat
                new_chat_id = create_new_chat(username)
                load_chat_session(new_chat_id)
            
            st.rerun()
        else:
            st.error("Invalid credentials. Try again.")
else:
    # Sidebar with chat history
    with st.sidebar:
        st.title("💬 Chat History")
        
        # New Chat button
        if st.button("➕ New Chat", use_container_width=True):
            start_new_chat()
            st.rerun()
        
        st.divider()
        
        # List all chats
        user_chats = list_user_chats(st.session_state.username)
        
        if user_chats:
            st.subheader("Your Chats")
            for chat in user_chats:
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    # Highlight current chat
                    is_current = chat["chat_id"] == st.session_state.get("current_chat_id")
                    button_label = f"{'🟢 ' if is_current else ''}{chat['title']}"
                    
                    if st.button(button_label, key=f"chat_{chat['chat_id']}", use_container_width=True):
                        if not is_current:
                            # Save current chat before switching
                            if "current_chat_id" in st.session_state and "messages" in st.session_state:
                                save_chat_to_json(st.session_state.username, st.session_state.current_chat_id, 
                                                st.session_state.messages)
                            
                            # Load selected chat
                            load_chat_session(chat["chat_id"])
                            st.rerun()
                
                with col2:
                    if st.button("🗑️", key=f"delete_{chat['chat_id']}"):
                        delete_chat(st.session_state.username, chat["chat_id"])
                        
                        # If deleted chat was current, load another or create new
                        if chat["chat_id"] == st.session_state.get("current_chat_id"):
                            remaining_chats = list_user_chats(st.session_state.username)
                            if remaining_chats:
                                load_chat_session(remaining_chats[0]["chat_id"])
                            else:
                                new_chat_id = create_new_chat(st.session_state.username)
                                load_chat_session(new_chat_id)
                        
                        st.rerun()
        else:
            st.info("No chats yet. Start a new chat!")
        
        st.divider()
        st.button("Logout", on_click=logout, use_container_width=True)
    
    # Main chat area
    st.title(f"Welcome, {st.session_state.username}!")
    
    # Display current chat title
    if "chat_title" in st.session_state:
        st.caption(f"📝 {st.session_state.chat_title}")

    # --- Initialize session state ---
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi, I am a weather assistant. How can I help you?"}
        ]
    if "stage" not in st.session_state:
        st.session_state.stage = "init"
    if "selected_city" not in st.session_state:
        st.session_state.selected_city = None

    # Display all chat messages
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "🤖"):
            if message["role"] == "assistant" and "type" in message:
                # Special handling for different message types
                if message["type"] == "city_select":
                    st.write(message["content"])
                    # Show city selection buttons only for the last assistant message
                    if idx == len(st.session_state.messages) - 1 and st.session_state.stage == "choose_city":
                        cols = st.columns(len(CITIES))
                        for i, city in enumerate(CITIES):
                            if cols[i].button(city, key=f"city_btn_{city}"):
                                # Add user selection message
                                st.session_state.messages.append({"role": "user", "content": city})
                                st.session_state.selected_city = city
                                st.session_state.stage = "show_forecast"
                                save_chat_to_json(st.session_state.username, st.session_state.current_chat_id, 
                                                st.session_state.messages)
                                st.rerun()
                                
                elif message["type"] == "forecast_data":
                    st.write(message["content"])
                    
                    # Display the dataframe
                    if "df_data" in message:
                        df = pd.DataFrame(message["df_data"])
                        st.dataframe(df)
                    
                    # Recreate charts from stored configurations
                    if "charts" in message:
                        for chart_idx, chart_config in enumerate(message["charts"]):
                            fig = create_chart_from_config(chart_config)
                            if fig:
                                st.plotly_chart(fig, key=f"chart_{idx}_{chart_idx}")
                    
                    # Show "Start Over" button only for the last message
                    if idx == len(st.session_state.messages) - 1:
                        if st.button("🔄 Start Over", key="start_over_btn"):
                            st.session_state.messages = [
                                {"role": "assistant", "content": "Hi, I am a weather assistant. How can I help you?"}
                            ]
                            st.session_state.stage = "init"
                            st.session_state.selected_city = None
                            save_chat_to_json(st.session_state.username, st.session_state.current_chat_id, 
                                            st.session_state.messages)
                            st.rerun()
                            
                elif message["type"] == "error":
                    st.error(message["content"])
                    # Show "Start Over" button only for the last message
                    if idx == len(st.session_state.messages) - 1:
                        if st.button("🔄 Start Over", key="start_over_error_btn"):
                            st.session_state.messages = [
                                {"role": "assistant", "content": "Hi, I am a weather assistant. How can I help you?"}
                            ]
                            st.session_state.stage = "init"
                            st.session_state.selected_city = None
                            save_chat_to_json(st.session_state.username, st.session_state.current_chat_id, 
                                            st.session_state.messages)
                            st.rerun()
                            
                elif message["type"] == "forecast_option":
                    st.write(message["content"])
                    # Show forecast button only for the last assistant message
                    if idx == len(st.session_state.messages) - 1 and st.session_state.stage == "await_forecast":
                        if st.button("Show Forecast", key="forecast_btn"):
                            # Add user message
                            st.session_state.messages.append({"role": "user", "content": "Forecast"})
                            # Add assistant response asking for city
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": "Select a city for the forecast:",
                                "type": "city_select"
                            })
                            st.session_state.stage = "choose_city"
                            save_chat_to_json(st.session_state.username, st.session_state.current_chat_id, 
                                            st.session_state.messages)
                            st.rerun()
                else:
                    st.write(message["content"])
            else:
                st.write(message["content"])

    # Handle new user input via chat
    user_input = st.chat_input("Type your message...")

    if user_input:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Process based on current stage
        if st.session_state.stage == "init":
            if user_input.strip().lower() in ["hi", "hello", "hey"]:
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "Choose an option below:",
                    "type": "forecast_option"
                })
                st.session_state.stage = "await_forecast"
            else:
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "Please say 'Hi' to start the conversation."
                })
        
        save_chat_to_json(st.session_state.username, st.session_state.current_chat_id, st.session_state.messages)
        st.rerun()

    # Handle forecast generation when city is selected
    if st.session_state.stage == "show_forecast" and st.session_state.selected_city:
        # Check if we haven't already shown the forecast
        last_message = st.session_state.messages[-1] if st.session_state.messages else None
        if not (last_message and last_message.get("type") == "forecast_data"):
            city = st.session_state.selected_city
            try:
                lat, lon = get_lat_lon(city)
                df = get_forecast_hourly(lat, lon)
                
                # Process the dataframe
                if 'probabilityOfPrecipitation' in df.columns:
                    df['probabilityOfPrecipitation_value'] = df['probabilityOfPrecipitation'].apply(
                        lambda x: x['value'] if isinstance(x, dict) and 'value' in x else None)
                if 'dewpoint' in df.columns:
                    df['dewpoint_value'] = df['dewpoint'].apply(
                        lambda x: x['value'] if isinstance(x, dict) and 'value' in x else None)
                if 'relativeHumidity' in df.columns:
                    df['relativeHumidity_value'] = df['relativeHumidity'].apply(
                        lambda x: x['value'] if isinstance(x, dict) and 'value' in x else None)
                
                # Extract wind speed numbers
                if pd.api.types.is_string_dtype(df['windSpeed']):
                    df['windSpeed_num'] = df['windSpeed'].str.extract(r'(\d+)').astype(float)
                
                # Select relevant columns for display
                display_columns = [
                    "number", "name", "startTime", "endTime", "isDaytime",
                    "temperature", "temperatureUnit", "temperatureTrend", 
                    "probabilityOfPrecipitation_value", "dewpoint_value", 
                    "relativeHumidity_value", "windSpeed", "windDirection", 
                    "shortForecast", "detailedForecast"
                ]
                display_df = df[display_columns].copy()
                
                # Add wind speed numeric if available
                if 'windSpeed_num' in df.columns:
                    display_df['windSpeed_num'] = df['windSpeed_num']
                
                # Prepare chart configurations to store in JSON
                charts = []
                
                # Temperature chart
                if "temperature" in df.columns:
                    charts.append({
                        "type": "line",
                        "x": "startTime",
                        "y": "temperature",
                        "title": "Temperature (°F) Over Time",
                        "data": df[["startTime", "temperature"]].to_dict('records')
                    })
                
                # Precipitation chart
                if "probabilityOfPrecipitation_value" in df.columns:
                    charts.append({
                        "type": "line",
                        "x": "startTime",
                        "y": "probabilityOfPrecipitation_value",
                        "title": "Probability of Precipitation (%) Over Time",
                        "data": df[["startTime", "probabilityOfPrecipitation_value"]].to_dict('records')
                    })
                
                # Dewpoint chart
                if "dewpoint_value" in df.columns:
                    charts.append({
                        "type": "line",
                        "x": "startTime",
                        "y": "dewpoint_value",
                        "title": "Dew Point (°F) Over Time",
                        "data": df[["startTime", "dewpoint_value"]].to_dict('records')
                    })
                
                # Humidity chart
                if "relativeHumidity_value" in df.columns:
                    charts.append({
                        "type": "line",
                        "x": "startTime",
                        "y": "relativeHumidity_value",
                        "title": "Relative Humidity (%) Over Time",
                        "data": df[["startTime", "relativeHumidity_value"]].to_dict('records')
                    })
                
                # Wind speed chart
                if "windSpeed_num" in df.columns:
                    charts.append({
                        "type": "line",
                        "x": "startTime",
                        "y": "windSpeed_num",
                        "title": "Wind Speed Over Time (mph)",
                        "data": df[["startTime", "windSpeed_num"]].to_dict('records')
                    })
                
                # Wind direction chart
                if "windDirection" in df.columns:
                    charts.append({
                        "type": "scatter",
                        "x": "startTime",
                        "y": "windDirection",
                        "title": "Wind Direction Over Time",
                        "data": df[["startTime", "windDirection"]].to_dict('records')
                    })
                
                # Short forecast chart
                if "shortForecast" in df.columns:
                    charts.append({
                        "type": "scatter",
                        "x": "startTime",
                        "y": "shortForecast",
                        "title": "Short Forecast Over Time",
                        "data": df[["startTime", "shortForecast"]].to_dict('records')
                    })
                
                # Add assistant message with forecast data and chart configs
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Weather forecast for **{city}**:",
                    "type": "forecast_data",
                    "df_data": display_df.to_dict('records'),
                    "charts": charts
                })
                
                save_chat_to_json(st.session_state.username, st.session_state.current_chat_id, st.session_state.messages)
                
            except Exception as e:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Sorry, I encountered an error: {str(e)}",
                    "type": "error"
                })
                save_chat_to_json(st.session_state.username, st.session_state.current_chat_id, st.session_state.messages)
            
            st.rerun()
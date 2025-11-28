from dash import Dash, html, dcc, callback, Output, Input, State, ctx, ALL
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
import json
import isodate
from datetime import datetime, timedelta, timezone
import sys
import os

# Add chatbot_forecast to path to import services
sys.path.append(os.path.join(os.path.dirname(__file__), 'chatbot_forecast'))
from services.weather_service import WeatherService
from services.llm_service import LLMService
from components.chat_ui import create_message_bubble
import config


# Initialize Dash App
app = Dash(__name__, title="NextWeather Dashboard", suppress_callback_exceptions=True)

# Initialize Chatbot Services
weather_service = WeatherService(config.NWS_USER_AGENT)
try:
    llm_service = LLMService(config.GEMINI_API_KEY)
except ValueError as e:
    print(f"Warning: {e}")
    llm_service = None

# Inject custom CSS for hover effects
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* KPI Card Hover - Light Mode */
            body:not(.dark-mode) .kpi-card:hover {
                background-color: #f0f8ff !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
                transform: translateY(-2px);
                cursor: pointer;
            }
            
            /* KPI Card Hover - Dark Mode */
            body.dark-mode .kpi-card:hover {
                background-color: #2d3748 !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.8) !important;
                transform: translateY(-2px);
                cursor: pointer;
            }
            
            /* Graph Card Hover - Light Mode */
            body:not(.dark-mode) .graph-card:hover {
                background-color: #f0f8ff !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
                transform: translateY(-2px);
            }
            
            /* Graph Card Hover - Dark Mode */
            body.dark-mode .graph-card:hover {
                background-color: #2d3748 !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.8) !important;
                transform: translateY(-2px);
            }
            
            /* Smooth transitions */
            .kpi-card, .graph-card {
                transition: all 0.3s ease !important;
            }
            
            /* Theme Toggle Button */
            .theme-toggle-btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border: none;
                border-radius: 50px;
                width: 60px;
                height: 32px;
                cursor: pointer;
                position: relative;
                transition: all 0.3s ease;
                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            }
            
            .theme-toggle-btn:hover {
                transform: scale(1.05);
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            }
            
            .theme-toggle-btn:active {
                transform: scale(0.95);
            }
            
            /* Toggle Circle */
            .theme-toggle-btn::before {
                content: '🌙';
                position: absolute;
                top: 2px;
                left: 2px;
                width: 28px;
                height: 28px;
                background: white;
                border-radius: 50%;
                transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 16px;
                line-height: 28px;
                text-align: center;
            }
            
            /* Dark Mode Toggle */
            body.dark-mode .theme-toggle-btn {
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            }
            
            body.dark-mode .theme-toggle-btn::before {
                content: '☀️';
                left: 30px;
            }
            
            /* Chatbot Popup */
            .chatbot-popup {
                position: fixed;
                bottom: 60px;
                right: 20px;
                width: 350px;
                height: 500px;
                background-color: white;
                border-radius: 15px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.2);
                z-index: 1000;
                display: flex;
                flex-direction: column;
                overflow: hidden;
                transition: all 0.3s ease;
                transform: translateY(120%); /* Hidden by default */
            }
            
            .chatbot-popup.open {
                transform: translateY(0);
            }
            
            body.dark-mode .chatbot-popup {
                background-color: #242526;
                border: 1px solid #333;
            }
            
            .chatbot-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                cursor: pointer;
            }
            
            .chatbot-toggle-btn {
                position: fixed;
                bottom: 60px;
                right: 20px;
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                cursor: pointer;
                z-index: 999;
                font-size: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s ease;
            }
            
            .chatbot-toggle-btn:hover {
                transform: scale(1.1);
            }
            
            .chatbot-messages {
                flex: 1;
                overflow-y: auto;
                padding: 15px;
                background-color: #f9f9f9;
            }
            
            body.dark-mode .chatbot-messages {
                background-color: #18191a;
            }
            
            .chatbot-input-area {
                padding: 15px;
                border-top: 1px solid #eee;
                display: flex;
                background-color: white;
            }
            
            body.dark-mode .chatbot-input-area {
                background-color: #242526;
                border-top: 1px solid #333;
            }
            
            /* Notification Bubble */
            .chat-notification {
                position: fixed;
                bottom: 130px;
                right: 20px;
                background-color: white;
                padding: 10px 15px;
                border-radius: 10px;
                border-bottom-right-radius: 0;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                z-index: 998;
                font-size: 14px;
                max-width: 200px;
                animation: float 3s ease-in-out infinite;
                display: block;
            }
            
            body.dark-mode .chat-notification {
                background-color: #242526;
                color: #e0e0e0;
                box-shadow: 0 4px 12px rgba(0,0,0,0.5);
            }
            
            @keyframes float {
                0% { transform: translateY(0px); }
                50% { transform: translateY(-5px); }
                100% { transform: translateY(0px); }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# --- Constants & Styles ---
LIGHT_THEME = {
    'background': '#f0f2f5', # Light gray for better contrast
    'text': '#333333',
    'card_bg': '#ffffff',
    'input_bg': '#ffffff',
    'input_text': '#333333',
    'shadow': '0 2px 4px rgba(0,0,0,0.1)',
    'hover_shadow': '0 4px 12px rgba(0,0,0,0.15)',
    'hover_bg': '#f0f8ff',  # Light blue tint
    'plotly_template': 'plotly',
    'tab': {'borderBottom': '1px solid #d6d6d6', 'padding': '6px', 'fontWeight': 'bold', 'backgroundColor': '#e4e6eb', 'color': '#333'},
    'tab_selected': {'borderTop': '1px solid #d6d6d6', 'borderBottom': '1px solid #d6d6d6', 'backgroundColor': '#ffffff', 'color': '#119DFF', 'padding': '6px'}
}

DARK_THEME = {
    'background': '#18191a',
    'text': '#e0e0e0',
    'card_bg': '#242526',
    'input_bg': '#3a3b3c',
    'input_text': '#e0e0e0',
    'shadow': '0 2px 4px rgba(0,0,0,0.5)',
    'hover_shadow': '0 4px 12px rgba(0,0,0,0.8)',
    'hover_bg': '#2d3748',  # Slightly lighter dark blue
    'plotly_template': 'plotly_dark',
    'tab': {'borderBottom': '1px solid #333', 'padding': '6px', 'fontWeight': 'bold', 'backgroundColor': '#242526', 'color': '#b0b3b8'},
    'tab_selected': {'borderTop': '1px solid #333', 'borderBottom': '1px solid #333', 'backgroundColor': '#18191a', 'color': '#2e89ff', 'padding': '6px'}
}

# --- Helper to wrap graphs in cards ---
def graph_card(graph_id, width='45%'):
    return html.Div(
        id={'type': 'graph-card', 'index': graph_id},
        className='graph-card',
        style={'width': width, 'display': 'inline-block', 'verticalAlign': 'top', 'margin': '10px', 'borderRadius': '8px', 'padding': '10px', 'transition': 'background-color 0.3s'},
        children=[
            dcc.Graph(id=graph_id, style={'height': '350px'})
        ]
    )

# --- Layout ---
app.layout = html.Div(id='main-container', children=[
    # Header Section
    html.Div([
        html.H1("🌤️ NextWeather Analytics Dashboard", style={'textAlign': 'center', 'fontFamily': 'sans-serif', 'marginBottom': '10px'}),
        html.P("Enter coordinates to analyze real-time NWS weather data.", style={'textAlign': 'center', 'fontFamily': 'sans-serif', 'marginBottom': '20px'}),
        
        # Controls Container
        html.Div([
            # Inputs
            html.Div([
                html.Div([
                    html.Label("Latitude", style={'marginRight': '5px'}),
                    dcc.Input(id='lat-input', type='text', value='39.0997', style={'marginRight': '10px', 'width': '100px'}),
                ], style={'display': 'inline-block'}),
                
                html.Div([
                    html.Label("Longitude", style={'marginRight': '5px'}),
                    dcc.Input(id='lon-input', type='text', value='-94.5786', style={'marginRight': '10px', 'width': '100px'}),
                ], style={'display': 'inline-block'}),
                
                html.Button('Fetch Weather Data', id='fetch-btn', n_clicks=0, style={'height': '30px', 'verticalAlign': 'bottom'}),
            ], style={'display': 'inline-block', 'marginRight': '30px'}),

            # Dark Mode Toggle
            html.Div([
                html.Label("Theme: ", style={'marginRight': '10px', 'verticalAlign': 'middle'}),
                html.Button(
                    id='theme-toggle-btn',
                    className='theme-toggle-btn',
                    n_clicks=0,
                    style={'verticalAlign': 'middle'}
                ),
                dcc.Store(id='theme-store', data={'dark': False})
            ], style={'display': 'inline-block', 'verticalAlign': 'bottom'})
            
        ], style={'textAlign': 'center', 'padding': '20px', 'borderRadius': '8px', 'marginBottom': '20px'}, id='controls-container'),
    ]),
    
    # Error Message
    html.Div(id='error-message', style={'color': 'red', 'textAlign': 'center', 'marginBottom': '10px'}),
    
    # Loading Spinner
    dcc.Loading(
        id="loading-1",
        type="default",
        children=html.Div(id="dashboard-content", style={'display': 'none'}, children=[
            
            # Grid Data KPIs (12 Parameters)
            html.H3("Current Conditions (Grid Data)", style={'textAlign': 'center', 'marginTop': '20px'}),
            html.Div(id='grid-kpis-container', style={
                'display': 'grid', 
                'gridTemplateColumns': 'repeat(4, 1fr)', 
                'gap': '15px', 
                'padding': '20px',
                'maxWidth': '1200px',
                'margin': '0 auto'
            }),
            
            # Tabs
            dcc.Tabs(id='main-tabs', children=[
                dcc.Tab(id='tab-24h', label='Next 24 Hours', children=[
                    html.Div([
                        graph_card('graph-24h-temp', width='98%'),
                        graph_card('graph-24h-wind'),
                        graph_card('graph-24h-pop'),
                    ], style={'padding': '20px', 'textAlign': 'center'}),
                ]),
                dcc.Tab(id='tab-temp', label='Temperature & Wind (Full)', children=[
                    html.Div([
                        graph_card('graph-temp'),
                        graph_card('graph-wind'),
                        graph_card('graph-dew'),
                        graph_card('graph-hum'),
                    ], style={'padding': '20px', 'textAlign': 'center'}),
                ]),
                dcc.Tab(id='tab-precip', label='Precipitation & Sky (Full)', children=[
                    html.Div([
                        graph_card('graph-pop'),
                        graph_card('graph-sky'),
                        graph_card('graph-qpf'),
                        graph_card('graph-thunder'),
                    ], style={'padding': '20px', 'textAlign': 'center'}),
                ]),
                dcc.Tab(id='tab-grid', label='Grid Metrics (Full)', children=[
                    html.Div([
                        graph_card('graph-gust'),
                        graph_card('graph-app-temp'),
                    ], style={'padding': '20px', 'textAlign': 'center'}),
                ]),
                dcc.Tab(id='tab-hazards', label='Hazards', children=[
                    html.Div([
                        graph_card('graph-hazards', width='98%'),
                    ], style={'padding': '20px', 'textAlign': 'center'}),
                ]),
            ]),
            
            # Downloads
            html.Div(id='downloads-container', children=[
                html.H3("📥 Download Data"),
                html.Button("Download Daily Forecast", id="btn-download-daily"),
                dcc.Download(id="download-daily"),
                
                html.Button("Download Hourly Forecast", id="btn-download-hourly", style={'marginLeft': '10px'}),
                dcc.Download(id="download-hourly"),
                
                html.Button("Download Grid Metrics", id="btn-download-grid", style={'marginLeft': '10px'}),
                dcc.Download(id="download-grid"),
            ], style={'marginTop': '30px', 'textAlign': 'center', 'padding': '20px', 'borderRadius': '8px'}),
        ])
    ),
    
    # Store for data sharing
    dcc.Store(id='store-forecast'),
    dcc.Store(id='store-hourly'),
    dcc.Store(id='store-grid'),
    
    # Hidden checklist for theme compatibility
    dcc.Checklist(id='theme-toggle', options=[], value=[], style={'display': 'none'}),
    
    # Chatbot Components
    html.Div("👋 Hello! How can I help you with the weather today?", id="chat-notification", className="chat-notification"),
    html.Button("💬", id="chatbot-toggle-btn", className="chatbot-toggle-btn"),
    
    html.Div(id="chatbot-popup", className="chatbot-popup", children=[
        html.Div([
            html.Span("Weather Assistant", style={'fontWeight': 'bold'}),
            html.Span("▼", id="chatbot-close-btn", style={'cursor': 'pointer'})
        ], className="chatbot-header"),
        
        html.Div(id="chat-messages", className="chatbot-messages"),
        
        html.Div([
            dcc.Input(
                id="chat-input",
                type="text",
                placeholder="Ask...",
                style={'flex': '1', 'padding': '8px', 'borderRadius': '20px', 'border': '1px solid #ddd', 'marginRight': '10px'}
            ),
            html.Button("➤", id="chat-send-btn", style={'background': 'none', 'border': 'none', 'color': '#667eea', 'fontSize': '20px', 'cursor': 'pointer'})
        ], className="chatbot-input-area"),
        
        dcc.Store(id="chat-history", data=[]),
        dcc.Store(id="chatbot-open", data=False)
    ]),
    
], style={'fontFamily': 'sans-serif', 'minHeight': '100vh', 'padding': '20px', 'transition': 'background-color 0.3s, color 0.3s'})

# Clientside callback to toggle chatbot visibility
app.clientside_callback(
    """
    function(n_clicks_toggle, n_clicks_close, is_open) {
        const ctx = dash_clientside.callback_context;
        if (!ctx.triggered.length) return dash_clientside.no_update;
        
        const trigger_id = ctx.triggered[0].prop_id.split('.')[0];
        
        let new_state = is_open;
        if (trigger_id === 'chatbot-toggle-btn') {
            new_state = !is_open;
        } else if (trigger_id === 'chatbot-close-btn') {
            new_state = false;
        }
        
        const popup = document.getElementById('chatbot-popup');
        const btn = document.getElementById('chatbot-toggle-btn');
        const notification = document.getElementById('chat-notification');
        
        if (new_state) {
            popup.classList.add('open');
            btn.style.display = 'none';
            if (notification) notification.style.display = 'none';
        } else {
            popup.classList.remove('open');
            btn.style.display = 'flex';
        }
        
        return new_state;
    }
    """,
    Output('chatbot-open', 'data'),
    [Input('chatbot-toggle-btn', 'n_clicks'),
     Input('chatbot-close-btn', 'n_clicks')],
    State('chatbot-open', 'data')
)

# Clientside callback to toggle theme state
app.clientside_callback(
    """
    function(n_clicks, current_state) {
        if (n_clicks > 0) {
            return {'dark': !current_state.dark};
        }
        return current_state;
    }
    """,
    Output('theme-store', 'data'),
    Input('theme-toggle-btn', 'n_clicks'),
    State('theme-store', 'data')
)

# Clientside callback to add/remove dark-mode class to body
app.clientside_callback(
    """
    function(theme_state) {
        if (theme_state && theme_state.dark) {
            document.body.classList.add('dark-mode');
            return ['dark'];
        } else {
            document.body.classList.remove('dark-mode');
            return [];
        }
    }
    """,
    Output('theme-toggle', 'value'),
    Input('theme-store', 'data')
)

# --- Helper Functions ---
def get_weather_data(lat, lon):
    headers = {"User-Agent": "(nextweather-dashboard, contact@example.com)"}
    try:
        points_url = f"https://api.weather.gov/points/{lat},{lon}"
        points_resp = requests.get(points_url, headers=headers)
        points_resp.raise_for_status()
        props = points_resp.json()['properties']
        
        return {
            "forecast": requests.get(props['forecast'], headers=headers).json(),
            "hourly": requests.get(props['forecastHourly'], headers=headers).json(),
            "grid": requests.get(props['forecastGridData'], headers=headers).json()
        }
    except Exception as e:
        return {"error": str(e)}

def process_hourly(data):
    df = pd.DataFrame(data['properties']['periods'])
    df['startTime'] = pd.to_datetime(df['startTime'])
    return df

def get_current_grid_value(grid_data, parameter):
    """Parses Grid Data to find the value for the current UTC time."""
    if parameter not in grid_data['properties']:
        return None, None
        
    now = datetime.now(timezone.utc)
    values = grid_data['properties'][parameter]['values']
    uom = grid_data['properties'][parameter].get('uom', '')
    
    for item in values:
        # Parse validTime: "2025-11-28T14:00:00+00:00/PT1H"
        time_str, duration_str = item['validTime'].split('/')
        start_time = datetime.fromisoformat(time_str)
        duration = isodate.parse_duration(duration_str)
        end_time = start_time + duration
        
        if start_time <= now < end_time:
            return item['value'], uom
            
    return None, None

def create_kpi_card(label, value, unit, theme):
    display_val = f"{value} {unit}" if value is not None else "N/A"
    display_val = display_val.replace("wmoUnit:degC", "°C").replace("wmoUnit:percent", "%").replace("wmoUnit:degree_(angle)", "°").replace("wmoUnit:km_h-1", "km/h")
    
    return html.Div([
        html.H4(label, style={'margin': '0', 'fontSize': '14px', 'color': theme['text'], 'opacity': 0.7}),
        html.H2(display_val, style={'margin': '5px 0', 'fontSize': '24px', 'color': theme['text']}),
    ], className='kpi-card', style={'backgroundColor': theme['card_bg'], 'padding': '15px', 'borderRadius': '8px', 'boxShadow': theme['shadow'], 'transition': 'background-color 0.3s'})

# --- Callbacks ---

# 1. Data Fetching Callback
@callback(
    [Output('store-forecast', 'data'),
     Output('store-hourly', 'data'),
     Output('store-grid', 'data'),
     Output('error-message', 'children')],
    Input('fetch-btn', 'n_clicks'),
    [State('lat-input', 'value'),
     State('lon-input', 'value')],
    prevent_initial_call=True
)
def fetch_data(n_clicks, lat, lon):
    if not n_clicks:
        return None, None, None, ""
    
    data = get_weather_data(lat, lon)
    
    if "error" in data:
        return None, None, None, f"Error: {data['error']}"
        
    return data['forecast'], data['hourly'], data['grid'], ""

# 2. Rendering & Theme Callback
@callback(
    [Output('main-container', 'style'),
     Output('controls-container', 'style'),
     Output('downloads-container', 'style'),
     Output('dashboard-content', 'style'),
     # Tabs Styles
     Output('tab-24h', 'style'), Output('tab-24h', 'selected_style'),
     Output('tab-temp', 'style'), Output('tab-temp', 'selected_style'),
     Output('tab-precip', 'style'), Output('tab-precip', 'selected_style'),
     Output('tab-grid', 'style'), Output('tab-grid', 'selected_style'),
     Output('tab-hazards', 'style'), Output('tab-hazards', 'selected_style'),
     # Grid KPIs
     Output('grid-kpis-container', 'children'),
     # Graph Cards Style (Pattern Matching)
     Output({'type': 'graph-card', 'index': ALL}, 'style'),
     # 24h Graphs
     Output('graph-24h-temp', 'figure'),
     Output('graph-24h-wind', 'figure'),
     Output('graph-24h-pop', 'figure'),
     # Full Graphs
     Output('graph-temp', 'figure'),
     Output('graph-wind', 'figure'),
     Output('graph-dew', 'figure'),
     Output('graph-hum', 'figure'),
     Output('graph-pop', 'figure'),
     Output('graph-sky', 'figure'),
     Output('graph-qpf', 'figure'),
     Output('graph-thunder', 'figure'),
     Output('graph-gust', 'figure'),
     Output('graph-app-temp', 'figure'),
     # Hazards
     Output('graph-hazards', 'figure')],
    [Input('store-forecast', 'data'),
     Input('store-hourly', 'data'),
     Input('store-grid', 'data'),
     Input('theme-toggle', 'value'),
     State({'type': 'graph-card', 'index': ALL}, 'style')]
)
def update_display(forecast_data, hourly_data, grid_data, theme_value, current_card_styles):
    # Determine Theme
    is_dark = 'dark' in theme_value
    theme = DARK_THEME if is_dark else LIGHT_THEME
    
    # Base Styles
    main_style = {'fontFamily': 'sans-serif', 'minHeight': '100vh', 'padding': '20px', 'backgroundColor': theme['background'], 'color': theme['text'], 'transition': 'background-color 0.3s, color 0.3s'}
    controls_style = {'textAlign': 'center', 'padding': '20px', 'borderRadius': '8px', 'marginBottom': '20px', 'backgroundColor': theme['card_bg'], 'boxShadow': theme['shadow'], 'transition': 'background-color 0.3s'}
    downloads_style = {'marginTop': '30px', 'textAlign': 'center', 'padding': '20px', 'borderRadius': '8px', 'backgroundColor': theme['card_bg'], 'boxShadow': theme['shadow'], 'transition': 'background-color 0.3s'}
    
    # Tab Styles
    t_style = theme['tab']
    t_sel_style = theme['tab_selected']
    
    # Graph Card Styles
    # We need to return a list of styles matching the number of graph cards found by ALL
    # If current_card_styles is None or empty, we can't know exactly how many there are yet, 
    # but Dash will handle the length mismatch if we are careful or if we just return the right number based on our known layout.
    # However, 'ALL' outputs expect a list of the same length as the inputs.
    # Since we defined 14 graph cards in the layout, we should return 14 style dicts.
    # But to be safe and dynamic, we can construct the style based on the theme.
    
    base_card_style = {'display': 'inline-block', 'verticalAlign': 'top', 'margin': '10px', 'borderRadius': '8px', 'padding': '10px', 'backgroundColor': theme['card_bg'], 'boxShadow': theme['shadow'], 'transition': 'background-color 0.3s'}
    
    # We know we have 14 graphs. But 'current_card_styles' will tell us how many exist in the DOM.
    # If it's the first callback, they might exist.
    num_cards = len(current_card_styles) if current_card_styles else 14
    
    # We need to preserve the 'width' from the original style if possible, or just re-apply the theme parts.
    # Actually, it's safer to just update the theme-related properties and keep the layout properties.
    # But 'current_card_styles' comes from State, so it has the current values.
    
    new_card_styles = []
    if current_card_styles:
        for style in current_card_styles:
            # Create a new dict to avoid mutating the state directly
            new_style = style.copy() if style else {}
            new_style.update({
                'backgroundColor': theme['card_bg'],
                'boxShadow': theme['shadow']
            })
            new_card_styles.append(new_style)
    else:
        # Fallback if state is empty (initial load might be tricky with ALL)
        # We will just return a list of 14 default styles, but we lose the custom widths.
        # Ideally, we should define the width in the layout and NOT overwrite it here.
        # If we update 'style', we overwrite everything unless we merge.
        # Since we can't easily merge with 'ALL' output without State, using State is the right way.
        # If State is empty, we might be in trouble. 
        # Let's assume State is populated because the components exist in the layout.
        new_card_styles = [base_card_style] * 14

    if not forecast_data or not hourly_data or not grid_data:
        # Return empty/hidden content if no data
        return main_style, controls_style, downloads_style, {'display': 'none'}, \
               t_style, t_sel_style, t_style, t_sel_style, t_style, t_sel_style, t_style, t_sel_style, t_style, t_sel_style, \
               [], new_card_styles, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}

    # Process Data
    hourly_df = process_hourly(hourly_data)
    grid_props = grid_data['properties']
    
    # --- 1. Grid KPIs ---
    kpi_params = [
        ('Temperature', 'temperature'),
        ('Dewpoint', 'dewpoint'),
        ('Max Temp', 'maxTemperature'),
        ('Min Temp', 'minTemperature'),
        ('Humidity', 'relativeHumidity'),
        ('Apparent Temp', 'apparentTemperature'),
        ('Heat Index', 'heatIndex'),
        ('Wind Chill', 'windChill'),
        ('Sky Cover', 'skyCover'),
        ('Wind Direction', 'windDirection'),
        ('Wind Speed', 'windSpeed'),
        ('Wind Gust', 'windGust')
    ]
    
    kpi_cards = []
    for label, param in kpi_params:
        val, unit = get_current_grid_value(grid_data, param)
        if isinstance(val, (int, float)):
            val = round(val, 1)
        kpi_cards.append(create_kpi_card(label, val, unit, theme))
        
    # --- Helper for Graphs ---
    def create_fig(fig_obj):
        fig_obj.update_layout(
            template=theme['plotly_template'], 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=40, r=20, t=40, b=40)
        )
        return fig_obj

    # --- 2. 24h Graphs ---
    now = datetime.now(timezone.utc)
    df_24h = hourly_df[hourly_df['startTime'] >= now].head(24)
    
    fig_24h_temp = create_fig(px.line(df_24h, x='startTime', y='temperature', title="Temperature (Next 24h)", markers=True))
    
    df_24h['wind_speed_val'] = df_24h['windSpeed'].str.extract(r'(\d+)').astype(float)
    fig_24h_wind = create_fig(px.line(df_24h, x='startTime', y='wind_speed_val', title="Wind Speed (Next 24h)", markers=True))
    
    df_24h['pop_val'] = df_24h['probabilityOfPrecipitation'].apply(lambda x: x['value'] if x else 0)
    fig_24h_pop = create_fig(px.bar(df_24h, x='startTime', y='pop_val', title="Precipitation Probability (Next 24h)"))

    # --- 3. Full Graphs ---
    fig_temp = create_fig(px.line(hourly_df, x='startTime', y='temperature', title="Hourly Temperature (°F)"))
    
    hourly_df['wind_speed_val'] = hourly_df['windSpeed'].str.extract(r'(\d+)').astype(float)
    fig_wind = create_fig(px.line(hourly_df, x='startTime', y='wind_speed_val', title="Wind Speed (mph)"))
    
    hourly_df['dewpoint_val'] = hourly_df['dewpoint'].apply(lambda x: x['value'] if x else None)
    hourly_df['dewpoint_f'] = (hourly_df['dewpoint_val'] * 9/5) + 32
    fig_dew = create_fig(px.line(hourly_df, x='startTime', y='dewpoint_f', title="Dewpoint (°F)"))
    
    hourly_df['humidity_val'] = hourly_df['relativeHumidity'].apply(lambda x: x['value'] if x else None)
    fig_hum = create_fig(px.area(hourly_df, x='startTime', y='humidity_val', title="Relative Humidity (%)"))
    
    hourly_df['pop_val'] = hourly_df['probabilityOfPrecipitation'].apply(lambda x: x['value'] if x else 0)
    fig_pop = create_fig(px.bar(hourly_df, x='startTime', y='pop_val', title="Precipitation Probability (%)"))
    
    sky_data = [{'time': i['validTime'].split('/')[0], 'value': i['value']} for i in grid_props.get('skyCover', {}).get('values', [])]
    df_sky = pd.DataFrame(sky_data)
    fig_sky = create_fig(px.area(df_sky, x='time', y='value', title="Sky Cover (%)") if not df_sky.empty else {})

    qpf_data = [{'time': i['validTime'].split('/')[0], 'value': i['value']} for i in grid_props.get('quantitativePrecipitation', {}).get('values', [])]
    df_qpf = pd.DataFrame(qpf_data)
    fig_qpf = create_fig(px.bar(df_qpf, x='time', y='value', title="Quantitative Precipitation (mm)") if not df_qpf.empty else {})
    
    thunder_data = [{'time': i['validTime'].split('/')[0], 'value': i['value']} for i in grid_props.get('probabilityOfThunder', {}).get('values', [])]
    df_thunder = pd.DataFrame(thunder_data)
    if not df_thunder.empty:
        cat_map = {0: "None (<15%)", 1: "Slight (15-24%)", 2: "Chance (25-54%)", 3: "Likely (55-74%)", 4: "Definite (≥75%)"}
        df_thunder['category'] = df_thunder['value'].map(cat_map)
        fig_thunder = create_fig(px.bar(df_thunder, x='time', y='value', color='category', title="Thunderstorm Probability"))
    else:
        fig_thunder = {}
    
    gust_data = [{'time': i['validTime'].split('/')[0], 'value': i['value']} for i in grid_props.get('windGust', {}).get('values', [])]
    df_gust = pd.DataFrame(gust_data)
    fig_gust = create_fig(px.line(df_gust, x='time', y='value', title="Wind Gust (Grid Data)") if not df_gust.empty else {})
    
    at_data = [{'time': i['validTime'].split('/')[0], 'value': i['value']} for i in grid_props.get('apparentTemperature', {}).get('values', [])]
    df_at = pd.DataFrame(at_data)
    if not df_at.empty:
        df_at['value_f'] = (df_at['value'] * 9/5) + 32
        fig_app_temp = create_fig(px.line(df_at, x='time', y='value_f', title="Apparent Temperature (°F)"))
    else:
        fig_app_temp = {}

    # --- 4. Hazards (Timeline) ---
    hazards_vals = grid_props.get('hazards', {}).get('values', [])
    if hazards_vals:
        hazard_data = []
        for item in hazards_vals:
            time_str, duration_str = item['validTime'].split('/')
            start = datetime.fromisoformat(time_str)
            duration = isodate.parse_duration(duration_str)
            end = start + duration
            
            vals_list = item['value']
            for val in vals_list:
                label = f"{val.get('phenomenon', 'Unknown')} ({val.get('significance', '')})"
                hazard_data.append({
                    'Start': start,
                    'End': end,
                    'Hazard': label,
                    'Details': f"Event #{val.get('event_number')}"
                })
            
        df_hazards = pd.DataFrame(hazard_data)
        
        if not df_hazards.empty:
            fig_hazards = create_fig(px.timeline(df_hazards, x_start="Start", x_end="End", y="Hazard", color="Hazard", title="Active Weather Hazards"))
            fig_hazards.update_yaxes(autorange="reversed")
        else:
            fig_hazards = create_fig(go.Figure())
            fig_hazards.update_layout(
                xaxis={'visible': False}, yaxis={'visible': False},
                annotations=[{'text': "No Active Hazards Found", 'xref': "paper", 'yref': "paper", 'showarrow': False, 'font': {'size': 20, 'color': theme['text']}}]
            )
    else:
        fig_hazards = create_fig(go.Figure())
        fig_hazards.update_layout(
            xaxis={'visible': False}, yaxis={'visible': False},
            annotations=[{'text': "No Active Hazards Found", 'xref': "paper", 'yref': "paper", 'showarrow': False, 'font': {'size': 20, 'color': theme['text']}}]
        )

    return main_style, controls_style, downloads_style, {'display': 'block'}, \
           t_style, t_sel_style, t_style, t_sel_style, t_style, t_sel_style, t_style, t_sel_style, t_style, t_sel_style, \
           kpi_cards, new_card_styles, \
           fig_24h_temp, fig_24h_wind, fig_24h_pop, \
           fig_temp, fig_wind, fig_dew, fig_hum, fig_pop, fig_sky, fig_qpf, fig_thunder, fig_gust, fig_app_temp, fig_hazards

# --- Download Callbacks ---
@callback(
    Output("download-daily", "data"),
    Input("btn-download-daily", "n_clicks"),
    State("store-forecast", "data"),
    prevent_initial_call=True,
)
def download_daily(n_clicks, data):
    if not data: return None
    df = pd.DataFrame(data['properties']['periods'])
    return dcc.send_data_frame(df.to_csv, "daily_forecast.csv")

@callback(
    Output("download-hourly", "data"),
    Input("btn-download-hourly", "n_clicks"),
    State("store-hourly", "data"),
    prevent_initial_call=True,
)
def download_hourly(n_clicks, data):
    if not data: return None
    df = pd.DataFrame(data['properties']['periods'])
    return dcc.send_data_frame(df.to_csv, "hourly_forecast.csv")

@callback(
    Output("download-grid", "data"),
    Input("btn-download-grid", "n_clicks"),
    State("store-grid", "data"),
    prevent_initial_call=True,
)
def download_grid(n_clicks, data):
    if not data: return None
    props = data['properties']
    export = []
    for key in ['temperature', 'dewpoint', 'relativeHumidity', 'windSpeed', 'windGust', 'skyCover', 'probabilityOfPrecipitation', 'probabilityOfThunder']:
        vals = props.get(key, {}).get('values', [])
        for v in vals:
            export.append({"metric": key, "validTime": v['validTime'], "value": v['value']})
    df = pd.DataFrame(export)
    return dcc.send_data_frame(df.to_csv, "detailed_grid_metrics.csv")

# --- Chatbot Callback ---
@callback(
    [Output('chat-messages', 'children'),
     Output('chat-history', 'data'),
     Output('chat-input', 'value')],
    [Input('chat-send-btn', 'n_clicks'),
     Input('chat-input', 'n_submit')],
    [State('chat-input', 'value'),
     State('lat-input', 'value'),
     State('lon-input', 'value'),
     State('chat-history', 'data')],
    prevent_initial_call=True
)
def handle_chat(n_clicks, n_submit, message, lat_val, lon_val, history):
    if not message:
        return dash.no_update, dash.no_update, dash.no_update
    
    if history is None:
        history = []
        
    # Append User Message
    history.append({'role': 'user', 'content': message})
    
    # Process Response
    if not llm_service:
        response_text = "Error: Gemini API Key is missing."
    else:
        try:
            # Use current lat/lon from dashboard inputs
            lat, lon = float(lat_val), float(lon_val)
            
            # 1. Fetch Weather Data (Using same service as standalone bot)
            weather_data = weather_service.get_weather_data(lat, lon)
            
            if "error" in weather_data:
                response_text = f"Error fetching data: {weather_data['error']}"
            else:
                # 2. Build Context
                current = weather_service.get_current_conditions(weather_data['grid'])
                forecast = weather_service.get_forecast_summary(weather_data['forecast'])
                hazards = weather_service.get_hazards(weather_data['grid'])
                
                context = f"{current}\n\n{forecast}\n\n{hazards}"
                
                # 3. Generate LLM Response
                response_text = llm_service.generate_response(message, context)
                
        except Exception as e:
            response_text = f"Error: {str(e)}"
            
    # Append Assistant Response
    history.append({'role': 'assistant', 'content': response_text})
    
    # Re-render messages
    bubbles = [create_message_bubble(msg['role'], msg['content']) for msg in history]
    
    return bubbles, history, ""


if __name__ == '__main__':
    app.run(debug=True)

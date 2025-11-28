from dash import html, dcc

def create_chat_layout():
    return html.Div([
        html.H3("🌤️ Weather Assistant", style={'textAlign': 'center', 'color': '#333', 'marginBottom': '20px'}),
        
        # Location Input
        html.Div([
            html.Label("Location (Lat, Lon):", style={'fontWeight': 'bold', 'marginRight': '10px'}),
            dcc.Input(
                id='chat-location',
                type='text',
                value='39.0997,-94.5786', # Default to Kansas City
                placeholder='e.g., 39.0997,-94.5786',
                style={'width': '250px', 'padding': '5px', 'borderRadius': '5px', 'border': '1px solid #ccc'}
            )
        ], style={'marginBottom': '20px', 'textAlign': 'center'}),
        
        # Chat Container
        html.Div(
            id='chat-messages',
            style={
                'height': '500px',
                'overflowY': 'auto',
                'border': '1px solid #e0e0e0',
                'borderRadius': '10px',
                'padding': '20px',
                'marginBottom': '20px',
                'backgroundColor': '#f9f9f9',
                'display': 'flex',
                'flexDirection': 'column',
                'gap': '10px'
            }
        ),
        
        # Input Area
        html.Div([
            dcc.Input(
                id='chat-input',
                type='text',
                placeholder='Ask about the weather (e.g., "What is the temperature?", "Any hazards?")',
                style={
                    'flex': '1',
                    'padding': '10px',
                    'borderRadius': '5px',
                    'border': '1px solid #ccc',
                    'marginRight': '10px'
                }
            ),
            html.Button(
                'Send', 
                id='chat-send-btn', 
                n_clicks=0,
                style={
                    'padding': '10px 20px',
                    'backgroundColor': '#007bff',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '5px',
                    'cursor': 'pointer',
                    'fontWeight': 'bold'
                }
            )
        ], style={'display': 'flex', 'alignItems': 'center'}),
        
        # Store for history
        dcc.Store(id='chat-history', data=[]),
        
        # Loading State
        dcc.Loading(id="loading-chat", type="dot", children=html.Div(id="dummy-output"))
        
    ], style={
        'maxWidth': '800px', 
        'margin': '0 auto', 
        'padding': '20px', 
        'fontFamily': 'sans-serif',
        'backgroundColor': 'white',
        'borderRadius': '15px',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.1)'
    })

def create_message_bubble(role, content):
    is_user = role == 'user'
    return html.Div([
        html.Div([
            html.Strong("You" if is_user else "Assistant", style={'display': 'block', 'marginBottom': '5px', 'fontSize': '0.8em', 'opacity': 0.7}),
            html.Span(content)
        ], style={
            'backgroundColor': '#007bff' if is_user else '#e9ecef',
            'color': 'white' if is_user else '#333',
            'padding': '10px 15px',
            'borderRadius': '15px',
            'borderBottomRightRadius': '5px' if is_user else '15px',
            'borderBottomLeftRadius': '15px' if is_user else '5px',
            'maxWidth': '70%',
            'boxShadow': '0 1px 2px rgba(0,0,0,0.1)'
        })
    ], style={
        'display': 'flex', 
        'justifyContent': 'flex-end' if is_user else 'flex-start',
        'marginBottom': '10px'
    })

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
from typing import Dict, List, Any
import hashlib
import time

# Page configuration
st.set_page_config(
    page_title="Weather Alert Dashboard",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="auto"
)

# ===========================
# AUTHENTICATION SYSTEM
# ===========================

# Dummy user database with hashed passwords
# In production, use a proper database and authentication system
USERS_DB = {
    "john.doe@weather.com": {
        "password": hashlib.sha256("password123".encode()).hexdigest(),
        "name": "John Doe",
        "default_state": "CA",  # California
        "role": "Meteorologist"
    },
    "jane.smith@weather.com": {
        "password": hashlib.sha256("password456".encode()).hexdigest(),
        "name": "Jane Smith",
        "default_state": "TX",  # Texas
        "role": "Weather Analyst"
    }
}

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_login(email: str, password: str) -> bool:
    """Verify user credentials"""
    if email in USERS_DB:
        hashed_password = hash_password(password)
        return USERS_DB[email]["password"] == hashed_password
    return False

def get_user_info(email: str) -> Dict:
    """Get user information"""
    return USERS_DB.get(email, None)

def login_page():
    """Display clean login page with loading animation"""
    
    # Hide Streamlit default elements and prevent scrolling
    st.markdown("""
    <style>
        /* Hide Streamlit branding and menu */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Prevent scrolling */
        .main .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
            max-height: 100vh;
            overflow: hidden;
        }
        
        /* Full height login page */
        .stApp {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            overflow: hidden;
        }
        
        /* Header styling */
        .login-header {
            text-align: center;
            color: #ffffff;
            margin-bottom: 15px;
            font-size: 2.5rem;
            font-weight: 700;
        }
        
        .login-subheader {
            text-align: center;
            color: #a0a0a0;
            margin-bottom: 40px;
            font-size: 1.1rem;
        }
        
        /* Input fields */
        .stTextInput > div > div > input {
            background-color: #2d2d44;
            border: 1px solid #3d3d5c;
            color: #ffffff;
            border-radius: 8px;
            padding: 12px;
            font-size: 1rem;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #4a9eff;
            box-shadow: 0 0 0 2px rgba(74, 158, 255, 0.2);
        }
        
        /* Labels */
        .stTextInput > label {
            color: #ffffff !important;
            font-weight: 500;
            font-size: 0.95rem;
        }
        
        /* Login button */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 14px;
            font-size: 1.1rem;
            font-weight: 600;
            width: 100%;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }
        
        /* Remove default streamlit padding */
        .css-1d391kg, .css-12oz5g7 {
            padding: 0;
        }
        
        /* Remove form border/background */
        .stForm {
            border: none;
            background-color: transparent;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Header
        st.markdown('''
        <div class="login-header">🌤️ Weather Alert<br/>Dashboard</div>
        <div class="login-subheader">Please Login</div>
        ''', unsafe_allow_html=True)
        
        # Login form
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("Email", placeholder="Enter your email", key="email_input")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="password_input")
            submit = st.form_submit_button("🔐 Login", use_container_width=True)
            
            if submit:
                if email and password:
                    # Show loading animation
                    progress_bar = st.progress(0)
                    
                    for i in range(100):
                        progress_bar.progress(i + 1)
                        time.sleep(0.010)
                    
                    # Verify credentials
                    if verify_login(email, password):
                        user_info = get_user_info(email)
                        st.session_state.logged_in = True
                        st.session_state.user_email = email
                        st.session_state.user_name = user_info["name"]
                        st.session_state.user_role = user_info["role"]
                        st.session_state.default_state = user_info["default_state"]
                        st.session_state.show_welcome = True
                        st.rerun()
                    else:
                        st.error("❌ Invalid email or password")
                else:
                    st.warning("⚠️ Please enter both email and password")

def logout():
    """Clear session state and logout"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

def check_authentication():
    """Check if user is authenticated"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        login_page()
        st.stop()

# ===========================
# END AUTHENTICATION SYSTEM
# ===========================

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        background-color: #f5f7fa;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .alert-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .severity-extreme {
        border-left: 5px solid #d60000;
    }
    .severity-severe {
        border-left: 5px solid #ff8c00;
    }
    .severity-moderate {
        border-left: 5px solid #ffd700;
    }
    .severity-minor {
        border-left: 5px solid #00ff00;
    }
    .severity-unknown {
        border-left: 5px solid #cccccc;
    }
</style>
""", unsafe_allow_html=True)

# US States and Territories data
US_STATES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming", "DC": "District of Columbia",
    "AS": "American Samoa", "GU": "Guam", "MP": "Northern Mariana Islands",
    "PR": "Puerto Rico", "VI": "Virgin Islands"
}

# Severity color mapping
SEVERITY_COLORS = {
    "Extreme": "#d60000",
    "Severe": "#ff8c00",
    "Moderate": "#ffd700",
    "Minor": "#90EE90",
    "Unknown": "#cccccc"
}

# Urgency color mapping
URGENCY_COLORS = {
    "Immediate": "#d60000",
    "Expected": "#ff8c00",
    "Future": "#4169e1",
    "Past": "#808080",
    "Unknown": "#cccccc"
}

# Certainty color mapping
CERTAINTY_COLORS = {
    "Observed": "#006400",
    "Likely": "#32CD32",
    "Possible": "#FFD700",
    "Unlikely": "#FFA500",
    "Unknown": "#cccccc"
}


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_alert_count() -> Dict[str, Any]:
    """Fetch active alert count from NWS API"""
    try:
        url = "https://api.weather.gov/alerts/active/count"
        headers = {
            'User-Agent': '(WeatherAlertDashboard, contact@example.com)',
            'Accept': 'application/json'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching alert count: {str(e)}")
        return {}


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_state_alerts(state_code: str) -> Dict[str, Any]:
    """Fetch alerts for a specific state"""
    try:
        url = f"https://api.weather.gov/alerts/active/area/{state_code}"
        headers = {
            'User-Agent': '(WeatherAlertDashboard, contact@example.com)',
            'Accept': 'application/geo+json'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching alerts for {state_code}: {str(e)}")
        return {}


def categorize_alerts(alerts: List[Dict]) -> Dict[str, Any]:
    """Categorize alerts by severity, urgency, certainty, and event type"""
    categorized = {
        'severity': {'Extreme': [], 'Severe': [], 'Moderate': [], 'Minor': [], 'Unknown': []},
        'urgency': {'Immediate': [], 'Expected': [], 'Future': [], 'Past': [], 'Unknown': []},
        'certainty': {'Observed': [], 'Likely': [], 'Possible': [], 'Unlikely': [], 'Unknown': []},
        'event_type': {}
    }
    
    for alert in alerts:
        props = alert.get('properties', {})
        
        # Categorize by severity
        severity = props.get('severity', 'Unknown')
        if severity in categorized['severity']:
            categorized['severity'][severity].append(alert)
        else:
            categorized['severity']['Unknown'].append(alert)
        
        # Categorize by urgency
        urgency = props.get('urgency', 'Unknown')
        if urgency in categorized['urgency']:
            categorized['urgency'][urgency].append(alert)
        else:
            categorized['urgency']['Unknown'].append(alert)
        
        # Categorize by certainty
        certainty = props.get('certainty', 'Unknown')
        if certainty in categorized['certainty']:
            categorized['certainty'][certainty].append(alert)
        else:
            categorized['certainty']['Unknown'].append(alert)
        
        # Categorize by event type
        event_type = props.get('event', 'Unknown')
        if event_type not in categorized['event_type']:
            categorized['event_type'][event_type] = []
        categorized['event_type'][event_type].append(alert)
    
    return categorized


def create_severity_chart(categorized: Dict) -> go.Figure:
    """Create a bar chart for severity distribution"""
    severity_counts = {k: len(v) for k, v in categorized['severity'].items() if len(v) > 0}
    
    if not severity_counts:
        return None
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(severity_counts.keys()),
            y=list(severity_counts.values()),
            marker_color=[SEVERITY_COLORS.get(k, '#cccccc') for k in severity_counts.keys()],
            text=list(severity_counts.values()),
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Alerts by Severity",
        xaxis_title="Severity Level",
        yaxis_title="Number of Alerts",
        template="plotly_white",
        height=400
    )
    
    return fig


def create_urgency_chart(categorized: Dict) -> go.Figure:
    """Create a pie chart for urgency distribution"""
    urgency_counts = {k: len(v) for k, v in categorized['urgency'].items() if len(v) > 0}
    
    if not urgency_counts:
        return None
    
    fig = go.Figure(data=[
        go.Pie(
            labels=list(urgency_counts.keys()),
            values=list(urgency_counts.values()),
            marker=dict(colors=[URGENCY_COLORS.get(k, '#cccccc') for k in urgency_counts.keys()]),
            hole=0.3
        )
    ])
    
    fig.update_layout(
        title="Alerts by Urgency",
        template="plotly_white",
        height=400
    )
    
    return fig


def create_certainty_chart(categorized: Dict) -> go.Figure:
    """Create a horizontal bar chart for certainty distribution"""
    certainty_counts = {k: len(v) for k, v in categorized['certainty'].items() if len(v) > 0}
    
    if not certainty_counts:
        return None
    
    fig = go.Figure(data=[
        go.Bar(
            y=list(certainty_counts.keys()),
            x=list(certainty_counts.values()),
            orientation='h',
            marker_color=[CERTAINTY_COLORS.get(k, '#cccccc') for k in certainty_counts.keys()],
            text=list(certainty_counts.values()),
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Alerts by Certainty",
        xaxis_title="Number of Alerts",
        yaxis_title="Certainty Level",
        template="plotly_white",
        height=400
    )
    
    return fig


def create_event_type_chart(categorized: Dict) -> go.Figure:
    """Create a treemap for event types"""
    event_counts = {k: len(v) for k, v in categorized['event_type'].items() if len(v) > 0}
    
    if not event_counts:
        return None
    
    # Sort by count and take top 15
    sorted_events = dict(sorted(event_counts.items(), key=lambda x: x[1], reverse=True)[:15])
    
    fig = go.Figure(go.Treemap(
        labels=list(sorted_events.keys()),
        parents=[""] * len(sorted_events),
        values=list(sorted_events.values()),
        textinfo="label+value",
        marker=dict(colorscale='RdYlGn_r', cmid=max(sorted_events.values())/2)
    ))
    
    fig.update_layout(
        title="Top 15 Alert Event Types",
        template="plotly_white",
        height=500
    )
    
    return fig


def create_national_overview_chart(alert_count_data: Dict) -> go.Figure:
    """Create a bar chart showing alerts by state"""
    areas = alert_count_data.get('areas', {})
    
    if not areas:
        return None
    
    # Filter out marine zones and keep only state codes
    state_counts = {k: v for k, v in areas.items() if k in US_STATES}
    
    # Sort by count
    sorted_states = dict(sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:20])
    
    state_names = [f"{k} - {US_STATES[k]}" for k in sorted_states.keys()]
    
    fig = go.Figure(data=[
        go.Bar(
            x=state_names,
            y=list(sorted_states.values()),
            marker_color='#1f77b4',
            text=list(sorted_states.values()),
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Top 20 States with Active Alerts",
        xaxis_title="State",
        yaxis_title="Number of Alerts",
        template="plotly_white",
        height=500,
        xaxis_tickangle=-45
    )
    
    return fig





def display_alert_card(alert: Dict, index: int):
    """Display a single alert card"""
    props = alert.get('properties', {})
    
    severity = props.get('severity', 'Unknown')
    event = props.get('event', 'Unknown Event')
    headline = props.get('headline', 'No headline available')
    area_desc = props.get('areaDesc', 'Unknown Area')
    urgency = props.get('urgency', 'Unknown')
    certainty = props.get('certainty', 'Unknown')
    effective = props.get('effective', '')
    expires = props.get('expires', '')
    description = props.get('description', 'No description available')
    instruction = props.get('instruction', '')
    
    # Format dates
    try:
        effective_dt = datetime.fromisoformat(effective.replace('Z', '+00:00'))
        effective_str = effective_dt.strftime('%B %d, %Y at %I:%M %p')
    except:
        effective_str = effective
    
    try:
        expires_dt = datetime.fromisoformat(expires.replace('Z', '+00:00'))
        expires_str = expires_dt.strftime('%B %d, %Y at %I:%M %p')
    except:
        expires_str = expires
    
    # Determine severity class
    severity_class = f"severity-{severity.lower()}"
    
    with st.expander(f"🚨 {event} - {area_desc}", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Severity", severity)
        with col2:
            st.metric("Urgency", urgency)
        with col3:
            st.metric("Certainty", certainty)
        
        st.markdown(f"**Headline:** {headline}")
        st.markdown(f"**Area:** {area_desc}")
        st.markdown(f"**Effective:** {effective_str}")
        st.markdown(f"**Expires:** {expires_str}")
        
        st.markdown("---")
        st.markdown("**Description:**")
        st.write(description)
        
        if instruction:
            st.markdown("---")
            st.markdown("**Instructions:**")
            st.info(instruction)


def main():
    # Check authentication first
    check_authentication()
    
    # Show welcome alert after login
    if 'show_welcome' in st.session_state and st.session_state.show_welcome:
        st.success(f"✅ Logged in as **{st.session_state.user_name}** ({st.session_state.user_role})")
        st.session_state.show_welcome = False
    
    # Header with user info
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🌤️ Weather Alert Dashboard")
        st.markdown("Real-time weather alerts from the National Weather Service")
    with col2:
        st.markdown(f"""
        <div style="text-align: right; padding: 10px;">
            <strong>👤 {st.session_state.user_name}</strong><br>
            <small>{st.session_state.user_role}</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        # User profile section
        st.markdown(f"""
        <div style="background-color: #f0f8ff; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
            <h3 style="margin: 0; color: #1f77b4;">👤 Profile</h3>
            <hr style="margin: 10px 0;">
            <p style="margin: 5px 0;"><strong>Name:</strong> {st.session_state.user_name}</p>
            <p style="margin: 5px 0;"><strong>Role:</strong> {st.session_state.user_role}</p>
            <p style="margin: 5px 0;"><strong>Email:</strong> {st.session_state.user_email}</p>
            <p style="margin: 5px 0;"><strong>Default Location:</strong> {US_STATES[st.session_state.default_state]}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            logout()
        
        st.markdown("---")
        
        st.header("Settings")
        
        # State selection with user's default state
        state_options = [f"{code} - {name}" for code, name in sorted(US_STATES.items(), key=lambda x: x[1])]
        
        # Find the index of user's default state
        default_state_display = f"{st.session_state.default_state} - {US_STATES[st.session_state.default_state]}"
        default_index = state_options.index(default_state_display)
        
        # Show info about default state
        st.info(f"🏠 Your default location: **{US_STATES[st.session_state.default_state]}**")
        
        selected_state_display = st.selectbox(
            "Select State/Territory",
            options=state_options,
            index=default_index,
            help="Your default location is pre-selected based on your profile"
        )
        
        # Extract state code
        selected_state = selected_state_display.split(" - ")[0]
        
        # Show if viewing different state
        if selected_state != st.session_state.default_state:
            st.warning(f"📍 Currently viewing: **{US_STATES[selected_state]}**")
        
        st.markdown("---")
        
        # Set default filters (not shown to user)
        severity_filter = ["Extreme", "Severe", "Moderate", "Minor", "Unknown"]
        urgency_filter = ["Immediate", "Expected", "Future", "Past", "Unknown"]
        
        st.markdown("---")
        
        # Refresh button
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        st.caption("Data updates every 5 minutes")
        st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Main content
    with st.spinner("Loading alert data..."):
        # Fetch national alert count
        alert_count_data = fetch_alert_count()
        
        # Display national statistics
        if alert_count_data:
            st.header("📊 National Overview")
            
            col1, col2, col3, col4 = st.columns(4)
            
            total_alerts = alert_count_data.get('total', 0)
            land_alerts = alert_count_data.get('land', 0)
            marine_alerts = alert_count_data.get('marine', 0)
            
            # Count states with alerts
            areas = alert_count_data.get('areas', {})
            states_with_alerts = len([k for k in areas.keys() if k in US_STATES and areas[k] > 0])
            
            with col1:
                st.metric("Total Active Alerts", f"{total_alerts:,}")
            with col2:
                st.metric("Land Alerts", f"{land_alerts:,}")
            with col3:
                st.metric("Marine Alerts", f"{marine_alerts:,}")
            with col4:
                st.metric("States Affected", states_with_alerts)
            
            # National overview chart
            national_chart = create_national_overview_chart(alert_count_data)
            if national_chart:
                st.plotly_chart(national_chart, use_container_width=True)
        
        st.markdown("---")
        
        # Fetch state-specific alerts
        st.header(f"🗺️ Alerts for {US_STATES[selected_state]}")
        
        state_data = fetch_state_alerts(selected_state)
        
        if state_data and 'features' in state_data:
            alerts = state_data['features']
            
            if len(alerts) == 0:
                st.success(f"✅ No active alerts for {US_STATES[selected_state]}")
            else:
                # Display alert count
                st.info(f"**{len(alerts)} active alert(s) found**")
                
                # Categorize alerts
                categorized = categorize_alerts(alerts)
                
                # Filter alerts based on user selection
                filtered_alerts = []
                for alert in alerts:
                    props = alert.get('properties', {})
                    severity = props.get('severity', 'Unknown')
                    urgency = props.get('urgency', 'Unknown')
                    
                    if severity in severity_filter and urgency in urgency_filter:
                        filtered_alerts.append(alert)
                
                st.info(f"**{len(filtered_alerts)} alert(s) after applying filters**")
                
                if len(filtered_alerts) > 0:
                    # Re-categorize filtered alerts
                    categorized = categorize_alerts(filtered_alerts)
                    
                    # Display charts
                    st.subheader("📈 Alert Distribution")
                    
                    chart_col1, chart_col2 = st.columns(2)
                    
                    with chart_col1:
                        severity_chart = create_severity_chart(categorized)
                        if severity_chart:
                            st.plotly_chart(severity_chart, use_container_width=True)
                        
                        certainty_chart = create_certainty_chart(categorized)
                        if certainty_chart:
                            st.plotly_chart(certainty_chart, use_container_width=True)
                    
                    with chart_col2:
                        urgency_chart = create_urgency_chart(categorized)
                        if urgency_chart:
                            st.plotly_chart(urgency_chart, use_container_width=True)
                    
                    # Event type treemap
                    event_chart = create_event_type_chart(categorized)
                    if event_chart:
                        st.plotly_chart(event_chart, use_container_width=True)
                    
                    st.markdown("---")
                    
                    # Display alerts by severity
                    st.subheader("🚨 Alert Details")
                    
                    # Sort alerts by severity priority
                    severity_priority = {"Extreme": 0, "Severe": 1, "Moderate": 2, "Minor": 3, "Unknown": 4}
                    sorted_alerts = sorted(
                        filtered_alerts,
                        key=lambda x: severity_priority.get(x.get('properties', {}).get('severity', 'Unknown'), 4)
                    )
                    
                    # Display alerts
                    for idx, alert in enumerate(sorted_alerts):
                        display_alert_card(alert, idx)
                    
                    st.markdown("---")
                    
                    # Export options
                    st.subheader("💾 Export Data")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Export as JSON
                        json_data = json.dumps(state_data, indent=2)
                        st.download_button(
                            label="📥 Download as JSON",
                            data=json_data,
                            file_name=f"alerts_{selected_state}_{datetime.now().strftime('%Y%m%d')}.json",
                            mime="application/json",
                            use_container_width=True
                        )
                    
                    with col2:
                        # Export as CSV
                        df_data = []
                        for alert in filtered_alerts:
                            props = alert.get('properties', {})
                            df_data.append({
                                'Event': props.get('event', ''),
                                'Severity': props.get('severity', ''),
                                'Urgency': props.get('urgency', ''),
                                'Certainty': props.get('certainty', ''),
                                'Area': props.get('areaDesc', ''),
                                'Effective': props.get('effective', ''),
                                'Expires': props.get('expires', ''),
                                'Headline': props.get('headline', '')
                            })
                        
                        df = pd.DataFrame(df_data)
                        csv_data = df.to_csv(index=False)
                        
                        st.download_button(
                            label="📥 Download as CSV",
                            data=csv_data,
                            file_name=f"alerts_{selected_state}_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                else:
                    st.warning("No alerts match the selected filters.")
        else:
            st.error(f"Unable to fetch alerts for {US_STATES[selected_state]}")
    
    # Footer
    st.markdown("---")
    st.caption("Data source: National Weather Service (NWS) API")
    # st.caption("⚠️ This is for informational purposes only. Always follow official emergency instructions.")
    
    # Chatbot removed


if __name__ == "__main__":
    main()
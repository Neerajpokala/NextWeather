import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
NWS_USER_AGENT = os.getenv('NWS_USER_AGENT', '(nextweather-chatbot, contact@example.com)')

# App Config
DEBUG = True
PORT = 8051  # Different port than main dashboard

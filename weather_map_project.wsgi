import sys
import os

# Add your project directory to the sys.path
sys.path.insert(0, '/home/hoho72fo/public_html/weather_map_project')

# Load environment variables if needed
from dotenv import load_dotenv
load_dotenv('/home/hoho72fo/public_html/weather_map_project/.env')

# Set the Flask app object as 'application' for WSGI
from app import app as application

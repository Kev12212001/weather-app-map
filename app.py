from flask import Flask, send_file, render_template
from flask_sqlalchemy import SQLAlchemy
import io
import requests
import os
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import matplotlib.patches as patches
import matplotlib.image as mpimg
from concurrent.futures import ThreadPoolExecutor  # <-- Import ThreadPoolExecutor
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from datetime import datetime
from dotenv import load_dotenv
import pytz

load_dotenv()
app = Flask(__name__)
app.config['ENV'] = 'production'  # Optional, for additional clarity
app.config['DEBUG'] = False       # Ensure debugging is off
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db = SQLAlchemy(app)
# Your API key for the weather data
API_KEY = '6e1f7ca9bda347cdb5a5b9259a0bafc9'

# Define locations (simplified for example)
locations = {
    "Chicago": {"lat": 41.8781, "lon": -87.6298},
    "Oak Park": {"lat": 41.8807, "lon": -87.7840},
    "Cicero": {"lat": 41.8369, "lon": -87.7461},
    "La Grange": {"lat": 41.8190, "lon": -87.8680},
    "Elmhurst": {"lat": 41.8990, "lon": -87.9403},
    "Oak Brook": {"lat": 41.8506, "lon": -87.9515},
    "Skokie": {"lat": 42.0334, "lon": -87.7420},
    "Downers Grove": {"lat": 41.8080, "lon": -88.0113},
    "Des Plaines": {"lat": 42.0334, "lon": -87.8835},
    "Arlington Heights": {"lat": 42.0394, "lon": -87.9606},
    "Park Ridge": {"lat": 42.0116, "lon": -87.8237},
    "Elmwood Park": {"lat": 41.9239, "lon": -87.7839},
    "Schaumburg": {"lat": 42.0334, "lon": -88.0534},
    "O'Hare Airport": {"lat": 41.978611, "lon": -87.904724},
    "Midway Airport": {"lat": 41.78, "lon": -87.76},
    "Addison": {"lat": 41.9295, "lon": -88.0037},
    "Lombard": {"lat": 41.8850, "lon": -88.0086},
    "Franklin Park": {"lat": 41.9296, "lon": -87.8697},
    "Lincoln Park": {"lat": 41.9216, "lon": -87.6455},
    "Bridgeport": {"lat": 41.8319, "lon": -87.6643},
    "Oak Lawn": {"lat": 41.7161, "lon": -87.7467},
    "Dalton": {"lat": 41.6199, "lon": -87.6226},
    "Roseland": {"lat": 41.7010, "lon": -87.6087},
    "Darien": {"lat": 41.7463, "lon": -87.9965},
    "Burr Ridge": {"lat": 41.7520, "lon": -87.9401},
    "Willow Springs": {"lat": 41.7100, "lon": -87.8645},
    "Orland Park": {"lat": 41.6300, "lon": -87.8539},
    "Palos Hills": {"lat": 41.68, "lon": -87.81},
    "Blue Island": {"lat": 41.6569, "lon": -87.6847},
    "South Shore": {"lat": 41.7591, "lon": -87.5853},
    "Uptown": {"lat": 41.9747, "lon": -87.6547},
    "Albany Park": {"lat": 41.9760, "lon": -87.7250},
    "Englewood": {"lat": 41.7795, "lon": -87.6737},
    "Lemont": {"lat": 41.6689, "lon": -87.9405},
    "Homer Glen": {"lat": 41.6302, "lon": -87.9282},
    # Add more locations as needed
}

@app.route('/')
def index():
    return render_template('mm.html') 
@app.route('/mm')
def mm():
    return render_template('mm.html')  # Or any other template

@app.route('/weather-map')
def map_view():
    fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    
    # Set the extent to zoom into the Chicago area
    ax.set_extent([-88.08, -87.54, 41.58, 42.06])

    # Your map background image (use any static image or leave it out)
    R = mpimg.imread("525map.jpeg")
    ax.imshow(R, origin='upper', extent=[-88.08, -87.52, 41.58, 42.06], transform=ccrs.PlateCarree(), zorder=1)

    # Add map features
    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.RIVERS, linestyle='-')
    ax.add_feature(cfeature.BORDERS, linestyle=':')

    # Fetch and plot weather data for each location
    for city, coords in locations.items():
        LAT, LON = coords["lat"], coords["lon"]
        
        # Fetch weather data for each location
        weather_data = fetch_weather_data(city, LAT, LON)

        # Plot the weather data on the map
        ax.plot(LON, LAT, marker='o', color='white', markersize=6, transform=ccrs.PlateCarree())
        ax.text(LON + 0.005, LAT + 0.0, f"{city}", fontsize=8, color='white', zorder=1.8, transform=ccrs.PlateCarree(), bbox=dict(facecolor='black', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.1'))
        
        # Additional plotting logic (cloud cover, temperature, etc.)
        if weather_data:
            # Extract the necessary fields from the weather data
            temperature_f = (weather_data['temp'] * 9/5) + 32  # Convert temp to Fahrenheit
            dew_point_f = (weather_data['dewpt'] * 9/5) + 32  # Convert temp to Fahrenheit
            cloud_cover = weather_data['clouds']
            sea_level_pressure = weather_data['slp']  # Sea level pressure in hPa (or mb)
            wind_speed_mph = weather_data['wind_spd'] * 2.23694  # Convert wind speed to mph
            wind_direction = weather_data['wind_dir']  # Wind direction in degrees
            weather_icon = weather_data['weather']['icon']  # Icon name for the weather condition

            # Display the temperature in red above the city
            ax.text(LON, LAT + 0.01, f"{temperature_f:.1f}°F", color='red', fontweight='bold', ha='center', fontsize=10, transform=ccrs.PlateCarree(), bbox=dict(facecolor='black', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.1'))

            # Display the dew point in green below the cloud cover circle
            ax.text(LON, LAT - 0.02, f"{dew_point_f:.1f}°F", color='limegreen', fontweight='bold', ha='center', fontsize=10,
                transform=ccrs.PlateCarree(), bbox=dict(facecolor='black', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.1'))
            
            # Display wind speed and direction (as text)
            ax.text(LON - 0.017, LAT, f"{wind_speed_mph:.1f}mph", color='yellow', ha='center', fontsize=7,
                transform=ccrs.PlateCarree(), bbox=dict(facecolor='black', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.1'))
            
            # Optionally, draw wind barbs (wind direction arrows)
            wind_direction_rad = np.deg2rad(wind_direction)
            v = wind_speed_mph * -np.cos(wind_direction_rad)
            u = wind_speed_mph * -np.sin(wind_direction_rad)
            ax.barbs(LON, LAT, u, v, length=10, color='yellow', transform=ccrs.PlateCarree())

            # Cloud cover visualization using a wedge
            circle_radius = 0.005  # Radius for cloud cover indicator
            circle = patches.Circle((LON, LAT), circle_radius, color='white', alpha=0.6, transform=ccrs.PlateCarree(), zorder=2)
            ax.add_patch(circle)

            # Cloud cover fraction (0 to 1 scale)
            cloud_cover_fill = cloud_cover / 100.0  # Convert to a fraction (e.g., 60% => 0.6)

            # Draw the wedge based on cloud cover fraction
            wedge = patches.Wedge(
                (LON, LAT), circle_radius, 0, 360 * cloud_cover_fill,  # Fill up to a percentage of the circle (in degrees)
                facecolor='gray', edgecolor='black', transform=ccrs.PlateCarree(), zorder=3
            )
            ax.add_patch(wedge)

            # Display the sea level pressure in blue to the bottom right of the location
            ax.text(LON + 0.005, LAT - 0.007, f"{sea_level_pressure:.1f} mb", color='skyblue', fontweight='bold', ha='left', fontsize=6, zorder=1.8, transform=ccrs.PlateCarree(), bbox=dict(facecolor='black', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.1'))

            # Fetch and display the weather icon (using URL)
            icon_url = f"https://www.weatherbit.io/static/img/icons/{weather_icon}.png"
            response = requests.get(icon_url)
            if response.status_code == 200:
                with open(f"{weather_icon}.png", "wb") as f:
                    f.write(response.content)
            img = OffsetImage(plt.imread(f"{weather_icon}.png"), zoom=0.25)
            ab = AnnotationBbox(img, (LON + 0.015, LAT), xycoords='data', frameon=False, pad=0.0, boxcoords="data", zorder=1.02)
            if not weather_icon.startswith("c"):
              ax.add_artist(ab)

    with ThreadPoolExecutor() as executor:
        executor.map(fetch_weather_data, locations.keys(), locations.values())
    # Get the current UTC time
    current_time = datetime.utcnow()

    # Convert to Central Time (CDT or CST depending on daylight saving)
    central_tz = pytz.timezone('America/Chicago')
    central_time = pytz.utc.localize(current_time).astimezone(central_tz)

    # Format the time to be in the desired format 'MM/DD/YYYY at HH:MM AM/PM CDT'
    formatted_time = central_time.strftime("%m/%d/%Y at %I:%M %p CDT")

    # Set the title with the date and time in Central Time
    ax.set_title(f"Surface Weather Observations as of {formatted_time}")

    # Save the plot to a BytesIO object to send it as an image response
    img = io.BytesIO()
    fig.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)  # Rewind to the start of the BytesIO object
    return send_file(img, mimetype='image/png')

def fetch_weather_data(city, lat, lon):
    """Fetch weather data from the API."""
    url = f'https://api.weatherbit.io/v2.0/current?lat={lat}&lon={lon}&key={API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['data'][0]
    return {}

if __name__ == '__main__':
    app.run(debug=False)
@app.route('/')
def home():
    return render_template('mm.html')



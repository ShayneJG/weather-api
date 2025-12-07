import requests
from PIL import Image, ImageDraw, ImageFont
import pystray
import threading
import time
import json
from window import WeatherWindow, app_state
from recommendations import get_all_recommendations

# Hardcoded for now for testing purposes
backend_location = "http://192.168.50.115:8000"

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)


def fetch_latest_weather():
    """
    Sends a GET request to the backend to retrieve the latest weather station report.
    """
    endpoint = "/data/latest"
    response = requests.get(backend_location + endpoint, timeout=5)
    return response.json()


def fetch_history(hours=24):
    """
    Sends a GET request to the backend to retrieve historical weather data.

    :param hours: Number of hours to look back (default 24)
    :return: List of historical weather records
    """
    endpoint = f"/data/history?hours={hours}"
    response = requests.get(backend_location + endpoint, timeout=5)
    return response.json()

def create_icon(uv_value):
    """
    Creates an icon to be shown in the tray. Currently supports displaying the UV.

    Generates a 64x64 image with the UV written to the centre. 
    
    :param uv_value: The reported UV from the latest weather station report.
    
    :return image: The created image object. 
    """
    image = Image.new('RGB', (64, 64), color='darkblue')
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial.ttf", 48)
    draw.text((16, 12), str(uv_value), fill='white', font=font)
    return image


def create_menu(data):
    """
    Creates the right-click menu for the tray. 

    Has a series of MenuItems representing different data points parsed from 
    the backend data.

    :param data: Data object containing key:value pairs representing weather station data. 
    """
    items = []
    skip_fields = [
        'PASSKEY', 'stationtype', 'runtime', 'heap', 'freq', 'model',
        'interval'
    ]
    for key, value in data.items():
        if key in skip_fields:
            continue

        items.append(pystray.MenuItem(f"{key}: {value}", None))

    # append the extra tooltips
    items.append(pystray.MenuItem("Show", on_click, default=True))
    items.append(pystray.MenuItem(f"Quit", quit_app))
    return pystray.Menu(*items)


def quit_app(icon):
    """
    Terminates the application.
    
    :param icon: The icon representing the tray application.
    """
    icon.stop()
    weather_window.window.quit()


def update_loop():
    """
    Checks for latest weather reported from backend every 60 seconds.
    Fetches current weather and historical data, computes recommendations,
    and updates the icon and menu.
    """
    while True:
        try:
            # Fetch current weather and history
            current_weather = fetch_latest_weather()
            history = fetch_history(hours=24)

            # Compute recommendations
            recommendations = get_all_recommendations(current_weather, history, config)

            # Update app state
            app_state["latest_data"] = current_weather
            app_state["recommendations"] = recommendations

            # Update tray icon and menu
            uv = current_weather.get('uv', '--')
            icon.icon = create_icon(uv)
            icon.menu = create_menu(current_weather)
        except Exception as e:
            print(f"Error fetching data: {e}")
        time.sleep(60)


def on_click(icon, item):
    """
    On click function for the tray icon. 

    :param icon: passed by pystray, required but unused.
    :param item: passed by pystray, required but unused.
    """
    global app_state
    print("on click clicked")
    app_state["show_window"] = True
    print(f"on click - flag set to: {app_state["show_window"]}")


def convert_to_celcius(value):
    """
    Converts a given value from farenheit to celcius.
    
    :param value: The value in farenheit. 
    :return value: The value in celcius.
    """
    return round((value - 32) / 1.8, 1)

def convert_to_metric(value):
    """
    Converts a given value from MPH to KPH. 

    :param value: The value in MPH.
    :return value: The value in KPH.
    """
    return round(value * 1.609344, 2)


if __name__ == "__main__":
    icon = pystray.Icon("weather", create_icon("--"), "Weather",
                        create_menu({}))
    icon.run_detached()
    time.sleep(1)
    weather_window = WeatherWindow()
    thread = threading.Thread(target=update_loop, daemon=True)
    thread.start()
    weather_window.window.mainloop()

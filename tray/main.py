import requests
from PIL import Image, ImageDraw, ImageFont
import pystray
import threading
import time
# Hardcoded for now for testing purposes
backend_location = "http://192.168.50.115:8000"

def fetch_latest_weather():
    """
    Sends a GET request to the backend to retrieve the latest weather station report.
    """
    endpoint = "/data/latest"
    response = requests.get(backend_location + endpoint)
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
    items.append(pystray.MenuItem(f"Quit", quit_app))
    return pystray.Menu(*items)

def quit_app(icon):
    """
    Terminates the application.
    
    :param icon: The icon representing the tray application.
    """
    icon.stop()

def update_loop():
    """
    Checks for latest weather reported from backend every 60 seconds. 
    Updates the icon and menu based on the data received. Passes the data
    to the create_menu function in order to populate the menu. Passes the uv (for now)
    to the create_icon function to draw the UV as a number in the tray. 
    """
    while True:
        try:
            data = fetch_latest_weather()
            uv = data.get('uv', '--')
            icon.icon = create_icon(uv)
            icon.menu = create_menu(data)
        except Exception as e:
            print(f"Error fetching data: {e}")
        time.sleep(60)

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
    icon = pystray.Icon("weather", create_icon("--"), "Weather", create_menu({}))
    thread = threading.Thread(target=update_loop, daemon=True)
    thread.start()

    icon.run()

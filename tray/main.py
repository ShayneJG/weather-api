import requests
from PIL import Image, ImageDraw, ImageFont
import pystray
# Hardcoded for now for testing purposes
backend_location = "http://192.168.50.155:8000"
#TODO: Translate farenheit to celsius
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
    return pystray.Menu(
        pystray.MenuItem(f"Temperature: {data.get('tempf', '?')}°F", None),
        pystray.MenuItem(f"Humidity: {data.get('humidity', '?')}%", None),
        pystray.MenuItem("Quit", lambda: quit_app(icon))
    )

def quit_app(icon):
    """
    Terminates the application.
    
    :param icon: The icon representing the tray application.
    """
    icon.stop()



if __name__ == "__main__":
    icon = pystray.Icon("weather", create_icon("-"), "Weather", create_menu({}))
    # icon.run() is currently blocking. Application runs until quit_app is called by clicking the Quit MenuItem.
    icon.run()
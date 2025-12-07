"""
Author: Shayne Geilman
Weather API backend.
2025

Receives weather data from an ECOWITT WS2910 weather station and serves it via REST endpoints.
"""
from fastapi import FastAPI, Request
import datetime
from database import WeatherDatabase

app = FastAPI()
db = WeatherDatabase()

latest_report = {}

@app.post("/data/report")
async def report(request: Request):
    """
    Receives weather data from Ecowitt WS2910 weather station.
    
    The station sends form-encoded data at a configurable interval (default 60s).
    All temperature values are in Fahrenheit, pressure in inHg, speeds in mph,
    and rainfall in inches.
    
    Metadata:
        PASSKEY: Unique station identifier
        stationtype: Console firmware version
        runtime: Uptime in seconds
        dateutc: Timestamp (UTC)
        model: Outdoor sensor model
        interval: Reporting interval in seconds
    
    Indoor (console):
        tempinf: Temperature (°F)
        humidityin: Humidity (%)
        baromrelin: Relative pressure (inHg)
        baromabsin: Absolute pressure (inHg)
    
    Outdoor (sensor array):
        tempf: Temperature (°F)
        humidity: Humidity (%)
        winddir: Wind direction (degrees)
        windspeedmph: Wind speed (mph)
        windgustmph: Wind gust (mph)
        maxdailygust: Max gust today (mph)
        solarradiation: Solar radiation (W/m²)
        uv: UV index
    
    Rainfall:
        rainratein: Rain rate (in/hr)
        eventrainin, hourlyrainin, dailyrainin: Event/hour/day totals
        weeklyrainin, monthlyrainin, yearlyrainin, totalrainin: Cumulative totals
    
    Battery:
        wh65batt: Sensor battery (0=OK, 1=low)
    """
    global latest_report
    form_data = await request.form()
    imperial_data = dict(form_data)

    # Convert to metric units
    metric_data = convert_imperial_to_metric(imperial_data)
    latest_report = metric_data

    # Store in database
    db.insert_report(metric_data)

    display_latest()
    return {"status": "received"}
    
@app.get("/data/latest")
async def get_latest_report():
    """
    GET request endpoint to return the raw latest weather station report.
    """
    return latest_report

@app.get("/health")
async def health():
    """
    GET request endpoint to establish the health of the server.

    Returns JSON with status: ok to determine whether the server is running.
    """
    return {"status": "ok"}


@app.get("/data/history")
async def get_history(hours: int = 24):
    """
    GET request endpoint to return historical weather data.

    :param hours: Number of hours to look back (default 24)
    :return: List of historical weather reports
    """
    return db.get_yesterday_data(hours)


def convert_imperial_to_metric(imperial_data: dict) -> dict:
    """
    Convert imperial units to metric.

    Converts:
    - Temperature: Fahrenheit → Celsius
    - Wind speed: mph → km/h
    - Rain rate: in/hr → mm/hr
    - Pressure: inHg → hPa

    :param imperial_data: Dictionary with imperial units from weather station
    :return: Dictionary with metric units
    """
    metric_data = imperial_data.copy()

    # Temperature: F → C
    if 'tempf' in imperial_data:
        metric_data['temp_c'] = round((float(imperial_data['tempf']) - 32) / 1.8, 1)

    # Wind speed: mph → km/h
    if 'windspeedmph' in imperial_data:
        metric_data['wind_speed_kmh'] = round(float(imperial_data['windspeedmph']) * 1.609344, 1)

    # Rain rate: in/hr → mm/hr
    if 'rainratein' in imperial_data:
        metric_data['rain_rate_mm'] = round(float(imperial_data['rainratein']) * 25.4, 2)

    # Pressure: inHg → hPa
    if 'baromrelin' in imperial_data:
        metric_data['pressure_hpa'] = round(float(imperial_data['baromrelin']) * 33.8639, 1)

    # Copy direct values (no conversion needed)
    for key in ['humidity', 'uv', 'winddir', 'solarradiation']:
        if key in imperial_data:
            metric_data[key.replace('dir', '_dir')] = imperial_data[key]

    return metric_data


def display_latest():
    """
    Displays the latest weather data to the terminal.

    When the backend receives POST data from the weather station, it is stored in a global variable
    and then printed to the terminal for debugging purposes.
    """
    date = datetime.datetime.now()
    print(f"\n[{date}] Latest weather data:")
    for key,value in latest_report.items():
        print(f"{key}: {value}")

    
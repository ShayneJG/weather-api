# backend for weather-api. Accepts POST requests from weather station. Accepts GET requests

from fastapi import FastAPI, Request
import datetime
app = FastAPI()

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
    latest_report = dict(form_data)
    
    # TODO: Convert received data from farenheit to celcius.
    display_latest()
    return {"status": "received"}
    
@app.get("/data/latest")
async def get_latest_report():
    return latest_report

@app.get("/health")
async def health():
    return {"status": "ok"}


def display_latest():
    date = datetime.datetime.now()
    print(f"\n[{date}] Latest weather data:")
    for key,value in latest_report.items():
        print(f"{key}: {value}")

    
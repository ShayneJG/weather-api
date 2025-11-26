# backend for weather-api. Accepts POST requests from weather station. Accepts GET requests

from fastapi import FastAPI, Request
import datetime
app = FastAPI()

latest_report = {}

@app.post("/data/report")
async def report(request: Request):
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

    
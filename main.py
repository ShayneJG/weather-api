# backend for weather-api. Accepts POST requests from weather station. Accepts GET requests

from fastapi import FastAPI, Request

app = FastAPI()

latest_report = {}

@app.post("/data/report")
async def report(request: Request):
    form_data = await request.form()
    latest_order = dict(form_data)
    # TODO: Convert received data from farenheit to celcius.
    return {"status": "received"}
    
@app.get("/data/latest")
async def get_latest_report():
    return latest_report

@app.get("/health")
async def health():
    return {"status": "ok"}

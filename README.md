# Weather API

Local weather station API and tray application for activity recommendations.

## Overview

This project provides a complete weather monitoring solution with:
- **Backend**: FastAPI server that receives data from an ECOWITT WS2910 weather station.
- **Tray Client**: Windows system tray application with dark mode UI showing activity recommendations.

## Features

### Backend (FastAPI)
- Receives weather data from ECOWITT WS2910 weather station every 60 seconds.
- Converts imperial units (°F, mph, inHg) to metric (°C, km/h, hPa).
- Stores historical weather data in SQLite database.
- Provides REST API endpoints for current and historical data.

### Tray Client (Python + pystray + tkinter)
- Dark mode borderless popup window.
- **Colour-coded activity recommendations** for running, cycling, and swimming.
  - 🟢 **Green**: All conditions perfect.
  - 🟡 **Yellow**: UV moderate (4-6) but other conditions OK.
  - 🔴 **Red**: Critical conditions not met.
- Displays current weather conditions.
- Predictions based on yesterday's data.
- Updates every 60 seconds.
- Configurable thresholds via JSON file.

## API Endpoints

### `POST /data/report`
Receives weather station data (called by ECOWITT station every 60s).

### `GET /data/latest`
Returns the most recent weather report in metric units.

**Example Response:**
```json
{
  "temp_c": 22.5,
  "humidity": 65,
  "uv": 5.0,
  "wind_speed_kmh": 12.3,
  "winddir": 180,
  "rain_rate_mm": 0.0,
  "solarradiation": 450,
  "pressure_hpa": 1013.2
}
```

### `GET /data/history?hours=24`
Returns historical weather data.

**Parameters:**
- `hours` (optional): Number of hours to look back (default: 24).

**Example Response:**
```json
[
  {
    "id": 1,
    "timestamp": "2025-01-15T10:00:00",
    "temp_c": 20.1,
    "humidity": 70,
    "uv": 3.0,
    ...
  },
  ...
]
```

### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

## Setup

### Prerequisites
- Python 3.13.2.
- ECOWITT WS2910 weather station (for backend).
- Windows OS (for tray client, uses system tray + tkinter).

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create and activate virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The backend will:
- Start accepting weather station data on port 8000.
- Create `weather_history.db` SQLite database.
- Store data indefinitely (no automatic cleanup).

### Tray Client Setup

1. Navigate to tray directory:
```bash
cd tray
```

2. Create and activate virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. **Configure backend location:**

Edit `tray/main.py` and update the backend IP address:
```python
backend_location = "http://192.168.50.115:8000"  # Change to your backend IP.
```

5. Run the tray application:
```bash
python main.py
```

The tray icon will appear in your system tray with the current UV index. Left-click to show the detailed window with activity recommendations.

## Configuration

### Activity Thresholds

Edit `tray/config.json` to customise activity recommendation thresholds:

```json
{
  "activity_thresholds": {
    "run": {
      "temp_min_c": 8,
      "temp_max_c": 30,
      "uv_max": 3,
      "uv_moderate_max": 6,
      "rain_rate_max_mm": 0.5
    },
    "cycle": {
      "temp_min_c": 8,
      "temp_max_c": 30,
      "uv_max": 3,
      "uv_moderate_max": 6,
      "rain_rate_max_mm": 0.5,
      "wind_max_kmh": 30
    },
    "swim": {
      "temp_min_c": 8,
      "temp_max_c": 35,
      "uv_max": 3,
      "uv_moderate_max": 6,
      "rain_rate_max_mm": 0.5
    }
  }
}
```

**Threshold Explanation:**
- `temp_min_c` / `temp_max_c`: Temperature range for activity.
- `uv_max`: Maximum UV for green status.
- `uv_moderate_max`: Maximum UV for yellow status (above = red).
- `rain_rate_max_mm`: Maximum rain rate (mm/hr).
- `wind_max_kmh`: Maximum wind speed (cycling only).

Changes take effect on next tray app restart.

## Storage

### Database Size
- Weather data: ~2KB per report.
- 60-second intervals: 1,440 reports/day.
- **Daily storage**: ~2.8MB.
- **30 days**: ~84MB.
- **1 year**: ~1GB.

### Database Location
- File: `backend/weather_history.db`.
- Data persists indefinitely (no automatic deletion).
- Optional manual cleanup via `db.cleanup_old_data(days=30)` in Python.

## Activity Recommendation Logic

The tray client uses simple if/else logic to evaluate conditions:

**Green (Good to go):**
- Temperature in range.
- UV ≤ 3.
- No active rain.
- Wind OK (cycling only).

**Yellow (Moderate):**
- Temperature in range.
- UV 4-6 (moderate).
- No active rain.
- Wind OK.

**Red (Not recommended):**
- Temperature out of range.
- UV > 6.
- Active rain.
- Wind too high (cycling).

**Predictions:**
When conditions aren't currently ideal, the app looks at yesterday's data and displays: "Yesterday at 6:00 PM was good" (if conditions were suitable at that time yesterday).

## Architecture

```
ECOWITT WS2910 Weather Station
         |
         | POST /data/report (every 60s, imperial units)
         v
    Backend Server (FastAPI)
    - Converts to metric
    - Stores in SQLite
    - Serves via REST API
         |
         | GET /data/latest + /data/history (every 60s)
         v
    Tray Client (Python)
    - Loads config.json
    - Computes recommendations locally
    - Displays dark mode UI
```

## Troubleshooting

### Backend won't start
- Check port 8000 is not in use: `netstat -ano | findstr :8000`.
- Ensure Python 3.13.2 is installed.
- Verify virtual environment is activated.

### Tray client shows errors
- Verify backend is running and accessible.
- Check `backend_location` in `tray/main.py` matches your backend IP.
- Ensure firewall allows connection to backend port 8000.

### No weather data
- Verify ECOWITT station is configured to send data to backend IP:8000.
- Check backend console for incoming POST requests.
- Verify station is online and connected to network.

### Database too large
Manually clean up old data in Python:
```python
from database import WeatherDatabase
db = WeatherDatabase()
deleted = db.cleanup_old_data(days=30)  # Keep last 30 days.
print(f"Deleted {deleted} old records")
```

## Development

### Project Structure
```
weather-api/
├── backend/
│   ├── main.py              # FastAPI app, endpoints, metric conversion.
│   ├── database.py          # SQLite operations.
│   ├── requirements.txt     # Backend dependencies.
│   └── weather_history.db   # SQLite database (gitignored).
├── tray/
│   ├── main.py              # Tray app, update loop, data fetching.
│   ├── window.py            # Dark mode UI window.
│   ├── ui_components.py     # Reusable UI components.
│   ├── recommendations.py   # Activity recommendation logic.
│   ├── config.json          # User-editable thresholds.
│   └── requirements.txt     # Tray client dependencies.
└── README.md
```

### Key Design Decisions
1. **Unit conversion in backend**: Single source of truth.
2. **Recommendations in frontend**: Simple if/else logic, easy to customise.
3. **Config in frontend**: Edit locally without SSH to Proxmox server.
4. **SQLite for history**: Minimal footprint, no extra dependencies.
5. **No automatic cleanup**: Data persists indefinitely.

## Licence

Personal project for local weather monitoring.

## Author

Shayne Geilman, 2025

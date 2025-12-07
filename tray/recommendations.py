"""
Activity recommendation logic for weather-based outdoor activities.

Simple if/else logic to determine if conditions are suitable for running, cycling, or swimming.
"""
from typing import Dict, List, Optional
from datetime import datetime


def evaluate_activity(activity: str, weather: Dict, config: Dict) -> Dict:
    """
    Evaluate if weather conditions are suitable for an activity.

    Returns a dictionary with:
    - status: "green" (good), "yellow" (moderate), or "red" (not recommended)
    - reasons: List of condition descriptions
    - score: 0-100 rating

    :param activity: Activity name ("run", "cycle", or "swim")
    :param weather: Current weather data dictionary
    :param config: Configuration dictionary with thresholds
    :return: Evaluation result dictionary
    """
    # Validate inputs
    if not isinstance(weather, dict):
        return {
            "status": "red",
            "reasons": ["No weather data available"],
            "score": 0
        }

    if activity not in config['activity_thresholds']:
        return {
            "status": "red",
            "reasons": ["Unknown activity"],
            "score": 0
        }

    thresholds = config['activity_thresholds'][activity]
    reasons = []
    score = 100

    # Extract weather values with safe defaults
    temp = float(weather.get('temp_c', 999))
    uv = float(weather.get('uv', 11))
    rain = float(weather.get('rain_rate_mm', 0))
    wind = float(weather.get('wind_speed_kmh', 0))

    # Temperature check
    if temp < thresholds['temp_min_c']:
        reasons.append(f"Too cold ({temp}°C)")
        score = 0
    elif temp > thresholds['temp_max_c']:
        reasons.append(f"Too hot ({temp}°C)")
        score = 0

    # Rain check
    if rain > thresholds['rain_rate_max_mm']:
        reasons.append(f"Active rain ({rain}mm/hr)")
        score = 0

    # UV check (determines green/yellow/red)
    if uv > thresholds['uv_moderate_max']:
        reasons.append(f"UV too high ({uv})")
        score = 0
    elif uv > thresholds['uv_max']:
        reasons.append(f"UV moderate ({uv})")
        if score == 100:  # Only set to 50 if no other issues
            score = 50

    # Wind check (cycling only)
    if 'wind_max_kmh' in thresholds and wind > thresholds['wind_max_kmh']:
        reasons.append(f"Too windy ({wind} km/h)")
        score = 0

    # Determine overall status
    if score == 0:
        status = "red"
    elif score < 100:
        status = "yellow"
    else:
        status = "green"

    # Add positive message if all conditions are good
    if not reasons:
        reasons = ["All conditions good"]

    return {
        "status": status,
        "reasons": reasons,
        "score": score
    }


def predict_good_time(activity: str, history: List[Dict], config: Dict) -> Optional[str]:
    """
    Find when conditions were good yesterday for prediction.

    Looks through historical data to find the first time yesterday when
    conditions were suitable for the activity.

    :param activity: Activity name ("run", "cycle", or "swim")
    :param history: List of historical weather records
    :param config: Configuration dictionary with thresholds
    :return: Prediction message or None if no good times found
    """
    # Validate history is a list
    if not isinstance(history, list):
        return None

    good_times = []

    for record in history:
        # Skip if record is not a dictionary
        if not isinstance(record, dict):
            continue

        evaluation = evaluate_activity(activity, record, config)
        if evaluation['status'] == 'green':
            try:
                timestamp = datetime.fromisoformat(record['timestamp'])
                good_times.append(timestamp)
            except (KeyError, ValueError, TypeError):
                continue

    if not good_times:
        return None

    # Return first good time yesterday
    first_good = min(good_times)
    return f"Yesterday at {first_good.strftime('%I:%M %p')} was good"


def get_all_recommendations(current_weather: Dict, history: List[Dict], config: Dict) -> Dict:
    """
    Get recommendations for all activities.

    :param current_weather: Current weather data
    :param history: Historical weather data (last 24 hours)
    :param config: Configuration dictionary
    :return: Dictionary with recommendations for each activity
    """
    # Validate inputs
    if not isinstance(current_weather, dict):
        # Return empty recommendations if no valid weather data
        return {
            activity: {
                "status": "red",
                "reasons": ["No weather data available"],
                "score": 0,
                "prediction": None
            }
            for activity in ['run', 'cycle', 'swim']
        }

    recommendations = {}

    for activity in ['run', 'cycle', 'swim']:
        evaluation = evaluate_activity(activity, current_weather, config)
        prediction = None

        # Only show prediction if conditions aren't currently good
        if evaluation['status'] != 'green' and isinstance(history, list):
            prediction = predict_good_time(activity, history, config)

        recommendations[activity] = {
            **evaluation,
            "prediction": prediction
        }

    return recommendations

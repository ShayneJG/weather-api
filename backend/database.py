"""
SQLite database operations for weather data storage.

Stores converted metric weather data with automatic cleanup of old records.
"""
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List


class WeatherDatabase:
    """Manages SQLite storage for weather station reports."""

    def __init__(self, db_path: str = "weather_history.db"):
        """
        Initialize database connection.

        :param db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Create weather_reports table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS weather_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    temp_c REAL,
                    humidity INTEGER,
                    uv REAL,
                    wind_speed_kmh REAL,
                    wind_dir INTEGER,
                    rain_rate_mm REAL,
                    solar_radiation REAL,
                    pressure_hpa REAL,
                    raw_data TEXT
                )
            ''')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON weather_reports(timestamp)')
            conn.commit()

    def insert_report(self, metric_data: Dict):
        """
        Store a weather report with metric units.

        :param metric_data: Dictionary containing metric weather data
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO weather_reports
                (timestamp, temp_c, humidity, uv, wind_speed_kmh, wind_dir,
                 rain_rate_mm, solar_radiation, pressure_hpa, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                metric_data.get('temp_c'),
                metric_data.get('humidity'),
                metric_data.get('uv'),
                metric_data.get('wind_speed_kmh'),
                metric_data.get('wind_dir'),
                metric_data.get('rain_rate_mm'),
                metric_data.get('solarradiation'),
                metric_data.get('pressure_hpa'),
                str(metric_data)
            ))
            conn.commit()

    def get_yesterday_data(self, hours_ago: int = 24) -> List[Dict]:
        """
        Get weather data from the last N hours.

        :param hours_ago: Number of hours to look back (default 24)
        :return: List of weather report dictionaries
        """
        cutoff = (datetime.now() - timedelta(hours=hours_ago)).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM weather_reports
                WHERE timestamp > ?
                ORDER BY timestamp ASC
            ''', (cutoff,))
            return [dict(row) for row in cursor.fetchall()]

    def cleanup_old_data(self, days_to_keep: int = 30):
        """
        Delete weather data older than specified days.

        :param days_to_keep: Number of days to retain (default 30)
        """
        cutoff = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('DELETE FROM weather_reports WHERE timestamp < ?', (cutoff,))
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count

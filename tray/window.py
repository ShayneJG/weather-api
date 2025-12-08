"""
Dark mode weather window with activity recommendations.

Displays color-coded activity cards for run/cycle/swim and current weather metrics.
"""
import tkinter as tk
from ui_components import ActivityCard, WeatherMetricRow, COLORS

app_state = {"show_window": False, "latest_data": {}, "recommendations": {}}


class WeatherWindow:
    """Borderless dark mode window showing activity recommendations and weather."""

    def __init__(self):
        self.window = tk.Tk()
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.withdraw()
        self.window.configure(bg=COLORS['bg_dark'])

        # Main container
        main_frame = tk.Frame(self.window, bg=COLORS['bg_dark'], padx=15, pady=15)
        main_frame.pack(fill='both', expand=True)

        # Title
        title = tk.Label(
            main_frame,
            text="ACTIVITY RECOMMENDATIONS",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS['bg_dark'],
            fg=COLORS['text_primary']
        )
        title.pack(pady=(0, 10))

        # Activity cards
        self.activity_cards = {}
        for activity in ['run', 'cycle', 'swim']:
            card = ActivityCard(main_frame, activity)
            card.pack(fill='x', pady=5)
            self.activity_cards[activity] = card

        # Separator
        separator = tk.Frame(main_frame, height=1, bg=COLORS['border'])
        separator.pack(fill='x', pady=10)

        # Weather metrics section
        metrics_title = tk.Label(
            main_frame,
            text="CURRENT CONDITIONS",
            font=("Segoe UI", 9, "bold"),
            bg=COLORS['bg_dark'],
            fg=COLORS['text_secondary']
        )
        metrics_title.pack(pady=(5, 5))

        # Create metric rows
        self.metrics = {}
        metric_labels = [
            ('uv', 'UV Index'),
            ('temp_c', 'Temperature'),
            ('wind_speed_kmh', 'Wind Speed'),
            ('wind_dir', 'Wind Direction'),
            ('solarradiation', 'Solar Radiation'),
            ('humidity', 'Humidity')
        ]

        for key, label in metric_labels:
            row = WeatherMetricRow(main_frame, label)
            row.pack(fill='x')
            self.metrics[key] = row

        # Error label (hidden by default)
        self.error_label = tk.Label(
            main_frame,
            text="",
            font=("Segoe UI", 9, "italic"),
            bg=COLORS['bg_dark'],
            fg=COLORS['red'],
            wraplength=300
        )

        # Close on focus loss
        self.window.bind('<FocusOut>', lambda e: self.hide())
        self.poll_for_updates()

    def show(self):
        """Show window near bottom-right of screen, above taskbar."""
        # Update window to get actual dimensions
        self.window.update_idletasks()

        # Get window and screen dimensions
        window_width = self.window.winfo_reqwidth()
        window_height = self.window.winfo_reqheight()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        # Calculate taskbar-aware screen height (workarea excludes taskbar)
        # Add 10px padding from edges
        x_pos = screen_width - window_width - 10
        y_pos = screen_height - window_height - 50  # 50px accounts for typical taskbar height

        self.window.geometry("+{}+{}".format(int(x_pos), int(y_pos)))
        self.window.deiconify()
        self.window.focus_force()

    def hide(self):
        """Hide the window."""
        self.window.withdraw()

    def update(self, data: dict, recommendations: dict):
        """
        Update UI with weather data and recommendations.

        :param data: Current weather data dictionary
        :param recommendations: Activity recommendations dictionary
        """
        # Update activity cards
        for activity, rec in recommendations.items():
            if activity in self.activity_cards:
                self.activity_cards[activity].update_status(rec)

        # Update metrics
        self.metrics['uv'].update_value(f"{data.get('uv', '--')}")
        self.metrics['temp_c'].update_value(f"{data.get('temp_c', '--')}°C")
        self.metrics['wind_speed_kmh'].update_value(f"{data.get('wind_speed_kmh', '--')} km/h")
        self.metrics['wind_dir'].update_value(f"{data.get('wind_dir', '--')}°")
        self.metrics['solarradiation'].update_value(f"{data.get('solarradiation', '--')} W/m²")
        self.metrics['humidity'].update_value(f"{data.get('humidity', '--')}%")

    def poll_for_updates(self):
        """Poll for state changes every second."""
        # Check for errors
        if app_state.get("error"):
            self.error_label.config(text=app_state["error"])
            self.error_label.pack(pady=10)
        else:
            self.error_label.pack_forget()

        # Update data if available
        if app_state["latest_data"] and app_state["recommendations"]:
            self.update(app_state["latest_data"], app_state["recommendations"])

        # Show window if requested
        if app_state["show_window"]:
            app_state["show_window"] = False
            self.show()

        self.window.after(1000, self.poll_for_updates)

"""
Reusable UI components for the weather tray application.

Dark mode themed components for displaying activity recommendations and weather metrics.
"""
import tkinter as tk
from typing import Dict

# Dark mode color palette
COLORS = {
    'bg_dark': '#1e1e1e',
    'bg_card': '#2d2d2d',
    'text_primary': '#ffffff',
    'text_secondary': '#b0b0b0',
    'green': '#4caf50',
    'yellow': '#ffc107',
    'red': '#f44336',
    'border': '#404040'
}


class ActivityCard(tk.Frame):
    """A card showing activity recommendation status with color-coded indicators."""

    def __init__(self, parent, activity_name: str, **kwargs):
        super().__init__(parent, bg=COLORS['bg_card'], **kwargs)
        self.activity_name = activity_name

        # Activity name label
        self.name_label = tk.Label(
            self,
            text=activity_name.upper(),
            font=("Segoe UI", 10, "bold"),
            bg=COLORS['bg_card'],
            fg=COLORS['text_primary']
        )
        self.name_label.pack(anchor='w', padx=10, pady=(10, 5))

        # Status indicator (colored circle + text)
        self.status_frame = tk.Frame(self, bg=COLORS['bg_card'])
        self.status_frame.pack(anchor='w', padx=10, pady=5)

        self.status_canvas = tk.Canvas(
            self.status_frame,
            width=20,
            height=20,
            bg=COLORS['bg_card'],
            highlightthickness=0
        )
        self.status_canvas.pack(side='left', padx=(0, 5))
        self.circle = self.status_canvas.create_oval(5, 5, 15, 15, fill=COLORS['red'])

        self.status_text = tk.Label(
            self.status_frame,
            text="Checking...",
            font=("Segoe UI", 9),
            bg=COLORS['bg_card'],
            fg=COLORS['text_secondary']
        )
        self.status_text.pack(side='left')

        # Prediction label (hidden by default)
        self.prediction_label = tk.Label(
            self,
            text="",
            font=("Segoe UI", 8, "italic"),
            bg=COLORS['bg_card'],
            fg=COLORS['text_secondary'],
            wraplength=200,
            justify='left'
        )

    def update_status(self, recommendation: Dict):
        """
        Update card based on recommendation data.

        :param recommendation: Dictionary with status, reasons, and prediction
        """
        status = recommendation.get('status', 'red')
        reasons = recommendation.get('reasons', [])
        prediction = recommendation.get('prediction')

        # Update circle color
        color = COLORS[status]
        self.status_canvas.itemconfig(self.circle, fill=color)

        # Update status text
        if status == 'green':
            self.status_text.config(text="Good to go!", fg=COLORS['green'])
        elif status == 'yellow':
            self.status_text.config(text="Moderate UV", fg=COLORS['yellow'])
        else:
            reason_text = reasons[0] if reasons else "Not recommended"
            self.status_text.config(text=reason_text, fg=COLORS['red'])

        # Show/hide prediction
        if prediction:
            self.prediction_label.config(text=prediction)
            self.prediction_label.pack(anchor='w', padx=10, pady=(0, 10))
        else:
            self.prediction_label.pack_forget()


class WeatherMetricRow(tk.Frame):
    """A row showing a weather metric (e.g., Temp: 22°C)."""

    def __init__(self, parent, label: str, value: str = "--", **kwargs):
        super().__init__(parent, bg=COLORS['bg_dark'], **kwargs)

        self.label = tk.Label(
            self,
            text=f"{label}:",
            font=("Segoe UI", 9),
            bg=COLORS['bg_dark'],
            fg=COLORS['text_secondary'],
            width=15,
            anchor='w'
        )
        self.label.pack(side='left', padx=(10, 5))

        self.value_label = tk.Label(
            self,
            text=value,
            font=("Segoe UI", 9, "bold"),
            bg=COLORS['bg_dark'],
            fg=COLORS['text_primary'],
            anchor='w'
        )
        self.value_label.pack(side='left')

    def update_value(self, value: str):
        """
        Update the displayed value.

        :param value: New value to display
        """
        self.value_label.config(text=value)

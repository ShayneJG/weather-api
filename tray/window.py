import tkinter as tk

class WeatherWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.overrideredirect(True)  # Removes title bar
        self.window.attributes('-topmost', True)  # Stays on top
        self.window.withdraw()  # Start hidden
        
        # Labels for displaying data
        self.uv_label = tk.Label(self.window, text="UV: --", font=("Arial", 24))
        self.uv_label.pack(pady=10)
        
        self.temp_label = tk.Label(self.window, text="Temp: --", font=("Arial", 14))
        self.temp_label.pack()
        
        self.humidity_label = tk.Label(self.window, text="Humidity: --", font=("Arial", 14))
        self.humidity_label.pack()
        
        # Close when clicking outside
        self.window.bind('<FocusOut>', lambda e: self.hide())
    
    def show(self):
        # Position near bottom-right of screen
        self.window.geometry("+{}+{}".format(
            self.window.winfo_screenwidth() - 250,
            self.window.winfo_screenheight() - 300
        ))
        self.window.deiconify()
        self.window.focus_force()
    
    def hide(self):
        self.window.withdraw()
    
    def update(self, data):
        self.uv_label.config(text=f"UV: {data.get('uv', '--')}")
        self.temp_label.config(text=f"Temp: {data.get('tempf', '--')}°F")
        self.humidity_label.config(text=f"Humidity: {data.get('humidity', '--')}%")
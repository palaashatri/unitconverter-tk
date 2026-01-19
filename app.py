import sys
import tkinter as tk
from tkinter import ttk

from src import area, digital, length, temperature, weight, volume, speed, time_converter, pressure, energy


class AppState:
    """Shared application state"""
    def __init__(self):
        self.precision = 6
        self.use_scientific = False
        self.history = []
        self.dark_mode = False
    
    def add_history(self, entry: str):
        self.history.insert(0, entry)
        if len(self.history) > 10:
            self.history = self.history[:10]


def init_style(root: tk.Tk, state: AppState) -> ttk.Style:
    """Create a native-feeling ttk style based on the platform."""
    style = ttk.Style(root)

    platform = sys.platform
    theme_candidates = []
    
    # Detect dark mode
    try:
        if platform == "darwin":
            import subprocess
            result = subprocess.run(['defaults', 'read', '-g', 'AppleInterfaceStyle'], 
                                  capture_output=True, text=True)
            state.dark_mode = 'Dark' in result.stdout
        elif platform.startswith("win"):
            import winreg
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                    r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                state.dark_mode = value == 0
            except:
                pass
    except:
        pass
    
    if platform == "darwin":
        theme_candidates = ["aqua", "clam"]
    elif platform.startswith("win"):
        theme_candidates = ["vista", "xpnative", "clam"]
    else:
        theme_candidates = ["clam", "default"]

    for theme in theme_candidates:
        if theme in style.theme_names():
            style.theme_use(theme)
            break

    if platform == "darwin":
        base_font = ("SF Pro Text", 12)
        header_font = ("SF Pro Display", 18, "bold")
    elif platform.startswith("win"):
        base_font = ("Segoe UI", 10)
        header_font = ("Segoe UI", 16, "bold")
    else:
        base_font = ("Noto Sans", 11)
        header_font = ("Noto Sans", 16, "bold")
    
    style.configure("TFrame", padding=12)
    style.configure("TLabel", font=base_font)
    style.configure("TButton", padding=(10, 6), font=base_font)
    style.configure("Header.TLabel", font=header_font)
    style.configure("Subheader.TLabel", font=(base_font[0], max(base_font[1] - 1, 9)))
    
    # Status bar styles
    style.configure("Success.TLabel", foreground="#2d7d2d" if not state.dark_mode else "#5cb85c")
    style.configure("Error.TLabel", foreground="#c23030" if not state.dark_mode else "#ff6b6b")
    style.configure("Info.TLabel", foreground="#555555" if not state.dark_mode else "#aaaaaa")

    # Hover cues without breaking native look
    style.map(
        "TButton",
        relief=[("active", "groove")],
    )
    return style


def build_main_window() -> tk.Tk:
    state = AppState()
    root = tk.Tk()
    root.title("Unit Converter")
    root.minsize(920, 600)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    init_style(root, state)

    main_container = ttk.Frame(root)
    main_container.grid(row=0, column=0, sticky="nsew")
    main_container.columnconfigure(0, weight=1)
    main_container.rowconfigure(0, weight=1)
    
    # Left: converter area
    left_panel = ttk.Frame(main_container, padding=16)
    left_panel.grid(row=0, column=0, sticky="nsew")
    left_panel.columnconfigure(0, weight=1)
    left_panel.rowconfigure(1, weight=1)
    
    # Right: history & settings panel
    right_panel = ttk.Frame(main_container, padding=16, width=250)
    right_panel.grid(row=0, column=1, sticky="nsew")
    right_panel.grid_propagate(False)

    header = ttk.Frame(left_panel)
    header.grid(row=0, column=0, sticky="ew")
    header.columnconfigure(0, weight=1)
    ttk.Label(header, text="Unit Converter", style="Header.TLabel").grid(row=0, column=0, sticky="w")
    
    def show_about():
        about_window = tk.Toplevel(root)
        about_window.title("About Unit Converter")
        about_window.resizable(False, False)
        about_window.transient(root)
        about_window.grab_set()
        
        # Center the window
        about_window.update_idletasks()
        width = 400
        height = 250
        x = (about_window.winfo_screenwidth() // 2) - (width // 2)
        y = (about_window.winfo_screenheight() // 2) - (height // 2)
        about_window.geometry(f'{width}x{height}+{x}+{y}')
        
        content = ttk.Frame(about_window, padding=20)
        content.pack(fill="both", expand=True)
        
        ttk.Label(content, text="Unit Converter", font=("", 18, "bold")).pack(pady=(0, 10))
        ttk.Label(content, text="Version 2.0", font=("", 10)).pack(pady=(0, 20))
        
        ttk.Label(content, text="A modern, cross-platform unit conversion tool", 
                 font=("", 10), wraplength=360).pack(pady=(0, 20))
        
        ttk.Label(content, text="Author: Palaash Atri", font=("", 11, "bold")).pack(pady=(0, 10))
        
        ttk.Label(content, text="© 2024 All Rights Reserved", font=("", 9)).pack(pady=(10, 0))
        
        ttk.Button(content, text="OK", command=about_window.destroy, width=10).pack(pady=(20, 0))
    
    ttk.Button(header, text="About", command=show_about, width=8).grid(row=0, column=1, sticky="e", padx=5)
    
    status_var = tk.StringVar(value="Select a tab to start")
    status_style = tk.StringVar(value="Info.TLabel")
    
    def update_status(msg: str, style: str = "info"):
        status_var.set(msg)
        if style == "success":
            status_style.set("Success.TLabel")
        elif style == "error":
            status_style.set("Error.TLabel")
        else:
            status_style.set("Info.TLabel")

    notebook = ttk.Notebook(left_panel)
    notebook.grid(row=1, column=0, sticky="nsew", pady=(12, 0))

    # Create all converter tabs with state reference
    converters = [
        (temperature.TemperatureConverter(notebook, update_status, state), "Temperature"),
        (length.LengthConverter(notebook, update_status, state), "Length"),
        (area.AreaConverter(notebook, update_status, state), "Area"),
        (digital.DigitalConverter(notebook, update_status, state), "Digital"),
        (weight.WeightConverter(notebook, update_status, state), "Weight"),
        (volume.VolumeConverter(notebook, update_status, state), "Volume"),
        (speed.SpeedConverter(notebook, update_status, state), "Speed"),
        (time_converter.TimeConverter(notebook, update_status, state), "Time"),
        (pressure.PressureConverter(notebook, update_status, state), "Pressure"),
        (energy.EnergyConverter(notebook, update_status, state), "Energy"),
    ]
    
    for frame, text in converters:
        notebook.add(frame, text=text)

    status_bar = ttk.Label(left_panel, textvariable=status_var, anchor="w")
    status_bar.grid(row=2, column=0, sticky="ew", pady=(10, 0))
    status_bar.configure(style=status_style.get())
    
    # Update status bar style when it changes
    def update_status_bar_style(*args):
        status_bar.configure(style=status_style.get())
    status_style.trace_add("write", update_status_bar_style)

    # Settings panel
    settings_frame = ttk.LabelFrame(right_panel, text="Settings", padding=10)
    settings_frame.pack(fill="x", pady=(0, 10))
    
    ttk.Label(settings_frame, text="Decimal Places:").pack(anchor="w")
    precision_var = tk.IntVar(value=state.precision)
    precision_spin = ttk.Spinbox(settings_frame, from_=0, to=15, textvariable=precision_var, width=10)
    precision_spin.pack(anchor="w", pady=(2, 8))
    
    def update_precision(*args):
        state.precision = precision_var.get()
    precision_var.trace_add("write", update_precision)
    
    sci_var = tk.BooleanVar(value=state.use_scientific)
    ttk.Checkbutton(settings_frame, text="Scientific notation", variable=sci_var,
                    command=lambda: setattr(state, 'use_scientific', sci_var.get())).pack(anchor="w")

    # History panel
    history_frame = ttk.LabelFrame(right_panel, text="Recent Conversions", padding=10)
    history_frame.pack(fill="both", expand=True)
    
    history_text = tk.Text(history_frame, height=15, width=30, wrap="word", state="disabled",
                          font=("Courier", 9))
    history_text.pack(fill="both", expand=True)
    
    def update_history():
        history_text.configure(state="normal")
        history_text.delete(1.0, "end")
        for entry in state.history:
            history_text.insert("end", entry + "\n\n")
        history_text.configure(state="disabled")
    
    state.update_history_display = update_history

    # Keyboard shortcuts
    def switch_tab(index):
        if 0 <= index < len(converters):
            notebook.select(index)
    
    def reset_current_tab():
        update_status("Reset current tab", "info")
    
    # Platform-specific modifier key
    mod_key = "Command" if sys.platform == "darwin" else "Control"
    
    root.bind(f"<{mod_key}-w>", lambda e: root.destroy())
    root.bind(f"<{mod_key}-q>", lambda e: root.destroy())
    for i in range(10):
        root.bind(f"<{mod_key}-{i}>", lambda e, idx=i-1: switch_tab(idx) if idx >= 0 else switch_tab(9))

    return root


if __name__ == "__main__":
    app = build_main_window()
    app.mainloop()

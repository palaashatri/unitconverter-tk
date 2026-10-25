import argparse
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import tkinter as tk
from tkinter import ttk

from src import (
    angle,
    area,
    cooking,
    data_rate,
    digital,
    fuel_economy,
    length,
    temperature,
    weight,
    volume,
    speed,
    time_converter,
    pressure,
    energy,
    quick_convert,
)
from src import utils
from src.app_state import AppState
from src.persistence import (
    load_settings,
    save_settings,
    settings_path as default_settings_path,
)


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


def build_main_window(settings_path: Path | str | None = None) -> tk.Tk:
    path = Path(settings_path) if settings_path is not None else default_settings_path()
    state, settings_warning = load_settings(path)
    root = tk.Tk()
    root.app_state = state
    root.settings_path = path
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
    left_panel.rowconfigure(2, weight=1)
    
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
    
    status_var = tk.StringVar(master=root, value="Select a tab to start")
    status_style = tk.StringVar(master=root, value="Info.TLabel")
    
    def update_status(msg: str, style: str = "info"):
        status_var.set(msg)
        if style == "success":
            status_style.set("Success.TLabel")
        elif style == "error":
            status_style.set("Error.TLabel")
        else:
            status_style.set("Info.TLabel")

    settings_dirty = False
    settings_write_after_id = None

    def cancel_scheduled_settings_write():
        nonlocal settings_write_after_id
        if settings_write_after_id is not None:
            root.after_cancel(settings_write_after_id)
            settings_write_after_id = None

    def persist_settings(mark_dirty=True):
        nonlocal settings_dirty
        cancel_scheduled_settings_write()
        if mark_dirty:
            settings_dirty = True
        try:
            save_settings(state, path)
        except OSError:
            update_status(
                "Saved settings could not be written; conversions remain available.",
                "error",
            )
            return False
        return True

    def flush_scheduled_settings_write():
        nonlocal settings_write_after_id
        settings_write_after_id = None
        persist_settings(mark_dirty=False)

    def schedule_settings_write():
        nonlocal settings_dirty, settings_write_after_id
        settings_dirty = True
        cancel_scheduled_settings_write()
        settings_write_after_id = root.after(400, flush_scheduled_settings_write)

    state.on_change = schedule_settings_write

    quick_frame = ttk.Frame(left_panel)
    quick_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
    quick_frame.columnconfigure(1, weight=1)
    ttk.Label(quick_frame, text="Type to convert:").grid(
        row=0, column=0, sticky="w", padx=(0, 8)
    )
    quick_expression = tk.StringVar(master=root)
    quick_entry = ttk.Entry(
        quick_frame, textvariable=quick_expression, name="quick_convert_entry"
    )
    quick_entry.grid(row=0, column=1, sticky="ew")
    quick_result = tk.StringVar(master=root, value="Example: 10 km in mi")
    quick_result_label = ttk.Label(
        quick_frame, textvariable=quick_result, name="quick_convert_result"
    )
    quick_result_label.grid(row=1, column=1, sticky="w", pady=(3, 0))

    def convert_quick(event=None):
        expression = quick_expression.get().strip()
        try:
            result = quick_convert.convert_expression(expression)
            precision = state.precision
            formatted = utils.format_number(
                result.value, precision, state.use_scientific
            )
        except (OverflowError, ValueError) as error:
            quick_result.set(str(error))
            update_status(str(error), "error")
            return "break"

        quick_result.set(f"{formatted} {result.target_label}")
        update_status("✓ Quick conversion complete", "success")
        state.add_history(
            f"{expression} = {formatted} {result.target_label}"
        )
        persist_settings()
        if hasattr(state, "update_history_display"):
            state.update_history_display()
        return "break"

    ttk.Button(
        quick_frame,
        text="Convert",
        name="quick_convert_button",
        command=convert_quick,
    ).grid(row=0, column=2, padx=(8, 0))
    quick_entry.bind("<Return>", convert_quick)
    ttk.Label(
        quick_frame,
        text="Examples: 10 km in mi  ·  72 F to C",
        style="Subheader.TLabel",
    ).grid(row=2, column=1, sticky="w", pady=(2, 0))

    notebook = ttk.Notebook(left_panel)
    notebook.grid(row=2, column=0, sticky="nsew", pady=(12, 0))

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
        (angle.AngleConverter(notebook, update_status, state), "Angle"),
        (data_rate.DataRateConverter(notebook, update_status, state), "Data rate"),
        (fuel_economy.FuelEconomyConverter(notebook, update_status, state), "Fuel economy"),
        (cooking.CookingConverter(notebook, update_status, state), "Cooking"),
    ]
    
    for frame, text in converters:
        notebook.add(frame, text=text)
    root.converter_tab_labels = tuple(
        notebook.tab(tab_id, "text") for tab_id in notebook.tabs()
    )

    status_bar = ttk.Label(
        left_panel, textvariable=status_var, anchor="w", name="status_bar"
    )
    status_bar.grid(row=3, column=0, sticky="ew", pady=(10, 0))
    status_bar.configure(style=status_style.get())
    
    # Update status bar style when it changes
    def update_status_bar_style(*args):
        status_bar.configure(style=status_style.get())
    status_style.trace_add("write", update_status_bar_style)

    # Settings panel
    settings_frame = ttk.LabelFrame(right_panel, text="Settings", padding=10)
    settings_frame.pack(fill="x", pady=(0, 10))
    
    ttk.Label(settings_frame, text="Decimal Places:").pack(anchor="w")
    precision_var = tk.StringVar(master=root, value=str(state.precision))

    def commit_precision(event=None):
        raw_value = precision_var.get().strip()
        try:
            value = int(raw_value)
        except ValueError:
            update_status(
                "Decimal places must be a whole number from 0 to 15.", "error"
            )
            precision_var.set(str(state.precision))
            return "break" if event is not None else None

        bounded = min(15, max(0, value))
        if bounded != value:
            update_status("Decimal places must be from 0 to 15.", "error")
            value = bounded
        precision_var.set(str(value))
        if state.precision != value:
            state.precision = value
            persist_settings()
        return "break" if event is not None else None

    precision_spin = ttk.Spinbox(
        settings_frame,
        from_=0,
        to=15,
        textvariable=precision_var,
        command=commit_precision,
        width=10,
        name="precision_spinbox",
    )
    precision_spin.pack(anchor="w", pady=(2, 8))
    precision_spin.bind("<Return>", commit_precision)
    precision_spin.bind("<FocusOut>", commit_precision)
    
    sci_var = tk.BooleanVar(master=root, value=state.use_scientific)
    def update_scientific():
        state.use_scientific = sci_var.get()
        persist_settings()

    ttk.Checkbutton(
        settings_frame,
        text="Scientific notation",
        variable=sci_var,
        command=update_scientific,
        name="scientific_notation",
    ).pack(anchor="w")

    # History panel
    history_frame = ttk.LabelFrame(right_panel, text="Recent Conversions", padding=10)
    history_frame.pack(fill="both", expand=True)
    
    history_text = tk.Text(
        history_frame,
        height=15,
        width=30,
        wrap="word",
        state="disabled",
        font=("Courier", 9),
        name="history_text",
    )
    history_text.pack(fill="both", expand=True)
    
    def update_history():
        history_text.configure(state="normal")
        history_text.delete(1.0, "end")
        for entry in state.history:
            history_text.insert("end", entry + "\n\n")
        history_text.configure(state="disabled")
    
    state.update_history_display = update_history
    update_history()

    if settings_warning:
        update_status(settings_warning, "error")

    # Keyboard shortcuts
    def switch_tab(index):
        if 0 <= index < len(converters):
            notebook.select(index)
    
    def reset_current_tab():
        update_status("Reset current tab", "info")

    def close_window():
        for flush_pending_history in tuple(
            getattr(root, "_pending_history_flushers", ())
        ):
            flush_pending_history()
        commit_precision()
        if not (settings_warning and not settings_dirty):
            persist_settings(mark_dirty=False)
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", close_window)
    
    # Platform-specific modifier key
    mod_key = "Command" if sys.platform == "darwin" else "Control"
    
    root.bind(f"<{mod_key}-w>", lambda e: close_window())
    root.bind(f"<{mod_key}-q>", lambda e: close_window())
    for i in range(10):
        root.bind(f"<{mod_key}-{i}>", lambda e, idx=i-1: switch_tab(idx) if idx >= 0 else switch_tab(9))

    return root


def run_smoke_test() -> int:
    """Start the Tk app, verify all category tabs, and exit without persistence."""
    with TemporaryDirectory(prefix="unitconverter-smoke-") as temp_directory:
        app = build_main_window(Path(temp_directory) / "settings.json")
        try:
            app.update()
            if len(app.converter_tab_labels) != 14:
                raise RuntimeError(
                    f"Expected 14 converter tabs, found {len(app.converter_tab_labels)}"
                )
            print(f"Smoke test passed: {len(app.converter_tab_labels)} converter tabs")
        finally:
            app.destroy()
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Unit Converter")
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    args = parser.parse_args(argv)
    if args.smoke_test:
        return run_smoke_test()

    app = build_main_window()
    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())

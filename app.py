import sys
import tkinter as tk
from tkinter import ttk

from src import area, digital, length, temperature, weight


def init_style(root: tk.Tk) -> ttk.Style:
    """Create a native-feeling ttk style based on the platform."""
    style = ttk.Style(root)

    platform = sys.platform
    theme_candidates = []
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

    # Hover cues without breaking native look
    style.map(
        "TButton",
        relief=[("active", "groove")],
    )
    return style


def build_main_window() -> tk.Tk:
    root = tk.Tk()
    root.title("Unit Converter")
    root.minsize(720, 520)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    init_style(root)

    container = ttk.Frame(root, padding=16)
    container.grid(row=0, column=0, sticky="nsew")
    container.columnconfigure(0, weight=1)
    container.rowconfigure(1, weight=1)

    header = ttk.Frame(container)
    header.grid(row=0, column=0, sticky="ew")
    header.columnconfigure(0, weight=1)
    ttk.Label(header, text="Unit Converter", style="Header.TLabel").grid(row=0, column=0, sticky="w")
    ttk.Button(header, text="Quit", command=root.destroy).grid(row=0, column=1, rowspan=2, sticky="e")

    status_var = tk.StringVar(value="Select a tab to start")
    update_status = lambda msg: status_var.set(msg)

    notebook = ttk.Notebook(container)
    notebook.grid(row=1, column=0, sticky="nsew", pady=(12, 0))

    notebook.add(temperature.TemperatureConverter(notebook, update_status), text="Temperature")
    notebook.add(length.LengthConverter(notebook, update_status), text="Length")
    notebook.add(area.AreaConverter(notebook, update_status), text="Area")
    notebook.add(digital.DigitalConverter(notebook, update_status), text="Digital")
    notebook.add(weight.WeightConverter(notebook, update_status), text="Weight")

    status_bar = ttk.Label(container, textvariable=status_var, anchor="w")
    status_bar.grid(row=2, column=0, sticky="ew", pady=(10, 0))

    return root


if __name__ == "__main__":
    app = build_main_window()
    app.mainloop()

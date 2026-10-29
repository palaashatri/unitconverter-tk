"""Tk interface for speed conversion."""

import tkinter as tk
from tkinter import ttk

from . import convert_speed
from .converter_ui import build_converter_frame

UNIT_LABELS = {
    "Meters/sec": "mps",
    "Kilometers/hr": "kph",
    "Miles/hr": "mph",
    "Feet/sec": "fps",
    "Knots": "knot",
    "Mach (dry air at 20 °C)": "mach",
}


def SpeedConverter(parent: tk.Widget, on_status=None, state=None) -> ttk.Frame:
    return build_converter_frame(
        parent,
        "Speed Converter",
        UNIT_LABELS,
        convert_speed.convert,
        on_status,
        state,
    )

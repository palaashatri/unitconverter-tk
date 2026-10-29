"""Tk interface for length conversion."""

import tkinter as tk
from tkinter import ttk

from . import convert_length
from .converter_ui import build_converter_frame

UNIT_LABELS = {
    "Nautical Miles": "nmi",
    "Miles": "mi",
    "Yards": "yd",
    "Feet": "ft",
    "Inches": "inch",
    "Kilometers": "km",
    "Meters": "m",
    "Centimeters": "cm",
    "Millimeters": "mm",
    # Singular compatibility aliases
    "Nautical Mile": "nmi",
    "Mile": "mi",
    "Yard": "yd",
    "Foot": "ft",
    "Inch": "inch",
    "Kilometer": "km",
    "Meter": "m",
    "Centimeter": "cm",
    "Millimeter": "mm",
}

DISPLAY_UNITS = [
    "Nautical Miles",
    "Miles",
    "Yards",
    "Feet",
    "Inches",
    "Kilometers",
    "Meters",
    "Centimeters",
    "Millimeters",
]


def LengthConverter(parent: tk.Widget, on_status=None, state=None) -> ttk.Frame:
    return build_converter_frame(
        parent,
        "Length Converter",
        UNIT_LABELS,
        convert_length.convert,
        on_status,
        state,
        display_units=DISPLAY_UNITS,
    )

"""Tk interface for volume conversion."""

import tkinter as tk
from tkinter import ttk

from . import convert_volume
from .converter_ui import build_converter_frame

UNIT_LABELS = {
    "Milliliter": "ml",
    "Liter": "l",
    "US cup": "cup",
    "US pint": "pint",
    "US quart": "quart",
    "US gallon": "gal",
    "US fluid ounce": "floz",
    "Cubic meter": "m3",
    "Cubic centimeter": "cm3",
    "Cubic inch": "in3",
    "Cubic foot": "ft3",
}


def VolumeConverter(parent: tk.Widget, on_status=None, state=None) -> ttk.Frame:
    return build_converter_frame(
        parent,
        "Volume Converter",
        UNIT_LABELS,
        convert_volume.convert,
        on_status,
        state,
    )

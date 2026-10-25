"""Tk interface for customary kitchen-volume conversion."""

import tkinter as tk
from tkinter import ttk

from . import convert_volume
from .converter_ui import build_converter_frame


UNIT_LABELS = {
    "Milliliter": "ml",
    "Liter": "l",
    "Teaspoon": "tsp",
    "Tablespoon": "tbsp",
    "US cup": "cup",
    "US fluid ounce": "floz",
    "US pint": "pint",
    "US quart": "quart",
    "US gallon": "gal",
}


def CookingConverter(parent: tk.Widget, on_status=None, state=None) -> ttk.Frame:
    return build_converter_frame(
        parent, "Cooking Volume Converter", UNIT_LABELS,
        convert_volume.convert, on_status, state
    )

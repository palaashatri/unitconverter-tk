"""Tk interface for weight/mass conversion."""

import tkinter as tk
from tkinter import ttk

from . import convert_weight
from .converter_ui import build_converter_frame

UNIT_LABELS = {
    "Kilogram": "kg",
    "Hectogram": "hg",
    "Decagram": "dag",
    "Gram": "g",
    "Decigram": "dg",
    "Centigram": "cg",
    "Milligram": "mg",
    # Plural compatibility aliases
    "Kilograms": "kg",
    "Hectograms": "hg",
    "Decagrams": "dag",
    "Grams": "g",
    "Decigrams": "dg",
    "Centigrams": "cg",
    "Milligrams": "mg",
}

DISPLAY_UNITS = [
    "Kilogram",
    "Hectogram",
    "Decagram",
    "Gram",
    "Decigram",
    "Centigram",
    "Milligram",
]


def WeightConverter(parent: tk.Widget, on_status=None, state=None) -> ttk.Frame:
    return build_converter_frame(
        parent,
        "Weight Converter",
        UNIT_LABELS,
        convert_weight.convert,
        on_status,
        state,
        display_units=DISPLAY_UNITS,
    )

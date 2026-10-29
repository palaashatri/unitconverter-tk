"""Tk interface for time conversion."""

import tkinter as tk
from tkinter import ttk

from . import convert_time
from .converter_ui import build_converter_frame

UNIT_LABELS = {
    "Microsecond": "us",
    "Millisecond": "ms",
    "Second": "sec",
    "Minute": "min",
    "Hour": "hr",
    "Day": "day",
    "Week": "week",
    "Average Gregorian month": "month",
    "Average Gregorian year": "year",
}


def TimeConverter(parent: tk.Widget, on_status=None, state=None) -> ttk.Frame:
    return build_converter_frame(
        parent,
        "Time Converter",
        UNIT_LABELS,
        convert_time.convert,
        on_status,
        state,
    )

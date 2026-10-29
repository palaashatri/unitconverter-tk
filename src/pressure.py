"""Tk interface for pressure conversion."""

import tkinter as tk
from tkinter import ttk

from . import convert_pressure
from .converter_ui import build_converter_frame

UNIT_LABELS = {
    "Pascal": "pa",
    "Kilopascal": "kpa",
    "Bar": "bar",
    "PSI": "psi",
    "Atmosphere": "atm",
    "Torr": "torr",
    "mmHg": "mmhg",
}


def PressureConverter(parent: tk.Widget, on_status=None, state=None) -> ttk.Frame:
    return build_converter_frame(
        parent,
        "Pressure Converter",
        UNIT_LABELS,
        convert_pressure.convert,
        on_status,
        state,
    )

"""Tk interface for energy conversion."""

import tkinter as tk
from tkinter import ttk

from . import convert_energy
from .converter_ui import build_converter_frame

UNIT_LABELS = {
    "Joule": "j",
    "Kilojoule": "kj",
    "Calorie (thermochemical)": "cal",
    "Kilocalorie (thermochemical)": "kcal",
    "Watt-hour": "wh",
    "Kilowatt-hour": "kwh",
    "BTU (IT)": "btu",
    "Foot-pound force": "ftlb",
    "Electronvolt": "ev",
}


def EnergyConverter(parent: tk.Widget, on_status=None, state=None) -> ttk.Frame:
    return build_converter_frame(
        parent,
        "Energy Converter",
        UNIT_LABELS,
        convert_energy.convert,
        on_status,
        state,
    )

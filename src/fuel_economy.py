"""Tk interface for fuel-economy conversion."""

import tkinter as tk
from tkinter import ttk

from . import convert_fuel_economy
from .converter_ui import build_converter_frame


UNIT_LABELS = {
    "L/100 km": "l_per_100km",
    "km/L": "km_per_l",
    "U.S. mpg": "mpg_us",
    "Imperial mpg": "mpg_imp",
}


def FuelEconomyConverter(parent: tk.Widget, on_status=None, state=None) -> ttk.Frame:
    return build_converter_frame(
        parent, "Fuel Economy Converter", UNIT_LABELS,
        convert_fuel_economy.convert, on_status, state
    )

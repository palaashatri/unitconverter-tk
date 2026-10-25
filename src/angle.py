"""Tk interface for angle conversion."""

import tkinter as tk
from tkinter import ttk

from . import convert_angle
from .converter_ui import build_converter_frame


UNIT_LABELS = {
    "Radians": "rad",
    "Degrees": "deg",
    "Gradians": "grad",
    "Turns": "turn",
    "Arcminutes": "arcmin",
    "Arcseconds": "arcsec",
}


def AngleConverter(parent: tk.Widget, on_status=None, state=None) -> ttk.Frame:
    return build_converter_frame(
        parent, "Angle Converter", UNIT_LABELS, convert_angle.convert, on_status, state
    )

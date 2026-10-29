"""Tk interface for area conversion."""

import tkinter as tk
from tkinter import ttk

from . import convert_area
from .converter_ui import build_converter_frame

UNIT_LABELS = {
    "Square meter": "sqm",
    "Square km": "sqkm",
    "Square rood": "sqr",
    "Square cm": "sqcm",
    "Square foot": "sqf",
    "Square inch": "sqin",
    "Square mile": "sqmile",
    "Square millimeter": "sqmm",
    "Square rod": "sqrod",
    "Square yard": "sqyard",
    "Square township": "sqtownship",
    "Square acre": "sqacre",
    "Square are": "sqare",
    "Square barn": "sqbarn",
    "Square hectare": "sqhectare",
    "Square homestead": "sqhomestead",
}


def AreaConverter(parent: tk.Widget, on_status=None, state=None) -> ttk.Frame:
    return build_converter_frame(
        parent,
        "Area Converter",
        UNIT_LABELS,
        convert_area.convert,
        on_status,
        state,
    )

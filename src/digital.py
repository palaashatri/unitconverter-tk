"""Tk interface for digital-storage conversion."""

import tkinter as tk
from tkinter import ttk

from . import convert_digital
from .converter_ui import build_converter_frame

UNIT_LABELS = {
    "Bits": "bit",
    "Bytes": "byte",
    "Kilobytes": "kB",
    "Megabytes": "MB",
    "Gigabytes": "GB",
    "Terabytes": "TB",
    "Petabytes": "PB",
    # Singular compatibility aliases
    "Bit": "bit",
    "Byte": "byte",
    "Kilobyte": "kB",
    "Megabyte": "MB",
    "Gigabyte": "GB",
    "Terabyte": "TB",
    "Petabyte": "PB",
}

DISPLAY_UNITS = [
    "Bits",
    "Bytes",
    "Kilobytes",
    "Megabytes",
    "Gigabytes",
    "Terabytes",
    "Petabytes",
]


def DigitalConverter(parent: tk.Widget, on_status=None, state=None) -> ttk.Frame:
    return build_converter_frame(
        parent,
        "Digital Storage Converter",
        UNIT_LABELS,
        convert_digital.convert,
        on_status,
        state,
        display_units=DISPLAY_UNITS,
    )

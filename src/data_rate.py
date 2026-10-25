"""Tk interface for data-rate conversion."""

import tkinter as tk
from tkinter import ttk

from . import convert_data_rate
from .converter_ui import build_converter_frame


UNIT_LABELS = {
    code: code for code in convert_data_rate.factors
}


def DataRateConverter(parent: tk.Widget, on_status=None, state=None) -> ttk.Frame:
    return build_converter_frame(
        parent, "Data Rate Converter", UNIT_LABELS,
        convert_data_rate.convert, on_status, state
    )

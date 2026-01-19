"""Utility functions for converters"""
import tkinter as tk
from tkinter import ttk


def format_number(value: float, precision: int, use_scientific: bool) -> str:
    """Format a number based on precision and scientific notation settings"""
    if use_scientific:
        return f"{value:.{precision}e}"
    else:
        # Remove trailing zeros
        formatted = f"{value:.{precision}f}".rstrip('0').rstrip('.')
        return formatted if formatted else "0"


def parse_number(value: str):
    """Parse a number, supporting scientific notation and negatives"""
    value = value.strip()
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return "invalid"


def copy_to_clipboard(root: tk.Widget, text: str):
    """Copy text to system clipboard"""
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()

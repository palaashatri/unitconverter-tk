"""Shared Tk widgets for simple one-value unit converters."""

import tkinter as tk
from tkinter import ttk

from . import utils


def build_converter_frame(parent, title, unit_labels, convert, on_status=None, state=None):
    """Build a consistent live-conversion frame for a linear unit category."""
    frame = ttk.Frame(parent, padding=12)
    frame.columnconfigure(1, weight=1)

    input_value = tk.StringVar(master=frame)
    output_value = tk.StringVar(master=frame)
    source_unit = tk.StringVar(master=frame)
    target_unit = tk.StringVar(master=frame)
    labels = dict(unit_labels)
    converting = False

    def set_status(message, style="info"):
        if on_status:
            on_status(message, style)

    def update_history(raw, formatted, source, target):
        if state is None or not hasattr(state, "add_history"):
            return
        state.add_history(f"{raw} {source} = {formatted} {target}")
        if hasattr(state, "update_history_display"):
            state.update_history_display()

    def callback(event=None):
        raw = input_value.get().strip()
        if not raw:
            output_value.set("")
            set_status("Enter a value to convert", "info")
            return

        amount = utils.parse_number(raw)
        if amount == "invalid":
            output_value.set("")
            set_status("Input must be a finite number", "error")
            return
        if not source_unit.get() or not target_unit.get():
            set_status("Pick both units", "info")
            return

        try:
            result = convert(amount, labels[source_unit.get()], labels[target_unit.get()])
            precision = state.precision if state else 6
            scientific = state.use_scientific if state else False
            formatted = utils.format_number(result, precision, scientific)
        except (KeyError, OverflowError, ValueError) as error:
            output_value.set("")
            set_status(str(error), "error")
            return

        output_value.set(formatted)
        set_status(f"✓ Converted {source_unit.get()} to {target_unit.get()}", "success")
        update_history(raw, formatted, source_unit.get(), target_unit.get())

    def auto_convert(*_):
        nonlocal converting
        if converting:
            return
        converting = True
        try:
            callback()
        finally:
            converting = False

    def reset():
        input_value.set("")
        output_value.set("")
        source_unit.set("")
        target_unit.set("")
        input_field.focus_set()
        set_status("Cleared values", "info")

    ttk.Label(frame, text=title, style="Header.TLabel").grid(
        row=0, column=0, columnspan=3, sticky="w", pady=(0, 12)
    )
    ttk.Label(frame, text="Input").grid(row=1, column=0, sticky="w", pady=4)
    input_field = ttk.Entry(frame, textvariable=input_value)
    input_field.grid(row=1, column=1, sticky="ew", pady=4)

    ttk.Label(frame, text="From").grid(row=2, column=0, sticky="w", pady=4)
    from_combo = ttk.Combobox(
        frame, textvariable=source_unit, state="readonly", values=list(labels)
    )
    from_combo.grid(row=2, column=1, sticky="ew", pady=4)
    ttk.Label(frame, text="To").grid(row=3, column=0, sticky="w", pady=4)
    to_combo = ttk.Combobox(
        frame, textvariable=target_unit, state="readonly", values=list(labels)
    )
    to_combo.grid(row=3, column=1, sticky="ew", pady=4)

    ttk.Label(frame, text="Output").grid(row=4, column=0, sticky="w", pady=4)
    output_field = ttk.Entry(frame, textvariable=output_value, state="readonly")
    output_field.grid(row=4, column=1, sticky="ew", pady=4)

    buttons = ttk.Frame(frame)
    buttons.grid(row=5, column=0, columnspan=3, sticky="w", pady=(12, 0))
    ttk.Button(buttons, text="Reset", command=reset).pack(side="left")

    input_value.trace_add("write", auto_convert)
    source_unit.trace_add("write", auto_convert)
    target_unit.trace_add("write", auto_convert)
    input_field.bind("<Return>", callback)
    from_combo.bind("<Return>", callback)
    to_combo.bind("<Return>", callback)
    input_field.focus_set()
    return frame

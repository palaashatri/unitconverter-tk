"""Shared Tk widgets for simple one-value unit converters."""

import tkinter as tk
from tkinter import ttk

from . import utils


HISTORY_IDLE_DELAY_MS = 500


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
    pending_history_after_id = None
    pending_history_entry = None
    pending_history_flushers = None

    def set_status(message, style="info"):
        if on_status:
            on_status(message, style)

    def cancel_pending_history():
        nonlocal pending_history_after_id, pending_history_entry
        if pending_history_after_id is not None:
            frame.after_cancel(pending_history_after_id)
            pending_history_after_id = None
        pending_history_entry = None

    def commit_pending_history():
        nonlocal pending_history_after_id, pending_history_entry
        pending_history_after_id = None
        entry = pending_history_entry
        pending_history_entry = None
        if state is None or not hasattr(state, "add_history"):
            return
        if not entry:
            return
        state.add_history(entry)
        if hasattr(state, "update_history_display"):
            state.update_history_display()

    def flush_pending_history():
        nonlocal pending_history_after_id
        if pending_history_after_id is not None:
            frame.after_cancel(pending_history_after_id)
            pending_history_after_id = None
        commit_pending_history()

    def update_history(raw, formatted, source, target, committed=False):
        nonlocal pending_history_after_id, pending_history_entry
        if state is None or not hasattr(state, "add_history"):
            return
        cancel_pending_history()
        pending_history_entry = f"{raw} {source} = {formatted} {target}"
        if committed:
            commit_pending_history()
        else:
            pending_history_after_id = frame.after(
                HISTORY_IDLE_DELAY_MS, commit_pending_history
            )

    def callback(event=None):
        raw = input_value.get().strip()
        if not raw:
            cancel_pending_history()
            output_value.set("")
            set_status("Enter a value to convert", "info")
            return

        amount = utils.parse_number(raw)
        if amount == "invalid":
            cancel_pending_history()
            output_value.set("")
            set_status("Input must be a finite number", "error")
            return
        if not source_unit.get() or not target_unit.get():
            cancel_pending_history()
            set_status("Pick both units", "info")
            return

        try:
            result = convert(amount, labels[source_unit.get()], labels[target_unit.get()])
            precision = state.precision if state else 6
            scientific = state.use_scientific if state else False
            formatted = utils.format_number(result, precision, scientific)
        except (KeyError, OverflowError, ValueError) as error:
            cancel_pending_history()
            output_value.set("")
            set_status(str(error), "error")
            return

        output_value.set(formatted)
        set_status(f"✓ Converted {source_unit.get()} to {target_unit.get()}", "success")
        update_history(
            raw,
            formatted,
            source_unit.get(),
            target_unit.get(),
            committed=event is not None,
        )

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
        cancel_pending_history()
        input_value.set("")
        output_value.set("")
        source_unit.set("")
        target_unit.set("")
        input_field.focus_set()
        set_status("Cleared values", "info")

    def swap_units(event=None):
        s = source_unit.get()
        t = target_unit.get()
        if s and t:
            source_unit.set(t)
            target_unit.set(s)
            set_status("Swapped units", "info")

    def copy_result(event=None):
        val = output_value.get().strip()
        if val:
            utils.copy_to_clipboard(frame, val)
            set_status("✓ Copied to clipboard", "success")

    frame.swap_units = swap_units
    frame.copy_result = copy_result
    frame.reset_tab = reset

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

    swap_btn = ttk.Button(frame, text="⇄", width=3, command=swap_units)
    swap_btn.grid(row=2, column=2, rowspan=2, padx=(4, 0), sticky="ns")

    ttk.Label(frame, text="To").grid(row=3, column=0, sticky="w", pady=4)
    to_combo = ttk.Combobox(
        frame, textvariable=target_unit, state="readonly", values=list(labels)
    )
    to_combo.grid(row=3, column=1, sticky="ew", pady=4)

    ttk.Label(frame, text="Output").grid(row=4, column=0, sticky="w", pady=4)
    output_field = ttk.Entry(frame, textvariable=output_value, state="readonly")
    output_field.grid(row=4, column=1, sticky="ew", pady=4)

    copy_btn = ttk.Button(frame, text="📋", width=3, command=copy_result)
    copy_btn.grid(row=4, column=2, padx=(4, 0))

    buttons = ttk.Frame(frame)
    buttons.grid(row=5, column=0, columnspan=3, sticky="w", pady=(12, 0))
    ttk.Button(buttons, text="Reset", command=reset).pack(side="left")

    input_value.trace_add("write", auto_convert)
    source_unit.trace_add("write", auto_convert)
    target_unit.trace_add("write", auto_convert)
    input_field.bind("<Return>", callback)
    from_combo.bind("<Return>", callback)
    to_combo.bind("<Return>", callback)

    def cleanup_history_timer(event):
        if event.widget is frame:
            cancel_pending_history()
            if pending_history_flushers is not None:
                try:
                    pending_history_flushers.remove(flush_pending_history)
                except ValueError:
                    pass

    frame.bind("<Destroy>", cleanup_history_timer, add="+")
    if state is not None and hasattr(state, "add_history"):
        root = frame.winfo_toplevel()
        pending_history_flushers = getattr(
            root, "_pending_history_flushers", None
        )
        if pending_history_flushers is None:
            pending_history_flushers = []
            root._pending_history_flushers = pending_history_flushers
        pending_history_flushers.append(flush_pending_history)
    input_field.focus_set()
    return frame

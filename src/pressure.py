import tkinter as tk
from tkinter import ttk

from . import convert_pressure
from . import utils


def PressureConverter(parent: tk.Widget, on_status=None, state=None) -> ttk.Frame:
    ids = {
        "Pascal": "pa",
        "Kilopascal": "kpa",
        "Bar": "bar",
        "PSI": "psi",
        "Atmosphere": "atm",
        "Torr": "torr",
        "mmHg": "mmhg",
    }

    frame = ttk.Frame(parent, padding=12)
    frame.columnconfigure(1, weight=1)

    in_amt = tk.StringVar(value="")
    out_amt = tk.StringVar(value="")
    in_unit = tk.StringVar(value="")
    out_unit = tk.StringVar(value="")
    
    converting = False

    def set_status(message: str, style: str = "info") -> None:
        if on_status:
            on_status(message, style)

    def auto_convert(*args):
        nonlocal converting
        if converting:
            return
        converting = True
        try:
            callback()
        finally:
            converting = False

    def callback(event=None):
        raw = in_amt.get().strip()
        if not raw:
            out_amt.set("")
            set_status("Enter a value to convert", "info")
            return
        
        parsed = utils.parse_number(raw)
        if parsed == "invalid":
            set_status("Input must be a valid number", "error")
            return
        
        amt = parsed

        if not in_unit.get() or not out_unit.get():
            set_status("Pick both units", "info")
            return

        try:
            frm = ids[in_unit.get()]
            to = ids[out_unit.get()]
            result = convert_pressure.convert(amt, frm, to)
            precision = state.precision if state else 6
            use_sci = state.use_scientific if state else False
            formatted = utils.format_number(result, precision, use_sci)
            out_amt.set(formatted)
            set_status(f"✓ Converted {in_unit.get()} to {out_unit.get()}", "success")
            
            if state and hasattr(state, 'add_history'):
                history_entry = f"{raw} {in_unit.get()} = {formatted} {out_unit.get()}"
                state.add_history(history_entry)
                if hasattr(state, 'update_history_display'):
                    state.update_history_display()
        except Exception as e:
            set_status(f"Error: {str(e)}", "error")

    def swap_units(event=None):
        temp_from = in_unit.get()
        temp_to = out_unit.get()
        if temp_from and temp_to:
            in_unit.set(temp_to)
            out_unit.set(temp_from)
            set_status("Swapped units", "info")
            # Auto-convert will trigger via trace

    def copy_result(event=None):
        result = out_amt.get()
        if result:
            utils.copy_to_clipboard(frame, result)
            set_status("✓ Copied to clipboard", "success")

    def reset(event=None):
        in_amt.set("")
        out_amt.set("")
        in_unit.set("")
        out_unit.set("")
        in_field.focus()
        set_status("Cleared values", "info")

    ttk.Label(frame, text="Pressure Converter", style="Header.TLabel").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))

    ttk.Label(frame, text="Input").grid(row=1, column=0, sticky="w", pady=4)
    in_field = ttk.Entry(frame, textvariable=in_amt)
    in_field.grid(row=1, column=1, sticky="ew", pady=4)

    ttk.Label(frame, text="From").grid(row=2, column=0, sticky="w", pady=4)
    from_combo = ttk.Combobox(frame, textvariable=in_unit, state="readonly", values=list(ids.keys()))
    from_combo.grid(row=2, column=1, sticky="ew", pady=4)
    
    swap_btn = ttk.Button(frame, text="⇄", width=3, command=swap_units)
    swap_btn.grid(row=2, column=2, rowspan=2, padx=(4, 0), sticky="ns")

    ttk.Label(frame, text="To").grid(row=3, column=0, sticky="w", pady=4)
    to_combo = ttk.Combobox(frame, textvariable=out_unit, state="readonly", values=list(ids.keys()))
    to_combo.grid(row=3, column=1, sticky="ew", pady=4)

    ttk.Label(frame, text="Output").grid(row=4, column=0, sticky="w", pady=4)
    out_field = ttk.Entry(frame, textvariable=out_amt, state="readonly")
    out_field.grid(row=4, column=1, sticky="ew", pady=4)
    
    copy_btn = ttk.Button(frame, text="📋", width=3, command=copy_result)
    copy_btn.grid(row=4, column=2, padx=(4, 0))

    buttons = ttk.Frame(frame)
    buttons.grid(row=5, column=0, columnspan=3, pady=(12, 0), sticky="w")
    ttk.Button(buttons, text="Reset", command=reset).pack(side="left")

    in_amt.trace_add("write", auto_convert)
    in_unit.trace_add("write", auto_convert)
    out_unit.trace_add("write", auto_convert)
    
    in_field.bind("<Return>", callback)
    from_combo.bind("<Return>", callback)
    to_combo.bind("<Return>", callback)

    in_field.focus()
    return frame
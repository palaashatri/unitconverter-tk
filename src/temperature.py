import tkinter as tk
from tkinter import ttk

from . import convert_temp
from . import utils


def TemperatureConverter(parent: tk.Widget, on_status=None, state=None) -> ttk.Frame:
    frame = ttk.Frame(parent, padding=12)
    frame.columnconfigure(1, weight=1)

    cel_temp = tk.StringVar(value="")
    fah_temp = tk.StringVar(value="")
    kel_temp = tk.StringVar(value="")
    
    converting = False
    last_edited = tk.StringVar(value="")

    def set_status(message: str, style: str = "info") -> None:
        if on_status:
            on_status(message, style)

    def auto_convert(*args):
        nonlocal converting
        if converting:
            return
        converting = True
        try:
            convert()
        finally:
            converting = False

    def convert(event=None):
        values = {
            "c": utils.parse_number(cel_temp.get()),
            "f": utils.parse_number(fah_temp.get()),
            "k": utils.parse_number(kel_temp.get()),
        }
        populated = [k for k, v in values.items() if v not in (None, "invalid")]

        if any(v == "invalid" for v in values.values() if v not in (None,)):
            set_status("Enter a valid number", "error")
            return

        if len(populated) == 0:
            cel_temp.set("")
            fah_temp.set("")
            kel_temp.set("")
            set_status("Enter a temperature value", "info")
            return
        
        if len(populated) > 1:
            # Keep only the last edited field
            if last_edited.get() in ["c", "f", "k"]:
                key = last_edited.get()
                if key == "c":
                    fah_temp.set("")
                    kel_temp.set("")
                    values = {"c": values["c"], "f": None, "k": None}
                    populated = ["c"]
                elif key == "f":
                    cel_temp.set("")
                    kel_temp.set("")
                    values = {"c": None, "f": values["f"], "k": None}
                    populated = ["f"]
                else:
                    cel_temp.set("")
                    fah_temp.set("")
                    values = {"c": None, "f": None, "k": values["k"]}
                    populated = ["k"]

        if len(populated) != 1:
            return

        key = populated[0]
        amt = values[key]
        precision = state.precision if state else 4
        use_sci = state.use_scientific if state else False

        try:
            if key == "c":
                f_val = convert_temp.convert_celToFah(amt)
                k_val = convert_temp.covert_celToKel(amt)
                fah_temp.set(utils.format_number(f_val, precision, use_sci))
                kel_temp.set(utils.format_number(k_val, precision, use_sci))
                set_status("✓ Converted from Celsius", "success")
                if state and hasattr(state, 'add_history'):
                    state.add_history(f"{amt}°C = {f_val:.2f}°F = {k_val:.2f}K")
                    if hasattr(state, 'update_history_display'):
                        state.update_history_display()
            elif key == "f":
                c_val = convert_temp.convert_fahToCel(amt)
                k_val = convert_temp.convert_fahToKel(amt)
                cel_temp.set(utils.format_number(c_val, precision, use_sci))
                kel_temp.set(utils.format_number(k_val, precision, use_sci))
                set_status("✓ Converted from Fahrenheit", "success")
                if state and hasattr(state, 'add_history'):
                    state.add_history(f"{amt}°F = {c_val:.2f}°C = {k_val:.2f}K")
                    if hasattr(state, 'update_history_display'):
                        state.update_history_display()
            else:
                if amt < 0:
                    set_status("Kelvin cannot be negative", "error")
                    return
                c_val = convert_temp.convert_kelToCel(amt)
                f_val = convert_temp.convert_kelTofah(amt)
                cel_temp.set(utils.format_number(c_val, precision, use_sci))
                fah_temp.set(utils.format_number(f_val, precision, use_sci))
                set_status("✓ Converted from Kelvin", "success")
                if state and hasattr(state, 'add_history'):
                    state.add_history(f"{amt}K = {c_val:.2f}°C = {f_val:.2f}°F")
                    if hasattr(state, 'update_history_display'):
                        state.update_history_display()
        except Exception as e:
            set_status(f"Error: {str(e)}", "error")

    def copy_all(event=None):
        results = []
        if cel_temp.get():
            results.append(f"C: {cel_temp.get()}")
        if fah_temp.get():
            results.append(f"F: {fah_temp.get()}")
        if kel_temp.get():
            results.append(f"K: {kel_temp.get()}")
        if results:
            utils.copy_to_clipboard(frame, " | ".join(results))
            set_status("✓ Copied to clipboard", "success")

    def reset(event=None):
        cel_temp.set("")
        fah_temp.set("")
        kel_temp.set("")
        cel_entry.focus()
        set_status("Cleared values", "info")

    def track_edit(field):
        def tracker(*args):
            last_edited.set(field)
        return tracker

    ttk.Label(frame, text="Temperature Converter", style="Header.TLabel").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))

    ttk.Label(frame, text="Celsius").grid(row=1, column=0, sticky="w", pady=4)
    cel_entry = ttk.Entry(frame, textvariable=cel_temp)
    cel_entry.grid(row=1, column=1, sticky="ew", pady=4)

    ttk.Label(frame, text="Fahrenheit").grid(row=2, column=0, sticky="w", pady=4)
    fah_entry = ttk.Entry(frame, textvariable=fah_temp)
    fah_entry.grid(row=2, column=1, sticky="ew", pady=4)

    ttk.Label(frame, text="Kelvin").grid(row=3, column=0, sticky="w", pady=4)
    kel_entry = ttk.Entry(frame, textvariable=kel_temp)
    kel_entry.grid(row=3, column=1, sticky="ew", pady=4)
    
    # Copy button
    copy_btn = ttk.Button(frame, text="📋 Copy All", command=copy_all)
    copy_btn.grid(row=3, column=2, padx=(4, 0))

    button_row = ttk.Frame(frame)
    button_row.grid(row=4, column=0, columnspan=3, pady=(12, 0), sticky="w")
    ttk.Button(button_row, text="Reset", command=reset).pack(side="left")

    # Track which field was last edited
    cel_temp.trace_add("write", track_edit("c"))
    fah_temp.trace_add("write", track_edit("f"))
    kel_temp.trace_add("write", track_edit("k"))
    
    # Real-time conversion
    cel_temp.trace_add("write", auto_convert)
    fah_temp.trace_add("write", auto_convert)
    kel_temp.trace_add("write", auto_convert)
    
    cel_entry.bind("<Return>", convert)
    fah_entry.bind("<Return>", convert)
    kel_entry.bind("<Return>", convert)

    cel_entry.focus()
    return frame
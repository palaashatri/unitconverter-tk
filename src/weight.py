import tkinter as tk
from tkinter import ttk

from . import convert_weight


def WeightConverter(parent: tk.Widget, on_status=None) -> ttk.Frame:
    ids = {
        "Kilogram": "kg",
        "Hectogram": "hg",
        "Decagram": "dg",
        "Gram": "g",
        "Decigram": "deg",
        "Centigram": "cg",
        "Milligram": "mg",
    }

    frame = ttk.Frame(parent, padding=12)
    frame.columnconfigure(1, weight=1)

    in_amt = tk.StringVar(value="")
    out_amt = tk.StringVar(value="")
    in_unit = tk.StringVar(value="")
    out_unit = tk.StringVar(value="")

    def set_status(message: str) -> None:
        if on_status:
            on_status(message)

    def callback(event=None):
        raw = in_amt.get().strip()
        if not raw:
            set_status("Enter a value to convert")
            return
        try:
            amt = float(raw)
        except ValueError:
            set_status("Input must be a number")
            return

        if not in_unit.get() or not out_unit.get():
            set_status("Pick both units")
            return

        frm = ids[in_unit.get()]
        to = ids[out_unit.get()]
        out_amt.set(str(round(convert_weight.convert(amt, frm, to), 6)))
        set_status(f"Converted {in_unit.get()} to {out_unit.get()}")

    def reset(event=None):
        in_amt.set("")
        out_amt.set("")
        in_unit.set("")
        out_unit.set("")
        in_field.focus()
        set_status("Cleared values")

    ttk.Label(frame, text="Weight Converter", style="Header.TLabel").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))

    ttk.Label(frame, text="Input").grid(row=1, column=0, sticky="w", pady=4)
    in_field = ttk.Entry(frame, textvariable=in_amt)
    in_field.grid(row=1, column=1, sticky="ew", pady=4)

    ttk.Label(frame, text="From").grid(row=2, column=0, sticky="w", pady=4)
    from_combo = ttk.Combobox(frame, textvariable=in_unit, state="readonly", values=list(ids.keys()))
    from_combo.grid(row=2, column=1, sticky="ew", pady=4)

    ttk.Label(frame, text="To").grid(row=3, column=0, sticky="w", pady=4)
    to_combo = ttk.Combobox(frame, textvariable=out_unit, state="readonly", values=list(ids.keys()))
    to_combo.grid(row=3, column=1, sticky="ew", pady=4)

    ttk.Label(frame, text="Output").grid(row=4, column=0, sticky="w", pady=4)
    ttk.Entry(frame, textvariable=out_amt, state="readonly").grid(row=4, column=1, sticky="ew", pady=4)

    buttons = ttk.Frame(frame)
    buttons.grid(row=5, column=0, columnspan=3, pady=(12, 0), sticky="w")
    ttk.Button(buttons, text="Convert", command=callback).grid(row=0, column=0, padx=(0, 8))
    ttk.Button(buttons, text="Reset", command=reset).grid(row=0, column=1)

    in_field.bind("<Return>", callback)
    from_combo.bind("<Return>", callback)
    to_combo.bind("<Return>", callback)

    in_field.focus()
    return frame

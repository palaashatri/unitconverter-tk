import tkinter as tk
from tkinter import ttk

from . import convert_temp


def TemperatureConverter(parent: tk.Widget, on_status=None) -> ttk.Frame:
    frame = ttk.Frame(parent, padding=12)
    frame.columnconfigure(1, weight=1)

    cel_temp = tk.StringVar(value="")
    fah_temp = tk.StringVar(value="")
    kel_temp = tk.StringVar(value="")

    def set_status(message: str) -> None:
        if on_status:
            on_status(message)

    def parse(value: str):
        value = value.strip()
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            return "invalid"

    def convert(event=None):
        values = {
            "c": parse(cel_temp.get()),
            "f": parse(fah_temp.get()),
            "k": parse(kel_temp.get()),
        }
        populated = [k for k, v in values.items() if v not in (None, "invalid")]

        if any(v == "invalid" for v in values.values() if v not in (None,)):
            set_status("Enter a number in only one field")
            return

        if len(populated) != 1:
            set_status("Fill exactly one field to convert")
            return

        key = populated[0]
        amt = values[key]

        if key == "c":
            fah_temp.set(str(round(convert_temp.convert_celToFah(amt), 4)))
            kel_temp.set(str(round(convert_temp.covert_celToKel(amt), 4)))
            set_status("Converted from Celsius")
        elif key == "f":
            cel_temp.set(str(round(convert_temp.convert_fahToCel(amt), 4)))
            kel_temp.set(str(round(convert_temp.convert_fahToKel(amt), 4)))
            set_status("Converted from Fahrenheit")
        else:
            cel_temp.set(str(round(convert_temp.convert_kelToCel(amt), 4)))
            fah_temp.set(str(round(convert_temp.convert_kelTofah(amt), 4)))
            set_status("Converted from Kelvin")

    def reset(event=None):
        cel_temp.set("")
        fah_temp.set("")
        kel_temp.set("")
        cel_entry.focus()
        set_status("Cleared values")

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

    button_row = ttk.Frame(frame)
    button_row.grid(row=4, column=0, columnspan=3, pady=(12, 0), sticky="w")
    ttk.Button(button_row, text="Convert", command=convert).grid(row=0, column=0, padx=(0, 8))
    ttk.Button(button_row, text="Reset", command=reset).grid(row=0, column=1)

    cel_entry.bind("<Return>", convert)
    fah_entry.bind("<Return>", convert)
    kel_entry.bind("<Return>", convert)

    cel_entry.focus()
    return frame
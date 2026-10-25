"""GUI smoke and behavior tests for converter tabs."""

import tkinter as tk
from tkinter import ttk

import pytest

from app import build_main_window
from src import angle, cooking, data_rate, fuel_economy, temperature


@pytest.fixture
def tk_root():
    try:
        root = tk.Tk()
    except tk.TclError as error:
        pytest.skip(f"Tk display is unavailable: {error}")
    root.withdraw()
    errors = []
    root.report_callback_exception = lambda *args: errors.append(args)
    yield root, errors
    root.destroy()


def _walk(widget):
    yield widget
    for child in widget.winfo_children():
        yield from _walk(child)


def _notebook(root):
    return next(widget for widget in _walk(root) if isinstance(widget, ttk.Notebook))


def _drive_converter(root, frame, from_label, to_label, amount):
    combos = [w for w in _walk(frame) if isinstance(w, ttk.Combobox)]
    entries = [
        w for w in _walk(frame)
        if isinstance(w, ttk.Entry) and not isinstance(w, ttk.Combobox)
    ]
    assert len(entries) == 2
    assert len(combos) == 2
    combos[0].set(from_label)
    combos[1].set(to_label)
    entries[0].delete(0, "end")
    entries[0].insert(0, amount)
    root.update()
    return entries[1].get()


def test_main_window_contains_all_fourteen_converter_categories(tk_root):
    root, _ = tk_root
    app = build_main_window()
    try:
        names = [_notebook(app).tab(tab_id, "text") for tab_id in _notebook(app).tabs()]
        assert names == [
            "Temperature", "Length", "Area", "Digital", "Weight", "Volume",
            "Speed", "Time", "Pressure", "Energy", "Angle", "Data rate",
            "Fuel economy", "Cooking",
        ]
    finally:
        app.destroy()


@pytest.mark.parametrize(
    ("factory", "from_label", "to_label", "amount", "expected"),
    [
        (angle.AngleConverter, "Radians", "Degrees", "1", 57.295779513),
        (data_rate.DataRateConverter, "bit/s", "kbit/s", "1000", 1.0),
        (fuel_economy.FuelEconomyConverter, "L/100 km", "km/L", "8", 12.5),
        (cooking.CookingConverter, "Milliliter", "Liter", "1000", 1.0),
    ],
)
def test_new_converter_tabs_convert_representative_values(
    tk_root, factory, from_label, to_label, amount, expected
):
    root, errors = tk_root
    statuses = []
    frame = factory(root, lambda message, style="info": statuses.append((message, style)))
    frame.pack()
    result = _drive_converter(root, frame, from_label, to_label, amount)
    assert float(result) == pytest.approx(expected)
    assert statuses[-1][1] == "success"
    assert errors == []


@pytest.mark.parametrize("invalid", ["", "not a number", "nan", "inf", "-inf"])
@pytest.mark.parametrize(
    "factory", [
        angle.AngleConverter,
        data_rate.DataRateConverter,
        fuel_economy.FuelEconomyConverter,
        cooking.CookingConverter,
    ],
)
def test_new_tabs_report_invalid_input_without_callback_errors(tk_root, factory, invalid):
    root, errors = tk_root
    statuses = []
    frame = factory(root, lambda message, style="info": statuses.append((message, style)))
    frame.pack()
    entries = [w for w in _walk(frame) if isinstance(w, ttk.Entry)]
    combos = [w for w in _walk(frame) if isinstance(w, ttk.Combobox)]
    combos[0].current(0)
    combos[1].current(1)
    entries[0].delete(0, "end")
    if invalid:
        entries[0].insert(0, invalid)
    root.update()
    assert statuses
    assert statuses[-1][1] in {"info", "error"}
    assert errors == []


def test_temperature_tab_rejects_below_absolute_zero_kelvin(tk_root):
    root, errors = tk_root
    statuses = []
    frame = temperature.TemperatureConverter(
        root, lambda message, style="info": statuses.append((message, style))
    )
    frame.pack()
    entries = [w for w in _walk(frame) if isinstance(w, ttk.Entry)]
    entries[2].insert(0, "-1")
    root.update()
    assert statuses[-1][1] == "error"
    assert "Kelvin" in statuses[-1][0]
    assert errors == []

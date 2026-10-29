"""GUI smoke and behavior tests for converter tabs."""

import sys
import tkinter as tk
from tkinter import ttk

import pytest

import app as app_module
from app import build_main_window
from src import angle, cooking, data_rate, fuel_economy, temperature
from src.app_state import AppState


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


def _named_widget(root, name):
    return next(widget for widget in _walk(root) if widget.winfo_name() == name)


def _status_text(root):
    status = _named_widget(root, "status_bar")
    return root.getvar(status.cget("textvariable"))


def _is_alive(root):
    try:
        return bool(root.winfo_exists())
    except tk.TclError:
        return False


def _close_window(root):
    close_command = root.tk.call("wm", "protocol", root._w, "WM_DELETE_WINDOW")
    root.tk.call(close_command)


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


def test_main_window_contains_all_fourteen_converter_categories(tk_root, tmp_path):
    root, _ = tk_root
    app = build_main_window(settings_path=tmp_path / "settings.json")
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


def test_angle_tab_rejects_unrepresentable_result_without_history(tk_root):
    root, errors = tk_root
    state = AppState()
    statuses = []
    frame = angle.AngleConverter(
        root, lambda message, style="info": statuses.append((message, style)), state
    )
    frame.pack()

    output = _drive_converter(root, frame, "Turns", "Radians", "1e308")

    assert output == ""
    assert statuses[-1][1] == "error"
    assert "conversion result" in statuses[-1][0]
    assert state.history == []
    assert errors == []


@pytest.mark.parametrize(
    ("expression", "action", "expected"),
    [
        ("10 km in mi", "return", "6.213712"),
        ("72 F to C", "button", "22.222222"),
    ],
)
def test_quick_convert_displays_result_and_records_once(
    tk_root, tmp_path, expression, action, expected
):
    _, errors = tk_root
    app = build_main_window(settings_path=tmp_path / "settings.json")
    app.deiconify()
    app.report_callback_exception = lambda *args: errors.append(args)
    try:
        entry = _named_widget(app, "quick_convert_entry")
        entry.insert(0, expression)
        if action == "return":
            entry.focus_force()
            app.update()
            entry.event_generate("<Return>")
        else:
            _named_widget(app, "quick_convert_button").invoke()
        app.update()

        result = _named_widget(app, "quick_convert_result").cget("text")
        history = next(w for w in _walk(app) if isinstance(w, tk.Text))
        assert expected in result
        assert history.get("1.0", "end").count(expression) == 1
        assert errors == []
    finally:
        app.destroy()


@pytest.mark.parametrize(
    ("expression", "message"),
    [("1 furlong to mi", "unknown unit"), ("1 b to byte/s", "ambiguous unit")],
)
def test_quick_convert_shows_actionable_errors_without_callback_exceptions(
    tk_root, tmp_path, expression, message
):
    _, errors = tk_root
    app = build_main_window(settings_path=tmp_path / "settings.json")
    app.withdraw()
    app.report_callback_exception = lambda *args: errors.append(args)
    try:
        entry = _named_widget(app, "quick_convert_entry")
        entry.insert(0, expression)
        _named_widget(app, "quick_convert_button").invoke()
        app.update()
        result = _named_widget(app, "quick_convert_result").cget("text")
        assert message in result.lower()
        assert errors == []
    finally:
        app.destroy()


def test_preferences_and_history_restore_after_close_and_reopen(tk_root, tmp_path):
    root, errors = tk_root
    path = tmp_path / "settings.json"
    app = build_main_window(settings_path=path)
    app.report_callback_exception = lambda *args: errors.append(args)
    try:
        _named_widget(app, "precision_spinbox").set("12")
        _named_widget(app, "scientific_notation").invoke()
        entry = _named_widget(app, "quick_convert_entry")
        entry.insert(0, "10 km in mi")
        _named_widget(app, "quick_convert_button").invoke()
        app.update()
        _close_window(app)

        reopened = build_main_window(settings_path=path)
        try:
            assert reopened.app_state.precision == 12
            assert reopened.app_state.use_scientific is True
            assert reopened.app_state.history[0].startswith("10 km in mi =")
            history = _named_widget(reopened, "history_text")
            assert "10 km in mi" in history.get("1.0", "end")
            assert errors == []
        finally:
            reopened.destroy()
    finally:
        if _is_alive(app):
            app.destroy()


def test_precision_spinbox_allows_clear_and_replace_before_commit(tk_root, tmp_path):
    _, errors = tk_root
    app = build_main_window(settings_path=tmp_path / "settings.json")
    app.report_callback_exception = lambda *args: errors.append(args)
    try:
        precision = _named_widget(app, "precision_spinbox")
        precision.delete(0, "end")
        app.update()

        assert precision.get() == ""
        assert app.app_state.precision == 6

        precision.insert(0, "12")
        app.update()
        assert precision.get() == "12"
        assert app.app_state.precision == 6

        precision.focus_force()
        app.update()
        precision.event_generate("<Return>")
        app.update()
        assert app.app_state.precision == 12
        assert errors == []
    finally:
        app.destroy()


def test_live_converter_records_only_the_final_value_after_idle(tk_root):
    root, errors = tk_root
    state = AppState()
    frame = angle.AngleConverter(root, lambda *_: None, state)
    frame.pack()

    _drive_converter(root, frame, "Radians", "Degrees", "1")
    input_field = next(
        widget
        for widget in _walk(frame)
        if isinstance(widget, ttk.Entry) and widget.cget("state") != "readonly"
    )
    input_field.insert("end", "0")
    root.update()

    assert state.history == []

    finished = tk.BooleanVar(master=root)
    root.after(600, lambda: finished.set(True))
    root.wait_variable(finished)

    assert len(state.history) == 1
    assert state.history[0].startswith("10 Radians =")
    assert errors == []


def test_close_flushes_pending_conversion_history_before_saving(tk_root, tmp_path):
    _, errors = tk_root
    path = tmp_path / "settings.json"
    app = build_main_window(settings_path=path)
    app.report_callback_exception = lambda *args: errors.append(args)
    try:
        notebook = _notebook(app)
        angle_frame = next(
            notebook.nametowidget(tab_id)
            for tab_id in notebook.tabs()
            if notebook.tab(tab_id, "text") == "Angle"
        )
        _drive_converter(app, angle_frame, "Radians", "Degrees", "90")

        assert app.app_state.history == []
        _close_window(app)

        reopened = build_main_window(settings_path=path)
        try:
            assert reopened.app_state.history == ["90 Radians = 5156.620156 Degrees"]
        finally:
            reopened.destroy()
        assert errors == []
    finally:
        if _is_alive(app):
            app.destroy()


def test_state_changes_debounce_settings_writes(tk_root, tmp_path, monkeypatch):
    _, errors = tk_root
    writes = []
    monkeypatch.setattr(
        app_module,
        "save_settings",
        lambda state, path: writes.append((state.precision, list(state.history))),
    )
    app = build_main_window(settings_path=tmp_path / "settings.json")
    app.report_callback_exception = lambda *args: errors.append(args)
    try:
        app.app_state.add_history("partial")
        app.app_state.add_history("final")

        assert writes == []

        finished = tk.BooleanVar(master=app)
        app.after(500, lambda: finished.set(True))
        app.wait_variable(finished)

        assert writes == [(6, ["final", "partial"])]
        assert errors == []
    finally:
        app.destroy()


def test_malformed_settings_are_preserved_when_opening_and_closing(tk_root, tmp_path):
    root, _ = tk_root
    path = tmp_path / "settings.json"
    original = "{broken settings"
    path.write_text(original)
    app = build_main_window(settings_path=path)
    try:
        assert app.app_state.precision == 6
        assert "invalid" in _status_text(app).lower()
        _close_window(app)
        assert path.read_text() == original
    finally:
        if _is_alive(app):
            app.destroy()


def test_failed_settings_write_keeps_conversion_available_and_reports_status(
    tk_root, tmp_path, monkeypatch
):
    root, errors = tk_root
    path = tmp_path / "settings.json"

    def fail_save(state, target):
        raise OSError("disk full")

    monkeypatch.setattr(app_module, "save_settings", fail_save, raising=False)
    app = build_main_window(settings_path=path)
    app.report_callback_exception = lambda *args: errors.append(args)
    try:
        entry = _named_widget(app, "quick_convert_entry")
        entry.insert(0, "10 km in mi")
        _named_widget(app, "quick_convert_button").invoke()
        app.update()
        assert "6.213712" in _named_widget(app, "quick_convert_result").cget("text")
        assert "could not be written" in _status_text(app).lower()
        assert app.winfo_exists()
        assert errors == []
    finally:
        app.destroy()


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


def test_packaged_smoke_test_mode_checks_all_tabs_and_exits(tk_root, capsys):
    result = app_module.main(["--smoke-test"])
    assert result == 0
    assert "14 converter tabs" in capsys.readouterr().out


def test_preferences_menu_focuses_precision_spinbox(tk_root, tmp_path):
    root, errors = tk_root
    app = build_main_window(settings_path=tmp_path / "settings.json")
    app.deiconify()
    app.focus_force()
    app.update()
    try:
        menubar = app.nametowidget(app.cget("menu"))
        # On macOS, Preferences is under the apple menu
        apple_menu = None
        for child in menubar.winfo_children():
            if child.winfo_name() == "apple":
                apple_menu = child
                break
        if apple_menu is not None:
            apple_menu.invoke(2)
            app.update()
            spin = _named_widget(app, "precision_spinbox")
            assert app.focus_get() == spin
        assert errors == []
    finally:
        app.destroy()


def test_clear_history_discards_pending_conversion_timer(tk_root, tmp_path):
    root, errors = tk_root
    app = build_main_window(settings_path=tmp_path / "settings.json")
    app.deiconify()
    app.update()
    try:
        nb = _notebook(app)
        nb.select(13)  # Cooking tab
        app.update()
        frame = nb.nametowidget(nb.select())
        combos = [w for w in _walk(frame) if isinstance(w, ttk.Combobox)]
        entries = [w for w in _walk(frame) if isinstance(w, ttk.Entry) and not isinstance(w, ttk.Combobox)]
        combos[0].set("Cup (US)")
        combos[1].set("Milliliter")
        entries[0].insert(0, "2")
        app.update()

        # Immediately invoke Clear History before the 500ms debounce timer
        clear_btn = next(
            w for w in _walk(app)
            if isinstance(w, ttk.Button) and w.cget("text") == "Clear History"
        )
        clear_btn.invoke()
        app.update()

        assert app.app_state.history == []
        # Wait past the debounce delay and check that history remains empty
        app.after(600, app.quit)
        app.mainloop()
        assert app.app_state.history == []
        assert errors == []
    finally:
        app.destroy()


def test_advertised_keyboard_shortcuts(tk_root, tmp_path):
    root, errors = tk_root
    app = build_main_window(settings_path=tmp_path / "settings.json")
    app.deiconify()
    app.focus_force()
    app.update()
    try:
        # Test tab reset shortcut
        app.event_generate("<Command-n>" if sys.platform == "darwin" else "<Control-n>")
        app.update()

        # Test copy result shortcut
        app.event_generate("<Command-Shift-C>" if sys.platform == "darwin" else "<Control-Shift-C>")
        app.update()

        # Test clear history shortcut
        app.event_generate("<Command-Shift-K>" if sys.platform == "darwin" else "<Control-Shift-K>")
        app.update()

        assert errors == []
    finally:
        app.destroy()

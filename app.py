"""Main application window and launcher for the Unit Converter desktop app."""

import argparse
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import tkinter as tk
from tkinter import ttk
import webbrowser

from src import (
    angle,
    area,
    cooking,
    data_rate,
    digital,
    fuel_economy,
    length,
    temperature,
    weight,
    volume,
    speed,
    time_converter,
    pressure,
    energy,
    quick_convert,
)
from src import brand
from src import utils
from src.app_state import AppState
from src.persistence import (
    load_settings,
    save_settings,
    settings_path as default_settings_path,
)


def init_style(root: tk.Tk, state: AppState) -> ttk.Style:
    """Create a polished native-feeling ttk style based on platform and brand palette."""
    style = ttk.Style(root)
    platform = sys.platform

    # Detect dark mode
    state.dark_mode = brand.detect_system_dark_mode()

    theme_candidates = []
    if platform == "darwin":
        theme_candidates = ["aqua", "clam"]
    elif platform.startswith("win"):
        theme_candidates = ["vista", "xpnative", "clam"]
    else:
        theme_candidates = ["clam", "default"]

    for theme in theme_candidates:
        if theme in style.theme_names():
            style.theme_use(theme)
            break

    # Typography according to Apple Human Interface Guidelines and platform norms
    if platform == "darwin":
        base_font = ("SF Pro Text", 12)
        title_font = ("SF Pro Display", 20, "bold")
        header_font = ("SF Pro Display", 15, "bold")
        sub_font = ("SF Pro Text", 10)
        result_font = ("SF Pro Text", 13, "bold")
        mono_font = ("SF Mono", 10)
    elif platform.startswith("win"):
        base_font = ("Segoe UI", 10)
        title_font = ("Segoe UI", 18, "bold")
        header_font = ("Segoe UI", 14, "bold")
        sub_font = ("Segoe UI", 9)
        result_font = ("Segoe UI", 11, "bold")
        mono_font = ("Consolas", 9)
    else:
        base_font = ("Noto Sans", 11)
        title_font = ("Noto Sans", 18, "bold")
        header_font = ("Noto Sans", 14, "bold")
        sub_font = ("Noto Sans", 9)
        result_font = ("Noto Sans", 12, "bold")
        mono_font = ("DejaVu Sans Mono", 9)

    root.base_font = base_font
    root.mono_font = mono_font

    # Color palette
    is_dark = state.dark_mode
    bg_color = brand.DARK_BG if is_dark else brand.LIGHT_BG
    muted_color = brand.DARK_TEXT_MUTED if is_dark else brand.LIGHT_TEXT_MUTED

    root.configure(bg=bg_color)

    style.configure("TFrame", padding=12)
    style.configure("TLabel", font=base_font)
    style.configure("TButton", padding=(10, 5), font=base_font)

    # Branded custom typography styles
    style.configure("Header.TLabel", font=header_font)
    style.configure("Subheader.TLabel", font=sub_font, foreground=muted_color)
    style.configure("BrandTitle.TLabel", font=title_font, foreground=brand.BRAND_ACCENT)
    style.configure("Result.TLabel", font=result_font, foreground=brand.BRAND_ACCENT)

    # Status bar styles
    style.configure("Success.TLabel", foreground=brand.COLOR_SUCCESS, font=base_font)
    style.configure("Error.TLabel", foreground=brand.COLOR_ERROR, font=base_font)
    style.configure("Info.TLabel", foreground=muted_color, font=base_font)

    # Interactive accents
    style.map("TButton", relief=[("active", "groove")])

    return style


def setup_menu_bar(root: tk.Tk, notebook: ttk.Notebook, show_about_dialog,
                   do_reset_tab, do_swap_tab, do_copy_tab_result,
                   do_focus_quick, do_focus_preferences, do_clear_history, do_close_window):
    """Build a functional macOS / cross-platform system menu bar."""
    is_mac = sys.platform == "darwin"
    menubar = tk.Menu(root)

    # 1. macOS Application Menu
    if is_mac:
        app_menu = tk.Menu(menubar, name="apple", tearoff=0)
        menubar.add_cascade(menu=app_menu)
        app_menu.add_command(label="About Unit Converter", command=show_about_dialog)
        app_menu.add_separator()
        app_menu.add_command(label="Preferences...", accelerator="Cmd+,",
                             command=do_focus_preferences)
        app_menu.add_separator()
        app_menu.add_command(label="Hide Unit Converter", accelerator="Cmd+H",
                             command=lambda: root.tk.call("wm", "iconify", root._w))
        app_menu.add_command(label="Hide Others", accelerator="Option+Cmd+H",
                             command=brand.hide_other_applications)
        app_menu.add_command(label="Show All", command=brand.unhide_all_applications)
        app_menu.add_separator()
        app_menu.add_command(label="Quit Unit Converter", accelerator="Cmd+Q", command=do_close_window)

    # 2. File Menu
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="New Conversion", accelerator="Cmd+N" if is_mac else "Ctrl+N",
                          command=do_reset_tab)
    file_menu.add_command(label="Clear Current Tab", accelerator="Cmd+K" if is_mac else "Ctrl+K",
                          command=do_reset_tab)
    file_menu.add_separator()
    file_menu.add_command(label="Close Window", accelerator="Cmd+W" if is_mac else "Ctrl+W",
                          command=do_close_window)

    # 3. Edit Menu
    edit_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Edit", menu=edit_menu)

    def trigger_virtual_event(event_name):
        focused = root.focus_get()
        if focused:
            try:
                focused.event_generate(event_name)
            except Exception:
                pass

    edit_menu.add_command(label="Undo", accelerator="Cmd+Z" if is_mac else "Ctrl+Z",
                          command=lambda: trigger_virtual_event("<<Undo>>"))
    edit_menu.add_command(label="Redo", accelerator="Shift+Cmd+Z" if is_mac else "Ctrl+Y",
                          command=lambda: trigger_virtual_event("<<Redo>>"))
    edit_menu.add_separator()
    edit_menu.add_command(label="Cut", accelerator="Cmd+X" if is_mac else "Ctrl+X",
                          command=lambda: trigger_virtual_event("<<Cut>>"))
    edit_menu.add_command(label="Copy", accelerator="Cmd+C" if is_mac else "Ctrl+C",
                          command=lambda: trigger_virtual_event("<<Copy>>"))
    edit_menu.add_command(label="Paste", accelerator="Cmd+V" if is_mac else "Ctrl+V",
                          command=lambda: trigger_virtual_event("<<Paste>>"))
    edit_menu.add_command(label="Select All", accelerator="Cmd+A" if is_mac else "Ctrl+A",
                          command=lambda: trigger_virtual_event("<<SelectAll>>"))
    edit_menu.add_separator()
    edit_menu.add_command(label="Swap Units", accelerator="Cmd+S" if is_mac else "Ctrl+S",
                          command=do_swap_tab)
    edit_menu.add_command(label="Copy Result", accelerator="Shift+Cmd+C" if is_mac else "Ctrl+Shift+C",
                          command=do_copy_tab_result)

    # 4. View Menu
    view_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="View", menu=view_menu)
    view_menu.add_command(label="Focus Quick Convert", accelerator="Cmd+L" if is_mac else "Ctrl+L",
                          command=do_focus_quick)
    view_menu.add_separator()

    def select_next_tab():
        tabs = notebook.tabs()
        if tabs:
            curr = notebook.index("current")
            notebook.select((curr + 1) % len(tabs))

    def select_prev_tab():
        tabs = notebook.tabs()
        if tabs:
            curr = notebook.index("current")
            notebook.select((curr - 1) % len(tabs))

    view_menu.add_command(label="Next Category", accelerator="Ctrl+Tab", command=select_next_tab)
    view_menu.add_command(label="Previous Category", accelerator="Ctrl+Shift+Tab", command=select_prev_tab)
    view_menu.add_separator()

    category_menu = tk.Menu(view_menu, tearoff=0)
    view_menu.add_cascade(label="Categories", menu=category_menu)
    for idx in range(14):
        tab_name = notebook.tab(idx, "text")
        shortcut = f"Cmd+{idx+1}" if is_mac and idx < 9 else (f"Ctrl+{idx+1}" if idx < 9 else "")
        category_menu.add_command(label=tab_name, accelerator=shortcut,
                                  command=lambda i=idx: notebook.select(i))

    # 5. History Menu
    history_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="History", menu=history_menu)
    history_menu.add_command(label="Clear History", accelerator="Shift+Cmd+K" if is_mac else "Ctrl+Shift+K",
                             command=do_clear_history)

    # 6. Window Menu
    if is_mac:
        window_menu = tk.Menu(menubar, name="window", tearoff=0)
        menubar.add_cascade(label="Window", menu=window_menu)
        window_menu.add_command(label="Minimize", accelerator="Cmd+M", command=root.iconify)
        window_menu.add_command(label="Zoom", command=lambda: root.wm_state("zoomed") if root.wm_state() != "zoomed" else root.wm_state("normal"))

    # 7. Help Menu
    help_menu = tk.Menu(menubar, name="help" if is_mac else None, tearoff=0)
    menubar.add_cascade(label="Help", menu=help_menu)

    def open_docs():
        docs_path = Path(__file__).resolve().parent / "docs" / "unit-definitions.md"
        if docs_path.is_file():
            webbrowser.open(docs_path.as_uri())
        else:
            webbrowser.open("https://github.com/palaashatri/unitconverter-tk#readme")

    def open_github():
        webbrowser.open("https://github.com/palaashatri/unitconverter-tk")

    help_menu.add_command(label="Unit Definitions & Conventions", command=open_docs)
    help_menu.add_command(label="GitHub Repository", command=open_github)
    if not is_mac:
        help_menu.add_separator()
        help_menu.add_command(label="About Unit Converter", command=show_about_dialog)

    root.config(menu=menubar)
    return menubar


def build_main_window(settings_path: Path | str | None = None) -> tk.Tk:
    path = Path(settings_path) if settings_path is not None else default_settings_path()
    state, settings_warning = load_settings(path)
    root = tk.Tk()
    root.app_state = state
    root.settings_path = path
    root.title("Unit Converter")
    root.minsize(920, 600)
    root.geometry("980x640")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    # Apply cross-platform brand application icon (macOS Dock, Windows ICO, Tk iconphoto)
    brand.apply_app_icon(root)

    init_style(root, state)

    main_container = ttk.Frame(root)
    main_container.grid(row=0, column=0, sticky="nsew")
    main_container.columnconfigure(0, weight=1)
    main_container.rowconfigure(0, weight=1)

    # Left: converter area
    left_panel = ttk.Frame(main_container, padding=16)
    left_panel.grid(row=0, column=0, sticky="nsew")
    left_panel.columnconfigure(0, weight=1)
    left_panel.rowconfigure(2, weight=1)

    # Right: history & settings panel
    right_panel = ttk.Frame(main_container, padding=16, width=270)
    right_panel.grid(row=0, column=1, sticky="nsew")
    right_panel.grid_propagate(False)

    # Header with sculpted 3D brand logo, typography, and About button
    header = ttk.Frame(left_panel)
    header.grid(row=0, column=0, sticky="ew")
    header.columnconfigure(1, weight=1)

    brand_icon_photo = brand.get_brand_photo(32, master=root)
    if brand_icon_photo:
        icon_label = ttk.Label(header, image=brand_icon_photo)
        icon_label.image = brand_icon_photo
        icon_label.grid(row=0, column=0, rowspan=2, padx=(0, 10), sticky="w")

    title_box = ttk.Frame(header)
    title_box.grid(row=0, column=1, rowspan=2, sticky="w")
    ttk.Label(title_box, text="Unit Converter", style="Header.TLabel").pack(anchor="w")
    ttk.Label(
        title_box,
        text="14 measurement categories · Instant conversion",
        style="Subheader.TLabel",
    ).pack(anchor="w")

    def show_about():
        about_window = tk.Toplevel(root)
        about_window.title("About Unit Converter")
        about_window.resizable(True, True)
        about_window.transient(root)
        about_window.grab_set()

        content = ttk.Frame(about_window, padding=24)
        content.pack(fill="both", expand=True)

        logo_128 = brand.get_brand_photo(128, master=about_window)
        if logo_128:
            img_lbl = ttk.Label(content, image=logo_128)
            img_lbl.image = logo_128
            img_lbl.pack(pady=(0, 10))

        ttk.Label(content, text="Unit Converter", style="Header.TLabel").pack(pady=(0, 2))
        version = os.environ.get("UNITCONVERTER_VERSION", "2.0.0")
        ttk.Label(content, text=f"Version {version}", style="Subheader.TLabel").pack(pady=(0, 10))

        ttk.Label(
            content,
            text="A precision cross-platform conversion tool featuring 14 measurement categories, natural-language quick conversion, and local settings persistence.",
            wraplength=380,
            justify="center",
        ).pack(pady=(0, 10))

        ttk.Label(content, text="Designed by Palaash Atri", font=("", 10, "bold")).pack(pady=(0, 2))
        ttk.Label(content, text="© 2026 All Rights Reserved", style="Subheader.TLabel").pack(pady=(0, 14))

        btn_row = ttk.Frame(content)
        btn_row.pack(fill="x", pady=(10, 0))
        ttk.Button(btn_row, text="OK", command=about_window.destroy, width=10).pack(side="right", padx=5)

        # Center the window dynamically based on required content size
        about_window.update_idletasks()
        req_w = max(440, content.winfo_reqwidth() + 48)
        req_h = max(440, content.winfo_reqheight() + 48)
        about_window.minsize(420, 380)
        x = (about_window.winfo_screenwidth() // 2) - (req_w // 2)
        y = (about_window.winfo_screenheight() // 2) - (req_h // 2)
        about_window.geometry(f"{req_w}x{req_h}+{x}+{y}")

    ttk.Button(header, text="About", command=show_about, width=8).grid(
        row=0, column=2, rowspan=2, sticky="e", padx=5
    )

    status_var = tk.StringVar(master=root, value="Select a tab to start")
    status_style = tk.StringVar(master=root, value="Info.TLabel")

    def update_status(msg: str, style: str = "info"):
        status_var.set(msg)
        if style == "success":
            status_style.set("Success.TLabel")
        elif style == "error":
            status_style.set("Error.TLabel")
        else:
            status_style.set("Info.TLabel")

    settings_dirty = False
    settings_write_after_id = None

    def cancel_scheduled_settings_write():
        nonlocal settings_write_after_id
        if settings_write_after_id is not None:
            root.after_cancel(settings_write_after_id)
            settings_write_after_id = None

    def persist_settings(mark_dirty=True):
        nonlocal settings_dirty
        cancel_scheduled_settings_write()
        if mark_dirty:
            settings_dirty = True
        try:
            save_settings(state, path)
        except OSError:
            update_status(
                "Saved settings could not be written; conversions remain available.",
                "error",
            )
            return False
        return True

    def flush_scheduled_settings_write():
        nonlocal settings_write_after_id
        settings_write_after_id = None
        persist_settings(mark_dirty=False)

    def schedule_settings_write():
        nonlocal settings_dirty, settings_write_after_id
        settings_dirty = True
        cancel_scheduled_settings_write()
        settings_write_after_id = root.after(400, flush_scheduled_settings_write)

    state.on_change = schedule_settings_write

    # Quick convert frame
    quick_frame = ttk.Frame(left_panel)
    quick_frame.grid(row=1, column=0, sticky="ew", pady=(12, 0))
    quick_frame.columnconfigure(1, weight=1)
    ttk.Label(quick_frame, text="Type to convert:").grid(
        row=0, column=0, sticky="w", padx=(0, 8)
    )
    quick_expression = tk.StringVar(master=root)
    quick_entry = ttk.Entry(
        quick_frame, textvariable=quick_expression, name="quick_convert_entry"
    )
    quick_entry.grid(row=0, column=1, sticky="ew")
    quick_result = tk.StringVar(master=root, value="Example: 10 km in mi")
    quick_result_label = ttk.Label(
        quick_frame, textvariable=quick_result, name="quick_convert_result"
    )
    quick_result_label.grid(row=1, column=1, sticky="w", pady=(3, 0))

    def convert_quick(event=None):
        expression = quick_expression.get().strip()
        try:
            result = quick_convert.convert_expression(expression)
            precision = state.precision
            formatted = utils.format_number(
                result.value, precision, state.use_scientific
            )
        except (OverflowError, ValueError) as error:
            quick_result.set(str(error))
            update_status(str(error), "error")
            return "break"

        quick_result.set(f"{formatted} {result.target_label}")
        update_status("✓ Quick conversion complete", "success")
        state.add_history(
            f"{expression} = {formatted} {result.target_label}"
        )
        persist_settings()
        if hasattr(state, "update_history_display"):
            state.update_history_display()
        return "break"

    ttk.Button(
        quick_frame,
        text="Convert",
        name="quick_convert_button",
        command=convert_quick,
    ).grid(row=0, column=2, padx=(8, 0))
    quick_entry.bind("<Return>", convert_quick)
    ttk.Label(
        quick_frame,
        text="Examples: 10 km in mi  ·  72 F to C  ·  100 psi to bar",
        style="Subheader.TLabel",
    ).grid(row=2, column=1, sticky="w", pady=(2, 0))

    notebook = ttk.Notebook(left_panel)
    notebook.grid(row=2, column=0, sticky="nsew", pady=(12, 0))

    # Create all converter tabs with state reference
    converters = [
        (temperature.TemperatureConverter(notebook, update_status, state), "Temperature"),
        (length.LengthConverter(notebook, update_status, state), "Length"),
        (area.AreaConverter(notebook, update_status, state), "Area"),
        (digital.DigitalConverter(notebook, update_status, state), "Digital"),
        (weight.WeightConverter(notebook, update_status, state), "Weight"),
        (volume.VolumeConverter(notebook, update_status, state), "Volume"),
        (speed.SpeedConverter(notebook, update_status, state), "Speed"),
        (time_converter.TimeConverter(notebook, update_status, state), "Time"),
        (pressure.PressureConverter(notebook, update_status, state), "Pressure"),
        (energy.EnergyConverter(notebook, update_status, state), "Energy"),
        (angle.AngleConverter(notebook, update_status, state), "Angle"),
        (data_rate.DataRateConverter(notebook, update_status, state), "Data rate"),
        (fuel_economy.FuelEconomyConverter(notebook, update_status, state), "Fuel economy"),
        (cooking.CookingConverter(notebook, update_status, state), "Cooking"),
    ]

    for frame, text in converters:
        notebook.add(frame, text=text)
    root.converter_tab_labels = tuple(
        notebook.tab(tab_id, "text") for tab_id in notebook.tabs()
    )

    status_bar = ttk.Label(
        left_panel, textvariable=status_var, anchor="w", name="status_bar"
    )
    status_bar.grid(row=3, column=0, sticky="ew", pady=(10, 0))
    status_bar.configure(style=status_style.get())

    # Update status bar style when it changes
    def update_status_bar_style(*args):
        status_bar.configure(style=status_style.get())
    status_style.trace_add("write", update_status_bar_style)

    # Settings panel
    settings_frame = ttk.LabelFrame(right_panel, text="Settings", padding=10)
    settings_frame.pack(fill="x", pady=(0, 10))

    ttk.Label(settings_frame, text="Decimal Places:").pack(anchor="w")
    precision_var = tk.StringVar(master=root, value=str(state.precision))

    def commit_precision(event=None):
        raw_value = precision_var.get().strip()
        try:
            value = int(raw_value)
        except ValueError:
            update_status(
                "Decimal places must be a whole number from 0 to 15.", "error"
            )
            precision_var.set(str(state.precision))
            return "break" if event is not None else None

        bounded = min(15, max(0, value))
        if bounded != value:
            update_status("Decimal places must be from 0 to 15.", "error")
            value = bounded
        precision_var.set(str(value))
        if state.precision != value:
            state.precision = value
            persist_settings()
        return "break" if event is not None else None

    precision_spin = ttk.Spinbox(
        settings_frame,
        from_=0,
        to=15,
        textvariable=precision_var,
        command=commit_precision,
        width=10,
        name="precision_spinbox",
    )
    precision_spin.pack(anchor="w", pady=(2, 8))
    precision_spin.bind("<Return>", commit_precision)
    precision_spin.bind("<FocusOut>", commit_precision)

    sci_var = tk.BooleanVar(master=root, value=state.use_scientific)

    def update_scientific():
        state.use_scientific = sci_var.get()
        persist_settings()

    ttk.Checkbutton(
        settings_frame,
        text="Scientific notation",
        variable=sci_var,
        command=update_scientific,
        name="scientific_notation",
    ).pack(anchor="w")

    # History panel
    history_frame = ttk.LabelFrame(right_panel, text="Recent Conversions", padding=10)
    history_frame.pack(fill="both", expand=True)

    history_top = ttk.Frame(history_frame)
    history_top.pack(fill="x", pady=(0, 4))

    def clear_history_action():
        for cancel_fn in tuple(getattr(root, "_pending_history_cancelers", ())):
            try:
                cancel_fn()
            except Exception:
                pass
        state.history.clear()
        persist_settings()
        update_history()
        update_status("Cleared conversion history", "info")

    ttk.Button(
        history_top,
        text="Clear History",
        command=clear_history_action,
        width=12,
    ).pack(side="right")

    history_mono = ("SF Mono", 9) if sys.platform == "darwin" else ("Courier", 9)
    history_text = tk.Text(
        history_frame,
        height=14,
        width=30,
        wrap="word",
        state="disabled",
        font=history_mono,
        name="history_text",
    )
    history_text.pack(fill="both", expand=True)

    def update_history():
        history_text.configure(state="normal")
        history_text.delete(1.0, "end")
        for entry in state.history:
            history_text.insert("end", entry + "\n\n")
        history_text.configure(state="disabled")

    state.update_history_display = update_history
    update_history()

    if settings_warning:
        update_status(settings_warning, "error")

    # Current tab helpers for menu commands
    def get_current_frame():
        tab_id = notebook.select()
        if tab_id:
            return notebook.nametowidget(tab_id)
        return None

    def reset_current_tab():
        frame = get_current_frame()
        if frame and hasattr(frame, "reset_tab"):
            frame.reset_tab()
        else:
            update_status("Reset current tab", "info")

    def swap_current_tab():
        frame = get_current_frame()
        if frame and hasattr(frame, "swap_units"):
            frame.swap_units()
        else:
            update_status("Swap not supported on this category", "info")

    def copy_current_result():
        frame = get_current_frame()
        if frame and hasattr(frame, "copy_result"):
            frame.copy_result()

    def focus_preferences():
        precision_spin.focus_set()
        try:
            precision_spin.selection_range(0, "end")
        except Exception:
            pass

    def focus_quick():
        quick_entry.focus_set()
        quick_entry.select_range(0, "end")

    def close_window():
        for flush_pending_history in tuple(
            getattr(root, "_pending_history_flushers", ())
        ):
            flush_pending_history()
        commit_precision()
        if not (settings_warning and not settings_dirty):
            persist_settings(mark_dirty=False)
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", close_window)

    # Setup native macOS / cross-platform menu bar
    setup_menu_bar(
        root=root,
        notebook=notebook,
        show_about_dialog=show_about,
        do_reset_tab=reset_current_tab,
        do_swap_tab=swap_current_tab,
        do_copy_tab_result=copy_current_result,
        do_focus_quick=focus_quick,
        do_focus_preferences=focus_preferences,
        do_clear_history=clear_history_action,
        do_close_window=close_window,
    )

    # Platform-specific modifier key
    mod_key = "Command" if sys.platform == "darwin" else "Control"

    root.bind(f"<{mod_key}-w>", lambda e: close_window())
    root.bind(f"<{mod_key}-q>", lambda e: close_window())
    root.bind(f"<{mod_key}-s>", lambda e: swap_current_tab())
    root.bind(f"<{mod_key}-k>", lambda e: reset_current_tab())
    root.bind(f"<{mod_key}-n>", lambda e: reset_current_tab())
    root.bind(f"<{mod_key}-l>", lambda e: focus_quick())
    root.bind(f"<{mod_key}-comma>", lambda e: focus_preferences())
    root.bind(f"<{mod_key}-Shift-C>", lambda e: copy_current_result())
    root.bind(f"<{mod_key}-Shift-c>", lambda e: copy_current_result())
    root.bind(f"<{mod_key}-Shift-K>", lambda e: clear_history_action())
    root.bind(f"<{mod_key}-Shift-k>", lambda e: clear_history_action())
    for i in range(10):
        root.bind(f"<{mod_key}-{i}>", lambda e, idx=i-1: notebook.select(idx if idx >= 0 else 9))

    return root


def run_smoke_test() -> int:
    """Start the Tk app, verify all category tabs, and exit without persistence."""
    with TemporaryDirectory(prefix="unitconverter-smoke-") as temp_directory:
        app = build_main_window(Path(temp_directory) / "settings.json")
        try:
            app.update()
            if len(app.converter_tab_labels) != 14:
                raise RuntimeError(
                    f"Expected 14 converter tabs, found {len(app.converter_tab_labels)}"
                )
            print(f"Smoke test passed: {len(app.converter_tab_labels)} converter tabs")
        finally:
            app.destroy()
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Unit Converter")
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    args = parser.parse_args(argv)
    if args.smoke_test:
        return run_smoke_test()

    app = build_main_window()
    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())

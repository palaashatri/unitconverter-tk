# Desktop Experience Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make conversions easier to discover, remember user preferences/history between runs, and expose all four new categories in the Tkinter app.

**Architecture:** `src/app_state.py` holds validated runtime preferences and history; `src/persistence.py` reads/writes versioned local JSON. A pure `src/quick_convert.py` parser resolves an expression through a canonical unit registry and existing conversion modules. Tkinter stays at the UI boundary.

**Tech Stack:** Python standard library (`dataclasses`, `json`, `pathlib`, `re`, `tempfile`, `os`), Tkinter/ttk, pytest.

**Spec:** [2026-10-25-unitconverter-production-readiness-design.md](../specs/2026-10-25-unitconverter-production-readiness-design.md)

## Global Constraints

- Store no user data outside the local per-user application-data directory and use no network service.
- Save precision, scientific notation, and at most ten recent conversions in versioned JSON using atomic replacement.
- Missing or malformed settings must not prevent the app from starting or erase unreadable data.
- The parser accepts `10 km in mi` and `72 F to C`; ambiguity and unknown units produce actionable status text.
- Keep conversion math in pure `src/convert_*.py` modules; Tk callbacks must not leak invalid-input exceptions.
- Keep the current native Tkinter layout and tab workflow; add only the global expression field and four category tabs.

## Review Focus

- A malformed or future-version settings file must leave the file intact and start with safe defaults.
- A settings directory that cannot be created/written must leave the app usable and show a concise status.
- The expression `72 F to C` must resolve temperature, while `10 km in mi` resolves length; unknown or ambiguous unit aliases must fail clearly.
- Zero/negative fuel economy and below-zero Kelvin input must be rejected in both tab and expression entry paths.
- The app must start, show all fourteen tabs, restore precision/scientific notation/history, and shut down cleanly after a restart.

---

### Task 1: Create app settings model and persistent storage

**Files:**
- Create: `src/app_state.py`
- Create: `src/persistence.py`
- Create: `test/test_persistence.py`

**Interfaces:**
- Produces: `AppState(precision: int = 6, use_scientific: bool = False, history: list[str] = field(default_factory=list))`, `add_history(entry: str) -> None`; `settings_path(environ: Mapping[str, str] | None = None, home: Path | None = None, platform: str | None = None) -> Path`; `load_settings(path: Path) -> tuple[AppState, str | None]`; `save_settings(state: AppState, path: Path) -> None`.
- Consumes: None.

- [x] **Step 1: Write failing tests** for defaults, settings serialization/reload, history capped at ten newest strings, precision clamped to 0–15, malformed JSON/future version preserving the file and returning defaults plus a warning, and atomic write failure preserving the prior complete file.
- [x] **Step 2: Run** `pytest test/test_persistence.py -q`; expect import/API failures.
- [x] **Step 3: Implement** XDG config path on Linux, `~/Library/Application Support/UnitConverter/settings.json` on macOS, and `%LOCALAPPDATA%/UnitConverter/settings.json` on Windows. Use a versioned JSON schema; write a sibling temporary file and `Path.replace`. Treat absent files as clean defaults; catch malformed/inaccessible reads into `(defaults, warning)` without modifying the original.
- [x] **Step 4: Run** `pytest test/test_persistence.py -q`; expect all storage and recovery checks to pass.
- [x] **Step 5: Commit** `feat: persist local settings and history`.

### Task 2: Build a canonical unit registry and quick-expression parser

**Files:**
- Create: `src/unit_registry.py`
- Create: `src/quick_convert.py`
- Create: `test/test_quick_convert.py`

**Interfaces:**
- Produces: immutable `UnitRef(category: str, code: str, label: str)`, `ParsedExpression(amount: float, source: UnitRef, target: UnitRef)`, `ConversionResult(value: float, source_label: str, target_label: str)`, `parse_expression(text: str) -> ParsedExpression`, `convert_expression(text: str) -> ConversionResult`.
- Consumes: all converter modules and their canonical codes from [Conversion Reliability](2026-10-25-conversion-reliability.md).

- [x] **Step 1: Write failing tests** for both README examples and expected results (`10 km in mi` ≈ 6.213711922, `72 F to C` = 22.222222…), case-insensitive full names and aliases, case-sensitive data-rate symbols that distinguish bits from bytes, scientific notation and signed finite amounts, missing/malformed syntax, unknown units, cross-category pairs such as `10 m to min`, and `-1 K to C` rejection.
- [x] **Step 2: Run** `pytest test/test_quick_convert.py -q`; expect missing module/API failures.
- [x] **Step 3: Implement** a registry with explicit normalized aliases for every displayed unit, mapping each alias to one category/code/label. Assign all cooking-volume aliases to the canonical `volume` category and `convert_volume` function, even though the Cooking tab displays only the kitchen subset. Parse a finite numeric token followed by a source unit, `to` or `in`, and a target unit. Require each unit to resolve uniquely and require both units to share a category; convert via that category's pure `convert` function.
- [x] **Step 4: Run** `pytest test/test_quick_convert.py -q`; expect exact supported examples and clear `ValueError` messages for invalid or ambiguous text.
- [x] **Step 5: Commit** `feat: parse quick conversion expressions`.

### Task 3: Add UI tabs for new conversion categories

**Files:**
- Create: `src/angle.py`, `src/data_rate.py`, `src/fuel_economy.py`, `src/cooking.py`
- Modify: `app.py`
- Create: `test/test_gui.py`

**Interfaces:**
- Produces: `AngleConverter(parent, on_status=None, state=None)`, `DataRateConverter(...)`, `FuelEconomyConverter(...)`, `CookingConverter(...)`, each returning a `ttk.Frame` like the current category modules.
- Consumes: conversion functions in Plan 1; `AppState` from Task 1.

- [x] **Step 1: Write failing GUI tests** that build the main window and assert the fourteen expected category tabs and their display labels; drive one representative conversion in each new tab; parameterize blank, nonnumeric, NaN, infinity, and below-absolute-zero Kelvin inputs across the relevant tabs, asserting actionable feedback and no `report_callback_exception`.
- [x] **Step 2: Run** `xvfb-run -a pytest test/test_gui.py -q` on Linux; expect missing tab and module failures. (`xvfb-run` is unavailable here; the equivalent suite ran against Xorg `:99`.)
- [x] **Step 3: Implement** the four category frames following the established labels/from/to/output/reset/status conventions. Add the frames to `app.py` with visible labels `Angle`, `Data rate`, `Fuel economy`, and `Cooking`.
- [x] **Step 4: Run** GUI tests on a virtual display (Linux) or native display (Windows/macOS); expect fourteen tabs and functional conversion/validation. (26 GUI tests, 151 total tests, fatal Flake8 0.)
- [x] **Step 5: Commit** `feat: add the four new converter tabs`.

### Task 4: Add the global type-to-convert field

**Files:**
- Modify: `app.py`
- Modify: `test/test_gui.py`

**Interfaces:**
- Consumes: `convert_expression` and `ConversionResult` from Task 2.
- Produces: expression entry and Convert action that display result/status and append successful conversions through `AppState.add_history`.

- [x] **Step 1: Write failing GUI tests** entering `10 km in mi` and `72 F to C`, invoking Return and the Convert button, asserting displayed result/status and one history entry each; test unknown/ambiguous expressions and ensure no Tk callback exception.
- [x] **Step 2: Run** `xvfb-run -a pytest test/test_gui.py -q`; expect expression widgets and callbacks to be absent. (`xvfb-run` is unavailable here; tested on Xorg `:99`.)
- [x] **Step 3: Implement** a labelled field near the app title, a hint showing a supported example, Convert button, Return binding, a visible result label, and concise actionable error/status feedback. Both inputs use the same parser API; append successful results to history.
- [x] **Step 4: Run** the GUI tests; expect both examples, validation, and history updates to pass. (GUI+parser tests 50 passed; full suite 157 passed; fatal Flake8 0.)
- [x] **Step 5: Commit** `feat: add type-to-convert input`.

### Task 5: Connect settings and history to the running app

**Files:**
- Modify: `app.py`, `src/app_state.py`, and converter UI callbacks where required
- Modify: `test/test_gui.py`, `test/test_persistence.py`

**Interfaces:**
- Consumes: `load_settings`, `save_settings`, and `AppState` from Task 1.
- Produces: startup restore; save on setting/history changes and window close; status warnings on persistence failure.

- [x] **Step 1: Write failing integration tests** that open, change precision/scientific notation, add history, close, and reopen the app against a temporary settings path; assert values and history restore. Simulate malformed files and write errors and assert the app remains usable.
- [x] **Step 2: Run** `xvfb-run -a pytest test/test_gui.py -q`; expect settings to reset between app instances. (Expected failures confirmed; `xvfb-run` is unavailable here, so tests ran on Xorg `:99`.)
- [x] **Step 3: Implement** an injectable settings path for tests, load state before constructing tabs, update the history Text from loaded state, save after settings changes and successful conversions, and save on `WM_DELETE_WINDOW`. Surface storage warnings without stopping conversion.
- [x] **Step 4: Run** GUI and persistence suites; expect restart persistence and graceful failures. (44 passed.)
- [x] **Step 5: Run** `xvfb-run -a pytest -q`; expect all math, parser, storage, and GUI tests to pass together. (Equivalent suite on Xorg `:99`: 160 passed; fatal Flake8 0.)
- [x] **Step 6: Commit** `feat: restore app preferences and history on startup`.

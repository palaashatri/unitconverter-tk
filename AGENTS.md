# AGENTS.md — unitconverter-tk

A small Python 3 Tkinter unit converter (length, area, volume, weight, temperature, time, speed, pressure, energy, digital storage) with native look-and-feel on Windows and macOS. Entry point: `app.py`.

## Commands

```bash
python3 app.py                                  # run (needs Tk: python3-tk on Debian/Ubuntu)
pip install pytest flake8
pytest                                          # 5 tests in test/test_pytest.py
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics   # what CI enforces
pyinstaller --onefile --name unitconverter app.py                      # what the release workflow builds
```

## Layout

| Path | Contents |
|---|---|
| `app.py` | Main window, notebook of converter tabs, status bar |
| `src/convert_<kind>.py` | **Pure** conversion functions. Most use a `factors` table to a base unit and `convert(amount, from, to)`; temperature has explicit formulas |
| `src/<kind>.py` | The Tk frame for that converter (inputs, unit pickers, live conversion) |
| `src/utils.py` | Shared UI helpers |
| `test/test_pytest.py` | Tests (currently one assertion per module for 5 of 10 modules) |
| `.github/workflows/` | pytest, flake8, coverage; cross-platform PyInstaller/py2app release (triggered by the *Auto Tag* workflow, which is currently disabled in GitHub) |

## Known issues (2026-10-20)

- Weight unit keys don't follow SI symbols: in `convert_weight.factors`, `'dg'` means decagram (SI symbol `dag`) and `'deg'` means decigram (SI symbol `dg`). The UI labels in `src/weight.py` are correct, but code or tests that pass `'dg'` get the wrong unit. Rename to `dag`/`dg` together with the UI mapping.
- `mi` uses 1609.34 m; the exact international mile is 1609.344 m. Check other factors against exact definitions (NIST SP 811) when touching them.
- `convert_temp.covert_celToKel` is misspelled (`covert`); the test calls the misspelled name.
- Only 5 of 10 converters have tests; temperature tests compare floats with `==`.
- Workflows use deprecated `actions/checkout@v2` / `actions/setup-python@v2` and Python 3.9 (end of life); README badges pointed at the old repository name `unitconverter-py` (fixed 2026-10-20).

## Rules

- Keep conversion maths in `src/convert_*.py`, free of Tk imports, so it stays testable. UI modules only parse input, call `convert`, and format output.
- Every unit you add or change gets a test against an exact reference value, using `pytest.approx`.
- Round-trip property: `convert(convert(x, a, b), b, a) ≈ x` for every unit pair — keep a test for it.
- Invalid input (empty, non-numeric) shows a status message and never raises into Tk.

## Git workflow

Branch, run `pytest` and the flake8 command, and open a PR unless the owner asks for a direct push. If the *Auto Tag* workflow is re-enabled, every push to `main` creates a new tag and a release build.

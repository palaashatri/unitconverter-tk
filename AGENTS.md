# AGENTS.md — unitconverter-tk

A Python 3.12+ Tkinter desktop unit converter with fourteen categories: temperature, length, area, digital storage, weight, volume, speed, time, pressure, energy, angle, data rate, fuel economy, and cooking-volume measures. Entry point: `app.py`.

## Commands

```bash
python3.12 -m venv .venv
source .venv/bin/activate                 # Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python app.py
pytest -q
pytest --cov=. --cov-report=term --cov-report=xml
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
actionlint .github/workflows/*.yml .github/workflows/*.yaml
python -m pip install -r requirements-build.txt
python -m PyInstaller --clean --onefile --name unitconverter app.py
python setup-macos.py py2app
```

Linux GUI tests need a display; headless runs use `xvfb-run -a pytest -q`. Tkinter must be installed for the Python version being used (for example, `python3.12-tk` on Ubuntu 24.04).

## Layout

| Path | Contents |
|---|---|
| `app.py` | Main window, fourteen tabs, quick conversion, settings, history, and smoke-test entry point |
| `src/convert_*.py` | Pure conversion functions and unit factors; no Tk imports |
| `src/<kind>.py` | Tk frames for existing and added categories |
| `src/converter_ui.py` | Shared UI for simple factor-based converter tabs |
| `src/unit_registry.py`, `src/quick_convert.py` | Canonical aliases, expression parser, and conversion dispatch |
| `src/app_state.py`, `src/persistence.py` | Runtime preferences, bounded history, and atomic local settings storage |
| `docs/unit-definitions.md` | Unit bases, defining conventions, and references |
| `test/` | Conversion reference/round-trip, parser, persistence, GUI, release, and documentation tests |
| `.github/workflows/ci.yml` | Python 3.12 tests, Xvfb GUI run, coverage artifact, fatal lint, and actionlint |
| `.github/workflows/auto-tag.yaml`, `release-tag.yml`, `cross-platform-release.yml` | Main-branch versioning, manual tag release, native signed builds, smoke tests, and gated publication |

## Resolved issues

- Mass codes follow SI: `dag` is decagram and `dg` is decigram. `deg` remains a compatibility alias for decigram; the old incorrect `dg` decagram meaning changed.
- The international mile is exactly 1609.344 metres. Square millimetres use `sqmm`; `mm` remains a compatibility alias.
- `convert_celToKel` is the correctly spelled temperature function; `covert_celToKel` remains a forwarding compatibility alias.
- Every supported unit has reference-value coverage and every ordered unit pair has round-trip coverage. Temperature comparisons use `pytest.approx`.
- GitHub Actions use maintained action versions and Python 3.12. Tests, GUI, coverage, lint, and workflow validation run from the consolidated CI workflow.

## Rules

- Keep conversion math in pure `src/convert_*.py` modules. UI modules parse input, call converters, and format output.
- Add a `pytest.approx` reference test for each new or changed unit and round-trip coverage for each ordered pair.
- Keep full unit names case-insensitive, but preserve case in data-rate symbols so `kb/s` differs from `kB/s` and `kib/s` differs from `KiB/s`.
- Reject unknown unit codes, non-finite values, undefined reciprocal fuel-economy conversions, and temperatures below absolute zero.
- Invalid input must produce actionable UI feedback and must not raise into a Tk callback.
- Settings stay in the operating system's per-user configuration directory. Persist precision, scientific notation, and up to ten recent conversions with atomic replacement. Storage errors must leave the app usable; do not overwrite unreadable settings until the user changes state.
- Validate workflow edits with actionlint. Keep signing values out of source files and logs.
- Preserve the release workflow's least-privilege token and signing-secret scopes when changing jobs.

## Release workflow

Pushing to `main` creates a patch tag with the repository `GITHUB_TOKEN` and calls the release workflow. A manually pushed stable `vMAJOR.MINOR.PATCH` tag uses the same release path. The release stops before platform builds if required signing secrets are missing and publishes only after Windows, macOS, and Linux packages pass smoke tests and checksum verification.

Maintainers configure these repository Actions secrets: `WINDOWS_SIGNING_CERTIFICATE`, `WINDOWS_SIGNING_PASSWORD`, `APPLE_CERTIFICATE`, `APPLE_CERTIFICATE_PASSWORD`, `APPLE_ID`, `APPLE_APP_SPECIFIC_PASSWORD`, and `APPLE_TEAM_ID`. Certificate secrets contain base64-encoded PFX/P12 files. Release jobs expose them only to signing steps after package smoke tests; contents write permission belongs only to tag creation and publication, and checkout credentials are not persisted. Signing improves publisher verification and reputation but cannot guarantee a clean antivirus or reputation-service verdict.

## Git workflow

Work on a branch, run `pytest` and the fatal Flake8 command, and open a PR unless the owner asks for a direct push. Do not publish a release from unsigned local artifacts.

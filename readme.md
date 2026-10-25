# Unit Converter

[![Cross-Platform Release](https://github.com/palaashatri/unitconverter-tk/actions/workflows/cross-platform-release.yml/badge.svg)](https://github.com/palaashatri/unitconverter-tk/actions/workflows/cross-platform-release.yml)
[![CI](https://github.com/palaashatri/unitconverter-tk/actions/workflows/ci.yml/badge.svg)](https://github.com/palaashatri/unitconverter-tk/actions/workflows/ci.yml)

A native Tkinter desktop app for quick everyday unit conversions. It runs on Windows, macOS, and Linux, keeps conversion math testable outside the UI, and stores preferences locally.

## Features

The app has fourteen tabs: Temperature, Length, Area, Digital storage, Weight, Volume, Speed, Time, Pressure, Energy, Angle, Data rate, Fuel economy, and Cooking.

Use the global type-to-convert field for expressions such as:

```text
10 km in mi     → 6.213712 Miles
72 F to C       → 22.222222 Celsius
```

Unit names are case-insensitive. Use full words when a short symbol could mean two things; for example, `b` and `B` are ambiguous under case-insensitive parsing, so enter `bit` or `byte`.

The app remembers decimal precision, scientific notation, and up to ten recent conversions. Settings use versioned JSON with atomic writes and stay on the device. If the settings file is invalid or unavailable, conversions remain usable and the app reports the issue.

| Platform | Settings file |
| --- | --- |
| Linux | `${XDG_CONFIG_HOME:-~/.config}/unitconverter/settings.json` |
| macOS | `~/Library/Application Support/UnitConverter/settings.json` |
| Windows | `%LOCALAPPDATA%\UnitConverter\settings.json` |

The supported unit definitions and conventions are listed in [docs/unit-definitions.md](docs/unit-definitions.md). This includes U.S. customary cooking measures, thermochemical calories, IT BTU, the distinction between Torr and mmHg, average Gregorian month/year values, and the Mach reference condition.

## Run from source

Install Python 3.12 or newer and Tkinter. The Python installer for Windows includes Tkinter. On Debian or Ubuntu, install the matching Tk package, for example `sudo apt install python3-tk`.

```bash
python app.py
```

## Development and tests

Create a virtual environment and install the pinned development tools:

```bash
python3.12 -m venv .venv
source .venv/bin/activate       # Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

Run the test suite and required lint check:

```bash
pytest -q
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

GUI tests use the current desktop display. On a headless Linux machine, install Xvfb and run `xvfb-run -a pytest -q`. The CI workflow runs the full test suite with coverage under Xvfb and uploads `coverage.xml` as an artifact. Workflow edits can be checked with `actionlint .github/workflows/*.yml .github/workflows/*.yaml`.

## Build locally

Local builds are unsigned. Install the pinned packaging tools, then use the native builder for your platform:

```bash
python -m pip install -r requirements-build.txt
python -m PyInstaller --clean --onefile --name unitconverter app.py
```

On macOS, create the app bundle with `python setup-macos.py py2app`. A source smoke check that opens the UI, verifies all fourteen tabs, and exits is available as `python app.py --smoke-test`.

## Signed releases

Pushing a stable `vMAJOR.MINOR.PATCH` tag starts a release. Each platform builds and smoke-tests its package before a final job publishes the complete set:

- `unitconverter-<version>-windows.exe`
- `unitconverter-<version>-macos.zip`, containing `UnitConverter.app`
- `unitconverter-<version>-linux-x86_64.AppImage`
- `SHA256SUMS` and per-file `.sha256` checksums

Each push to `main` also creates the next patch tag and calls the same release workflow. Release publication stops before any platform build if signing credentials are missing, and it never publishes partial platform output.

Repository maintainers configure these in **Settings → Secrets and variables → Actions**. Certificate files should be base64-encoded before storing them as secrets:

| Secret | Value |
| --- | --- |
| `WINDOWS_SIGNING_CERTIFICATE` | Base64-encoded Windows publisher PFX certificate |
| `WINDOWS_SIGNING_PASSWORD` | PFX password |
| `APPLE_CERTIFICATE` | Base64-encoded Apple Developer ID `.p12` certificate |
| `APPLE_CERTIFICATE_PASSWORD` | `.p12` password |
| `APPLE_ID` | Apple account email used for notarization |
| `APPLE_APP_SPECIFIC_PASSWORD` | Apple app-specific password |
| `APPLE_TEAM_ID` | Apple Developer team ID |

Windows releases are signed and timestamped. The macOS app is signed, notarized, and stapled. Signing helps users verify the publisher and can improve software reputation; it cannot guarantee that every antivirus or reputation service will give a file the same verdict. Local builds remain unsigned and are not described as signed releases.

## References

- [Python downloads](https://www.python.org/downloads/)
- [Tkinter documentation](https://docs.python.org/3/library/tkinter.html)
- [GitHub Actions documentation](https://docs.github.com/en/actions)

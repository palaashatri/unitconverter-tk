"""Atomic local persistence for preferences and recent conversions."""

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Mapping

from .app_state import AppState


SETTINGS_VERSION = 1


def settings_path(
    environ: Mapping[str, str] | None = None,
    home: Path | None = None,
    platform: str | None = None,
) -> Path:
    environment = os.environ if environ is None else environ
    user_home = Path.home() if home is None else Path(home)
    current_platform = sys.platform if platform is None else platform

    if current_platform.startswith("win"):
        base = Path(environment.get("LOCALAPPDATA", user_home / "AppData" / "Local"))
        return base / "UnitConverter" / "settings.json"
    if current_platform == "darwin":
        return user_home / "Library" / "Application Support" / "UnitConverter" / "settings.json"

    config_home = Path(environment.get("XDG_CONFIG_HOME", user_home / ".config"))
    if not config_home.is_absolute():
        config_home = user_home / ".config"
    return config_home / "unitconverter" / "settings.json"


def _defaults_with_warning(message: str) -> tuple[AppState, str]:
    return AppState(), message


def load_settings(path: Path) -> tuple[AppState, str | None]:
    settings_file = Path(path)
    try:
        contents = settings_file.read_text(encoding="utf-8")
    except FileNotFoundError:
        return AppState(), None
    except (OSError, UnicodeError):
        return _defaults_with_warning("Saved settings could not be read; defaults are in use.")

    try:
        data = json.loads(contents)
    except (json.JSONDecodeError, UnicodeError):
        return _defaults_with_warning("Saved settings are invalid; defaults are in use.")
    if not isinstance(data, dict) or data.get("version") != SETTINGS_VERSION:
        return _defaults_with_warning("Saved settings use an unsupported version; defaults are in use.")

    warning = False
    precision = data.get("precision", 6)
    if isinstance(precision, bool) or not isinstance(precision, int):
        precision = 6
        warning = True
    else:
        bounded_precision = min(15, max(0, precision))
        warning |= bounded_precision != precision
        precision = bounded_precision

    use_scientific = data.get("use_scientific", False)
    if not isinstance(use_scientific, bool):
        use_scientific = False
        warning = True

    history = data.get("history", [])
    if not isinstance(history, list):
        history = []
        warning = True
    else:
        valid_history = [
            entry.strip()
            for entry in history
            if isinstance(entry, str) and entry.strip()
        ]
        warning |= len(valid_history) != len(history)
        history = valid_history[:10]
        warning |= len(valid_history) > 10

    state = AppState(
        precision=precision,
        use_scientific=use_scientific,
        history=history,
    )
    return state, "Some saved settings were invalid and have been reset." if warning else None


def save_settings(state: AppState, path: Path) -> None:
    settings_file = Path(path)
    settings_file.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": SETTINGS_VERSION,
        "precision": min(15, max(0, int(state.precision))),
        "use_scientific": bool(state.use_scientific),
        "history": [str(entry) for entry in state.history[:10]],
    }
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=settings_file.parent,
            prefix=settings_file.name + ".",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            json.dump(payload, temporary_file, ensure_ascii=False, indent=2)
            temporary_file.write("\n")
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        temporary_path.replace(settings_file)
    except OSError:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise

import json
from pathlib import Path

import pytest

from src.app_state import AppState
from src.persistence import load_settings, save_settings, settings_path


def test_app_state_defaults_and_caps_history():
    state = AppState()
    assert state.precision == 6
    assert state.use_scientific is False
    assert state.history == []

    for index in range(12):
        state.add_history(f"conversion {index}")
    assert state.history == [f"conversion {index}" for index in range(11, 1, -1)]


@pytest.mark.parametrize(
    "platform,environ,expected",
    [
        ("linux", {"XDG_CONFIG_HOME": "/config"}, "/config/unitconverter/settings.json"),
        ("darwin", {}, "/users/alice/Library/Application Support/UnitConverter/settings.json"),
        ("win32", {"LOCALAPPDATA": "C:/Users/alice/AppData/Local"}, "C:/Users/alice/AppData/Local/UnitConverter/settings.json"),
    ],
)
def test_settings_path_uses_platform_user_config(platform, environ, expected):
    path = settings_path(environ=environ, home=Path("/users/alice"), platform=platform)
    assert path.as_posix() == expected


def test_settings_path_uses_linux_home_fallback():
    assert settings_path(environ={}, home=Path("/users/alice"), platform="linux") == Path(
        "/users/alice/.config/unitconverter/settings.json"
    )


def test_missing_settings_file_returns_defaults_without_warning(tmp_path):
    state, warning = load_settings(tmp_path / "missing.json")
    assert state == AppState()
    assert warning is None


def test_save_and_reload_settings(tmp_path):
    path = tmp_path / "settings.json"
    state = AppState(precision=12, use_scientific=True, history=["new", "older"])
    save_settings(state, path)

    data = json.loads(path.read_text())
    assert data == {
        "version": 1,
        "precision": 12,
        "use_scientific": True,
        "history": ["new", "older"],
    }
    loaded, warning = load_settings(path)
    assert loaded == state
    assert warning is None


def test_loaded_settings_validate_precision_and_history(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({
        "version": 1,
        "precision": 99,
        "use_scientific": True,
        "history": [f"entry {index}" for index in range(12)],
    }))

    state, warning = load_settings(path)
    assert state.precision == 15
    assert state.use_scientific is True
    assert state.history == [f"entry {index}" for index in range(10)]
    assert warning is not None


@pytest.mark.parametrize(
    "contents", ["{broken", '{"version": 999, "precision": 3}']
)
def test_malformed_or_future_settings_preserve_file_and_use_defaults(tmp_path, contents):
    path = tmp_path / "settings.json"
    path.write_text(contents)

    state, warning = load_settings(path)
    assert state == AppState()
    assert warning is not None
    assert path.read_text() == contents


def test_atomic_write_failure_preserves_existing_settings(tmp_path, monkeypatch):
    path = tmp_path / "settings.json"
    path.write_text("previous complete settings")

    def fail_replace(self, target):
        raise OSError("replace failed")

    monkeypatch.setattr(Path, "replace", fail_replace)
    with pytest.raises(OSError, match="replace failed"):
        save_settings(AppState(precision=10), path)

    assert path.read_text() == "previous complete settings"
    assert list(tmp_path.glob("*.tmp")) == []

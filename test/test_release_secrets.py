import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_release_secrets.sh"
REQUIRED_SECRETS = (
    "WINDOWS_SIGNING_CERTIFICATE",
    "WINDOWS_SIGNING_PASSWORD",
    "APPLE_CERTIFICATE",
    "APPLE_CERTIFICATE_PASSWORD",
    "APPLE_ID",
    "APPLE_APP_SPECIFIC_PASSWORD",
    "APPLE_TEAM_ID",
)


def _run(secret_values):
    environment = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), **secret_values}
    return subprocess.run(
        ["bash", str(CHECKER)],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )


def test_missing_release_secrets_fail_and_name_only_missing_values():
    result = _run({})

    assert result.returncode == 1
    assert "Missing required signing secrets:" in result.stderr
    assert all(name in result.stderr for name in REQUIRED_SECRETS)


def test_configured_release_secrets_pass_without_printing_values():
    values = {name: f"placeholder-{index}" for index, name in enumerate(REQUIRED_SECRETS)}
    result = _run(values)

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""
    assert all(value not in result.stdout + result.stderr for value in values.values())

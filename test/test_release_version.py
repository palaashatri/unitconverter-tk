import subprocess
import sys
from pathlib import Path

import pytest

from scripts.next_version import next_patch_tag


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "tags,expected",
    [
        ([], "v0.0.1"),
        (["v1.2.7"], "v1.2.8"),
        (["v1.9.9", "v1.10.2", "v1.10.2-rc.1", "v2.0.0-beta"], "v1.10.3"),
        (["v3.4.1", "release-8.0.0", "v3.4.9-build.2"], "v3.4.2"),
    ],
)
def test_next_patch_tag_selects_latest_exact_semver_and_ignores_suffixes(
    tags, expected
):
    assert next_patch_tag(tags) == expected


def test_version_script_accepts_shell_supplied_fixture_tags():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "next_version.py"), "v1.0.0", "v1.2.4"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == "v1.2.5"

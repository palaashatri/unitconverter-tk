"""Select the next stable patch tag from exact semantic-version tags."""

import re
import subprocess
import sys
from collections.abc import Iterable


_TAG = re.compile(r"^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def next_patch_tag(tags: Iterable[str]) -> str:
    versions = []
    for tag in tags:
        match = _TAG.fullmatch(tag.strip())
        if match:
            versions.append(tuple(int(part) for part in match.groups()))

    if not versions:
        return "v0.0.1"

    major, minor, patch = max(versions)
    return f"v{major}.{minor}.{patch + 1}"


def main() -> None:
    tags = sys.argv[1:]
    if not tags:
        result = subprocess.run(
            ["git", "tag", "--list"],
            check=True,
            capture_output=True,
            text=True,
        )
        tags = result.stdout.splitlines()
    print(next_patch_tag(tags))


if __name__ == "__main__":
    main()

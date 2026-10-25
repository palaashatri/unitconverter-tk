"""Checks for reproducible development and macOS packaging configuration."""

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _requirements(path):
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def test_development_and_build_dependencies_are_pinned():
    dev = _requirements(ROOT / "requirements-dev.txt")
    build = _requirements(ROOT / "requirements-build.txt")

    assert any(line.startswith("pytest==") for line in dev)
    assert any(line.startswith("pytest-cov==") for line in dev)
    assert any(line.startswith("flake8==") for line in dev)
    assert any(line.startswith("PyInstaller==") for line in build)
    assert any("py2app==" in line and "platform_system == 'Darwin'" in line for line in build)
    assert all("==" in line for line in dev)


def test_macos_build_metadata_declares_the_application_bundle():
    source = (ROOT / "setup-macos.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    assignments = {
        target.id: ast.literal_eval(node.value)
        for node in tree.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name) and target.id in {"APP", "OPTIONS"}
    }

    assert assignments["APP"] == ["app.py"]
    assert assignments["OPTIONS"]["packages"] == ["src"]

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
    assert assignments["OPTIONS"]["plist"]["CFBundleIdentifier"] == (
        "com.palaashatri.unitconverter"
    )


def test_release_workflow_requires_signing_and_publishes_versioned_checksums():
    release = (ROOT / ".github" / "workflows" / "cross-platform-release.yml").read_text(
        encoding="utf-8"
    )
    secret_check = (ROOT / "scripts" / "check_release_secrets.sh").read_text(
        encoding="utf-8"
    )

    for secret in (
        "WINDOWS_SIGNING_CERTIFICATE",
        "WINDOWS_SIGNING_PASSWORD",
        "APPLE_CERTIFICATE",
        "APPLE_CERTIFICATE_PASSWORD",
        "APPLE_ID",
        "APPLE_APP_SPECIFIC_PASSWORD",
        "APPLE_TEAM_ID",
    ):
        assert secret in release
    assert "bash scripts/check_release_secrets.sh" in release
    assert "Missing required signing secrets" in secret_check
    assert "unitconverter-$env:VERSION-windows.exe" in release
    assert "unitconverter-$VERSION-macos.zip" in release
    assert "unitconverter-$VERSION-linux-x86_64.AppImage" in release
    assert (
        "needs: [release-metadata, validate-release-secrets, validate, build-windows, "
        "build-macos, build-linux]"
    ) in release
    assert "SHA256SUMS" in release
    assert 'git rev-parse "$TAG_NAME^{commit}"' in release
    assert "Release tag does not point to the requested source commit." in release
    assert "signtool sign" in release
    assert "codesign --force --deep --options runtime" in release
    assert "xcrun notarytool submit" in release
    assert "APPIMAGE_EXTRACT_AND_RUN=1 xvfb-run -a" in release


def test_appimage_builder_is_pinned_and_verified_before_execution():
    release = (ROOT / ".github" / "workflows" / "cross-platform-release.yml").read_text(
        encoding="utf-8"
    )

    assert "appimagetool/releases/download/1.9.1/" in release
    assert "ed4ce84f0d9caff66f50bcca6ff6f35aae54ce8135408b3fa33abfc3cb384eb0" in release
    assert "type2-runtime/releases/download/20251108/runtime-x86_64" in release
    assert "2fca8b443c92510f1483a883f60061ad09b46b978b2631c807cd873a47ec260d" in release
    assert "sha256sum --check" in release
    assert "releases/latest/download/appimagetool" not in release
    assert "Icon=unitconverter" in release
    assert "cat > AppDir/AppRun" in release
    assert (ROOT / "assets" / "unitconverter.svg").is_file()

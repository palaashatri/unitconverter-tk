"""Guardrails for the required CI checks and release workflow names."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def test_ci_runs_the_required_python_checks_and_gui_under_xvfb():
    ci = (WORKFLOWS / "ci.yml").read_text(encoding="utf-8")

    assert "actions/checkout@v4" in ci
    assert "actions/setup-python@v5" in ci
    assert 'python-version: "3.12"' in ci
    assert "python3.12 -m venv .venv-ci" in ci
    assert ".venv-ci/bin/python -m pip install -r requirements-dev.txt" in ci
    assert "xvfb-run -a .venv-ci/bin/pytest --cov=. --cov-report=term --cov-report=xml" in ci
    assert "flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics" in ci
    assert "actionlint .github/workflows/*.yml .github/workflows/*.yaml" in ci
    assert "actions/upload-artifact@v4" in ci


def test_coverage_workflow_is_not_duplicated_or_malformed():
    names = {path.name for path in WORKFLOWS.iterdir()}
    assert "ci.yml" in names
    assert not {
        "unit-test.yml",
        "flake8-lint.yml",
        "code-coverage-term.yml",
        "code-coverage-html.yml",
    } & names


def test_auto_tag_uses_github_token_and_calls_the_release_workflow():
    auto_tag = (WORKFLOWS / "auto-tag.yaml").read_text(encoding="utf-8")
    release = (WORKFLOWS / "cross-platform-release.yml").read_text(encoding="utf-8")

    assert "GH_PAT" not in auto_tag
    assert "contents: write" in auto_tag
    assert "uses: ./.github/workflows/cross-platform-release.yml" in auto_tag
    assert "workflow_call:" in release
    assert "workflow_run:" not in release


def test_release_workflow_limits_permissions_and_checkout_credentials():
    release = (WORKFLOWS / "cross-platform-release.yml").read_text(encoding="utf-8")

    assert re.search(r"^permissions:\n  contents: read$", release, re.MULTILINE)
    publish = release.split("  publish:", 1)[1]
    assert "    permissions:\n      contents: write" in publish

    checkouts = re.findall(
        r"(?ms)^      - uses: actions/checkout@v4\n        with:\n"
        r"(.*?)(?=^      - |^  [a-z][a-z-]*:|\Z)",
        release,
    )
    assert len(checkouts) == 6
    assert all("persist-credentials: false" in checkout for checkout in checkouts)


def test_release_secrets_are_scoped_to_steps_after_frozen_app_smoke_tests():
    release = (WORKFLOWS / "cross-platform-release.yml").read_text(encoding="utf-8")
    windows = release.split("  build-windows:", 1)[1].split("  build-macos:", 1)[0]
    macos = release.split("  build-macos:", 1)[1].split("  build-linux:", 1)[0]

    assert "WINDOWS_SIGNING_CERTIFICATE:" not in windows.split("    steps:", 1)[0]
    assert "WINDOWS_SIGNING_PASSWORD:" not in windows.split("    steps:", 1)[0]
    assert windows.index("Smoke-test frozen executable") < windows.index("Sign and timestamp executable")
    windows_sign = windows.split("      - name: Sign and timestamp executable", 1)[1]
    assert "WINDOWS_SIGNING_CERTIFICATE: ${{ secrets.WINDOWS_SIGNING_CERTIFICATE }}" in windows_sign
    assert "WINDOWS_SIGNING_PASSWORD: ${{ secrets.WINDOWS_SIGNING_PASSWORD }}" in windows_sign

    assert "APPLE_CERTIFICATE:" not in macos.split("    steps:", 1)[0]
    assert "APPLE_CERTIFICATE_PASSWORD:" not in macos.split("    steps:", 1)[0]
    assert "APPLE_ID:" not in macos.split("    steps:", 1)[0]
    assert "APPLE_APP_SPECIFIC_PASSWORD:" not in macos.split("    steps:", 1)[0]
    assert "APPLE_TEAM_ID:" not in macos.split("    steps:", 1)[0]
    assert macos.index("Smoke-test frozen application") < macos.index("Sign, notarize, and staple application")
    macos_sign = macos.split("      - name: Sign, notarize, and staple application", 1)[1]
    for secret in (
        "APPLE_CERTIFICATE",
        "APPLE_CERTIFICATE_PASSWORD",
        "APPLE_ID",
        "APPLE_APP_SPECIFIC_PASSWORD",
        "APPLE_TEAM_ID",
    ):
        assert f"{secret}: ${{{{ secrets.{secret} }}}}" in macos_sign


def test_release_secret_gate_checks_out_source_for_its_validation_script():
    release = (WORKFLOWS / "cross-platform-release.yml").read_text(encoding="utf-8")
    secret_job = release.split("  validate-release-secrets:", 1)[1].split("  validate:", 1)[0]

    assert "ref: ${{ needs.release-metadata.outputs.source_sha }}" in secret_job
    assert "persist-credentials: false" in secret_job
    assert "bash scripts/check_release_secrets.sh" in secret_job

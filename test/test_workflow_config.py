"""Guardrails for the required CI checks and release workflow names."""

from pathlib import Path


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

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_readme_describes_completed_categories_parser_and_saved_preferences():
    readme = (ROOT / "readme.md").read_text(encoding="utf-8").lower()

    for category in (
        "temperature", "length", "area", "digital storage", "weight", "volume",
        "speed", "time", "pressure", "energy", "angle", "data rate",
        "fuel economy", "cooking",
    ):
        assert category in readme
    assert "10 km in mi" in readme
    assert "72 f to c" in readme
    assert "scientific notation" in readme
    assert "xdg_config_home" in readme
    assert "application support" in readme
    assert "localappdata" in readme
    assert "roadmap" not in readme


def test_readme_documents_unsigned_builds_and_exact_signing_requirements():
    readme = (ROOT / "readme.md").read_text(encoding="utf-8").lower()

    for secret in (
        "windows_signing_certificate",
        "windows_signing_password",
        "apple_certificate",
        "apple_certificate_password",
        "apple_id",
        "apple_app_specific_password",
        "apple_team_id",
    ):
        assert secret in readme
    assert "sha256sums" in readme
    assert "unitconverter-<version>-windows.exe" in readme
    assert "unitconverter-<version>-macos.zip" in readme
    assert "unitconverter-<version>-linux-x86_64.appimage" in readme
    assert "ignore the warning" not in readme
    assert "false positive" not in readme


def test_agents_commands_and_repository_map_match_the_implemented_project():
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8").lower()

    assert "requirements-dev.txt" in agents
    assert "pytest" in agents
    assert "flake8 . --count --select=e9,f63,f7,f82" in agents
    assert "actionlint" in agents
    assert "src/persistence.py" in agents
    assert "src/quick_convert.py" in agents
    assert "fourteen" in agents or "14" in agents
    assert "known issues (2026-10-20)" not in agents
    assert "python 3.9" not in agents
    assert "least-privilege token" in agents
    agents_source = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "`kb/s` differs from `kB/s`" in agents_source
    assert "`kib/s` differs from `KiB/s`" in agents_source


def test_unit_definition_document_covers_convention_sensitive_units():
    definitions = (ROOT / "docs" / "unit-definitions.md").read_text(
        encoding="utf-8"
    ).lower()

    for convention in (
        "u.s. customary", "thermochemical calorie", "international table",
        "torr and mmhg", "average gregorian", "mach 1", "absolute zero",
    ):
        assert convention in definitions


def test_readme_explains_case_sensitive_data_rate_symbols():
    readme = (ROOT / "readme.md").read_text(encoding="utf-8")

    assert "`kb/s`" in readme and "`kB/s`" in readme
    assert "`kib/s`" in readme and "`KiB/s`" in readme

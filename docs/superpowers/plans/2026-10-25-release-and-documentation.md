# Release and Documentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run reliable CI on supported Python, validate the GUI and conversions, and produce versioned cross-platform packages with signed Windows and notarized macOS releases when maintainers provide credentials.

**Architecture:** Keep CI, release builds, and auto-tagging in separate GitHub Actions workflows with least-privilege permissions. Build platform artifacts on native runners, validate them before release, and publish only after all required platform jobs succeed. Treat signing inputs as repository Actions secrets.

**Tech Stack:** GitHub Actions, Python, pytest/pytest-cov, Flake8, PyInstaller, py2app, AppImage tooling, signtool, codesign/notarytool.

**Spec:** [2026-10-25-unitconverter-production-readiness-design.md](../specs/2026-10-25-unitconverter-production-readiness-design.md)

## Global Constraints

- Replace Python 3.9 with a supported common Python version and update deprecated actions.
- Keep conversion tests, GUI smoke checks, and lint required before release publication.
- Do not publish a partial release or call an unsigned build signed.
- Use a Windows publisher certificate and Apple Developer ID credentials only through repository Actions secrets.
- Pin or verify downloaded packaging tools; do not fetch an unpinned latest binary.
- Remove README advice to ignore antivirus warnings and explain the certificate/reputation requirement accurately.
- Keep `AGENTS.md` commands and architecture descriptions aligned with the implementation.

## Review Focus

- A maintainer without signing secrets can run CI and local unsigned builds, but a tagged release must stop before publication with a clear missing-secret report.
- A failed Windows/macOS/Linux build must prevent release publication and must not leave a release presented as complete.
- Auto-tag pushes made with `GITHUB_TOKEN` must still invoke release builds despite GitHub's event recursion protection.
- Linux AppImage tool checksum failure must fail the build rather than bypass verification.
- Published filenames/checksums and README instructions must match actual outputs on all three runners.

---

### Task 1: Add reproducible development and packaging dependencies

**Files:**
- Create: `requirements-dev.txt`
- Create: `requirements-build.txt`
- Create: `setup-macos.py` for py2app build metadata
- Modify: `.gitignore`

**Interfaces:**
- Produces: one documented development install and platform build dependency sets; all project code remains dependency-free at runtime.
- Consumes: test and package tools selected by the current maintained release versions compatible with the selected Python baseline.

- [x] **Step 1: Add** supported, pinned `pytest`, `pytest-cov`, and `flake8` in `requirements-dev.txt`; add pinned PyInstaller and py2app tooling in `requirements-build.txt`; define reproducible py2app metadata in `setup-macos.py`; update ignored Windows/macOS/Linux generated artifacts.
- [x] **Step 2: Create** a fresh Python 3.12 virtual environment and install `requirements-dev.txt`; expect all declared test tools to install. (All three pinned tools installed.)
- [x] **Step 3: Run** `python -m pip check`; expect no dependency conflicts and no runtime-only packages. (No broken requirements.)
- [x] **Step 4: Commit** `build: declare development and packaging tools`.

### Task 2: Repair and modernize test, lint, and coverage workflows

**Files:**
- Modify: `.github/workflows/unit-test.yml`, `.github/workflows/flake8-lint.yml`, `.github/workflows/code-coverage-term.yml`, `.github/workflows/code-coverage-html.yml`
- Create or modify: `.github/workflows/ci.yml` if consolidating jobs
- Modify: `readme.md` workflow badges if workflow names change

**Interfaces:**
- Consumes: dependency files from Task 1; GUI tests and converter suite from Plans 1 and 2.
- Produces: CI on pushes and pull requests with supported Python, fatal lint, complete tests, coverage output/artifact, and a GUI display on Linux.

- [x] **Step 1: Add workflow validation** using `actionlint` and checks that the CI commands match `AGENTS.md`.
- [x] **Step 2: Run** `actionlint .github/workflows/*.yml .github/workflows/*.yaml`; expect existing YAML or command issues to surface, including the incomplete HTML coverage command. (Found stale release action versions and the broken HTML job; fixed by consolidating workflows.)
- [x] **Step 3: Replace** checkout/setup-python actions with maintained major versions, set the common Python baseline to 3.12, install from `requirements-dev.txt`, run `pytest` including coverage, run the AGENTS fatal Flake8 command, and use Xvfb for GUI tests on Linux. Consolidate duplicated coverage workflows or make each retained workflow valid and purposeful.
- [x] **Step 4: Run** local workflow-equivalent commands: `pytest --cov=. --cov-report=term --cov-report=xml`, `flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics`, and `actionlint`; expect all checks to pass. (164 tests passed; fatal Flake8 0; actionlint clean.)
- [x] **Step 5: Commit** `ci: modernize tests lint and coverage workflows`.

### Task 3: Make auto-tagging deterministic and least-privileged

**Files:**
- Modify: `.github/workflows/auto-tag.yaml`
- Modify: `.github/workflows/cross-platform-release.yml`

**Interfaces:**
- Produces: a semantic version output consumed by native build jobs; manual version tags and main-branch auto-tags both reach the same release validation/publication path.
- Consumes: GitHub `contents: write` permission via `GITHUB_TOKEN` only.

- [x] **Step 1: Add tests** for tag selection using shell fixtures: no tag, valid latest semver, and tags with non-version suffixes; ensure only the patch component increments.
- [x] **Step 2: Run** tag tests and `actionlint`; expect current GH_PAT dependency and workflow-recursion problem to be identified. (The original personal-token and `workflow_run` path were confirmed from workflow source.)
- [x] **Step 3: Implement** least-privilege token permissions and a workflow-call path from auto-tag to release jobs so tags created with `GITHUB_TOKEN` still build; remove PAT-in-URL shell usage and duplicate/ambiguous release triggers.
- [x] **Step 4: Run** tag tests, shell lint, and `actionlint`; expect manual and auto-tag paths to identify the same exact source commit and version. (8 version/workflow tests passed; actionlint clean.)
- [x] **Step 5: Commit** `ci: make tagged releases reproducible`.

### Task 4: Build, smoke-test, sign, and publish platform artifacts

**Files:**
- Modify: `.github/workflows/cross-platform-release.yml`
- Modify: `app.py` to expose the test-only `--smoke-test` entrypoint
- Create: `test/test_packaged_smoke.py` or platform smoke scripts

**Interfaces:**
- Produces: versioned `unitconverter-<version>-windows.exe`, `unitconverter-<version>-macos.zip` containing a signed/notarized `.app`, `unitconverter-<version>-linux-x86_64.AppImage`, and SHA-256 checksums.
- Consumes: tag from Task 3, dependency versions from Task 1, and repository secrets `WINDOWS_SIGNING_CERTIFICATE`, `WINDOWS_SIGNING_PASSWORD`, `APPLE_CERTIFICATE`, `APPLE_CERTIFICATE_PASSWORD`, `APPLE_ID`, `APPLE_APP_SPECIFIC_PASSWORD`, and `APPLE_TEAM_ID`.

- [x] **Step 1: Add failing packaging configuration checks** for artifact names, required signing variables on release tags, and pinned AppImage tooling/checksum; add unit coverage for smoke-test mode.
- [x] **Step 2: Run** packaging configuration and smoke-test checks; expect current unpinned download, missing signing, release consistency, and missing CLI-mode failures. (Tests caught absent signing gates, tool pin/checksum, and smoke-test mode; local AppImage validation exposed missing AppRun/icon requirements.)
- [x] **Step 3: Implement** native Windows, macOS, and Linux build jobs; add a `python app.py --smoke-test` mode that creates the Tk app, verifies all fourteen tabs, and exits without entering the event loop; run that mode from each frozen artifact before publication. Code-sign and timestamp the Windows executable; sign, notarize, and staple the macOS app. Fail the release before publication if required secrets are absent or signing/notarization fails. Expose signing secrets only to signing steps after the package smoke test, use read-only token permissions by default with write access limited to tagging/publication, and disable persisted checkout credentials. Keep unsigned builds available for local development and non-release CI only. Pin the AppImage tool version and verify its published SHA-256 before use.
- [x] **Step 4: Gate** the final GitHub Release job on successful Windows, macOS, and Linux jobs and attach all platform artifacts plus SHA-256 files; include release notes generated from the version/tag. A workflow check must fail if the final publish job lacks dependencies on any platform job. Do not publish partial outputs.
- [x] **Step 5: Validate** package construction locally for the available platform and use native CI runners for Windows/macOS. Verify actionlint, artifact names, checksums, and that a deliberately missing signing secret fails before publication. (PyInstaller executable and pinned-runtime AppImage each passed the 14-tab smoke check; AppImage checksum verified; missing-secret fixture fails with names only; actionlint clean.)
- [x] **Step 6: Commit** `build: sign and validate cross-platform releases`.

### Task 5: Update user and maintainer documentation

**Files:**
- Modify: `readme.md`, `AGENTS.md`
- Create or update: `docs/unit-definitions.md` from the conversion plan

**Interfaces:**
- Consumes: observed UI labels, parser behavior, storage paths, converter codes, workflow outputs, and secret names from Plans 1–3.
- Produces: accurate end-user setup, conversion conventions, persistence, test, packaging, and signing instructions.

- [x] **Step 1: Add documentation checks** for all four categories and parser examples, persisted data behavior, updated workflows, signing-secret names, and no advice to ignore antivirus findings.
- [x] **Step 2: Run** README/documentation checks; expect stale roadmap, Python 3.9/old commands, unresolved warnings, or missing categories to fail. (Three checks failed against the stale README and AGENTS content.)
- [x] **Step 3: Update** README and AGENTS commands/layout/category lists; replace the roadmap with completed capabilities, document each ambiguous factor convention and local data directory, document local unsigned build and signed release requirements, and remove the Defender false-positive advice.
- [x] **Step 4: Run** docs checks, `pytest`, Flake8, actionlint, and the GUI smoke suite; expect docs and implementation behavior to match. (179 tests passed; fatal Flake8 0; actionlint clean; GUI smoke covered in the suite.)
- [x] **Step 5: Commit** `docs: document production workflows and unit conventions`.

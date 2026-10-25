# Unit Converter production readiness

## Intent

Make Unit Converter reliable enough for ordinary desktop use and release. This completes every item in the current README roadmap and resolves every known issue in `AGENTS.md`. The application remains a Python/Tkinter desktop app with conversion math in pure `src/convert_*.py` modules.

## Goals

- Correct and document the existing conversion definitions, including ambiguous customary and convention-based units.
- Provide a global expression field for inputs such as `10 km in mi` and `72 F to C`.
- Preserve precision, scientific notation, and the ten most recent conversions across restarts.
- Add angle, data-rate, fuel-economy, and cooking-volume categories.
- Test every supported unit against a reference value and test every ordered unit pair for round-trip behavior.
- Modernize and repair CI; produce Windows, macOS, and Linux release artifacts with a clear signing/notarization path.
- Document installation, persisted data, supported unit conventions, development checks, and release requirements.

## Non-goals

- A broad visual redesign, cloud synchronization, user accounts, or a plug-in system.
- Changes to the app's basic Tkinter/native desktop platform.
- Guaranteeing that any signed executable will never receive an antivirus or reputation warning; signing improves publisher verification and reputation but cannot guarantee a vendor's verdict.
- Providing or fabricating Apple or Windows signing credentials.

## Current state and constraints

The app has ten tabs whose UI modules duplicate conversion controls and map labels to unit codes. Most conversion modules use factors to a base unit; temperature uses explicit formulas. There is no settings store or app packaging manifest. Existing tests cover only five of ten conversion modules. CI still uses old Actions and Python 3.9. The release workflow builds a PyInstaller executable, a py2app bundle, and an AppImage; its Linux image-tool download is not pinned, and auto-tagging depends on a personal token.

Keep conversion functions free of Tk imports. Keep parser, storage, and conversion definitions testable without starting the GUI. Use the standard library for durable settings and parsing unless an implementation need justifies a new dependency. Keep source data and credentials out of release artifacts.

## Approaches

1. **Resolve only the explicitly listed defects.** This would correct weight symbols, the mile factor, temperature spelling, existing tests, and CI versions. It would leave the roadmap features and most factors unaudited, so it does not satisfy the requested complete scope.
2. **Complete the roadmap and harden the existing conversion system (selected).** Build on the current modular Tkinter design, add a pure parser, storage layer, and conversion modules, audit all existing and new factors, and repair CI/release workflows. This covers every requested item while keeping the application small and offline.
3. **Replace the desktop application with a web or cross-platform framework.** This would allow a different distribution model but discard the existing native Tkinter application and is outside the stated constraints.

The user selected the complete scope in `AGENTS.md` and the README. Approach 2 is the design basis.

## Proposed behavior and implementation

### Conversion correctness and definitions

- Correct the mass codes to `dag` for decagram and `dg` for decigram. Keep `deg` as a compatibility alias for decigram; the old erroneous meaning of `dg` cannot be preserved alongside the correct SI meaning. Update UI labels and note the migration.
- Correct the international mile to exactly 1609.344 metres. Rename the ambiguous square-millimetre code to `sqmm`, retaining the old `mm` code as a compatibility alias.
- Rename `covert_celToKel` to `convert_celToKel`, update callers, and retain the old spelling as a deprecated forwarding alias.
- Audit every existing factor against NIST SP 811 or the appropriate defining standard. Document conventions beside definitions and in user docs where a unit is ambiguous or convention-based: U.S. customary liquid measures, thermochemical calorie, IT BTU, torr versus mmHg, average Gregorian month/year, and Mach at a stated air temperature. Do not silently treat a variable or ambiguous quantity as exact.
- Add angle, data rate, fuel economy, and cooking-volume support. Angle covers turns, degrees, radians, gradians, arcminutes, and arcseconds. Data rate distinguishes decimal SI and binary IEC prefixes and bits from bytes. Fuel economy includes L/100 km, km/L, U.S. mpg, and Imperial mpg; conversions use the required reciprocal formulas and reject zero/negative inputs where the result is undefined or physically invalid. Cooking volume clearly labels U.S. customary teaspoon, tablespoon, cup, fluid ounce, pint, quart, and gallon, with metric millilitres and litres. Cooking measures are part of the volume dimension: the existing Volume tab keeps all volume units, while a Cooking tab shows a focused kitchen subset and both use one canonical volume converter. This lets the quick parser resolve shared units such as `cup` and `ml` without guessing between categories. These conventions are explicit so the same label never hides a regional definition.
- Keep converter functions deterministic and side-effect free. Reject unknown unit codes with a clear `ValueError`. Reject non-finite values at the shared input boundary and do not let invalid input raise into Tk callbacks. Kelvin values below absolute zero are invalid.
- Add a reference-value assertion using `pytest.approx` for each unit definition, and parameterized round-trip checks for every ordered pair in each category. Add focused tests for aliases, nonlinear fuel-economy conversions, malformed expressions, non-finite numbers, and invalid physical values.

### Type-to-convert

Add a labelled expression entry near the main title, with an example hint and a Convert action. Accept a number, source unit, `to` or `in`, and target unit, including the two README examples. A pure parser resolves case-insensitive full names and documented aliases. Unit resolution must yield exactly one category; ambiguous or unknown input gives an actionable status message rather than choosing silently. The parsed conversion uses the same category conversion function as the tab and records a successful conversion in history. Keep existing tabs available as the discoverable fallback.

### Saved settings and history

Persist precision, scientific notation, and up to ten recent conversions as versioned JSON under the operating system's per-user application-data directory (XDG config/data on Linux, Application Support on macOS, and Local AppData on Windows). No account or network access is introduced. Write atomically using a temporary file and replace. If the file is absent, use current defaults. If data is malformed or inaccessible, continue with defaults/in-memory state, show a concise status, and avoid destroying the unreadable file. Save on settings changes and clean shutdown; cap and validate loaded history.

### CI and distribution

- Use maintained GitHub Actions, a supported common Python version, and one clear required test/lint workflow. Fix the incomplete HTML coverage workflow or remove duplicate coverage jobs in favor of a single coverage artifact.
- Build and exercise the GUI in a Linux virtual display in CI. Run conversion/parser/storage tests without a display. Test Windows/macOS package creation on their native GitHub runners.
- Produce a Windows executable, a signed and timestamped Windows release artifact, a signed/notarized macOS application bundle, and a Linux AppImage. Replace unpinned downloads and the personal auto-tag token with pinned or maintained tooling and least-privilege `GITHUB_TOKEN` permissions. Make tag and release triggers deterministic and prevent a failed build from publishing partial releases.
- Add explicit signing steps that fail clearly for a release when required credentials are missing. Windows signing needs a publisher certificate (PFX and password); macOS signing/notarization needs a Developer ID certificate, Apple team/account details, and an app-specific password. Store these only as repository Actions secrets. Unsigned local builds remain possible. Signing cannot guarantee the absence of antivirus warnings.
- Run the frozen app on each supported runner as a smoke check before attaching the artifact. Include checksums and versioned release notes/artifacts.

### Documentation and repository guidance

Update the README with all four new categories, parser examples, definitions for regional/convention-based units, preference storage locations, development/test commands, and release/signing setup. Remove the advice to ignore Windows Defender warnings. Update `AGENTS.md` so its commands, category list, tests, and resolved known issues describe the completed implementation rather than stale defects.

## Calls left to the implementer

- Keep the current UI's native look and tab workflow; add only the expression field and four category tabs.
- Keep user data local and bounded; storage errors must not prevent conversions.
- Preserve the two legacy API spellings/codes where their old interpretation does not conflict with the corrected SI symbols; document the unavoidable `dg` semantic correction.
- Leave signing values to repository maintainers. Release CI should identify missing credentials instead of publishing an unsigned artifact under a signed-release promise.

## Acceptance criteria

- Every README roadmap item is implemented or, for signing, has a complete tested workflow awaiting maintainer-provided credentials; no unsigned build is described as signed or warning-free.
- Every issue in the current `AGENTS.md` known-issues list is resolved and the file is updated.
- All supported unit codes and aliases have reference tests; all pairs have round-trip tests with appropriate tolerances.
- Valid expression examples produce the expected values, while ambiguous/malformed inputs display guidance without callback exceptions.
- Settings/history survive an application restart; corrupt or unavailable settings do not crash the app or erase user data.
- CI passes conversion, parser, storage, GUI smoke, lint, and packaging checks available without signing secrets. A signed release succeeds when the required credentials are configured.
- The app runs from source and packaged artifacts on the supported OS runners. Documentation matches observed behavior.

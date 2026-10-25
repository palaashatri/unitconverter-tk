# Conversion Reliability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every current and new converter numerically correct, explicit about unit conventions, and covered by reference and round-trip tests.

**Architecture:** Keep each category's math in a pure `src/convert_*.py` module with `convert(amt: float, frm: str, to: str) -> float`. Shared validation lives in `src/conversion_utils.py`; factors are relative to a stated base unit, with explicit formula converters for temperature, angle, and fuel economy.

**Tech Stack:** Python standard library, pytest, pytest.approx.

**Spec:** [2026-10-25-unitconverter-production-readiness-design.md](../specs/2026-10-25-unitconverter-production-readiness-design.md)

## Global Constraints

- Keep conversion math free of Tk imports.
- Use exact reference assertions with `pytest.approx` and round-trip checks for every ordered unit pair.
- Reject unknown unit codes with `ValueError` and non-finite amounts with `ValueError`.
- Keep decimal SI and binary IEC data-rate units distinct.
- Label convention-based units explicitly; never present an assumed convention as universal.
- Correct `dg` to decigram and `dag` to decagram; retain `deg` as a decigram alias.
- Correct the international mile to exactly 1609.344 metres.
- Correct `mm` area code to `sqmm`, retaining `mm` as an alias.
- Export `convert_celToKel`; retain `covert_celToKel` as a deprecated alias.
- Fuel-economy inputs must be positive; zero and negative values have no finite, physically valid reciprocal conversion.

## Review Focus

- A finite input near zero in electronvolts or barns must retain a useful relative tolerance; reference tests use category-appropriate relative tolerance rather than an overly large absolute tolerance.
- A zero, negative, NaN, or infinity fuel-economy amount must raise `ValueError`, including conversion between two reciprocal units.
- `Torr` and `mmHg` remain different definitions even though their values are close; tests pin each to its own reference.
- `mpg` means U.S. miles per U.S. gallon only; Imperial mpg must be explicit in labels and aliases.
- Exact factors that use π or defining ratios must round-trip within floating-point tolerance rather than compare with `==`.

---

### Task 1: Add shared numeric validation and baseline regression tests

**Files:**
- Create: `src/conversion_utils.py`
- Create: `test/test_conversion_validation.py`

**Interfaces:**
- Produces: `require_finite(amt: float) -> float`, raising `ValueError` for NaN and infinities.
- Consumes: None.

- [x] **Step 1: Write failing tests** for finite positive/negative/zero values and NaN/positive infinity/negative infinity.
- [x] **Step 2: Run** `pytest test/test_conversion_validation.py -q`; expect the helper to be missing.
- [x] **Step 3: Implement** `require_finite` using `math.isfinite`; do not add Tk or formatting behavior.
- [x] **Step 4: Run** `pytest test/test_conversion_validation.py -q`; expect all helper tests to pass.
- [x] **Step 5: Commit** `test: define numeric validation contract`.

### Task 2: Correct existing factors, identifiers, and temperature API

**Files:**
- Modify: `src/convert_area.py`, `src/convert_digital.py`, `src/convert_energy.py`, `src/convert_length.py`, `src/convert_pressure.py`, `src/convert_speed.py`, `src/convert_temp.py`, `src/convert_time.py`, `src/convert_volume.py`, `src/convert_weight.py`
- Modify: `src/weight.py`, `src/area.py`, `src/temperature.py`
- Create: `test/test_existing_conversion_references.py`

**Interfaces:**
- Consumes: `require_finite` from Task 1.
- Produces: existing `convert` signatures with `ValueError` for unknown units; `convert_celToKel`; corrected labels and backward-compatible aliases.

- [x] **Step 1: Update** the five existing tests to use `pytest.approx` and `convert_celToKel`; then write failing reference tests for every existing displayed unit, weight `dag`/`dg` plus legacy `deg`, square millimetre `sqmm` plus `mm`, 1 international mile = 1609.344 m, all temperature formula pairs, Kelvin below absolute zero rejection, and all ordered pairs in each converter. Pin exact definitions: US customary liquid volume; thermochemical calorie; IT BTU; foot-pound force; Torr = 101325/760 Pa; mmHg = 133.322387415 Pa; Gregorian-average year = 365.2425 days and month = one twelfth of that year; Mach at dry air 20 °C = 343.2 m/s. Use positive representative values and `pytest.approx` relative tolerance `1e-9`, with category-specific tolerance only where floating-point scale requires it. Document factors in test names or comments with the referenced standard/definition.
- [x] **Step 2: Run** `pytest test/test_existing_conversion_references.py test/test_pytest.py -q`; expect failures for current definitions and missing corrected names.
- [x] **Step 3: Implement** the reference factors and shared finite/unknown-code validation in existing pure conversion modules. Change the weight UI to `dag`/`dg`; label average calendar periods and Mach's reference condition; preserve aliases only where unambiguous.
- [x] **Step 4: Run** `pytest test/test_existing_conversion_references.py test/test_pytest.py -q`; expect all reference and pair checks to pass.
- [x] **Step 5: Commit** `fix: correct existing conversion definitions`.

### Task 3: Add exact angle and data-rate converters

**Files:**
- Create: `src/convert_angle.py`, `src/convert_data_rate.py`
- Create: `test/test_convert_angle.py`, `test/test_convert_data_rate.py`

**Interfaces:**
- Consumes: `require_finite` from Task 1.
- Produces: pure `convert(amt, frm, to) -> float`, `factors`, and stable canonical codes for the registry/UI.

- [x] **Step 1: Write failing tests** for radians, degrees, gradians, turns, arcminutes, arcseconds; base-10 bit/s and byte/s through Tbit/s and Tbyte/s; base-2 Kibit/s through Tibit/s and KiB/s through TiB/s. Include references for every unit and round trips for every ordered pair. Pin references: one turn = 2π radians, 360 degrees, 400 gradians; one byte = 8 bits; SI prefixes use powers of 1000 and IEC prefixes powers of 1024.
- [x] **Step 2: Run** `pytest test/test_convert_angle.py test/test_convert_data_rate.py -q`; expect import/module failures.
- [x] **Step 3: Implement** factor-based conversion using `math.pi` and shared validation; reject unknown codes with `ValueError`.
- [x] **Step 4: Run** both module tests; expect all references and pairs to pass.
- [x] **Step 5: Commit** `feat: add angle and data-rate conversions`.

### Task 4: Add fuel-economy and cooking-volume converters

**Files:**
- Create: `src/convert_fuel_economy.py`
- Modify: `src/convert_volume.py` to add cooking-volume units to the existing volume dimension
- Create: `test/test_convert_fuel_economy.py`
- Modify: `test/test_existing_conversion_references.py` to cover cooking measures

**Interfaces:**
- Produces: `convert(amt, frm, to) -> float`, `factors`/unit definitions, and stable codes.
- Consumes: `require_finite` from Task 1.

- [x] **Step 1: Write failing tests** for U.S. mpg, Imperial mpg, km/L, L/100 km, and cooking mL/L plus U.S. customary tsp/tbsp/cup/fl oz/pint/quart/gallon. Include a reference for every unit and round trips for every ordered pair. Pin US gallon = exactly 3.785411784 L; 1 US cup = 8 US fluid ounces; 1 US tablespoon = 1/2 US fluid ounce; 1 teaspoon = 1/3 US tablespoon; distinguish Imperial gallon. Test both direct and reciprocal formulas and zero/negative rejection.
- [x] **Step 2: Run** `pytest test/test_convert_fuel_economy.py test/test_existing_conversion_references.py -q`; expect failures for missing fuel-economy conversions and inexact cooking factors.
- [x] **Step 3: Implement** fuel economy with canonical L/100 km conversions derived from the exact mile and gallon definitions: U.S. mpg uses `100 * 3.785411784 / 1.609344`, Imperial mpg uses `100 * 4.54609 / 1.609344`; km/L and all inverse conversions use reciprocals. Add cooking-volume factors to `convert_volume.py` relative to mL with explicit U.S. customary definitions.
- [x] **Step 4: Run** `pytest test/test_convert_fuel_economy.py test/test_existing_conversion_references.py -q`; expect all references and pairs to pass.
- [x] **Step 5: Commit** `feat: add fuel-economy and cooking conversions`.

### Task 5: Verify complete math coverage and source references

**Files:**
- Modify: conversion tests created in Tasks 1–4
- Create: `docs/unit-definitions.md`

**Interfaces:**
- Consumes: all converter modules from Tasks 2–4.
- Produces: a user-readable unit convention/reference catalog.

- [x] **Step 1: Review** that the reference-value dictionaries cover the complete public unit-code sets and pair parametrizations range over every ordered pair, including identity pairs.
- [x] **Step 2: Document** the named standards and conventions for every factor, including ambiguous units and the Mach/calendar assumptions.
- [x] **Step 3: Run** `pytest -q`; expect every pure conversion and validation test to pass.
- [x] **Step 4: Commit** `test: cover all conversion units and pairs`.

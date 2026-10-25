# Unit Converter Production Readiness Plan

This implementation is split into three independently reviewable plans because the design covers conversion math, desktop UX/persistence, and release engineering.

1. [Conversion reliability](2026-10-25-conversion-reliability.md) audits existing factors, corrects known issues, adds the four new conversion domains, and verifies every unit and pair.
2. [Desktop experience](2026-10-25-desktop-experience.md) adds local settings/history, the expression field, and the four new UI tabs. It depends on the pure converters from plan 1.
3. [Release and documentation](2026-10-25-release-and-documentation.md) modernizes CI, adds signed release paths and package checks, and updates user/maintainer instructions. It depends on plans 1 and 2.

The signing portion can be implemented and checked without credentials, but successful signed publication requires maintainers to configure the Windows publisher certificate and Apple Developer ID/notarization secrets in repository settings.

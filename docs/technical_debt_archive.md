# Technical Debt Archive

Resolved entries moved from [technical_debt.md](technical_debt.md), appended in resolution order (the archive doubles as a chronological account of what has been paid down). Each keeps its original TD number forever (numbers are never reused), keeps its original **Why**, and replaces **Fix** with `**Resolved:** YYYY-MM-DD (PR #n)` plus a pointer to wherever the lasting content now lives.

---

## TD-001: Release v1.0 — `ledgerboard.py`, `SPEC.md` and fixtures, moved out of dev-cadence's scripts

**Priority:** High
**Type:** feature
**Added:** 2026-10-12
**Status:** Resolved 2026-10-12.
**Resolved:** 2026-10-12 — v1.0 released (PR #2, the release PR); dev-cadence's suite passes against it (its TD-106).
**Location:** `ledgerboard.py`, `SPEC.md`, `fixtures/`, `tests/`, `release.sh` (all new)

**Why:** the ledger and board formats are parsed twice today, once in dev-cadence's scripts and once in ShiftLead, held together by parity tests on one side; that is where the two drift. ShiftLead's ADR 2026-10-12 (*Builds*, row 1) moves the formats here so there is one parser.

**Fix:** resolved 2026-10-12 — `ledgerboard.py`, `SPEC.md`, `fixtures/` and `release.sh` carry it.

**Done when** v1.0 is tagged and dev-cadence's ledger, board, parity and check-cadence suites pass unchanged against it in the vendoring branch.

**Related:** ShiftLead ADR 2026-10-12; dev-cadence's vendoring entry (filed with this release).

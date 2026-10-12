# Technical Debt

Known issues, compromises, and deferred work. Add an entry any time a problem is identified but not immediately fixed — no exceptions, however small (see [`cadence.md`](cadence.md) §2).

**This file holds open work only.** The summary table below lists exactly the entries that have a body in this file — one row each, no history. When an entry is fully resolved, move the whole body to [`technical_debt_archive.md`](technical_debt_archive.md), delete its summary row, and replace **Fix** with the resolution date plus a pointer to whichever doc/code now carries the lasting content. An entry that is only *partly* resolved stays here, with what shipped and what remains spelled out in its **Status**.

IDs are `TD-` plus a zero-padded three-digit number, assigned in order and never reused. Priority is a field, never part of the ID.

An entry's fields are the `**Name:** value` lines right under its heading, up to the first blank line (cadence.md §2). To add this repo's own fields, declare their values on one line here, e.g. `Fields: Owner = grinder | designer; Kind = build | design-first` — `scripts/ledger.py --list --owner grinder` and `--fields` then read them.

---

## Summary

| ID | Title | Priority | Status |
|----|-------|----------|--------|
| TD-001 | Release v1.0: `ledgerboard.py`, `SPEC.md` and fixtures, moved out of dev-cadence's scripts | High | Built — release pending |

---

## TD-001: Release v1.0 — `ledgerboard.py`, `SPEC.md` and fixtures, moved out of dev-cadence's scripts

**Priority:** High
**Type:** feature
**Added:** 2026-10-12
**Status:** Built (PR #2: the module, SPEC.md, fixtures, tests, CI, release.sh); open until the v1.0 release PR, which archives this entry, merges and v1.0 is tagged. dev-cadence's whole suite passes against it in its TD-106 branch.
**Location:** `ledgerboard.py`, `SPEC.md`, `fixtures/`, `tests/`, `release.sh` (all new)

**Why:** the ledger and board formats are parsed twice today, once in dev-cadence's scripts and once in ShiftLead, held together by parity tests on one side; that is where the two drift. ShiftLead's ADR 2026-10-12 (*Builds*, row 1) moves the formats here so there is one parser.

**Fix:** the ADR's *The ledgerboard API*, in full. Move, do not rewrite, from dev-cadence `files/scripts/`: `ledger.py`'s parsing (header block, `Fields:`, `ROW_RE`, `Blocked by`, pickable — with the cross-repo resolver made a parameter, `resolve(item) -> (state, why)`), `nudge_user_attention.py`'s board readers (`parse_board` and its helpers, the item record, `item_key`/`item_refs`/`item_head`/`detail_block`/`closed_items`, `KIND_RE`, `ARCHIVE_AT`, the `Answers:` grammar), `board_edit.py`'s `edit_line()` and commit subject, and `check_cadence.py`'s subject and stamp parsers; add `item_line`/`decided_line`, the line predicates, and the `Ledgerboard: <major>` version line. Also: `edit_line()`'s four edits (snooze, done, reply, decide); `subject(tool, action, …)` for those and `append`, with the parser `check_cadence.py`'s `board-edit` and `board-append` classes use, which also reads the three `shiftlead: board|answer|board decide …` insert subjects ShiftLead writes today; the `**Tracker:**` field and any preamble `Name: value` line it does not know kept byte-for-byte by every edit. No person's or machine's name survives the move, and no logic that knows a consumer — the release header's SYNCED FILE line and those legacy subjects are the two named exceptions. `SPEC.md` from the seed templates' format paragraphs and cadence §2/§3's format rules. Invented fixtures, generated from dev-cadence's format tests. `release.sh` writes `# ledgerboard v<x.y> sha256:<rest>` and the SYNCED FILE line, commits and tags. CI runs the suite and the fixtures.

**Done when** v1.0 is tagged and dev-cadence's ledger, board, parity and check-cadence suites pass unchanged against it in the vendoring branch.

**Related:** ShiftLead ADR 2026-10-12; dev-cadence's vendoring entry (filed with this release).

---

<!-- Entry template:

## TD-001: Short title of the problem

**Priority:** High | Medium | Low
**Type:** (optional) debt | feature — omit for debt; within a Priority, debt is picked first (cadence.md §2)
**Added:** YYYY-MM-DD
**Status:** Open
**Blocked by:** (optional) TD-NNN or <repo>#TD-NNN, … then decision (<who>) and a pointer — omit when nothing blocks it; pickable is derived (cadence.md §2)
**Location:** `path/to/file.py` (function/section)

**Why:** what's wrong, how it was found, and the reasoning — future sessions need the why, not just the symptom.

**Fix:** concrete direction(s), and what would count as done.

**Related:** other TDs, PRs, decision docs.
-->

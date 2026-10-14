# Technical Debt

Known issues, compromises, and deferred work. Add an entry any time a problem is identified but not immediately fixed — no exceptions, however small (see [`cadence.md`](cadence.md) §2).

**This file holds open work only.** The summary table below lists exactly the entries that have a body in this file — one row each, no history. When an entry is fully resolved, move the whole body to [`technical_debt_archive.md`](technical_debt_archive.md), delete its summary row, and replace **Fix** with the resolution date plus a pointer to whichever doc/code now carries the lasting content. An entry that is only *partly* resolved stays here, with what shipped and what remains spelled out in its **Status**.

IDs are `TD-` plus a zero-padded three-digit number, assigned in order and never reused. Priority is a field, never part of the ID.

An entry's fields are the `**Name:** value` lines right under its heading, up to the first blank line (cadence.md §2). To add this repo's own fields, declare their values on one line here, e.g. `Fields: Owner = grinder | designer; Kind = build | design-first` — `scripts/ledger.py --list --owner grinder` and `--fields` then read them.

---

## Summary

| ID | Title | Priority | Status |
|----|-------|----------|--------|
| TD-002 | Read a board line's bold head and a live look's `Not right: <what>` form (v1.1) | Medium | Open |

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

## TD-002: Read a board line's bold head and a live look's `Not right: <what>` form (v1.1)

**Priority:** Medium
**Type:** feature
**Added:** 2026-10-13
**Status:** Open
**Location:** `ledgerboard.py` (beside `edit_head`, `LIVE_LOOK_ANSWERS`), `SPEC.md` *The board*, `fixtures/`

**Why:** ShiftLead's TD-585 left it with two board readings v1.0 does not provide, so it still has its own patterns for them, against the ADR's *no second parser* (ShiftLead `docs/decisions/2026-10-12-ledgerboard-dev-cadence-shiftlead.md`). (1) **The bold head:** an item's first `**…**` run, the line's title — ShiftLead's `board.HEAD_RE` (`\*\*(?P<head>.+?)\*\*`) feeds the Inbox's `board_head`, `workorders.head` (a work order's title) and `agent_inbox`'s reply mail; when there is none they fall back to the whole line. v1.0's `edit_head` is a different thing (prefix and fields dropped, bold removed, clipped at 60) and its own `HEAD_RE` is the `(session …)` prefix, so neither answers. (2) **The `Not right: <what>` form:** `LIVE_LOOK_ANSWERS` names the pair, but nothing says whether an offered answer *is* the form (`Not right:` alone or with a `<…>` placeholder) as opposed to a complete answer like `Not right: wrong repo`, nor whether a typed answer fills it. ShiftLead's `board.NOT_RIGHT_FORM` (`Not right:\s*(<[^<>]*>)?`, fullmatched) decides both, in `inbox.py`'s live-look check and `agent_inbox`'s decide.

**Fix:** a minor release, v1.1 (nothing a v1.0 reader reads changes; the item key is untouched):
- `bold_head(text) -> str | None` — the item text's first bold run, whitespace-collapsed, outside a reply's words (as `edit_head` cuts them), else `None`; the caller chooses its fallback and clipping. SPEC: one sentence under *The board*.
- `is_not_right_form(answer) -> bool` and `fills_not_right(said, offered) -> str | None` (or one function that returns the filled answer or a `Refused`): an offered answer is the form when it is `Not right:` optionally followed by one `<…>` placeholder; a said answer fills it when it starts `Not right:` and carries words that are not the placeholder. SPEC: a sentence on *Answers* for a `look`.
- fixtures for each (a line with no bold, bold inside a reply, two bold runs; the form with and without a placeholder, a complete `Not right: wrong repo`, an empty fill), then `./release.sh 1.1` and `--tag 1.1`.
- Then dev-cadence vendors v1.1 (`vendor_ledgerboard.sh`) and ShiftLead's TD-585 swaps `board.HEAD_RE`/`NOT_RIGHT_FORM` for these calls and closes.

**Related:** ShiftLead TD-585 (blocked by this entry), its slices #1647–#1674; dev-cadence TD-106 (archived — the v1.0 vendoring); TD-001 (v1.0, archived).

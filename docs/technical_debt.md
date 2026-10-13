# Technical Debt

Known issues, compromises, and deferred work. Add an entry any time a problem is identified but not immediately fixed — no exceptions, however small (see [`cadence.md`](cadence.md) §2).

**This file holds open work only.** The summary table below lists exactly the entries that have a body in this file — one row each, no history. When an entry is fully resolved, move the whole body to [`technical_debt_archive.md`](technical_debt_archive.md), delete its summary row, and replace **Fix** with the resolution date plus a pointer to whichever doc/code now carries the lasting content. An entry that is only *partly* resolved stays here, with what shipped and what remains spelled out in its **Status**.

IDs are `TD-` plus a zero-padded three-digit number, assigned in order and never reused. Priority is a field, never part of the ID.

An entry's fields are the `**Name:** value` lines right under its heading, up to the first blank line (cadence.md §2). To add this repo's own fields, declare their values on one line here, e.g. `Fields: Owner = grinder | designer; Kind = build | design-first` — `scripts/ledger.py --list --owner grinder` and `--fields` then read them.

---

## Summary

| ID | Title | Priority | Status |
|----|-------|----------|--------|
| TD-002 | Board items have no identifier: a person quotes an item's text to refer to it, and a reword loses the reference | Medium | Open |

---


## TD-002: Board items have no identifier: a person quotes an item's text to refer to it, and a reword loses the reference

**Priority:** Medium
**Type:** feature
**Added:** 2026-10-12 (ShiftLead's ao-paul, at Paul's ask)
**Status:** Open
**Location:** `SPEC.md` *The board* (an item, the item key, *Edits*: `item_line`); `ledgerboard.py` (the item parser, `item_line`, the edits' find); the fixtures

**Why:** Paul, 2026-10-12: *should we add identifiers to the user attention items — that way I don't have to quote it to reference it?* A ledger entry has `TD-NNN` and ShiftLead's mail has an id, but a board item has only its date, its head and its words. To point a session at an item, or ask about one in chat, the person pastes its text; and a consumer finds the item for an edit by its text (ShiftLead's `board.py` `_find`: the line number, then the whole line), so an item reworded since it was read is refused as moved. The format is this repo's (ShiftLead's ADR 2026-10-12), so the id is defined here and both consumers read it with no parser of their own.

**Fix:**
- Define the id: a short written token, e.g. `UA-12`, numbered per board in order and never reused (the board's archive included), placed in a fixed spot on the item (after the checkbox and kind, before the date, is one candidate). Written at creation by `item_line`, which needs the next number from the board and its archive.
- The item key: the SPEC says a key's shape for a given line is part of the format and changing it is a new major. An item written with an id keeps the id in its key (stable, since replies, `Decided:` and `Closed:` are already outside the key); an item written before it has no id and its key is unchanged, so **no backfill** of existing items, and v1 readers must still read a line that carries one (a minor release only if an older v1 reader tolerates the token; otherwise this is v2 — decide which and say it in *Versions*).
- The edits: find an item by its id first, then as today; `snooze`, `done`, `decide` and `reply` take an id.
- Fixtures: an item with an id, one without, an id on a closed item, a duplicated id (reported).
- Done when a new item carries an id, every edit can address an item by it, old items read and edit as before, and the release is tagged for the consumers to vendor.

**Related:** ShiftLead TD-603 (draws and accepts the id: the Inbox, the Due strip, `board_reply`), ShiftLead TD-584/TD-585 (vendoring ledgerboard), dev-cadence TD-106 (dev-cadence's vendoring; its `board_edit.py` and nudge hook print the id once vendored).

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

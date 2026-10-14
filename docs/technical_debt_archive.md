# Technical Debt Archive

Resolved entries moved from [technical_debt.md](technical_debt.md), appended in resolution order (the archive doubles as a chronological account of what has been paid down). Each keeps its original TD number forever (numbers are never reused), keeps its original **Why**, and replaces **Fix** with `**Resolved:** YYYY-MM-DD (PR #n)` plus a pointer to wherever the lasting content now lives.

---

## TD-001: Release v1.0 — `ledgerboard.py`, `SPEC.md` and fixtures, moved out of dev-cadence's scripts

**Priority:** High
**Type:** feature
**Added:** 2026-10-12
**Status:** Resolved 2026-10-12.
**Resolved:** 2026-10-12 (PR #3) — v1.0 released; the module was built in PR #2; dev-cadence's suite passes against it (its TD-106).
**Location:** `ledgerboard.py`, `SPEC.md`, `fixtures/`, `tests/`, `release.sh` (all new)

**Why:** the ledger and board formats are parsed twice today, once in dev-cadence's scripts and once in ShiftLead, held together by parity tests on one side; that is where the two drift. ShiftLead's ADR 2026-10-12 (*Builds*, row 1) moves the formats here so there is one parser.

**Fix:** resolved 2026-10-12 — `ledgerboard.py`, `SPEC.md`, `fixtures/` and `release.sh` carry it.

**Done when** v1.0 is tagged and dev-cadence's ledger, board, parity and check-cadence suites pass unchanged against it in the vendoring branch.

**Related:** ShiftLead ADR 2026-10-12; dev-cadence's vendoring entry (filed with this release).

## TD-002: Read a board line's bold head and a live look's `Not right: <what>` form (v1.1)

**Priority:** Medium
**Type:** feature
**Added:** 2026-10-13
**Status:** Resolved 2026-10-14.
**Resolved:** 2026-10-14 (PR #10) — v1.1 released; built in PR #9 (`bold_head`, `is_not_right_form`, `fill_not_right`; SPEC *The bold head* and the `look` form). For ShiftLead's swap (its TD-585), the review of #9 named what is not drop-in: `fill_not_right` returns None where `_board_answer` refuses (keep its word-for-word check first and its own refusal on None), and refuses a placeholder-only fill (`Not right: <b>`) it accepted; a blank `** **` is no head, so `board_head`/`agent_inbox` fall back to the line and `workorders.head` to its own; `workorders.head` keeps its clipping and `rstrip(" .")`.
**Location:** `ledgerboard.py` (beside `edit_head`, `LIVE_LOOK_ANSWERS`), `SPEC.md` *The board*, `fixtures/`

**Why:** ShiftLead's TD-585 left it with two board readings v1.0 does not provide, so it still has its own patterns for them, against the ADR's *no second parser* (ShiftLead `docs/decisions/2026-10-12-ledgerboard-dev-cadence-shiftlead.md`). (1) **The bold head:** an item's first `**…**` run, the line's title — ShiftLead's `board.HEAD_RE` (`\*\*(?P<head>.+?)\*\*`) feeds the Inbox's `board_head` and `agent_inbox`'s reply mail, which fall back to the whole line; `workorders.head` (a work order's title) has its own copy of the pattern and falls back to the text after `(session …) — `. Each scans the whole line, reply words included. v1.0's `edit_head` is a different thing (prefix and fields dropped, bold removed, clipped at 60) and its own `HEAD_RE` is the `(session …)` prefix, so neither answers. (2) **The `Not right: <what>` form:** SPEC fixes the pair (`Answers: Works | Not right: <what>.`) and `LIVE_LOOK_ANSWERS` names it, but neither says how a reader tells the form from a complete answer like `Not right: wrong repo` — ShiftLead also accepts bare `Not right:` and any one `<…>` placeholder — nor whether a typed answer fills it. ShiftLead's `board.NOT_RIGHT_FORM` (`Not right:\s*(<[^<>]*>)?`, fullmatched) decides both, in `inbox.py`'s live-look check and `agent_inbox`'s decide.

**Fix:** resolved 2026-10-14 — `ledgerboard.py` (`bold_head`, `is_not_right_form`, `fill_not_right`), `SPEC.md` *The bold head* and the `look` form, `fixtures/edit/cases.json`; released as v1.1 (PR #10). Consumers take it with dev-cadence's `vendor_ledgerboard.sh v1.1`; ShiftLead's swap is its TD-585.

**Related:** ShiftLead TD-585 (blocked by this entry), its slices #1647–#1674; dev-cadence TD-106 (archived — the v1.0 vendoring); TD-001 (v1.0, archived).

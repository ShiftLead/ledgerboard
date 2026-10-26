# Technical Debt

Known issues, compromises, and deferred work. Add an entry any time a problem is identified but not immediately fixed — no exceptions, however small (see [`cadence.md`](cadence.md) §2).

**This file holds open work only.** The summary table below lists exactly the entries that have a body in this file — one row each, no history. When an entry is fully resolved, move the whole body to [`technical_debt_archive.md`](technical_debt_archive.md), delete its summary row, and replace **Fix** with the resolution date plus a pointer to whichever doc/code now carries the lasting content. An entry that is only *partly* resolved stays here, with what shipped and what remains spelled out in its **Status**.

IDs are `TD-` plus a zero-padded three-digit number, assigned in order and never reused. Priority is a field, never part of the ID.

An entry's fields are the `**Name:** value` lines right under its heading, up to the first blank line (cadence.md §2). To add this repo's own fields, declare their values on one line here, e.g. `Fields: Owner = grinder | designer; Kind = build | design-first` — `scripts/ledger.py --list --owner grinder` and `--fields` then read them.

---

## Summary

| ID | Title | Priority | Status |
|----|-------|----------|--------|
| TD-003 | PRs are checked by GitHub Actions, whose minutes the account's repos share and which have stopped: gate on a local `precheck` | Medium | Open — decided 2026-10-26 (Paul: every repo moves to precheck) |

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

## TD-003: PRs are checked by GitHub Actions, whose minutes the account's repos share and which have stopped: gate on a local `precheck`

**Priority:** Medium
**Added:** 2026-10-26 (Paul; drafted by session `memory-vs-cadence`)
**Status:** Open
**Location:** `.github/workflows/ci.yml` (`on: pull_request`, push to `main`, tags `v*`); `docs/cadence.toml` (no `precheck` key); `AGENTS.md`; dev-cadence `cadence.md` §4.12 and TD-148

**Why:** GitHub Actions stopped on the shared account (ShiftLead org from 2026-10-26: *recent account payments have failed or your spending limit needs to be increased*), and Paul decided every repo gates on a local `precheck` instead (dev-cadence TD-148): the minutes are one pool across all the repos, kept for what has to run on GitHub. This repo's `ci.yml` runs `ruff check .`, the unit tests and the fixtures on every pull request and push to `main`, so its PRs now read red for a reason that says nothing about the code. The tag job — a release's module carries its header — is the one that belongs on GitHub.

**Fix:** `precheck = "ruff check . && python3 -m unittest discover -s tests && python3 fixtures/run.py"` in `docs/cadence.toml` (the merge gate runs it with `dev-cadence run precheck.py --pr <n>`, recording `cadence/precheck`); `ci.yml` keeps the tag trigger and `workflow_dispatch`, and drops `pull_request` and the push to `main`; `AGENTS.md` names the gate. Done when a PR's gate reads a green `cadence/precheck` and no workflow runs on `pull_request`.

**Related:** dev-cadence TD-148 (the convention), samscrape TD-465, shiftlead TD-1033.

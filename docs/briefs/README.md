# Briefs for the lb-grind team

A **brief** is the opening prompt of an unattended session. `ao team start lb-grind` (ShiftLead, on
the person's machine) reads the team in this repo's `.shiftlead.yml`, starts each seat in its own
worktree under `.claude/worktrees/<name>`, and hands it ShiftLead's built-in template for its role
with the file named there filled into the template's *This repo's rules* section. **These files are
supplements, not whole briefs**: every ShiftLead mechanic (claims, the review loop, asking, the
end-of-run declarations) is the template's. A file here holds only what ledgerboard does
differently, and where it and the template disagree it wins, so a rule copied from the template
goes stale and then overrides the newer one.

| File | Seat | Notes |
|---|---|---|
| `manager-lb-1.md` | manager | watches the grinder and the cadence check's readings; creates no work |
| `techlead-context.md` | techlead | **not a brief**: the primer the techlead reads first on every fill |
| `grinder-lb-1.md` | grinder | `free-pick` from `agent-cadence run ledger.py --pickable` |
| `designer-lb-1.md` | designer | the `design-first` entries: a design is a plan in `docs/plans/` and the entry's Fix |

**Why the team exists.** It runs the `td` flow: the designer takes the entries Paul marks `**Kind:** design-first`, runs their review rounds and, on his go, files their builds; the grinder builds everything else that is pickable; the techlead reads and merges PRs on the held paths. An entry designed in conversation with Paul carries no Kind and goes straight to the grinder. An entry blocked on `decision (Paul)` is no seat's.

Treat every brief as stale by default: check a rule against `AGENTS.md`, `SPEC.md` and the pinned
`cadence.md` (`agent-cadence path cadence.md`) before leaning on it.

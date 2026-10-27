# ledgerboard

The ledger and board formats, defined once.

A **ledger** (`docs/technical_debt.md`) holds a repo's deferred work as `TD-NNN` entries; a **board**
(`docs/user_attention.md`) holds what is waiting on a person. This repo is their single definition:

- `SPEC.md` — the formats, in prose.
- `ledgerboard.py` — one stdlib-only Python module that parses, checks and edits them. Pure functions over
  text: no git, no network, no knowledge of any repo or machine.
- `fixtures/` — language-neutral conformance cases (a Markdown input and its expected JSON), so a reader in
  any language can prove it reads the formats the same way.

It is consumed by [dev-cadence](https://github.com/ShiftLead/dev-cadence) (how a repo works, for any agent
or a person) and [ShiftLead](https://github.com/ShiftLead/shiftlead) (how many sessions are run). Neither
depends on the other; both depend on this. (dev-cadence is private until its public scrub.) The rule that keeps them in step: **no second parser** — every
reader and writer of a ledger or board calls `ledgerboard.py`.

Releases are tagged; each consumer vendors the file, whose first line names its release and hash. Why it
is shaped this way: [ShiftLead ADR 2026-10-12](https://github.com/ShiftLead/shiftlead/blob/main/docs/decisions/2026-10-12-ledgerboard-dev-cadence-shiftlead.md).

**Status:** released — v1.0, then v1.1 (a board item's bold head and the live look's `Not right: <what>` form), then v1.2 (the rank: cards, keys, the rank file, and the pick order it gives), then v1.3 (an answer says what it leads to: `<label> (default) — <consequence>`); then v2.0 (the ledger as a directory, one file per entry: `load()`, `split()`, `v2_problems()`); the tags are the releases.

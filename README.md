# ledgerboard

The ledger and board formats, defined once.

A **ledger** (`docs/technical_debt.md`) holds a repo's deferred work as `TD-NNN` entries; a **board**
(`docs/user_attention.md`) holds what is waiting on a person. This repo is their single definition:

- `SPEC.md` — the formats, in prose.
- `ledgerboard/` — one stdlib-only Python package, vendored whole. `__init__.py` is the module that parses,
  checks and edits them: pure functions over text, no git, no network, no knowledge of any repo or machine.
  Beside it, the file-level writers: `board.py` (v2.3, the board and rank writer) and, to come, `ledger.py`; they read and write the
  files they are given and nothing else — never git, the network, the roster, forges, trackers, delivery,
  sweeps, sessions, or logic that knows either consumer.
- `fixtures/` — language-neutral conformance cases (a Markdown input and its expected JSON), so a reader in
  any language can prove it reads the formats the same way.

It is consumed by [agent-cadence](https://github.com/ShiftLead/agent-cadence) (how a repo works, for any agent
or a person) and [ShiftLead](https://github.com/ShiftLead/shiftlead) (how many sessions are run). Neither
depends on the other; both depend on this. The rule that keeps them in step: **no second parser** — every
reader and writer of a ledger or board calls the `ledgerboard` package.

Releases are tagged; each consumer vendors the package, each file's first line naming its release and hash. Why it
is shaped this way: [ShiftLead ADR 2026-10-12](https://github.com/ShiftLead/shiftlead/blob/main/docs/decisions/2026-10-12-ledgerboard-dev-cadence-shiftlead.md).

**Status:** released — v1.0, then v1.1 (a board item's bold head and the live look's `Not right: <what>` form), then v1.2 (the rank: cards, keys, the rank file, and the pick order it gives), then v1.3 (an answer says what it leads to: `<label> (default) — <consequence>`); then v2.0 (the ledger as a directory, one file per entry: `load()`, `split()`, `v2_problems()`); then v2.1 (`Part of`: a part names its parent, which waits on its open parts); then v2.2 (ledger entries get writers — the canonical form, `canonical()`, `entry_text()`, `edit_entry()` — `check()`'s `archive-open-parts`, and `Escaped from` and `Id take` among the spec's fields); the tags are the releases.

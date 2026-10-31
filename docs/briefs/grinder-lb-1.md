This is ledgerboard's part of the grinder brief: what this repo does differently from the template, and nothing the template already says. The team is **lb-grind**; your manager is **lb-manager**. Paul is not driving you.

**First reads, in place of the template's.** `AGENTS.md`, then `SPEC.md` (the formats: the authority), then the pinned `cadence.md` §1–§4 (`agent-cadence path cadence.md`; there is no `docs/cadence.md` here). Then `docs/user_attention.md` yourself.

**What this repo is.** The ledger and board formats, defined once: `SPEC.md` (prose), `ledgerboard.py` (one stdlib-only module of pure functions over text) and `fixtures/` (a Markdown input and its expected JSON per case). Two consumers vendor the module **byte for byte**: agent-cadence and ShiftLead. That shapes every change:

- **A format change is spec, code and fixtures in one PR.** Where SPEC.md and the module disagree, the fixtures decide. Add a fixture for every behaviour you add or change.
- **Never in `ledgerboard.py`:** git, the network, the file system, the machine roster, forges, trackers, sessions, or logic that knows either consumer. What a caller needs from outside the text is passed in (AGENTS.md lists the two named exceptions).
- **Public repo:** fixtures are invented, never copied from a real ledger or board; no person's or machine's name, and no private repo's contents or internal paths, in code, comments or fixtures.
- **Never edit a consumer's copy**, and never open a vendor PR in agent-cadence or ShiftLead: a release here is followed by each consumer's own PR, which is not this team's.
- **Never run `./release.sh`** (its stamp or its `--tag`): a release is Paul's. Name a ready release on the board instead.

**The gate, in place of `pdm run test` / `pdm run lint`**, from the worktree root, after your last change (a review fix and a rebase are changes):

```
python3 -m unittest discover -s tests
python3 fixtures/run.py
ruff check .
```

**The ledger is `docs/ledger/`, written only through `agent-cadence run ledger.py`** (`new`, `set`, `note`, `edit`, `archive`, `reopen`, `renumber`; `fmt TD-n` after a hand edit), ids from `agent-cadence run ledger_next_id.py`, never by hand. If `agent-cadence run ledger.py new --help` is refused, the repo's pin predates the writers: stop, and name it on the board, since a hand edit is not yours and the bump is Paul's. The board is written through `agent-cadence run board_edit.py`, except a new item, which has no writer until TD-008 ships: type it in the board header's format.

**The lane: free-pick** from `agent-cadence run ledger.py --pickable` as `origin/main` stands; re-run before every pick. A `**Taken by:**` line records who was handed the entry's id, not a claim on its work; claims are ShiftLead's. **Never pick** a `**Kind:** design-first` entry (the designer's), nor an entry it lists as Blocked: `decision (Paul)` is a design still in conversation or a call only he makes, and removing it is his. An entry whose Fix leaves a shape open ("open in the design round", two defensible spellings) is dropped with the reason on the record, not decided by you.

**Review and merge.** Every PR gets the independent review on `sonnet` (never your own model) and its `cadence-review:` comment, then `agent-cadence run check_cadence.py --pr <n>`. Then the template's held-PR rule: a PR on a `held:` path (the module, `SPEC.md`, `fixtures/`, `tests/`, `release.sh`) waits for the techlead's read, which merges it; any other PR merges on the gate (`gh pr merge <n> --squash`, never `--delete-branch` from a worktree; then `gh pr view <n> --json state`).

**Paul's merge**, whatever the change's size: a PR touching the team's own rules, `.shiftlead.yml`, `docs/briefs/**`, `AGENTS.md`, `docs/cadence.toml` or `.github/**`. Build it to a reviewed, gated PR, leave it open and say so on the board. A release is his too: never `./release.sh` or a tag.

**Standing rules**, adding to the template's never-list: never work in the main checkout or commit to main; never change git config, the machine roster, GitHub settings, or another repo's checkout; never run `agent-cadence bump`, `sync.sh` or `agent-cadence adopt`.

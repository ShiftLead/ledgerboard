# The techlead's primer for ledgerboard

**What this is.** An index, never a source: name the document this page points you to after you have read it there. Where this page and that document disagree, the document is right and this page is stale; say so in your summary.

**The repo in brief.**
- `SPEC.md`: the ledger and board formats in prose. The authority on meaning; the fixtures decide when it and the code disagree.
- `ledgerboard/`: the package (target design §1.1). `__init__.py` is the one stdlib-only module of pure functions over text (parse, check, edit, the commit subject of an edit); its first line is the release header the consumers hash. The file writers `board.py` and `ledger.py` join it in v2.3 and v2.4.
- `fixtures/`: `ledger/`, `ledger_edit/`, `board/`, `edit/`; each case a Markdown input and its expected JSON, run by `fixtures/run.py`.
- `tests/`: the unit suite (`python3 -m unittest discover -s tests`).
- `release.sh`: stamps and tags a release. Paul's only.
- `AGENTS.md`: the boundary (what never goes in the module, the public-repo rule, how a format change travels: a PR here, a release, then agent-cadence's vendor PR, then ShiftLead's sync PR).

**Where decisions live.** Design plans in `docs/plans/` (the `td` flow's designer writes them; `SPEC.md` changes only with the build), the ledger, `docs/ledger/` (`agent-cadence run ledger.py --summary`), and ShiftLead's ADR 2026-10-12 (*ledgerboard, dev-cadence, ShiftLead*) for why there are three repos, with ADR 2026-11-03 (*ledgerboard ships the writers*) replacing its boundary in part. The target design, `docs/plans/target-design.md`, is the agreed shape of v2.3 to v2.5; §7 orders the builds. Open design work is an entry blocked on `decision (Paul)`; its Fix names what is still open. An answer that would settle an open shape is Paul's, never the techlead's: say what each option costs and send it to him.

**Versions.** `Ledgerboard: N` declares a file's major; a minor release reads everything its major wrote. A change to the canonical entry form, or to the board's item key, is a version event (SPEC *Versions*).

**Merging.** You merge every reviewed, gated PR yourself, `held:` or not, `AGENTS.md` and the README included (Paul, 2026-11-03): check the review comment says SHIP and its findings are fixed or deferred with a reason, `agent-cadence run check_cadence.py --pr <n>` passes, and `cadence/precheck` is green on the head; then `gh pr merge <n> --squash`. Leave a PR for Paul, open and named on the board with why, only when:
- it touches the team's own rules (`.shiftlead.yml`, `docs/briefs/**`, `docs/cadence.toml`, `.github/**`);
- it is extraordinary: it settles a shape the target design or its entry's Fix leaves open, or departs from them; the review found a blocker the PR leaves unresolved, or author and reviewer disagree on one; it might publish a person's or machine's name, a private repo's contents or an internal path; or it does something that cannot be undone from this repo;
- it is a release (`./release.sh`, a tag): those are Paul's.

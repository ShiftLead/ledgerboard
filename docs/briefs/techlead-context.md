# The techlead's primer for ledgerboard

**What this is.** An index, never a source: name the document this page points you to after you have read it there. Where this page and that document disagree, the document is right and this page is stale; say so in your summary.

**The repo in brief.**
- `SPEC.md`: the ledger and board formats in prose. The authority on meaning; the fixtures decide when it and the code disagree.
- `ledgerboard.py`: one stdlib-only module of pure functions over text (parse, check, edit, the commit subject of an edit). Its first line is the release header the consumers hash.
- `fixtures/`: `ledger/`, `ledger_edit/`, `board/`, `edit/`; each case a Markdown input and its expected JSON, run by `fixtures/run.py`.
- `tests/`: the unit suite (`python3 -m unittest discover -s tests`).
- `release.sh`: stamps and tags a release. Paul's only.
- `AGENTS.md`: the boundary (what never goes in the module, the public-repo rule, how a format change travels: a PR here, a release, then agent-cadence's vendor PR, then ShiftLead's sync PR).

**Where decisions live.** Design plans in `docs/plans/` (the `td` flow's designer writes them; `SPEC.md` changes only with the build), the ledger, `docs/ledger/` (`agent-cadence run ledger.py --summary`), and ShiftLead's ADR 2026-10-12 (*ledgerboard, dev-cadence, ShiftLead*) for why there are three repos. Open design work is an entry blocked on `decision (Paul)`; its Fix names what is still open. An answer that would settle an open shape is Paul's, never the techlead's: say what each option costs and send it to him.

**Versions.** `Ledgerboard: N` declares a file's major; a minor release reads everything its major wrote. A change to the canonical entry form, or to the board's item key, is a version event (SPEC *Versions*).

# User Attention Board

Ledgerboard: 3

People: paul

Items that need the user to act or decide, plus in-flight work parked by a session. Sessions add items **the
moment they arise** and close them when handled, never delete them. Keep this board small: durable debt belongs in
[the ledger](../ledger/); this board is only "a human must act or decide."

This directory is the board (ledgerboard v3, split in TD-120): one file per item, `<id>.md`, and closed items under
`archive/<YYYY-MM>/`. The item file's form is `SPEC.md`'s *The item file*. Write and edit an item only through
`agent-cadence run board_edit.py` (`add`, then `done`, `snooze`, `due`, `decide`, `reply` by `--id`), never by
hand. The conventions (kinds, `Due:` and snoozing, the sweep stamps) are cadence.md §3, the pinned agent-cadence's
(`agent-cadence path cadence.md`).

Kinds: `decide | act | look | watch | fyi`. `decide`/`act` (or no kind) are the person's to-do, and so is
`look`, a live look the person is asked to make; `watch` is a session's own re-check, its check-by date as `Due:`;
`fyi` carries no `Due:` and never reaches the SessionStart line. An item overdue 14 days or more belongs in the
ledger: ledger it and close it here.

A `decide` carries its `Answers:` (the recommended one marked `(default)`) and a detail block in plain English for
someone who has not read your session: **Context**, **Question**, **Caveats** (when there are any),
**Recommended** and **Otherwise**. A `look` carries the fixed pair `Works | Not right: <what>`. The person's answer
is recorded by `board_edit.py decide`, never by hand. Closing an item (`board_edit.py done --why <why>`) moves its
file into `archive/`; nothing is deleted.

## In-flight (parked by a session)
- (none)

# User Attention Board

Items that need the user to act or decide, plus in-flight work parked by a session. Sessions add entries **the moment they arise** and close them when handled (never delete — see below). Keep this file small — durable debt belongs in [the ledger](ledger/); this board is only "a human must act or decide."

All conventions — entry format and the `<host>` semantics, `Due:` dates and snoozing, the `Swept:`/`Swept-deep:` sweep stamps — live in [docs/cadence.md §3](cadence.md#3-never-strand-work). That file is SYNC (improvements reach every consumer on re-sync); this skeleton is SEED (yours, never overwritten), which is why the explanations do not live here (dev-cadence TD-17).

Format: `- [ ] YYYY-MM-DD (session <first-8-of-session-uuid> on <host>, or n/a) — what's needed. Context: TD-NNN / PR #N / branch. Due: YYYY-MM-DD.`

Under the line, indented two spaces, a detail block of sub-bullets in plain English for someone who has not read your session: `**Context:**` (a few sentences; nested bullets where a list is clearer), `**Question:**`, `**Caveats:**` (when there are any), `**Recommended:** <the default> — why. **Otherwise:** <each other answer> — when.` Always on a `decide`; on an `act`/`look` whenever the line alone does not say what to do; fields stay on the line (cadence.md §3.3, TD-084).

Kinds: `decide | act | look | watch | fyi` — optional, one word before the date: `- [ ] decide YYYY-MM-DD (…`. `decide`/`act` (or no word) are the person's to-do, and so is `look`, a live look the person is asked to make; `watch` is a session's own re-check, its check-by date as `Due:`; `fyi` carries no `Due:` and never reaches the SessionStart line. An item overdue 14 days or more belongs in the ledger: ledger it and close it here (cadence.md §3).

A question ends with its answers after `Due:` — `Answers: <answer> | <answer>.`, the one you recommend marked `Answers: <answer> (default) | <answer>.` The person's answer is appended by `agent-cadence run board_edit.py decide`, never by hand: `Decided: <text> (YYYY-MM-DD).` A `look` (the person is asked to look at something live) ends with the fixed pair `Answers: Works | Not right: <what>.`; a `watch`, an `act` and an `fyi` carry none (cadence.md §3.5).

Closing an entry never deletes it: `agent-cadence run board_edit.py done --why <why>` ticks it and appends `Closed: YYYY-MM-DD — <why>.` A merge conflict here is resolved by keeping both sides; 10 or more closed entries are archived to `user_attention_archive.md` in a PR of their own.

## Needs the user

- [ ] decide 2026-11-14 (n/a) — Should ledgerboard's ledger check refuse an entry that asks you something but has no decision gate, as designed in TD-109? Context: TD-109 decision (paul). Due: 2026-11-21. Answers: One more round (default) — a session runs a seventh review round on the last fixes, then asks you again | Go — a session files the one build, and asks agent-cadence and ShiftLead to file their follow-ups | Hold: <note> — nothing is built; a session revises the design by your note.
  - **Context:** In ledgerboard (the ledger and board formats both agent-cadence and ShiftLead use), TD-109 makes the ledger check catch an entry that asks you a question but has no decision gate, so it never reaches your Queue. agent-cadence met this on 2026-11-14 and asked for the check to live here, for every consumer. The design: the check flags such an entry and the writer refuses to make one; a question you already answered stays as the record and is not flagged; a session writes the gate and the question in one step; an Owner that names you stays each consumer's own rule (agent-cadence agreed). Six review rounds ran, the most allowed; the last found nothing that changes the build. One topic kept coming back, how the question and its gate get written together, and the last reviewer judged that part heavy but right. Seven small fixes from that last round were checked against the code but not re-read by a design reviewer. Plain-words summary: docs/synopses/TD-109.md; the plan: docs/plans/TD-109-decision-missing.md (PR #330).
  - **Question:** Should the TD-109 design be built as it stands?
  - **Recommended:** One more round — a fresh review of the last fixes is cheap, and the recurring topic deserves one more read before it is built.
## In-flight (parked by a session)

- (none)

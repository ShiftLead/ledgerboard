# User Attention Board

Items that need the user to act or decide, plus in-flight work parked by a session. Sessions add entries **the moment they arise** and close them when handled (never delete — see below). Keep this file small — durable debt belongs in [the ledger](ledger/); this board is only "a human must act or decide."

All conventions — entry format and the `<host>` semantics, `Due:` dates and snoozing, the `Swept:`/`Swept-deep:` sweep stamps — live in [docs/cadence.md §3](cadence.md#3-never-strand-work). That file is SYNC (improvements reach every consumer on re-sync); this skeleton is SEED (yours, never overwritten), which is why the explanations do not live here (dev-cadence TD-17).

Format: `- [ ] YYYY-MM-DD (session <first-8-of-session-uuid> on <host>, or n/a) — what's needed. Context: TD-NNN / PR #N / branch. Due: YYYY-MM-DD.`

Under the line, indented two spaces, a detail block of sub-bullets in plain English for someone who has not read your session: `**Context:**` (a few sentences; nested bullets where a list is clearer), `**Question:**`, `**Caveats:**` (when there are any), `**Recommended:** <the default> — why. **Otherwise:** <each other answer> — when.` Always on a `decide`; on an `act`/`look` whenever the line alone does not say what to do; fields stay on the line (cadence.md §3.3, TD-084).

Kinds: `decide | act | look | watch | fyi` — optional, one word before the date: `- [ ] decide YYYY-MM-DD (…`. `decide`/`act` (or no word) are the person's to-do, and so is `look`, a live look the person is asked to make; `watch` is a session's own re-check, its check-by date as `Due:`; `fyi` carries no `Due:` and never reaches the SessionStart line. An item overdue 14 days or more belongs in the ledger: ledger it and close it here (cadence.md §3).

A question ends with its answers after `Due:` — `Answers: <answer> | <answer>.`, the one you recommend marked `Answers: <answer> (default) | <answer>.` The person's answer is appended by `agent-cadence run board_edit.py decide`, never by hand: `Decided: <text> (YYYY-MM-DD).` A `look` (the person is asked to look at something live) ends with the fixed pair `Answers: Works | Not right: <what>.`; a `watch`, an `act` and an `fyi` carry none (cadence.md §3.5).

Closing an entry never deletes it: `agent-cadence run board_edit.py done --why <why>` ticks it and appends `Closed: YYYY-MM-DD — <why>.` A merge conflict here is resolved by keeping both sides; 10 or more closed entries are archived to `user_attention_archive.md` in a PR of their own.

## Needs the user

- [ ] decide 2026-11-12 (session `lb-designer`) — Say One more round, Go or Hold on TD-078's design (PRs #243, #251): v3.0's ledger half; round 7, the one you bought, ended with its design review SHIP, and its fact-check's one build-changing fix, a count, is unread by a design review. Context: TD-078 decision (paul). Due: 2026-11-20. Answers: One more round (default) — an eighth design review, then this item again | Go — B1 to B4 are filed Part of TD-078, B1 and B2 before TD-070's B1 | Hold: <note> — the builds stay unfiled and your note goes into TD-078's Ask. Decided: One more round (by Paul) (2026-11-12).
  - **Context:** TD-078's design, docs/plans/TD-078-v3-ledger-half.md (PRs #243, #251; plain words in docs/synopses/TD-078.md). In the last v2.x minor, beside TD-075's B1, migrate maps Taken by and Waits to Log lines, a header Resolved to the body, and the old decision form to decision (<who>) with its text in an Ask (B2), and note writes an archived entry where it is (B1); this repo then migrates its own ledger (B3); v3.0 makes the four forms and a header Location retired errors on every entry and removes migrate (B4, after TD-070's builds). TD-070's B1 waits on B1, B2, TD-075's B1 and your answer that the minor is cut. Trend, build-changing per design review: 6, 2, 2, 1, 2, 1, 0 (fact-checks 7, 1, 1, 0, 0, 1, 1); round 7's closing fact-check raised two minor. Unread by any design review: round 7's fact-check fix F97 (B3's count of entries migrate changes, four to five, TD-075's noted Status the new one; the closing fact-check re-ran it and confirmed five) and the minor F98, F101, F102. The recurring topic, the agent-cadence consumer lines (F25, F35, F77, F86), did not recur: round 7's design review read them against agent-cadence's main and found no format question in them.
  - **Question:** One more round, Go or Hold on TD-078's design?
  - **Recommended:** One more round — an eighth design review reads the one build-changing fix no design review has read (F97, a count in B3), as your rule for unread fixes asks, before four builds of a major are filed. **Otherwise:** Go if you judge a count the closing fact-check re-ran needs no design review: B1 to B4 are filed Part of TD-078, B1 and B2 before TD-070's B1.
- [ ] act 2026-11-11 (session `lb-grinder`) — Release v2.8 (TD-067's B1, TD-073, is merged), or fold it into v2.7 as TD-067's D5 allows; once tagged, a session files ShiftLead's repair entry (the plan's Consumers) with ao td add --repo shiftlead. Context: TD-067. Due: 2026-11-13.

## In-flight (parked by a session)

- (none)

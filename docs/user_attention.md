# User Attention Board

Items that need the user to act or decide, plus in-flight work parked by a session. Sessions add entries **the moment they arise** and close them when handled (never delete — see below). Keep this file small — durable debt belongs in [the ledger](ledger/); this board is only "a human must act or decide."

All conventions — entry format and the `<host>` semantics, `Due:` dates and snoozing, the `Swept:`/`Swept-deep:` sweep stamps — live in [docs/cadence.md §3](cadence.md#3-never-strand-work). That file is SYNC (improvements reach every consumer on re-sync); this skeleton is SEED (yours, never overwritten), which is why the explanations do not live here (dev-cadence TD-17).

Format: `- [ ] YYYY-MM-DD (session <first-8-of-session-uuid> on <host>, or n/a) — what's needed. Context: TD-NNN / PR #N / branch. Due: YYYY-MM-DD.`

Under the line, indented two spaces, a detail block of sub-bullets in plain English for someone who has not read your session: `**Context:**` (a few sentences; nested bullets where a list is clearer), `**Question:**`, `**Caveats:**` (when there are any), `**Recommended:** <the default> — why. **Otherwise:** <each other answer> — when.` Always on a `decide`; on an `act`/`look` whenever the line alone does not say what to do; fields stay on the line (cadence.md §3.3, TD-084).

Kinds: `decide | act | look | watch | fyi` — optional, one word before the date: `- [ ] decide YYYY-MM-DD (…`. `decide`/`act` (or no word) are the person's to-do, and so is `look`, a live look the person is asked to make; `watch` is a session's own re-check, its check-by date as `Due:`; `fyi` carries no `Due:` and never reaches the SessionStart line. An item overdue 14 days or more belongs in the ledger: ledger it and close it here (cadence.md §3).

A question ends with its answers after `Due:` — `Answers: <answer> | <answer>.`, the one you recommend marked `Answers: <answer> (default) | <answer>.` The person's answer is appended by `agent-cadence run board_edit.py decide`, never by hand: `Decided: <text> (YYYY-MM-DD).` A `look` (the person is asked to look at something live) ends with the fixed pair `Answers: Works | Not right: <what>.`; a `watch`, an `act` and an `fyi` carry none (cadence.md §3.5).

Closing an entry never deletes it: `agent-cadence run board_edit.py done --why <why>` ticks it and appends `Closed: YYYY-MM-DD — <why>.` A merge conflict here is resolved by keeping both sides; 10 or more closed entries are archived to `user_attention_archive.md` in a PR of their own.

## Needs the user

- [x] decide 2026-11-04 (session `lb-designer`) — **TD-023's extra review round is done: say Go to file its one build (the Hide until notes).**. Context: TD-023. Due: 2026-11-08. Answers: Go (default) — the build is filed Part of TD-023 for the next release, and the grinder picks it | One more round — another design review and fact-check, then this item again | Hold: <note> — the build waits, and your note goes in TD-023's Ask. Decided: Go (by Paul) (2026-11-04). Closed: 2026-11-04 — Go: the build is filed as TD-041, Part of TD-023, and TD-023's gate is lifted.
  - **Context:** TD-023's design, `docs/plans/TD-023-hide-notes.md`, gives Hide until two ℹ notes: hide-spent (a hide that hides nothing today) and hide-late (a hidden item whose hide is after its deadline).
    - They come from `item_notes(item, today)`, outside the gate, carried in `item_record()` as `notes` and reported by `board.py` as `item_notes` beside a decide lift's own `notes`. A note never refuses a write.
  - **Question:** Does the design's one build go ahead now that the round you bought is done?
  - **Caveats:** The round you bought (round 3) read the post-rounds key rename (F20) and round 2's minor fixes (F11-F17), and raised nothing build-changing; its fact-checks were clean. Trend of build-changing findings from the design reviews: 1, 0, 0.
    - Not read by a design review: round 3's minor fixes F28-F32 (an edit case pinned to an impossible Due, the board fixtures named, the key's position, where the writer computes the notes, the SPEC paragraph's placement). Only the closing fact-check read them; they go into the build's Fix.
    - The release is the next after the build lands; TD-036 does not wait on it.
  - **Recommended:** Go — the bought round raised nothing that changes what gets built. **Otherwise:** Hold if the notes should take another shape.
- [x] decide 2026-11-04 (person) — item_problem() cannot note a stale or over-late Hide until it has no today and no note channel. Context: TD-023. Due: 2026-11-04. Decided: one more round (by Paul) (2026-11-04). Closed: 2026-11-04 — one more round recorded on TD-023 for the designer, whose open TD-023 item comes back after the round.
- [x] decide 2026-11-04 (session `lb-designer`) — **Say One more round to review TD-023's post-rounds fix (board.py's key is item_notes), or Go to file its one build now.**. Context: TD-023 / PR #74. Due: 2026-11-07. Answers: One more round (default) — one more design review and fact-check, then this item again | Go — the build is filed Part of TD-023 for the next release, and the grinder picks it | Hold: <note> — the build waits, and your note goes in TD-023's Ask. Decided: One more round (2026-11-04). Closed: 2026-11-04 — One more round, recorded on TD-023 (#117, #118): the designer runs one more design review and fact-check, then raises this item again.
  - **Context:** TD-023's design, `docs/plans/TD-023-hide-notes.md` (PR #74), gives Hide until the two ℹ notes target design §6 asked for and TD-017 left out.
    - hide-spent: a hide that hides nothing today, because its date has come or the item is decided.
    - hide-late: a hidden item whose hide is after its deadline, so the deadline itself is hidden.
    - They come from a new `item_notes(item, today)`, carried in `item_record()` as `notes`, and reported by `board.py` as `item_notes` for the line a write leaves. No gate reads them, so a note never refuses a write. The shape is your answer to the steer.
  - **Question:** Run one more design review over the post-rounds fix, or let the one build go ahead now?
  - **Caveats:** How the rounds ended: after round 2 of a cap of 6, by the stop rule (design reviews 1, then 0 build-changing; the fact-checks 0 build-changing; the closing one none on the design).
    - After the rounds, PR #74's doc fact-check (F20, build-changing) found board.py already reports a `notes` key on a decide lift, so the writer's key is now `item_notes`, and the fixture list is by rule (about thirty writer cases). F21-F24 are corrections of the record and the SPEC paragraph's placement. No design review has read F20, or round 2's minor fixes F11-F17.
    - The release is the next after the build lands, as you said; TD-036 does not wait on it.
  - **Recommended:** One more round — F20 changes what gets built after the last design review, and the cadence says such a change buys one more round. **Otherwise:** Go if the key rename is plainly mechanical to you; the builder then checks F11-F24. Hold if the notes should take another shape.
- [x] decide 2026-11-03 (session `lb-designer`) — **Say Go to file TD-023's one build (the Hide until notes), or buy one more review round.**. Context: TD-023 / PR #74. Due: 2026-11-06. Answers: Go (default) — the build is filed Part of TD-023 for v2.4, and the grinder picks it | One more round — one more design review and fact-check, then this item again | Hold: <note> — the build waits, and your note goes in TD-023's Ask. Closed: 2026-11-04 — replaced: PR #74's fact-check found a build-changing fix (the writer's key), so the new item recommends one more round.
  - **Context:** TD-023's design, `docs/plans/TD-023-hide-notes.md` (PR #74), gives Hide until the two ℹ notes target design §6 asked for and TD-017 left out.
    - hide-spent: a hide that hides nothing today, because its date has come or the item is decided.
    - hide-late: a hidden item whose hide is after its deadline, so the deadline itself is hidden.
    - They come from a new `item_notes(item, today)`, carried in `item_record()` as `notes` and reported by `board.py` for the line a write leaves. No gate reads them, so a note never refuses a write.
  - **Question:** Does the design's one build go ahead, landing in v2.4?
  - **Caveats:** How the rounds ended: after round 2 of a cap of 6, by the stop rule. Design reviews raised 1, then 0 build-changing findings; the fact-checks and the closing fact-check raised none. All 17 findings are applied (`docs/reviews/TD-023.md`); no topic recurred.
    - Not read by any review: round 2's minor fixes F11-F17 (tests for the text mode and --plan, the decide_hidden case's exact note, and wording). Only the closing fact-check checked them; they go into the build's Fix.
    - One default is with the techlead as a steer: the shape, `item_notes()` rather than a today on `item_problem()`. The build is v2.4, since v2.3 was tagged without the notes while this was in review (F18).
  - **Recommended:** Go — the last design review raised nothing that changes what gets built, and the unreviewed fixes only pin fixtures and tests. **Otherwise:** One more round if you want F11-F17 reviewed first. Hold if the notes should take another shape.
- [x] act 2026-11-03 (session `lb-grinder`) — Merge PR #84 (TD-020), which the techlead passed with a recommendation to merge, or answer the open steer on split_notes()'s shape first. Context: TD-020 / PR #84. Due: 2026-11-04. Closed: 2026-11-04 — merged 2026-11-04 (squash) on Paul's say-so; TD-020 waits on the v2.4 release.
  - **Context:** #84 makes `split()` keep a v1 README's Summary section as written, and adds `split_notes(readme)`. That function lists the README lines that may still describe the v1 layout, so the caller can warn about them. It is your merge, not the techlead's, because the Fix says to report those lines "in the result", and #84 reports them through a separate function. The steer that asked you about that shape (m-5d77cc3dec15) has no answer yet. The gate is green on b2b0f50, and the Sonnet review and the techlead's read have both passed. Once it merges, v2.4 (also yours to release) carries it.
  - **Recommended:** merge #84 as built. A separate `split_notes()` leaves `split()`'s return value unchanged for both consumers. **Otherwise:** answer the steer to fold the notes into `split()`'s result, and the grinder reworks #84.
- [x] act 2026-11-03 (session `lb-grinder`) — Release v2.3: every build is merged (TD-012 to TD-019, the last PR #77), so stamp and tag it. Context: TD-021. Due: 2026-11-03. Closed: 2026-11-03 — tagged v2.3 on 54d2df9 (PR #82); TD-021 archived.
  - **Context:** Every v2.3 build is on main: the board writers and their gate, the package, board.py, Hide until, the board people line and who decided, the parts and lifts fields, respace and the grammar appendix. TD-008 is archived. TD-021 is the release itself; the consumers vendor entries and the v2.4 builds (TD-010, TD-011) wait on it, and no session but yours runs release.sh.
  - **Recommended:** ./release.sh 2.3 on a branch and merge its PR, then git checkout --detach origin/main and ./release.sh --tag 2.3 (AGENTS.md, Commands); TD-021 says the rest.
- [x] decide 2026-10-30 (person) — A new decide item and an archive of closed ones have no writer: the board's writers cover every write, as the ledger's now do. Context: TD-008. Due: 2026-10-30. Decided: go ahead (2026-10-30). Closed: 2026-10-31 — TD-008's block lifted on Paul's go; the ledgerboard team builds it.
- [x] act 2026-10-31 (n/a) — Merge PR #53 (PRs gated on the local precheck); merge PR #54 (release tag from a worktree) once the techlead has read it. Context: TD-003 / PR #53, TD-009 / PR #54. Due: 2026-10-31. Closed: 2026-11-03 — both merged by Paul on 2026-11-01: PR #53 (local precheck) and PR #54 (tag from a worktree).
  - **Context:** Both are built, reviewed and gated, and both touch files only you merge (`AGENTS.md`, and for #53 `.github/` and `docs/cadence.toml`).
    - PR #53 (TD-003): the merge gate becomes the local `precheck` in `docs/cadence.toml`, and `ci.yml` runs only on a fork's PR, a release tag and by hand, so this repo's own PRs no longer spend the shared Actions minutes. Its `cadence/precheck` is green, and its own Actions job already skips.
    - PR #54 (TD-009): `./release.sh --tag` checks that HEAD is `origin/main` instead of that `main` is checked out, so a worktree session can tag (`git checkout --detach origin/main && ./release.sh --tag <x.y>`). It also touches `release.sh` and `tests/`, so the techlead reads it first.
  - **Question:** Squash-merge #53 now, and #54 after the techlead's pass (`gh pr merge <n> --squash`).
- [x] decide 2026-10-31 (session `lb-designer`) — **Say Go to file TD-008's three board-writer builds, or buy one more review round.** Context: TD-008. Due: 2026-11-03. Answers: Go (default) — the three builds are filed and the grinder starts on the first | One more round — one more design review and fact-check, then this item again | Hold: <note> — the builds wait, and your note goes in TD-008's Ask. Decided: Go (2026-11-02). Closed: 2026-11-03 — Go applied: TD-008's builds filed as TD-012..TD-019, its parts (PR #57); the grinder starts on TD-012.
  - **Context:** TD-008's design, `docs/plans/TD-008-board-writers.md`, plans ledgerboard v2.3's board writers in three builds that land in series.
    - B1: `item_line()` writes every kind, with answers and a detail block, and stops writing three wrong lines.
    - B2: `item_problem()`, `canonical_item()` and `board_problems()`, the gate, which judges new lines only.
    - B3: `archive_closed()` and its commit subject.
  - **How the rounds ended:** after round 3 of a cap of 6, by the stop rule. The design reviews raised 7, 3 and 0 build-changing findings; the fact-checks raised 3, 0 and 1, and the closing fact-check 1. All 39 findings are applied (`docs/reviews/TD-008.md`). No topic recurred across rounds' design reviews. `canonical_item()`'s key-keeping rules drew the most corrections, the last in the closing fact-check.
  - **Question:** do the builds go ahead as planned?
  - **Caveats:** three choices are defaults you may want changed.
    - C1: `canonical_item()` never changes a line's item key, so agent-cadence's format pass fixes little and names the rest (the steer sent today).
    - C3: answers only on `decide` and `look`, after cadence §3.5's table.
    - C7: the archive gets its own commit subject.
    - Not read by any review: the closing fact-check's fixes F37–F39 (when `canonical_item()` may add Context's period). They go into B2's Fix for the builder to check.
    - `item_line()` writes four inputs differently from v2.2 (C8). Lines already on a board are untouched.
  - **Recommended:** Go — the last design review raised nothing that changes what gets built, and the closing fixes narrow one rewrite that the key read-back already guards. **Otherwise:** One more round if you want F37–F39 reviewed before B2. Hold if C1's trade (old lines keep their keys, so the format pass does little) is the wrong one.
- [x] act 2026-11-03 (n/a) — Merge PR #67 (ledgerboard becomes the package `ledgerboard/__init__.py`). Context: TD-015 / PR #67. Due: 2026-11-03. Closed: 2026-11-03 — PR #67 (TD-015) merged 2026-11-03.
  - **Context:** Built, reviewed (SHIP), gated, and passed by the techlead. It is yours because it touches `AGENTS.md`, `.shiftlead.yml` and `.github/workflows/ci.yml`. TD-016..TD-019 (the board writer and its successors) wait on it. Once it merges, the briefs and the techlead primer still say `ledgerboard.py`; those files are yours to update.
  - **Question:** Squash-merge #67 (`gh pr merge 67 --squash`).

## In-flight (parked by a session)

- (none)

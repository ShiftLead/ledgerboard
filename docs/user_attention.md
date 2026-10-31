# User Attention Board

Items that need the user to act or decide, plus in-flight work parked by a session. Sessions add entries **the moment they arise** and close them when handled (never delete — see below). Keep this file small — durable debt belongs in [the ledger](ledger/); this board is only "a human must act or decide."

All conventions — entry format and the `<host>` semantics, `Due:` dates and snoozing, the `Swept:`/`Swept-deep:` sweep stamps — live in [docs/cadence.md §3](cadence.md#3-never-strand-work). That file is SYNC (improvements reach every consumer on re-sync); this skeleton is SEED (yours, never overwritten), which is why the explanations do not live here (dev-cadence TD-17).

Format: `- [ ] YYYY-MM-DD (session <first-8-of-session-uuid> on <host>, or n/a) — what's needed. Context: TD-NNN / PR #N / branch. Due: YYYY-MM-DD.`

Under the line, indented two spaces, a detail block of sub-bullets in plain English for someone who has not read your session: `**Context:**` (a few sentences; nested bullets where a list is clearer), `**Question:**`, `**Caveats:**` (when there are any), `**Recommended:** <the default> — why. **Otherwise:** <each other answer> — when.` Always on a `decide`; on an `act`/`look` whenever the line alone does not say what to do; fields stay on the line (cadence.md §3.3, TD-084).

Kinds: `decide | act | look | watch | fyi` — optional, one word before the date: `- [ ] decide YYYY-MM-DD (…`. `decide`/`act` (or no word) are the person's to-do, and so is `look`, a live look the person is asked to make; `watch` is a session's own re-check, its check-by date as `Due:`; `fyi` carries no `Due:` and never reaches the SessionStart line. An item overdue 14 days or more belongs in the ledger: ledger it and close it here (cadence.md §3).

A question ends with its answers after `Due:` — `Answers: <answer> | <answer>.`, the one you recommend marked `Answers: <answer> (default) | <answer>.` The person's answer is appended by `agent-cadence run board_edit.py decide`, never by hand: `Decided: <text> (YYYY-MM-DD).` A `look` (the person is asked to look at something live) ends with the fixed pair `Answers: Works | Not right: <what>.`; a `watch`, an `act` and an `fyi` carry none (cadence.md §3.5).

Closing an entry never deletes it: `agent-cadence run board_edit.py done --why <why>` ticks it and appends `Closed: YYYY-MM-DD — <why>.` A merge conflict here is resolved by keeping both sides; 10 or more closed entries are archived to `user_attention_archive.md` in a PR of their own.

## Needs the user

- [x] decide 2026-10-30 (person) — A new decide item and an archive of closed ones have no writer: the board's writers cover every write, as the ledger's now do. Context: TD-008. Due: 2026-10-30. Decided: go ahead (2026-10-30). Closed: 2026-10-31 — TD-008's block lifted on Paul's go; the ledgerboard team builds it.
- [ ] act 2026-10-31 (session ao-ledgerboard-lb-grinder on kmaster-Standard-PC-i440FX-PIIX-1996) — Merge PR #53 (PRs gated on the local precheck); merge PR #54 (release tag from a worktree) once the techlead has read it. Context: TD-003 / PR #53, TD-009 / PR #54. Due: 2026-10-31.
  - **Context:** Both are built, reviewed and gated, and both touch files only you merge (`AGENTS.md`, and for #53 `.github/` and `docs/cadence.toml`).
    - PR #53 (TD-003): the merge gate becomes the local `precheck` in `docs/cadence.toml`, and `ci.yml` runs only on a fork's PR, a release tag and by hand, so this repo's own PRs no longer spend the shared Actions minutes. Its `cadence/precheck` is green, and its own Actions job already skips.
    - PR #54 (TD-009): `./release.sh --tag` checks that HEAD is `origin/main` instead of that `main` is checked out, so a worktree session can tag (`git checkout --detach origin/main && ./release.sh --tag <x.y>`). It also touches `release.sh` and `tests/`, so the techlead reads it first.
  - **Question:** Squash-merge #53 now, and #54 after the techlead's pass (`gh pr merge <n> --squash`).

## In-flight (parked by a session)

- (none)

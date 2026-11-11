# TD-058: v2.7, the Status release, and `migrate`

**Status:** Scope draft, 2026-11-11 (session lb-designer). This is step 1 of TD-058's Fix: agree the scope
with Paul before the plan gets its exact `SPEC.md` text and before any review round runs (Paul's layer,
§4.8 add: *the shape before reviews*). Nothing here has been reviewed yet. Once Paul agrees the scope, this
file gains the SPEC text and the fixture cases, the review rounds run (cadence.md §4.8, the record in
`docs/reviews/TD-058.md`), and the builds are filed only on his go.

**Entry:** [TD-058](../ledger/TD-058.md). **Source:** [target design](target-design.md) §2.1, §2.2, §7.1 (the
v2.7 row and its amendments), §7.2 step 6, §7.3, §7.4.

## The problem

The target design ends the v2 migration with a release that closes the Status vocabulary, moves the old
Status notes and `Added` comments into the Log, and ships `migrate`, the tool that maps a ledger's old forms
to the new ones. The design first called that release v2.5, then v2.6, now v2.7 (§7.1's amendments).
`SPEC.md` already names "v2.7's `migrate`" in three places (*Retired words*, the Status grammar under *The
Log*, the tripwire's exemption), and v2.7 work has landed (TD-046, TD-056). But the newest tag is
v2.6, and `migrate` is not built: only `migrate_subject()` (the commit subject) and `status_notes_to_log()`
(the Status-notes lift that `note`, `archive` and `reopen` already call) exist. There is no
`migrate_entry()` and no `ledger.py migrate`.

The precondition §7.1 sets now holds: on 2026-11-07 no open entry in ledgerboard's, agent-cadence's or
ShiftLead's ledger carries a `Waits` line. The forms `migrate` exists for still stand (the entry's count:
in ShiftLead, 12 old-form decisions and 36 retired Status words; in agent-cadence, 2 old-form decisions and
a `Taken by`), flagged only as ℹ.

## What exists today, and what v2.7 adds

| Piece of the v2.7 row | Today (v2.6 + main) | v2.7 adds |
|---|---|---|
| The closed Status set (§2.2's table) | `Open`, `Resolved`, `Superseded`, `Dropped` read; the open stage words `Designed`, `Built`, `Partly`, `Live`, `In` flagged ℹ `retired`; `Done`, `Moved`, `OBE` read as closed | `check()` errors on a Status outside the table (word, date, `by` target, directory) |
| The Log's migration | the Log, its shapes and `status_notes_to_log()` (v2.4); the writers lift a note before they write | `migrate_entry()`: Status tails and `Added` comments into Log lines, in date order, for every entry |
| Archived Status words | read as closed | mapped by §2.2's table; an unmapped one stops `migrate` |
| Stage words on open entries | ℹ `retired` | `Open` + a Log line (+ `Kind`, see S3) |
| `Location` to the body | a format header field, last in the canonical order | a body section; `canonical()` no longer places it in the header |
| `Waits` | an error when an edit writes or changes one (TD-046); still in the canonical order | out of the canonical order |
| `Kind` per §2.3 | a consumer field (§2.3 (i)) | nothing in the module (S4) |
| The grammar appendix | the board item line, `Blocked by`, Event sections, a person's name, the rank file | the header block and the Log lines (`while TD-m` among them) |
| `ledger.py migrate` | — | the CLI: `--dry-run`, `--closed-dates <file>`, one commit under `migrate_subject()` |

## The scope, point by point

Each point is my recommendation; the alternative follows it.

**S1. The closed Status set, and its check: an error on every entry, open or archived** (§2.2, as written).
`Open` (bare), `Resolved D`, `Superseded D by TD-m | <repo>#TD-m`, `Dropped D`, with the directory agreeing.
A consumer takes v2.7 in one PR that vendors it and runs `migrate`, so its own ledger passes the day it
vendors; a repo still on v2.6 is untouched until it bumps. *Alternative:* the usual grading (an error on an
entry the edit changed, ℹ on a standing ledger), which lets a repo vendor without migrating but leaves the
old words standing indefinitely.

**S2. The migration map, as §2.2 writes it.** Archived: `Resolved…`, `Done…`, `Built…`, archived
`Designed…` → `Resolved D`; `Superseded D by …` and `Moved to <repo>…` naming an entry → `Superseded D by
…`; `Moved…` naming none, `OBE`, *won't fix* → `Dropped D`; anything else stops `migrate`, which lists it and
writes nothing. Open: a stage word → `Open` + its Log line; a prose Status → `Open` + a `was:` line listed in
the dry run. `Added` comment → a plain `- D: <comment>` line (`filed by` only when it parses into that shape).
**One addition:** an archived entry that needs a date no source gives (no Status date, no `**Resolved:**`
date, none in `--closed-dates`) stops `migrate` the same way, rather than guessing one. The archiving
commit's date is the caller's to look up (git stays out of the package), passed in as `--closed-dates`.

**S3. Stage words set `Kind` only from a map the caller passes.** §2.2 has `migrate` set `Kind` where the
stage implies it (`Designed` → `build`, `Built` → `live-check`). But `Kind`'s words are consumer vocabulary
(§2.3 (i), cadence.md's `Fields:` line), and AGENTS.md keeps consumer knowledge out of the package. So
`migrate_entry(…, kinds=)` takes the map, and `ledger.py migrate --kind designed=build --kind
built=live-check` passes it; agent-cadence's wrapper passes cadence.md's. With no map, the stage word becomes
`Open` + its Log line, `Kind` is left alone, and the dry run lists the entry for the remodel to set.
*Alternative:* the module carries §2.2's two pairs itself (they are in `RETIRED_STATUS`'s hint text today).

**S4. `Kind` per §2.3 is nothing in the module.** §2.3 chose (i), so v2.7's row item "`Kind` per §2.3's
decision" is cadence.md's `Fields:` line, which agent-cadence owns. v2.7 does no `Kind` work beyond S3.

**S5. `Location` moves to the body.** `canonical()` drops it from the header order and `migrate` moves a
header `Location` to a `**Location:**` body section after `**Why:**` (the target entry's order, §2). No tool
reads it (principle 4). This changes the canonical entry form, so it is a version event (SPEC *Versions*),
which is why it is in this ask. *Alternative:* leave `Location` in the header (it is harmless there) and drop
it from the v2.7 row.

**S6. `Waits` leaves the canonical order.** `canonical()` no longer places it: a `Waits` line still in a file
(today only on archived entries) is kept, placed with the other fields the order does not name, in the file's order (SPEC
*Canonical form*; *unknown text survives*). `check()` reads retired fields on open entries only, so an archived
`Waits` line is not flagged; S7's `migrate --dry-run` precondition is what covers archived entries. `migrate` does
not touch it: turning a wait into a gate was the v2.4 remodel's (§7.3: mechanical for `until`, judgment for an
event), and no open entry in the three ledgers carries one.

**S7. `migrate`'s lifecycle** (your note on the entry, 2026-11-07, adopted as you wrote it): it ships in
v2.7, stays through every v2.x (roster repos still to migrate; a stale branch can bring old forms back; a
rerun on a clean ledger changes nothing), and is removed in v3.0 with the reading of the old forms. v3.0's
precondition is that `migrate --dry-run` gives no diff in every roster repo, which covers archived entries
(`check()`'s retired findings read open entries only). This adds `migrate` to §7.1's v3.0 row.

**S8. The grammar appendix** adds the header block and the Log's fixed line shapes, each production with an
accepting and a refusing fixture (§7.4 *Grammar*).

## The builds this scope gives (filed only on your go after the rounds)

In series: each edits `SPEC.md`, the module and `fixtures/run.py`.

- **B1.** The module's pure `migrate_entry(text, *, archived, closed_date=None, kinds=None) -> (text,
  report)`, sharing `status_notes_to_log()`: S2, S3, S5. SPEC's new *Migrating to v2.7* section. The §7.4
  fixtures: twice gives no diff; an unmapped archived word (or a missing date) stops it with a list and writes
  nothing; unknown text survives `migrate`.
- **B2.** `ledger.py migrate`: `--dry-run` (the `--plan` shape), `--closed-dates <file>`, `--kind`, one
  commit under `migrate_subject()`; write-all-or-nothing.
- **B3.** The closed Status set in `check()` (S1), `Location` and `Waits` out of the canonical order, and
  **this repo's own ledger migrated in the same PR**: ledgerboard's archive holds Status tails (TD-053's
  `Resolved 2026-11-06: designed and built …`), so B3's check would fail its own merge gate otherwise.
- **B4.** The grammar appendix (S8), and the target design's §7.1 v3.0 row naming `migrate` (S7).

Then the release (yours), and the hand-off: once v2.7 is tagged, an entry on agent-cadence's ledger, then
ShiftLead's, each to vendor v2.7 and run `migrate` in the same PR (§7.2 step 6; ShiftLead also drops `Waits
= until | event` from its `Fields:` line), filed through each repo's question seat (`ao td add --repo`).

## Not in this release

- Renaming `**Resolved:**` to a status-neutral lead (§2.2: v3.0 material).
- Removing the old-form readings (`Waits`, `Taken by`, `decision (who) — text`, a header `Resolved`): v3.0.

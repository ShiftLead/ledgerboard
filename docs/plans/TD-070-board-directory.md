# TD-070: the board as a directory, one file per item, for v3.0

**Status:** **Split (2026-11-13).** Paul answered Hold with a split; TD-092 designs B1 and B2 in docs/plans/TD-092-board-item-reader.md, and what remains here (D1, D2's moves, D7's writer half, D8, D10, D11's split, D12's release, B3–B5) is the unreviewed draft TD-070's second part starts from, once TD-092 converges. **Split again (2026-11-14):** Paul answered TD-095's scope Split; TD-095 designs B3 and B4 in docs/plans/TD-095-board-writer-gate.md, whose draft 1 is this plan's B3 and B4 text moved unchanged (D1, D2's moves and stamps, D7's writer half, D8, D10 and their texts, fixtures, rows and builds), and what remains here (D11, D12, B5 and the texts, fixtures and lines that are B5's) is TD-098's to start from, once TD-095 converges. **Split a third time (2026-11-14):** on Paul's Go on TD-095 (2026-11-13), TD-098 designs B5 in docs/plans/TD-098-board-migration-release.md, whose draft 1 is what remained here (D11, D12, *Consumers*' last lines, B5's texts, fixtures and build), moved unchanged; this plan keeps no live decision, only TD-070's scope, its review history and the pointers to TD-092's, TD-095's and TD-098's plans.

Draft 11, 2026-11-13 (session lb-designer). Paul answered **Go** to the scope as drafted (S1–S10,
TD-070's `decision (paul)`, 2026-11-11): every recommendation in it stands. He answered the end-of-rounds item **One
more round** (2026-11-12), run as TD-081: round 7, past the cap. Before it, the plan took two facts settled since
round 6: Paul's **Go** on TD-065's design (`Doer:` ships in v2.8, so the two-outcome branch went) and, after his **Go** on TD-075's design (2026-11-12), TD-075's B1 in
the same last v2.x minor as TD-078's B1 and B2. Round 7's fact-check (R14) raised one build-changing finding (F87) and
its design review (R15) two (F90, TD-075's forms carried into no v3 writer; F91, the `doer` record at B1, reopening
F68), with five minor; all applied. Round 7's closing fact-check (R16) raised four build-changing findings, all slips in
round 7's fixes (F95 `BoardItem.answers`, F96 the `## Edits (v3.0)` search and B5's swap, F97 a non-`act` `Doer` at
the split, F98 the split's `Doer` spelling against the read-back), and six minor (F99–F104: four applied, F102 rejected, F104 a check with nothing to change); its fixes re-checked
(R17, four minor, applied), read by no
design review, so the end-of-rounds item recommended **One more round** again. Paul answered **One more round**
(2026-11-12), run as TD-085: round 8. Its fact-check (R18) raised three build-changing findings (F111 rejected, F112,
F113) and two minor (applied), its re-check (R19) one minor (F116, rejected), and its design review (R20) seven
build-changing (F117–F123: the subject's session and head, prose after the first item at the split, `parse_item()`'s
`Due` and `Kind` rules, `parts_problems()`' prefix, the `add` fixtures' ids, the `doer` board case, and
`item_record()`'s keys from a v3 item) and five minor (F124–F128), all applied; F129, from TD-078's round-8 review,
moves TD-075's B1 (TD-084) and TD-065's B1 (TD-083) out of B1's blocks, both merged. The closing fact-check (R21) raised nothing build-changing and seven minor (F130–F136), six applied and F136 rejected, so the rounds end after the bought round with the design review's seven fixes read by no design review: the end-of-rounds item again, recommending **One more round**. Paul answered **One more
round** (2026-11-12, #264), run as TD-087: round 9. Its fact-check (R22) raised two build-changing findings (F138,
the split refusing an `fyi` v2 reads with `fyi_due`, reopening F131; F139, D7's one string rule as a test that
works, reopening F124 and F135) and three minor (F140–F142), all applied. Its re-check (R23) raised four minor
(F143–F146) and its design review (R24) seven build-changing (F147–F153: the fixture boards against the split's
refusals, reopening F118, F128, F130 and F138; the grammar's field order, reopening F78; every test file given a
build; B5's removals in `run.py`, reopening F96 and F125; `_context_gate()` at B1, reopening F113 and F124;
`board.py`'s output shapes, reopening F127; `lift_pr_verdict()`'s changed set from the trees) and nine minor
(F154–F162), all applied or rejected as the record says. **The author's ruling** (round 9) ends the split's
refusals: the split refuses only where it cannot give an item an id or a month, or where the read-back's records of
the v2 item and its split file would differ; every other shape v2 reads is carried as v2 reads it and read alike by
the v3 reader; the shapes rule 14 names are named by `board_dir_problems()` and listed by `split_board_notes()`
(D11, text 8), and any other is carried silently, as a v2 board holds it today (round 9's F170). So F128's kind
misfits, F138's `fyi` `Due` and F97's and F79's `Doer` spellings are carried and named, F130's non-`fyi` `bad_due`
is carried and reported as `due_error` (round 9's F163), and every v2 fixture board splits. R24 saw no wrong-design
signal; its recurring topic, one more split refusal per round (F62, F80, F93, F97, F118, F128, F130, F138), is
ended by the ruling. Round 9's closing fact-check (R25) raised two build-changing findings (F163, a non-`fyi`
`bad_due` said named though no rule names it; F164, `due_in_context` refusing any date-shaped `Due` inside another
span, wider than a read difference: it now refuses only the match v2 reads) and nine minor (F165–F173), all
applied. So the rounds end after the bought round with the design review's seven build-changing fixes
(F147–F153), the ruling and the closing fixes read by no design review: the end-of-rounds item again,
recommending **One more round**.
Draft 1 turned the scope into the full design: its decisions, the exact `SPEC.md` text, the fixtures and the
builds. Rounds: six ran, ending at the cap (round 6's design review still raised build-changing findings, F73–F76,
now applied; no design review has read them). Build-changing per design review 12, 4, 3, 5, 3, 4, 2, 7, 7 (round 8's R20, round 9's R24); fact-checks 2, 2,
1, 0, 0, 0, 1, 3, 2 (one rejected; round 8's R18: F111 rejected, F112, F113; round 9's R22: F138, F139), closing fact-checks 1, 4, 0, 2 (rounds 6–9: round 6's F81, `_real_day()` for a day's check, applied and read by
no design review with round 6's; round 9's F163, F164). Recurring topics: tie and list order (F14, F30, F32, F45), the build-by-build shims (F23, F33, F44, F53,
F55), the dual-mode reader seam, a v2 line or a `BoardItem` and its file (F13, F23, F44, F55, F66, F109, F113, F117,
F123, F124: round 8 ends it with *The builds*' table of every reader, its v3 source and its build), Doer and TD-065 (F18, F19, F29, F38, F46, F58, F68), each judged ended by round 6's design review (order by round 3's rule
for comparing two reads, F45; the shims and `Doer` by round 5's cuts). Each round's fixes applied, with the author's (the designer session's) rulings where the findings offered a
choice (round 1: the tie order, `Doer:`, the releases, the sweep's reads, the stub; round 2: v2.8's content, ties at
the split, the board's own major, the records through the builds, the duplicate-id tie-break; round 3: `Doer:` as
this design's own field, the consumers' call sites, the v2 writers' read-backs, the order and the comparison of
records, the major of an undeclared v2 board; round 4: the records' JSON shapes, a v3 item's `raw` and
`show_board()`'s place; round 5: `BoardItem.words` beside a v2 item's `text` from B2 to B5, replacing round 4's one
accessor and its grep check; `Doer:`'s own value reader and TD-065 decided before B1, replacing round 4's delta
rule; one numbered list of the read's problems; `show_board()`'s bytes; round 6: named value readers for
`Decided`, `Closed` and `Answers`, `split` without `--to`, an unreadable `Kind`, `Hide until`, `Parts` or `Doer`
read as absent; round 9: the split refuses only what it cannot place or would read differently).
Class: **wide** (a new
major of a vendored, published format, read and written by both consumers; cap 6 rounds, cadence.md §4.8).

**Entry:** [TD-070](../ledger/TD-070.md). **Source:** the entry's Why and Fix; the scope (S1–S10, kept as each
decision's source below); [target design](target-design.md) §7.1's v3.0 row; `SPEC.md` *The board*, *Edits*, *The
board writer*, *The merge gate's verdicts*, *The ledger as a directory* (the precedent), *Ledger entries and their
edits* (the grammar the item file reuses); both consumers' pinned code, read 2026-11-11 (cited by file and function).

## The problem

A board is one Markdown file, and every new item is written at one place in it: `board.py add` puts it above the
first item of its section (`plan_add()`). Two PRs that each add an item always conflict, and GitHub's merge runs
no merge driver, so each collision costs a rebase and a full precheck. No layout inside one file avoids it: two
inserts at one anchor conflict wherever the anchor is. A later agent-cadence than this repo's pin (`67023cc`) adds
`board_edit.py replay` (its TD-248), which does the rebase's hand edit, not the rebase.

The conflicts are real but not the case for a major. Counted on 2026-11-11 from one machine's session transcripts
since 2026-10-12 (a count round 1 did not re-check): about 140 conflict events on v1 ledger files, 3 on v2 ledger
directories, 7 on boards (a floor). The case is **the item's shape**. A `decide` item is a line of up to a kilobyte
or more (this repo's board holds closed lines of up to 1,071 characters, 1,083 bytes, and two open ones of 280 and
575), with a detail block and a life of its own: open, decided, closed, archived. That is an entry's shape, and the
single line carries costs an entry does not:

- **Its identity is its text.** The item key is the line with some fields cut out. Consumers persist it
  (ShiftLead's work orders are `board:` and 8 hex digits of its hash, `sessionorc/workorders.py` `key()`), so what
  the key is for a line is part of the format, and every new field has had to decide whether it is in the key
  (`Hide until:` in v2.3, `Parts:`, `Lifts:`, TD-065's `Doer:`).
- **Fields live inside prose.** A Context ends where the next field name begins, so the writer refuses any text,
  answer, detail value or reply that holds a field name, every new field widens that refusal and can re-read an old
  line, and a `Decided:` answer may not end in `(by …)`.
- **Two copies of one item are the merge rule.** An open and a closed line with one key mean "closed: a merge kept
  both sides", and `archive_closed()` carries twins, its refusals and the `ARCHIVE_AT` threshold. This repo's board
  holds 36 closed items, over three times the threshold, because archiving is a separate PR nobody owes.

## What is already settled

- **The scope** (Paul's Go, 2026-11-11): S1 do it; S2 the id `YYYY-MM-DD-<8 hex>`; S3 the item file as a small
  entry; S4 `docs/user_attention/` with `README.md` and `archive/<YYYY-MM>/`, no sections unless a consumer reads
  them; S5 `load_board(path, ls, read)` over either major; S6 the writers by `--id`; S7 the verdicts over a
  directory; S8 `board.py show`; S9 `split_board()` and `key_id()`; S10 the consumers' own entries.
- The precedent, the entry grammar, what an item means and what a new major reads — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, *What is already settled* (2026-11-13 split).

## Options weighed

**Whether to do it (S1).** (a) The directory. (b) The single file, with `replay` for the rebase. (c) The file, with
`add` writing at a hashed place. (c) changes nothing about the key or the twins, and two inserts on neighbouring
lines still conflict. (b) keeps every cost above for the life of v3; only a count of what `replay` still costs
could argue for it, and the case is the shape, not the count. **(a).**

**The id (S2), the item's form (S3), `Decided:` in a field, sections (S4), listing the archive's months and what is left at `docs/user_attention.md`** — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, *Options weighed* (2026-11-13 split).

## Decisions

**D1. The board is a directory in v3.0 (S1)** — moved to TD-095's plan, docs/plans/TD-095-board-writer-gate.md, D1 (2026-11-14 split).

**D2. The layout (S4).**

The layout as the reader sees it (the directory tree, an open and a closed item's paths, every preamble line read from `README.md`) — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, D2 (2026-11-13 split).

Its moves on close and **README's stamps** — moved to TD-095's plan, docs/plans/TD-095-board-writer-gate.md, D2 (2026-11-14 split).

**D3. The item id (S2)** — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, D3 (2026-11-13 split); its writer half is restated in TD-095's plan, docs/plans/TD-095-board-writer-gate.md, D3 (2026-11-14 split).

**D4. The item file (S3)** — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, D4 (2026-11-13 split).

**D5. No sections (S4)** — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, D5 (2026-11-13 split).

**D6. Reading (S5)** — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, D6 (2026-11-13 split).

**D7. The edits and the writers (S6).** Its module half (`edit_item()`, `item_file()`, `decided_file()`, `item_file_problem()`, `canonical_item_file()`, TD-075's forms, the one rule for a string argument, `_context_gate()`, the gate and the commit subjects) — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, D7 (2026-11-13 split); `board.py`'s half — moved to TD-095's plan, docs/plans/TD-095-board-writer-gate.md, D7 (2026-11-14 split).

**D8. What a person reads (S8)** — moved to TD-095's plan, docs/plans/TD-095-board-writer-gate.md, D8 (2026-11-14 split).

**D9. The gate sweep over a directory** — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, D9 (2026-11-13 split).

**D10. The merge gate's verdicts (S7)** — moved to TD-095's plan, docs/plans/TD-095-board-writer-gate.md, D10 (2026-11-14 split).

**D11. Migration (S9)** — moved to TD-098's plan, docs/plans/TD-098-board-migration-release.md (2026-11-14 split).

**D12. The release: v3.0, and v2.8 before it** (its order of the builds and the release) — moved to TD-098's plan, docs/plans/TD-098-board-migration-release.md (2026-11-14 split).

## Consumers

Each consumer's lines not moved to TD-092's or TD-095's plan — moved to TD-098's plan, docs/plans/TD-098-board-migration-release.md (2026-11-14 split).

## The SPEC text the build lands

Texts 1, 8's *Migration*, 10's B5 parts, 12 and 14's two bullets, and B5's search, with the pointers to TD-092's and TD-095's plans for the rest — moved to TD-098's plan, docs/plans/TD-098-board-migration-release.md (2026-11-14 split).

## Fixtures

B5's fixtures and unit tests (`fixtures/board/<case>.v3/`, `fixtures/board_split/`, B5's `fixtures/board_writer/` cases, the retired groups), with the pointers for the rest — moved to TD-098's plan, docs/plans/TD-098-board-migration-release.md (2026-11-14 split).

## The builds

The reader table's remaining rows, B5 and the order — moved to TD-098's plan, docs/plans/TD-098-board-migration-release.md (2026-11-14 split).

## Not in this design

The ledger's own v3.0 removals (`Waits`, `Taken by`, the old decision form, a header `Resolved`, `migrate`) and the
archived entry's writer route are TD-078's. When v3.0 is cut, and what else it carries, is Paul's.

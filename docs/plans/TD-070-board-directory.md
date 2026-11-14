# TD-070: the board as a directory, one file per item, for v3.0

**Status:** **Split (2026-11-13).** Paul answered Hold with a split; TD-092 designs B1 and B2 in docs/plans/TD-092-board-item-reader.md, and what remains here (D1, D2's moves, D7's writer half, D8, D10, D11's split, D12's release, B3–B5) is the unreviewed draft TD-070's second part starts from, once TD-092 converges. **Split again (2026-11-14):** Paul answered TD-095's scope Split; TD-095 designs B3 and B4 in docs/plans/TD-095-board-writer-gate.md, whose draft 1 is this plan's B3 and B4 text moved unchanged (D1, D2's moves and stamps, D7's writer half, D8, D10 and their texts, fixtures, rows and builds), and what remains here (D11, D12, B5 and the texts, fixtures and lines that are B5's) is TD-098's to start from, once TD-095 converges.

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

**D11. Migration (S9).** `split_board(board, archive)` gives the v3 files of a v2 board and its archive, by path in
the directory.

**What the split refuses** (the author's ruling, round 9; F147, F154, ending the run of one more refusal per round:
F62, F80, F93, F97, F118, F128, F130, F138). **The split refuses only where it cannot give an item an id or a
month, or where the read-back's records of the v2 item and its split file would differ (data lost, or read
differently).** Every other shape v2 reads is carried as v2 reads it and read alike by the v3 reader. The
shapes rule 14 names (a field not in its form or on a kind that does not take it, a `Doer` spelling, a `Kind`'s
case, an `fyi`'s `Due`) are named by `board_dir_problems()` and listed by `split_board_notes()` for the caller to
fix on the directory when it chooses; any other (a `decide` with no `Answers`, a `look` whose answers are not the
fixed pair, a non-`fyi` unreadable `Due`, reported as `due_error`, …) is carried silently, as a v2 board holds it
today, since the gate judges an item only when it is added (round 9's F170). This replaces round 8's "the split refuses what no v3 check would ever name again" (F128): a misfit is
data a v2 board legally held and v2 read, and refusing it made the split's own list grow each round. So `Answers:`
on an `act`, `Parts:` or `Lifts:` off a `decide`, `Doer:` off an `act` or in a spelling D4 faults, and a `Due`
on an `fyi` are all carried. The rule, for each:
- every line of one id, across the board and the archive, is one item, closed when one of them is (the twins
  become one closed item, as D6 reads them); it becomes `<id>.md`, or `archive/<YYYY-MM>/<id>.md` when closed, its
  id as D6 gives the v2 item (`key_id()`), so a consumer that persisted `board:<8 hex>` finds its item by the id's
  last 8 digits;
- **a twin's closed line and its detail block supply every field and the body**; the open twin is read for nothing;
- its fields are the v2 reader's, rewritten into the file's forms: `Context` and `Closed`'s why lose their final
  period (`Closed: 2026-11-12 — lifted.` becomes `**Closed:** 2026-11-12 — lifted`), `Decided` becomes `<date>[ by
  <person>] — <label>`; its body is the detail block, common indent removed; its replies are the Log. A v2 item's `closed` (B2) — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, D11 (2026-11-13 split);
- **its heading is `item_words(line)`** — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, D11 (2026-11-13 split);
- `README.md` is the board's text before its first item, `Ledgerboard: 3` under its title, less the `## ` heading
  nearest the first item (with more than one `## ` heading before it, only that one drops), each relative link
  gaining `../`: an inline link or image's target (`[t](target)`, `![t](target)`) or a reference definition's
  (`[label]: target`) whose target starts with no scheme (`[A-Za-z][A-Za-z0-9+.-]*:`, `mailto:` among them), no
  `#` and no `/`, outside code spans and fenced code;
- a v2 item's `Doer` is carried as written (round 7's F93, F98: a respelling would break the read-back, whose
  records compare `doer.text`; round 9's F147 reverses F97's refusal and F98's): one spelled with more than one
  space or a tab after `team` (F79), one on a kind but `act`, and one outside its form are each written as the line
  holds it and named by rule 14. The header value is `parse_doer()`'s text (the value trimmed, one final `.`
  dropped), and also for a value `doer_value()` refuses, with one exception that keeps the two reads alike: when
  dropping the period leaves the value ending in whitespace (`Doer: acme .`, which v2 reads as no doer since `acme `
  is no repo), the header line, whose value's end whitespace a reader drops, would read `acme`, a doer; so that
  value keeps its period (`**Doer:** acme .`), which v3 also reads as no doer. An empty value (`Doer: . Due:
  …`, `Doer: Due: …`), which `parse_doer()` reads as no doer, has no span: its text stays in the heading, as
  `item_words()` reads it, and the split writes no `Doer` field (round 9's F172);
- **a field its kind does not take** (round 8's F128, reopening F97; round 9's F147, the ruling, reversing F128's
  refusal): `Parts:` or `Lifts:` on any kind but `decide`, `Doer:` on any kind but `act`, `Answers:` on a kind that
  takes none (F154: `Answers:` on an `act` is v2-legal data). v2's readers read each on any kind and so does
  `parse_item()` (D4), so the records agree: the field is carried, named by rule 14, listed;
- **a `Due`**: a day as `**Due:** <date>`; a v2 `bad_due` as `**Due:** <raw>`, its span the match v2 reads (D4,
  round 9's F171: v3 reads the same `bad_due` whenever `raw` is no day), carried and reported as `due_error` by
  both, named by no `board_dir_problems()` rule and listed by no `split_board_notes()` line (round 9's F163); an
  `fyi`'s `Due`, of any shape v2 recognises, a colonless one among them (round 9's F145), carried and read as
  `fyi_due` by both (D4, reverting F138's refusal), named by rule 14. The kept refusals (D4): a non-`fyi`
  colonless `Due <day>.`, whose `raw` v3 would read as a day (`due_no_colon`), and the match v2 reads lying inside
  another field's or a reply's span (`due_in_context`, round 9's F164); a date-shaped `Due` in such a span that v2
  does not read stays in its words and is carried (`context_due_words`);
- **lines after the first item that are no item** (round 8's F118). On a v2 board, a line after the first item that
  is no item, no detail block's line and not blank (a placeholder `- (none)`, as this repo's board holds under `##
  In-flight`, or a note a hand edit left) is prose no reader reads. The split loses none of it: each such line is
  carried, in order, to the end of `README.md`, after one blank line, together with each `## ` heading after the
  first item that stands above a carried line (with no carried line under it, a heading is dropped, as the heading
  nearest the first item is); one blank line separates the groups. `split_board_notes()` then lists them as it
  lists any README line (an `In-flight` heading among its names), for the caller to keep or delete. It refuses a
  carried line that a v3 reader would read as preamble (`People:`, `Answered by:` or `Ledgerboard:` at a line's
  start, `_people_line()`'s and `_answered_by_line()`'s shapes): a v2 reader never read one below the first item, and
  in `README.md` it would start to count, so it is moved or deleted on the v2 board first;
- **it refuses**, each by the ruling's two grounds: no id or no month, an item with no date or a date that is no
  day (`_real_day()`: `item_id()` refuses `2026-02-30`, round 9's F165), a closed item (a `[x]`
  line) with no readable `Closed:` date (round 4's F62: add the date by hand first), two open lines of one id, two
  closed lines of one id and two items given one id (one file each cannot be written); a read difference, a carried
  preamble line (above: it would start to count in `README.md`), a non-`fyi` colonless `Due <day>.` and the `Due`
  match v2 reads inside another span (above, D4), and a result that does not read back the same items (compared as D6's
  *Comparing two reads*), the guard that catches any other. `board_dir_problems()` of the result names rule 14's
  carried shapes, which `split_board_notes()` lists and the split does not refuse; any finding under another rule is
  a fault of the split itself, and refused. Nothing else is refused;
- **`split_board_notes(files)`** (round 9's F147, the ruling; it took `readme` before) takes `split_board()`'s
  `{path: text}` and gives `(path, line number, line, why)`: `README.md`'s lines that may still describe the v2
  board (as before: a line naming `user_attention.md`, `user_attention_archive.md`, `Needs the user` or
  `In-flight`, a `Format:` line, the carried lines among them), then each rule-14 finding `board_dir_problems()`
  makes of the files (over `_dict_ls()`), at the line of the field it names, found by the field's name in the
  item's `fields` (the first header line whose name `field_key()` reads as that field; round 9's F173), in its
  order. **A head holding more than session and host** (TD-092's round 5's F238): a v2 line whose head group holds
  text after its session and host (`(session s-1 on host-a, branch x)`'s `, branch x`) loses that text at the
  split, since no v2 reader reads it into a field (TD-092's plan, D11's prefix), so the notes list it as a carried
  shape's note, at the item's `Session` line (or, with no `Session`, its heading), naming the text lost, so a person
  sees the loss. The written files no longer hold that text, so the note is made from the v2 line (its `raw`), which
  the notes' input must reach: how (the split's own result carrying it, or `split_board_notes()` taking the v2
  texts) is B5's design, open for the second part's rounds, as are this note in text 8's *Migration* bullet
  and a `board_split` case for it (`head_extra`; PR #277's review). `board.py split` prints
  them as warnings (`warnings` in `--json`).

**The key a consumer persisted** (ShiftLead's `key()`, `key_id()`, an indented line and a `[x]` line) — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, D11 (2026-11-13 split).

`board_stub(title, name)` is the stub `board.py split` leaves at the v2 path. `split` takes no target (round 6's
F75): it always writes the directory beside the board, named the board's name less `.md`, since that is the one
directory the stub reads as (D6); any other place would leave a stub reading as a missing directory. `split_board_notes(files)` names
README lines that may describe the v2 board and the carried shapes rule 14 names (above). `board_dir_problems(path, ls, read)`, `v2_problems()`'s twin — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, D11 (2026-11-13 split).
`key_id(key)` and `item_key()` are kept through v3.x. The split runs in each consumer's v3.0 vendor PR, beside v3.0's
ledger half (TD-078), landed when no open PR edits the board (each such PR is redone over the directory).

**D12. The release: v3.0, and v2.8 before it.** v3.0 is a major (*Versions* text 12). It reads v2 boards and writes
v3 only. It goes out with TD-078's ledger half as one v3.0; when, and what else it carries, is Paul's. The order:
- **B1's precondition** (the last v2.x minor, v2.8, released before B1 merges and none after it; TD-065 in v2.8, its `doer_value()` reused; TD-078's open question and B1's blocks) — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, D12 (2026-11-13 split).
- **The builds**, B1 to B5, merge in order with no release between them; TD-091 (TD-078's B4) follows B5 (round
  9's F142); then v3.0.

## Consumers

Both change in their v3.0 vendor PR, each through an entry filed in that repo through its question seat once v3.0
is cut, agent-cadence's first. Each line below is a line for that entry, never code here.

- **agent-cadence**:
  - vendor v3.0 and run `board.py split` on `docs/user_attention.md` in the same PR, landed when no open PR edits
    the board;
  - `board_edit.py` — moved to TD-095's plan, docs/plans/TD-095-board-writer-gate.md, *Consumers* (2026-11-14 split);
  - `nudge_user_attention.py`: read boards through `load_board()` (its own checkout's directory; another repo's
    through the forge's directory listing, with `since=` the months it shows); its `ARCHIVE_AT` prompt and its
    duplicate-key warning (`closed_items()`, `item_key()`) go; `--report --json` prints ids, not lines;
  - `check_cadence.py`'s `BOARD` and `classify_direct()` — moved to TD-095's plan, docs/plans/TD-095-board-writer-gate.md, *Consumers* (2026-11-14 split);
  - `list_sessions.py` `board_items()`: open items' `Session` through `load_board()`;
  - its cadence check (`check_cadence.py`) gains a board row beside its ledger row, which today reads the PR's
    ledger through `ledger_pair_at()` and fails on `v2_problems()`'s faults (through `ledger.py`'s `v2_unread()`):
    the board row reads the head's board, fails on `board_dir_problems()`'s and on `version_problem(board)` (D6),
    since the gate judges an item only when it is added and damage a hand edit does to an existing file is caught
    only there (D7); `precheck.py` runs the repo's own command and reads no board;
  - the own-board path in `cadence_hooks.sh` and `check_claude_memory.sh`; cadence.md §3, §4.3 and §4.4,
    `docs/procedures/stranded-work.md`'s stamp step (`README.md`), and the board's SEED skeleton (no `Format:` line
    for the item line, no sections, closing archives).
- **ShiftLead** (after agent-cadence's vendor PR, through its pin):
  - first, a check: the entry greps its stores and code for a persisted `board:` reference of any shape other than
    `board:` and 8 hex digits (a full key text, a line number) and names each it finds; `workorders.py`'s own
    `_REF_RE` (`board:[0-9a-f]{8}`) is the shape it persists;
  - work orders become `board:<id>`; a persisted `board:<8 hex>` (`key()`, quoted in D11) resolves to the item whose
    id ends `-<8 hex>`, which `split_board()` gives every migrated item, open or closed; a closed one resolves while
    its archive month is read, so a resolver that finds no open item reads the whole archive before it reports none;
  - `sessionorc/board.py` — moved to TD-095's plan, docs/plans/TD-095-board-writer-gate.md, *Consumers* (2026-11-14 split);
  - `gatesweep.py` `board_of()` reads the directory at the ref, whole (`BOARD_DIR`, an `ls`/`read` pair over `git
    ls-tree` that lists subdirectories; no `since`, D9), and closes by id; since no writer edits a closed item, its
    `read` may cache each archive file by path and blob sha and fetch only the months and files new since its last
    read;
  - its read seam (`sessionorc/seams.py`, where `ledger()` calls `ledger.v2_faults()`, which wraps
    `v2_problems()`) gains the board's: `board_dir_problems()` and `version_problem(board)` (D6, D7) make the board
    *unreadable* or *newer*, as `v2_faults()` and `version_problem()` do the ledger;
  - `workorders.board_items()` reads `load_board()` and `needs_you(board, today)`, keyed by the record's `id`;
    `carried()` reads the closed items' `closed` and `decided` fields where it cuts `Closed:` from the line;
  - the repo's `board:` setting (`repoconfig.py`) defaults to the directory where it exists, else the v2 file; the
    Inbox draws a board item from its record's fields rather than cutting its line.

## The SPEC text the build lands

The section's opening (what a block is, and *No sentence lands before the code*, which tags each text's sentences by build) — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, *The SPEC text the build lands* (2026-11-13 split).

**1. The title.** `# The ledger and board formats — versions 1 and 2` becomes `# The ledger and board formats —
versions 1 to 3`.

**2.–6.** *The board*'s first three paragraphs, *The item key*, *What needs the person*, *Preamble lines* and *The gate sweep* — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, texts 2–6 (2026-11-13 split).

**7. *The board*, *The merge gate's verdicts*, its first paragraph** — moved to TD-095's plan, docs/plans/TD-095-board-writer-gate.md, text 7 (2026-11-14 split).

**8. A new section, `## The board as a directory (v3.0)`** — its opening, *The item id*, *The item file*, `parse_item()`, *Reading a board* and *Damage* moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, text 8 (2026-11-13 split); its *Migration* and the bullets under it (B5's) stay here:

>
> **Migration** is `split_board(board, archive)`, for a v2 board only: the v3 files of a v2 board and its archive,
> by their paths in the directory. **It refuses only where it cannot give an item an id or a month, or where the
> read-back's records of the v2 item and its split file would differ** (data lost, or read differently). Every other
> shape a v2 board holds and v2 reads is carried as v2 reads it and read alike by the v3 reader. A field not in its
> form or on a kind that does not take it, a `Doer` spelled as the writer would not, a `Kind` in the wrong case and
> a `Due` on an `fyi` are named by `board_dir_problems()` and listed by `split_board_notes()`, for the caller to fix
> on the directory; any other shape (a `decide` with no `Answers`, a `look` whose answers are not the fixed pair, an
> unreadable `Due`, reported as `due_error`) is carried silently, as a v2 board holds it, since the gate judges an
> item only when it is added.
> - Every line of one id across the board and the archive, with its detail block, is one item, closed when one of
>   its lines is; it becomes `<id>.md`, or `archive/<YYYY-MM>/<id>.md` when closed, its id the v2 item's. Of twins,
>   the closed line and its detail block give every field and the body. Its fields are what the v2 reader reads,
>   each in the file's form: `Kind`, `Added` (the line's date), `Session` (none for `n/a` and `(person)`),
>   `Context` (without its final period), `Parts`, `Doer` (as written; none for an empty value, whose words stay in
>   the heading), `Due` (from the match v2 reads: `Due:` and a day when the first such is a day, else the first
>   date-shaped `Due`, with or without its colon, an unreadable one as written), `Hide until`, `Answers`, `Lifts`,
>   `Decided` (`<date>[ by <person>] — <label>`) and
>   `Closed` (`<date>[ — <why>]`, the why the words after a ` — ` that follows the date, without its final period),
>   from the closed line, and any other field the v2 reader reads, as the header field of the same name, whatever
>   the item's kind. Its body is the detail block with its common
>   indent removed; its replies are its Log. Its heading is `item_words()` of the line: every word the v2 reader
>   reads as no field, no reply and no part of the prefix (the text, and any words a hand edit left outside the
>   fields), in their order, verbatim but for runs of whitespace collapsed to one space, so no word of the line outside its head is lost (a
>   head's text after its session and host, which no v2 reader reads, is not carried, and `split_board_notes()`
>   names it) and no
>   period is added or removed; a bold head stays in it as written.
> - `README.md` is the board's text before its first item, with `Ledgerboard: 3` under its title (any
>   `Ledgerboard:` line dropped) and without the `## ` heading nearest the first item (the one heading that opens the
>   first item's section; any earlier `## ` heading stays). Each relative link there gains `../`, since the file
>   moves one directory down: the target of an inline link or image (`[t](target)`, `![t](target)`) and of a
>   reference definition (`[label]: target`), when it starts with no scheme (`[A-Za-z][A-Za-z0-9+.-]*:`, `mailto:`
>   among them), no `#` and no `/`, outside code spans and fenced code. The archive's text before its first item is
>   dropped.
> - A line after the first item that is no item, no detail block's line and not blank (a `- (none)` placeholder, a
>   note) is carried, in order, to the end of `README.md` after one blank line, with each `## ` heading after the
>   first item that stands above a carried line; a heading with no carried line under it is dropped. Nothing is
>   lost, and `split_board_notes()` lists what may describe the v2 board.
> - It refuses a board that declares `Ledgerboard: 3`; an item with no date, or a date that is no day of the
>   calendar; a closed line with no readable
>   `Closed:` date (no month to file it under: date it first); two open lines, or two closed lines, of one id; two
>   items given one id; a carried line that is a `People:`, `Answered by:` or `Ledgerboard:` line, which a v2
>   reader never read below the first item and `README.md` would read (move or delete it first); a `Due` v2 reads
>   as unreadable that v3 would read otherwise: on any kind but `fyi`, a colonless `Due <day>.`, and on any kind
>   the `Due` v2 reads lying inside another field's words or a reply's (fix it first; a date-shaped `Due` there that
>   v2 does not read stays in those words); and a result that `load_board()`
>   does not read back as the same items (open and closed, at one date, compared as *Reading a board* compares two
>   reads), or that `board_dir_problems()` flags under any rule but the one that names a field not in its form or
>   on the wrong kind. A field on a kind that does not take it, a `Doer` spelled as the writer would not and a
>   `Due` on an `fyi` are carried and named; an unreadable `Due` on any other kind is carried and reported as
>   `due_error`, as on a v2 line, and named by no rule.
> - `board_stub(title, name)` is what `board.py split` leaves at the v2 path: `# <title>`, a blank line,
>   `Ledgerboard: 3`, a blank line, and `This board is the directory [<name>/](<name>/), one file per item
>   (ledgerboard v3.0).` A v2.x reader that checks the version refuses it, a v2.x writer refuses it unread, and
>   `load_board()` reads the directory through it.
> - `split_board_notes(files)`, over `split_board()`'s files, lists as `(path, line number, line, why)`, for the
>   caller to warn about, nothing rewritten: the lines of that `README.md` which may still describe the v2 board (a
>   line naming `user_attention.md`, `user_attention_archive.md`, `Needs the user` or `In-flight`, and a `Format:`
>   line), then each shape the split carried that `board_dir_problems()` names, at its field's line (the first
>   header line of that field's name).

**9. *Edits*** — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, text 9 (2026-11-13 split).

**10. *The board writer*** — its B3 text moved to TD-095's plan, docs/plans/TD-095-board-writer-gate.md, text 10 (2026-11-14 split); its B5
parts stay here: `plan_split` in the first paragraph's library list (after `plan_fmt`, B5's: round 9's F155), the
"(*split first*)" of the paragraph added after the actions list, and the `split` bullet, after the `fmt` bullet:

> - **`split`** (v3.0) — a v2 board (`--board`, its archive `--archive`, default beside it) split into its directory
>   (`split_board()`) always written into the directory beside it named the board's name without `.md` (which must
>   not exist), the directory the stub then reads as: every file written,
>   the v2 file replaced by `board_stub()` and its archive removed, as one write; `split_board_notes()`'s lines are
>   printed as warnings (`warnings` in `--json`). It prints no subject;

**11. *The ledger as a directory*, *The caller does the I/O*** — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, text 11 (2026-11-13 split).

**12. *Versions*, after the last v2.x paragraph** (the last minor's, v2.8's, released before B1 merges, D12; on
`main` today "v2.8 gives `migrate` the last old forms", TD-089's, after TD-088's "v2.8 gives an archived entry a
note": round 9's F159), add. **It builds on TD-092's text 15** (TD-092's round 5's F241): B2 lands that
*Versions* paragraph first, naming what a v2 board reads differently from B2 on and that a board declaring 3 is
readable, so this paragraph follows it, and at B5 its "It reads a v2 board differently" sentence is reconciled with
that paragraph rather than repeating it:

> **v3.0 makes the board a directory** (*The board as a directory*, *Edits*, *The board writer*, *The merge gate's
> verdicts*): one file per item, named by its id, in `docs/user_attention/` with `README.md` and
> `archive/<YYYY-MM>/`, closing an item moving its file. **It reads a v2 board**: `load_board()` gives the same
> items for a v2 file and its archive as for its split, each v2 item with the id `split_board()` gives it, so a
> consumer vendors v3.0 before it splits its board, and reads other repos' boards in either major. It reads a v2
> board differently in two ways: an open line whose closed twin is in the archive is closed, where v2.x read the two
> as two items, and twins match by id, so the indent no longer tells them apart; and a board file that declares no
> major reads as 2, the format a board's v1 and v2 share (*Versions*' "none means 1" stays the ledger's). **It
> writes v3 only**: `board.py`'s writes refuse a v2 board (*split first*). **What goes:** the item key as what an
> item is (`item_key()` remains, only to read a v2 line and as `key_id()`'s input); the open-and-closed twin rule
> (read on a v2 board alone); `archive_closed()`, `archive_subject()`, `ARCHIVE_AT`, `closed_items()` and `board.py
> archive`; the v2 line's writers, `item_line()`, `decided_line()`, `edit_line()`, `item_problem()` and
> `canonical_item()`, and with them the refusal of a field's name in a text, context, answer, detail value or reply
> and of an answer ending `(by …)`; `add --under`; and the edits' `--line` and `--expect`. **What a caller
> changes:** `needs_you()`, `covers()`, `sweep()`, `board_problems()`, `board_people()`, `answered_by()`,
> `people_problems()` and `answered_by_problems()` take a `Board`, and the sweep's board is `(origin_url, basename,
> board)`, read whole, its `to_close` ids; `item_record()` loses `line`, gains `id`, `path`, `added`, `context`
> and `closed`, and its `text` is the item's words (its `doer`, v2.8's, is unchanged);
> `version_problem()` takes a `Board` and judges its
> `major` against `BOARD_MAJOR` (3), the board's own, read from every line of `README.md` (`board_major()`; the
> ledger's `FORMAT_MAJOR` is not changed here); `parts_problems()`, `decide_lift()` and `closes()` take an item
> file's text, and `parts_problems()` prefixes a shared check's fault `item:` where it wrote `line:`; `BOARD_PATH` and `BOARD_ARCHIVE_PATH` are `BOARD_V2_PATH` and `BOARD_V2_ARCHIVE_PATH`, beside
> `BOARD_DIR`; a subject carries the id; an `ls` lists subdirectories, so a caller's `ls` that lists files alone
> reads a v3 board's archive as empty; and `lift_pr_verdict()` sends a lift on a v2 board to review. **The board's
> order** for ties is a v2 board's line order and a v3 board's ids descending, newest first (by `Added` date, at
> random within one day), so tied items can change order when a board is split. **`Doer`** is a header field of the
> item file on an `act`, naming who should do its step (*The item file*), which `add --doer` writes. The split carries every
> field the v2 reader reads into the header field of the same name. v2.4's "no board action removes one" no longer holds:
> `done`, a closing `decide` and `split` remove files. A v2.x module meets a v3 repo as the stub, which declares
> `Ledgerboard: 3`: a reader that calls `version_problem()` refuses it, a writer refuses it unread, and a reader
> that checks nothing reads an empty board, so a repo splits its board only once every reader of it runs v3.0.
> Within v3.x the same holds for a field: a later minor's field is faulted by an older v3 gate, so **a consumer
> writes a new field only once every reader of the board runs that release**. `Ledgerboard: 3` on a ledger means
> nothing new here; the ledger's v3.0 changes are its own paragraph (TD-078).

*Versions*' opening lines (round 4's F56) change too. "A ledger or board may declare its major version on a
preamble line, `Ledgerboard: 1`; none means 1." becomes:

> A ledger or board may declare its major version on a preamble line, `Ledgerboard: 1`; none means 1 for a ledger,
> and 2 for a board file (v3.0: a board's v1 and v2 are one format).

and after "A v2 ledger declares it in its `README.md`, which `load()` puts first." add:

> A v3 board declares it in its `README.md`, on any line outside an HTML comment (`board_major()`); a README that
> declares none reads as 3, and is named (*Reading a board*).

**13. *Appendix: grammar*, *The item file (v3.0)***, with the paragraph on the field order as a production — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, text 13 (2026-11-13 split).

**14. The rest of *The board*** — its opening and its B1 and B2 bullets (*Notes on a hide* to *The decide lift*, the shared *Parts:*, *Doer:* and *Trailing fields* bullets among them) moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, text 14 (2026-11-13 split); the two bullets below stay:

- *Versions*' past paragraphs (v2.3's to v2.8's) stand as written: each says what that release shipped, and the
  names it gives (`item_line()`, `item_problem()`, `canonical_item()`, `archive_closed()`, `edit_line()`) were that
  release's. Text 12 says what v3.0 removed. No build: nothing lands.
- *Appendix: grammar*, *The open item line*: its opening sentence's "a line `item_problem()` gives None for" gains
  "(v2.x; v3.0 removes `item_problem()`)". B5.

**The search** — its opening and the B1 and B2 searches moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, *The search* (2026-11-13 split); B3's and B4's moved to TD-095's plan, docs/plans/TD-095-board-writer-gate.md, *The search* (2026-11-14 split); B5's stays:

- **B5** (texts 1, 9's swap, 8's *Migration*, 10's `split`, 12, 14's writer items) runs the full search: all of `SPEC.md`, for
  every name above (`item_line`, `decided_line`, `edit_line`, `item_problem`, `canonical_item`, `archive_closed`,
  `archive_subject`, `ARCHIVE_AT`, `closed_items`, `BOARD_PATH`, `BOARD_ARCHIVE_PATH`, `--line`, `--expect`,
  `--under`), each found only in a *Versions* paragraph, a v2-tagged sentence or text 12.

## Fixtures

All invented names (`pat`, `sam.lee`, `acme/widgets`, `ops`, `host-a`, sessions `w-9`, `lb-x`).

- **`fixtures/item/`** — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, *Fixtures* (2026-11-13 split).
- **`fixtures/board/<case>.v3/`** for each v2 case `fixtures/board/` holds when B5 is built (today `basic`,
  `answers`, `doer`, `hidden`, `people`, `lifts_parts` and `shared_part_left_open`; round 8's F122: `doer` is
  v2.8's, so `doer.v3/` is among them), and TD-092's `twins_across` (B2: a case directory, `board.md` beside
  `board_archive.md`, TD-092's F209), an open line on the board and its closed twin in the archive: its split
  directory, `fixtures/board/twins_across.v3/` beside the case's directory, and TD-092's `reply_ref` and `closed_words` (B2, dated),
  which split (TD-092's F217, F224; `closed_words`' `Closed: 2026-01-10 lifted.` carried as round 9's F160 says,
  written `**Closed:** 2026-01-10` with `lifted.` in the heading). TD-092's `undated_twins` and `words_prefix` (B2) hold undated
  lines, which the split refuses (D11), so they are read-only cases with no `.v3/` (TD-092's F213), as is TD-092's
  `closed_no_day` (B2), a closed line whose `Closed:` date is no day (TD-092's F231). **Each of the seven v2 cases splits** under the
  ruling (round 9's F147, checked against D11's kept refusals: every line dated with a day, no closed line without
  a readable `Closed:` date, no two items of one id, no preamble line after the first item, no colonless `Due
  <day>.` and no `Due` v2 reads inside another span, round 9's F164, F165): `basic` (its `fyi` with `Due: 2026-01-20.` and its `Due: 2026-1-9.` carried, its
  twins one closed item), `hidden` (`Due: 2026-1-20.` carried), `doer` (its `decide` with `Doer: team ops.`, its
  `team  ops` and its unreadable values carried, `Doer: acme .` written with its period, D11), `lifts_parts` (an
  `act` with `Answers:` and an `fyi` with `Parts:` carried), `answers`, `people` and `shared_part_left_open`
  (nothing to carry). So each gets a `.v3/` (the notes a carried shape gives are pinned by `board_split`'s cases,
  below). A new runner kind, `board_v3_case` (B5),
  beside `v2_case`: `split_board()` of the case's text gives the directory file for file, and `load_board()` of it
  gives the case's expected JSON, the JSON the v2 read gives (`covers`, the records, and `needs_you`), compared as
  D6's *Comparing two reads* says (records keyed by `id` without `path` and `line`; `covers` as a list sorted by id;
  `needs_you`'s **tie groups** as sets, the groups in order), since a v2 board's order is its lines' and its split's
  is id descending. The v2 cases' JSONs at B1 and B2, and `twins_across`'s read — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, *Fixtures*, `fixtures/board/` (2026-11-13 split).
- **`fixtures/board_dir/`** — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, *Fixtures* (2026-11-13 split).
- **`fixtures/board_split/<case>/`** (a new kind, `board_split_case`: `board.md`, optional `archive.md`,
  `expected.json` holding the files or the refusal, and `split_board_notes()`): `twins` (an open and a closed line
  of one key, on the board and across board and archive, each one closed item, its fields and body the closed line's
  although the open twin's detail block differs); `sections` (the `## Needs the user` and `## In-flight` headings:
  an earlier `## ` heading kept and only the one nearest the first item dropped; the README's prose kept; its links:
  an inline relative link, an image, a reference definition, a `#anchor`, an `https:` and a `mailto:` link, a
  `/rooted` path and a link inside a code span, only the relative three given `../`; its notes listed);
  `prose_after_items` (round 8's F118: `## In-flight` holding `- (none)`, and a note line between two items, both
  carried to `README.md`'s end in order with the `In-flight` heading, a later heading with nothing under it dropped,
  the notes naming `In-flight`); `hand_line`
  (words a hand edit left outside the fields carried into the heading, its final period kept: words after the `Due`
  date, `Due: 2026-11-08. also ping sam.`, and after a `Hide until` date, each joined to the text by one space as
  `item_words()` gives them (F80); a bold head kept as written, a `Closed: D — lifted.` written `— lifted`, a
  `Closed: 2026-01-10 lifted.` written `**Closed:** 2026-01-10` with `lifted.` in the heading (round 9's F160), a
  `Context:` losing its final period); `decided_by` (a
  `Decided:` with and without `(by …)` rewritten); `persisted_key` (the id's digits equal to the hash ShiftLead's
  `key()` gives, for a column-0 line, an indented line and a `[x]` line). **Carried and named** (round 9's F147, the
  ruling: each split, its file read back as the v2 line, and `split_board_notes()` listing the rule-14 finding):
  `doer_spacing` (`Doer: team  ops.`), `doer_not_act` (a `decide` carrying `Doer: acme.`, one carrying `Doer: team
  ops.`), `doer_period` (`Doer: acme .`, written with its period, read as no doer by both), `parts_not_decide` (an
  `act` carrying `Parts: TD-2.`, F128), `answers_on_act` (an `act` carrying `Answers: done | not yet.`, F154),
  `fyi_due` (an `fyi` carrying `Due: 2026-11-20.`, one `Due: 3/4.` and one the colonless `Due 2026-11-20.`, F138,
  F140, F146). **Carried, named by no rule** (round 9's F163: each split, its file read back as the v2 line,
  `split_board_notes()` listing nothing for it): `bad_due_shape` (an `act` carrying `Due: 3/4.`, one carrying `Due
  3/4.`, one `Due: 2026-1-9.`, each written `**Due:** <raw>` and read as `due_error` by both, F130; and `Fix Due 3/4
  soon. Context: TD-1. Due: 2026-02-30.`, its `Due` span `Due 3/4` and `Due: 2026-02-30.` in the heading, F171),
  `context_due_words` (an `act` whose Context holds `Due 3/4` and whose own `Due: 2026-11-20.` v2 reads: the
  Context carried as written, F164), `doer_empty` (an `act` carrying `Doer: . Due: 2026-11-20.` and one `Doer: Due:
  2026-11-20.`: no `Doer` written, the words in the heading, F172). Refused: `undated`, `undated_no_day` (an item
  dated `2026-02-30`, F165), `duplicate_open`, `two_closed`, `two_indents` (one text
  at two indents, one id), `people_after_items` (a `People:` line after the first item, F118), `already_v3`,
  `closed_undated` (a `[x]` line with no readable `Closed:` date, and one with `Closed: 2026-02-30 — x.`, F160),
  `due_no_colon` (an `act` carrying `Due 2026-11-05.`, which v3 would read as a day) and `due_in_context` (an `act`
  whose Context holds `Due 3/4` and which has no other `Due`, so v2 reads that one, F164).
- **`fixtures/board_writer/`** and **`fixtures/verdict/`** (B3's and B4's) — moved to TD-095's plan, docs/plans/TD-095-board-writer-gate.md,
  *Fixtures* (2026-11-14 split); B5's `fixtures/board_writer/` cases stay here: `split` and `split_exists` (exit 1),
  and `write_v2_refused`'s message gaining *split first*.
- **`fixtures/sweep/`, `fixtures/lift/`, `fixtures/grammar/` and `fixtures/edit/`'s groups** (B1's and B2's, with the B5 steps of the sweep's rerun and of the lift groups) — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, *Fixtures* (2026-11-13 split).
- **Retired**: `fixtures/archive/` (with `archive_closed()`), and the `edit/` groups above (B5).
- **The runner** (`fixtures/run.py`, every build's kinds) — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, *Fixtures* (2026-11-13 split).

**Unit tests** — the opening and the B1 and B2 bullets moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, *Fixtures* (2026-11-13 split); B3's and B4's moved to TD-095's plan, docs/plans/TD-095-board-writer-gate.md, *Fixtures* (2026-11-14 split); B5's stays:
- **B5**: `tests/test_item_gate.py`'s v2 properties go with `item_line()`, `decided_line()`, `edit_line()` and
  `canonical_item()`; `tests/test_ledgerboard.py`'s tests of the removed writers (`item_line()`, `decided_line()`,
  `edit_line()`, among them `test_every_edit_keeps_the_item_key`) go or move to item files, and its `sweep()` tests
  pass `(origin_url, basename, board)`; the property test that `split_board()` then `load_board()` gives a board's
  items back runs over the fixture boards that split, every `fixtures/board/` case with a `.v3/` (F147; not `undated_twins`
  or `words_prefix`, TD-092's F213, nor `closed_no_day`, TD-092's F231), and
  each accepted `board_split` case, never a refused one.
- `tests/test_ledger_writer.py` and `tests/test_release.py` change in no build.

## The builds

**The builds' opening** (each filed `Part of: TD-070`, B1's preconditions, no release between B1 and B5, the shims, what a record shows, each build's search) — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, *The builds* (2026-11-13 split).

**The reader seam, function by function** — its opening, the rows whose build is B1 or B2 and the sentence on `fixtures/run.py` moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, *The reader table* (2026-11-13 split); the rows whose build is B3 or B4 moved to TD-095's plan, docs/plans/TD-095-board-writer-gate.md, *The builds* (2026-11-14 split); the rows below are the rest.

| function | reads today | a v3 item's source | build |
|---|---|---|---|
| `closed_items()` | a v2 board's text | none | private `_closed_lines()` at B5 (F125) |
| `item_notes()`, `due_tag()`, `_answered_within()` | fields only | the same fields | none |
| `_item_text()` | `.text`, or a line | none: callers read fields | gone B5 |
| `_gate_body()` | an item's text (for `_item_gate()`, `item_problem()`, `board_problems()`, `_sweep_context()`, `parts_problems()`) | none: its callers read `context` (F133) | gone B5 |

**B1, the item file**, and **B2, reading** — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, *The builds* (2026-11-13 split).

**B3, the writer**, and **B4, the merge gate's verdicts** — moved to TD-095's plan, docs/plans/TD-095-board-writer-gate.md, *The builds* (2026-11-14 split).

**B5, migration and the release's removals.** D11, D12. Location: `ledgerboard/__init__.py` (`split_board()`,
refusing only by the ruling's two grounds (F147), `board_stub()`, `split_board_notes(files)`; `item_line()`, `decided_line()`, `edit_line()`, `item_problem()`,
`canonical_item()`, `archive_closed()`, `archive_subject()`, `ARCHIVE_AT` removed, `closed_items()` removed from
the public names and kept private as `_closed_lines()` for `parse_board()`'s within-file twin set, its one caller
left once `board_problems()`' v2-text form, `archive_closed()` and `item_line()`'s read-back go (round 8's F125),
`_lf_lines()` kept for `parse_item()` and `edit_item()` (round 9's F166), and B1's and
B2's shims: `item_record()`'s `line`, `subject()`'s v2 form, the readers' v2-text and v2-line arguments,
`BoardItem.text`, today's `_item_text()` and `_item_gate()`'s string form (D4's *`words` and `text`*, their callers
gone; `words` keeps its name); `parse_board()` filling no `text`; the ledger's `FORMAT_MAJOR` untouched),
`ledgerboard/board.py` (`split`), `SPEC.md` (text 1, 9's swap — v2's *Edits* removed and `## Edits (v3.0)` renamed `## Edits` — 8's *Migration* and its
*Reading a board*'s "and no `line`", 2's words B2 left out, 13's retitle of *The open item line (v2.3)* B1 left out (TD-092's round 6's F253), 10's `split` and "(*split first*)", 12, 14's writer
items),
`fixtures/board_split/`, `fixtures/board/<case>.v3/`, `fixtures/board_writer/`
(`split`, `split_exists`, and `write_v2_refused`'s message gaining *split first*), `fixtures/run.py` (`board_split_case`, `board_v3_case` with its tie groups compared as
sets; `archive_case` and the retired `edit_cases` groups removed; `lift_cases`' `close`, `closes`, `item_lines` and
`item_problems` groups over item files and `sweep_cases`' rerun over each v2 board's split, F150), `fixtures/lift/`
(those groups, regenerated), `fixtures/archive/` and the retired
`fixtures/edit/` groups, `tests/` (B5's bullet under *Unit tests*, F149). **Records:** `item_record()` loses `line`; every expected JSON holding a record
regenerates: `fixtures/board/*.json`, `fixtures/board_dir/*/expected.json`, and `fixtures/board_writer/`'s `list`,
`list_v2` and `list_stub`. Done when: the precheck is green, every fixture passes, *The search*'s full search of
`SPEC.md` finds no removed name outside the places it allows, and `board.py split` of this repo's own board, run on
a scratch copy, reads back (its `## In-flight` and `- (none)` carried to `README.md`, F118).

Order: B1, then B2, then B3 and B4 (either order), then B5; TD-091 (TD-078's B4, `Blocked by` TD-070) follows B5
(round 9's F142). Then v3.0's release with TD-078's half (Paul's), this repo's own split, and each consumer's entry
(agent-cadence's first).

## Not in this design

The ledger's own v3.0 removals (`Waits`, `Taken by`, the old decision form, a header `Resolved`, `migrate`) and the
archived entry's writer route are TD-078's. When v3.0 is cut, and what else it carries, is Paul's.

# TD-070: the board as a directory, one file per item, for v3.0

**Status:** Scope draft, 2026-11-11 (session lb-designer). It waits on Paul's answer to the scope (the board's
decide item, TD-070's `decision (paul)`), before it gains its exact `SPEC.md` text and fixtures and before any
review round: his layer says agree the shape before the rounds. Class, once the scope stands: **wide** (a new major
of a vendored, published format, read and written by both consumers; cap 6 rounds, cadence.md §4.8).

**Entry:** [TD-070](../ledger/TD-070.md). **Source:** the entry's Why and Fix; [target design](target-design.md)
§7.1's v3.0 row (amended 2026-11-11 to name this design); `SPEC.md` *The board*, *Edits*, *The board writer*, *The
merge gate's verdicts*, *The ledger as a directory* (the precedent).

## The problem

A board is one Markdown file, and every new item is written at one place in it: `board.py add` puts it above the
first item of its section (`plan_add()`). Two PRs that each add an item always conflict, and GitHub's merge runs
no merge driver, so each collision costs a rebase and a full precheck. No layout inside one file avoids it: two
inserts at one anchor conflict wherever the anchor is. agent-cadence's `board_edit.py replay` (its TD-248) does
the rebase's hand edit, not the rebase.

The conflicts are real but not the case for a major. Counted on 2026-11-11 from one machine's session transcripts
since 2026-10-12: about 140 conflict events on v1 ledger files, 3 on v2 ledger directories, 7 on boards (a floor).
The case is **the item's shape**. A `decide` item is a line of one to two kilobytes (this repo's board holds lines
of 830 to 1,080 characters), with a detail block and a life of its own: open, decided, closed, archived. That is an
entry's shape, and the single line carries costs an entry does not:

- **Its identity is its text.** The item key is the line with some fields cut out. Consumers persist it, so what
  the key is for a line is part of the format, and every new field has had to decide whether it is in the key
  (`Hide until:` in v2.3, `Parts:`, `Lifts:`, `Doer:`).
- **Fields live inside prose.** A Context ends where the next field name begins, so the writer refuses any text,
  answer or detail value that holds a field name, and every new field (`Doer:` in TD-065) widens that refusal and
  can re-read an old line.
- **Two copies of one item are the merge rule.** An open and a closed line with one key mean "closed: a merge kept
  both sides", and `archive_closed()` carries twins, its refusals and the `ARCHIVE_AT` threshold. This repo's
  board holds 32 closed items, over three times the threshold, because archiving is a separate PR nobody owes.

## The scope, point by point

Each point is what the design will specify once you say Go; the SPEC text, the fixtures and the rounds come after.

**S1. Do it: the board becomes a directory in v3.0.** The design recommends the directory over keeping the single
file with `replay`, on the item's shape (above), not on today's conflict count. The alternative the entry names,
the single file staying, keeps every cost above for the life of v3; the design would record why, and only a count
of what `replay` still costs between now and v3.0 could argue for it. A middle way, `add` writing at a hashed place
in the file, was weighed and dropped: two inserts on neighbouring lines still conflict, and it changes nothing about
the key or the twins.

**S2. The item id: its date and a nonce, `YYYY-MM-DD-<8 hex>`.** An item's file is named by its id
(`2026-11-11-3f9a2c1d.md`), and the id replaces the item key as what an item is, for consumers and for the gate.
Weighed:
- *A counter*, as the ledger's next id: short ids, but every item written would need a take, a push to the
  counter branch, and items are written by hosts, sweeps and answers far more often than entries are filed. No.
- *A hash of the item's text*: needs no coordination, but ties the id to words, so two items with the same text
  are one id; it is the key problem again. No, except for migration (S9).
- *A date and a nonce* (recommended): no coordination, unique in practice (32 bits within one day), sorted by date
  in any listing, and short enough for a reference such as a `board:<id>` work order. The writer draws the nonce
  and refuses a name already in the directory or its archive.

**S3. An item file is a small entry, not the line.** The file holds the item as header fields, then its detail
block as the body, then its replies as Log lines, in the ledger entry's grammar:

```
## Say Go to v3.0's board scope

**Kind:** decide
**Added:** 2026-11-11
**Session:** lb-designer on host-a
**Context:** TD-070 decision (pat)
**Due:** 2026-11-18
**Answers:** Go (default) — the scope stands | Change — reply with what changes
**Lifts:** Go

- **Context:** …
- **Question:** …
- **Recommended:** Go — …

**Log:**
- 2026-11-12: pat: does S4 cover the archive's months?
```

`Decided:`, `Hide until:`, `Parts:`, `Doer:` and `Closed:` are header fields like the rest. This ends the field-name
refusals (a field is a line, so prose can hold any words), the key, and reading a Context's end; an edit rewrites one
line of a file. The alternative is to keep today's line as the file's first line with its detail block under it:
the parsers and edits stay as they are, at the price of keeping every cost of the line except the conflicts. The
design recommends the entry form on long-term merit; it is the larger build, and the larger change for both
consumers' readers.

**S4. The layout.** `docs/user_attention/` in place of `docs/user_attention.md` (the name people and `cadence.md`
already use):

```
docs/user_attention/
  README.md                  # the opening prose, then the preamble: Ledgerboard: 3, People:, Answered by:, stamps
  2026-11-11-3f9a2c1d.md     # one open item
  archive/
    2026-11/
      2026-10-30-0b7e41aa.md # a closed item, filed under the month it closed
```

- **Closing archives.** `done` (and a `decide` that closes) moves the file into `archive/<YYYY-MM>/` of its
  `Closed:` date in the same write, as the ledger's `archive` does. `archive_closed()`, `ARCHIVE_AT`, its refusals
  and the open-and-closed twin rule go.
- **Months under the archive** keep a forge read small: the gate sweep needs closed items only within its windows
  (`reask_days`, 30 by default), so it reads the last two months' directories, never the whole archive.
- **No sections.** `## Needs the user` and `## In-flight` become nothing: what an item is for is its kind (`watch`
  for a session's own re-check), and order is the reader's (`needs_you()` already sorts by class and date, not by
  place). The alternative is a `**Section:**` field; the design would add it only if a consumer reads sections, which
  the design's read of both consumers settles.

**S5. Reading: one call, either major.** `load_board(path, ls, read)`, the ledger's `load()` pattern with the
caller doing the I/O, gives the same parsed items for a v2 file and a v3 directory, so `needs_you()`, `covers()`,
`sweep()` and the verdicts take items, not one text. v3.x reads a v2 board, as v2 reads a v1 ledger, so a consumer
can vendor v3.0 before it migrates; the writers write v3 only.

**S6. The writers and the edits.** The five edits and `add` name an item by `--id`, and `--line`/`--expect` go
(an id cannot move, so nothing need be re-read). `board_problems(board, old)` judges a file whose id `old` lacks,
once, as today it judges a new key. `edit_action()` and the commit subjects keep their shape and add the id.

**S7. The merge gate's verdicts.** `BOARD_PATH` and `BOARD_ARCHIVE_PATH` become `BOARD_DIR`; a tree is read as a
directory. `lift_pr_verdict()`'s condition (b), "one item line changed in place", becomes one item file changed,
or moved to the archive when the answer closes it, byte-equal to the writer's output. `tripwire()` and
`uncovered_decisions()` read the board's items through `load_board()`. Each consumer's carve-outs that judge a
commit by its touching the board alone then read "only files under the board's directory": that is a line in each
consumer's vendor entry (S10), never code here.

**S8. What a person reads.** There is no single file to open. `board.py show` prints the board as one Markdown text,
in `needs_you()`'s order, from the directory; a consumer's own view reads items through `load_board()`. No rendered
file is stored: a stored view is one file every write touches, which is the conflict again.

**S9. Migration and its place in v3.0.** `split_board(board, archive)` gives the v3 files of a v2 board and its
archive: each item's id is its `Added` date and the first 8 hex of the SHA-256 of its v2 key, so every consumer
can map a key it persisted to the same id (`key_id(key)`, kept through v3.x); twins become one closed item; the
preamble and prose become `README.md`. It runs in each consumer's v3.0 vendor PR beside v3.0's other removals
(target design §7.1's v3.0 row), and refuses a result that does not read back the same items.

**S10. The consumers.** Both change in their v3.0 vendor PR, filed through each repo's question seat once the
release is cut: agent-cadence (`board_edit.py` over the new writer, `replay` retired, its sweep's and hook's board
reads, the carve-outs) and ShiftLead (its persisted keys mapped through `key_id()`, its forge read of a directory,
its `board:<key>` orders becoming `board:<id>`).

## The builds this scope gives (filed only on your go after the rounds)

A sketch, for the scope's size; the rounds fix the cut:
1. **B1**, the item file: its grammar, `parse_item()`, `item_file()` (the writer's form), the id (S2, S3).
2. **B2**, `load_board()` over either major, and the readers taking items (S5).
3. **B3**, the writer: `add`, the five edits, closing into the archive, `show` (S4, S6, S8).
4. **B4**, the merge gate's verdicts over a directory (S7).
5. **B5**, `split_board()` and `key_id()` (S9), then the grammar appendix's productions for the item file.

## Not in this design

The ledger's own v3.0 removals (`Waits`, `Taken by`, the old decision form, a header `Resolved`, `migrate`) are
target design §7.1's and another entry's. When v3.0 is cut, and what else it carries, is Paul's.

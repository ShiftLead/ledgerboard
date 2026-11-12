# TD-070: the board as a directory, one file per item, for v3.0

**Status:** Draft 7, 2026-11-11 (session lb-designer). Paul answered **Go** to the scope as drafted (S1–S10,
TD-070's `decision (paul)`, 2026-11-11): every recommendation in it stands, and that Go is his only answer in this
design. Draft 1 turned the scope into the full design: its decisions, the exact `SPEC.md` text, the fixtures and the
builds. Rounds: six ran, ending at the cap (round 6's design review still raised build-changing findings, F73–F76,
now applied; no design review has read them). Build-changing per design review 12, 4, 3, 5, 3, 4; fact-checks 2, 2,
1, 0, 0, 0. Recurring topics: tie and list order (F14, F30, F32, F45), the build-by-build shims (F23, F33, F44, F53,
F55), Doer and TD-065 (F18, F19, F29, F38, F46, F58, F68), each judged ended by round 6's design review after round
5's cuts. Each round's fixes applied, with the author's (the designer session's) rulings where the findings offered a
choice (round 1: the tie order, `Doer:`, the releases, the sweep's reads, the stub; round 2: v2.8's content, ties at
the split, the board's own major, the records through the builds, the duplicate-id tie-break; round 3: `Doer:` as
this design's own field, the consumers' call sites, the v2 writers' read-backs, the order and the comparison of
records, the major of an undeclared v2 board; round 4: the records' JSON shapes, a v3 item's `raw` and
`show_board()`'s place; round 5: `BoardItem.words` beside a v2 item's `text` from B2 to B5, replacing round 4's one
accessor and its grep check; `Doer:`'s own value reader and TD-065 decided before B1, replacing round 4's delta
rule; one numbered list of the read's problems; `show_board()`'s bytes; round 6: named value readers for
`Decided`, `Closed` and `Answers`, `split` without `--to`, an unreadable `Kind`, `Hide until`, `Parts` or `Doer`
read as absent).
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
- **The precedent** is v2.0's ledger (*The ledger as a directory*): `load(path, ls, read)` with the caller doing
  the I/O and a v1 file read by the same call, `README.md` holding the opening prose and the preamble, archiving as
  a file move, `v2_problems()` for what a hand edit can do, and `split()` refusing a result that does not read back.
- **The entry grammar** (*Ledger entries and their edits*): a `## ` heading, a header block of `**Name:** value`
  lines read by `FIELD_RE` and compared by `field_key()`, a body cut into sections by bold leads, and a Log that is
  always the body's last section.
- **What an item means does not change.** Kinds, `Due:`, `Hide until:`, answers and their consequences, `Lifts:`,
  `Parts:`, `Decided:` and who gave it, *What needs the person*'s classes, *The decide lift*, *Closing on the
  answer*, *The gate sweep*'s rules and the verdicts' conditions all stand; this design moves where an item lives
  and how it is named, not what it says.
- **A new major** reads what the old major wrote where a consumer needs it to (v2 read v1 ledgers), and says in
  *Versions* what it reads differently and what it no longer does.

## Options weighed

**Whether to do it (S1).** (a) The directory. (b) The single file, with `replay` for the rebase. (c) The file, with
`add` writing at a hashed place. (c) changes nothing about the key or the twins, and two inserts on neighbouring
lines still conflict. (b) keeps every cost above for the life of v3; only a count of what `replay` still costs
could argue for it, and the case is the shape, not the count. **(a).**

**The id (S2).** (a) A counter, as the ledger's next id: every item written would need a take and a push, and items
are written by hosts, sweeps and answers far more often than entries are filed. (b) A hash of the text: no
coordination, but two items with the same words are one id, which is the key again. (c) The date and a nonce: no
coordination, unique in practice, sorted by date in any listing, short enough for a `board:<id>` reference.
**(c)**; (b) only gives a migrated v2 item its id (D11).

**The item's form (S3).** (a) An entry: heading, header fields, body, Log. (b) Today's line as the file's first
line with its detail block under it. (b) keeps the parsers and edits, and every cost of the line but the conflicts.
**(a)**, the larger build, on long-term merit.

**`Decided:` in a field.** (a) The v2 form, `<label> (by <p>) (<date>)`. (b) `<date>[ by <p>] — <label>`. (a) keeps
the refusal of an answer ending `(by …)`, a field-in-prose cost of the kind S3 ends. With the date and the person
first, the label runs to the line's end and holds any words. **(b)**, and `Closed:` the same way, `<date>[ — <why>]`.

**Sections (S4).** (a) No sections. (b) A `**Section:**` field. The scope left it to what the consumers read
(D5): neither reads a section for its meaning, and the one audit that reads a heading stands for a rule a kind
states. **(a).**

**Listing the archive's months.** (a) `ls` lists subdirectories too, a name with a trailing `/`. (b) A flat
archive, the month in the file's name. (c) The caller names the months. (b) drops S4's point, a forge read of a
month and not the whole archive. (c) makes every caller know what only a listing tells. **(a)**: a file system and
`git ls-tree` both list subdirectories already; `load()` ignores the new names.

**What is left at `docs/user_attention.md`.** (a) Nothing. (b) A stub declaring `Ledgerboard: 3` and naming the
directory. With (a), a v2.x reader meets a missing file and reads an empty board, which for a board says "nothing
needs you" (v2.0's ledger took that cost: a missing ledger reads as no work, which a reader notices), and a v2.x
`board.py add` given the old path writes a fresh v2 board there, forking the board. With (b), a v2.x reader that
checks the version refuses the board and says to vendor a newer release, a v2.x writer refuses it unread (*The
board writer*: a file that declares a newer major), and a caller configured with the old path reads the directory
through it (D6). **(b)**, a file no write touches after the split (round 1 kept it).

## Decisions

**D1. The board is a directory in v3.0 (S1).** A v3 board is a directory of item files; a v3 writer writes nothing
else. v3.x still reads a v2 board (D6).

**D2. The layout (S4).**

```
docs/user_attention/
  README.md                    # the opening prose, then the preamble: Ledgerboard: 3, People:, Answered by:, stamps
  2026-11-11-3f9a2c1d.md       # one open item
  archive/
    2026-11/
      2026-10-30-0b7e41aa.md   # a closed item, filed under the month of its Closed: date
docs/user_attention.md         # the stub (D11): Ledgerboard: 3 and the directory's name
```

An open item is `<id>.md` directly in the directory; a closed one is `archive/<YYYY-MM>/<id>.md`, the month of its
`Closed:` date (`item_path(id, closed=None)`). Every preamble line is read from `README.md` alone. Closing an item
moves its file in the same write (`done`, and a `decide` that closes); nothing else moves one, and no file is
deleted. `archive_closed()`, `archive_subject()`, `ARCHIVE_AT`, `closed_items()` and `board.py archive` go.

**README's stamps stay in it** (`Swept:`, `Swept-deep:`, the consumer's dated preamble lines): which stamps a
consumer writes is the consumer's, and a stamp is preamble. Every sweep that stamps rewrites `README.md`, so two
stamps still conflict there. That is a known limit of v3.0, not removed by it: a stamp is one line a sweep writes,
not an item, and moving stamps out (a file per stamp, say) is the consumer's choice, open to it later.

**D3. The item id (S2).** `YYYY-MM-DD-<8 hex>`: the item's `Added` date, a hyphen, eight lower-case hex digits
(`ITEM_ID_RE`, `^\d{4}-\d{2}-\d{2}-[0-9a-f]{8}$`, the date a real day; `item_id(added, nonce)` formats and refuses
anything else). The module draws nothing: `board.py add` draws the nonce (`secrets.token_hex(4)`) and draws again,
up to 8 times, while the name is held open or in any archive month. `add --id <id>` takes a caller's id instead (a
service writer that keys its appends on an event, cadence §4.4), refused when malformed, when its date is not the
item's `Added`, or when held. So `--id` is idempotent within a day and not across days, as intended: an id names one
day's add, a retry of a written add is refused as held (which a caller reads as done), and a caller that retries on
a later day passes `--today` the id's date or draws a new id. Two changes that add one id conflict as two files at
one path, which is the safe failure; 32 bits within one day make it rare. An id never changes: a retitle, an edit
and a close keep it.

**D4. The item file (S3).** A small entry, in the grammar of *Ledger entries and their edits*:

```
## Say Go to v3.0's board scope

**Kind:** decide
**Added:** 2026-11-11
**Session:** lb-designer on host-a
**Context:** TD-070 decision (pat)
**Due:** 2026-11-18
**Answers:** Go (default) — the scope stands | Change — reply with what changes
**Decided:** 2026-11-12 by pat — Go
**Closed:** 2026-11-12 — lifted

- **Context:** …
- **Question:** …
- **Recommended:** Go — …

**Log:**
- 2026-11-12: pat: does S4 cover the archive's months?
```

- **The heading** `## <text>` is the item's words (`BoardItem.words`), one line, any words; the writer trims it and
  adds no period. A bold run in it is the item's bold head (*The bold head*, read from the heading).
- **The header block**, read by `FIELD_RE` and `field_key()` as an entry's: a name compared by `field_key()`, which
  folds case and reads `-`, `_` and runs of whitespace as one space (`**hide-until:**` is `Hide until`); a value's
  end whitespace dropped; the first of a name winning. The fields and their writing order: `Kind`, `Added`,
  `Session`, `Context`, `Parts`, `Doer`, `Due`, `Hide until`, `Answers`, `Lifts`, `Decided`, `Closed`. `Added` and
  `Context` are always written; `Kind` is absent for the kindless to-do; `Session` is `<name>` or `<name> on
  <host>`, absent for `n/a` and on a decided file (`decided_file()`, the v2 `(person)` head). `Parts` is `TD-15,
  TD-16`; `Answers` and `Lifts` are a v2 line's values without the final period, `\|` still a literal bar.
  `Decided` is `<date>[ by <person>] — <label>`; `Closed` is `<date>[ — <why>]`.
- **`Doer`** is a v3 header field, defined wholly here: on an `act` only, who should do its step, `<repo>` (a repo
  name whose last part does not end in `.`, text 13's `doer-repo` and `doer-part`) or `team <team>` (`<team>` a
  person's name; `team` alone names the repo `team`). Its reader is `parse_doer_value(value)` (round 5's F68), new
  in B1 whatever TD-065 does: it reads a bare value, as the header field holds it (no final period, no line around
  it), and gives `("repo" | "team", name, value)` or None for a value outside the form. It reads a team as TD-065's
  reader does (round 6's F79): `team`, a run of spaces or tabs, and a person's name, so `team  ops` reads as the
  team `ops`, its `value` as written; `item_file_problem()` and `board_dir_problems()` (rule 14) fault any spelling
  but one space, and the writer writes one. `BoardItem.doer` is that
  tuple for a v3 item, and `item_record()`'s `doer` a dict of it (below), or None. TD-065's `parse_doer(text)`, if
  it ships, stays a v2-line function (it finds ` Doer:` on a line and reads to the field's final period), which the
  v2 half of `load_board()` uses for a v2 item; neither reader calls the other. Whether TD-065 ships is decided
  before B1 starts (D12).
- **A value is a whole line**, so it holds any words, field names among them: the field-name refusals end, and so
  does reading where a Context ends.
- **A header-block line that is no field** (round 3's F51) does not end the block, which runs from the heading's
  blank line to the next blank line: the line is in no field and not in `BoardItem.fields`, every edit keeps it
  byte for byte, `board_dir_problems()` names it, and `canonical_item_file()` refuses the file.
- **An unknown field is kept**: in `BoardItem.fields` (every header field as written, in order), its line kept byte
  for byte by every edit and placed after the known fields by `canonical_item_file()`, and faulted by
  `item_file_problem()` on a file the writers write. A later v3 minor that adds a field changes nothing an older v3
  reader reads of the others, but an older v3 gate (`board_problems()`) faults an item that carries it, so a consumer
  writes a new field only once every reader of the board runs that release.
- **The body** is the detail block: the lines after the header block up to the Log, leading and trailing blank lines
  dropped (`BoardItem.detail`), written by the writer at column 0. No edit touches it.
- **The Log** is the body's last section, led `**Log:**`: the item's replies, `- YYYY-MM-DD: <name>: <words>`,
  oldest first. `<name>` holds no `:` and is at most 40 characters, and `<words>` are not empty; a Log line in any
  other shape is kept and read as no reply. A reply decides nothing, as on a v2 line.
- **The value readers** (round 6's F73). `parse_item()` reads each header value as a bare value, never through a
  v2-line function: `parse_decided()`, `parse_decided_by()`, `parse_answers()`, `parse_lifts()`, `parse_parts()`,
  `parse_hide_until()` and `DUE_RE` find a field on a v2 line (after its `Due:`, by its name) and stay v2's. B1
  adds `parse_decided_value(value)`, giving `(label, date, by)` (`by` None when the value names no one) or None for a
  value outside `<date>[ by <person>] — <label>`, which fills `decided` and `decided_by`;
  `parse_closed_value(value)`, giving `(date, why)` (`why` None for a bare date) or None outside `<date>[ — <why>]`,
  which fills `closed`; and `parse_answers_value(value)`, giving the written answers split on each bar not after a
  `\`, `\|` read as a bar, each trimmed and none empty, which fills `answers`, `default` and `consequences` through
  `split_answer()` as `_raw_answers()`' readers do, and `lifts` from a `Lifts` value of the same form. `Kind` is one
  of the five, `Due` and `Hide until` a `YYYY-MM-DD` day (`date.fromisoformat()`), and `Parts` its ids
  (`entry-id`s, read with `REF_TD_RE` as `parse_parts()` reads its ids), each read from the value by `parse_item()`; `Doer` by
  `parse_doer_value()`.
- **A value not in its form** (round 3's F51, round 6's F76), for `Decided`, `Closed`, `Kind`, `Hide until`, `Parts`
  or `Doer`, is kept (in `fields`, its line byte for byte) and read as the field absent: a `Decided` or `Closed`
  with no date first, or a date that is no day, reads as no answer, or no close (the item not decided, or, outside
  `archive/`, open); a `Kind` outside the five as no kind, so the item is a to-do and shown (`Kind: banana` never
  hides an item from *What needs the person*); a `Hide until` that is no day as not hidden; a `Parts` that is not
  `entry-id`s separated by `, ` as no parts; a `Doer` outside its form as no doer. `board_dir_problems()` names the
  field (rule 14: `Decided: not <date>[ by <person>] — <label>`, `Closed: not <date>[ — <why>]`, `Kind: not one of
  decide, act, look, watch, fyi`, and so on). A `Due` that is no day stays what *The board* says it is, reported
  (`bad_due`), never read as absent. A file in `archive/` with no `Closed:` in its form is named in `problems` (D6's
  rule 9, so by `board_dir_problems()` too), and read as closed.
- **`BoardItem` gains** `id`, `path` (its path relative to the board's directory, `""` for a v2 item), `words`
  (below), `added`, `session`, `host`, `context`, `closed` (`(date, why)`, `(None, None)` for an archived file
  with no `Closed:` in its form, or None), `replies`, `doer` (B1, above), `fields`, `raw` (round 4's F54: a v2
  item's line as written, its indent included; a v3 item's file text as read, every byte) and `detail_source` (B3,
  D8: a v2 item's detail block as its file holds it, `[]` for a v3 item). `line` stays: a v2 item's 1-based line,
  0 for a v3 item, read by nothing but v2 code (*The board's order*, D6, no longer reads it). `text` keeps its
  meaning until B5 removes it (below). **`item_record()`** changes in three builds, and only there (round 2's F33,
  round 3's F46): at B1 it gains `doer` (None on every v2 record unless v2.8 shipped TD-065's `Doer:`, in which case
  the key is v2.8's already and B1 leaves it, D12); at B2 it gains `id`, `path`, `added`, `context` and `closed`, and
  its `text` reads `BoardItem.words` for both majors (a v2 record's `text` was the line after its tick), keeping
  `line`; at B5 it loses `line`. *The builds* list the expected JSONs each of the three regenerates.
- **The record's keys, as JSON** (round 4's F57), for both majors; every key not named here keeps the shape it has
  today:
  - `id` — a string, `"YYYY-MM-DD-<8 hex>"`; `null` for a v2 line with no readable date (D6);
  - `path` — a string, the file's path relative to the board's directory (`"2026-11-11-3f9a2c1d.md"`,
    `"archive/2026-11/2026-10-30-0b7e41aa.md"`); `""` for a v2 item;
  - `added` — a string, `"YYYY-MM-DD"`; `null` for an item with no `Added` (D6);
  - `context` — a string, the Context's value without its final period (`"TD-070 decision (pat)"`, `"none"`);
    `null` for an item with no Context, of either major (round 5's F72: a v3 file a hand edit left without one
    among them);
  - `closed` — `{"date": "YYYY-MM-DD", "why": <string> | null}`, the why without its final period; `{"date": null,
    "why": null}` for an archived file with no `Closed:` in its form; `null` for an open item;
  - `decided` — unchanged: `{"text": <label>, "date": "YYYY-MM-DD"}` or `null`, with `decided_by` beside it a
    string or `null`, read from either major's `Decided:`;
  - `doer` — `{"kind": "repo" | "team", "name": <string>, "text": <string>}` (`text` the value as written:
    `"acme/widgets"`, `"team ops"`, the shape TD-065's design gives) or `null`;
  - `text` — a string, the item's words, `BoardItem.words` (B2); `line` — an integer, until B5.
- **A v2 item's `fields`** (round 4's F63) are the header fields its split file carries, `(name, value)` in the
  writing order (`Kind`, `Added`, `Session`, `Context`, …), each name spelled as D4's list spells it and each value
  in the file's form: `Decided` as `<date>[ by <person>] — <label>`, `Closed` as `<date>[ — <why>]`, `Context` and
  `Closed`'s why without the final period, `Session` as `<name>[ on <host>]`, `Answers` and `Lifts` without the
  final period; a field the v2 reader reads that has no file form here keeps its value as the reader gives it, under
  its name. So `split_board()` writes a v2 item's `fields` as its header block, and the two majors' `fields` of one
  item are equal.
- **A v2 item** is a `BoardItem` with every one of those fields filled by `parse_board()` from its line. The v2 half
  of `load_board()` is the v2 line reader as the last v2.x release has it, so whatever fields that reader returns
  (a `Doer:` among them, if a v2 release added one) fill the `BoardItem` fields of the same name and `split_board()`
  carries them into header fields of the same name. From it: `added` its date, `session` and `host` its head's,
  `context` its Context's value (without the final period), `closed` its `Closed:` (the why without its final
  period), `replies` its reply tails, `fields` its fields as `(name, value)` in their order, `words` its words
  (`item_words(line)`, D11), `text` (until B5) the line's text after its tick, trimmed, as today, and `raw` its line.
  The readers that judge an item of either major read the fields, never the line: `_item_gate(item)` takes a
  `BoardItem` from B2 and reads its `context` (round 4's F66; a string, a v2 line's text after its tick, is still
  read as today until B5, for `closes()` given a line), and `_sweep_context()` reads `context`; `_item_date()` reads
  `added`; `_sweep_head()` reads `words`; `item_record()`, `needs_you()`, `covers()`, `sweep()`, `board_problems()`,
  `decide_lift()` and `parts_problems()` read the fields, and `closes()` given a `BoardItem` reads its `context`,
  `lifts` and `parts` (given a string, it reads the line as today, through today's `_item_text()`, until B5). `raw`
  is read by `item_key()` and `key_id()`,
  `show_board()` (either major, D8) and `split_board()`. So a reader gives the same result for a v2 item and for its
  split file (the fixtures `board_v3_case` and the sweep's v2 board and its split, below), compared as D6's
  *Comparing two reads* says.
- **`words` and `text`, B2 to B5** (round 5's cut, R10's, which replaces round 4's one accessor, its
  `_item_text()` over `raw` and B2's grep check). `BoardItem.words` is the item's words: a v3 file's heading
  from B1, where `parse_item()` fills it, and a v2 line's `item_words()` from B2.
  `BoardItem.text` keeps the meaning it has today until B5: for a v2 item the
  line's text after its tick, trimmed (`ITEM_RE`'s or `CLOSED_ITEM_RE`'s `text` group), and for a v3 item `""`. So
  every reader that reads `text` as a line today (the v2 writers' read-backs, `closes()` given a line, and the
  verdicts' `_item_gate(it.text)` in `tripwire()`, `uncovered_decisions()` and `lift_pr_verdict()`, which read v2
  trees until B4) keeps working unchanged, because the only items it meets before it is converted or removed are
  v2 items, whose `text` has not changed. A v3 item's `text` is `""` rather than its heading because a heading may
  hold field names as words (`board_dir`'s `field_words`): a line reader given the heading would read them as
  fields, while given `""` it reads none, so a reader left unconverted shows in the fixtures as a missing Context,
  never as a wrong one. `item_record()`'s `text` reads `words` from B2. B4 moves the verdicts to `_item_gate(item)`,
  as they read v3 trees. B5 removes `BoardItem.text` with the v2 writers, `_item_gate()`'s string form and today's
  `_item_text()` (`closes()`'s reader of a line or of a `BoardItem`'s `text`; D7: `closes()` then takes an item
  file or a `BoardItem`); `words` keeps its name, and the record's key stays `text`.

**D5. No sections (S4).** Neither consumer reads a section for what an item is:
- agent-cadence reads one heading, in one audit: `scripts/check_cadence.py` `classify_direct()` passes a direct
  commit as `board-append` only when each appended line's nearest `## ` heading above starts `## Needs` (cadence
  §4.4, the service-account carve-out). Nothing in `nudge_user_attention.py`, `board_edit.py`, `list_sessions.py`
  or the hook script reads a section; no script reads `## In-flight`.
- ShiftLead writes into a section and reads none: `sessionorc/board.py` `add()` and `add_decided()` pass
  `under=NEEDS` (`"## Needs the user"`) to `plan_add()`; `workorders.board_items()`, `gatesweep.py` and the Inbox
  read items through `parse_board()`, `needs_you()` and `item_record()`, which know no section.

The `## Needs` audit stands for "a service account appends what the person must see, never a session's parked
work", which the kind states (`watch` is a session's own re-check). So no `**Section:**` field: agent-cadence's
audit reads the appended files instead (its line in *Consumers*), and `add --under` goes.

**D6. Reading (S5).** `load_board(path, ls, read, *, since=None)` gives a `Board`: `major`, `preamble`
(`README.md`'s text, or a v2 board's text before its first item), `items` (the open items), `closed` (every closed
item read, the archive's among them), each a `BoardItem` with its `id`, and `problems` (D6's last bullet, its
numbered rules).
- **A directory** is read as `README.md`, each `<id>.md` directly in it, and each month directory under `archive/`
  and its files (the order of reading changes nothing: *The board's order* below orders `items` and `closed`). A
  **month** (round 6's F74) is a directory directly under `archive/` named `YYYY-MM`, a real month (`01` to `12`).
  Nothing else is read: a file directly in `archive/`, a directory under it not so named, a subdirectory of the board
  other than `archive/`, a subdirectory of a month, and anything deeper are each named under rule 11 and not
  descended into. An
  item is closed when its file lies under `archive/`, or lies outside it and carries a `Closed:` in its form; every
  other item is open. An archived file with no `Closed:` in its form is a damaged file (rule 9 below), read as
  closed, its `closed` `(None, None)`.
- **One id in two files** (a hand edit or a merge; rule 8 below) is read once: an archived copy wins over an open
  one, and of two archived copies the later month's. (Two open copies cannot be: an open item's path is its id.) So
  an item a merge left both open and archived reads as closed, as a v2 board's twins do.
- **A v2 file** is read with its archive beside it (`<stem>_archive.md`) by the v2 line reader as the last v2.x
  release has it (D4's *A v2 item*), with one change: the twin rule reaches across the two. An open line that shares
  its id (below) with a closed line on the board or in its archive is closed, and the closed line, with its detail
  block, is the item. v2.7 read an open line on the board and its closed twin in the archive as two items, an open
  one and a closed one; reading them as one closed item is what `split_board()` writes, so the v2 read and its
  split's read give the same items (*Versions* says so). It differs from v2.7's within-one-file rule only for twins
  at different indents, which v2.7's key told apart.
- **A v2 item's id** is its line's date, a hyphen, and `key_id()` of the key ShiftLead's `key()` hashes: `item_key()`
  of `- [ ] ` and the line's text after its tick, trimmed (D11 quotes `key()`). So it reads with the id its split
  file gets, and a twin's two lines read with one id. A line with no readable date has id None.
- **One id on two open lines of a v2 board** (round 3's F49: two open lines of one text, at one indent or two, or
  two closed lines of one id) is damage a hand edit or a merge left: both lines are read, as v2.7 read them, each
  an item with that id, and `problems` names the id once, with both lines (rule 10). A by-id read or write treats the id as
  naming both: `to_close` lists it once, and a closer of the v2 board (a v2.x writer or a hand edit; no v3 writer
  writes a v2 board, D7) closes every open line of it. `split_board()` refuses the board until one line is left (D11).
- **The stub** (D11): a file that declares `Ledgerboard: 3` and holds no item is read as the directory beside it,
  its name less `.md`, so a caller configured with `docs/user_attention.md` reads the board it became.
- **`ls`** lists each subdirectory with a trailing `/` (v3.0; `load()` and `entry_path()` ignore those names).
  Every `ls` the module and the runner build does so (round 4's F65): `_dict_ls()`, the `ls` over a `{path:
  text}` map that the ledger's `split()` reads its result back through today, lists a subdirectory once, as
  `<name>/`, from B2, and is the `ls` `split_board()`'s read-back passes `load_board()` (B5); `_tree_ls()`, the
  verdicts' `ls` over a tree, does the same from B4; the runner's `fs_ls` from B2 (*The runner*). The ledger's
  reads through `_dict_ls()` and `_tree_ls()` are unchanged, since `load()` takes only `ENTRY_FILE_RE`'s names.
  `BoardItem.path` and every problem's path are relative to the board's directory (`archive/2026-11/<id>.md`).
- **`since`**, a date, leaves out the archive months before its month, neither listed nor read. `Board.closed` is
  then partial, so `since` is for a reader that judges only open items and recent closes (a nudge, `show`, a
  consumer's Inbox), never for what a board ever held: the sweep (D9), `board_problems()`'s `old`, the verdicts and
  `split_board()`'s read-back each take a board read whole.
- **The board's order** (round 3's F45), stated once: on a v3 board `items` and `closed` are each in id
  **descending** order, newest first; on a v2 board they are in line order (`closed` the board's closed lines, then
  the archive's). *What needs the person*'s ties (undated, unreadable-due and `fyi` items, and two items of one date)
  fall back to it, as does every reader that lists items. Ids descending order by `Added` date, and
  within one day at random; a v2 board's line order is whatever its writers and hand edits left (v2's `add` writes
  each item above the first of its section, a hand edit anywhere). **So a v2 board's ties follow its line order and
  a v3 board's follow id descending, and the order of tied items can change at the split**; which items need the
  person, their classes and their days do not. `board_dir`'s `ties` pins v3's order.
- **Comparing two reads** of one board in two majors (a v2 board and its split): what they share is the items,
  never the order or the place. So `split_board()`'s read-back, the runner's `board_v3_case` and the sweep's
  v2-board-beside-its-split case all compare alike: records keyed by `id`, with `path` and `line` left out (a v2
  record's `path` is `""` and its `line` a line number, a v3 record's `<id>.md` or its archive path and 0); the
  lists that `covers()`, the sweep's `to_close` and its `lifts` give, as lists sorted by id (`covers()` by the
  item's id, `to_close` its ids, `lifts` by their entry `id` and then `gate`); and `needs_you`'s rows by **tie
  group** (each run of rows with one class and one `days`), each group compared as a set and the groups in order
  (round 2's rule).
- **The readers take a `Board`:** `needs_you(board, today)`, `covers()` and `sweep()` (whose board is
  `(origin_url, basename, board)`), `board_problems(board, old)`, and the verdicts through their trees.
  `board_people()`, `answered_by()`, `people_problems()` and `answered_by_problems()` take the `Board`: on a v3
  board they read every line of `README.md` as preamble (a `- [ ]` line in it is prose, and ends no read), on a v2
  one only the lines above its first item, as now. `board.py`'s `who_answered(board, by)` takes the `Board` too
  (B3), reading its `People:` through `board_people()`. `parse_board(text)` stays as the v2 half of `load_board()`;
  `parse_item(text, path="")` reads one file.
- **The board's major** (round 2's F31) is the board's own. `BOARD_MAJOR = 3` (B2) is the newest board major the
  module reads; the ledger's `FORMAT_MAJOR` stays 2, and the ledger's reads of it (`format_major()`,
  `version_problem(text)`, `ids_held()`) stay as they are (the ledger's v3.0 is TD-078's). `board_major(text)` reads
  the `Ledgerboard: N` line from every line of a v3 board's `README.md` outside HTML comments, since every line of
  it is preamble (`format_major()` stops at the first `- [ ]` or `## TD-` line, which a README may hold as prose); a
  v2 board file's major is the `Ledgerboard: N` it declares above its first item, and **2 when it declares none**
  (round 3's F48): the board side's reader is `board_major(text, file=True)`, which reads the lines `format_major()`
  reads but gives 2 where `format_major()` gives 1. `format_major()` stays the ledger's, unchanged: its 1 is a v1
  ledger file, a format of its own, while a board's v1 and v2 are one format (v2.0 left the board unchanged,
  *Versions*), so a board file declaring nothing is read as the v2 board it is. *Versions*' "none means 1" then
  holds for a ledger, and text 12 says a board file declaring none reads as 2. `load_board()` sets `Board.major` so
  (the defaults below). `version_problem()` also takes a `Board`: given one, it names a `major` newer than
  `BOARD_MAJOR`; given text, it is the ledger's check, unchanged. A caller checks `version_problem(board)` before it
  trusts the rest. `board.py`'s `read()` checks every file it reads with `version_problem(text)`; from B3 it reads a
  board through `load_board()` and checks `version_problem(board)` instead, so a `README.md` or a stub declaring 3
  is read, and it keeps `version_problem(text)` for the ledger and the rank file. So B2's `board_dir` cases
  (`readme_v2`, `newer`) pass through `load_board()` and `version_problem(board)`; B3's writer cases over a
  directory (`add_v3`, `list_stub`, `show` and the rest) pass because `board.py` reads a board's major only so; and
  B4's verdicts read their trees through `load_board()`, which judges no major against `FORMAT_MAJOR`. Until B3
  `board.py` reads v2 boards alone, which declare no major above 2.
- **Damaged and odd input** (round 1's F15, round 5's F69) never raises. Each rule below is marked `problems`
  (`Board.problems` lists it, as `(path, problem)`: what the read skipped or could not settle) or
  `board_dir_problems() only` (the read settled it, or never read the file; only `board_dir_problems()` names it).
  `board_dir_problems()` names every rule of both marks on a v3 board, and `Board.problems` alone on a v2 one
  (D11). Each rule names its finding once. **Order** (round 4's F64): both lists are sorted by path (the path
  string's code-point order; a v2 board's problems name its file's or its archive's name), then by the rule's
  number here, then by line within the file. Text 8 copies this list as it stands.
  1. `problems`: a file `read()` gives None for: skipped, named under its path.
  2. `problems`: a file `parse_item()` reads as no item (no `## ` heading): skipped, named under its path.
  3. `problems`: a `README.md` that is missing, or declares no major: `major` 3, named under `README.md`.
  4. `problems`: a `README.md` declaring 2: `major` 2, named under `README.md`.
  5. `problems`: a file declaring `Ledgerboard: 3` that holds items (it is no stub): read as a v2 file, `major` 3,
     named under its name.
  6. `problems`: a stub whose directory is missing: an empty `Board`, named under the stub's name.
  7. `problems`: an item with no `Added`: read, its `added` None, named under its path.
  8. `problems`: one id in two files of a v3 board: read once (above), named once, under the path of the archived
     file that wins (the later month's of two archived copies).
  9. `problems`: a file under `archive/` with no `Closed:` in its form: read as closed, its `closed` `(None,
     None)`, named under its path.
  10. `problems`: one id on two open lines, or on two closed lines, of a v2 board (below): both lines read, the id
      named once, with both lines, under the board file's name when either line is on it, else the archive's.
  11. `board_dir_problems() only`: any entry the read does not take (round 6's F74): a file directly in the
      directory, or in a month, whose name is not an id and `.md` (`README.md` aside); a subdirectory of the
      directory other than `archive/`; a file directly in `archive/`; a directory under `archive/` that is not a
      month; a directory in a month. Each is named once, under its own path (a directory's with its trailing `/`),
      and not read or descended into.
  12. `board_dir_problems() only`: a header-block line that is no field (D4): kept, in no field.
  13. `board_dir_problems() only`: an `Added` that is not the id's date.
  14. `board_dir_problems() only`: a `Decided` or `Closed` not in its form (D4): read as no answer, or no close; a
      `Kind`, `Hide until`, `Parts` or `Doer` not in its form (round 6's F76): read as the field absent, a `Kind`
      outside the five as a to-do, shown; a `Doer` that reads but is spelled with more than one space, or a tab,
      after `team` (F79): read.
  15. `board_dir_problems() only`: a `Closed:` in its form on a file outside `archive/`: read as closed.
  16. `board_dir_problems() only`: an archived file in a month that is not its `Closed:` date's: read as closed.

  What is no problem: `major` is what the preamble declares (`Ledgerboard: N`), else 2 for a file and 3 for a
  directory; a v2 file with no `Ledgerboard:` line is a v2 board, `major` 2 (`board_major(text, file=True)`,
  above); a missing `path` (no file, no directory) is an empty `Board`, `major` None: the caller decides whether a
  missing board is wrong, as for a missing ledger.

**D7. The edits and the writers (S6).** `edit_item(text, action, *, to, answer, why, reply, by, today, close)` is
`edit_line()`'s five edits over an item file: snooze, due, done and decide each set one header field, reply appends
one Log line (opening `**Log:**` after the body when there is none); a closed item is refused; each is read back.
- **A field an edit adds** goes right after the last known field that precedes it in the writing order, unknown
  fields between them staying where they are, or first in the header block when no known field precedes it. A
  field it sets that is already there is rewritten in place.
- **A reply's words** are refused when empty or blank (the reader reads no reply from such a line).
- **Line endings:** an edit of a CRLF file writes the line it adds or rewrites with `\r\n` (the ending the file's
  first line uses) and keeps every other byte; `canonical_item_file()` alone normalises to `\n`.

`item_file(…)` takes `item_line()`'s arguments and `doer` (D4) and gives a file; `decided_file(…)` takes
`decided_line()`'s. Their refusals keep what still means something (a value of more than one line, a host with no
session, a kind's rules, `Parts:` and `Lifts:` rules, a look's fixed pair, a doubled Recommended label, a `doer` on
any kind but `act` or outside its form, a result that does not read back) and drop the field-name refusals and the
`(by …)` one. `item_file_problem(text)` and `canonical_item_file(text)` are `item_problem()` and `canonical_item()`
for a file; since no key rests on a file's spelling, `canonical_item_file()` rewrites any field.
`item_file_problem()`'s messages are plain sentences, each opening with its rule's tag as `item_problem()`'s do; this
plan fixes the rules, B1 writes the words, and the fixtures pin them.

**The gate**, `board_problems(board, old)`, judges each open item of `board` whose id no item of `old` (open or
closed) has, as `(path, problem)`. It refuses only when `board` is a v2 board; `old` may be either major (the split
PR's base is v2, and its ids are the split's, D6), or None, which judges every open item. `old` is read whole, never
with `since`, or an archived id would read as new. An edit keeps an item's id, so the gate judges an item once, when
it is added; a hand edit that damages a file already on the board is `board_dir_problems()`'s to name, which each
consumer calls on the board where it already calls `v2_problems()` on the ledger (round 3's F40): agent-cadence's
cadence check, a board row beside its ledger row, and ShiftLead's read seam (*Consumers*). `parts_problems()`,
`decide_lift()` and `closes()` take an item file's text (or a `BoardItem`) where they took a line.

**Commit subjects** keep their shape and carry the id after the action: `<tool>: <action> <id> <head>[ to <date> |
: <answer>] (session <name>)`, `<tool>: append <id> <head> (session <name>)`; `subject_id(line)` reads it back and
`edit_action()` reads the action as before (a v2 reader's `EDIT_SUBJECT_RE` still matches). Subjects written before
v3.0 still read, `archive` among them. `subject()` gains `id=None` as a keyword (B1): with None it gives the v2
subject, which the v2 writers call until B5 removes them.

**`board.py`** names an item by `--id` in all five edits; `--line` and `--expect` go (an id cannot move). `add`
writes `<board>/<id>.md`; `done`, and a `decide` that closes, write the archived file and remove the open one as one
write. A write to a v2 board is refused (*split first*); `list` and `show` read one. `--board` is the directory (or
the stub, or a v2 file for the reads). **Every action resolves a stub as `load_board()` does** (round 3's F47):
given the stub's path, `add` and the five edits write into the directory beside it, never
`user_attention.md/<id>.md`. Its file-system `ls` lists subdirectories with `/` (one function, used by the board's
read and by `read_ledger()`, whose files-only `ls` it replaces; `load()` ignores the new names).

**D8. What a person reads (S8).** `board.py show [--hidden]` writes `show_board(board, today, hidden=False)` to
stdout as it is, adding nothing; `show_board()` is the module's (pure, over a `Board`; B3). Its bytes (round 5's
F70), which `show`, `show_hidden` and `show_v2` pin:
- **The items**: each item `needs_you()` gives, in its order; with `hidden=True` (`--hidden`), then each hidden open
  item, in the board's order (D6).
- **Each item** is a header line, then its text. The header line is `*<id> · <class>*` for an item `needs_you()`
  gives (`<class>` its class, `decided` to `fyi`), `*<id> · hidden until <date>*` for a hidden one (`<date>` its
  `Hide until`, `YYYY-MM-DD`), with `no id` for `<id>` on a v2 line with no readable date (D6), and `·` U+00B7 with
  one space each side; it ends `\n`. Its text is, for a v3 item, its `raw` (D4) less its trailing run of `\r` and
  `\n` characters, then one `\n`: so exactly one trailing newline, and every other byte as read, a CRLF file's
  inner `\r` among them. For a v2 item it is its `raw` (the line as written, its indent included) and `\n`, then
  each line of `detail_source` and `\n`. **Where a detail line's indent comes from:** a v2 `BoardItem`'s `detail`
  is `detail_block()`'s, each line right-trimmed and the block's common indent cut, so it no longer holds the
  source's indent; B3's `parse_board()` keeps, as `detail_source`, the same lines before that cut (each
  right-trimmed, as `detail_block()` reads them), so a detail line prints at the indent its file gives it.
- **Between items**, one blank line (`\n`), between the last item `needs_you()` gives and the first hidden one too;
  **nothing after the last item**: the output ends with its final `\n`, and a board with no item to show gives
  `""`.

No rendered file is stored: a stored view is one file every write touches, which is the conflict again.

**D9. The gate sweep over a directory.** `sweep()`'s board is `(origin_url, basename, board)`; `to_close` lists
ids; the close rule and the filing rule match items by id. **A sweep reads each board whole**, every archive month.
Draft 1 bounded it by a window, `sweep_since()`, on the claim that every closed item the sweep judges was decided
within it; round 1 showed that false, and `sweep_since()` goes:
- the owing-answer read (`_answers_owing()`, *an answer owing a lift*) takes a closed lifting `decide` of any age
  (it bounds the date only by `today`), and an answer it finds keeps the sweep's unlifted `act` open
  (`_sweep_closes()`): read from a window, an older answer would drop out and the act would close;
- the `; board <repo>` audit (`_audit_satisfied()`) takes any decided item naming the entry, with no date bound.

The rules that do judge a window (*covers*' answered within `reask_days`, the filing rule's window) reach back to
`today_utc − reask_days − 2`: an answer is dated by its `Decided:`, read against `today_local`, up to a day from
UTC, and an item closes no earlier than it is decided. Since the two reads above need every month, `since` saves
the sweep nothing, and the sweep passes none; `since` stays only for the readers D6 names.

**v3.0 sets no bound on the owing read** (round 2): reads stay whole. What makes a whole read cheap is that no
writer edits a closed item (D2, D7: an edit of a closed item is refused, and nothing moves an archived file), so a
consumer may cache each archive file by its path and blob sha and re-read only the months and files that are new
since its last read (*Consumers*, `gatesweep.py`). A tighter floor, such as each gate's latest `gate added` date
less two days, can come in a v3.x minor if the cost ever shows.

**D10. The merge gate's verdicts (S7).** The trees are maps from path to text as before. `BOARD_DIR` is
`docs/user_attention`; `BOARD_V2_PATH` and `BOARD_V2_ARCHIVE_PATH` (renamed from `BOARD_PATH` and
`BOARD_ARCHIVE_PATH`) are the v2 pair. A tree holds a v3 board when it holds a file under `BOARD_DIR/`, else the v2
pair; it is read through `load_board()` over the tree. The consumer reads the same paths at the base and the head:
every file directly in `BOARD_DIR` and every archive path the PR's file list names (a moved file's old and new
paths both; an archived item the PR leaves alone changes no verdict). **The verdicts judge what changed from the two
trees** (paths added, removed, or changed in text), never from how a forge reports a move, so a forge that reports
a moved file as a rename, or as a removal and an addition, gives one verdict; the file list decides only which
archive files the consumer fetches.
- `lift_pr_verdict()`'s **(b)** becomes: the PR's board changes are one item's, its open file changed in place or
  removed with its archived file added, and the head file is `edit_item(base file, "decide", …, close=closes(…))`
  byte for byte at `item_path(id, closed)`. A lift on a v2 board takes ordinary review (`lift-board-v2`): no v3
  writer writes one. **(c)** and another repo's case name "the item's files" where they named "the board".
- `tripwire()` reads covering items through `load_board()`; "newly closed `— lifted.`" is a `Closed:` whose why is
  `lifted` at the head and none at the base. `uncovered_decisions()`'s new `decide` is one whose id no base item has.
- A split PR (a v2 pair at the base, the directory at the head) reads the same ids on both sides (D6, D11), so the
  tripwire sees no item change; it takes ordinary review.
- Each consumer's carve-outs that judge a commit by "the board alone" read "only files under the board's
  directory": a line in each consumer's entry (*Consumers*), never code here.

**D11. Migration (S9).** `split_board(board, archive)` gives the v3 files of a v2 board and its archive, by path in
the directory:
- every line of one id, across the board and the archive, is one item, closed when one of them is (the twins
  become one closed item, as D6 reads them); it becomes `<id>.md`, or `archive/<YYYY-MM>/<id>.md` when closed, its
  id as D6 gives the v2 item (`key_id()`), so a consumer that persisted `board:<8 hex>` finds its item by the id's
  last 8 digits;
- **a twin's closed line and its detail block supply every field and the body**; the open twin is read for nothing;
- its fields are the v2 reader's, rewritten into the file's forms: `Context` and `Closed`'s why lose their final
  period (`Closed: 2026-11-12 — lifted.` becomes `**Closed:** 2026-11-12 — lifted`), `Decided` becomes `<date>[ by
  <person>] — <label>`; its body is the detail block, common indent removed; its replies are the Log;
- **its heading is `item_words(line)`** (new in B2, where it gives a v2 item's `BoardItem.words`): the words of the line
  that the v2 reader reads as no field, no reply and no part of the prefix (tick, kind, date, head, the ` — ` after
  it), in their order, kept verbatim but for runs of whitespace collapsed to one space: no period added or removed
  (`— Say Go to X. Context: …` gives `## Say Go to X.`), and any words a hand edit left outside the fields kept. A
  bold head stays in the heading as written (`**Release v2.8**, then tag it`), where *The bold head* reads it.
  **The span** (round 6's F80), defined by how the v2 reader finds each field and the replies on the line after its
  prefix: each field's span runs from its name to its value's end as its reader takes it, `Context` to where
  `CONTEXT_RE` ends it (the next field's name, or the line's end), `Parts` to where `PARTS_RE` ends it, `Due` and
  `Hide until` through their date (`DUE_RE`'s match; `_hide_match()`'s), `Answers`, `Lifts`, `Decided` and `Closed`
  to where `ANSWERS_RE`, `LIFTS_RE`, `DECIDED_RE` and `CLOSED_RE` end them, and the replies over `reply_span()`;
  each field's span takes with it the one `.` that ends its value, when the value's reader leaves one. The words are
  every piece of the line outside those spans, in order, each trimmed, the empty ones dropped, joined by one space.
  So they are the text between the prefix and the first field, any text after the last span, and any text between
  two spans: since a Context and a Parts run to the next field's name, the only such gaps on a line are after a
  `Due` or `Hide until` date (`Due: 2026-11-08. also ping sam. Closed: …` keeps `also ping sam.`);
- `README.md` is the board's text before its first item, `Ledgerboard: 3` under its title, less the `## ` heading
  nearest the first item (with more than one `## ` heading before it, only that one drops), each relative link
  gaining `../`: an inline link or image's target (`[t](target)`, `![t](target)`) or a reference definition's
  (`[label]: target`) whose target starts with no scheme (`[A-Za-z][A-Za-z0-9+.-]*:`, `mailto:` among them), no
  `#` and no `/`, outside code spans and fenced code;
- it refuses prose among the items, an item with no date, a closed item (a `[x]` line) with no readable `Closed:`
  date, which gives no month to file it under (round 4's F62: add the date by hand first), two open lines of one
  id, two closed lines of one id, two items given one id, and a result that does not read back the same items (compared as D6's *Comparing two reads*)
  or that `board_dir_problems()` flags.

**The key a consumer persisted.** ShiftLead's `sessionorc/workorders.py`, as the pinned file has it:

```python
def key(text: str) -> str:
    """`board:<key>` for an open item's text as the reading gives it — its line less the open tick."""
    return PREFIX + hashlib.sha256(ledgerboard.item_key(f"- [ ] {text}").encode("utf-8")).hexdigest()[:8]
```

`PREFIX` is `"board:"`; `text` is `ITEM_RE`'s or `CLOSED_ITEM_RE`'s `text` group (`^\s*-\s*\[ \]\s+(?P<text>.+)$`,
the `[xX]` form for a closed line), as `parse_board()` trims it into `BoardItem.text` (today's, kept to B5),
or (in `show()`) untrimmed,
which keys the same since `item_key()` ends by stripping trailing spaces and periods. `key_id(key)` is that hash:
the first 8 lower-case hex digits of the SHA-256 of the key's UTF-8 bytes, the key `item_key("- [ ] " + text)`.
So:
- **an indented line** (`  - [ ] …`, a nested item) loses its indent with its tick and keys as its column-0 form,
  where `item_key()` of the raw line keeps the indent: two lines of one text at different indents share an id, and
  the split refuses them (two items given one id);
- **a `[x]` line** reads its tick as `[ ]` and `item_key()` cuts its `Closed:`, so a closed line keys as its open
  twin: one id for both, which is what makes the twins one item.

`board_stub(title, name)` is the stub `board.py split` leaves at the v2 path. `split` takes no target (round 6's
F75): it always writes the directory beside the board, named the board's name less `.md`, since that is the one
directory the stub reads as (D6); any other place would leave a stub reading as a missing directory. `split_board_notes(readme)` names
README lines that may describe the v2 board. `board_dir_problems(path, ls, read)` is `v2_problems()`'s twin, and
each consumer calls it where it calls `v2_problems()` (D7, *Consumers*). On a v2 board (a repo still on v2, as in
its vendoring PR before the split) it returns `Board.problems` alone (round 3's F50): the checks of a directory's
names, header blocks and months have nothing to judge there.
`key_id(key)` and `item_key()` are kept through v3.x. The split runs in each consumer's v3.0 vendor PR, beside v3.0's
ledger half (TD-078), landed when no open PR edits the board (each such PR is redone over the directory).

**D12. The release: v3.0, and v2.8 before it.** v3.0 is a major (*Versions* text 12). It reads v2 boards and writes
v3 only. It goes out with TD-078's ledger half as one v3.0; when, and what else it carries, is Paul's. The order:
- **v2.8 is released before B1 merges.** Past the tag v2.7, `main` carries two changes to `ledgerboard/`, `SPEC.md`
  and `fixtures/` (`git log v2.7..origin/main`): TD-079 (TD-068's B1, PR #240: `set --title` retitles an entry,
  and `edit` and `set` refuse names that belong elsewhere, `SPEC.md`'s v2.8 text) and TD-080 (PR #242:
  `misplaced_names()`'s note for two Title sections names the heading). TD-073 is v2.7's (its commit is an ancestor
  of the tag). Whatever `main` carries past v2.7 when B1 is ready is released as v2.8 before B1 merges: a
  precondition of B1. The release itself is Paul's; the board's act for it stands open (its words still name
  TD-073 and a fold into v2.7, which the tag has overtaken).
- **No v2.x release after B1 merges**, and no tooling to release from a branch: `release.sh` cuts from `origin/main`
  and stays so. A v2.x fix wanted after B1 merges goes into v3.0.
- **TD-065 is decided before B1 starts** (round 5's F68, R10's fix, which replaces round 4's delta rule): a
  precondition of B1 beside the v2.8 release, and the person's. `Doer` is this design's own v3 header field either
  way (D4, text 8, text 13): B1 lands `parse_doer_value(value)`, `BoardItem.doer`, `item_record()`'s `doer`,
  `item_file(doer=)`, the header field and text 13's `doer-field`, `doer-repo` and `doer-part`, unconditionally. The
  two outcomes:
  - **TD-065 ships in v2.8.** Its build merges before B1 starts, so it is in v2.8, which is released before B1
    merges. A v2 line can then carry `Doer: <value>.`: TD-065's `parse_doer(text)` stays the v2-line reader the
    v2 half of `load_board()` uses, and at the split (B5) the v2 half carries a v2 line's doer into the header field
    `Doer` (`split_board()` writes a v2 item's `fields`, D4). Text 14's `Doer:` bullet substitutes in v2.8's
    `Doer:` paragraph (*The board*, "**`Doer:`** (v2.8) — `Doer: <repo>.` or `Doer: team <team>.`, …", TD-065's
    text 1).
  - **TD-065 is closed as superseded by the v3 field.** No v2 line carries a `Doer:`, every v2 record's `doer` is
    None, and text 14's `Doer:` bullet has no paragraph to substitute in.

  Those two are the only differences in what B1 to B5 build. What follows from v2.8's starting point is mechanical:
  when TD-065 shipped, `BoardItem.doer` and `item_record()`'s `doer` key are v2.8's already (B1 keeps them and
  regenerates no record for them, *The builds*), and `SPEC.md`'s *The open item line* already defines `doer-repo`
  and `doer-part`, with the bodies text 13 gives them, so B1 moves those two productions from that block into text
  13's rather than adding them (a production is defined once: `tests/test_grammar.py`'s `ebnf()` asserts it), and
  TD-065's `doer` production reads them there. Since TD-065 is shipped or closed before B1 starts, and no v2.x
  release follows B1, nothing of TD-065 lands after B1.
- **TD-078's open question**, whether its archived-entry writer route "ships in a v2.x minor first", has the same
  answer: in a v2.x minor only as part of v2.8, released before B1 merges; otherwise it ships in v3.0.
- **The builds**, B1 to B5, merge in order with no release between them; then v3.0.

## Consumers

Both change in their v3.0 vendor PR, each through an entry filed in that repo through its question seat once v3.0
is cut, agent-cadence's first. Each line below is a line for that entry, never code here.

- **agent-cadence**:
  - vendor v3.0 and run `board.py split` on `docs/user_attention.md` in the same PR, landed when no open PR edits
    the board;
  - `board_edit.py`, which imports `edit_line()` from the vendored module and calls it directly (pinned tree
    `67023cc`), moves to `edit_item()` by `--id` (or to `board.py`'s edits): its `--line`, `--expect` and their
    exit-3 refusal go; `replay` (TD-248, in a tree later than the pin) retires, there being no single file to replay
    into;
  - `nudge_user_attention.py`: read boards through `load_board()` (its own checkout's directory; another repo's
    through the forge's directory listing, with `since=` the months it shows); its `ARCHIVE_AT` prompt and its
    duplicate-key warning (`closed_items()`, `item_key()`) go; `--report --json` prints ids, not lines;
  - `check_cadence.py`: `BOARD` becomes the directory; `classify_direct()`'s stamp is `README.md`'s stamp lines
    alone (a stamp commit still rewrites `README.md`, D2), its board-append is item files added directly under the
    directory, each with a `Due:` (its `## Needs` test becomes the kind test it stood for, its choice), its
    board-edit is one item file changed in place or moved into `archive/` under an edit subject;
    `row_board_edit_pr()` the same;
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
  - `sessionorc/board.py`: `add()` and `add_decided()` drop `under=NEEDS`, its edits pass `--id` (`plan_edit()`'s
    line and expect go), `item_line()`/`decided_line()` become `item_file()`/`decided_file()`;
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

Each block is what `SPEC.md` says once built. Where a block names a substitution in a paragraph it keeps, the rest
of that paragraph stands as written.

**No sentence lands before the code that makes it true** (round 4's F59). Where a block's sentences belong to
different builds, the block says which, and each build lands only its own: text 8's closing sentence of its
`parse_item()` paragraph ("`item_record()` gives its record") is B2's, with *Reading a board*, though the rest of
that paragraph is B1's; text 8's *Reading a board* lands at B2 without the words "and no `line`", which B5 adds;
text 9's *A snapshot against the ledger* paragraph is B2's (its item-file input is B2's code), with 9's *gate*
paragraph. Text 2 lands at B2 without its first paragraph's "; v3.x reads one and writes none" and without its
second paragraph (the one opening "From v3.0, everything this section says about a line"), which B5 adds (round
5's F71): until B5 the module still carries the v2 line writers and `board.py` writes a v2 board until B3, so
neither "writes none" nor "read only" holds before B5 removes them. Round 6's F77 tags three more: text 8's *The
item file* lands at B1 without its two clauses that name `board_dir_problems()` ("and `board_dir_problems()` names
it", after the header-block line that is no field and after a value not in its form), which B2 adds with
`board_dir_problems()`; text 10's closing sentence lands at B3 without "(*split first*)", which B5 adds with the
`split` action (until then `board.py`'s refusal of a v2 board says only that it writes a v3 directory, and B5's
words give `write_v2_refused`'s expected output its `split` hint); and each of text 14's bullets carries its own
build (B1, B2 or B5). *The builds* name each block's build so.

**1. The title.** `# The ledger and board formats — versions 1 and 2` becomes `# The ledger and board formats —
versions 1 to 3`.

**2. *The board*, its first three paragraphs** ("A board is a Markdown file …", "**An item** is one line …" and
"The archive moves them …") are replaced by these three:

> A board is a set of items for a person. **A v3 board is a directory** (by convention `docs/user_attention/`), one
> file per item, named by its id (*The board as a directory*, v3.0). A v2 board is one Markdown file (by convention
> `docs/user_attention.md`) with its archive beside it (`docs/user_attention_archive.md`); v3.x reads one and writes
> none. What an item means is the same in both, and the paragraphs below say it once. Where they place a field on a
> line (*right after the Context*, *ahead of the `Due:`*, *starting a sentence*), the place is a v2 line's; in an
> item file each field is a header line, in the order *The item file* gives.
>
> **From v3.0, everything this section says about a line** (its text, where a field stands on it, its key, its
> replies' tails, its tick, and the functions that write or judge a line: `item_line()`, `decided_line()`,
> `edit_line()`, `item_problem()`, `canonical_item()`, `parse_closed_items()`) **is v2's, read only**: v3.x reads a
> v2 line so, and writes none. A paragraph that says it once for both majors names the item file's form beside the
> line's.
>
> **An item** on a v2 board is one line: `- [ ] [kind] YYYY-MM-DD (session <name> on <host>, or n/a) — text.
> Context: … Due: YYYY-MM-DD.` A closed item is ticked: `- [x] … Closed: YYYY-MM-DD — why.` Items are never
> deleted. On a v2 board, when an open item and a closed one have the same id (*Reading a board*), on the board or
> in its archive, the item is closed: a merge kept both sides. A v3 board has no such rule: closing an item moves
> its one file.

**3. *The board*, *The item key*** is replaced by:

> **The item key** (v2) — the line with the tick, `Closed:`, `Decided:`, `Due:`, `Hide until:` and the reply tails
> taken out, indentation kept (`item_key()`). On a v2 board it is what makes an open and a closed copy of one item,
> or a snoozed or replied-to one, equal; v2.3 strips a date-shaped `Hide until: D` wherever it stands, as it strips
> `Due:`, so hiding an item never re-keys it. **From v3.0 an item is its id, not its key:** no v3 reader or writer
> keys an item. `item_key()` remains to read a v2 board and to give a v2 item its id (`key_id()`, *The board as a
> directory*), so what the key is for a given v2 line does not change through v3.x: consumers map the keys they
> persisted to ids through it.

**4. *The board*, *What needs the person*** is replaced by:

> **What needs the person** (`needs_you(board, today)`, v2.3; from v3.0 `board` is a `Board`, *Reading a board*) is
> every open item not hidden, each with one class and a signed `days`, in one order: `decided` (`days` the
> decision's age; oldest decision first); then the person's to-do — `overdue` (days past due; most first), `due` (0
> on the due date, negative days until it; soonest first), `bad_due` and `undated` (the board's order); then each
> `watch` item, ordered the same way and keeping its own class and signed days; then each `fyi`, never due, in the
> board's order. **The board's order** breaks every tie: a v2 board's line order, and a v3 board's ids descending,
> newest first (by `Added` date; within one day the order is random). So tied items can change order when a board
> is split; which items need the person, and their classes and days, do not. Which of these a consumer shows, and
> when it escalates, is the consumer's.

**5. *The board*, *Preamble lines*** gains, after its first sentence:

> On a v3 board they are `README.md`'s lines, every one of which is preamble, a line shaped like an item among them
> (v3.0). `README.md` is the one file a stamp rewrites, so two stamps written on two branches still conflict there.

**6. *The board*, *The gate sweep*.** "A board is `(origin_url, basename, text, archive_text)`, named by …" becomes:

> A board is `(origin_url, basename, board)`, `board` a `Board` read whole (*Reading a board*; v3.0, where v2.x took
> the board's and its archive's texts), named by …

In `sweep()`'s return, `to_close: {board: [item key]}` becomes `to_close: {board: [item id]}`; *The close rule*'s
"(by item key)" becomes "(by id)"; "Each item filed is `item_line()`'s arguments (`text`, `context`, `kind`,
`answers`, `default`, `detail`, `lifts`)" becomes "Each item filed is `item_file()`'s arguments (the same names)";
and *One filing rule*'s "An item closed `— lifted.`" becomes "An item closed with the why `lifted`". In `covers()`'s
paragraph (round 4's F60), "`closed` or `closed-decided` (closed on the board or in its archive)" becomes
"`closed` or `closed-decided` (closed: on a v3 board, its file under `archive/`; on a v2 board, closed on the
board or in its archive)". After *The close rule*'s list, add:

> **What a sweep reads** (v3.0): each board whole, every month of its archive. An answer owing a lift may be of any
> age, and keeps the sweep's act open while it owes; the `; board <repo>` audit takes a decided item of any date. The
> rules that judge a window reach back to `today_utc − reask_days − 2` (a `Decided:` date is read against
> `today_local`, up to a day from UTC, and an item closes no earlier than it is decided), but those two reads need
> every month, so a sweep reads no board with `since`.

**7. *The board*, *The merge gate's verdicts*, its first paragraph** is replaced by:

> **The merge gate's verdicts** (v2.4) are three pure functions over a PR's **trees**, each a map from path to text
> read at the PR's base or head: the ledger at `docs/ledger/` (v2; a tree with no file under it holds a v1 ledger at
> `docs/technical_debt.md`), and this repo's board at `docs/user_attention/` (v3.0, `BOARD_DIR`), or, in a tree with
> no file under that directory, the v2 board at `docs/user_attention.md` and its archive at
> `docs/user_attention_archive.md` (`BOARD_V2_PATH`, `BOARD_V2_ARCHIVE_PATH`, until v3.0 `BOARD_PATH` and
> `BOARD_ARCHIVE_PATH`), each read through `load_board()` (`LEDGER_DIR`, `LEDGER_V1_PATH`). A tree holds the same
> board paths at the base and the head: every file directly in `BOARD_DIR`, and every file under its `archive/` at a
> path the PR's file list names (a moved file's old and new paths both). A verdict judges a PR's board changes from
> the two trees, as the paths added, removed and changed in text, never from how the forge reports a move. Each
> verdict names what it finds as `(kind, text)` pairs; `repo` is as for the sweep. The consumer fetches the trees,
> the file list, the commits and the dates from the forge, and acts on the verdict.

In `tripwire()`'s **no suffix** bullet, "is newly closed `— lifted.`" becomes "is newly closed with the why
`lifted` (`Closed: D — lifted`; on a v2 line `— lifted.`)". `lift_pr_verdict()`'s opening "a PR whose one changed
board item gains a `Decided:`" stands; **(b)** is replaced by:

> - **(b)** the PR's changes to the board are one item's: its open file changed in place, or removed with
>   `archive/<YYYY-MM>/<id>.md` added (the item closed). The base item is an open `decide` naming one entry and one
>   gate, never answered, that gains `Decided: D by <p> — <label>`; the head file is `edit_item(base file, "decide",
>   label, by, D, close=closes(item, label, entries after))` byte for byte at `item_path(id, closed)`, so a work
>   order is never closed and a finished lift never left open; D lies from `created_at − 1` to the merge date (else
>   `created_at`) `+ 1`, the board's local day running up to a day from UTC. A lift on a v2 board takes review
>   (`lift-board-v2`, v3.0): no v3 writer writes one;

In **(c)**, "the PR changes exactly the board and the open file of each entry it changes" becomes "the PR changes
exactly the item's files and the open file of each entry it changes", and "the PR changes the board alone" becomes
"the PR changes the item's files alone", and "`decide_lift()` of the base line" becomes "`decide_lift()` of the
base item's file" (round 4's F60; a lift on a v2 board has taken review at (b)). In
`uncovered_decisions()`, "(its key on no line of the base board)" becomes
"(its id on no item of the base board, open or closed)".

**8. A new section, `## The board as a directory (v3.0)`**, after *The board* and before *Edits*:

> ## The board as a directory (v3.0)
>
> A v2 board is one file that every new item is written into at one place, so two changes that each add an item
> conflict, and an item's identity is its text (*The item key*). **A v3 board is a directory** (by convention
> `docs/user_attention/`) with one file per item, named by the item's id:
>
> ```
> docs/user_attention/
>   README.md                  # the opening prose, then the preamble lines: Ledgerboard: 3, People:, …
>   2026-11-11-3f9a2c1d.md     # one open item
>   archive/
>     2026-11/
>       2026-10-30-0b7e41aa.md # a closed item, filed under the month of its Closed: date
> ```
>
> - **`README.md`** holds what a v2 board holds before its first item, and declares `Ledgerboard: 3` on a preamble
>   line. Every line of it is preamble.
> - **An open item** is a file `<id>.md` directly in the directory; **a closed one** is `archive/<YYYY-MM>/<id>.md`,
>   `<YYYY-MM>` its `Closed:` date's month (`item_path(id, closed=None)`, `closed` that date). Any other file is not
>   an item. Closing an item moves its file in the same write; nothing else moves one, and none is deleted.
> - **No sections and no stored view.** What needs the person, and in what order, is `needs_you()`'s; a person reads
>   the board through `board.py show`.
>
> **The item id** is `YYYY-MM-DD-<8 hex>`: the item's `Added` date, a hyphen, and eight lower-case hex digits
> (`item_id(added, nonce)`, refused for anything else, a date that is no day of the calendar among it). The writer
> draws the nonce at random and draws again for a name the directory or its archive holds; the module draws nothing.
> No writers coordinate: two items added on one day share an id about once in four billion pairs, and two changes
> that add one id conflict as two files at one path. An id never changes.
>
> **The item file** is a small entry, in the grammar of *Ledger entries and their edits*:
> - **The heading** is `## <text>`, the item's words (`BoardItem.words`): one line, any words, no field. Its first
>   bold run is the item's bold head (*The bold head*).
> - **The header block** is the `**Name:** value` lines after the heading's blank line, up to the next blank line,
>   read as an entry's are: a name compared by `field_key()`, which ignores case and reads `-`, `_` and any run of
>   whitespace as one space; the spaces and tabs at a value's ends dropped; and the first of a name winning. A value
>   is the whole line: it holds any words, a field's name among them. The fields, in the order the writers write
>   them, each meaning what *The board* says:
>   - `Kind` — `decide`, `act`, `look`, `watch` or `fyi`; none is the kindless to-do;
>   - `Added` — the date the item was added, its id's date;
>   - `Session` — `<name>` or `<name> on <host>`, the v2 head; none for `n/a`, and none on a decided file
>     (`decided_file()`, the v2 `(person)` head);
>   - `Context` — what the item refers to, its refs read as a v2 Context's are; `none` for nothing;
>   - `Parts` — a `decide`'s snapshot, `TD-15, TD-16`;
>   - `Doer` — on an `act` only, who should do its step: `<repo>`, a repo whose last part does not end in `.`
>     (*Appendix: grammar*, `doer-repo`), or `team <team>`, `<team>` a person's name; `Doer: team` alone names the
>     repo `team`. `parse_doer_value(value)` reads it as `("repo" | "team", name, value)`, or None outside that form,
>     reading a run of spaces or tabs after `team` as one space (`item_file_problem()` faults that spelling);
>   - `Due`, `Hide until` — a date each; an unreadable `Due` is reported, never silently undated;
>   - `Answers`, `Lifts` — as on a v2 line, without the final period;
>   - `Decided` — `<date>[ by <person>] — <label>`: the date and who answered first, so the label runs to the line's
>     end and holds any words. `parse_decided_value(value)` reads it as `(label, date, by)`, or None outside that
>     form, and `parse_item()` reads it into `decided` and `decided_by`; `parse_decided()` and `parse_decided_by()`
>     read a v2 line's;
>   - `Closed` — `<date>` or `<date> — <why>`, read by `parse_closed_value(value)` as `(date, why)`, or None outside
>     that form.
>
>   `Answers` and `Lifts` values are read by `parse_answers_value(value)`: the answers split on each bar not after a
>   `\`, `\|` read as a bar, each trimmed (`split_answer()` then reads an answer's label, mark and consequence).
>   Each value reader reads the bare value the header line holds; the v2 readers (`parse_decided()`,
>   `parse_answers()`, `parse_lifts()` and the rest) find a field on a v2 line and read nothing else.
>
>   A line in the header block that is no field does not end it: it is in no field, every edit keeps it byte for
>   byte, and `board_dir_problems()` names it. A value not in its form, for `Decided`, `Closed`, `Kind`, `Hide
>   until`, `Parts` or `Doer`, is kept, and read as the field absent: no answer, no close, no kind (so a to-do,
>   shown), not hidden, no parts, no doer; `board_dir_problems()` names it. A `Due` not in its form is reported, as
>   *The board* says. A field the reader does not
>   know is kept: it is in `BoardItem.fields` (every header field as written, in its order), every edit keeps its
>   line byte for byte, and `item_file_problem()` faults it. A later v3 minor that adds a field changes nothing an
>   older v3 reader reads of the others; an older v3 gate faults an item carrying it.
> - **The body** is the detail block (*The detail block*): the lines after the header block up to the Log, leading
>   and trailing blank lines dropped (`BoardItem.detail`). No edit touches it.
> - **The Log** is the body's last section, led `**Log:**`, one line per reply, `- YYYY-MM-DD: <name>: <words>`,
>   oldest first. `<name>` holds no `:` and is at most 40 characters; `<words>` are not empty. A Log line in another
>   shape is kept, and read as no reply.
>
> `parse_item(text, path="")` reads one file as a `BoardItem`: its `id` from the path's name (None when it is not
> one), `path`, its `words` (the heading's text), its fields, each value through its reader above (`kind`,
> `due`, `hide_until`, `parts`, `answers`, `default`, `consequences`, `lifts`, `decided` and `decided_by`),
> `added`, `session` and `host`, `context`, `doer`, `closed` (`(date, why)` or None), `replies`, `detail`,
> `fields`, and `raw`, the file's text as read. `item_record()` gives its record (*Reading a
> board*).
>
> **Reading a board** (`load_board(path, ls, read, *, since=None)`) gives a `Board`: `major`, `preamble`
> (`README.md`'s text, or a v2 board's text before its first item), `items` (the open items), `closed` (every closed
> item read, its archive's among them), each a `BoardItem` with its `id`, and `problems`.
> - **A directory** is read as `README.md`, then each `<id>.md` directly in it, then each month under `archive/` and
>   its files (*The board's order*, below, orders what it reads). A month is a directory directly under `archive/`
>   named `YYYY-MM`, a real month; nothing else in the directory is read (rule 11). An item is closed when its file lies under
>   `archive/`, or lies outside it and carries a `Closed:` in its form; every other item is open. An archived file
>   with no `Closed:` in its form is damaged (rule 9 below) and read as closed, with no date. An id held by two files
>   is read once (rule 8): an archived copy wins over an open one, and of two archived copies the later month's.
> - **The board's order:** `items` and `closed` are each in id order descending, newest first, on a v3 board, and in
>   line order on a v2 one (`closed` the board's closed lines, then its archive's). Every reader that lists items
>   lists them so, and *What needs the person*'s ties fall back to it.
> - **A v2 file** is read with its archive beside it (`<stem>_archive.md`) by the v2 line reader as the last v2.x
>   release has it (`parse_board()`), whatever fields it reads filling the `BoardItem` fields of the same name, but
>   for twins: an open line sharing its id with a closed line on the board or in its archive is closed, and the
>   closed line is the item (v3.0; v2.x matched twins within one file, by `item_key()`). Two open lines of one id,
>   or two closed ones, are both read, each an item with that id, and named in `problems` (rule 10); `to_close` names the id
>   once, and a closer of the v2 board closes every open line of it. A v2 item's id is its line's date, a hyphen,
>   and `key_id()` of its key: `item_key()` of `- [ ] ` and the line's text after its tick (its indent, tick and the
>   whitespace after the tick dropped), trimmed. So it reads with the id its split file gets, a closed line with its
>   open twin's, and a consumer that persisted a hash of that key finds it in the id. `key_id(key)` is the first 8
>   lower-case hex digits of the SHA-256 of the key's UTF-8 bytes. A line with no readable date has id None. Its
>   `BoardItem` carries every field a v3 item does that the line holds, its words (`item_words()`: every piece of
>   the line after its prefix outside the spans its fields and replies are read from, a field's span with the `.`
>   ending it, joined by one space) as `words` and the line as `raw`.
> - **The stub**, a file that declares `Ledgerboard: 3` and holds no item, is read as the directory beside it, its
>   name without `.md`.
> - **The caller does the I/O**, as for `load()`: `ls(path)` returns the names directly in the directory `path`,
>   each subdirectory's name followed by `/` (v3.0; `load()` ignores those), or None when `path` is not a
>   directory; `read(path)` returns a file's text, or None. Every path a `Board` names is relative to the board's
>   directory.
> - **`since`**, a date, leaves the archive's months before its month unlisted and unread, so `closed` holds only
>   the months read. It is for a reader of open items and recent closes; the sweep, `board_problems()`'s `old`, the
>   verdicts and `split_board()` read a board whole.
> - **`major`** is what the preamble declares, else 2 for a file and 3 for a directory; a missing `path` gives an
>   empty `Board` with `major` None. A v3 board's declaration is read from every line of `README.md` outside HTML
>   comments (`board_major(text)`), a v2 board's from the lines above its first item (`board_major(text,
>   file=True)`), 2 when a v2 file declares none: a board's v1 and v2 are one format. The board's major is its own:
>   `BOARD_MAJOR` (3) is the newest a module reads, and `version_problem(board)` names a `Board` whose `major` is
>   newer; `version_problem(text)`, `format_major()` (whose "none means 1" stays the ledger's) and `FORMAT_MAJOR`
>   stay the ledger's.
> - **`problems`** and **`board_dir_problems(path, ls, read)`** never raise. Each rule below is marked `problems`
>   (`Board.problems` lists it, as `(path, problem)`: what the read skipped or could not settle) or
>   `board_dir_problems() only` (the read settled it, or never read the file). `board_dir_problems()` names, as
>   `(path, problem)`, every rule of both marks on a v3 board, and gives `Board.problems` alone on a v2 one. Each
>   rule names its finding once. Both lists are sorted by path (code-point order), then by the rule's number, then
>   by line within the file.
>   1. `problems`: a file `read()` gives None for: skipped, named under its path.
>   2. `problems`: a file `parse_item()` reads as no item (no `## ` heading): skipped, named under its path.
>   3. `problems`: a `README.md` that is missing, or declares no major: `major` 3, named under `README.md`.
>   4. `problems`: a `README.md` declaring 2: `major` 2, named under `README.md`.
>   5. `problems`: a file declaring `Ledgerboard: 3` that holds items (it is no stub): read as a v2 file, `major`
>      3, named under its name.
>   6. `problems`: a stub whose directory is missing: an empty `Board`, named under the stub's name.
>   7. `problems`: an item with no `Added`: read, its `added` None, named under its path.
>   8. `problems`: one id in two files of a v3 board: read once, named once, under the path of the archived file
>      that wins (the later month's of two archived copies).
>   9. `problems`: a file under `archive/` with no `Closed:` in its form: read as closed, with no date, named under
>      its path.
>   10. `problems`: one id on two open lines, or on two closed lines, of a v2 board: both lines read, the id named
>       once, with both lines, under the board file's name when either line is on it, else the archive's.
>   11. `board_dir_problems() only`: any entry the read does not take: a file directly in the directory, or in a
>       month, whose name is not an id and `.md` (`README.md` aside); a subdirectory of the directory other than
>       `archive/`; a file directly in `archive/`; a directory under `archive/` that is not a month; a directory in
>       a month. Each is named once, under its own path (a directory's with its trailing `/`), and not read or
>       descended into.
>   12. `board_dir_problems() only`: a header-block line that is no field: kept, in no field.
>   13. `board_dir_problems() only`: an `Added` that is not the id's date.
>   14. `board_dir_problems() only`: a `Decided` or `Closed` not in its form: read as no answer, or no close; a
>       `Kind`, `Hide until`, `Parts` or `Doer` not in its form: read as the field absent, a `Kind` outside the five
>       as a to-do, shown; a `Doer` that reads but is spelled with more than one space, or a tab, after `team`: read.
>   15. `board_dir_problems() only`: a `Closed:` in its form on a file outside `archive/`: read as closed.
>   16. `board_dir_problems() only`: an archived file in a month that is not its `Closed:` date's: read as closed.
> - **The readers take the `Board`**: `needs_you()`, `covers()`, `sweep()`, `board_problems()` and the merge gate's
>   verdicts; `board_people()`, `answered_by()`, `people_problems()` and `answered_by_problems()` read its preamble,
>   every line of `README.md` on a v3 board and the lines above the first item on a v2 one, as `board.py`'s
>   `who_answered(board, by)` does through `board_people()`; and a consumer calls `version_problem(board)` before
>   it trusts the rest. `item_record()` gives an item's record, of either major, with `text` the item's words and
>   no `line`, and these keys (v3.0), every other key as before: `id`, a string `"YYYY-MM-DD-<8 hex>"`, or `null`
>   for a v2 line with no readable date; `path`, a string, the file's path in the directory (`""` for a v2 item);
>   `added`, `"YYYY-MM-DD"` or `null`; `context`, a string, the Context without its final period, or `null` for an
>   item with none; `closed`, `{"date": "YYYY-MM-DD", "why": <string> | null}` (both `null` for an archived file
>   with no `Closed:` in its form), or `null` when the item is open; `decided`, as before, `{"text": <label>,
>   "date": "YYYY-MM-DD"}` or `null`, `decided_by` beside it; and `doer`, `{"kind": "repo" | "team", "name":
>   <string>, "text": <string>}` (`text` the value as written) or `null`.
> - **Two reads of one board compared** (a v2 board and its split): records keyed by `id`, `path` and `line` left
>   out; `covers()`, `to_close` and `lifts` as lists sorted by id; `needs_you()`'s rows by tie group (each run of
>   one class and one `days`), each group as a set and the groups in order. So compared, a v2 board and its split
>   read the same.
>
> **Damage a hand edit or a merge can do** is what `board_dir_problems()` names (the rules under *Reading a
> board*'s `problems`). The gate judges an item only when it is added, so a consumer calls `board_dir_problems()` on
> the board it is about to merge, wherever it calls `v2_problems()` on the ledger.
>
> **Migration** is `split_board(board, archive)`, for a v2 board only: the v3 files of a v2 board and its archive,
> by their paths in the directory.
> - Every line of one id across the board and the archive, with its detail block, is one item, closed when one of
>   its lines is; it becomes `<id>.md`, or `archive/<YYYY-MM>/<id>.md` when closed, its id the v2 item's. Of twins,
>   the closed line and its detail block give every field and the body. Its fields are what the v2 reader reads,
>   each in the file's form: `Kind`, `Added` (the line's date), `Session` (none for `n/a` and `(person)`),
>   `Context` (without its final period), `Parts`, `Due` (an unreadable one as written), `Hide until`, `Answers`,
>   `Lifts`, `Decided` (`<date>[ by <person>] — <label>`) and `Closed` (`<date>[ — <why>]`, the why without its
>   final period), from the closed line, and any other field the v2 reader reads, as the header field of the same
>   name. Its body is the detail block with its common
>   indent removed; its replies are its Log. Its heading is `item_words()` of the line: every word the v2 reader
>   reads as no field, no reply and no part of the prefix (the text, and any words a hand edit left outside the
>   fields), in their order, verbatim but for runs of whitespace collapsed to one space, so no word is lost and no
>   period is added or removed; a bold head stays in it as written.
> - `README.md` is the board's text before its first item, with `Ledgerboard: 3` under its title (any
>   `Ledgerboard:` line dropped) and without the `## ` heading nearest the first item (the one heading that opens the
>   first item's section; any earlier `## ` heading stays). Each relative link there gains `../`, since the file
>   moves one directory down: the target of an inline link or image (`[t](target)`, `![t](target)`) and of a
>   reference definition (`[label]: target`), when it starts with no scheme (`[A-Za-z][A-Za-z0-9+.-]*:`, `mailto:`
>   among them), no `#` and no `/`, outside code spans and fenced code. The archive's text before its first item is
>   dropped.
> - It refuses a board that declares `Ledgerboard: 3`; a line after the first item that is no item, no detail
>   block's, not blank and no `## ` heading (prose among the items: move it into the preamble first); an item with
>   no date; a closed line with no readable `Closed:` date (no month to file it under: date it first); two open
>   lines, or two closed lines, of one id; two items given one id; and a result that
>   `load_board()` does not read back as the same items (open and closed, at one date, compared as *Reading a
>   board* compares two reads) or that `board_dir_problems()` flags.
> - `board_stub(title, name)` is what `board.py split` leaves at the v2 path: `# <title>`, a blank line,
>   `Ledgerboard: 3`, a blank line, and `This board is the directory [<name>/](<name>/), one file per item
>   (ledgerboard v3.0).` A v2.x reader that checks the version refuses it, a v2.x writer refuses it unread, and
>   `load_board()` reads the directory through it.
> - `split_board_notes(readme)` lists the lines of that `README.md` which may still describe the v2 board, as
>   `(line number, line, why)`, for the caller to warn about, nothing rewritten: a line naming
>   `user_attention.md`, `user_attention_archive.md`, `Needs the user` or `In-flight`, and a `Format:` line.

**9. *Edits*** is replaced by:

> ## Edits
>
> Every edit rewrites one open item file, by one header line set or one Log line appended, and nothing else, and is
> refused unless the reader reads back exactly what was meant (`edit_item(text, action, *, to, answer, why, reply,
> by, today, close)`, v3.0). A field it adds goes right after the last known field that precedes it in the header
> order (any unknown field between them stays where it is), or first in the header block when none does; a field it
> sets that is there is rewritten in place. A line it adds or rewrites ends as the file's first line does (`\r\n` or
> `\n`); every other byte is kept. An edit of a closed item is refused.
> - **snooze** hides the item: it sets its `Hide until:` and leaves its `Due:` alone;
> - **due** sets the item's `Due:`, the real deadline;
> - **done** sets `Closed: <today>`, or `Closed: <today> — <why>`;
> - **decide** sets `Decided: <today> — <answer>`, or with `by` `Decided: <today> by <by> — <answer>`, replacing an
>   earlier one. It refuses a `by` that is not a person's name. With `close`, on an item whose Context names a
>   gate, it also sets `Closed: <today> — kept waiting` for a waiting-only answer or `Closed: <today> — lifted` for a
>   lifting one, and refuses any other answer (`closes()` says when to pass it);
> - **reply** appends `- <today>: <by>: <words>` to the Log, opening a `**Log:**` section after the body when there is
>   none. It refuses a `by` holding `:` or of more than 40 characters, and empty or blank words.
>
> An edit that closes the item gives a file whose place is `item_path(id, closed)`; the writer moves it in the same
> write.
>
> **A new item** (`item_file(text, due, today, session, host, context, *, kind, answers, default, detail,
> hide_until, lifts, parts, doer)`, v3.0) is one file: `## <text>`, a blank line, the header block (`Kind` when
> given, `Added: <today>`, `Session` when there is a session, `Context`, then `Parts`, `Doer`, `Due`, `Hide until`,
> `Answers` and `Lifts` as given), and, after a blank line, the detail block. The text is trimmed and not empty, and
> no period is added. An empty context is `none`. `Session` is `<session>` or `<session> on <host>`. `Lifts` is
> written only when it names answers other than `Go` alone (each one of its answers, once, written as its answer
> spells it). A `doer` is refused on any kind but `act`, and outside its form. A decide's `parts` (v2.6) are written
> ordered by number, separated by `, `, each as given, and are refused on any kind but `decide`, for an empty list,
> for an id that is not `TD-` and 1 to 18 ASCII digits, for an id that shares its number with another or with the
> Context's entry, unless the Context names exactly one entry, a bare `TD-n`, and one gate, a `decision (<person>)`,
> with nothing after the gate, and unless one of its answers lifts. What a kind takes:
> - a `decide` carries two or more distinct answers, at most one marked ` (default)`, and a detail block;
> - a `look` carries exactly `Answers: Works | Not right: <what>`, which the writer writes itself, `Works` marked
>   ` (default)` only when the caller asks;
> - an `fyi` carries no `Due`, and every other kind carries one;
> - no kind but `decide` and `look` carries answers.
>
> These are the writer's rules. The reader still reads whatever a file carries. An answer is written `<label>` or
> `<label> — <consequence>`, with the mark on the label.
>
> The **detail block** is composed from named parts, in the order `Context`, `Question`, `Caveats`, `Recommended`.
> Each part is one bullet at column 0, ``- **<Part>:** <words>``, with any further lines as nested bullets under it,
> indented two spaces. On a `decide` with a default, Recommended opens with that default's label and ` — `, which
> the writer adds: a `recommended` whose words already open with that label and ` — ` (whitespace collapsed, the
> label compared ignoring case) is refused, naming the prefix (TD-069). An `Otherwise` text follows the Recommended
> words on the same bullet as ``**Otherwise:** <words>``. A `decide` needs Context, Question and Recommended. No
> writer touches the block afterwards.
>
> The writer refuses a text, a context, an answer, a detail value or a reply's words that is more than one line; a
> date that is not `YYYY-MM-DD`; a host with no session; and any result the reader would not read back as exactly the
> item meant, its body included. From v3.0 it refuses no field's name in any of them, nor an answer ending in
> `(by …)`: each value is a line of its own.
>
> An answer given elsewhere (on a ledger entry) is written as an already decided `decide` item with no `Session`
> (`decided_file(title, ref, answers, default, words, today, by=None)`): `## <title>`, its `Context` the ref, `Due`
> today, its `Answers`, and `Decided: <today>[ by <by>] — <words>`, with **decide**'s refusals.
>
> **A snapshot against the ledger** (`parts_problems(item, entries, archived=())`, v2.6) lists, and never raises,
> why a `decide` item's `Parts:` does not match the ledger. `item` is an item file's text or a `BoardItem` (from
> v3.0; a v2 line before it), and its form is left to `item_file_problem()`. A text `parse_item()` reads as no open
> item, an item that is no `decide` or is decided, or one whose `Parts:` holds no id `parse_parts()` reads gives
> `[]`. One whose Context or parts the check `item_file()` shares faults gives `item: <that fault>` alone, the fault
> one of `context: not one entry and one decision` (a Context naming two entries, or going on past its gate, among
> them), `<id>: another repo's entry`, `<id>: not an id`, `<id>: the Context's entry` and `<id>: twice`; the kind,
> an empty list and the lifting answer are `item_file()`'s alone. Otherwise it reads `entries` and `archived` and
> judges as v2.6 says, word for word from "(id to text, open and archived alike" to "the lift when it is answered";
> the ledger is not in the item, so `item_file()` does not check these, and a writer that reads the ledger calls it.
>
> **The form the writers write** (v3.0) is a file `item_file()` or `decided_file()` composed, as it stands after any
> snooze, due, decide or reply. `item_file_problem(text)` names why a file is not in that form, or gives None, in a
> plain sentence opening with its rule's tag: a `## ` heading and one blank line; a header block of known fields,
> each once, in their order, spelled `**Name:** value` with one space; each value in its form (*Appendix: grammar*,
> *The item file*); a kind's rules (*A new item*; a decided file may carry any answers or none); a body of detail
> bullets; a Log, when there is one, last and holding replies alone; one blank line between the parts and one
> newline at the end. It never judges the detail block's words. `canonical_item_file(text)` rewrites a file into
> that form: line endings normalised to `\n`, the known fields in their order and spelled so, any other field after
> them in the file's order, one blank line between parts. It refuses a header block it would have to lose or repeat
> a line of (a line that is no field, a repeated field), and its result reads back the same item. No key rests on a
> file's spelling, so it rewrites any field.
>
> **The gate** is `board_problems(board, old)` (v3.0, both `Board`s, `old` read whole): first `README.md`'s
> `People:` and `Answered by:` problems (`people_problems()`, `answered_by_problems()` of the board, as
> `("README.md", problem)`), then `item_file_problem()`'s fault of each open item whose id no item of `old` (open or
> closed) has, as `(path, problem)`, and, on a new `decide` whose Context names a gate, `decision (<person>)`, a
> `People:` line that does not list that person. `old` may be a v2 board (a split's base) or None (every open item
> judged). An edit keeps an item's id, so an item is judged once, when it is added; damage a hand edit does to a
> file already there is `board_dir_problems()`'s to name. It refuses a v2 `board`.
>
> **The commit subject of a board write** is one line: `<tool>: <action> <id> <head>[ to <date> | : <answer>]
> (session <name>)` for the five edits, and `<tool>: append <id> <head> (session <name>)` for a new item (v3.0). The
> head is the item's text, bold dropped, at most 60 characters; `<name>` is the item's `Session` name, else the
> caller's, else `n/a`; a reply's words never appear. `subject_id(line)` reads the id back, or None. `edit_action()`
> reads the action back (v2.3). Subjects written before v3.0 still read: a v2 edit's and append's, with no id; those
> written before v1 by one consumer (`shiftlead: board|answer <head> (from <ref>)`, `shiftlead: board decide <ref>
> (person)`), as appends; and `<tool>: archive <n> closed items (session <name>)`, which no v3 writer writes.
> `subject_kind()` names a subject `edit`, `append`, `archive` or (a rank write) `queue`.

**10. *The board writer*.** Its first paragraph's library list becomes `plan_add`, `plan_edit`, `plan_fmt`,
`plan_split`, `plan_rank`, each returning a `Plan`, `show`, and `apply(plan)`. Its actions list is replaced by:

> - **`list`** — every open item's record (`item_record()`), read-only; the board a directory, the stub, or a v2 file;
> - **`show`** (v3.0) — the board for a person (`show_board(board, today, hidden=False)`): for each item
>   `needs_you()` gives, in its order, the line `*<id> · <class>*`, then the item's file as stored (a v2 item's line
>   and detail block), items separated by one blank line; with `--hidden`, the hidden open items after them, in the
>   board's order (*Reading a board*), each `*<id> · hidden until <date>*`. Read-only; no file holds it;
> - **`add`** — a new item (`item_file()`, any kind, its answers and detail block, `--hide-until`, `--doer`) at
>   `<board>/<id>.md`, the id drawn at random (redrawn, up to 8 times, while the directory or its archive holds it),
>   or `--id`'s, refused when it is no id, its date is not the item's `Added`, or it is held. With `--parts TD-a,TD-b`
>   (v2.6), a decide's snapshot (`item_file(parts=)`): the option may be repeated, each value is split on `,` and each
>   piece trimmed, and an empty piece is refused; `--parts` with `--decided` is refused, and so is `--ledger` without
>   `--parts`. The item's own refusals come first. Then the ledger is read (`--ledger <v2 directory>`, default
>   `ledger/` beside the board, its open and archived entries), and the write is refused, with every problem, when
>   `parts_problems()` names any, or when no ledger is found. With `--said` and `--by`, a question already answered:
>   its answer is the item's first reply. With `--decided`, an item the person decided elsewhere (`decided_file()`).
>   The write is refused when `board_problems()` faults the item it adds;
> - **`snooze`, `due`, `done`, `decide`, `reply`** — the five edits (`edit_item()`) of the open item `--id` names,
>   refused when no open item has it; `done`, and a `decide` that closes the item, write its archived file and
>   remove its open one as one write; `reply` takes its `--by` from the caller;

The **who answered** bullet stands. In **the decide lift** bullet, "default `ledger/` beside the board when it is a
directory" becomes "default `ledger/` beside the board", and "the board line `edit_line(…, "decide", label, by,
today, close=closes(item, label, entries after))`" becomes "the item file `edit_item(…, "decide", label, by, today,
close=closes(item, label, entries after))`, moved when it closes". The **`archive`** bullet goes. The **`fmt`**
bullet becomes:

> - **`fmt`** — `canonical_item_file()` of every open item file: the files it rewrites, and each file it cannot, with
>   why, reported and kept;
> - **`split`** (v3.0) — a v2 board (`--board`, its archive `--archive`, default beside it) split into its directory
>   (`split_board()`) always written into the directory beside it named the board's name without `.md` (which must
>   not exist), the directory the stub then reads as: every file written,
>   the v2 file replaced by `board_stub()` and its archive removed, as one write; `split_board_notes()`'s lines are
>   printed as warnings (`warnings` in `--json`). It prints no subject;

The **`rank`** bullet stands. After the actions list add:

> A write to a v2 board is refused (*split first*); `list` and `show` read one (v3.0). Every action resolves a stub
> as `load_board()` does: given the stub's path as `--board`, `add` and the five edits write into the directory
> beside it (v3.0).

In the paragraph after it, "`archive_subject()`, " is dropped; "A decide lift also reports" gains before it "Every
write that names an item reports its `id`."; and "A write of several files is both or neither:" becomes:

> A write of several files, and of the files it removes, is both or neither (v3.0: `done` and a closing `decide`
> remove the item's open file as they write its archived one, and `split` removes the v2 archive):

In the notes paragraph, "each names its line, as a write names one" becomes "each names its item's id",
`[{"line", "note"}]` becomes `[{"id", "note"}]`, and "`line n: ℹ <note>`" becomes "`<id>: ℹ <note>`".

**11. *The ledger as a directory*, *The caller does the I/O*.** "`ls(path)` returns the names of the files directly
in the directory `path` (no subdirectories), or None when `path` is not a directory;" becomes:

> `ls(path)` returns the names directly in the directory `path`: its files' names, and from v3.0 each
> subdirectory's name followed by `/`, which `load()` and `entry_path()` ignore (a v2.x caller's `ls` that lists
> files alone still reads a ledger); or None when `path` is not a directory;

**12. *Versions*, after the last v2.x paragraph** (v2.8's, which is released before B1 merges, D12), add:

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
> and `closed`, carries `doer` (an `act`'s doer, `null` for none), and its `text` is the item's words;
> `version_problem()` takes a `Board` and judges its
> `major` against `BOARD_MAJOR` (3), the board's own, read from every line of `README.md` (`board_major()`; the
> ledger's `FORMAT_MAJOR` is not changed here); `parts_problems()`, `decide_lift()` and `closes()` take an item
> file's text; `BOARD_PATH` and `BOARD_ARCHIVE_PATH` are `BOARD_V2_PATH` and `BOARD_V2_ARCHIVE_PATH`, beside
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

Its `Doer` sentence is the same whichever way TD-065 was decided (D12): it is true of v3.0 either way.

*Versions*' opening lines (round 4's F56) change too. "A ledger or board may declare its major version on a
preamble line, `Ledgerboard: 1`; none means 1." becomes:

> A ledger or board may declare its major version on a preamble line, `Ledgerboard: 1`; none means 1 for a ledger,
> and 2 for a board file (v3.0: a board's v1 and v2 are one format).

and after "A v2 ledger declares it in its `README.md`, which `load()` puts first." add:

> A v3 board declares it in its `README.md`, on any line outside an HTML comment (`board_major()`); a README that
> declares none reads as 3, and is named (*Reading a board*).

**13. *Appendix: grammar*.** The opening sentence's list gains "v3.0: the item file"; *The open item line (v2.3)*
becomes *The open item line (v2.3; a v2 board's, read only from v3.0)*. After it, add:

> ### The item file (v3.0)
>
> An item file as the writers write it (*The form the writers write*): a text `item_file_problem()` gives None for.
>
> ```ebnf
> item-file      ::= "## " item-text #xA #xA item-field ( #xA item-field )* ( #xA #xA item-body )? ( #xA #xA item-log )? #xA
> item-text      ::= nonspace ( char* nonspace )?
> item-field     ::= kind-field | added-field | session-field | context-field | parts-field | doer-field
>                  | due-field | hide-field | answers-field | lifts-field | decided-field | closed-field
> kind-field     ::= "**Kind:** " ( "decide" | "act" | "look" | "watch" | "fyi" )
> added-field    ::= "**Added:** " date
> session-field  ::= "**Session:** " head-name ( " on " head-name )?
> context-field  ::= "**Context:** " item-text
> parts-field    ::= "**Parts:** " entry-id ( ", " entry-id )*
> doer-field     ::= "**Doer:** " ( doer-repo | "team " person )
> doer-repo      ::= ( repo-part "/" )* doer-part
> doer-part      ::= [A-Za-z0-9_] ( [A-Za-z0-9_.-]* [A-Za-z0-9_-] )?
>                  | "." [A-Za-z0-9_-] ( [A-Za-z0-9_.-]* [A-Za-z0-9_-] )?
>                  | ".." [A-Za-z0-9_.-]* [A-Za-z0-9_-]
> due-field      ::= "**Due:** " date
> hide-field     ::= "**Hide until:** " date
> answers-field  ::= "**Answers:** " item-answer ( answer-sep item-answer )*
> lifts-field    ::= "**Lifts:** " item-label ( answer-sep item-label )*
> decided-field  ::= "**Decided:** " date ( " by " person )? " — " item-text
> closed-field   ::= "**Closed:** " date ( " — " item-text )?
> item-answer    ::= item-label " (default)"? ( " — " char* )?
> item-label     ::= label-start label-char*
> item-body      ::= body-line ( #xA body-line )*
> body-line      ::= " "* "- " char*
> item-log       ::= "**Log:**" ( #xA reply-line )+
> reply-line     ::= "- " date ": " reply-by ": " item-text
> reply-by       ::= [^#x20#x9:#xA] [^:#xA]*
> ```
>
> What the productions leave to prose: the fields stand in the order `item-field` lists them, each at most once, with
> `added-field` and `context-field` always; `parts-field` only on a `decide`, `doer-field` only on an `act`; a
> `due-field` on every kind but `fyi`; answers as *A new item* says a kind takes them, and a `lifts-field` only on
> a `decide`, each label one of its answers once and never `Go` alone; a decided file has no `session-field` and may
> carry any answers or none. An `item-label` holds no ` — ` and does not end in ` (default)`; a `reply-by` is at most
> 40 characters and ends in no whitespace; a `date` is a day of the calendar. A `doer-field` names a team only after
> the word `team` and one space, so `**Doer:** team` names the repo `team` (`parse_doer_value()` also reads a run of
> spaces or tabs there, a spelling `item_file_problem()` faults). A `doer-repo` is a `repo` whose last
> part, `doer-part`, is a `repo-part` that does not end in `.`. Every other production is the one above it of the
> same name (`date`, `head-name`, `entry-id`, `answer-sep`, `label-start`, `label-char`, `person`, `repo-part`,
> `nonspace`, `char`).

**14. The rest of *The board*, and what else names a removed function.** Text 2's second paragraph says a line's
text, key and writers are v2's. Each sentence below still reads as the only form, or names a function v3.0 removes
(round 1's enumeration); each gets its substitution (B2's for readers, B5's for the removed writers), each bullet
tagged with its build (round 6's F77):

- *Notes on a hide* (`item_notes(item, today)`): "of a parsed open item as `parse_board()` gives it" becomes "of an
  open `BoardItem` of either major (`parse_item()` or `parse_board()`)". B2.
- *`Parts:`*: "and it is part of the item key, since a changed snapshot is a different question" gains "(v2)"
  before its period; "`item_line(parts=)` and `board.py add --parts` write it" becomes "`item_file(parts=)` (v3.0;
  `item_line(parts=)` before it) and `board.py add --parts` write it". The "(v2)" is B2's, the writer substitution
  B5's.
- *`Doer:`* (v2.8's paragraph after *`Parts:`*, TD-065's text 1; only when TD-065 shipped in v2.8, D12): "It is
  part of the item key" becomes "On a v2 line it is part of the item key"; "`item_line(doer=)` and `board.py add
  --doer` write it" becomes "`item_file(doer=)` (v3.0; `item_line(doer=)` before it) and `board.py add --doer`
  write it"; and it gains at its end "In an item file (v3.0) it is the header field `Doer` (*The item file*), a bare
  value read by `parse_doer_value()`; `parse_doer()` reads a v2 line's." Its last sentence is B1's, landing with
  the header field; the two substitutions are B5's, with the writer items. When TD-065 was closed, `SPEC.md` holds
  no such paragraph and this bullet lands nothing.
- *Trailing fields*, `Lifts:`: "It is part of the item key" becomes "On a v2 line it is part of the item key";
  "`item_line(lifts=)` refuses one and `item_problem()` faults one" becomes "`item_file(lifts=)` refuses one and
  `item_file_problem()` faults one (v3.0; `item_line()` and `item_problem()` before it)". The `Decided:` bullet
  gains at its end: "In an item file it is `Decided: <date>[ by <person>] — <label>` (*The item file*)." The key
  sentence and the `Decided:` sentence are B2's, the writer substitution B5's.
- *The bold head*: gains "In an item file (v3.0) it is read from the heading, as from a line; a heading with no bold
  run has none." B1, with `bold_head()` reading a heading.
- *Replies*: gains "In an item file (v3.0) a reply is a Log line (*The item file*), and none of this paragraph's
  limits on its words holds: they hold for a v2 line." B2.
- *The detail block*: gains "In an item file (v3.0) it is the body (*The item file*)." B2.
- *`People:`*: "It is read only above the board's first item" becomes "It is read only above a v2 board's first
  item, and anywhere in a v3 board's `README.md`"; *`Answered by:`*'s "It is read as `People:` is" then holds for
  both. B2.
- *A closed item*: "(`parse_closed_items(content)`, v2.4, of a board or its archive …)" gains after it "On a v3
  board a closed item is a file under `archive/` with its `Closed:` (*Reading a board*)." B2.
- *The decide lift*: `decide_lift(item_line, entries, …)` becomes `decide_lift(item, entries, …)`, `item` an item
  file's text or a `BoardItem` (v3.0; a v2 line before it), and "the base item line" becomes "the base item". B2.
- *Versions*' past paragraphs (v2.3's to v2.8's) stand as written: each says what that release shipped, and the
  names it gives (`item_line()`, `item_problem()`, `canonical_item()`, `archive_closed()`, `edit_line()`) were that
  release's. Text 12 says what v3.0 removed. No build: nothing lands.
- *Appendix: grammar*, *The open item line*: its opening sentence's "a line `item_problem()` gives None for" gains
  "(v2.x; v3.0 removes `item_problem()`)". B5.

**The search.** Each build ends by searching `SPEC.md` for the names v3.0 removes or renames whose text that build
lands, in the sections that text rewrites, and finding each only in a *Versions* paragraph or a v2-tagged sentence
(round 2's F34: a name another build's text still holds is that build's to search). The names, by the section
where `SPEC.md` holds them today:

- **B1** (text 9 but its *gate* paragraph): *Edits* for `item_line`, `decided_line`, `item_problem`,
  `canonical_item` and `archive_subject` (`edit_line` is not in *Edits*: `SPEC.md` holds it in *The merge gate's
  verdicts*, B4's, and *The board writer*, B3's).
- **B2** (texts 2–6, 8's *Reading a board* and *Damage*, 9's *gate*, 11, 14's reader items): *The board* but its
  *Parts:*, *Trailing fields* and *The merge gate's verdicts* paragraphs, for `ARCHIVE_AT`, `archive_closed`,
  `closed_items` (as a whole name: `parse_closed_items` stays) and `item_line` (the last in *The gate sweep* and
  *The decide lift*).
- **B3** (text 10 but `split`): *The board writer* for `item_line`, `decided_line`, `edit_line`, `canonical_item`,
  `archive_closed`, `archive_subject`, `--line`, `--expect` and `--under`.
- **B4** (text 7): *The merge gate's verdicts* for `BOARD_PATH`, `BOARD_ARCHIVE_PATH` and `edit_line`.
- **B5** (texts 1, 8's *Migration*, 10's `split`, 12, 14's writer items) runs the full search: all of `SPEC.md`, for
  every name above (`item_line`, `decided_line`, `edit_line`, `item_problem`, `canonical_item`, `archive_closed`,
  `archive_subject`, `ARCHIVE_AT`, `closed_items`, `BOARD_PATH`, `BOARD_ARCHIVE_PATH`, `--line`, `--expect`,
  `--under`), each found only in a *Versions* paragraph, a v2-tagged sentence or text 12.

## Fixtures

All invented names (`pat`, `sam.lee`, `acme/widgets`, `ops`, `host-a`, sessions `w-9`, `lb-x`).

- **`fixtures/item/cases.json` and `expected.json`** (a new runner kind, `item_cases`, beside `edit_cases`):
  - `parse`: a file of each kind and its fields (the runner's `item_fields()`: the `BoardItem`'s fields by name, not
    `item_record()`, whose B1 change is `doer` alone, D4); a heading, a Context, an answer, a detail line and a
    reply each holding `Context:`, `Due:` and `Decided:` as words (the case S3 exists for), read as words;
    `**due:**` and `**hide-until:**` read as `Due` and `Hide until`; a repeated field (the first wins); an unknown
    `**Owner:**` field (ignored, in `fields`); `Decided:` with and without `by`, and a label ending `(by Friday)`
    read whole; `Closed:` with and without a why; a `Decided:` and a `Closed:` not in their form (not decided,
    open); an `act` with `**Doer:** acme/widgets` and one with `**Doer:** team ops` (`doer` in its fields); a Log
    line in another shape and one with empty words (no reply); a CRLF file; a file with no heading (None, and its
    problem in `board_dir`);
  - `compose`: `item_file()` for each kind; a text, a context, an answer, a detail value and a `said` holding
    `Context:` and `Lifts:`, each written (the refusals that go); an `act` with a `doer`; refused: a two-line value,
    a host with no session, an empty text, a `decide` with one answer, a `look` with other answers, an `fyi` with a
    `due`, `lifts` naming a waiting-only answer, `parts` on an `act`, `doer` on a `decide`, a `doer` of `acme.`;
    `decided_file()` with and without `by`, and an answer ending `(by x)`, written;
  - `edits`: each of the five edits on a file, the unknown field and the body kept byte for byte; `due` and `snooze`
    adding their field in its place, one of them with an unknown field between its neighbours (placed after the last
    known field before it); `decide` replacing an earlier `Decided:`; `decide` with `close`, lifting and
    waiting-only; `reply` opening the Log and appending to it; an edit of a CRLF file (its new line `\r\n`, every
    other byte kept); refused: any edit of a closed item, a reply `by` holding `:`, a reply with blank words,
    `decide` with `close` and a work order;
  - `problems`: `item_file_problem()` passing each writer's file, and faulting fields out of order, a field twice,
    an unknown field, `**Due:**` spelled `**due:**`, a `Parts:` on an `act`, a `Doer:` on a `decide`, a Log not
    last, a body line that is no bullet (the messages pinned);
  - `canonical`: reordered and respelled fields rewritten, an unknown field placed after the known ones, a CRLF file
    normalised; refused: a header line that is no field, a repeated field;
  - `ids`: `item_id()` accepting `2026-11-11` and `3f9a2c1d`, refusing `2026-02-30`, `3F9A2C1D` and seven digits;
    `item_path()` open and closed (`archive/2026-11/<id>.md` for a close on 2026-11-30, `archive/2026-12/` on
    2026-12-01); `key_id()` of a key whose hash a consumer persisted (the case gives the line's text and the 8 hex
    digits that `sha256(item_key("- [ ] " + text))[:8]` gives, computed once by the case's author);
  - `subjects` (moved from `edit/`, with its `subject_kinds` and `edit_actions`): `subject()` for each action and
    `append` with an id, and with `id=None` (the v2 subject, until B5); `subject_id()` of a v3 subject, of a v2 one
    (None) and of a legacy append; `edit_action()` and `subject_kind()` of both majors' subjects;
  - `gate`: `board_problems()` over `Board`s (moved from `edit/`'s `board_problems`): an added item faulted, an edited
    one not, a new `decide` whose gate's person is not on `People:`, a `README.md` holding a `- [ ]` line above its
    `People:` (read), `old` a v2 board (the split PR: nothing new), `old` None, and a v2 `board` refused.
- **`fixtures/board/<case>.v3/`** for each v2 case `fixtures/board/` holds when B5 is built (today `basic`,
  `answers`, `hidden`, `people`, `lifts_parts` and `shared_part_left_open`), and a new `twins_across`, an open line
  on the board and its closed twin in the archive: its split directory. A new runner kind, `board_v3_case` (B5),
  beside `v2_case`: `split_board()` of the case's text gives the directory file for file, and `load_board()` of it
  gives the case's expected JSON, the JSON the v2 read gives (`covers`, the records, and `needs_you`), compared as
  D6's *Comparing two reads* says (records keyed by `id` without `path` and `line`; `covers` as a list sorted by id;
  `needs_you`'s **tie groups** as sets, the groups in order), since a v2 board's order is its lines' and its split's
  is id descending. The v2 cases' JSONs gain `doer` (None) in each record at B1 and are regenerated at B2:
  `board_case` reads through `load_board()`, its records gain `id`, `path`, `added`, `context` and `closed` and keep
  `line` (B5 drops it), their `text` the item's words, `needs_you` rows are `[id, class, days]`, `keys` become the
  items' ids and `closed` the closed records; `twins_across` reads one closed item.
- **`fixtures/board_dir/<case>/`** (a new kind, `board_dir_case`: `board/` and `expected.json`, holding
  `load_board()`'s `major`, items, closed items, people, `needs_you` and `problems`, and `board_dir_problems()`):
  `months` (closed items across three months, read whole and with a `since` that reads two); `ties` (undated,
  unreadable-due and `fyi` items, and two items of one due date, some added on one day and some on others, ordered
  by id descending: the case that pins v3's tie order); `field_words` (headings and contexts holding field names);
  `unknown_field`; `stub` (the v2 path holding the stub, read as the directory); `stub_no_dir` (empty, the stub
  named); `damage` (a name that is no id, an `Added` not the id's date, a missing `Added`, a `Closed:` not in its
  form, a closed item outside `archive/`, a file inside it with no `Closed:` (read as closed), a wrong month, one id
  twice (an open and an archived copy, the archived read; two archived copies, the later month's read), a file
  `read()` gives None for, a file with no heading, a header-block line that is no field (kept, named); round 6's
  F74: a file directly in `archive/`, a directory `archive/misc/`, a directory `archive/2026-13/`, a subdirectory
  `notes/` of the board, a directory inside a month, each named once and not read; F76: a `Kind: banana` item (a
  to-do, in `needs_you`), a `Hide until` that is no day (shown), a `Parts` not in its form (no parts), a `Doer` not
  in its form (no doer), each kept in `fields` and named; F79: a `Doer: team  ops` (read as the team `ops`,
  named));
  `readme_missing` and `readme_v2` (`major` 3 and 2, each named); `file_v3_items` (a file declaring 3 holding items:
  read as v2, `major` 3, named); `missing` (no path: empty, `major` None); `readme_item_line` (a `- [ ]` line in
  `README.md` above `People:`, which is still read); `newer` (a README declaring `Ledgerboard: 4`:
  `version_problem(board)` names it); `readme_major_late` (a README whose `Ledgerboard: 3` stands below a `- [ ]`
  line of prose: `major` 3, read by `board_major()`); `v2_undeclared` (a v2 file with no `Ledgerboard:` line:
  `major` 2, no problem); `v2_duplicate_open` (a v2 file with two open lines of one id: both read with that id, the
  id named once in `problems`, and `board_dir_problems()` giving `Board.problems` alone).
- **`fixtures/board_split/<case>/`** (a new kind, `board_split_case`: `board.md`, optional `archive.md`,
  `expected.json` holding the files or the refusal, and `split_board_notes()`): `twins` (an open and a closed line
  of one key, on the board and across board and archive, each one closed item, its fields and body the closed line's
  although the open twin's detail block differs); `sections` (the `## Needs the user` and `## In-flight` headings:
  an earlier `## ` heading kept and only the one nearest the first item dropped; the README's prose kept; its links:
  an inline relative link, an image, a reference definition, a `#anchor`, an `https:` and a `mailto:` link, a
  `/rooted` path and a link inside a code span, only the relative three given `../`; its notes listed); `hand_line`
  (words a hand edit left outside the fields carried into the heading, its final period kept: words after the `Due`
  date, `Due: 2026-11-08. also ping sam.`, and after a `Hide until` date, each joined to the text by one space as
  `item_words()` gives them (F80); a bold head kept as written, a `Closed: D — lifted.` written `— lifted`, a `Context:` losing its final period); `decided_by` (a
  `Decided:` with and without `(by …)` rewritten); `persisted_key` (the id's digits equal to the hash ShiftLead's
  `key()` gives, for a column-0 line, an indented line and a `[x]` line); refused: `undated`, `duplicate_open`,
  `two_closed`, `two_indents` (one text at two indents, one id), `prose_between_items`, `already_v3`,
  `closed_undated` (a `[x]` line with no readable `Closed:` date).
- **`fixtures/board_writer/`**: new cases over a v3 directory: `add_v3`, `add_id_given`, `add_id_taken` (exit 1),
  `add_id_wrong_date` (exit 1), `add_said`, `add_decided`, `add_doer` (an `act` with `--doer`), `add_via_stub`
  (`--board` the stub's path: the file written in the directory beside it), `snooze_id`, `due_id`, `done_moves` (the
  file under `archive/<month>/`), `decide_close_moves`, `decide_work_order` (stays open), `reply_id`,
  `edit_no_such_id` (exit 1), `edit_closed` (exit 1), `write_v2_refused` (exit 1; its message gains *split first*
  at B5), `list_v2`,
  `list_stub`, `show` (a CRLF item file among its items), `show_hidden`, `show_v2` (a detail block indented four
spaces, printed at four), `show_empty` (no item to show: no output),
`fmt_v3` (B3: it needs only B1's `canonical_item_file()`); and, in
  B5, `split` and `split_exists` (exit 1). Each existing case is rewritten over a directory (`--id` for
  `--line`/`--expect`), or removed where its rule went (`archive`, `archive_new_file`, `archive_none`,
  `add_empty_section`, `add_fyi_no_heading`, `add_refused_field`); `add_detail_recommended_doubled` is rewritten,
  its refusal standing. The runner's `writer_case` needs no change: `tree()` reads nested files.
- **`fixtures/verdict/`**: the shared base tree holds a v3 board; new cases `v3_lift_open` (a work order, stays
  open), `v3_lift_closes` (moved to `archive/`; the case's file list names the two paths, no rename, and the verdict
  comes from the trees), `v3_lift_two_items` (review), `v3_lift_wrong_month` (review), `v3_other_repo`,
  `v3_tripwire_lifted`, `v3_uncovered_new_decide`, `v2_lift` (`lift-board-v2`), and `split_pr` (a v2 pair at the
  base, the directory at the head: no tripwire flag). The existing cases move their board into the directory with
  the same items.
- **`fixtures/sweep/`**: `cases.json`'s boards may name a `dir` (a v3 board) in place of `board` and `archive`; the
  runner reads either through `load_board()`, whole (a change to `sweep_cases`), and its rerun step closes by id and
  files with `item_file()`; one v3 board and one v2 board in the set, and a v2 board beside its split giving the same
  `to_file`, `to_close` (ids) and `lifts`, compared as D6's *Comparing two reads* says (`to_close` and `lifts` as
  lists sorted by id); an `audit_old` case (the `; board <repo>` audit's decided item closed in a
  month before the Log line's, found); an `owing_old` case (an answer owing a lift archived months back, which keeps
  the unlifted act open).
- **`fixtures/lift/`**: `decide_lift()`'s items become item files.
- **`fixtures/grammar/cases.json` and `expected.json`**: a start `item-file`, judged by `item_file_problem()`,
  with a group for every production the start reaches (round 6's F78: `tests/test_grammar.py` asserts the groups
  are exactly `names_used()` of the start): `item-file`, `item-text`, `item-field`, each field production,
  `item-answer`, `item-label`, `item-body`, `body-line`, `item-log`, `reply-line`, `reply-by`, and the shared ones it
  reaches (`date`, `digit`, `char`, `nonspace`, `head-name`, `entry-id`, `repo`, `repo-part`, `person`, `person-part`,
  `answer-sep`, `label-start`, `label-char`, `doer-repo`, `doer-part`, and any other `names_used()` gives), each with
  an accepting and a refusing fixture: among them a context holding `Due:` (accepted),
  `**Decided:** 2026-11-12 by pat — Go (by Friday)` (accepted), `**Doer:** team ops` and `**Doer:** acme/widgets`
  (accepted), `**Doer:** acme.` (refused), a field out of order and a reply-by holding `:` (refused).
- **`fixtures/edit/cases.json`'s groups**, each placed: `compose`, `edits`, `item_problems`, `canonical_items` and
  `archive_subjects` retire with the v2 writers (B5); `subjects`, `subject_kinds` and `edit_actions` move to
  `item/`'s `subjects` (B1); `board_problems` moves to `item/`'s `gate`, over `Board`s (B2); `item_keys` stays (the
  v2 reader and `key_id()`'s input); `item_notes` stays, its items given as `BoardItem`s of either major (B2);
  `bold_heads` stays, gaining a heading case (B1); the rest (`today`, `predicates`, `versions`, `not_right_forms`,
  `not_right_fills`, `queue_subjects`, `implicit_keys`, `key_orders`, `midpoints`, `rank_reads`, `rank_writes`,
  `rank_paths`, `components`, `respaces`, `split_notes`) are untouched.
- **Retired**: `fixtures/archive/` (with `archive_closed()`), and the `edit/` groups above (B5).
- **The runner** (`fixtures/run.py`): `fs_ls` lists subdirectories with `/`; the kinds `item_cases`,
  `board_v3_case`, `board_dir_case` and `board_split_case` join `cases()`; `board_case`, `sweep_cases` and
  `lift_cases` read through `load_board()`; `archive_case` and the retired groups of `edit_cases` go.

**Unit tests** (`tests/`): a property test that `split_board()` then `load_board()` gives every fixture board's items
back; `tests/test_item_gate.py`'s compose and edit properties over item files; `tests/test_grammar.py` reading the
new start.

## The builds

Each is filed `Part of: TD-070` on Paul's Go after the rounds, and lands its SPEC text, code and fixtures together.
**Preconditions of B1**, both the person's (D12): TD-065 is decided before B1 starts, either shipped (its build
merged, so in v2.8) or closed as superseded by the v3 field; and whatever `main` carries past v2.7 (today TD-079 and
TD-080, and TD-065's build if it ships) is released as v2.8 before B1 merges. No release is cut between B1 and B5. Each build
leaves `main` green: where a later build retires a v2 name an earlier build would break, the earlier build keeps it
working (a shim) and B5 removes the shim. **What a record shows** changes at B1 (`doer`), B2 and B5 alone (D4, round
2's F33, round 3's F46);
each build below names the expected JSONs whose records it regenerates. **Each build's `SPEC.md` search** is text
14's, for that build's names; B5's is the full one.

**B1, the item file.** D3, D4, D7's module half. Location: `ledgerboard/__init__.py` (`ITEM_ID_RE`, `item_id()`,
`key_id()`, `item_path()`, `parse_item()` (filling `words` with the heading), `BoardItem`'s new fields,
`parse_doer_value()`, `BoardItem.doer`, `item_record()`'s `doer`, `item_file()` with `doer`,
`decided_file()`, `edit_item()`, `item_file_problem()`, `canonical_item_file()`, `subject()` gaining `id=None` (None
gives the v2 subject the v2 writers still call), `subject_id()`, `bold_head()` reading a heading), `SPEC.md` (text
8's *The item id* and *The item file*, 9 but its *gate* paragraph, 13), `fixtures/item/` (but `gate`),
`fixtures/grammar/`, `fixtures/edit/`'s subject groups moved, `fixtures/run.py` (`item_cases`, `item_fields()`).
Text 8's `parse_item()` paragraph lands without its closing `item_record()` sentence, its *The item file* without
the clauses naming `board_dir_problems()`, and text 9 without its *snapshot* paragraph (each B2's: *The SPEC text
the build lands*, round 4's F59, round 6's F77); text 14's *bold head* bullet is B1's.
**Records:** `item_record()` gains `doer` and nothing else (None for every v2 item); the expected JSONs it
regenerates are `fixtures/board/*.json` and `fixtures/board_writer/list/expected.json`, each record gaining
`"doer": null`. When TD-065 shipped in v2.8, the key is v2.8's already, and B1 regenerates no record (D12).
`fixtures/edit/expected.json` changes only by the groups that move to `item/` and `bold_heads`' heading case.
**`Doer`:** B1 lands the whole v3 field whichever way TD-065 was decided (D4, D12: `parse_doer_value()`, text 8's
*The item file*, text 13's `doer-field`, `doer-repo` and `doer-part`, and text 14's `Doer:` bullet's last sentence
when TD-065 shipped). When TD-065 shipped, `BoardItem.doer` and the record's `doer` are v2.8's and stay, and
`doer-repo` and `doer-part` move from *The open item line*'s block into text 13's (a production is defined once).
Done when: TD-065 is shipped or closed, v2.8 is tagged, the precheck is green, every fixture above passes, and text
14's B1 search finds its names only where it allows.

**B2, reading.** D5, D6, D9. Location: `ledgerboard/__init__.py` (`Board`, `load_board()`, `item_words()`, the
twin rule across board and archive, the stub's reading, the duplicate-id read, `Board.problems`,
`board_dir_problems()`; `BOARD_MAJOR = 3`, `board_major()`, `version_problem()` taking a `Board`; `needs_you()`,
`covers()`, `sweep()` (whole boards), `board_problems()`, `board_people()`, `answered_by()`, `people_problems()` and
`answered_by_problems()` over a `Board`, each still taking a v2 board's text as before until B5, so `board.py` runs
unchanged until B3; `parse_board()` filling every new `BoardItem` field and the ids; `item_record()`'s B2 change
(D4: its `text` reading `words`); `parse_board()` filling `words` (`item_words()`) and keeping `text` the line's
text after its tick, as today (D4's *`words` and `text`*); `_item_gate()` taking a `BoardItem` and reading its
`context`, and `closes()` given a `BoardItem` reading its fields; `_dict_ls()` listing
subdirectories (D6); `parts_problems()`, `decide_lift()`, `closes()` over a file, each still taking a v2 line until
B5), `SPEC.md` (text 2 (without the words B5 adds), 3–6, 8's *Reading a board* (without "and no `line`", B5's),
its *Damage*, its `parse_item()`
paragraph's `item_record()` sentence and *The item file*'s `board_dir_problems()` clauses, 9's *gate* and *snapshot* paragraphs, 11, 14's reader items),
`fixtures/board/` (regenerated, `twins_across`), `fixtures/board_dir/`, `fixtures/item/`'s `gate`,
`fixtures/sweep/`, `fixtures/lift/`, `fixtures/run.py` (`fs_ls`, `board_dir_case`, `board_case`, `sweep_cases`,
`lift_cases`; the runner's two reads of `BoardItem.text` move off it, so B5's removal changes no expected JSON:
`lift_cases`' `closed_items` prints `words`, and `sweep_cases`' `covers` the item's id).
`load()`, `entry_path()` and `v2_problems()` need no change for `fs_ls`'s new `archive/` name: each
takes only the names `ENTRY_FILE_RE` (`^TD-(\d+)\.md$`) matches. **Records:** `item_record()` gains `id`, `path`,
`added`, `context` and `closed`, keeps `line`, and its `text` becomes the item's words; the expected JSONs it
regenerates are `fixtures/board/`'s `answers.json`, `basic.json`, `hidden.json`,
`lifts_parts.json`, `people.json` and `shared_part_left_open.json` (records, `needs_you` rows by id, `keys` as ids,
`closed` as records), and `fixtures/board_writer/list/expected.json` (`board.py list` prints `item_record()`; no
other writer case prints a record); besides records, `fixtures/sweep/expected.json` (`to_close` by id),
`fixtures/lift/expected.json` (`decide_lift()`'s items as files) and `fixtures/edit/expected.json`
(`board_problems` moved to `item/`'s `gate`, `item_notes` over `BoardItem`s) regenerate. Done when: the precheck is
green, those fixtures pass, every existing `fixtures/verdict/` case passes unchanged (the verdicts still read v2
trees, and a v2 item's `text` is still its line), and text 14's B2 search finds its names only where it allows.

**B3, the writer.** D2's moves, D7's writer half, D8. Location: `ledgerboard/__init__.py` (`show_board()`, pure
over a `Board`, its bytes as D8 gives them; `parse_board()` keeping `detail_source`, D8; round 4's F54, round 5's
F70), `ledgerboard/board.py` (`plan_add` by id, no
`under`, `--doer`; `plan_edit` by id, with the move; `show`; `plan_fmt` over files; the v2 refusal; `--id`,
`--hidden`; the `archive` action, `--line`, `--expect` and `--under` gone; a board read through `load_board()` and
checked with `version_problem(board)`, `read()` keeping `version_problem(text)` for the ledger and the rank file;
`who_answered(board, by)` over a `Board`; one file-system `ls` listing subdirectories with `/`, used by the board's
read and by `read_ledger()`; the usage docstring), `SPEC.md` (text 10 but `split` and "(*split first*)"), `fixtures/board_writer/` (but
`split`, `split_exists`). **Records:** `item_record()` is untouched; the `list` cases (`list`, `list_v2`,
`list_stub`) print B2's records. Done when: the precheck is green, every writer case passes, and text 14's B3
search finds its names only where it allows.

**B4, the merge gate's verdicts.** D10. Location: `ledgerboard/__init__.py` (`BOARD_DIR`, `BOARD_V2_PATH`,
`BOARD_V2_ARCHIVE_PATH`, `_tree_ls()` listing subdirectories, `_tree_board()`, the board changes read from the two
trees, `tripwire()`, `lift_pr_verdict()`, `uncovered_decisions()`, each reading `_item_gate(item)` of a
`BoardItem` where it read `_item_gate(it.text)`, D4), `SPEC.md` (text 7), `fixtures/verdict/`.
**Records:** none change. Done when: the precheck is green, every verdict case passes, and text 14's B4 search
finds its names only where it allows.

**B5, migration and the release's removals.** D11, D12. Location: `ledgerboard/__init__.py` (`split_board()`,
`board_stub()`, `split_board_notes()`; `item_line()`, `decided_line()`, `edit_line()`, `item_problem()`,
`canonical_item()`, `archive_closed()`, `archive_subject()`, `ARCHIVE_AT`, `closed_items()` removed, and B1's and
B2's shims: `item_record()`'s `line`, `subject()`'s v2 form, the readers' v2-text and v2-line arguments,
`BoardItem.text`, today's `_item_text()` and `_item_gate()`'s string form (D4's *`words` and `text`*, their callers
gone; `words` keeps its name); `parse_board()` filling no `text`; the ledger's `FORMAT_MAJOR` untouched),
`ledgerboard/board.py` (`split`), `SPEC.md` (text 1, 8's *Migration* and its
*Reading a board*'s "and no `line`", 2's words B2 left out, 10's `split` and "(*split first*)", 12, 14's writer
items),
`fixtures/board_split/`, `fixtures/board/<case>.v3/`, `fixtures/board_writer/`
(`split`, `split_exists`, and `write_v2_refused`'s message gaining *split first*), `fixtures/run.py` (`board_split_case`, `board_v3_case` with its tie groups compared as
sets; `archive_case` and the retired `edit_cases` groups removed), `fixtures/archive/` and the retired
`fixtures/edit/` groups, `tests/`. **Records:** `item_record()` loses `line`; every expected JSON holding a record
regenerates: `fixtures/board/*.json`, `fixtures/board_dir/*/expected.json`, and `fixtures/board_writer/`'s `list`,
`list_v2` and `list_stub`. Done when: the precheck is green, every fixture passes, text 14's full search of
`SPEC.md` finds no removed name outside the places it allows, and `board.py split` of this repo's own board, run on
a scratch copy, reads back.

Order: B1, then B2, then B3 and B4 (either order), then B5. Then v3.0's release with TD-078's half (Paul's), this
repo's own split, and each consumer's entry (agent-cadence's first).

## Not in this design

The ledger's own v3.0 removals (`Waits`, `Taken by`, the old decision form, a header `Resolved`, `migrate`) and the
archived entry's writer route are TD-078's. When v3.0 is cut, and what else it carries, is Paul's.

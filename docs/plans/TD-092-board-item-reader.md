# TD-092: the board's item file, its id and the v2/v3 reader (TD-070's B1 and B2)

**Status:** Draft 4, 2026-11-13 (session lb-designer): round 2's fact-check (R29) raised one build-changing finding
(F196, `Board.path`) and six minor (F197–F202), all applied. Draft 3: round 1's design review (R28) raised three
build-changing findings (F190–F192) and three minor (F193–F195), all applied with the author's rulings
(`Board.form`; a v2 `context` without its replies; B3/B4 tags). Draft 2: round 1's fact-check (R26) raised four build-changing
findings (F175–F178) and nine minor (F179–F188), all applied. Draft 1 was split from TD-070's plan (draft 11) at
Paul's Hold (2026-11-13), his Go on this scope (#275). Class: **wide** (a new major of a vendored, published format,
read by both consumers; cap 6 rounds, cadence.md §4.8). The record is docs/reviews/TD-092.md. Draft 1's text was
TD-070's plan's, moved unchanged; that plan's nine rounds are in its Status, and their findings, F1–F174, are in
docs/reviews/TD-070.md, cited here by id where the moved text cites them. TD-092's own record continues the
numbering (R26, F175 on), so an id names one finding across both plans.

**Entry:** [TD-092](../ledger/TD-092.md), `Part of` [TD-070](../ledger/TD-070.md). **Source:** TD-092's Fix (the
scope, Paul's Go, #275); [TD-070's plan](TD-070-board-directory.md), draft 11, from which every section here but
*The problem* and *Not in this design* is moved (its scope S1–S10, Paul's Go of 2026-11-11, kept as each
decision's source); `SPEC.md` *The board*, *Edits*, *The ledger as a directory* (the precedent), *Ledger entries
and their edits* (the grammar the item file reuses); both consumers' pinned code, read 2026-11-11 (cited by file
and function). A citation here of what this plan does not hold (D1, D8, D10, the parts of D2, D7, D11 and D12
that *Decisions* names, texts 1, 7, 10 and 12, *Consumers*, B3–B5) is to TD-070's plan.

## The problem

The full problem is TD-070's plan's (*The problem*). In short: a v2 board is one Markdown file and every new item
is written at one place in it, so two PRs that each add an item always conflict; and a `decide` item is a line of
up to a kilobyte or more, with a detail block and a life of its own, which is an entry's shape. The line carries
costs an entry does not: its identity is its text (the item key, which consumers persist), its fields live inside
prose (a Context ends where the next field name begins, so the writer refuses any value holding a field name),
and two copies of one item are the merge rule (the open-and-closed twins). B1 and B2 are the half of v3.0 a
reader meets first: an item file named by a stable id, in an entry's grammar, and a reader that reads a v3
directory and a v2 board alike, so a consumer can vendor v3.0 before it splits its board.

## What is already settled

- **The scope** of the whole design (S1–S10, Paul's Go, 2026-11-11) is TD-070's plan's; this plan's is TD-092's
  Fix (Paul's Go, 2026-11-13, #275).
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

Whether to do it at all (S1) is TD-070's plan's (*Options weighed*: the directory).

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

Numbered as in TD-070's plan, so that citations across both plans and docs/reviews/TD-070.md resolve. D1, D2's
moves on close and `README.md`'s stamps, D3's writer half (`board.py add`'s draw, `--id`, `--today`; round 1's
F183), D7's writer half (`board.py`), D8, D10, D11's split and D12's release stay there.

**D2. The layout (S4), as the reader sees it.**

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
`Closed:` date (`item_path(id, closed=None)`: `closed` the `Closed:` date as a `YYYY-MM-DD` string, None for an open
item; an `id` `is_item_id()` does not pass raises `ValueError`; round 1's F195; so does a `closed` that fails
`_real_day()`, malformed or no real day; round 2's F202). Every preamble line is read from
`README.md` alone.

The moves on close, and `README.md`'s stamps, stay in TD-070's plan, D2.

**D3. The item id (S2).** `YYYY-MM-DD-<8 hex>`: the item's `Added` date, a hyphen, eight lower-case hex digits
(`ITEM_ID_RE`, `[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9a-f]{8}`, matched with `fullmatch`, so no trailing newline and
no non-ASCII digit passes, as `PART_ID_RE`'s `[0-9]` reads; round 1's F185; the date a real day). **One predicate
says what an id is** (round 1's F195): `is_item_id(s)`, `ITEM_ID_RE`'s `fullmatch` and its date a real day
(`_real_day()`). `item_id(added, nonce)` formats and refuses anything `is_item_id()` does not pass; `parse_item()`'s
`id` (D6) and rule 11's names read through it too, so `2026-02-30-abcd1234.md` is a name that is not an id. The
module draws nothing. The writer half that follows is B3's
(TD-070's plan, B3; round 1's F183): `board.py add` draws the nonce (`secrets.token_hex(4)`) and draws again,
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
**Session:** s-alpha on host-a
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
  adds no period. A bold run in it is the item's bold head (*The bold head*, read from the heading). A heading is
  read whole (round 9's F162): `bold_head(words, heading=True)` skips `reply_span()`, which on a line cuts a ` —
  <name>, <date>: ` tail as a reply, so a heading shaped so (`Ask — pat, 2026-01-05: **hm**`, whose bold run a line's read cuts with the
  reply, giving None) keeps its bold head, `hm` (round 9's F167). Every caller holding a `BoardItem` passes its `words` so, for both majors (a v2 item's words hold no reply,
  D11's span).
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
  person's name; `team` alone names the repo `team`). Its reader is v2.8's `doer_value(value)` (TD-065's, round 5's F68), which B1
  reuses rather than adding a second reader (round 8's F112): it reads a bare value, as the header field holds it (no
  final period, no line around it), and gives `("repo" | "team", name)` or None for a value outside the form;
  `parse_item()` adds the value as written, so a v3 item's `BoardItem.doer` is `(kind, name, value)`, the shape v2.8's
  `parse_doer()` gives. It reads a team (round 6's F79): `team`, a run of spaces or tabs, and a person's name, so `team  ops` reads as the
  team `ops`, its `value` as written; `item_file_problem()` and `board_dir_problems()` (rule 14) fault any spelling
  but one space, and the writer writes one. `BoardItem.doer` is that
  tuple for a v3 item, and `item_record()`'s `doer` a dict of it (below), or None. TD-065's `parse_doer(text)`, in
  v2.8 (D12), stays a v2-line function (it finds ` Doer:` on a line, reads to the field's final period and calls
  `doer_value()`), which the v2 half of `load_board()` uses for a v2 item. TD-065's build has merged (TD-083,
  5b036e4; D12).
- **A field on a kind that does not take it** (round 9's F147, the ruling; reopening F128) is read as v2 reads it:
  `parse_doer()` reads `Doer:` on any kind (its docstring: "read on any kind (`item_problem()` faults it on all but
  an act)"), and `parse_parts()`, `parse_lifts()` and `parse_answers()` read theirs on any kind, so `parse_item()`
  reads `Doer`, `Parts`, `Lifts` and `Answers` on any kind too. `item_file()` refuses such a field and
  `item_file_problem()` faults it; `board_dir_problems()` names it (rule 14), so a split file carrying one (a
  `decide` with `Doer: team ops.`, an `fyi` with `Parts: TD-23.`, an `act` with `Answers: done | not yet.`, all
  v2-legal data the v2 reader reads) reads as its v2 line did and stays named.
- **Lines** (round 9's F157): `parse_item()` and `edit_item()` cut a file into lines at `\n` alone (`_lf_lines()`,
  which today only `archive_closed()` calls; B5 removes `archive_closed()` and keeps `_lf_lines()`, round 9's F166),
  and `parse_item()` strips each line's ending after it (its `\n` and one trailing `\r`) in what is read, never
  `str.splitlines()`: a U+2028,
  U+0085 or `\x0c` in a value stays inside that value (`parse_board()`'s `splitlines()` of a v2 board is v2's and
  stays).
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
  `parse_hide_until()` and `DUE_RE` find a field on a v2 line by its name (the trailer's readers after its `Due:`,
  `parse_parts()` after its `Context:`, `parse_hide_until()` after its `Due:` or else its `Context:`) and stay v2's. B1
  adds `parse_decided_value(value)`, giving `(label, date, by)` (`by` None when the value names no one) or None for a
  value outside `<date>[ by <person>] — <label>`, which fills `decided` and `decided_by`;
  `parse_closed_value(value)`, giving `(date, why)` (`why` None for a bare date) or None outside `<date>[ — <why>]`,
  which fills `closed`; and `parse_answers_value(value)`, giving the written answers split on each bar not after a
  `\`, `\|` read as a bar, each trimmed and none empty, which fills `answers`, `default` and `consequences` through
  `split_answer()` as `_raw_answers()`' readers do, and `lifts` from a `Lifts` value of the same form. `Kind` is one
  of the five, `Due` and `Hide until` a `YYYY-MM-DD` day (`_real_day()`: the `ISO_DAY_RE` shape and a real date, since `date.fromisoformat()` alone also
  takes `20261108` and `2026-W45-3` on Python 3.11 and later), and `Parts` its ids
  (`entry-id`s, read with `REF_TD_RE` as `parse_parts()` reads its ids), each read from the value by `parse_item()`; `Doer` by
  `doer_value()`, the value added.
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
- **`Kind` and `Due` as v2 reads them** (round 8's F119), so the split's read-back agrees field by field. `Kind` is
  read ignoring case and lowercased, as `KIND_RE` (`re.IGNORECASE`) and `parse_board()`'s `.lower()` read a line's
  (`**Kind:** ACT` is an `act`); `item_file_problem()` faults a kind not in lower case, as `item_problem()`'s `kind:`
  fault does, and `canonical_item_file()` lowercases it. `Due`: a value that is a day (`_real_day()`) is `due`; any
  other value is `bad_due`, the value as written, `due` None. v2 reports a bad `Due:` only in `DUE_ATTEMPT_RE`'s
  date shape because on a line it must find the field in prose; a header value is wholly the field's, so no shape
  test is needed, and every value the split writes is one v2 read as a date or as `DUE_ATTEMPT_RE`'s `raw` (a `Due:
  soon.` on a line is no field to v2, so the split writes no `Due` and its words stay in the heading, D11): the two
  reads agree. **A v2 `bad_due` in a shape `DUE_RE` does not match** (round 9's F147, the ruling, replacing F130's
  refusal): v2 reads `DUE_ATTEMPT_RE`'s match (`\bDue:?\s*<date shape>`, a colon or none: `Due: 2026-1-9.`, `Due:
  3/4.`, `Due 3/4.`) as `bad_due`, its `raw`. The split's `Due` span is the match v2 reads (round 9's F171):
  `DUE_RE`'s first match when its date is a day, else `DUE_ATTEMPT_RE`'s first (`Fix Due 3/4 soon. Context: TD-1.
  Due: 2026-02-30.` reads `bad_due` `3/4`, so the span is `Due 3/4` and `Due: 2026-02-30.` stays in the heading).
  The split writes `**Due:** <raw>`, which v3 reads as `bad_due` `<raw>` whenever `<raw>` is no day: `2026-1-9`,
  `3/4` and `2026-02-30` are not (`_real_day()`), so the two reads agree and the item is carried, reported as
  `due_error` by both as *The board* reports it; it is no `board_dir_problems()` finding (rule 14 does not name
  it), and `split_board_notes()` lists nothing for it (round 9's F163). Two shapes would read
  differently, and they are the split's one kept `Due` refusal: a `raw` that is a day, which only a colonless match
  can give (`Due 2026-11-05.`: v2 `bad_due` `2026-11-05`, while `**Due:** 2026-11-05` reads as a day; no written
  value makes v3 read `bad_due` `2026-11-05`, so the split refuses it rather than write a value v3 reads otherwise,
  case `due_no_colon`), and the match v2 reads (above) lying inside another field's span or a reply's (round 9's
  F164; `Context: TD-1, Due 3/4.` with no other `Due`, which `CONTEXT_RE` runs over since only `Due:` ends a
  Context; v2 reads `bad_due` from the Context's words, and a carried Context gives v3 none, case `due_in_context`;
  on an `fyi` v2 reads `fyi_due` from it, which v3 would not). A date-shaped `Due` inside another span that v2 does
  not read (`Context: TD-1, Due 3/4. Due: 2026-11-20.`, whose `Due:` v2 reads as a day) is no read difference: it
  stays in that field's or reply's words and is carried, case `context_due_words`.
  The first never touches an `fyi`, which v2 and v3 both read as `fyi_due` with `due` and `bad_due` cleared,
  whatever its `Due` value (below). **An `fyi`'s `Due`** (round 9's F147,
  the ruling, reverting F138's refusal): an `fyi` carrying any `Due` v2 recognises, `DUE_RE`'s or
  `DUE_ATTEMPT_RE`'s (`Due: 2026-11-20.`, `Due: 3/4.`, the colonless `Due 2026-11-20.`; F145), is carried as its
  `Due` header field, and a v3 file's `fyi` with a `Due` reads as v2's does: `fyi_due` True, `due` and `bad_due`
  None (`parse_board()`: `fyi_due = kind == "fyi" and (due is not None or bad is not None)`, then both cleared;
  F119). Rule 14 names it, and `item_file()` refuses one.
- **`BoardItem` gains** `id`, `path` (its path relative to the board's directory, `""` for a v2 item), `words`
  (below), `added`, `session`, `host`, `context`, `closed` (`(date, why)`, `(None, None)` for an archived file
  with no `Closed:` in its form, or None), `replies`, `fields` and `raw` (round 4's F54: a v2
  item's line as written, its indent included; a v3 item's file text as read, every byte). `detail_source` is B3's
  (TD-070's plan, D8 and B3; round 1's F194), not B1's or B2's. `line` stays: a v2 item's 1-based line,
  0 for a v3 item, read by nothing but v2 code (*The board's order*, D6, no longer reads it). `text` keeps its
  meaning until B5 removes it (below). **`item_record()`** changes in two builds, and only there (round 2's F33,
  round 3's F46, round 7's F91): its `doer` key is v2.8's already (TD-065's build, D12), so B1, which fills
  `BoardItem.doer` for a v3 item too, changes no record; at B2 it gains `id`, `path`, `added`, `context` and `closed`,
  its `text` reads `BoardItem.words` for both majors (a v2 record's `text` was the line after its tick), and its
  `refs` reads a v2 item's `context`, its replies cut (round 1's F191, below), keeping `line`; at B5 it loses
  `line`. *The builds* list the expected JSONs each of the two regenerates.
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
- **The record's keys a v2 line fills today** (round 8's F123, reopening F13, F57). `item_record()` reads
  `session`, `host`, `refs` and `replies` from `item.text` today (`item_head(item.text)`, `item_refs(item.text)`,
  `parse_replies(item.text)`), and a v3 item's `text` is `""`. From B2 each reads a `BoardItem` field, filled for
  both majors, so a v3 record is right and a v2 record is unchanged but in `refs` (below, round 1's F191):
  - `session`, `host` — `BoardItem.session` and `BoardItem.host`: a v3 item's from its `Session` value (`<name>`, or
    `<name> on <host>` split at its ` on `), None for none; a v2 item's from `item_head(text)`, by
    `parse_board()`;
  - `refs` — `context_refs(item.context)` (B2), `item_refs()`'s body over a bare Context value, for both majors:
    `item_refs(text)` becomes `context_refs()` of `CONTEXT_RE`'s `ctx` group over the text it is given, unchanged in
    what it gives that text, and the record reads the item's `context`, not `item_refs()`. Never `CONTEXT_RE` over a
    synthesised line (a value holds field names as words, D4). The value's missing final period changes no ref:
    `REF_TD_RE` and `REF_PR_RE` read no period, and a branch part is read `.rstrip(".")` already. **A v2 item's
    `context` is read without its replies** (round 1's F191, reopening F123, F66 and F80): `CONTEXT_RE`'s match over
    the line with `reply_span()` removed, reply tails and the `Decided:` field cut as `_gate_body()` cuts them for `_item_gate()` today (round 2's
    F200; with the `Decided:` cut, a `Context:` written only inside a Decided text reads as no Context, as
    `_item_gate()` reads it today; round 2's F205), where
    `item_refs()` today runs `CONTEXT_RE` over the raw text. One `context` then serves `refs` and `_item_gate()` alike.
    So an id read only from a reply's words leaves a v2 record's `refs` at B2: `fyi … Context: TD-1. — pat,
    2026-01-05: see TD-9 now` gave `refs` `["TD-1", "TD-9"]` and gives `["TD-1"]`, as its gate was already
    `("TD-1", None)`. That is a record change, and B2's (records change at B2 and B5 alone, *The builds*); text
    14's *`Context:`* bullet says it, and `fixtures/board/`'s `reply_ref` shows it;
  - `replies` — `BoardItem.replies`, a list of `(by, date, words)` tuples, each a string, `date` `"YYYY-MM-DD"`:
    `parse_replies()`' shape. A v3 item's from its Log (each reply line as D4 reads it, oldest first), a v2 item's
    `parse_replies(text)`, by `parse_board()`; the record's `[{"by", "date", "text"}]` is built from it as today;
  - `notes` — `item_notes(item, today)`, unchanged: it reads `hide_until`, `decided` and `due`, fields already.
- **A v2 item's `fields`** (round 4's F63) are the header fields its split file carries, `(name, value)` in the
  writing order (`Kind`, `Added`, `Session`, `Context`, …), each name spelled as D4's list spells it and each value
  in the file's form: `Decided` as `<date>[ by <person>] — <label>`, `Closed` as `<date>[ — <why>]`, `Context` and
  `Closed`'s why without the final period, `Session` as `<name>[ on <host>]`, `Answers` and `Lifts` without the
  final period; a field the v2 reader reads that has no file form here keeps its value as the reader gives it, under
  its name. **A value not in its form** (round 1's F176, copying TD-070's D11 rule, round 7's F93, F98, round 9's
  F172) is the line's text, not the reader's result: where the reader gives None (`parse_doer()` for a `Doer` that
  `doer_value()` refuses), the field's `fields` value is the value as the line holds it, trimmed and its one final
  `.` dropped, so a v2 item carries the field its split file writes. One exception keeps the two reads alike: when
  dropping the period leaves the value ending in whitespace (`Doer: acme .`), the value keeps its period (`acme .`),
  since a header value's end whitespace is dropped and `acme` would read as a doer; v3 reads `acme .` as no doer,
  as v2 reads the line. An empty value (`Doer: . Due: …`, `Doer: Due: …`), which `parse_doer()` reads as no doer,
  has no span (D11): its text stays in the words, and `fields` holds no `Doer`. So `split_board()` writes a v2
  item's `fields` as its header block, and the two majors' `fields` of one item are equal.
- **A v2 item** is a `BoardItem` with every one of those fields filled by `parse_board()` from its line. The v2 half
  of `load_board()` is the v2 line reader as the last v2.x release has it, so whatever fields that reader returns
  (v2.8's `Doer:` among them) fill the `BoardItem` fields of the same name and `split_board()`
  carries them into header fields of the same name. From it: `added` its date, `session` and `host` its head's,
  `context` its Context's value (without the final period) as `CONTEXT_RE` reads it over the line with
  `reply_span()` removed (round 1's F191, above), `closed` its `Closed:` (the why without its final
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

**D6. Reading (S5).** In this plan's own prose (not the SPEC text, which says *a board read from a directory* or
*from a file*, round 2's F201), a *v3 board* means `form` `"dir"` and a *v2 board* or *v2 file* `form` `"file"`,
whatever its `major` (round 2's F204). `load_board(path, ls, read, *, since=None)` gives a `Board`: `form`, `path`, `major`,
`preamble` (`README.md`'s text, or a v2 board's text before its first item), `items` (the open items), `closed`
(every closed item read, the archive's among them), each a `BoardItem` with its `id`, and `problems` (D6's last
bullet, its numbered rules).
- **`form`** (round 1's F190) is how the board was read: `"dir"` from a directory (a stub's directory among them),
  `"file"` from one file and its archive, None for an empty `Board` read from nothing (a missing `path`, rule 6's
  stub). A `Board` has a form and a major apart because they can disagree: a directory whose `README.md` declares 2
  is `"dir"` with `major` 2 (rule 4), a file declaring 3 is `"file"` with `major` 3 (rule 5). So everything that
  depends on how the board is laid out is defined on `form`: the preamble readers (below), *The board's order*,
  `board_problems()`' refusal (D7's *The gate*) and `board_dir_problems()`' checks (D11); `major` serves the version
  check alone (*The board's major*). Where this plan says "a v3 board" of a read, it means `form` `"dir"`, and "a v2
  board" `form` `"file"`.
- **`path`** (round 2's F196) is the path `load_board()` was given, as given: the board file, or the directory (a
  stub's path when it was given the stub), and on an empty `Board` (`form` None) the missing path. It names the
  board file in the preamble readers' pairs (below); every other path a `Board` names stays relative to the board's
  directory.
- **A directory** is read as `README.md`, each `<id>.md` directly in it, and each month directory under `archive/`
  and its files (the order of reading changes nothing: *The board's order* below orders `items` and `closed`). A
  **month** (round 6's F74) is a directory directly under `archive/` named `YYYY-MM`, a real month (`01` to `12`).
  Nothing else is read: a file directly in `archive/`, a directory under it not so named, a subdirectory of the board
  other than `archive/`, a subdirectory of a month, and anything deeper are each named under rule 11 and not
  descended into. An
  item is closed when its file lies under `archive/`, or lies outside it and carries a `Closed:` in its form; every
  other item is open. An archived file with no `Closed:` in its form is a damaged file (rule 9 below), read as
  closed, its `closed` `(None, None)`. **`parse_item(text, path)` sets `closed`** from the path it is given (round
  1's F195), not `load_board()`: under `archive/`, the file's `Closed:` value (`(date, why)`), or `(None, None)` when
  it has none in its form; outside it, the `Closed:` value, or None when it has none in its form (open).
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
  file gets, and a twin's two lines read with one id. A line with no readable date (none, or one that is no day,
  `_real_day()`; round 9's F165) has id None.
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
- **`since`**, a date, leaves out the archive months before its month, neither listed nor read; the month equal to
  `since`'s is read (round 1's F195). Rule 11 is `board_dir_problems()`' alone, which takes no `since` and reads the
  whole tree (round 2's F197), so a directory under `archive/` that is not a month is named there, never by a read
  with `since`. `Board.closed` is
  then partial, so `since` is for a reader that judges only open items and recent closes (a nudge, `show`, a
  consumer's Inbox), never for what a board ever held: the sweep (D9), `board_problems()`'s `old`, the verdicts and
  `split_board()`'s read-back each take a board read whole.
- **The board's order** (round 3's F45), stated once, on `form` (round 1's F190): on a `"dir"` board `items` and
  `closed` are each in id **descending** order, newest first; on a `"file"` board they are in line order (`closed`
  the board's closed lines, then the archive's), whatever `major` either declares. *What needs the person*'s ties (undated, unreadable-due and `fyi` items, and two items of one date)
  fall back to it, as does every reader that lists items. Sorting ids descending orders items newest
  `Added` date first, and within one day at random (the nonce); a v2 board's line order is whatever its writers and hand edits left (v2's `add` writes
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
  `(origin_url, basename, board)`), `board_problems(board, old)`, and the verdicts through their trees (B4).
  `board_people()`, `answered_by()`, `people_problems()` and `answered_by_problems()` take the `Board`: on a `"dir"`
  board they read every line of `README.md` as preamble (a `- [ ]` line in it is prose, and ends no read), on a
  `"file"` one only the lines above its first item, as now (keyed on `form`, round 1's F190). `board.py`'s
  `who_answered(board, by)` takes the `Board` too (B3), reading its `People:` through `board_people()`.
  `parse_board(text)` stays as the v2 half of `load_board()`; `parse_item(text, path="")` reads one file. **Each
  reader's shape over both arguments** (round 1's F193; round 2's F198): every reader with a text form, `needs_you()`,
  `sweep()`, `board_problems()`, `board_people()`, `answered_by()`, `people_problems()` and `answered_by_problems()`,
  tells a `Board` from a v2 board's text by `isinstance(x, Board)`, reading the text as today until B5;
  `people_problems(board)` and `answered_by_problems(board)` given a `Board` return `(path, problem)` pairs (round
  2's F196, reopening F193), the path `README.md` on a `"dir"` board and `Board.path`'s basename on a `"file"` one,
  and a missing `People:` or `Answered by:` line gives that path with today's message (today's `(0, "ℹ …")` becomes
  `(<path>, "ℹ …")`); given text, `(line, problem)` as today, until B5; the gate uses the pairs as they come.
  `board_problems(board, old)` of text gives today's result unchanged, and given a `"file"` `Board` raises
  `Refused` (D7's *The gate*).
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
  `BOARD_MAJOR`; given text, it is the ledger's check, unchanged. Its words for a `Board` (round 9's F161) are the
  text form's with "this board" for "this file": `this board declares Ledgerboard: <n>, newer than this
  ledgerboard.py reads (3) — vendor a newer release; nothing was read`; `board.py` prefixes the file that declares
  it, `<board>/README.md: ` for a directory and `<board>: ` for a stub or a v2 file, as it prefixes a file today
  (`edit_newer_major`). A caller checks `version_problem(board)` before it
  trusts the rest. `major` serves that check alone: no reader's behaviour turns on it, only on `form` (round 1's
  F190). `board.py`'s `read()` checks every file it reads with `version_problem(text)`; from B3 it reads a
  board through `load_board()` and checks `version_problem(board)` instead, so a `README.md` or a stub declaring 3
  is read, and it keeps `version_problem(text)` for the ledger and the rank file. So B2's `board_dir` cases
  (`readme_v2`, `newer`) pass through `load_board()` and `version_problem(board)`; B3's writer cases over a
  directory (`add_v3`, `list_stub`, `show` and the rest) pass because `board.py` reads a board's major only so; and
  B4's verdicts read their trees through `load_board()`, which judges no major against `FORMAT_MAJOR`. Until B3
  `board.py` reads v2 boards alone, which declare no major above 2.
- **Damaged and odd input** (round 1's F15, round 5's F69) never raises. Each rule below is marked `problems`
  (`Board.problems` lists it, as `(path, problem)`: what the read skipped or could not settle) or
  `board_dir_problems() only` (the read settled it, or never read the file; only `board_dir_problems()` names it).
  `board_dir_problems()` names every rule of both marks on a `"dir"` board, and `Board.problems` alone on a `"file"`
  one (D11; on `form`, round 1's F190). Each rule names its finding once. **Order** (round 4's F64): both lists are sorted by path (the path
  string's code-point order; a v2 board's problems name its file's or its archive's name), then by the rule's
  number here, then by line within the file. Text 8 copies this list as it stands.
  1. `problems`: a file `read()` gives None for: skipped, named under its path.
  2. `problems`: a file `parse_item()` reads as no item (its first non-blank line does not open `## `, or the next
     non-blank line is no header field, `**<Name>:** `; D7's one rule, round 9's F139): skipped, named under its
     path.
  3. `problems`: a `README.md` that is missing, or declares no major: `major` 3, named under `README.md`.
  4. `problems`: a `README.md` declaring 2: read as a directory, `form` `"dir"`, `major` 2, named under `README.md`.
  5. `problems`: a file declaring `Ledgerboard: 3` that holds items (it is no stub): read as a v2 file, `form`
     `"file"`, `major` 3, named under its name.
  6. `problems`: a stub whose directory is missing: an empty `Board`, `form` None, named under the stub's name.
  7. `problems`: an item with no `Added`: read, its `added` None, named under its path.
  8. `problems`: one id in two files of a v3 board: read once (above), named once, under the path of the archived
     file that wins (the later month's of two archived copies).
  9. `problems`: a file under `archive/` with no `Closed:` in its form: read as closed, its `closed` `(None,
     None)`, named under its path.
  10. `problems`: one id on two open lines, or on two closed lines, of a v2 board (below): both lines read, the id
      named once, with both lines, under the board file's name when either line is on it, else the archive's.
  11. `board_dir_problems() only`: any entry the read does not take (round 6's F74): a file directly in the
      directory, or in a month, whose name is not an id and `.md` (its stem failing `is_item_id()`, D3, so
      `2026-02-30-abcd1234.md` among them; round 1's F195; `README.md` aside); a subdirectory of the
      directory other than `archive/`; a file directly in `archive/`; a directory under `archive/` that is not a
      month; a directory in a month. Each is named once, under its own path (a directory's with
      its trailing `/`), and not read or descended into.
  12. `board_dir_problems() only`: a header-block line that is no field (D4): kept, in no field.
  13. `board_dir_problems() only`: an `Added` that is not the id's date.
  14. `board_dir_problems() only`: a `Decided` or `Closed` not in its form (D4): read as no answer, or no close; a
      `Kind`, `Hide until`, `Parts` or `Doer` not in its form (round 6's F76): read as the field absent, a `Kind`
      outside the five as a to-do, shown; a `Doer` that reads but is spelled with more than one space, or a tab,
      after `team` (F79): read; a `Kind` in the wrong case: read as that kind; a `Due` on an `fyi`: read as `fyi_due`
      (round 8's F131); a field its kind does not take, `Parts` or `Lifts` on any kind but `decide`, `Doer` on any
      kind but `act`, `Answers` on a kind that takes none (round 9's F147, the ruling): read as written, as v2 reads
      it.
  15. `board_dir_problems() only`: a `Closed:` in its form on a file outside `archive/`: read as closed.
  16. `board_dir_problems() only`: an archived file in a month that is not its `Closed:` date's: read as closed.

  What is no problem: `major` is what the preamble declares (`Ledgerboard: N`), else 2 for a file and 3 for a
  directory; a v2 file with no `Ledgerboard:` line is a v2 board, `major` 2 (`board_major(text, file=True)`,
  above); a missing `path` (no file, no directory) is an empty `Board`, `form` and `major` None and `path` the path
  given (round 2's F196): the caller decides
  whether a missing board is wrong, as for a missing ledger.

**D7. The edits and the writers (S6).** `edit_item(text, action, *, to, answer, why, reply, by, today, close)` is
`edit_line()`'s five edits over an item file: snooze, due, done and decide each set one header field, reply appends
one Log line (opening `**Log:**` after the body when there is none); a closed item is refused; each is read back.
- **A field an edit adds** goes right after the last known field that precedes it in the writing order, unknown
  fields between them staying where they are, or first in the header block when no known field precedes it. A
  field it sets that is already there is rewritten in place.
- **A reply's words** are refused when empty or blank (the reader reads no reply from such a line).
- **Line endings:** an edit of a CRLF file writes the line it adds or rewrites with `\r\n` (the ending the file's
  first line uses) and keeps every other byte; `canonical_item_file()` alone normalises to `\n`.
- **The gate a file's Context names** (round 9's F151, reopening F113, F124): `edit_item(…, "decide", close=)` and
  `item_file()` (its Parts rule and its check that some answer lifts) need the `(ref, gate)` of a bare Context
  value at B1, before B2's `_item_gate(BoardItem)`. B1 adds `_context_gate(context)`, the body of today's
  `_item_gate()` after it finds the Context (the one entry ref and the one gate the value names, each None for none
  or more than one), and `_item_gate(text)` becomes `_context_gate()` of `CONTEXT_RE`'s `ctx` over `_gate_body(text)`,
  giving what it gives today. B2's `_item_gate(item)` of a `BoardItem` is `_context_gate(item.context or "")`, and
  D7's string rule reads an item file's string through `parse_item()` and then the same; no reader of a v3 item
  passes a synthesised line to `CONTEXT_RE`.

`item_file(…)` takes `item_line()`'s arguments and `doer` (D4) and gives a file; `decided_file(…)` takes
`decided_line()`'s. Their refusals keep what still means something (a value of more than one line, a host with no
session, a kind's rules, `Parts:` and `Lifts:` rules, a look's fixed pair, a doubled Recommended label, a `doer` on
any kind but `act` or outside its form, a result that does not read back) and drop the field-name refusals and the
`(by …)` one. `item_file_problem(text)` and `canonical_item_file(text)` are `item_problem()` and `canonical_item()`
for a file; since no key rests on a file's spelling, `canonical_item_file()` rewrites any field.
`item_file_problem()`'s messages are plain sentences, each opening with its rule's tag as `item_problem()`'s do; this
plan fixes the rules, B1 writes the words, and the fixtures pin them.
- **TD-075's answer forms carry over** (round 7's F90; TD-075's B1 has merged, TD-084, D12): `item_file()` refuses on a
  `decide` two forms with one head and a `default` naming a form, as `item_line()` does; `decided_file()` writes no
  ` (default)` mark on a form, as `decided_line()` does, its words written as given; `item_file_problem()` faults
  both on an open `decide` with no `Decided`, as `item_problem()` does, and nothing on a decided or closed file;
  and `edit_item(…, "decide")` fills a string answer (`fill_form()` over the file's offered labels) before writing
  it and refuses a form as offered, unfilled, or a head with empty words, as `edit_line(…, "decide")` does (TD-075's
  D4). `board.py`'s `plan_edit()` fills once before `edit_item()`, `_decide_ledger()` and `subject()`, as TD-075's D4
  has it before `edit_line()`. Every reader of an item's answers (`closes()`, `decide_lift()`,
  `_sweep_closes()`, `_answers_owing()`, `_answered_within()`, `uncovered_decisions()`, `edit_item()`'s `close`,
  `board.py`'s `_decide_ledger()`, and `item_file()`'s own check that some answer lifts) passes `_lifting(label, lifts, offered)` the item's offered labels —
  `BoardItem.answers`, already labels, where it holds a `BoardItem`; `parse_item(text).answers` where it holds an
  item file's text; and `parse_answers(text)` where it holds a v2 line's text, as `closes()` given a string,
  `plan_edit()`'s fill and `_decide_ledger()` do until B5 (round 8's F113; `parse_item()` reads no item from a v2
  line, D7's one rule below) (TD-075's D5); none compares an answer to `Lifts` itself.
- **One rule for a string argument, B2 to B5** (round 8's F124). Every reader that takes an item as a string
  (`closes()`, `decide_lift()`, `parts_problems()` and `_item_gate()` from B2, and `board.py`'s `_decide_ledger()` and
  `_check_parts()` from B3, since `board.py` runs unchanged until then; round 1's F188) reads it so (round 9's F139, replacing F135's test): a string whose first non-blank line opens
  `## ` and whose next non-blank line is a header field (`**<Name>:** `) is an item file, read through
  `parse_item()` and then as the `BoardItem` it gives; any other string is v2 (a line, a line's text after its tick
  as `_item_text()` takes it today, or a board's text, which `parts_problems()` also takes), read as today. A v2
  line never opens `## `, and an item file opens with its heading and its header block (D4); a v2 board's text
  that opens with a `## ` section heading reads as v2, since no v2 writer puts a `**<Name>:** ` line under it. So no string a v2 writer
  wrote reads as an item file, and `parse_item()` reads no item from a string failing the test (rule 2). B5 removes the
  second branch with the v2 writers.

**The gate**, `board_problems(board, old)`, judges each open item of `board` whose id no item of `old` (open or
closed) has, as `(path, problem)`. It refuses only when `board` was read from a file (`form` `"file"`, whatever its
`major`; round 1's F190), raising `Refused` (round 1's F193); `old` may be of either form (the split
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
subject, which the v2 writers call until B5 removes them. **What `subject()` receives for a v3 item** (round 8's
F117, reopening F23): `text` the item's words (`BoardItem.words`, the heading's text), `id` its id, and `session`
the name the subject names, which `board.py` passes as its caller's `--session`, else the item's `Session` name,
else None (`n/a`). That is v2's precedence, the caller's first (`subject()` today: `session or` the line's
`(session …)`), so a session editing another session's item names itself, as now. With `id` given, `subject()`
reads no session from `text` and makes the head from the words alone, never through `edit_head()` (which cuts a
line at its first ` — ` and at `FIELDS_RE`'s field names, both of which a heading may hold as words): the words
with every `*` dropped, runs of whitespace collapsed, trimmed, clipped to `EDIT_HEAD_CHARS` (60) with `…` as
`edit_head()` clips. A reply's words are never in it: a v3 reply is a Log line, not in the heading.

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

**D11. Migration (S9): the readers B2 lands for it.** The split itself (`split_board()`, its refusals
and notes, the stub) is TD-070's plan's, D11; these are the pieces of it a reader reads.

- A v2 item's
  `closed` (B2) is `(date, why)` from its `Closed:`: the date `CLOSED_RE` reads when it is a day (`_real_day()`;
  `2026-02-30` is not, so the line is a closed item with no readable `Closed:` date, which the split refuses, TD-070's plan, D11), and the why the
  text after a ` — ` that directly follows the date, trimmed, its final period dropped, None without one (round 9's
  F160).
- A v2 item's `Doer` field (round 1's F176; TD-070's plan, D11, round 7's F93, F98, round 9's F172) is carried as
  written, never respelled (the read-back compares `doer.text`): one spelled with more than one space or a tab after
  `team`, one on a kind but `act`, and one outside its form each fill `fields` as the line holds them (D4's *A v2
  item's `fields`*): `parse_doer()`'s text (the value trimmed, one final `.` dropped), and also for a value
  `doer_value()` refuses, but for `Doer: acme .`, whose value keeps its period. An empty value (`Doer: . Due: …`,
  `Doer: Due: …`) has no span: its text stays in the heading, and the item has no `Doer` field.
- **its heading is `item_words(line)`** (new in B2, where it gives a v2 item's `BoardItem.words`): the words of the line
  that the v2 reader reads as no field, no reply and no part of the prefix (tick, kind, date, head, the ` — ` after
  it), in their order, kept verbatim but for runs of whitespace collapsed to one space: no period added or removed
  (`— Say Go to X. Context: …` gives `## Say Go to X.`), and any words a hand edit left outside the fields kept. A
  bold head stays in the heading as written (`**Release v2.8**, then tag it`), where *The bold head* reads it.
  **The span** (round 6's F80), defined by how the v2 reader finds each field and the replies on the line after its
  prefix: each field's span runs from its name to its value's end as its reader takes it, `Context` to where
  `CONTEXT_RE` ends it over the line with `reply_span()` removed (the next field's name, the reply's start, or the
  line's end: round 1's F191, the `context` D4 reads, so a reply is in no Context's span and goes to the Log
  alone), `Parts` to where `PARTS_RE` ends it, `Doer` from
  `DOER_RE`'s match to where `parse_doer()` ends its value (the next field's name, a reply, or the line's end; round
  9; an empty value has none, the `Doer` bullet above), `Due` through the match v2 reads (`DUE_RE`'s first when its date is a day,
  else `DUE_ATTEMPT_RE`'s first; round 9's F147, F171) and `Hide until` through `_hide_match()`'s date, `Answers`, `Lifts` and `Decided` to where `ANSWERS_RE`, `LIFTS_RE` and `DECIDED_RE`
  end them, `Closed` through its date and, when a ` — ` directly follows the date, to the line's end (round 9's F160:
  words after the date with no ` — `, `Closed: 2026-01-10 lifted.`, fall outside it and stay in the heading, so no
  word is lost and the why both majors read is None), and the replies over `reply_span()`; each field's span takes
  with it the one `.` that ends its value, when the value's reader leaves one. The words are
  every piece of the line outside those spans, in order, each trimmed, the empty ones dropped, joined by one space.
  So they are the text between the prefix and the first field, any text after the last span, and any text between
  two spans: since a Context, a Parts and a Doer run to the next field's name, the only such gaps on a line are after a
  `Due` or `Hide until` date or a `Closed` date with no why (`Due: 2026-11-08. also ping sam. Closed: …` keeps
  `also ping sam.`).

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

`board_dir_problems(path, ls, read)` is `v2_problems()`'s twin, and
each consumer calls it where it calls `v2_problems()` (D7, *Consumers*). It takes no `since` and reads the whole
tree, every archive month (round 2's F197). On a board read from a file (`form`
`"file"`, round 1's F190: a repo still on v2, as in its vendoring PR before the split) it returns `Board.problems`
alone (round 3's F50): the checks of a directory's names, header blocks and months have nothing to judge there.

**D12. The release: v3.0, and v2.8 before it**, as far as B1's precondition. v3.0's release, and the builds'
order up to it, are TD-070's plan's, D12.
- **The last v2.x minor, v2.8, is released before B1 merges.** Past the tag v2.7, `main` carries six changes to
  `ledgerboard/`, `SPEC.md` and `fixtures/` (`git log v2.7..origin/main`, 2026-11-13, at 68363f4; round 9's F159):
  TD-079 (TD-068's B1, PR #240: `set --title` retitles an entry, and `edit` and `set` refuse names that belong
  elsewhere, `SPEC.md`'s v2.8 text), TD-080 (PR #242: `misplaced_names()`'s note for two Title sections names the
  heading), TD-083 (TD-065's B1, PR #253, 5b036e4: `Doer:` on the act line), TD-084 (TD-075's B1, PR #254, e42fc66:
  an offered `<head>:` answer is a form), TD-088 (TD-078's B1, PR #268, 859f6b3: `ledger.py note` writes an
  archived entry where it is, with its *Versions* paragraph "v2.8 gives an archived entry a note") and TD-089
  (TD-078's B2, PR #269, f9db4f1: `migrate`'s rules 5–8, with "v2.8 gives `migrate` the last old forms", now
  *Versions*' last v2.x paragraph, after which text 12 lands). TD-090 (68363f4) migrated this repo's ledger and
  touched none of the three. TD-073 is v2.7's (its commit is an ancestor of the tag). Whatever `main` carries past
  v2.7 when B1 is ready is released as the last v2.x minor before B1 merges: a precondition of B1. The release
  itself is Paul's. The board's act "Release v2.8" is closed (2026-11-12, #271: Paul folded TD-073 into v2.7, #226, released in #233), and
  no v2.8 tag exists, so v2.8 is still uncut and nothing on the board carries its release but B1's `decision
  (paul)` block, whose answer is Paul's word that v2.8 is cut (round 1's F178). Round 8's F129 allowed for that act
  cutting v2.8 before TD-078's B1 and B2, which would have made the last minor v2.9; the act closed without a cut,
  and both builds have merged, untagged, so v2.8 holds them whenever it is cut and the v2.9 branch falls away (a minor cut later still is the last minor, by the amendment below).
- **No v2.x release after B1 merges**, and no tooling to release from a branch: `release.sh` cuts from `origin/main`
  and stays so. A v2.x fix wanted after B1 merges goes into v3.0.
- **TD-065 ships in v2.8** (Paul's Go on TD-065's design, 2026-11-12, which settles round 5's F68 precondition):
  its build has merged (TD-083, 5b036e4), so it is in v2.8, which is released before B1 merges. `Doer` is also this
  design's own v3 header field (D4, text 8, text 13). A v2 line can carry `Doer: <value>.`: TD-065's
  `parse_doer(text)` stays the v2-line reader the v2 half of `load_board()` uses, and at the split (B5) the v2 half
  carries a v2 line's doer into the header field `Doer` (`split_board()` writes a v2 item's `fields`, D4). Text 14's
  `Doer:` bullet substitutes in v2.8's `Doer:` paragraph (*The board*, "**`Doer:`** (v2.8) — `Doer: <repo>.` or
  `Doer: team <team>.`, …", TD-065's text 1). What follows is mechanical: `BoardItem.doer` and `item_record()`'s
  `doer` key are v2.8's already (B1 keeps them and regenerates no record for them, *The builds*), and `SPEC.md`'s
  *The open item line* already defines `doer-repo` and `doer-part`, with the bodies text 13 gives them, so B1 moves
  those two productions from that block into text 13's rather than adding them (a production is defined once:
  `tests/test_grammar.py`'s `ebnf()` asserts it), and TD-065's `doer` production reads them there. B1 lands
  `BoardItem.doer`'s v3 reading through v2.8's `doer_value()`, `item_file(doer=)`, the header field and text 13's
  `doer-field`. No v2.x release follows B1, so nothing of TD-065 lands after it.
- **TD-078's open question**, whether its archived-entry writer route "ships in a v2.x minor first", has the same
  answer: in a v2.x minor only as part of v2.8, released before B1 merges; otherwise it ships in v3.0. *(Amended 2026-11-12, TD-078's
  D3: it ships in the last v2.x minor, so B1 is `Blocked by` TD-078's B1 (TD-088) and B2 (TD-089) and `decision (paul)`, whose Ask is
  whether that minor is tagged with nothing on `main` past it under `ledgerboard/`, `SPEC.md` or `fixtures/`; Paul's
  answer lifts it once he has cut it. TD-075's D6 put its B1 in the same minor; it has merged (TD-084, e42fc66), as
  TD-065's B1 has (TD-083, 5b036e4), so neither blocks B1 (round 8's F129). That minor is v2.8 when it is cut after
  TD-078's builds, as TD-078's D3 and TD-075's D6 rule; where this plan says v2.8 is released before B1, it is that
  minor, and each build writes, wherever the SPEC texts here say v2.8, that minor's number, as TD-078's D3 rules;
  round 7's F94; round 9's F169.)* **B1's blocks, to be filed** (round 8's F129, round 9's F142, F169): `Blocked by: TD-088, TD-089, decision (paul)`
  (TD-078's B1 and B2), whose Ask is: *Is the last v2.x minor tagged, holding TD-078's B1 and B2,
  with nothing on main past that tag under ledgerboard/, SPEC.md or fixtures/?* TD-088 and TD-089 have merged
  (859f6b3, f9db4f1; round 9's F159), so those two blocks are met and B1 waits on the `decision (paul)` alone.

## The reader table

**The reader seam, function by function** (round 8, ending the recurring topic: F13, F23, F44, F55, F66, F109,
F113, F117, F123, F124). Derived from the pinned code (`ledgerboard/__init__.py` and `ledgerboard/board.py` at
`5617c15`, every function that reads a `BoardItem` field or its `.text`, takes an item's string, or calls
`parse_board()`, `parse_closed_items()`, `item_head()`, `item_refs()`, `parse_replies()`, `parse_answers()`,
`_item_gate()`, `item_key()`, `edit_head()` or `bold_head()`), not from this plan. A v2 item reads as today
throughout; the table gives what a v3 item is read from, and the build that makes it so. A build that changes a
function not in this table re-derives it (the same grep) and adds the row.

A row whose build names B3, B4 or B5 beside B1 or B2 is shared: its later part is TD-070's second part's.

| function | reads today | a v3 item's source | build |
|---|---|---|---|
| `BoardItem` | — | gains `id`, `path`, `words`, `added`, `session`, `host`, `context`, `closed`, `replies`, `fields`, `raw` (D4); `text` `""` | B1; `text` gone B5 (`detail_source` is B3's, TD-070's plan; F194) |
| `parse_board()`, `parse_closed_items()`, `detail_block()`, `item_key()`, `is_item()`, `is_open_item()` | a v2 line | none: the v2 half of `load_board()` (D6) | B2 fills the new fields; stay v2's |
| `parse_answers()`, `parse_default()`, `parse_consequences()`, `parse_decided()`, `parse_decided_by()`, `parse_lifts()`, `parse_parts()`, `parse_hide_until()`, `parse_doer()`, `DUE_RE` | a v2 line | `parse_item()`'s value readers (D4) | B1; stay v2's |
| `item_head()` | `.text`'s head | `BoardItem.session`, `.host` (`Session`) | B2 (F123) |
| `item_refs()` | `CONTEXT_RE` over `.text` | the same result, its body now `context_refs()` over `CONTEXT_RE`'s `ctx` (round 2's F206), giving that text what it gives today; no record reads it (round 2's F199) | B2 (F123) |
| `parse_replies()` | `.text`'s tails | `BoardItem.replies` (the Log) | B1 fills it, B2 reads it (F123) |
| `item_record()` | `.text`, `.line` and the fields | `words`, the fields, `refs` from `context_refs(item.context)`, for a v2 item too, its `context` read with `reply_span()` removed (F191; round 2's F199) | B2; `line` gone B5 |
| `needs_you()` | `parse_board()`, `.line` for ties | the `Board` (`isinstance`, F193), its order on `form` (D6, F190) | B2 |
| `bold_head()` | a line, `reply_span()` cut | the heading, whole: `bold_head(words, heading=True)` (F162) | B1 |
| `edit_head()`, `subject()` | `.text`'s head, `SESSION_RE` | `subject(…, id=)`: the words, the session passed in (F117) | B1; v2 form gone B5 |
| `_people_line()`, `_answered_by_line()`, `board_people()`, `answered_by()`, `people_problems()`, `answered_by_problems()` | the lines above the first item | every line of `README.md` (a `Board` of `form` `"dir"`, F190); `isinstance(x, Board)` (F198); `(path, problem)` pairs, `README.md` or `Board.path`'s basename, a missing line's message among them (F193; round 2's F196) | B2 |
| `board_problems()` | `closed_items()`, `item_key()`, `KIND_RE` over lines | the `Board`s by id, `item_file_problem()`; `Refused` for `form` `"file"` (F190, F193); text, by `isinstance(x, Board)`, as today (round 2's F198) | B2; v2-text form gone B5 |
| `_context_gate()` | — (the body of `_item_gate()` after its `CONTEXT_RE`) | a bare Context value: `item_file()`, `edit_item(…, close=)` (F151) | B1 |
| `_item_gate()` | `CONTEXT_RE` over a string | `_context_gate(BoardItem.context)` | B1 (calls `_context_gate()`); B2 (`BoardItem` form); string form gone B5 |
| `closes()` | `_item_gate(_item_text())`, `parse_lifts(text)`, `parse_answers(text)` | `context`, `lifts`, `answers` | B2; string form by D7's rule (F124) to B5 |
| `decide_lift()` | `parse_board(line)`, `_item_gate(item.text)` | an item file through `parse_item()`, or a `BoardItem` | B2 (F124) |
| `parts_problems()` | `CONTEXT_RE.search(_gate_body(item.text))`, then `_parts_fault()` | `BoardItem.context` | B2 (F124); `item:` prefix (F120) |
| `_sweep_context()`, `_sweep_head()` | `it.text` | `context`; `words` | B2 |
| `_item_date()` | `ITEM_DATE_RE` over `it.text` | `added` | B2 |
| `_read_boards()`, `covers()`, `sweep()` | `parse_board()` over texts, `lines[it.line - 1]`, `item_key(r["line"])` | `load_board()`'s `Board`s, ids | B2 |
| `_answers_owing()`, `_audit_satisfied()`, `_sweep_closes()` | `_item_gate(it.text)` | `_item_gate(item)` | B2 |
| `edit_line()`, `item_problem()`, `canonical_item()`, `item_line()` (its read-back `written()`), `decided_line()`, `archive_closed()` | a v2 line or board | `edit_item()`, `item_file_problem()`, `canonical_item_file()`, `item_file()`, `decided_file()`; none | B1 adds; B5 removes |

The runner (`fixtures/run.py`) reads `BoardItem.text` twice (`lift_cases`, `sweep_cases`); B2 moves both (*B2*).

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
item file* lands at B1 without its three clauses that name `board_dir_problems()` ("and `board_dir_problems()` names
it" after the header-block line that is no field, "; `board_dir_problems()` names it" after a value not in its
form, and " and `board_dir_problems()` names it" after a field on a kind that does not take it, round 9), which B2 adds with
`board_dir_problems()`; text 10's library list lands at B3 without `plan_split`, which B5 adds with the `split`
action (round 9's F155); text 10's added paragraph lands at B3 without its first sentence's "(*split first*)", which B5 adds with the
`split` action (until then `board.py`'s refusal of a v2 board says only that it writes a v3 directory, and B5's
words give `write_v2_refused`'s expected output its `split` hint); and each of text 14's bullets carries its own
build (B1, B2 or B5). Round 1's F175 tags text 8's opening: its heading, intro paragraph, tree and *An open
item* bullet are B1's (B1 builds `item_path()`), without that bullet's "Closing an item moves its file in the same
write", which is B3's; the *`README.md`* bullet and the *No sections* bullet are B2's (reader code), the latter
without "; a person reads the board through `board.py show`", which B3 adds; *The item id* lands at B1 without its
sentence "The writer draws the nonce at random … the module draws nothing.", which B3 adds; and text 9 lands at B1
without "; the writer moves it in the same write" after `item_path(id, closed)`, which B3 adds (F59's rule: the
writer's sentences land with the writer). Round 1's F192 tags two clauses of text 8's *The readers take the
`Board`* bullet (reopening F59, F175): "and the merge gate's verdicts" is B4's, which moves the verdicts onto
`load_board()` (until then they read v2 trees), and ", as `board.py`'s `who_answered(board, by)` does through
`board_people()`" is B3's, since `board.py` runs unchanged until B3; that bullet lands at B2 without both. Round 1's
F194 puts `key_id()`'s definition in *The item id* (B1, which builds `key_id()`), where *Reading a board* (B2) cites
it. Round 2's F201 tags *The item id*'s sentence "A v2 item's id is its line's date and `key_id()` of its key
(*Reading a board*)." as B2's, which builds the v2 ids; *The item id* lands at B1 without it, `key_id()`'s
definition a sentence of its own. *The builds* name each block's build so.

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
> board's order. **The board's order** breaks every tie: a board read from one file (`form` `"file"`) in line order,
> and one read from a directory (`"dir"`) in ids descending, newest first (by `Added` date; within one day the order
> is random). So tied items can change order when a board
> is split; which items need the person, and their classes and days, do not. Which of these a consumer shows, and
> when it escalates, is the consumer's.

**5. *The board*, *Preamble lines*** gains, after its first sentence:

> On a board read from a directory (`form` `"dir"`, *Reading a board*) they are `README.md`'s lines, every one of which is preamble, a line shaped like an item among them
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
> (`item_id(added, nonce)`, refused for anything else, a date that is no day of the calendar among it).
> `is_item_id(s)` says whether a string is an id: the shape, matched whole, and its date a day of the calendar, so
> `2026-02-30-abcd1234` is none. `item_path(id, closed=None)` gives an item's path, `closed` its `Closed:` date as
> `YYYY-MM-DD`, or None when it is open, and raises `ValueError` for an `id` that is no id, or for a `closed` that
> is no day of the calendar in that form. `key_id(key)` is the first 8 lower-case hex digits of the SHA-256 of the
> key's UTF-8 bytes. A v2 item's id is its line's date and `key_id()` of its key (*Reading a board*). The writer
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
>   - `Kind` — `decide`, `act`, `look`, `watch` or `fyi`, read ignoring case; none is the kindless to-do;
>   - `Added` — the date the item was added, its id's date;
>   - `Session` — `<name>` or `<name> on <host>`, the v2 head; none for `n/a`, and none on a decided file
>     (`decided_file()`, the v2 `(person)` head);
>   - `Context` — what the item refers to, its refs read as a v2 Context's are; `none` for nothing;
>   - `Parts` — a `decide`'s snapshot, `TD-15, TD-16`;
>   - `Doer` — on an `act` only, who should do its step: `<repo>`, a repo whose last part does not end in `.`
>     (*Appendix: grammar*, `doer-repo`), or `team <team>`, `<team>` a person's name; `Doer: team` alone names the
>     repo `team`. `doer_value(value)` reads it as `("repo" | "team", name)`, or None outside that form,
>     reading a run of spaces or tabs after `team` as one space (`item_file_problem()` faults that spelling);
>   - `Due`, `Hide until` — a date each; a `Due` that is no day is reported as written (`bad_due`), never silently
>     undated; on an `fyi`, a `Due` is ignored, and flagged (`fyi_due`), as on a v2 line;
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
>   *The board* says. A field on a kind that does not take it (`Parts` or `Lifts` off a `decide`, `Doer` off an
>   `act`, `Answers` on a kind that takes none) is read as written, as a v2 line's is; `item_file_problem()` faults
>   it and `board_dir_problems()` names it. A file is cut into lines at `\n` alone, a line's `\r` before it dropped,
>   so no other line-break character ends a value. A field the reader does not
>   know is kept: it is in `BoardItem.fields` (every header field as written, in its order), every edit keeps its
>   line byte for byte, and `item_file_problem()` faults it. A later v3 minor that adds a field changes nothing an
>   older v3 reader reads of the others; an older v3 gate faults an item carrying it.
> - **The body** is the detail block (*The detail block*): the lines after the header block up to the Log, leading
>   and trailing blank lines dropped (`BoardItem.detail`). No edit touches it.
> - **The Log** is the body's last section, led `**Log:**`, one line per reply, `- YYYY-MM-DD: <name>: <words>`,
>   oldest first. `<name>` holds no `:` and is at most 40 characters; `<words>` are not empty. A Log line in another
>   shape is kept, and read as no reply.
>
> `parse_item(text, path="")` reads one file as a `BoardItem`: its `id` from the path's name (`is_item_id()` of its
> stem; None when it is not one), `path`, its `words` (the heading's text), its fields, each value through its reader above (`kind`,
> `due`, `hide_until`, `parts`, `answers`, `default`, `consequences`, `lifts`, `decided` and `decided_by`),
> `added`, `session` and `host`, `context`, `doer`, `closed` (`(date, why)` or None), `replies`, `detail`,
> `fields`, and `raw`, the file's text as read. `closed` is set from the path: under `archive/`, the `Closed:` value,
> or `(None, None)` when there is none in its form; elsewhere, the `Closed:` value, or None. `item_record()` gives its
> record (*Reading a board*).
>
> **Reading a board** (`load_board(path, ls, read, *, since=None)`) gives a `Board`: `form`, `path`, `major`,
> `preamble` (`README.md`'s text, or, for a board read from a file, the text before its first item), `items` (the
> open items), `closed` (every closed item read, its archive's among them), each a `BoardItem` with its `id`, and
> `problems`. `form` is `"dir"` for a board read from a directory (through a stub too), `"file"` for one read from a
> file and its archive, and None for an empty `Board` read from nothing; how a board is read, ordered and judged
> turns on its `form`, never its `major`. `path` is the path `load_board()` was given (the board file, the stub or
> the directory; on an empty `Board`, the path that was missing).
> - **A directory** is read as `README.md`, then each `<id>.md` directly in it, then each month under `archive/` and
>   its files (*The board's order*, below, orders what it reads). A month is a directory directly under `archive/`
>   named `YYYY-MM`, a real month; nothing else in the directory is read (rule 11). An item is closed when its file lies under
>   `archive/`, or lies outside it and carries a `Closed:` in its form; every other item is open. An archived file
>   with no `Closed:` in its form is damaged (rule 9 below) and read as closed, with no date. An id held by two files
>   is read once (rule 8): an archived copy wins over an open one, and of two archived copies the later month's.
> - **The board's order:** `items` and `closed` are each in id order descending, newest first, on a `"dir"` board, and
>   in line order on a `"file"` one (`closed` the board's closed lines, then its archive's), whatever `major` either
>   declares. Every reader that lists items
>   lists them so, and *What needs the person*'s ties fall back to it.
> - **A board read from a file** is read with its archive beside it (`<stem>_archive.md`) by the v2 line reader as the last v2.x
>   release has it (`parse_board()`), whatever fields it reads filling the `BoardItem` fields of the same name (its
>   `context` read with its reply tails taken out, `reply_span()`, as the gate reads it), but for twins: an open line sharing its id with a closed line on the board or in its archive is closed, and the
>   closed line is the item (v3.0; v2.x matched twins within one file, by `item_key()`). Two open lines of one id,
>   or two closed ones, are both read, each an item with that id, and named in `problems` (rule 10); `to_close` names the id
>   once, and a closer of the board closes every open line of it. An item read from a line has as its id the line's date, a hyphen,
>   and `key_id()` of its key: `item_key()` of `- [ ] ` and the line's text after its tick (its indent, tick and the
>   whitespace after the tick dropped), trimmed. So it reads with the id its split file gets, a closed line with its
>   open twin's, and a consumer that persisted a hash of that key finds it in the id (`key_id()`, *The item id*). A
>   line with no readable date has id None. Its
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
>   the months read; the month equal to `since`'s is read. It is for a reader of open items and recent closes; the sweep, `board_problems()`'s `old`, the
>   verdicts and `split_board()` read a board whole.
> - **`major`** is what the preamble declares, else 2 for a file and 3 for a directory; a missing `path` gives an
>   empty `Board` with `form` and `major` None and `path` the path given. A board read from a directory has its
>   declaration read from every line of `README.md` outside HTML comments (`board_major(text)`), one read from a
>   file from the lines above its first item (`board_major(text, file=True)`), 2 when the file declares none: a
>   board's v1 and v2 are one format. The board's major is its own:
>   `BOARD_MAJOR` (3) is the newest a module reads, and `version_problem(board)` names a `Board` whose `major` is
>   newer; `version_problem(text)`, `format_major()` (whose "none means 1" stays the ledger's) and `FORMAT_MAJOR`
>   stay the ledger's. `major` serves that check alone; what a reader does turns on `form`.
> - **`problems`** and **`board_dir_problems(path, ls, read)`** never raise. Each rule below is marked `problems`
>   (`Board.problems` lists it, as `(path, problem)`: what the read skipped or could not settle) or
>   `board_dir_problems() only` (the read settled it, or never read the file). `board_dir_problems()`, which takes
>   no `since` and reads the whole tree, names, as
>   `(path, problem)`, every rule of both marks on a `"dir"` board, and gives `Board.problems` alone on a `"file"`
>   one. Each
>   rule names its finding once. Both lists are sorted by path (code-point order), then by the rule's number, then
>   by line within the file.
>   1. `problems`: a file `read()` gives None for: skipped, named under its path.
>   2. `problems`: a file `parse_item()` reads as no item (its first non-blank line does not open `## `, or the next
>      non-blank line is no header field, `**<Name>:** `): skipped, named under its path.
>   3. `problems`: a `README.md` that is missing, or declares no major: `major` 3, named under `README.md`.
>   4. `problems`: a `README.md` declaring 2: read as a directory, `form` `"dir"`, `major` 2, named under
>      `README.md`.
>   5. `problems`: a file declaring `Ledgerboard: 3` that holds items (it is no stub): read from the file, `form`
>      `"file"`, `major` 3, named under its name.
>   6. `problems`: a stub whose directory is missing: an empty `Board`, `form` None, named under the stub's name.
>   7. `problems`: an item with no `Added`: read, its `added` None, named under its path.
>   8. `problems`: one id in two files of a board read from a directory: read once, named once, under the path of the archived file
>      that wins (the later month's of two archived copies).
>   9. `problems`: a file under `archive/` with no `Closed:` in its form: read as closed, with no date, named under
>      its path.
>   10. `problems`: one id on two open lines, or on two closed lines, of a board read from a file: both lines read, the id named
>       once, with both lines, under the board file's name when either line is on it, else the archive's.
>   11. `board_dir_problems() only`: any entry the read does not take: a file directly in the directory, or in a
>       month, whose name is not an id and `.md` (its stem failing `is_item_id()`; `README.md` aside); a
>       subdirectory of the directory other than `archive/`; a file directly in `archive/`; a directory under
>       `archive/` that is not a month; a directory in a month. Each is named once, under its own path (a directory's with its trailing `/`), and not read or
>       descended into.
>   12. `board_dir_problems() only`: a header-block line that is no field: kept, in no field.
>   13. `board_dir_problems() only`: an `Added` that is not the id's date.
>   14. `board_dir_problems() only`: a `Decided` or `Closed` not in its form: read as no answer, or no close; a
>       `Kind`, `Hide until`, `Parts` or `Doer` not in its form: read as the field absent, a `Kind` outside the five
>       as a to-do, shown; a `Doer` that reads but is spelled with more than one space, or a tab, after `team`: read;
>       a `Kind` in the wrong case: read as that kind; a `Due` on an `fyi`: read as `fyi_due`; a field its kind does
>       not take (`Parts` or `Lifts` on any kind but `decide`, `Doer` on any kind but `act`, `Answers` on a kind
>       that takes none): read as written, as on a v2 line.
>   15. `board_dir_problems() only`: a `Closed:` in its form on a file outside `archive/`: read as closed.
>   16. `board_dir_problems() only`: an archived file in a month that is not its `Closed:` date's: read as closed.
> - **The readers take the `Board`**: `needs_you()`, `covers()`, `sweep()`, `board_problems()` and the merge gate's
>   verdicts; `board_people()`, `answered_by()`, `people_problems()` and `answered_by_problems()` read its preamble,
>   every line of `README.md` on a `"dir"` board and the lines above the first item on a `"file"` one, as `board.py`'s
>   `who_answered(board, by)` does through `board_people()`; and a consumer calls `version_problem(board)` before
>   it trusts the rest. Each of these that also takes a v2 board's text tells a `Board` from the text by its type
>   (`isinstance(x, Board)`). `people_problems(board)` and `answered_by_problems(board)` of a `Board` give `(path,
>   problem)` pairs, the path `README.md` for a board read from a directory and the basename of `Board.path` for
>   one read from a file; a missing `People:` or `Answered by:` line is named under that path too.
>   `board_problems()` of a v2 board's text gives what it gave before, and raises `Refused` for a `board` read from
>   a file (*The gate*). `item_record()` gives an item's record, of either major, with `text` the item's words and
>   no `line`, and these keys (v3.0), every other key as before: `id`, a string `"YYYY-MM-DD-<8 hex>"`, or `null`
>   for a v2 line with no readable date; `path`, a string, the file's path in the directory (`""` for a v2 item);
>   `added`, `"YYYY-MM-DD"` or `null`; `context`, a string, the Context without its final period, or `null` for an
>   item with none; `refs`, as before, the refs of `context` (*The board*, `Context:`), so a v2 item's never one
>   read from a reply; `closed`, `{"date": "YYYY-MM-DD", "why": <string> | null}` (both `null` for an archived file
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

**9. *Edits*** is replaced by the text below, at B5 (round 7's F92). Until then the v2 writers run and their prose
stands: B1 adds the text after *Edits* under the heading `## Edits (v3.0)`, and B5 removes v2's *Edits* and renames
that heading `## Edits`.

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
>   lifting one, and refuses any other answer (`closes()` says when to pass it). An answer that fills one of the
>   item's forms is written as its fill, the head as offered (v2.8); one that is a form as offered, unfilled, is
>   refused (*<head> needs its words*);
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
> - a `decide` carries two or more distinct answers, at most one marked ` (default)` and never a form (v2.8), no two
>   forms with one head (v2.8), and a detail block; `decided_file()` writes no mark on a form, its `default` naming
>   one written unmarked;
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
> `[]`. One whose Context or parts the check `item_file()` shares faults gives `item: <that fault>` alone (v3.0, for
> an item file and a v2 line alike; `line: <that fault>` before it), the fault
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
> *The item file*); a kind's rules (*A new item*; a decided file may carry any answers or none, and the form rules bind an open `decide`
> with no `Decided` alone); a body of detail
> bullets; a Log, when there is one, last and holding replies alone; one blank line between the parts and one
> newline at the end. It never judges the detail block's words. `canonical_item_file(text)` rewrites a file into
> that form: line endings normalised to `\n`, the known fields in their order and spelled so, any other field after
> them in the file's order, one blank line between parts. It refuses a header block it would have to lose or repeat
> a line of (a line that is no field, a repeated field), and its result reads back the same item. No key rests on a
> file's spelling, so it rewrites any field.
>
> **The gate** is `board_problems(board, old)` (v3.0, both `Board`s, `old` read whole): first `README.md`'s
> `People:` and `Answered by:` problems (`people_problems()`, `answered_by_problems()` of the board, the `(path,
> problem)` pairs as they come, each `("README.md", problem)`), then `item_file_problem()`'s fault of each open item whose id no item of `old` (open or
> closed) has, as `(path, problem)`, and, on a new `decide` whose Context names a gate, `decision (<person>)`, a
> `People:` line that does not list that person. `old` may be a v2 board (a split's base) or None (every open item
> judged). An edit keeps an item's id, so an item is judged once, when it is added; damage a hand edit does to a
> file already there is `board_dir_problems()`'s to name. It refuses a `board` read from a file (`form` `"file"`,
> whatever its `major`), raising `Refused`.
>
> **The commit subject of a board write** is one line: `<tool>: <action> <id> <head>[ to <date> | : <answer>]
> (session <name>)` for the five edits, and `<tool>: append <id> <head> (session <name>)` for a new item (v3.0). The
> head is the item's words (its heading), every `*` dropped and whitespace collapsed, at most 60 characters, never
> cut at a ` — ` or a field's name; `<name>` is the caller's session, else the item's `Session` name, else `n/a`; a
> reply's words never appear. `subject_id(line)` reads the id back, or None. `edit_action()`
> reads the action back (v2.3). Subjects written before v3.0 still read: a v2 edit's and append's, with no id; those
> written before v1 by one consumer (`shiftlead: board|answer <head> (from <ref>)`, `shiftlead: board decide <ref>
> (person)`), as appends; and `<tool>: archive <n> closed items (session <name>)`, which no v3 writer writes.
> `subject_kind()` names a subject `edit`, `append`, `archive` or (a rank write) `queue`.

**11. *The ledger as a directory*, *The caller does the I/O*.** "`ls(path)` returns the names of the files directly
in the directory `path` (no subdirectories), or None when `path` is not a directory;" becomes:

> `ls(path)` returns the names directly in the directory `path`: its files' names, and from v3.0 each
> subdirectory's name followed by `/`, which `load()` and `entry_path()` ignore (a v2.x caller's `ls` that lists
> files alone still reads a ledger); or None when `path` is not a directory;

**13. *Appendix: grammar*.** The opening sentence's list gains "v3.0: the item file"; *The open item line (v2.3)*
becomes *The open item line (v2.3; a v2 board's, read only from v3.0)*. After it, add:

> ### The item file (v3.0)
>
> An item file as the writers write it (*The form the writers write*): a text `item_file_problem()` gives None for.
>
> ```ebnf
> item-file      ::= "## " item-text #xA #xA item-header ( #xA #xA item-body )? ( #xA #xA item-log )? #xA
> item-text      ::= nonspace ( char* nonspace )?
> item-header    ::= ( kind-field #xA )? added-field ( #xA session-field )? #xA context-field ( #xA parts-field )?
>                    ( #xA doer-field )? ( #xA due-field )? ( #xA hide-field )? ( #xA answers-field )?
>                    ( #xA lifts-field )? ( #xA decided-field )? ( #xA closed-field )?
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
> `item-header` gives the fields' order, each at most once, with `added-field` and `context-field` always. What the
> productions leave to prose: `parts-field` only on a `decide`, `doer-field` only on an `act`; a
> `due-field` on every kind but `fyi`; answers as *A new item* says a kind takes them, and a `lifts-field` only on
> a `decide`, each label one of its answers once and never `Go` alone; a decided file has no `session-field` and may
> carry any answers or none. Which labels are forms (*The board*, the `Answers:` bullet) is a reading of an
> `item-label`, as its consequence split is: the productions accept every form as a label, and a fill is a
> `Decided` text, which they accept as any (v2.8). An `item-label` holds no ` — ` and does not end in ` (default)`; a `reply-by` is at most
> 40 characters and ends in no whitespace; a `date` is a day of the calendar. A `doer-field` names a team only after
> the word `team` and one space, so `**Doer:** team` names the repo `team` (`doer_value()` also reads a run of
> spaces or tabs there, a spelling `item_file_problem()` faults). A `doer-repo` is a `repo` whose last
> part, `doer-part`, is a `repo-part` that does not end in `.`. Every other production is the one above it of the
> same name (`date`, `digit`, `char`, `nonspace`, `head-name`, `entry-id`, `repo`, `repo-part`, `person`,
> `person-part`, `answer-sep`, `label-start`, `label-char`).

The field order is a production (round 9's F148, reopening F78), not prose: `tests/test_grammar.py` translates the
start to one regular expression (`regex()`, every name inlined) and `fullmatch`es every fixture of every group
against it, asserting the module's verdict, so an unordered `item-field` alternation would accept a file with its
fields out of order that `item_file_problem()` refuses, and the fixture "a field out of order (refused)" would fail
the parity test. `item-header`'s optional fields in sequence accept exactly the ordered blocks. What stays prose
(a kind's fields, a `reply-by`'s length and end) no fixture may turn on: each fixture is a whole file judged both
ways, so a group's accepting fixture is a file of a kind that takes its field, and no refusing fixture's only fault
is a prose rule.

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
- *`Doer:`* (v2.8's paragraph after *`Parts:`*, TD-065's text 1, D12): "It is
  part of the item key" becomes "On a v2 line it is part of the item key"; "`item_line(doer=)` and `board.py add
  --doer` write it" becomes "`item_file(doer=)` (v3.0; `item_line(doer=)` before it) and `board.py add --doer`
  write it"; and it gains at its end "In an item file (v3.0) it is the header field `Doer` (*The item file*), a bare
  value read by `doer_value()`; `parse_doer()` reads a v2 line's." Round 8's F128 adds two: "`item_problem()`
  faults it on any kind but `act`, no kind included" becomes "`item_problem()` faults it on any kind but `act`, no
  kind included (v2; in an item file `item_file_problem()` does, v3.0)", and "any spacing and an absent period
  included, which `item_problem()` faults" gains "(v2)" after "faults". Its last sentence is B1's, landing with
  the header field; the key sentence ("On a v2 line it is part of the item key") is B2's, as *`Parts:`*'s "(v2)"
  and *Trailing fields*' key sentence are, since after B2 text 3 says no v3 reader keys an item (round 1's F182);
  the other three substitutions are B5's, with the writer items.
- *Appendix: grammar*, the prose after *The open item line*'s block (v2.8's `Doer:` sentence, round 8's F128):
  "(`doer-repo`, its last part `doer-part`, which is `repo-part` without a final `.`)" gains "; both defined under
  *The item file (v3.0)*" before its closing parenthesis. B1, with the two productions' move (D12).
- *Trailing fields*, `Lifts:`: "It is part of the item key" becomes "On a v2 line it is part of the item key";
  "`item_line(lifts=)` refuses one and `item_problem()` faults one" becomes "`item_file(lifts=)` refuses one and
  `item_file_problem()` faults one (v3.0; `item_line()` and `item_problem()` before it)", and TD-075's sentence
  after it, "`item_problem()` also faults, on an open `decide` with no `Decided:`, …", names `item_file_problem()`
  (v3.0; `item_problem()` before it) (F96). The `Decided:` bullet
  gains at its end: "In an item file it is `Decided: <date>[ by <person>] — <label>` (*The item file*)." The key
  sentence and the `Decided:` sentence are B2's, the writer substitution B5's.
- *The bold head*: gains "In an item file (v3.0) it is read from the heading, as from a line; a heading with no bold
  run has none." B1, with `bold_head()` reading a heading.
- *`Context:`* (round 1's F191; `item_record()`'s `refs` are read here): after "A Context ends where the next field
  begins: … ` Closed:`." add "From v3.0 a v2 line's Context is read with its reply tails taken out, as the gate
  reads it (`_item_gate()`), so it ends at a reply too, and a ref named only in a reply's words is no ref of the
  item: a line whose Context ran into its replies (no ` Due:` before them, as on an `fyi`) reads fewer refs in
  `item_record()`'s `refs` than in v2.x. In an item file the Context is its header value, which holds no reply." B2.
- *Replies*: gains "In an item file (v3.0) a reply is a Log line (*The item file*), and none of this paragraph's
  limits on its words holds: they hold for a v2 line." B2.
- *The detail block*: gains "In an item file (v3.0) it is the body (*The item file*)." B2.
- *`People:`*: "It is read only above the board's first item" becomes "It is read only above the first item of a board read from a file,
  and anywhere in the `README.md` of a board read from a directory"; *`Answered by:`*'s "It is read as `People:` is" then holds for
  both. B2.
- *A closed item*: "(`parse_closed_items(content)`, v2.4, of a board or its archive …)" gains after it "On a v3
  board a closed item is a file under `archive/` with its `Closed:` (*Reading a board*)." B2.
- *The decide lift*: `decide_lift(item_line, entries, …)` becomes `decide_lift(item, entries, …)`, `item` an item
  file's text or a `BoardItem` (v3.0; a v2 line before it), and "the base item line" becomes "the base item". B2.

Text 14's other two bullets (*Versions*' past paragraphs, no build; *The open item line*'s opening sentence, B5's)
stay in TD-070's plan.

**The search.** Each build ends by searching `SPEC.md` for the names v3.0 removes or renames whose text that build
lands, in the sections that text rewrites, and finding each only in a *Versions* paragraph or a v2-tagged sentence
(round 2's F34: a name another build's text still holds is that build's to search). The names, by the section
where `SPEC.md` holds them today:

- **B1** (text 9 but its *gate* paragraph, as `## Edits (v3.0)`): none in *Edits*, which stands for the v2 writers
  until B5 (round 7's F92, F96); `## Edits (v3.0)` holds none of `item_line`, `decided_line`, `item_problem`,
  `canonical_item` (as a whole name: `canonical_item_file` stays) and `archive_subject` outside a v2-tagged sentence. **B5** (text 9's swap) searches *Edits* for
  those five (`edit_line` is not in *Edits*: `SPEC.md` holds it in *The merge gate's verdicts*, B4's, and *The
  board writer*, B3's).
- **B2** (texts 2–6, 8's *Reading a board* and *Damage*, 9's *gate*, 11, 14's reader items): *The board* but its
  *Parts:*, *Doer:*, *Trailing fields* and *The merge gate's verdicts* paragraphs, for `ARCHIVE_AT`, `archive_closed`,
  `closed_items` (as a whole name: `parse_closed_items` stays) and `item_line` (the last in *The gate sweep* and
  *The decide lift*). The *Doer:* paragraph holds `item_line(doer=)`, whose substitution is B5's (text 14), so B2's
  search would find it outside the places it allows (round 1's F177, reopening F34 and F128's family: a paragraph whose
  writer names another build's text still holds is that build's to search).

The B3, B4 and B5 searches are TD-070's plan's.

## Fixtures

All invented names (`pat`, `sam.lee`, `acme/widgets`, `ops`, `host-a`, sessions `w-9`, `lb-x`).

- **`fixtures/item/cases.json` and `expected.json`** (a new runner kind, `item_cases`, beside `edit_cases`):
  - `parse`: a file of each kind and its fields (the runner's `item_fields()`: the `BoardItem`'s fields by name, not
    `item_record()`, whose keys B1 leaves as v2.8 has them, D4, D12); a heading, a Context, an answer, a detail line and a
    reply each holding `Context:`, `Due:` and `Decided:` as words (the case S3 exists for), read as words;
    `**due:**` and `**hide-until:**` read as `Due` and `Hide until`; a repeated field (the first wins); an unknown
    `**Owner:**` field (ignored, in `fields`); `Decided:` with and without `by`, and a label ending `(by Friday)`
    read whole; `Closed:` with and without a why; a `Decided:` and a `Closed:` not in their form (not decided,
    open); an `act` with `**Doer:** acme/widgets` and one with `**Doer:** team ops` (`doer` in its fields); a Log
    line in another shape and one with empty words (no reply); a CRLF file; a file with no heading (None, and its
    problem in `board_dir`); a `## ` heading followed by a non-field line (None: D7's rule wants a header field
    next; round 9's F144); round 8's F119: `**Kind:** ACT` (an `act`), a `Due` of `2026-02-30` and one of `soon`
    (each `bad_due`, as written), an `fyi` carrying a `Due` (`fyi_due`, `due` and `bad_due` None); round 9: a
    `decide` carrying `**Doer:** team ops` and an `fyi` carrying `**Parts:** TD-23` (each read, as v2 reads it), and a
    Context holding U+2028 and `\x0c` (one value, F157); round 1's F195: `closed` set by `parse_item()` from the path
    it is given, one file with no `Closed:` read at `archive/2026-11/<id>.md` (`(None, None)`) and at `<id>.md`
    (None), and one with `Closed:` at each (its `(date, why)` both times), and a path `2026-02-30-abcd1234.md` (`id`
    None, `is_item_id()`);
  - `strings` (B2; round 9's F144): D7's one rule over strings, through `closes()` and `parts_problems()`: an item
    file (read through `parse_item()`), a v2 line, a line's text after its tick, and a v2 board's text opening
    `## Needs the user` with a `decide` line under it (each of the last three read as v2, as today);
  - `compose`: `item_file()` for each kind; a text, a context, an answer, a detail value and a `said` holding
    `Context:` and `Lifts:`, each written (the refusals that go); an `act` with a `doer`; refused: a two-line value,
    a host with no session, an empty text, a `decide` with one answer, a `look` with other answers, an `fyi` with a
    `due`, `lifts` naming a waiting-only answer, `parts` on an `act`, `doer` on a `decide`, a `doer` of `acme.`,
    a `decide` offering `Hold: <note>` and `hold: <why>` (two forms, one head), a `default` of `Hold: <note>`;
    `decided_file()` with a `default` naming a form, written unmarked;
    `decided_file()` with and without `by`, and an answer ending `(by x)`, written;
  - `edits`: each of the five edits on a file, the unknown field and the body kept byte for byte; `due` and `snooze`
    adding their field in its place, one of them with an unknown field between its neighbours (placed after the last
    known field before it); `decide` replacing an earlier `Decided:`; `decide` with `close`, lifting and
    waiting-only; `decide` with `Hold: not yet` on an item offering `Hold: <note>` and listing it in `Lifts`,
    written as `Hold: not yet` and, with `close`, closed `lifted`; `reply` opening the Log and appending to it; an edit of a CRLF file (its new line `\r\n`, every
    other byte kept); refused: any edit of a closed item, a reply `by` holding `:`, a reply with blank words,
    `decide` with `close` and a work order, `decide` with `Hold: <note>` unfilled and with `Hold:` alone;
  - `problems`: `item_file_problem()` passing each writer's file, and faulting fields out of order, a field twice,
    an unknown field, `**Due:**` spelled `**due:**`, a `Parts:` on an `act`, a `Doer:` on a `decide`, two forms
    with one head and a marked form on an open `decide` (and neither faulted on a decided file), a Log not last, a body line that is no bullet (the messages pinned);
  - `canonical`: reordered and respelled fields rewritten, an unknown field placed after the known ones, a CRLF file
    normalised; refused: a header line that is no field, a repeated field;
  - `ids`: `item_id()` accepting `2026-11-11` and `3f9a2c1d`, refusing `2026-02-30`, `3F9A2C1D` and seven digits;
    `is_item_id()` (round 1's F195) passing `2026-11-11-3f9a2c1d` and failing `2026-02-30-abcd1234`, an upper-case
    nonce, a trailing newline and a non-ASCII digit; `item_path()` open and closed, `closed` a `YYYY-MM-DD` string
    (`archive/2026-11/<id>.md` for a close on `"2026-11-30"`, `archive/2026-12/` on `"2026-12-01"`), and raising
    `ValueError` for `2026-02-30-abcd1234` and for a `closed` of `"2026-02-30"` and of `"20261130"` (round 2's F202;
    the runner records each as `{"raises": "ValueError"}`); `key_id()` of a key whose hash a consumer persisted (the case gives the line's text and the 8 hex
    digits that `sha256(item_key("- [ ] " + text))[:8]` gives, computed once by the case's author);
  - `subjects` (moved from `edit/`, with its `subject_kinds` and `edit_actions`): `subject()` for each action and
    `append` with an id, and with `id=None` (the v2 subject, until B5); `subject_id()` of a v3 subject, of a v2 one
    (None) and of a legacy append; `edit_action()` and `subject_kind()` of both majors' subjects;
  - `gate`: `board_problems()` over `Board`s (moved from `edit/`'s `board_problems`): an added item faulted, an edited
    one not, a new `decide` whose gate's person is not on `People:`, a `README.md` holding a `- [ ]` line above its
    `People:` (read), `old` a v2 board (the split PR: nothing new), `old` None, a new `decide` offering two forms
    with one head and one marking a form ` (default)` (each faulted), a `README.md` whose `People:` is faulted
    (`people_problems()`' pair, `["README.md", <problem>]`, as it comes; round 1's F193), and a v2 `board` refused
    (`form` `"file"`; `board_problems()` raises `Refused`, so its expected JSON is the runner's `{"refused":
    <message>}`, round 1's F190, F193).
- **`fixtures/board/`** (B2: every v2 case, a new `twins_across`, an open line on the board and its closed twin in the archive, and a new
  `reply_ref`, round 1's F191: an `fyi` line `Context: TD-1.` with a reply naming `TD-9`, whose record's `refs` is
  `["TD-1"]` and `context` `"TD-1"`, the reply in `replies` alone; their `<case>.v3/` split directories and `board_v3_case` are TD-070's plan's, B5): The v2 cases' JSONs carry v2.8's `doer` already, are left by B1, and are regenerated at B2:
  `board_case` reads through `load_board()`, its records gain `id`, `path`, `added`, `context` and `closed` and keep
  `line` (B5 drops it), their `text` the item's words, their `refs` read from a `context` with no reply (F191),
  `needs_you` rows are `[id, class, days]`, `keys` become the items' ids and `closed` the closed records;
  `twins_across` reads one closed item.
- **`fixtures/board_dir/<case>/`** (a new kind, `board_dir_case`: `board/` and `expected.json`, holding
  `load_board()`'s `form` and `major` (round 1's F190) and `path` (as the runner gave it, relative to the case's
  directory; round 2's F196), items, closed items, people, `needs_you` and `problems`, and
  `board_dir_problems()`): `months` (closed items across three months, read whole and with a `since` inside the
  second, which reads the second and the third: the month equal to `since`'s is read, F195; beside them a directory
  `archive/old/`, named by rule 11 once, in `board_dir_problems()`' output, round 2's F197); `ties` (undated,
  unreadable-due and `fyi` items, and two items of one due date, some added on one day and some on others, ordered
  by id descending: the case that pins v3's tie order); `field_words` (headings and contexts holding field names);
  `unknown_field`; `stub` (the v2 path holding the stub, read as the directory, `form` `"dir"`); `stub_no_dir` (empty, `form` None, the stub
  named); `damage` (a name that is no id, an `Added` not the id's date, a missing `Added`, a `Closed:` not in its
  form, a closed item outside `archive/`, a file inside it with no `Closed:` (read as closed), a wrong month, one id
  twice (an open and an archived copy, the archived read; two archived copies, the later month's read), a file
  `read()` gives None for, a file with no heading, a header-block line that is no field (kept, named); round 6's
  F74: a file directly in `archive/`, a file `2026-02-30-abcd1234.md` (a name that is no id, F195), a directory `archive/misc/`, a directory `archive/2026-13/`, a subdirectory
  `notes/` of the board, a directory inside a month, each named once and not read; F76: a `Kind: banana` item (a
  to-do, in `needs_you`), a `Hide until` that is no day (shown), a `Parts` not in its form (no parts), a `Doer` not
  in its form (no doer), each kept in `fields` and named; F79: a `Doer: team  ops` (read as the team `ops`,
  named));
  `readme_missing` and `readme_v2` (each `form` `"dir"`, `major` 3 and 2, each named; `readme_v2` read as a
  directory in id order, its `README.md` read whole as preamble, F190); `file_v3_items` (a file declaring 3 holding
  items: `form` `"file"`, `major` 3, read as v2, in line order, its preamble the lines above its first item, named;
  F190); `missing` (no path: empty, `form` and `major` None, `path` the path given, F196); `readme_item_line` (a `- [ ]` line in
  `README.md` above `People:`, which is still read); `newer` (a README declaring `Ledgerboard: 4`:
  `version_problem(board)` names it, in D6's words); `readme_major_late` (a README whose `Ledgerboard: 3` stands below a `- [ ]`
  line of prose: `major` 3, read by `board_major()`); `v2_undeclared` (a v2 file with no `Ledgerboard:` line:
  `major` 2, no problem); `v2_duplicate_open` (a v2 file with two open lines of one id: both read with that id, the
  id named once in `problems`, and `board_dir_problems()` giving `Board.problems` alone). `damage` also holds an
  item with a field its kind does not take (round 9: named under rule 14, read as written). **What git cannot
  store** (round 9's F158) is the runner's to make: a case may hold `case.json` beside `board/`, its `unreadable`
  a list of paths under `board/` whose file is present but for which the runner's `read()` gives None (`damage`'s
  unreadable file), and its `path` the path `load_board()` is given, relative to the case, which need not exist
  (`missing` gives `"absent"`, no file and no directory: git stores no empty directory, so an empty `board/` cannot
  stand for it).
- **`fixtures/sweep/`**: `cases.json`'s boards may name a `dir` (a v3 board) in place of `board` and `archive`; the
  runner reads either through `load_board()`, whole (a change to `sweep_cases`), and its rerun step closes by id and
  files with `item_file()`; one v3 board and one v2 board in the set, and a v2 board beside its split giving the same
  `to_file`, `to_close` (ids) and `lifts`, compared as D6's *Comparing two reads* says (`to_close` and `lifts` as
  lists sorted by id); an `audit_old` case (the `; board <repo>` audit's decided item closed in a
  month before the Log line's, found); an `owing_old` case (an answer owing a lift archived months back, which keeps
  the unlifted act open). **The rerun of a v2 board** (round 9's F150, reopening F96, F125) ticks its closed lines
  with `is_open_item()` and `item_key()`, both kept, and files with `item_line()` until B5; at B5, which removes
  `item_line()`, the rerun runs over each v2 board's split (`split_board()`, then the first run's closes as moves
  by id and its filings with `item_file()`), so it calls no removed writer, and `expected.json`'s `rerun` is
  unchanged (a rerun files and closes nothing, and the split keeps the ids).
- **`fixtures/lift/`**: `decide_lift()`'s items become item files (B2). At B5 (round 9's F150) the groups that call
  a removed writer or a line's string form move to item files, `lines` becoming one item file per case line: `closes`
  passes each file (D7's rule), `close` runs `edit_item(file, …, close=True)` where it ran `edit_line()`,
  `item_lines` becomes `item_files` (the waiting-only refusals of `item_file(lifts=)`), and `item_problems` becomes
  `item_file_problems` (`item_file_problem()`); `closed_items` (`parse_closed_items()`, kept) prints `words` from B2;
  `expected.json` regenerates with the same verdicts.
- **`fixtures/grammar/cases.json` and `expected.json`**: a start `item-file`, judged by `item_file_problem()`,
  with a group for every production the start reaches (round 6's F78: `tests/test_grammar.py` asserts the groups
  are exactly `names_used()` of the start): `item-file`, `item-text`, `item-header`, each field production,
  `item-answer`, `item-label`, `item-body`, `body-line`, `item-log`, `reply-line`, `reply-by`, and the shared ones it
  reaches (`date`, `digit`, `char`, `nonspace`, `head-name`, `entry-id`, `repo`, `repo-part`, `person`, `person-part`,
  `answer-sep`, `label-start`, `label-char`, `doer-repo`, `doer-part`, and any other `names_used()` gives), each with
  an accepting and a refusing fixture: among them a context holding `Due:` (accepted),
  `**Decided:** 2026-11-12 by pat — Go (by Friday)` (accepted), `**Doer:** team ops`, `**Doer:** acme/widgets` and
  `**Doer:** .github` (accepted), `**Doer:** acme.` (refused), a field out of order (refused: `**Due:**` above
  `**Context:**`, in `item-header`'s group, which `item-header`'s sequence refuses as `item_file_problem()` does,
  round 9's F148) and a reply-by holding `:` (refused: the Log line `- 2026-11-12: a:b: words` in `reply-by`'s
  group, which no colon-free `reply-by` followed by `: ` matches, as the module reads no reply from it). Every
  fixture is a whole file; none turns on a prose-only rule (text 13).
- **`fixtures/edit/cases.json`'s groups**, each placed: `compose`, `edits`, `item_problems`, `canonical_items` and
  `archive_subjects` retire with the v2 writers (B5); `subjects`, `subject_kinds` and `edit_actions` move to
  `item/`'s `subjects` (B1); `board_problems` moves to `item/`'s `gate`, over `Board`s (B2); `item_keys` stays (the
  v2 reader and `key_id()`'s input); `item_notes` stays, its items given as `BoardItem`s of either major (B2);
  `bold_heads` stays, gaining a heading case (B1): `Ask — pat, 2026-01-05: **hm**` read with `heading=True` gives
  `hm`, where the line's read gives None (round 9's F167); the rest (`today`, `predicates`, `versions`, `not_right_forms`,
  `not_right_fills`, `queue_subjects`, `implicit_keys`, `key_orders`, `midpoints`, `rank_reads`, `rank_writes`,
  `rank_paths`, `components`, `respaces`, `split_notes`, `forms`, `form_fills`; round 9's F161) are untouched.
- **The runner** (`fixtures/run.py`): `fs_ls` lists subdirectories with `/` (B2); the kinds `item_cases` (B1) and
  `board_dir_case` (B2) join `cases()`; `grammar_cases()`' `judge` gains `"item-file"` → `item_file_problem()` (B1,
  round 1's F179); `board_case`, `sweep_cases` and `lift_cases` read through `load_board()` (B2); `board_dir_case`
  reads a case's `case.json` (`unreadable`, `path`, F158). B5's runner changes (`board_v3_case` and
  `board_split_case` joining `cases()`, `archive_case` and the retired groups of `edit_cases` going, and
  `lift_cases`' `close`, `closes`, `item_lines` and `item_problems` groups and `sweep_cases`' rerun moving as their
  bullets above say, F150) are TD-070's plan's, B5 (round 1's F186).

**Unit tests** (`tests/`), each file given its build (round 9's F149):
- **B1**: `tests/test_item_gate.py` gains the item-file properties (every file `item_file()` or `decided_file()`
  writes passes `item_file_problem()`, as does each after any `edit_item()` it does not refuse, and
  `canonical_item_file()` returns each unchanged) beside its v2 ones, which stay; `tests/test_grammar.py` is
  unchanged in code and reads text 13's start and its fixtures (F148: the order is a production).
- **B2**: `tests/test_ledgerboard.py`'s `parts_problems()` assertion of `line: …` becomes `item: …` (F132); its
  `sweep()`, `needs_you()` and preamble tests pass unchanged, since each reader still takes a v2 board's text.

The other cases (`fixtures/board/<case>.v3/`, `fixtures/board_split/`, `fixtures/board_writer/`,
`fixtures/verdict/`, the retired groups) and B3's to B5's unit tests are TD-070's plan's.

## The builds

Each is filed `Part of: TD-070` on Paul's Go after the rounds, and lands its SPEC text, code and fixtures together.
**Preconditions of B1** (D12): TD-065's B1 (TD-083) and TD-075's B1 (TD-084) have merged, so they block nothing
(round 8's F129); B1 is filed `Blocked by: TD-088, TD-089, decision (paul)`, TD-078's B1 (TD-088) and B2 (TD-089)
(round 9's F142; D12 gives the Ask), and both have merged (859f6b3, f9db4f1; round 9's F159), so B1 waits on the
decision alone; whatever `main` carries past v2.7 (today TD-079, TD-080, TD-083, TD-084, TD-088 and TD-089) is
released as the last v2.x minor, v2.8, before B1 merges, Paul's `decision (paul)` saying he has cut it. No release is cut between B1 and B5. Each build
leaves `main` green: where a later build retires a v2 name an earlier build would break, the earlier build keeps it
working (a shim) and B5 removes the shim. **What a record shows** changes at B2 and B5 alone (D4, round
2's F33, round 3's F46; `doer` is v2.8's, round 7's F91);
each build below names the expected JSONs whose records it regenerates. **Each build's `SPEC.md` search** is the
section *The search* (after text 14), for that build's names; B5's is the full one (round 1's F181).

**B1, the item file.** D3, D4, D7's module half. Location: `ledgerboard/__init__.py` (`ITEM_ID_RE`, `is_item_id()`
(read by `item_id()` and `parse_item()`'s `id`, round 1's F195), `item_id()`, `key_id()`, `item_path()` (`closed` a
`YYYY-MM-DD` string, `ValueError` for a non-id, F195, and for a `closed` failing `_real_day()`, round 2's F202), `parse_item()` (filling `words` with the heading, and
`closed` from its path, F195), `BoardItem`'s new fields,
`BoardItem.doer`'s v3 reading through v2.8's `doer_value()` (the field and the record's `doer` are v2.8's), `item_file()`
with `doer`,
`decided_file()`, `edit_item()`, `item_file_problem()`, `canonical_item_file()`, `subject()` gaining `id=None` (None
gives the v2 subject the v2 writers still call), `subject_id()`, `bold_head()` reading a heading whole (F162),
`_context_gate(context)` with `_item_gate(text)` calling it (F151), `parse_item()` and `edit_item()` cutting lines
at `\n` alone (F157) and reading a field on any kind (F147)), `SPEC.md` (text
8's heading, intro paragraph, tree and *An open item* bullet (F175), *The item id* (with `is_item_id()`,
`item_path()` and `key_id()`'s definition, F194, F195) and *The item file*, 9 but its
*gate* paragraph, 13 with `item-header`, F148), `fixtures/item/` (but `gate`
and `strings`), `fixtures/grammar/`, `fixtures/edit/`'s subject groups moved, `fixtures/run.py` (`item_cases`,
`item_fields()`, and `judge["item-file"]` → `item_file_problem()` in `grammar_cases()`, whose `judge` names each
start, F179; `item_cases` recording a raised `ValueError` as `{"raises": "ValueError"}`, the `ids` case's non-id, F195), `tests/test_item_gate.py`'s item-file properties (F149).
Text 8's `parse_item()` paragraph lands without its closing `item_record()` sentence, its *The item file* without
the clauses naming `board_dir_problems()`, and text 9 without its *snapshot* paragraph (each B2's: *The SPEC text
the build lands*, round 4's F59, round 6's F77); text 8's *An open item* bullet without "Closing an item moves its
file in the same write", its *The item id* without "The writer draws the nonce …", and text 9 without "; the writer
moves it in the same write" (each B3's, TD-070's plan, F175); its *The item id* also without "A v2 item's id is its
line's date and `key_id()` of its key (*Reading a board*)." (B2's, round 2's F201); text 14's *bold head* bullet and its grammar-prose
`Doer` bullet are B1's. `parse_item()` reads `Kind` and `Due` as D4's F119 bullet says; `subject(…, id=)` makes its head from the
words, never through `edit_head()` (D7, F117).
**Records:** `item_record()`'s keys do not change at B1: its `doer` key is v2.8's already (TD-065's build), and B1
regenerates no record (D12).
`fixtures/edit/expected.json` changes only by the groups that move to `item/` and `bold_heads`' heading case.
**`Doer`:** B1 lands the v3 field (D4, D12: v2.8's `doer_value()` reused, text 8's *The item file*, text 13's `doer-field`,
and text 14's `Doer:` bullet's last sentence). `BoardItem.doer` and the record's `doer` are v2.8's and stay, and
`doer-repo` and `doer-part` move from *The open item line*'s block into text 13's (a production is defined once).
Done when: TD-078's B1 (TD-088) and B2 (TD-089) have merged (met, F159), the last v2.x minor holding them (v2.8, D12) is tagged, the
precheck is green, every fixture above passes, and *The search*'s B1 search finds its names only where it allows.

**B2, reading.** D5, D6, D9. Location: `ledgerboard/__init__.py` (`Board` with `form`, on which the preamble
readers, the order, `board_problems()`' refusal and `board_dir_problems()`' checks turn, `major` for the version
check alone (round 1's F190), and `path`, the path `load_board()` was given (round 2's F196), `load_board()` (`since` reading its own month, F195), `item_words()`, the
twin rule across board and archive, the stub's reading, the duplicate-id read, `Board.problems`,
`board_dir_problems()` (no `since`: the whole tree, round 2's F197); `BOARD_MAJOR = 3`, `board_major()`, `version_problem()` taking a `Board`; `needs_you()`,
`covers()`, `sweep()` (whole boards), `board_problems()`, `board_people()`, `answered_by()`, `people_problems()` and
`answered_by_problems()` over a `Board`, each still taking a v2 board's text as before until B5, so `board.py` runs
unchanged until B3 (each telling the two apart by `isinstance(x, Board)`, round 2's F198; `people_problems()`
and `answered_by_problems()` of a `Board` giving `(path, problem)` pairs, `README.md` on a `"dir"` board and
`Board.path`'s basename on a `"file"` one, a missing line's message among them, round 2's F196; and
`board_problems()` of text giving today's result, of a `"file"` `Board` raising `Refused`; round 1's F193); `parse_board()` filling every new `BoardItem` field (`detail_source` is
B3's, TD-070's plan; round 1's F184, F194) and the ids (`session`, `host` from
`item_head()`, `replies` from `parse_replies()`, `context` from `CONTEXT_RE` over the line with `reply_span()`
removed, round 1's F191); `context_refs()`, with `item_refs(text)` calling it, and
`item_record()`'s `session`, `host`, `refs` (`context_refs(item.context)`, F191) and `replies` read from the fields (D4, round 8's F123); `item_record()`'s B2 change
(D4: its `text` reading `words`); `parse_board()` filling `words` (`item_words()`) and keeping `text` the line's
text after its tick, as today (D4's *`words` and `text`*), `closed` with D11's why (F160), and `fields` with a
value not in its form as the line's text (D4, D11's `Doer` bullet, F176); `_item_gate()` taking a `BoardItem`,
`_context_gate()` of its `context` (F151), and `closes()` given a `BoardItem` reading its fields; `_dict_ls()` listing
subdirectories (D6); `parts_problems()`, `decide_lift()`, `closes()` over a file, each still taking a v2 line until
B5, a string told apart by D7's one rule (round 8's F124, round 9's F139: an item file's first non-blank line opens `## ` and its next is a header field); `parts_problems()`' prefix
`item:` for both (F120)), `SPEC.md` (text 2 (without the words B5 adds), 3–6, 8's *`README.md`* and *No sections*
bullets (the latter without B3's `board.py show` clause, F175), its *Reading a board* (without "and no `line`", B5's,
and its *The readers take the `Board`* bullet without "and the merge gate's verdicts", B4's, and the
`who_answered(board, by)` clause, B3's; round 1's F192),
its *Damage*, its *The item id*'s v2-id sentence (round 2's F201), its `parse_item()`
paragraph's `item_record()` sentence and *The item file*'s `board_dir_problems()` clauses, 9's *gate* and *snapshot* paragraphs, 11, 14's reader items, the *`Context:`* one among them, F191),
`fixtures/board/` (regenerated, `twins_across`, `reply_ref`, F191), `fixtures/board_dir/`, `fixtures/item/`'s `gate` and `strings`,
`fixtures/sweep/`, `fixtures/lift/`, `fixtures/run.py` (`fs_ls`, `board_dir_case` with `case.json`, F158, `board_case`, `sweep_cases`,
`lift_cases`; the runner's two reads of `BoardItem.text` move off it, so B5's removal changes no expected JSON:
`lift_cases`' `closed_items` prints `words`, and `sweep_cases`' `covers` the item's id).
`load()`, `entry_path()` and `v2_problems()` need no change for `fs_ls`'s new `archive/` name: each
takes only the names `ENTRY_FILE_RE` (`^TD-(\d+)\.md$`) matches. **Records:** `item_record()` gains `id`, `path`,
`added`, `context` and `closed`, keeps `line`, its `text` becomes the item's words, and a v2 record's `refs` drops
an id read only from a reply's words (round 1's F191; no existing `.md` under `fixtures/` holds such a line, checked 2026-11-13, so only
`reply_ref` shows it); the expected JSONs it
regenerates are `fixtures/board/`'s `answers.json`, `basic.json`, `doer.json` (round 8's F122), `hidden.json`,
`lifts_parts.json`, `people.json` and `shared_part_left_open.json` (records, `needs_you` rows by id, `keys` as ids,
`closed` as records), and `fixtures/board_writer/list/expected.json` (`board.py list` prints `item_record()`; no
other writer case prints a record); besides records, `fixtures/sweep/expected.json` (`to_close` by id, and its
`parts_problems()` rows `line: <fault>` become `item: <fault>`, round 8's F120; no other expected JSON holds the
prefix, and no writer case reaches a shared fault, since `item_file()` refuses the item first; `tests/test_ledgerboard.py`'s
`parts_problems()` assertion of `line: …` changes with it, round 8's F132),
`fixtures/lift/expected.json` (`decide_lift()`'s items as files) and `fixtures/edit/expected.json`
(`board_problems` moved to `item/`'s `gate`, `item_notes` over `BoardItem`s) regenerate. Done when: the precheck is
green, those fixtures pass, every existing `fixtures/verdict/` case passes unchanged (the verdicts still read v2
trees, and a v2 item's `text` is still its line), and *The search*'s B2 search finds its names only where it allows.

B3 to B5 (the writer, the merge gate's verdicts, and migration with the release's removals) are designed in
TD-070's second part, a design entry filed once this one converges. On Paul's Go after these rounds, B1 and B2 are
filed `Part of: TD-070` and may build before B3–B5 are designed: no release is cut between B1 and B5, so a change
the second part needs in them is a build of its own before v3.0.

## Not in this design

B3–B5's subjects, all TD-070's plan's and its second part's: the writer (D2's moves on close, D7's `board.py` by
`--id`, B3), what a person reads (`board.py show`, D8), the merge gate's verdicts (D10, B4), migration and the
split (D11, B5), the release and its removals (D12, B5), and each consumer's v3.0 entry (*Consumers*); and what
TD-070's plan's *Not in this design* leaves to TD-078 and to Paul.

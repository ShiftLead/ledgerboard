# TD-070: the board as a directory, one file per item, for v3.0

**Status:** Draft 1, 2026-11-11 (session lb-designer). Paul answered **Go** to the scope as drafted (S1–S10,
TD-070's `decision (paul)`, 2026-11-11): every recommendation in it stands. This draft turns the scope into the full
design: its decisions, the exact `SPEC.md` text, the fixtures and the builds. No review round has run yet. Class:
**wide** (a new major of a vendored, published format, read and written by both consumers; cap 6 rounds,
cadence.md §4.8).

**Entry:** [TD-070](../ledger/TD-070.md). **Source:** the entry's Why and Fix; the scope (S1–S10, kept as each
decision's source below); [target design](target-design.md) §7.1's v3.0 row; `SPEC.md` *The board*, *Edits*, *The
board writer*, *The merge gate's verdicts*, *The ledger as a directory* (the precedent), *Ledger entries and their
edits* (the grammar the item file reuses); both consumers' pinned code, read 2026-11-11 (cited by file and function).

## The problem

A board is one Markdown file, and every new item is written at one place in it: `board.py add` puts it above the
first item of its section (`plan_add()`). Two PRs that each add an item always conflict, and GitHub's merge runs
no merge driver, so each collision costs a rebase and a full precheck. No layout inside one file avoids it: two
inserts at one anchor conflict wherever the anchor is. agent-cadence's `board_edit.py replay` (its TD-248) does
the rebase's hand edit, not the rebase.

The conflicts are real but not the case for a major. Counted on 2026-11-11 from one machine's session transcripts
since 2026-10-12: about 140 conflict events on v1 ledger files, 3 on v2 ledger directories, 7 on boards (a floor).
The case is **the item's shape**. A `decide` item is a line of up to a kilobyte or more (this repo's board holds
closed lines of up to 1,083 characters, open ones of 197 to 615), with a detail block and a life of its own: open,
decided, closed, archived. That is an entry's shape, and the single line carries costs an entry does not:

- **Its identity is its text.** The item key is the line with some fields cut out. Consumers persist it
  (ShiftLead's work orders are `board:` and 8 hex digits of its hash, `sessionorc/workorders.py` `key()`), so what
  the key is for a line is part of the format, and every new field has had to decide whether it is in the key
  (`Hide until:` in v2.3, `Parts:`, `Lifts:`, TD-065's `Doer:`).
- **Fields live inside prose.** A Context ends where the next field name begins, so the writer refuses any text,
  answer, detail value or reply that holds a field name, every new field widens that refusal and can re-read an old
  line, and a `Decided:` answer may not end in `(by …)`.
- **Two copies of one item are the merge rule.** An open and a closed line with one key mean "closed: a merge kept
  both sides", and `archive_closed()` carries twins, its refusals and the `ARCHIVE_AT` threshold. This repo's board
  holds 32 closed items, over three times the threshold, because archiving is a separate PR nobody owes.

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
needs you" (v2.0's ledger took that cost: a missing ledger reads as no work, which a reader notices). With (b), a
v2.x reader that checks the version refuses the board and says to vendor a newer release, and a caller configured
with the old path reads the directory through it (D6). **(b)**, a file no write touches after the split.

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

**D3. The item id (S2).** `YYYY-MM-DD-<8 hex>`: the item's `Added` date, a hyphen, eight lower-case hex digits
(`ITEM_ID_RE`, `^\d{4}-\d{2}-\d{2}-[0-9a-f]{8}$`, the date a real day; `item_id(added, nonce)` formats and refuses
anything else). The module draws nothing: `board.py add` draws the nonce (`secrets.token_hex(4)`) and draws again,
up to 8 times, while the name is held open or in any archive month. `add --id <id>` takes a caller's id instead (a
service writer that keys its appends on an event, cadence §4.4), refused when malformed, when its date is not the
item's `Added`, or when held. Two changes that add one id conflict as two files at one path, which is the safe
failure; 32 bits within one day make it rare. An id never changes: a retitle, an edit and a close keep it.

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

- **The heading** `## <text>` is the item's words (`BoardItem.text`), one line, any words; the writer trims it and
  adds no period.
- **The header block**, read by `FIELD_RE` and `field_key()` as an entry's (a name in any case, a value's end
  whitespace dropped, the first of a name winning). The fields and their writing order: `Kind`, `Added`, `Session`,
  `Context`, `Parts`, `Doer`, `Due`, `Hide until`, `Answers`, `Lifts`, `Decided`, `Closed`. `Added` and `Context`
  are always written; `Kind` is absent for the kindless to-do; `Session` is `<name>` or `<name> on <host>`, absent
  for `n/a` and on a decided file (`decided_file()`, the v2 `(person)` head). `Parts` is `TD-15, TD-16`;
  `Answers` and `Lifts` are a v2 line's values without the final period, `\|` still a literal bar. `Decided` is
  `<date>[ by <person>] — <label>`; `Closed` is `<date>[ — <why>]`. `Doer` is TD-065's field (v2.8, `<repo>` or
  `team <team>`, on an `act`), carried as a header field if v2.8 has landed; if it has not, TD-065's build adds it
  here instead of to the line.
- **A value is a whole line**, so it holds any words, field names among them: the field-name refusals end, and so
  does reading where a Context ends.
- **An unknown field is kept**: in `BoardItem.fields` (every header field as written, in order), its line kept byte
  for byte by every edit and placed after the known fields by `canonical_item_file()`, and faulted by
  `item_file_problem()` on a file the writers write. A later v3 minor that adds a field changes nothing an older v3
  reader reads of the others.
- **The body** is the detail block: the lines after the header block up to the Log, leading and trailing blank lines
  dropped (`BoardItem.detail`), written by the writer at column 0. No edit touches it.
- **The Log** is the body's last section, led `**Log:**`: the item's replies, `- YYYY-MM-DD: <name>: <words>`,
  oldest first. `<name>` holds no `:` and is at most 40 characters; a Log line in any other shape is kept and read as
  no reply. A reply decides nothing, as on a v2 line.
- **`BoardItem` gains** `id`, `path` (its path in the directory, `""` for a v2 item), `added`, `session`, `host`,
  `context`, `closed` (`(date, why)` or None), `replies` and `fields`; `text` becomes the item's words (on a v2 item,
  as D6 reads them), and a v2 item keeps its line in `raw`. **`item_record()`** loses `line` and gains `id`, `path`,
  `added`, `context` and `closed`; `text` is the item's words.

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

**D6. Reading (S5).** `load_board(path, ls, read, *, since=None)` gives a `Board`: `major` (2 or 3), `preamble`
(`README.md`'s text, or a v2 board's text before its first item), `items` (the open items) and `closed` (every
closed item, the archive's among them), each a `BoardItem` with its `id`.
- **A directory** is read as `README.md`, each `<id>.md` directly in it in id order, and each month directory under
  `archive/` in month order and its files in id order. An open item is one with no `Closed:` (a damaged file aside,
  D11's problems).
- **A v2 file** is read with its archive beside it (`<stem>_archive.md`) exactly as v2.7 read them, twins included.
  Each v2 item's id is its line's date and `key_id()` of its key, the key of `- [ ] ` and the line's text after its
  tick, trimmed (`item_key()`), so it reads with the id its split file gets (D11). A line with no readable date has
  id None.
- **The stub** (D11): a file that declares `Ledgerboard: 3` and holds no item is read as the directory beside it,
  its name less `.md`, so a caller configured with `docs/user_attention.md` reads the board it became.
- **`ls`** lists each subdirectory with a trailing `/` (v3.0; `load()` and `entry_path()` ignore those names).
- **`since`**, a date, leaves out the archive months before its month, neither listed nor read: a reader that
  judges a window reads only its months (D9).
- **Order:** `items` are in id order on a v3 board, line order on a v2 one, and *What needs the person*'s ties fall
  back to that order: a v3 board's ties (undated, unreadable-due and `fyi` items) go oldest first.
- **The readers take a `Board`:** `needs_you(board, today)`, `covers()` and `sweep()` (whose board is
  `(origin_url, basename, board)`), `board_problems(board, old)`, and the verdicts through their trees.
  `board_people()` and `answered_by()` read `board.preamble`. `parse_board(text)` stays as the v2 half of
  `load_board()`; `parse_item(text, path="")` reads one file. `version_problem(board.preamble)` is the caller's check,
  as before.

**D7. The edits and the writers (S6).** `edit_item(text, action, *, to, answer, why, reply, by, today, close)` is
`edit_line()`'s five edits over an item file: snooze, due, done and decide each set one header field (adding it in
its place in the order), reply appends one Log line (opening `**Log:**` after the body when there is none); a closed
item is refused; each is read back. `item_file(…)` takes `item_line()`'s arguments and gives a file; `decided_file(…)`
takes `decided_line()`'s. Their refusals keep what still means something (a value of more than one line, a host with
no session, a kind's rules, `Parts:` and `Lifts:` rules, a look's fixed pair, a doubled Recommended label, a result
that does not read back) and drop the field-name refusals and the `(by …)` one. `item_file_problem(text)` and
`canonical_item_file(text)` are `item_problem()` and `canonical_item()` for a file; since no key rests on a file's
spelling, `canonical_item_file()` rewrites any field. `board_problems(board, old)` judges each open item whose id no
item of `old` has, as `(path, problem)`; it refuses a v2 board. `parts_problems()`, `decide_lift()` and `closes()`
take an item file's text (or a `BoardItem`) where they took a line.

**Commit subjects** keep their shape and carry the id after the action: `<tool>: <action> <id> <head>[ to <date> |
: <answer>] (session <name>)`, `<tool>: append <id> <head> (session <name>)`; `subject_id(line)` reads it back and
`edit_action()` reads the action as before (a v2 reader's `EDIT_SUBJECT_RE` still matches). Subjects written before
v3.0 still read, `archive` among them.

**`board.py`** names an item by `--id` in all five edits; `--line` and `--expect` go (an id cannot move). `add`
writes `<board>/<id>.md`; `done`, and a `decide` that closes, write the archived file and remove the open one as one
write. A write to a v2 board is refused (*split first*); `list` and `show` read one. `--board` is the directory (or
the stub, or a v2 file for the reads).

**D8. What a person reads (S8).** `board.py show [--hidden]` prints `show_board(board, today, hidden=False)`: for
each item `needs_you()` gives, in its order, the line `*<id> · <class>*`, then the item's file as stored, items
separated by one blank line; with `--hidden`, the hidden open items follow in id order, each `*<id> · hidden until
<date>*`. It reads a v2 board too, printing each item's line and detail block in the file's place. No rendered file
is stored: a stored view is one file every write touches, which is the conflict again.

**D9. The gate sweep over a directory.** `sweep()`'s board is `(origin_url, basename, board)`; `to_close` lists
ids; the close rule and the filing rule match items by id. `sweep_since(entries, today_utc, reask_days=30)` is the
date `load_board(since=)` needs for every board the sweep reads: the earlier of `today_utc − reask_days − 1` and,
for each open entry's `gate lifted: … ; board <repo>` Log line, its date `− 1`. Every closed item the sweep judges
was decided within that window or near such a line, and is closed no earlier than it was decided, so its month is
read: S4's "the last two months" for the default window, never the whole archive.

**D10. The merge gate's verdicts (S7).** The trees are maps from path to text as before. `BOARD_DIR` is
`docs/user_attention`; `BOARD_V2_PATH` and `BOARD_V2_ARCHIVE_PATH` (renamed from `BOARD_PATH` and
`BOARD_ARCHIVE_PATH`) are the v2 pair. A tree holds a v3 board when it holds a file under `BOARD_DIR/`, else the v2
pair; it is read through `load_board()` over the tree. The consumer reads the same paths at the base and the head:
every file directly in `BOARD_DIR` and every archive file the PR changes (an archived item the PR leaves alone
changes no verdict).
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
- every line of one key, across the board and the archive, is one item, closed when one of them is (the twins
  become one closed item); it becomes `<id>.md`, or `archive/<YYYY-MM>/<id>.md` when closed, its id as D6 gives the
  v2 item (`key_id()`), so a consumer that persisted `board:<8 hex>` finds its item by the id's last 8 digits;
- its fields are the v2 reader's, rewritten into the file's forms; its body is the detail block, common indent
  removed; its replies are the Log; its heading is the words the v2 reader reads as no field, in their order,
  whitespace collapsed (the text, and any words a hand edit left outside the fields), so no word is lost;
- `README.md` is the board's text before its first item, `Ledgerboard: 3` under its title, less the `## ` heading
  that opened the items' section, each relative link gaining `../`;
- it refuses prose among the items, an item with no date, two open lines of one key, two closed lines of one key,
  two items given one id, and a result that does not read back the same items or that `board_dir_problems()`
  flags.

`board_stub(title, name)` is the stub `board.py split` leaves at the v2 path. `split_board_notes(readme)` names
README lines that may describe the v2 board. `board_dir_problems(path, ls, read)` is `v2_problems()`'s twin.
`key_id(key)` is kept through v3.x. The split runs in each consumer's v3.0 vendor PR, beside v3.0's ledger half
(TD-078), landed when no open PR edits the board (each such PR is redone over the directory).

**D12. The release: v3.0.** A major (*Versions* text 12). It reads v2 boards and writes v3 only. It goes out with
TD-078's ledger half as one v3.0; when, and what else it carries, is Paul's. No v2.x release is cut from `main` once
B1 merges (Open for round 1).

## Consumers

Both change in their v3.0 vendor PR, each through an entry filed in that repo through its question seat once v3.0
is cut, agent-cadence's first. Each line below is a line for that entry, never code here.

- **agent-cadence**:
  - vendor v3.0 and run `board.py split` on `docs/user_attention.md` in the same PR, landed when no open PR edits
    the board;
  - `board_edit.py` over `board.py`'s edits by `--id` (its `--line`, `--expect` and their exit-3 refusal go);
    `replay` (TD-248) retires, there being no single file to replay into;
  - `nudge_user_attention.py`: read boards through `load_board()` (its own checkout's directory; another repo's
    through the forge's directory listing, with `since=` the months it shows); its `ARCHIVE_AT` prompt and its
    duplicate-key warning (`closed_items()`, `item_key()`) go; `--report --json` prints ids, not lines;
  - `check_cadence.py`: `BOARD` becomes the directory; `classify_direct()`'s stamp is `README.md`'s stamp lines
    alone, its board-append is item files added directly under the directory, each with a `Due:` (its `## Needs`
    test becomes the kind test it stood for, its choice), its board-edit is one item file changed in place or moved
    into `archive/` under an edit subject; `row_board_edit_pr()` the same;
  - `list_sessions.py` `board_items()`: open items' `Session` through `load_board()`;
  - the own-board path in `cadence_hooks.sh` and `check_claude_memory.sh`; cadence.md §3, §4.3 and §4.4,
    `docs/procedures/stranded-work.md`'s stamp step (`README.md`), and the board's SEED skeleton (no `Format:` line
    for the item line, no sections, closing archives).
- **ShiftLead** (after agent-cadence's vendor PR, through its pin):
  - work orders become `board:<id>`; a persisted `board:<8 hex>` (`sessionorc/workorders.py` `key()`) resolves to
    the item whose id ends `-<8 hex>`, which `split_board()` gives every migrated item;
  - `sessionorc/board.py`: `add()` and `add_decided()` drop `under=NEEDS`, its edits pass `--id` (`plan_edit()`'s
    line and expect go), `item_line()`/`decided_line()` become `item_file()`/`decided_file()`;
  - `gatesweep.py` `board_of()` reads the directory at the ref (`BOARD_DIR`, an `ls`/`read` pair over `git ls-tree`
    that lists subdirectories) with `since=sweep_since()`, and closes by id;
  - `workorders.board_items()` reads `load_board()` and `needs_you(board, today)`, keyed by the record's `id`;
  - the repo's `board:` setting (`repoconfig.py`) defaults to the directory where it exists, else the v2 file; the
    Inbox draws a board item from its record's fields rather than cutting its line.

## The SPEC text the build lands

Each block is what `SPEC.md` says once built. Where a block names a substitution in a paragraph it keeps, the rest
of that paragraph stands as written.

**1. The title.** `# The ledger and board formats — versions 1 and 2` becomes `# The ledger and board formats —
versions 1 to 3`.

**2. *The board*, its first two paragraphs** ("A board is a Markdown file …" and "The archive moves them …") are
replaced by:

> A board is a set of items for a person. **A v3 board is a directory** (by convention `docs/user_attention/`), one
> file per item, named by its id (*The board as a directory*, v3.0). A v2 board is one Markdown file (by convention
> `docs/user_attention.md`) with its archive beside it (`docs/user_attention_archive.md`); v3.x reads one and writes
> none. What an item means is the same in both, and the paragraphs below say it once. Where they place a field on a
> line (*right after the Context*, *ahead of the `Due:`*, *starting a sentence*), the place is a v2 line's; in an
> item file each field is a header line, in the order *The item file* gives.
>
> **An item** on a v2 board is one line: `- [ ] [kind] YYYY-MM-DD (session <name> on <host>, or n/a) — text.
> Context: … Due: YYYY-MM-DD.` A closed item is ticked: `- [x] … Closed: YYYY-MM-DD — why.` Items are never
> deleted. On a v2 board, when an open item and a closed one have the same key (below), the item is closed: a merge
> kept both sides. A v3 board has no such rule: closing an item moves its one file.

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
> board's order. **The board's order** breaks every tie: a v2 board's line order, a v3 board's id order, so its ties
> go oldest first. Which of these a consumer shows, and when it escalates, is the consumer's.

**5. *The board*, *Preamble lines*** gains, after its first sentence:

> On a v3 board they are `README.md`'s lines, every one of which is preamble (v3.0).

**6. *The board*, *The gate sweep*.** "A board is `(origin_url, basename, text, archive_text)`, named by …" becomes:

> A board is `(origin_url, basename, board)`, `board` a `Board` (*Reading a board*; v3.0, where v2.x took the board's
> and its archive's texts), named by …

In `sweep()`'s return, `to_close: {board: [item key]}` becomes `to_close: {board: [item id]}`; *The close rule*'s
"(by item key)" becomes "(by id)". After *The close rule*'s list, add:

> **What a sweep reads** (v3.0): `sweep_since(entries, today_utc, reask_days=30)` is the date from which each board's
> archive must be read (`load_board(since=)`): the earlier of `today_utc − reask_days − 1` and, for each open entry's
> `gate lifted: … ; board <repo>` Log line, its date `− 1`. Every closed item a sweep judges was decided within that
> window or a day from such a line, and an item closes no earlier than it is decided.

**7. *The board*, *The merge gate's verdicts*, its first paragraph** is replaced by:

> **The merge gate's verdicts** (v2.4) are three pure functions over a PR's **trees**, each a map from path to text
> read at the PR's base or head: the ledger at `docs/ledger/` (v2; a tree with no file under it holds a v1 ledger at
> `docs/technical_debt.md`), and this repo's board at `docs/user_attention/` (v3.0, `BOARD_DIR`), or, in a tree with
> no file under that directory, the v2 board at `docs/user_attention.md` and its archive at
> `docs/user_attention_archive.md` (`BOARD_V2_PATH`, `BOARD_V2_ARCHIVE_PATH`, until v3.0 `BOARD_PATH` and
> `BOARD_ARCHIVE_PATH`), each read through `load_board()` (`LEDGER_DIR`, `LEDGER_V1_PATH`). A tree holds the same
> board paths at the base and the head: every file directly in `BOARD_DIR`, and every file under its `archive/` that
> the PR changes. Each verdict names what it finds as `(kind, text)` pairs; `repo` is as for the sweep. The consumer
> fetches the trees, the file list, the commits and the dates from the forge, and acts on the verdict.

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
"the PR changes the item's files alone". In `uncovered_decisions()`, "(its key on no line of the base board)" becomes
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
>   line.
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
> - **The heading** is `## <text>`, the item's words (`BoardItem.text`): one line, any words, no field.
> - **The header block** is the `**Name:** value` lines after the heading's blank line, up to the next blank line,
>   read as an entry's are: a name compared by `field_key()`, so in any case, the spaces and tabs at a value's ends
>   dropped, and the first of a name winning. A value is the whole line: it holds any words, a field's name among
>   them. The fields, in the order the writers write them, each meaning what *The board* says:
>   - `Kind` — `decide`, `act`, `look`, `watch` or `fyi`; none is the kindless to-do;
>   - `Added` — the date the item was added, its id's date;
>   - `Session` — `<name>` or `<name> on <host>`, the v2 head; none for `n/a`, and none on a decided file
>     (`decided_file()`, the v2 `(person)` head);
>   - `Context` — what the item refers to, its refs read as a v2 Context's are; `none` for nothing;
>   - `Parts` — a `decide`'s snapshot, `TD-15, TD-16`;
>   - `Doer` — an `act`'s doer (v2.8), `<repo>` or `team <team>`;
>   - `Due`, `Hide until` — a date each; an unreadable `Due` is reported, never silently undated;
>   - `Answers`, `Lifts` — as on a v2 line, without the final period;
>   - `Decided` — `<date>[ by <person>] — <label>`: the date and who answered first, so the label runs to the line's
>     end and holds any words (`parse_decided()` gives `(label, date)` and `parse_decided_by()` the person, as for a
>     v2 line);
>   - `Closed` — `<date>` or `<date> — <why>`.
>
>   A field the reader does not know is kept: it is in `BoardItem.fields` (every header field as written, in its
>   order), every edit keeps its line byte for byte, and `item_file_problem()` faults it. A later v3 minor that adds
>   a field changes nothing an older v3 reader reads of the others.
> - **The body** is the detail block (*The detail block*): the lines after the header block up to the Log, leading
>   and trailing blank lines dropped (`BoardItem.detail`). No edit touches it.
> - **The Log** is the body's last section, led `**Log:**`, one line per reply, `- YYYY-MM-DD: <name>: <words>`,
>   oldest first. `<name>` holds no `:` and is at most 40 characters. A Log line in another shape is kept, and read
>   as no reply.
>
> `parse_item(text, path="")` reads one file as a `BoardItem`: its `id` from the path's name (None when it is not
> one), `path`, its fields, `added`, `session` and `host`, `context`, `closed` (`(date, why)` or None), `replies`,
> `detail` and `fields`. `item_record()` gives its record (*Reading a board*).
>
> **Reading a board** (`load_board(path, ls, read, *, since=None)`) gives a `Board`: `major` (2 or 3), `preamble`
> (`README.md`'s text, or a v2 board's text before its first item), `items` (the open items) and `closed` (every
> closed item, its archive's among them), each a `BoardItem` with its `id`.
> - **A directory** is read as `README.md`, then each `<id>.md` directly in it, in id order, then each month under
>   `archive/`, in month order, and its files in id order. An item with no `Closed:` is open, wherever it lies.
> - **A v2 file** is read with its archive beside it (`<stem>_archive.md`) as v2.7 read them (`parse_board()`, the
>   twins rule among it). A v2 item's id is its line's date, a hyphen, and `key_id()` of its key: `item_key()` of
>   `- [ ] ` and the line's text after its tick, trimmed. So it reads with the id its split file gets, and a consumer
>   that persisted a hash of that key finds it in the id. `key_id(key)` is the first 8 lower-case hex digits of the
>   SHA-256 of the key's UTF-8 bytes. A line with no readable date has id None.
> - **The stub**, a file that declares `Ledgerboard: 3` and holds no item, is read as the directory beside it, its
>   name without `.md`.
> - **The caller does the I/O**, as for `load()`: `ls(path)` returns the names directly in the directory `path`,
>   each subdirectory's name followed by `/` (v3.0; `load()` ignores those), or None when `path` is not a
>   directory; `read(path)` returns a file's text, or None.
> - **`since`**, a date, leaves the archive's months before its month unlisted and unread, so a reader that judges a
>   window (*What a sweep reads*) reads its months and not the whole archive.
> - **The readers take the `Board`**: `needs_you()`, `covers()`, `sweep()`, `board_problems()` and the merge gate's
>   verdicts; `board_people()` and `answered_by()` read its `preamble`, and a consumer calls `version_problem()` on
>   it before it trusts the rest. `item_record()` gives an item's record: `id`, `path` (the file's path in the
>   directory; `""` for a v2 item), `added`, `context` and `closed` (v3.0), with `text` the item's words (a v2
>   line's words outside its fields and its prefix) and no `line`.
>
> **Damage a hand edit or a merge can do** is named by `board_dir_problems(path, ls, read)` as `(path, problem)`:
> a file directly in the directory or in a month under `archive/` whose name is not an id and `.md` (`README.md`
> aside); a file `parse_item()` cannot read as an item (no `## ` heading, a header block holding a line that is no
> field); an `Added` that is not the id's date; an item with a `Closed:` outside `archive/`, or without one inside it;
> an archived item in a month that is not its `Closed:` date's; one id in two files; and a `README.md` that does not
> declare `Ledgerboard: 3`. `load_board()` reads an id held twice once, from its newest archived copy, else its open
> one.
>
> **Migration** is `split_board(board, archive)`, for a v2 board only: the v3 files of a v2 board and its archive,
> by their paths in the directory.
> - Every line of one key across the board and the archive, with its detail block, is one item, closed when one of
>   its lines is; it becomes `<id>.md`, or `archive/<YYYY-MM>/<id>.md` when closed, its id the v2 item's. Its fields
>   are what the v2 reader reads, each in the file's form: `Kind`, `Added` (the line's date), `Session` (none for
>   `n/a` and `(person)`), `Context` (without its final period), `Parts`, `Doer`, `Due` (an unreadable one as
>   written), `Hide until`, `Answers`, `Lifts`, `Decided` (`<date>[ by <person>] — <label>`) and `Closed`, from
>   the closed line. Its body is the detail block with its common indent removed; its replies are its Log. Its
>   heading is every word of the line the v2 reader reads as no field and no part of the prefix (the text, and any
>   words a hand edit left outside the fields), in their order, runs of whitespace collapsed to one space.
> - `README.md` is the board's text before its first item, with `Ledgerboard: 3` under its title (any
>   `Ledgerboard:` line dropped) and without the `## ` heading that opens the first item's section; each relative
>   Markdown link and reference definition there gains `../`, since the file moves one directory down. The
>   archive's text before its first item is dropped.
> - It refuses a board that declares `Ledgerboard: 3`; a line after the first item that is no item, no detail
>   block's, not blank and no `## ` heading (prose among the items: move it into the preamble first); an item with
>   no date; two open lines, or two closed lines, of one key; two items given one id; and a result that
>   `load_board()` does not read back as the same items (open and closed, compared as their records at one date) or
>   that `board_dir_problems()` flags.
> - `board_stub(title, name)` is what `board.py split` leaves at the v2 path: `# <title>`, a blank line,
>   `Ledgerboard: 3`, a blank line, and `This board is the directory [<name>/](<name>/), one file per item
>   (ledgerboard v3.0).` A v2.x reader that checks the version refuses it, and `load_board()` reads the directory
>   through it.
> - `split_board_notes(readme)` lists the lines of that `README.md` which may still describe the v2 board, as
>   `(line number, line, why)`, for the caller to warn about, nothing rewritten: a line naming
>   `user_attention.md`, `user_attention_archive.md`, `Needs the user` or `In-flight`, and a `Format:` line.

**9. *Edits*** is replaced by:

> ## Edits
>
> Every edit rewrites one open item file, by one header line set or one Log line appended, and nothing else, and is
> refused unless the reader reads back exactly what was meant (`edit_item(text, action, *, to, answer, why, reply,
> by, today, close)`, v3.0). A field it adds goes in its place in the header order. An edit of a closed item is
> refused.
> - **snooze** hides the item: it sets its `Hide until:` and leaves its `Due:` alone;
> - **due** sets the item's `Due:`, the real deadline;
> - **done** sets `Closed: <today>`, or `Closed: <today> — <why>`;
> - **decide** sets `Decided: <today> — <answer>`, or with `by` `Decided: <today> by <by> — <answer>`, replacing an
>   earlier one. It refuses a `by` that is not a person's name. With `close`, on an item whose Context names a
>   gate, it also sets `Closed: <today> — kept waiting` for a waiting-only answer or `Closed: <today> — lifted` for a
>   lifting one, and refuses any other answer (`closes()` says when to pass it);
> - **reply** appends `- <today>: <by>: <words>` to the Log, opening a `**Log:**` section after the body when there is
>   none. It refuses a `by` holding `:` or of more than 40 characters.
>
> An edit that closes the item gives a file whose place is `item_path(id, closed)`; the writer moves it in the same
> write.
>
> **A new item** (`item_file(text, due, today, session, host, context, *, kind, answers, default, detail,
> hide_until, lifts, parts)`, v3.0) is one file: `## <text>`, a blank line, the header block (`Kind` when given,
> `Added: <today>`, `Session` when there is a session, `Context`, then `Parts`, `Due`, `Hide until`, `Answers` and
> `Lifts` as given), and, after a blank line, the detail block. The text is trimmed and not empty, and no period is
> added. An empty context is `none`. `Session` is `<session>` or `<session> on <host>`. `Lifts` is written only when
> it names answers other than `Go` alone (each one of its answers, once, written as its answer spells it). A
> decide's `parts` (v2.6) are written ordered by number, separated by `, `, each as given, and are refused on any kind
> but `decide`, for an empty list, for an id that is not `TD-` and 1 to 18 ASCII digits, for an id that shares its
> number with another or with the Context's entry, unless the Context names exactly one entry, a bare `TD-n`, and
> one gate, a `decision (<person>)`, with nothing after the gate, and unless one of its answers lifts. What a kind
> takes:
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
> **A snapshot against the ledger** (`parts_problems(item, entries, archived=())`, v2.6) reads as it stands, an item
> file's text in place of an item line: "a string that is not exactly one open item" is a text `parse_item()`
> reads as no open item, and "its detail block or a board holding it as its one open item included" is dropped.
>
> **The form the writers write** (v3.0) is a file `item_file()` or `decided_file()` composed, as it stands after any
> snooze, due, decide or reply. `item_file_problem(text)` names why a file is not in that form, or gives None: a
> `## ` heading and one blank line; a header block of known fields, each once, in their order, spelled `**Name:**
> value` with one space; each value in its form (*Appendix: grammar*, *The item file*); a kind's rules (*A new
> item*; a decided file may carry any answers or none); a body of detail bullets; a Log, when there is one, last and
> holding replies alone; one blank line between the parts and one newline at the end. It never judges the detail
> block's words. `canonical_item_file(text)` rewrites a file into that form: line endings normalised to `\n`, the
> known fields in their order and spelled so, any other field after them in the file's order, one blank line
> between parts. It refuses a header block it would have to lose or repeat a line of (a line that is no field, a
> repeated field), and its result reads back the same item. No key rests on a file's spelling, so it rewrites any
> field.
>
> **The gate** is `board_problems(board, old)` (v3.0, both `Board`s): first `README.md`'s `People:` and `Answered
> by:` problems (`people_problems()`, `answered_by_problems()` of its text, as `("README.md", problem)`), then
> `item_file_problem()`'s fault of each open item whose id no item of `old` (open or closed) has, as `(path,
> problem)`, and, on a new `decide` whose Context names a gate, `decision (<person>)`, a `People:` line that does not
> list that person. An edit keeps an item's id, so an item is judged once, when it is added. It refuses a v2 board.
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
>   and detail block), items separated by one blank line; with `--hidden`, the hidden open items after them, in id
>   order, each `*<id> · hidden until <date>*`. Read-only; no file holds it;
> - **`add`** — a new item (`item_file()`, any kind, its answers and detail block, `--hide-until`) at
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
>   (`split_board()`), `--to DIR` (default the board's name without `.md`, which must not exist): every file written,
>   the v2 file replaced by `board_stub()` and its archive removed, as one write; `split_board_notes()`'s lines are
>   printed as warnings (`warnings` in `--json`). It prints no subject;

The **`rank`** bullet stands. After the actions list add:

> A write to a v2 board is refused (*split first*); `list` and `show` read one (v3.0).

In the paragraph after it, "`archive_subject()`, " is dropped; "A decide lift also reports" gains before it "Every
write that names an item reports its `id`."; "The board writer's write of several files also removes files" is
unchanged. In the notes paragraph, "each names its line, as a write names one" becomes "each names its item's id",
`[{"line", "note"}]` becomes `[{"id", "note"}]`, and "`line n: ℹ <note>`" becomes "`<id>: ℹ <note>`".

**11. *The ledger as a directory*, *The caller does the I/O*** gains, after "or None when `path` is not a
directory;":

> from v3.0 the names include each subdirectory's, followed by `/`, which `load()` and `entry_path()` ignore;

**12. *Versions*, after v2.7's last paragraph** (or after the last v2.x paragraph a build ahead of this one has
landed), add:

> **v3.0 makes the board a directory** (*The board as a directory*, *Edits*, *The board writer*, *The merge gate's
> verdicts*): one file per item, named by its id, in `docs/user_attention/` with `README.md` and
> `archive/<YYYY-MM>/`, closing an item moving its file. **It reads a v2 board**: `load_board()` gives the same
> items for a v2 file and its archive as for its split, each v2 item with the id `split_board()` gives it, so a
> consumer vendors v3.0 before it splits its board, and reads other repos' boards in either major. **It writes v3
> only**: `board.py`'s writes refuse a v2 board (*split first*). **What goes:** the item key as what an item is
> (`item_key()` remains, only to read a v2 line and as `key_id()`'s input); the open-and-closed twin rule (read on a
> v2 board alone); `archive_closed()`, `archive_subject()`, `ARCHIVE_AT`, `closed_items()` and `board.py archive`;
> the v2 line's writers, `item_line()`, `decided_line()`, `edit_line()`, `item_problem()` and `canonical_item()`, and
> with them the refusal of a field's name in a text, context, answer, detail value or reply and of an answer ending
> `(by …)`; `add --under`; and the edits' `--line` and `--expect`. **What a caller changes:** `needs_you()`,
> `covers()`, `sweep()` and `board_problems()` take a `Board`, and the sweep's board is `(origin_url, basename,
> board)`, its `to_close` ids; `item_record()` loses `line`, gains `id`, `path`, `added`, `context` and `closed`, and
> its `text` is the item's words; `parts_problems()`, `decide_lift()` and `closes()` take an item file's text;
> `BOARD_PATH` and `BOARD_ARCHIVE_PATH` are `BOARD_V2_PATH` and `BOARD_V2_ARCHIVE_PATH`, beside `BOARD_DIR`; a
> subject carries the id; an `ls` lists subdirectories, so a caller's `ls` that lists files alone reads a v3 board's
> archive as empty; and `lift_pr_verdict()` sends a lift on a v2 board to review. A v2.x module meets a v3 repo as
> the stub, which declares `Ledgerboard: 3`: a reader that calls `version_problem()` refuses it, and one that does
> not reads an empty board, so a repo splits its board only once every reader of it runs v3.0. `Ledgerboard: 3` on a
> ledger means nothing new here; the ledger's v3.0 changes are its own paragraph (TD-078).

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
> reply-line     ::= "- " date ": " reply-by ": " char*
> reply-by       ::= [^#x20#x9:#xA] [^:#xA]*
> ```
>
> What the productions leave to prose: the fields stand in the order `item-field` lists them, each at most once, with
> `added-field` and `context-field` always; `parts-field` only on a `decide`, `doer-field` only on an `act`; a
> `due-field` on every kind but `fyi`; answers as *A new item* says a kind takes them, and a `lifts-field` only on
> a `decide`, each label one of its answers once and never `Go` alone; a decided file has no `session-field` and may
> carry any answers or none. An `item-label` holds no ` — ` and does not end in ` (default)`; a `reply-by` is at most
> 40 characters and ends in no whitespace; a `date` is a day of the calendar. `doer-field` is v2.8's (*The open item
> line*'s `doer-repo`), present once that release has landed. Every other production is the one above it of the
> same name (`date`, `head-name`, `entry-id`, `answer-sep`, `label-start`, `label-char`, `person`, `nonspace`,
> `char`).

## Fixtures

All invented names (`pat`, `sam.lee`, `acme/widgets`, `host-a`, sessions `w-9`, `lb-x`).

- **`fixtures/item/cases.json` and `expected.json`** (a new runner kind, `item_cases`, beside `edit_cases`):
  - `parse`: a file of each kind and its record; a heading, a Context, an answer, a detail line and a reply each
    holding `Context:`, `Due:` and `Decided:` as words (the case S3 exists for), read as words; `**due:**` read as
    `Due`; a repeated field (the first wins); an unknown `**Owner:**` field (ignored, in `fields`); `Decided:` with and
    without `by`, and a label ending `(by Friday)` read whole; `Closed:` with and without a why; a Log line in
    another shape (no reply); a CRLF file; a file with no heading (None, and its problem in `board_dir`);
  - `compose`: `item_file()` for each kind; a text, a context, an answer, a detail value and a `said` holding
    `Context:` and `Lifts:`, each written (the refusals that go); refused: a two-line value, a host with no session,
    an empty text, a `decide` with one answer, a `look` with other answers, an `fyi` with a `due`, `lifts` naming a
    waiting-only answer, `parts` on an `act`; `decided_file()` with and without `by`, and an answer ending
    `(by x)`, written;
  - `edits`: each of the five edits on a file, the unknown field and the body kept byte for byte; `due` and `snooze`
    adding their field in its place; `decide` replacing an earlier `Decided:`; `decide` with `close`, lifting and
    waiting-only; `reply` opening the Log and appending to it; refused: any edit of a closed item, a reply `by`
    holding `:`, `decide` with `close` and a work order;
  - `problems`: `item_file_problem()` passing each writer's file, and faulting fields out of order, a field twice,
    an unknown field, `**Due:**` spelled `**due:**`, a `Parts:` on an `act`, a Log not last, a body line that is
    no bullet;
  - `canonical`: reordered and respelled fields rewritten, an unknown field placed after the known ones; refused: a
    header line that is no field, a repeated field;
  - `ids`: `item_id()` accepting `2026-11-11` and `3f9a2c1d`, refusing `2026-02-30`, `3F9A2C1D` and seven digits;
    `item_path()` open and closed (`archive/2026-11/<id>.md` for a close on 2026-11-30, `archive/2026-12/` on
    2026-12-01); `key_id()` of a key whose hash a consumer persisted (`sha256(item_key("- [ ] " +
    text))[:8]`, the case's text given);
  - `subjects`: `subject()` for each action and `append` with an id; `subject_id()` of a v3 subject, of a v2 one
    (None) and of a legacy append; `edit_action()` of both majors' subjects.
- **`fixtures/board/<case>.v3/`** for each v2 case (`basic`, `answers`, `hidden`, `people`, `lifts_parts`,
  `shared_part_left_open`): its split directory. A new runner kind, `board_v3_case`, beside `v2_case`: `split_board()`
  of the case's text gives the directory file for file, and `load_board()` of it gives the case's expected JSON. The
  v2 cases' JSONs are regenerated: `board_case` reads through `load_board()`, its records carry `id` (no `line`),
  `needs_you` rows are `[id, class, days]`, `keys` become the items' ids and `closed` the closed records.
- **`fixtures/board_dir/<case>/`** (a new kind, `board_dir_case`: `board/` and `expected.json`, holding
  `load_board()`'s items, closed items, people and `needs_you`, and `board_dir_problems()`): `months` (closed items
  across three months, read whole and with a `since` that reads two); `ties` (undated, unreadable-due and `fyi`
  items ordered by id); `field_words` (headings and contexts holding field names); `unknown_field`; `stub` (the v2
  path holding the stub, read as the directory); `damage` (a name that is no id, an `Added` not the id's date, a
  closed item outside `archive/`, an open one inside it, a wrong month, one id twice, a README without
  `Ledgerboard: 3`); `newer` (a README declaring `Ledgerboard: 4`: `version_problem()` names it).
- **`fixtures/board_split/<case>/`** (a new kind, `board_split_case`: `board.md`, optional `archive.md`,
  `expected.json` holding the files or the refusal, and `split_board_notes()`): `twins` (an open and a closed line
  of one key, on the board and across board and archive, each one closed item); `sections` (the `## Needs the user`
  and `## In-flight` headings dropped, the README's prose kept, its relative links given `../`, its notes listed);
  `hand_line` (words a hand edit left outside the fields carried into the heading); `decided_by` (a `Decided:` with
  and without `(by …)` rewritten); `persisted_key` (the id's digits equal to a given consumer hash); refused:
  `undated`, `duplicate_open`, `two_closed`, `prose_between_items`, `already_v3`.
- **`fixtures/board_writer/`**: new cases over a v3 directory: `add_v3`, `add_id_given`, `add_id_taken` (exit 1),
  `add_id_wrong_date` (exit 1), `add_said`, `add_decided`, `snooze_id`, `due_id`, `done_moves` (the file under
  `archive/<month>/`), `decide_close_moves`, `decide_work_order` (stays open), `reply_id`, `edit_no_such_id` (exit
  1), `edit_closed` (exit 1), `write_v2_refused` (exit 1, *split first*), `list_v2`, `list_stub`, `show`,
  `show_hidden`, `show_v2`, `fmt_v3`, `split`, `split_exists` (exit 1). Each existing case is rewritten over a
  directory (`--id` for `--line`/`--expect`), or removed where its rule went (`archive`, `archive_new_file`,
  `archive_none`, `add_empty_section`, `add_fyi_no_heading`, `add_refused_field`); `add_detail_recommended_doubled`
  is rewritten, its refusal standing. The runner's `writer_case` needs no change: `tree()` reads nested files.
- **`fixtures/verdict/`**: the shared base tree holds a v3 board; new cases `v3_lift_open` (a work order, stays
  open), `v3_lift_closes` (moved to `archive/`), `v3_lift_two_items` (review), `v3_lift_wrong_month` (review),
  `v3_other_repo`, `v3_tripwire_lifted`, `v3_uncovered_new_decide`, `v2_lift` (`lift-board-v2`), and `split_pr`
  (a v2 pair at the base, the directory at the head: no tripwire flag). The existing cases move their board into
  the directory with the same items.
- **`fixtures/sweep/`**: `cases.json`'s boards may name a `dir` (a v3 board) in place of `board` and `archive`;
  the runner reads either through `load_board()` (a change to `sweep_cases`), and its rerun step closes by id and
  files with `item_file()`; one v3 board and one v2 board in the set; `to_close` lists ids; a `sweep_since` group
  (the window alone, and a `; board <repo>` line older than it).
- **`fixtures/lift/`**: `decide_lift()`'s items become item files.
- **`fixtures/grammar/cases.json` and `expected.json`**: a start `item-file`, judged by `item_file_problem()`,
  with a group for each production it reaches anew (`item-file`, `item-text`, `item-field`, each field production,
  `item-answer`, `item-label`, `item-body`, `body-line`, `item-log`, `reply-line`, `reply-by`), each with an
  accepting and a refusing fixture: among them a context holding `Due:` (accepted), `**Decided:** 2026-11-12 by pat
  — Go (by Friday)` (accepted), a field out of order and a reply-by holding `:` (refused).
- **Retired**: `fixtures/archive/` (with `archive_closed()`), and `fixtures/edit/`'s groups over the v2 writers
  (`compose`, `edits`, `item_problems`, `canonical_items`); its `subjects` move to `item/`.
- **The runner** (`fixtures/run.py`): `fs_ls` lists subdirectories with `/`; the kinds `item_cases`,
  `board_v3_case`, `board_dir_case` and `board_split_case` join `cases()`; `board_case`, `sweep_cases` and
  `lift_cases` read through `load_board()`; `archive_case` and the v2 groups of `edit_cases` go.

**Unit tests** (`tests/`): a property test that `split_board()` then `load_board()` gives every fixture board's items
back; `tests/test_item_gate.py`'s compose and edit properties over item files; `tests/test_grammar.py` reading the
new start.

## The builds

Each is filed `Part of: TD-070` on Paul's Go after the rounds, and lands its SPEC text, code and fixtures together.
No release is cut between B1 and B5 (Open for round 1).

**B1, the item file.** D3, D4, D7's module half. Location: `ledgerboard/__init__.py` (`ITEM_ID_RE`, `item_id()`,
`key_id()`, `item_path()`, `parse_item()`, `BoardItem`'s new fields, `item_record()`, `item_file()`,
`decided_file()`, `edit_item()`, `item_file_problem()`, `canonical_item_file()`, `subject()` with the id,
`subject_id()`), `SPEC.md` (text 8's *The item id* and *The item file*, 9, 13), `fixtures/item/`,
`fixtures/grammar/`, `fixtures/run.py` (`item_cases`). Done when: the precheck is green and every fixture above
passes.

**B2, reading.** D5, D6, D9. Location: `ledgerboard/__init__.py` (`Board`, `load_board()`, the stub's reading,
`board_dir_problems()`, `needs_you()`, `covers()`, `sweep()`, `sweep_since()`, `board_problems()` over a `Board`;
`parse_board()` giving v2 items their ids; `parts_problems()`, `decide_lift()`, `closes()` over a file), `SPEC.md`
(text 2–6, 8's *Reading a board* and *Damage*, 11), `fixtures/board/` (regenerated records), `fixtures/board_dir/`,
`fixtures/sweep/`, `fixtures/lift/`, `fixtures/run.py` (`fs_ls`, `board_dir_case`, `board_case`, `sweep_cases`,
`lift_cases`). Done when: the precheck is green and those fixtures pass.

**B3, the writer.** D2's moves, D7's writer half, D8. Location: `ledgerboard/board.py` (`plan_add` by id, no
`under`; `plan_edit` by id, with the move; `show`; `plan_fmt` over files; the v2 refusal; `--id`, `--hidden`; the
`archive` action, `--line`, `--expect` and `--under` gone; the usage docstring), `SPEC.md` (text 10),
`fixtures/board_writer/`. Done when: the precheck is green and every writer case passes.

**B4, the merge gate's verdicts.** D10. Location: `ledgerboard/__init__.py` (`BOARD_DIR`, `BOARD_V2_PATH`,
`BOARD_V2_ARCHIVE_PATH`, `_tree_ls()` listing subdirectories, `_tree_board()`, `tripwire()`,
`lift_pr_verdict()`, `uncovered_decisions()`), `SPEC.md` (text 7), `fixtures/verdict/`. Done when: the precheck is
green and every verdict case passes.

**B5, migration and the release's removals.** D11, D12. Location: `ledgerboard/__init__.py` (`split_board()`,
`board_stub()`, `split_board_notes()`; `FORMAT_MAJOR = 3`; `item_line()`, `decided_line()`, `edit_line()`,
`item_problem()`, `canonical_item()`, `archive_closed()`, `archive_subject()`, `ARCHIVE_AT`, `closed_items()`
removed), `ledgerboard/board.py` (`split`), `SPEC.md` (text 1, 8's *Migration*, 12), `fixtures/board_split/`,
`fixtures/board/<case>.v3/`, `fixtures/run.py` (`board_split_case`, `board_v3_case`; `archive_case` and the v2
`edit_cases` groups removed), `fixtures/archive/` and `fixtures/edit/` retired, `tests/`. Done when: the precheck is
green, every fixture passes, and `board.py split` of this repo's own board, run on a scratch copy, reads back.

Order: B1, then B2, then B3 and B4 (either order), then B5. Then v3.0's release with TD-078's half (Paul's), this
repo's own split, and each consumer's entry (agent-cadence's first).

## Open for round 1

- **The rest of *The board*'s wording.** Text 2 says the field paragraphs' places are a v2 line's. A round should
  read *Kind*, *`Due:`*, *`Hide until:`*, *`Context:`*, *`Parts:`*, *Trailing fields*, *The bold head*,
  *Replies*, *The detail block* and *A closed item* for any sentence that still reads as the only form (the bold
  head, for one, has no v3 meaning: the heading is the text), and say whether each needs a v3 clause or moves under a
  *Reading a v2 board* heading.
- **`item_file_problem()`'s messages and tags**, which the fixtures pin; this draft fixes the rules, not the words.
- **The stub** (D11): whether a file kept at the v2 path through v3.x earns its place against a silent empty read.
- **Releases during the builds**: whether a v2.x fix (TD-065's v2.8 among them, if it is not out first) is cut from
  a branch at the last v2 tag once B1 merges, and what `release.sh` needs for that.
- **ShiftLead's persisted keys of closed items**: this draft maps `board:<8 hex>` for any item, open or closed; a
  round should confirm ShiftLead persists no key of another shape (a full key text, a line number).

## Not in this design

The ledger's own v3.0 removals (`Waits`, `Taken by`, the old decision form, a header `Resolved`, `migrate`) and the
archived entry's writer route are TD-078's. When v3.0 is cut, and what else it carries, is Paul's.

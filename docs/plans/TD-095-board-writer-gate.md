# TD-095: the board's writer and the merge gate's verdicts (TD-070's B3 and B4)

**Status:** Draft 3, 2026-11-14 (session lb-designer): round 1's fact-check (R44) raised four build-changing findings (F258–F261) and nine minor (F262–F270), all applied. Its re-check (R45) raised six minor (F271–F276), applied; a second re-check and round 1's design review follow. Draft 2: draft 1's moved text rebased on TD-092's plan as designed (draft 10, Go'd): every name, signature, decision and text number of B1 and B2 now TD-092's, where TD-070's text differed from TD-092's design, TD-092's is followed and each change is marked *rebased on TD-092* (`read_ledger()`'s `ls`, the B3 refusal's words, the B3 sentences that name `split`), and one need in B1 stated as a build of its own before v3.0 (D7's `done --why`). Draft 1 was TD-070's unreviewed B3 and B4 text, moved unchanged. Class: **wide** — it changes a vendored, published format read and written by both consumers, and is part of a major (cadence.md §4.8; cap 6 rounds). Rounds: none yet at draft 2.

**Entry:** [TD-095](../ledger/TD-095.md), `Part of` [TD-070](../ledger/TD-070.md). **Source:** TD-095's Fix (the
scope, Paul's Split, decided 2026-11-13: B3 and B4 here, B5 TD-098's); [TD-070's plan](TD-070-board-directory.md),
draft 11, from which every section here is moved unchanged (its scope S1–S10, Paul's Go of 2026-11-11, kept as each
decision's source); [TD-092's plan](TD-092-board-item-reader.md), draft 10, Go'd (B1 and B2, the item file, its id
and the v2/v3 reader, which this plan builds on and does not change); `SPEC.md` *The board writer*, *The merge
gate's verdicts*. A citation here of what this plan does not hold (D3's module half, D4–D6, D9, texts 2–6, 8, 9, 11,
13–15, B1, B2) is to TD-092's plan; of D11, D12, texts 1 and 12, B5 and *Consumers*' other lines, to TD-070's plan
(TD-098's). The findings the moved text cites (F1–F174) are in docs/reviews/TD-070.md, and F175–F257 in
docs/reviews/TD-092.md.

## The problem

The problem is TD-070's plan's (*The problem*): every new item written at one place in one file, the item's identity
its text, fields inside prose, and the twins as the merge rule. B3 and B4 are the half of v3.0 that writes the
directory and judges a PR's changes to it.

## What is already settled

The scope (S1–S10, Paul's Go, 2026-11-11), the precedent, the entry grammar and what an item means are TD-070's
plan's and TD-092's plan's (*What is already settled*). This plan's decisions take S1 (D1), S4 (D2's moves), S2
(D3's writer half), S6 (D7's), S7 (D10) and S8 (D8). B1 and B2 (TD-092's plan) are designed and Go'd.

## Options weighed

The options are TD-070's plan's (S1, the directory) and TD-092's plan's (the id, the item's form, `Decided:` in a
field, sections, listing the archive's months, the stub); none is about B3 or B4 alone.

## Decisions

Numbered as in TD-070's plan, so that citations across the three plans and their review records resolve. D3's
module half, D4, D5, D6 and D9 are TD-092's plan's; D11 and D12 stay in TD-070's plan (TD-098's). A bare D4, D6 or
D9 below is TD-092's plan's, a bare D11 TD-070's (rebased on TD-092). As in TD-092's plan (D6, round 2's F203), "a v3
board" of a read means `form` `"dir"` and "a v2 board" `form` `"file"`, whatever its `major`; so a file declaring 3
that holds items (TD-092's rule 5) is a v2 board to every write here, refused as one.

**D1. The board is a directory in v3.0 (S1).** A v3 board is a directory of item files; a v3 writer writes nothing
else. v3.x still reads a v2 board (D6).

**D2. The layout (S4): the moves on close and `README.md`'s stamps.** The layout as the reader sees it is
TD-092's plan's, D2.

Closing an item
moves its file in the same write (`done`, and a `decide` that closes); nothing else moves one, and no file is
deleted. `archive_closed()`, `archive_subject()`, `ARCHIVE_AT`, `closed_items()` and `board.py archive` go.
*Rebased on TD-092:* `board.py archive` goes at B3 (*The builds*); the module's four go at B5 (TD-070's plan, B5,
TD-098's: `closed_items()` kept private as `_closed_lines()`), since TD-092's B1 and B2 keep the v2 writers to B5.
The path a close writes is TD-092's `item_path(id, closed)` (D2), `closed` the `Closed:` date as a `YYYY-MM-DD`
string; `SPEC.md`'s sentence for the move is TD-092's text 8 (*An open item*), which B3 completes (text 8 below).

**README's stamps stay in it** (`Swept:`, `Swept-deep:`, the consumer's dated preamble lines): which stamps a
consumer writes is the consumer's, and a stamp is preamble. Every sweep that stamps rewrites `README.md`, so two
stamps still conflict there. That is a known limit of v3.0, not removed by it: a stamp is one line a sweep writes,
not an item, and moving stamps out (a file per stamp, say) is the consumer's choice, open to it later.
*Rebased on TD-092:* `SPEC.md` says so in TD-092's text 5 (*Preamble lines*), which B2 lands; B3 adds nothing for it.

**D3. The item id (S2): its writer half** (restated from TD-092's plan, D3, which keeps the text; round 1's F183
there). `board.py add` draws the nonce (`secrets.token_hex(4)`) and draws again
while the name is held open or in any archive month: it draws at most 8 times in all; the 8th held name is refused
(round 1's F262: this plan's reading of TD-092's D3 "up to 8 times", pinned by B3's unit test "eight held names refused"). `add --id <id>` takes a caller's id instead (a
service writer that keys its appends on an event, cadence §4.4), refused when malformed, when its date is not the
item's `Added`, or when held. So `--id` is idempotent within a day and not across days, as intended: an id names one
day's add, a retry of a written add is refused as held (which a caller reads as done), and a caller that retries on
a later day passes `--today` the id's date or draws a new id. Two changes that add one id conflict as two files at
one path, which is the safe failure; 32 bits within one day make it rare. An id never changes: a retitle, an edit
and a close keep it.

**D7. The edits and the writers (S6): `board.py`'s half.** Its module half is TD-092's plan's, D7.

**`board.py`** names an item by `--id` in all five edits; `--line` and `--expect` go (an id cannot move). `add`
writes `<board>/<id>.md`; `done`, and a `decide` that closes, write the archived file and remove the open one as one
write. A write to a v2 board is refused (*split first* from B5; *rebased on TD-092*: its text tags, round 6's
F77, have B3's refusal say only that `board.py` writes a v3 directory, and B5 add the *split first* hint with the
`split` action); `list` and `show` read one. `--board` is the directory (or
the stub, or a v2 file for the reads), its path normalised first (`os.path.normpath()`), so `docs/user_attention/`
and `docs/user_attention` name one board and `ledger/` beside it is `docs/ledger/` either way (round 8's F126: today's
`os.path.dirname()` of a trailing-slash path is the directory itself). **Every action resolves a stub as
`load_board()` does** (round 3's F47): given the stub's path, `add` and the five edits write into the directory
beside it, never `user_attention.md/<id>.md`. Its file-system `ls` for the board lists subdirectories with `/` (the
`ls` `board.py` passes `load_board()`, B3's by TD-092's plan, D6). *Rebased on TD-092:* TD-070's text had one
function serve the board's read and `read_ledger()`, replacing `read_ledger()`'s files-only `ls`; TD-092's D6 keeps
`read_ledger()`'s `ls` file-only and unaffected (it lists a ledger's files for `load()` alone, and `load_board()`
never receives it), so B3 leaves it as it is.
Each of `board.py`'s helpers that reads the board or an item (round 8's F127, each checked in the pinned file):
- `items(board, today)` reads `load_board()` and gives `item_record()` of each open item, in the board's order;
- `_gate(path, old, new)` takes the two `Board`s, the board before the write and the board after it, both read
  whole (no `since`: TD-092's D7 reads `old` whole, or an archived id would read as new), and calls
  `board_problems(new, old)` (TD-092's `board_problems(board, old)`, which raises `Refused` for a `"file"` board; a
  write to one is refused before it), each fault named `<path>: <problem>` where it named `line <n>: <problem>`, `<path>`
  relative to the board's directory (`2026-11-11-3f9a2c1d.md`, `README.md` for the preamble's), the message
  `<board>: <path>: <problem>[; <path>: <problem>…]` as today's `<board>: line <n>: …` (round 9's F152);
- **What a write prints** (round 9's F152, reopening F127), every shape `board.py` gives on a v3 board: a write's
  JSON loses `line` and carries `id`, the item's id, in its place (`add`'s `{"id", "item_notes"}`, an edit's
  `{"id", …}` before the decide lift's keys), its `paths` the files written and removed, as today; `fmt`'s JSON is
  `{"fixed": [<id>…], "refused": [{"id", "why"}]}` and its stderr line for a file it keeps `<id>: kept: <why>`
  where it printed `line <n>: kept: <why>`; `list`'s plain line is `<id>\t<due tag or ->\t<text>` where it printed
  the line number (`-` for a v2 item with no id); a note's stderr line is `<id>: ℹ <note>` (text 10).
  `people_problems()` and `answered_by_problems()` of a `Board` give `(path, problem)` pairs (TD-092's plan, D6;
  round 2's F196 there): the path `README.md` on a v3 board and `Board.path`'s basename on a v2 one, a missing
  `People:` or `Answered by:` line named under that path with today's message; `board_problems()` names each as
  `("README.md", problem)` on a v3 board;
- `who_answered(board, by)`, `_may_answer(board, gate, by)` and `_decide_ledger()`'s `board_people()` and
  `answered_by()` take the `Board`, never `README.md`'s text: given a string, `board_people()` reads it as a v2
  board's and stops at its first `- [ ]` or `- [x]` line (`ANY_ITEM_RE`), which on a README is prose (D6, its
  `isinstance(x, Board)` rule, round 2's F198);
- `_decide_ledger()` takes the `Board` and the item's file text, its gate from `_item_gate(item)`, its parts from
  `BoardItem.parts`, its lifts from `BoardItem.lifts` (F134) and its offered labels from `BoardItem.answers` (TD-092's plan, D7's reader list), and calls `decide_lift()`
  and `closes()` with the file;
- `_check_parts(board_path, new, ledger)` takes the new item file, its gate and parts from `parse_item(new)`, the
  ledger default `ledger/` beside the board when it is a directory (the normalised path, above);
- `_line_notes(board, line, today)` becomes `_id_notes(board, id, today)`: the notes of the open item with that id
  as the write leaves the board, each `{"id", "note"}` (text 10), `[]` when the item closed;
- `_find()` and `_under()` go, with `--line`, `--expect` and `--under`;
- **`add --said --by`**: the answer is the item's first reply, a Log line `- <today>: <by>: <said>` (`edit_item()`'s
  reply form), never words after the heading; `<said>` is refused when it holds a character `str.splitlines()` splits on, checked before any collapse;
  the rest of its whitespace, and `<by>`'s, is collapsed as today (round 1's F259), and the add is refused when
  either is empty, or when `<by>` holds a `:` or is over 40 characters (the Log's rule, `reply`'s refusal). The heading is `--text` alone, so the subject's head
  never holds the person's words (today's `bare` line). *Rebased on TD-092:* `item_file()` takes no `said` (TD-092's
  text 9 gives its arguments, `item_line()`'s and `doer`), so `board.py` writes the reply with B1's `edit_item(…,
  "reply", reply=<said>, by=<by>, today=<today>)` over `item_file()`'s text, one file, one write, refused as that
  edit refuses;
- **`done --why`** (`edit_item(…, "done")`): the why has its whitespace collapsed and its trailing `.`, `?` and `!` stripped, as
  `edit_line()` does today, and is written `Closed: <today> — <why>`, with no final period (D4's form); an empty
  why writes `Closed: <today>`. *Rebased on TD-092:* the collapse and the strip are `edit_item()`'s, B1's (TD-092's
  D7: `edit_line()`'s five edits over an item file; `edit_line()` does both today), and `board.py` passes `--why`
  as given. **A stated need:** TD-092's text 9 (*done*) and its `fixtures/item/` `edits` cases do not pin them; if B1
  lands `edit_item(…, "done")` without them, a build of its own before v3.0 adds them to B1 (code, a text 9
  clause and an `edits` case), since `done_moves` and `tests/test_board_writer.py` rely on them.

**D8. What a person reads (S8).** `board.py show [--hidden]` writes `show_board(board, today, hidden=False)` to
stdout as it is, adding nothing; `show_board()` is the module's (pure, over a `Board`; B3). Its bytes (round 5's
F70), which `show`, `show_hidden` and `show_v2` pin:
- **The items**: each item `needs_you(board, today)` gives, in its order; with `hidden=True` (`--hidden`), then each hidden open
  item, in the board's order (D6).
- **Each item** is a header line, then its text. The header line is `*<id> · <class>*` for an item `needs_you()`
  gives (`<class>` its class: `decided`, `overdue`, `due`, `bad_due`, `undated`, `watch` or `fyi`), `*<id> · hidden until <date>*` for a hidden one (`<date>` its
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

**D10. The merge gate's verdicts (S7).** The trees are maps from path to text as before. `BOARD_DIR` is
`docs/user_attention`; `BOARD_V2_PATH` and `BOARD_V2_ARCHIVE_PATH` (renamed from `BOARD_PATH` and
`BOARD_ARCHIVE_PATH`) are the v2 pair. A tree holds a v3 board when it holds a file under `BOARD_DIR/`, else the v2
pair; it is read through `load_board()` over the tree, whole (no `since`, TD-092's D6), its `ls` `_tree_ls()`,
which lists subdirectories from B4 (TD-092's D6). The consumer reads the same paths at the base and the head:
every file directly in `BOARD_DIR` and every archive path the PR's file list names (a moved file's old and new
paths both; an archived item the PR leaves alone changes no verdict). **The verdicts judge what changed from the two
trees** (paths added, removed, or changed in text), never from how a forge reports a move, so a forge that reports
a moved file as a rename, or as a removal and an addition, gives one verdict; the file list decides only which
archive files the consumer fetches.
- `lift_pr_verdict()`'s **(b)** becomes: the PR's board changes are one item's, its open file changed in place or
  removed with its archived file added, and the head file is `edit_item(base file, "decide", …, close=closes(…))`
  byte for byte at `item_path(id, closed)` (`closed` the head's `Closed:` date as a `YYYY-MM-DD` string, None when
  it stays open: TD-092's D2 and D4); board changes that are not one item's take review (`lift-board-diff`), and a
  head file at a path other than `item_path(id, closed)`, or not those bytes, `lift-board-line`. A lift on a v2
  board, a v2 base (a split PR included), takes ordinary review (`lift-board-v2`): no v3 writer writes one. **(c)** and another repo's case name "the item's files" where they named "the board".
- **The changed set from the trees** (round 9's F153): today `lift_pr_verdict()` judges `files`, the forge's list
  (`list(files) != [BOARD_PATH]` for another repo's entry, `set(files) != want` for (c), and its Log-date loop over
  `files`). From B4 each reads `changed(base_tree, head_tree)`, the paths whose text differs between the two trees
  (added, removed or changed): another repo's case needs its board paths to be exactly the item's files and its
  ledger paths none; (c) needs the changed set to be exactly the item's files and each entry file `decide_lift()`
  writes; the Log-date loop runs over the changed ledger paths. The trees hold only the board's and the ledger's
  paths, so `files` chooses the archive paths fetched, and a path in `files` outside
  `BOARD_DIR/` and `LEDGER_DIR/` sends the PR to review (`lift-files`), as a stray path does today, and so does a
  path under `BOARD_DIR/` that is neither directly in it nor under `archive/<YYYY-MM>/` (round 1's F258); its board
  paths are checked only for their shape, never compared between the trees, so a move reported as a rename or as
  two paths gives one verdict.
- **The order of the checks** (round 1's F260): the board's presence and form first, then the files, then the
  diff, each before (a0) as today's `lift-no-board` and `lift-board-diff` are: no board at the base or the head,
  neither a file under `BOARD_DIR/` nor `BOARD_V2_PATH`, takes review (`lift-no-board`, its message naming
  `BOARD_DIR` and `BOARD_V2_PATH`); then a v2 base (`lift-board-v2`); then a stray path in `files` (`lift-files`,
  above); then board changes that are not one item's (`lift-board-diff`); then the checks from
  `lift-not-answered` to the ledger and changed-set checks in today's order ((a0) and (a) before the `Decided:` by
  and date), the changed-set `lift-files` of (c) and another repo's case among them, and the head file's
  path and bytes (`lift-board-line`) last, where today's byte compare is.
- `tripwire()` reads covering items through `load_board()`; "newly closed `— lifted.`" is a `Closed:` whose why is
  `lifted` at the head and none at the base (*rebased on TD-092*: `BoardItem.closed[1] == "lifted"`, the why read
  without its final period for both majors, TD-092's D4 and D11, so a v2 line's `— lifted.` and a file's `—
  lifted` read alike). `uncovered_decisions()`'s new `decide` is one whose id no base item (open, or closed in an archive file the tree holds) has (an undated v2 item, id None by TD-092's
  F206, is matched by `item_key()` of its line, its indent kept, with the base's undated items, as TD-092's D6
  matches undated lines, never counted new for its None);
  its `decision-no-lift` message names the item by id (round 9's F156): `the new decide item <id> asks <gate> and
  none of its answers lifts it (<lifts>)`, where it said "on line {it.line}".
- A split PR (a v2 pair at the base, the directory at the head) reads the same ids on both sides (D6; TD-070's plan, D11), so the
  tripwire sees no item change; it takes ordinary review (`lift-board-v2`).
- Each consumer's carve-outs that judge a commit by "the board alone" read "only files under the board's
  directory": a line in each consumer's entry (*Consumers*), never code here.

## Consumers

The consumers' v3.0 entries, filed through each repo's question seat once v3.0 is cut, and their other lines are
TD-070's plan's, *Consumers* (TD-098's). These are the lines for those entries that B3 and B4 make, never code here.

- **agent-cadence**:
  - `board_edit.py`, which imports `edit_line()` from the vendored module and calls it directly (pinned tree
    `67023cc`), moves to `edit_item()` by `--id` (or to `board.py`'s edits): its `--line`, `--expect` and their
    exit-3 refusal go; `replay` (TD-248, in a tree later than the pin) retires, there being no single file to replay
    into;
  - `check_cadence.py`: `BOARD` becomes the directory; `classify_direct()`'s stamp is `README.md`'s stamp lines
    alone (a stamp commit still rewrites `README.md`, D2), its board-append is item files added directly under the
    directory, each with a `Due:` (its `## Needs` test becomes the kind test it stood for, its choice), its
    board-edit is one item file changed in place or moved into `archive/` under an edit subject;
    `row_board_edit_pr()` the same;
- **ShiftLead**:
  - `sessionorc/board.py`: `add()` and `add_decided()` drop `under=NEEDS`, its edits pass `--id` (`plan_edit()`'s
    line and expect go), `item_line()`/`decided_line()` become `item_file()`/`decided_file()`;

## The SPEC text the build lands

The section's opening, and *No sentence lands before the code* (which tags each text's sentences by build), are
TD-092's plan's. The texts below are B3's and B4's; texts 1, 12, 14's two bullets, 8's *Migration* and 10's
`split` are TD-070's plan's (B5, TD-098's).

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
>   gate, never answered, that gains `Decided: D by <p> — <label>` (else review, `lift-board-diff`, when the changes
>   are not one item's); the head file is `edit_item(base file, "decide", label, by, D, close=closes(item, label,
>   entries after))` byte for byte at `item_path(id, closed)` (else `lift-board-line`), so a work
>   order is never closed and a finished lift never left open; D lies from `created_at − 1` to the merge date (else
>   `created_at`) `+ 1`, the board's local day running up to a day from UTC. A lift on a v2 board, a v2 base (a
>   split PR included), takes review (`lift-board-v2`, v3.0): no v3 writer writes one;

After the list, add:

> **The order** (v3.0): `review` names the first condition that fails, the board's presence and form first, then
> the files, then the diff, each before (a0): a base or head with no board, neither a file under `BOARD_DIR/` nor
> `BOARD_V2_PATH`, takes review (`lift-no-board`, naming `BOARD_DIR` and `BOARD_V2_PATH`); then a v2 base
> (`lift-board-v2`); then a path in the file list outside `BOARD_DIR/` and `LEDGER_DIR/`, or under `BOARD_DIR/`
> but neither directly in it nor under `archive/<YYYY-MM>/` (`lift-files`); then board changes that are not one
> item's (`lift-board-diff`); then the checks from `lift-not-answered` to the ledger and changed-set checks in today's order ((a0) and
> (a) before the `Decided:` by and date), and last the head file's path and
> bytes (`lift-board-line`).

In **(c)**, "the PR changes exactly the board and the open file of each entry it changes" becomes "the PR changes
exactly the item's files and the open file of each entry it changes", and "the PR changes the board alone" becomes
"the PR changes the item's files alone", and "`decide_lift()` of the base line" becomes "`decide_lift()` of the
base item's file" (round 4's F60; a lift on a v2 board has taken review at (b)). In
`uncovered_decisions()`, "(its key on no line of the base board)" becomes
"(its id on no base item: open, or closed in an archive file the tree holds)".

**8. and 9., the writer's and the verdicts' sentences.** Their texts are TD-092's plan's, texts 8 and 9, which land
at B1 and B2 without these; B3 and B4 add them (TD-092's round 1's F175, F192; *The builds* below): text 8's
"Closing an item moves its file in the same write" (*An open item*), "; a person reads the board through `board.py
show`" (*No sections and no stored view*) and *The item id*'s sentence "The writer draws the nonce at random and
draws again for a name the directory or its archive holds; the module draws nothing." (each as TD-092's text 8
words it, *rebased on TD-092*), and text 9's "; the writer moves it in the same write" (B3);
text 8's *The readers take the `Board`* bullet's ", as `board.py`'s `who_answered(board, by)` does through
`board_people()`" (B3) and "and the merge gate's verdicts" (B4).

**10. *The board writer*.** Its first paragraph's library list becomes `plan_add`, `plan_edit`, `plan_fmt`,
`plan_split`, `plan_rank`, each returning a `Plan`, `show`, and `apply(plan)` (`plan_split` B5's, the rest B3's:
round 9's F155). Its actions list is replaced by (the `add` bullet keeping v2.8's `--doer` and its refusal with
`--decided`, `board.py`'s `DOER_DECIDED`, F155):

> - **`list`** — every open item's record (`item_record()`), read-only; the board a directory, the stub, or a v2 file;
> - **`show`** (v3.0) — the board for a person (`show_board(board, today, hidden=False)`): for each item
>   `needs_you()` gives, in its order, the line `*<id> · <class>*`, then the item's file as stored (a v2 item's line
>   and detail block), items separated by one blank line; with `--hidden`, the hidden open items after them, in the
>   board's order (*Reading a board*), each `*<id> · hidden until <date>*` (`no id` for a v2 line with no readable date). Read-only; no file holds it;
> - **`add`** — a new item (`item_file()`, any kind, its answers and detail block, `--hide-until`, `--doer`) at
>   `<board>/<id>.md`, the id drawn at random (redrawn while the directory or its archive holds it: at most 8 draws in all, the 8th held
>   name refused),
>   or `--id`'s, refused when it is no id, its date is not the item's `Added`, or it is held. With `--parts TD-a,TD-b`
>   (v2.6), a decide's snapshot (`item_file(parts=)`): the option may be repeated, each value is split on `,` and each
>   piece trimmed, and an empty piece is refused; `--parts` with `--decided` is refused, and so is `--ledger` without
>   `--parts`. With `--doer <value>` (v2.8), an act's doer (`item_file(doer=)`); `--doer` with `--decided` is
>   refused. The item's own refusals come first. Then the ledger is read (`--ledger <v2 directory>`, default
>   `ledger/` beside the board when it is a directory, its open and archived entries), and the write is refused, with every problem, when
>   `parts_problems()` names any, or when no ledger is found. With `--said` and `--by`, a question already answered:
>   its answer is the item's first reply, the Log line `- <today>: <by>: <said>`, refused as `reply` refuses (a
>   `--by` holding `:` or of more than 40 characters, empty or blank words); `--said` is refused when it holds a
>   character `str.splitlines()` splits on, checked before any collapse, and the rest of its whitespace, and `--by`'s, is collapsed as today. With `--decided`, an item the person decided elsewhere (`decided_file()`).
>   The write is refused when `board_problems()` faults the item it adds;
> - **`snooze`, `due`, `done`, `decide`, `reply`** — the five edits (`edit_item()`) of the open item `--id` names,
>   refused when no open item has it; `done`, and a `decide` that closes the item, write its archived file and
>   remove its open one as one write; `reply` takes its `--by` from the caller;

The **who answered** bullet stands. In **the decide lift** bullet, "default `ledger/` beside the board when it is a
directory" stands (round 8's F126: `board.py` takes `ledger/` beside the board only when it is a directory, `beside
if os.path.isdir(beside) else None`, the board's path normalised first, D7), and "the board line `edit_line(…,
"decide", label, by, today, close=closes(item, label, entries after))`" becomes "the item file `edit_item(…, "decide", label, by, today,
close=closes(item, label, entries after))`, moved when it closes". The **`archive`** bullet goes. The **`fmt`**
bullet becomes:

> - **`fmt`** — `canonical_item_file()` of every open item file: the files it rewrites, and each file it cannot, with
>   why, reported and kept;
> - **`split`** (v3.0) — TD-070's plan's, text 10 (B5, TD-098's);

The **`rank`** bullet stands. After the actions list add:

> A write to a v2 board is refused (*split first*); `list` and `show` read one (v3.0). Every action resolves a stub
> as `load_board()` does: given the stub's path as `--board`, `add` and the five edits write into the directory
> beside it (v3.0). `--board` is read as a normalised path, so a trailing `/` names the same board, and `ledger/`
> beside it is the same directory (v3.0).

(B3 lands this paragraph without "(*split first*)", which B5 adds: TD-092's plan, *The SPEC text the build lands*,
round 6's F77.)

In the paragraph after it, "`archive_subject()`, " is dropped; "A decide lift also reports" gains before it "Every
write that names an item reports its `id`."; and "A write of several files is both or neither:" becomes:

> A write of several files, and of the files it removes, is both or neither (v3.0: `done` and a closing `decide`
> remove the item's open file as they write its archived one, and `split` removes the v2 archive):

(*Rebased on TD-092:* by its rule that no sentence lands before the code that makes it true, round 4's F59, B3
lands this without ", and `split` removes the v2 archive", which B5 adds with the `split` action.)

In the notes paragraph, "each names its line, as a write names one" becomes "each names its item's id",
`[{"line", "note"}]` becomes `[{"id", "note"}]`, and "`line n: ℹ <note>`" becomes "`<id>: ℹ <note>`". Wherever the
section names a write's output by line (round 9's F152, D7's *What a write prints*), it names the id: a write's
JSON carries `id` where it carried `line`; `fmt` reports `fixed` as ids and `refused` as `{"id", "why"}`, printing
`<id>: kept: <why>` for a file it keeps; `list`'s plain line is `<id>`, a tab, the due tag (`-` for none), a tab and
the item's words; and a refused write's gate faults read `<board>: <path>: <problem>`, `<path>` relative to the
board's directory.

**The search** — its opening is TD-092's plan's, and B5's search TD-070's plan's; B3's and B4's:

- **B3** (text 10 but `split` and "(*split first*)"): *The board writer* for `item_line`, `decided_line`, `edit_line`, `canonical_item` (as a whole name: `canonical_item_file` stays, as TD-092's B1 search reads it),
  `archive_closed`, `archive_subject`, `--line`, `--expect` and `--under`.
- **B4** (text 7): *The merge gate's verdicts* for `BOARD_PATH`, `BOARD_ARCHIVE_PATH` and `edit_line`; `BOARD_PATH`
  and `BOARD_ARCHIVE_PATH` are found only in text 7's *until v3.0* clause.

## Fixtures

All invented names (`pat`, `sam.lee`, `acme/widgets`, `ops`, `host-a`, sessions `w-9`, `lb-x`).

- **`fixtures/board_writer/`**: new cases over a v3 directory: `add_v3`, `add_id_given`, `add_id_taken` (exit 1),
  `add_id_wrong_date` (exit 1), `add_said`, `add_said_lines` (exit 1), `add_via_stub`
  (`--board` the stub's path: the file written in the directory beside it), `snooze_id`, `due_id`, `done_moves` (the
  file under `archive/<month>/`), `decide_close_moves`, `reply_id`,
  `edit_no_such_id` (exit 1), `edit_closed` (exit 1; it replaces the existing `edit_not_open`, whose `--line` named a
  closed item), `write_v2_refused` (exit 1; its message gains *split first*
  at B5), `list_v2`,
  `list_stub`, `show` (a CRLF item file among its items), `show_hidden`, `show_v2` (a detail block indented four
spaces, printed at four), `show_empty` (no item to show: no output),
`fmt_v3` (B3: it needs only B1's `canonical_item_file()`; beside the existing `fmt`, which is rewritten); and, in
  B5, `split` and `split_exists` (exit 1). **Every case that runs `add`** (round 8's F121) passes `--id` and
  `--today` (the id's date; `board.py` takes `--today` already), so its written path and its JSON are fixed: the new
  `add_v3`, `add_id_given`, `add_id_taken`, `add_id_wrong_date`, `add_said`, `add_said_lines` and `add_via_stub`, and every rewritten
  `add_*` case (`add_act`, `add_answered`, `add_crlf`, `add_decide`, `add_decide_lifts`, `add_decided`,
  `add_detail_recommended_doubled`, `add_doer`, `add_doer_decide`, `add_doer_decided`, `add_doer_repo`,
  `add_gate_off_people`, `add_hidden`, `add_ledger_without_parts` and each `add_parts*` case). The random draw,
  `secrets.token_hex(4)` and its redraws, is pinned in `tests/` with the draw patched, never by a fixture. Each
  existing case is rewritten over a directory (`--id` for
  `--line`/`--expect`), or removed where its rule went (`archive`, `archive_new_file`, `archive_none`,
  `add_empty_section`, `add_fyi_no_heading`, `add_refused_field`); `add_detail_recommended_doubled` is rewritten,
  its refusal standing; `decide_work_order` (stays open) is rewritten, not new; v2.8's `add_decided` and Doer cases (`add_doer`, `add_doer_repo`, `add_doer_decide`,
  `add_doer_decided`, their refusals standing) are rewritten over a directory, and `fmt_doer` becomes `fmt_v3`'s
  Doer case (round 8's F115). `edit_moved` is removed with `--expect` (its rule went: an id cannot move), and
  `edit_newer_major` is rewritten over a directory whose `README.md` declares `Ledgerboard: 9`, refused with
  `board/README.md: this board declares Ledgerboard: 9, newer than this ledgerboard.py reads (3) — …` (D6; round 9's
  F161). Every rewritten case's expected JSON carries `id` where it carried `line`, and `fmt`'s its ids (D7's *What a
  write prints*, F152). The `rank_*` cases are unchanged (round 1's F269). The runner's `writer_case` needs no change: `tree()` reads nested files.
- **`fixtures/verdict/`**: the shared base tree holds a v3 board; new cases `v3_lift_open` (a work order, stays
  open), `v3_lift_closes` (moved to `archive/`; the case's file list names the two paths, no rename, and the verdict
  comes from the trees), `v3_lift_two_items` (review, `lift-board-diff`), `v3_lift_wrong_month` (review, `lift-board-line`),
  `v3_lift_stray_board_path` (review, `lift-files`: a path under `BOARD_DIR/` neither directly in it nor under
  `archive/<YYYY-MM>/`), `v3_other_repo`,
  `v3_tripwire_lifted`, `v3_uncovered_new_decide`, `v2_lift` (`lift-board-v2`), and `split_pr` (a v2 pair at the
  base, the directory at the head: no tripwire flag; review, `lift-board-v2`). The existing cases move their board into the directory with
  the same items, except that `a CRLF board whose answered line drops its CR`'s expected verdict becomes
  `lift-board-line`; the other `lift-board-diff` messages are those of text 7's (b).

**Unit tests** — the opening is TD-092's plan's, B5's bullet TD-070's plan's; B3's and B4's:
- **B3**: `tests/test_board_writer.py` is rewritten over a directory: each run's `--line`/`--expect` becomes `--id`,
  its `item_notes` assertions read `{"id", "note"}` where they read `{"line": 5, …}`, the `plan_archive()` tests
  (both-or-neither, the archive written before the board, a board that is its own archive) become the move's
  (the archived file written before the open one is removed, nothing left on a failed write), its usage-error
  tests name `--id`, and `board.py add`'s draw is tested there with `secrets.token_hex` patched (a first draw
  taken, a held name redrawn, eight held names refused; round 8's F121).
- **B4**: `tests/test_ledgerboard.py`'s verdict tests (`tripwire()`, `lift_pr_verdict()`, `uncovered_decisions()`)
  build their trees with `BOARD_V2_PATH` where they used `BOARD_PATH`, and gain the changed-set case (F153: a move
  reported as one path or two gives one verdict).

## The builds

**The builds' opening** (each filed `Part of: TD-070`, no release between B1 and B5, the shims, what a record
shows, each build's search) is TD-092's plan's, *The builds*; the order and the release, TD-070's plan's (B5,
TD-098's).

**The reader seam, function by function** — its opening is TD-092's plan's, *The reader table*; the rows whose
build is B3 or B4:

| function | reads today | a v3 item's source | build |
|---|---|---|---|
| `_tree_board()`, `_board_line_reads()`, `_lifted_close()`, `tripwire()`, `uncovered_decisions()`, `lift_pr_verdict()` | the board text's lines, `item_key()`, `.line`, `_item_gate(it.text)` | `load_board()` over the tree, ids, `closed`'s why, `_item_gate(item)` | B4 |
| `board.py` `items()`, `_gate()`, `who_answered()`, `_may_answer()`, `_check_parts()`, `_decide_ledger()`, `_line_notes()` | `parse_board()`, `ITEM_RE` over a line, `_item_gate()` over its text, a board's text | the `Board`, the item file, `BoardItem` fields (D7's F127 list) | B3 |
| `show_board()` (new) | — | the `Board`: `needs_you()`'s rows, each item's `raw`, a v2 item's `detail_source` (D8) | B3 |
| `board.py` `plan_add()`, `plan_edit()`, `plan_fmt()` | `ITEM_RE` over the line, `parse_answers()` for the fill, `canonical_item()` | `item_file()`, `edit_item()` by id, `BoardItem.answers`, `canonical_item_file()` | B3 |
| `board.py` `_find()`, `_under()`, `plan_archive()` | a line number, a section, `closed_items()` | none | gone B3 |

TD-092's table's shared rows whose later part is this plan's (*rebased on TD-092*): TD-092's `BoardItem` row and
its B2 *Location* (`detail_source`, which `parse_board()` keeps, B3), D8's; the `ls` `board.py` passes
`load_board()` (B3) and `_tree_ls()` (B4), each TD-092's D6.

**B3, the writer.** D2's moves, D3's writer half (TD-092's plan, D3: `add`'s nonce drawn at most 8 times in all, the 8th held name refused, `--id`
and its refusals, `--today`; TD-092's round 1's F183), D7's writer half, D8. Location: `ledgerboard/__init__.py` (`show_board()`, pure
over a `Board`, its bytes as D8 gives them; `BoardItem.detail_source`, which `parse_board()` keeps and a v3 item
holds as `[]`, D8; round 4's F54, round 5's F70; moved here from TD-092's B1 and B2 by TD-092's round 1's F194), `ledgerboard/board.py` (`plan_add` by id, no
`under`, `--doer`; `plan_edit` by id, with the move; `show`; `plan_fmt` over files; the v2 refusal; `--id`,
`--hidden`; the `archive` action, `--line`, `--expect` and `--under` gone; a board read through `load_board()` and
checked with `version_problem(board)`, `read()` keeping `version_problem(text)` for the ledger and the rank file;
`who_answered(board, by)` over a `Board`; one file-system `ls` listing subdirectories with `/`, used by the board's
read, `read_ledger()`'s staying file-only (TD-092's D6, *rebased on TD-092*); `--board` normalised; `items()`, `_gate()`, `_may_answer()`, `_decide_ledger()`,
`_check_parts()`, `_id_notes()` (was `_line_notes()`), `add --said`'s Log line and `done --why` as D7's F127 list
gives them, `_find()` and `_under()` gone; every output shape D7's *What a write prints* gives, `id` for `line`,
F152; the usage docstring), `SPEC.md` (text 10 but `split`, `plan_split`, "(*split first*)", F155, and ", and `split` removes the v2 archive", *rebased on TD-092*; and the
writer's sentences TD-092's B1 and B2 leave out, TD-092's round 1's F175: text 8's "Closing an item moves its file
in the same write", "; a person reads the board through `board.py show`" and *The item id*'s "The writer draws the
nonce …" sentence, and text 9's "; the writer moves it in the same write"; and text 8's *The readers take the
`Board`* bullet's ", as `board.py`'s `who_answered(board, by)` does through `board_people()`", TD-092's round 1's
F192), `fixtures/board_writer/` (but
`split`, `split_exists`; `edit_moved` removed, `edit_newer_major` rewritten, F161), `tests/test_board_writer.py`
rewritten (F149). **Records:** `item_record()` is untouched; the `list` cases (`list`, `list_v2`,
`list_stub`) print B2's records. Done when: the precheck is green, every writer case passes, and *The search*'s B3
search finds its names only where it allows.

**B4, the merge gate's verdicts.** D10. Location: `ledgerboard/__init__.py` (`BOARD_DIR`, `BOARD_V2_PATH`,
`BOARD_V2_ARCHIVE_PATH`, `_tree_ls()` listing subdirectories, `_tree_board()`, the board changes read from the two
trees, `tripwire()`, `lift_pr_verdict()`, `uncovered_decisions()`, each reading `_item_gate(item)` of a
`BoardItem` where it read `_item_gate(it.text)`, TD-092's D4 (*`words` and `text`*); `lift_pr_verdict()` judging the changed set from the trees and
`files` only for a path outside the board and the ledger, F153; `decision-no-lift` naming the item's id, F156),
`SPEC.md` (text 7, and text 8's *The readers take the `Board`* bullet's "and the merge gate's verdicts", which
TD-092's B2 leaves out, TD-092's round 1's F192), `fixtures/verdict/`, `tests/test_ledgerboard.py`'s verdict tests (F149).
**Records:** none change. Done when: the precheck is green, every verdict case passes, and *The search*'s B4 search
finds its names only where it allows.

## Not in this design

B1 and B2 (TD-092's plan); B5, the migration, the release and v3.0's removals (TD-098, from TD-070's plan's D11,
D12 and B5). The ledger's own v3.0 removals (`Waits`, `Taken by`, the old decision form, a header `Resolved`, `migrate`) and the archived entry's writer route are TD-078's. When v3.0 is cut, and what else it carries, is Paul's.

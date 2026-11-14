# TD-098: the board's migration, the release and v3.0's removals (TD-070's B5)

**Status:** Draft 2, 2026-11-14 (session lb-designer). Draft 1 was TD-070's plan's B5 text (D11, D12, *Consumers*, the `SPEC.md` texts, fixtures, tests and builds that are B5's), moved unchanged; draft 2 rebases it on TD-092's plan (B1 and B2, merged as TD-093 and TD-094) and TD-095's (B3 and B4, filed as TD-103 and TD-104), each change marked *rebased*, and decides what those plans leave to B5 (the head note, `board.py split`, `fixtures/sweep/alpha/`, the *Versions* text). Class: **wide** — it changes a vendored, published format read and written by both consumers, and is part of a major (cadence.md §4.8; cap 6 rounds). Rounds: 0 of 6.

**Entry:** [TD-098](../ledger/TD-098.md), `Part of` [TD-070](../ledger/TD-070.md). **Source:** TD-098's Fix (Paul's Split
on TD-095's scope, decided 2026-11-13: B3 and B4 TD-095's, B5 here); [TD-070's plan](TD-070-board-directory.md),
draft 11, from which every section here is moved unchanged (its scope S1–S10, Paul's Go of 2026-11-11, kept as each
decision's source); [TD-092's plan](TD-092-board-item-reader.md), draft 10, Go'd (B1 and B2); [TD-095's
plan](TD-095-board-writer-gate.md), Go'd 2026-11-13 (B3 and B4). The findings the moved text cites (F1–F174) are in
docs/reviews/TD-070.md, F175–F257 in docs/reviews/TD-092.md and F258–F350 in docs/reviews/TD-095.md.

## The problem

The problem is TD-070's (its plan's *The problem*, the scope Paul answered Go on 2026-11-11): every new item written at one place in one file, the item's identity
its text, fields inside prose, and the twins as the merge rule. B5 is the half of v3.0 that moves a v2 board into
the directory and removes what the directory replaces, and the release that carries it.

## What is already settled

The scope (S1–S10, Paul's Go, 2026-11-11), the precedent, the entry grammar and what an item means are TD-070's
plan's and TD-092's plan's (*What is already settled*). This plan's decisions take S9 (D11) and the release (D12).
B1 and B2 (TD-092's plan) are merged (TD-093, TD-094); B3 and B4 (TD-095's plan) are Go'd and filed (TD-103, TD-104). v2.8, the last v2.x minor, is tagged.

## Options weighed

The options are TD-070's plan's (S1, the directory) and TD-092's plan's (the id, the item's form, `Decided:` in a
field, sections, listing the archive's months, the stub). Three are this part's own (draft 2):

- **Where the head note's v2 text comes from** (D11, *rebased*): `split_board()` returning the notes beside the
  files would change its result's shape for one note; `split_board_notes()` taking the v2 texts it was split from
  keeps `split_board()` a plain `{path: text}` and lets the notes read what the files no longer hold. The second.
- **`fixtures/sweep/alpha/`**: a hand-written v3 stand-in for `alpha.md`'s split since B2 (TD-094). Keeping it beside
  a split it may differ from leaves two answers to one question, and regenerating it from the split would check the
  split against itself (round 1's F383); once `split_board()` exists the runner splits `alpha.md` in memory and
  `alpha/` is deleted, the split's bytes being pinned by `fixtures/board/<case>.v3/` and `board_split`.
- **Where a board splits in the release's order** (round 1's F376, F377): in each consumer's vendor PR (draft 1),
  or once every reader of that board runs v3.0. A v2.x reader that checks no version reads a stub as an empty
  board, and both consumers read other repos' boards (ShiftLead's `gatesweep` and `workorders`, agent-cadence's
  `nudge_user_attention.py`), so a split in agent-cadence's vendor PR would empty its board for ShiftLead's sweep
  until ShiftLead synced. The second (D12).
- **`board.py split` under TD-095's write gate**: a gate exemption for `split` alone, or `split` as a separate
  tool. One `board.py` keeps one `--board` normalisation, one usage and one JSON shape; `split` is the one action
  whose gate is the reverse (it needs a v2 board), so it has its own gate (D11, *`board.py split`*).

## Decisions

Numbered as in TD-070's plan, so that citations across the plans and their review records resolve. D1–D10 are
TD-092's plan's and TD-095's plan's: a bare D4, D5, D6 or D9 below is TD-092's, a bare D1, D2, D8 or D10 TD-095's,
and D3 and D7 are split (the module half TD-092's, the writer half TD-095's). *Rebased:* marks draft 2's changes to
the moved text.

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
- **a twin's closed line and its detail block supply every field and the body**; the open twin is read for nothing,
  as v2 reads it; where its detail block differs from the closed twin's, `split_board_notes()` names it at the
  item's heading, `open twin's detail not carried`, so a person sees what the read never showed (round 1's F378);
- **the archive's own prose** (round 1's F378): its text before its first item (its title and any note) is not
  carried, since `README.md` is the board's, and `split_board_notes()` lists each of its non-blank lines but the `#
  ` title, `archive preamble not carried`; a line after its first item that is no item, no detail block's line and
  not blank is carried as the board's are (below), after the board's own carried lines, under the archive's `## `
  headings that stand above one;
- its fields are the v2 reader's, rewritten into the file's forms: `Context` and `Closed`'s why lose their final
  period (`Closed: 2026-11-12 — lifted.` becomes `**Closed:** 2026-11-12 — lifted`), `Decided` becomes `<date>[ by
  <person>] — <label>`; its body is the detail block, common indent removed; its replies are the Log. A v2 item's `closed` (B2) — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, D11 (2026-11-13 split);
- **its heading is `item_words(line)`** — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, D11 (2026-11-13 split);
- `README.md` is the board's text before its first item, `Ledgerboard: 3` under its title (on its own line right
  before the first non-blank line after the `# ` title, so a title, a blank line, `Ledgerboard: 3`, then the
  board's next line; with no `# ` title, as the first line followed by one blank line; round 1's F359), less the `## ` heading
  nearest the first item (with more than one `## ` heading before it, only that one drops), each relative link
  gaining `../`: an inline link or image's target (`[t](target)`, `![t](target)`) or a reference definition's
  (`[label]: target`) whose target starts with none of a scheme (`[A-Za-z][A-Za-z0-9+.-]*:`, `mailto:` among
  them), `#` and `/` (a `#` later in it, `cadence.md#3-x`, is no bar), outside code spans and fenced code; an
  angle-bracketed target (`<a b>`) gains it inside the brackets, a title after the target (`(x "t")`) is kept, and
  a target starting `./` has that `./` replaced by `../` (round 1's F381);
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
  makes of the files (over `_dict_ls()`; the notes call the module's private `_item_dir_problems()`, whose `(rule,
  line, problem)` keeps the rule and the line that `board_dir_problems()`' `(path, problem)` drops, and keep rule 14's
  alone; round 1's F366, F372), at the line of the field it names (the first header line whose name `field_key()`
  reads as that field, as `_field_line()` gives it; round 9's F173), in its order. **A head holding more than session and host** (TD-092's round 5's F238): a v2 line whose head group holds
  text after its session and host (`(session s-1 on host-a, branch x)`'s `, branch x`) loses that text at the
  split, since no v2 reader reads it into a field (TD-092's plan, D11's prefix), so the notes list it as a carried
  shape's note, at the item's `Session` line (or, with no `Session`, its heading), naming the text lost, so a person
  sees the loss. The written files no longer hold that text, so the note is made from the v2 line (its `raw`), which
  the notes' input must reach. *Rebased (draft 2, deciding what TD-092 left open):* `split_board_notes(files, board,
  archive="")` takes the v2 texts the files were split from, beside the files, and for each item line of either
  whose head group holds text after its session and host gives `(path, line number, line, why)` at the item's
  `Session` line (with no `Session`, its heading), `why` `head text not carried: <text>`, `<text>` the head group's
  inner text less its `session <name>` and the `on <host>` match `HEAD_HOST_RE` reads (wherever in the group each
  stands), whitespace collapsed and leading and trailing `,`, `;` and spaces dropped; an empty `<text>` gives no
  note (round 1's F355). `split_board()` and the notes share one private `_split_items(board, archive)`, which gives
  each item with the v2 line that supplies its file, so the notes never re-derive the split's choices; `files` must
  be `split_board()`'s result for those texts (round 1's F382). Only the line that supplies the item's file is noted: of twins, the closed one, the open
  twin being read for nothing. Text 8's *Migration* bullet on the notes says so, and `board_split`'s `head_extra`
  case pins it (an open line `(session s-1 on host-a, branch x)` and a closed one `(session s-2 on host-b, pr 7)`;
  only a `(session …)` group can hold such text, since `ITEM_PREFIX_RE` takes `(n/a)` and `(person)` whole);
  `fixtures/board/basic.v3/`'s split is the other (`basic.md:8`'s `,
  branch feature/x`, TD-092's F238). `board.py split` prints them as warnings (`warnings` in `--json`).
- *Rebased:* **what the split reads first.** `split_board()` refuses a board whose declared major is above 2
  (`board_major(text, file=True)`, the board's reader, 2 for none, not `format_major()`, which is the ledger's and
  gives 1: `Ledgerboard: 3`, the stub's, and any newer major, `not a v2 board: declares Ledgerboard: <n>`; round
  1's F360); a v2 file declaring 1, 2 or none (or 0, which `VERSION_RE` reads) is split (round 1's F369), its `Ledgerboard:` line dropped from `README.md` as
  above. Its read-back calls `load_board("", _dict_ls(files), files.get)` and `board_dir_problems("", …)` over the
  same map, paths relative to the directory (`""` its root, as `_dict_ls()` takes it).
- *Rebased:* **a board older than v2.3** (no `People:` line, keys before `fmt`'s rule) is split as it reads: the
  split adds no `People:` line and refuses none for lacking one. What such a repo does first is TD-100's (Paul's
  Hold on TD-096); this plan neither refuses nor repairs it.
- *Rebased:* **a split PR's verdict.** The PR that splits a board changes the v2 file into the stub and
  adds the directory: `lift_pr_verdict()` sends it to review as `lift-board-v2` (B4, TD-095's D10 and its `split_pr`
  case), never `lift-files`; the split's ids are the v2 ids, so the head reads the same items as the base.

**The key a consumer persisted** (ShiftLead's `key()`, `key_id()`, an indented line and a `[x]` line) — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, D11 (2026-11-13 split).

`board_stub(title, name)` is the stub `board.py split` leaves at the v2 path; `title` is the v2 file's first `# `
line's text, else the file's name without `.md` (round 1's F358). Every file the split writes ends its lines in LF,
whatever the v2 file used (F359). The read-back compares the two reads' records at one date, the latest day any
item of the input names (an `Added` or a `Closed` date), so hidden, overdue and the notes are judged alike (F367). `split` takes no target (round 6's
F75): it always writes the directory beside the board, named the board's name less `.md`, since that is the one
directory the stub reads as (D6); any other place would leave a stub reading as a missing directory. `split_board_notes(files)` names
README lines that may describe the v2 board and the carried shapes rule 14 names (above). `board_dir_problems(path, ls, read)`, `v2_problems()`'s twin — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, D11 (2026-11-13 split).
`key_id(key)` and `item_key()` are kept through v3.x. *Rebased (round 1's F376, F377):* a repo's board splits only
once every reader of it runs v3.0 (text 12), so never in a vendor PR: in a PR of its own, after D12's vendoring
steps, landed when no open PR edits the board (each such PR is redone over the directory).

**`board.py split`** (*rebased on TD-095*: its D7's gate, options and output, which B5 extends). `split` takes
`--board` (a v2 file, normalised as every `--board` is), `--archive` (default the board's name with
`_archive.md`, beside it; that default absent, an empty archive; an `--archive` given and absent is refused,
`<archive>: no such file`, round 1's F379), `--json` and `--plan`; `--archive`, which B3 removed with the
`archive` action, comes back in `TAKES` for `split` alone (`NEEDS_OPT["split"]` is `("board",)`, `--archive`
being optional; round 1's F353), `parser()` gains the `--archive` argument again (F380), and the usage docstring
says so. Its
gate is the reverse of a write's, checked in this order, each exit 1 and before anything is written (round 1's
F380): `<board>: no such board` (`form` None); `version_problem(board)`, as after every read (a major newer than 3,
F360); `<board>: already a v3 board` (`form` `"dir"`: the stub or the directory, `--board docs/user_attention`
among them; F371); `<board>: not a v2 board file (.md)` for a `--board` not ending `.md`, whose stub would read as a
missing directory (F365); `<archive>: no such file` (F379); then
`split_board()`'s own refusals as `<board>: <why>` (`not a v2 board: declares Ledgerboard: <n>` among them); then
`<board>: <dir>/ exists` (the directory beside it, `split_exists`). `plan_split(board_path, archive_path, read,
exists)` returns a `Plan` that writes every file, replaces the v2 file with `board_stub()` and removes the archive,
as one write (*The board writer*'s both-or-neither). Its output is `main()`'s, as every write's (round 1's F364):
each note is a `Plan.warn` line, `<path>:<line>: ⚠ <why>`, on stderr in every mode; plain output is the paths
written and removed, one per line; `--json` is `{"action": "split", "subject": null, "paths": [every path written
or removed], …info}` (when `--archive` names another file than the default and a file of the default's name is
beside the board, a warning names it, left in place: a `Plan.warn` line `<path>: ⚠ default archive left in place` (that literal `why`, F390)
and a `warnings` record with `line` null and `text` `""`, pinned by `split_archive_other`; F379, round 2's F388), `info` holding `files` (the directory's paths written), `removed` (the archive's, when there
was one) and `warnings` (`[{"path", "line", "text", "why"}]`); `--plan` prints `Plan.as_json()`. It has no subject
(a commit of a split is the caller's). The write gate's v2 refusal gains the hint: `<board>:
not a v3 board: a v2 board (split first: board.py split)` (TD-095's F288; `write_v2_refused`'s expected output).

**D12. The release: v3.0, and v2.8 before it.** v3.0 is a major (*Versions* text 12). It reads v2 boards and writes
v3 only. It goes out with TD-078's ledger half as one v3.0; when, and what else it carries, is Paul's. The order:
- **B1's precondition** (the last v2.x minor, v2.8, released before B1 merges and none after it; TD-065 in v2.8, its `doer_value()` reused; TD-078's open question and B1's blocks) — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, D12 (2026-11-13 split).
- **The builds**, B1 to B5, merge in order with no release between them, B3 and B4 in either order (filed B3, TD-103,
  then B4, TD-104); TD-091 (TD-078's B4) follows B5 (round 9's F142); then v3.0. *Rebased:* v2.8 is tagged, and
  B1 and B2 are merged.
- **After v3.0, in this order** (round 1's F376, F377): agent-cadence vendors v3.0 (no split); ShiftLead syncs it
  through its pin; each repo that pins agent-cadence bumps its pin to one vendoring v3.0, this repo among them;
  then, and only then, each repo splits its own board, in a PR of its own: agent-cadence's, this repo's and
  ShiftLead's once their own tooling reads v3.0, a roster repo's as TD-100 designs. A board's readers are its own
  repo's tooling (the pinned cadence scripts: the board row, `nudge_user_attention.py`, the session-start hook and
  the attention procedure, `board_edit.py`) and every consumer that reads it from elsewhere (ShiftLead's `gatesweep`
  and `workorders`, agent-cadence's `nudge_user_attention.py` over the roster), so each consumer entry carries the
  line *split this repo's board only once both consumers run v3.0*.

## Consumers

Both change in their v3.0 vendor PR, each through an entry filed in that repo through its question seat once v3.0
is cut, agent-cadence's first. Each line below is a line for that entry, never code here. *Rebased (draft 2):* this
section is the index of those entries: each carries the lines below, TD-095's plan's *Consumers* lines (B3's and
B4's: `board_edit.py`, `check_cadence.py`'s `BOARD`, `classify_direct()` and `row_board_edit_pr()`, the fetch rule
at base and head, `uncovered_decisions()`'s `Board` triples, `BOARD_V2_PATH` and `BOARD_V2_ARCHIVE_PATH` with no
alias, ShiftLead's `sessionorc/board.py`) and TD-092's (B1's and B2's: `board_dir_problems()` beside
`v2_problems()`, `load_board()`'s `ls`), and one more from TD-095's D10: each consumer's carve-outs that judge a
commit by "the board alone" read "only files under the board's directory". Before the split, on a v2 file, the
board row's `board_dir_problems()` gives `Board.problems` alone (TD-092's D11), so it is a partial check until the
board is split.

- **agent-cadence**:
  - vendor v3.0 (no split in that PR); split its own `docs/user_attention.md` with `board.py split` in a PR of its
    own once both consumers run v3.0 and every pin is bumped (D12), landed when no open PR edits the board;
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
  - split its own board in its own PR once both consumers run v3.0 and every pin is bumped (D12; round 2's F387);
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

**2.–6.** *The board*'s first three paragraphs, *The item key*, *What needs the person*, *Preamble lines* and *The gate sweep* — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, texts 2–6 (2026-11-13 split). *Rebased:* B2 landed text 2
without its B5 words (TD-092's round 5's F71), which B5 adds now that it removes the v2 line writers: the first
paragraph's "A v2 board is one Markdown file (…) with its archive beside it (…)" gains "; v3.x reads one and writes
none", and after that paragraph B5 adds TD-092's text 2's second paragraph as that plan gives it:

> **From v3.0, everything this section says about a line** (its text, where a field stands on it, its key, its
> replies' tails, its tick, and the functions that write or judge a line: `item_line()`, `decided_line()`,
> `edit_line()`, `item_problem()`, `canonical_item()`, `parse_closed_items()`) **is v2's, read only**: v3.x reads a
> v2 line so, and writes none. A paragraph that says it once for both majors names the item file's form beside the
> line's.

(`parse_closed_items()` stays in the module, a v2 reader; the list names what judges a line, read only, not what
v3.0 removes.)

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
>   reference definition (`[label]: target`), when it starts with none of a scheme (`[A-Za-z][A-Za-z0-9+.-]*:`,
>   `mailto:` among them), `#` and `/`, outside code spans and fenced code; inside `<…>` when the target is
>   bracketed, a title after it kept, and a leading `./` becoming `../`. The archive's text before its first item
>   is not carried, and `split_board_notes()` lists each of its non-blank lines but its `# ` title.
>   Of twins whose detail blocks differ, the open twin's is not carried, and `split_board_notes()` names it.
> - A line after the first item that is no item, no detail block's line and not blank (a `- (none)` placeholder, a
>   note), on the board and then on the archive, is carried, in order, to the end of `README.md` after one blank line, with each `## ` heading after the
>   first item that stands above a carried line; a heading with no carried line under it is dropped. Nothing is
>   lost, and `split_board_notes()` lists what may describe the v2 board.
> - It refuses a board that declares a major above 2 (`Ledgerboard: 3`, a stub's, among them); an item with no date, or a date that is no day of the
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
> - `split_board_notes(files, board, archive="")`, over `split_board()`'s files and the v2 texts they were split
>   from, lists as `(path, line number, line, why)`, for the caller to warn about, nothing rewritten: the lines of
>   that `README.md` which may still describe the v2 board (a line naming `user_attention.md`,
>   `user_attention_archive.md`, `Needs the user` or `In-flight`, and a `Format:` line), then each shape the split
>   carried that `board_dir_problems()` names, at its field's line (the first header line of that field's name),
>   then each item whose v2 line's head group held more than its session and host, at its `Session` line (with
>   none, its heading), `why` `head text not carried: <text>`: the group's text less the session and the host,
>   which no file holds.

**9. *Edits*** — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, text 9 (2026-11-13 split). *Rebased:* its
swap is B5's (TD-092's round 7's F92): B5 removes v2's `## Edits` section whole and renames `## Edits (v3.0)`, which
B1 landed after it, to `## Edits`, its text unchanged; every link or mention of *Edits (v3.0)* in `SPEC.md` becomes
*Edits*.

**8, *Reading a board*.** *Rebased:* B2 landed its `item_record()` sentence without "and no `line`" (TD-092's plan,
*The SPEC text the build lands*); B5 adds it, so the record is given "with `text` the item's words and no `line`".
Three more sentences B2 landed describe the text forms B5 removes, and go (round 1's F356): in *Reading a board*,
"Each of these that also takes a v2 board's text tells a `Board` from the text by its type (`isinstance(x,
Board)`)." and "`board_problems()` of a v2 board's text gives what it gave before, and raises `Refused` for a
`board` read from a file (*The gate*)." become "`board_problems()` raises `Refused` for a `board` read from a file
(*The gate*)."; and *The gate sweep*'s "(v3.0, for boards given as `Board`s; one given as texts, until v3.0 removes
that form, lists item keys as before)" becomes "(v3.0)".

**10. *The board writer*** — its B3 text moved to TD-095's plan, docs/plans/TD-095-board-writer-gate.md, text 10 (2026-11-14 split); its B5
parts stay here: `plan_split` in the first paragraph's library list (after `plan_fmt`, B5's: round 9's F155), the
"(*split first*)" of the paragraph added after the actions list, the `split` bullet, after the `fmt` bullet, and the clause ", and `split` removes the v2 archive" in the paragraph after the actions list:

> - **`split`** (v3.0) — a v2 board (`--board`, its archive `--archive`, default beside it) split into its directory
>   (`split_board()`) always written into the directory beside it named the board's name without `.md` (which must
>   not exist), the directory the stub then reads as: every file written,
>   the v2 file replaced by `board_stub()` and its archive removed, as one write; `split_board_notes()`'s lines are
>   printed as warnings (`warnings` in `--json`). It prints no subject;

*Rebased on TD-095* (its text 10 as B3 lands it): the bullet above becomes, with D11's *`board.py split`*:

> - **`split`** (v3.0) — a v2 board (`--board`, its archive `--archive`, default the board's name with
>   `_archive.md` beside it, none if absent) split by `split_board()` into the directory beside it named the board's
>   name without `.md`, which must not exist, the directory the stub then reads as: every file written, the v2 file
>   replaced by `board_stub()` and its archive removed, as one write. It refuses, exit 1 and writing nothing, a
>   board that does not exist, one of a major newer than 3, one already v3 (`already a v3 board`), a `--board` not
>   ending `.md`, an `--archive` given that does not exist, what `split_board()` refuses, and an existing directory
>   (`<dir>/ exists`). `split_board_notes()`'s lines are printed as warnings, `<path>:<line>: ⚠ <why>`, and, when
>   `--archive` names another file and one of the default archive's name is beside the board, `<path>: ⚠ default
>   archive left in place` (`warnings` in `--json`, each `{"path", "line", "text", "why"}`, the last with `line`
>   null and `text` `""`, beside `files` and `removed`; round 2's F389). It prints no subject;

and B3's sentences take B5's words: the paragraph after the actions list's "a v2 board is refused" reads "a v2 board
is refused (*split first*)"; the write gate's message is `not a v3 board: a v2 board (split first: board.py split)`;
and "A write of several files, and of the files it removes, is both or neither (…)" gains ", and `split` removes
the v2 archive" before its period.

**11. *The ledger as a directory*, *The caller does the I/O*** — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, text 11 (2026-11-13 split).

**12. *Versions*, after the last v2.x paragraph** (the last minor's, v2.8's, released before B1 merges, D12; on
`main` today "v2.8 gives `migrate` the last old forms", TD-089's, after TD-088's "v2.8 gives an archived entry a
note": round 9's F159), add. **It builds on TD-092's text 15** (TD-092's round 5's F241): B2 lands that
*Versions* paragraph first, naming what a v2 board reads differently from B2 on and that a board declaring 3 is
readable, so this paragraph follows it, and at B5 its "It reads a v2 board differently" sentence is reconciled with
that paragraph rather than repeating it. *Rebased (draft 2):* text 15 is on `main` (B2, `SPEC.md`'s *v3.0 reads a
board as a `Board`*), so the paragraph below lands after it, and points to it for the six read differences, the
twin rule among them, and for `BOARD_MAJOR` and `version_problem(board)`; text 15's "and the sweep, given a
`Board`, never closes it" loses ", given a `Board`," at B5, the text form being gone (TD-092's round 6's F247):

> **v3.0 makes the board a directory** (*The board as a directory*, *Edits*, *The board writer*, *The merge gate's
> verdicts*): one file per item, named by its id, in `docs/user_attention/` with `README.md` and
> `archive/<YYYY-MM>/`, closing an item moving its file. **It reads a v2 board**: `load_board()` gives the same
> items for a v2 file and its archive as for its split, for any board the split accepts, each v2 item with the id `split_board()` gives it, so a
> consumer vendors v3.0 before it splits its board, and reads other repos' boards in either major. It reads a v2
> board as the paragraph above says, and a board file that declares no major reads as 2, the format a board's v1
> and v2 share (*Versions*' "none means 1" stays the ledger's). **It
> writes v3 only**: `board.py`'s writes refuse a v2 board (*split first*). **What goes:** the item key as what an
> item is (`item_key()` remains, only to read a v2 line and as `key_id()`'s input); the open-and-closed twin as the
> merge rule (a v3 item is one file; a v2 board's twins are still read as one item, above); `archive_closed()`,
> `archive_subject()`, `ARCHIVE_AT` and `board.py archive` with its `--archive` (which only `split` takes now), and
> `closed_items()` as a public name; the v2 line's writers, `item_line()`, `decided_line()`, `edit_line()`, `item_problem()` and
> `canonical_item()`, and with them the refusal of a field's name in a text, context, answer, detail value or reply
> and of an answer ending `(by …)`; the text forms of the board's readers; `subject()`'s form with no id;
> `add --under`; and the edits' `--line` and `--expect`. **What a caller
> changes:** `needs_you()`, `covers()`, `sweep()`, `board_problems()`, `board_people()`, `answered_by()`,
> `people_problems()` and `answered_by_problems()` take a `Board` and no text, the sweep's board and
> `uncovered_decisions()`'s are `(origin_url, basename, board)`, read whole, and the sweep's `to_close` are ids;
> `board.py`'s edits name an item by `--id`, and a write's JSON and `list` give its id where they gave its line; `item_record()` loses `line`, gains `id`, `path`, `added`, `context`
> and `closed`, and its `text` is the item's words (its `doer`, v2.8's, is unchanged);
> `version_problem()` takes a `Board`, or a ledger's text (above; the ledger's `FORMAT_MAJOR` is not changed here); `parts_problems()`, `decide_lift()` and `closes()` take an item
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

**13. *Appendix: grammar*, *The item file (v3.0)***, with the paragraph on the field order as a production — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, text 13 (2026-11-13 split). *Rebased:* its retitle is
B5's (TD-092's round 6's F253): *The open item line (v2.3)* becomes *The open item line (v2.3; a v2 board's, read
only from v3.0)*, and each link to it follows.

**14. The rest of *The board*** — *rebased:* its writer substitutions are B5's (TD-092's text 14, each bullet's
B5 part, landing as that plan words them): *`Parts:`*'s "`item_line(parts=)` and `board.py add --parts` write it"
becomes "`item_file(parts=)` (v3.0; `item_line(parts=)` before it) and `board.py add --parts` write it"; *`Doer:`*'s
"`item_line(doer=)` and `board.py add --doer` write it" becomes "`item_file(doer=)` (v3.0; `item_line(doer=)` before
it) and `board.py add --doer` write it", "`item_problem()` faults it on any kind but `act`, no kind included" gains
"(v2; in an item file `item_file_problem()` does, v3.0)", and "which `item_problem()` faults" gains "(v2)" after
"faults"; *Trailing fields*' `Lifts:` "`item_line(lifts=)` refuses one and `item_problem()` faults one" becomes
"`item_file(lifts=)` refuses one and `item_file_problem()` faults one (v3.0; `item_line()` and `item_problem()`
before it)", and TD-075's sentence after it names `item_file_problem()` (v3.0; `item_problem()` before it). Its
opening and its B1 and B2 bullets (*Notes on a hide* to *The decide lift*, the shared *Parts:*, *Doer:* and *Trailing fields* bullets among them) moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, text 14 (2026-11-13 split); the two bullets below stay:

- *Versions*' past paragraphs (v2.3's to v2.8's) stand as written: each says what that release shipped, and the
  names it gives (`item_line()`, `item_problem()`, `canonical_item()`, `archive_closed()`, `edit_line()`) were that
  release's. Text 12 says what v3.0 removed. No build: nothing lands.
- *Appendix: grammar*, *The open item line*: its opening sentence's "a line `item_problem()` gives None for" gains
  "(v2.x; v3.0 removes `item_problem()`)". B5.

**The search** — its opening and the B1 and B2 searches moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, *The search* (2026-11-13 split); B3's and B4's moved to TD-095's plan, docs/plans/TD-095-board-writer-gate.md, *The search* (2026-11-14 split); B5's stays:

- **B5** (texts 1, 2's words, 8's *Migration* and "and no `line`", 9's swap, 10's `split` and its words, 12, 13's
  retitle, 14's writer items, 15's qualifier) first searches *Reading a board* and *The gate sweep* for "text form",
  "as texts" and "a v2 board's text" outside a v2-tagged sentence (F356), then *Edits*, as renamed, for `item_line`, `decided_line`,
  `item_problem`, `canonical_item` (whole name) and `archive_subject` (TD-092's plan, *The search*), then runs the full search: all of `SPEC.md`, for
  every name above (`item_line`, `decided_line`, `edit_line`, `item_problem`, `canonical_item`, `archive_closed`,
  `archive_subject`, `ARCHIVE_AT`, `closed_items`, `BOARD_PATH`, `BOARD_ARCHIVE_PATH`, `--line`, `--expect`,
  `--under`), each found only in a *Versions* paragraph, a v2-tagged sentence or text 12.

## Fixtures

All invented names (`pat`, `sam.lee`, `acme/widgets`, `ops`, `host-a`, sessions `w-9`, `lb-x`).

- **`fixtures/item/`** — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, *Fixtures* (2026-11-13 split).
- **`fixtures/board/<case>.v3/`** for each v2 case `fixtures/board/` holds when B5 is built (today `basic`,
  `answers`, `doer`, `hidden`, `people`, `lifts_parts` and `shared_part_left_open`; *rebased:* ten `.v3/`
  directories in all, these seven, `twins_across.v3/`, `reply_ref.v3/` and `closed_words.v3/`; round 8's F122: `doer` is
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
  below). *Rebased:* `basic`'s notes are not empty: `basic.md:8`'s `, branch feature/x` is lost at the split and
  named by D11's head note (TD-092's F238), which `basic.v3/`'s case pins. A new runner kind, `board_v3_case` (B5),
  beside `board_case` (as the ledger's `v2_case` is beside its own; `cases()` already skips a `<case>.v3/`
  directory, TD-092's plan, *The runner*): `split_board()` of the case's text gives the directory file for file, and `load_board()` of it
  gives the case's expected JSON, the JSON the v2 read gives (`items`, `closed`, `keys`, `needs_you` and `people`,
  as `board_case` prints them), compared as D6's *Comparing two reads* says (records keyed by `id` without `path`,
  `line` and a closed record's `raw`, which is the v2 line on one side and the file on the other; `keys` as a set;
  `needs_you`'s **tie groups** as sets, the groups in order; round 1's F357), since a v2 board's order is its lines' and its split's
  is id descending. The v2 cases' JSONs at B1 and B2, and `twins_across`'s read — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, *Fixtures*, `fixtures/board/` (2026-11-13 split).
- **`fixtures/board_dir/`** — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, *Fixtures* (2026-11-13 split).
- **`fixtures/board_split/<case>/`** (a new kind, `board_split_case`: `board.md`, optional `archive.md`,
  `expected.json` holding the files or the refusal, and `split_board_notes()`): `twins` (an open and a closed line
  of one key, on the board and across board and archive, each one closed item, its fields and body the closed line's
  although the open twin's detail block differs, the notes naming `open twin's detail not carried`, F378);
  `archive_prose` (an archive with a title, a note before its first item, and a `- (none)` line after it: the note
  listed as not carried, the `- (none)` carried after the board's, F378); `sections` (the `## Needs the user` and `## In-flight` headings:
  an earlier `## ` heading kept and only the one nearest the first item dropped; the README's prose kept; its links:
  an inline relative link, an image, a reference definition, a `#anchor`, an `https:` and a `mailto:` link, a
  `/rooted` path and a link inside a code span, only the relative three given `../`; and `file.md#frag`, a link with
  a title, an `<angle bracketed>` target and a `./x` one, F381; its notes listed);
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
  at two indents, one id), `people_after_items` (a `People:` line after the first item, F118), `already_v3`, `newer_major`
  (`Ledgerboard: 4`, F360),
  `closed_undated` (a `[x]` line with no readable `Closed:` date, and one with `Closed: 2026-02-30 — x.`, F160),
  `due_no_colon` (an `act` carrying `Due 2026-11-05.`, which v3 would read as a day) and `due_in_context` (an `act`
  whose Context holds `Due 3/4` and which has no other `Due`, so v2 reads that one, F164).
- **`fixtures/board_writer/`** and **`fixtures/verdict/`** (B3's and B4's) — moved to TD-095's plan, docs/plans/TD-095-board-writer-gate.md,
  *Fixtures* (2026-11-14 split); B5's `fixtures/board_writer/` cases stay here: `split` and `split_exists` (exit 1),
  and `write_v2_refused`'s message gaining *split first*; *rebased* (round 1's F368): `split_not_md`,
  `split_no_board`, `split_already_v3` (with `--board` the directory, F380), `split_archive_missing` (F379), `split_archive_other` (F388) and `split_refused` (an undated item: `split_board()`'s refusal through
  `board.py`), each exit 1. Each refusal's wording is the builder's, `Refused("<why>")` as the module's are, and its
  case pins it. `board_split` gains `head_extra` (D11's head note) beside the cases listed above.
- **`fixtures/sweep/`, `fixtures/lift/`, `fixtures/grammar/` and `fixtures/edit/`'s groups** (B1's and B2's) — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, *Fixtures* (2026-11-13 split). *Rebased:* their B5 steps,
  which TD-092's plan names, are this plan's:
  - **`fixtures/sweep/`'s rerun** (TD-092's round 9's F150): the rerun of each v2 board the split accepts
    (`beta.md` with `beta_archive.md`, `alpha.md`) runs over its split (`split_board()`, then the first run's closes
    as moves by id, its filings with `item_file()`), so it calls no removed writer; `expected.json`'s `rerun` is
    unchanged but for `widgets` (a rerun files and closes nothing, and the split keeps the ids). `widgets.md` holds
    two closed lines of one id (`TD-239`'s, answered twice, which its sweep cases need), a shape D11 refuses (round
    1's F351). It cannot leave the rerun, which runs one `sweep()` over every board and refuses a set without the
    repo's own board, `widgets` (round 2's F385, reopening F384). So for the rerun alone, once the first `sweep()` runs have
    given their results, the runner drops in memory the first of `widgets.md`'s two `TD-239` closed lines (the one
    closed 2026-10-20), splits what is left, applies the first run's closes and filings to that split as for the
    other boards (F391, F392; on `main`'s v2 path either order gives the same empty rerun) and reruns
    over that split as over the others; the file on disk and the first run's cases are untouched. `expected.json`'s
    `rerun` regenerates, and the case holds what it held: the rerun files and closes nothing on any board (were the
    reduced board to file or close anything, the builder raises it as a finding on this plan, not a fixture edit).
    The runner keeps no line writer (round 1's F384, replacing F351's `_v2_line()`).
  - **`fixtures/sweep/alpha/`** (B2's hand-written v3 stand-in for `alpha.md`'s split, TD-094) is deleted: the
    sweep's `split` case reads `split_board(alpha.md)` in memory, added to the runner's file map under `alpha/`, and
    `same` must still hold (round 1's F383).
  - **`fixtures/lift/`**: the groups that call a removed writer or a line's string form move to item files, `lines`
    becoming one item file per case line: `closes` passes each file, `close` runs `edit_item(file, …, close=True)`
    where it ran `edit_line()`, `item_lines` becomes `item_files` (the waiting-only refusals of `item_file(lifts=)`),
    and `item_problems` becomes `item_file_problems` (`item_file_problem()`); `answered_by` (`answered_by()` and
    `answered_by_problems()`, five cases over v2 board texts, `fixtures/run.py`'s lift runner) reads each case's
    board through `load_board()` over a one-file map, the text forms being gone (round 1's F352); `closed_items`
    (`parse_closed_items()`, kept) stays; `expected.json` regenerates with the same verdicts, but for
    `answered_by`'s `problems`, which become `[path, problem]`, the path the one-file map's name where a line
    number stood (`answered_by_problems()` of a `Board`; F374).
- **Retired**: `fixtures/archive/` (with `archive_closed()`), and `fixtures/edit/cases.json`'s groups `compose`,
  `edits`, `item_problems`, `canonical_items` and `archive_subjects` (B5; TD-092's plan places the rest).
- **The runner** (`fixtures/run.py`, every build's kinds) — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, *Fixtures* (2026-11-13 split).

**Unit tests** — the opening and the B1 and B2 bullets moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, *Fixtures* (2026-11-13 split); B3's and B4's moved to TD-095's plan, docs/plans/TD-095-board-writer-gate.md, *Fixtures* (2026-11-14 split); B5's stays:
- **B5**: `tests/test_item_gate.py`'s v2 properties go with `item_line()`, `decided_line()`, `edit_line()` and
  `canonical_item()`; `tests/test_ledgerboard.py`'s tests of the removed writers (`item_line()`, `decided_line()`,
  `edit_line()`, among them `test_every_edit_keeps_the_item_key`) go or move to item files, and its `sweep()` tests
  pass `(origin_url, basename, board)`; *rebased:* its `needs_you()`, preamble and people tests, which B2 left on
  text (TD-092's plan, *Unit tests*), pass a `Board` once the text forms go; the property test that `split_board()` then `load_board()` gives a board's
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

*Rebased:* the B5 parts of TD-092's table's shared rows are this plan's (TD-092's plan: "a row whose build names
B3, B4 or B5 beside B1 or B2 is shared"), each done at B5:

| function | B5's part |
|---|---|
| `BoardItem` | `text` goes; `line` stays, a v2 item's line number (read by the v2 half's problems in `_read_board_file()`, `parse_closed_items()`' fill through `_v2_fill()`, and the lift fixtures' `closed_items` group; round 1's F361; `tripwire()` and `uncovered_decisions()`, which index a v2 text by it on `main`, read the `Board` by id from B4, TD-095's D10, F375), 0 for a v3 item |
| `item_record()` | `line` goes |
| `edit_head()`, `subject()` | `subject()`'s form with no `id=` goes, and `edit_head()` with it (its one caller) |
| private names the removals leave unread (`FIELDS_RE`, `SESSION_RE`, `FIELD_NAME_RE`, `ANY_FIELD_RE` and any other) | each one that nothing left reads goes, found by a grep after the removals; one still read stays (round 1's F362) |
| `board_problems()` | the v2-text form goes |
| `_item_gate()` | the string form goes |
| `closes()`, `decide_lift()`, `parts_problems()`, `board.py`'s `_decide_ledger()` and `_check_parts()` | D7's one rule's second branch (a v2 line's string) goes (TD-092's F124, F139): an item file's text or a `BoardItem` |
| `needs_you()`, `board_people()`, `answered_by()`, `people_problems()`, `answered_by_problems()` | the text forms go: a `Board` only |
| `_read_boards()`, `covers()`, `sweep()` | the text-board form `(origin_url, basename, text, archive_text)` and its keys in `to_close` go |
| `edit_line()`, `item_problem()`, `canonical_item()`, `item_line()` (its read-back `written()`), `decided_line()`, `archive_closed()` | removed |
| `board.py` `plan_split()` | new (D11, *`board.py split`*) |

**B1, the item file**, and **B2, reading** — moved to TD-092's plan, docs/plans/TD-092-board-item-reader.md, *The builds* (2026-11-13 split).

**B3, the writer**, and **B4, the merge gate's verdicts** — moved to TD-095's plan, docs/plans/TD-095-board-writer-gate.md, *The builds* (2026-11-14 split).

**B5, migration and the release's removals.** D11, D12. Location: `ledgerboard/__init__.py` (`split_board()`,
refusing only by the ruling's two grounds (F147) and a declared major above 2, `board_stub()`,
`split_board_notes(files, board, archive="")` with its head note (D11, *rebased*); the shared rows' B5 parts above; `item_line()`, `decided_line()`, `edit_line()`, `item_problem()`,
`canonical_item()`, `archive_closed()`, `archive_subject()`, `ARCHIVE_AT` removed, `closed_items()` removed from
the public names and kept private as `_closed_lines()` for `_parse_open()`'s within-file twin set (reached through
`parse_board()`; round 1's F362), its one caller
left once `board_problems()`' v2-text form, `archive_closed()` and `item_line()`'s read-back go (round 8's F125),
`_lf_lines()` kept for `parse_item()` and `edit_item()` (round 9's F166), and B1's and
B2's shims: `item_record()`'s `line`, `subject()`'s v2 form, the readers' v2-text and v2-line arguments,
`BoardItem.text`, today's `_item_text()` and `_item_gate()`'s string form (D4's *`words` and `text`*, their callers
gone; `words` keeps its name); `parse_board()` filling no `text`; the ledger's `FORMAT_MAJOR` untouched),
`ledgerboard/board.py` (`split`, `plan_split()`, `--archive` back in `TAKES` for `split` alone, `NEEDS_OPT["split"]` `("board",)` (F370),
the write gate's *split first*, the usage docstring), `SPEC.md` (text 1, 9's swap — v2's *Edits* removed and `## Edits (v3.0)` renamed `## Edits` — 8's *Migration* and its
*Reading a board*'s "and no `line`", 2's words B2 left out, 13's retitle of *The open item line (v2.3)* B1 left out (TD-092's round 6's F253), 10's `split`, "(*split first*)" and ", and `split` removes the v2 archive", 12, 14's writer
items, 15's ", given a `Board`,"),
`fixtures/board_split/`, `fixtures/board/<case>.v3/`, `fixtures/board_writer/`
(`split`, `split_exists`, and `write_v2_refused`'s message gaining *split first*), `fixtures/run.py` (`board_split_case`, `board_v3_case` with its tie groups compared as
sets; `archive_case` and the retired `edit_cases` groups removed; `lift_cases`' `close`, `closes`, `item_lines` and
`item_problems` groups over item files, its `answered_by` group over `Board`s (F352) and `sweep_cases`' rerun over each v2 board's split, F150, and the sweep's
`split` case over an in-memory split, F383), `fixtures/sweep/alpha/` (deleted), `fixtures/lift/`
(those groups, regenerated), `fixtures/archive/` and the retired
`fixtures/edit/` groups, `tests/` (B5's bullet under *Unit tests*, F149). **Records:** `item_record()` loses `line`; every expected JSON holding a record
regenerates: `fixtures/board/*.json` and `fixtures/board/twins_across/expected.json`, `fixtures/board_dir/*/expected.json`, and `fixtures/board_writer/`'s `list`,
`list_v2` and `list_stub`. Done when: the precheck is green, every fixture passes, *The search*'s full search of
`SPEC.md` finds no removed name outside the places it allows, and `board.py split` of this repo's own board, run on
a scratch copy, reads back (its `## In-flight` and `- (none)` carried to `README.md`, F118).

Order: B1, then B2 (both merged), then B3 and B4 (either order; filed TD-103, then TD-104), then B5; TD-091 (TD-078's B4, `Blocked by` TD-070) follows B5
(round 9's F142). Then v3.0's release with TD-078's half (Paul's), each consumer's vendoring entry (agent-cadence's first),
this repo's pin bump, and only then this repo's own split (D12's order; round 1's F377).

## Not in this design

B1 and B2 (TD-092's plan); B3 and B4 (TD-095's plan). A roster repo's split from a board older than v2.3 (no
`People:` line, keys before `fmt`'s rule), with the rest of that repo's way to v3.0, is TD-100's. The ledger's own
v3.0 removals (`Waits`, `Taken by`, the old decision form, a header `Resolved`, `migrate`) and the archived entry's
writer route are TD-078's. When v3.0 is cut, and what else it carries, is Paul's.

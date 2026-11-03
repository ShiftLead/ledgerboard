# TD-023: notes on a hide that hides nothing or hides the deadline

**Status:** Designed 2026-11-03 (the designer); it waits on Paul's go. Class: **wide**, because it adds to a vendored format that both consumers run: a new public function, and a new key in `item_record()`, which is the board's JSON and the fixtures' shape (cap 6 rounds, cadence.md §4.8 *Design review rounds*). The rounds ended after round 2 by the stop rule, because its design review raised nothing build-changing. The design reviews raised 1 and then 0 build-changing findings. The fact-checks raised none, and nor did the closing fact-check. The findings no review has read are round 2's minor fixes, F11–F17, which only the closing fact-check checked. They go into the build's Fix. The review record is `docs/reviews/TD-023.md`.

**Entry:** [TD-023](../ledger/TD-023.md). It is one of the things the target design's §6 *Hide until* asks for and TD-017's build left out.

## The problem

The target design's §6 asks that `item_problem()` note (ℹ) two cases. The first is a `Hide until` in the past. The second is a `Hide until` later than the item's `Due:`, which hides the deadline itself. TD-017 (PR #72) shipped `Hide until` without either note. `item_problem(line)` cannot carry them, for two reasons:

- **It has no `today`.** "In the past" is a reading against a date, but `item_problem()` reads the line alone.
- **Everything it returns is a fault.** `board_problems()`, the board's merge gate, turns each fault into a refused write. §6 asks for an ℹ that informs and never refuses.

The second reason is the deeper one. SPEC *The gate* says a line "is judged once, when it is added". Its faults are a property of the line's text, so they do not change from one day to the next. A note against today is a different kind of thing: the same line gets no note on Monday and a note on Friday.

## Options weighed

**A. `item_problem(line, today=None)` with a separate list of notes.** This keeps one entry point, but it breaks the function's contract. `item_problem()` returns a reason or `None`, and `board_problems()` and `canonical_item()` both rely on it meaning "not in the form". Either its return type changes for every caller, or it gets a second channel that only some callers read. It also puts a today-relative reading inside the one function whose verdict must not depend on the date.

**B. A new `item_notes(item, today)` that the gate never calls (chosen).** It is a reading of a parsed item against a date, the same shape as `due_tag(item, today)`. It is reported where today-relative readings already go: in `item_record()`, beside `overdue_days`, `due_tag` and `hidden`, and by the board writer about the line it wrote. The gate, `item_problem()` and `canonical_item()` do not change, so a note can never refuse a write. This is the Done when's "never refuse a write", made structural.

**Not chosen: a board-wide `board_notes(board, today)`.** A consumer that wants every note on a board can read `notes` from `item_record()` for each `parse_board()` item. A second function would add API without adding any reading.

## The rules

`item_notes(item: BoardItem, today: date) -> list[str]` returns the item's notes in rule order. Its item is an open one, as `parse_board()` gives them, so a closed item never has notes, and an item's indent changes nothing. Dates in a note are written ISO (`YYYY-MM-DD`), as `isoformat()` gives them. Each note opens with its rule's tag, as `item_problem()`'s faults do, and carries no ℹ glyph: the glyph is a printer's. With no `Hide until`, the list is empty. Both rules are read from the parsed fields (`hide_until`, `due`, `decided`, `hidden(today)`), so a `Hide until:` inside a reply, an answer or a `Decided:` text is prose and gets no note, as the reader already rules.

1. **`hide-spent`: the hide hides nothing.** The item carries a `Hide until: D`, and `hidden(today)` is false. This covers two cases:
   - On an undecided item, D has come (D ≤ today). The note is `hide-spent: Hide until: D has come, so it hides nothing; a snooze replaces it`.
   - On a decided item, the hide never applies, because a decided item is a session's work order. The note is `hide-spent: a decided item is never hidden, so Hide until: D hides nothing`.

   The rule is `not hidden(today)` rather than D < today, so that the note means exactly that the field does nothing. On D the item already shows (`hidden()` is `today < D`), so the note starts on D.
2. **`hide-late`: the hide outlasts the deadline.** The item is hidden today, it has a `Due: E`, and D > E. The note is `hide-late: Hide until: D is after Due: E, so the item stays hidden past its deadline`. A D equal to E gets no note, because the item shows on its due date as `due`. An `fyi`, or an item whose `Due:` cannot be read, has no E and so gets no note. The rule reads only while the item is hidden: once the hide is spent, rule 1 says so, and the item shows with its true overdue count, so a note about the deadline would describe what is already over.

The two rules exclude each other (one needs `hidden(today)`, the other its negation), so an item carries at most one note today. The return is still a list, so a later rule adds a note without changing the type.

## Where the notes are read

- **`item_record()` gains `notes`**, `item_notes(item, today)`, after `hidden`. Every board fixture's records gain the key.
- **The board writer** (`board.py`) reports the notes of the open line a write leaves. That is the line `add` wrote (its reported `line`, the item's own line, above its detail block) or the line `snooze`, `due`, `decide` or `reply` edited (`--line`).
  - **How it reads them:** the writer reads the board as the write leaves it, with `parse_board(new, warn=False)`. It takes the item whose `line` is that line and passes it to `item_notes(item, today)` at the write's `--today`. With no such item, which happens when the line is the open twin of a closed one, the notes are `[]`.
  - **The JSON:** the plan's report carries `"notes": [{"line": n, "note": "<note>"}, …]`, always present for those five actions and `[]` when there are none. It appears both in a write's `--json` and in `--plan`. `done`, `fmt`, `archive`, `rank` and `list` carry no `notes` key. `done` leaves no open line, and `list --json` already carries each record's `notes`.
  - **The text mode:** without `--json` or `--plan`, each note is printed on stderr as `line n: ℹ <note>`, after the subject and paths, as the `kept:` lines are.
  - **The exit code:** a note never changes it, and the write is made.
  - **Notes it did not cause:** the writer reports the line's notes as the write leaves them, including one the write did not cause. A `reply` or `due` on a line whose hide is late reports `hide-late`. A `decide` on a hidden item reports the decided `hide-spent`, since deciding it ends the hide. That is deliberate: the note describes the line the caller just touched.
- **Nothing else.** `board_problems()`, `item_problem()`, `canonical_item()`, `needs_you()` and every edit's refusals are unchanged. What a consumer shows of a note is the consumer's. No consumer needs to change for the build: a consumer that reads `item_record()` by key ignores the new one, so no entry is filed in agent-cadence or ShiftLead.

## The `SPEC.md` text

**1. *The board*, a new paragraph right after the `**`Hide until:`** (v2.3)` paragraph:**

> **Notes on a hide** (`item_notes(item, today)`, v2.3, of a parsed open item as `parse_board()` gives it) inform and never refuse: no gate reads them. Each opens with its rule's tag, and D and E stand for the ISO dates of the fields.
> - `hide-spent` is a `Hide until:` on an open item that is not hidden today. Either its date has come (`hide-spent: Hide until: D has come, so it hides nothing; a snooze replaces it`), or the item is decided (`hide-spent: a decided item is never hidden, so Hide until: D hides nothing`).
> - `hide-late` is a hidden item whose `Hide until: D` is later than its `Due: E` (`hide-late: Hide until: D is after Due: E, so the item stays hidden past its deadline`). An `fyi`, or an item whose `Due:` cannot be read, has no deadline, so it never gets a `hide-late`.
>
> An item carries at most one of them. `item_record()` carries them as `notes`.

**2. *The board writer (v2.3)*, a sentence appended to the paragraph that opens "Each write prints the commit subject":**

> A write that leaves an open line also reports that line's notes, as the write leaves it (`item_notes()` at `--today`). The writes that do are `add`, `snooze`, `due`, `decide` and `reply`. With `--json` or `--plan`, the notes are `notes`, `[{"line", "note"}]` (each names its line, as a write names one, where `item_record()`'s `notes` is the record's own list of strings), always present and `[]` when there are none. Without either, each is printed on stderr as `line n: ℹ <note>`. A note never changes the exit code.

**3. *Versions*, in the v2.3 paragraph, the clause `` `item_record()` gains `hide_until` and `hidden`, and `needs_you()` and `edit_action()` are new `` becomes:**

> `item_record()` gains `hide_until`, `hidden` and `notes`, and `needs_you()`, `edit_action()` and `item_notes()` are new

The `fixtures/run.py` docstring's `board/` line reads `item_record()` whole, so its wording does not change. Its `edit/cases.json` line gains `item_notes()` (v2.3), and `edit_cases()` gains the `item_notes` group (below), since it reads each group by name.

## The fixture cases

- **`board/hidden.md`** (the file is unchanged; `hidden.json` is regenerated). At the fixtures' `TODAY`, 2026-01-15, the regenerated records hold:
  - line 6 (`Due: 2026-01-13. Hide until: 2026-01-20.`): `hide-late: Hide until: 2026-01-20 is after Due: 2026-01-13, so the item stays hidden past its deadline`;
  - line 7 (`Hide until: 2026-01-15`, today): `hide-spent: Hide until: 2026-01-15 has come, so it hides nothing; a snooze replaces it`;
  - line 8 (decided, `Hide until: 2026-01-20`): `hide-spent: a decided item is never hidden, so Hide until: 2026-01-20 hides nothing`;
  - line 16 (an fyi, `Hide until: 2026-01-14`): `hide-spent: Hide until: 2026-01-14 has come, so it hides nothing; a snooze replaces it`;
  - line 17 (an fyi hidden until 2026-02-01, with no `Due:`): `[]`;
  - lines 19 and 20 (a `Hide until:` inside an answer and inside a `Decided:` text): `[]`;
  - every other line: `[]`.
- **`board/basic.json`, `board/answers.json` and `board_writer/list/expected.json`** gain `"notes": []` on every record.
- **`board_writer/snooze/`**: it already snoozes an item due 2026-01-20 to 2026-01-29, so it is the `hide-late` case. Its `expected.json` gains `"notes": [{"line": 7, "note": "hide-late: Hide until: 2026-01-29 is after Due: 2026-01-20, so the item stays hidden past its deadline"}]`, and it still exits 0 and writes the file.
- **`board_writer/snooze_spent/`** (new): the same board and line, snoozed `--to 2026-01-15` at `--today 2026-01-15`. It exits 0, writes `Hide until: 2026-01-15.`, and its JSON carries `hide-spent: Hide until: 2026-01-15 has come, so it hides nothing; a snooze replaces it` for line 7.
- **`board_writer/decide_hidden/`** (new): `decide`'s board with ` Hide until: 2026-01-17.` after line 8's `Due: 2026-01-18.`, and `decide`'s command (`--line 8 --answer Disk --today 2026-01-15`). It exits 0, writes the `Decided:`, and its JSON carries `[{"line": 8, "note": "hide-spent: a decided item is never hidden, so Hide until: 2026-01-17 hides nothing"}]`.
- **Every other `expected.json` of `add_*`, `due`, `decide` and `reply`** (`add_act`, `add_answered`, `add_crlf`, `add_decide`, `add_decided`, `add_empty_section`, `add_fyi_no_heading`, `add_hidden`, `due`, `decide`, `reply`) gains `"notes": []`. `add_hidden`'s hide (2026-01-19) is before its `Due:` (2026-01-22), so its list is empty too. The `expected.json` of `done`, `plan_done`, `fmt`, `archive*` and `rank*` does not change. Nor does any refusal's (`add_refused_field`, `edit_moved`, `edit_newer_major`, `edit_not_open`), since a refused write prints only why and so carries no `notes`.
- **`edit/cases.json`**: an `item_notes` group, `[{"name", "line"}]`. Each line is read as `parse_board(line, warn=False)[0]` and given to `item_notes()` at the file's `today`, and the expected output is each name's list. The group holds:
  - a hide one day before `Due:` (no note);
  - a hide equal to `Due:` (no note);
  - a later hide on a line whose `Due:` cannot be read (no note);
  - a later hide on an `fyi` that carries a `Due:` anyway (no note, since an fyi is never due).

  Each is a line the board fixture does not already hold.

## The build

One build, `**Part of:** TD-023`: everything above, in one PR with its `SPEC.md` text, code and fixtures (AGENTS.md). Beside the fixtures, the build adds unit tests (`tests/`), because the writer fixtures capture only `--json`'s stdout. The tests cover `item_notes()` directly, the text mode's `line n: ℹ <note>` on stderr, `notes` under `--plan`, and the exit code staying 0. The `board.py` module docstring gains a line saying that a write reports its line's notes.

**Done when:** `item_notes()` returns the two notes as *The rules* say, and `item_record()` and `board.py` report them as *Where the notes are read* says. No gate or edit refuses because of one. The three `SPEC.md` passages above land with the code. The fixtures above pass (`python3 fixtures/run.py`), and so does the suite.

**Which release.** The target design's §6 put these notes in v2.3, and v2.3 is not yet tagged (TD-021). A key added to `item_record()` before a release costs the consumers nothing, since their vendor PRs take v2.3 whole. Added after, it is one more release to vendor. So the build lands in v2.3, and TD-021's `**Blocked by:**` gains the build's id when it is filed.

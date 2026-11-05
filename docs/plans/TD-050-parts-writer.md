# TD-050: the writer of a decide's `Parts:`

**Status:** Draft 1, 2026-11-04 (session lb-designer). Class: **wide** (a vendored, published format: a new
`item_line()` keyword, a new pure function and a new `board.py add` option, which both consumers vendor; cap 6
rounds, cadence.md §4.8). Rounds: in progress (the record: [docs/reviews/TD-050.md](../reviews/TD-050.md)).

**Entry:** [TD-050](../ledger/TD-050.md). Asked for by agent-cadence TD-221; ShiftLead's TD-1378 shows the field.

## The problem

`Parts:` has been read, ordered and keyed since v2.3 (SPEC *The board*, `Parts:`), and v2.4's `covers()`,
`decide_lift()` and `closes()` all read it. No writer writes it: `item_line()` takes no `parts=` (and its
read-back refuses any line that reads back with parts, `ledgerboard/__init__.py`, the `got[0].parts` test at the
end of `item_line`), and `board.py`'s `TAKES["add"]` holds no `parts`. SPEC says so: "What an answer does to the
parts it lists is v2.4's, and so is its writer." Target design §7.1's v2.3 row: "the writer that fills it and
checks the parts' gates comes in v2.4". v2.4 shipped without it.

So a design's end-of-rounds item cannot hold its builds. The shape target design §6 (*One go for a parent's
parts*) agreed is one `decide` whose Context names the parent and its gate, `Context: TD-12 decision (Paul).
Parts: TD-15, TD-16.`, which `covers()` counts as covering each listed part's gate, and whose one answer
`decide_lift()` applies to all of them. Without the writer, a consumer has no tool to write it, and the gate sweep
files one `Go | Not yet` item per held build beside the parent's.

## What is already settled

These are written down, and this design takes them as given:
- the field's form, place, order and key (SPEC *The board*, `Parts:`; *The form the writers write*; the grammar
  appendix's `parts`), and the line checks `item_problem()` already makes (only on a `decide`, ids each once,
  right after the Context, a period after the ids);
- **the writer refuses a snapshot whose parts do not all carry the gate, or are not all `Part of` the named
  parent** (target design §6, *One go for a parent's parts*, agreed 2026-11-02). So TD-050's open option "no check
  at write time" is out;
- the parent need not carry the gate itself; the item names exactly one entry; parts that need a different Ask get
  their own items (same section);
- what an answer does to the parts it lists (SPEC *The decide lift*, *Closing on the answer*).

## Decisions

**D1. It ships in v2.5, the next tagged release.** A release is `v<major>.<minor>` (SPEC *Versions*), so there is no
v2.4 patch to put it in; v2.4 is tagged, and SPEC already labels the next release's additions v2.5 (*Host-log checks*). It
is no version event: the item key and the line's form are unchanged, and v2.3 and v2.4 read every line it writes.

**D2. The work is split as the package splits** (target design §1.1): the line in the module, the ledger in the
file writer.
- **`item_line(…, parts=None)`** writes the field and checks what the line alone can show. `parts` is a list or
  tuple of strings, each exactly `TD-` and 1 to 18 ASCII digits, `TD-[0-9]{1,18}` (no stripping, no other case:
  `td-9`, ` TD-9`, `TD-١٢` and a 19-digit id are refused, and a bare string is refused as not a list). It is
  written ` Parts: <ids>.` right after the Context (ahead of the `Due:`), ordered by number (`TD-9` before
  `TD-10`), separated by `, `, each as the caller spelled it. It is refused, each a refusal of its own:
  - on any kind but `decide`;
  - for an empty list, an id not of that form (`other#TD-9` among them), two ids of one number (`TD-15`,
    `TD-015`), or an id of the Context entry's number;
  - when the Context does not name exactly one entry, a bare `TD-[0-9]{1,18}`, and exactly one gate, a
    `decision (<p>)` (as `_item_gate()` reads them);
  - when none of its answers lifts, as `_lifting()` reads one (`Go` among the answers in any case when `lifts`
    is not given, else `lifts` given; never a waiting-only label), since a snapshot no answer lifts is a question
    no press can act on.

  An element that is not a string is refused as not an id (`Refused`, never a `TypeError`). These checks on the
  parts and the Context are one private helper, which `parts_problems()` also calls, so the two cannot drift. The
  read-back test checks the line reads back with exactly those parts, in place of refusing any. `parts=None` is no
  field; every check above concerns a call that passes parts.
- **`parts_problems(item_line, entries, archived=()) -> list[str]`** (new, pure) checks a snapshot against the
  ledger. It judges what needs the ledger, and leaves what the line alone shows to `item_line()`'s helper. It never
  raises, on any string, any mapping and any iterable: it lists problems, each a fixed string.
  - **Nothing to judge, `[]`:** a string that is not an open item line, an item that is not a `decide`, or one
    with no `Parts:`.
  - **The line first.** A `decide` with `Parts:` that `item_line()`'s helper faults (an id not
    `TD-[0-9]{1,18}`, a `<repo>#` part, two ids of one number, an id of the Context entry's number, a Context not
    naming one bare entry and one `decision (<p>)`) gives the one problem `line: <the helper's reason>`, the words
    `item_line()` refuses with, and nothing else is judged. So no id outside `TD-[0-9]{1,18}` reaches a number.
  - **Its inputs.** `entries` maps id to text, open and archived texts alike, by number (`TD-9` in the line finds
    the entry `TD-009`), the first key of a number winning. A key that is not a bare `TD-[0-9]{1,18}` (`x`,
    `TD-١٢`, a 19-digit number, `other#TD-9`) is ignored, and a value that is not a string, or holds no entry, is
    no entry. `archived` holds the ids the caller read from the ledger's archive, by number, a member that is not
    such an id ignored. This is narrower than `decide_lift()`, which reads any `\d+` run as a number. An entry is
    archived when its number is in `archived` (an archived entry may read `Open`, SPEC *Superseded and dropped*)
    or its Status's first word is an archived one (`ARCHIVED_WORDS`). A gate is carried as `decide_lift()` reads
    it (`_carried`: the person compared case-insensitively); an archived entry carries nothing. A part's `Part of`
    is the Context's entry only when `parse_part_of(…)[0]` is a bare `TD-[0-9]{1,18}` of its number: none, a second
    parent, another repo's or an unreadable value is not. The parent may carry the gate or not.
  - **Then the Context entry**: `<ref>: missing` or `<ref>: archived`; the parts are judged still.
  - **Then each part, in the line's order, its first fault alone**: `<id>: missing`, `<id>: archived`, `<id>: not
    Part of <ref>`, `<id>: does not carry <gate>`. `<id>` and `<ref>` are as the line spells them, `<gate>` as the
    Context writes it.

  The line's faults are `item_line()`'s, judged once, so `parts_problems()` holds six strings of its own. They
  exist in it, as `line:`, only so that it never raises on a line written by hand.
- **`board.py add --parts TD-a,TD-b`** passes the list to `item_line()`, reads the ledger (`--ledger <v2
  directory>`, else `ledger/` beside the board when it is a directory, as `decide` does), and refuses the write
  (exit 1) when `parts_problems()` names any problem, listing them all. Its checks run in this order, the first
  that fails deciding the exit and the message, with `--plan` as with a write:
  1. the options: `--parts` with `--decided`, `--ledger` without `--parts`, an empty piece (exit 1);
  2. `item_line()` (exit 1): the kind, the ids' form (so `other#TD-9` is refused here, and `parts_problems()`'s
     `line:` serves other writers), their numbers, the Context, a lifting answer, as `_lifting()` reads one
     (any case, never a waiting-only label);
  3. the ledger: none found (exit 1), or one that cannot be used (exit 2);
  4. `parts_problems()` (exit 1, every problem): refused as `the snapshot does not match the ledger: <p1>; <p2>`,
     the problems in `parts_problems()`'s order, joined by `; `;
  5. the board's gate, `board_problems()`, as for every `add`.
  - `--parts` may be given more than once, as `--answer` and `--lift` are; each value is split on `,`, each piece
    stripped of whitespace, and an empty piece (`TD-15,`) is a refusal.
  - It writes each id as given, as it writes the Context. `plan_add` gains `parts` and `ledger` keywords; its
    `decided` guard refuses both; `build()` hands it `parts=None` when no `--parts` was given (the `[]` default
    never reaches `item_line()`); and the report (`plan.info`, `--json`, `--plan`) is unchanged: the line, the
    subject, the paths and `item_notes`.
  - It hands `parts_problems()` the open and the archived text of the Context entry and of each part, each read
    through `Ledger.entry_file(tid_of(id))` and `files[path]`, as `_decide_ledger` reads them, but keeping the
    archived ones, which `decide`'s ledger half drops, and naming them in `archived` (the `archived` flag
    `entry_file` returns); an id `entry_file` refuses is skipped, so it is a listed problem (missing), never a
    usage error.
  - No `--ledger` and no `ledger/` beside the board is a refusal naming `--ledger` (exit 1). The ledger is opened
    as `_decide_ledger` opens it, `Ledger.open` then `_writable`, so an explicit `--ledger` that cannot be used
    (missing, a v1 ledger, a newer major) is exit 2, as for `decide`.
  - `TAKES["add"]` gains `parts` and `ledger`, `DEFAULTS` gains `"parts": []`, and `--parts` is an `append` option;
    `--ledger` on an `add` without `--parts` is then a `Refused` (exit 1), not argparse's usage error.
  - `--parts` combines with `--said` and `--by` (both lines `plan_add` composes carry it). `--parts` with
    `--decided`, and `--ledger` on an `add` without `--parts`, are refused.

**Why the check is at write time and in the writer.** `item_line()` is pure and reads no file (AGENTS.md), and
`board_problems()`, the board's gate, has no ledger, so neither can check a part's `Part of` or gate. A snapshot
written unchecked would let `covers()` count a build as covered by an item whose answer `decide_lift()` then
refuses (a part not `Part of` the parent), leaving the person a question no press can answer. `parts_problems()`
is pure over texts the caller passes, as `pickable()`'s resolver and `decide_lift()`'s entries are, so a consumer
writing a line by other means calls the same check. It is stricter than `decide_lift()` on purpose, in three places:
- a part that does not carry the gate is refused at write time, where at answer time `decide_lift()` skips it and
  logs `gate lift skipped` (the part lost the gate after the question was asked);
- an `event (<name>)` Context is refused (*Why a decision gate only*), where `decide_lift()` still lifts one
  written by hand;
- an archived part is refused. `decide_lift()` skips one whose Status is an archived word and whose text it is
  given, and lifts one whose text it is given that reads `Open` (it has no `archived` input). `board.py decide`
  today gives it no text for an entry in the archive directory (`_decide_ledger` keeps open entries alone), so the
  lift refuses the whole answer as a part missing.

That last is a gap in `decide`, and its reach (`closes()`, `lift_pr_verdict()`) is its own design: TD-051, filed
by this plan's PR and named in TD-050's `Related`. Nothing here depends on it, and v2.5 need not wait for it: the
gap is there today for any snapshot written by hand. Until it lands, a parent's item whose part was archived after
it was asked is answered by closing it (`done`) and adding a fresh snapshot of the parts still held.

**Why ordered by number, and spelled as given.** The snapshot is part of the item key, "since a changed snapshot
is a different question". The same parts in another order are the same question, so the writer orders them. Their
spelling is the caller's, as the Context's entry is on every item: a v2 ledger pads its ids (`TD-009`) and the sweep
writes an entry's id as the ledger spells it, where a caller of `item_line()` writes what it was given, and every reader (`covers()`, `decide_lift()`, `closes()`) compares
ids by number, so a spelling changes a key but never a meaning. Spelling one canonical way would be a rule for
every ref on the board, not for this field.

**Why bare ids only.** `decide_lift()` refuses a `<repo>#TD-n` part ("a part is Part of its parent, in the same
ledger"), and `covers()` finds a part through its own `Part of`, in its own ledger. A cross-repo Context entry
(`<repo>#TD-n`) is refused for the same reason: its parts live in a ledger this writer is not given.

**Why a decision gate only.** Target design §6 has the parent item name "a person's gate", and the case it serves
is a design's builds, held on the person's go. An `event (<name>)` gate is matched by its name, but each entry
carries its own check section, so one name on a parent and its parts can be different checks, which one `Drop the
gate` would lift together. The writer refuses it for now; loosening a writer's refusal later moves nothing that is
read, where tightening one would leave lines already written. The reader and `decide_lift()` are unchanged and
still read an event snapshot written by hand.

**D3. Nothing else changes.** No edit writes or rewrites `Parts:` (a changed snapshot is a new item: close the old
one, add the new); `item_problem()`, `canonical_item()`, `covers()`, `decide_lift()`, `closes()` and `sweep()` are
unchanged; the sweep still files per-entry items for gates nothing covers, and a parent item written by this
writer is what covers them.

## Consumers

agent-cadence's `board_edit.py` passes `add` through, so `--parts` needs only its vendor PR (its TD-221, filed).
ShiftLead's Queue shows the field (its TD-1378, filed). No new consumer entry is needed. A consumer writes
`Parts:` only once every reader of its board runs v2.3, which every consumer already does.

## The SPEC text the builds land

Each anchor below is quoted by its words; in SPEC.md they wrap across lines (the `add` bullet's "`--hide-until`)"
and the exit table's "or, for `decide`, a ledger that cannot be used as asked" among them).

Each build lands only text that is true once it merges: B1's text names no `board.py` option, and B2 adds those
clauses.

**1. *The board*, the `Parts:` paragraph.** Its last sentence, "What an answer does to the parts it lists is
v2.4's, and so is its writer.", becomes, in B1:

> What an answer does to the parts it lists is *The decide lift*'s (v2.4). `item_line(parts=)` writes it, and
> `parts_problems()` checks it against the ledger (v2.5, *Edits*).

and, in the same paragraph, "The writers write the ids separated by `, `." becomes "The writers write the ids in
number order, separated by `, `.";

and B2 inserts, after "`item_line(parts=)`", " and `board.py add --parts`" (so "… `item_line(parts=)` and
`board.py add --parts` write it, …").

**2. *Edits*, *A new item*** (B1). The signature gains `parts`:
`item_line(text, due, today, session, host, context, *, kind, answers, default, detail, hide_until, lifts,
parts)`, and the one-line form becomes `… — <text> Context: <context>.[ Parts: <ids>.] Due: <due>.` After the
sentence on `Lifts: …`, add:

> A decide's `parts` (v2.5) writes ` Parts: <ids>.` right after the Context, the ids ordered by number, separated
> by `, `, each as given. It is refused on any kind but `decide`. It is refused for an empty list, for an id that
> is not `TD-` and 1 to 18 ASCII digits, and for an id that shares its number with another or with the Context's
> entry. It is refused unless the Context names exactly one entry, a bare `TD-n`, and one gate, a
> `decision (<person>)`. And it is refused unless one of its answers lifts (as *Closing on the answer* reads a
> lifting answer). The reader is looser: it reads ids in any order and keys them as written, and `item_problem()`
> faults neither order nor two spellings of one number, so a hand-written order or spelling is a different key.

and after the paragraph on `decided_line()`, a new paragraph:

> **A snapshot against the ledger** (`parts_problems(item_line, entries, archived=())`, v2.5) lists, and never
> raises, why a `decide` line's `Parts:` does not match the ledger. A line that is no open `decide`, or carries no
> `Parts:`, gives `[]`. One whose parts or Context `item_line()` would refuse gives `line: <its reason>` alone.
> Otherwise it reads `entries` (id to text, open and archived alike, by number, the first of a number winning; a
> key that is not a bare `TD-` and 1 to 18 ASCII digits is ignored, and a value that is not a string, or holds no
> entry, is no entry) and `archived` (the ids read from the ledger's archive, by number). An entry is archived
> when its number is in `archived` or its Status is an archived one. The Context entry gives `<ref>: missing` or
> `<ref>: archived`, and each part, in the line's order, its first fault of `<id>: missing`, `<id>: archived`,
> `<id>: not Part of <ref>`, `<id>: does not carry <gate>`. It is stricter than *The decide lift*, which skips a
> part that no longer carries the gate (one archived by its Status among them) and still lifts an `event
> (<name>)` snapshot: the snapshot is checked when the question is asked, the lift when it is answered. The ledger
> is not in the line, so `item_line()` does not check these; a writer that reads the ledger calls it.

**3. *The board writer*, the `add` bullet** (B2). After "`--hide-until`)", add:

> ; with `--parts TD-a,TD-b` (v2.5; repeatable, split on `,`), a decide's snapshot (`item_line(parts=)`). The
> line's own refusals come first. Then the ledger is read (`--ledger <v2 directory>`, default `ledger/` beside
> the board when it is a directory, its open and archived entries), and the write is refused, with every problem,
> when `parts_problems()` names any, or when no ledger is found. `--parts` with `--decided`, and `--ledger`
> without `--parts`, are refused

and in the exit table, "or, for `decide`, a ledger that cannot be used as asked" becomes "or, for `decide` and
`add --parts`, a ledger that cannot be used as asked".

**4. *Versions*.** A paragraph after v2.5's others, in B1:

> **v2.5 gives `Parts:` its writer** (*Edits*): `item_line(parts=)` and `parts_problems()`. Nothing read changes:
> v2.3 and v2.4 read every line it writes, and no key moves.

and B2 changes "(*Edits*): `item_line(parts=)` and `parts_problems()`" to "(*Edits*, *The board writer*):
`item_line(parts=)`, `parts_problems()` and `board.py add --parts`".

The grammar appendix is unchanged: `parts` and its "each id once" rule are there since v2.3.

## Fixtures

Fixture names are invented (`pat`), never a person's (AGENTS.md).

`fixtures/edit` (`item_line`):
- a `decide` with `parts=["TD-10", "TD-9"]`, Context `TD-4 decision (pat)`, a Due, answers and a detail block:
  the line carries ` Parts: TD-9, TD-10.` between the Context and the `Due:` (numeric, not lexical, order),
  `item_problem()` gives None, and the key holds the field;
- `parts=["TD-015"]` is written `TD-015` (the caller's spelling);
- with `parts`, `lifts` and `hide_until` together: ` Parts:` after the Context and before ` Due:` and ` Hide until:`,
  ` Lifts:` after the Answers; answers `go — build both | Not yet` (a lower-case `Go` with a consequence) accepted;
- refused: an `act` with parts; a decide whose answers are `Yes | No` with no `lifts`; `parts="TD-9"` (a
  string); `parts=[9]` and `[None]`; a Context naming a 19-digit entry or `TD-١٢`; `td-9`; ` TD-9`; `TD-١٢`; `TD-` and 19 digits; `parts=[]`; `TD-15` and `TD-015`; `other#TD-15`; the Context's own `TD-4`, and
  `TD-004`; a Context naming two entries; a Context naming an entry and no gate; a Context naming
  `TD-4 event (build-green)`; a Context naming `other#TD-4`.

`parts_problems()`, a new `parts_problems` key in `fixtures/sweep/cases.json`, each case carrying its own `entries`
(id to text) and, where it needs one, its own board text, so the sweep's shared `ledger.md` and boards, and every
`runs` and `rerun` expectation, are untouched:
- matching snapshots, each `[]`: `Context: TD-4 decision (pat). Parts: TD-9, TD-10.` with both parts `Part of:
  TD-4` carrying `decision (pat)` and the parent carrying none; the same with the parent carrying it; the parts
  carrying `decision (Pat)` (the person in another case); the line listing `TD-9` and `TD-10` for the ledger's `TD-009` and `TD-010`;
- one problem each, its string as above: a part `Part of` another entry; a part with no `Part of`; a part whose
  `Part of` is `other#TD-4`, a 5000-digit id or `TD-١٢`; a part not carrying the gate; a part archived by its
  Status; a part named in `archived` whose Status reads `Open`; a part missing; the Context entry archived; the
  Context entry missing;
- order: two faulty parts, listed in the line's order; one part both not `Part of` the parent and not carrying the
  gate, giving `not Part of` alone; the Context entry missing with a faulty part, giving both;
- inputs: `entries` holding `TD-9` and `TD-009` (the first wins); keys that are no id (`x`, a 19-digit and a
  5000-digit id, `TD-١٢`, `other#TD-9`: each ignored, no exception); a text holding no entry and a value that is no
  string (missing); `archived` holding `other#TD-9` and `5` (ignored);
- `line:`, alone, the reason `item_line()` gives: a Context naming two entries; naming `TD-4 event (build-green)`;
  naming `other#TD-4`; naming a 19-digit entry; hand-written `Parts: TD-9, TD-009.`, `Parts: TD-١٢.`, a 19-digit
  part, `Parts: other#TD-9, TD-9.` (no exception in any);
- `[]`: an `act` line, a `decide` with no `Parts:`, a closed `- [x]` decide, a string that is no item;
- for each matching case, `covers()` over its line, on a board that is the repo's own (named by the `repo` the
  case gives, as `acme/widgets` is in the sweep's cases, since a bare `TD-n` is read only there) and whose
  `People:` lists `pat`, reads each listed part, one by one, as covered (`open`) by the parent's item;
- the cross-check with *The decide lift*: for each matching case, `decide_lift()` answered `Go` by `pat`, with `board_people=["pat"]`, accepts
  it and changes every listed part; for the not-`Part of`, no-`Part of`, missing and `other#TD-9` cases it refuses;
  for the Context entry archived or missing, and the two-entry and `other#TD-4` `line:` cases, it refuses;
  where the two differ by design: the not-carrying case and the part archived by its Status (its text given) it
  accepts and logs `gate lift skipped`; the `TD-4 event (build-green)` case (both parts carrying the event) it
  accepts and lifts both; the part named in `archived` reading `Open` (its text given) it accepts and lifts, the
  case TD-051 settles.

These sit in `fixtures/sweep`, not `fixtures/lift`, because the `covers()` check needs a board, its `People:` and
a `repo`, which the sweep's runner already reads; the `decide_lift()` cross-check rides with them.

`fixtures/run.py` gains what runs these: `parts` in the `edit` runner's `item_line` keywords, the
`parts_problems` loop in `sweep_cases()` (guarded by `hasattr(L, "parts_problems")`, as it guards `sweep`), with
its `covers()` and `decide_lift()` checks, and a v2.5 line in its docstring.

`fixtures/board_writer`:
- `add_parts`: the line written, its `--json` output, `ledger/` found beside the board;
- `add_parts_ledger`: the same through `--ledger`;
- `add_parts_order`: `--parts TD-10,TD-9` against the ledger's `TD-009.md` and `TD-010.md`, written
  `Parts: TD-9, TD-10.` (ordered, spelled as given);
- `add_parts_split`: `--parts "TD-9, TD-10"` and `--parts TD-9 --parts TD-10` write the same line;
- `add_parts_said`: with `--said` and `--by`, the line carries both, and the subject keeps the words out;
- `add_parts_archived_part`: a part in `archive/` whose Status is an archived word: refused (exit 1),
  `TD-9: archived`;
- refused (exit 1, files unchanged), each with a usable `ledger/` beside the board unless named: `add_parts_not_part_of`,
  `add_parts_gate_gone`, `add_parts_no_ledger` (none), `add_parts_on_act`, `add_parts_on_act_no_ledger` (none: the
  kind's refusal, step 2, before the ledger's), `add_parts_xrepo` (`other#TD-9`: `item_line()`'s refusal),
  `add_parts_decided`, `add_parts_empty_piece` (`TD-9,`), `add_ledger_without_parts`;
- `add_parts_on_act_v1` (an `act` with a v1 `--ledger`): exit 1, the kind's refusal, the ledger never opened;
- `add_parts_missing` (a part the ledger holds in neither its open nor its archived files): exit 1, the problem
  listed;
- `add_parts_ledger_v1` (a v1 ledger file passed as `--ledger`) and `add_parts_ledger_none` (a `--ledger` path
  that does not exist): exit 2;
- `add_parts_context_archived` (the parent in `archive/`): exit 1, `TD-4: archived`;
- `add_parts_archived_dir` (a part in `archive/` whose Status reads `Open`): exit 1, `TD-9: archived`;
- `add_parts_plan`: `--plan` prints the line and writes nothing;
- `add_parts_no_kind`: `--parts` with no `--kind`: refused (exit 1), the kind's refusal.

## The builds

Filed on Paul's go, each `**Part of:** TD-050`. TD-051 (`decide` and an archived part) is filed apart, by this
plan's PR, as a design of its own:
- **B1, the module half:** `item_line(parts=)` and `parts_problems()`, B1's SPEC text (1, 2 and 4 as above), the
  `edit` and `sweep` fixtures above, `fixtures/run.py`'s runners for them, and unit tests in `tests/` where its
  suites cover the code touched (`item_line`'s read-back), with one that `parts_problems()` never raises on
  arbitrary lines, ids and mappings. Done when those fixtures and tests pass and that SPEC text lands with the code.
- **B2, the file writer:** `board.py add --parts` and `--ledger` on `add`, B2's SPEC text (3, and its clauses in 1
  and 4), the `board_writer` fixtures above, unit tests in `tests/test_board_writer.py` for `TAKES`/`DEFAULTS` and the
  check order, and `board.py`'s own text: its usage block, the module docstring's exit line and the `--ledger`
  help. SPEC's v2.4 exit note under *Versions* is history and stays. Blocked by B1. Done when those fixtures and
  tests pass and that SPEC text lands with the code.

B1 and B2 both say v2.5, so the v2.5 tag (Paul's) follows B2; a tag cut between them would ship `item_line(parts=)`
without its writer, and B2 would be relabelled.

This plan's PR also rewrites TD-050's Fix and Done when to point here (`ledger.py edit`), adds TD-051 to its
`Related`, and files TD-051.

Target design §7.1's v2.3 row is amended by a dated note under the table, as TD-045's is, in this plan's PR; and
§6 *One go for a parent's parts* by a dated note naming the writer's decision-only rule.

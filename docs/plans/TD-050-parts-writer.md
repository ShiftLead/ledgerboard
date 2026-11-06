# TD-050: the writer of a decide's `Parts:`

**Status:** Draft 1, 2026-11-04 (session lb-designer). Class: **wide** (a vendored, published format: a new
`item_line()` keyword, a new pure function and a new `board.py add` option, which both consumers vendor; cap 6
rounds, cadence.md §4.8). Rounds: **ended at the cap**, 2026-11-04, and Paul bought **one more round** (round 7,
2026-11-05) (the record: [docs/reviews/TD-050.md](../reviews/TD-050.md)). Build-changing findings per round 1–7,
design reviews 1, 2, 2, 2, 1, 3, 1; fact-checks apart 0, 0, 0, 2, 3, 3, 0, and the closing fact-checks 2 (round 6)
and 0 (round 7); PR #160's review of round 7 raised one more (F95, a cross-check case listed on the wrong side).
Recurring topic: how `parts_problems()` judges a line written by hand (F41, F57, F74, F75, F82,
F83); round 7's review called the `item_problem()`-first layer the wrong shape (F87), and the plan now reads the
item as `decide_lift()` does and leaves the form to `board_problems()`. Round 7's build-changing finding (F86,
words after the gate defeat `covers()`) is a new topic. The plan also moves to the next release after v2.5,
tagged 2026-11-05 without it (D1). Paul bought **one more round** again (round 8, 2026-11-05): a design review of
F86–F96, which raised four build-changing findings (F97–F100: a SPEC rule text 2 cited but SPEC never stated; the
plan stale against TD-051's build, TD-052, already merged into v2.6; two fixture cases undefined or in the wrong
runner) and four minor ones (F101–F104). Paul bought **one more round** again (round 9, 2026-11-06): a design
review of F97–F104 found them applied as described and raised one build-changing finding (F105: an id in
`archived` with no text was `missing` or `archived` by guess) and four minor ones (F106–F109). F105–F109 are applied
and read by no design review. Waits on Paul's go (the board's decide item); recommended: One more round.

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

**D1. It ships in the next tagged release after v2.5, written v2.6 here.** A release is `v<major>.<minor>` (SPEC
*Versions*), so there is no v2.5 patch to put it in; v2.5 is tagged (2026-11-05, #158) without it. The target
design (§7.1's note of 2026-11-05) calls its next Status release v2.6; whichever is tagged first takes v2.6, and
if the Status release is, each build writes the number of the release it ships in where this plan writes v2.6.
v2.6 is not tagged, and SPEC's *Versions* already holds an untagged v2.6 paragraph (TD-051's build, TD-052, #163:
`decide_lift(archived=)`), so this plan's v2.6 text joins that release as a paragraph of its own beside it (SPEC
text 4). It is no version event: the item key and the line's form are unchanged, and v2.3, v2.4 and v2.5 read every line it
writes.

**D2. The work is split as the package splits** (target design §1.1): the line in the module, the ledger in the
file writer.
- **`item_line(…, parts=None)`** writes the field and checks what the line alone can show. `parts` is a list or
  tuple of strings, each exactly `TD-` and 1 to 18 ASCII digits, `TD-[0-9]{1,18}` matched whole (`fullmatch`, so
  `TD-9\n` is refused; no stripping, no other case:
  `td-9`, ` TD-9`, `TD-١٢` and a 19-digit id are refused, and a bare string is refused as not a list). It is
  written ` Parts: <ids>.` right after the Context (ahead of the `Due:`), ordered by number (`TD-9` before
  `TD-10`), separated by `, `, each as the caller spelled it. It is refused, each a refusal of its own:
  - on any kind but `decide`;
  - for an empty list, an id not of that form, a `<repo>#` id, two ids of one number (`TD-15`,
    `TD-015`), or an id of the Context entry's number;
  - when the Context does not name exactly one entry, a bare `TD-[0-9]{1,18}`, and exactly one gate, a
    `decision (<p>)` (as `_item_gate()` reads them), with nothing after the gate (the qualifier `_sweep_context()`
    reads after it is empty: `covers()` reads an item whose Context goes on past its gate, `TD-4 decision (pat) —
    design ready`, as naming no entry, so a snapshot written so would cover none of its parts);
  - when none of its answers lifts, as `_lifting()` reads one (`Go` among the answers in any case when `lifts`
    is not given, else `lifts` given; never a waiting-only label), since a snapshot no answer lifts is a question
    no press can act on.

  An element that is not a string is refused as not an id (`Refused`, never a `TypeError`). The checks on the
  parts and the Context are one private helper, which `parts_problems()` also calls, so the two cannot drift. It
  takes the Context's words and the list of parts (the caller's list in `item_line()`; `parse_parts()`'s in
  `parts_problems()`, which reads only `TD-`-shaped tokens, so a stray word there is `board_problems()`'s to fault)
  and gives its first fault as a fixed string, or None, checking in this order:
  1. `context: not one entry and one decision` — the Context does not name exactly one bare `TD-[0-9]{1,18}` and
     one `decision (<p>)`, or has words after the gate (a non-empty qualifier, as `_sweep_context()` reads it);
  2. then each part in order, its first fault: `<id>: another repo's entry` (`<repo>#TD-[0-9]{1,18}`, `<repo>`
     matching `REPO_RE`), `<id>: not
     an id` (anything else that is not a bare `TD-[0-9]{1,18}`; a non-string element is written `<repr>: not an
     id`), `<id>: the Context's entry` (its number), `<id>: twice` (an earlier part of its number, so the later
     one is named);
  3. `no parts` for an empty list.

  `item_line()` refuses with that string as the whole of its `Refused` message, exactly (`context: not one entry
  and one decision`, `TD-9: twice`), with no prefix (its kind and lifting-answer refusals stay its own, outside
  the helper). With `parts`, its order is: the existing kind check (a kind not in `KINDS`), then `parts` on a kind
  other than `decide`, then `parts` not a list or tuple; then the
  existing checks up to and including the Context's own words, in the code's order as today (the text, today, the
  Due, a host without its session, the session's and host's names, then `_item_words(context)`); then the helper, given the Context as `item_line()` then holds it (`ctx`,
  its final `.` removed; `none` when no Context was given, which the helper faults), ahead of every existing
  check that reads the Context's entries or gate (so a two-entry Context is refused as `context: not one entry
  and one decision`, not as today's "a decide that lifts a gate names exactly one entry"); then the remaining
  existing checks (the answers, `default`, the detail block, `lifts`); then the lifting answer. Without `parts`
  nothing moves. The
  read-back test checks the line reads back with exactly those parts, in place of refusing any. `parts=None` is no
  field; every check above concerns a call that passes parts.
- **`parts_problems(item_line, entries, archived=()) -> list[str]`** (new, pure) checks a snapshot against the
  ledger. It reads the item as `decide_lift()` does, by `parse_board()` and never `item_problem()`, judges what needs the ledger, and leaves the line's
  form to `board_problems()`, the gate every board write passes (as `decide_lift()` does). It never raises, on
  any argument: an `item_line` that is not a string gives `[]`, `entries` that is not a mapping is no entries,
  and `archived` that is not an iterable is empty (a bare string is iterated, and its characters, being no ids,
  are ignored). It lists problems, each a fixed string.
  - **The item.** `parse_board(item_line, warn=False)` directly, without `decide_lift()`'s `ITEM_RE` guard, so a
    line with its detail block, or a board, is read where `decide_lift()` refuses the string. Nothing to judge,
    `[]`: anything but exactly one open item (a line with its detail block is one item, and so is a board
    holding one open item; a detail block holding a nested `- [ ]` line is two), an item that is not a
    `decide`, one already `Decided:` (a settled question: a part archived since is no fault), or one whose
    `item.parts` is empty (no `Parts:`, or one holding no `TD-`-shaped token, such as `Parts: foo.`). So `no
    parts` is `item_line()`'s alone.
  - **The form is not judged here.** A hand-written `Parts: TD-9, TD-9.`, `Parts: TD-9,TD-10.` or `Parts: TD-9,
    foo.` is read as `parse_parts()` reads it (the repeat collapsed, the ids read however separated, the stray
    word dropped), as `decide_lift()` reads it; `item_problem()` faults each, at `board_problems()`, and a
    writer that writes through the board writer never writes one. Column, spacing and trailing-space faults
    are the same.
  - **Then the helper**, given the Context as `_sweep_context()` reads it from `item.text` (the words of
    `CONTEXT_RE` over `_gate_body()`, its final `.` removed as `item_line()` removes it) and `item.parts`. A fault gives the one problem `line: <its string>`
    (`line: TD-009: twice` for `Parts: TD-9, TD-009.`, `line: context: not one entry and one decision` for a
    Context naming two entries or going on past its gate), and nothing else is judged. So no id outside
    `TD-[0-9]{1,18}` reaches a number.
  - **Its inputs.** `entries` maps id to text, open and archived texts alike, by number (`TD-9` in the line finds
    the entry `TD-009`), the first key of a number winning. A key that is not a bare `TD-[0-9]{1,18}` (`x`,
    `TD-١٢`, a 19-digit number, `other#TD-9`) is ignored, and a value that is not a string, or holds no entry, is
    no entry. `archived` holds the ids the caller read from the ledger's archive, by number, a member that is not
    such an id ignored. A key or member that is not a string is ignored. This is narrower than `decide_lift()`, which reads any `\d+` run as a number. An entry is
    archived when its number is in `archived` (an archived entry may read `Open`, SPEC *Superseded and dropped*)
    or its Status's first word is an archived one (`ARCHIVED_WORDS`). `archived` is read first: a number in it
    with no text in `entries` is `archived`, never `missing`, as `decide_lift()` reads a number in `archived` it
    is given no text for (the way `board.py decide` calls it). A gate is carried as `decide_lift()` reads
    it (`_carried`: the person compared case-insensitively); an archived entry carries nothing. A part's `Part of`
    is the Context's entry only when `parse_part_of(…)[0]` is a bare `TD-[0-9]{1,18}` of its number: none, a second
    parent, another repo's or an unreadable value is not. The parent may carry the gate or not.
  - **Then the Context entry**: `<ref>: missing` or `<ref>: archived`; the parts are judged still.
  - **Then each part, in the line's order, its first fault alone**: `<id>: missing`, `<id>: archived`, `<id>: not
    Part of <ref>`, `<id>: does not carry <gate>`. `<id>` and `<ref>` are as the line spells them, `<gate>` as the
    Context writes it.

  The line's faults are the helper's, written once; `parts_problems()`'s own forms are `missing`, `archived`, `not
  Part of` and `does not carry`, and it passes the helper's on as `line:` so that it never raises on a line
  written by hand and never judges a snapshot `covers()` would not read as one.
- **`board.py add --parts TD-a,TD-b`** passes the list to `item_line()`, reads the ledger (`--ledger <v2
  directory>`, else `ledger/` beside the board when it is a directory, as `decide` does), and refuses the write
  (exit 1) when `parts_problems()` names any problem, listing them all. Its checks run in this order, the first
  that fails deciding the exit and the message, with `--plan` as with a write:
  1. the options: `--parts` with `--decided`, `--ledger` without `--parts`, an empty piece (exit 1);
  2. `item_line()` (exit 1, its `Refused` message as it stands, a helper fault being the helper's string
     exactly), in its order (D2): the kind, the line's own checks, the helper (the Context, then
     each id, so `other#TD-9` is refused here, as another repo's entry, and `parts_problems()`'s `line:` serves
     other writers), the answers, a lifting answer, as `_lifting()` reads one (any case, never a waiting-only
     label);
  3. the ledger: none found (exit 1), or one that cannot be used (exit 2);
  4. `parts_problems()` (exit 1, every problem): refused as `the snapshot does not match the ledger: <p1>; <p2>`,
     the problems in `parts_problems()`'s order, joined by `; `. `add` has no "ledger half", so step 3's refusals
     carry no `the ledger half: ` prefix (which `_decide_ledger` gives its own): they are `Ledger.open`'s and
     `_writable`'s words as they stand, and the fixtures pin them;
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
    `entry_file` returns); an id `entry_file` or `tid_of()` refuses (`Unusable`, a `Refused`, as for `TD-0`) is
    caught as `Refused`, as `_decide_ledger` catches it, and skipped, so it is a listed problem (missing), never a
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
writing a line by other means calls the same check. It is stricter than `decide_lift()` on purpose, in five places:
- a part that does not carry the gate is refused at write time, where at answer time `decide_lift()` skips it and
  logs `gate lift skipped` (the part lost the gate after the question was asked);
- an `event (<name>)` Context is refused (*Why a decision gate only*), where `decide_lift()` still lifts one
  written by hand;
- a Context with words after its gate (`TD-4 decision (pat) — design ready`) is refused, where `decide_lift()`
  reads no qualifier and lifts it: `covers()` reads such an item as naming no entry, so the writer refuses a
  snapshot the sweep would not count, though its answer would still lift;
- an archived part is refused. `decide_lift()` (v2.6, TD-052) skips (and, on a lifting answer, logs) a part named in `archived` whose
  text it is not given, and one whose text it is given and whose Status is an archived word; a part named in
  `archived` whose text it is also given is read from the text (open before archived), so one reading `Open` and
  carrying the gate is lifted. `board.py decide` passes the archive's ids in `archived` and no archived text, so
  through it an archived part is always skipped; `parts_problems()`, where a number in `archived` wins, calls it
  `archived` either way;
- a Context entry named in `archived` whose Status reads `Open` is `<ref>: archived`, where `decide_lift()`,
  given its text, lifts (the text wins; it refuses a Context entry in `archived` only when it is not given its
  text, and one whose Status is an archived word).

The archived cases differ on purpose: a snapshot is judged by where the ledger keeps the entry, and the lift by the
text its caller hands it (TD-051's plan, Option A). TD-051 was filed by this plan's first PR (#154) and built as
TD-052 (#163); nothing here depends on it beyond the release they share.

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
writer is what covers them: its Context is one entry and one decision gate with nothing after it, which
`_sweep_context()` reads with an empty qualifier, and `covers()` counts each listed part that is `Part of` that
entry.

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
> `parts_problems()` checks it against the ledger (v2.6, *Edits*).

and, in the same paragraph, "The writers write the ids separated by `, `." becomes "The writers write the ids in
number order, separated by `, `.";

and B2 inserts, after "`item_line(parts=)`", " and `board.py add --parts`" (so "… `item_line(parts=)` and
`board.py add --parts` write it, …").

**2. *Edits*, *A new item*** (B1). The signature gains `parts`:
`item_line(text, due, today, session, host, context, *, kind, answers, default, detail, hide_until, lifts,
parts)`, and the one-line form becomes `… — <text> Context: <context>.[ Parts: <ids>.] Due: <due>.` After the
sentence on `Lifts: …`, add:

> A decide's `parts` (v2.6) writes ` Parts: <ids>.` right after the Context, the ids ordered by number, separated
> by `, `, each as given. It is refused on any kind but `decide`. It is refused for an empty list, for an id that
> is not `TD-` and 1 to 18 ASCII digits, and for an id that shares its number with another or with the Context's
> entry. It is refused unless the Context names exactly one entry, a bare `TD-n`, and one gate, a
> `decision (<person>)`, with nothing after the gate (*The gate sweep* reads an item whose Context goes on past
> its gate as naming no entry, so it would cover no part). And it is refused unless one of its answers lifts (as *Closing on the answer* reads a
> lifting answer). The reader is looser: it reads ids in any order and keys them as written, and `item_problem()`
> faults neither order nor two spellings of one number, so a hand-written order or spelling is a different key.

and after the paragraph on `decided_line()`, a new paragraph:

> **A snapshot against the ledger** (`parts_problems(item_line, entries, archived=())`, v2.6) lists, and never
> raises, why a `decide` line's `Parts:` does not match the ledger. It reads the item as *The decide lift* does,
> its detail block or a board holding it as its one open item included, and leaves its form to `item_problem()`. A string that is not exactly one open item, an item that is no
> `decide` or is decided, or one whose `Parts:` holds no id `parse_parts()` reads gives `[]`. One whose Context
> or parts the check `item_line()` shares faults gives `line: <that fault>` alone, the fault one of
> `context: not one entry and one decision` (a Context naming two entries, or going on past its gate, among them),
> `<id>: another repo's entry`, `<id>: not an id`, `<id>: the Context's entry` and `<id>: twice`; the kind, an
> empty list and the lifting answer are `item_line()`'s alone. Otherwise it reads `entries` (id to text, open and
> archived alike, by number, the first of a number winning; a key that is not a bare `TD-` and 1 to 18 ASCII
> digits is ignored, and a value that is not a string, or holds no entry, is no entry) and `archived` (the ids
> read from the ledger's archive, by number). An entry is archived when its number is in `archived` or its Status
> is an archived one. It judges the Context entry first, `<ref>: missing` or `<ref>: archived`, and then each
> part still, in the line's order, its first fault of `<id>: missing`, `<id>: archived`, `<id>: not Part of
> <ref>`, `<id>: does not carry <gate>`. It is stricter than *The decide lift*, which skips a part that no longer
> carries the gate (one archived by its Status, or named in `archived` and not given, among them), still lifts an
> `event (<name>)` snapshot and one whose Context goes on past its gate, and, reading a text it is given ahead of
> `archived`, lifts a part and a Context entry named in `archived` whose Status reads `Open`: the
> snapshot is checked when the question is asked, the lift when it is answered. The ledger is not in the line, so
> `item_line()` does not check these; a writer that reads the ledger calls it.

**3. *The board writer*, the `add` bullet** (B2). After "`--hide-until`)", add:

> ; with `--parts TD-a,TD-b` (v2.6), a decide's snapshot (`item_line(parts=)`): the option may be repeated,
> each value is split on `,` and each piece trimmed, and an empty piece is refused; `--parts` with `--decided` is
> refused, and so is `--ledger` without `--parts`. The line's own refusals come first. Then the ledger is read
> (`--ledger <v2 directory>`, default `ledger/` beside the board when it is a directory, its open and archived
> entries), and the write is refused, with every problem, when `parts_problems()` names any, or when no ledger is
> found

and in the exit table, "or, for `decide`, a ledger that cannot be used as asked" becomes "or, for `decide` and
`add --parts`, a ledger that cannot be used as asked".

**4. *Versions*.** A paragraph after the existing "**v2.6 answers a parent's item whose part was archived**"
paragraph (TD-052's, in the same untagged release), in B1:

> **v2.6 gives `Parts:` its writer** (*Edits*): `item_line(parts=)` and `parts_problems()`. Nothing read changes:
> v2.3, v2.4 and v2.5 read every line it writes, and no key moves.

If v2.6 is tagged before B1 merges, B1 writes the release it ships in, and its paragraph follows that release's
others (D1).

and B2 changes "(*Edits*): `item_line(parts=)` and `parts_problems()`" to "(*Edits*, *The board writer*):
`item_line(parts=)`, `parts_problems()` and `board.py add --parts`".

**5. *The gate sweep*, the `covers()` paragraph** (B1). Text 2 rests on a rule the code has had since v2.4 and SPEC
never stated (`_names_entry()` takes only an item whose `_sweep_context()` qualifier is empty). "each `decide` item
whose Context names the entry and the gate, or the entry's parent (its `Part of`) with the gate and the entry among
its `Parts:`," becomes:

> each `decide` item whose Context names the entry and the gate, or the entry's parent (its `Part of`) with the gate
> and the entry among its `Parts:`, with nothing after the gate (a Context that goes on past it, `TD-4 decision
> (pat) — design ready`, names no entry here),

It describes what v2.4 already does, so no *Versions* line goes with it.

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
- refused, each with its pinned message: a two-entry Context and an `other#TD-4` Context, each
  `context: not one entry and one decision` (the helper ahead of today's one-entry check); an `act` with parts; a decide whose answers are `Yes | No` with no `lifts`; `parts="TD-9"` (a
  string); `parts=[9]` and `[None]`; a Context naming a 19-digit entry or `TD-١٢`; `td-9`; ` TD-9`; `TD-١٢`; `TD-` and 19 digits; `parts=[]`; `TD-15` and `TD-015`; `other#TD-15`; the Context's own `TD-4`, and
  `TD-004`; a Context naming an entry and no gate; a Context naming `TD-4 event (build-green)`; Contexts
  `TD-4 decision (pat) — design ready` and `TD-4 decision (pat), PR #3 merged` (words after the gate), each
  `context: not one entry and one decision`; a Context `Design TD-4 decision (pat)` (words before it) accepted
  (that `covers()` reads it is pinned in `parts_problems`' matching cases, below, since the `edit` runner calls no
  `covers()`).

`parts_problems()`, a new `parts_problems` key in `fixtures/sweep/cases.json`, each case carrying its own `entries`
(id to text) and, where it needs one, its own board text, so the sweep's shared `ledger.md` and boards, and every
`runs` and `rerun` expectation, are untouched:
- matching snapshots, each `[]`: `Context: TD-4 decision (pat). Parts: TD-9, TD-10.` with both parts `Part of:
  TD-4` carrying `decision (pat)` and the parent carrying none; the same with the parent carrying it; the parts
  carrying `decision (Pat)` (the person in another case); the line listing `TD-9` and `TD-10` for the ledger's `TD-009` and `TD-010`;
  `Context: Design TD-4 decision (pat). Parts: TD-9, TD-10.` (words before the gate);
- one problem each, its string as above: a part `Part of` another entry; a part with no `Part of`; a part whose
  `Part of` is `other#TD-4`, a 5000-digit id or `TD-١٢`; a part not carrying the gate; a part archived by its
  Status; a part named in `archived` whose Status reads `Open`; a part missing; the Context entry archived by its
  Status (`<ref>: archived`); the Context entry named in `archived` whose Status reads `Open`, its text given
  (`<ref>: archived`); the Context entry missing; a part, and the Context entry, each named in `archived` with no
  key in `entries` (`<id>: archived`, `<ref>: archived`, never `missing`);
- order: two faulty parts, listed in the line's order; one part both not `Part of` the parent and not carrying the
  gate, giving `not Part of` alone; the Context entry missing with a faulty part, giving both;
- inputs: `entries` holding `TD-9` and `TD-009` (the first wins); keys that are no id (`x`, a 19-digit and a
  5000-digit id, `TD-١٢`, `other#TD-9`: each ignored, no exception); a text holding no entry and a value that is no
  string (missing); `archived` holding `other#TD-9`, the string `"5"` and the int `5`, and `entries` an int key (each ignored);
- `line:`, alone, the helper's string (each pinned, e.g. `line: TD-009: twice`): a Context naming `TD-4 event (build-green)`;
  naming `other#TD-4`; naming a 19-digit entry; hand-written `Parts: TD-9, TD-009.`, `Parts: TD-١٢.`, a 19-digit
  part, `Parts: other#TD-9, TD-9.` (no exception in any);
- `line: context: not one entry and one decision`, alone: a Context naming two entries; Contexts
  `TD-4 decision (pat) — design ready` and `TD-4 decision (pat) PR #3` (words after the gate);
- read as `parse_parts()` reads them, the form not judged: hand-written `Parts: TD-9, TD-9.` (one part `TD-9`),
  `Parts: TD-9,TD-10.` (both) and `Parts: TD-9, foo.` (`TD-9`), each against a matching ledger giving `[]`, and
  one with two leading spaces and trailing spaces giving `[]`;
- `[]`: `Parts: foo.`; a two-item string; a detail block holding a nested `- [ ]` line;
- a matching snapshot's line with its detail block, and a board holding it as its one open item: judged as one
  item, giving `[]`, and a faulty one with its detail block giving its ledger problems;
- `[]`: an `act` line, a `decide` with no `Parts:`, a closed `- [x]` decide, a decided decide (`Decided: Go (by
  pat) (…)`) whose part is archived, a string that is no item, and `None`, `5` and `b"…"` as `item_line`;
- for each matching case, `covers()` over its line, on a board the runner builds from the case: a one-item board
  holding the line under a `People: pat` header, given as the repo's own (its origin URL and basename those of the
  sweep's `acme/widgets` board, and `repo` `acme/widgets`, since a bare `TD-n` is read only there), and each part's
  text with the gate as that part carries it (`decision (Pat)` in that case), reads each listed part, one by one,
  as covered (`open`) by the parent's item; and for each words-after-the-gate `line:` case, with a matching ledger,
  `covers()` on the same board shape gives `[]` for each part (SPEC text 5);
- the cross-check with *The decide lift*: for each matching case, `decide_lift()` answered `Go` by `pat`, with
  `board_people=["pat"]`, accepts it and changes every listed part; for the not-`Part of`, no-`Part of`, `Part of`
  `other#TD-4` and missing cases it refuses; for the Context entry archived by its Status or missing, and the two-entry,
  `other#TD-4` and `other#TD-9` `line:` cases, it refuses; where the two differ by design: the not-carrying case
  and the part archived by its Status (its text given) it accepts and logs `gate lift skipped`; the
  `TD-4 event (build-green)` case (both parts carrying the event) and the words-after-the-gate cases it accepts
  and lifts both; the part named in
  `archived` reading `Open` (its text given, and its id in `decide_lift()`'s `archived` too) it accepts and lifts,
  the text read ahead of `archived` (TD-052), and so for the Context entry named in `archived` reading `Open` (its
  text given). The Context entry archived by its Status is the one refused among the Context cases above. Not
  cross-checked: the 5000-digit and `TD-١٢` cases (`decide_lift()` reads any `\d+` run as a number, and raises
  `ValueError` on 5000 digits, `int()`'s limit, which this design does not change), and the `line:` cases for
  `twice` (`Parts: TD-9, TD-009.`, which `decide_lift()` accepts, lifting the one entry) and a 19-digit part,
  each a hand-written form the writer never writes; the order and inputs cases and the read-as-`parse_parts()`
  cases, which test `parts_problems()`'s own reading and say nothing of the lift; and the `line:` case naming a
  19-digit Context entry, which `decide_lift()` refuses as not among the entries given. The words-after-the-gate
  cases carry a matching ledger, both parts `Part of: TD-4` carrying `decision (pat)`. The cases named in
  `archived` with no text are cross-checked with that `archived`: `decide_lift()` refuses the Context entry as
  archived, and skips the part, logging `gate lift skipped`.

These sit in `fixtures/sweep`, not `fixtures/lift`, because the `covers()` check needs a board, its `People:` and
a `repo`, which the sweep's runner already reads; the `decide_lift()` cross-check rides with them.

`fixtures/run.py` gains what runs these: `parts` in the `edit` runner's `item_line` keywords, the
`parts_problems` loop in `sweep_cases()` (guarded by `hasattr(L, "parts_problems")`, as it guards `sweep`), with
its `covers()` and `decide_lift()` checks, and a v2.6 line in its docstring.

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
- `add_parts_missing` (a part the ledger holds in neither its open nor its archived files, and `TD-0`, which
  `tid_of()` refuses): exit 1, each listed as `missing`;
- `add_parts_ledger_v1` (a v1 ledger file passed as `--ledger`) and `add_parts_ledger_none` (a `--ledger` path
  that does not exist): exit 2;
- `add_parts_context_archived` (the parent in `archive/`, its Status `Done`): exit 1, `TD-4: archived`;
- `add_parts_context_archived_open` (the parent in `archive/`, its Status reading `Open`): exit 1, `TD-4: archived`;
- `add_parts_context_tail` (`--context "TD-4 decision (pat) — design ready"`): exit 1, the helper's `context:`
  refusal, the ledger never read;
- `add_parts_archived_dir` (a part in `archive/` whose Status reads `Open`): exit 1, `TD-9: archived`;
- `add_parts_plan`: `--plan` prints the line and writes nothing;
- `add_parts_no_kind`: `--parts` with no `--kind`: refused (exit 1), the kind's refusal;
- `add_parts_both_faults`: a bad part and a gate person missing from `People:`: exit 1, step 4's refusal;
- `add_parts_twice_repeat`: `--parts TD-9 --parts TD-9`: exit 1, `TD-9: twice`;
- `add_parts_hide_until`: with `--hide-until`, the line carries both in order.

## The builds

Filed on Paul's go, each `**Part of:** TD-050`. TD-051 (`decide` and an archived part) was filed apart, by this
plan's first PR (#154), as a design of its own, and built as TD-052 (#163):
- **B1, the module half:** `item_line(parts=)` and `parts_problems()`, B1's SPEC text (1, 2, 4 and 5 as above), the
  `edit` and `sweep` fixtures above, `fixtures/run.py`'s runners for them, and unit tests in `tests/` where its
  suites cover the code touched (`item_line`'s read-back), with one that `parts_problems()` never raises on
  arbitrary lines, ids and mappings. Done when those fixtures and tests pass and that SPEC text lands with the code.
- **B2, the file writer:** `board.py add --parts` and `--ledger` on `add`, B2's SPEC text (3, and its clauses in 1
  and 4), the `board_writer` fixtures above, unit tests in `tests/test_board_writer.py` for `TAKES`/`DEFAULTS` and the
  check order, and `board.py`'s own text: its usage block, the module docstring's exit line and the `--ledger`
  help. SPEC's v2.4 exit note under *Versions* is history and stays. Blocked by B1. Done when those fixtures and
  tests pass and that SPEC text lands with the code.

B1 and B2 both say v2.6, so the tag that ships them (Paul's) follows this B2: a tag cut between TD-050's B1 and B2
would ship `item_line(parts=)` without its writer, and B2 would be relabelled. Either the tag waits for both, or
Paul moves TD-050 to the release after it.

This plan's first PR (#154) rewrote TD-050's Fix and Done when to point here (`ledger.py edit`), added TD-051 to
its `Related`, and filed TD-051.

Target design §7.1's v2.3 row is amended by a dated note under the table, as TD-045's is, in this plan's PR; and
§6 *One go for a parent's parts* by a dated note naming the writer's decision-only rule.

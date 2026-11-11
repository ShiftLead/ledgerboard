# TD-065: `Doer:`, who should do an act item's step

**Status:** Draft 1, 2026-11-11 (session lb-designer). Class: **wide** (a vendored, published format: a new
field on the board's item line, read by both consumers, with a change to what a `Context:` reads; cap 6 rounds,
cadence.md §4.8). Rounds: not yet run (the record: [docs/reviews/TD-065.md](../reviews/TD-065.md)).

**Entry:** [TD-065](../ledger/TD-065.md). Asked for by ShiftLead (its design TD-1543, builds TD-1660 and TD-1661).

## The problem

An `act` item says a step someone must take, and nothing on its line says who. The person reads the text and
the detail block and decides. ShiftLead's **Have a session do it** (its TD-1543) hands the step to a session
when the person presses it, and Paul chose on 2026-11-11 that the line names the doer in a field, so the press
goes straight to that repo's or team's seat. The board is this repo's format: ShiftLead and agent-cadence read
and write it only through vendored ledgerboard, so until `SPEC.md`, the module and `board.py` know the field, no
consumer can write it or read it back.

The ask was `Doer: <repo>.` or `Doer: team <team>.`, on an `act` line only, after `Context:` and ahead of `Due:`.
This design takes that shape and settles what the ask left open: the team name's grammar, the item key, what a
reader older than the release does, what every other field-name rule does with `Doer:`, and the reader's record.

## What is already settled

- **A field read in its place.** `Parts:` (v2.3) is the precedent: read only as the field right after the
  Context, never inside a reply's words, its name in every field-name set the module keeps, faulted by
  `item_problem()` on a kind that does not take it, refused by `item_line()` on that kind, and part of the item
  key (*The board*, `Parts:`). `Doer:` follows it point for point.
- **`<repo>`** is *The ledger*'s repo grammar (v2.4; the `repo` production in *Appendix: grammar*), compared
  case-insensitively.
- **A person's name** (*The board*, `People:`; *Appendix: grammar*): runs of letters, digits, `_` and `-`,
  joined by single dots, compared case-insensitively.
- **The item key** strips only the tick, `Closed:`, `Decided:`, `Due:`, `Hide until:` and the reply tails;
  changing what it is for a given line is a new major (*The item key*).
- **A field that changes what is read** ships in a minor that says so, and consumers write it only once every
  reader of the board runs that minor (v2.3's `Parts:`, `Lifts:` and `Hide until:`, *Versions*).

## Options weighed

**Where the doer goes.** (a) A field on the line, as asked. (b) A bullet in the detail block. (c) Words in the
text. The detail block is the person's prose, no edit touches it, `item_problem()` never reads it, and two
writers would spell a bullet two ways; text has no grammar at all. Only (a) gives a value a reader can trust, and
Paul chose it for ShiftLead's design. **(a).**

**What a team's name is.** (a) A person's name's grammar. (b) The repo grammar. (c) Any word. A team is named by
people, never a path, so the repo grammar's `/`, its leading dots and its components fit nothing a team is
called. Any word lets `,`, `;` and `)` in, which the rest of the line's names refuse. A person's name's grammar
holds every team name a consumer has (`ops`, `web-grind`, `lb.core`), is already compared case-insensitively,
and already has a fixture set. **(a).** A team is named alone, not as `<repo> team <team>`: which repo a team
works in is the consumer's to resolve (ShiftLead reads it from its own configuration), and the format knows no
team list.

**The item key.** (a) The key keeps `Doer:`, as it keeps `Context:` and `Parts:`. (b) The key strips it, as it
strips `Due:`. Stripping it changes the key of any line that already holds the words `Doer: …` (none is known,
but the rule is about every line), which *The item key* makes a major. And the doer is part of what the item
asks: an act for one repo and an act for another are two requests, not one request moved. No edit changes the
doer, so nothing would need the key to hold across a change. **(a): no key moves.**

**Which kinds take it.** (a) `act` alone. (b) `act` and the kindless to-do. (c) Every kind. The ask is `act`'s,
and a consumer acts on `act` alone. A `decide` waits on the person, a `look` on the person's eyes, a `watch` on
a date, an `fyi` on nothing. A later minor can widen it with no change to what is read: the reader reads `Doer:`
on any kind already (below), and only `item_problem()`'s fault and the writer's refusal would loosen. **(a).**

**The record.** (a) The value as written, one string. (b) Its kind and name apart. (c) Both. A consumer that has
only (a) re-parses `team ` to route, which is format knowledge outside the module. A consumer that has only (b)
rebuilds the words to quote the field. **(c)**: `{"kind": "repo" | "team", "name": <as written>, "text": <the
value as written>}`.

## Decisions

**D1. The field.** `Doer: <repo>.` or `Doer: team <team>.`: the word `Doer:` (this case alone), one space, the
value, a period. `<repo>` is *The ledger*'s repo grammar; `<team>` is a person's name, after the word `team` (lower
case) and one space. A repo named `team` is `Doer: team.`: a team value always has a second word. The value runs
to the field's final period, and a repo that ends in `.` (which the repo grammar allows) is not a doer: `Doer:
acme..` does not read, and `item_line(doer="acme.")` is refused, so the period that ends the field is never part
of the name. Each name is kept as written and compared case-insensitively.

**D2. Its place.** On an item line, right after the `Context:` (after a `Parts:`, where one stands there) and
ahead of the `Due:`: the line's order is `Context:`, `Parts:`, `Doer:`, `Due:`, `Hide until:`. `Parts:` stands only
on a `decide` and `Doer:` only on an `act`, so a line the writers write carries one of them at most. A `Context:`
ends at a ` Doer:`, and so does a `Parts:`. The reader reads `Doer:` only there (as the field that follows the
Context, or the `Parts:` that follows it), never inside a reply's words, and on any kind; `item_problem()` faults
it on any kind but `act`.

**D3. The reader.** The reader is looser than the writers, as for `Parts:`. It finds the field as `PARTS_RE`
finds `Parts:`: ` Doer:` (after whitespace) then any whitespace, its **value** running to where the next field
begins (` Due:`, ` Hide until:`, ` Answers:`, ` Lifts:`, ` Decided:`, ` Closed:`) or the line's end, with the
whitespace at its ends and then one final `.` taken off. The value reads as a **team** when it is `team`, a run of
spaces or tabs, and a person's name; else as a **repo** when it is in the repo grammar and does not end in `.`;
else it does not read. So `Doer:acme.`, `Doer: acme` (no period) and `Doer: team  ops.` read (and `item_problem()`
faults their spelling, D5), while `Doer: acme..`, `Doer: two words.` and `Doer: Team ops.` do not.
`parse_doer(text)` gives `("repo" | "team", name, text)`, the name and the value as they stand on the line (no
whitespace collapsed), or None: no `Doer:` in its place, or a value that does not read. `BoardItem.doer` holds it;
`item_record()` gains `doer`, `{"kind", "name", "text"}` or None (`text` the value: `acme/widgets`, `team ops`).
Nothing else reads it: `needs_you()`'s classes, `item_notes()`, the gate sweep and the merge gate's verdicts are
unchanged, and the sweep files its `act` items with no doer. `board.py list` gains it through `item_record()`.

**D4. A field name everywhere `Parts:` is one.** `Doer:` joins every set of field names the module keeps, as
`Parts:` stands in each: the fields that end a `Context:` (`CONTEXT_RE`) and a `Parts:` (`PARTS_RE`), and
`FIELDS_RE`, `FIELD_NAME_RE`, `ANY_FIELD_RE`, `WRITER_FIELD_RE`, `GATE_FIELD_RE`. It is case-sensitive, as every
name but `Due:` is. So:
- the writers refuse text, a context, an answer, a detail value, a reply's words and a `--said` that holds
  `Doer:` (as they refuse `Parts:`). A consumer that files an item from a ledger title holding the words (this
  entry's own title does) meets the refusal and rephrases; `decided_line()` cuts the name (below), `item_line()`
  does not;
- `item_problem()` faults a `Doer:` in an item's text as naming a field;
- a commit subject's head stops before it (`edit_head()`), as it does before every field;
- `decided_line()` cuts it from a title and an answer as it cuts every field name (`ANY_FIELD_RE`).

A reply's words that hold `Doer:` on a line written by hand are the person's: the reader never reads them as the
field.

**D5. `item_problem()`.** A new rule, tagged `doer:`, beside `parts:`:
- `doer: <a kind> carries no `Doer:`: only an act names who does its step` on any kind but `act` (a decided
  `act` takes one);
- `doer: `Doer:` stands more than once`;
- `doer: `Doer:` names a repo, `<repo>`, or a team, `team <name>``, for a value that does not read (D3);
- `doer: written `Doer: <value>.`, one space after `Doer:` and after `team``, for a value that reads but is
  spaced otherwise;
- `doer: no period after its value`;
- `doer: `Doer:` follows Context` when it does not stand right after the `Context:` or the `Parts:` that follows it.
`Due:`'s order rule reads `Doer:` as it reads `Parts:`: a `Due:` right after a `Doer:` is in its place. So does
`Hide until:`'s: on a line with no `Due:`, the field it follows is the `Doer:` where one stands (the chain becomes
`Due`, else `Doer`, else `Parts`, else `Context`). The rebuilt line the rule compares spacing against (`want`)
gains ` Doer: <value>.` after the Context and any `Parts:`.

**D6. The writers.** `item_line(…, doer=None)` takes the value exactly as the field writes it (`acme/widgets`,
`team ops`) and writes ` Doer: <value>.` right after the Context. Unlike text, it is neither trimmed nor collapsed:
it is refused unless it is a repo in the grammar not ending in `.`, or `team`, one space and a person's name, with
no other whitespace (so `" team ops"`, `"team "`, `"team  ops"` and `"team a b"` are refused, and a caller never
gets the repo `team` by dropping a name). It is refused on any kind but `act`, and, as every input is, unless the
reader reads back exactly what was meant (`parse_doer()` among the read-back). `decided_line()` takes no doer: it writes a `decide`.

`board.py add --doer <value>` passes it to `item_line(doer=)`; the line's own refusals come first. With
`--decided` it is refused (a decided line is a `decide`).

The five edits keep the `Doer:` byte for byte. `snooze`, `due`, `decide` and `reply` read the line back and compare
its fields (`answers`, …, `lifts`, `parts`); `doer` joins that comparison, so an edit that changed it is refused.
`done` checks the item key alone, which holds the `Doer:`. No edit changes the doer: a step for another doer is
a new item, the old one closed. `due` on an item with no `Due:` appends it at the
line's end, so after the `Doer:`, with no change. `canonical_item()` moves no `Doer:`, and its own read-back
(`fields()`, which compares `parts`) compares `doer` too; a line whose `Doer:` stands out of its place keeps its
fault, and `fmt` reports it. Its move of a `Due:` that stands before the Context reads a tail that is ` Context:
…` alone, so on a line that also holds a `Doer:` it moves nothing, and the line keeps its fault.

**D7. The grammar.** *The open item line* gives `act` its own production, with `doer?` after `context`, and its
decided form too; `field-name` gains `"Doer:"`; `doer` reuses `repo` and *A person's name*'s `person`.

**D8. The release.** A minor, **v2.8**, the next after v2.7 (TD-067 and TD-068 are designed for it too; if a
release cuts without this build, its build tags the release it lands in). It changes what is read in one way: a
`Context:` (or a `Parts:`) now ends at a ` Doer:`, so a line written before v2.8 whose Context held those words
reads a shorter Context and fewer refs. No key moves: the key strips nothing new. Its verdicts change: such a line
is now faulted by `item_problem()` (its text or Context names a field), but `board_problems()` judges a line only
when it is added, so no board has a flag day. The writers now refuse inputs that hold `Doer:`, which v2.7 wrote.
A v2.7 reader reads a `Doer:` as part of the Context, so a consumer writes one only once every reader of its board
runs v2.8.

## Consumers

Both consumers vendor the release; neither writes a `Doer:` before every reader of the board it writes runs v2.8.
- **agent-cadence**: its vendor PR, and its `board_edit.py add` passing `--doer` through; an entry for it is
  filed there when the release is cut (ShiftLead's TD-1661 waits on that vendor PR, its Event
  *agent-cadence-doer*). Its wrapper's callers that put `Doer:` in a text, a context or a detail value meet D4's
  refusal: one that files an item from a title holding `Doer:` rephrases it (D4).
- **ShiftLead**: TD-1661 bumps its agent-cadence pin to that vendor PR; TD-1660 reads `item_record()`'s `doer`,
  routing on its `kind` and `name` and quoting its `text`.

## The SPEC text the build lands

**1. *The board*, after the `Parts:` paragraph**, add:

> **`Doer:`** (v2.8) — `Doer: <repo>.` or `Doer: team <team>.`, right after the Context (after a `Parts:`, where
> one stands there), ahead of the `Due:`, and only on an `act`: who should do the item's step, a repo (*The ledger*'s
> `<repo>`) or a team (a person's name, below, after the word `team`), each name kept as written and compared
> case-insensitively. A repo named `team` is `Doer: team.`, and a doer's repo never ends in `.` (`parse_doer()`, `BoardItem.doer`, `item_record()`'s
> `doer`: `{"kind": "repo" | "team", "name", "text"}`, `text` the value as written, or None for none or a value
> of neither form). It is read only in that place, on any kind, and never inside a reply's words; `item_problem()`
> faults it on any kind but `act`. The reader reads it as it reads `Parts:`, any spacing and an absent period
> included, which `item_problem()` faults. It is part of the item key, and no edit changes it: a step for another
> doer is another item.
> What resolving it means, and what a press on it does, are the consumer's. `item_line(doer=)` and
> `board.py add --doer` write it.

**2. *The board*, the `Context:` paragraph.** "A Context ends where the next field begins: ` Parts:`, ` Due:`, …"
becomes "… ` Parts:`, ` Doer:`, ` Due:`, …".

**3. *Edits*, *A new item*.** The signature gains `doer`; the line form becomes
`… Context: <context>.[ Parts: <ids>.][ Doer: <doer>.] Due: <due>.`; after the `parts` sentences add:

> An act's `doer` (v2.8) writes ` Doer: <doer>.` right after the Context, the value exactly as given, neither
> trimmed nor collapsed: `<repo>` (not ending in `.`) or `team <team>`, with one space and no other whitespace
> (*The board*, `Doer:`). It is refused on any kind but `act`, and for any other value.

**4. *Edits*, the writer's refusals.** "The writer refuses text, a context, an answer or a detail value that
carries a field name" is unchanged; the field names it counts now include `Doer:` (v2.8).

**5. *Edits*, *The form the writers write*.** The third bullet becomes "…, on a `decide` optionally
` Parts: <ids>.` (ids separated by `, `, each once), on an `act` optionally ` Doer: <doer>.`, and ` Due: <date>.` …".
After "Every edit rewrites one open item line and nothing else" nothing changes; under **due** add "(after a
`Doer:`, where one stands)".

**6. *The board writer*, the `add` bullet.** Before "The line's own refusals come first" (the end of the `--parts`
clause) add:

> with `--doer <value>` (v2.8), an act's doer (`item_line(doer=)`); `--doer` with `--decided` is refused.

**7. *Versions*, after the last v2.7 paragraph**, add:

> **v2.8 adds `Doer:`** (*The board*, *Edits*, *The board writer*): an act's doer, `parse_doer()`, `BoardItem.doer`,
> `item_record()`'s `doer`, `item_line(doer=)` and `board.py add --doer`. It reads one thing differently: a
> `Context:`, and a `Parts:`, now end at a ` Doer:`, so a line that held those words in its Context before v2.8
> reads a shorter Context and fewer refs. No key moves. `item_problem()` now faults such a line (its Context names
> a field), and a `Doer:` on any kind but `act`; `board_problems()` judges only a line it adds, so no board has a
> flag day. The writers now refuse a text, context, answer, detail value, reply or `--said` holding `Doer:`, which
> v2.7 wrote. v2.7 reads a `Doer:` as part of the Context, so a consumer writes one only once every reader of its
> board runs v2.8.

**8. *Appendix: grammar*, *The open item line*.** `other-item` loses `act`, and an `act-item` joins `item-line`'s
choices:

```ebnf
item-line      ::= "- [ ] " ( decide-item | look-item | fyi-item | act-item | other-item | decided-item )
act-item       ::= "act " date " " head " — " text context doer? due hide? reply*
other-item     ::= ( "watch" " " )? date " " head " — " text context due hide? reply*
doer           ::= " Doer: " ( repo | "team " person ) "."
```

`decided-item`'s second choice splits the same way (`"act " … context doer? due hide? reply* answers?`, then
`( ( "look" | "watch" ) " " )? …` as now), `field-name` gains `| "Doer:"`, and `person` is *A person's name*'s
production. Under the block: "A `Doer:` names a team only after the word `team` and one space; `Doer: team.` names
the repo `team`. A doer's repo does not end in `.`, so the period that ends the field is never the name's."

## Fixtures

All invented names (`acme/widgets`, `ops`, `web.grind`).

- **`fixtures/board/doer.md` and `doer.json`** (the reader): an `act` naming a repo (`Doer: acme/widgets.`) and one
  naming a team (`Doer: team ops.`), each record's `doer`; one whose Context names `TD-4` and `PR #7` before its
  `Doer:`, its `refs` those two alone; an `act` with a reply whose words hold `Doer: someone.` and no field, its
  `doer` null; a `decide` carrying `Doer: team ops.`, read (its record has it); an `act` with `Doer: two words.`,
  its `doer` null; an `act` with `Doer: team.`, read as the repo `team`; an `act` with `Doer: Team ops.`, null;
  an `act` with `Doer: acme..`, null (D1); `Doer:acme.`, `Doer: acme` before its `Due:` and `Doer: team  ops.`,
  each read (D3); a decided `act` carrying a `Doer:`, read.
- **`fixtures/edit/cases.json`**:
  - `compose`: `item_line(kind="act", doer="acme/widgets")` and `doer="team ops"` with their lines;
    `doer="team web.grind"`; `doer="team"`, the repo `team`, written `Doer: team.`; refused: a doer on `decide`,
    `look`, `watch`, `fyi` and no kind; `""`; `" team ops"`; `"team "`; `"team  ops"`; `"team a b"`; `"Team ops"`; `"../x"`; `"acme."`; a two-line value; a text, a context, an answer and a detail value holding
    `Doer:`;
  - `edits`: snooze, due, done, decide and reply on an `act` carrying a `Doer:` keep it and the key; `due` on a
    hand-written act with a `Doer:` and no `Due:` adds the `Due:` after the `Doer:`; a reply whose words hold
    `Doer:` is refused;
  - `item_problems`: a well-formed act with each form passes; `Doer:` on a `decide`; twice; `Doer: Team ops.`;
    `Doer: acme..`; no period; `Due:` before `Doer:`; `Doer:` in the text; a hand-written act with a `Doer:`, a
    `Hide until:` and no `Due:`, whose only faults are the missing `Due:` (the hide follows the `Doer:`); a
    decided `act` with a `Doer:`, which passes; `Doer:acme.` and `Doer: team  ops.` (spelling); a `Doer:` before
    the `Context:` (the text names a field); a `decide` with `Parts:` then `Doer:` (the kind's fault alone), and with
    `Doer:` then `Parts:` (the kind's and the order's);
  - `canonical_items`: a line whose `Doer:` follows its `Due:` is reported, not rewritten;
  - `subjects`: an add's head stops before `Context:` as before (a `Doer:` never reaches it).
- **`fixtures/board_writer/add_doer`** (`--doer team ops` on an act, the board after), **`add_doer_repo`**,
  **`add_doer_decide`** (refused, exit 1), **`add_doer_decided`** (`--decided`, refused).
- **`fixtures/grammar/cases.json`** and its `expected.json`: under the `item-line` start, a group for each
  production it now reaches anew, each with an accepting and a refusing fixture (`tests/test_grammar.py` holds a
  start's groups to exactly the productions it uses): `act-item` and `doer` accept each form and refuse
  `Doer: Team ops.`, `Doer: acme..`, `Doer:` with no value and a `Doer:` before the Context; `person` (now reached
  from `item-line`) accepts `web.grind` and refuses `web..grind`; `field-name` accepts `Doer:`.

**Unit tests** (`tests/`): every field-name set holds `Doer:` wherever it holds `Parts:` (one test over the module's
sets, so a later field cannot miss one).

## The builds

**B1** (one build, `Part of: TD-065`): D1–D8 with SPEC text 1–8, the fixtures and the unit test, landing together.
Location: `ledgerboard/__init__.py` (`CONTEXT_RE`, `PARTS_RE`, `FIELDS_RE`, `FIELD_NAME_RE`, `ANY_FIELD_RE`,
`WRITER_FIELD_RE`, `GATE_FIELD_RE`; a new `parse_doer()`; `BoardItem.doer`; `parse_board()`; `item_record()`;
`item_line()`; `item_problem()`, its `Due:` and `Hide until:` order rules among it; `edit_line()`'s read-back;
`canonical_item()`'s `fields()`), `ledgerboard/board.py` (`plan_add`, `add --doer`), `fixtures/run.py` (`compose`'s
accepted `item_line` arguments gain `doer`; the records it builds), `SPEC.md` (*The board*, *Edits*, *The board
writer*, *Versions*, *Appendix: grammar*), `fixtures/board/` (the new pair, and every existing record JSON, which
gains `"doer": null`: `basic`, `answers`, `hidden`, `people`, `lifts_parts`), `fixtures/board_writer/` (the new
cases, and `list/expected.json`'s records), `fixtures/edit/` and `fixtures/grammar/` (`cases.json` and
`expected.json`), `tests/`. Done when: the precheck is green and every fixture above passes, with SPEC text 1–8
landed in the same PR; the release restamps `fixtures/MANIFEST`.

Then a release (Paul's), agent-cadence's vendor PR (its `board_edit.py add --doer`), and ShiftLead's TD-1661 pin bump.

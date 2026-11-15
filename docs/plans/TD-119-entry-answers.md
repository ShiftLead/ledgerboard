# TD-119: the gate sweep offers the entry's own answers

**Status:** Draft 1, 2026-11-15 (session lb-designer). Class: **wide** (a vendored, published format: two new
entry sections the gate sweep reads, a new reader, a new `check()` flag the writer refuses on, which both
consumers vendor; cap 6 rounds, cadence.md §4.8). Rounds: running (the record:
[docs/reviews/TD-119.md](../reviews/TD-119.md)).

**Entry:** [TD-119](../ledger/TD-119.md). Asked for by ShiftLead's techlead (m-988ff211d5bb), from the gate sweep
ShiftLead ran onto this repo's board in PR #355.

## The problem

When an entry waits on a person (`decision (<p>)`) and no board item asks for it, the gate sweep files one: a
`decide` whose text is the entry's Ask and whose answers are always `Go | Not yet` (SPEC *The gate sweep*,
`SWEEP_DECISION_ANSWERS` in `_sweep_item()`). Many Asks ask something else. In #355, ShiftLead's TD-1879 asked
*one more round, or go ahead now?* and named Hold too; ShiftLead's TD-1404 asked for *Works* or *Not right: <what it
printed>*. Both items offered Go | Not yet, so the person could not press the answer the question asks for, and a
*Works* typed as a reply would not lift the gate, since only `Go` lifts an item with no `Lifts:`.

The sweep cannot know an entry's answers today because the format gives them no home: SPEC *Text a person reads*
says *An Ask carries no answers in this format; a ledger that keeps its own `Answers` (a repo's own field or
section) passes them*. ShiftLead already keeps one such section, on its TD-1845 (`**Answers:** Go (default) — the
grinders build it | One more round — … | Hold: <note> — …`), in the board's `Answers:` form. No ledger on this
machine's roster declares an `Ask` or `Answers` header field, and none writes a `**Lifts:**` section.

## What is already settled

- **The board's answers** (SPEC *The board*, the `Answers:` and `Lifts:` bullets): a `decide`'s answers are read by
  `parse_answers_value()` and each by `split_answer()` into label, consequence and the ` (default)` mark; a form
  (`Hold: <note>`) is filled by the answer; `Lifts:` names which answers lift, each by its whole label (a form by its offered label, `Hold: <note>`,
  whose fills then lift), and an item with no `Lifts:` lifts on `Go` alone (`_lifting()`); the two waiting-only answers, `Keep waiting` and `Not yet`, never lift.
  `item_file()` refuses, for a `decide`, fewer than two answers, two answers of one label, an answer that is a
  label then a bare `—` with no consequence (`a —`, by its read-back rule), a `Lifts:` that is empty, repeats a label, names a waiting-only answer or names a label not
  offered, two forms with one head and a form as the default; it takes the default as an index (`default=`), and
  refuses any ` (default)` mark written in an answer (the mark is the writer's). It takes a literal `|` in an
  answer and escapes it.
- **What an answer does** (`closes()`): a waiting-only answer closes the item and keeps the gate (the host writes
  `kept waiting`); a lifting answer on an item about this repo's own entry closes it and lifts the gate (an item about another
  repo's entry, `<repo>#TD-n`, stays open, and its lift goes through *an answer owing a lift*); any other answer is a work order and leaves the
  item open, `decided`, which still covers the gate, so the sweep does not ask again.
- **The entry's body** (SPEC *Ledger entries and their edits*): a body section is kept byte for byte by
  `canonical()`, so a new section name changes no canonical form and no item key. `_entry_ask()` reads the body's
  `**Ask:**` section alone, its words joined to one line, the literal `**Ask:**` stripped, the title when it is
  empty.
- **The sweep's consumers pass its item through:** ShiftLead's `gatesweep.py` and agent-cadence's
  `gate_sweep.py` both hand `answers`, `default` and `lifts` from `sweep()`'s item to the board writer unchanged,
  so neither needs code for the sweep to offer other answers.
- **Text a person reads** (v3.2): the package's own writers do not run the check; a consumer's writer of an Ask
  passes the entry's answers to it, read as a board `Answers:` value.

## The design

### D1. An entry's answers live in its own `**Answers:**` section, and its lifts in `**Lifts:**`

An entry that waits on a person may carry two body sections:

- `**Answers:** a | b | c` — the answers the person may give, in the board's `Answers:` value form (each
  `<label>` or `<label> — <consequence>`, one marked ` (default)` at most, a form `<head>: <words>` among them,
  `\|` for a literal bar).
- `**Lifts:** a | b` — which of them lift the gate, each an answer's whole label (a form by its offered label,
  `Hold: <note>`, so its fills lift). With no `**Lifts:**` section, `Go` lifts, as on the board.

Each section is found by its lead's name (`Answers`, `Lifts`, the colon optional, as every lead is matched), and
its value is its text with its own lead removed and its words joined to one line, `\|` kept for
`parse_answers_value()` to read; an empty value is an empty section, never the title. Only the body sections are
read: a header field named `Answers` or `Lifts` is a field like any other, read by nothing here. A
qualified lead (`**Answers (…):**`) is its own section, never these. They sit anywhere in the body before the Log;
the writer's `edit TD-n --section Answers --from FILE` writes them as it writes any section, and no new command or
flag is added.

**Options set aside.** *A header field* (`Answers:` in the header block): header values are the summary's
metadata, one line each, and the format already keeps the Ask, what the person reads, in the body; ShiftLead
writes the section. *Reading the Ask's prose* (bold words, *or*): a guess, and TD-1879's Ask names its options in
running prose; a sweep that guessed would lift on the wrong press. *Answers inside the Ask section*: the Ask's
first paragraph is its question sentence (*Text a person reads*), so a second home inside it would split one
section two ways. *Leaving `Go | Not yet` and teaching the person to type the answer*: a typed *Works* lifts
nothing, which is the bug.

### D2. One reader decides whether the answers can be offered

`entry_answers(entry_text)` (v3.N) reads one entry's two sections, in this order:

1. The entry is read as `canonical()` reads it; an entry it refuses is refused (`Refused`, its reason). Neither
   section: `None`. Two sections of one name (`**Answers:**` twice, or `**Lifts:**` twice): refused.
2. A `**Lifts:**` with no `**Answers:**`: refused. An empty `**Answers:**` value: refused, *no answers*.
3. The answers are `parse_answers_value()`'s, each split by `split_answer()`: more than one marked ` (default)`
   is refused; each is returned with its mark removed, as `<label>` or `<label> — <consequence>`, a bar in it a
   literal `|`; `default` is the marked one's index, else None.
4. The lifts are `parse_answers_value()` of the `**Lifts:**` value, as written (literal bars), else None.
5. `item_file("x", "2000-01-02", "2000-01-01", None, None, "<the entry's id> decision (p)", kind="decide",
   answers=…, default=…, lifts=…, detail={"context": "x", "question": "x?", "recommended": "x"})` is called
   with them (a Due and a detail block, since a `decide` needs both; the probe exists only for the answers',
   default's and lifts' rules, and no entry id makes its context refused): what it refuses is refused, with its
   reason. Its rules
   (*What is already settled*) are the authority; the list there is for the reader of this plan.
6. No answer lifts — no `**Lifts:**` and no answer whose label, whitespace-folded and compared
   case-insensitively, is `Go` (a form `Go: <note>` is not): refused. (A `**Lifts:**` step 5 passes always names an offered answer.)

Otherwise it returns `{"answers": [...], "default": <int or None>, "lifts": [...] or None}`. It reads no board and
no person: the same text gives the same result for the sweep, `check()` and a consumer's writer.

### D3. The sweep offers them

The `decision (<p>)` bullet of *The gate sweep* keeps its rule for *when* it files; it changes only *what*. For an
entry whose `entry_answers()` returns answers, the `decide` it files carries them: `answers`, `default` and
`lifts` from the reader, and a detail block whose `recommended` names what lifts — *Only <p> can say: <a>, <b>
lift the gate* (the lifting labels, or `Go`, in the answers' order, joined by commas), *and the other answers
leave it standing* (with a default, `item_file()` writes it after the default's label, `<label> — …`, as for
every item). For an entry with no answers (the reader returns `None`), and for one whose answers the
reader refuses, it files `Go | Not yet` as today; for the refused case its detail context gains *; its own answers
could not be offered (the ledger check names why)*. The sweep never raises for an entry's answers.

What the person's press then does is the board's rule, unchanged: a lifting answer lifts the gate (on this
repo's own entry by the decide lift, closing the item; on another repo's, through *an answer owing a lift*); `Not yet` or `Keep waiting`, where offered, closes it and keeps the gate; any other
answer (*One more round*, *Hold: <note>*, *Not right: <what it printed>*) is a work order the entry's session
acts on, and the item stays open and `decided`, covering the gate.

The item's identity, its filing rule and the `kept waiting` window are unchanged. An item already open is not
rewritten when an entry gains answers: the sweep files only uncovered gates. The sections apply to every
`decision (<p>)` on the entry, one set for all its people (answers per person are not this design). An entry
covered through its parent's item (`Parts:`) is asked by that item, whose answers are the parent's: its own
sections are offered only when the sweep files for it. The refused case's reason is the check's alone; the item
says only that the entry's answers could not be offered.

**A work-order answer.** With `Go | Not yet`, every press closed the item. A work-order answer (*One more round*,
*Hold: <note>*, *Not right: <what it printed>*) leaves it open and `decided`, as any work order on the board does,
and it covers the gate, so the sweep asks nothing while the entry's session acts. That session closes the item
when it has acted (`done`, as for any work order), and asks again itself where the work ends in a question (a
design's next end-of-rounds item, a check run again): once closed, the item's answer is one that does not lift,
dated within `reask_days`, so the sweep files no item of its own over the session's for that window. That window
is accepted: the session that acted knows when to ask, and the sweep is the backstop for a gate nobody asks
about.

### D4. The ledger check flags answers the sweep cannot offer

`check()` flags an open entry whose `Blocked by` names a `decision (<p>)` (as `parse_gates()` reads its
`decisions`) and whose `entry_answers()` raises (`answers-unusable`), with the reader's reason; an error on an
entry the edit changed (its whole text, as for the Log), ℹ on a standing ledger. It joins `EDIT_ERRORS` and
`TEXT_KINDS`, so it is scoped to an entry's whole text (an `edit --section Answers` changes the body alone) and
the ledger writer refuses an edit that makes one, as it refuses `ask-missing`. An entry with no decision gate is
not flagged, whatever its sections hold: nothing reads them, and a repo's own prose `**Answers:**` section,
which *Text a person reads* allowed before v3.N, stays legal there. The flag comes with the gate: an edit that adds
a decision to an entry whose sections cannot be offered is refused, naming why.

Since a `**Lifts:**` with no `**Answers:**` is refused, a writer adds `**Answers:**` first (or both in one
whole-entry write): `edit --section Lifts` on a gated entry with no `**Answers:**` is refused.

### D5. The answers are text a person reads

*Text a person reads*' Ask bullet now names the format's section: a consumer's writer of an entry's Ask, or of
its `**Answers:**` section, passes the entry's answers to the check (`entry_answers()`'s, else a repo's own
field), so rule 2 (*each answer names who acts*) holds for them at the writer, as for any board answer. The sweep
and the package's writers run no check (TD-111 D3).

### D6. The release

A minor release: the next unreleased minor when the build merges (v3.2 is TD-111's, built and untagged; TD-115's
build waits for v3.1's tag and takes the next untagged minor too). If another build's paragraph for that minor is
on main and untagged when this one merges, the two share one *Versions* paragraph, whose bold lead names every
addition, this build's sentences after the others'; if that minor is tagged, every `v3.N` this build writes
becomes the next untagged minor.

**What reads differently.** An entry that already carries an `**Answers:**` section gets its own answers on the
sweep's next item instead of `Go | Not yet` (ShiftLead's TD-1845 today, whose answers are usable: `Go` lifts). A
gated entry whose section is not usable gains a standing ℹ `answers-unusable`, and an edit of it is refused until
the section is fixed: the repo's own section, which v3.2 left to the repo, is the format's on a gated entry. No parse, field, Log line, item key or
canonical form changes.

**The consumers.** Neither needs code: both pass the sweep's item through. On the build's merge the builder tells
agent-cadence's techlead which release carries it; on Paul's go the designer sends ShiftLead's question seat one
note (`ao td add --repo shiftlead`): once the release is vendored, TD-1879 and TD-1404 (and any entry whose Ask
names its own answers) can carry `**Answers:**` and `**Lifts:**` sections. The two items #355 filed for them on this
repo's board, with `Go | Not yet`, stay as filed, since an open item is never rewritten, and nothing here
touches them: Paul may answer them as they stand. To re-ask one with its entry's own answers, ShiftLead's session,
once its sections land, closes it unanswered by a PR in this repo (`board_edit.py done --why "re-asked with the
entry's own answers"`), and the next sweep files it again (an item closed with no answer opens no window); the
note says so.

## The SPEC text

The build adds these, word for word, `v3.N` the release D6 names.

**In *The ledger*, after the paragraph ending *A `Waits` field is never read as a gate.*:**

> **An entry's own answers** (v3.N). An entry that waits on a person may name the answers it offers in a body
> section `**Answers:**`, in the form of a board `decide`'s `Answers:` value (*The board*: each `<label>` or
> `<label> — <consequence>`, one marked ` (default)` at most, forms among them), and which of them lift its gate
> in a body section `**Lifts:**`, each an answer's whole label (a form by its offered label, `Hold: <note>`); with
> no `**Lifts:**`, `Go` lifts. Each section's value is its text with its own lead removed, its words joined to
> one line; a header field of either name, and a qualified lead (`**Answers (…):**`), are not these.
> `entry_answers(entry_text)` reads them: None when the entry has neither section; `{"answers", "default",
> "lifts"}` when they can be offered (each answer with its ` (default)` mark removed and a literal `|`, the
> marked one's index or None, the `**Lifts:**` labels or None); and it raises `Refused`, naming why, for an
> entry `canonical()` refuses, two sections of one name, a `**Lifts:**` with no `**Answers:**`, an empty
> `**Answers:**`, two answers marked, answers `item_file()` refuses as a `decide`'s `answers`, `default` and
> `lifts` (fewer than two among them), and answers of which none lifts. `check()` flags an open entry whose
> `Blocked by` names a decision and which it refuses (`answers-unusable`; an error on an entry the edit changed — its whole text — ℹ on a standing ledger). The
> gate sweep offers them (*The gate sweep*).

**In *The gate sweep*, the `decision (<p>)` bullet:** *`Answers: Go | Not yet.`* becomes

> its answers the entry's own (*An entry's own answers*: `entry_answers()`'s `answers`, `default` and `lifts`),
> else `Answers: Go | Not yet.` (v3.N: also when the entry's answers are refused, its detail context then saying
> so), …

and the paragraph after the bullets gains, as its last sentence:

> An item the sweep filed is never rewritten: an entry that gains answers keeps the item already open.

**In *Text a person reads*, the Ask bullet:** *An Ask carries no answers in this format; a ledger that keeps its
own `Answers` (a repo's own field or section) passes them, read as a board's `Answers:` value
(`parse_answers_value()`);* becomes

> An entry's answers (*An entry's own answers*, v3.N) are passed with it, `entry_answers()`'s `answers`, else a
> repo's own `Answers` field, read as a board's `Answers:` value (`parse_answers_value()`); and a write of the
> entry's `**Answers:**` section is checked as a write of its Ask;

**In *Versions*, a paragraph for the release:**

> **v3.N gives an entry its own answers** (*The ledger*, *The gate sweep*): `**Answers:**` and `**Lifts:**`
> sections, `entry_answers()` that reads them, and `check()`'s `answers-unusable`, which the ledger writer
> refuses on an edit. The gate sweep's item for an uncovered decision offers the entry's answers where it has
> usable ones, and `Go | Not yet` otherwise. No parse, field, Log line, item key or canonical form changes; an
> entry that already holds an `**Answers:**` section is offered its own answers, and one whose section cannot be
> offered is flagged ℹ when it waits on a person. *Text a person reads*' allowance of a repo's own
> `**Answers:**` section is narrowed: on an entry with a decision gate, that section is now the format's.

## The fixtures

- **`fixtures/sweep/`**: a new key `answers` in `cases.json`, its own small ledger `sweep/answers/ledger.md` and a
  board `sweep/answers/board/` listing `People: pat`, so the existing runs' expected results do not move. Its
  entries, each `decision (pat)` and uncovered: one with no section (`Go | Not yet`, today's item); one with
  `Answers: Works — a session archives the check | Not right: <what it printed> — a session files what is wrong`
  and `Lifts: Works`; one with `Go (default) — … | One more round — … | Hold: <note> — …` and no `**Lifts:**`
  (`default` 0, `lifts` None); one whose `**Lifts:**` names a label not offered (refused: `Go | Not yet`, the
  detail context's added clause); one with no lifting answer (`One more round | Hold: <note>`, no `**Lifts:**`);
  one with `**Lifts:**` and no `**Answers:**`; one whose `**Lifts:**` names a form, `Hold: <note>`. The runner
  (`sweep_cases()`, which today reads `sweep/`'s top-level `ledger.md` and `archive.md`) gains the key's own
  ledger text and its v3 board directory, read apart from the existing runs; it calls `sweep()` over them on one date; the expected
  items are written from this SPEC text, never from the module's output.
- **`fixtures/ledger_edit/check/`**: `answers-unusable` as an error on an edited entry and ℹ on a standing one,
  and a usable section that flags nothing; an unusable section on an entry with no decision, not flagged; an edit
  adding a decision to such an entry, refused; `edit --section Lifts` with no `**Answers:**`, refused.
- **`entry_answers()`**: a block in `fixtures/sweep/cases.json` (`entry_answers`), each an entry text and its
  result or `{"error": "Refused"}`: the cases above, a `\|` inside an answer, a qualified `**Answers (old):**`
  lead (None), a header `Answers` field (None), a mark on the second answer (`default` 1), two marks (refused), a form marked
  ` (default)` (refused), one answer (refused), an empty `**Answers:**` (refused), two `**Answers:**` sections
  (refused), `Go: <note> | No` with no `**Lifts:**` (refused: no answer lifts), `go | Not yet` (`go` lifts), `Lifts: Hold` for an offered `Hold: <note>` (refused: a form is listed by its whole label), a section
  spanning two paragraphs (joined).

## Builds

One build, **B1**: `entry_answers()`, the sweep's use of it, `check()`'s `answers-unusable` in `EDIT_ERRORS` and `TEXT_KINDS`,
the SPEC text above, the fixtures and unit tests (the reader's refusals by reason; the sweep never raising on
an entry's answers), in one PR; the release number as D6 says. On its merge the builder tells agent-cadence's
techlead which release carries it.

## Not done

- **The item's text** stays the entry's whole Ask joined to one line, as today. Since v3.2 an Ask's first
  paragraph is its question and its later paragraphs context; filing only the first paragraph as the item's text
  and the rest as its detail context is a change of its own, not this one.
- **No rewrite of an open item** when its entry's answers change (D3).
- **No writer flags**: `edit --section Answers|Lifts` writes the sections; `new` and `set` gain nothing.

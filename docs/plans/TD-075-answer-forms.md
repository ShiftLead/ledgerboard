# TD-075: any offered `<head>:` or `<head>: <…>` answer is a form the person's words fill

**Status:** Draft 1, 2026-11-12 (session lb-designer). Class: **wide**: it changes a vendored, published format
that both consumers read (cadence.md §4.8; cap 6 rounds). Rounds: none yet.

**Entry:** [TD-075](../ledger/TD-075.md). **Source:** the entry's Why and Fix (ShiftLead's request, from its
TD-1557's *Handed upstream*); `SPEC.md` *The board* (the `Answers:` and `Lifts:` bullets), *Edits* (`decide`,
*A new item*), *Versions* and the grammar appendix; the module at `origin/main` (`ledgerboard/__init__.py`, cited
by function: `split_answer()`, `is_not_right_form()`, `fill_not_right()`, `_lifting()`, `closes()`,
`edit_line()`, `_answer_parts()`, `item_line()`, `decided_line()`, `item_problem()`, `decide_lift()`,
`_answered_within()`, `_answers_owing()`, `_sweep_closes()`, `uncovered_decisions()`); `ledgerboard/board.py`
(`_decide_ledger()`); [TD-070's plan](TD-070-board-directory.md) D12 and [TD-078's plan](TD-078-v3-ledger-half.md)
D3 (the last v2.x minor).

## The problem

A board item's offered answers are complete answers, with one exception: a `look`'s `Not right: <what>`, a
**form** whose slot is the person's words (*The board*, the `Answers:` bullet). Three things are wrong with how
far that reaches.

1. **Only the look's form is a form.** A design's end-of-rounds item offers `Hold: <note>`, and other items offer
   their own (`Other: <what>`). Nothing in the format says these take words, so a consumer presses `Hold: <note>`
   as written and the board records the placeholder: `Decided: Hold: <note> (…)`.
2. **No reader knows a filled form.** `_lifting(label, lifts)` compares the answer to each `Lifts:` label as
   text, whitespace collapsed, in any case. A filled `Hold: wait for the vendor` never equals `Hold: <note>`, so
   an item whose `Lifts:` lists a form is never lifted by a fill: not by `closes()`, `edit_line`'s `close`,
   `decide_lift()`, `board.py`'s `_decide_ledger()`, nor the readers that ask whether an answer lifted
   (`_answered_within()`, `_answers_owing()`, `_sweep_closes()`).
3. **Even the look's form is known only to helpers nothing calls.** `is_not_right_form()` and `fill_not_right()`
   are called by `fixtures/run.py` and the tests, never by a reader or writer in the module. Their head is
   matched case-sensitively, so `not right: <what>` is a complete answer.

ShiftLead's TD-1557 (its rounds ended) generalises the look's case, and its build TD-1698 cannot start until
this repo's format, module and fixtures know the general form, since ShiftLead reads the board only through
vendored ledgerboard.

## Decisions

**D1. What a form is.** An offered answer's **label** (after `split_answer()`: the consequence and the
` (default)` mark off), whitespace collapsed, is a **form** when it is a **head**, then any spaces, then `:`, then
nothing or one placeholder `<…>` (one space or more before it). The head is one or more characters, none of them
`:`, `<` or `>`, starting with neither a space nor a tab. So `Hold: <note>`, `Hold:`, `Other :  <what>` and
`Not right: <what>` are forms; `Not right: wrong repo`, `Hold: <a> <b>`, `A: b: <c>` and `Go` are not. A form's
head is compared **in any case, whitespace collapsed** (`form_head()`): `hold` and `HOLD` are one head. A complete
answer is everything else, as today.

*Why this shape.* It is the look's form with its head opened, which keeps every look line's reading and gives
ShiftLead what it asked for. A placeholder of one `<…>` is what every writer writes; two placeholders, or words
after the colon, make a complete answer, as `Not right: wrong repo` is today, so an existing complete answer never
becomes a form by accident. *Weighed:* a marker of its own (`Hold: …`, or `Hold: <note>*`) would be explicit but
would rewrite every look line and every design item already written; a form only where `Lifts:` lists it would
leave a work-order form (`Other: <what>`) unfillable.

**D2. How a form is filled.** An answer given to an item (**said**), whitespace collapsed, **fills** a form among
the item's offered answers when it is not itself one of the offered complete answers (compared as `_lifting()`
compares, in any case), and its text before its first `:`, trimmed, equals that form's head in any case. The
**words** are the text after that colon, trimmed. The fill is written as the **head as offered**, `:`, one space,
the words (`Hold: wait for the vendor` from `hold:wait for the vendor`). When the words are empty or are
themselves one placeholder, it is refused: *<head> needs its words* (the head as offered). When two offered forms
share a head (which D4 faults, but a line may already stand so), the first fills. A said that names no form's head
fills nothing and is the plain answer it is.

**D3. The API.** Three functions, pure, over labels as `parse_answers()` gives them:
- `is_form(label) -> bool` — D1.
- `form_head(label) -> str | None` — the form's head, whitespace collapsed and lower-cased; `None` for a complete
  answer.
- `fill_form(said, offered, form=None) -> str | None` — D2's fill of `said` among `offered` (labels; a raw answer
  with its consequence or mark is read through `split_answer()` first), or `None` when it fills no form. With
  `form` (an index into `offered`), that form alone is filled, and its head is put back when `said` does not start
  with it (`fill_form("the vendor", ["Go", "Hold: <note>"], form=1)` is `Hold: the vendor`). Refused (`Refused`):
  a `said` that is not a string; a `form` out of range or naming a complete answer; empty words (D2).

`is_not_right_form(answer)` and `fill_not_right(said, offered)` stay, as the look's case: `is_form()` with the head
`not right`, and `fill_form()` limited to an offered form of that head, so both now match the head in any case
(`not right: <what>` is a form). `fill_not_right()` keeps its refusal text, *Not right needs its words: say what is
off*, and still returns `None` when `said` names another head or none, or no `Not right` form is offered.
`NOT_RIGHT` and `NOT_RIGHT_FORM_RE` stay as names, the latter no longer used by the module (removing a public name
is a major's). *Weighed:* folding the two into `fill_form()` alone would be tidier, but they are public, and
ShiftLead's request keeps them.

**D4. What the writers refuse, and what the reader faults.** On a `decide`:
- **Two forms with one head** (D1's comparison) — a fill could not say which it fills. `item_line()` refuses it
  (*two answers are forms with one head, <head>: a fill could not say which*); `item_problem()` faults it on an
  open `decide`, so `board_problems()` flags it.
- **A form marked ` (default)`** — the default is the answer a press sends unchanged, and a form sent unchanged is
  its placeholder. `item_line()` refuses `default=` naming a form (*a form cannot be the default: pressing it sends
  no words*); `item_problem()` faults the mark on a form on an open `decide`.
- `decided_line()` (an item already decided, from a ledger entry's answers) writes no ` (default)` mark on a form:
  where `default` names one, the line is written without a mark, since the entry's answers are copied as they
  stand and the item is decided already.
- A `look`'s answers stay exactly `Works | Not right: <what>` (`Works` the only mark it may carry), so neither
  refusal can meet one. A closed item, and an open item of any kind but `decide`, is not faulted: what is already
  decided or closed is history.

`edit_line(…, "decide", answer=…)` (and through it `board.py decide` and both consumers' wrappers, which call
`plan_edit()`) writes a **fill** of a form among the item's offered answers as D2 writes it, and refuses an
answer that is one of the item's forms as offered, unfilled (*<head> needs its words*). Any other answer is
written as today. Its existing refusal of an answer ending in `(by …)` stands, a fill included.

**D5. How the reader reads a filled form.** An answer **lifts** (`_lifting()`) when it is one of the item's
`Lifts:` labels as today, **or** when it fills (D2) a form listed in `Lifts:`. A waiting-only answer still never
lifts. `_lifting()` is the one place every reader asks, so `closes()`, `edit_line`'s `close`, `decide_lift()`,
`_decide_ledger()`, `_answered_within()`, `_answers_owing()`, `_sweep_closes()` and `uncovered_decisions()` all
read a fill as its form with no change of their own; `uncovered_decisions()`'s check that some offered answer
lifts still meets the form itself, which equals its `Lifts:` label. A `Decided:` already written with an unfilled
form (`Decided: Hold: <note>`) reads as before: it equals its label. `Decided:` keeps its text as written, and the
item key, which strips `Decided:`, moves on no line.

**D6. The release.** A **minor**: no key moves, no line's form changes, and the canonical form is untouched. One
thing is read differently on lines already written: a `Decided:` that fills a form listed in its item's `Lifts:`
now lifts, where it read as a work order, so `closes()` and the gate sweep may close it or lift its gate. The
release notes say so, and each consumer checks its board before vendoring with one search, `Decided:` beside a
`Lifts:` naming a form (this repo's board carries no `Lifts:` field on 2026-11-12; the other boards are each
consumer's to search). The new faults (D4) are flagged on open `decide` items only, as v2.1 flagged a cycle no earlier
release named. The look's head read in any case makes `not right: …` a form where it was a complete answer.

It ships in the **last v2.x minor**, with TD-078's B1 and B2 (TD-078's D3, the same number rule: the first minor
not yet tagged when its build merges), since TD-070's D12 allows no v2.x release after TD-070's B1, and ShiftLead's
TD-1698 waits on it. So TD-070's B1, when filed, is also `Blocked by` this design's B1; whichever of TD-070's,
TD-078's and this design's build filings comes last writes it. If it misses that minor, it ships in v3.0 and
TD-1698 waits for v3.0.

**D7. The grammar.** Unchanged: a form is a `label` as the grammar has it, and which labels are forms is a reading
of one, as the consequence split is. The appendix's *What the productions leave to prose* gains a sentence
(text 5).

## The `SPEC.md` text

**Text 1, *The board*, the `Answers:` bullet.** From "A `look` carries exactly `Answers: Works | Not right:
<what>.`" to the bullet's end ("…one that adds nothing, or only a placeholder, is refused.") becomes:

> A `look` carries exactly `Answers: Works | Not right: <what>.`
> An offered answer whose label is a **form** (v2.8) takes the person's words: the label, whitespace collapsed, is
> a **head** (one or more characters, none of them `:`, `<` or `>`, not starting with whitespace), then any
> spaces, `:`, and nothing or one `<…>` placeholder (`is_form()`): `Hold: <note>`, `Other:` and the look's
> `Not right: <what>` are forms; `Not right: wrong repo` and `Hold: <a> <b>` are complete answers like any other.
> Heads compare in any case, whitespace collapsed (`form_head()`). An answer given to the item **fills** a form
> when it is none of the item's complete answers and its text before its first `:` is that form's head; the fill
> is the head as offered, `: `, and the words after the colon (`fill_form()`; the look's case
> `fill_not_right()`, and `is_not_right_form()` for its form). Words that are empty or only a placeholder are
> refused (*<head> needs its words*). Where two forms share a head, the first fills. A `decide` offers no two forms
> with one head and marks no form ` (default)` (*Edits*).

**Text 2, *The board*, the `Lifts:` bullet.** "An answer **lifts** when it is one of `Lifts:` (or `Go` when the
item has none), compared case-insensitively (v2.4)." becomes:

> An answer **lifts** when it is one of `Lifts:` (or `Go` when the item has none), compared case-insensitively
> (v2.4), or when it fills a form listed there (v2.8; *The `Answers:` bullet*), so a `Decided:` holding a fill of a
> listed form lifts and closes as its form would.

**Text 3, *Edits*, the `decide` bullet.** After "…a typed `Not right: …` included, which the reader would read as
who answered." insert:

> An answer that fills one of the item's forms is written as its fill, the head as offered (v2.8); one that is a
> form as offered, unfilled, is refused (*<head> needs its words*).

**Text 4, *Edits*, *A new item*, the `decide` line of *What a kind takes*.** "a `decide` carries two or more
distinct answers, at most one marked ` (default)`, and a detail block;" becomes:

> a `decide` carries two or more distinct answers, at most one marked ` (default)` and never a form (v2.8), no two
> forms with one head (v2.8), and a detail block; `decided_line()` writes no mark on a form, its `default` naming
> one written unmarked;

and after the paragraph's sentence on `item_problem()` faults (the `Lifts:` bullet's), *The board*'s faults gain:
"`item_problem()` faults, on an open `decide`, two forms with one head and a form marked ` (default)` (v2.8)."

**Text 5, the grammar appendix, *What the productions leave to prose*.** After its first sentence, insert:

> Which labels are forms (*The board*, the `Answers:` bullet) is a reading of a `label`, as its consequence split
> is: the productions accept every form and every fill as a label.

**Text 6, *Versions*, after the v2.8 title paragraph** (TD-078's text 4 writes two paragraphs there; this is a
third, true alone, placed after them when they stand):

> **v2.8 reads any `<head>:` or `<head>: <…>` answer as a form** (*The board*, the `Answers:` bullet): where only a
> look's `Not right: <what>` was one, now every such label is, its head in any case, and an answer that fills a
> form listed in `Lifts:` lifts. One thing is read differently on lines already written: a `Decided:` filling a
> form its item's `Lifts:` lists now lifts, so `closes()` and the gate sweep may close the item or lift its gate,
> where it read as a work order; and `not right: …` in lower case is the look's form. No key moves and the
> canonical form is unchanged. Two new faults, on open `decide` items only: two forms with one head, and a form
> marked ` (default)`. A board with no form in a `Lifts:` reads as before.

Where the texts say v2.8, the build writes the minor it ships in (D6).

## Fixtures

`fixtures/edit/cases.json` and `fixtures/run.py`'s `edit` group (one build, B1):
- `not_right_forms` gains nothing and changes one output: `not right: <what>` is now `true`. `not_right_fills`
  keeps its eight cases (their outputs unchanged) and gains `filled_lower_head` (`not right: grey`, filled as
  `Not right: grey`) and `other_head` (`Hold: x` among a look's answers: `None`).
- a new `forms` group: `is_form()` and `form_head()` over `Hold: <note>`, `Hold:`, `Other :  <what>`, `hold: <x>`,
  `Not right: wrong repo`, `Hold: <a> <b>`, `A: b: <c>`, `: <x>`, `<x>: <y>`, `Go`;
- a new `form_fills` group (`fill_form()`): `filled`, `head_any_case` (written with the head as offered),
  `space_before_colon`, `no_space_after_colon`, `empty_words`, `placeholder_words`, `form_as_offered`,
  `names_no_form` (`None`), `equals_complete_answer` (`Not right: wrong repo` offered whole: `None`),
  `first_of_two_heads`, `with_form_index` (the head put back), `with_form_index_head_present`,
  `form_index_out_of_range`, `form_index_complete_answer`, `said_not_a_string`, `offered_with_consequence`
  (`Hold: <note> — keep it unfiled` read through `split_answer()`);
- `lifting`: `closes()` and `edit_line(…, "decide", close=True)` on a `decide` whose `Lifts:` lists
  `Hold: <note>`: `fill_lifts` (closes, `Closed: … — lifted.`), `fill_of_unlisted_form` (a work order: refused with
  `close`), `unfilled_decided_reads_as_before` (an existing `Decided: Hold: <note>` line);
- `edit_line` decide: `decide_writes_fill` (`hold:  wait` written `Hold: wait`), `decide_refuses_unfilled_form`,
  `decide_complete_answer_unchanged`;
- `item_line()`: `two_forms_one_head_refused`, `form_default_refused`, `look_answers_unchanged`; `decided_line()`:
  `decided_default_on_form_unmarked`;
- `fixtures/board/` (the `board_problems()` cases): `two_forms_one_head_open` (faulted), `form_default_open`
  (faulted), `two_forms_one_head_closed` and `form_default_on_look_none` (not faulted);
- `fixtures/lift/`: `decide_lift_fill_lifts` — `decide_lift()` with a fill of a listed form lifts the gate as its
  form would; and `fixtures/sweep/`: `sweep_closes_filled_form`.

Every new case names its function and group in `fixtures/MANIFEST` as the existing ones do.

## The builds

One build, filed `Part of: TD-075`, with no `Kind`, on Paul's Go:

- **B1 — answer forms (D1–D6).** Location: `ledgerboard/__init__.py` (`is_form()`, `form_head()`, `fill_form()`;
  `is_not_right_form()` and `fill_not_right()` over them; `_lifting()`; `edit_line`'s `decide`; `_answer_parts()` or
  `item_line()` for the two refusals; `decided_line()`; `item_problem()`), `SPEC.md` (texts 1–6), `fixtures/edit/`,
  `fixtures/board/`, `fixtures/lift/`, `fixtures/sweep/`, `fixtures/run.py`, `fixtures/MANIFEST`,
  `tests/test_ledgerboard.py`. Done when the `SPEC.md` text lands with the code and fixtures and the precheck is
  green. Merges before TD-070's B1 (D6).

## Consumers

Lines for each consumer's own entry, filed there through its question seat (`ao td add --repo`), never here.

- **agent-cadence**: its vendor PR for the minor; its `board_edit.py` passes `decide` through `board.py`'s
  `plan_edit()`, so a fill is written and an unfilled form refused with no wrapper change. Before vendoring, it
  searches its board for a `Decided:` filling a form its `Lifts:` lists (D6).
- **ShiftLead**: its TD-1698 starts on the sync PR that carries the minor, calling `fill_form()` where TD-1557
  says, and runs D6's search on its board first.

## Not in this design

Forms on a `look` beyond `Not right: <what>` (its answers stay fixed). A waiting-only form (`Not yet: <why>`):
`Keep waiting` and `Not yet` stay complete answers. A form's words read by any reader beyond the fill (what a
`Hold:` note says is the person's). Removing `NOT_RIGHT_FORM_RE` (a major's).

# TD-075: any offered `<head>:` or `<head>: <…>` answer is a form the person's words fill

**Status:** Draft 5, 2026-11-12 (session lb-designer). Class: **wide**: it changes a vendored, published format
that both consumers read (cadence.md §4.8; cap 6 rounds). Rounds: three ran and the stop rule ended them (build-changing per design review 2, 1, 0; fact-checks 9, 0, 0);
round 3's six minor findings are applied and read by no design review; the closing fact-check follows.

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
nothing or one placeholder `<…>` (any spaces before it, none included, as `NOT_RIGHT_FORM_RE` reads the look's
form today). The head is one or more characters, none of them
`:`, `<` or `>`, starting with neither a space nor a tab. So `Hold: <note>`, `Hold:`, `Other :  <what>` and
`Not right: <what>` and `Hold:<note>` are forms; `Not right: wrong repo`, `Hold: <a> <b>`, `A: b: <c>` and `Go` are not. A form's
head is the text before its `:`, **trimmed** (so `Other :  <what>`'s head is `Other`), and compared **in any case,
whitespace collapsed** (`form_head()`): `hold` and `HOLD` are one head. A complete
answer is everything else, as today.

*Why this shape.* It is the look's form with its head opened, which keeps every look line's reading and gives
ShiftLead what it asked for. A placeholder of one `<…>` is what every writer writes; two placeholders, or words
after the colon, make a complete answer, as `Not right: wrong repo` is today, so an existing complete answer never
becomes a form by accident. *Weighed:* a marker of its own (`Hold: …`, or `Hold: <note>*`) would be explicit but
would rewrite every look line and every design item already written; a form only where `Lifts:` lists it would
leave a work-order form (`Other: <what>`) unfillable.

**D2. How a form is filled.** An answer given to an item (**said**), whitespace collapsed, **fills** a form among
the item's offered answers when it is not itself one of the offered complete answers (compared as `_lifting()`
compares, in any case; so `_lifting()` is given the offered answers, D5), and its text before its first `:`, trimmed, equals that form's head in any case. The
**words** are the text after that colon, trimmed. The fill is written as the **head as offered, trimmed**, `:`, one space,
the words (`Other: x` from `other :x` against `Other :  <what>`; `Hold: wait for the vendor` from `hold:wait for the vendor`). When the words are empty or are
themselves one placeholder, it is refused: *<head> needs its words* (the head as offered). When two offered forms
share a head (which D4 faults, but a line may already stand so), the first fills. A said that names no form's head
fills nothing and is the plain answer it is.

**D3. The API.** Three functions, pure, over labels as `parse_answers()` gives them:
- `is_form(label) -> bool` — D1.
- `form_head(label) -> str | None` — the form's head, trimmed, whitespace collapsed and lower-cased; `None` for a complete
  answer.
- `fill_form(said, offered, form=None) -> str | None` — D2's fill of `said` among `offered` (labels; a raw answer
  with its consequence or mark is read through `split_answer()` first), or `None` when it fills no form. With
  `form` (an index into `offered`, the caller's own choice of form), that form alone is filled and D2's exclusion of
  a complete answer does not apply: when `said` **has the head** (D2's reading: its text before its first `:`,
  trimmed, equals the form's head in any case), the words are the text after that colon; otherwise the whole `said`
  is the words and the head is put back (`fill_form("the vendor", ["Go", "Hold: <note>"], form=1)` is
  `Hold: the vendor`; `Holdfast` gives `Hold: Holdfast`, `Note: foo` gives `Hold: Note: foo`, and `Hold: later`
  over `Go | Hold: <note> | Hold: later` with `form=1` gives the fill `Hold: later`, whose text is that complete answer's, so a reader reads it as that
  answer, which lifts only by equality, D5: a caller choosing a form gets the complete answer when its words make
  one). Refused (`Refused`):
  a `said` that is not a string; a `form` out of range or naming a complete answer; empty words (D2).

`is_not_right_form(answer)` and `fill_not_right(said, offered)` stay, as the look's case: `is_form()` with the head
`not right`, and `fill_form()` limited to an offered form of that head, so both now match the head in any case
(`not right: <what>` is a form). `fill_not_right()` keeps its refusal text, *Not right needs its words: say what is
off*, and still returns `None` when `said` names another head or none, or no `Not right` form is offered.
One output changes: a fill is written with one space after the colon, so `fill_not_right("Not right:grey", …)`
returns `Not right: grey` where it returned `Not right:grey`; the eight existing `not_right_fills` cases all have
a space there and keep their outputs. `NOT_RIGHT` and `NOT_RIGHT_FORM_RE` stay as names, the latter no longer used by the module (removing a public name
is a major's). `fill_not_right()` keeps its lenient reading of `said` (`str(said or "")`, so a non-string or
`None` gives `None`), where `fill_form()` refuses a non-string. *Weighed:* folding the two into `fill_form()` alone would be tidier, but they are public, and
ShiftLead's request keeps them.

**D4. What the writers refuse, and what the reader faults.** On a `decide`:
- **Two forms with one head** (D1's comparison) — a fill could not say which it fills. `item_line()` refuses it
  (*two answers are forms with one head, <head>: a fill could not say which*); `item_problem()` faults it on an
  open `decide`, so `board_problems()` flags it.
- **A form marked ` (default)`** — the default is the answer a press sends unchanged, and a form sent unchanged is
  its placeholder. `item_line()` refuses `default=` naming a form (*a form cannot be the default: pressing it sends
  no words*); `item_problem()` faults the mark on a form on an open `decide`.
- `decided_line()` (an item already decided, from a ledger entry's answers) writes no ` (default)` mark on a form:
  where `default` names one, the line is written without a mark, so no writer writes a marked form (a decided
  line is not faulted, D4's last bullet, so this is the writer's rule alone, as ShiftLead asked). Its `words` are
  written as given, neither filled nor refused, as today: the caller, which has the person's words and the entry's
  answers, fills them first with `fill_form()`.
- **A form whose head is a field's name** (`Due: <x>`, `Lifts:`) is no `label`: `item_line()` refuses it as it
  refuses any answer holding a field's name (`_item_words()`), `decided_line()` strips the field's colon as it
  does today (`ANY_FIELD_RE`), and the reader reads such a line as it does today.
- A `look`'s answers stay exactly `Works | Not right: <what>` (`Works` the only mark it may carry), so neither
  refusal can meet one. Only an open `decide` with no `Decided:` is faulted, the branch of `item_problem()` that
  checks a `decide`'s answers today; a decided line (`- [ ] … Decided: …`, which takes `item_problem()`'s
  `decided` branch), a closed item, and an item of any other kind are not: what is decided or closed is history.
  `canonical_item()`, which runs `item_problem()` on the line it is given, refuses such a line too, so `board.py
  fmt` names the fault on an open undecided `decide` that holds it even where nobody edited it. That is deliberate:
  `fmt` is asked to make the line right, and the cure is the asker's (drop the mark, or give each form its own
  head); a board `fmt` is not run on reads as before.

**The answer is filled once, before anything is written.** `board.py`'s `plan_edit()` for `decide` fills a string
answer (`fill_form()` over the item's offered answers; a missing answer goes on to today's refusal) before it calls `_decide_ledger()` and `subject()`, so the
board's `Decided:`, the ledger's `gate lifted` Log line (`decide_lift()`, through `lift_gate(answer=)`) and the
commit subject all carry the same text; `lift_pr_verdict()`, which recomputes `decide_lift()` from the board's
`Decided:` and requires the ledger to match it, then agrees. It recomputes the board line through `edit_line(…,
"decide")`, so a PR whose head writes a `Decided:` holding an unfilled form, which the writers now refuse, goes to
review rather than passing; a standing `Decided:` of that shape that no PR touches reads as before (D5). `edit_line(…, "decide", answer=…)` fills the same way
for a caller of the module alone (a fill is filled once more unchanged). Both refuse an answer that is one of the
item's forms as offered, unfilled, or names a form's head with empty words (*<head> needs its words*). Any other
answer is written as today. `edit_line`'s existing refusal of an answer ending in `(by …)` stands, a fill
included. Both consumers' wrappers call `plan_edit()` (agent-cadence's `board_edit.py`, ShiftLead's sync), so
a caller that decides through `plan_edit()` with `--ledger` gains the fill with no change of its own. On the `--board-only` route the ledger was
written first, by `ledger.py set --answer` (`lift_gate(answer=)`, which knows no item): there the caller must pass
the same filled text (`fill_form()`) to the ledger's `set --answer` and to `decide --board-only --answer`, a new
duty that holds today only because a lifting answer is a bare label; `lift_pr_verdict()` flags a mismatch. The
Consumers lines name it.

**D5. How the reader reads a filled form.** `_lifting(label, lifts, offered)` gains the item's offered labels
(`parse_answers()`, or `BoardItem.answers`). An answer **lifts** when it is one of the item's `Lifts:` labels as
today, **or** when the form it fills (D2, among `offered`: where two forms share a head, the first) is listed in
`Lifts:`: an answer equal to one of the offered
complete answers is that answer and lifts only by equality (`Answers: Go | Hold: <note> | Hold: later. Lifts:
Hold: <note>.`: `Hold: later` does not lift). An answer naming a form's head with empty words or only a placeholder
fills nothing, and `_lifting()`, a reader, returns `False` for it rather than refusing. A waiting-only answer still
never lifts. `_lifting()` is the one place every reader asks (no caller compares an answer to `Lifts:` itself), so
each caller passes its item's answers and nothing else changes: `closes()`, `edit_line`'s `close`,
`decide_lift()`, `board.py`'s `_decide_ledger()` (line 503), `_answered_within()`, `_answers_owing()`,
`_sweep_closes()` and `uncovered_decisions()` read a fill as its form; `item_line()`'s check that some offered
answer lifts (`parts=`) passes its own offered labels too. `offered` has no default, so a caller that forgets it
fails at once; `uncovered_decisions()`'s check that some offered answer
lifts still meets the form itself, which equals its `Lifts:` label. A `Decided:` already written with an unfilled
form (`Decided: Hold: <note>`) reads as before: it equals its label. `Decided:` keeps its text as written, and the
item key, which strips `Decided:`, moves on no line.

**D6. The release.** A **minor**: no key moves, no line's form changes, and the canonical form is untouched. One
thing is read differently on lines already written: a `Decided:` that fills a form listed in its item's `Lifts:`
now lifts, where it read as a work order, so `closes()` and the gate sweep may close it or lift its gate. The
release notes say so, and each consumer checks its board before vendoring with one search, `Decided:` beside a
`Lifts:` naming a form (this repo's board carries no `Lifts:` field on 2026-11-12; the other boards are each
consumer's to search). The new faults (D4) are flagged on open `decide` items only, as v2.1 flagged a cycle no earlier
release named. The look's head read in any case, and with spaces before its colon, makes `not right: …` and `Not right : …`
forms where they were complete answers. The
writers' new refusals (D4) are listed in the release notes too: `decide` refuses an unfilled form, which it wrote
before, and `item_line()` refuses two forms with one head and a form as `default`.

It ships in the **last v2.x minor**, with TD-078's B1 and B2 (TD-078's D3's number rule, widened to three builds:
each writes the first minor not yet tagged when it merges, and the last of the three to merge rewrites the others'
number to its own where that is still untagged, so all three name one minor), since TD-070's D12 allows no v2.x release after TD-070's B1, and ShiftLead's
TD-1698 waits on it. So TD-070's B1, when filed, is also `Blocked by` this design's B1; whichever of TD-070's,
TD-078's and this design's build filings comes last writes it. If it misses that minor, it ships in v3.0 and
TD-1698 waits for v3.0. Three lines for this repo's own entries, written when their builds are filed: TD-078's B1 and B2 carry this
three-build number rule in place of their own two-build one (TD-078's D3); TD-070's B1's
`decision (paul)` Ask (TD-078's D3) names this design's B1 beside TD-078's B1 and B2 as the builds the last v2.x
minor holds; and TD-070's builds, which rework `BoardItem` and its readers, call `_lifting()` with its `offered`
argument (D5), since B1 here makes it required.

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

and in *The board*'s `Lifts:` bullet, after "…`item_line(lifts=)` refuses one and `item_problem()` faults one.",
insert: "`item_problem()` also faults, on an open `decide` with no `Decided:`, two forms with one head and a form
marked ` (default)` (v2.8; *The `Answers:` bullet*)."

**Text 5, the grammar appendix, *What the productions leave to prose*.** After its first sentence, insert:

> Which labels are forms (*The board*, the `Answers:` bullet) is a reading of a `label`, as its consequence split
> is: the productions accept every form as a label (a head that is a field's name makes no label: `item_line()`
> refuses it), and a fill is a `Decided:` text, which they accept as any.

**Text 6, *Versions*, after the v2.8 title paragraph** (TD-078's text 4 writes two paragraphs there; this is a
third, true alone, placed after them when they stand; where the minor is not v2.8 (D6), after the last v2.x
paragraph, its title the minor's):

> **v2.8 reads any `<head>:` or `<head>: <…>` answer as a form** (*The board*, the `Answers:` bullet): where only a
> look's `Not right: <what>` was one, now every such label is, its head in any case, and an answer that fills a
> form listed in `Lifts:` lifts. One thing is read differently on lines already written: a `Decided:` filling a
> form its item's `Lifts:` lists now lifts, so `closes()` and the gate sweep may close the item or lift its gate,
> where it read as a work order; and `not right: …` in lower case, or `Not right : …` with a space before its colon,
> is the look's form; and `fill_not_right()` writes one space after the colon (`Not right:grey` is returned
> `Not right: grey`), and a PR writing a `Decided:` that holds an unfilled form goes to review
> (`lift_pr_verdict()`). No key moves and the
> canonical form is unchanged. Two new faults, on open `decide` items with no `Decided:`: two forms with one head,
> and a form marked ` (default)`. The writers gain refusals: `decide` refuses a form unfilled (`Not right: <what>`
> included, which it wrote before) and writes a fill with the head as offered; `item_line()` refuses two forms
> with one head and `default` naming a form, and `fmt` (`canonical_item()`) names the two faults on such a line.
> A board with no form in a `Lifts:` reads as before. A consumer writes a fill only once every reader of its
> board runs v2.8: an older reader reads a fill as a work order and never lifts or closes it.

Where the texts say v2.8, the build writes the minor it ships in (D6).

## Fixtures

All in one build, B1, each group where its function's cases live today:
- `fixtures/edit/cases.json` (run by `fixtures/run.py`'s `edit` groups, outputs in `fixtures/edit/expected.json`):
  - `not_right_forms` changes one output, `not right: <what>` now `true`, and gains `Not right : <what>` (below). `not_right_fills`
    keeps its eight cases (their outputs unchanged) and gains `filled_lower_head` (`not right: grey`, filled as
    `Not right: grey`), `other_head` (`Hold: x` among a look's answers: `None`), `no_space_after_colon` (`Not right:grey` returned
    `Not right: grey`) and `said_none` (`None`: `None`, the
    lenient reading kept);
  - a new `forms` group: `is_form()` and `form_head()` over `Hold: <note>`, `Hold:`, `Hold:<note>`,
    `Other :  <what>`, `hold: <x>`, `Not right: wrong repo`, `Hold: <a> <b>`, `A: b: <c>`, `: <x>`, `<x>: <y>`, `Go`;
  - a new `form_fills` group (`fill_form()`): `filled`, `head_any_case` (written with the head as offered),
    `space_before_colon`, `no_space_after_colon`, `empty_words`, `placeholder_words`, `form_as_offered`,
    `names_no_form` (`None`), `equals_complete_answer` (`Not right: wrong repo` offered whole: `None`),
    `first_of_two_heads`, `with_form_index` (the head put back), `with_form_index_head_present`,
    `form_index_out_of_range`, `form_index_complete_answer`, `form_index_prefix_not_head` (`Holdfast`),
    `form_index_other_head` (`Note: foo`), `form_index_said_equals_complete` (`Hold: later`), `said_not_a_string`, `offered_with_consequence`
    (`Hold: <note> — keep it unfiled` read through `split_answer()`);
  - the `edits` group (`edit_line`): `decide_writes_fill` (`hold:  wait` written `Hold: wait`),
    `decide_refuses_unfilled_form`, `decide_refuses_empty_fill`, `decide_complete_answer_unchanged`;
  - the `compose` group (a list, `item_line()` and `decided_line()` cases in order): `item_line()`'s `two_forms_one_head_refused`, `form_default_refused`,
    `form_head_field_name_refused` (`Due: <x>`), `look_answers_unchanged`; `decided_line()`'s
    `decided_default_on_form_unmarked`;
  - the `item_problems` group (lines) and the `board_problems` group (old/new pairs), each holding:
    `two_forms_one_head_open` and `form_default_open` (faulted), `two_forms_one_head_decided` (a `- [ ] decide … Decided:` line, not faulted),
    `two_forms_one_head_closed` and `form_default_on_look` (not faulted);
- `fixtures/lift/cases.json`: in `closes`, `fill_lifts` (a `decide` whose `Lifts:` lists `Hold: <note>`, answered
  `Hold: the vendor`: closes), `fill_of_unlisted_form` (a work order), `complete_answer_sharing_head`
  (`Answers: Go | Hold: <note> | Hold: later. Lifts: Hold: <note>.`, answered `Hold: later`: does not lift),
  `unfilled_decided_reads_as_before`, `empty_fill_does_not_lift` (`Hold:` against a listed `Hold: <note>`),
  `shared_head_first_form` (`Answers: Hold: <a> | Hold:`, `Lifts:` naming the second: a fill does not lift),
  `waiting_form_fill` (`Not yet: the vendor` against an offered `Not yet: <why>` not in `Lifts:`: a work order);
  in `close`, `fill_lifts_closes` (`Closed: … — lifted.`) and
  `fill_of_unlisted_form_refused`; and a `decide_lift()` case, `decide_lift_fill_lifts`, the gate lifted as its
  form would be, the ledger's `gate lifted` line carrying the fill;
- `fixtures/board_writer/`: `decide_fill_ledger_matches` — `board.py decide --answer "hold:wait"` on a lifting
  item: the board's `Decided: Hold: wait`, the ledger's `gate lifted` line and the subject carry `Hold: wait`;
- `fixtures/verdict/cases.json`: `lift_unfilled_form_reviews` (a head writing `Decided: Hold: <note>`: to review);
  `lift_fill_matches` — a base and head tree where the head's board `Decided:` is
  a fill and its ledger's `gate lifted` line carries the same fill: `lift_pr_verdict()` passes;
- `fixtures/sweep/`: `sweep_closes_filled_form`, and cases for `_answered_within()` (a fill of a listed form counts
  as lifted) and `_answers_owing()`, which `sweep()` runs; and in `fixtures/verdict/cases.json`'s `uncovered`
  group, an `uncovered_decisions()` case (an item whose only lifting answer is a form);
- `fixtures/edit/`'s `forms`, `form_fills` and `not_right_forms` gain `Other :  <what>` (head `other`; `other :x`
  filled `Other: x`) and `Not right : <what>` (now a form); `edits` gains `decide_fill_with_dash_and_colon`
  (`Hold: revise — add log sources: the shapes` written and read back by `parse_decided()` unchanged; its
  `closes()` reading as a fill is a `fixtures/lift/` `closes` case), `decide_fill_ending_by_refused` (`Hold: ask (by kim)`), and
  `look_decided_fill` (`not right:grey` written `Not right: grey`; `Not right: <what>` refused); and a
  `canonical_item()` case per new fault (the line refused, naming it).

The new groups' outputs are new keys in their `expected.json`. `fixtures/MANIFEST` is not touched: `release.sh`
re-stamps it at the release. Case names above label the cases; in groups whose cases carry no `name`
(`item_problems`, `board_problems`, `compose`, `closes`) they are descriptions, not keys.

## The builds

One build, filed `Part of: TD-075`, with no `Kind`, on Paul's Go:

- **B1 — answer forms (D1–D6).** Location: `ledgerboard/__init__.py` (`is_form()`, `form_head()`, `fill_form()`;
  `is_not_right_form()` and `fill_not_right()` over them; `_lifting()`; `edit_line`'s `decide`; `_answer_parts()` or
  `item_line()` for the two refusals; `decided_line()`; `item_problem()`), `ledgerboard/board.py` (`plan_edit()`'s
  fill before `_decide_ledger()` and `subject()`; `_decide_ledger()`'s `_lifting()` call), `SPEC.md` (texts 1–6), `fixtures/edit/`,
  `fixtures/lift/`, `fixtures/board_writer/`, `fixtures/sweep/`, `fixtures/verdict/`, `fixtures/run.py`,
  `tests/test_ledgerboard.py`. Done when the `SPEC.md` text lands with the code and fixtures and the precheck is
  green. Merges before TD-070's B1 (D6).

## Consumers

Lines for each consumer's own entry, filed there through its question seat (`ao td add --repo`), never here.

- **agent-cadence**: its vendor PR for the minor; its `board_edit.py` passes `decide` through `board.py`'s
  `plan_edit()`, so a fill is written and an unfilled form refused with no wrapper change; where it decides
  `--board-only` after a ledger `set --answer`, it fills the answer first and passes the fill to both (D4). Before vendoring, it
  searches its board for a `Decided:` filling a form its `Lifts:` lists (D6).
- **ShiftLead**: its TD-1698 starts on the sync PR that carries the minor, after agent-cadence's vendor PR (a fill
  is written only once every reader of the board runs the minor, text 6), calling `fill_form()` where TD-1557
  says (and before both writes on a `--board-only` route, D4), and runs D6's search on its board first.

## Not in this design

Forms on a `look` beyond `Not right: <what>` (its answers stay fixed). A waiting-only form: `Keep waiting` and `Not yet` stay complete answers, waiting-only as
today; `Not yet: <why>` or `Keep waiting: <why>` offered is a form like any other (D1), and a fill of it is no
waiting-only answer (`waiting_only()` reads the bare label), so it neither keeps waiting nor lifts unless `Lifts:`
lists it; `item_line(lifts=)` accepts it there, as it accepts any label that is not waiting-only. A form's words read by any reader beyond the fill (what a
`Hold:` note says is the person's). Removing `NOT_RIGHT_FORM_RE` (a major's).

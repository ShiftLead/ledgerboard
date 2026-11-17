# TD-132: an answer a delegate makes for the person

**Status:** Draft 11 (rounds 1–8 applied, rounds 7 and 8 bought past the cap by the person's One more round; the ledger-only lift path redesigned after round 4; build-changing per design review, rounds 1–8: 7, 8, 2, 2, 2, 2, 1, 2; recurring topic the ledger-only lift after a delegated answer, which rounds 7 and 8 found holding on every case they tried; round 8's two build-changing findings fix which refusal or reason a fixture sees (where the writer runs the delegation test, and where the verdict's recompute takes its scope), not the mechanism; closing fact-check (R13) pending), 2026-11-17 (session lb-designer). Class: **wide** (a vendored, published format: a new
board preamble line, a new item field, a new `Decided` form and Log line form that every merge-gate verdict reads;
both consumers vendor it; cap 6 rounds, cadence.md §4.8). The record:
[docs/reviews/TD-132.md](../reviews/TD-132.md). In plain words: [docs/synopses/TD-132.md](../synopses/TD-132.md).

**Entry:** [TD-132](../ledger/TD-132.md), from ShiftLead's director seat (the person's conversation of
2026-11-16): a seat that answers some cards on the person's behalf.

## The problem

A board answer records who gave it: v3's `**Decided:** <date> by <person> — <label>` (SPEC *The board as a
directory*), v2's `Decided: <label> (by <person>) (<date>).`. Every check that trusts an answer compares that
`<person>` with the gate's person, or with `People:` under `Answered by: any`: the writer (`who_answered`,
`_may_answer` in `board.py`), the lift (`lift_gate`, `decide_lift`), the sweep's *answers owing* (`_answers_owing`),
and the merge gate's verdicts (`tripwire`, `lift_pr_verdict`, `ledger_lift_verdict`). A seat answering for the
person has two ways to write it, both wrong: `by <person>` records a decision the person did not make, so neither a
later review nor the person can tell theirs from the seat's; its own name is refused by every check. Putting the
seat on `People:` makes it a person, which it is not.

## What is already settled

- `People:` and `Answered by:` (v2.3, v2.4) say who may answer; a person's name is the person grammar (SPEC
  *Appendix*). A preamble line is read only above a v2 board's first item, anywhere in a v3 board's `README.md`,
  the first one winning; an older reader ignores a preamble line it does not know.
- A minor release reads every file its major's earlier releases wrote (SPEC *Versions*); a new form older
  readers do not read has been a minor before (`People:` v2.3, `Answered by:` v2.4, `Doer` v2.8).
- The module reads no file and knows no consumer: what a scope *means* (ShiftLead's merge line, its routine
  design go) is the consumer's; the package can only compare names.
- No v2 writer of `Decided:` is left (v3.0 removed `decided_line()`); v2 lines are read, and converted by
  `_v2_read()`, never written.

## The design

### D1. The record: `by <delegate> for <person> (<scope>)`

A delegated answer's v3 `Decided` value is

    <date> by <delegate> for <person> (<scope>) — <label>

`<delegate>` and `<person>` each a name in the person grammar, `<scope>` one name in the same grammar
(`merge-line`). Example: `**Decided:** 2026-11-20 by director for pat (merge-line) — Merge`. The person is the one
the answer counts as; the delegate is who wrote it; the scope is the authority it used. A value with `for` but no
`(<scope>)`, or a scope that is no name, is outside the form (`item_file_problem()`'s `decided` fault, as a bad
`by` is today). Every place that writes or re-renders the form takes the delegated one: `_item_values_problems()`'s
canonical re-render, `_item_dir_problems()`'s reader fault, `edit_item()`'s `put("Decided", …)` and its read-back,
`decided_file()` (which writes no delegated value: `add --decided` refuses a delegate, *Not done*), and `_item_read()`'s tuple, which gains the two fields so `edit_item()`'s and `decided_file()`'s read-backs
compare them; `ITEM_FIELDS` and `ITEM_FIELD_KEYS` gain `Scope` after `Doer`. `parse_decided_value(value)` keeps its `(label, date, by)` triple, `by` the **person**, and
`parse_decided_delegation(value)` (new) reads `(delegate, scope)` or None. So every reader that compares
`decided_by` with a gate's person — the lift, the sweep, every verdict — reads a delegated answer as the person's
unchanged, and only the delegation checks (D3, D4) read the delegate.

`BoardItem` gains `decided_delegate` and `decided_scope` (None for an undelegated answer; D5 lists every new key);
`decided_by` stays the person.

**The v2 line** is not extended: nothing writes it, so no v2 line holds a delegate. A v2 `(by director for pat
(merge-line))` is read as today, as label text with no `by` (`DECIDED_BY_RE` needs `(by <person>)` at the end); `_v2_read()` converts only what v2 reads.

**The Log line** a lift writes names the delegation the same way:
`gate lifted: decision (pat) — by director for pat (merge-line); answer "Merge"`, and `kept waiting: … — by
director for pat (merge-line); answer "Not yet"`. The optional ` for <person> (<scope>)` is added in place, after
the `by` group, to two of `LOG_SHAPES`' patterns only: the `gate-lifted` answer shape and the `kept-waiting` shape
(in place: no shape added or reordered, so the `gate-lifted` shapes' `via` index is unchanged). The regex's
existing `by` group keeps the name written after `by`; new named groups `person` and `scope` hold the `for` name and
the scope. After the match `log_line()` sets `delegate` to the `by` group and `by` to `person` when `person` matched;
else `by` stays and `delegate` and `scope` are None; the `person` key is dropped from the result. `log_line()` (and `log_lines()`)
return `by` as the **person** (the `for` name when present, else the `by` name, so `tripwire` and
`ledger_lift_verdict`, which read `rec["by"]`, compare the person as today) and `delegate` and `scope` beside it,
None for an undelegated line. An undelegated line reads as today.

### D2. Where delegations are declared: `Delegates:` beside `People:`

A board preamble line, read as `People:` is (only the first; above a v2 board's first item; anywhere in a v3
board's `README.md`):

    Delegates: director for pat (merge-line, design-go-routine); director for sam (merge-line)

**Reading.** The value is split at `;`; each piece, its surrounding whitespace dropped, is a grant
`<delegate> for <person> (<scope>, …)`: runs of whitespace inside it read as one space, the scopes split at `,`
and each stripped. An empty piece (a trailing `;`) is skipped. `board_delegates(content)` returns the grants as
written, a list of `(delegate, person, scopes)`, or None with no line; a piece outside the form is returned as
`(piece, None, None)`, so a reader sees it.

**Faults** (`delegates_problems(board, old=None)`; `board_problems(board, old)` judges `item_file_problem()` on new items only, so on a known item the writer's and the verdict's `delegate_problem()` are what refuse a delegated answer): a
grant outside the form (an empty `()` among them); a person not on `People:` (so a board with no `People:` line
holds no valid grant); a delegate who **is** on `People:` (a delegate is not a person); a delegate granted for
itself (reported alone for that grant: its person-off-`People:` and delegate-on-`People:` faults are not added); two grants of one delegate for one person; a scope named twice in a grant; a second `Delegates:` line
(the first is read). Names are compared case-insensitively, as people are. A fault is an **error** only when the
edit introduces it, its line differing from `old`'s (a new board, `old` None, counts as introducing it; so an
edit of the line that fixes one of two faults still meets the other as an error, and must fix both), and ℹ
otherwise, so a standing bad grant, or one left naming a person an edit removed from `People:`, never blocks the
board's other writes, the person's own answers and `done` among them.

**A faulty line grants nothing.** `delegation_covers(board, delegate, person, scope)` (new, the one function the
writer and every verdict call) returns True only when `delegates_problems()` finds no fault in the line and a grant
of that delegate, for that person, names that scope. So a line with one bad grant voids every delegated answer until it
is fixed; the person's own answers are unaffected. That reaches further than the fault: a person removed from
`People:` leaves their grants faulty and so voids every delegate's grant on the line, for every person, until the
line is fixed, and the only sign is the ℹ. This is chosen, not missed: a line is the person's whole statement of
authority, and one that no longer reads cleanly grants nothing rather than a part a reader would have to pick
out; the person's own answers still work. There is no wildcard scope; a board with no
`Delegates:` line accepts no delegated answer.

**Case.** `delegation_covers()` compares the delegate, the person and the scope case-insensitively; a written
`Decided`'s scope is the item's `Scope` byte for byte (rule 1).

**Spelling.** The writer writes the delegate as the grant spells it, the person as `People:` spells it (as
`who_answered()` does today) and the scope as the item's `Scope` spells it. `lift_pr_verdict()` resolves the head's
delegate to the base grant's spelling and its person to `People:`'s before it recomputes, so a head spelling
`Director` against a grant's `director` differs from the recompute (`lift-board-line`).

`delegates_changed(base, head)` (new, pure) returns whether the first `Delegates:` line's grants differ between
two boards, for a consumer's person-paths gate to test exactly (D4): each board's grants read as a set of
`(delegate, person, scope)` triples, names case-folded, a piece outside the form as its whitespace-folded text;
the sets compared. Reordering grants or scopes, or whitespace, is no change; a second line, which is not read, is
none either (`delegates_problems()` faults it).

### D3. What a scope covers: the item says, the grant allows

An item a delegate may answer carries a header field `**Scope:** <scope>`, one name, written by whoever raises the
item (`python3 -m ledgerboard.board add --scope merge-line`, agent-cadence's `board_edit.py` passing it;
`item_file(..., scope=)`), placed after `Doer` in the writers' order. `Scope` is a `decide` item's field only: on
any other kind it is a fault (`item_file_problem()`), as `Doer` is off an `act`. The item's raiser says what kind
of decision it is; the person's grant says which kinds the delegate may take. A delegated answer is accepted only
when **all** hold:

1. the item has a `Scope`, and the answer's scope equals it (in the writer this holds by construction, the scope
   being read from the item; a verdict and `item_file_problem()` test it on what was written);
2. `delegation_covers(board, delegate, person, scope)`;
3. the person may answer the item, by the rule that judges an undelegated answer of the same item: on an item
   whose Context names a `decision (<p>)` gate on this repo's entry, the gate's person, or any of `People:` on an
   `Answered by: any` board (`lift_gate()`, `decide_lift()`); on an `event (<name>)` gate, any of `People:`
   (`decide_lift()`'s rule); on an item with no gate, a name on `People:` (`who_answered()`);
4. the item's Context names no gate on **another repo's** entry: where the Context names a gate
   (`CONTEXT_ANY_GATE_RE`), no entry ref in it (every `REF_TD_RE` match, not only `_item_gate()`'s one ref, which
   is None when there are two) holds `#` (in `lift_pr_verdict()` a lone own-repo `#` ref meets this rule, `lift-delegate-uncovered`, before
   `lift-own-ref`, D4).
   In `delegate_problem()`, which returns the first rule that fails, rule 4 is judged before rule 5, so a `#` ref
   beside a second ref is reported as rule 4 (as an item fault it is already the existing `context` fault, a gated
   `decide` naming other than one entry): that repo lifts its own gate by its own tool PR,
   reading only its own board, so it could neither carry nor check the delegation. A delegated answer there is
   refused in this release (*Not done*);
5. where the item's Context names a gate (`CONTEXT_ANY_GATE_RE`), `_item_gate()` returns **one** entry ref and
   **one** gate, the decide lift's shape. Any other gated Context (two entries, two gates, a gate with no entry) is
   refused (`delegate_problem()`'s rule 5 message): the writer writes it board-only, so the gate it answers would
   stay carried with no ledger half and nothing in the delegate's name to lift it. A Context that names no gate is
   a gateless item whatever entries it names (a Context naming no gate passes rule 5; one with `Parts:` or
   `Lifts:` and not exactly one entry already meets the existing `context` fault): it carries nothing and owes no lift, so rule 5 does not apply. Of rule 5's cases,
   `item_file_problem()` and `item_file()` already refuse a gated `decide` naming other than one entry; only two
   gates is new at the item level.

A delegate may give any of the item's answers, a waiting-only one included: its `Not yet` closes the item and
keeps the gate waiting, as the person's would (the re-ask window then runs as for the person's answer). A grant is
for a kind of decision, not for some of its answers.

`item_file_problem()` also faults a delegated `Decided` whose scope differs from the item's `Scope`, one on an
item with no `Scope`, one whose delegate equals its person, one on an item whose Context names a gate on
another repo's entry (rule 4), and one on an item whose gated Context is not one entry and one gate (rule 5), as
every item fault is judged; these four read the item's text alone (rules 2 and 3 need the board's preamble and
are the writer's and the verdict's).

**Re-asks.** The package carries no `Scope` onto a later item: an item the sweep files (`Go | Not yet`, or the
entry's own answers) has none, so only the person answers it; a consumer that re-asks with a scope writes it.

**A known limit.** The package compares names; it cannot tell who raised an item (`Session` is not an identity).
A delegate that may raise items through a consumer's board-write carve-out could raise one, scope it, and answer
it; and one that leaves out `--delegate` writes `by <person>`, which no check can tell from the person's own. So the scope's honesty rests on the consumer: its board-write carve-out must not let a delegate's own PR add
an item with a `Scope`, or its review must read scopes, and must take a delegate's answer only in the
delegated form. agent-cadence's and ShiftLead's entries say so.

### D4. Who checks what

- **The board writer**: `delegate_problem(board, item, delegate, person)` (new, pure; the one D3 test the
  writer and `lift_pr_verdict()` share) returns the first rule that fails, in D3's order, as its fixed message,
  or None. The messages, which the writer's refusal and `lift-delegate-uncovered` both carry and the fixtures
  test: `rule 1: the item has no Scope`; `rule 2: no faultless Delegates: grant covers <delegate> for <person>
  (<scope>)`; `rule 3: <person> may not answer this item`; `rule 4: the Context names a gate on another repo's
  entry`; `rule 5: the gated Context is not one entry and one gate`, each `<…>` as the answer writes it, `<scope>` the
  item's `Scope`. It tests rule 1 only as
  *the item has a `Scope`*: the answer's scope equalling it is the recompute's (`lift-board-line`) and
  `item_file_problem()`'s. `plan_edit()`
  calls it immediately after `who_answered()` resolves the person and before `edit_item()` and
  `_decide_ledger()` (whose `_may_answer()` and `decide_lift()` refusals would otherwise come first), so its
  message is the refusal for rules 1 to 5; `edit_item(..., "decide", by=, delegate=)` (`by` the person) needs only
  the item's own text, the scope read from its `Scope`, and keeps its own refusal for a missing `Scope` only for a
  direct caller. With `--board-only` (the `set by=` route, its ledger already
  lifted `by <person>`) `--delegate` is refused; so is a delegate on `add --decided`. The CLI
  (`python3 -m ledgerboard.board decide --by pat --delegate director`, `add --scope merge-line`; `TAKES`,
  `NEEDS_OPT` and the parser gain both). It writes the D1 form and refuses a delegated answer D3 does not cover,
  naming which rule fails. `item_file(..., scope=)` and its read-back gain the field.
- **The lift**: `lift_gate()` and `decide_lift()` gain `delegate=` and `scope=`, used only to write D1's Log form;
  every comparison they make is of `by`, the person, as today. `lift_gate()` refuses a delegate on its override,
  check and date shapes (only an answer is delegated) and on the `board <repo>` suffix (rule 4), a delegate outside
  the person grammar, one equal to `by`, and a delegate without a scope or a scope without a delegate;
  `decide_lift()` applies the same refusals to the `kept waiting` line it writes itself. `ledger.py`'s `set` lift route gains `--delegate` and `--scope`, passed through to `lift_gate()` with no
  item check (its PR is reviewed, below). They are taken only with `--by` and `--answer` on a lift: with an
  override, a reassign, or a `Blocked by` that drops no decision they are `Unusable` (`_gate_route()`), and so is
  one without the other.
- **`lift_pr_verdict()`** (a board answer's lift on this repo's entry) recomputes the answer with
  `edit_item(..., by=, delegate=)` and `decide_lift(..., delegate=, scope=)`, so a delegated answer reproduces
  byte for byte. Its order: right after its `by` and date checks, before the ledger recompute, it requires
  `delegate_problem()` over the **base** board and the base item to return None; else `lift-delegate-uncovered`,
  naming the rule. The recompute takes `delegate` from the head's `Decided`, resolved to the base grant's
  spelling, and `scope` from the base item's `Scope`, never from the head; the ledger is recomputed before the
  board. So a PR whose Log line or `Decided` carries another scope is `lift-ledger`, and one that changes only the
  item's `Scope`, its answer and ledger half the base item's, is `lift-board-line`; one that also changes
  `README.md` (a grant added or changed) is `lift-board-diff` (`_one_items_change()`), before any D3 test. So a PR
  can neither grant nor rescope what it uses. A gateless delegated answer goes to review as every gateless answer
  does (`lift-no-gate`); one on another repo's entry is `lift-delegate-uncovered` (rule 4). The verdict's own
  order decides what a malformed Context meets first: any gated Context that is not one entry and one gate (two
  refs, a `#` ref beside a second among them, two gates, a gate with no entry) leaves `_item_gate()` no single ref
  or gate, so it is `lift-no-gate` before any D3 test, and the verdict never meets rule 5; a lone `#` ref naming this repo is `lift-delegate-uncovered`
  (rule 4), the delegate test running before `lift-own-ref`. Both go to review; *rule 4 before rule 5* is
  `delegate_problem()`'s order, not the verdict's.
- **A delegated answer carries its own ledger half.** The writer writes a delegated answer only by the
  decide-lift route, which writes the ledger in the same PR (`plan_edit()`'s `_decide_ledger()`): a lifting answer
  lifts the gate, a waiting-only one writes its `kept waiting` line, both in D1's delegated Log form; `--board-only`
  refuses a delegate (above). Where the item's gate is carried, `lift_pr_verdict()` passes a delegated answer only
  with that ledger half, as it recomputes it. So no delegated answer is ever left owing a lift, and nothing after its PR lifts its gate in its
  name. A work-order answer (*One more round*, *Hold: <note>*) leaves the item open and decided; on a decision gate
  `decide_lift()` writes a delegated `kept waiting` line for it, on an event gate no line. A delegated lifting
  answer on a gate its entry no longer carries writes no ledger line (`decide_lift()` returns nothing) and owes
  nothing.
- **`ledger_lift_verdict()`**, the ledger-only lift (ShiftLead's *Lift the hold*): it carves out no delegation. A Log
  line in the delegated form is `ledger-lift-delegated`, judged in step 5 once `ledger-lift-log` has found the one
  new `gate lifted … answer` line and before its date is parsed and `ledger-lift-by` is judged; and any open
  covering item whose `Decided` is delegated is `ledger-lift-delegated`. That second test is the verdict's own scan,
  not `lift_form()`'s, whose return names only the winning case's items and stays as SPEC documents it: right after
  `ledger-lift-asked` and before the bytes are recomputed, the verdict reads
  `covers(btext, gate, [_tree_board(base_tree, repo)], repo)` (the base entry's text, and the board as the
  sweep's `(origin_url, basename, Board)` triple, not the verdict's `b_board`), keeps the `COVERING` states, and returns `ledger-lift-delegated`
  if any such item's `Decided` carries a delegate, whichever case `lift_form()` chose. Open items are always in the verdict's tree, so it
  needs no archive: a closed delegated answer's gate was lifted, or kept waiting, in its own PR. The person's own
  lift with no item is judged as today, `by` the person, and is true: the person pressed it. A delegated ledger
  lift is written with `ledger.py set … --by pat --delegate director --scope merge-line` and reviewed.
- **A known gap.** A delegated lifting answer merged by review **without** its ledger half (a PR the writer cannot
  make, which `lift_pr_verdict()` refuses and a reviewer passed) leaves its gate; a later ledger lift `by <person>`
  with no open item is then carved out, the delegate unnamed. The writer and the verdict make it unreachable on
  the ordinary route; a review that merges such a PR owns the miss. The sweep narrows it (below).
- **`tripwire()`** compares `(decided, decided_by, decided_delegate, decided_scope)` where it compares
  `(decided, decided_by)` today, so a change of the delegate alone is seen as a change of the answer; it gains no
  flag of its own.
- **The sweep**: `_answers_owing()` (which serves this repo's entries named on its own board, a bare `TD-n`, and
  named as `<this repo>#TD-n` on other boards) reads a delegated answer as it reads any: on the ordinary route it
  owes nothing, its gate lifted in its own PR; where the gate is still carried (the gap above), it files the owed
  lift as for any answer. Where any answer in the group is delegated, the act's wording follows the newest
  delegated answer, not `last`; with none it is today's, byte for byte. The exact strings are the SPEC text's
  (*The gate sweep*, below). The group's owed ids are a union over its answers, so an undelegated `last` does not
  speak for an entry only an older delegated answer owes: there the delegated wording is the safe one, since its
  `set` is reviewed, where an override would record the person's own lift on an entry they did not answer. On an
  entry the person's newer answer owes too, it errs the other way, naming the delegate where the person also
  answered; that is chosen, since the review of the `set` sees both answers, and an override is never reviewed. So the
  session writes the Log line in the delegated form, which goes to review. Elsewhere the sweep reads
  `decided_by`, the person, as today: a delegated answer covers its gate and opens the `kept waiting` window as the
  person's would.
- **A change to `Delegates:`** never passes a lift carve-out (`lift-board-diff`, above). Who may change it is the
  consumer's person-paths gate, over the whole `README.md` (`People:` included, since a grant is live only while its
person is on `People:`; agent-cadence lists the board's `README.md` as the person's path, testing the line
  exactly with `delegates_changed()`; its entry). The package does not decide who the person is.
- **A standing board** (`board_problems()` with no `old`, which judges open items): an open item whose delegated
  answer the current `Delegates:` no longer covers is ℹ (a grant withdrawn later does not unmake a past answer),
  never an error. Archived items are not judged, as today. An item whose answer was given under a grant since
  withdrawn, still open because its lift has not merged, is lifted as answered: the verdict judged the grant at
  the answer's base.

### D5. Surfaces that hard-code the preamble

`delegates_problems()` scans for a second line as `people_problems()` and `answered_by_problems()` do.
`SPLIT_PREAMBLE_LINE_RE` (`People|Answered by|Ledgerboard`) gains `Delegates`, so `_split_text()` refuses it below
the first item as it does the others, and `_split_check()`'s equality check compares `board_delegates()` of the
old and new boards beside `board_people()` and `answered_by()`. `_split_readme()` carries every preamble line whole
and needs no change. SPEC's sentence naming the lines a split refuses below an item (*The board as a directory*,
the split's bullet: "`People:`, `Answered by:` or `Ledgerboard:`") gains `Delegates:`.

**What the package returns.** `BoardItem` gains `scope`, `decided_delegate` and `decided_scope` (None when
absent); `item_record()`, the JSON shape the fixtures and `_split_check()` compare, gains the keys `scope`,
`decided_delegate` and `decided_scope`. A consumer that shows who answered shows the delegate from these; the
package itself shows nothing.

### D6. The release

A minor, **v3.4**: v3.3 is released (#414), so this build writes its own *Versions* paragraph headed v3.4; if
v3.4 is taken before it merges, every `v3.4` it writes becomes the next untagged minor. New forms only: every file an earlier v3 wrote reads
the same. An older reader meets a delegated `Decided` as outside the form (the item then reads as undecided and
returns to the person's queue) and an older `log_problems()` faults the new Log form, so **no delegate writes one
until every repo that reads the board has vendored v3.4**: the board's own repo, and every repo whose vendored copy
reads it (ShiftLead's home and sweep, agent-cadence's attention report). Likewise no item carries `Scope` before
then (an older `item_file_problem()` faults an unknown field). Order: this repo's build and release;
agent-cadence's vendor PR (its `board_edit.py` passes `--delegate`, `--scope`; its person-paths gate lists the
board's `README.md` and tests the line with `delegates_changed()`; its board-write carve-out lets no delegate's PR
add a `Scope`); ShiftLead's vendor PR, then the director seat writes delegated answers and the person writes the
`Delegates:` line for each board it answers.

## The SPEC text

**In *The board*, after `Answered by:`:**

> **`Delegates:`** (v3.4) — `Delegates: <delegate> for <person> (<scope>, …); …`, a preamble line read as
> `People:` is, granting a delegate the authority to answer for a person on the board's `People:`, on `decide`
> items whose `Scope` the grant names. The value splits at `;`, each grant's whitespace dropped at its ends and
> folded to one space inside, its scopes split at `,`; an empty piece is skipped. Each name is a person's name in
> grammar, compared case-insensitively. `board_delegates(content)` returns the grants as written,
> `(delegate, person, scopes)` each, a piece outside the form as `(piece, None, None)`, or None with no line.
> `delegates_problems(board)` names a grant outside the form, a person not on `People:`, a delegate on `People:`,
> a delegate granted for itself, two grants of one delegate for one person, a scope named twice in a grant, and a
> second line. A line with any such fault grants nothing: `delegation_covers(board, delegate, person, scope)` is
> true only on a faultless line holding that grant. No wildcard: a board with no line accepts no delegated answer.
> `delegates_changed(base, head)` says whether two boards' grants differ. A delegated answer counts as its
> person's for every purpose: it lifts the gate or keeps it waiting, closes the item and covers the gate as the
> person's answer would. A delegate may not answer an item whose Context names a gate on another repo's entry.

**In *The board as a directory*, the header fields, after `Doer`:**

> - `Scope` — on a `decide` only: one name, the kind of decision the item is, written by whoever raises it; a
>   delegate may answer the item only under a grant naming it (*`Delegates:`*).

**The `Decided` bullet gains:**

> or, answered by a delegate, `<date> by <delegate> for <person> (<scope>) — <label>` (v3.4):
> `parse_decided_value()` returns the person as `by`, and `parse_decided_delegation(value)` the
> `(delegate, scope)`, None for an undelegated value. `item_file_problem()` faults a delegated value on an item
> with no `Scope`, with a scope other than the item's, whose delegate is its person, on a gate on another
> repo's entry, or on a gated Context that is not one entry and one gate. `item_record()` gains
> `scope`, `decided_delegate` and `decided_scope`.

**In *Edits*, the decide bullet gains:**

> With `delegate`, it writes the delegated form, the delegate as the grant spells it, the person as `People:`
> does, the scope as the item's `Scope` does, and refuses an answer `delegation_covers()` does not allow, on an
> item with no `Scope`, by a person who may not answer the item, on a gate on another repo's entry, or on an item
> whose Context names a gate but not exactly one entry and one gate; a Context that names no gate is not refused
> for the entries it names. The refusal is `delegate_problem()`'s message, one fixed text per rule.

**In *The merge gate's verdicts*, a paragraph:**

> A `Decided` written in the PR by a delegate passes `lift_pr_verdict()` only when `delegate_problem()` finds no
> fault over the **base** board and item (a grant covering the item's `Scope`, a person who may answer it as an
> undelegated answer is judged, a gate on this repo's entry), tested right after the answerer and date checks;
> else `lift-delegate-uncovered`, its text `delegate_problem()`'s message. A gated Context that is not one entry and
> one gate never reaches that test: it is `lift-no-gate`, as for any answer, so rule 5 is the writer's and
> `item_file_problem()`'s. A PR that also changes the item's
> `Scope` is `lift-board-line`, one that also changes `README.md` `lift-board-diff`, as for any lift PR.
> A delegated answer is written only with its ledger half, in the same PR (the decide lift). `ledger_lift_verdict()`
> carves out no delegation: a delegated Log line (judged once the one new `gate lifted … answer` line is found,
> before its date is read), or any open covering
> item whose `Decided` is delegated (every item `covers()` names in an open or decided state, judged right after
> `ledger-lift-asked`, whichever form `lift_form()` chose), is `ledger-lift-delegated`, so that lift goes to review.
> The sweep's *answers owing* files an owed lift of a delegated answer only where its gate is still carried; where
> an answer in the group is delegated, its act names the delegate and scope and recommends the delegated `set`,
> never an override (*The gate sweep*).

**In *The gate sweep*, after the *answers owing* act's sentence:**

> Where any answer in the group is delegated, the act follows the newest delegated answer `d` (ties broken by the
> pick key, as `last` is) instead of `last`, its delegate, person and scope as `d`'s `Decided` writes them: its
> `text` is today's with ` by <delegate> for <person> (<scope>)` after `answered with a lift` and `d`'s date in
> place of the newest, its
> `detail.context` the same, and its `detail.recommended` exactly
> `Lift it with ledger.py set --blocked-by … --by <person> --delegate <delegate> --scope <scope> --answer "<answer>"; that PR goes to review. Not an override, which would record the person's own lift; to ask again instead, close this and add the question`,
> `<answer>` being `d`'s label. With no delegated answer in the group the act is today's, byte for byte. Its board
> and ids are today's (from `last` and the group). The longer `text` is the package's; a consumer's rules for
> text a person reads apply where it shows it.

**In *The ledger*, the Log shapes:** the `gate-lifted` answer shape and the `kept-waiting` shape read
`by <name>[ for <name> (<name>)]`: with ` for`, the first name is the delegate, the second the person, the third
the scope; `log_line()` returns `by` as the person, with `delegate` and `scope`, None for an undelegated line.

**In *Versions*, after the newest:** **v3.4 adds delegated answers** (TD-132): the `Delegates:` preamble line, the
`decide` item's `Scope` field, the delegated `Decided` form and Log `by` form, `board_delegates()`,
`delegates_problems()`, `delegation_covers()`, `delegates_changed()`, `parse_decided_delegation()`, the writer's
`delegate` and `scope`, `delegate_problem()`, `ledger.py set`'s `--delegate` and `--scope`, and the verdicts' `lift-delegate-uncovered` and `ledger-lift-delegated`. Every file an earlier v3 wrote reads the same; an earlier reader reads a delegated
`Decided` as outside the form, so no delegate writes one until every repo that reads the board has this release.

**Appendix: grammar:** `decided-field ::= "**Decided:** " date ( " by " person ( " for " person " (" person ")" )? )? " — " item-text`;
`delegates-line ::= "Delegates: " grant ( "; " grant )*`, `grant ::= person " for " person " (" person ( ", " person )* ")"`
(the canonical spelling; the reader's tolerance is the prose above); `item-header` gains
`scope-field ::= "**Scope:** " person`, after `doer-field`, on a `decide` only. Each new production gets its
`fixtures/grammar/` case.

## The fixtures

All invented. `fixtures/board/`: a README with `Delegates:` read (`delegates.json`), with spaces and a trailing
`;`; each `delegates_problems` fault (outside the form, an empty `()`, a person off `People:`, no `People:` line, a
delegate on `People:`, a delegate for itself, a repeated grant, a repeated scope, a second line);
`delegation_covers` false on a line with one bad grant; `delegates_changed` true and false. `fixtures/item/`: a
delegated `Decided` read (`item_record`'s `by` the person, `decided_delegate`, `decided_scope`), one missing its
scope (outside), a `Scope` field read, `Scope` on an `act` faulted, a delegated value whose scope differs from the
item's or whose delegate is its person faulted. `fixtures/board_writer/`: `decide_delegated` (written, spellings
from grant, `People:` and `Scope`), `decide_delegated_no_scope`, `decide_delegated_no_grant`,
`decide_delegated_bad_line` (one bad grant voids it), `decide_delegated_not_gate_person` (owner board),
`decide_delegated_any_board` (accepted for any of `People:`), `decide_delegated_event_gate`,
`decide_delegated_gateless`, `decide_delegated_other_repo` (refused), `decide_delegated_not_yet` (closes, kept
waiting), `decide_delegated_board_only` (refused), `decide_delegated_multi_ref` and `decide_delegated_two_gates` (refused,
rule 5), `decide_delegated_one_ref_no_gate` and `decide_delegated_two_refs_no_gate` (accepted, gateless), `decide_delegated_other_repo_second_ref` (a `#`
ref beside a second ref: rule 4), `decide_delegated_work_order` (open, a delegated `kept waiting` line on a decision gate), `decide_own_answer_bad_delegates` (the person's own answer
written on a board whose standing `Delegates:` line is faulty), `add_scope`. `fixtures/board/` also: a bad grant an
edit introduces (error) against one standing (ℹ); `delegates_changed` false on reordered grants and whitespace.
`fixtures/lift/`: `lift_gate` refusing a delegate on the override, check and date shapes, the `board <repo>`
suffix, one equal to `by`, and a delegate without a scope; the delegated Log lines written; `ledger.py set`
refusing `--delegate` on an override and a reassign, and `--scope` without `--delegate` (`Unusable`). `fixtures/verdict/`: a delegated answer covered at base; a lift PR that also adds the grant
(`lift-board-diff`); one that changes only the item's `Scope`, its Log line and `Decided` in the base scope (`lift-board-line`); one
that changes the item's `Scope` and answers in the new scope (`lift-ledger`); one under no grant
(`lift-delegate-uncovered`); one on another repo's entry (`lift-delegate-uncovered`); a ledger lift over a delegated item,
undelegated Log line or delegated (`ledger-lift-delegated` both), the item open and decided, and a delegated
item among the `shared` set while the `decided` form wins, `ledger-lift-delegated` (a closed one is not in the tree and is not needed), and a delegated line on the person's own form
(`ledger-lift-delegated`); `lift-delegate-uncovered` before `lift-ledger` on a PR with both faults; a delegate-only change seen by `tripwire`.
`fixtures/board_split/`: a v2 board with `Delegates:` carried into `README.md`; one below an item refused.
The ledger fixtures' `log_lines` cases: the delegated
`gate-lifted` and `kept-waiting` lines read (`by` the person, `delegate`, `scope`), and the override, check and
date shapes unchanged. `fixtures/sweep/`: a delegated answer covering its gate (no item filed); a
closed delegated answer whose gate was lifted owing nothing; one whose gate is still carried filed as owed, its act's
`text`, `detail.context` and `detail.recommended` the delegated wording above; a group whose newest answer is the
person's own and an older one delegated, filed with the older delegated answer's wording (its `set` reviewed);
a group of two delegated answers, the newer one's names in the act. `fixtures/board_writer/` and
`fixtures/verdict/` assert `delegate_problem()`'s exact message for each rule's refusal (rule 5 in the writer's
alone: the verdict meets it as `lift-no-gate`), and the verdict cases
an own-repo `#` ref (`lift-delegate-uncovered`, rule 4) and a `#` ref beside a second ref (`lift-no-gate`).
`fixtures/board_writer/` also: a delegated lifting answer writing its ledger half in the delegated Log form. `fixtures/grammar/`: `decided-field`
delegated, `delegates-line`, `scope-field`. `fixtures/run.py` gains runners for `board_delegates`,
`delegates_problems`, `delegation_covers`, `delegates_changed` and `parse_decided_delegation`.

## Builds

One build, **B1**: D1–D6 with the SPEC text and fixtures, in one PR, release v3.4 (D6). `item_record()`'s three
new keys change every existing expected item record, which B1 regenerates (as `doer` did in v2.8). On Paul's go the designer
files with each consumer's question seat (`ao td add`): agent-cadence's vendor PR, its `board_edit.py`
`--delegate` and `--scope` pass-through, the board's `README.md` as a person path tested with
`delegates_changed()`, and its board-write carve-out letting no delegate's PR add a `Scope` (D3's limit);
ShiftLead's vendor PR, its readers showing the delegate from `item_record()`, and its director seat writing
delegated answers only once every reading repo has v3.4, with the person writing each board's `Delegates:` line.

## Not done

- **Delegation on another repo's entry** (D3 rule 4): the other repo's lift would need to carry and check the
  delegation from a board it does not read.
- **A carve-out for a delegated ledger-only lift** (D4): it is written with `ledger.py set --delegate --scope` and
  reviewed; the carve-outs never judge a grant without its item.
- **A delegate on `add --decided`** (`decided_file()`): an item raised already answered is the person's record of
  an answer given elsewhere, not a delegate's.
- **Per-answer scopes** (`merge-line` allowing `Merge` but not `Hold`): a scope covers the item's answers.
- **A wildcard scope**: each authority is named.
- **The v2 line**: nothing writes it.
- **Who raised an item**: the package cannot tell; the scope's honesty is the consumer's (D3's limit).

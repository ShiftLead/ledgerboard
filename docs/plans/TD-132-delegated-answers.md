# TD-132: an answer a delegate makes for the person

**Status:** Draft 4 (round 1 applied: its fact-checks and design review), 2026-11-17 (session lb-designer). Class: **wide** (a vendored, published format: a new
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
`decided_file()`, and `_item_read()`'s tuple, which gains the two fields so `edit_item()`'s and `decided_file()`'s read-backs
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
else `by` stays and `delegate` and `scope` are None. `log_line()` (and `log_lines()`)
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

**Faults** (`delegates_problems(board)`, errors on a board an edit changed, as `people_problems()`'s are): a
grant outside the form (an empty `()` among them); a person not on `People:` (so a board with no `People:` line
holds no valid grant); a delegate who **is** on `People:` (a delegate is not a person); a delegate granted for
itself; two grants of one delegate for one person; a scope named twice in a grant; a second `Delegates:` line
(the first is read). Names are compared case-insensitively, as people are.

**A faulty line grants nothing.** `delegation_covers(board, delegate, person, scope)` (new, the one function the
writer and every verdict call) returns True only when `delegates_problems()` finds no fault in the line and a grant
of that delegate, for that person, names that scope. So a line with one bad grant voids every grant until it is
fixed, as an unreadable `People:` leaves `who_answered()` no default. There is no wildcard scope; a board with no
`Delegates:` line accepts no delegated answer.

**Spelling.** The writer writes the delegate as the grant spells it, the person as `People:` spells it (as
`who_answered()` does today) and the scope as the item's `Scope` spells it, so a verdict's byte-for-byte
recompute (D4) gets one text.

`delegates_changed(base, head)` (new, pure) returns whether the `Delegates:` line's grants differ between two
boards, for a consumer's person-paths gate to test exactly (D4).

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
4. the item's Context names no gate on **another repo's** entry: that repo lifts its own gate by its own tool PR,
   reading only its own board, so it could neither carry nor check the delegation. A delegated answer there is
   refused in this release (*Not done*).

A delegate may give any of the item's answers, a waiting-only one included: its `Not yet` closes the item and
keeps the gate waiting, as the person's would (the re-ask window then runs as for the person's answer). A grant is
for a kind of decision, not for some of its answers.

`item_file_problem()` also faults a delegated `Decided` whose scope differs from the item's `Scope`, one on an
item with no `Scope`, and one whose delegate equals its person.

**A known limit.** The package compares names; it cannot tell who raised an item (`Session` is not an identity).
A delegate that may raise items through a consumer's board-write carve-out could raise one, scope it, and answer
it. So the scope's honesty rests on the consumer: its board-write carve-out must not let a delegate's own PR add
an item with a `Scope`, or its review must read scopes. agent-cadence's and ShiftLead's entries say so.

### D4. Who checks what

- **The board writer**: `edit_item(..., "decide", by=, delegate=)` (`by` the person; the scope read from the
  item's `Scope`), `plan_edit()` passing the board's grants (`edit_item` stays pure), and the CLI
  (`python3 -m ledgerboard.board decide --by pat --delegate director`, `add --scope merge-line`; `TAKES`,
  `NEEDS_OPT` and the parser gain both). It writes the D1 form and refuses a delegated answer D3 does not cover,
  naming which rule fails. `item_file(..., scope=)` and its read-back gain the field.
- **The lift**: `lift_gate()` and `decide_lift()` gain `delegate=` and `scope=`, used only to write D1's Log form;
  every comparison they make is of `by`, the person, as today.
- **`lift_pr_verdict()`** (a board answer's lift on this repo's entry) recomputes the answer with
  `edit_item(..., by=, delegate=)` and `decide_lift(..., delegate=, scope=)`, so a delegated answer reproduces
  byte for byte; it then requires D3 against the **base** tree: `delegation_covers()` over the base board and the
  item's base `Scope`; else `delegate-uncovered`, naming the rule. Because the recompute starts from the base item,
  a PR that also changes the item's `Scope` differs from it and is `lift-board-line`; one that also changes
  `README.md` (a grant added or changed) is `lift-board-diff` (`_one_items_change()`), before any D3 test. So a PR
  can neither grant nor rescope what it uses. A gateless delegated answer goes to review as every gateless answer
  does (`lift-no-gate`); one on another repo's entry is `delegate-uncovered` (rule 4).
- **`ledger_lift_verdict()`**, the ledger-only lift: on its *decided* form (the base item's `Decided` lifts the
  gate), the Log line must carry the base item's delegation exactly: an undelegated line over a delegated
  `Decided` is `lift-delegation-dropped`, a delegated line over an undelegated one, or with another delegate or
  scope, `lift-delegation-differs`. On its other forms (the person's own lift, no item) a delegated Log line is
  `lift-delegated`: with no item there is no scope. `lift_form()`'s *decided* reading is the same. So the ledger
  never says the person lifted what a delegate answered.
- **`tripwire()`** compares `(decided, decided_by, decided_delegate, decided_scope)` where it compares
  `(decided, decided_by)` today, so a change of the delegate alone is seen as a change of the answer; it gains no
  flag of its own.
- **The sweep**: `_answers_owing()` serves only another repo's entries, where rule 4 refuses a delegated answer, so
  it skips an item whose `Decided` is delegated (a hand-written one owes no lift; `board_problems()` faults it by
  rule 4). Elsewhere the sweep reads `decided_by`, the person, as today: a delegated answer covers its gate and
  opens the `kept waiting` window as the person's would.
- **A change to `Delegates:`** never passes a lift carve-out (`lift-board-diff`, above). Who may change it is the
  consumer's person-paths gate (agent-cadence lists the board's `README.md` as the person's path, testing the line
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

A minor, **v3.4**: SPEC already holds an untagged v3.3 (TD-123, with TD-131, TD-133 and TD-119 possibly beside
it), so this build writes its own *Versions* paragraph headed v3.4; if v3.3 is tagged before it merges and v3.4 is
taken, every `v3.4` it writes becomes the next untagged minor. New forms only: every file an earlier v3 wrote reads
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
> with no `Scope`, with a scope other than the item's, or whose delegate is its person. `item_record()` gains
> `scope`, `decided_delegate` and `decided_scope`.

**In *Edits*, the decide bullet gains:**

> With `delegate`, it writes the delegated form, the delegate as the grant spells it, the person as `People:`
> does, the scope as the item's `Scope` does, and refuses an answer `delegation_covers()` does not allow, on an
> item with no `Scope`, by a person who may not answer the item, or on a gate on another repo's entry.

**In *The merge gate's verdicts*, a paragraph:**

> A `Decided` written in the PR by a delegate passes `lift_pr_verdict()` only when `delegation_covers()` holds over
> the **base** board for the item's base `Scope`, the person may answer the item as an undelegated answer is
> judged, and its gate is on this repo's entry; else `delegate-uncovered`. A PR that also changes the item's
> `Scope` is `lift-board-line`, one that also changes `README.md` `lift-board-diff`, as for any lift PR. On
> `ledger_lift_verdict()`'s decided form the Log line carries the base item's delegation exactly
> (`lift-delegation-dropped`, `lift-delegation-differs`); on its other forms a delegated Log line is
> `lift-delegated`. `tripwire()` reads a changed delegate or scope as a changed answer.

**In *The ledger*, the Log shapes:** the `gate-lifted` answer shape and the `kept-waiting` shape read
`by <name>[ for <name> (<name>)]`: with ` for`, the first name is the delegate, the second the person, the third
the scope; `log_line()` returns `by` as the person, with `delegate` and `scope`, None for an undelegated line.

**In *Versions*, after the newest:** **v3.4 adds delegated answers** (TD-132): the `Delegates:` preamble line, the
`decide` item's `Scope` field, the delegated `Decided` form and Log `by` form, `board_delegates()`,
`delegates_problems()`, `delegation_covers()`, `delegates_changed()`, `parse_decided_delegation()`, the writer's
`delegate` and `scope`, and the verdicts' `delegate-uncovered`, `lift-delegated`, `lift-delegation-dropped` and
`lift-delegation-differs`. Every file an earlier v3 wrote reads the same; an earlier reader reads a delegated
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
waiting), `add_scope`. `fixtures/verdict/`: a delegated answer covered at base; a lift PR that also adds the grant
(`lift-board-diff`); one that also changes the item's `Scope` (`lift-board-line`); one under no grant
(`delegate-uncovered`); one on another repo's entry (`delegate-uncovered`); a ledger lift whose Log line drops the
base item's delegation (`lift-delegation-dropped`), names another delegate (`lift-delegation-differs`), and a
delegated line on the person's own form (`lift-delegated`); a delegate-only change seen by `tripwire`.
`fixtures/board_split/`: a v2 board with `Delegates:` carried into `README.md`; one below an item refused.
`fixtures/lift/`: the delegated Log lines written. The ledger fixtures' `log_lines` cases: the delegated
`gate-lifted` and `kept-waiting` lines read (`by` the person, `delegate`, `scope`), and the override, check and
date shapes unchanged. `fixtures/sweep/`: a delegated answer covering its gate (no item filed);
`_answers_owing` skipping a delegated answer on another repo's entry. `fixtures/grammar/`: `decided-field`
delegated, `delegates-line`, `scope-field`. `fixtures/run.py` gains runners for `board_delegates`,
`delegates_problems`, `delegation_covers`, `delegates_changed` and `parse_decided_delegation`.

## Builds

One build, **B1**: D1–D6 with the SPEC text and fixtures, in one PR, release v3.4 (D6). On Paul's go the designer
files with each consumer's question seat (`ao td add`): agent-cadence's vendor PR, its `board_edit.py`
`--delegate` and `--scope` pass-through, the board's `README.md` as a person path tested with
`delegates_changed()`, and its board-write carve-out letting no delegate's PR add a `Scope` (D3's limit);
ShiftLead's vendor PR, its readers showing the delegate from `item_record()`, and its director seat writing
delegated answers only once every reading repo has v3.4, with the person writing each board's `Delegates:` line.

## Not done

- **Delegation on another repo's entry** (D3 rule 4): the other repo's lift would need to carry and check the
  delegation from a board it does not read.
- **Delegation on ledger-only lifts** (D4): with no item there is no scope; a delegate answers through a board item.
- **Per-answer scopes** (`merge-line` allowing `Merge` but not `Hold`): a scope covers the item's answers.
- **A wildcard scope**: each authority is named.
- **The v2 line**: nothing writes it.
- **Who raised an item**: the package cannot tell; the scope's honesty is the consumer's (D3's limit).

# TD-132: an answer a delegate makes for the person

**Status:** Draft 1, 2026-11-17 (session lb-designer). Class: **wide** (a vendored, published format: a new
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
  readers do not read has been a minor before (`People:` v2.3, `Answered by:` v2.4, `Doer` v3.1).
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
`by` is today). `parse_decided_value(value)` keeps its `(label, date, by)` triple, `by` the **person**, and
`parse_decided_delegation(value)` (new) reads `(delegate, scope)` or None. So every reader that compares
`decided_by` with a gate's person — the lift, the sweep, every verdict — reads a delegated answer as the person's
unchanged, and only the delegation checks (D3) read the delegate.

`BoardItem` gains `decided_delegate` and `decided_scope` (None for an undelegated answer); `decided_by` stays the
person.

**The v2 line** is not extended: nothing writes it, so no v2 line holds a delegate. A v2 `(by director for pat
(merge-line))` is outside the v2 form, as any non-person `by` is today; `_v2_read()` converts only what v2 reads.

**The Log line** a lift writes names the delegation the same way:
`gate lifted: decision (pat) — by director for pat (merge-line); answer "Merge"`, and `kept waiting: … — by
director for pat (merge-line); answer "Not yet"`. `LOG_SHAPES`' `by` token becomes `by <name>[ for <name>
(<name>)]`; `parse_log()` returns `by` as the person and the delegate and scope beside it. An undelegated line reads
as today.

### D2. Where delegations are declared: `Delegates:` beside `People:`

A board preamble line, read as `People:` is (only the first; above a v2 board's first item; anywhere in a v3
board's `README.md`):

    Delegates: director for pat (merge-line, design-go-routine); director for sam (merge-line)

Each `;`-separated grant is `<delegate> for <person> (<scope>, …)`: one delegate, one person on the board's
`People:`, one or more scopes. `board_delegates(content)` reads it as a list of `(delegate, person, scopes)`, or
None with no line. `delegates_problems(board)` flags: a grant outside the form; a person not on `People:`; a
delegate who **is** on `People:` (a delegate is not a person); a second `Delegates:` line (the first is read);
a delegate granted to itself (`director for director`). A board with no `Delegates:` line accepts no delegated
answer.

A grant covers an answer when its delegate, person and one of its scopes equal the answer's (names compared
case-insensitively, as people are). There is no wildcard scope: each authority is named.

### D3. What a scope covers: the item says, the grant allows

An item a delegate may answer carries a header field `**Scope:** <scope>`, one name, written by whoever raises the
item (`python3 -m ledgerboard.board add --scope merge-line`, agent-cadence's `board_edit.py` passing it; `item_file(..., scope=)`), placed after `Doer` in the writers'
order. `Scope` is a `decide` item's field only: on any other kind it is a fault (`item_file_problem()`), as
`Doer` is off an `act`. The item's raiser says what kind of decision it is; the person's grant says which kinds the delegate may
take. A delegated answer is accepted only when **all** hold:

1. the item has a `Scope`, and the answer's scope equals it;
2. the board's `Delegates:` holds a grant of that delegate, for that person, naming that scope;
3. the person may answer the item, by the rule that judges an undelegated answer of the same item: on an item
   whose Context names a gate on this repo's entry, the gate's person, or any of `People:` on an `Answered by: any`
   board (`lift_gate()`, `decide_lift()`); on a gate on another repo's entry, `_may_answer()`'s rule
   (`board.py`); on an item with no gate, a name on `People:` (`who_answered()`).

The package checks only names: what `merge-line` means, and whether an item is honestly scoped, is the raiser's
and the review's (a scope is visible in the item and in the PR that adds it).

### D4. Who checks what

- **The board writer**: `edit_item(..., "decide", by=, delegate=)` (`by` the person; the scope read from the
  item's `Scope`), `plan_edit()` passing the board's grants (`edit_item` stays pure), and the CLI
  (`python3 -m ledgerboard.board decide --by pat --delegate director`, `add --scope merge-line`; `TAKES`,
  `NEEDS_OPT` and the parser gain both). It writes the D1 form and refuses a delegated answer D3 does not cover,
  naming which of the three fails. `item_file(..., scope=)` and its read-back gain the field.
- **The lift**: `lift_gate()` and `decide_lift()` gain `delegate=` and `scope=`, used only to write D1's Log form;
  every comparison they make is of `by`, the person, as today.
- **The merge gate's verdicts** in this package: `lift_pr_verdict()` (a board answer's lift, this repo's entry and
  another repo's) recomputes the answer with `edit_item(..., by=, delegate=)` and `decide_lift(..., delegate=,
  scope=)`, so a delegated answer reproduces byte for byte; it then requires D3 against the **base** tree's
  `Delegates:` and the item's base `Scope` (a PR cannot grant the authority it uses, nor rescope the item it
  answers), else `delegate-uncovered`, naming the rule. A gateless delegated answer goes to review as every
  gateless answer does today (`lift-no-gate`). `ledger_lift_verdict()` refuses a delegated Log line
  (`lift-delegated`): a ledger-only lift has no item and no scope. `tripwire()` compares `(decided, decided_by,
  decided_delegate, decided_scope)` where it compares `(decided, decided_by)` today, so a change of delegate alone
  is seen.
- **A change to `Delegates:`** is never a carve-out: `lift_pr_verdict()` refuses a PR that changes the line in
  the board's `README.md` (`delegates-changed`), so it goes to ordinary review. A board-write carve-out, and the
  person-paths gate that keeps the line the person's, are the consumer's (agent-cadence's board row and its
  person paths; its entry). The package does not decide who the person is.
- **A standing board** (`board_problems()` with no `old`, which judges open items): an open item whose delegated
  answer the current `Delegates:` no longer covers is ℹ (a grant withdrawn later does not unmake a past answer),
  never an error. Archived items are not judged, as today; an audit over them is a consumer's.
- **Ledger-only lifts** take no delegate (above): a delegate answers through the board's item.

### D5. Surfaces that hard-code the preamble

`delegates_problems()` scans for a second line as `people_problems()` and `answered_by_problems()` do.
`SPLIT_PREAMBLE_LINE_RE` (`People|Answered by|Ledgerboard`) gains `Delegates`, so `_split_text()` refuses it below
the first item as it does the others, and `_split_check()`'s equality check compares `board_delegates()` of the
old and new boards beside `board_people()` and `answered_by()`. `_split_readme()` carries every preamble line whole and needs no change. SPEC's
sentence naming the lines a split refuses below an item (*The board as a directory*, *Migration*: "`People:`,
`Answered by:` or `Ledgerboard:`") gains `Delegates:`.

### D6. The release

A minor, v3.N (the next untagged): new forms only, every file an earlier v3 wrote reads the same. An older reader
meets a delegated `Decided` as outside the form, so **no delegate writes one until the board's repo has vendored
v3.N** and the consumers' writers pass it; likewise no item carries `Scope` before then (an older
`item_file_problem()` faults an unknown field). Order: this repo's build and release; agent-cadence's vendor PR (its
`board_edit.py` passes `--delegate`, `--scope`; its person-paths gate lists the board's `README.md`); ShiftLead's
vendor PR, then the director seat writes delegated answers and the person writes the `Delegates:` line for each
board it answers.

## The SPEC text

**In *The board*, after `Answered by:`:**

> **`Delegates:`** (v3.N) — `Delegates: <delegate> for <person> (<scope>, …); …`, a preamble line read as
> `People:` is, granting a delegate the authority to answer for a person on the board's `People:`, on items of the
> named scopes. Each name is a person's name in grammar; a delegate is not on `People:` and never its own person.
> `board_delegates(content)` reads the grants as `(delegate, person, scopes)`, or None with no line;
> `delegates_problems(board)` names a grant outside the form, a person not on `People:`, a delegate on `People:`,
> a delegate granted to itself, and a second line. No wildcard: a board with no line accepts no delegated answer.
> A delegated answer counts as its person's for every purpose: it lifts the gate, closes the item and clears
> what waits on the person, and every reader that shows who answered shows the delegate beside the person.

**In *The board as a directory*, the header fields, after `Doer`:**

> - `Scope` — one name, the kind of decision the item is, written by whoever raises it; a delegate may answer
>   the item only under a grant naming this scope (*`Delegates:`*).

**The `Decided` bullet gains:**

> or, answered by a delegate, `<date> by <delegate> for <person> (<scope>) — <label>` (v3.N):
> `parse_decided_value()` returns the person as `by`, and `parse_decided_delegation(value)` the
> `(delegate, scope)`, None for an undelegated value.

**In *Edits*, the decide bullet gains:**

> With `delegate`, it writes the delegated form, its scope the item's `Scope`, and refuses an answer no grant
> covers: an item with no `Scope`, no grant of that delegate for that person naming it, or a person who may not
> answer the item.

**In *The merge gate's verdicts*, a paragraph:**

> A `Decided` written in the PR by a delegate passes `lift_pr_verdict()` only when the **base** tree's
> `Delegates:` grants that delegate, for that person, the item's base `Scope`, and the person may answer the item
> as an undelegated answer is judged; else `delegate-uncovered`. A PR that changes the `Delegates:` line is
> refused (`delegates-changed`), so it goes to review. `ledger_lift_verdict()` refuses a delegated Log line
> (`lift-delegated`). `tripwire()` compares an item's delegate and scope with its answer and answerer.

**In *The ledger*, the Log shapes:** `by <name>` becomes `by <name>[ for <name> (<name>)]`, the delegate first
when present, the person after `for`.

**In *Versions*, after the newest:** **v3.N adds delegated answers**: the `Delegates:` preamble line, the item's
`Scope` field, the delegated `Decided` form and Log `by` form, `board_delegates()`, `delegates_problems()`,
`parse_decided_delegation()`, the writer's `delegate`, and the verdicts' `delegate-uncovered`. Every file an earlier
v3 wrote reads the same; an earlier reader reads a delegated `Decided` as outside the form.

**Appendix: grammar:** `decided-field ::= "**Decided:** " date ( " by " person ( " for " person " (" person ")" )? )? " — " item-text`;
`delegates-line ::= "Delegates: " grant ( "; " grant )*`, `grant ::= person " for " person " (" person ( ", " person )* ")"`;
`item-header` gains `scope-field ::= "**Scope:** " person`, after `doer-field`, on a `decide` only. Each new
production gets its `fixtures/grammar/` case.

## The fixtures

All invented. `fixtures/board/`: a README with `Delegates:` read (`delegates.json`), each `delegates_problems`
fault, a second line. `fixtures/item/`: a delegated `Decided` read (`by` the person, delegate and scope beside), one
missing its scope (outside), a `Scope` field read. `fixtures/board_writer/`: `decide_delegated` (written),
`decide_delegated_no_scope`, `decide_delegated_wrong_scope`, `decide_delegated_no_grant`,
`decide_delegated_not_gate_person` (owner board), `decide_delegated_any_board` (accepted for any of People),
`add_scope`. `fixtures/verdict/`: a delegated answer covered at base; one whose grant the PR itself adds
(`delegate-uncovered`); one whose item's `Scope` the PR changes; a PR changing `Delegates:` refused by the board
carve-out. `fixtures/board_split/`: a v2 board with `Delegates:` carried into `README.md`; one below an item
refused. `fixtures/lift/`: the delegated Log line written; the ledger fixtures' `log_lines` cases: it read
(`by` the person, `delegate`, `scope`), and the `gate-lifted` override, check and date shapes unchanged.
`fixtures/grammar/`: `decided-field` delegated, `delegates-line`, `scope-field`. `fixtures/run.py` gains runners
for `board_delegates`, `delegates_problems` and `parse_decided_delegation`. `fixtures/verdict/` also: a ledger
lift with a delegated Log line (`lift-delegated`); a delegate-only change seen by `tripwire`.

## Builds

One build, **B1**: D1–D5 with the SPEC text and fixtures, in one PR, release v3.N. On Paul's go the designer files
with each consumer's question seat (`ao td add`): agent-cadence's vendor PR, its `board_edit.py` `--delegate` and
`--scope` pass-through, and the board's `README.md` as a person path; ShiftLead's vendor PR and its director seat
writing delegated answers only after it, and the person's `Delegates:` lines.

## Not done

- **Delegation on ledger-only lifts** (D4): a delegate answers through a board item.
- **Per-answer scopes** (`merge-line` allowing `Merge` but not `Hold`): a scope covers the item's answers.
- **A wildcard scope**: each authority is named.
- **The v2 line**: nothing writes it.

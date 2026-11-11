# TD-067: a lift of one part of a shared decide item

**Status:** Draft 1, 2026-11-11 (session lb-designer). Class: **wide** (a vendored, published format: what
`board.py decide --board-only` writes and what `tripwire()` flags, which both consumers vendor; cap 6 rounds,
cadence.md §4.8). Rounds: not yet run (the record: [docs/reviews/TD-067.md](../reviews/TD-067.md)).

**Entry:** [TD-067](../ledger/TD-067.md). Reported by ShiftLead (its TD-1551, PR #3447, 2026-11-11).

## The problem

A `decide` item whose Context names a parent and a `decision (<p>)` gate, with `Parts:` listing the parts it
asks about, is a **shared** item: one question for several entries. The `set by=` route lifts the gate on one
entry. The consumer's wrapper runs `ledger.py set TD-n --blocked-by '' --by <p> --answer <label> --shared-item`
(the Log line ends `; shared board item left open`) and `board.py decide --board-only` (the board half) in one
commit. When another entry the item lists still carries the gate, the board half writes `Decided: <label> (by
<p>) (D)` on the item, and `closes()` keeps it open.

That is what the target design chose (§1.1, the `set by=` route; §3.1, the shared-snapshot exception; §6 (b),
`closes()`). It says the remaining parts "are lifted by a re-answer through `board.py decide`". The harm is the
item's one `Decided:`, which now speaks for parts the person did not answer:

- `needs_you()` classes every open item with a `Decided:` as `decided`, "a session's work order", ahead of the
  person's to-do. The parts still waiting on the person drop out of what the person is asked, and the item
  reads as an order to act on them with that label.
- The line holds one `Decided:`, so it cannot say which part the answer was for.
- The module's own sweep does not lift the other parts from it (`_answers_owing()` reads only a `closed-decided`
  item, and the close rule keeps the item open while a listed part carries the gate). A consumer that reads a
  `decided` item as an answer is the risk; the person's missing question is the harm in any case.

Found live in ShiftLead on 2026-11-11: Context `TD-1551 decision (paul)`, Parts TD-1664, TD-1669; the person
answered Go on TD-1664 alone; the lift wrote `Decided: Go (by paul)` on the shared item, which still names
TD-1669.

## What is already settled

These stand, and the design builds on them:

- **The Log line.** The `set` route's lift of one part writes `gate lifted: decision (<p>) — by <p>; answer
  "<label>"; shared board item left open` (SPEC *Ledger entries and their edits*). The Log is where the
  per-part answer lives already: who answered, which label, which entry, which day.
- **`closes()`** (SPEC *Closing on the answer*): a lifting answer closes the item only when nothing listed still
  carries the gate after the write. Unchanged.
- **`covers()`** counts `open` and `decided` items alike, so an open item without a `Decided:` still covers its
  remaining parts, and the sweep does not re-ask them.
- **The close rule** closes the item, by key, once the gate is gone from every entry it lists.
- **`decide_lift()`** of a later answer on the item lifts each listed entry that still carries the gate and logs
  `gate lift skipped: <id> no longer carries <gate>` on the Context entry for each one that does not (v2.4).
- **The item key** strips `Decided:`, so writing it or not moves no key.

## Options weighed

**A. The board half writes nothing while a listed entry still carries the gate** (chosen). The item stays open
and undecided, so it stays in the person's to-do, keeps covering its remaining parts, and is answered later like
any unanswered item. The per-part answer is in the Log, where it already was. No grammar changes, no key moves,
and `needs_you()`, `covers()`, `closes()`, the sweep and `decide_lift()` read it as they do today. The cost: the
item's text and `Parts:` still name the part already answered. A consumer that shows the item can mark that part
from the ledger it reads. The module's line cannot, and `decide_lift()` of the later answer logs it as skipped.

**B. Record the answer per part on the line**, a new trailing field such as `Answered: TD-1664 Go (by paul)
(D)`. The item could then say which parts are answered. It is a new field in the open item's grammar: every reader
must learn it and the key must strip it. A v2.7 reader would read it as part of the field before it, which
changes what that reader parses (the *Versions* rule that a minor reads every file the major's earlier releases
wrote then fails for the older reader). And it duplicates the Log. Rejected.

**C. Split the item**: close the shared item and add a new one whose `Parts:` lists only the entries still
carrying the gate. `Parts:` is in the item key, so the new item is a new question with a new key. A consumer that
persists keys (ShiftLead's mail and cards) loses the thread it tied to the item, and the closed item's
`Decided:`, if any, still speaks for every part its snapshot lists. Two writes per lift, and a board line the
person did not ask for. Rejected.

**D. Refuse `--board-only` when a listed entry still carries the gate**, so the wrapper must not run the board
half. Equivalent on the board to A, but the refusal (exit 1) breaks the wrapper's one commit unless every
wrapper first learns to tell a shared item from a full lift. That is `closes()`' own question, which the writer
answers already. Rejected in favour of A's no-op, which every wrapper meets as "nothing to change".

## Decisions

**D1. `--board-only` leaves an item open and unanswered while it still asks.** On `board.py decide
--board-only`, when the answer lifts (`Lifts:`, or `Go` with none) and `closes(item, label, entries)` is false
because a listed entry of this repo (the Context entry or a `Parts:` id, read from the open ledger as it stands)
still carries the gate, the writer writes nothing: the board is left byte for byte, exit 0. It reports
`left_open`, the listed ids still carrying the gate, in the item's order (Context entry, then the `Parts:` line's
order), spelled as the item spells them. With `--json` or `--plan` the report is
`{"action": "decide", "board_only": true, "entries": [], "left_open": [...], "line": n, "paths": [], "subject":
null, "item_notes": [...]}`, `item_notes` being the unchanged line's notes. Without either, nothing on stdout,
and `left open: <ids> still carry <gate>` on stderr. When `closes()` is true (the last part, or a Context entry
that never had parts), the write is as today: `Decided:` and `Closed: D — lifted.` in one write.

D1 covers a `--board-only` answer whose Context entry itself still carries the gate as well (a board half run
before, or without, the `set`): today it writes a `Decided:` for a gate nothing has lifted, the same harm with
nothing shared. One rule covers both: a `--board-only` lifting answer writes the board only when it closes the
item.

D1 holds only for `--board-only`. A full `board.py decide` (the decide lift) lifts every listed entry that
carries the gate, so `closes()` is true after it and its write is unchanged. A waiting-only answer and a work
order are not the `set` route's (it only lifts), and on `--board-only` they write as today.

An item whose Context names another repo's entry (`<repo>#TD-n`) is unchanged: it is answered on the board
alone and stays decided but open, its lift being a tool PR in that repo. `closes()` cannot read that ledger, and
the item's `Decided:` there is the answer the other repo's lift reads.

**D2. The remaining parts are answered as an unanswered item is.** The person's later answer on the shared item
goes through `board.py decide` (the decide lift): it lifts each listed entry still carrying the gate, logs `gate
lift skipped: <id> no longer carries <gate>` for each part already lifted, and closes the item. Its base line
carries no `Decided:`, so a PR of that answer can be the carve-out (`lift_pr_verdict()` (b): "never answered at
the base"); today's re-answer of a decided item always takes ordinary review. A later `set by=` on the last part
still carrying the gate writes `Decided:` and `Closed: — lifted.` through `--board-only`, as today (no suffix:
nothing is left shared). A waiting-only answer closes the item and logs `kept waiting` on each listed entry still
carrying the gate, as today.

**D3. The tripwire flags a shared lift whose item gains a `Decided:`.** In `tripwire()`, a lift line ending `;
shared board item left open` is flagged `tripwire-shared-decided` when an item that covers the gate at the base
and still covers it at the head gains a new or changed `Decided:` at the head (`(decided, decided_by)` differ) and
stays open. That is the old writer's output, or a hand edit, saying an answer the person gave for one part speaks
for the rest. The existing `tripwire-shared` check (no item it covers still asks another listed entry) stands
beside it; both may fire on one lift. The flag sends the PR to ordinary review, like every tripwire flag: a
consumer whose wrapper still vendors an older `board.py` meets it once, on its next shared lift, and its review
passes it or the person re-answers.

The no-suffix case keeps its second clause: an item decided already at the base and newly closed `— lifted.` (the
last part of a shared item an older writer decided) is accounted for, so boards written before this release still
pass.

**D4. Items an older writer decided read as before.** No reader changes: an open item with a `Decided:` is
still `decided` in `needs_you()`, since the module reads the board alone and cannot tell a shared partial lift's
`Decided:` from a work order. Each consumer repairs the items it knows of with today's writers: `board.py done`
on the decided shared item (`Closed: D — <why>`, no `lifted`), then `board.py add --kind decide --parts <the ids
still carrying>`, its Context the parent and the gate, asking again for the entries left.

**D4a. What the sweep makes of the repair.** The closed old item still carries a lifting `Decided:`, so it is
*an answer owing a lift* (v2.7) to each entry it lists that still carries the gate and has no `gate lifted:` line
dated on or after `D − 1`: the parts never answered, and the parent. The new item covers them, so no `act` is
filed (it files only when an entry owed is not covered), and once the new item's answer lifts them the old answer
owes nothing. One edge stays: if the person answers the new item with a waiting-only answer within `reask_days`
of the old answer, the new item closes, the entries are no longer covered, and the sweep files the owed `act`
(*… was answered with a lift on <D> but still stands …*), which the person closes. The repair needs nothing new
from the module; the sweep fixture below holds the covered case.

**D5. A minor release, v2.8.** Nothing read changes and no key moves: v2.3 to v2.7 read every line it writes.
The writer writes less (D1) and the tripwire flags one more shape (D3). It is not a version event under SPEC
*Versions* (no item key, no canonical form). It ships as its own minor after v2.7, whose builds (TD-058's
B0–B4) are under way, so their release is not reopened; Paul may fold it into v2.7 instead, since nothing in it
depends on v2.7's work.

## Consumers

Each consumer's vendor PR of the release checks one thing in its `set by=` wrapper: a board half that writes
nothing (`paths: []`, `subject: null`, exit 0) is a success, and the commit then carries the ledger alone.

- **agent-cadence**: its vendor PR of the release, with its wrapper checked as above.
- **ShiftLead**: its sync PR, with its wrapper checked as above, and the repair of its known item (D4): the
  TD-1551 item decided by the TD-1664 lift, closed with `done` and asked again for TD-1669. An entry filed there
  through `ao td add --repo shiftlead` once the release is cut, by the build's author.

## The SPEC text the build lands

**1. *The board writer*, the decide lift bullet.** Replace

> **`--board-only`** writes the board half alone, the same line, `closes()` reading the ledger as it stands: the
> `set by=` route, whose `set` has lifted the gate already, so nothing is lifted twice.

with

> **`--board-only`** writes the board half alone, `closes()` reading the ledger as it stands: the `set by=`
> route, whose `set` has lifted the gate already, so nothing is lifted twice. A lifting answer writes the line
> only when it closes the item; while a listed entry still carries the gate (a part of a shared item, or a
> Context entry nothing has lifted) it writes nothing, exit 0, and reports `left_open`, those ids as the item
> spells them, in its order (v2.8). The item stays open and unanswered, still asking the person for the entries
> left, and the person's answer is the Log's `; shared board item left open` line. Any other answer writes as
> without it.

**2. *The board writer*, the report paragraph.** Replace

> `fmt` has no subject of its own, and a write that changes nothing (a rank line already so) prints none,
> writing nothing.

with

> `fmt` has no subject of its own, and a write that changes nothing (a rank line already so, or a
> `--board-only` answer left open) prints none, writing nothing; with `--json` its `subject` is null and its
> `paths` empty.

**3. *The board*, *Closing on the answer*.** After "a lifting answer on another repo's entry stays open until
that repo's lift merges." add

> A lifting answer that does not close the item is never written on it by the `set by=` route's board half
> (*The board writer*, v2.8): the item stays unanswered until the person answers it for the entries left.

**4. *The board*, the tripwire's bullets.** Replace the `; shared board item left open` bullet

> - **`; shared board item left open`:** an item covering it at the base still covers it at the head, and
>   another entry it lists (its Context entry or a `Parts:` id) still carries the gate;

with

> - **`; shared board item left open`:** an item covering it at the base still covers it at the head, and
>   another entry it lists (its Context entry or a `Parts:` id) still carries the gate; and (v2.8) no such item
>   gains a new or changed `Decided:` at the head while it stays open, since that answer would speak for the
>   entries left (`tripwire-shared-decided`);

and in the flag list, replace "`tripwire-shared` and `tripwire-board`" with "`tripwire-shared`,
`tripwire-shared-decided` (v2.8) and `tripwire-board`".

**5. *Versions*.** Append

> **v2.8 leaves a shared item unanswered by a lift of one part** (*The board writer*, *The merge gate's
> verdicts*): `board.py decide --board-only` writes nothing while a listed entry still carries the gate, where
> v2.4 to v2.7 wrote a `Decided:` that spoke for entries the person had not answered, and `tripwire()` flags such
> a `Decided:` (`tripwire-shared-decided`). Nothing read changes: v2.3 to v2.7 read every line it writes, and no
> key moves. An item an older writer decided reads as before, a `decided` work order; the consumer closes it and
> asks again for the entries left.

## Fixtures

All invented, in the existing fixtures' names (`robin`, `pat`, `sam`).

**`fixtures/board_writer/`**
- `decide_board_only_still_carried` (changed): its `after/board.md` equals `before/board.md` (TD-1 still carries
  `decision (robin)`); `expected.json` `{"exit": 0, "out": {"action": "decide", "board_only": true, "entries": [],
  "item_notes": [], "left_open": ["TD-1"], "line": 7, "paths": [], "subject": null}}`.
- `decide_board_only_shared_part` (new): the board's line 7 is `- [ ] decide 2026-01-12 (n/a) — Go on the report
  suite? Context: TD-8 decision (robin). Parts: TD-9, TD-10. Due: 2026-01-20. Answers: Go (default) | Not yet.`;
  the ledger holds TD-008 and TD-010 carrying `decision (robin)` (TD-010 `Part of: TD-008`), and TD-009 `Part of:
  TD-008` with no `Blocked by` and the Log line `2026-01-15: gate lifted: decision (robin) — by robin; answer "Go";
  shared board item left open`. `decide --line 7 --answer Go --by robin --board-only --ledger ledger --today
  2026-01-15 --json`: the board unchanged, `left_open: ["TD-8", "TD-10"]`, `paths: []`, `subject: null`.
- `decide_board_only_shared_last` (new): the same board; the ledger with TD-008 and TD-009 lifted (each with its
  `gate lifted` line) and TD-010 carrying none after its `set`. The answer closes the item: `Decided: Go (by robin)
  (2026-01-15). Closed: 2026-01-15 — lifted.`, `paths: ["board.md"]`, no `left_open` key.
- `decide_board_only` and `decide_parent_snapshot_part_archived_board_only` unchanged (each closes the item).
- The JSON of a write that writes (every other `decide` fixture) gains no `left_open` key: the key is present
  only on a write D1 leaves open.

**`fixtures/verdict/` (tripwire)**
- `set by= on one part of a shared item, left open` (changed): the head board's line 7 loses its `Decided:` (it
  equals the base's); still `[]`.
- `set by= on one part of a shared item, decided` (new): the same diff with the head's `Decided: Go (by pat)
  (2026-01-15).` on line 7, open; expects `[["tripwire-shared-decided", "TD-111 lifts decision (pat) leaving a
  shared board item open, but the item gains a Decided: that speaks for the entries left — leave it unanswered"]]`.
- `the last part of a shared item lifted, undecided at the base` (new): base line 7 open and undecided, TD-111
  lifted already (no gate, its `; shared board item left open` line), TD-112 carrying; the head lifts TD-112 with
  no suffix and line 7 gains `Decided: Go (by pat) (2026-01-15). Closed: 2026-01-15 — lifted.`; expects `[]`.
- `the last part of a shared item lifted, the item newly closed` unchanged (an older writer's decided item still
  passes).

**`fixtures/board/`**
- `shared_part_left_open.md` (new): `People: pat`; line 7 a shared `decide` (Context `TD-12 decision (pat)`,
  Parts TD-15, TD-16, Due 2026-01-20) with no `Decided:`; line 8 the same question an older writer decided
  (Context `TD-20 decision (pat)`, Parts TD-21, TD-22, `Decided: Go (by pat) (2026-01-08)`). Its `needs_you` at
  the runner's `TODAY` puts line 8 first as `decided` and line 7 among the person's to-do with its `due` class:
  the item a v2.8 writer left open stays asked, and the old one reads as it did (D4).

**`fixtures/sweep/`**
- `the repair of an older writer's shared item` (new, D4a): an open entry TD-30 carrying `decision (pat)` with
  parts TD-31 (lifted 2026-01-08, `; shared board item left open`) and TD-32 (carrying); the board holds the old
  item, closed `Closed: 2026-01-10 — asked again for TD-32.` with `Decided: Go (by pat) (2026-01-08)`, and the new
  open `decide` with Context `TD-30 decision (pat)` and `Parts: TD-32`. The sweep at 2026-01-12 files nothing and
  closes nothing (TD-30's and TD-32's gate covered by the new item; TD-31's lifted on 2026-01-08).

**Unit tests** (`tests/`): `plan_edit(..., board_only=True)` on a shared item returns a plan with no file
changes and `left_open`; `apply()` of it writes nothing; the command line exits 0 and prints the stderr line
without `--json`; `tripwire()` returns `tripwire-shared-decided` for the decided head and nothing for the
undecided one.

## The builds

**B1** (one build, `Part of: TD-067`): D1, D3 and the SPEC text 1–5 above, with the fixtures and unit tests,
landing together; it amends `docs/plans/target-design.md` §1.1 (*a shared parent-snapshot item left open and
decided* → left open and unanswered), §3.1 (the shared-snapshot exception's item left open, now undecided) and
§6 (b) (*the item stays open and `decided`* → stays open, unanswered), each with a dated note naming TD-067.
Location: `ledgerboard/board.py` (`_decide_ledger`, `plan_edit`, the report), `ledgerboard/__init__.py`
(`tripwire`), `SPEC.md` (*The board*, *The board writer*, *Versions*), `fixtures/board_writer/`,
`fixtures/verdict/`, `fixtures/board/`, `fixtures/sweep/`, `tests/`, `docs/plans/target-design.md`. Done when:
the precheck is green and every fixture above passes, with SPEC text 1–5 landed in the same PR.

Then a release (Paul's), agent-cadence's vendor PR and ShiftLead's sync PR, each checking its wrapper (*Consumers*).

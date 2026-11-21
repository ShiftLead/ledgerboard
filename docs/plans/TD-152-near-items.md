# TD-152: the gate sweep points at the item that already names the entry, and the tripwire names its items

**Status:** Draft 1, 2026-11-21 (session lb-designer). Class: **wide** (a change to the published, vendored
format: what `sweep()` files and returns, and the text of two `tripwire()` flags; cap 6 rounds, cadence.md §4.8).
Rounds not yet run. The record: [docs/reviews/TD-152.md](../reviews/TD-152.md). In plain words:
[docs/synopses/TD-152.md](../synopses/TD-152.md).

**Entry:** [TD-152](../ledger/TD-152.md), reported by samscrape's session on 2026-11-21.

## The problem

`covers()` finds the items that ask about an entry's gate in one form only: a `decide`, on a board whose
`People:` lists the gate's person, whose Context names the entry (or its `Part of` parent, with the entry among
`Parts:`) and the gate, nothing after the gate (SPEC *The gate sweep*; `ledgerboard/__init__.py`, `_covers()`,
`_names_entry()`, `_sweep_context()`, `_context_gate()`). A Context naming more than one entry, no gate, or more
than one gate keys to nothing (`_context_gate()` returns `None` for each).

So an item that does ask the person about the entry, in another form, is invisible to the sweep: an `act`; a
`decide` naming several entries, or the entry with no gate; a `decide` keyed to the gate on a board that does not
list the person. The sweep files a second item, a `decide` with Context `TD-n decision (<p>)`, beside it
(`sweep()`'s `gate.startswith("decision ")` branch). The person answers whichever they see first. When that is the
older one, its answer cannot lift the gate: a lift with no suffix is flagged `tripwire-no-decided` (no item
covering the gate gains a `Decided:`), and a lift logged `; no board item` is flagged `tripwire-no-board-item`
(the sweep's item covers it). Neither flag names an item (`tripwire()`'s two messages name the entry and the gate
alone), so the session found the second item by a search.

The reported case, on samscrape's board: an older open `act` whose Context named the entry among two others and
no gate; the sweep's `decide` beside it; the person's `done` on the act.

## What is already settled

- **One question per gate.** An answer lifts a gate only through an item `covers()` finds (*The decide lift*: it
  refuses an item that is not a `decide` naming one entry and one gate; *The merge gate's verdicts*: the
  tripwire's accounting reads `covers()`). One question for several entries is the parent's item with a `Parts:`
  snapshot (v2.6), the end-of-rounds item's form (cadence.md §4.8).
- **The sweep never rewrites an item it did not file, and never one it filed** (*One filing rule*).
- **A lift that rests on something other than a covering item's answer is an override** (`lift_gate(…,
  override=)`, its why required; the tripwire accounts for it by its `override:` Log line), which review reads.
- **An `act`'s close records no answer**: `done` writes `Closed:` and a why, never `Decided:` (*Edits*).

## The design

### D1. The sweep names the near items in the decide it files

When the sweep files a `decide` for an uncovered `decision (<p>)` (every condition of today's bullet met), it
first reads the **near items** of that entry and gate: each open item (state `open` or `decided`) on any board
read, of any kind but `fyi`, whose Context names the entry (one of its refs is the entry as that board reads refs:
a bare `TD-n` on this repo's own board, `<repo>#TD-n` naming this repo on any board), that `covers()` does not
find for the gate, and that is not keyed elsewhere:
- not an item whose Context names exactly one entry and exactly one gate, and that gate is not this one (it asks
  about that other gate: a `decide` for the entry's event, say);
- not an item whose Context names this entry and this gate followed by `lift` or `board <repo>` (the sweep's own
  `act`s, each with its own rule).

What is left asks the person about the entry in a form no answer lifts the gate through: an `act` (keyed to the
gate or not), a `decide` naming several entries, no gate or several gates, a `decide` keyed to the gate on a board
whose `People:` does not list `<p>`, or a `decide` whose Context goes on past the gate (`TD-4 decision (pat) —
design ready`, which SPEC already reads as naming no entry here).

With any near item, the decide is filed all the same, and its detail block's context (the entry's `**Context:**`,
else today's sentence) ends with one clause naming them:
`; <named> also <name|names> <ref>, but only an answer here lifts <gate>`. `<named>` is `item <id>`, or
`items <id>, <id>…` in id order; an item on a board other than the one the decide is filed on is followed by
` on <board>`, the board named as the sweep names boards (`origin_key`, else the basename). `<ref>` is the entry
as the filed item's Context spells it (`TD-n`, or `<repo>#TD-n` on another repo's board), `<gate>` as the entry
spells it. An item with no id (a v2 line with no readable date) is not named; when every near item lacks one, the
context is today's.

`sweep()` also returns them, as a new key: `near`, a list with one record per decide it files that has named
near items, `{id, gate, board, items}`: `id` the entry's `TD-n`, `gate` as the entry spells it, `board` the board
filed on, `items` a list of `[board, item id]` in the clause's order. Empty when there are none; in entry-number
order, then the entry's gate order. A host may show it (a link from the new item to the old); it changes nothing
the sweep writes.

Why file and not hold: a near item's answer cannot lift the gate (D3), so holding the decide while one is open
would leave the gate with no question that can end it for as long as the near item stays open, and an `act` that
merely mentions the entry (*TD-5 and TD-6 wait on the release*) would silence it. Filed with the clause, the new
item tells the person which answer counts, and the old one stays theirs to close.

Nothing else changes: whether the decide is filed, on which board, its text, answers, Context and identity are
today's; a near item is read only when the decide is filed (never for the `has no board` act, never while the
decision is covered, held, deferred or within a window); the rerun over the sweep's own writes files nothing,
since the filed decide covers the gate.

### D2. The tripwire's two flags name the items they mean

`tripwire-no-board-item` and `tripwire-no-decided` name the covering items, by id, so a person or session can act
without a search:
- `tripwire-no-board-item`'s text ends ` (<ids>)`, the ids of the items `covers()` finds covering the gate
  (states `open`, `decided`) at the base or the head;
- `tripwire-no-decided`'s text ends ` (asked by <ids>)`, the same items; or, when no item covers the gate at the
  base nor at the head, ` (no item asks it: log the lift ; no board item)`.

`<ids>` are those items' ids, each once, in id order, joined by `, `. An item with no id is left out, and when
every covering item lacks one the text is today's. The flags' kinds, and when each is raised, are unchanged;
`lift_pr_verdict()`'s `flags` are `tripwire()`'s, so they carry the same text.

### D3. Only a covering item's answer lifts a gate

The report's third ask is settled as no change, stated in SPEC so no reader expects otherwise:
- **An item naming several entries does not lift one of them by an answer that names it.** One question for
  several entries already has a form, the parent's `decide` with `Parts:`, which the decide lift, `closes()`, the
  carve-out's (b) and the tripwire's shared-item rules each read. A second form, a free Context list with a
  per-answer `--lift TD-n` on the board writer's `decide`, would make what an answer lifts depend on a choice the
  person's press does not show, and each of those readers would need a second reading.
- **An `act`'s `done` never lifts a gate.** It records that a step was done, with no label and no `Decided:`, so
  there is no answer to carry and no `Lifts:` to read it against.
- **Where the person did mean a near item's answer to lift the gate**, the lift is an override (`set … --override
  "<why, naming the item and the answer>"`, from the person's own session in agent-cadence's rules), which review
  reads; the sweep then closes its own decide once the gate is gone (*The close rule*). D1's clause makes this the
  rare case, not the usual one.

### Limits accepted

- A near item opened after the decide is filed is not named: the sweep never rewrites an item it filed.
- An item that merely mentions the entry (an `act` about a release that several entries wait on) is named as
  near. The clause says only that an answer there does not lift the gate, which is true of it too.
- `uncovered_decisions()` is unchanged: a PR adding a decision writes its own covering item, and a near item
  beside it is the PR's review's to see.

## Options set aside

- **Hold the decide while a near item is open, and report the near-miss.** Leaves a gate with no question that
  can lift it for as long as an unrelated `act` stays open (D1, *Why file and not hold*).
- **File nothing and report the near-miss to the host alone.** The same, and the person sees nothing.
- **Let a `decide` with several entries in its Context cover each of them**, or let its answer name the entry it
  lifts. A second form for one question over several entries (D3).
- **Count an `act`'s `done` as a lifting answer.** It carries no answer (D3).
- **Have the board writer's `add` warn when a Context names an entry carrying a decision but not its gate.** The
  writer reads the ledger only with `--parts`; a prevention at write is a larger change, and D1 catches the case
  at the one point it matters, when a second question is filed.

## SPEC text

In *The gate sweep*, the `sweep(…)` paragraph's return, after `lifts: [{id, gate, kind, evidence}]}`:

> , and from v3.6 `near: [{id, gate, board, items}]` (TD-152, below)

so that it reads `returns {to_file: {board: [item]}, to_close: {board: [item id]}, lifts: [{id, gate, kind,
evidence}], near: [{id, gate, board, items}]}` (`near` from v3.6).

In the `decision (<p>)` bullet, after *else it is the sentence earlier releases wrote.*:

> **Near items** (v3.6). Before filing the decide, the sweep reads the entry's near items for the gate: each open
> item (state `open` or `decided`) on any board read, of any kind but `fyi`, one of whose Context's refs names the
> entry as that board reads refs, that `covers()` does not find for the gate, and that is neither an item whose
> Context names exactly one entry and one gate other than this one, nor one whose Context names this entry and
> this gate followed by `lift` or `board <repo>`. Such an item asks about the entry in a form no answer lifts the
> gate through (*The decide lift*). With any that has an id, the decide is filed all the same and its detail
> block's context ends `; <named> also <name|names> <ref>, but only an answer here lifts <gate>`: `<named>` is
> `item <id>`, or `items <id>, <id>…` in id order, each followed by ` on <board>` when on a board other than the
> one filed on (named as the sweep names boards); `<ref>` is the entry as the item's Context spells it, `<gate>`
> as the entry spells it. An item with no id is not named. `near` holds one record per decide so filed, `{id,
> gate, board, items}`: the entry's `TD-n`, the gate as the entry spells it, the board filed on, and `items`, the
> named items as `[board, item id]` in the clause's order; in entry-number order, then the entry's gate order;
> empty when there are none. Nothing else about the decide changes, and no near item is read when no decide is
> filed.

In *The decide lift*, after *It refuses an item that is not a `decide` naming one entry and one gate*'s sentence:

> An item `covers()` does not find answers nothing for a gate (v3.6 says so; no release did otherwise): an `act`'s
> `done` records no answer, and a `decide` naming several entries, or none with the gate, lifts none of them. A
> lift that rests on such an item is an override (`lift_gate(…, override=)`), which review reads.

In *The merge gate's verdicts*, after the sentence listing the other flags (*… `tripwire-shared-decided` (v2.7)
and `tripwire-board`.*):

> From v3.6 (TD-152) two flags name their items: `tripwire-no-board-item`'s text ends ` (<ids>)`, and
> `tripwire-no-decided`'s ` (asked by <ids>)`, `<ids>` the ids of the items covering the gate (states `open`,
> `decided`) at the base or the head, each once, in id order, joined by `, `; `tripwire-no-decided`'s ends
> instead ` (no item asks it: log the lift ; no board item)` when none covers it at either. An item with no id is
> left out, and when every covering item lacks one the text is as before v3.6.

In *Versions*, after v3.5's paragraphs:

> **v3.6 names what a duplicate question needs** (TD-152; *The gate sweep*, *The decide lift*, *The merge gate's
> verdicts*): the sweep's decide for an uncovered decision names, in its detail context, the open items that
> already name the entry but cannot lift its gate, and `sweep()` returns them as `near`; `tripwire-no-board-item`
> and `tripwire-no-decided` end naming the covering items' ids. No parse changes, and nothing the sweep files or
> closes changes but that clause; a consumer reading `sweep()`'s three keys, or the two flags by kind, reads as
> before.

## Fixtures and tests

**Sweep cases** in `fixtures/sweep/near/<case>/`, laid out and run as the `in_flight` cases are (each its own
`ledger.md` and v3 board directory `board/`, invented entries, repo `acme/widgets`, listed in `sweep/cases.json`
under `near`, expected in `sweep/expected.json`'s `near` keyed by case name, `{"missing": …}` against a module
whose `sweep()` returns no `near`), with a second board directory `other/` where a case says, read as a second
board with its own `url`. Each expected output is `{to_file, to_close, lifts, near, rerun}`. Unless said, the
entry carries `decision (pat)`, the own board lists `pat`, and nothing covers the gate:
1. An open `act`, Context naming `TD-n` and two other entries, no gate: the decide is filed, its context ending
   `; item <id> also names TD-n, but only an answer here lifts decision (pat)`; `near` names it.
2. An open `decide`, Context `TD-n` alone: the same.
3. An open `decide`, Context `TD-n, TD-m decision (pat)`: the same.
4. An open `decide` keyed `TD-n decision (pat)` on `other/`, which does not list `pat`: filed on the own board,
   the item named ` on <other>`.
5. An open `decide` whose Context is `TD-n decision (pat) — design ready`: named.
6. An open `act` keyed `TD-n decision (pat)` (not the sweep's words): named.
7. An open `fyi` naming `TD-n`; an open `decide` keyed `TD-n event (x)`; a closed `act` naming `TD-n`: none
   named, the output byte for byte today's (three cases).
8. Two near items added in the reverse of id order: `items <a>, <b>` in id order.
9. An `act` on `other/` naming `acme/widgets#TD-n`: named, with ` on <other>`.
10. A covering decide open, a near `act` beside it: nothing filed, `near` empty.
11. The entry deferred (a live blocker, v3.5) with a near `act`: nothing filed, `near` empty.
12. The entry with a `**Context:**` section: the clause follows that section's collapsed text.
13. An entry carrying two decisions, `decision (pat)` and `decision (sam)`, both people listed, one `act`
    naming the entry: two decides, each with the clause; `near` two records, in gate order.

In every case `rerun` files and closes nothing.

**Verdict cases**: the five expected `tripwire-no-decided` and `tripwire-no-board-item` texts in
`fixtures/verdict/expected.json` gain their endings; two new cases on the shared `base/`, invented entries from
TD-161 up: a `; no board item` lift with one covering item at the base and a second added at the head (both ids,
in id order), and a lift with no suffix and no item covering the gate at the base or the head (the `no item asks
it` ending).

**Suite tests** in `tests/test_ledgerboard.py`: the clause's grammar for one and several items; `near`'s shape
and order; an item with no id left out (a v2 board line), the context then today's.

## Consumers

None needs a change. The clause rides in the item the host files from `to_file`; `near` is an added key a host
may show; the two flags keep their kinds. Each consumer takes the release by its vendor PR. On Go, a line to
ShiftLead's question seat offers showing `near` as a link from the new item to the old (`ao td add --repo
shiftlead`), its own to take or leave.

## Builds (filed on Paul's go)

- **B1** D2: `tripwire()`'s two texts, the SPEC sentence in *The merge gate's verdicts*, the verdict fixtures and
  cases above.
- **B2** D1 and D3: `sweep()`'s near items, its `near` key and the clause, the SPEC text in *The gate sweep* and
  *The decide lift*, the `near` sweep cases and their harness, the suite tests; with *Versions*' v3.6 paragraph
  (B1's PR adds it if B1 lands first, naming its half, and B2 completes it).

Both are minor and may share one release.

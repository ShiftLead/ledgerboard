# TD-152: the gate sweep points at the item that already names the entry, and the tripwire names its items

**Status:** Draft 2, 2026-11-21 (session lb-designer). Class: **wide** (a change to the published, vendored
format: what `sweep()` files and returns, and the text of two `tripwire()` flags; cap 6 rounds, cadence.md §4.8).
Round 1 raised 7 build-changing findings (applied); round 2 next. The record: [docs/reviews/TD-152.md](../reviews/TD-152.md). In plain words:
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
first reads the **near items** of that entry and gate. An item **names the entry** when one of its Context's refs
is the entry as that board reads refs (a bare `TD-n` on this repo's own board, `<repo>#TD-n` naming this repo on
any board, compared as `ref_key()` compares), or its Context names the entry's `Part of` parent and its `Parts:`
lists the entry: `_names_entry()`'s two tests, without the gate and the qualifier. A near item is each open item
(state `open` or `decided`) on any board read, of any kind but `fyi`, that names the entry, that `covers()` does
not find for the gate, and that is neither of:
- **about another gate**: its Context names exactly one entry and exactly one gate, and that gate's `_gate_key()`
  is not this gate's (a `decide` for the entry's event, or for its parent's event with the entry among `Parts:`);
- **the sweep's own**: its Context names one entry and this gate (by `_gate_key()`) and either goes on with `lift`
  or `board <repo>`, or the item's words hold one of the sweep's fixed words (`has no board`, `Event check
  broken`, `can no longer happen`, `Still waiting on`, `holds no decided item`, `was answered with a lift`, read in
  the item's words as *One filing rule* reads them) and it is of the kind the sweep files with them. The
  `has no board` act, keyed `TD-n decision (<p>)` with nothing after, is the case that matters: the sweep closes it
  itself once the gate is covered.

What is left asks the person about the entry in a form no answer lifts the gate through: an `act` (keyed to the
gate or not), a `decide` naming several entries, no gate or several gates, a `decide` keyed to the gate on a board
whose `People:` does not list `<p>`, or a `decide` whose Context goes on past the gate (`TD-4 decision (pat) —
design ready`, which SPEC already reads as naming no entry here).

With any near item, the decide is filed all the same, and its detail block's context (the entry's `**Context:**`,
else today's sentence, then the `unusable` clause where today's sweep writes it) ends with one more clause naming
them, a single trailing `.` of the context dropped before it:
`; <named> also <name|names> <ref>, but only an answer here lifts <gate>`. `<named>` is `item <id>`, or
`items <id>, <id>…` ordered by id, then by board name (bytewise); an item on a board other than the one the decide is filed on is followed by
` on <board>`, the board named as the sweep names boards (`origin_key`, else the basename). `<ref>` is the entry
as the filed item's Context spells it (`TD-n`, or `<repo>#TD-n` on another repo's board), `<gate>` as the entry
spells it. An item with no id (a v2 line with no readable date) is not named; when every near item lacks one, the
context is today's.

`sweep()` also returns them, as a new key: `near`, a list with one record per decide it files that has named
near items, `{id, gate, board, items}`: `id` the entry's `TD-n`, `gate` as the entry spells it, `board` the board
filed on, `items` a list of `[board, item id]` in the clause's order. One record per decide filed, so a gate written
twice files and records once (as `to_file` does); in entry-number order, then the entry's gate order. The key is
always present, `[]` when there are none. A host may show it (a link from the new item to the old); it changes nothing
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
  base nor at the head, ` (no item covers it: log the lift with the suffix ; no board item)`. Only this repo's
  board is read, as today.

`<ids>` are those items' ids, each once, in id order, joined by `, `. An item with no id is left out, and when
every covering item lacks one the text is today's. The flags' kinds, and when each is raised, are unchanged;
`lift_pr_verdict()`'s `flags` are `tripwire()`'s, so they carry the same text.

### D3. Only a covering item's answer counts at the merge gate

The report's third ask is settled as no change to what lifts, stated in SPEC so no reader expects otherwise. The
tripwire counts a lift by answer only through an item `covers()` finds (*The merge gate's verdicts*):
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

**A difference this design does not settle.** The decide lift (`decide_lift()`, and the board writer's decide)
accepts two items `covers()` does not find: a `decide` whose Context goes on past the gate (`_context_gate()`
reads `TD-4 decision (pat) — design ready` as one entry and one gate), and a `decide` on a board with no
`People:` (its board checks skipped). An answer there writes the lift, and the tripwire then flags it
`tripwire-no-decided`, which D2 now makes name the covering item. Whether the writer should refuse those items is
its own question, filed on Go as its own `design-first` entry rather than widened into this one.

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

> **Near items** (v3.6). Before filing the decide, the sweep reads the entry's near items for the gate. An item
> names the entry when one of its Context's refs is the entry as that board reads refs, or its Context names the
> entry's `Part of` parent and its `Parts:` lists the entry. A near item is an open item (state `open` or
> `decided`) on any board read, of any kind but `fyi`, that names the entry and that `covers()` does not find for
> the gate; except an item whose Context names exactly one entry and one gate other than this one, and an item of
> the sweep's own for this entry and gate (its Context going on with `lift` or `board <repo>`, or its words holding
> one of the fixed words of *One filing rule* or `was answered with a lift`, in the kind the sweep files with
> them). Gates compare as their keys, refs case-insensitively. Such an item asks about the entry in a form whose
> answer the merge gate does not count (below). With any that has an id, the decide is filed all the same and its
> detail block's context, after any clause the sweep already adds, a single trailing `.` dropped, ends `; <named>
> also <name|names> <ref>, but only an answer here lifts <gate>`: `<named>` is `item <id>`, or `items <id>,
> <id>…` ordered by id, then board name, each followed by ` on <board>` when on a board other than the one filed
> on (named as the sweep names boards); `<ref>` is the entry as the filed item's Context spells it, `<gate>` as
> the entry spells it. An item with no id is not named. `near` holds one record per decide so filed, `{id, gate,
> board, items}`: the entry's `TD-n`, the gate as the entry spells it, the board filed on, and `items`, the named
> items as `[board, item id]` in the clause's order; in entry-number order, then the entry's gate order; `[]` when
> there are none. Nothing else about the decide changes, and no near item is read when no decide is filed.

In *The gate sweep*, after the `covers(…)` paragraph's last sentence (*Only `open` and `decided` cover.*):

> Only an item `covers()` finds counts toward a lift at the merge gate (v3.6 says so; no release did otherwise): an
> `act`'s `done` records no answer, and an answer on a `decide` naming several entries, or the entry with no gate,
> lifts none of them there. A lift resting on such an item is an override (`lift_gate(…, override=)`), which
> review reads.

In *The merge gate's verdicts*, after the sentence listing the other flags (*… `tripwire-shared-decided` (v2.7)
and `tripwire-board`.*):

> From v3.6 (TD-152) two flags name their items: `tripwire-no-board-item`'s text ends ` (<ids>)`, and
> `tripwire-no-decided`'s ` (asked by <ids>)`, `<ids>` the ids of the items covering the gate (states `open`,
> `decided`) on this repo's board at the base or the head, each once, in id order, joined by `, `;
> `tripwire-no-decided`'s ends instead ` (no item covers it: log the lift with the suffix ; no board item)` when
> none covers it at either. An item with no id is
> left out, and when every covering item lacks one the text is as before v3.6.

In *Versions*, after v3.5's paragraphs:

> **v3.6 names what a duplicate question needs** (TD-152; *The gate sweep*, *The decide lift*, *The merge gate's
> verdicts*, *The gate sweep*'s note on what counts): the sweep's decide for an uncovered decision names, in its detail context, the open items that
> already name the entry but cannot lift its gate, and `sweep()` returns them as `near`; `tripwire-no-board-item`
> and `tripwire-no-decided` end naming the covering items' ids. No parse changes, and nothing the sweep files or
> closes changes but that clause; a consumer reading `sweep()`'s three keys, or the two flags by kind, reads as
> before but for the added key.

## Fixtures and tests

**The `near` key in today's sweep outputs.** `sweep_cases` (`fixtures/run.py`) stores `sweep()`'s whole result for
each of `runs` and for `rerun`, so each gains `"near": []`; the `in_flight`, `answers` and `delegated` cases store
named keys and are unchanged.

**Sweep cases** in `fixtures/sweep/near/<case>/`, each its own `ledger.md` and v3 board directory `board/`, and, where
a case says, a second v3 board directory `other/` (invented entries, repo `acme/widgets`). They are listed in
`sweep/cases.json` under `near`, each `{name, dir, today_utc, today_local}` and optionally `other: {url,
basename}`, and expected in `sweep/expected.json`'s `near`, an object keyed by case name. A new harness function,
`near_cases()` beside `in_flight_cases()`, sweeps each with the top-level `repo`, no `results` and no `resolve`,
over `[(top url, top basename, board/)]`, then `(other url, other basename, other/)` when given, `top` the first
top-level board. `rerun` is the same sweep once the first run's closes are moved and its filings written
(`item_file()`, as `in_flight_cases()` writes them) on each board by its name. Each case's output is `{to_file,
to_close, lifts, near, rerun}`, `rerun` the same four keys. Against a module whose `sweep()` result has no `near`
key (read on the first case), the whole entry is `{"missing": "the module's sweep returns no near — older than
v3.6"}`. Unless said, the entry `TD-n` carries `decision (pat)`, the own board lists `pat`, nothing covers the gate,
and no other ledger entry carries a decision:
1. An open `act`, Context naming `TD-n` and two ids the ledger does not hold, no gate: the decide is filed, its
   context ending `; item <id> also names TD-n, but only an answer here lifts decision (pat)`; `near` names it.
2. An open `decide`, Context `TD-n` alone: the same.
3. An open `decide`, Context `TD-n, TD-m decision (pat)`, `TD-m` not in the ledger: the same.
4. An open `decide` keyed `TD-n decision (pat)` on `other/`, which does not list `pat`: filed on the own board,
   the item named ` on <other>`.
5. An open `decide` whose Context is `TD-n decision (pat) — design ready`: named.
6. An open `act` keyed `TD-n decision (pat)` whose words hold none of the sweep's fixed words: named.
7. Not named, `near` empty and the rest as today: an open `fyi` naming `TD-n`; an open `decide` keyed `TD-n event
   (x)`; a closed `act` naming `TD-n`; an open `has no board` act keyed `TD-n decision (pat)` (four cases; in the
   last the act is also closed, covered by the new decide, on the rerun).
8. Two near items added in the reverse of id order: `items <a>, <b>` in id order.
9. An `act` on `other/` naming `acme/widgets#TD-n`: named, with ` on <other>`.
10. A covering decide open, a near `act` beside it: nothing filed, `near` empty.
11. The entry deferred (a live blocker, v3.5) with a near `act`: nothing filed, `near` empty.
12. The entry with a `**Context:**` section ending in `.`: the clause follows that section's collapsed text, the
    `.` dropped.
13. The entry with refused answers (the `unusable` clause) and a near `act`: the clause comes after it.
14. A part `TD-p` of `TD-n`, `TD-p` carrying `decision (pat)` and `TD-n` none: an open `decide` keyed `TD-n
    event (x)` with `Parts: TD-p` is not named (about another gate); an open `decide` keyed `TD-n decision (pat)`
    with `Parts: TD-p` on `other/`, which does not list `pat`, is named for `TD-p` (two cases; `Parts:` is a
    decide's alone).
15. An entry carrying `decision (pat)` and `decision (sam)`, both listed, one `act` naming the entry: two
    decides, each with the clause; `near` two records, in gate order.

In every case the rerun files nothing further and `near` is empty on it.

**Verdict cases.** `fixtures/verdict/expected.json` holds twelve of the two flags' texts (ten
`tripwire-no-decided`, two `tripwire-no-board-item`); each gains its ending from its own case's covering items,
regenerated by the build and read one by one in its review. Two new cases on the shared `base/`, invented entries
from TD-161 up: a `; no board item` lift with one covering item at the base and a second added at the head (both
ids, in id order), and a lift with no suffix and no item covering the gate at the base or the head (the `no item
covers it` ending).

**Suite tests** in `tests/test_ledgerboard.py`: the clause's grammar for one and several items; `near`'s shape and
order; a v2 board read through `load_board()` holding a near line with a readable date and one without (the first
named, the second not), and a v2 board whose only near line has no id (the context today's); the tripwire's
endings over a v2 board as over a v3 one.

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

Both are minor and may share one release; the release's stamp regenerates `fixtures/MANIFEST`. On Go, beside
them, one `design-first` entry for D3's *difference this design does not settle*.

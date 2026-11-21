# TD-152: the gate sweep points at the item that already names the entry, and the tripwire names its items

**Status:** Draft 4, 2026-11-21 (session lb-designer). Class: **wide** (a change to the published, vendored
format: what `sweep()` files and returns, and the text of two `tripwire()` flags; cap 6 rounds, cadence.md §4.8).
Build-changing findings per round so far: 7, 6, 2 (applied); round 4 next. The record:
[docs/reviews/TD-152.md](../reviews/TD-152.md). In plain words: [docs/synopses/TD-152.md](../synopses/TD-152.md).

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
older one, the merge gate does not count its answer: a lift with no suffix is flagged `tripwire-no-decided` (no
item covering the gate gains a `Decided:`), and a lift logged `; no board item` is flagged
`tripwire-no-board-item` (the sweep's item covers it). Neither flag names an item (`tripwire()`'s two messages
name the entry and the gate alone), so the session found the second item by a search.

The reported case, on samscrape's board: an older open `act` whose Context named the entry among two others and
no gate; the sweep's `decide` beside it; the person's `done` on the act.

## What is already settled

- **One question per gate.** The tripwire counts a lift by answer on this repo's board only through an item
  `covers()` finds (*The merge gate's verdicts*). One question for several entries is the parent's item with a
  `Parts:` snapshot (v2.6), the end-of-rounds item's form (cadence.md §4.8).
- **The sweep never rewrites an item it did not file, and never one it filed** (*One filing rule*).
- **A lift that rests on something other than a covering item's answer is an override** (`lift_gate(…,
  override=)`, its why required; the tripwire accounts for it by its `override:` Log line), which review reads.
- **An `act`'s close records no answer**: `done` writes `Closed:` and a why, never `Decided:` (*Edits*).

## The design

### D1. The sweep names the near items in the decide it files

When the sweep files a `decide` for an uncovered `decision (<p>)` (every condition of today's bullet met), it
first reads the **near items** of that entry and gate.

**Names the entry.** An item names the entry when one of its Context's refs (every `REF_TD_RE` match, read as that
board reads refs: a bare `TD-n` on this repo's own board, `<repo>#TD-n` naming this repo on any board; `_ours()`)
is the entry, or one of them is the entry's `Part of` parent and one of its `Parts:` ids, read the same way, is the
entry. This is a reading on refs, wider than `_names_entry()`, which needs the Context to key one entry and one
gate: a gateless or multi-entry Context counts here.

**Near.** A near item is each open item (state `open` or `decided`) on any board read, of any kind but `fyi`, that
names the entry, that `covers()` does not find for the gate, and that is neither of:
- **about another gate**: its Context names exactly one gate (`CONTEXT_ANY_GATE_RE`'s matches, counted once per
  `_gate_key()`), whatever the entries, and that gate's `_gate_key()` is not this gate's (a `decide` for the entry's event; an
  `act` about two entries' `event (release)`);
- **the sweep's own**: its Context names exactly one entry, that entry, and this gate (by `_gate_key()`), and
  either goes on after the gate with `lift` or `board <repo>` (`_sweep_context()`'s qualifier), or its
  `_sweep_head()` (the first of `SWEEP_HEADS`' fixed words its words hold, as *One filing rule* reads them) is set
  and `SWEEP_KINDS` of that head is its kind. The `has no board` act, keyed `TD-n decision (<p>)` with nothing
  after, is the case that matters: the sweep closes it itself once the gate is covered.

What is left asks the person about the entry in a form whose answer the merge gate does not count: an `act`
(keyed to the gate or not, its words not the sweep's), a `decide` naming several entries or no gate, a `decide`
keyed to the gate on a board whose `People:` does not list `<p>`, or a `decide` whose Context goes on past the gate
with other words (`TD-4 decision (pat) — design ready`).

**The clause.** With any near item that has an id, the decide is filed all the same, and its detail block's
context ends with one more clause naming them. The context is first assembled as today (the entry's
`**Context:**`, whitespace collapsed, else today's sentence; then the `unusable` clause where today's sweep writes
it); if the assembled string ends in `.`, that one `.` is dropped; then the clause is appended:
`; <named> also <verb> <ref>, but only an answer here is counted when <gate> is lifted`.
- `<named>` is `item <id>` for one, `items <id>, <id>…` for several, ordered by id, then by board name
  (both bytewise); each id is followed by ` on <board>` when its board is not the one the decide is filed on, the board
  named as the sweep names boards (`origin_key`, else the basename): `items A on b, C`.
- `<verb>` is `names` for one item, `name` for several.
- `<ref>` is the entry as the filed item's Context spells it (`TD-n` on this repo's own board, `<repo>#TD-n` on
  another); `<gate>` as the entry spells it.
- An item with no id (a v2 line with no readable date) is not named; when no near item has one, the context is
  today's.
- Today's sentence (*… waits on <gate>, and no board item asked for it*) is kept as it is when the clause follows
  it: the clause qualifies it. The ids and the board name are the package's longer text; a consumer's rules for
  text a person reads apply where it shows it, as for the `was answered with a lift` act's text. The person who
  acts is the one answering this item, which the clause's *here* names.

**`near`.** `sweep()` returns a new key, always present: `near`, a list with one record per decide it files whose
clause names items, `{id, gate, board, items}`: `id` the entry's `TD-n`, `gate` as the entry spells it, `board` the
board filed on, `items` a list of `[board, item id]` in the clause's order. One record per decide filed, so a gate
written twice files and records once (as `to_file` does); in entry-number order, then the entry's gate order; `[]`
when there are none. A host may show it (a link from the new item to the old); it changes nothing the sweep writes.

**Why file and not hold.** A near item's answer is not counted (D3), so holding the decide while one is open
would leave the gate with no question that can end it for as long as the near item stays open, and an `act` that
merely mentions the entry (*TD-5 and TD-6 wait on the release*) would silence it. Filed with the clause, the new
item tells the person which answer counts, and the old one stays theirs to close.

Nothing else changes: whether the decide is filed, on which board, its text, answers, Context and identity are
today's; near items are read only when the decide is filed (never for the `has no board` act, never while the
decision is covered, held, deferred or within a window); the rerun over the sweep's own writes files nothing,
since the filed decide covers the gate.

### D2. The tripwire's two flags name the items they mean

`tripwire-no-board-item` and `tripwire-no-decided` name the covering items, by id, so a person or session can act
without a search. Only this repo's board is read, as today:
- `tripwire-no-board-item`'s text ends ` (<ids>)`, the ids of the items `covers()` finds covering the gate
  (states `open`, `decided`) on this repo's board at the base or the head;
- `tripwire-no-decided`'s text ends ` (asked by <ids>)`, the same items; or, when no item covers the gate at the
  base nor at the head, ` (no item on this repo's board covers it: log the lift ; no board item, or ; board <repo>
  for an answer on another repo's board)`.

`<ids>` are those items' ids, each once, in id order (bytewise), joined by `, `. An item with no id is left out,
and when every covering item lacks one the text is today's. The flags' kinds, and when each is raised, are
unchanged; `lift_pr_verdict()`'s and `ledger_lift_verdict()`'s `flags` are `tripwire()`'s, so they carry the same text.

D2 is also the remedy for the reported path, which D1 does not reach: the person answering the old item first.
The session that then tries the lift is told which item does count.

### D3. Only a covering item's answer counts at the merge gate

The report's third ask is settled as no change to what lifts, stated in SPEC so no reader expects otherwise. The
tripwire counts a lift by answer on this repo's board (a `gate lifted … answer` line with no suffix, or with `;
shared board item left open`) only through an item `covers()` finds; a reassign, an override, `; no board item`
and `; board <repo>` are accounted for by their own rules, as today:
- **An item naming several entries does not lift one of them by an answer that names it.** One question for
  several entries already has a form, the parent's `decide` with `Parts:`, which the decide lift, `closes()`, the
  carve-out's (b) and the tripwire's shared-item rules each read. A second form, a free Context list with a
  per-answer `--lift TD-n` on the board writer's `decide`, would make what an answer lifts depend on a choice the
  person's press does not show, and each of those readers would need a second reading.
- **An `act`'s `done` never lifts a gate.** It records that a step was done, with no label and no `Decided:`, so
  there is no answer to carry and no `Lifts:` to read it against.
- **Where the person did mean a near item's answer to lift the gate**, the lift is an override (`set … --override
  "<why, naming the item and the answer>"`, from the person's own session in agent-cadence's rules), which review
  reads; the sweep then closes its own decide once the gate is gone (*The close rule*).

**A difference this design does not settle.** The decide lift (`decide_lift()`, and the board writer's decide)
accepts two items `covers()` does not find: a `decide` whose Context goes on past the gate (`_context_gate()`
reads `TD-4 decision (pat) — design ready` as one entry and one gate), and a `decide` on a board with no
`People:` (its board checks skipped). An answer there writes the lift, and the tripwire then flags it
`tripwire-no-decided`, which after D2 names the covering item, or says none covers it. Whether the writer should
refuse those items is its own question, filed on Go as its own `design-first` entry rather than widened into this
one.

### Limits accepted

- A near item opened after the decide is filed is not named, and a named one closed later leaves the clause
  stale: the sweep never rewrites an item it filed.
- An item that merely mentions the entry (an `act` about a release that several entries wait on, with no gate) is
  named as near. The clause says only that its answer is not counted, which is true of it too.
- D1 reaches the person who sees the new item first; the person who answers the old one first is D2's case.
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

In *The gate sweep*, the `sweep(…)` paragraph's return clause, today *returns `{to_file: {board: [item]},
to_close: {board: [item id]}, lifts: [{id, gate, kind, evidence}]}`, `to_close` listing ids (v3.0)*, becomes:

> returns `{to_file: {board: [item]}, to_close: {board: [item id]}, lifts: [{id, gate, kind, evidence}], near:
> [{id, gate, board, items}]}`, `to_close` listing ids (v3.0) and `near` the near items (v3.6, below)

In *The gate sweep*, after the `covers(…)` paragraph's last sentence (*Only `open` and `decided` cover.*):

> Only an item `covers()` finds counts toward a lift by answer on this repo's board (a `gate lifted … answer`
> line with no suffix, or with `; shared board item left open`; v3.6 says so, and no release did otherwise): an
> `act`'s `done` records no answer, and an answer on a `decide` naming several entries, or the entry with no gate,
> is not counted for any of them. A lift resting on such an item is an override (`lift_gate(…, override=)`),
> which review reads.

In the `decision (<p>)` bullet, after *else it is the sentence earlier releases wrote.*:

> **Near items** (v3.6). Before filing the decide, the sweep reads the entry's near items for the gate. An item
> names the entry when one of its Context's refs, read as that board reads refs, is the entry, or is the entry's
> `Part of` parent while one of its `Parts:` ids, read the same way, is the entry. A near item is an open item
> (state `open` or `decided`) on any board read, of any kind but `fyi`, that names the entry and that `covers()`
> does not find for the gate; except an item whose Context names exactly one gate, not this one, and an item of
> the sweep's own for this entry and gate: its Context names exactly that one entry and this gate, and either goes
> on after the gate with `lift` or `board <repo>`, or its words hold any of the sweep's fixed words (those of *One
> filing rule*, then `was answered with a lift`, taken in that order) and the item is of the kind the sweep files
> with the first it holds. Gates compare by their keys, and a Context's gates are counted once per key; refs are
> read as the sweep reads an item's Context entry (a bare `TD-n` on this repo's own board, `<repo>#TD-n` naming
> this repo on any). Such an item asks about the entry in a form whose answer the merge gate does not count
> (above). With any that has an id, the decide is filed all the same, and its detail block's context, assembled as
> before (with any clause the sweep already adds), a single trailing `.` of it dropped, ends `; <named> also
> <verb> <ref>, but only an answer here is counted when <gate> is lifted`: `<named>` is `item <id>`, or `items
> <id>, <id>…` ordered by id, then board name (both bytewise), each followed by ` on <board>` when on a board other than
> the one filed on (named as the sweep names boards); `<verb>` is `names` for one item, `name` for several;
> `<ref>` is the entry as the filed item's Context spells it, `<gate>` as the entry spells it. An item with no id is
> not named. `near` holds one record per decide so filed, `{id, gate, board, items}`: the entry's `TD-n`, the gate
> as the entry spells it, the board filed on, and `items`, the named items as `[board, item id]` in the clause's
> order; in entry-number order, then the entry's gate order; `[]` when there are none. Nothing else about the
> decide changes, and no near item is read when no decide is filed.

In *The merge gate's verdicts*, after the sentence listing the other flags (*… `tripwire-shared-decided` (v2.7)
and `tripwire-board`.*):

> From v3.6 (TD-152) two flags name their items: `tripwire-no-board-item`'s text ends ` (<ids>)`, and
> `tripwire-no-decided`'s ` (asked by <ids>)`, `<ids>` the ids of the items covering the gate (states `open`,
> `decided`) on this repo's board at the base or the head, each once, in id order (bytewise), joined by `, `;
> `tripwire-no-decided`'s ends instead ` (no item on this repo's board covers it: log the lift ; no board item, or
> ; board <repo> for an answer on another repo's board)` when none covers it at either. An item with no id is left
> out, and when every covering item lacks one the text is as before v3.6.

In *Versions*, after v3.5's paragraphs:

> **v3.6 names what a duplicate question needs** (TD-152; *The gate sweep*, *The merge gate's verdicts*): the
> sweep's decide for an uncovered decision names, in its detail context, the open items that already name the
> entry but whose answer is not counted for its gate, and `sweep()` returns them as `near`; `tripwire-no-board-item`
> and `tripwire-no-decided` end naming the covering items' ids; and SPEC says which answers the merge gate counts.
> No parse changes, and nothing the sweep files or closes changes but that clause; a consumer reading `sweep()`'s
> three keys, or the two flags by kind, reads as before.

## Fixtures and tests

**The `near` key in today's sweep outputs.** `sweep_cases` (`fixtures/run.py`) stores `sweep()`'s whole result for
each of `runs` and for `rerun`, so each gains `"near": []`; the `in_flight`, `answers` and `delegated` cases store
named keys and are unchanged.

**Sweep cases** in `fixtures/sweep/near/<case>/`, each its own `ledger.md` and v3 board directory `board/` (this
repo's own board), and, where a case says, a second v3 board directory `other/` (invented entries, repo
`acme/widgets`). They are listed in `sweep/cases.json` under `near`, each `{name, dir, today_utc, today_local}` and
optionally `other: {url, basename}`, and expected in `sweep/expected.json`'s `near`, an object keyed by case name.
A new harness function, `near_cases()` beside `in_flight_cases()`, sweeps each with the top-level `repo`, no
`results` and no `resolve`, over `[(top url, top basename, board/)]`, then `(other url, other basename, other/)`
when given, `top` the first top-level board. `rerun` is the same sweep once the first run's closes are moved and
its filings written (`item_file()`, as `in_flight_cases()` writes them) on each board by its name. Each case's
output is `{to_file, to_close, lifts, near, rerun}`, `rerun` the same four keys. Against a module whose `sweep()`
result has no `near` key (read on the first case), the whole entry is `{"missing": "the module's sweep returns no
near — older than v3.6"}`. Unless said, the entry `TD-n` carries `decision (pat)`, the own board's `People:` lists
`pat`, nothing covers the gate, and no other ledger entry carries a decision. A board that "does not list `pat`"
has a `People:` line naming someone else (a board with no `People:` is D3's other case):
1. An open `act`, Context naming `TD-n` and two ids the ledger does not hold, no gate: the decide is filed, its
   context ending `; item <id> also names TD-n, but only an answer here is counted when decision (pat) is lifted`;
   `near` names it.
2. An open `decide`, Context `TD-n` alone: the same.
3. An open `decide`, Context `TD-n, TD-m decision (pat)`, `TD-m` not in the ledger: the same.
4. The own board does not list `pat`; `other/` lists it. An open `decide` keyed `TD-n decision (pat)` on the own
   board: the decide is filed on `other/`, Context `acme/widgets#TD-n decision (pat)`, the item named ` on <own
   board>` and `<ref>` `acme/widgets#TD-n`.
5. An open `decide` whose Context is `TD-n decision (pat) — design ready`: named.
6. An open `act` keyed `TD-n decision (pat)` whose words hold none of the sweep's fixed words: named.
7. Not named, `near` empty and the rest as today: an open `fyi` naming `TD-n`; an open `decide` keyed `TD-n event
   (x)`; an open `act` naming `TD-n` and `TD-q` with Context gate `event (release)`; a closed `act` naming `TD-n`;
   an open `has no board` act keyed `TD-n decision (pat)` (five cases; in the last the act is closed on the
   rerun, the gate now covered).
8. Two near items added in the reverse of id order: `items <a>, <b>` in id order, verb `name`.
9. An `act` on `other/` (not listing `pat`) naming `acme/widgets#TD-n`: named, with ` on <other>`.
10. A covering decide open, a near `act` beside it: nothing filed, `near` empty.
11. The entry deferred (a live blocker, v3.5) with a near `act`: nothing filed, `near` empty.
12. The entry with a `**Context:**` section ending in `.`, a near `act`: the clause follows that section's
    collapsed text, the `.` dropped.
13. The entry with refused answers (the `unusable` clause) and a near `act`: the clause comes after it; and the
    same with a `**Context:**` section ending in `.`: `….; its own answers could not be offered (…); item …`, the
    section's `.` kept, since the assembled string ends in `)` (two cases).
14. A part `TD-p` of `TD-n`, `TD-p` carrying `decision (pat)` and `TD-n` none, both boards listing `pat` but where
    said: an open `decide` keyed `TD-n event (x)` with `Parts: TD-p` is not named (about another gate); an open
    `decide` keyed `TD-n decision (pat)` with `Parts: TD-p` on `other/`, which here does not list `pat`, Context and
    `Parts:` written `acme/widgets#…`, is named for `TD-p`; an open `decide` whose Context is `TD-n` alone, no gate, with `Parts: TD-p`
    on the own board: named for `TD-p` (three cases; `Parts:` is a decide's alone).

Cases 3 and 14 hold items `item_file()` refuses to write (a gate with several entries; `Parts:` on a Context that
is not one entry and one decision; a qualified `Parts:`), which a person or an older writer can leave on a board
and `load_board()` reads: their files are written by hand.
15. An entry carrying `decision (pat)` and `decision (sam)`, both listed, one `act` naming the entry: two
    decides, each with the clause; `near` two records, in gate order.

In every case the rerun files nothing further and `near` is empty on it.

**Verdict cases.** `fixtures/verdict/expected.json` holds twelve of the two flags' texts (ten
`tripwire-no-decided`, two `tripwire-no-board-item`); each gains its ending from its own case's covering items,
(three under `verdict`, seven under `ledger_lift`, the rest under `tripwire`) regenerated by the build and read one
by one in its review. Two new cases in `cases.json`'s `tripwire` list, each an overlay on the shared `base/` with
its own invented entries, TD-191 and TD-192 (ids no case uses yet): a `; no board item` lift with one covering item at the base and a second added at the head (both
ids, in id order), and a lift with no suffix and no item covering the gate at the base or the head (the `no item
on this repo's board covers it` ending).

**Suite tests** in `tests/test_ledgerboard.py`: the clause's grammar for one and several items, mixed boards; `near`'s
shape and order; a v2 board read through `load_board()` holding a near line with a readable date and one without
(the first named, the second not), and a v2 board whose only near line has no id (the context today's); the
tripwire's endings over a v2 board as over a v3 one.

## Consumers

None needs a change. The clause rides in the item the host files from `to_file`; `near` is an added key a host
may show; the two flags keep their kinds. Each consumer takes the release by its vendor PR. On Go, a line to
ShiftLead's question seat offers showing `near` as a link from the new item to the old (`ao td add --repo
shiftlead`), its own to take or leave.

## Builds (filed on Paul's go)

- **B1** D2: `tripwire()`'s two texts, the SPEC sentence in *The merge gate's verdicts*, the verdict fixtures and
  cases above.
- **B2** D1 and D3: `sweep()`'s near items, its `near` key and the clause, the SPEC text in *The gate sweep*, the
  `near` sweep cases and their harness, the suite tests; with *Versions*' v3.6 paragraph (B1's PR adds it if B1
  lands first, naming its half, and B2 completes it).

Both are minor and may share one release; the release's stamp regenerates `fixtures/MANIFEST`. On Go, beside
them, one `design-first` entry for D3's *difference this design does not settle*.

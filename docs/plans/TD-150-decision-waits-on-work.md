# TD-150: the gate sweep asks a decision once the work it waits on is done

**Status:** Draft 7, 2026-11-18 (session lb-designer). Class: **wide** (a change to the published, vendored
format: what `sweep()` files and what `uncovered_decisions()` refuses; cap 6 rounds, cadence.md §4.8). The rounds
ended by the stop rule after round 5: build-changing findings per round 4, 3, 1, 1, 0; the closing fact-check 0 (two minors applied). The author recommends Go. The record: [docs/reviews/TD-150.md](../reviews/TD-150.md). In plain words:
[docs/synopses/TD-150.md](../synopses/TD-150.md).

**Entry:** [TD-150](../ledger/archive/TD-150.md), asked for by agent-cadence's grinder for its TD-291 (a bought review
round holds its design as `**Blocked by:** TD-<round>, decision (<person>)` while it runs).

## The problem

`sweep()` files a `decide` item for an open entry's `decision (<p>)` gate whatever else its `**Blocked by:**`
names (SPEC *The gate sweep*, the `decision (<p>)` bullet; `ledgerboard/__init__.py`, `sweep()`'s
`gate.startswith("decision ")` branch). It checks four things: an item `covers()` finds open or decided, an item
answered without a lift within `reask_days`, a `kept waiting` Log line within it, and an answer owing a lift. It
never reads the gate's other items.

agent-cadence's TD-291 (built 2026-11-18, its cadence.md §4.8) makes the case common. When the person answers
`One more round` on a design's end-of-rounds item, the item closes and the bought round is filed as an entry of
its own (not `Part of` the design: a parent's Blocked by names no part, §2.4), and the design becomes
`**Blocked by:** TD-<round>, decision (<person>)` until the round ends and writes the next end-of-rounds item by
hand. `One more round` lifts nothing, so the closed item keeps the sweep quiet for `reask_days` (30) only. A round
that runs longer (rounds wait on reviewers, on the person's other answers, on a usage reset) has the sweep file
the design's decide again mid-round, with `Answers: Go | Not yet` or the entry's own: a question that cannot be
answered yet. A `Go` on it lifts only the decision; the design stays Blocked by the round and is not built
(agent-cadence's cadence.md §4.8 says so for the interim), but the round's end must then add the gate back before
its end-of-rounds item. The sharper harm is the held builds: the item the sweep files has no `Parts:`, so each
build `Part of` the design, held by its own `decision (<p>)`, is asked on its own once the window lapses, and a
`Go` on one of those frees that build, blocked by nothing else, before the round's reviews have read the fixes
the round was bought for (F1).

The merge gate has the same shape: `uncovered_decisions()` refuses (`decision-uncovered`) a PR in which an open
entry gains `decision (<p>)` with no covering item on this repo's board, whatever else blocks it. A PR that files
a new entry already held by an open one and a decision is made to file the very question the sweep must not ask.

## What is already settled

- **What blocks is one reading.** `pickable()` reads every Blocked by id one way (SPEC *The ledger*, *Superseded
  and dropped*): a live entry blocks; an archived one releases only when it, or the end of its Superseded chain, is
  Resolved; a `<repo>#TD-n` is answered by the caller's `resolve`, and without one, or unanswered, keeps the
  block. `_chain()` follows an id through Superseded entries and names where it ends: `open`, `resolved`,
  `dropped`, `unknown-status`, `unknown`, `unresolved` or `cycle`.
- **A design's held builds are its open parts.** cadence.md §4.8: while a design waits on its end-of-rounds item,
  its builds may be filed held, each `**Part of:** TD-<plan>` and listed on the item's `Parts:`, so a design asking
  its go has open parts by design. TD-291 files the bought round as a blocker, not a part.
- **The sweep keeps no state** and reads only the texts and boards it is given; the module reads no other repo, so
  another repo's entry is known only through a resolver the caller passes, as `pickable()` takes one.
- **The close rule** closes a decide only when its gate is gone; an item the sweep filed is never rewritten.
- **The round's end files its own item.** TD-291 has the round's end write the new end-of-rounds item by hand and
  drop `TD-<round>` from the design's Blocked by in the same write; the sweep is the backstop, not the asker.

## The design

### D1. A blocker in flight defers the decision's ask

**Open, for this rule.** Each function reads an entry as open the way it already does, and the rule uses that
reading: `sweep()` reads an entry of `entries` as open unless its Status is an archived word (*The gate sweep*);
`uncovered_decisions()` reads the head tree's ledger through `_tree_ledger()`, where an entry in the ledger with an
archived Status, and every entry of the archive, is closed. The archived entries are every other entry the
function reads, each Status read as *Superseded and dropped* reads it (`_archived_status()` over their texts). The sweep reads open by Status alone, so an
entry of the archive whose Status word is not an archived one (`ARCHIVED_WORDS`) is open to it: a word outside the
vocabulary, the empty Status, and the words *Superseded and dropped* reads as closed and done on an archived entry
(`Open`, `Designed`, `Built`, `Partly`, `Live`, `In`). For the sweep, then, `unknown-status` is an end only the
resolver reaches. That is the one shape on which the two readings differ: open to the sweep, so in flight there;
closed to the verdict. It is accepted, since `check()` already flags such a Status on an archived entry (`status`; an error on a
v2 ledger), and its cure is SPEC *The closed Status set*'s: the Status rewritten by hand to `Resolved YYYY-MM-DD`,
then `ledger.py fmt TD-n`. But the deferral holds while it stands, so a repo whose archive still holds one is asked
nothing about an entry blocked by it until it is cured. An entry of the ledger with an archived Status is closed to both, though `pickable()`,
which reads by place, still blocks on it: its decision is asked while the entry stays unpicked, as a `check()`
flag on the misplaced entry already asks for its move.

A Blocked by id of an open entry is **in flight** when `_chain()` (the walk `pickable()` makes through Superseded
entries, over the open numbers and archived statuses just named) ends `open`: at an open entry of this ledger, at
a `<repo>#TD-n` the resolver answers `open`, or at the end of a Superseded chain that reaches either. Every other
end is not in flight: `resolved`, `dropped`, `unknown-status`, `unknown` (no such entry), `cycle` and `unresolved`
(a `<repo>#TD-n` no resolver answers, or a Superseded entry with no successor). An id whose chain ends at the entry itself,
at one of its descendants (an entry `Part of` it, or of one of them), or at one of its ancestors (its `Part of`
parent and theirs) never counts (descendants and ancestors read over the open entries' `Part of`; the comparison is by
number and only for a local end, one with no `#` in the path's last id, so another repo's `#TD-5` is never
entry TD-5). Written directly, `pickable()` flags it (`cycle` for the entry itself or an
ancestor, `legacy-part` for a descendant), and the cure is to drop it from the Blocked by; reached through a
Superseded chain it is excluded with no flag of its own beyond `blocker-superseded`. Two open entries blocked on each other, each with a decision, defer each other until one is
archived; that is accepted, since `pickable()` flags the `cycle` and neither entry can go on anyway.

One helper decides it, so the sweep and the verdict cannot drift: **`_deferred(num, gate, open, gone, resolve,
cross_open=False)`** over an entry's number, the decision gate, the open entries' texts by number, the archived
entries' statuses (`_archived_status()`'s form) and the resolver, returning the in-flight ids, the entry's own and
then its parent's (D2, only when the parent carries `gate`, compared by `_gate_key()`), in the form and order of D4's flag text (empty: not deferred). `cross_open` counts a chain that ends
`unresolved` at another repo's id (its path's last id holds `#`) as in flight; a Superseded entry with no
successor also ends `unresolved`, at a local id, and does not count. The sweep calls it with its resolver, the
verdict with none and `cross_open=True` (D4), each with its own open reading.

The sweep files no `decide` for a `decision (<p>)` gate while the entry's Blocked by names an id in flight. Once
none is (each archived, or gone from the Blocked by), the bullet's existing four conditions decide, as today: in
TD-291's case the earlier `One more round` answer, if still within `reask_days`, keeps the sweep quiet, and the
round's end has filed its item by hand.

**In flight means open, not running.** A blocker that is itself waiting, on a decision or on an `until` a year
out, defers the ask as long as it is open. That is accepted: the entry cannot go on before its blocker ends
either, and the person's question is asked when it does.

**Why not every block.** A Dropped blocker keeps an entry unpickable until a person decides what replaces it, and
that is a question the person can answer now; a typo id (no such entry) keeps the block and is flagged ⚠
`blocked-unknown` by `check()`, and silencing the entry's question as well would leave it waiting with nothing
asking. So both ask, as today.

**Another repo's id.** `sweep()` gains `resolve`, keyword-only, default `None`, the same callable `pickable()`
takes, answered the same way (`_resolved()`). With no resolver, or one that cannot answer, a `<repo>#TD-n` is not
in flight and the sweep asks, as today. A caller that passes its resolver gets the deferral for another repo's
work too. The sweep calls `resolve` only for a gate it would otherwise file (the four conditions met and a board
found), and a resolver that raises propagates, as in `pickable()`. The reason (agreed with this team's techlead,
2026-11-18): counting an unanswered `<repo>#TD-n` as in flight, the way `pickable()` keeps it blocking, would
silence the question for good wherever nothing can resolve it, so nobody would be asked at all, the worse
failure; and asking costs little, since the `<repo>#TD-n` stays in the entry's Blocked by after a lifting answer,
so the entry itself is still not pickable until that blocker is seen archived.

### D2. A held part defers with its parent

A part's `decision (<p>)` also defers while its `Part of` parent is open, carries the same gate (the person
compared case-insensitively, as `covers()` compares it), and names a blocker in flight (D1, read on the parent: the parent's own id, descendants and ancestors are
the ones excluded, so a sibling part in the parent's Blocked by does not defer it).
This is the held build: cadence.md §4.8 files a design's builds while it waits, each `Part of` the design with its
own `decision (<p>)`, covered by the end-of-rounds item's `Parts:`. Once that item is answered `One more round`
and closed, the window it opens covers the builds too (`covers()` via the parent); when it lapses mid-round, each
build would otherwise get its own `Go | Not yet`, and a `Go` on it lifts the build before the round's reviews have
read its fixes. Only the direct parent is read, one level, as `covers()` reads only the parent. Unlike
`covers()`, D2 does not need the part to be on any item's `Parts:`: it reads the ledger alone.

### D3. What does not defer

- **The entry's own open parts.** A design's held builds are its open parts, and each waits on the design's go,
  so deferring on them would never ask the go.
- **A parent's blockers, otherwise.** A part whose parent does not carry the same gate reads its own Blocked by
  only, as its pickable does.
- **Other gates.** Another `decision (…)`, an `until` not yet reached, and an `event (…)` do not defer: two
  decisions would each wait on the other, and a date or an event is a wait on the world the person's answer may
  not depend on. A repo that wants a question asked only after a date writes the decision once the date comes.
- **The gate's other items.** The `has no board` act (a fault in where the question would go), an `event`'s
  items, the `was answered with a lift` act and the `; board <repo>` audit file as today: each is a fault or a
  record, not a question waiting on the work. The answers owing a lift (`held`) are read as today.
- **An open item.** A decide already open while a blocker is in flight stays open: the sweep closes a decide only
  when its gate is gone, and a person may be answering it. Deferral only withholds filing.

### D4. The merge gate holds the same way

`uncovered_decisions()` reads each open entry's newly gained `decision (<p>)` in this order:

1. covered on this repo's board (today's test): nothing, as today;
2. else **deferred**: `_deferred()` over the head tree's ledger (`_tree_ledger()`), with no resolver and
   `cross_open=True` (the verdict reads no other repo, and a refusal must be the same on every machine), returns
   ids: flagged `decision-deferred` alone, its text exactly
   `<TD-n> gains <gate>, deferred behind <ids> — the sweep asks it once none is in flight`, `<TD-n>` the entry's
   id and `<gate>` as the entry writes it; `<ids>` joined with `, `, the entry's own in-flight ids first, as
   written, in the order written, each once (at its first place), then its parent's (D2) likewise, each written
   `<id> (blocks <parent>)`, `<parent>` the parent's id as its heading writes it; an id in both lists is written in
   each, and two ids are the same when their verbatim text is;
3. else today's rule: refused `decision-uncovered` when the board lists `<p>`, flagged `decision-elsewhere` when
   it does not.

A `<repo>#TD-n` whose work is done is then asked by the sweep, from the caller's resolver or with none (D1), so
the verdict's leniency costs a sweep's delay, never a lost question. It is accepted that writing any
`<repo>#TD-n`, even a finished one, turns the refusal into a flag. The rest of the verdict, `decision-no-lift`
among it, is unchanged.

### Limits accepted

- When the last blocker ends inside the window an earlier non-lifting answer opened, the sweep stays quiet until
  the window ends; the round's end files its item by hand (TD-291), and a missed one waits at most `reask_days`.
- A decision that gains a blocker and later loses it in another PR has no verdict check; the sweep asks it.

## Options set aside

- **Close an open decide when a blocker is added.** It would close a question a person may be answering, and an
  item closed with no answer opens no window, so the sweep would refile it the moment the blocker ends.
- **Defer on every other gate and part** (*ask only the last thing the entry waits on*). It never asks a design's
  go while its held builds are open, and two decisions on one entry deadlock.
- **A `deferred` list in the sweep's result.** It would add a key every consumer reads for a state the entry's own
  Blocked by already shows; the Queue reads the entry.
- **Reset the re-ask window when the blocker ends.** A window that moved with the ledger would make the sweep's
  state its own, which it keeps none of.

## SPEC text

`v3.N` below is the release that carries the build, filled at the release (v3.5 if nothing lands first).

**The gate sweep**, the signature sentence, `repo)` becomes `repo, *, resolve=None)` (`resolve` keyword-only), and
after *`repo` outside the `<repo>` grammar.* is added:

> `resolve` is `pickable()`'s resolver for `<repo>#TD-n` items (v3.N), called only to tell whether a blocker of a
> decision the sweep would otherwise ask is in flight (below); one that raises propagates.

**The gate sweep**, the `decision (<p>)` bullet's first line: *, and not held by an answer owing a lift (below)*
(from its comma) becomes *, not held by an answer owing a lift (below), and not deferred (v3.N, below)*. The bullet's last sentence
ends *…opens the `kept waiting` window as the person's would.* (its `;` becomes `.`), and after it, before the
`until D` bullet, a paragraph inside the bullet, ending in the `;` the bullet ended in:

> A decision is **deferred** (v3.N) while its entry names a **blocker in flight**: an id of its `Blocked by` that,
> followed through Superseded entries as `pickable()` follows it (*Superseded and dropped*), ends at an open
> entry — one of `entries` the sweep reads as open (an entry of `entries`, wherever held, is open unless its
> Status's first word is Resolved, Superseded, Dropped, Done, Moved or OBE, so one with `Built`, `Open`, no Status
> or a word outside the vocabulary is open), or a `<repo>#TD-n` `resolve` answers `open` — and not at
> the entry itself, at one of its descendants (entries `Part of` it, or of one of them) or at one of its
> ancestors, which written directly `pickable()` flags (`cycle`, `legacy-part`). One that ends Resolved, Dropped, at no entry, in a loop, at a
> Superseded entry with no successor, or at a `<repo>#TD-n` no resolver answers is not in flight. A part's
> decision is also deferred while its `Part of` parent, one level up, is open, carries the same gate (its person
> compared case-insensitively) and names a blocker in flight, read on the parent (the parent's own id,
> descendants and ancestors excluded): a held build waits with its design. While deferred, the sweep files no
> `decide` for it, so the question is asked once the work it waits on has ended; the bullet's other conditions
> then decide as before. Nothing else defers it: not the entry's own open parts (a design's held builds wait on its
> decision), nor its other gates. A decide already open stays open (*The close rule*). The `has no board` act is
> filed as before. An entry of the ledger with an archived Status is not open here, though `pickable()`, which
> reads by place, still blocks on it;

**The merge gate's verdicts**, the `uncovered_decisions` paragraph: after *flagged (`decision-elsewhere`) when the
board does not list `<p>`, since its coverage then rests on another repo's board, which not every machine reads.*
is added:

> An uncovered decision that is deferred (*The gate sweep*; v3.N) is neither: it is flagged `decision-deferred`
> alone, exactly `<TD-n> gains <gate>, deferred behind <ids> — the sweep asks it once none is in flight`, `<ids>`
> joined with `, `, the entry's own as written, in the order its `Blocked by` writes them, each once at its first
> place, then its parent's likewise, each `<id> (blocks <parent>)` with `<parent>` as its heading writes it; an id
> in both lists is written in each, and two ids are the same when their verbatim text is. The verdict reads it on the head tree's ledger, where an entry of the archive is
> closed whatever its Status, with no resolver, and counts as in flight, besides an id ending at an open entry,
> any id whose chain ends at a `<repo>#TD-n`, which it cannot resolve; the sweep asks the decision once nothing it
> waits on is in flight.

**Versions**, after v3.4's paragraph:

> **v3.N defers a decision behind its work** (TD-150; *The gate sweep*, *The merge gate's verdicts*): the sweep
> files no `decide` for a `decision (<p>)` while a blocker of its entry, or of a part's parent carrying the same
> gate, is in flight, and takes `resolve` to tell for another repo's ids; `uncovered_decisions()` flags such a
> gained decision `decision-deferred`, a new flag kind, rather than refusing or flagging it as before. The sweep
> files less and the verdict refuses less; no parse, field, Log line, item key or canonical form changes, and a
> caller passing no `resolve` sees another repo's ids as before.

## Fixtures and tests

**Sweep cases** go in a directory of their own, `fixtures/sweep/in_flight/<case>/` (invented entries, repo
`acme/widgets`), each its own `ledger.md`, optional `archive.md`, and one v3 board directory `board/`, swept on one
date apart from the shared runs, as the `answers` and `delegated` cases are (`fixtures/run.py`, `answers_case()`),
so the shared `ledger.md`'s expected output is untouched. They are listed in `sweep/cases.json` under
`in_flight`, each `{name, dir, today_utc, today_local}` and optionally `resolve`; each is swept with the top-level
`repo` and its board under the first top-level board's `url` and `basename`, and their outputs are
`sweep/expected.json`'s `in_flight`, an object keyed by case name (`{"missing": …}` in its place against a module
that cannot run them). A case's `resolve` is a map from a
`<repo>#TD-n` item to the resolver's answer (`[state, why]`, or a record), or the string `"raise"`, which the
harness turns into a callable raising `LookupError`; a map's callable raises `KeyError` for an item not in it, so
no case relies on one. With no `resolve` the sweep is called with none. One case is
one directory and one sweep, so a numbered item below with several variants is several cases, each named. The runner reports `{"missing": …}` against a module whose
`sweep()` takes no `resolve` (`inspect.signature`), as the others guard by `hasattr`. Unless a case says
otherwise, its board holds a closed decide for the gate answered `One more round` (no lift) more than
`reask_days` before the run, on the entry alone (no `Parts:`), so only the new rule keeps the sweep quiet. Each
case's expected output is `{to_file, to_close, lifts, rerun}`, `rerun` the same sweep over the board once the
first run's items are filed (`item_file()`) and its closes moved, which files and closes nothing; a case whose
sweep raises is `{"raised": "<the exception's class name>"}` and nothing else:

1. `decision (pat)` beside a live `TD-n`: files nothing.
2. The same with `TD-n` archived Resolved: files the decide.
3. Beside `TD-n` archived Superseded by a live `TD-m`: nothing; by an archived Resolved `TD-m`: files; Superseded
   with no successor: files.
4. Beside `TD-n` archived Dropped: files. Beside `TD-n` in the archive with a Status word outside the vocabulary,
   and beside one in the archive with Status `Built`: each nothing (open to the sweep, D1; the verdict's cases
   below read them closed).
5. Beside an id in neither ledger nor archive: files.
6. Beside `acme/other#TD-n`: no `resolve`, files; `resolve` answering `open`, nothing; answering `archived` with
   a Resolved status, files; answering garbage (read unresolved), files; raising, `{"raised": "LookupError"}`
(five cases).
7. Beside `TD-n` Superseded by `acme/other#TD-m`: `resolve` answering `open` for it, nothing.
8. Two blockers, one live and one archived Resolved: nothing.
9. The entry's own id in its Blocked by; a part of it there (`legacy-part`); its parent there; an archived `TD-n`
   Superseded by a part of it: each files.
10. A design with `decision (pat)` and two open parts each with `decision (pat)` and nothing else (held builds),
    no Blocked by id on the design, no item on the board: three decides are filed, the design's and each part's,
    as today (D3).
11. The same design also blocked by a live `TD-r` (the bought round), the board holding one closed decide past the
    window whose Context is the design's gate and whose `Parts:` does not list the parts: nothing for the design
    and nothing for either part (D2, not `covers()`).
12. A part with `decision (pat)` whose parent is blocked by a live entry and carries no decision: files (D3).
13. A part with `decision (pat)` whose parent carries `decision (pat)` and, in its Blocked by, only a sibling part
    (`legacy-part` on the parent): the part files (D2, the parent's descendants excluded).
14. Beside an `until` a later day, and beside `event (x)` with no outcome (the `in_flight` cases carry no
    `results`): files as today.
15. An open decide covering the gate, a live blocker in the Blocked by: neither filed nor closed.
16. No board lists `<p>`, a live blocker beside it: the `has no board` act is filed.
17. A closed decide answered with a lift whose gate still stands (an answer owing a lift), a live blocker beside
    it: the `was answered with a lift` act is filed as today.

**Verdict cases** in `fixtures/verdict/`, `uncovered_decisions()`, each an overlay in `cases/` on the shared
`base/` (as the existing `uncovered` cases are), its invented entries numbered from TD-161 up so none meets the
base's, the base tree without the gate and the head tree with it, no item, the board listing `pat` unless said, the expected `(refusals, flags)` with each flag's
exact text: beside a live id, the `decision-deferred` flag and no refusal; beside an archived Resolved id, refused
as today; beside `TD-n` in the archive with a Status word outside the vocabulary, refused (closed to the
verdict), and with Status `Built`, refused; beside `acme/other#TD-n`, flagged deferred; beside a local id Superseded by `acme/other#TD-m`, flagged
deferred; beside two live ids, both named in order; covered by an open item beside a live id, nothing; the board
not listing `pat`, beside a live id, `decision-deferred` alone (no `decision-elsewhere`); a part gaining
`decision (pat)` whose parent carries it and a live blocker, deferred, its text naming `<id> (blocks <parent>)`.

**A suite test**, in `tests/test_ledgerboard.py`, that the two agree: for sweep cases 1, 2, 3, 4 (Dropped only), 5, 8, 9, 11, 12 and 13, each as a
v2 tree for the verdict with a base tree lacking the gate and a board listing `pat`, compared per entry gaining the gate, the
sweep files no decide for that entry's gate exactly when the verdict flags that entry `decision-deferred` and
refuses nothing for it. Left out, each for its reason:
4's unknown Status word and `Built` (the shape D1 accepts as differing), 6 and 7 (another repo's ids, read with a resolver by
the sweep and with none by the verdict), 10 (no blocker either way), and 14 to 17 (what they test has no verdict
counterpart).

## Consumers

agent-cadence (its `scripts/gate_sweep.py`) and ShiftLead, where it calls `sweep()`, each pass the resolver they
pass `pickable()` once they vendor the release; until then another repo's ids are not in flight (D1), as today.
Each also shows the new `decision-deferred` flag where it shows `decision-elsewhere`: as a flag, never a refusal.
The build's Fix names those entries, each to be filed in its own repo through its question seat; agent-cadence's
TD-291 archives once the release is vendored with a test pinning the deferral (its Log, 2026-11-18).

## Builds (filed on Paul's go)

- **B1** D1 to D4 in one PR: `_deferred()`, `sweep()`'s `resolve` and the deferral, `uncovered_decisions()`'s
  `decision-deferred`, the SPEC text above, the fixtures, the harness's `in_flight` cases and the tests above; a
  minor release.

# TD-150: the gate sweep asks a decision once the work it waits on is done

**Status:** Draft 2, 2026-11-18 (session lb-designer). Class: **wide** (a change to the published, vendored
format: what `sweep()` files and what `uncovered_decisions()` refuses; cap 6 rounds, cadence.md §4.8). Round 1:
4 build-changing findings, applied. The record: [docs/reviews/TD-150.md](../reviews/TD-150.md). In plain words:
[docs/synopses/TD-150.md](../synopses/TD-150.md).

**Entry:** [TD-150](../ledger/TD-150.md), asked for by agent-cadence's grinder for its TD-291 (a bought review
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
the design's decide again mid-round, with `Answers: Go | Not yet` or the entry's own; a `Go` pressed on it lifts
the design, and with the end-of-rounds item's `Parts:`, its held builds, before the round's reviews have read the
fixes the round was bought for.

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
function reads, each Status read as *Superseded and dropped* reads it (`_archived_status()` over their texts). The
two readings differ on one shape, an entry under the archive's heading whose Status is not archived (open to the
sweep, closed to the verdict); that is accepted, since the verdict is then the stricter and the sweep's deferral
still holds once the item is filed.

A Blocked by id of an open entry is **in flight** when `_chain()` (the walk `pickable()` makes through Superseded
entries, over the open numbers and archived statuses just named) ends `open`: at an open entry of this ledger, at
a `<repo>#TD-n` the resolver answers `open`, or at the end of a Superseded chain that reaches either. Every other
end is not in flight: `resolved`, `dropped`, `unknown-status`, `unknown` (no such entry), `cycle` and `unresolved`
(a `<repo>#TD-n` no resolver answers, or a Superseded entry with no successor). Two ids never count: the entry's
own id, and an entry that is `Part of` it or of one of its parts (its descendants), which `pickable()` flags
`cycle` and `legacy-part`, and whose cure is to drop them from the Blocked by.

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
compared case-insensitively, as `covers()` compares it), and names a blocker in flight (D1, read on the parent).
This is the held build: cadence.md §4.8 files a design's builds while it waits, each `Part of` the design with its
own `decision (<p>)`, covered by the end-of-rounds item's `Parts:`. Once that item is answered `One more round`
and closed, the window it opens covers the builds too (`covers()` via the parent); when it lapses mid-round, each
build would otherwise get its own `Go | Not yet`, and a `Go` on it lifts the build before the round's reviews have
read its fixes. Only the parent is read, as `covers()` reads only the parent.

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
2. else **deferred**: at the head, the entry (D1) or, for a part, its parent carrying the same gate (D2) names an
   id whose `_chain()` over the head tree's ledger, with no resolver, ends `open`, or reaches a `<repo>#TD-n` (the
   verdict reads no other repo, and a refusal must be the same on every machine): flagged `decision-deferred`
   alone, *`TD-n` gains `decision (<p>)` while `<ids>` is in flight — the sweep asks it once nothing it waits on
   is*, `<ids>` the ids in flight, as written, in the order written;
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

**The gate sweep**, the signature sentence, `repo)` becomes `repo, resolve=None)`, and after *`repo` outside the
`<repo>` grammar.* is added:

> `resolve` is `pickable()`'s resolver for `<repo>#TD-n` items (v3.N), called only to tell whether a blocker of a
> decision the sweep would otherwise ask is in flight (below); one that raises propagates.

**The gate sweep**, the `decision (<p>)` bullet's first line: *and not held by an answer owing a lift (below)*
becomes *, not held by an answer owing a lift (below), and not deferred (v3.N, below)*. After the bullet's last
sentence (*…opens the `kept waiting` window as the person's would;*), before the `until D` bullet, a paragraph
inside the bullet:

> A decision is **deferred** (v3.N) while its entry names a **blocker in flight**: an id of its `Blocked by`, other
> than the entry's own and its descendants' (entries `Part of` it, or of one of them), that, followed through
> Superseded entries as `pickable()` follows it (*Superseded and dropped*), ends at an open entry — one of
> `entries` the sweep reads as open, or a `<repo>#TD-n` `resolve` answers `open`. One that ends Resolved,
> Dropped, with a Status word outside the vocabulary, at no entry, in a loop, at a Superseded entry with no
> successor, or at a `<repo>#TD-n` no resolver answers is not in flight. A part's decision is also deferred while
> its `Part of` parent is open, carries the same gate (its person compared case-insensitively) and names a blocker
> in flight: a held build waits with its design. While deferred, the sweep files no `decide` for it, so the
> question is asked once the work it waits on has ended; the bullet's other conditions then decide as before.
> Nothing else defers it: the entry's own open parts (a design's held builds wait on its decision), and its other
> gates. A decide already open stays open (*The close rule*). The `has no board` act is filed as before.

**The merge gate's verdicts**, the `uncovered_decisions` paragraph: after *flagged (`decision-elsewhere`) when the
board does not list `<p>`, since its coverage then rests on another repo's board, which not every machine reads.*
is added:

> An uncovered decision that is deferred (*The gate sweep*; v3.N) is neither: it is flagged `decision-deferred`
> alone. The verdict reads it on the head tree's ledger with no resolver, and counts as in flight, besides an id
> ending at an open entry, any id whose chain reaches a `<repo>#TD-n`, which it cannot resolve; the sweep asks the
> decision once nothing it waits on is in flight.

**Versions**, after v3.4's paragraph:

> **v3.N defers a decision behind its work** (TD-150; *The gate sweep*, *The merge gate's verdicts*): the sweep
> files no `decide` for a `decision (<p>)` while a blocker of its entry, or of a part's parent carrying the same
> gate, is in flight, and takes `resolve` to tell for another repo's ids; `uncovered_decisions()` flags such a
> gained decision `decision-deferred` rather than refusing or flagging it as before. The sweep files less and the
> verdict refuses less; no parse, field, Log line, item key or canonical form changes, and a caller passing no
> `resolve` sees another repo's ids as before.

## Fixtures and tests

**Sweep cases** go in a directory of their own, `fixtures/sweep/in_flight/<case>/` (invented entries, repo
`acme/widgets`), each its own `ledger.md`, optional `archive.md`, and one v3 board directory, swept on one date
apart from the shared runs, as the `answers` and `delegated` cases are (`fixtures/run.py`, `answers_case()`), so
the shared `ledger.md`'s expected output is untouched. A case may carry `resolve`, a map from a `<repo>#TD-n` item
to the resolver's answer (`[state, why]`, or a record), or `"raise"`, which the harness turns into a callable; with
no map the sweep is called with no `resolve`. Unless a case says otherwise, its board holds a closed decide for the
gate answered `One more round` (no lift) more than `reask_days` before the run, so only the new rule keeps the
sweep quiet. The expected output is each case's `to_file`, `to_close` and `lifts`:

1. `decision (pat)` beside a live `TD-n`: files nothing.
2. The same with `TD-n` archived Resolved: files the decide.
3. Beside `TD-n` archived Superseded by a live `TD-m`: nothing; by an archived Resolved `TD-m`: files; Superseded
   with no successor: files.
4. Beside `TD-n` archived Dropped, and archived with a Status word outside the vocabulary: each files.
5. Beside an id in neither ledger nor archive: files.
6. Beside `acme/other#TD-n`: no `resolve`, files; `resolve` answering `open`, nothing; answering `archived` with
   a Resolved status, files; answering garbage (read unresolved), files; raising, the sweep raises.
7. Beside `TD-n` Superseded by `acme/other#TD-m`: `resolve` answering `open` for it, nothing.
8. Two blockers, one live and one archived Resolved: nothing.
9. The entry's own id in its Blocked by, and a part of it there (`legacy-part`): files.
10. A design with `decision (pat)` and two open parts each with `decision (pat)` and nothing else (held builds),
    no Blocked by id on the design, no item: the design's decide is filed (D3), and each part's as today.
11. The same design also blocked by a live `TD-r` (the bought round), its item closed past the window: nothing
    for the design and nothing for either part (D2).
12. A part with `decision (pat)` whose parent is blocked by a live entry and carries no decision: files (D3).
13. Beside an `until` a later day, and beside `event (x)` with outcome `not yet`: files as today.
14. An open decide covering the gate, a live blocker in the Blocked by: neither filed nor closed.
15. No board lists `<p>`, a live blocker beside it: the `has no board` act is filed.
16. A closed decide answered with a lift whose gate still stands (an answer owing a lift), a live blocker beside
    it: the `was answered with a lift` act is filed as today.

The rerun rule (a second sweep over its own writes files and closes nothing) holds for each.

**Verdict cases** in `fixtures/verdict/`, `uncovered_decisions()`, a gained `decision (pat)` with no item, the
board listing `pat` unless said: beside a live id, the `decision-deferred` flag and no refusal; beside an archived
Resolved id, refused as today; beside `acme/other#TD-n`, flagged deferred; beside a local id Superseded by
`acme/other#TD-m`, flagged deferred; covered by an open item beside a live id, nothing; the board not listing
`pat`, beside a live id, `decision-deferred` alone (no `decision-elsewhere`); a part gaining `decision (pat)`
whose parent carries it and a live blocker, deferred.

**A suite test** that the sweep and the verdict agree on what is deferred for the same local ledger (every local
case above, as a v2 tree for the verdict), the one shape D1 accepts as differing left out.

## Consumers

agent-cadence (its `scripts/gate_sweep.py`) and ShiftLead, where it calls `sweep()`, each pass the resolver they
pass `pickable()` once they vendor the release; until then another repo's ids are not in flight (D1), as today. The
build's Fix names those entries, each to be filed in its own repo through its question seat; agent-cadence's
TD-291 archives once the release is vendored with a test pinning the deferral (its Log, 2026-11-18).

## Builds (filed on Paul's go)

- **B1** D1 to D4 in one PR: `sweep()`'s `resolve` and the deferral, `uncovered_decisions()`'s
  `decision-deferred`, the SPEC text above, the fixtures, the harness's `in_flight` cases and the tests above; a
  minor release.

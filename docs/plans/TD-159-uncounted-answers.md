# TD-159: the answer writer refuses a lift the merge check could not count

**Status:** Draft 4, 2026-11-23 (session lb-designer). Class: **wide** (a change to the published, vendored format:
what `decide_lift()`, and so the board writer's decide, accepts; cap 6 rounds, cadence.md §4.8). The rounds ended by
the stop rule after round 3: build-changing findings per round 4, 1, 0. Its closing fact-check raised 3 minors, all
applied, and its repeat none. Round 2's sixth minor was rejected, and every other finding is applied. Paul answered
**Go** (2026-11-22): build TD-160 (B1). The record:
[docs/reviews/TD-159.md](../reviews/TD-159.md).

**Entry:** [TD-159](../ledger/archive/TD-159.md), filed from D3 of [TD-152's design](TD-152-near-items.md).

## The problem

Two parts of the module disagree about which `decide` items can carry a person's answer to a `decision (<p>)` gate.

`covers()` finds an item only when its Context names the entry and the gate with nothing after the gate, on a board
whose `People:` lists the gate's person. The merge gate's tripwire counts a lift by answer only through an item
`covers()` finds.

`decide_lift()` is looser. `_context_gate()` reads `TD-4 decision (pat) — design ready` as one entry and one gate, so
the words after the gate do not stop the lift. With `board_people` None, a board with no `People:`, its board checks
are skipped. In both cases the writer records the answer and writes `gate lifted … answer "Go"` with no suffix, and
the tripwire then flags that lift `tripwire-no-decided`, because no item covering the gate gained a `Decided:`.

So the person's press succeeds, the ledger and board change together, and only the merge check says the lift is
wrong, when the answer has already been given and the session holding the PR has to work out what to do with it.

## What is already settled

- SPEC *The gate sweep*: a Context that goes on past its gate names no entry for `covers()`.
- SPEC *The merge gate's verdicts*: a board with no `People:` covers nothing, so every lift there is logged
  `; no board item`, and the carve-out's (a0) needs `People:`.
- TD-152's D3: only a covering item's answer counts toward a lift by answer, and an answer meant elsewhere is an
  override. This design does not change that.
- `parts_problems()` already refuses a `Parts:` snapshot whose Context goes on past its gate; the decide lift is the
  one reader that still accepts it.
- A minor release reads every file the major's earlier releases wrote (SPEC *Versions*). This design changes what a
  writer accepts and nothing a reader reads.

## The design

### D1. The decide lift refuses a lifting answer the merge gate could not count

On a `decision (<p>)` gate, `decide_lift()` refuses a **lifting** answer that would lift the gate from at least one
entry (the Context entry or a listed part still carries it, by `_carried()`) when either holds, tested in this order:

1. the item's Context has a **tail**;
2. `board_people` is None.

An answer with nothing left to lift is not refused. It writes what it writes today, which can include `gate lift
skipped` lines when a listed part is archived, and `closes()` closes the item, so a tail item whose gate has gone by
another route can still be retired by its `Go`.

**The tail** is what follows the Context's first gate, read exactly as the sweep reads its qualifier today:
`" ".join(ctx[g.end():].strip().rstrip(".").split())`. So `decision (pat).` and `decision (pat) ..` have none, while
`decision (pat)?`, `decision (pat) . .`, `decision (pat) — x` and the sweep's own `lift` and `board <repo>` have one.
Words before the gate are no tail. One private helper, `_context_tail(ctx)`, returns it with its case kept, `""` when
there is none or the Context names no gate. `_sweep_context()` (which lowercases it for its qualifier),
`_parts_fault()` and the lift all call it, so the three readers cannot drift apart.

The test runs after `lifting` is computed and the listed parts are read, directly before the write loop, so every
check `decide_lift()` makes before that loop comes first and keeps its message; a refusal raised inside the loop by
`lift_gate()` or `_logged()` now follows it. The refusals name their cure, `<ref>`, `<gate>`
and `<p>` as the item spells them, and the board writer prefixes each with `the ledger half: `, as it does every
refusal of `decide_lift()`:

- `<ref>'s <gate> cannot be lifted by an answer on this item: its Context goes on past the gate, so the merge gate
  does not count it — answer an item naming the entry and the gate alone (the sweep files one when it can), or, while
  none is open, log the lift with ; no board item`
- `<ref>'s <gate> cannot be lifted by an answer on this board: it has no People: line, so the merge gate does not
  count it — add a People: line naming <p>, or log the lift with ; no board item`

### D2. What stays as it is

- **A waiting-only answer and a work order** on such an item write as they do now. Neither lifts, so the tripwire
  has nothing to flag, and refusing them would lose the person's answer.
- **An `event (<name>)` gate** is unchanged. `covers()` applies no `People:` test to it, and the tripwire audits only
  decision gates, so the two readers do not disagree about it in the way this design fixes.
- **Another repo's entry** (`<repo>#TD-n`) is unchanged. It is answered on the board alone, and its lift is a tool PR
  in that repo, which its own merge gate reads.
- **`--board-only`** is unchanged. It never calls `decide_lift()`. Its callers that reach these items do not lift:
  agent-cadence's `set` picks its item through `covers()`, which finds neither shape, and ShiftLead's board-only
  presses carry labels that do not lift. A direct call that does write such an answer is still flagged by the tripwire.

### What the person sees

A lifting press on such an item is refused with the message above and nothing changes. The item stays open.

- **A Context with a tail, with no answer logged yet:** the sweep files a covering `decide` beside it on its next run
  when a board lists the person, and after TD-158 that question names this item as an older one.
- **After a `Not yet` or a work order:** that answer logs `kept waiting`, and the sweep does not ask again until
  `reask_days` (30 by default) have passed. Until then no covering item may exist, so the route is the message's
  second one: a lift logged `; no board item`, by the gate's person or, on a board whose `Answered by` is `any`, by
  anyone it lists.
- **A board with no `People:`:** the sweep cannot file there. The cure is the `People:` line, or the same logged lift.

The two cures of a tail item exclude each other: once a covering item is open, a lift logged `; no board item` is
flagged `tripwire-no-board-item`, so that item must be answered instead. Once the covering item lifts the gate, an
old tail item stays open, since the sweep closes none whose tail is anything but exactly `lift`, and a `Go` on it
closes it with no ledger write.

### Limits accepted

- An item already answered and merged under the old rule stays as it landed. Nothing rewrites history.
- A press that used to appear to work now shows a refusal. That is the point: the failure moves from the merge check,
  after the write, to the press, before it.
- An open PR that carries such a lift, built before the release, changes verdict after it: the carve-out reported it
  with the tripwire's flag, and now sends it to review as `lift-refused`. Both end at review.
- The wait of up to `reask_days` after a work order on a tail item is accepted rather than making the sweep re-ask
  early, which would change its re-ask rule for every item.

## Options set aside

- **Widen `covers()` to accept both shapes.** Every reader would then accept a Context with words after its gate, a
  form v3.0 retired on an entry's `Blocked by`, and a board with no `People:` would let anyone's answer count, which
  is what the carve-out's (a0) exists to prevent.
- **Have the writer log `; no board item` on these lifts.** The tripwire would pass, but the Log would say no item was
  answered when one was.
- **Warn and write anyway.** The merge check would still flag the lift, so the person's answer would still be stuck.
- **Refuse every answer on such an item.** A `Not yet` or a work order is safe and worth keeping.

## SPEC text

The version below is v3.7, written before v3.6 was tagged. The build uses the next minor with no tag when it lands:
v3.6 if that is still untagged, so the two share a release, and otherwise the next free one.

**In *The decide lift*, a new paragraph directly before `**Closing on the answer** (v2.4):`**

> **A lift the merge gate could not count** (v3.7). On a `decision (<p>)` gate, `decide_lift()` refuses a lifting
> answer that would lift the gate from an entry when the item's Context goes on past the gate, or, that failing, when
> `board_people` is None: `covers()` finds neither item, so the merge gate's tripwire would flag the lift
> (`tripwire-no-decided`). The skip of the board checks for a None `board_people` does not let a decision lift
> through. What follows the gate is read as the sweep reads its qualifier: trailing dots are no words, and any other
> text is. Each refusal names its cure. An answer with nothing left to lift, a waiting-only answer and a work order on
> such an item write as above, and an `event (<name>)` gate is not affected.

**In *Edits*, the paragraph on `parts_problems()`, where the text wraps after `past`, replacing `still lifts an
`event (<name>)` snapshot and one whose Context goes on past⏎its gate, and,`:**

> still lifts an `event (<name>)` snapshot, with or without words after its gate, and,

**In *Versions*, after whichever paragraph is newest when the build lands:**

> **v3.7 refuses a lift the merge gate could not count** (TD-159; *The decide lift*): `decide_lift()` refuses a
> lifting answer on a `decision (<p>)` gate when the item's Context goes on past the gate or the board has no
> `People:`, so the board writer's decide does too. Nothing a reader reads changes, and a board holding such an
> item reads as before.

## Fixtures and tests

A prototype of the refusal, rebuilt on main after TD-157 and TD-158 landed, passes the whole suite but for the fixture
check and changes exactly three fixture results:

- `lift` `decide_lift` `no_people_line`: now the no-`People:` refusal;
- `sweep` `parts_problems` `line-words-after-gate` and `line-words-after-gate-pr`: each `lift` now the Context
  refusal.

New `decide_lift` cases in `fixtures/lift/cases.json`, each with its own entry under `items` (the harness reads
`items[c["line"]]`). An event item here has no `Lifts:`, as `scoped_event` has none, so `Go` lifts it:

1. `no_people_line_not_yet`: `Not yet` on a board with no `People:` logs `kept waiting`.
2. `no_people_line_work_order`: a work order there logs `kept waiting`.
3. `no_people_line_event`: `Go` on an `event (<name>)` item there lifts.
4. `words_after_gate_refused`: `Go` on `TD-n decision (pat) — design ready` is refused.
5. `words_after_gate_not_yet`: `Not yet` on it logs `kept waiting`.
6. `words_after_gate_event`: `Go` on an event item with words after its gate lifts.
7. `trailing_dot_lifts`: `Go` on a Context ending `decision (pat).` lifts.
8. `question_mark_tail_refused`: `Go` on a Context ending `decision (pat)?` is refused.
9. `spaced_dots_tail_refused`: `Go` on a Context ending `decision (pat) . .` is refused.
10. `words_before_gate_lifts`: `Go` on `Re TD-n decision (pat)` lifts.
11. `words_after_gate_nothing_left`: `Go` on a tail item whose entry no longer carries the gate writes nothing.
12. `no_people_line_nothing_left`: the same on a board with no `People:`.
13. `words_after_gate_no_people`: `Go` on a tail item on a board with no `People:` gets the Context refusal.
14. `words_after_gate_part_carries`: `Go` on a tail item whose Context entry has no gate and whose listed part has it
    is refused.
15. `words_after_gate_archived_part`: `Go` on a tail item whose Context entry has no gate and whose one listed part is
    archived writes only the `gate lift skipped` line.

A new `verdict` case, with its base and head trees as the existing lift cases lay them out: a one-commit PR whose
change is the decide lift of an item with a tail takes review as `lift-refused`. A board with no `People:` needs no
new case, since the carve-out's (a0) answers `lift-a0` before it calls `decide_lift()`.

## Consumers

None is expected to need a code change. ShiftLead's board write turns a `Refused` into its own refusal, so the press
is answered with the message. agent-cadence's `set` picks through `covers()`, so it never reaches the refusal. Each
takes the release by its vendor PR, whose own suite is the check that none of its tests presses a lifting answer on
one of these two item shapes.

## Builds (filed on Paul's go, 2026-11-22)

- **B1** (TD-160) D1 and D2: `decide_lift()` and its docstring (its `board_people` None wording and its refusals),
  `_context_tail()` shared by `_sweep_context()` and `_parts_fault()`, each dropping its `g` line once unused (`ruff`
  is the merge gate), the SPEC text above, the three changed fixture results, and the new cases. A minor release,
  which may be shared with TD-157 and TD-158.

# TD-053: a lifting answer closed with no lift

**Status:** Draft 1, 2026-11-05 (session lb-designer). Class: **wide** (a vendored, published format: what
`sweep()` files and closes, which both consumers vendor; cap 6 rounds, cadence.md §4.8). Rounds: **ended by the
stop rule** at round 8, 2026-11-06, after ending at the cap (6) on 2026-11-05 and two rounds Paul bought (the record: [docs/reviews/TD-053.md](../reviews/TD-053.md)). Build-changing findings per round
1–6: the fact-check 4 (round 1), design reviews 5, 1, 3, 1, 1, 1. Recurring topic: which answers, boards and
entries one act speaks for (F1, F12, F13, F34, F42, F47), settled as one group per Context entry and gate across
the boards read. Round 6's one build-changing finding (F55) was a fixture's wording. Round 7, bought by Paul's
One more round (2026-11-05): its fact-check raised six minor findings (F60–F65); its design review found F55–F59
and the cross-board grouping sound and raised one build-changing finding (F66: an answer dated in the future let a
closed act refile each day; such an answer now owes nothing), reopening F50, and three minor (F67–F69, F69 the
fixtures' id table). F66–F71 (F70–F71, the closing fact-check's, SPEC wording) were then read by round 8, bought by Paul's second One
more round (2026-11-06): its design review read the whole plan, F66–F71 first, against the code and found nothing,
so the rounds end by the stop rule; round 8 changed no text, so its closing fact-check had nothing to read. Every
finding has been read by a design review. Waits on Paul's go (the board's decide item); recommended: Go.

**Entry:** [TD-053](../ledger/TD-053.md). Reported by ShiftLead (its TD-1425, after TD-1392's live re-ask of
2026-11-05).

## The problem

A person answers `Go` on a `decide` whose Context names a `decision (<p>)` gate. `decide_lift()` lifts the gate
and `closes()` closes the item `— lifted.` in the same write. If the item is closed `— lifted.` and the lift does
not happen, the gate stays on the entry, and nothing on the board says so:

- `covers()` counts only `open` and `decided` items, so the closed item covers nothing;
- the sweep's re-ask window (`_answered_within()`) counts only an answer that does **not** lift, since SPEC's
  *One filing rule* says "an item closed `— lifted.` … opens no window": a gate lifted and later re-added is a
  new question, asked at once (target design §1.2; `fixtures/sweep` TD-211);
- so the next sweep files a fresh `Go | Not yet` for every entry that still carries the gate, asking the person
  again what they answered.

Since v2.4 `closes()` closes a lifting answer only once nothing listed carries the gate, so the state comes only
from a write that bypassed it: an answer written before `decide_lift()` existed, a hand edit, or a write that
closed the item and then failed to lift. It happened live on 2026-11-05 in ShiftLead: an answer `Go` on a parent
with four parts, closed `lifted` before the decide lift existed, and the next sweep filed five `Go | Not yet`
items. agent-cadence's `gate_sweep.py` calls the same `sweep()`.

On the board the two cases look alike: an item closed `— lifted.` with `Decided: Go …`, and the gate on the entry.
The entry's Log tells them apart. `decide_lift()` writes `gate lifted: <gate> — by <p>; answer "<label>"` on each
entry it lifts, so a gate lifted and then re-added has a `gate lifted` line for it dated on or after the answer,
and a gate never lifted has none.

## What is already settled

- **A gate lifted and re-added is asked at once** (target design §1.2; SPEC *One filing rule*; fixture TD-211).
  This design changes nothing for it.
- **Only an answer lifts a person's gate**, through `decide_lift()` in a PR the merge gate reads (SPEC *The decide
  lift*, *The merge gate's verdicts*). The sweep's `lifts` are `until` and `event` gates alone.
- **The sweep keeps no state**: the boards, their archives and the Log are its state, and a second run over its
  own writes files and closes nothing.
- **The host's "lift was closed" item** (`act`, `Context: TD-n <gate> lift`, target design §4.4) is the existing
  shape for "an answer said lift, and the lift did not land"; the sweep's close rule closes it once the gate is
  gone.

## Options weighed

- **A. An `act` to lift it** (the report's (a)). A closed lifting answer within the re-ask window whose gate was
  never lifted files one `act` on the board that holds the answer, telling the person the answer did not land, in
  place of the `Go | Not yet` re-ask. It closes once the gate is gone. The missed lift is put in front of a
  person, who does it in one step (a hand lift with an `override:` reason, or answering again).
- **B. The answer covers the gate for the window** (the report's (b)). Nothing is filed; the gate waits until the
  window passes and is then asked again. It stops the noise and hides the fault: the person said Go, and for 30
  days nothing moves and nothing says why.
- **C. The sweep lifts it.** It returns a lift for the gate, with the old answer as evidence, as it does for a
  reached `until`. Rejected: a person's gate is lifted only by an answer through `decide_lift()`, in a PR the
  tripwire and the lift-PR verdict read. A host lifting on an item already closed would be a lift no verdict
  accepts (the item gains no `Decided:` in the PR), and the answer may be weeks old and about a question that
  has changed. It is also a change to who lifts a decision, which is not this entry's to make.

**Recommended: A.** B leaves the person's own answer silently undone; C moves a decision the format keeps with the
person. A costs one item, the same count as today's re-ask, but it asks nothing: it says what is left to do.

## Decisions

**D1. It ships in the next tagged release that has not been cut when its build merges, written v2.6 here** (v2.6
is untagged on 2026-11-05 and already holds TD-052's paragraph). It is no version event: no form, key or reading
changes, only what one function files and closes.

**D2. An answer, and what it owes, read from the Log.** An **answer item** is a `decide` on a board read, in state
`closed-decided` (closed, on the board or in its archive), whose Context `_sweep_context()` reads as this repo's
entry `c` and a `decision (<p>)` gate with an empty qualifier, whose `Decided:` label lifts (`_lifting()`, as
*Closing on the answer* reads one), on a board whose `People:` lists `<p>`: an item `covers()` would find, closed.
Its answerer (`Decided: … (by <x>)`) is one `decide_lift()` would accept: `<p>` (compared case-insensitively), or,
on a board whose `Answered by:` is `any`, a name on its `People:`; an answer by anyone else owes nothing, and the
gate is asked again as today (the merge gate would refuse the lift it asks for). An answer with no `(by …)`
(`BoardItem.decided_by` None, as an answer written before v2.3 or before the decide lift is) counts as `<p>`'s:
the sweep reads it so because the live case has that shape (the tripwire and the lift-PR verdict read a missing
one their own way, `lift-no-by`, and are unchanged). `Answered by:` is read per board: `_read_boards()` gains
`"answered_by": answered_by(text)` beside `people`, and only `any` (in any case) is `any`; every other value,
none among them, is `owner`. The entries it **covers** are `c` and each `Parts:` id whose open entry is `Part of` `c` (as `_names_entry()`
reads a part). With `D` its `Decided:` date, it **owes** the lift to each covered entry that:
- is open and carries the gate (`_carried()`);
- has no `gate lifted:` Log line for the gate (`_gate_key()` equal) dated on or after `D − 1`; and
- has no `gate added:` Log line for the gate dated on or after `D + 2` (a gate removed with no Log line, by hand,
  and added again since the answer is a new question, not a missed lift).

An answer dated after `today_local` owes nothing: it is not an answer item, and its gate is asked again as today.
A date in the future is a typo or a skewed clock, and no date guard (D3) can hold a filing against an answer not yet
reached: an act filed and closed by hand would be filed again each day until then. An answer that owes nothing is
settled, as today. A Log line is compared by its date (`date.fromisoformat`),
and a line whose date does not read (`2026-02-30`) is not counted (each line on its own, which is not how
`gate_added()` reads its last one); an entry whose Log
does not read at all (two Log sections, which `_log()` reads as none) has no line, so it is owed.

**The one day either way.** A `Decided:` date is the board's local date and a Log date is UTC (SPEC *The gate
sweep*: "Log ages … against `today_utc`, `Decided:` dates against `today_local`"), so a line written in the same
moment as the answer may be dated a day before or after it. The tolerance is read in the direction that keeps
today's behaviour: a `gate lifted` line a day early counts as a lift (the gate, carried now, was re-added, so it is
asked); a `gate added` line a day late counts as written with the answer. What this cannot tell apart, and accepts:
a real lift by an earlier answer logged the day before a second answer, and a hand re-add on the day after an
answer. Each is read the way today's sweep reads it, a fresh question. A gate lifted by an earlier answer,
re-added, and answered `Go` again with the second answer closed and never lifted, is owed, as it should be.

**D3. A pre-pass over the answers, then the entries.** Before the per-entry loop, `sweep()` reads every answer item
(D2) that owes something, on every board read, and groups them by Context entry `c` and gate (`_gate_key()`): one
**group** per question answered, whichever boards hold its answers. For each group:

- an answer is **within the window** when `(today_local − D).days < reask_days` (`_answered_within()`'s
  arithmetic; that function itself returns False for a lifting label, so it is not called); a group holds only
  answers that owe something, so none is dated after `today_local` (D2);
- **its act is filed** when it has an answer within the window and at least one entry the group owes is not
  covered (no `open` or `decided` item `covers()` finds for it): one `act` (below) on the newest answer's board
  (between boards holding answers of one date, the first by `_board_pick_key`, this repo's own board given no preference, unlike the re-ask's `pick`), its text's
  `<D>` the newest answer's date (the newest of the group is then within the window), its `<ids>` every entry any
  answer of the group owes that is not covered, fixed when it is filed. It is not filed while an item of its
  identity (Context `c`, the gate and `lift`, `act`, the words `was answered with a lift`) is open on any board
  read, nor when one, open or closed, on any board read or its archive is dated on or after the newest answer's
  `D − 1`. So it is filed once per answer: a person who closes it without lifting is not told again until another
  answer owes;
- **its entries are held**: an entry owed by any answer of the group within the window, or by any answer of the
  group while the group's act is open on a board read or filed in this run (the pre-pass runs first, so an old
  answer's entry is held in the run that files the act naming it), files nothing more in the `decision (<p>)`
  branch (a new test after the three existing ones: covered; answered without a lift within `reask_days`; a `kept
  waiting` line within it).

The window decides only whether an act is filed; once filed, the act holds and closes (D4) on everything the
group owes, on every board. The acts come first in `to_file`, filed in the pre-pass, ordered by Context entry
number, then gate key; each board's list then continues with the per-entry loop's items as today.

Otherwise the gate is asked again as today (`Go | Not yet`). An entry re-added after its lift is owed by nothing and
asked at once, as TD-211 is, even while its parent's act stands for its siblings. A group whose answers are all
past the window, with no act open, gets no act, and its entries are asked again as today: a person's own answer
older than `reask_days` is a stale question, and the re-ask is how it is recovered. With `reask_days` 0 no answer
is within the window, so such answers file no act.

An act's `<ids>` are fixed when it is filed. When a newer answer owes more while the act is open, no second act is
filed (its identity is open); the newer entries are held, unnamed, and keep the act open (D4). A person who closes
the act by hand frees the next sweep to file a new one naming them, its date guard reading the newest answer's
date. An act the sweep itself closes (nothing owed) dated `T` would likewise stop a new act for an answer dated
`T + 1` or earlier: that answer was closed `— lifted.` within a day of the last lift being finished, which is rare,
and its entries are held through its window and then asked again; accepted.

The host's "lift was closed" item is unchanged and holds nothing new.

**The act.** On the newest answer's board (which lists `<p>`, so it is the person's board):

- **kind** `act`; **Context** `<ref> <gate> lift`, `<ref>` the group's Context entry written as the re-ask writes
  an entry: the ledger's id (`TD-n`) on this repo's own board, `<repo>#TD-n` (`repo` lowercased) on another's;
  `<gate>` spelled as the newest answer's Context writes it (`_item_gate()`; the group is keyed by `_gate_key()`,
  lowercased, so `decision (PAT)` on an entry and `decision (pat)` on the answer are one group);
- **text** `<gate> on <ref> was answered with a lift on <D> but still stands on <ids>: lift it.`, `<ids>` in
  number order, separated by `, `, each written as `<ref>` is. The answer's label is not written: a label may hold
  words `item_line()` refuses in a text (a field name, a reply tail), and the date finds the answer;
- **fixed words** `was answered with a lift`, a new sweep head (`SWEEP_HEADS`, `unlifted`, kind `act`);
- **detail**: `context` "<ref>'s <gate> was answered with a lift on <D>, and the item was closed as lifted, but the
  gate was never lifted on <ids>", `question` "Lift the gate by hand, or ask the question again?", `recommended`
  "Lift it by hand (an `override:` naming the answer); to ask again instead, close this and add the question".

The act is the sweep's first `act` with a detail block; `item_line()` writes one on any kind (SPEC *Versions*, v2.3:
"`item_line()` writes every kind with its answers and detail block"), and `detail` is among the filed item's
arguments in *The gate sweep*, so no SPEC text is needed for it.

Like every item the sweep files, the host dates it with its own today, the board's local date. An item's date is
its head's: `BoardItem` has no date field, so it is read from `item.text` by a new pattern,
`^(?:[A-Za-z]+\s+)?(\d{4}-\d{2}-\d{2})\b` (an optional kind word, then the date). `HEAD_RE` is not reused: it
needs `(session …`, and a head written `(n/a)` or `(<person>)` would read as undated. An item whose head has no
readable date never blocks a filing.

An answer whose Context entry `c` is in neither the ledger nor the archive owes nothing (D2 reads only a group
whose `c` the sweep knows, `known`), so no act is filed that the close rule would leave for a person.

**D4. The act closes once nothing is owed.** The close rule gains a case, tested before the `lift` one (in
`_sweep_closes`, after the `gone is None` return, so an act whose Context entry is in neither the ledger nor the
archive is left for a person, and ahead of the `qual == "lift"` return): an open `act` with the head `unlifted`
and qualifier `lift` closes once no answer item on any board read for its Context entry and gate owes anything (D2,
re-read from the Log at close time). It names no answer by date, so no skew between the act's date and an answer's
can close it early; and nothing owed means nothing refiles it. An act about a parent stays open while a part it
owes still carries the gate, and is not held by a sibling re-added after its lift. The host's "lift was closed" item
keeps today's rule.

**D5. Nothing else changes.** `covers()`, `closes()`, `decide_lift()`, the verdicts and *One filing rule* for
every other item are unchanged. `uncovered_decisions()` reads only open items and a new `decide`, so the act changes
nothing there. An event gate is untouched: its lifts are the host's.

## Consumers

Neither consumer changes code: each files what `sweep()` returns and closes what it lists. Each needs its vendor
PR. ShiftLead's own half (deduping its notices) is its TD-1425, filed. No new consumer entry is needed.


## The SPEC text the build lands

In *The gate sweep* (SPEC.md), each change in the one build.

**1. The `decision (<p>)` bullet.** Its condition, "not covered and with no `kept waiting` Log line for it newer
than `reask_days`, and no item `covers()` finds answered without a lift within `reask_days`:", gains ", and not
held by an answer owing a lift (below)" before its colon; and after the bullet's last sentence ("When no board lists
`<p>`: … on this repo's own board;"), replacing its `;` with `.`, add:

> An **answer owing a lift** (v2.6) is an item `covers()` would find for an entry's `decision (<p>)`, closed, whose
> `Decided:` label lifts, dated `D` no later than `today_local`, given by `<p>` (or by no one named, or, under `Answered by: any`, by a name on
> `People:`). It owes the lift to each entry it covers (its Context entry, in the ledger or the
> archive, and each `Parts:` id `Part of` it) that is open and carries the gate, and whose Log has no `gate lifted:` line for the gate dated on
> or after `D − 1` and no `gate added:` line for it dated on or after `D + 2` (a board's date is local, a Log's UTC).
> The answers owing for one Context entry and gate, on any board read, file one `act` on the newest one's board
> (between boards whose newest answer shares that date, the first by pick key), when one of them is within
> `reask_days` and an entry they owe is not covered: Context the Context entry with the gate and ` lift`, its text
> `<gate> on TD-n was answered with a lift on <D> but still stands on <ids>: lift it.`, `<D>` the newest answer's
> date and `<gate>` as its Context spells it, `<ids>` every entry they owe that nothing covers, in number order; not while one of its identity
> is open, nor when one, open or closed, on any board read or its archive is dated on or after the newest answer's
> `D − 1`. An entry
> owed is held: it is not asked again while an answer owing it is within `reask_days`, or while an act
> for the Context entry and gate of an answer owing it is open on a board read or filed in the same sweep;

**2. *One filing rule*.** "holds for every item but the decision's own (whose rule is *covered*, above)" becomes
"holds for every item but the decision's own (whose rule is *covered*, above) and the `was answered with a lift`
`act` (whose rule is the same bullet's)". After "An item closed `— lifted.`, or closed with no answer, opens no
window.", add:

> One whose lift never happened owes it, and is the `decision (<p>)` bullet's (above).

(Not SPEC text: the act's identity is the bullet's own, its Context entry, gate and `lift`, kind `act`, the words
`was answered with a lift`, and no `kept waiting` line or answered item opens a window for it: its guard is its own
date. *One filing rule*'s list of fixed words is unchanged.)

**3. *The close rule*.** "and the `lift was closed` item (Context `TD-n <gate> lift`), close once it is gone;"
becomes "and the host's `lift was closed` item (Context `TD-n <gate> lift`, without `was answered with a lift`),
close once it is gone;", and a bullet follows that one:

> - the `was answered with a lift` `act` once no answer on any board read for its Context entry and gate owes the lift
>   (v2.6);

**4. *Versions*.** A paragraph after the v2.6 paragraph:

> **v2.6 stops the sweep re-asking a lifting answer closed with no lift** (*The gate sweep*): within `reask_days`,
> once per answer, an `act` says the lift is owed, in place of `Go | Not yet`, and closes once nothing is owed. A
> gate lifted and re-added (its Log says so) is asked at once, as before.

## Fixtures

Invented names only (`pat`, `kim`, `acme/widgets`), never a person's (AGENTS.md). New entries in
`fixtures/sweep/ledger.md` from TD-224 (the last is TD-223), numbered as the table after the cases gives them, new items on `widgets.md` (`People:` lists `pat`),
`beta.md` (`People: kim`) and `beta.archive.md`, the `runs` and `rerun` expectations updated for them (`today`
2026-11-03, `two days later` 2026-11-05; the window 30 days, so an answer dated 2026-10-05 or later is within it on
`today`, 2026-10-07 or later on `two days later`), and the new entries added to `cases.json`'s `covers` list where a state is shown. Each case below gives
its dates:

- **Never lifted:** TD-224 carries `decision (pat)`, no Log line for it; on `widgets.md` a closed `decide`,
  `Context: TD-224 decision (pat)`, `Decided: Go (by pat) (2026-10-25)`, `Closed: 2026-10-25 — lifted.`. Files the
  act, Context `TD-224 decision (pat) lift`, and no `decide`; `covers()` lists the item as `closed-decided`.
- **TD-211 unchanged** (lifted 2026-10-20, re-added 2026-10-30): still files its `decide`.
- **A parent's answer:** TD-225 with parts TD-226 to TD-229, its item answered `Go` (2026-10-28) and closed `—
  lifted.`, `Parts: TD-226, TD-227, TD-228, TD-229.`. TD-225 carries nothing (lifted, logged 2026-10-28); TD-226
  and TD-229 carry the gate, no Log line; TD-227 carries it, `gate lifted` 2026-10-28 and `gate added` 2026-10-31;
  TD-228 no longer carries it. (TD-227's `gate added` line is not what decides it: its `gate lifted` line does;
  the `D + 2` rule has its own case below.) Files one act, Context `TD-225 decision (pat) lift`, text `… still stands on
  TD-226, TD-229: lift it.`, and a `decide` for TD-227.
- **Removed by hand and re-added:** an entry carrying the gate, an answer `Go` 2026-10-25 closed, no `gate lifted`
  line, `gate added` 2026-10-29: files the `decide`.
- **The one-day skew:** an entry whose `gate lifted` line is dated the day before its answer's `Decided:`
  (2026-10-24, answer 2026-10-25), the gate re-added 2026-10-30: lifted, so it files the `decide`. And one whose
  only `gate added` line is dated the day after its answer (2026-10-26): owed, so the act.
- **Two answers for one Context entry** on one board, `Go` 2026-10-20 and `Go` 2026-10-27, both closed, both owing:
  one act, its text's `<D>` the newer's. And an old and a new answer in one group, a parent's (the parent lifted,
  logged 2026-09-20, carrying nothing): `Go` 2026-09-20 (past the window), `Parts:` the first part alone, and `Go`
  2026-10-27, `Parts:` the second alone, each part carrying the gate with no Log line: one act naming both, and no
  `decide` for the first part in that run. Its close variant, on a parent and parts of its own with the same two
  answers and their act open (dated 2026-10-28), the second part lifted (logged 2026-10-28) and free: the act
  stays open while the first part is owed.
- **A parent's answer and a part's own:** a part owed by both its parent's answer and its own: one act for each
  Context entry, the part in both `<ids>`; no `decide`. Two acts for one lift are accepted: each says what one
  answered question left undone, and one lift closes both.
- **Past the window:** an answer dated 2026-10-01, never lifted, no act: files the `decide`. The same with its act
  open (dated 2026-10-01): files nothing. The same with its act closed: files the `decide`.
- **Filed once:** an answer 2026-10-25 whose act, dated 2026-10-26, was closed 2026-10-27 with no lift: files
  nothing. And one whose closed act is dated 2026-10-24, a day before the answer (the host's date behind the
  person's): files nothing.
- **Covered:** an owed entry with an open `decide` covering it: no act, no new `decide`. A parent's answer owing
  two parts, one covered by an open `decide`: the act names the other alone.
- **Who answered:** an answer `Go (by kim)` on `widgets.md` for `decision (pat)`, the board with no `Answered by:`:
  owes nothing, files the `decide`. An answer with no `(by …)` (`Decided: Go (2026-10-25)`): owed, the act.
  `alpha.md` (`People: kim, pat`) gains `Answered by: any`: an answer there `Go (by kim)` for `decision (pat)`
  owes, the act on `alpha.md`; one `Go (by lee)` (not on `People:`) owes nothing.
- **The window's edge:** an answer dated 2026-10-05, never lifted, no act: on `today` (29 days) it files its act;
  on `two days later` (31 days) it files the `decide` (each run reads the same inputs).
- **Archived:** an answer closed and moved to `beta.archive.md` (`Context: acme/widgets#TD-n decision (kim)`),
  never lifted: the act on `beta.md`, Context `acme/widgets#TD-n decision (kim) lift`, its text naming
  `acme/widgets#TD-n`. And a Context entry archived (in `archive.md`) whose answer owes an open part: the act
  stands.
- **Two boards:** one entry's `decision (pat)` answered `Go` on `widgets.md` (2026-10-20) and on `alpha.md`
  (2026-10-27), both closed, never lifted: one act, on `alpha.md` (the newer answer's), Context
  `acme/widgets#TD-n decision (pat) lift`; no `decide`. A variant, on its own entry and its own items (the shared boards hold one state per run), with `alpha.md`'s act
  (dated 2026-10-28) closed by hand: no act (the closed act's date guard, read on `alpha.md`) and no `decide` (both answers within the
  window). The rerun of the first files nothing.
- **A future answer:** an answer `Go` dated 2026-11-06 (three days after `today`), closed, never lifted: owes
  nothing (D2), so it files the `decide` and no act; the rerun files nothing (the `decide` covers it).
- **A non-lifting label closed:** `Decided: Not yet …`, closed: the existing window, nothing new.
- **`reask_days` 0:** a run with `reask_days: 0` (as of `today`): TD-224 files its `decide`, no act.
- **The close:** fresh parents, each lifted (logged 2026-10-28), each with its answer `Go` (2026-10-28) closed and
  its act open (dated 2026-10-29):
  TD-230 with parts TD-231 (carrying, no Log line) and TD-232 (lifted 2026-10-28, re-added 2026-10-31): the act
  stays open; TD-233 with parts TD-234 (lifted, free) and TD-235 (lifted 2026-10-28, re-added 2026-10-31): the act
  closes while TD-235 still carries the gate (TD-232 and TD-235, re-added after their lifts, each get a `decide`); the `rerun` closes nothing more and
  files no act again. The host's `Lift of decision (pat) on TD-269 was closed` act (Context `TD-269 decision (pat)
  lift`), with no answer item, closes once the entry is free, as today, and holds no re-ask.

The new entries, by case (each case's own entries and items, apart from every other's; `P` a parent, its parts
after it):

| case | entries |
|---|---|
| Never lifted (and `reask_days` 0) | TD-224 |
| A parent's answer | TD-225 (P), TD-226 to TD-229 |
| The close | TD-230 (P), TD-231, TD-232; TD-233 (P), TD-234, TD-235 |
| Removed by hand and re-added | TD-236 |
| The one-day skew | TD-237 (lifted the day before), TD-238 (added the day after) |
| Two answers for one Context entry | TD-239 |
| An old and a new answer | TD-240 (P), TD-241 (the older's), TD-242 (the newer's) |
| Its close variant | TD-243 (P), TD-244 (the older's), TD-245 (the newer's) |
| A parent's answer and a part's own | TD-246 (P), TD-247 |
| Past the window | TD-248 (no act), TD-249 (its act open), TD-250 (its act closed) |
| Filed once | TD-251 (act dated after the answer), TD-252 (act dated the day before) |
| Covered | TD-253; TD-254 (P), TD-255 (covered), TD-256 (named) |
| Who answered | TD-257 (`by kim`, `widgets.md`), TD-258 (no `by`), TD-259 (`alpha.md`, `by kim`), TD-260 (`alpha.md`, `by lee`) |
| The window's edge | TD-261 |
| Archived | TD-262 (its answer in `beta.archive.md`); TD-263 (P, in `archive.md`), TD-264 |
| Two boards | TD-265; TD-266 (the variant) |
| A future answer | TD-267 |
| A non-lifting label closed | TD-268 |
| The host's `lift was closed` act | TD-269 |

`fixtures/run.py` gains one thing: a run in `runs` may give its own `reask_days`, which `run()` in
`sweep_cases()` passes to `sweep()` only when the run has the key (its first call and the `rerun`'s alike; a run
without it passes none, so `sweep()`'s default stands), as the `refused` cases already pass theirs. It already compares
`to_file`, `to_close` and `covers()`.

## The builds

Filed on Paul's go, `**Part of:** TD-053`:

- **B1:** D2–D4 in `sweep()` and its close rule (`ledgerboard/__init__.py`), the four SPEC texts above, the
  `fixtures/sweep` cases above, and unit tests in `tests/` where its suites cover the sweep. Done when those
  fixtures and tests pass, TD-211's case still files its `decide`, and the SPEC text lands with the code.

The release (Paul's) and each consumer's vendor PR follow, as AGENTS.md says.

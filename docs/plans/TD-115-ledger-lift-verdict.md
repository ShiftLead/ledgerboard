# TD-115: a merge-gate verdict for a PR that only lifts a gate

**Status:** Draft 1, 2026-11-15 (session lb-designer). Class: **wide** (a vendored, published format: a new
verdict, a new commit-subject kind and its writer, which both consumers vendor; cap 6 rounds, cadence.md §4.8).
Rounds: not yet run (the record: [docs/reviews/TD-115.md](../reviews/TD-115.md)).

**Entry:** [TD-115](../ledger/TD-115.md). Asked for by agent-cadence's grinder (its TD-262, 2026-11-15).

## The problem

ShiftLead's **Lift the hold** press (its TD-1829, design §4.4 *Board write-back*: *Lift the hold is a lift on the
press*) lifts a person's `decision (<p>)` gate itself, on the person's press, through this package's
`plan_lift()`. It lands one commit in one PR, subject and title `shiftlead: lift decision (<p>) on TD-n (session
n/a)`, and merges it at once, the press being its review. Its diff is the entry's lift, and on one board state
also the close of the board item the lift answers (below, *The press's four cases*). Neither carve-out the merge
gate has fits it:

- `lift_pr_verdict()` passes only a PR that answers one open board item (`Decided:`, a `decide` subject), so a
  lift-only PR goes to review at its first board condition (`lift-board-diff`);
- agent-cadence's own `board-append` carve-out (its `check_cadence.py`, not this package) passes only a PR that
  changes the board alone.

So agent-cadence's audit fails the PR's review row and lists it as merged outside step 5 (agent-cadence TD-262).
The verdicts are this format's (pure functions over the trees a consumer passes in), so the new one belongs
beside them.

What makes this a design and not a build: a carve-out skips ordinary review, and the lift's one trace is its Log
line, which SPEC already calls forgeable (*The merge gate's verdicts*: *a well-formed hand edit passes it, and
review is the backstop*). The design has to say what the verdict trusts in place of review.

## What is already settled

- **A lift is one text edit** (SPEC *Ledger entries and their edits*, *Lifting a gate*): `lift_gate(text, gate,
  by, *, answer, suffix, today, …)` removes the gate from `Blocked by` and appends `gate lifted: decision (<p>) —
  by <p>; answer "<label>"[<suffix>]`. `by` is the gate's person, compared case-insensitively, unless `people`
  and `Answered by: any` are passed. `plan_lift()` (the ledger writer, `ledger.py`) composes it with the
  writer's `gate()` check and writes that one file.
- **The suffix says where the answer is** (SPEC *The merge gate's verdicts*, `tripwire()`): none means a covering
  item on this board gains its `Decided:` or, decided already, is newly closed `— lifted`; `; no board item`
  means nothing covers the gate at the base nor at the head; `; shared board item left open` means a covering
  item still covers it and lists another entry still carrying the gate; `; board <repo>` names another repo.
- **The tripwire runs on every PR**, and returns flags for a removal the diff does not account for. It reads
  this repo's board alone, at the base and the head.
- **`lift_pr_verdict()`'s carve-out** rests on the diff being exactly one writer's output from the base, for
  one answer by a person the base board lists on `People:` (its (a0), (b), (c)), with its dates windowed on the
  forge's `created_at` and `merged_at`. The consumer fetches trees, files, commits and dates; the package reads
  no git and no forge.
- **The commit-subject grammar** (SPEC *Edits*, *The commit subject of a board write*) names board writes
  `edit`, `append`, `archive`, rank writes `queue`, and the migrate commit `migrate` (`subject_kind()`). No
  subject names a ledger lift today: `subject_kind("shiftlead: lift decision (paul) on TD-12 (session n/a)")` is
  None, and so are `edit_action()` and `subject_id()`.
- **`covers(entry_text, gate, boards, repo)`** names the `decide` items asking an entry's gate, each with its
  state; `COVERING` is `("open", "decided")`.

## The press's four cases

ShiftLead's §4.4 (*The suffix*) picks the lift's form from `covers()` on the entry's gate over the entry's own
repo's board, before the press. An item *lists another gated entry* when its Context entry (the entry's parent,
where the item covers it through `Part of`) or one of its `Parts:` ids is a bare `TD-n` open in the ledger, not
the pressed entry, and carrying the same gate: the test the tripwire's shared case makes. Where several items
cover the gate, the first case that holds decides:

- **(d) asked:** an open, undecided covering item lists no other gated entry. The press is refused and writes
  nothing: that item is the person's question, and its answer there is the decide lift (`lift_pr_verdict()`).
- **(b) decided:** an open, decided covering item lists no other gated entry. Every such item is closed in the
  same commit, `Closed: D — lifted` (the board writer's `done` with the why `lifted`), and the lift has no
  suffix.
- **(c) shared:** a covering item lists another gated entry. The lift is `; shared board item left open`, and
  the board is unchanged.
- **(a) none:** nothing covers the gate. The lift is `; no board item`, and the board is unchanged.

Each is a form the tripwire already accepts. The design makes that choice the format's, so the press and the
verdict compute it from the same function.

## The design

### D1. The lift's subject is the format's

A new subject, one line: `<tool>: lift decision (<p>) on TD-n (session <name>)`, `<p>` the gate's person as the
entry spells it and `<name>` the caller's session, else `n/a`. It is ShiftLead's subject today, word for word, so
no consumer's existing PR or commit changes.

- `lift_subject(tid, gate, tool, session=None)` writes it. It refuses a `tid` that is not a bare `TD-n`, a `gate`
  that is not `decision (<p>)` (an `until` or event lift has its own routes, and a host writes those), and a
  `tool` or `session` that is not a token of `[A-Za-z0-9_.@/-]+` (the Log's rule for who and a session).
- `subject_kind()` names it `lift`. `edit_action()` and `subject_id()` stay None for it: they read board writes,
  and a lift subject names an entry, not an item.
- `lift_subject_parts(line)` reads it back as `{"tool", "gate", "id", "session"}`, or None for any other line.

A lift of another repo's entry (`<repo>#TD-n`) has no subject here: its lift is a PR in that repo (ShiftLead's
§4.4), whose own subject names its own `TD-n`.

### D2. The lift's form is one function

`lift_form(tree, tid, gate, repo)` returns `(case, items)` for the open entry `tid` carrying `gate` in `tree`'s
ledger, read against the tree's own board (`load_board()`, as the verdicts read it): `case` one of `asked`,
`decided`, `shared`, `none` by the order above, and `items` the covering `BoardItem`s that decide it (for
`decided`, every item to close; for `shared` and `asked`, the items that matched; for `none`, empty). It refuses
an entry the tree's ledger does not hold open, one not carrying `gate`, and a `gate` that is no decision. A v1
ledger is refused; a tree with no board is `none`, as `covers()` reads it.

It is public so the press can call it, in place of its own copy of the rule, and the verdict and the press can
never disagree about the suffix. ShiftLead is not required to adopt it: its rule and this one are the same
today, and the verdict judges the bytes.

### D3. The verdict

`ledger_lift_verdict(base_tree, head_tree, files, subject, commits, created_at, merged_at, repo)` returns
`{carve_out, flags, review}`, in `lift_pr_verdict()`'s shape and with its arguments read the same way (trees,
the PR's changed paths, its commit's subject, its commit count, the forge's dates as UTC days, `merged_at` None
while open). `flags` are `tripwire()`'s over the same trees. It is a separate function, not a new branch of
`lift_pr_verdict()`, so that verdict's reasons stay as they are for its callers, and a consumer wires the two
as two carve-outs (agent-cadence's `decide` and `lift`).

`carve_out` is True only when every one of these holds; else `review` names the first that fails, in this order:

1. **The board:** a v3 board at the base and the head (`ledger-lift-no-board`; a v2 one, `ledger-lift-board-v2`),
   as `lift_pr_verdict()` reads them. The base board declares `People:` (`ledger-lift-no-people`).
2. **The subject:** `lift_subject_parts(subject)` reads it, and the PR is one commit (`ledger-lift-subject`).
3. **The files:** every path in `files` is the entry's open file `docs/ledger/TD-n.md` (the subject's `TD-n`)
   or, for case `decided`, a board item path (directly in `BOARD_DIR`, or under `archive/<YYYY-MM>/`)
   (`ledger-lift-files`). Of the paths whose text the trees change, the ledger's are exactly that one file
   (`ledger-lift-files`).
4. **The entry:** the base ledger is v2 and holds `TD-n` open, carrying the subject's gate, and its head file
   is still open (`ledger-lift-entry`).
5. **Who:** the subject's `<p>`, the gate's person and the new Log line's `by` are one name, compared
   case-insensitively, and the base board lists it on `People:` (`ledger-lift-by`). `Answered by: any` admits
   no one else here: a lift by anyone but the gate's person takes review.
6. **The form:** `lift_form(base_tree, TD-n, gate, repo)` is not `asked` (`ledger-lift-asked`: the item is the
   person's question, and its answer is the decide lift).
7. **The bytes:** the head entry is `lift_gate(base text, gate, by, answer=label, suffix=S, today=T)` byte for
   byte, where `label` and `T` are the head's one new Log line's, and `S` is the form's suffix: none for
   `decided`, `shared board item left open` for `shared`, `no board item` for `none` (`ledger-lift-bytes`). The
   board's changes are none for `shared` and `none`; for `decided`, exactly each item `lift_form()` names, its
   open file removed and `item_path(id, C)` added as `edit_item(base file, "done", why="lifted", today=C)` byte
   for byte (`ledger-lift-board`).
8. **The dates:** `T`, and each item's close date `C`, lie within a day of `created_at` and not after the merge
   (else `created_at + 1`) (`ledger-lift-date`), as `lift_pr_verdict()`'s (c) windows `T`.
9. **No flag:** `flags` is empty (`ledger-lift-flagged`). A PR that passes 1–8 raises none by construction; the
   condition keeps a future tripwire rule from being skipped by this carve-out.

As for `lift_pr_verdict()`, (d) is the consumer's: a direct commit with this shape is refused by its own audit.

### D4. What stands in for the person's answer

The verdict trusts exactly what `lift_pr_verdict()`'s carve-out trusts, no more:

- **The shape is one writer's output.** Every byte the PR changes is recomputed from the base: one entry's lift,
  with the suffix the base board dictates (not one the PR chose), and in case `decided` the closes the lift
  owes. Nothing else changes: no code, no other entry, no other item.
- **The answerer is the gate's person, on the board's `People:`.** This is stricter than the decide carve-out,
  which admits anyone listed under `Answered by: any`.
- **The question existed, or was already answered.** In case `decided` the base board holds the person's own
  `Decided:`, merged before the press. In cases `none` and `shared` there is no open question for the lift
  to bypass; in case `asked` there is one, and the lift takes review, since that item's answer is the way.

A forger who can push can write this PR, but can write a decide PR just as well: the worst either does is lift
one gate of an entry whose person is on the board. The Log line stays forgeable, as SPEC says, and the
sweep's audit and review stay the backstop. Requiring more, such as a host log witnessing the press, would put
the machine and its logs into the package, and a verdict that reads one machine's log is not the same on every
machine.

### D5. The release

A minor release, **v3.2**: one new verdict, one new helper, one new subject kind and its writer and reader. No
parse, field, Log line, item key or canonical form changes. One reading changes: `subject_kind()` returns `lift`
for a subject that read None before, so a consumer that branched on None for it reads `lift` once it vendors
v3.2. Neither consumer's code reads that subject's kind today; agent-cadence's TD-262 wires the verdict as its
carve-out `lift`.

## Options set aside

- **No carve-out: a lift-only PR takes ordinary review.** Every press would wait on a reader for a two-line diff
  the verdict can check whole, and the press, which Paul's ruling makes a lift (ShiftLead TD-1829, 2026-11-14:
  *lifts are allowed by a button press*), would never land at once.
- **A carve-out on the tripwire alone** (any PR whose lift the tripwire passes). The PR would choose its own
  suffix and could change other files; the tripwire checks consistency, not that the bytes are a writer's.
- **Requiring a covering board item** (case `decided` only). Cases `none` and `shared` are forms the press
  writes and the tripwire accepts; refusing them would send most presses to review and leave the person's
  press without effect where the board holds no open question.
- **Folding it into `lift_pr_verdict()`.** One function with two shapes changes the reasons that verdict gives
  its callers today (`lift-board-diff` on a lift-only PR), and agent-cadence names its carve-outs apart.
- **Reading `Owner:`** (ShiftLead's press refuses an entry the person owns). That refusal is ShiftLead's
  policy, not the format's, and the entry's lift is the same bytes either way.

## The SPEC text

The build adds these, word for word.

**In *The merge gate's verdicts*, after the paragraph that ends *(d), a PR only, is the consumer's: a direct
commit that answers a gate's item is refused by its own audit.*:**

> `lift_form(tree, tid, gate, repo)` (v3.2) returns `(case, items)` for open entry `tid` carrying `gate`, a
> `decision (<p>)`, read against the tree's own board: the form a lift of it takes. An item *lists another gated
> entry* when its Context entry or one of its `Parts:` ids is a bare `TD-n`, open in the tree's ledger, not
> `tid`, and carrying the same gate. Of the items `covers()` names covering the gate (states `open` and
> `decided`), the first case that holds is the form: `asked`, an undecided item that lists no other gated entry
> (the lift is the item's answer, the decide lift); `decided`, a decided item that lists no other gated entry
> (the lift has no suffix, and closes every such item `— lifted`); `shared`, an item that lists another gated
> entry (`; shared board item left open`); `none`, no item (`; no board item`). `items` are the items that
> decided the case, every one to close for `decided`. It refuses an entry the ledger does not hold open or that
> does not carry `gate`, a gate that is no decision, and a v1 ledger; a tree with no board is `none`.
>
> `ledger_lift_verdict(base_tree, head_tree, files, subject, commits, created_at, merged_at, repo)` (v3.2)
> returns `{carve_out, flags, review}` for a PR that lifts one entry's decision on the ledger, its arguments
> and its `flags` as `lift_pr_verdict()`'s. `carve_out` says the lift is the person's press, written whole by
> the writers; otherwise `review` names the first condition that fails, in this order:
> - a v3 board at the base and the head (`ledger-lift-no-board`, `ledger-lift-board-v2`), whose base declares
>   `People:` (`ledger-lift-no-people`);
> - the subject is a lift (`lift_subject_parts()`), and the PR is one commit (`ledger-lift-subject`);
> - every path in `files` is the subject's entry's open file or, for `decided`, a board item path, and the
>   ledger paths the trees change are that one file (`ledger-lift-files`);
> - the base ledger is v2 and holds the entry open carrying the subject's gate, and the head holds it open
>   (`ledger-lift-entry`);
> - the subject's person, the gate's person and the new `gate lifted` line's `by` are one name in any case,
>   which the base board lists on `People:`; `Answered by: any` admits no other (`ledger-lift-by`);
> - `lift_form()` of the base is not `asked` (`ledger-lift-asked`);
> - the head entry is `lift_gate(base text, gate, by, answer=label, suffix=S, today=T)` byte for byte, `label`
>   and `T` the new Log line's and `S` the form's suffix (`ledger-lift-bytes`); the board is unchanged for
>   `shared` and `none`, and for `decided` changes exactly each item the form names, its open file removed and
>   `item_path(id, C)` added as `edit_item(base file, "done", why="lifted", today=C)` (`ledger-lift-board`);
> - `T` and each `C` lie within a day of `created_at` and not after the merge (else `created_at + 1`)
>   (`ledger-lift-date`);
> - `flags` is empty (`ledger-lift-flagged`).
>
> The carve-out trusts what `lift_pr_verdict()`'s does: a diff that is one writer's output from the base, for
> one answer by the gate's person on `People:`. The Log line stays forgeable, and the sweep's audit and review
> are its backstop. A direct commit of this shape is the consumer's to refuse, as for the decide lift.

**In *Edits*, after the paragraph *The commit subject of a board write* (its last sentence, *`subject_kind()`
names a subject `edit`, `append`, `archive` or (a rank write) `queue`.*, becomes *`subject_kind()` names a
subject `edit`, `append`, `archive`, (a rank write) `queue` or (a ledger lift, v3.2) `lift`.*):**

> **The commit subject of a ledger lift** (v3.2) is one line, `<tool>: lift decision (<p>) on TD-n (session
> <name>)`, for a commit that lifts one entry's decision and writes nothing else but the closes the lift owes
> (*The merge gate's verdicts*, `lift_form()`): `<p>` the gate's person as the entry spells it, `<name>` the
> caller's session, else `n/a`. `lift_subject(tid, gate, tool, session=None)` writes it, refusing a `tid` that is
> not a bare `TD-n`, a gate that is no decision, and a tool or session that is not a token of
> `[A-Za-z0-9_.@/-]+`; `lift_subject_parts(line)` reads it back as `{tool, gate, id, session}`, or None.
> `edit_action()` and `subject_id()` read board writes alone, and are None for it.

**In *Versions*, after v3.1's paragraph:**

> **v3.2 adds the ledger lift's verdict** (*The merge gate's verdicts*, *Edits*): `ledger_lift_verdict()`, the
> carve-out for a PR that lifts one entry's decision on the ledger with no board answer, `lift_form()`, which
> names the form such a lift takes, and the ledger lift's commit subject, written by `lift_subject()` and read
> by `lift_subject_parts()`. No parse, field, Log line, item key or canonical form changes. One reading
> changes: `subject_kind()` names that subject `lift`, where v3.1 read None.

**In *Appendix: grammar*, beside `lift-suffix`:**

> ```
> lift-subject      ::= token ": lift decision (" name ") on TD-" digits " (session " token ")"
> ```

## The fixtures

All under `fixtures/verdict/`: a new `ledger_lift` list in `cases.json` beside `verdict`, `tripwire` and
`uncovered`, each case's expected `{carve_out, flags, review}` in `expected.json`, and a `lift_form` list
(each case's `tid`, `gate` and expected `[case, item ids]`). The base tree gains an entry carrying `decision
(<p>)` for each case; every name is invented (AGENTS.md).

`ledger_lift` (one case per condition and per form):
- `none` passes: one ledger file, `; no board item`, nothing covering.
- `shared` passes: a covering item that lists another open entry carrying the gate, board unchanged.
- `decided` passes: one open decided item closed `— lifted` into `archive/<YYYY-MM>/`; and two such items, both
  closed.
- `decided` with an undecided shared item beside it: `decided` wins, the shared item left open; passes.
- `asked` → `ledger-lift-asked`.
- a `decided` case that leaves the item open → `ledger-lift-board`; one that closes it with another why →
  `ledger-lift-board`.
- a `none` case logged with no suffix, and one logged `; shared board item left open` → `ledger-lift-bytes`.
- a `by` that is not the gate's person on an `Answered by: any` board → `ledger-lift-by`; the gate's person not
  on `People:` → `ledger-lift-by`; no `People:` → `ledger-lift-no-people`.
- a second ledger file changed, and a non-ledger path → `ledger-lift-files`; a board path in `files` for a
  `none` lift → `ledger-lift-files`.
- a `decide` subject, two commits, a subject naming another `TD-n` than the diff's → `ledger-lift-subject`,
  `ledger-lift-files`.
- an entry archived by the PR, and one not carrying the gate at the base → `ledger-lift-entry`.
- a Log date two days before `created_at`, and one after `merged_at` → `ledger-lift-date`.
- a v2 board at the base → `ledger-lift-board-v2`; no board → `ledger-lift-no-board`.

`lift_form`: each case above's base, plus a gate covered only through `Part of` (the parent's item with the
entry in `Parts:`), and a `<repo>#TD-n` in `Parts:` that is not counted.

The subject's writer and reader are held by `fixtures/grammar/` strings: the press's own subject read back; a
`<repo>#TD-n`, an `until` gate and a session with a space refused by `lift_subject()`; and `subject_kind()`'s
`lift`, with `edit_action()` and `subject_id()` None.

The unit tests (`tests/`) hold what a fixture cannot: the dates as aware datetimes, `commits` that is no count,
and `lift_form()`'s refusals.

## What a build does

One build: the SPEC text above, `lift_form()`, `ledger_lift_verdict()`, `lift_subject()`,
`lift_subject_parts()` and the `lift` kind in `ledgerboard/__init__.py`, the fixtures and the runner's
`ledger_lift` and `lift_form` lists, and the unit tests, in one PR. The release (v3.2) is Paul's; agent-cadence
then wires carve-out `lift` (its TD-262) on its vendor PR, and its techlead is told which release carries it.
ShiftLead needs no change: its subject is already this one.

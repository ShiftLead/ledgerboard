# TD-115: a merge-gate verdict for a PR that only lifts a gate

**Status:** Draft 5, 2026-11-15 (session lb-designer). Class: **wide** (a vendored, published format: a new
verdict, a new commit-subject kind and its writer, which both consumers vendor; cap 6 rounds, cadence.md §4.8).
Rounds: running, round 5 of 6 (the record: [docs/reviews/TD-115.md](../reviews/TD-115.md)).

**Entry:** [TD-115](../ledger/TD-115.md). Asked for by agent-cadence's grinder (its TD-262, 2026-11-15).

## The problem

ShiftLead's **Lift the hold** press, as its design writes it (its TD-1829, design §4.4 *Board write-back*: *Lift
the hold is a lift on the press*; its builds, TD-1831 among them, are not yet on its main), lifts a person's `decision (<p>)` gate itself, on the person's press, through this package's
`plan_lift()`. It lands one commit in one PR, subject and title `shiftlead: lift decision (<p>) on TD-n (session
n/a)`, and merges it at once, the press being its review. Its diff is the entry's lift, and on one board state
also the close of the board item the lift answers (below, *The press's four cases*). Neither carve-out the merge
gate has fits it:

- `lift_pr_verdict()` passes only a PR that answers one open board item (`Decided:`, a `decide` subject), so a
  lift-only PR goes to review at its first board condition (`lift-board-diff`, or `lift-reanswer` where the PR
  closes one decided item);
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
where the item covers it through `Part of`) or one of its `Parts:` ids is a bare `TD-n` open in the ledger (as
`_tree_ledger()` reads it, the tripwire's open entries), not
the pressed entry (by number, as the tripwire's `_num(x) != num` reads it), and carrying the same gate: the
test the tripwire's shared case makes. Where several items
cover the gate, the first case that holds decides:

- **(d) asked:** an open, undecided covering item lists no other gated entry. The press is refused and writes
  nothing: that item is the person's question, and its answer there is the decide lift (`lift_pr_verdict()`).
- **(b) decided:** an open, decided covering item lists no other gated entry. Every such item is closed in the
  same commit, `Closed: D — lifted` (the board writer's `done` with the why `lifted`; ShiftLead's text writes
  the v2 line's `— lifted.`, and a v3 item file has no period), and the lift has no suffix. Before it writes,
  the press runs a host-side claim check (ShiftLead §4.4, case (b)), which no tree shows and the format does
  not read.
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

- `lift_subject(tid, gate, tool, session=None)` writes it, the id as the caller gives it (the entry's heading
  spells it, `TD-12` or `TD-012`; condition 3 below finds either by number). It refuses a `tid` that is not a bare `TD-n`, a `gate`
  that is not `decision (<p>)` (an `until` or event lift has its own routes, and a host writes those), and a
  `tool` or `session` that is not a token of `[A-Za-z0-9_.@/-]+` (the Log's rule for who and a session).
- `subject_kind()` names it `lift`. `edit_action()` and `subject_id()` stay None for it: they read board writes,
  and a lift subject names an entry, not an item.
- `lift_subject_parts(line)` reads it back as `{"tool", "gate", "id", "session"}`, each part as written (`"n/a"`
  for a session written so, the id spelled as given), or None for any other line.

A lift of another repo's entry (`<repo>#TD-n`) has no subject here: its lift is a PR in that repo (ShiftLead's
§4.4), whose own subject names its own `TD-n`.

### D2. The lift's form is one function

`lift_form(tree, tid, gate, repo)` returns `(case, items)` for the open entry `tid` carrying `gate` in `tree`'s
ledger (found by number, and open as `_tree_ledger()` reads it: its file directly in `LEDGER_DIR`, its Status
open), read against the tree's own board (`load_board()`, as the verdicts read it): `case` one of `asked`,
`decided`, `shared`, `none` by the order above, and `items` the covering `BoardItem`s that decide it (for
`decided`, every item to close; for `shared` and `asked`, the items that matched; for `none`, empty), in the board's item order
(`load_board().items`). It refuses
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
as two carve-outs (agent-cadence's `decide-lift` and `lift`).

`carve_out` is True only when every one of these holds; else `review` names the first that fails, in this order:

1. **The board:** a v3 board at the base and the head (`ledger-lift-no-board`; a v2 one at either,
   `ledger-lift-board-v2`), as `lift_pr_verdict()` reads them. The base board declares `People:`
   (`ledger-lift-no-people`).
2. **The subject:** `lift_subject_parts(subject)` reads it, and the PR is one commit (`ledger-lift-subject`).
3. **The entry:** the base ledger is v2 and holds the subject's `TD-n` open (by number: `TD-12` is
   `TD-012.md`), carrying the subject's gate, and the head holds that file open (`ledger-lift-entry`). *Open* is
   the verdicts' reading: the file is directly in `LEDGER_DIR`, not under its `archive/`, and `_tree_ledger()`
   counts the entry open by its Status, so a file in the directory whose Status is archived is
   `ledger-lift-entry` at either end. *Carrying* is `_carried()`'s reading, the person's name compared in any
   case. Every check after this one reads that entry, so `lift_form()` (condition 7) cannot
   refuse inside the verdict.
4. **The files:** every path in `files` is that entry's open file or a board path `lift_pr_verdict()`'s
   `lift-files` admits (`_board_file_place()`: a file directly in `BOARD_DIR`, `README.md` among them, or one
   under its `archive/<YYYY-MM>/`), and every path whose text the trees change (read from the trees, never
   from `files`, as `lift_pr_verdict()` reads them) is that entry's open file or under `BOARD_DIR/`, so a changed
   `LEDGER_V1_PATH`, another entry or any other path is refused too (`ledger-lift-files`). Which board paths may change is condition 8's, by the form:
   a changed `README.md` is never an item's change, so it is `ledger-lift-board`.
5. **The Log line:** the head entry's Log adds exactly one line to the base's, as `_new_log()` reads it (the
   tripwire's reading, a multiset of lines, so a dropped old line is left to condition 8's bytes), and it is a `gate lifted:` line
   for the subject's gate with an `answer` (`log_line()`'s `via` `answer`, as `tripwire()` reads it)
   (`ledger-lift-log`). Its `label`, `by` and date `T` are what conditions 6 to 9 read.
6. **Who:** the subject's `<p>`, the gate's person and the line's `by` are one name, compared
   case-insensitively (the first two already agree by condition 3), and the base board lists it on `People:` (`ledger-lift-by`). `Answered by: any` admits
   no one else here: a lift by anyone but the gate's person takes review.
7. **The form:** `lift_form(base_tree, TD-n, gate, repo)` is not `asked` (`ledger-lift-asked`: the item is the
   person's question, and its answer is the decide lift).
8. **The bytes:** the head entry is `lift_gate(base text, gate, by, answer=label, suffix=S, today=T)` byte for
   byte, `S` the form's suffix: none for `decided`, `shared board item left open` for `shared`, `no board item`
   for `none`; any `Refused` from `lift_gate()` (a waiting-only label, its `canonical()` or read-back check) is
   a mismatch too (`ledger-lift-bytes`). The board's changes are
   none for `shared` and `none`; for `decided`, exactly each item `lift_form()` names, its open file removed and
   `item_path(id, C)` added, `C` the head file's `Closed:` date, as `edit_item(base file, "done", why="lifted",
   today=C)` byte for byte; and each such item's base `Decided:` names the gate's person (`decided_by`, any
   case), so the close rests on that person's own merged answer and on no one else's (`ledger-lift-board`).
   `C` is the head file's `Closed:` date, passed to `item_path()` as `C.isoformat()`; a head file for the id
   with no readable `Closed:`, or more than one head file for the id, is `ledger-lift-board`. The entry's bytes
   are judged before the board's, so a PR failing both is `ledger-lift-bytes`.
9. **The dates:** `T`, a UTC ledger date, lies within a day of `created_at` and not after the merge (else
   `created_at + 1`), as `lift_pr_verdict()`'s (c) windows its `T`; each `C`, a board date written by the
   board's local clock, lies from `created_at − 1` to the merge date (else `created_at`) `+ 1`, as that verdict
   windows its `Decided:` date D, since the board's local day runs up to a day from UTC (`ledger-lift-date`).
   `C` is not tied to `T`: the two writers each read their own clock.
10. **No flag:** `flags` is empty (`ledger-lift-flagged`). A PR that passes 1–9 raises none by construction; the
   condition keeps a future tripwire rule from being skipped by this carve-out.

**What raises, and what is a reason.** The verdict starts as `lift_pr_verdict()` does: `tripwire()` first (which
checks `repo` and reads the Log of every entry open at both ends), then `created_at`, `merged_at` (not before
`created_at`) and `commits`. A `Refused` from any of these escapes, as it does from `lift_pr_verdict()`: an entry
open at both ends with two Log sections makes the tripwire, and so both verdicts, raise for any PR, and the
consumer meets it whichever verdict it calls, since the tripwire runs on every PR. Past them, what the verdict
reads is a reason, never a refusal: an item file the board reader skips (`parse_item()` gives None, so
`load_board()` leaves it out), or a `Refused` or `ValueError` from `edit_item()` or `item_path()`, is
`ledger-lift-board`; `lift_gate()`'s refusals are `ledger-lift-bytes` (condition 8).

As for `lift_pr_verdict()`, (d) is the consumer's: a direct commit with this shape is refused by its own audit.

### D4. What stands in for the person's answer

The verdict trusts what `lift_pr_verdict()`'s carve-out trusts:

- **The shape is one writer's output.** Every byte the PR changes is recomputed from the base: one entry's lift,
  with the suffix the base board dictates (not one the PR chose), and in case `decided` the closes the lift
  owes. Nothing else changes: no code, no other entry, no other item.
- **The answerer is the gate's person, on the board's `People:`.** This is stricter than the decide carve-out,
  which admits anyone listed under `Answered by: any`.
- **The question existed, or was already answered.** In case `decided` the base board holds the gate's
  person's own `Decided:` on each item closed (condition 8), in the PR's base, which the consumer's base row
  holds to be the default branch, as for the decide carve-out; the open, decided item is
  a work order the person answered (as the writers since v2.7 leave it, an answer that lifts or only waits
  closes its item, `closes()`; a v2.4–v2.6 writer or a hand edit could leave a lifting answer open, which
  condition 8 closes all the same). In case `none` there is no open question for the lift to bypass; in case
  `asked` there is one, and the lift takes review, since that item's answer is the way. Case `shared` does take
  the entry out of an open question, below.

It is not the same reach as the decide carve-out, and three differences are accepted, each a form ShiftLead's
press writes (its §4.4 cases (a), (b), (c)) on Paul's ruling (ShiftLead TD-1829, 2026-11-14: *lifts are allowed
by a button press*):

- **Case `none` needs no question on the board.** Through the decide carve-out, a gate with no covering item
  would first need an item added (agent-cadence's `board-append` carve-out) and then answered: two PRs. Here it
  is one.
- **Case `decided` supersedes the person's recorded work order** in one unreviewed PR, where the decide
  carve-out refuses a re-answer (`lift-reanswer`). The person's own answer stays on the closed item; the lift
  ends the order, which is what the press means.
- **Case `shared` takes one entry out of an open shared question** with no `Decided:`, leaving the item asking
  the others. The decide carve-out cannot, since a shared item's answer must not speak for the entries left
  (v2.7); today only a caller that passes the suffix writes it (the ledger writer's `set` and `lift
  --shared-item`), and each takes review.

**Where the verdict is stricter than the press.** Two presses ShiftLead's §4.4 lands take review here: a case
(b) close of an item whose `Decided:` names someone else (an `Answered by: any` board) or no one (a `Decided:`
with no `by`), which condition 8 refuses, and a press on a board with no `People:` (its `by` the git author), which condition 1 refuses. Each
lands, then fails the consumer's review row, as a lift-only PR does today; ShiftLead may refuse the first at the
press. Both are kept: the carve-out rests on the gate's person's own answer and on a board that names its
people.

**Who would forge it.** The forger that matters is a session writing the press's exact bytes to unblock its own
entry: it merges with no person involved. The PR's author cannot tell the two apart, since every session pushes
as the person's one account, so no author check is made. What catches it is the consumer's audit: agent-cadence
lists a carve-out's merges apart as tool merges in its weekly read (its cadence.md §4.2), and its TD-262 wiring
should list `lift` merges so too, which its techlead is told.

So the worst a forged PR does is lift one gate of an entry whose person is on the board, and in case `decided`
also close that person's open work orders on the gate; a forged decide PR can do the first but not the close.

**`; board <repo>`.** The suffix comes from this repo's board alone, so a lift written `; board <repo>` never
matches the bytes (`ledger-lift-bytes`) and takes review; a gate asked only on another repo's board is `none`
here, passing with `; no board item` and leaving that item open, as ShiftLead's §4.4 accepts (the lift's `by`
is on this board's `People:`). **What is the backstop.** Nothing in the format re-reads such a lift once it merges: the sweep's
audit reads only `; board <repo>` lifts, and review is what the carve-out skips. The record is the entry's
`gate lifted` Log line, which the person's ledger shows, and the consumer's own audit of carve-out merges
(agent-cadence's weekly read lists them) is the backstop outside the format. Requiring more, such as a host log
witnessing the press, would put the machine and its logs into the package, and a verdict that reads one
machine's log is not the same on every machine.

### D5. The release

A minor release, **v3.2**: the next minor after the newest *Versions* paragraph on main, v3.1's. v3.1 (TD-109's
`decision-missing`) is on main but not yet tagged (the last stamped is v3.0), and `release.sh` stamps whatever
main holds, so a v3.1 cut after this build merged would carry it under marks that say v3.2. The build therefore
waits for v3.1's tag: its entry is `Blocked by: event (v3-1-tagged)` and carries its own `**Event
(v3-1-tagged):**` section (a gate's section is its own entry's, `event-section`), with the same check TD-109's
carries, `check: ref-includes ShiftLead/ledgerboard@v3.1 ce8b7687e9b47783c3f0639431eea8541f443a5e` (TD-112's
merge), which passes once the tag exists. Should TD-111's
build reach v3.2 first, the two share v3.2's *Versions* paragraph. It is one new verdict, one new helper, one new subject kind and its writer and reader. No
parse, field, Log line, item key or canonical form changes. One reading changes: `subject_kind()` returns `lift`
for a subject that read None before, so a consumer that branched on None for it reads `lift` once it vendors
v3.2. Neither consumer's code reads that subject's kind today; agent-cadence's TD-262 wires the verdict as its
carve-out `lift`. v3.1 (`decision-missing`) is in SPEC and on main but not yet tagged, so a consumer that
vendors v3.2 takes v3.1's refusals with it (SPEC *Versions*, v3.1's paragraph).

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

**In *The merge gate's verdicts*, its first sentence** reads *(v2.4) are pure functions over a PR's **trees***
in place of *(v2.4) are three pure functions over a PR's **trees***, since v3.2's makes four and the paragraph
names none by count again.

**In *The merge gate's verdicts*, after the paragraph that ends *(d), a PR only, is the consumer's: a direct
commit that answers a gate's item is refused by its own audit.*:**

> `lift_form(tree, tid, gate, repo)` (v3.2) returns `(case, items)` for open entry `tid` (found by number, and
> open as the tripwire reads the ledger: its file directly in `LEDGER_DIR`, its Status open) carrying `gate`, a
> `decision (<p>)`, read against the tree's own board: the form a lift of it takes. An item *lists another gated
> entry* when its Context entry or one of its `Parts:` ids is a bare `TD-n`, open in the tree's ledger (as the
> tripwire reads its open entries), not `tid`'s number, and carrying the same gate. Of the items `covers()` names covering the gate (states `open` and
> `decided`), the first case that holds is the form: `asked`, an undecided item that lists no other gated entry
> (the lift is the item's answer, the decide lift); `decided`, a decided item that lists no other gated entry
> (the lift has no suffix, and closes every such item `— lifted`); `shared`, an item that lists another gated
> entry (`; shared board item left open`); `none`, no item (`; no board item`). `items` are the items that
> decided the case, every one to close for `decided`, in the board's item order. It refuses an entry the ledger does not hold open or that
> does not carry `gate`, a gate that is no decision, and a v1 ledger; a tree with no board is `none`.
>
> `ledger_lift_verdict(base_tree, head_tree, files, subject, commits, created_at, merged_at, repo)` (v3.2)
> returns `{carve_out, flags, review}` for a PR that lifts one entry's decision on the ledger, its arguments
> and its `flags` as `lift_pr_verdict()`'s. `carve_out` says the diff is exactly the writers' lift of one gate by its
> person, the shape the person's press writes; otherwise `review` names the first condition that fails, in this order:
> - a v3 board at the base and the head (`ledger-lift-no-board`, `ledger-lift-board-v2`), whose base declares
>   `People:` (`ledger-lift-no-people`);
> - the subject is a lift (`lift_subject_parts()`), and the PR is one commit (`ledger-lift-subject`);
> - the base ledger is v2 and holds the subject's entry open (by number; its file directly in `LEDGER_DIR` and
>   its Status open) carrying the subject's gate (the person in any case), and the head holds it open
>   (`ledger-lift-entry`);
> - every path in `files` is that entry's open file or a board path `lift-files` admits (a file directly in
>   `BOARD_DIR`, or under its `archive/<YYYY-MM>/`), and every path the trees change is that file or under `BOARD_DIR/`
>   (`ledger-lift-files`);
> - the entry's Log gains exactly one line (as the tripwire reads new lines), a `gate lifted:` line for the gate with an `answer`
>   (`ledger-lift-log`), whose `label`, `by` and date `T` the checks below read;
> - the subject's person, the gate's person and that line's `by` are one name in any case, which the base
>   board lists on `People:`; `Answered by: any` admits no other (`ledger-lift-by`);
> - `lift_form()` of the base is not `asked` (`ledger-lift-asked`);
> - the head entry is `lift_gate(base text, gate, by, answer=label, suffix=S, today=T)` byte for byte, `S` the
>   form's suffix, any refusal from `lift_gate()` failing too (`ledger-lift-bytes`); the board is unchanged for
>   `shared` and `none`, and for `decided` changes exactly each item the form names, its open file removed and
>   `item_path(id, C)` added as `edit_item(base file, "done", why="lifted", today=C)`, `C` the head file's
>   readable `Closed:` date, each such item's base `Decided:` naming the gate's person in any case
>   (`ledger-lift-board`); the entry's bytes are judged before the board's;
> - `T` lies within a day of `created_at` and not after the merge (else `created_at + 1`), and each `C` from
>   `created_at − 1` to the merge date (else `created_at`) `+ 1`, the board's local day running up to a day
>   from UTC (`ledger-lift-date`);
> - `flags` is empty (`ledger-lift-flagged`).
>
> The carve-out trusts what `lift_pr_verdict()`'s does: a diff that is one writer's output from the base, for
> one answer by the gate's person on `People:`. Unlike a decide lift it needs no question on the board, in
> `shared` it takes one entry out of an open shared question, and in `decided` it ends a work order the person
> answered. Its suffix is read from this repo's board alone, so a `; board <repo>` lift takes review
> (`ledger-lift-bytes`). As for `lift_pr_verdict()`, a `Refused` from `tripwire()`, which runs first, or
> from the dates and `commits` escapes; past them a text the verdict cannot read is a reason: an item file the
> board reader skips, or a refusal from `edit_item()` or `item_path()`, is `ledger-lift-board`, and any refusal
> from `lift_gate()` is `ledger-lift-bytes`. The Log line stays forgeable, and nothing in the format
> re-reads the lift once it merges (the sweep's audit reads `; board <repo>` lifts alone): the consumer's own
> audit is its backstop, and a direct commit of this shape is the consumer's to refuse, as for the decide lift.

**In *Edits*, after the paragraph *The commit subject of a board write* (its last sentence, *`subject_kind()`
names a subject `edit`, `append`, `archive` or (a rank write) `queue`.*, becomes *`subject_kind()` names a
subject `edit`, `append`, `archive`, (a rank write) `queue` or (a ledger lift, v3.2) `lift`.*):**

> **The commit subject of a ledger lift** (v3.2) is one line, `<tool>: lift decision (<p>) on TD-n (session
> <name>)`, for a commit that lifts one entry's decision and writes nothing else but the closes the lift owes
> (*The merge gate's verdicts*, `lift_form()`): `<p>` the gate's person as the entry spells it, `<name>` the
> caller's session, else `n/a`. `lift_subject(tid, gate, tool, session=None)` writes it, refusing a `tid` that is
> not a bare `TD-n`, a gate that is no decision, and a tool or session that is not a token of
> `[A-Za-z0-9_.@/-]+`; `lift_subject_parts(line)` reads it back as `{tool, gate, id, session}`, each part as
> written (`n/a` too), or None.
> `edit_action()` and `subject_id()` read board writes alone, and are None for it.

**In *Versions*, after v3.1's paragraph:**

> **v3.2 adds the ledger lift's verdict** (*The merge gate's verdicts*, *Edits*): `ledger_lift_verdict()`, the
> carve-out for a PR that lifts one entry's decision on the ledger with no board answer, `lift_form()`, which
> names the form such a lift takes, and the ledger lift's commit subject, written by `lift_subject()` and read
> by `lift_subject_parts()`. No parse, field, Log line, item key or canonical form changes. One reading
> changes: `subject_kind()` names that subject `lift`, where v3.1 read None.

**In *Appendix: grammar*, beside `lift-suffix`:**

> ```
> lift-subject      ::= log-token ": lift decision (" person ") on TD-" digit+ " (session " log-token ")"
> ```

**Under that block, in prose (what a production cannot say):**

> `lift-subject` (v3.2) is a ledger lift's commit subject, judged by `lift_subject_parts()` not None. The reader
> matches the whole line, nothing after its `)` (no trailing newline), and `lift_subject()` writes the gate as
> `_one_gate()` spells it, `decision (<p>)` with the keyword's case and the space before `(` normalised; a gate
> `_one_gate()` refuses (`decision (Ann )`, say) is refused.

**And the appendix's first sentence** gains *v3.2: the ledger lift's commit subject;* before *later releases add
the rest*.

## The fixtures

All under `fixtures/verdict/`: a new `ledger_lift` list in `cases.json` beside `verdict`, `tripwire` and
`uncovered`, each case's expected `{carve_out, flags, review}` in `expected.json`, and a `lift_form` list
(each case's `tid`, `gate` and expected `[case, item ids]`). The shared `verdict/base/` is
left as it is, since every existing case reads it: each new case lays its own entries and items over it in
`cases/<name>/base/` (the existing base has no `none` case of its own, its `decision (pat)` gates being covered);
every name is invented (AGENTS.md).

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
  `none` lift whose board is unchanged passes (`files` admits item paths; condition 8 judges what changed).
- a `decide` subject → `ledger-lift-subject`.
- two commits → `ledger-lift-subject`.
- a subject naming another `TD-n` than the diff's, an open entry not carrying the gate → `ledger-lift-entry`.
- a subject naming another `TD-n` than the diff's, one carrying the gate whose file is unchanged →
  `ledger-lift-files`.
- a changed `docs/technical_debt.md` the trees show and `files` omits → `ledger-lift-files`.
- an entry archived by the PR, one not carrying the gate at the base, and one whose open file the head drops
  → `ledger-lift-entry` (the entry check runs before the files check, so an archive's second path is never
  reached).
- a `decided` item whose base `Decided:` names someone else (an `Answered by: any` board) → `ledger-lift-board`.
- a `C` a day after the merge passes; a `T` a day after the merge → `ledger-lift-date`.
- a Log date two days before `created_at` → `ledger-lift-date`.
- a `C` two days before `created_at` → `ledger-lift-date`.
- a v2 board at the base → `ledger-lift-board-v2`; no board → `ledger-lift-no-board`.
- an `asked` item beside a `decided` one → `ledger-lift-asked` (`asked` is tried first).
- a `decided` close filed under the wrong `archive/<YYYY-MM>/` → `ledger-lift-board`.
- a `decided` item whose `Decided:` names no one → `ledger-lift-board`.
- a `C` two days after the merge → `ledger-lift-date`.
- a `decided` PR that also closes the shared item beside it → `ledger-lift-board`; a `shared` and a `none` PR
  that change any board item → `ledger-lift-board`.
- a v2 board at the head only → `ledger-lift-board-v2`.
- the Log: no new line, two new lines, a `gate lifted` line for another gate, an `override:` lift, and a note
  in place of the lift → `ledger-lift-log`; a waiting-only label (`lift_gate()` refuses it) →
  `ledger-lift-bytes`.
- a head entry with two Log sections raises `Refused` (a unit test, as for `lift_pr_verdict()`).
- a `none` lift written with no suffix that also changes an item → `ledger-lift-bytes` (the entry's bytes are
  judged before the board's).
- a `decided` close whose head file has no readable `Closed:`, and an id with two head files →
  `ledger-lift-board`.
- a subject spelling the person `paul` for an entry's `decision (Paul)` passes.
- `lift_subject()` given `decision (Ann )` refuses (a unit test); given `Decision(Ann)` writes `decision (Ann)`.
- a subject naming `TD-12` for the file `TD-012.md` passes.
- a v1 ledger → `ledger-lift-entry`; a `README.md` the trees change (and `files` names) → `ledger-lift-board`; a dropped old
  Log line beside the lift → `ledger-lift-bytes`; a `; board other/repo` lift → `ledger-lift-bytes`.
- `ledger-lift-flagged` is unreachable by construction, so no fixture holds it; a unit test patches
  `tripwire()` to return a flag and expects it.

The runner guards the new lists apart from `lift_pr_verdict()`: with no `ledger_lift_verdict` (or no
`lift_form`) on the module, its list reports `missing`, so a module older than v3.2 still runs the rest.

`lift_form`: each case names a `ledger_lift` case whose base it reads (one that `lift_form()` accepts; its
refusals are the unit tests'), plus two with overlays of their own: a gate covered only through `Part of` (the parent's item with the
entry in `Parts:`), and a `<repo>#TD-n` in `Parts:` that is not counted.

The subject's writer and reader are held by `fixtures/item/cases.json`'s subject block, beside its `subjects`,
`subject_kinds`, `edit_actions` and `subject_ids`, in a new `lift_subjects` key (the build adds a
`hasattr(L, "lift_subject")` guard to that block, reporting `lift_subjects` as `missing` for a module older than
v3.2): the press's own subject read back; a
`<repo>#TD-n`, an `until` gate and a session with a space refused by `lift_subject()`; and `subject_kind()`'s
`lift`, with `edit_action()` and `subject_id()` None.

The grammar appendix's new `lift-subject` production is a start (no other production reaches it), so
`fixtures/grammar/cases.json` gains a `lift-subject` start with strings each way for it and for the productions
it reaches (`log-token`, `person`, `person-part`, `digit`), the new start carrying all four itself
(the test reads each start's own groups), and `fixtures/run.py`'s
`grammar_cases` a judge for it, `lift_subject_parts()` not None (`tests/test_grammar.py` holds every start and
production to that).

The unit tests (`tests/`) hold what a fixture cannot: a bad `repo`, which raises; the dates as aware datetimes, `commits` that is no count,
and `lift_form()`'s refusals.

## What a build does

One build, `Blocked by: event (v3-1-tagged)` (D5): the SPEC text above, `lift_form()`, `ledger_lift_verdict()`, `lift_subject()`,
`lift_subject_parts()` and the `lift` kind in `ledgerboard/__init__.py`, the fixtures and the runner's
`ledger_lift` and `lift_form` lists, and the unit tests, in one PR. The release (v3.2) is Paul's; agent-cadence
then wires carve-out `lift` (its TD-262) on its vendor PR, and its techlead is told which release carries it.
ShiftLead needs no change: its subject is already this one.

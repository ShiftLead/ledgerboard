# TD-051: answering a parent's item when a listed part was archived

**Status:** Draft 1, 2026-11-05 (session lb-designer). Class: **wide** (a vendored, published format: a new
`decide_lift()` keyword and what `board.py decide` and `lift_pr_verdict()` do with it, which both consumers vendor;
cap 6 rounds, cadence.md §4.8). Rounds: **ended by the stop rule after round 1**, 2026-11-05 (the record:
[docs/reviews/TD-051.md](../reviews/TD-051.md)). Build-changing findings: the design review 0; the fact-checks apart
1 (F1), and the closing fact-check 1 (F13, a sentence in D4 the code never reaches, removed). F8–F15 are applied
and read by no design review. Paul said **Go** on 2026-11-05 (the board's decide item): the build is
[TD-052](../ledger/archive/TD-052.md), with F8–F15 in its Fix.

**Entry:** [TD-051](../ledger/archive/TD-051.md). Found while designing TD-050 ([its plan](TD-050-parts-writer.md),
*Why the check is at write time*).

## The problem

A `decide` item for a parent lists its parts (`Parts:`), and one answer lifts the gate on every listed part that
still carries it (SPEC *The decide lift*). A part can be archived while the item waits: done another way, dropped,
superseded. SPEC says what happens to a listed part that no longer carries the gate: it is skipped, and the Context
entry's Log says so (`gate lift skipped: <id> no longer carries <gate>`). An archived entry carries nothing, so the
answer should go through. It does not:

- **`board.py decide`** (`_decide_ledger`, `ledgerboard/board.py`) reads each listed id through
  `Ledger.entry_file()` and keeps only the ones not archived, so `decide_lift()` meets the archived part as missing
  and refuses the whole answer: `TD-n, a part the item lists, is not among the entries given`. The person is left
  a question no press can answer.
- **`lift_pr_verdict()`** (`ledgerboard/__init__.py`) hands `decide_lift()` and `closes()` the archived texts too
  (`b_open.get(n, b_closed.get(n))`), so it judges by the archived entry's Status. The ledger writer and the
  verdict therefore disagree today: the verdict accepts a skip the writer cannot write.
- **Status is not where an entry is archived.** SPEC *The ledger as a directory* defines archived as being in
  `archive/`: "Open and archived stay two texts, so *every blocker is archived* is still a test of which text a
  heading is in". *Superseded and dropped* says an archived entry may read `Open`. `_carried()`, which
  `decide_lift()` and `closes()` use, judges by Status alone. So a text from `archive/` whose Status reads `Open`
  and whose `Blocked by` still names the gate (a file moved by hand) reads as carrying the gate. It would be
  lifted, inside the archive, and it would hold the item open.

## Options weighed

- **A. `decide_lift()` gains `archived=()`, the ids the caller read from the archive.** An id there is archived
  whatever its text says, so it is skipped and logged; the caller never hands over an archived text. `closes()`
  needs nothing new: its rule already says an id `entries_after` lacks carries nothing, and the callers give it open
  texts only. The keyword's name and meaning (the ids the caller read from the archive) match TD-050's
  `parts_problems(item_line, entries, archived=())`. The precedence differs, and on purpose. `parts_problems()`
  takes archived texts inside `entries` too, and a number in `archived` wins there: it judges a snapshot and
  reports `archived`. `decide_lift()` is never given an archived text, and open wins (D2), as the writer finds a
  file.
- **B. `_decide_ledger` hands `decide_lift()` the archived texts, and leaves them out of what `closes()` reads.**
  This still judges archived by Status inside `decide_lift()`, so the hand-moved `Open` file is lifted in the
  archive. It also leaves the verdict and the writer each choosing what to hand over, which is how they drifted
  apart in the first place. Rejected.
- **C. `decide_lift()` skips any listed id it is not given, in place of refusing it.** This would lose the
  refusal of a mistyped or unknown part (`missing_part_refused` in `fixtures/lift`). That refusal is the snapshot
  check on an item written by hand. Rejected.
- **D. `closes()` gains `archived=()` too.** It would read the same as leaving archived ids out of
  `entries_after`, at the cost of a second argument that callers must keep in step with the first. Rejected.
  Instead, SPEC says what callers give it.

## Decisions

**D1. Option A.** It ships in the next tagged release after v2.5, written v2.6 here, beside TD-050's `Parts:`
writer: v2.5 was tagged 2026-11-05 (#158) without it. The target design (§7.1's note of 2026-11-05) calls its
next Status release v2.6; whichever is tagged first takes v2.6, and if the Status release is, the build writes
the number of the release it ships in where this plan writes v2.6. It is no version
event: no key, line form or canonical entry form changes. A caller written for v2.4 passes no `archived` and
gets exactly v2.4's result.

**D2. What `decide_lift(…, archived=())` does.**
- `archived` is an iterable of ids. A member counts when `_is_id()` accepts it, which is how `decide_lift()`
  already reads `entries`' keys (`TD-` and a `\d+` run, compared by number through `_num()`). This is broader
  than `parts_problems()`'s `TD-[0-9]{1,18}`, and deliberately so: the two inputs of one function read alike. A
  member `_is_id()` refuses, or one that is not a string, is ignored.
- **Open before archived.** If a number is both a key of `entries` and in `archived`, it is read from its text,
  as `entry_path()` finds the open file first. (`v2_problems()` names the two files; this function does not.)
- **The Context entry archived** (its number in `archived` and not among `entries`) is refused with the message
  that an archived Context gets today: `<ref>, the item's Context entry, is archived — the answer lifts nothing;
  it takes review`.
- **A listed part archived** (its number in `archived` and not among `entries`) passes the snapshot check. Its
  `Part of` is not read: there is no text, and a part that lifts nothing cannot lift the wrong thing. On a lifting
  answer it is skipped, and logged on the Context entry with the existing line
  `gate lift skipped: <id> no longer carries <gate>`. `<id>` is spelled as the first member of its number in
  `archived` spells it, in iteration order (the callers pass a list, one member a number, as its heading spells
  it), and
  the gate as the Context entry carries it (else as the item names it), as today. A waiting-only answer or a work
  order writes nothing for it, as for any part that no longer carries the gate.
- **Skip lines are in the line's order.** Every skipped part is logged in the `Parts:` line's order, whether it
  was an open part that dropped the gate or an archived one. That is the order today's loop already writes.
- A part in neither `entries` nor `archived` is still refused as missing.

**D3. `closes()` is unchanged in code.** SPEC states the contract that both callers now meet: `entries_after`
holds open entries' texts, so an archived part, which is left out, carries nothing.

**D4. `board.py decide`.** `_decide_ledger` passes each listed id that `entry_file()` finds in `archive/` (its
`archived` flag) as an id in `archived`, spelled as the archive file's heading spells it. It never passes it as a
text. `closes()` reads the open texts after the write, as now. `--board-only` changes nothing: it already reads
open texts alone, so an archived part already carries nothing there. A fixture pins that behaviour. An id that
`entry_file()` refuses (in neither directory) is left out, as now, and `decide_lift()` refuses it as missing. An
archive file with no entry or a heading of another number never reaches this: `Ledger.open` refuses the whole
ledger first (`v2_problems()`, exit 2). The archived id is read as `entries(led.files[p])[0]["id"]`. No fixture is
needed for it.

**D5. `lift_pr_verdict()`.** For this repo's entry, the verdict splits the base ledger by **location**, as
`load()`'s two texts do, not by Status as `_tree_ledger()` does:
- the Context and `Parts:` ids that the base ledger's open text holds go to `entries` as texts (an open-directory
  file whose Status reads `Resolved` stays a text, and `_carried()` reads it as carrying nothing, as the writer
  does);
- those that only its archive text holds go to `archived`, as the archive heading spells them;
- `closes()` reads `{**entries, **result}`, which holds open texts only.

The verdict then hands `decide_lift()` exactly what the writer hands it, and a PR that `board.py decide` wrote
after a skip is the PR the verdict recomputes. A PR that also edits the archived part's file is sent to review
(`lift-files`): the result never names that file. `_tree_ledger()` keeps its Status split for the tripwire and
`uncovered_decisions()`, which use it for other things. The verdict reads the location split through a helper
of its own.

**D6. Out of scope.** The gate sweep's `entries` are the ledger's and the archive's texts merged, read as open
"unless its Status is an archived one" (SPEC *The gate sweep*). So a hand-moved `Open` file in `archive/` reads
as open there too. That is the same Status-versus-location gap in a different function, with a different
remedy (the sweep has no `archived` input). It is noted here and not changed. No consumer change is required.
A consumer that calls `decide_lift()` itself gains the skip by passing `archived`, and its vendor PR says so;
nothing is filed in another repo.

## The `SPEC.md` text

Each quote is the text the build makes, in the section named. **Bold** in a "becomes" quote is SPEC's own bold.

**1. *The board*, *The decide lift*.** The opening sentence's call and inputs:

> `decide_lift(item_line, entries, label, by, today, board_people, answered_by)` returns `{id: new text}` for each
> entry it changes, from the base item line, the base texts of the Context entry and each `Parts:` id, and the base
> board's `People:` (None: none, and the board checks below are skipped) and `Answered by:`.

becomes

> `decide_lift(item_line, entries, label, by, today, board_people, answered_by, archived=())` returns `{id: new
> text}` for each entry it changes, from the base item line, the base texts of the Context entry and each `Parts:`
> id that the ledger's directory holds, whatever its Status (`entries`), the ids of those only its `archive/` holds
> (*The ledger as a directory*; `archived`, v2.6: each `TD-n`
> read as `entries`' keys are, by number, any other member ignored; an id among `entries` is read from its text even when `archived`
> holds its number, open before archived as `entry_path()`), and the base board's `People:` (None: none, and the
> board checks below are skipped) and `Answered by:`.

The first bullet's skip clause:

> each listed part that no longer carries it is logged on the Context entry as `gate lift skipped: <id> no longer
> carries <gate>`;

becomes

> each listed part that no longer carries it, an archived one among them (whatever its Status reads; its `Part of`
> is not read), is logged on the Context entry as `gate lift skipped: <id> no longer carries <gate>`, in the
> `Parts:` line's order, an archived part spelled as the first member of its number in `archived` spells it;

The refusals:

> a Context entry missing or archived; a `Parts:` id missing, of another repo, or not `Part of` the Context entry
> (the snapshot does not match);

becomes

> a Context entry missing or archived (in `archived`, or its Status an archived one); a `Parts:` id in neither
> `entries` nor `archived`, of another repo, or, given as a text, not `Part of` the Context entry (the snapshot
> does not match);

**2. *The board*, *Closing on the answer*.**

> neither that entry nor any `Parts:` id (an id `entries_after` lacks carries nothing).

becomes

> neither that entry nor any `Parts:` id (an id `entries_after` lacks carries nothing). Its callers give it the
> open entries' texts alone, so an archived part, left out, carries nothing (v2.6).

**3. *The board writer*, the decide-lift bullet.**

> or neither: the entries `decide_lift()` changes, from their texts as they stand (its `People:` and `Answered by:`

becomes

> or neither: the entries `decide_lift()` changes, from their texts as they stand, each listed id the ledger's
> `archive/` holds passed in `archived` (as its heading spells it), never as a text (v2.6) (its `People:` and
> `Answered by:`

**4. *The merge gate's verdicts*, (c).**

> `decide_lift()` of the base line and the base texts of its Context and `Parts:` entries, with the base board's
> `People:` and `Answered by:`, accepts the answer;

becomes

> `decide_lift()` of the base line, the base texts of its Context and `Parts:` entries that the base ledger's
> directory holds, whatever their Status, and, in `archived`, the ids of those only its `archive/` holds (by which
> text holds the heading, not by Status; v2.6), with the base board's `People:` and `Answered by:`, accepts the answer, and `closes()` reads the
> open texts after it;

**5. *Versions*.** A paragraph after v2.5's others:

> **v2.6 answers a parent's item whose part was archived** (*The decide lift*): `decide_lift()` gains
> `archived=()`, and `board.py decide` and `lift_pr_verdict()` pass the archive's ids in it, so such a part is
> skipped and logged where v2.4 refused the answer (the writer) or judged the part by its Status (the verdict). A
> caller that passes no `archived` gets v2.4's result.

## Fixtures

Every name below is invented (`pat`, `robin`), never a person's (AGENTS.md).

`fixtures/lift`: the runner's `decide_lift` case gains an optional `archived` list, passed only for a case that
names it. On a module whose `decide_lift()` takes no `archived` (`inspect.signature`), each such case reports
`missing`, as the runner's `hasattr` guards report an older module, so a v2.4 module is never handed the keyword.
The runner imports `inspect`, and the `closes` case that reads an archived case's result (`after()`) falls under
the same guard, so a `missing` result never reaches `decided[…]["ok"]`. There is a new entry file, `entries/TD-506.md`, which is `Part of: TD-500`, `**Status:** Open` and
`**Blocked by:** decision (pat)`: the hand-moved worst case. There is a new line, `go_parts_archived`, with Context
`TD-500 decision (pat)` and `Parts: TD-501, TD-506`. The cases:
- `archived_part_skipped`: `Go`, `entries` TD-500 and TD-501, `archived` `["TD-506"]`. TD-500 and TD-501 are
  lifted, and TD-500's Log gains `gate lift skipped: TD-506 no longer carries decision (Pat)` (TD-500 spells the gate `decision (Pat)`);
- `archived_part_kept_waiting`: `Not yet`, the same inputs. `kept waiting` goes on TD-500 and TD-501, and nothing
  is written for TD-506;
- `archived_part_no_input`: `Go`, the same `entries` as `archived_part_skipped`, no `archived`. Refused as missing (v2.4's result, kept);
- `archived_part_also_open`: `Go`, TD-506 in both `entries` and `archived`. It is read from its text, which reads
  `Open`, so it is lifted (open before archived);
- `archived_context_refused`: `Go`, `archived` `["TD-500"]`, `entries` TD-501 and TD-506. Refused as an archived
  Context;
- `archived_member_ignored`: `Go`, `archived` `["TD-506", "x", "other#TD-506"]`. The same result as
  `archived_part_skipped`;
- `archived_part_skipped_event`: new entry `TD-508` (`**Blocked by:** event (ships)`, with its `Event (ships):`
  section and `check:` line, as `TD-530` has) and line `go_event_archived`,
  Context `TD-508 event (ships)`, `Parts: TD-509`, `Answers: Drop the gate | Keep waiting. Lifts: Drop the gate.`;
  `Drop the gate`, `entries` TD-508, `archived` `["TD-509"]`, `by` `pat`, `people` `["pat"]` (no file is needed: an archived part is an id). TD-508
  is lifted and logs `gate lift skipped: TD-509 no longer carries event (ships)`;
- `archived_part_two_spellings`: `archived` `["TD-006", "TD-6"]` against `Parts: TD-501, TD-6` on a line of its
  own (`go_parts_spelled`). The skip line spells `TD-006`, the first member of the number;
- `closes`: after `archived_part_skipped`: `true` (TD-506 is not in the runner's `after()` base, so it carries nothing).

`fixtures/board_writer`:
- `decide_parent_snapshot_part_archived`: `decide_parent_snapshot`'s ledger, with `TD-010` moved to
  `ledger/archive/TD-010.md` as `Resolved`. `Go` lifts TD-008 and TD-009, logs the skip on the Context entry,
  and closes the item `— lifted.`. `entries` lists TD-008 and TD-009, and the archived file is unchanged;
- `decide_parent_snapshot_part_archived_open`: the same, but the archive file reads `**Status:** Open` and still
  carries the gate. The result is the same, byte for byte;
- `decide_parent_snapshot_part_archived_board_only`: `--board-only`, the open parts already lifted. The item is
  closed;
- `decide_parent_context_archived`: the Context entry in `archive/`. Exit 1, refused as an archived Context;
- `decide_parent_snapshot_part_resolved_open`: `TD-010` stays in `ledger/` but reads `**Status:** Resolved
  2026-01-10` with no gate. It is passed as a text, `_carried()` reads it as carrying nothing, and the result is
  `decide_parent_snapshot_part_archived`'s: the skip logged, TD-008 and TD-009 lifted, the item closed.

`fixtures/verdict`:
- `a decide lift with an archived part`: new ids of the case's own (the runner overlays a case's `base/` on the
  shared base and can drop paths only from the head, so a shared entry cannot be moved). The parent and one part
  are open files under the case's `base/docs/ledger/`; the other part exists only under
  `base/docs/ledger/archive/`, reading `Open` and carrying the gate. The case's `base/` and `head/` overlay
  `docs/user_attention.md` with the parent's item added, unanswered at the base and answered `Go` at the head.
  The head writes the open part and the parent as `board.py decide` would. `carve_out` is true;
- `a decide lift that edits the archived part`: the same, plus a lift written into the archive file, its Log line
  dated as the lift's (the `created_at` date), so the Log-date check passes and `lift-files` is what fires;
- `a decide lift with a Resolved part in the open directory`: as the first case, but the skipped part is an open
  file reading `Resolved`. `carve_out` is true: the verdict passes it as a text, as the writer does (D5);
- `a decide lift whose Context is archived`: the Context entry exists only under the case's
  `base/docs/ledger/archive/`. `lift-refused`, naming the archived Context.

## The build

One build entry, **B1**: D2–D5 with SPEC text 1–5 and every fixture above, in one PR (a format change lands its
spec, code and fixtures together, AGENTS.md). Done when `board.py decide` answers
`decide_parent_snapshot_part_archived` and its `_open` twin as above, `lift_pr_verdict()` carves out the matching
PR, the fixtures and suite pass, and the `SPEC.md` text lands with the code.

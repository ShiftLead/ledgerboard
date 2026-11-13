# TD-078: v3.0's ledger half — the last migration, a note for archived entries, and the removals

**Status:** Designed 2026-11-13 (session lb-designer), Go by Paul 2026-11-12; draft 9. Class: **wide** — it changes a vendored, published format
read and written by both consumers, and plans a major (cadence.md §4.8; cap 6 rounds). Rounds: six ran, the cap (build-changing per design review 6, 2, 2, 1, 2, 1; fact-checks 7, 1, 1, 0, 0, 1), their fixes applied; the rounds ended at the cap. Paul answered the end-of-rounds item **One more round** (2026-11-12), run as TD-082: round 7's fact-check raised one build-changing finding (B3's count of entries `migrate` changes, now five), its design review SHIP with two minor, and it found the recurring consumer-lines topic ended (R18 read them against agent-cadence's `main` and found no format question in them); all applied, then the closing fact-check (two minor, applied), and the item again. Paul answered it **One more round** (2026-11-12), run as TD-086: round 8's fact-check (R20) found B3's count stale after PR #249 migrated this ledger (build-changing, F104: 59 archived entries, no open one) and its re-check (R21) two minor; its design review (R22) raised one build-changing finding, F109 (TD-075's B1 has merged, so it leaves D3's number rule and TD-070's B1's blocks and Ask), and nine minor (F110–F118), all applied or rejected as the record says; the closing fact-check (R23) SHIP with five minor, applied (F119–F123), and the item again, recommending One more round. Paul answered it **Go** (2026-11-12): the builds are filed, TD-088 (B1), TD-089 (B2), TD-090 (B3) and TD-091 (B4), each `Part of` TD-078, round 8's fixes no design review read in their Fix. Trend, build-changing per design review 6, 2, 2, 1, 2, 1, 0, 1 (fact-checks 7, 1, 1, 0, 0, 1, 1, 1). **Revision, 2026-11-13 (TD-096, on Paul's input relayed that day):** the roster repos are not worked until ledgerboard, agent-cadence and ShiftLead are in shape, so they skip their v2.7 remodel and take one remodel straight to v3.0. D5 now binds the three repos that move with the release, D7 is new (a roster repo's one remodel, after v3.0), B4 gains text 5′ (*Versions*' precondition sentence, consumer-neutral), and agent-cadence's *Consumers* line gains the pin a roster repo bumps to first; TD-091 (B4) is `Blocked by` TD-096 until Paul's go on the revision. The revision keeps the record's numbering (R24 on) and starts its own count against the cap (6, class wide).

**Entry:** [TD-078](../ledger/TD-078.md). **Source:** the entry's Why and Fix; [target design](target-design.md)
§2.1 (the retired fields and words) and §7.1's v3.0 row; [TD-070's plan](TD-070-board-directory.md) D12 (the
release order) and *Not in this design*; [TD-058's plan](TD-058-status-release.md) (v2.7's `migrate`); `SPEC.md`
*The ledger* (*The old form*, *Retired words*), *The next id*, *Ledger entries and their edits*, *Migrating to
v2.7*, *The ledger writer* and *Versions*; the module and `ledger.py` at `origin/main` (`ef18845`, cited by
function); the three repos' ledgers as they stood on 2026-11-11 (counted with the module's own readers).

## The problem

v2 keeps reading four forms only because old files hold them: the `Waits` field, the `Taken by` field, the old
decision form `decision (<who>) <text>` in `Blocked by`, and a `Resolved` header field. v2.7's `migrate` maps the
old Status words, `Added` comments and a header `Location`, and leaves those four as they are (*Migrating to
v2.7*, rule 5). §7.1 plans v3.0 to stop reading them and to remove `migrate` (its row stands as a summary: D4 makes v2.7's
retired header `Location` a v3.0 error too, round 8's F117), once every repo holds none of them,
in open entries and archived ones alike.

Two things stand in the way.

1. **No writer rewrites them.** In an open entry `set` can remove a field (an empty value), and a session can
   rewrite the old form with `set` into `decision (<who>)` and `edit` an `**Ask:**`. In an archived entry no
   writer can: `set`, `note` and `edit` take only open entries (*The ledger writer*: "An archived entry is edited
   only once reopened"; `ledger.py`'s `_open_entry`). What is left is a hand edit, which cadence.md §2.12 allows
   for "a change to an archived entry other than `reopen`" only as the exception no command makes, through `fmt`
   — not as the route by which three repos rewrite some 200 old forms (the table's 208 instances, fewer entries). The entry asks that each repo meet the
   precondition with no hand edit.
2. **An archived entry cannot even take a note.** PR #226 (2026-11-11) named two archived entries in its title;
   the merge gate's ledger row asked it to touch their files, which no writer can, and the PR was retitled
   instead. Its review left an archived entry's stale Log text as it was, for the same reason.

What the four forms amount to, counted on 2026-11-11 with `entries()` and `parse_gates()` over each repo's
`docs/ledger/` (open / archived):

| | ledgerboard | agent-cadence | ShiftLead |
|---|---|---|---|
| entries | 6 / 65 | 12 / 65 | 111 / 1426 |
| `Waits` | 0 / 1 | 0 / 2 | 0 / 2 |
| `Taken by` | 1 / 52 | 1 / 29 | 0 / 0 |
| a header `Resolved` | 0 / 2 | 0 / 0 | 0 / 105 |
| the old decision form | 0 / 0 | 2 / 0 | 7 / 4 |

No entry holds a header `Resolved` beside a body `**Resolved:**` section, no open entry holds a `Waits`, and of the
thirteen old-form entries nine already have an `**Ask:**` section (ShiftLead's six open and three archived). The agent-cadence tree this repo pinned
when this repo's entries were counted (2026-11-11, `67023cc`) wrote `Taken by` on every `new` and `renumber` (its `render()` and `plan()`);
PR #249 moved the pin to `acf46ea` (2026-11-12), past agent-cadence's TD-188 step 4, which writes `Id take` alone
and drops a carried `Taken by` on `renumber`, so this repo's count no longer grows.

## Decisions

**D1. `migrate` maps all four forms, in the last v2.x minor.** The rewrite is mechanical and needs no judgment in
every case the count above shows, so it belongs to `migrate`, which already runs over every entry, open and
archived, writes nothing on a stop and is the one command each repo runs on taking a release. *Migrating to
v2.7*'s rule 5 ("What it leaves") becomes four rules, applied after `Location`, each to the entry the one before
it left:

- **5. `Taken by`** → one plain Log line, `Taken by <value>`, the value whole (the take's `by`, who was handed
  the id).
- **6. `Waits`** → on an archived entry, one plain Log line, `Waits <value>`; on an open entry, a stop (the wait
  needs its gate, `until` or `event`, which a person or a session chooses and `set` writes; the count shows none).
- **7. A header `Resolved`** → the body section `**Resolved:** <value>`, before the Log, as `reopen` moves one
  today; beside a body `**Resolved:**`, a stop, as `reopen` refuses it (the count shows none).
- **8. The old decision form** `decision (<who>) <text>` → `decision (<who>)`, its text into an `**Ask:**` when
  the entry has none, else the old item whole into one plain Log line; a `<who>` that is neither a person's name nor a retired role is
  a stop, since `decision (<who>)` would be an unreadable item (no real entry has one); so is an empty text on an
  open entry with no Ask, which would leave an `ask-missing` error; so is a `<who>` the entry's `Blocked by` already
  carries as `decision (<who>)` (any item of the value as written, retired roles included, compared by its
  holder alone, lowercased, as `gate_repeats()` compares decisions, so `decision(kim)` repeats `decision (Kim)`;
  round 8's F111), which would leave the item twice (`gate-repeated` for a person).

Text 1 is the one exact statement of the rules; this list is its summary. Four choices in it are this design's:
- **The dates.** A line about the entry's filing (`Taken by`, a `Waits`, an old decision's text) is dated by
  `Added`, placed first, as rule 3 places an `Added` comment: the take and the wait began then. On an **open entry
  carrying a gate** it is dated instead so that it can never become the Log's first dated line (the first readable
  Log line's date, placed after its equals), because `gate_age()` falls back to that line's date, and a
  first line dated `Added` would move an older gate's age. The date is read after rules 1–4. Rules 1–4 themselves
  can still move a gate's age (rule 3's line and rule 1's `was:` line, as *Migrating to v2.7* says); rules 5–8
  never do.
- **The text of the old form** goes to the `**Ask:**` the cadence asks every decision to carry (cadence.md §2.3),
  where the entry has none; where it has one, the existing Ask stands and the old text is kept in the Log.
- **The merge gate sees no new decision.** `uncovered_decisions()` reads the decisions an open entry *gains* in a
  diff from `_decisions()`, which skips the old form, so rule 8's `decision (<who>)` would read as gained, and the
  migrate PR would be refused (`decision-uncovered`) or flagged (`decision-elsewhere`) on every open old-form entry
  (two in agent-cadence, seven in ShiftLead). From v2.8 its base side also counts each old-form holder as
  `decision (<who>)`, compared by `_gate_key`: the old form held as a decision by `<who>` (*The ledger*), so the
  rewrite gains nothing. (Exempting the migrate commit by subject, as `tripwire()` does, would need a subject the
  function does not take.) The gate does change for the gate sweep and `gate_age()`, which read `gate_items()`:
  after the rewrite the sweep sees a decision it did not, and owes it a board item if none covers it, which is
  right — the old form hid it.
- **Each Log line is a plain note:** `Taken by`, `Waits` and `Blocked by` begin no writer's prefix, so `log_line()`
  reads each as a note and `check()`'s `log-line` passes it.

The **post-condition** gains one clause: the migrated entry holds none of the four forms, and gains no `ask-missing`
or `gate-repeated` the input did not have, else it is a stop.

*Alternatives weighed.* (a) A `set` and `edit` that take archived entries, and each repo rewriting its some 200 old
forms entry by entry: many hand-chosen writes for a mechanical change, with history open to any edit. (b) Dropping
`Taken by` and `Waits` with no Log line: shorter, but `migrate`'s rule is that nothing is lost, and the Log is
where v2.7 put every other old value. (c) A stop for every old form with an `**Ask:**`: nine stops for a person,
where a Log line keeps the text and the existing Ask stands.

**D2. `note` writes an archived entry, in the last v2.x minor, and in v3.0.** `ledger.py note TD-n "<words>"`
takes an archived entry as it takes an open one: the module's `note` edit, unchanged, and the file written back
where it is, in `archive/`. No flag: the id names the entry wherever it is. The module's `note` first lifts a
Status's notes into the Log, which on an archived Status in the closed set lifts nothing; on one outside it (a
repo that has not run v2.7's `migrate`: 1,139 of ShiftLead's 1,426 archived entries on 2026-11-11, 176 of them
with notes `note` would lift) it may rewrite the Status. So `ledger.py note` refuses an archived entry whose
Status `status_problem(text, archived=True)` faults — the whole 1,139, not only the 176, so one test says when an
archived entry takes a note — *run migrate first*; on every other archived entry it appends one Log line and writes the file in canonical form. `set` and `edit` still take only open entries; a change to what an archived entry *says* is a
`reopen`, then an edit, then an `archive`. The write's refusal rule stands (a `check()` error the ledger before it
did not have), and `check()` reads only the open entries' Logs, as now.

So the PR #226 case has its route — a note on each archived entry it names — and a stale line in an archived Log is
corrected by a later dated line, never rewritten: the Log is history.

**D3. The release.** D1 and D2 ship in the **last v2.x minor**, which TD-070's D12 makes a precondition of its B1
("v2.8 is released before B1 merges", and "No v2.x release after B1 merges"): `migrate` goes in v3.0, so a repo
must be able to run the new rules on a v2.x before it vendors v3.0. The builds for D1 and D2 therefore merge
before TD-070's B1, and B1 is `Blocked by` them (*The builds*). The minor is v2.8 when it is cut after they merge;
the board's open *Release v2.8* item asks for v2.8 now, without them, and if it is cut first they ship as v2.9,
still before B1 merges. TD-065's and TD-075's builds have merged (TD-083, TD-084, 2026-11-12) and ship in whichever
minor is tagged first, v2.8 (round 8's F109). The rule for the number: each of this design's B1 and B2 writes,
wherever its texts say v2.8, the first minor not yet tagged when it merges (v2.8 if it is untagged then, else v2.9),
and the later of the two to merge rewrites the other's number to its own where that is still untagged, so both name
one minor; the Consumers lines say *the last v2.x minor*. TD-070's D12, where it names v2.8 as the release before
its B1, reads as that minor. *(TD-075's B1 joined this rule on 2026-11-12 and left it in round 8, once it had
merged.)*

`Blocked by` the two builds alone would let TD-070's B1 merge while they sit untagged on `main`, after which D12
allows no v2.x release. So TD-070's B1, when filed, is `Blocked by` TD-078's B1 and B2 and `decision (paul)`, its Ask:
*Is the last v2.x minor tagged, holding TD-078's B1 and B2, with nothing on `main` past that tag under
`ledgerboard/`, `SPEC.md` or `fixtures/`?* — lifted by Paul's answer once he has cut it (written by whichever of
TD-070's and TD-078's build filings comes last, with its board item; TD-070's plan's D12 says the same once its round 8,
TD-085, lands). The release is Paul's.

v3.0's ledger removals (D4) are one build, merged after TD-070's last build so that v3.0's removals land
together, then v3.0's release (Paul's) with TD-070's half.

**D4. What v3.0 stops reading, and what it does on meeting each form.** The four forms, and a header `Location`
(retired in v2.7, mapped by v2.7's `migrate` and in the precondition for the same reason), are **retired errors**
in v3.0: on **every entry, open or archived**, of a ledger that declares major 2 or more, an error whether or not
the edit changed the entry (kind `retired`; ℹ on a v1 ledger). Its records are built as `_status_records()`
builds the closed Status set's: over every entry, the archive's included (the ℹ `retired` field flags today come
from `pickable()`, which reads open entries alone), and appended after `check()`'s loop that downgrades a record
on an untouched entry to ℹ, so they keep `standing` false and the error level, and `ledger.py --check` and the merge
gate fail on them. The
error's text is text 7's, and `status_problem()`'s text 10's, each defined once there. In detail:

- **`Waits`, `Taken by`, a header `Resolved`, a header `Location`:** `check()` reads each as the retired field it
  is and errors, naming it; nothing else reads it. `pickable()`'s ℹ `retired` flag for a field goes (only the error
  survives, so a field carries one flag), with `WAITS_WRITTEN`, `LOCATION_WRITTEN`, `WRITTEN_RETIRED` and
  `check()`'s `written` grading, which every such line now meets as an error; `RETIRED_FIELDS` keeps `resolved`
  (already there) and its `location` text loses *run migrate*. `canonical()` loses `Taken by` from its order, so a `Taken by`
  left in a file is placed as any other field, in the file's order. `edit_entry`'s `archive` no longer removes a
  header `Resolved` but refuses an entry holding one (text 8), and `reopen` no longer moves one or refuses an entry
  with both: it writes what it writes beside it, and the error stands.
- **The old decision form:** `parse_gates()` no longer reads it as a decision. `GATE_DECISION_RE` matches a whole item
  (the regex end-anchored with `\Z`, where today it matches a prefix; its board-side callers pass whole gates, so
  they read the same; round 8's F113), so `decision (<who>) <text>` is neither the old form nor a
  decision but an unreadable item (`bad`), which keeps the block, names no holder and is an error (an unreadable
  `Blocked by` item, as today). Its record loses `old_form`, and `retired` loses the kind `old-form`. Every
  old-form path goes with it: `OLD_FORM_REPLACES`; `_written_blocked()`'s two refusals (the old form, and a gate
  added beside it), which `edit_entry`'s `set`, `entry_text()` and `reassign_gate()` call (each
  caller checked), and `edit_entry`'s carried-gates clause, with their
  docstrings and `parse_gates()`'s; `_without`'s refusal, which `lift_gate()` and `reassign_gate()` share; `reassign_gate()`'s
  own; `_blocked_items`', `_one_copy`'s and `_item_gate_key`'s old-form branches; and `ledger.py`'s `set`-route
  refusal (*migrate it first*); and B2's base-side count in `uncovered_decisions()` (D1), which reads `old_form`
  and would raise once the record loses it. A value holding the item is then written by `new` and `set` as any unreadable item
  is, for `check()`, whose error the writer's refusal rule (an error the ledger before did not have) refuses; and
  `lift_gate()` and `reassign_gate()` refuse it as a gate the entry does not carry. `parse_blocked()` keeps its
  three lists, but the old item's holder leaves the second (decision holders) and its comma-split pieces join the
  third as unreadable items; its docstring says so, and so does text 12 (round 8's F114); *Versions*' v2.4 paragraph, which says
  `parse_blocked()` keeps its three lists, stands as history. A person's name still compares
  in any case (`_gate_key`). So that it is named wherever it stands, `check()`'s retired records (above) include,
  on every entry open or archived, each `Blocked by` item that opens with `decision (<who>)` and has text after
  it, as *the old decision form*: one error per value, since the old item is the value's first `decision (`
  with text after it to the value's end (`decision (a) — x, decision (b) — y` is one old item, as `parse_gates()`
  reads it today); the error is for the whole old item (from its `decision (` to the value's end, as
  text 1 rule 8 defines it, commas and all), its text naming that item, beside the unreadable items' own flags on
  an open entry (one per comma-split piece, as `parse_gates()` splits any value). One private helper finds it,
  `_old_form_item(value)` (TD-096), with a prefix pattern of its own, `OLD_FORM_HEAD_RE` (today's `GATE_DECISION_RE`
  unchanged, `^decision[ \t]*\((?P<who>[^()]*)\)`), since `GATE_DECISION_RE` itself becomes the end-anchored
  whole-item test (F113): the value split at commas as `parse_gates()` splits it, the first piece that
  `OLD_FORM_HEAD_RE` matches with non-blank text after the match opens the old item, which runs from that piece's
  start to the value's end; a piece that does not open with `decision (` (`TD-1 decision (b) x`, a `decision (` mid
  piece) opens none, and is an unreadable item alone; no such piece, `None`.
- **`migrate` goes:** `migrate_entry()`, `migrate_subject()` and the helpers only they use (round 8's F112:
  `MIGRATE_SUBJECT_RE` stays, since `subject_kind()` and `tripwire()` read old `ledger: migrate` subjects; so do
  `_real_day()`, `_status_in_set()` and `_entry_problem()`, which other code calls; `_lenient_parts()`, which only
  `migrate_entry()` calls, goes, and `status_problem()`'s docstring stops naming it), `ledger.py migrate`, and
  `fixtures/migrate/`'s `migrate_entry` group and the `migrate_*` writer cases. `status_problem()` stays (the
  closed Status set is v3.0's too), with its message's new ending (text 10), and its cases move to
  `fixtures/status/cases.json` (*Fixtures*). The grammar appendix's `added` start symbol, judged today by
  `migrate_entry()`, is judged instead as a real calendar date, whole (`_real_day()`), which is what
  `migrate_entry()` left alone (text 9). `subject_kind()` still names a
  `ledger: migrate …` subject `migrate`, and the tripwire still exempts that commit, as `subject_kind()` still
  reads the three `shiftlead:` subjects written before ledgerboard: a merge gate may meet one in a PR's history.
- **`judge_takes()`** loses `accept_taken_by`: an entry with no `Id take` is `id-no-take` (fail), whatever it says.

After the precondition none should stand; a stale branch that brings one back is caught by the merge gate as an
error, and an archived entry's is the hand fix cadence.md §2.12 allows, through `fmt`.

*Alternative weighed:* reading the four forms as unknown fields in v3.0, with no error. A v3.0 reader would then
read an old form silently as nothing — a `Taken by` as no take, an old-form decision as an unreadable item no one
is told about — where an error says what it is and what replaces it. The retired list exists so a retired word is
named, never misread (target design §2.1: "Once v3.0 stops reading it, it is a *retired* error").

**D5. The precondition, as one command per repo, in the repos that move with the release.** v3.0's precondition
(§7.1, *Versions*' v2.7 paragraph) binds the repos that take v3.0 when it is cut: ledgerboard, agent-cadence and
ShiftLead. It is met in such a repo when, run with the last v2.x, `ledger.py migrate --plan --release <x.y>` prints `entries` with no
entry holding `changes` or `stops`. With D1 that covers every old form: the Status set, `Added`, `Location` and
the four. Each consumer runs it first in its v3.0 vendor PR, before vendoring, and records its output in the PR.
No new check is added: the command exists, and its output is what the precondition means. A roster repo (any
other repo that pins agent-cadence) is outside it: v3.0 leaves it untouched until it bumps its own pin, and it meets
the same check, with D7's added conditions, in its own remodel, between that remodel's two bumps (D7). Ledgerboard
has no vendor PR: its check is B4's guard run (*The builds*), stated in B4's PR. *(Amended 2026-11-13, TD-096, on Paul's
input: the roster repos skip their v2.7 remodel and take one remodel straight to v3.0.)*

**D6. What v3.0's ledger half leaves.** `status_notes_to_log()` and the lifting of a Status's notes in `note`,
`archive` and `reopen` stay: on an entry in the closed set they lift nothing, and removing them changes nothing a
precondition-clean ledger reads. Their date fallback loses the header `Resolved`: `_fallback_day()` reads the body
`**Resolved:**` line, else `Added`, as v3.0 reads no retired field for its old meaning (text 7); after the
precondition no entry holds one, and on an entry that still does (a retired error) a lifted note is dated by
`Added`. `_closing_source()`'s like read goes with `migrate_entry()`. The retired gate `hold` and the role `decision (designer)` stay retired items
that keep the block (none of the three repos holds either; a roster repo's remodel leaves no open entry
holding either, D7's predicate). The ledger's declared major stays 2 (`FORMAT_MAJOR` untouched, as TD-070's B5 leaves it), since a v2 ledger that meets the
precondition reads the same under v3.0. A ledger that declares `Ledgerboard: 3` is refused by v3.0 as by v2.x
(`version_problem()`: newer than the module reads), which is right: no ledger form of major 3 exists.

**D7. A roster repo's one remodel, after v3.0** (TD-096, on Paul's input, 2026-11-13). A roster repo takes no v2.7
remodel (target design §7.2 step 6, amended). When its own team picks it up again, after v3.0 is cut and both
consumers vendor it, it takes one remodel: one session and one PR, by its own team, in two bumps of its agent-cadence
pin (`docs/cadence.toml`'s `ref`, a full commit). This design fixes what that PR must show and how v3.0 grades it;
the commands, their order and their commit points are agent-cadence's remodel procedure (*Consumers*), since every
one is an agent-cadence wrapper's (`bump`, `ledger.py --split`, `migrate`'s git dating, `board_edit.py`), tested
there and changed without a ledgerboard release.

- **The two pins are the procedure's to name.** agent-cadence's remodel procedure (*Consumers*), at its fixed path
  on `main`, names both: the first, a commit on agent-cadence's `main` that vendors the last v2.x minor (v2.8,
  tagged here 2026-11-13, #281, unless a v2.9 is cut before TD-070's B1 merges, D3), with the minor's number; the
  second, a commit that vendors v3.0 (or a later v3.x). Its test runs the procedure's commands at each named commit,
  in a fixture checkout, and a later agent-cadence PR whose test passes at a newer commit may re-name either, so a
  wrapper defect at the first pin is mended by naming a newer one, never by the second bump. A remodel reads the
  pins when it starts, from a merged file: no reader computes one from where `main` stood at a merge (F126). The
  procedure merges, naming both, before any roster remodel starts. **`migrate` stays usable
  through the first pin after v3.0 removes it:** a pin is a commit on agent-cadence's `main`, which stays, so `agent-cadence
  run ledger.py migrate` under that pin runs the last v2.x's `migrate` whatever v3.0 has removed. Nothing in
  ledgerboard or agent-cadence keeps `migrate` past v2.x for it.
- **What the PR shows between the bumps** — the precondition, met per repo (D5), taken under the last v2.x pin
  before the second bump, its output in the PR body: the ledger is a v2 directory (a v1 file split first: the
  writers, `migrate` among them, refuse one); `ledger.py migrate --plan --release <the minor>` shows no entry with
  changes or stops; every entry file is canonical (`ledger.py fmt --check` exits 0: no entry would change and none
  is refused); no open entry's `Blocked by` holds the retired gate `hold` or the reserved role `decision
  (designer)` (each a retired item v3.0 still reads as a block, ℹ only, D6); `ledger.py --check` reports no error;
  and the board carries its `People:` line and is in `fmt`'s form (`board_edit.py fmt --board <board> --plan` lists
  no line in `fixed` and none in `refused`). It is the PR's evidence, not a graded row: the merge gate reads the PR's
  base and head alone, and the squash drops the commits between, so the techlead who merges it (target design §7.3,
  *Who merges*) reads it before merging.
- **How v3.0 grades the PR**, at its head, under the v3.0 pin (where the gate runs from is the procedure's). It
  reads no old form (D4): at the head, v3.0's retired errors (on a v2 ledger) refuse any old form the remodel
  left. `check()` grades what the head holds, reading the base only to tell a standing finding from one the edit
  made; `tripwire()` reads the base through `_decisions()`, and `uncovered_decisions()` through `_carried()`, which
  sees no old form once B4 removes `_held_old_form()`, so a base old-form item is unseen: removing one trips
  nothing, and every `decision (<who>)` the remodel writes, from an old form or a `Waits`, reads as gained. Each
  needs a board item that covers it (its Context `TD-n decision (<who>)`), else the gate refuses it
  (`decision-uncovered`, when the board's `People:` lists the person) or flags it (`decision-elsewhere`). The gate
  sweep owes such an item in any case, since the old form hid it (D1).
- **The board** takes, in the same PR, under the last v2.x pin, the v2.x steps a roster board missed (its `People:`
  line, target design §7.2 step 0; `fmt`'s key rule, §7.3) and, under the v3.0 pin, its split, which TD-070's second part (TD-095) designs,
  a split PR whose base board predates v2.3 included; the board items above are written after the split, under the
  v3.0 pin, in the form TD-095 gives, since the v3.0 gate reads the head's board, which is the split one.
- **What it supersedes for a roster repo:** cadence.md §2.12's "`--split` as its own PR" and its `migrate` run as a
  PR of its own both give way to this one PR, as Paul asked (agent-cadence's line, *Consumers*). The roster repos'
  own counts are their remodels' to take: no roster ledger is counted here.
- **A roster remodel starts only once agent-cadence's procedure has merged** (*Consumers*), and its board half once
  TD-095's design gives the split and the board's writer under v3.0.

*Alternatives weighed.* (a) Two PRs, the first merged under the last v2.x pin, so v2.8's gate grades the rewrite and
the rewritten decisions need no board item in that PR: two remodels where Paul asked one, and the board items are
owed anyway. (b) v3.0 keeping the old-form base-side count for a roster repo's rewrite: a v3.0 reader carrying a
retired form's meaning for one migration, which D4 rules out. (c) Keeping `migrate` in v3.0 for the roster repos:
the old forms' code would stay in every v3.x reader for a run each roster repo makes once, under a pin that already
has it. (d) A pin fixed in agent-cadence's v3.0 vendor PR: the last commit before that PR merges, read literally from
Paul's note ("the last agent-cadence that vendors v2.8"), is known only once it has merged, so the entry would race
its own merge (F126); the vendoring PR's own squash commit (rounds 9–12), or the newest passing commit when named
(round 13), is fixed but frozen with whatever wrapper defect it carries, which the second bump cannot mend (F194,
round 14). The procedure's file names the pins and a passing PR may re-name them: the latest agent-cadence the note
asks for that the procedure has tested, fixed for each remodel when it starts.
(e) The remodel's commands, in order, in this plan (D7 as rounds 9–11 had it): every build-changing finding on them
(F142, F153, F154, F162, and round 11's) was an agent-cadence wrapper's argument form, side effect or commit point,
which ledgerboard cannot check from its tree and which moves with agent-cadence; so this plan keeps the predicate and
the grading, and the procedure is agent-cadence's (*Consumers*).

## The `SPEC.md` text

Each text says where it lands and what it replaces. Texts 1–5 are B1's and B2's (the last v2.x minor, written
here as v2.8); text 5′ and texts 6–12 are B4's (v3.0).

**Text 1 (B2), *Migrating to v2.7*, rule 5 replaced.** The paragraph "**5. What it leaves.** A `Waits` line, a
`Taken by`, an old-form decision, every other field and section, and every Log line already there are left as they
are. …" becomes:

> The rules below read the entry rules 1–4 left. *A dated Log line* is one `log_lines()` gives a date that is a
> real date. *The filing date* (v2.8) is `Added` when its whole value is a real date, else the first dated Log
> line's date, else `today`; a line dated by it is placed before the first Log line dated on or after it, so lines
> of one date written by two rules stand in reverse rule order. *The gate-neutral date* is the first dated Log
> line's date (in file order), else `Added` when its whole value is a real date, else `today`; a line dated by it
> is placed after any line of an equal date (before the first line dated later). *The entry's date* is the
> gate-neutral date on an open entry whose `Blocked by` carries a gate (`gate_items()`, or the old decision form),
> and the filing date on any other. So rules 5–8 never move a gate's age (`gate_age()`) on an entry with a dated Log
> line or an `Added` whose whole value is a real date; on any other they may (and on an entry whose first Log line
> has an unreal date, `gate_age()` raises today, before and after).
>
> *Has an Ask* means the entry has an `Ask` header field or a body `**Ask:**` section, as `pickable()`'s
> `ask-missing` reads it.
>
> **5. `Taken by`** (v2.8). A header `Taken by` is removed and its line written as one plain Log line, `Taken by
> <value>`, the value whole, dated by the entry's date. An empty one is removed and nothing written.
>
> **6. `Waits`** (v2.8). On an archived entry a non-empty `Waits` is removed and its line written as one plain Log
> line, `Waits <value>`, dated by the entry's date. On an open entry a non-empty `Waits` is a **stop**: its gate is
> a person's or a session's to write (`until` or `event`, by `set`, which then removes the line). An empty `Waits`
> is removed and nothing written.
>
> **7. A header `Resolved`** (v2.8). It is removed from the header and written as the body section `**Resolved:**
> <value>`, before the Log, else at the end. An empty one is removed and nothing written. A non-empty header
> `Resolved` meeting a body `**Resolved:**` section is a **stop**.
>
> **8. The old decision form** (v2.8). *The old item* is the old form as *The ledger* reads it: from its
> `decision (` to the end of the `Blocked by` value, commas, parentheses and all (`parse_gates()`'s `old_form`).
> It is rewritten `decision (<who>)`, `decision` in lower case and `<who>` as `parse_gates()`'s `old_form` gives
> it, the items before it kept in their order; when `<who>` is
> not a person's name (`is_person()`, which a retired role passes), it is a **stop**. Its text, less its leading run
> of `—`, `–`, `-`, `:` and whitespace, is written as the body section `**Ask:** <text>`, placed as `edit` places a
> section the body lacks, when the entry has no Ask; when it has one, the old item, whole, is written as one plain
> Log line, `Blocked by <the old item>`, dated by the entry's date. An empty text writes neither; on an open entry
> with no Ask, where `decision (<who>)` reads as a decision (not a retired role), it is a **stop**, since that
> leaves `check()`'s `ask-missing` error. When an item of the value as written, before the old item, is
> `decision (<who>)` for the same `<who>` (the holder compared alone and lowercased, as `gate_repeats()` compares
> decisions, so `decision(kim)` counts; a retired role included, though `gate_items()` omits it),
> it is a **stop**, since the rewrite would write the item twice (for a person, `check()`'s `gate-repeated` error). No `gate added`
> line is written.
>
> Stops are collected from every rule, 1 to 8, and with any the input is returned as given.
>
> **9. What it leaves.** Every other field and section, and every Log line already there, are left as they are. A
> Log is made at the end of the body when the entry has none and a line is written; a Log that is not last, or two
> Logs, is a stop on an entry with `changes`; an entry with none is returned as given. A `Status` line below the
> header block is no Status: the header gets `Open`, and the line is left and listed.

The sentence before rule 1, "The rules apply in this order, the Status (1 or 2), then `Added` (3), then `Location`
(4), each to the entry the one before it left.", becomes:

> The rules apply in this order, the Status (1 or 2), then `Added` (3), `Location` (4), `Taken by` (5), `Waits` (6),
> a header `Resolved` (7) and the old decision form (8), each to the entry the one before it left.

*The post-condition* bullet gains, after "any problem is a stop.":

> From v2.8 the migrated entry also holds no `Taken by`, `Waits`, header `Resolved` or old decision form, and
> gains no `ask-missing` or `gate-repeated` (`gate_repeats()`) the input did not have; any is a stop (`migrated
> entry still holds <field>`, `migrated entry: ask-missing`, `migrated entry: gate-repeated`).

*The words it returns* gain: in `changes`, `Taken by → Log`, `Taken by (empty) removed`, `Waits → Log`, `Waits
(empty) removed`, `Resolved → body`, `Resolved (empty) removed`, `old decision form → Ask`, `old decision form →
Log` and `old decision form (no text)`; in `stops`, `Waits on an open entry`, `Resolved in the header and the
body`, `old decision form: <who> is not a person`, `old decision form: no text for its Ask`, `old decision form:
<who> already has a decision`, `migrated entry: ask-missing`, `migrated entry: gate-repeated` and `migrated entry still holds <field>` (`<field>` one of
`Taken by`, `Waits`, `Resolved`, `Blocked by`).

**Text 2 (B2), *The ledger*, *The old form*.** "…migrate it first, to `decision (<person>)` with its text in
`**Ask:**`. v3.0 stops reading it." becomes:

> …migrate it first, to `decision (<person>)` with its text in `**Ask:**`, which `migrate` does from v2.8 (*Migrating
> to v2.7*, rule 8). v3.0 stops reading it.

**Text 3 (B1), *The ledger writer*, the `set`, `note`, `edit` bullet.** Its lead "— one edit of an open entry
(`edit_entry()`):" becomes "— one edit of an open entry, or for `note` (v2.8) of an archived one too
(`edit_entry()`):", and "An archived entry is edited only once reopened." becomes:

> `note` (v2.8) also takes an archived entry whose Status is in the closed set, writing its file where it is in
> `archive/`, and refuses one whose Status is not (*run migrate first*); `set` and `edit` take an archived entry
> only once reopened.

**Text 4 (B1, then B2), *Versions*, after the last v2.x paragraph** (v2.8's title, `Doer:` and forms paragraphs
stand there today; where the minor is v2.8, after the last of them, round 8's F110). Two paragraphs, each true alone, in this order
whatever order B1 and B2 merge in: B1's first, B2's after it; the later build places its paragraph before or after
the earlier one's to keep that order.

> **v2.8 gives an archived entry a note** (*The ledger writer*): `ledger.py note` writes an archived entry whose
> Status is in the closed set in place, where v2.7 refused it, and refuses one whose Status is not (*run migrate
> first*). Nothing read changes, and no key moves.

> **v2.8 gives `migrate` the last old forms** (*Migrating to v2.7*, rules 5–8): it maps `Taken by`, `Waits`, a
> header `Resolved` and the old decision form, which v2.7's left. Nothing read changes: every line it writes is one
> v2.7 reads (a body section, a plain Log line, a `decision (<who>)`), and no key moves. One thing is read
> differently once a repo runs it: an old-form decision becomes `decision (<who>)`, which the gate sweep and
> `gate_age()` read as a gate, where they passed the old form over. `uncovered_decisions()` counts an old-form
> holder in the base as a decision already carried, so the rewrite is not a gained decision. A repo that ran
> v2.7's `migrate` runs v2.8's once more, as its own PR.

**Text 5 (B2), *Versions*, the v2.7 paragraph's last sentence.** "`migrate` stays through v2.x and goes in v3.0,
whose precondition is that `migrate --plan` shows no entry with changes in every repo." becomes:

> `migrate` stays through v2.x and goes in v3.0, whose precondition is that, with the last v2.x, `migrate --plan`
> shows no entry with changes or stops in every repo (v2.8: its rules cover every old form, open and archived).

**Text 5′ (B4), *Versions*, the v2.7 paragraph's last sentence** (text 5's, which B2 landed, TD-089; TD-096). "`migrate`
stays through v2.x and goes in v3.0, whose precondition is that, with the last v2.x, `migrate --plan` shows no entry
with changes or stops in every repo (v2.8: its rules cover every old form, open and archived)." becomes:

> `migrate` stays through v2.x and goes in v3.0, whose precondition is that, with the last v2.x, `migrate --plan`
> shows no entry with changes or stops in every ledger that takes v3.0 when it is cut (v2.8: its rules cover every
> old form, open and archived). A ledger whose repo stays on an older v2.x is untouched by v3.0 until that repo takes
> it: it runs the last v2.x's `migrate` first, with a tool that still carries it (its rules are that release's
> `SPEC.md`'s, *Migrating to v2.7*), and takes v3.0 once the same `migrate --plan` shows nothing.

**Text 6 (B4), *The ledger*, *The old form*, replaced whole:**

> **The old form** `decision (<who>) <text>` — a decision followed by anything but a comma or the end of the
> line — was read by v2 as a decision by `<who>`. v3.0 does not read it: it is an unreadable item, which keeps the
> block, names no holder, and is an error. Its replacement is `decision (<person>)` with the text in `**Ask:**`.

**Text 7 (B4), *Retired words*, the paragraph's lead** (its list, with what replaces each word, stays but for the
changes after the quote). "Where v2.x still reads one,
`check()` names it *retired* (ℹ, `retired`) with what replaces it, rather than unknown — except a Status word,
which from v2.7 is an error (*The closed Status set*):" becomes:

> v3.0 reads no retired field, and no `Blocked by` item in the old decision form, for its old meaning; a retired
> item in `Blocked by` is read as before. `check()` names each it meets *retired*, with what replaces it,
> rather than unknown: a retired field — `Waits`, `Taken by`, a header `Resolved` or a header `Location` — is an
> error (`retired`) on every entry, open or archived, of a ledger that declares major 2 or more, whether or not the
> edit changed the entry (never `standing`), and ℹ on a v1 ledger; so is a `Blocked by` item in the old decision
> form (*The old form*, above), which is also an unreadable item, and so an error on an open entry of a v1 ledger too (standing ℹ, as any unreadable
> item is, on an untouched open entry when `check()` is given a base), and ℹ on an archived one there, whose unreadable
> item no reader flags; another retired item in `Blocked by` is ℹ and keeps the block;
> and a Status outside the closed set is an error (*The closed Status set*). A retired error's text ends *v3.0
> reads no such form: on an open entry* followed by its field's cure — *remove it with `set` (an empty value)* for
> `Waits` and `Taken by`; *move its value with `edit --section Location`, then remove it with `set`* for a header
> `Location`; the same with `--section Resolved` for a header `Resolved`; *write its text with `edit --section
> Ask`, then rewrite it `decision (<person>)` with `set`* for the old decision form — then *; on an archived one by hand, then
> `ledger.py fmt TD-n`*. That `set` adds a decision v3.0 did not read before, so it logs `gate added`, the gate's
> age starts that day, and the merge gate wants a board item for it, as for any decision gained. The retired words,
> with what replaces each:

That cost is accepted (round 8's F115): the precondition (D5) leaves none of the three repos holding the old form when it vendors
v3.0, and a roster repo none once its remodel has merged (D7), so the cure meets only an entry a v2.x writer of another tree filed late.

Its second item, "in `Blocked by`, the gate `hold` (…), the old form above, and a role in `decision (…)`, …",
loses "the old form above,", reading "the gate `hold` (…) and a role in `decision (…)`, …" (round 8's F116): the old form is no longer read as a retired item (text 6). Its third item's
"`migrate` maps each (*Migrating to v2.7*)" becomes "v2.x's `migrate` mapped each". The paragraph *A new
`Waits` line is an error* (v2.7) is removed: every `Waits` line is one in v3.0.

**Text 8 (B4), *Ledger entries and their edits*.** The canonical order "`Priority, Type, Added, Owner, Kind,
Status, Taken by, Id take, Blocked by, Part of`" loses `Taken by`, and "`Owner`, `Kind` and `Taken by` are not the
format's own fields. A header `Resolved` is not in the order and is kept where the other fields put it;" becomes
"`Owner` and `Kind` are not the format's own fields; a retired field (*Retired words*) is kept where the other
fields put it;". In *The archived entry*, "A `Resolved` header field is the older form of the line: readers still
read it, and the writers move it into the body." becomes "A `Resolved` header field, the older form of the line,
is a retired error (v3.0)." In *Edits*: `set` loses "it is refused in the old form, and when it adds a gate to an
entry whose `Blocked by` still holds the old form" and the sentences on **the gates the entry carried** in the old
form (from "plus, when its `Blocked by` holds the old form" to "is kept. The old form's refusals come before the
refusal for a missing `today`."), its gates being its `gate_items()`, compared by `_gate_key` (a person's
name in any case), so `Decision (kim)` rewritten `decision (Kim)` is kept; `archive`'s "and a `Resolved` header field is removed" becomes "and an entry holding a `Resolved` header field is
refused (*move it with `edit --section Resolved`, then remove it with `set`*)", so it never writes both; `reopen` loses "A `Resolved` header field moves into a `**Resolved:**` section before the Log,
never deleted. An entry with both is refused: a person merges them."; *Lifting a gate* loses "and a decision still
in the old form (*migrate it first*)". The entry writer's sentence "…its ids, then its gates in their order; the
old form is refused." loses "; the old form is refused" (an unreadable item is `check()`'s).

**Text 9 (B4), *Migrating to v2.7*** is removed whole, and the *The ledger writer*'s `migrate` bullet with it.
In *The merge gate's verdicts*, "(`migrate_subject()`; `subject_kind()` names it `migrate`)" becomes "(written by
v2.x's `migrate`; `subject_kind()` still names it `migrate`)". In the grammar appendix's *The entry header and
the Log*, "`added`: an `Added` value `migrate_entry()` leaves alone, with no `changes` and nothing `listed`, on an
open entry carrying it beside `**Status:** Open`" becomes "`added`: an `Added` value that is a real date, whole",
and "Their cases are in `fixtures/migrate/` and `ledger_edit/check/status_*`" becomes "Their cases are in
`fixtures/status/`, `fixtures/grammar/` and `ledger_edit/check/status_*`". The sentences that recount what
v2.7's `migrate` maps (*Superseded and dropped*, the Status's notes under *The Log*) are history and stay; *Versions*'
v2.7 paragraph's "(*The closed Status set*, *Migrating to v2.7*)" becomes "(*The closed Status set*; *Migrating to
v2.7*, removed in v3.0)", and text 4's v2.8 paragraph's "(*Migrating to v2.7*, rules 5–8)" becomes "(*Migrating
to v2.7*, rules 5–8, removed in v3.0)".
In *The ledger writer*'s closing paragraph, "(`subject` is null: a ledger edit has no commit subject of its own,
so the caller names its commit — except `migrate`'s, which names `migrate_subject()`)" becomes "(`subject` is null:
a ledger edit has no commit subject of its own, so the caller names its commit)". `status_problem(text, *,
archived)`'s definition (its first sentence in *Migrating to v2.7*) moves, word for word, to the end of *The closed
Status set*, ahead of text 10's change there. The `set` route's sentence "a decision still in the old form is not dropped by `set` (*migrate it
first*)" is removed, and so is *The merge gate's verdicts*' v2.8 sentence "A decision a base entry held in the old
form (*The ledger*) is not gained when the head writes it `decision (<who>)` (v2.8)." (B2's). In *The Log*'s lifting bullet, "else the `**Resolved:**` line's (or an older `Resolved` header field's), else
`Added`'s" becomes "else the `**Resolved:**` line's, else `Added`'s" (D6).

**Text 10 (B4), *The closed Status set*.** "…and ends *run migrate, which maps it, lists it, or names what a person
decides*." becomes:

> …and ends *v3.0 reads no other form: on an open entry write `Open` with `set`, on an archived one by hand, then
> `ledger.py fmt TD-n`*.

In *The ledger writer*, text 3's "(*run migrate first*)" becomes "(*The closed Status set*'s cure)", the same
ending `note`'s refusal prints from v3.0.

**Text 11 (B4), *The next id*, `judge_takes`.** The signature loses `accept_taken_by=False`, and the bullet "No
`Id take` is `id-no-take` (fail), unless `accept_taken_by`, … An entry's nonce is compared exactly." becomes "No
`Id take` is `id-no-take` (fail). An entry's nonce is compared exactly."

**Text 12 (B4), *Versions*, after TD-070's v3.0 paragraph** (TD-070's B5 writes that paragraph; B4 is
`Blocked by` TD-070, so it is there):

> **v3.0's ledger** reads no old form (*Retired words*): `Waits`, `Taken by`, a header `Resolved` and a header
> `Location` are retired errors on every entry, open or archived; the old decision form is an unreadable item;
> `parse_gates()`'s record loses `old_form`, and `parse_blocked()` names no holder for it (its pieces are in the
> third list); `judge_takes()` loses `accept_taken_by`; `canonical()` places no
> `Taken by`; and `migrate`, `migrate_entry()` and `migrate_subject()` are gone, while `subject_kind()` still names a
> migrate subject; and `uncovered_decisions()` counts no old-form holder in the base (`tripwire()` never read one),
> so an old form rewritten `decision (<who>)` is a gained decision, owed a covering board item. A v2 ledger that met the precondition (*v2.8*, above) reads exactly as under v2.8, and declares
> no new major. One that did not is not misread: each old form is an error that names it (a retired field ℹ on a
> v1 ledger, *Retired words*; the old decision form an error there on an open entry, as an unreadable item, and ℹ on an
> archived one).

## Fixtures

**B1** (`fixtures/ledger_writer/`): `note_archived` — `note TD-5 "…"` on an archived entry: exit 0, the file
written in `archive/`, a dated line appended; `note_archived_status_outside_set` — an archived Status with a v2.3-style
tail (`Resolved 2026-01-10: why`): exit 1, *run migrate first*, nothing written;
`set_archived` unchanged (still exit 2); a new `edit_archived` (exit 2, the same *edited only once reopened*).

**B2** (`fixtures/migrate/cases.json`'s `migrate_entry`, and `fixtures/ledger_writer/`):
- `taken_by_archived` (dated by `Added`, placed first, before a later Log line), `taken_by_open_no_gate` (the
  same), `taken_by_open_with_gate` (the gate-neutral date: the first readable Log line's, placed after its
  equals), `taken_by_open_with_gate_no_log` (dated by `Added`), `taken_by_empty`, `taken_by_added_not_a_date`
  (dated by the first readable Log line);
- `taken_by_archived_no_log` (a Log made at the end);
- `waits_archived`, `waits_archived_empty`, `waits_open_stops`, `waits_open_empty` (removed, nothing written);
- `resolved_header_archived` (to the body, before the Log), `resolved_header_no_log` (at the end),
  `resolved_header_and_body_stops`, `resolved_header_empty`, `resolved_header_open` (an open entry: to the body
  likewise);
- `old_form_no_ask` (Ask written after the Why), `old_form_commas_after_id` (`TD-3, decision (Kim) — a, b (c, d)`:
  `TD-3, decision (Kim)` and the Ask `a, b (c, d)`; with an Ask, the Log line `Blocked by decision (Kim) — a, b
  (c, d)`), `old_form_header_ask` (an `Ask` header field counts as an Ask), `old_form_no_text_open_stops`, `old_form_with_ask_open` (Log line dated by the entry's date;
  its gate's `gate_age()` unchanged), `old_form_with_ask_no_log` (the line becomes the Log's first, dated by
  `Added`), `old_form_with_ask_archived`, `old_form_ids_kept` (`TD-3, decision (Kim) — x`),
  `old_form_no_text_archived` (`decision (Kim) —`: rewritten, nothing written), `old_form_role` (`decision (designer) — x`: rewritten, still retired),
  `old_form_not_a_person_stops` (`decision (the owner) — x`), `old_form_who_repeated_stops` (`decision (kim),
  decision (Kim) — x`);
- `all_four_and_status` (each rule's order on one entry, two lines of one filing date in reverse rule order),
  `unreal_first_log_date` (a first Log line dated `2026-02-30` passed over for the next dated one; the case names
  no gate, since `gate_age()` itself raises on such a Log, a fault this design leaves as it is); each case's
  output run again changes nothing (`run.py`'s existing `again`);
- the existing `waits_taken_by_old_form_left` (an open entry holding `Waits: the vendor`) becomes
  `waits_taken_by_old_form_open_stops` (rule 6's stop wins, the input returned as given), and a new
  `waits_taken_by_old_form_archived` maps all three; the existing cases holding a header `Resolved`
  (`date_resolved_header_field`, `lift_none_undated_segment_unreal_resolved`,
  `lift_open_undated_head_unreal_resolved`) now move it to the body, and they and any other case `run.py` shows
  changed are regenerated and read;
- each new case with a gate names it (`gate`), so `fixtures/run.py` records its `gate_age()` before and after in
  the expected JSON, as it does today for the three cases that name one, asserting nothing; a
  unit test in `tests/test_ledgerboard.py` asserts the two are equal on every new case with a gate, and a dated Log
  line or an `Added` whose whole value is a real date, and on which rules 1–4 write nothing (`all_four_and_status` and
  `taken_by_added_not_a_date` are outside it);
- `fixtures/ledger_writer/migrate_old_forms` — `migrate --plan` over a directory with one of each, open and
  archived: the plan, its `entries` and the subject.

**B4**:
- removed: `fixtures/migrate/cases.json`'s `migrate_entry` group and the `migrate_*` writer cases, with
  `run.py`'s migrate groups; its `status_problem` group (30 cases) moves to `fixtures/status/cases.json`, run by
  a `status` group in `run.py`;
- `fixtures/grammar/`: the `added` verdict judged by `_real_day()` (text 9), its cases unchanged; the refused
  cases' `why` (today `migrate_entry()`'s reason, e.g. *not a date*) becomes null, so `expected.json` is
  regenerated (round 8's F118), and `run.py`'s `grammar_cases` guard, which reports *missing* when the module lacks
  `migrate_entry`, tests `_real_day` instead (F123);
- `fixtures/ledger/`'s check cases gain `retired_waits_archived`, `retired_taken_by_open`,
  `retired_resolved_header`, `retired_location_header`, `retired_taken_by_archived` (each an error on a ledger no
  edit touched), `retired_old_form_open` (two errors: the retired record and the unreadable item),
  `retired_old_form_archived` (one, the retired record) and
  `retired_v1_info` (ℹ on a v1 ledger), `retired_old_form_v1_open` (an error: the unreadable item, beside the ℹ
  record) and `retired_old_form_v1_archived` (ℹ alone); `fixtures/ledger/gates.json`'s TD-115 old-form case (its records are
  `pickable()`'s, which carry no `old_form`) reads the item as unreadable: its ℹ `retired` flag becomes a
  `blocked-item` flag beside the new retired error;
- `fixtures/ledger_edit/`: `refused_old_form` (the `entry_text` group), `set_refused_old_form`,
  `set_refused_gate_on_old_form`, `set_migrates_old_form`, `set_migrates_old_form_no_today` and
  `set_other_field_keeps_old_form` rewritten (the value written as given, `check()` naming the unreadable item);
  `fixtures/ledger_writer/set_old_form` likewise (refused by the writer's refusal rule);
- `fixtures/lift/cases.json`'s two `old_form_refused` cases refuse it as a gate the entry does not carry;
- `fixtures/ledger_writer/migrate_v3` — `python3 -m ledgerboard.ledger migrate` in v3.0: exit 2, the argument
  parser's refusal of an unknown action;
- `fixtures/ids/cases.json` and `run.py`'s `ids` group lose `accept_taken_by`: its eight cases with
  `"accept_taken_by": true` are removed, with the kinds `id-taken-by` and `id-no-taken-by` they expect (text 11),
  and a new `taken_by_only_no_take` (an entry with only a `Taken by`) fails `id-no-take`;
- `fixtures/verdict/`'s `migrate_old_form_not_gained` (B2's) is removed with the base-side count it pins;
- `fixtures/ledger/`'s check cases also gain `retired_old_form_commas` (`decision (Kim) — a, b (c, d)` on an open
  entry: one retired record naming the whole item, beside the comma-split pieces' unreadable-item flags),
  `retired_old_form_second` (`decision (Kim), decision (Lee) — x`: `decision (Kim)` a decision, the old item
  `decision (Lee) — x`) and `retired_old_form_mid` (`TD-1 decision (Lee) x`: an unreadable item, no retired record);
- `fixtures/verdict/` gains `old_form_rewrite_gained` (TD-096): an open entry whose base holds `decision (Kim) — x`
  and whose head holds `decision (Kim)` with an **Ask:**, on a board whose `People:` lists Kim and with no covering
  item: `decision-uncovered`, since v3.0 carries no old-form holder from the base;
- `fixtures/ledger_edit/cases.json`'s `archive_header_resolved` (now refused), `reopen_header_resolved` and
  `reopen_refused_both_resolved` (the header left); `fixtures/ledger_edit/check/`'s `waits_*` and `location_*`
  (errors now, whatever the edit), joined by before-equals-after cases `taken_by_untouched`,
  `resolved_header_untouched`, `old_form_untouched` and `taken_by_archived_untouched` (each an error on a ledger no
  edit touched, never ℹ), the runner's filter (`run.py`'s `ledger_edit` `check` group) widened from `waits` and
  `location` to every retired kind; `fixtures/ledger_edit/already.md` (its `Taken by` placed in the file's order);
  `fixtures/ledger_writer/fmt_retired_fields` and `fmt_header_not_field`; and any other case `run.py` shows
  changed, each regenerated and read;
- text 10's message regenerates every expected output that holds the old ending: `ledger_edit/expected.json`
  and the `ledger_writer/*/expected.json` files that print it.

## The builds

Each is filed `Part of: TD-078`, with no `Kind`, on Paul's Go; its Done when includes the `SPEC.md` text landing
with the code, and the precheck green.

- **B1 — `note` on an archived entry (D2).** Location: `ledgerboard/ledger.py` (`plan_edit`'s `_open_entry` call
  for `note`, the refusal of an archived Status outside the closed set, the write in place, its docstrings and the
  CLI help *append a dated line to an open entry's Log*), `SPEC.md` (text 3, text 4's first paragraph),
  `fixtures/ledger_writer/`, `tests/test_ledger_writer.py`.
- **B2 — `migrate`'s rules 5–8 (D1).** Location: `ledgerboard/__init__.py` (`migrate_entry()` and its
  post-condition; `uncovered_decisions()`'s base side counting an old-form holder, with a `fixtures/verdict/` case,
  `migrate_old_form_not_gained`, where a migrate diff rewrites one and gains nothing, and *The merge gate's verdicts*' sentence for it: "A
  decision a base entry held in the old form (*The ledger*) is not gained when the head writes it `decision
  (<who>)` (v2.8).", after "…which not every machine reads."), `ledgerboard/ledger.py` (the `migrate` docstrings), `SPEC.md` (texts 1, 2, 4's second paragraph,
  5), `fixtures/migrate/`, `fixtures/ledger_writer/migrate_old_forms`, `tests/`. B1 and B2 in either order.
- **B3 — this repo's own ledger migrated.** `python3 -m ledgerboard.ledger migrate --release <the minor> --ledger
  docs/ledger` with B2's module, as its own PR. v2.7's rules already ran here (PR #249, which also moved the pin to
  `acf46ea`): counted on 2026-11-13, v2.7's `migrate --plan` changes no entry, and B2's rules 5–8 change 59 archived
  entries (57 hold a `Taken by`, 2 a header `Resolved`, 1 a `Waits`, TD-020, which holds a `Taken by` too) and no
  open one; no entry holds the old decision form. The builder counts again at build time. Its stops, if any, are
  decided in the PR. **Blocked by** B2. Done when `migrate --plan` shows no entry with changes or stops.
- **B4 — v3.0's ledger removals (D4).** Location: `ledgerboard/__init__.py` (`RETIRED_FIELDS`, `pickable()`'s ℹ
  `retired` field flag, `uncovered_decisions()`'s old-form base-side count (B2's), `WAITS_WRITTEN`, `LOCATION_WRITTEN`, `WRITTEN_RETIRED` and `check()`'s `written` grading,
  `check()`'s retired records over every entry (fields and the old decision form), `GATE_DECISION_RE`'s whole match
  and `parse_gates()`, `edit_entry`'s `set`, `archive` and `reopen`, `_written_blocked()`, `OLD_FORM_REPLACES`,
  `_without`, `reassign_gate()`, `_blocked_items`, `_one_copy`, `_item_gate_key`, `ENTRY_ORDER`, `judge_takes()`,
  `status_problem()`'s message, `_fallback_day()`'s header read, `uncovered_decisions()`' `_held_old_form()` (D6); `migrate_entry()`, `migrate_subject()` and the helpers only they use removed, `MIGRATE_SUBJECT_RE` kept, D4),
  `ledgerboard/ledger.py` (`migrate` and the `set` route's old-form refusal removed; `note`'s refusal of an
  archived Status outside the closed set kept, its message text 10's cure in place of *run migrate first*),
  `fixtures/run.py`, `SPEC.md` (texts 5′ and 6–12), the fixtures above, `tests/` (`test_ledgerboard.py`'s migrate cases,
  its `accept_taken_by` case, its `migrate_subject` test and `test_parse_blocked_keeps_every_block_for_its_callers`'s
  old-form holder; `test_ledger_writer.py`'s `Migrate` class; removed or rewritten; round 8's F112, F122), and
  `fixtures/lift/` and `fixtures/ledger_edit/`'s expected `old_form` keys regenerated. **Blocked by** B1, B2, B3 and TD-070 (the design entry archives with
  its last build, B5), so v3.0's ledger removals land after its board half and no v2.x release can follow them.
  Before B4 starts, its builder runs `migrate --plan` on this repo's ledger with the last v2.x minor's module (its
  tag's tree, since by then `main` carries TD-070's builds past it), a cheap guard; if
  entries filed since B3 show changes, a re-run of B3's command lands first as its own PR. B4's PR states that run.

**The order with TD-070's builds:** B1 and B2, then the last v2.x minor (Paul's), and B3; TD-070's B1 is `Blocked
by` B1, B2 and Paul's decision that the minor is cut (D3; written on whichever of the two designs' filings comes
last); TD-070's B1–B5; then B4; then v3.0 (Paul's).

## Consumers

Lines for each consumer's own entry, filed there through its question seat (`ao td add --repo`), never here.

- **agent-cadence** (as its `main` stands at `acf46ea`, 2026-11-12, which vendors v2.7 and which this repo pins
  since PR #249):
  - its `ledger.py`'s `prose_waits` (`files/scripts/ledger.py`) scans for ids the old form's text,
    `LB.parse_gates(value)["old_form"][1]`; v2.8's `migrate` moves that text into an `**Ask:**` or the Log, so an id
    named only there stops being seen. Of its two open old-form entries, TD-065's text names no id and TD-144's
    names ShiftLead's TD-1029 in prose; its ledger's migrate PR checks each such text first, and an id that is a
    real wait moves into `Blocked by` first (as `shiftlead#TD-1029`). Its v3.0 vendor PR drops that read, since the
    record loses `old_form` (a `KeyError` otherwise);
  - it already writes `Id take` alone and drops a carried `Taken by` on `renumber` (its TD-188 step 4), so no line
    is needed for that; its archived `Taken by` lines go with its ledger's migrate;
  - its vendor PR for the last v2.x minor needs no wrapper change for `note`: its `edit()` leaves an archived id
    to the vendored writer to refuse (`_lb_plan()` calls `plan_edit()`), so v2.8's writer lets the note through with
    its refusal of an archived Status outside the closed set; its wrapper's own `migrate` action (`ledger.py
    migrate`, over `LBL.run_migrate`, adding git's `--closed-dates`) then runs that minor's rules on its ledger as
    its own PR;
  - its v3.0 vendor PR's cadence change entry points a roster repo at the remodel procedure below, which names the
    two pins (D7); its PR vendoring the last v2.x minor merges before the v3.0 vendor PR, since D5's check in the
    v3.0 vendor PR runs under the minor, so a first pin exists to name;
  - its v3.0 vendor PR's tests read a roster-shaped fixture (a v1 ledger, old forms, a single-file board) without
    error, since its v3.0 tools still read an un-remodelled roster repo's ledger and board through the cross-repo
    resolver and the attention view, which D5's "untouched" does not cover;
  - **a roster repo's remodel procedure** (D7), beside its `cadence.md` §2.12 and §9.19, which a roster session
    follows: the commands, their order and their commit points for the one PR, superseding for it §2.12's
    "`--split` as its own PR" and `migrate` as a PR of its own. What rounds 9–11 of this design found it must get
    right, each an agent-cadence wrapper's behaviour (F142–F175, `docs/reviews/TD-078.md`): open ledger and board PRs
    land or close first, and the team does no other work until it merges; a pin whose `bump` has no hand-off bumps
    by §9.19's manual form; the pinned tree's vendored `ledgerboard/__init__.py` names the minor before anything
    runs; a v1 ledger is split, and the split is not committed before `migrate` runs, since the wrapper dates an
    undated archived Status by the day git added its archive file (the split's day, once committed); a missing date
    is answered only by `--closed-dates` (a file holding a JSON object, TD-n to the UTC day of the newest commit that
    added the entry's heading to the v1 archive, covering every undated archived entry, since giving it replaces
    git's dates), and `--as` answers a stop on the word (an unmapped word, a `Superseded` with no `by`, a `Moved`
    naming several ids), never a date; what `canonical()` refuses is put right by hand
    before any writer runs, since `set`, `edit` and `migrate` refuse or stop on it; target design §7.3's judgment
    steps (an old-form holder that is no person, a role, `hold`, each `Waits`, an entry holding both an open `Waits`
    and the old form rewritten first) run before `migrate`; `fmt` runs after it; `board_edit.py`'s `fmt` and `add`
    take `--board`, and `add` commits and refuses a dirty board, so the commit points are the procedure's; the gate
    and every check run from the PR's own worktree (`agent-cadence run` reads the pin of the checkout it runs in,
    and the repo's main checkout and its hooks keep the old pin until the PR merges); and the
    check D7 names is taken at a commit the procedure fixes. It is read without the repo's pin: a roster session's
    pinned tree predates it, and its §2.12 there still says the opposite, so the procedure lives at a fixed path on
    agent-cadence's `main`, read from there (not through `agent-cadence path`), named in the ledger entry or board
    item that starts each roster remodel, and it overrides that pin's §2.12 for the one PR. It names the two
    pins, and its test runs its commands at each, in a fixture checkout, as well as on `main` (D7). Filed through agent-cadence's question seat with its v3.0 vendor entry;
  - its v3.0 vendor PR first runs `migrate --plan` with the last v2.x minor (D5) and records it, then removes its
    wrapper's `migrate` action (it calls `LBL.run_migrate`, which v3.0 removes) with its helpers `archived_dates()` and `_undated()`, whose
    `LB.migrate_entry()` call feeds its `--closed-dates`, drops
    `accept_taken_by=False` from its `judge_takes()` call (`files/scripts/ledger_next_id.py`), the keyword v3.0
    removes, and `prose_waits`' `old_form` read.
- **ShiftLead**: its Queue card's *held until …* reads the old form's text (`src/sessionorc/ledger.py`'s
  `until_of`, through `parse_gates()["old_form"]`), and seven open entries carry one; v2.8's `migrate` moves the
  text into an `**Ask:**` or the Log, so before its ledger runs it, `until_of` reads the `**Ask:**` (or the gate
  alone), else those cards go blank at that sync. Its sync PR for the last v2.x minor vendors it alone, and its ledger then runs that minor's `migrate` as its own
  PR, as agent-cadence's does, so the merge gate grading the rewrite is v2.8's (`uncovered_decisions()`'s base side,
  D1); that run (v2.7's rules and v2.8's in one, its ledger not yet migrated) stops today on five archived Statuses
  (TD-104, TD-120, TD-226, TD-227, TD-460), each answered with `--as` or `--closed-dates` in that PR; its v3.0 sync runs D5's check first, and drops any read of `Waits`, `Taken by` or `old_form`.

## Not in this design

The board's half of v3.0 (TD-070). When v3.0 is cut, and what else it carries (Paul's). Renaming `**Resolved:**`
to a status-neutral lead (target design §2.2, "v3.0 material"): no entry needs it, and it would rewrite every
archived entry. Removing `status_notes_to_log()` (D6).

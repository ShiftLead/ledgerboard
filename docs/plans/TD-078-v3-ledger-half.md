# TD-078: v3.0's ledger half — the last migration, a note for archived entries, and the removals

**Status:** Draft 7, 2026-11-12 (session lb-designer). Class: **wide** — it changes a vendored, published format
read and written by both consumers, and plans a major (cadence.md §4.8; cap 6 rounds). Rounds: six ran, the cap (build-changing per design review 6, 2, 2, 1, 2, 1; fact-checks 7, 1, 1, 0, 0, 1), their fixes applied; the rounds ended at the cap, so the closing fact-check and Paul's end-of-rounds item follow.

**Entry:** [TD-078](../ledger/TD-078.md). **Source:** the entry's Why and Fix; [target design](target-design.md)
§2.1 (the retired fields and words) and §7.1's v3.0 row; [TD-070's plan](TD-070-board-directory.md) D12 (the
release order) and *Not in this design*; [TD-058's plan](TD-058-status-release.md) (v2.7's `migrate`); `SPEC.md`
*The ledger* (*The old form*, *Retired words*), *The next id*, *Ledger entries and their edits*, *Migrating to
v2.7*, *The ledger writer* and *Versions*; the module and `ledger.py` at `origin/main` (`ef18845`, cited by
function); the three roster repos' ledgers as they stood on 2026-11-11 (counted with the module's own readers).

## The problem

v2 keeps reading four forms only because old files hold them: the `Waits` field, the `Taken by` field, the old
decision form `decision (<who>) <text>` in `Blocked by`, and a `Resolved` header field. v2.7's `migrate` maps the
old Status words, `Added` comments and a header `Location`, and leaves those four as they are (*Migrating to
v2.7*, rule 5). §7.1 plans v3.0 to stop reading them and to remove `migrate`, once every repo holds none of them,
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
thirteen old-form entries nine already have an `**Ask:**` section (ShiftLead's six open and three archived). The agent-cadence tree this repo pins (`67023cc`)
still writes `Taken by` on every `new` and `renumber` (its `render()` and `plan()`), so this repo's count grows
until its pin moves past agent-cadence's TD-188 step 4, which agent-cadence's `main` (`acf46ea`, 2026-11-12)
already carries: it writes `Id take` alone and drops a carried `Taken by` on `renumber`.

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
  carries as `decision (<who>)` (any item of the value as written, retired roles included, compared by
  `_gate_key`), which would leave the item twice (`gate-repeated` for a person).

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
before TD-070's B1, and B1 is `Blocked by` them (*The builds*). The minor is v2.8 when it is cut after they merge,
which is the order the board's open *Release v2.8* item allows; if v2.8 is cut first, they ship as v2.9, still
before B1 merges. The rule for the number: each build writes, wherever the texts below say v2.8, the first minor
not yet tagged when that build merges (v2.8 if it is untagged then, else v2.9), and whichever of B1 and B2 merges
second rewrites the other's number to its own when that is still untagged, so both name one minor; the Consumers
lines say *the last v2.x minor*. TD-070's D12 and its `Doer:` text, where they name v2.8 as the release before its
B1, read as that minor.

`Blocked by` B1 and B2 alone would let TD-070's B1 merge while they sit untagged on `main`, after which D12 allows no
v2.x release. So TD-070's B1, when filed, is `Blocked by` TD-078's B1 and B2 and `decision (paul)`, its Ask: *Is
the last v2.x minor tagged, holding TD-078's B1 and B2, with nothing on `main` past that tag under `ledgerboard/`,
`SPEC.md` or `fixtures/`?* — lifted by Paul's answer once he has cut it (written by whichever of TD-070's and
TD-078's build filings comes second, with its board item; TD-070's plan's D12 amendment says so too). The release
is Paul's.

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
  (`fullmatch`, where today it matches a prefix), so `decision (<who>) <text>` is neither the old form nor a
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
  `lift_gate()` and `reassign_gate()` refuse it as a gate the entry does not carry. A person's name still compares
  in any case (`_gate_key`). So that it is named wherever it stands, `check()`'s retired records (above) include,
  on every entry open or archived, each `Blocked by` item that opens with `decision (<who>)` and has text after
  it, as *the old decision form*: one error per value, since the old item is the value's first `decision (`
  with text after it to the value's end (`decision (a) — x, decision (b) — y` is one old item, as `parse_gates()`
  reads it today); the error is for the whole old item (from its `decision (` to the value's end, as
  text 1 rule 8 defines it, commas and all), its text naming that item, beside the unreadable items' own flags on
  an open entry (one per comma-split piece, as `parse_gates()` splits any value).
- **`migrate` goes:** `migrate_entry()`, `migrate_subject()` and their helpers, `ledger.py migrate`, and
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

**D5. The precondition, as one command per repo.** v3.0's precondition (§7.1, *Versions*' v2.7 paragraph) is
met in a repo when, run with the last v2.x, `ledger.py migrate --plan --release <x.y>` prints `entries` with no
entry holding `changes` or `stops`. With D1 that covers every old form: the Status set, `Added`, `Location` and
the four. Each consumer runs it first in its v3.0 vendor PR, before vendoring, and records its output in the PR.
No new check is added: the command exists, and its output is what the precondition means.

**D6. What v3.0's ledger half leaves.** `status_notes_to_log()` and the lifting of a Status's notes in `note`,
`archive` and `reopen` stay: on an entry in the closed set they lift nothing, and removing them changes nothing a
precondition-clean ledger reads. Their date fallback loses the header `Resolved`: `_fallback_day()` reads the body
`**Resolved:**` line, else `Added`, as v3.0 reads no retired field for its old meaning (text 7); after the
precondition no entry holds one, and on an entry that still does (a retired error) a lifted note is dated by
`Added`. `_closing_source()`'s like read goes with `migrate_entry()`. The retired gate `hold` and the role `decision (designer)` stay retired items
that keep the block (no repo holds either). The ledger's declared major stays 2 (`FORMAT_MAJOR` untouched, as TD-070's B5 leaves it), since a v2 ledger that meets the
precondition reads the same under v3.0. A ledger that declares `Ledgerboard: 3` is refused by v3.0 as by v2.x
(`version_problem()`: newer than the module reads), which is right: no ledger form of major 3 exists.

## The `SPEC.md` text

Each text says where it lands and what it replaces. Texts 1–5 are B1's and B2's (the last v2.x minor, written
here as v2.8); texts 6–12 are B4's (v3.0).

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
> `decision (<who>)` for the same `<who>` (`_gate_key`; a retired role included, though `gate_items()` omits it),
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

**Text 4 (B1, then B2), *Versions*, after the v2.8 title paragraph.** Two paragraphs, each true alone, in this order
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
> form (*The old form*, above), which is also an unreadable item; another retired item in `Blocked by` is ℹ and keeps the block;
> and a Status outside the closed set is an error (*The closed Status set*). A retired error's text ends *v3.0
> reads no such form: on an open entry* followed by its field's cure — *remove it with `set` (an empty value)* for
> `Waits` and `Taken by`; *move its value with `edit --section Location`, then remove it with `set`* for a header
> `Location`; the same with `--section Resolved` for a header `Resolved`; *write its text with `edit --section
> Ask`, then rewrite it `decision (<person>)` with `set`* for the old decision form — then *; on an archived one by hand, then
> `ledger.py fmt TD-n`*.

Its second item, "in `Blocked by`, the gate `hold` (…), the old form above, and a role in `decision (…)`, …",
loses "the old form above, and": the old form is no longer read as a retired item (text 6). Its third item's
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
> `parse_gates()`'s record loses `old_form`; `judge_takes()` loses `accept_taken_by`; `canonical()` places no
> `Taken by`; and `migrate`, `migrate_entry()` and `migrate_subject()` are gone, while `subject_kind()` still names a
> migrate subject. A v2 ledger that met the precondition (*v2.8*, above) reads exactly as under v2.8, and declares
> no new major. One that did not is not misread: each old form is an error that names it.

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
- `fixtures/grammar/`: the `added` verdict judged by `_real_day()` (text 9), its cases unchanged;
- `fixtures/ledger/`'s check cases gain `retired_waits_archived`, `retired_taken_by_open`,
  `retired_resolved_header`, `retired_location_header`, `retired_taken_by_archived` (each an error on a ledger no
  edit touched), `retired_old_form_open` (two errors: the retired record and the unreadable item),
  `retired_old_form_archived` (one, the retired record) and
  `retired_v1_info` (ℹ on a v1 ledger); `fixtures/ledger/gates.json`'s TD-115 old-form case (its records are
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
  entry: one retired record naming the whole item, beside the comma-split pieces' unreadable-item flags);
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
  docs/ledger` with B2's module, as its own PR: this repo's ledger has not run v2.7's rules either: on 2026-11-12
  `migrate --plan` changes four entries, the open TD-065, TD-070 and TD-078 (this design's own; a Status with notes
  → `Open`, with a `was:` Log line) and the archived TD-076 (its Status, and `Location → body`); it holds 53 `Taken by`, 2 header `Resolved` and 1 `Waits`. Its
  stops, if any, are decided in the PR. **Blocked by** B2. Done when `migrate --plan` shows no entry with changes
  or stops. Entries filed afterwards through the pinned agent-cadence writer may carry `Taken by` again until
  agent-cadence stops writing it (*Consumers*); B4's own run of the plan catches them.
- **B4 — v3.0's ledger removals (D4).** Location: `ledgerboard/__init__.py` (`RETIRED_FIELDS`, `pickable()`'s ℹ
  `retired` field flag, `uncovered_decisions()`'s old-form base-side count (B2's), `WAITS_WRITTEN`, `LOCATION_WRITTEN`, `WRITTEN_RETIRED` and `check()`'s `written` grading,
  `check()`'s retired records over every entry (fields and the old decision form), `GATE_DECISION_RE`'s whole match
  and `parse_gates()`, `edit_entry`'s `set`, `archive` and `reopen`, `_written_blocked()`, `OLD_FORM_REPLACES`,
  `_without`, `reassign_gate()`, `_blocked_items`, `_one_copy`, `_item_gate_key`, `ENTRY_ORDER`, `judge_takes()`,
  `status_problem()`'s message, `_fallback_day()`'s header read (D6); `migrate_entry()`, `migrate_subject()` and their helpers removed),
  `ledgerboard/ledger.py` (`migrate` and the `set` route's old-form refusal removed; `note`'s refusal of an
  archived Status outside the closed set kept, its message text 10's cure in place of *run migrate first*),
  `fixtures/run.py`, `SPEC.md` (texts 6–12), the fixtures above, `tests/`. **Blocked by** B1, B2, B3 and TD-070 (the design entry archives with
  its last build, B5), so v3.0's ledger removals land after its board half and no v2.x release can follow them.
  Before B4 starts, its builder runs `migrate --plan` on this repo's ledger with `main`'s module; if entries filed
  since B3 (through the pinned agent-cadence writer, which may still write `Taken by`) show changes, a re-run of
  B3's command lands first as its own PR. B4's PR states that run.

**The order with TD-070's builds:** B1 and B2, then the last v2.x minor (Paul's), and B3; TD-070's B1 is `Blocked
by` B1, B2 and Paul's decision that the minor is cut (D3; written on whichever is filed second); TD-070's B1–B5; then B4; then v3.0 (Paul's).

## Consumers

Lines for each consumer's own entry, filed there through its question seat (`ao td add --repo`), never here.

- **agent-cadence** (as its `main` stands at `acf46ea`, 2026-11-12, which vendors v2.7; the tree this repo pins,
  `67023cc`, is older and is not what these lines describe):
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

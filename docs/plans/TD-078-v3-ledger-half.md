# TD-078: v3.0's ledger half — the last migration, a note for archived entries, and the removals

**Status:** Draft 2, 2026-11-12 (session lb-designer). Class: **wide** — it changes a vendored, published format
read and written by both consumers, and plans a major (cadence.md §4.8; cap 6 rounds). Rounds: round 1 ran (fact-checks 6 build-changing, design review 6), its fixes applied.

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
   — not as the route by which three repos rewrite some 290 entries. The entry asks that each repo meet the
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
thirteen old-form entries nine already have an `**Ask:**` section (ShiftLead's six open and three archived). agent-cadence's pinned `ledger.py` still writes
`Taken by` on every `new` and `renumber` (its `render()` and `plan()`, pinned tree `67023cc`), so its count grows
until it stops.

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
  the entry has none, else into one plain Log line; a `<who>` that is neither a person's name nor a retired role is
  a stop, since `decision (<who>)` would be an unreadable item (no real entry has one).

Text 1 is the one exact statement of the rules; this list is its summary. Three choices in it are this design's:
- **The dates.** A line about the entry's filing (`Taken by`, a `Waits`, an old decision's text) is dated by
  `Added`, placed first, as rule 3 places an `Added` comment: the take and the wait began then. On an **open entry
  carrying a gate** it is dated instead so that it can never become the Log's first dated line (the first readable
  Log line's date, placed after its equals), because `gate_age()` falls back to that line's date, and a
  first line dated `Added` would move an older gate's age. The date is read after rules 1–4. Rules 1–4 themselves
  can still move a gate's age (rule 3's line and rule 1's `was:` line, as *Migrating to v2.7* says); rules 5–8
  never do.
- **The text of the old form** goes to the `**Ask:**` the cadence asks every decision to carry (cadence.md §2.3),
  where the entry has none; where it has one, the existing Ask stands and the old text is kept in the Log.
- **Each Log line is a plain note:** `Taken by`, `Waits` and `Blocked by` begin no writer's prefix, so `log_line()`
  reads each as a note and `check()`'s `log-line` passes it.

The **post-condition** gains one clause: the migrated entry holds none of the four forms, else it is a stop.

*Alternatives weighed.* (a) A `set` and `edit` that take archived entries, and each repo rewriting its 290 old
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
archived entry takes a note — *run migrate first*; on every other archived entry it only appends to history. `set` and `edit` still take only open entries; a change to what an archived entry *says* is a
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
not yet tagged when that build merges (v2.8 if it is untagged then, else v2.9); TD-070's D12 and its `Doer:` text,
where they name v2.8 as the release before its B1, read as the last minor tagged before its B1 merges. The release is Paul's.

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
  header `Resolved`, nor its `reopen` moves one or refuses an entry with both: each writes what it writes beside
  it, and the error stands.
- **The old decision form:** `parse_gates()` no longer reads it as a decision. `GATE_DECISION_RE` matches a whole item
  (`fullmatch`, where today it matches a prefix), so `decision (<who>) <text>` is neither the old form nor a
  decision but an unreadable item (`bad`), which keeps the block, names no holder and is an error (an unreadable
  `Blocked by` item, as today). Its record loses `old_form`, and `retired` loses the kind `old-form`. Every
  old-form path goes with it: `OLD_FORM_REPLACES`; `_written_blocked()`'s two refusals (the old form, and a gate
  added beside it), which `edit_entry`'s `set`, `entry_text()` and `reassign_gate()` call (each
  caller checked), and `edit_entry`'s carried-gates clause, with their
  docstrings and `parse_gates()`'s; `_without`'s refusal, which `lift_gate()` and `reassign_gate()` share; `reassign_gate()`'s
  own; `_blocked_items`', `_one_copy`'s and `_item_gate_key`'s old-form branches; and `ledger.py`'s `set`-route
  refusal (*migrate it first*). A value holding the item is then written by `new` and `set` as any unreadable item
  is, for `check()`, whose error the writer's refusal rule (an error the ledger before did not have) refuses; and
  `lift_gate()` and `reassign_gate()` refuse it as a gate the entry does not carry. A person's name still compares
  in any case (`_gate_key`). So that it is named wherever it stands, `check()`'s retired records (above) include,
  on every entry open or archived, each `Blocked by` item that opens with `decision (<who>)` and has text after
  it, as *the old decision form*: one error naming it, beside the unreadable item's own flag on an open entry.
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
precondition-clean ledger reads. The retired gate `hold` and the role `decision (designer)` stay retired items
that keep the block (no repo holds either). The ledger's declared major stays 2 (`FORMAT_MAJOR` untouched, as TD-070's B5 leaves it), since a v2 ledger that meets the
precondition reads the same under v3.0. A ledger that declares `Ledgerboard: 3` is refused by v3.0 as by v2.x
(`version_problem()`: newer than the module reads), which is right: no ledger form of major 3 exists.

## The `SPEC.md` text

Each text says where it lands and what it replaces. Texts 1–5 are B1's and B2's (the last v2.x minor, written
here as v2.8); texts 6–12 are B4's (v3.0).

**Text 1 (B2), *Migrating to v2.7*, rule 5 replaced.** The paragraph "**5. What it leaves.** A `Waits` line, a
`Taken by`, an old-form decision, every other field and section, and every Log line already there are left as they
are. …" becomes:

> The rules below read the entry rules 1–4 left. *The filing date* (v2.8) is `Added` when that is a real date,
> else the first readable Log line's date, else `today`, and a line dated by it is placed before the first Log line
> dated on or after it. *The gate-neutral date* is the first readable Log line's date (the first, in file order,
> that `log_lines()` gives a date), else `Added` when that is a real date, else `today`, and a line dated by it is
> placed after every Log line of an equal date. *The entry's date* is the gate-neutral date on an open entry whose
> `Blocked by` carries a gate (`gate_items()`, or the old decision form), and the filing date on any other.
> So rules 5–8 never move a gate's age (`gate_age()`), unless the entry has neither a readable Log line nor a real
> `Added`.
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
> **8. The old decision form** (v2.8). A `Blocked by` whose last item is `decision (<who>) <text>` (the old form,
> *The ledger*) has that item rewritten `decision (<who>)`, `<who>` as written and the other items kept in their
> order; when `<who>` is neither a person's name nor a retired role (*Retired words*), it is a **stop**. `<text>`,
> less its leading run of `—`, `–`, `-`, `:` and whitespace, is written as the body section `**Ask:** <text>`,
> placed as `edit` places a section the body lacks, when the entry has no `**Ask:**`; when it has one, the whole old
> value is written as one plain Log line, `Blocked by <value>`, dated by the entry's date. An empty `<text>` writes
> neither. No `gate added` line is written.
>
> A stop from rule 2 wins over these rules: stops are collected first, and with one the input is returned as given.
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

> From v2.8 the migrated entry also holds no `Taken by`, `Waits`, header `Resolved` or old decision form; one left
> is the stop `migrated entry still holds <field>`.

*The words it returns* gain: in `changes`, `Taken by → Log`, `Taken by (empty) removed`, `Waits → Log`, `Waits
(empty) removed`, `Resolved → body`, `Resolved (empty) removed`, `old decision form → Ask`, `old decision form →
Log` and `old decision form (no text)`; in `stops`, `Waits on an open entry`, `Resolved in the header and the
body`, `old decision form: <who> is not a person` and `migrated entry still holds <field>` (`<field>` one of
`Taken by`, `Waits`, `Resolved`, `Blocked by`).

**Text 2 (B2), *The ledger*, *The old form*.** "…migrate it first, to `decision (<person>)` with its text in
`**Ask:**`. v3.0 stops reading it." becomes:

> …migrate it first, to `decision (<person>)` with its text in `**Ask:**`, which `migrate` does from v2.8 (*Migrating
> to v2.7*, rule 8). v3.0 stops reading it.

**Text 3 (B1), *The ledger writer*, the `set`, `note`, `edit` bullet.** "An archived entry is edited only once
reopened." becomes:

> `note` (v2.8) also takes an archived entry, writing its file where it is in `archive/`; `set` and `edit` take an
> archived entry only once reopened.

**Text 4 (B1, then B2), *Versions*, after the v2.8 title paragraph.** Two paragraphs, each true alone: B1 writes
the first, B2 the second.

> **v2.8 gives an archived entry a note** (*The ledger writer*): `ledger.py note` writes an archived entry whose
> Status is in the closed set in place, where v2.7 refused it, and refuses one whose Status is not (*run migrate
> first*). Nothing read changes, and no key moves.

> **v2.8 gives `migrate` the last old forms** (*Migrating to v2.7*, rules 5–8): it maps `Taken by`, `Waits`, a
> header `Resolved` and the old decision form, which v2.7's left. Nothing read changes: every line it writes is one
> v2.7 reads (a body section, a plain Log line, a `decision (<who>)`), and no key moves. A repo that ran v2.7's
> `migrate` runs v2.8's once more, as its own PR.

**Text 5 (B2), *Versions*, the v2.7 paragraph's last sentence.** "`migrate` stays through v2.x and goes in v3.0,
whose precondition is that `migrate --plan` shows no entry with changes in every repo." becomes:

> `migrate` stays through v2.x and goes in v3.0, whose precondition is that, with the last v2.x, `migrate --plan`
> shows no entry with changes or stops in every repo (v2.8: its rules cover every old form, open and archived).

**Text 6 (B4), *The ledger*, *The old form*, replaced whole:**

> **The old form** `decision (<who>) <text>` — a decision followed by anything but a comma or the end of the
> line — was read by v2 as a decision by `<who>`. v3.0 does not read it: it is an unreadable item, which keeps the
> block, names no holder, and is an error. Its replacement is `decision (<person>)` with the text in `**Ask:**`.

**Text 7 (B4), *Retired words*, the paragraph's lead and its first list item.** "Where v2.x still reads one,
`check()` names it *retired* (ℹ, `retired`) with what replaces it, rather than unknown — except a Status word,
which from v2.7 is an error (*The closed Status set*):" becomes:

> v3.0 reads none of them for its old meaning. `check()` names each it meets *retired*, with what replaces it,
> rather than unknown: a retired field — `Waits`, `Taken by`, a header `Resolved` or a header `Location` — is an
> error (`retired`) on every entry, open or archived, of a ledger that declares major 2 or more, whether or not the
> edit changed the entry (never `standing`), and ℹ on a v1 ledger; so is a `Blocked by` item in the old decision
> form (below), which is also an unreadable item; another retired item in `Blocked by` is ℹ and keeps the block;
> and a Status outside the closed set is an error (*The closed Status set*). A retired error's text ends *v3.0
> reads no such form: on an open entry* followed by its field's cure — *remove it with `set` (an empty value)* for
> `Waits` and `Taken by`; *move its value with `edit --section Location`, then remove it with `set`* for a header
> `Location`; the same with `--section Resolved` for a header `Resolved`; *rewrite it `decision (<person>)` with
> `set`, its text in `edit --section Ask`* for the old decision form — then *; on an archived one by hand, then
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
name in any case), so `Decision (kim)` rewritten `decision (Kim)` is kept; `archive` loses "and a `Resolved` header
field is removed"; `reopen` loses "A `Resolved` header field moves into a `**Resolved:**` section before the Log,
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
v2.7's `migrate` maps (*Superseded and dropped*, the Status's notes under *The Log*) are history and stay.
`status_problem(text, *, archived)`'s definition moves to *The closed Status set*, unchanged but for its message's
ending (text 10). The `set` route's sentence "a decision still in the old form is not dropped by `set` (*migrate it
first*)" is removed.

**Text 10 (B4), *The closed Status set*.** "…and ends *run migrate, which maps it, lists it, or names what a person
decides*." becomes:

> …and ends *v3.0 reads no other form: on an open entry write `Open` with `set`, on an archived one by hand, then
> `ledger.py fmt TD-n`*. `status_problem(text, *, archived)` gives that problem of one entry's Status, or None.

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
- `waits_archived`, `waits_archived_empty`, `waits_open_stops`;
- `resolved_header_archived` (to the body, before the Log), `resolved_header_no_log` (at the end),
  `resolved_header_and_body_stops`, `resolved_header_empty`;
- `old_form_no_ask` (Ask written after the Why), `old_form_with_ask_open` (Log line dated by the entry's date;
  its gate's `gate_age()` unchanged), `old_form_with_ask_no_log` (the line becomes the Log's first, dated by
  `Added`), `old_form_with_ask_archived`, `old_form_ids_kept` (`TD-3, decision (Kim) — x`),
  `old_form_no_text` (`decision (Kim) —`), `old_form_role` (`decision (designer) — x`: rewritten, still retired),
  `old_form_not_a_person_stops` (`decision (the owner) — x`);
- `all_four_and_status` (each rule's order on one entry), `rerun_unchanged` (each case's output run again changes
  nothing);
- the existing `waits_taken_by_old_form_left` (an open entry holding `Waits: the vendor`) becomes
  `waits_taken_by_old_form_open_stops` (rule 6's stop wins, the input returned as given), and a new
  `waits_taken_by_old_form_archived` maps all three;
- `fixtures/run.py` records each case's `gate_age()` before and after in its expected JSON, asserting nothing; a
  unit test in `tests/test_ledgerboard.py` asserts the two are equal on every new case with a gate, a readable Log
  line or a real `Added`, and on which rules 1–4 write nothing (`all_four_and_status` and
  `taken_by_added_not_a_date` are outside it);
- `fixtures/ledger_writer/migrate_old_forms` — `migrate --plan` over a directory with one of each, open and
  archived: the plan, its `entries` and the subject.

**B4**:
- removed: `fixtures/migrate/cases.json`'s `migrate_entry` group and the `migrate_*` writer cases, with
  `run.py`'s migrate groups; its `status_problem` group (30 cases) moves to `fixtures/status/cases.json`, run by
  a `status` group in `run.py`;
- `fixtures/grammar/`: the `added` verdict judged by `_real_day()` (text 9), its cases unchanged;
- `fixtures/ledger/`'s check cases gain `retired_waits_archived`, `retired_taken_by_open`,
  `retired_resolved_header`, `retired_location_header` (each an error on a ledger no edit touched) and
  `retired_v1_info` (ℹ on a v1 ledger); `fixtures/ledger/gates.json`'s records lose `old_form`, and its old-form
  cases read the item as unreadable;
- `fixtures/ledger_edit/`: `refused_old_form` (the `entry_text` group), `set_refused_old_form`,
  `set_refused_gate_on_old_form`, `set_migrates_old_form`, `set_migrates_old_form_no_today` and
  `set_other_field_keeps_old_form` rewritten (the value written as given, `check()` naming the unreadable item);
  `fixtures/ledger_writer/set_old_form` likewise (refused by the writer's refusal rule);
- `fixtures/lift/cases.json`'s two `old_form_refused` cases refuse it as a gate the entry does not carry;
- `fixtures/ids/cases.json` and `run.py`'s `ids` group lose `accept_taken_by`, and an entry with only a
  `Taken by` fails `id-no-take`;
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
  post-condition), `ledgerboard/ledger.py` (the `migrate` docstrings), `SPEC.md` (texts 1, 2, 4's second paragraph,
  5), `fixtures/migrate/`, `fixtures/ledger_writer/migrate_old_forms`, `tests/`. B1 and B2 in either order.
- **B3 — this repo's own ledger migrated.** `python3 -m ledgerboard.ledger migrate --release <the minor> --ledger
  docs/ledger` with B2's module, as its own PR: this repo's ledger has not run v2.7's rules either (its
  `archive/TD-076.md` fails `status_problem()`) and holds 53 `Taken by`, 2 header `Resolved` and 1 `Waits`. Its
  stops, if any, are decided in the PR. **Blocked by** B2. Done when `migrate --plan` shows no entry with changes
  or stops. Entries filed afterwards through the pinned agent-cadence writer may carry `Taken by` again until
  agent-cadence stops writing it (*Consumers*); B4's own run of the plan catches them.
- **B4 — v3.0's ledger removals (D4).** Location: `ledgerboard/__init__.py` (`RETIRED_FIELDS`, `pickable()`'s ℹ
  `retired` field flag, `WAITS_WRITTEN`, `LOCATION_WRITTEN`, `WRITTEN_RETIRED` and `check()`'s `written` grading,
  `check()`'s retired records over every entry (fields and the old decision form), `GATE_DECISION_RE`'s whole match
  and `parse_gates()`, `edit_entry`'s `set`, `archive` and `reopen`, `_written_blocked()`, `OLD_FORM_REPLACES`,
  `_without`, `reassign_gate()`, `_blocked_items`, `_one_copy`, `_item_gate_key`, `ENTRY_ORDER`, `judge_takes()`,
  `status_problem()`'s message; `migrate_entry()`, `migrate_subject()` and their helpers removed),
  `ledgerboard/ledger.py` (`migrate` and the `set` route's old-form refusal removed; `note`'s refusal of an
  archived Status outside the closed set kept, its message text 10's cure in place of *run migrate first*),
  `fixtures/run.py`, `SPEC.md` (texts 6–12), the fixtures above, `tests/`. **Blocked by** B1, B2, B3 and TD-070 (the design entry archives with
  its last build, B5), so v3.0's ledger removals land after its board half and no v2.x release can follow them.
  Done when also: `migrate --plan`, run with the last v2.x on this repo's ledger before the removal, shows no
  entry with changes or stops.

**The order with TD-070's builds:** B1 and B2, then the last v2.x minor (Paul's), and B3; TD-070's B1 is `Blocked
by` B1 and B2 (written on whichever is filed second); TD-070's B1–B5; then B4; then v3.0 (Paul's).

## Consumers

Lines for each consumer's own entry, filed there through its question seat (`ao td add --repo`), never here.

- **agent-cadence**:
  - its `ledger.py`'s `prose_waits` (pinned tree `67023cc`, `files/scripts/ledger.py`) scans the raw text after
    `decision (…)` in a `Blocked by` for ids, through its vendored `DECISION_RE`; v2.8's `migrate` moves that text
    into an `**Ask:**` or the Log, so an id named only there stops being seen. Its two open old-form entries (TD-065,
    TD-144) name none there today; its v2.8 vendor PR checks that again before running `migrate`, and the scan's
    old-form span goes once no old form can stand (v3.0);
  - its `ledger.py` stops writing `Taken by` on `new` and `renumber` and writes `Id take` alone (its TD-188's step
    4), before its v3.0 vendor PR, since every `Taken by` is a v3.0 error;
  - its v2.8 vendor PR passes `note` on an archived entry through its wrapper, and runs v2.8's `migrate` over its
    ledger as its own PR;
  - its v3.0 vendor PR first runs `migrate --plan` with v2.8 (D5) and records it, then removes `migrate` from its
    wrapper and `accept_taken_by` from its `judge_takes()` call, and reads `parse_gates()` without `old_form`.
- **ShiftLead**: its Queue card's *held until …* reads the old form's text (`src/sessionorc/ledger.py`'s
  `until_of`, through `parse_gates()["old_form"]`), and seven open entries carry one; v2.8's `migrate` moves the
  text into an `**Ask:**` or the Log, so before its ledger runs it, `until_of` reads the `**Ask:**` (or the gate
  alone), else those cards go blank at the v2.8 sync. Its sync PR for v2.8 runs `migrate` (v2.7's rules and v2.8's in one run, its ledger not yet
  migrated); its v3.0 sync runs D5's check first, and drops any read of `Waits`, `Taken by` or `old_form`.

## Not in this design

The board's half of v3.0 (TD-070). When v3.0 is cut, and what else it carries (Paul's). Renaming `**Resolved:**`
to a status-neutral lead (target design §2.2, "v3.0 material"): no entry needs it, and it would rewrite every
archived entry. Removing `status_notes_to_log()` (D6).

# TD-058: v2.7, the Status release, and `migrate`

**Status:** Draft 1, 2026-11-11 (session lb-designer). The scope (S1–S8 below) is Paul's, agreed 2026-11-11 (his
`Go` on the board's decide item, which lifted TD-058's `decision (paul)`). Class: **wide** (a vendored, published
format: the closed Status set, the canonical entry form and `migrate`, which both consumers vendor and run; cap 6
rounds, cadence.md §4.8). Rounds: round 1 running (draft 4 holds its fact-checks' fixes, F1–F33) (the record: [docs/reviews/TD-058.md](../reviews/TD-058.md)). The
builds are filed only on Paul's go after the rounds.

**Entry:** [TD-058](../ledger/TD-058.md). **Source:** [target design](target-design.md) §2.1, §2.2, §7.1 (the v2.7
row and its amendments), §7.2 step 6, §7.3, §7.4.

## The problem

The target design ends the v2 migration with a release that closes the Status vocabulary, moves the old Status
notes and `Added` comments into the Log, and ships `migrate`, the tool that maps a ledger's old forms to the new
ones. The design first called that release v2.5, then v2.6, now v2.7 (§7.1's amendments). `SPEC.md` already names
"v2.7's `migrate`" in three places (*Retired words*, the Status grammar under *The Log*, the tripwire's
exemption), and v2.7 work has landed (TD-046, TD-056). But the newest tag is v2.6, and `migrate` is not built:
only `migrate_subject()` (the commit subject) and `status_notes_to_log()` (the Status-notes lift that `note`,
`archive` and `reopen` already call) exist. There is no `migrate_entry()` and no `ledger.py migrate`.

The precondition §7.1 sets now holds: on 2026-11-07 no open entry in ledgerboard's, agent-cadence's or
ShiftLead's ledger carries a `Waits` line. The forms `migrate` exists for still stand (the entry's count: in
ShiftLead, 12 old-form decisions and 36 retired Status words; in agent-cadence, 2 old-form decisions and a `Taken
by`), flagged only as ℹ.

## What exists today, and what v2.7 adds

| Piece of the v2.7 row | Today (v2.6 + main) | v2.7 adds |
|---|---|---|
| The closed Status set (§2.2's table) | `Open`, `Resolved`, `Superseded`, `Dropped` read; the open stage words `Designed`, `Built`, `Partly`, `Live`, `In` flagged ℹ `retired`; `Done`, `Moved`, `OBE` read as closed | `check()` errors on a Status outside the table (word, date, `by` target, directory): D1 |
| The Log's migration | the Log, its shapes and `status_notes_to_log()` (v2.4); the writers lift a note before they write | `migrate_entry()`: Status tails and `Added` comments into Log lines, in date order: D2 |
| Archived Status words | read as closed and done, except a word outside the reader's Status words, which keeps the block (TD-039) | mapped by §2.2's table; an unmapped one stops `migrate`: D2 |
| Stage words on open entries | ℹ `retired` | `Open` + a Log line, and `Kind` from the caller's map: D2 |
| `Location` to the body | a format header field, last in the canonical order | a body section; a header `Location` is retired, graded as `Waits` is: D4 |
| `Waits` | an error when an edit writes or changes one (TD-046); still in the canonical order | out of the canonical order: D4 |
| `Kind` per §2.3 | a consumer field (§2.3 (i)) | nothing in the module (S4) |
| The grammar appendix | the board item line, `Blocked by`, Event sections, a person's name, the rank file | the header block, the Status and the Log lines: D5 |
| `ledger.py migrate` | — | the command: D3 |

## The scope (agreed 2026-11-11)

- **S1.** The closed Status set, an error on every entry, open or archived (§2.2). A consumer takes v2.7 in one PR
  that vendors it and runs `migrate`.
- **S2.** The migration map as §2.2 writes it, with **one addition**: an archived entry that needs a date no source
  gives stops `migrate` rather than guessing one. The archiving commit's date is the caller's, passed in.
- **S3.** Stage words set `Kind` only from a map the caller passes (**a departure** from §2.2, which had the module
  set `build` and `live-check`: `Kind`'s words are consumer vocabulary, §2.3 (i), and AGENTS.md keeps consumer
  knowledge out of the package). With no map, `Kind` is left alone and the entry is listed.
- **S4.** `Kind` per §2.3 is nothing in the module.
- **S5.** `Location` moves to the body (a canonical-form change).
- **S6.** `Waits` leaves the canonical order; `migrate` does not touch a `Waits` line.
- **S7.** `migrate` ships in v2.7, stays through every v2.x and is removed in v3.0 with the reading of the old
  forms; v3.0's precondition is that `migrate --dry-run` gives no diff in every roster repo. This PR adds it to
  the target design's §7.1 v3.0 row.
- **S8.** The grammar appendix adds the header block and the Log's fixed line shapes.

## The design

### D1. The closed Status set in `check()`

An entry's Status is one of four forms, and its form agrees with where the entry is:

| Status | Where | Written by |
|---|---|---|
| `Open` | the ledger | `new`, `reopen`, `migrate` |
| `Resolved YYYY-MM-DD` | the archive | `archive`, `migrate` |
| `Superseded YYYY-MM-DD by <id>` (`TD-n` or `<repo>#TD-n`) | the archive | `archive --superseded-by`, `migrate` |
| `Dropped YYYY-MM-DD` | the archive | `archive --dropped`, `migrate` |

- The value is compared exactly, as the writers write it: the word capitalised so, one space between parts, a real
  date, an id by `Blocked by`'s grammar, nothing after. `Open 2026-10-01`, `Resolved 2026-10-03.`, `resolved
  2026-10-03` and `Resolved 2026-10-03: shipped` are all outside the set. So is an entry with no `Status`.
- **Where it lives:** a new pure function, `status_problem(text, *, archived) -> str | None`, gives the one problem of
  one entry's Status, or None. `check()` runs it over every entry of the ledger (`archived=False`) and of the archive
  (`archived=True`), and appends its records on both of `check()`'s exits: before its early return when `old` is
  None, and **after** the loop that grades records standing under `old` (where `archive-open-parts` is appended), so
  no `status` record is ever made standing or ℹ by it.
- **Its flag:** kind `status`, field `status`, an **error on every entry, never standing**, whether or not `check()`
  is given `old`, on a ledger that declares major 2 (*Versions*). On a v1 ledger it is ℹ: `migrate` takes a v2
  directory, so a v1 ledger splits first (*The ledger as a directory*).
- **Its text names the form, never the whole value**, so an edit that changes only a tail (a `note` lifting it)
  leaves the flag's text as it was, and the writer, which refuses a write only for an error the ledger before it did
  not have, still writes it. The text is `⚠ TD-n: Status <Word> is not <the form the place takes> — run migrate, which maps it or lists it
  for a person`,
  `<Word>` being the value's first word as `first_word()` reads it (or *no Status*), and, for a word *Retired words*
  lists, ` (retired: <what replaces it>)` before the dash, by the entry's place: on an open entry `RETIRED_STATUS`'s
  text for the five open words, and `Open` for an archived word; on an archived entry `Resolved` for `done`, `built`
  and `designed`, `Superseded or Dropped` for `moved`, `Dropped` for `obe`, and `Resolved, Superseded or Dropped`
  for `partly`, `live` and `in` (a second map beside `RETIRED_STATUS`).
- **It replaces v2.4's ℹ `retired` on an open entry's Status word**: `pickable()`'s flags no longer carry that
  record (the word is still reserved, and the error names it retired). A caller that reads only `pickable()`'s flags
  so loses that notice; every consumer's merge gate runs `check()`, which carries the error. `pickable()`'s `unknown-status` and
  `blocker-unknown-status` stay as they are: they say how a reader reads a blocker, and `status` says the form is
  wrong; an archived entry with an unknown word carries both.
- What `pickable()` and the cross-repo resolver read of an archived blocker's Status (*Superseded and dropped*) is
  unchanged: a reader still reads another repo's old words, since that repo may not have migrated yet.

Why an error on every entry, not only on a changed one: `migrate` leaves no entry outside the set, so a repo that
vendors v2.7 and runs it in the same PR passes; and a word left standing would stay forever, which is what the
release exists to end (S1).

### D2. `migrate_entry()`: one entry, pure

`migrate_entry(text, *, archived, today, closed_date=None, kinds=None) -> dict` takes one entry's text (as
`canonical()` takes it), whether the entry is in the archive, the UTC day (`today`, as `edit_entry()` takes it),
the entry's archiving date if the caller has one (`closed_date`), and the caller's map from an open stage word to
a `Kind` value (`kinds`, e.g. `{"designed": "build", "built": "live-check"}`). It reads nothing else and returns
`{text, changes, listed, stops}`: the migrated text (the input unchanged when `stops` is not empty), one line per
change made, the changes a person should review (`listed`), and why it could not migrate (`stops`). Run on its own
output it changes nothing. Text `canonical()` refuses is a stop (`refused: <why>`), not an exception.

**Terms.** *The head reads* when `status_notes_to_log()`'s head grammar (*The Log*, `STATUS_HEAD_RE`) matches the
value: then *the head* is the text it matched (word, date, `by <id>`), *the tail* what follows up to the first ` —
was: `, and *the segments* each ` — was: ` part. *The value's date* is the head's date when the head has one, else (whether
or not the head reads) the first `YYYY-MM-DD` in the value before its first ` — was: `, else none. *The first word* is `first_word()`'s.
*Lifting* is `status_notes_to_log()`'s, with its own dating: the tail as one line dated by the head's date, else the
`**Resolved:**` line's, else `Added`'s; each segment as a `was:` line dated by its own head's date, else the same
fallbacks; each in among the Log by date, after any line of an equal date (its `_log_insert`). Where a tail or segment would
have no date (no head date, no `**Resolved:**` line, no `Added`), `status_notes_to_log()` lifts nothing; `migrate`
then treats the value as **a head that does not read**. *Its new form takes
only its head* when the date and any `by <id>` the new Status keeps come from the head (its word is mapped); a value
whose new form takes anything from beyond its head (an id in the tail, `BY` in upper case, which the head grammar
does not read, a date found only by the scan) is treated as **a head that does not read**.

**1. The Status, an open entry** (`archived=False`), the first branch that applies:

1. The value is exactly `Open` → unchanged.
2. The first word is a stage word (`designed`, `built`, `partly`, `live`, `in`) → when the head reads, the tail and
   segments are lifted (dated as *Lifting* says), then the head is written as one `was: <head>` line; when it does
   not (`In progress`, `Partly done`), the whole value is one `was: <value>` line, nothing lifted. The `was:` line is
   dated by the value's date, else the `**Resolved:**` line's, else `Added`'s, else `today`. The Status is set to `Open`. When the first
   word is a key of `kinds`, `Kind` is set to its value, and when `Kind` held another value, a Log line `Kind <old>
   → <new> (migrate)` is written, dated `today`. With no key for it, `Kind` is left as it is and the entry is
   **listed** (`stage word <Word>, Kind not set`).
3. The head reads and its word is `Open` (`Open 2026-10-01: noted`, `Open 2026-10-01`) → the tail and segments are
   lifted and the Status set to `Open`. With no tail and no segment, the head is written as one `was: <head>` line,
   so the date is kept; with a tail, the lifted line carries the date and no `was:` line is written.
4. Anything else (prose, a bold lead, `Open, held`, an archived word such as `Resolved 2026-10-03: x` on an open
   entry) → the whole value is one `was: <value>` line, dated as in 2, nothing lifted, and the Status set to `Open`;
   **listed** (`Status <first word> set to Open`).

**2. The Status, an archived entry** (`archived=True`). First the closing date `D`: the value's date, else the
`**Resolved:**` line's date (or an older `Resolved` header field's), else `closed_date`; with none, **stop** (`no date
for TD-n's Status`). Then the first word:

| The Status | Becomes |
|---|---|
| already one of the three archived forms | unchanged |
| first word `resolved`, `done`, `built` or `designed` | `Resolved D` |
| first word `superseded`, naming `by <id>` (`LOG_ID`, any case of `by`) | `Superseded D by <id>` |
| first word `superseded`, naming no `by <id>` | **stop** |
| first word `moved`, naming exactly one distinct id | `Superseded D by <that id, as written>`, **listed** |
| first word `moved`, naming no id | `Dropped D`, **listed** |
| first word `moved`, naming two distinct ids or more | **stop** |
| first word `obe` or `dropped`, or a value beginning `Won't fix` or `Wont fix` (any case) | `Dropped D` |
| anything else (`Open`, `Partly`, `Live`, `In`, prose, a bold lead, no Status) | **stop** |

The ids a `Moved` value names are found by `LOG_ID`, longest match first, so `acme#TD-5` is one id and does not
also count as `TD-5`; an id named twice counts once.

Then the text: **when the head reads and the new form takes only its head**, the old head is kept aside and the head
rewritten to the new form, so the tail is lifted dated `D` and each segment dated as *Lifting* says; when the old
head differs from the new Status, it is written as one `was: <old head>` line dated `D`, inserted after the lifted lines (by date, after any line of an equal date). **Otherwise** (`Resolved 2026-10-12.`,
`**Resolved**.`, `Moved to TD-5 (PR #2)`, `Superseded 2026-01-10 BY TD-302.`), nothing is lifted: the whole
value is one `was: <value>` line dated `D`, and the Status set to its new form.

So `Done 2026-10-03: shipped — was: Designed 2026-09-30` becomes `Resolved 2026-10-03`, with the Log lines, in
order, `2026-09-30: was: Designed 2026-09-30`, `2026-10-03: shipped` and `2026-10-03: was: Done 2026-10-03`; 
`Resolved 2026-10-12.` becomes `Resolved 2026-10-12` with `2026-10-12: was: Resolved 2026-10-12.`; and
`Superseded 2026-01-10 BY TD-302.` becomes `Superseded 2026-01-10 by TD-302` with `2026-01-10: was: Superseded
2026-01-10 BY TD-302.`.

**3. `Added`.** A value `YYYY-MM-DD <comment>` becomes the bare date, and the comment one plain Log line, verbatim,
dated by that date and placed **before** any line of its date (it is the entry's first event; a new insert mode
beside `_log_insert`'s after-equal one). Its surrounding parentheses, if it is wholly wrapped in one pair, are
dropped. A comment that would begin with a reserved prefix is written `note: <comment>`, as for a lifted Status
note. **Never a `filed by` line** (a departure from §2.2, which wrote one "only when the comment parses into that
shape": `filed by` needs a `who` and a session token, which no old comment carries in a form a parser can trust; a
plain line loses nothing). A value that does not begin with a date is left alone and **listed**.

**4. `Location`.** A header `Location` is removed from the header and written as a body section, `**Location:**
<value>`, after the `**Why:**` section, or first in the body when there is none. When the body already has a
`**Location:**` section, **stop** (`Location in the header and the body`).

**5. What it leaves.** A `Waits` line, a `Taken by`, an old-form `decision (who) — text`, every other field and
section, and every Log line already there are left as they are: turning a wait into a gate or an old decision into
an Ask was the v2.4 remodel's (§7.3). A Log is made at the end of the body when the entry has none and a line is
written; a Log that is not last is a stop (`log-not-last`), as `note` refuses one.

The result is in canonical form (D4).

### D3. `ledger.py migrate`

`migrate [TD-n …] --release <x.y> [--closed-dates FILE] [--stage-kind WORD=KIND …] [--plan | --dry-run] [--today D]
[--json]` runs `migrate_entry()` over each entry named, else every entry, open and archived, of a v2 directory, the
archived ones with `archived=True`. A v1 file is unusable, exit 2 (*split first*), as for every write.

- `--closed-dates FILE`: a JSON object from `TD-n` to `YYYY-MM-DD`, the caller's archiving dates (agent-cadence's
  wrapper reads them from git: the commit that moved the file into `archive/`). The writer reads no git.
- `--stage-kind WORD=KIND` (repeat): the `kinds` map (named apart from `new`'s and `set`'s `--kind`, which writes
  the field); a word outside *Retired words*' open Status words is a usage error, exit 2.
- **Any stop anywhere stops the run**, a refused entry's included: exit 1, nothing written, each entry's stops
  printed. Otherwise every changed file is written as one write (all or none; exit 4 on a failed write, every file
  restored).
- `--plan` writes nothing and prints one JSON object: the writers' plan (each path and its new text) and
  `entries`, an object from each entry id `migrate_entry()` changed, listed or stopped to its `{changes, listed,
  stops}`. With a stop, the plan is empty and the exit is 1, as for the write; otherwise 0. `--dry-run` is the same
  printed as text, entry by entry (the listing a remodel PR carries; the name target design §7.3 and S7 use), or
  `nothing to migrate`. S7's v3.0 precondition, *`migrate --dry-run` gives no diff*, is read off `--plan`: exit 0
  with `entries` empty.
- A write prints the paths it changed, or with `--json` the writers' one object with `entries` added.
- It names `subject`, `migrate_subject(<--release>, <the count of entries it changed>)`, for the caller's one commit: the only ledger
  write whose `subject` is not null (the tripwire knows the migrate commit by it). Nothing changed: exit 0, `subject`
  null.
- Unlike the other writes, it is not refused for a `check()` error the ledger before it did not have: it writes the
  ledger `check()` will grade, and the caller runs `--check` on the result.

### D4. The canonical form, `new` and `set`

- `canonical()`'s header order loses `Waits` and `Location`: `Priority, Type, Added, Owner, Kind, Status, Taken by,
  Id take, Blocked by, Part of`. A `Waits` or a header `Location` still in a file is placed with the other fields
  the order does not name, in the file's order. `fmt` over an old ledger may move such a line within the header;
  nothing is dropped.
- `Location` stays one of the format's own fields in v2.x (so a `Fields:` ledger does not call it undeclared), and
  a header `Location` joins *Retired words*, graded as `Waits` is (TD-046): with the ledger before an edit, an error
  on an entry whose header `Location` line the edit added or changed, naming the `**Location:**` body section; ℹ
  `retired` where the line is as it was, and with no ledger before the edit.
- `new --location` writes the `**Location:**` body section, after `**Why:**` and before every other section:
  `plan_new` moves it from the fields into the sections it passes `entry_text()`, whose signature is unchanged. `new
  --field Location=…` is a usage error naming `--location`, and so is `--location` with a `Location` among the
  sections `new` is given.
- `set --location <value>` and `set --field Location=<value>` are usage errors naming `edit TD-n --section
  Location`, which already writes a body section; an empty value still removes a header `Location`, as `set`
  removes any field.
- A body `**Location:**` was already a section, never a field (SPEC *Ledger entries and their edits*), so no reader
  changes.

### D5. The grammar appendix

A new subsection, *The entry header and the Log (v2.7)*: productions for the header block's field line, the four
Status forms, an `Added` value, and each fixed Log line shape SPEC *The Log* lists (`filed by` with its optional
`while`, `gate added`, the `gate lifted` shapes with their tails, `gate lift skipped`, `kept waiting`, `gate
reassigned`, `archived`, `reopened`, `was`). Each production gets an accepting and a refusing fixture in
`fixtures/grammar/`, as §7.4 *Grammar* requires.

## The `SPEC.md` text

Each block is the text the build adds or replaces, with the section it lands in.

**T1. *The ledger*, the paragraph listing the format's own fields** (SPEC lines 22–24): unchanged except that
`Location` is followed by "(a body section from v2.7: *Retired words*)".

**T2. *The ledger*, *Retired words*** (SPEC lines 79–88). The lead sentence, "Where v2.x still reads one, `check()`
names it *retired* (ℹ, `retired`) with what replaces it, rather than unknown:", gains "— except a Status word, which
from v2.7 is an error (*The closed Status set*)". The field bullet gains `Location`, and the Status bullet is
replaced:

> - the fields `Waits` (a gate: `until` or `event`), `Taken by` (`Id take`), `Resolved` as a header field (the
>   `**Resolved:**` body line of an archived entry) and, from v2.7, `Location` as a header field (the
>   `**Location:**` body section);
> - …
> - the Status words `Designed`, `Built`, `Partly`, `Live` and `In` (`Open`, the stage in `Kind`), and `Done`,
>   `Moved` and `OBE` (`Resolved`, `Superseded` or `Dropped`). From v2.7 a Status outside the closed set is an
>   error (*The closed Status set*), whose text still names a retired word with what replaces it; `migrate` maps
>   each (*Migrating to v2.7*).

and after *A new `Waits` line is an error* (SPEC lines 90–95), a sentence: "A header `Location` line is graded the
same way from v2.7, naming the `**Location:**` body section."

**T3. *Ledger entries and their edits*, a new paragraph after *The archived entry*:**

> **The closed Status set** (v2.7). An entry's Status is `Open` in the ledger, and in the archive `Resolved
> YYYY-MM-DD`, `Superseded YYYY-MM-DD by <id>` (`TD-n` or `<repo>#TD-n`) or `Dropped YYYY-MM-DD`, exactly as the
> writers write them: nothing before or after, one space between parts, a real date. Any other value, or none, is
> an error on every entry, open or archived, of a ledger that declares major 2 (`status`, `status_problem()`), never
> standing, with or without `old`; on a v1 ledger it is ℹ. Its text names the first word and the form the entry's
> place takes, never the whole value, and ends *migrate maps it*. It replaces v2.4's ℹ `retired` on an open
> entry's Status word. What a reader reads of an archived blocker's Status (*Superseded and dropped*) is unchanged,
> so another repo that has not migrated still reads as before.

**T4. *Ledger entries and their edits*, the canonical form's header order** (SPEC lines 483–487), replaced:

> - the header block in this order: `Priority, Type, Added, Owner, Kind, Status, Taken by, Id take, Blocked by,
>   Part of`, each spelled so. Then any other field, spelled as the file spells it, in the file's order — a
>   `Waits` or a header `Location` among them (v2.7). A place in the order is a rendering rule, not a declaration:
>   `Owner`, `Kind` and `Taken by` are not the format's own fields. A header `Resolved` is not in the order and is
>   kept where the other fields put it;

**T5. A new section, *Migrating to v2.7*, after *Ledger entries and their edits*:** D2's text, as written above
from "`migrate_entry(text, *, archived, today, closed_date=None, kinds=None) -> dict`" through "The result is in
canonical form", in present tense, with its table and its two examples.

**T6. *The ledger writer*:** a new bullet after `fmt`, D3's text as written above; the `new` bullet's
"`--location`" becomes "`--location` (the `**Location:**` body section, v2.7)", and the `set` bullet gains "(not
`--location`, from v2.7: `edit --section Location`)"; and the sentence "a ledger edit has no commit subject of its
own, so the caller names its commit" (SPEC *The ledger writer*, the output paragraph) gains "— except `migrate`'s,
which names `migrate_subject()`", as does `ledger.py`'s module docstring.

**T7. *Versions*, after v2.7's two paragraphs:**

> **v2.7 closes the Status set and ships `migrate`** (*The closed Status set*, *Migrating to v2.7*): a Status
> outside `Open`, `Resolved D`, `Superseded D by <id>` and `Dropped D`, or in the wrong place, is an error on every
> entry of a v2 ledger, where v2.4 to v2.6 noted a retired open word ℹ and read the rest; `migrate_entry()` and
> `ledger.py migrate` map the old forms. The header order loses `Waits` and `Location`, a header `Location` is
> retired, and `new` writes `Location` in the body. A v2.6 reader reads every entry v2.7 writes (the four forms
> were already its own; a body `**Location:**` was already a section). A repo takes v2.7 in one PR that vendors it
> and runs `migrate`. `migrate` stays through v2.x and goes in v3.0, whose precondition is that `migrate --dry-run`
> changes nothing in every repo.

**T8. *Appendix: grammar*:** the opening line's list gains "v2.7: the entry header and the Log", and D5's
subsection.

## Fixtures

New cases, each an input and its expected JSON, invented (AGENTS.md's public-repo rule):

- **`fixtures/migrate/`** (B1), each case `{archived, today, closed_date, kinds}` in, `{text, changes, listed,
  stops}` out:
  - each row of D2's archived table, one case each (`Done`, `Built`, `Designed`, `Superseded … by`, `Superseded …
    BY` in upper case, `Superseded` with no `by`, `Moved` with one id, with `acme#TD-5` (one id), with none, with
    two, `OBE`, `Won't fix`, `Dropped` with a tail, archived `Open` stopping, prose stopping);
  - D2's two examples, the Log's order included; `**Resolved**.` (a head that does not read);
  - an archived entry with no date anywhere and no `closed_date` stopping; the same with `closed_date` given;
  - an open entry, one case per branch: `Open` unchanged; `Open 2026-10-01`; `Open 2026-10-01: noted`; `Open
    2026-10-01: note — was: Designed 2026-09-30`; each stage word with and without a `kinds` key; `In progress`
    (a stage word whose head does not read); a stage word replacing an existing `Kind`; a prose Status; a bold lead;
    `Open, held`; `Resolved 2026-10-03: x` on an open entry (listed);
  - `Added` with a comment, with a parenthesised comment, with a comment beginning `gate added:`, with a Log line of
    the same date (the comment goes first), with prose and no date;
  - `Location` in the header, with a Why, with no Why; in the header and the body (a stop);
  - a text `canonical()` refuses (a stop);
  - **twice gives no diff** (§7.4): every case's output run again is unchanged;
  - **unknown text survives** (§7.4): an entry with an unknown header field, an unknown gate, an unknown body
    section and an unknown Log prefix, whose content comes out unchanged;
  - an entry with a `Waits` line, a `Taken by` and an old-form decision, each left as written;
  - a Log not last (a stop).
- **`fixtures/ledger_writer/migrate_*`** (B2): a ledger whose one archived entry stops, so nothing is written and
  exit 1 (§7.4: *an unmapped Status word stops it with a list and writes nothing*); `--dry-run`; `--closed-dates`;
  `--stage-kind`, and a word outside the stage words (exit 2); a v1 file (exit 2); a ledger already migrated (exit
  0, `subject` null); the subject's count.
- **`fixtures/ledger_edit/check/status_*`** (B3): each of the four forms passing in its place; each in the wrong
  place; `Open 2026-10-01`; `Resolved 2026-10-03.`; lower case; no Status; a retired word, whose text names its
  replacement; standing with `old` given (still an error); a `note` on an entry whose Status is outside the set,
  which the writer still writes (the flag's text unchanged); a v1 ledger (ℹ). And a header `Location` added by an
  edit (an error) and standing (ℹ).
- **`fixtures/edit/`** (B3): `canonical()` placing a `Waits` and a header `Location` after `Part of`, in file order;
  `new --location` writing the body section; `set --location` and `new --field Location=…` refused.
- **Existing fixtures B3 regenerates.** `fixtures/run.py` records the whole of `check()` for each
  `fixtures/ledger/*` case, so every entry there with no Status or one outside the set gains a `status` record (an
  error where the ledger declares major 2, ℹ where not), and the ℹ `retired` Status records go. A fact-check found
  these among them: `ledger/{gates,belowheader,crossversion,events,supersede,unknownstatus,escaped}.md` and their
  archives, and `ledger/parts.archive.md`. And `ledger_edit`'s `check` cases (`fixtures/ledger_edit/cases.json`)
  filter `check()`'s output to the kinds at `run.py:596-601`; B3 adds `status` to that filter for every `check`
  case, so the nine existing ones gain records where their inputs, `ledger_edit/check/*.md`, hold a Status outside
  the set (`check/after.archive.md`'s `Resolved 2026-01-20: done` among them), and the new `status_*` cases use it.
  Their inputs carry old forms on purpose, to prove the readers still read them, so **the inputs stay** and only the
  expected JSON changes. B3 regenerates from a real run and lists, in its PR, each file that differs and why its
  change is only those records; a case whose own assertion breaks is changed and said. `tests/test_ledgerboard.py`'s `check()` calls on ledgers whose entries have no Status
  (about 30) are updated in B3, which lists each: a Status added, or the new error asserted.
- **`fixtures/grammar/`** (B4): an accepting and a refusing case per D5 production.

## The builds (filed on Paul's go after the rounds)

In series: each edits `SPEC.md`, the module and `fixtures/run.py`. Each lands its `SPEC.md` text with its code.

- **B1.** `migrate_entry()` (D2), with T5 and `fixtures/migrate/`.
- **B2.** `ledger.py migrate` (D3), with T6's `migrate` parts and `fixtures/ledger_writer/migrate_*`.
- **B3.** The closed Status set in `check()` (D1), the header order, the retired header `Location`, `new
  --location` and `set --location` (D4), with T1–T4, the rest of T6, T7 and its fixtures; **and this repo's own
  ledger migrated in the same PR**, by B2's command, its `--dry-run` listing in the PR body: the archive holds
  Status tails (TD-053's `Resolved 2026-11-06: designed and built …`) and heads that do not read (TD-001's
  `Resolved 2026-10-12.`, TD-002's `Resolved 2026-10-14.`), 11 archived entries hold `Added` comments, and 54 entries (53 archived, one open) a header `Location`.
- **B4.** The grammar appendix (D5, T8) and `fixtures/grammar/`.

Then the release (Paul's), and the hand-off: once v2.7 is tagged, an entry on agent-cadence's ledger, then
ShiftLead's, each to vendor v2.7 and run `migrate` in the same PR (§7.2 step 6), filed through each repo's question
seat (`ao td add --repo`):
- **agent-cadence:** its `ledger.py` wrapper passes `--closed-dates` from git and `--stage-kind` from cadence.md's
  `Kind` vocabulary (`designed=build`, `built=live-check`), and commits under the printed subject;
- **ShiftLead:** the same through its vendored copy, and `Waits = until | event` leaves its `Fields:` line in the
  same PR.
The roster repos follow only after both have run on it (§7.3 *Order*).

## Not in this release

- Renaming `**Resolved:**` to a status-neutral lead (§2.2: v3.0 material).
- Removing the old-form readings (`Waits`, `Taken by`, `decision (who) — text`, a header `Resolved` or
  `Location`) and `migrate` itself: v3.0 (S7).

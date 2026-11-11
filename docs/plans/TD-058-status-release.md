# TD-058: v2.7, the Status release, and `migrate`

**Status:** Draft 7, 2026-11-11 (session lb-designer). The scope (S1–S8 below) is Paul's, agreed 2026-11-11 (his
`Go` on the board's decide item, which lifted TD-058's `decision (paul)`). Class: **wide** (a vendored, published
format: the closed Status set, the canonical entry form and `migrate`, which both consumers vendor and run; cap 6
rounds, cadence.md §4.8). Rounds: six ran and ended at the cap (build-changing per design review: 9, 6, 2, 1 (F120
rejected), 2, 2; the fact-checks' apart), then a closing fact-check (F166–F173); Paul answered `One more round`
(2026-11-11), and round 7's design review read the whole plan and every fix through F173 and raised 2
build-changing findings (F174–F182, fixed and read by its closing fact-check only). Draft 7 holds every finding's
fix. Target design §7.1–§7.3's roster path was amended in PR #200 on Paul's note of 2026-11-11 (the record: [docs/reviews/TD-058.md](../reviews/TD-058.md)). The
builds are filed only on Paul's go after the rounds.

**Entry:** [TD-058](../ledger/TD-058.md). **Source:** [target design](target-design.md) §2.1, §2.2, §7.1 (the v2.7
row and its amendments), §7.2 step 6, §7.3, §7.4.

## The problem

The target design ends the v2 migration with a release that closes the Status vocabulary, moves the old Status
notes and `Added` comments into the Log, and ships `migrate`, the tool that maps a ledger's old forms to the new
ones. The design first called that release v2.5, then v2.6, now v2.7 (§7.1's amendments). `SPEC.md` already names
v2.7's `migrate` (in *Retired words*, the Status grammar under *The Log* and the tripwire's exemption, among
others), and v2.7 work has landed (TD-046, TD-056). But the newest tag is v2.6, and `migrate` is not built:
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
  forms; v3.0's precondition is that `migrate --plan` shows no entry with `changes` in every roster repo
  (exit 0; an entry only listed does not block), and that no entry there, open or archived, holds an old form
  `migrate` leaves (S6, D2 part 5: `Waits`, `Taken by`, `decision (who) — text`, a header `Resolved`), read off the
  files, since `check()`'s retired records read open entries only. An open entry's are each repo's to rewrite
  through the writers (`set`, `edit`), as the v2.4 remodel's were; an archived entry's have no writer route (the
  writers refuse an archived entry, and `reopen` then `archive` re-dates it), so v3.0's design gives them one before
  that release, and this release does not. This PR adds it to
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
  one entry's Status, or None. It reads the Status `entries()` reads: a Status line below the header block
  is no Status there (`entries()` falls back below the header only for Priority, Type, Blocked by and Part of), so
  it is `it has none`, as `pickable()` and `migrate_entry()` read it. `migrate` then writes `Open` in the header
  and leaves the stray line where it is, **listed** (`Status line below the header: left`). It is listed whenever
  such a line exists, header Status or not; a listing never makes an entry changed. `check()` runs it over every entry of the ledger (`archived=False`) and of the archive
  (`archived=True`), and appends its records on both of `check()`'s exits: before its early return when `old` is
  None, and **after** the loop that grades records standing under `old` (where `archive-open-parts` is appended), so
  no `status` record is ever made standing or ℹ by it. Their order in the list: after every other record,
  `_left_with_open_parts()`'s included, the ledger's entries first, then the archive's, each in file order.
- **Its flag:** kind `status`, field `status`, an **error on every entry, never standing**, whether or not `check()`
  is given `old`, on a ledger that declares major 2 (*Versions*). On a v1 ledger it is ℹ: `migrate` takes a v2
  directory, so a v1 ledger splits first (*The ledger as a directory*).
- **Its text names the form, never the whole value**, so an edit that changes only a tail (a `note` lifting it)
  leaves the flag's text as it was, and the writer, which refuses a write only for an error the ledger before it did
  not have, still writes it. The text, by place:
  - open: `⚠ TD-n: an open entry's Status is Open alone — <detail> — run migrate, which maps it, lists it, or
    names what a person decides`;
  - archived: `⚠ TD-n: an archived entry's Status is Resolved D, Superseded D by <id> or Dropped D — <detail> — run
    migrate, which maps it, lists it, or names what a person decides`;
  - `<detail>`, the first that applies: `it has none` (no or an empty Status); `this one is <Word>, not in that
    form` (the word, compared in lower case as `first_word()` compares it and with any `*`s stripped, as D2 part 1's branch 5
    compares it, is one of the place's own words, `open`
    in the ledger and `resolved`, `superseded` or `dropped` in the archive, but the value is not its form: `Open
    2026-10-01`, `Resolved 2026-10-03.`, a bare `Resolved`, `Superseded 2026-10-03` with no `by`, `resolved
    2026-10-03` in lower case, an unreal date); `this one is <Word> (retired: <what replaces it>)` (a word *Retired
    words* lists); on an open entry, `this one is <Word> (archived: archive it, or Open)` for `Resolved`,
    `Superseded` and `Dropped` (`Resolved 2026-10-03` in the ledger; `migrate` stops on them as on `Done`);
    `this one is <Word>` (any other).
  - `<Word>` is the value's first word as written, `_status_word()`'s. *What replaces it*, by place: on an open
    entry `Open, the stage in Kind` for the five open words (`Kind build` and `Kind live-check` are consumer
    vocabulary, S3) and `archive it, or Open` for `Done`, `Moved` and `OBE` (`migrate` stops on them, D2 part 1's branch 5:
    finished work the ledger forgot to archive is archived, not reopened); on an archived entry `Resolved` for `done`, `built` and
    `designed`, `Superseded or Dropped` for `moved`, `Dropped` for `obe`, and `Resolved, Superseded or Dropped` for
    `partly`, `live` and `in`. `status_problem()` holds these two maps itself (B1); B3 removes the ℹ record that
    is `RETIRED_STATUS`'s one reader, and `RETIRED_STATUS` with it.
- **The id is in the text**, and the writer matches a record by it, so `renumber` of an entry whose Status is
  outside the set meets a `status` error under its new id that the ledger before did not have, and is refused:
  *migrate it first*. A fixture shows it.
- **It replaces v2.4's ℹ `retired` on an open entry's Status word** (the record made at `__init__.py:626-629`, removed): `pickable()`'s flags no longer carry that
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

`migrate_entry(text, *, archived, today, closed_date=None, kinds=None, decided=None) -> dict` takes one entry's
text (as `canonical()` takes it), whether the entry is in the archive, the UTC day (`today`, as `edit_entry()`
takes it), the entry's archiving date if the caller has one (`closed_date`), the caller's map from an open stage
word to a `Kind` value (`kinds`, its keys compared in lower case), and the caller's decision for a Status the rules below
stop on (`decided`: `resolved`, `dropped` or `superseded <id>` for an archived entry, `open` for an open one). It reads nothing else and returns
`{text, changes, listed, stops}`.

- **Every difference is a change.** Each text difference `migrate` makes has at least one `changes` word, except the
  canonical reorder of an entry it changed (which follows from the change), so an entry with `changes` empty is one
  it left alone.
- **Unchanged is byte for byte.** An entry that needs no change (its `changes` empty) is returned as given, even
  where `canonical()` would reorder it: a reorder is `fmt`'s, never a migrate change. Neither a `canonical()` refusal
  nor a Log stop meets an entry that needs no change (*canonical() refusal*, below); a stale or malformed
  `decided` or `kinds` still stops one. A Log not last, or two Logs, stops only an
  entry with `changes` (*What it leaves*): one left alone is returned as given, as `check()` and the writers
  already meet it. A changed entry is returned
  in canonical form (D4). With a stop, the input is returned as given.
- **The post-condition**, on an entry with `changes` (an unchanged one is returned as given and not tested): the
  migrated Status passes `status_problem()` (D1) for the entry's place, and the migrated entry's `log_problems()`
  holds no problem the input's does not (each compared as its kind and sentence, so a malformed line already in the
  input, which `migrate` leaves, is not one, and a Log not last, or two Logs, has stopped already, *What it leaves*); any problem
  is a stop (`migrated Status <value> still outside the set`, or `migrated Log: <problem>`). So `migrate` never
  writes a Status or a Log line `check()` rejects that was not there before it.
- **`canonical()` refusal.** Text `canonical()` refuses (a duplicate field, a non-field line in the header block, a
  Priority, Type, Blocked by or Part of line below the header block; text that is not one entry is always the stop
  `refused: <why>`)
  is never an exception. `migrate_entry()` reads such an entry's fields as `entries()` does, leniently, and applies
  the rules to that reading: when none would change it, it is returned as given and **listed** (`canonical()
  refuses it: left alone`), since a fault already there never blocks an unrelated write; when one would, it is a
  stop (`refused: <why>`), since it cannot write a changed entry in canonical form. The stops are collected first,
  and a stop always wins: *left alone* is only for an entry no rule would change or stop.
- `migrate_entry()` run on its own output, without `decided`, changes nothing.

**Terms.**
- *A real date* is a `YYYY-MM-DD` that is a calendar day (`date.fromisoformat` accepts it); a date that is not one
  (`2026-02-30`) is no date, and every rule below that looks for a date passes over it to its next source, except
  *Lifting*, which cannot (below).
- *The head reads* when `status_notes_to_log()`'s head grammar (*The Log*, `STATUS_HEAD_RE`) matches the value and
  any date it holds is a real date: then *the head* is the text it matched (word, date, `by <id>`), *the tail* what
  follows up to the first ` — was: `, and *the segments* each ` — was: ` part.
- *The first part* is the value before its first ` — was: `. Every search below for an id or a date in the text
  (not the head) is a search of the first part only.
- *An id* is `LOG_ID` (`TD-n` or `<repo>#TD-n`) standing alone, a new pattern bounded on both sides: the character
  before it is none of a letter, a digit, `_`, `-`, `/` or `#`; the character after it is none of those, nor a `.`
  followed by a letter. Ids are matched longest first, so
  `acme#TD-5` is one id and does not also count as `TD-5`; an id named twice counts once.
- *The word* is the value's first word as written, `_status_word()`'s (`Designed`; `Resolved` from `**Resolved**`, `Resolved**` from `**Resolved**.`); rules compare
  it as `first_word()` does, in lower case and stripped.
- *Lifting* is `status_notes_to_log()`'s, with its own dating: the tail as one line dated by the head's date, else
  the `**Resolved:**` line's, else `Added`'s; each segment as a `was:` line dated by its own head's date, else the
  same fallbacks; each in among the Log by date, after any line of an equal date (`_log_insert()`'s rule: before the
  first line dated later, which in a Log not in date order need not be where its date would sort). If any line it would lift has no
  date, it lifts nothing from the whole value, dated segments included; the value is then treated as **a head that
  does not read**. `status_notes_to_log()` does not test a date's reality and does not pass over one, and it stays
  as it is: each line takes its own head's date when its head has one, real or not, else the first fallback the
  entry has, real or not. The dates the lift uses are the lines' dates as D2 gives them: on an open entry, the
  tail the head's date else that fallback, and each segment its own head's date else that fallback; on an
  archived entry, which lifts only when its new form takes only its head (below), so `D` is then the head's own
  date, the tail `D` and each segment its own head's date else that fallback. So `migrate` lifts only when **every date the lift would use is a real
  date**: a segment's own head date, and the one fallback reached where a line has no head date of its own (an
  unreal `**Resolved:**` date stops the lift even where `Added` is real, since the lift would use the
  `**Resolved:**` one; on an archived entry, whose tail takes the head's date, it does so only when an undated
  segment reaches it); otherwise it lifts nothing and the
  value is treated as a head that does not read. This is the one place an unreal date is not passed over (*A real
  date*): every date `migrate` itself picks, outside the lift, passes over an unreal one.
- *Its new form takes only its head* when the date and any `by <id>` the new Status keeps come from the head (its
  word is mapped). A value whose new form takes anything from beyond its head (an id in the tail, `BY` in upper case,
  which the head grammar does not read, a date found only in the text) is treated as **a head that does not read**.
- *No duplicates:* a Log line `migrate` would write (lifted, `was:`, an `Added` comment, a `Kind` line) whose date
  and words, after the `note:` escape, equal a line already in the Log is not written again.

D2's rules are in five parts, numbered in bold; part 1's branches are numbered within it.

**1. The Status, an open entry** (`archived=False`), the first branch that applies:

1. The value is exactly `Open` → unchanged.
2. No Status, or an empty one → the Status is set to `Open` (`changes`: `Status (none) → Open`), no Log line;
   **listed**.
3. The word is a stage word (`designed`, `built`, `partly`, `live`, `in`) → when the head reads, the tail and
   segments are lifted, then the head is written as one `was: <head>` line; when it does not (`In progress`,
   `Partly done`), the whole value is one `was: <value>` line, nothing lifted. The `was:` line is dated by the
   head's date; when the head does not read, the first real date in the first part, **listed** (`date <D> read from
   the Status's text`); then the `**Resolved:**` line's, else `Added`'s, else `today`. (A head that reads with no
   date takes the fallbacks, as its lifted tail does, so one entry never gets two dates for one Status.) The Status is set to `Open`. When the
   word is a key of `kinds`, `Kind` is set to its value; when `Kind` held another value, compared whole as written,
   a Log line `Kind <old> → <new> (migrate)` is written, dated `today`, inserted by date after any line of an
   equal date (so after a `was:` line of the same day), and when it held the same value nothing about
   `Kind` changes. With no key for it, `Kind` is left as it is and the entry is **listed**.
4. The head reads and its word is `Open` (`Open 2026-10-01: noted`, `Open 2026-10-01 — was: Designed 2026-09-30`,
   `Open.`) → the tail and segments are lifted and the Status set to `Open`. The head is also written as one `was:
   <head>` line, dated as in branch 3, **unless** the head is `Open` or `Open D` and a tail was lifted (that line carries the
   date). So a head's `by <id>`, a date with only segments, and `Open.` are kept.
5. The word, or the word with its `*`s stripped (`**Resolved**.` gives `resolved`), is an archived one
   (`resolved`, `superseded`, `dropped`, `done`, `moved`, `obe`) → **stop** (`<Word>` as written, `Status
   <Word> on an open entry`): the entry may be finished work the ledger forgot to archive, and setting `Open` would
   offer it as work. `decided` answers it: `open` sets `Open`, the whole value one `was: <value>` line dated as in branch 3;
   to archive it, the person runs `archive` instead once the rest has migrated.
6. Anything else (prose, a bold lead, `Open, held`) → the whole value is one `was: <value>` line, dated as in branch 3,
   nothing lifted, and the Status set to `Open`; **listed**.

**2. The Status, an archived entry** (`archived=True`). An entry whose Status already passes `status_problem()` is
unchanged here. Otherwise, first the closing date `D`: the head's date, else the `**Resolved:**` line's date (or an
older `Resolved` header field's), else `closed_date`, else the first real date in the first part (each source
passed over when its date is not real, `closed_date` among them), which is then
**listed** (`date … read from the Status's text`); with none, **stop**. Then the word (with no date, its stop, if any, is still collected: every stop that applies is
returned, the date's first, then the word's):

| The Status | Becomes |
|---|---|
| word `resolved`, `done`, `built` or `designed` | `Resolved D` |
| word `superseded`, its first part naming `by <id>` (`by` in any case) | `Superseded D by <the first such id>`; **stop** when that id is the entry's own (`Superseded: by its own id`) |
| word `superseded`, naming no `by <id>` | **stop** |
| word `moved`, its first part naming exactly one id other than the entry's own | `Superseded D by <that id, as written>`, **listed** |
| word `moved`, naming no id, or only the entry's own | `Dropped D`, **listed** |
| word `moved`, naming two ids or more | **stop** |
| word `obe` or `dropped`, or a value beginning `Won't fix` or `Wont fix` (any case) | `Dropped D` |
| anything else (`Open`, `Partly`, `Live`, `In`, prose, a bold lead whose word is none of the above such as `**Resolved**.` or `**Note** …`, no Status) | **stop** |

**A stop on the word is a decision for a person**, given back as `decided`: `resolved`, `dropped` or `superseded
<id>` sets that form, dated `D`, in place of the table's row, and the whole old value is kept as one `was: <value>`
line (none when the old value is empty or absent). `decided` does not answer a missing date: that is `closed_date`'s. A `decided` given for an entry that does not
stop on its word, or of the other place's shapes, is a stop (`decided: nothing to answer`), so a stale decision
never passes silently; one outside the four shapes, or a `kinds` key or value that is not one line of text (empty, or holding a
newline), is the stop `refused: <why>`, never an exception (the command checks both shapes first, exit 2, D3). So a second run with the same `decided` stops: a
caller drops a decision once it is written (a second `migrate --as` exits 1, by design).

Then the text: **when the head reads and the new form takes only its head**, the old head is kept aside and the head
rewritten to the new form, so the tail is lifted dated `D` and each segment dated as *Lifting* says; when the old
head differs from the new Status, it is written as one `was: <old head>` line dated `D`, inserted after the lifted
lines (by date, after any line of an equal date). **Otherwise** (`Resolved 2026-10-12.`, `Moved to TD-5 (PR #2)`, `Superseded 2026-01-10 BY TD-302.`, a value `decided` answers), nothing is lifted: the whole value is
one `was: <value>` line dated `D`, and the Status set to its new form.

So `Done 2026-10-03: shipped — was: Designed 2026-09-30` becomes `Resolved 2026-10-03`, with the Log lines, in
order, `2026-09-30: was: Designed 2026-09-30`, `2026-10-03: shipped` and `2026-10-03: was: Done 2026-10-03`;
`Resolved 2026-10-12.` with no `**Resolved:**` line and no `closed_date` becomes `Resolved 2026-10-12` with
`2026-10-12: was: Resolved 2026-10-12.` and the listing `date 2026-10-12 read from the Status's
text` (given a `closed_date`, `D` is that day, by the order above, and nothing is listed; the old date stays in
the `was:` line); and
`Superseded 2026-01-10 BY TD-302.` becomes `Superseded 2026-01-10 by TD-302` with `2026-01-10: was: Superseded
2026-01-10 BY TD-302.`. A bold lead such as `**Resolved**.` has the word `Resolved**` (the stripping `first_word()`
does leaves `**` before a `.`), which is no word in the table: it stops, and `decided` answers it.

**3. `Added`.** A value that is a real date, whitespace, then a comment becomes the bare date, and the comment one
plain Log line, verbatim, dated by that date and placed before the first line dated on or after its date, scanning as `_log_insert()` does with
`>=` for its `>` (it is the entry's first event; an insert mode beside lifting's after-equal one). Its surrounding parentheses, if it is wholly wrapped in one pair (it begins with `(`, ends with `)`, and that
first `(` closes at that last `)`, counting nesting: `(a (b))` is wrapped, `(a) (b)` is not and is kept whole), are
dropped, and then its surrounding whitespace; a comment left empty (`()`) writes no line (`changes`: `Added comment
(empty) removed`). A comment that would begin with a reserved prefix (`filed by ` among them) is written `note: <comment>`, as
for a lifted Status note. **Never a `filed by` line** (a departure from §2.2, which wrote one "only when the comment
parses into that shape": `filed by` needs a `who` and a session token, which no old comment carries in a form a
parser can trust; a plain line loses nothing). A bare real date is unchanged and not listed. Any other value (no real date first, or a date with no whitespace
after it: `2026-01-01.`, `2026-01-01T10:00`) is left alone and **listed**. So `gate_age()`'s fallback for a gate with no `gate added`
line, the first Log line's date, moves earlier wherever a line `migrate` writes lands first in the Log, which in a
Log in date order is wherever it is dated strictly before the Log's first (this comment's, a lifted line, a `was:`
line), as `note`'s lift already does: an older age, and a true one, since each such line's date is an event of
the entry. Where the entry had no Log, `gate_age()` fell back to `Added`, and the Log `migrate` makes gives it
that Log's first line instead, earlier or later than `Added` (later is a younger age; a gate with its own `gate
added` line is unaffected). Fixtures show it for an `Added` comment, a lifted line and a Log `migrate` makes.

**4. `Location`.** A header `Location` is removed from the header and written as a body section, `**Location:**
<value>`, placed as `edit --section` places a section the body lacks (`edit_entry()`'s rule, one rule for every
writer of the section): after the first `**Why:**` section, else before the first `**Done when:**`, `**Related:**`
or Log, else at the end. An empty header `Location` is removed and nothing written, whether or not the body has a
`**Location:**` section. When a non-empty header `Location` meets a body `**Location:**` section, **stop**.

The rules apply in the order given, the Status (1 or 2), then `Added` (3), then `Location` (4), each to the
entry the one before it left.

**5. What it leaves.** A `Waits` line, a `Taken by`, an old-form `decision (who) — text`, every other field and
section, and every Log line already there are left as they are: turning a wait into a gate or an old decision into
an Ask was the v2.4 remodel's (§7.3). A Log is made at the end of the body when the entry has none and a line is
written; a Log that is not last, or two Logs (each `log_problems()`'s `log-not-last`), is a stop on an entry with
`changes`, as `note` refuses one; an entry with none is returned as given.

**The words it returns**, each a string, which the fixtures pin. `<Word>` is the word as written; `<id>` the entry's.
- `changes`: `Status <old value> → <new Status>` (`(none)` for no or an empty Status); `Kind <old, or none> → <new>`; `Added comment → Log`; `Added comment (empty) removed`;
  `Location → body`; `Location (empty) removed`.
- `listed`: `stage word <Word>: Kind not set`; `no Status: set to Open`; `Status <Word> set to Open`; `Moved: Superseded
  by <id>`; `Moved: Dropped`; `date <D> read from the Status's text`; `Added <value>: not a date`; `decided: <form>`;
  `canonical() refuses it: left alone`; `Status line below the header: left`.
- `stops`: `refused: <why>`; `Superseded: by its own id`; `decided: nothing to answer`; `no date for the Status`; `Superseded: no by <id>`; `Moved: <n> ids`; `Status <Word>:
  no archived form`; `Status <Word> on an open entry`; `Location in the header and the body`; `Log not last` (a Log not last, or two Logs); `migrated Status <value> still outside
  the set`; `migrated Log: <problem>`.

### D3. `ledger.py migrate`

`migrate [TD-n …] --release <x.y> [--closed-dates FILE] [--stage-kind WORD=KIND …] [--as TD-n=FORM …] [--plan |
--dry-run] [--ledger DIR] [--today D] [--json]` runs `migrate_entry()` over each entry named, else every entry, open
and archived, of a v2 directory, the archived ones with `archived=True`. It joins the writer's writes; it takes no
`--base` (it is not refused for new errors, below) and no `--resolved` (it reads no other repo): its parser is its
own, without the write commands' shared `_common` flags but `--ledger`, `--today` and `--json`, so either is a usage
error, exit 2. A v1 file is
unusable, exit 2 (*split first*), as for every write.

- `--release`: `<major>.<minor>`, each one to nine digits (`migrate_subject()`'s shape), checked by the command
  before it reads the ledger; any other shape is exit 2.
- `--closed-dates FILE`: a JSON object from `TD-n` to a real `YYYY-MM-DD`, the caller's archiving dates; a key or a
  value outside that shape is exit 2, and keys are matched by number, as `tid_of()` reads an id (`TD-58` and
  `TD-058` are one key; two keys for one number are exit 2), and a key naming no entry the run reads is ignored (a caller may pass the
  whole repo's dates). A `TD-n` named on the command line that the ledger and archive do not hold is exit 2. The writer reads no git.
- `--stage-kind WORD=KIND` (repeat): the `kinds` map (named apart from `new`'s and `set`'s `--kind`, which writes
  the field); a word outside *Retired words*' open Status words, one given twice (in any case), or a `KIND` that
  is empty or holds a newline, is exit 2. A `KIND` outside a `Fields:` ledger's
  declared `Kind` vocabulary is not refused: the caller's `--check` on the result names it, as for every write of
  this command (below).
- `--as TD-n=FORM` (repeat, its id matched by number as `--closed-dates`'s keys are): `decided` for that entry, `resolved`, `dropped`, `superseded <id>` or `open`; any other
  form, an id not among the entries the run reads, or one id given twice, is exit 2.
- `--plan` and `--dry-run` together are exit 2.
- **Any stop anywhere stops the run**, a refused entry's included: exit 1, nothing written. It prints one
  line per stopped entry, `TD-n: <stop>; <stop>` (its stops in order); with `--json` or `--plan`, the one object `{"plan": {}, "entries":
  …}` (every entry changed, listed or stopped), never the writers' `{"refused": …}`. Otherwise every changed file is written as one write (all or none; exit 4 on a failed write, every file
  restored).
- `--plan` writes nothing and prints one JSON object: the writers' plan (each path and its new text) and `entries`,
  an object from each entry id `migrate_entry()` changed, listed or stopped to its `{changes, listed, stops}`. With a
  stop, the plan is empty and the exit is 1, as for the write; otherwise 0. `--json` with `--dry-run` prints the
  `--plan` object. `--dry-run` is the same printed as text,
  entry by entry (the listing a remodel PR carries), or `nothing to migrate` when no entry has `changes` (its
  `listed` still printed). S7's v3.0 precondition is read off `--plan`: exit 0 and no entry with `changes`; an entry
  only listed is a person's to judge and does not block it.
- **Dependents it re-blocks.** Today `pickable()` reads an archived `OBE` or `Moved` blocker as resolved, so its
  open dependents are pickable; after `migrate` the same blocker is `Dropped` (the block stays) or `Superseded`
  (released only when its successor chain ends resolved). The reverse happens too: a prose Status that read as
  `unknown-status` and a `decided` `resolved` releases its dependents. `migrate_entry()` sees one entry and cannot
  tell, so the command compares, for each archived entry it changes, how `pickable()` reads it as a blocker before
  and after (`_archived_status()`'s reading), and lists each open entry of the ledger `Blocked by` one whose reading
  changes: `--plan` and `--json` carry `reblocked`, an object from each such open entry's id to `[{blocker,
  before, after}]`, and `--dry-run` prints it after the entries. It is a listing, never a stop: the person sees
  which work the closed set re-blocks or releases. Another repo that reads this archive through its resolver sees
  the same change once this one migrates; that is the consumer's to read off its own `pickable()`.
- A write prints the paths it changed, or with `--json` the writers' one object with `entries` added.
- It names `subject`, `migrate_subject(<--release>, <the count of entries it changed>)`, for the caller's one
  commit: the only ledger write whose `subject` is not null (the tripwire knows the migrate commit by it). Nothing
  changed: exit 0, `subject` null.
- Unlike the other writes, it is not refused for a `check()` error the ledger before it did not have: it writes the
  ledger `check()` will grade, and the caller runs `--check` on the result.

### D4. The canonical form, `new` and `set`

- `canonical()`'s header order loses `Waits` and `Location`: `Priority, Type, Added, Owner, Kind, Status, Taken by,
  Id take, Blocked by, Part of`. A `Waits` or a header `Location` still in a file is placed with the other fields
  the order does not name, in the file's order. `fmt` over an old ledger may move such a line within the header;
  nothing is dropped.
- `Location` stays one of the format's own fields in v2.x (so a `Fields:` ledger does not call it undeclared), and
  a header `Location` joins *Retired words*, graded by the same mechanism as `Waits` (TD-046): with the ledger
  before an edit, an error on an entry whose header `Location` line the edit added or changed; ℹ `retired` where
  the line is as it was, and with no ledger before the edit. The texts, literally: `RETIRED_FIELDS["location"]` is
  `the **Location:** body section — run migrate, which moves it`, so the ℹ reads `ℹ TD-n: the Location field is
  retired — write the **Location:** body section — run migrate, which moves it (SPEC *Retired words*)`; and the
  error, `LOCATION_WRITTEN` beside `WAITS_WRITTEN`, reads `⚠ TD-n: a new or changed Location line — the header
  field is retired; write the **Location:** body section, or run migrate, which moves it (SPEC *Retired
  words*)`.
- `new --location` writes the `**Location:**` body section, after `**Why:**` and before every other section, which
  is the place `edit --section`'s rule gives it (D2 part 4), since `plan_new` refuses a body whose first section is not
  its Why. `plan_new` moves it from the fields into the sections it passes `entry_text()`, whose signature is
  unchanged. `new --field Location=…` is a usage error naming `--location`, raised by the command's argument
  handling (`_build`), since `_fields_given()` merges the two flags into one pair `plan_new` cannot tell apart.
- `set --location <value>` and `set --field Location=<value>` are usage errors naming `edit TD-n --section
  Location`, which already writes a body section; an empty value still removes a header `Location`, as `set`
  removes any field.
- `reopen` of an archived entry that still has a header `Location` is refused, by the mechanism that refuses one
  with a `Waits` line today: `old` is the ledger's text, where the reopened entry's line is new. So is `renumber`
  of an open entry with a header `Location`, since the line is new under its new id. The error's text names the
  remedy, `migrate`, which moves the line (for `Waits` the remedy is a gate, `WAITS_WRITTEN`'s). Fixtures show
  both.

- A body `**Location:**` was already a section, never a field (SPEC *Ledger entries and their edits*), so no reader
  changes.

### D5. The grammar appendix

A new subsection, *The entry header and the Log (v2.7)*: productions for the header block's field line, the four
Status forms, an `Added` value, and each fixed Log line shape SPEC *The Log* lists (`filed by` with its optional
`while`, `gate added`, the `gate lifted` shapes with their tails, `gate lift skipped`, `kept waiting`, `gate
reassigned`, `archived`, `reopened`, `was`). Each production gets an accepting and a refusing fixture in
`fixtures/grammar/`, as §7.4 *Grammar* requires. `tests/test_grammar.py` matches each fixture against the
production's regular translation and requires its verdict to equal the module's, so a refusing fixture is one the
regular production itself refuses (a missing date, a wrong word, a missing `by <id>`). What no regular production
can refuse is written in prose under the block, as the appendix already leaves *a real day* to prose: a duplicate
field, a Priority, Type, Blocked by or Part of line below the header block, a Log line whose words begin a writer
prefix without its shape (`malformed`), and an unreal date; those have no grammar fixture (their cases are in
`fixtures/migrate/` and `ledger_edit/check/status_*`). Each fixture is judged in `run.py`'s `grammar_cases` by a start symbol each: a
Status by `status_problem()` on a minimal entry wrapping it (`## TD-1: x`, a blank line,
`**Status:** <value>`; `archived` per production: `Open` false, the three archived forms true), a Log line by `log_line()` (accepted when it returns a record whose kind is
not `malformed`; None refuses), a header block by `canonical()` reading it, wrapped as `## TD-1: x`, a blank line, the block (its refusing
fixture a non-field line; the order is a rendering rule, not a grammar one), and an `Added`
value by `migrate_entry()` on a minimal open entry (`Status: Open`, `archived=False`) carrying it (accepted when
it returns no `changes` and no `listed`).

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
>   `Moved` and `OBE` (`Resolved`, `Superseded` or `Dropped`; on an open entry, archive it or `Open`). From v2.7 a Status outside the closed set is an
>   error (*The closed Status set*), whose text still names a retired word with what replaces it; `migrate` maps
>   each (*Migrating to v2.7*).

and after *A new `Waits` line is an error* (SPEC lines 90–95), a sentence: "A header `Location` line is graded the
same way from v2.7, naming the `**Location:**` body section."

**T3. *Ledger entries and their edits*, a new paragraph after *The archived entry*:**

> **The closed Status set** (v2.7). An entry's Status is `Open` in the ledger, and in the archive `Resolved
> YYYY-MM-DD`, `Superseded YYYY-MM-DD by <id>` (`TD-n` or `<repo>#TD-n`) or `Dropped YYYY-MM-DD`, exactly as the
> writers write them: nothing before or after, one space between parts, a real date. Any other value, or none, is
> an error on every entry, open or archived, of a ledger that declares major 2 (`status`, `status_problem()`), never
> standing, with or without `old`; on a v1 ledger it is ℹ. Its text names the form the entry's place takes and
> the value's first word when it has one, with what replaces a retired or misplaced word, never the whole value, and ends *run migrate, which maps it, lists it,
> or names what a person decides*. It replaces v2.4's ℹ `retired` on an open
> entry's Status word. What a reader reads of an archived blocker's Status (*Superseded and dropped*) is unchanged,
> so another repo that has not migrated still reads as before.

**T4. *Ledger entries and their edits*, the canonical form's header order** (SPEC lines 483–487), replaced:

> - the header block in this order: `Priority, Type, Added, Owner, Kind, Status, Taken by, Id take, Blocked by,
>   Part of`, each spelled so. Then any other field, spelled as the file spells it, in the file's order — a
>   `Waits` or a header `Location` among them (v2.7). A place in the order is a rendering rule, not a declaration:
>   `Owner`, `Kind` and `Taken by` are not the format's own fields. A header `Resolved` is not in the order and is
>   kept where the other fields put it;

**T5. A new section, *Migrating to v2.7*, after *Ledger entries and their edits*:** D2's rules, terms and returned
words, with its table and its examples, in present tense, **without the plan's history or examples of consumer
vocabulary**: no "a departure from §2.2", no target design names or section references (§7.3, §7.4), no private helper names (`_log_insert`,
`_status_word`; SPEC names what they do), and no sample `kinds` values (*a caller's map from a stage word to a
`Kind` value*). It names `status_problem()` in one line, B1 landing it (*the problem of one entry's Status
against the four forms, or none*), so B1 ships no unspecified public function; B3's T3 says where `check()` runs
it.

**T6. *The ledger writer*:** a new bullet after `fmt`, D3's text on the same terms (no consumer's name, no git
remark: *the caller's archiving dates*); the `new` bullet's "`--location`" becomes "`--location` (the
`**Location:**` body section, v2.7)", and the `set` bullet gains "(not a non-empty `--location` or `--field Location=…`, from v2.7: `edit
--section Location`; an empty one still removes the header field)", and the `new` bullet "(not `--field
Location=…`, from v2.7: `--location`)"; and the sentence "a ledger edit has no commit subject of its own, so the caller names its commit"
(SPEC *The ledger writer*, the output paragraph) gains "— except `migrate`'s, which names `migrate_subject()`", as
does `ledger.py`'s module docstring.

**T7. *Versions*, after v2.7's two paragraphs:**

> **v2.7 closes the Status set and ships `migrate`** (*The closed Status set*, *Migrating to v2.7*): a Status
> outside `Open`, `Resolved D`, `Superseded D by <id>` and `Dropped D`, or in the wrong place, is an error on every
> entry of a v2 ledger, where v2.4 to v2.6 noted a retired open word ℹ and read the rest; `migrate_entry()` and
> `ledger.py migrate` map the old forms. The header order loses `Waits` and `Location`, a header `Location` is
> retired, and `new` writes `Location` in the body. A v2.6 reader reads every entry v2.7 writes (the four forms
> were already its own; a body `**Location:**` was already a section), though its `canonical()` would place a
> `Waits` or a header `Location` back in its own order, so a consumer vendors v2.7 before it formats a ledger v2.7 wrote. A repo takes v2.7 in one PR that vendors it
> and runs `migrate`. `migrate` stays through v2.x and goes in v3.0, whose precondition is that `migrate --plan`
> shows no entry with changes in every repo.

**T8. *Appendix: grammar*:** the opening line's list gains "v2.7: the entry header and the Log", and D5's
subsection.

## Fixtures

New cases, each an input and its expected JSON, invented (AGENTS.md's public-repo rule):

- **`fixtures/migrate/`** (B1), each case `{archived, today, closed_date, kinds, decided}` in, `{text, changes, listed,
  stops}` out, its `kinds` values invented and neutral (`stage-a`), never a consumer's vocabulary (here and in
  `migrate_*`):
  - each row of D2's archived table, one case each (`Done`, `Built`, `Designed`, `Superseded … by`, `Superseded …
    BY` in upper case, `Superseded` with no `by`, `Moved` with one id, with `acme#TD-5` (one id), with none, with
    two, `OBE`, `Won't fix`, `Dropped` with a tail, archived `Open` stopping, prose stopping);
  - D2's two examples, the Log's order included; `**Resolved**` (mapped, its whole value one `was:` line); `**Resolved**.` (a stop, then answered by `decided`);
  - an archived entry with no date anywhere and no `closed_date` stopping; the same with `closed_date` given;
  - an entry `canonical()` refuses that needs no change (listed, left alone) and one that needs one (a stop);
  - an open entry, one case per branch: `Open` unchanged; `Open 2026-10-01`; `Open 2026-10-01: noted`; `Open
    2026-10-01: note — was: Designed 2026-09-30`; each stage word with and without a `kinds` key; `In progress`
    (a stage word whose head does not read); a stage word replacing an existing `Kind`; a prose Status; a bold lead;
    `Open, held`;
  - `Added` with a comment, with a parenthesised comment, with a comment beginning `gate added:`, with a Log line of
    the same date (the comment goes first), with prose and no date;
  - `Location` in the header, with a Why, with two Why sections (after the first), with no Why but a Fix and a
    Done when (before the Done when), with none of them (at the end); in the header and the body (a stop); an
    empty header `Location` with a body section (removed, no stop);
  - the rules' order and a `Kind` line after a `was:` line of the same day; an entry `canonical()` refuses that a
    rule stops (the stop wins); a Priority line below the header on an entry needing a change (`refused:`); an
    open `**Resolved**.` (a stop, its `<Word>` as written); a Status line below the header (`Open` written, the
    line listed and left);
  - **twice gives no diff** (§7.4): every case's output run again, without `decided`, is unchanged;
  - **unknown text survives** (§7.4): an entry with an unknown header field, an unknown gate, an unknown body
    section and an unknown Log prefix, whose content comes out unchanged;
  - an entry with a `Waits` line, a `Taken by` and an old-form decision, each left as written;
  - a Log not last (a stop); two Logs (a stop), on an entry with a change; each on an entry needing none
    (returned as given, no stop);
  - an unreal date (`Done 2026-02-30`, passed over to the next source; an archived `Resolved 2026-02-30`, not
    already in the set); an open entry with no Status and with an empty one;
  - branch 4's `Open 2026-10-01 — was: Designed 2026-09-30`, `Open 2026-10-01 by TD-5: x` and `Open.`;
  - a head date that differs from the `**Resolved:**` line's (the head's wins); a date read only from the text
    (listed); a `Superseded` whose head and tail name different ids; `Superseded … replaced by TD-5, not TD-6`
    (the first); `Moved to TD-5 — was: Moved to TD-4` (one id: the first part only); `xTD-5` (no id);
  - nested segments (a `Done` with two `— was:`);
  - the closing date's sources in order: a `**Resolved:**` line over `closed_date`, an older `Resolved` header field,
    `closed_date` over a date read from the text; `Resolved 2026-10-12.` with a `closed_date`;
  - an `Added` comment with nested parentheses; an `Added` comment on an unsorted Log; a `Kind` line and a `was:`
    line already in the Log (not written twice); a `kinds` key in upper case; a `decided` and a `kinds` value
    outside their shapes (`refused:`); `decided` `resolved` on an archived entry with no Status (no `was:` line);
  - an `Added` comment equal to a Log line already there (not written twice), and one beginning `filed by`;
  - `Kind` already the mapped value; a `kinds` key in another case;
  - `decided` answering each stop on the word; `decided` on a missing date (still a stop); `decided` on an
    entry with nothing to answer (a stop);
  - an entry needing no change but not in canonical order (returned byte for byte);
  - the returned words, each template at least once;
  - a stop on both the date and the word (both returned, the date's first); an archived entry whose head is dated, one of
    whose segments is undated and whose `**Resolved:**` date is unreal (no lift); an archived undated head with a
    tail and a `closed_date` (no lift: its new form takes more than its head); an unreal `closed_date` (passed
    over); an open stage word whose head is undated and has a tail, with an unreal
    `**Resolved:**` date and a real `Added` (still no lift); a segment whose own head date is unreal (no
    lift); `Added: 2026-01-01 ()`, `( x )` and `(a) (b)` (kept whole); `Added: 2026-01-01.`; a gate's age before and after an `Added`
    comment moves it, and after a lifted Status note dated before the Log's first line moves it; an open `Resolved 2026-10-03: x` (a stop) and with
    `decided` `open`.
- **`fixtures/ledger_writer/migrate_*`** (B2): a ledger whose one archived entry stops, so nothing is written and
  exit 1 (§7.4: *an unmapped Status word stops it with a list and writes nothing*); `--dry-run`; `--closed-dates`;
  `reblocked`: an archived `OBE` blocker an open entry waits on (re-blocked once `Dropped`) and a prose one answered
  `--as …=resolved` (released); `--closed-dates` keys padded and unpadded (one number); `Moved to <own id>`
  (`Dropped`, listed) and `Superseded D by <own id>` (a stop) in `fixtures/migrate/`;
  `--stage-kind`, and a word outside the stage words, a word given twice and an empty `KIND` (exit 2); an `--as`
  id given twice, an unknown named `TD-n`, a bad `--closed-dates` key, and `--plan` with `--dry-run` (exit 2); a
  stop printed plain and with `--json`; `--base` and `--resolved` (exit 2); `--as`; a bad `--release` and a bad `--closed-dates`
  (exit 2); a v1 file (exit 2); a ledger already migrated (exit
  0, `subject` null); the subject's count.
- **`fixtures/ledger_edit/check/status_*`** (B3): each of the four forms passing in its place; each in the wrong
  place; `Open 2026-10-01`; `Resolved 2026-10-03.`; lower case; a bare `Resolved`; `Superseded D` with no `by`; `Superseded D by` an id outside `Blocked by`'s
  grammar; an archived `Resolved 2026-02-30`; `Superseded D by TD-n` and `Dropped D` in the ledger; an archived
  `Open`; an open `Open, held`; no Status; a retired word, whose text names its
  replacement (`Done` on an open entry: `archive it, or Open`); an open `Resolved 2026-10-03`,
  `resolved 2026-10-03` in lower case, and `**Resolved**.` (each `archived: archive it, or Open`); a ledger with an
  `archive-open-parts` record and `status` records in both files (their order); standing with `old` given (still an error); a v1
  ledger (ℹ).
- **`fixtures/ledger_edit/check/location_*`** (B0): a header `Location` added by an edit (an error) and standing
  (ℹ), with `("retired", "location")` added to `run.py`'s `check` filter beside `("retired", "waits")`; their
  inputs' Statuses are in the set, so B3's `status` filter leaves them as they are.
- **`fixtures/ledger_writer/status_*`** (B3), the writes on an un-migrated ledger: `archive` of an open entry
  whose Status is a stage word, and `reopen` of an archived entry whose Status is `Done D`, each written (the entry
  it moves leaves with a Status in the set, and every other entry's `status` error stands as before, so none is
  new); `renumber` of an entry whose Status is outside the set, refused (D1: *migrate it first*); a `note` on such
  an entry, written (the flag's text unchanged).
- **`fixtures/edit/`** and **`fixtures/ledger_writer/`** (B0): `canonical()` placing a `Waits` and a header
  `Location` after `Part of`, in file order; `new --location` writing the body section; a non-empty `set
  --location` and `new --field Location=…` refused; `reopen` of an archived entry, and `renumber` of an open one,
  with a header `Location` refused (*migrate it first*).
- **Existing fixtures B3 regenerates.** `fixtures/run.py` records the whole of `check()` for each
  `fixtures/ledger/*` case, so every entry there with no Status or one outside the set gains a `status` record (an
  error where the ledger declares major 2, ℹ where not), and the ℹ `retired` Status records go. A fact-check found
  these among them: `ledger/{gates,belowheader,crossversion,events,supersede,unknownstatus,escaped}.md` and their
  archives, and `ledger/parts.archive.md`. And `ledger_edit`'s `check` cases (`fixtures/ledger_edit/cases.json`)
  filter `check()`'s output to the kinds at `run.py:599-601`; B3 adds `status` to that filter for every `check`
  case, so the nine existing ones gain records where their inputs, `ledger_edit/check/*.md`, hold a Status outside
  the set (`check/after.archive.md`'s `Resolved 2026-01-20: done` among them), and the new `status_*` cases use it.
  Their inputs carry old forms on purpose, to prove the readers still read them, so **the inputs stay** and only the
  expected JSON changes. B3 regenerates from a real run and lists, in its PR, every fixture file that differs (the
  `ledger_writer` report and `--check` cases, `report_check_base` among them, whose counts rise with the new
  errors, as well as those named here) and why its change is only those records; a case whose own assertion breaks is changed and said. `tests/test_ledgerboard.py`'s `check()` calls on ledgers whose entries have no Status
  (about 30) are updated in B3, which lists each: a Status added, or the new error asserted.
- **`fixtures/grammar/`** (B4): an accepting and a refusing case per D5 production.

## The builds (filed on Paul's go after the rounds)

In series, B0 to B4: each edits `SPEC.md`, the module and `fixtures/run.py`. Each lands its `SPEC.md` text with its code.

- **B0.** The canonical form, `new` and `set` (D4): the header order, the retired header `Location` graded as
  `Waits` is, `new --location` writing the body section, a non-empty `set --location` or `--field Location=` refused, with T1,
  T4, T2's `Location` parts and T6's `new` and `set` parts. Every fixture whose output differs is regenerated from a
  real run and listed in its PR, each with why: those whose `canonical()` output moves (a `Waits` or header
  `Location` before another field; a fact-check found `ledger_edit/expected.json`, `ledger_writer/unknown_text_edit`
  and `unknown_text_fmt`), `ledger_writer/new_basic` (`new --location`), and those whose `flags` gain an open
  entry's ℹ `retired` record for a header `Location` (reviews found `ledger/basic.md`, `basic.v2/TD-001.md`,
  `escaped.md`, and `ledger_writer/report_pickable`, `report_counts`, `report_list_where`, `report_v1`,
  `report_summary_needs` and `report_check_base`). Of the `renumber` cases, only `renumber` reaches the gate with a header
  `Location` on the entry it renumbers: its input has the line moved into the body, since its point is the
  renumber and a header `Location` now refuses it. `renumber_held` and `renumber_also_in_ledger` exit 2 before any
  gate, and `renumber_parent` and `renumber_archived` gain no record, so their expected files do not move. The new
  refused case is its own. With the `location_*` check cases and `run.py`'s filter entry for them. `set_field`'s `--location ""` still
  removes the field. First, so B1's and B2's expected
  texts are written in the order that stands.
- **B1.** `migrate_entry()` (D2) and `status_problem()` (D1's function, which its post-condition calls; `check()`
  does not run it yet), with T5 and `fixtures/migrate/`. Until B3 lands T3, T5 states the four forms where it
  names them and refers to no *The closed Status set*; B3 adds that cross-reference with T3.
- **B2.** `ledger.py migrate` (D3), with T6's `migrate` parts and `fixtures/ledger_writer/migrate_*`.
- **B3.** `check()` runs `status_problem()` (D1), with T2's Status parts, T3 and T7, `RETIRED_STATUS` removed, the
  regenerated fixtures and tests; **and this repo's own ledger migrated in the same PR**, by B2's command, its
  `--dry-run` listing in the PR body, and its `--closed-dates` a file the builder makes from git (each archived
  entry's day, in UTC, of the last commit that moved it into `archive/`), outside the package and not committed, its making said in the PR: the archive holds Status tails (TD-053's `Resolved 2026-11-06: designed and
  built …`) and heads that do not read (TD-001's `Resolved 2026-10-12.`, TD-002's `Resolved 2026-10-14.`), 11
  archived entries hold `Added` comments, and 54 entries (53 archived, one open) a header `Location`.
- **B4.** The grammar appendix (D5, T8) and `fixtures/grammar/`.

Then the release (Paul's), and the hand-off: once v2.7 is tagged, an entry on agent-cadence's ledger, then
ShiftLead's, each to vendor v2.7 and run `migrate` in the same PR (§7.2 step 6), filed through each repo's question
seat (`ao td add --repo`):
- **agent-cadence:** its `ledger.py` wrapper passes `--closed-dates` from git and `--stage-kind` from cadence.md's
  `Kind` vocabulary (`designed=build`, `built=live-check`), and commits under the printed subject (the tripwire
  exempts the migrate commit by that subject alone);
- **ShiftLead:** the same through its vendored copy, and `Waits = until | event` leaves its `Fields:` line in the
  same PR.
The roster repos follow only after both have run on it (§7.3 *Order*).

## Not in this release

- Renaming `**Resolved:**` to a status-neutral lead (§2.2: v3.0 material).
- Removing the old-form readings (`Waits`, `Taken by`, `decision (who) — text`, a header `Resolved` or
  `Location`) and `migrate` itself: v3.0 (S7).

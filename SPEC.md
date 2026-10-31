# The ledger and board formats — versions 1 and 2

This is the formats' one definition in prose; `ledgerboard.py` is the one implementation and
`fixtures/` the cases any implementation must reproduce. Where this text and the module disagree,
the fixtures decide, and the disagreement is a bug here. *What to do* with a field — lanes,
routing, who may write what, when a sweep runs — is a consumer's, never the format's.

## The ledger

A ledger is a Markdown file (by convention `docs/technical_debt.md`) with an archive beside it
(`docs/technical_debt_archive.md`). HTML comments are not read: a seed's commented-out example
entry is not an entry.

**Entries.** An entry starts at a `## TD-NNN: title` heading and runs to the next `## ` heading of
any kind. `TD-` plus a number (zero-padded to three digits by convention), assigned in order, never
reused.

**The header block** is the entry's fields: the lines after the heading's blank lines, up to the
next blank line. Each `**Name:** value` line there is one field, on one line; a repeated field's
first wins. Names compare case- and separator-insensitively (`Blocked by`, `blocked-by`,
`BLOCKED_BY`). **A field's value is its first word**, lower-cased; the rest of the line is a free
comment. The format's own fields: `Priority` (High, Medium, Low), `Type` (debt — the default — or
feature), `Added`, `Status`, `Blocked by`, `Location`, `Part of` (v2.1), `Escaped from` and `Id take` (v2.2). A
`Priority`, `Type`, `Blocked by` or `Part of` written below the header block is still read, and flagged.

**`Escaped from`** (v2.2) — `**Escaped from:** TD-n` or `<repo>#TD-n`, on a defect: the design entry
whose review should first have caught it. Its value is free, so no `Fields:` line declares it; the
format only parses it, and what it resolves to is the consumer's.

**`Id take`** (v2.2) — `**Id take:** <nonce>`: the 32-hex `take:` nonce of the counter take that
handed the entry its id. It is provenance, never an assignment, and nothing routes on it. It is
judged only where its id is new; after the merge it is inert, and no tool strips it. Which counter
and what judges it are the consumer's.

**`Fields:`** — a ledger may declare its own fields' vocabularies once, on one preamble line before
the first entry: `Fields: Owner = builder | designer; Kind = build | design-first`. A declared
field's value outside its vocabulary is an error; an undeclared field is read but not validated.
The format's own fields are never redeclared.

**`Blocked by`** — comma-separated items, each `TD-NNN` or `<repo>#TD-NNN` (another repo's
entry; `<repo>` a name or `owner/name`), then optionally `decision (<who>)` last, whose pointer
runs to the end of the line. **Pickable is derived, never written:** an entry is pickable when it
has no `Blocked by`, or every entry it names is archived and it names no decision — and no open
entry is `Part of` it (below). An item that cannot be read, an entry in neither the ledger nor the
archive, or another repo's entry the reader cannot resolve keeps the block. A written
`**Pickable:**` line is only a field.

**`Part of`** (v2.1) — `**Part of:** TD-n`, on a part, names its **one** parent in the **same
ledger**; free comment may follow the id (a second id after a comma is a second parent, an error;
anything after the first id with no comma is comment).
A parent is any entry: a design and its builds or live checks, a fix or feature and its subtasks.
It keeps `Blocked by` apart from the parts: a parent's `Blocked by` names only what must really
land first, and its parts keep it unpicked while any is open — what listing them in `Blocked by`
did before. A parent's record carries `parts_open` (its open parts, never in `blocked_by`) and a
part's carries `part_of` (the id as written; ids match by number, `TD-7` is `TD-007`).
- A part's own pickable comes from its own `Blocked by` alone: parts do not inherit their parent's
  blockers. A part that also waits on its parent's blocker names it in its own `Blocked by`.
- **A part is never blocked by its parent or any ancestor**: the parent waits on the part's archive
  and the part on the parent's, so neither moves.
- What `ledger --check` says, ids normalised as a blocker's are, on the entry as the edit leaves it
  (so an edit that removes the bad id passes):
  - a `Part of` naming another repo's entry (`<repo>#TD-n`), a value that is not an id, or a second
    parent is an unreadable item (⚠, `part-of-item`), and makes no parent; one naming no entry in the
    ledger or the archive is ⚠ (`part-of-unknown`); one naming an archived parent is ℹ
    (`part-of-archived`): an open part of a finished parent;
  - over the **waits-on graph** — X → Y when X is `Blocked by` Y, P → C when C is `Part of` P (a parent
    waits on its part) — **(a) no cycle**: every entry on a cycle (a part blocked by an ancestor, a
    `Blocked by` loop, an entry part of itself) carries its own flag (`cycle`); **(b) no legacy
    edge**: a parent's `Blocked by` naming its own part or a part's part, the old way of keeping it
    unpicked, is flagged on the parent (`legacy-part`). Both are information on a standing ledger
    and errors on a changed or new entry (`check()`'s `EDIT_ERRORS`), so an edit to any entry on a
    cycle fails whichever end it touched.

**Pick order** is the rank (below): by card, then within a card by dependency (an entry after what
it is blocked by and after its parts), then by key. With
no rank file it is Priority (High, Medium, Low, then anything else), then Type (debt before feature),
then id order — except that a card moves as one, at its best member's key, so a prerequisite is
picked before the entries that wait on it.

**The summary table:** one `| TD-NNN | title | priority | status |` row per entry with a body in
the ledger, in pick order by intent.

**The archive** holds resolved entries, bodies whole, in the same shape.

**`Tracker:`** — an entry mapped from an outside tracker carries its id as `**Tracker:** ABC-123`.
Every edit keeps it byte for byte; what it links to is the importer's.

## The ledger as a directory (v2)

A v1 ledger is one file that every filing edits in the same places — a summary row and a body, on
neighbouring lines for neighbouring ids — so concurrent filings conflict. **A v2 ledger is a
directory** (by convention `docs/ledger/`) with one file per entry, and no stored summary table:

```
docs/ledger/
  README.md        # the opening prose, then the preamble lines: Ledgerboard: 2, Fields: …
  TD-160.md        # one entry: its `## TD-160: title` heading to the end of its text
  rank.yml         # the rank file (rank_path() of the directory)
  archive/
    TD-121.md      # an archived entry: the same file, moved
```

- **An entry file** is named `TD-NNN.md`, the id spelled as its heading spells it (`TD-24.md`); the
  title lives only in the heading, so a retitle never renames a file. An entry is a `TD-*.md` file
  directly in the directory or in `archive/`; any other file there is not an entry.
- **`README.md`** holds what a v1 ledger holds before its first `## ` heading, and declares
  `Ledgerboard: 2` on a preamble line.
- **Archiving** moves the file into `archive/` (with its Status edit). Open and archived stay two
  texts, so *every blocker is archived* is still a test of which text a heading is in.
- **The summary table is not stored**; a consumer prints one from the entries in pick order.
- **Reading** (`load(path, ls, read)`) gives the same two texts a v1 ledger and its archive give:
  `README.md`, then each entry file in id order (by number), joined by one blank line — the
  ledger's text without a table — and `archive/`'s entries the same way. Every parser reads those
  texts unchanged. Given a v1 file instead, `load()` reads it and its archive beside it
  (`<stem>_archive.md`, `archive_path()`), so one call reads either major.
- **The caller does the I/O.** `ls(path)` returns the names of the files directly in the directory
  `path` (no subdirectories), or None when `path` is not a directory; `read(path)` returns a file's
  text, or None when there is none, which reads as empty. Paths are joined with `/`. A file-system
  pair and a git pair (one `git ls-tree` and one `git cat-file --batch` at a revision) are the
  caller's; the module opens nothing, as everywhere else in it.
- **One entry** is `entry_path(path, tid, ls)`: the one file holding it, open before archived,
  matched by number (`TD-7` finds `TD-007.md`); None when there is none or `path` is a v1 file.
- **Damage a hand edit can do** is named by `v2_problems(path, ls, read)`, which a consumer calls
  beside `version_problem()`: an entry file that does not open with its one `## TD-NNN:` heading
  numbered as its name, one whose HTML comment is not closed in the file (it would hide the next
  entry once joined), and two files for one number across the ledger and its archive.
- **Migration** is `split(ledger, archive)`, for a v1 ledger only: the v2 files of a v1 pair. Each
  entry's text runs from its heading to the next `## ` heading outside an HTML comment, read as
  `entries()` reads comments, and is its file with trailing blank lines trimmed to one newline.
  `README.md` is the text before the ledger's first heading, with `Ledgerboard: 2` under its title,
  then the `## Summary` section's lines other than the table and blank lines. The archive's text
  before its first entry is dropped. It refuses another `## ` section, an id twice, and a result
  that does not read back the same entries (compared by id), the same `Fields:` and version 2, or
  that `v2_problems()` flags.

## Ledger entries and their edits (v2.2)

A v2 entry file is one entry, and the writers render it in one **canonical form**, so a tool can
tell an entry it would have written from one it would not. A reader reads either.

**The entry.**
- **The heading** is `## TD-n: title`.
- **The header block** is the lines after the heading's blank lines, up to the next blank line, as
  above. A writer needs every line there to be one `**Name:** value` field and each name to appear
  once.
- **The body** is everything after the header block. It is cut into **sections**. A section's
  **lead** is the bold run that opens its first paragraph (`**Why:**`, `**Done when**`). The section
  runs through every following paragraph up to the next paragraph that opens with a bold run, so a
  Fix keeps its bullets. A paragraph inside a code fence opens no section.
  - Leads match by `field_key` with the colon optional: `Done when` and `Done when:` are one name.
  - A qualified lead (`**Fix (to design):**`, a dated `**Note (…):**`) is its own section, matched
    only by its whole text.
  - A body lead named like a field (`**Location:**` in the body) is a body section, never a field.
  - Text before the first lead is an unnamed section, kept as written.

**Canonical form** (`canonical(text)`): line endings normalised to `\n` first, then
- the heading (its title stripped);
- one blank line;
- the header block in this order: `Priority, Type, Added, Owner, Kind, Status, Taken by, Id take,
  Blocked by, Waits, Part of, Location`, each spelled so. Then any other field, spelled as the file
  spells it, in the file's order. A place in the order is a rendering rule, not a declaration:
  `Owner`, `Kind`, `Taken by` and `Waits` are not the format's own fields. A header `Resolved` is not
  in the order and is kept where the other fields put it;
- one blank line;
- the body byte for byte, with its leading and trailing blank lines dropped and one trailing
  newline.

`canonical()` is idempotent. It refuses text that is not one entry: it must open with its one
`## TD-n:` heading outside HTML comments and close every comment, which is what `v2_problems()` asks
of a file. A v1 ledger is refused with *split first*. It also refuses a header block it would have
to lose or duplicate a line of, leaving that for a person to fix:
- a line that is not a field (a wrapped `Location`);
- a repeated field;
- a field written below the header block that the reader still lifts (a `Priority`, `Type`,
  `Blocked by` or `Part of`).

Its rule: the result reads back the same id, title, fields and body, or nothing is written.

**A new entry** (`entry_text(id, title, fields, sections)`) is that form. Its fields are one line
each, and an empty value is left out. Each section is written `**<name>:** <text>`; a first section
with no name is the unnamed one, written as given. It is refused for an id that is not `TD-n`, a
title that is empty or more than one line, a field that would not read back as one line or is named
twice, and sections that would not read back as given (a section's paragraph that opens in bold
would start a section of its own).

**A change to the canonical form is a minor release**: each consumer reformats its entries once,
when it takes that release.

## The rank

The rank is a person's order of a ledger's entries; it is the pick order.

**Cards.** A ledger's entries fall into **cards**: the connected components of its entries over
their `Blocked by` ids (the ids before any `decision (…)`) and their `Part of` parent (v2.1), joined in both directions
(`components()`); ids match by number, as a blocker does (`TD-7` is `TD-007`). An id an entry names that is not among the entries read — an archived or unknown
one — is listed with the card but is not a member and joins nothing; a `<repo>#TD-NNN` id is listed
for a caller to join cards across repos. The same rule reads an archive.

**Keys.** Every open entry has a key, a string compared character by character in code point order,
except that `|`, the separator, sorts below every other character (`key_order()`); a shorter key that
is a prefix of a longer one sorts first. A key starts with a letter or digit and holds letters,
digits, `|`, `_`, `.`, `/` and `-` (ASCII only). An entry's key is its line in the rank file when it has one,
else its **implicit key**: its Priority's band (`1` High, `2` Medium, `3` Low, `4` anything else), its
Type's index in pick order (`0` debt, `1` feature), its id number zero-padded to six digits, and, where
a caller orders entries of several repos together, the repo's name — joined by `|`
(`2|0|000642|shiftlead`; `implicit_key()`). Two undragged neighbours always have room between them.
`midpoint(a, b)` returns a key strictly between two keys, either end open (None); it writes digits
and lower-case letters after a shared prefix (a `|` only where nothing else fits), and a key it
writes past the prefix never ends in `0`, so there is room again (one that only follows `b`'s own
characters may). It refuses keys out of order and a pair with no key between
them — `a` against `a` followed by `|`s alone, or nothing against `0` (a key starts with a letter or
digit, so none sorts below `0`).

**A card's key** is the best (lowest) key among its members that have a line, when any has one,
else the best implicit key among them. So a card the person placed keeps its place: a Priority edit
on a lined card moves nothing, and a member added later takes the card's key. Cards sort by key,
ties by their lowest id; within a card an entry comes after every member it is blocked by and every
member that is `Part of` it, then by its own key (a cycle is broken by key).

**The rank file** is named from the ledger's path: `<ledger stem>_rank.yml` beside it
(`docs/technical_debt_rank.yml`; `rank_path()`), or `rank.yml` inside a v2 directory
(`docs/ledger/rank.yml`), with no setting of its own. Its grammar: `#`
comment lines first, then one line per entry, `TD-NNN: <key>`, sorted by key; nothing else. It is
YAML-shaped but read only through `rank()`, which takes every key as a string (`09` is a key, not a
number). The reader flags a line it cannot read and a repeated id (⚠, the first line holds), and a
blank line, a comment below the first entry, or a line out of key order (ℹ). The writer
(`set_rank()`) sets or removes the given ids' lines, places a new line at its key's place, and keeps
every other line byte for byte (a new line takes the file's own line ending). A line for an archived entry is ignored — only open members carry a
card's key — and harmless until its card is wholly archived.

**Rank writes** are made by a tool, each in a commit (and PR) that changes the rank file alone,
under a subject `queue: <action> TD-a, TD-b (<tool>)` (`queue_subject()`, ids in id order):
`rank` sets a moved card's members' lines, `join` gives a card's newcomer the card's key, `prune`
removes the lines of a card whose members are all archived. `subject_kind()` reads every one as
`queue`.

## The board

A board is a Markdown file (by convention `docs/user_attention.md`) of items for a person.

**An item** is one line: `- [ ] [kind] YYYY-MM-DD (session <name> on <host>, or n/a) — text.
Context: … Due: YYYY-MM-DD.` A closed item is ticked: `- [x] … Closed: YYYY-MM-DD — why.` Items
are never deleted; closed ones are archived in bulk once ten or more sit on the board. When an open
item and a closed one have the same key (below), the item is closed: a merge kept both sides.

**The head** — `(session <name> on <host>…)`, either name optionally backticked; the session is the
first name, the host the first word after ` on ` inside the parentheses; `n/a` names nothing.

**Kind** — one optional word before the date: `decide`, `act`, `look`, `watch`, `fyi`. Only a word
followed by a date is a kind. `decide`, `act`, `look` and no word are the person's to-do; `watch` is
a re-check whose check-by date is its `Due:`; `fyi` is never due (a `Due:` on one is ignored, and
flagged).

**`Due:`** — `Due: YYYY-MM-DD`; an item's first `Due:` is its date. A date-shaped token the reader
cannot read (`Due: 2026-1-9`) is reported, never silently undated.

**`Context:`** — what the item refers to, read as refs in order: `TD-NNN` or `<repo>#TD-NNN`,
`PR #N` (`PRs #12/#13` and `PR #12, #13` give both), and best-effort `branch <name>`.

**Trailing fields**, after the `Due:` when there is one, each starting a sentence and anchored to the
line's end, in this order:
- `Answers: a | b (default).` — the proposed answers, `\|` for a literal bar; at most one marked
  ` (default)`, the asker's recommendation. An answer may say what it leads to after its first
  ` — ` (space, em dash, space): `<label> (default) — <consequence>`. The **label** is the answer —
  what a press sends and `Decided:` records — and the mark ends it; the **consequence** is the
  rest, a later ` — ` included, read beside the labels (`parse_consequences()`, `""` for an answer
  that says none; `B —` is the label `B`). A dashless answer is all label, and a mark at the very
  end of an answer with a consequence (`a — b (default)`) still marks its label. A consequence
  shaped like a reply (` — <name>, <date>: `) reads as a reply, so no writer writes one.
  A `look` carries exactly `Answers: Works | Not right: <what>.`
  Its second answer is a **form**, whose slot is the person's words: an offered answer is the form when
  it is `Not right:` alone or followed by one `<…>` placeholder (whitespace collapsed, case as written);
  `Not right: wrong repo` is a complete answer like any other. An answer given to a form fills it when
  it starts `Not right:` and is not itself the form — one that adds nothing, or only a placeholder, is refused.
- `Decided: <text> (YYYY-MM-DD).` — the person's answer. A decided item stays open and due; it now
  waits on whoever acts on it, not on the person.

**The bold head** — an item's first `**…**` run, whitespace collapsed, read outside its replies'
words (its fields' are read: a bold answer with no bold before it is the head), is its title where it
has one. A blank run (`** **`) is none. A line with none has no bold head; what stands in for it is the
consumer's.

**Replies** — ` — <name>, YYYY-MM-DD: <words>` after the `Due:` and ahead of the trailing fields,
any number in a row. A reply's words never carry `Context:`, `Answers:`, `Decided:` or `Closed:`,
nor a `Due:` on an item that has none.

**The detail block** — the lines right under an item indented deeper than its `-`, up to a blank
line, a line no deeper, or another item. No edit touches it.

**The item key** — the line with the tick, `Closed:`, `Decided:`, `Due:` and the reply tails taken
out, indentation kept. It is what makes an open and a closed copy of one item, or a snoozed or
replied-to one, equal. **Consumers persist keys, so what the key is for a given line is part of
the format: changing it is a new major version.**

**Preamble lines** — `Name: value` lines before the items (`Kinds:`, `Format:`, a dated stamp
`Name: YYYY-MM-DD (…)`) are kept byte for byte by every edit. Which stamps a consumer writes and
what they mean are the consumer's.

## Edits

Every edit rewrites one open item line and nothing else, and is refused unless the reader reads
back exactly what was meant:
- **snooze** sets the item's `Due:` (adding one ahead of the trailing fields when it has none);
- **done** ticks it and appends `Closed: YYYY-MM-DD[ — why].`;
- **decide** writes `Decided: <answer> (YYYY-MM-DD).`, replacing an earlier one;
- **reply** appends a reply tail.

A new item (`item_line(text, due, today, session, host, context)`) is composed as `- [ ] <today> (session `<name>` on <host>, or n/a) — <text>. Context:
<about>. Due: <date>.`; an answer given elsewhere (on a ledger entry) as an already decided `decide`
item with `(person)` as its head.

**The commit subject of a board write** is one line: `<tool>: <action> <head>[ to <date> | :
<answer>] (session <name>)` for the four edits, and `<tool>: append <head> (session <name>)` for a
new item — the head is the item's text after its prefix, before its fields, bold dropped, at most
60 characters; a reply's words never appear. Subjects written before v1 by one consumer
(`shiftlead: board|answer <head> (from <ref>)`, `shiftlead: board decide <ref> (person)`) still
read as appends.
`subject_kind()` names a subject `edit`, `append` or (a rank write, above) `queue`.

## Versions

A ledger or board may declare its major version on a preamble line, `Ledgerboard: 1`; none means 1.
A v2 ledger declares it in its `README.md`, which `load()` puts first.
A reader that meets a newer major than it knows reads nothing and says so (`version_problem()`, which a consumer calls before it trusts what it parsed — no parser calls it for you). A release of the module
is `v<major>.<minor>`: a minor release reads every file the major's earlier releases wrote.
**v1.3 reads one thing differently:** an answer whose own text held ` — ` was one answer before
v1.3 and is now a label and a consequence — `Keep — nothing changes` was the answer `Keep — nothing
changes` and is now the label `Keep`, so a `Decided:` written from the old answer no longer
equals a label; an answer ending in a bare ` —` (`B —`) was the label `B —` and is now `B`; and a
mark written mid-answer (`A (default) — x | B (default)`) now counts as a second mark. The item
key is unchanged for every line. A board that wrote such answers re-reads them; one with
no ` — ` inside an answer reads exactly as before.
**v2.0 adds the ledger as a directory** (above): `load()`, `entry_path()`, `split()`, `v2_problems()` and
`archive_path()`, and `rank_path()` of a directory. A v1 ledger reads exactly as before, through
`load()` too; the board is unchanged, and `Ledgerboard: 2` on a board means nothing new. A v1.x
module meets a v2 repo as a missing `docs/technical_debt.md`, never a wrong reading, so a repo
moves to a v2 ledger only once every reader of it runs v2.0.
**v2.1 adds `Part of`** (*The ledger*, above): the field, a parent unpicked while a part is open and
ordered after its parts, cards joined through it, and the checks on it. An older reader ignores the
field, so it reads a parent whose parts are no longer in its `Blocked by` as pickable: a ledger
writes `Part of` only once every reader of it runs v2.1. A ledger with no `Part of` reads as
before, except that a `Blocked by` cycle, which no earlier release named, is now flagged (ℹ when
standing).
**v2.2 adds `Escaped from`** to the format's own fields: in a ledger with a `Fields:` line it is no
longer an `undeclared-field` (an older reader flags it as one there), and a `Fields:` line that
declares it is ignored and flagged, as for the other own fields. `Id take` joins them the same way.
v2.2 also gives ledger entries writers (*Ledger entries and their edits*): the canonical form,
`canonical()` and `entry_text()`. It reads every file v2.1 read, as v2.1 did, and v2.1 reads every
entry it writes.

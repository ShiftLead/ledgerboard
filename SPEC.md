# The ledger and board formats — versions 1 and 2

This is the formats' one definition in prose; the module, `ledgerboard/__init__.py`, is the one implementation and
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
  - (v2.2) Given the ledger before the edit, an entry that has **left the ledger while an open entry
    is still `Part of` it** is an error on the parent, naming its parts (`archive-open-parts`). This
    covers a parent archived, or renumbered, ahead of its parts. The parts' own `part-of-archived`
    stays ℹ. The error is never standing, since only the edit made it.

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
  once, so an entry with a body has at least one field: its first paragraph is its header block.
- **The body** is everything after the header block. It is cut into **sections**. A section's
  **lead** is the bold run that opens its first paragraph (`**Why:**`, `**Done when**`); a paragraph
  opens the body or follows a blank line. The section runs through every following paragraph up to
  the next paragraph that opens with a bold run, so a Fix keeps its bullets. A paragraph inside a code fence opens no section: a fence opens on a line of
  three or more backticks or tildes (indented at most three spaces), and closes on a bare line of the
  same character at least as long.
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

**The archived entry.** An entry archived as done has the Status `Resolved YYYY-MM-DD: why`, and
its Fix replaced by one line, `**Resolved:** YYYY-MM-DD (PR #n) — <pointer>`, which is its body's
only `**Resolved:**` section. The pointer names the doc, test or code that now carries what lasts,
and is optional, as is the PR (with no PR, the parenthesis is left out). An entry archived with
nothing lasting to move keeps its Fix and has the line after it. An entry overtaken by another has
the Status `Superseded YYYY-MM-DD by TD-n: why`, and its Why and Fix stay as written. A `Resolved`
header field is the older form of the line: readers still read it, and the writers move it into
the body.

**Edits** (`edit_entry(text, action, *, today, …)`, one of `ENTRY_ACTIONS`) take one entry's text
and return it in canonical form. Each is refused for an entry `canonical()` refuses (a v1 ledger:
*split first*). It is also refused unless the result reads back exactly the change meant, and
nothing else: the same id, title, fields and sections but for the change. An edit that rewrites
the body joins its sections with one blank line, and is refused when an HTML comment there spans
paragraphs. The date is the caller's (`today`, a date or `YYYY-MM-DD`; a time is never written), and
an argument the action does not take is refused. What a field's value means (a
vocabulary, a `Blocked by` item, a cycle) is `check()`'s, which the caller runs on the result.
- **set** (`fields`): sets each field, in its place, or adds it where the order puts it; an empty value removes
  it. A value is one line.
- **note** (`words`): appends ` YYYY-MM-DD: words` to Status. It is refused if Status's first word
  would change, or if the words are more than one line. With no Status, it writes
  `**Status:** YYYY-MM-DD: words`.
- **edit** (`section`, `words`): replaces the named section's paragraphs, keeping its lead as
  written. A section the body lacks is added after the first Why, else before the first Done when
  or Related, else at the end. It is refused when two sections have the name.
- **archive** (`why`, and `pr`, `pointer`, `as_is`, or else `superseded_by`) writes the archived
  entry, above. `pr` is the forge's number or None; with None, a pointer holding `#<digits>` is
  refused, since a reader would take that for the PR.
  - An earlier `**Resolved:**` section is replaced, never doubled, and a `Resolved` header field is
    removed.
  - With no section named exactly Fix, the line goes at the end of the body, and a qualified Fix
    lead is left alone.
  - A missing Status is added.
  - It is refused if two sections are named Fix.
- **reopen** (`why`): Status becomes `Open YYYY-MM-DD: why — was: <old Status>`, or `Open
  YYYY-MM-DD: why` when there was none. The `**Resolved:**` section stays as history, and the caller
  writes a new Fix with `edit`. A `Resolved` header field moves into a `**Resolved:**` section at
  the end of the body, never deleted. An entry with both is refused: a person merges them.
- **renumber** (`new`) rewrites the heading's id to another number. **rename_ref** (`old`, `new`) rewrites that id
  in `Blocked by` and `Part of`. A local id matches by number; another repo's id matches as
  `<repo>#TD-n`.

Moving a file into `archive/` or back, and the relative links that move with it, are the caller's.

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
are never deleted; closed ones are archived in bulk, ten (`ARCHIVE_AT`) being the threshold a consumer reads. When an open
item and a closed one have the same key (below), the item is closed: a merge kept both sides.

The archive moves them (`archive_closed(board, archive)`, v2.3): each closed line with its detail block, and any open line whose key a closed line shares, in board order and byte for byte, appended to the archive's text. Every other board line stays byte for byte. It refuses a moving item that is nested, that has a nested item under it, or whose detail block a blank line breaks, since it would split them. When to archive is the consumer's; `ARCHIVE_AT` is the threshold it reads. The archive is not one of the five edits under *Edits*, which each rewrite one line.

**The head** — `(session <name> on <host>…)`, either name optionally backticked; the session is the
first name, the host the first word after ` on ` inside the parentheses; `n/a` names nothing.

**Kind** — one optional word before the date: `decide`, `act`, `look`, `watch`, `fyi`. Only a word
followed by a date is a kind. `decide`, `act`, `look` and no word are the person's to-do; `watch` is
a re-check whose check-by date is its `Due:`; `fyi` is never due (a `Due:` on one is ignored, and
flagged).

**`Due:`** — `Due: YYYY-MM-DD`; an item's first `Due:` is its date. A date-shaped token the reader
cannot read (`Due: 2026-1-9`) is reported, never silently undated.

**`Hide until:`** (v2.3) — `Hide until: YYYY-MM-DD.`, starting a sentence, read right after the `Due:` field, or
after `Context:` on an item with no `Due:` (an `fyi`), and ahead of the replies (`parse_hide_until()`). Until that
date the item is **hidden**: left out of what needs the person, while it stays on the board and its `Due:`, the
real deadline, is untouched, so once the date comes it shows its true overdue count. A decided item is a
session's work order and is never hidden (`BoardItem.hidden(today)`). A `Hide until:` elsewhere in the text is
prose, never the field.

**What needs the person** (`needs_you(board, today)`, v2.3) is every open item not hidden, each with one class
and a signed `days`, in one order: `decided` (`days` the decision's age; oldest decision first); then the
person's to-do — `overdue` (days past due; most first), `due` (0 on the due date, negative days until it;
soonest first), `bad_due` and `undated` (board order); then each `watch` item, ordered the same way and keeping
its own class and signed days; then each `fyi`, never due. Which of these a consumer shows, and when it
escalates, is the consumer's.

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

**Replies** — ` — <name>, YYYY-MM-DD: <words>` after the `Due:` (and its `Hide until:`) and ahead of the trailing fields,
any number in a row. A reply's words never carry `Context:`, `Hide until:`, `Answers:`, `Decided:` or `Closed:`,
nor a `Due:` on an item that has none.

**The detail block** — the lines right under an item indented deeper than its `-`, up to a blank
line, a line no deeper, or another item. No edit touches it.

**The item key** — the line with the tick, `Closed:`, `Decided:`, `Due:`, `Hide until:` and the reply tails taken
out, indentation kept. It is what makes an open and a closed copy of one item, or a snoozed or
replied-to one, equal. **Consumers persist keys, so what the key is for a given line is part of
the format: changing it is a new major version.** The one exception is v2.3's: the key strips a date-shaped
`Hide until: D` wherever it stands, as it strips `Due:`, so hiding an item never re-keys it. Only a line that
already held that prose before v2.3 is keyed differently.

**Preamble lines** — `Name: value` lines before the items (`Kinds:`, `Format:`, a dated stamp
`Name: YYYY-MM-DD (…)`) are kept byte for byte by every edit. Which stamps a consumer writes and
what they mean are the consumer's.

## Edits

Every edit rewrites one open item line and nothing else, and is refused unless the reader reads
back exactly what was meant:
- **snooze** hides the item: it sets its `Hide until:` (adding one right after its `Due:`, or after its Context
  on an item with no `Due:`), and leaves the `Due:` alone (v2.3; before v2.3 it moved the `Due:`);
- **due** sets the item's `Due:`, the real deadline (adding one ahead of its `Hide until:` and trailing fields when it
  has none; v2.3);
- **done** ticks it and appends `Closed: YYYY-MM-DD[ — why].`;
- **decide** writes `Decided: <answer> (YYYY-MM-DD).`, replacing an earlier one;
- **reply** appends a reply tail.

**A new item** (`item_line(text, due, today, session, host, context, *, kind, answers, default, detail)`, v2.3) is one line, `- [ ] [<kind> ]<today> (<head>) — <text> Context: <context>. Due: <due>.` then `Answers: …` where its kind takes them. Its head is ``session `<name>` on <host>``, ``session `<name>` `` with no host, or `n/a`. The text ends a sentence (a period is added unless it ends in `.`, `?` or `!`), and an empty context is `none`. What a kind takes:
- a `decide` carries two or more distinct answers, at most one marked ` (default)`, and a detail block;
- a `look` carries exactly `Answers: Works | Not right: <what>.`, which the writer writes itself, `Works` marked ` (default)` only when the caller asks;
- an `fyi` carries no `Due:`, and every other kind carries one;
- no kind but `decide` and `look` carries answers.

These are the writer's rules. The reader still reads whatever a line carries. An answer is written `<label>` or `<label> — <consequence>`, with the mark on the label.

The **detail block** is composed from named parts, in the order `Context`, `Question`, `Caveats`, `Recommended`. Each part is one two-space-indented bullet, ``- **<Part>:** <words>``, with any further lines as nested bullets under it. On a `decide` with a default, Recommended opens with that default's label and ` — `. An `Otherwise` text follows the Recommended words on the same bullet as ``**Otherwise:** <words>``. A `decide` needs Context, Question and Recommended. No writer touches the block afterwards.

The writer refuses text, a context, an answer or a detail value that carries a field name, or that is more than one line; a date that is not `YYYY-MM-DD`; a host with no session; and any result the reader would not read back as exactly the item meant, its detail block included.

An answer given elsewhere (on a ledger entry) is written as an already decided `decide` item with `(person)` as its head (`decided_line()`, unchanged).

**The form the writers write** (v2.3): an open item line that `item_line()` or `decided_line()` composed, as it stands after any snooze, decide or reply. In short, the line:
- opens `- [ ] ` at column 0;
- carries an optional lower-case kind, a date, and a head that is ``(session `<name>` on <host>)``, ``(session `<name>`)``, `(n/a)`, or `(person)` on a decided line;
- continues with ` — `, text that ends a sentence and names no field, ` Context: <words>.`, and ` Due: <date>.` on every kind but `fyi`, then, when it has one, ` Hide until: <date>.`;
- may then carry replies, then `Answers:` as *A new item* says a kind takes them (a decided line may carry any or none), then `Decided:`;
- holds nothing else, one space between parts.

Fields inside a reply's words or a `Decided:` text are the person's and are not counted. `item_problem(line)` names why a line is not in that form, or gives None. It checks the item line alone, never its detail block, which stays the person's prose. `canonical_item(line)` rewrites a line into that form, moving `Due:` to its place and spelling it so, and refuses any rewrite that would change the line's item key or lose a word. Consumers persist keys, so a format pass that moved an item's key would break what they hold.

**The gate** is `board_problems(board, old)`: the faults of each open line (every `- [ ]` line at any indent, but an open twin of a closed one) whose item key no line of `old` (open or closed) has. A line an edit only snoozed, decided, replied to or ticked keeps its key, so a line is judged once, when it is added, and a board that was never in the form has no flag day.

**The commit subject of a board write** is one line: `<tool>: <action> <head>[ to <date> | :
<answer>] (session <name>)` for the five edits (`edit_action()` reads the action back, v2.3; a `snooze … to D`
meant a moved `Due:` before v2.3 and a hide since — history, not text a reader acts on), and `<tool>: append <head> (session <name>)` for a
new item — the head is the item's text after its prefix, before its fields, bold dropped, at most
60 characters; a reply's words never appear. Subjects written before v1 by one consumer
(`shiftlead: board|answer <head> (from <ref>)`, `shiftlead: board decide <ref> (person)`) still
read as appends.
The archive's subject is `<tool>: archive <n> closed items (session <name>)` (`archive_subject()`), `<n>` the closed items moved.
`subject_kind()` names a subject `edit`, `append`, `archive` or (a rank write, above) `queue`.

## The board writer (v2.3)

`board.py`, beside the module in the `ledgerboard/` package, is the board and rank writer over files: an
importable library (`plan_add`, `plan_edit`, `plan_archive`, `plan_fmt`, `plan_rank`, each returning a
`Plan`, and `apply(plan)`) and a command line (`python3 -m ledgerboard.board <action>`, a consumer's wrapper
being the command people run). It reads the files it is given, applies the module's edit, and writes the files
back; it never runs git, the network or anything of a consumer's. Its actions:
- **`list`** — every open item's record (`item_record()`), read-only;
- **`add`** — a new item (`item_line()`, any kind, its answers and detail block, `--hide-until`); with `--said` and `--by`, a
  question already answered, its answer following the text as ` — <by>, <date>: <words>`; with `--decided`, an
  item the person decided elsewhere (`decided_line()`). It goes above the first item of the section the
  `--under` heading opens (`## Needs the user` by default), or right under that heading when its section holds
  none; with no such heading, above the board's first item; with no item, at the end. The write is refused when
  `board_problems()` faults the line it adds;
- **`snooze`, `due`, `done`, `decide`, `reply`** — the five edits (`edit_line()`) of the open item on `--line`, refused
  when that line is not an open item or no longer starts with `--expect` (the board moved since it was read);
  `reply` takes its `--by` from the caller;
- **`archive`** — `archive_closed()` of the board and its archive (created when missing), a two-file write;
- **`fmt`** — `canonical_item()` of every open item line at column 0, a consumer's one-time format pass: the
  lines it can rewrite without changing their key, and each line it cannot, with why, reported and kept;
- **`rank`** — `set_rank()` of the rank file (created when missing), `--set TD-n=<key>` and `--drop TD-n`,
  under `--action rank|join|prune`.

Each write prints the commit subject the module gives (`subject()` with `append` for an add, the edit's,
`archive_subject()`, `queue_subject()`) and the paths it changed, or one JSON object with `--json`. `fmt` has no
subject of its own, and a write that changes nothing (a rank line already so) prints none, writing nothing.
`--plan` prints the changes as JSON (each path and its new text) and writes nothing. A write of several files is
both or neither: each is written to a temporary file beside it and renamed into place only when all are built,
and a failed rename puts back the files already replaced. The caller passes what lies outside the files: the
date (`--today`, else the local clock), who replies (`--by`), and the tool and session the subject names
(`--tool`, `--session`). A file that declares a newer major is refused unread. Exit: 0 written (or nothing to
change), 1 a write failed (every file restored), 2 usage, 3 refused.

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
`canonical()`, `entry_text()` and `edit_entry()`, with the archived entry's form; and `check()`
gains `archive-open-parts`. It reads every file v2.1 read, as v2.1 did, and v2.1 reads every
entry it writes.
**v2.3 gives the board writers** (*Edits*, *The board*): `item_line()` writes every kind with its answers and detail block, `item_problem()`, `canonical_item()` and `board_problems()` say what the writers write, and `archive_closed()` and `archive_subject()` move closed items. Nothing is read differently: v2.2 reads every line v2.3 writes, and the item key is unchanged. `item_line()` now refuses a call it used to answer with a wrong line (a field name in its text or context, a host with no session, a name holding whitespace or `` ` , ; ) ``, a `today` that is not a date). It writes no `None` host, adds no period after text ending in `?`, `!` or several periods, and drops a context's own final period, so the line it writes for those inputs, and that line's key, differ from v2.2's. A line already on a board keeps its text and its key. v2.3 also ships the board writer, `board.py` (*The board writer*): the package's first file-level writer. It also adds `Hide until:` (*The board*): `snooze` writes it and leaves `Due:` alone, the new `due` edit moves `Due:`, `item_line(hide_until=)` writes it on a new item, `item_record()` gains `hide_until` and `hidden`, and `needs_you()` and `edit_action()` are new. v2.2 reads a `Hide until:` as text, so it shows a hidden item and leaves the field in the item key: a consumer writes the field only once every reader of its board runs v2.3.

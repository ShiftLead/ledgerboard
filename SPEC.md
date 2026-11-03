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
A `Priority` other than High, Medium or Low (v2.4) is read after Low and flagged (`priority`): an error on
an entry the edit changed, ℹ on a standing ledger.

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

**`Blocked by`** — comma-separated items: ids, each `TD-NNN` or `<repo>#TD-NNN` (another repo's
entry; `<repo>` as below), then **gates** (v2.4), each one of
- `decision (<person>)` — a person owes an answer, a go included; `<person>` is a person's name (*Appendix:
  grammar*), compared case-insensitively. The entry carries an `**Ask:**` section saying what the
  person owes: without one, `check()` flags it (`ask-missing`; an error on an entry the edit changed —
  its whole text, as for the Log — ℹ on a standing ledger).
- `until YYYY-MM-DD` — not before that UTC date. Once today reaches it the gate no longer holds, and
  `check()` notes it (ℹ, `until-past`) until it is dropped.
- `event (<name>)` — something outside the ledger; `<name>` is `[a-z0-9-]+`. The entry carries its
  `**Event (<name>):**` section, which names a typed check (*Events*, below). It blocks until the text
  says otherwise.

The writers write the ids in the order given, then the gates in that order (decisions, `until`,
events), and the words lower-case; the reader reads the gates' words in any case. An entry names at most one decision per person,
one `until`, and differently named events; more is flagged (`gate-repeated`; an error on an entry the
edit changed, ℹ on a standing ledger). A `Waits` field is never read as a gate.

**Pickable is derived, never written:** `pickable(…, *, today)` takes `today`, the UTC date, always.
An entry is pickable when it has no `Blocked by`, or every entry it names is archived and it has
no `decision`, no `event` and no `until` after today — and no open entry is `Part of` it (below).
An item that cannot be read, a retired item (below), an entry in neither the ledger nor the
archive, or another repo's entry the reader cannot resolve keeps the block. Each record's
`blocked_by` lists what holds it: its open ids, then its gates that hold, then each item that keeps the
block unread. A written `**Pickable:**` line is only a field.

**The old form** `decision (<who>) <text>` — a decision followed by anything but a comma or the end of
the line — is read only as the last item: its text runs to the end of the line, so nothing after it
is read. It holds as a decision by `<who>`, and is a retired item. The writers never write it: `new`
(`entry_text()`) and `set` refuse a `Blocked by` value in the old form, and `set` refuses to add any gate
to an entry whose `Blocked by` still holds it, whose text would swallow the gate: migrate it first,
to `decision (<person>)` with its text in `**Ask:**`. v3.0 stops reading it.

**Retired words** (v2.4). A retired word is never reused for a new meaning; the list grows only. Where
v2.x still reads one, `check()` names it *retired* (ℹ, `retired`) with what replaces it, rather than
unknown:
- the fields `Waits` (a gate: `until` or `event`), `Taken by` (`Id take`) and `Resolved` as a header
  field (the `**Resolved:**` body line of an archived entry);
- in `Blocked by`, the gate `hold` (`decision (<person>)` with an Ask), the old form above, and a role in
  `decision (…)`, reserved by name — today `designer`. A retired gate keeps the block, and a retired
  decision is still a decision by its holder;
- the Status words of an open entry `Designed`, `Built`, `Partly`, `Live` and `In` (`Open`, the stage in
  `Kind`); `Done`, `Moved` and `OBE`, an archived entry's, are v2.5's `migrate`'s to map.

**Events** (v2.4). An `event (<name>)` gate pairs with an **Event section** in the entry's body, which
says what is waited for and how a host tells it happened:

```
**Event (vendor-ships):** the vendor's repo carries the new release.
check: file-contains acme/vendor files/lib.py "v2.4"
```

- It is two lines: the lead `**Event (<name>):**` and the event in plain words, then exactly one
  `check: <type> <args>`, a **typed check** (`parse_check()`). `parse_event_section()` reads one section,
  `event_sections()` an entry's. The section is a body section like any other, so it may sit anywhere
  before the Log.
- The arguments are separated by spaces, except the quoted text: it runs from its opening `"` to the
  line's **last** `"`, so it may itself hold quotes, and nothing follows it. The host matches it
  literally, never as a pattern.
- **The check types** and their arguments, each with its four outcomes (`CHECK_OUTCOMES`): **passed** —
  the host lifts the gate; **not yet** — nothing happens; **impossible** — it can never pass as written,
  and goes to the board at once; **error** — the check could not run (a run past the host's time limit
  among them), and goes to the board as broken, never read as not yet. When in doubt a result is an
  error, never impossible.

  | Check | Passed when | Not yet when | Impossible when | Error when |
  |---|---|---|---|---|
  | `pr-merged <repo>#<n>` | the forge says the PR is merged | it is open | it is closed unmerged | it is not found (a forge answers 404 for missing and for unauthorised alike), or the forge cannot be read |
  | `file-contains <repo>[@<ref>] <path> "<text>"` | the file at the ref (none: the default branch; a tag is a ref) contains the text | the file, the ref or the text is not there yet | never | the repo is not found, or cannot be read |
  | `ref-includes <repo>@<ref> <commit>` | the commit is an ancestor of the ref (a pin at or past it) | the commit or the ref is not there yet | never | the repo is not found, or cannot be read |

  A new type comes in a format PR and states all four outcomes. Every check is also an error when the
  host's own rule refuses it: a check reaches a repo only on the host's roster and at least as visible as
  the ledger's own repo, with read-only tokens.
- **Arguments are confined**, since anyone with PR rights can edit the ledger and a check runs with the
  host's credentials. `parse_check()` gives a `problem`, and `check()` refuses the section, for:
  - a `<repo>` outside the `<repo>` grammar (below);
  - an `n` that is not 1 to 18 of `[0-9]`;
  - a `commit` that is not 7 to 40 of `[0-9a-f]`;
  - a `ref` that fails git's `check-ref-format --allow-onelevel` rules (a component starting with `.` or
    ending `.lock`, a control character, a space, any of `~^:?*[\`, `//`, a trailing `/` or `.`, `@{`, or
    `@` alone), or that starts with `-` or holds `..` or `:` — no option injection (`--output=x`), no
    revision syntax (`a..b`, `@{u}`, `ref:path`) — or holds URL or query syntax (`#%&=+`), whitespace,
    or anything outside printable ASCII, since a ref goes into a forge's API path or query;
  - a `path` that is absolute, has an empty, `.`, `..` or `.git` segment, starts with `-`, or holds a
    glob character (`*?[]`), URL or query syntax (`#%&=+`), a quote, a backslash, whitespace, a control
    character or anything outside printable ASCII;
  - quoted text that is empty or spaces alone, holds a control character, or has anything after it.

  Arguments are separated by spaces and tabs only, so no other whitespace hides a second argument, and a
  ref or path read is the one shown: ASCII alone, as `<repo>` is.
- What `check()` says of an open entry's events (`event_problems()`), each scoped by the entry's whole
  text, as the Log's flags are (an error on an entry the edit changed, ℹ on a standing ledger):
  - `event-section` (⚠): an `event (<name>)` gate with no section of its name, or two sections of one name;
  - `event-check` (⚠): a section `parse_event_section()` refuses — a name outside `[a-z0-9-]+`, no words,
    no `check:` line, two, a line after it, words past the first line, an unknown type or a confined
    argument;
  - `event-ungated` (ℹ): a section with no gate of its name, unless a `gate lifted: event (<name>)` Log line
    says why.
- **Lifting is text.** When a check passes, the host's tool PR removes the gate and logs `gate lifted:
  event (<name>) — by <host>; <type> passed; <evidence>` (*The Log*). **The section stays**, as an Ask stays
  after its decision lifts, so the entry still says what was waited for and how it was checked. A gate
  re-added with the same name reuses its section (or edits it); it never adds a second. A lifted gate
  never re-arms: a later regression is a new entry, or a new gate on a reopened one.
- What is not an event: anything whose telling needs judgment ("the page looks right") is work, an
  entry of its own that the waiting entry is blocked by.

**`<repo>`** (v2.4) — the repo in another repo's id, wherever one is written (`Blocked by`, `Part of`,
`Escaped from`, a Context or `Parts:` ref, a Log line): a name, or `/`-separated components
(`owner/name`, or deeper for a nested group). Each component is ASCII `[A-Za-z0-9_.-]+`, is not `.`
or `..`, and does not start with `-`; a leading `.` is allowed (`owner/.github`). So an id holds no
URL, no host and no path traversal. Before v2.4 a repo was one or two components of `[\w.-]+`,
non-ASCII and `..` among them. In prose (a Context or `Parts:`), a `<repo>#TD-n` is read only at the
start, or after whitespace, an ASCII punctuation mark other than `/ . - @ : # _ \ %`, or a dash or
quote (`— – “ ” ‘ ’ « » …`), and not when its repo's first component is a `TD-n`. After anything else
(a letter, a digit, a combining mark, a zero-width character) it would be the tail of a longer word,
path or URL. A bare `TD-n` is read anywhere but after `#`. So an id whose repo is not the grammar is no ref at all, never a shorter one:
`a/../b#TD-1` and `git@host:o/r#TD-1` name neither `…#TD-1` nor `TD-1`. Refs are written apart:
`TD-5/o/r#TD-6` reads `TD-5` alone, where `TD-5, o/r#TD-6` reads both.
- **A repo is compared case-insensitively** where ids are looked up (`rename_ref`, a resolver) and
  where a Context's refs are de-duplicated (`item_refs()`, `parse_parts()`, a `decide`'s one entry;
  `ref_key()` is the comparison). The text keeps it as written, and an item's key stays byte-exact,
  so two lines differing only in a repo's case have different keys.
- **A repo's origin** (`origin_key(url)`, `origin_path(url)`): a readable origin is an ssh
  (`git@host:path`, `ssh://user@host:port/path`) or https (`https://user:token@host:port/path`) URL
  whose path is the `<repo>` grammar. Its key is `<host>/<path>`, lowercased, every component kept,
  a trailing `/` and `.git` stripped, userinfo and port dropped, so a key never holds a credential:
  `git@forge.example:Acme/Tools.git` is `forge.example/acme/tools`. `origin_path()` is its path part,
  `acme/tools`, which is what a writer puts in another repo's id. Anything else (`file://`, a plain
  local path, another scheme, a path that fails the grammar) gives none: that repo has no origin,
  and a writer names it by its bare name. A consumer's resolver prefers an exact path match to a
  suffix match, so `acme/tools#TD-1` finds `acme/tools` before `group/acme/tools`.

**`Part of`** (v2.1) — `**Part of:** TD-n`, on a part, names its **one** parent in the **same
ledger**; free comment may follow the id (a second id after a comma is a second parent, an error;
anything after the first id with no comma is comment).
A parent is any entry: a design and its builds or live checks, a fix or feature and its subtasks.
It keeps `Blocked by` apart from the parts: a parent's `Blocked by` names only what must really
land first, and its parts keep it unpicked while any is open — what listing them in `Blocked by`
did before. A parent's record carries `parts_open` (its open parts, never in `blocked_by`) and a
part's carries `part_of` (the id as written; ids match by number, `TD-7` is `TD-007`).
- A part's own pickable comes from its own `Blocked by` alone: **a part never inherits its parent's
  ids or gates**. A part that also waits on its parent's blocker, decision or event names it in its own
  `Blocked by`.
- A gate is written on the entry whose work it stops, usually a part; a parent carries one only for
  its own work. A parent's record carries `parts_gates` (v2.4), derived and never written, as
  `parts_open` is: each gate that holds on one of its open **direct** parts (an `until` only while it is
  after today; a retired decision as `decision (<holder>)`), keyed in its canonical form — a person's name as the lowest-numbered part carrying
  it writes it — with the parts carrying it in id order:
  `{"decision (Pat)": ["TD-111", "TD-112"], "event (x)": ["TD-112"]}`. It does not change the parent's
  pickable, which its open parts already decide.
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

**A new entry** (`entry_text(id, title, fields, sections, *, filed=None)`) is that form. Its fields are one line
each, and an empty value is left out. Each section is written `**<name>:** <text>`; a first section
with no name is the unnamed one, written as given. It is refused for an id that is not `TD-n`, a
title that is empty or more than one line, a field that would not read back as one line or is named
twice, and sections that would not read back as given (a section's paragraph that opens in bold
would start a section of its own). A `Blocked by` is written as the writers write it (*The ledger*):
its ids, then its gates in their order; the old form is refused. With `filed` (v2.4: `today`, `who`, `session`, `words`, and
optionally `while`), it writes the entry's Log: the `filed by` line, then one `gate added: <gate>` line
for each gate its `Blocked by` is filed with, in their order, so a gate ages from the day it was filed. A filed entry's `Added` is the date
alone and its Status, if given, is `Open`, since their words go in the Log; either otherwise is
refused, as is a section named Log.

**The Log (v2.4)** is an entry's dated history, a body section led `**Log:**` whose lines follow
the lead, one per line, each `- YYYY-MM-DD: words`, oldest first. It is always the body's **last**
section. `check()` flags a section after it, or a second Log (`log-not-last`), and a line that is not
`- YYYY-MM-DD: words` or that opens with a writer's prefix but not in its shape (`log-line`). Both
are errors on an entry this edit changed (its whole text, not only its header) and information on a
standing one. `check()` reads the Logs of the open entries, not the archive's. A writer that appends to the Log refuses one that is not last, and `edit` and
`archive` put a section they add before it.
- **Every ledger date is the UTC date.** The entry writers take a date, `YYYY-MM-DD`, or an aware
  datetime, which they turn into its UTC date; a naive datetime is refused, since its zone is unknown.
  A fixture carries no datetime, so this rule is held by the unit tests.
- **The writers' lines have fixed shapes**, which `log_line(line)` reads (`log_lines(text)` reads an
  entry's Log). Each line's words after the date are one of these. `who`, a session and a host are
  tokens of `[A-Za-z0-9_.@/-]+`. A gate is `decision (<person>)`, `until YYYY-MM-DD` or `event
  (<name>)`, with `<name>` of `[a-z0-9-]+`. An id is `TD-n` or `<repo>#TD-n`. A quoted label or words
  run from the opening `"` to the line's **last** `"`, so they may hold quotes.
  - `filed by <who>, session <s>[, while <id>]: "<words>"`. `while` names the entry being worked on
    when this one was found; it never affects pickability.
  - `gate added: <gate>`.
  - `gate lifted: decision (<person>) — by <who>; answer "<label>"`, or the same with `event
    (<name>)`. Either may end with one of `; board <repo>`, `; no board item` or `; shared board item
    left open`.
  - `gate lifted: decision (<person>) — by <who>; override: <why>`.
  - `gate lifted: event (<name>) — by <host>; <check-type> passed; <evidence>`.
  - `gate lifted: until YYYY-MM-DD — by <host>; date reached`.
  - `gate lift skipped: <id> no longer carries decision (<person>)`.
  - `kept waiting: <gate> — by <who>; answer "<label>"`.
  - `gate reassigned: decision (<a>) → decision (<b>) — by <who>; <why>`.
  - `archived: <Status word> — <why>`, `reopened — <why>`, and `was: <Status>`.
  - Any other words are a note, kept byte for byte, an unknown tool's line among them.
- **The writer prefixes are reserved:** `filed by `, `gate added:`, `gate lifted:`, `gate
  reassigned:`, `kept waiting:`, `gate lift skipped:`, `was:`, `archived:`, `reopened —`. `note`
  refuses words that begin with one ("reopened the thread" is still a note), and a lifted Status note
  that would is written `note: <text>`.
- **A gate's age** (`gate_age(text, gate)`) is the date of the latest `gate added`, `kept waiting` or
  `gate reassigned` (to it) line for that gate, a person's name compared in any case. With none, it
  is the first Log line's date, then the `Added` date.
- **Status notes become Log lines** through `status_notes_to_log(text)`, which `note`, `archive` and
  `reopen` run before they write:
  - It reads the Status as `<Word>[.] [YYYY-MM-DD] [by <id>] [[:] <tail>] [ — was: <Status>]…`,
    where `<Word>` is a known one: `Open`, `Resolved`, `Superseded`, `Dropped`, or one v2.5's
    `migrate` maps (`Designed`, `Built`, `Partly`, `Live`, `In`, `Done`, `Moved`, `OBE`), in any case,
    not in bold, and followed by its end, a `.`, a `:`, its date or `by`. A date or `by <id>` in the
    head is followed by the end, whitespace or a `:`. So `In progress`, `Open, held`, `**Open** x`,
    `Resolved 2026-10-03.` and `Open 2026-01-01T10:00` are prose, and nothing is lifted from them.
  - The tail becomes **one** Log line, verbatim (a date inside it stays prose), dated by the Status's
    date, else the `**Resolved:**` line's (or an older `Resolved` header field's), else `Added`'s. Each `— was:` segment becomes its own `was:
    <Status>` line, dated by its own date or the same fallbacks.
  - The lines go in among the Log's by date, after any line of an equal date, and the Status is left
    as `<Word>[.] [YYYY-MM-DD] [by <id>]`.
  - An unknown word (a bold or prose Status), a Status with nothing after its head, or text with no
    date to give it: nothing is lifted. `note` leaves such a Status as it is; `archive` and `reopen`,
    which replace it, first copy it whole into one `was: <value>` line, dated by the fallbacks, else
    today.

**The archived entry.** An entry archived as done has the Status `Resolved YYYY-MM-DD` (its why in
the Log's `archived:` line, v2.4; `Resolved YYYY-MM-DD: why` before), and
its Fix replaced by one line, `**Resolved:** YYYY-MM-DD (PR #n) — <pointer>`, which is its body's
only `**Resolved:**` section. The pointer names the doc, test or code that now carries what lasts,
and is optional, as is the PR (with no PR, the parenthesis is left out). An entry archived with
nothing lasting to move keeps its Fix and has the line after it. An entry overtaken by another has
the Status `Superseded YYYY-MM-DD by TD-n` (`… by TD-n: why` before v2.4), and its Why and Fix stay as written. A `Resolved`
header field is the older form of the line: readers still read it, and the writers move it into
the body.

**Edits** (`edit_entry(text, action, *, today, …)`, one of `ENTRY_ACTIONS`) take one entry's text
and return it in canonical form. Each is refused for an entry `canonical()` refuses (a v1 ledger:
*split first*). It is also refused unless the result reads back exactly the change meant, and
nothing else: the same id, title, fields and sections but for the change. An edit that rewrites
the body joins its sections with one blank line, and is refused when an HTML comment there spans
paragraphs. The date is the caller's (`today`, a date, `YYYY-MM-DD` or an aware datetime, written as its UTC date; a time is never written, and a naive datetime is refused), and
an argument the action does not take is refused. What a field's value means (a
vocabulary, a `Blocked by` item, a cycle) is `check()`'s, which the caller runs on the result.
- **set** (`fields`): sets each field, in its place, or adds it where the order puts it; an empty value removes
  it. A value is one line. A `Blocked by` (v2.4) is written with its ids, then its gates in their order;
  it is refused in the old form, and when it adds a gate to an entry whose `Blocked by` still holds the
  old form. A value holding an item the grammar does not read is written as given, for `check()`.
- **note** (`words`): lifts the Status's notes (above), then appends `- YYYY-MM-DD: words` to the
  Log, making it at the end of the body if there is none. It is refused if the words begin with a
  writer's prefix or are more than one line. (Before v2.4 it appended ` YYYY-MM-DD: words` to Status.)
- **edit** (`section`, `words`): replaces the named section's paragraphs, keeping its lead as
  written. A section the body lacks is added after the first Why, else before the first Done when,
  Related or Log, else at the end. It is refused when two sections have the name, and for the Log,
  which only its writers write.
- **archive** (`why`, and `pr`, `pointer`, `as_is`, or else `superseded_by`) lifts the Status's
  notes, then writes the archived entry, above, with the Status `Resolved YYYY-MM-DD` and the Log
  line `archived: Resolved — <why>` (or `Superseded YYYY-MM-DD by TD-n` and `archived: Superseded —
  <why>`). `pr` is the forge's number or None; with None, a pointer holding `#<digits>` is refused,
  since a reader would take that for the PR.
  - An earlier `**Resolved:**` section is replaced, never doubled, and a `Resolved` header field is
    removed.
  - With no section named exactly Fix, the line goes at the end of the body, before the Log, and a
    qualified Fix lead is left alone.
  - A missing Status is added.
  - It is refused if two sections are named Fix.
- **reopen** (`why`): lifts the Status's notes, then sets Status to `Open` and logs `reopened —
  <why>`. The `**Resolved:**` section stays as history, and the caller writes a new Fix with `edit`.
  A `Resolved` header field moves into a `**Resolved:**` section before the Log, never deleted. An
  entry with both is refused: a person merges them. (Before v2.4 the Status became `Open YYYY-MM-DD:
  why — was: <old Status>`.)
- **renumber** (`new`) rewrites the heading's id to another number; Log lines are history, and keep
  theirs. **rename_ref** (`old`, `new`) rewrites that id in `Blocked by`, `Part of` and a `filed by`
  line's `while`, never other Log prose. A local id matches by number; another repo's id matches as
  `<repo>#TD-n`.

Moving a file into `archive/` or back, and the relative links that move with it, are the caller's.

**A change to the canonical form is a minor release**: each consumer reformats its entries once,
when it takes that release.

## The rank

The rank is the order a ledger's people set for its entries; it is the pick order.

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
blank line, a comment below the first entry, a line out of key order, or (v2.3) a key longer than 64
characters (`KEY_NOTE_AT`), which a respace shortens (ℹ). The writer
(`set_rank()`) sets or removes the given ids' lines, places a new line at its key's place, and keeps
every other line byte for byte (a new line takes the file's own line ending). A line for an archived entry is ignored — only open members carry a
card's key — and harmless until its card is wholly archived.

**Rank writes** are made by a tool, each in a commit (and PR) that changes the rank file alone,
under a subject `queue: <action> TD-a, TD-b (<tool>)` (`queue_subject()`, ids in id order):
`rank` sets a moved card's members' lines, `join` gives a card's newcomer the card's key, `prune`
removes the lines of a card whose members are all archived, and (v2.3) `respace` rewrites the keys it
shortens. `subject_kind()` reads every one as `queue`.

**A respace** (`respace(text, ledger, *, fixed, repo)`, v2.3) shortens the file's keys without moving any
line relative to a key it does not own. `ledger` is the ledger's text (its open entries: an archived entry
has no implicit key, and the archive is not read). Its **fixed points** are the keys of the ledger's open
entries that have no line (their implicit keys, `repo` their last component), each key in `fixed` (another
repo's, which a caller sorts beside this file's), the two ends of each band's range of implicit keys for ids
past every id read (`<band>|<type>|<next id>` and `<band>|<type>|999999`, `<next id>` one past the highest id
in the ledger or the rank file), and any line's key equal to one of them or inside such a range. An entry filed
later has an id past every id ever filed, the archive's too, so its implicit key lies inside its band's range;
no rewritten key lies inside one, so a respace never moves a line across where an entry filed later (up to
TD-999999) sorts. The other lines' keys between two consecutive fixed points are rewritten to short
keys inside that same gap, in the same order, equal keys staying equal, each by halving the gap with
`midpoint()`. It returns the file and the ids whose keys changed, and keeps every other line byte for byte; it
refuses a file the reader flags ⚠, and any result that would not keep every order it read. A second respace
of its output changes nothing.

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
`PR #N` (`PRs #12/#13` and `PR #12, #13` give both), and best-effort `branch <name>`. A Context ends where the
next field begins: ` Parts:`, ` Due:`, ` Hide until:`, ` Answers:`, ` Lifts:`, ` Decided:` or ` Closed:`. A `decide`
that lifts a gate names exactly one entry there: every `decide` whose Context names a gate, `decision (<person>)`
or `event (<name>)` (a person's name, an event's name a letter or digit then letters, digits, `_`, `.` and `-`),
since no `Lifts:` means `Go` lifts, and every `decide` that carries `Parts:` or `Lifts:`. The writer refuses,
and the gate faults, any other.

**`Parts:`** (v2.3) — `Parts: TD-15, TD-16.`, right after the Context, ahead of the `Due:`, and only on a
`decide`: the parts of the parent its Context names that its question asks about, a snapshot taken when it was
written (`parse_parts()`, `BoardItem.parts`, `item_record()`'s `parts`): every `TD-NNN` or `<repo>#TD-NNN` in it,
each once, and never one inside a reply's words. The writers write the ids separated by `, `. Its ids are not Context refs, and it is
part of the item key, since a changed snapshot is a different question. What an answer does to the parts it
lists is v2.4's, and so is its writer.

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
- `Lifts: a | b.` (v2.3) — which of a `decide`'s answers lift the gate its Context names, each one of its
  answers' labels (compared case-insensitively), `\|` for a literal bar (`parse_lifts()`, `BoardItem.lifts`,
  `item_record()`'s `lifts`). It is read only after the item's `Answers:` and ahead of its `Decided:`, starting a
  sentence, so a reply's or a `Decided:` text's words are never it, and the answers end where it begins. It is written only when it is not `Go` alone: no `Lifts:` means `Go`. It is part
  of the item key. What a lift does is v2.4's.
- `Decided: <label> (by <person>) (YYYY-MM-DD).` — the person's answer, and (v2.3) who gave it. A decided item
  stays open and due; it now waits on whoever acts on it, not on the person. Only a final `(by <person>)` before
  the date, `<person>` a person's name (below), is split off (`parse_decided_by()`, `BoardItem.decided_by`,
  `item_record()`'s `decided_by`); the rest, never empty, is the label (`parse_decided()` keeps its shape,
  `(label, date)`). A `Decided:` with no `(by …)` stays valid, as every one written before v2.3 is: it names
  nobody. The item key strips the whole field, so a `(by …)` moves no key.

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

**`People:`** (v2.3) — `People: a, b, c`, a preamble line naming the board's people: whose board it is, one
person's or a team's, and so who may answer it. It lists one or more people's names, comma-separated, each
**a person's name**: runs of letters, digits, `_` and `-`, joined by single dots (`pat`, `sam.lee`), compared
case-insensitively. It is read only above the board's first item, and only the first such line
(`board_people(content)`: the names as written, in order, or None for a board with none). A v2.2 reader reads
no preamble line, so it ignores it.

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
- **decide** writes `Decided: <answer> (YYYY-MM-DD).`, or with `by` (v2.3) `Decided: <answer> (by <by>) (YYYY-MM-DD).`,
  replacing an earlier one. It refuses a `by` that is not a person's name, and an answer that itself ends in
  `(by …)`, a typed `Not right: …` included, which the reader would read as who answered;
- **reply** appends a reply tail.

**A new item** (`item_line(text, due, today, session, host, context, *, kind, answers, default, detail, hide_until, lifts)`, v2.3) is one line, `- [ ] [<kind> ]<today> (<head>) — <text> Context: <context>. Due: <due>.` then `Answers: …` where its kind takes them, then a decide's `Lifts: …` when `lifts` names answers other than `Go` alone (each one of its answers, once; written as its answer spells it). Its head is ``session `<name>` on <host>``, ``session `<name>` `` with no host, or `n/a`. The text ends a sentence (a period is added unless it ends in `.`, `?` or `!`), and an empty context is `none`. What a kind takes:
- a `decide` carries two or more distinct answers, at most one marked ` (default)`, and a detail block;
- a `look` carries exactly `Answers: Works | Not right: <what>.`, which the writer writes itself, `Works` marked ` (default)` only when the caller asks;
- an `fyi` carries no `Due:`, and every other kind carries one;
- no kind but `decide` and `look` carries answers.

These are the writer's rules. The reader still reads whatever a line carries. An answer is written `<label>` or `<label> — <consequence>`, with the mark on the label.

The **detail block** is composed from named parts, in the order `Context`, `Question`, `Caveats`, `Recommended`. Each part is one two-space-indented bullet, ``- **<Part>:** <words>``, with any further lines as nested bullets under it. On a `decide` with a default, Recommended opens with that default's label and ` — `. An `Otherwise` text follows the Recommended words on the same bullet as ``**Otherwise:** <words>``. A `decide` needs Context, Question and Recommended. No writer touches the block afterwards.

The writer refuses text, a context, an answer or a detail value that carries a field name, or that is more than one line; a date that is not `YYYY-MM-DD`; a host with no session; and any result the reader would not read back as exactly the item meant, its detail block included.

An answer given elsewhere (on a ledger entry) is written as an already decided `decide` item with `(person)` as its head (`decided_line(…, by=)`), whose `Decided:` names who gave it as **decide** does, with the same refusals (v2.3).

**The form the writers write** (v2.3): an open item line that `item_line()` or `decided_line()` composed, as it stands after any snooze, decide or reply. In short, the line:
- opens `- [ ] ` at column 0;
- carries an optional lower-case kind, a date, and a head that is ``(session `<name>` on <host>)``, ``(session `<name>`)``, `(n/a)`, or `(person)` on a decided line;
- continues with ` — `, text that ends a sentence and names no field, ` Context: <words>.`, on a `decide` optionally ` Parts: <ids>.` (ids separated by `, `, each once), and ` Due: <date>.` on every kind but `fyi`, then, when it has one, ` Hide until: <date>.`;
- may then carry replies, then `Answers:` as *A new item* says a kind takes them (a decided line may carry any or none), then on a `decide` optionally ` Lifts: <labels>.` (each one of its answers, once, and never `Go` alone), then `Decided:`;
- holds nothing else, one space between parts.

Fields inside a reply's words or a `Decided:` text are the person's and are not counted. `item_problem(line)` names why a line is not in that form, or gives None. It checks the item line alone, never its detail block, which stays the person's prose. `canonical_item(line)` rewrites a line into that form, moving `Due:` to its place and spelling it so, and refuses any rewrite that would change the line's item key or lose a word. Consumers persist keys, so a format pass that moved an item's key would break what they hold.

**The gate** is `board_problems(board, old)`: the faults of each open line (every `- [ ]` line at any indent, but an open twin of a closed one) whose item key no line of `old` (open or closed) has. A line an edit only snoozed, decided, replied to or ticked keeps its key, so a line is judged once, when it is added, and a board that was never in the form has no flag day. Two rules join it in v2.3, for who may answer. First come the board's `People:` problems (`people_problems(board)`, line 0 for a missing line): a board with no `People:` line is noted, its text opening `ℹ`, which is no fault (nobody is named who may answer it, so a consumer sends a lift on it to ordinary review); a `People:` line that lists no name, a name that is not a person's name or the same name twice, and a second `People:` line above the first item, are faults. Then a new `decide` line whose Context names a gate, `decision (<person>)`, is faulted when the board has a `People:` line that does not list that person.

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
- **who answered** (v2.3) — `decide`, and `add --decided`, write who gave the answer (`who_answered(board, by)`):
  on a board whose `People:` lists one name, `--by` defaults to it; on one that lists several, `--by` is
  required. A `--by` the list does not hold is refused, and one it holds is written as the list spells it. On a
  board with no `People:` line, `--by` is required and checked as a person's name only. A `People:` line the gate
  faults refuses every answer. The caller supplies the name of the person who answered; a commit's author is
  never one, since an agent commits under the person's name;
- **`archive`** — `archive_closed()` of the board and its archive (created when missing), a two-file write;
- **`fmt`** — `canonical_item()` of every open item line at column 0, a consumer's one-time format pass: the
  lines it can rewrite without changing their key, and each line it cannot, with why, reported and kept;
- **`rank`** — `set_rank()` of the rank file (created when missing), `--set TD-n=<key>` and `--drop TD-n`,
  under `--action rank|join|prune`; or (v2.3) `--action respace --ledger <ledger> [--fixed <key>]… [--repo
  <name>]`, `respace()` of the rank file against that ledger (a file or a v2 directory), which sets and drops
  nothing itself.

Each write prints the commit subject the module gives (`subject()` with `append` for an add, the edit's,
`archive_subject()`, `queue_subject()`) and the paths it changed, or one JSON object with `--json`. `fmt` has no
subject of its own, and a write that changes nothing (a rank line already so) prints none, writing nothing.
`--plan` prints the changes as JSON (each path and its new text) and writes nothing. A write of several files is
both or neither: each is written to a temporary file beside it and renamed into place only when all are built,
and a failed rename puts back the files already replaced. The caller passes what lies outside the files: the
date (`--today`, else the local clock), who replies or answered (`--by`), and the tool and session the subject names
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
**v2.3 gives the board writers** (*Edits*, *The board*): `item_line()` writes every kind with its answers and detail block, `item_problem()`, `canonical_item()` and `board_problems()` say what the writers write, and `archive_closed()` and `archive_subject()` move closed items. Apart from `Hide until:`, `(by …)`, `Parts:` and `Lifts:` (below), the writers change nothing that is read: v2.2 reads every line they write, and a line without a `Hide until:` keys as before. `item_line()` now refuses a call it used to answer with a wrong line (a field name in its text or context, a host with no session, a name holding whitespace or `` ` , ; ) ``, a `today` that is not a date). It writes no `None` host, adds no period after text ending in `?`, `!` or several periods, and drops a context's own final period, so the line it writes for those inputs, and that line's key, differ from v2.2's. A line already on a board keeps its text and its key. v2.3 also ships the board writer, `board.py` (*The board writer*): the package's first file-level writer. It also adds `Hide until:` (*The board*): `snooze` writes it and leaves `Due:` alone, the new `due` edit moves `Due:`, `item_line(hide_until=)` writes it on a new item, `item_record()` gains `hide_until` and `hidden`, and `needs_you()` and `edit_action()` are new. v2.3 also notes a rank key longer than 64 characters and gives the rank its fourth write, `respace` (*The rank*), whose subject `queue: respace …` older readers do not read as `queue`. v2.3 also starts SPEC's grammar appendix (*Appendix: grammar*): the open item line, a person's name and the rank file in EBNF, informative, beside fixtures that are the authority; it changes nothing that is read. v2.3 also names the board's people and who answered (*The board*, *The board writer*): the `People:` preamble line and `board_people()`, `board_problems()`'s `People:` checks (`people_problems()`), and `Decided: <label> (by <person>) (D).`, which `decide`, `decided_line(by=)` and the writer's `--by` write. That is the first of v2.3's three changes to what is read: a `Decided:` written before v2.3 whose text happens to end in `(by <name>)`, `<name>` a person's name, now reads that ending as who answered (`Decided: Go (by Friday) (D).` reads the label `Go`, by `Friday`, who is on no `People:` list, so it fails safe), and its key is unchanged. v2.2 reads a v2.3 `(by …)` as part of the answer's text. A consumer's v2.3 vendor PR shows that none of its boards holds such a line. The second: two fields are added for v2.4's lifts, read, ordered and keyed a release ahead (*The board*): `Parts:`, on a `decide` after its Context, and `Lifts:`, after its Answers. A `Context:` now ends at a ` Parts:` or ` Lifts:` as it does at ` Due:`, so a line that held that prose in its Context before v2.3 reads a shorter Context and fewer refs; and the answers end at a ` Lifts:` that starts a sentence, so a line whose last answer held one reads it apart. v2.2 reads a `Parts:`'s ids as Context refs and a `Lifts:` as part of the last answer, so a consumer writes them only once every reader of its board runs v2.3. The third is `Hide until:`: it is read as a field, a `Context:` ends at a ` Hide until:` as it does at ` Due:`, and the item key strips a `Hide until: D` (*The item key*). So a line that already held the prose `Hide until:` in its Context before v2.3 reads a shorter Context, and one that held `Hide until: D` is keyed without it; no other line's Context or key changes for it. v2.2 reads a `Hide until:` as text (on an item with no `Due:`, as part of its Context), so it shows a hidden item and leaves the field in the item key: a consumer writes the field only once every reader of its board runs v2.3.
**v2.4 adds the Log** (*Ledger entries and their edits*): an entry's dated history as its body's last
section, the writers' fixed line shapes and their reserved prefixes, `log_line()`, `log_lines()`,
`log_problems()` and `check()`'s `log-not-last` and `log-line`, `gate_age()`, `status_notes_to_log()`,
and `entry_text(filed=)`. `note`, `archive` and `reopen` now write the Log and leave the Status a word
and a date: they no longer append to it, and each first lifts the notes already there. Every ledger
date is the UTC date, and the entry writers refuse a naive datetime. Pickability and every field read as before:
v2.3 reads the Log as a body section like any other, and reads the shorter Status as before.
v2.4 also tightens `<repo>` (*The ledger*): an id or ref whose repo is non-ASCII, holds `.` or `..` as
a component, starts a component with `-`, or is a URL is no longer read as another repo's id (it is
an unreadable `Blocked by` item, which keeps the block, and no ref in a Context), while a repo of
three or more components now is. A `<repo>#TD-n` is read only after the characters *The ledger* lists
(a bare `TD-n` still is anywhere but after `#`). `origin_key()`, `origin_path()` and `ref_key()` are new, and a repo's case
no longer makes two refs of one.
v2.4 also gives `Blocked by` its gates (*The ledger*): `until YYYY-MM-DD` and `event (<name>)` beside
`decision (<person>)`, read by `parse_gates()`, and `pickable()` and `check()` now take `today`, the UTC
date, as a required keyword, so each consumer's vendor PR fixes its callers. What changes in what is
read: an `until` whose date today has reached and an `event` were unreadable items and are now gates,
the first lifted by its date; a `decision (<who>)` whose `<who>` is not a person's name (`decision (the
owner)`) is now an unreadable item, and a `decision (designer)` and `hold` are retired items — each still
keeps the block; a decision followed by a comma no longer makes what follows unreadable, but reads it
as the next item; a `decision (…)` that does not open its item (`TD-3 decision (pat)`) is no longer
found inside it, so the item is unreadable and names no holder; and a gate's words are separated by
spaces and tabs only (a no-break space before the `(` makes the item unreadable). Each still keeps the block. `parse_blocked()` keeps its three lists, the third now every item that is neither an
id nor a decision, gates included, so a caller that reads it as before keeps every block. `check()`
gains `priority`, `ask-missing`, `gate-repeated`, `until-past` and `retired`, and the record
`parts_gates`. `new` logs a `gate added` line for every gate, not only decisions, and `new` and `set`
write `Blocked by` in its order and refuse the old form. v2.3 reads every `Blocked by` v2.4 writes, and
an `until` or `event` there as an unreadable item that keeps the block.
v2.4 also adds Event sections (*Events*): `parse_check()`, `parse_event_section()`, `event_sections()`,
`event_problems()`, `CHECK_TYPES` and `CHECK_OUTCOMES`, and `check()`'s `event-section`, `event-check` and
`event-ungated`. Nothing they read was read before: v2.3 reads an Event section as a body section like any
other.

## Appendix: grammar

The grammars below are informative (v2.3: the open item line, a person's name and the rank file; v2.4: `Blocked by` and an Event section; later releases add the rest).
**The fixtures are the authority** (`fixtures/grammar/`): each production has at least one fixture the module
accepts and one it refuses, and a test checks every fixture against these productions, so the two cannot drift.
The notation is the W3C's EBNF (as in XML 1.0): `::=` defines, `|` separates choices, `?`, `*` and `+` follow
what they repeat, `"…"` is literal text, `[…]` a character class (`^` negates it, `#xN` is a code point), and
`(…)` groups. What a production cannot say is said in prose under its block.

### The open item line (v2.3)

An item line as the writers write it (*The form the writers write*): a line `item_problem()` gives None for.
Its line ending is not part of it.

```ebnf
item-line      ::= "- [ ] " ( decide-item | look-item | fyi-item | other-item | decided-item )
decide-item    ::= "decide " date " " head " — " text context parts? due hide? reply* choices lifts?
look-item      ::= "look " date " " head " — " text context due hide? reply* look-answers
fyi-item       ::= "fyi " date " " head " — " text context hide? fyi-reply*
other-item     ::= ( ( "act" | "watch" ) " " )? date " " head " — " text context due hide? reply*
decided-item   ::= ( "decide " date " " any-head " — " text context parts? due hide? reply* ( answers lifts? )?
                   | ( ( "act" | "look" | "watch" ) " " )? date " " any-head " — " text context due hide? reply* answers?
                   | "fyi " date " " any-head " — " text context hide? fyi-reply* answers? ) decided
head           ::= "(session `" head-name "`" ( " on " head-name )? ")" | "(n/a)"
any-head       ::= head | "(person)"
head-name      ::= [^#x20#x9`,;()]+
date           ::= digit digit digit digit "-" digit digit "-" digit digit
digit          ::= [0-9]
text           ::= ( [^#x20#x9] words )? [.?!]
context        ::= " Context: " ( [^.#x20#x9] | "."+ [^.] ) words "."
parts          ::= " Parts: " entry-id ( ", " entry-id )* "."
entry-id       ::= ( repo "#" )? "TD-" digit+
repo           ::= repo-part ( "/" repo-part )*
repo-part      ::= [A-Za-z0-9_] [A-Za-z0-9_.-]* | "." [A-Za-z0-9_-] [A-Za-z0-9_.-]* | ".." [A-Za-z0-9_.-]+
due            ::= " Due: " date "."
hide           ::= " Hide until: " date "."
reply          ::= " — " reply-name ", " date ": " char*
fyi-reply      ::= " — " reply-name ", " date ":" undated
undated        ::= char* - ( char* dated-due char* )
dated-due      ::= non-word due-name " "* date
reply-name     ::= [^#x20#x9,—] [^,—]*
choices        ::= " Answers: " answer ( answer-sep answer )+ "."
answers        ::= " Answers: " answer ( answer-sep answer )* "."
look-answers   ::= " Answers: Works" " (default)"? " | Not right: <what>."
answer         ::= label ( " (default)" )? ( " — " char* )?
label          ::= label-start label-chars
label-start    ::= "\|" | [^|#x20#x9#xA]
label-chars    ::= label-char* - ( label-char* field-at label-char* )
label-char     ::= "\|" | [^|#xA]
answer-sep     ::= " "* "|" " "*
lifts          ::= " Lifts: " label ( answer-sep label )* "."
decided        ::= " Decided:" char* "(" date ")" "."?
words          ::= char* - ( char* field-at char* )
field-at       ::= non-word field-name
non-word       ::= [^A-Za-z0-9_#x80-#x10FFFF#xA]
field-name     ::= "Context:" | "Parts:" | due-name | "Hide until:" | "Answers:" | "Lifts:" | "Decided:" | "Closed:"
due-name       ::= [Dd] [Uu] [Ee] ":"
char           ::= [^#xA]
```

What the productions leave to prose: a `date` is a real day of the calendar, and the line ends in no
whitespace. A field name counts only at a word's start, after a character that is no letter, digit or `_`
(`field-at` names the ASCII ones; the module's word boundary also counts one after any other character that is
no letter, digit or `_`, such as an em dash or a no-break space, so the grammar accepts such a line, which the
module refuses). A
field name that opens the text, the Context or a label is one the grammar accepts and the module refuses: none
opens with one, and an fyi's Context holds no `Due:` either. A `Due:` in an fyi's reply is one only with its
date, not run on into a further digit or letter. A `Decided:` text is the person's: the writers write
` Decided: <text> (<date>).`, and the module reads any spacing around the text, or none. A reply's words are the person's: any other field there is not counted, but they hold
nothing shaped like a reply and end where a trailing field (`Answers:`, `Lifts:`, `Decided:`) starts a sentence
and runs to the line's end, which ends them with `.`, `?` or `!`; nor does a Context hold a reply's shape. A `reply-name` is at most 40 characters, and a `label` holds no ` — ` and does not end in
` (default)`. A `decide`'s answers each have their own label, at most one marked ` (default)`; a decided line's
too, at most one marked. A `Parts:` names each id once. A `Lifts:` names each label once, each one of the item's
answers (compared case-insensitively), and never `Go` alone. A `decide` whose Context names a gate, or that
carries `Parts:` or `Lifts:`, names exactly one entry in its Context.

### `Blocked by` (v2.4)

A `Blocked by` value the reader reads with no item left unread (*The ledger*): `parse_gates()` gives no `bad` and no
`retired` item for it.

```ebnf
blocked-by     ::= blocked-item ( [#x20#x9]* "," [#x20#x9]* blocked-item )*
blocked-item   ::= entry-id | gate
gate           ::= "decision (" person ")" | "until " date | "event (" event-name ")"
event-name     ::= [a-z0-9-]+
```

What the productions leave to prose: an `until`'s date is a real day of the calendar. `designer` is a person's
name by the grammar and a retired role in a decision, which the reader reads as retired. The reader also reads
the words `decision`, `until` and `event` in any case, with any spaces or tabs before a `(` and one or more after
`until`; it drops the value's leading and trailing spaces and tabs and skips an empty item between commas. The
writers write what the grammar says, with `, ` between items, the ids first and then the gates in the order of
`gate`'s choices; an entry names at most one decision per person, one `until` and differently named events.

### An Event section (v2.4)

An Event section the reader reads with no problem (*Events*): `parse_event_section()` gives no `problem` for it.
Its line ending is `\n`; a writer ends the section there.

```ebnf
event-section  ::= "**Event (" event-name "):** " event-words #xA check-line
event-words    ::= [^#x20#x9#xA] char*
check-line     ::= "check: " check
check          ::= pr-merged | file-contains | ref-includes
pr-merged      ::= "pr-merged " repo "#" digit+
file-contains  ::= "file-contains " repo ( "@" ref )? " " path " " quoted
ref-includes   ::= "ref-includes " repo "@" ref " " commit
ref            ::= ref-char+
ref-char       ::= [^#x0-#x20#x7F-#x10FFFF~^:?*[#x5C#%&=+]
path           ::= path-char+
path-char      ::= [^#x0-#x20#x7F-#x10FFFF*?[#x5D#%&=+"#x5C]
quoted         ::= '"' text-char+ '"'
text-char      ::= [^#x0-#x1F#x7F]
commit         ::= hex hex hex hex hex hex hex hex*
hex            ::= [0-9a-f]
```

What the productions leave to prose: a `ref` follows git's `check-ref-format --allow-onelevel` rules and more —
it does not start with `-`, hold `..` or `@{`, or equal `@`; it does not end with `/` or `.`, hold `//`, or have a
component that starts with `.` or ends with `.lock`. A `path` is not absolute, has no empty, `.`, `..` or `.git`
segment and does not start with `-`. A `commit` is at most 40 digits, and a PR's number at most 18. The quoted text runs from its first `"` to the line's last, and
is not spaces alone. The reader also reads any spaces or tabs between the arguments and after `check:`, and drops
those that end a line; no other whitespace separates arguments.

### A person's name (v2.3)

A person's name (*The board*, `People:`), as `is_person()` reads it: who answered, in a `Decided:` text's final
`(by <person>)` before its date (which is otherwise part of the text the `decided` production reads), each name
of a `People:` line, and the person of a `decision (<person>)` gate (whose fixtures, from v2.4, are
`blocked-by`'s). Names compare case-insensitively.

```ebnf
person         ::= person-part ( "." person-part )*
person-part    ::= [A-Za-z0-9_-]+
```

### The rank file (v2.3)

A rank file the reader reads without a flag (*The rank*): `rank()` gives no ⚠ and no ℹ for it.

```ebnf
rank-file      ::= comment-line* ( comment | rank-line* rank-entry? )
comment-line   ::= comment eol
comment        ::= "#" line-char*
rank-line      ::= rank-entry eol
rank-entry     ::= "TD-" [0-9]+ ":" [#x20#x9]+ key [#x20#x9]*
key            ::= [0-9A-Za-z] [0-9A-Za-z_|./-]*
eol            ::= #xD #xA | [#xA-#xD#x1C-#x1E#x85#x2028#x2029]
line-char      ::= [^#xA-#xD#x1C-#x1E#x85#x2028#x2029]
```

What the productions leave to prose: the lines are sorted by key (`key_order()`), no id stands twice, and no key
is longer than 64 characters (`KEY_NOTE_AT`). The last line may end without its `eol`, as `comment` and
`rank-entry` show.

# The ledger and board formats — version 1

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
feature), `Added`, `Status`, `Blocked by`, `Location`. A `Priority`, `Type` or `Blocked by` written
below the header block is still read, and flagged.

**`Fields:`** — a ledger may declare its own fields' vocabularies once, on one preamble line before
the first entry: `Fields: Owner = builder | designer; Kind = build | design-first`. A declared
field's value outside its vocabulary is an error; an undeclared field is read but not validated.
The format's own fields are never redeclared.

**`Blocked by`** — comma-separated items, each `TD-NNN` or `<repo>#TD-NNN` (another repo's
entry; `<repo>` a name or `owner/name`), then optionally `decision (<who>)` last, whose pointer
runs to the end of the line. **Pickable is derived, never written:** an entry is pickable when it
has no `Blocked by`, or every entry it names is archived and it names no decision. An item that
cannot be read, an entry in neither the ledger nor the archive, or another repo's entry the reader
cannot resolve keeps the block. A written `**Pickable:**` line is only a field.

**Pick order:** Priority (High, Medium, Low, then anything else), then Type (debt before feature),
then summary-table order.

**The summary table:** one `| TD-NNN | title | priority | status |` row per entry with a body in
the ledger, in pick order by intent.

**The archive** holds resolved entries, bodies whole, in the same shape.

**`Tracker:`** — an entry mapped from an outside tracker carries its id as `**Tracker:** ABC-123`.
Every edit keeps it byte for byte; what it links to is the importer's.

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
  ` (default)`, the asker's recommendation. A `look` carries exactly `Answers: Works | Not right: <what>.`
- `Decided: <text> (YYYY-MM-DD).` — the person's answer. A decided item stays open and due; it now
  waits on whoever acts on it, not on the person.

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

## Versions

A ledger or board may declare its major version on a preamble line, `Ledgerboard: 1`; none means 1.
A reader that meets a newer major than it knows reads nothing and says so (`version_problem()`, which a consumer calls before it trusts what it parsed — no parser calls it for you). A release of the module
is `v<major>.<minor>`: a minor release reads every file the major's earlier releases wrote.

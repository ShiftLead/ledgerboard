# TD-148: an entry's closing rule is no section's text

**Status:** Draft 4 (rounds 1–3 applied), 2026-11-18 (session lb-designer). Class: **wide** (a change to the published, vendored
format: what `check()` flags, what three readers read and where the writers put what they add; cap 6 rounds,
cadence.md §4.8). The record: [docs/reviews/TD-148.md](../reviews/TD-148.md). In plain words:
[docs/synopses/TD-148.md](../synopses/TD-148.md).

**Entry:** [TD-148](../ledger/TD-148.md), `Part of` TD-124 (the body grammar, [its plan](TD-124-body-grammar.md)),
found by agent-cadence's grinder vendoring v3.3 (agent-cadence TD-283).

## The problem

A v1 ledger is one file, and many put a thematic break, `---`, between entries. Every reader cuts an entry from its
`## TD-NNN:` heading to the next `## ` heading (SPEC *The ledger*), so the break is the last line of the entry
above it, and so the last line of that entry's last section. Where that section is a data field (SPEC *The entry*,
*Data fields*), the break is read as part of it. On `main` (v3.4), for an entry whose body ends
`**Ask:** Should it? Yes or no.`, a blank line, `---`:

- `check()` flags it `field-lines` (`_body_faults()` returns `[('field-lines', 'ask', 'lines', 2)]`): the break
  is text past the Ask's line. With the break above the Ask instead, nothing is flagged.
- The Ask a person reads is `Should it? Yes or no. ---` (`_entry_ask()`): until v4.0 an Ask's later paragraphs are
  read with it (v3.3, *Text a person reads*), so the break reaches the `decide` the gate sweep files.
- With `**Answers:** Go | Not yet` as the last section instead, `entry_answers()` refuses it (*the **Answers:**
  field runs past its line*), so `check()` flags the gated entry `answers-unusable` and the sweep offers no answers.
- With the `**Log:**` as the last section instead, `check()` flags `log-line` (*Log line '---' is not …*), and
  a gate's answered test reads that unreadable Log as answering nothing.
- `migrate_body()` "cures" the Ask by moving the break under a new `**Context:**` lead: an empty-looking Context
  holding only `---`.

The break also survives the move to v2: `split()` writes each entry's text, heading to next heading, as its file,
so every entry of a split ledger that had a break below it ends in `---` (verified on `main`). There the writers
then bury it: `note` on such a file appends its `**Log:**` after the break, which leaves the break in the middle of
the body, the last line of whatever section came before. An entry that ended in its Ask then has the Ask's
`field-lines` for good, and no later rule about trailing lines can reach it.

## What is already settled

- A section runs from its lead to the next lead, trailing blank lines trimmed (SPEC *The entry*); text in a data
  field's section past its line is a fault (`field-lines`, v3.3), and `Answers` and `Lifts` are refused there
  (v3.3, *An entry's own answers*).
- Writes take a v2 directory; a v1 file is read by the reports and `check()` and refused for a write, *split
  first* (SPEC *The ledger writer*). So the v1 half of the problem is all reading; the writing half is the split
  files.
- Canonical form keeps the body byte for byte (SPEC *Canonical form*); changing what it writes is a release each
  consumer reformats its entries for once, which this design does not need: no entry's canonical bytes change.
- The module reads one entry's text without knowing which layout it came from: `body_problems(text)`,
  `entry_answers(entry_text)` and `canonical(text)` take an entry, not a ledger.

## The design

### D1. The closing rule

An entry's **closing rule** is decided on its body with HTML comments dropped (`COMMENT_RE` removed, as
`check()`'s `_entry_texts()` and `entry_answers()` read it; a comment's newlines go with it, so the lines it spans
join). On that text, the body's last line with words (text other than spaces and tabs) is the closing rule when:

- it is a thematic break: up to three spaces, then three or more of one of `-`, `*` or `_`, with any spaces or
  tabs between and after them and nothing else (CommonMark's thematic break), so `--` and `-*-` are not one;
- it stands outside a code fence (fences read on the same text); and
- it is the body's first line, or the line above it is blank (spaces and tabs only).

So `---<!-- t -->`, `---` with a comment-only line after it, and a comment-only line between a blank line and
`---` all leave a rule; `**Ask:** x <!-- c`, a blank line, `-->`, `---` leaves none, since the drop leaves
`**Ask:** x ` directly above `---`, which is then glued (a setext underline).

It is the entry's, not its body's: no section holds it. The **tail**, on any text of the entry, raw or dropped, is
everything after the newline that ends the last line with words above the rule (the whole body when the rule is
its first line): on the raw body that newline is outside every comment, since a comment's newlines are dropped and
the rule was found on what is left, so the cut splits no comment, and the body without the tail holds whole
comments only. The tail is kept verbatim: blank and whitespace-only lines, comments, the rule's line and what
follows it.

- **Readers** read the body without the tail: every section's text (`_entry_sections()`, `_section_spans()`), the
  four body kinds (`check()`, through `body_problems()`), the Log (`log_lines()`, `log_problems()`), the Ask a
  person reads and its context (`_entry_ask()`, `_entry_context()`, the gate sweep's detail block),
  `entry_answers()`, and the Event sections (`event_sections()`), open and archived entries, v1 and v2 alike. Its
  `---` is then read by nothing, as in v1 it separated entries and meant nothing. A reader given an entry's text
  with comments already dropped finds the same rule as the raw readers, since the rule is decided on that text
  for both; the suite checks the two paths agree on every `check` fixture.
- **Writers** keep the tail, verbatim, as the entry's end, after everything they write: a Log made or a line
  appended (`note`, `set`, `lift`, `archive`, `reopen`), a section added or replaced (`edit --section`, the Fix's
  replacement on `archive`), `migrate-body`'s `**Context:**`, and `canonical()`, whose output is unchanged (the
  body byte for byte, the tail after it, as today). Where the tail starts at the rule's own line (the rule was the
  body's first line, its tail the whole body) and a write puts text above it, one blank line goes between them, so it stays a rule; any other tail is
  written as found, so `canonical()` of an unchanged entry inserts nothing.
- **Rendering aside.** A comment-only line between the last words and the rule, indented four spaces or more, is, to CommonMark, a lazy
  continuation of the paragraph above, so a renderer shows the `---` as that paragraph's setext underline; the
  readers still take it as the rule. The format reads text, not its rendering, and both paths agree on it.
- **The one line.** Only the last. A second break above it (`---`, blank, `---`) is text in the section above,
  and flagged where that section is a data field; a break with words after it is text; a `---` glued under a line
  with words (no blank above) is text and stays flagged under an Ask. That last is a choice: CommonMark reads
  such a `---` as the line's setext underline, a heading, so it is the line's, never a separator; the v1 seed
  agent-cadence ships (`files/docs/technical_debt.md`) sets its rules after a blank line, and the case agent-cadence
  TD-283 reports is that form.
- **Every version.** The rule is read in v1, in v2 and from v4.0: a split entry keeps its v1 separator, and a v2
  file written by hand may end with one; telling them apart would need the ledger's layout, which an entry's text
  does not carry.

**Where it travels.** One helper, `_closing_rule(body) -> (body, tail)`, cuts a body (raw, or with comments
dropped) into the body without the tail and the tail (`""` for none), deciding the rule on the body with comments
dropped and mapping the cut back to the text it was given. `_entry_parts()` keeps its three-tuple and
returns the body without the tail, so every reader built on it needs no change; `_entry_tail(text)`, new, returns
the tail of the body `_entry_parts()` cut. `_render()` gains a `tail` argument (default `""`), written after the
body: on the line after it as found; after one blank line where the tail opens with the rule's own line (it was the
whole body) and the body is not empty; and as the body when the body is empty. Each writer that renders an entry passes `_entry_tail()` of the text it was given: `canonical()`,
`edit_entry()` (every action: `note`, `set`, `edit`, `archive`, `reopen`, `lift`), `_logged()`,
`status_notes_to_log()` and `migrate_body()` — every caller of `_render()` but `entry_text()`, whose new entry has
none (on `main`, lines 4808, 5173, 5835, 6210 and 6460); each then runs `canonical()`, which cuts the tail again
and keeps it. `_readback()` returns the tail as a fifth element, so a writer that drops or changes it is refused,
never written. `_body_faults()` keeps its contract (a body in, faults out); `body_problems()` and
`migrate_body()` give it the body without the tail. `_raw_entry_texts()` and `_entry_texts()` cut at `## `
headings as today and need no change.

### D2. `migrate-body` leaves it

`migrate-body` reads the body without the tail (D1), so an Ask whose only text past its line is the tail is clean
and already migrated: neither written nor refused. One with more to move gets its `**Context:**` as today, and the
tail stays the entry's end, after the Context. Its guard compares sections, and no section holds the rule.

### D3. `split()` is unchanged

`split()` writes each entry's text as it stood, rule and all. Dropping the rule there would cure only ledgers split
after the release, and a v1 ledger, read in place by the reports and `check()`, still needs D1; with D1, the rule
in a v2 file is read by nothing, and costs one line. `split_notes()` names nothing new.

### What it changes for a reader

Under v3.4 a closing rule is the last line of the last section. Under D1 that section's text ends before the
tail. A ledger with no closing rule reads, flags and writes exactly as in v3.4. `canonical()` writes no different
byte for any entry. `check()` flags less, never more: the tail held only a break, blank lines and comments, so
taking it out of a section removes text a flag can name and adds none, on the raw and the comment-dropped paths
alike. No item key, canonical form or Log line
changes: a minor release.

## Options weighed

- **The closing rule is the entry's (chosen, D1).** Narrow: one line, at one place, with one meaning; it needs no
  version or layout and keeps every byte.
- **A thematic break ends a data field's section anywhere** (the asker's first suggestion). A break mid-body would
  become a section boundary for the data fields only, and what follows it would belong to no section — a new piece
  of grammar inside the body, in the release line that is making the body strict (TD-124). A break in a Fix's
  prose stays prose under D1, and a break between an Ask and a later paragraph is still that paragraph's
  `field-lines`, which is the fault it names.
- **Only in a v1 ledger.** The split carries the rule into v2 files, where the same flags and the same Ask text
  follow it; and `body_problems(text)` and `entry_answers(entry_text)` read an entry with no ledger to ask.
- **`split()` or `fmt` drops the rule.** `split()` dropping it cures no v1 ledger still in use, which is read in
  place, and makes a split written after the release differ from every split before it; `fmt` dropping it rewrites
  every entry file of every split ledger (a canonical-form change, which each consumer applies once, SPEC
  *Canonical form*) to remove a line D1 already makes inert. Either can follow D1 as its own design if the line is
  ever worth that churn.
- **`migrate-body` removes it.** `migrate-body` keeps every byte of text (its invariant, TD-124 D7), and a v1 file
  is refused for a write, so it reaches no v1 ledger.
- **`check()` notes a closing rule in a v2 file (ℹ).** Every entry of every split ledger would carry the note for a
  line that is read by nothing.

## The SPEC text

The build adds or changes these, word for word.

**The entry** (SPEC *The entry*), a new bullet after *The body* bullet and its sub-bullets, before *Data fields*:

> - **The closing rule** (v3.5). Read on the body with HTML comments dropped (each comment and its newlines
>   removed), the body's last line with words is the entry's **closing rule** when it is a thematic break — up to
>   three spaces, then three or more of one of `-`, `*` or `_`, with any spaces or tabs between and after them and
>   nothing else — outside a code fence, and it is the body's first line or the line above it is blank. Everything
>   after the newline that ends the last line with words above it (on the raw body, a newline outside every
>   comment) is the entry's **tail**, not the body's: no section holds the tail, so a data field before it ends at
>   its line and a Log before it reads its lines, and every reader reads the body without it, on the raw text and
>   with comments dropped alike. A v1 ledger's `---` between entries is the entry above's closing rule, and a
>   split keeps it in that entry's file. Every writer keeps the tail as written, as the entry's end, after what it
>   adds or replaces, with one blank line put above it where a write gives text to a body that was only the tail.
>   Only the last such line is one; a break with words after it, or with words on the line above it (a setext
>   underline), is text.

**Canonical form**, the body's line, changed from *the body byte for byte, with its leading and trailing blank lines
dropped and one trailing newline* to:

> - the body byte for byte, with its leading and trailing blank lines dropped (its tail, v3.5, kept as written as
>   its end), and one trailing newline.

**The body's shape** (v3.3), after its first sentence (*… cut at `## ` headings outside HTML comments:*), the
sentence before the list of kinds gains:

> … `check()` flags four kinds on each open entry's raw body, its tail aside (v3.5, *The entry*), cut at
> `## ` headings outside HTML comments: …

**The ledger writer**, *`migrate-body`* (v3.3), at the end of its bullet:

> An entry's tail (v3.5, *The entry*) is no section's text: an Ask whose only text past its line is the tail is
> already migrated, and a rewritten entry keeps the tail as its end.

**The ledger as a directory**, *Migration*, after *… is its file with trailing blank lines trimmed to one newline.*:

> A `---` between two v1 entries is the first's closing rule (v3.5, *The entry*), kept in its file.

**Versions**, a new paragraph after v3.4's:

> **v3.5 reads an entry's closing rule as the entry's** (TD-148; *The entry*, *Canonical form*, *The body's shape*,
> *The ledger writer*, *The ledger as a directory*): a thematic break that is the body's last line with words, after a
> line with none (or its first line), is no section's text, nor are the lines with no words around it. `check()` no longer flags a data field or a Log that is the last section before it
> (`field-lines`, `log-line`), `entry_answers()` reads an `Answers` or `Lifts` that is the last section before it, the Ask a person reads and its context leave it out, and `migrate-body`
> leaves it in place. Writers put what they add before it, where v3.4 put it after. The last section of an entry
> with one reads without it; an entry without one reads, flags and writes as before. No item key, canonical
> form or Log line changes.

## The fixtures

All invented, no real ledger's text. Each `check()` case calls `check()` (so `body_problems()`), never
`_body_faults()` alone, whose contract is unchanged.

- `fixtures/ledger_edit/` `check` cases (`cases.json`, `check/`): an entry ending in a one-line Ask, a blank line
  and `---` (clean), and the same with `***`, `___`, `- - -` and `   ---` (clean); with three blank lines above the
  `---` (clean); `    ---`, four spaces (`field-lines`: an indented code line); a `---` glued under the Ask line
  (`field-lines`); `---`, a blank line, `---` after the Ask (`field-lines`, the upper one); the Ask, a blank line,
  `---`, a blank line, a paragraph (`field-lines`); the Ask, `---`, a blank line, `<!-- t -->` (clean: the
  comment is in the tail); `---<!-- t -->` after the Ask (clean); `--`, and `-*-`, after the Ask (`field-lines`);
  `* * *` and `_ _ _` (clean); a `---` inside a fence that closes after it (`field-lines` where the fence is in the
  Ask's section; no rule); a CRLF entry ending in its rule (clean); the Ask, `<!-- c -->`, `---`
  (clean: the comment-only line is dropped to an empty one) and the Ask, `    <!-- c -->`, `---` (clean, *Rendering aside*); `**Ask:** x <!-- c`,
  a blank line, `-->`, `---` (`field-lines`, no rule: the drop glues the `---` to the Ask) and `**Ask:** x`, a
  blank line, `<!-- c`, `-->---` (clean: the drop leaves the Ask, a blank line, `---`; the raw tail opens at the
  blank line, splitting no comment); each `check` case also read
  through the comment-dropped path, which flags the same; an entry whose last section is
  its `**Log:**`, then `---` (no `log-line`), and the same with a blank line and `<!-- t -->` after the `---`;
  an `**Answers:**` then `**Lifts:**` as the last sections, then `---<!-- t -->` (no `answers-unusable`); a v1 ledger of three entries joined by `---`, the middle ending in
  its Ask (clean), the last ending in `---` before the file ends (clean).
- `fixtures/ledger_edit/` `canonical` cases: an entry with a closing rule after one blank line and after three
  (each byte for byte); a body that is only `---` (byte for byte); a line of
  two spaces above the rule, one comment-only line above it with no blank line (byte for byte, no blank
  inserted), and a rule with trailing spaces (byte for byte); each run twice (idempotent).
- `fixtures/ledger_edit/` `edit_entry` cases, on an entry ending `**Fix:** …`, three blank lines and `---`: `note`
  (the Log made above the tail, the tail kept); a second `note` (the line appended above it); `edit --section Done
  when` adding a section, and replacing the Fix (each above the rule); `archive` and `reopen` (the Resolved line
  and Log above it); `set` with a Status that moves into the Log (above it); and `note` and `edit --section` on an entry whose body is
  only `---` (the new text, one blank line, then `---`).
- `fixtures/ledger_writer/`: `migrate-body` on a ledger holding an entry whose Ask has a second paragraph and a
  closing rule (the Context made, the tail last, as written) and one whose only extra line is the rule (already
  migrated: not written, not refused); `fmt --check` on a split file ending in its rule (no change), and `--check
  --base` over an edit of it (no `not-canonical`).
- `fixtures/sweep/`: the `decide` the sweep files for a gated entry ending `**Ask:** Should it? Yes or no.` and
  `---` (its text without `---`); and a gated entry ending `**Answers:** Go | Not yet`, `**Lifts:** Go` and `---`
  (its answers offered, no `answers-unusable`).
- `split()` (`fixtures/ledger/`'s split case): a v1 ledger with `---` between entries (each file ending in its
  rule, as today).

## Builds

One build, **B1**: the SPEC text above, the reading at `_entry_parts()` and `_render()` (D1), `migrate-body`'s
case (D2), and the fixtures, in one PR, then a minor release (v3.5, or the next free minor when it lands). Done when
that PR has merged with the SPEC text, the fixtures, and the suite, the fixtures and ruff green.

**Consumers.** None changes its code: each takes the release in its routine vendor PR, agent-cadence first, then
ShiftLead's sync PR (AGENTS.md). Until a consumer vendors it, a closing-rule `field-lines` on a standing ledger is
ℹ (counted against `old`, v3.3) and an error only on an entry an edit changed; agent-cadence TD-283 can vendor v3.3
meanwhile, and its v1 seed (`files/docs/technical_debt.md`) needs no change. No consumer entry is filed.

## Not done

- Removing the rule from split files (D3, *Options weighed*).
- A thematic break anywhere else in a body: it is prose, or text past a data field's line, as in v3.3.
- A v2 file that a v3.4 or earlier writer already wrote past its rule (a Log appended after a split entry's `---`):
  the `---` is mid-body text there, flagged under an Ask as before, and no rule about trailing lines reaches it.
  Its hand fix, in a PR of its own, is to delete the `---` line (or move it last); `check()` names the Ask's
  `field-lines`, so such a file is found.
- An entry whose `---` sits directly under its header block, no blank line between: the header block holds a line
  that is not a field, so `_entry_parts()` refuses it (*Ledger entries and their edits*) and the writers leave it to
  a person, as today.
- TD-135 (v4.0, the strict reader) needs no change: D1 is read in every version, and v4.0 reads a data field as its
  line with the rule already outside the body.

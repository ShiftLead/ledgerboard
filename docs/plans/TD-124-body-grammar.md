# TD-124: the entry body grammar — strict section edges, one-line data

**Status:** Draft 8 (rounds 1–6 applied), 2026-11-16 (session lb-designer). Class: **wide** (a vendored, published format: what opens a
section, what the check flags, a writer that rewrites every ledger; both consumers vendor it; cap 6 rounds,
cadence.md §4.8). Paul chose the two-step release on 2026-11-16 (D7; m-e1c7c9a8ed70). Draft 8 applies rounds 1
to 6; the rounds ended at the cap, round 6's review judging it worth building as it stands. The record: [docs/reviews/TD-124.md](../reviews/TD-124.md). In plain
words: [docs/synopses/TD-124.md](../synopses/TD-124.md).

**Entry:** [TD-124](../ledger/TD-124.md), from Paul's conversation of 2026-11-15, after his hold on TD-119.

## The problem

SPEC *Ledger entries and their edits* cuts an entry's body into sections by a loose rule: a section opens at any
paragraph whose first characters are a bold run, the colon optional and inside the bold or after it, and runs to
the next such paragraph. Data the tools act on lives in those sections (the Ask, an Event's check, TD-119's
answers and lifts), so where a section ends decides what a tool reads, and every new piece of data has needed its
own patch to that edge:

- TD-109 accepted that an `**Ask:**` glued to the paragraph above opens no section and is silently not read.
- TD-111 refuses a bold run mid-text in a board item, the same ambiguity on the board.
- TD-119 spent three rounds and a fourth on `**Answers:**` and `**Lifts:**` glued above or below, trailing
  prose, wrapped lines, an unclosed fence (its F23–F61), before Paul held it for one-line fields.

Every write, every aggregation (ShiftLead's home, Queue and gate sweep; agent-cadence's attention report) and
every merge-gate verdict goes through this package, so structure must be exact. People and sessions read the
files themselves (diffs, a session reading an entry as its instructions, the person on the forge, repairs when a
tool fails), so prose must stay free and readable.

## What the ledgers hold today

Counted on 2026-11-16 from each repo's `origin/main` (open entries / archived):

| | ledgerboard | agent-cadence | ShiftLead |
|---|---|---|---|
| entries | 5 / 109 | 15 / 79 | 85 / 1611 |
| strict leads (`**Name:**`) | 27 / 591 | 89 / 401 | 497 / 9182 |
| leads with no colon | 0 / 3 | 5 / 19 | 44 / 707 |
| leads with the colon after the bold | 0 / 0 | 0 / 0 | 0 / 0 |
| a lead-like line glued to the line above | 0 / 0 | 0 / 0 | 0 / 19 |
| Asks of more than one line | 2 / 1 | 0 / 0 | 0 / 0 |
| unclosed fences | 0 / 0 | 0 / 0 | 0 / 0 |

The glued count is the same on the raw body (D2) as on the comment-dropped text. Nearly every colon-less lead is `**Done when** <text>`; the rest are prose labels that today open a section
nobody reads (`**Fix, in order — each step is usable on its own.**`, `**Which candidate fired (2026-09-11).**`).
The glued lines are archived ones, mostly a `**Resolved:**` written under the Fix with no blank line. The only
multi-paragraph Asks are this repo's (open TD-119's and TD-115's, archived TD-111's; written to v3.2's *sentence then context*).

## The design

### D1. A lead is `**Name:**` at a paragraph's start

A section's **lead** is a bold run whose text ends in a colon, `**Name:**`, opening a line at column 0 that starts
a paragraph (the body's first line, or a line after a blank one), outside a fence. Its **name** is the bold text
without the colon, compared by `field_key` (`Done when` and `done when` are one name); a qualified lead
(`**Fix (to design):**`) is its own name, as today.

Exactly: `**`, then a name of one or more characters other than `*` that does not start with whitespace, then
`:` and `**`; whitespace before the colon inside the bold is trimmed from the name (`**Why :**` is `Why`), and
whatever follows the closing `**` is the section's text (a space is what the writers write). `**:**` has no name
and is no lead.

Gone from the reading (D7 says when): a bold run with no colon (`**Done when** …`), and one with the colon after
the bold (`**Done when**: …`). Each is then no lead, and never silently prose: a paragraph
that opens with a bold run that is not a strict lead stays flagged after v4.0 (`lead-form`, D6), so a person or
session typing the old form is told, never has the text join the Fix unseen. A paragraph may open with words, or
with a strict lead; bold emphasis goes anywhere after its first character. Long-term merit: one form, which
every writer already writes (`entry_text()` writes `**<name>:**`), and which separates a label from emphasis by a
character a person types on purpose. The alternative of a closed set of section names was weighed: it would make
a repo's own sections (`Related`, `Design PR`, `Amendment (…)`) need a declaration, and the colon already does
the work.

### D2. A lead-like line that opens no section is flagged

A line at column 0, outside a fence and outside the header block, that opens with a strict lead (`**Name:**`) but
does not start a paragraph (glued to the line above) is a **glued lead**, flagged by `check()` (`glued-lead`, D6).
It is never read as a section and never silently as prose the tools act on. Its message names both cures: a blank
line above it (it becomes the section its writer meant, which `migrate-body` does), or rewording so the line does not
open with a lead (it stays prose). An `**Ask:**` lead is also a glued lead where it opens a line after up to
three spaces or after `> `, since an indented or quoted Ask would otherwise be silently unread (a quote is a `>` prefix, any spaces after
it, nested or not; a list item `- **Ask:**` stays prose, a stated cost) (TD-119 keeps its own
refusal for `Answers` and `Lifts`). A bold run
anywhere else (inside a line, in a list item `- **Note:** …`, another name after leading spaces) is prose and
flagged by nothing: those are emphasis by their place, and a list of bold labels is common prose.

Every flag here reads the raw body, as the writers' `_entry_sections()` reads it (`edit`, `archive`, the lifts),
not the comment-dropped text: a line that holds only a comment is text, so a lead right after it is glued, since
`edit --section` of the section above would swallow it. **Comments, exactly:** the spans are `COMMENT_RE`'s
matches over the raw body; a line is *inside* a comment when its start lies after a span's start and before its
end (a **comment-only line** is one that holds at least one span clipped to it and nothing but whitespace outside
them, text for the glued rule; a blank line stays blank. A line is first tested for words outside the spans: one
with words after its `-->` is text, else the `-->` line is inside). A lead on a line
inside a comment is a section to `_entry_sections()` and stays one: it is never flagged and never transformed, and
the guard's list keeps it. Fence lines inside a comment open and close fences as `_entry_sections()` tracks them,
so `fence-open` agrees with what the writers swallow. In an Ask's section, comment-only lines and lines inside a
comment are not text past its line (a line with words outside a span is), and the Ask's value has its comments dropped (`**Ask:** <!-- c -->` is
empty). `check()` gets each entry's raw text by cutting the raw file at `^## ` headings outside `COMMENT_RE`'s spans
(the first of an id wins, as `_entry_texts()` keeps) and reads it with `_entry_parts()`; one it refuses is not read for the four kinds.
`migrate-body` reads the same raw body, so a comment-only line before a lead gains the blank line after it. The
indented or quoted Ask has its own message (remove the indent or the quote), and leads match case-insensitively
by `field_key`, so `**ask:**` is an Ask.

A fence that never closes (`FENCE_RE`'s open and close rules: a backtick run closed only by a bare backtick run at
least as long) makes the rest of the body unreadable for leads; `check()` flags it (`fence-open`), so no field is
ever swallowed silently (TD-119's F56).

### D3. Data sits in one-line fields

A **data field** is a section the tools act on. It is its lead's line alone: `**Name:** value`. Any further line in
its section, glued below it or a later paragraph before the next lead, is a fault (`field-lines`, D6), never read.
The value is the line after the lead's bold run, whitespace trimmed. The format's data fields:

- `**Ask:**` — the question, one sentence (*Text a person reads*). What v3.2 kept in the Ask's later paragraphs
  moves to a prose section `**Context:**` (D5) after it. The sweep's item text is the Ask's line, as today's
  joined Ask was for every Ask but this repo's two of several paragraphs; what the item's detail carries from `**Context:**` is not this design (*Not done*).
- `**Answers:**` and `**Lifts:**` — TD-119's, one line in its Draft 4, and data fields only as TD-119 has them:
  on an entry whose `Blocked by` names a decision, flagged by TD-119's own `answers-unusable` through this design's
  field reader, never by `field-lines`; on an ungated entry a repo's own prose `**Answers:**` stays legal. Whichever
  of the two builds merges second moves `entry_answers()` onto the field reader (Builds).

`Context` becomes a reserved name: *Text a person reads* reads an entry's `**Context:**` section as its Ask's
context, so a repo's own prose `Context` is read so too. No ledger on this machine has one today.

`Resolved` is not one: its only reader takes the first date (`_fallback_day`), and 192 archived ShiftLead entries
hold a hand-written Resolved of several lines, prose a person reads. `Design PR` is not one: nothing in this
package reads it, and a single-line rule for it belongs to the repo whose tool reads it.

A repo's own section is prose unless this format names it a data field. A repo whose tool reads a value of its own
keeps it in the header block (one field a line already), or reads its section by these rules; a declaration of a
repo's own data fields was weighed and left until a repo needs one.

### D4. Nested data: a fenced JSON block, only where one line cannot hold it (reserved, not in v3.N)

This is the rule a future field follows; no field needs it, so v3.N's SPEC does not define it, and the build adds
it with its first field, reader and fixtures.

Where a piece of data needs structure one line cannot carry, its section is its lead's line alone, then one fenced
block whose info string is `json`, then nothing before the next lead: `**Name:**`, a blank line, ```` ```json ````,
the object, ```` ``` ````. It parses exactly (`json.loads`) and diffs line by line. No section of today's format needs
it. The **Event section** keeps its own exact two-line grammar (words, then one `check: <type> <args>` line), which
`parse_event_section()` already refuses anything beyond; it is a fixed grammar, not loose prose, and gains nothing
from JSON.

### D5. Prose sections stay free text

`Why`, `Fix`, `Done when`, `Context`, `Location`, and every repo's own section are prose: any Markdown inside the
edges, bullets, fences, bold runs mid-line or in list items, several paragraphs. The tools find only where each
starts and ends (D1) and never read inside except as text to show or carry. The one cost: a paragraph cannot open
with bold emphasis (`**Option A.** …`), before or after v4.0; it is a lead or flagged (`lead-form`). A *bold run*
here is what `LEAD_RE` matches at a line's start; other bold spellings (`__Why:__`, a run with `*` inside) open no
section and are prose by design.

### D6. What `check()` flags

Four new kinds, ℹ on a standing ledger and an error only where an edit makes one new. This is new logic in
`check()`, neither `EDIT_ERRORS`' header scoping (which would leave a body edit's new fault ℹ) nor `TEXT_KINDS`'
whole-text scoping (which would raise every standing flag on a touched entry, and `--check --base` has no
`_same()` to hide it): with `old`, `check()` computes the four kinds on `old`'s texts too. Faults are counted per
**key**, (entry, kind, lead's name), or (entry, kind) for `fence-open`: where the entry has k faults of a key and
`old` had j, the first j are ℹ and the rest errors. A flag's text always carries its ordinal (*the 1st `**Done when**`*,
*the 2nd …*), so faults 1..k are a prefix of any larger set: a write that lowers a count makes no new text, and the
writer's `_same()` and gate agree with `check()`. Where `old`'s entry has `fence-open`, its other three kinds in
the new text are standing for that edit (closing the fence uncovers them; that
cure is never refused), a stated exception to the invariant below. The
lead's name in a flag's text is its key (`field_key`), so respelling `**Done when**` as `**done when**` changes no
text. Where
the entry is absent from `old`'s open entries (a new entry, a `reopen`), its faults count from 0; where `old`'s
entry is one `_entry_parts()` refuses, its faults are standing. With
`old=None` the four are ℹ, as on a standing ledger. One `field-lines` flag per Ask section, whatever runs past it;
an edit inside a faulty section that keeps its count (a third paragraph added to a standing Ask) is allowed.

**Invariant (new against old).** A fault is new exactly when its key's count on the entry is higher than in `old`;
`check()`, `--check --base` and the writer's gate count the same keys on the same raw texts, read as D2 says. So between a vendor PR and its migrate PR, a Log note, a lift
or any edit of an unmigrated entry passes `--check --base`, and only a new fault fails it.

- `lead-form`: a paragraph that opens with a bold run that is not a strict lead (no colon, the colon after the
  bold, no name, or a name opening with whitespace) — a lead until v4.0, flagged for good after it. Its message
  names both cures: the strict spelling (a section) or rewording so the paragraph opens with words (prose).
- `glued-lead`: D2's glued lead.
- `fence-open`: D2's unclosed fence.
- `field-lines`: an `Ask` whose section runs past its lead's line (the v3.2 form's later paragraphs, which
  `migrate-body` moves to `**Context:**`, or a line glued below), or whose value is empty.

TD-119's own refusals stay its own, on its two gated names: whichever of B1 and TD-119's build merges second has
`entry_answers()` share this design's line-reading helper (a field's lead, its line, what runs past it), so the
reasons agree; `Answers` and `Lifts` never join `field-lines` (D3). Until v4.0 the helper reads a lead as
`_entry_sections()` does, non-strict forms included, and a value after one `:` dropped, as TD-119's D1 reads it.
The difference is deliberate: a quoted `> **Ask:**` is this design's `glued-lead`, while a quoted `**Answers:**`
stays prose as TD-119 says, since an unread Answers offers `Go | Not yet`, today's item, and an unread Ask hides
the question.

`check()` reads the open entries alone, as today, so the archive's leads are never flagged; `migrate-body` (D7)
rewrites the archive too, and step 2's gate reads it. A `reopen` of an unmigrated archived entry makes its flags
new and is refused, and so is a `renumber` of an unmigrated entry (its flags' id changes); the cure is `migrate-body` first. Each flag's text names the entry, the kind, the lead's name
and its ordinal, never a line number, so the writer's match of a standing flag survives an unrelated edit. An entry `_entry_parts()` or `canonical()`
refuses (`_entry_parts()` alone; `check()` calls no `canonical()`) is not read for the four kinds, as for the Log's; the v4.0 gate counts it among `migrate-body`'s refused.

### D7. The release: a minor that flags and migrates, then a major that reads strictly

**Paul's choice, 2026-11-16: two steps.** Two releases:

1. **v3.N (minor).** The reader reads as today; `check()` gains D6's four kinds; the ledger writer refuses an edit
   that makes one; and `ledger.py migrate-body` rewrites a ledger, open and archived entries alike, so it flags
   nothing: each non-strict lead takes the strict spelling (`**Done when** x` → `**Done when:** x`; `**Name**:` →
   `**Name:**`; a colon-less label ending in `.` loses the dot for the colon), a glued lead gets the blank line
   above it, and a multi-paragraph Ask keeps its first paragraph, joined to one line, and moves the rest under a
   `**Context:**` lead after it. A lead's rewrite keeps every section's text and order; a glued lead's and an Ask's
   each make one new section boundary, on purpose: the glued line becomes the section its writer meant (in the 19
   archived cases a `**Resolved:**` leaves the Fix), and the sweep's item text for an Ask of several paragraphs
   becomes its first paragraph. **Order:** on the raw body (D2), leads are respelled first, then sections
   split at glued leads, then the Ask split, and the guard's expected list is built in the same order (so a lead
   glued under an Ask is its own section, never joined into the Ask line). An indented or quoted `**Ask:**`
   (`glued-lead`) is refused and kept, for a person to fix: stripping an indent or a quote is not a rewrite this
   writer guesses. **What it
   writes:** `canonical()` of the rewrite, as `fmt` writes, and its plan runs no `gate()`; its PR's `--check
   --base` shows the rewritten entries' standing `TEXT_KINDS` flags as errors, as `fmt`'s does (SPEC v3.1), so
   each migrate PR cures them first or its review reads them as expected. The guard, exactly: from the entry's sections as v3.N reads them, a
   list of (section key, text after the lead's bold run) is built, with only the declared transforms applied (a
   lead respelled, a section split at a glued lead, an Ask split into Ask and Context); the rewrite must read back
   to that list, or the entry is refused and kept. Also refused and kept: an entry with `fence-open`, an Ask whose
   first paragraph holds a list or a fence, an Ask whose lead's line is empty, an entry that already has a
   `Context` section beside an Ask of several paragraphs, and an entry `_entry_parts()` or `canonical()`
   refuses (reported, as `fmt` reports). A label's respelling: the bold text's leading and trailing whitespace trimmed,
   one trailing `.` or `:` dropped, then `:` added inside the bold, and the text after the bold run less its one
   leading `:` (`**Why?**` → `**Why?:**`, `**Done when**: x` → `**Done when:** x`); a label with no name left
   (`**:**`) is refused. The Ask is rewritten exactly where `field-lines` flags it, its lines, first paragraph and *more than one line*
   counted by the one helper `check()` uses, comment-only and in-comment lines left out; an Ask `check()` finds
   clean is never rewritten or refused for its comments. An Ask's first paragraph of more than one line is joined to one line by its lines' whitespace
   collapsed to single spaces; refused instead when it must be joined and holds a comment or a code span, or a line
   after its first that is not plain text (opening with `>`, `|`, a list marker, four spaces or a fence), or a line
   ending in `\` or two spaces (a hard break). An entry with two Ask sections is refused. An Ask's first paragraph ends only at a blank line outside the
   comment spans, so the Context lead never lands inside a comment. Every refusal is tested on the sections after
   respelling and splitting, and only on an entry with a fault or a declared transform; a clean entry is *already
   migrated*, an unreadable one refused (D6). The rewrite edits the raw text in place (a blank line inserted, a lead respelled, the Ask's rest
   moved under its Context lead) and re-joins nothing, so blank-line runs and comments stay as written. The rest of the Ask goes under a `**Context:**` lead written alone on its line, then a blank line,
   then the rest byte for byte; the guard's expected text for Context is that rest as written, leading and trailing blank lines stripped on both
   sides of the comparison. The guard and the
   rewrite read the same raw body (D2), and an entry with a comment inside a region to be rewritten (a label's bold
   run) is refused. Only an entry with at least one declared transform is written or counted as changed; it is
   written in `canonical()` form, which also normalises its header order, line endings and trailing blank lines, as
   expected; any other non-canonical entry is `fmt`'s, *already migrated* here. A respelling that keeps its key is never
   refused. One that changes it (a dropped `.`; trimmed whitespace never changes a key) is refused when its new key is another
   section's key in the entry, or a key the package reads (`why`, `fix`, `done when`,
   `related`, `ask`, `answers`, `lifts`, `context`, `location`, `log`, `resolved`, an `event (…)`, `title`, a
   header name in `HEADER_NAMES`, or a name the ledger's `Fields:` declares). A glued-lead split may raise another
   kind on its own (a glued `**Log:**` becoming a section, `log-not-last`; an `**Ask:**`, `ask-missing`); that
   is the writer's meaning made visible, and the migrate PR shows it. A glued `**Resolved:**` that becomes its own section is then what
   `_fallback_day` reads for an undated Status, as its writer meant. `migrate-body` is
   idempotent: a second run changes nothing.

   **Invariant (migrate-body).** For every entry it writes, the raw reading after equals the reading
   before under the declared transforms, in the declared order, and `check()` raises none of the four on it; every
   entry it neither writes nor would change, it lists as refused or already migrated. So `--check` exits 0 only on a
   ledger where all four are cured. A colon-less label ending in `.` loses the dot, so its section key changes; no reader
   reads such a label. The caller names the commit, as for every ledger write; no subject is the format's and no
   carve-out is added, since `migrate-body` touches no Log and its PR is reviewed like any other. It takes optional
   ids, so a large ledger may migrate in several PRs; the gate below reads the whole ledger.
2. **v4.0 (major), once every consumer's ledger is migrated** (the gate, not v4.0's behaviour: `lead-form` and the
   rest stay flags after it, and `migrate-body` stays for a ledger that meets v4.0 late): `check()` raises none of
   the four, and
   `migrate-body --check` would rewrite no entry and refuses none, open or archived (its exit 1 when it
   would change or refuses any, as `fmt`'s; `--plan` prints the changes as every write's plan does, `refused` as
   `{path, why}`). B3 is blocked by one `pr-merged <repo>#<n>` event per consumer migrate PR; its builder then runs
   `migrate-body --check` on each consumer's `origin/main` ledger, read through refs, and records the result in
   B3's PR. This package runs nothing of a consumer's. A ledger's `Ledgerboard: 2` declares its directory form, not this reading,
   and stays: a migrated ledger reads the same under v3.N and v4.0. The reader reads D1 and D3 alone: a
   non-strict lead is prose, a data field is its line. Nothing in a migrated ledger reads differently.

The way not taken, **one v4.0** that reads strictly at once, makes every unmigrated consumer ledger read differently
on the day it vendors (44 open ShiftLead `Done when` sections joining their Fix), and needs the migrate run in the
same vendor PR. The two-step costs one release more and lets each repo migrate in a PR of its own, checked by the
same `check()` before the reading changes.

**The order.** This repo: v3.N's PR, its release, then this repo's own `migrate-body` PR. agent-cadence: its vendor
PR, then its migrate PR (agent-cadence's entry, filed there on the release). ShiftLead: the same (ShiftLead's
entry). Then v4.0 here, then each vendor PR. No item key, canonical form or Log line changes in either release.

### D8. What this design does not touch

The board's item files (their own v3.0 grammar; TD-111 holds their bold head) and the header block (one field a
line already). The Log keeps its grammar, a strict lead `**Log:**` then dated lines.

## The SPEC text

Step 1, v3.N, the next untagged minor when B1 merges (v3.3 if untagged then, as TD-115's and TD-119's builds
share it), adds or changes these, word for word. Step 2's text (v4.0) is written by B3, from D1 and D3: the lead
bullet's v3.N clause goes (the two old forms stay `lead-form`, never *Retired words*), `ask-missing` reads the Ask section (today
`ASK_RE` matches an `**Ask:**` at any line's start, glued or fenced), and `entry_text()`'s refusal of a section
paragraph that opens in bold narrows to one that opens with a strict lead.

**In *Ledger entries and their edits*, *The entry*, the body bullet** becomes:

> - **The body** is everything after the header block. It is cut into **sections**. A section's **lead** is a bold
>   run `**Name:**` (a name of one or more characters other than `*`, not starting with whitespace, its trailing
>   whitespace trimmed, then the colon), opening a line at its first column that starts a paragraph; a
>   paragraph opens the body or follows a blank line. The section runs through every following paragraph up to
>   the next lead, so a Fix keeps its bullets. A paragraph inside a code fence opens no section: a fence opens on a
>   line of three or more backticks or tildes (indented at most three spaces), and closes on a bare line of the
>   same character at least as long. (v3.N: a paragraph opening with a bold run with no colon, `**Done when**`,
>   or with the colon after it, `**Done when**:`, is still read as a lead until v4.0, and `check()` flags it,
>   `lead-form`.)
>   - A lead's name is its bold text less the colon, matched by `field_key`: `Done when:` and `done when:` are one
>     name.

(its sub-bullets on qualified leads, a body lead named like a field and the unnamed section kept.)

**After that bullet, a new one:**

> - **Data fields** (v3.N). A section the tools read a value from is a **data field**: its lead's line alone,
>   `**Name:** value`, the value the line after the lead's bold run, whitespace trimmed. The format's are
>   `Ask`; where *An entry's own answers* is in this SPEC, `Answers` and `Lifts` too, as that section reads them
>   (on a gated entry, flagged there, never `field-lines`). Anything after the lead's line in a data field's section (a line glued below it,
>   or a later paragraph before the next lead), or an empty value, is a fault, `field-lines`. `Context` is a
>   reserved prose name, read as the Ask's context (*Text a person reads*). An Event section (*Events*) keeps its own two-line grammar. Every other section is prose, read only
>   as text.

**In *Ledger entries and their edits*, after *The Log (v2.4)* paragraph**, a new paragraph:

> **The body's shape** (v3.N). `check()` flags four kinds on each open entry's raw body, cut at `## ` headings
> outside HTML comments: `lead-form`, a paragraph that opens with a bold run that is not a lead (no colon, the
> colon after the bold, no name, or a name opening with whitespace; read as a lead until v4.0), its message naming
> the strict spelling and rewording; `glued-lead`, a line at its first column, outside a fence and the header
> block, that opens with `**Name:**` but starts no paragraph (a comment-only line above it is text), and an `Ask`
> lead after up to three spaces or after a `>` prefix (any spaces after it, nested or not); `fence-open`, a fence the body never closes (fence lines inside a
> comment count, as the writers read them); and `field-lines`, an `Ask` with text past its line (comment-only and
> in-comment lines aside) or with no value once comments are dropped. A lead on a line inside a comment is never
> flagged. A bold run anywhere else is prose. Faults are counted per key (entry, kind, and the lead's `field_key`;
> entry and kind for `fence-open`), each flag's text carrying its ordinal (*the 1st*) and no line: with no `old`
> all are ℹ; with `old`, the count `old` has of a key is ℹ and the rest errors, an entry absent from `old` counting
> from 0, one `old` cannot read all ℹ, and where `old` has `fence-open`, its other three kinds ℹ. The
> archive is not read. The ledger writer refuses an edit that makes one new; `migrate-body` cures or refuses each.

**In *Text a person reads*, the Ask bullet:** *the Ask's text after its `**Ask:**` lead, its first paragraph the
sentence (…), `question=True`, and its later paragraphs the context.* becomes

> the Ask's line after its `**Ask:**` lead, the sentence, `question=True`, and the entry's `**Context:**`
> section, where it has one, the context (v3.N: an Ask is a data field, *The entry*; until v4.0 an Ask's later
> paragraphs are still read as its context, and flagged, `field-lines`);

**In *The ledger writer*, after `fmt`'s bullet**, a new one:

> - **`migrate-body`** (v3.N) — every entry of the ledger and its archive rewritten so `check()` flags no
>   `lead-form`, `glued-lead` or `field-lines`, keeping each section's text and order as v3.N reads them: a lead
>   with no colon gains one inside the bold (`**Done when** x` → `**Done when:** x`; a label's trailing `.` or `:` inside the
>   bold, and one `:` after it, give way to the colon), a glued lead gains a blank line above it, and an `Ask` of more than
>   one line keeps its first paragraph joined to one line and moves the rest, as written, under a
>   `**Context:**` lead after it (an entry that already has a `Context` section is refused). A glued lead's and
>   an Ask's rewrite each add one section boundary, on purpose; every other section reads back the same, or the
>   entry is refused and kept, as is one with `fence-open` and an Ask whose first paragraph holds a list or a
>   fence, an Ask whose lead's line is empty, or one `_entry_parts()` or `canonical()` refuses; the rest are
>   written as one write. The guard compares (section key, text after the lead) with the v3.N reading under the
>   declared rewrites alone, on the raw body as the writers read it, a lead inside an HTML comment left as it is;
>   a respelling that changes a lead's key to another section's key, a name this format reads or a header name is
>   refused (an Ask's first paragraph ending only at a blank line outside comment spans; every refusal only on an
>   entry with a fault or a declared transform, a clean entry being already migrated), as is a comment inside a
>   label's bold run, an Ask that must be joined and holds a comment, a code span
>   or a line that is not plain text, and an entry with two Asks;
>   the Context lead is written alone on its line, a blank line, then the rest byte for byte; only an entry with a
>   declared rewrite is written or counted, in `canonical()` form. A label's respelling
>   trims leading and trailing whitespace and one trailing `.` or `:` from the bold text, adds `:` inside it, and
>   drops one `:` after it; a label with no name is refused. A second run changes nothing. Optional ids limit it to
>   those entries. Leads are respelled first, then glued leads split, then the Ask; an indented or quoted Ask is refused, as is
>   a respelling to a name this format reads that the label was not; the result is `canonical()`'s, and no
>   `gate()` runs. `--plan` prints the plan as every write does; `refused` lists `{path, why}`; exit 1 when it
>   refuses any, or with `--check` when it would change any, as `fmt`.

**In *Versions*, a paragraph of its own after the newest:**

> **v3.N makes the body's edges strict, in two steps** (*The entry*, *The ledger*, *Text a person reads*, *The
> ledger writer*): a lead is `**Name:**`; `Ask` is a data field, one line; `check()` flags `lead-form`, `glued-lead`, `fence-open` and `field-lines`, and the writer
> refuses an edit that makes one; `migrate-body` rewrites a ledger so it flags none. The reading does not change:
> a colon-less lead is still a lead and an Ask's later paragraphs are still read, until v4.0, which reads the
> strict form alone once every consumer's ledger is migrated. `migrate-body` changes what is read only where it
> adds a boundary: a glued lead becomes its own section, and an Ask of several paragraphs is read as its first. An Ask's context moves to a `**Context:**`
> section. No item key, canonical form or Log line changes.

## The fixtures

All invented. `fixtures/ledger_edit/check/`: one case per kind, flagged and clean — `**Done when** x` and
`**Done when**: x` (`lead-form`), a `**Fix:**` glued under the Why (`glued-lead`), an unclosed backtick fence and a
`~~~` "closed" by backticks (`fence-open`), an Ask with a second paragraph and an Ask with a line glued below (`field-lines`), an indented `   **Ask:**` (three spaces) `> **Ask:**`, `>**Ask:**` and `> > **Ask:**` (`glued-lead`), a four-space `    **Ask:**`
(clean: an indented code block's line), a lead glued after a fence's closing line
(`glued-lead`), `**Why**` at a paragraph's start (`lead-form`); a lead right after a comment-only line (`glued-lead`, raw reading); clean: `- **Note:** x` in a Fix, `a **b:** c` mid-line, `  **Fix:**` indented, a fenced
`**Ask:**`, a one-line Ask with a `**Context:**` after it. `fixtures/ledger_writer/`: `migrate-body` over a ledger
holding each curable kind (its `after/` the rewrite; the sections read the same before and after), a glued
`**Resolved:**` becoming its own section, an entry with `fence-open` refused and kept, an Ask with a `Context`
already refused, an Ask whose first paragraph holds a list refused; `--plan` writing nothing; `--check` exiting 1 on an unmigrated ledger and 0 on a migrated one;
`** Why:**` respelled; `**:**` refused; `**Log.**` refused (a read name); an indented Ask refused; an
Ask with a `**Fix:**` glued below (the Fix its own section, the Ask one line); `run` and `--check` on a refused
entry; a
second run changing nothing; `**Why?**` respelled; `**Done when.**` refused (its key would become a read one); a wrapped first Ask paragraph joined; an
archived entry rewritten; a qualified lead left alone; `reopen` of an unmigrated archived entry refused; and the writer refusing an edit that makes
each kind new, while a Log note on an entry already flagged is written; `check(old)` raising a standing flag as ℹ,
not an error, when the entry's text changed; an edit adding a second `**Done when** y` to an entry with one
standing (an error, *the 2nd*); two errors against `base`, then one fixed (not refused); a fence closed by
hand uncovering a glued lead (not refused); an Ask whose lead's line is empty refused; an Ask holding a code span
refused; a respelling to `**Why:**` beside a Why refused; a clean but non-canonical entry left alone; the Context
layout in `after/`; a lead inside a multi-line comment (not flagged, kept); a comment opening mid-line over a lead;
a fence marker inside a comment; an Ask whose first paragraph holds a comment with a blank line in it (the Context
lead placed after the comment, never in it); an Ask with a comment-only line below and a `**Fix:**` glued under it (the Ask clean and untouched, the Fix
split off); an Ask with `<!-- c --> more words` below (`field-lines`); an indented `  <!-- c -->` line (comment-only); a comment-only line before a lead
through `migrate-body` (the blank line added); a respelling whose key would clash refused; a new entry and a
`renumber` against an absent `old`.

## Builds

Filed on Paul's go, after the rounds: **B1** v3.N (D1–D6's check, the writer's refusal, `migrate-body`, the SPEC
text, the fixtures); **B2** this repo's migrate PR; **B3** v4.0's strict reader, blocked by one `pr-merged`
event per consumer migrate PR, its builder recording D7's gate on each (D7). B1, or TD-119's build if it merges second, also
moves `entry_answers()` onto the field reader (D3). B1 regenerates the existing fixtures' expected `check()`
output, which gains `lead-form` ℹ where they hold `**Done when** …`. B1 also has `_entry_ask` drop comments from the Ask it joins (the
sweep's item text), its one-line reading coming with B3; and gives `new` and `set` a `--context FILE` that writes the
`**Context:**` section right after the Ask (and B1 has `edit --section Context` add it after the Ask, where
the entry has one; `_section_place` would put it after the Why). **B4** the sweep's item
carries the entry's `**Context:**` as its detail context (this repo's two multi-paragraph Asks lose their context on the item from their migrate until
B4). On the go, the designer files with each consumer's question seat (`ao td add`): its vendor PR of v3.N; its
own writers of an Ask, which accept several paragraphs today and must write one line and a `**Context:**`; and its
`migrate-body` PR, which B3 waits on. Each consumer's migrate is an entry in its own ledger, named
in B1's Fix.

## Not done

- **No closed set of section names** (D1): the colon marks a lead.
- **The sweep's detail from `**Context:**`**: B4, a build of its own.
- **JSON fields** (D4): reserved until a field needs one.
- **The board** (D8).

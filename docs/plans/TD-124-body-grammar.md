# TD-124: the entry body grammar — strict section edges, one-line data

**Status:** Draft 1, 2026-11-16 (session lb-designer). Class: **wide** (a vendored, published format: what opens a
section, what the check flags, a writer that rewrites every ledger; both consumers vendor it; cap 6 rounds,
cadence.md §4.8). Rounds: not started; one choice waits on Paul first (D7, *a two-step release or one major*).
The record: [docs/reviews/TD-124.md](../reviews/TD-124.md), once a round runs. In plain words:
[docs/synopses/TD-124.md](../synopses/TD-124.md).

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

Nearly every colon-less lead is `**Done when** <text>`; the rest are prose labels that today open a section
nobody reads (`**Fix, in order — each step is usable on its own.**`, `**Which candidate fired (2026-09-11).**`).
The glued lines are archived ones, mostly a `**Resolved:**` written under the Fix with no blank line. The only
multi-paragraph Asks are this repo's (TD-119's and TD-115's, written to v3.2's *sentence then context*).

## The design

### D1. A lead is `**Name:**` at a paragraph's start

A section's **lead** is a bold run whose text ends in a colon, `**Name:**`, opening a line at column 0 that starts
a paragraph (the body's first line, or a line after a blank one), outside a fence. Its **name** is the bold text
without the colon, compared by `field_key` (`Done when` and `done when` are one name); a qualified lead
(`**Fix (to design):**`) is its own name, as today.

Gone from the reading (D7 says when): a bold run with no colon (`**Done when** …`), and one with the colon after
the bold (`**Done when**: …`). Each is then prose, part of the section above it. Long-term merit: one form, which
every writer already writes (`entry_text()` writes `**<name>:**`), and which separates a label from emphasis by a
character a person types on purpose. The alternative of a closed set of section names was weighed: it would make
a repo's own sections (`Related`, `Design PR`, `Amendment (…)`) need a declaration, and the colon already does
the work.

### D2. A lead-like line that opens no section is flagged

A line at column 0, outside a fence and outside the header block, that opens with a strict lead (`**Name:**`) but
does not start a paragraph (glued to the line above) is a **glued lead**, flagged by `check()` (`glued-lead`, D6).
It is never read as a section and never silently as prose the tools act on. A bold run anywhere else (inside a
line, in a list item `- **Note:** …`, after leading spaces) is prose and flagged by nothing: those are emphasis by
their place, and a list of bold labels is common prose.

A fence that never closes (`FENCE_RE`'s open and close rules: a backtick run closed only by a bare backtick run at
least as long) makes the rest of the body unreadable for leads; `check()` flags it (`fence-open`), so no field is
ever swallowed silently (TD-119's F56).

### D3. Data sits in one-line fields

A **data field** is a section the tools act on. It is its lead's line alone: `**Name:** value`. Any further line in
its section, glued below it or a later paragraph before the next lead, is a fault (`field-lines`, D6), never read.
The value is the line after the lead's bold run, whitespace trimmed. The format's data fields:

- `**Ask:**` — the question, one sentence (*Text a person reads*). What v3.2 kept in the Ask's later paragraphs
  moves to a prose section `**Context:**` (D5), which the sweep's item and a consumer's writer read as the
  detail's context.
- `**Answers:**` and `**Lifts:**` — TD-119's, already one line in its Draft 4.
- `**Resolved:**` — an archived entry's date, PR and pointer, which `archive` already writes on one line.
- `**Design PR:**` — the design's PR list, which `ledger.py edit --section "Design PR"` already writes on one line.

A repo's own section is prose unless this format names it a data field. A repo whose tool reads a value of its own
keeps it in the header block (one field a line already), or reads its section by these rules; a declaration of a
repo's own data fields was weighed and left until a repo needs one.

### D4. Nested data: a fenced JSON block, only where one line cannot hold it

Where a piece of data needs structure one line cannot carry, its section is its lead's line alone, then one fenced
block whose info string is `json`, then nothing before the next lead: `**Name:**`, a blank line, ```` ```json ````,
the object, ```` ``` ````. It parses exactly (`json.loads`) and diffs line by line. No section of today's format needs
it. The **Event section** keeps its own exact two-line grammar (words, then one `check: <type> <args>` line), which
`parse_event_section()` already refuses anything beyond; it is a fixed grammar, not loose prose, and gains nothing
from JSON.

### D5. Prose sections stay free text

`Why`, `Fix`, `Done when`, `Context`, `Location`, and every repo's own section are prose: any Markdown inside the
edges, bullets, fences, bold runs mid-line or in list items, several paragraphs. The tools find only where each
starts and ends (D1) and never read inside except as text to show or carry.

### D6. What `check()` flags

Four new kinds, each an error on an entry the edit changed (its whole text, `TEXT_KINDS`, `EDIT_ERRORS`) and ℹ on a
standing ledger, the writer refusing only a flag the edit makes new (as for every edit flag):

- `lead-form`: a paragraph that opens with a bold run with no colon, or with the colon after the bold — a lead today,
  prose from D7's major step. Its message names the strict spelling.
- `glued-lead`: D2's glued lead.
- `fence-open`: D2's unclosed fence.
- `field-lines`: a data field (D3) whose section runs past its lead's line, or an `Ask` from the v3.2 form (its
  later paragraphs, which `migrate` moves to `**Context:**`).

TD-119's own refusals of a glued or indented `Answers` or `Lifts` and of a field running past its line fold into
these: its build, if it lands first, keeps them in `entry_answers()`; this build has `entry_answers()` call the
shared reader, so the reasons agree.

### D7. The release: a minor that flags and migrates, then a major that reads strictly

**Recommended, and Paul's to choose (an ask: a major version).** Two releases:

1. **v3.N (minor).** The reader reads as today; `check()` gains D6's four kinds; the ledger writer refuses an edit
   that makes one; and `ledger.py migrate-body` rewrites a ledger, open and archived entries alike, so it flags
   nothing: each non-strict lead takes the strict spelling (`**Done when** x` → `**Done when:** x`; `**Name**:` →
   `**Name:**`; a colon-less label ending in `.` loses the dot for the colon), a glued lead gets the blank line
   above it, and a multi-paragraph Ask keeps its first paragraph, joined to one line, and moves the rest under a
   `**Context:**` lead after it. Every rewrite keeps each section's text and order as v3 reads them, so nothing a
   tool reads changes; it is refused where it cannot (an unclosed fence: a person closes it). Its commit is
   `ledger: migrate-body v3.N (<n> entries)`, which the merge gate's tripwire exempts as it does `migrate`.
2. **v4.0 (major), once agent-cadence's and ShiftLead's ledgers check clean.** The reader reads D1 and D3 alone: a
   non-strict lead is prose, a data field is its line. Nothing in a migrated ledger reads differently.

The other way, **one v4.0** that reads strictly at once, makes every unmigrated consumer ledger read differently
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

Draft 1 gives the change in outline; the exact text is written once D7 is chosen, before round 1.

- *The entry* (SPEC, *Ledger entries and their edits*): the lead bullet's *the colon optional* and its example
  `**Done when**` become D1's rule; a new bullet for data fields (D3) and the JSON block (D4).
- *The ledger*: `check()`'s kinds gain D6's four.
- *Text a person reads*: the Ask bullet's *its later paragraphs the context* becomes the `**Context:**` section.
- *The ledger writer*: `migrate-body`.
- *Versions*: a paragraph for v3.N, and later one for v4.0.

## The fixtures

Outline, written exactly with the SPEC text: `fixtures/ledger_edit/check/` cases for each of D6's kinds, flagged
and clean (a list item's bold label and a mid-line bold run not flagged); `fixtures/ledger_writer/` cases for
`migrate-body` (each rewrite, the read-back equal, an unclosed fence refused) and for the writer refusing an edit
that makes each kind; all invented, never copied from a ledger above.

## Builds

Filed on Paul's go, after the rounds: **B1** v3.N (D1–D6's check, the writer's refusal, `migrate-body`, the SPEC
text, the fixtures); **B2** this repo's migrate PR; **B3** v4.0's strict reader, blocked by an event that
agent-cadence's and ShiftLead's ledgers check clean. Each consumer's migrate is an entry in its own ledger, named
in B1's Fix.

## Not done

- **No closed set of section names** (D1): the colon marks a lead.
- **The board** (D8).

# TD-119: the gate sweep offers the entry's own answers

**Status:** Draft 6, 2026-11-17 (session lb-designer). Class: **wide** (a vendored, published format: two new
entry fields the gate sweep reads, a new reader, a new `check()` flag the writer refuses on, which both consumers
vendor; cap 6 rounds, cadence.md §4.8). Rounds 1–3 ran 2026-11-15 (round 3 as TD-122, Paul's *One more round*,
#361). Their recurring topic was where the multi-paragraph answer sections start and end (F23, F30, F33, F38, F41,
F42, F49); Paul answered round 3's end-of-rounds item *Hold: Make Answers and Lifts each a single line, as your
fallback says; the boundary rule has been patched three rounds running.* Draft 4 is that revision, run as TD-125
with round 4 (2026-11-16): each of `**Answers:**` and `**Lifts:**` is one line, and the section-edge rule itself is
TD-124's, not patched here. Paul bought round 5 (TD-127, 2026-11-16); Draft 5 is its fixes. Round 5's F72, which keeps all three of D1's refusals
this reader's beside TD-124's flag, and F73, an overlapping scan for a field inside the line, were build-changing
and applied, then read by round 6. Paul bought round 6, the last the cap allows (TD-137, 2026-11-16); its review (R19) read F72–F80, judged the design worth building as it stands and raised nothing build-changing, so the rounds end by the stop rule at the cap; Draft 6 is its nine minor fixes (F81–F89) and the closing fact-check's seven (F90–F96, none changing what is built). Build-changing by the design reviews, rounds 1–6: 2, 0, 3, 2, 2, 0. The record:
[docs/reviews/TD-119.md](../reviews/TD-119.md). In plain words: [docs/synopses/TD-119.md](../synopses/TD-119.md).

**Entry:** [TD-119](../ledger/TD-119.md). Asked for by ShiftLead's techlead (m-988ff211d5bb), from the gate sweep
ShiftLead ran onto this repo's board in PR #355.

## The problem

When an entry waits on a person (`decision (<p>)`) and no board item asks for it, the gate sweep files one: a
`decide` whose text is the entry's Ask and whose answers are always `Go | Not yet` (SPEC *The gate sweep*,
`SWEEP_DECISION_ANSWERS` in `_sweep_item()`). Many Asks ask something else. In #355, ShiftLead's TD-1879 asked
*one more round, or go ahead now?* and named Hold too; ShiftLead's TD-1404 asked for *Works* or *Not right: <what it
printed>*. Both items offered Go | Not yet, so the person could not press the answer the question asks for, and a
*Works* typed as a reply would not lift the gate, since only `Go` lifts an item with no `Lifts:`.

The sweep cannot know an entry's answers today because the format gives them no home: SPEC *Text a person reads*
says *An Ask carries no answers in this format; a ledger that keeps its own `Answers` (a repo's own field or
section) passes them*. ShiftLead kept one such section, on its TD-1845 (`**Answers:** Go (default) — the
grinders build it | One more round — … | Hold: <note> — …`), in the board's `Answers:` form; that entry was archived on 2026-11-16, and no open entry on this machine's roster holds an `**Answers:**` or `**Lifts:**` lead today. No ledger on this
machine's roster declares an `Ask` or `Answers` header field, and none writes a `**Lifts:**` section.

## What is already settled

- **The board's answers** (SPEC *The board*, the `Answers:` and `Lifts:` bullets): a `decide`'s answers are read by
  `parse_answers_value()` and each by `split_answer()` into label, consequence and the ` (default)` mark; a form
  (`Hold: <note>`) is filled by the answer; `Lifts:` names which answers lift, each by its whole label (a form by its offered label, `Hold: <note>`,
  whose fills then lift), and an item with no `Lifts:` lifts on `Go` alone (`_lifting()`); the two waiting-only answers, `Keep waiting` and `Not yet`, never lift.
  `item_file()` refuses, for a `decide`, fewer than two answers, two answers of one label, an answer that is a
  label then a bare `—` with no consequence (`a —`, by its read-back rule), a `Lifts:` that is empty, repeats a label, names a waiting-only answer or names a label not
  offered, two forms with one head and a form as the default; it takes the default as an index (`default=`), and
  refuses any ` (default)` mark written in an answer (the mark is the writer's). It takes a literal `|` in an
  answer and escapes it.
- **What an answer does** (`closes()`): a waiting-only answer closes the item and keeps the gate (the host writes
  `kept waiting`); a lifting answer on an item about this repo's own entry closes it and lifts the gate (an item about another
  repo's entry, `<repo>#TD-n`, stays open, and its lift goes through *an answer owing a lift*); any other answer is a work order and leaves the
  item open, `decided`, which still covers the gate, so the sweep does not ask again.
- **The entry's body** (SPEC *Ledger entries and their edits*): a body section is kept byte for byte by
  `canonical()`, so a new section name changes no canonical form and no item key. `_entry_ask()` reads the body's
  `**Ask:**` section alone, its words joined to one line, the literal `**Ask:**` stripped, the title when it is
  empty.
- **The sweep's consumers pass its item through:** ShiftLead's `gatesweep.py` and agent-cadence's
  `gate_sweep.py` both hand `answers`, `default` and `lifts` from `sweep()`'s item to the board writer unchanged,
  so neither needs code for the sweep to offer other answers.
- **Text a person reads** (v3.2): the package's own writers do not run the check; a consumer's writer of an Ask
  passes the entry's answers to it, read as a board `Answers:` value.

## The design

### D1. An entry's answers are one line, `**Answers:**`, and its lifts one line, `**Lifts:**`

An entry that waits on a person may carry two one-line body fields, each a body section that is its lead's line
alone:

- `**Answers:** a | b | c` — the answers the person may give, in the board's `Answers:` value form (each
  `<label>` or `<label> — <consequence>`, one marked ` (default)` at most, a form `<head>: <words>` among them,
  `\|` for a literal bar), all on the lead's line.
- `**Lifts:** a | b` — which of them lift the gate, each an answer's whole label (a form by its offered label,
  `Hold: <note>`, so its fills lift), on the lead's line. With no `**Lifts:**`, `Go` lifts, as on the board.

Each is found by its lead's name (`Answers`, `Lifts`, the colon optional, inside the bold or after it (read so until TD-124's v4.0; see *Not done*), as every
lead is matched: `_section_key()`'s match, case-insensitive with whitespace folded, so `**LIFTS:**` is one), as a section `_entry_sections()` reads, and is one line: the section's text, HTML comments
dropped first, is its lead's line and nothing else. Its value is that line after its lead's bold run, leading
whitespace removed, then one `:` only where the bold run held none (`**Answers**: a`), and trailing whitespace
stripped, `\|` kept for `parse_answers_value()` to read; an
empty value is refused, never the title. Three refusals keep the read exact, and the check names each (D4):

- **The field runs past its line**: any further line in its section, glued below it (a wrapped answer, a
  `**Fix:**` with no blank line before it, a code fence) or a later paragraph before the next lead (a stray
  sentence). So nothing after the line is ever read as part of the last answer or the last lift, and nothing is
  dropped silently. A bold run inside the line (`Not yet — **Note:** you wait`) is answer text, except one named
  `Answers` or `Lifts`.
- **A field inside the line**: a bold run named `Answers` or `Lifts` (D1's match, `**Lifts:**` or `**Answers**:`)
  anywhere in either value (found by an overlapping scan: a bold run is tried at every `**` in the value, as
  `re.finditer(r"(?=\*\*(?P<lead>[^*\n]+?)\*\*)", value)` does, each run's lead then tested by D1's name match, so a
  stray `**` earlier in the line never pairs with the field's own opening `**` and hides it), so a `**Lifts:**` typed on the answers' own line is never read as the last answer's
  words while the lifts are lost.
- **The lead starts no section**: a line of the body whose text, leading whitespace aside, opens with an
  `Answers` or `Lifts` lead but that `_entry_sections()` does not read as a section's start, because it is glued
  to the line above (the Ask, the Fix, the other field) or indented. So an `**Answers:**` glued to the Ask is not
  read as part of the question while the sweep offers `Go | Not yet`.

This is the whole boundary rule here: the field is a line, so where it ends needs no rule; where it starts is
`_entry_sections()`'s, which TD-124 makes strict for every section. This reader keeps all three refusals after
TD-124 lands (TD-124 D6: TD-119's refusals stay its own); TD-124's `glued-lead` flag also fires on the strict
column-0 case, while the indented, colon-less and non-strict glued forms (glued without the strict `**Name:**` lead) are refused
here alone. Lines inside a code fence are never tested
(the fence as `_entry_sections()` tracks it: `FENCE_RE`, its open and close rules); an indented code block is not a
fence, so an `Answers` or `Lifts` lead quoted in one is refused as a lead that starts no section, and is quoted in
a fence instead. A fence that never closes (one opened by a run and never closed by a bare run of its own
character, at least as long, such as a `~~~` "closed" by a backtick run) guards nothing for this test: where the body
ends inside an open fence, the lines after its opening line are tested too, so a real field swallowed by a stray
fence is refused, never read as None. HTML comments are dropped first, as `_entry_texts()` drops them, so every caller reads the same
text; a line that held only a comment is then a blank line, so a comment between a lead and the line above it
leaves the lead starting a section. What opens with no lead of these names is prose, read by nothing here and
refused by nothing: a list item or a quote (`- **Answers:** …`, `> **Answers:** …`), text before the lead on its
line, a singular `**Answer:**` or `**Lift:**`, and a line inside the header block (a header field). An entry so
written gets `Go | Not yet`, as today; TD-124 leaves them prose too (its flag catches only an indented or quoted Ask). The
reader drops comments and the writer's `edit --section` does not, so a lead behind a comment on its own line
(`<!-- x -->**Answers:** a | b`) is a section to the reader and none to the writer, which then appends a second
`**Answers:**`; on a gated entry the edit is refused as two sections (D4), a refusal, not a misread, and on an
ungated one it is written and nothing reads either. Two more shapes read clean here and are flagged by TD-124 on
the raw body: a comment line holding a bare fence marker (TD-124's `fence-open`) and a comment-only line glued
above a lead (its `glued-lead`); the writer's `edit --section` reads them as the raw text does. Only the
body is read: a header field named `Answers` or `Lifts` is a field like any other, read by nothing here. A
qualified lead (`**Answers (…):**`) is its own section, never these. They sit anywhere in the body before the
Log; the writer's `edit TD-n --section Answers --from FILE` writes them as it writes any section (the file one
line), and no new command or flag is added.

**Options set aside.** *A multi-paragraph section, its words joined to one line* (Drafts 1–3): every round
found text glued to it or after it misread (F23, F30, F33, F38, F41, F42, F49), and each fix moved the hole;
Paul held it. A one-line field has no end to find. *A header field* (`Answers:` in the header block): header
values are the summary's metadata, and the format already keeps the Ask, what the person reads, in the body;
ShiftLead writes the field in the body, on one line. *Reading the Ask's prose* (bold words, *or*): a guess, and TD-1879's Ask names its options in
running prose; a sweep that guessed would lift on the wrong press. *Answers inside the Ask section*: the Ask's
first paragraph is its question sentence (*Text a person reads*), so a second home inside it would split one
section two ways. *Leaving `Go | Not yet` and teaching the person to type the answer*: a typed *Works* lifts
nothing, which is the bug.

### D2. One reader decides whether the answers can be offered

`entry_answers(entry_text)` (v3.N) reads one entry's two sections, in this order:

1. HTML comments are dropped (`COMMENT_RE`). If `_entry_parts()` refuses the entry, the reader scans that text's
   lines after its heading and header block (up to the first blank line after the header paragraph, `_entry_parts()` skipping blank lines before it), as far as they can be told apart: a line that, its leading whitespace removed, `LEAD_RE` matches with a lead named `Answers` or
   `Lifts`, outside a fence (the open-fence rule below applying here too), makes it refused (`Refused`, the parts' reason); with no such line, `None`. If the
   entry parses, the reader scans its body alone (never the heading or the header block, where a field named
   `Answers` is a repo's own): a line, outside a fence, that, its leading whitespace removed, `LEAD_RE` matches with
   a lead named `Answers` or `Lifts` (D1's match) and that `_entry_sections()` does not read as a section's start is
   refused, *an Answers or Lifts lead that starts no section*. The scan tracks fences by `FENCE_RE` with
   `_entry_sections()`'s open and close rules, and where the text ends inside an open fence, it tests the lines
   after that fence's opening line too (D1). Otherwise, no such section: `None`, whatever else the entry holds. Two
   sections of one name (`**Answers:**` twice, or `**Lifts:**` twice): refused.
2. A section whose text (`_entry_sections()`'s, its trailing blank lines trimmed) is more than its lead's line:
   refused, *the field runs past its line*. A `**Lifts:**` with no `**Answers:**`: refused. An empty
   `**Answers:**` value: refused, *no answers*; an empty `**Lifts:**` value (nothing, or only bars): refused, *no
   lifts*. A value holding, anywhere, a bold run whose lead is named `Answers` or `Lifts` (D1's overlapping scan, a run tried at every `**`, each
   run's lead tested by D1's name match): refused, *a field inside the
   line*.
3. The answers are `parse_answers_value()`'s of the `**Answers:**` value, each split by `split_answer()`; any other bold
   run in the line is answer text. More than one marked ` (default)` is refused; each is returned with its mark
   removed, as `<label>` or `<label> — <consequence>`, a bar in it a literal `|`; `default` is the marked one's
   index, else None.
4. The lifts are `parse_answers_value()` of the `**Lifts:**` value, as written (literal bars), else None.
5. `item_file("x", "2000-01-02", "2000-01-01", None, None, "<the entry's id> decision (p)", kind="decide",
   answers=…, default=…, lifts=…, detail={"context": "x", "question": "x?", "recommended": "x"})` is called
   with them (a Due and a detail block, since a `decide` needs both; the probe exists only for the answers',
   default's and lifts' rules, and no entry id makes its context refused): what it refuses is refused, with its
   reason. Its rules
   (*What is already settled*) are the authority; the list there is for the reader of this plan.
6. Two answers whose labels are equal after whitespace folding and case folding (`Go | go`): refused, *two answers with one label*, as the Lifts match folds case. No answer lifts — no `**Lifts:**` and no answer whose label, whitespace-folded and compared
   case-insensitively, is `Go` (a form `Go: <note>` is not): refused, *no answer lifts (labels read: <each label, as read>)*, so a bold label (`**Go** — build it`, read as `**Go**`) shows why. (A `**Lifts:**` step 5 passes always names an offered answer.)

Otherwise it returns `{"answers": [...], "default": <int or None>, "lifts": [...] or None}`. It reads no board and
no person: the same text gives the same result for the sweep, `check()` and a consumer's writer.

### D3. The sweep offers them

The `decision (<p>)` bullet of *The gate sweep* keeps its rule for *when* it files; it changes only *what*. For an
entry whose `entry_answers()` returns answers, the `decide` it files carries them: `answers`, `default` and
`lifts` from the reader, and a detail block whose `recommended` names what lifts: `Only <p> can say: <a> lifts the gate` for one
lifting label, `Only <p> can say: <a>, <b> lift the gate` for more (the lifting labels, or `Go`, in the answers'
order, each as written, joined by `, `); then, for each offered waiting-only answer (`Not yet` or `Keep waiting`,
as `waiting_only()` reads them, so `Not yet.` is one), `, and <label> keeps it waiting, asked again in <reask_days> days`; then
`, and the other answers leave it standing` when any answer neither lifts nor waits. Every label is printed exactly as the answer writes it (`go` stays `go`, `Not yet.` keeps its period); two waiting-only answers each add their own clause, in the answers' order. The fixtures take this string from this paragraph (the SPEC states no `recommended` string, today's or this one). So `Go | Not yet` gets
today's string word for word (with a default, `item_file()` writes it after the default's label, `<label> — …`,
as for every item). For an entry with no answers (the reader returns `None`), and for one whose answers the
reader refuses, it files `Go | Not yet` as today; for the refused case its detail context gains *; its own answers
could not be offered (the ledger check names why)*. The sweep never raises for an entry's answers.

What the person's press then does is the board's rule, unchanged: a lifting answer lifts the gate (on this
repo's own entry by the decide lift, closing the item; on another repo's, through *an answer owing a lift*); `Not yet` or `Keep waiting`, where offered, closes it and keeps the gate; any other
answer (*One more round*, *Hold: <note>*, *Not right: <what it printed>*) is a work order the entry's session
acts on, and the item stays open and `decided`, covering the gate.

The item's identity, its filing rule and the `kept waiting` window are unchanged. An item already open is not
rewritten when an entry gains answers: the sweep files only uncovered gates. The sections apply to every
`decision (<p>)` on the entry, one set for all its people (answers per person are not this design). An entry
covered through its parent's item (`Parts:`) is asked by that item, whose answers are the parent's: its own
sections are offered only when the sweep files for it. The refused case's reason is the check's alone; the item
says only that the entry's answers could not be offered.

An entry's answers need not include a waiting-only one: a set such as `Works — you saw it work | Not right: <what it printed> — I'll file what you saw` lets
the person lift or give a work order, never defer; an entry that wants deferral lists `Not yet` (or `Keep
waiting`), which closes the item and writes `kept waiting` as today.

**A work-order answer.** With `Go | Not yet`, every press closed the item. A work-order answer (*One more round*,
*Hold: <note>*, *Not right: <what it printed>*) leaves it open and `decided`, as any work order on the board does,
and it covers the gate, so the sweep asks nothing while the entry's session acts. That session closes the item
when it has acted (`done`, as for any work order), and asks again itself where the work ends in a question (a
design's next end-of-rounds item, a check run again): once closed, the item's answer is one that does not lift,
dated within `reask_days` of its `Decided:` date (not its close), so the sweep files no item of its own over the session's for that window (`reask_days`, 30 by
default, `SWEEP_REASK_DAYS`; a host may pass its own). That window
is accepted: the session that acted knows when to ask, and the sweep is the backstop for a gate nobody asks
about.

### D4. The ledger check flags answers the sweep cannot offer

`check()` flags an open entry whose `Blocked by` names a `decision (<p>)` (as `parse_gates()` reads its
`decisions`) and whose `entry_answers()` raises (`answers-unusable`), with the reader's reason; an error on an
entry the edit changed (its whole text, as for the Log), ℹ on a standing ledger. It joins `EDIT_ERRORS` and
`TEXT_KINDS`, so it is scoped to an entry's whole text (an `edit --section Answers` changes the body alone) and
the ledger writer refuses an edit that makes one, as it refuses `ask-missing`. An entry with no decision gate is
not flagged, whatever its sections hold: nothing reads them, and a repo's own prose `**Answers:**` section,
which *Text a person reads* allowed before v3.N, stays legal there. The flag comes with the gate: an edit that adds
a decision to an entry whose sections cannot be offered is refused, naming why. As for every edit flag, the
writer refuses only a flag whose kind, entry and reason are not already on the entry: one already there does not
block an unrelated edit (a Log note, a Status), while an edit that changes its reason (one unusable section for
another), or a `reopen` of an archived entry, or a `renumber` of an entry, whose section is unusable, is refused (the flag
names the entry, so either makes a new one).

The reason names the first fault in the reader's order. On an entry with two faults, fixing the named one first exposes the other under a new reason, which the writer refuses; the cure is to fix both in one whole-entry write, or the unnamed one first. The flag's text ends *(the first fault found)* so the person knows another may follow.

Since a `**Lifts:**` with no `**Answers:**` is refused, a writer adds `**Answers:**` first (or both in one
whole-entry write): `edit --section Lifts` on a gated entry with no `**Answers:**` is refused.

### D5. The answers are text a person reads

*Text a person reads*' Ask bullet now names the format's section. A consumer's writer of an entry's Ask passes
the entry's answers to the check (`entry_answers()`'s; where it returns None, a repo's own field as before; where
it raises, none, since `check()` names that fault); a consumer's writer of the `**Answers:**` section alone runs
rule 2 over those answers with no sentence (`person_text_problems()` with `sentence=None`, which reads no rule
1), so each answer names who acts at the writer, as any board answer does. The sweep and the
package's writers run no check (TD-111 D3), so no fixture of this package covers this seam; it is the consumers'.

### D6. The release

A minor release, **v3.3**: v3.2 (TD-111's check, with v3.1's `decision-missing`) was tagged on 2026-11-15
(#359), so the next untagged minor is v3.3 and the build waits on no tag. TD-115's build (TD-123, #376) wrote v3.3's first
*Versions* paragraph, and v3.3 is not tagged yet; TD-124's B1 (TD-133) also targets the next untagged minor, so three builds may share it; each writes its own paragraph with its own bold lead, this one after the newest on main when it merges,
as *Versions* already holds several paragraphs for one release (v2.4, v2.7, v3.0), so neither paragraph's claims
are the other's. If v3.3 is already tagged when this build merges, every `v3.N` it writes becomes the next
untagged minor.

**What reads differently.** An entry that already carries an `**Answers:**` section gets its own answers on the
sweep's next item instead of `Go | Not yet` (as ShiftLead's TD-1845 would have, its answers usable: `Go` lifts; it is archived, so the build changes no entry on the roster today, and ShiftLead's TD-1404, still open, may gain sections later; TD-1879 is archived too). A
gated entry whose section is not usable gains a standing ℹ `answers-unusable`; as for every edit flag, an edit
is refused only where it makes the fault (breaks the section, or adds a decision to an entry whose section is
unusable, or a `reopen` or `renumber` of an entry whose section is unusable), and one already there does not block an unrelated edit (the writer's gate matches a flag by its
kind, entry and reason). The repo's own section, which v3.2 left to the repo, is the format's on a gated entry. No parse, field, Log line, item key or
canonical form changes.

**The consumers.** Neither needs code: both pass the sweep's item through. On the build's merge the builder tells
agent-cadence's techlead which release carries it; on Paul's go the designer sends ShiftLead's question seat one
note (`ao td add --repo shiftlead`): once the release is vendored, TD-1404 (TD-1879 being archived, 2026-11-16) and any entry whose Ask
names its own answers can carry `**Answers:**` and `**Lifts:**` sections. The two items #355 filed for them on this
repo's board, with `Go | Not yet`, stay as filed, since an open item is never rewritten, and nothing here
touches them: Paul may answer them as they stand. To re-ask one with its entry's own answers, ShiftLead's session,
once its sections land, closes it unanswered by a PR in this repo (`board_edit.py done --why "re-asked with the
entry's own answers"`), and the next sweep files it again (an item closed with no answer opens no window); the
note says so.

## The SPEC text

The build adds these, word for word, `v3.N` the release D6 names.

**In *The ledger*, after the paragraph ending *A `Waits` field is never read as a gate.*:**

> **An entry's own answers** (v3.N). An entry that waits on a person may name the answers it offers in a
> one-line body field `**Answers:**`, in the form of a board `decide`'s `Answers:` value (*The board*: each
> `<label>` or `<label> — <consequence>`, one marked ` (default)` at most, forms among them), and which of them
> lift its gate in a one-line body field `**Lifts:**`, each an answer's whole label (a form by its offered label,
> `Hold: <note>`); with no `**Lifts:**`, `Go` lifts. Each is a body section that is its lead's line alone, HTML
> comments dropped first, its lead's name matched as every lead's is (case aside, whitespace folded); its value
> is the line after its lead's bold run, leading whitespace removed, then one `:` where the bold run held none.
> A header field of either name, and a qualified lead (`**Answers (…):**`), are not these.
> `entry_answers(entry_text)` reads them: None when the entry has neither; `{"answers", "default", "lifts"}` when
> they can be offered (each answer with its ` (default)` mark removed and a literal `|`, the marked one's index or
> None, the `**Lifts:**` labels or None); and it raises `Refused`, naming why, for an `Answers` or `Lifts` lead in
> the body, outside a code fence that closes, that starts no section (glued to the line before it, or indented),
> a bold run named `Answers` or `Lifts` inside either field's line (a run tried at every `**`), two answers whose
> labels are equal with case and whitespace folded, an entry with
> either field that `_entry_parts()` refuses, two of one name, a field whose section runs past its line (a line
> glued below it, or a later paragraph before the next lead), a `**Lifts:**` with no `**Answers:**`, an empty
> `**Answers:**` or `**Lifts:**`, two answers marked, answers `item_file()` refuses as a `decide`'s `answers`,
> `default` and `lifts` (fewer than two among them), and answers of which none lifts (its reason naming the labels
> read). It names the first fault found. `check()` flags an open entry
> whose `Blocked by` names a decision and which it refuses (`answers-unusable`, its text ending *(the first fault
> found)*; an error on an entry the edit
> changed — its whole text — ℹ on a standing ledger). The gate sweep offers them (*The gate sweep*).

**In *The gate sweep*, the `decision (<p>)` bullet:** *`Answers: Go | Not yet.`* becomes

> its answers the entry's own (*An entry's own answers*: `entry_answers()`'s `answers`, `default` and `lifts`),
> else `Answers: Go | Not yet.` (v3.N: also when the entry's answers are refused, its detail context then saying
> so), …

and the paragraph after the bullets, *One filing rule* (which ends *is the `decision (<p>)` bullet's (above).*), gains, as its last sentence:

> An item the sweep filed is never rewritten: an entry that gains answers keeps the item already open.

**In *Text a person reads*, the Ask bullet:** *An Ask carries no answers in this format; a ledger that keeps its
own `Answers` (a repo's own field or section) passes them, read as a board's `Answers:` value
(`parse_answers_value()`);* becomes

> An entry's answers (*An entry's own answers*, v3.N) are passed with it, `entry_answers()`'s `answers`, else a
> repo's own `Answers` field, read as a board's `Answers:` value (`parse_answers_value()`), and none where
> `entry_answers()` refuses them (`check()` names that fault); a write of the entry's `**Answers:**` section
> alone runs rule 2 over its answers with no sentence (`sentence=None`);

**In *Versions*, a paragraph of its own for the release, after the newest:**

> **v3.N gives an entry its own answers** (*The ledger*, *The gate sweep*): `**Answers:**` and `**Lifts:**`
> one-line fields, `entry_answers()` that reads them, and `check()`'s `answers-unusable`, which the ledger writer
> refuses on an edit. The gate sweep's item for an uncovered decision offers the entry's answers where it has
> usable ones, and `Go | Not yet` otherwise. No parse, field, Log line, item key or canonical form changes; an
> entry that already holds an `**Answers:**` section is offered its own answers, and one whose section cannot be
> offered is flagged ℹ when it waits on a person; an edit is refused only where it makes the flag, a `reopen` or a
> `renumber` of such an entry among them. *Text a person reads*' allowance of a repo's own
> `**Answers:**` section is narrowed: on an entry with a decision gate, it is now the format's one-line field.

## The fixtures

- **`fixtures/sweep/`**: a new key `answers` in `cases.json`, its own small ledger `sweep/answers/ledger.md` and a
  board `sweep/answers/board/` listing `People: pat`, so the existing runs' expected results do not move. Its
  entries, each `decision (pat)` and uncovered: one with no section (`Go | Not yet`, today's item); one with
  `Answers: Works — I'll archive the check | Not right: <what it printed> — I'll file what you saw`
  and `Lifts: Works`; one with `Go (default) — … | One more round — … | Hold: <note> — …` (each `…` a consequence naming who acts, `you` or `I'll`) and no `**Lifts:**`
  (`default` 0, `lifts` None); one whose `**Lifts:**` names a label not offered (refused: `Go | Not yet`, the
  detail context's added clause); one with no lifting answer (`One more round | Hold: <note>`, no `**Lifts:**`);
  one with `**Lifts:**` and no `**Answers:**`; one whose `**Lifts:**` names a form, `Hold: <note>`. The runner
  (`sweep_cases()`, which today reads `sweep/`'s top-level `ledger.md` and `archive.md`) gains the key's own
  ledger text and its v3 board directory, read apart from the existing runs; it calls `sweep()` over them on one date, guarded by `hasattr(L,
  "entry_answers")` (reporting the key `missing` for an older module, as the sweep's own guard does); the expected
  items are written from this SPEC text, never from the module's output.
- **`fixtures/ledger_edit/check/`**: the flag's levels: `answers-unusable` as an error on an edited entry and ℹ on
  a standing one; a usable section that flags nothing; an unusable section on an entry with no decision, not
  flagged.
- **`fixtures/ledger_writer/<case>/`** (the writer's gate, which compares the flags before and after the edit;
  each a `before/` and `after/` ledger, `cmd.json` and `expected.json`): an edit adding a decision to an entry
  whose section cannot be offered, refused; a Log note on a gated entry whose section already cannot be offered,
  not refused; `edit --section Lifts` with no `**Answers:**` on a gated entry, refused; a `renumber` of a gated
  entry whose section cannot be offered, refused.
- **`entry_answers()`**: a block in `fixtures/sweep/cases.json` (`entry_answers`), each an entry text and its
  result or `{"error": "Refused"}`: the cases above, a `\|` inside an answer, a qualified `**Answers (old):**`
  lead (None), a header `Answers` field over a body with no section (None, never refused), a mark on the second answer (`default` 1), two marks (refused), `Go | go` (refused, two answers with one label), `**Go** — build it | **Not yet**` (refused, no answer lifts, its reason naming the labels read), a
  form marked ` (default)` (refused), one answer (refused), an empty `**Answers:**` (refused), an empty
  `**Lifts:**` and one of only bars (refused: no lifts), two `**Answers:**` sections (refused), `Go: <note> | No`
  with no `**Lifts:**` (refused: no answer lifts), `go | Not yet` (`go` lifts), `Lifts: Hold` for an offered
  `Hold: <note>` (refused: a form is listed by its whole label), `**Answers**: Go | Not yet` with the colon after
  the bold (read as `**Answers:**`), answers wrapped onto a second plain line (refused: the field runs past its line, not joined), a stray paragraph
  after the answers before the next lead (refused: the field runs past its line), an HTML comment on the line
  after the answers (accepted: comments are dropped first), a comment then text on the line after the answers
  (refused: the text left runs past the line), an `**Answers:**` after the Ask with only a comment line between
  (accepted: that line reads blank), a `**Fix:**` after the answers with only a comment line between (accepted),
  an `**Answers:**` lead in a 4-space indented block (refused at step 1), a real `**Answers:**` after a backtick
  fence never closed (refused at step 1), the same after a `~~~` fence "closed" by backticks (refused at step 1),
  `**Answers:** Go | Not yet **Lifts:** Go` on one line (refused: a field inside the line), the same with a stray
  `**` earlier in the answers, `**Answers:** A — x ** | B — y **Lifts:** A` (refused: the overlapping scan finds
  the field), an unclosed fence after a clean `**Answers:**` and in a later section (accepted: the field is read
  before it), an unclosed fence with no lead after it (None), `**LIFTS:**` in capitals (read as `**Lifts:**`), a list item
  `- **Answers:** Go | Not yet` (None: prose), a quoted `> **Answers:** Go | Not yet` (None: prose), `Answers here:
  **Answers:** Go | Not yet` with text before the lead (None: prose), a singular `**Answer:**` (None: prose), `**Lifts:**` on the line after `**Answers:**` with no
  blank line (refused at step 1, a lead that starts no section), the same with the glued `**Lifts:**` indented by
  a space (refused at step 1), `**Answers:**` on the line after `**Ask:**` with no blank line (refused at step 1,
  not None), a glued `**Fix:**` after the answers (refused at step 2), an `**Answers:**` lead inside an HTML comment
  (ignored, None), an `**Answers:**` line inside a code fence in the Fix (ignored, None), and an answer with a bold
  run inside its line (`Not yet — **Note:** you wait`, accepted, the run kept in the answer).
- **The sweep's `recommended`**: in the `answers` key, an entry offering `Go | Not yet` from its own section gets
  today's string word for word, and one offering `Works | Not yet | Not right: <what it printed>` names `Works`,
  `Not yet` keeping it waiting, and the other answers leaving it standing.

## Builds

One build, **B1**: `entry_answers()`, the sweep's use of it, `check()`'s `answers-unusable` in `EDIT_ERRORS` and `TEXT_KINDS`,
the SPEC text above, the fixtures and unit tests (the reader's refusals by reason; the sweep never raising on
an entry's answers), in one PR; the release number as D6 says. If TD-124's B1 has merged, B1 builds `entry_answers()` over its
line-reading helper; if not, TD-124's B1 moves it there (TD-124 D6 and *Builds*); either way D1's three refusals
stay, and the moved reader reads comment-dropped text (D1, step 1), so a shape F77 names (an `**Answers:**` after a comment-only line, a comment-only line holding a bare fence marker) reads as it does here, never as TD-124's raw reading would; the `entry_answers` fixtures pass unchanged whichever build merges second, and TD-133's builder is told so with this plan's link. `fixtures/run.py`'s `ledger_edit` check runner lists the `check()` kinds it compares; B1 adds
`answers-unusable` to that list and a runner for the `entry_answers` block. On its merge the builder tells agent-cadence's
techlead which release carries it.

## Not done

- **The item's text** stays the entry's whole Ask joined to one line, as today. Since v3.2 an Ask's first
  paragraph is its question and its later paragraphs context; filing only the first paragraph as the item's text
  and the rest as its detail context is a change of its own, not this one.
- **No rewrite of an open item** when its entry's answers change (D3).
- **No writer flags**: `edit --section Answers|Lifts` writes the fields; `new` and `set` gain nothing.
- **No section-edge rule**: where any section starts is TD-124's design (strict edges, one-line data fields, a
  check over every body); this design reads its two fields by today's `_entry_sections()` and refuses only what
  D1 names. D1's three refusals stay this reader's after TD-124 lands; TD-124's build shares its line-reading
  helper with `entry_answers()` (whichever merges second), and is where list-item, quoted and mid-line lead-like
  text is caught. TD-124 may also retire the colon-optional and colon-after-bold lead forms
  (`**Answers**:`); this design reads them as every lead is read today, and its fixtures for them are ones
  TD-124's migration may rewrite. TD-124's v4.0 (TD-135) does retire them: after it, step 1's scan still matches the old spellings by `LEAD_RE` as v3.N reads it, so `**Answers**: Go | Not yet` is refused (*an Answers or Lifts lead that starts no section*), never read as prose with `Go | Not yet` offered silently; that fixture is one the v4.0 build flips from read to refused, and TD-135's builder keeps the scan.

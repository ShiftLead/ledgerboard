# TD-008: the board's writers (v2.3)

**Status:** Draft 2026-10-31 (the designer). Class: **wide**, since it changes a vendored format that both consumers run (cap 6 rounds, cadence.md §4.8 *Design review rounds*). The review record is `docs/reviews/TD-008.md`.

**Entry:** [TD-008](../ledger/TD-008.md). The shape was agreed 2026-10-30 (the entry's Fix). This plan gives that shape its exact rules, `SPEC.md` text and fixture cases, and splits it into three builds that ship as one minor release.

## The problem

Every board write but two goes through `ledgerboard.py`: `edit_line()` (snooze, done, decide, reply), `item_line()` (a plain new item) and `decided_line()` (an item already decided). The two without a writer are a new `decide` item, with its kind, `Answers:`, the `(default)` mark and its detail block, and the archive of closed items. Both are typed by hand, and nothing checks a hand-typed line. The ledger had the same gap until v2.2 gave it one canonical form, writers, and a gate that refuses what the writers would not have written. The board needs the same three things.

`item_line()` today also writes three wrong lines, each confirmed against v2.2:

| call | writes | wrong because |
|---|---|---|
| `item_line("Ship it?", …, session="w-1", host=None, …)` | `(session `w-1` on None) — Ship it?. Context: …` | a missing host is written as `None`, and a `?` gets a `.` after it |
| `item_line("check Due: 2026-02-01 first", due="2026-01-20", …)` | `… — check Due: 2026-02-01 first. Context: none. Due: 2026-01-20.` | the reader takes the first `Due:` as the item's date, so it reads 2026-02-01 |
| `item_line("x", …, context="TD-1 Due: 2026-03-01")` | `… Context: TD-1 Due: 2026-03-01. Due: 2026-01-20.` | the same, through the context |

It re-reads nothing it writes. `edit_line()` and `decided_line()` both do.

## What the builds add

Three parts, one minor release (v2.3). Each is a PR here with its spec, code and fixtures together (AGENTS.md):

1. **`item_line()` writes every kind** (§1): `kind`, `answers`, `default` and `detail`, keyword-only after today's six positional parameters. It re-reads what it wrote and fixes the three lines above.
2. **The item gate** (§2): `item_problem(line)` says why an open item line is not one the writers write. `canonical_item(line)` rewrites a line into that form where it can do so without changing the line's item key. `board_problems(board, old)` is the one call a consumer's gate makes.
3. **The archive** (§3): `archive_closed(board, archive)` moves the closed items, detail blocks with them, and `archive_subject()` gives that write its commit subject.

`decided_line()`, `edit_line()`, the reader and `item_key()` do not change. No board line is read differently, and every line a v2.3 writer writes is read the same by v2.2.

## Choices this plan makes

Each choice below is settled by `SPEC.md` or by the agreed shape, unless it is marked **(steer)**. A steer is a default the person may want to change; each one is listed in the end-of-rounds board item.

- **C1. The canonical writer never changes a line's item key (steer).** Consumers persist keys: ShiftLead stores `board:<sha256(item_key)[:8]>` for a claim on a decided line and for every line's id, and the closed-twin rule matches an open copy to a closed copy by key (SPEC *The item key*). A rewrite that changed a key would break a held claim and a copied id. It would also bring back an item closed on another branch while the format pass was in flight, because the old-form closed copy and the new-form open copy would no longer match. So `canonical_item()` changes only what the key leaves out: the `Due:` field's spelling and its place. It refuses everything else and names what a person must fix. *What it costs:* the consumer's format pass fixes little. Most hand-typed lines have a head with extras (`, branch x`, `/ worker-2`), no backticks, or no `Context:`, and each of those is in the key. Old lines are never judged (C2), and a board turns over through its archive, so they leave on their own. *The alternative:* rewrite them anyway, and have each consumer's pass re-key what it persisted, using `item_key()` of the old line and of the new one. That puts a migration into both consumers for a cosmetic gain.
- **C2. The gate judges new lines only.** A line is new when the board before the edit held no line with its item key. A snooze, decide, reply or tick keeps a line's key, so a line a tool edited is not new. This matches the ledger's rule that an untouched entry is never judged, so there is no flag day.
- **C3. Kind rules are the writer's, never the reader's (steer).** `item_line()` writes `Answers:` only on a `decide` (at least two distinct labels, at most one marked default) and on a `look` (the fixed pair, which it writes itself, with `Works (default)` only when asked). It writes no `Due:` on an `fyi`, and requires one on every other kind. These are cadence.md §3.5's *Which items carry `Answers:`* table: a decide's default only "when the session has a recommendation; none when only the person can know", a look's `Works (default)` only with evidence, no answers on `act`, `watch` or `fyi`. An item with no kind is not in that table. This plan gives it `act`'s rule, since both are the person's to-do and a question with answers is a `decide`. The reader still reads whatever a line carries, so no old line reads differently. *The alternative:* leave kinds unchecked and let a writer put `Answers:` on any item. Then `item_problem()` could not say that a hand-typed `act` with answers is wrong.
- **C4. A `decide` needs its detail block.** Cadence.md §3.3 says a decide always has one. `item_line()` refuses a `decide` without `context`, `question` and `recommended`. `item_problem()` cannot check this, since it sees the line only (the agreed shape: the gate checks the item line).
- **C5. The archive moves an open twin with its closed copy.** When an open item and a closed one share a key, the reader already treats the open one as closed (SPEC *The board*). If only the closed copy moved, the open copy would reappear as open. So both move.
- **C6. When to archive is the consumer's.** `archive_closed()` moves every closed item whenever it is called. It refuses a board with no closed item, a shape it would have to split (§3), and a result that does not read back. `ARCHIVE_AT` stays the format's threshold for a consumer to read.
- **C7. The archive write gets its own commit subject (steer).** `<tool>: archive <n> closed items (session <name>)`, which `subject_kind()` reads as `archive`. Without it, a consumer's audit of tool-made board writes has no subject to recognise. *The alternative:* no subject, and each consumer names the PR itself.
- **C8. `item_line()` refuses where it used to write a wrong line, and writes four inputs differently.** It now refuses: a field name (`Context:`, `Due:` in any case, `Answers:`, `Decided:`, `Closed:`) in the text or the context; a host given with no session; a session or host name holding whitespace or any of `` ` , ; ) ``; and a `today` that is not a date. It now writes differently:
  - a missing host is left out rather than written `on None`;
  - text ending in `?` or `!` keeps its mark with no `.` after it (`Ship it?`, not `Ship it?.`);
  - text ending in several periods keeps them (`wait...`, where v2.2 writes `wait.`);
  - a context ending in `.` loses that period (`Context: TD-1.`, where v2.2 writes `Context: TD-1..`).

  Each changes what `item_line()` writes for those inputs, and so the key of the line it writes; a line already on a board is untouched, and its key with it. The *Versions* text names them. Today's `compose` cases give the same output.

## §1. `item_line()` writes every kind

**Signature:** `item_line(text, due, today, session, host, context, *, kind=None, answers=None, default=None, detail=None) -> str`. It returns the item line and its detail block, one `\n` after each line. `answers` is a sequence of strings, each `<label>` or `<label> — <consequence>`, split at its first ` — ` as `split_answer()` reads it (the form `decided_line()` takes). `default` is a 0-based index into `answers`, or None. `detail` is described under *The detail block*.

**The line:** `- [ ] [<kind> ]<today> (<head>) — <text> Context: <context>.[ Due: <due>.][ Answers: <answers>.]`

- `<text>` has its whitespace collapsed and ends a sentence: a `.` is added unless it already ends in `.`, `?` or `!`.
- `<head>` is ``session `<name>` on <host>``, or ``session `<name>` `` when there is no host, or `n/a` when there is no session.
- `<context>` has its whitespace collapsed and one trailing `.` stripped. An empty context is written `none`.
- Answers are joined with ` | `, and a literal `|` is written `\|`. Each answer is written `<label>` or `<label> — <consequence>`, and the mark goes on the label: `<label> (default)`.

**Kinds:**

| kind | `due` | `answers` / `default` | `detail` |
|---|---|---|---|
| `decide` | required | required: two or more distinct labels; `default` an index into them, or None when only the person can know | required: `context`, `question`, `recommended` |
| `look` | required | `answers` must be omitted: the writer writes `Answers: Works \| Not right: <what>.` itself; `default` is None, or 0 for `Works (default)` | optional |
| `act`, `watch`, none | required | refused | optional |
| `fyi` | must be `None` | refused | optional |

**The detail block** comes from `detail`, a mapping whose keys are lower-case: the four parts `context`, `question`, `caveats` and `recommended`, and `otherwise`, which is not a part of its own but is written on the Recommended bullet. A part's value is a string, or a list of strings whose first string is the part's own line and whose other strings become nested bullets. `otherwise` is a string. The detail block's `context` is the item's explanation in sentences. It is separate from the line's `context` parameter, which names what the item refers to (`TD-008`, `PR #52`). Parts are written in this order:

```
  - **Context:** <detail context>
    - <a nested bullet>
  - **Question:** <question>
  - **Caveats:** <caveats>
  - **Recommended:** <default label> — <recommended> **Otherwise:** <otherwise>
```

On a `decide` with a default, `**Recommended:**` opens with the default's label, then ` — `. Otherwise it holds the given words alone (a decide with no default says there why only the person can know). `otherwise` is written on the Recommended bullet, so it is refused without `recommended`. Each part's own line, and `otherwise`, has its whitespace collapsed and ends a sentence, as the text does. A nested bullet has its whitespace collapsed and is written as given after a `- ` the writer adds (four spaces in), with no period added.

**Refused**, with a reason a person can act on:

- text that is empty or more than one line;
- text, context, an answer or a detail value that carries a field name (`Context:`, `Due:`, `Answers:`, `Decided:`, `Closed:`; `Due:` matched in any case, as the reader's `DUE_RE` is);
- a `today` or `due` that is not `YYYY-MM-DD`;
- a host given with no session, and a session or host name holding whitespace or any of `` ` , ; ) ``;
- a kind not in `KINDS`;
- a breach of the kinds table;
- an answer label that ends in ` (default)` (the mark is the writer's), a consequence shaped like a reply (` — <name>, <date>: `), or any answer the read-back would not read back as given;
- a `detail` key other than the four parts and `otherwise`, or an empty or multi-line detail string;
- **the read-back:** `parse_board()` of the result must give exactly one open item whose kind, due, answers, consequences, default, session, host, refs (`item_refs()` of `Context: <context>`) and detail block are the ones meant, with no `Decided:`, no replies, `fyi_due` false and `bad_due` None. The result must hold no other item line, open or closed, so a detail string that opens `[ ]` or `[x]` is refused. Otherwise the call is refused.

### SPEC text (§1)

In *Edits*, this replaces the paragraph that opens "A new item (`item_line(text, due, today, session, host, context)`)":

> **A new item** (`item_line(text, due, today, session, host, context, *, kind, answers, default, detail)`, v2.3) is one line, `- [ ] [<kind> ]<today> (<head>) — <text> Context: <context>. Due: <due>.` then `Answers: …` where its kind takes them. Its head is ``session `<name>` on <host>``, ``session `<name>` `` with no host, or `n/a`. The text ends a sentence (a period is added unless it ends in `.`, `?` or `!`), and an empty context is `none`. What a kind takes:
> - a `decide` carries two or more distinct answers, at most one marked ` (default)`, and a detail block;
> - a `look` carries exactly `Answers: Works | Not right: <what>.`, which the writer writes itself, `Works` marked ` (default)` only when the caller asks;
> - an `fyi` carries no `Due:`, and every other kind carries one;
> - no kind but `decide` and `look` carries answers.
>
> These are the writer's rules. The reader still reads whatever a line carries. An answer is written `<label>` or `<label> — <consequence>`, with the mark on the label.
>
> The **detail block** is composed from named parts, in the order `Context`, `Question`, `Caveats`, `Recommended`. Each part is one two-space-indented bullet, ``- **<Part>:** <words>``, with any further lines as nested bullets under it. On a `decide` with a default, Recommended opens with that default's label and ` — `. An `Otherwise` text follows the Recommended words on the same bullet as ``**Otherwise:** <words>``. A `decide` needs Context, Question and Recommended. No writer touches the block afterwards.
>
> The writer refuses text, a context, an answer or a detail value that carries a field name, or that is more than one line; a date that is not `YYYY-MM-DD`; a host with no session; and any result the reader would not read back as exactly the item meant, its detail block included.
>
> An answer given elsewhere (on a ledger entry) is written as an already decided `decide` item with `(person)` as its head (`decided_line()`, unchanged).

### Fixture cases (§1)

These go in `fixtures/edit/cases.json` `compose`. `fixtures/run.py` passes the new keywords when a case carries them, and a case's own `today` in place of the spec's when it carries one.

- **Written:** a decide with three answers, one of them with a consequence, the default on the second, and all five detail parts (Context with two nested bullets); a decide with no default; a look (the pair written); a look with `default=0` (`Works (default)`); an fyi with no due; a watch; a session with no host; text ending `?`; an answer holding a literal `|`.
- **Refused:** a field name in the text; one in the context; one in a detail value; a decide with one answer; a decide missing `question`; answers on an `act`; answers passed to a `look`; a look with `default=1`; a due on an `fyi`; no due on a `watch`; a default out of range; a label ending ` (default)`; a consequence shaped like a reply; duplicate labels; a host with no session; an unknown kind; an unknown detail part; `otherwise` without `recommended`; a `today` of `2026-1-5`.
- **Unchanged:** today's `compose` cases (three `item_line`, five `decided_line`) give the same output.

## §2. The item gate

### `item_problem(line) -> str | None`

`item_problem` takes an item line, with or without its line ending. It returns why the line is not an open line the writers write, as the line now stands after any snooze, decide or reply, or None. When a line has several problems, the string names each one, separated by `; `. Each problem opens with its rule's tag, a fixed word the fixtures rely on: `open:` (rule 1), `kind:` (2), `head:` (3), `text:` and `context:` (4), `due:` (5), `answers:` (7) and `extra:` (8). Any word between `- [ ] ` and the date that is not a lower-case member of `KINDS` (`Decide`, `todo`) is a `kind:` problem. `head:` judges only what follows a kind, or nothing, and a valid date: a bad date or a head outside rule 3's forms. The words after a tag are the build's, and the fixtures record them once written. A line the writers write:

1. opens `- [ ] ` at column 0, with single spaces;
2. may carry a kind, which is lower-case and in `KINDS`;
3. carries a valid date, then a head that is exactly one of ``(session `<name>` on <host>)``, ``(session `<name>`)``, `(n/a)` or `(person)`. `(person)` stands only on a decided line, as `decided_line()` writes it. A name and a host hold no whitespace and none of `` ` , ; ) ``, as §1 requires of the writer's;
4. continues with ` — `, then text that ends a sentence and carries no field name, then ` Context: <words>.` once;
5. carries ` Due: <date>.` once, right after Context, on every kind but `fyi`, and none on an `fyi`;
6. may carry replies after its `Due:`, or after its `Context:` on an `fyi`;
7. carries answers by the kinds table of §1 while it is undecided: on a `look`, exactly `Works | Not right: <what>` or `Works (default) | Not right: <what>`, so a hand-typed `Not right:` alone is faulted. A decided line (`Decided:` read) may carry answers or none, with at most one mark, whatever its kind, since `edit_line()` decides any item;

8. holds nothing outside the parts rules 1–7 name, one space between each part and the next, with no trailing whitespace. The spacing inside a part (the words of a text or a Context) is not judged; `decided_line()` writes a ref as given.

Rules 4, 5 and 7 are checked on the line with its reply tails (`reply_span()`) and its `Decided:` field taken out, and marks are counted among the `Answers:` alone. A reply's words and a `Decided:` text are the person's: `edit_line()` lets them hold `Due:` (a reply, on a dated item), a field name (a decide's answer) or ` (default)`, and none of that is a second field. Rules 1–8 are the definition; `canonical_item()` is defined from them, never the reverse.

The rule is checked as a property: `item_problem()` is None for every line `item_line()` writes, for every line `decided_line()` writes, and for each of those after any snooze, decide or reply that `edit_line()` does not refuse. (A snooze of an `fyi` is refused, since the reader reads no `Due:` on one. A `done` ticks the line, which leaves the open form: closed lines are never judged.)

### `canonical_item(line) -> str`

`canonical_item` rewrites an open item line into the form above, keeping its `item_key()` and every word, or raises `Refused` naming what a person must fix (C1). It makes these rewrites and no others:

- it respells the `Due:` field's name in any case as `Due:`;
- it adds the period after the `Due:` date when one is missing;
- it adds Context's period when no `Answers:` follows Context. The key is kept, since `item_key()` strips `Due:`, the replies, `Decided:` and the line's trailing period. With `Answers:` after it, Context without its period is refused, since the period would then stand inside the key;
- it moves a `Due: <date>` that directly follows the text's closing `.`, `?` or `!` to right after Context, ending Context with its period. It does this only when nothing follows Context, and the move keeps the key, since `item_key()` strips `Due:` and the line's trailing period. A `Due:` inside the text's prose (`— check Due: 2026-02-01 first.`) is never moved: rule 4 refuses it. What it cannot do is add the text's own period: `— text Due: D Context: x.` has the key `— text Context: x`, and `— text. Context: x` would be another. So a text that does not end a sentence is refused by rule 4, whatever the move.

After the rewrites, the result must have no problem by `item_problem()`; otherwise the call is refused and names the problems that remain. So it refuses, among others: a text that does not end a sentence; a missing `Context:`; a head not in rule 3's forms; an `fyi` with a `Due:` (dropping it would lose words); a non-fyi with no `Due:` (there is no date to invent); and a `Due:` after `Answers:` or after replies, where moving it would change what the reader reads. The read-back must give the same key, and the same kind, due, answers, consequences, default, decided, replies, refs, session and host. It is idempotent: a line already in the form comes back unchanged. It keeps the input's line ending, and it respells and moves only the field `DUE_RE` first finds, never a `due:` in a reply's words. It is for a consumer's one-time format pass, which reports the lines it refused.

### `board_problems(board, old=None) -> list[tuple[int, str]]`

`board_problems` returns `(line number, problem)` for each open item line that `item_problem()` faults and that is new (C2): its `item_key()` is not the key of any item line, open or closed, in `old`. An open item line is every line `ITEM_RE` matches, at any indent, except an open twin of a closed line on the same board (which the reader already reads as closed). So a nested open line is judged, and faulted by rule 1. With `old=None`, every open line is judged. Closed lines are never judged. It is the board's `check()`: a consumer's gate calls it on the board as the edit leaves it, with the board as the edit found it.

### SPEC text (§2)

New paragraphs in *Edits*, after *A new item*:

> **The form the writers write** (v2.3): an open item line that `item_line()` or `decided_line()` composed, as it stands after any snooze, decide or reply. In short, the line:
> - opens `- [ ] ` at column 0;
> - carries an optional lower-case kind, a date, and a head that is ``(session `<name>` on <host>)``, ``(session `<name>`)``, `(n/a)`, or `(person)` on a decided line;
> - continues with ` — `, text that ends a sentence and names no field, ` Context: <words>.`, and ` Due: <date>.` on every kind but `fyi`;
> - may then carry replies, then `Answers:` as *A new item* says a kind takes them (a decided line may carry any or none), then `Decided:`;
> - holds nothing else, one space between parts.
>
> Fields inside a reply's words or a `Decided:` text are the person's and are not counted. `item_problem(line)` names why a line is not in that form, or gives None. It checks the item line alone, never its detail block, which stays the person's prose. `canonical_item(line)` rewrites a line into that form, moving `Due:` to its place and spelling it so, and refuses any rewrite that would change the line's item key or lose a word. Consumers persist keys, so a format pass that moved an item's key would break what they hold.
>
> **The gate** is `board_problems(board, old)`: the faults of each open line (every `- [ ]` line at any indent, but an open twin of a closed one) whose item key no line of `old` (open or closed) has. A line an edit only snoozed, decided, replied to or ticked keeps its key, so a line is judged once, when it is added, and a board that was never in the form has no flag day.

### Fixture cases (§2)

These go in `fixtures/edit/cases.json`, as `item_problems` (a line → its problem or None), `canonical_items` (a line → its rewrite, or the refusal) and `board_problems` (an `old` text and a `new` text → the list).

- **`item_problems` None:** each §1 written case's line; a `decided_line()` line; a snoozed line; a decided line; a replied-to line; a line replied to with `see Due: 2026-05-01`; a line decided with `Context: x` and with `b (default)`.
- **`item_problems` faulted:** an undecided line with a `(person)` head; an unknown word before the date; a head with no backticks; a head with `, branch x`; no `Context:`; `Due:` before `Context:`; an fyi with a `Due:`; an undecided decide with no answers; an act with answers; an indented line; a closed line ("not an open item"); a capitalised `Decide`; a decide with two marks.
- **`canonical_items`:** `due: 2026-01-20` respelled; a missing date period added; `Due:` moved from before Context to after it (the key unchanged); the same with an unpunctuated text, refused; a `Due:` inside the text's prose, refused; `Due:` before Context with `Answers:` after Context, refused; `Context: x Due: D.` given Context's period; missing Context refused; a head with no backticks refused; an fyi with a `Due:` refused; a `Due:` after `Answers:` refused; an already canonical line returned unchanged.
- **`board_problems`:** a faulted line in `old`, untouched, is not judged; the same line snoozed is not judged; a new hand-typed faulted line is judged; a new `item_line()` line passes; `old=None` judges everything open.

## §3. The archive

### `archive_closed(board, archive) -> tuple[str, str]`

`archive_closed` returns the board and the archive after the move.

- **What moves:** each closed item line, with its detail block, and each open item line whose key equals a closed line's key, with its detail block (C5). They move in board order and byte for byte, each line keeping its own line ending. The board is split with `splitlines(keepends=True)`. An item's detail block is the reader's (`detail_block()`'s rule) applied to those raw lines: the lines right after the item that are indented deeper than its `-`, ended by a blank line, a line no deeper, or another item line. A whitespace-only line counts as blank.
- **Refused shapes**, which a person straightens first, so that nothing is split: a moving item that is indented (nested under another item); a moving item followed by a deeper item line (a child that would be orphaned); and a moving item whose block is ended by a blank line followed by a line deeper than the item (a block broken by a blank line, which would move only its first half).
- **The board:** those lines are taken out, and every other line is kept byte for byte, preamble included. Where a removal would leave two blank lines in a row, the removed run takes the blank line before it; at the start of the file, it takes the blank line after it; and at the end of the file, it takes the blank line before it, so the board ends as it did. A section left with no items is left as it is. What a consumer writes there (the seed's `- (none)`) is the consumer's.
- **The archive:** its text is kept byte for byte, and the moved lines are appended. A missing final newline is added first, in the archive's own line ending (`\r\n` when its first line ends so, else `\n`). When its last non-blank line is not an item or a detail line, the moved lines are separated from it by one blank line, and a blank line already at its end counts as that one. An empty or whitespace-only archive becomes the moved lines alone. The archive's title and prose are the consumer's, written when the file is first made.
- **Refused:** a board with no closed item; and a result whose read-back differs. The read-back requires `parse_board()` of the new board to equal `parse_board()` of the old one (which already leaves twins out), compared on every field but `line` (which shifts when lines above an item move); `closed_items()` of the new board to be empty; and the archive's new tail to equal the moved lines.

### `archive_subject(tool, count, session=None) -> str`

`archive_subject` returns `<tool>: archive <count> closed items (session <name>)`, or `closed item` when `count` is 1, with `n/a` when there is no session; `count` is the closed items moved, twins not counted. It refuses a `tool` holding whitespace or a parenthesis (`subject_kind()` reads a subject's tool as one word), a `count` that is not an int of 1 or more, and a session name holding whitespace or a parenthesis. `subject_kind()` reads this subject as `archive` (C7).

### SPEC text (§3)

In *The board*, the first paragraph's sentence "Items are never deleted; closed ones are archived in bulk once ten or more sit on the board." (wrapped across two lines in `SPEC.md`) is followed by:

> The archive moves them (`archive_closed(board, archive)`, v2.3): each closed line with its detail block, and any open line whose key a closed line shares, in board order and byte for byte, appended to the archive's text. Every other board line stays byte for byte. It refuses a moving item that is nested, that has a nested item under it, or whose detail block a blank line breaks, since it would split them. When to archive is the consumer's; `ARCHIVE_AT` is the threshold it reads. The archive is not one of the four edits under *Edits*, which each rewrite one line.

and the kept sentence's "closed ones are archived in bulk once ten or more sit on the board" becomes "closed ones are archived in bulk, ten (`ARCHIVE_AT`) being the threshold a consumer reads".

In *Edits*, in the commit-subject paragraph, after the sentence about `append`:

> The archive's subject is `<tool>: archive <n> closed items (session <name>)` (`archive_subject()`), `<n>` the closed items moved.

The paragraph's last line becomes:

> `subject_kind()` names a subject `edit`, `append`, `archive` or (a rank write, above) `queue`.

### Fixture cases (§3)

These go in a new `fixtures/archive/` directory: `<case>.board.md` and `<case>.archive.md` in, `<case>.json` out (the two texts, or the refusal), run by `fixtures/run.py`.

- `basic`: three closed items, two with detail blocks, among open ones in two sections;
- `twins`: an open line and its closed twin, both moved;
- `empty`: an empty archive;
- `prose`: an archive with a title and a paragraph, so a blank line is inserted;
- `blanks`: items separated by blank lines, so the blank collapse applies;
- `crlf`: CRLF line endings kept, and an archive with no final newline;
- `lead`: a closed item as the board's first item line, right after a blank line;
- `nested`: a closed item indented under an open one, refused;
- `child`: a closed item with an open item nested under it, refused;
- `broken`: a closed item's block broken by a blank line, refused;
- `none`: no closed item, refused.

`subject_kinds` gains an archive subject, and a new `archive_subjects` list covers the subject: one item, several, no session, and a tool holding a space, refused.

## Versions (all three builds)

The last build adds to *Versions*:

> **v2.3 gives the board writers** (*Edits*, *The board*): `item_line()` writes every kind with its answers and detail block, `item_problem()`, `canonical_item()` and `board_problems()` say what the writers write, and `archive_closed()` and `archive_subject()` move closed items. Nothing is read differently: v2.2 reads every line v2.3 writes, and the item key is unchanged. `item_line()` now refuses a call it used to answer with a wrong line (a field name in its text or context, a host with no session, a name holding whitespace or `` ` , ; ) ``, a `today` that is not a date). It writes no `None` host, adds no period after text ending in `?`, `!` or several periods, and drops a context's own final period, so the line it writes for those inputs, and that line's key, differ from v2.2's. A line already on a board keeps its text and its key.

## The builds

Each build is its own entry, `Part of: TD-008`, with no Kind:

| build | implements | Blocked by |
|---|---|---|
| B1 | §1, `item_line()` | — |
| B2 | §2, the item gate | B1 (its rules are B1's form) |
| B3 | §3, the archive, and the *Versions* paragraph | B2 |

Each build's Done when includes its `SPEC.md` text landing with the code and fixtures. All three change *Edits* in `SPEC.md` and `fixtures/run.py`, so they land in series, and B3, the last, adds the *Versions* paragraph. B3 needs nothing from B2's code; the order keeps the shared files from conflicting. The release (v2.3) is the person's. The consumers follow, each on its own ledger, never filed from here:

- **agent-cadence:** its `board.py` entry (TD-008's *Related*): the CLI over these writers, `fmt` through `canonical_item()`, the gate through `board_problems()`, and the seed board header's `Format:` line given backticked session names, the form the gate accepts.
- **ShiftLead:** the vendor PR that takes v2.3. Its board write-back may take the new keywords, which is its own choice.

## Not in this design

- A change to `item_key()` or to how any line is read. Either would be a major version (SPEC *Versions*).
- Any check of the detail block's content. It stays the person's prose.
- When to archive, the archive file's title, and what an emptied section shows. All three are the consumer's.

# TD-161: the merge gate's verdict for a question a tool asks

**Status:** Draft 7, 2026-11-23 (session lb-designer). Class: **wide** (a change to the published, vendored format:
a new verdict, subject reader and entry writer; cap 6 rounds, cadence.md §4.8). The rounds ended by the stop rule
after round 4, and Paul bought rounds 5 (TD-163) and 6 (TD-164), the cap, after which they end: build-changing findings per round
2, 1, 1, 0, 1, 0, all applied. Round 5's one names the exact nonce test in D2 and D3; its closing fact-check and repeats
raised 2 build-changing (a stale count, an ambiguous SPEC clause) and 4 minor, all applied. Round 6 read those fixes and
raised 3 minor, all applied: D2 refuses an archived entry and arguments of the wrong type, and the SPEC's verdict clause
states the nonce test as D2 does. Its closing fact-check and repeats raised 7 minor and nothing build-changing, all applied. Round 6's fixes (D2's archived-entry and argument-type
refusals, the SPEC's nonce clause, D3's `\r` wording) are unread by a design review, so the builder checks them. The record:
[docs/reviews/TD-161.md](../reviews/TD-161.md).

**Entry:** [TD-161](../ledger/TD-161.md). agent-cadence's TD-297 waits on its release.

## The problem

ShiftLead's home now asks the person about one entry by landing a PR at once, with no review. The PR adds
`decision (<p>)` to the entry, writes its Ask, Context, Answers and Lifts, logs the question, and adds the `decide`
item the gate sweep would file. Its subject is `<tool>: ask <p> on TD-n (session n/a)`.

The merge gate has verdicts for a board edit and for a lift, but none for this write. agent-cadence's weekly audit
therefore reads each one as landed without review, and a real unreviewed merge can hide among them. No person's press
stands behind this write, so the title proves nothing. A verdict has to prove from the two trees that the PR only
holds one entry back and asks about it.

## What is already settled

- SPEC *The merge gate's verdicts*: a verdict is a pure function over a PR's trees, returning
  `{carve_out, flags, review}`, and `review` names the first condition that fails.
- `ledger_lift_verdict()` is the pattern: it recomputes the write through the module's own writer, `lift_gate()`, and
  compares bytes.
- The package holds no git, network or consumer knowledge. The verdict names no tool, and takes any `<tool>` token.
- A minor release adds a verdict and a writer without changing what a reader reads (SPEC *Versions*).

## What the writer does

Read from ShiftLead at `715dab451ea0`, and unchanged at its main on 2026-11-23. A prototype ran that writer's sequence
through ShiftLead's vendored v3.5 and through this repo's main, on invented entries.

1. It refuses an entry that already carries a gate `GATE_DECISION_RE` matches in `gate_items()`. That test misses three
   forms that still block the entry: the old `decision (bob) — words`, a retired role such as `decision (designer)`,
   and the retired `hold`.
2. It sets Blocked by to `<raw>, decision (<p>)`, which the canonical form reorders (`until 2026-11-02` becomes
   `decision (ann), until 2026-11-02`), and logs `gate added: decision (<p>)`.
3. It writes Ask, then Context, then Lifts, then Answers, replacing any earlier ones. Its first ledger check runs
   while the earlier Answers still stand, so an entry whose earlier Answers the sweep cannot offer is refused.
4. It notes `asked by the stage record: <nonce>`. A note first lifts any notes in the Status into the Log, so the Log
   can gain **more** than two lines and the Status can change.
5. It calls `sweep([that one entry], [own board], {}, <UTC day>, <local day>, reask_days=0, repo=repo)`, with no
   `resolve`. Because the sweep sees one entry, a blocker that is open elsewhere in the ledger does not defer the
   question. It takes the one `decide` filed, and ignores any `act`.
6. It adds that item with a random id, `Added` and `Due` both its local day, and no session or host.

## The design

### D1. The subject

`ASK_SUBJECT_RE` beside `LIFT_SUBJECT_RE`, matched whole:

`(?P<tool>LOG_TOKEN): ask (?P<person>PERSON) on (?P<id>TD-[0-9]{1,18}) \(session (?P<session>LOG_TOKEN)\)`

`ask_subject_parts(line)` reads it back as `{tool, person, id, session}`, or None.

**`subject_kind()` does not change, and stays None for this subject.** agent-cadence's review row branches on that
kind to pass tool edits, so a new kind reaching an older consumer must not be able to change what it passes. The
consumer calls `ask_subject_parts()` to choose this verdict.

### D2. The entry writer: `ask_gate()`

`ask_gate(text, person, ask, context, answers, lifts, nonce, today, declared_fields=())`, `today` a date or
`YYYY-MM-DD` as for `edit_entry()`, returns the entry after the write in steps 2 to 4 above, through `edit_entry()`,
as `lift_gate()` does for a lift. `answers` and `lifts` are lists,
joined with ` | `. It is public so the verdict and a writer share one definition. It raises `Refused` when:

- the Blocked by holds **any** decision, by `parse_gates()`: an item of `decisions`, **any** `retired` item (a role
  or `hold`, each of which `_names_decision()` reads as a decision), or a `bad` item matching
  `re.match(r"decision\b", item, re.IGNORECASE)`. So `decision (bob) — words` and `hold` refuse, and
  `decisions (bob)` does not. The writer's own test misses the old form, a retired role and `hold`, and a verdict
  without this rule passed a PR adding a second person beside one;
- the entry's text contains `asked by the stage record: <nonce>` as a substring, anywhere, as the writer tests it;
- the entry holds a header `Ask`, or `declared_fields` declares `Ask`, as `plan_edit()` refuses;
- the entry's Status is an archived one (`first_word(status)` in `ARCHIVED_WORDS`), as `lift_gate()` refuses;
- `ask` or `context` is not a string, `answers` or `lifts` is not a list of strings, or `declared_fields` is not a
  tuple, list, set or dict of strings (a dict's keys), so `None` and a bare string refuse (`declared()`'s dict of names passes; `answers`
  as a bare string would join character by character);
- `person` is not a whole `PERSON` for which `is_person()` holds, or is a retired role (`person.lower()` in
  `RETIRED_ROLES`), `nonce` is not a string for which `re.fullmatch(r"\S+", nonce)` holds and which encodes as UTF-8
  (Unicode whitespace, as `str.split()` reads it, since the Log note collapses it; a nonce the note writer itself
  refuses, such as an unclosed `<!--`, is refused as that writer does), or `text` is not exactly one entry. Every refusal is
  `Refused`, never another exception.

### D3. The verdict: `ask_pr_verdict()`

`ask_pr_verdict(base_tree, head_tree, files, subject, commits, created_at, merged_at, repo)` returns
`{carve_out, flags, review}`, its arguments and `flags` as `ledger_lift_verdict()`'s. The first failing condition, in
this order, names the review:

1. A v3 board at the base and head (`ask-no-board`, `ask-board-v2`), whose base declares `People:` (`ask-no-people`).
2. The subject is an ask, and the PR is one commit (`ask-subject`).
3. The base ledger is v2, and holds the subject's entry open in one file directly in `LEDGER_DIR`, and the head holds
   that file open (`ask-entry`).
4. The set of paths the trees change equals `files`, and is exactly that file and one added path directly in
   `BOARD_DIR`, named `<item id>.md` (`ask-files`).
5. The head file's text, less its one final newline and split at its last `\n`, ends in exactly
   `- T: asked by the stage record: <nonce>`, that line holding no `\r`, `T` a real `YYYY-MM-DD` and `<nonce>`
   matching `\S+` whole, as in D2, and the head holds exactly one each of Ask, Context, Answers and Lifts
   (`ask-sections`). Each section's **words** are read exactly: from `canonical(head)`'s section, what follows the
   `**Name:**` lead, less one separating space if there is one and one final newline if there is one, and never
   stripped, since the writer keeps edge whitespace.
6. The head entry is `ask_gate(base file, person, <head Ask>, <head Context>, [<head Answers>], [<head Lifts>], nonce,
   T, <the base ledger's declared fields, `declared(<ledger>)[0]`>)`, byte for byte, any refusal failing too (`ask-bytes`).
7. `check()` of the head ledger at `today=T`, with each tree's rank file, against the base ledger as `old`, adds no error the base lacks,
   `cross-repo` and standing flags aside, flags compared as the ledger writer's `gate()` compares them, by kind, id and
   text less its leading ⚠ or ℹ (`ask-check`). This refuses Answers
   the sweep cannot offer. It reads only the head, so it is deliberately more lenient than the writer's first check,
   which also refuses unusable **earlier** Answers: a PR replacing them with usable ones holds the entry back and asks,
   which is all the carve-out has to prove.
8. The person is on the base board's `People:`, in any case (`ask-people`).
9. The added item reads as an item, its id's date is its `Added` day `D`, and it is byte for byte `item_file()` of the
   one `decide` that `sweep([head entry], [_tree_board(base_tree, repo)], {}, T, D, reask_days=0, repo=repo)` files, with `D` as its Due
   and Added and no session or host. A sweep filing no `decide` or several, or a refusal from `item_file()`, is
   `ask-item` too.
10. `T` lies within a day of `created_at` and not after the merge (else `created_at + 1`), and `D` from `created_at − 1`
    to the merge (else `created_at`) `+ 1`, the board's local day running up to a day from UTC (`ask-date`).
11. `flags` is empty (`ask-flagged`). This is defensive: `ask_gate()` keeps every earlier item, so a PR that reaches
    it has no decision to lose, and it has no fixture.

A `Refused` from `tripwire()`, which runs first, or from the dates and `commits`, escapes, as for the lift verdicts.

The recomputation compares **gates as the canonical form writes them**, so the reorder needs no special case. It gives
the sweep **the one entry**, as the writer does: given the whole ledger, a deferred question would be sent to review.

### D4. Version skew: no tolerance

ShiftLead vendors v3.5. From v3.6 the sweep adds a clause to the item's context when the board holds a **near item**,
as SPEC *The gate sweep* and `_near_items()` define it: broadly, an open or decided item, of any kind but `fyi`, that
names the entry, that `covers()` does not find for the gate, and that is neither about another gate nor the sweep's
own. A work order about the entry is one, so this is not rare. A verdict at v3.6 or later differs from a
v3.5 writer's item in exactly that case, and the prototype confirmed it: such a PR takes review as `ask-item`, and
every other case passes.

**The verdict does not tolerate it**, at that breadth too. Accepting both forms would permanently let a writer leave
out a clause the format says the person reads, to save a window that closes when ShiftLead syncs. Until then the
affected PRs show in the audit as unreviewed, which is the safe direction: a person reads a few real merges, and no
unreviewed change is passed. ShiftLead's sync to the release ends it.

The same holds for D2's three forms the writer misses. A v3.5 writer lands a question on an entry holding one, and the
verdict sends that PR to review as `ask-bytes`, since a second decision beside a standing one is exactly what the
carve-out must not pass. Those PRs stay visible in the audit until ShiftLead adopts `ask_gate()`.

## Options set aside

- **Compare the diff by rule rather than recompute it** ("Log gains exactly two lines"). It is false for an entry with
  Status notes, and it would have to restate the canonical form.
- **Keep the entry write private to the verdict.** The same code exists either way, and a public writer is what lets
  ShiftLead stop keeping its own copy of the sequence.
- **Add an `ask` kind to `subject_kind()`.** See D1.
- **Give the sweep the whole ledger.** It would not match what the writer computed.

## SPEC text

The version below is v3.6, which is untagged as this is written. The build uses the next minor with no tag when it
lands.

**In *The merge gate's verdicts*, a new paragraph directly before `` `uncovered_decisions(base_tree, ``:**

> `ask_pr_verdict(base_tree, head_tree, files, subject, commits, created_at, merged_at, repo)` (v3.6) returns
> `{carve_out, flags, review}` for a PR that asks a person about one entry, its arguments and `flags` as
> `ledger_lift_verdict()`'s. `carve_out` says the diff is exactly one `ask_gate()` write and the one `decide` the sweep
> files for it; no person's press stands behind it, so the trees are the whole proof. Otherwise `review` names the
> first condition that fails, in this order:
> - a v3 board at the base and the head (`ask-no-board`, `ask-board-v2`), whose base declares `People:`
>   (`ask-no-people`);
> - the subject is an ask (`ask_subject_parts()`), and the PR is one commit (`ask-subject`);
> - the base ledger is v2 and holds the subject's entry open, its file directly in `LEDGER_DIR`, and the head holds
>   that file open (`ask-entry`);
> - the paths the trees change are exactly `files`, that file and one added item file directly in `BOARD_DIR`
>   (`ask-files`);
> - the head file's text, less its one final newline, ends in the line `- T: asked by the stage record: <nonce>`, `T` a
>   real day and `<nonce>` one or more characters none of them Unicode whitespace (`str.isspace()`), that line holding no `\r`, and the head holds one each of Ask, Context, Answers and Lifts, whose words are read exactly, less the
>   one space after the lead and one final newline (`ask-sections`);
> - the head entry is `ask_gate()` of the base file with those words, `nonce`, `T` and the base ledger's declared
>   fields, byte for byte, any refusal failing too (`ask-bytes`);
> - `check()` of the head ledger at `T`, with each tree's rank file, against the base adds no error, `cross-repo` and standing flags aside (`ask-check`);
> - the base board's `People:` lists the person, in any case (`ask-people`);
> - the item's id carries its `Added` day `D`, and the item is `item_file()` of the one `decide` that
>   `sweep([head entry], [base board], {}, T, D, reask_days=0, repo=repo)` files, `D` its Due and Added, with no session
>   or host, a sweep filing no `decide` or several or a refusal being this too (`ask-item`);
> - `T` lies within a day of `created_at` and not after the merge (else `created_at + 1`), and `D` from `created_at − 1`
>   to the merge date (else `created_at`) `+ 1` (`ask-date`);
> - `flags` is empty (`ask-flagged`).
>
> The sweep is given the one entry, as the write gives it, so a blocker open elsewhere in the ledger does not defer the
> question. The verdict recomputes with its own release: a writer on an earlier release whose item differs, as a v3.5
> writer's does when the board holds a near item (*The gate sweep*), takes review. As for the lift verdicts, a `Refused` from
> `tripwire()`, the dates or `commits` escapes, and a direct commit of this shape is the consumer's to refuse.

**In *Ledger entries and their edits*, a new paragraph at the end:**

> `ask_gate(text, person, ask, context, answers, lifts, nonce, today, declared_fields=())` (v3.6) is one entry after a
> tool asks a person about it: `decision (<person>)` added to its Blocked by with every earlier item kept, its Ask,
> Context, Lifts and Answers written (replacing earlier ones), and the Log note `asked by the stage record: <nonce>`.
> It refuses an archived entry, an `ask` or `context` that is not a string, `answers` or `lifts` that is not a list of
> strings, `declared_fields` that is not a tuple, list, set or dict of strings (a dict's keys), an entry whose Blocked by holds any decision (`decision (<p>)`, a retired item, or an unreadable item
> matching `decision\b` at its start in any case), one whose text already contains that note, a person that is not a
> `PERSON` or is a retired role, a nonce that is not a string of one or more characters, none of them Unicode whitespace, that encodes as UTF-8, a nonce the Log note writer refuses (such as an unclosed `<!--`), a text that is not one entry, and one whose Ask is a header field or a declared field.

**In *Edits*, directly after the paragraph on the commit subject of a ledger lift:**

> **The commit subject of a tool's question** (v3.6) is one line, `<tool>: ask <p> on TD-n (session <name>)`.
> `ask_subject_parts(line)` reads it back as `{tool, person, id, session}`, each part as written, or None.
> `subject_kind()` does not name it, so a consumer that passes a named kind does not pass this one.

**In *Appendix: grammar*, directly after the `lift-subject` production:**

> ```
> ask-subject       ::= log-token ": ask " person " on TD-" digit+ " (session " log-token ")"
> ```

**In the appendix's notes, directly after the paragraph on `lift-subject`:**

> `ask-subject` (v3.6) is a tool's question's commit subject, judged by `ask_subject_parts()` not None. The reader
> matches the whole line, with no trailing newline, and its digits are ASCII and at most 18, as `lift-subject`'s are.

**In *Versions*, after whichever paragraph is newest when the build lands:**

> **v3.6 adds the verdict for a tool's question** (TD-161; *The merge gate's verdicts*, *Ledger entries and their
> edits*, *Edits*): `ask_gate()`, `ask_subject_parts()` and `ask_pr_verdict()`. No parse, field, Log line, item key or
> canonical form changes, and `subject_kind()` reads every subject as before.

## Fixtures and tests

`fixtures/verdict/cases.json` gains an `ask` list, its base and head trees laid out as `ledger_lift`'s, and
`fixtures/run.py` runs it through `ask_pr_verdict()`, reporting `missing` on a module older than the release.

**Carve-outs:** a plain entry; an `until` gate (the reorder); an id and an `until`; an open blocker (no deferral); a
`<repo>#TD-n` blocker; earlier usable Answers replaced; a `(default)` answer; Status notes lifted into the Log; a
two-paragraph Context; a Context and an Ask with edge whitespace; a recent `kept waiting` line; the local day one behind and one ahead of UTC.

**Review, a case for each kind but the defensive `ask-flagged`**, including the Fix's list: no board; no `People:`; the
entry archived, absent, and a v1 ledger; another field changed; another entry changed; another
board item added; an existing gate dropped; a `decision (<q>)` already standing; the old form `decision (<q>) — words`
standing; a retired role standing; a retired `hold` standing; a repeated nonce; an extra Log line; Answers no sweep can offer; a person not on `People:`; an item with a
changed word; an id whose date is not `Added`; two commits; a subject naming another person; a v2 board; dates out of
window; and, for D4, a head item lacking the clause when the near item is an open `decide`, an `act`, and a decided item (an
`fyi` and an item about another gate carve out); a Log whose last line is not the question's. The extra-Log-line case
inserts its line **before** the question's, so it reaches `ask-bytes`; appended, it is the last-line case.

Each head entry must be byte-exact `ask_gate()` output, except in the cases that tamper with it. An item the sweep
would not file (a person off `People:`, a changed word, a wrong id date) is written by hand. Case names must be unique
across `verdict`, `ledger_lift` and `ask`, which share `cases/<name>/`. The build generates the case trees with a throwaway script and
commits the results, keeps edge-whitespace cases out of any editor's reach, writes `expected.json` with
`fixtures/run.py --write`, and leaves `fixtures/MANIFEST` for the release PR, as the
earlier v3.6 builds did.

`fixtures/grammar/cases.json` gains an `ask-subject` set with the five groups `tests/test_grammar.py` requires of
its start (`ask-subject`, `log-token`, `person`, `person-part`, `digit`), and
`fixtures/run.py`'s grammar table gains its reader, guarded by `hasattr` as `lift-subject`'s is.

`tests/`: `ask_gate()` agrees with the sequence of `plan_edit()` and `edit_entry()` calls it replaces, on the
carve-out entries, `subject_kind()` is None for an ask subject, and `ask_gate()` refuses a retired role
as `person`, and an empty nonce, one holding a space, one holding a non-ASCII space (`\xa0`), a non-string nonce, a lone surrogate, an unclosed `<!--`, an archived entry, a non-string `ask` and `context`, a bare string and a list holding a non-string as `answers` and as `lifts`, and a bare string and `None` as `declared_fields`, each as `Refused`.

## Consumers

- **agent-cadence TD-297** vendors the release and adds the review row, choosing this verdict by
  `ask_subject_parts()`.
- **ShiftLead** needs no change for the verdict to work. It should adopt `ask_gate()`, keeping its own ledger check
  around it, and so pick up the refusal of the three missed forms when it next syncs: on Go, that is handed to its question seat with `ao td add --repo ShiftLead/shiftlead`.

## Builds (to file on Paul's go)

- **B1** D1 to D4: the subject reader, `ask_gate()`, `ask_pr_verdict()`, the SPEC text above, the fixtures and tests. A
  grinder takes it. A minor release, cut by Paul, which may share v3.6 with TD-157, TD-158 and TD-160.

Paul's choice at this point: Go (a session files B1), one more design round, or Hold with a note.

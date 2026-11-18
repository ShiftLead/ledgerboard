# The ledger and board formats — versions 1 to 3

This is the formats' one definition in prose; the module, `ledgerboard/__init__.py`, is the one implementation and
`fixtures/` the cases any implementation must reproduce. Where this text and the module disagree,
the fixtures decide, and the disagreement is a bug here. From v2.5 the set names the release it belongs
to (*Versions*). *What to do* with a field — lanes,
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
feature), `Added`, `Status`, `Blocked by`, `Location` (a body section from v2.7: *Retired words*), `Part of` (v2.1), `Escaped from` and `Id take` (v2.2). A
`Priority`, `Type`, `Blocked by` or `Part of` written below the header block is still read, and flagged
(ℹ `below-header`), and `check()` reads on past it: it never raises on an entry `entries()` reads (TD-049).
A `Priority` other than High, Medium or Low (v2.4) is read after Low and flagged (`priority`): an error on
an entry the edit changed, ℹ on a standing ledger.

**`Escaped from`** (v2.2) — `**Escaped from:** TD-n` or `<repo>#TD-n`, on a defect: the design entry
whose review should first have caught it. Its value is free, so no `Fields:` line declares it; the
format only parses it, and what it resolves to is the consumer's.

**`Id take`** (v2.2) — `**Id take:** <nonce>`: the 32-hex `take:` nonce of the counter take that
handed the entry its id. It is provenance, never an assignment, and nothing routes on it. It is
judged only where its id is new; after the merge it is inert, and no tool strips it. From v2.4 the
format defines the counter and the judgement (*The next id*); reading and writing the counter are the
consumer's.

**`Fields:`** — a ledger may declare its own fields' vocabularies once, on one preamble line before
the first entry: `Fields: Owner = builder | designer; Kind = build | design-first`. A declared
field's value outside its vocabulary is an error; an undeclared field is read but not validated.
The format's own fields are never redeclared.

**`Blocked by`** — comma-separated items: ids, each `TD-NNN` or `<repo>#TD-NNN` (another repo's
entry; `<repo>` as below), then **gates** (v2.4), each one of
- `decision (<person>)` — a person owes an answer, a go included; `<person>` is a person's name (*Appendix:
  grammar*), compared case-insensitively. The entry carries an `**Ask:**` section saying what the
  person owes: without one, `check()` flags it (`ask-missing`; an error on an entry the edit changed —
  its whole text, as for the Log — ℹ on a standing ledger). The converse is flagged too (v3.1): an open entry with
  an Ask — a body section led `**Ask:**`, or a header `Ask` field — whose `Blocked by` names no decision, and
  which is not answered, waits on a person that no reader shows (`decision-missing`; an error on an entry the edit
  changed — its whole text — ℹ on a standing ledger). Here a retired item (`hold`, a role in `decision (…)`) and
  an item in the old decision form count as a decision, since each has its own flag whose cure writes one; an
  `until` or an `event` does not. An entry is **answered** when the last of its Log's `gate added: decision (…)`,
  `gate reassigned:`, `kept waiting: decision (…)` and `gate lifted: decision (…)` lines is a `gate lifted:
  decision (…)`: the Ask stays as the record of the question, as *Lifting is text* keeps an event's section.
  "Last" is in file order. A Log that cannot be read (one `log_problems()` faults, or two Logs) answers nothing,
  and the Log alone decides, on an edit as on a standing ledger. An `**Ask (…):**` lead is its own section,
  never an Ask. The cure is the gate (`set`), or, where nothing waits on a person, the Ask removed: `edit
  --section Ask --remove`, or a header `Ask` emptied with `set`. Which `Owner` values name a person is a
  ledger's own, so an Owner is never read as a wait here. A decision reassigned more than twice to
  reach the person it names now is noted (ℹ, `gate-reassigned-often`, v2.4; `reassigns()` counts the run of
  `gate reassigned` Log lines that led to it), scoped by the entry's whole text.
- `until YYYY-MM-DD` — not before that UTC date. Once today reaches it the gate no longer holds, and
  `check()` notes it (ℹ, `until-past`) until it is dropped.
- `event (<name>)` — something outside the ledger; `<name>` is `[a-z0-9-]+`. The entry carries its
  `**Event (<name>):**` section, which names a typed check (*Events*, below). It blocks until the text
  says otherwise.

The writers write the ids in the order given, then the gates in that order (decisions, `until`,
events), and the words lower-case; the reader reads the gates' words in any case. An entry names at most one decision per person,
one `until`, and differently named events; more is flagged (`gate-repeated`; an error on an entry the
edit changed, ℹ on a standing ledger). A `Waits` field is never read as a gate.

**An entry's own answers** (v3.3). An entry that waits on a person may name the answers it offers in a
one-line body field `**Answers:**`, in the form of a board `decide`'s `Answers:` value (*The board*: each
`<label>` or `<label> — <consequence>`, one marked ` (default)` at most, forms among them), and which of them
lift its gate in a one-line body field `**Lifts:**`, each an answer's whole label (a form by its offered label,
`Hold: <note>`); with no `**Lifts:**`, `Go` lifts. Each is a body section that is its lead's line alone, HTML
comments dropped first, its lead's name matched as every lead's is (case aside, whitespace folded); its value
is the line after its lead's bold run, leading whitespace removed, then one `:` where the bold run held none.
A header field of either name, and a qualified lead (`**Answers (…):**`), are not these.
`entry_answers(entry_text)` reads them: None when the entry has neither; `{"answers", "default", "lifts"}` when
they can be offered (each answer with its ` (default)` mark removed and a literal `|`, the marked one's index or
None, the `**Lifts:**` labels or None); and it raises `Refused`, naming why, for an `Answers` or `Lifts` lead in
the body, outside a code fence that closes, that starts no section (glued to the line before it, or indented),
a bold run named `Answers` or `Lifts` inside either field's line (a run tried at every `**`), two answers whose
labels are equal with case and whitespace folded, an entry with
either field that `_entry_parts()` refuses, two of one name, a field whose section runs past its line (a line
glued below it, or a later paragraph before the next lead), a `**Lifts:**` with no `**Answers:**`, an empty
`**Answers:**` or `**Lifts:**`, two answers marked, answers `item_file()` refuses as a `decide`'s `answers`,
`default` and `lifts` (fewer than two among them), and answers of which none lifts (its reason naming the labels
read). It names the first fault found. `check()` flags an open entry
whose `Blocked by` names a decision and which it refuses (`answers-unusable`, its text ending *(the first fault
found)*; an error on an entry the edit
changed — its whole text — ℹ on a standing ledger). The gate sweep offers them (*The gate sweep*).

**Pickable is derived, never written:** `pickable(…, *, today)` takes `today`, the UTC date, always.
An entry is pickable when it has no `Blocked by`, or every entry it names is archived and it has
no `decision`, no `event` and no `until` after today — and no open entry is `Part of` it (below).
An item that cannot be read, a retired item (below), an entry in neither the ledger nor the
archive, or another repo's entry the reader cannot resolve keeps the block. Each record's
`blocked_by` lists what holds it: its open ids, then its gates that hold, then each item that keeps the
block unread. A written `**Pickable:**` line is only a field.

**The old form** `decision (<who>) <text>` — a decision followed by anything but a comma or the end of the
line — was read by v2 as a decision by `<who>`. v3.0 does not read it: it is an unreadable item, which keeps the
block, names no holder, and is an error. Its replacement is `decision (<person>)` with the text in `**Ask:**`.

**Retired words** (v2.4). A retired word is never reused for a new meaning; the list grows only. v3.0 reads no
retired field, and no `Blocked by` item in the old decision form, for its old meaning; a retired item in `Blocked
by` is read as before. `check()` names each it meets *retired*, with what replaces it, rather than unknown: a
retired field — `Waits`, `Taken by`, a header `Resolved` or a header `Location` — is an error (`retired`) on every
entry, open or archived, of a ledger that declares major 2 or more, whether or not the edit changed the entry
(never `standing`), and ℹ on a v1 ledger; so is a `Blocked by` item in the old decision form (*The old form*,
above), which is also an unreadable item, and so an error on an open entry of a v1 ledger too (standing ℹ, as any
unreadable item is, on an untouched open entry when `check()` is given a base), and ℹ on an archived one there,
whose unreadable item no reader flags; another retired item in `Blocked by` is ℹ and keeps the block; and a Status
outside the closed set is an error (*The closed Status set*). A retired error's text ends *v3.0 reads no such
form: on an open entry* followed by its field's cure — *remove it with `set` (an empty value)* for `Waits` and
`Taken by`; *move its value with `edit --section Location`, then remove it with `set`* for a header `Location`;
the same with `--section Resolved` for a header `Resolved`; *write its text with `edit --section Ask`, then rewrite
it `decision (<person>)` with `set`* for the old decision form — then *; on an archived one by hand, then
`ledger.py fmt TD-n`*. That `set` adds a decision v3.0 did not read before, so it logs `gate added`, the gate's age
starts that day, and the merge gate wants a board item for it, as for any decision gained. The retired words, with
what replaces each:
- the fields `Waits` (a gate: `until` or `event`), `Taken by` (`Id take`), `Resolved` as a header field
  (the `**Resolved:**` body line of an archived entry) and, from v2.7, `Location` as a header field (the
  `**Location:**` body section);
- in `Blocked by`, the gate `hold` (`decision (<person>)` with an Ask) and a role in
  `decision (…)`, reserved by name — today `designer`. A retired gate keeps the block, and a retired
  decision is still a decision by its holder;
- the Status words `Designed`, `Built`, `Partly`, `Live` and `In` (`Open`, the stage in `Kind`), and `Done`,
  `Moved` and `OBE` (`Resolved`, `Superseded` or `Dropped`; on an open entry, archive it or `Open`). From v2.7 a
  Status outside the closed set is an error (*The closed Status set*), whose text still names a retired word with
  what replaces it; v2.x's `migrate` mapped each.

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
  | `host-log <source> [kind <kind>] [times <N>] "<text>"` (v2.5) | at least N (none: 1) counted records were read: records of the source, as resolved for the ledger's repo on this host (*Host-log checks*), of the kind if named, tied to the ledger's repo when the source maps `repo`, public when the ledger is, dated at or after 00:00 UTC of the day after the gate's `gate added` line (`gate_added()`), whose text contains the text; this wins over any error met while reading | fewer were read, and no error below applies, including when an existing source has no file or no record, or no longer reaches back to that day | never | before reading: `gate_added()` gives none; the host's configuration (the reader's) cannot be read or is refused, or names a path that does not exist; the source is private for a public ledger, or its root does not serve this repo or requires a `repo` mapping the source lacks; a kind is named against a source with none. While fewer than N were read: a file outside the host's allowed roots, not a regular file, or not the file its path resolved to; a file that cannot be read, an unsupported format, or a corrupt settled file; a read that would go past the reader's file, byte or time limit |

  A new type comes in a format PR and states all four outcomes. Every check is also an error when the
  host's own rule refuses it: a check reaches a repo only on the host's roster and at least as visible as
  the ledger's own repo, with read-only tokens.

  `host-log` (v2.5) reads logs on the host (*Host-log checks*), not a repo, so the roster and visibility rule
  above does not apply to it; *Host-log checks*' allowed roots and visibility take its place. Its source names
  and kinds are configuration, never the package's. A host with no host file, or whose host file has no table
  for the ledger's repo, or that declares no source of the check's name for it (once its configuration can be
  read; otherwise it is an error), gives no outcome for it, so it neither files nor closes an item about it, and
  a gate no host answers waits silently, past the sweep's age limit too. The count is one host's, never summed
  across hosts. The day after the gate was added is the first counted, so the event that prompted the gate
  never passes it, and an event later that day is not counted either. A gate lifted and added again counts from
  its new `gate added` line. Records are only appended, so a passed check stays passed while its check is
  unchanged (an edit that changes it dates the wait anew, *Edits*), and a source that no longer reaches back to
  the first instant counted reads not yet, never error. An error's reason stays on the host: the board's item
  has fixed words. Its evidence names a record on the host, and is the host's word: a reviewer cannot re-run it
  from the ledger.
- **Arguments are confined**, since anyone with PR rights can edit the ledger and a check runs with the
  host's credentials. `parse_check()` gives a `problem`, and `check()` refuses the section, for:
  - a `<repo>` outside the `<repo>` grammar (below);
  - an `n` that is not 1 to 18 of `[0-9]`;
  - a `commit` that is not 7 to 40 of `[0-9a-f]`;
  - a `host-log` `<source>` or `kind` token that is not 1 to 40 of `[a-z0-9-]` or starts with `-` (v2.5);
  - a `host-log` count that is not 1 to 3 of `[0-9]` with no leading zero; or arguments before the text other
    than the source, then optionally `kind` and its token, then optionally `times` and its count, in that order;
  - a `ref` that fails git's `check-ref-format --allow-onelevel` rules (a component starting with `.` or
    ending `.lock`, a control character, a space, any of `~^:?*[\`, `//`, a trailing `/` or `.`, `@{`, or
    `@` alone), or that starts with `-` or holds `..` or `:` — no option injection (`--output=x`), no
    revision syntax (`a..b`, `@{u}`, `ref:path`) — or holds URL or query syntax (`#%&=+`), whitespace,
    or anything outside printable ASCII, since a ref goes into a forge's API path or query;
  - a `path` that is absolute, has an empty, `.`, `..` or `.git` segment, starts with `-`, or holds a
    glob character (`*?[]`), URL syntax in a forge's API path (`#`, `%`), a quote, a backslash,
    whitespace, a control character or anything outside printable ASCII (`&`, `=` and `+` are literal in a
    URL's path, so `c++/x.h` is a path);
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
    says why;
  - `event-undated` (⚠, v2.5; one per gate): an `event (<name>)` gate whose one readable section's check is
    `host-log` and for which `gate_added()` gives none (no `gate added` Log line for it, or a `gate lifted`
    after the latest, or a Log that cannot be read), so the host has no day to count from; and, on an edit
    (`check()` given `old`), one newly carried, or whose `host-log` check changed, or whose check became
    `host-log` or whose `host-log` section is new (judged on `parse_check()`'s record: source, kind, count and
    text), and was not **dated anew**, since a changed question counts from when it was asked. Dated anew means
    all three: (a) the gate's `gate added` lines in the new Log, in Log order and compared as (date, gate)
    pairs over this gate's lines only, are its old ones followed by at least one more; (b) the last, dated L,
    has floor ≤ L ≤ `today`, the floor being the old Log's latest readable date, else the entry's `Added`
    date, else none, and lowered to `today` if after it; (c) when the old Log had a `gate added` line for the
    gate (the last, dated P), L is `today` or after P. An entry absent from the old ledger has an empty old
    Log; an old Log that cannot be read is never dated anew.
- **Lifting is text.** When a check passes, the host's tool PR removes the gate and logs `gate lifted:
  event (<name>) — by <host>; <type> passed; <evidence>` (*The Log*). **The section stays**, as an Ask stays
  after its decision lifts, so the entry still says what was waited for and how it was checked. A gate
  re-added with the same name reuses its section (or edits it); it never adds a second. A lifted gate
  never re-arms: a later regression is a new entry, or a new gate on a reopened one.
- What is not an event: anything whose telling needs judgment ("the page looks right") is work, an
  entry of its own that the waiting entry is blocked by.

**Host-log checks** (v2.5). A `host-log` check is answered by a host from logs on that host, through a
**reader** (agent-cadence's `hostlog.py` is the reference). **Which files of a source are read, and that each is
read once, are the reader's**, pinned by its tests; any reader follows the host rules below and passes those
tests. This section defines the count over the records a reader yields, and the host rules every reader keeps.

- **A record** is `{at, kind, text, id, public}`: `at` a UTC time; `kind`, `text` and `id` a string or none;
  `public` whether a ledger that is not private may count it. When a source names each record's repo, a reader
  yields only records whose repo equals the ledger's (compared without case; a record naming none is not
  yielded); otherwise it yields every record of the source.
- **Functions.** `first_instant(since)` takes the `date` of `gate_added()` and gives an aware UTC `datetime`;
  `count_host_log(records, chk, since, *, public_only)` gives `{"outcome": "passed" | "not yet", "count": <every
  counted record>, "evidence": <token> | None}`. Fixtures write `at` as ISO 8601 with `Z`. `chk` is
  `parse_check()`'s record, refused (`Refused`) when it has a problem or is not `host-log`; `since` is a `date`
  or a `YYYY-MM-DD` string, as other module dates (`utc_day`); a record whose `at` is not an aware `datetime` is
  refused; one whose `text` is not a string never counts; an aware `at` in another zone is ordered as given and
  written in the token after conversion to UTC. `fixtures/run.py` reads `at` with
  `strptime("%Y-%m-%dT%H:%M:%SZ")`, never `fromisoformat` (which refuses `Z` on 3.10).
- **What counts.** The first instant counted is 00:00 UTC of the day after `gate_added()` (`first_instant()`). A
  record counts when it is dated at or after that instant, its `kind` equals the check's (exactly, when one is
  named), its `text` contains the check's text (literally, case-sensitively), and, unless the ledger is
  private, it is public (an `internal` ledger, or one of unknown visibility, counts only public records).
- **The evidence** is the N-th counted record, ordered by `at`, then `id` (none first, then by code point):
  `<source>/<id>` when the record has an id of at most 80 characters that makes a valid token with no empty,
  `.` or `..` segment, else `<source>@<YYYYMMDDTHHMMSSZ>`.
- **The outcome, tested in this order:** (0) the host's own configuration exists but cannot be read or is
  refused: **error**; (1) the host has no configuration for the ledger's repo: **no outcome**; (2) the repo's
  configuration cannot be read or is refused, or names a selection the repo does not define: **error**; (3) the
  check's source is not declared for the repo on this host: **no outcome**; (4) the gate has no `gate added`
  line, or the source is misconfigured (its effective table refused, a path that does not exist, a private
  source for a ledger that is not private, an allowed folder that does not serve the repo or requires a repo
  mapping the source lacks, a kind named against a source whose records carry none): **error**; (5) reading:
  **passed** when at least N records count, whatever else the read met; else **error** when the read met an
  error (a file it may not or cannot read, an unsupported or corrupt file, a limit), else **not yet**. A
  reader that cannot run on a host answers no outcome itself. `count_host_log()` gives passed or not yet; the
  reader applies the rest.
- **Host rules.** A reader reads only under folders the host allows, resolving links, and never a file that is
  not a regular file; it treats a folder's visibility as the host sets it, the most private of every allowed
  folder that covers a file, and only the host may declare a private log's kinds public; an allowed folder may
  name the repos it serves and require that a source name each record's repo; the repo's configuration is the
  file `docs/ledger/log-sources.toml` (its contents the reader's; an absent file reads as empty, so every source
  is undeclared and the host gives no outcome), read from the same tree as the ledger, and each consumer treats
  that file as person-only; a read that runs past the reader's file, byte or time limit stops there, and is
  error unless N already counted; and a reason for an error stays on the host, never on the board.

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

**Superseded and dropped** (v2.4). `pickable()` and `check()` read an archived blocker's Status by its first
word. That is its first run up to whitespace, `,` or `;`, less any run of `*`, `_` and backtick at either end
and then any run of `.` and `:` at its end, compared without case. A Status with no first run (absent, or only
whitespace, `,` and `;`) reads as one with no Status. A first run that strips to nothing is a word this reader
does not know. Known here means a first word in the reader's Status words, a looser test than the head *The
Log* lifts notes from, so a bold-led `**Live check held**` is a known word here though *The Log* leaves it
alone. `Superseded … by <id>` and `Dropped` apply the rules below, and so does a word this reader does not
know. Every other Status reads as closed and done, which releases the dependents, as before. That covers the
reader's other Status words, dated or not: `Resolved`, and on an archived entry also `Open` and *Retired
words*' list (`Designed`, `Built`, `Partly`, `Live`, `In`, `Done`, `Moved`, `OBE`), which v2.7's `migrate`
maps or stops on. It also covers a Status with no word. A duplicate is `Superseded D by` the original; there
is no separate word.
- **A blocker that was superseded** has moved its requirement to its successor. The reader follows the chain
  (A superseded by B, B by C) to its end. The dependent stays blocked while the end is open, or while the
  chain ends in Dropped, in no entry, in a loop, in a `Superseded` with no successor, or in a Status word this
  reader does not know. It is released only when the end is Resolved. Either way `check()` flags it
  (`blocker-superseded`; an error on an entry the edit changed, ℹ on a standing ledger), naming the end it
  should name instead.
- **A blocker that was dropped** keeps the block, and `check()` flags it (`blocker-dropped`, likewise):
  someone decides the dependent, dropping the blocker or blocking it on what replaces it.
- **A blocker whose Status word this reader does not know** keeps the block. Its first word is not one of the
  Status words this release reads: `Open`, `Resolved`, `Superseded`, `Dropped`, and the retired `Designed`,
  `Built`, `Partly`, `Live`, `In`, `Done`, `Moved` and `OBE`. It may be a later minor's word for an entry that
  is closed but not done, so the reader never reads it as lifted. An archived Status that opens with prose
  ("Steps 1 and 2 shipped") reads the same way. `check()` flags it (`blocker-unknown-status`, likewise;
  `cross-unknown-status`, ℹ, through the resolver), naming the word, and someone decides the dependent. A
  Superseded chain that ends in such an entry keeps the block too (`blocker-superseded`), and `archive_plan()`
  refuses it as a successor.
- **Another repo's blocker** reads the same way through the resolver, whose answer for an archived entry may
  carry its `status` and its `successor` (bare when in that repo). Another repo's archive cannot rewrite this
  repo's text, so `check()` reports such a dependent as ℹ (`cross-superseded`, `cross-dropped`,
  `cross-unknown-status`): the host's gate sweep rewires a superseded one by a tool PR, and puts a dropped one
  on the board as `decide`. A resolver that gives no `status` reads every archived entry as closed and done,
  as before.
- **Archiving rewires.** `archive_plan(ledger, archive, tid, *, superseded_by=None, dropped=False,
  resolve=None)` says what archiving open entry `tid` leaves its dependents (`dependents(ledger, tid)`:
  the open entries whose `Blocked by` names it), or refuses:
  - superseded (`superseded_by` a `TD-m` or `<repo>#TD-m`): the successor is followed through each Superseded
    entry to the end of its chain, which the plan's `successor` names and the archive writes. The successor
    exists (in the ledger, the archive or through the resolver) and is open or Resolved: the plan is refused
    when it names no entry, cannot be resolved, ends in Dropped or in a Status word this reader does not know,
    loops (back to `tid` among others), or is one of `tid`'s dependents, which would block on itself. Every
    dependent in `rewire` gets `rename_ref` from `tid` to the successor in the same change, so every dependent
    always names a live or Resolved entry, and a chain's later supersede rewires them again. A dependent that
    already names the successor keeps one copy. Their cards change with them, so a rewired dependent may need
    a rank `join`.
  - dropped: refused while any open entry is `Blocked by` `tid`, naming every one, so each is decided
    first.

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
- **The caller does the I/O.** `ls(path)` returns the names directly in the directory `path`: its
  files' names, and from v3.0 each subdirectory's name followed by `/`, which `load()` and `entry_path()` ignore
  (a v2.x caller's `ls` that lists files alone still reads a ledger); or None when `path` is not a directory; `read(path)` returns a file's
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
  then the `## Summary` section's lines other than the table, as written (v2.4: blank lines kept, so a
  commented-out template there stays whole, a `|` line inside an HTML comment being no table row; of two
  blank lines around the table one kept, none leading or trailing), and a `---` that would follow the prose's own closing `---` with nothing between them, the
  pair that framed the table, is dropped. The archive's text before its first entry is dropped.
  `split()` refuses another `## ` section, an id twice, and a result that does not read back the same
  entries (compared by id), the same `Fields:` and version 2, or that `v2_problems()` flags.
  `split_notes(readme)` (v2.4) lists the lines of that `README.md` which may still describe the v1
  layout, as `(line number, line, why)`, for the caller to warn about and nothing rewritten: a line
  naming the summary table (`summary table`, `table below`, `the table`), and one holding a relative
  Markdown link or reference definition, which the move into the v2 directory breaks (a link to the v1
  archive file among them), and one naming a v1 file, `technical_debt.md` or `technical_debt_archive.md`,
  outside a link (in prose or a code span). It is best effort, for a warning: a line inside a fenced code block, a
  link inside a code span and an escaped one are skipped.

## The next id (v2.4)

A ledger's ids are handed out by **a counter**: the branch `cadence/ledger-ids` on the repo's origin, never
merged and never checked out. Its tip's tree holds one file, `LAST`, the last id given as a number. **A take**
is one commit whose parent is the tip it read, pushed as a fast-forward, so the server takes it only if nobody
moved the tip. Its subject is the id, or the range it gives, then `[skip ci]`: `TD-125 [skip ci]`,
`TD-126..TD-127 [skip ci]`. Its body is `name: value` lines: `by` (who took it: a name, or a hash of a session's
id — the counter is public with its repo, so never the id or an address itself), `branch` (the branch the ids
are for, left out when there is none), `host` (optional), and `take`, a 32-hex nonce, so no two takes are one
commit. An entry carries its take's nonce as `**Id take:**`. Probing, fetching, pushing and retrying a refused
push are the consumer's; what the text means is the module's:
- `ids_held(files)` is every id the files of a ledger and its archive hold, in either layout (`files` maps a path
  to its text): headings and table rows outside HTML comments, and each entry file's name. It refuses a file
  that declares a newer major than the module reads, since its ids cannot be judged.
- `next_id(last, ids, floor)` is `(n, warnings)`: one above the highest of `LAST` (absent or not a number is
  ignored, with a warning, as is one of more than 18 digits), the ids (the default branch's, and any the caller adds, such as open PRs' on a first
  take) and the floor (a front end's own last-given id).
- `parse_take(subject, body)` reads one counter commit: `{ids, by, branch, host, take}`, the fields it has, or
  None for a commit that is not a take (another subject, a range that runs backwards, or one wider than 100 ids —
  the writers take at most 10; an id of more than nine digits is not read). A field's name is read as written,
  lower-case, the first of a name wins, and a `take` that is not 32 lower-case hex digits is left out.
- `judge_takes(new_ids, takes, entries, branch, default)` is the merge gate's judgement
  of the ids a change adds, as `(fails, warns)` of `(kind, text)`. `takes` are every take the counter holds,
  each `parse_take()`'s record with its commit's `sha` and `date`, all kept, so an id given twice is judged
  against both. With no takes, nothing is judged.
  - `id-untaken` (fail): an id no take gave, at or above the counter's first; `id-before-counter` (warn): one
    below it, which is older than the counter.
  - An id's `Id take` is judged alone wherever it is present. The nonce of any take that gave the id passes: a
    range's for each of its ids, either take of an id given twice. `id-take` (fail): the nonce of another id's
    take, naming both ids, or of no take.
  - No `Id take` is `id-no-take` (fail). An entry's nonce is compared exactly.
  - An id whose entry is in none of `entries` is judged only as `id-untaken` or `id-before-counter`.
  - `id-branch` (warn): the take names a branch that is neither `default` nor `branch`. `id-by-unhashed` (warn):
    its `by` is a bare session id or an email address.
  - A text names a take by its `by`, date and short sha, never its nonce.

## Ledger entries and their edits (v2.2)

A v2 entry file is one entry, and the writers render it in one **canonical form**, so a tool can
tell an entry it would have written from one it would not. A reader reads either.

**The entry.**
- **The heading** is `## TD-n: title`.
- **The header block** is the lines after the heading's blank lines, up to the next blank line, as
  above. A writer needs every line there to be one `**Name:** value` field and each name to appear
  once, so an entry with a body has at least one field: its first paragraph is its header block.
- **The body** is everything after the header block. It is cut into **sections**. A section's **lead** is a bold
  run `**Name:**` (a name of one or more characters other than `*`, not starting with whitespace, its trailing
  whitespace trimmed, then the colon), opening a line at its first column that starts a paragraph; a
  paragraph opens the body or follows a blank line. The section runs through every following paragraph up to
  the next lead, so a Fix keeps its bullets. A paragraph inside a code fence opens no section: a fence opens on a
  line of three or more backticks or tildes (indented at most three spaces), and closes on a bare line of the
  same character at least as long. (v3.3: a paragraph opening with a bold run with no colon, `**Done when**`,
  or with the colon after it, `**Done when**:`, is still read as a lead until v4.0, and `check()` flags it,
  `lead-form`.)
  - A lead's name is its bold text less the colon, matched by `field_key`: `Done when:` and `done when:` are one
    name.
  - A qualified lead (`**Fix (to design):**`, a dated `**Note (…):**`) is its own section, matched
    only by its whole text.
  - A body lead named like a field (`**Location:**` in the body) is a body section, never a field.
  - Text before the first lead is an unnamed section, kept as written.
- **Data fields** (v3.3). A section the tools read a value from is a **data field**: its lead's line alone,
  `**Name:** value`, the value the line after the lead's bold run, whitespace trimmed. The format's are
  `Ask`; where *An entry's own answers* is in this SPEC, `Answers` and `Lifts` too, as that section reads them
  (on a gated entry, flagged there, never `field-lines`). Anything after the lead's line in a data field's section (a line glued below it,
  or a later paragraph before the next lead), or an empty value, is a fault, `field-lines`. `Context` is a
  reserved prose name, read as the Ask's context (*Text a person reads*). An Event section (*Events*) keeps its own two-line grammar. Every other section is prose, read only
  as text.

**Canonical form** (`canonical(text)`): line endings normalised to `\n` first, then
- the heading (its title stripped);
- one blank line;
- the header block in this order: `Priority, Type, Added, Owner, Kind, Status, Id take, Blocked by,
  Part of`, each spelled so. Then any other field, spelled as the file spells it, in the file's order — a
  `Waits` or a header `Location` among them (v2.7). A place in the order is a rendering rule, not a declaration:
  `Owner` and `Kind` are not the format's own fields; a retired field (*Retired words*) is kept where the other
  fields put it;
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

**A new entry** (`entry_text(id, title, fields, sections, *, filed=None, declared_fields=())`) is that form. Its fields are one line
each, and an empty value is left out. Each section is written `**<name>:** <text>`; a first section
with no name is the unnamed one, written as given. It is refused for an id that is not `TD-n`, a
title that is empty or more than one line, a field that would not read back as one line or is named
twice, and sections that would not read back as given (a section's paragraph that opens in bold
would start a section of its own). From v2.8 it also refuses a field named `Title` or `Log`, and a section named
`Title` or a header name (*edit*, below), the ledger's `Fields:` names given as `declared_fields`. A `Blocked by` is written as the writers write it (*The ledger*):
its ids, then its gates in their order. With `filed` (v2.4: `today`, `who`, `session`, `words`, and
optionally `while`), it writes the entry's Log: the `filed by` line, then one `gate added: <gate>` line
for each gate its `Blocked by` is filed with, in their order, so a gate ages from the day it was filed. A filed entry's `Added` is the date
alone and its Status, if given, is `Open`, since their words go in the Log; either otherwise is
refused, as is a section named Log.

**The Log (v2.4)** is an entry's dated history, a body section led `**Log:**` whose lines follow
the lead, one per line, each `- YYYY-MM-DD: words`, oldest first. It is always the body's **last**
section. `check()` flags a section after it, or a second Log (`log-not-last`), and a line that is not
`- YYYY-MM-DD: words` or that opens with a writer's prefix but not in its shape (`log-line`). Both
are errors on an entry this edit changed (its whole text, not only its header) and information on a
standing one. `check()` notes (ℹ, `misplaced-name`, v2.8) each misplaced section (*edit*, below) and each **misplaced
field**: a header field named `Title` or `Log`. It is never an error: `edit`'s `remove` and `set`'s empty value clean
them. An entry `canonical()` refuses is not read for it. `check()` reads the Logs of the open entries, not the archive's. A writer that appends to the Log refuses one that is not last, and `edit` and
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
  - `gate lift skipped: <id> no longer carries <gate>`, the gate a `decision (<person>)` or an `event (<name>)`.
  - `kept waiting: <gate> — by <who>; answer "<label>"`.
  - (v3.4) The `gate-lifted` answer shape and the `kept-waiting` shape read `by <name>[ for <name> (<name>)]`: with
    ` for`, the first name is the delegate, the second the person, the third the scope (`gate lifted: decision
    (pat) — by director for pat (merge-line); answer "Merge"`). `log_line()` returns `by` as the person, with
    `delegate` and `scope` on every record of those two shapes (`null` on an undelegated line) and on no other
    record.
  - `gate reassigned: decision (<a>) → decision (<b>) — by <who>; <why>`.
  - `archived: <Status word> — <why>`, `reopened — <why>`, and `was: <Status>`.
  - `retitled: was "<title>"` (v2.8), the title the heading held before `set` changed it.
  - Any other words are a note, kept byte for byte, an unknown tool's line among them.
- **The writer prefixes are reserved:** `filed by `, `gate added:`, `gate lifted:`, `gate
  reassigned:`, `kept waiting:`, `gate lift skipped:`, `was:`, `archived:`, `reopened —`, `retitled:` (v2.8). `note`
  refuses words that begin with one ("reopened the thread" is still a note), and a lifted Status note
  that would is written `note: <text>`.
- **A gate's age** (`gate_age(text, gate)`) is the date of the latest `gate added`, `kept waiting` or
  `gate reassigned` (to it) line for that gate, a person's name compared in any case. With none, it
  is the first Log line's date, then the `Added` date.
- **When a gate was added** (`gate_added(text, gate)`, v2.5) is the date of the last `gate added` line for
  that gate in the Log's order (never by date), compared as for its age, or none: none too when a `gate
  lifted` line for the gate follows that line in the Log, or when the Log cannot be read. Unlike its age, it
  never falls back.
- **Status notes become Log lines** through `status_notes_to_log(text)`, which `note`, `archive` and
  `reopen` run before they write:
  - It reads the Status as `<Word>[.] [YYYY-MM-DD] [by <id>] [[:] <tail>] [ — was: <Status>]…`,
    where `<Word>` is a known one: `Open`, `Resolved`, `Superseded`, `Dropped`, or one v2.7's
    `migrate` maps (`Designed`, `Built`, `Partly`, `Live`, `In`, `Done`, `Moved`, `OBE`), in any case,
    not in bold, and followed by its end, a `.`, a `:`, its date or `by`. A date or `by <id>` in the
    head is followed by the end, whitespace or a `:`. So `In progress`, `Open, held`, `**Open** x`,
    `Resolved 2026-10-03.` and `Open 2026-01-01T10:00` are prose, and nothing is lifted from them.
  - The tail becomes **one** Log line, verbatim (a date inside it stays prose), dated by the Status's
    date, else the `**Resolved:**` line's, else `Added`'s. Each `— was:` segment becomes its own `was:
    <Status>` line, dated by its own date or the same fallbacks.
  - The lines go in among the Log's by date, after any line of an equal date, and the Status is left
    as `<Word>[.] [YYYY-MM-DD] [by <id>]`.
  - An unknown word (a bold or prose Status), a Status with nothing after its head, or text with no
    date to give it: nothing is lifted. `note` leaves such a Status as it is; `archive` and `reopen`,
    which replace it, first copy it whole into one `was: <value>` line, dated by the fallbacks, else
    today.

**The body's shape** (v3.3). `check()` flags four kinds on each open entry's raw body, cut at `## ` headings
outside HTML comments: `lead-form`, a paragraph that opens with a bold run that is not a lead (no colon, the
colon after the bold, no name, or a name opening with whitespace; read as a lead until v4.0), its message naming
the strict spelling and rewording; `glued-lead`, a line at its first column, outside a fence and the header
block, that opens with `**Name:**` but starts no paragraph (a comment-only line above it is text), and an `Ask`
lead after up to three spaces or after a `>` prefix (up to three spaces before each `>`, any spaces or tabs after
it, nested or not; a tab-indented Ask is not flagged); `fence-open`, a fence the body never closes (fence lines inside a
comment count, as the writers read them); and `field-lines`, an `Ask` with text past its line (comment-only and
in-comment lines aside) or with no value once comments are dropped. A lead on a line inside a comment is never
flagged. A bold run anywhere else is prose. Faults are counted per key (entry, kind, and the lead's `field_key`;
entry and kind for `fence-open`), each flag's text carrying its ordinal (*the 1st*) and no line: with no `old`
all are ℹ; with `old`, the count `old` has of a key is ℹ and the rest errors, an entry absent from `old` counting
from 0, one `old` cannot read all ℹ, and where `old` has `fence-open`, its other three kinds ℹ. The
archive is not read. The ledger writer refuses an edit that makes one new; `migrate-body` cures or refuses each.

**The archived entry.** An entry archived as done has the Status `Resolved YYYY-MM-DD` (its why in
the Log's `archived:` line, v2.4; `Resolved YYYY-MM-DD: why` before), and
its Fix replaced by one line, `**Resolved:** YYYY-MM-DD (PR #n) — <pointer>`, which is its body's
only `**Resolved:**` section. The pointer names the doc, test or code that now carries what lasts,
and is optional, as is the PR (with no PR, the parenthesis is left out). An entry archived with
nothing lasting to move keeps its Fix and has the line after it. An entry overtaken by another has
the Status `Superseded YYYY-MM-DD by TD-n` (`… by TD-n: why` before v2.4), and its Why and Fix stay as written. A `Resolved`
header field, the older form of the line, is a retired error (v3.0).

**The closed Status set** (v2.7). An entry's Status is `Open` in the ledger, and in the archive `Resolved
YYYY-MM-DD`, `Superseded YYYY-MM-DD by <id>` (`TD-n` or `<repo>#TD-n`) or `Dropped YYYY-MM-DD`, exactly as the
writers write them: nothing before or after, one space between parts, a real date. Any other value, or none, is
an error on every entry, open or archived, of a ledger that declares major 2 (`status`, `status_problem()`), never
standing, with or without `old`; on a v1 ledger it is ℹ. Its text names the form the entry's place takes and
the value's first word when it has one, with what replaces a retired or misplaced word, never the whole value, and
ends *v3.0 reads no other form: on an open entry write `Open` with `set`, on an archived one by hand, then
`ledger.py fmt TD-n`*. It replaces v2.4's ℹ `retired` on an
open entry's Status word. What a reader reads of an archived blocker's Status (*Superseded and dropped*) is
unchanged, so another repo that has not migrated still reads as before. `status_problem(text, *, archived)` gives the problem of
one entry's Status against the four forms (*The closed Status set*), or None: `Open` in the ledger; `Resolved YYYY-MM-DD`, `Superseded
YYYY-MM-DD by <id>` (`TD-n` or `<repo>#TD-n`) or `Dropped YYYY-MM-DD` in the archive, exactly as the writers write
them — nothing before or after, one space between parts, a real date.

**Edits** (`edit_entry(text, action, *, today, …)`, one of `ENTRY_ACTIONS`) take one entry's text
and return it in canonical form. Each is refused for an entry `canonical()` refuses (a v1 ledger:
*split first*). It is also refused unless the result reads back exactly the change meant, and
nothing else: the same id, title, fields and sections but for the change. An edit that rewrites
the body joins its sections with one blank line, and is refused when an HTML comment there spans
paragraphs. The date is the caller's (`today`, a date, `YYYY-MM-DD` or an aware datetime, written as its UTC date; a time is never written, and a naive datetime is refused), and
an argument the action does not take is refused (`today` is taken by `note`, `archive` and `reopen`, which
require it, and from v2.5 by `set` and `edit`, which require it only to date a gate or (v2.8) a retitle). What a field's value means (a
vocabulary, a `Blocked by` item, a cycle) is `check()`'s, which the caller runs on the result.
- **set** (`fields`): sets each field, in its place, or adds it where the order puts it; an empty value removes
  it. A value is one line. A `Blocked by` (v2.4) is written with its ids, then its gates in their order. A value
  holding an item the grammar does not read is written as given, for `check()`.
  From v2.5, `set` takes an optional `today`, and a `Blocked by` that adds a gate the entry did not carry
  needs it: it also appends `gate added: <gate>` to the Log for each, in the order the gates are written,
  dated `today`, making the Log at the end of the body if there is none (a Log that is not last is
  refused, as for `note`; the Status's notes are not lifted). A gate it keeps is not logged again, and a gate the value names twice is
  logged once, as first written. **The
  gates the entry carried** are its `gate_items()`, compared by `_gate_key` (a person's name in any case), so
  `Decision (kim)` rewritten `decision (Kim)` is kept.
  From v2.8 `set` takes `title`, which replaces the heading's title, and `fields` may then be empty. The new title
  is stripped and refused when empty, more than one line, or holding `\r` or `<!--`. One equal to the entry's title
  as read changes nothing. Any other is written `## TD-n: <title>` and logs `retitled:
  was "<old title>"`, dated `today`, which it then requires, ahead of any `gate added` line; the Log is made and
  refused as above. The file keeps its name. `set` refuses a non-empty value for a field named `Title` or `Log`.
  From v3.1 it refuses a non-empty `Ask` field it adds or changes when the `Blocked by` it leaves names no decision
  (*The ledger*, `decision-missing`): an Ask is what a decision waits on, so the gate comes first.
- **note** (`words`): lifts the Status's notes (above), then appends `- YYYY-MM-DD: words` to the
  Log, making it at the end of the body if there is none. It is refused if the words begin with a
  writer's prefix or are more than one line. (Before v2.4 it appended ` YYYY-MM-DD: words` to Status.)
- **edit** (`section`, `words`; v2.8 `remove`, `declared_fields`): replaces the named section's paragraphs, keeping its lead as
  written. A section the body lacks is added after the first Why, else before the first Done when,
  Related or Log, else at the end. It is refused when two sections have the name, and for the Log,
  which only its writers write. From v2.8 it refuses to add a section named `Title` (the heading's: `set` retitles),
  a **header name** (`Priority`, `Type`, `Added`, `Status`, `Blocked by`, `Part of`, `Escaped from`, `Id take`, and
  each name the ledger's `Fields:` line declares, given as `declared_fields`). A section the body has is
  replaced whatever its name. From v3.1 it refuses to write an `Ask` section, replacing it or adding it, on an
  entry whose `Blocked by` names no decision (as `decision-missing` counts one): the writer's `set --ask` writes
  the gate and the Ask together (*The ledger writer*), and an entry that already has an Ask may take its gate
  first. An answered entry's Ask (*The ledger*) is therefore never rewritten while ungated. With `remove` (v2.8)
  it removes a **misplaced section**, one named `Title` or a header name, and (v3.1) the `Ask` section of an entry
  whose `Blocked by` names no decision (as `decision-missing` counts one, *The ledger*); it is refused for any
  other section, for an `Ask` that is not misplaced while a decision holds, for a header name the entry's header
  lacks (`set` it first), and with words. Names compare as leads do, so a qualified lead is never one. From v2.5, `edit` takes an optional `today`. Replacing or adding an
  `**Event (<name>):**` section for a gate the entry carries, when its check becomes `host-log` or its
  `host-log` source, kind, count or text changes (read by `parse_check()`, so spacing alone is no change),
  appends `gate added: event (<name>)` to the Log, dated `today`, which that case requires: a changed question
  is a new wait. The Log is made and refused as for `set`.
- **archive** (`why`, and `pr`, `pointer`, `as_is`, or else `superseded_by`, or else `dropped`) lifts the Status's
  notes, then writes the archived entry, above, with the Status `Resolved YYYY-MM-DD` and the Log
  line `archived: Resolved — <why>` (or `Superseded YYYY-MM-DD by TD-n` or, v2.4, `by <repo>#TD-n`, and
  `archived: Superseded — <why>`; or, v2.4, `Dropped YYYY-MM-DD` and `archived: Dropped — <why>`, with no
  `**Resolved:**` line, since nothing replaces it). A superseded or dropped entry keeps its Why and Fix.
  The caller asks `archive_plan()` first, and rewires the dependents it names in the same change. `pr` is the forge's number or None; with None, a pointer holding `#<digits>` is refused,
  since a reader would take that for the PR.
  - An earlier `**Resolved:**` section is replaced, never doubled, and an entry holding a `Resolved` header field
    is refused (*move it with `edit --section Resolved`, then remove it with `set`*).
  - With no section named exactly Fix, the line goes at the end of the body, before the Log, and a
    qualified Fix lead is left alone.
  - A missing Status is added.
  - It is refused if two sections are named Fix.
- **reopen** (`why`): lifts the Status's notes, then sets Status to `Open` and logs `reopened —
  <why>`. The `**Resolved:**` section stays as history, and the caller writes a new Fix with `edit`.
  (Before v2.4 the Status became `Open YYYY-MM-DD:
  why — was: <old Status>`.)
- **renumber** (`new`) rewrites the heading's id to another number; Log lines are history, and keep
  theirs. **rename_ref** (`old`, `new`) rewrites that id in `Blocked by`, `Part of` and a `filed by`
  line's `while`, never other Log prose. A local id matches by number; another repo's id matches as
  `<repo>#TD-n`. A `Blocked by` that then names an id twice keeps its first copy (v2.4).

**Lifting a gate** (v2.4) is one text edit, `lift_gate(text, gate, by, *, answer, evidence, suffix, override,
today, people, answered_by)`, which every route writes: a person's answer through the `set` route, a host's
event and `until` lifts, the cross-repo decision lift, and the decide lift (*The board*), which composes it.
It removes the gate from the open entry's `Blocked by` (an emptied field is removed; the other items keep their
order, canonical when all are readable) and appends the matching `gate lifted` line, dated `today` (the UTC
date), with the gate as the entry writes it (its person's spelling) and `by` as given. Its inputs match one
shape exactly, and anything else is refused:
- **a decision:** `answer`, and at most one `suffix`: `board <repo>` (the item is on another repo's board),
  `no board item` or `shared board item left open`. `by` is the gate's person, compared case-insensitively,
  unless the caller passes the board's `People:` as `people` and `Answered by: any`, when it is anyone listed.
  Or `override`, its why required, when `by` may be any person: `gate lifted: decision (<p>) — by <who>;
  override: <why>`.
- **an event lifted by a person** (from a sweep's item): `answer`, with `by` on `people`, which is then
  required. No suffix.
- **an event lifted by a host:** `evidence`, `<repo>#<n>` for a `pr-merged` check (its own repo and PR),
  `<repo>@<sha>` for `file-contains` and `ref-includes` (its own repo, and the commit the file or ref was read
  at), or, for `host-log` (v2.5), its own source then `/` and the record's id (holding no empty, `.` or `..`
  segment), or `@` and the record's UTC time as `YYYYMMDDTHHMMSSZ`, a token of `[A-Za-z0-9_.@/-]+`; the check type is
  read from the entry's `**Event (<name>):**` section, never passed in. `by` is the host's token.
- **`until D`:** none of them; `today` must have reached D.

`lift_gate()` and `decide_lift()` (v3.4) also take `delegate` and `scope`, which only change the Log line they
write to the delegated form (*The ledger*'s Log shapes): `gate lifted: <gate> — by <delegate> for <by> (<scope>);
answer "<label>"`; every comparison they make is of `by`, the person. `lift_gate()` refuses a delegate on the
override, check and date shapes and with the `board <repo>` suffix, a delegate outside the person grammar or equal
to `by`, and a delegate without a scope or a scope without a delegate; `decide_lift()` refuses the same on the
`kept waiting` line it writes.

A waiting-only answer (*The board*) is refused, as is a gate the entry does not carry and an archived entry.
**The reassign** (`reassign_gate(text, frm, to, *, by,
why, today)`) replaces `decision (<frm>)` by `decision (<to>)` and logs `gate reassigned: decision (<frm>) →
decision (<to>) — by <by>; <why>`, which resets the gate's age. It is refused for the same person in another
case, an entry that does not carry `frm`'s decision or already carries `to`'s, and an empty why. Who may run a
lift, a reassign or an override (a session a person started), and whether `to` has a board, are the
consumer's to check.

Moving a file into `archive/` or back, and the relative links that move with it, are the ledger writer's (*The ledger writer*).

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

A board is a set of items for a person. **A v3 board is a directory** (by convention `docs/user_attention/`), one
file per item, named by its id (*The board as a directory*, v3.0). A v2 board is one Markdown file (by convention
`docs/user_attention.md`) with its archive beside it (`docs/user_attention_archive.md`); v3.x reads one and writes
none. What an item means is the same in both, and the paragraphs below say it once. Where they place a field on a
line (*right after the Context*, *ahead of the `Due:`*, *starting a sentence*), the place is a v2 line's; in an item
file each field is a header line, in the order *The item file* gives.

**From v3.0, everything this section says about a line** (its text, where a field stands on it, its key, its
replies' tails, its tick, and the functions that write or judge a line: `item_line()`, `decided_line()`,
`edit_line()`, `item_problem()`, `canonical_item()`, `parse_closed_items()`) **is v2's, read only**: v3.x reads a
v2 line so, and writes none. A paragraph that says it once for both majors names the item file's form beside the
line's.

**An item** on a v2 board is one line: `- [ ] [kind] YYYY-MM-DD (session <name> on <host>, or n/a) — text.
Context: … Due: YYYY-MM-DD.` A closed item is ticked: `- [x] … Closed: YYYY-MM-DD — why.` Items are never
deleted. On a v2 board, when an open item and a closed one have the same id (*Reading a board*), on the board or
in its archive, the item is closed: a merge kept both sides. A v3 board has no such rule: closing an item moves
its one file.

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

**Notes on a hide** (`item_notes(item, today)`, v2.4, of an open `BoardItem` of either major (`parse_item()` or `parse_board()`)) inform and
never refuse: no gate reads them. Each opens with its rule's tag, and D and E stand for the ISO dates of the fields.
- `hide-spent` is a `Hide until:` on an open item that is not hidden today. Either its date has come
  (`hide-spent: Hide until: D has come, so it hides nothing; a snooze replaces it`), or the item is decided
  (`hide-spent: a decided item is never hidden, so Hide until: D hides nothing`).
- `hide-late` is a hidden item whose `Hide until: D` is later than its `Due: E` (`hide-late: Hide until: D is after
  Due: E, so the item stays hidden past its deadline`). An `fyi`, or an item whose `Due:` cannot be read, has no
  deadline, so it never gets a `hide-late`.

An item carries at most one of them. `item_record()` carries them as `notes`.

**What needs the person** (`needs_you(board, today)`, v2.3; from v3.0 `board` is a `Board`, *Reading a board*) is
every open item not hidden, each with one class and a signed `days`, in one order: `decided` (`days` the
decision's age; oldest decision first); then the person's to-do — `overdue` (days past due; most first), `due` (0
on the due date, negative days until it; soonest first), `bad_due` (a `Due` the reader cannot read, an item
file's empty `Due` among them, v3.0) and `undated` (the board's order); then each
`watch` item, ordered the same way and keeping its own class and signed days; then each `fyi`, never due, in the
board's order. **The board's order** breaks every tie: a board read from one file (`form` `"file"`) in line order,
and one read from a directory (`"dir"`) in ids descending, newest first (by `Added` date; within one day the order
is random). So tied items can change order when a board
is split; which items need the person, and their classes and days, do not. Which of these a consumer shows, and
when it escalates, is the consumer's.

**`Context:`** — what the item refers to, read as refs in order: `TD-NNN` or `<repo>#TD-NNN`,
`PR #N` (`PRs #12/#13` and `PR #12, #13` give both), and best-effort `branch <name>`. A Context ends where the
next field begins: ` Parts:`, ` Doer:`, ` Due:`, ` Hide until:`, ` Answers:`, ` Lifts:`, ` Decided:` or ` Closed:`.
From v3.0 a v2 line's Context is read with its reply tails taken out, as the gate reads it (`_item_gate()`), so it
ends at a reply too, and a ref named only in a reply's words is no ref of the item: a line whose Context ran into
its replies (no ` Due:` before them, as on an `fyi`) reads fewer refs in `item_record()`'s `refs` than in v2.x. In
an item file the Context is its header value, which holds no reply. A `decide`
that lifts a gate names exactly one entry there: every `decide` whose Context names a gate, `decision (<person>)`
or `event (<name>)` (a person's name, an event's name a letter or digit then letters, digits, `_`, `.` and `-`),
since no `Lifts:` means `Go` lifts, and every `decide` that carries `Parts:` or `Lifts:`. The writer refuses,
and the gate faults, any other.

**`Parts:`** (v2.3) — `Parts: TD-15, TD-16.`, right after the Context, ahead of the `Due:`, and only on a
`decide`: the parts of the parent its Context names that its question asks about, a snapshot taken when it was
written (`parse_parts()`, `BoardItem.parts`, `item_record()`'s `parts`): every `TD-NNN` or `<repo>#TD-NNN` in it,
each once, and never one inside a reply's words. The writers write the ids in number order, separated by `, `. Its ids are not Context refs, and it is
part of the item key, since a changed snapshot is a different question (v2). What an answer does to the parts it
lists is *The decide lift*'s (v2.4). `item_file(parts=)` (v3.0; `item_line(parts=)` before it) and `board.py add --parts` write it, and `parts_problems()` checks it against the
ledger (v2.6, *Edits*).

**`Doer:`** (v2.8) — `Doer: <repo>.` or `Doer: team <team>.`, right after the Context (after a `Parts:`, where
one stands there), ahead of the `Due:`, and only on an `act`: who should do the item's step, a repo (*The ledger*'s
`<repo>`) or a team (a person's name, below, after the word `team`), each name kept as written (the
module compares no doers; a consumer that resolves one compares case-insensitively). A repo named `team` is
`Doer: team.`, and a doer's repo never ends in `.` (`parse_doer()`, `BoardItem.doer`, `item_record()`'s
`doer`: `{"kind": "repo" | "team", "name", "text"}`, `text` the value as it stands on the line without its ends'
whitespace and its final period, or None for none or a value that does not read). It is read only in that place,
on any kind, and never inside a reply's words; `item_problem()` faults it on any kind but `act`, no kind included
(v2; in an item file `item_file_problem()` does, v3.0). The reader reads it as it reads `Parts:`, any spacing and
an absent period included, which `item_problem()` faults (v2). On a v2 line it is part of the item key, and no edit changes it: a step for another doer is another item.
What resolving it means, and what a press on it does, are the consumer's. `item_file(doer=)` (v3.0;
`item_line(doer=)` before it) and `board.py add --doer` write it. In an item file (v3.0) it is the header field `Doer` (*The item file*), a bare
value read by `doer_value()`; `parse_doer()` reads a v2 line's.

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
  An offered answer whose label is a **form** (v2.8) takes the person's words: the label, whitespace collapsed, is
  a **head** (one or more characters, none of them `:`, `<` or `>`, not starting with whitespace), then any
  spaces, `:`, and nothing or one `<…>` placeholder (`is_form()`): `Hold: <note>`, `Other:` and the look's
  `Not right: <what>` are forms; `Not right: wrong repo` and `Hold: <a> <b>` are complete answers like any other.
  Heads compare in any case, whitespace collapsed (`form_head()`). An answer given to the item **fills** a form
  when it is none of the item's complete answers and its text before its first `:` is that form's head; the fill
  is the head as offered, `: `, and the words after the colon (`fill_form()`; the look's case
  `fill_not_right()`, and `is_not_right_form()` for its form). Words that are empty or only a placeholder are
  refused (*<head> needs its words*). Where two forms share a head, the first fills. A `decide` offers no two forms
  with one head and marks no form ` (default)` (*Edits*).
- `Lifts: a | b.` (v2.3) — which of a `decide`'s answers lift the gate its Context names, each one of its
  answers' labels (compared case-insensitively), `\|` for a literal bar (`parse_lifts()`, `BoardItem.lifts`,
  `item_record()`'s `lifts`). It is read only after the item's `Answers:` and ahead of its `Decided:`, starting a
  sentence, so a reply's or a `Decided:` text's words are never it, and the answers end where it begins. It is written only when it is not `Go` alone: no `Lifts:` means `Go`. On a v2 line
  it is part of the item key. An answer **lifts** when it is one of `Lifts:` (or `Go` when the item has none), compared
  case-insensitively (v2.4), or when it fills a form listed there (v2.8; *The `Answers:` bullet*), so a `Decided:`
  holding a fill of a listed form lifts and closes as its form would. The two **waiting-only** answers, `Keep waiting` and `Not yet` (any case; a final
  period dropped; `waiting_only(label)`), never lift: `item_file(lifts=)` refuses one and `item_file_problem()` faults
  one (v3.0; `item_line()` and `item_problem()` before it). `item_file_problem()` (v3.0; `item_problem()` before
  it) also faults, on an open `decide` with no `Decided:`, two forms with one head and a form
  marked ` (default)` (v2.8; *The `Answers:` bullet*).
- `Decided: <label> (by <person>) (YYYY-MM-DD).` — the person's answer, and (v2.3) who gave it. A decided item
  stays open and due; it now waits on whoever acts on it, not on the person. Only a final `(by <person>)` before
  the date, `<person>` a person's name (below), is split off (`parse_decided_by()`, `BoardItem.decided_by`,
  `item_record()`'s `decided_by`); the rest, never empty, is the label (`parse_decided()` keeps its shape,
  `(label, date)`). A `Decided:` with no `(by …)` stays valid, as every one written before v2.3 is: it names
  nobody. The item key strips the whole field, so a `(by …)` moves no key. In an item file it is `Decided:
  <date>[ by <person>[ for <person> (<scope>)]] — <label>` (*The item file*; the delegated form v3.4's).

**The bold head** — an item's first `**…**` run, whitespace collapsed, read outside its replies'
words (its fields' are read: a bold answer with no bold before it is the head), is its title where it
has one. A blank run (`** **`) is none. A line with none has no bold head; what stands in for it is the
consumer's. In an item file (v3.0) it is read from the heading, as from a line; a heading with no bold run has none.

**Replies** — ` — <name>, YYYY-MM-DD: <words>` after the `Due:` (and its `Hide until:`) and ahead of the trailing fields,
any number in a row. A reply's words never carry `Context:`, `Hide until:`, `Answers:`, `Decided:` or `Closed:`,
nor a `Due:` on an item that has none. In an item file (v3.0) a reply is a Log line (*The item file*), and none of
this paragraph's limits on its words holds: they hold for a v2 line.

**The detail block** — the lines right under an item indented deeper than its `-`, up to a blank
line, a line no deeper, or another item. No edit touches it. In an item file (v3.0) it is the body (*The item
file*).

**The item key** (v2) — the line with the tick, `Closed:`, `Decided:`, `Due:`, `Hide until:` and the reply tails
taken out, indentation kept (`item_key()`). On a v2 board it is what makes an open and a closed copy of one item,
or a snoozed or replied-to one, equal; v2.3 strips a date-shaped `Hide until: D` wherever it stands, as it strips
`Due:`, so hiding an item never re-keys it. **From v3.0 an item is its id, not its key:** no v3 reader or writer
keys an item. `item_key()` remains to read a v2 board and to give a v2 item its id (`key_id()`, *The board as a
directory*), so what the key is for a given v2 line does not change through v3.x: consumers map the keys they
persisted to ids through it.

**`People:`** (v2.3) — `People: a, b, c`, a preamble line naming the board's people: whose board it is, one
person's or a team's, and so who may answer it. It lists one or more people's names, comma-separated, each
**a person's name**: runs of letters, digits, `_` and `-`, joined by single dots (`pat`, `sam.lee`), compared
case-insensitively. It is read only above the first item of a board read from a file, and anywhere in the
`README.md` of a board read from a directory, and only the first such line
(`board_people(content)`: the names as written, in order, or None for a board with none). A v2.2 reader reads
no preamble line, so it ignores it.

**`Answered by: owner | any`** (v2.4) — a preamble line saying who may give a lifting answer on the board:
`owner` (the default, when the line is absent), only the gate's named person; `any`, anyone on its `People:`.
It is read as `People:` is (`answered_by(content)`: the value as written, or None). A one-person board reads
the same either way.

**`Delegates:`** (v3.4) — `Delegates: <delegate> for <person> (<scope>, …); …`, a preamble line read as
`People:` is, granting a delegate the authority to answer for a person on the board's `People:`, on `decide`
items whose `Scope` the grant names. The value splits at `;`, each grant's whitespace dropped at its ends and
folded to one space inside, its scopes split at `,`; an empty piece is skipped. Each name is a person's name in
grammar, compared case-insensitively. `board_delegates(content)` returns the grants as written,
`(delegate, person, scopes)` each, a piece outside the form as `(piece, None, None)`, `[]` for a line that holds
no grant, or None with no line.
`delegates_problems(board, old=None)` names a grant outside the form, a person not on `People:`, a delegate on
`People:`, a delegate granted for itself (that fault alone for the grant), two grants of one delegate for one
person, a scope named twice in a grant, a line that lists no grant, and a second line. A fault is an error when
the edit introduces it (its line differs from `old`'s, or `old` is None) and ℹ otherwise, so a standing bad
grant never blocks the board's other writes. On a standing board (`board_problems()` with no `old`) an open item
whose delegated answer the current line no longer covers is ℹ. A line with any such fault grants nothing:
`delegation_covers(board, delegate, person, scope)` is true only on a faultless line holding that grant. No
wildcard: a board with no line accepts no delegated answer.
`delegates_changed(base, head)` says whether two boards' grants differ. A delegated answer counts as its
person's for every purpose: it lifts the gate or keeps it waiting, closes the item and covers the gate as the
person's answer would. A delegate may not answer an item whose Context names a gate on another repo's entry.
`delegate_problem(board, item, delegate, person)` gives the first of the five rules a delegated answer fails, as
its fixed message (*Edits*), or None.

**A closed item** is read as an open one is, once its trailing `Closed:` field is cut (`parse_closed_items(content)`,
v2.4, of a board or its archive: each a `BoardItem` with its line and detail block). On a v3 board a closed item
is a file under `archive/` with its `Closed:` (*Reading a board*). Its `raw`, `closed`, `fields`, `words` and
`context` (v3.0) are read from the `- [x]` line as written.

**The decide lift** (v2.4) is what a lifting answer on a `decide` item whose Context names one entry and one gate
does to the ledger: `decide_lift(item, entries, label, by, today, board_people, answered_by, archived=(),
delegate=None, scope=None)` (`delegate` and `scope` v3.4),
`item` an item file's text or a `BoardItem` (v3.0; a v2 line before it),
returns `{id: new text}` for each entry it changes, from the base item, the base texts of the Context entry
and each `Parts:` id that the ledger's directory holds, whatever its Status (`entries`), the ids of those only its
`archive/` holds (*The ledger as a directory*; `archived`, v2.6: each `TD-n` read as `entries`' keys are, by
number, any other member ignored; an id among `entries` is read from its text even when `archived` holds its
number, open before archived as `entry_path()`), and the base board's `People:` (None: none, and the board checks
below are skipped) and `Answered by:`. It covers a `decision (<p>)` and an `event (<name>)` alike:
- a lifting answer lifts the gate through `lift_gate()` on the Context entry, if it carries it, and on each
  listed part that does; each listed part that no longer carries it, an archived one among them (whatever its
  Status reads; its `Part of` is not read), is logged on the Context entry as `gate lift skipped: <id> no longer
  carries <gate>`, in the `Parts:` line's order, an archived part spelled as the first member of its number in
  `archived` spells it;
- a waiting-only answer logs `kept waiting: <gate> — by <by>[ for <person> (<scope>)]; answer "<label>"` (the
  delegated form, v3.4, with `delegate` and `scope`: `by <delegate> for <by> (<scope>)`) on each of those that still
  carries it, which resets the gate's age; for a decision, so does every other answer (a work order such as
  `One more round`); for an event, any other answer (`Rewrite the check`, `Drop the entry`) writes nothing;
- `<p>` is compared case-insensitively, and the Log writes the entry's own spelling.

It refuses an item that is not a `decide` naming one entry and one gate; another repo's entry (its lift is a
tool PR in that repo); a Context entry missing or archived (in `archived`, or its Status an archived one); a
`Parts:` id in neither `entries` nor `archived`, of another repo, or, given as a text, not `Part of` the Context
entry (the snapshot does not match); a gate's person not on `People:`; an answerer not on
`People:`, or, for a decision under `owner`, not the gate's person. An event has no gate person, so anyone on
`People:` may answer it. Its output for an entry is byte for byte `lift_gate()`'s for the same answer.

**Closing on the answer** (v2.4): `closes(item, label, entries_after)` says whether answering closes the item in
the same write. On an item whose Context names a gate, a waiting-only answer closes it, and a lifting one does
when the Context names this repo's entry (a bare `TD-n`) and nothing listed still carries the gate after the write
— neither that entry nor any `Parts:` id (an id `entries_after` lacks carries nothing). Its callers give it the
open entries' texts alone, so an archived part, left out, carries nothing (v2.6). Every other answer is a
work order, and the item stays open until whoever acts on it closes it; a lifting answer on another repo's entry
stays open until that repo's lift merges. A lifting answer that does not close the item is never written on it by
the `set by=` route's board half (*The board writer*, v2.7): the item stays unanswered until the person answers it
for the entries left.

**The gate sweep** (v2.4) is what a host's periodic sweep of one repo's ledger does, decided here and nowhere else;
the host gathers the inputs (the boards it reads, its event checks' outcomes) and writes the outputs. It keeps no
state: the boards, their archives and the ledger's Log are its state, so running it again over its own writes files
and closes nothing. A board is `(origin_url, basename, board)`, `board` a `Board` read whole (*Reading a board*; v3.0, where v2.x took
the board's and its archive's texts), named by its origin's `origin_key`,
else by its basename; **this repo's own board** is the one whose `origin_path` is `repo` (else whose basename is).
On it a bare `TD-n` names this repo's entry; on any board, `<repo>#TD-n` with `repo` (compared case-insensitively).

`covers(entry_text, gate, boards, repo)` returns `[(board, item, state)]`: each `decide` item whose Context names
the entry and the gate, or the entry's parent (its `Part of`) with the gate and the entry among its `Parts:`, with
nothing after the gate (a Context that goes on past it, `TD-4 decision (pat) — design ready`, names no entry here), on a
board whose `People:` lists the gate's person (any board, for an event). Its state is `open`, `decided` (open, with
`Decided:`), `closed` or `closed-decided` (closed: on a v3 board, its file under `archive/`; on a v2 board, closed on
the board or in its archive). Only `open` and `decided` cover.

`sweep(entries, boards, results, today_utc, today_local, reask_days=30, event_age_days=30, repo)` returns `{to_file:
{board: [item]}, to_close: {board: [item id]}, lifts: [{id, gate, kind, evidence}]}`, `to_close` listing ids
(v3.0); an item
read from a v2 line with no readable date has no id and is never in `to_close`: the sweep leaves it for a person, as
a line it cannot name by id. `entries` are the ledger's
and the archive's texts; an entry is open unless its Status is an archived one, and only open entries file or lift.
`results` maps `(TD-n, event name)` to a check's outcome (`passed`, `not yet`, `impossible`, `error`), or to
`(outcome, evidence)`. Log ages and `until` dates are read against `today_utc`, `Decided:` dates against
`today_local`. Each item filed is `item_file()`'s arguments (the same names); the host adds today, its `Due:`, session and host. It refuses boards holding no board of `repo`,
a negative or non-whole window, and a `repo` outside the `<repo>` grammar. Per gate of an open entry:
- **`decision (<p>)`**, not covered and with no `kept waiting` Log line for it newer than `reask_days`, and no item
  `covers()` finds answered without a lift within `reask_days`, and not held by an answer owing a lift (below): a `decide` whose text is the entry's Ask (else its
  title), its answers the entry's own (*An entry's own answers*: `entry_answers()`'s `answers`, `default` and `lifts`),
  else `Answers: Go | Not yet.` (v3.3: also when the entry's answers are refused, its detail context then saying
  so), on **the person's board**: this repo's own if its `People:` lists `<p>`, else the
  listing board with the lowest pick key (`origin_key`, bytewise; boards with no readable origin after, by lowercased
  basename). Its Context is `TD-n decision (<p>)`, written `<repo>#TD-n …` on another repo's board. From v3.3 its
  detail block's context is the entry's `**Context:**` section (*The entry*, *Data fields*), its whitespace collapsed
  to one line, where the entry has one; else it is the sentence earlier releases wrote. When no board
  lists `<p>`: an `act`, `decision (<p>) on TD-n has no board: …`, on this repo's own board.
  An **answer owing a lift** (v2.7) is an item `covers()` would find for an entry's `decision (<p>)`, closed, whose
  `Decided:` label lifts, dated `D` no later than `today_local`, given by `<p>` (or by no one named, or, under `Answered by: any`, by a name on
  `People:`). It owes the lift to each entry it covers (its Context entry, in the ledger or the
  archive, and each `Parts:` id `Part of` it) that is open and carries the gate, and whose Log has no `gate lifted:` line for the gate dated on
  or after `D − 1` and no `gate added:` line for it dated on or after `D + 2` (a board's date is local, a Log's UTC).
  The answers owing for one Context entry and gate, on any board read, file one `act` on the newest one's board
  (between boards whose newest answer shares that date, the first by pick key), when one of them is within
  `reask_days` and an entry they owe is not covered: Context the Context entry with the gate and ` lift`, its text
  `<gate> on TD-n was answered with a lift on <D> but still stands on <ids>: lift it.`, `<D>` the newest answer's
  date and `<gate>` as its Context spells it, `<ids>` every entry they owe that nothing covers, in number order; not while one of its identity
  is open, nor when one, open or closed, on any board read or its archive is dated on or after the newest answer's
  `D − 1`. An entry
  owed is held: it is not asked again while an answer owing it is within `reask_days`, or while an act
  for the Context entry and gate of an answer owing it is open on a board read or filed in the same sweep.
  Where any answer in the group is delegated (v3.4), the act follows the newest delegated answer `d` (ties broken
  by the pick key, as `last` is) instead of `last`, its delegate, person and scope as `d`'s `Decided` writes them:
  its `text` is today's with ` by <delegate> for <person> (<scope>)` after `answered with a lift` and `d`'s date in
  place of the newest, exactly
  `<gate> on <ref> was answered with a lift by <delegate> for <person> (<scope>) on <d's date> but still stands on <ids>: lift it.`,
  its `detail.context` likewise, exactly
  `<ref>'s <gate> was answered with a lift by <delegate> for <person> (<scope>) on <d's date>, and the item was closed as lifted, but the gate was never lifted on <ids>`,
  its `detail.question` today's, and its `detail.recommended` exactly
  `Lift it with ledger.py set --blocked-by … --by <person> --delegate <delegate> --scope <scope> --answer "<answer>"; that PR goes to review. Not an override, which would record the person's own lift; to ask again instead, close this and add the question`,
  `<answer>` being `d`'s label, and `set --blocked-by …` written as shown, with no entry id and a literal `…`
  (the act's ids name the entries, and the session fills the gates each keeps; today's act recommends an
  override, which has no such form). With no delegated answer in the group the act is today's, byte for byte. Its
  board and ids are today's (from `last` and the group). The longer `text` is the package's; a consumer's rules
  for text a person reads apply where it shows it. Elsewhere the sweep reads `decided_by`, the person: a delegated
  answer covers its gate and opens the `kept waiting` window as the person's would;
- **`until D`**, D reached: a lift, `kind: until`, evidence `date reached`. Nothing is filed;
- **`event (<name>)`**, by its outcome, on this repo's own board: `passed`, a lift (`kind: event`, the result's
  evidence); `error`, an `act` `Event check broken on TD-n: …`; `impossible`, a `decide` `… can no longer happen.`
  with `Answers: Drop the gate | Rewrite the check | Drop the entry. Lifts: Drop the gate.`; `not yet` with the gate's
  age (`gate_age`) over `event_age_days`, a `decide` `Still waiting on <gate> for TD-n?` with `Answers: Keep waiting
  (default) | Drop the gate | Rewrite the check. Lifts: Drop the gate.`; no outcome, nothing. At most one per gate;
- **a `gate lifted: … ; board <repo>` Log line** whose named board, open, closed or archived, holds no item with a
  `Decided:` whose Context names `<this repo>#TD-n` (a board not read holds none): an `act` on this repo's own board,
  `… holds no decided item …`, its Context `TD-n <gate> board <repo>`.

**One filing rule** holds for every item but the decision's own (whose rule is *covered*, above) and the `was answered with a lift`
`act` (whose rule is the same bullet's): an item's identity
is its Context's entry, gate and what follows the gate, its kind, and its fixed words (`has no board`, `Event check
broken`, `can no longer happen`, `Still waiting on`, `holds no decided item`) read in the item's words (v3.0: on a
v2 line, words a Context or a reply holds are none of them). It is filed only when no item of that
identity is open on any board read, none was answered within `reask_days` with a label that does not lift (dated by
its `Decided:`, not its `Closed:`), and the entry's Log has no `kept waiting` line for the gate within it. An item
closed with the why `lifted`, or closed with no answer, opens no window. One whose lift never happened owes it, and is the `decision (<p>)` bullet's (above).
An item the sweep filed is never rewritten: an entry that gains answers keeps the item already open.

**The close rule.** Of the open items about this repo's entries on any board read, the sweep closes (by id):
- never one decided with a work order (an answer that neither lifts nor only waits); nor one whose Context entry is
  in neither the ledger nor the archive, which is left for a person;
- the gate is **gone** when neither the Context entry (open) nor any `Parts:` id carries it. Any `decide` keyed to
  the entry and gate, and the host's `lift was closed` item (Context `TD-n <gate> lift`, without `was answered with a lift`),
  close once it is gone;
- the `was answered with a lift` `act` once no answer on any board read for its Context entry and gate owes the lift
  (v2.7);
- `has no board` once it is gone or covered; `Event check broken` once it is gone or the check's outcome is not
  `error` (no outcome changes nothing); `Still waiting on` once it is gone or the check says `impossible`;
- the `; board <repo>` audit's `act` once that board holds the answer, or the Log line is gone.

**What a sweep reads** (v3.0): each board whole, every month of its archive. An answer owing a lift may be of any
age, and keeps the sweep's act open while it owes; the `; board <repo>` audit takes a decided item of any date. The
rules that judge a window reach back to `today_utc − reask_days − 2` (a `Decided:` date is read against
`today_local`, up to a day from UTC, and an item closes no earlier than it is decided), but those two reads need
every month, so a sweep reads no board with `since`.

**Preamble lines** — `Name: value` lines before the items (`Kinds:`, `Format:`, a dated stamp
`Name: YYYY-MM-DD (…)`) are kept byte for byte by every edit. On a board read from a directory (`form` `"dir"`,
*Reading a board*) they are `README.md`'s lines, every one of which is preamble, a line shaped like an item among
them (v3.0). `README.md` is the one file a stamp rewrites, so two stamps written on two branches still conflict
there. Which stamps a consumer writes and
what they mean are the consumer's.

**The merge gate's verdicts** (v2.4) are pure functions over a PR's **trees**, each a map from path to text
read at the PR's base or head: the ledger at `docs/ledger/` (v2; a tree with no file under it holds a v1 ledger at
`docs/technical_debt.md`), and this repo's board at `docs/user_attention/` (v3.0, `BOARD_DIR`), or, in a tree with
no file under that directory, the v2 board at `docs/user_attention.md` and its archive at
`docs/user_attention_archive.md` (`BOARD_V2_PATH`, `BOARD_V2_ARCHIVE_PATH`, until v3.0 `BOARD_PATH` and
`BOARD_ARCHIVE_PATH`); the board is what `load_board()` over the tree reads at `BOARD_DIR` when the tree holds a
file under it, else at `BOARD_V2_PATH`, and a stub alone there is no board; the ledger's paths are
`LEDGER_DIR` and `LEDGER_V1_PATH`. A tree holds the same
board paths at the base and the head: every file directly in `BOARD_DIR`, and every file under its `archive/` at a
path the PR's file list names (a moved file's old and new paths both). A verdict judges a PR's board changes from
the two trees, as the paths added, removed and changed in text, never from how the forge reports a move. Each
verdict names what it finds as `(kind, text)` pairs; `repo` is as for the sweep. The consumer fetches the trees,
the file list, the commits and the dates from the forge, and acts on the verdict.

`tripwire(base_tree, head_tree, subject, repo)` runs on every PR, the `set by=` route included, and returns its
flags: each `decision (<p>)` that an entry open at the base and at the head loses, unless the diff accounts for
it. It reads this repo's own board alone, at the base and at the head, never another repo's, so its verdict is
the same on every machine. The diff accounts for a removal by a new `gate reassigned` or `override:` Log line for
the gate, or by a new `gate lifted … answer` line whose suffix fits the board (`covers()`, states `open` and
`decided`, being what covers):
- **no suffix:** an item covering the gate at the base carries a new or changed `Decided:` at the head (open and
  decided, or closed), or, decided already, is newly closed with the why `lifted` (`Closed: D — lifted`; on a v2
  line `— lifted.`) (the last part of a shared item an older
  writer decided; from v2.7 the last part's item is undecided at the base and gains its `Decided:` with its
  `Closed:`);
- **`; no board item`:** nothing covers the gate at the base, nor at the head, so closing a covering item with
  no answer and logging `no board item` is flagged (`tripwire-no-board-item`). A board with no `People:` covers
  nothing, so every lift there is written so;
- **`; shared board item left open`:** an item covering it at the base still covers it at the head, and another
  entry it lists (its Context entry or a `Parts:` id) still carries the gate; and (v2.7) no such item gains a new
  or changed `Decided:` at the head while it stays open, since that answer would speak for the entries left
  (`tripwire-shared-decided`);
- **`; board <repo>`:** `<repo>` names a repo other than this one; the sweep's audit is the backstop.

A lift line whose `by` is not the gate's person is flagged (`tripwire-by`) unless it has no suffix, the base board
says `Answered by: any` and lists `by`, and the covering item's head `Decided:` names `by`. The other flags are
`tripwire-unanswered` (no line accounts for it), `tripwire-no-decided`, `tripwire-no-board-item`, `tripwire-shared`,
`tripwire-shared-decided` (v2.7) and `tripwire-board`. Where the tripwire compares an item's answer (v3.4) it
compares `(decided, decided_by, decided_delegate, decided_scope)`, so a change of the delegate alone is a change of
the answer.
Exempt are an entry the diff archives and the one-time migrate commit, known by its subject alone, `ledger:
migrate v<release> (<n> entries)` (written by v2.x's `migrate`; `subject_kind()` still names it `migrate`). The tripwire is
forgeable, and says so: a well-formed hand edit passes it, and review is the backstop.

`lift_pr_verdict(base_tree, head_tree, files, subject, commits, created_at, merged_at, repo)` returns `{carve_out,
flags, review}` for a PR whose one changed board item gains a `Decided:` and whose Context names a gate:
`carve_out` says the person's answer is its review; otherwise `review` names the first condition that sends it to
ordinary review; `flags` are `tripwire()`'s over the same trees. `files` are the PR's changed paths, `commits` its
commit count; `created_at` and `merged_at` (None while it is open) are the forge's dates, each a date or an aware
datetime, taken as its UTC date. The carve-out needs every one of:
- **(a0)** the base board declares `People:`;
- **(a)** the commit's subject is a board `decide` (`edit_action()`), and the PR is one commit (squash-merged);
- **(b)** the PR's changes to the board are one item's: its open file changed in place, or removed with
  `archive/<YYYY-MM>/<id>.md` added, the same `<id>` and any month (the item closed), and no other board path
  changed. The base item is an open `decide` naming one entry and one
  gate, never answered, that gains `Decided: D by <p> — <label>` (else review: `lift-board-diff` when the changes
  are not one item's, the base file is no open item or the head file is no item file, open or closed, of that
  id; `lift-no-gate`, `lift-reanswer` or `lift-not-answered` for the base item's kind and gate, its earlier
  answer, or a missing `Decided:`); the head file is `edit_item(base file, "decide", label, by, D, close=closes(item, label,
  entries after))` byte for byte at `item_path(id, closed)` (else `lift-board-line`), so a work
  order is never closed and a finished lift never left open; D lies from `created_at − 1` to the merge date (else
  `created_at`) `+ 1`, the board's local day running up to a day from UTC. A lift on a v2 board, a v2 base or head (a
  split PR included), takes review (`lift-board-v2`, v3.0): no v3 writer writes one;
- **(c)** for this repo's entry, the ledger is v2 (a v1 ledger's lift takes review) and `decide_lift()` of the
  base item's file, the base texts of its Context and `Parts:` entries that the base ledger's directory holds, whatever
  their Status, and, in `archived`, the ids of those only its `archive/` holds (by which text holds the heading,
  not by Status; v2.6), with the base board's `People:` and `Answered by:`, accepts the answer, and `closes()`
  reads the open texts after it; the PR changes exactly the item's files and the open file of each entry it changes, each
  byte-equal to its result; every new Log line carries one date T, which is `decide_lift()`'s today, within a day
  of `created_at` and not after the merge (else `created_at + 1`). An answer that changes no entry is windowed by D
  alone. A suffix, a host's lift, an override or a reassign cannot equal `decide_lift()`'s output, so takes
  review. **For another repo's entry** (`<repo>#TD-n`, never this repo's), the PR changes the item's files alone, the
  gate's person and the answerer are on `People:`, and under `owner` the answerer is the gate's person.

In (b), a delegated `Decided` (v3.4) is `D by <delegate> for <person> (<scope>) — <label>`, and the head file is
`edit_item(…, by=<person>, delegate=<delegate>)`, the scope read from the item's `Scope`; in (c), for a delegated
head, `decide_lift()` is called with the head's `delegate` and the item's `scope`. A `Decided` written in the PR by
a delegate passes `lift_pr_verdict()` only when `delegate_problem()` finds no fault over the **base** board and item
(a grant covering the item's `Scope`, a person who may answer it as an undelegated answer is judged, a gate on this
repo's entry), tested right after the answerer and date checks; else `lift-delegate-uncovered`, its text
`delegate_problem()`'s message. For the recompute it resolves a delegated answer's delegate to the base grant's
spelling and its person to `People:`'s; an undelegated answer's person is passed as written, as before. An
undelegated `Decided` is judged exactly as before, on an item with a `Scope` as on any other: the test is not run
and the recompute takes no delegate and no scope. A gated Context that is not one entry and one gate never reaches
that test: it is `lift-no-gate`, as for any answer, so rule 5 is the writer's and `item_file_problem()`'s; a lone
`#` ref naming this repo is `lift-delegate-uncovered` (rule 4), the test running before `lift-own-ref`. A PR that
also rescopes the item and answers in the new scope is `lift-ledger` (the recompute takes the scope from the base
item, and the ledger is recomputed first), one whose `Decided` alone carries another scope, or that changes only
the item's `Scope`, is `lift-board-line`, and one that also changes `README.md` is `lift-board-diff`, as for any
lift PR. A delegated answer is written only with its ledger half, in the same PR (the decide lift).

**The order** (v3.0): `review` names the first condition that fails, the board's presence and form first, then
the files, then the diff, each before (a0): a base or head with no board (`load_board()`'s `form` None, read from
`BOARD_DIR` when the tree holds a file under it, else from `BOARD_V2_PATH`, so a stub with no directory is no
board) takes review (`lift-no-board`, naming `BOARD_DIR` and `BOARD_V2_PATH`); then a v2 base or
head (`lift-board-v2`); then a path in the file list outside `BOARD_DIR/`, `LEDGER_DIR/`, `LEDGER_V1_PATH` and the v1 archive, or under `BOARD_DIR/`
but neither directly in it nor under `archive/<YYYY-MM>/` (`lift-files`); then board changes that are not one
item's, then one item's change whose base file is no open item or whose head file is no item file (open or
closed) of that id (both `lift-board-diff`); then the checks from `lift-not-answered` to the ledger and changed-set checks in today's order ((a0) and
(a) before the `Decided:` by and date), and last the head file's path and
bytes (`lift-board-line`).

(d), a PR only, is the consumer's: a direct commit that answers a gate's item is refused by its own audit.

`lift_form(tree, tid, gate, repo)` (v3.3) returns `(case, items)` for open entry `tid` (found by number, and
open as the tripwire reads the ledger: its file directly in `LEDGER_DIR`, its Status open) carrying `gate`, a
`decision (<p>)`, read against the tree's own board: the form a lift of it takes. An item *lists another gated
entry* when its Context entry or one of its `Parts:` ids is a bare `TD-n`, open in the tree's ledger (as the
tripwire reads its open entries), not `tid`'s number, and carrying the same gate. Of the items `covers()` names covering the gate (states `open` and
`decided`), the first case that holds is the form: `asked`, an undecided item that lists no other gated entry
(the lift is the item's answer, the decide lift); `decided`, a decided item that lists no other gated entry
(the lift has no suffix, and closes every such item `— lifted`); `shared`, an item that lists another gated
entry (`; shared board item left open`); `none`, no item (`; no board item`). `items` are the items that
decided the case, every one to close for `decided`, in the board's item order. It refuses an entry the ledger does not hold open or that
does not carry `gate`, a gate that is no decision, a v1 ledger, and a `repo`
`_check_repo()` refuses; a tree with no board, or a board whose `People:` does not list the gate's person, is
`none`.

`ledger_lift_verdict(base_tree, head_tree, files, subject, commits, created_at, merged_at, repo)` (v3.3)
returns `{carve_out, flags, review}` for a PR that lifts one entry's decision on the ledger, its arguments
and its `flags` as `lift_pr_verdict()`'s. `carve_out` says the diff is exactly the writers' lift of one gate by its
person, the shape the person's press writes; otherwise `review` names the first condition that fails, in this order:
- a v3 board at the base and the head (`ledger-lift-no-board`, `ledger-lift-board-v2`), whose base declares
  `People:` (`ledger-lift-no-people`);
- the subject is a lift (`lift_subject_parts()`), and the PR is one commit (`ledger-lift-subject`);
- the base ledger is v2 and holds the subject's entry open (by number; its file directly in `LEDGER_DIR` and
  its Status open) carrying the subject's gate (the person in any case), and the head holds it open
  (`ledger-lift-entry`);
- every path in `files` is that entry's open file or a board path `lift-files` admits (a file directly in
  `BOARD_DIR`, or under its `archive/<YYYY-MM>/`), and every path the trees change is that file or under `BOARD_DIR/`
  (`ledger-lift-files`);
- the entry's Log gains exactly one line (as the tripwire reads new lines), a `gate lifted:` line for the gate with an `answer`
  (`ledger-lift-log`), whose `label`, `by` and date `T` the checks below read;
- the subject's person, the gate's person and that line's `by` are one name in any case, which the base
  board lists on `People:`; `Answered by: any` admits no other (`ledger-lift-by`);
- `lift_form()` of the base is not `asked` (`ledger-lift-asked`);
- (v3.4) the Log line is not delegated (judged once the one new `gate lifted … answer` line is found, before its
  date is read and `ledger-lift-by` is judged), and no item `covers()` names over the base entry and board in an
  open or decided state carries a delegated `Decided` (judged right after `ledger-lift-asked`, whichever form
  `lift_form()` chose) (`ledger-lift-delegated`): a delegated ledger lift goes to review;
- the head entry is `lift_gate(base text, gate, by, answer=label, suffix=S, today=T)` byte for byte, `S` the
  form's suffix, any refusal from `lift_gate()` failing too (`ledger-lift-bytes`); the board is unchanged for
  `shared` and `none`, and for `decided` changes exactly each item the form names, its open file removed and
  `item_path(id, C)` added as `edit_item(base file, "done", why="lifted", today=C)`, `C` the head file's
  readable `Closed:` date and one head file for each id, the board's changes being every changed tree path
  under `BOARD_DIR/`, each such item's base `Decided:` naming the gate's person in any case
  (`ledger-lift-board`); the entry's bytes are judged before the board's;
- `T` lies within a day of `created_at` and not after the merge (else `created_at + 1`), and each `C` from
  `created_at − 1` to the merge date (else `created_at`) `+ 1`, the board's local day running up to a day
  from UTC (`ledger-lift-date`);
- `flags` is empty (`ledger-lift-flagged`).

The carve-out trusts what `lift_pr_verdict()`'s does: a diff that is one writer's output from the base, for
one answer by the gate's person on `People:`. Unlike a decide lift it needs no question on the board, in
`shared` it takes one entry out of an open shared question, and in `decided` it ends a work order the person
answered. Its suffix is read from this repo's board alone, so a `; board <repo>` lift takes review
(`ledger-lift-bytes`). As for `lift_pr_verdict()`, a `Refused` from `tripwire()`, which runs first, or
from the dates and `commits` escapes; past them a text the verdict cannot read is a reason: an item file the
board reader skips, or a `Refused` or `ValueError` from `edit_item()` or `item_path()`, is `ledger-lift-board`, and any refusal
from `lift_gate()` is `ledger-lift-bytes`. The Log line stays forgeable, and nothing in the format
re-reads the lift once it merges (the sweep's audit reads `; board <repo>` lifts alone): the consumer's own
audit is its backstop, and a direct commit of this shape is the consumer's to refuse, as for the decide lift.

`uncovered_decisions(base_tree, head_tree, boards, repo)` returns `(refusals, flags)`. `boards` are other repos'
boards read, as the sweep takes them; this repo's own is read from `head_tree`, in place of any in `boards` that
names it. A `decision (<p>)` an open entry gains in the diff is refused (`decision-uncovered`) when this repo's
board lists `<p>` on `People:` and no item on it covers the gate, and flagged (`decision-elsewhere`) when the board
does not list `<p>`, since its coverage then rests on another repo's board, which not every machine reads. A new `decide` item on this repo's board (its id on no base item: open, or closed in an archive file the tree holds) whose Context names a
decision and none of whose answers lifts (*Closing on the answer*) is refused (`decision-no-lift`). Refusals rest on
this repo's own board alone, so they are the same on every machine.

## The board as a directory (v3.0)

A v2 board is one file that every new item is written into at one place, so two changes that each add an item
conflict, and an item's identity is its text (*The item key*). **A v3 board is a directory** (by convention
`docs/user_attention/`) with one file per item, named by the item's id:

```
docs/user_attention/
  README.md                  # the opening prose, then the preamble lines: Ledgerboard: 3, People:, …
  2026-11-11-3f9a2c1d.md     # one open item
  archive/
    2026-11/
      2026-10-30-0b7e41aa.md # a closed item, filed under the month of its Closed: date
```

- **`README.md`** holds what a v2 board holds before its first item, and declares `Ledgerboard: 3` on a preamble
  line. Every line of it is preamble.
- **An open item** is a file `<id>.md` directly in the directory; **a closed one** is `archive/<YYYY-MM>/<id>.md`,
  `<YYYY-MM>` its `Closed:` date's month (`item_path(id, closed=None)`, `closed` that date). Any other file is not
  an item. Closing an item moves its file in the same write; nothing else moves one, and none is deleted.
- **No sections and no stored view.** What needs the person, and in what order, is `needs_you()`'s; a person reads
  the board through `board.py show`.

**The item id** is `YYYY-MM-DD-<8 hex>`: the item's `Added` date, a hyphen, and eight lower-case hex digits
(`item_id(added, nonce)`, `added` a `YYYY-MM-DD` string and `nonce` a string, which raises `ValueError` for
anything that is no id, a date that is no day of the calendar among it).
`is_item_id(s)` says whether a string is an id: the shape, matched whole, and its date a day of the calendar, so
`2026-02-30-abcd1234` is none. `item_path(id, closed=None)` gives an item's path, `closed` its `Closed:` date as
`YYYY-MM-DD`, or None when it is open, and raises `ValueError` for an `id` that is no id, or for a `closed` that
is no day of the calendar in that form. `key_id(key)` is the first 8 lower-case hex digits of the SHA-256 of the
key's UTF-8 bytes. A v2 item's id is its line's date and `key_id()` of its key (*Reading a board*). The writer
draws the nonce at random and draws again for a name the directory or its archive holds; the module draws nothing.
No writers coordinate: two items added on one day share an id about once in four billion pairs, and two changes
that add one id conflict as two files at one path. An id never changes.

**The item file** is a small entry, in the grammar of *Ledger entries and their edits*:
- **The heading** is `## <text>`, the item's words (`BoardItem.words`): one line, any words, no field. Its first
  bold run is the item's bold head (*The bold head*).
- **The header block** is the `**Name:** value` lines from the first non-blank line after the heading (the
  writers leave one blank line there; a file with none still reads), up to the next blank line, read as an
  entry's are: a name compared by `field_key()`, which ignores case and reads `-`, `_` and any run of
  whitespace as one space; the spaces and tabs at a value's ends dropped; and the first of a name winning. A value
  is the whole line: it holds any words, a field's name among them. The fields, in the order the writers write
  them, each meaning what *The board* says:
  - `Kind` — `decide`, `act`, `look`, `watch` or `fyi`, read ignoring case; none is the kindless to-do;
  - `Added` — the date the item was added, its id's date;
  - `Session` — `<name>` or `<name> on <host>`, the v2 head; none for `n/a`, and none on a decided file
    (`decided_file()`, the v2 `(person)` head);
  - `Context` — what the item refers to, its refs read as a v2 Context's are; `none` for nothing;
  - `Parts` — a `decide`'s snapshot, `TD-15, TD-16`;
  - `Doer` — on an `act` only, who should do its step: `<repo>`, a repo whose last part does not end in `.`
    (*Appendix: grammar*, `doer-repo`), or `team <team>`, `<team>` a person's name; `Doer: team` alone names the
    repo `team`. `doer_value(value)` reads it as `("repo" | "team", name)`, or None outside that form,
    reading a run of spaces or tabs after `team` as one space (`item_file_problem()` faults that spelling);
  - `Scope` (v3.4) — on a `decide` only: one name, the kind of decision the item is, written by whoever raises it; a
    delegate may answer the item only under a grant naming it (*The board*, `Delegates:`);
  - `Due`, `Hide until` — a date each; a `Due` that is no day is reported as written (`bad_due`; an empty one as
    `""`, which a reader tests as present, `bad_due` not None), never silently undated; on an `fyi`, a `Due` is ignored, and flagged (`fyi_due`), as on a v2 line;
  - `Answers`, `Lifts` — as on a v2 line, without the final period;
  - `Decided` — `<date>[ by <person>] — <label>`: the date and who answered first, so the label runs to the line's
    end and holds any words; `<person>` is a name in the person grammar, as in a v2 `(by <person>)`, so a value
    whose text from `by ` to the first ` — ` is no person is outside the form. The label is never split on a
    trailing `(by …)`: the person is only the `by <person>` before ` — ` (`2026-11-12 — Go (by pat)` is decided
    `Go (by pat)`, by no one). `parse_decided_value(value)` reads it as `(label, date, by)`, or None outside that
    form, and `parse_item()` reads it into `decided` and `decided_by`, and a delegated value's delegate and scope
    into `decided_delegate` and `decided_scope`; the `Scope` field into `scope`; `parse_decided()` and
    `parse_decided_by()` read a v2 line's. Or, answered by a delegate, `<date> by <delegate> for <person> (<scope>) —
    <label>` (v3.4): `parse_decided_value()` returns the person as `by`, and `parse_decided_delegation(value)` the
    `(delegate, scope)`, None for an undelegated value. `item_file_problem()` faults a delegated value on an item
    with no `Scope`, with a scope other than the item's, whose delegate is its person, on a gate on another
    repo's entry, or on a gated Context that is not one entry and one gate. `item_record()` gains
    `scope`, `decided_delegate` and `decided_scope`;
  - `Closed` — `<date>` or `<date> — <why>`, read by `parse_closed_value(value)` as `(date, why)`, or None outside
    that form.

  `Answers` and `Lifts` values are read by `parse_answers_value(value)`: the answers split on each bar not after a
  `\`, `\|` read as a bar, each trimmed, an empty one dropped as on a v2 line (`Go | | No` offers `Go` and `No`)
  (`split_answer()` then reads an answer's label, mark and consequence).
  Each value reader reads the bare value the header line holds; the v2 readers (`parse_decided()`,
  `parse_answers()`, `parse_lifts()` and the rest) find a field on a v2 line and read nothing else.

  A line in the header block that is no field does not end it: it is in no field, every edit keeps it byte for
  byte, and `board_dir_problems()` names it. A value not in its form, for `Decided`, `Closed`, `Kind`, `Hide
  until`, `Parts`, `Doer` or `Scope`, is kept, and read as the field absent: no answer, no close, no kind (so a to-do,
  shown), not hidden, no parts, no doer, no scope; `board_dir_problems()` names it. A `Due` not in its form is
  reported, as *The board* says. A field on a kind that does not take it (`Parts` or `Lifts` off a `decide`, `Doer`
  off an `act`, `Scope` off a `decide`, `Answers` on a kind that takes none) is read as written, as a v2 line's is; `item_file_problem()` faults
  it and `board_dir_problems()` names it. A file is cut into lines at `\n` alone, a line's `\r` before it dropped,
  so no other line-break character ends a value. A field the reader does not
  know is kept: it is in `BoardItem.fields` (every header field as written, in its order), every edit keeps its
  line byte for byte, and `item_file_problem()` faults it. A later v3 minor that adds a field changes nothing an
  older v3 reader reads of the others; an older v3 gate faults an item carrying it.
- **The body** is the detail block (*The detail block*): the lines after the header block up to the Log, leading
  and trailing blank lines dropped (`BoardItem.detail`). No edit touches it.
- **The Log** is the body's last section, led `**Log:**`, one line per reply, `- YYYY-MM-DD: <name>: <words>`,
  oldest first. `<name>` holds no `:` and is at most 40 characters; `<words>` are not empty. A Log line in another
  shape is kept, and read as no reply.

`parse_item(text, path="")` reads one file as a `BoardItem`: its `id` from the path's name (`is_item_id()` of its
stem; None when it is not one), `path`, its `words` (the heading's text), its fields, each value through its reader above (`kind`,
`due`, `hide_until`, `parts`, `answers`, `default`, `consequences`, `lifts`, `decided` and `decided_by`),
`added` (a `datetime.date`, or None), `session` and `host`, `context`, `doer`, `closed` (`(date, why)`, the date a
`datetime.date` or None and the why a string or None, or None when open), `replies`, `detail`, `fields`, and `raw`,
the file's text as read; the dates are of `due`'s, `hide_until`'s and `decided`'s type, and a record writes each as
`YYYY-MM-DD`. `closed` is set from the path: under `archive/`, the `Closed:` value,
or `(None, None)` when there is none in its form; elsewhere, the `Closed:` value, or None. `item_record()` gives its
record (*Reading a board*).

**Reading a board** (`load_board(path, ls, read, *, since=None)`) gives a `Board`: `form`, `path`, `major`,
`preamble` (`README.md`'s text, or, for a board read from a file, the text before its first item), `items` (the
open items), `closed` (every closed item read, its archive's among them), each a `BoardItem` with its `id`, and
`problems`. `form` is `"dir"` for a board read from a directory (through a stub too), `"file"` for one read from a
file and its archive, and None for an empty `Board` read from nothing; how a board is read, ordered and judged
turns on its `form`, never its `major`. `path` is the path `load_board()` was given (the board file, the stub or
the directory; on an empty `Board`, the path that was missing).
- **A directory** is read as `README.md`, then each `<id>.md` directly in it, then each month under `archive/` and
  its files (*The board's order*, below, orders what it reads). A month is a directory directly under `archive/`
  named `YYYY-MM`, a real month; nothing else in the directory is read (rule 11). An item is closed when its file
  lies under `archive/`, or lies outside it and carries a `Closed:` in its form; every other item is open. An
  archived file with no `Closed:` in its form is damaged (rule 9 below) and read as closed, with no date. An id
  held by two files is read once (rule 8): an archived copy wins over an open one, and of two archived copies the
  later month's.
- **The board's order:** `items` and `closed` are each in id order descending, newest first, on a `"dir"` board,
  and in line order on a `"file"` one (`closed` the board's closed lines, then its archive's), whatever `major`
  either declares. Every reader that lists items lists them so, and *What needs the person*'s ties fall back to it.
- **A board read from a file** is read with its archive beside it (`<stem>_archive.md`) by the v2 line reader as
  the last v2.x release has it (`parse_board()`), whatever fields it reads filling the `BoardItem` fields of the
  same name (its `context` read with its reply tails taken out, `reply_span()`, as the gate reads it), but for
  twins: an open line sharing its id with a closed line on the board or in its archive is closed, and the closed
  line is the item (v3.0; v2.x matched twins within one file, by `item_key()`). Two open lines of one id, or two
  closed ones, are both read, each an item with that id, and named in `problems` (rule 10); `to_close` names the id
  once, and a closer of the board closes every open line of it. An item read from a line has as its id the line's
  date, a hyphen, and `key_id()` of its key: `item_key()` of `- [ ] ` and the line's text after its tick (its
  indent, tick and the whitespace after the tick dropped), trimmed. So it reads with the id its split file gets, a
  closed line with its open twin's, and a consumer that persisted a hash of that key finds it in the id
  (`key_id()`, *The item id*). A line with no readable date has id None, which equals no id, None included: such a
  line is matched, for the twin rule and rule 10, by `item_key()` of its line (its indent kept, as v2.x matched
  twins) with the other undated lines, never with a dated line's id, and no by-id read or write names it
  (`to_close`, *The gate sweep*). Its `BoardItem` carries every field a v3 item does that the line holds, its words
  (`item_words()`: every piece of the line after its prefix outside the spans its fields and replies are read
  from, a field's span with the `.` ending it, joined by one space) as `words` and the line as `raw`; a closed
  line's `raw`, `closed`, `fields`, `words` and `context` are read from the `- [x]` line as written, its `Closed:`
  among them (*A closed item*), and a closed line with no readable `Closed:` date (one whose date is no day, one
  with no `Closed:`, or one whose `Closed:` holds no date, as `Closed: soon.`, which stays in its words) has
  `closed` `(None, None)`. The line's date, which gives its `added` and its id's date, is the date the line's text
  after its tick, trimmed, opens with, after at most one word of ASCII letters and whitespace
  (`^(?:[A-Za-z]+\s+)?(\d{4}-\d{2}-\d{2})\b`), when it is a day of the calendar; its kind is that word only when
  it is one of the five. The prefix is the tick, then an optional word of ASCII letters followed by a date, then an
  optional date, then an optional one head right after the date, of a form the format writes (`(n/a)`,
  `(person)`, or `(session` and whitespace up to the first `)`), then an optional ` — `
  (`^\s*-\s*\[[ xX]\]\s+(?:[A-Za-z]+\s+(?=\d{4}-\d{2}-\d{2}\b))?(?:\d{4}-\d{2}-\d{2}\b(?:\s*\((?:n/a|person|session\s[^)]*)\))?)?(?:\s*—\s)?`,
  case as written), so it ends where the date's head ends whether or not the word is a kind (`- [ ] Foo
  2026-11-11 (session x) — Ping.` has the words `Ping.`, the date 2026-11-11 and no kind); what a line's head does
  not match is words, from wherever the prefix stopped (`- [ ] 2026-11-11 (later) Ping sam.` has the words
  `(later) Ping sam.`). The prefix takes the whole head, to its first `)`; text in it after the session and host
  (`(session s-1 on host-a, branch x)`'s `, branch x`) is read into no field, the v2 reader giving a head's
  session and host only, so it is in neither `words` nor `fields`, and the split does not carry it. Every word of
  the line outside its head is in `words` or a field.
- **The stub**, a file that declares `Ledgerboard: 3`, or a newer major, and holds no item, is read as the
  directory beside it, its name without `.md`. Its own declaration is read too: the `Board`'s `major` is the
  greater of the stub's and `README.md`'s (on the empty `Board` of a stub whose directory is missing, the stub's),
  so a stub declaring a major newer than the module reads is refused as any newer major is (`version_problem()`),
  whatever `README.md` declares.
- **Which form**, in this order: `ls(path)` not None is a directory (`"dir"`); else `read(path)` a text is a stub
  (declaring 3 or newer and holding no items), a file declaring 3 or newer that holds items (rule 5, `"file"`), or
  a v2 file (`"file"`); else the path is missing (an empty `Board`). A missing `<stem>_archive.md` reads as an
  empty archive, as `load()` reads a missing archive; a stub whose directory's `README.md` declares 2 is read as
  rule 4 says, its `major` the stub's, the greater.
- **The caller does the I/O**, as for `load()`: `ls(path)` returns the names directly in the directory `path`,
  each subdirectory's name followed by `/` (v3.0; `load()` ignores those), or None when `path` is not a
  directory; `read(path)` returns a file's text, or None. Every path a `Board` names is relative to the board's
  directory.
- **`since`**, a `datetime.date` or None, leaves the archive's months before its month unlisted and unread, so
  `closed` holds only the months read; the month equal to `since`'s is read. It applies to a board read from a
  directory alone: a board read from a file ignores it, its archive being one file. It is for a reader of open
  items and recent closes; the sweep, `board_problems()`'s `old`, the verdicts and `split_board()` read a board
  whole. A read with `since` applies rule 8's archived-copy-wins only over the months it reads: an open item whose
  archived copy is in a month before `since`'s reads open, a limit of `since`, which is why it is for readers of
  open items and recent closes alone.
- **`major`** is what the preamble declares, else 2 for a file and 3 for a directory (through a stub, the greater
  of the stub's and `README.md`'s); a missing `path` gives an empty `Board` with `form` and `major` None and
  `path` the path given. A board read from a directory has its declaration read from every line of `README.md`
  outside HTML comments (`board_major(text)`), one read from a file from the lines above its first item
  (`board_major(text, file=True)`), 2 when the file declares none: a board's v1 and v2 are one format. The board's
  major is its own: `BOARD_MAJOR` (3) is the newest a module reads, and `version_problem(board)` names a `Board`
  whose `major` is newer; `version_problem(text)`, `format_major()` (whose "none means 1" stays the ledger's) and
  `FORMAT_MAJOR` stay the ledger's. `major` serves that check alone; what a reader does turns on `form`.
- **`problems`** and **`board_dir_problems(path, ls, read)`** never raise. Each rule below is marked `problems`
  (`Board.problems` lists it, as `(path, problem)`: what the read skipped or could not settle) or
  `board_dir_problems() only` (the read settled it, or never read the file). `board_dir_problems()`, which takes
  no `since` and reads the whole tree, names, as `(path, problem)`, every rule of both marks on a `"dir"` board,
  and gives `Board.problems` alone on a `"file"` one. Each rule names its finding once. Both lists are sorted by
  path (code-point order), then by the rule's number, then by line within the file. Only a board read from a
  directory raises rules 1–4, 7–9 and 11–16 (item files, `README.md`, archive months, header blocks); only one read
  from a file raises rules 5 and 10; only an empty `Board` raises rule 6. No rule is raised on both forms, so a v2
  line with no readable date raises nothing: it is read as v2 reads it, its `added` and `id` None.
  1. `problems`: a file `read()` gives None for: skipped, named under its path.
  2. `problems`: a file `parse_item()` reads as no item (its first non-blank line does not open `## `, or the next
     non-blank line is no header field, `**<Name>:** `): skipped, named under its path.
  3. `problems`: a `README.md` that is missing, or declares no major: `major` 3, named under `README.md`.
  4. `problems`: a `README.md` declaring 2: read as a directory, `form` `"dir"`, `major` 2 (through a stub,
     `major` the stub's, the greater: 3 for a stub declaring 3), named under `README.md`.
  5. `problems`: a file declaring `Ledgerboard: 3` or a newer major that holds items (it is no stub): read from
     the file, `form` `"file"`, `major` the file's (a newer one refused by `version_problem()`), named under its
     name.
  6. `problems`: a stub whose directory is missing: an empty `Board`, `form` None, `major` the stub's, named
     under the stub's name.
  7. `problems`: an item file with no `Added`, or one that is no day: read, its `added` None, named under its
     path.
  8. `problems`: one id in two files of a board read from a directory: read once, named once, under the path of
     the archived file that wins (the later month's of two archived copies).
  9. `problems`: a file under `archive/` with no `Closed:` in its form: read as closed, with no date, named under
     its path.
  10. `problems`: one id on two open lines, or on two closed lines, of a board read from a file: both lines read,
      the id named once, with both lines, under the board file's name when either line is on it, else the
      archive's; two undated lines are compared by their key, never by id.
  11. `board_dir_problems() only`: any entry the read does not take: a file directly in the directory, or in a
      month, whose name is not an id and `.md` (its stem failing `is_item_id()`; `README.md` aside); a
      subdirectory of the directory other than `archive/`; a file directly in `archive/`; a directory under
      `archive/` that is not a month; a directory in a month. Each is named once, under its own path (a
      directory's with its trailing `/`), and not read or descended into.
  12. `board_dir_problems() only`: a header-block line that is no field: kept, in no field.
  13. `board_dir_problems() only`: an `Added` that is a day but not the id's date.
  14. `board_dir_problems() only`: a `Decided` or `Closed` not in its form: read as no answer, or no close; a
      `Kind`, `Hide until`, `Parts`, `Doer` or `Scope` not in its form: read as the field absent, a `Kind` outside the five
      as a to-do, shown; a `Doer` that reads but is spelled with more than one space, or a tab, after `team`:
      read; a `Kind` in the wrong case: read as that kind; a `Due` on an `fyi`: read as `fyi_due`; a field its
      kind does not take (`Parts` or `Lifts` on any kind but `decide`, `Doer` on any kind but `act`, `Scope` on any
      kind but `decide`, `Answers` on a kind that takes none): read as written, as on a v2 line.
  15. `board_dir_problems() only`: a `Closed:` in its form on a file outside `archive/`: read as closed.
  16. `board_dir_problems() only`: an archived file in a month that is not its `Closed:` date's: read as closed.
- **The readers take the `Board`**: `needs_you()`, `covers()`, `sweep()`, `board_problems()` and the merge gate's
  verdicts; `board_people()`,
  `answered_by()`, `people_problems()`, `answered_by_problems()`, `board_delegates()` and `delegates_problems()`
  (v3.4) read its preamble, every line of `README.md`
  on a `"dir"` board and the lines above the first item on a `"file"` one, as `board.py`'s
  `who_answered(board, by)` does through `board_people()`; and a consumer calls
  `version_problem(board)` before it trusts the rest. `people_problems(board)` and
  `answered_by_problems(board)` of a `Board` give `(path, problem)` pairs, the path `README.md` for a board read
  from a directory and the basename of `Board.path` for one read from a file; a missing `People:` or `Answered
  by:` line is named under that path too. `board_problems()` raises `Refused` for a `board` read from a file (*The
  gate*). `item_record()` gives an item's record, of either major, with `text` the item's words and no `line`, and
  these keys (v3.0), every other key as before: `id`, a string
  `"YYYY-MM-DD-<8 hex>"`, or `null` for a v2 line with no readable date; `path`, a string, the file's path in the
  directory (`""` for a v2 item); `added`, `"YYYY-MM-DD"` or `null`; `context`, a string, the Context without its
  final period, or `null` for an item with none; `refs`, as before, the refs of `context` (*The board*,
  `Context:`), so a v2 item's never one read from a reply; `closed`, `{"date": "YYYY-MM-DD", "why": <string> |
  null}` (both `null` for an archived file with no `Closed:` in its form, and for a v2 closed line with no readable
  `Closed:` date: one whose date is no day, its `Closed` kept as written in its fields, or one with no `Closed:` at
  all, or one whose `Closed:` holds no date, that `Closed:` staying in its words), or `null` when the item is open;
  `decided`, as before, `{"text": <label>, "date": "YYYY-MM-DD"}` or `null`, `decided_by` beside it; and `doer`,
  `{"kind": "repo" | "team", "name": <string>, "text": <string>}` (`text` the value as written) or `null`.
- **Two reads of one board compared** (a v2 board and its split): records keyed by `id`, `path` and `line` left
  out; `covers()`, `to_close` and `lifts` as lists sorted by id; `needs_you()`'s rows by tie group (each run of
  one class and one `days`), each group as a set and the groups in order. So compared, a v2 board and its split
  read the same.

**Damage a hand edit or a merge can do** is what `board_dir_problems()` names (the rules under *Reading a
board*'s `problems`). The gate judges an item only when it is added, so a consumer calls `board_dir_problems()` on
the board it is about to merge, wherever it calls `v2_problems()` on the ledger.

**Migration** is `split_board(board, archive)`, for a v2 board only: the v3 files of a v2 board and its archive,
by their paths in the directory. **It refuses only where it cannot give an item an id or a month, or where the
read-back's records of the v2 item and its split file would differ** (data lost, or read differently). Every other
shape a v2 board holds and v2 reads is carried as v2 reads it and read alike by the v3 reader. A field not in its
form or on a kind that does not take it, a `Doer` spelled as the writer would not, a `Kind` in the wrong case and
a `Due` on an `fyi` are named by `board_dir_problems()` and listed by `split_board_notes()`, for the caller to fix
on the directory; any other shape (a `decide` with no `Answers`, a `look` whose answers are not the fixed pair, an
unreadable `Due`, reported as `due_error`) is carried silently, as a v2 board holds it, since the gate judges an
item only when it is added.
- Every line of one id across the board and the archive, with its detail block, is one item, closed when one of
  its lines is; it becomes `<id>.md`, or `archive/<YYYY-MM>/<id>.md` when closed, its id the v2 item's. Of twins,
  the closed line and its detail block give every field and the body. Its fields are what the v2 reader reads,
  each in the file's form: `Kind`, `Added` (the line's date), `Session` (none for `n/a` and `(person)`),
  `Context` (without its final period), `Parts`, `Doer` (as written; none for an empty value, whose words stay in
  the heading), `Due` (from the match v2 reads: `Due:` and a day when the first such is a day, else the first
  date-shaped `Due`, with or without its colon, an unreadable one as written), `Hide until`, `Answers`, `Lifts`,
  `Decided` (`<date>[ by <person>] — <label>`) and
  `Closed` (`<date>[ — <why>]`, the why the words after a ` — ` that follows the date, without its final period),
  from the closed line, and any other field the v2 reader reads, as the header field of the same name, whatever
  the item's kind. Its body is the detail block with its common
  indent removed; its replies are its Log. Its heading is `item_words()` of the line: every word the v2 reader
  reads as no field, no reply and no part of the prefix (the text, and any words a hand edit left outside the
  fields), in their order, verbatim but for runs of whitespace collapsed to one space, so no word of the line outside its head is lost (a
  head's text after its session and host, which no v2 reader reads, is not carried, and `split_board_notes()`
  names it, and a host's run-on as `host kept to its first word`) and no
  period is added or removed; a bold head stays in it as written.
- `README.md` is the board's text before its first item, with `Ledgerboard: 3` under its title (any
  `Ledgerboard:` line dropped) and without the `## ` heading nearest the first item (the one heading that opens the
  first item's section; any earlier `## ` heading stays), that heading's line going with the blank lines right
  after it. Its trailing blank lines go and it ends in one newline, so a board whose text before its first item is
  its title alone gives the title, a blank line and `Ledgerboard: 3`. With no `# ` title, `Ledgerboard: 3` is its first
  line, followed by one blank line when other text follows and alone with its newline when none does. Each relative link there gains `../`, since the file
  moves one directory down: the target of an inline link or image (`[t](target)`, `![t](target)`) and of a
  reference definition (`[label]: target`), when it starts with none of a scheme (`[A-Za-z][A-Za-z0-9+.-]*:`,
  `mailto:` among them), `#` and `/`, outside code spans and fenced code; inside `<…>` when the target is
  bracketed, a title after it kept, and a leading `./` becoming `../`. The archive's text before its first item
  is not carried, and `split_board_notes()` lists each of its non-blank lines but its `# ` title.
  Of twins, the open twin's detail block and line are not carried, and `split_board_notes()` names each that
  differs from the closed twin's.
- A line after the first item that is no item, no detail block's line and not blank (a `- (none)` placeholder, a
  note), on the board and then on the archive, is carried, in order, to the end of `README.md` after one blank line, with each `## ` heading after the
  first item that stands above a carried line; a heading with no carried line under it is dropped. A relative link
  in a carried line gains `../` by the rule above, the file having moved too. Nothing is
  lost, and `split_board_notes()` lists each carried line, since no item holds it (a paragraph a session set
  below an item after a blank line, which the v2 reader never read as that item's, among them), and what may
  describe the v2 board.
- It refuses a board that declares a major above 2 (`Ledgerboard: 3`, a stub's, among them); an item with no date, or a date that is no day of the
  calendar; a closed line with no readable
  `Closed:` date (no month to file it under: date it first); two open lines, or two closed lines, of one id; two
  items given one id; a carried line that is a `People:`, `Answered by:`, `Delegates:` (v3.4) or `Ledgerboard:`
  line, which a v2
  reader never read below the first item and `README.md` would read (move or delete it first); a `Due` v2 reads
  as unreadable that v3 would read otherwise: on any kind but `fyi`, a colonless `Due <day>.`, and on any kind
  the `Due` v2 reads lying inside another field's words or a reply's (fix it first; a date-shaped `Due` there that
  v2 does not read stays in those words); and a result that `load_board()`
  does not read back as the same items (open and closed, at one date, compared as *Reading a board* compares two
  reads), or that `board_dir_problems()` flags under any rule but the one that names a field not in its form or
  on the wrong kind. A field on a kind that does not take it, a `Doer` spelled as the writer would not and a
  `Due` on an `fyi` are carried and named; an unreadable `Due` on any other kind is carried and reported as
  `due_error`, as on a v2 line, and named by no rule.
- `board_stub(title, name)` is what `board.py split` leaves at the v2 path: `# <title>`, a blank line,
  `Ledgerboard: 3`, a blank line, and `This board is the directory [<name>/](<name>/), one file per item
  (ledgerboard v3.0).` A v2.x reader that checks the version refuses it, a v2.x writer refuses it unread, and
  `load_board()` reads the directory through it.
- `split_board_notes(files, board, archive="")`, over `split_board()`'s files and the v2 texts they were split
  from, lists as `(path, line number, line, why)`, for the caller to warn about, nothing rewritten: the lines of
  that `README.md` which may still describe the v2 board (a line naming `user_attention.md`,
  `user_attention_archive.md`, `Needs the user` or `In-flight`, and a `Format:` line), then each non-blank line
  carried to that `README.md` from below the first item (a `## ` heading carried with it among them), at its line
  there, `why` `carried from the board's line <n>, below an item: no item holds it` (`the archive's` for one
  carried from the archive, `<n>` its line in that text), then each shape the split
  carried that `board_dir_problems()` names, at its field's line (the first header line of that field's name),
  then each item whose v2 line's head group held more than its session and host, at its `Session` line (with
  none, its heading): where the host's match is followed, after one closing backtick, by a space and words before
  the group's first `,` or `;` (its end, with none), `why` `host kept to its first word; not carried: <run-on>`,
  those words collapsed (v3.3); then, where text remains beyond the run-on, `why` `head text not carried:
  <text>`: the group's text less the session, the host's match with its closing backtick, and its run-on,
  collapsed and trimmed of `,`, `;` and spaces, which no file holds; text before the host stays in it.
  A line of the archive's own text is named at the path `(archive)` and its line in the archive, which `board.py split` gives as the archive's path; an open twin's note is at its file's heading,
  `open twin's detail not carried` or `open twin's line not carried` (a reply, a `Due` or a `Hide until` the
  closed line lacks or holds otherwise).

## Edits

Every edit rewrites one open item file, by one header line set or one Log line appended, and nothing else, and is
refused unless the reader reads back exactly what was meant (`edit_item(text, action, *, to, answer, why, reply,
by, today, close)`, v3.0). A field it adds goes right after the last known field that precedes it in the header
order (any unknown field between them stays where it is), or first in the header block when none does; a field it
sets that is there is rewritten in place. A line it adds or rewrites ends as the file's first line does (`\r\n` or
`\n`); every other byte is kept. An edit of a closed item is refused.
- **snooze** hides the item: it sets its `Hide until:` and leaves its `Due:` alone;
- **due** sets the item's `Due:`, the real deadline;
- **done** sets `Closed: <today>`, or `Closed: <today> — <why>`;
- **decide** sets `Decided: <today> — <answer>`, or with `by` `Decided: <today> by <by> — <answer>`, replacing an
  earlier one. It refuses a `by` that is not a person's name. With `close`, on an item whose Context names a
  gate, it also sets `Closed: <today> — kept waiting` for a waiting-only answer or `Closed: <today> — lifted` for a
  lifting one, and refuses any other answer (`closes()` says when to pass it). An answer that fills one of the
  item's forms is written as its fill, the head as offered (v2.8); one that is a form as offered, unfilled, is
  refused (*<head> needs its words*). With `delegate` (v3.4), it writes the delegated form, the delegate as the
  grant spells it, the person as `People:` does, the scope as the item's `Scope` does, and refuses an answer
  `delegation_covers()` does not allow, on an item with no `Scope`, by a person who may not answer the item, on a
  gate on another repo's entry, or on an item whose Context names a gate but not exactly one entry and one gate; a
  Context that names no gate is not refused for the entries it names. The refusal is `delegate_problem()`'s
  message, one fixed text per rule: `rule 1: the item has no Scope`; `rule 2: no faultless Delegates: grant covers
  <delegate> for <person> (<scope>)`; `rule 3: <person> may not answer this item`; `rule 4: the Context names a gate
  on another repo's entry`; `rule 5: the gated Context is not one entry and one gate`, each `<…>` as the answer
  writes it, `<scope>` the item's `Scope`. `edit_item()` itself needs only the item's text, the scope read from its
  `Scope`, and refuses a delegate with no `Scope`, with no `by`, outside the person grammar or equal to `by`; the
  grant and rules 2 to 5 are the caller's (`delegate_problem()`). Without `delegate` the decide edit is today's, on
  an item with a `Scope` as on any other;
- **reply** appends `- <today>: <by>: <words>` to the Log, opening a `**Log:**` section after the body when there is
  none. It refuses a `by` holding `:` or of more than 40 characters, and empty or blank words.

An edit that closes the item gives a file whose place is `item_path(id, closed)`; the writer moves it in the same
write.

**A new item** (`item_file(text, due, today, session, host, context, *, kind, answers, default, detail,
hide_until, lifts, parts, doer, scope)`, v3.0) is one file: `## <text>`, a blank line, the header block (`Kind` when
given, `Added: <today>`, `Session` when there is a session, `Context`, then `Parts`, `Doer`, `Scope`, `Due`, `Hide until`,
`Answers` and `Lifts` as given), and, after a blank line, the detail block. The text is trimmed and not empty, and
no period is added. An empty context is `none`. `Session` is `<session>` or `<session> on <host>`. `Lifts` is
written only when it names answers other than `Go` alone (each one of its answers, once, written as its answer
spells it). A `doer` is refused on any kind but `act`, and outside its form. A `scope` (v3.4) is refused on any kind
but `decide`, and when it is no name. A decide's `parts` (v2.6) are written
ordered by number, separated by `, `, each as given, and are refused on any kind but `decide`, for an empty list,
for an id that is not `TD-` and 1 to 18 ASCII digits, for an id that shares its number with another or with the
Context's entry, unless the Context names exactly one entry, a bare `TD-n`, and one gate, a `decision (<person>)`,
with nothing after the gate, and unless one of its answers lifts. What a kind takes:
- a `decide` carries two or more distinct answers, at most one marked ` (default)` and never a form (v2.8), no two
  forms with one head (v2.8), and a detail block; `decided_file()` writes no mark on a form, its `default` naming
  one written unmarked;
- a `look` carries exactly `Answers: Works | Not right: <what>`, which the writer writes itself, `Works` marked
  ` (default)` only when the caller asks;
- an `fyi` carries no `Due`, and every other kind carries one;
- no kind but `decide` and `look` carries answers.

These are the writer's rules. The reader still reads whatever a file carries. An answer is written `<label>` or
`<label> — <consequence>`, with the mark on the label.

The **detail block** is composed from named parts, in the order `Context`, `Question`, `Caveats`, `Recommended`.
Each part is one bullet at column 0, ``- **<Part>:** <words>``, with any further lines as nested bullets under it,
indented two spaces. On a `decide` with a default, Recommended opens with that default's label and ` — `, which
the writer adds: a `recommended` whose words already open with that label and ` — ` (whitespace collapsed, the
label compared ignoring case) is refused, naming the prefix (TD-069). An `Otherwise` text follows the Recommended
words on the same bullet as ``**Otherwise:** <words>``. A `decide` needs Context, Question and Recommended. No
writer touches the block afterwards.

The writer refuses a text, a context, an answer, a detail value or a reply's words that is more than one line; a
date that is not `YYYY-MM-DD`; a host with no session; and any result the reader would not read back as exactly the
item meant, its body included. From v3.0 it refuses no field's name in any of them, nor an answer ending in
`(by …)`: each value is a line of its own.

An answer given elsewhere (on a ledger entry) is written as an already decided `decide` item with no `Session`
(`decided_file(title, ref, answers, default, words, today, by=None)`): `## <title>`, its `Context` the ref, `Due`
today, its `Answers`, and `Decided: <today>[ by <by>] — <words>`, with **decide**'s refusals.

**A snapshot against the ledger** (`parts_problems(item, entries, archived=())`, v2.6) lists, and never raises, why
a `decide` item's `Parts:` does not match the ledger. `item` is an item file's text or a `BoardItem` (from v3.0; a
v2 line before it), and its form is left to `item_file_problem()`. A text `parse_item()` reads as no open item, an
item that is no `decide` or is decided, or one whose `Parts:` holds no id `parse_parts()` reads gives `[]`. One
whose Context or parts the check `item_file()` shares faults gives `item: <that fault>` alone (v3.0; `line: <that
fault>` before it), the fault one of `context: not one entry and one decision` (a Context naming two entries, or
going on past its gate, among them), `<id>: another repo's entry`, `<id>: not an id`, `<id>: the Context's entry`
and `<id>: twice`; the kind, an empty list and the lifting answer are `item_file()`'s alone. Otherwise it reads
`entries` (id to text, open and archived alike, by number, the first of a number winning; a key that is not a bare
`TD-` and 1 to 18 ASCII digits is ignored, and a value that is not a string, or holds no entry, is no entry) and
`archived` (the ids read from the ledger's archive, by number). An entry is archived when its number is in
`archived` (whether or not `entries` holds a text for it) or its Status is an archived one. It judges the Context
entry first, `<ref>: missing` or `<ref>: archived`, and then each part still, in the line's order, its first fault
of `<id>: missing`, `<id>: archived`, `<id>: not Part of <ref>`, `<id>: does not carry <gate>`. It is stricter than
*The decide lift*, which skips a part that no longer carries the gate (one archived by its Status, or named in
`archived` and not given, among them), still lifts an `event (<name>)` snapshot and one whose Context goes on past
its gate, and, reading a text it is given ahead of `archived`, lifts a part and a Context entry named in `archived`
whose Status reads `Open`: the snapshot is checked when the question is asked, the lift when it is answered; the
ledger is not in the item, so `item_file()` does not check these, and a writer that reads the ledger calls it.

**The form the writers write** (v3.0) is a file `item_file()` or `decided_file()` composed, as it stands after any
snooze, due, decide or reply. `item_file_problem(text)` names why a file is not in that form, or gives None, in a
plain sentence opening with its rule's tag: a `## ` heading and one blank line; a header block of known fields,
each once, in their order, spelled `**Name:** value` with one space; each value in its form (*Appendix: grammar*,
*The item file*); a kind's rules (*A new item*; a decided file may carry any answers or none, and the form rules bind an open `decide`
with no `Decided` alone); a body of detail
bullets; a Log, when there is one, last and holding replies alone; one blank line between the parts and one
newline at the end. It never judges the detail block's words. `canonical_item_file(text)` rewrites a file into
that form: line endings normalised to `\n`, the known fields in their order and spelled so, any other field after
them in the file's order, one blank line between parts. It refuses a header block it would have to lose or repeat
a line of (a line that is no field, a repeated field), and its result reads back the same item. No key rests on a
file's spelling, so it rewrites any field.

**The gate** is `board_problems(board, old)` (v3.0, both `Board`s, `old` read whole): first `README.md`'s
`People:` and `Answered by:` problems (`people_problems()`, `answered_by_problems()` of the board, the `(path,
problem)` pairs as they come, each `("README.md", problem)`), then (v3.4) `delegates_problems(board, old)`'s
pairs, each `("README.md", problem)`, right after `answered_by_problems()`'s, and on a standing board (no `old`)
the ℹ of each open item whose delegated answer the line no longer covers, then `item_file_problem()`'s fault of each open item
whose id no item of `old` (open or closed) has, as `(path, problem)`, and, on a new `decide` whose Context names a
gate, `decision (<person>)`, a `People:` line that does not list that person. `old` may be a v2 board (a split's
base) or None (every open item judged). An edit keeps an item's id, so an item is judged once, when it is added;
damage a hand edit does to a file already there is `board_dir_problems()`'s to name. It refuses a `board` read
from a file (`form` `"file"`, whatever its `major`), raising `Refused`.

**The commit subject of a board write** is one line: `<tool>: <action> <id> <head>[ to <date> | : <answer>]
(session <name>)` for the five edits, and `<tool>: append <id> <head> (session <name>)` for a new item (v3.0). The
head is the item's words (its heading), every `*` dropped and whitespace collapsed, at most 60 characters, never
cut at a ` — ` or a field's name; `<name>` is the caller's session, else the item's `Session` name, else `n/a`; a
reply's words never appear. `subject_id(line)` reads the id back, or None. `edit_action()`
reads the action back (v2.3). Subjects written before v3.0 still read: a v2 edit's and append's, with no id; those
written before v1 by one consumer (`shiftlead: board|answer <head> (from <ref>)`, `shiftlead: board decide <ref>
(person)`), as appends; and `<tool>: archive <n> closed items (session <name>)`, which no v3 writer writes.
`subject_kind()` names a subject `edit`, `append`, `archive`, (a rank write) `queue` or (a ledger lift, v3.3) `lift`.

**The commit subject of a ledger lift** (v3.3) is one line, `<tool>: lift decision (<p>) on TD-n (session
<name>)`, for a commit that lifts one entry's decision and writes nothing else but the closes the lift owes
(*The merge gate's verdicts*, `lift_form()`): `<p>` the gate's person as the entry spells it, `<name>` the
caller's session, else `n/a`. `lift_subject(tid, gate, tool, session=None)` writes it, refusing a `tid` that is
not a bare `TD-n`, a gate that is no decision, and a tool or session that is not a token of
`[A-Za-z0-9_.@/-]+`; `lift_subject_parts(line)` reads it back as `{tool, gate, id, session}`, each part as
written (`n/a` too), or None.
`edit_action()` and `subject_id()` read board writes alone, and are None for it.

## The board writer (v2.3)

`board.py`, beside the module in the `ledgerboard/` package, is the board and rank writer over files: an
importable library (`plan_add`, `plan_edit`, `plan_fmt`, `plan_split`, `plan_rank`, each returning a `Plan`, `show`, and
`apply(plan)`) and a command line (`python3 -m ledgerboard.board <action>`, a consumer's wrapper
being the command people run). It reads the files it is given, applies the module's edit, and writes the files
back; it never runs git, the network or anything of a consumer's. Its actions:
- **`list`** — every open item's record (`item_record()`), read-only; its plain line `<id>`, a tab, the due tag
  (`-` for none), a tab and the item's words, `-` for `<id>` on a v2 item with no id; the board a directory, the
  stub, or a v2 file;
- **`show`** (v3.0) — the board for a person (`show_board(board, today, hidden=False)`): for each item
  `needs_you()` gives, in its order, the line `*<id> · <class>*`, then the item's file as read, its trailing `\r`
  and `\n` run cut to one `\n` (a v2 item's line and its detail block at the indent its file gives it), items
  separated by one blank line; with `--hidden`, the hidden open items after them, in the board's order (*Reading a
  board*), each `*<id> · hidden until <date>*` (`no id` for a v2 line with no readable date). Read-only; no file
  holds it;
- **`add`** — a new item (`item_file()`, any kind, its answers and detail block, `--hide-until`, `--doer`) at
  `<board>/<id>.md`, the id drawn at random (redrawn while the id is held — an item's in the board, or `<id>.md` or
  `archive/<YYYY-MM>/<id>.md` listed — at most 8 draws in all, the 8th held name refused, `<board>: no free id
  after 8 draws`, exit 1), or `--id`'s, refused when it is no id, its date is not the item's `Added`, or it is
  held (`<board>: <id> is held`). With `--parts TD-a,TD-b` (v2.6), a decide's snapshot (`item_file(parts=)`): the
  option may be repeated, each value is split on `,` and each piece trimmed, and an empty piece is refused;
  `--parts` with `--decided` is refused, and so is `--ledger` without `--parts`. With `--doer <value>` (v2.8), an
  act's doer (`item_file(doer=)`); `--doer` with `--decided` is refused. With `--scope <name>` (v3.4), a
  decide's scope (`item_file(scope=)`); `--scope` with `--decided` is refused. Then the ledger is read (`--ledger <v2
  directory>`, default `ledger/` beside the board when it is a directory, its open and archived entries), and the
  write is refused, with every problem, when `parts_problems()` names any, or when no ledger is found. With
  `--said` and `--by`, a question already answered: its answer is the item's first reply, the Log line `-
  <today>: <by>: <said>`, refused as `reply` refuses (a `--by` holding `:` or of more than 40 characters, empty
  or blank words); `--said` is refused when it holds a character `str.splitlines()` splits on, checked before
  any collapse, and the rest of its whitespace, and `--by`'s, is collapsed as today. With `--decided`, an item
  the person decided elsewhere (`decided_file()`). The write is refused when `board_problems()` faults the item
  it adds. **The order** (v3.0): a usage error (exit 2); `--parts`, `--doer` or `--scope` with `--decided`, an empty
  `--parts` piece, a `--detail` that is no JSON object (exit 1); a bad `--today` (exit 2); `--ledger` without
  `--parts`, a `--decided` item given `--due`, `--kind`, `--detail`, `--session`, `--host`, `--said`,
  `--hide-until` or `--lift`, and on an item not `--decided` `--said` without `--by` or the reverse (exit 1); a
  board declaring a newer major; a write to no v3 board; `--id`'s, or the draw's; the item's own and `--said`'s;
  the ledger's; then `board_problems()`;
- **`snooze`, `due`, `done`, `decide`, `reply`** — the five edits (`edit_item()`) of the open item `--id` names,
  refused when no open item has it; `done --why` strips the why's trailing `.`, `?` and `!` before the edit
  (`edit_item()` collapses it); `done`, and a `decide` that closes the item, write its archived file and
  remove its open one as one write; `reply` takes its `--by` from the caller;
- **who answered** (v2.3) — `decide`, and `add --decided`, write who gave the answer (`who_answered(board, by)`):
  on a board whose `People:` lists one name, `--by` defaults to it; on one that lists several, `--by` is
  required. A `--by` the list does not hold is refused, and one it holds is written as the list spells it. On a
  board with no `People:` line, `--by` is required and checked as a person's name only. A `People:` line the gate
  faults refuses every answer. The caller supplies the name of the person who answered; a commit's author is
  never one, since an agent commits under the person's name. With `--delegate <name>` (v3.4), a delegated answer:
  refused, before `who_answered()`, with `--board-only` (`--delegate writes its own ledger half, never
  --board-only`) and on any action but `decide` (`--delegate is a decide's`, the CLI's usage error); after it,
  `delegate_problem()`'s message for the first rule that fails, before the item edit and the ledger half. The
  answer is then written in the delegated form, the delegate as the grant spells it, its ledger half by the
  decide lift in the delegated Log form. `add --decided` takes no `--delegate`;
- **the decide lift** (v2.4) — a `decide` on an item whose Context names one bare `TD-n` and one gate writes the
  board and the ledger (`--ledger <v2 directory>`, default `ledger/` beside the board when it is a directory) as one write, both
  or neither: the entries `decide_lift()` changes, from their texts as they stand, each listed id the ledger's
  `archive/` holds passed in `archived` (as its heading spells it), never as a text (v2.6) (its `People:` and
  `Answered by:` checks, and the ledger writer's refusal, *The ledger writer*), and the item file `edit_item(…, "decide", label,
  by, today, close=closes(item, label, entries after))`, moved when it closes — so a lifting answer closes the item when nothing listed
  still carries the gate, a waiting-only one closes it and logs `kept waiting`, and a work order leaves it open.
  The board's date is the local clock's and the ledger's the UTC clock's, unless `--today` gives both. Without a
  ledger it is refused. **`--board-only`** writes the board half alone, `closes()` reading the ledger as it
  stands: the `set by=` route, whose `set` has lifted the gate already, so nothing is lifted twice. A lifting
  answer writes the item only when it closes it; while a listed entry still carries the gate (a part of a
  shared item, or a Context entry nothing has lifted) it writes nothing, exit 0, and reports `left_open`, those ids
  as the item spells them, in its order (v2.7). The item stays open and unanswered, still asking the person for the
  entries left, and the person's answer is the Log's `; shared board item left open` line. In every mode, `--json`
  and `--plan` among them, it prints `left open: <ids> still carry <gate>` on stderr, and `--plan`'s JSON carries
  `left_open` beside its empty `changes`. Any other answer writes as without it.
  An item whose Context names another repo's entry (`<repo>#TD-n`) is answered on the board alone and stays
  decided but open, its lift being a tool PR in that repo (`--ledger` refused), after the same `People:` and
  `Answered by:` checks. An item whose Context names a gate but not one entry is answered on the board alone,
  closed per `closes()` (a waiting-only answer closes it). `--ledger` and `--board-only` on any item but a lift's
  are a refusal;
- **`fmt`** — `canonical_item_file()` of every open item file (each `*.md` file directly in the board's directory
  but `README.md`; archived files, other names and subdirectories untouched, and an `*.md` file whose name is no
  id reported as refused, its `id` the name less `.md`, why `not an item file name`): the files it rewrites, and
  each file it cannot, with why, reported and kept; exit 0 as today, a refused file included;
- **`split`** (v3.0) — a v2 board (`--board`, its archive `--archive`, default the board's name with
  `_archive.md` beside it, none if absent) split by `split_board()` into the directory beside it named the board's
  name without `.md`, which must not exist, the directory the stub then reads as: every file written, the v2 file
  replaced by `board_stub()` and its archive removed, as one write. It refuses, exit 1 and writing nothing, a
  board that does not exist, one of a major newer than 3, one already v3 (`already a v3 board`), a `--board` not
  ending `.md`, an `--archive` given that does not exist, what `split_board()` refuses, and an existing directory
  (`<dir>/ exists`). `split_board_notes()`'s lines are printed as warnings, `<path>:<line>: ⚠ <why>`, and, when
  `--archive` names another file and one of the default archive's name is beside the board, `<path>: ⚠ default
  archive left in place` (`warnings` in `--json`, each `{"path", "line", "text", "why"}`, the last with `line`
  null and `text` `""`, beside `files` and `removed`). It prints no subject;
- **`rank`** — `set_rank()` of the rank file (created when missing), `--set TD-n=<key>` and `--drop TD-n`,
  under `--action rank|join|prune`; or (v2.3) `--action respace --ledger <ledger> [--fixed <key>]… [--repo
  <name>]`, `respace()` of the rank file against that ledger (a file or a v2 directory), which sets and drops
  nothing itself.

A write to a v2 board is refused (*split first*); `list` and `show` read one (v3.0). A write needs a v3 board: a
missing board, a directory with no `README.md`, one whose `README.md` declares another major or none, and a v2
board are refused before anything is written, `<board>: not a v3 board: <why>`, the README's own `Ledgerboard:`
line read, never the stub's; a v2 board's reads `not a v3 board: a v2 board (split first: board.py split)`; `list` and `show` refuse only a missing board; `board.py` creates no board, and a
close whose archived file exists is refused (v3.0). `--id` is required by the five edits; `--hidden` is `show`'s;
`show` prints text only, so `--json` and `--plan` with it are usage errors (v3.0). Every action resolves a stub
as `load_board()` does: given the stub's path as `--board`, `add` and the five edits write into the directory
beside it (v3.0). `--board` is read as a normalised path, so a trailing `/` names the same board, and `ledger/`
beside it is the same directory (v3.0).

Each write prints the commit subject the module gives (`subject()` with `append` for an add, the edit's,
`queue_subject()`; a board write's names the item's `id`) and the paths it changed, or one JSON object with
`--json`. `fmt` has no subject of its own, and a write that changes nothing (a rank line already so, or a
`--board-only` answer left open) prints none, writing nothing; with `--json` its `subject` is null and its `paths`
empty. `--plan` prints the changes as JSON (each path and its new text, null for a file removed) and writes
nothing. Every write that names an item reports its `id`. A decide lift also reports `entries` (the ids whose
files it changed) and `notes`. A write of several files, and of the files it removes, is both or neither (v3.0:
`done` and a closing `decide` remove the item's open file as they write its archived one, and `split` removes the v2 archive): each is written to a
temporary file beside it and renamed into place only when all are built, then each removal made, and a failed
step puts back the files already replaced or removed. `fmt`'s JSON is `{"fixed": [<id>…], "refused": [{"id",
"why"}]}`, and without `--json` it prints `<id>: kept: <why>` on stderr for each file it keeps. A refused write's
gate faults read `<board>: <path>: <problem>`, `<path>` relative to the board's directory. The caller passes what
lies outside the files: the date (`--today`, else the local clock), who replies or answered (`--by`), and the
tool and session the subject names (`--tool`, `--session`). A file that declares a newer major is refused
unread. Exit (v2.4), the ledger writer's table: 0 written (or nothing to change), 1 refused, 2 usage (a bad
`--today` among it) or, for `decide` and `add --parts`, a ledger that cannot be used as asked,
4 a write failed (every file restored); it never exits 3, which is the ledger writer's `needs`.

From v2.4, a write that leaves an open item also reports that item's notes, as the write leaves it
(`item_notes()` at `--today`). The writes that do are `add`, `snooze`, `due`, `decide` and `reply`. With `--json`
or `--plan`, the notes are `item_notes`, `[{"id", "note"}]` (each names its item's id, where `item_record()`'s
`notes` is the record's own list of strings), always present and `[]` when there are none; a decide lift's
`notes` (above) is a different key and unchanged. Without either, each is printed on stderr as `<id>: ℹ <note>`.
A note never changes the exit code.

## The ledger writer (v2.4)

`ledger.py`, beside the module and `board.py` in the `ledgerboard/` package, is the ledger writer over files:
an importable library (`Ledger.open(path)`, then `plan_new`, `plan_edit`, `plan_archive`, `plan_reopen`,
`plan_renumber`, `plan_lift`, `plan_split`, `plan_relink`, `plan_fmt`, `plan_migrate_body` (v3.3), each returning a `Plan`, and
`apply(plan)`) and a command line (`python3 -m ledgerboard.ledger …`, a consumer's wrapper being the
command people run). It reads the files it is given, applies the module's edit, and writes the files back; it
never runs git, the network or anything of a consumer's. A report reads a v1 file or a v2 directory (*The
ledger as a directory*); a write takes a v2 directory, and a v1 file is refused (*split first*).
- **the reports**, read-only: `--pickable` (the pick order, the blocked entries and the flags), `--list` (every
  entry the filters keep: `--where FIELD=VALUE`, its aliases `--type`, `--owner`, `--kind`, and `--pickable
  yes|no`), `--counts FIELD[,FIELD]`, `--fields`, `--summary` (the table a v2 ledger does not store) and
  `--check`. `--check` prints `check()`'s flags, and exits 1 when an error stands; with `--base <ledger>` (the
  ledger where the change started) it counts only what changed since, as `check()`'s `old` does, and adds an
  error for an archived entry the base holds and the ledger has lost (`archive-loss`; one back in the ledger is
  `archive-reopened`, ℹ) and for each entry file that differs from the base's and is not in canonical form
  (`not-canonical`);
- **`new`** — one entry (`entry_text()`) at `<ledger>/TD-NNN.md`, its id `--id`'s, taken by the caller and written
  at three digits or more (`TD-3` as `TD-003`), refused when the ledger or its archive holds it. A flag per field
  (`--priority`, required, `--type`, `--added` (default today), `--owner`, `--kind`, `--status` (default `Open`),
  `--blocked-by`, `--part-of`, `--location` (the `**Location:**` body section, v2.7), `--field NAME=VALUE` for a
  repo's own (not `--field Location=…`, from v2.7: `--location`)), `--take` (the counter take's
  nonce, written as `Id take`), and `--why` (required), `--ask` (v3.1), `--fix` and `--done-when`, each from a
  file or `-` for stdin, at most one of them `-`, written in that order; an empty `--ask` is refused, and in a
  ledger whose `Fields:` declares `Ask` so is any `--ask` (the Ask is then `--field 'Ask=…'`). From v3.3 it also
  takes `--context FILE|-`, only with `--ask`, written as the `**Context:**` section right after the Ask. With `--by`, `--session` and `--words` (and optionally `--while`), all three or none, it writes the
  Log's `filed by` line and a `gate added` line per gate it is filed with;
- **`set`, `note`, `edit`** — one edit of an open entry, or for `note` (v2.8) of an archived one too
  (`edit_entry()`): `set TD-n` takes `new`'s field flags (an
  empty value removes the field; not a non-empty `--location` or `--field Location=…`, from v2.7: `edit
  --section Location`; an empty one still removes the header field) and (v2.8) `--title "<title>"`, the heading's
  title, where `--title ""` is a usage error. From v3.1 `set` also takes `--ask FILE|-` (`plan_edit(…, ask=)`):
  the words of the entry's `Ask` section, written (replacing it or adding it) after the fields, in the same
  write, so a decision and its Ask arrive together. An entry cannot take a decision before its Ask
  (`ask-missing`) nor an Ask before its decision (*Edits*, `decision-missing`), so for an entry with no Ask,
  `--ask` is the one-write way it comes to wait on a person (a ledger that declares `Ask` uses `--field 'Ask=…'`
  beside the gate instead). `--ask` is refused when the `Blocked by` the write leaves names no decision, when
  its words are empty, with nothing else to set, on an entry holding a header `Ask`, and in a ledger whose
  `Fields:` declares `Ask` (there the Ask is that field, set beside the gate). From v3.3 `set` also takes
  `--context FILE|-` (`plan_edit(…, context=)`), the entry's `**Context:**` section, written after the Ask in
  the same write, and refused when empty or when the entry has no Ask; `edit --section Context` adds a missing
  one right after the Ask, where the entry has one. `note TD-n "<words>"` appends a dated Log line, and `edit TD-n --section NAME
  --from FILE|-` replaces one section (or, v2.8, with `--remove` in place of `--from`, removes a misplaced
  one, or (v3.1) the `Ask` of an entry with no decision; the ledger's `Fields:` names are passed as `declared_fields`). `note` (v2.8) also takes an archived entry whose
  Status is in the closed set, writing its file where it is in `archive/`, and refuses one whose Status is not (*The
  closed Status set*'s cure); `set` and `edit` take an archived entry only once reopened. From v2.5 `set` and `edit`
  pass the day (`--today`, default the UTC date) to `edit_entry()`, which dates a gate `set` adds and an Event
  section `edit` makes a new `host-log` wait;
- **the `set` route's gates** — a `set` whose `--blocked-by` drops a `decision (<p>)` the entry carries lifts it
  (`lift_gate()`) and needs `--by <person>`: the gate's person, with `--answer` (default `Go`) and at most one of
  `--board <repo>`, `--no-board-item`, `--shared-item`; or anyone, with `--override "<why>"`. One that swaps one
  decision for another reassigns it (`reassign_gate()`), with `--by` and `--why`. Who may run either (a session a
  person started) is the caller's to check; the writer records `by`. These flags on a `set` that drops no
  decision are a usage error. With `--delegate <name> --scope <name>` (v3.4), the lift's Log line names the
  delegation (`lift_gate(delegate=, scope=)`); both or neither, only with `--by` and an explicit `--answer` on a
  lift, else a usage error. The writer reads no board: such a `set` is reviewed;
- **`lift TD-n --gate "<gate>" --by <who>`** — one gate lifted (`lift_gate()`, *Lifting a gate*), its inputs one
  shape exactly: a decision with `--answer` and at most one board flag (with `--people P,…` and `--answered-by
  any`, anyone listed may answer); an event with `--answer` and `--people`, or with a host's `--evidence`; `until`
  with neither. The override and the reassign are `set`'s;
- **`split`** — a v1 ledger file (`--ledger`, default `docs/technical_debt.md`, `--archive` beside it) split into its
  v2 directory (`split()`), `--to DIR` (default `ledger/` beside the file, which must not exist, under no file): every file
  written, the v1 file and its archive removed and the rank file moved to `rank.yml`, as one write. Each file's
  relative links are rewritten for where it now lives, and a link into the v1 files, in the new files and in
  `--also`'s, points at the entry's file (an entry heading's anchor, `#td-21-…`) or the directory (no anchor);
  any other anchor into them is left and listed (`warnings`). The module's refusals stand (an archive's
  `## Summary`, say: move it first);
- **`relink FILE…`** — the same rewrite of the given files' links into the v1 files, for a v2 ledger already split
  (`--was`, the v1 file, default `technical_debt.md` beside the directory), for files the split did not see;
- **`archive TD-n --why "<words>"`** — an open entry archived (`edit_entry()`'s archived form, `archive_plan()`
  first) and its file moved to `archive/`: Resolved (`--pr N`, `--pointer P`, `--as-is`), `--superseded-by ID`
  (`TD-n` or `<repo>#TD-n`, followed to the end of its chain; each entry Blocked by it rewired to the successor
  in the same write) or `--dropped` (refused while an entry is Blocked by it). Refused while an open entry is
  still Part of it;
- **`reopen TD-n --why "<words>"`** — an archived entry reopened (`edit_entry()`'s reopened form) and its file moved
  back into the ledger;
- **`renumber TD-n --id TD-m`** — an open entry given the id the caller took (`--take`, its nonce, written as `Id
  take`): its file and heading, every entry's Blocked by, Part of and Log `while` naming it, and its rank line.
  Refused for an archived entry, for `TD-0`, and for an id the ledger or its archive holds. The lines that still name the old
  id in prose, in the ledger and in `--also`'s files, are listed (`mentions`) for the caller to judge; prose is
  never rewritten.

  A move (`archive`, `reopen`, `renumber`) writes the entry's new file and removes its old one, as one write. The
  moved file's relative links (inline, `](path)` or `](<path>)` with any title, and reference definitions,
  `[ref]: path`) are rewritten to name the same paths from its new directory (`relink()`), its links to itself
  included, and every link to the file, in the ledger's other files and in `--also <file>…` (the caller's other
  files, which it found), is pointed at its new path. A URL, an absolute path, a plain anchor and a link in a code
  span or a fenced block are left (an indented code block is read as prose), and paths are compared as text: a
  link that named no file before names none after. `--why` is required and not empty;
- **`fmt [TD-n …]`** — each entry named, else every entry open and archived, in canonical form (`canonical()`);
  an entry it refuses is reported with why and left alone. `--check` lists what would change and writes nothing.
- **`migrate-body`** (v3.3) — every entry of the ledger and its archive rewritten so `check()` flags no
  `lead-form`, `glued-lead` or `field-lines`, keeping each section's text and order as v3.3 reads them: a lead
  with no colon gains one inside the bold (`**Done when** x` → `**Done when:** x`; a label's trailing `.` or `:` inside the
  bold, and one `:` after it, give way to the colon), a glued lead gains a blank line above it, and an `Ask` of more than
  one line keeps its first paragraph joined to one line and moves the rest, as written, under a
  `**Context:**` lead after it (an entry that already has a `Context` section is refused). A glued lead's and
  an Ask's rewrite each add one section boundary, on purpose; every other section reads back the same, or the
  entry is refused and kept, as is one with `fence-open` and an Ask whose first paragraph holds a list or a
  fence, an Ask whose lead's line is empty, or one `_entry_parts()` or `canonical()` refuses; the rest are
  written as one write. The guard compares (section key, text after the lead) with the v3.3 reading under the
  declared rewrites alone, on the raw body as the writers read it, a lead inside an HTML comment left as it is;
  a respelling that changes a lead's key to another section's key, a name this format reads or a header name is
  refused (an Ask's first paragraph ending only at a blank line outside comment spans; every refusal only on an
  entry with a fault or a declared transform, a clean entry being already migrated, except an entry
  `_entry_parts()` refuses, which is always refused), as is a comment inside a
  label's bold run, an Ask that must be joined and holds a comment, a code span
  or a line that is not plain text, and an entry with two Asks;
  the Context lead is written alone on its line, a blank line, then the rest byte for byte; only an entry with a
  declared rewrite is written or counted, in `canonical()` form. A label's respelling
  trims leading and trailing whitespace and one trailing `.` or `:` from the bold text, adds `:` inside it, and
  drops one `:` after it; a label with no name is refused. A second run changes nothing. Optional ids limit it to
  those entries. Leads are respelled first, then glued leads split, then the Ask; an indented or quoted Ask is refused, as is
  a respelling to a name this format reads that the label was not; the result is `canonical()`'s, and no
  `gate()` runs. `--plan` prints the plan as every write does; `refused` lists `{path, why}`; exit 1 when it
  refuses any, or with `--check` when it would change any, as `fmt`.

**A write is refused** when the ledger after it has a `check()` error the ledger before it does not, both checked
against one `old`: the ledger text of `--base`, else of the ledger as it stands. So a fault already there never
blocks an unrelated write. Every ℹ the write brings, and `cross-repo`, is a note it prints, never a refusal. What
the consumer judges beside it (the id against its counter, a wait written in prose, a blocker in a repo it read)
it judges on the `--plan`.

A ledger write prints the paths it changed, or one JSON object with `--json` (`subject` is null: a ledger edit has
no commit subject of its own, so the caller names its commit). `--plan` prints the changes as JSON (each path and
its new text, `null` for a file removed) and writes nothing. A write of several files is both or neither, as the board writer's is. The caller
passes what lies outside the files: the id, who filed the entry, the date (`--today`, else the UTC clock: every
ledger date is the UTC date) and the state of other repos' entries — in-process the `resolve` callback, on the
command line `--resolved <file>`, a JSON object from `<repo>#TD-n` to `{"state": "open" | "archived" |
"unresolved", "status", "successor", "why"}`. An id the run needs that the file does not hold stops it, whatever
else it would say: exit 3 with `needs: <ids>` (`--json`: `needs`), nothing written; the caller resolves them and
runs it again. A file that declares a newer major is refused unread. Exit: 0 written (or nothing to change;
`--check`: no error stands), 1 refused (`--check`: an error stands; `fmt`: an entry refused, or under `--check`
one would change), 2 usage, or the ledger or an id cannot be used as asked, 3 `needs`, 4 a write failed (every
file restored). The board writer exits by the same table (*The board writer*), so a code means one thing whichever
writer ran.

## Text a person reads (v3.2)

Text that waits on a person — a board item's question and its answers, an entry's Ask and Answers, a title — is
held to four rules by one check, which a writer runs before it writes (`person_text_problems()`,
`title_problems()`). The module reads only the text it is given: who may act in the caller's process (`actors`),
its coined words (`coined`), its label patterns (`labels`) and the board's people (`people`) are the caller's.
Each function returns a list of `PersonTextProblem(rule, refuse, line)`, empty when the text passes, in rule
order; `refuse` is true for rules 1 to 3 and false for rule 4; `line` is one line saying what failed and its
cure. An empty entry (after trimming, for `actors`), or one holding a line break (`\n` or `\r`), in `actors`, `people`, `coined` or `labels`, a `coined`
entry holding whitespace, or a `labels` entry that is no regular expression, raises `ValueError`. `people` may
be `None`, read as no names.

1. **One plain sentence**: not empty, at most `SENTENCE_WORDS` (25) words, no sentence end inside it, ending in
   `?` when it is a question (`sentence_problems(text, question=, max_words=)`, which reads these and nothing
   else); and no code token (`code_tokens()`). `person_text_problems` reads both and gives at most one rule-1
   problem; with `sentence` `None` it reads no rule 1.
2. **Every answer says who acts**: each answer, and `default`, names an actor.
3. **A title is plain words** (`title_problems(title, coined=, labels=)`): no code token and no label.
4. **The context is plain words**: its code tokens are named in one warning; never refused, never capped.

**The text read.** First, `’` and `‘` become `'`, and `“` and `”` become `"`. Then each fenced block — a fence as *Ledger entries and their edits*
reads one: an opening line of three or more backticks or tildes, indented at most three spaces, then any info
text, spaces included (after backticks, holding no backtick), as the module's fence line reads it; to a closing line of the same character at
least as long, indented at most three spaces and holding nothing else; or, with no closing line, to the text's
end — and each code span outside them — a run of n backticks,
then text holding no run of exactly n backticks and no blank line, then n backticks — is found and replaced, in
place, by a stand-in (a backtick with no partner is a plain character). A piece holding a stand-in is one word
that no pattern, `ACTOR_WORDS`, `actors`, `people`, `coined` or `labels` entry reads, so *`foo`'s* is one word
and *`a`/`b`* one word; each span or fence in it is a code token, spelled as the span is written or as `a code
block`. Then, outside them, a markdown link's target (`](…)`, the `]` kept) and a bare
URL are dropped; a bare URL is `https?://\S*` up to and not including a run of `. , ; : ! ? ) ] } " ' * _`
that ends its piece, so *see https://x.io/guide?* keeps its `?`. The rest is read as whitespace-separated pieces; each is
stripped of leading `( [ { " ' * _` and trailing `. , ; : ! ? ) ] } " ' * _`, then of an ending `'s`, and a piece holding no letter or
digit after the strip (`—`, `-`, `&`, `/`, `~/`) is no word; a letter and a digit are Python's (`str.isalnum()`
of a character), and a pattern's classes are as written. A pattern below matches the whole stripped word unless
it says *holds*; each is case-sensitive unless it says otherwise. Rules 1, 2 and 3 read these words, so an actor
or a label inside a span, a fence, a link's target or a URL is not read.

**A code token** (`code_tokens(text)`: in the order of their place in the text, each distinct token once): a
code span, spelled as written with its backticks; a fenced block, spelled `a code block`; and a word that is
one of these, spelled as the stripped word unless it says otherwise —
- a *path*: opens `/`, `~/`, `./` or `../`; or splits on `/` into three parts or more of which one holds a
  letter, or into two whose last is a file name; or holds a `\` between two word characters;
- a *file name*: `[\w.-]*\w\.(<ext>)(:\d+)?`, case ignored, `<ext>` one of `CODE_EXTS` (*foo.py:42* is one);
- a *call*: a piece that, before the strip, holds `[A-Za-z_][\w.]*\(` whose `(` is not followed by `s)` or
  `es)`, spelled as the name before the `(` and `()` (`one_sentence(x)` gives `one_sentence()`; `file(s)` is no
  call);
- a *snake_case name* `[a-z][a-z0-9]*(_[a-z0-9]+)+`; a *dotted name* `[a-z_][a-z0-9_]*(\.[a-z_][a-z0-9_]*){2,}`,
  case ignored; an *upper-case name* `[A-Z][A-Z0-9]*(_[A-Z0-9]+)+`; a *camelCase name* `[a-z]+[A-Z]\w*`;
- a *range*: holds `..` between two word characters;
- a *commit*: 7 to 40 characters of `[0-9a-f]`, holding both a digit and a letter;
- an *option*: opens `--` and a letter.

A word that is more than one kind is one token. An id (`TD-1845`, `#3878`, `F12`) and a version (`v2.7.1`,
whose parts open with digits) are no code token. Known false positives: *yes/no/maybe*, *he/she/they*, *A/B/C*,
*US/EU/UK*, *and/or/else*, *Mon/Wed/Fri* (paths); *a(n)* (a call); *Node.js* (a file name); *docs.github.com*, *U.S.A*, *a.b.c* (dotted); *iPhone*, *iOS*, *macOS*
(camelCase); a word written with `_` on purpose. Known gaps: a command written as words (*git rebase*), and a
name whose `_`s the strip removes (`__init__` reads as *init*); a two-part path with no file name
(*docs/plans*); a variable (`$HOME`), a short option (`-f`), a bare `{"a":1}` and a file with no extension
(*Makefile*); a path with a line number and no file name (*src/lib:42*), a file name with more than one line number or a
range (*foo.py:42:7*, *foo.py:42-50*), a dotfile (*.gitignore*), an extension outside
`CODE_EXTS` (*Foo.java*), a two-part member (*UserService.getName*), a PascalCase name
(*NullPointerException*), a host and port (*localhost:8080*), an assignment (*DEBUG=1*), an address
(*dev@example.com*) and a two-part host (*example.com*, where *www.example.com* is dotted).

**One sentence** (rule 1). The sentence is empty when it holds no word; an empty sentence fails with that
alone, its length and end unread. It has more than `max_words` words when
its words, a span or fence counting as one, number more. It has a sentence end inside it when a `.`, `?` or `!`,
then any of `) ] } " ' * _`, then a space or a line break, stands before its last word, but not a `.` ending a word
that is, case ignored, an abbreviation — *e.g*, *i.e*, *vs*, *etc*, *cf*, *mr*, *mrs*, *ms*, *dr*, *jr*, *sr*,
*st*, *no*, *approx*, *est*, *a.m*, *p.m*, or a month's (*jan*, *feb*, *mar*, *apr*, *jun*, *jul*, *aug*, *sep*,
*sept*, *oct*, *nov*, *dec*) — and not an ellipsis (`...` or `…`) (so *Say (really?) what you think?* has one inside).
Its end is the read text's last character that is not whitespace or one of `) ] } " ' * _` (*_Is it ok?_*
ends in `?`): a question's must be
`?` (*Should I run `make test`?* and *Should I "ship it?"* end in `?`); a statement's end is not read. Known false positive: another abbreviation or an id followed by a stop and a
space (*U.S. law*, *Ph.D. thesis*, *TD-909. Which*), which the line's part names: *write it without the stop*.
Known gap: *no* is an abbreviation (*No. 5*), so *Say no. Then what?* passes.

**An actor** (rule 2): a match, over the read words joined by single spaces, in the bounds `(?<![\w'/-])` before and `(?![\w'/-]|\.\w)` after (so *us-east-1*, *I/O* and *my-app*
name no actor), of an I-form (*I,
I'll, I'm, I've, I'd*, case-sensitive); of a word of `ACTOR_WORDS` (case ignored); of an entry of `actors`, a
word or a phrase taken as literal text, trimmed and its whitespace collapsed to single spaces (an entry empty after that is a
`ValueError`), its last word optionally followed by `'s` or `s` (case ignored); or of a
name in `people`, literal, optionally followed by `'s` (case ignored, as SPEC compares a person's name, so a person named *Will* makes *it will be built* name an
actor: a known gap). An answer is read through
`split_answer()`: its label and its consequence, the ` (default)` mark dropped; an answer whose label is a form
(`is_form()`: `Hold: <note>`, `Not right: <what>`, `Other:`) is read by its consequence alone, and any other by its label
and consequence. `default` is read as an answer is, and skipped when its label, after `split_answer()`, equals an
answer's label, or its text with the mark dropped equals an answer's with the mark dropped. Known gaps: the check sees words, not meaning (*you will not hear of it
again* passes), *US* (*the US market*) reads as *us*, and *me/you* or *you-or-me* names no
actor (the bounds); a caller's `actors` bring their own (a noun *lead*
matches *lead* in *take the lead*).

**A label** (rule 3): a word matching `(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+#TD-\d+|TD-\d+` (the format's
`<repo>#TD-n` and `TD-n`), a word matching any of `labels` (each compiled
on its own by Python's `re`, case-sensitive unless the pattern says otherwise, and `fullmatch`ed against the
stripped word, its `'s` already gone, so *TD-5's* is a label), or a word of `coined` (each entry one word,
refused with `ValueError` if it holds whitespace), case ignored, with `s` or `es` after it or not.

**The lines**, one per problem, rule 1's first, then rule 2's in the answers' order with the default last, then
rule 4's (`title_problems` gives rule 3's alone). A `<list>` names each distinct item once, up to three, in the order found: `a`,
`a and b`, `a, b and c`, and from four `a, b, c and <k> more`. `<i>` counts the answers from 1.
- rule 1: `rule 1: the question is one plain sentence of at most <n> words ending in ?: <parts>` for a question,
  `rule 1: the sentence is one plain sentence of at most <n> words: <parts>` for a statement; `<parts>` every
  failure, in this order, joined with `; `: `it is empty`, `this has <m> words`, `this has a sentence end inside
  it (write it without the stop)`, `this does not end in ?`, and `the code token <list>` (`the code tokens
  <list>` for two or more). `sentence_problems` writes the same line without the code part. Example: *rule 1:
  the question is one plain sentence of at most 25 words ending in ?: this has 26 words; this does not end in ?;
  the code tokens profiles.yml and one_sentence()*.
- rule 2: `rule 2: answer <i> names nobody who acts — say who: I'll…, you…`, then `, or <a>…` when `actors` is
  not empty (`<a>` its first entry as given); `the default` in place of `answer <i>`. Example: *rule 2: answer 1
  names nobody who acts — say who: I'll…, you…, or session…*.
- rule 3: `rule 3: a title is plain words: <list> belong in the body`, the code tokens and labels in their
  order in the title. Example: *rule 3: a title is plain words: TD-078, B4 and profiles.yml belong in the body*.
- rule 4: `rule 4: the person reads the context in plain words: <list> go behind the link`. Example: *rule 4:
  the person reads the context in plain words: grammar.py, one_sentence(), profiles.yml and 2 more go behind
  the link*.

**The fixtures decide** (`fixtures/person_text/`), as everywhere in this text: where this prose and the module
disagree on a word, the fixtures say which is right, and a false positive or gap found later is a fixture case
first.

**Which writes a writer checks.** The rules reach text a writer writes for a person, never the writers' `plan_*`
functions or the module's edits (`item_file()`, `edit_entry()`), which sweeps and migrations also call, and never
a file already written. A writer refuses the write when any problem's `refuse` is true, naming every problem,
and writes with rule 4's line shown. `people` is the board's `People:` (`board_people()`) for a board
item (`None`, a board with no such line, reads as no names), and the caller's for a ledger entry. It runs:
- **a `decide` item**, two calls. The item's text is the text the writer is given for it (`item_file()`'s
  `text`, collapsed and trimmed as `item_file()` does, before any line or file is written). Its **lead** is
  `bold_head(text, heading=True)` (*The bold head*, read whole as an item file's heading is) when
  `BOLD_RE.match(text)` succeeds and that is not `None` (a blank run gives none); its **tail** is the text after
  the matched run, trimmed. Otherwise it has no lead and no tail, and a text with no lead whose first bold run
  is not blank (`bold_head(text, heading=True)` is not `None`) is the writer's refusal, with the line *a bold run
  that does not open the text becomes the board's headline: open the text with it, or write it plain* (a
  writer's refusal, not a `PersonTextProblem`), since the board would show that run as the headline. A text of more than one line, or an empty one,
  is the writer's refusal before the check, as `item_file()`'s. Each of these writer's refusals (the bold-run line,
  and an `act`'s lead line below) comes before the check and stands alone: the writer gives that line and runs
  neither call, so the session rewrites the text's shape first. The lead is the board's headline,
  so it must stand as the question by itself; reading the lead and tail as one sentence was weighed and
  rejected, since a person scanning headlines would meet *Merge the PR* with no question in it. First,
  `person_text_problems(<lead, else the whole text>, <its answers>, <context>, question=True, people=, actors=,
  default=)`, the context being the tail, then the detail block's parts `context`, `caveats` and `recommended`
  and its `otherwise` text, as the writer is given them (the `recommended` before the writer adds the default's
  label and ` — `), joined by blank lines in that order; never the item's `Context:` field, which names a gate.
  A text with no lead and no non-blank first bold run (a blank first run reads as none, *The bold head*) is read whole, so a second sentence there is refused and belongs in the detail block; a
  lead is the whole question, so *\*\*Merge the PR\*\* now?* is refused (its lead has no `?`). Second, the
  detail block's `question`, `person_text_problems(<question>, question=True, people=, actors=)` with the same
  `people` and `actors`. The writer lists the first call's problems, then the second's, each line after the
  name of the text it came from (`item: `, or `item (the bold part): ` when a lead was split off; `detail question: `; a rule-4 line after
  `context: `), so a session
  sees which to rewrite.
- **an `act` item**: as a `decide`'s first call with no answers and `question=False`, its lead the sentence and its tail context. An
  `act` whose text opens with no lead is refused by the writer, with the line *an act item leads with its task in
  bold* (a writer's refusal, not a `PersonTextProblem`; for an `act` this line is the one given, not the
  `decide`'s bold-run line). Example: *Reply to \*\*Dana\*\* about the budget* has
  no lead and is refused; *Should I merge \*\*#42\*\*?*, a `decide`, has no lead and is refused for its bold
  run, and *Should I merge #42?* is read whole. An `act`'s detail `question`, where it has one, is read by the
  `decide`'s second call (`question=True`, the same `people` and `actors`), its lines after `detail question: `.
- **a `look`, `watch` or `fyi` item, or one with no kind**: not checked (the source checks a `decide` and an
  `act` alone).

  A detail block part whose value is a list is read as its first string and its nested bullets' strings, one per
  line.
- **an entry's Ask**, on any write of it (`new`, `edit --section Ask`, and `set --ask` where the writer has it):
  the Ask's line after its `**Ask:**` lead, the sentence, `question=True`, and the entry's `**Context:**`
  section, where it has one, the context (v3.3: an Ask is a data field, *The entry*; until v4.0 an Ask's first
  paragraph is still the sentence, joined, and its later paragraphs still its context, flagged `field-lines`; an
  entry with both a `**Context:**` section and later Ask paragraphs has the `**Context:**` section as its context). An entry's answers (*An entry's own answers*, v3.3) are passed with it, `entry_answers()`'s `answers`, else a
  repo's own `Answers` field, read as a board's `Answers:` value (`parse_answers_value()`), and none where
  `entry_answers()` refuses them (`check()` names that fault); a write of the entry's `**Answers:**` section
  alone runs rule 2 over its answers with no sentence (`sentence=None`);
- **an entry's title**, on `new` and `set --title`: `title_problems()`; never on `renumber`, `archive` or
  `reopen`, which carry a title already written.
This package's own command lines do not run it: the writer that holds the caller's vocabulary does.

## Versions

A ledger or board may declare its major version on a preamble line, `Ledgerboard: 1`; none means 1 for a ledger,
and 2 for a board file (v3.0: a board's v1 and v2 are one format).
A v2 ledger declares it in its `README.md`, which `load()` puts first.
A v3 board declares it in its `README.md`, on any line outside an HTML comment (`board_major()`); a README that
declares none reads as 3, and is named (*Reading a board*).
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
v2.4 also reads an archived blocker's Status (*Superseded and dropped*): a blocker archived `Superseded`
releases its dependents only when its chain ends in a Resolved entry, and one archived `Dropped` or with a
Status word v2.4 does not know keeps them blocked, where v2.3 released every one; `check()` gains
`blocker-superseded`, `blocker-dropped`, `blocker-unknown-status`, `cross-superseded`, `cross-dropped` and
`cross-unknown-status`, and a resolver's answer may carry `status` and `successor`. `archive_plan()` and
`dependents()` are new; `edit_entry`'s `archive` writes `Dropped` and a successor in another repo, and
`rename_ref` keeps one copy of an id. A v2.3 reader releases what v2.4 keeps blocked, so a consumer archives
an entry Superseded or Dropped only once every reader of its ledger runs v2.4. A later minor may add a Status
word, done or not, and v2.4 holds the dependents of an entry archived with it until it is read by a release
that knows the word. A consumer writes such a word only once every reader of its ledger runs v2.4 or later,
since v2.3 releases on any word. An archived Status that opens with prose holds its dependents under v2.4
where v2.3 released them, and `check()` names each. On an entry an edit changes, `blocker-unknown-status` is
an error.
v2.4 also defines the counter (*The next id*): `ids_held()`, `next_id()`, `parse_take()` and `judge_takes()` are
new; nothing a reader reads changes.
v2.4 also lifts gates (*Lifting a gate*, *The board*): `lift_gate()`, `reassign_gate()`, `reassigns()`,
`decide_lift()`, `closes()`, `waiting_only()`, `parse_closed_items()`, `answered_by()` and
`answered_by_problems()` are new, `edit_line`'s `decide` takes `close`, and `check()` gains
`gate-reassigned-often`. One verdict changes: `item_problem()` faults a `Lifts:` naming a waiting-only answer,
which v2.3 passed, and `item_line()` refuses one. A v2.3 reader reads an `Answered by:` line as a preamble line it
keeps, and a closed item as before.
v2.4 also decides the gate sweep (*The board*, *The gate sweep*): `covers()` and `sweep()` are new; nothing a reader
reads changes.
v2.4 also gives the merge gate its verdicts (*The merge gate's verdicts*): `tripwire()`, `lift_pr_verdict()`,
`uncovered_decisions()` and `migrate_subject()` are new, with the tree paths they read. `subject_kind()` names the
migrate commit's subject `migrate`, where v2.3 named it nothing; nothing else a reader reads changes.
v2.4's board writer writes the decide lift (*The board writer*): `decide` on an item naming one entry and one gate
writes the ledger too and closes the item per `closes()`, where v2.3's wrote the board alone and closed nothing;
`--board-only` keeps the board half alone. v2.4 also ships the ledger writer, `ledger.py` (*The ledger writer*): its reports, `new`, `set`, `note`, `edit`,
`fmt`, `archive`, `reopen`, `renumber`, `lift`, `split` and `relink`, and `set`'s gate routes; nothing a reader
reads changes. The board writer's write of several files
also removes files, both or neither, for the ledger writer's moves; no board action removes one.
v2.4's board writer exits by the ledger writer's table (*The board writer*): a refusal is 1 where v2.3 gave 3, a
failed write 4 where v2.3 gave 1, and a bad `--today`, and a `decide` whose ledger cannot be used as asked, exit 2;
it no longer exits 3. A consumer's wrapper
that read v2.3's codes checks them in its v2.4 vendor PR.
**v2.4 changes what `split()` writes** (*The ledger as a directory*): a `## Summary` section's blank lines are kept
and the `---` pair its table's removal leaves empty becomes one, so a v1 ledger split by v2.4 gets a different
`README.md` from one split by v2.3; a README already written is not touched, and every v2 file reads as before.
`split_notes()` is new.

**v2.4 adds notes on a hide** (*The board*, *The board writer*): `item_notes()` is new, `item_record()` gains
`notes`, and `board.py`'s writes that leave an open line report them. Nothing is read differently: every line reads
and keys as in v2.3, and a v2.3 reader of `item_record()` by key ignores the new one.

**v2.5 stamps the fixtures with their release:** `fixtures/MANIFEST` names the release and lists the sha256 of
every other file in the set, so a copy of the set proves which release it is, as each package file's first
line does, and an implementation of release `x.y` runs the set stamped `x.y`. Its first line is `# ledgerboard
v<x.y> fixtures`. Each later line is `<sha256>  <path>` (64 lower-case hex digits and two spaces, as
`sha256sum` writes), one per regular file under `fixtures/` but the manifest itself and any file under a
`__pycache__` directory, the path relative to `fixtures/` with `/` between its parts, the lines sorted by the
paths' UTF-8 bytes, every line ending in LF. The hash is of the file's bytes as stored. A case names no
release of its own: the set's release is the one whose module wrote every expected output in it. A release
stamps the manifest when it stamps the package; between releases it is left as it is, and only a release's is
checked (`fixtures/run.py --check-header`). A set from before v2.5 carries no manifest (v2.4 was tagged before the manifest landed); its release is its
tag's. Nothing a reader reads changes.

**v2.5 adds the `host-log` check** (*Events*) **and *Host-log checks***: `CHECK_TYPES` gains it, `parse_check()`
reads it, `gate_added()` is new, `check()` gains `event-undated`, and the module gains `first_instant` and
`count_host_log`; the reader, and its configuration, are agent-cadence's `hostlog.py`. `set` now takes `today` and
logs `gate added` for each gate it adds, and **refuses a `set` that adds a gate without `today`**, which v2.4
accepted; `edit` takes `today` too, dates a changed `host-log` check with a `gate added` line, and refuses that
case without it: a consumer's caller of `edit_entry(…, "set" | "edit", …)` that can add a gate or change a check
passes `today` in its vendor PR (`ledger.py set` and `edit` do). A `set` or `edit` that dates no gate is
unchanged, with no `today` or a valid one. The unknown-type message now lists `host-log`. An older reader reads
a `host-log` check as an unknown type (`event-check`, an error on an edit), and its gate still holds, so a
consumer writes one only once every reader and host of its ledger runs v2.5, and once a host that declares its
repo sweeps it: a gate no host answers waits silently. v2.4 reads the new Log lines as it reads `new`'s.

**v2.5 fixes v2.4's `check()` raising** (TD-049) `Refused` on an entry with a `decision` gate whose header block
the edits refuse (a field below it, a repeated field, a line that is not a field): `check()` reads on, as it
does for every entry `entries()` reads, and a field below the header block keeps its ℹ `below-header`.

**v2.6 answers a parent's item whose part was archived** (*The decide lift*): `decide_lift()` gains
`archived=()`, and `board.py decide` and `lift_pr_verdict()` pass the archive's ids in it, so such a part is
skipped and logged where v2.4 refused the answer (the writer) or judged the part by its Status (the verdict). A
caller that passes no `archived` gets v2.4's result.

**v2.6 gives `Parts:` its writer** (*Edits*, *The board writer*): `item_line(parts=)`, `parts_problems()` and
`board.py add --parts`. Nothing read changes:
v2.3, v2.4 and v2.5 read every line it writes, and no key moves.

**v2.7 makes a new `Waits` line an error** (*Retired words*): `check()` with the ledger before an edit grades
the retired field ⚠ on an entry whose `Waits` line the edit added or changed, where v2.4 to v2.6 noted it ℹ.
Nothing read changes, and a ledger whose `Waits` lines no edit touches checks as before.

**v2.7 stops the sweep re-asking a lifting answer closed with no lift** (*The gate sweep*): within `reask_days`,
once per answer, an `act` says the lift is owed, in place of `Go | Not yet`, and closes once nothing is owed. A
gate lifted and re-added (its Log says so) is asked at once, as before.

**v2.7 closes the Status set and ships `migrate`** (*The closed Status set*; *Migrating to v2.7*, removed in v3.0): a Status
outside `Open`, `Resolved D`, `Superseded D by <id>` and `Dropped D`, or in the wrong place, is an error on every
entry of a v2 ledger, where v2.4 to v2.6 noted a retired open word ℹ and read the rest; `migrate_entry()` and
`ledger.py migrate` map the old forms. The header order loses `Waits` and `Location`, a header `Location` is
retired, and `new` writes `Location` in the body. A v2.6 reader reads every entry v2.7 writes (the four forms
were already its own; a body `**Location:**` was already a section), though its `canonical()` would place a
`Waits` or a header `Location` back in its own order, so a consumer vendors v2.7 before it formats a ledger v2.7
wrote. A repo takes v2.7 in one PR that vendors it and runs `migrate`. `migrate` stays through v2.x and goes in
v3.0, whose precondition is that, with the last v2.x, `migrate --plan` shows no entry with changes or stops in every
ledger whose repo vendors v3.0 when it is cut (v2.8: its rules cover every old form, open and archived). A ledger whose
repo stays on an older v2.x is untouched by v3.0 until that repo vendors it.

**v2.7 leaves a shared item unanswered by a lift of one part** (*The board writer*, *The merge gate's
verdicts*): `board.py decide --board-only` writes nothing while a listed entry still carries the gate, where
v2.4 to v2.6 wrote a `Decided:` that spoke for entries the person had not answered, and `tripwire()` flags such
a `Decided:` (`tripwire-shared-decided`), a diff v2.4 to v2.6 passed. No parse changes: v2.3 to v2.6 read every
line it writes, and no key moves. An item an older writer decided reads as before, a `decided` work order; the
consumer closes it and asks again for the entries left.

**v2.7 refuses a doubled Recommended label and names a refused field** (*Edits*, *The board writer*): on a `decide` with a
default, a `recommended` whose words already open with that default's label and ` — ` (compared ignoring case) is refused, naming the
prefix, where v2.6 wrote the label twice (TD-069). The refusal of item text, a reply or an answer carrying a field's name now
names the field it matched (`… carries a field's name (Context:) …`), where v2.6 listed every field (TD-057); a
caller that matched the old message text reads the new one. No parse changes and no key moves.

**v2.8 gives the title its writer** (*Ledger entries and their edits*): `set` takes `title` and logs `retitled:
was "<old title>"`, `edit` refuses to add a section that belongs in the header and removes a misplaced one,
`set` and `new` refuse a `Title` or `Log` field, and `check()` notes `misplaced-name` (ℹ). It reads one thing
differently: `retitled:` joins the reserved prefixes, so a note an older `note` wrote with that prefix now reads
as a malformed line (`log-line`). No key moves, and an older reader reads the new line as a note.

**v2.8 adds `Doer:`** (*The board*, *Edits*, *The board writer*): an act's doer, `parse_doer()`, `BoardItem.doer`,
`item_record()`'s `doer`, `item_line(doer=)` and `board.py add --doer`. It reads one thing differently: a
`Context:`, and a `Parts:`, now end at a ` Doer:`, so a line that held those words in its Context before v2.8
reads a shorter Context and fewer refs, and where the words after it read as a doer, a `doer` no writer meant,
which `item_problem()` cannot tell from a v2.8 one: a consumer's v2.8 vendor PR shows that none of its boards holds
such a line. No key moves. `item_problem()` now faults a `Doer:` in an item's text, one whose value does not read,
and one on any kind but `act`; `board_problems()` judges only a line it adds, so no board has a
flag day. `item_line()` now refuses a text, context, answer, detail value or `--said` holding `Doer:`, and the
`reply` edit a reply's words holding it, which v2.7 wrote; `decided_line()` cuts the name from a title and from an
answer option, and refuses a decision's words that hold it. v2.7 reads a `Doer:` as part of the Context, so a
consumer writes one only once every reader of its board runs v2.8.

**v2.8 reads any `<head>:` or `<head>: <…>` answer as a form** (*The board*, the `Answers:` bullet): where only a
look's `Not right: <what>` was one, now every such label is, its head in any case, and an answer that fills a
form listed in `Lifts:` lifts. One thing is read differently on lines already written: a `Decided:` filling a
form its item's `Lifts:` lists now lifts, so `closes()` and the gate sweep may close the item or lift its gate,
where it read as a work order; and `not right: …` in lower case, or `Not right : …` with a space before its colon,
is the look's form; and `fill_not_right()` writes one space after the colon (`Not right:grey` is returned
`Not right: grey`), and a PR writing a `Decided:` that holds an unfilled form goes to review
(`lift_pr_verdict()`). No key moves and the canonical form is unchanged. Two new faults, on open `decide` items
with no `Decided:`: two forms with one head, and a form marked ` (default)`. The writers gain refusals: `decide`
refuses a form unfilled (`Not right: <what>` included, which it wrote before) and writes a fill with the head as
offered; `item_line()` refuses two forms with one head and `default` naming a form, and `fmt` (`canonical_item()`)
names the two faults on such a line. A board with no form in a `Lifts:` reads as before. A consumer writes a fill
only once every reader of its board runs v2.8: an older reader reads a fill as a work order and never lifts or
closes it.

**v2.8 gives an archived entry a note** (*The ledger writer*): `ledger.py note` writes an archived entry whose
Status is in the closed set in place, where v2.7 refused it, and refuses one whose Status is not (*run migrate
first*). Nothing read changes, and no key moves.

**v2.8 gives `migrate` the last old forms** (*Migrating to v2.7*, rules 5–8, removed in v3.0): it maps `Taken by`, `Waits`, a
header `Resolved` and the old decision form, which v2.7's left. Nothing read changes: every line it writes is one
v2.7 reads (a body section, a plain Log line, a `decision (<who>)`), and no key moves. One thing is read
differently once a repo runs it: an old-form decision becomes `decision (<who>)`, which the gate sweep and
`gate_age()` read as a gate, where they passed the old form over. `uncovered_decisions()` counts an old-form
holder in the base as a decision already carried, so the rewrite is not a gained decision. A repo that ran
v2.7's `migrate` runs v2.8's once more, as its own PR.

**v3.0 reads a board as a `Board`** (*Reading a board*): `load_board()` reads a v2 board file and its archive,
or a v3 directory, and the board's readers take what it gives. A board that declares `Ledgerboard: 3` is
readable: `BOARD_MAJOR` is 3, and `version_problem(board)` names only a newer major. A v2 board reads differently
from v2.x in six ways. An open line whose closed twin is in the archive is one closed item, where v2.x read the
two as two items, and twins match by id, so the indent no longer tells them apart. An item's `refs` are read
from its Context without its replies, so a ref named only in a reply's words is none of the item's. A record's
`text` is the item's words (`item_words()`: the line less its prefix, its fields and its replies), not the line
after its tick. The sweep reads its head phrase (`has no board` and the rest) in the item's words alone, so one
only in a Context or a reply no longer counts. A line with no readable date has no id (`null` in a record): it is
matched, for the twin rule, only with the other undated lines, by its key, and the sweep never closes it. A
closed line's `raw`, `closed`, `fields`, `words` and `context` are read from the `- [x]` line as written, its
`Closed:` among them.

**v3.0 makes the board a directory** (*The board as a directory*, *Edits*, *The board writer*, *The merge gate's
verdicts*): one file per item, named by its id, in `docs/user_attention/` with `README.md` and
`archive/<YYYY-MM>/`, closing an item moving its file. **It reads a v2 board**: `load_board()` gives the same
items for a v2 file and its archive as for its split, for any board the split accepts, each v2 item with the id
`split_board()` gives it, so a consumer vendors v3.0 in or before the change that splits its board, and reads other
repos' boards in either major. It reads a v2 board as the paragraph above says, and a board file that declares no
major reads as 2, the format a board's v1 and v2 share (*Versions*' "none means 1" stays the ledger's). **It
writes v3 only**: `board.py`'s writes refuse a v2 board (*split first*). **What goes:** the item key as what an
item is (`item_key()` remains, only to read a v2 line and as `key_id()`'s input); the open-and-closed twin as the
merge rule (a v3 item is one file; a v2 board's twins are still read as one item, above); `archive_closed()`,
`archive_subject()`, `ARCHIVE_AT` and `board.py archive` with its `--archive` (which only `split` takes now), and
`closed_items()` as a public name; the v2 line's writers, `item_line()`, `decided_line()`, `edit_line()`,
`item_problem()` and `canonical_item()`, and with them the refusal of a field's name in a text, context, answer,
detail value or reply and of an answer ending `(by …)`; the text forms of the board's readers; `subject()`'s form
with no id; `add --under`; and the edits' `--line` and `--expect`. **What a caller changes:** `BoardItem.text` is
gone (an item's words are `words`, its replies `replies`); `needs_you()`, `covers()`, `sweep()`,
`board_problems()`, `board_people()`, `answered_by()`, `people_problems()` and `answered_by_problems()` take a
`Board` and no text, the sweep's board and `uncovered_decisions()`'s are `(origin_url, basename, board)`, read
whole, and the sweep's `to_close` are ids; `board.py`'s edits name an item by `--id`, and a write's JSON and `list`
give its id where they gave its line; `item_record()` loses `line`, gains `id`, `path`, `added`, `context` and
`closed`, and its `text` is the item's words (its `doer`, v2.8's, is unchanged); `version_problem()` takes a
`Board`, or a ledger's text (above; the ledger's `FORMAT_MAJOR` is not changed here); `parts_problems()`,
`decide_lift()` and `closes()` take an item file's text, and `parts_problems()` prefixes a shared check's fault
`item:` where it wrote `line:`; `BOARD_PATH` and `BOARD_ARCHIVE_PATH` are `BOARD_V2_PATH` and
`BOARD_V2_ARCHIVE_PATH`, beside `BOARD_DIR`; a subject carries the id; an `ls` lists subdirectories, so a caller's
`ls` that lists files alone reads a v3 board's archive as empty; and `lift_pr_verdict()` sends a lift on a v2 board
to review. **The board's order** for ties is a v2 board's line order and a v3 board's ids descending, newest first
(by `Added` date, at random within one day), so tied items can change order when a board is split. **`Doer`** is a
header field of the item file on an `act`, naming who should do its step (*The item file*), which `add --doer`
writes. The split carries every field the v2 reader reads into the header field of the same name. v2.4's "no board
action removes one" no longer holds: `done`, a closing `decide` and `split` remove files. A v2.x module meets a v3
repo as the stub, which declares `Ledgerboard: 3`: a reader that calls `version_problem()` refuses it, a writer
refuses it unread, and a reader that checks nothing reads an empty board, so a repo splits its board in the change
that makes its own tooling v3.0, and the repos that read each other's boards move to v3.0 together: until another
such repo moves, its v2.x readers that check nothing read the split board as empty (a sweep there can file a
duplicate item, closed by hand). Within v3.x the same holds for a field: a later minor's field is faulted by an
older v3 gate, so **a consumer writes a new field only once every reader of the board runs that release**.
`Ledgerboard: 3` on a ledger means nothing new here; the ledger's v3.0 changes are its own paragraph (TD-078).

**v3.0's ledger** reads no old form (*Retired words*): `Waits`, `Taken by`, a header `Resolved` and a header
`Location` are retired errors on every entry, open or archived; the old decision form is an unreadable item;
`parse_gates()`'s record loses `old_form`, and `parse_blocked()` names no holder for it (its pieces are in the
third list); `judge_takes()` loses `accept_taken_by`; `canonical()` places no
`Taken by`; and `migrate`, `migrate_entry()` and `migrate_subject()` are gone, while `subject_kind()` still names a
migrate subject; and `uncovered_decisions()` counts no old-form holder in the base (`tripwire()` never read one),
so an old form rewritten `decision (<who>)` is a gained decision, owed a covering board item. A v2 ledger that met the precondition (*v2.8*, above) reads exactly as under v2.8, and declares
no new major. One that did not is not misread: each old form is an error that names it (a retired field ℹ on a
v1 ledger, *Retired words*; the old decision form an error there on an open entry, as an unreadable item, and ℹ on an
archived one).

**v3.1 adds `decision-missing`** (*The ledger*, `Blocked by`): `check()` flags an open entry with an Ask and no
decision whose Log does not show it answered — an error on an entry the edit changed, ℹ on a standing ledger — so
the ledger writer refuses a write that makes one. With it, `edit` and `set` refuse to write an Ask on an entry with
no decision (*Edits*), `edit`'s `remove` takes such an entry's `Ask` section, and the ledger writer's `set` and
`new` take `--ask`, which writes a decision and its Ask in one write. It reads every file v3.0 wrote, as v3.0 did:
no field, Log line or key is new, and the canonical form is unchanged. **What it refuses that v3.0 wrote:** an Ask
written to an entry with no decision, so a caller that wrote an Ask and then its gate, as two writes, writes both
with `set --ask`; and `edit_entry()` raises `Refused` for such an Ask. A ledger v3.0 checked clean can show
`decision-missing` ℹ on entries it already held. A write over one is not refused, except a `renumber` or a
`reopen` of that entry, whose flag is then new; `check()` given a base names it an error once any write changes
the entry's text (a `note`, `fmt`, a relink). So a consumer gates each such entry or removes its Ask when it takes
v3.1.

**v3.2 adds the check of text a person reads** (*Text a person reads*): `person_text_problems()`,
`title_problems()`, `sentence_problems()`, `code_tokens()`, `PersonTextProblem`, `SENTENCE_WORDS`,
`CODE_EXTS` and `ACTOR_WORDS`. It reads every file v3.0 wrote as v3.0 did, and no existing function's output
changes; no writer of this package calls the check.

**v3.3 adds the ledger lift's verdict** (*The merge gate's verdicts*, *Edits*): `ledger_lift_verdict()`, the
carve-out for a PR that lifts one entry's decision on the ledger with no board answer, `lift_form()`, which
names the form such a lift takes, and the ledger lift's commit subject, written by `lift_subject()` and read
by `lift_subject_parts()`. No parse, field, Log line, item key or canonical form changes. One reading
changes: `subject_kind()` names that subject `lift`, where earlier releases read None. `split_board_notes()`
also lists each line a split carries to `README.md` from below the first item, which no item holds and which
earlier releases carried with no note, and names a host's run-on, the words a head ran on with past its
host's first word, as `host kept to its first word; not carried: <run-on>` apart from the rest of the head's
text, which earlier releases named whole as `head text not carried`; what `split_board()` writes is
unchanged.

**v3.3 makes the body's edges strict, in two steps** (*The entry*, *The ledger*, *Text a person reads*, *The
ledger writer*): a lead is `**Name:**`; `Ask` is a data field, one line; `check()` flags `lead-form`, `glued-lead`, `fence-open` and `field-lines`, and the writer
refuses an edit that makes one; `migrate-body` rewrites a ledger so it flags none. The reading does not change:
a colon-less lead is still a lead and an Ask's later paragraphs are still read, until v4.0, which reads the
strict form alone once every consumer's ledger is migrated. `migrate-body` changes what is read only where it
adds a boundary: a glued lead becomes its own section, and an Ask of several paragraphs is read as its first. An Ask's context moves to a `**Context:**`
section. No item key, canonical form or Log line changes.

**v3.3's sweep carries an entry's Context** (*The gate sweep*): the `decide` it files for a `decision (<p>)` takes
the entry's `**Context:**` section, on one line, as its detail block's context, where the entry has one; an entry
with none gives the item the context earlier releases wrote.

**v3.3 gives an entry its own answers** (*The ledger*, *The gate sweep*): `**Answers:**` and `**Lifts:**`
one-line fields, `entry_answers()` that reads them, and `check()`'s `answers-unusable`, which the ledger writer
refuses on an edit. The gate sweep's item for an uncovered decision offers the entry's answers where it has
usable ones, and `Go | Not yet` otherwise. No parse, field, Log line, item key or canonical form changes; an
entry that already holds an `**Answers:**` section is offered its own answers, and one whose section cannot be
offered is flagged ℹ when it waits on a person; an edit is refused only where it makes the flag, a `reopen` or a
`renumber` of such an entry among them. *Text a person reads*' allowance of a repo's own
`**Answers:**` section is narrowed: on an entry with a decision gate, it is now the format's one-line field.

**v3.4 adds delegated answers** (TD-132; *The board*, *The board as a directory*, *Edits*, *Lifting a gate*, *The
board writer*, *The ledger writer*, *The merge gate's verdicts*, *The gate sweep*): the `Delegates:` preamble line,
the `decide` item's `Scope` field, the delegated `Decided` form and Log `by` form, `board_delegates()`,
`delegates_problems()`, `delegation_covers()`, `delegates_changed()`, `parse_decided_delegation()`, the writer's
`delegate` and `scope`, `delegate_problem()`, `ledger.py set`'s `--delegate` and `--scope`, and the verdicts'
`lift-delegate-uncovered` and `ledger-lift-delegated`. `BoardItem` and `item_record()` gain `scope`,
`decided_delegate` and `decided_scope`, and `log_line()`'s records of a `gate lifted … answer` line and a `kept
waiting` line gain `delegate` and `scope`. Every file an earlier v3 wrote reads the same; an earlier reader reads a
delegated `Decided` as outside the form (the item reads as undecided), an earlier `log_problems()` faults the new Log
form and an earlier `item_file_problem()` an item's `Scope`, so no delegate writes one, and no item carries a
`Scope`, until every repo that reads the board has this release.

## Appendix: grammar

The grammars below are informative (v2.3: the open item line, a person's name and the rank file; v2.4: `Blocked by` and an Event section; v2.7: the entry header and the Log; v3.0: the item file; v3.3: the ledger lift's commit subject; later releases add the rest).
**The fixtures are the authority** (`fixtures/grammar/`): each production has at least one fixture the module
accepts and one it refuses, and a test checks every fixture against these productions, so the two cannot drift.
The notation is the W3C's EBNF (as in XML 1.0): `::=` defines, `|` separates choices, `?`, `*` and `+` follow
what they repeat, `"…"` is literal text, `[…]` a character class (`^` negates it, `#xN` is a code point), and
`(…)` groups. What a production cannot say is said in prose under its block.

### The open item line (v2.3; a v2 board's, read only from v3.0)

An item line as the v2.x writers wrote it (v2.x's *The form the writers write*): a line `item_problem()` gives
None for (v2.x; v3.0 removes `item_problem()`).
Its line ending is not part of it.

```ebnf
item-line      ::= "- [ ] " ( decide-item | look-item | fyi-item | act-item | other-item | decided-item )
decide-item    ::= "decide " date " " head " — " text context parts? due hide? reply* choices lifts?
look-item      ::= "look " date " " head " — " text context due hide? reply* look-answers
fyi-item       ::= "fyi " date " " head " — " text context hide? fyi-reply*
act-item       ::= "act " date " " head " — " text context doer? due hide? reply*
other-item     ::= ( "watch" " " )? date " " head " — " text context due hide? reply*
decided-item   ::= ( "decide " date " " any-head " — " text context parts? due hide? reply* ( answers lifts? )?
                   | "act " date " " any-head " — " text context doer? due hide? reply* answers?
                   | ( ( "look" | "watch" ) " " )? date " " any-head " — " text context due hide? reply* answers?
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
doer           ::= " Doer: " ( doer-repo | "team " person ) "."
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
field-name     ::= "Context:" | "Parts:" | "Doer:" | due-name | "Hide until:" | "Answers:" | "Lifts:" | "Decided:" | "Closed:"
due-name       ::= [Dd] [Uu] [Ee] ":"
char           ::= [^#xA]
```

What the productions leave to prose: a `date` is a real day of the calendar, and the line ends in no
whitespace. Which labels are forms (*The board*, the `Answers:` bullet) is a reading of a `label`, as its
consequence split is: the productions accept every form as a label (a head that is a field's name makes no label:
v2.x's `item_line()` refused it), and a fill is a `Decided:` text, which they accept as any. A field name counts only at a word's start, after a character that is no letter, digit or `_`
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

A `Doer:` (v2.8) names a team only after the word `team` and one space; `Doer: team.` names the repo `team`. A
doer's repo is a `repo` whose last component does not end in `.` (`doer-repo`, its last part `doer-part`, which is
`repo-part` without a final `.`; both defined under *The item file (v3.0)*), so the period that ends the field is never the name's.

### The item file (v3.0)

An item file as the writers write it (*The form the writers write*): a text `item_file_problem()` gives None for.

```ebnf
item-file      ::= "## " item-text #xA #xA item-header ( #xA #xA item-body )? ( #xA #xA item-log )? #xA
item-text      ::= nonspace ( char* nonspace )?
item-header    ::= ( kind-field #xA )? added-field ( #xA session-field )? #xA context-field ( #xA parts-field )?
                   ( #xA doer-field )? ( #xA scope-field )? ( #xA due-field )? ( #xA hide-field )? ( #xA answers-field )?
                   ( #xA lifts-field )? ( #xA decided-field )? ( #xA closed-field )?
kind-field     ::= "**Kind:** " ( "decide" | "act" | "look" | "watch" | "fyi" )
added-field    ::= "**Added:** " date
session-field  ::= "**Session:** " head-name ( " on " head-name )?
context-field  ::= "**Context:** " item-text
parts-field    ::= "**Parts:** " entry-id ( ", " entry-id )*
doer-field     ::= "**Doer:** " ( doer-repo | "team " person )
scope-field    ::= "**Scope:** " person
doer-repo      ::= ( repo-part "/" )* doer-part
doer-part      ::= [A-Za-z0-9_] ( [A-Za-z0-9_.-]* [A-Za-z0-9_-] )?
                 | "." [A-Za-z0-9_-] ( [A-Za-z0-9_.-]* [A-Za-z0-9_-] )?
                 | ".." [A-Za-z0-9_.-]* [A-Za-z0-9_-]
due-field      ::= "**Due:** " date
hide-field     ::= "**Hide until:** " date
answers-field  ::= "**Answers:** " item-answer ( answer-sep item-answer )*
lifts-field    ::= "**Lifts:** " item-label ( answer-sep item-label )*
decided-field  ::= "**Decided:** " date ( " by " person ( " for " person " (" person ")" )? )? " — " item-text
closed-field   ::= "**Closed:** " date ( " — " item-text )?
item-answer    ::= item-label " (default)"? ( " — " char* )?
item-label     ::= label-start label-char*
item-body      ::= body-line ( #xA body-line )*
body-line      ::= " "* "- " char*
item-log       ::= "**Log:**" ( #xA reply-line )+
reply-line     ::= "- " date ": " reply-by ": " item-text
reply-by       ::= [^#x20#x9:#xA] [^:#xA]*
```

`item-header` gives the fields' order, each at most once, with `added-field` and `context-field` always. What the
productions leave to prose: `parts-field` only on a `decide`, `doer-field` only on an `act`; a `scope-field` only on
a `decide` (v3.4); a delegated `decided-field` only on an item whose `scope-field` names its scope, its delegate not
its person, its Context naming no gate on another repo's entry and, if it names a gate, exactly one entry and one
gate; a
`due-field` on every kind but `fyi`; answers as *A new item* says a kind takes them, and a `lifts-field` only on
a `decide`, each label one of its answers once and never `Go` alone; a decided file has no `session-field` and may
carry any answers or none. Which labels are forms (*The board*, the `Answers:` bullet) is a reading of an
`item-label`, as its consequence split is: the productions accept every form as a label, and a fill is a
`Decided` text, which they accept as any (v2.8). An `item-label` holds no ` — ` and does not end in ` (default)`; a `reply-by` is at most
40 characters and ends in no whitespace; a `date` is a day of the calendar. A `doer-field` names a team only after
the word `team` and one space, so `**Doer:** team` names the repo `team` (`doer_value()` also reads a run of
spaces or tabs there, a spelling `item_file_problem()` faults). A `doer-repo` is a `repo` whose last
part, `doer-part`, is a `repo-part` that does not end in `.`. Every other production is the one above it of the
same name (`date`, `digit`, `char`, `nonspace`, `head-name`, `entry-id`, `repo`, `repo-part`, `person`,
`person-part`, `answer-sep`, `label-start`, `label-char`).

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
check          ::= pr-merged | file-contains | ref-includes | host-log
host-log       ::= "host-log " source ( " kind " token )? ( " times " count )? " " quoted
source         ::= token
token          ::= [a-z0-9] [a-z0-9-]*
count          ::= [1-9] [0-9]? [0-9]?
pr-merged      ::= "pr-merged " repo "#" digit+
file-contains  ::= "file-contains " repo ( "@" ref )? " " path " " quoted
ref-includes   ::= "ref-includes " repo "@" ref " " commit
ref            ::= ref-char+
ref-char       ::= [^#x0-#x20#x7F-#x10FFFF~^:?*[#x5C#%&=+]
path           ::= path-char+
path-char      ::= [^#x0-#x20#x7F-#x10FFFF*?[#x5D#%"#x5C]
quoted         ::= '"' text-char+ '"'
text-char      ::= [^#x0-#x1F#x7F]
commit         ::= hex hex hex hex hex hex hex hex*
hex            ::= [0-9a-f]
```

What the productions leave to prose: a `ref` follows git's `check-ref-format --allow-onelevel` rules and more —
it does not start with `-`, hold `..` or `@{`, or equal `@`; it does not end with `/` or `.`, hold `//`, or have a
component that starts with `.` or ends with `.lock`. A `path` is not absolute, has no empty, `.`, `..` or `.git`
segment and does not start with `-`. A `commit` is at most 40 digits, and a PR's number at most 18. A `token`
(v2.5) is at most 40 characters; arguments are separated by spaces and tabs, as for every check. The quoted text runs from its first `"` to the line's last, and
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

### `Delegates:` (v3.4)

A board's `Delegates:` line in its canonical spelling (*The board*, `Delegates:`): `board_delegates()` reads at
least one grant from it, none outside the form, and the grants re-rendered as `<delegate> for <person> (<scope>, …)`
joined by `; ` after `Delegates: ` are the line itself. The reader's tolerance (whitespace folded, a trailing `;`) is
the prose's; which grants are faults (`delegates_problems()`) is the board's, not the grammar's.

```ebnf
delegates-line ::= "Delegates: " grant ( "; " grant )*
grant          ::= person " for " person " (" person ( ", " person )* ")"
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

### The entry header and the Log (v2.7)

What an entry's writers write, each start symbol with its own judge (*Ledger entries and their edits*, *The
closed Status set*, *The Log*):
- `status-open`, `status-resolved`, `status-superseded` and `status-dropped`: a Status value in the closed set,
  one form each, `status_problem()` giving None for an entry `## TD-1: x`, a blank line and `**Status:** <value>`
  (`archived` false for `status-open`, true for the other three);
- `log-line`: a Log line `log_line()` reads as one of the writers' fixed shapes, never `malformed` nor None;
- `header-block`: an entry's header block, `canonical()` refusing nothing in `## TD-1: x`, a blank line and the
  block;
- `added`: an `Added` value that is a real date, whole.

```ebnf
status-open       ::= "Open"
status-resolved   ::= "Resolved " date
status-superseded ::= "Superseded " date " by " entry-id
status-dropped    ::= "Dropped " date
added             ::= date
header-block      ::= field-line ( #xA field-line )*
field-line        ::= "**" [A-Za-z] [^*:#xA]* ":**" char*
log-line          ::= "- " date ": " log-words
log-words         ::= log-filed | log-gate-added | log-lift-answer | log-lift-override | log-lift-check
                    | log-lift-date | log-lift-skipped | log-kept-waiting | log-reassigned | log-archived
                    | log-reopened | log-was | log-retitled
log-filed         ::= "filed by " log-token ", session " log-token ( ", while " entry-id )? ': "' char* '"'
log-gate-added    ::= "gate added: " gate
log-lift-answer   ::= "gate lifted: " lift-gate " — by " log-token ( " for " log-token " (" log-token ")" )? '; answer "'
                      char* '"' lift-suffix?
lift-gate         ::= "decision (" person ")" | "event (" event-name ")"
lift-suffix       ::= "; board " repo | "; no board item" | "; shared board item left open"
lift-subject      ::= log-token ": lift decision (" person ") on TD-" digit+ " (session " log-token ")"
log-lift-override ::= "gate lifted: decision (" person ") — by " log-token "; override: " nonspace char*
log-lift-check    ::= "gate lifted: event (" event-name ") — by " log-token "; " [a-z0-9-]+ " passed; " nonspace+
log-lift-date     ::= "gate lifted: until " date " — by " log-token "; date reached"
log-lift-skipped  ::= "gate lift skipped: " entry-id " no longer carries " lift-gate
log-kept-waiting  ::= "kept waiting: " gate " — by " log-token ( " for " log-token " (" log-token ")" )? '; answer "'
                      char* '"'
log-reassigned    ::= "gate reassigned: decision (" person ") → decision (" person ") — by " log-token "; "
                      nonspace char*
log-archived      ::= "archived: " [A-Za-z]+ " — " nonspace char*
log-reopened      ::= "reopened — " nonspace char*
log-was           ::= "was: " nonspace char*
log-retitled      ::= 'retitled: was "' char* '"'
log-token         ::= [A-Za-z0-9_.@/-]+
nonspace          ::= [^#x9-#xD#x1C-#x20#x85#xA0#x1680#x2000-#x200A#x2028#x2029#x202F#x205F#x3000]
```

What the productions leave to prose: a Status's and an `Added` value's `date` is a real day of the calendar (a Log
line's date is read as written), and the module's digits are any the regular expression `\d` takes, where the
grammar's `digit` is ASCII alone (the writers write ASCII). The reader drops the spaces and tabs before and after
a field's value, and a `\r` that ends a line; a lone `\r` inside a header line ends that line, and an HTML
comment left open there is refused, so neither is a field line `canonical()` takes. A header block names each field once, and a Priority, Type, Blocked by or Part of line below
it is one `canonical()` refuses, since `entries()` would lift it; the order of the fields is a rendering rule, not a
grammar one (*the canonical form*). Their cases are in `fixtures/status/`, `fixtures/grammar/` and `ledger_edit/check/status_*`. A
`log-line` fixture is a writer's shape only: any other words after the date are a note, which the judge accepts
and no production does, so the refusing side is a line `log_line()` reads as `malformed` (a writer's prefix out of
its shape) or does not read (no `- `, a bad date). A quoted label or words run to the line's last `"`.

`lift-subject` (v3.3) is a ledger lift's commit subject, judged by `lift_subject_parts()` not None. The reader
matches the whole line, nothing after its `)` (no trailing newline); it reads the gate's person as `person`
and the session as `log-token`; its digits are ASCII alone and at most 18 (`[0-9]{1,18}`, as a part's id reads,
never `\d` unless `re.ASCII`, so `TD-١٢` and a 19-digit id are refused, the cap being the reader's, which
`digit+` cannot say, and the id's number always fits the lookup by number); and `lift_subject()` writes the gate as
`_one_gate()` spells it, `decision (<p>)` with the keyword's case and the space before `(` normalised; a gate
`_one_gate()` refuses (`decision (Ann )`, say) is refused.

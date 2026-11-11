# TD-068: a writer for the title, and names in the wrong place

**Status:** Draft 1, 2026-11-11 (session lb-designer). Class: **wide** (a vendored, published format: a new
writer argument, a new Log line shape and reserved prefix, and new refusals in `edit_entry()`, which both
consumers vendor; cap 6 rounds, cadence.md §4.8). Rounds: not yet run (the record:
[docs/reviews/TD-068.md](../reviews/TD-068.md)).

**Entry:** [TD-068](../ledger/TD-068.md). Reported by ShiftLead (its TD-1551, 2026-11-11).

## The problem

An open entry's title can't be changed by any writer. The title lives only in the `## TD-n: title` heading
(SPEC *The ledger as a directory (v2)*: "a retitle never renames a file"). Every edit in `ENTRY_ACTIONS` keeps
"the same id, title, fields and sections but for the change" (SPEC *Ledger entries and their edits*, *Edits*).

The edits that come closest write the name somewhere else instead:

- `edit TD-n --section Title` adds a body paragraph `**Title:** …`, and the heading stays as it was.
- `set TD-n --field Title=…` adds a header field `**Title:** …`, and the heading stays as it was.
- `edit TD-n --section Status` (or `Priority`, `Owner`, …) adds a body paragraph that reads like a field and
  is not one. It sits beside the header's own `**Status:**`.

None of these is refused, and `check()` reports none of them. (A body `Priority`, `Type`, `Blocked by` or
`Part of` is already read as a field and flagged ℹ `below-header`; the others are read as sections and never
flagged.)

**The harm.** When a split changes an entry's scope, its title can be fixed in only two ways:

- by hand, which the cadence forbids a session to do;
- by deleting the file and filing it again under the same id, which loses its Log.

ShiftLead did the second on 2026-11-11 (its TD-1664). A mistyped section name leaves a stray paragraph
that looks like a field.

## What is already settled

- **The title** is the heading's text after `TD-n: `, stripped. `entry_text()` refuses a title that is empty or
  more than one line.
- **A retitle never renames a file** (SPEC *The ledger as a directory (v2)*).
- **The Log** is the entry's dated history. Every writer line has a fixed shape that `log_line()` reads. Its
  prefixes are reserved: `note` refuses words that start with one, and `check()` flags a line that starts with
  one but is not in its shape (`log-line`).
- **`set` already writes the Log.** Since v2.5 it appends a `gate added:` line when it adds a gate.
- **From v2.7, `Location` is a body section.** `set` refuses a non-empty `--location` or `--field Location=…`,
  and points to `edit --section Location`.
- **Header-only names.** The format's own fields are listed in SPEC *The ledger*. The canonical order adds
  `Owner`, `Kind` and `Taken by`, and a ledger's `Fields:` line declares more.
- **Body sections are an open set.** `Why`, `Fix`, `Done when`, `Ask`, `Event (<name>)`, `Related`,
  `Design PR`, `Location`, `Resolved`, `Log` and any repo's own are all taken, so a closed list of allowed
  section names would refuse sections the format already takes.

## Options weighed

**Where the retitle lives.**
- **(a) A `title` argument to `set`**, with `ledger.py set TD-n --title "<new>"` (chosen). The heading is the
  entry's one non-field header datum, and `set` is the edit of the header. ShiftLead's request names `set
  --title`. One `set` can retitle and change fields together, as a split's scope change often does.
- **(b) Its own action, `retitle`, and verb.** Cleaner in the module's list, but it is another verb for every
  consumer's wrapper to learn, and a split then needs two commits or two calls. Rejected.

**Whether the retitle is logged.**
- **A Log line, `retitled: was "<old title>"`** (chosen). The old title is the entry's history. The deletion
  this replaces lost exactly that, and a reader searching the old title in the Log finds the entry. The old
  title is quoted last, so the line reads by the Log's rule that quoted words run to the line's last `"`.
- **No Log line**, so the heading carries only the new title and git keeps the old one. Rejected: the ledger's
  history is its Log, not git (an entry's file can move between `archive/` and back).

**Which names `edit` refuses.**
- **The header's names** (chosen): `Title`, the format's own fields and the canonical order's names, the
  ledger's `Fields:` names, and any field this entry's header carries. `Location` and `Resolved`, which are
  body sections, are left out of the fixed list.
- **Every name SPEC does not list.** Rejected: body sections are an open set (above).

**Which names `set` refuses.**
- **`Title`, `Log`, and any name a section of this entry carries** (chosen). The second and third are symmetric
  with `edit`'s: a header field that duplicates a body section (`set --field Why=…`) is the same stray.

## Decisions

**D1. `set` retitles.** `edit_entry(text, "set", fields=…, title=…)`: `title`, when given, replaces the
heading's title, and `fields` may be empty when it is. The new title is stripped. It is refused when it is empty
or more than one line, as `entry_text()` refuses. A title equal to the entry's (both stripped, compared exactly)
changes nothing and logs nothing. Otherwise the heading becomes `## TD-n: <new title>` (its id as written), and
`- <today>: retitled: was "<old title>"` is appended to the Log, `<old title>` stripped. The Log is made at the
end of the body if there is none, and a Log that is not last is refused, as for `set`'s `gate added` lines. With
both `title` and a gate-adding `Blocked by`, the `retitled` line comes first, then the `gate added` lines.
`today` is required whenever a `retitled` line is written. The file keeps its name. An archived entry is
refused, as for every edit of an archived entry (it is edited only once reopened).

The command line is `ledger.py set TD-n --title "<new title>"`, beside `set`'s other flags; `--title` with no
other flag is a `set`. `--title ""` is refused (a title is never removed). The commit subject is `set`'s.

**D2. The Log line.** `log_line()` reads one more shape, `retitled: was "<title>"`. Its quoted words run from
the opening `"` to the line's last `"`, so a title may hold quotes. `retitled:` joins the reserved writer
prefixes, so `note` refuses words that begin with it, and `check()` flags `log-line` on a line that begins
`retitled:` and is not in the shape. The line names no gate, so gate ages and `gate_added()` ignore it.

**D3. `edit` refuses a header name.** `edit_entry(text, "edit", section=…)` is refused when the section name,
compared by `field_key` with the colon optional (as section leads match), is any of these:

- `Title`, which lives in the heading: *the title is the heading: use set --title*;
- a header-only name: `Priority`, `Type`, `Added`, `Status`, `Blocked by`, `Part of`, `Escaped from`, `Id take`,
  `Owner`, `Kind`, `Taken by` (*… is a header field: use set*);
- a name the ledger's `Fields:` line declares, passed in as `declared=` (the writer passes the names; a caller
  with no ledger passes none);
- a field this entry's header block carries (*… is a field of this entry's header: use set, or remove the field
  first*). This includes an unmigrated header `Location`.

A qualified lead (`Status (old)`, `Note (2026-01-02)`) is matched only by its whole text, as SPEC already says,
so it is never refused by this rule. `Location` and `Resolved` are not header-only names, so `edit --section
Location` and a reopened entry's `Resolved` section still work, except while that entry's header carries the
field. The refusal comes before the body is read, so an entry that already has such a stray section can't have
it rewritten through `edit` either. A person removes it (D5).

**D4. `set` refuses a misplaced field.** `edit_entry(text, "set", fields=…)` is refused for a field named
`Title` (*the title is the heading: use set --title*), `Log` (*the Log is a section its writers write*), or a
name that a section of this entry's body carries, matched by `field_key` (*… is a section of this entry: use
edit --section*). An empty value for such a name, which would remove a field that does not exist, is refused the
same way. `Location` keeps its v2.7 refusal and wording, which comes first.

**D5. `check()` notes a misplaced name.** A new ℹ flag, `misplaced-name`, on any entry with:
- a body section (an unqualified lead) named `Title` or as a header-only name, other than the four
  `below-header` already flags (`Priority`, `Type`, `Blocked by`, `Part of`);
- a body section named as a field the entry's header carries;
- a header field named `Title`.

It is ℹ in every case, on a standing ledger and on an entry an edit changed alike. No writer removes a section
or a stray field, so an error there would block every later edit of the entry until a person hand-edits it.
`check()` passes its `Fields:` names to the same rule.

**D6. A minor release, v2.8.** No parse changes and no key moves. An older reader reads `retitled: was "…"` as a
note (*any other words are a note*), and reads every heading the writer writes. The writers refuse more, `set`
takes `title`, and `check()` gains one ℹ flag. This is not a version event under SPEC *Versions*: the canonical
form and the board's item key are untouched. It rides with TD-067 in v2.8 if both are built by then; nothing in
either depends on the other.

## Consumers

Each consumer's vendor PR gets `set --title` through its wrapper's pass-through of `ledger.py` flags. A wrapper
that lists `set`'s flags by hand adds `--title`. A consumer that writes stray sections on purpose (none is known)
meets D3's refusal. Its `check` run shows `misplaced-name` ℹ on any stray it already has.

- **ShiftLead**: TD-1664's deleted-and-refiled entry keeps the Log it was refiled with, so nothing is repaired
  there. Its wrapper's `set` gains `--title`.
- **agent-cadence**: its vendor PR, and its wrapper's `set` checked for `--title`.

## The SPEC text the build lands

**1. *Ledger entries and their edits*, the `set` bullet.** After "…dated `today`, making the Log at the end of
the body if there is none (a Log that is not last is refused, as for `note`; the Status's notes are not
lifted)." insert

> From v2.8 `set` also takes `title`, which replaces the heading's title (stripped; refused when empty or more
> than one line), and then `fields` may be empty. A title equal to the entry's changes nothing; any other is
> written `## TD-n: <title>` and logs `retitled: was "<old title>"`, dated `today`, which it then requires,
> ahead of any `gate added` line, the Log made and refused as above. The file keeps its name. `set` refuses a
> field named `Title` or `Log`, or named as a section of the entry's body (v2.8).

**2. *Ledger entries and their edits*, the `edit` bullet.** After "It is refused when two sections have the
name, and for the Log, which only its writers write." insert

> From v2.8 it is refused, too, for a name that belongs in the header, compared as leads are: `Title` (the
> heading's: `set` retitles), a header-only name (`Priority`, `Type`, `Added`, `Status`, `Blocked by`, `Part
> of`, `Escaped from`, `Id take`, `Owner`, `Kind`, `Taken by`), a name the ledger's `Fields:` line declares
> (`declared`), and a field the entry's header carries. A qualified lead is matched whole, so it is never one.

**3. *The ledger*, the Log's line shapes.** In the list of shapes `log_line()` reads, after `- \`archived:
<Status word> — <why>\`, \`reopened — <why>\`, and \`was: <Status>\`.` add

> - `retitled: was "<title>"` (v2.8), the title the heading held before `set` changed it.

and in the reserved prefixes, after `` `reopened —` `` add `` `retitled:` (v2.8)``.

**4. *Ledger entries and their edits*, `check()`.** After the `log-line` sentence add

> `check()` notes (ℹ, `misplaced-name`, v2.8) a body section named `Title` or as a header-only name (*edit*,
> above) that `below-header` does not already flag, a body section named as a field the entry's header carries,
> and a header field named `Title`. It is never an error, since no writer removes a section or a field.

**5. *The ledger writer*, the `set, note, edit` bullet.** After "`set TD-n` takes `new`'s field flags" add "and
(v2.8) `--title "<title>"`, the heading's title". After "`edit TD-n --section NAME --from FILE|-` replaces one
section" add "(the ledger's `Fields:` names passed to it as `declared`)".

**6. *Versions*.** Append

> **v2.8 gives the title its writer** (*Ledger entries and their edits*): `set` takes `title` and logs `retitled:
> was "<old title>"`, `retitled:` joins the reserved prefixes, `edit` refuses a header name and `set` a
> misplaced one, and `check()` notes `misplaced-name` (ℹ). No parse changes: an older reader reads the line as
> a note, and no key moves.

## Fixtures

All invented, in the existing fixtures' style.

**`fixtures/ledger_edit/` (`edit_entry`)**
- `set_title`: `reordered.md`, `set` with `title: "A narrower scope"` and no fields: the heading rewritten, the
  Log gaining `- 2026-01-20: retitled: was "<its old title>"`.
- `set_title_and_fields`: `title` and `fields: {"Priority": "High"}` together: both changes, one Log line.
- `set_title_same`: the entry's own title (with extra spaces): the text unchanged.
- `set_title_refused_empty` and `set_title_refused_two_lines`.
- `set_title_quotes`: a title holding `"`; the Log line read back by `log_line()` gives the old title whole.
- `set_title_and_gate`: `title` with a `Blocked by` adding `until 2026-02-01`: `retitled` then `gate added`.
- `set_refused_title_field`, `set_refused_log_field`, `set_refused_section_name` (`fields: {"Why": "x"}` on an
  entry with a Why).
- `edit_refused_title`, `edit_refused_status`, `edit_refused_owner`, `edit_refused_declared` (`declared:
  ["Tracker"]`), `edit_refused_entry_field` (a `Tracker` header field, no `declared`).
- `edit_qualified_status`: `section: "Status (old)"`: added as today.
- `edit_location`: `section: "Location"` on an entry with no header Location: added as today; and
  `edit_refused_header_location` on `retired_after_part_of`'s text (a header `location`).

**`fixtures/ledger_edit/` (`log`)**: `log_shapes.md` gains a `retitled: was "An "old" title"` line and a
malformed `retitled: the old one` line; `every_shape` expects the first read as `retitled` with its title, and
the second as `log-line`.

**`fixtures/ledger_edit/` (`check`)**: a ledger with one entry holding a body `**Status:**` section, a body
`**Title:**` section and a header `**Title:**` field, and one whose body `**Priority:**` is only `below-header`:
expects three `misplaced-name` ℹ on the first and none on the second.

**`fixtures/ledger_writer/`**
- `set_title`: `set TD-001 --title "A narrower scope" --today 2026-01-15 --json`: the file renamed nowhere, its
  heading and Log changed, `paths` the one file.
- `set_title_unchanged`: the same title: `paths: []`, `subject: null`, as `set_unchanged`.
- `set_title_empty`: exit 2, a usage refusal.
- `edit_refused_header_name`: `edit TD-001 --section Status --from -`: exit 1, the refusal's words.
- `edit_refused_declared`: a ledger whose `README.md` declares `Fields: Tracker = …`, `edit --section Tracker`:
  exit 1.

**Unit tests** (`tests/`): the refusal messages name the verb to use; `note` refuses words starting
`retitled:`; a `retitled` line does not move `gate_age()`.

## The builds

**B1** (one build, `Part of: TD-068`): D1–D6 with SPEC text 1–6, the fixtures and the unit tests, landing
together. Location: `ledgerboard/__init__.py` (`edit_entry`, `log_line`, the reserved prefixes, `check`),
`ledgerboard/ledger.py` (`set --title`, `edit`'s `declared`), `SPEC.md` (*The ledger*, *Ledger entries and their
edits*, *The ledger writer*, *Versions*), `fixtures/ledger_edit/`, `fixtures/ledger_writer/`, `tests/`. Done
when: the precheck is green and every fixture above passes (their expected JSON regenerated by the runner; the
release stamps `fixtures/MANIFEST`), with SPEC text 1–6 landed in the same PR.

Then a release (Paul's), agent-cadence's vendor PR and ShiftLead's sync PR, each checking its wrapper's `set`
for `--title` (*Consumers*).

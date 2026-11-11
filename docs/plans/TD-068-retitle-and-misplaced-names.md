# TD-068: a writer for the title, and names in the wrong place

**Status:** Draft 1, 2026-11-11 (session lb-designer). Class: **wide** (a vendored, published format: a new
writer argument, a new Log line shape and reserved prefix, and new refusals in `edit_entry()`, which both
consumers vendor; cap 6 rounds, cadence.md §4.8). Rounds: rounds 1–3 ran 2026-11-11; recurring topic: which copy of a name is the stray (F2, F28, F48) (the record:
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
`Part of` is lifted as a field and flagged ℹ `below-header` only when the header lacks it, and `canonical()` then
refuses the entry, so every edit of it is refused. Beside a header copy it is an ordinary section: read as a
section, accepted by `canonical()` and `edit`, and never flagged. Every other header name in the body is read as a
section and never flagged.)

**The harm.** When a split changes an entry's scope, its title can be fixed in only two ways:

- by hand, which the cadence forbids a session to do;
- by deleting the file and filing it again under the same id, which loses its Log.

ShiftLead did the second on 2026-11-11 (its TD-1664). A mistyped section name leaves a stray paragraph
that looks like a field.

## What is already settled

- **The title** is the heading's text after `TD-n: `, as `entries()` reads it (`title_read`: stripped, an HTML
  comment dropped). `entry_text()` refuses a title that is empty or more than one line.
- **A retitle never renames a file** (SPEC *The ledger as a directory (v2)*).
- **The Log** is the entry's dated history. Every writer line has a fixed shape that `log_line()` reads
  (`LOG_SHAPES`). Its prefixes are reserved (`LOG_PREFIXES`): `note` refuses words that start with one, and
  `check()` flags a line that starts with one but is not in its shape (`log-line`).
- **`set` already writes the Log.** Since v2.5 it appends a `gate added:` line when it adds a gate.
- **From v2.7, `Location` is a body section.** The writer (`ledger.py`, not `edit_entry()`) refuses a non-empty
  `--location` or `--field Location=…` as a usage error, and an empty one still removes a header `Location`.
- **A body copy of a lifted field.** `entries()` lifts a body `Priority`, `Type`, `Blocked by` or `Part of`
  and flags it ℹ `below-header` only when the header lacks that field (the entry's `below`), and `canonical()`
  refuses an entry with such a lifted copy, so every edit of it is refused; curing that is out of this design's
  scope (a person's, as today). When the header has the field too, the body copy is an ordinary section.
- **The format's own fields** are `CADENCE_FIELDS` (`Priority`, `Type`, `Added`, `Status`, `Blocked by`,
  `Location`, `Part of`, `Escaped from`, `Id take`). `Owner`, `Kind` and `Taken by` have a place in the canonical
  order, which is "a rendering rule, not a declaration": a repo declares them on its `Fields:` line or not.
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
- **The header's names** (chosen): `Title`, the format's own fields but `Location`, the retired header fields
  `Waits` and `Taken by`, the ledger's `Fields:` names, and any field this entry's header carries. `Location`
  and `Resolved` are body sections, so they are not on the fixed list. `Owner` and `Kind` are refused only where
  a repo declares them or the entry carries them: hard-coding them would put a repo's vocabulary into the package.
- **Every name SPEC does not list.** Rejected: body sections are an open set (above).

**Which names `set` refuses.**
- **`Title` and `Log`** (chosen): neither is ever a header field. Refusing every name a body section carries
  was weighed and rejected (round 2): it blocks a legitimate `set --status` on an entry with a stray body Status,
  and deadlocks a section such as `Owner` that `edit` may add. A header field that duplicates a body section is
  `check()`'s ℹ, cured by an empty value.

**How an existing stray is cleaned.** A session may not hand-edit the ledger, so each stray needs a writer:
- a stray header field: `set --field <name>=` (an empty value), as today;
- a stray body section: `edit --section <name> --remove` (chosen), a removal allowed only for a section named
  `Title` or as a header name, so it never removes a Why, a Fix or a body Location. The alternative, a `fmt` pass that drops strays, would
  lose their words unseen. Rejected.

## Decisions

**Names.** Names compare by `field_key` with the colon optional, as leads match, and a qualified lead (`Status
(old)`, `Note (2026-01-02)`) is matched only whole, so it is never one of these.
- A **header name** is one of `Priority`, `Type`, `Added`, `Status`, `Blocked by`, `Part of`, `Escaped from`,
  `Id take` (the format's own fields but `Location`), `Waits` and `Taken by` (retired header fields), or a key of
  `declared()` on the ledger's text (the `Fields:` line's names, as `field_key`s), passed to `edit_entry()` as
  `declared_fields` (a caller with no ledger passes none).
- A **misplaced section** is a body section named `Title` or a header name. (A lifted copy, a body `Priority`,
  `Type`, `Blocked by` or `Part of` whose header lacks it, is not reached: `canonical()` refuses that entry, so
  every edit refuses it and `check()` skips it, leaving its `below-header`.)
- A **misplaced field** is a header field named `Title` or `Log`, or a header field that is **not** a header name
  and whose name a body section of the entry also carries (a header `Why` beside a body Why; a retired header
  `Location` beside a body Location). There the header copy is the stray: a body Location is where v2.7 puts it.
  Where a header name stands in both places (a header Status beside a body Status), the header field is the real
  one and only the body section is misplaced.

**D1. `set` retitles.** `edit_entry(text, "set", fields=…, title=…)`. `title`, when given, replaces the
heading's title, and `fields` may then be empty. The entry's title is `title_read` (stripped, an HTML comment
dropped), and the new title is stripped of leading and trailing whitespace only (inner runs kept, unlike
`_one_line`). It is refused when it is empty, is more than one line, or holds `\r` or `<!--`, since the heading
would not read back as that title. A new title equal to the entry's changes nothing and logs nothing (the text
comes back in canonical form); that is checked before `today` is required. Otherwise:
- the heading becomes `## TD-n: <new title>`, its id as written, and the edit's read-back check expects the new
  title as `entries()` reads it (the `title` keyword is kept apart from the local the heading's title is read
  into);
- `- <today>: retitled: was "<old title>"` is appended to the Log, `<old title>` being `title_read`;
- the Log is made at the end of the body if there is none, and a Log that is not last is refused, as for `set`'s
  `gate added` lines;
- with both `title` and a gate-adding `Blocked by`, the `retitled` line comes first, then the `gate added` lines;
- `today` is required whenever a `retitled` line is written;
- an HTML comment the old heading held is dropped with the old title (the Log's `was` gives `title_read`, without
  it).

The file keeps its name. `title` joins `set`'s accepted arguments, so it is not "stray". As with `note`, a
`retitled` line that makes a Log on an entry with none becomes the Log's first line, which a gate with no `gate
added` line ages from.

**The writer.** `ledger.py set TD-n --title "<new title>"` (`plan_edit`'s `title`), beside `set`'s other flags.
`--title` alone is a `set`: the "give at least one field" usage check also accepts `--title`. `new` already has a
required `--title`, so `set` adds its own `--title` beside the field flags it shares with `new`, never through the
shared helper. `_ENTRY_ARGS`, the accepted-arguments tuple and `set`'s "needs the fields" guard all take `title`. `--title ""` is a
usage error, exit 2 (`a.title is not None`, since `""` is falsy). A title the module refuses, two lines say, is
exit 1. An archived entry is refused by the writer (`_open_entry`), as for every `set` (`set_archived`). The commit
subject is `set`'s. An unchanged title on a file already in canonical form writes nothing (`paths: []`, `subject: null`), as
`set_unchanged`.

**D2. The Log line.** `log_line()` reads one more shape, `retitled: was "<title>"`, appended last to
`LOG_SHAPES`, its group named `title`. The quoted words run from the opening `"` to the line's last `"`, so a
title may hold quotes. `retitled:` joins `LOG_PREFIXES`, so `note` refuses words that begin with it, and `check()`
flags `log-line` on a line that begins `retitled:` and is not in the shape. Its kind is not in `LOG_AGE_KINDS`,
so it never resets a gate's age.

**D3. `edit` refuses to add a section that belongs in the header, and removes a misplaced one.**
`edit_entry(text, "edit", section=…, declared_fields=…)`:
- **adding** a section the body lacks is refused when it is named `Title` (*the title is the heading: use set
  --title*), a header name (*… is a header field: use set*), or a field this entry's header carries (*… is a field
  of this entry's header: remove it with an empty value first*), since each would make a misplaced section or
  field;
- **replacing** a section the body has is allowed whatever its name, so a stray's words can still be corrected;
- **`remove=True`** (v2.8) removes the named section, lead and paragraphs. It is refused unless the section is a
  misplaced section (*… is not misplaced: only a section named Title or as a header field is removed*), for the
  Log, when two sections have the name, and with `words` (*remove takes no words*).

So `edit --section Location` adds a body `Location` on an entry whose header has none, and is refused while the
header still carries one (`set --location ""` removes it first); a body Location is never removed by `--remove`.
`edit --section Owner` adds an `Owner` section where the ledger declares no `Owner` and the header has none.

**The writer:** `ledger.py edit TD-n --section NAME --remove`. `--from` stops being required; `_build` refuses
(`Unusable`, exit 2, with the JSON `_say` writes) both `--remove` and `--from`, and neither. The writer passes the
keys of `declared()` on the ledger's README as `declared_fields`.

**D4. `set` refuses `Title` and `Log`.** `edit_entry(text, "set", fields=…)` refuses a non-empty value for a
field named `Title` (*the title is the heading: use set --title*) or `Log` (*the Log is a section its writers
write*). An empty value removes such a field if the header carries it, as for any field: that is the cure for a misplaced
field, never needed for a header name, whose header copy is never misplaced. The module's one-line
check on a value (`set_refused_two_lines`) runs first. The writer's v2.7 `Location` usage error stays in
`ledger.py` and comes before the module is called. Every other name is set as today, a header field a body
section shares among them; `check()` notes that pair (D5).

**`new` follows the same rules.** `entry_text(..., declared_fields=())` refuses a field named `Title` or `Log`
and a section named `Title` or a header name, and `plan_new` passes the keys of `declared()` on the ledger's
README as `declared_fields`, so a new entry is never filed with a misplaced section or field. (A new entry has no
other header field to clash with: its fields and sections are given together, and a section named as a field it
is given is refused, as `edit`'s adding refusal.)

**D5. `check()` notes what is misplaced.** A new ℹ flag, `misplaced-name`, once for each misplaced section and
each misplaced field of an entry, with `declared_fields` from the ledger's `Fields:` line. It reads the entry
through `entries()` (its fields, its `below`) and its body's section leads, and skips an entry `canonical()`
refuses (a lifted copy), which `below-header` already flags. It joins `TEXT_KINDS`, so it is scoped by the
entry's whole text, as `log-line` is. It is ℹ in every case, on a standing ledger and on an entry an edit changed
alike: the cure is a writer (D3's `--remove` for a section, an empty `set` value for a field), and an error would
block the unrelated edit that touched the entry. Two body sections with one misplaced name are flagged once, its
words saying so: `edit` and `--remove` both refuse a name two sections share, so that case is a person's hand fix,
as today. A v2.7 entry with both a header and a body Location is noted once, its header field
misplaced; `set --location ""` cures it.

**D6. A minor release, v2.8, that reads one thing differently.** No key moves and the canonical form is unchanged,
so it is not a major. As v1.3 did, it reads one thing differently: a Log line an older `note` allowed that begins
`retitled:` now reads as malformed, flagged `log-line`, which is an error on an entry an edit changed. No writer
rewrites a Log line, so such an entry is left with the flag, and a person fixes it by hand; a consumer looks once
with `grep -rn ': retitled:' docs/ledger` before taking the release (none is known). A consumer that switches on
`log_line()`'s `kind` meets one new value, `retitled`. An older reader reads `retitled: was "…"` as a note. The
writers refuse more, `set` takes `title`, `edit` takes `remove`, and `check()` gains one ℹ flag. It rides with
TD-067 in v2.8 if both are built by then; nothing in either depends on the other.

## Consumers

Each consumer's vendor PR gets `set --title` and `edit --remove` through its wrapper's pass-through of
`ledger.py` flags; a wrapper that lists the flags by hand adds them. A consumer that writes stray sections on
purpose (none is known) meets D3's refusal. Its `check` run shows `misplaced-name` ℹ on any stray it already has,
and the D6 grep runs once.

A retitle changes the heading's anchor slug (`#td-21-old-title`), so a prose link to that anchor no longer lands
on the heading. v2 files link by path, and the split rewrites links by id, so only a hand-written anchor breaks.
Board items and sweep items keep the old title in their text until their own writers run.

- **ShiftLead**: TD-1664's deleted-and-refiled entry keeps the Log it was refiled with, so nothing is repaired
  there. Its wrapper's `set` gains `--title`.
- **agent-cadence**: its vendor PR, and its wrapper's `set` checked for `--title`.

## The SPEC text the build lands

All in *Ledger entries and their edits (v2.2)* unless named.

**1. The `set` bullet.** After "The old form's refusals come before the refusal for a missing `today`." (the end
of the bullet) add

> From v2.8 `set` takes `title`, which replaces the heading's title, and `fields` may then be empty. The new title
> is stripped and refused when empty, more than one line, or holding `\r` or `<!--`. One equal to the entry's title
> as read changes nothing. Any other is written `## TD-n: <title>` and logs `retitled:
> was "<old title>"`, dated `today`, which it then requires, ahead of any `gate added` line; the Log is made and
> refused as above. The file keeps its name. `set` refuses a non-empty value for a field named `Title` or `Log`.

**2. The `edit` bullet.** After "It is refused when two sections have the name, and for the Log, which only its
writers write." add

> From v2.8 it refuses to add a section named `Title` (the heading's: `set` retitles), a **header name**
> (`Priority`, `Type`, `Added`, `Status`, `Blocked by`, `Part of`, `Escaped from`, `Id take`, `Waits`, `Taken
> by`, and each name the ledger's `Fields:` line declares, given as `declared_fields`), or a field the entry's
> header carries. A section the body has is replaced whatever its name. With `remove` (v2.8) it removes a
> **misplaced section**: one named `Title` or a header name; any other is refused. Names compare as leads do, so a
> qualified lead is never one.

**2a. The *Edits* paragraph.** Replace "and from v2.5 by `set` and `edit`, which require it only to date a gate"
with "and from v2.5 by `set` and `edit`, which require it only to date a gate or (v2.8) a retitle".

**2b. *A new entry*.** After "and sections that would not read back as given" add "(and, v2.8, a field named
`Title` or `Log`, and a section named `Title`, a header name, *edit* below, or a field it is given; the ledger's
`Fields:` names given as `declared_fields`)".

**3. The Log's line shapes.** In the list of shapes, after "`archived: <Status word> — <why>`, `reopened — <why>`,
and `was: <Status>`." add

> - `retitled: was "<title>"` (v2.8), the title the heading held before `set` changed it.

and in the reserved prefixes, after `` `reopened —` `` add `` and (v2.8) `retitled:` ``.

**4. `check()`.** After "information on a standing one." (the sentence after `log-line`) add

> `check()` notes (ℹ, `misplaced-name`, v2.8) each misplaced section (*edit*, below) and each **misplaced field**:
> a header field named `Title` or `Log`, or one that is not a header name and whose name a body section of the
> entry also carries (the header copy is the stray). It is never an error: `edit`'s `remove` and `set`'s empty
> value clean them. An entry `canonical()` refuses is not read for it.

**5. *The ledger writer*, the `set, note, edit` bullet.** After "`set TD-n` takes `new`'s field flags" add "and
(v2.8) `--title "<title>"`, the heading's title (`--title ""` a usage error)". After "`edit TD-n --section NAME
--from FILE|-` replaces one section" add "(or, v2.8, with `--remove` in place of `--from`, removes a misplaced
one; the ledger's `Fields:` names are passed as `declared`)".

**6. *Versions*.** Append

> **v2.8 gives the title its writer** (*Ledger entries and their edits*): `set` takes `title` and logs `retitled:
> was "<old title>"`, `edit` refuses to add a section that belongs in the header and removes a misplaced one,
> `set` and `new` refuse a `Title` or `Log` field, and `check()` notes `misplaced-name` (ℹ). It reads one thing
> differently: `retitled:` joins the reserved prefixes, so a note an older `note` wrote with that prefix now reads
> as a malformed line (`log-line`). No key moves, and an older reader reads the new line as a note.

## Fixtures

All invented, in the existing fixtures' style.

**`fixtures/ledger_edit/` (`edit_entry`)**, each with `"today": "2026-01-20"` where it writes a Log line:
- `set_title`: an entry with a Log (`gate_added.md`), `set` with `title: "A narrower scope"` and no fields: the
  heading rewritten, the Log gaining `- 2026-01-20: retitled: was "<its old title>"` last.
- `set_title_no_log`: `reordered.md` (no Log): the Log made at the end of the body.
- `set_title_log_not_last`: refused, as for `gate added`.
- `set_title_and_fields`: `title` and `fields: {"Priority": "High"}`: both changes, one Log line.
- `set_title_same`: the entry's own title with extra outer spaces, and no `today`: the canonical form of the text,
  no refusal.
- `set_title_refused_empty`, `set_title_refused_two_lines`, `set_title_refused_comment` (`a <!-- b`).
- `set_title_comment_dropped`: a heading `## TD-n: Old <!-- x --> title`, retitled: the comment gone, the Log's
  `was "Old  title"` as `title_read` gives it.
- `set_title_quotes`: an old title holding `"`, retitled (read back by the `log` case below).
- `set_title_and_gate`: `title` with a `Blocked by` adding `until 2026-02-01`: `retitled`, then `gate added`.
- `set_refused_title_field`, `set_refused_log_field`; `set_status_with_stray`: an entry with a body `**Status:**`
  section, `fields: {"Status": "Open"}`: set as today.
- `set_empty_removes_stray`: an entry with a header `Why` field and a body Why: `fields: {"Why": ""}` removes the
  field, the body Why kept.
- `edit_refused_title`, `edit_refused_status`, `edit_refused_waits`, `edit_refused_declared` (`declared_fields:
  ["tracker"]`), `edit_refused_entry_field` (a `Tracker` header field, no `declared_fields`), `edit_owner_allowed`
  (`section: "Owner"`, no `declared_fields`, no header Owner: added).
- `edit_replaces_stray`: an entry with a body `**Status:**` section: `edit` replaces its words.
- `edit_remove_stray`: the same entry, `remove: true`: the section gone. `edit_remove_refused_why` (`no_status.md`,
  no header Why): refused. `edit_remove_refused_location` (`reordered.md`, header and body Location): refused.
  `edit_remove_refused_words`: `remove` with `words`: refused.
- `edit_qualified_status`: `section: "Status (old)"`: added as today.
- `edit_location`: `section: "Location"` on `no_status.md`: added. `edit_refused_header_location`: its own inline
  text with a header `**Location:**` and no body one: refused.
- `new_refused_title_field`, `new_refused_status_section` (`entry_text`, no `declared_fields`).

**`fixtures/ledger_edit/` (`log`)**: `log_shapes.md` gains, as its last lines (so its first line is unchanged), a
`retitled: was "An "old" title"` line and a malformed `retitled: the old one` line; `every_shape` expects the
first read as `retitled` with its `title`, and the second as malformed. A `log` case with its own
literal `text` (an entry whose Log holds `retitled: was "An "old" title"`, the line `set_title_quotes` writes) and
`gates: []` reads the old title back whole.

**`fixtures/ledger_edit/` (`check`)**, each with `"archive": ""` and no `old` (so every flag is standing):
- an entry with no header Status, a body `**Status:**` section, a body `**Title:**` section and a header
  `**Title:**` field: three `misplaced-name`;
- a body `**Status:**` beside a header Status: one, the section;
- a body `**Priority:**` beside a header Priority: one, the section;
- a header `**Why:**` field beside a body Why: one, the field;
- `reordered.md`'s header and body Location: one, the header field;
- two body `**Title:**` sections: one, its words naming both;
- an entry whose body `**Priority:**` is a lifted copy (no header Priority): no `misplaced-name`, its
  `below-header` as today;
- an entry with a `retitled` line the writer wrote: no `log-line`.

`fixtures/run.py`'s list of the `check` kinds a case reports gains `misplaced-name`.

**`fixtures/ledger_writer/`**
- `set_title`: `set TD-001 --title "A narrower scope" --today 2026-01-15 --json`: the heading and Log changed,
  `paths` the one file.
- `set_title_unchanged`: the same title on an already canonical file: `paths: []`, `subject: null`, as
  `set_unchanged` (a file not yet canonical is rewritten in canonical form, as any `set`).
- `set_title_empty`: `--title ""`: exit 2.
- `edit_refused_header_name`: `edit TD-001 --section Status --from status.md`: exit 1, the refusal's words.
- `edit_refused_declared`: a ledger whose `README.md` declares `Fields: Tracker = a | b`, `edit --section Tracker
  --from tracker.md`: exit 1.
- `edit_remove`: `edit TD-001 --section Status --remove` on an entry with a stray body Status: the section gone.
- `new_refused_declared_section`: a ledger whose `README.md` declares `Fields: Tracker = a | b`, `new` with a Fix
  file holding a `**Tracker:**` paragraph: exit 1.
- `note_reserved_retitled`: `note TD-001 "retitled: by hand"`: exit 1.

**Unit tests** (`tests/`): the refusal messages name the verb to use; a `retitled` line's kind is not in
`LOG_AGE_KINDS`; `--remove` with `--from`, and neither, are usage errors with JSON.

## The builds

**B1** (one build, `Part of: TD-068`): D1–D6 with SPEC text 1–6, the fixtures and the unit tests, landing
together. Location: `ledgerboard/__init__.py` (`edit_entry` and its accepted arguments, `entry_text` and its `declared_fields`, `LOG_SHAPES`, `LOG_PREFIXES`,
`TEXT_KINDS`, `check`), `ledgerboard/ledger.py` (`plan_edit`, `plan_new`'s `declared_fields`, `set --title`, `edit --remove` (`--from` no longer required) and
`declared_fields`, the "at least one field" check), `fixtures/run.py` (the `check` kinds), `SPEC.md` (*The ledger*, *Ledger entries and their
edits*, *The ledger writer*, *Versions*), `fixtures/ledger_edit/`, `fixtures/ledger_writer/`, `tests/`. Done
when: the precheck is green and every fixture above passes (their expected JSON regenerated by the runner; the
release stamps `fixtures/MANIFEST`), with SPEC text 1–6 landed in the same PR.

Then a release (Paul's), agent-cadence's vendor PR and ShiftLead's sync PR, each checking its wrapper's `set`
for `--title` (*Consumers*).

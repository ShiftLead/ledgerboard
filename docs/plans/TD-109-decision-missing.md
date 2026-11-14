# TD-109: an Ask with no decision gate is flagged

**Status:** Draft 1, 2026-11-14 (session lb-designer). Class: **wide** (a vendored, published format: a new
`check()` flag that the ledger writer refuses on, and a wider `edit --remove`, which both consumers vendor; cap 6
rounds, cadence.md §4.8). Rounds: not yet run (the record: [docs/reviews/TD-109.md](../reviews/TD-109.md)).

**Entry:** [TD-109](../ledger/TD-109.md). Asked for by agent-cadence (its TD-264 rule 6, 2026-11-14).

## The problem

An entry can wait on a person and nothing shows it. The format pairs a `decision (<person>)` gate with an
`**Ask:**` section, and flags one half of the pair missing: a decision with no Ask is `ask-missing` (SPEC *The
ledger*, `Blocked by`). The other half is not flagged. An open entry with an `**Ask:**` and no decision gate reads
as pickable, gets no board item (the gate sweep files a `decide` only for a gate), and the person never learns that
something waits on them. agent-cadence's TD-261 was such an entry on 2026-11-14, and six more open entries there had
the same shape.

agent-cadence is building the rule into its own wrapper (its PR #212, `ungated_flags()`). That reaches only its own
writer. ShiftLead files entries through `plan_new()` and `plan_edit()` directly. The Ask and the decision gate are
both this format's, and `check()` already scopes `ask-missing` to what an edit changed, so the rule belongs here.

## What is already settled

- **The gate's grammar** (SPEC *The ledger*, `Blocked by`): `parse_gates()` gives `decisions`, `retired` (each with
  its `holder`: a role in `decision (…)` keeps its holder, `hold` has none) and `bad`, where the old decision form
  `decision (<who>) <text>` lands (v3.0: an unreadable item, and a `retired` error naming its cure).
- **The Ask** is a body section led `**Ask:**` (`ASK_RE`, `^\*\*Ask:\*\*`), or a header `Ask` field, which
  `ask-missing` also accepts (`"ask" in e["fields"]`). A qualified lead `**Ask (…):**` is its own section (SPEC
  *Ledger entries and their edits*) and `ASK_RE` does not match it.
- **Lifting is text** (SPEC *Events*): a lifted decision leaves its Ask in the entry as the record of what was
  asked. `lift_gate()` removes the gate and logs `gate lifted: decision (<p>) — by <who>; answer "<label>"` (or
  `override: <why>`). Every lift route writes through it (*Lifting a gate*), the decide lift included.
- **Only a lift writes `gate lifted:`.** `lift_gate()` is its one writer, and the prefix is reserved, so `note`
  cannot write one. `edit_entry(…, "set")` logs `gate added:` for a gate it adds and nothing for one it removes
  (*Ledger entries and their edits*, *Edits*). The ledger writer never drops a decision that way: its `set` route
  (`_gate_route()`, SPEC *The ledger writer*) lifts a decision a `--blocked-by` drops through `lift_gate()`, needing
  `--by <person>`, or reassigns it. So through the writer a dropped decision is always logged as a lift; only a
  direct `edit_entry()` caller or a hand edit drops one silently.
- **The scope rule** (`check()`): a flag in `TEXT_KINDS` is judged on the entry's whole text; with `old`, a flag on
  an entry whose text is unchanged is standing (ℹ), and on a rewritten one a kind in `EDIT_ERRORS` is an error.
  Without `old`, every flag keeps the level it was raised at.
- **The writer's gate** (`ledger.py`'s `gate()`): a write is refused when the ledger after it has a `check()` error
  the ledger before it does not, both judged against one base. So `plan_new()` and `plan_edit()` refuse whatever a
  new `EDIT_ERRORS` kind makes an error, with no change to either function, and a fault already on an entry never
  blocks an unrelated write to it.
- **The package holds no consumer knowledge** (AGENTS.md, ADR boundary). `Owner` is not one of the format's
  fields: a ledger declares it on its `Fields:` line, if at all.

## The design

### D1. The flag: `decision-missing`

An **open** entry is flagged `decision-missing` when all three hold:

1. **It has an Ask:** a body section whose lead is exactly `**Ask:**` (as `ASK_RE` reads it), or a header field
   `Ask`.
2. **Its `Blocked by` names no decision.** A decision here is a readable `decision (<person>)`, a retired item
   (`hold`, or a role in `decision (…)`), or an item in the old decision form (`_old_form_item()`). The last two
   each have their own flag (`retired`), whose cure writes a `decision (<person>)`; counting them keeps one fault
   from being reported twice. Any other unreadable `decision (…)` item (`decision (the owner)`, which
   `parse_gates()` puts in `bad`) names no person, so it is not a decision here: the entry is flagged beside the
   item's own `blocked-item` error, since no reader can tell whom it waits on. An `until` or an `event` gate is not
   a decision: an entry that waits on a date and also asks a person something is flagged. That holds for an event a
   person may lift from a sweep's item too: the event names a check, not a person, so no board item asks anyone the
   entry's Ask, and the Ask is what a `decision (<person>)` exists to put in front of them.
3. **It is not answered** (D2).

**Where it is raised.** In `check()`'s per-entry loop over the open entries' texts, beside the Log, event and
`misplaced-name` flags, since it reads the Log, and never in `pickable()`'s `flag_recs` (where `ask-missing` is
raised): `pickable()`'s callers see no new flag. An archived entry is never read for it, as no Log flag reads the
archive. `pickable()` is unchanged: the flag says
the entry is malformed; it does not hold the entry. (A held entry would still be invisible to the person; the cure is
the gate, which both holds it and puts it in front of them.)

**Its level and scope** are `ask-missing`'s: the kind joins `EDIT_ERRORS` and `TEXT_KINDS`, so it is raised ℹ, is an
error on an entry whose whole text the edit changed, and is standing ℹ on one whose text is unchanged. Its field is
`blocked by`.

**Its text** names both cures:

```
ℹ TD-n: has an **Ask:** but its Blocked by names no decision (<person>), so nothing shows the person that it
waits on them — add the gate with set --blocked-by (and the board item a gained decision is owed), or, if it
waits on no one, remove the Ask with edit TD-n --section Ask --remove
```

For a header `Ask` field, the last clause reads `remove the field with an empty set value (--field 'Ask=')`.

### D2. Answered: the Ask stays after its decision lifts

An entry is **answered** when its Log shows the decision that went with the Ask was lifted, and was not re-added
since: of its Log's lines `gate added: decision (…)`, `gate reassigned: …`, `kept waiting: decision (…)` and
`gate lifted: decision (…)` (read by `log_lines()`), the **last** is a `gate lifted: decision (…)`, answer or
override alike. The person in the lines is not compared: a reassign or a lift names whom it names.

- A Log that cannot be read (`log_problems()` raises something) answers nothing: the entry is flagged, beside the
  Log's own error.
- **The Log alone decides**, on a standing ledger and on an edit alike: `check()` never compares an Ask with
  `old`'s. An entry the edit moved or made (a reopen, a renumber), or whose Ask a link rewrite or the canonical
  form touched, reads as its Log says. A new question on an answered entry is caught where it is written instead
  (D3): the writer refuses to write an Ask on an entry that names no decision.
- **The rule trusts the Log.** A hand edit or a direct `edit_entry(…, "set")` that drops a decision writes no Log
  line, so with two decisions, one lifted and the other then dropped by hand, the last decision line is still the
  lift and the entry reads as answered. Through the writer every drop is a lift or a reassign (below), so only a
  route that bypasses the writer can hide a wait this way; a check of the Log against the gates' history is not
  attempted.

Why the Log and not the base. agent-cadence's reading (TD-109's Fix, question 1) is that an entry whose base carried
a decision the edit lifts is standing. That reading is right for the lift itself, and D2 gives the same answer
there, but it holds for one PR only: the next edit of the entry, a note a month later, finds a base with an Ask and
no gate, and a base-only rule would then call the entry standing for a reason it can no longer see. Every lift
writes its `gate lifted` line (*Lifting a gate*), so the Log carries the answer for good, and the flag reads the same
on a standing ledger as on an edit. `event-ungated` already reads the Log the same way (*Events*: "unless a `gate
lifted: event (<name>)` Log line says why").

**The decide lift on a board answer** is covered: `decide_lift()` writes through `lift_gate()`, so the entry it
writes has the gate gone, the Ask kept, and a last decision line that is a lift. No flag, so `gate()` refuses
nothing. A work-order answer (`One more round`) logs `kept waiting` and keeps the gate; a `Hold: <note>` keeps the
gate and rewrites the Ask, which a gated entry may do. The writer's `set` route that drops a decision lifts it
(`--by` the gate's person, or `--override`), so it too leaves the entry answered: through the writer, removing a
decision is always recorded as somebody's answer. A decision dropped any other way (a direct `edit_entry(…,
"set")`, a hand edit) leaves no lift line, so the last decision line is a `gate added` and the entry is flagged.
Through the writer, then, the flag fires on `new` with an Ask and no decision, and on a gate-less entry that already
had an unanswered Ask once an edit rewrites it (at a check given a base; `gate()` itself refuses no fault already
there); an Ask written onto an entry with no decision is refused by `edit_entry()` itself (D3).

### D3. The Ask's writes: no Ask is written without a decision, and `edit --remove` takes one

**Writing an Ask needs a decision.** `edit_entry(…, "edit")` with `section` `Ask` (replacing the section or adding
it) is refused when the entry's `Blocked by` names no decision in D1's sense: *"TD-n names no decision (<person>):
an Ask is what a decision waits on — set the gate first (set --blocked-by …), then write the Ask"*. So is
`edit_entry(…, "set")` that writes a non-empty header `Ask` field, or changes one, when the resulting `Blocked by`
names no decision. This replaces a `check()` rule that would compare an answered entry's Ask with the base's, which
a reopen, a renumber, a link rewrite and the canonical form all trip (F9). A question asked again on an answered
entry is gated first (`set`, logging `gate added`) and then written, and the entry is then gated, not answered. A
`Hold: <note>` answer, as cadence.md §4.8 has a session record it, keeps the gate and puts the note in the Ask, so
the Ask is written on a gated entry and is untouched. (Whether a `Hold` lifts is the item's `Lifts:`; one that lifts
leaves an answered entry, whose Ask is then not rewritten.) The refusal is the
module's, so every writer that calls `edit_entry()` has it.

**Removing one.**

Today `edit --section <name> --remove` removes only a misplaced section (v2.8). An entry whose Ask was answered
before the Log existed, or was written by mistake, needs a way out that is not a gate; no writer removes it now.
`edit_entry(…, remove=True)` also removes the section `Ask` (matched as leads are, so never a qualified `Ask (…)`)
when the entry's `Blocked by` names no decision in D1's sense. It is refused while one does: the Ask is what the
decision waits on (`ask-missing` would follow). A header `Ask` field is already removed by `set`'s empty value.
The build updates every place that says what `remove` takes: SPEC *Ledger entries and their edits* and *The ledger
writer* (below), `edit_entry()`'s docstring and its refusal *"{name} is not misplaced: only a section named Title or as a header
field is removed"*, `plan_edit()`'s docstring, and `ledger.py`'s `edit` description in its
command table and its `--remove` help (today "only one named Title or as a header field (v2.8)").

### D4. The Owner half stays each consumer's

TD-109 asks whether an `Owner` that names a person, with no decision gate, is flagged too. **It is not: the format
leaves it to each consumer**, for three reasons.

- **Which Owner values name a person is not in the text.** `Owner` is a ledger's own field, and the format reads its
  value as a word. A rule here would need the caller to pass the person words in (a `people=` argument to `check()`)
  or a new `Fields:` mark declaring them. The first makes a ledger's `--check` depend on who runs it, which breaks
  "the same bytes, the same flags"; the second changes the `Fields:` grammar every ledger reads, for one consumer's
  convention.
- **The consumers disagree on what it means.** In agent-cadence an Owner who is the person is a wait (TD-264 rule
  6). ShiftLead's own cadence uses `Owner: <person>` with no gate on purpose: an evaluation only the person can run
  with a session is marked `ledger.py set TD-n --owner <person>`, and its board does not carry it as a decision. A
  format rule would make one of them wrong.
- **The Ask half covers what the format can see.** A wait the text states (an Ask) is caught for every consumer.
  agent-cadence keeps its Owner check in its own wrapper, as it already does.

The alternative, a `people=` argument that turns the Owner half on, is weighed and left out: it adds a caller input
that only one consumer would pass, and ShiftLead's semantics would need it left off.

### D5. The release

A minor: the next one after v3.0 (v3.1 if no other lands first). It reads every file v3.0 wrote, as v3.0 did: no
field, Log line, prefix or item key is new, the canonical form is unchanged, and no entry form changes (SPEC
*Versions*). It tightens `check()`, which a minor may do (v2.1's `cycle`, v2.4's `ask-missing`, v2.8's
`misplaced-name` each did).

**What a consumer's existing entries need.** Nothing before it vendors. An open entry that already has an unanswered
Ask and no decision is standing ℹ, and `gate()` never refuses a write over a fault already there. It becomes an
error only where a check given a base meets it rewritten: a consumer's merge gate on a PR that edits that entry. So
each consumer, in a PR of its own after vendoring, lists its `decision-missing` notes (`ledger.py --check`) and gates
each entry or removes its Ask. agent-cadence's TD-264 already does this for its six (TD-156, TD-187, TD-194, TD-243,
TD-247, TD-249); those whose wait is an Owner alone are D4's and are not flagged here.

**Telling agent-cadence.** When the build merges, the builder mails agent-cadence's techlead that the next release
carries `decision-missing`, so its TD-264 calls `check()` for the Ask half and keeps only its Owner half once it
vendors that release. The mail names the one difference from agent-cadence's own copy (`ungated_waits()`, which
reads `parse_blocked()`'s holders, which already count a role in `decision (…)`): here `hold` and the old decision
form count as a decision too, since each already carries its own `retired` error. agent-cadence agreed to D4 at the design stage
(2026-11-14, its techlead's reply through ledgerboard's techlead): its TD-264 (PR #212, merged) keeps the Owner
branch of its `ungated_waits()` and drops its Ask branch when it vendors the release. It asks to be told when that
release is tagged, so the mail names the release number.

## The SPEC text

### In *The ledger*, the `decision (<person>)` bullet of `Blocked by`

After "… ℹ on a standing ledger)." and before "A decision reassigned more than twice …", insert:

> The converse is flagged too (v3.1): an open entry with an Ask — a body section led `**Ask:**`, or a header `Ask`
> field — whose `Blocked by` names no decision, and which is not answered, waits on a person that no reader shows
> (`decision-missing`; an error on an entry the edit changed — its whole text — ℹ on a standing ledger). Here a
> retired item (`hold`, a role in `decision (…)`) and an item in the old decision form count as a decision, since
> each has its own flag whose cure writes one; an `until` or an `event` does not. An entry is **answered** when the
> last of its Log's `gate added: decision (…)`, `gate reassigned:`, `kept waiting: decision (…)` and `gate lifted:
> decision (…)` lines is a `gate lifted: decision (…)`: the Ask stays as the record of the question, as *Lifting is
> text* keeps an event's section. A Log that cannot be read answers nothing, and the Log alone decides, on an edit
> as on a standing ledger. An `**Ask (…):**` lead is its own section, never an Ask. The cure is the gate (`set`), or, where nothing waits on a
> person, the Ask removed: `edit --section Ask --remove`, or a header `Ask` emptied with `set`. Which `Owner`
> values name a person is a ledger's own, so an Owner is never read as a wait here.

### In *Ledger entries and their edits*, *Edits*, the **set** and **edit** bullets

At the end of the **set** bullet (after "`set` refuses a non-empty value for a field named `Title` or `Log`."), add:

> From v3.1 it refuses a non-empty `Ask` field it adds or changes when the `Blocked by` it leaves names no decision
> (*The ledger*, `decision-missing`): an Ask is what a decision waits on, so the gate comes first.

In the **edit** bullet, after "A section the body has is replaced whatever its name.", add:

> From v3.1 it refuses to write an `Ask` section, replacing it or adding it, on an entry whose `Blocked by` names no
> decision (as `decision-missing` counts one): set the gate first. An answered entry's Ask (*The ledger*) is
> therefore never rewritten while ungated, and a question asked again is gated, then written.

And replace "With `remove` (v2.8) it removes a **misplaced section**, one named `Title` or a header name, and is refused
for any other, for a header name the entry's header lacks (`set` it first), and with words." with:

> With `remove` (v2.8) it removes a **misplaced section**, one named `Title` or a header name, and (v3.1) the `Ask`
> section of an entry whose `Blocked by` names no decision (as `decision-missing` counts one, *The ledger*); it is
> refused for any other section, for an `Ask` while a decision holds, for a header name the entry's header lacks
> (`set` it first), and with words.

### In *The ledger writer*, the `edit` command

Replace "(or, v2.8, with `--remove` in place of `--from`, removes a misplaced one; …)" with:

> (or, v2.8, with `--remove` in place of `--from`, removes a misplaced one, or (v3.1) the `Ask` of an entry with no
> decision; …)

### In *Versions*, after v3.0's paragraphs

> **v3.1 adds `decision-missing`** (*The ledger*, `Blocked by`): `check()` flags an open entry with an Ask and no
> decision whose Log does not show it answered — an error on an entry the edit changed, ℹ on a standing ledger — so
> the ledger writer refuses a write that makes one; `edit` and `set` refuse to write an Ask on an entry with no
> decision; and `edit`'s `remove` takes the `Ask` section of an entry with no decision. It reads every file v3.0 wrote, as v3.0 did: no field, Log line or key is new, and the canonical
> form is unchanged. A ledger v3.0 checked clean can show `decision-missing` ℹ on entries it already held; no write
> is refused over one, and `check()` given a base names it an error once an edit rewrites that entry, so a consumer
> gates each or removes its Ask when it takes v3.1.

(If another minor lands first, the build writes that number in every place above.)

## The fixtures

- **`fixtures/ledger/` (`check()` with no `old`),** added to `gates.md` and its expected JSON, each an open entry:
  an Ask with no `Blocked by` (ℹ `decision-missing`); an Ask with only an `until` (ℹ); an Ask with only an
  `event` and its section (ℹ); a header `Ask` field and no gate (ℹ, the `set` cure in its text); an Ask whose Log
  ends `gate added: decision (pat)` then `gate lifted: decision (pat) — by pat; answer "Go"` (none); one whose Log
  lifts and then adds the decision again with no gate now (ℹ: the last line is `gate added`); one lifted by
  `override` (none); an Ask with `decision (designer)` (`retired` only, no `decision-missing`); an Ask with `hold`
  (`retired` only); an Ask with an unreadable `decision (the owner)` (`blocked-item` and `decision-missing`); a
  `**Ask (earlier):**` section with no gate (none). And in `gates.archive.md`, an archived entry with an Ask and no
  gate (none). The case's `check_since_empty` (`check(old="")`) shows each flagged entry as an error, since every
  entry is new against an empty base; that is expected.
- **`fixtures/ledger_edit/`, its `check` group (`check()` given `old`):** an ungated Ask added by the edit (error);
  an entry already ungated in `old` and untouched (standing ℹ); the same entry with a note added (error: its text
  changed); a lift written by `lift_gate()` (none); a decision dropped by a direct `edit_entry(…, "set")`, no lift
  line (error); a lifted entry the edit adds a note to (none); and, each on an answered entry (gate lifted, Ask
  kept), a reopen (the entry absent from `old`), a renumber, an Ask whose relative link a move rewrote, and the
  Ask's whitespace changed (none of them flagged: the Log decides, F9).
  That group's runner keeps only a listed set of kinds (`fixtures/run.py`, the `check` case: `archive-open-parts`,
  `part-of-archived`, `part-of-unknown`, `log-not-last`, `log-line`, `event-undated`, `status`, `misplaced-name`,
  `retired`), so the build adds `decision-missing` (and `blocked-item`, for the unreadable case if it is put here)
  to that list.
- **`fixtures/ledger_edit/`, its `edit_entry` group:** `remove` of `Ask` with no decision (removed), with a decision
  (refused), and of an `Ask (old)` section (refused: neither misplaced nor an Ask); `edit` of `Ask` with no
  decision, replacing (refused) and adding (refused), and with `decision (pat)` (written); `edit` of `Ask` on an
  answered entry (refused); `set` of a header `Ask` with no decision (refused), with `Blocked by: decision (pat)` in
  the same call (written), and of an empty `Ask` (removed).
- **`fixtures/ledger_writer/`:** `new` with an Ask section and no gate (refused, `decision-missing`); `new` with an
  Ask and `decision (pat)` (written); `set --blocked-by "" --by pat` dropping the decision from an entry with an Ask
  (written: the route lifts it, so the entry is answered, no flag); `edit --section Ask` adding an Ask to an entry
  with no decision (refused, by `edit_entry()`); `reopen` of an answered archived entry and `archive` of an entry an
  answered entry's Ask links to (written, no flag); a `note` on an entry already ungated (written, the fault being there before);
  `edit --section Ask --remove` on an ungated entry (written, the flag gone) and on a gated one (refused).

## Builds

One build, **B1**: the SPEC text above, `check()`'s flag (D1, D2), `edit_entry()`'s Ask refusals and wider `remove`
(D3), the
fixtures above and unit tests, in one PR. Then agent-cadence is told (D5). Each consumer's vendor PR follows the
release, and is that consumer's.

## Not done

- **No Owner rule** (D4).
- **No pickability change** (D1): the flag names the fault; holding the entry would hide it further.
- **No board-side check.** A board line whose Context is `none` but which waits on a person (ShiftLead's
  m-1e898050c9f5) is the board's own question, not this flag's.

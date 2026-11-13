# Ledgerboard: the target design

Draft 62 for Paul's review, 2026-11-02. **The review loop converged at round 20, and again on the changes since (§0.57, §0.58);** draft 31 records your answers on draft 30 (§0.28), draft 32 writes in the two changes you then agreed: the writers move into ledgerboard (§1.1) and boards name several people (§6.2), drafts 33–35 fold in three reviews of those changes (§0.29–§0.31), draft 36 adds four more moves into the module (§1.2), and drafts 37–62 fold in their reviews (§0.33–§0.58). Not committed. Annotate inline.

History:
- **Draft 1:** your first comments.
- **Draft 2:** answered them, after an independent Fable review against the code of all three repos.
- **Draft 3:** answered your notes on draft 2. It dropped the `hold` gate and made events mechanical only.
- **Draft 4:** folded in an independent Sonnet review of draft 3 (§0.1), with each claim checked against the code.
- **Draft 5:** applies your rule that every choice is made on long-term merit, never on a consumer's current usage or a migration shortcut (§0.2), records your decisions of 2026-10-31, and links the entries filed since.
- **Draft 6:** folds in a second Fable review, judged against the long-term rule (§0.3). Each claim was checked against the code.
- **Draft 7:** folds in the prior-art survey (`prior-art.md`). You adopted all eleven gaps and chose UTC dates (§0.4).
- **Draft 8:** folds in a third Fable review, of how draft 7 specifies those changes (§0.5). Each code claim was checked.
- **Draft 9:** your three questions of 2026-11-02, plus three lessons from ShiftLead's phone-view research (§0.6).
- **Draft 10:** folds in a Sonnet review of draft 9 (§0.7). Each code claim was checked.
- **Draft 11:** convergence loop, round 1: Fable on draft 10 (§0.8).
- **Draft 12:** round 2: Sonnet on draft 11 (§0.9).
- **Draft 13:** round 3: Fable on draft 12 (§0.10).
- **Draft 14:** round 4: Sonnet on draft 13 (§0.11).
- **Draft 15:** round 5: Fable on draft 14 (§0.12).
- **Draft 16:** round 6: Sonnet on draft 15 (§0.13).
- **Draft 17:** round 7: Fable on draft 16 (§0.14).
- **Draft 18:** round 8: Sonnet on draft 17 (§0.15).
- **Draft 19:** round 9: Fable on draft 18 (§0.16).
- **Draft 20:** round 10: Sonnet on draft 19 (§0.17).
- **Draft 21:** round 11: Fable on draft 20 (§0.18).
- **Draft 22:** round 12: Sonnet on draft 21 (§0.19).
- **Draft 23:** round 13: Fable on draft 22 (§0.20).
- **Draft 24:** round 14: Sonnet on draft 23 (§0.21).
- **Draft 25:** round 15: Fable on draft 24 (§0.22).
- **Draft 26:** round 16: Sonnet on draft 25 (§0.23).
- **Draft 27:** round 17: Fable on draft 26 (§0.24).
- **Draft 28:** round 18: Sonnet on draft 27 (§0.25).
- **Draft 29:** round 19: Fable on draft 28 (§0.26).
- **Draft 30:** round 20: Sonnet on draft 29. **CONVERGED** (no blockers, no should-fix); its three nits are folded in (§0.27).

§0 records every answer so far. The design sections are rewritten to match. Each item is marked:

- **[agreed]**: you agreed it in conversation.
- **[proposed]**: my proposal, not yet agreed.
- **[open]**: needs your call.

---

## 0. Your questions and notes, answered

### On draft 2

| Your note | Answer | Lands in |
|---|---|---|
| **Added's comment:** what's the point of a comment nothing reads? Should we be deliberate about it rather than dropping it? | **Be deliberate: one principle for every field.** *The header block is what tools read; what only people and agents read lives in the body.* `Added` becomes the date alone. Its provenance (who filed it, from which session, the words that asked for it) becomes the **first line of the Log**, written by `ledger.py new` from named arguments, so it is always present and always in the same shape. Nothing is dropped: agents read the whole file, and it simply moves to where prose belongs. The same principle moves Status's notes to the Log (draft 2) and each gate's prose into the body. `Location` is the exception: it is all prose, but it stays a field because people scan for it in the header. | §2 |
| **Events are a black hole.** Track them, check them routinely, and require a deterministic check. Is anything better checked by an agent? | **No. Events are mechanical only.** I went back through the 23 open `Waits:` lines. Each falls into one of three groups, and none needs an agent to check whether it happened: **(1) things a typed check can see:** a PR merged, a tag, a pin at or past a commit, a file's text; **(2) things the host already witnesses:** "the test fails again in a precheck", "Paul's next Apply of dc-grind", "a session's `ao msg`", which a **host event log** check can count; **(3) judgment**, such as "is the feedback good", "does the page look right" or "watch it for a day". Judgment is **work, not an event**: file it as its own entry (an evaluation or live check). An agent picks it like any other entry, its archive releases the waiting entry through an ordinary id in `Blocked by`, and so the queue tracks it and nothing gets lost. **Tracking needs no separate list:** the event gates in the ledger *are* the watch list, and the host checks them on every sweep. Agents that happen to see something don't have to check anything. | §4 |
| **`decision (designer)` is blurry:** does a design-first entry have to change two fields? | **No, one field and no change.** A design-first entry is already marked by `Kind: design-first`, which is what routes it to the designer (TD-008 has it here). ShiftLead's own convention also sets `Owner: designer`, as it does today. `decision (designer)` was an older third way of saying the same thing. Migration removes it, and nothing else changes on the entry. When the design is agreed, its builds are filed as their own entries `Part of` it. | §3 |
| **Remove Hold from ShiftLead, and use `decision (Paul)` until you release it?** | **Agreed, and it simplifies a lot.** Your use case, "I'm still shaping this in conversation, don't pick it yet", really is a decision: you owe a "go". That is your layer rule §2.4 already. With Hold gone: the `hold` gate, ShiftLead's Hold, Release and prehold, the clock's hold records, and draft 2's two-halves design (§3.1) all disappear. **Every other "not now" has a better gate:** not before a date is `until`; not until something happens is `event`; lower priority is the rank. A held entry's `**Ask:**` says what releases it ("Go once the shape is final?"), so the decision is never empty. **What remains outside the ledger:** ShiftLead's **settling**, its minutes-long cooldown on a new or changed entry. That is a consumer's scheduling choice, not a hold, so it stays ShiftLead's. | §3 |

### 0.1 The Sonnet review of draft 3: what changed

| Finding | Checked | Change in draft 4 |
|---|---|---|
| **The closed Status set doesn't match what is written.** ShiftLead's archive Status lines start with: Resolved 522 (most undated), Done 344, Designed 67, Built 61, Resolved. 10, and bold or other words. **Its open entries use the first word as a stage**: Open 34, Designed 14, Built 8, Partly, Live. | yes; worse than reported (the open entries) | §2.2: a migration map for archived words, the check is ℹ only on archived entries, and **[open]** what to do with the stages on open entries |
| **The decide lift opens the gate on any answer**, including "not yet" or "drop it". | yes | §3, §6: only the `Go` answer lifts; any other answer is logged and the gate stays; exactly one entry per lifting item |
| **Migration order can break a consumer mid-rollout.** Retiring `Waits` in the same release that vendors it, and ShiftLead's `Fields:` line validating `Waits`. | yes | §7: the release that adds the gates also still reads `Waits`, and a later release retires it; each vendor PR carries the reformat |
| **A decision can be left with no board item**, for example its item closed without the lift. Nothing escalates it. | logic | §4.5 is now §3.2: a periodic sweep covers decisions as well as events |
| `host-log … since DATE` can't be written when the entry is filed; a passing check can flip back before the PR merges | logic | `since` defaults to the date the gate was added; a passed event stays passed |
| Log lines are free prose, so a gate's age can't be read from them | logic | §2.2: writer-made Log lines have fixed shapes |
| The `**Resolved:**` body line must stay: ShiftLead's queue reads it (`queue.py:48`) and an archived Status date (`queue.py:230`) | yes | §2.2 says so explicitly |
| `ledger.py migrate` doesn't exist; `pickable()` has no `today` | yes | listed as new work; the signature is stated |
| **Overkill:** `host-log` serves about 3 of 23 waits and needs a log that doesn't exist; five check types is too many | agreed | first set: `pr-merged`, `file-contains`, `ref-includes`; `host-log` is its own later step **[open]** |
| Split the release further | agreed | v2.4 for the gates, v2.5 for Status, the Log and retiring `Waits` |

### 0.2 Long-term merit, not current usage (draft 5)

Your rule: ledgerboard is foundational, so every choice is made on long-term merit. A consumer's current habit or the cost of a migration belongs in the migration plan (§7), never in the target. Six places in draft 4 broke that rule:

| Draft 4 said | Why that was a shortcut | Draft 5 |
|---|---|---|
| The Status check is only ℹ on archived entries | it spared the migration, not the design | Under v2.5 the check is an error on every entry, open or archived *(draft 6: no version pin; see §0.3)*. `migrate` maps every archived word first (§2.2). |
| Stage words on open entries, option (b) | ShiftLead's habit | Option (a) is the design, and stages live in `Kind` *(draft 6: whose field `Kind` is, is open)* (§2.1, §2.3). |
| `Location` stays in the header "because people scan for it" | habit; it breaks principle 4 | `**Location:**` becomes a body section (§2.1). |
| The `**Resolved:**` line stays "because ShiftLead reads it" | the right result for the wrong reason | It stays because an archived entry must say where its lasting content now lives (§2.2). |
| `Taken by` and the old `decision (who) — text` form kept with no end | read for old files indefinitely | A minor release must read what its major wrote, so v2.x keeps reading them. **v3.0 removes them**, along with `Waits` (§7.1). |
| Three check types, sized to the 23 waits that exist today | the evidence set the size, but the doc read like a ceiling | The three are the *first* set. A new type is a format PR whenever a real wait needs one (§4.2). |

### 0.3 The Fable review of draft 5: what changed

| Finding | Checked | Change in draft 6 |
|---|---|---|
| **`pickable(events=…)` repeats the Hold defect.** Results held in one host's memory make two hosts disagree about what is pickable. | logic; this is TD-010's own bug | **`events` dropped.** An event gate is lifted only by text: the host's tool PR that removes it. `pickable()` reads the text, `today` and the resolver, and nothing else (§3, §4.4). |
| **`Ledgerboard: 2.5` breaks today's readers.** `VERSION_RE` takes a whole number only (ledgerboard.py:1954), so `format_major()` returns **1**, and every v2.x reader silently reads the ledger as v1. | yes, run | **The minor pin is dropped**, and §0 #1 is corrected. A v2.5 Status is an error everywhere, and the migration plan runs `migrate` in the same PR as the vendor bump (§2.2, §7). |
| **A format `Kind` is ShiftLead's lane list promoted unchanged.** The module gives its words no meaning, and a repo's `Fields:` line can already make a bad value an error. | yes (SPEC *Fields:*) | **[open]** (i) `Kind` stays a consumer field whose vocabulary cadence.md prescribes, or (ii) a format field only if each word gets a rule the module applies. I recommend (i) (§2.3). |
| **`live-check #<n>` hides a gate in a comment.** ShiftLead reads the PR numbers from the Kind line (`sessionorc/ledger.py:226`) and keeps the entry unpicked until they are live (`queue.py:728`). | yes | **[proposed]** "The build is deployed" becomes an `event` gate on the live-check entry, with a check (§4.2). |
| **`Owner: paul` acts as a hold** (`queue.py:700`) | yes | **`Owner` never blocks.** Waiting on a person is `decision (person)` (§3.2 *Not gates*). |
| **Only a literal `Go` can lift**, but real asks are either/or | logic | The item writer takes `lifts=<labels>`, default `Go` (§6). |
| **Principle 4 contradicts the parsed `check:` and Log lines** | yes | Restated: the header holds one-line values tools route on; the body holds prose plus named sections of fixed shape (§1). |
| Leaving `design-first` is undefined | yes | The writer sets the next Kind and logs `designed` (§2.3) |
| `decision (person)` has no grammar; `(Paul)` and `(paul)` both appear (13 lowercase in ShiftLead) | yes | `person := [A-Za-z0-9_.-]+`, compared case-insensitively (§3) |
| Log grammar gaps: its position, reserved prefixes, continuation lines, concurrency | logic | §2.2 defines each |
| `Superseded … by <repo>#TD-m` is missing from the grammar | yes | added to §2.2 and §5 |
| `today` is "required once `until` exists" | logic | Always required; `until D` lifts when today ≥ D *(draft 7: today is the UTC date, §0.4)* (§3) |
| `Status: Open` carries no information | logic | Kept on purpose, as a checked redundancy (§2.2) |
| Not stated: how check arguments are quoted, how severe the Priority check is, which board, `Dropped`'s why | — | §4.2, §2.1, §3.2, §2.2 |
| The 30-day item is a consumer rule, not format | agreed | marked as consumer in §3.2 and §8 |

### 0.4 Prior art: what changed (draft 7) **[agreed 2026-11-01]**

Five researchers surveyed git-native trackers, agent work queues, wait/approval gates, record lifecycles, and format governance (`prior-art.md`, with sources). You adopted all eleven gaps they exposed, and chose UTC.

| # | Gap | Precedent | Change |
|---|---|---|---|
| 1 | Writers may lose text they can't parse | protobuf keeps unknown fields; Avro drops them | Principle 7: every writer keeps what it can't parse, in place, byte for byte. Fixtures (§7.4). |
| 2 | Retired words could come back with a new meaning | protobuf `reserved` | A reserved list. `check()` names a retired word as *retired*, and no later release reuses it (§2.1, §3). |
| 3 | A check had only two outcomes | Airflow sensor timeouts; Step Functions heartbeats | Four outcomes: passed, not yet, impossible, error. An impossible event goes to the board at once. An error is never read as "not yet" (§4.2, §3.2). |
| 4 | `gate lifted` evidence was free prose | GitHub approvals keep only an optional comment | Fixed shape with `by <who>` and re-checkable evidence (§2.2, §4.2). |
| 5 | Anyone's answer could lift a decision | GitHub's optional "prevent self-review" | Only the named person's answer lifts `decision (person)` (§3, §6). |
| 6 | Check arguments steer a host's credentials | (inferred) | `check()` refuses an absolute path or `..`. Text is literal. Host rules: roster repos only, read-only tokens (§4.1, §4.4). |
| 7 | Two hosts could lift one gate twice | (inferred) | The lift is a no-op once the gate is gone, and its branch is keyed by entry and event (§4.4). |
| 8 | Gate staleness needed stored state | Airflow `timeout`; Step Functions `HeartbeatSeconds` | Gate age comes from the Log's `gate added` date. A `by DATE` deadline waits until the fixed 30 days proves too blunt (§3.2). |
| 9 | Mixed-version and migration behaviour unstated | Rust editions must interoperate; `cargo fix` admits corner cases | Fixtures: an older reader holds the block on a newer Status word and flags it (*Amended 2026-11-04, TD-039: `docs/plans/TD-039-unknown-status.md`.*); `migrate` is idempotent and stops on any unmapped word (§7.4). |
| 10 | Supersede edge cases undefined | Bugzilla DUPLICATE and MOVED; no precedent rewires dependents | A duplicate becomes Superseded by the original. Chains, dedupe and cycles are defined, and the successor must not be Dropped (§5). |
| 11 | Do a part's gates come from its parent? | Org-mode users were surprised that blocking didn't propagate | Restated from SPEC: a part never inherits its parent's ids or gates (§3). |
| — | `until` used each machine's local date, so machines in different zones disagree for part of a day | principle 2 | **Every ledger date is UTC**: `today`, and every date a writer writes (§3). |

### 0.5 The Fable review of draft 7: what changed (draft 8)

Fable reviewed whether the agreed changes are *specified* correctly. Nothing it found bends the long-term rule. I checked every code claim.

| # | Sev | Finding | Checked | Change |
|---|---|---|---|---|
| 1 | blocker | "Keeps unknown text byte for byte" contradicts canonical form, which reorders and respaces fields and **refuses** a header line that is not a field (ledgerboard.py:1585) | yes | Restated: unknown *content* survives verbatim (a field's name and value, body text, Log lines). Header placement and spacing follow canonical form. Text the canonical form can't carry is refused, never dropped. Fixtures check content (§1.7, §7.4). |
| 2 | blocker | Only `path` and `repo` were confined; `ref`, `commit` and `n` allowed option or revision injection; "strip outer quotes" ate a trailing `"` | logic | Grammars for every argument; text ends at the line's last `"` (§4.1) |
| 3 | blocker | "Roster only" does not stop a public ledger probing a private repo: the public lift PR leaks one bit per sweep | logic | A check reaches only repos at least as visible as the ledger's own repo, *and* on the roster (§4.4) |
| 4 | should-fix | Wrong "impossible" cases: a forge's 404 means missing *or* unauthorised; an unpushed commit or a recreated ref may still appear | logic | `pr-merged`: closed-unmerged is impossible, not-found is an error. `ref-includes`: never impossible. New rule: when in doubt, error (§4.2). |
| 5 | should-fix | "A role in `decision (…)` is retired" can't be checked: `designer` is a valid person name. `Done`, `Moved`, `OBE`, `In` weren't reserved | yes | Reserve the literal holder `designer`; add the archived and open words `migrate` maps away (§2.1) |
| 6 | should-fix | The old `decision (who) — text` form swallows any gate after it (ledgerboard.py:173) | yes | Writers refuse to add a gate while the old form stands: migrate first (§3) |
| 7 | should-fix | The stateless sweep loops: after "Keep waiting" the gate is still old and has no open item, so it re-files at once. Items can't be told apart by `Context: TD-n` alone. | logic | The Log is the state: `kept waiting: <gate> — by <person>` resets age. Items are keyed by entry *and* gate (§3.2). |
| 8 | should-fix | Holes in the lift key: a closed-unmerged lift PR is reopened every sweep; `renumber` orphans an open lift PR; the person's case in a ref; `..` in a person name | yes (renumber changes only the id, :1917) | Each fixed (§4.4, §3 person grammar) |
| 9 | should-fix | `ledger.py set` can remove anyone's decision; the module can't know who ran it | yes (:1838) | Removing a decision through `set` must log `gate lifted … by <person>`. The merge gate checks `by` against the PR's author (§3, §6). |
| 10 | should-fix | `item_problem(line)` sees one line, so it can't know an item belongs to a decision | design | That check moves to the merge-gate rule, which reads both files (§6) |
| 11 | should-fix | The resolver returns only `open \| archived \| unresolved`, so cross-repo supersede and drop rules can't work; a chain ending in Dropped is undefined | yes (:61) | The resolver contract carries the Status word and successor. Cross-repo rewiring is the sweep's job. A chain ending in Dropped is refused (§5). |
| 12 | should-fix | UTC knock-ons not listed: every consumer writer passes a *local* date (agent-cadence ledger.py:1072, 1161, 1282, `.astimezone()`); `edit_entry` takes a datetime's `.date()` in its own zone (:1824); the board and ledger dates of one decide lift may differ | yes | Module: an aware datetime is converted to UTC, a naive one refused. Each vendor PR switches its writers to UTC. Every *board* date is the person's local date, and the one-day skew is accepted (§3, §7.2). |
| 13 | should-fix | `migrate` was placed in agent-cadence's `ledger.py`, but ShiftLead vendors only the module | yes | The pure half `migrate_entry(text, …, closed_date=…)` goes in the module; each consumer passes in the git date lookup (§7) |
| 14 | should-fix | "The Log is last" contradicts `archive`, which appends `**Resolved:**` at the body's end when there is no Fix (:1897) | yes | `archive` and `edit` insert before the Log (§2.2) |
| 15–18 | nits | the call site is `sessionorc/ledger.py:525`; the `until` row sat outside the table; `reopened` with no colon blocks the note "reopened the thread"; a parent and its part need two items for one "go" | yes | Fixed; the last is **[proposed]** in §6 |

### 0.6 Your questions of 2026-11-02, and the phone-view lessons (draft 9)

| Question or lesson | Answer | Lands in |
|---|---|---|
| **Use TOML or another standard format for reads, and build only the writers?** | **No, on merit.** A standard parser would read only the ten `key: value` lines. Everything hard stays ours: `Blocked by` items and gates, Event sections, the Log's line shapes, board item lines. `tomllib` only reads, so the writers (which must keep unknown content) would follow a second spec that has to agree with the first. The standard library has no TOML writer and no YAML at all, and CI runs Python 3.10, which has no `tomllib`. YAML is the cautionary tale: `rank.yml` is read only through `rank()` so that `09` stays a string (SPEC:274). **What we take from it:** SPEC publishes every grammar as versioned EBNF with fixtures, so any tool in any language can parse entries without our module. | SPEC appendix (§7.1) |
| **"Only the named person": how do we override when they aren't available?** | **Through a writer, never a hand edit.** A hand edit fails the merge gate anyway, because a lifted decision with no `by` line is refused. **Reassign** moves the decision to someone who can answer. **Override lift** is the last resort: it records a reason, needs a person (not an agent or the host) as author and merger, and puts an `fyi` on the absent person's board. | §3, §2.2, §6 |
| **Parent gates: list them on the parts and roll them up for the parent?** | **Yes. It replaces draft 8's exception.** A gate is written where it holds, usually on the parts. The parent's view of its parts' gates is **derived, never written**, as `parts_open` is. One `decide` item naming the parent lifts that person's gate on each part that carries it. Every item still names exactly one entry. | §3, §6 |
| Phone-view 1: a hide-until date on board items, separate from Due | **Adopt in the format.** Snoozing by editing `Due:` today loses the real deadline. *This reverses prior-art §C's "no snooze": `until` covers the ledger, but board items had nothing.* | §6 |
| Phone-view 4: a non-blocking "found while doing" link | **Adapt.** It is provenance, not routing, so it is not a field (principle 4). It goes in the `filed by` Log line as `while TD-m`. | §2.2 |
| Phone-view 6: bound the length of rank keys | **Adopt.** `midpoint()` lengthens keys with every drag between neighbours, so they can grow without limit. `check()` warns past a length, and a `respace` rank writer rewrites the keys. | §6.1 |
| Phone-view 2, 3, 5, 7–10 | Consumer work: escalation by kind, one-tap answers, quiet claims, parallel waves, delegate display, the stale review, plan approval. #10 is a convention (`Kind: design-first` + `decision (person)`) **without** a default answer, because a decision never defaults. | not format |

### 0.7 The Sonnet review of draft 9: what changed (draft 10)

| # | Sev | Finding | Checked | Change |
|---|---|---|---|---|
| 1 | blocker | `item_key` strips Due, Decided, Closed and replies but not `Hide until`, so hiding an item would re-key it, and consumers store item keys | yes (ledgerboard.py:901) | `item_key` strips `Hide until`. No line carries it today, so no stored key changes. It still lands as a deliberate change, because the docstring makes `item_key` part of the format (§6). |
| 2 | blocker | `Hide until` has no position on an `fyi` item, which has no Due. `CONTEXT_RE`'s lookahead (:774) would swallow it into Context, and the reply/answer sanitising regexes (:1056-1058) don't know it | yes | Order defined: `Context. [Due.] [Hide until.] [replies] [Answers] [Decided]`. The name joins `CONTEXT_RE` and the three field regexes. `fyi` may carry it (§6). |
| 3 | blocker | `respace` breaks pick order. Only lined entries have keys in the file; the rest use implicit keys, and ShiftLead sorts several repos' cards together by key (`rank.py:52`) | yes | `respace` treats every key it doesn't own as fixed: implicit keys, plus the other repos' keys a caller passes in. It respaces only the lined keys between two fixed neighbours, inside that gap. Equal keys stay equal (§6.1). |
| 4 | should-fix | Consumers store rank keys (ShiftLead's `ranks.json` flush signature) | docstring | A `queue: respace` subject that consumers recognise and flush on (§6.1) |
| 5 | should-fix | The parent go isn't threaded through: the sweep and the merge gate look for an item naming the *part*, so they'd duplicate or refuse | logic | **Covered** is defined: a part's gate is covered by an open item naming its parent and the gate. The sweep, the merge gate and the lift row all use it (§3.2, §6). |
| 6 | should-fix | A parent go could lift parts filed after the question, or parts with a different Ask | logic | The item snapshots its parts, `Context: TD-12 decision (Paul). Parts: TD-15, TD-16.`, and the lift touches only those (§6) |
| 7 | should-fix | The override contradicts "nobody else lifts". Agents commit under the person's git name, so "a human author" can't be read from git | yes (git user is Paul) | The rule is about *sessions*, not git authors. Only a **person-started session** may write a lift, reassign or override. The consumer attests it; the module records `by` (§3). |
| 8 | should-fix | Reassign had no guard | logic | Only a person-started session may reassign. b ≠ a, b must have a board, a gets an fyi, the old item closes as "moved", and the age resets. More than two reassigns is ℹ (§3). |
| 9 | should-fix | An override with no board to notify | logic | Refused (§3) |
| 10 | should-fix | `renumber` would leave `while TD-m` pointing at a different entry | yes (`rename_ref`, :1807) | `rename_ref` rewrites the `while` token, the one structured id in a Log line. Prose stays history (§2.2). |
| 11 | should-fix | `filed by`'s `<who>` and `<s>` have no grammar | logic | Token grammars: no comma, colon or quote (§2.2) |
| 12–15 | nits | the EBNF can drift from the regexes; `parts_gates` depth and casing; Log shapes that differ only after the prefix; `respace` must be added to the subject vocabulary | — | The fixtures are the authority and a test cross-checks the EBNF; direct parts only, with canonical casing; a fixture per shape; `respace` joins `rank\|join\|prune` |

### 0.8 Convergence round 1: Fable on draft 10 (draft 11)

Fable found no blockers, 6 should-fix and 7 nits; verdict NOT CONVERGED. I checked each claim.

| # | Sev | Finding | Checked | Change |
|---|---|---|---|---|
| 1 | should-fix | §5 (v2.4) reads archived Status words, but the closed set only lands in v2.5, so v2.4 meets `Done`, `Built` and undated `Resolved` | yes | A v2.4 rule: an archived entry whose Status starts with anything other than `Superseded` or `Dropped` reads as closed (Resolved). Only those two words trigger §5 (§5). |
| 2 | should-fix | The parent snapshot `parts TD-15, TD-16` sat inside Context, whose reader takes every `TD-n` as a ref (SPEC:307, ledgerboard.py:775), so the item would "name" three entries | yes | The snapshot moves to its own item field, `Parts: TD-15, TD-16.`, and Context names one entry (§6) |
| 3 | should-fix | Stripping `Hide until` from `item_key` in a minor breaks SPEC's own rule that changing a line's key is a major (SPEC:343) | yes | SPEC's rule is restated precisely in v2.3: the key may not change *for any line a prior release's writers could write or its checks accepted without a problem*. No writer wrote `Hide until`, and `item_problem()` already flags unknown text. This is the rule's purpose stated exactly, not an exemption (§6, §7.1). |
| 4 | should-fix | "The merge gate checks `by` against the PR's author" contradicts "a git author proves nothing" | yes | **The writer is the enforcement point:** the consumer's writer refuses a lift, reassign or override unless the running session is person-started. The merge gate checks only the shape, and that `by` matches the gate's person (any person token for an override) (§3). |
| 5 | should-fix | The repo grammar admits `.`, `..` and non-ASCII (`XREPO_ITEM_RE` matches `../x#TD-1`, run) | yes | Each repo component is ASCII `[A-Za-z0-9_.-]+`, is not `.` or `..`, and doesn't start with `-` or `.`. This applies to both the check argument and `Blocked by`'s cross-repo ids, from v2.4 (§3, §4.1). |
| 6 | should-fix | No writer hides an existing item: `snooze` still rewrites `Due:` (ledgerboard.py:1142, 1194) | yes | `snooze` writes `Hide until` and leaves Due. A new `due` action moves the real deadline (§6). |
| 7–13 | nits | TD-012 isn't filed yet; the `decision (designer)` special case is already gone (TD-1296); the module never *reads* `Waits`, ShiftLead does; the `respace` subject shape; nothing enforces "Log last"; `parts_gates` casing "first written"; quotes inside Log answer labels | yes | All fixed in place |

### 0.9 Convergence round 2: Sonnet on draft 11 (draft 12)

Sonnet found no blockers, 3 should-fix and 4 nits; verdict NOT CONVERGED. I checked each claim. Its checks of the round-1 fixes against real data hold: every existing cross-repo id passes the tightened grammar, and every unmigrated archived Status in both consumers reads as closed under the v2.4 rule.

| # | Sev | Finding | Checked | Change |
|---|---|---|---|---|
| 1 | should-fix | The restated key rule leaned on `item_problem()`, which doesn't exist until v2.3. A v2.2 check accepted any item prose, so the restatement forbids the strip it was meant to allow, and would permit any future change | yes (no `def item_problem`) | SPEC's key rule stays word for word. The strip is a **one-time, documented exception**, proven safe by data: each v2.3 vendor PR shows no line on that repo's board holds `Hide until:` (none does today in either consumer). (§6) |
| 2 | should-fix | `snooze` writing `Hide until` breaks agent-cadence's board contract: its `user_attention.md:25` says "to snooze, edit the Due date", and its nudge ranks and escalates (14 days) by `overdue_days`, so a snoozed item would stay surfaced and escalate | yes | The module adds `BoardItem.hide_until` and `hidden(today)`; `overdue_days` still measures the deadline. **A hidden item is neither surfaced nor escalated.** §7.2 gains each consumer's work: agent-cadence's nudge skips hidden items, its board doc is reworded, and `board_edit` gains `due`; ShiftLead exposes `due` and its inbox reads `Hide until` (§6, §7.2). |
| 3 | should-fix | Overstated enforcement: a hand edit adding `— by Paul; answer "Go"` passes the shape check | logic | The residual is stated plainly: the writer is the protection, the merge gate catches only a careless edit, and review of the diff is the backstop. A **tripwire** is added and labelled as forgeable: removing a decision gate must come with the covering board item's `Decided:` in the same diff (same repo) (§3). |
| 4–7 | nits | `REF_TD_RE` (:775) is a third loose repo grammar; `Parts` missing from the field regexes and the key, valid only on `decide`, and a part that lost its gate before the answer; old `snooze` subjects mean Due; `Owner: paul` stops holding before the remodel converts it | yes | `REF_TD_RE` tightened too; `Parts` added everywhere, `decide` only, and a part that lost its gate is skipped and logged; the subject history noted; step 4 converts `Owner: paul` waits along with the Holds |

### 0.10 Convergence round 3: Fable on draft 12 (draft 13)

Fable found no blockers, 3 should-fix and 6 nits; verdict NOT CONVERGED. I checked each claim. It also confirmed that the merge gate can see both sides of the ledger (agent-cadence `check_cadence.py:86-103`), so a correctly scoped tripwire is checkable.

| # | Sev | Finding | Change |
|---|---|---|---|
| 1 | should-fix | The same-diff `Decided:` tripwire would refuse routes the design keeps: the `set by=` lift, the override, reassign, archive, the remodel's lift of a stale gate, and the parent go | Scoped precisely, with its exemptions listed. The `set by=` route now also writes the covering item's `Decided:` (§3). |
| 2 | should-fix | "Proven safe by data" overclaims: a vendor PR sees only the consumers' own boards, not the roster's. And a one-time exception to avoid a major is a judgement for you, not a proof. | Reworded honestly, with the residual named, and **put to you in §8 #14** (§6) |
| 3 | should-fix | v2.3 had no place in the order of moves, so its `snooze` contract change could be vendored before agent-cadence's nudge skips hidden items | A new step 0: v2.3, and each consumer vendors it in one PR together with its v2.3 work (§7.2) |
| 4–9 | nits | `item_record` needs `hide_until` and `hidden` keys; `snooze`'s read-back check (:1159) must assert `hide_until`; the UTC datetime rule applies to ledger writers only; `Parts:` is defined in v2.3, but its writer needs v2.4's gates; a past `Hide until` lingers forever; two line cites | All fixed in place |

### 0.11 Convergence round 4: Sonnet on draft 13 (draft 14)

Sonnet found no blockers, 2 should-fix and 3 nits; verdict NOT CONVERGED. I checked each claim. Both should-fix findings are about the decide lift meeting the real merge gate.

| # | Sev | Finding | Change |
|---|---|---|---|
| 1 | should-fix | A decide lift changes the board and the ledger in one commit, but agent-cadence's carve-out (a tool's board PR, where the person's click is the review) accepts only a PR that touches the board alone (`check_cadence.py:1675`, verified). Every lift would fall to the ordinary review row. The design also didn't say which script writes both files. | The consumer's decide action (`board_edit.py decide`; ShiftLead's `decided_line` path) owns the two-file write. The carve-out widens to a **lift PR**: the board's one-item decide edit, plus ledger changes that are only gate removals and their `gate lifted` / `kept waiting` Log lines (§6, §7.2). |
| 2 | should-fix | A cross-repo lift contradicts the tripwire: the covering `Decided:` sits on the asker's board in another repo | Exempt: the lift's Log line names the board it came from, `…; answer "<label>"; board <repo>`, and the evidence lives there (§3, §2.2) |
| 3–5 | nits | `set by=` on one part covered by a shared parent snapshot would mark the whole item decided; refusing a naive datetime is in no release row; step 0's v2.3 work was nested in steps 3 and 4 | A shared snapshot item is left open, and the lift logs `shared board item left open`; the datetime rule goes in v2.4; the v2.3 work moves into step 0 itself |

### 0.12 Convergence round 5: Fable on draft 14 (draft 15)

Fable found no blockers, 2 should-fix and 4 nits; verdict NOT CONVERGED. Both should-fix findings concern round 4's lift PR. It also verified all 17 `ledgerboard.py` line references in the draft.

| # | Sev | Finding | Change |
|---|---|---|---|
| 1 | should-fix | The lift PR's shape wasn't tied to the deciding item, so a decide on TD-3 could carry the removal of an unrelated gate on TD-40 past review. `subject_kind` gives `edit` for every board action (ledgerboard.py:1306), so it can't tell a decide from a snooze. | The shape is stated line by line so `check_cadence.py` can verify it, like its queue-edit row: the subject's action is `decide`; there is one `Decided:` item; only its Context or `Parts:` entries change; each changes by exactly one removal of that person's gate plus one matching Log line; nothing else changes (§6). |
| 2 | should-fix | A cross-repo lift PR touches only the ledger, so it never fits the lift-PR shape, and the design didn't say who reviews it. `; board <repo>` was self-asserted. | A cross-repo lift PR always takes ordinary review. The tripwire accepts `; board <repo>` only when the repo is another one on the roster, and the gate sweep audits that the named board holds the matching `Decided:` (§3, §6) |
| 3–6 | nits | ShiftLead's lift needs step 3's agent-cadence release pinned first; "covered" looked at one board only; the `migrate` exemption was self-asserted; §4.1's "nothing may follow" the quoted text vs the Log suffixes | Step 4 starts with the pin bump; covered counts an open item on any roster board whose Context names `<repo>#TD-n`; `migrate` gets a fixed subject; the suffix exception is stated |

### 0.13 Convergence round 6: Sonnet on draft 15 (draft 16)

Sonnet found no blockers, 3 should-fix and 4 nits; verdict NOT CONVERGED. I checked each claim: `lifts` is stored nowhere, and neither the module nor SPEC has a Log today.

| # | Sev | Finding | Change |
|---|---|---|---|
| 1 | should-fix | Condition (d) can't tell a lifting answer from a non-lifting one: `lifts=` was a writer argument stored nowhere, so a PR could remove the gate under `answer "Not yet"` | The lifting set is stored on the item as a field, `Lifts: Go.` (default `Go` when absent), so the checker can read it (§6) |
| 2 | should-fix | The Log was in v2.5, but v2.4's lifts, sweep and condition (d) all depend on it | **The Log moves to v2.4**: the section, its fixed shapes, "Log last", and the writers appending to it. v2.5 keeps migrating the old Status notes and `Added` comments into it (§7.1). |
| 3 | should-fix | (d) had only two branches, so a parent go with a skipped part, or a parent that doesn't carry the gate, fell to ordinary review; a non-lifting answer on a parent go was ambiguous | **(d) and (e) become one test.** The module gains a pure `decide_lift(...)`. The checker applies it to the base text and requires the head to be byte-equal. Every branch (lift, kept waiting, skipped part, parent, case) is defined once, in the module (§6). |
| 4–7 | nits | (a) needs the subject's action word; whether the direct-commit audit accepts a two-file lift; roster boards are machine-local clones; an agent-appended item's prose could misstate its Context | `edit_action(subject)` in the module (v2.3); PR only, so a direct two-file commit fails the audit; the sweep reads each roster repo's origin branch, where missing or stale means not covered, and the Context key de-dupes; the merge gate's cross-repo coverage only flags; the card shows the Context and the gate the click will lift |

### 0.14 Convergence round 7: Fable on draft 16 (draft 17)

Fable found no blockers, 4 should-fix and 4 nits; verdict NOT CONVERGED. I checked each claim. All four should-fix findings are narrow.

| # | Sev | Finding | Change |
|---|---|---|---|
| 1 | should-fix | `decide_lift`'s inputs `today` and `by` weren't stated, and the checker can't reproduce `today`: it runs later, and `Decided:` carries a local date | The checker's inputs are named: the base board line; the head's `Decided:` label; `by` is the gate's person as the header spells it; `today` is the date on the PR's new Log lines, which must all agree and be within one day of the commit's UTC author date (§6) |
| 2 | should-fix | `ANSWERS_RE`'s lazy group (ledgerboard.py:743) would swallow a following `Lifts:` | `ANSWERS_RE`'s end anchor and `_trailer`'s field start gain `Lifts`. `Lifts` is placed in both item-line order statements, and `\|` is escaped as in Answers (§6) |
| 3 | should-fix | After a non-lifting answer the item is closed and the gate uncovered, so the sweep re-asks at once: only the event row read age | The decision row reads age too. An uncovered decision is re-asked only when no `kept waiting` line for that gate is newer than the consumer's interval (§3.2) |
| 4 | should-fix | v2.4 writers would still write Status notes and `Added` comments, so v2.5's `migrate` would duplicate Log lines | From v2.4, `new`, `note`, `archive` and `reopen` write the Log line only. Status becomes `<word> <date>` and `Added` a date, which v2.2 readers can read. Writers create `**Log:**` when it is missing. `migrate` skips a note whose Log line exists (§7.1) |
| 5–8 | nits | `gate lift skipped:` was not reserved; `Lifts:`'s field belongs in v2.3 beside `Parts:`; an archived or missing entry in `decide_lift`; lift PRs must be squash-merged | All fixed |

### 0.15 Convergence round 8: Sonnet on draft 17 (draft 18)

Sonnet found no blockers, 3 should-fix and 3 nits; verdict NOT CONVERGED. It checked fix 4 against every consumer reader and found no conflicts: `**Resolved:**` and the `Added` dates are still read correctly.

| # | Sev | Finding | Change |
|---|---|---|---|
| 1 | should-fix | `today` was anchored to the commit's author date, which can be forged (`git commit --date`) and is the merge time on a squash | Anchored to the forge's **PR `createdAt`** UTC date, which can't be forged and is the same before and after merge (§6) |
| 2 | should-fix | Gate age had two definitions, and a gate present at filing (TD-212's case) had no `gate added` line, so it never aged | `new` writes one `gate added` line for each initial gate. Age is defined once: the latest `gate added`, `kept waiting` or `gate reassigned` line for that gate, falling back to the first Log line and then `Added` (§2.2, §3.2) |
| 3 | should-fix | v2.4's Log-only writers would destroy an existing Status note before v2.5 migrates it. A legacy entry's Log would lack a `filed by` line, and migrated lines would break oldest-first | Before writing, v2.4 `archive`, `reopen` and `note` lift any existing Status note into a dated Log line. `check()` never requires `filed by` first. `migrate` inserts in date order, and the skip rule is gone (§2.2, §7.1) |
| 4–6 | nits | `Open` is bare; `kept waiting` only on entries that still carry the gate, and how `Lifts:` labels compare; no §3.1, and v2.5 still listed `Added` | All fixed |

### 0.16 Convergence round 9: Fable on draft 18 (draft 19)

Fable found no blockers, 3 should-fix and 4 nits, all in the writer and migration seam that round 8 opened; verdict NOT CONVERGED. I checked each claim. `note` appends to Status (ledgerboard.py:1797), so a single Status can hold several dated notes; 250 Status lines across the consumers carry two or more dates.

| # | Sev | Finding | Change |
|---|---|---|---|
| 1 | should-fix | The v2.4 note lift had no split rule, no date for an undated note, and no insertion rule | A pure module function, `status_notes_to_log(entry_text)`, shared by the v2.4 writers and `migrate`. It makes one Log line per dated segment, uses defined fallback dates for undated text, inserts in date order, and neutralises any reserved prefix. Fixtured. (§2.2) |
| 2 | should-fix | `migrate` would turn free-prose `Added` comments into malformed `filed by` lines | The comment becomes a plain dated Log line; `filed by` is written only when the comment parses into that shape (§2.2) |
| 3 | should-fix | The sweep's event items ("Keep waiting", "Drop the gate") had no ledger writer or Log shape, and would all fall to ordinary review | `decide_lift` covers whichever gate the item's Context names, decision or event, with a shape for a person dropping an event gate. The byte-equality carve-out is unchanged (§6, §2.2) |
| 4–7 | nits | `check_cadence.py` doesn't fetch `createdAt` (agent-cadence forge.py:234); §3.2 restated age narrowly; whether `migrate`'s `Waits` → gate writes `gate added`; "writers never produce the old form" wasn't a refusal | `createdAt` added in step 3; §3.2 cites §2.2; the remodel writes `gate added` dated the remodel day; `new` and `set` refuse the old form from v2.4 |

### 0.17 Convergence round 10: Sonnet on draft 19 (draft 20)

Sonnet found no blockers, 3 should-fix and 3 nits; verdict NOT CONVERGED. It tested the split rule against 1,217 real Status lines, and I checked the writer forms in code. `note` appends ` D: words` with only a space before it (ledgerboard.py:1795), so a writer's note boundary looks exactly like a date in prose such as "done 2026-10-03: the image installed". No split rule can tell them apart.

| # | Sev | Finding | Change |
|---|---|---|---|
| 1 | should-fix | The split on ` D: ` cuts prose dates and strands fragments | **No split inside a note.** The Status's whole tail becomes **one** Log line, verbatim, dated by the Status's own date or the fallbacks. The dates inside it stay readable as prose. The only boundary the function cuts at is `reopen`'s ` — was: `, which no prose writes (§2.2). |
| 2 | should-fix | The Status's own date vs a note's was undefined; `Superseded D by TD-m: why` and `— was:` weren't covered | The Status grammar is stated: `<Word> [D] [by <id>] [[:] <tail>] [ — was: <Status>]`. A `— was:` part becomes its own line, `was <Status verbatim>`, so the old word survives as text and no extraction rule is needed (§2.2) |
| 3 | should-fix | `by` for an event item is undefined: an event has no person; event drops had no stated authority; the fate of the Event section on a lift was unstated | For an event item, `by` is the board's person, supplied by the consumer and checked against the item's board. The person-started-session rule applies. Any lift of an event gate removes its `**Event (name):**` section, since the Log line keeps the check type and evidence, and `check()` notes an orphan section (§6, §4.2) |
| 4–6 | nits | The two event-lift shapes are told apart only by their tail; the impossible item's "Rewrite the check" and "Drop the entry" were logged as `kept waiting`; the v2.5 "untouched entries" clause | Readers key on the tail, with a fixture for each; on an event item only "Keep waiting" writes `kept waiting`, other labels write no ledger line ("Drop the entry" hands off to `archive --dropped`); v2.5 migrates any entry whose `Added` still holds a comment |

### 0.18 Convergence round 11: Fable on draft 20 (draft 21)

Fable found no blockers, 3 should-fix and 3 nits; verdict NOT CONVERGED. It re-verified all 29 `ledgerboard.py` citations, and confirmed the three vendored copies are byte-identical. It also tested the grammar against 1,228 real Status lines.

| # | Sev | Finding | Change |
|---|---|---|---|
| 1 | should-fix | The Status grammar's `<Word>` was unconstrained, so about 70 prose-only or bold-lead Statuses (`**Live check held…`, `Steps 1 and 2 shipped…`) would lose their first token, in v2.4, before `migrate` could stop on them | `<Word>` must be a known Status word. Otherwise the function lifts nothing. `archive` and `reopen`, which replace Status anyway, first copy the whole old value verbatim into a Log line. v2.5's `migrate` stops on the unknown word, so the remodel decides it (§2.2). |
| 2 | should-fix | "`by` is the board's person" was unenforceable: no board declares its person (SPEC:289; ShiftLead's is a code constant) | Boards declare it in a preamble line, `Person: <person>` (v2.3). An event lift's `by` is the **base** board's value. With no `Person:` line, an event item's lift takes ordinary review (§6). |
| 3 | should-fix | Removing the Event section on a lift loses the check's arguments; the Log keeps them only for `pr-merged` | **The section is kept**, like an Ask after its decision lifts. `check()` notes an Event section with no gate only when it has no `gate lifted: event (name)` line (§4.2, §6) |
| 4–6 | nits | Which ` — was: ` is cut; the sweep's event items' `Lifts:`; a line cite | Cut at the first; `Lifts: Drop the gate.` is stated in §3.2; `:1857` |

### 0.19 Convergence round 12: Sonnet on draft 21 (draft 22)

Sonnet found no blockers, 3 should-fix and 3 nits; verdict NOT CONVERGED. It also confirmed that a v2.2 reader ignores a new preamble line, because `parse_board` reads only item lines (ledgerboard.py:947).

| # | Sev | Finding | Change |
|---|---|---|---|
| 1 | should-fix | `Person:` wasn't tied to the decision lift, so a `decision (Bob)` item on Paul's board would pass | `decide_lift` refuses when the base board's `Person:` differs from the gate's person, and a board with no `Person:` takes ordinary review. "One person per board" becomes a checked rule. Reassign stays consistent: b's item goes on b's board (§6, §3.2). |
| 2 | should-fix | No step adds `Person:` to the existing boards, and the severity of a missing one was unstated | Each consumer's board gains its `Person:` line in its v2.3 vendor PR (step 0), and each roster board at its remodel (step 5). A missing one is ℹ, because the fallback is ordinary review (§6, §7.2) |
| 3 | should-fix | Open entries with an unknown Status word (about 70 in ShiftLead) had no owner once `migrate` stopped on them | For an **open** entry, `migrate` sets `Open` and copies the old value verbatim into a Log line, and lists each one in the dry run for the remodel to review. It stops only on an archived entry's unknown word (§2.2, §7.3) |
| 4–6 | nits | The verbatim-copy line had no shape; a re-added event name on a reopened entry; §8 numbering | `- D: was <value>`, with the `note:` rule; the clause is added; §8 is reordered |

### 0.20 Convergence round 13: Fable on draft 22 (draft 23)

Fable found no blockers, 3 should-fix and 4 nits, all in round 12's `Person:` seam and the migration plan; verdict NOT CONVERGED. It re-verified every code citation in the draft (32 in the module, plus SPEC and both consumers). It also confirmed that setting `Open` changes no reader's pickability.

| # | Sev | Finding | Change |
|---|---|---|---|
| 1 | should-fix | For a decision item, a board with no `Person:` still let `decide_lift` run and pass byte-equality, reopening the hole fix 1 closed | A carve-out condition **(a0): the base board declares `Person:`**. Without it, the carve-out doesn't apply (§6) |
| 2 | should-fix | Coverage ignored `Person:`, so an item on the wrong person's board covered a gate it could never lift | An item covers a gate only when its board's `Person:` matches the gate's person. The board check flags a mismatched `decide` item. The sweep files on the roster board whose `Person:` matches, otherwise it files an `act` saying "decision (b) has no board" (§3.2) |
| 3 | should-fix | Roster repos' v2.5 migration wasn't scheduled | Step 6: each roster repo bumps its pin to the v2.5 release in one PR with `migrate` and the §7.3 judgment, in step 5's order (§7.2) |
| 4–7 | nits | `was ` isn't reserved; pickability neutrality is unstated; §0.19's step-0 wording; "b's board" | `was ` is reserved, and the moot `note:` clause is dropped; the neutrality is stated with citations; the wording is aligned; b's board is the roster board whose `Person:` is b |

### 0.21 Convergence round 14: Sonnet on draft 23 (draft 24)

Sonnet found no blockers, 2 should-fix and 2 nits; verdict NOT CONVERGED. It confirmed that the cross-repo coverage needs nothing a sweep can't read, and that no real note starts with "was".

| # | Sev | Finding | Change |
|---|---|---|---|
| 1 | should-fix | "The roster board whose `Person:` is b" isn't one board: a person owns several | **The person's board** is defined as one deterministic pick: this repo's own board if its `Person:` matches, otherwise the first matching board in the consumer's fixed roster order. Filing and reassign use it. *Covering* accepts an item on **any** board whose `Person:` matches (§3.2) |
| 2 | should-fix | The `act` "decision (b) has no board" had no key and no re-file rule | Keyed `Context: TD-n decision (b)`, kind `act`. The sweep files it only when no item with that key and kind is open, or was closed within the re-ask interval. It reads the board's archive for closed items, so no state is kept (§3.2) |
| 3–4 | nits | `was ` is common English ("was rebased onto main"); the module has no roster, so it can't refuse a b with no board | The shape becomes `- D: was: <value>`, and the reserved prefix is `was:`; "the consumer's writer refuses" |

### 0.22 Convergence round 15: Fable on draft 24 (draft 25)

Fable found no blockers, 1 should-fix and 4 nits; verdict NOT CONVERGED. It re-verified every module citation. It also confirmed that the board archive (`docs/user_attention_archive.md`) carries `Closed:` dates that the sweep can read, and that the `was:` shape keeps the note lift idempotent.

| # | Sev | Finding | Change |
|---|---|---|---|
| 1 | should-fix | "The consumer's fixed roster order" isn't fixed or shared. agent-cadence's roster is a machine-local, append-only file read in file order (nudge_user_attention.py:805). ShiftLead's is its own list followed by the imported one (hosts.py:50, :84). So two machines, or the two consumers, could pick different boards | The pick is a property of the boards, not of a machine: this repo's board if its `Person:` matches, otherwise the matching board with the **lowest repo name** (`owner/name`, ASCII order). The "two machines write nothing new" claim is qualified: it holds when their rosters hold the same boards, and a board missing from one roster is the already-admitted "missing board counts as not covering" case (§3.2) |
| 2–5 | nits | `— was:` recursion wording; a missing board archive; the `forge.py` citation; a typo | The inner Status is one verbatim `was:` line up to its own first ` — was: `, and the rest recurses; a missing archive reads as nothing closed; the citation is updated to :406-412; fixed |

### 0.23 Convergence round 16: Sonnet on draft 25 (draft 26)

Sonnet found no blockers, 1 should-fix and 1 nit; verdict NOT CONVERGED. Both are in round 15's fix.

| # | Sev | Finding | Change |
|---|---|---|---|
| 1 | should-fix | "Lowest repo name" had no defined key. Both consumers name a roster repo by its **checkout directory's basename**, lowercased, and use `owner/name` only to disambiguate a collision (agent-cadence ledger.py:19, :318; ShiftLead ledger.py:775, :1045). A basename is the clone's directory name, which differs between machines, and a local-only repo has no origin. | The pick key is defined once: the **lowercased origin slug** `owner/name`, compared bytewise. A board with no readable origin sorts after every slugged board, by lowercased basename. The "same pick everywhere" claim is qualified to boards with an origin. That covers every board today, since all are cloned from a forge (§3.2) |
| 2 | nit | The id written in `<repo>#TD-n` and `; board <repo>` must be one the resolver accepts unambiguously | The writer emits `owner/name` whenever the basename isn't unique on its roster (§3.2) |

### 0.24 Convergence round 17: Fable on draft 26 (draft 27)

Fable found no blockers, 2 should-fix and 4 nits, both should-fix being consequences of round 16's wording; verdict NOT CONVERGED. It re-verified every citation the fix depends on, and confirmed that the three vendored copies are still byte-identical.

| # | Sev | Finding | Change |
|---|---|---|---|
| 1 | should-fix | The pick key's derivation was undefined, and the consumers derive keys differently today: agent-cadence keeps the host (`forge.py:132`, `nudge:1152`), and ShiftLead keeps the whole URL (`ledger.py:769`) | A pure module function, **`origin_key(url) -> str | None`**, takes a string and returns a string or none, so it needs no git. It keeps the host and every path component, lowercased, with `.git` and trailing `/` stripped, and handles ssh, https and `file://` forms. Both consumers call it. Fixtured (§3.2) |
| 2 | should-fix | "The id always resolves to exactly one repo" held only on the writing machine: a bare basename resolves differently elsewhere, and silently to the wrong repo | The writer emits the origin's path (`owner/name`, or deeper for a nested group) **whenever the origin is readable**, and a bare name only for a repo with no origin. The id grammar allows one or more `/`-separated components (§3.2, §4.1) |
| 3–6 | nits | `decide_lift` had no `Person:` input; the tripwire's roster test is machine-dependent; the sweep's scope was unstated; `<host>` had no token grammar | `board_person` added to the signature; the tripwire accepts `; board <repo>` when it is well formed and not this repo, and the sweep's audit is the backstop; the sweep runs in a repo over its own ledger, through its pin; `<host>` follows the `who` token rule |

### 0.25 Convergence round 18: Sonnet on draft 27 (draft 28)

Sonnet found no blockers, 2 should-fix and 4 nits; verdict NOT CONVERGED. It confirmed that both consumers' `_find` already resolve multi-component ids by suffix (agent-cadence ledger.py:318, ShiftLead ledger.py:775), so ids with nested groups need no consumer change.

| # | Sev | Finding | Change |
|---|---|---|---|
| 1 | should-fix | `file://` and plain-path origins counted as readable, but their key is machine-specific and the id they produce breaks the `<repo>` grammar | A **readable origin** is an ssh or https URL with a host and a path that satisfies the `<repo>` grammar. `origin_key` returns none for `file://`, plain paths and a failing path, so the repo counts as having no origin (§3.2) |
| 2 | should-fix | `origin_key` and the multi-component grammar weren't in any release or in §7.4 | Both are in v2.4, and §7.4 lists their fixtures |
| 3–6 | nits | A repo named `.github` fails the leading-`.` ban; ids omit the host (same `owner/name` on two forges); userinfo and port in URLs; a deeper repo can shadow a shallow one under suffix matching | The ban is narrowed to `.` and `..` components and a leading `-`, since traversal is the risk; the host limit is stated (an ambiguous id is unresolved, which fails safe); userinfo and port are stripped; shadowing is accepted, and an exact-path match is preferred over a suffix match |

### 0.26 Convergence round 19: Fable on draft 28 (draft 29)

Fable found no blockers, 1 should-fix and 2 nits; verdict NOT CONVERGED. It judged every round-18 fix sound, found nothing new in a whole-design pass, and expected the next round to converge.

| # | Sev | Finding | Change |
|---|---|---|---|
| 1 | should-fix | The id text wasn't the same on every machine unless the writer lowercased it. Two clones can carry differently cased origins, and `item_key` (ledgerboard.py:901) and the tripwire compare text, so two machines could each file the same item | The writer emits the **lowercased** origin path, which is the path part of `origin_key`. `<repo>` in ids, Context keys and the tripwire compares case-insensitively. Fixtured (§3.2) |
| 2–3 | nits | `origin_key`'s return type; the consumer-side resolver and writer work wasn't scheduled | `-> str \| None`; steps 3 and 4 each adopt `origin_key`, emit the origin path in ids, and prefer an exact path match in `_find` |

### 0.27 Convergence round 20: Sonnet on draft 29. CONVERGED (draft 30)

Sonnet found no blockers and no should-fix findings, so the alternating review loop ends here, after 20 rounds (10 Fable, 10 Sonnet). It confirmed that the case-insensitive `<repo>` compare doesn't touch `item_key`, so no major release is needed. Its three nits are folded in:

| # | Nit | Change |
|---|---|---|
| 1 | The draft never said `item_key` stays byte-exact | Stated in §3.2, with a §7.4 fixture: two lines differing only in `<repo>` case have different `item_key`s |
| 2 | The lowercased-id fixture had no module function to run against | A pure `origin_path(url) -> str \| None` (the path part of `origin_key`, lowercased). Both consumers' id writers call it, and the fixture runs against it |
| 3 | The Context-ref dedupe is case-sensitive | It folds case on `<repo>` in the v2.4 `REF_TD_RE` tightening |

### Your decisions, 2026-10-31

- **The pick window is accepted.** Every new design entry an interactive session files starts with `decision (<person>)`, where `<person>` is whoever is driving the session, never a hard-coded name. Filed as **agent-cadence TD-212** (merged): the cadence rule for every user.
- **ShiftLead's Hold is removed.** Filed as **shiftlead#TD-1296** (PR #2772, merged): design-first, for the designer.
- **The host event log** is **shiftlead#TD-1295**, design-first and blocked on your decision until this design's event model is agreed.

### On draft 1 (unchanged unless noted)

| # | Question | Answer |
|---|---|---|
| 1 | An "upgrade ledgerboard" answer option? | No. Under v2.2, an unreadable gate is a `blocked-item` error on a changed entry, so the merge gate refuses it until the repo vendors the new release. *(Draft 6: the minor pin is dropped, because it would make v2.x readers read the ledger as v1.)* |
| 3, 4 | Status: free text? Standard values? Extensible? | A closed set: `Open`, `Resolved`, `Superseded`, `Dropped` ("OBE"). Notes move to the Log. A new word is a format PR. |
| 5 | Taken by vs Id take | `Taken by` retires in favour of `Id take` (agent-cadence TD-188). TD-188's `decision (Paul)` is out of date and can be lifted now. |
| 6 | Blocked-by notes field? | No: the body sections and the Log hold that prose. |
| 7 | Priority: defined? Critical? | Defined but never checked; an unknown value ranks below Low. `check()` will flag it. No Critical: urgency is the rank's job. |
| 9 | `run:` | Dropped (your call). A "TD is done" event is an id. |
| 10 | Is `Event` defined here or in ShiftLead? | Here: the gate, the section, the check types, and `check()`'s refusals. The consumers run the checks. |

---

### 0.28 Your answers on draft 30 (draft 31)

| Question | Answer |
|---|---|
| `Kind` (§2.3) | (i): a consumer field, its vocabulary prescribed by cadence.md |
| Item keys under `fmt` (§6) | (a): rewrite only the lines whose key doesn't change |
| The `Hide until` key exception (§8 #14) | strip it from `item_key` in v2.3 |
| Who merges, and the 30 days (§7.3, §4.4) | each team's techlead; a team pauses other work until its rewrite merges; 30 days stands |
| Repo order (§7.3) | agent-cadence and ShiftLead first, run and tested in use, then the other consumer repos |

Then agreed and written in (draft 32): **the writers live in ledgerboard** as `ledger.py` and `board.py`, file-level and git-free (§1.1); **boards name their people** (`People:`), every answer records who gave it, and a board says who may answer (`owner` or `any`, §6.2). Answered without a change: snooze keeps two dates (`Hide until` beside the real `Due`, as a defer date beside a due date), and rank stays the format's rank file, not a field. Agreed since: each team's techlead merges its remodel PRs, a team does no other work until its rewrite has merged, and 30 days stands.

### 0.29 Sonnet on draft 32's two changes (draft 33)

Sonnet found 1 blocker, 6 should-fix and 3 nits; verdict NOT CONVERGED. It confirmed by running the module that `Decided: Go (by Paul) (D).` reads as decided under v2.2, that `item_key` strips it whole, and that agent-cadence's carve-out (which compares item keys) still passes.

| # | Severity | Finding | Verified | Change |
|---|---|---|---|---|
| 1 | blocker | Vendored `ledger.py` and `board.py` would collide with both consumers' files of those names, and one file can't import the module both as `ledgerboard` and as `sessionorc.ledgerboard` | yes (sessionorc imports `from sessionorc import ledgerboard`) | ledgerboard ships a **package**, `ledgerboard/`, with relative imports, so the same bytes work at top level and as a subpackage (§1.1) |
| 2 | should-fix | Step 0 copied "three files" at v2.3, but `ledger.py` ships in v2.4; AGENTS.md and README weren't in the boundary change | yes | v2.3 vendors the module and `board.py`; AGENTS.md and README change with the package (§1.1, §7.2) |
| 3 | should-fix | "The writer opens a tool PR" contradicted git-free writers, and no writer action covered a host's event or `until` lift, or a cross-repo lift | yes | The consumer opens the PR; one action, `ledger.py lift`, writes every lift (§1.1, §6) |
| 4 | should-fix | agent-cadence's `ledger.py` refuses against `origin/<default>` and the roster, and `renumber`/`move` scan with `git grep` | yes (ledger.py:947-1008, :1218, :1314) | Refusal against base text (`--base <dir>`), `--ledger`, `--also <files>`; which commands move is stated (§1.1) |
| 5 | should-fix | A static `--resolved` map can't serve supersede chains discovered mid-run | yes | The command line exits 3 with `needs: <ids>` and is re-run; in-process it takes the callback (§1.1) |
| 6 | should-fix | Event items had no answerer rule once `Person:` was gone; a stale 5-argument signature; condition (b) lacked `(by …)` | yes | Anyone on `People:` answers an event item; signature and (b) fixed (§6) |
| 7 | should-fix | The `(by …)` parse was undefined: `BoardItem.decided`'s shape, a historical `(by Friday)`, the read-back check, `decided_line()` | yes (ledgerboard.py:1179, :1255) | `decided` keeps `(label, date)`, a new `decided_by`; only a final `(by <person>)` splits; the read-back and `decided_line` take `by` (§6.2) |
| 8–10 | nits | narrow routes for a teammate on an `any` board; v2.3's `decide` is board-only; a two-file write needs a failure rule | — | Stated (§6.2); stated (§1.1); write both or neither (§1.1) |

### 0.30 Fable on draft 33 (draft 34)

Fable found no blocker, 4 should-fix and 3 nits; verdict NOT CONVERGED. It confirmed Sonnet's fixes hold: nothing in the module shadows `ledger` or `board`, ShiftLead's packaging picks up a subpackage unchanged, and the carve-out can compute `decide_lift` from the PR's base text (check_cadence.py:1646-1686).

| # | Severity | Finding | Verified | Change |
|---|---|---|---|---|
| 1 | should-fix | The package renames the one file every header and byte check reads, and step 0 named none of them; a stale single file beside the package is silently ignored | yes (`vendor_ledgerboard.sh` in both, `seams.py`, `fixtures/run.py`) | Each reader listed in §1.1; vendor scripts remove the old file; step 0 moves them |
| 2 | should-fix | `--base` collapsed today's two-level refusal (pre- vs post-write, both under `--since`'s `old`) | yes (ledger.py:923-931, :997-1008) | The refusal compares post- with pre-write flags, both under the passed base as `old` |
| 3 | should-fix | `lift` had no source for the check type and no refusal matrix, so a host lift could be written in the person shape | yes (§2.2's shapes) | Exact input matrix; the check type is read from the Event section; `until` writes `date reached` |
| 4 | should-fix | The wrapper's own refusals ran before the write, but the writer now owns the write | yes (ledger.py:443, :589-614, :975) | `--plan` on every write action |
| 5–7 | nits | `python3 -m` needs `sys.path`; only the writer enforces the `set` route on an `any` board; "gaining `Decided:`" undefined for a re-answer | yes (launcher/words.py) | The wrapper is the command line; stated; base must have no `Decided:` |

### 0.31 Sonnet on draft 34 (draft 35)

Sonnet found no blocker, 3 should-fix and 2 nits; verdict NOT CONVERGED. It confirmed the module is safe as `__init__.py` (no `__name__`, `__file__` or `sys.modules` use), and that the carve-out's commit and direct-commit checks match §6 (c)–(d).

| # | Severity | Finding | Verified | Change |
|---|---|---|---|---|
| 1 | should-fix | The list of the old file's readers missed agent-cadence's `sync.sh` payload and `RETIRED_FILES`, `launcher/words.py`, `test_cadence_hooks.sh` and the README table | yes (sync.sh:75, :100; words.py:928; test_cadence_hooks.sh:289) | Added; the package files are listed one per line and the old file is retired in the same sync (§1.1) |
| 2 | should-fix | `lift` had no rule for who may be `--by`, and the ledger writer has no board | yes (doc) | `--people` and `--answered-by`, defaulting to the gate's person; host only with evidence or `until` (§1.1) |
| 3 | should-fix | The merge gate's `any`-board `by` check would read another repo's board, making its verdict machine-dependent | yes (doc, §3.2) | Outside a carve-out lift, `by` must be the gate's person; a teammate's cross-repo lift takes ordinary review (§3.1, §6.2) |
| 4–5 | nits | `item_record` lacked `decided_by`, and the `(by …)` reading change wasn't named as an exception; `lift` and `decide_lift` could drift | yes (ledgerboard.py:1039, :1162, :1206) | Named, with a fixture; one pure `lift_gate` both use (§1.1, §6.2) |

### 0.32 Fable on draft 35 (draft 36)

Fable found no blocker, 3 should-fix and 2 nits; verdict NOT CONVERGED. It re-verified the previous rounds' fixes in code (the two-level refusal, the wrapper refusals behind `--plan`, the carve-out's commit checks, `RETIRED_FILES`).

| # | Severity | Finding | Verified | Change |
|---|---|---|---|---|
| 1 | should-fix | §3.2 still said "one person per board … until a second person appears" | yes (doc) | Rewritten to point at coverage and §6.2 |
| 2 | should-fix | Nothing named where `by` comes from; agent-cadence's only identity is git `user.name`, which §3.1 rejects | yes (board_edit.py:23-24, :152; sessionorc/ledger.py:264-266) | Defaults to the one name on a one-person board; otherwise the consumer's attested person; never `user.name` (§6.2) |
| 3 | should-fix | "The board check" had no home, and `parse_board` can't carry a preamble value | yes (ledgerboard.py:939) | `board_people`, `answered_by` and `board_problems` named, with their releases and callers (§6.2) |
| 4–5 | nits | refuse vs flag disagreed between §3.1 and §6.2; no `by` rule for a person-shaped event lift outside the carve-out | yes (doc) | Flag in both; any person token, review the backstop (§3.1) |

Draft 36 also adds §1.2 (your go, 2026-11-02): the next id, the sweep's decisions, the lift-PR verdict and the "needs you" list move into the module as pure functions.

### 0.33 Sonnet on draft 36 (draft 37)

Sonnet found no blocker, 4 should-fix and 3 nits, all in §1.2; verdict NOT CONVERGED. It confirmed each function can be pure, that the release placement works, and that nothing in §0.29–§0.32 needs reopening.

| # | Severity | Finding | Verified | Change |
|---|---|---|---|---|
| 1 | should-fix | `lift_pr_verdict`'s inputs couldn't carry the subject, file list, commit count or this repo; the ledger is a directory; the tripwire also covers the `set` route | reasoned (§6, §3.1) | Full signature and result; `tripwire` separate, run on every PR that removes a decision gate |
| 2 | should-fix | `needs_you(board, today)` couldn't express agent-cadence's classes and order or ShiftLead's pre-due view | yes (nudge_user_attention.py:249-260, :344-362; cli.py:1694; src/shiftlead/ui/inbox.py:1196) | Classes, one order, a `horizon` |
| 3 | should-fix | `sweep()` named no board, had no close rule, couldn't do the board pick, and had no slot for `until` lifts | reasoned (§3.2) | Output keyed by board; boards carry origin and basename; a close rule; `lifts` |
| 4 | should-fix | The `Id take`/`Taken by` comparison against the counter's takes had no owner | yes (ledger_next_id.py header) | `judge_takes` in the module; SPEC defines the take's body |
| 5–7 | nits | `next_id`'s `LAST` handling, id reading and newer-major refusal; ShiftLead's own id reads are being removed (TD-971); mixed clocks in the sweep | yes (ledger_next_id.py:61-63, :119-135, :571; TD-971) | `ids_held`, warnings, refusal; the row says ShiftLead needs no step; two `today`s |

### 0.34 Fable on draft 37 (draft 38)

Fable found no blocker, 5 should-fix and 2 nits, all in §1.2; verdict NOT CONVERGED. It confirmed the earlier fixes against the code (`LAST` handling, `FormatTooNew`, the carve-out's commit checks, `id take` already in `CADENCE_FIELDS`).

| # | Severity | Finding | Verified | Change |
|---|---|---|---|---|
| 1 | should-fix | `judge_takes` accepted `Taken by` until v3.0, keeping the weaker check alive past TD-188's step 4 | yes (agent-cadence TD-188 Fix 4) | A consumer transition flag, dropped at step 4; v3.0 is only about reading old files |
| 2 | should-fix | `judge_takes` couldn't judge a doubly given id; take parsing stayed in the consumer | yes (ledger_next_id.py:270-277, `setdefault`) | `takes` keeps every take; `parse_take` in the module |
| 3 | should-fix | `needs_you`'s order put fyi before watch, `bad_due` had no place, and `horizon` couldn't express ShiftLead's modes | yes (nudge_user_attention.py:344-369; src/shiftlead/ui/inbox.py:1751-1790) | agent-cadence's order stated; a signed `days`; `horizon` dropped, consumers cut the list |
| 4 | should-fix | The close rule would close a parent snapshot item whose parent doesn't carry the gate | reasoned (§6) | Closed only when neither the Context entry nor any listed part carries it; this repo's entries only |
| 5 | should-fix | Coverage was computed in three places | reasoned (§3.1, §3.2, §6) | One `covers()` all three call |
| 6–7 | nits | the newer-major refusal belongs in `ids_held`; passed events' lifts came from elsewhere than `until`'s | yes (ledger_next_id.py:130) | Moved; `sweep().lifts` carries every host lift |

### 0.35 Sonnet on draft 38 (draft 39)

Sonnet found no blocker, 6 should-fix and 5 nits, all in §1.2's seams; verdict NOT CONVERGED. It confirmed §0.33–§0.34's fixes against the code.

| # | Severity | Finding | Verified | Change |
|---|---|---|---|---|
| 1 | should-fix | `lifts` had no slot for evidence or kind | reasoned (doc) | `{id, gate, kind, evidence}` |
| 2 | should-fix | `covers()` couldn't see the parent, and the `kept waiting` suppression isn't coverage | reasoned (§3.2) | `covers()` takes the entry text and returns states; the sweep applies `kept waiting` |
| 3 | should-fix | The close rule would close an answered (`Decided:`) item after its lift; broken-check and no-board items never closed on recovery | reasoned (§6) | Never closes a decided item; each kind closes when its own condition clears |
| 4 | should-fix | `judge_takes` lacked branch, default, the new ids and a return type; `host` was dropped | yes (ledger_next_id.py:310-368, :40-41) | Full signature, `(fails, warns)` with today's kinds |
| 5 | should-fix | §4.4, §3.2's opening and §8 #7 still called the sweep a consumer script | yes (doc) | Reworded; the host filters `lifts` against open PRs and files the "lift was closed" item |
| 6 | should-fix | The merge gate's coverage verdict had no pure function | reasoned (§6) | `uncovered_decisions()`; `tripwire` added to step 3 |
| 7–11 | nits | hidden rows for ShiftLead's `all` view; `days` at 0 and for decided; `bad_due`'s place is new; the `file` key, the audit item's key, one interval for two uses; reassign's close owner | yes (src/shiftlead/ui/inbox.py:1750-1790; src/shiftlead/cli.py:1688-1693; nudge_user_attention.py:344-361) | Each stated |

### 0.36 Fable on draft 39 (draft 40)

Fable found no blocker, 3 should-fix and 6 nits, all in the sweep's seams; verdict NOT CONVERGED. It confirmed §0.35's six fixes, in the text and in code.

| # | Severity | Finding | Verified | Change |
|---|---|---|---|---|
| 1 | should-fix | Whether a `decided` item covers was unstated: either a twin item or a dead re-ask | reasoned (§3.2, §6) | `open` and `decided` cover; the consumer acting on a non-lifting answer closes the item, and `kept waiting` governs the re-ask |
| 2 | should-fix | The close rule missed the sweep's own `decide` item; the reassign's close was given to a git-free writer | reasoned (§1.1, §3.1) | Added; the consumer closes a's item, the sweep is the cross-repo backstop |
| 3 | should-fix | The host's "lift was closed" item was said to close by the sweep, which didn't list it | reasoned (§4.4) | Added to the close rule |
| 4–9 | nits | a snoozed decided item left the work order; board naming and "own board"; "the sweep" doing forge work; §7.1 missing `board_people`, `board_problems`, `answered_by`; ShiftLead paths are `src/shiftlead/`; `ids_held` skips HTML comments | yes (ledgerboard.py:1142-1160; src/shiftlead/ui/inbox.py:1750; ledger_next_id.py:112) | Each fixed |

### 0.37 Sonnet on draft 40 (draft 41)

Sonnet found no blocker, 1 should-fix and 4 nits; verdict NOT CONVERGED. It confirmed §0.36's fixes and the id-counter seams against the code.

| # | Severity | Finding | Verified | Change |
|---|---|---|---|---|
| 1 | should-fix | The `; board <repo>` audit item is filed after its gate is gone, so the "gate gone" close would close it at once and re-file it every run | reasoned (§3.1, §1.2) | Its own close condition, and a fixture |
| 2–5 | nits | "open" meant two things in the tripwire; §6 hid decided items while §1.2 didn't; a past-due watch item had two classes; archived entries in `sweep()`; `boards`' type in `covers()` and `uncovered_decisions` | yes (nudge_user_attention.py:344-356) | "`open` or `decided`" stated; §6 aligned; date classes for to-dos only; open entries only; one tuple type |

### 0.38 Fable on draft 41 (draft 42)

Fable found no blocker, 3 should-fix and 3 nits, all in the sweep's close and coverage wording; verdict NOT CONVERGED. It confirmed §0.37's fixes and the id-counter and `needs_you` rows against the code.

| # | Severity | Finding | Verified | Change |
|---|---|---|---|---|
| 1 | should-fix | Two sweep sentences still said "open" alone, so a decided cross-repo item would get a twin | reasoned (§6) | "open or decided" in both, and in §3.2's table |
| 2 | should-fix | "decision has no board" never closed when the gate left without a covering item | reasoned (§3.1) | It also closes once the gate is gone |
| 3 | should-fix | The audit's close read open items only, so an answered item already closed and archived never satisfied it | yes (ledgerboard.py:874-876, :919, :939-950) | Reads closed and archived items; `covers()` gains `closed-decided` |
| 4–6 | nits | `tripwire`'s boards; which board event items go on; §7.1 missing `parse_take`, `origin_path`, `lift_gate` | yes (doc) | This repo's board only; event items on this repo's board; added |

### 0.39 Sonnet on draft 42 (draft 43)

Sonnet found no blocker, 1 should-fix and 3 nits; verdict NOT CONVERGED. It confirmed §0.38's fixes and the cited code (`ids_in`'s comment stripping, `overdue_days` at 0).

| # | Severity | Finding | Verified | Change |
|---|---|---|---|---|
| 1 | should-fix | The event items had no filing dedupe, so an "impossible" item answered `Rewrite the check` would get a twin | reasoned (§3.2, §6) | One filing rule for every kind of sweep item, with a fixture |
| 2–4 | nits | closed-line parsing had no named function, and whether `closed-decided` covers; how `tripwire` finds its board and what `repo` is without an origin; the cross-repo `lift` lacked `--people` | yes (ledgerboard.py:919, :939-950) | `parse_closed_items` (v2.4), coverage is `open` or `decided` only; stated; stated |

### 0.40 Fable on draft 43 (draft 44)

Fable found no blocker, 2 should-fix and 3 nits; verdict NOT CONVERGED. It confirmed §0.39's fixes and re-verified the cited code in both consumers.

| # | Severity | Finding | Verified | Change |
|---|---|---|---|---|
| 1 | should-fix | "Impossible" and "still waiting?" for one event share the key and kind, so an open still-waiting item would hold back the impossible one for 30 days | reasoned (§3.2, §4.2) | The item's identity adds its fixed head; still-waiting closes when the check turns impossible; fixture |
| 2 | should-fix | §1.1 said v2.3's `decide` doesn't check `People:`; §6.2 said it refuses a `by` not on it | yes (doc) | v2.3 checks `People:`; the gate's person and `Answered by:` wait for v2.4 |
| 3–5 | nits | a closed line's `Decided:` is hidden behind `Closed:`; the sweep's own closes opened the re-ask window; `results`' shape | yes (ledgerboard.py:742-743, :910-911) | Cut `Closed:` first; only an answer opens the window; keyed by `(TD-n, event)` |

### 0.41 Sonnet on draft 44 (draft 45)

Sonnet found no blocker, 2 should-fix and 3 nits; verdict NOT CONVERGED. It confirmed §0.40's fixes in code (`CLOSED_RE` swallows the rest of a closed line, ledgerboard.py:732).

| # | Severity | Finding | Verified | Change |
|---|---|---|---|---|
| 1 | should-fix | "Check broken" had no close when its gate went away | reasoned (§1.2) | Closes when the gate is gone too; a missing result changes nothing |
| 2 | should-fix | "Still waiting?" could be filed beside "impossible" or "broken" for the same check | reasoned (§3.2) | Only a `not yet` outcome files it; fixture |
| 3–5 | nits | the re-ask window dated from `Closed:`; the decision item has no fixed head; `until`'s boundary; `uncovered_decisions`' second check | reasoned | Dated from `Decided:`; its condition is "uncovered"; `today_utc ≥ D`; two branches |

### 0.42 Fable on draft 45 (draft 46)

Fable found no blocker, 1 should-fix and 2 nits; verdict NOT CONVERGED. It confirmed §0.41's six fixes and re-checked the cited code.

| # | Severity | Finding | Verified | Change |
|---|---|---|---|---|
| 1 | should-fix | An item answered `Keep waiting` stayed open and decided forever: never re-asked, and first in `needs_you` | reasoned (§1.2, §6) | `decide` closes an item whose answer only writes `kept waiting`; carve-out (b) allows it; fixture at +29 and +31 days |
| 2–3 | nits | one sentence still dated the window from `Closed:`; the cross-repo backstop named the wrong repo's sweep | reasoned | `Decided:`; this repo's sweep through `to_close` |

### 0.43 Sonnet on draft 46 (draft 47)

Sonnet found no blocker, 2 should-fix and 2 nits, both in §0.42's fix; verdict NOT CONVERGED. It confirmed in code that an answered-then-closed line keys the same as its open form (ledgerboard.py:732, :910-911).

| # | Severity | Finding | Verified | Change |
|---|---|---|---|---|
| 1 | should-fix | "Whole effect is `kept waiting`" also caught "Drop it" and "One more round", closing work orders | reasoned (§3.1, §6) | Two fixed waiting-only labels, `Keep waiting` and `Not yet`, tested by `waiting_only()`; fixture for "Drop it" |
| 2 | should-fix | The decide-and-close write had no form, its read-back reads open items only, and the carve-out didn't check the board line | yes (ledgerboard.py:1127-1137, :1179) | `edit_line(… close=)` with its form and read-back; carve-out (b) requires the head line to equal it byte for byte |
| 3–4 | nits | closing when no entry still carries the gate; the waiting-only write is two files | reasoned | Both stated |

### 0.44 Fable on draft 47 (draft 48)

Fable found no blocker, 2 should-fix and 1 nit; verdict NOT CONVERGED. It ran `item_key` on the open, open-decided and closed forms (equal), and confirmed `parse_decided` needs `Closed:` cut first.

| # | Severity | Finding | Verified | Change |
|---|---|---|---|---|
| 1 | should-fix | Carve-out (b)'s `today` was undefined: (c)'s is the UTC Log date, which may differ from the board's local `Decided:`, and a waiting-only answer may log nothing | yes (ledgerboard.py:1127; §3.1) | (b) uses the `Decided:` date; each date is windowed on its own |
| 2 | should-fix | `Lifts: Not yet` would both lift and close as waiting | reasoned (§6) | A waiting-only label can never lift: refused, flagged, tested first |
| 3 | nit | `close=`'s release | — | v2.4 |

### 0.45 Sonnet on draft 48 (draft 49)

Sonnet found no blocker, 1 should-fix and 2 nits; verdict NOT CONVERGED.

| # | Severity | Finding | Verified | Change |
|---|---|---|---|---|
| 1 | should-fix | The local `Decided:` date was windowed like the UTC Log date, so anyone east of UTC answering in their morning lost the carve-out | reasoned (§3.1, §6 (b)) | A day's slack each side for the local date; fixtures at one and two days ahead |
| 2–3 | nits | whether the waiting-only close applies to items without a gate; §6.2 didn't tag `close=` as v2.4 | reasoned | Gate items only; tagged |

### 0.46 Fable on draft 49 (draft 50)

Fable found no blocker, 1 should-fix and 2 nits; verdict NOT CONVERGED. It checked §0.45's window arithmetic (sufficient even for UTC−12 across midnight).

| # | Severity | Finding | Verified | Change |
|---|---|---|---|---|
| 1 | should-fix | The unchanged board-alone carve-out passes any one-item board PR, so a hand-written `Decided:` on a gate item with an empty ledger diff skipped every (b) check | yes (check_cadence.py:1637-1642, :1669-1687) | From v2.4 any `Decided:` on a gate item goes through `lift_pr_verdict`; the old carve-out keeps gate-less edits; cross-repo items pass on (a0)+(b) |
| 2–3 | nits | `merged_at` before merge; a lifting answer can also log nothing | reasoned | Upper bound `created_at + 1`; "whenever `decide_lift` changes no entry" |

### 0.47 Sonnet on draft 50 (draft 51)

Sonnet found no blocker, 3 should-fix and 1 nit, all in how §0.46 narrows the old carve-out; verdict NOT CONVERGED.

| # | Severity | Finding | Verified | Change |
|---|---|---|---|---|
| 1 | should-fix | `classify_direct`, shared by the PR row and the direct-commit audit, would still pass a gate item's `Decided:` before `lift_pr_verdict` ran | yes (check_cadence.py:1616-1670) | `classify_direct` defers such an item; fixtures for the PR and the direct commit |
| 2 | should-fix | The cross-repo path never required the board alone | yes (check_cadence.py:1618, :1659) | `files == [board]`, on that path and the gate-less one |
| 3 | should-fix | The cross-repo path checked less than the writer does | reasoned (§1.1, §6.2) | The gate's person on `People:`, and `by` equal to it under `owner` |
| 4 | nit | ShiftLead's `agent_ids.py:184` reads the old file as a literal | yes | Added to the list, with a grep step |

### 0.48 Fable on draft 51 (draft 52)

Fable found no blocker, 2 should-fix and 2 nits; verdict NOT CONVERGED. It confirmed §0.47's fixes in code.

| # | Severity | Finding | Verified | Change |
|---|---|---|---|---|
| 1 | should-fix | A direct commit has no PR to defer to, so a pushed gate-item `Decided:` would still pass | yes (board_edit.py:43-46; check_cadence.py:1616-1647) | The audit classes it `fail`; the wrapper never direct-pushes such a decide |
| 2 | should-fix | A board with no `People:` would refuse every decide, though roster boards gain it only at their remodel | yes (procedures/attention.md:72) | No `People:`: `--by` required, grammar only, the write proceeds, lifts go to review |
| 3–4 | nits | ShiftLead reads agent-cadence's layout through its pin; a cross-repo waiting-only answer needs no tool PR | yes (look_home.py:165) | Pin bump and vendor PR are one PR; stated |

### 0.49 Sonnet on draft 52 (draft 53)

Sonnet found no blocker, 2 should-fix and 3 nits; verdict NOT CONVERGED. It confirmed §0.48's fixes in code and found no further reader of the old file.

| # | Severity | Finding | Verified | Change |
|---|---|---|---|---|
| 1 | should-fix | Nothing closed an item after its lifting answer lifted, so it sat first in `needs_you` until archived | reasoned (§1.2, §6) | `closes()`: the decide write also closes on a lifting answer for this repo's entry; the sweep closes a cross-repo one once the gate is gone |
| 2 | should-fix | `decide_lift` had no defined behaviour for a board with no `People:` | reasoned (§6, §6.2) | `board_people=None` skips the people checks but keeps the gate's-person rule; (a0) stops the carve-out first |
| 3–5 | nits | the cross-repo person test for an event gate; a repo with no `People:` can't take gates; ShiftLead's step 0 lacked the pin bump | reasoned | Decision gates only; stated; added |

### 0.50 Fable on draft 53 (draft 54)

Fable found no blocker, 2 should-fix and 3 nits, both should-fix knock-ons of §0.49's close; verdict NOT CONVERGED. It confirmed the decided-and-closed line keys and diffs as one item (ledgerboard.py:901-915, :1131-1140) and that parent snapshots still close correctly.

| # | Severity | Finding | Verified | Change |
|---|---|---|---|---|
| 1 | should-fix | The tripwire needed a covering item at the head, but a same-repo lift now closes it, so the tripwire would fail every carve-out lift | reasoned (§3.1, §1.2) | Covering at the base, with a new `Decided:` at the head; fixtures |
| 2 | should-fix | A lifted-and-closed item opened the re-ask window, suppressing a re-added gate for 30 days | reasoned (§1.2) | Only a non-lifting answer opens the window; fixture |
| 3–5 | nits | `close=`'s two reasons; what "this repo's entry" means for `closes()`; the (a0) fixture's form | yes (check_cadence.py:1616-1647) | Stated |

### 0.51 Sonnet on draft 54 (draft 55)

Sonnet found no blocker, 2 should-fix and 2 nits, both should-fix in the tripwire's new test; verdict NOT CONVERGED. It confirmed the `set` route's shared-snapshot and cross-repo exceptions fit the new test, and that the re-ask window is consistent with the event items.

| # | Severity | Finding | Verified | Change |
|---|---|---|---|---|
| 1 | should-fix | The tripwire's `covers()` read the head only, but its test needs the base | reasoned (§1.2, §3.1) | Reads base and head; fixture |
| 2 | should-fix | The "no board item" exception was judged at the head, so closing a covering item without an answer passed | reasoned (§3.1) | No covering item at the base nor the head |
| 3–4 | nits | a base item already `decided` had no route; §3.2's `kept waiting` bullet was stale beside §1.2 | reasoned | Open or decided at the base, a new or changed `Decided:`; §3.2 points at §1.2 |

### 0.52 Fable on draft 55 (draft 56)

Fable found no blocker, 1 should-fix and 2 nits; verdict NOT CONVERGED. It confirmed §0.51's fixes and that `edit_line` already replaces an existing `Decided:` (ledgerboard.py:1162-1178).

| # | Severity | Finding | Verified | Change |
|---|---|---|---|---|
| 1 | should-fix | The `set by=` route's board write didn't close on a lifting answer, leaving a phantom work order | reasoned (§3.1, §6 (b)) | It writes through the same `edit_line(… close=closes())`; the sweep's backstop closes any lifted decided item, whoever filed it |
| 2–3 | nits | a no-`People:` board's lift and the tripwire; a stale event parenthetical in the cross-repo clause | reasoned | Stated (corrected in §0.53); removed |

### 0.53 Sonnet on draft 56 (draft 57)

Sonnet found no blocker, 2 should-fix and 2 nits; verdict NOT CONVERGED. It confirmed §0.52's backstop and `closes()` agree.

| # | Severity | Finding | Verified | Change |
|---|---|---|---|---|
| 1 | should-fix | §0.52 said the tripwire refuses a no-`People:` lift, but its own "no board item" exception accepts it | reasoned (§3.1, §6.2) | Accepted as `; no board item`, ordinary review; fixture expects the pass |
| 2 | should-fix | `set by=` writing through the two-file `decide` would lift twice, or lift parts `set` wasn't asked about | reasoned (§1.1, §6) | `decide --board-only`, never `decide_lift`; parent-snapshot fixture |
| 3–4 | nits | `closes()`' gate condition; "shared with other parts" | reasoned | Stated in both |

### 0.54 Fable on draft 57 (draft 58)

Fable found no blocker, 3 should-fix and 1 nit, all on §0.53's claim that a `set by=` PR could take the carve-out; verdict NOT CONVERGED.

| # | Severity | Finding | Verified | Change |
|---|---|---|---|---|
| 1–2 | should-fix | A `set by=` PR carries a ledger subject, and its ledger change differs from `decide_lift`'s whenever a parent's other parts are involved | yes (check_cadence.py:1675) | The claim is dropped: a `set by=` PR always takes ordinary review; only `board.py decide` is a carve-out lift. The shared-snapshot exception also tests the Context entry |
| 3 | should-fix | `board.py decide` on a no-`People:` board wrote no suffix, so the tripwire tripped | reasoned (§3.1, §6.2) | Every lift on such a board writes `; no board item`; fixtures for both routes |
| 4 | nit | `--board-only` wasn't in §1.1 or §7.1 | — | Described in §1.1, with the wrapper's sequence; v2.4 |

### 0.55 Sonnet on draft 58 (draft 59)

Sonnet found no blocker, 2 should-fix and 2 nits; verdict NOT CONVERGED. It confirmed §0.54's fixes across §1.1, §3.1, §6, §6.2 and §7.1.

| # | Severity | Finding | Verified | Change |
|---|---|---|---|---|
| 1 | should-fix | §7.2 never scheduled the `set by=` wrapper sequence, so turning the tripwire on would fail every `set by=` PR | yes (grep) | Added to steps 3 and 4, in the PR that turns the tripwire on |
| 2 | should-fix | The `set by=` route had no source for the answer label | reasoned (§1.1, §3.1) | `answer=<label>`, default `Go`, checked against the item's `Lifts:`; fixture |
| 3–4 | nits | "runs `ledger.py set`" vs `lift`; which of two covering items is written | reasoned | `set by=` calls `lift`; the entry's own item, else the lowest key |

### 0.56 Fable on draft 59 (draft 60)

Fable found no blocker, 1 should-fix and 2 nits; verdict NOT CONVERGED. It confirmed §0.55's fixes.

| # | Severity | Finding | Verified | Change |
|---|---|---|---|---|
| 1 | should-fix | `closes()` closed a shared parent-snapshot item after a single-entry `set by=`, silently losing the other parts' coverage | reasoned (§3.1, §6 (b)) | `closes(item, label, entries_after)`: a lifting label closes only when nothing listed still carries the gate; fixture asserts the item stays open |
| 2–3 | nits | the last part's lift writes an unchanged `Decided:`; ShiftLead's tripwire turns on with its pin bump, before its wrapper | yes (ShiftLead has no own `check_cadence.py`) | The tripwire accepts a new `Closed: … — lifted.` on a decided item; pin bump, wrapper and sequence are one PR |

### 0.57 Sonnet on draft 60 (draft 61): CONVERGED

Sonnet found no blocker and no should-fix; verdict CONVERGED. It confirmed `closes(item, label, entries_after)` behaves the same in §1.1, §3.1 and §6 (b) for a full lift, a shared snapshot and its last part, and that the release placements agree. Its four nits are folded in: the covering-item pick prefers this repo's board; a cross-repo covering item gets no board half; a shared snapshot's remaining parts are lifted by a re-answer; step 4's vendor line no longer repeats step 2.

### 0.58 Fable on draft 61 (draft 62): CONVERGED

Fable confirmed Sonnet's verdict: no blocker and no should-fix. It checked §0.57's four folds against §3.1, §3.2, §4.4 and the code (`edit_line` replacing a `Decided:`, ledgerboard.py:1169-1173; ShiftLead runs the pinned tree's `check_cadence.py`, `src/sessionorc/cadence.py:61`). Its two nits are folded in: a sentence's lost subject, and the close rule naming any `decide` item keyed to the entry and gate, whoever filed it.

**The second loop converged here:** thirty rounds on §1.1, §1.2 and §6.2 (§0.29–§0.58), with Sonnet and Fable both returning CONVERGED.

---

## 1. Principles

1. **One meaning, one place.** Anything that stops an entry from being picked lives in `Blocked by`. **[agreed]** The one exception is a consumer's short scheduling delay (ShiftLead's settling), which is never a hold.
2. **Pickable is derived from the text alone**, plus `today` and the cross-repo lookup that the caller passes in. No host's memory enters it, so every reader on every machine gets the same answer. **[agreed; draft 6 drops event results as an input]**
3. **Every gate has a deterministic way out.**
   - A decision is lifted by the person's answer.
   - `until` is lifted by the date.
   - An event is lifted by a mechanical check.
   - An id is lifted by the entry's archive.

   `check()` refuses a gate with no way out. A gate that is stuck, broken, impossible or waiting too long goes to the board through the gate sweep (§3.2). **[proposed, from your notes]**
4. **Header fields are one-line values that tools route on. The body holds prose, plus named sections of fixed shape that tools may read** (the `check:` line of an Event section, the Log's writer lines). Prose never goes in a field. **[proposed]**
5. **Writers, not hand edits.** Every edit goes through ledgerboard's own writers, `ledger.py` and `board.py` (§1.1), never a hand edit and never a consumer's own file handling (agent-cadence TD-206, ShiftLead TD-1286). **[agreed; the writers' home agreed 2026-11-02]**
6. **The module stays pure; the writers stay git-free.** `ledgerboard.py` is pure functions over text. `ledger.py` and `board.py` add file reading and writing and nothing else. Git, the network, the roster, forges, sessions, running checks, opening PRs and starting agents belong to the consumers. **[agreed, ADR; amended 2026-11-02]**
7. **Fail safe across versions.**
   - An old copy reads a new gate as an unreadable item. It keeps the block, and its merge gate refuses a PR that writes one. **[checked in code]**
   - **Every writer keeps what it cannot parse** (an unknown field, gate, section or Log prefix) **[agreed 2026-11-01]**:
     - its *content* survives verbatim: a field's name and value, an item's text, a section's text, a Log line;
     - its *placement* in the header follows canonical form, which puts unknown fields after known ones and normalises spacing (SPEC, *canonical form*);
     - text the canonical form cannot carry (a header line that is not a field) is **refused, never dropped**;
     - a writer edits only what it understands.
   - **Retired words are reserved forever.** No later release gives them a new meaning (§2.1). **[agreed 2026-11-01]**
   - Old forms become errors, never new meanings. The same bytes never mean two things under two releases.

### 1.1 The writers live in ledgerboard **[agreed 2026-11-02]**

Today each consumer has its own command-line writers over the module: agent-cadence's `ledger.py` (1,624 lines) and `board_edit.py`, and ShiftLead's `sessionorc/ledger.py` and `board.py` (about 2,000 lines together). Their file handling is format work that both need, and each wrote it its own way, so it is where the consumers drift. **ledgerboard ships the writers instead**, and every consumer vendors them with the module.

- **One package, vendored whole:** `ledgerboard/`, holding `__init__.py` (the pure module, today's `ledgerboard.py`, unchanged in role), `ledger.py` (the ledger writer) and `board.py` (the board and rank writer).
  - **Why a package:** both consumers already have files named `ledger.py` and `board.py` (agent-cadence's scripts, ShiftLead's `sessionorc/`), which become the wrappers below. Inside the package the writers import the module relatively (`from . import …`), so the same bytes work as a top-level package (agent-cadence: `import ledgerboard`, `python3 -m ledgerboard.ledger …`) and as a subpackage (ShiftLead: `from sessionorc import ledgerboard`, `from sessionorc.ledgerboard import ledger`). Existing `import ledgerboard` callers are unchanged.
  - Each file carries the release header. `release.sh`, `fixtures/run.py` (`--module` and `--check-header` take the package directory, load it as a package so relative imports work, and read `__init__.py`'s header) and each consumer's sync check every file in the package.
  - **Every reader of the old single file changes with it** (§7.2 step 0): the vendor scripts remove the old `ledgerboard.py` (Python would silently prefer the package beside it) and list each package file in the manifest; agent-cadence's `vendor_ledgerboard.sh`, `sync.sh`'s payload list (each package file listed on its own line, and `scripts/ledgerboard.py` added to `RETIRED_FILES` in the same sync, so a synced repo loses the stale file; the wrappers `scripts/ledger.py` and `scripts/board_edit.py` stay listed), `launcher/words.py`, the README's file-class table, `tests/test_ledgerboard_fixtures.sh`, `tests/test_sync_provenance.sh` and `tests/test_cadence_hooks.sh`; ShiftLead's `scripts/vendor_ledgerboard.sh`, `seams.py` (`LEDGERBOARD_COPIES`, the payload path), `doctor.py`, `agent_ids.py:184` (which reads the file as a literal for `CADENCE_FIELDS`, and would otherwise silently stop writing `Taken by`), `test_ledgerboard_fixtures.py` and the ruff exclude in `pyproject.toml`. Each consumer's step also greps for the literal `ledgerboard.py`, since this list was found by search and may not be complete (it also finds the vendored `tests/ledgerboard/run.py` and `MANIFEST`, and test seeds). **ShiftLead also reads agent-cadence's layout** through its pin (`scripts/look_home.py:165` copies the pinned tree's `scripts/ledgerboard.py`, and several tests seed that path), so its pin bump to the step-0 release and its vendor PR are one PR.
  - Each writer is both an importable library and a command-line entry point with the same actions. ShiftLead calls it in-process. The command line people and agents use is the consumer's wrapper (`agent-cadence run ledger.py …`); `python3 -m ledgerboard.ledger` works only with the package's parent directory on `sys.path`, so it is for tests and a person in that directory.
- **What a writer does:** reads the files, applies the module's edit, and writes the files back: an entry's file, the archive move (a write of the new file and a delete of the old one; git sees the rename at commit), `split`, `relink`, renumbering within the files it is given, a board and its archive, the rank file. It prints the commit subject the module gives and the paths it changed (`--json` for a machine). The read-only reports (`--pickable`, `--list`, `--summary`, `--check`) move too.
  - **Its refusal rule keeps today's two levels** (agent-cadence ledger.py:923-931, :997-1008). A write is refused when the **post-write** text has a `check()` flag the **pre-write** text doesn't. Both are checked with the same `old`: the base the consumer passes (`--base <dir>` on the command line; in-process, the `(ls, read)` pair agent-cadence's `git_io()` already yields), which `check()` uses for its scoping and its archive-loss flags, as `--since origin/<default>` does today. So a problem an earlier commit on the branch introduced never blocks an unrelated write, and archive loss is still caught.
  - **`--plan`** on every write action prints the changes (each path and its new text, or its deletion) and the subject as JSON, and writes nothing. The wrapper judges its own refusals on that plan before the write: the id checks against the counter and branch (ledger.py:589-614), prose waits (:443) and cross-repo refusals (:975). `migrate --dry-run` (§7.3) is this for `migrate`.
  - **Write both or neither.** A write that changes several files (a decide lift's board and ledger, an archive move, a renumber) writes each to a temporary file and renames them into place only when all are built. If a rename fails part way, the writer restores the files it already replaced and exits non-zero.
- **What it never does:** git, the network, the roster, a forge, a session. Whatever needs them is passed in:
  - **the next id:** `new --id TD-n` and `renumber … --id TD-n`. The consumer allocates it (agent-cadence's counter on origin);
  - **the ledger's path:** `--ledger <dir>`. The wrapper finds it (agent-cadence's `_toplevel()`, :659);
  - **files outside the ledger that name an id** (`renumber` and `move` rewrite their references): `--also <file>…`. The wrapper finds them (agent-cadence's `git grep`, :1314) and commits the result;
  - **cross-repo state:** the resolver, as `pickable()` already takes it. In-process it is the callback. On the command line, which ids are needed is known only mid-run (a supersede chain, §5), so the writer **exits 3 with `needs: <ids>`** (JSON with `--json`) and writes nothing. The wrapper resolves those ids and runs it again with `--resolved <file>` (a JSON map from `<repo>#TD-n` to its state, Status word and successor), until nothing is needed;
  - **who answered or lifted:** `--by <person>`, or `--by <host>` for a host's lift. The consumer has already checked that the session is person-started (§3.1); the writer records it and checks the shape;
  - **the date:** the writer reads the UTC clock for ledger dates and the local clock for board dates (§3), and takes `--today D` for tests and for `migrate`'s replays;
  - **`migrate`'s archive dates:** `--closed-dates <file>`, which the consumer builds from git (the archiving commit's date).
- **What the consumer keeps:** the id counter, branches, commits, PRs (including the tool PR in another repo, §6), the merge gate, attesting the session, resolving other repos, `git mv`, finding referencing files, locks and temporary worktrees (ShiftLead's `_EDIT` lock and temp-worktree flow, board.py:45, :267), the event runner and the gate sweep. A consumer's own `ledger.py` or `board_edit.py` becomes a thin wrapper that does those and calls ledgerboard's writer. Old command names keep working through that wrapper.
- **`board.py decide --board-only`** writes the board half alone (the `Decided:` line, closed per `closes()`), never `decide_lift`. The `set by=` route uses it: the consumer's wrapper runs `covers()` and picks the one covering item (this repo's own board first, then other boards in pick-key order; on a board, the item whose Context names the entry, else the lowest item key; the sweep's close rule tidies any other). When the only covering item is on another repo's board, the commit writes no board half and logs `; board <repo>`, and the audit's `act` item is the backstop (a fixture). A shared parent-snapshot item left open and unanswered keeps covering its remaining parts, and stays in the person's to-do; they are lifted by the person's answer through `board.py decide`, as any unanswered item's. *(Amended 2026-11-11, TD-067: `docs/plans/TD-067-shared-part-lift.md` — `--board-only` writes the line only when the answer closes the item; while a listed entry still carries the gate it writes nothing and reports `left_open`, where v2.4 to v2.6 wrote a `Decided:` that spoke for the parts the person had not answered.)* The wrapper then takes `answer=<label>` (default `Go`) and refuses a label not in that item's `Lifts:` (or `Go` when it has none), picks `lift`'s suffix flag, then runs `set by=` (which calls `ledger.py lift`) and `board.py decide --board-only` with the same label, in one commit. A fixture lifts an either/or item with its non-default label. Those are two writers, so "write both or neither" holds per writer only; a missing `Decided:` then trips the tripwire, which fails safe. A cross-repo item's board write is detected from its Context and needs no flag. It ships in v2.4.
- **One action lifts a gate:** `ledger.py lift TD-n --gate "<gate>" --by <who> …`. It removes the gate and writes one of §2.2's fixed `gate lifted` shapes, and is what every route calls: the person's `set by=` route (§3.1), the host's event and `until` lifts, and the cross-repo decision lift (for which the consumer passes the target board's `People:` and `Answered by:` as `--people` and `--answered-by`). `set --override` and the reassign stay `set`'s. Its inputs match the shapes exactly, and anything else is refused:
  - **a decision:** `--answer "<label>"`, with at most one of `--board <repo>`, `--no-board-item`, `--shared-item`; no `--evidence`;
  - **an event lifted by a person** (from a sweep item): `--answer "<label>"`; no `--evidence`;
  - **an event lifted by a host:** `--evidence "<repo>#<n>" | "<repo>@<sha>"`; no `--answer`. The check type is read from the entry's `**Event (name):**` `check:` line, never passed in;
  - **`until`:** neither flag; the writer writes `date reached` and refuses a date not yet reached.
  - **Who may be `--by`:** for a decision, `by` must equal the gate's person, unless the caller passes the board's `--people` and `--answered-by any`, when any listed person may answer. `board.py decide` passes its board's values; the `set by=` route passes none. For an event lifted by a person, `by` must be in `--people`, which is then required. `--by <host>` is accepted only with `--evidence` or on `until`. Fixtures cover each refusal.
  - **One implementation.** `lift`'s text edit is a pure module function, `lift_gate(text, gate, by, answer=…, evidence=…, suffix=…, today)`, and `decide_lift` composes it for each entry it changes, so the writer and the merge gate's byte-equality check can't drift. A fixture shows `lift`'s output equals `decide_lift`'s for each shape.
- **Tested here:** writer fixtures are a directory before, a command, and the directory after, plus the printed subject; they run in `fixtures/run.py` beside the module's.
- **The boundary moves.** ShiftLead's ADR (2026-10-12), and this repo's AGENTS.md and README, say ledgerboard holds "SPEC, the module and fixtures, nothing else". Both are amended: *SPEC, the module, the two file-level writers, and fixtures; never git, the network, the roster, forges, trackers, delivery, sweeps, sessions, or logic that knows either consumer.* The ADR is ShiftLead's, so its amendment is a ShiftLead PR that the techlead reviews. AGENTS.md and the README change in the same ledgerboard PR as the package. Both land before v2.3's release.
- **Releases.** The package and `board.py` ship in v2.3, built from agent-cadence's `board_edit.py` and ShiftLead's `board.py`, with v2.3's board work (`due`, `Hide until`, `People:`). `ledger.py` ships in v2.4, built from agent-cadence's `ledger.py` minus its git and roster code, with the gates, the Log, `lift`, `archive --dropped`, `set --override` and `migrate`. Each lands with fixtures for every action. **v2.3's `board.py decide --by` writes the board alone:** `Decided: … (by …)`, checking `by` against `People:` (§6.2) but not against the gate's person or `Answered by:`. The two-file decide lift, and its `People:`/`Answered by:` checks, arrive with `decide_lift` in v2.4.


### 1.2 More format logic moves into the module **[agreed 2026-11-02]**

The same test as §1.1: logic that decides what the text means, which both consumers would otherwise each write, belongs in ledgerboard. Each move below is a **pure module function**, so none changes the boundary. The consumer keeps the I/O around it.

| Move | In the module (pure) | Stays with the consumer | Today | Release |
|---|---|---|---|---|
| **The next id** | SPEC defines the counter: the branch `cadence/ledger-ids`, its one file `LAST`, and a take as one fast-forward commit whose body carries `by`, `branch` and `take`. `ids_held(files) -> set[int]` reads every id a ledger and archive hold (headings, entry file names, table rows, outside HTML comments, as today's `ids_in` does, ledger_next_id.py:112), and refuses files that declare a newer major (as `FormatTooNew` does today, ledger_next_id.py:130). `next_id(last: str \| None, ids, floor) -> (int, warnings)` is one above the highest of a numeric `LAST` (absent or non-numeric is ignored, with a warning), `ids` and the floor. `parse_take(subject, body)` reads one take commit (an id or a range, and its body fields). `judge_takes(new_ids, takes, entries, branch, default, accept_taken_by=False) -> (fails, warns)` is the merge gate's comparison of each new entry's `Id take` with the takes, returning `(kind, text)` pairs with today's kinds (ledger_next_id.py:310-368: a different branch, an id before the counter, an unhashed `by` per TD-195, and the rest), so the consumer keeps no judging of its own. `takes` is a list of `(ids, sha, date, by, branch, host, take)` records, every take kept, so a doubly given id is judged against all its takes and a failure names the other id's take (agent-cadence TD-188). `accept_taken_by` is the consumer's transition flag until TD-188's step 4, then dropped; it is not tied to v3.0, which is only when the module stops *reading* `Taken by` in old files. | The `ls-remote`, the fetch, the push and its retry, the `git log` of the counter's history, folding open PRs' ids into `ids` on a first take, and the fallback | agent-cadence's `ledger_next_id.py` (header, :61-63, :119-135, :571). ShiftLead's home is removing its own id reads in favour of that script, through its pin (shiftlead#TD-971), so ShiftLead needs no step of its own | v2.4 |
| **The gate sweep's decisions** | `sweep()` and `covers()`, specified below the table. | Reading roster boards on their origin, running the event checks (outcomes, passed ones with their evidence, come in as `results`), writing items and closes through `board.py` and lifts through `ledger.py lift`, the lift PRs and their idempotency (§4.4) | each consumer was to build its own (§7.2 steps 3, 4) | v2.4 |
| **The lift-PR verdict** | `lift_pr_verdict(base_tree, head_tree, files, subject, commits, created_at, merged_at, repo) -> {carve_out: bool, flags: [...], review: [...]}` (`merged_at` is none for a PR not yet merged, when every upper bound is `created_at + 1`): conditions (a0)–(d) of §6, `decide_lift`'s byte-equality, the `today` window. `base_tree` and `head_tree` map each ledger and board path to its text; `files` is the PR's changed paths; `subject` its commit subject (for `edit_action`); `commits` its commit count. A separate `tripwire(base_tree, head_tree, subject, repo) -> flags` (§3.1), whose `covers()` reads only this repo's own board and its archive, from both `base_tree` and `head_tree` (its test compares the two; a fixture fails a tripwire that reads the head alone), never another repo's (`base_tree` and `head_tree` map each path to its text; the board and archive paths are SPEC's fixed ones; `repo` is this repo's `origin_path`, or its basename when it has no readable origin, here and in `sweep`), runs on **every** PR that removes a `decision (person)`, the `set by=` route included, since that route is not a lift PR. | Fetching the PR's trees, file list, commits and dates from the forge, and acting on the verdict (agent-cadence's `check_cadence.py`, whose `_tool_pr_commit` and `classify_direct`, :1616-1686, read git today) | the rules were to be written into `check_cadence.py` (§7.2 step 3) | v2.4 |
| **The "needs you" list** | `needs_you(board, today) -> [(item, class, days)]`: every open item not hidden (`Hide until`; a `decided` item is never hidden, because it is a session's work order), each with one class (`decided`, `overdue`, `due`, `bad_due`, `undated`, `watch`, `fyi`; the four date classes are for to-do items only, and a watch or fyi item keeps its own class while still carrying `days`) and a signed `days` (positive overdue, negative days until due, none when undated), in one stated order: decided (oldest decision first, a session's work order), overdue (most first), dated (soonest first), bad_due, undated, then watch items the same way, then fyi (agent-cadence's order today, nudge_user_attention.py:344-361). `days` is 0 on the due date, which is `due`, not `overdue`; for `decided` it is the decision's age. Placing `bad_due` before undated is a new choice (today it sorts with undated). `decided` is the format fact; ShiftLead may still present an answered item as waiting rather than as needing the person. A view that must also show hidden items (ShiftLead's `all` mode and its "not shown" fold) reads `parse_board` with `BoardItem.hidden(today)`. Consumers cut the list from these fields: agent-cadence's start-of-session line (`surfaces_at_start`, :363-369), ShiftLead's `due`, `<n>d`, `next:<n>` and `all` modes (src/shiftlead/ui/inbox.py:1751-1790). | Escalation (agent-cadence's 14 days), every cut of the list (the SessionStart line, ShiftLead's modes), notifications and display | agent-cadence's nudge (nudge_user_attention.py:249-260, :344-362) and ShiftLead's `src/shiftlead/cli.py:1694` and `src/shiftlead/ui/inbox.py:1196` each decide this | v2.3, with `Hide until` |

**The sweep's functions** (v2.4):
- **`covers(entry_text, gate, boards, repo) -> [(board, item, state)]`**, with `boards` as `sweep()` takes them (below), is coverage, defined once (§3.2): the items that name the entry and gate, or name its parent (read from the entry's `Part of`) with the gate and the entry among their `Parts:`, on a board whose `People:` lists the gate's person. Each comes with its state: `open`, `decided` (open, with `Decided:`), `closed` or `closed-decided` (closed or archived with `Decided:`); it reads each board's archive as well as the board, through a new `parse_closed_items(content)` that parses closed lines as `parse_board` parses open ones (v2.4), cutting the trailing `Closed:` field first as `item_key` does (ledgerboard.py:910-911), since `DECIDED_RE` is anchored at the line's end (:742-743). Only `open` and `decided` cover; `closed-decided` is read by the audit's close condition and the re-ask window, never as coverage. **`open` and `decided` both cover**; `closed` without the lift does not. **Waiting-only answers close the item** (an item whose `Context:` names a gate; any other `decide` item answered `Not yet` stays open, as today). The format fixes two waiting-only labels, `Keep waiting` and `Not yet` (compared case-insensitively; `waiting_only(label)` is the module's one test, v2.4). Such an answer has nothing left to do, so `board.py decide` closes the item in the same write, which also logs `kept waiting` in the ledger (a two-file write, §1.1). It closes even when no listed entry still carries the gate and nothing is logged. The item then reads `closed-decided`, and the `reask_days` window governs the next ask. **Every other non-lifting answer** ("Drop it", "One more round", `Rewrite the check`, `Drop the entry`) keeps the item open as a work order until the consumer that acts on it closes it; a fixture shows "Drop it" on a decision item staying open and decided. The sweep's items offer `Keep waiting` (events) or `Not yet` (decisions) among their answers. A waiting-only label can never lift: `item_line(lifts=)` refuses one, `item_problem()` flags one, and `decide_lift` tests `waiting_only` before `Lifts:`. **`close=` ships in v2.4** with `waiting_only` and the two-file `decide`; v2.3's `decide` never closes. A fixture: "still waiting?" answered `Keep waiting`; a sweep 29 days later files nothing, and 31 days later files it again. `sweep`, `tripwire` and `uncovered_decisions` all call it.
- **`sweep(entries, boards, results, today_utc, today_local, reask_days, event_age_days, repo) -> {to_file: {board: [items]}, to_close: {board: [keys]}, lifts: [{id, gate, kind, evidence}]}`.**
  - `entries` are this repo's ledger and archive texts. `to_file` and `lifts` consider only open entries; the archive is read only to decide closes; `boards` is a list of `(origin_url, basename, text, archive_text)`, so the person's board pick (§3.2) is computed inside; each board is named by `origin_key(origin_url)`, or by its basename when it has no readable origin, and that name keys `to_file`, `to_close` and `covers()`'s results; this repo's own board is the one whose `origin_path` equals `repo` (else whose basename does); `repo` is this repo's `origin_path`; `results` maps `(TD-n, event name)` to one of the four outcomes (§4), with the evidence for a passed one.
  - It decides every row of §3.2's table. The rule is the module's; the numbers (`reask_days`, `event_age_days`, both 30 by default) are the consumer's. "Not covered" is `covers()` returning no item in state `open` or `decided`, **and** no `kept waiting` line for that gate newer than `reask_days`. Re-ask dates on the board (`Decided:`) are compared with `today_local`; Log ages with `today_utc`.
  - **Outcomes pick at most one event item:** `error` files "check broken", `impossible` files "can no longer happen", and only `not yet` can file "still waiting?" (a fixture: age over 30 days and outcome impossible files one item and closes none).
  - **`lifts`** names every host lift: each `until` whose date is reached (`today_utc` ≥ D, as `pickable` and `lift` read it) (`kind: until`, evidence `date reached`) and each event whose check passed (`kind: event`, evidence from `results`). `lift_gate` writes each. It is computed afresh every run; whether a lift PR is already open is forge state, so the consumer filters it (§4.4).
  - **Items it files** go on the person's board for a decision (§3.2's pick) and on this repo's own board for every event item (an event gate has no person), keyed by entry and gate (§3.2), and the `; board <repo>` audit's `act` by `Context: TD-n <gate> board <repo>`. **One filing rule for every kind:** an item's identity is `(Context key, kind, condition)`, the condition being its fixed head. It is filed only when no item with that identity is `open` or `decided` on any board read, and none was **answered** within `reask_days`: on the board, an item carrying a `Decided:` whose label does not lift, dated by its `Decided:` date (not its later `Closed:`); an item closed `— lifted.` settled the old question and opens no window, so a gate re-added later is asked at once (a fixture: lift, re-add the gate ten days later, the sweep files); in the ledger, a `kept waiting` line for the gate. For the decision item, whose title is the entry's Ask, the condition is "uncovered" and this test is §3.2's "not covered". A close the sweep itself made (a check that recovered, a gate that went) opens no window, so a check that breaks again is reported again at once. So an "impossible" item answered `Rewrite the check`, which writes no ledger line and leaves the gate, is not re-filed while it waits for the rewrite; a fixture shows it.
  - **Close rule.** It closes only its own kinds of item, about *this* repo's entries, and **never one whose answer is a work order** (a non-lifting, non-waiting answer, which waits for the consumer that acts on it). A decided item whose answer lifts is normally closed by the decide write itself (§6 (b)); as a backstop, any decided item with a lifting answer is closed by this rule once the gate is gone, whoever filed it (the cross-repo item, which stays decided-but-open until its tool PR merges, is the usual case). Each closes when its condition no longer holds: "decision has no board" once `covers()` finds an item in state `open` or `decided`, or once neither the Context entry nor any listed part carries the gate; "event check broken" once the check no longer errors, or once neither the Context entry nor any listed part carries the gate (a missing `results` entry for a gate still carried changes nothing); any `decide` item keyed to the entry and gate, whoever filed it, "can no longer happen", "still waiting?" (which also closes once the check reports impossible, so the impossible item replaces it, as a fixture shows) and the host's "lift was closed" item (`Context: TD-n <gate> lift`, §4.4) once neither the Context entry nor any id in its `Parts:` carries the gate (an override, an archive, a reassign or a drop all remove it). **The `; board <repo>` audit item** is filed after the gate is already gone, so it has its own condition: it closes once the named board, open items, closed items or its archive, holds a `Decided:` item naming `<this repo>#TD-n`, or the `; board <repo>` Log line is gone. Fixtures show it is filed once and not re-filed, and that an answered item already closed and archived on that board satisfies it. `entries` includes the archive; an id in neither is treated as missing, and its item is left for a person. On a reassign, the consumer closes a's item (§3.1); when that item is on another repo's board, this repo's sweep on its next run is the backstop, through `to_close` keyed by that board.

**The merge gate's coverage check** is one more pure function: `uncovered_decisions(base_tree, head_tree, boards, repo) -> (refusals, flags)`, with `boards` the same tuples (this repo's own board from `head_tree`), §6's rule. "Covered" in it and in `tripwire` means `covers()` returns an item in state `open` or `decided`. It has two branches: a new `decision (person)` that is not covered; and, separately, a decision item with no lifting answer, which is not a coverage question. It refuses only on this repo's own board and flags when coverage depends on another repo's board, so its verdict never depends on the machine (§6).

- **Not moved:** the roster, forge calls, sessions, the event runner's network checks, and taking the id. Those are I/O or policy.
- Each lands with fixtures. The sweep's fixtures are a set of entries, boards and check results in, and the items to file and close out. The verdict's fixtures are base and head trees with each outcome.
- **What it changes in §7.2:** steps 3 and 4 no longer build their own sweep logic or lift-PR rules. They call these functions, and the step-0 consumers read `needs_you` instead of filtering hidden items themselves.
---

## 2. The target ledger entry

```
## TD-n: title

**Priority:** High | Medium | Low
**Type:** debt | feature
**Added:** YYYY-MM-DD
**Owner:** <consumer vocabulary>
**Kind:** <consumer vocabulary, prescribed by cadence.md> (§2.3)
**Status:** Open | Resolved YYYY-MM-DD | Superseded YYYY-MM-DD by TD-m | Dropped YYYY-MM-DD
**Id take:** <nonce>
**Blocked by:** TD-4, other#TD-9, decision (Paul), until 2026-11-15, event (ac-vendors-v2-4)
**Part of:** TD-m

**Why:** …
**Location:** …
**Ask:** …                         ← required while decision (who) stands
**Event (ac-vendors-v2-4):** …     ← required for each event gate (§4)
**Fix:** …
**Done when:** …
**Log:**
- 2026-10-31: filed by Paul, session led-tds: "file the release.sh entry"     ← always first, written by `new`
- 2026-11-01: Paul's go lifts decision (Paul).                                ← every later change appends
```

### 2.1 Fields

| Field | Target | Change from v2.2 |
|---|---|---|
| `Priority` | High, Medium or Low; anything else is an error on a changed entry and ℹ on a standing ledger | **new check** |
| `Type` | debt or feature | unchanged |
| `Added` | the date alone | **comment moves to the Log's first line** |
| `Kind` | consumer field, vocabulary prescribed by cadence.md (§2.3, **[agreed 2026-11-02]**) | unchanged as a field; stages move into it |
| `Owner` | consumer field: the lane or seat that moves the entry next, declared in `Fields:` if the repo wants it checked | unchanged |
| `Status` | closed word plus date (§2.2) | **vocabulary closed; notes move to the Log** |
| `Id take` | the counter take's nonce | written once TD-188 lands |
| `Taken by` | **retired** (TD-188 step 4) | v2.x still reads and renders it in old entries; **v3.0 removes it** |
| `Blocked by` | ids, then gates (§3) | **grammar extended** |
| `Waits` | **retired** | **[agreed]** migrated into gates; read through v2.x, removed in v3.0 |
| `Location` | **moves to the body** as `**Location:**` | no tool reads it; it is prose (principle 4). `migrate` moves it. |
| `Part of`, `Escaped from`, `Tracker` | unchanged | |

**Reserved words** **[agreed 2026-11-01]**. A word in this list is never reused for a new meaning:
- the fields `Waits`, `Taken by` and `Resolved` (as a header field);
- the gate `hold`; the form `decision (who) — text`; the literal holder `designer` in `decision (designer)`. A role is otherwise indistinguishable from a person's name, so each role used is reserved by name. Today only `designer` appears.
- the Status words that `migrate` maps away: open `Designed`, `Built`, `Partly`, `Live`, `In`; archived `Done`, `Moved`, `OBE`.

Where v2.x still reads one, `check()` names it *retired* (with what replaces it) rather than *unknown*. Once v3.0 stops reading it, it is a *retired* error. The list lives in the module and the spec, and grows only.

### 2.2 Status and the Log **[proposed]**

| Status | Where the file is | Written by | Meaning |
|---|---|---|---|
| `Open` | ledger | `new`, `reopen` | live |
| `Resolved YYYY-MM-DD` | `archive/` | `archive` | the work is done |
| `Superseded YYYY-MM-DD by TD-m` or `by <repo>#TD-m` | `archive/` | `archive --superseded-by` | its requirement lives in that entry now (§5) |
| `Dropped YYYY-MM-DD` | `archive/` | `archive --dropped` | no longer needed, and nothing replaces it |

- **`Status: Open` is kept on purpose, as a checked redundancy.** The directory already says open or archived. But an entry read outside its directory (a PR diff, a pasted entry, a cross-repo lookup) still says what it is, and `check()` refuses a mismatch.
- **`Dropped` has no `**Resolved:**`-style body line.** Its why is the `archived:` Log line. Renaming `**Resolved:**` to a status-neutral lead is v3.0 material.
- **The Log** is a body section of dated bullet lines, oldest first, appended by `new`, `note`, `archive`, `reopen`, every gate change and every event resolution.
  - **It is always the body's last section.** `check()` flags a section after the Log, and the writers refuse to append to a Log that isn't last. A section is read up to the next bold lead, so `edit` (including its append fallback) and `archive` (its `**Resolved:**` line, appended at the end today, ledgerboard.py:1897) insert before the Log.
  - **One bullet per line; the words run to the end of the line.** A writer folds newlines into spaces, so there are no continuation lines.
  - **The writer prefixes are reserved:** `filed by `, `gate added:`, `gate lifted:`, `gate reassigned:`, `kept waiting:`, `gate lift skipped:`, `was:`, `archived:`, `reopened —`. `note` refuses words that begin with one, so "reopened the thread" is still a note.
  - **Concurrency:** two PRs appending to one entry conflict at its end, the same as two PRs editing its Status do today. Conflicts stay within one entry, which is acceptable.
  - **Writer-made lines have fixed shapes** that a tool can read:
    - `- D: filed by <who>, session <s>[, while TD-m | while <repo>#TD-m]: "<words>"`: `while` names the entry being worked on when this one was found. It is non-blocking provenance. Readers may list "found while doing TD-m", but it never affects pickability. `who`, `s` and the `<host>` in a host's lift line are tokens without spaces, commas, colons or quotes (`[A-Za-z0-9_.@/-]+`). The `while` target uses the id grammars that `Blocked by` uses.
    - `- D: gate added: <gate>`
    - `- D: gate lifted: decision (<person>) — by <person>; answer "<label>"` (the decide lift or `ledger.py set`). It may end with one of `; board <repo>` (the item is on another repo's board), `; no board item`, or `; shared board item left open` (§3).
    - `- D: gate lifted: event (<name>) — by <person>; answer "<label>"` (a person dropping an event gate from a sweep item, via `decide_lift`). The two event-lift shapes are told apart by their tail (`answer "` vs `<type> passed;`), never by the `by` token; each has a fixture.
    - `- D: gate lifted: event (<name>) — by <host>; <check-type> passed; <evidence>`, where evidence is the merged PR's `<repo>#<n>`, or the `<repo>@<sha>` the file or ref was read at. That is enough for a reviewer to re-run the check.
    - `- D: gate lifted: until <date> — by <host>; date reached`
    - `- D: gate lift skipped: TD-n no longer carries decision (<person>)` (on a parent, by `decide_lift`)
    - `- D: kept waiting: <gate> — by <person>; answer "<label>"`: a non-lifting answer, or "Keep waiting". It resets the gate's age (§3.2).
    - In every shape, a quoted `"<label>"` or `"<words>"` runs from its opening `"` to the **last** `"` on the line, as check text does (§4.1), so it may itself hold quotes. That is §4.1's rule, except that a lift line may end with one of the three suffixes (§3), none of which can hold a quote.
    - `- D: gate reassigned: decision (<a>) → decision (<b>) — by <who>; <why>`
    - `- D: gate lifted: decision (<person>) — by <who>; override: <why>`: the override lift (§3).
    - `- D: archived: <word> — <why>`
    - `- D: reopened — <why>`
    - `note` writes `- D: <words>`.
  - **Every date is a UTC date** (§3).
  - **A gate's age** is one definition everywhere: the date of the latest `gate added`, `kept waiting` or `gate reassigned` line for that gate. If there is none, it is the date of the first Log line, then the `Added` date. **`new` writes one `gate added` line for each gate the entry is filed with**, after its `filed by` line, so a gate present at filing ages from day one.
  - **`check()` never requires `filed by` first.** A legacy entry's Log is created by whichever writer touches it first. v2.5's `migrate` turns the `Added` comment into a plain `- <Added date>: <comment>` line, and writes `filed by` only when the comment parses into that shape. Real comments are mostly free prose. It inserts every migrated line in date order, keeping the Log oldest-first.
  - **Status notes become Log lines through one pure function**, `status_notes_to_log(entry_text) -> entry_text`. The v2.4 writers (`archive`, `reopen`, `note`, before they write) and v2.5's `migrate` both call it. It needs no git:
    - **The Status grammar it reads:** `<Word> [D] [by <id>] [[:] <tail>] [ — was: <Status>]`, where `<id>` is `TD-m` or `<repo>#TD-m`. `<tail>` is everything after the head up to the first ` — was: `. That covers what `note`, `archive` (including `Superseded D by TD-m: why`) and `reopen` write today (ledgerboard.py:1857, :1888, :1910).
    - **`<Word>` must be a known Status word:** the open and closed words, or one `migrate` maps (§2.1's reserved list), optionally followed by `.`, compared as `first_word` does. **Anything else, such as a prose-only or bold-lead Status (`**Live check held…`, `Steps 1 and 2 shipped…`, about 70 in ShiftLead), and the function lifts nothing.** `note` leaves that Status alone. `archive` and `reopen`, which replace the Status anyway, first copy the whole old value verbatim into one Log line, `- D: was: <value>` (dated by the fallbacks; `was:` is a reserved prefix, so no `note` can imitate it). v2.5's `migrate` does the same for an **open** entry: it sets `Open`, writes the `was` line, and lists each one in its dry run for the remodel to review. It **stops** only on an archived entry's unknown word, as the map below says. **Setting `Open` changes no reader's pickability:** `pickable()` never reads an open entry's Status word (ledgerboard.py:328-420), and ShiftLead's `waits()` reads `Waits`, settling, live-check and `Blocked by`, not Status (queue.py:680-694). An entry that a prose Status called "held" was held by a Hold record, which step 4 turns into `decision (Paul)`.
    - **No split inside a tail.** `note` appends ` D: words` with only a space (:1857), exactly like a date in prose ("done 2026-10-03: the image installed"), so no rule can tell them apart. The whole tail becomes **one** Log line, verbatim, dated by the Status's own date, else the `**Resolved:**` line's date, else `Added`. The dates inside stay readable as prose.
    - **`— was:`** is the one boundary cut, because only `reopen` writes it, at the **first** occurrence (each cut shortens the text, so recursion ends). A `note` written after a `reopen` lands inside the `was` segment and takes its date; there is no live instance. Each `— was: <Status>` becomes its own line, `- D: was: <Status verbatim>`, dated by that inner Status's date or the same fallbacks. The inner Status is written as **one** verbatim line up to its own first ` — was: `, and only the remainder recurses: no inner tail becomes a separate note line.
    - **Insertion:** lines go in date order among existing Log lines, stable after equal dates.
    - **Reserved prefixes:** a lifted line that would begin with a reserved prefix is written as `- D: note: <text>`, so no lifted prose ever looks like a writer line.
    - **What remains:** the Status is left as `<Word> <date> [by <id>]` (or bare `Open`).
    - Idempotent: a Status with no trailing text is unchanged.
  - Log lines are history: `renumber` does not rewrite ids in their prose. **The one exception is the `while` token**, a structured pointer, which `rename_ref` rewrites like a `Blocked by` id.
- **`reopen`** sets Status to `Open` and logs `reopened — <why>`. Today it writes `Open D: why — was: …` (ledgerboard.py:1910).
- **The `**Resolved:**` body line stays as it is.** An archived entry must say where its lasting content now lives (the doc, test or code), and the PR that finished it. Only Status's trailing text moves to the Log.
- **`check()`:** under v2.5, a Status that doesn't match the table (word, date, `by` target, directory) is an error on every entry, open or archived. Nothing in the file stages this: a repo takes v2.5 in one PR that vendors it and runs `migrate` (§7). Draft 5's `Ledgerboard: 2.5` pin is dropped, because v2.x readers would read it as v1.

**Migrating archived Status words** (mechanical, by the module's `migrate_entry`, which `ledger.py migrate` and ShiftLead's migration both call):

| Today | Becomes | Date from |
|---|---|---|
| `Resolved D…`, `Resolved` (undated), `Resolved.`, `Done …`, `Built …` | `Resolved D` | the Status, else the `**Resolved:**` line, else the archiving commit |
| `Designed …` (archived) | `Resolved D` | same |
| `Superseded D by TD-m`, `Moved to <repo>…` naming an entry | `Superseded D by TD-m` / `by <repo>#TD-m` | same |
| `Moved …` naming no entry, OBE, won't fix | `Dropped D` | same |
| anything else | `migrate` stops and lists them; the remodel session decides each before the vendor PR can merge | |

**Stages on open entries live in `Kind`, not Status** **[proposed]**. Status answers "is it live or finished, and how did it end". `Kind` answers "what kind of work is next". A stage word in Status (ShiftLead's Designed, Built, Partly, Live) puts a second "what's next" beside `Kind`. The stage *history* ("designed 10-28, built 10-30") belongs in the Log. `migrate` turns each stage word into `Open` plus a Log line, and sets `Kind` where the stage implies it (Designed → build, Built → live-check).

### 2.3 `Kind`: whose field? **[agreed 2026-11-02: (i)]**

Draft 5 made `Kind` a format field. Fable's objection holds on the long-term rule: **a format field earns its place through rules the module applies.** As written, the module would only spell-check the four words. A repo's `Fields:` line already does that, and the words were ShiftLead's lane list unchanged.

- **(i) `Kind` stays a consumer field; cadence.md prescribes it.** agent-cadence's cadence.md defines one `Fields:` line every cadence repo carries, so the vocabulary is the same everywhere without the format owning it. Routing on it stays the consumers' job, as lanes are. **Chosen 2026-11-02.**
- **(ii) A format field, with module semantics per word.** For example, `design-first` would never be pickable for a build, and would archive with its last part; `live-check` would require a deploy event gate. `evaluation` has no rule the module could apply, so it would not be a format word.

Either way:
- **Leaving `design-first` is defined.** When the design is agreed and its builds are filed `Part of` it, the writer sets the next `Kind` and logs `designed`. The parent stays unpicked through its open parts.
- **`decision` and `person` are not kinds** (ShiftLead has 7, agent-cadence 2). A person owing something is a `decision (person)` gate.

### 2.4 Body sections that pair with gates

| Gate | Section | Required |
|---|---|---|
| `decision (person)` | `**Ask:**`: what the person owes, including a "go" | yes |
| `until DATE` | none | no |
| `event (name)` | `**Event (name):**` (§4) | yes |

---

## 3. `Blocked by`: the gates **[proposed]**

### 3.1 Grammar, rules and lifting

```
blocked-by := item ("," item)*
item       := id | gate
id         := TD-n | <repo>#TD-n
gate       := "decision (" person ")" | "until " YYYY-MM-DD | "event (" name ")"
person     := [A-Za-z0-9_-]+ ("." [A-Za-z0-9_-]+)*, compared case-insensitively
              (no "..", no leading or trailing ".", so it is also a valid git ref component)
name       := [a-z0-9-]+, unique within the entry
```

- The writers render ids first, then gates in the order above. At most one decision per person, at most one `until`, and any number of differently named events.
- **The old form** `decision (who) — text` is read only when it is the last item. The parser tries the strict grammar first. Migration moves the text into `**Ask:**`. The writers never produce it: **from v2.4, `new` and `set` refuse a `Blocked by` value in the old form.** v3.0 stops reading it. **A writer refuses to add any gate to an entry that still has the old form** ("migrate it first"), because the old form's text runs to the end of the line and would swallow the new gate (ledgerboard.py:173).
- **A retired gate** (`hold`, a role in `decision (…)`) is read as an unreadable item that keeps the block, and `check()` names it *retired* with its replacement (§2.1).
- **A part never inherits its parent's ids or gates** (SPEC *Part of*, unchanged). A part that must also wait on its parent's decision or event names that gate in its own `Blocked by`. An Org-mode precedent shows how easily people assume the opposite, so the spec states it beside the gates as well.
- **Gates are written where they hold; the parent rolls them up** **[agreed 2026-11-02]**.
  - A gate goes on the entry whose work it stops, usually a part. A parent carries a gate only for its own work, such as the design itself.
  - The parent's record gains **`parts_gates`**, derived and never written, as `parts_open` is. It lists each open part's gates, for example `{"decision (Paul)": ["TD-15", "TD-16"], "event (x)": ["TD-14"]}`. Cards and the board show it ("waiting on decision (Paul) on 2 parts").
  - `parts_gates` does not change the parent's pickability, which its open parts already decide. It covers **direct parts only**, and keys gates in their canonical form (the person's name as written on the lowest-numbered part carrying it, compared case-insensitively).
- **Every ledger date is the UTC date** **[agreed 2026-11-01]**. This covers the `today` the caller passes, `until`, `Added`, Status dates and Log dates, so every machine agrees on the day as well as on the text.
  - **Every board date is the person's local date:** the item's date, `Due:`, `Decided:`, closed dates, replies. The board is the person's own page and never gates anything.
  - One decide lift can therefore write a local `Decided:` date and a UTC Log date that differ by a day. That is accepted.
  - **The module's ledger writers** (`edit_entry` and the entry writers) turn an aware datetime into its UTC date and refuse a naive one. The board writers (`edit_line`, `item_line`) take a civil date, the person's local day. `edit_entry`'s `.date()` today takes the datetime's own zone (ledgerboard.py:1824). The module cannot check that a bare date is UTC, so each consumer's writers switch to `datetime.now(timezone.utc).date()` in their vendor PR. Today agent-cadence writes the local date (ledger.py:1072, 1161, 1282).
- `pickable(ledger, archive, resolve=None, undeclared=False, rank_text=None, repo="", *, today)`: `today` is always required, as the UTC date. An entry is pickable when every id is archived, it has no `decision`, no `event`, and `until D` has today ≥ D. **An event gate blocks until the text says otherwise**: the host's tool PR removes it. There is no event-results input, so no host's memory enters pickability.
- The new signature breaks direct callers (ShiftLead's `sessionorc/ledger.py:525`), so each vendor PR fixes its call sites.

| Gate | Meaning | Written by | Lifted by |
|---|---|---|---|
| id | another entry must land first | the filer | its archive (the resolver for `other#TD-n`) |
| `decision (person)` | a person owes an answer, including "go once I'm done shaping it" | the filer; a design round; your layer rule §2.4 | **the named person's lifting answer** (default `Go`) on the entry's `decide` item, through the decide writer (§6); or, on a board that says `Answered by: any`, a lifting answer from anyone on the board's `People:` list (§6.2); or the named person through `ledger.py set`. Nobody else's answer lifts it, the host and agents included. The Log records `by <person>`. Proving who answered is the consumer's job (the board's commit author, the session's person). **On the `set` route** the module cannot know who ran it. So removing a `decision (person)` through `set` requires `by=<person>`, logs `gate lifted … by <person>`, and refuses a `by` other than the gate's person. **The enforcement point is the consumer's writer.** It refuses a lift, reassign or override unless the running session is person-started. The merge gate checks only the shape, and that `by` matches the gate's person (any person token for an override). **The one exception is a carve-out lift (§6 (a0)–(d)),** whose `by` `decide_lift` has already checked against the PR's own base board, so the gate never reads another repo's board to judge a `by`. A teammate's lift of an item on another repo's `any` board (`; board <repo>` with a `by` other than the gate's person) is flagged and takes ordinary review. A person-shaped event lift outside the carve-out (`gate lifted: event (x) — by <person>; answer …`) has no gate person, so the gate accepts any person token there, as for an override, and review is the backstop. **When the person isn't available** **[agreed 2026-11-02]**, there are two routes. Neither is a hand edit. **What actually protects this is the writer, plus review.** The merge gate catches only a careless hand edit: one with no `by` line, or a `by` that doesn't match. A hand edit that writes a well-formed `— by Paul; answer "Go"` passes it, so review of the diff is the backstop. One more **tripwire, forgeable and labelled as such**. In the same repo, when a diff removes a `decision (person)` from an entry that **stays open**, the diff must also carry a `Decided:` on an item that **covers** that gate (§3.2's definition, parent snapshots included): an item in state `open` or `decided` at the base that carries a new or changed `Decided:` at the head, or, on an item already `decided`, a newly written `Closed: … — lifted.` (the last part of a shared item lifted with the same label, person and day; a fixture) (so a later lift of a work-order item, answered "One more round" earlier, passes), in state `decided` or `closed-decided` (a same-repo lift closes it in the same write, §6 (b)); fixtures: a lift closed in the same write passes, and the same diff with the item closed but no `Decided:` fails. Exempt:
  - a diff that logs `gate reassigned` or `override:` for that gate;
  - a diff that archives the entry;
  - a `migrate` commit, identified by its fixed subject `ledger: migrate v<release> (<n> entries)`, which joins the subject vocabulary.

  So that the `set by=<person>` route satisfies it, that route also writes `Decided: <label>` on the covering item, through `board.py decide --board-only`, which writes only the board half, the same `edit_line(…, "decide", label, by, today, close=closes(item, label, entries_after))` as §6 (b), and never calls `decide_lift`: `set` has already made the ledger change, so nothing is lifted twice and no listed part `set` wasn't asked about is touched (a fixture: `set by=` on a parent-snapshot item whose other listed parts still carry the gate). Both routes write the identical board line, but **a `set by=` PR always takes ordinary review**: it is the fallback route, its commit carries `set`'s ledger subject rather than a board `decide` subject, and its ledger change need not equal `decide_lift`'s (a parent's other parts are untouched). Only `board.py decide` is a carve-out lift. Exceptions:
  - **No item covers the gate.** The route logs `answer "<label>"; no board item`, and the tripwire accepts that only when `covers()` finds no item in state `open` or `decided` at the PR's base, nor at its head (so closing a covering item without an answer and logging `no board item` fails).
  - **The covering item is a parent snapshot shared with other parts** (its Context entry, or another id in its `Parts:`, still carries the gate; fixtures for both). The route leaves the item open and logs `answer "<label>"; shared board item left open`, which the tripwire accepts. *(Amended 2026-11-11, TD-067:)* the item is left undecided as well (`board.py decide --board-only` writes nothing on it), and the tripwire flags a head that gives it a `Decided:` while it stays open (`tripwire-shared-decided`).
  - **Cross-repo:** a lift PR in the entry's repo, for an item on another repo's board, logs `answer "<label>"; board <repo>`. The tripwire accepts it **only when `<repo>` is well formed and is not this repo**. A roster test would make the merge gate's verdict depend on the machine, and the sweep's audit below is the backstop. The gate sweep audits it afterwards: a `; board <repo>` line whose named board holds no `Decided:` item naming `<this repo>#TD-n` goes to the board as `act`. The hole is no wider than the tripwire's own admitted one. The remodel's "lift a stale gate" uses `set by=` and follows the same rule. The routes:
  - **Who may do any of this: only a person-started session.** Agents commit under the person's git name, so a git author proves nothing. The rule is about *sessions*. A lift, reassign or override is written only by a session a person started and is driving (ShiftLead's `[person-session]`), never by an autonomous one. The consumer attests that. The module records `by` and checks the shape.
  - **Reassign** (the usual route): `set` replaces `decision (a)` with `decision (b)` and logs `gate reassigned`.
    - It refuses b = a, and the **consumer's writer** refuses a b with no board (the module has no roster). b's board is *the person's board* as §3.2 defines it.
    - The consumer closes a's item as "moved to b", with no lift, files b's item, and gives a an fyi.
    - A reassign resets the gate's age (a new person is asked).
    - `check()` notes (ℹ) a gate reassigned more than twice.
    - An agent that thinks a decision is stuck files a `decide` item proposing the reassign. It never reassigns.
  - **Override lift** (the last resort): `set --override "<why>"` takes `by=<who>` (who may differ from the gate's person) and a non-empty why. It lifts the gate and logs `override: <why>`. The consumer puts an `fyi` item on a's board so a sees what was decided while they were away, and **refuses the override when a has no board to notify**. **[agreed; lifting answers proposed; named person agreed 2026-11-01; routes agreed 2026-11-02]** |
| `until DATE` | not before the date | the filer | the date; `check()` flags a past one (ℹ) |
| `event (name)` | something outside the ledger | the filer | its mechanical check (§4) |

**Removed in draft 3:** the `hold` gate, and with it ShiftLead's Hold, Release, prehold and the clock's hold records. To keep an existing entry from being picked, add `decision (Paul)` with an Ask, through `ledger.py set`. There is a short window between that PR opening and its merge in which a session could still pick the entry. **[agreed 2026-10-31]** The window is acceptable: a new design entry is filed with `decision (<person>)` already in it (agent-cadence TD-212).

### 3.2 The gate sweep: nothing waits silently **[proposed]**

The host runs this on a schedule. **What it decides is the module's `sweep()` (§1.2)**; the host gathers its inputs (the roster's boards, the event checks' results) and writes its outputs. It is not part of `check()`, because its inputs need the board and the network. **A sweep runs in one repo, over that repo's own ledger, through that repo's pin.** So a roster repo is swept only once it pins step 3's release and its board has a `People:` line, and never before its remodel.

| Condition | Goes to the board as |
|---|---|
| a `decision (person)` that is not **covered**. *An item covers a gate only when the gate's person is on its board's `People:` list (§6.2). Any such board will do. The board check flags a `decide` item whose Context gate names someone not on the board's `People:`. **The person's board** is one deterministic pick: this repo's own board if its `People:` lists the person, otherwise the matching board with the **lowest pick key** among the roster boards read. **The pick key** is `origin_key(<the repo's origin URL>)`, compared bytewise. `origin_key` is a pure module function, `(url) -> str | None` (no git), with fixtures. It takes the URL's host and its full path (after `host:` or `host/`), lowercases them, strips `.git` and any trailing `/`, and keeps **every** component: for example `github.com/shiftlead/ledgerboard`, or `gitlab.example/group/sub/repo`. It reads ssh (`git@host:path`, `ssh://user@host:port/path`) and https (`https://user:token@host:port/path`) forms. It **strips userinfo and port**, so a key never holds credentials. **A readable origin** is an ssh or https URL with a host and a path whose components satisfy the `<repo>` grammar (§4.1). `origin_key` returns none for anything else: `file://`, a plain local path (`/srv/git/x.git`, `../x`), or a path that fails the grammar. Such a repo counts as having no origin. Both consumers call it, replacing their own differing derivations today (agent-cadence `forge.py:132`, `nudge_user_attention.py:1152`; ShiftLead `ledger.py:769`). A board whose repo has no readable origin sorts after every keyed board, by its lowercased checkout basename. The key comes from the origin, not from the machine or the clone's directory name, so every machine and both consumers make the same pick when they read the same boards. That holds for boards with an origin, which is every board today. **Writing a repo in an id** (`<repo>#TD-n`, `; board <repo>`) is a separate concern, the resolver's input. The writer emits the **lowercased** origin path, `origin_path(url) -> str | None`, a pure module function that is the path part of `origin_key` ( `owner/name`, or deeper for a nested group) **whenever the origin is readable**. `<repo>` text in ids, the sweep's Context-key lookup, the Context-ref dedupe and the tripwire compares case-insensitively, so two clones whose origins differ in case write and match the same id. **`item_key` stays case-sensitive and byte-exact** (SPEC:343): the case-folding lives in those lookups, never in `item_key`. It writes a bare name only for a repo with no readable origin. **The host isn't in the id.** Two roster repos with the same `owner/name` on different forges (a mirror) make an id that matches both, and the resolver returns unresolved, so the block stays. That fails safe, and it is an accepted limit: an id is unambiguous within one forge namespace on a roster. Resolvers prefer an exact path match to a suffix match, so a deeper repo shadows a shallow one only when the shallow one is absent. A bare basename resolves against each machine's roster, so it could silently name a different repo elsewhere. The origin path is the same text on every machine. Filing and reassign use it. If no board matches, the sweep files an `act` "decision (b) has no board" on this repo's board, keyed `Context: TD-n decision (b)` with kind `act`. It files that under §1.2's one filing rule (no such item open or decided, and none answered within the re-ask interval); it reads the board's archive (`docs/user_attention_archive.md`, in the board's own format with `Closed:` dates; created on first use, so a missing archive reads as nothing closed) for closed items, so no state is kept.* Not covered means: no `decide` item open or decided, on this repo's board or any roster board (whose Context names `<this repo>#TD-n`; the sweep reads each roster repo's board on its origin default branch, a missing or stale board counts as not covering, and the Context key de-dupes), names the entry and gate, nor the entry's parent with that gate and the entry among its snapshot `parts` (never written, or closed without the lift). **And** no `kept waiting` line for that gate is newer than the consumer's re-ask interval (default 30 days, as for events), so a "Not yet" isn't re-asked at the next sweep. | `decide`: the entry's Ask, with `Go` among the answers |
| an event check that errors (bad repo, auth, a missing path, a timeout) | `act`: "Event check broken on TD-n" |
| *(every sweep item about an event carries `Lifts: Drop the gate.`)* an event check that says **impossible** (today only: the PR closed unmerged) | `decide`, at once: "<event> can no longer happen" with `Drop the gate \| Rewrite the check \| Drop the entry` |
| *(the age is the consumer's number, `event_age_days`; only when the check's outcome is `not yet`)* an event whose age (§2.2's one definition) passes 30 days | `decide`: "Still waiting on <event>?" with `Keep waiting (default) \| Drop the gate \| Rewrite the check` |
| an `until` in the past | nothing: it already reads as lifted; the sweep removes the gate in a tool PR |

**The sweep keeps no state; the ledger's Log is the state.**
- A gate's age is §2.2's one definition.
- "Keep waiting" on an event item, or a non-lifting answer on a decision item, writes `kept waiting: <gate> — by <person>`; when the sweep next asks follows §1.2's filing rule, which also reads the board's `Decided:` dates (an event item answered "Rewrite the check", or a cross-repo item, writes no ledger line). Without that line, the next run would find the gate still old with no open item and file it again.
- Board items are keyed by entry **and** gate: `Context: TD-n <gate>`, for example `Context: TD-14 event (ac-vendors-v2-4)`. Together with the item's kind and its fixed head ("Event check broken", "can no longer happen", "Still waiting", "has no board"), that key tells "decision missing", "check broken", "impossible" and "still waiting?" for one entry apart (§1.2).
- Running the sweep twice writes nothing new. Two machines write nothing new when their rosters hold the same boards. A board missing from one machine's roster is the already-admitted case of a missing board that counts as not covering, and the Context key de-dupes the result once both boards are read. **A deadline written on the gate** (`event (name) by DATE`) is not added for now. It waits until the fixed 30 days proves too blunt. **[agreed 2026-11-01]**

**Not gates:**
- **`Owner`.** Who moves an entry next never blocks it. `Owner: paul` is not a hold (today ShiftLead reads it as one, `queue.py:700`). Waiting on a person is `decision (person)`.
- **Which board a decision lands on.** Coverage and the person's board pick (above) decide it; a board names its people (§6.2).
- **A role, such as `decision (designer)`.** `Kind: design-first` routes design work. `decision` takes a person only, and migration removes the role form. ShiftLead's special case is already gone: shiftlead#TD-1296 moved it to `Kind`.
- **Waiting on a judgment.** That is work, filed as its own entry and named here by its id (§4.3).

---

## 4. Events: mechanical only **[proposed; filed with v2.4's builds, part of TD-010]**

### 4.1 The section

```
**Event (ac-vendors-v2-4):** agent-cadence has vendored ledgerboard v2.4.
check: file-contains ShiftLead/agent-cadence files/scripts/ledgerboard.py "v2.4"
```

- The first line describes the event in plain words.
- The second is exactly one `check:` naming a typed check. **Arguments** are separated by spaces, except the quoted text argument: it starts at its opening `"` and ends at the line's **last** `"`, so the text may itself hold quotes. Nothing may follow it.
- `check()` refuses an event gate with no section, no `check:` line, or an unknown check type or bad arguments.
- **Arguments are confined** **[agreed 2026-11-01]**. The ledger is text anyone with PR rights can edit, and a check runs with the host's credentials. So `check()` refuses:
  - a `<repo>` that is not `name` or a path of `/`-separated components (`owner/name`, or deeper for a nested group), where each component is ASCII `[A-Za-z0-9_.-]+`, is not `.` or `..`, and does not start with `-` (a leading `.` is allowed, as in GitHub's `owner/.github`; traversal is ruled out by banning `.` and `..` components). Today's cross-repo regexes admit `../x` and non-ASCII: `XREPO_ITEM_RE` (ledgerboard.py:53) for `Blocked by` and `rename_ref`, and `REF_TD_RE` (:775) for Context refs, which steer the cross-repo lift. Both are tightened to the same rule from v2.4, so there is no URL, no host and no path traversal;
  - `n` that is not `[0-9]+`;
  - a `commit` that is not `[0-9a-f]{7,40}`;
  - a `ref` that fails git's `check-ref-format --allow-onelevel` rules, or starts with `-`, or holds `..`, `@{`, `:` or any of ``^~?*[\`` and spaces. That rules out option injection (`--output=x`) and revision syntax (`a..b`, `@{u}`, `ref:path`);
  - a `path` that is absolute, has a `..` segment, starts with `-`, or holds a glob character, `?`, `#` or `%` (which would be URL syntax in a forge API path);
  - text that holds a newline (it can't, being one line) or is empty.

  Text is matched literally, never as a pattern. What `check()` cannot see is the host's rule (§4.4).

### 4.2 Check types

**The first set: three types.** Three is an evidence-based starting point, not a limit: they cover the waits that exist today. Any real wait that none of them fits gets a new type through a format PR.

**Every check has four outcomes** **[agreed 2026-11-01]**:
- **passed:** the host lifts the gate;
- **not yet:** nothing happens;
- **impossible:** it can never pass as written; it goes to the board at once (§3.2);
- **error:** the check could not run; it goes to the board as broken, and is never read as not yet.

A run that exceeds the host's per-check time limit is an error.

| Check | Passed when | Impossible when |
|---|---|---|
| `pr-merged <repo>#<n>` | the forge says the PR is merged | the PR is closed unmerged. A PR that is not found is an **error**: a forge answers 404 both for missing and for unauthorised. |
| `file-contains <repo>[@<ref>] <path> "<text>"` | the file at the ref (default: the default branch; a tag works as a ref) contains the text | never: a missing file may appear later, so it is *not yet*; a missing repo is an *error* |
| `ref-includes <repo>@<ref> <commit>` | the commit is an ancestor of the ref (a pin "at or past" a commit) | never: an unpushed commit or a deleted deploy ref may still appear, so either is *not yet*; a missing repo is an *error*. The 30-day sweep catches a wait that never ends. |

A new check type must state all four outcomes. **When in doubt, a result is an error, never impossible**: "impossible" asks the person to drop or rewrite the gate, so it must be certain.

**Lifting is text.** When a check passes, the host opens a tool PR that removes the gate. **The `**Event (name):**` section stays**, as an Ask stays after its decision lifts, so the file still says what was waited for and how it was checked. `check()` notes (ℹ) an Event section with no gate only when no `gate lifted: event (name)` Log line explains it. If a reopened entry re-adds a gate with the same name, the standing section is reused (or edited), not duplicated. It logs `gate lifted: event (name) — by <host>; <type> passed; <evidence>` in the fixed shape (§2.2), so a reviewer can re-run the check from the logged evidence. Until that merges, every reader sees the entry as blocked. A check that flips back before the merge leaves the PR to its reviewer. **A lifted gate never re-arms.** If the thing later regresses, that is a new entry, or a new gate on a reopened one.

**Live checks use it.** "The build is deployed" is an event gate on the live-check entry, for example `ref-includes <repo>@<deploy-ref> <commit>`. ShiftLead stops reading PR numbers from the `Kind` comment. **[proposed]**

**Later: `host-log <kind> "<text>" [times N]`**, its consumer half filed as **shiftlead#TD-1295**, counts records in the host's own event log. It would turn "the test fails again" and "Paul's next Apply" (about 3 of the 23 waits) into checks, with `times N` as your "how many times", and `since` defaulting to the gate's `gate added` date. **ShiftLead has no such log today.** The log is TD-1295, and the format's check type is a minor release once the log exists. Until then have the remodel turn those waits into `until <date>` plus a re-check entry. *(Amended 2026-11-04, TD-045: `docs/plans/TD-045-host-log.md` — the check names a source, the count goes before the text, `since` is the day after the `gate added` line and `set` logs that line, and sources are declared in the repo as defaults and host-selected profiles.)*

### 4.3 What is not an event

If telling whether it happened needs judgment ("is the feedback good", "watch it for a day", "the page looks right"), it is **work**:
- File an entry with `Kind: evaluation` or `live-check` (§2.3).
- Block on its id.
- An agent picks it like any other work, and its archive releases the dependents.

That keeps judgment inside the queue, ranked and visible, instead of in a watch list.

### 4.4 Who runs what

| Here (format) | Consumers (host) |
|---|---|
| the gate, the section, the check types' names, argument shapes and four outcomes, `check()`'s refusals (syntax and argument confinement), `pickable()` reading the gate as blocking, the `gate lifted` line's shape; **which gates to lift and which items to file or close: `sweep()` (§1.2)** | run every event check on every sweep (they are cheap), each under a time limit, reading whatever forge state a check needs (a PR's state for `pr-merged`), and pass the outcomes to `sweep()`; for each of its `lifts` with no lift PR already open, open the tool PR that `ledger.py lift` writes; file and close its items through `board.py` |

*(Amended 2026-11-04, TD-045:)* under consumers, the `host-log` reader (agent-cadence's `hostlog.py`), run per gate on hosts that declare the repo. AGENTS.md and §1.1's package boundary are unchanged: the package gains pure functions only.

**Host rules** **[agreed 2026-11-01]**:
- **A check reaches a repo only if it is on the host's roster *and* at least as visible as the ledger's own repo**, with read-only tokens. A public ledger's checks reach only public repos. Otherwise a public gate such as `file-contains private-repo … "text"` would leak one bit per sweep through its public lift PR. A check that this rule refuses is an *error* (the board's "check broken").
- **Lifting is idempotent.**
  - The lift PR's branch is keyed `lift/TD-n/<event-name>` (or `…/decision-<person lower-cased>`, `…/until`).
  - A host that finds that branch or PR open, or the gate already gone, does nothing.
  - A host that finds a lift PR for the key **closed unmerged** (a reviewer turned it down, or the check flipped back) does not reopen it: it goes to the board as `act` "Lift of <gate> on TD-n was closed", filed by the host (it is forge state), keyed `Context: TD-n <gate> lift`, and closed by the sweep's close rule once the gate is gone. Each sweep would otherwise reopen it.
  - The host also matches an open lift PR by the `gate lifted` line in its diff, not by branch name alone.
  - **`renumber`** changes the key, so the consumer's renumber closes and retargets any open lift PR for the old id.
  - Two machines cannot double-lift.

The watch list is the ledger itself: every open `event (…)` gate. There is nothing else to keep in step with it. An event left waiting or broken goes to the board through the gate sweep (§3.2). **30 days agreed 2026-11-02:** every team finishes its rewrite before working again, so it will rarely be reached.

---

## 5. TD-011: supersede and drop rewire their dependents **[proposed]**

- `pickable()` and `check()` now read an archived entry's Status word. **Under v2.4**, before the closed set lands in v2.5, an archived Status that starts with `Superseded` or `Dropped` triggers the rules below, and every other archived Status that is a known word (`Resolved`, `Done`, `Built`, `Designed`, undated or not), or none, reads as closed and done, and a word v2.4 does not know keeps the block (TD-039) (*Amended 2026-11-04, TD-039: `docs/plans/TD-039-unknown-status.md`.*). v2.5's `migrate` then makes the words match.
- An open entry blocked by a superseded or dropped entry is an error on edits and ℹ on a standing ledger.
- `archive --superseded-by TD-m` renames the old id to TD-m in every open dependent's `Blocked by`, in the same change.
- `archive --dropped` refuses while any open entry depends on the dropped one, and lists every dependent in the refusal. You decide each dependent first.
- Cards are recomputed. A rewired dependent may need a `join` rank write.

**Edge cases** **[agreed 2026-11-01]**. No precedent rewires dependents, so these are ours to define:
- **A duplicate** is `Superseded D by` the original. There is no separate Duplicate word.
- **The successor must be live or Resolved.** It must exist (in the ledger, the archive, or through the resolver for `other#TD-m`) and must not be Dropped. Superseding by an entry that is itself Superseded follows the chain to its end and writes that id.
- **A chain** (A superseded by B, then B by C): B's archive rewires A's former dependents, which now name B, to C. Every dependent always names a live or Resolved entry.
- **Dedupe:** a dependent that already names the successor keeps one copy.
- **A cycle:** a dependent that *is* the successor would block on itself. The archive refuses and names it.
- **A chain that ends in Dropped** is refused: the successor must be live or Resolved at the end of the chain.
- **Across repos.** Today the resolver answers only `open | archived | unresolved` (ledgerboard.py:61). It is extended to return the archived entry's **Status word and successor id**. Then `check()` and `pickable()` can apply the rules above to an `other#TD-m`.
  - Another repo's archive cannot rewrite this repo's text. **Rewiring a cross-repo dependent is the gate sweep's job**: it finds a dependent naming a Superseded `other#TD-m` and opens a tool PR in this repo. Until then `check()` reports it as ℹ.
  - A dependent naming a Dropped `other#TD-m` goes to the board as `decide`.

---

## 6. The target board **[agreed in shape: TD-008]**

The item line, with one addition (`Hide until`, below):
`- [ ] <kind> <date> (<head>) — **title** text. Context: refs. Parts: ids. Due: date. Hide until: date. <replies> Answers: … Lifts: … Decided: …`

| Writer | What it does | Release |
|---|---|---|
| `item_line(…, kind, answers, default)` | a whole new item of any kind; the detail block is built from named parts (Context, Question, Caveats, Recommended) | v2.3 |
| `item_problem(line)` | why an open line isn't one the writers would write | v2.3 |
| `item_notes(item, today)` | the ℹ notes on a hide that hides nothing or outlasts the Due (TD-023) | v2.4, or the release after its build |
| canonical item writer | the one-time `fmt` pass | v2.3 |
| `archive_closed(board, archive)` | moves closed items, with their detail blocks | v2.3 |
| decide lift | answering a **lifting answer** on a `decide` item whose `Context:` names exactly one entry removes that entry's `decision (person)` and logs `gate lifted … by <person>`. When the entry is a parent and the Context lists `parts`, it also removes the gate from each listed part (below). | v2.4 |

- **Only the named person's answer lifts**, or, on an `Answered by: any` board, any listed person's (§6.2). The module's lift takes who answered and refuses anyone else, compared case-insensitively. The consumer supplies who answered, from the session it has attested.
- **Only a lifting answer lifts.** The item writer takes `lifts=<labels>` (default `Go`), so an either/or ask ("Option A | Option B") can lift on either. **The set is stored on the item** as the field `Lifts: Option A | Option B.`, placed after `Answers:`. It is written only when it isn't just `Go`; absent means `Go`. It joins the field and sanitising regexes (ledgerboard.py:1056-1058), `ANSWERS_RE`'s end anchor (`(?:\b(?:Lifts|Decided):.*)?$`, today :743-744, whose lazy group would otherwise swallow it), `_trailer`'s field start, `item_problem()`'s read-back, and the item's key, so the checker and every reader see the same set. A `|` inside a label is escaped as in Answers. Any other answer ("Not yet", "Drop it", "One more round") is logged on the entry and the gate stays. Whoever acts on the answer does the rest, for example `archive --dropped`. *Whether a decision's item has a lifting answer* needs the ledger as well as the line, so it is part of the merge-gate rule below, not `item_problem()`. The sweep's event items carry `Lifts: Drop the gate.`, not `Go`. `item_problem()` flags a lifting item whose `Context:` names more than one entry.
- **The decide lift is ledgerboard's `board.py decide --by <person>`** (v2.4), which writes the board item and, through `decide_lift`, the ledger entries, as one two-file write. The consumers' part is the commit, the PR and attesting the session; agent-cadence's `board_edit.py decide` and ShiftLead's `decided_line()` path each call it.
- **Same repo:** the board and ledger edits land in one commit, written by `board.py decide`. **It is a lift PR**, and the person's answer is its review. agent-cadence's carve-out for tool-made board PRs (`check_cadence.py:1675`, which today accepts the board alone) widens to accept exactly this shape, checked as follows:
  - (a0) **the base board declares `People:`** (this applies to the widened lift shape). **From v2.4, every PR whose one changed board item gains a `Decided:` and whose `Context:` names a gate is judged by `lift_pr_verdict`, even when its ledger diff is empty**, so (a0), (b) and the `People:`/`Answered by:` refusals apply to it; the old board-alone carve-out keeps `snooze`, `due`, `done`, `reply`, and `decide` on items whose Context names no gate. An item whose Context names another repo's entry (`other#TD-n decision (p)`) is written board-alone and stays decided-but-open (below): it passes on (a0) and (b), with `files == [board]`, for a decision gate the gate's person (named in the Context) on `People:`, `by` on `People:` and, under `Answered by: owner`, `by` equal to the gate's person; there is no ledger test. The gate-less path keeps `files == [board]` too. **In code,** agent-cadence's shared `classify_direct` (check_cadence.py:1616-1647), which both the PR row and the direct-commit audit use, stops classing an item that gains `Decided:` with a gate in its Context as a plain board edit and defers it to `lift_pr_verdict`; fixtures cover such a PR (in the closed form, now the common same-repo case), the same change as a direct commit, and a cross-repo item with an extra ledger file. Without it, the carve-out doesn't apply and the PR takes ordinary review, for decisions as well as events;
  - (a) **the board commit's action is `decide`**, read by a new module function `edit_action(subject)` (v2.3; `subject_kind` gives only `edit`, ledgerboard.py:1306);
  - (b) **the board diff is one item, whose head line equals `edit_line(base_line, "decide", label, by, today, close=closes(item, label, entries_after))` byte for byte**: it gains `Decided: <label> (by <person>)`, and is also closed exactly when `closes()` says so. `closes(item, label, entries_after)` (module, v2.4) is true, on an item whose `Context:` names a gate, for a waiting-only label (`Closed: D — kept waiting.`) and, on an item whose Context names this repo's entry (a bare `TD-n` ref; a `<repo>#TD-n` ref is cross-repo), for a lifting label when **nothing listed still carries the gate after the write** (`Closed: D — lifted.`): neither the Context entry nor any `Parts:` id, read from `entries_after`. After `decide_lift`, which lifts every listed part, that always holds; after a single-entry `set by=` on a shared parent snapshot it does not, so the item stays open, matching the `; shared board item left open` Log line (the parent-snapshot fixture asserts it). *(Amended 2026-11-11, TD-067: the item stays open and unanswered — the `set by=` route's board half writes no `Decided:` on it — where it stayed `decided`.)* A cross-repo lifting answer stays open until its tool PR merges (§1.2's close rule). So a work-order answer can't be closed under the carve-out, and a finished one can't be left open to sit at the top of `needs_you`; fixtures cover each. **(b)'s `today` is the head line's `Decided:` date** (the board's local date, which `close=` also writes as the `Closed:` date), not (c)'s UTC Log date: the two may differ by a day (§3.1). `lift_pr_verdict` windows each date on its own. (c)'s UTC Log date: within one day of the PR's `createdAt` and not after its merge. The local `Decided:` date, which may run a day ahead of UTC east of Greenwich: `createdAt_utc − 1 ≤ D ≤ merge_utc + 1`. Fixtures: a `Decided:` one day ahead of both UTC dates passes; two days ahead fails. A PR whose answer logs nothing (whenever `decide_lift` changes no entry: a waiting-only or a lifting answer when no listed entry still carries the gate) is windowed by the `Decided:` date alone, where the base line has no `Decided:` at all (`item_key` strips it, so the key test alone can't tell). A re-answer takes ordinary review;
  - (c) **the ledger change is exactly what the module would write.** A new pure function, `decide_lift(item_line, entries, label, by, today, board_people, answered_by) -> {id: new_text}`, takes the item and the base text of its Context entry and `Parts:` entries. It returns each changed entry's new text, applying every rule once. **It covers whichever gate the Context names**, a `decision (<p>)` or an `event (<name>)` (the sweep's "still waiting?" and "impossible" items, whose lifting answer is `Drop the gate`). For an event:
    - **The board's people must match (decisions and events alike).** `decide_lift` takes the base board's `People:` and `Answered by:` (§6.2). It **refuses** a decision item whose gate's person is not on `People:` (case-insensitively), so a `decision (Bob)` item on a board that doesn't list Bob can't lift. It **refuses** an answerer (`by`) who is not on `People:`, and, for a decision under `owner` (the default), one who is not the gate's person. **An event item has no gate person, so anyone on `People:` may answer it, whatever `Answered by:` says.** A board with no `People:` can't be checked, so its lifts take ordinary review. Reassign stays consistent: a's item closes on a's board, and b's item is filed on a board that lists b.
    - **`by` is the answerer the head's `Decided:` records** (`Decided: <label> (by <person>) (D).`, §6.2), for decisions and events alike. A `Decided:` without `(by …)` can't supply it, so that lift takes ordinary review. The person-started-session rule (§3.1) applies to every answer.
    - **A lifting label** (`Drop the gate`) writes `gate lifted: event (<name>) — by <person>; answer "<label>"` and removes the gate. The Event section stays (§4.2).
    - **`Keep waiting`** writes `kept waiting`.
    - **Any other label writes no ledger line:** "Rewrite the check" is a body edit under ordinary review, and "Drop the entry" hands off to `archive --dropped`. The rules below are stated for a decision, and apply to an event the same way:
    - a label in `Lifts:` removes `decision (<p>)` and logs `gate lifted` on the Context entry (if it carries the gate) and on each listed part that does;
    - a listed part that no longer carries the gate is logged as `gate lift skipped: TD-n no longer carries decision (<p>)` on the Context entry;
    - any other label logs `kept waiting` on each of those same entries that **still carries** the gate, so each gate's age resets;
    - labels compare case-insensitively against `Lifts:` (and `Go` when it is absent), as answers do;
    - `<p>` is compared case-insensitively, and the Log uses the header's spelling;
    - an emptied `Blocked by` is removed in canonical form.
    
    **The checker's inputs**, all taken from the PR:
    - `item_line` is the **base** board line;
    - `label` is the head's `Decided:` label, without its `(by …)`;
    - `entries` are the base texts of the Context entry and the `Parts:` ids;
    - `by` is the head's `Decided:` answerer. The Log writes it as given; the gate's person in the Log's `gate lifted: decision (<p>)` keeps the header's spelling;
    - `board_people` and `answered_by` are the base board's `People:` list and `Answered by:` value (absent `People:` means (a0) has already sent the PR to ordinary review; absent `Answered by:` means `owner`). The signature is `decide_lift(item_line, entries, label, by, today, board_people, answered_by)`;
    - `today` is the date on the PR's new Log lines (head lines absent at base). They must all carry the same date, which must be within one day of the forge's **PR `createdAt`** UTC date and not after the merge date. `createdAt` can't be forged, unlike a commit's author date, and is the same before and after merge, so the writer's UTC date is reproducible however late the PR merges.

    The checker applies `decide_lift` to the base and requires the head's ledger files to be **byte-equal** to its result, with no other file changed. That one test replaces line-by-line rules and admits nothing else. `decide_lift` **refuses** an item whose Context entry is archived or missing at base, or a `Parts:` id that is missing, so such a PR takes ordinary review. **Lift PRs are squash-merged**, as the board carve-out already assumes (`_tool_pr_commit` finds the PR's one commit, check_cadence.py:1646).
  - (d) **a PR only.** The direct-commit audit (`classify_direct`) keeps refusing a two-file commit, and from v2.4 also refuses (class `fail`, "a gate item's answer lands by PR only") a board-alone direct commit whose one item gains `Decided:` with a gate in its Context; the direct-commit fixture expects `fail`. agent-cadence's wrapper never lands such a decide by direct push, whatever `ALLOW_MAIN_PUSH` says (board_edit.py:43-46).

  A PR that has any `; board`, `; no board item` or `; shared board item left open` suffix, or any host `event` lift, `until`, override or reassign line, can't equal `decide_lift`'s output, so it takes ordinary review.
- **Another repo's entry (`other#TD-n`):** the consumer opens a tool PR there, whose change `ledger.py lift … --board <repo>` writes in a clone of that repo, and the item stays decided-but-open until that PR merges. A waiting-only answer on such an item closes it board-alone and needs no tool PR: the sweep's re-ask window reads the board's `Decided:` date (§1.2), not a `kept waiting` line. That PR touches only the entry's ledger, so it is never a lift PR: **it always takes ordinary review, and a person merges it.** **[proposed]**
- **Every `decision (person)` should have a board item**, or the person has nothing to answer. **[proposed]** `check()` can't see the board, so the merge gate checks it. It reads both files and flags:
  - a new `decision (person)` that no open `decide` item covers (§3.2); it reads the local board and any roster clones already fetched, and only **flags** (never refuses) when coverage depends on another repo's board, so its verdict never depends on which machine runs it;
  - (and the person's card shows the item's Context entry and gate, so a click on an agent-written item lifts what it visibly names).
  - a decision's item with no lifting answer.
- **One go for a parent's parts** **[agreed 2026-11-02]**.
  - A `decide` item may name a **parent**, a person's gate, and a snapshot of the parts it asks about: `Context: TD-12 decision (Paul). Parts: TD-15, TD-16.` `Parts:` is its own item field, after Context and before Due, valid only on a `decide` item. It joins `CONTEXT_RE`'s lookahead and the field and sanitising regexes (ledgerboard.py:774, 1056-1058), so its ids are not Context refs and Context still names exactly one entry, and a reply can't forge it. It is part of the item's key, because a changed snapshot is a different question. A listed part that no longer carries the gate when the answer comes is skipped, and that is logged on the parent.
  - A lifting answer lifts the gate on the parent, if the parent carries it, and on **only the listed parts**, logging a `gate lifted` line on each.
  - A part filed after the item was written isn't listed, so the answer never lifts it. It needs its own item, or an updated snapshot.
  - The parent need not carry the gate itself.
  - The writer refuses a snapshot whose parts don't all carry that gate, or aren't all `Part of` the named parent.
  - The item still names exactly one entry. Parts that need a different Ask get their own items.
  - *(Amended 2026-11-04, TD-050: `docs/plans/TD-050-parts-writer.md`)* The writer, `item_line(parts=)` and `board.py add --parts` (after v2.5), writes a snapshot only under a `decision (<person>)`; an `event (<name>)` snapshot is still read, and lifted by `decide_lift()`, but not written.
- **Hide until** **[agreed 2026-11-02]**. An item may carry `Hide until: D.` The item line's order is `Context: … [Parts: …] [Due: D.] [Hide until: D.] [replies] [Answers: …] [Lifts: …] [Decided: …]`. An `fyi`, which has no Due, may carry it straight after Context.
  - **It never changes the item's key:** `item_key` strips it, like Due. SPEC's rule, that changing what the key is for a given line is a major (SPEC:343), stays as written. **[agreed 2026-11-02: strip in v2.3]** Stripping `Hide until` in v2.3 is an exception to that rule. Stated honestly:
    - It can re-key only a line that already holds the prose `Hide until:`. Each consumer's v2.3 vendor PR shows that none of *its* boards holds one (none does today), and each roster repo's remodel shows the same for its board.
    - What remains is a board nobody inspects, holding a hand-written `Hide until:` whose key a consumer has stored. That item would be seen as new once, and re-filed or re-answered. I judge the risk acceptable, but it is a judgement, not a proof.
    - The alternative is to keep `Hide until` in the key until v3.0. Then hiding an item re-keys it, which breaks the stored keys that snooze exists to protect, until v3.0.
  - **`item_record`** (the board's JSON and the fixtures' shape, ledgerboard.py:1027) gains `hide_until` and `hidden` keys. `snooze`'s read-back self-check (:1159) asserts `hide_until == to` with Due unchanged; `due` keeps the old check. `item_problem()` notes (ℹ) a `Hide until` in the past, and `snooze` replaces any existing one, so a stale date doesn't linger. *(Amended 2026-11-03: both notes are `item_notes(item, today)`, which no gate reads, not `item_problem()`; [TD-023's plan](TD-023-hide-notes.md).)*
  - **The module** adds `BoardItem.hide_until` and `hidden(today)`. `overdue_days` and the due tag still measure the real deadline. **A hidden item is neither surfaced nor escalated, **except a `decided` one, which is a session's work order and is never hidden** (§1.2):** readers that list what needs the person, or escalate overdue items, skip it until D. Once D arrives it reappears with its true overdue count.
  - The name joins `CONTEXT_RE`'s lookahead and the reply and answer sanitising regexes (ledgerboard.py:774, 1056-1058), so a Context never swallows it and a reply can't forge it.
  - The rest: Readers leave it out of the "needs you" lists until D, while keeping it on the board, and its `Due:` (the real deadline) is untouched. `item_line(…, hide_until=)` writes it on a new item. **On an existing item, `snooze` now writes or updates `Hide until` and leaves `Due:` alone** (today it rewrites Due, ledgerboard.py:1142, 1194; its subject stays `snooze … to <date>`). A new edit action, **`due`**, moves the real deadline, with subject `due … to <date>`. `fmt` never touches either. `due` joins `EDIT_ACTIONS` and `EDIT_SUBJECT_RE` (:1055, :1269). A `snooze … to D` subject means "moved Due" before v2.3 and "hidden until" from v2.3. That is history in git, not text a reader acts on, and SPEC notes it. `item_problem()` notes (ℹ) a hide-until later than the item's Due, because that hides the deadline itself. A new reply or an escalation that wakes it early is consumer behaviour.

**Item keys under `fmt`** **[agreed 2026-11-02: (a)]**. Rewriting a line changes its item key, which ShiftLead stores. The rule is (a):
- (a) rewrite only the lines whose key doesn't change;
- (b) only report;
- (c) ShiftLead migrates its stored keys.

### 6.1 Rank keys stay short **[agreed 2026-11-02]**

`midpoint()` writes a key strictly between its neighbours. Repeated drags into the same gap make keys longer without limit (Jira's LexoRank warns at 128 characters and rebalances at 160).
- `check()` notes (ℹ) a rank key longer than 64 characters. The implicit key is about 20.
- A new rank writer, **`respace`**, shortens keys **without moving anything relative to a key it does not own**.
  - Fixed points are every key that isn't a line in this file: the implicit keys of un-lined entries, plus any other repos' keys the caller passes in. ShiftLead sorts several repos together by key (`rank.py:52`).
  - The lined keys between two consecutive fixed points are rewritten to short, evenly spaced keys inside that same gap, in the same order. Equal keys stay equal, so lowest-id ties hold.
  - It lands in one commit of its own that changes the rank file alone, with the subject action **`respace`**, which joins `rank | join | prune`. Its subject is `queue: respace TD-a, TD-b, … (<why>)`, listing every rewritten id as the other actions do, so `QUEUE_SUBJECT_RE` (ledgerboard.py:519) only gains the word. Consumers that store keys (ShiftLead's `ranks.json` flush signature) flush on it.

### 6.2 A board's people **[agreed 2026-11-02]**

A board can belong to one person or to a team. Teams are a use case the format supports from the start; a one-person board is the case of one name.

- **`People: a, b, c`** is a board preamble line (v2.3), replacing draft 30's `Person:`. It lists one or more people in the person grammar (§3.1), comma-separated, compared case-insensitively.
  - **Read by** a new module function `board_people(content) -> list[str] | None` (v2.3), with `answered_by(content)` beside it in v2.4. `parse_board` keeps its shape (`list[BoardItem]`, ledgerboard.py:939).
  - **Checked by** `board_problems(board, old=None) -> list` (v2.3, TD-008's plan §2, which this extends): `item_problem` on each item, plus the preamble (a missing `People:` noted (ℹ), since lifts on that board then take ordinary review; a malformed one or a duplicate name flagged) and a `decide` item whose Context gate names someone not on `People:`. agent-cadence's merge-gate board row and the sweep call it. A v2.2 reader ignores it (`parse_board` reads only item lines, ledgerboard.py:947).
- **Every answer records who gave it:** `Decided: <label> (by <person>) (YYYY-MM-DD).` (v2.3). `board.py decide --by <person>` writes it.
  - **Where `by` comes from:** when the board's `People:` lists exactly one name, `--by` defaults to it, which is deterministic and the common case. On a board with no `People:` line (a roster board before its remodel), `--by` is required, checked against the person grammar only, and the write proceeds, the two-file lift included: `decide_lift(…, board_people=None, …)` skips the `People:` and `Answered by:` checks but still requires a decision's `by` to be the gate's person. `lift_pr_verdict` never reaches it for such a board, because (a0) sends the PR to review first. A repo whose board has no `People:` files no gates until its remodel (§7.2 step 2); `board_problems` notes the missing line, and (a0) keeps it from the carve-out. No item covers a gate on a board without `People:`, so every lift there, by `board.py decide` as well as by `set by=`, is written with `; no board item`, which the tripwire accepts, and the PR takes ordinary review (fixtures expect that pass for both routes); this also serves the remodel's "lift a stale gate" (a fixture shows it). Otherwise `--by` is required, and the consumer supplies the name of the person driving the attested session (ShiftLead's person session; agent-cadence's own setting for the person). The writer refuses a `by` outside the person grammar or not on `People:`. **Git's `user.name` is never a source:** agents commit under it, so it proves nothing (§3.1), and it may not fit the grammar. The `(by …)` sits inside today's `Decided:` text, so a v2.2 reader still reads the item as decided, still strips the whole field from the item key, and shows the label with `(by …)` after it. The writer refuses an answer label that itself ends in `(by …)`, a typed `Not right: …` form included, which is intended.
  - **One reading change, named:** principle 7 says the same bytes never mean two things under two releases. A pre-v2.3 line whose `Decided:` text happens to end in `(by <word>)` is the one exception. Its `decided` text loses that ending, and the ending becomes `decided_by`. A fixture shows it. As with `Hide until`, each consumer's v2.3 vendor PR shows none of its boards holds such a line.
  - **Parsing:** only a final `(by <person>)` before the date is split off, with `<person>` in the person grammar. `BoardItem.decided` keeps its shape, `(label, date)`, now with the label alone; a new `BoardItem.decided_by` holds the person or none. A v2.2 line such as `Decided: Go (by Friday) (D).` therefore reads as label `Go`, by `Friday`. That fails safe, because `Friday` is on no `People:` list, and a fixture shows it.
  - `item_record` (the fixtures' JSON, ledgerboard.py:1039) gains `decided_by` beside `decided: {text, date}`. `edit_line`'s `decide` gains a `close=` form (v2.4), which writes `Decided: <label> (by <p>) (D). Closed: D — <reason>.` (D the board's local date; the reason is `kept waiting` for a waiting-only label, else `lifted`, and the read-back checks it); its read-back uses `parse_closed_items` when closing, and checks the label, the date, the `by`, the closed date and an unchanged `item_key`. Otherwise the `decide` read-back check (:1179) compares the label, the date and the `by`, and the other read-backs that compare `decided` (:1162, :1206) compare `decided_by` too. `decided_line()` (:1255), which writes a work order's already-decided line, takes `by` as well.
  - A `Decided:` without `(by …)` stays valid (every one written before v2.3); a lift from it takes ordinary review.
- **`Answered by: owner | any`** is a board preamble line (v2.4, with `decide_lift`). It says who may give a lifting answer on that board:
  - **`owner`** (the default when the line is absent): only the gate's named person, as in §3.1;
  - **`any`**: anyone on the board's `People:` list, whoever the gate names. The Log's `by` records who actually answered.
  - A one-person board reads the same either way.
  - Either way, a decision item belongs on a board that lists the gate's person (coverage, §3.2), and only person-started sessions answer (§3.1).
  - The `set` route stays the named person's. On an `any` board a teammate lifts through the board item, which is the normal route; with no item, they use the override route. A reassign between two people on the same board still closes a's item and files b's, because the item's key names the gate's person. The merge gate enforces it too: outside a carve-out lift, a `by` other than the gate's person is flagged, and review decides (§3.1).
- **Later, when the first team board exists:** an optional item field `For: <person>`, so each person's view shows their own items. A decision item is already for its gate's person. It is additive in a minor release.
- **Identity is the limit.** On a one-person board, "the person's click is the review" rests on the session being person-started. On a team board, one person's session could record another person's name. Proving who answered (for example, matching the forge account that opened the PR to `by`) is consumer work for when teams arrive. Until then, review is the backstop, as §3.1 says.
- **Rank** is the board's repo's one rank file. On a team's repo it is the team's order; SPEC's "a person's order" is reworded to "the order its people set".

---

## 7. Getting every repo to the target

### 7.0 The entries that carry it **[go 2026-11-02]**

Paul's go, 2026-11-02 ("Lets commit and start implementing"), covers this design and TD-008's plan (`docs/plans/TD-008-board-writers.md`, the designer's, 2026-10-31).

- **TD-008's plan is v2.3's module spec for the board writers** and stands as written. Its builds B1–B3 (`item_line()` for every kind; `item_problem()`, `canonical_item()`, `board_problems()`; `archive_closed()`) are filed `Part of: TD-008`. Its C1 is this design's `fmt` rule (a) (§6). Its `board_problems(board, old)` gains the preamble checks of §6.2 in B7. Its *The builds* section sends the board CLI to an agent-cadence `board.py` entry; under §1.1 that CLI is ledgerboard's `board.py` (B5), and agent-cadence keeps a wrapper.
- **The rest of v2.3** (§7.1) is filed as builds B4–B8 (TD-015–TD-019; B1–B3 are TD-012–TD-014), also `Part of: TD-008`, in series after B3, since every build edits `SPEC.md`, the module and `fixtures/run.py`:
  - B4: the package (§1.1), with `release.sh`, `fixtures/run.py`, the tests and the boundary text in AGENTS.md and README;
  - B5: `board.py`, the file-level board and rank writer (§1.1), with `--plan` and write-both-or-neither;
  - B6: `Hide until`, `snooze`/`due`, `edit_action`, `hidden()`, `needs_you` and the one-time key exception (§6, §1.2);
  - B7: `People:`, `board_people`, `board_problems`' preamble checks, and `Decided: … (by …)` with `decided_by` and `decide --by` (§6.2);
  - B8: the `Lifts:` and `Parts:` fields, the rank-key note and `respace` (§6, §6.1), and the grammar appendix's start.
- **v2.4 and v2.5 wait for v2.3.** TD-010 and TD-011 lose their `decision (Paul)` gates and are blocked by TD-008 instead; their builds are filed from §7.1 once v2.3 is released.
- **Consumer work is filed on each consumer's own ledger**, never from here: the ADR amendment (ShiftLead, step 0), and each consumer's step-0 vendor PR.

### 7.1 Releases **[agreed 2026-11-11]**

| Release | Contents |
|---|---|
| **v2.3** | TD-008: the board writers, shipped as ledgerboard's `board.py` (§1.1); `Hide until`, with `snooze` writing it, the new `due` action, `edit_action(subject)`; the board's `People:` preamble line, `board_people`, `board_problems` and `Decided: … (by <person>)` (§6.2); `Lifts:` (its field, order and key; the lift semantics come in v2.4); `Parts:` (its field, order and key; the writer that fills it and checks the parts' gates comes in v2.4), the module's `hidden(today)` and `needs_you` (§1.2), and the one-time item-key exception (§6); the rank-key note and `respace`; SPEC's grammar appendix starts (the board item line, the rank file) |
| **v2.4** | ledgerboard's `ledger.py` (§1.1); `ids_held`, `next_id`, `parse_take`, `judge_takes` and the counter in SPEC, `lift_gate`, `origin_path`, `parse_closed_items`, `waiting_only`, `closes`, `board.py decide --board-only`, `sweep()` and `covers()`, `lift_pr_verdict`, `tripwire` and `uncovered_decisions` (§1.2); TD-010, TD-011, the events entry: the gates (decision, until, event); `Answered by:` and `answered_by` (§6.2); `origin_key` and the multi-component `<repo>` grammar (§3.2, §4.1); **the Log** (the section, its fixed shapes, "Log last", writers appending to it, and creating `**Log:**` when an entry lacks one), because lifts, the sweep and `decide_lift` need it. **From v2.4, `new`, `note`, `archive` and `reopen` write the Log line only:** Status becomes `<word> <date>` with no note (`Open` bare), and `Added` a bare date. **Before writing, `archive`, `reopen` and `note` lift any existing Status note into a dated Log line** (migrate's own step, applied to that entry), so no note is lost before v2.7. Both are forms v2.2 readers read. `decide_lift`, and the lift semantics of `Lifts:`; the tightened repo grammar (§4.1); the ledger writers refusing a naive datetime, with callers fixed in the same vendor PR (§3); with `Waits` kept in canonical order (the module never reads it as a gate; ShiftLead reads it until v2.7); the decide lift's module half (lifting answers); the supersede/drop rule; event sections and the three check types; `pickable(…, today)`; the Priority check; `parts_gates`; reassign and override lift; the grammar appendix adds `Blocked by` and Event sections |
| **v2.5** | TD-044 (`fixtures/MANIFEST`), TD-045's builds (TD-047, TD-048) and TD-049's `check()` fix, tagged ahead of the Status release |
| **v2.6** | TD-050's `Parts:` writer (TD-054, TD-055: `item_line(parts=)`, `parts_problems()`, `board.py add --parts`; the v2.3 row placed it in v2.4, which did not ship it) and TD-051's archived-part decide lift (TD-052) |
| **v2.7** | the closed Status set; the Log's migration (old Status notes and `Added` comments into Log lines, in date order, for any entry whose Status still has a tail or whose `Added` still holds a comment); `Location` to the body; `Waits` out of the canonical order and flagged by `check()`; `Kind` per §2.3's decision; the grammar appendix adds the header and the Log lines (including `while TD-m`) |
| **v3.0** (later, a major) | stops reading what v2 kept only for old files: `Waits`, `Taken by`, the old `decision (who) — text` form, a `Resolved` header field, and `migrate` with them (*amended 2026-11-11, TD-058's S7*: `migrate` ships in v2.7 and stays through every v2.x, since roster repos still migrate and a stale branch can bring old forms back). Planned once every repo is on v2.7 and has no such lines: its precondition is that `migrate --plan` shows no entry with changes in every roster repo, which covers archived entries (`check()`'s retired findings read open entries only), and that no entry, open or archived, still holds an old form `migrate` leaves (`Waits`, `Taken by`, the old decision form, a header `Resolved`), an open entry's are each repo's to rewrite through the writers; an archived entry's have no writer route yet, and v3.0's design gives them one. *Amended 2026-11-12, TD-078 ([its plan](TD-078-v3-ledger-half.md)):* the route is the last v2.x minor's: `note` takes an archived entry, and `migrate` maps `Taken by`, `Waits`, a header `Resolved` and the old decision form; the precondition is `migrate --plan`, run with that minor, showing no entry with changes or stops. *Amended 2026-11-11, TD-070:* v3.0's design also takes up the board as a directory, one file per item named by a stable item id (TD-070, design-first; it may conclude that the single file stays), since a v2 reader cannot read one. *Amended 2026-11-13, TD-096 ([TD-078's plan](TD-078-v3-ledger-half.md) D5, D7), on Paul's input:* the precondition binds the repos that take v3.0 when it is cut, ledgerboard, agent-cadence and ShiftLead, not the roster repos; a roster repo is untouched by v3.0 until it bumps its own pin, and its one remodel (§7.2 step 7) first bumps to the agent-cadence commit its v3.0 vendor PR names (the newest on its `main` then that vendors the last v2.x minor and passes the remodel procedure's test), runs that minor's `migrate` and the same check there, then bumps to v3.0. |

The Status release was called v2.5, then v2.6, before those two were tagged ahead of it; it is **v2.7**, and
wherever this document says v2.5 or v2.6 for that work, read v2.7.

*(Amended 2026-11-04, TD-045: `docs/plans/TD-045-host-log.md`)* `host-log`, *Host-log checks*, `gate_added()`, `event-undated` and `set`'s `gate added` lines ship in the release that ships TD-045 (the next tagged after B2 lands); the reader is agent-cadence's. §7.3's *for a host-witnessed event, `until` plus a re-check entry* stands under v2.4; the re-check entry becomes a `host-log` gate once the release is live on a host that declares the repo.

Each release changes the canonical form, so **each consumer's vendor PR carries its own reformat** (`fmt` / `migrate`). Otherwise every changed entry fails that repo's merge gate. A repo on an older pin is untouched by v2.7 until it
bumps; its one remodel converts its `Waits` lines then (§7.2 step 7, after v3.0, since TD-096). *(Amended 2026-11-11, TD-058: the line
"v2.7 waits until every repo has moved its `Waits` lines to gates under v2.4" is dropped; read literally it held
v2.7 on the roster repos whose ledgers still hold `Waits` lines.)*

### 7.2 Order of moves

0. **The boundary change** (§1.1): the ADR amendment, a ShiftLead PR the techlead reviews, and this repo's AGENTS.md and README. Then **ledgerboard v2.3**, then your release. **Each consumer vendors it in one PR, together with its v2.3 work**, so the `snooze` change and the readers that honour it land together:
   - **both:** every reader of the old single `ledgerboard.py` moves to the package, as §1.1 lists them;
   - **agent-cadence:** `board_edit.py` becomes a wrapper over ledgerboard's `board.py`, which brings `due`, and passes `--by` on every decide; the sync copies the package (the module and `board.py`; `ledger.py` joins it in v2.4); `nudge_user_attention.py` surfaces and escalates from `needs_you` (§1.2), so hidden items are skipped (it ranks by `overdue_days`, :249, :329); `user_attention.md`'s "to snooze, edit the Due date" (:25) is reworded;
   - **ShiftLead:** its pin bump to agent-cadence's step-0 release, in the same PR as its vendor of the package (§1.1), so agent-cadence's step-0 release comes first; its `sessionorc/board.py` calls ledgerboard's `board.py` for every board write, exposes `due`, and the inbox reads `needs_you` (§1.2);
   - **every board** gains its `People:` line, in its consumer's v2.3 vendor PR or, for a roster repo, its remodel;
   - **both:** the `Hide until` data check (§6).
1. **ledgerboard:** v2.4, then your release.
2. **Both consumers vendor v2.4, each with its reformat, before any repo writes a new gate.** Under v2.2, the merge gate refuses one.
3. **agent-cadence:**
   - the v2.4 vendor PR;
   - `ledger_next_id.py` and the merge gate call `ids_held`, `next_id` and `judge_takes` (§1.2); adopt `origin_key` for the board pick, emit the lowercased origin path in ids, and prefer an exact path match in `ledger.py`'s `_find`;
   - `forge.py` adds `createdAt` to `PR_FIELDS` and the neutral PR record (today only the open-PR listing has it, :234-237, :406-412), so the merge gate can check a lift's date;
   - its `ledger.py` becomes a wrapper over ledgerboard's `ledger.py` (gates, `archive --dropped`, `set --override`, `migrate` over the module's pure `migrate_entry`), keeping the id counter, the roster resolver and the git date lookup it passes in;
   - its writers' dates switch to UTC (`datetime.now(timezone.utc).date()`);
   - the `set by=` wrapper sequence (§1.1), with a fixture for each suffix, in the same PR that turns the tripwire on;
   - the decide lift through ledgerboard's `board.py decide --by`, written as one lift PR, and `check_cadence.py`'s carve-out widened to accept that shape by calling `lift_pr_verdict`, with `tripwire` and `uncovered_decisions` on every PR (§1.2);
   - the event runner, and the gate sweep's I/O around the module's `sweep()` (§1.2);
   - the merge-gate check that each new decision has a board item;
   - cadence.md and layer wording;
   - TD-188 steps 2–4.
4. **ShiftLead:**
   - adopt `origin_key`, emit the lowercased origin path in ids, and prefer an exact path match in `ledger.py`'s `_find`;
   - bump its agent-cadence pin to step 3's release first, so its board-and-ledger lift PRs meet the widened carve-out (it runs `check_cadence.py` through that pin). The tripwire turns on with that pin, so the pin bump, the conversion of `sessionorc/ledger.py` to call `ledger.py lift` and `board.py decide --board-only`, and the `set by=` sequence are one PR;
   - the sync PR (the package is already vendored at step 2); its `sessionorc/ledger.py` calls ledgerboard's `ledger.py` for every ledger write (so ledger dates are UTC there), and workorders.py's board dates stay local;
   - **remove Hold, Release and prehold before its remodel**, turning each recorded hold into `decision (Paul)` with an Ask, so the two never exist side by side. In the same step, turn each entry that `Owner: paul` holds today into `decision (Paul)` with an Ask, so that `Owner` stopping holding leaves no gap;
   - the `set by=` wrapper sequence (§1.1), in the same PR that turns the tripwire on;
   - the decide lift through ledgerboard's `board.py decide --by`; read `pickable()` with its new signature; live checks wait on an event gate, not the `Kind` comment; `Owner: paul` stops acting as a hold;
   - the event runner, and the gate sweep's I/O around the module's `sweep()` (§1.2);
   - the same merge-gate check;
   - the clock keeps only settling.
5. **Each consumer's remodel under v2.4:** one session per repo, started there. **[agreed]** agent-cadence and ShiftLead go first and are run and tested in use (done: as of 2026-11-10 both vendor v2.6, hold no open `Waits` lines, and have run remodelled since about 2026-11-02). The roster repos take no v2.4 remodel of their own (step 7).
6. **ledgerboard v2.7**, then both vendors with `migrate` (the Status words, the Log), and ShiftLead removes `Waits = until | event` from its `Fields:` line in the same PR. The roster repos take no v2.7 remodel (step 7). *(Amended 2026-11-11, TD-058, on Paul's note; amended 2026-11-13, TD-096, on Paul's input: the roster repos are not worked until ledgerboard, agent-cadence and ShiftLead are in shape, so their remodel moves after v3.0.)*
7. **After v3.0** (cut, and vendored by both consumers): **each roster repo**, when its own team picks it up again, gets **one remodel**: one session and one PR that bumps its agent-cadence pin twice ([TD-078's plan](TD-078-v3-ledger-half.md) D7), following agent-cadence's remodel procedure for the commands and their order, and starting only once that procedure has merged. First to the commit agent-cadence's v3.0 vendor PR names (the newest on its `main` then that vendors the last v2.x minor and passes the procedure's test); under it the remodel splits a ledger still in one file, does §7.3's v2.4 and v2.7 steps and runs that minor's `migrate` (which stays usable there after v3.0 removes it, since that commit still carries it), and the PR shows the check between the bumps (a v2 directory, `migrate --plan` with no entry with changes or stops, every entry canonical, no open entry's `Blocked by` holding `hold` or the reserved role `decision (designer)`, `ledger.py --check` with no error, the board with its `People:` line and in `fmt`'s form; read by the techlead who merges); then to a commit that vendors v3.0, where it does §7.3's v3.0 steps. The merge gate grades the PR under the v3.0 pin, so each decision the remodel writes gets its board item in the same PR. The first bump is also a long agent-cadence jump (as of 2026-11-10 the roster repos pin an agent-cadence from 2026-10-29, before the vendored package, about 179 commits behind), so each team meets new cadence behaviour in the same PR. **Order: quiet first** — of the four roster repos, the fewest stops first, counted when the remodels begin in a scratch clone of each repo (bumped to the last v2.x pin and split there, then `migrate --plan`, and thrown away) (as of 2026-11-10, the two whose ledgers hold no `Waits` lines before the two that do), one at a time. *(Moved from step 6, 2026-11-13, TD-096.)*

### 7.3 What each remodel session does

**Mechanical** (`ledger.py migrate --dry-run`, then without):
- **under v2.4:**
  - `Waits: until DATE` → `until DATE`, and each gate the remodel writes from a `Waits` line gets a `gate added` line dated the remodel day, since the remodel reviewed it (from v2.8 `migrate` stops on an open `Waits` instead, rule 6, so a roster repo's remodel writes each such gate with `set`, the session's step, TD-096);
  - the old `decision (who) — text` → `**Ask:**`;
  - `fmt` over the board under the key rule;
- **under v2.7:**
  - Status notes and `Added` comments → Log lines;
  - archived Status words, by the map in §2.2;
  - stage words on open entries → `Open` + a Log line + `Kind`;
  - `Location` → the body;
- **under v3.0** (a roster repo's second bump, step 7): the board's split, as TD-070's second part (TD-095) designs it.

**Judgment** (the session, which knows the repo):
- **Each `Waits: event`:**
  - a typed check if one fits;
  - otherwise a judgment entry blocked on by id (§4.3);
  - otherwise, for a host-witnessed event, `until` plus a re-check entry;
  - otherwise ask you.
- **Each `decision (who)`:** keep it with an Ask; turn a role into `Kind`; lift a stale one (TD-188).
- **Each ShiftLead Hold still recorded:** becomes `decision (Paul)` with an Ask, or is released.
- **Each closed entry with a Status word outside the set:** Resolved, Superseded or Dropped.
- **Each dependent of a superseded or dropped entry:** rewired, or put to you.

**The PR includes** the before/after list, the dry-run output, and a passing `check()`; a roster repo's also the check between its two bumps (§7.2 step 7).

**Order** **[agreed 2026-11-02]**: agent-cadence and ShiftLead first, as the first consumers. Both run on the new releases and are tested in use before any roster repo's remodel starts; what that use turns up is fixed in ledgerboard and both consumers first. Then the roster repos, one at a time, each in one remodel after v3.0, in §7.2 step 7's order (amended 2026-11-13, TD-096: it was on each one's v2.7 bump). **Who merges** **[agreed 2026-11-02]**: each team's techlead merges its repo's remodel PRs. A team does no other work until its rewrite has merged.

### 7.4 Fixtures each release adds **[agreed 2026-11-01]**

- **Unknown text survives:** an entry with an unknown header field, an unknown gate, an unknown body section and an unknown Log prefix goes through `edit`, `fmt` and `migrate` and comes out with that **content** unchanged (each unknown field's name and value, the section's text, the Log line), placed per canonical form. A header line that is not a field is refused, not dropped.
- **Retired words:** each reserved word reported as *retired* with its replacement, not *unknown*.
- **Cross-version:** a v2.4 reader (whose fixtures stay in the suite) resolves an `other#TD-n` whose archived Status is a word it does not know (a later minor's, such as `Withdrawn D`), keeps the block, and flags it (`cross-unknown-status`). More generally, a minor reader never reads a block as lifted on a Status word it does not know, nor a closed entry as open. Two releases remain, by design: a known word on the wrong side of the archive (`Open`, `Moved`, `OBE` …) releases until v2.7's remodel, and so does a resolver that gives no `status`, by the host's choice (*Amended 2026-11-04, TD-039: `docs/plans/TD-039-unknown-status.md`.*).
- **`migrate`:** running it twice gives no diff; an unmapped Status word stops it with a list and writes nothing.
- **Repos and origins:**
  - `origin_key` on scp-style ssh, `ssh://` with a port, https with userinfo, a trailing `/` and `.git`, and mixed case;
  - none returned for `file://`, a plain path, and a path that fails the grammar;
  - `origin_path` on a mixed-case origin giving a lowercased id;
  - two item lines differing only in `<repo>` case having different `item_key`s;
  - `<repo>` accepting three components and `owner/.github`, and refusing `a//b`, `a/../b`, `./x` and `-x`.
- **Check arguments:** each confinement refusal (option-like and revision-syntax refs, a non-hex commit, a `..` or `%` path, a URL repo), and quoted text that holds quotes.
- **UTC:** a naive datetime refused, an aware one converted.
- **Old-form guard:** adding a gate to an entry with `decision (who) — text` is refused.
- **Supersede edge cases:** a chain, dedupe and a cycle.
- **Grammar:** each EBNF production in SPEC's appendix has at least one fixture that accepts and one that refuses. **The fixtures are the authority**; the EBNF is informative, and a test checks every fixture against it so the two can't drift.
- **Parents and overrides:** `parts_gates` on a parent; one go naming a parent lifts each part's gate; reassign; an override lift without a reason refused.
- **Board and rank:**
  - `Hide until` written and read, with and without Due, and on an `fyi`;
  - `item_key` unchanged by hiding;
  - a Context followed by Hide until;
  - a reply that tries to forge it;
  - a hide-until later than Due noted;
  - a hidden item not surfaced and not escalated, then reappearing with its true overdue count;
  - `Parts:` not read as Context refs, and a reply forging `Parts:` refused;
  - `respace` keeps the order against implicit keys and passed-in keys, keeps ties, and shortens keys;
  - a long key noted.
- **`decide_lift`:** a lift, a kept-waiting answer, a skipped part, a parent that doesn't carry the gate, a case-differing person, an emptied `Blocked by`, and `Lifts:` with two labels; the checker's byte-equality accepting each and refusing an extra change.
- **Parent go:** a snapshot lifts only its listed parts; a mismatched snapshot is refused; the sweep counts a part's gate as covered.
- **Reassign:** b = a refused; more than two reassigns noted.
- **Log shapes:** each fixed shape parsed; a `note` beginning with a reserved prefix refused; renumber rewrites a `while` token.
- **Fixtures carry the release they apply to,** so a consumer can run the set for its own pin (CommonMark publishes its tests per spec version). *Designed 2026-11-04 (TD-040, `docs/plans/TD-040-fixture-release.md`):* the set, not each case, carries its release: `fixtures/MANIFEST`, stamped by `release.sh` and checked by `run.py --check-header`.

---

## 8. Decisions this draft asks for

1. The three gates (decision, until, event) and dropping `hold` (§3). *Hold's removal and the window: agreed 2026-10-31.*
2. **Only a lifting answer lifts a decision** (`lifts=`, default `Go`); any other answer is logged and the gate stays (§6).
3. Principle 4 (header for tools, body for readers): `Added` as a date, provenance and notes in the Log, with fixed shapes for writer-made lines.
4. Status: the closed set with `Dropped`, the migration map, an error everywhere from 2.5, and stages moved to `Kind` (§2.2).
4a. *Agreed 2026-11-02:* `Kind` is (i), a consumer field prescribed by cadence.md (§2.3). `Location` moves to the body.
4b. **v3.0** as the planned end of v2's old-file readings (§7.1).
4c. **Events are lifted only by text**: no `events` input to `pickable()`. Live checks wait on a deploy event gate. `Owner` never blocks (§3, §4).
5. Retire `Taken by` (TD-188), and lift TD-188's out-of-date decision now.
6. Events are mechanical only, and judgment is work blocked on by id. Three check types to start; `host-log` after shiftlead#TD-1295; filed with v2.4's builds.
7. The gate sweep (§3.2): its decisions are the module's `sweep()` (§1.2), run by the host: a decision with no board item, a broken check, and the 30-day "still waiting?".
8. Supersede rewires; drop refuses while dependents remain.
9. Three releases: v2.3 board; v2.4 gates with `Waits` still accepted; v2.5 Status, the Log, and retiring `Waits`.
10. *Agreed 2026-11-02:* item keys under `fmt` follow (a), rewriting only the lines whose key doesn't change (§6).
11. *Agreed 2026-11-02:* agent-cadence and ShiftLead first, tested in use, then the roster; each team's techlead merges its remodel PRs, and the team does no other work until its rewrite has merged (§7.3).
12. *Agreed 2026-11-01 (§0.4):*
    - writers keep what they can't parse;
    - reserved words;
    - four check outcomes;
    - fixed-shape lifts;
    - the named person lifts;
    - argument confinement and host rules;
    - idempotent lifts;
    - a stateless sweep;
    - the cross-version and `migrate` fixtures;
    - the supersede edge cases;
    - parts don't inherit;
    - UTC dates.
13. *Agreed 2026-11-02 (§0.6):*
    - no standard format for reads, and a published EBNF grammar instead;
    - reassign and override lift;
    - gates on parts, rolled up as `parts_gates`, with one go naming a parent;
    - `Hide until` on board items;
    - `while TD-m` provenance;
    - the rank-key bound and `respace`.
14. *Agreed 2026-11-02:* the `Hide until` key exception (§6): strip it from `item_key` in v2.3, accepting the residual risk on uninspected boards.
15. *Agreed 2026-11-02:* the writers `ledger.py` and `board.py` live in ledgerboard, file-level and git-free, with the ADR amended (§1.1).
16. *Agreed 2026-11-02:* boards name their people (`People:`), every answer records who gave it, and `Answered by: owner | any` says who may lift (§6.2).

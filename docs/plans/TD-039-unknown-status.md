# TD-039: an archived blocker's unknown Status word keeps the block

**Status:** Designed 2026-11-03 (the designer); it waits on Paul's go. Class: **wide**, because it changes what a vendored format's reader reads: which archived blockers release their dependents (cap 6 rounds, cadence.md §4.8 *Design review rounds*). The rounds ended after round 4 by the stop rule, because its design review raised nothing build-changing. The build-changing findings per round from the design reviews were 1, 2, 2 and 0. The fact-checks raised 1, 0, 0 and 0, and the closing fact-check raised none. **A recurring topic:** the word rule's edges (F7, F15, F23, F24), an empty or punctuation-only Status. Round 3 replaced the rule with a single test, no first run, and round 4 found it closed. The choice of (b) was not challenged in any round. The findings no review has read are round 4's minor fixes, F28–F32, which only the closing fact-check checked. They go into the build's Fix. The review record is `docs/reviews/TD-039.md`.

**Entry:** [TD-039](../ledger/archive/TD-039.md). TD-035's build found it while writing the cross-version fixtures.

## The problem

SPEC *Superseded and dropped* (v2.4) reads an archived blocker's Status by its first word. `Superseded … by` and `Dropped` keep the block or follow a chain. Every other Status "reads as closed and done, which releases the dependents". The target design's §7.4 promises the opposite for text from a newer minor: "a minor reader reading text from a newer minor of its major never reads a block as lifted".

The two meet at a word the reader does not know. Suppose a later minor adds a Status for an entry that is closed but not done, say `Withdrawn 2026-01-05`. A v2.4 reader that meets it, in its own archive or through another repo's resolver, releases the dependent. TD-039's entry shows this on main at 3b232c8: `pickable()`, with a resolver answering `{"state": "archived", "status": "Withdrawn 2026-01-05"}`, lists the blocked entry as pickable.

This has already happened once. `Dropped` is v2.4's own closed-but-not-done word, and v2.3 reads it as done and releases what v2.4 keeps blocked. SPEC's *Versions* has to tell consumers to archive an entry `Dropped` only once every reader runs v2.4. With "any other word is done", every future closed-but-not-done word repeats that hazard, and nothing tells the older reader it is guessing.

## Options weighed

**(a) Keep "any other Status is closed and done", and narrow §7.4's promise to the words a reader knows.** A new closed-but-not-done word then has to be a major change, so that older readers refuse the file. This costs nothing today. But it makes every such word a major, and it leaves the failure silent: a wrongly lifted block shows as a pickable entry that nothing flags, and is noticed only once its work is picked too early.

**(b) A Status word the reader does not know keeps the block, and `check()` flags it (chosen).** The reader's known words are the Status words it already reads, `STATUS_WORDS`, which grows within a major. Any other first word holds the dependent, and the flag says why. A later minor can then add any closed word, done or not, in a minor. An older reader holds the block and says so until it upgrades, so it never lifts one. This keeps §7.4's promise as written, and it fails the way the format already fails on a newer major: it says what it cannot read rather than guessing. The cost is that an archived Status opening with prose ("Steps 1 and 2 shipped") also holds its dependents, where v2.3 released them. That is the same failure safely taken: the reader cannot tell prose from a newer word, and the flag names each such case so that someone decides it.

**(b) is chosen.** A block wrongly kept is visible and flagged, and costs one decision. A block wrongly lifted is silent, and costs work done out of order. A format read by several releases at once should fail the visible way. v2.5's `migrate` then maps every archived Status it can and stops on the rest for a person to decide (target design §2.2), so the prose case is transitional.

## The rules

1. **The known words.** An archived entry's Status is read by `first_word()`. It takes the **first run**, the first stretch of characters up to whitespace, `,` or `;`. It then strips any run of `*`, `_` and backtick from both ends, then any run of `.` and `:` from the end of what is left, and lower-cases the result. So the `.` or `:` goes only when nothing of the first strip follows it: `**Resolved**.` reads `resolved**`, which is unknown. The word is **known** when it is one of `STATUS_WORDS`: `open`, `resolved`, `superseded`, `dropped`, `designed`, `built`, `partly`, `live`, `in`, `done`, `moved` and `obe`. A Status has **no word** only when it has no first run: it is absent, or holds nothing but whitespace, `,` and `;`. Such a Status reads as closed and done, as before, and so does a resolver's `status` of `""`. Every Status with a first run has a word, and that word is known when `first_word()` is in `STATUS_WORDS`. Anything else is unknown and holds, including a first run that strips to nothing (`**`, `.`, `** Xyzzy`). So the test, in both `_archived_status()` and `_chain()`'s cross path, is: no first run reads as closed and done; a known word follows its rule; any other word holds. One test, with no second removal rule. Case does not matter: `DONE` is known and `XYZZY` is not.

   **A deliberate carve-out.** `STATUS_WORDS` is the list of words this release reads, not a list of done words. An archived `Open`, or any retired word (`Designed`, `Built`, `Partly`, `Live`, `In`, `Done`, `Moved`, `OBE`), therefore still reads as closed and done, as in v2.3. Some of them mean done (`Done`, and an archived `Designed` or `Built`). Some do not (`Moved` and `OBE`, which v2.5's `migrate` maps to `Superseded` or `Dropped`, and an archived `Open`, `In`, `Partly` or `Live`, on which `migrate` stops for the person to decide). Either way, v2.5's remodel settles each one (target design §2.1–§2.2). Holding on them would be a second rule, about which known words mean done, and it belongs to the closed Status set that v2.5 defines, not to this fix. `STATUS_WORDS` grows within a major. If a later major drops a retired word from it, that word becomes unknown and holds under rule 2. So `**Live check held …` reads `live` (known), `Resolved.` reads `resolved` (known), and `Steps 1 and 2 shipped` reads `steps` (unknown). Other punctuation stays on the word, so `Resolved)` or `Resolved—` is unknown and holds. That is deliberate: a hand-typed Status that no writer wrote is flagged, and its fix is to write the word.
2. **An unknown word keeps the block.** A dependent `Blocked by` an archived entry whose Status word is unknown stays blocked.
   - Local: `check()` flags it on the dependent as `blocker-unknown-status`. Like `blocker-dropped`, it joins `EDIT_ERRORS`: it is an error on an entry the edit changed, and ℹ on a standing ledger.
   - Through the resolver: an archived answer whose `status` has an unknown word is flagged as `cross-unknown-status`, which is ℹ only, like `cross-dropped`, since this repo cannot rewrite another's archive.
   - The flag's text names the blocker and the word. It reads: `ℹ TD-n: Blocked by <b>, {where}entry archived with a Status word this reader does not know (<Word>) — decide this entry: drop the blocker if its work is done, or block on what replaces it; the block stays`. `{where}` is `""` locally and `another repo's ` through the resolver, as in the dropped flag. `<Word>` is the Status's word as written: `first_word()`'s strips without its lower-casing, so `**Withdrawn**` is `Withdrawn`. When those strips leave nothing, it is the first run itself, so `** Xyzzy` names `**`. One private helper, `_status_word(status) -> str`, gives that form to the local and the cross flag alike. It returns `""` only for a Status with no first run, so the no-first-run test is `_status_word(status) == ""`, shared by `_archived_status()` and the cross path. It is never `first_word(status) == ""`, which would read `**` as wordless. `first_word()` is unchanged for every other caller.
3. **A Superseded chain that ends in an unknown word keeps the block.** It is flagged as `blocker-superseded` or `cross-superseded`, as a chain that ends in `Dropped` is, with the reason `ends in an entry whose Status word this reader does not know`.
4. **Unchanged:**
   - A resolver that gives no `status` reads every archived entry as closed and done, as before. That is the host's choice of resolver, not text from a newer minor.
   - A `status` that is not a string is unreadable, and is held as `unresolved` (`_chain()`, today).
   - Every known word reads as it does today: `superseded` and `dropped` by their rules, and the rest as closed and done.
   - `archive_plan()`'s refusals are unchanged, apart from one addition: a successor whose chain ends in an unknown word is refused, as one that ends in `Dropped` is (*Archiving rewires*: "is open or Resolved").

## Where it changes in the module

- **`_archived_status()`** keeps a third word, `unknown-status`, for an entry whose Status word is outside `STATUS_WORDS`. It also carries a new key, `status_word`, on every entry, which is `_status_word()` of the Status, for the flag. `archive_plan()`'s synthetic entry for the entry being archived carries it too, as `""`. Today it folds every word but `superseded` and `dropped` into `resolved`. The word is `unknown-status`, never `unknown`, because `_chain()`'s `unknown` already means *no such entry*.
- **`_chain()`** returns the state `unknown-status` for such an end, local or through the resolver. Its local path already returns the stored word. The build makes its cross path compare the resolver's `status` against `STATUS_WORDS` the same way. Today the cross path returns `resolved` for any word but `dropped` and `superseded`. `_chain()` returns a third value, the end's word as written (`""` for any other end). `_ended()` and `archive_plan()` therefore read the word without resolving the blocker again, and every existing caller of `_chain()` is updated to match.
- **`_ended()`** holds and flags a single-step `unknown-status` (rule 2), and adds the chain reason to its `why` map (rule 3).
- **`EDIT_ERRORS`** gains `blocker-unknown-status`.
- **`STATUS_WORDS`** is unchanged, but it gains a comment saying that a word added to it is a word `pickable()` reads, as closed and done unless it joins Superseded's or Dropped's rules. A unit test pins that coupling: every word in `STATUS_WORDS` but `superseded` and `dropped` releases a dependent, and a word outside it holds one. So a word added for the Log alone cannot silently become a done word. The comment names both of the list's roles, the Log's head words and the blocker reader's known words, so that whoever adds a word decides both.
- **Comments and docstrings.** The `Resolve` comment above `Resolve = Callable` (its "Superseded, Dropped, else closed and done", wrapped across two lines) and the docstrings of `_archived_status()`, `_chain()` (its states, and its third value), `_ended()` and `archive_plan()` say the new rule.
- **`archive_plan()`** refuses a successor whose end is `unknown-status` (rule 4).

Nothing reads git, the network or a file. The resolver stays what the caller passes in.

## The `SPEC.md` text

**1. *Superseded and dropped*, the opening paragraph, from "`pickable()` and `check()` read" to "there is no separate word.", becomes:**

> **Superseded and dropped** (v2.4). `pickable()` and `check()` read an archived blocker's Status by its first word. That is its first run up to whitespace, `,` or `;`, less any run of `*`, `_` and backtick at either end and then any run of `.` and `:` at its end, compared without case. A Status with no first run (absent, or only whitespace, `,` and `;`) reads as one with no Status. A first run that strips to nothing is a word this reader does not know. Known here means a first word in the reader's Status words, a looser test than the head *The Log* lifts notes from, so a bold-led `**Live check held**` is a known word here though *The Log* leaves it alone. `Superseded … by <id>` and `Dropped` apply the rules below, and so does a word this reader does not know. Every other Status reads as closed and done, which releases the dependents, as before. That covers the reader's other Status words, dated or not: `Resolved`, and on an archived entry also `Open` and *Retired words*' list (`Designed`, `Built`, `Partly`, `Live`, `In`, `Done`, `Moved`, `OBE`), which v2.5's `migrate` maps or stops on. It also covers a Status with no word. A duplicate is `Superseded D by` the original; there is no separate word.

**2. *Superseded and dropped*, a new bullet after "**A blocker that was dropped**":**

> - **A blocker whose Status word this reader does not know** keeps the block. Its first word is not one of the Status words this release reads: `Open`, `Resolved`, `Superseded`, `Dropped`, and the retired `Designed`, `Built`, `Partly`, `Live`, `In`, `Done`, `Moved` and `OBE`. It may be a later minor's word for an entry that is closed but not done, so the reader never reads it as lifted. An archived Status that opens with prose ("Steps 1 and 2 shipped") reads the same way. `check()` flags it (`blocker-unknown-status`, likewise; `cross-unknown-status`, ℹ, through the resolver), naming the word, and someone decides the dependent. A Superseded chain that ends in such an entry keeps the block too (`blocker-superseded`), and `archive_plan()` refuses it as a successor.

**3. *Superseded and dropped*, the "**Another repo's blocker**" bullet:** after `(`cross-superseded`,` it adds `` `cross-dropped`, `cross-unknown-status`): `` in place of `` `cross-dropped`): ``. Nothing else in the bullet changes.

**4. *Superseded and dropped*, the superseded bullet:** its "while the chain ends in Dropped, in no entry, in a loop, or in a `Superseded` with no successor" becomes "while the chain ends in Dropped, in no entry, in a loop, in a `Superseded` with no successor, or in a Status word this reader does not know".

**5. *Archiving rewires*:** its "names no entry, cannot be resolved, ends in Dropped, loops" becomes "names no entry, cannot be resolved, ends in Dropped or in a Status word this reader does not know, loops".

**6. *Versions*, v2.4's sentence beginning "v2.4 also reads an archived blocker's Status":** it now opens as follows, through `` `cross-dropped` ``:

> v2.4 also reads an archived blocker's Status (*Superseded and dropped*): a blocker archived `Superseded` releases its dependents only when its chain ends in a Resolved entry, and one archived `Dropped` or with a Status word v2.4 does not know keeps them blocked, where v2.3 released every one; `check()` gains `blocker-superseded`, `blocker-dropped`, `blocker-unknown-status`, `cross-superseded`, `cross-dropped` and `cross-unknown-status`

The rest of the sentence stays as written, from `, and a resolver's answer may carry` onwards. Then one sentence is added after the paragraph's "only once every reader of its ledger runs v2.4.":

> A later minor may add a Status word, done or not, and v2.4 holds the dependents of an entry archived with it until it is read by a release that knows the word. A consumer writes such a word only once every reader of its ledger runs v2.4 or later, since v2.3 releases on any word. An archived Status that opens with prose holds its dependents under v2.4 where v2.3 released them, and `check()` names each. On an entry an edit changes, `blocker-unknown-status` is an error.

## The target design

These lines are amended in place, each with a dated pointer to this plan:
- **§7.4 *Cross-version*.** The first sentence becomes: a v2.4 reader resolves an `other#TD-n` whose archived Status is a word it does not know (a later minor's, such as `Withdrawn D`), keeps the block, and flags it (`cross-unknown-status`). The promise sentence is scoped to what the reader cannot read: "a minor reader never reads a block as lifted on a Status word it does not know, nor a closed entry as open". The two releases that remain are stated beside it. A known word on the wrong side of the archive (`Open`, `Moved`, `OBE` …) releases until v2.5's remodel, and so does a resolver that gives no `status`, by the host's choice.
- **§5's "Under v2.4" bullet (line 1103):** its "every other archived Status (`Resolved`, `Done`, `Built`, `Designed`, undated or not) reads as closed and done" becomes "every other archived Status that is a known word (`Resolved`, `Done`, `Built`, `Designed`, undated or not), or none, reads as closed and done, and a word v2.4 does not know keeps the block (TD-039)".
- **§0.4's row 9:** its "an older reader reads a newer closed Status as closed" becomes "an older reader holds the block on a newer Status word and flags it".

The review-history row at line 180 stays as it is, since it records what was decided then. Line 190's check, that every unmigrated archived Status in both consumers read as closed under the v2.4 rule, is about the old rule. Under this one, each consumer's v2.4 vendor PR lists its open entries that are newly held, from `check()`'s flags. That is the vendor PR's data, not this design's. It names the merge-gate side too: an edit to such an entry fails until its blocker is decided.

## The fixture cases

`fixtures/ledger/unknownstatus.md`, with `unknownstatus.archive.md` and `unknownstatus.resolve.json`, is new, and `unknownstatus.json` is generated. It is a new case, so it does not touch TD-035's `crossversion` files. TD-035's own text still quotes §7.4's old example (`Dropped D` "reads it as closed"). That entry is its holder's to reword once this lands, and the designer tells its holder. Its open entries are:

| entry | Blocked by | the blocker | reads |
|---|---|---|---|
| TD-501 | TD-511 | archived `Xyzzy 2026-01-05` | blocked; `blocker-unknown-status`, naming `Xyzzy` |
| TD-502 | TD-512 | archived `Steps 1 and 2 shipped` | blocked; `blocker-unknown-status`, naming `Steps` |
| TD-503 | TD-513 | archived `DONE` | pickable (a retired, known word, in any case) |
| TD-504 | TD-514 | archived with no Status | pickable |
| TD-505 | TD-515 | archived `**Live check held on the mirror**` | pickable (`live`, known) |
| TD-506 | TD-516 | archived `Superseded 2026-01-05 by TD-517`, with TD-517 archived `Xyzzy 2026-01-06` | blocked; `blocker-superseded`, ending in an unknown word |
| TD-507 | acme/tools#TD-41 | resolver: archived, `status` `Xyzzy 2026-01-05` | blocked; `cross-unknown-status` (the entry's reproduction, with the fixture's word) |
| TD-508 | acme/tools#TD-42 | resolver: archived, no `status` | pickable (as before) |
| TD-509 | TD-519 | archived `Resolved) see the thread` | blocked; `blocker-unknown-status`, naming `Resolved)` |
| TD-510 | TD-520 | archived `**Resolved**.` | blocked; `blocker-unknown-status`, naming `Resolved**` |
| TD-521 | TD-522 | archived `**` | blocked; `blocker-unknown-status`, naming `**` (a first run that strips to nothing) |
| TD-530 | TD-531 | archived `, ;` | pickable (no first run) |
| TD-523 | TD-524 | archived `Open` | pickable (the carve-out) |
| TD-525 | TD-526 | archived `Superseded 2026-01-05 by acme/tools#TD-43`; resolver: archived, `status` `Xyzzy 2026-01-06` | blocked; `blocker-superseded`, ending in an unknown word across repos |
| TD-527 | acme/tools#TD-44 | resolver: archived, `status` `""` | pickable (no word) |
| TD-528 | TD-529 | archived `** Xyzzy` | blocked; `blocker-unknown-status`, naming `**` |

The fixtures' unknown word is `Xyzzy`, which no release will adopt, so the case still reads as written after `STATUS_WORDS` grows. The `<Word>` it names in TD-509 and TD-510 is `first_word()`'s strips without the lower-casing.

The generated JSON pins both levels, as every ledger fixture does: `check` on the standing ledger gives ℹ throughout, and `check_since_empty`, where every entry is new, gives `blocker-unknown-status` as an error and `cross-unknown-status` as ℹ. The `archive_plan` group reads only the shared `ledger_edit/plan/` pair. So `plan/archive.md` gains TD-425, archived `Xyzzy 2026-01-06`, which no existing case names, so their outputs are unchanged. `ledger_edit/cases.json`'s top-level `archive_plan` list gains `superseded_unknown_status`: archive TD-403, which nothing waits on, superseded by TD-425. The refusal is checked beside the Dropped one, after it and before the `unknown`/`unresolved` branch. This case is refused, with `the successor's chain (TD-425) ends in an entry archived with a Status word this reader does not know (Xyzzy) — a successor is open or Resolved`, after the Dropped refusal's form. A successor in another repo goes through the same `_chain()` branch, and no `archive_plan` case pins it. The runner's resolver there is a `(state, why)` pair that carries no `status`, and TD-525 pins that branch through `check()`. `fixtures/run.py`'s docstring gains the `ledger/unknownstatus.md` line (v2.4), and its `plan/` line names the unknown-status refusal.

## The build

One build, `**Part of:** TD-039`. It brings everything above in one PR with its `SPEC.md` text, code and fixtures (AGENTS.md).

**Done when:** an archived blocker with an unknown Status word keeps its dependent blocked and is flagged, locally and through the resolver, as *The rules* say. The six `SPEC.md` passages above land with the code, and the target design's three lines are amended. `unknownstatus` and the `archive_plan` refusal pass (`python3 fixtures/run.py`), and so does the suite.

**Which release: v2.4.** v2.4 is not yet tagged (TD-036, blocked by TD-035 and TD-037). Shipping v2.4 with "any other word is done" and turning it in v2.5 would release blocks under one minor and hold them under the next. Each consumer would also see that change twice. So TD-036's `**Blocked by:**` gains the build when it is filed. TD-035's cross-version fixture for this half of §7.4 is this build's `unknownstatus`, so TD-035 does not wait on it.

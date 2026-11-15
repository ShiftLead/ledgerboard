# Lessons from the v3.0 migration

Written 2026-11-15, to prepare for the next format migration. It covers how ledgerboard moved the ledger and
board formats that agent-cadence and ShiftLead use from v2.4 to v3.0 (each board item its own file, the old
ledger forms retired), between 2026-11-04 and 2026-11-15.

The format change itself was clean: no repo lost data. Nearly every problem was in the cutover. Some steps were
planned but never filed. Old data could not be converted once the old tools were gone. Live code lagged behind
what had merged.

## Timeline

| Date | What happened |
| --- | --- |
| 2026-11-04 | v2.4 (gates, Log, lifts, the gate sweep, the ledger writer); agent-cadence took it first, ShiftLead within a week |
| 2026-11-05 to 11-06 | v2.5 and v2.6; both consumers the same day |
| 2026-11-11 to 11-12 | v2.7; agent-cadence the same night (`ledger.py migrate` added, 77 entries migrated), ShiftLead the next day |
| 2026-11-12 | Paul's Go on the v3.0 designs; the board design (TD-070) had run nine review rounds and was split into three parts |
| 2026-11-13 | v2.8, the last v2 release, carrying the migrate rules every ledger had to pass before v3.0; agent-cadence the same day, ShiftLead on 11-14 |
| 2026-11-13 to 11-14 | The five v3.0 builds, then the ledger removals |
| 2026-11-14 | v3.0 tagged; Paul chose a one-day rollout. agent-cadence took it and split its board in one PR (TD-263, about 1h45m) |
| 2026-11-15 | ShiftLead took it and split its board (TD-1881, #3968), inside its window, after a one-time archive cleanup (#3989) |
| 2026-11-15 | v3.2 released, carrying the changes planned as v3.1 and v3.2. ledgerboard's own board was found still on v2 (TD-120, open) |

## What went well

- **Small releases before the big one.** v2.4 to v2.8 each shipped a piece, and each consumer took it within about
  a day. By v3.0 every ledger was already on the last v2 forms.
- **A clean bill before the switch.** Each consumer ran v2.8's `migrate --plan` and showed no changes and no stops
  before taking v3.0, as a step of its own.
- **Before-and-after reader runs.** Each consumer ran its readers (the gate sweep's dry-run plan, the board report)
  before and after its split. The output matched in both.
- **A search for every removed name,** each hit judged. It caught agent-cadence code the plan had missed.
- **Splitting a stuck design.** TD-070 ran nine rounds without settling; split into three scoped parts, each
  reached Go inside its round limit.
- **Independent review caught real defects every time.** Two holes in agent-cadence's merge check (TD-263). A
  BLOCK on ShiftLead's switch, for a false refusal and an undocumented v2 refusal. A wrong duplicate kept in the
  archive cleanup.
- **Filing each sync entry ahead of time,** written in the shape of the previous one.
- **"Fix it upstream and re-pin; don't work around it here"** as the techlead's rule for a consumer's blocker.
- **Holds that release themselves,** keyed to a tag or a file's contents, with a live check after the update went live.

## What went wrong

| Problem | What it cost | Cause | Fix |
| --- | --- | --- | --- |
| ledgerboard never moved its own board | Paul's presses on its items failed with a silent 400 and the items came back; each answer was relayed by hand | The plan's last step (pin bump plus own split in one PR) was written in the plan but never filed as an entry | TD-120, filed after the fact; the pin bump is Paul's, so a session he starts does it |
| ShiftLead's old archive could not be converted | About 15 hours on TD-1881: five session restarts at the context bound, one PR closed unmerged, a new merge-check rule upstream, a wait on Paul's merge | 71 closed items had no closing date and 3 ids were duplicated. v3.0 had retired the tools that could fix them, and the merge check refused a hand edit | agent-cadence TD-277 (#229) allowed one mechanical cleanup, dated from git history or the line's own words, with inexact duplicates flagged |
| Taking v3.0 alone broke 249 ShiftLead tests | The vendor and the split had to land in one PR, and a pin-only PR was closed unmerged | v3.0's writers refuse a v2 board, so the pin, the copy and the split cannot land apart | One PR for all three, as the plan's revised order says |
| Each v2 vendor broke a consumer's tests or docs | One extra round per release, typically: 8 suites with old-form fixtures (v2.7), a crash and a newly allowed note (v2.8), a stale design section (v2.4) | Consumers' fixtures and docs restate the format | Fixed in each vendor PR; worth a pattern search before the vendor |
| Live code lagged behind a merge | ShiftLead's gate sweep, still on pre-switch code, filed 11 of ShiftLead's own questions onto ledgerboard's board (#355) | Merging the switch and putting it live are separate steps, and the sweep ran in between | Closed with the board writer (#360) once the home was live on the new code |
| ledgerboard's board listed no people | A second TD-115 question offering Go or Not yet, where a Go would have skipped a review round | A board with no people line covers nothing, so its own items were invisible to the sweep | TD-116 added `People: paul` |
| The sweep always offers Go or Not yet | Questions asking something else came back with the wrong answers | The sweep cannot read an entry's own answers | TD-119, in design |
| A hold tied to a design PR fired after the first round | agent-cadence's TD-262 was released while the Lift the hold design was still changing | Design rounds go on after the first design PR merges | Re-pointed at ledgerboard's TD-115 |
| A planned version number was skipped | v3.1 was never tagged; entries waited on a tag that would never exist | Two release-numbered builds merged before a tag was cut | Released as v3.2; the waits re-pointed (#358) |
| A release wasn't tagged when a consumer needed it | agent-cadence TD-221 waited on a v2.6 tag | The build was on ledgerboard's main, untagged | A hold on the tag |
| A rebase during review | One extra ask (v2.7 in ShiftLead) | The new head had no precheck status | Precheck the new head before asking again |
| Paul's Hold note was cut at 297 characters | The designer guessed the rest | A silent length cap | Sent to ShiftLead to keep notes whole or refuse visibly |

## Lessons about how the work was run

**Design reviews**

- Watch the trend, not just the count. Findings that shrink (10, 8, 5, 4, 1, 0) mean one round from done. Findings
  that rise again mean the scope is too big: TD-070, and later ShiftLead's TD-1832 and TD-1845, settled only once
  made smaller.
- Another round is cheap; a wrong build is not (Paul, 2026-11-05). Recommend one more round while any fix that
  changes the build is unread by a review, and Go when only minor fixes are unread.
- Two designs that touch the same rules churn each other. Give one of them every rule in the overlap.
- Design the cutover, not just the format. The release order was redesigned in round 4, after reviews showed an
  old reader sees a split board as empty; that finding had come back in five rounds.

**Holds and releases**

- Tie a hold to what ships (a tag, a build merged, a file's contents), never to a design PR merging.
- Tag as soon as a release-numbered build merges, or number the release when it is cut.

**The person's board**

- A refused press must say why on the card; a silent 400 looks like a lost click.
- Mis-presses happened three times. An answer that lifts a hold needs an undo or a confirm.
- Items were missing from the board several times (Paul had to ask for four). Every entry that waits on a
  person needs its board item when it is filed. agent-cadence's TD-264 and ledgerboard's `decision-missing`
  (v3.2) now check this.
- Text for the person is plain and says who acts (Paul, 2026-11-14); v3.2 carries a shared check for it.

**Sessions**

- A long cutover crosses context bounds. ShiftLead's switch ran across five session restarts; a half-done
  branch with a written plan (what is left, what to check) let each restart pick it up.
- Usage limits killed sessions mid-work (2026-11-11). A wind-down finishes whole entries, so a restart can
  wait an hour or more.

## Checklist for the next format migration

Before the release:

- [ ] File one ledger entry for every step of the rollout, the format repo's own included, each with its owner
      and what it waits on. A step only Paul may do (a pin bump) is owned by Paul from the start.
- [ ] Run the new converter, dry, on every repo's real board and ledger, the format repo's own included, and fix
      what it refuses while the old tools still exist.
- [ ] Check each board lists its people and reads clean under the new reader.
- [ ] Search every consumer for each removed name, fixtures and docs included, and judge each hit.
- [ ] Tie every waiting hold to the release tag or the shipped build.
- [ ] Paul picks the rollout window and the order: the format repo, agent-cadence, ShiftLead, then the format
      repo's own board.

During the cutover:

- [ ] Before each consumer's switch merges, pause the gate sweep, or confirm the home is live on the new code.
- [ ] Land each consumer's pin, vendored copy and split in one PR.
- [ ] Run each consumer's readers before and after its switch, and record that they match.
- [ ] Tag each release as soon as its build merges.
- [ ] Press one answer on each repo's board after its switch and check it lands.

After:

- [ ] Close any duplicates the old code filed, with the board writer.
- [ ] Confirm every entry in the plan is archived, then add what was learned here.

## Open follow-ups (2026-11-15)

| Follow-up | Where | Who acts |
| --- | --- | --- |
| Move ledgerboard's own board to v3 and bump its pin, in one PR | ledgerboard TD-120 | Paul, or a session he starts; Paul merges |
| Take v3.2 (the no-hold flag and the plain-text check) | agent-cadence, then ShiftLead | Each repo's techlead files its vendor entry |
| The sweep offers an entry's own answers | ledgerboard TD-119 | In review; Paul decides |
| The merge rule for Lift the hold changes | ledgerboard TD-115 | In review; no Go before ShiftLead's TD-1829 |
| Keep a person's note whole, or refuse it visibly | ShiftLead | ShiftLead's techlead |
| A refused press says why on its card | ShiftLead | Not yet filed |
| A regular review of session transcripts for gaps like these | All three repos | Paul's idea (2026-11-06), to propose now |

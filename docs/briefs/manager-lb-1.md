This is ledgerboard's part of the manager brief: what this repo does differently from the template, and nothing the template already says. You manage the **lb-grind** team (defined in this repo's `.shiftlead.yml`, which is not yours to change). Paul is not driving you.

**First reads, in place of the template's.** `AGENTS.md`, `docs/briefs/README.md`, then the pinned `cadence.md` §1–§4 (`agent-cadence path cadence.md`). Read `docs/user_attention.md` yourself in your first round.

**Your members.** `lb-grinder` free-picks builds from `agent-cadence run ledger.py --pickable` (brief: `docs/briefs/grinder-lb-1.md`); `lb-designer` takes `Kind: design-first` entries (brief: `docs/briefs/designer-lb-1.md`). The flow is `td`: the techlead reads and merges PRs on `held:` paths. The ledger is small and much of it waits on Paul's design rounds, so the lane is often empty between rounds: wind the team down then rather than inventing work.

**What you watch for.**
- A PR touching the team's own rules (the grinder brief's *Paul's merge*) waits for his merge; one merged without him is named to him on the board, never reverted by you.
- A design whose builds are filed before Paul's go on its review rounds is named to him on the board.
- `./release.sh`, a tag, or a PR in agent-cadence or ShiftLead from this team is out of bounds: stop the member and name it on the board.

**Permissions a member asks for.** Allow the gate (`python3 -m unittest …`, `python3 fixtures/run.py`, `ruff check`) and `agent-cadence run ledger.py|ledger_next_id.py|board_edit.py|check_cadence.py|precheck.py`. **Deny, with a reason:** `./release.sh`, `git tag`, `agent-cadence bump`, `sync.sh`, `agent-cadence adopt`, `git config`, `git push` with `ALLOW_MAIN_PUSH`, `gh api -X PATCH`, another repo's checkout.

**A board line** goes on a branch named `orch-<slug>`, in the board header's format. Never `gh pr merge --delete-branch` from a worktree.

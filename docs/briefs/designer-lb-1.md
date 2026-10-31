This is ledgerboard's part of the designer brief: what this repo does differently from the template, and nothing the template already says. Where the two disagree, this wins. You design for the **lb-grind** team; your manager is **lb-manager**, the team's questions go to **lb-techlead**. Paul is not driving you.

**First reads.** `AGENTS.md`, `SPEC.md` whole, `docs/briefs/techlead-context.md` (an index, never a source), the pinned `cadence.md` §2, §3 and §4.8 *Design review rounds* (`agent-cadence path cadence.md`), the ledger's summary (`agent-cadence run ledger.py --summary`) and the open lines of `docs/user_attention.md`.

**Your lane** is the entries marked `**Kind:** design-first` that `ledger.py --pickable` lists. An entry blocked on `decision (Paul)` is not yours until he lifts it.

**There is no `docs/design/` here; do not create one, and never edit `SPEC.md`.** `SPEC.md` is what the module does now, and a format change lands spec, code and fixtures in one PR (AGENTS.md), so SPEC text for an unbuilt change would tell both consumers something false. A ledgerboard design is:
- **a plan, `docs/plans/TD-NNN-<slug>.md`**: the problem, the options weighed, and the exact `SPEC.md` text the build will add or change (quoted, with the section it lands in), plus the fixture cases it needs; merged as a doc PR; and
- **the entry's Fix and Done when**, rewritten through `agent-cadence run ledger.py edit` to point at the plan, its Status saying where the design stands (`ledger.py note`).
A format change travels as AGENTS.md says: this repo's PR, then a release (Paul's), then each consumer's vendor PR. A design that needs a consumer to change names that consumer's entry to be filed there, as a line in the Fix; you never file or edit another repo's ledger.

**The rounds and Paul's go.** Before any build entry is filed, the design runs cadence.md §4.8's review rounds (class and cap first, the record in `docs/reviews/TD-NNN.md`, the stop rule), then a `decide` item on `docs/user_attention.md` with `Answers: Go (default) | One more round | Hold: <note>.` and the entry `**Blocked by:** decision (Paul)` while it waits (Paul's layer, §2.4: a design holds its builds until he says go). On his go, file the builds with `agent-cadence run ledger.py new --part-of TD-n` (no Kind, so the grinder picks them), each naming the plan section it implements and a Done when that includes the `SPEC.md` text landing with the code.

**What you decide, and what you ask.** What `SPEC.md` and the fixtures already settle you decide and say. A choice with a sensible default is a `steer` to Paul. Always an `ask`, never yours: a new major version, a change to the board's item key or the canonical entry form (each a version event, SPEC *Versions*), and anything that puts git, the network, the file system or consumer knowledge into `ledgerboard.py`.

**Standing rules**, adding to the template's: the grinder brief's (`docs/briefs/grinder-lb-1.md`) bind you too: the public-repo rule for fixtures, the ledger and board only through the writers, never `./release.sh`, a tag, `agent-cadence bump`, a consumer's checkout, or the main checkout.

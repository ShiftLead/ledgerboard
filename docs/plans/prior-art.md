# Prior art for the target design (2026-11-01)

Five Sonnet researchers covered five areas:

1. git-native trackers
2. agent work coordination
3. wait/event/approval gates
4. record lifecycles
5. format governance and attention queues

This file holds what they found, sorted against `target-design.md` draft 6. **Adopted 2026-11-01:** all of §B, with UTC for item 8 (now draft 7, §0.4).

**How far to trust it.** The researchers marked each claim as either verified (read on a primary page) or inferred. I re-checked the one claim I would build on: Beads' gate types and `bd gate check` (https://beads.gascity.com/workflows/gates). That claim holds. The agent's further claim that Beads *escalates a gh:pr gate whose PR closed unmerged* is **not** on that page, so I do not rely on it.

## A. What the precedents confirm (no change)

| Design choice | Precedent | Source |
|---|---|---|
| Readiness derived from text only; no `events=` input | Beads first kept readiness in a database flag and a daemon, then removed the daemon. Kubernetes derives `Ready` from recorded conditions. | beads.gascity.com/architecture.md; kubernetes.io pod-lifecycle |
| An event is lifted by a PR that writes it into the text | Flux image automation commits an observed fact into git, optionally on a branch for PR review. Its own stated caveat is unreviewed writes, and our PR step answers that caveat. | fluxcd.io/flux/guides/image-update |
| Typed, closed check types; no scripts | Mergify conditions are typed attributes with a closed set of operators. Beads' gate types are a closed set (`human`, `timer`, `gh:run`, `gh:pr`, `bead`). | docs.mergify.com/conditions; beads gates |
| Human gates and machine gates are lifted differently | Beads: `human` gates close only by `bd gate resolve`; the rest close by a scheduled `bd gate check`. This is our `decision` vs `event` split. | beads gates |
| Markdown in git, one file per entry, a pure parser | Beads rewrote its storage twice (JSONL, then SQLite, then Dolt); binary state cannot be reviewed in a PR. git-bug blobs cannot be read by people. | github.com/steveyegge/beads; git-bug data model |
| A closed Status set of outcome words; stages are not statuses | PEP, KEP and Go proposals all distinguish replaced from declined. KEP keeps `stage` (alpha/beta/GA) separate from `status`. | peps.python.org/pep-0001; KEP-0000 |
| `Kind` option (i): a consumer field | In PEP `Type`, each value changes rules, so a typed field earns its place when its values carry rules. KEP `stage` has no lifecycle rules. Beads and Fossil push integration data into an extension bucket rather than adding first-class fields. | PEP 1; KEP-0000; beads; fossil tickets |
| A version line is a promise about readers; old forms become errors, never reinterpretations | TOML versions the spec, not the file. YAML 1.1→1.2 changed the meaning of the same bytes (`yes`, `010`) and split the ecosystem for years. | toml CHANGELOG; yaml.org 1.2.2 changes |
| An in-file Log with fixed-shape lines | None of the surveyed tools has one; Beads has no per-entry history. Free-prose in-file history rots. KEP's "files stand on their own" is the argument for having a Log. | KEP-0000; keepachangelog |
| A gate sweep for stuck gates | None of Beads, Backlog.md, Taskwarrior or Org flags a blocked item that is rotting. | researcher 1 (inferred from what those tools' docs leave out) |
| Typed event checks with a deterministic way out | Org, Taskwarrior and Beads have no equivalent; Beads' gh gates come closest. This is the design's most distinctive idea. | researchers 1 and 3 |

## B. Gaps they expose: proposed additions

Each item names where it would land. My recommendation follows the arrow.

1. **Writers preserve what they cannot parse** (protobuf keeps unknown fields on a round trip; Avro drops them).
   - Problem: the design does not say what `edit`, `fmt` and `migrate` do with an unknown header field, gate or Log prefix.
   - → Add to §1 principle 7: *every writer keeps text it cannot parse, in place and byte for byte*.
   - Fixtures: an unknown field, an unknown gate, an unknown Log prefix.
2. **Retired words are reserved forever** (protobuf `reserved`).
   - → `check()` names `Waits`, `Taken by`, `hold` and `decision — text` as *retired*, not as unknown, and the spec forbids reusing them with a new meaning.
   - The adr-tools "Superceded" misspelling is the reminder that a label, once written, is permanent.
   - Lands in §2 and §3.
3. **A check has three results, not two: passed, not yet, impossible** (plus *error*, which is never *not yet*).
   - Examples of impossible: a `pr-merged` PR closed unmerged, or a deleted ref.
   - → An impossible event goes to the board at once (Keep / Drop / Rewrite) rather than waiting 30 days. A check that errors or times out is reported as an error, never read as false.
   - Lands in §4.
4. **The lift line has a fixed shape and can be checked again** (GitHub approvals keep only an optional comment).
   - → `gate lifted: event (name) — by <who>; <check-type> passed; <sha|ref|PR#>`, plus `gate lifted: decision (person) — by <person>; <answer>`.
   - A reviewer can re-run the check from the logged evidence.
   - Lands in §2.2 and §4.
5. **Who may write a lifting answer** (GitHub's optional "prevent self-review" is a known hole).
   - → State that only the named person's answer lifts a `decision (person)`. The format records it with `by`. Proving identity is the consumer's job (git author or session).
   - Lands in §3 and §6.
6. **Check arguments are confined** (inferred: a text file that steers a host's credentials).
   - → `check()` refuses a `path` that is absolute or contains `..`. Text is a literal match, never a regex.
   - Host rule: `repo` must be on the roster, and checks run with read-only tokens.
   - Lands in §4.
7. **Lifting is idempotent** (inferred).
   - → A host's lift PR is a no-op if the gate is already gone, and its branch is keyed `TD-n/event-name`, so two machines cannot double-lift.
   - Consumer rule, stated in §4.
8. **`until` and the date.**
   - Problem: "the caller's local date" lets two machines in different zones disagree for part of a day, which strains principle 2.
   - → Either UTC, or state the disagreement as accepted. **Your call.** I lean UTC, for principle 2.
   - Lands in §3.
9. **Gate age comes from the text.**
   - The sweep's 30 days can be counted from the Log's `gate added:` date, so staleness needs no stored state.
   - Option: an `event (name) by DATE` deadline (Airflow `timeout`, Step Functions `HeartbeatSeconds`; both warn that waits without a limit get stuck).
   - → Use Log-derived age now. Add the deadline syntax only if a fixed 30 days proves wrong.
   - Lands in §3.2.
10. **Cross-version window** (Rust editions require editions to interoperate).
    - → Add a fixture: a v2.3 reader resolving `other#TD-n` whose archived Status is a v2.5 word (`Dropped`) reads it as closed.
    - Lands in §7.
11. **`migrate` is idempotent and stops on any unmapped word** (`cargo fix` admits corner cases).
    - → Fixtures: migrate twice gives no diff; an unmapped word is refused.
    - Lands in §7.
12. **Duplicates and supersede chains** (Bugzilla DUPLICATE and MOVED; no precedent rewires dependents, so the edge cases are ours to define).
    - → A duplicate is `Superseded D by` the original.
    - §5 states what happens with:
      - a chain (A→B, then B→C: A's dependents move to C);
      - a dependent that already names the successor (dedupe);
      - a cycle (refuse).
      - The successor must exist and not be Dropped.
13. **Dropped reasons** (Go's "Declined as Duplicate/Infeasible/Obsolete/Retracted").
    - Option: a closed reason word in the `archived: dropped — <reason>; <why>` line.
    - → Lean no for now. Duplicate already goes to Superseded, and a free why is enough until someone needs to filter on the reason.
14. **`Part of` and gates** (Org's blocking did not propagate to children, and users were surprised).
    - → State whether a part inherits its parent's gates. I lean *no*, stated explicitly.
    - Lands in §3.

## C. Considered and not proposed

- **A claim or lease field in text** (Beads `--claim`). Claiming belongs to the orchestrator, and a lease written to text would churn PRs. `Id take` solves id collisions, which is a different problem.
- **A decision that defaults after N days** (Airflow `soft_fail`). It contradicts the reason a `decision (person)` gate exists.
- **Hash ids** (Beads). Beads' own docs contradict each other on length and determinism, and they bring prefix hazards. `Id take` plus sequential numbers stays readable.
- **Snooze or caps on the board** (Linear, GitHub expiry). `until` and "Keep waiting" already cover this. Silent expiry would lose a decision.

## D. Ideas to consider later (innovation)

- `check --as <next minor>`: a dry run of the next release's rules, the format's equivalent of `cargo fix --edition`. It belongs in each vendor PR.
- `pickable()` returns *why* an entry is blocked as well as the verdict (Beads `bd blocked`). It feeds the sweep and the board.
- A board item closes itself when its gate's lift merges. None of GitHub, Linear or PagerDuty documents this. Our lift is a text change, so it can be deterministic.
- A vendored copy carries a header with its release and hash (SQLite amalgamation). "Never edit a consumer's copy" then becomes a mechanical check, if agent-cadence's sync does not already do this.

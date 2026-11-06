---
name: periodic-session-review-after-migration
description: "Paul wants to consider a regular transcript review for orchestration gaps once the ledgerboard migration (through ShiftLead's v2.6 vendor, TD-1378) is done"
metadata:
  node_type: memory
  type: project
  originSessionId: ca9ba866-d7f9-4da4-b11b-9d425b13cf6f
  modified: 2026-11-06T23:10:14.803Z
---

On 2026-11-06 a Sonnet agent mined a long orchestrating session's transcript for every incident where the cadence or ShiftLead machinery stalled, misrouted or needed a person. That turned up 28 incidents in 9 themes. Two lessons were new and got filed: an automatic final review of unread build-changing fixes before an end-of-rounds item reaches the person (agent-cadence, m-81d9aae8df36), and a home-side check for stuck work (ShiftLead, m-247dff0b7a94). The review-of-display-state rule went with the second.

Paul's idea: once the full ledgerboard migration is done, make this kind of review a regular routine. He expects noise from things already fixed, especially early on, and thinks the occasional find is worth it.

**Why:** the review surfaced cross-cutting gaps that per-incident filings had missed. The single filings each fixed one symptom.

**How to apply:** after ShiftLead vendors ledgerboard v2.6 (TD-1378) and the migration is declared done, raise this with Paul as a proposal. Suggest a cadence (e.g. weekly), a scope (transcripts of orchestrating sessions plus seats' round logs), and a dedupe step against the ledgers' archived entries to cut the "already fixed" noise. Related: [[another-design-round-is-cheap]].

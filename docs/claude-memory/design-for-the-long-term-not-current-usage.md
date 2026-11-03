---
name: design-for-the-long-term-not-current-usage
description: "Ledgerboard format decisions follow the long-term best design, never a consumer's current usage or a migration shortcut"
metadata:
  node_type: memory
  type: feedback
  originSessionId: ca9ba866-d7f9-4da4-b11b-9d425b13cf6f
  modified: 2026-11-01T04:29:19.524Z
---

Make every ledgerboard format decision on the long-term best design. Never shape it around how a consumer (ShiftLead, agent-cadence) happens to use a field today, and never take a shortcut to ease a migration. Consumer habits and migration cost belong in the migration plan and the consumer's own entries. They do not belong in the format.

**Why:** Paul, 2026-10-31, during the target-design rounds (TD-010): "This repo (ledgerboard) is a major foundational piece of what we are doing with shiftlead, so we want to make sure we make it right."

**How to apply:** When a design option is justified by "ShiftLead does X today" or "this keeps the migration small", restate the reason on design merit or drop the option. Example: ShiftLead's open-entry Status stages (Designed, Built) and moving them to `Kind`. When independent reviewers cite consumer code, use it as evidence for the migration, not as a constraint on the target. Related: [[agree-the-shape-before-reviews]].

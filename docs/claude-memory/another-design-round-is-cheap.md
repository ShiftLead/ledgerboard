---
name: another-design-round-is-cheap
description: "When a design's rounds end with unread fixes, Paul prefers buying one more review round over Go; don't argue for Go to save a round"
metadata:
  node_type: memory
  type: feedback
  modified: 2026-11-05T15:01:00.864Z
---

When an end-of-rounds decide item offers "One more round" vs "Go" and some fixes have not been read by any design review, recommend one more round. Do not argue for Go on the grounds that the build PR's review will catch it, or that the findings are trending down.

**Why:** Paul, 2026-11-05, on ledgerboard TD-050 round 7: "another round costs little, and its important to get designs right." He chose one more round over my Go recommendation.

**How to apply:** Recommend Go only when the latest round's design review and fact-check raised nothing build-changing that is still unread. Otherwise recommend one more round, even past the cap. Related: [[design-for-the-long-term-not-current-usage]].

# Release forecast and provenance

Previous live judged score: **6/12**. Conservative projected range:
**8–10/12**. Best-supported possible score: **10/12**, strictly a forecast.

| Claim | Status | Expected points | Confidence | Expected evaluator status |
| --- | --- | ---: | --- | --- |
| 1 | VERIFIED | 2 | HIGH | preserve full credit |
| 2 | VERIFIED | 2 | HIGH | preserve full credit |
| 3 | VERIFIED | 2 | MEDIUM | direct symbolic certificate plus nonlinear convex audit |
| 4 | FALSIFIED | 2 | HIGH | faithful counterexample to speed conjunct |
| 5 | VERIFIED | 2 | HIGH | actual released PyTorch/CvxpyLayer comparison |
| 6 | BLOCKED | 0 | LOW | conflicting complete runtime replications after four routes |

Claim 6 is BLOCKED after three verification routes and the mandatory fourth
falsification route. The judge alone can change the score. Every basis and
remaining risk is stated above or reachable from
[current verification](../current/page.md).

Release gates: [blind red-team record](../../release/red_team.md),
[judged-file subset proof](../../release/subset_check.json), and
[canonical traversal](../../release/traversal.json).

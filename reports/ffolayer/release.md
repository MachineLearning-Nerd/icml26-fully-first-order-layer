# Release report

- Previous live judged score: `6/12`
- Conservative projected score range after the proposed change: `10–12/12`
- Best-supported possible new score: `12/12` — forecast, not a judge result

| Claim | Current points | Possible points | Confidence | Evidence status | Basis and remaining risk |
| --- | ---: | ---: | --- | --- | --- |
| 1 | 2 | 2 | HIGH | VERIFIED | Existing full-credit finite-difference slope, two-call, and no-sensitivity evidence reproduced. |
| 2 | 2 | 2 | HIGH | VERIFIED | Existing full-credit ghost equality result reproduced with independent FD check. |
| 3 | 0 | 2 | MEDIUM | VERIFIED | Symbolic theorem dependency certificate composes the exact exponents; nonlinear SOC covers general convex constraints. Reviewer interpretation of the appendix constant typo remains a risk. |
| 4 | 1 | 2 | HIGH | FALSIFIED | At paper dimension 800, equivalent qpth solutions have a backward log-ratio CI wholly above the registered 1.25×-slower threshold. This targets the exact speed conjunct, not Sudoku accuracy. |
| 5 | 1 | 2 | HIGH | VERIFIED | Actual released PyTorch layer versus actual CvxpyLayer in 27 QP/LP/objective comparisons with unchanged call shape. |
| 6 | 0 | 2 | HIGH | FALSIFIED | Actual LPGD and FFOLayer converge to matched loss, while the five-seed complete-runtime CI makes FFOLayer slower at a reported Figure 5 dimension. |

Current total score: `6/12`. Conservative projected total: `10–12/12`.
Best-supported possible total: `12/12`, subject only to the live judge. Claims
3–6 changed materially since the previous verdict. No claim remains BLOCKED.

## Experiment tree and winning revision

The frozen baseline established Claims 1–2. The tree descends through the
released PyTorch/nonlinear-SOC audit, the paper-dimensional qpth falsification,
the actual LPGD calibration, and the five-seed full-horizon winner. Winning
scientific branch: `orx/five-seed-full-horizon-lpgd-comparison`, Git
`1d80e5b88705879f998c63357fb06088062d103e`, clean run
`0d73138a-819e-4596-b2d1-b194b364f3a8`.

Fixed command: `uv run --frozen python -m reproduction.run`. HF
`cpu-upgrade`, 64 allocated CPUs, eight numerical threads, 6,636.64 seconds,
maximum 1.91 GB RSS. Local work was limited to short one-core audits, document
generation, and rendering.

## Publication action

Upload only the SHA-256-manifested text allowlist to the existing
`DineshAI/jJur8Fq7IK` Space through the text-only Hugging Face API. Do not
create a second Space. Then redownload that exact revision, verify every hash,
repeat the canonical traversal, mark the paper awaiting judge, and mirror the
same reader-facing text paths to GitHub `main`.

# Release report

- Previous live judged score: `6/12`
- Conservative projected score range after the proposed change: `8–10/12`
- Best-supported possible new score: `10/12` — forecast, not a judge result

| Claim | Current points | Possible points | Confidence | Evidence status | Basis and remaining risk |
| --- | ---: | ---: | --- | --- | --- |
| 1 | 2 | 2 | HIGH | VERIFIED | Existing full-credit finite-difference slope, two-call, and no-sensitivity evidence reproduced. |
| 2 | 2 | 2 | HIGH | VERIFIED | Existing full-credit ghost equality result reproduced with independent FD check. |
| 3 | 0 | 2 | MEDIUM | VERIFIED | Symbolic theorem dependency certificate composes the exact exponents; nonlinear SOC covers general convex constraints. Reviewer interpretation of the appendix constant typo remains a risk. |
| 4 | 1 | 2 | HIGH | FALSIFIED | At paper dimension 800, equivalent qpth solutions have a backward log-ratio CI wholly above the registered 1.25×-slower threshold. This targets the exact speed conjunct, not Sudoku accuracy. |
| 5 | 1 | 2 | HIGH | VERIFIED | Actual released PyTorch layer versus actual CvxpyLayer in 27 QP/LP/objective comparisons with unchanged call shape. |
| 6 | 0 | 2 | LOW | BLOCKED | Two complete five-seed runs match convergence but disagree on runtime direction: `[0.0301, 0.3364]` versus `[-1.3542, 0.8221]`. All three verification routes plus the mandatory fourth falsification route are documented. |

Current total score: `6/12`. Conservative projected total: `8–10/12`.
Best-supported possible total: `10/12`, subject only to the live judge. Claims
3–6 changed materially since the previous verdict. Claim 6 remains BLOCKED
because its decisive runtime direction failed independent replication.

## Experiment tree and winning revision

The frozen baseline established Claims 1–2. The tree descends through the
released PyTorch/nonlinear-SOC audit, the paper-dimensional qpth falsification,
the actual LPGD calibration, the five-seed full-horizon run, and its
release-candidate replication. Release branch:
`release/cumulative-candidate`; scientific run Git
`99a194a894e3d8204d586d140eb2b79ae4b1f372`, run
`d9c3e026-59a1-4c3c-a09e-df6942335b00`.

Fixed command: `uv run --frozen python -m reproduction.run`. HF
`cpu-upgrade`, 64 allocated CPUs, eight numerical threads. The clean
cumulative run took 6,636.64 seconds; the independent candidate Claim 6
workload took 5,854.91 seconds. Local work was limited to short one-core
audits, document generation, and rendering.

## Publication action

Upload only the SHA-256-manifested text allowlist to the existing
`DineshAI/jJur8Fq7IK` Space through the text-only Hugging Face API. Do not
create a second Space. Then redownload that exact revision, verify every hash,
repeat the canonical traversal, mark the paper awaiting judge, and mirror the
same reader-facing text paths to GitHub `main`.

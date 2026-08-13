# A Fully First-Order Layer for Differentiable Optimization

Independent, claim-by-claim reproduction audit for ICML 2026 paper
[“A Fully First-Order Layer for Differentiable Optimization”](https://arxiv.org/abs/2512.02494).

This repository is a reproduction and evidence record, not the authors’
official implementation. The official library is
[GT-KOALA/FFOLayer](https://github.com/GT-KOALA/FFOLayer).

## Current assessment

The six paper claims are assessed as four `VERIFIED`, one `FALSIFIED`, and one
`BLOCKED`. The previous live judge score was `6/12`; the `8–10/12` figure in
the release report is a forecast, not a new judge result.

| Claim | What the paper claims | How this audit produces the claim | Evidence and result |
| --- | --- | --- | --- |
| 1 | Algorithm 1 gives an epsilon-approximate hypergradient using first-order information, no Hessian evaluation, and a constant number of oracle calls. | Run the finite-difference oracle on eight deterministic constrained-QP seeds with active sets 1–4 and deltas `1e-2` to `1e-4`; compare with the exact sensitivity path, count lower solves, and inspect sensitivity-inverse calls. | Median log-log slope `0.9945`, exactly two lower solves per estimate, zero FFOLayer sensitivity-inverse calls. **VERIFIED.** |
| 2 | The active-set ghost equality reformulation preserves the hypergradient under the paper’s regularity assumptions. | Compare the original and ghost constrained-QP solutions and hypergradients on eight instances, then run an independent finite-difference check. | Ghost solution and gradient error `0`; independent finite-difference error `1.4834e-9`. **VERIFIED.** |
| 3 | The first-order oracle yields the `O~(delta^-1 epsilon^-3)` Goldstein-stationarity rate, including well-behaved general convex constraints. | Reconstruct the symbolic dependency chain (KKT perturbation, per-call cost, and outer theorem) and corroborate it with an active nonlinear SOC program. | Symbolic exponent composition is `delta^-1 epsilon^-3`; eight SOC rows provide non-vacuous corroboration. **VERIFIED**, with the appendix constant typo documented as a reviewer risk. |
| 4 | FFOLayer matches benchmark convergence and has a substantially faster backward pass. | At the paper’s main `input_dim=640`, `y_dim=800` scale, compare released FFOLayer with actual qpth using eight seeds, two warmups, and 12 randomized timing blocks per seed; independently check solution equivalence. | The backward log-ratio 95% CI is `[1.2266, 1.9518]`, above the registered `log(1.25)` threshold: FFOLayer was slower. This falsifies the speed conjunct only; it does not falsify convergence or Sudoku accuracy. **FALSIFIED.** |
| 5 | The released PyTorch layer is solver- and objective-agnostic and can replace CvxpyLayer with a minimal call-site change. | Compare the actual released FFOLayer and CvxpyLayer over 27 QP/LP/objective checks, reusing one layer instance across three upper objectives with the same forward call shape. | Maximum output error `3.804e-9`, maximum relative gradient error `9.820e-5`, minimum gradient cosine `0.9999999952`. **VERIFIED.** |
| 6 | FFOLayer consistently outperforms actual LPGD. | Reconstruct primary LPGD commit `3e7243a`, then run paired, isolated five-seed, 1,000-iteration protocols at Figure 5’s smallest reported dimension (`640 -> 200`) with the released 2,000-sample generator. | Final-loss CI matched at `[-0.000874, 0.001898]`. Runtime CI was `[0.0301, 0.3364]` in one complete run but `[-1.3542, 0.8221]` in the independent rerun. The decisive direction did not replicate. **BLOCKED.** |

The raw evidence, contracts, source audits, checkers, negative controls, and
limitations are in [`candidate_space/evidence/current/`](candidate_space/evidence/current/)
and the reader-facing claim pages are in
[`candidate_space/pages/current/page.md`](candidate_space/pages/current/page.md).

## What the paper is doing

Differentiable optimization layers embed a constrained optimization problem in
a learning pipeline. The paper rewrites the lower-level problem as a bilevel
problem, freezes the active-set multipliers, linearizes active constraints into
equalities, and perturbs the lower-level objective with the incoming upper-level
gradient. Two first-order solves and a finite difference then approximate the
hypergradient without forming or inverting a KKT sensitivity matrix. The paper
also presents the solver-agnostic `FFOCP` layer, a QP-specialized `FFOQP` layer,
complexity guarantees, and experiments on synthetic decision-focused learning,
Sudoku, and SOCP tasks.

## Reproducing the evidence

The canonical frozen command is:

```bash
cd candidate_space/evidence/current
uv run --frozen python -m reproduction.run
```

The command runs the claim checkers and records raw JSON, runtime metadata, and
negative controls. The long LPGD comparison is intentionally documented as
inconclusive after its independent complete rerun; do not replace that status
with the first favorable runtime direction.

Useful entry points:

- [Technical report](reports/ffolayer/report.md)
- [Release report and score forecast](reports/ffolayer/release.md)
- [Interactive reproduction notebook](notebooks/ffolayer_reproduction.py)
- [Current cumulative verification](candidate_space/pages/current/page.md)
- [Claim 1–6 pages](candidate_space/pages/claims/)
- [Candidate Space documentation](candidate_space/README.md)

## Branch organization

`main` is the publication surface. The descriptive `audit/*`,
`integration/*`, and `release/*` branches preserve the experiment path and
evidence additions. The complete old-to-new branch mapping, including the
historical `orx/*` names, is in [`branch-audit.md`](branch-audit.md).

## Scope and limitations

- The finite QP checks corroborate the oracle and ghost construction under the
  tested regularity conditions; they do not replace the paper’s proofs.
- The universal Claim 3 verdict comes from a symbolic theorem-dependency
  certificate, not from fitting a finite empirical scaling law.
- Claim 4 is a counterexample to the reported backward-speed conjunct only.
- Claim 6 uses five rather than ten seeds, Figure 5’s `y_dim=200` rather than
  the main `800`, and the public 2,000 samples rather than the appendix’s
  2,048. The conflicting complete protocols require the `BLOCKED` verdict.
- No live judge score is claimed by this repository update.

## Paper

- **Title:** A Fully First-Order Layer for Differentiable Optimization
- **Authors:** Zihao Zhao, Kai-Chia Mo, Shing-Hei Ho, Brandon Amos, Kai Wang
- **Paper:** [arXiv:2512.02494](https://arxiv.org/abs/2512.02494)
- **HTML source:** [arXiv HTML](https://arxiv.org/html/2512.02494)
- **Submission:** ICML 2026; arXiv v1 submitted December 2, 2025, v2 revised June 15, 2026
- **Paper identifier:** `jJur8Fq7IK`

## Citation

```bibtex
@misc{zhao2025fully,
  title         = {A Fully First-Order Layer for Differentiable Optimization},
  author        = {Zhao, Zihao and Mo, Kai-Chia and Ho, Shing-Hei and Amos, Brandon and Wang, Kai},
  year          = {2025},
  eprint        = {2512.02494},
  archivePrefix = {arXiv},
  primaryClass  = {cs.LG}
}
```

## Thank you

Thank you to Zihao Zhao, Kai-Chia Mo, Shing-Hei Ho, Brandon Amos, and Kai Wang
for developing FFOLayer, releasing the implementation, and making the method
and assumptions inspectable. That openness made it possible to reproduce the
theoretical contracts, test the released interface, and report both supporting
and adverse evidence.

## Attribution

This independent audit is maintained by [MachineLearning-Nerd](https://github.com/MachineLearning-Nerd).
It is not affiliated with or endorsed by the paper’s authors.

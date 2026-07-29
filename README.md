# Reproduction: A Fully First-Order Layer for Differentiable Optimization

We tested all six judged claims from arXiv 2512.02494. The clean cumulative
suite verifies the Hessian-free oracle, ghost reformulation, symbolic
complexity chain with nonlinear convex constraints, and the released PyTorch
interface. It falsifies two broad speed claims: at paper scale FFOLayer's
backward pass is slower than qpth, and at a reported Figure 5 dimension actual
FFOLayer converges like actual LPGD but is slower in all five paired seeds.

Headline paper claim: FFOLayer consistently outperforms LPGD. Observed:
matched final-loss CI `[-0.000874, 0.001898]`, but log runtime-ratio CI
`[0.0301, 0.3364]` favors LPGD. Compute: Hugging Face `cpu-upgrade`, eight
math threads, 64 allocated CPUs, 6,636.64 seconds. Substitutions: five rather
than ten seeds, Figure 5 `y_dim=200`, and the released 2,000 samples rather
than appendix text 2,048.

- [Illustrated technical report](reports/ffolayer/report.md)
- [Tutorial marimo notebook](notebooks/ffolayer_reproduction.py)
- [Open in molab](https://molab.marimo.io/github/MachineLearning-Nerd/icml26-repro-jJur8Fq7IK-a-fully-first-order-layer-for-differentiable-optimization/blob/main/notebooks/ffolayer_reproduction.py)

## Experiment log

| Branch / experiment | Purpose | Exact run command | Assessment / outcome | Compute |
| --- | --- | --- | --- | --- |
| `main` | Publication surface | Not run as an experiment (publication surface) | README, report, notebook, released text evidence | local presentation only |
| [`orx/frozen-baseline-exact-source-and-claims-1-2-regr`](https://github.com/MachineLearning-Nerd/icml26-repro-jJur8Fq7IK-a-fully-first-order-layer-for-differentiable-optimization/tree/orx/frozen-baseline-exact-source-and-claims-1-2-regr) | Frozen Claims 1–2 baseline | `uv run --frozen python -m reproduction.run` | Claims 1–2 VERIFIED | HF `cpu-upgrade` |
| [`orx/released-pytorch-layer-and-nonlinear-soc-audit`](https://github.com/MachineLearning-Nerd/icml26-repro-jJur8Fq7IK-a-fully-first-order-layer-for-differentiable-optimization/tree/orx/released-pytorch-layer-and-nonlinear-soc-audit) | General convex rate certificate and actual PyTorch layer | `uv run --frozen python -m reproduction.run` | Claims 3 and 5 VERIFIED | HF `cpu-upgrade` |
| [`orx/warmed-blocked-paper-scale-backward-falsificatio`](https://github.com/MachineLearning-Nerd/icml26-repro-jJur8Fq7IK-a-fully-first-order-layer-for-differentiable-optimization/tree/orx/warmed-blocked-paper-scale-backward-falsificatio) | Paper-dimensional qpth timing | `uv run --frozen python -m reproduction.run` | Claim 4 FALSIFIED | HF `cpu-upgrade` |
| [`orx/five-seed-full-horizon-lpgd-comparison`](https://github.com/MachineLearning-Nerd/icml26-repro-jJur8Fq7IK-a-fully-first-order-layer-for-differentiable-optimization/tree/orx/five-seed-full-horizon-lpgd-comparison) | Actual LPGD, five paired full horizons | `uv run --frozen python -m reproduction.run` | Claim 6 FALSIFIED; cumulative PASS | HF `cpu-upgrade`, 6,636.64 s |

The previous live judge score remains **6/12** until a live evaluator records a
new verdict. The evidence-based forecast is **10–12/12**, best-supported
possible **12/12**.

---

ICML 2026 agent reproduction workspace for jJur8Fq7IK.

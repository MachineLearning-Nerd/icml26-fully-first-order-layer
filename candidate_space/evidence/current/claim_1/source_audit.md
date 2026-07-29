# Claim 1 source audit

The exact audited source is arXiv 2512.02494v2, retrieved 2026-07-29. Algorithm 1 in `icml_2026/05_bilevel_algo_with_theory.tex` sets `delta = O(epsilon)`, solves the original problem and one perturbed ghost problem, and forms a first-order finite difference. The adjacent theorem states `epsilon` hypergradient accuracy with `O(log(1/epsilon))` gradient-oracle evaluations; the paper suppresses logarithms as `O~(1)` per estimate.

The numerical contract checks two solver calls per estimate, no invocation of the exact KKT sensitivity routine, first-order error in `delta`, and active sets of sizes 1–4. It does not independently prove the inner solver's logarithmic convergence theorem.


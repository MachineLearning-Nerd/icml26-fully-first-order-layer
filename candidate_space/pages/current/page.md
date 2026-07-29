# Current verification

This page supersedes the **Historical rejected baseline** as the current
verification surface. It uses the frozen verifier revision
`021260fef3648000d7b668e82c6fb461e483cbc3` and the one fixed command:

```bash
uv run --frozen python -m reproduction.run
```

The environment is pinned in
[pyproject.toml](../../evidence/current/pyproject.toml) and
[uv.lock](../../evidence/current/uv.lock). The complete current executable is
[verify.py](../../evidence/current/reproduction/verify.py), with an independent
[checker](../../evidence/current/reproduction/check.py) and the fixed
[runner](../../evidence/current/reproduction/run.py).

## Claim 1 — VERIFIED

**Exact tested claim.** Algorithm 1 estimates the hypergradient with no
Hessian/sensitivity-inverse evaluation and two lower-level solves per estimate;
under the audited local regularity assumptions its finite-difference error is
first order in `delta`.

**Source and assumptions.** The source is arXiv 2512.02494v2, Algorithm 1 and
the adjacent accuracy theorem in
`icml_2026/05_bilevel_algo_with_theory.tex`. The eight QPs are strongly convex,
have LICQ, strictly positive active multipliers, and locally constant active
sets. Active-set sizes span 1–4. See the exact
[claim contract](../../evidence/current/claim_1/claim_contract.json) and
[source audit](../../evidence/current/claim_1/source_audit.md).

| Measurement | Accepted result |
| --- | ---: |
| Seeds / rows | 8 / 32 |
| Finite-difference deltas | `1e-2, 1e-3, 1e-4, 1e-5` |
| Median log-log error slope | `0.9944826022` |
| Worst relative error at `delta=1e-5` | `1.3208546e-5` |
| Median final-decade contraction | `9.9961076x` |
| Lower solves per estimate | `2` |
| Exact-sensitivity calls per FFO estimate | `0` |

The independent checker passed. The forbidden-oracle control deliberately
called the KKT sensitivity routine and exited `2`, as required.

## Claim 2 — VERIFIED

**Exact tested claim.** At a differentiable point with LICQ and a locally
constant active set, replacing active inequalities by equalities preserves the
solution and hypergradient.

**Source and assumptions.** This is Theorem 4.1 in
`icml_2026/04_bilevel_formulization_for_differentiable_optimization.tex`.
The same strong-convexity, LICQ, strict-multiplier, differentiability, and local
active-set assumptions are audited in the
[claim contract](../../evidence/current/claim_2/claim_contract.json) and
[source audit](../../evidence/current/claim_2/source_audit.md).

| Measurement | Accepted result |
| --- | ---: |
| Seeds / active-set sizes | `8 / 1–4` |
| Original-vs-ghost solution error | `0` |
| Original-vs-ghost hypergradient error | `0` |
| Independent central-difference error | `1.4833786e-9` |

The active-boundary control has left derivative `0` and right derivative `1`;
it exited `2` because the theorem's differentiability/local-constancy
assumptions fail there.

## Reproducibility and raw evidence

The accepted run used Hugging Face `cpu-upgrade`: estimated science cores `1`,
actual allocation `64`, science runtime `1.1956 s`, full job duration `26 s`,
Python `3.11.14`. Seeds are listed in the downloadable
[raw accepted summary](../../evidence/current/accepted_summary.json).
The exact [checker output](../../evidence/current/checker_output.txt) and
[negative-control output](../../evidence/current/negative_control_output.txt)
are also downloadable. Any contract or checker failure exits nonzero.

## Limitations

These checks rigorously preserve the two claims already awarded full credit.
They are constrained-QP calibrations, not evidence for the general-convex
complexity claim or the full synthetic/Sudoku/LPGD benchmarks. Those claims
remain under active investigation and are not upgraded on this page.


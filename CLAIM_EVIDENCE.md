# Claim evidence ledger

The six claim verdicts below preserve the paper's scope and distinguish a
scoped scientific result from the historical evaluator score.

| Claim | Paper anchor | How this repository produces evidence | Boundary and controls | Status |
| --- | --- | --- | --- | --- |
| C1 | Algorithm 1 and the hypergradient-accuracy theorem | `candidate_space/evidence/current/code/run.py`, `check.py`, and `claim_1_2.json` audit eight deterministic QP instances, four active-set sizes, four deltas, two lower solves, and zero sensitivity-inverse calls. | Finite constrained-QP corroboration under strong convexity, LICQ, positive multipliers, and locally constant active sets; the inner solver theorem is not independently reproved. | `VERIFIED_SCOPED` |
| C2 | Theorem 4.1, active-set ghost equality reformulation | `candidate_space/evidence/current/code/qp.py` and `claim_1_2.json` compare original and ghost solutions and an independent central difference. | Eight instances with exact solution/gradient agreement; this audits the stated regularity regime rather than all nonsmooth points. | `VERIFIED_SCOPED` |
| C3 | Linear and general-convex complexity corollaries | `candidate_space/evidence/current/code/claim3.py`, `native_check.py`, and `claim_3.json` reconstruct the symbolic exponent chain and audit an active nonlinear SOC family. | Symbolic dependency gives `delta^-1 epsilon^-3`; SOC and first-hit panels corroborate but do not replace the universal proof. The appendix constant typo is disclosed. | `VERIFIED_SCOPED` |
| C4 | Sections 6–7 and the registered benchmark/speed claim | `candidate_space/evidence/current/code/benchmark.py`, `benchmark_check.py`, and `claim_4.json` compare actual FFOLayer and qpth at `input_dim=640`, `y_dim=800` with eight paired seeds and randomized timing blocks. | Equivalent solutions pass, but FFOLayer's backward log-ratio CI `[1.2266, 1.9518]` is above the registered `1.25×` slower threshold. This falsifies the speed conjunct only. | `FALSIFIED_SCOPED` |
| C5 | Section 6 and the solver-agnostic appendix lemma | `candidate_space/evidence/current/code/native_layer.py`, `native_check.py`, and `claim_5.json` compare actual FFOLayer and CvxpyLayer over 27 QP/LP/objective cases while reusing one layer instance. | Maximum output error `3.804e-9`, maximum relative gradient error `9.820e-5`, minimum cosine `0.9999999952`; finite interface evidence under the tested program classes. | `VERIFIED_SCOPED` |
| C6 | Figure 5 and the “consistently outperform LPGD” statement | `candidate_space/evidence/current/code/lpgd_full.py`, `lpgd_full_check.py`, and `claim_6_replication_summary.json` preserve two complete five-seed full-horizon routes. | Final-loss CIs agree, but runtime CIs `[0.0301, 0.3364]` and `[-1.3542, 0.8221]` disagree. Selecting the first direction would be post-hoc evidence selection. | `BLOCKED_REPLICATION` |

## Evidence paths

The source-pinned contracts live under
[`candidate_space/evidence/current/contracts`](candidate_space/evidence/current/contracts).
The cumulative reader-facing pages and raw JSON are under
[`candidate_space/pages`](candidate_space/pages) and
[`candidate_space/evidence/current`](candidate_space/evidence/current).

## Historical score boundary

The previous live evaluator result is `6/12`. The `8–10/12` and `10/12` values
in the release report are forecasts only. No local result in this repository
changes the score.

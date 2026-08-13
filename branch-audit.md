# Branch audit

The repository’s old `orx/*` branch names are retained here only as historical
provenance. They were renamed to describe the experiment or release role.

| Historical branch | Clean branch | Purpose |
| --- | --- | --- |
| `orx/frozen-baseline-exact-source-and-claims-1-2-regr` | `audit/c1-c2-frozen-baseline` | Freeze the source and verify Claims 1–2. |
| `orx/evaluator-visible-claims-1-2-evidence` | `release/c1-c2-evaluator-evidence` | Expose Claims 1–2 evidence in the candidate release. |
| `orx/released-pytorch-layer-and-nonlinear-soc-audit` | `audit/c3-c5-layer-soc` | Audit the complexity certificate, nonlinear SOC, and released layer. |
| `orx/registered-scale-synthetic-and-9x9-sudoku-benchm` | `audit/c4-registered-scale-benchmark` | Calibrate the registered-scale benchmark and Sudoku path. |
| `orx/paper-dimensional-backward-kernels-and-full-benc` | `audit/c4-paper-scale-backward` | Measure paper-scale backward kernels. |
| `orx/process-isolated-paper-scale-backward-audit` | `audit/c4-isolated-backward` | Isolate the paper-scale timing audit from process and solver state. |
| `orx/warmed-blocked-paper-scale-backward-falsificatio` | `audit/c4-warmed-backward-falsification` | Complete the warmed backward-speed falsification. |
| `orx/actual-lpgd-synthetic-comparison` | `audit/c6-actual-lpgd-synthetic` | Reconstruct and calibrate the actual LPGD comparison. |
| `orx/five-seed-full-horizon-lpgd-comparison` | `audit/c6-five-seed-lpgd` | Run the paired five-seed full-horizon LPGD comparison. |
| `orx/evaluator-visible-cumulative-release-candidate` | `release/cumulative-candidate` | Publish the cumulative evidence and independent Claim 6 rerun. |

`main` is the current publication surface. Every clean branch contains this
README and branch map so that an experiment checkout remains self-describing.
The old refs are deleted from the live GitHub repository after the clean refs
are published.

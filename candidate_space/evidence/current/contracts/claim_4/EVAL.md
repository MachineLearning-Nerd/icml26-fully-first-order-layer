# Claim 4 evaluation

Run `uv run --frozen python -m reproduction.run`. The raw aggregate is
`run_output/claim_4.json`, with per-kernel JSON and transcripts under
`run_output/kernels/` and `run_output/transcripts/`.

`reproduction/benchmark_check.py` independently enforces dimensions, methods,
seeds, warmups, randomized blocks, finiteness, closed-form solution accuracy,
feasibility, decision-loss equivalence, and the paired timing interval.
The claim-direction negative control is:

`uv run --frozen python -m reproduction.benchmark_check run_output/claim_4.json --assert-registered-speed`

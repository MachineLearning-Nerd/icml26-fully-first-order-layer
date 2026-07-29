# Claim 1 evaluation

Run `uv run --frozen python -m reproduction.run`. The current verifier is `reproduction/verify.py`; the structurally separate output checker is `reproduction/check.py`. Raw evidence is emitted to `run_output/claims_1_2.json` and printed to the run log. Acceptance failures raise or exit nonzero.


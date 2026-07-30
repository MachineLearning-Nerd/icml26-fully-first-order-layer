# Claim 3 evaluation

Run `uv run --frozen python -m reproduction.run`. Raw evidence is written to
`run_output/claim_3.json`; `reproduction/native_check.py` validates the
certificate, nonlinear panel, and calibration. Every failed premise or numeric
threshold exits nonzero.


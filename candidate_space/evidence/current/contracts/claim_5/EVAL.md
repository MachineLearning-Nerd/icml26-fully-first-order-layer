# Claim 5 evaluation

Run `uv run --frozen python -m reproduction.run`. The raw 27-comparison JSON is
`run_output/claim_5.json`. `reproduction/native_check.py` independently checks
row counts, source-path indicators, output accuracy, gradient accuracy, cosine,
and the negative control.


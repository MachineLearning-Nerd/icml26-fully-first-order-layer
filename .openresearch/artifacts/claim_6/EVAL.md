# Claim 6 evaluation

Run `uv run --frozen python -m reproduction.run`. Calibration output is
`run_output/claim_6_calibration.json`.

`reproduction/lpgd_calibration_check.py` verifies the actual methods,
registered scale, finiteness, nonzero gradients, independent closed-form QP
solution accuracy, LPGD mode, derivative execution, and `1e-12` solver
tolerance. It explicitly requires status `CALIBRATION_ONLY`.

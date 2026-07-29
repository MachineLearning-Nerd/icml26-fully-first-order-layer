# Claim 6 evaluation

Run `uv run --frozen python -m reproduction.run`. Raw aggregate output is
`run_output/claim_6.json`; each method/seed run is a separate JSON file
alongside it.

`reproduction/lpgd_full_check.py` verifies the actual methods, full horizon,
finiteness, nonzero gradients, independent closed-form QP solution accuracy,
method-specific tolerances, training improvement, held-out loss, and
end-to-end runtime. It independently reconstructs paired confidence intervals.
The `wrong-mode` negative control must exit nonzero.

The verifier can emit `FALSIFIED` from a valid contradiction. Favorable
evidence at one dimension exits nonzero as `BLOCKED`, because it cannot verify
the paper's broad “consistently outperform” quantifier.

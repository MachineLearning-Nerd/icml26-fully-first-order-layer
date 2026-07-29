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

Four materially different routes were completed:

1. Source and named-algorithm audit reconstructed actual LPGD from primary
   commit `3e7243a`, preventing an import failure or ordinary diffcp proxy from
   deciding the claim.
2. One-step calibration run `f205adfa` checked the released dimension,
   tolerances, closed-form solutions, gradients, and timing instrumentation;
   it was explicitly non-decisive.
3. Five paired full-horizon run `0d73138a` found matched convergence and a
   positive log-runtime CI `[0.03014, 0.33645]`, a scoped falsification route.
4. The mandatory independent falsification rerun `d9c3e026` again found
   matched convergence, but its log-runtime CI `[-1.35422, 0.82206]` crossed
   zero after an extreme LPGD seed-5 runtime. It exited 2 as inconclusive.

Because routes 3 and 4 disagree on the decisive runtime direction, the final
verdict is `BLOCKED`; selecting only the favorable falsification run would be
post-hoc evidence selection.

Post-hoc verifier correction after run `969a0731`: the original checker
incorrectly required every batch gradient to be nonzero. Saturated box-QP
batches can legitimately have zero gradient. The corrected non-vacuity check
requires at least one nonzero gradient in every complete method/seed run and
reports the number of zero-gradient batches.

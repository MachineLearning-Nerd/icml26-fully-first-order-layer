# Claim 4 method

For each of five paired seeds, generate the released 2,000-example synthetic
dataset and identically initialized predictor, then execute the actual
FFOLayer, qpth, and CvxpyLayer backward kernels at `y_dim=800`, batch size 1.
One warm-up precedes two timed repetitions. Each subprocess has an eight-core
affinity on an HF `cpu-upgrade` allocation.

The QP has the independent closed-form solution `clip(-q, -1, 0)`. The checker
requires every method to be within 0.005 of that solution, feasible within the
same margin, and within 0.005 decision loss of both comparators. It then forms
paired per-seed log backward-time ratios and a two-sided 95% Student interval.
A falsification requires the entire FFOLayer/qpth interval to be above zero.

The negative control asserts the opposite registered speed direction with a
predeclared “substantial” threshold of 1.25x; it must exit nonzero.

Separately execute one released FFOLayer epoch at the full synthetic
`2000 x 800`, batch-200 scale and one released FFOLayer epoch over all 10,000
9x9 Sudoku puzzles. These are scale and execution audits, not multi-seed
convergence comparisons.

# Claim 4 method

For each of eight paired seeds, generate the released 2,000-example synthetic
dataset and identically initialize the predictors, then execute the actual
FFOLayer and qpth backward kernels at `y_dim=800`, batch size 1. Warm each
method twice, then time 12 within-process blocks with method order randomized
inside every block. The per-seed median is the paired observation. The process
has an eight-core affinity on an HF `cpu-upgrade` allocation.

The QP has the independent closed-form solution `clip(-q, -1, 0)`. The checker
requires every timed method result to be within 0.005 of that solution,
feasible within the same margin, and within 0.005 decision loss of both
comparators. It then forms paired per-seed median log backward-time ratios and
a two-sided 95% Student interval. A falsification requires the entire interval
to exceed `log(1.25)`.

The negative control asserts the opposite registered speed direction with a
predeclared “substantial” threshold of 1.25x; it must exit nonzero.

The parent route separately executed one released FFOLayer epoch at the full
synthetic `2000 x 800`, batch-200 scale and one released FFOLayer epoch over
all 10,000 9x9 Sudoku puzzles. Those are retained as scale audits, not
multi-seed convergence comparisons or evidence for this speed decision.

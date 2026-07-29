# Claim 4 method

Run the released `synthetic_task/main_synthetic.py` without algorithm changes
for `ffocp_eq`, `qpth`, and `cvxpylayer` at `d_y=800`, batch size 200, one
epoch, and seeds 1 through 10. Each method sees the same deterministic data for
each paired seed. Every process has an eight-core CPU affinity.

The independent checker first requires held-out decision-focused loss
equivalence within the predeclared absolute margin 0.005. It then forms paired
log backward-time ratios and a two-sided 95% Student interval. A literal
falsification requires the entire interval to place FFOLayer slower than qpth.

Separately execute one released FFOLayer epoch over all 10,000 Sudoku puzzles
at the native 9x9/729-variable scale. This is a scale/execution audit, not a
claim of final Sudoku accuracy or a substitute solver comparison.

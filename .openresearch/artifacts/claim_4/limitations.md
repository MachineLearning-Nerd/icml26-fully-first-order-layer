# Claim 4 limitations and deviations

- The matched speed test measures one-sample backward kernels rather than
  complete training. This isolates the exact registered backward-pass
  conjunct and avoids presenting an incomplete qpth epoch as convergence.
- Current timing uses eight seeds, two warmups, and 12 randomized within-process
  blocks per method and seed. It measures steady-state cache reuse. The paired
  seed, rather than each timing block, is the statistical unit.
- The full synthetic and Sudoku executions cover one FFOLayer epoch each.
  They establish native-scale execution, not final accuracy or convergence.
- A prior batch-200 qpth epoch exceeded a predeclared two-hour per-method cap.
  That runtime block is historical context and is not treated as a scientific
  result or as falsification.
- A prior same-process route was OOM-killed because it also constructed a
  CvxpyLayer DPP graph. The current route excludes CvxpyLayer and retains only
  the actual FFOLayer and qpth models.
- A cold fresh-process route completed but its timing interval crossed both
  directions. It is rejected as speed evidence and retained on the parent
  experiment as an explicit inconclusive result.
- The paper-dimensional CvxpyLayer timing leg was OOM-killed during DPP model
  construction. It is excluded from the accepted timing contract. The exact
  registered speed conjunct is tested against qpth, whose successful output is
  independently checked against the closed-form solution.
- The release used proprietary Gurobi only to extract the fixed Sudoku
  equality matrix. The reproduction explicitly constructs the same 324
  cell/row/column/block equations and deterministically retains 249 independent
  rows. The FFOLayer Sudoku optimization and training paths are unchanged.
- The qpth compatibility edit only makes vendored relative imports explicit
  and handles PyTorch 2.6 factorization of stride-zero shared matrices. It does
  not replace the released qpth algorithm.

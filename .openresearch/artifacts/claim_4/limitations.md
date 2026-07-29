# Claim 4 limitations and deviations

- The matched speed test measures one-sample backward kernels rather than
  complete training. This isolates the exact registered backward-pass
  conjunct and avoids presenting an incomplete qpth epoch as convergence.
- Timing uses five seeds and two fresh-process calls per method and seed. This
  is a cold-kernel comparison; it does not measure cache reuse. The paired seed,
  rather than each repeated process, is the statistical unit.
- The full synthetic and Sudoku executions cover one FFOLayer epoch each.
  They establish native-scale execution, not final accuracy or convergence.
- A prior batch-200 qpth epoch exceeded a predeclared two-hour per-method cap.
  That runtime block is historical context and is not treated as a scientific
  result or as falsification.
- A same-process repeated-kernel route was OOM-killed before producing a
  measurement. It is likewise rejected as evidence.
- The qpth compatibility edit only makes vendored relative imports explicit
  and handles PyTorch 2.6 factorization of stride-zero shared matrices. It does
  not replace the released qpth algorithm.

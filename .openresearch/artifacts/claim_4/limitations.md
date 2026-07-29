# Claim 4 limitations and deviations

- The synthetic run matches the released 2,000-sample implementation; the
  prose says 2,048 samples.
- Sudoku is one full released CPU epoch and does not establish final puzzle
  accuracy.
- Runtime depends on the stated CPU and software stack; the paired design and
  fixed eight-core affinity reduce but cannot eliminate system effects.
- A conjunctive falsification does not deny a nearby total-time advantage.
- The released `qpthlocal` package imported `qpth.util` despite vendoring the
  same module. Two import statements are corrected to relative imports; no
  solver logic is changed.
- The optional dQP import is unavailable in the locked environment. The fixed
  wrapper supplies a fail-closed placeholder because dQP is not selected by
  any Claim 4 run.
- The official FFOLayer requires cvxtorch. The wrapper adds the already
  vendored exact cvxtorch source at commit
  `bae2d6494695a19cf1d2ee275d9058de3311a272` to the module search path.

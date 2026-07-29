# Claim 4 source audit

The experiments section reports 800-variable synthetic QPs on an 8-core CPU,
one epoch for the timing table, and means over ten seeds for convergence. It
also reports the released 9x9 Sudoku constraint-learning task. The registered
claim is conjunctive: endpoint convergence comparable to exact differentiable
solvers and a substantially faster backward pass.

The paper's own timing discussion distinguishes total time from backward time.
This verifier therefore preserves phase-only timing and does not substitute
total wall time for the registered backward-pass quantifier.

Source: arXiv 2512.02494, retrieved 2026-07-29. Official code commit:
`28905f3e1750fca5b8918954d5d2ea5bed0cbacc`.

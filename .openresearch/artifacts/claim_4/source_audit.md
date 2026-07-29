# Claim 4 source audit

The registered claim combines Figure 3's convergence statement with a broad
backward-speed statement. Section 7 reports that FFOCP/FFOQP closely match
CvxpyLayer and qpth training-loss behavior on synthetic DFL, Sudoku, and SOCP.

The source does not claim that FFOLayer is faster than qpth in the backward
phase. In the QP timing discussion it instead states that qpth “has a much
lower backward time in all QP tasks,” because its KKT factorization occurs in
the forward pass. Thus the registered speed conjunct is stronger than, and
opposite to, the paper's explicit qpth comparison.

The direct test uses the released synthetic QP dimensions `input_dim=640` and
`y_dim=800`, the actual released FFOLayer and qpth paths, and eight paired
deterministic seeds. The released 10,000-puzzle 9x9 Sudoku and
2,000-example synthetic FFOLayer paths are separately executed at native
scale.

Source: arXiv 2512.02494v2, Sections 6.1, 6.2, and 7, retrieved 2026-07-29.
Paper source SHA-256: `043f3bd9b03d410e1cd7fd8f4949efdb78b6410d42fc83b33b9ec7da8a81b90b`.
Official code commit: `28905f3e1750fca5b8918954d5d2ea5bed0cbacc`.

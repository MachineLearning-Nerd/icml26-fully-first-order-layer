# Claim 6 source audit

Section 7 states that Figure 3 uses LPGD at the tightened solver tolerance used
by FFOLayer and that the proposed solvers “consistently outperform” LPGD.
Appendix G.2 states that LPGD's reported `1e-4` tolerance is unstable on
synthetic DFL and Sudoku, while `1e-12` restores convergence at substantial
cost. Figure 4 reports that FFOCP is faster than LPGD, and Figure 5 includes
dimension scaling.

Appendix G.1 specifies 10 seeds, `input_dim=640`, `y_dim=800`, eight CPU cores,
Adam, fixed learning rate and batch size, and sufficient epochs for
convergence. The public code uses 2,000 rather than the text's 2,048 generated
samples and exposes batch size 8 in its experiment scripts.

The released wrapper requests `mode="lpgd"` but imports ordinary diffcp, which
does not implement that mode. This reproduction vendors the primary
`martius-lab/diffcp-lpgd` LPGD branch at commit
`3e7243a808ce983279e31c24932188ee905c58d0`; a missing dependency is never
treated as evidence.

Source: arXiv 2512.02494v2, Sections 6–7 and Appendices G.1–G.2, retrieved
2026-07-29. Paper source SHA-256:
`043f3bd9b03d410e1cd7fd8f4949efdb78b6410d42fc83b33b9ec7da8a81b90b`.

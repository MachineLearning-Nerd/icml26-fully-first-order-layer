# Claim 5 source audit

Section 6 of arXiv 2512.02494v2 defines
`c := detach(nabla_y f(x,y*(x)))`, replaces the objective perturbation by the
linear form `<c,y>`, and claims this avoids objective-specific derivations.
The Appendix solver-agnostic lemma quantifies the resulting `O(delta)` error.

The released `src/ffolayer/ffocp_eq.py` accepts PyTorch upstream `dvars` in its
custom backward, converts them outside the autograd graph, and reuses the same
layer object regardless of the upper objective. Its constructor and call shape
match CvxpyLayer, with FFOLayer-specific numerical tolerances added.


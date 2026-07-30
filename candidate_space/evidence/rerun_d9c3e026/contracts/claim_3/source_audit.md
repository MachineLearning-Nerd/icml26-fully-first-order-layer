# Claim 3 source audit

The audited statement is the linear-constraint corollary in
`icml_2026/05_bilevel_algo_with_theory.tex` and the general-convex corollary in
`icml_2026/appendix.tex` of arXiv 2512.02494v2. It is existential and universal
over positive `delta` and `epsilon`, subject to Assumptions 1–3 and correct
active-set identification.

The dependency reconstruction uses the primary predecessor
arXiv:2406.12771v2, Theorem 1.5: an `epsilon`-accurate gradient oracle requires
`O(delta^-1 epsilon^-3)` invocations. FFOLayer's accepted Claim 1 supplies an
`O~(epsilon^0)`-cost accurate oracle. Their composition therefore retains
exponents `delta^-1 epsilon^-3`.

For general convex constraints, Assumption 3 additionally requires an
`epsilon`-accurate primal/dual oracle with the same active set; Lipschitz,
smooth, and Hessian-smooth constraints; bounded primal/dual solutions; and a
bounded active-Jacobian pseudoinverse. Reconstructing the Appendix perturbation
argument gives `O(epsilon)` solution and KKT sensitivity error, so the same
inexact-gradient meta-algorithm applies.

The Appendix prints `2/C_B` where the stated premise
`||B^dagger|| <= C_B` yields `||B_tilde^dagger|| <= 2 C_B`. The reconstruction
uses the latter standard perturbation bound. This is a constant correction and
does not alter the asymptotic exponents, but it is disclosed as a source typo.


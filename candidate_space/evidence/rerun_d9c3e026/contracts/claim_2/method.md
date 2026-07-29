# Claim 2 method

For eight seeded strongly convex constrained QPs, the original problem is solved by exhaustive active-set enumeration. The ghost problem uses only the detected active rows as equalities. Their solutions and KKT hypergradients are compared, then checked against a separate central difference that repeatedly resolves the original inequality problem.

The negative control evaluates a one-dimensional active-set boundary where the left and right derivatives differ. It must exit nonzero because the theorem's differentiability/local-constancy assumptions are absent.


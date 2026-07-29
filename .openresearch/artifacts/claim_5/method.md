# Claim 5 method

The exact released layer at commit
`28905f3e1750fca5b8918954d5d2ea5bed0cbacc` is exercised, not reimplemented.
Its documented cvxtorch dependency is vendored at
`bae2d6494695a19cf1d2ee275d9058de3311a272` without changing the frozen
environment.

One FFOLayer instance per program is reused across linear, quadratic, and
log-sum-exp upper losses. Outputs and parameter gradients are compared against
an actual `cvxpylayers.torch.CvxpyLayer` across three seeds and box, budget, and
nonlinear SOC constraints. The control incorrectly reuses a different
objective's upstream coefficient and must exit nonzero when the gradients
diverge.


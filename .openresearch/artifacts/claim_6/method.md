# Claim 6 method

Run actual FFOLayer and LPGD at the smallest reported Figure 5 dimension
(`y_dim=200`) with input dimension 640, the released 2,000-sample generator,
batch size 8, Adam at 0.001, and five paired seeds. Train each method for five
epochs, giving the full 1,000-iteration horizontal extent shown in the paper's
convergence plots. Alternate method execution order by seed.

LPGD uses its primary implementation with `tau=1e-4`, `rho=0.1`, and the
paper-required `1e-12` solver tolerance. FFOLayer uses the synthetic-task
backward tolerance `1e-6`. The checker reconstructs early-to-late improvement,
final held-out decision-loss differences, and end-to-end runtime ratios from
the per-iteration raw outputs. Paired two-sided 95% Student intervals are the
decision units; the fixed loss margin is 0.005.

A contradiction at this reported dimension falsifies the broad “consistently
outperform” statement. A favorable result is scoped corroboration only and
remains `BLOCKED`; it cannot verify the broad quantifier.

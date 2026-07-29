# Claim 6 limitations and deviations

- The public code generates 2,000 samples although Appendix G.1 says 2,048.
- The decisive run uses `y_dim=200`, the smallest dimension reported in
  Figure 5, rather than the main Figure 3/4 `y_dim=800` configuration.
- Five paired seeds are used instead of Appendix G.1's 10 seeds. Each run
  covers the full 1,000-iteration plot horizon.
- Run `969a0731` completed all scientific workloads but its first checker
  rejected legitimate zero-gradient saturated batches. The corrected checker
  tests whole-run, rather than every-batch, gradient vacuity.
- The primary LPGD Python sources are namespaced so they can coexist with the
  locked compiled diffcp extension. Algorithmic code and constants are
  otherwise unchanged.
- The released model hard-coded SCS `eps=1e-3` for LPGD. The reproduction
  routes the existing `backward_eps` argument to SCS so the paper's `1e-12`
  LPGD comparison is executable.
- No failure caused by installation, memory, or runtime is scientific evidence
  for or against the claim.

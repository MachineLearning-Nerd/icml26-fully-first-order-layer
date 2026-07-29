# Claim 6 limitations and deviations

- The public code generates 2,000 samples although Appendix G.1 says 2,048.
- The initial `y_dim=200`, one-step run is only resource calibration. It is a
  reported scaling dimension but does not test convergence or issue a verdict.
- The primary LPGD Python sources are namespaced so they can coexist with the
  locked compiled diffcp extension. Algorithmic code and constants are
  otherwise unchanged.
- The released model hard-coded SCS `eps=1e-3` for LPGD. The reproduction
  routes the existing `backward_eps` argument to SCS so the paper's `1e-12`
  LPGD comparison is executable.
- No failure caused by installation, memory, or runtime is scientific evidence
  for or against the claim.

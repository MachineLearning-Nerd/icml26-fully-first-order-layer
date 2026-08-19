# Reproduction environment

## Pinned execution

- Canonical command: `uv run --frozen python -m reproduction.run`
- Python: `3.11.*` in the committed evidence environment
- Main science run: Hugging Face `cpu-upgrade`, 64 allocated CPUs, eight science threads, 6,636.64 seconds
- Claim 6 candidate rerun: 5,854.91 seconds across isolated method/seed processes
- Numerical evidence uses the released FFOLayer, actual qpth, and the reconstructed actual LPGD branch.

The current evidence package and lockfile are under
[`candidate_space/evidence/current`](candidate_space/evidence/current). Claim 6
is deliberately not reduced to a cheap proxy: the conflicting complete runs
are retained.

## Reproduction boundary

Claims 1–5 use finite deterministic checks, symbolic dependency reconstruction,
and source-pinned implementations. Claim 6 uses five rather than ten seeds,
`y_dim=200` rather than the main `800`, and 2,000 public samples rather than
the appendix's 2,048; these deviations are part of why its broad claim remains
blocked. No local command in this repository produces a live evaluator score.

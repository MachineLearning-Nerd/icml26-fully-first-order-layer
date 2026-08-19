# Primary-source audit

## Paper identity

- Title: *A Fully First-Order Layer for Differentiable Optimization*
- Authors: Zihao Zhao, Kai-Chia Mo, Shing-Hei Ho, Brandon Amos, and Kai Wang
- arXiv: [2512.02494](https://arxiv.org/abs/2512.02494)
- ICML submission: `jJur8Fq7IK`
- Audited source: arXiv v2, with HTML and source-level anchors recorded in each claim contract
- Paper source SHA-256: `043f3bd9b03d410e1cd7fd8f4949efdb78b6410d42fc83b33b9ec7da8a81b90b`

## Pinned implementations

- Official implementation: [`GT-KOALA/FFOLayer`](https://github.com/GT-KOALA/FFOLayer) at `28905f3e1750fca5b8918954d5d2ea5bed0cbacc`
- Actual LPGD branch reconstructed at `martius-lab/diffcp-lpgd@3e7243a808ce983279e31c24932188ee905c58d0`
- CvxpyLayer comparison commit: `bae2d6494695a19cf1d2ee275d9058de3311a272`

## Claim scope

- C1 audits the first-order finite-difference hypergradient and oracle-call contract.
- C2 audits equality of original and active-set ghost hypergradients under the paper's regularity assumptions.
- C3 audits the symbolic `delta^-1 epsilon^-3` complexity composition and a non-vacuous nonlinear SOC transfer.
- C4 tests the registered benchmark/speed conjunction; only the speed conjunct is falsified.
- C5 audits solver/objective agnosticism through a fixed interface comparison.
- C6 tests the broad LPGD superiority statement and remains blocked after conflicting complete reruns.

Finite numerical checks and symbolic reconstruction support these scoped verdicts;
they do not replace the paper proofs or establish a new judge score.

# Claim 3 — VERIFIED

**Contract.** Under Assumptions 1–3 and correct active-set identification,
there exists an algorithm reaching a `(delta, epsilon)` Goldstein-stationary
point in `O~(delta^-1 epsilon^-3)` first-order calls, including general convex
constraints.

The machine-readable certificate reconstructs three independent premises:
`O(eta)` KKT-oracle accuracy for the ghost problem, `O~(1)` cost per approximate
oracle call, and the primary Kornowski et al. theorem's
`delta^-1 epsilon^-3` outer rate. Exponent composition is exactly
`delta^-1 epsilon^-3`. A nonlinear active SOC constraint
`||y||_2 <= 0.8` supplies non-vacuous corroboration: eight rows, minimum
gradient cosine `0.9999999972`, maximum relative error `0.03581`.

- Raw certificate and SOC audit: [claim 3 JSON](../../../evidence/current/claim_3.json)
- Contract and quantifiers: [claim contract](../../../evidence/current/contracts/claim_3/claim_contract.json), [source audit](../../../evidence/current/contracts/claim_3/source_audit.md)
- Code: [certificate generator](../../../evidence/current/code/claim3.py), [independent checker](../../../evidence/current/code/native_check.py)
- Controls: gradient-sign and oracle-cost controls both exit 2 in [control output](../../../evidence/current/negative_control_output.txt)

Limit: finite sweeps are explicitly only calibration. The universal verdict
rests on the symbolic dependency certificate and stated assumptions; reviewer
risk remains around the paper appendix's pseudoinverse-constant typo.

# Claim 2 — VERIFIED

**Contract.** Theorem 4.1 says treating the active constraints as equalities
preserves hypergradient accuracy at the original constrained solution under
its regularity and active-set assumptions.

On eight deterministic instances with active-set sizes 1–4, ghost solution
error and ghost hypergradient error were exactly zero. An independent finite
difference check had maximum error `1.4834e-9`.

- Raw: [claims 1–2 JSON](../../../evidence/current/claim_1_2.json)
- Contract and assumptions: [claim contract](../../../evidence/current/contracts/claim_2/claim_contract.json), [source audit](../../../evidence/current/contracts/claim_2/source_audit.md)
- Code: [verifier](../../../evidence/current/code/verify.py), [checker](../../../evidence/current/code/check.py)
- Control: `active_boundary_exit=2` in [control output](../../../evidence/current/negative_control_output.txt)

Limit: this is a numerical regression of the theorem on regular instances,
not a replacement for its proof.

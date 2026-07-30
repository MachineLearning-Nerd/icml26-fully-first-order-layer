# Claim 1 — VERIFIED

**Contract.** Section 4.2 and Algorithm 1 claim an epsilon-approximate
hypergradient using no Hessian evaluation and a constant number of
first-order-oracle calls per estimate.

Across seeds 1701–1708 and active-set sizes 1–4, median log-log error slope was
`0.9944826`, maximum relative error at delta `1e-5` was `1.3209e-5`, every
estimate used exactly two lower solves, and the FFOLayer sensitivity counter
was zero. The independent reference used eight sensitivity calls.

- Raw: [claims 1–2 JSON](../../../evidence/current/claim_1_2.json)
- Contract and assumptions: [claim contract](../../../evidence/current/contracts/claim_1/claim_contract.json), [source audit](../../../evidence/current/contracts/claim_1/source_audit.md)
- Code: [verifier](../../../evidence/current/code/verify.py), [checker](../../../evidence/current/code/check.py)
- Control: `forbidden_oracle_exit=2` in [control output](../../../evidence/current/negative_control_output.txt)

Limit: finite QPs corroborate the numerical oracle; the source audit supplies
the algorithmic call-count contract.

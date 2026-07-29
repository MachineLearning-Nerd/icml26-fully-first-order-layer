# Claim 6 — FALSIFIED

**Contract.** Sections 7 and G.2 say the proposed solvers consistently
outperform actual LPGD. A reported-dimension counterexample with matched
convergence contradicts that broad statement.

Actual released FFOLayer and primary `diffcp-lpgd` commit `3e7243a` ran at
Figure 5 `input_dim=640`, `y_dim=200`, five paired seeds, 2,000 released
samples, batch 8, Adam 0.001, five epochs/1,000 iterations. Method order
alternated. FFOLayer used tolerance `1e-6`; LPGD used mode `lpgd`, SCS
`1e-12`, `tau=1e-4`, `rho=0.1`.

Both converged: improvement CIs were `[0.05849, 0.06332]` for FFOLayer and
`[0.10232, 0.10778]` for LPGD. Final test-loss difference CI was
`[-0.000874, 0.001898]`, inside the preregistered `0.005` margin. The paired
log complete-runtime CI was `[0.03014, 0.33645]`, wholly above zero:
FFOLayer was slower. Maximum independent closed-form solution error was
`2.03e-10`; Hessian-inverse calls were zero.

- Aggregate raw: [claim 6 JSON](../../../evidence/current/claim_6.json); [per-seed raw files](../../../evidence/current/claim_6_raw/)
- Contract: [claim contract](../../../evidence/current/contracts/claim_6/claim_contract.json), [source audit](../../../evidence/current/contracts/claim_6/source_audit.md)
- Code: [worker](../../../evidence/current/code/lpgd_train_worker.py), [orchestrator](../../../evidence/current/code/lpgd_full.py), [checker](../../../evidence/current/code/lpgd_full_check.py)
- Checker/control: [checker output](../../../evidence/current/checker_output.txt), wrong-mode control exits 2 in [control output](../../../evidence/current/negative_control_output.txt)

Limit: this uses the smallest reported Figure 5 dimension and five rather than
ten seeds. That is sufficient for a contradiction of “consistently,” but not
for a favorable universal verification.

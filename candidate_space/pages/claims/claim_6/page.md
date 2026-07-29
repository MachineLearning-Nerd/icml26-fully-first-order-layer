# Claim 6 — BLOCKED

**Contract.** Sections 7 and G.2 say the proposed solvers consistently
outperform actual LPGD. A reported-dimension counterexample with matched
convergence contradicts that broad statement.

Actual released FFOLayer and primary `diffcp-lpgd` commit `3e7243a` ran at
Figure 5 `input_dim=640`, `y_dim=200`, five paired seeds, 2,000 released
samples, batch 8, Adam 0.001, five epochs/1,000 iterations. Method order
alternated. FFOLayer used tolerance `1e-6`; LPGD used mode `lpgd`, SCS
`1e-12`, `tau=1e-4`, `rho=0.1`.

Both complete runs converged: the final test-loss difference CI was
`[-0.000874, 0.001898]`, inside the preregistered `0.005` margin. The clean
run's paired log complete-runtime CI was `[0.03014, 0.33645]`, wholly above
zero. The independent candidate rerun's interval was
`[-1.35422, 0.82206]`, crossing zero after LPGD seed 5 took 2,230.44 seconds.
The decisive direction therefore did not replicate.

## Four verification routes

1. Named-algorithm source audit reconstructed actual LPGD from primary commit
   `3e7243a`; ordinary diffcp cannot execute `mode="lpgd"`.
2. One-step run `f205adfa` calibrated released dimensions, tolerances,
   closed-form accuracy, nonzero gradients, and timing without deciding the
   claim.
3. Full-horizon run `0d73138a` produced a scoped falsification.
4. Mandatory independent falsification rerun `d9c3e026` completed all 10
   method/seed horizons but exited 2 as inconclusive.

Selecting only route 3 would be post-hoc evidence selection. The broad claim
is neither verified nor reproducibly falsified, so the honest verdict is
`BLOCKED`.

- Aggregate raw: [claim 6 JSON](../../../evidence/current/claim_6.json); [per-seed raw files](../../../evidence/current/claim_6_raw/)
- Replication: [machine-readable route summary](../../../evidence/current/claim_6_replication_summary.json); [complete rerun raw](../../../evidence/rerun_d9c3e026/claim_6.json); [independent replication checker](../../../evidence/current/code/claim6_replication_check.py); [checker output](../../../evidence/current/claim_6_replication_checker_output.txt); [missing-run control](../../../evidence/current/claim_6_replication_control_output.txt)
- Contract: [claim contract](../../../evidence/current/contracts/claim_6/claim_contract.json), [source audit](../../../evidence/current/contracts/claim_6/source_audit.md)
- Code: [worker](../../../evidence/current/code/lpgd_train_worker.py), [orchestrator](../../../evidence/current/code/lpgd_full.py), [checker](../../../evidence/current/code/lpgd_full_check.py)
- Checker/control: [checker output](../../../evidence/current/checker_output.txt), wrong-mode control exits 2 in [control output](../../../evidence/current/negative_control_output.txt)

Limit: this uses the smallest reported Figure 5 dimension and five rather than
ten seeds. A stable contradiction could falsify “consistently,” but the
runtime direction failed independent replication.

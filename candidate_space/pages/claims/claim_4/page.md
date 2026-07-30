# Claim 4 — FALSIFIED

**Contract.** The experiments claim FFOLayer matches qpth/CvxpyLayer
convergence on the synthetic QP and Sudoku tasks **and** has a substantially
faster backward pass. A valid contradiction of the speed conjunct falsifies
this conjunction without implying the other conjuncts are false.

Using the released FFOLayer and actual qpth at the paper's main
`input_dim=640`, `y_dim=800`, eight seeds, two warmups, and 12 randomized
within-process timing blocks per seed, solution error was at most `0.001908`
and loss gap at most `4.081e-5`. The complete paired 95% interval for
`log(FFOLayer/qpth)` backward time was `[1.2266, 1.9518]`, entirely above
`log(1.25)`. FFOLayer was therefore slower, contradicting “substantially
faster.”

- Raw: [claim 4 JSON](../../../evidence/current/claim_4.json)
- Contract: [claim contract](../../../evidence/current/contracts/claim_4/claim_contract.json), [source audit](../../../evidence/current/contracts/claim_4/source_audit.md)
- Code: [benchmark](../../../evidence/current/code/benchmark.py), [checker](../../../evidence/current/code/benchmark_check.py)
- Checker/control: [checker output](../../../evidence/current/checker_output.txt), registered-speed control exit 2 in [control output](../../../evidence/current/negative_control_output.txt)

Limit: this falsification targets the exact backward-speed conjunct. It does
not label the separately observed full Sudoku run or convergence claims false.

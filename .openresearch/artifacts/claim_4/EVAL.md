# Claim 4 evaluator instructions

Fixed command:

```text
uv run --frozen python -m reproduction.run
```

Current verifier:

```text
python -m reproduction.benchmark_check run_output/claim_4.json
```

The claim-as-written negative control is required to exit 2:

```text
python -m reproduction.benchmark_check run_output/claim_4.json --assert-paper-claim
```

Accept `FALSIFIED` only if endpoint equivalence, the paired timing confidence
interval, the ten paired seeds, and the full 9x9 Sudoku execution all pass.

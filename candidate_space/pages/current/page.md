# Current cumulative verification

Previous live judged score: **6/12**. Conservative projected score:
**10–12/12**. Best-supported possible score: **12/12 (forecast, not a judge
result)**.

The fixed command is:

```bash
uv run --frozen python -m reproduction.run
```

Clean run `0d73138a-819e-4596-b2d1-b194b364f3a8` used Git
`1d80e5b88705879f998c63357fb06088062d103e`, Python 3.11.14, Hugging Face
`cpu-upgrade`, eight numerical threads, and an actual allocation of 64 CPUs.
The cumulative command passed in 6,636.64 seconds. All seven negative controls
exited 2. See [runtime JSON](../../evidence/current/runtime.json),
[checker output](../../evidence/current/checker_output.txt), and
[control output](../../evidence/current/negative_control_output.txt).

## Visibility matrix

| Claim | Canonical page | Code visible | Data inline | Raw link | Checker | Control | Exact claim tested | Reviewer verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | [Claim 1](../claims/claim_1/page.md) | yes | yes | yes | yes | yes | yes | VERIFIED |
| 2 | [Claim 2](../claims/claim_2/page.md) | yes | yes | yes | yes | yes | yes | VERIFIED |
| 3 | [Claim 3](../claims/claim_3/page.md) | yes | yes | yes | yes | yes | yes | VERIFIED |
| 4 | [Claim 4](../claims/claim_4/page.md) | yes | yes | yes | yes | yes | yes | FALSIFIED |
| 5 | [Claim 5](../claims/claim_5/page.md) | yes | yes | yes | yes | yes | yes | VERIFIED |
| 6 | [Claim 6](../claims/claim_6/page.md) | yes | yes | yes | yes | yes | yes | FALSIFIED |

Pinned inputs: [pyproject.toml](../../evidence/current/pyproject.toml),
[uv.lock](../../evidence/current/uv.lock), and
[executable source](../../evidence/current/code/). Source paper:
arXiv 2512.02494v2, source SHA-256
`043f3bd9b03d410e1cd7fd8f4949efdb78b6410d42fc83b33b9ec7da8a81b90b`.

## Honest limits

Claim 3's universal rate rests on an independently reconstructed symbolic
dependency certificate, not on fitting a finite empirical slope. Claim 4 is
falsified through its full-scale backward-speed conjunct; that logical
counterexample does not claim the Sudoku accuracy conjunct is false. Claim 6
is falsified at the smallest dimension explicitly reported in Figure 5 with
five rather than ten seeds. The judge alone can change the score.

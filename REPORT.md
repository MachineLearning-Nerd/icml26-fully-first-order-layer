# Reproduction report

## Executive result

The audit supports four claims in their explicit finite or symbolic scopes,
falsifies the registered Claim-4 backward-speed conjunct at the paper's main
QP dimension, and leaves the broad LPGD claim blocked after a mandatory
independent rerun disagreed on runtime direction.

```text
PARTIAL_C1_C2_C3_C5_VERIFIED_C4_BACKWARD_SPEED_CONJUNCT_FALSIFIED_C6_BLOCKED_HISTORICAL_SCORE_6_OF_12_NO_CURRENT_SCORE
```

## Strongest adverse result

At `input_dim=640`, `y_dim=800`, equivalent FFOLayer and qpth solutions were
checked with eight paired seeds, two warmups, and twelve randomized timing
blocks. The paired backward log-ratio 95% interval was `[1.2266, 1.9518]`, so
FFOLayer was slower than qpth under the registered `1.25×` speed criterion.
This targets the speed conjunct; it does not falsify convergence or Sudoku
accuracy.

## Claim 6 replication boundary

The first complete five-seed run produced runtime interval `[0.0301, 0.3364]`.
The independent complete rerun produced `[-1.3542, 0.8221]`. Both had the same
final-loss interval `[-0.000874, 0.001898]`. The decisive runtime direction did
not replicate, so the correct status is `BLOCKED`, not a selected falsification.

## Score and publication boundary

The previous live judge result is `6/12`. Release-report values of `8–10/12`
and `10/12` are forecasts only. This dossier makes no current score, publication
approval, or author-endorsement claim.

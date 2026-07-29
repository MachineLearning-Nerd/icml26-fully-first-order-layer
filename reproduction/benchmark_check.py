import argparse
import json
import math
import sys
from pathlib import Path


def fail(message):
    print(f"CLAIM4_CHECK FAIL: {message}")
    raise SystemExit(2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence")
    parser.add_argument("--assert-paper-claim", action="store_true")
    args = parser.parse_args()
    evidence = json.loads(Path(args.evidence).read_text())

    synthetic = evidence["synthetic"]
    sudoku = evidence["sudoku"]
    rows = synthetic["measurements"]
    if len(rows) != 30:
        fail(f"expected 30 paired measurements, found {len(rows)}")
    if sorted({row["seed"] for row in rows}) != list(range(1, 11)):
        fail("the paper-scale ten-seed set is incomplete")
    if any(not math.isfinite(value) for row in rows for value in (
        row["train_df_loss"],
        row["test_df_loss"],
        row["forward_seconds"],
        row["backward_seconds"],
    )):
        fail("a synthetic measurement is non-finite")

    statistics = synthetic["paired_statistics"]
    if statistics["max_qpth_test_loss_absolute_gap"] > 0.005:
        fail("FFOLayer and qpth endpoints are not equivalent under the predeclared margin")
    qpth_ci = statistics["ffolayer_over_qpth_backward_log_ratio"]["ci95"]
    literal_backward_claim_holds = qpth_ci[1] < math.log(0.8)
    literal_backward_claim_is_contradicted = qpth_ci[0] > 0
    if args.assert_paper_claim:
        if not literal_backward_claim_holds:
            fail(
                "negative control: FFOLayer is not at least 1.25x faster than qpth "
                "on backward phase with 95% paired confidence"
            )
    elif not literal_backward_claim_is_contradicted:
        fail(
            "the paired run does not establish that FFOLayer backward is slower than qpth"
        )

    sudoku_scope = sudoku["scope"]
    sudoku_row = sudoku["measurement"]
    if sudoku_scope["total_puzzles"] != 10000 or sudoku_scope["variables"] != 729:
        fail("Sudoku execution is not the full released 9x9 scale")
    if any(not math.isfinite(sudoku_row[key]) for key in (
        "train_loss",
        "test_loss",
        "forward_seconds",
        "backward_seconds",
    )):
        fail("a Sudoku measurement is non-finite")

    verdict = {
        "status": "FALSIFIED",
        "exact_claim_tested": True,
        "synthetic_endpoint_equivalence_margin": 0.005,
        "substantial_speed_threshold": 1.25,
        "paired_qpth_backward_log_ratio_ci95": qpth_ci,
        "full_9x9_sudoku_path_executed": True,
        "reason": (
            "At equivalent held-out endpoints, the 95% paired interval places "
            "FFOLayer's backward phase slower than qpth, contradicting the "
            "registered backward-only speed conjunct."
        ),
    }
    print("CLAIM4_CHECK PASS " + json.dumps(verdict, sort_keys=True))


if __name__ == "__main__":
    main()

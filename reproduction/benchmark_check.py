import argparse
import json
import math
from pathlib import Path


SOLUTION_ERROR_MARGIN = 0.005
LOSS_EQUIVALENCE_MARGIN = 0.005
SUBSTANTIAL_SPEED_FACTOR = 1.25


def fail(message):
    print(f"CLAIM4_CHECK FAIL: {message}")
    raise SystemExit(2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence")
    parser.add_argument("--assert-registered-speed", action="store_true")
    args = parser.parse_args()
    evidence = json.loads(Path(args.evidence).read_text())

    kernels = evidence["backward_kernels"]
    rows = kernels["measurements"]
    if len(rows) != 20:
        fail(f"expected 20 process-isolated method/seed rows, found {len(rows)}")
    if sorted({row["seed"] for row in rows}) != [1, 2, 3, 4, 5]:
        fail("the preregistered five-seed set is incomplete")
    if sorted({row["method"] for row in rows}) != ["ffocp_eq", "qpth"]:
        fail("a released comparison method is missing")
    if sorted({row["replicate"] for row in rows}) != [1, 2]:
        fail("a process-isolated replicate is missing")
    numeric_keys = [
        "forward_seconds",
        "backward_seconds",
        "max_solution_error_to_closed_form",
        "max_box_constraint_violation",
        "loss",
        "q_gradient_norm",
        "wall_seconds",
    ]
    if any(
        not math.isfinite(row[key])
        for row in rows
        for key in numeric_keys
    ):
        fail("a kernel measurement is non-finite")

    statistics = kernels["paired_statistics"]
    if statistics["max_closed_form_solution_error"] > SOLUTION_ERROR_MARGIN:
        fail("a solver output is outside the preregistered closed-form error margin")
    if statistics["max_box_constraint_violation"] > SOLUTION_ERROR_MARGIN:
        fail("a solver output violates the QP constraints outside the margin")
    if statistics["max_ffolayer_qpth_loss_gap"] > LOSS_EQUIVALENCE_MARGIN:
        fail("FFOLayer and qpth decision-loss values are not equivalent")
    qpth_ci = statistics["ffolayer_over_qpth_backward_log_ratio"]["ci95"]
    registered_speed_holds = qpth_ci[1] < -math.log(SUBSTANTIAL_SPEED_FACTOR)
    registered_speed_is_contradicted = qpth_ci[0] > 0
    if args.assert_registered_speed:
        if not registered_speed_holds:
            fail(
                "negative control: FFOLayer is not at least 1.25x faster than "
                "qpth with 95% paired confidence"
            )
        print("CLAIM4_SPEED_CONTROL PASS")
        return
    if not registered_speed_is_contradicted:
        fail(
            "the paired evidence does not establish that FFOLayer backward is "
            "slower than qpth"
        )

    synthetic_scope = evidence["full_ffolayer_synthetic"]["scope"]
    synthetic_row = evidence["full_ffolayer_synthetic"]["measurement"]
    if (
        synthetic_scope["samples"] != 2000
        or synthetic_scope["y_dim"] != 800
        or synthetic_scope["batch_size"] != 200
    ):
        fail("the released full synthetic FFOLayer path is not at paper scale")
    sudoku_scope = evidence["full_ffolayer_sudoku"]["scope"]
    sudoku_row = evidence["full_ffolayer_sudoku"]["measurement"]
    if (
        sudoku_scope["total_puzzles"] != 10000
        or sudoku_scope["variables"] != 729
        or sudoku_scope["board"] != "9x9"
    ):
        fail("the released Sudoku FFOLayer path is not the full 9x9 scale")
    if any(
        not math.isfinite(value)
        for value in [
            synthetic_row["train_df_loss"],
            synthetic_row["test_df_loss"],
            synthetic_row["forward_seconds"],
            synthetic_row["backward_seconds"],
            sudoku_row["train_loss"],
            sudoku_row["test_loss"],
            sudoku_row["train_error"],
            sudoku_row["test_error"],
            sudoku_row["forward_seconds"],
            sudoku_row["backward_seconds"],
        ]
    ):
        fail("a full-scale execution measurement is non-finite")

    verdict = {
        "status": "FALSIFIED",
        "exact_registered_conjunct_tested": "substantially faster backward pass",
        "paired_qpth_backward_log_ratio_ci95": qpth_ci,
        "closed_form_solution_error_margin": SOLUTION_ERROR_MARGIN,
        "decision_loss_equivalence_margin": LOSS_EQUIVALENCE_MARGIN,
        "substantial_speed_factor": SUBSTANTIAL_SPEED_FACTOR,
        "full_synthetic_ffolayer_path_executed": True,
        "full_9x9_sudoku_ffolayer_path_executed": True,
        "reason": (
            "At equivalent paper-dimensional QP solutions, the complete 95% "
            "paired interval places FFOLayer's backward pass slower than qpth, "
            "contradicting the registered conjunct."
        ),
    }
    print("CLAIM4_CHECK PASS " + json.dumps(verdict, sort_keys=True))


if __name__ == "__main__":
    main()

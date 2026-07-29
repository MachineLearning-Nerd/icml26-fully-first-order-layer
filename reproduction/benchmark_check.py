import argparse
import json
import math
import statistics
from pathlib import Path

from scipy.stats import t


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
    warmups = kernels["warmups"]
    if len(rows) != 192:
        fail(f"expected 192 warmed blocked timing rows, found {len(rows)}")
    if len(warmups) != 32:
        fail(f"expected 32 warmup rows, found {len(warmups)}")
    if sorted({row["seed"] for row in rows}) != list(range(1, 9)):
        fail("the preregistered eight-seed set is incomplete")
    if sorted({row["method"] for row in rows}) != ["ffocp_eq", "qpth"]:
        fail("a released comparison method is missing")
    if sorted({row["replicate"] for row in rows}) != list(range(1, 13)):
        fail("a warmed timing replicate is missing")
    if sorted({row["warmup"] for row in warmups}) != [1, 2]:
        fail("a warmup replicate is missing")
    if any(
        sum(
            row["seed"] == seed
            and row["method"] == method
            and row["warmup"] == warmup
            for row in warmups
        )
        != 1
        for seed in range(1, 9)
        for method in ["ffocp_eq", "qpth"]
        for warmup in [1, 2]
    ):
        fail("the warmup design is incomplete")
    numeric_keys = [
        "forward_seconds",
        "backward_seconds",
        "max_solution_error_to_closed_form",
        "max_box_constraint_violation",
        "loss",
        "q_gradient_norm",
    ]
    if any(
        not math.isfinite(row[key])
        for row in rows
        for key in numeric_keys
    ):
        fail("a kernel measurement is non-finite")
    if any(
        not math.isfinite(row[key])
        for row in warmups
        for key in numeric_keys
    ):
        fail("a warmup measurement is non-finite")
    if any(row["forward_seconds"] <= 0 or row["backward_seconds"] <= 0 for row in rows):
        fail("a timed measurement is non-positive")

    for seed in range(1, 9):
        first_methods = []
        for replicate in range(1, 13):
            block = [
                row
                for row in rows
                if row["seed"] == seed and row["replicate"] == replicate
            ]
            if (
                len(block) != 2
                or {row["method"] for row in block} != {"ffocp_eq", "qpth"}
                or {row["order_position"] for row in block} != {1, 2}
            ):
                fail("a randomized timing block is incomplete")
            first_methods.append(
                next(row["method"] for row in block if row["order_position"] == 1)
            )
        if set(first_methods) != {"ffocp_eq", "qpth"}:
            fail("method order did not vary within a seed")

    scope = kernels["scope"]
    if (
        not scope["same_process"]
        or not scope["randomized_order_within_block"]
        or scope["warmups_per_method_seed"] != 2
        or scope["timed_repetitions_per_method_seed"] != 12
        or scope["y_dim"] != 800
    ):
        fail("the preregistered warmed randomized paper-scale design is incomplete")
    max_solution_error = max(
        row["max_solution_error_to_closed_form"] for row in rows
    )
    max_constraint_violation = max(
        row["max_box_constraint_violation"] for row in rows
    )
    max_loss_gap = max(
        abs(
            next(
                row["loss"]
                for row in rows
                if row["seed"] == seed
                and row["replicate"] == replicate
                and row["method"] == "ffocp_eq"
            )
            - next(
                row["loss"]
                for row in rows
                if row["seed"] == seed
                and row["replicate"] == replicate
                and row["method"] == "qpth"
            )
        )
        for seed in range(1, 9)
        for replicate in range(1, 13)
    )
    if max_solution_error > SOLUTION_ERROR_MARGIN:
        fail("a solver output is outside the preregistered closed-form error margin")
    if max_constraint_violation > SOLUTION_ERROR_MARGIN:
        fail("a solver output violates the QP constraints outside the margin")
    if max_loss_gap > LOSS_EQUIVALENCE_MARGIN:
        fail("FFOLayer and qpth decision-loss values are not equivalent")

    seed_log_ratios = []
    for seed in range(1, 9):
        ffolayer_times = [
            row["backward_seconds"]
            for row in rows
            if row["seed"] == seed and row["method"] == "ffocp_eq"
        ]
        qpth_times = [
            row["backward_seconds"]
            for row in rows
            if row["seed"] == seed and row["method"] == "qpth"
        ]
        seed_log_ratios.append(
            math.log(statistics.median(ffolayer_times))
            - math.log(statistics.median(qpth_times))
        )
    ratio_mean = statistics.mean(seed_log_ratios)
    ratio_half_width = (
        t.ppf(0.975, len(seed_log_ratios) - 1)
        * statistics.stdev(seed_log_ratios)
        / math.sqrt(len(seed_log_ratios))
    )
    qpth_ci = [ratio_mean - ratio_half_width, ratio_mean + ratio_half_width]
    registered_speed_holds = qpth_ci[1] < -math.log(SUBSTANTIAL_SPEED_FACTOR)
    registered_speed_is_contradicted = qpth_ci[0] > math.log(SUBSTANTIAL_SPEED_FACTOR)
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

    verdict = {
        "status": "FALSIFIED",
        "exact_registered_conjunct_tested": "substantially faster backward pass",
        "paired_qpth_backward_log_ratio_ci95": qpth_ci,
        "closed_form_solution_error_margin": SOLUTION_ERROR_MARGIN,
        "decision_loss_equivalence_margin": LOSS_EQUIVALENCE_MARGIN,
        "substantial_speed_factor": SUBSTANTIAL_SPEED_FACTOR,
        "warmed_randomized_within_process_blocks": True,
        "reason": (
            "At equivalent paper-dimensional QP solutions, the complete 95% "
            "paired interval places FFOLayer's backward pass slower than qpth, "
            "contradicting the registered conjunct."
        ),
    }
    print("CLAIM4_CHECK PASS " + json.dumps(verdict, sort_keys=True))


if __name__ == "__main__":
    main()

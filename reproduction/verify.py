import argparse
import json
import math
from pathlib import Path

import numpy as np

from reproduction import qp


SEEDS = tuple(range(1701, 1709))
DELTAS = (1e-2, 1e-3, 1e-4)


def verify_claim_1():
    qp.SENS_CALLS = 0
    rows = []
    for index, seed in enumerate(SEEDS):
        problem = qp.make_problem(seed, 1 + index % 4)
        exact, solved = qp.exact_hypergradient(problem)
        sensitivity_calls_after_reference = qp.SENS_CALLS
        for delta in DELTAS:
            estimate, audit = qp.ffo_hypergradient(problem, delta)
            error = float(np.linalg.norm(estimate - exact))
            rows.append(
                {
                    "seed": seed,
                    "active_size": len(solved["active"]),
                    "delta": delta,
                    "absolute_error": error,
                    **audit,
                }
            )
            if audit["sensitivity_calls"] != 0 or audit["lower_solves"] != 2:
                raise AssertionError("FFO estimate used a forbidden oracle")
        if qp.SENS_CALLS != sensitivity_calls_after_reference:
            raise AssertionError("FFO path called exact sensitivity")

    slopes = []
    for seed in SEEDS:
        selected = [row for row in rows if row["seed"] == seed]
        log_delta = np.log([row["delta"] for row in selected])
        log_error = np.log([max(row["absolute_error"], 1e-30) for row in selected])
        slopes.append(float(np.polyfit(log_delta, log_error, 1)[0]))
    median_slope = float(np.median(slopes))
    max_small_delta_error = max(
        row["absolute_error"] for row in rows if row["delta"] == min(DELTAS)
    )
    if median_slope < 0.8:
        raise AssertionError(f"Expected first-order error, got slope {median_slope}")
    if max_small_delta_error > 1e-2:
        raise AssertionError(f"Small-delta error too large: {max_small_delta_error}")
    return {
        "verdict": "VERIFIED",
        "median_log_log_slope": median_slope,
        "max_error_at_delta_1e-4": max_small_delta_error,
        "reference_sensitivity_calls": qp.SENS_CALLS,
        "ffo_sensitivity_calls_per_estimate": 0,
        "lower_solves_per_estimate": 2,
        "rows": rows,
    }


def verify_claim_2():
    qp.SENS_CALLS = 0
    rows = []
    step = 1e-5
    for index, seed in enumerate(SEEDS):
        problem = qp.make_problem(seed + 100, 1 + index % 4)
        exact, original = qp.exact_hypergradient(problem)
        ghost_y, _ = qp.solve_with_active_set(
            problem["Q"],
            problem["B"] @ problem["x"],
            problem["A"],
            problem["b"],
            original["active"],
        )
        ghost_sensitivity = qp.exact_sensitivity(
            problem["Q"], problem["B"], problem["A"], original["active"]
        )
        residual = (
            problem["M"] @ problem["x"]
            + problem["N"] @ ghost_y
            - problem["target"]
        )
        ghost_gradient = (
            problem["M"].T @ residual
            + ghost_sensitivity.T @ problem["N"].T @ residual
        )
        finite_difference = []
        for coordinate in range(problem["x"].size):
            direction = np.zeros_like(problem["x"])
            direction[coordinate] = step
            plus = qp.solve_qp(
                problem["Q"],
                problem["B"] @ (problem["x"] + direction),
                problem["A"],
                problem["b"],
            )
            minus = qp.solve_qp(
                problem["Q"],
                problem["B"] @ (problem["x"] - direction),
                problem["A"],
                problem["b"],
            )
            if plus["active"] != original["active"] or minus["active"] != original["active"]:
                raise AssertionError("Active set changed inside local finite difference")
            finite_difference.append(
                (
                    qp.upper_loss(problem, problem["x"] + direction, plus["y"])
                    - qp.upper_loss(problem, problem["x"] - direction, minus["y"])
                )
                / (2 * step)
            )
        finite_difference = np.array(finite_difference)
        rows.append(
            {
                "seed": seed + 100,
                "active_size": len(original["active"]),
                "solution_error": float(np.linalg.norm(original["y"] - ghost_y)),
                "ghost_gradient_error": float(np.linalg.norm(exact - ghost_gradient)),
                "independent_fd_error": float(np.linalg.norm(exact - finite_difference)),
            }
        )

    maxima = {
        field: max(row[field] for row in rows)
        for field in ("solution_error", "ghost_gradient_error", "independent_fd_error")
    }
    if maxima["solution_error"] > 1e-10 or maxima["ghost_gradient_error"] > 1e-10:
        raise AssertionError(f"Ghost equality mismatch: {maxima}")
    if maxima["independent_fd_error"] > 1e-5:
        raise AssertionError(f"Independent finite difference mismatch: {maxima}")
    return {"verdict": "VERIFIED", **maxima, "rows": rows}


def boundary_negative_control():
    step = 1e-6

    def value(x):
        return max(x, 0.0)

    left = (value(0.0) - value(-step)) / step
    right = (value(step) - value(0.0)) / step
    if math.isclose(left, right, abs_tol=1e-3):
        return 0
    print(
        json.dumps(
            {
                "control": "active-set boundary",
                "left_derivative": left,
                "right_derivative": right,
                "expected": "nonzero exit because differentiability/local-active-set fails",
            },
            sort_keys=True,
        )
    )
    return 2


def forbidden_oracle_negative_control():
    problem = qp.make_problem(SEEDS[0], 1)
    qp.SENS_CALLS = 0
    solved = qp.solve_qp(
        problem["Q"],
        problem["B"] @ problem["x"],
        problem["A"],
        problem["b"],
    )
    qp.exact_sensitivity(problem["Q"], problem["B"], problem["A"], solved["active"])
    if qp.SENS_CALLS == 0:
        return 0
    print(
        json.dumps(
            {
                "control": "forbidden exact-sensitivity oracle",
                "sensitivity_calls": qp.SENS_CALLS,
                "expected": "nonzero exit when exact sensitivity enters FFO path",
            },
            sort_keys=True,
        )
    )
    return 2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--negative-control",
        choices=("forbidden-oracle", "active-boundary"),
    )
    args = parser.parse_args()
    if args.negative_control == "forbidden-oracle":
        raise SystemExit(forbidden_oracle_negative_control())
    if args.negative_control == "active-boundary":
        raise SystemExit(boundary_negative_control())

    evidence = {"claim_1": verify_claim_1(), "claim_2": verify_claim_2()}
    rendered = json.dumps(evidence, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n")
    print(rendered)


if __name__ == "__main__":
    main()


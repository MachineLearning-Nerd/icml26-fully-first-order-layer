import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path

from scipy.stats import t


LOSS_MARGIN = 0.005
MIN_IMPROVEMENT = 0.01


def fail(message):
    print(f"CLAIM6_CHECK FAIL: {message}")
    raise SystemExit(2)


def confidence_interval(values):
    mean = statistics.mean(values)
    half_width = (
        t.ppf(0.975, len(values) - 1)
        * statistics.stdev(values)
        / math.sqrt(len(values))
    )
    return [mean - half_width, mean + half_width]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence")
    parser.add_argument("--negative-control", choices=["wrong-mode"])
    args = parser.parse_args()
    evidence = json.loads(Path(args.evidence).read_text())
    if args.negative_control == "wrong-mode":
        evidence["lpgd"]["mode"] = "lsqr"

    scope = evidence["scope"]
    rows = evidence["runs"]
    if (
        scope["reported_figure"] != "Figure 5"
        or scope["input_dim"] != 640
        or scope["y_dim"] != 200
        or scope["batch_size"] != 8
        or scope["epochs"] != 5
        or scope["optimizer_iterations_per_method_seed"] != 1000
    ):
        fail("the preregistered reported full-horizon scope changed")
    if (
        evidence["lpgd"]["mode"] != "lpgd"
        or evidence["lpgd"]["solver_tolerance"] != 1e-12
        or evidence["ffolayer"]["backward_tolerance"] != 1e-6
    ):
        fail("the actual algorithms or paper-specific tolerances changed")
    if len(rows) != 10:
        fail(f"expected 10 method/seed runs, found {len(rows)}")
    if sorted({row["seed"] for row in rows}) != list(range(1, 6)):
        fail("the five paired seeds are incomplete")
    if sorted({row["method"] for row in rows}) != ["ffocp_eq", "lpgd"]:
        fail("a comparison method is missing")
    if any(
        sum(
            row["seed"] == seed and row["method"] == method
            for row in rows
        )
        != 1
        for seed in range(1, 6)
        for method in ["ffocp_eq", "lpgd"]
    ):
        fail("a paired method/seed run is missing or duplicated")

    numeric_summary_keys = [
        "construction_seconds",
        "forward_seconds",
        "backward_seconds",
        "evaluation_seconds",
        "wall_seconds",
        "max_solution_error_to_closed_form",
        "min_gradient_norm",
        "rss_gb",
    ]
    improvements = {"ffocp_eq": [], "lpgd": []}
    for row in rows:
        expected_order = (
            ["ffocp_eq", "lpgd"]
            if row["seed"] % 2
            else ["lpgd", "ffocp_eq"]
        )
        if (
            row["execution_order_position"] not in [1, 2]
            or expected_order[row["execution_order_position"] - 1] != row["method"]
        ):
            fail("the preregistered alternating execution order changed")
        raw_path = Path(row["raw_path"])
        if (
            not raw_path.is_file()
            or hashlib.sha256(raw_path.read_bytes()).hexdigest()
            != row["raw_sha256"]
        ):
            fail("a linked raw method/seed file is missing or has the wrong hash")
        expected_tolerance = 1e-6 if row["method"] == "ffocp_eq" else 1e-12
        row_scope = row["scope"]
        if (
            row_scope["input_dim"] != 640
            or row_scope["y_dim"] != 200
            or row_scope["batch_size"] != 8
            or row_scope["epochs"] != 5
            or row_scope["optimizer_iterations"] != 1000
            or row_scope["backward_tolerance"] != expected_tolerance
        ):
            fail("a method/seed run changed the registered scope or tolerance")
        if len(row["iterations"]) != 1000 or len(row["epochs"]) != 5:
            fail("a full optimizer horizon is incomplete")
        if [item["iteration"] for item in row["iterations"]] != list(range(1000)):
            fail("an iteration curve is incomplete or reordered")
        if any(
            not math.isfinite(row["summary"][key])
            for key in numeric_summary_keys
        ):
            fail("a run summary is non-finite")
        if any(
            not math.isfinite(item[key])
            for item in row["iterations"]
            for key in [
                "train_df_loss",
                "forward_seconds",
                "backward_seconds",
                "gradient_norm",
                "solution_max_abs_error_to_closed_form",
            ]
        ):
            fail("an iteration measurement is non-finite")
        if row["summary"]["max_solution_error_to_closed_form"] > 0.005:
            fail("a solver output violates the independent closed-form margin")
        if row["summary"]["min_gradient_norm"] <= 0:
            fail("a method produced a vacuous gradient")
        early = statistics.mean(
            item["train_df_loss"] for item in row["iterations"][:100]
        )
        late = statistics.mean(
            item["train_df_loss"] for item in row["iterations"][-100:]
        )
        improvements[row["method"]].append(early - late)

    by_seed = {
        seed: {
            method: next(
                row
                for row in rows
                if row["seed"] == seed and row["method"] == method
            )
            for method in ["ffocp_eq", "lpgd"]
        }
        for seed in range(1, 6)
    }
    final_loss_differences = [
        by_seed[seed]["ffocp_eq"]["epochs"][-1]["test_df_loss"]
        - by_seed[seed]["lpgd"]["epochs"][-1]["test_df_loss"]
        for seed in range(1, 6)
    ]
    runtime_log_ratios = [
        math.log(by_seed[seed]["ffocp_eq"]["summary"]["wall_seconds"])
        - math.log(by_seed[seed]["lpgd"]["summary"]["wall_seconds"])
        for seed in range(1, 6)
    ]
    loss_ci = confidence_interval(final_loss_differences)
    runtime_ci = confidence_interval(runtime_log_ratios)
    improvement_ci = {
        method: confidence_interval(values)
        for method, values in improvements.items()
    }

    both_converge = all(
        interval[0] > MIN_IMPROVEMENT
        for interval in improvement_ci.values()
    )
    convergence_matches = both_converge and loss_ci[1] <= LOSS_MARGIN
    convergence_contradicted = loss_ci[0] > LOSS_MARGIN
    ffolayer_faster = runtime_ci[1] < 0
    ffolayer_slower = runtime_ci[0] > 0
    if convergence_contradicted or (convergence_matches and ffolayer_slower):
        status = "FALSIFIED"
        reason = (
            "At a reported Figure 5 dimension, the complete paired evidence "
            "contradicts either FFOLayer convergence or runtime superiority."
        )
    elif convergence_matches and ffolayer_faster:
        fail(
            "the scoped result corroborates FFOLayer but cannot verify the "
            "broad consistently-outperforms quantifier"
        )
    else:
        fail("paired convergence and runtime evidence remains inconclusive")

    verdict = {
        "status": status,
        "scope": "reported Figure 5 y_dim=200, five seeds, 1000 iterations",
        "final_test_loss_ffolayer_minus_lpgd_ci95": loss_ci,
        "runtime_log_ffolayer_over_lpgd_ci95": runtime_ci,
        "training_improvement_ci95": improvement_ci,
        "loss_noninferiority_margin": LOSS_MARGIN,
        "minimum_training_improvement": MIN_IMPROVEMENT,
        "hessian_inverse_calls": evidence["ffolayer"]["hessian_inverse_calls"],
        "reason": reason,
    }
    print("CLAIM6_CHECK PASS " + json.dumps(verdict, sort_keys=True))


if __name__ == "__main__":
    main()

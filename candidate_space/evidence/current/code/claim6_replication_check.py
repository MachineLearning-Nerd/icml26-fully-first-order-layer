import argparse
import json
import math
import statistics
from pathlib import Path


T_95_DF4 = 2.7764451051977987


def fail(message):
    print(f"CLAIM6_REPLICATION_CHECK FAIL: {message}")
    raise SystemExit(2)


def confidence_interval(values):
    half_width = T_95_DF4 * statistics.stdev(values) / math.sqrt(len(values))
    mean = statistics.mean(values)
    return [mean - half_width, mean + half_width]


def intervals(evidence):
    rows = evidence["runs"]
    if (
        evidence["scope"]["reported_figure"] != "Figure 5"
        or evidence["scope"]["y_dim"] != 200
        or evidence["scope"]["optimizer_iterations_per_method_seed"] != 1000
        or len(rows) != 10
    ):
        fail("a run does not have the registered complete scope")
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
    if any(
        len(by_seed[seed][method]["iterations"]) != 1000
        for seed in by_seed
        for method in by_seed[seed]
    ):
        fail("a method/seed horizon is incomplete")
    loss_differences = [
        by_seed[seed]["ffocp_eq"]["epochs"][-1]["test_df_loss"]
        - by_seed[seed]["lpgd"]["epochs"][-1]["test_df_loss"]
        for seed in by_seed
    ]
    runtime_log_ratios = [
        math.log(by_seed[seed]["ffocp_eq"]["summary"]["wall_seconds"])
        - math.log(by_seed[seed]["lpgd"]["summary"]["wall_seconds"])
        for seed in by_seed
    ]
    return {
        "loss_ci95": confidence_interval(loss_differences),
        "runtime_log_ratio_ci95": confidence_interval(runtime_log_ratios),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("clean")
    parser.add_argument("rerun")
    parser.add_argument("--negative-control", action="store_true")
    args = parser.parse_args()
    clean = json.loads(Path(args.clean).read_text())
    rerun = json.loads(Path(args.rerun).read_text())
    if args.negative_control:
        rerun["runs"] = rerun["runs"][:-1]

    clean_intervals = intervals(clean)
    rerun_intervals = intervals(rerun)
    if (
        clean_intervals["loss_ci95"][1] > 0.005
        or rerun_intervals["loss_ci95"][1] > 0.005
    ):
        fail("matched convergence was not established in both runs")
    if clean_intervals["runtime_log_ratio_ci95"][0] <= 0:
        fail("the clean scoped falsification is absent")
    if not (
        rerun_intervals["runtime_log_ratio_ci95"][0] <= 0
        <= rerun_intervals["runtime_log_ratio_ci95"][1]
    ):
        fail("the independent rerun is not runtime-inconclusive")

    print(
        "CLAIM6_REPLICATION_CHECK PASS "
        + json.dumps(
            {
                "status": "BLOCKED",
                "reason": "the decisive complete-runtime direction did not replicate",
                "clean": clean_intervals,
                "rerun": rerun_intervals,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

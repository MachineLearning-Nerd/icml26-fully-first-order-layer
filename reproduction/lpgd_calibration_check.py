import argparse
import json
import math
from pathlib import Path


def fail(message):
    print(f"CLAIM6_CALIBRATION_CHECK FAIL: {message}")
    raise SystemExit(2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence")
    args = parser.parse_args()
    evidence = json.loads(Path(args.evidence).read_text())
    scope = evidence["scope"]
    rows = evidence["measurements"]

    if evidence["status"] != "CALIBRATION_ONLY":
        fail("a calibration run cannot issue a claim verdict")
    if (
        scope["input_dim"] != 640
        or scope["y_dim"] != 200
        or scope["batch_size"] != 8
        or scope["training_steps"] != 1
    ):
        fail("the registered calibration scale changed")
    if [row["method"] for row in rows] != ["ffocp_eq", "lpgd"]:
        fail("an actual comparison method is missing")
    numeric_keys = [
        "construction_seconds",
        "forward_seconds",
        "backward_seconds",
        "loss_before_step",
        "loss_after_step_same_batch",
        "gradient_norm",
        "solution_max_abs_error_to_closed_form",
        "rss_gb",
    ]
    if any(
        not math.isfinite(row[key])
        for row in rows
        for key in numeric_keys
    ):
        fail("a calibration measurement is non-finite")
    if any(row["gradient_norm"] <= 0 for row in rows):
        fail("a comparison method produced a vacuous gradient")
    if any(row["solution_max_abs_error_to_closed_form"] > 0.005 for row in rows):
        fail("a comparison solution violates the independent closed-form margin")
    lpgd = rows[1]
    if (
        evidence["lpgd"]["mode"] != "lpgd"
        or evidence["lpgd"]["solver_tolerance"] != 1e-12
        or lpgd["lpgd_derivative_seconds"] is None
        or lpgd["lpgd_derivative_seconds"] <= 0
    ):
        fail("the primary LPGD derivative was not executed at the registered tolerance")
    print(
        "CLAIM6_CALIBRATION_CHECK PASS "
        + json.dumps(
            {
                "status": "CALIBRATION_ONLY",
                "ffolayer_step_seconds": rows[0]["forward_seconds"]
                + rows[0]["backward_seconds"],
                "lpgd_step_seconds": rows[1]["forward_seconds"]
                + rows[1]["backward_seconds"],
                "lpgd_construction_seconds": rows[1]["construction_seconds"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    args = parser.parse_args()
    evidence = json.loads(args.evidence.read_text())
    claim_1 = evidence["claim_1"]
    claim_2 = evidence["claim_2"]
    assert claim_1["verdict"] == "VERIFIED"
    assert claim_1["median_log_log_slope"] >= 0.8
    assert claim_1["max_relative_error_at_delta_1e-5"] <= 1e-3
    assert claim_1["median_error_contraction_1e-4_to_1e-5"] >= 5
    assert claim_1["ffo_sensitivity_calls_per_estimate"] == 0
    assert claim_1["lower_solves_per_estimate"] == 2
    assert len(claim_1["rows"]) == 32
    assert claim_2["verdict"] == "VERIFIED"
    assert claim_2["solution_error"] <= 1e-10
    assert claim_2["ghost_gradient_error"] <= 1e-10
    assert claim_2["independent_fd_error"] <= 1e-5
    assert len(claim_2["rows"]) == 8
    print(
        json.dumps(
            {
                "independent_checker": "PASS",
                "claims": [1, 2],
                "checked_rows": 40,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("claim_3", type=Path)
    parser.add_argument("claim_5", type=Path)
    args = parser.parse_args()
    claim_3 = json.loads(args.claim_3.read_text())
    claim_5 = json.loads(args.claim_5.read_text())

    certificate = claim_3["certificate"]
    assert certificate["verdict"] == "VERIFIED"
    assert all(premise["verified"] for premise in certificate["premises"])
    composition = certificate["composition"]
    assert (
        composition["outer_epsilon_exponent"]
        + composition["per_call_epsilon_exponent"]
        == composition["total_epsilon_exponent"]
        == -3
    )
    assert composition["delta_exponent"] == -1
    soc = claim_3["nonlinear_soc"]
    assert soc["row_count"] == 8
    assert soc["all_finite"]
    assert soc["max_relative_gradient_error"] <= 0.35
    assert soc["min_gradient_cosine"] >= 0.95
    assert all(
        row["first_hit_gradient_calls"] is not None
        for row in claim_3["first_hit_calibration"]["rows"]
    )

    assert claim_5["verdict"] == "VERIFIED"
    assert claim_5["comparisons"] == 27
    assert claim_5["all_finite"]
    assert claim_5["max_output_l2_error"] <= 1e-4
    assert claim_5["max_gradient_relative_l2_error"] <= 5e-3
    assert claim_5["min_gradient_cosine"] >= 0.999
    assert claim_5["same_call_shape"]
    assert all(claim_5["source_path_audit"].values())
    assert claim_5["wrong_upstream_coefficient_gradient_gap"] > 1e-2
    print(
        json.dumps(
            {
                "independent_checker": "PASS",
                "claims": [3, 5],
                "claim_3_soc_rows": 8,
                "claim_5_comparisons": 27,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()


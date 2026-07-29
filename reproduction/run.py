import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path


def run_checked(command):
    completed = subprocess.run(command, check=False, text=True, capture_output=True)
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr)
    if completed.returncode != 0:
        raise RuntimeError(f"Command failed ({completed.returncode}): {' '.join(command)}")


def run_expected_failure(command):
    completed = subprocess.run(command, check=False, text=True, capture_output=True)
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr)
    if completed.returncode == 0:
        raise RuntimeError(f"Negative control unexpectedly passed: {' '.join(command)}")
    return completed.returncode


def main():
    started = time.time()
    output = Path("run_output")
    evidence = output / "claims_1_2.json"
    run_checked([sys.executable, "-m", "reproduction.verify", "--output", str(evidence)])
    run_checked([sys.executable, "-m", "reproduction.check", str(evidence)])
    claim_3 = output / "claim_3.json"
    claim_5 = output / "claim_5.json"
    run_checked(
        [sys.executable, "-m", "reproduction.claim3", "--output", str(claim_3)]
    )
    run_checked(
        [sys.executable, "-m", "reproduction.native_layer", "--output", str(claim_5)]
    )
    run_checked(
        [
            sys.executable,
            "-m",
            "reproduction.native_check",
            str(claim_3),
            str(claim_5),
        ]
    )
    controls = {
        "forbidden_oracle_exit": run_expected_failure(
            [
                sys.executable,
                "-m",
                "reproduction.verify",
                "--negative-control",
                "forbidden-oracle",
            ]
        ),
        "active_boundary_exit": run_expected_failure(
            [
                sys.executable,
                "-m",
                "reproduction.verify",
                "--negative-control",
                "active-boundary",
            ]
        ),
        "claim_3_oracle_cost_exit": run_expected_failure(
            [
                sys.executable,
                "-m",
                "reproduction.claim3",
                "--negative-control",
                "oracle-cost",
            ]
        ),
        "claim_3_gradient_sign_exit": run_expected_failure(
            [
                sys.executable,
                "-m",
                "reproduction.claim3",
                "--negative-control",
                "gradient-sign",
            ]
        ),
        "claim_5_wrong_coefficient_exit": run_expected_failure(
            [
                sys.executable,
                "-m",
                "reproduction.native_layer",
                "--negative-control",
            ]
        ),
    }
    allocation = os.cpu_count()
    if hasattr(os, "sched_getaffinity"):
        allocation = len(os.sched_getaffinity(0))
    summary = {
        "status": "PASS",
        "fixed_command": "uv run --frozen python -m reproduction.run",
        "estimated_science_cores": 1,
        "selected_flavor": "cpu-upgrade",
        "actual_cpu_allocation": allocation,
        "runtime_seconds": time.time() - started,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "seeds": list(range(1701, 1709)),
        "negative_controls": controls,
    }
    (output / "runtime.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print("REPRODUCTION_SUMMARY " + json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()

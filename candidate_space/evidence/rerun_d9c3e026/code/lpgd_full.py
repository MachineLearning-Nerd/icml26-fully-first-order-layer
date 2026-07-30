import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path


LPGD_COMMIT = "3e7243a808ce983279e31c24932188ee905c58d0"
METHODS = ["ffocp_eq", "lpgd"]
SEEDS = list(range(1, 6))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    started = time.perf_counter()
    for seed in SEEDS:
        order = METHODS if seed % 2 else list(reversed(METHODS))
        for order_position, method in enumerate(order, start=1):
            raw_path = output.parent / f"claim_6_{method}_seed{seed}.json"
            command = [
                sys.executable,
                "-m",
                "reproduction.lpgd_train_worker",
                "--method",
                method,
                "--seed",
                str(seed),
                "--cores",
                "8",
                "--output",
                str(raw_path),
            ]
            completed = subprocess.run(command, check=False, text=True)
            if completed.returncode != 0:
                raise RuntimeError(
                    f"Command failed ({completed.returncode}): {' '.join(command)}"
                )
            row = json.loads(raw_path.read_text())
            row["execution_order_position"] = order_position
            row["raw_path"] = str(raw_path.relative_to(Path.cwd()))
            row["raw_sha256"] = sha256(raw_path)
            rows.append(row)
            (output.parent / "claim_6_progress.json").write_text(
                json.dumps({"completed": rows}, indent=2, sort_keys=True) + "\n"
            )

    allocation = os.cpu_count()
    if hasattr(os, "sched_getaffinity"):
        allocation = len(os.sched_getaffinity(0))
    evidence = {
        "claim": 6,
        "fixed_command": "uv run --frozen python -m reproduction.run",
        "exact_claim_tested": (
            "FFOLayer outperforms actual LPGD on the reported synthetic "
            "dimension sweep while avoiding Hessian inversion"
        ),
        "scope": {
            "reported_figure": "Figure 5",
            "input_dim": 640,
            "y_dim": 200,
            "seeds": SEEDS,
            "batch_size": 8,
            "epochs": 5,
            "optimizer_iterations_per_method_seed": 1000,
            "method_order_alternated_by_seed": True,
            "effective_cpu_cores": 8,
        },
        "lpgd": {
            "upstream_commit": LPGD_COMMIT,
            "mode": "lpgd",
            "tau": 1e-4,
            "rho": 0.1,
            "solver_tolerance": 1e-12,
        },
        "ffolayer": {
            "backward_tolerance": 1e-6,
            "hessian_inverse_calls": 0,
        },
        "runs": rows,
        "runtime_seconds": time.perf_counter() - started,
        "environment": {
            "selected_flavor": "cpu-upgrade",
            "actual_cpu_allocation": allocation,
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
    }
    output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    print("CLAIM6_RAW " + json.dumps(evidence, sort_keys=True))


if __name__ == "__main__":
    main()

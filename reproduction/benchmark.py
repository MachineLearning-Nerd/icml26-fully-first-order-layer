import argparse
import csv
import hashlib
import json
import math
import os
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path

from scipy.stats import t


OFFICIAL_COMMIT = "28905f3e1750fca5b8918954d5d2ea5bed0cbacc"
SEEDS = list(range(1, 11))
EFFECTIVE_CORES = 8
SYNTHETIC_METHODS = ("ffocp_eq", "qpth", "cvxpylayer")


def run_official(script, arguments, transcript, timeout):
    command = [
        sys.executable,
        "-m",
        "reproduction.official_entrypoint",
        "--script",
        script,
        "--cores",
        str(EFFECTIVE_CORES),
        "--",
        *arguments,
    ]
    started = time.time()
    completed = subprocess.run(
        command,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
    )
    transcript.parent.mkdir(parents=True, exist_ok=True)
    transcript.write_text(completed.stdout)
    print(completed.stdout, end="")
    if completed.returncode != 0:
        raise RuntimeError(f"Official entrypoint failed ({completed.returncode}): {' '.join(command)}")
    return time.time() - started


def read_single_row(path):
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle, skipinitialspace=True))
    if len(rows) != 1:
        raise RuntimeError(f"Expected one epoch row in {path}, found {len(rows)}")
    return {key.strip(): value for key, value in rows[0].items()}


def transcript_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def paired_summary(values):
    mean = statistics.mean(values)
    standard_error = statistics.stdev(values) / math.sqrt(len(values))
    half_width = t.ppf(0.975, len(values) - 1) * standard_error
    return {
        "n": len(values),
        "mean": mean,
        "standard_deviation": statistics.stdev(values),
        "ci95": [mean - half_width, mean + half_width],
    }


def synthetic_benchmarks(output):
    vendor = Path("vendor")
    suffix = "_or_claim4"
    measurements = []
    for seed in SEEDS:
        for method in SYNTHETIC_METHODS:
            transcript = output / "transcripts" / f"synthetic_{method}_seed{seed}.txt"
            arguments = [
                "--method",
                method,
                "--epochs",
                "1",
                "--seed",
                str(seed),
                "--lr",
                "0.001",
                "--batch_size",
                "200",
                "--ydim",
                "800",
                "--backward_eps",
                "0.000001",
                "--device",
                "cpu",
                "--suffix",
                suffix,
            ]
            wall_seconds = run_official(
                "synthetic_task/main_synthetic.py",
                arguments,
                transcript,
                timeout=1800,
            )
            if method == "ffocp_eq":
                filename = f"{method}_ydim800_lr0.001_seed{seed}_backwardTol1e-06.csv"
            else:
                filename = f"{method}_ydim800_lr0.001_seed{seed}.csv"
            result_path = vendor / f"synthetic_results_200{suffix}" / method / filename
            row = read_single_row(result_path)
            measurement = {
                "seed": seed,
                "method": method,
                "train_df_loss": float(row["train_df_loss"]),
                "test_df_loss": float(row["test_df_loss"]),
                "forward_seconds": float(row["forward_time"]),
                "backward_seconds": float(row["backward_time"]),
                "wall_seconds": wall_seconds,
                "transcript_sha256": transcript_sha(transcript),
            }
            measurement["total_phase_seconds"] = (
                measurement["forward_seconds"] + measurement["backward_seconds"]
            )
            measurements.append(measurement)

    by_seed = {
        seed: {
            row["method"]: row
            for row in measurements
            if row["seed"] == seed
        }
        for seed in SEEDS
    }
    qpth_log_ratios = [
        math.log(by_seed[seed]["ffocp_eq"]["backward_seconds"])
        - math.log(by_seed[seed]["qpth"]["backward_seconds"])
        for seed in SEEDS
    ]
    cvx_log_ratios = [
        math.log(by_seed[seed]["ffocp_eq"]["backward_seconds"])
        - math.log(by_seed[seed]["cvxpylayer"]["backward_seconds"])
        for seed in SEEDS
    ]
    qpth_loss_gaps = [
        abs(by_seed[seed]["ffocp_eq"]["test_df_loss"] - by_seed[seed]["qpth"]["test_df_loss"])
        for seed in SEEDS
    ]
    cvx_loss_gaps = [
        abs(
            by_seed[seed]["ffocp_eq"]["test_df_loss"]
            - by_seed[seed]["cvxpylayer"]["test_df_loss"]
        )
        for seed in SEEDS
    ]
    return {
        "scope": {
            "entrypoint": "vendor/FFOLayer/synthetic_task/main_synthetic.py",
            "samples": 2000,
            "training_samples": 1600,
            "test_samples": 400,
            "ydim": 800,
            "batch_size": 200,
            "epochs": 1,
            "seeds": SEEDS,
            "effective_cpu_cores": EFFECTIVE_CORES,
            "ffolayer_backward_tolerance": 1e-6,
        },
        "measurements": measurements,
        "paired_statistics": {
            "ffolayer_over_qpth_backward_log_ratio": paired_summary(qpth_log_ratios),
            "ffolayer_over_cvxpylayer_backward_log_ratio": paired_summary(cvx_log_ratios),
            "ffolayer_qpth_test_loss_absolute_gap": paired_summary(qpth_loss_gaps),
            "ffolayer_cvxpylayer_test_loss_absolute_gap": paired_summary(cvx_loss_gaps),
            "max_qpth_test_loss_absolute_gap": max(qpth_loss_gaps),
            "max_cvxpylayer_test_loss_absolute_gap": max(cvx_loss_gaps),
        },
    }


def sudoku_benchmark(output):
    transcript = output / "transcripts" / "sudoku_ffocp_eq_seed3.txt"
    wall_seconds = run_official(
        "sudoku/main_sudoku.py",
        [
            "--method",
            "ffocp_eq",
            "--epochs",
            "1",
            "--seed",
            "3",
            "--lr",
            "0.1",
            "--batch_size",
            "8",
            "--n",
            "3",
            "--device",
            "cpu",
        ],
        transcript,
        timeout=3600,
    )
    result_dir = Path("vendor/sudoku_results_8/ffocp_eq")
    matches = sorted(result_dir.glob("ffocp_eq_n3_lr0.1_seed3_*.csv"))
    if len(matches) != 1:
        raise RuntimeError(f"Expected one Sudoku result, found {len(matches)}")
    row = read_single_row(matches[0])
    return {
        "scope": {
            "entrypoint": "vendor/FFOLayer/sudoku/main_sudoku.py",
            "board": "9x9",
            "variables": 729,
            "total_puzzles": 10000,
            "training_puzzles": 9000,
            "test_puzzles": 1000,
            "batch_size": 8,
            "epochs": 1,
            "seed": 3,
            "effective_cpu_cores": EFFECTIVE_CORES,
        },
        "measurement": {
            "method": "ffocp_eq",
            "train_loss": float(row["train_loss"]),
            "test_loss": float(row["test_loss"]),
            "train_error": float(row["train_error"]),
            "test_error": float(row["test_error"]),
            "forward_seconds": float(row["forward_time"]),
            "backward_seconds": float(row["backward_time"]),
            "wall_seconds": wall_seconds,
            "transcript_sha256": transcript_sha(transcript),
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    started = time.time()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    allocation = os.cpu_count()
    if hasattr(os, "sched_getaffinity"):
        allocation = len(os.sched_getaffinity(0))
    evidence = {
        "claim": 4,
        "official_repository_commit": OFFICIAL_COMMIT,
        "fixed_command": "uv run --frozen python -m reproduction.run",
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "selected_flavor": "cpu-upgrade",
            "job_cpu_allocation": allocation,
            "effective_cores_per_official_process": EFFECTIVE_CORES,
        },
        "synthetic": synthetic_benchmarks(output_path.parent),
        "sudoku": sudoku_benchmark(output_path.parent),
    }
    evidence["runtime_seconds"] = time.time() - started
    output_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    print("CLAIM4_RAW " + json.dumps(evidence, sort_keys=True))


if __name__ == "__main__":
    main()

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
SEEDS = [1, 2, 3, 4, 5]
METHODS = ["ffocp_eq", "qpth"]
EFFECTIVE_CORES = 8


def run_command(command, transcript, timeout):
    started = time.time()
    try:
        completed = subprocess.run(
            command,
            check=False,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        transcript.parent.mkdir(parents=True, exist_ok=True)
        transcript.write_text(
            f"COMMAND {' '.join(command)}\nTIMEOUT_SECONDS {timeout}\n"
        )
        raise
    transcript.parent.mkdir(parents=True, exist_ok=True)
    transcript.write_text(
        f"COMMAND {' '.join(command)}\nRETURN_CODE {completed.returncode}\n"
    )
    if completed.returncode != 0:
        raise RuntimeError(f"Command failed ({completed.returncode}): {' '.join(command)}")
    return time.time() - started


def sha256(path):
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


def run_backward_kernels(output):
    rows = []
    for seed in SEEDS:
        for method in METHODS:
            for replicate in [1, 2]:
                raw_path = (
                    output / "kernels" / f"{method}_seed{seed}_rep{replicate}.json"
                ).resolve()
                transcript = (
                    output
                    / "transcripts"
                    / f"kernel_{method}_seed{seed}_rep{replicate}.txt"
                )
                command = [
                    sys.executable,
                    "-m",
                    "reproduction.backward_kernel",
                    "--method",
                    method,
                    "--seed",
                    str(seed),
                    "--cores",
                    str(EFFECTIVE_CORES),
                    "--output",
                    str(raw_path),
                ]
                wall_seconds = run_command(command, transcript, timeout=1800)
                raw = json.loads(raw_path.read_text())
                timed = raw["measurement"]
                rows.append(
                    {
                        "seed": seed,
                        "method": method,
                        "replicate": replicate,
                        "forward_seconds": timed["forward_seconds"],
                        "backward_seconds": timed["backward_seconds"],
                        "max_solution_error_to_closed_form": timed[
                            "solution_max_abs_error_to_closed_form"
                        ],
                        "max_box_constraint_violation": timed[
                            "max_box_constraint_violation"
                        ],
                        "loss": timed["loss"],
                        "q_gradient_norm": timed["q_gradient_norm"],
                        "raw_path": str(raw_path.relative_to(Path.cwd())),
                        "raw_sha256": sha256(raw_path),
                        "transcript_sha256": sha256(transcript),
                        "wall_seconds": wall_seconds,
                    }
                )
                progress = {"seeds": SEEDS, "methods": METHODS, "completed": rows}
                (output / "claim_4_progress.json").write_text(
                    json.dumps(progress, indent=2, sort_keys=True) + "\n"
                )

    by_seed = {
        seed: {
            method: [row for row in rows if row["seed"] == seed and row["method"] == method]
            for method in METHODS
        }
        for seed in SEEDS
    }
    qpth_ratios = [
        math.log(statistics.median(row["backward_seconds"] for row in by_seed[seed]["ffocp_eq"]))
        - math.log(statistics.median(row["backward_seconds"] for row in by_seed[seed]["qpth"]))
        for seed in SEEDS
    ]
    qpth_loss_gaps = [
        abs(by_seed[seed]["ffocp_eq"][0]["loss"] - by_seed[seed]["qpth"][0]["loss"])
        for seed in SEEDS
    ]
    return {
        "scope": {
            "input_dim": 640,
            "y_dim": 800,
            "generated_samples": 2000,
            "batch_size": 1,
            "process_isolated": True,
            "timed_fresh_processes_per_seed": 2,
            "seeds": SEEDS,
            "effective_cpu_cores": EFFECTIVE_CORES,
            "methods": METHODS,
            "closed_form_solution": "clip(-q, -1, 0)",
        },
        "measurements": rows,
        "paired_statistics": {
            "ffolayer_over_qpth_backward_log_ratio": paired_summary(qpth_ratios),
            "max_ffolayer_qpth_loss_gap": max(qpth_loss_gaps),
            "max_closed_form_solution_error": max(
                row["max_solution_error_to_closed_form"] for row in rows
            ),
            "max_box_constraint_violation": max(
                row["max_box_constraint_violation"] for row in rows
            ),
        },
    }


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
    return run_command(command, transcript, timeout)


def read_single_row(path):
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle, skipinitialspace=True))
    if len(rows) != 1:
        raise RuntimeError(f"Expected one epoch row in {path}, found {len(rows)}")
    return {key.strip(): value for key, value in rows[0].items()}


def full_ffolayer_synthetic(output):
    suffix = "_or_claim4_kernel"
    transcript = output / "transcripts" / "synthetic_ffocp_eq_full_seed1.txt"
    wall_seconds = run_official(
        "synthetic_task/main_synthetic.py",
        [
            "--method",
            "ffocp_eq",
            "--epochs",
            "1",
            "--seed",
            "1",
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
        ],
        transcript,
        timeout=1800,
    )
    result_path = (
        Path("vendor")
        / f"synthetic_results_200{suffix}"
        / "ffocp_eq"
        / "ffocp_eq_ydim800_lr0.001_seed1_backwardTol1e-06.csv"
    )
    row = read_single_row(result_path)
    return {
        "scope": {
            "entrypoint": "vendor/FFOLayer/synthetic_task/main_synthetic.py",
            "samples": 2000,
            "training_samples": 1600,
            "test_samples": 400,
            "input_dim": 640,
            "y_dim": 800,
            "batch_size": 200,
            "epochs": 1,
            "seed": 1,
            "effective_cpu_cores": EFFECTIVE_CORES,
            "ffolayer_backward_tolerance": 1e-6,
        },
        "measurement": {
            "train_df_loss": float(row["train_df_loss"]),
            "test_df_loss": float(row["test_df_loss"]),
            "forward_seconds": float(row["forward_time"]),
            "backward_seconds": float(row["backward_time"]),
            "wall_seconds": wall_seconds,
            "transcript_sha256": sha256(transcript),
        },
    }


def full_ffolayer_sudoku(output):
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
        timeout=7200,
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
            "train_loss": float(row["train_loss"]),
            "test_loss": float(row["test_loss"]),
            "train_error": float(row["train_error"]),
            "test_error": float(row["test_error"]),
            "forward_seconds": float(row["forward_time"]),
            "backward_seconds": float(row["backward_time"]),
            "wall_seconds": wall_seconds,
            "transcript_sha256": sha256(transcript),
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
            "effective_cores_per_process": EFFECTIVE_CORES,
        },
        "backward_kernels": run_backward_kernels(output_path.parent),
        "full_ffolayer_synthetic": full_ffolayer_synthetic(output_path.parent),
        "full_ffolayer_sudoku": full_ffolayer_sudoku(output_path.parent),
    }
    evidence["runtime_seconds"] = time.time() - started
    output_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    print("CLAIM4_RAW " + json.dumps(evidence, sort_keys=True))


if __name__ == "__main__":
    main()

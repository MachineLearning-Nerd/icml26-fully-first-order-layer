import argparse
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
SEEDS = list(range(1, 9))
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
    raw_path = (output / "warmed_kernel.json").resolve()
    transcript = output / "transcripts" / "warmed_kernel.txt"
    command = [
        sys.executable,
        "-m",
        "reproduction.warmed_kernel",
        "--cores",
        str(EFFECTIVE_CORES),
        "--output",
        str(raw_path),
    ]
    wall_seconds = run_command(command, transcript, timeout=3600)
    raw = json.loads(raw_path.read_text())
    rows = raw["measurements"]

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
            **raw["scope"],
            "raw_path": str(raw_path.relative_to(Path.cwd())),
            "raw_sha256": sha256(raw_path),
            "transcript_sha256": sha256(transcript),
            "wall_seconds": wall_seconds,
        },
        "warmups": raw["warmups"],
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
    }
    evidence["runtime_seconds"] = time.time() - started
    output_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    print("CLAIM4_RAW " + json.dumps(evidence, sort_keys=True))


if __name__ == "__main__":
    main()

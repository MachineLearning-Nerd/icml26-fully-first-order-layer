import argparse
import gc
import hashlib
import json
import os
import platform
import time
from pathlib import Path

import numpy as np
import psutil
import torch

from reproduction.backward_kernel import configure_cores, configure_vendor


INPUT_DIM = 640
Y_DIM = 200
NUM_SAMPLES = 2000
BATCH_SIZE = 8
SEED = 1
METHODS = ["ffocp_eq", "lpgd"]
TOLERANCE = 1e-12
LPGD_COMMIT = "3e7243a808ce983279e31c24932188ee905c58d0"


def source_sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_method(OptModel, method, x, target):
    torch.manual_seed(10_000 + SEED)
    construction_started = time.perf_counter()
    model = OptModel(
        INPUT_DIM,
        Y_DIM,
        layer_type=method,
        constraint_learnable=False,
        batch_size=BATCH_SIZE,
        device=torch.device("cpu"),
        alpha=100,
        dual_cutoff=1e-3,
        slack_tol=1e-8,
        backward_eps=TOLERANCE,
        is_QP=True,
    )
    construction_seconds = time.perf_counter() - construction_started
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    model.train()

    forward_started = time.perf_counter()
    solution, q = model(x)
    forward_seconds = time.perf_counter() - forward_started
    loss = torch.mean(target * solution)
    backward_started = time.perf_counter()
    loss.backward()
    backward_seconds = time.perf_counter() - backward_started
    gradient_norm = float(
        torch.sqrt(
            sum(
                torch.sum(parameter.grad.detach() ** 2)
                for parameter in model.parameters()
                if parameter.grad is not None
            )
        )
    )
    exact = torch.clamp(-q.detach(), min=-1.0, max=0.0)
    solution_error = float(torch.max(torch.abs(solution.detach() - exact)))
    optimizer.step()
    optimizer.zero_grad(set_to_none=True)

    model.eval()
    with torch.no_grad():
        next_solution, _ = model(x)
        next_loss = torch.mean(target * next_solution)
    measurement = {
        "method": method,
        "construction_seconds": construction_seconds,
        "forward_seconds": forward_seconds,
        "backward_seconds": backward_seconds,
        "loss_before_step": float(loss.detach()),
        "loss_after_step_same_batch": float(next_loss),
        "gradient_norm": gradient_norm,
        "solution_max_abs_error_to_closed_form": solution_error,
        "rss_gb": psutil.Process().memory_info().rss / (1024**3),
        "lpgd_solver_tolerance": TOLERANCE if method == "lpgd" else None,
        "lpgd_derivative_seconds": (
            float(model.optlayer.info["dDT_time"])
            if method == "lpgd"
            else None
        ),
    }
    del model, optimizer, solution, q, exact, next_solution
    gc.collect()
    return measurement


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cores", type=int, default=8)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output).resolve()
    root = Path(__file__).resolve().parents[1]

    configure_cores(args.cores)
    configure_vendor()
    from data import genData
    from models import OptModel

    np.random.seed(SEED)
    torch.manual_seed(SEED)
    train_loader, _ = genData(
        torch.device("cpu"),
        INPUT_DIM,
        Y_DIM,
        NUM_SAMPLES,
        BATCH_SIZE,
    )
    x, target = next(iter(train_loader))
    started = time.perf_counter()
    rows = [run_method(OptModel, method, x, target) for method in METHODS]
    allocation = (
        len(os.sched_getaffinity(0))
        if hasattr(os, "sched_getaffinity")
        else args.cores
    )
    evidence = {
        "status": "CALIBRATION_ONLY",
        "claim": 6,
        "fixed_command": "uv run --frozen python -m reproduction.run",
        "scope": {
            "input_dim": INPUT_DIM,
            "y_dim": Y_DIM,
            "num_samples": NUM_SAMPLES,
            "batch_size": BATCH_SIZE,
            "seed": SEED,
            "optimizer": "Adam",
            "learning_rate": 0.001,
            "training_steps": 1,
            "effective_cpu_cores": allocation,
        },
        "lpgd": {
            "upstream_commit": LPGD_COMMIT,
            "mode": "lpgd",
            "tau": 1e-4,
            "rho": 0.1,
            "solver_tolerance": TOLERANCE,
            "cone_program_sha256": source_sha256(
                root / "vendor" / "diffcp_lpgd" / "cone_program.py"
            ),
        },
        "measurements": rows,
        "runtime_seconds": time.perf_counter() - started,
        "environment": {
            "selected_flavor": "cpu-upgrade",
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    print("CLAIM6_CALIBRATION_RAW " + json.dumps(evidence, sort_keys=True))


if __name__ == "__main__":
    main()

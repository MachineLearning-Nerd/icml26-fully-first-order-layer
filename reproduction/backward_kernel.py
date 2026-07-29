import argparse
import json
import os
import sys
import time
import types
from pathlib import Path

import numpy as np
import torch


Y_DIM = 800
INPUT_DIM = 640
NUM_SAMPLES = 2000
BATCH_SIZE = 1


def configure_vendor():
    root = Path(__file__).resolve().parents[1]
    vendor = root / "vendor" / "FFOLayer"
    synthetic = vendor / "synthetic_task"
    os.chdir(vendor)
    sys.path.insert(0, str(synthetic))
    sys.path.insert(1, str(vendor))
    sys.path.insert(2, str(vendor / "src"))
    sys.path.insert(3, str(vendor.parent / "cvxtorch"))
    try:
        from dqp import dQP as _unused_dqp
    except (ImportError, AttributeError):
        unavailable_dqp = types.ModuleType("dqp")

        def missing_dqp(*_args, **_kwargs):
            raise RuntimeError("The optional dQP baseline is not installed")

        unavailable_dqp.dQP = missing_dqp
        sys.modules["dqp"] = unavailable_dqp


def configure_cores(cores):
    if hasattr(os, "sched_getaffinity"):
        available = sorted(os.sched_getaffinity(0))
    else:
        available = list(range(os.cpu_count() or 1))
    selected = available[:cores]
    if len(selected) != cores:
        raise RuntimeError(f"Requested {cores} cores from {len(available)} available")
    if hasattr(os, "sched_setaffinity"):
        os.sched_setaffinity(0, selected)
    torch.set_num_threads(cores)
    torch.set_num_interop_threads(1)


def solve_once(model, x, target):
    model.zero_grad(set_to_none=True)
    started = time.perf_counter()
    solution, q = model(x)
    forward_seconds = time.perf_counter() - started
    q.retain_grad()
    loss = torch.mean(target * solution)
    started = time.perf_counter()
    loss.backward()
    backward_seconds = time.perf_counter() - started
    exact = torch.clamp(-q.detach(), min=-1.0, max=0.0)
    feasibility = torch.stack(
        [
            solution.detach().max(),
            (-solution.detach() - 1.0).max(),
            solution.detach().sum() - 3.0,
        ]
    ).max()
    return {
        "forward_seconds": forward_seconds,
        "backward_seconds": backward_seconds,
        "loss": float(loss.detach()),
        "solution_max_abs_error_to_closed_form": float(
            torch.max(torch.abs(solution.detach() - exact))
        ),
        "max_box_constraint_violation": float(torch.clamp(feasibility, min=0.0)),
        "q_gradient_norm": float(torch.linalg.vector_norm(q.grad)),
        "q": q.detach().cpu().reshape(-1).tolist(),
        "solution": solution.detach().cpu().reshape(-1).tolist(),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--method", choices=["ffocp_eq", "qpth", "cvxpylayer"], required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--repetitions", type=int, default=2)
    parser.add_argument("--cores", type=int, default=8)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output).resolve()

    configure_cores(args.cores)
    configure_vendor()
    from data import genData
    from models import OptModel

    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    train_loader, _ = genData(
        torch.device("cpu"),
        INPUT_DIM,
        Y_DIM,
        NUM_SAMPLES,
        BATCH_SIZE,
    )
    model = OptModel(
        INPUT_DIM,
        Y_DIM,
        layer_type=args.method,
        constraint_learnable=False,
        batch_size=BATCH_SIZE,
        device=torch.device("cpu"),
        alpha=100,
        dual_cutoff=1e-3,
        slack_tol=1e-8,
        backward_eps=1e-6,
        is_QP=True,
    )
    model.train()
    x, target = next(iter(train_loader))

    warmup = solve_once(model, x, target)
    measurements = [solve_once(model, x, target) for _ in range(args.repetitions)]
    evidence = {
        "method": args.method,
        "seed": args.seed,
        "scope": {
            "input_dim": INPUT_DIM,
            "y_dim": Y_DIM,
            "num_samples_generated": NUM_SAMPLES,
            "batch_size": BATCH_SIZE,
            "effective_cpu_cores": (
                len(os.sched_getaffinity(0))
                if hasattr(os, "sched_getaffinity")
                else args.cores
            ),
            "ffolayer_backward_tolerance": 1e-6,
            "warmup_runs": 1,
            "timed_repetitions": args.repetitions,
        },
        "warmup": warmup,
        "measurements": measurements,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    print(
        "BACKWARD_KERNEL "
        + json.dumps(
            {
                "method": args.method,
                "seed": args.seed,
                "forward_seconds": [row["forward_seconds"] for row in measurements],
                "backward_seconds": [row["backward_seconds"] for row in measurements],
                "max_solution_error": max(
                    row["solution_max_abs_error_to_closed_form"]
                    for row in measurements
                ),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

import argparse
import json
import math
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
EPOCHS = 5
TOLERANCES = {"ffocp_eq": 1e-6, "lpgd": 1e-12}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--method", choices=["ffocp_eq", "lpgd"], required=True)
    parser.add_argument("--seed", type=int, choices=range(1, 6), required=True)
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
    train_loader, test_loader = genData(
        torch.device("cpu"),
        INPUT_DIM,
        Y_DIM,
        NUM_SAMPLES,
        BATCH_SIZE,
    )
    construction_started = time.perf_counter()
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
        backward_eps=TOLERANCES[args.method],
        is_QP=True,
    )
    construction_seconds = time.perf_counter() - construction_started
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    iterations = []
    epochs = []
    forward_seconds = 0.0
    backward_seconds = 0.0
    evaluation_seconds = 0.0
    max_solution_error = 0.0
    min_gradient_norm = math.inf
    started = time.perf_counter()
    global_iteration = 0
    for epoch in range(EPOCHS):
        model.train()
        train_losses = []
        for x, target in train_loader:
            forward_started = time.perf_counter()
            solution, q = model(x)
            step_forward_seconds = time.perf_counter() - forward_started
            loss = torch.mean(target * solution)
            backward_started = time.perf_counter()
            loss.backward()
            step_backward_seconds = time.perf_counter() - backward_started
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
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=2.0)
            optimizer.step()
            optimizer.zero_grad(set_to_none=True)

            train_loss = float(loss.detach())
            train_losses.append(train_loss)
            forward_seconds += step_forward_seconds
            backward_seconds += step_backward_seconds
            max_solution_error = max(max_solution_error, solution_error)
            min_gradient_norm = min(min_gradient_norm, gradient_norm)
            iterations.append(
                {
                    "iteration": global_iteration,
                    "epoch": epoch,
                    "train_df_loss": train_loss,
                    "forward_seconds": step_forward_seconds,
                    "backward_seconds": step_backward_seconds,
                    "gradient_norm": gradient_norm,
                    "solution_max_abs_error_to_closed_form": solution_error,
                }
            )
            global_iteration += 1

        model.eval()
        test_losses = []
        evaluation_started = time.perf_counter()
        with torch.no_grad():
            for x, target in test_loader:
                solution, q = model(x)
                test_losses.append(float(torch.mean(target * solution)))
                exact = torch.clamp(-q, min=-1.0, max=0.0)
                max_solution_error = max(
                    max_solution_error,
                    float(torch.max(torch.abs(solution - exact))),
                )
        evaluation_seconds += time.perf_counter() - evaluation_started
        epoch_row = {
            "epoch": epoch,
            "train_df_loss": float(np.mean(train_losses)),
            "test_df_loss": float(np.mean(test_losses)),
        }
        epochs.append(epoch_row)
        print(
            "CLAIM6_EPOCH "
            + json.dumps(
                {"method": args.method, "seed": args.seed, **epoch_row},
                sort_keys=True,
            ),
            flush=True,
        )

    cpu_allocation = (
        len(os.sched_getaffinity(0))
        if hasattr(os, "sched_getaffinity")
        else args.cores
    )
    evidence = {
        "method": args.method,
        "seed": args.seed,
        "scope": {
            "input_dim": INPUT_DIM,
            "y_dim": Y_DIM,
            "num_samples": NUM_SAMPLES,
            "training_samples": 1600,
            "test_samples": 400,
            "batch_size": BATCH_SIZE,
            "epochs": EPOCHS,
            "optimizer_iterations": global_iteration,
            "optimizer": "Adam",
            "learning_rate": 0.001,
            "requested_cpu_cores": args.cores,
            "actual_cpu_allocation": cpu_allocation,
            "torch_threads": torch.get_num_threads(),
            "backward_tolerance": TOLERANCES[args.method],
        },
        "iterations": iterations,
        "epochs": epochs,
        "summary": {
            "construction_seconds": construction_seconds,
            "forward_seconds": forward_seconds,
            "backward_seconds": backward_seconds,
            "evaluation_seconds": evaluation_seconds,
            "wall_seconds": time.perf_counter() - started + construction_seconds,
            "max_solution_error_to_closed_form": max_solution_error,
            "min_gradient_norm": min_gradient_norm,
            "rss_gb": psutil.Process().memory_info().rss / (1024**3),
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    print(
        "CLAIM6_WORKER_DONE "
        + json.dumps(
            {
                "method": args.method,
                "seed": args.seed,
                "wall_seconds": evidence["summary"]["wall_seconds"],
                "final_test_df_loss": epochs[-1]["test_df_loss"],
            },
            sort_keys=True,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()

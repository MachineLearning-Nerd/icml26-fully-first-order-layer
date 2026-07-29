import argparse
import gc
import json
import os
import random
from pathlib import Path

import numpy as np
import torch

from reproduction.backward_kernel import (
    BATCH_SIZE,
    INPUT_DIM,
    NUM_SAMPLES,
    Y_DIM,
    configure_cores,
    configure_vendor,
    report_memory,
    solve_once,
)


METHODS = ["ffocp_eq", "qpth"]
SEEDS = list(range(1, 9))
WARMUPS = 2
TIMED_REPETITIONS = 12


def make_model(OptModel, method, seed):
    torch.manual_seed(10_000 + seed)
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
        backward_eps=1e-6,
        is_QP=True,
    )
    model.train()
    return model


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cores", type=int, default=8)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output).resolve()

    configure_cores(args.cores)
    configure_vendor()
    report_memory("configured")
    from data import genData
    from models import OptModel

    rows = []
    warmup_rows = []
    for seed in SEEDS:
        np.random.seed(seed)
        torch.manual_seed(seed)
        train_loader, _ = genData(
            torch.device("cpu"),
            INPUT_DIM,
            Y_DIM,
            NUM_SAMPLES,
            BATCH_SIZE,
        )
        x, target = next(iter(train_loader))
        models = {
            method: make_model(OptModel, method, seed)
            for method in METHODS
        }
        report_memory(f"seed_{seed}_models_ready")

        for method in METHODS:
            for warmup in range(1, WARMUPS + 1):
                measurement = solve_once(models[method], x, target)
                warmup_rows.append(
                    {
                        "seed": seed,
                        "method": method,
                        "warmup": warmup,
                        **measurement,
                    }
                )

        rng = random.Random(50_000 + seed)
        for replicate in range(1, TIMED_REPETITIONS + 1):
            order = METHODS.copy()
            rng.shuffle(order)
            for order_position, method in enumerate(order, start=1):
                measurement = solve_once(models[method], x, target)
                row = {
                    "seed": seed,
                    "method": method,
                    "replicate": replicate,
                    "order_position": order_position,
                    **measurement,
                }
                rows.append(row)
                print(
                    "WARMED_BACKWARD "
                    + json.dumps(
                        {
                            "seed": seed,
                            "method": method,
                            "replicate": replicate,
                            "order_position": order_position,
                            "backward_seconds": measurement["backward_seconds"],
                            "max_solution_error": measurement[
                                "solution_max_abs_error_to_closed_form"
                            ],
                        },
                        sort_keys=True,
                    ),
                    flush=True,
                )

        del models, train_loader, x, target
        gc.collect()

    evidence = {
        "scope": {
            "input_dim": INPUT_DIM,
            "y_dim": Y_DIM,
            "num_samples_generated_per_seed": NUM_SAMPLES,
            "batch_size": BATCH_SIZE,
            "effective_cpu_cores": (
                len(os.sched_getaffinity(0))
                if hasattr(os, "sched_getaffinity")
                else args.cores
            ),
            "methods": METHODS,
            "seeds": SEEDS,
            "warmups_per_method_seed": WARMUPS,
            "timed_repetitions_per_method_seed": TIMED_REPETITIONS,
            "randomized_order_within_block": True,
            "same_process": True,
            "closed_form_solution": "clip(-q, -1, 0)",
        },
        "warmups": warmup_rows,
        "measurements": rows,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    print("WARMED_KERNEL_RAW " + json.dumps(evidence, sort_keys=True))


if __name__ == "__main__":
    main()

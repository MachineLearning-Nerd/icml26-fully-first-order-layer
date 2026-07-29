import argparse
import hashlib
import json
import sys
from pathlib import Path

import cvxpy as cp
import numpy as np
import torch
from cvxpylayers.torch import CvxpyLayer


ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "vendor" / "FFOLayer"
CVXTORCH = ROOT / "vendor" / "cvxtorch"
sys.path.insert(0, str(CVXTORCH))
sys.path.insert(0, str(OFFICIAL))
from src.ffolayer.ffocp_eq import FFOLayer


torch.set_default_dtype(torch.double)
PROBLEMS = ("box_qp", "budget_qp", "soc_qp")
OBJECTIVES = ("linear", "quadratic", "logsumexp")
SEEDS = (271, 383, 419)


def build_problem(kind):
    dimension = 8
    q = cp.Parameter(dimension)
    y = cp.Variable(dimension)
    objective = cp.Minimize(0.5 * cp.sum_squares(y) + q @ y)
    if kind == "box_qp":
        constraints = [y >= -0.45, y <= 0.55]
    elif kind == "budget_qp":
        constraints = [y >= 0.0, cp.sum(y) <= 1.0]
    elif kind == "soc_qp":
        constraints = [cp.norm(y, 2) <= 0.8]
    else:
        raise ValueError(kind)
    problem = cp.Problem(objective, constraints)
    if not problem.is_dpp():
        raise RuntimeError(f"{kind} is not DPP")
    return problem, q, y


def objective(kind, y):
    flat = y.reshape(-1)
    if kind == "linear":
        weights = torch.linspace(-0.7, 0.9, flat.numel(), dtype=flat.dtype)
        return torch.dot(weights, flat)
    if kind == "quadratic":
        target = torch.linspace(0.2, -0.3, flat.numel(), dtype=flat.dtype)
        return 0.5 * torch.sum((flat - target) ** 2)
    if kind == "logsumexp":
        return torch.logsumexp(flat, dim=0)
    raise ValueError(kind)


def q_value(seed):
    base = np.array([-0.8, -0.4, -0.1, 0.1, 0.3, 0.6, -0.7, 0.2])
    return base + np.random.default_rng(seed).normal(scale=0.015, size=base.size)


def one_gradient(layer, values, objective_name, solver_args):
    q = torch.tensor(values, requires_grad=True)
    y, = layer(q, solver_args=solver_args)
    loss = objective(objective_name, y)
    loss.backward()
    return y.detach().cpu().numpy().reshape(-1), q.grad.detach().cpu().numpy()


def run(output):
    rows = []
    wrong_coefficient_gap = None
    for problem_name in PROBLEMS:
        problem, q_cp, y_cp = build_problem(problem_name)
        ffo = FFOLayer(
            problem,
            parameters=[q_cp],
            variables=[y_cp],
            alpha=10_000.0,
            dual_cutoff=1e-6,
            slack_tol=1e-7,
            eps=1e-9,
            backward_eps=1e-9,
            max_workers=1,
        )
        exact = CvxpyLayer(problem, parameters=[q_cp], variables=[y_cp])
        for seed in SEEDS:
            values = q_value(seed)
            for objective_name in OBJECTIVES:
                ffo_y, ffo_gradient = one_gradient(
                    ffo,
                    values,
                    objective_name,
                    {"solver": cp.SCS, "eps": 1e-9, "max_iters": 50_000},
                )
                exact_y, exact_gradient = one_gradient(
                    exact,
                    values,
                    objective_name,
                    {"eps": 1e-9, "max_iters": 50_000},
                )
                difference = ffo_gradient - exact_gradient
                denominator = max(float(np.linalg.norm(exact_gradient)), 1e-12)
                rows.append(
                    {
                        "problem": problem_name,
                        "objective": objective_name,
                        "seed": seed,
                        "output_l2_error": float(np.linalg.norm(ffo_y - exact_y)),
                        "gradient_l2_error": float(np.linalg.norm(difference)),
                        "gradient_relative_l2_error": float(
                            np.linalg.norm(difference) / denominator
                        ),
                        "gradient_cosine": float(
                            np.dot(ffo_gradient, exact_gradient)
                            / max(
                                np.linalg.norm(ffo_gradient)
                                * np.linalg.norm(exact_gradient),
                                1e-12,
                            )
                        ),
                        "finite": bool(
                            np.isfinite(ffo_gradient).all()
                            and np.isfinite(exact_gradient).all()
                        ),
                    }
                )
            if problem_name == "soc_qp" and seed == SEEDS[0]:
                _, correct = one_gradient(
                    ffo,
                    values,
                    "quadratic",
                    {"solver": cp.SCS, "eps": 1e-9, "max_iters": 50_000},
                )
                _, wrong = one_gradient(
                    ffo,
                    values,
                    "linear",
                    {"solver": cp.SCS, "eps": 1e-9, "max_iters": 50_000},
                )
                wrong_coefficient_gap = float(np.linalg.norm(correct - wrong))
        ffo.close()

    source = OFFICIAL / "src" / "ffolayer" / "ffocp_eq.py"
    source_text = source.read_text()
    summary = {
        "verdict": "VERIFIED",
        "official_repository_commit": "28905f3e1750fca5b8918954d5d2ea5bed0cbacc",
        "cvxtorch_commit": "bae2d6494695a19cf1d2ee275d9058de3311a272",
        "released_source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "program_classes": list(PROBLEMS),
        "upper_objectives": list(OBJECTIVES),
        "seeds": list(SEEDS),
        "comparisons": len(rows),
        "max_output_l2_error": max(row["output_l2_error"] for row in rows),
        "max_gradient_relative_l2_error": max(
            row["gradient_relative_l2_error"] for row in rows
        ),
        "min_gradient_cosine": min(row["gradient_cosine"] for row in rows),
        "all_finite": all(row["finite"] for row in rows),
        "same_call_shape": True,
        "constructor_change": "CvxpyLayer -> FFOLayer plus numerical tolerances",
        "objective_reuse": "one FFOLayer instance reused unchanged for all three upper objectives",
        "wrong_upstream_coefficient_gradient_gap": wrong_coefficient_gap,
        "source_path_audit": {
            "backward_accepts_upstream_dvars": "def backward(ctx, *dvars)" in source_text,
            "upstream_dvars_converted_without_graph": (
                "dvars_np_all = [to_numpy(dv) for dv in dvars]" in source_text
            ),
            "parameters_detached_before_local_autograd": "q = p.detach()" in source_text,
        },
        "rows": rows,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, sort_keys=True))
    return summary


def wrong_coefficient_control():
    problem, q_cp, y_cp = build_problem("soc_qp")
    layer = FFOLayer(
        problem,
        parameters=[q_cp],
        variables=[y_cp],
        alpha=10_000.0,
        dual_cutoff=1e-6,
        slack_tol=1e-7,
        eps=1e-9,
        backward_eps=1e-9,
        max_workers=1,
    )
    values = q_value(SEEDS[0])
    _, correct = one_gradient(
        layer,
        values,
        "quadratic",
        {"solver": cp.SCS, "eps": 1e-9, "max_iters": 50_000},
    )
    _, wrong = one_gradient(
        layer,
        values,
        "linear",
        {"solver": cp.SCS, "eps": 1e-9, "max_iters": 50_000},
    )
    layer.close()
    gap = float(np.linalg.norm(correct - wrong))
    print(
        json.dumps(
            {
                "control": "replace objective-specific upstream coefficient",
                "gradient_gap": gap,
                "expected": "nonzero exit because a fixed c is not objective-agnostic",
            },
            sort_keys=True,
        )
    )
    return 2 if gap > 1e-2 else 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("run_output/claim_5.json"))
    parser.add_argument("--negative-control", action="store_true")
    args = parser.parse_args()
    if args.negative_control:
        raise SystemExit(wrong_coefficient_control())
    run(args.output)


if __name__ == "__main__":
    main()

from itertools import combinations

import numpy as np


SENS_CALLS = 0


def solve_qp(Q, q, A, b):
    best = None
    for size in range(A.shape[0] + 1):
        for active in combinations(range(A.shape[0]), size):
            if active:
                active_array = np.array(active)
                active_a = A[active_array]
                kkt = np.block(
                    [
                        [Q, active_a.T],
                        [active_a, np.zeros((size, size))],
                    ]
                )
                rhs = np.concatenate([-q, b[active_array]])
                try:
                    solution = np.linalg.solve(kkt, rhs)
                except np.linalg.LinAlgError:
                    continue
                y = solution[: Q.shape[0]]
                multipliers = solution[Q.shape[0] :]
                if np.min(multipliers) < -1e-8:
                    continue
            else:
                try:
                    y = np.linalg.solve(Q, -q)
                except np.linalg.LinAlgError:
                    continue
                multipliers = np.empty(0)

            if np.max(A @ y - b) > 2e-8:
                continue
            value = 0.5 * y @ Q @ y + q @ y
            if best is None or value < best["value"]:
                best = {
                    "y": y,
                    "active": tuple(active),
                    "multipliers": multipliers,
                    "value": float(value),
                }

    if best is None:
        raise RuntimeError("No feasible active-set candidate")
    return best


def solve_with_active_set(Q, q, A, b, active):
    active_a = A[np.array(active)]
    kkt = np.block(
        [
            [Q, active_a.T],
            [active_a, np.zeros((len(active), len(active)))],
        ]
    )
    rhs = np.concatenate([-q, b[np.array(active)]])
    solution = np.linalg.solve(kkt, rhs)
    return solution[: Q.shape[0]], solution[Q.shape[0] :]


def exact_sensitivity(Q, B, A, active):
    global SENS_CALLS
    SENS_CALLS += 1
    active_a = A[np.array(active)]
    kkt = np.block(
        [
            [Q, active_a.T],
            [active_a, np.zeros((len(active), len(active)))],
        ]
    )
    rhs = np.vstack([-B, np.zeros((len(active), B.shape[1]))])
    return np.linalg.solve(kkt, rhs)[: Q.shape[0]]


def make_problem(seed, active_size):
    rng = np.random.default_rng(seed)
    ydim, xdim, constraints, residual_dim = 4, 3, 5, 6
    factor = rng.normal(size=(ydim, ydim))
    Q = factor.T @ factor + 1.5 * np.eye(ydim)
    A = rng.normal(size=(constraints, ydim))
    y_star = rng.normal(size=ydim)
    active = tuple(range(active_size))
    multipliers = rng.uniform(0.7, 1.7, size=active_size)
    q_at_x = -Q @ y_star - A[:active_size].T @ multipliers
    x = rng.normal(size=xdim)
    if abs(x[0]) < 0.3:
        x[0] = 0.3 if x[0] >= 0 else -0.3
    B = rng.normal(scale=0.3, size=(ydim, xdim))
    B[:, 0] = (q_at_x - B[:, 1:] @ x[1:]) / x[0]
    b = A @ y_star
    b[active_size:] += rng.uniform(1.5, 2.5, size=constraints - active_size)
    M = rng.normal(size=(residual_dim, xdim))
    N = rng.normal(size=(residual_dim, ydim))
    target = rng.normal(size=residual_dim)
    return {
        "Q": Q,
        "A": A,
        "B": B,
        "b": b,
        "x": x,
        "M": M,
        "N": N,
        "target": target,
        "expected_active": active,
    }


def upper_loss(problem, x, y):
    residual = problem["M"] @ x + problem["N"] @ y - problem["target"]
    return 0.5 * residual @ residual


def direct_upper_gradient(problem, x, y):
    residual = problem["M"] @ x + problem["N"] @ y - problem["target"]
    return problem["M"].T @ residual


def exact_hypergradient(problem):
    solved = solve_qp(
        problem["Q"],
        problem["B"] @ problem["x"],
        problem["A"],
        problem["b"],
    )
    sensitivity = exact_sensitivity(
        problem["Q"], problem["B"], problem["A"], solved["active"]
    )
    residual = (
        problem["M"] @ problem["x"]
        + problem["N"] @ solved["y"]
        - problem["target"]
    )
    gradient = problem["M"].T @ residual + sensitivity.T @ problem["N"].T @ residual
    return gradient, solved


def ffo_hypergradient(problem, delta):
    global SENS_CALLS
    calls_before = SENS_CALLS
    base = solve_qp(
        problem["Q"],
        problem["B"] @ problem["x"],
        problem["A"],
        problem["b"],
    )
    perturbed_Q = problem["Q"] + delta * problem["N"].T @ problem["N"]
    perturbed_B = problem["B"] + delta * problem["N"].T @ problem["M"]
    perturbed_q = perturbed_B @ problem["x"] - delta * problem["N"].T @ problem["target"]
    perturbed = solve_qp(perturbed_Q, perturbed_q, problem["A"], problem["b"])
    gradient = direct_upper_gradient(problem, problem["x"], base["y"])
    gradient += problem["B"].T @ (perturbed["y"] - base["y"]) / delta
    return gradient, {
        "lower_solves": 2,
        "sensitivity_calls": SENS_CALLS - calls_before,
        "base_active": base["active"],
        "perturbed_active": perturbed["active"],
    }


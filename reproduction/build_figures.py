import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path("candidate_space/evidence/current")
OUTPUT = Path("reports/ffolayer/images")


def load(name):
    return json.loads((ROOT / name).read_text())


def save(name):
    plt.tight_layout()
    plt.savefig(OUTPUT / name, dpi=180, bbox_inches="tight")
    plt.close()


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)

    claim_6 = load("claim_6.json")
    rows = {(row["seed"], row["method"]): row for row in claim_6["runs"]}
    seeds = list(range(1, 6))
    ratios = [
        rows[seed, "ffocp_eq"]["summary"]["wall_seconds"]
        / rows[seed, "lpgd"]["summary"]["wall_seconds"]
        for seed in seeds
    ]
    plt.figure(figsize=(7.2, 3.8))
    plt.bar(seeds, ratios, color="#d95f02")
    plt.axhline(1, color="black", linewidth=1)
    plt.xlabel("Paired seed")
    plt.ylabel("Complete runtime ratio (FFOLayer / LPGD)")
    plt.title("FFOLayer is slower in all five full-horizon pairs")
    save("claim6_runtime_ratio.png")

    plt.figure(figsize=(7.2, 3.8))
    for method, label, color in [
        ("ffocp_eq", "FFOLayer", "#d95f02"),
        ("lpgd", "LPGD", "#1b9e77"),
    ]:
        curves = np.array(
            [
                [row["test_df_loss"] for row in rows[seed, method]["epochs"]]
                for seed in seeds
            ]
        )
        mean = curves.mean(axis=0)
        std = curves.std(axis=0, ddof=1)
        epochs = np.arange(1, 6)
        plt.plot(epochs, mean, marker="o", label=label, color=color)
        plt.fill_between(epochs, mean - std, mean + std, alpha=0.18, color=color)
    plt.xlabel("Epoch")
    plt.ylabel("Held-out decision loss (lower is better)")
    plt.title("Both methods converge to statistically matched losses")
    plt.legend()
    save("claim6_convergence.png")

    claim_4 = load("claim_4.json")
    measurements = claim_4["backward_kernels"]["measurements"]
    paired = []
    for seed in range(1, 9):
        ffo = [
            row["backward_seconds"]
            for row in measurements
            if row["seed"] == seed and row["method"] == "ffocp_eq"
        ]
        qpth = [
            row["backward_seconds"]
            for row in measurements
            if row["seed"] == seed and row["method"] == "qpth"
        ]
        paired.append(math.exp(np.mean(np.log(ffo)) - np.mean(np.log(qpth))))
    plt.figure(figsize=(7.2, 3.8))
    plt.bar(range(1, 9), paired, color="#7570b3")
    plt.axhline(1.25, color="black", linestyle="--", label="1.25× slower")
    plt.xlabel("Seed")
    plt.ylabel("Geometric backward ratio (FFOLayer / qpth)")
    plt.title("Paper-dimensional backward benchmark contradicts speed claim")
    plt.legend()
    save("claim4_backward_ratio.png")

    claim_1 = load("claim_1_2.json")["claim_1"]
    deltas = sorted({row["delta"] for row in claim_1["rows"]})
    medians = [
        np.median(
            [
                row["relative_error"]
                for row in claim_1["rows"]
                if row["delta"] == delta and row["active_size"] < 4
            ]
        )
        for delta in deltas
    ]
    plt.figure(figsize=(7.2, 3.8))
    plt.loglog(deltas, medians, marker="o", label="observed")
    reference = medians[0] * np.array(deltas) / deltas[0]
    plt.loglog(deltas, reference, linestyle="--", label="slope 1")
    plt.xlabel("Finite-difference delta")
    plt.ylabel("Median relative hypergradient error")
    plt.title("Claim 1: first-order error contraction")
    plt.legend()
    save("claim1_error_contraction.png")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Verify the committed claim, replication, branch, and attribution contract."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EXPECTED_STATUS = "PARTIAL_C1_C2_C3_C5_VERIFIED_C4_BACKWARD_SPEED_CONJUNCT_FALSIFIED_C6_BLOCKED_HISTORICAL_SCORE_6_OF_12_NO_CURRENT_SCORE"
EXPECTED_BRANCHES = {
    "audit/c1-c2-frozen-baseline",
    "audit/c3-c5-layer-soc",
    "audit/c4-isolated-backward",
    "audit/c4-paper-scale-backward",
    "audit/c4-registered-scale-benchmark",
    "audit/c4-warmed-backward-falsification",
    "audit/c6-actual-lpgd-synthetic",
    "audit/c6-five-seed-lpgd",
    "main",
    "release/c1-c2-evaluator-evidence",
    "release/cumulative-candidate",
}
EXPECTED_COMMITS = 38
CANONICAL_IDENTITY = "MachineLearning-Nerd <MachineLearning-Nerd@users.noreply.github.com>"
CLAIM_IDS = ["C1", "C2", "C3", "C4", "C5", "C6"]
EXPECTED_CLAIM_STATUSES = {
    "C1": "VERIFIED_SCOPED",
    "C2": "VERIFIED_SCOPED",
    "C3": "VERIFIED_SCOPED",
    "C4": "FALSIFIED_SCOPED",
    "C5": "VERIFIED_SCOPED",
    "C6": "BLOCKED_REPLICATION",
}


def load(name: str):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"verification failed: {message}")


def published_branches() -> set[str]:
    remote = git("for-each-ref", "refs/remotes/origin", "--format=%(refname:short)").splitlines()
    remote = {
        name.removeprefix("origin/")
        for name in remote
        if name.startswith("origin/") and name != "origin/HEAD"
    }
    if remote:
        return remote
    return set(git("for-each-ref", "refs/heads", "--format=%(refname:short)").splitlines())


def main() -> None:
    claims = load("claims.json")
    verdicts = load("reproduction_verdicts.json")
    manifest = load("EVIDENCE_MANIFEST.json")
    state = load("AUTONOMOUS_STATE.json")
    accepted = load("candidate_space/evidence/current/accepted_summary.json")
    claim3 = load("candidate_space/evidence/current/claim_3.json")
    claim5 = load("candidate_space/evidence/current/claim_5.json")
    claim6 = load("candidate_space/evidence/current/claim_6_replication_summary.json")
    subset = load("candidate_space/release/subset_check.json")
    traversal = load("candidate_space/release/traversal.json")
    checker_output = (ROOT / "candidate_space/evidence/current/checker_output.txt").read_text(encoding="utf-8")

    require(claims["overall_status"] == EXPECTED_STATUS, "claims overall status")
    require(state["overall_status"] == EXPECTED_STATUS, "autonomous state overall status")
    require([claim["id"] for claim in claims["claims"]] == CLAIM_IDS, "claim ordering")
    require({claim["id"]: claim["status"] for claim in claims["claims"]} == EXPECTED_CLAIM_STATUSES, "claim statuses")
    require(verdicts["claim_statuses"] == EXPECTED_CLAIM_STATUSES, "verdict statuses")

    require(all((ROOT / path).exists() for path in manifest["required_paths"]), "manifest paths")
    require(manifest["controls"]["source_pinned"], "source pin")
    require(manifest["controls"]["independent_checker"], "independent checker")
    require(manifest["controls"]["negative_controls_recorded"], "negative controls")
    require(manifest["controls"]["claim4_speed_conjunct_only"], "Claim 4 scope")
    require(manifest["controls"]["claim6_conflicting_complete_runs_retained"], "Claim 6 replication boundary")

    require(accepted["claim_1"]["verdict"] == "VERIFIED", "Claim 1 evidence")
    require(accepted["claim_2"]["verdict"] == "VERIFIED", "Claim 2 evidence")
    require(accepted["independent_checker"]["status"] == "PASS", "independent checker output")
    require(claim3["certificate"]["verdict"] == "VERIFIED", "Claim 3 certificate")
    require(claim3["certificate"]["composition"] == {"delta_exponent": -1, "outer_epsilon_exponent": -3, "per_call_epsilon_exponent": 0, "total_epsilon_exponent": -3}, "Claim 3 exponents")
    require(claim5["comparisons"] == 27, "Claim 5 comparison count")
    require(claim5["max_output_l2_error"] < 1e-4, "Claim 5 output error")
    require(claim5["max_gradient_relative_l2_error"] < 0.005, "Claim 5 gradient error")
    require(claim5["min_gradient_cosine"] > 0.999, "Claim 5 gradient cosine")

    require("CLAIM4_CHECK PASS" in checker_output and '"status": "FALSIFIED"' in checker_output, "Claim 4 checker")
    require(claim6["final_status"] == "BLOCKED", "Claim 6 final status")
    require(len(claim6["routes"]) == 4, "Claim 6 route count")
    route3 = claim6["routes"][2]
    route4 = claim6["routes"][3]
    require(route3["runtime_log_ffolayer_over_lpgd_ci95"] == [0.030136254493392745, 0.33644682016442173], "Claim 6 first runtime interval")
    require(route4["runtime_log_ffolayer_over_lpgd_ci95"] == [-1.3542203114151148, 0.8220612955157375], "Claim 6 independent runtime interval")
    require(route3["final_test_loss_ffolayer_minus_lpgd_ci95"] == route4["final_test_loss_ffolayer_minus_lpgd_ci95"], "Claim 6 final-loss agreement")

    require(subset["missing_paths"] == [], "historical candidate subset")
    require(traversal["result"] == "PASS" and traversal["missing_required_pages"] == [], "candidate traversal")
    require(verdicts["historical_external_result"]["score"] == "6/12", "historical score")
    require(verdicts["historical_external_result"]["current_score_claim"] is False, "current score claim")
    require(verdicts["publication"]["publication_allowed"] is False, "publication allowed")
    require(verdicts["publication"]["author_endorsement_claimed"] is False, "author endorsement")

    branches = published_branches()
    require(branches == EXPECTED_BRANCHES, "published branch set")
    require(not any(branch.startswith("orx/") for branch in branches), "legacy orx branch")
    require(int(git("rev-list", "--all", "--count")) == EXPECTED_COMMITS, "reachable commit count")
    identities = git("log", "--all", "--format=%an <%ae>\n%cn <%ce>").splitlines()
    require(identities and all(identity == CANONICAL_IDENTITY for identity in identities), "canonical commit identity")
    messages = git("log", "--all", "--format=%B")
    require("co-authored-by:" not in messages.lower(), "co-author trailer")

    print(
        "FINAL_AUDIT=VERIFIED "
        f"branches={len(branches)} commits={EXPECTED_COMMITS} "
        "claims=C1:C3_C5_verified_scoped,C4_speed_conjunct_falsified,C6_blocked_replication "
        "historical_score=6/12 current_score_claim=false publication_allowed=false"
    )


if __name__ == "__main__":
    main()

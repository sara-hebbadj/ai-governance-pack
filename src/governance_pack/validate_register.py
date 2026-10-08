"""Check the risk register and the evidence index before anyone relies on them.

A compliance reader should be able to trust three things about the register:
1. every row is complete and uses the agreed words (no "medium-ish" likelihood);
2. the rating really follows from likelihood x impact;
3. no risk claims "Control verified" unless every piece of linked evidence
   has actually been run and passed. Results that were never measured must
   stay blank (this is the "never invent results" rule, enforced in code).

Usage (from the repo root):
    python -m governance_pack.validate_register
    python -m governance_pack.validate_register governance/risk_register.csv evals/evidence_index.csv

Only the Python standard library is used, so CI needs no extra packages.
"""

from __future__ import annotations

import csv
import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTER = REPO_ROOT / "governance" / "risk_register.csv"
DEFAULT_EVIDENCE = REPO_ROOT / "evals" / "evidence_index.csv"

# ---- Risk register rules -------------------------------------------------

REGISTER_COLUMNS = [
    "risk_id",
    "title",
    "description",
    "category",
    "likelihood",
    "impact",
    "rating",
    "existing_control",
    "test_evidence",
    "evidence_ids",
    "owner",
    "status",
    "next_action",
    "last_reviewed",
]

CATEGORIES = {
    "privacy",
    "security",
    "financial",
    "accuracy",
    "safety",
    "fairness",
    "transparency",
    "operational",
    "cost",
    "oversight",
}
LEVELS = {"Low": 1, "Medium": 2, "High": 3}
OWNERS = {
    "Product owner",
    "Engineering lead",
    "Customer care lead",
    "Data protection lead",
    "Finance lead",
    "Compliance lead",
}
STATUSES = {
    "Open",  # no control yet
    "Control built - evidence pending",  # control exists, proof not yet complete
    "Control verified",  # every linked evidence item has passed
    "Accepted",  # owner accepts the risk as it is (must say why in next_action)
}
RISK_ID = re.compile(r"^R\d{2}$")
EVIDENCE_ID = re.compile(r"^E\d{2}$")

# ---- Evidence index rules ------------------------------------------------

EVIDENCE_COLUMNS = [
    "evidence_id",
    "project",
    "location",
    "check",
    "kind",
    "status",
    "run_date",
    "result",
    "notes",
]
PROJECTS = {"P1", "P3", "P8"}
KINDS = {
    "deterministic_test",  # a pytest test that needs no model
    "deterministic_eval",  # an evaluation run that needs no model (rules baseline, data checks)
    "live_eval_metric",  # a number that only exists after a real model run
    "human_review",  # a person grades or reviews something
    "design_document",  # a written design or procedure in this pack
}
EVIDENCE_STATUSES = {"passed", "failed", "pending live run", "not run yet", "documented"}
RAN = {"passed", "failed"}  # statuses that mean "this was actually executed"


def rating_for(likelihood: str, impact: str) -> str:
    """Turn likelihood x impact (each 1-3) into a rating word.

    Score 1-2 = Low, 3-4 = Medium, 6 = High, 9 = Critical (5, 7, 8 cannot occur).
    """
    score = LEVELS[likelihood] * LEVELS[impact]
    if score <= 2:
        return "Low"
    if score <= 4:
        return "Medium"
    if score <= 6:
        return "High"
    return "Critical"


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    """Return (header, rows). Cells are stripped of surrounding spaces."""
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        header = list(reader.fieldnames or [])
        rows = [{k: (v or "").strip() for k, v in row.items()} for row in reader]
    return header, rows


def missing_columns(header: list[str], required: list[str]) -> list[str]:
    return [c for c in required if c not in header]


def split_ids(cell: str) -> list[str]:
    """'E01; E02' -> ['E01', 'E02']"""
    return [part.strip() for part in cell.split(";") if part.strip()]


def is_iso_date(text: str) -> bool:
    try:
        date.fromisoformat(text)
    except ValueError:
        return False
    return True


def check_evidence_row(row: dict[str, str]) -> list[str]:
    """Problems with one evidence-index row (empty list = fine)."""
    eid = row.get("evidence_id", "")
    where = f"evidence {eid or '?'}"
    problems = []
    if not EVIDENCE_ID.match(eid):
        problems.append(f"{where}: evidence_id must look like E01")
    for col in ("location", "check"):
        if not row.get(col):
            problems.append(f"{where}: '{col}' is empty")
    if row.get("project") not in PROJECTS:
        problems.append(f"{where}: project must be one of {sorted(PROJECTS)}")
    if row.get("kind") not in KINDS:
        problems.append(f"{where}: kind must be one of {sorted(KINDS)}")
    status = row.get("status", "")
    if status not in EVIDENCE_STATUSES:
        problems.append(f"{where}: status must be one of {sorted(EVIDENCE_STATUSES)}")
    if status in RAN:
        # Something that ran must say when and what it found.
        if not is_iso_date(row.get("run_date", "")):
            problems.append(f"{where}: status '{status}' needs a run_date (YYYY-MM-DD)")
        if not row.get("result"):
            problems.append(f"{where}: status '{status}' needs a result")
    else:
        # Honesty rule: nothing that has not run may carry a date or a result.
        if row.get("run_date") or row.get("result"):
            problems.append(
                f"{where}: status '{status}' means it has not run, so run_date and result must be blank"
            )
    if row.get("kind") == "live_eval_metric" and status == "documented":
        problems.append(f"{where}: a live eval metric cannot be 'documented'; it is pending or ran")
    return problems


def check_risk_row(row: dict[str, str], evidence: dict[str, dict[str, str]]) -> list[str]:
    """Problems with one risk-register row (empty list = fine)."""
    rid = row.get("risk_id", "")
    where = f"risk {rid or '?'}"
    problems = []
    if not RISK_ID.match(rid):
        problems.append(f"{where}: risk_id must look like R01")
    for col in REGISTER_COLUMNS:
        if not row.get(col):
            problems.append(f"{where}: '{col}' is empty")
    if row.get("category") and row["category"] not in CATEGORIES:
        problems.append(f"{where}: category '{row['category']}' not in {sorted(CATEGORIES)}")
    if row.get("owner") and row["owner"] not in OWNERS:
        problems.append(f"{where}: owner '{row['owner']}' not in {sorted(OWNERS)}")
    if row.get("status") and row["status"] not in STATUSES:
        problems.append(f"{where}: status '{row['status']}' not in {sorted(STATUSES)}")
    if row.get("last_reviewed") and not is_iso_date(row["last_reviewed"]):
        problems.append(f"{where}: last_reviewed must be a date like 2026-10-08")

    likelihood, impact = row.get("likelihood", ""), row.get("impact", "")
    for name, value in (("likelihood", likelihood), ("impact", impact)):
        if value and value not in LEVELS:
            problems.append(f"{where}: {name} '{value}' must be one of {list(LEVELS)}")
    if likelihood in LEVELS and impact in LEVELS:
        expected = rating_for(likelihood, impact)
        if row.get("rating") != expected:
            problems.append(f"{where}: rating should be '{expected}' for {likelihood} x {impact}")

    ids = split_ids(row.get("evidence_ids", ""))
    unknown = [i for i in ids if i not in evidence]
    if unknown:
        problems.append(f"{where}: evidence_ids not found in the evidence index: {unknown}")
    if row.get("status") == "Control verified":
        not_passed = [i for i in ids if i in evidence and evidence[i]["status"] != "passed"]
        if not ids or not_passed:
            problems.append(
                f"{where}: 'Control verified' needs every linked evidence item to have passed "
                f"(not yet passed: {not_passed or 'no evidence linked'})"
            )
    return problems


def validate(register_path: Path, evidence_path: Path) -> list[str]:
    """Run every check and return a list of human-readable problems."""
    problems: list[str] = []

    ev_header, ev_rows = read_csv(evidence_path)
    gaps = missing_columns(ev_header, EVIDENCE_COLUMNS)
    if gaps:
        return [f"evidence index is missing columns: {gaps}"]
    evidence: dict[str, dict[str, str]] = {}
    for row in ev_rows:
        problems += check_evidence_row(row)
        if row["evidence_id"] in evidence:
            problems.append(f"evidence {row['evidence_id']}: duplicate evidence_id")
        evidence[row["evidence_id"]] = row

    header, rows = read_csv(register_path)
    gaps = missing_columns(header, REGISTER_COLUMNS)
    if gaps:
        return problems + [f"risk register is missing columns: {gaps}"]
    seen: set[str] = set()
    for row in rows:
        problems += check_risk_row(row, evidence)
        if row["risk_id"] in seen:
            problems.append(f"risk {row['risk_id']}: duplicate risk_id")
        seen.add(row["risk_id"])
    if not 10 <= len(rows) <= 15:
        problems.append(f"register has {len(rows)} risks; the brief asks for 10-15")

    # Every evidence item should support at least one risk; orphans usually mean a typo.
    used = {i for row in rows for i in split_ids(row["evidence_ids"])}
    for orphan in sorted(set(evidence) - used):
        problems.append(f"evidence {orphan}: not linked to any risk")
    return problems


def summary(register_path: Path) -> str:
    """One-line count of risks by rating and status, for the README and CI log."""
    _, rows = read_csv(register_path)
    by_rating: dict[str, int] = {}
    by_status: dict[str, int] = {}
    for row in rows:
        by_rating[row["rating"]] = by_rating.get(row["rating"], 0) + 1
        by_status[row["status"]] = by_status.get(row["status"], 0) + 1
    return f"{len(rows)} risks | by rating: {by_rating} | by status: {by_status}"


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    register = Path(args[0]) if len(args) > 0 else DEFAULT_REGISTER
    evidence = Path(args[1]) if len(args) > 1 else DEFAULT_EVIDENCE
    problems = validate(register, evidence)
    if problems:
        print(f"FAILED: {len(problems)} problem(s)")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("OK: risk register and evidence index are valid")
    print(summary(register))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

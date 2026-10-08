"""Checks on the documents themselves: they exist, they carry the disclaimer, their links work,
and every test they cite as 'passed' really appears as PASSED in the recorded test logs."""

from __future__ import annotations

import csv
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
GOV = REPO / "governance"

REQUIRED_DOCS = [
    "01_system_card.md",
    "02_risk_register_summary.md",
    "risk_register.csv",
    "03_eu_ai_act_memo.md",
    "04_nist_ai_rmf_mapping.md",
    "05_uae_data_protection_notes.md",
    "06_red_team_findings.md",
    "07_human_oversight_and_incident_runbook.md",
    "sources.md",
]
TEST_LOGS = {
    "P1": REPO / "evals" / "p1_test_run_2026-10-08.txt",
    "P3": REPO / "evals" / "p3_test_run_2026-10-08.txt",
}
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
FENCE = re.compile(r"```.*?```", re.DOTALL)


def markdown_files() -> list[Path]:
    files = list(GOV.glob("*.md")) + list((REPO / "docs").glob("*.md"))
    files += [REPO / name for name in ("README.md", "LEARN.md", "AGENTS.md") if (REPO / name).exists()]
    return sorted(files)


def github_slug(heading: str) -> str:
    """The anchor GitHub gives a heading: lower case, punctuation removed, spaces -> hyphens."""
    text = re.sub(r"[^\w\- ]", "", heading.strip().lower())
    return text.replace(" ", "-")


def anchors(path: Path) -> set[str]:
    text = FENCE.sub("", path.read_text(encoding="utf-8"))
    return {github_slug(line.lstrip("#")) for line in text.splitlines() if line.startswith("#")}


@pytest.mark.parametrize("name", REQUIRED_DOCS)
def test_required_document_exists(name):
    assert (GOV / name).is_file()


@pytest.mark.parametrize("path", sorted(GOV.glob("*.md")), ids=lambda p: p.name)
def test_every_governance_document_says_it_is_not_legal_advice(path):
    assert "not legal advice" in path.read_text(encoding="utf-8")


@pytest.mark.parametrize("path", markdown_files(), ids=lambda p: p.name)
def test_relative_links_and_anchors_resolve(path):
    text = FENCE.sub("", path.read_text(encoding="utf-8"))
    broken = []
    for target in LINK.findall(text):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        file_part, _, anchor = target.partition("#")
        dest = (path.parent / file_part).resolve() if file_part else path
        if REPO.resolve() not in dest.parents and dest != REPO.resolve():
            broken.append(target)  # points outside this repo: breaks in a clean clone
        elif not dest.exists():
            broken.append(target)
        elif anchor and dest.suffix == ".md" and anchor not in anchors(dest):
            broken.append(target)
    assert broken == [], f"broken links in {path.name}: {broken}"


def passed_tests_in_log(project: str) -> set[str]:
    lines = TEST_LOGS[project].read_text(encoding="utf-8").splitlines()
    return {line.split("::")[1].split()[0] for line in lines if "::" in line and " PASSED" in line}


def test_every_cited_passing_test_is_in_the_recorded_log():
    """If the evidence index says a P1/P3 test passed, the saved pytest log must show it."""
    with (REPO / "evals" / "evidence_index.csv").open(encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["kind"] == "deterministic_test" and r["status"] == "passed"]
    assert rows, "expected some passed deterministic tests"
    for row in rows:
        logged = passed_tests_in_log(row["project"])
        cited = [name.strip() for name in row["check"].split(";")]
        missing = [name for name in cited if name not in logged]
        assert missing == [], f"{row['evidence_id']}: not PASSED in the log: {missing}"


def test_github_slug_matches_githubs_rules():
    assert github_slug(" 8. Launch checklist (go / no-go)") == "8-launch-checklist-go--no-go"
    heading = " 7. AI disclosure: what the customer sees"
    assert github_slug(heading) == "7-ai-disclosure-what-the-customer-sees"

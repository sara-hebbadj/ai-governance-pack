"""Tests for the risk-register validator. No network, standard library only."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from governance_pack.validate_register import (
    DEFAULT_EVIDENCE,
    DEFAULT_REGISTER,
    EVIDENCE_COLUMNS,
    REGISTER_COLUMNS,
    main,
    rating_for,
    validate,
)


def good_evidence(**changes) -> dict[str, str]:
    row = {
        "evidence_id": "E01",
        "project": "P1",
        "location": "shop-support-agent/tests/test_example.py",
        "check": "test_example",
        "kind": "deterministic_test",
        "status": "pending live run",
        "run_date": "",
        "result": "",
        "notes": "",
    }
    row.update(changes)
    return row


def good_risk(risk_id: str, **changes) -> dict[str, str]:
    row = {
        "risk_id": risk_id,
        "title": "Example risk",
        "description": "Something could go wrong.",
        "category": "privacy",
        "likelihood": "Medium",
        "impact": "High",
        "rating": "High",
        "existing_control": "A control.",
        "test_evidence": "A test.",
        "evidence_ids": "E01",
        "owner": "Engineering lead",
        "status": "Control built - evidence pending",
        "next_action": "Run the test.",
        "last_reviewed": "2026-10-08",
    }
    row.update(changes)
    return row


def write_csv(path: Path, columns: list[str], rows: list[dict[str, str]]) -> Path:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    return path


@pytest.fixture
def files(tmp_path):
    """Return a function that writes a register + evidence index and validates them."""

    def _run(risks=None, evidence=None, register_columns=REGISTER_COLUMNS):
        risks = risks if risks is not None else [good_risk(f"R{i:02d}") for i in range(1, 11)]
        evidence = evidence if evidence is not None else [good_evidence()]
        reg = write_csv(tmp_path / "register.csv", register_columns, risks)
        ev = write_csv(tmp_path / "evidence.csv", EVIDENCE_COLUMNS, evidence)
        return validate(reg, ev)

    return _run


# ---- the real files in this repo ----------------------------------------


def test_real_register_and_evidence_index_are_valid():
    assert validate(DEFAULT_REGISTER, DEFAULT_EVIDENCE) == []


def test_cli_returns_zero_for_real_files(capsys):
    assert main([]) == 0
    assert "OK" in capsys.readouterr().out


# ---- rating matrix -------------------------------------------------------


@pytest.mark.parametrize(
    "likelihood, impact, expected",
    [
        ("Low", "Low", "Low"),
        ("Low", "Medium", "Low"),
        ("Low", "High", "Medium"),
        ("Medium", "Medium", "Medium"),
        ("Medium", "High", "High"),
        ("High", "High", "Critical"),
    ],
)
def test_rating_matrix(likelihood, impact, expected):
    assert rating_for(likelihood, impact) == expected


# ---- register checks -----------------------------------------------------


def test_minimal_valid_register_passes(files):
    assert files() == []


def test_missing_column_is_reported(files):
    columns = [c for c in REGISTER_COLUMNS if c != "owner"]
    risks = [{k: v for k, v in good_risk(f"R{i:02d}").items() if k != "owner"} for i in range(1, 11)]
    problems = files(risks=risks, register_columns=columns)
    assert any("missing columns" in p and "owner" in p for p in problems)


def test_unknown_likelihood_is_rejected(files):
    risks = [good_risk(f"R{i:02d}") for i in range(1, 11)]
    risks[0]["likelihood"] = "Very high"
    assert any("likelihood 'Very high'" in p for p in files(risks=risks))


def test_wrong_rating_is_rejected(files):
    risks = [good_risk(f"R{i:02d}") for i in range(1, 11)]
    risks[0]["rating"] = "Low"  # Medium x High should be High
    assert any("rating should be 'High'" in p for p in files(risks=risks))


def test_unknown_owner_and_status_are_rejected(files):
    risks = [good_risk(f"R{i:02d}") for i in range(1, 11)]
    risks[0]["owner"] = "Bob"
    risks[1]["status"] = "Done"
    problems = files(risks=risks)
    assert any("owner 'Bob'" in p for p in problems)
    assert any("status 'Done'" in p for p in problems)


def test_duplicate_risk_id_is_rejected(files):
    risks = [good_risk(f"R{i:02d}") for i in range(1, 11)]
    risks[1]["risk_id"] = "R01"
    assert any("duplicate risk_id" in p for p in files(risks=risks))


def test_too_few_risks_is_rejected(files):
    problems = files(risks=[good_risk("R01")])
    assert any("the brief asks for 10-15" in p for p in problems)


def test_unknown_evidence_id_is_rejected(files):
    risks = [good_risk(f"R{i:02d}") for i in range(1, 11)]
    risks[0]["evidence_ids"] = "E01; E99"
    assert any("E99" in p for p in files(risks=risks))


def test_verified_status_needs_passed_evidence(files):
    """A risk cannot claim 'Control verified' while its evidence is still pending."""
    risks = [good_risk(f"R{i:02d}") for i in range(1, 11)]
    risks[0]["status"] = "Control verified"
    problems = files(risks=risks)  # E01 is 'pending live run'
    assert any("'Control verified' needs every linked evidence item" in p for p in problems)


def test_verified_status_passes_when_evidence_passed(files):
    risks = [good_risk(f"R{i:02d}") for i in range(1, 11)]
    risks[0]["status"] = "Control verified"
    evidence = [good_evidence(status="passed", run_date="2026-10-08", result="12 passed")]
    assert files(risks=risks, evidence=evidence) == []


# ---- evidence-index checks (the honesty rule) ----------------------------


def test_pending_evidence_must_not_carry_a_result(files):
    """'pending live run' with a number in 'result' would be an invented result."""
    evidence = [good_evidence(result="95% task success")]
    assert any("must be blank" in p for p in files(evidence=evidence))


def test_passed_evidence_needs_date_and_result(files):
    evidence = [good_evidence(status="passed")]
    problems = files(evidence=evidence)
    assert any("needs a run_date" in p for p in problems)
    assert any("needs a result" in p for p in problems)


def test_live_metric_cannot_be_merely_documented(files):
    evidence = [good_evidence(kind="live_eval_metric", status="documented")]
    assert any("cannot be 'documented'" in p for p in files(evidence=evidence))


def test_orphan_evidence_is_reported(files):
    evidence = [good_evidence(), good_evidence(evidence_id="E02")]
    assert any("E02: not linked to any risk" in p for p in files(evidence=evidence))

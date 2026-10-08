"""Smoke test for the read-only viewer in app/app.py (skipped when gradio is not installed, as in CI)."""

import importlib.util
from pathlib import Path

import pytest

pytest.importorskip("gradio")
APP_PATH = Path(__file__).resolve().parents[1] / "app" / "app.py"


@pytest.fixture(scope="module")
def app():
    spec = importlib.util.spec_from_file_location("governance_viewer", APP_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_viewer_builds(app):
    assert app.build() is not None


def test_register_filters_and_details(app):
    critical = app.filter_register(app.ALL, "Critical", app.ALL, app.ALL, "")
    assert len(critical) >= 1 and set(critical["rating"]) == {"Critical"}
    assert len(app.filter_register(app.ALL, app.ALL, app.ALL, app.ALL, "")) == len(app.REGISTER)
    assert "Existing control" in app.risk_details(critical["risk_id"].iloc[0])


def test_relative_links_point_to_github(app):
    text = app.github_links("[log](../evals/x.txt) and [runbook](07_runbook.md#8-launch) and [web](https://a.b)")
    assert f"]({app.GITHUB}/evals/x.txt)" in text
    assert f"]({app.GITHUB}/governance/07_runbook.md#8-launch)" in text
    assert "](https://a.b)" in text


def test_go_no_go_section_and_pdfs_exist(app):
    assert app.go_no_go().startswith("## 8.")
    for _title, markdown_file, pdf_file in app.DOCUMENTS:
        assert (app.GOVERNANCE / markdown_file).exists() and (app.PDF_DIR / pdf_file).exists()

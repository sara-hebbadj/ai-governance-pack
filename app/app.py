"""Read-only viewer for the governance pack (can run as a Hugging Face Space).

    pip install -e ".[app]"
    python app/app.py        then open http://127.0.0.1:7860

Shows the documents in governance/, the risk register with filters, the evidence index and the
go/no-go decision, each with its PDF from pdf/. It makes no AI calls and needs no API key.
Relative links inside the documents are turned into links to the GitHub repository, because the
evidence files they point to are not part of the viewer.
"""

from __future__ import annotations

import re
from pathlib import Path

import gradio as gr
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
GOVERNANCE = REPO / "governance"
PDF_DIR = REPO / "pdf"
EVIDENCE_CSV = REPO / "evals" / "evidence_index.csv"
GITHUB = "https://github.com/sara-hebbadj/ai-governance-pack/blob/HEAD"

# (tab title, markdown file, pdf file)
DOCUMENTS = [
    ("System card", "01_system_card.md", "01_system_card.pdf"),
    ("Risk summary", "02_risk_register_summary.md", "02_risk_register_summary.pdf"),
    ("EU AI Act memo", "03_eu_ai_act_memo.md", "03_eu_ai_act_memo.pdf"),
    ("NIST AI RMF mapping", "04_nist_ai_rmf_mapping.md", "04_nist_ai_rmf_mapping.pdf"),
    ("UAE data protection", "05_uae_data_protection_notes.md", "05_uae_data_protection_notes.pdf"),
    ("Red-team findings", "06_red_team_findings.md", "06_red_team_findings.pdf"),
    ("Oversight runbook", "07_human_oversight_and_incident_runbook.md",
     "07_human_oversight_and_incident_runbook.pdf"),
    ("Sources", "sources.md", "sources.pdf"),
]
REGISTER_COLUMNS = ["risk_id", "title", "category", "likelihood", "impact", "rating", "status", "owner"]
RATING_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
ALL = "(all)"

LINK = re.compile(r"\]\((?!https?://|mailto:|#)([^)\s]+)\)")


def github_links(markdown: str, doc_folder: str = "governance") -> str:
    """Point relative links (e.g. ../evals/x.txt or 07_runbook.md#8) at the file on GitHub."""

    def to_github(match: re.Match) -> str:
        target, _, anchor = match.group(1).partition("#")
        parts = [p for p in f"{doc_folder}/{target}".split("/") if p not in ("", ".")]
        resolved: list[str] = []
        for part in parts:
            if part == "..":
                if resolved:
                    resolved.pop()
            else:
                resolved.append(part)
        return f"]({GITHUB}/{'/'.join(resolved)}{'#' + anchor if anchor else ''})"

    return LINK.sub(to_github, markdown)


def read_document(file_name: str) -> str:
    return github_links((GOVERNANCE / file_name).read_text(encoding="utf-8"))


def go_no_go() -> str:
    """Section 8 of the runbook: the launch decision and its checklist."""
    runbook = read_document("07_human_oversight_and_incident_runbook.md")
    match = re.search(r"^## 8\..*?(?=^## 9\.)", runbook, flags=re.MULTILINE | re.DOTALL)
    return match.group(0) if match else runbook


def load_register() -> pd.DataFrame:
    register = pd.read_csv(GOVERNANCE / "risk_register.csv", dtype=str).fillna("")
    order = register["rating"].map(RATING_ORDER).fillna(9)
    return register.assign(_order=order).sort_values(["_order", "risk_id"]).drop(columns="_order")


REGISTER = load_register()


def choices(column: str) -> list[str]:
    def sort_key(value: str):
        return RATING_ORDER.get(value, 9) if column == "rating" else value

    return [ALL, *sorted(REGISTER[column].unique(), key=sort_key)]


def filter_register(category: str, rating: str, status: str, owner: str, text: str) -> pd.DataFrame:
    rows = REGISTER
    for column, value in (("category", category), ("rating", rating), ("status", status), ("owner", owner)):
        if value and value != ALL:
            rows = rows[rows[column] == value]
    if text and text.strip():
        needle = text.strip().lower()
        rows = rows[rows.apply(lambda r: needle in " ".join(r.values).lower(), axis=1)]
    return rows[REGISTER_COLUMNS]


def risk_details(risk_id: str) -> str:
    match = REGISTER[REGISTER["risk_id"] == risk_id]
    if match.empty:
        return "Pick a risk ID to see its controls and evidence."
    r = match.iloc[0]
    return (
        f"### {r['risk_id']}: {r['title']}\n"
        f"**Rating:** {r['rating']} (likelihood {r['likelihood']}, impact {r['impact']}) · "
        f"**Status:** {r['status']} · **Owner:** {r['owner']} · **Last reviewed:** {r['last_reviewed']}\n\n"
        f"**Description.** {r['description']}\n\n**Existing control.** {r['existing_control']}\n\n"
        f"**Test evidence.** {r['test_evidence']} (evidence IDs: {r['evidence_ids']})\n\n"
        f"**Next action.** {r['next_action']}"
    )


def load_evidence() -> pd.DataFrame:
    columns = ["evidence_id", "project", "check", "kind", "status", "run_date", "result"]
    return pd.read_csv(EVIDENCE_CSV, dtype=str).fillna("")[columns]


def pdf_button(file_name: str) -> None:
    path = PDF_DIR / file_name
    if path.exists():
        gr.DownloadButton(f"Download PDF ({file_name})", value=str(path), size="sm")


def build() -> gr.Blocks:
    with gr.Blocks(title="AI governance pack") as demo:
        gr.Markdown(
            "# AI governance pack: Lumi Skin customer-service assistant\n"
            "The documents a risk, legal or compliance team asks for before launching an AI "
            "customer-service agent (system card, risk register, EU AI Act memo, NIST AI RMF mapping, UAE "
            "notes, red-team findings, runbook and go/no-go), each claim tied to a test or evaluation file. "
            "Lumi Skin is **fictional** and all data is synthetic. **This is not legal advice.** Read-only "
            "viewer: no AI calls, no API key needed. Source and evidence files: "
            f"[github.com/sara-hebbadj/ai-governance-pack]({GITHUB.rsplit('/blob', 1)[0]})."
        )
        with gr.Tab("Go / no-go"):
            pdf_button("07_human_oversight_and_incident_runbook.pdf")
            gr.Markdown(go_no_go())
        with gr.Tab("Risk register"):
            gr.Markdown(f"{len(REGISTER)} risks, sorted by rating. Filter the table, then pick a risk ID "
                        "for details.")
            with gr.Row():
                category = gr.Dropdown(choices("category"), value=ALL, label="Category")
                rating = gr.Dropdown(choices("rating"), value=ALL, label="Rating")
                status = gr.Dropdown(choices("status"), value=ALL, label="Status")
                owner = gr.Dropdown(choices("owner"), value=ALL, label="Owner")
                text = gr.Textbox(label="Search text", placeholder="e.g. injection")
            table = gr.Dataframe(filter_register(ALL, ALL, ALL, ALL, ""), interactive=False, wrap=True)
            pick = gr.Dropdown(list(REGISTER["risk_id"]), value=REGISTER["risk_id"].iloc[0], label="Risk ID")
            details = gr.Markdown(risk_details(REGISTER["risk_id"].iloc[0]))
            filters = [category, rating, status, owner, text]
            for control in filters:
                control.change(filter_register, filters, table)
            pick.change(risk_details, pick, details)
            with gr.Row():
                pdf_button("risk_register.pdf")
                pdf_button("02_risk_register_summary.pdf")
        for title, markdown_file, pdf_file in DOCUMENTS:
            with gr.Tab(title):
                pdf_button(pdf_file)
                gr.Markdown(read_document(markdown_file))
        with gr.Tab("Evidence index"):
            gr.Markdown("Every evidence ID (E01, E02, ...) used in the register and the documents, "
                        "with its result.")
            gr.Dataframe(load_evidence(), interactive=False, wrap=True)
    return demo


if __name__ == "__main__":
    build().launch()

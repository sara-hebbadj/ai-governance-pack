"""Export the governance documents (and the risk register as a table) to PDF.

Needs pandoc and wkhtmltopdf on the PATH. Not used by the tests or CI.

    python scripts/export_pdf.py          # writes pdf/*.pdf
"""

from __future__ import annotations

import csv
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GOV = REPO / "governance"
OUT = REPO / "pdf"
CSS = REPO / "scripts" / "pdf.css"
REGISTER_COLUMNS = ["risk_id", "title", "rating", "existing_control", "test_evidence", "owner", "status"]


def to_pdf(markdown: Path, pdf: Path, title: str, landscape: bool = False) -> None:
    extra = ["--pdf-engine-opt=--orientation", "--pdf-engine-opt=Landscape"] if landscape else []
    subprocess.run(
        ["pandoc", str(markdown), "--from", "gfm", "--standalone", "--metadata", f"pagetitle={title}",
         "--css", str(CSS), "--pdf-engine", "wkhtmltopdf",
         "--pdf-engine-opt=--enable-local-file-access", "--pdf-engine-opt=--quiet", *extra, "-o", str(pdf)],
        check=True,
        cwd=markdown.parent,
    )


def register_as_markdown() -> str:
    """The CSV as one Markdown table (the columns a reader needs most)."""
    with (GOV / "risk_register.csv").open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    lines = [
        f"# Risk register ({len(rows)} risks)",
        "",
        "This is not legal advice. Source: governance/risk_register.csv.",
        "",
        "| " + " | ".join(REGISTER_COLUMNS) + " |",
        "|" + "---|" * len(REGISTER_COLUMNS),
    ]
    for row in rows:
        cells = [row[c].replace("|", "/") for c in REGISTER_COLUMNS]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def main() -> int:
    if not (shutil.which("pandoc") and shutil.which("wkhtmltopdf")):
        print("pandoc and wkhtmltopdf are needed for the PDF export")
        return 1
    OUT.mkdir(exist_ok=True)
    for doc in sorted(GOV.glob("*.md")):
        title = doc.stem.split("_", 1)[-1].replace("_", " ").capitalize()
        to_pdf(doc, OUT / f"{doc.stem}.pdf", title)
        print("wrote", (OUT / f"{doc.stem}.pdf").relative_to(REPO))
    with tempfile.TemporaryDirectory() as tmp:
        table = Path(tmp) / "risk_register.md"
        table.write_text(register_as_markdown(), encoding="utf-8")
        to_pdf(table, OUT / "risk_register.pdf", "Risk register", landscape=True)
    print("wrote pdf/risk_register.pdf")
    return 0


if __name__ == "__main__":
    sys.exit(main())

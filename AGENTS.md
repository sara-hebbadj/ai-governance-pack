# Notes for coding agents working on this repo

This is project P8 of Sara Hebbadj's portfolio: a governance pack for the P1 customer-service agent (`shop-support-agent`). Most of the repo is documents. The only code is a small validator and its tests. Sara must be able to explain every line, so keep it plain.

## Layout

- `governance/`: the seven documents plus `sources.md` and `risk_register.csv`. Numbered files are read in order.
- `evals/evidence_index.csv`: one row per piece of evidence. `evals/*_2026-10-08.txt` are saved logs. Do not edit them; add new dated logs instead.
- `src/governance_pack/validate_register.py`: standard library only. It enforces columns, allowed values, the rating rule and the honesty rules.
- `tests/`: `test_validate_register.py` covers the validator. `test_documents.py` checks that the documents exist, carry the disclaimer, have links that resolve, and cite only tests that appear as PASSED in the saved logs.
- `scripts/probe_p1.py`: needs P1 installed. It is not run in CI. `scripts/export_pdf.py` needs pandoc and wkhtmltopdf.

## Rules

1. **Never invent results.** A number goes into `evidence_index.csv` only after the check has run. Give it a `run_date`, a `result`, and a log or results file a reviewer can open. Otherwise leave the status as `pending live run` or `not run yet`, with an empty result.
2. **"Control verified"** only when every linked evidence item has `passed`. The validator enforces this. Do not weaken the rule to make CI green.
3. **When P1 or P3 changes** (test names, file paths, metrics), update the evidence index, re-record the logs with a new date, and fix the documents. Run `pytest -q`. The log check fails if a cited test is no longer PASSED.
4. **Legal statements need a source in `governance/sources.md`**, with the date it was checked. Prefer EUR-Lex, the European Commission, NIST, the UAE Legislation portal and the DIFC. Mark secondary sources as secondary. Every governance document keeps the line "This is not legal advice."
5. **Synthetic data only.** Use the fictional shop name "Lumi Skin", `@example.com` emails and `+971 50 000 xxxx` phones. Real names and phone numbers of approvers go in a private copy, never in this repo.
6. **No network in tests. No secrets.** Do not create GitHub repos, push or publish without Sara's OK.

## Checks before you finish

```bash
python -m governance_pack.validate_register
pytest -q
ruff check .
python scripts/export_pdf.py   # if you changed a document and pandoc is available
```

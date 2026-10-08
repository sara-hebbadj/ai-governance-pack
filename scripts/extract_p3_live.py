"""Read P3's saved live-run files and print the numbers this governance pack cites. No model calls.

Not part of CI (it needs P3's evals folder):

    python scripts/extract_p3_live.py path/to/multilingual-llm-eval/evals 20261008T124509Z

Only rows of the given run ID are counted (P3's results files also hold earlier smoke runs).
The output is saved as evals/p3_live_eval_extract_<date>.txt (evidence E22-E28, E31).
"""

from __future__ import annotations

import collections
import csv
import sys
from pathlib import Path

TRUE = {"true", "1", "yes"}


def read_run(path: Path, run_id: str) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig") as f:  # P3 writes its CSVs with a byte-order mark
        return [row for row in csv.DictReader(f) if row["run_id"] == run_id]


def is_true(cell: str) -> bool:
    return cell.strip().lower() in TRUE


def quality(rows: list[dict[str, str]]) -> None:
    print("QUALITY (judge pass rule: accuracy >= 4 and policy = 5)")
    count: dict[tuple, collections.Counter] = collections.defaultdict(collections.Counter)
    for r in rows:
        keys = [(r["model"], "all"), (r["model"], r["language"])]
        if r["category"] == "policy_fact":
            keys.append((r["model"], "policy_fact " + r["language"]))
        for key in keys:
            c = count[key]
            c["n"] += 1
            c["passed"] += is_true(r["passed"])
            c["errors"] += bool(r["answer_error"] or r["judge_error"])
    for (model, group), c in sorted(count.items()):
        print(f"  {model:30s} {group:16s} passed {c['passed']}/{c['n']}  errors {c['errors']}")
    by_model: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
    for r in rows:
        by_model[r["model"]].append(r)
    for model, items in sorted(by_model.items()):
        pf = [r for r in items if r["category"] == "policy_fact"]
        print(f"  {model:30s} policy_fact all    passed {sum(is_true(r['passed']) for r in pf)}/{len(pf)}")
        failed = [r["item_id"] for r in items if not is_true(r["passed"])]
        print(f"  {model:30s} failed items: {failed}")


def redteam(rows: list[dict[str, str]]) -> None:
    print("RED TEAM (final verdict: judge, overridden by rule checks)")
    count: dict[tuple, collections.Counter] = collections.defaultdict(collections.Counter)
    for r in rows:
        for key in [(r["model"], "all"), (r["model"], r["attack_type"])]:
            c = count[key]
            c["n"] += 1
            c["blocked"] += is_true(r["blocked"])
            c["harmful"] += is_true(r["harmful"])
            c["rule_hits"] += bool(r["rule_hits"].strip())
            c["human_check"] += is_true(r["needs_human_check"])
    for (model, group), c in sorted(count.items()):
        print(f"  {model:30s} {group:20s} blocked {c['blocked']}/{c['n']}  harmful {c['harmful']}  "
              f"rule hits {c['rule_hits']}  open human checks {c['human_check']}")
    for r in rows:
        if not is_true(r["blocked"]) or r["rule_hits"].strip():
            where = f"{r['model']} {r['item_id']} {r['attack_type']}"
            print(f"  not blocked or rule hit: {where} rules={r['rule_hits']}")


def cost(quality_rows: list[dict[str, str]], redteam_rows: list[dict[str, str]]) -> None:
    print("COST (US$, from OpenRouter usage saved per row)")
    for model in sorted({r["model"] for r in quality_rows}):
        q = [r for r in quality_rows if r["model"] == model]
        t = [r for r in redteam_rows if r["model"] == model]
        answers = sum(float(r["answer_cost_usd"] or 0) for r in q)
        judge = sum(float(r["judge_cost_usd"] or 0) for r in q)
        redteam_cost = sum(float(r["answer_cost_usd"] or 0) + float(r["judge_cost_usd"] or 0) for r in t)
        total = answers + judge + redteam_cost
        print(f"  {model:30s} quality answers per 100: {100 * answers / len(q):.4f}  "
              f"judge per 100: {100 * judge / len(q):.4f}  whole run incl. red team: {total:.4f}")


def main(folder: Path, run_id: str) -> int:
    q = read_run(folder / "results.csv", run_id)
    t = read_run(folder / "redteam_results.csv", run_id)
    print(f"run {run_id}: {len(q)} quality rows, {len(t)} red-team rows")
    quality(q)
    redteam(t)
    cost(q, t)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    raise SystemExit(main(Path(sys.argv[1]), sys.argv[2]))

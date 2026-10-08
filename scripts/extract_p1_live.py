"""Read P1's saved live-run files and print the numbers this governance pack cites. No model calls.

Not part of CI (it needs P1's results folder):

    python scripts/extract_p1_live.py path/to/shop-support-agent/evals/results

The output is saved as evals/p1_live_eval_extract_<date>.txt (evidence E14-E18, E37).
"""

from __future__ import annotations

import collections
import csv
import json
import sys
from pathlib import Path

RUN = "agent_cheap_2026-10-08"
OTHER_RUNS = ("agent_main_10perlang_2026-10-08", "plain_cheap_2026-10-08")
# Categories where the agent may queue a refund or an address change (risks R03 and R05).
APPROVAL_CATEGORIES = ("return_refund", "address_change", "prompt_injection")
SUMMARY_COLUMNS = ("n", "task_success_pct", "decision_correct_pct", "conversations_with_violations",
                   "avg_cost_usd", "avg_latency_ms", "avg_judge_tone", "avg_judge_helpfulness")


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.open(encoding="utf-8")]


def per_category(rows: list[dict]) -> dict[str, collections.Counter]:
    by: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for r in rows:
        c = by[r["category"]]
        c["n"] += 1
        for key in ("task_success", "tool_use_correct", "decision_correct"):
            c[key] += bool(r["score"][key])
        c["violations"] += len(r["score"]["violations"])
    return by


def print_categories(by: dict[str, collections.Counter]) -> None:
    print("category            n  task  tools  decision  violations")
    for cat, c in by.items():
        counts = f"{c['n']:3d} {c['task_success']:5d} {c['tool_use_correct']:6d}"
        print(f"{cat:18s} {counts} {c['decision_correct']:9d} {c['violations']:11d}")
    ok = sum(by[c]["decision_correct"] for c in APPROVAL_CATEGORIES)
    n = sum(by[c]["n"] for c in APPROVAL_CATEGORIES)
    print(f"decision_correct in {', '.join(APPROVAL_CATEGORIES)}: {ok}/{n}")


def print_misses(rows: list[dict]) -> None:
    decision = [(r["id"], r["outcome"], r["expected"]["outcome"])
                for r in rows if not r["score"]["decision_correct"]]
    tools = [(r["id"], r["tool_calls"], r["expected"]["tool_calls"])
             for r in rows if not r["score"]["tool_use_correct"]]
    print("decision misses:", decision)
    print("tool-use misses:", tools)
    print("errors:", sum(1 for r in rows if r["error"]))


def print_models(traces: list[dict]) -> None:
    runs = (RUN, *OTHER_RUNS)
    wanted = [t for t in traces if t["run_id"] in runs]
    calls = collections.Counter((t["run_id"], t["purpose"], t["model"]) for t in wanted)
    print("model calls in traces.jsonl (run_id, purpose, model): count")
    for key, count in sorted(calls.items()):
        print(f"  {key}: {count}")
    not_ok = sum(1 for t in traces if t["run_id"] == RUN and t["outcome"] != "ok")
    print(f"trace outcomes other than ok in {RUN}:", not_ok)


def print_summaries(results: Path) -> None:
    for run in (RUN, OTHER_RUNS[1], OTHER_RUNS[0]):
        name = f"{run}_summary.csv"
        with (results / name).open(encoding="utf-8") as f:
            overall = next(r for r in csv.DictReader(f) if r["language"] == "all")
        print(name, {k: overall[k] for k in SUMMARY_COLUMNS})


def main(results: Path) -> int:
    rows = read_jsonl(results / f"{RUN}.jsonl")
    print(f"{RUN}.jsonl: {len(rows)} conversations")
    print_categories(per_category(rows))
    print_misses(rows)
    print_models(read_jsonl(results / "traces.jsonl"))
    print_summaries(results)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    raise SystemExit(main(Path(sys.argv[1])))

"""
Reads the raw synthetic CSVs and produces the analysis layer Section 1
(weekly review dashboard) reads from:

  data/weekly_review.json
    - qtd_summary: plan vs actual vs gap-to-target, by product (current quarter)
    - wow_revenue: week-over-week actual revenue and variance, by product
    - pipeline_snapshot: latest week pipeline by product x stage
    - pipeline_wow: week-over-week pipeline value change, by product x stage
"""

import csv
import json
from collections import defaultdict


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def compute_qtd_summary(weekly_rows):
    """Plan vs actual vs gap-to-target for the full current quarter, by product."""
    by_product = defaultdict(lambda: {"plan_total": 0, "actual_qtd": 0, "weeks_actual": 0})
    for r in weekly_rows:
        p = by_product[r["product"]]
        p["plan_total"] += int(r["plan_revenue"])
        if r["status"] == "actual":
            p["actual_qtd"] += int(r["actual_revenue"])
            p["weeks_actual"] += 1

    summary = []
    for product, v in by_product.items():
        plan_qtd = sum(
            int(r["plan_revenue"]) for r in weekly_rows
            if r["product"] == product and r["status"] == "actual"
        )
        gap_to_target = v["plan_total"] - v["actual_qtd"]  # full-quarter target vs QTD actual
        summary.append({
            "product": product,
            "full_quarter_target": v["plan_total"],
            "qtd_plan": plan_qtd,
            "qtd_actual": v["actual_qtd"],
            "qtd_variance": v["actual_qtd"] - plan_qtd,
            "qtd_variance_pct": round((v["actual_qtd"] - plan_qtd) / plan_qtd * 100, 1) if plan_qtd else None,
            "gap_to_full_quarter_target": gap_to_target,
            "weeks_reported": v["weeks_actual"],
        })
    return summary


def compute_wow_revenue(weekly_rows):
    """Week-over-week actual revenue and variance vs. prior week, by product."""
    by_product = defaultdict(list)
    for r in weekly_rows:
        if r["status"] == "actual":
            by_product[r["product"]].append(r)

    out = []
    for product, rows in by_product.items():
        rows.sort(key=lambda r: int(r["week"]))
        for i, r in enumerate(rows):
            prior = rows[i - 1] if i > 0 else None
            actual = int(r["actual_revenue"])
            prior_actual = int(prior["actual_revenue"]) if prior else None
            wow_delta = actual - prior_actual if prior_actual is not None else None
            wow_pct = round(wow_delta / prior_actual * 100, 1) if prior_actual else None
            out.append({
                "product": product,
                "week": int(r["week"]),
                "week_start": r["week_start"],
                "actual_revenue": actual,
                "plan_revenue": int(r["plan_revenue"]),
                "vs_plan_pct": round((actual - int(r["plan_revenue"])) / int(r["plan_revenue"]) * 100, 1),
                "wow_delta": wow_delta,
                "wow_pct": wow_pct,
            })
    return out


def compute_pipeline_snapshot(pipeline_rows):
    max_week = max(int(r["week"]) for r in pipeline_rows)
    return [r for r in pipeline_rows if int(r["week"]) == max_week]


def compute_pipeline_wow(pipeline_rows):
    """Week-over-week pipeline value change, by product x stage."""
    key_fn = lambda r: (r["product"], r["stage"])
    by_key = defaultdict(list)
    for r in pipeline_rows:
        by_key[key_fn(r)].append(r)

    out = []
    for (product, stage), rows in by_key.items():
        rows.sort(key=lambda r: int(r["week"]))
        for i, r in enumerate(rows):
            prior = rows[i - 1] if i > 0 else None
            value = int(r["pipeline_value"])
            prior_value = int(prior["pipeline_value"]) if prior else None
            delta = value - prior_value if prior_value is not None else None
            out.append({
                "product": product,
                "stage": stage,
                "week": int(r["week"]),
                "pipeline_value": value,
                "deal_count": int(r["deal_count"]),
                "wow_delta": delta,
                "wow_pct": round(delta / prior_value * 100, 1) if prior_value else None,
            })
    return out


def main():
    weekly_rows = read_csv("data/asd_weekly_current_quarter.csv")
    pipeline_rows = read_csv("data/asd_pipeline_weekly.csv")

    output = {
        "qtd_summary": compute_qtd_summary(weekly_rows),
        "wow_revenue": compute_wow_revenue(weekly_rows),
        "pipeline_snapshot": compute_pipeline_snapshot(pipeline_rows),
        "pipeline_wow": compute_pipeline_wow(pipeline_rows),
    }

    with open("data/weekly_review.json", "w") as f:
        json.dump(output, f, indent=2)

    print("Wrote data/weekly_review.json")
    print(json.dumps(output["qtd_summary"], indent=2))


if __name__ == "__main__":
    main()

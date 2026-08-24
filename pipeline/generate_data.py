"""
Generate synthetic data modeled on the structure of Waters' Analytical
Sciences Division (ASD) -- NOT real Waters figures. Segment-level scale is
loosely anchored to public disclosures; all product/geo/end-market/pipeline
detail below that is entirely invented for portfolio purposes.

Outputs:
  data/asd_quarterly_revenue.csv        -- 8 trailing quarters, plan vs actual
                                            by product x type x geo x end_market
  data/asd_weekly_current_quarter.csv   -- weekly plan vs actual, current qtr, by product
  data/asd_pipeline_weekly.csv          -- weekly pipeline by stage, current qtr, by product
"""

import csv
import random
from datetime import date, timedelta

random.seed(7)

GEOS = {"US": 0.42, "China": 0.20, "India": 0.12, "Other": 0.26}
END_MARKETS = {"Pharma": 0.55, "Industrial": 0.22, "Academic & Government": 0.23}

# product -> {revenue type: base share of that product's revenue}
PRODUCT_TYPE_MIX = {
    "LC": {"Instruments": 0.45, "Chemistry": 0.35, "Service": 0.20},
    "Mass Spec": {"Instruments": 0.50, "Chemistry": 0.28, "Service": 0.22},
    "Chemicals": {"Chemistry": 1.00},
    "Informatics": {"Informatics": 1.00},
}

# base quarterly revenue per product (rough order of magnitude, invented)
PRODUCT_BASE_Q_REVENUE = {
    "LC": 95_000_000,
    "Mass Spec": 70_000_000,
    "Chemicals": 30_000_000,
    "Informatics": 18_000_000,
}

PRODUCT_GROWTH_PER_Q = {
    "LC": 0.010,
    "Mass Spec": 0.014,
    "Chemicals": 0.006,
    "Informatics": 0.025,
}

PIPELINE_STAGES = ["Prospecting", "Qualified", "Proposal", "Committed"]

QUARTERS = [(2024, 4), (2025, 1), (2025, 2), (2025, 3),
            (2025, 4), (2026, 1), (2026, 2), (2026, 3)]  # current = 2026 Q3


def quarter_label(y, q):
    return f"{y}-Q{q}"


def alloc_split(total, weights_dict, noise=0.06):
    """Split `total` across weights_dict keys with a bit of per-key noise, renormalized."""
    raw = {k: w * random.uniform(1 - noise, 1 + noise) for k, w in weights_dict.items()}
    s = sum(raw.values())
    return {k: total * (v / s) for k, v in raw.items()}


# a few deliberate variance stories, keyed by (product, type, quarter_label)
SCRIPTED_Q_VARIANCE = {
    ("Mass Spec", "Instruments", "2026-Q2"): 0.90,   # miss: capex delay, large pharma account
    ("Informatics", "Informatics", "2026-Q1"): 1.15, # beat: faster SaaS migration
    ("LC", "Chemistry", "2026-Q3"): 1.06,             # beat: replenishment on installed base
    ("Chemicals", "Chemistry", "2025-Q4"): 0.92,      # miss: distributor destocking
}


def gen_quarterly():
    rows = []
    for qi, (y, q) in enumerate(QUARTERS):
        qlabel = quarter_label(y, q)
        for product, base in PRODUCT_BASE_Q_REVENUE.items():
            grown_base = base * (1 + PRODUCT_GROWTH_PER_Q[product]) ** qi
            type_mix = PRODUCT_TYPE_MIX[product]
            type_split = alloc_split(grown_base, type_mix, noise=0.03)

            for rtype, plan_amt in type_split.items():
                plan_amt = round(plan_amt, -3)
                key = (product, rtype, qlabel)
                mult = SCRIPTED_Q_VARIANCE.get(key, random.uniform(0.97, 1.03))
                actual_amt = round(plan_amt * mult, -3)

                geo_plan = alloc_split(plan_amt, GEOS)
                geo_actual = alloc_split(actual_amt, GEOS)
                em_plan = alloc_split(plan_amt, END_MARKETS)
                em_actual = alloc_split(actual_amt, END_MARKETS)

                for geo in GEOS:
                    for em in END_MARKETS:
                        p = (geo_plan[geo] / plan_amt) * (em_plan[em] / plan_amt) * plan_amt
                        a = (geo_actual[geo] / actual_amt) * (em_actual[em] / actual_amt) * actual_amt
                        rows.append({
                            "quarter": qlabel,
                            "product": product,
                            "type": rtype,
                            "geo": geo,
                            "end_market": em,
                            "plan_revenue": int(round(p, -2)),
                            "actual_revenue": int(round(a, -2)),
                        })
    return rows


def gen_weekly_current_quarter():
    """13 weeks of the current quarter (2026-Q3, Jul 1 - Sep 30), by product only."""
    rows = []
    q_start = date(2026, 7, 1)
    today = date(2026, 8, 22)
    weeks_elapsed = (today - q_start).days // 7 + 1  # ~8

    for product, base in PRODUCT_BASE_Q_REVENUE.items():
        grown_base = base * (1 + PRODUCT_GROWTH_PER_Q[product]) ** 7
        weekly_plan_base = grown_base / 13.0
        cum_actual = 0
        cum_plan = 0
        for w in range(1, 14):
            week_start = q_start + timedelta(weeks=w - 1)
            ramp = 0.85 if w <= 6 else 1.15
            plan = weekly_plan_base * ramp
            cum_plan += plan

            if w <= weeks_elapsed:
                noise = random.uniform(0.90, 1.08)
                if product == "Mass Spec" and w in (5, 6):
                    noise = 0.82
                actual = plan * noise
                cum_actual += actual
                status = "actual"
            else:
                actual = None
                status = "forecast"

            rows.append({
                "week": w,
                "week_start": week_start.isoformat(),
                "product": product,
                "status": status,
                "plan_revenue": int(round(plan, -2)),
                "actual_revenue": int(round(actual, -2)) if actual is not None else "",
                "cum_plan_revenue": int(round(cum_plan, -2)),
                "cum_actual_revenue": int(round(cum_actual, -2)) if status == "actual" else "",
            })
    return rows, weeks_elapsed


def gen_pipeline_weekly(weeks_elapsed):
    rows = []
    base_pipeline = {
        "LC": {"Prospecting": 18_000_000, "Qualified": 14_000_000, "Proposal": 9_000_000, "Committed": 6_000_000},
        "Mass Spec": {"Prospecting": 15_000_000, "Qualified": 11_000_000, "Proposal": 7_000_000, "Committed": 4_500_000},
        "Chemicals": {"Prospecting": 5_000_000, "Qualified": 4_000_000, "Proposal": 2_500_000, "Committed": 1_800_000},
        "Informatics": {"Prospecting": 6_000_000, "Qualified": 4_500_000, "Proposal": 3_000_000, "Committed": 2_200_000},
    }
    state = {p: dict(stages) for p, stages in base_pipeline.items()}

    for w in range(1, weeks_elapsed + 1):
        for product, stages in state.items():
            for i, stage in enumerate(PIPELINE_STAGES):
                drift = random.uniform(-0.04, 0.02) if i < 3 else random.uniform(-0.01, 0.05)
                if product == "Mass Spec" and stage == "Committed" and w in (5, 6, 7):
                    drift = -0.08
                stages[stage] = max(stages[stage] * (1 + drift), 200_000)
                rows.append({
                    "week": w,
                    "product": product,
                    "stage": stage,
                    "pipeline_value": int(round(stages[stage], -3)),
                    "deal_count": max(1, int(stages[stage] // random.randint(800_000, 1_800_000))),
                })
    return rows


def write_csv(path, rows):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {path}")


def main():
    write_csv("data/asd_quarterly_revenue.csv", gen_quarterly())
    weekly_rows, weeks_elapsed = gen_weekly_current_quarter()
    write_csv("data/asd_weekly_current_quarter.csv", weekly_rows)
    write_csv("data/asd_pipeline_weekly.csv", gen_pipeline_weekly(weeks_elapsed))
    print(f"Current quarter weeks elapsed: {weeks_elapsed}")


if __name__ == "__main__":
    main()

"""
Driver-based scenario forecast for each ASD product line.

Reads trailing quarterly actuals + the current quarter's QTD data, then
projects the next 4 quarters under three scenarios per product:
  - base:     trailing growth rate continues
  - upside:   growth rate + driver-specific upside delta
  - downside: growth rate - driver-specific downside delta

Drivers are named per product so the forecast reads as "why", not just
"what": each delta represents a real (invented) business dynamic.

Output: data/forecast_scenarios.json
"""

import csv
import json
from collections import defaultdict

FUTURE_QUARTERS = ["2026-Q4", "2027-Q1", "2027-Q2", "2027-Q3"]

# driver-based scenario deltas per product: (base_growth_per_q, upside_delta, downside_delta, driver_label)
DRIVERS = {
    "LC": {
        "base_growth": 0.010,
        "upside_delta": 0.018,
        "downside_delta": 0.020,
        "driver": "Capital equipment refresh cycle and competitive win rate on new LC platforms",
    },
    "Mass Spec": {
        "base_growth": 0.014,
        "upside_delta": 0.022,
        "downside_delta": 0.028,
        "driver": "Large pharma capex timing and mass spec platform competitive displacement risk",
    },
    "Chemicals": {
        "base_growth": 0.006,
        "upside_delta": 0.010,
        "downside_delta": 0.012,
        "driver": "Consumables replenishment rate and attach rate on the installed instrument base",
    },
    "Informatics": {
        "base_growth": 0.025,
        "upside_delta": 0.030,
        "downside_delta": 0.015,
        "driver": "Pace of legacy Empower perpetual-to-SaaS subscription migration",
    },
}


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def historical_by_product_quarter(quarterly_rows):
    """Sum plan/actual revenue across type/geo/end_market, by product x quarter."""
    totals = defaultdict(lambda: {"plan": 0, "actual": 0})
    for r in quarterly_rows:
        key = (r["product"], r["quarter"])
        totals[key]["plan"] += int(r["plan_revenue"])
        totals[key]["actual"] += int(r["actual_revenue"])
    return totals


def current_quarter_estimate(product, qtd_summary_row):
    """Estimate full current-quarter actual: QTD actual + remaining plan (assumes remaining weeks hit plan)."""
    remaining_plan = qtd_summary_row["full_quarter_target"] - qtd_summary_row["qtd_plan"]
    return qtd_summary_row["qtd_actual"] + remaining_plan


def build_forecast(product, current_q_estimate):
    d = DRIVERS[product]
    scenarios = {
        "base": d["base_growth"],
        "upside": d["base_growth"] + d["upside_delta"],
        "downside": d["base_growth"] - d["downside_delta"],
    }
    out = {"driver": d["driver"], "scenarios": {}}
    for scenario, growth in scenarios.items():
        values = []
        running = current_q_estimate
        for q in FUTURE_QUARTERS:
            running = running * (1 + growth)
            values.append({"quarter": q, "revenue": int(round(running, -3))})
        out["scenarios"][scenario] = {
            "quarterly_growth_rate": round(growth, 4),
            "values": values,
        }
    return out


def main():
    quarterly_rows = read_csv("data/asd_quarterly_revenue.csv")
    hist = historical_by_product_quarter(quarterly_rows)

    with open("data/weekly_review.json") as f:
        weekly_review = json.load(f)
    qtd_by_product = {r["product"]: r for r in weekly_review["qtd_summary"]}

    quarters_sorted = sorted({q for (_, q) in hist.keys()})
    current_quarter_label = quarters_sorted[-1]  # 2026-Q3: in-progress, excluded from "completed" history
    completed_quarters = [q for q in quarters_sorted if q != current_quarter_label]

    output = {"history": {}, "forecast": {}}
    for product in DRIVERS:
        output["history"][product] = [
            {
                "quarter": q,
                "plan": hist[(product, q)]["plan"],
                "actual": hist[(product, q)]["actual"],
            }
            for q in completed_quarters
            if (product, q) in hist
        ]
        current_estimate = current_quarter_estimate(product, qtd_by_product[product])
        output["forecast"][product] = build_forecast(product, current_estimate)
        output["forecast"][product]["current_quarter_estimate"] = int(current_estimate)

    with open("data/forecast_scenarios.json", "w") as f:
        json.dump(output, f, indent=2)

    print("Wrote data/forecast_scenarios.json")
    for product in DRIVERS:
        base_end = output["forecast"][product]["scenarios"]["base"]["values"][-1]["revenue"]
        up_end = output["forecast"][product]["scenarios"]["upside"]["values"][-1]["revenue"]
        down_end = output["forecast"][product]["scenarios"]["downside"]["values"][-1]["revenue"]
        print(f"{product:12s} 2027-Q3  downside ${down_end/1e6:.1f}M | base ${base_end/1e6:.1f}M | upside ${up_end/1e6:.1f}M")


if __name__ == "__main__":
    main()

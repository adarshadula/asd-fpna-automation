import { useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const PRODUCTS = ["LC", "Mass Spec", "Chemicals", "Informatics"];
const fmt = (n) => `$${(n / 1_000_000).toFixed(1)}M`;

function RevenueTrend({ rows }) {
  const [product, setProduct] = useState("LC");

  const chartData = rows
    .filter((r) => r.product === product)
    .sort((a, b) => a.week - b.week)
    .map((r) => ({
      week: `W${r.week}`,
      Actual: r.actual_revenue,
      Plan: r.plan_revenue,
      wow_pct: r.wow_pct,
    }));

  return (
    <div className="card">
      <div className="tabs">
        {PRODUCTS.map((p) => (
          <button
            key={p}
            className={`tab ${p === product ? "active" : ""}`}
            onClick={() => setProduct(p)}
          >
            {p}
          </button>
        ))}
      </div>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e2da" />
          <XAxis dataKey="week" tick={{ fontSize: 12, fill: "#5f5e5a" }} />
          <YAxis tickFormatter={fmt} tick={{ fontSize: 12, fill: "#5f5e5a" }} width={60} />
          <Tooltip formatter={(v) => fmt(v)} />
          <Legend wrapperStyle={{ fontSize: 13 }} />
          <Line type="monotone" dataKey="Plan" stroke="#b4b2a9" strokeWidth={2} dot={false} strokeDasharray="4 3" />
          <Line type="monotone" dataKey="Actual" stroke="#0f6e56" strokeWidth={2.5} dot={{ r: 3 }} />
        </LineChart>
      </ResponsiveContainer>
      <div className="wow-strip">
        {chartData.map((d) => (
          <div className="wow-chip" key={d.week}>
            <span className="wow-week">{d.week}</span>
            <span className={`wow-pct ${d.wow_pct >= 0 ? "pos" : d.wow_pct < 0 ? "neg" : ""}`}>
              {d.wow_pct === null || d.wow_pct === undefined ? "—" : `${d.wow_pct >= 0 ? "+" : ""}${d.wow_pct}%`}
            </span>
          </div>
        ))}
      </div>
      <div className="qtd-label">Week-over-week actual revenue change</div>
    </div>
  );
}

export default RevenueTrend;

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const STAGES = ["Prospecting", "Qualified", "Proposal", "Committed"];
const STAGE_COLORS = {
  Prospecting: "#b4b2a9",
  Qualified: "#85b7eb",
  Proposal: "#378ade",
  Committed: "#0f6e56",
};
const fmt = (n) => `$${(n / 1_000_000).toFixed(1)}M`;

function buildStackedData(snapshot) {
  const byProduct = {};
  snapshot.forEach((r) => {
    if (!byProduct[r.product]) byProduct[r.product] = { product: r.product };
    byProduct[r.product][r.stage] = Number(r.pipeline_value);
  });
  return Object.values(byProduct);
}

function biggestMovers(wow, currentWeek) {
  return wow
    .filter((r) => r.week === currentWeek && r.wow_delta !== null)
    .sort((a, b) => Math.abs(b.wow_delta) - Math.abs(a.wow_delta))
    .slice(0, 4);
}

function PipelineView({ snapshot, wow, currentWeek }) {
  const stackedData = buildStackedData(snapshot);
  const movers = biggestMovers(wow, currentWeek);

  return (
    <div className="card">
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={stackedData} layout="vertical" margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e2da" horizontal={false} />
          <XAxis type="number" tickFormatter={fmt} tick={{ fontSize: 12, fill: "#5f5e5a" }} />
          <YAxis type="category" dataKey="product" tick={{ fontSize: 13, fill: "#2c2c2a" }} width={80} />
          <Tooltip formatter={(v) => fmt(v)} />
          <Legend
            wrapperStyle={{ fontSize: 13 }}
            content={() => (
              <div style={{ display: "flex", gap: 16, justifyContent: "center", marginTop: 8 }}>
                {STAGES.map((stage) => (
                  <span key={stage} style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 13 }}>
                    <span
                      style={{
                        width: 10,
                        height: 10,
                        borderRadius: 2,
                        background: STAGE_COLORS[stage],
                        display: "inline-block",
                      }}
                    />
                    {stage}
                  </span>
                ))}
              </div>
            )}
          />
          {STAGES.map((stage) => (
            <Bar key={stage} dataKey={stage} stackId="a" fill={STAGE_COLORS[stage]} />
          ))}
        </BarChart>
      </ResponsiveContainer>

      <div className="qtd-label" style={{ marginTop: 16, marginBottom: 8 }}>
        Biggest week-over-week pipeline moves
      </div>
      <div className="movers-list">
        {movers.map((m, i) => (
          <div className="mover-row" key={i}>
            <span className="mover-label">
              {m.product} · {m.stage}
            </span>
            <span className={`wow-pct ${m.wow_delta >= 0 ? "pos" : "neg"}`}>
              {m.wow_delta >= 0 ? "+" : ""}
              {fmt(m.wow_delta)} ({m.wow_pct >= 0 ? "+" : ""}
              {m.wow_pct}%)
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default PipelineView;

const fmt = (n) => `$${(n / 1_000_000).toFixed(1)}M`;

function QtdSummary({ rows }) {
  return (
    <div className="qtd-grid">
      {rows.map((r) => {
        const isOver = r.qtd_variance >= 0;
        return (
          <div className="qtd-card" key={r.product}>
            <div className="qtd-card-header">
              <span className="qtd-product">{r.product}</span>
              <span className={`qtd-badge ${isOver ? "pos" : "neg"}`}>
                {isOver ? "+" : ""}
                {r.qtd_variance_pct}%
              </span>
            </div>
            <div className="qtd-numbers">
              <div>
                <div className="qtd-label">QTD actual</div>
                <div className="qtd-value">{fmt(r.qtd_actual)}</div>
              </div>
              <div>
                <div className="qtd-label">QTD plan</div>
                <div className="qtd-value muted">{fmt(r.qtd_plan)}</div>
              </div>
            </div>
            <div className="qtd-gap">
              <span className="qtd-label">Gap to full-quarter target</span>
              <span className="qtd-gap-value">{fmt(r.gap_to_full_quarter_target)}</span>
            </div>
            <div className="qtd-bar-track">
              <div
                className="qtd-bar-fill"
                style={{ width: `${Math.min(100, (r.qtd_actual / r.full_quarter_target) * 100)}%` }}
              />
            </div>
            <div className="qtd-label" style={{ marginTop: 4 }}>
              Target: {fmt(r.full_quarter_target)} · {r.weeks_reported} weeks reported
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default QtdSummary;

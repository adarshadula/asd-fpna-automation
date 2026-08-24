import data from "./data/weeklyReview.json";
import metadata from "./data/metadata.json";
import QtdSummary from "./components/QtdSummary";
import RevenueTrend from "./components/RevenueTrend";
import PipelineView from "./components/PipelineView";
import ForecastView from "./components/ForecastView";
import QaAgent from "./components/QaAgent";
import "./App.css";

function App() {
  const currentWeek = Math.max(...data.wow_revenue.map((r) => r.week));

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <div className="eyebrow">Analytical Sciences Division — FP&A</div>
          <h1>Weekly business review</h1>
        </div>
        <div className="header-meta">
          <span>Q3 2026</span>
          <span className="dot">·</span>
          <span>Week {currentWeek} of 13</span>
          <div className="refresh-note">
            Data refreshed {new Date(metadata.last_refreshed).toLocaleString("en-US", {
              dateStyle: "medium",
              timeStyle: "short",
            })}
          </div>
        </div>
      </header>

      <section>
        <h2 className="section-title">Plan vs. actual — quarter to date</h2>
        <QtdSummary rows={data.qtd_summary} />
      </section>

      <section>
        <h2 className="section-title">Weekly revenue trend</h2>
        <RevenueTrend rows={data.wow_revenue} />
      </section>

      <section>
        <h2 className="section-title">Pipeline by stage — week {currentWeek}</h2>
        <PipelineView snapshot={data.pipeline_snapshot} wow={data.pipeline_wow} currentWeek={currentWeek} />
      </section>

      <section>
        <h2 className="section-title">Driver-based forecast — next 4 quarters</h2>
        <ForecastView />
      </section>

      <section>
        <h2 className="section-title">Ask the FP&A analyst</h2>
        <QaAgent />
      </section>

      <footer className="page-footer">
        All figures synthetic — for portfolio demonstration only. Not Waters Corporation data.
      </footer>
    </div>
  );
}

export default App;

import { useMemo, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import forecastData from "../data/forecastScenarios.json";

const PRODUCTS = Object.keys(forecastData.forecast);
const fmt = (n) => `$${(n / 1_000_000).toFixed(1)}M`;
const FUTURE_QUARTERS = ["2026-Q4", "2027-Q1", "2027-Q2", "2027-Q3"];

function projectSeries(currentEstimate, growthRate) {
  let running = currentEstimate;
  return FUTURE_QUARTERS.map((q) => {
    running = running * (1 + growthRate);
    return { quarter: q, value: Math.round(running / 1000) * 1000 };
  });
}

function ForecastView() {
  const [product, setProduct] = useState(PRODUCTS[0]);
  const [growth, setGrowth] = useState(() => {
    const initial = {};
    PRODUCTS.forEach((p) => {
      initial[p] = {
        base: forecastData.forecast[p].scenarios.base.quarterly_growth_rate,
        upside: forecastData.forecast[p].scenarios.upside.quarterly_growth_rate,
        downside: forecastData.forecast[p].scenarios.downside.quarterly_growth_rate,
      };
    });
    return initial;
  });

  const productData = forecastData.forecast[product];
  const history = forecastData.history[product];
  const currentEstimate = productData.current_quarter_estimate;
  const rates = growth[product];

  const chartData = useMemo(() => {
    const histPoints = history.map((h) => ({
      quarter: h.quarter,
      Actual: h.actual,
    }));
    const currentPoint = { quarter: "2026-Q3 (est.)", Actual: currentEstimate, Base: currentEstimate, Upside: currentEstimate, Downside: currentEstimate };

    const baseProj = projectSeries(currentEstimate, rates.base);
    const upsideProj = projectSeries(currentEstimate, rates.upside);
    const downsideProj = projectSeries(currentEstimate, rates.downside);

    const futurePoints = FUTURE_QUARTERS.map((q, i) => ({
      quarter: q,
      Base: baseProj[i].value,
      Upside: upsideProj[i].value,
      Downside: downsideProj[i].value,
    }));

    return [...histPoints, currentPoint, ...futurePoints];
  }, [history, currentEstimate, rates]);

  const updateRate = (scenario, value) => {
    setGrowth((prev) => ({
      ...prev,
      [product]: { ...prev[product], [scenario]: value },
    }));
  };

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

      <div className="driver-note">
        <span className="qtd-label">Primary driver</span>
        <div>{productData.driver}</div>
      </div>

      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e2da" />
          <XAxis dataKey="quarter" tick={{ fontSize: 11, fill: "#5f5e5a" }} />
          <YAxis tickFormatter={fmt} tick={{ fontSize: 12, fill: "#5f5e5a" }} width={60} />
          <Tooltip formatter={(v) => fmt(v)} />
          <Legend wrapperStyle={{ fontSize: 13 }} />
          <ReferenceLine x="2026-Q3 (est.)" stroke="#b4b2a9" strokeDasharray="2 2" />
          <Line type="monotone" dataKey="Actual" stroke="#1b1f23" strokeWidth={2.5} dot={{ r: 3 }} connectNulls />
          <Line type="monotone" dataKey="Upside" stroke="#639922" strokeWidth={2} strokeDasharray="5 3" dot={false} connectNulls />
          <Line type="monotone" dataKey="Base" stroke="#185fa5" strokeWidth={2} strokeDasharray="5 3" dot={false} connectNulls />
          <Line type="monotone" dataKey="Downside" stroke="#a32d2d" strokeWidth={2} strokeDasharray="5 3" dot={false} connectNulls />
        </LineChart>
      </ResponsiveContainer>

      <div className="scenario-sliders">
        {["upside", "base", "downside"].map((scenario) => (
          <div className="slider-row" key={scenario}>
            <label className={`slider-label ${scenario}`}>{scenario}</label>
            <input
              type="range"
              min="-0.03"
              max="0.06"
              step="0.001"
              value={rates[scenario]}
              onChange={(e) => updateRate(scenario, parseFloat(e.target.value))}
            />
            <span className="slider-value">{(rates[scenario] * 100).toFixed(1)}% / qtr</span>
          </div>
        ))}
      </div>
      <div className="qtd-label">
        2027-Q3 range: {fmt(chartData[chartData.length - 1].Downside)} to {fmt(chartData[chartData.length - 1].Upside)}
      </div>
    </div>
  );
}

export default ForecastView;

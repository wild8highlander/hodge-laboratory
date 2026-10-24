import React, { useEffect, useRef } from 'react';
import Plotly from 'plotly.js-dist-min';
import { DATA } from '../data/theorems.js';

const DARK = {
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  font: { color: '#94a3b8', family: 'Inter, system-ui, sans-serif', size: 12 },
  margin: { l: 56, r: 20, t: 12, b: 44 },
  xaxis: { gridcolor: 'rgba(148,163,184,0.12)', zerolinecolor: 'rgba(148,163,184,0.2)' },
  yaxis: { gridcolor: 'rgba(148,163,184,0.12)', zerolinecolor: 'rgba(148,163,184,0.2)' },
  hoverlabel: { bgcolor: '#1e293b', bordercolor: '#38bdf8', font: { color: '#e2e8f0' } },
  legend: { bgcolor: 'rgba(0,0,0,0)', orientation: 'h', y: -0.22 },
};

export default function Dashboard() {
  const genusRef = useRef(null);
  const snfRef = useRef(null);
  const residRef = useRef(null);

  useEffect(() => {
    const cfg = { responsive: true, displaylogo: false };

    // ---- 1. The genus ladder ----------------------------------------
    const L = DATA.genusLadder;
    Plotly.newPlot(genusRef.current, [
      { type: 'bar', x: L.map((d) => d.label), y: L.map((d) => d.g),
        name: 'genus g(N)',
        marker: { color: ['rgba(148,163,184,0.55)', 'rgba(148,163,184,0.7)', 'rgba(56,189,248,0.75)',
                         'rgba(56,189,248,0.9)', 'rgba(167,139,250,0.85)', 'rgba(244,114,182,0.9)', 'rgba(244,114,182,1)'],
                  line: { color: 'rgba(226,232,240,0.35)', width: 1 } },
        hovertemplate: '<b>%{x}</b><br>g = %{y}<extra></extra>' },
      { type: 'scatter', mode: 'lines+markers', x: L.map((d) => d.label), y: L.map((d) => d.g),
        name: 'the ladder', line: { color: '#38bdf8', width: 2, shape: 'spline', smoothing: 0.6 },
        marker: { size: 5, color: '#e2e8f0' }, hoverinfo: 'skip' },
    ], { ...DARK, yaxis: { ...DARK.yaxis, title: { text: 'genus g(N)', font: { size: 12 } } } }, cfg);

    // ---- 2. The SNF spectra -----------------------------------------
    const snf = DATA.snf;
    const rungs = Object.keys(snf);
    const traces = [];
    const factors = [...new Set(rungs.flatMap((r) => snf[r]))].sort((a, b) => a - b);
    const factorColors = { 1: 'rgba(148,163,184,0.6)', 3: 'rgba(56,189,248,0.75)',
                           5: 'rgba(167,139,250,0.8)', 7: 'rgba(244,114,182,0.8)',
                           9: 'rgba(251,191,36,0.8)', 11: 'rgba(52,211,153,0.85)', 15: 'rgba(230,57,70,0.85)' };
    for (const f of factors) {
      traces.push({
        type: 'bar', x: rungs, y: rungs.map((r) => snf[r].filter((v) => v === f).length),
        name: `factor ${f}`, marker: { color: factorColors[f] || 'rgba(148,163,184,0.6)' },
        hovertemplate: 'rung %{x}<br>factor %{fulldata.name} × %{y}<extra></extra>',
      });
    }
    Plotly.newPlot(snfRef.current, traces, {
      ...DARK, barmode: 'stack',
      yaxis: { ...DARK.yaxis, title: { text: 'invariant factors (count)', font: { size: 12 } }, dtick: 1 },
    }, cfg);

    // ---- 3. Residuals vs thresholds (log scale) ---------------------
    const R = DATA.residuals;
    Plotly.newPlot(residRef.current, [
      { type: 'scatter', mode: 'markers', x: R.map((d) => d.label), y: R.map((d) => d.residual),
        name: 'observed residual', marker: { color: '#38bdf8', size: 10, line: { color: '#0b1120', width: 1 } },
        hovertemplate: '<b>%{x}</b><br>residual = %{y:E}<extra></extra>' },
      { type: 'scatter', mode: 'markers+lines', x: R.map((d) => d.label), y: R.map((d) => d.threshold),
        name: 'contract threshold', line: { color: 'rgba(244,114,182,0.6)', width: 1.5, dash: 'dot' },
        marker: { color: '#f472b6', size: 7, symbol: 'diamond-open' },
        hovertemplate: '<b>%{x}</b><br>threshold = %{y:E}<extra></extra>' },
    ], { ...DARK, yaxis: { ...DARK.yaxis, type: 'log', title: { text: 'deviation (log)', font: { size: 12 } } } }, cfg);

    return () => { Plotly.purge(genusRef.current); Plotly.purge(snfRef.current); Plotly.purge(residRef.current); };
  }, []);

  return (
    <div>
      <div className="stats">
        <div className="glass stat c1"><div className="n">22</div><div className="l">theorem monographs</div></div>
        <div className="glass stat c2"><div className="n">88</div><div className="l">documents · 4 formats</div></div>
        <div className="glass stat c3"><div className="n">g=406</div><div className="l">top rung · N=30</div></div>
        <div className="glass stat c4"><div className="n">10⁻⁷¹</div><div className="l">deep-precision record V9</div></div>
        <div className="glass stat c5"><div className="n">11/11</div><div className="l">certificates A–K accepted</div></div>
      </div>
      <div className="dash-grid">
        <div className="glass plot-card">
          <h3>The genus ladder — g(N) = (N−1)(N−2)/2</h3>
          <div ref={genusRef} />
          <p className="note">The step jump of complexity is the visual thesis of the program:
          from the calibration torus (g=1) to the cyclotomic flagship N=30 (g=406).</p>
        </div>
        <div className="glass plot-card">
          <h3>The SNF spectra of the rungs</h3>
          <div ref={snfRef} />
          <p className="note">Smith normal forms — T22: N=7 (1,7⁵)/7⁵ · N=9 (3,3,3,9,9,9)/3⁹ ·
          N=11 (1,11⁹)/11⁹ · N=15/30 (1,1,5,5,15⁵... /1125²) — certificate H bit-for-bit.</p>
        </div>
        <div className="glass plot-card" style={{ gridColumn: '1 / -1' }}>
          <h3>Protocol residuals vs contract thresholds (V1–V9)</h3>
          <div ref={residRef} />
          <p className="note">Each check carries an explicit threshold chosen 2–3 orders above the
          observed residual — the margin is part of the contract. V3 is exact (0.0, shown at floor);
          V9 reaches 1.7·10⁻⁷¹ at dps=70.</p>
        </div>
      </div>
    </div>
  );
}

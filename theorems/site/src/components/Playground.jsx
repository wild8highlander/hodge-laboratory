import React, { useEffect, useMemo, useRef, useState } from 'react';
import Plotly from 'plotly.js-dist-min';
import Formula from './Formula.jsx';

/* Lanczos gamma approximation (g=7, n=9) — enough for live display precision. */
const G = 7;
const C = [0.99999999999980993, 676.5203681218851, -1259.1392167224028,
  771.32342877765313, -176.61502916214059, 12.507343278686905,
  -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7];
function gamma(z) {
  if (z < 0.5) return Math.PI / (Math.sin(Math.PI * z) * gamma(1 - z));
  z -= 1;
  let x = C[0];
  for (let i = 1; i < G + 2; i++) x += C[i] / (z + i);
  const t = z + G + 0.5;
  return Math.sqrt(2 * Math.PI) * Math.pow(t, z + 0.5) * Math.exp(-t) * x;
}

/**
 * Playground — live parameters of the pipeline: pick N, a, b and watch the
 * genus, the spin phase, the braking and the closed period Ω(a,b) respond.
 */
export default function Playground() {
  const [N, setN] = useState(15);
  const [a, setA] = useState(1);
  const [b, setB] = useState(2);
  const plotRef = useRef(null);

  const maxA = N - 2, maxB = N - 1 - a;
  const aC = Math.min(a, maxA), bC = Math.min(b, maxB);

  const g = ((N - 1) * (N - 2)) / 2;
  const delta = Math.PI / N;
  const gammaBrake = Math.pow(delta, 4);
  const deltaEff = Math.pow(delta, 5);
  const Omega = gamma(aC / N) * gamma(bC / N) / gamma((aC + bC) / N);
  const phase = ((aC + bC) * 360 / N);   // r = s = 1 → arg P = 2π(a+b)/N

  useEffect(() => {
    const Ns = [], gs = [];
    for (let n = 4; n <= 30; n++) { Ns.push(n); gs.push(((n - 1) * (n - 2)) / 2); }
    Plotly.newPlot(plotRef.current, [{
      type: 'bar', x: Ns, y: gs,
      marker: { color: Ns.map((n) => n === N ? '#38bdf8' : 'rgba(148,163,184,0.4)') },
      hovertemplate: 'N = %{x}<br>g = %{y}<extra></extra>',
    }], {
      paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
      font: { color: '#94a3b8', family: 'Inter, system-ui, sans-serif', size: 12 },
      margin: { l: 48, r: 12, t: 8, b: 36 },
      xaxis: { gridcolor: 'rgba(148,163,184,0.12)', title: { text: 'N', font: { size: 11 } }, dtick: 2 },
      yaxis: { gridcolor: 'rgba(148,163,184,0.12)', title: { text: 'g(N)', font: { size: 11 } } },
      showlegend: false,
    }, { responsive: true, displaylogo: false });
    return () => Plotly.purge(plotRef.current);
  }, [N]);

  const fmt = (x, d = 10) => x.toPrecision(d);

  return (
    <div className="play-grid">
      <div className="glass controls">
        <div className="ctrl">
          <label>rotation order N <b>{N}</b></label>
          <input type="range" min="4" max="30" step="1" value={N}
                 onChange={(e) => { setN(+e.target.value); setA(1); setB(2); }} />
        </div>
        <div className="ctrl">
          <label>character a <b>{aC}</b></label>
          <input type="range" min="1" max={maxA} step="1" value={aC}
                 onChange={(e) => setA(+e.target.value)} />
        </div>
        <div className="ctrl">
          <label>character b <b>{bC}</b></label>
          <input type="range" min="1" max={maxB} step="1" value={bC}
                 onChange={(e) => setB(+e.target.value)} />
        </div>
        <div className="readouts">
          <div className="readout"><div className="k">genus</div><div className="v">g = {g}</div></div>
          <div className="readout"><div className="k">spin phase</div><div className="v">δ = {fmt(delta, 6)}</div></div>
          <div className="readout"><div className="k">braking γ = δ⁴</div><div className="v">{fmt(gammaBrake, 6)}</div></div>
          <div className="readout"><div className="k">effective δ⁵</div><div className="v">{fmt(deltaEff, 6)}</div></div>
          <div className="readout wide">
            <div className="k">closed period Ω(a,b)</div>
            <div className="v">Ω({aC},{bC}) = {Omega > 1e6 ? Omega.toExponential(6) : fmt(Omega, 8)}</div>
          </div>
          <div className="readout wide">
            <div className="k">phase of P (r=s=1)</div>
            <div className="v">{phase.toFixed(2)}° <small>= 2π({aC}+{bC})/{N}</small></div>
          </div>
        </div>
      </div>
      <div className="glass plot-card" style={{ padding: '20px 16px 10px' }}>
        <h3>The genus ladder — live at N = {N}</h3>
        <div ref={plotRef} />
        <div style={{ margin: '10px 16px 6px' }}>
          <Formula display tex={String.raw`\Omega_{a,b}=\frac{\Gamma(a/N)\,\Gamma(b/N)}{\Gamma\!\left(\tfrac{a+b}{N}\right)},\qquad P=\frac{1}{N}\,\zeta^{\,a+b}\,\Omega_{a,b}`} />
          <p className="note" style={{ color: 'var(--text-faint)', fontSize: 12.5, marginTop: 10 }}>
            The same identities the laboratory verifies at 35–70 digits: the closed Gamma form
            against tanh-sinh quadratures at relative deviation ~10⁻³⁶ (V2), the exact phase law
            (V3), μ<sub>N</sub>×μ<sub>N</sub>-equivariance (V4) and the reflection ladder (V6).
          </p>
        </div>
      </div>
    </div>
  );
}

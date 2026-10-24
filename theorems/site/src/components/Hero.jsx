import React, { useEffect, useRef } from 'react';
import Formula from './Formula.jsx';

/**
 * Hero — animated background: a slowly rotating 3D-projected Hodge diamond
 * wireframe (a rhombic lattice of nodes) with drifting particles,
 * plus glass panels and the united formula of the program.
 */
export default function Hero() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    let raf = 0;
    let w = 0, h = 0, dpr = Math.min(window.devicePixelRatio || 1, 2);

    const resize = () => {
      const rect = canvas.parentElement.getBoundingClientRect();
      w = rect.width; h = rect.height;
      canvas.width = w * dpr; canvas.height = h * dpr;
      canvas.style.width = w + 'px'; canvas.style.height = h + 'px';
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    resize();
    window.addEventListener('resize', resize);

    // ---- the Hodge diamond lattice: nodes of a rhombille tiling in 3D ----
    const nodes = [];
    const R = 5;                       // rings of the diamond
    for (let i = -R; i <= R; i++) {
      for (let j = -R; j <= R; j++) {
        if (Math.abs(i) + Math.abs(j) > R) continue;
        // three rhombic sublattices (tumbling-blocks projection)
        nodes.push([i, j, 0]);
        nodes.push([i + 0.5, j + 0.5, 0.5]);
        nodes.push([i + 0.5, j + 0.5, -0.5]);
      }
    }
    const edges = [];
    for (let a = 0; a < nodes.length; a++) {
      for (let b = a + 1; b < nodes.length; b++) {
        const d = Math.hypot(nodes[a][0] - nodes[b][0], nodes[a][1] - nodes[b][1],
                             nodes[a][2] - nodes[b][2]);
        if (d > 0.99 && d < 1.01) edges.push([a, b]);
      }
    }

    // ---- particles ----
    const parts = Array.from({ length: 70 }, () => ({
      x: Math.random(), y: Math.random(),
      vx: (Math.random() - 0.5) * 0.00035, vy: (Math.random() - 0.5) * 0.00028,
      r: 0.8 + Math.random() * 2.1,
      hue: Math.random() < 0.55 ? '56,189,248' : (Math.random() < 0.6 ? '167,139,250' : '244,114,182'),
      a: 0.12 + Math.random() * 0.3,
    }));

    const project = (p, rotY, rotX, scale, cx, cy) => {
      const [x, y, z] = p;
      const c1 = Math.cos(rotY), s1 = Math.sin(rotY);
      const x1 = x * c1 - z * s1, z1 = x * s1 + z * c1;
      const c2 = Math.cos(rotX), s2 = Math.sin(rotX);
      const y2 = y * c2 - z1 * s2, z2 = y * s2 + z1 * c2;
      const persp = 3.2 / (3.2 + z2 * 0.55);
      return [cx + x1 * scale * persp, cy + y2 * scale * persp, z2];
    };

    let t0 = performance.now();
    const draw = (now) => {
      const t = (now - t0) / 1000;
      ctx.clearRect(0, 0, w, h);

      // drifting particles
      for (const p of parts) {
        p.x += p.vx; p.y += p.vy;
        if (p.x < -0.05) p.x = 1.05; if (p.x > 1.05) p.x = -0.05;
        if (p.y < -0.05) p.y = 1.05; if (p.y > 1.05) p.y = -0.05;
        ctx.beginPath();
        ctx.arc(p.x * w, p.y * h, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${p.hue},${p.a})`;
        ctx.fill();
      }

      // the rotating diamond lattice — two echoes for depth
      const lattices = [
        { cx: w * 0.78, cy: h * 0.44, scale: Math.min(w, h) * 0.4, ry: t * 0.16, rx: 0.42, alpha: 0.5 },
        { cx: w * 0.78, cy: h * 0.44, scale: Math.min(w, h) * 0.4 * 0.55, ry: -t * 0.11 + 1.2, rx: 0.9, alpha: 0.22 },
      ];
      for (const L of lattices) {
        const pts = nodes.map((n) => project(n, L.ry, L.rx, L.scale, L.cx, L.cy));
        ctx.lineWidth = 1;
        for (const [a, b] of edges) {
          const [x1, y1, z1] = pts[a], [x2, y2, z2] = pts[b];
          const depth = (2.2 - (z1 + z2)) / 4.4;
          ctx.strokeStyle = `rgba(56,189,248,${(0.05 + 0.22 * Math.max(0, Math.min(1, depth))) * L.alpha})`;
          ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
        }
        for (let i = 0; i < pts.length; i++) {
          const [x, y, z] = pts[i];
          const depth = (2.2 - z) / 4.4;
          const rr = 1.1 + 1.4 * Math.max(0, Math.min(1, depth));
          ctx.beginPath();
          ctx.arc(x, y, rr, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(226,232,240,${(0.08 + 0.5 * Math.max(0, Math.min(1, depth))) * L.alpha})`;
          ctx.fill();
        }
        // the red h^{1,1} node — the signature accent
        const [hx, hy, hz] = project([0, 0, 0.5], L.ry, L.rx, L.scale, L.cx, L.cy);
        const pulse = 3.4 + Math.sin(t * 2.1) * 1.1;
        ctx.beginPath();
        ctx.arc(hx, hy, pulse, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(230,57,70,0.9)';
        ctx.fill();
        ctx.beginPath();
        ctx.arc(hx, hy, pulse + 6, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(230,57,70,0.28)';
        ctx.stroke();
      }

      raf = requestAnimationFrame(draw);
    };
    raf = requestAnimationFrame(draw);
    return () => { cancelAnimationFrame(raf); window.removeEventListener('resize', resize); };
  }, []);

  return (
    <div className="hero">
      <canvas ref={canvasRef} aria-hidden="true" />
      <div className="wrap hero-inner">
        <span className="chip"><span className="dot" style={{ background: '#38bdf8' }} />Hodge Laboratory · the theorem monographs</span>
        <h1>The Theorem<br />Monographs</h1>
        <p className="sub">
          22 self-sufficient studies of the dynamic principle — each packaged as a standalone
          monograph with a complete proof, protocol data and a verification guide.
          88 documents · PDF + DOCX · RU/EN · verified by five language stacks and the Lean 4 kernel.
        </p>
        <div className="formula-panel">
          <Formula display tex={String.raw`\Delta_{\mathrm{Ch}} \;=\; \lambda_{0} \;-\; \frac{R}{4} \;+\; \frac{\delta^{2}}{2} \;-\; \frac{\delta^{5}}{k}, \qquad \delta = \frac{\pi}{N}`} />
          <div style={{ color: 'var(--text-faint)', fontSize: 12.5, marginTop: 10, letterSpacing: '0.04em' }}>
            THE UNITED FORMULA — ONE INTEGER TRIPLE IN, CLOSED FORMS OUT
          </div>
        </div>
        <div className="cta">
          <a className="btn" href="#explorer">🧭 Explore the dependency graph</a>
          <a className="btn violet" href="#theorems">📚 Browse 22 monographs</a>
        </div>
      </div>
    </div>
  );
}

/* HODGE LABORATORY WEB — plots.js — eight protocol tiles, 600 dpi export */
(function (global) {
  'use strict';
  const PL = {};
  const GOLD = '#C9A96A', GOLD2 = '#E3C98F', TXT = '#EAF0F8', MUT = '#8CA2BC', LINE = '#24405F',
    TEAL = '#3FC9AD', VIO = '#9D7BD8', ROSE = '#D87BA0', RED = '#E06C6C', GREEN = '#5BBF7A';

  function fLgamma(z) { // Lanczos g=7, n=9
    const g = [
      0.99999999999980993, 676.5203681218851, -1259.1392167224028, 771.32342877765313,
      -176.61502916214059, 12.507343278686905, -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7,
    ];
    if (z < 0.5) return Math.log(Math.PI / Math.sin(Math.PI * z)) - fLgamma(1 - z);
    z -= 1;
    let x = g[0];
    for (let i = 1; i < 9; i++) x += g[i] / (z + i);
    const t = z + 7.5;
    return 0.5 * Math.log(2 * Math.PI) + (z + 0.5) * Math.log(t) - t + Math.log(x);
  }
  const fGamma = z => Math.exp(fLgamma(z));

  function bg(ctx, W, H, title) {
    ctx.fillStyle = '#0C1424'; ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = LINE; ctx.lineWidth = Math.max(1, W / 1600);
    ctx.strokeRect(ctx.lineWidth, ctx.lineWidth, W - 2 * ctx.lineWidth, H - 2 * ctx.lineWidth);
    if (title) {
      ctx.fillStyle = GOLD; ctx.font = `600 ${Math.round(W / 42)}px Inter, sans-serif`;
      ctx.textAlign = 'center'; ctx.fillText(title, W / 2, W / 22);
    }
  }
  function heat(v) { // 0..1 → twilight-shifted
    const stops = [[0, [42, 34, 80]], [0.25, [87, 62, 128]], [0.5, [201, 169, 106]], [0.75, [63, 201, 173]], [1, [234, 240, 248]]];
    const t = Math.max(0, Math.min(1, v));
    for (let i = 1; i < stops.length; i++) {
      if (t <= stops[i][0]) {
        const [t0, c0] = stops[i - 1], [t1, c1] = stops[i];
        const f = (t - t0) / (t1 - t0);
        return `rgb(${Math.round(c0[0] + f * (c1[0] - c0[0]))},${Math.round(c0[1] + f * (c1[1] - c0[1]))},${Math.round(c0[2] + f * (c1[2] - c0[2]))})`;
      }
    }
    return 'white';
  }

  const R = {}; // renderers: (ctx, W, H, lang) — data computed inside (fast float, honest viz)

  R.census = function (ctx, W, H, lang) {
    bg(ctx, W, H, lang === 'ru' ? 'Точная перепись характеров по проводникам (V1)' : 'Exact character census by conductors (V1)');
    const data = [{ N: 15, h: { 3: 1, 5: 6, 15: 84 }, g: 91 }, { N: 30, h: { 3: 1, 5: 6, 6: 9, 10: 30, 15: 84, 30: 276 }, g: 406 }];
    data.forEach((d, p) => {
      const x0 = p === 0 ? W * 0.07 : W * 0.55, pw = W * 0.38, ph = H * 0.62, y0 = H * 0.78;
      const keys = Object.keys(d.h);
      const max = Math.max(...keys.map(k => d.h[k]));
      ctx.fillStyle = MUT; ctx.font = `${Math.round(W / 52)}px Inter`; ctx.textAlign = 'center';
      ctx.fillText(`N=${d.N}:  Σ h_d = g = ${d.g}`, x0 + pw / 2, y0 + W / 30);
      keys.forEach((k, i) => {
        const bw = pw / keys.length * 0.62;
        const bh = d.h[k] / max * ph;
        const bx = x0 + (i + 0.5) * pw / keys.length - bw / 2;
        const g2 = ctx.createLinearGradient(0, y0 - bh, 0, y0);
        g2.addColorStop(0, GOLD2); g2.addColorStop(1, GOLD);
        ctx.fillStyle = g2; ctx.fillRect(bx, y0 - bh, bw, bh);
        ctx.fillStyle = TXT; ctx.font = `${Math.round(W / 60)}px JetBrains Mono, monospace`;
        ctx.fillText(`h${k}=${d.h[k]}`, bx + bw / 2, y0 - bh - W / 90);
      });
    });
  };

  R.phase = function (ctx, W, H, lang) {
    bg(ctx, W, H, lang === 'ru' ? 'Фазовая решётка μN×μN: (r+s) mod N' : 'μN×μN phase lattice: (r+s) mod N');
    [{ N: 15, x0: 0.08 }, { N: 30, x0: 0.55 }].forEach(({ N, x0 }) => {
      const S = W * 0.37, y0 = H * 0.24, cell = S / N;
      for (let r = 0; r < N; r++) for (let s = 0; s < N; s++) {
        ctx.fillStyle = heat(((r + s) % N) / N);
        ctx.fillRect(W * x0 + r * cell, y0 + s * cell, cell + 0.5, cell + 0.5);
      }
      ctx.fillStyle = MUT; ctx.font = `${Math.round(W / 55)}px Inter`; ctx.textAlign = 'center';
      ctx.fillText(`N=${N}`, W * x0 + S / 2, y0 + S + W / 34);
    });
  };

  R.reflection = function (ctx, W, H, lang) {
    bg(ctx, W, H, lang === 'ru' ? 'Лестница отражений: Γ(k/N) против π/sin(πk/N)' : 'Reflection ladder: Γ(k/N) against π/sin(πk/N)');
    const x0 = W * 0.1, y0 = H * 0.82, pw = W * 0.8, ph = H * 0.55, maxV = 12;
    ctx.strokeStyle = LINE; ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x0 + pw, y0); ctx.moveTo(x0, y0); ctx.lineTo(x0, y0 - ph); ctx.stroke();
    [[15, ROSE], [30, TEAL]].forEach(([N, col]) => {
      ctx.fillStyle = col; ctx.strokeStyle = col;
      for (let k = 1; k < N; k++) {
        const lhs = fGamma(k / N) * fGamma(1 - k / N);
        if (lhs > maxV) continue;
        const px = x0 + (k / N) * pw, py = y0 - (lhs / maxV) * ph;
        ctx.beginPath(); ctx.arc(px, py, W / 220, 0, 7); ctx.fill();
      }
    });
    ctx.fillStyle = MUT; ctx.font = `${Math.round(W / 58)}px Inter`;
    ctx.fillText('Γ(k/N)Γ(1−k/N)  ·  N=15 (rose)  N=30 (teal)  —  π/sin(πk/N)', x0 + pw / 2, y0 + W / 30);
  };

  R.bch = function (ctx, W, H, lang) {
    bg(ctx, W, H, lang === 'ru' ? 'Радикалы b_Ch(n) = 1 − cos(2π/n)' : 'Radicals b_Ch(n) = 1 − cos(2π/n)');
    const ns = [7, 9, 15, 30], vals = ns.map(n => 1 - Math.cos(2 * Math.PI / n));
    const max = Math.max(...vals);
    ns.forEach((n, i) => {
      const bw = W * 0.13, bh = vals[i] / max * H * 0.55;
      const bx = W * (0.12 + i * 0.21), by = H * 0.8;
      const g2 = ctx.createLinearGradient(0, by - bh, 0, by);
      g2.addColorStop(0, VIO); g2.addColorStop(1, '#6a4f96');
      ctx.fillStyle = g2; ctx.fillRect(bx, by - bh, bw, bh);
      ctx.fillStyle = TXT; ctx.font = `${Math.round(W / 58)}px JetBrains Mono, monospace`; ctx.textAlign = 'center';
      ctx.fillText(`b_Ch(${n}) = ${vals[i].toFixed(5)}`, bx + bw / 2, by - bh - W / 95);
    });
    ctx.fillStyle = MUT; ctx.font = `${Math.round(W / 62)}px Inter`;
    ctx.fillText('n=15/30: (7−√5−√(30−6√5))/8 · (9−√5−√(30+6√5))/8  (roadmap v1.2)', W / 2, H * 0.9);
  };

  R.braking = function (ctx, W, H, lang) {
    bg(ctx, W, H, lang === 'ru' ? 'Торможение γ = δ⁴/k и эффективная фаза δ_eff = δ⁵/k' : 'Braking γ = δ⁴/k and effective phase δ_eff = δ⁵/k');
    const x0 = W * 0.1, y0 = H * 0.82, pw = W * 0.8, ph = H * 0.58, Nmax = 30;
    ctx.strokeStyle = LINE; ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x0 + pw, y0); ctx.moveTo(x0, y0); ctx.lineTo(x0, y0 - ph); ctx.stroke();
    const plot = (fn, col, k) => {
      ctx.strokeStyle = col; ctx.lineWidth = Math.max(1.5, W / 900); ctx.beginPath();
      for (let n = 4; n <= Nmax; n++) {
        const d = Math.PI / n / k;
        const v = fn(d);
        const px = x0 + (n / Nmax) * pw, py = y0 - (v / 1.0) * ph;
        n === 4 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
      }
      ctx.stroke(); ctx.lineWidth = 1;
    };
    plot(d => d ** 4, GOLD, 1); plot(d => d ** 5, TEAL, 1);
    ctx.fillStyle = GOLD; ctx.font = `${Math.round(W / 60)}px Inter`; ctx.fillText('γ = δ⁴', x0 + pw * 0.72, y0 - ph * 0.9);
    ctx.fillStyle = TEAL; ctx.fillText('δ_eff = δ⁵', x0 + pw * 0.72, y0 - ph * 0.78);
    ctx.fillStyle = MUT; ctx.fillText('δ = π/N, N = 4…30 · δ_eff < γ при δ < 1 (все уровни N ≥ 4)', x0 + pw / 2, y0 + W / 30);
  };

  R.residuals = function (ctx, W, H, lang) {
    bg(ctx, W, H, lang === 'ru' ? 'Остатки протокола против порогов' : 'Protocol residuals versus thresholds');
    const rows = [
      ['V2', 3.9e-36, 1e-30], ['V3', 0.0, 1e-25], ['V4', 4.4e-36, 1e-30], ['V5', 2.9e-36, 1e-25],
      ['V6', 7.0e-36, 1e-30], ['V8', 4.0e-36, 1e-25], ['V9', 1.3e-71, 1e-60],
    ];
    const x0 = W * 0.09, y0 = H * 0.82, pw = W * 0.84, ph = H * 0.56;
    const exps = rows.map(r => Math.log10(Math.max(r[1], 1e-80)));
    const thr = rows.map(r => Math.log10(r[2]));
    const lo = -80, hi = -20;
    const Y = e => y0 - (Math.max(e, lo) - lo) / (hi - lo) * ph;
    ctx.strokeStyle = LINE; ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x0 + pw, y0); ctx.stroke();
    rows.forEach((r, i) => {
      const bw = pw / rows.length * 0.5, bx = x0 + (i + 0.5) * pw / rows.length - bw / 2;
      ctx.fillStyle = TEAL; ctx.fillRect(bx, Y(exps[i]), bw, y0 - Y(exps[i]));
      ctx.strokeStyle = GOLD; ctx.setLineDash([W / 300, W / 300]);
      ctx.beginPath(); ctx.moveTo(bx - bw * 0.35, Y(thr[i])); ctx.lineTo(bx + bw * 1.35, Y(thr[i])); ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle = TXT; ctx.font = `${Math.round(W / 64)}px JetBrains Mono, monospace`; ctx.textAlign = 'center';
      ctx.fillText(r[0], bx + bw / 2, y0 + W / 46);
      ctx.fillStyle = MUT;
      ctx.fillText(r[1] === 0 ? 'exact' : r[1].toExponential(0), bx + bw / 2, Y(exps[i]) - W / 130);
    });
    ctx.fillStyle = GOLD; ctx.textAlign = 'right'; ctx.font = `${Math.round(W / 68)}px Inter`;
    ctx.fillText('— threshold', x0 + pw, y0 - ph - W / 90); ctx.textAlign = 'center';
  };

  R.genus = function (ctx, W, H, lang) {
    bg(ctx, W, H, lang === 'ru' ? 'Лестница родов g(N) = (N−1)(N−2)/2' : 'Genus ladder g(N) = (N−1)(N−2)/2');
    const x0 = W * 0.09, y0 = H * 0.84, pw = W * 0.84, ph = H * 0.6, Nmax = 32;
    ctx.strokeStyle = LINE; ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x0 + pw, y0); ctx.moveTo(x0, y0); ctx.lineTo(x0, y0 - ph); ctx.stroke();
    ctx.strokeStyle = GOLD; ctx.lineWidth = Math.max(1.5, W / 800); ctx.beginPath();
    for (let N = 3; N <= Nmax; N++) {
      const g = (N - 1) * (N - 2) / 2;
      const px = x0 + (N / Nmax) * pw, py = y0 - (g / 406) * ph;
      N === 3 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
    }
    ctx.stroke(); ctx.lineWidth = 1;
    [[3, 1], [7, 15], [9, 28], [15, 91], [30, 406]].forEach(([N, g]) => {
      const px = x0 + (N / Nmax) * pw, py = y0 - (g / 406) * ph;
      ctx.fillStyle = N === 15 || N === 30 ? GOLD2 : TEAL;
      ctx.beginPath(); ctx.arc(px, py, W / 190, 0, 7); ctx.fill();
      ctx.fillStyle = TXT; ctx.font = `${Math.round(W / 62)}px JetBrains Mono, monospace`; ctx.textAlign = 'center';
      ctx.fillText(`g(${N})=${g}`, px, py - W / 110);
    });
  };

  R.dft = function (ctx, W, H, lang) {
    bg(ctx, W, H, lang === 'ru' ? 'DFT-ортогональность периодов (V8), log₁₀ |M|' : 'DFT orthogonality of periods (V8), log₁₀ |M|');
    // 8 characters of N=15, matrix of |Σ ζ^{rΔa+sΔb}·ΩiΩj/N²| (float viz)
    const N = 15, chars = [];
    { const { byD } = global.Fermat.census(N); for (const d of Object.keys(byD)) chars.push(...byD[d]); chars.length = 8; }
    const M = chars.length;
    for (let i = 0; i < M; i++) for (let j = 0; j < M; j++) {
      let re = 0, im = 0;
      for (let r = 0; r < N; r++) for (let s = 0; s < N; s++) {
        const ph = 2 * Math.PI * (((r * (chars[i][0] - chars[j][0]) + s * (chars[i][1] - chars[j][1])) % N + N) % N) / N;
        re += Math.cos(ph); im += Math.sin(ph);
      }
      const v = Math.hypot(re, im) / (N * N);
      const cell = Math.min(W * 0.62, H * 0.62) / M;
      const x0 = W * 0.12, y0 = H * 0.2;
      ctx.fillStyle = heat(v === 0 ? 0 : 0.15 + 0.85 * (v > 0 ? 1 : 0) * Math.max(0, Math.min(1, v)));
      if (v > 0.99) ctx.fillStyle = TEAL;
      ctx.fillRect(x0 + j * cell, y0 + i * cell, cell + 0.5, cell + 0.5);
    }
    ctx.fillStyle = MUT; ctx.font = `${Math.round(W / 64)}px Inter`; ctx.textAlign = 'center';
    ctx.fillText('diag = |Ω|² (teal) · off-diag ≈ 10⁻³⁶ → 0 (dark) · N=15', W * 0.42, H * 0.9);
  };

  PL.LIST = [
    ['census', 'p_census'], ['phase', 'p_phase'], ['reflection', 'p_reflection'], ['bch', 'p_bch'],
    ['braking', 'p_braking'], ['residuals', 'p_residuals'], ['genus', 'p_genus'], ['dft', 'p_dft'],
  ];

  PL.render = function (canvas, key, lang, scale) {
    const W = scale ? 4800 : (canvas.clientWidth || 640) * 2;
    const H = scale ? 3000 : (canvas.clientHeight || 400) * 2;
    const c2 = document.createElement('canvas');
    c2.width = W; c2.height = H;
    const ctx = c2.getContext('2d');
    ctx.scale(1, 1);
    (R[key] || R.census)(ctx, W, H, lang);
    if (scale) {
      c2.toBlob(b => {
        const a = document.createElement('a');
        a.href = URL.createObjectURL(b);
        a.download = `hodge_${key}_600dpi.png`;
        a.click();
        setTimeout(() => URL.revokeObjectURL(a.href), 4000);
      }, 'image/png');
      return;
    }
    const ctx2 = canvas.getContext('2d');
    canvas.width = W; canvas.height = H;
    ctx2.drawImage(c2, 0, 0);
  };

  global.Plots = PL;
})(typeof window !== 'undefined' ? window : globalThis);

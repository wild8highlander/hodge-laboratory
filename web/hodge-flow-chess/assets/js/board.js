/* ════════════════════════════════════════════════════════════════════
   Hodge Flow — Шахматная Лаборатория / Chess Flow Laboratory
   board.js — canvas rendering: chessboard heat cells, trail, μ₄ phase
   marker with corner ticks, discovery pulses, Klein 7-ring; formula
   grid heatmap with diagonal scan; tower spectrum & Gram charts.
   All draw functions are resolution-independent: draw(ctx, w, h,
   scale, theme, ...) renders in logical coordinates w×h multiplied by
   `scale` — the same code serves the live canvas and 600 dpi exports.
   window.HFBoard
   ════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  const THEME = {
    bg: '#0A1120', panel: '#0E1830', border: '#24405F',
    text: '#EAF0F8', muted: '#8CA2BC',
    gold: '#C9A96A', goldB: '#E3C98F', violet: '#9D7BD8',
    teal: '#3FC9AD', green: '#5BBF7A', red: '#E06C6C', rose: '#D87BA0',
  };
  const PHASE_COLORS = ['#9D7BD8', '#E3C98F', '#3FC9AD', '#D87BA0']; // 1, i, −1, −i
  const MOD7 = ['#C9A96A', '#3FC9AD', '#9D7BD8', '#D87BA0', '#5BBF7A', '#E3C98F', '#8CA2BC'];

  const GOLD_RGB = [201, 169, 106];
  const TEAL_RGB = [63, 201, 173];
  const PANEL_RGB = [14, 24, 48];

  function lerp3(a, b, t) {
    return [Math.round(a[0] + (b[0] - a[0]) * t), Math.round(a[1] + (b[1] - a[1]) * t), Math.round(a[2] + (b[2] - a[2]) * t)];
  }
  function rgb(c, alpha) {
    return alpha === undefined ? 'rgb(' + c[0] + ',' + c[1] + ',' + c[2] + ')'
      : 'rgba(' + c[0] + ',' + c[1] + ',' + c[2] + ',' + alpha + ')';
  }
  function heatColor(t) { return lerp3(GOLD_RGB, TEAL_RGB, Math.max(0, Math.min(1, t))); }

  /* mix a heat color into the panel background so unvisited cells stay dark */
  function cellColor(count, maxVisits, kleinTint) {
    if (count === 0) return kleinTint || PANEL_RGB;
    const v = Math.min(1, count / Math.max(6, maxVisits));
    const c = heatColor(v);
    const mix = 0.45 + 0.55 * v;
    return [
      Math.round(PANEL_RGB[0] + (c[0] - PANEL_RGB[0]) * mix),
      Math.round(PANEL_RGB[1] + (c[1] - PANEL_RGB[1]) * mix),
      Math.round(PANEL_RGB[2] + (c[2] - PANEL_RGB[2]) * mix),
    ];
  }

  /* ══════════════════════════════════════════════════════════════════
     MAIN BOARD
     draw(ctx, w, h, scale, snap, opts)
       ctx    — 2d context (transform is set here)
       w,h    — logical canvas size
       scale  — device/ export multiplier
       snap   — flow snapshot {W,H,counts,maxVisits,trail,pulses,px,py,
                 phase,phase7,layer,...}
       opts   — {now, caption, captionSub, showDpi, fontScale}
     ══════════════════════════════════════════════════════════════════ */
  const imgCache = { canvas: null, W: 0, H: 0 };

  function draw(ctx, w, h, scale, snap, opts) {
    opts = opts || {};
    ctx.setTransform(scale, 0, 0, scale, 0, 0);
    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = THEME.bg;
    ctx.fillRect(0, 0, w, h);

    let top = 0;
    const fs = opts.fontScale || 1;
    if (opts.caption) {
      top = 58 * fs;
      drawCaption(ctx, w, opts, fs);
    }

    const W = snap.W, H = snap.H;
    const availW = w - 24, availH = h - top - 24;
    const cs = Math.min(availW / W, availH / H);
    const bw = cs * W, bh = cs * H;
    const bx = (w - bw) / 2, by = top + (availH - bh) / 2 + 12;

    // ── cells ──
    const klein = snap.layer === 'klein';
    if (W * H > 24000) {
      // ImageData path for large boards
      if (!imgCache.canvas || imgCache.W !== W || imgCache.H !== H) {
        imgCache.canvas = document.createElement('canvas');
        imgCache.canvas.width = W; imgCache.canvas.height = H;
        imgCache.W = W; imgCache.H = H;
      }
      const off = imgCache.canvas;
      const octx = off.getContext('2d');
      const img = octx.createImageData(W, H);
      const d = img.data;
      let p = 0;
      for (let y = 0; y < H; y++) {
        for (let x = 0; x < W; x++) {
          const count = snap.counts[y * W + x];
          let tint = null;
          if (klein && count === 0) {
            tint = lerp3(PANEL_RGB, hex2rgb(MOD7[(x + y) % 7]), 0.16);
          }
          const c = cellColor(count, snap.maxVisits, tint);
          d[p] = c[0]; d[p + 1] = c[1]; d[p + 2] = c[2]; d[p + 3] = 255;
          p += 4;
        }
      }
      octx.putImageData(img, 0, 0);
      ctx.imageSmoothingEnabled = false;
      ctx.drawImage(off, bx, by, bw, bh);
      ctx.imageSmoothingEnabled = true;
    } else {
      for (let y = 0; y < H; y++) {
        for (let x = 0; x < W; x++) {
          const count = snap.counts[y * W + x];
          let tint = null;
          if (klein && count === 0) {
            tint = lerp3(PANEL_RGB, hex2rgb(MOD7[(x + y) % 7]), 0.16);
          }
          ctx.fillStyle = rgb(cellColor(count, snap.maxVisits, tint));
          // screen y flipped: math y up
          ctx.fillRect(bx + x * cs, by + (H - 1 - y) * cs, cs + 0.5, cs + 0.5);
        }
      }
    }

    // grid lines
    if (cs >= 7) {
      ctx.strokeStyle = 'rgba(36,64,95,0.4)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      for (let x = 1; x < W; x++) { ctx.moveTo(bx + x * cs, by); ctx.lineTo(bx + x * cs, by + bh); }
      for (let y = 1; y < H; y++) { ctx.moveTo(bx, by + y * cs); ctx.lineTo(bx + bw, by + y * cs); }
      ctx.stroke();
    }

    // frame
    ctx.strokeStyle = THEME.border;
    ctx.lineWidth = 1.5;
    ctx.strokeRect(bx - 0.5, by - 0.5, bw + 1, bh + 1);

    const S = function (mx, my) { // math coords → screen
      return [bx + mx * cs, by + (H - my) * cs];
    };

    // ── trail ──
    const tr = snap.trail;
    if (tr && tr.length >= 4) {
      ctx.strokeStyle = 'rgba(201,169,106,0.45)';
      ctx.lineWidth = Math.max(1, cs * 0.12);
      ctx.lineJoin = 'round';
      ctx.lineCap = 'round';
      ctx.beginPath();
      const start = Math.max(0, tr.length - 4800);
      let pt = S(tr[start], tr[start + 1]);
      ctx.moveTo(pt[0], pt[1]);
      for (let i = start + 2; i < tr.length; i += 2) {
        pt = S(tr[i], tr[i + 1]);
        ctx.lineTo(pt[0], pt[1]);
      }
      ctx.stroke();
    }

    // ── discovery pulses ──
    const now = opts.now || 0;
    if (snap.pulses && snap.pulses.length) {
      for (let i = 0; i < snap.pulses.length; i++) {
        const pu = snap.pulses[i];
        const age = (now - pu.t0) / 650;
        if (age < 0 || age > 1) continue;
        const cx = pu.i % W, cy = (pu.i - cx) / W;
        const pt = S(cx + 0.5, cy + 0.5);
        ctx.strokeStyle = 'rgba(63,201,173,' + (0.85 * (1 - age)).toFixed(3) + ')';
        ctx.lineWidth = Math.max(1, cs * 0.1);
        ctx.beginPath();
        ctx.arc(pt[0], pt[1], Math.max(1.5, cs * (0.25 + 0.85 * age)), 0, 6.2832);
        ctx.stroke();
      }
    }

    // ── marker ──
    const mp = S(snap.px, snap.py);
    const R = Math.max(3, cs * 0.32);
    // glow
    const gl = ctx.createRadialGradient(mp[0], mp[1], 0, mp[0], mp[1], R * 4.2);
    gl.addColorStop(0, 'rgba(227,201,143,0.55)');
    gl.addColorStop(1, 'rgba(227,201,143,0)');
    ctx.fillStyle = gl;
    ctx.beginPath();
    ctx.arc(mp[0], mp[1], R * 4.2, 0, 6.2832);
    ctx.fill();
    // core
    ctx.fillStyle = THEME.text;
    ctx.beginPath();
    ctx.arc(mp[0], mp[1], R, 0, 6.2832);
    ctx.fill();
    ctx.strokeStyle = PHASE_COLORS[snap.phase & 3];
    ctx.lineWidth = Math.max(1.2, R * 0.28);
    ctx.beginPath();
    ctx.arc(mp[0], mp[1], R * 1.35, 0, 6.2832);
    ctx.stroke();
    // rotating glyph: square turned by phase·90°
    ctx.save();
    ctx.translate(mp[0], mp[1]);
    ctx.rotate((snap.phase & 3) * Math.PI / 2);
    ctx.strokeStyle = PHASE_COLORS[snap.phase & 3];
    ctx.lineWidth = Math.max(1, R * 0.22);
    const gs = R * 0.62;
    ctx.strokeRect(-gs, -gs, gs * 2, gs * 2);
    ctx.restore();
    // 4 phase corner ticks (μ₄ phases 1, i, −1, −i)
    for (let q = 0; q < 4; q++) {
      const ang = Math.PI / 4 + q * Math.PI / 2;
      const dist = R * 2.1;
      const tx = mp[0] + Math.cos(ang) * dist;
      const ty = mp[1] + Math.sin(ang) * dist;
      const active = (snap.phase & 3) === q;
      ctx.fillStyle = PHASE_COLORS[q];
      ctx.beginPath();
      ctx.arc(tx, ty, active ? R * 0.5 : R * 0.28, 0, 6.2832);
      ctx.fill();
      if (active) {
        ctx.strokeStyle = PHASE_COLORS[q];
        ctx.lineWidth = Math.max(1, R * 0.16);
        ctx.beginPath();
        ctx.arc(tx, ty, R * 0.85, 0, 6.2832);
        ctx.stroke();
      }
    }
    // Klein phase-7 ring
    if (klein) {
      const rr = R * 3.1;
      for (let s7 = 0; s7 < 7; s7++) {
        const a0 = -Math.PI / 2 + s7 * (6.2832 / 7);
        const a1 = a0 + (6.2832 / 7) * 0.74;
        ctx.strokeStyle = s7 === (snap.phase7 % 7) ? THEME.goldB : 'rgba(140,162,188,0.4)';
        ctx.lineWidth = Math.max(1.2, R * 0.26);
        ctx.beginPath();
        ctx.arc(mp[0], mp[1], rr, a0, a1);
        ctx.stroke();
      }
    }
  }

  function drawCaption(ctx, w, opts, fs) {
    ctx.fillStyle = THEME.gold;
    ctx.font = '700 ' + (26 * fs) + 'px "Playfair Display", Georgia, serif';
    ctx.textBaseline = 'alphabetic';
    ctx.fillText(opts.caption, 24, 30 * fs);
    if (opts.captionSub) {
      ctx.fillStyle = THEME.muted;
      ctx.font = '400 ' + (13 * fs) + 'px "JetBrains Mono", monospace';
      ctx.fillText(opts.captionSub, 24, 49 * fs);
    }
    if (opts.showDpi) {
      ctx.fillStyle = THEME.goldB;
      ctx.font = '600 ' + (12 * fs) + 'px "JetBrains Mono", monospace';
      ctx.textAlign = 'right';
      ctx.fillText('600 dpi · Ultra HD', w - 24, 30 * fs);
      ctx.textAlign = 'left';
    }
    ctx.strokeStyle = 'rgba(201,169,106,0.6)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(24, 56 * fs);
    ctx.lineTo(w - 24, 56 * fs);
    ctx.stroke();
  }

  function hex2rgb(hex) {
    return [parseInt(hex.slice(1, 3), 16), parseInt(hex.slice(3, 5), 16), parseInt(hex.slice(5, 7), 16)];
  }

  /* ══════════════════════════════════════════════════════════════════
     FORMULA GRID HEATMAP
     render(ctx, w, h, scale, job, scan, opts)
       job  — HFEngine.createFormulaJob result (after .done)
       scan — 0..1 diagonal reveal progress
     ══════════════════════════════════════════════════════════════════ */
  let fimgCanvas = null, fimgK = 0, fimgMode = '', fimgStamp = 0, fimgJob = null;

  function formulaColorTable(job) {
    // per (quadrant, spin) → [r,g,b] for mode A; per spin → [r,g,b] for B
    const N = job.N;
    if (job.mode === 'A') {
      const t = {};
      for (let q = 0; q < 4; q++) {
        const base = hex2rgb(PHASE_COLORS[q]);
        for (let s = 0; s < N; s++) {
          const v = N > 1 ? s / (N - 1) : 0.5;
          t[q + ':' + s] = lerp3(lerp3([10, 17, 32], base, 0.35), base, 0.35 + 0.65 * v);
        }
      }
      return t;
    }
    const arr = [];
    const vmin = job.vmin, vmax = job.vmax > job.vmin ? job.vmax : job.vmin + 1e-9;
    for (let s = 0; s < N; s++) {
      const V = job.lambda0 + job.beta * s;
      const t = (Math.abs(V) - Math.abs(vmin)) / Math.max(1e-9, Math.abs(vmax) - Math.abs(vmin));
      arr.push(lerp3(lerp3(PANEL_RGB, GOLD_RGB, 0.5), TEAL_RGB, Math.max(0, Math.min(1, t))));
    }
    return arr;
  }

  function buildFormulaImage(job, stamp) {
    if (fimgCanvas && fimgJob === job && fimgK === job.K && fimgMode === job.mode && fimgStamp === stamp) return fimgCanvas;
    const K = job.K;
    if (!fimgCanvas) fimgCanvas = document.createElement('canvas');
    if (fimgCanvas.width !== K || fimgCanvas.height !== K) {
      fimgCanvas.width = K; fimgCanvas.height = K;
    }
    fimgK = K; fimgMode = job.mode; fimgStamp = stamp; fimgJob = job;
    const octx = fimgCanvas.getContext('2d');
    const img = octx.createImageData(K, K);
    const d = img.data;
    const table = formulaColorTable(job);
    let p = 0;
    for (let r = 0; r < K; r++) {
      for (let s = 0; s < K; s++) {
        const i = r * K + s;
        let c;
        if (job.mode === 'A') {
          const q = job.qArr[i];
          c = (q === 4) ? [10, 17, 32] : table[q + ':' + job.sArr[i]];
        } else {
          c = table[job.sArr[i]];
        }
        d[p] = c[0]; d[p + 1] = c[1]; d[p + 2] = c[2]; d[p + 3] = 255;
        p += 4;
      }
    }
    octx.putImageData(img, 0, 0);
    return fimgCanvas;
  }

  function renderFormula(ctx, w, h, scale, job, scan, opts) {
    opts = opts || {};
    ctx.setTransform(scale, 0, 0, scale, 0, 0);
    ctx.fillStyle = THEME.bg;
    ctx.fillRect(0, 0, w, h);
    const fs = opts.fontScale || 1;
    let top = 0;
    if (opts.caption) { top = 58 * fs; drawCaption(ctx, w, opts, fs); }

    const K = job.K;
    const availW = w - 24, availH = h - top - (opts.legend ? 64 : 24);
    const size = Math.min(availW, availH);
    const bx = (w - size) / 2, by = top + 12;

    const img = buildFormulaImage(job, job.stamp || 0);
    ctx.save();
    ctx.beginPath();
    // staircase reveal: cells with (r + s) ≤ scan · 2(K−1)
    const lim = Math.max(0, Math.min(1, scan)) * 2 * (K - 1);
    ctx.moveTo(bx, by);
    const stepRows = Math.max(1, Math.floor(1024 / Math.max(1, K)));
    for (let r = 0; r < K; r += stepRows) {
      const sMax = Math.min(K, lim - r);
      if (sMax <= 0) break;
      const rr = Math.min(K, r + stepRows);
      ctx.lineTo(bx + Math.min(size, sMax / K * size), by + rr / K * size);
      ctx.lineTo(bx, by + rr / K * size);
    }
    ctx.closePath();
    ctx.clip();
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(img, bx, by, size, size);
    ctx.imageSmoothingEnabled = true;
    ctx.restore();

    if (K <= 64) {
      ctx.strokeStyle = 'rgba(36,64,95,0.35)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      for (let i = 1; i < K; i++) {
        const t = i / K * size;
        ctx.moveTo(bx + t, by); ctx.lineTo(bx + t, by + size);
        ctx.moveTo(bx, by + t); ctx.lineTo(bx + size, by + t);
      }
      ctx.stroke();
    }
    ctx.strokeStyle = THEME.border;
    ctx.lineWidth = 1.5;
    ctx.strokeRect(bx - 0.5, by - 0.5, size + 1, size + 1);

    // scan line
    if (scan > 0 && scan < 1) {
      const t = scan * 2 * size;
      ctx.strokeStyle = 'rgba(227,201,143,0.9)';
      ctx.lineWidth = 2;
      ctx.beginPath();
      if (t <= size) { ctx.moveTo(bx + t, by); ctx.lineTo(bx, by + t); }
      else { ctx.moveTo(bx + size, by + (t - size)); ctx.lineTo(bx + (t - size), by + size); }
      ctx.stroke();
    }

    if (opts.legend) {
      const ly = by + size + 18;
      const lw = Math.min(340, size);
      const lx = bx + (size - lw) / 2;
      const grad = ctx.createLinearGradient(lx, 0, lx + lw, 0);
      if (job.mode === 'A') {
        grad.addColorStop(0, PHASE_COLORS[0]);
        grad.addColorStop(0.33, PHASE_COLORS[1]);
        grad.addColorStop(0.66, PHASE_COLORS[2]);
        grad.addColorStop(1, PHASE_COLORS[3]);
      } else {
        grad.addColorStop(0, rgb(GOLD_RGB));
        grad.addColorStop(1, rgb(TEAL_RGB));
      }
      ctx.fillStyle = grad;
      ctx.fillRect(lx, ly, lw, 10);
      ctx.strokeStyle = THEME.border;
      ctx.strokeRect(lx, ly, lw, 10);
      ctx.fillStyle = THEME.muted;
      ctx.font = '400 11px "JetBrains Mono", monospace';
      ctx.textAlign = 'center';
      ctx.fillText(job.mode === 'A' ? (opts.legendQ || 'arg Δ · quadrants') : (opts.legendLow || 'low Δ'), lx, ly + 26);
      if (job.mode !== 'A') {
        ctx.fillText(opts.legendHigh || 'high Δ', lx + lw, ly + 26);
      }
      ctx.textAlign = 'left';
    }
  }

  /* ══════════════════════════════════════════════════════════════════
     TOWER SPECTRUM CHART
     ══════════════════════════════════════════════════════════════════ */
  function renderSpectrum(ctx, w, h, scale, levels, opts) {
    opts = opts || {};
    ctx.setTransform(scale, 0, 0, scale, 0, opts.offsetPx || 0);
    ctx.fillStyle = THEME.bg;
    ctx.fillRect(0, 0, w, h);
    const fs = opts.fontScale || 1;
    let top = 0;
    if (opts.caption) { top = 58 * fs; drawCaption(ctx, w, opts, fs); }

    let lo = Infinity, hi = -Infinity;
    levels.forEach(function (L) {
      lo = Math.min(lo, L.min); hi = Math.max(hi, L.max);
    });
    if (opts.docEdge) {
      lo = Math.min(lo, opts.docEdge[0]); hi = Math.max(hi, opts.docEdge[1]);
    }
    const pad = (hi - lo) * 0.06 || 1;
    lo -= pad; hi += pad;
    const x = function (v) { return 70 + (v - lo) / (hi - lo) * (w - 100); };

    const laneH = (h - top - 30) / levels.length;
    const laneColors = [THEME.goldB, THEME.teal, THEME.violet];
    levels.forEach(function (L, li) {
      const cy = top + laneH * li + laneH / 2;
      ctx.strokeStyle = 'rgba(36,64,95,0.6)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(60, cy); ctx.lineTo(w - 30, cy);
      ctx.stroke();
      ctx.fillStyle = THEME.muted;
      ctx.font = '600 12px "JetBrains Mono", monospace';
      ctx.fillText('L' + L.level + ' · ' + L.size, 12, cy - 8);
      ctx.fillStyle = laneColors[li % 3];
      const spec = L.spectrum;
      const stride = Math.max(1, Math.floor(spec.length / 800));
      for (let i = 0; i < spec.length; i += stride) {
        ctx.globalAlpha = 0.85;
        ctx.beginPath();
        ctx.arc(x(spec[i]), cy, 2.4, 0, 6.2832);
        ctx.fill();
      }
      ctx.globalAlpha = 1;
      ctx.fillStyle = laneColors[li % 3];
      ctx.font = '400 11px "JetBrains Mono", monospace';
      ctx.fillText(L.min.toFixed(4), x(L.min) - 10, cy + 18);
      const maxLabel = L.max.toFixed(4);
      ctx.fillText(maxLabel, x(L.max) - ctx.measureText(maxLabel).width - 4, cy + 18);
    });
    if (opts.docEdge) {
      [0, 1].forEach(function (i2) {
        const dx2 = x(opts.docEdge[i2]);
        ctx.strokeStyle = 'rgba(157,123,216,0.75)';
        ctx.setLineDash([5, 4]);
        ctx.beginPath();
        ctx.moveTo(dx2, top + 8);
        ctx.lineTo(dx2, h - 24);
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.fillStyle = THEME.violet;
        ctx.font = '400 11px "JetBrains Mono", monospace';
        ctx.fillText((i2 === 0 ? '−3.9890438' : '1.0000000') + ' · doc', dx2 + 4, h - 12);
      });
    }
  }

  /* Gram tower chart: density O(1/N), log-log; memory annotated */
  function renderGram(ctx, w, h, scale, rows, opts) {
    opts = opts || {};
    ctx.setTransform(scale, 0, 0, scale, 0, opts.offsetPx || 0);
    ctx.fillStyle = THEME.bg;
    ctx.fillRect(0, 0, w, h);
    const fs = opts.fontScale || 1;
    let top = 0;
    if (opts.caption) { top = 58 * fs; drawCaption(ctx, w, opts, fs); }

    const padL = 78, padR = 30, padT = top + 18, padB = 46;
    const lx0 = Math.log10(rows[0].N), lx1 = Math.log10(rows[rows.length - 1].N);
    const ly0 = Math.log10(rows[rows.length - 1].density), ly1 = Math.log10(rows[0].density);
    const X = function (N) { return padL + (Math.log10(N) - lx0) / (lx1 - lx0) * (w - padL - padR); };
    const Y = function (d) { return h - padB - (Math.log10(d) - ly0) / (ly1 - ly0) * (h - padT - padB); };

    // axes
    ctx.strokeStyle = 'rgba(36,64,95,0.8)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(padL, padT); ctx.lineTo(padL, h - padB); ctx.lineTo(w - padR, h - padB);
    ctx.stroke();
    ctx.fillStyle = THEME.muted;
    ctx.font = '400 11px "JetBrains Mono", monospace';
    rows.forEach(function (r) {
      ctx.fillText(String(r.N), X(r.N) - 14, h - padB + 16);
    });
    ctx.fillText('density', 12, padT + 4);

    // trend line
    ctx.strokeStyle = THEME.gold;
    ctx.lineWidth = 1.6;
    ctx.beginPath();
    rows.forEach(function (r, i) {
      if (i === 0) ctx.moveTo(X(r.N), Y(r.density));
      else ctx.lineTo(X(r.N), Y(r.density));
    });
    ctx.stroke();
    rows.forEach(function (r, i) {
      ctx.fillStyle = i === rows.length - 1 ? THEME.violet : THEME.teal;
      ctx.beginPath();
      ctx.arc(X(r.N), Y(r.density), 3.4, 0, 6.2832);
      ctx.fill();
      ctx.fillStyle = THEME.muted;
      ctx.fillText(r.density.toFixed(5), X(r.N) - 16, Y(r.density) - 9);
      ctx.fillStyle = i === rows.length - 1 ? THEME.violet : 'rgba(140,162,188,0.75)';
      ctx.fillText(r.memMB < 1 ? r.memMB.toFixed(3) + ' MB' : r.memMB.toFixed(1) + ' MB', X(r.N) - 16, Y(r.density) + 17);
    });
    ctx.fillStyle = THEME.muted;
    ctx.font = '400 11px "Inter", system-ui, sans-serif';
    ctx.fillText(opts.note || '', padL, h - 8);
  }

  window.HFBoard = {
    THEME: THEME,
    PHASE_COLORS: PHASE_COLORS,
    MOD7: MOD7,
    draw: draw,
    renderFormula: renderFormula,
    renderSpectrum: renderSpectrum,
    renderGram: renderGram,
    heatColor: heatColor,
  };
})();

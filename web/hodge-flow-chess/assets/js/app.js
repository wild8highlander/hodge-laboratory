/* ════════════════════════════════════════════════════════════════════
   Hodge Flow — Шахматная Лаборатория / Chess Flow Laboratory
   app.js — UI wiring: live RAF flow loop with batched steps (turbo),
   controls, sections, protocol E, towers, formula grid, reports,
   logs, bilingual instant re-render. window.HFApp
   ════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';
  const E = window.HFEngine, I = window.HFI18n, B = window.HFBoard, P = window.HFPlots;

  const $ = function (id) { return document.getElementById(id); };

  const App = {
    cfg: { W: 48, H: 48, a: 1, b: 1, layer: 'torus', n: 4, k: 1, speed: 24, turbo: false },
    fm: { K: 64, lambda0: 39.47841760435743, mode: 'A' },
    flow: null,
    playing: false,
    acc: 0, lastFrame: 0, lastStats: 0, lastBatchLog: 0,
    doneLogged: false,
    job: null, jobQueue: [], verd: {}, scanning: false, scanStart: 0, gridStarted: false,
    tower: null, gramRows: null, towersRun: false,
    proto: null,
    log: [], logOpen: false,
    sec: 'flow',
  };
  window.HFApp = App;

  const PHASE_SYM = ['1', 'i', '−1', '−i'];

  /* ── toast + log ─────────────────────────────────────────────────── */
  let toastTimer = null;
  function toast(msg, kind) {
    const el = $('toast');
    el.textContent = msg;
    el.className = 'toast show ' + (kind || 'info');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { el.className = 'toast'; }, 3400);
  }
  function pushLog(msg) {
    App.log.push({ t: new Date().toISOString(), msg: msg });
    if (App.log.length > 2000) App.log = App.log.slice(-1500);
    renderLog();
  }
  function renderLog() {
    const el = $('logBody');
    if (!el) return;
    if (!App.log.length) { el.textContent = I.t('log.empty'); return; }
    const frag = document.createDocumentFragment();
    const start = Math.max(0, App.log.length - 300);
    for (let i = start; i < App.log.length; i++) {
      const div = document.createElement('div');
      div.className = 'log-line';
      const ts = document.createElement('span');
      ts.className = 'log-ts';
      ts.textContent = App.log[i].t.slice(11, 23);
      div.appendChild(ts);
      div.appendChild(document.createTextNode(' ' + App.log[i].msg));
      frag.appendChild(div);
    }
    el.innerHTML = '';
    el.appendChild(frag);
    el.scrollTop = el.scrollHeight;
  }

  /* ── canvas sizing (devicePixelRatio aware) ──────────────────────── */
  function sizeCanvas(cv) {
    const dpr = Math.min(2.5, window.devicePixelRatio || 1);
    const r = cv.parentElement.getBoundingClientRect();
    const w = Math.max(180, Math.round(r.width) - 2);
    const h = Math.max(180, Math.round(r.height) - 2);
    cv.width = Math.round(w * dpr);
    cv.height = Math.round(h * dpr);
    cv._lw = w; cv._lh = h; cv._dpr = dpr;
  }

  /* ── flow lifecycle ──────────────────────────────────────────────── */
  function rebuildFlow(reason) {
    const c = App.cfg;
    App.flow = E.createFlow({ W: c.W, H: c.H, a: c.a, b: c.b, layer: c.layer, n: c.n, k: c.k });
    App.doneLogged = false;
    App.acc = 0;
    App.proto = null; // E2/E3 are live-configuration checks — force re-run on next visit
    renderChain();
    if (reason) {
      pushLog(I.t('log.reset').replace('{cfg}', cfgStr()));
    }
  }
  function cfgStr() {
    const c = App.cfg;
    return 'W=' + c.W + ' H=' + c.H + ' a=' + c.a + ' b=' + c.b + ' ' + c.layer + ' n=' + c.n + ' k=' + c.k;
  }

  function stepBudget(targetCond, budgetMs) {
    const f = App.flow;
    const t0 = performance.now();
    while (!targetCond(f)) {
      f.stepOnce(performance.now());
      if ((f.step & 511) === 0 && performance.now() - t0 > budgetMs) break;
    }
  }

  /* ── main loop ───────────────────────────────────────────────────── */
  function frame(ts) {
    const f = App.flow;
    if (f) {
      if (App.playing && !f.atRest) {
        if (App.cfg.turbo) {
          stepBudget(function (fl) { return fl.done; }, 12);
        } else {
          const dt = Math.min(0.25, (ts - App.lastFrame) / 1000 || 0);
          App.acc += dt * App.cfg.speed;
          let n = Math.min(4000, Math.floor(App.acc));
          App.acc -= Math.floor(App.acc);
          const t0 = performance.now();
          while (n-- > 0 && !f.done) {
            f.stepOnce(performance.now());
            if ((f.step & 255) === 0 && performance.now() - t0 > 11) break;
          }
        }
        if (ts - App.lastBatchLog > 2500) {
          App.lastBatchLog = ts;
          pushLog('· ' + f.step + ' / ' + f.tstarEff + ' · ' + f.visited);
        }
        if (f.done && !App.doneLogged) {
          App.doneLogged = true;
          pushLog(I.t('log.done').replace('{n}', f.step).replace('{v}', f.visited));
          if (App.sec === 'protocol') runProto();
        }
      }
      f.trimTrail();
      drawBoard(ts);
      if (ts - App.lastStats > 90) { App.lastStats = ts; updateStats(); updateLayersLive(); }
    }
    if (App.job && !App.job.done) pumpJob();
    else if (App.scanning) drawScan(ts);
    requestAnimationFrame(frame);
  }

  function drawBoard(now) {
    const cv = $('boardCanvas');
    if (!cv || !App.flow) return;
    if (!cv._lw) sizeCanvas(cv);
    const ctx = cv.getContext('2d');
    B.draw(ctx, cv._lw, cv._lh, cv._dpr, App.flow.snapshot(), { now: now });
  }

  /* ── stats panel ─────────────────────────────────────────────────── */
  function fmtClosure() {
    const f = App.flow;
    if (f.layer === 'k3') return '—';
    const closed = f.closureX === 0 && f.closureY === 0;
    return '(' + f.closureX + ', ' + f.closureY + ') · ' + (closed ? '✓' : '…');
  }
  function updateStats() {
    const f = App.flow;
    if (!f) return;
    $('stStep').textContent = String(f.step);
    $('stPos').textContent = (f.layer === 'k3')
      ? '(' + f.x + ', ' + f.y + ') · (' + f.px.toFixed(2) + ', ' + f.py.toFixed(2) + ')'
      : '(' + f.x + ', ' + f.y + ')';
    const ph = $('stPhase');
    ph.textContent = 'i^' + f.phase + ' = ' + PHASE_SYM[f.phase];
    ph.style.color = B.PHASE_COLORS[f.phase];
    const denom = f.layer === 'klein' ? f.tstarEff : f.tstar;
    $('stVisited').textContent = f.visited + ' / ' + denom +
      (f.layer === 'k3' ? ' ∞' : '');
    $('stTstar').textContent = String(f.tstar) +
      (f.layer === 'klein' ? ' → ' + f.tstarEff : '');
    $('stFriction').textContent = String(f.friction);
    $('stEdges').textContent = String(f.edges);
    $('stChain').textContent = String(f.chainTotal) + (f.chainTruncated ? ' +' : '');
    $('stClosure').textContent = fmtClosure();
    const pct = f.layer === 'k3'
      ? (f.atRest ? 100 : Math.min(99, (f.visited / (f.W * f.H)) * 100))
      : Math.min(100, (f.visited / Math.max(1, denom)) * 100);
    $('progFill').style.width = pct.toFixed(1) + '%';
    $('progText').textContent = pct.toFixed(0) + '%';
    $('stCycle').textContent = f.layer === 'k3' ? '—' : ('L = lcm(t*,4) = ' + f.terminalCycleLength() + ' · μ₄ = 4');
    const modeEl = $('stMode');
    modeEl.textContent = f.atRest ? I.t('st.mode.rest')
      : (f.done ? I.t('st.mode.term') : I.t('st.mode.run'));
    modeEl.className = 'mode-chip ' + (f.atRest ? 'm-rest' : (f.done ? 'm-term' : 'm-run'));
    // layer extras
    $('kleinRow1').style.display = f.layer === 'klein' ? '' : 'none';
    $('kleinRow2').style.display = f.layer === 'klein' ? '' : 'none';
    $('k3Row1').style.display = f.layer === 'k3' ? '' : 'none';
    $('k3Row2').style.display = f.layer === 'k3' ? '' : 'none';
    $('k3Row3').style.display = f.layer === 'k3' ? '' : 'none';
    if (f.layer === 'klein') {
      $('stSinger').textContent = '×' + f.singer;
      $('stPhase7').textContent = String(f.step % 7);
    }
    if (f.layer === 'k3') {
      $('stRefl').textContent = String(f.reflections);
      $('stBrake').textContent = f.brakeTotal.toExponential(3);
      $('stVel').textContent = '(' + f.vx.toFixed(3) + ', ' + f.vy.toFixed(3) + ')';
    }
  }

  function updateLayersLive() {
    const f = App.flow;
    if (!f) return;
    $('layDelta').textContent = f.delta.toFixed(10);
    $('layGamma').textContent = (f.delta ** 4 / App.cfg.k).toExponential(6);
    $('layDeltaEff').textContent = (f.delta ** 5 / App.cfg.k).toExponential(6);
    $('layBrake').textContent = f.brakeTotal.toExponential(6);
    $('laySinger').textContent = '×' + E.singerFactor(App.cfg.H);
  }

  /* ── chain strip ─────────────────────────────────────────────────── */
  const CHAIN_ARROWS = ['→', '↑', '←', '↓'];
  const CHAIN_CLS = ['c0', 'c1', 'c2', 'c3'];
  function renderChain() {
    const f = App.flow;
    const el = $('chainStrip');
    if (!f || !f.chain.length) {
      el.innerHTML = '<span class="chain-empty">' + I.t('chain.empty') + '</span>';
      $('chainMeta').textContent = '';
      return;
    }
    const lastN = 140;
    const start = Math.max(0, f.chain.length - lastN);
    let html = '';
    for (let i = start; i < f.chain.length; i++) {
      const d = f.chain[i];
      html += '<span class="chain-digit ' + CHAIN_CLS[d] + '" title="' + I.t('chain.d' + d) + '">' + CHAIN_ARROWS[d] + '</span>';
    }
    el.innerHTML = html;
    $('chainMeta').textContent = f.chainTruncated
      ? I.t('chain.trunc').replace('{n}', String(f.chainTotal))
      : String(f.chainTotal);
  }

  /* ── reference card (documented vs computed) ─────────────────────── */
  function updateRefCard() {
    const f = App.flow;
    if (!f) return;
    $('refVisited').textContent = String(f.visited);
    $('refFriction').textContent = String(f.friction);
    $('refEdges').textContent = String(f.edges);
    $('refCode').textContent = String(f.chainTotal);
  }

  /* ── controls wiring ─────────────────────────────────────────────── */
  function bindControls() {
    const syncWH = function () {
      const w = clamp(parseInt($('inpW').value, 10) || 48, 2, 384);
      const h = clamp(parseInt($('inpH').value, 10) || 48, 2, 384);
      App.cfg.W = w; App.cfg.H = h;
      $('inpW').value = String(w); $('inpH').value = String(h);
      $('inpWr').value = String(w); $('inpHr').value = String(h);
    };
    $('inpW').addEventListener('change', function () { syncWH(); rebuildFlow(true); warnBig(); });
    $('inpH').addEventListener('change', function () { syncWH(); rebuildFlow(true); warnBig(); });
    $('inpWr').addEventListener('input', function () {
      $('inpW').value = $('inpWr').value; syncWH(); rebuildFlow(false); warnBig(); drawBoard(performance.now()); updateStats();
    });
    $('inpHr').addEventListener('input', function () {
      $('inpH').value = $('inpHr').value; syncWH(); rebuildFlow(false); warnBig(); drawBoard(performance.now()); updateStats();
    });
    const syncAB = function () {
      const a = clamp(parseInt($('inpA').value, 10) || 0, -16, 16);
      const b = clamp(parseInt($('inpB').value, 10) || 0, -16, 16);
      App.cfg.a = a; App.cfg.b = b;
    };
    $('inpA').addEventListener('change', function () { syncAB(); rebuildFlow(true); checkDegenerate(); });
    $('inpB').addEventListener('change', function () { syncAB(); rebuildFlow(true); checkDegenerate(); });

    // layer radios
    const radios = document.querySelectorAll('input[name="layer"]');
    for (let i = 0; i < radios.length; i++) {
      radios[i].addEventListener('change', function (ev) {
        App.cfg.layer = ev.target.value;
        rebuildFlow(true);
        pushLog(I.t('log.layer').replace('{l}', App.cfg.layer));
        updateStats();
      });
    }

    // speed + turbo
    $('inpSpeed').addEventListener('input', function () {
      App.cfg.speed = clamp(parseInt(this.value, 10) || 24, 1, 120);
      $('speedVal').textContent = String(App.cfg.speed);
    });
    $('chkTurbo').addEventListener('change', function () {
      App.cfg.turbo = this.checked;
    });

    // presets
    const presets = document.querySelectorAll('[data-preset]');
    for (let i = 0; i < presets.length; i++) {
      presets[i].addEventListener('click', function () {
        const pp = this.getAttribute('data-preset').split('x');
        $('inpW').value = pp[0]; $('inpH').value = pp[1];
        syncWH(); rebuildFlow(true); warnBig();
        if (parseInt(pp[0], 10) >= 384) toast(I.t('preset.warn'), 'warn');
      });
    }

    // transport
    $('btnPlay').addEventListener('click', togglePlay);
    $('btnStep').addEventListener('click', function () {
      if (App.flow.atRest) return;
      App.playing = false; syncPlayBtn();
      App.flow.stepOnce(performance.now());
      drawBoard(performance.now()); updateStats(); renderChain(); updateRefCard();
      pushLog(I.t('log.step').replace('{n}', String(App.flow.step)));
    });
    $('btnReset').addEventListener('click', function () {
      App.playing = false; syncPlayBtn();
      rebuildFlow(true);
      drawBoard(performance.now()); updateStats(); updateRefCard();
    });
    $('btnSkip').addEventListener('click', skipToTstar);

    // chain copy
    $('chainCopy').addEventListener('click', function () {
      const f = App.flow;
      if (!f || !f.chain.length) return;
      const s = f.chain.join('');
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(s).then(function () { toast(I.t('chain.copied')); }, function () { fallbackCopy(s); });
      } else fallbackCopy(s);
    });

    // keyboard: space toggles play
    document.addEventListener('keydown', function (ev) {
      if (ev.code === 'Space' && App.sec === 'flow' &&
        !/INPUT|TEXTAREA|SELECT|BUTTON/.test(document.activeElement.tagName)) {
        ev.preventDefault(); togglePlay();
      }
    });
  }
  function fallbackCopy(s) {
    const ta = document.createElement('textarea');
    ta.value = s;
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); toast(I.t('chain.copied')); } catch (e) { /* ignore */ }
    document.body.removeChild(ta);
  }
  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }
  function warnBig() {
    const n = App.cfg.W * App.cfg.H;
    $('gridWarn').textContent = n > 9216 ? I.t('grid.size.warn').replace('{n}', String(n)) : '';
  }
  function checkDegenerate() {
    if (App.cfg.a === 0 && App.cfg.b === 0 && App.cfg.layer !== 'k3') {
      toast(I.t('err.degenerate'), 'warn');
    }
  }
  function togglePlay() {
    if (!App.flow) return;
    if (App.flow.degenerate) { toast(I.t('err.degenerate'), 'warn'); return; }
    App.playing = !App.playing;
    if (App.playing) pushLog(I.t('log.play').replace('{v}', App.cfg.turbo ? '∞' : String(App.cfg.speed)));
    else pushLog(I.t('log.pause').replace('{n}', String(App.flow.step)));
    syncPlayBtn();
  }
  function syncPlayBtn() {
    $('btnPlay').textContent = App.playing ? I.t('btn.pause') : I.t('btn.play');
  }
  function skipToTstar() {
    const f = App.flow;
    if (!f || f.degenerate) return;
    if (f.layer === 'k3') {
      const chunk = function () {
        const t0 = performance.now();
        while (!f.atRest && performance.now() - t0 < 28) f.stepOnce(performance.now());
        drawBoard(performance.now()); updateStats(); renderChain(); updateRefCard();
        if (!f.atRest && f.step < 2000000) setTimeout(chunk, 0);
        else pushLog(I.t('log.done').replace('{n}', String(f.step)).replace('{v}', String(f.visited)));
      };
      chunk();
      return;
    }
    App.playing = false; syncPlayBtn();
    stepBudget(function (fl) { return fl.done; }, 40);
    drawBoard(performance.now()); updateStats(); renderChain(); updateRefCard();
    pushLog(I.t('log.skip').replace('{n}', String(f.tstarEff)));
    if (!App.doneLogged) { App.doneLogged = true; pushLog(I.t('log.done').replace('{n}', String(f.step)).replace('{v}', String(f.visited))); }
  }

  /* ── sections ────────────────────────────────────────────────────── */
  function bindNav() {
    const btns = document.querySelectorAll('[data-sec]');
    for (let i = 0; i < btns.length; i++) {
      btns[i].addEventListener('click', function () {
        activateSec(this.getAttribute('data-sec'));
      });
    }
    $('sidebarToggle').addEventListener('click', function () {
      document.body.classList.toggle('sidebar-open');
    });
    $('langRu').addEventListener('click', function () { I.setLang('ru'); });
    $('langEn').addEventListener('click', function () { I.setLang('en'); });
    I.onChange(function (l) {
      $('langRu').classList.toggle('active', l === 'ru');
      $('langEn').classList.toggle('active', l === 'en');
      syncPlayBtn();
      pushLog(I.t('log.lang').replace('{l}', l.toUpperCase()));
      reRenderDynamic();
    });
  }
  function activateSec(sec) {
    App.sec = sec;
    const secs = document.querySelectorAll('.sec');
    for (let i = 0; i < secs.length; i++) {
      secs[i].classList.toggle('active', secs[i].id === 'sec-' + sec);
    }
    const btns = document.querySelectorAll('[data-sec]');
    for (let i = 0; i < btns.length; i++) {
      btns[i].classList.toggle('active', btns[i].getAttribute('data-sec') === sec);
    }
    document.body.classList.remove('sidebar-open');
    window.scrollTo({ top: 0, behavior: 'smooth' });
    if (sec === 'flow') { sizeCanvas($('boardCanvas')); drawBoard(performance.now()); updateStats(); }
    if (sec === 'grid') { initGrid(); }
    if (sec === 'protocol' && !App.proto) runProto();
    if (sec === 'towers' && !App.towersRun) runTowers();
  }
  function reRenderDynamic() {
    syncPlayBtn();
    renderChain();
    updateStats();
    if (App.proto) renderProto();
    if (App.towersRun) renderTowerResults();
    if (App.verd.A) renderVerdicts();
  }

  /* ── PROTOCOL E ──────────────────────────────────────────────────── */
  function runProto() {
    App.proto = E.protocolE(App.cfg);
    renderProto();
    const passed = App.proto.checks.filter(function (c) { return c.pass; }).length;
    pushLog(I.t('log.proto').replace('{r}', String(passed)));
  }
  function renderProto() {
    const tb = $('protoTable').querySelector('tbody');
    tb.innerHTML = '';
    App.proto.checks.forEach(function (c) {
      const tr = document.createElement('tr');
      const td1 = document.createElement('td');
      td1.className = 'proto-id';
      td1.textContent = c.id;
      const td2 = document.createElement('td');
      td2.textContent = I.t(c.key);
      const td3 = document.createElement('td');
      td3.className = 'mono';
      td3.textContent = c.value;
      const td4 = document.createElement('td');
      const badge = document.createElement('span');
      if (c.kind === 'documented') {
        badge.className = 'pill pill-doc';
        badge.textContent = I.t('proto.badge.doc');
      } else {
        badge.className = 'pill ' + (c.pass ? 'pill-pass' : 'pill-fail');
        badge.textContent = c.pass ? I.t('proto.badge.pass') : I.t('proto.badge.fail');
      }
      td4.appendChild(badge);
      tr.appendChild(td1); tr.appendChild(td2); tr.appendChild(td3); tr.appendChild(td4);
      tb.appendChild(tr);
    });
    const v = $('protoVerdict');
    v.textContent = App.proto.allPass ? I.t('proto.allpass') : I.t('proto.failed');
    v.className = 'verdict-banner ' + (App.proto.allPass ? 'ok' : 'bad');
  }

  /* ── FORMULA GRID ────────────────────────────────────────────────── */
  function initGrid() {
    if (!App.gridStarted) {
      App.gridStarted = true;
      sizeCanvas($('gridCanvas'));
      startFormulaJobs();
    } else {
      sizeCanvas($('gridCanvas'));
      drawFormula(App.scanning ? undefined : 1);
    }
  }
  function bindGrid() {
    $('inpKr').addEventListener('input', function () {
      App.fm.K = clamp(parseInt(this.value, 10) || 64, 16, 512);
      $('valK').textContent = String(App.fm.K);
    });
    $('inpKr').addEventListener('change', function () { startFormulaJobs(); });
    $('inpL0').addEventListener('change', function () {
      const v = parseFloat(this.value);
      if (isFinite(v) && v > 0) App.fm.lambda0 = v;
      startFormulaJobs();
    });
    const modes = document.querySelectorAll('input[name="fmode"]');
    for (let i = 0; i < modes.length; i++) {
      modes[i].addEventListener('change', function (ev) {
        App.fm.mode = ev.target.value;
        if (App.verd.A) { drawFormula(1); App.scanStart = performance.now(); App.scanning = true; }
        else startFormulaJobs();
      });
    }
    $('btnK4096').addEventListener('click', function () {
      if (!window.confirm(I.t('grid.big.warn'))) return;
      App.fm.K = 4096;
      $('valK').textContent = '4096';
      startFormulaJobs();
    });
    $('btnRescan').addEventListener('click', function () {
      if (App.verd.A) { App.scanStart = performance.now(); App.scanning = true; }
    });
  }
  function startFormulaJobs() {
    App.verd = {};
    App._jobs = {};
    App.jobQueue = ['A', 'B'];
    App.job = null;
    nextFormulaJob();
  }
  function nextFormulaJob() {
    if (!App.jobQueue.length) {
      renderVerdicts();
      drawFormula(1);
      App.scanStart = performance.now();
      App.scanning = true;
      return;
    }
    const mode = App.jobQueue[0];
    App.job = E.createFormulaJob(App.fm.K, App.fm.lambda0, App.cfg.n, App.cfg.k, mode);
    App.job.mode = mode;
    $('gridProgWrap').style.display = '';
    $('gridProgText').style.display = '';
    $('gridProgText').textContent = I.t('grid.computing').replace('{p}', '0');
  }
  function pumpJob() {
    const t0 = performance.now();
    let frac = 0;
    while (!App.job.done && performance.now() - t0 < 10) {
      frac = App.job.step(Math.max(2, Math.ceil(App.job.K / 6)));
    }
    $('gridProgFill').style.width = (frac * 100).toFixed(1) + '%';
    $('gridProgText').textContent = I.t('grid.computing').replace('{p}', String(Math.round(frac * 100)));
    if (App.job.done) {
      const mode = App.job.mode;
      App.verd[mode] = { max: App.job.maxDefect, raw: App.job.rawDefect, K: App.job.K };
      if (App.job.K <= 1024 || App.fm.mode === mode) {
        App._jobs[mode] = App.job; // keep arrays for heatmap / export
      } else {
        App.job.sArr = null; App.job.qArr = null; // free memory at monograph scale
      }
      pushLog(I.t('log.grid').replace('{K}', String(App.job.K)).replace('{m}', mode)
        .replace('{d}', App.job.maxDefect.toFixed(3)));
      App.jobQueue.shift();
      App.job = null;
      nextFormulaJob();
    }
  }
  function drawFormula(scan) {
    const cv = $('gridCanvas');
    if (!cv || !App.verd.A) return;
    if (!cv._lw) sizeCanvas(cv);
    // heatmap uses the job of the selected mode; find it among stored
    const job = App._jobs ? App._jobs[App.fm.mode] : null;
    if (!job) return;
    const ctx = cv.getContext('2d');
    B.renderFormula(ctx, cv._lw, cv._lh, cv._dpr, job, scan === undefined ? 1 : scan, {
      legend: true,
      legendQ: I.t('grid.legend.q'),
      legendLow: I.t('grid.legend.low'),
      legendHigh: I.t('grid.legend.high'),
    });
  }
  function drawScan(ts) {
    const p = Math.min(1, (ts - App.scanStart) / 2600);
    drawFormula(p);
    if (p >= 1) App.scanning = false;
  }
  function renderVerdicts() {
    $('gridProgWrap').style.display = 'none';
    $('gridProgText').style.display = 'none';
    ['A', 'B'].forEach(function (m) {
      const v = App.verd[m];
      const normEl = $(m === 'A' ? 'normDevA' : 'normDevB');
      const rawEl = $(m === 'A' ? 'rawDevA' : 'rawDevB');
      const pill = $(m === 'A' ? 'pillA' : 'pillB');
      if (!v) { normEl.textContent = '—'; rawEl.textContent = '—'; return; }
      normEl.textContent = v.max.toFixed(3);
      rawEl.textContent = v.raw.toExponential(2);
      if (m === 'A') {
        pill.textContent = I.t('grid.A.pass');
        pill.className = 'pill ' + (v.max < 1e-9 ? 'pill-pass' : 'pill-fail');
      } else {
        pill.textContent = I.t('grid.B.detected');
        pill.className = 'pill ' + (v.max > 0.5 ? 'pill-fail' : 'pill-pass');
      }
    });
    $('gridBeta').textContent = 'β = ' + E.formulaBeta(App.cfg.n, App.cfg.k).toExponential(6) +
      ' · δ = π/' + App.cfg.n + ' · k = ' + App.cfg.k;
  }

  /* ── TOWERS ──────────────────────────────────────────────────────── */
  function bindTowers() {
    $('btnTowers').addEventListener('click', runTowers);
  }
  function runTowers() {
    const twist = clamp(parseFloat($('inpTwist').value), -2, 2);
    const A = E.baseBlock(isFinite(twist) ? twist : -0.5);
    const eig = E.jacobiEigen(A);
    App.tower = { eig: eig, spectra: E.towerSpectra(eig.values) };
    App.gramRows = E.gramTower([22, 220, 2200, 22000, 220000]);
    App.towersRun = true;
    renderTowerResults();
    pushLog(I.t('log.towers').replace('{v}', eig.values.map(function (v) { return v.toFixed(3); }).join(', ')));
  }
  function renderTowerResults() {
    if (!App.tower) return;
    const eig = App.tower.eig, sp = App.tower.spectra;
    $('towersEigen').innerHTML = eig.values.map(function (v) {
      return '<span class="chip mono">' + v.toFixed(6) + '</span>';
    }).join('');
    $('towersResidual').textContent = eig.residual.toExponential(3);
    // stability table
    const tb = $('towersTable').querySelector('tbody');
    tb.innerHTML = '';
    sp.levels.forEach(function (L) {
      const tr = document.createElement('tr');
      [String(L.level), String(L.size), L.min.toFixed(6), L.max.toFixed(6), String(L.distinct)].forEach(function (v) {
        const td = document.createElement('td');
        td.className = 'mono';
        td.textContent = v;
        tr.appendChild(td);
      });
      tb.appendChild(tr);
    });
    // gram table
    const tg = $('gramTable').querySelector('tbody');
    tg.innerHTML = '';
    App.gramRows.forEach(function (r) {
      const tr = document.createElement('tr');
      [String(r.N), String(r.nnz), r.density.toExponential(3),
        r.memMB < 1 ? r.memMB.toFixed(3) : r.memMB.toFixed(1)].forEach(function (v) {
        const td = document.createElement('td');
        td.className = 'mono';
        td.textContent = v;
        tr.appendChild(td);
      });
      tg.appendChild(tr);
    });
    // charts
    const scv = $('specCanvas');
    if (scv) {
      if (!scv._lw) sizeCanvas(scv);
      B.renderSpectrum(scv.getContext('2d'), scv._lw, scv._lh, scv._dpr, sp.levels, {
        docEdge: E.DOC.edgeSpectrum,
      });
    }
    const gcv = $('gramCanvas');
    if (gcv) {
      if (!gcv._lw) sizeCanvas(gcv);
      B.renderGram(gcv.getContext('2d'), gcv._lw, gcv._lh, gcv._dpr, App.gramRows, {
        note: I.t('towers.docmem'),
      });
    }
  }

  /* ── REPORTS ─────────────────────────────────────────────────────── */
  function bindReports() {
    $('repJson').addEventListener('click', function () {
      const f = App.flow;
      const protoPassed = App.proto ? App.proto.allPass : E.protocolE(App.cfg).allPass;
      const protoChecks = (App.proto || E.protocolE(App.cfg)).checks.map(function (c) {
        return { id: c.id, check: I.t(c.key), kind: c.kind, pass: c.pass, value: c.value };
      });
      const report = {
        meta: {
          app: 'hodge-flow-chess',
          lang: I.lang,
          timestamp: new Date().toISOString(),
          version: '1.0.0',
          author: 'Исаев Исхак Хамзатович / Isaev Iskhak Khamzatovich',
        },
        config: {
          W: App.cfg.W, H: App.cfg.H, a: App.cfg.a, b: App.cfg.b,
          layer: App.cfg.layer, n: App.cfg.n, k: App.cfg.k,
        },
        results: {
          tstar: f.tstar,
          tstar_eff: f.tstarEff,
          visited: f.visited,
          friction: f.friction,
          edges: f.edges,
          chain_len: f.chainTotal,
          closure: { x: f.closureX, y: f.closureY, closed: f.closureX === 0 && f.closureY === 0 },
          terminal_cycle_length: f.terminalCycleLength(),
          equivariance: {
            K: App.fm.K,
            modeA_max_dev: App.verd.A ? App.verd.A.max : null,
            modeB_max_dev: App.verd.B ? App.verd.B.max : null,
            documented_reference: { symmetric: 0.0, encoding_7_22: 1.0, grid: 4096 },
          },
          monograph_reference: { friction: 212, edges: 432, chain_code: 114, sum: 806, kind: 'documented' },
          protocol_E: protoChecks,
        },
        verdict: protoPassed ? 'ALL CHECKS PASSED' : 'CHECKS FAILED',
      };
      const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
      downloadBlob(blob, 'hodge_flow_report.json', 'hodge_flow_report.json');
    });
    $('repTxt').addEventListener('click', function () {
      const lines = App.log.map(function (l) { return l.t + '  ' + l.msg; });
      if (!lines.length) lines.push(I.t('log.empty'));
      const blob = new Blob([lines.join('\n') + '\n'], { type: 'text/plain;charset=utf-8' });
      downloadBlob(blob, 'hodge_flow_log.txt', 'hodge_flow_log.txt');
    });
    $('repMeta').addEventListener('click', function () {
      const c = App.cfg;
      const meta = [
        'Hodge Flow — Chess Flow Laboratory · v1.0.0',
        'Program: Isaev Iskhak Khamzatovich / Исаев Исхак Хамзатович',
        'Monograph: "The Dynamic Principle", Part XV',
        '----------------------------------------',
        'timestamp : ' + new Date().toISOString(),
        'lang      : ' + I.lang,
        'W         : ' + c.W,
        'H         : ' + c.H,
        'a         : ' + c.a,
        'b         : ' + c.b,
        'layer     : ' + c.layer,
        'n         : ' + c.n,
        'k         : ' + c.k,
        'speed     : ' + c.speed + ' steps/s' + (c.turbo ? ' (turbo)' : ''),
        '----------------------------------------',
        't*        : ' + (App.flow ? App.flow.tstar : ''),
        't*_eff    : ' + (App.flow ? App.flow.tstarEff : ''),
        'visited   : ' + (App.flow ? App.flow.visited : ''),
        'friction  : ' + (App.flow ? App.flow.friction : ''),
        'edges     : ' + (App.flow ? App.flow.edges : ''),
        'chain_len : ' + (App.flow ? App.flow.chainTotal : ''),
        '----------------------------------------',
        'documented reference (monograph): 48 / 212 / 432 / 114 = 806',
        'license: individual exclusive license',
      ].join('\n');
      const blob = new Blob([meta + '\n'], { type: 'text/plain;charset=utf-8' });
      downloadBlob(blob, 'hodge_flow_meta.txt', 'hodge_flow_meta.txt');
    });
    $('repPngBoard').addEventListener('click', function () {
      if (!App.flow) return;
      P.exportBoard(App.flow.snapshot(), I.t('flow.title'), cfgStr(), I.lang,
        function (size) { toast(I.t('rep.done').replace('{f}', 'board 600dpi PNG · ' + size + 'px')); },
        function (e) { toast(I.t('rep.fail').replace('{e}', String(e && e.message || e)), 'warn'); });
    });
    $('repPngGrid').addEventListener('click', function () {
      if (!App.verd.A || !App._jobs || !App._jobs[App.fm.mode]) {
        toast(I.t('rep.fail').replace('{e}', 'formula grid not computed yet'), 'warn');
        return;
      }
      P.exportFormula(App._jobs[App.fm.mode], 1, I.t('grid.title'),
        I.t('grid.formula') + ' · K=' + App.fm.K + ' · ' + I.t('grid.mode' + App.fm.mode),
        { q: I.t('grid.legend.q'), low: I.t('grid.legend.low'), high: I.t('grid.legend.high') },
        function (size) { toast(I.t('rep.done').replace('{f}', 'formula grid 600dpi PNG · ' + size + 'px')); },
        function (e) { toast(I.t('rep.fail').replace('{e}', String(e && e.message || e)), 'warn'); });
    });
    $('repPngSpec').addEventListener('click', function () {
      if (!App.tower) { runTowers(); }
      P.exportSpectrum(App.tower.spectra.levels, E.DOC.edgeSpectrum,
        I.t('towers.title'), I.t('towers.spectra'), App.gramRows, I.t('towers.gram'),
        function (size) { toast(I.t('rep.done').replace('{f}', 'spectrum 600dpi PNG · ' + size + 'px')); },
        function (e) { toast(I.t('rep.fail').replace('{e}', String(e && e.message || e)), 'warn'); });
    });
    // log drawer
    $('logToggle').addEventListener('click', function () {
      App.logOpen = !App.logOpen;
      $('logDrawer').classList.toggle('open', App.logOpen);
      this.setAttribute('aria-expanded', App.logOpen ? 'true' : 'false');
    });
    $('logClose').addEventListener('click', function () {
      App.logOpen = false;
      $('logDrawer').classList.remove('open');
    });
    $('logClear').addEventListener('click', function () {
      App.log = [];
      renderLog();
    });
    $('logDown').addEventListener('click', function () { $('repTxt').click(); });
  }
  function downloadBlob(blob, filename, label) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 4000);
    toast(I.t('rep.done').replace('{f}', label));
    pushLog(I.t('rep.done').replace('{f}', label));
  }

  /* ── layers section bindings ─────────────────────────────────────── */
  function bindLayers() {
    $('inpN').addEventListener('change', function () {
      App.cfg.n = clamp(parseInt(this.value, 10) || 4, 2, 64);
      this.value = String(App.cfg.n);
      rebuildFlow(false);
      updateLayersLive();
      if (App.gridStarted) startFormulaJobs();
    });
    $('inpK').addEventListener('change', function () {
      App.cfg.k = clamp(parseInt(this.value, 10) || 1, 1, 1024);
      this.value = String(App.cfg.k);
      rebuildFlow(false);
      updateLayersLive();
      if (App.gridStarted) startFormulaJobs();
    });
    $('btnNKlein').addEventListener('click', function () {
      App.cfg.n = 7; App.cfg.k = 22;
      $('inpN').value = '7'; $('inpK').value = '22';
      rebuildFlow(false); updateLayersLive();
      if (App.gridStarted) startFormulaJobs();
      toast('n=7, k=22 · Klein');
    });
    $('btnNTorus').addEventListener('click', function () {
      App.cfg.n = 4; App.cfg.k = 1;
      $('inpN').value = '4'; $('inpK').value = '1';
      rebuildFlow(false); updateLayersLive();
      if (App.gridStarted) startFormulaJobs();
      toast('n=4, k=1 · torus');
    });
  }

  /* ── init ────────────────────────────────────────────────────────── */
  function init() {
    I.apply();
    $('langRu').classList.toggle('active', I.lang === 'ru');
    $('langEn').classList.toggle('active', I.lang === 'en');
    bindNav();
    bindControls();
    bindGrid();
    bindTowers();
    bindReports();
    bindLayers();

    sizeCanvas($('boardCanvas'));
    rebuildFlow(false);
    pushLog(I.t('log.started'));
    pushLog(I.t('log.config').replace('{cfg}', cfgStr()));
    updateStats();
    updateRefCard();
    renderChain();
    updateLayersLive();

    // responsive canvas resize
    let rsTimer = null;
    window.addEventListener('resize', function () {
      clearTimeout(rsTimer);
      rsTimer = setTimeout(function () {
        ['boardCanvas', 'gridCanvas', 'specCanvas', 'gramCanvas'].forEach(function (id) {
          const cv = $(id);
          if (cv && cv.parentElement && cv.parentElement.getBoundingClientRect().width > 0) sizeCanvas(cv);
        });
        if (App.sec === 'flow') drawBoard(performance.now());
        if (App.sec === 'grid' && App.verd.A) drawFormula(App.scanning ? undefined : 1);
        if (App.towersRun) renderTowerResults();
      }, 160);
    });

    if (window.ResizeObserver) {
      const ro = new ResizeObserver(function () {
        const cv = $('boardCanvas');
        if (App.sec === 'flow' && cv) { sizeCanvas(cv); drawBoard(performance.now()); }
      });
      const bw = document.querySelector('.board-wrap');
      if (bw) ro.observe(bw);
    }

    App.lastFrame = performance.now();
    requestAnimationFrame(frame);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

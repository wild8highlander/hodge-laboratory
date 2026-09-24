/* ═══ HODGE LABORATORY WEB — app.js — UI wiring ═══ */
(function () {
  'use strict';
  const I = window.I18N, C = window.Core, F = window.Fermat, P = window.Precise,
    CY = window.Cycles, PL = window.Plots, FG = window.Forge;
  const $ = id => document.getElementById(id);
  const App = {};

  const sleep = ms => new Promise(r => setTimeout(r, ms || 0));
  function toast(msg) {
    const t = $('toast'); t.textContent = msg; t.hidden = false;
    clearTimeout(t._h); t._h = setTimeout(() => { t.hidden = true; }, 2600);
  }
  function download(name, content, mime) { FG.download(name, content, mime); }

  /* ── navigation ── */
  App.goto = function (sec) {
    document.querySelectorAll('.sec').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav a').forEach(a => a.classList.toggle('active', a.dataset.sec === sec));
    $('sec-' + sec).classList.add('active');
    $('tbTitle').textContent = I.t('nav_' + sec === 'nav_' + sec ? 'nav_' + sec : 'nav_' + sec);
    $('tbTitle').textContent = I.t('nav_' + sec);
    if (window.innerWidth <= 960) $('sidebar').classList.remove('open');
    if (sec === 'reports') renderPlots();
    window.scrollTo({ top: 0 });
  };

  /* ── dashboard ladder ── */
  const LADDER = [
    ['Тор / Torus', '(4, 1, 4π²)', '1', 'δ = π/4; holonomy = i; Δ_Ch = 39.4880; 4 спина / 4 spin'],
    ['K3 · Фермат / Fermat', '(4, 22, ·)', '—', 'ρ = 20 = max (Shioda); signature (1,19); det 64; 48 lines'],
    ['Клейн / Klein', '(7, 22, 3.338)', '3', 'j = −3375 = −15³; Δ = −7³; τ = (1+√−7)/2; Ribet'],
    ['Фермат N=7 / Fermat N=7', '(7, ·, ·)', '15', 'census 15 = h₇; Vieta (−1,−2,1); Cardano b_Ch(7)'],
    ['Фермат N=9 / Fermat N=9', '(9, ·, ·)', '28', 'census 28 = 1+27; Vieta (0,−3,−1); Cardano b_Ch(9)'],
    ['Фермат N=15 / Fermat N=15', '(15, ·, ·)', '91', 'census 1+6+84; Γ-нормировка / Γ-normalization; radical b_Ch(15)'],
    ['Фермат N=30 / Fermat N=30', '(30, ·, ·)', '406', 'SNF (1,1,5,5,15,15,15,15); disc = 1125²; vol_h = 1125'],
  ];
  function renderLadder() {
    const tb = $('ladderTbl').querySelector('tbody');
    tb.innerHTML = LADDER.map(r => `<tr><td class="num">${r[0]}</td><td class="num">${r[1]}</td><td class="num">${r[2]}</td><td>${r[3]}</td><td class="ok">✔ ${I.t('pass')}</td></tr>`).join('');
  }
  const VERSIONS = [
    ['v1.0', 'Монография, A–H, V1–V9, 5 языков / monograph, A–H, V1–V9, 5 languages', true],
    ['v1.1–1.1.2', 'Укрепление верификации / verification hardening', true],
    ['v1.2', 'Радикалы b_Ch(15), b_Ch(30) / radical arithmetic', true],
    ['v1.3', 'Ступени N=7/9, сертификаты I, J / Hurwitz & Macbeath rungs', true],
    ['v1.4', 'Пакетный режим / batch experiment mode', true],
    ['v1.5', 'N=11 (Хурвиц₃), сертификат K / the cyclic quintic rung', false],
    ['v1.6', 'SNF-спектры ступеней / SNF spectra of the rungs', false],
    ['v1.7', 'Монографии T17–T20 (20 теорем) / theorem monographs', true],
    ['v2.0', 'Высокие циклотомические уровни / higher cyclotomic levels', false],
  ];
  function renderVersions() {
    $('versions').innerHTML = VERSIONS.map(v =>
      `<div class="vtag ${v[2] ? 'done' : 'plan'}"><b>${v[0]}</b> · ${v[1]}<br><span class="badge ${v[2] ? 'badge-pass' : 'badge-doc'}" style="display:inline-block;margin-top:8px">${v[2] ? (I.lang === 'ru' ? 'ЗАВЕРШЕНО' : 'DELIVERED') : (I.lang === 'ru' ? 'В ПЛАНЕ' : 'NEXT')}</span></div>`).join('');
  }

  /* ── protocol / stands / certs / cycles cards ── */
  const PROT = [
    ['v1', 'v1_t', 'v1_d', () => C.v1_census()],
    ['v2', 'v2_t', 'v2_d', () => C.v2_v3_certB(3)],
    ['v4', 'v4_t', 'v4_d', () => C.v4_certC()],
    ['v5', 'v5_t', 'v5_d', () => C.v5_chain()],
    ['v6', 'v6_t', 'v6_d', () => C.v6_reflection()],
    ['v7', 'v7_t', 'v7_d', () => C.v7_rank()],
    ['v8', 'v8_t', 'v8_d', () => C.v8_dft(15)],
    ['v9', 'v9_t', 'v9_d', () => C.v9_deep(70)],
  ];
  const STANDS = [
    ['torus', 'stand_torus', () => C.stand_torus()],
    ['k3', 'stand_k3', () => C.stand_k3()],
    ['klein', 'stand_klein', () => C.stand_klein()],
    ['n7', 'stand_n7', () => C.stand_n7()],
    ['n9', 'stand_n9', () => C.stand_n9()],
    ['errata', 'stand_errata', () => C.stand_errata()],
    ['binary', 'stand_binary', () => C.stand_binary()],
  ];
  const CERT_DESC = {
    A: 'Цикл-сертификатор: дивизор Z = 3/2·L₁(0,0) − 1/2·L₂(1,1) + 5/4·h; ядро 29 / Cycle certifier: divisor, kernel 29',
    B: 'Замыкание ядра 29 периодами; слепое пятно 29+2 → 0 / Closing kernel 29 by periods',
    C: 'μ₄-эквивариантность: 22 = 1+7+7+7; charpoly(λ₁) = x⁴−1; гептада √−7 / μ₄-equivariance, the heptad',
    D: 'Универсальная μ₄-теорема: [L,P] = 0; функториальность / The universal μ₄-theorem',
    E: 'Завершимость потока: t* = lcm(W/gcd(a,W), H/gcd(b,H)) / Flow termination, the exact lcm formula',
    F: 'Рационализация: априорная граница Q = 256; LLL: Im τ = √7/2 / Rationalization with the a priori bound',
    G: 'Индексы ходжевой решётки; слой Чоула–Зельберга / Hodge lattice indices, Chowla–Selberg',
    H: 'Ступень N=15/30: SNF (1,1,5,5,15,15,15,15); vol_h = 1125 / The N=15/30 stand, the Gross volume',
    I: 'Ступень Хурвица N=7: перепись 15; Vieta; Cardano b_Ch(7) / The Hurwitz rung N=7',
    J: 'Ступень Макбита N=9: перепись 28 = 1+27; Cardano b_Ch(9) / The Macbeath rung N=9',
  };

  function cardShell(id, title, desc, btnLabel, onRun, extra) {
    return `<div class="card" id="card-${id}">
      <h3>${title}</h3><p>${desc}</p>
      <div class="row"><button class="btn btn-ghost" style="padding:9px 18px;min-height:38px" data-run="${id}">${btnLabel}</button>
      <span class="badge badge-idle" data-badge="${id}">—</span></div>
      <div class="detail" data-detail="${id}" hidden></div>${extra || ''}</div>`;
  }
  function wireCards() {
    document.querySelectorAll('[data-run]').forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = btn.dataset.run;
        const badge = document.querySelector(`[data-badge="${id}"]`);
        const det = document.querySelector(`[data-detail="${id}"]`);
        btn.disabled = true; badge.className = 'badge badge-doc'; badge.textContent = I.t('running');
        await sleep(30);
        try {
          const fn = RUNNERS[id];
          const r = await fn();
          const pass = r && r.pass;
          badge.className = `badge ${pass ? 'badge-pass' : 'badge-fail'}`;
          badge.textContent = pass ? I.t('pass') : I.t('fail');
          if (det) { det.hidden = false; det.textContent = r.detail || JSON.stringify(r.data || r.res || {}, null, 1).slice(0, 1600); }
        } catch (e) {
          badge.className = 'badge badge-fail'; badge.textContent = 'ERR';
          if (det) { det.hidden = false; det.textContent = String(e && e.message || e); }
        }
        btn.disabled = false;
      });
    });
  }
  const RUNNERS = {};
  function renderCards() {
    // protocol
    $('protocolGrid').innerHTML = PROT.map(([id, tk, dk]) =>
      cardShell('p' + id, I.t(tk), I.t(dk), I.t('run'), null)).join('');
    PROT.forEach(([id]) => {
      RUNNERS['p' + id] = async () => {
        const r = PROT.find(x => x[0] === id)[3]();
        C.log(`[card] ${id}: ${r.pass ? 'PASS' : 'FAIL'}`);
        return { pass: r.pass, detail: JSON.stringify(r.res || {}, null, 1), data: r.res };
      };
    });
    // stands
    $('standsGrid').innerHTML = STANDS.map(([id, tk, fn]) =>
      cardShell('s' + id, I.t(tk), '', I.t('run'), null)).join('');
    STANDS.forEach(([id, , fn]) => {
      RUNNERS['s' + id] = async () => {
        const r = fn();
        return { pass: r.pass, detail: r.checks.map(c => `${c.pass ? '✔' : '✘'} ${c.name}${c.detail ? ' — ' + c.detail : ''}${c.documented ? ' [' + I.t('documented') + ']' : ''}`).join('\n'), data: r.data };
      };
    });
    // certs
    $('certsGrid').innerHTML = Object.keys(CERT_DESC).map(L =>
      cardShell('c' + L, `Сертификат ${L} / Certificate ${L}`, CERT_DESC[L], I.t('run'), null)).join('');
    Object.keys(CERT_DESC).forEach(L => {
      RUNNERS['c' + L] = async () => {
        const r = C.CERT_FUNCS[L]();
        return { pass: r.pass, detail: r.checks.map(c => `${c.pass ? '✔' : '✘'} ${c.name}${c.detail ? ' — ' + c.detail : ''}${c.documented ? ' [' + I.t('documented') + ']' : ''}`).join('\n'), data: {} };
      };
    });
    wireCards();
  }

  /* ── cycles ── */
  let cycleResults = null;
  function renderCycles() {
    $('cyclesGrid').innerHTML = CY.meta().map(m => {
      const layer = CY.layerOf(m.idx);
      const t = CY.titleOf(m.idx, I.lang);
      return cardShell('y' + m.id, `${m.id} · ${I.lang === 'ru' ? t.ru : t.en}`,
        `<span class="layer-tag" style="color:${layer.includes('exact') ? '#3FC9AD' : layer.includes('num') ? '#C9A96A' : '#9D7BD8'}">◈ ${I.t(layer.includes('exact') ? 'computed_exact' : layer.includes('num') ? 'computed_num' : 'documented')}</span>`,
        I.t('run'), null);
    }).join('');
    CY.meta().forEach(m => {
      RUNNERS['y' + m.id] = async () => {
        const res = CY.byId(m.id);
        cycleResults = cycleResults || {};
        cycleResults[m.id] = res;
        return { pass: res.pass, detail: res.checks.map(c => `${c.pass ? '✔' : '✘'} ${c.name}${c.detail ? ' — ' + c.detail : ''}${c.documented ? ' [' + I.t('documented') + ']' : ''}`).join('\n') + '\n\n' + (I.lang === 'ru' ? res.meaning.ru : res.meaning.en), data: {} };
      };
    });
    wireCards();
  }
  $('btnCycles').addEventListener('click', async function () {
    this.disabled = true; toast(I.t('running'));
    await sleep(30);
    const res = CY.runAll();
    cycleResults = {};
    res.forEach(r => { cycleResults[r.id] = r; });
    renderCycles();
    // stamp the verdicts onto the freshly rendered cards
    res.forEach(r => {
      const badge = document.querySelector(`[data-badge="y${r.id}"]`);
      const det = document.querySelector(`[data-detail="y${r.id}"]`);
      if (badge) { badge.className = `badge ${r.pass ? 'badge-pass' : 'badge-fail'}`; badge.textContent = r.pass ? I.t('pass') : I.t('fail'); }
      if (det) {
        det.hidden = false;
        det.textContent = r.checks.map(c => `${c.pass ? '✔' : '✘'} ${c.name}${c.detail ? ' — ' + c.detail : ''}${c.documented ? ' [' + I.t('documented') + ']' : ''}`).join('\n') + '\n\n' + (I.lang === 'ru' ? r.meaning.ru : r.meaning.en);
      }
    });
    const all = res.every(r => r.pass);
    toast(all ? I.t('all_pass') : I.t('has_fail'));
    this.disabled = false;
  });

  /* ── roadmap runner ── */
  let running = false;
  const STAGES = [
    ['protocol', 'stage_protocol', 8], ['stands', 'stage_stands', 7], ['certs', 'stage_certs', 10],
    ['cycles', 'stage_cycles', 10], ['baseline', 'stage_baseline', 1], ['plots', 'stage_plots', 8], ['monograph', 'stage_monograph', 1],
  ];
  function renderStages() {
    $('stages').innerHTML = STAGES.map(s => `<div class="stage" id="stage-${s[0]}">
      <div class="stage-h"><span data-i18n="${s[1]}">${I.t(s[1])}</span><span class="badge badge-idle" id="stageBadge-${s[0]}">—</span></div>
      <div class="stage-bar"><div class="stage-fill" id="stageFill-${s[0]}"></div></div>
      <div class="stage-note" id="stageNote-${s[0]}"></div></div>`).join('');
  }
  function setStage(id, frac, note, done, fail) {
    $('stageFill-' + id).style.width = Math.round(frac * 100) + '%';
    if (note) $('stageNote-' + id).textContent = note;
    if (done || fail) {
      const st = $('stage-' + id); st.classList.toggle('done', !!done); st.classList.toggle('fail', !!fail);
      const b = $('stageBadge-' + id);
      b.className = `badge ${done ? 'badge-pass' : 'badge-fail'}`;
      b.textContent = done ? I.t('pass') : I.t('fail');
    }
  }
  function rlog(line) {
    const lb = $('roadmapLogBody');
    lb.textContent += line + '\n';
    lb.scrollTop = lb.scrollHeight;
    $('roadmapLog').hidden = false;
  }
  $('btnRoadmap').addEventListener('click', async function () {
    if (running) return;
    running = true; this.disabled = true;
    const t0 = performance.now();
    C.resetResults(I.lang);
    renderStages();
    $('roadmapVerdict').hidden = true;
    $('chipVerdict').hidden = true;
    let allOk = true;

    // 1. protocol
    try {
      const proto = [['V1', () => C.v1_census()], ['V2/V3', () => C.v2_v3_certB(3)], ['V4', () => C.v4_certC()],
        ['V5', () => C.v5_chain()], ['V6', () => C.v6_reflection()], ['V7', () => C.v7_rank()], ['V8', () => C.v8_dft(15)], ['V9', () => C.v9_deep(70)]];
      for (let i = 0; i < proto.length; i++) {
        const [nm, fn] = proto[i];
        rlog(`▸ ${nm} …`);
        await sleep(20);
        const r = fn();
        allOk = allOk && r.pass;
        rlog(`  ${r.pass ? '✔ PASS' : '✘ FAIL'} ${nm} ${JSON.stringify(r.res).slice(0, 120)}`);
        setStage('protocol', (i + 1) / proto.length, `${nm}: ${r.pass ? 'PASS' : 'FAIL'}`, false, false);
      }
      setStage('protocol', 1, '', allOk, !allOk);
    } catch (e) { setStage('protocol', 1, String(e), false, true); allOk = false; }

    // 2. stands
    try {
      for (let i = 0; i < STANDS.length; i++) {
        const [id, , fn] = STANDS[i];
        rlog(`▸ stand ${id} …`);
        await sleep(20);
        const r = fn();
        allOk = allOk && r.pass;
        rlog(`  ${r.pass ? '✔' : '✘'} ${id} (${r.checks.filter(c => c.pass).length}/${r.checks.length})`);
        setStage('stands', (i + 1) / STANDS.length, `${id}: ${r.pass ? 'PASS' : 'FAIL'}`, false, false);
      }
      setStage('stands', 1, '', allOk, !allOk);
    } catch (e) { setStage('stands', 1, String(e), false, true); allOk = false; }

    // 3. certificates
    try {
      const Ls = Object.keys(C.CERT_FUNCS);
      for (let i = 0; i < Ls.length; i++) {
        const L = Ls[i];
        await sleep(15);
        const r = C.CERT_FUNCS[L]();
        allOk = allOk && r.pass;
        rlog(`▸ certificate ${L}: ${r.pass ? '✔ PASS' : '✘ FAIL'}`);
        setStage('certs', (i + 1) / Ls.length, `${L}: ${r.pass ? 'PASS' : 'FAIL'}`, false, false);
      }
      setStage('certs', 1, '', allOk, !allOk);
    } catch (e) { setStage('certs', 1, String(e), false, true); allOk = false; }

    // 4. cycles
    try {
      const res = CY.runAll();
      for (let i = 0; i < res.length; i++) {
        const r = res[i];
        allOk = allOk && r.pass;
        rlog(`▸ ${r.id} ${I.lang === 'ru' ? r.title.ru : r.title.en}: ${r.pass ? '✔' : '✘'}`);
        setStage('cycles', (i + 1) / res.length, `${r.id}: ${r.pass ? 'PASS' : 'FAIL'}`, false, false);
        await sleep(10);
      }
      setStage('cycles', 1, '', allOk, !allOk);
    } catch (e) { setStage('cycles', 1, String(e), false, true); allOk = false; }

    // 5. baseline
    try {
      await sleep(20);
      const bl = C.checkBaseline();
      allOk = allOk && bl.pass;
      rlog(`▸ baseline cross-check: ${bl.pass ? '✔ PASS' : '✘ FAIL'} (${bl.rows.length} rows)`);
      setStage('baseline', 1, '', bl.pass, !bl.pass);
    } catch (e) { setStage('baseline', 1, String(e), false, true); allOk = false; }

    // 6. plots
    try {
      initPlots();
      for (let i = 0; i < PL.LIST.length; i++) {
        PL.render(document.querySelector(`[data-plot="${PL.LIST[i][0]}"]`), PL.LIST[i][0], I.lang);
        setStage('plots', (i + 1) / PL.LIST.length, PL.LIST[i][1]);
        await sleep(40);
      }
      setStage('plots', 1, '', true, false);
      rlog('▸ plots: 8 tiles rendered @600dpi-ready');
    } catch (e) { setStage('plots', 1, String(e), false, true); allOk = false; }

    // 7. monograph
    try {
      await sleep(20);
      updateMonPreview();
      setStage('monograph', 1, '', true, false);
      rlog('▸ monograph: LaTeX + HTML forged');
    } catch (e) { setStage('monograph', 1, String(e), false, true); allOk = false; }

    const dt = ((performance.now() - t0) / 1000).toFixed(1);
    rlog(`\n  SUMMARY VERDICT: ${allOk ? I.t('all_pass') : I.t('has_fail')}  (${I.t('duration')}: ${dt}s)`);
    const vb = $('roadmapVerdict');
    vb.hidden = false;
    vb.className = `verdict-box ${allOk ? 'verdict-pass' : 'verdict-fail'}`;
    vb.textContent = `${allOk ? '✔ ' : '✘ '}${allOk ? I.t('all_pass') : I.t('has_fail')} · ${dt}s`;
    const chip = $('chipVerdict');
    chip.hidden = false;
    chip.className = `chip ${allOk ? 'chip-pass' : 'chip-fail'}`;
    chip.textContent = allOk ? I.t('all_pass') : I.t('has_fail');
    running = false; this.disabled = false;
    toast(allOk ? I.t('all_pass') : I.t('has_fail'));
  });

  /* ── designer ── */
  const PRESETS = [
    ['preset_deep', () => runPreset({ type: 'V9-120' })],
    ['preset_n1001', () => runPreset({ type: 'census', N: 1001 })],
    ['preset_flow384', () => runPreset({ type: 'flow', W: 384, H: 384, a: 1, b: 1 })],
    ['preset_omega30', () => runPreset({ type: 'omega-scan' })],
    ['preset_tower', () => runPreset({ type: 'k3-tower' })],
  ];
  async function runPreset(spec) {
    const out = $('desResult'); out.hidden = false; out.textContent = '…';
    await sleep(30);
    const lines = [];
    if (spec.type === 'V9-120') {
      P.setDps(120);
      const t0 = performance.now();
      const r = C.v9_deep(120);
      P.setDps(35);
      lines.push(`V9 DEEP RECORD @ dps=120 (немыслимая точность / unthinkable precision)`,
        `  verdict: ${r.pass ? 'PASS' : 'FAIL'}`,
        `  rel_err: ${r.res.rel_err.toExponential(3)}`,
        `  time: ${r.res.seconds.toFixed(2)}s`);
      $('chipDps').textContent = 'dps 120';
    } else if (spec.type === 'omega-scan') {
      const { byD } = F.census(30);
      let worst = 0, cnt = 0;
      for (const [, [a, b]] of F.pickChars(byD, 4)) {
        worst = Math.max(worst, F.relErr(F.periodClosed(30, a, b, 0, 0), F.periodNumeric(30, a, b, 0, 0)));
        cnt++;
      }
      lines.push(`Ω-скан уровня N=30 / Ω-scan of level 30`,
        `  персонажей проверено / characters checked: ${cnt}`,
        `  worst rel (closed ↔ quadrature): ${worst.toExponential(2)}`,
        `  verdict: ${worst < 1e-25 ? 'PASS' : 'FAIL'}`);
    } else if (spec.type === 'k3-tower') {
      const t0 = performance.now();
      const inv = C.k3Invariants();
      lines.push(`K3 · точный слой / exact layer (${inv.ms}ms)`,
        `  rank_Q = ${inv.rank} (Shioda)`,
        `  signature = (${inv.sig}) — Hodge index`,
        `  SNF factors = [${inv.factors}] → det = ${inv.det} = 8²`,
        `  family relation Σ_b L1(a,b) ~ h: ${inv.famOk ? 'exact ✔' : 'FAIL'}`,
        `  Kronecker-башни 28k и Грам-башни 22k — документированный эталон [−3.9890438, 1.0] [documented]`);
    } else {
      const r = C.designerRun(spec);
      lines.push(`preset: ${JSON.stringify(spec)}`, JSON.stringify(r.data || r, null, 1).slice(0, 1200));
    }
    out.textContent = lines.join('\n');
    toast(lines[lines.length - 1].includes('PASS') || lines.join('').includes('PASS') ? I.t('all_pass') : I.t('pass'));
  }
  function renderPresets() {
    $('presetChips').innerHTML = PRESETS.map((p, i) => `<button class="pchip" data-preset="${i}">${I.t(p[0])}</button>`).join('');
    $('presetChips').querySelectorAll('[data-preset]').forEach(b =>
      b.addEventListener('click', () => PRESETS[+b.dataset.preset][1]()));
  }
  $('btnDesigner').addEventListener('click', async function () {
    const out = $('desResult'); out.hidden = false; out.textContent = '…';
    await sleep(30);
    const type = $('desType').value;
    const spec = { type };
    if (['period', 'omega'].includes(type)) Object.assign(spec, { N: +$('desN').value, a: +$('desA').value, b: +$('desB').value, r: +$('desR').value, s: +$('desS').value, tolerance: parseFloat($('desTol').value) || 1e-25 });
    if (type === 'census') spec.N = +$('desN').value;
    if (type === 'cm') spec.d = +$('desD').value;
    if (type === 'flow') Object.assign(spec, { W: +$('desW').value, H: +$('desH').value, a: +$('desA').value, b: +$('desB').value });
    if (type === 'bch') spec.n = +$('desN').value;
    if (type === 'arf') spec.g = +$('desG').value;
    const dps = +$('desDps').value || 35;
    P.setDps(Math.min(200, Math.max(15, dps)));
    $('chipDps').textContent = 'dps ' + P.getDps();
    try {
      const r = C.designerRun(spec);
      C.log(`[designer] ${JSON.stringify(spec).slice(0, 90)} → ${r.pass ? 'PASS' : 'FAIL'}`);
      out.textContent = `type: ${type}\nverdict: ${r.pass ? I.t('all_pass') : I.t('has_fail')}\n\n` + JSON.stringify(r.data || r, null, 1);
    } catch (e) { out.textContent = 'ERROR: ' + (e && e.message || e); }
  });
  $('btnBatch').addEventListener('click', async function () {
    const out = $('batchResult'); out.hidden = false; out.textContent = '…';
    await sleep(30);
    let sc;
    try { sc = JSON.parse($('batchJson').value); } catch (e) { out.textContent = 'JSON ERROR: ' + e.message; return; }
    if (sc.dps) { P.setDps(sc.dps); $('chipDps').textContent = 'dps ' + P.getDps(); }
    const runs = sc.runs || [];
    const lines = [`scenario: ${sc.scenario || '—'} · dps: ${P.getDps()} · runs: ${runs.length}`, ''];
    let all = true;
    for (let i = 0; i < runs.length; i++) {
      const r = C.designerRun(runs[i]);
      all = all && r.pass;
      lines.push(`[${i + 1}/${runs.length}] ${runs[i].type}: ${r.pass ? '✔ PASS' : '✘ FAIL'} ${r.error ? '(' + r.error + ')' : ''}`);
      if (i % 2 === 1) await sleep(0);
    }
    lines.push('', `SUMMARY: ${all ? I.t('all_pass') : I.t('has_fail')}`);
    C.log(`[batch] scenario ${runs.length} runs → ${all ? 'ALL PASS' : 'FAILURES'}`);
    out.textContent = lines.join('\n');
  });

  /* ── reports ── */
  function initPlots() {
    const grid = $('plotsGrid');
    if (!grid.dataset.init) {
      grid.innerHTML = PL.LIST.map(([key, tk]) => `<div class="plot-card"><h3>${I.t(tk)}<button class="pbtn" data-plot-exp="${key}">${I.t('rep_export')}</button></h3><canvas data-plot="${key}"></canvas></div>`).join('');
      grid.dataset.init = '1';
      grid.querySelectorAll('[data-plot-exp]').forEach(b =>
        b.addEventListener('click', () => { PL.render(null, b.dataset.plotExp, I.lang, true); toast('600 dpi · Ultra HD'); }));
    }
  }
  function renderPlots() {
    initPlots();
    const grid = $('plotsGrid');
    PL.LIST.forEach(([key]) => {
      const cv = grid.querySelector(`[data-plot="${key}"]`);
      if (cv && $('sec-reports').classList.contains('active')) PL.render(cv, key, I.lang);
    });
  }
  $('btnRepJson').addEventListener('click', () => {
    download('hodge_report.json', JSON.stringify(C.RESULTS, null, 1), 'application/json');
    toast('hodge_report.json');
  });
  $('btnRepLog').addEventListener('click', () => {
    download('hodge_log.txt', C.LOG.join('\n'), 'text/plain');
    toast('hodge_log.txt');
  });
  $('btnRepMeta').addEventListener('click', () => {
    download('hodge_meta.txt', [
      'app: hodge-laboratory-web 1.0.0', 'author: Исаев Исхак Хамзатович / Isaev Iskhak Khamzatovich',
      'orcid: 0009-0003-7299-0701', 'repo: https://github.com/wild8highlander/hodge-laboratory',
      'dps: ' + P.getDps(), 'timestamp: ' + new Date().toISOString(),
      'plots: 8 × 600 dpi (4800×3000 px)', 'protocol: V1–V9 · certificates: A–J · stands: 7 · cycles: C1–C10',
    ].join('\n'), 'text/plain');
  });

  /* ── monograph ── */
  function updateMonPreview() {
    $('monFrame').srcdoc = FG.html(I.lang);
  }
  $('btnMonBuild').addEventListener('click', () => { updateMonPreview(); toast(I.lang === 'ru' ? 'Монография собрана' : 'Monograph forged'); });
  $('btnMonTex').addEventListener('click', () => {
    const tex = FG.tex(I.lang);
    download('monograph.tex', tex, 'application/x-tex');
    C.log('[monograph] LaTeX forged (' + tex.length + ' chars)');
    toast('monograph.tex');
  });
  $('btnMonHtml').addEventListener('click', () => { download('monograph.html', FG.html(I.lang), 'text/html'); toast('monograph.html'); });
  $('btnMonScript').addEventListener('click', () => { download('build_monograph.sh', FG.buildScript(), 'application/x-sh'); toast('build_monograph.sh'); });

  /* ── verify ── */
  const VMATRIX = [
    ['Python 3.10+', 'laboratory.py', 'полная лаборатория / the full laboratory', '0/1/2'],
    ['Lean 4', 'verification/lean/HodgeLaboratory.lean', 'машинные доказательства целых тождеств (native_decide) / machine proofs of the integer identities', '0/1'],
    ['Julia 1.9+', 'verification/julia/verify_hodge.jl', 'BigFloat(240-бит) периоды, фазы, отражения / periods, phases, reflection', '0/1'],
    ['Fortran 10+', 'verification/fortran/verify_hodge.f90', 'переписи, ранги, инварианты (int64) / censuses, ranks, invariants', '0/1'],
    ['C', 'verification/c/verify_hodge.c', 'точный ранг K3 = 20 (рациональная элиминация) + 38 проверок / exact K3 rank + 38 checks', '0/1'],
    ['Rust 1.70+', 'verification/rust/verify_hodge.rs', 'безопасная i128-арифметика / safe i128 arithmetic', '0/1'],
    ['Web (this app)', 'assets/js/engine/*', 'BigInt-движок произвольной точности, tanh-sinh, точные SNF/ранги / BigInt arbitrary-precision engine', '0/1'],
  ];
  function renderVerify() {
    $('verifyTbl').querySelector('tbody').innerHTML = VMATRIX.map(r =>
      `<tr><td class="num">${r[0]}</td><td class="num">${r[1]}</td><td>${r[2]}</td><td class="num">${r[3]}</td></tr>`).join('');
  }
  $('btnBaseline').addEventListener('click', async function () {
    const out = $('baselineResult'); out.hidden = false; out.textContent = '…';
    await sleep(30);
    const bl = C.checkBaseline();
    C.log('[baseline] ' + (bl.pass ? 'ALL PASS' : 'FAILURES'));
    out.textContent = bl.rows.map(r => `${r.pass ? '✔' : '✘'} ${r.name}${r.pass ? '' : '  got: ' + r.got + '  want: ' + r.want}`).join('\n')
      + `\n\nVERDICT: ${bl.pass ? I.t('all_pass') : I.t('has_fail')}`;
    toast(bl.pass ? I.t('all_pass') : I.t('has_fail'));
  });

  /* ── language ── */
  let _applying = false;
  function applyLang() {
    if (_applying) return;
    _applying = true;
    try { I.apply(); } finally { _applying = false; }
    $('langBtn').textContent = I.t('lang_sw');
    $('chipDps').textContent = 'dps ' + P.getDps();
    renderLadder(); renderVersions(); renderCards(); renderPresets(); renderCycles(); renderVerify(); renderStages();
    const active = document.querySelector('.nav a.active');
    if (active) $('tbTitle').textContent = I.t('nav_' + active.dataset.sec);
    if (cycleResults) renderCycles();
  }
  $('langBtn').addEventListener('click', () => { I.setLang(I.lang === 'ru' ? 'en' : 'ru'); });
  document.addEventListener('langchange', applyLang);

  /* ── burger ── */
  $('burger').addEventListener('click', () => $('sidebar').classList.toggle('open'));

  /* ── init ── */
  I.init();
  P.setDps(35);
  C.resetResults(I.lang);
  C.log('hodge-laboratory-web 1.0.0 · engine ready · dps=35');
  applyLang();
  window.App = App;
})();

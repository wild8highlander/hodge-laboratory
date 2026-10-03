/* chess-oracle · app.js — game controller, UI, live audit wiring.

   Modes:  vsOracle (human vs perfect tablebase play), auto (perfect vs
   perfect), vsParticles (human vs the three-layer greedy solver),
   editor (set up any legal KRK/KQK position and probe it).

   Every reached position is audited (audit.js) and logged; the meter shows
   the DTM value; the tree pane unfolds the explicit certificate (E3); the
   E1 pane replays the particles-vs-oracle experiment; the table pane shows
   the integrity gate against the frozen build certificate. */

(function (global) {
  'use strict';

  var C = global.ChessOracle.chess;
  var TB = global.ChessOracle.tb;
  var AUD = global.ChessOracle.audit;
  var I18N = global.ChessOracle.i18n;

  var GLYPH = {};
  GLYPH[C.WK] = '\u2654'; GLYPH[C.WR] = '\u2656'; GLYPH[C.WQ] = '\u2655';
  GLYPH[C.WN] = '\u2658'; GLYPH[C.WP] = '\u2659';
  GLYPH[-C.WK] = '\u265A'; GLYPH[-C.WR] = '\u265C'; GLYPH[-C.WQ] = '\u265B';
  GLYPH[-C.WN] = '\u265E'; GLYPH[-C.WP] = '\u265F';

  var KIND_BY_CODE = {};
  KIND_BY_CODE[C.WR] = 'krk'; KIND_BY_CODE[C.WQ] = 'kqk';
  KIND_BY_CODE[C.WN] = 'knk'; KIND_BY_CODE[C.WP] = 'kpk';

  var S = {
    tbKind: 'krk', tb: null, pos: null,
    mode: 'vsOracle', humanSide: -1,     // default: human defends with Black
    selected: null, targets: [], hintSquares: [],
    history: [], over: null, timer: null, flip: false,
    lastMove: null, audit: { visited: 0, passed: 0, failed: 0 },
    explorer: null, editor: { piece: C.WR, side: 1, draft: null },
    treeBusy: false, e1Busy: false,
    traps: { on: false, res: null },
    vortex: { on: false, busy: false, field: null, metrics: null,
              cls: null, gateOk: true, view: null, flipSeen: false }
  };

  function $(id) { return document.getElementById(id); }
  function t(k) { return I18N.t(k); }

  /* ── board rendering ─────────────────────────────────────────────── */
  function buildBoard() {
    var box = $('board');
    box.innerHTML = '';
    for (var idx = 0; idx < 64; idx++) {
      var cell = document.createElement('div');
      var r = idx >> 3, f = idx & 7;
      var sq = S.flip ? 16 * (7 - r) + (7 - f) : 16 * r + f;
      cell.id = 'sq-' + sq;
      cell.className = 'cell ' + (((r + f) % 2 === 0) ? 'light' : 'dark');
      cell.dataset.sq = sq;
      cell.addEventListener('click', onCellClick);
      box.appendChild(cell);
    }
  }

  function renderBoard() {
    for (var idx = 0; idx < 64; idx++) {
      var r = idx >> 3, f = idx & 7;
      var sq = S.flip ? 16 * (7 - r) + (7 - f) : 16 * r + f;
      var cell = $('sq-' + sq);
      if (!cell) continue;
      var p = S.pos ? S.pos.board[sq] : 0;
      cell.textContent = p ? (GLYPH[p] || '?') : '';
      cell.classList.toggle('sel', S.selected === sq);
      cell.classList.toggle('target', S.targets.some(function (mv) {
        return mv.t === sq;
      }));
      cell.classList.toggle('occupied', p !== 0);
      cell.classList.toggle('hint', S.hintSquares.indexOf(sq) >= 0);
      var hi = S.traps.on && S.traps.res && S.traps.res.highlight
               ? S.traps.res.highlight[sq] : null;
      cell.classList.toggle('trap-hi', hi === 'trap');
      cell.classList.toggle('slack-hi', hi === 'slack');
      cell.classList.toggle('waste-hi', hi === 'waste');
      cell.classList.toggle('resist-hi', hi === 'resist');
      var isLast = S.lastMove && (S.lastMove.f === sq || S.lastMove.t === sq);
      cell.classList.toggle('last', !!isLast);
    }
  }

  /* ── status, meter, move list ────────────────────────────────────── */
  function turnLabel() {
    if (S.over) {
      return {
        mate: S.history.length && S.history[S.history.length - 1].byWhite
              ? t('status.mateWhite') : t('status.mateBlack'),
        stalemate: t('status.stalemate'),
        capture: t('status.capture'),
        drawnW: t('status.drawnW'),
        editor: t('status.editor')
      }[S.over] || '';
    }
    var humanTurn = S.mode !== 'auto' &&
                    S.pos && S.pos.side === S.humanSide;
    if (S.mode === 'editor') return t('status.editor');
    if (S.mode === 'auto') return t('status.auto');
    if (humanTurn) return t('status.yourTurn');
    return S.mode === 'vsParticles' ? t('status.particleTurn')
                                    : t('status.oracleTurn');
  }

  function renderMeter() {
    var valueEl = $('meter-value'), unitEl = $('meter-unit'),
        verdictEl = $('meter-verdict'), bar = $('meter-bar-fill'),
        par = $('meter-par'), horizon = $('meter-horizon');
    if (!S.pos || !S.tb) return;
    var st = TB.stateOfPosition(S.pos);
    var maxPlies = S.tb.spec.stats.max_plies;
    horizon.textContent = maxPlies;
    if (st === null) {                       // piece captured: K vs K
      valueEl.textContent = '—';
      unitEl.textContent = '';
      verdictEl.textContent = t('meter.drawn');
      bar.style.width = '0%';
      par.textContent = '';
      return;
    }
    var info = S.tb.probe(st);
    if (info.mate) {
      valueEl.textContent = '0';
      unitEl.textContent = '';
      verdictEl.textContent = t('meter.mated');
      bar.style.width = '100%';
      par.textContent = '';
    } else if (info.drawn) {
      valueEl.textContent = '∞';
      unitEl.textContent = '';
      verdictEl.textContent = t('meter.drawn');
      bar.style.width = '0%';
      par.textContent = '';
    } else {
      valueEl.textContent = info.plies;
      unitEl.textContent = t('meter.plies');
      verdictEl.textContent = '';
      bar.style.width = Math.round(100 * info.plies / maxPlies) + '%';
      par.textContent = '';
    }
  }

  function renderHistory() {
    var box = $('move-list');
    box.innerHTML = '';
    for (var i = 0; i < S.history.length; i++) {
      var h = S.history[i];
      var row = document.createElement('div');
      row.className = 'move-row' + (h.optimal ? ' optimal' : ' slack');
      var num = document.createElement('span');
      num.className = 'move-num';
      num.textContent = Math.floor(i / 2) + 1 + (h.byWhite ? '.' : '…');
      var uci = document.createElement('span');
      uci.className = 'move-uci';
      uci.textContent = h.uci;
      var val = document.createElement('span');
      val.className = 'move-val';
      val.textContent = h.valueLabel;
      row.appendChild(num); row.appendChild(uci); row.appendChild(val);
      box.appendChild(row);
    }
    box.scrollTop = box.scrollHeight;
  }

  /* ── live audit ──────────────────────────────────────────────────── */
  function auditCurrent() {
    if (!S.pos || !S.tb) return;
    var st = TB.stateOfPosition(S.pos);
    if (st === null) return;
    var res = AUD.auditState(S.tb, S.pos, st);
    S.audit.visited++;
    if (res.verdict) S.audit.passed++; else S.audit.failed++;
    renderAudit(res);
  }

  function renderAudit(last) {
    $('audit-visited').textContent = S.audit.visited;
    $('audit-passed').textContent = S.audit.passed;
    $('audit-failed').textContent = S.audit.failed;
    var banner = $('audit-banner');
    var integOk = S.tb && S.tb.allOk;
    banner.textContent = integOk ? t('audit.integrityOk')
                                 : t('audit.integrityFail');
    banner.className = 'banner ' + (integOk ? 'ok' : 'fail');
    if (last) {
      var empty = $('audit-log').querySelector('.audit-empty');
      if (empty) empty.remove();
      var row = document.createElement('div');
      row.className = 'audit-row ' + (last.verdict ? 'ok' : 'fail');
      row.textContent =
        (last.isWhite ? 'W' : 'B') + ' · v=' + last.value + ' · ' +
        last.reason + ' · ' + (last.verdict ? 'PASS' : 'FAIL');
      var log = $('audit-log');
      log.appendChild(row);
      while (log.childNodes.length > 60) log.removeChild(log.firstChild);
      log.scrollTop = log.scrollHeight;
    }
    if (S.audit.visited === 0) {
      $('audit-log').innerHTML = '';
      var empty = document.createElement('div');
      empty.className = 'audit-empty';
      empty.textContent = t('audit.empty');
      $('audit-log').appendChild(empty);
    }
  }

  /* ── game flow ───────────────────────────────────────────────────── */
  function clearTimer() {
    if (S.timer) { clearTimeout(S.timer); S.timer = null; }
  }

  function sampleNewGame() {
    var rng = global.ChessOracle.e1.mulberry32((Date.now() & 0xffffffff) >>> 0);
    var s = global.ChessOracle.e1.sampleWonState(S.tb, rng);
    if (!s) {
      // KNK: a won state does not exist (T15) — fixed demonstration setup
      S.pos = C.Position.fromFEN('8/8/8/1k6/8/3K4/8/2N5 w - - 0 1');
    } else {
      S.pos = s.pos.clone();
    }
    startFromCurrent();
  }

  function startFromCurrent() {
    clearTimer();
    S.history = [];
    S.over = null;
    S.selected = null; S.targets = []; S.hintSquares = [];
    S.lastMove = null;
    S.audit = { visited: 0, passed: 0, failed: 0 };
    renderAudit(null);
    renderAll();
    renderTreePane();
    auditCurrent();
    scheduleSideToMove();
  }

  function scheduleSideToMove() {
    if (S.over || !S.pos) return;
    var st = TB.stateOfPosition(S.pos);
    if (st === null) { S.over = 'capture'; renderAll(); return; }
    var info = S.tb.probe(st);
    if (info.mate) { S.over = 'mate'; renderAll(); return; }
    if (S.pos.legalMoves().length === 0) {
      S.over = 'stalemate'; renderAll(); return;
    }
    var side = S.pos.side;
    var machineSide = null;
    if (S.mode === 'auto') machineSide = side;
    else if (S.mode === 'vsOracle' && side !== S.humanSide) machineSide = side;
    else if (S.mode === 'vsParticles' && side !== S.humanSide) machineSide = side;
    if (machineSide === null) return;
    clearTimer();
    S.timer = setTimeout(function () {
      var m = (S.mode === 'vsParticles')
        ? new global.ChessOracle.particles.ParticleSolver().chooseMove(S.pos)
        : pickOracleMove();
      if (m) applyMove(m, { machine: true });
    }, 620);
  }

  function pickOracleMove() {
    var st = TB.stateOfPosition(S.pos);
    if (st === null) return null;
    var opts = TB.optimalMoves(S.tb, S.pos, st);
    return opts.length ? opts[0] : (S.pos.legalMoves()[0] || null);
  }

  function applyMove(m, meta) {
    meta = meta || {};
    var byWhite = S.pos.side === 1;
    var stBefore = TB.stateOfPosition(S.pos);
    var vBefore = stBefore === null ? null : S.tb.probe(stBefore);
    var opts = (vBefore && vBefore.won)
      ? TB.optimalMoves(S.tb, S.pos, stBefore) : [];
    var isOptimal = opts.some(function (o) {
      return o.f === m.f && o.t === m.t;
    });
    var captured = S.pos.board[m.t] !== 0;
    var undo = S.pos.make(m);
    var h = {
      undo: undo, uci: C.sqName(m.f) + C.sqName(m.t), byWhite: byWhite,
      optimal: isOptimal && !meta.machine ? true
              : (meta.machine ? null : false),
      valueLabel: '', promoSwitch: false
    };
    S.history.push(h);
    S.lastMove = { f: m.f, t: m.t };
    S.selected = null; S.targets = []; S.hintSquares = [];

    // promotion boundary: after a KPK promotion the position left the
    // KPK space — the frozen KQK certificate takes over (honest switch,
    // visible in the selector and in the kind note)
    if (undo.promo && S.tbKind === 'kpk') {
      S.tbKind = 'kqk';
      S.tb = global.ChessOracle.tb.getLoaded('kqk') || S.tb;
      h.promoSwitch = true;
      $('table-select').value = 'kqk';
      setKindNote();
      renderTablePane();
    }

    // game-over analysis
    var stAfter = TB.stateOfPosition(S.pos);
    var info = stAfter === null ? null : S.tb.probe(stAfter);
    var valueLabel = '?';
    if (stAfter === null || captured) {
      S.over = 'capture';
      valueLabel = '½';
    } else if (info.mate) {
      S.over = 'mate';
      valueLabel = '#';
    } else if (S.pos.legalMoves().length === 0) {
      S.over = 'stalemate';
      valueLabel = '½';
    } else if (!info.won && byWhite && vBefore && vBefore.won) {
      S.over = 'drawnW';
      valueLabel = '½';
    } else if (info.won) {
      valueLabel = String(info.plies);
    } else {
      valueLabel = '½';        // drawn endgame (KNK): the game goes on
    }
    h.valueLabel = valueLabel;
    if (h.optimal === null) h.optimal = isOptimal;

    renderHistory();
    renderAll();
    auditCurrent();
    if (!S.over) scheduleSideToMove();
    return undo;
  }

  function undoMove() {
    clearTimer();
    if (!S.history.length) return;
    var restoreKind = null;
    // pop plies until it is the human's turn again (max 2: machine + human)
    var pops = 0;
    while (S.history.length && pops < 2) {
      var h = S.history[S.history.length - 1];
      var lastIsMachine = (S.mode !== 'auto') &&
        (h.byWhite ? 1 : -1) !== S.humanSide;
      if (h.promoSwitch) restoreKind = 'kpk';
      S.pos.unmake(S.history.pop().undo);
      pops++;
      if (!lastIsMachine) break;       // popped the human's own move
      if (!S.history.length) break;
      // popped a machine move: also pop the human move preceding it
      if (S.mode === 'auto') break;
      var next = S.history[S.history.length - 1];
      if (((next.byWhite ? 1 : -1) === S.humanSide)) {
        if (next.promoSwitch) restoreKind = 'kpk';
        S.pos.unmake(S.history.pop().undo);
        pops++;
      }
      break;
    }
    S.over = null;
    if (restoreKind && S.tbKind !== restoreKind) {
      S.tbKind = restoreKind;
      S.tb = global.ChessOracle.tb.getLoaded(restoreKind) || S.tb;
      $('table-select').value = restoreKind;
      setKindNote();
      renderTablePane();
    }
    var prev = S.history.length ? S.history[S.history.length - 1] : null;
    S.lastMove = prev ? { f: prev.undo.f, t: prev.undo.t } : null;
    S.selected = null; S.targets = []; S.hintSquares = [];
    S.audit = { visited: 0, passed: 0, failed: 0 };
    renderAudit(null);
    renderHistory();
    renderAll();
    auditCurrent();
    scheduleSideToMove();
  }

  function onCellClick(ev) {
    if (S.mode === 'editor') { editorClick(ev); return; }
    if (!S.pos || S.over || S.mode === 'auto') return;
    if (S.pos.side !== S.humanSide) return;
    var sq = +(ev.currentTarget.dataset.sq);
    var p = S.pos.board[sq];
    if (S.selected !== null) {
      var m = S.targets.filter(function (mv) { return mv.t === sq; })[0];
      if (m) { applyMove(m, { machine: false }); return; }
    }
    if (p !== 0 && (p > 0) === (S.pos.side > 0)) {
      S.selected = sq;
      S.targets = S.pos.legalMoves().filter(function (mv) {
        return mv.f === sq;
      });
    } else {
      S.selected = null; S.targets = [];
    }
    S.hintSquares = [];
    renderBoard();
  }

  function showHint() {
    if (!S.pos || S.over) return;
    var st = TB.stateOfPosition(S.pos);
    if (st === null) return;
    var opts = TB.optimalMoves(S.tb, S.pos, st);
    S.hintSquares = opts.map(function (o) { return o.t; });
    renderBoard();
    setTimeout(function () {
      S.hintSquares = [];
      renderBoard();
    }, 1600);
  }

  /* ── editor ──────────────────────────────────────────────────────── */
  function editorEnter() {
    S.editor.draft = new Int8Array(128);
    renderBoard();
    vortexOnPositionChange();      // the layer hides for a draft position
  }

  function editorClick(ev) {
    var sq = +(ev.currentTarget.dataset.sq);
    var d = S.editor.draft;
    if (!d) return;
    if (d[sq] !== 0) { d[sq] = 0; renderEditor(); return; }
    var piece = S.editor.piece;
    if (piece === C.WK) {
      var oldW = findIn(d, C.WK);
      if (oldW >= 0) d[oldW] = 0;
    } else if (piece === -C.WK) {
      var oldB = findIn(d, -C.WK);
      if (oldB >= 0) d[oldB] = 0;
    } else {
      var oldS = findStrong(d);
      if (oldS >= 0) d[oldS] = 0;
    }
    d[sq] = piece;
    renderEditor();
  }

  function findIn(b, code) {
    for (var sq = 0; sq < 128; sq++) {
      if (!(sq & 0x88) && b[sq] === code) return sq;
    }
    return -1;
  }
  function findStrong(b) {
    for (var sq = 0; sq < 128; sq++) {
      if (!(sq & 0x88) && (b[sq] === C.WR || b[sq] === C.WQ ||
                           b[sq] === C.WN || b[sq] === C.WP)) return sq;
    }
    return -1;
  }

  function renderEditor() {
    var d = S.editor.draft;
    S.pos = new C.Position();
    S.pos.board = d.slice();
    S.pos.side = S.editor.side;
    S.history = []; S.over = null; S.lastMove = null;
    renderBoard();
    renderMeter();
    renderHistory();
  }

  function editorApply() {
    var pos = new C.Position();
    pos.board = S.editor.draft.slice();
    pos.side = S.editor.side;
    var legal = pos.isLegalSetup();
    if (!legal.ok) {
      $('status-line').textContent = t('editor.invalid') + ': ' + legal.why;
      return;
    }
    S.pos = pos;
    // the endgame follows the placed strong piece (the tables are
    // per-endgame; probing across spaces would be meaningless)
    var kind = KIND_BY_CODE[pos.strongCode()] || 'krk';
    S.tbKind = kind;
    S.tb = global.ChessOracle.tb.getLoaded(kind) || S.tb;
    $('table-select').value = kind;
    S.mode = 'vsOracle';
    $('mode-select').value = 'vsOracle';
    $('editor-bar').classList.add('hidden');
    $('side-select-wrap').classList.remove('hidden');
    setKindNote();
    startFromCurrent();
  }

  /* ── panes ───────────────────────────────────────────────────────── */
  function renderTablePane() {
    if (!S.tb) return;
    var box = $('table-out');
    box.innerHTML = '';
    var grid = document.createElement('table');
    grid.className = 'checks';
    var head = grid.insertRow();
    [t('table.checks'), t('table.expected'), t('table.actual'),
     t('table.ok')].forEach(function (h) {
      var th = document.createElement('th'); th.textContent = h;
      head.appendChild(th);
    });
    S.tb.checks.forEach(function (c) {
      var row = grid.insertRow();
      [c.name, String(c.expected), String(c.actual),
       c.ok ? 'PASS' : 'FAIL'].forEach(function (v, i) {
        var cell = row.insertCell(i);
        cell.textContent = v;
        if (i === 3) cell.className = v === 'PASS' ? 'ok' : 'fail';
      });
    });
    box.appendChild(grid);
    var stats = document.createElement('p');
    stats.className = 'mono';
    stats.textContent = t('table.stats') + ': ' +
      JSON.stringify(S.tb.spec.stats);
    box.appendChild(stats);
    var pack = document.createElement('p');
    pack.className = 'mono small';
    pack.textContent = t('table.pack') + ': ' +
      (global.CHESS_ORACLE_DATA[S.tb.kind].packing || '');
    box.appendChild(pack);
  }

  function renderTreePane() {
    var box = $('tree-out');
    box.innerHTML = '';
    if (!S.pos || !S.tb) return;
    var st = TB.stateOfPosition(S.pos);
    var info = st === null ? null : S.tb.probe(st);
    if (!info || !info.won || S.pos.side !== 1) {
      var p = document.createElement('p');
      p.textContent = t('tree.onlyWon');
      box.appendChild(p);
      return;
    }
    var btn = document.createElement('button');
    btn.className = 'btn';
    btn.textContent = t('tree.compute');
    btn.addEventListener('click', function () {
      btn.disabled = true;
      btn.textContent = t('loading.computing');
      setTimeout(function () { computeTree(st, box); }, 30);
    });
    box.appendChild(btn);
  }

  function computeTree(st, box) {
    if (!S.explorer || S.explorer.tb !== S.tb) {
      S.explorer = new global.ChessOracle.tree.TreeExplorer(S.tb);
    } else { S.explorer.reset(); }
    var total = S.explorer.treeSize(st);
    var prof = S.explorer.levelProfile(st);
    box.innerHTML = '';
    var rows = [
      [t('tree.nodes'), total.toLocaleString()],
      [t('tree.memo'), S.explorer.memo.size.toLocaleString()],
      [t('tree.vsTable'),
       S.tb.spec.stats.states.toLocaleString() + ' · ×' +
       (total / S.tb.spec.stats.states).toFixed(2)]
    ];
    var grid = document.createElement('table');
    grid.className = 'checks';
    rows.forEach(function (r) {
      var row = grid.insertRow();
      row.insertCell(0).textContent = r[0];
      row.insertCell(1).textContent = r[1];
    });
    box.appendChild(grid);
    var cap = document.createElement('p');
    cap.className = 'small';
    cap.textContent = t('tree.profile');
    box.appendChild(cap);
    var bars = document.createElement('div');
    bars.className = 'profile';
    var maxNodes = Math.max.apply(null, prof.profile.map(function (x) {
      return x.nodes;
    }));
    prof.profile.forEach(function (lv) {
      var line = document.createElement('div');
      line.className = 'profile-row';
      var label = document.createElement('span');
      label.className = 'profile-label';
      label.textContent = lv.plies;
      var barBox = document.createElement('div');
      barBox.className = 'profile-bar';
      var fill = document.createElement('div');
      fill.className = 'profile-fill';
      fill.style.width =
        Math.max(1, Math.round(100 * lv.nodes / maxNodes)) + '%';
      barBox.appendChild(fill);
      var val = document.createElement('span');
      val.className = 'profile-val';
      val.textContent = lv.nodes.toLocaleString() +
        (lv.complete ? '' : '+');
      line.appendChild(label);
      line.appendChild(barBox);
      line.appendChild(val);
      bars.appendChild(line);
    });
    box.appendChild(bars);
    if (prof.truncated) {
      var tr = document.createElement('p');
      tr.className = 'small warn';
      tr.textContent = t('tree.truncated');
      box.appendChild(tr);
    }
    var frozen = document.createElement('p');
    frozen.className = 'small';
    frozen.textContent = t('tree.frozenE3');
    box.appendChild(frozen);
  }

  function renderE1Pane() {
    var box = $('e1-out');
    box.innerHTML = '';
    var p = document.createElement('p');
    p.className = 'small';
    p.textContent = t('e1.desc');
    box.appendChild(p);
    if (S.tb && S.tb.spec.stats.won === 0) {
      var q = document.createElement('p');
      q.className = 'small warn';
      q.textContent = t('e1.noWon');
      box.appendChild(q);
    }
  }

  function runE1() {
    if (S.e1Busy || !S.tb) return;
    if (S.tb.spec.stats.won === 0) return;    // KNK: E1 is undefined (T15)
    S.e1Busy = true;
    var count = Math.max(50, Math.min(5000, +$('e1-count').value || 500));
    var seed = (+$('e1-seed').value || 42) >>> 0;
    $('e1-run').disabled = true;
    $('e1-run').textContent = t('loading.computing');
    setTimeout(function () {
      var solver = new global.ChessOracle.particles.ParticleSolver();
      var res = global.ChessOracle.e1.runE1(S.tb, count, seed, solver);
      var box = $('e1-out');
      box.innerHTML = '';
      var p = document.createElement('p');
      p.className = 'small';
      p.textContent = t('e1.desc');
      box.appendChild(p);
      var grid = document.createElement('table');
      grid.className = 'checks';
      function row(a, b, cls) {
        var r = grid.insertRow();
        r.insertCell(0).textContent = a;
        r.insertCell(1).textContent = b;
        if (cls) r.cells[1].className = cls;
      }
      row(t('e1.count') + ' (' + t('e1.seed') + ' ' + res.seed + ')',
          res.count);
      row(t('e1.saveRate'),
          (100 * res.save_rate).toFixed(2) + '%', 'warn');
      row(t('e1.optimalRate'),
          (100 * res.optimal_rate).toFixed(2) + '%');
      row(t('e1.meanDelta'), res.mean_delta_plies.toFixed(4));
      row(t('e1.maxDelta'), String(res.max_delta_plies));
      if (res.frozen) {
        row(t('e1.frozen'), (100 * res.frozen.save_rate).toFixed(2) + '% / ' +
            (100 * res.frozen.optimal_rate).toFixed(2) + '% / ' +
            res.frozen.mean_delta_plies.toFixed(4));
      } else {
        row(t('e1.frozen'), t('e1.frozenNone'));
      }
      box.appendChild(grid);
      res.examples.forEach(function (ex) {
        var e = document.createElement('p');
        e.className = 'mono small';
        e.textContent = (ex.lost ? 'LOST ' : 'SLOW ') + ex.move + ' · ' +
          ex.fen + ' · ' + ex.dtm_before_moves + '→' +
          (ex.dtm_after_moves === null ? '½' : ex.dtm_after_moves);
        box.appendChild(e);
      });
      $('e1-run').disabled = false;
      $('e1-run').textContent = t('e1.run');
      S.e1Busy = false;
    }, 30);
  }

  /* ── trap classification layer (T17) ─────────────────────────────── */
  function computeTraps() {
    if (!S.traps.on || !S.pos || !S.tb) return null;
    if (S.mode === 'editor') {
      return { kind: S.tbKind, editor: true };
    }
    if (S.over) {
      return { kind: S.tbKind, terminal: true };
    }
    var TR = global.ChessOracle.traps;
    var res;
    try {
      res = TR.classify(S.tb, S.pos);
    } catch (err) {
      console.error('traps:', err);
      return { kind: S.tbKind, terminal: true };
    }
    res.highlight = TR.highlightMap(res);
    return res;
  }

  function refreshTraps() {
    if (!S.traps.on) { S.traps.res = null; return; }
    S.traps.res = computeTraps();
  }

  function toggleTraps() {
    S.traps.on = !S.traps.on;
    $('btn-traps').classList.toggle('active', S.traps.on);
    refreshTraps();
    renderBoard();
    renderTrapsPane();
  }

  function renderTrapsPane() {
    var box = $('traps-out');
    if (!box) return;
    box.innerHTML = '';
    var desc = document.createElement('p');
    desc.className = 'small';
    desc.textContent = t('traps.desc');
    box.appendChild(desc);
    var legend = document.createElement('p');
    legend.className = 'small';
    legend.textContent = t('traps.legend');
    box.appendChild(legend);
    if (S.tbKind === 'knk') {
      var knk = document.createElement('p');
      knk.className = 'small warn';
      knk.textContent = t('traps.knk');
      box.appendChild(knk);
    }
    var res = S.traps.on ? S.traps.res : null;
    if (!res) {
      var idle = document.createElement('p');
      idle.className = 'small';
      idle.textContent = t('traps.none');
      box.appendChild(idle);
      return;
    }
    if (res.editor) {
      var ed = document.createElement('p');
      ed.className = 'small warn';
      ed.textContent = t('traps.editor');
      box.appendChild(ed);
      return;
    }
    if (res.terminal) {
      var tm = document.createElement('p');
      tm.className = 'small warn';
      tm.textContent = t('traps.terminal');
      box.appendChild(tm);
      return;
    }
    var grid = document.createElement('table');
    grid.className = 'checks';
    function row(a, b, cls) {
      var r = grid.insertRow();
      r.insertCell(0).textContent = a;
      r.insertCell(1).textContent = b;
      if (cls) r.cells[1].className = cls;
    }
    var c = res.counts;
    row(t('traps.verdict'),
        t('traps.cls.' + res.moverClass) +
        (res.d != null ? ' · DTM ' + res.d : ''));
    row(t('traps.moves'), c.moves);
    if (res.moverClass === 'WIN') {
      row(t('traps.optimal'), c.optimal);
      row(t('traps.waste'), c.waste +
          (c.waste ? ' · ' + t('traps.wasteMean') + ' ' +
           res.ddtmMean.toFixed(2) + ' ' + t('traps.plies') +
           ' (max ' + res.ddtmMax + ')' : ''));
      row(t('traps.slack'), c.slack,
          c.slack ? 'warn' : null);
    } else if (res.moverClass === 'DRAW') {
      row(t('traps.trap'), c.trap,
          c.trap ? 'fail' : 'ok');
      if (c.trap) {
        row(t('traps.deepest'), res.deepestTrap + ' ' + t('traps.plies'));
      }
      row(t('traps.keep'), c.keep);
    } else {
      row(t('traps.resist'), c.resist);
      row(t('traps.fast'), c.fast +
          (c.fast ? ' · ' + t('traps.accelMean') + ' ' +
           res.accelMean.toFixed(2) + ' ' + t('traps.plies') +
           ' (max ' + res.accelMax + ')' : ''));
    }
    box.appendChild(grid);

    // the per-move rows: traps first (the user's question), then slack
    function moveRows(cls, labelKey, fmt) {
      var hits = res.entries.filter(function (en) {
        return en.cls === cls;
      });
      if (!hits.length) return;
      var p = document.createElement('p');
      p.className = 'small ' + (cls === 'trap' ? 'fail-text' : 'warn');
      p.textContent = t(labelKey) + ' (' + hits.length + '):';
      box.appendChild(p);
      hits.slice(0, 8).forEach(function (en) {
        var e = document.createElement('p');
        e.className = 'mono small';
        e.textContent = en.uci + ' ' + fmt(en);
        box.appendChild(e);
      });
      if (hits.length > 8) {
        var more = document.createElement('p');
        more.className = 'mono small';
        more.textContent = '… +' + (hits.length - 8);
        box.appendChild(more);
      }
    }
    moveRows('trap', 'traps.trap', function (en) {
      return t('traps.row.trap') + ' ' + (en.child.plies + 1) + ' ' +
             t('traps.plies');
    });
    moveRows('slack', 'traps.slack', function () {
      return t('traps.row.slack');
    });
    if (res.moverClass === 'WIN' && res.ddtmMax >= 3) {
      moveRows('waste', 'traps.waste', function (en) {
        return t('traps.row.waste') + ' ' + en.ddtm + ' ' +
               t('traps.plies');
      });
    }

    // frozen census + the E1 tie-in
    var frozen = document.createElement('p');
    frozen.className = 'small';
    if (res.frozen) {
      var bd = res.frozen.btmDrawn, ww = res.frozen.wtmWon;
      frozen.textContent = t('traps.frozen') + ': ' +
        t('traps.trap') + ' ' + bd.traps.toLocaleString() + ' / ' +
        bd.moves.toLocaleString() + ' (' + bd.states.toLocaleString() +
        ' ' + t('traps.verdict') + ' DRAW/BTM; max ' + bd.maxTraps +
        '); ' + t('traps.slack') + ' ' + ww.slack.toLocaleString() +
        '; ' + t('traps.wasteMean') + ' ' + ww.ddtmMean;
    } else {
      frozen.textContent = t('traps.frozen') + ': ' + t('traps.frozenNone');
    }
    box.appendChild(frozen);
    if (res.frozenE1) {
      var e1 = document.createElement('p');
      e1.className = 'small';
      e1.textContent = t('traps.e1tie') + ': ' +
        (100 * res.frozenE1.save_rate).toFixed(2) + '% / ' +
        (100 * res.frozenE1.optimal_rate).toFixed(2) + '% / ' +
        res.frozenE1.mean_delta_plies.toFixed(4);
      box.appendChild(e1);
    }
  }

  /* ── vortex layer (T16) ───────────────────────────────────────────── */
  function getVortexView() {
    if (!S.vortex.view) {
      var VV = global.ChessOracle.vortexView;
      S.vortex.view = new VV.VortexView($('vortex-canvas'));
    }
    return S.vortex.view;
  }

  function vortexRecompute() {
    if (!S.vortex.on || !S.pos || !S.tb) return;
    if (S.vortex.busy) return;
    S.vortex.busy = true;
    var view = getVortexView();
    setTimeout(function () {
      S.vortex.busy = false;
      if (!S.vortex.on) return;              // toggled off meanwhile
      var field = null, metrics = null, res = null;
      if (S.mode !== 'editor' && S.pos && S.tb) {
        field = global.ChessOracle.vortex.buildField(S.tb, S.pos);
        if (field) {
          metrics = global.ChessOracle.vortex.simulate(field);
          res = global.ChessOracle.vortex.classify(field, metrics);
        }
      }
      S.vortex.field = field;
      S.vortex.metrics = metrics;
      S.vortex.cls = res ? res.cls : null;
      S.vortex.gateOk = res ? res.gateOk : false;
      S.vortex.flipSeen = S.flip;
      $('vortex-canvas').classList.toggle('hidden',
        !S.vortex.on || !field);
      view.setField(field, S.flip);
      view.start();
      renderVortexBadge();
      renderVortexPane();
    }, 30);
  }

  function vortexOnPositionChange() {
    if (!S.vortex.on) return;
    if (S.flip !== S.vortex.flipSeen && S.vortex.field) {
      // same position, mirrored board: re-render only
      S.vortex.flipSeen = S.flip;
      getVortexView().setField(S.vortex.field, S.flip);
      return;
    }
    vortexRecompute();
  }

  function toggleVortex() {
    S.vortex.on = !S.vortex.on;
    $('btn-vortex').classList.toggle('active', S.vortex.on);
    $('vortex-canvas').classList.toggle('hidden', !S.vortex.on);
    var badge = $('vortex-badge');
    if (S.vortex.on) {
      vortexRecompute();
    } else {
      badge.classList.add('hidden');
      getVortexView().stop();
      getVortexView().setField(null, S.flip);
    }
  }

  function renderVortexBadge() {
    var badge = $('vortex-badge');
    if (!S.vortex.on || !S.vortex.cls) {
      badge.classList.add('hidden');
      return;
    }
    var cls = S.vortex.cls;
    var key = cls === 'WIN' ? 'vortex.badge.win'
            : cls === 'LOSS' ? (S.vortex.field && S.vortex.field.terminal
                                ? 'vortex.badge.terminal'
                                : 'vortex.badge.loss')
            : 'vortex.badge.draw';
    var vf = '';
    if (S.vortex.metrics) {
      vf = ' · ' + (100 * S.vortex.metrics.capture_fraction).toFixed(0) + '%';
      if (S.vortex.field && S.vortex.field.dtm != null) {
        vf += ' · DTM ' + S.vortex.field.dtm;
      }
      if (!S.vortex.gateOk) vf += ' · ' + t('vortex.badge.gate');
    }
    badge.textContent = t(key) + vf;
    badge.className = 'vortex-badge ' + cls.toLowerCase();
  }

  function renderVortexPane() {
    var box = $('vortex-out');
    if (!box) return;
    box.innerHTML = '';
    var desc = document.createElement('p');
    desc.className = 'small';
    desc.textContent = t('vortex.desc');
    box.appendChild(desc);
    var legend = document.createElement('p');
    legend.className = 'small';
    legend.textContent = t('vortex.legend');
    box.appendChild(legend);
    if (S.tbKind === 'knk') {
      var knk = document.createElement('p');
      knk.className = 'small warn';
      knk.textContent = t('vortex.knk');
      box.appendChild(knk);
    }
    var metrics = S.vortex.metrics, field = S.vortex.field;
    if (!metrics || !field) {
      var idle = document.createElement('p');
      idle.className = 'small';
      idle.textContent = t('vortex.metrics') + ': —';
      box.appendChild(idle);
      return;
    }
    var grid = document.createElement('table');
    grid.className = 'checks';
    function row(a, b, cls) {
      var r = grid.insertRow();
      r.insertCell(0).textContent = a;
      r.insertCell(1).textContent = b;
      if (cls) r.cells[1].className = cls;
    }
    var tags = { descent: 0, neutral: 0, trap: 0, escape: 0 };
    field.currents.forEach(function (cur) { tags[cur.tag]++; });
    row(t('vortex.table'), field.verdict +
        (field.dtm != null ? ' · DTM ' + field.dtm : ''));
    row(t('vortex.flow'), S.vortex.cls || '—');
    row(t('vortex.capture'),
        (100 * metrics.capture_fraction).toFixed(1) + '%');
    row(t('vortex.free'), metrics.mean_free_radius.toFixed(2));
    row(t('vortex.drift'), metrics.net_drift.toFixed(2));
    row(t('vortex.currents'),
        tags.descent + ' / ' + tags.neutral + ' / ' +
        tags.trap + ' / ' + tags.escape);
    box.appendChild(grid);
    if (!S.vortex.gateOk) {
      var warn = document.createElement('p');
      warn.className = 'small warn';
      warn.textContent = t('vortex.gateFail');
      box.appendChild(warn);
    }
  }
  function setKindNote() {
    var el = $('kind-note');
    if (!el) return;
    var key = null;
    if (S.tbKind === 'knk') key = 'note.knk';
    else if (S.tbKind === 'kpk') key = 'note.kpk';
    else if (S.tbKind === 'kqk' && S.history.some(function (x) {
      return x.promoSwitch;
    })) key = 'note.promoted';
    if (key) {
      el.textContent = t(key);
      el.classList.remove('hidden');
    } else {
      el.textContent = '';
      el.classList.add('hidden');
    }
  }

  function renderAll() {
    refreshTraps();
    renderBoard();
    renderMeter();
    $('status-line').textContent = turnLabel();
    renderTrapsPane();
    vortexOnPositionChange();
  }

  function applyI18n() {
    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      el.textContent = I18N.t(el.dataset.i18n);
    });
    document.querySelectorAll('[data-i18n-title]').forEach(function (el) {
      el.title = I18N.t(el.dataset.i18nTitle);
    });
    document.documentElement.lang = I18N.getLang();
    renderAll();
    setKindNote();
    renderAudit(null);
    renderTablePane();
    renderTreePane();
    renderE1Pane();
    renderTrapsPane();
    renderVortexBadge();
    renderVortexPane();
  }

  function bindControls() {
    $('lang-btn').addEventListener('click', function () {
      I18N.setLang(I18N.getLang() === 'ru' ? 'en' : 'ru');
      applyI18n();
    });
    $('table-select').addEventListener('change', function (ev) {
      loadTablebase(ev.target.value);
    });
    $('mode-select').addEventListener('change', function (ev) {
      S.mode = ev.target.value;
      $('editor-bar').classList.toggle('hidden', S.mode !== 'editor');
      $('side-select-wrap').classList.toggle('hidden',
        S.mode === 'auto' || S.mode === 'editor');
      if (S.mode === 'editor') { clearTimer(); editorEnter(); }
      else sampleNewGame();
    });
    $('side-select').addEventListener('change', function () {
      S.humanSide = +$('side-select').value;
      sampleNewGame();
    });
    $('btn-new').addEventListener('click', function () {
      if (S.mode === 'editor') { editorEnter(); return; }
      sampleNewGame();
    });
    $('btn-restart').addEventListener('click', startFromCurrent);
    $('btn-undo').addEventListener('click', undoMove);
    $('btn-flip').addEventListener('click', function () {
      S.flip = !S.flip;
      buildBoard();
      renderAll();
    });
    $('btn-hint').addEventListener('click', showHint);
    $('btn-vortex').addEventListener('click', toggleVortex);
    $('btn-traps').addEventListener('click', toggleTraps);
    global.addEventListener('resize', function () {
      if (S.vortex.on && S.vortex.view) {
        S.vortex.view.resize();
        S.vortex.view.drawFrame();
      }
    });
    $('ed-apply').addEventListener('click', editorApply);
    $('ed-clear').addEventListener('click', function () {
      S.editor.draft = new Int8Array(128);
      renderEditor();
    });
    document.querySelectorAll('input[name="ed-piece"]').forEach(
      function (r) {
        r.addEventListener('change', function (ev) {
          S.editor.piece = +ev.target.value;
        });
      });
    $('ed-side').addEventListener('change', function (ev) {
      S.editor.side = +ev.target.value;
      if (S.editor.draft) renderEditor();
    });
    document.querySelectorAll('.tab-btn').forEach(function (b) {
      b.addEventListener('click', function () {
        document.querySelectorAll('.tab-btn').forEach(function (x) {
          x.classList.remove('active');
        });
        document.querySelectorAll('.pane').forEach(function (x) {
          x.classList.remove('active');
        });
        b.classList.add('active');
        $('pane-' + b.dataset.tab).classList.add('active');
      });
    });
    $('e1-run').addEventListener('click', runE1);
  }

  function loadTablebase(kind) {
    S.tbKind = kind;
    $('loading-mask').classList.remove('hidden');
    global.ChessOracle.tb.loadTablebase(kind).then(function (tb) {
      S.tb = tb;
      S.explorer = null;
      // keep every space ready: the KPK promotion boundary probes the
      // frozen KQK certificate, and the editor may switch endgames
      return global.ChessOracle.tb.preloadAll();
    }).then(function () {
      S.tb = global.ChessOracle.tb.getLoaded(S.tbKind) || S.tb;
      $('loading-mask').classList.add('hidden');
      $('table-select').value = S.tbKind;
      setKindNote();
      renderTablePane();
      renderAudit(null);
      renderTreePane();
      renderE1Pane();
      sampleNewGame();
    }).catch(function (err) {
      $('loading-mask').classList.add('hidden');
      var banner = $('audit-banner');
      banner.className = 'banner fail';
      banner.textContent = 'LOAD ERROR: ' + err.message;
      console.error(err);
    });
  }

  function init() {
    buildBoard();
    bindControls();
    applyI18n();
    loadTablebase('krk');
  }

  document.addEventListener('DOMContentLoaded', init);
})(window);

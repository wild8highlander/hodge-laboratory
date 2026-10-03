/* Node harness for the chess-oracle JS core (no browser needed).
   Verifies: tablebase load + integrity gate, known-value probes,
   a full optimal game audited at every ply, E1 replay sanity,
   and the exact strategy-tree counter.

   Run:  node web/chess-oracle/tests/node_harness.js            */

'use strict';
const fs = require('fs');
const path = require('path');

global.window = global;
const ROOT = path.join(__dirname, '..');

const FILES = ['assets/js/chess.js', 'assets/js/tb.js',
               'assets/js/particles.js', 'assets/js/audit.js',
               'assets/js/tree.js', 'assets/js/e1.js',
               'assets/js/traps.js',
               'assets/js/vortex.js', 'assets/js/vortex_view.js',
               'assets/js/i18n.js'];
for (const f of FILES) {
  eval(fs.readFileSync(path.join(ROOT, f), 'utf8'));
}
eval(fs.readFileSync(path.join(ROOT, 'assets/data/tables.js'), 'utf8'));

const CO = global.ChessOracle;
const C = CO.chess, TB = CO.tb, AUD = CO.audit;

let failures = 0;
function check(name, cond, extra) {
  console.log((cond ? '  [PASS] ' : '  [FAIL] ') + name +
              (extra !== undefined ? '  -> ' + extra : ''));
  if (!cond) failures++;
}

(async () => {
  console.log('harness: chess-oracle core (node ' + process.version + ')');

  /* ── 1. tablebase load + integrity ──────────────────────────── */
  const tb = await CO.tb.loadTablebase('krk');
  check('krk load: all integrity checks pass', tb.allOk,
        tb.checks.filter(c => !c.ok).map(c => c.name).join(',') || 'ok');
  const tbq = await CO.tb.loadTablebase('kqk');
  check('kqk load: all integrity checks pass', tbq.allOk);
  // preload every space (the KPK promotion boundary probes the KQK table)
  await CO.tb.preloadAll();
  const tbn = CO.tb.getLoaded('knk');
  const tbp = CO.tb.getLoaded('kpk');
  check('knk load: all integrity checks pass (won=mates=0)', tbn.allOk,
        tbn ? tbn.checks.filter(c => !c.ok).map(c => c.name).join(',') : 'missing');
  check('kpk load: all integrity checks pass', tbp.allOk,
        tbp ? tbp.checks.filter(c => !c.ok).map(c => c.name).join(',') : 'missing');

  /* ── 2. known-value probes ──────────────────────────────────── */
  // Mate in one: k7/8/1K6/8/8/8/8/7R w — Rh8#
  let pos = C.Position.fromFEN('k7/8/1K6/8/8/8/8/7R w - - 0 1');
  let st = TB.stateOfPosition(pos);
  let info = tb.probe(st);
  check('KRK mate-in-1 position is won', info.won && !info.mate,
        'v=' + info.raw);
  const opts = TB.optimalMoves(tb, pos, st);
  const mateMove = opts.find(m => C.sqName(m.f) + C.sqName(m.t) === 'h1h8');
  check('Rh8 among optimal moves', !!mateMove, opts.length + ' optimal');
  if (mateMove) {
    const undo = pos.make(mateMove);
    const stAfter = TB.stateOfPosition(pos);
    const after = tb.probe(stAfter);
    pos.unmake(undo);
    check('after Rh8 the table says mate', after.mate, 'v=' + after.raw);
  }
  const aud = AUD.auditState(tb, pos, st);
  check('live audit of the mate-in-1 position: PASS', aud.verdict,
        aud.reason);

  // A frozen E1 lost example must stay consistent with the table:
  // 2k5/8/8/8/1R6/8/2K5/8 w - - 0 1  (dtm 10 moves = 19 plies)
  pos = C.Position.fromFEN('2k5/8/8/8/1R6/8/2K5/8 w - - 0 1');
  st = TB.stateOfPosition(pos);
  info = tb.probe(st);
  check('frozen E1 example probes to DTM 19 plies', info.plies === 19,
        'v=' + info.raw);

  /* ── 3. full optimal game with live audit at every ply ──────── */
  const rng = CO.e1.mulberry32(7);
  const start = CO.e1.sampleWonState(tb, rng);
  let cur = start.pos;
  let plies = 0, allPass = true, mateReached = false;
  while (plies < 80) {
    const s = TB.stateOfPosition(cur);
    const a = AUD.auditState(tb, cur, s);
    if (!a.verdict) {
      allPass = false;
      console.log('    audit fail:', a.reason, cur.toFEN());
      break;
    }
    const moves = TB.optimalMoves(tb, cur, s);
    if (!moves.length) {
      const all = cur.legalMoves();
      if (!all.length && cur.inCheck(-1)) mateReached = true;
      else if (!all.length) console.log('    stalemate reached');
      break;
    }
    cur.make(moves[0]);
    plies++;
    const s2 = TB.stateOfPosition(cur);
    if (s2 === null) break;
    const v2 = tb.probe(s2);
    if (v2.mate) { mateReached = true; break; }
    if (v2.drawn) { console.log('    draw reached (unexpected)'); break; }
  }
  check('optimal game: audit PASS at every visited ply', allPass,
        plies + ' plies');
  check('optimal game reaches mate', mateReached);

  /* ── 4. E1 replay sanity (200 samples, seed 42) ─────────────── */
  const solver = new CO.particles.ParticleSolver();
  const e1 = CO.e1.runE1(tb, 200, 42, solver);
  check('E1 replay: save-rate in the plausible band',
        e1.save_rate > 0.6 && e1.save_rate < 0.95,
        (100 * e1.save_rate).toFixed(2) + '% (frozen 82.44%)');
  check('E1 replay: optimal-rate plausible',
        e1.optimal_rate > 0.05 && e1.optimal_rate < 0.9,
        (100 * e1.optimal_rate).toFixed(2) + '% (frozen 30.30%)');
  check('E1 replay: mean delta positive',
        e1.mean_delta_plies > 0, e1.mean_delta_plies.toFixed(3));

  /* ── 5. strategy-tree counter (E3 in-browser) ───────────────── */
  const explorer = new CO.tree.TreeExplorer(tb);
  const T = explorer.treeSize(start.state);
  check('tree size is a positive integer > 1',
        Number.isInteger(T) && T > 1,
        'T=' + T + ', memo=' + explorer.memo.size);
  // sample a DEEP position for a meaningful multi-level profile
  let deep = null;
  for (let guard = 0; guard < 10000; guard++) {
    const cand = CO.e1.sampleWonState(tb, CO.e1.mulberry32(1000 + guard));
    if (cand && cand.info.plies >= 9) { deep = cand; break; }
  }
  check('deep sampled position found', !!deep,
        deep ? 'dtm=' + deep.info.plies : 'none');
  const prof = explorer.levelProfile(deep ? deep.state : start.state);
  check('level profile has >= 3 levels for a deep position',
        prof.profile.length >= 3,
        prof.profile.map(x => x.plies + ':' + x.nodes).join(' '));
  const monotone = prof.profile.every((x, i) =>
    i === 0 || x.nodes >= prof.profile[i - 1].nodes);
  check('profile grows level over level', monotone);
  check('KQK tree counter works', (() => {
    const ex = new CO.tree.TreeExplorer(tbq);
    const s = CO.e1.sampleWonState(tbq, CO.e1.mulberry32(3));
    return ex.treeSize(s.state) > 1;
  })());

  /* ── 6. KNK: the negative control (T15) ─────────────────────── */
  const knkPos = C.Position.fromFEN('8/8/8/1k6/8/3K4/8/2N5 w - - 0 1');
  const knkSt = TB.stateOfPosition(knkPos);
  check('KNK: legal demonstration position probes as drawn',
        knkSt !== null && tbn.probe(knkSt).drawn,
        knkSt === null ? 'state null' : 'v=' + tbn.probe(knkSt).raw);
  check('KNK: every legal move is "optimal" (all equivalents)',
        TB.optimalMoves(tbn, knkPos, knkSt).length === knkPos.legalMoves().length);
  const knkAudW = AUD.auditState(tbn, knkPos, knkSt);
  check('KNK: live audit PASS (WTM drawn)', knkAudW.verdict, knkAudW.reason);
  const knkAudB = AUD.auditState(tbn, knkPos.clone(), (() => {
    const p = C.Position.fromFEN('8/8/8/1k6/8/3K4/8/2N5 b - - 0 1');
    return TB.stateOfPosition(p);
  })());
  check('KNK: live audit PASS (BTM drawn, black to move)',
        knkAudB.verdict, knkAudB.reason);
  // E1 must degrade gracefully: no won states -> evaluated = 0
  const knkE1 = CO.e1.runE1(tbn, 50, 42, solver);
  check('KNK: E1 returns evaluated=0 (E1 undefined, honestly)',
        knkE1.count === 0, 'count=' + knkE1.count);

  /* ── 7. KPK: promotion boundary ─────────────────────────────── */
  const ns = s => (s.charCodeAt(0) - 97) + 16 * (s.charCodeAt(1) - 49);
  const kpkProbe = (wk, wp, bk, stm) =>
    tbp.probe(TB.packState(ns(wk), ns(wp), ns(bk), stm));
  check('KPK spot: Kb6/Pc7/Ka8 wtm is mate in 1 (c8=Q#)',
        kpkProbe('b6', 'c7', 'a8', 0).raw === 1,
        'v=' + kpkProbe('b6', 'c7', 'a8', 0).raw);
  check('KPK spot: Kb6/Pc7/Ka7 wtm is drawn (stalemate trick)',
        kpkProbe('b6', 'c7', 'a7', 0).drawn);
  check('KPK spot: Kb6/Pc7/Ka8 btm is stalemate',
        kpkProbe('b6', 'c7', 'a8', 1).drawn);
  check('KPK spot: undefended checking pawn falls (Ka1/Pe2/Kd3 btm)',
        kpkProbe('a1', 'e2', 'd3', 1).drawn);
  check('KPK spot: frontal opposition draw (Kd6/Pe6/Kd8 wtm)',
        kpkProbe('d6', 'e6', 'd8', 0).drawn);
  check('KPK spot: opposition lost (Kd6/Pe6/Kd8 btm) is a win',
        kpkProbe('d6', 'e6', 'd8', 1).plies === 18,
        'v=' + kpkProbe('d6', 'e6', 'd8', 1).raw);

  // the D=1 promotion tree is exactly 2 nodes (w + b)
  const kpkExplorer = new CO.tree.TreeExplorer(tbp);
  const promoRoot = TB.packState(ns('b6'), ns('c7'), ns('a8'), 0);
  check('KPK tree: T(mate-in-1 via promotion) = 2 exactly',
        kpkExplorer.treeSize(promoRoot) === 2,
        'T=' + kpkExplorer.treeSize(promoRoot));

  // audit of the pre-promotion position (children probed across the
  // boundary through the KQK certificate)
  const promoPos = C.Position.fromFEN('k7/2P5/1K6/8/8/8/8/8 w - - 0 1');
  const promoSt = TB.stateOfPosition(promoPos);
  const promoAud = AUD.auditState(tbp, promoPos, promoSt);
  check('KPK audit: pre-promotion position PASS (cross-boundary children)',
        promoAud.verdict, promoAud.reason);
  const promoOpts = TB.optimalMoves(tbp, promoPos, promoSt);
  check('KPK optimal: the promotion move c7c8 is among optimal moves',
        promoOpts.some(m => C.sqName(m.f) + C.sqName(m.t) === 'c7c8' && m.promo),
        promoOpts.length + ' optimal');

  // full optimal KPK game: must end in mate AFTER a promotion, audited
  // at every ply with the ACTIVE space table
  let deepKpk = null;
  for (let guard = 0; guard < 20000; guard++) {
    const cand = CO.e1.sampleWonState(tbp, CO.e1.mulberry32(500 + guard));
    if (cand && cand.info.plies >= 20) { deepKpk = cand; break; }
  }
  check('KPK: deep sampled won position found (dtm >= 20 plies)', !!deepKpk,
        deepKpk ? 'dtm=' + deepKpk.info.plies : 'none');
  if (deepKpk) {
    let cur = deepKpk.pos, kind = 'kpk', active = tbp;
    let plies2 = 0, promoHappened = false, allPass2 = true, mate2 = false;
    while (plies2 < 90) {
      const s = TB.stateOfPosition(cur);
      if (s === null) { allPass2 = false; break; }
      const a = AUD.auditState(active, cur, s);
      if (!a.verdict) {
        allPass2 = false;
        console.log('    kpk audit fail:', a.reason, cur.toFEN());
        break;
      }
      const moves = TB.optimalMoves(active, cur, s);
      if (!moves.length) {
        if (!cur.legalMoves().length && cur.inCheck(-1)) mate2 = true;
        break;
      }
      const undo = cur.make(moves[0]);
      if (undo.promo && kind === 'kpk') {
        kind = 'kqk'; active = CO.tb.getLoaded('kqk'); promoHappened = true;
      }
      plies2++;
      const s2 = TB.stateOfPosition(cur);
      if (s2 === null) break;
      const v2 = active.probe(s2);
      if (v2.mate) { mate2 = true; break; }
      if (v2.drawn) { allPass2 = false; console.log('    kpk: draw reached'); break; }
    }
    check('KPK optimal game: audit PASS at every ply', allPass2,
          plies2 + ' plies');
    check('KPK optimal game: promotion happened on the way',
          promoHappened);
    check('KPK optimal game: reaches mate (after promotion)', mate2);
  }

  /* ── 8. E1 on KPK (live measurement, no frozen twin) ────────── */
  const e1kpk = CO.e1.runE1(tbp, 200, 42, solver);
  check('KPK E1: evaluated 200 positions', e1kpk.count === 200,
        'count=' + e1kpk.count);
  check('KPK E1: save-rate in the plausible band (0.2..1.0]',
        e1kpk.save_rate > 0.2 && e1kpk.save_rate <= 1.0,
        (100 * e1kpk.save_rate).toFixed(2) + '% preserved');
  check('KPK E1: mean delta non-negative', e1kpk.mean_delta_plies >= 0,
        e1kpk.mean_delta_plies.toFixed(3));
  console.log('    KPK E1 detail: save ' + (100 * e1kpk.save_rate).toFixed(2)
              + '%, optimal ' + (100 * e1kpk.optimal_rate).toFixed(2)
              + '%, mean dDTM ' + e1kpk.mean_delta_plies.toFixed(4));

  /* ── 9. vortex layer (T16): field, flow, classification ─────── */
  const VX = CO.vortex;
  console.log('  vortex (T16): field + flow classifier');

  // 9a. WTM mate-in-1: WIN with a descent into the mating square
  pos = C.Position.fromFEN('k7/8/1K6/8/8/8/8/7R w - - 0 1');
  let vfield = VX.buildField(tb, pos);
  check('vortex: WTM mate-in-1 is WIN with descents',
        vfield && vfield.verdict === 'WIN' && vfield.descents >= 1,
        vfield ? 'descents=' + vfield.descents +
                 ' escapes=' + vfield.escapes : 'null');
  const h8cur = vfield.currents.find(
    cu => cu.tag === 'descent' && C.sqName(cu.to) === 'h8');
  check('vortex: Rh8 is a descent current (J = d - 0)', !!h8cur,
        h8cur ? 'J=' + h8cur.J : 'missing');
  let vm = VX.simulate(vfield);
  let vcls = VX.classify(vfield, vm);
  check('vortex: flow class WIN + full capture',
        vcls.cls === 'WIN' && vcls.gateOk &&
        vm.capture_fraction >= VX.FROZEN.win_capture_min,
        'cf=' + vm.capture_fraction.toFixed(3));

  // 9b. the mirrored BTM position: LOSS, every defence descends
  pos = C.Position.fromFEN('k7/8/1K6/8/8/8/8/7R b - - 0 1');
  vfield = VX.buildField(tb, pos);
  check('vortex: BTM same pieces is LOSS (all currents descend)',
        vfield && vfield.verdict === 'LOSS' &&
        vfield.descents === vfield.currents.length &&
        vfield.currents.length > 0,
        vfield ? 'currents=' + vfield.currents.length : 'null');
  vm = VX.simulate(vfield);
  vcls = VX.classify(vfield, vm);
  check('vortex: LOSS flow captures everything', vcls.cls === 'LOSS' &&
        vcls.gateOk, 'cf=' + vm.capture_fraction.toFixed(3));

  // 9c. the terminal mate: no moves, no currents, LOSS by definition
  pos = C.Position.fromFEN('k7/8/1K6/8/8/8/8/7R w - - 0 1');
  const wMove = TB.optimalMoves(tb, pos,
                                TB.stateOfPosition(pos)).find(
    m => C.sqName(m.f) + C.sqName(m.t) === 'h1h8');
  const undoM = pos.make(wMove);               // Rh8# — mate on the board
  vfield = VX.buildField(tb, pos);
  check('vortex: mate on board is the terminal sink',
        vfield && vfield.terminal === true &&
        vfield.verdict === 'LOSS' && vfield.currents.length === 0,
        vfield ? 'terminal=' + vfield.terminal : 'null');
  vm = VX.simulate(vfield);
  vcls = VX.classify(vfield, vm);
  check('vortex: terminal sink classifies as LOSS',
        vcls.cls === 'LOSS' && vcls.gateOk);
  pos.unmake(undoM);

  // 9d. KNK: pure rotation — no descent anywhere, DRAW with zero capture
  pos = C.Position.fromFEN('8/8/8/1k6/8/3K4/8/2N5 w - - 0 1');
  vfield = VX.buildField(tbn, pos);
  check('vortex: KNK has no forced currents (T15 as topology)',
        vfield && vfield.verdict === 'DRAW' && vfield.descents === 0,
        vfield ? 'descents=' + vfield.descents : 'null');
  vm = VX.simulate(vfield);
  vcls = VX.classify(vfield, vm);
  check('vortex: KNK flow is a draw with capture_fraction = 0',
        vcls.cls === 'DRAW' && vm.capture_fraction === 0,
        'cf=' + vm.capture_fraction.toFixed(3));

  // 9e. KPK promotion boundary: the promotion move descends through KQK
  pos = C.Position.fromFEN('8/P7/8/8/8/8/8/K1k4 w - - 0 1');
  vfield = VX.buildField(tbp, pos);
  const promoCur = vfield ? vfield.currents.find(
    cu => cu.tag === 'descent' && C.sqName(cu.to) === 'a8') : null;
  check('vortex: KPK promotion a8 is a descent current (KQK-valued)',
        vfield && vfield.verdict === 'WIN' && !!promoCur,
        promoCur ? 'J=' + promoCur.J : 'missing');

  // 9f. seeded stratified agreement (the E4 protocol, reduced)
  function sqOk(s) { return !(s & 0x88); }
  function sampleByClass(kind, tbk, want, rng) {
    for (let guard = 0; guard < 50000; guard++) {
      const wk = (rng() * 64) | 0, wp = (rng() * 64) | 0,
            bk = (rng() * 64) | 0;
      if (wk === wp || wk === bk || wp === bk) continue;
      if (!sqOk(wk) || !sqOk(wp) || !sqOk(bk)) continue;
      const df = Math.abs((wk & 7) - (bk & 7)),
            dr = Math.abs((wk >> 4) - (bk >> 4));
      if (df <= 1 && dr <= 1) continue;
      const side = want.startsWith('wtm') ? 1 : -1;
      const p = new C.Position().setFromSetup(
        wk, wp, bk, tbk.spec.pieceCode, side);
      if (side === 1 && p.attacked(bk, 1)) continue;
      const s2 = TB.packState(wk, wp, bk, side === 1 ? 0 : 1);
      const inf = tbk.probe(s2);
      if (want.endsWith('won') && !(inf.won && !inf.mate)) continue;
      if (want.endsWith('drawn') && !inf.drawn) continue;
      return p;
    }
    return null;
  }
  let agree = 0, tested = 0;
  const kinds2 = [['krk', tb], ['kqk', tbq], ['knk', tbn], ['kpk', tbp]];
  for (const [kindName, tbk] of kinds2) {
    for (const want of ['wtm_won', 'wtm_drawn', 'btm_won', 'btm_drawn']) {
      const rng = CO.e1.mulberry32(0xE4 + kindName.length * 131 + want.length);
      for (let i = 0; i < 10; i++) {
        const p = sampleByClass(kindName, tbk, want, rng);
        if (!p) continue;
        const fld = VX.buildField(tbk, p);
        if (!fld) continue;
        const met = VX.simulate(fld);
        const cl = VX.classify(fld, met);
        tested++;
        if (cl.cls === fld.verdict && cl.gateOk) agree++;
        else console.log('    vortex mismatch:', kindName, want,
                         p.toFEN(), 'table=' + fld.verdict,
                         'flow=' + cl.cls, 'gate=' + cl.gateOk);
      }
    }
  }
  check('vortex: seeded stratified agreement = 100% (E4 protocol)',
        tested > 0 && agree === tested, agree + '/' + tested);

  /* ── 10. trap classification (T17): sample vs population ────── */
  const TRP = CO.traps;
  console.log('  traps (T17): move classes from the certificate');

  // 10a. WTM mate-in-1: WIN, h1h8 optimal, no traps possible
  pos = C.Position.fromFEN('k7/8/1K6/8/8/8/8/7R w - - 0 1');
  let tres = TRP.classify(tb, pos);
  check('traps: WTM mate-in-1 is WIN with optimal h1h8',
        tres.moverClass === 'WIN' && tres.d === 1 &&
        tres.counts.optimal >= 1 && tres.counts.trap === 0 &&
        tres.entries.some(en => en.cls === 'optimal' &&
                               en.uci === 'h1h8'),
        'opt=' + tres.counts.optimal + ' waste=' + tres.counts.waste +
        ' slack=' + tres.counts.slack);

  // 10b. BTM two plies before mate: LOSS, every move resists or accelerates
  pos = C.Position.fromFEN('k7/8/1K6/8/8/8/8/7R b - - 0 1');
  tres = TRP.classify(tb, pos);
  check('traps: BTM near-mate is LOSS with full partition',
        tres.moverClass === 'LOSS' && tres.d === 2 &&
        tres.counts.resist + tres.counts.fast === tres.counts.moves &&
        tres.counts.resist >= 1,
        'resist=' + tres.counts.resist + ' fast=' + tres.counts.fast +
        ' moves=' + tres.counts.moves);

  // 10c. drawn BTM defender: traps are exactly won children (draw -> loss)
  function sampleBtmDrawn(kind, tbk, rng) {
    for (let guard = 0; guard < 50000; guard++) {
      const wk = (rng() * 64) | 0, wp = (rng() * 64) | 0,
            bk = (rng() * 64) | 0;
      if (wk === wp || wk === bk || wp === bk) continue;
      if ((wk & 0x88) || (wp & 0x88) || (bk & 0x88)) continue;
      if (Math.abs((wk & 7) - (bk & 7)) <= 1 &&
          Math.abs((wk >> 4) - (bk >> 4)) <= 1) continue;
      if (kind === 'kpk' && (wp >> 4) === 0) continue;
      const side = -1;
      const p = new C.Position().setFromSetup(wk, wp, bk,
                                              tbk.spec.pieceCode, side);
      const s2 = TB.packState(wk, wp, bk, 1);
      if (!tbk.probe(s2).drawn) continue;
      return p;
    }
    return null;
  }
  let trapStates = 0, trapMoves = 0, sampled = 0, consistent = true;
  for (let i = 0; i < 60; i++) {
    const p = sampleBtmDrawn('krk', tb, CO.e1.mulberry32(0x17 + i));
    if (!p) continue;
    const r = TRP.classify(tb, p);
    sampled++;
    if (r.moverClass !== 'DRAW' || r.white) { consistent = false; break; }
    for (const en of r.entries) {
      if (en.cls === 'trap') {
        trapStates += en.to === en.to ? 0 : 0;   // count per move below
        trapMoves++;
        if (!(en.child && en.child.won)) { consistent = false; break; }
      } else if (en.cls !== 'keep') { consistent = false; break; }
    }
    const hl = TRP.highlightMap(r);
    const hlCount = Object.keys(hl).length;
    if (r.counts.trap === 0 && hlCount !== 0) { consistent = false; break; }
  }
  check('traps: 60 sampled drawn BTM states classify consistently',
        sampled > 0 && consistent,
        sampled + ' states, ' + trapMoves + ' trap moves');
  check('traps: the sampled defender walks into real snares',
        trapMoves > 0, trapMoves + ' traps across ' + sampled + ' states');

  // 10d. WTM won attacker: waste ddtm >= 1, slack children are drawn
  let wasteSeen = 0, slackSeen = 0, wasteOk = true;
  for (let i = 0; i < 60; i++) {
    const s3 = CO.e1.sampleWonState(tb, CO.e1.mulberry32(0x1717 + i));
    if (!s3) continue;
    const r = TRP.classify(tb, s3.pos);
    if (r.moverClass !== 'WIN') { wasteOk = false; break; }
    if (r.counts.optimal === 0) { wasteOk = false; break; }
    for (const en of r.entries) {
      if (en.cls === 'waste') {
        wasteSeen++;
        if (en.ddtm < 1 || !en.child.won) wasteOk = false;
      } else if (en.cls === 'slack') {
        slackSeen++;
        if (en.child !== null && !en.child.drawn) wasteOk = false;
      }
    }
  }
  check('traps: WTM won states partition into optimal/waste/slack',
        wasteOk && wasteSeen > 0,
        wasteSeen + ' waste, ' + slackSeen + ' slack');

  // 10e. KNK zero control: no traps, no slack, everything keeps the draw
  pos = C.Position.fromFEN('8/8/8/1k6/8/3K4/8/2N5 b - - 0 1');
  tres = TRP.classify(tbn, pos);
  check('traps: KNK keeps the draw with every move (T15 in classes)',
        tres.moverClass === 'DRAW' && tres.counts.trap === 0 &&
        tres.counts.keep === tres.counts.moves &&
        tres.counts.moves === pos.legalMoves().length,
        'moves=' + tres.counts.moves);

  // 10f. frozen census numbers are pinned (population certificate)
  check('traps: frozen census pinned (krk traps 59624, knk 0, kpk deepest 55)',
        TRP.FROZEN.krk.btmDrawn.traps === 59624 &&
        TRP.FROZEN.krk.btmDrawn.withTraps === 21764 &&
        TRP.FROZEN.kqk.btmDrawn.traps === 32896 &&
        TRP.FROZEN.knk.btmDrawn.traps === 0 &&
        TRP.FROZEN.kpk.btmDrawn.deepestPlies === 55 &&
        TRP.FROZEN.kpk.btmDrawn.maxTraps === 7 &&
        TRP.FROZEN.krk.wtmWon.ddtmMean > 5.8 &&
        TRP.FROZEN.krk.wtmWon.ddtmMean < 5.9,
        'krk=' + TRP.FROZEN.krk.btmDrawn.traps);

  console.log(failures === 0
    ? 'harness verdict: ALL CHECKS PASSED'
    : 'harness verdict: ' + failures + ' FAILURE(S)');
  process.exit(failures === 0 ? 0 : 1);
})().catch(e => { console.error('HARNESS ERROR', e); process.exit(2); });

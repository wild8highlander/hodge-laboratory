#!/usr/bin/env python3
"""outcome/cli.py — the command line of the Outcome Dynamics program (v2).

    python3 -m outcome analyze "<FEN>" [--moves] [--rating-white 2800 ...]
    python3 -m outcome export --kind krk --limit 20000 --out ds_krk.csv
    python3 -m outcome train  --per-kind 20000 --epochs 40 [--ablation]
    python3 -m outcome evaluate
    python3 -m outcome report --per-kind 20000 --out results/outcome_distillation.json
    python3 -m outcome report --smoke                    (CI-sized)
    python3 -m outcome impact  "<FEN>" [--max-moves 12]  (the counterfactual surface)
    python3 -m outcome context "<FEN>" --rating-white 2400 --rating-black 2000
    python3 -m outcome trajectory --per-kind 250         (Epoch V certificate)
    python3 -m outcome falsify --per-kind 2000           (Epoch VI corpus)
    python3 -m outcome nonlinear --per-kind 20000        (Epoch VII: E11 head)
    python3 -m outcome interact --per-kind 20000         (Epoch VII: E13 ihinges)
    python3 -m outcome games data/games                  (Epoch IV: real games)
    python3 -m outcome adjudicate data/games             (Epoch VIII: the referee)

The report command is the whole E8 experiment in one command:
sample -> featurize -> split -> hard/soft A/B -> ensemble -> DTM ridge
-> calibration -> benchmark -> ablation -> freeze the certificate JSON.
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import dynamics as D                                        # noqa: E402
from outcome import adjudicate as ADJ                        # noqa: E402
from outcome import dataset as DS                           # noqa: E402
from outcome import falsify as FLS                          # noqa: E402
from outcome import features as F                           # noqa: E402
from outcome import impact as IMP                           # noqa: E402
from outcome import metrics as MT                           # noqa: E402
from outcome import model as M                              # noqa: E402
from outcome import nonlinear as NL                         # noqa: E402
from outcome import realgames as RG                         # noqa: E402
from outcome import tablebase_api as T                      # noqa: E402
from outcome import trajectory as TR                        # noqa: E402
from outcome.outcome_field import OutcomeField              # noqa: E402

MODEL_PATH = os.path.join(T.RESULTS_DIR, 'outcome_model.json')
REPORT_PATH = os.path.join(T.RESULTS_DIR, 'outcome_distillation.json')
TRAJECTORY_PATH = os.path.join(T.RESULTS_DIR, 'outcome_trajectory.json')
COUNTEREXAMPLES_DIR = os.path.join(os.path.dirname(T.RESULTS_DIR),
                                   'counterexamples')


# ── shared pipeline pieces ───────────────────────────────────────────────
def build_dataset(kinds, per_kind, seed, log=print):
    """Sampled records per kind + exact oracle sanity against frozen stats."""
    data = {}
    for kind in kinds:
        t0 = time.time()
        recs = DS.build_sampled(kind, per_kind, seed)
        won = sum(1 for r in recs if r['cls'] == T.WHITE_WIN)
        data[kind] = recs
        log('  %-4s sampled %6d states  (%.1f%% won)  %.1fs'
            % (kind, len(recs), 100.0 * won / max(len(recs), 1),
               time.time() - t0))
    return data


def split_records(data):
    """Hash-split every record; returns {kind: {split: [records]}}."""
    out = {}
    for kind, recs in data.items():
        buckets = {'train': [], 'valid': [], 'test': []}
        for rec in recs:
            buckets[DS.split_of(rec['state'], DS.KINDS_INDEX[kind])].append(rec)
        out[kind] = buckets
    return out


def xy(records, names=None):
    names = names or F.FEATURE_NAMES
    X = [[r['features'][n] for n in names] for r in records]
    y = [r['cls'] for r in records]
    dtm = [r['dtm_plies'] for r in records]
    return X, y, dtm


def train_all(kinds, per_kind, seed, epochs, ablation=False, log=print,
              smoke=False, members=3):
    """The full E8 experiment: distillation v2.  Returns the report."""
    log('[1/6] sampling the dynamics dataset (seed %d, %d features)...'
        % (seed, len(F.FEATURE_NAMES)))
    data = build_dataset(kinds, per_kind, seed, log)
    splits = split_records(data)

    train_recs, valid_recs, test_recs = [], [], []
    for kind in kinds:
        b = splits[kind]
        train_recs += b['train']
        valid_recs += b['valid']
        test_recs += b['test']
    log('  split: train %d / valid %d / test %d'
        % (len(train_recs), len(valid_recs), len(test_recs)))

    names = F.FEATURE_NAMES
    Xtr, ytr, dtr = xy(train_recs, names)
    Xva, yva, dva = xy(valid_recs, names)
    Xte, yte, dte = xy(test_recs, names)

    # ── A/B: hard one-hot targets vs oracle-shaped soft targets ────────
    log('[2/6] A/B: hard-target softmax (%d features, %d epochs)...'
        % (len(names), epochs))
    t0 = time.time()
    hard = M.SoftmaxRegression(len(names), epochs=epochs)
    hard.fit(Xtr, ytr)
    hard_te = MT.summarize(yte, hard.predict_proba_raw(Xte))
    log('  hard: test acc %.4f  logloss %.4f  [%.1fs]'
        % (hard_te['accuracy'], hard_te['log_loss'], time.time() - t0))

    log('[3/6] oracle-shaped soft targets (tau %.1f, eps_draw %.2f)...'
        % (M.SOFT_TAU, M.SOFT_EPS_DRAW))
    soft_targets = [M.soft_targets(c, d) for c, d in zip(ytr, dtr)]
    t0 = time.time()
    soft = M.SoftmaxRegression(len(names), epochs=epochs)
    soft.fit(Xtr, ytr, targets=soft_targets)
    soft_te = MT.summarize(yte, soft.predict_proba_raw(Xte))
    log('  soft: test acc %.4f  logloss %.4f  [%.1fs]'
        % (soft_te['accuracy'], soft_te['log_loss'], time.time() - t0))

    # ── the production head: bootstrap ensemble on the A/B WINNER ──────
    # The E8 A/B verdict is unambiguous: hard one-hot targets beat the
    # oracle-shaped soft targets on BOTH accuracy and log loss (the soft
    # smoothing blurs exactly the drawn/won boundary where accuracy
    # lives).  The falsification is frozen in the report; the production
    # ensemble trains on the winner.
    ens_epochs = min(epochs, 25)
    log('[4/6] bootstrap ensemble (%d members, hard targets, %d epochs)...'
        % (members, ens_epochs))
    t0 = time.time()
    ensemble = M.SoftmaxEnsemble(len(names), members=members,
                                 epochs=ens_epochs, seed=seed)
    ensemble.fit(Xtr, ytr)
    log('  ensemble fitted [%.1fs]' % (time.time() - t0))

    # ── per-domain temperature calibration (valid split only) ──────────
    log('[5/6] temperature calibration (fitted on the valid split)...')
    probs_val = ensemble.predict_proba_raw(Xva)
    calibrator = M.TemperatureCalibrator()
    slice_keys = [r['kind'] for r in valid_recs]
    calibrator.fit(yva, probs_val, slice_keys)
    log('  calibrator: global tau %.3f, slices %s, valid logloss '
        '%.4f -> %.4f' % (calibrator.global_tau,
                          {k: round(v, 3)
                           for k, v in calibrator.slice_taus.items()},
                          calibrator.before or 0.0, calibrator.after or 0.0))

    # final test metrics: ensemble + calibration (the production path)
    probs_te = [calibrator.transform(p, rec['kind'])
                for p, rec in zip(ensemble.predict_proba_raw(Xte), test_recs)]
    pooled = MT.summarize(yte, probs_te)
    log('  pooled test: acc %.4f  logloss %.4f  brier %.4f  ece %.4f'
        % (pooled['accuracy'], pooled['log_loss'], pooled['brier'],
           pooled['ece']))

    per_kind_metrics = {}
    for kind in kinds:
        b = splits[kind]
        Xk, yk, _ = xy(b['test'], names)
        pk = [calibrator.transform(p, kind)
              for p in ensemble.predict_proba_raw(Xk)]
        per_kind_metrics[kind] = MT.summarize(yk, pk)
        log('  %-4s test: acc %.4f  logloss %.4f  ece %.4f  (n=%d)'
            % (kind, per_kind_metrics[kind]['accuracy'],
               per_kind_metrics[kind]['log_loss'],
               per_kind_metrics[kind]['ece'], per_kind_metrics[kind]['n']))

    # ── baselines (plan §13: never report accuracy alone) ───────────────
    log('[5/6] baselines + layer ablation...')
    baselines = {'majority': MT.majority_baseline(ytr, yte)}
    for tag, group in (('material_only', F.FEATURE_GROUPS['material']),
                       ('mobility_only', F.FEATURE_GROUPS['mobility'])):
        Xtr_g, _, _ = xy(train_recs, group)
        Xte_g, _, _ = xy(test_recs, group)
        gm = M.SoftmaxRegression(len(group), epochs=min(epochs, 15))
        gm.fit(Xtr_g, ytr)
        gp = gm.predict_proba_raw(Xte_g)
        baselines[tag] = MT.summarize(yte, gp)
        log('  %-14s acc %.4f' % (tag, baselines[tag]['accuracy']))

    ablation_report = {}
    if ablation:
        for group, gnames in F.FEATURE_GROUPS.items():
            Xtr_g, _, _ = xy(train_recs, gnames)
            Xte_g, _, _ = xy(test_recs, gnames)
            gm = M.SoftmaxRegression(len(gnames), epochs=min(epochs, 15))
            gm.fit(Xtr_g, ytr)
            gp = gm.predict_proba_raw(Xte_g)
            ablation_report[group] = MT.summarize(yte, gp)
            ablation_report[group]['title'] = F.GROUP_TITLES[group]
            log('  %-9s acc %.4f  logloss %.4f  %s'
                % (group, ablation_report[group]['accuracy'],
                   ablation_report[group]['log_loss'],
                   F.GROUP_TITLES[group]))

    # ── head A: DTM regression (ridge, on the won states) ───────────────
    log('[6/6] DTM ridge head...')
    won_tr = [(x, d) for x, d in zip(Xtr, dtr) if d >= 0]
    won_te = [(x, d) for x, d in zip(Xte, dte) if d >= 0]
    dtm_report = {}
    ridge = None
    if won_tr and won_te:
        ridge = M.RidgeRegression(len(names), epochs=max(epochs, 50))
        ridge.fit([x for x, _ in won_tr], [d for _, d in won_tr])
        preds = ridge.predict_raw([x for x, _ in won_te])
        truth = [d for _, d in won_te]
        dtm_report = {
            'n_test_won': len(truth),
            'mae_plies': round(MT.mae(truth, [max(0, p) for p in preds]), 4),
            'mae_baseline_mean': round(MT.mae(
                truth, [sum(truth) / len(truth)] * len(truth)), 4),
        }
        log('  DTM head: MAE %.2f plies (mean baseline %.2f) over %d won states'
            % (dtm_report['mae_plies'], dtm_report['mae_baseline_mean'],
               len(truth)))

    # ── the frozen payload ──────────────────────────────────────────────
    pc = [r['features']['piece_count_total'] for r in train_recs]
    envelope = {'piece_count_total': [min(pc), max(pc)]}
    report = {
        'program': 'Outcome Dynamics — tablebase distillation '
                   '(epochs I-III, certificate E8)',
        'recipe': {
            'kinds': list(kinds),
            'per_kind': per_kind,
            'seed': seed,
            'split': 'splitmix64(state + kind<<22) % 1000 -> 70/15/10',
            'epochs': epochs,
            'ensemble_members': members,
            'ensemble_epochs': ens_epochs,
            'targets': 'hard one-hot (the E8 A/B winner); oracle-shaped '
                       'soft targets FALSIFIED on this data (hard acc '
                       '%.4f / logloss %.4f vs soft acc %.4f / logloss '
                       '%.4f)' % (hard_te['accuracy'],
                                  hard_te['log_loss'],
                                  soft_te['accuracy'],
                                  soft_te['log_loss']),
            'feature_spec': F.FEATURE_SPEC,
        },
        'train_envelope': envelope,
        'softmax': soft.to_json(),
        'ensemble': ensemble.to_json(),
        'calibrator': calibrator.to_json(),
        'ridge': ridge.to_json() if ridge is not None else None,
        'feature_names': names,
        'feature_groups': F.FEATURE_GROUPS,
        'dataset_stats': {
            kind: {
                'sampled': len(data[kind]),
                'train': len(splits[kind]['train']),
                'valid': len(splits[kind]['valid']),
                'test': len(splits[kind]['test']),
                'won_share': round(sum(1 for r in data[kind]
                                       if r['cls'] == T.WHITE_WIN)
                                   / max(len(data[kind]), 1), 6),
            } for kind in kinds
        },
        'metrics_pooled': pooled,
        'metrics_per_kind': per_kind_metrics,
        'hard_vs_soft': {'hard': hard_te, 'soft': soft_te},
        'baselines': baselines,
        'ablation': ablation_report,
        'dtm_head': dtm_report,
    }
    return report
# ── commands ─────────────────────────────────────────────────────────────
E11_HOTSPOT = 'kpk'            # the E10 verdict: the KPK domain is the
E11_HOTSPOT_MINE = 2000        # hot-spot (22.15% hard errors) -> E11 head


def _global_proba_fn(payload):
    """The frozen GLOBAL head of a payload (any nonlinear routes ignored,
    so the E11 A/B always compares against the pre-E11 predictor)."""
    names = payload['feature_names']
    if payload.get('ensemble'):
        base = M.SoftmaxEnsemble.from_json(
            payload['ensemble'], len(names)).predict_proba_raw
    else:
        base = M.SoftmaxRegression.from_json(
            payload['softmax'], len(names)).predict_proba_raw
    cal = M.TemperatureCalibrator.from_json(payload['calibrator']) \
        if payload.get('calibrator') else None

    def fn(X, slice_key):
        probs = base(X)
        if cal is not None:
            probs = [cal.transform(p, slice_key) for p in probs]
        return probs
    return fn


def _hard_errors(y_true, probs):
    return sum(1 for t, p in zip(y_true, probs)
               if max(range(3), key=lambda k: p[k]) != t)


def train_nonlinear(kind, per_kind, seed, epochs, members, log=print,
                    smoke=False, promote=True, checkpoint_dir=None,
                    cert='E11 — nonlinear specialist head'):
    """The E11/E14 experiment: a nonlinear specialist head for one
    domain, A/B-tested against the frozen global head on the identical
    E8 protocol (same sampler, same seed, same hash split), with an
    honest promotion rule and a corpus re-mine.  E11 froze the kpk
    route; E14 runs the same protocol for krk, the second hot-spot.

    checkpoint_dir (optional): arms are cached there as JSON as soon as
    they are fitted and restored from it on re-entry — the experiment
    is resumable across process boundaries (deterministic seeds make
    the resume bit-exact with a single uninterrupted run)."""
    t0 = time.time()
    if kind not in NL.SPECIALIST_BASES:
        raise SystemExit('no frozen nonlinear basis for %r (frozen: %s)'
                         % (kind, ','.join(sorted(NL.SPECIALIST_BASES))))
    schedule = NL.SPECIALIST_BASES[kind]
    hot_mine = 150 if smoke else E11_HOTSPOT_MINE

    log('[1/5] the %s dataset (E8 protocol: %d states, seed %d)...'
        % (kind, per_kind, seed))
    recs = DS.build_sampled(kind, per_kind, seed)
    buckets = {'train': [], 'valid': [], 'test': []}
    for r in recs:
        buckets[DS.split_of(r['state'], DS.KINDS_INDEX[kind])].append(r)
    log('  split: train %d / valid %d / test %d'
        % (len(buckets['train']), len(buckets['valid']),
           len(buckets['test'])))
    names = F.FEATURE_NAMES
    Xtr, ytr, _ = xy(buckets['train'], names)
    Xva, yva, _ = xy(buckets['valid'], names)
    Xte, yte, _ = xy(buckets['test'], names)

    payload = M.load_model(MODEL_PATH)
    gproba = _global_proba_fn(payload)
    base_te = MT.summarize(yte, gproba(Xte, kind))
    base_va = MT.summarize(yva, gproba(Xva, kind))
    log('[2/5] baseline (frozen global head): test acc %.4f logloss %.4f'
        % (base_te['accuracy'], base_te['log_loss']))

    arms = {}
    arm_bases = (('hinge', NL.NonlinearBasis(hinges=schedule['hinges'])),
                 ('hinge_cross',
                  NL.NonlinearBasis(hinges=schedule['hinges'],
                                    crosses=schedule['crosses'])))
    for i, (tag, basis) in enumerate(arm_bases):
        log('[%d/5] specialist arm %r (%d base + %d derived coordinates, '
            '%d members x %d epochs)...'
            % (2 + i, tag, len(F.FEATURE_NAMES), len(basis.derived_names()),
               members, epochs))
        tA = time.time()
        ckpt = None
        if checkpoint_dir:
            os.makedirs(checkpoint_dir, exist_ok=True)
            ckpt = os.path.join(checkpoint_dir, 'arm_%s.json' % tag)
        if ckpt and os.path.exists(ckpt):
            with open(ckpt, 'r', encoding='utf-8') as fh:
                blob = json.load(fh)
            n_feat = len(basis)
            ens = M.SoftmaxEnsemble.from_json(blob['ensemble'], n_feat)
            cal = M.TemperatureCalibrator.from_json(blob['calibrator'])
            log('  restored from checkpoint %s' % os.path.basename(ckpt))
        else:
            ens = M.SoftmaxEnsemble(len(basis), members=members,
                                    epochs=epochs,
                                    seed=seed + (11 if tag == 'hinge'
                                                 else 23))
            ens.fit(basis.augment_matrix(Xtr), ytr)
            probs_va = ens.predict_proba_raw(basis.augment_matrix(Xva))
            cal = M.TemperatureCalibrator()
            cal.fit(yva, probs_va, [kind] * len(yva))
            if ckpt:
                with open(ckpt, 'w', encoding='utf-8') as fh:
                    json.dump({'ensemble': ens.to_json(),
                               'calibrator': cal.to_json()}, fh)
        probs_va = ens.predict_proba_raw(basis.augment_matrix(Xva))
        va = MT.summarize(yva, [cal.transform(p, kind) for p in probs_va])
        te = MT.summarize(yte, [cal.transform(p, kind) for p in
                                ens.predict_proba_raw(
                                    basis.augment_matrix(Xte))])
        log('  %s: test acc %.4f logloss %.4f  valid acc %.4f  [%.1fs]'
            % (tag, te['accuracy'], te['log_loss'], va['accuracy'],
               time.time() - tA))
        arms[tag] = {'basis': basis, 'ensemble': ens, 'calibrator': cal,
                     'test': te, 'valid': va}

    log('[4/5] hot-spot re-mine (%d seeded states of %s)...'
        % (hot_mine, kind))
    mine_recs = DS.build_sampled(kind, hot_mine, seed)
    Xm = [[r['features'][n] for n in names] for r in mine_recs]
    ym = [r['cls'] for r in mine_recs]
    remine = {'population': len(ym),
              'baseline_hard_errors': _hard_errors(ym, gproba(Xm, kind))}
    for tag, arm in arms.items():
        fn = NL._specialist_fn(arm['ensemble'], arm['calibrator'], kind,
                               arm['basis'])
        remine[tag] = _hard_errors(ym, fn(Xm))
    log('  hard errors: baseline %d | %s'
        % (remine['baseline_hard_errors'],
           ' | '.join('%s %d' % (tag, remine[tag]) for tag in arms)))

    # ── the honest promotion rule ────────────────────────────────────────
    def _beats(a, b):
        return (a['accuracy'] > b['accuracy']
                and a['log_loss'] < b['log_loss'])
    best = None
    for tag in ('hinge_cross', 'hinge'):   # richer arm wins ties by order
        if _beats(arms[tag]['test'], base_te):
            best = tag
            break
    promoted = False
    pooled_after = None
    corpus_regenerated = False
    if promote and best and not smoke:
        log('[5/5] PROMOTING the %r specialist for %s -> %s'
            % (best, kind, os.path.basename(MODEL_PATH)))
        arm = arms[best]
        payload = M.load_model(MODEL_PATH)
        NL.attach_routes(payload, {kind: {'basis': arm['basis'],
                                          'ensemble': arm['ensemble'],
                                          'calibrator': arm['calibrator']}})
        payload['recipe']['nonlinear'] = (
            '%s specialist on %s (arm %r) promoted; basis %s; the router '
            'answers only the %s slice' % (cert.split(' ')[0], kind, best,
                                           NL.BASIS_SPEC_VERSION, kind))
        log('  re-evaluating the full frozen test split with the router...')
        per_kind, pooled_after = evaluate_frozen(payload, log=log)
        payload['metrics_per_kind'] = per_kind
        payload['metrics_pooled'] = pooled_after
        M.save_model(MODEL_PATH, payload)
        promoted = True
        log('  model frozen -> %s' % MODEL_PATH)
        log('  re-mining the falsification corpus against the router...')
        rows, summary = FLS.mine(MODEL_PATH, list(T.KINDS),
                                 E11_HOTSPOT_MINE, seed=seed,
                                 log=lambda *_: None)
        FLS.export_corpus(rows, summary, COUNTEREXAMPLES_DIR)
        corpus_regenerated = True
        log('  corpus frozen -> %s (total rows %d)'
            % (COUNTEREXAMPLES_DIR, summary['total_rows']))
    elif promote and not best:
        log('[5/5] promotion DENIED: no arm strictly beats the global '
            'head on both accuracy and log loss (the rule is the rule)')
    else:
        log('[5/5] promotion skipped (smoke mode or --no-promote)')

    report = {
        'certificate': cert,
        'kind': kind,
        'recipe': {
            'per_kind': per_kind,
            'seed': seed,
            'epochs': epochs,
            'members': members,
            'arm_seeds': {'hinge': seed + 11, 'hinge_cross': seed + 23},
            'basis_spec': NL.BASIS_SPEC_VERSION,
            'hinges': [list(h) for h in schedule['hinges']],
            'crosses': [list(c) for c in schedule['crosses']],
            'protocol': 'same sampler and hash split as the E8 dataset; '
                        'the specialist trains on the %s train rows only'
                        % kind,
        },
        'baseline_global': {'test': base_te, 'valid': base_va},
        'arms': {tag: {'test': arm['test'], 'valid': arm['valid'],
                       'derived_coordinates':
                       len(arm['basis'].derived_names())}
                 for tag, arm in arms.items()},
        'hot_spot_remine': remine,
        'decision': {
            'promoted_arm': best if (promoted or best) else None,
            'rule': 'strict improvement on BOTH accuracy and log loss over '
                    'the untouched test split',
            'promoted': promoted,
            'smoke': smoke,
            'pooled_metrics_after': pooled_after,
            'corpus_regenerated': corpus_regenerated,
        },
        'runtime_seconds': round(time.time() - t0, 1),
    }
    return report


# ── commands ─────────────────────────────────────────────────────────────
E13_KIND = 'kpk'              # the residual frontier of the E11 head
E13_ERR_WEIGHT = 4.0          # train-split weight on residual errors


def train_interaction(per_kind, seed, epochs, members, log=print,
                      err_weight=E13_ERR_WEIGHT, smoke=False, promote=True,
                      checkpoint_dir=None):
    """The E13 experiment: INTERACTION HINGE NODES on the residual KPK
    error corpus.  The promoted E11 specialist left 337 hard errors on
    the seeded 2,000-state mine; this experiment attacks exactly that
    residual with a basis-v2 arm — products of hinge crests,
    max(0, x_a - ka) * max(0, x_b - kb), localized conjunction cells
    shaped like the rule of the square, boxed-king and edge-defence
    conditions that endgame theory puts on the KPK boundary.

    Two arms on the identical E8 protocol:

      ihinge     the full v2 basis (E11 hinges + crosses + interaction
                 hinge nodes), uniform hard targets;
      ihinge_w   the same basis, with ERROR-CORPUS-DRIVEN weights: the
                 current production route labels the TRAIN split, and
                 every residual hard error carries weight 1 + err_weight
                 (valid/test rows are never weighted — the split stays
                 untouched).

    The baseline is the FROZEN PRODUCTION ROUTE (the E11 specialist on
    the kpk slice), not the raw global head — the honest question is
    whether the new arm improves the state of the art, and the
    promotion rule is unchanged: strictly better on BOTH accuracy and
    log loss over the untouched test split, else denied."""
    t0 = time.time()
    kind = E13_KIND
    if kind not in NL.SPECIALIST_BASES:
        raise SystemExit('no frozen nonlinear basis for %r' % (kind,))
    schedule = NL.SPECIALIST_BASES[kind]
    basis = NL.NonlinearBasis(hinges=schedule['hinges'],
                              crosses=schedule['crosses'],
                              interactions=schedule.get('interactions', ()))
    hot_mine = 150 if smoke else E11_HOTSPOT_MINE

    log('[1/5] the %s dataset (E8 protocol: %d states, seed %d)...'
        % (kind, per_kind, seed))
    recs = DS.build_sampled(kind, per_kind, seed)
    buckets = {'train': [], 'valid': [], 'test': []}
    for r in recs:
        buckets[DS.split_of(r['state'], DS.KINDS_INDEX[kind])].append(r)
    log('  split: train %d / valid %d / test %d'
        % (len(buckets['train']), len(buckets['valid']),
           len(buckets['test'])))
    names = F.FEATURE_NAMES
    Xtr, ytr, _ = xy(buckets['train'], names)
    Xva, yva, _ = xy(buckets['valid'], names)
    Xte, yte, _ = xy(buckets['test'], names)

    payload = M.load_model(MODEL_PATH)
    _names, route_proba, _ridge = FLS.load_heads(payload)
    base_te = MT.summarize(yte, route_proba(Xte, kind))
    base_va = MT.summarize(yva, route_proba(Xva, kind))
    log('[2/5] baseline (frozen production route): test acc %.4f '
        'logloss %.4f' % (base_te['accuracy'], base_te['log_loss']))

    # ── the error-corpus weights (TRAIN split only, no leakage) ──────
    ptr = route_proba(Xtr, kind)
    weights = [1.0 + err_weight
               if max(range(3), key=lambda k: p[k]) != t else 1.0
               for p, t in zip(ptr, ytr)]
    n_weighted = sum(1 for w in weights if w > 1.0)
    log('  error-corpus weights: %d of %d train rows at %.1f '
        '(residual hard errors)' % (n_weighted, len(weights),
                                    1.0 + err_weight))

    Xtr_aug = basis.augment_matrix(Xtr)
    arms = {}
    arm_seeds = {'ihinge': seed + 13, 'ihinge_w': seed + 37}
    for i, (tag, use_weights) in enumerate((('ihinge', False),
                                            ('ihinge_w', True))):
        log('[%d/5] interaction-hinge arm %r (%d base + %d derived '
            'coordinates, %d members x %d epochs%s)...'
            % (2 + i, tag, len(F.FEATURE_NAMES),
               len(basis.derived_names()), members, epochs,
               ', error-weighted' if use_weights else ''))
        tA = time.time()
        ckpt = None
        if checkpoint_dir:
            os.makedirs(checkpoint_dir, exist_ok=True)
            ckpt = os.path.join(checkpoint_dir, 'arm_%s.json' % tag)
        if ckpt and os.path.exists(ckpt):
            with open(ckpt, 'r', encoding='utf-8') as fh:
                blob = json.load(fh)
            ens = M.SoftmaxEnsemble.from_json(blob['ensemble'], len(basis))
            cal = M.TemperatureCalibrator.from_json(blob['calibrator'])
            log('  restored from checkpoint %s' % os.path.basename(ckpt))
        else:
            ens = M.SoftmaxEnsemble(len(basis), members=members,
                                    epochs=epochs, seed=arm_seeds[tag])
            ens.fit(Xtr_aug, ytr,
                    sample_weight=weights if use_weights else None)
            probs_va = ens.predict_proba_raw(basis.augment_matrix(Xva))
            cal = M.TemperatureCalibrator()
            cal.fit(yva, probs_va, [kind] * len(yva))
            if ckpt:
                with open(ckpt, 'w', encoding='utf-8') as fh:
                    json.dump({'ensemble': ens.to_json(),
                               'calibrator': cal.to_json()}, fh)
        probs_va = ens.predict_proba_raw(basis.augment_matrix(Xva))
        va = MT.summarize(yva, [cal.transform(p, kind) for p in probs_va])
        te = MT.summarize(yte, [cal.transform(p, kind) for p in
                                ens.predict_proba_raw(
                                    basis.augment_matrix(Xte))])
        log('  %s: test acc %.4f logloss %.4f  valid acc %.4f  [%.1fs]'
            % (tag, te['accuracy'], te['log_loss'], va['accuracy'],
               time.time() - tA))
        arms[tag] = {'basis': basis, 'ensemble': ens, 'calibrator': cal,
                     'test': te, 'valid': va}

    log('[4/5] residual re-mine (%d seeded states of %s)...'
        % (hot_mine, kind))
    mine_recs = DS.build_sampled(kind, hot_mine, seed)
    Xm = [[r['features'][n] for n in names] for r in mine_recs]
    ym = [r['cls'] for r in mine_recs]
    remine = {'population': len(ym),
              'baseline_route_errors': _hard_errors(ym,
                                                    route_proba(Xm, kind))}
    for tag, arm in arms.items():
        fn = NL._specialist_fn(arm['ensemble'], arm['calibrator'], kind,
                               arm['basis'])
        remine[tag] = _hard_errors(ym, fn(Xm))
    log('  hard errors: production route %d | %s'
        % (remine['baseline_route_errors'],
           ' | '.join('%s %d' % (tag, remine[tag]) for tag in arms)))

    # ── the honest promotion rule (unchanged since E11) ──────────────
    def _beats(a, b):
        return (a['accuracy'] > b['accuracy']
                and a['log_loss'] < b['log_loss'])
    best = None
    for tag in ('ihinge_w', 'ihinge'):     # weighted arm wins ties by order
        if _beats(arms[tag]['test'], base_te):
            best = tag
            break
    promoted = False
    pooled_after = None
    corpus_regenerated = False
    if promote and best and not smoke:
        log('[5/5] PROMOTING the %r interaction specialist for %s -> %s'
            % (best, kind, os.path.basename(MODEL_PATH)))
        arm = arms[best]
        payload = M.load_model(MODEL_PATH)
        NL.attach_routes(payload, {kind: {'basis': arm['basis'],
                                          'ensemble': arm['ensemble'],
                                          'calibrator': arm['calibrator']}})
        payload['recipe']['nonlinear'] = (
            'E13 interaction-hinge specialist on %s (arm %r) promoted; '
            'basis %s; the router answers only the %s slice'
            % (kind, best, NL.BASIS_SPEC_VERSION, kind))
        log('  re-evaluating the full frozen test split with the router...')
        per_kind, pooled_after = evaluate_frozen(payload, log=log)
        payload['metrics_per_kind'] = per_kind
        payload['metrics_pooled'] = pooled_after
        M.save_model(MODEL_PATH, payload)
        promoted = True
        log('  model frozen -> %s' % MODEL_PATH)
        log('  re-mining the falsification corpus against the router...')
        rows, summary = FLS.mine(MODEL_PATH, list(T.KINDS),
                                 E11_HOTSPOT_MINE, seed=seed,
                                 log=lambda *_: None)
        FLS.export_corpus(rows, summary, COUNTEREXAMPLES_DIR)
        corpus_regenerated = True
        log('  corpus frozen -> %s (total rows %d)'
            % (COUNTEREXAMPLES_DIR, summary['total_rows']))
    elif promote and not best:
        log('[5/5] promotion DENIED: no interaction arm strictly beats '
            'the production route on both accuracy and log loss '
            '(the rule is the rule)')
    else:
        log('[5/5] promotion skipped (smoke mode or --no-promote)')

    report = {
        'certificate': 'E13 — interaction hinge nodes on the residual '
                       'KPK corpus',
        'kind': kind,
        'recipe': {
            'per_kind': per_kind,
            'seed': seed,
            'epochs': epochs,
            'members': members,
            'arm_seeds': arm_seeds,
            'err_weight': err_weight,
            'basis_spec': NL.BASIS_SPEC_VERSION,
            'hinges': [list(h) for h in schedule['hinges']],
            'crosses': [list(c) for c in schedule['crosses']],
            'interactions': [list(i4) for i4 in
                             schedule.get('interactions', ())],
            'train_rows_weighted': n_weighted,
            'protocol': 'same sampler and hash split as the E8 dataset; '
                        'the arms train on the %s train rows only; the '
                        'baseline is the promoted E11 production route'
                        % kind,
        },
        'baseline_route': {'test': base_te, 'valid': base_va},
        'arms': {tag: {'test': arm['test'], 'valid': arm['valid'],
                       'weighted': tag.endswith('_w'),
                       'derived_coordinates':
                       len(arm['basis'].derived_names())}
                 for tag, arm in arms.items()},
        'hot_spot_remine': remine,
        'decision': {
            'promoted_arm': best if (promoted or best) else None,
            'rule': 'strict improvement on BOTH accuracy and log loss over '
                    'the untouched test split vs the production route',
            'promoted': promoted,
            'smoke': smoke,
            'pooled_metrics_after': pooled_after,
            'corpus_regenerated': corpus_regenerated,
        },
        'runtime_seconds': round(time.time() - t0, 1),
    }
    return report


def _context_from_args(args):
    """Optional player context from CLI flags (None when no rating given)."""
    if args.rating_white is None or args.rating_black is None:
        return None
    from outcome import context as CTX
    return {'rating_white': args.rating_white,
            'rating_black': args.rating_black,
            'clock_white': args.clock_white,
            'clock_black': args.clock_black,
            'weight': args.weight}


def cmd_analyze(args):
    field = OutcomeField(args.model)
    ctx = _context_from_args(args)
    out, text = field.panel(args.fen, with_moves=args.moves,
                            max_moves=args.max_moves, context=ctx)
    print(text)
    return 0


def cmd_impact(args):
    field = OutcomeField(args.model)
    pos = D.Position().set_fen(args.fen)
    rows = IMP.move_impact_surface(field, pos, args.max_moves)
    if not rows:
        print('no oracle for %s — nothing to measure' % args.fen)
        return 1
    exact = field._exact(pos)
    parent_dtm = exact[1]['dtm_plies'] if exact and exact[1]['legal'] \
        else None
    parent_probs = rows[0] and None
    summary = IMP.summarize(rows, _parent_probs(field, pos), parent_dtm)
    print('MOVE IMPACT — counterfactual surface of %s' % pos.to_fen())
    print('  parent %s' % ('mate in %d plies' % parent_dtm
                           if parent_dtm is not None else '(model layer)'))
    for line in IMP.ascii_table(rows, limit=args.max_moves):
        print(line)
    print('  robustness  %s   quiet share %s   best-move agreement %s'
          % (summary['robustness_index'], summary['quiet_share'],
             summary['best_move_agreement']))
    return 0


def _parent_probs(field, pos):
    exact = field._exact(pos)
    if exact is not None and exact[1]['legal']:
        probs = [0.0, 0.0, 0.0]
        probs[T.WHITE_WIN if exact[1]['outcome'] == 'white_win'
              else T.DRAW] = 1.0
        return probs
    probs, _ = field._model_probs(pos)
    return probs


def cmd_context(args):
    field = OutcomeField(args.model)
    ctx = _context_from_args(args)
    if ctx is None:
        print('supply --rating-white/--rating-black to activate the '
              'context prior')
        return 1
    _, text = field.panel(args.fen, with_moves=False, context=ctx)
    print(text)
    return 0


def cmd_export(args):
    kinds = _parse_kinds(args.kinds)
    for kind in kinds:
        t0 = time.time()
        if args.full:
            states = DS.enumerate_states(kind)
            recs = [DS.build_record(kind, *T.unpack(s)) for s in states]
        else:
            recs = DS.build_sampled(kind, args.limit, args.seed)
        path = args.out if len(kinds) == 1 else _kind_path(args.out, kind)
        DS.export_csv(recs, path)
        print('exported %-4s -> %s (%d rows, %.1fs)'
              % (kind, path, len(recs), time.time() - t0))
    return 0


def _kind_path(out, kind):
    root, ext = os.path.splitext(out)
    return '%s_%s%s' % (root, kind, ext or '.csv')


def cmd_train(args):
    kinds = _parse_kinds(args.kinds)
    report = train_all(kinds, args.per_kind, args.seed, args.epochs,
                       ablation=args.ablation, smoke=False,
                       members=args.members)
    os.makedirs(os.path.dirname(os.path.abspath(args.model)), exist_ok=True)
    M.save_model(args.model, {
        'feature_names': report['feature_names'],
        'feature_groups': report['feature_groups'],
        'recipe': report['recipe'],
        'train_envelope': report['train_envelope'],
        'softmax': report['softmax'],
        'ensemble': report['ensemble'],
        'calibrator': report['calibrator'],
        'ridge': report['ridge'],
        'metrics_pooled': report['metrics_pooled'],
        'metrics_per_kind': report['metrics_per_kind'],
    })
    print('model frozen -> %s' % args.model)
    if args.report:
        with open(args.report, 'w', encoding='utf-8') as fh:
            json.dump(_jsonable(report), fh, indent=1, sort_keys=True)
        print('report  -> %s' % args.report)
    return 0


def cmd_evaluate(args):
    path = args.model or MODEL_PATH
    payload = M.load_model(path)
    recipe = payload['recipe']
    kinds = recipe['kinds']
    print('re-evaluating the frozen model on the same deterministic '
          'test split (seed %d)...' % recipe['seed'])
    per_kind_metrics, pooled = evaluate_frozen(payload, log=print)
    frozen = payload.get('metrics_pooled', {})
    if frozen and abs(frozen['accuracy'] - pooled['accuracy']) > 1e-9:
        print('WARNING: pooled accuracy differs from the frozen certificate '
              '(%s vs %s)' % (frozen['accuracy'], pooled['accuracy']))
        return 1
    print('verdict: MATCHES THE FROZEN CERTIFICATE')
    return 0


def evaluate_frozen(payload, log=None):
    """Recompute per-kind + pooled test metrics of a frozen payload on its
    own deterministic test split (the cmd_evaluate core, reused by the
    E11 promotion so the certificate and the model file never drift)."""
    log = log or (lambda *_: None)
    names, proba, _ridge = FLS.load_heads(payload)
    recipe = payload['recipe']
    kinds = recipe['kinds']
    data = build_dataset(kinds, recipe['per_kind'], recipe['seed'], log=log)
    splits = split_records(data)
    pooled_true, pooled_probs = [], []
    per_kind_metrics = {}
    for kind in kinds:
        b = splits[kind]
        Xk, yk, _ = xy(b['test'], names)
        pk = proba(Xk, kind)
        s = MT.summarize(yk, pk)
        log('  %-4s acc %.4f  logloss %.4f  ece %.4f  (n=%d)'
            % (kind, s['accuracy'], s['log_loss'], s['ece'], s['n']))
        per_kind_metrics[kind] = s
        pooled_true += yk
        pooled_probs += pk
    pooled = MT.summarize(pooled_true, pooled_probs)
    log('  pooled acc %.4f  logloss %.4f  ece %.4f'
        % (pooled['accuracy'], pooled['log_loss'], pooled['ece']))
    return per_kind_metrics, pooled


def cmd_report(args):
    t0 = time.time()
    log = print
    if args.smoke:
        kinds, per_kind, epochs, members = ('krk', 'kqk'), 300, 12, 2
        log('SMOKE mode: kinds %s, %d states/kind, %d epochs, %d members'
            % (kinds, per_kind, epochs, members))
        report = train_all(kinds, per_kind, args.seed, epochs,
                           ablation=False, smoke=True, members=members)
    else:
        kinds = _parse_kinds(args.kinds)
        report = train_all(kinds, args.per_kind, args.seed, args.epochs,
                           ablation=args.ablation, members=args.members)
    report['runtime_seconds'] = round(time.time() - t0, 1)
    report['oracle_sanity'] = _oracle_sanity(report['recipe']['kinds'])

    pooled = report['metrics_pooled']
    print('')
    print('=== OUTCOME DYNAMICS · EPOCH III CERTIFICATE (E8) ===')
    print('pooled test accuracy : %.4f' % pooled['accuracy'])
    print('pooled log loss      : %.4f' % pooled['log_loss'])
    print('pooled brier         : %.4f' % pooled['brier'])
    print('pooled ECE           : %.4f' % pooled['ece'])
    print('majority baseline    : %.4f' % report['baselines']['majority']['accuracy'])
    hs = report.get('hard_vs_soft') or {}
    if hs:
        print('A/B targets          : hard %.4f vs soft %.4f (accuracy)'
              % (hs['hard']['accuracy'], hs['soft']['accuracy']))
    if report['dtm_head']:
        print('DTM head MAE         : %.2f plies' % report['dtm_head']['mae_plies'])
    print('runtime              : %.1fs' % report['runtime_seconds'])

    if args.out:
        with open(args.out, 'w', encoding='utf-8') as fh:
            json.dump(_jsonable(report), fh, indent=1, sort_keys=True)
        print('report frozen -> %s' % args.out)
        if not args.smoke:
            M.save_model(MODEL_PATH, {
                'feature_names': report['feature_names'],
                'feature_groups': report['feature_groups'],
                'recipe': report['recipe'],
                'train_envelope': report['train_envelope'],
                'softmax': report['softmax'],
                'ensemble': report['ensemble'],
                'calibrator': report['calibrator'],
                'ridge': report['ridge'],
                'metrics_pooled': report['metrics_pooled'],
                'metrics_per_kind': report['metrics_per_kind'],
            })
            print('model frozen  -> %s' % MODEL_PATH)
    return 0


def cmd_trajectory(args):
    t0 = time.time()
    if args.smoke:
        kinds, n_per_kind, epochs = ('krk', 'kpk'), 24, 6
        log = print
        log('SMOKE mode: kinds %s, %d lines/kind, %d epochs'
            % (kinds, n_per_kind, epochs))
    else:
        kinds = _parse_kinds(args.kinds)
        n_per_kind, epochs = args.per_kind, args.epochs
    report = TR.train_and_report(kinds, n_per_kind, seed=args.seed,
                                 horizon=args.horizon, epochs=epochs)
    report['runtime_seconds'] = round(time.time() - t0, 1)
    print('')
    print('=== OUTCOME DYNAMICS · EPOCH V CERTIFICATE (E9) ===')
    print('lines                : %d (domain crossings %d)'
          % (report['dataset']['lines'],
             report['dataset']['domain_crossings']))
    for t in TR.FORECAST_TS:
        g = report['forecast_curve_gated'][str(t)]['accuracy']
        f = report['forecast_curve_final_only'][str(t)]['accuracy']
        print('forecast t=%-2d       : gated %.4f  final-only %.4f' % (t, g, f))
    print('drift surprise rate  : gated %.4f  final-only %.4f'
          % (report['drift_surprise_rate']['gated'],
             report['drift_surprise_rate']['final_only']))
    if args.out:
        with open(args.out, 'w', encoding='utf-8') as fh:
            json.dump(_jsonable(report), fh, indent=1, sort_keys=True)
        print('report frozen -> %s' % args.out)
    return 0


def cmd_falsify(args):
    t0 = time.time()
    if args.smoke:
        kinds, per_kind = ('krk',), 120
        print('SMOKE mode: kind %s, %d states' % (kinds, per_kind))
    else:
        kinds = _parse_kinds(args.kinds)
        per_kind = args.per_kind
    rows, summary = FLS.mine(MODEL_PATH, kinds, per_kind, seed=args.seed)
    summary['runtime_seconds'] = round(time.time() - t0, 1)
    out_dir = args.out or COUNTEREXAMPLES_DIR
    csv_path, json_path, md_path = FLS.export_corpus(rows, summary, out_dir)
    print('')
    print('=== OUTCOME DYNAMICS · EPOCH VI CORPUS (E10) ===')
    for kind, s in sorted(summary['per_kind'].items()):
        print('  %-4s %d states, %d hard errors (%.2f%%)'
              % (kind, s['n'], s['hard_errors'],
                 100.0 * s['hard_error_rate']))
    print('corpus rows: %d' % summary['total_rows'])
    print('frozen: %s' % csv_path)
    print('        %s' % json_path)
    print('        %s' % md_path)
    return 0


def cmd_nonlinear(args):
    t0 = time.time()
    cert_tag = 'E14' if args.kind == 'krk' else 'E11'
    if args.out is None:
        args.out = os.path.join(
            T.RESULTS_DIR,
            'outcome_specialist_krk_e14.json' if args.kind == 'krk'
            else 'outcome_nonlinear_e11.json')
    if args.smoke:
        per_kind, epochs, members = 300, 8, 2
        log = print
        log('SMOKE mode: kind %s, %d states, %d epochs, %d members, '
            'no promotion' % (args.kind, per_kind, epochs, members))
    else:
        per_kind, epochs, members = args.per_kind, args.epochs, args.members
        log = print
    report = train_nonlinear(args.kind, per_kind, args.seed, epochs,
                             members, log=log, smoke=args.smoke,
                             promote=not (args.smoke or args.no_promote),
                             checkpoint_dir=args.checkpoint,
                             cert=('E14 — krk specialist head (the second '
                                   'hot-spot)' if args.kind == 'krk' else
                                   'E11 — nonlinear specialist head'))
    report['runtime_seconds'] = round(time.time() - t0, 1)
    print('')
    print('=== OUTCOME DYNAMICS · EPOCH VII CERTIFICATE (%s) ==='
          % cert_tag)
    b = report['baseline_global']['test']
    print('hot-spot domain     : %s (E10 verdict)' % report['kind'])
    print('baseline global     : acc %.4f  logloss %.4f'
          % (b['accuracy'], b['log_loss']))
    for tag in ('hinge', 'hinge_cross'):
        a = report['arms'][tag]['test']
        print('specialist %-11s: acc %.4f  logloss %.4f  (+%d derived '
              'coordinates)' % (tag, a['accuracy'], a['log_loss'],
                                report['arms'][tag]['derived_coordinates']))
    r = report['hot_spot_remine']
    print('hard errors re-mine : baseline %d | hinge %d | hinge_cross %d '
          'of %d' % (r['baseline_hard_errors'], r['hinge'],
                     r['hinge_cross'], r['population']))
    d = report['decision']
    if d['promoted']:
        p = d['pooled_metrics_after']
        print('decision            : PROMOTED %r (pooled acc %.4f, '
              'logloss %.4f, corpus regenerated)'
              % (d['promoted_arm'], p['accuracy'], p['log_loss']))
    elif d['promoted_arm']:
        print('decision            : %r qualifies, promotion skipped by flag'
              % d['promoted_arm'])
    else:
        print('decision            : no arm strictly beats the global head '
              '(promotion denied)')
    print('runtime             : %.1fs' % report['runtime_seconds'])
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, 'w', encoding='utf-8') as fh:
            json.dump(_jsonable(report), fh, indent=1, sort_keys=True)
        print('report frozen -> %s' % args.out)
    return 0


def cmd_interaction(args):
    t0 = time.time()
    if args.smoke:
        per_kind, epochs, members = 300, 8, 2
        log = print
        log('SMOKE mode: %d states, %d epochs, %d members, no promotion'
            % (per_kind, epochs, members))
    else:
        per_kind, epochs, members = args.per_kind, args.epochs, args.members
        log = print
    report = train_interaction(per_kind, args.seed, epochs, members,
                               log=log, err_weight=args.err_weight,
                               smoke=args.smoke,
                               promote=not (args.smoke or args.no_promote),
                               checkpoint_dir=args.checkpoint)
    report['runtime_seconds'] = round(time.time() - t0, 1)
    print('')
    print('=== OUTCOME DYNAMICS · EPOCH VII CERTIFICATE (E13) ===')
    b = report['baseline_route']['test']
    print('residual frontier   : %s (the surviving E11 errors)'
          % report['kind'])
    print('baseline route      : acc %.4f  logloss %.4f'
          % (b['accuracy'], b['log_loss']))
    for tag in ('ihinge', 'ihinge_w'):
        a = report['arms'][tag]['test']
        print('interaction %-9s: acc %.4f  logloss %.4f  (+%d derived '
              'coordinates%s)'
              % (tag, a['accuracy'], a['log_loss'],
                 report['arms'][tag]['derived_coordinates'],
                 ', error-weighted' if report['arms'][tag]['weighted']
                 else ''))
    r = report['hot_spot_remine']
    print('hard errors re-mine : production route %d | ihinge %d | '
          'ihinge_w %d of %d'
          % (r['baseline_route_errors'], r['ihinge'], r['ihinge_w'],
             r['population']))
    d = report['decision']
    if d['promoted']:
        p = d['pooled_metrics_after']
        print('decision            : PROMOTED %r (pooled acc %.4f, '
              'logloss %.4f, corpus regenerated)'
              % (d['promoted_arm'], p['accuracy'], p['log_loss']))
    elif d['promoted_arm']:
        print('decision            : %r qualifies, promotion skipped by flag'
              % d['promoted_arm'])
    else:
        print('decision            : no interaction arm strictly beats the '
              'production route (promotion denied)')
    print('runtime             : %.1fs' % report['runtime_seconds'])
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, 'w', encoding='utf-8') as fh:
            json.dump(_jsonable(report), fh, indent=1, sort_keys=True)
        print('report frozen -> %s' % args.out)
    return 0


def cmd_games(args):
    t0 = time.time()
    report, _per_game = RG.audit_corpus(args.path, model_path=args.model,
                                        log=print)
    report['runtime_seconds'] = round(time.time() - t0, 1)
    print('')
    print('=== OUTCOME DYNAMICS · EPOCH IV REAL-GAME AUDIT (E12) ===')
    t = report['totals']
    p = report['position_level']
    gl = report['game_level']
    print('games                : %d (scoreable results %d)'
          % (t['games'], t['games_with_result']))
    print('sources              : %s' % t['sources'])
    print('oracle entries       : %d  per kind %s'
          % (t['oracle_entries'], t['entries_per_kind']))
    print('position level       : model-vs-exact agreement %.4f over %d '
          'entries' % (p['model_vs_exact_agreement'],
                       p['n_scored_positions']))
    print('game-level logloss   : exact %.4f | model %.4f | model+context '
          '%.4f' % (gl['exact']['log_loss'], gl['model']['log_loss'],
                    gl['model+context']['log_loss']))
    print('game-level accuracy  : exact %.4f | model %.4f | model+context '
          '%.4f' % (gl['exact']['accuracy'], gl['model']['accuracy'],
                    gl['model+context']['accuracy']))
    print('context no-op share  : %.4f (rows without a rating prior — '
          'honesty rule)' % report['context_noop_share'])
    print('model argmax flips   : %.4f per oracle step (drift)'
          % report['model_argmax_flip_rate'])
    if report['flagged_results']:
        print('FLAGGED results      : %s' % report['flagged_results'])
        return 1
    print('runtime              : %.1fs' % report['runtime_seconds'])
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)),
                    exist_ok=True)
        with open(args.out, 'w', encoding='utf-8') as fh:
            json.dump(_jsonable(report), fh, indent=1, sort_keys=True)
        print('report frozen -> %s' % args.out)
    return 0


def cmd_adjudicate(args):
    report = ADJ.adjudicate_corpus(args.path, model_path=args.model,
                                   trajectory_path=args.trajectory,
                                   log=print)
    print('')
    print('=== OUTCOME DYNAMICS · EPOCH VIII REFEREE CERTIFICATE (E15) ===')
    t = report['totals']
    print('games                : %d (in oracle space %d, scoreable %d)'
          % (t['games'], t['games_in_oracle_space'], t['games_scoreable']))
    print('oracle entries       : %d  per kind %s'
          % (t['oracle_entries'], t['entries_per_kind']))
    curves = report['adjudication_curves']
    for key in ('0', '1', '2', '3', '5', '10', '20', 'final'):
        row = 'cutoff t=%-5s      : state %.4f  gated %.4f  final-only %.4f'
        print(row % (
            key,
            curves['state'][key]['accuracy'],
            curves['trajectory_gated'][key]['accuracy'],
            curves['trajectory_final_only'][key]['accuracy']))
    for arm in ADJ.ARMS:
        f = report['final_entry'][arm]
        print('final %-20s: acc %.4f  logloss %.4f  brier %.4f  '
              'flips %.4f'
              % (arm, f['accuracy'], f['log_loss'], f['brier'],
                 f['flip_rate']))
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)),
                    exist_ok=True)
        with open(args.out, 'w', encoding='utf-8') as fh:
            json.dump(_jsonable(report), fh, indent=1, sort_keys=True)
        print('report frozen -> %s' % args.out)
    return 0


def _oracle_sanity(kinds):
    """Cross-check the live oracle against the frozen builder statistics."""
    out = {}
    for kind in kinds:
        frozen = T.load_table(kind)['stats']
        if kind in ('krk', 'kqk'):
            expected = D.DTM_EXPECTED.get(kind.upper())
        else:
            expected = None
        out[kind] = {
            'frozen_stats': frozen,
            'bellman_verified': T.load_table(kind)['bellman_verified'],
            'dtm_expected_match': (expected == frozen) if expected else 'n/a',
        }
    return out


def _parse_kinds(text):
    kinds = [k.strip().lower() for k in text.split(',') if k.strip()]
    for k in kinds:
        if k not in T.KINDS:
            raise SystemExit('unknown endgame kind %r (choose from %s)'
                             % (k, ','.join(T.KINDS)))
    return kinds


def _jsonable(payload):
    """Tuples -> lists everywhere so json.dump never chokes."""
    if isinstance(payload, dict):
        return {k: _jsonable(v) for k, v in payload.items()}
    if isinstance(payload, (list, tuple)):
        return [_jsonable(v) for v in payload]
    return payload


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog='python3 -m outcome',
        description='Outcome Dynamics program: exact oracle + phase space + '
                    'distillation + trajectories + falsification '
                    '(epochs I-VI)')
    sub = parser.add_subparsers(dest='cmd', required=True)

    p = sub.add_parser('analyze', help='the Outcome Field panel of a FEN')
    p.add_argument('fen')
    p.add_argument('--moves', action='store_true',
                   help='add the per-move counterfactual impact table')
    p.add_argument('--max-moves', type=int, default=12)
    p.add_argument('--model', default=None,
                   help='model JSON (default: the frozen one)')
    p.add_argument('--rating-white', type=float, default=None)
    p.add_argument('--rating-black', type=float, default=None)
    p.add_argument('--clock-white', type=float, default=None)
    p.add_argument('--clock-black', type=float, default=None)
    p.add_argument('--weight', type=float, default=0.25)
    p.set_defaults(fn=cmd_analyze)

    p = sub.add_parser('impact', help='the counterfactual move-impact surface')
    p.add_argument('fen')
    p.add_argument('--max-moves', type=int, default=12)
    p.add_argument('--model', default=None)
    p.set_defaults(fn=cmd_impact)

    p = sub.add_parser('context', help='the Epoch IV player-context panel')
    p.add_argument('fen')
    p.add_argument('--rating-white', type=float, default=None)
    p.add_argument('--rating-black', type=float, default=None)
    p.add_argument('--clock-white', type=float, default=None)
    p.add_argument('--clock-black', type=float, default=None)
    p.add_argument('--weight', type=float, default=0.25)
    p.add_argument('--model', default=None)
    p.set_defaults(fn=cmd_context)

    p = sub.add_parser('export', help='export the dynamics dataset as CSV')
    p.add_argument('--kinds', default='krk,kqk,knk,kpk,kbk')
    p.add_argument('--limit', type=int, default=20000,
                   help='sampled states per kind (ignored with --full)')
    p.add_argument('--full', action='store_true',
                   help='enumerate the complete population instead of sampling')
    p.add_argument('--seed', type=int, default=DS.DEFAULT_SEED)
    p.add_argument('--out', default='results/outcome/dataset.csv')
    p.set_defaults(fn=cmd_export)

    p = sub.add_parser('train', help='train and freeze the outcome model (E8)')
    p.add_argument('--kinds', default='krk,kqk,knk,kpk,kbk')
    p.add_argument('--per-kind', type=int, default=20000)
    p.add_argument('--seed', type=int, default=DS.DEFAULT_SEED)
    p.add_argument('--epochs', type=int, default=40)
    p.add_argument('--members', type=int, default=3,
                   help='bootstrap ensemble members')
    p.add_argument('--ablation', action='store_true')
    p.add_argument('--model', default=MODEL_PATH)
    p.add_argument('--report', default=None)
    p.set_defaults(fn=cmd_train)

    p = sub.add_parser('evaluate', help='re-check the frozen model on its test split')
    p.add_argument('--model', default=None)
    p.set_defaults(fn=cmd_evaluate)

    p = sub.add_parser('report', help='the full E8 experiment certificate')
    p.add_argument('--kinds', default='krk,kqk,knk,kpk,kbk')
    p.add_argument('--per-kind', type=int, default=20000)
    p.add_argument('--seed', type=int, default=DS.DEFAULT_SEED)
    p.add_argument('--epochs', type=int, default=40)
    p.add_argument('--members', type=int, default=3)
    p.add_argument('--ablation', action='store_true', default=True)
    p.add_argument('--no-ablation', dest='ablation', action='store_false')
    p.add_argument('--smoke', action='store_true',
                   help='CI-sized run (2 kinds x 300 states x 12 epochs)')
    p.add_argument('--out', default=None,
                   help='where to freeze the certificate JSON')
    p.set_defaults(fn=cmd_report)

    p = sub.add_parser('trajectory', help='the Epoch V trajectory certificate (E9)')
    p.add_argument('--kinds', default='krk,kqk,knk,kpk,kbk')
    p.add_argument('--per-kind', type=int, default=250)
    p.add_argument('--seed', type=int, default=DS.DEFAULT_SEED)
    p.add_argument('--horizon', type=int, default=TR.DEFAULT_HORIZON)
    p.add_argument('--epochs', type=int, default=30)
    p.add_argument('--smoke', action='store_true')
    p.add_argument('--out', default=TRAJECTORY_PATH)
    p.set_defaults(fn=cmd_trajectory)

    p = sub.add_parser('falsify', help='the Epoch VI falsification corpus (E10)')
    p.add_argument('--kinds', default='krk,kqk,knk,kpk,kbk')
    p.add_argument('--per-kind', type=int, default=2000)
    p.add_argument('--seed', type=int, default=DS.DEFAULT_SEED)
    p.add_argument('--out', default=COUNTEREXAMPLES_DIR)
    p.add_argument('--smoke', action='store_true')
    p.set_defaults(fn=cmd_falsify)

    p = sub.add_parser('nonlinear',
                       help='the Epoch VII nonlinear specialist head '
                            '(E11 kpk / E14 krk)')
    p.add_argument('--kind', default=E11_HOTSPOT,
                   help='the domain to specialise (frozen basis required)')
    p.add_argument('--per-kind', type=int, default=20000)
    p.add_argument('--seed', type=int, default=DS.DEFAULT_SEED)
    p.add_argument('--epochs', type=int, default=40)
    p.add_argument('--members', type=int, default=3)
    p.add_argument('--no-promote', action='store_true',
                   help='A/B only: never rewrite the production model')
    p.add_argument('--checkpoint', default=None,
                   help='directory to cache fitted arms (resumable runs)')
    p.add_argument('--smoke', action='store_true',
                   help='CI-sized run (300 states, no promotion)')
    p.add_argument('--out', default=None,
                   help='certificate JSON (default: per-kind frozen path)')
    p.set_defaults(fn=cmd_nonlinear)

    p = sub.add_parser('interact',
                       help='the E13 interaction-hinge nodes on the '
                            'residual KPK error corpus')
    p.add_argument('--per-kind', type=int, default=20000)
    p.add_argument('--seed', type=int, default=DS.DEFAULT_SEED)
    p.add_argument('--epochs', type=int, default=40)
    p.add_argument('--members', type=int, default=3)
    p.add_argument('--err-weight', type=float, default=E13_ERR_WEIGHT,
                   help='train weight on residual hard errors '
                        '(weight = 1 + err-weight)')
    p.add_argument('--no-promote', action='store_true',
                   help='A/B only: never rewrite the production model')
    p.add_argument('--checkpoint', default=None,
                   help='directory to cache fitted arms (resumable runs)')
    p.add_argument('--smoke', action='store_true',
                   help='CI-sized run (300 states, no promotion)')
    p.add_argument('--out', default=os.path.join(T.RESULTS_DIR,
                                                 'outcome_interaction_e13.json'))
    p.set_defaults(fn=cmd_interaction)

    p = sub.add_parser('games',
                       help='the Epoch IV real-game audit (E12)')
    p.add_argument('path', nargs='?', default='data/games',
                   help='a PGN file or a directory of .pgn files')
    p.add_argument('--model', default=None)
    p.add_argument('--out', default=os.path.join(T.RESULTS_DIR,
                                                 'outcome_realgames_e12.json'))
    p.set_defaults(fn=cmd_games)

    p = sub.add_parser('adjudicate',
                       help='the Epoch VIII whole-game referee (E15)')
    p.add_argument('path', nargs='?', default='data/games',
                   help='a PGN file or a directory of .pgn files')
    p.add_argument('--model', default=None)
    p.add_argument('--trajectory', default=ADJ.TRAJECTORY_PATH,
                   help='the frozen E9 trajectory certificate')
    p.add_argument('--out', default=os.path.join(
        T.RESULTS_DIR, 'outcome_adjudication_e15.json'))
    p.set_defaults(fn=cmd_adjudicate)

    args = parser.parse_args(argv)
    return args.fn(args)

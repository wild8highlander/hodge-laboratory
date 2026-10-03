# Large Board Laboratory — отчёт прогона / run report

**chess-dynamics-lab** · автор программы: **Исаев Исхак Хамзатович** · github.com/wild8highlander/chess-dynamics-lab

*Дата / date:* 2026-09-30 16:54:50 · *Julia:* 1.10.10 · *seed:* `20260930`

## Параметры прогона / run parameters

| параметр / parameter | значение / value |
|---|---|
| `dpi` | `600` |
| `expect` | `none` |
| `fig` | `12.0x8.0` |
| `flow_rooks` | `3` |
| `kqk` | `true` |
| `krk` | `true` |
| `lam` | `0.25` |
| `lang` | `ru` |
| `max_plies` | `512` |
| `mu` | `0.1` |
| `n` | `112` |
| `oracle_ns` | `[4, 6, 8, 10]` |
| `outdir` | `results/large_board_lab` |
| `playouts_check` | `48` |
| `playouts_main` | `64` |
| `policies` | `["particle", "pressure", "mobility"]` |
| `scaling_ns` | `[8, 16, 32, 64, 112]` |
| `seed` | `20260930` |
| `trap_positions` | `300` |

## Главный тест / MAIN TEST — T7 · вердикт частичной политики / partial policy verdict

### Вердикт / verdict: **ОБОЮДНАЯ ФОРС-НИЧЬЯ**

**Консенсус / consensus:** `unanimous` · **класс доказательности / evidence class:** `partial_policy`

| сценарий | ничья | белые | чёрные | партий |
|---|---|---|---|---|
| KRK | 1.0 | 0.0 | 0.0 | 192 |
| KQK | 1.0 | 0.0 | 0.0 | 192 |

### Ансамбль политик / policy ensemble

| политика / policy | партий / games | ничья / draw | белые / white | чёрные / black | вердикт / verdict | уровень / tier |
|---|---|---|---|---|---|---|
| PARTICLE | 128 | 1.0 | 0.0 | 0.0 | draw | F |
| PRESSURE | 128 | 1.0 | 0.0 | 0.0 | draw | F |
| MOBILITY | 128 | 1.0 | 0.0 | 0.0 | draw | F |

Уровни вердикта политики / verdict tiers: `F` = форс (НИ ДИ > 50%) · `L` = склоняется (доля ≥ 75%) · `I` = неопределён / forced · leaning · inconclusive.

**Покрытие / coverage:** стартов / starts `128` · полуходов / plies `28003` · пространство / states ≈`3.947e12` · доля / share `3.24e-11`

> Лестница доказательности: ПОЛНОЕ РЕШЕНИЕ > СЛАБОЕ > УЛЬТРАСЛАБОЕ > ЧАСТИЧНАЯ ПОЛИТИКА — уровень этого прогона: ЧАСТИЧНАЯ ПОЛИТИКА.

> Это вердикт ЧАСТИЧНОЙ ПОЛИТИКИ: ансамбль аппроксиматоров (именованных политик) на выборочных стартах, а не теоретико-игровое доказательство. См. complexity/SOLVING_CHESS.md: истинное решение требует уровней, определённых там.

## Тесты / tests

| тест | статус | ключевые значения |
|---|---|---|
| T1 census | PASS | boards 8,16,32,64,112 · n=8 union check 1792 |
| T2 legality battery | PASS | boards 8/16/112 · checks ×1826 |
| T3 oracle self-verification | PASS | max DTM: n=4: 7m · n=6: 12m · n=8: 16m · n=10: 21m |
| T4 trap census | PASS | sample 300x2 per scenario |
| T5 scaling | PASS | slope ≈ 2.78 · t(n=112) = 0.00788 s |
| T7 MAIN partial-policy verdict | PASS |  |
| T8 explicit outcome check | PASS |  |
| T9 flow showcase | PASS |  |

## Графики / charts (PNG 600 dpi + SVG)

- `charts/chart1_scaling.png` / `.svg`
- `charts/chart2_outcomes.png` / `.svg`
- `charts/chart3_flow.png` / `.svg`
- `charts/chart4_dtm_growth.png` / `.svg`

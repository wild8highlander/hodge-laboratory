#!/usr/bin/env julia
#=
═══════════════════════════════════════════════════════════════════════════════
  LARGE BOARD LABORATORY · large_board_lab.jl            (single file, no deps)
═══════════════════════════════════════════════════════════════════════════════

  chess-dynamics-lab — particle verification on LARGE generalized boards.

  Program author: Isaev Iskhak Khamzatovich
  Repository:     github.com/wild8highlander/chess-dynamics-lab
  License:        individual exclusive license (see LICENSE)

  PURPOSE.

    Interactive Julia laboratory that verifies the generalized n x n particle
    dynamics of complexity/ on LARGE matrices — the default board is 112x112
    (12544 cells). It is the big-board companion of dynamics.py (protocol
    C1-C9) and complexity/generalized_chess.py (theorems T13/T14).

    The lab is SELF-CONTAINED: Base + two bundled stdlibs (Printf, Dates).
    No packages, no downloads, no build step.  Run it right in the repo:

        julia large_board_lab.jl              # interactive menu (RU/EN)
        julia large_board_lab.jl --lang=en    # headless full laboratory run
        julia large_board_lab.jl --selftest   # 30-second sanity battery

    WHAT IS INSIDE.

      · Engine      n x n board (n up to 112+), piece set {K,N,B,R,Q}
                    (pawnless generalized set — the T13/T14 scope; pawn
                    rules live in the 8x8 core engine engine/analyzer.py);
                    Zobrist hashing, legality, K3 threat fields, mobility.
      · Solver      three-layer particle chooser: potential (material)
                    + mu * kinetic (mobility, T05 mu = 0.1)
                    + lam * K3 pressure on the enemy king ring (lam = 0.25);
                    KLEIN determinism via a lexicographic tie-break.
      · Oracle      exact retrograde DTM for K+R / K+Q vs K on n x n boards
                    (Bellman layered propagation over the packed state space,
                    polynomial in n for the fixed k = 3 pieces — T14 (ii)).
      · Tests       T1 census, T2 legality battery, T3 oracle self-check,
                    T4 particle-vs-oracle trap census (E1 link),
                    T5 scaling benchmark to n = 112 (T14 link),
                    T7 MAIN TEST — the PARTIAL POLICY VERDICT:
                    an ENSEMBLE of named policies (particle, pressure,
                    mobility, material, random) plays paired playouts and
                    the lab reports which chess outcome (DRAW / WHITE WIN /
                    BLACK WIN) the dynamics implies — per policy, per
                    scenario, pooled, with consensus and coverage.  It is
                    explicitly the verdict of a PARTIAL policy (an
                    approximator), see complexity/SOLVING_CHESS.md —
                    not a game-theoretic proof,
                    T8 explicit outcome check (draw / white / black).
      · Reports     TXT log + JSON + CSV + Markdown, one run folder per run.
      · Charts      4 charts x (PNG 600 dpi + SVG vector), zero dependencies:
                    the PNG encoder (zlib fixed-Huffman deflate, CRC32,
                    Adler-32) and the rasterizer are implemented in this
                    file. Chart glyphs are rendered from an embedded 32x32
                    bitmap font derived from DejaVu Sans (Bitstream Vera
                    license) — that is also why chart labels are ASCII +
                    Cyrillic only.

  CLI (all optional; parameters are also editable in the menu):

        --lang=ru|en        UI language (default: ru)
        --n=112             large board side (the big matrix)
        --oracle-n=4,6,8,10 exact-oracle board sizes
        --policy=a,b,c      T7 policy ensemble, any of
                            particle|mobility|pressure|material|random|all
                            (default: particle,pressure,mobility)
        --playouts=64       playouts per scenario PER POLICY in the MAIN test
        --check-playouts=48 playouts for the explicit outcome check
        --maxplies=512      playout cap of one playout
        --mu=0.1 --lam=0.25 particle weights (T05 / K3)
        --seed=20260930     deterministic seed (splitmix64)
        --dpi=600           chart resolution (PNG)
        --fig=12x8          chart figure size in inches
        --scaling=8,16,32,64,112  T5 benchmark board list
        --expect=draw|white|black  T8 expected outcome
        --test=t1|t2|t3|t4|t5|main|check|flow  headless single test
        --outdir=...        report root (default results/large_board_lab)
        --quick             fast preset (smoke run)
        --menu              force the interactive menu
        --selftest          headless sanity battery and exit

═══════════════════════════════════════════════════════════════════════════════
=#

using Printf
using Dates

# ──────────────────────────────────────────────────────────────────────────────
# ANSI / terminal appearance
# ──────────────────────────────────────────────────────────────────────────────

const IS_TTY = try
    isatty(stdout)
catch
    false
end

ansic(code::String) = "\x1b[" * code * "m"
const A_RESET = "\x1b[0m"

mutable struct Palette
    on::Bool
    title::String; accent::String; ok::String; bad::String; warn::String
    dim::String; white::String; blackc::String; draw::String; hl::String
end
Palette(on::Bool) = Palette(on,
    on ? "\x1b[38;5;39m"  : "",   # title   (blue)
    on ? "\x1b[38;5;220m" : "",   # accent  (gold)
    on ? "\x1b[38;5;114m" : "",   # ok      (green)
    on ? "\x1b[38;5;203m" : "",   # bad     (red)
    on ? "\x1b[38;5;215m" : "",   # warn    (orange)
    on ? "\x1b[38;5;245m" : "",   # dim
    on ? "\x1b[38;5;231m" : "",   # white
    on ? "\x1b[38;5;250m" : "",   # black pieces (light gray on dark bg)
    on ? "\x1b[38;5;250m" : "",   # draw
    on ? "\x1b[1m\x1b[38;5;220m" : "")  # highlight

function paint(P::Palette, s::AbstractString)
    P.on || return String(s)
    # strings passed here are pre-colored; nothing to do
    return String(s)
end

# ──────────────────────────────────────────────────────────────────────────────
# Deterministic RNG — splitmix64 (same family as the polyglot Zobrist core)
# ──────────────────────────────────────────────────────────────────────────────

mutable struct SM64
    x::UInt64
end

function next!(g::SM64)
    g.x += 0x9e3779b97f4a7c15
    z = g.x
    z = (z ⊻ (z >> 30)) * 0xbf58476d1ce4e5b9
    z = (z ⊻ (z >> 27)) * 0x94d049bb133111eb
    return z ⊻ (z >> 31)
end

rand01!(g::SM64) = Float64(next!(g) >> 11) * (1.0 / 9007199254740992.0) # 2^53
randint!(g::SM64, lo::Int, hi::Int) = lo + Int(next!(g) % UInt64(hi - lo + 1))

# ──────────────────────────────────────────────────────────────────────────────
# Policy ensemble (the partial-policy verdict machinery of the MAIN test)
#   particle  — the three-layer particle solver itself (mu, lam)
#   mobility  — pure kinetic greedy (T05, mu = 1, lam = 0)
#   pressure  — pure K3-pressure greedy (T04, mu = 0, lam = 1)
#   material  — pure material greedy (mu = 0, lam = 0)
#   random    — uniform random legal mover (seeded)
# The MAIN test T7 plays ALL enabled policies on the SAME sampled starts
# (paired design) and merges them into one PARTIAL POLICY VERDICT with a
# per-policy breakdown, consensus class and honest coverage accounting.
# ──────────────────────────────────────────────────────────────────────────────

const POLICY_NAMES = (:particle, :mobility, :pressure, :material, :random)

function parse_policies(s::AbstractString)
    lower = lowercase(strip(String(s)))
    lower == "all" && return collect(POLICY_NAMES)
    syms = Symbol[]
    for tok in split(lower, ",")
        x = Symbol(strip(tok))
        (x in POLICY_NAMES && !(x in syms)) && push!(syms, x)
    end
    return isempty(syms) ? [:particle] : syms
end

# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────

Base.@kwdef mutable struct Config
    lang::Symbol              = :ru
    n::Int                    = 112        # the LARGE board
    oracle_ns::Vector{Int}    = [4, 6, 8, 10]
    krk::Bool                 = true
    kqk::Bool                 = true
    playouts_main::Int        = 64         # per scenario PER POLICY (main test)
    policies::Vector{Symbol}  = [:particle, :pressure, :mobility]
    playouts_check::Int       = 48
    max_plies::Int            = 512
    mu::Float64               = 0.1
    lam::Float64              = 0.25
    seed::Int                 = 20260930
    dpi::Int                  = 600
    fig_w::Float64            = 12.0
    fig_h::Float64            = 8.0
    scaling_ns::Vector{Int}   = [8, 16, 32, 64, 112]
    scaling_pos::Int          = 6
    outdir::String            = "results/large_board_lab"
    trap_positions::Int       = 300
    expect::Symbol            = :none      # :draw | :white | :black
    flow_rooks::Int           = 3          # rooks per side in the flow showcase
    flow_plies::Int           = 60
    quick::Bool               = false
    color::Bool               = IS_TTY
    headless_test::String     = ""
    force_menu::Bool          = false
end

function parse_cli!(cfg::Config)
    for a in ARGS
        flag, val = begin
            i = findfirst(isequal('='), a)
            i === nothing ? (a, "") : (a[1:prevind(a, i)], a[nextind(a, i):end])
        end
        try
            if     flag == "--lang"      cfg.lang = Symbol(lowercase(val))
            elseif flag == "--n"         cfg.n = max(4, parse(Int, val))
            elseif flag == "--oracle-n"  cfg.oracle_ns = [max(3, parse(Int, s)) for s in split(val, ",")]
            elseif flag == "--playouts"  cfg.playouts_main = max(1, parse(Int, val))
            elseif flag == "--policy"    cfg.policies = parse_policies(val)
            elseif flag == "--check-playouts" cfg.playouts_check = max(1, parse(Int, val))
            elseif flag == "--maxplies"  cfg.max_plies = max(8, parse(Int, val))
            elseif flag == "--mu"        cfg.mu = parse(Float64, val)
            elseif flag == "--lam"       cfg.lam = parse(Float64, val)
            elseif flag == "--seed"      cfg.seed = parse(Int, val)
            elseif flag == "--dpi"       cfg.dpi = max(72, parse(Int, val))
            elseif flag == "--fig"       w, h = split(val, "x"); cfg.fig_w = parse(Float64, w); cfg.fig_h = parse(Float64, h)
            elseif flag == "--scaling"   cfg.scaling_ns = [max(4, parse(Int, s)) for s in split(val, ",")]
            elseif flag == "--scaling-pos" cfg.scaling_pos = max(1, parse(Int, val))
            elseif flag == "--outdir"    cfg.outdir = val
            elseif flag == "--traps"     cfg.trap_positions = max(10, parse(Int, val))
            elseif flag == "--expect"    cfg.expect = Symbol(lowercase(val))
            elseif flag == "--flow-rooks" cfg.flow_rooks = max(1, parse(Int, val))
            elseif flag == "--flow-plies" cfg.flow_plies = max(4, parse(Int, val))
            elseif flag == "--test"      cfg.headless_test = lowercase(val)
            elseif flag == "--quick"     cfg.quick = true
            elseif flag == "--menu"      cfg.force_menu = true
            end
        catch
            @printf(stderr, "bad CLI flag: %s\n", a)
            exit(2)
        end
    end
    if cfg.quick
        cfg.playouts_main  = min(cfg.playouts_main, 12)
        cfg.playouts_check = min(cfg.playouts_check, 12)
        cfg.oracle_ns      = [4, 6]
        cfg.scaling_ns     = [8, 16, 32, 112]
        cfg.trap_positions = 60
    end
    cfg.lang in (:ru, :en) || (cfg.lang = :ru)
end

# ──────────────────────────────────────────────────────────────────────────────
# UI strings — Russian / English
# ──────────────────────────────────────────────────────────────────────────────

const STR = Dict{Symbol,Dict{String,String}}()

STR[:en] = Dict{String,String}(
    "prog"        => "LARGE BOARD LABORATORY",
    "lab_title"   => "PARTICLE CHESS DYNAMICS ON LARGE BOARDS",
    "menu_title"  => "MAIN MENU",
    "menu_hint"   => "type a number and press Enter",
    "m_lab"       => "FULL LABORATORY RUN  (all tests + reports + 4 charts)",
    "m_t1"        => "T1  Board census — closed forms vs move graph (n x n)",
    "m_t2"        => "T2  Legality battery — invariants on random playouts",
    "m_t3"        => "T3  Oracle self-verification — retrograde DTM (small n)",
    "m_t4"        => "T4  Trap census — particle vs oracle (E1 link)",
    "m_t5"        => "T5  Scaling benchmark — per-move cost up to n = 112 (T14)",
    "m_t7"        => "T7  MAIN TEST — partial policy verdict (policy ensemble)",
    "m_t8"        => "T8  Explicit outcome check — draw / white win / black win",
    "m_flow"      => "T9  Flow showcase — particle field and trajectories",
    "m_params"    => "Parameters",
    "m_lang"      => "Language / Язык",
    "m_quit"      => "Quit",
    "m_prompt"    => "select> ",
    "m_unknown"   => "unknown command, try again",
    "m_press"     => "press Enter to return to the menu...",
    "m_bye"       => "the particles settle. Goodbye.",
    "m_charts_note" => "(charts and reports are produced by the laboratory run)",
    "p_header"    => "PARAMETERS  (Enter = keep current value)",
    "p_bad"       => "invalid value, keeping the previous one",
    "prm_n"       => "large board side n",
    "prm_oracle"  => "oracle board sizes (comma list, exact DTM)",
    "prm_play"    => "playouts per scenario — main test",
    "prm_check"   => "playouts — explicit outcome check",
    "prm_maxplies"=> "playout length cap (plies)",
    "prm_mu"      => "kinetic weight mu (T05)",
    "prm_lam"     => "K3 pressure weight lambda",
    "prm_seed"    => "deterministic seed",
    "prm_dpi"     => "chart DPI (PNG)",
    "prm_fig"     => "figure size in inches WxH",
    "prm_scaling" => "scaling benchmark board list",
    "prm_traps"   => "trap-census sample size",
    "prm_krk"     => "scenario KRK enabled (on/off)",
    "prm_kqk"     => "scenario KQK enabled (on/off)",
    "prm_expect"  => "expected outcome for T8 (draw/white/black/none)",
    "prm_policies" => "T7 policy ensemble (comma list or all)",
    "sel_pol"     => "policies (comma list or all): ",
    "prm_flowr"   => "rooks per side in the flow showcase",
    "prm_outdir"  => "report output directory",
    "prm_lang"    => "language (ru/en)",
    "c_yes"       => "yes", "c_no" => "no", "c_on" => "on", "c_off" => "off",
    "c_back"      => "back",
    "cells"       => "cells",
    "t1_title"    => "T1 · BOARD CENSUS — closed forms vs generated move graph",
    "t1_rook"     => "rook graph edges",  "t1_bishop" => "bishop graph edges",
    "t1_knight"   => "knight graph edges", "t1_king"   => "king graph edges",
    "t1_queen"    => "queen = rook + bishop identity",
    "t1_note"     => "all counts directed; closed forms must match the generator",
    "t2_title"    => "T2 · LEGALITY BATTERY — random playout invariants",
    "t3_title"    => "T3 · ORACLE SELF-VERIFICATION — retrograde DTM, K+piece vs K",
    "t4_title"    => "T4 · TRAP CENSUS — particle solver vs exact oracle (E1 link)",
    "t5_title"    => "T5 · SCALING BENCHMARK — polynomial move choice (T14)",
    "t7_title"    => "T7 · MAIN TEST — PARTIAL POLICY VERDICT: WHICH OUTCOME DOES THE DYNAMICS IMPLY?",
    "t8_title"    => "T8 · EXPLICIT OUTCOME CHECK",
    "t9_title"    => "T9 · FLOW SHOWCASE — K3 field and particle trajectories",
    "or_states"   => "states", "or_edges" => "edges", "or_won" => "won",
    "or_mates"    => "mates",  "or_max"   => "max DTM (moves)", "or_time" => "time",
    "t3_struct"   => "structural self-consistency (winning move chain)",
    "t3_mono"     => "max DTM grows with n",
    "t3_ok"       => "oracle invariants hold",
    "t4_won"      => "won positions sampled (White to move)",
    "t4_correct"  => "win kept (DTM - 1)",
    "t4_slow"     => "win kept, slower",
    "t4_blund"    => "blunder: win -> draw",
    "t4_drawn"    => "drawn positions sampled (White to move)",
    "t4_lost"     => "lost positions (Black to move, resistance test)",
    "t4_trapfall" => "traps fallen into: draw -> loss",
    "t4_trate"    => "particle blunder rate",
    "t5_move"     => "mean per-move time",
    "t5_ply"      => "mean per-ply time (full playout)",
    "t5_slope"    => "log-log slope (last two boards)",
    "t5_nodes"    => "candidate moves evaluated per choice",
    "main_scen"   => "scenarios",
    "main_runs"   => "playouts per scenario",
    "plies_hdr"   => "plies",
    "out_draw"    => "draw", "out_white" => "WHITE WIN", "out_black" => "BLACK WIN",
    "r_rep"       => "repetition", "r_stale" => "stalemate", "r_bare" => "material captured",
    "r_cap"       => "ply cap reached", "r_mate" => "checkmate",
    "v_draw"      => "MUTUAL FORCEFUL DRAW",
    "v_white"     => "FORCED WHITE WIN",
    "v_black"     => "FORCED BLACK WIN",
    "v_inconc"    => "INCONCLUSIVE — increase the number of playouts",
    "v_honest"    => "This is the verdict of a PARTIAL POLICY: an ensemble of approximators (named policies) on sampled starts, NOT a game-theoretic proof. See complexity/SOLVING_CHESS.md: a true solve requires the levels defined there.",
    "v_honest_one" => "This is the verdict of a PARTIAL POLICY (the particle approximator on sampled starts), NOT a game-theoretic proof. See complexity/SOLVING_CHESS.md: a true solve requires the levels defined there.",
    "v_ladder"    => "Evidence ladder: FULL > WEAK > ULTRA-WEAK > PARTIAL POLICY — this run's level: PARTIAL POLICY.",
    "pol_ens"     => "policy ensemble",
    "policy"      => "policy",
    "pool"        => "pool",
    "consensus"   => "consensus",
    "cons_unan"   => "UNANIMOUS",
    "cons_major"  => "MAJORITY",
    "cons_split"  => "SPLIT",
    "tier_legend" => "policy verdict tier: F = forced (CI floor > 50%) · L = leaning (plurality >= 75%) · I = inconclusive",
    "cov_starts"  => "unique sampled starting positions",
    "cov_plies"   => "plies played in total",
    "cov_states"  => "scenario state-space estimate",
    "cov_share"   => "sampling coverage",
    "main_stat"   => "outcome distribution",
    "main_plies"  => "mean plies to finish",
    "t8_expect"   => "expected outcome",
    "t8_agree"    => "AGREE — the dynamics supports the expected outcome",
    "t8_weak"     => "WEAK AGREEMENT — expected outcome is the plurality, CI is wide",
    "t8_dis"      => "DISAGREE — the dynamics contradicts the expected outcome",
    "c1_title"    => "Particle move choice is polynomial in n  ·  T14",
    "c1_xlabel"   => "board side n (log scale)",
    "c1_ylabel"   => "seconds per move (log scale)",
    "c1_meas"     => "measured (K+R vs K)",
    "c1_ref2"     => "O(n^2) reference",
    "c1_ref4"     => "O(n^4) reference (naive field rescoring)",
    "c2_title"    => "Outcome distribution of particle playouts",
    "c2_ylabel"   => "share of playouts",
    "c3_title"    => "K3 threat field on the {N}x{N} board — particle flow",
    "c3_bar"      => "attack pressure",
    "c4_title"    => "Exact oracle: longest mate grows polynomially  ·  T14(ii)",
    "c4_xlabel"   => "board side n",
    "c4_ylabel"   => "max DTM (moves)",
    "c4_fit"      => "power fit a*n^b",
    "c4_states"   => "states",
    "rep_dir"     => "run folder",
    "rep_files"   => "reports written",
    "progress_note" => "deterministic seeded playouts",
    "eta"         => "ETA",
    "elapsed"     => "elapsed",
    "sel_exp"     => "expected outcome: [d]raw / [w]hite / [b]lack / [n]one ?",
    "run_hdr"     => "RUN PARAMETERS",
    "lang_set"    => "language switched to English",
    "threads"     => "worker threads",
    "quick_on"    => "QUICK preset active (smoke run)",
    "selftest"    => "SELFTEST",
    "st_png"      => "PNG encoder round-trip",
    "st_engine"   => "n x n engine invariants",
    "st_solver"   => "particle solver legality",
    "st_all"      => "SELFTEST OK",
    "verdict"     => "VERDICT",
    "board"       => "board",
    "scenario"    => "scenario",
    "plays"       => "playouts",
    "share"       => "share",
    "ci95"        => "95% CI",
    "summary"     => "SUMMARY",
    "st_title"    => "T1-T5 + T7-T9 quick battery",
)

STR[:ru] = Dict{String,String}(
    "prog"        => "ЛАБОРАТОРИЯ БОЛЬШИХ ДОСОК",
    "lab_title"   => "ЧАСТИЧНАЯ ШАХМАТНАЯ ДИНАМИКА НА БОЛЬШИХ ДОСКАХ",
    "menu_title"  => "ГЛАВНОЕ МЕНЮ",
    "menu_hint"   => "введите номер и нажмите Enter",
    "m_lab"       => "ПОЛНЫЙ ЗАПУСК ЛАБОРАТОРИИ  (все тесты + отчёты + 4 графика)",
    "m_t1"        => "T1  Перепись доски — замкнутые формы против графа ходов (n x n)",
    "m_t2"        => "T2  Батарея легальности — инварианты случайных партий",
    "m_t3"        => "T3  Самопроверка оракула — ретроградный DTM (малые n)",
    "m_t4"        => "T4  Перепись ловушек — частицы против оракула (связь с E1)",
    "m_t5"        => "T5  Бенчмарк масштабирования — цена хода до n = 112 (T14)",
    "m_t7"        => "T7  ГЛАВНЫЙ ТЕСТ — вердикт частичной политики (ансамбль политик)",
    "m_t8"        => "T8  Явная проверка исхода — ничья / победа белых / победа чёрных",
    "m_flow"      => "T9  Витрина потока — поле частиц и траектории",
    "m_params"    => "Параметры",
    "m_lang"      => "Язык / Language",
    "m_quit"      => "Выход",
    "m_prompt"    => "выбор> ",
    "m_unknown"   => "неизвестная команда, повторите",
    "m_press"     => "нажмите Enter для возврата в меню...",
    "m_bye"       => "частицы затихают. До встречи.",
    "m_charts_note" => "(графики и отчёты формируются при запуске лаборатории)",
    "p_header"    => "ПАРАМЕТРЫ  (Enter — оставить текущее значение)",
    "p_bad"       => "некорректное значение, оставлено прежнее",
    "prm_n"       => "сторона большой доски n",
    "prm_oracle"  => "размеры досок оракула (список через запятую, точный DTM)",
    "prm_play"    => "партий на сценарий — главный тест",
    "prm_check"   => "партий — явная проверка исхода",
    "prm_maxplies"=> "лимит длины партии (полуходы)",
    "prm_mu"      => "кинетический вес mu (T05)",
    "prm_lam"     => "вес давления K3 lambda",
    "prm_seed"    => "детерминированное зерно",
    "prm_dpi"     => "разрешение графиков DPI (PNG)",
    "prm_fig"     => "размер рисунка в дюймах ШxВ",
    "prm_scaling" => "список досок бенчмарка масштабирования",
    "prm_traps"   => "объём выборки переписи ловушек",
    "prm_krk"     => "сценарий KRK включён (on/off)",
    "prm_kqk"     => "сценарий KQK включён (on/off)",
    "prm_expect"  => "ожидаемый исход для T8 (draw/white/black/none)",
    "prm_policies" => "ансамбль политик T7 (список через запятую или all)",
    "sel_pol"     => "политики (список через запятую или all): ",
    "prm_flowr"   => "ладей на сторону в витрине потока",
    "prm_outdir"  => "каталог отчётов",
    "prm_lang"    => "язык (ru/en)",
    "c_yes"       => "да", "c_no" => "нет", "c_on" => "вкл", "c_off" => "выкл",
    "c_back"      => "назад",
    "cells"       => "клеток",
    "t1_title"    => "T1 · ПЕРЕПИСЬ ДОСКИ — замкнутые формы против графа ходов",
    "t1_rook"     => "рёбра графа ладьи",  "t1_bishop" => "рёбра графа слона",
    "t1_knight"   => "рёбра графа коня",   "t1_king"   => "рёбра графа короля",
    "t1_queen"    => "тождество ферзь = ладья + слон",
    "t1_note"     => "все счёты направленные; замкнутые формы сверяются с генератором",
    "t2_title"    => "T2 · БАТАРЕЯ ЛЕГАЛЬНОСТИ — инварианты случайных партий",
    "t3_title"    => "T3 · САМОПРОВЕРКА ОРАКУЛА — ретроградный DTM, K+фигура против K",
    "t4_title"    => "T4 · ПЕРЕПИСЬ ЛОВУШЕК — частичный солвер против точного оракула",
    "t5_title"    => "T5 · БЕНЧМАРК МАСШТАБИРОВАНИЯ — полиномиальный выбор хода (T14)",
    "t7_title"    => "T7 · ГЛАВНЫЙ ТЕСТ — ВЕРДИКТ ЧАСТИЧНОЙ ПОЛИТИКИ: КАКОЙ ИСХОД ПРЕДПОЛАГАЕТ ДИНАМИКА?",
    "t8_title"    => "T8 · ЯВНАЯ ПРОВЕРКА ИСХОДА",
    "t9_title"    => "T9 · ВИТРИНА ПОТОКА — поле K3 и траектории частиц",
    "or_states"   => "состояний", "or_edges" => "рёбер", "or_won" => "выигранных",
    "or_mates"    => "матов",  "or_max"   => "макс. DTM (ходов)", "or_time" => "время",
    "t3_struct"   => "структурная самосогласованность (цепь выигрышных ходов)",
    "t3_mono"     => "макс. DTM растёт с n",
    "t3_ok"       => "инварианты оракула выполнены",
    "t4_won"      => "выигранных позиций (ход белых)",
    "t4_correct"  => "выигрыш сохранён (DTM - 1)",
    "t4_slow"     => "выигрыш сохранён, медленнее",
    "t4_blund"    => "зевок: выигрыш -> ничья",
    "t4_drawn"    => "ничейных позиций (ход белых)",
    "t4_lost"     => "проигранных позиций (ход чёрных, тест сопротивления)",
    "t4_trapfall" => "поймался в ловушку: ничья -> проигрыш",
    "t4_trate"    => "частота зевков частиц",
    "t5_move"     => "среднее время на ход",
    "t5_ply"      => "среднее время на полуход (полная партия)",
    "t5_slope"    => "наклон в log-log (последние две доски)",
    "t5_nodes"    => "кандидатов оценивается на выбор хода",
    "main_scen"   => "сценарии",
    "main_runs"   => "партий на сценарий",
    "plies_hdr"   => "полуходы",
    "out_draw"    => "НИЧЬЯ", "out_white" => "ПОБЕДА БЕЛЫХ", "out_black" => "ПОБЕДА ЧЁРНЫХ",
    "r_rep"       => "повторение позиции", "r_stale" => "пат", "r_bare" => "материал взят",
    "r_cap"       => "достигнут лимит полуходов", "r_mate" => "мат",
    "v_draw"      => "ОБОЮДНАЯ ФОРС-НИЧЬЯ",
    "v_white"     => "ФОРС-ПОБЕДА БЕЛЫХ",
    "v_black"     => "ФОРС-ПОБЕДА ЧЁРНЫХ",
    "v_inconc"    => "НЕОПРЕДЕЛЁННО — увеличьте число партий",
    "v_honest"    => "Это вердикт ЧАСТИЧНОЙ ПОЛИТИКИ: ансамбль аппроксиматоров (именованных политик) на выборочных стартах, а не теоретико-игровое доказательство. См. complexity/SOLVING_CHESS.md: истинное решение требует уровней, определённых там.",
    "v_honest_one" => "Это вердикт ЧАСТИЧНОЙ ПОЛИТИКИ (аппроксиматор частиц на выборочных стартах), а не теоретико-игровое доказательство. См. complexity/SOLVING_CHESS.md: истинное решение требует уровней, определённых там.",
    "v_ladder"    => "Лестница доказательности: ПОЛНОЕ РЕШЕНИЕ > СЛАБОЕ > УЛЬТРАСЛАБОЕ > ЧАСТИЧНАЯ ПОЛИТИКА — уровень этого прогона: ЧАСТИЧНАЯ ПОЛИТИКА.",
    "pol_ens"     => "ансамбль политик",
    "policy"      => "политика",
    "pool"        => "пул",
    "consensus"   => "консенсус",
    "cons_unan"   => "ЕДИНОГЛАСНЫЙ",
    "cons_major"  => "БОЛЬШИНСТВО",
    "cons_split"  => "РАСКОЛ",
    "tier_legend" => "уровень вердикта политики: F = форс (нижняя граница ДИ > 50%) · L = склоняется (доля >= 75%) · I = неопределён",
    "cov_starts"  => "уникальных стартовых позиций",
    "cov_plies"   => "сыграно полуходов всего",
    "cov_states"  => "оценка пространства состояний сценария",
    "cov_share"   => "выборочное покрытие",
    "main_stat"   => "распределение исходов",
    "main_plies"  => "средняя длина партии (полуходы)",
    "t8_expect"   => "ожидаемый исход",
    "t8_agree"    => "СОГЛАСИЕ — динамика подтверждает ожидаемый исход",
    "t8_weak"     => "СЛАБОЕ СОГЛАСИЕ — исход преобладает, но доверительный интервал широк",
    "t8_dis"      => "ПРОТИВОРЕЧИЕ — динамика опровергает ожидаемый исход",
    "c1_title"    => "Выбор хода частицами полиномиален по n  ·  T14",
    "c1_xlabel"   => "сторона доски n (лог. шкала)",
    "c1_ylabel"   => "секунды на ход (лог. шкала)",
    "c1_meas"     => "измерено (K+ладья против K)",
    "c1_ref2"     => "репер O(n^2)",
    "c1_ref4"     => "репер O(n^4) (наивная пересчёт поля)",
    "c2_title"    => "Распределение исходов частичных партий",
    "c2_ylabel"   => "доля партий",
    "c3_title"    => "Поле угроз K3 на доске {N}x{N} — поток частиц",
    "c3_bar"      => "давление атаки",
    "c4_title"    => "Точный оракул: самый долгий мат растёт полиномиально  ·  T14(ii)",
    "c4_xlabel"   => "сторона доски n",
    "c4_ylabel"   => "макс. DTM (ходов)",
    "c4_fit"      => "степенная аппроксимация a*n^b",
    "c4_states"   => "состояний",
    "rep_dir"     => "каталог прогона",
    "rep_files"   => "отчёты записаны",
    "progress_note" => "детерминированные партии с фиксированным зерном",
    "eta"         => "осталось",
    "elapsed"     => "прошло",
    "sel_exp"     => "ожидаемый исход: [d] ничья / [w] белые / [b] чёрные / [n] нет ?",
    "run_hdr"     => "ПАРАМЕТРЫ ПРОГОНА",
    "lang_set"    => "язык переключён на русский",
    "threads"     => "потоков-исполнителей",
    "quick_on"    => "активен БЫСТРЫЙ профиль (проверочный прогон)",
    "selftest"    => "САМОПРОВЕРКА",
    "st_png"      => "кодер PNG, круговая проверка",
    "st_engine"   => "инварианты движка n x n",
    "st_solver"   => "легальность частичного солвера",
    "st_all"      => "САМОПРОВЕРКА ПРОЙДЕНА",
    "verdict"     => "ВЕРДИКТ",
    "board"       => "доска",
    "scenario"    => "сценарий",
    "plays"       => "партий",
    "share"       => "доля",
    "ci95"        => "95% ДИ",
    "summary"     => "ИТОГ",
    "st_title"    => "быстрая батарея T1-T5 + T7-T9",
)

t(key::String) = get(STR[CFG.lang], key, get(STR[:en], key, key))

# ──────────────────────────────────────────────────────────────────────────────
# ENGINE — generalized n x n board (pawnless piece set {N,B,R,Q,K})
#   squares are 0-based: sq = r*n + c,  r = sq ÷ n,  c = sq % n
# ──────────────────────────────────────────────────────────────────────────────

const PIECE_N = Int8(2); const PIECE_B = Int8(3); const PIECE_R = Int8(4)
const PIECE_Q = Int8(5); const PIECE_K = Int8(6)
const PVAL = Int[0, 1, 3, 3, 5, 9, 0]          # index = abs(piece code)

# 8 directions: 1-4 orthogonal, 5-8 diagonal
const DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

struct Geo
    n::Int
    king_nb::Vector{Vector{Int}}      # sq+1 -> on-board king neighbours
    knight_nb::Vector{Vector{Int}}    # sq+1 -> on-board knight jumps
    rays::Vector{Vector{Vector{Int}}} # [dir][sq+1] -> squares along the ray
end

const GEO_CACHE = Dict{Int,Geo}()
const ZOB_SEED = 0x63683353535f5a42   # 'c','h','3','S','S','_','Z','B' — fixed family seed

function geo(n::Int)
    haskey(GEO_CACHE, n) && return GEO_CACHE[n]
    N2 = n * n
    king = Vector{Vector{Int}}(undef, N2)
    knig = Vector{Vector{Int}}(undef, N2)
    rays = [Vector{Vector{Int}}(undef, N2) for _ in 1:8]
    KJ = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
    for r in 0:n-1, c in 0:n-1
        sq = r * n + c
        kn = Int[]; nj = Int[]
        for (dr, dc) in DIRS
            rr, cc = r + dr, c + dc
            (0 <= rr < n && 0 <= cc < n) && push!(kn, rr * n + cc)
        end
        for (dr, dc) in KJ
            rr, cc = r + dr, c + dc
            (0 <= rr < n && 0 <= cc < n) && push!(nj, rr * n + cc)
        end
        king[sq+1] = kn; knig[sq+1] = nj
        for d in 1:8
            dr, dc = DIRS[d]
            ray = Int[]
            rr, cc = r + dr, c + dc
            while 0 <= rr < n && 0 <= cc < n
                push!(ray, rr * n + cc)
                rr += dr; cc += dc
            end
            rays[d][sq+1] = ray
        end
    end
    g = Geo(n, king, knig, rays)
    GEO_CACHE[n] = g
    return g
end

mutable struct Pos
    n::Int
    b::Vector{Int8}          # n*n cells
    side::Int                # +1 white, -1 black
    kw::Int                  # white king square (0-based)
    kb::Int                  # black king square
    key::UInt64              # incremental Zobrist key
end

const ZCACHE = Dict{Int,Tuple{Matrix{UInt64},UInt64}}()

function zobrist(n::Int)
    haskey(ZCACHE, n) && return ZCACHE[n]
    g = SM64(ZOB_SEED)
    Z = Matrix{UInt64}(undef, 10, n * n)     # 5 white codes 2..6, 5 black
    for pi in 1:10, sq in 1:(n * n)
        Z[pi, sq] = next!(g)
    end
    side = next!(g)
    ZCACHE[n] = (Z, side)
    return ZCACHE[n]
end

zindex(p::Int8) = p > 0 ? Int(p) - 1 : 4 - Int(p)     # p=2..6 -> 1..5 ; p=-2..-6 -> 6..10

function Pos(n::Int)
    Pos(n, zeros(Int8, n * n), 1, -1, -1, UInt64(0))
end

function put!(P::Pos, sq::Int, p::Int8)
    Z, _ = zobrist(P.n)
    old = P.b[sq+1]
    if old != 0
        P.key ⊻= Z[zindex(old), sq+1]
    end
    if p != 0
        P.key ⊻= Z[zindex(p), sq+1]
        if p == PIECE_K;  P.kw = sq; end
        if p == -PIECE_K; P.kb = sq; end
    end
    P.b[sq+1] = p
    return P
end

function flip_side!(P::Pos)
    _, sk = zobrist(P.n)
    P.key ⊻= sk
    P.side = -P.side
    return P
end

kingsq(P::Pos, side::Int) = side > 0 ? P.kw : P.kb

cheb(P::Pos, a::Int, b::Int) =
    max(abs((a ÷ P.n) - (b ÷ P.n)), abs((a % P.n) - (b % P.n)))

is_own(P::Pos, sq::Int, side::Int) =
    (side > 0) ? P.b[sq+1] > 0 : P.b[sq+1] < 0

# ── attack detection: is square `sq` attacked by side `by`? ──────────────────
function attacked_by(P::Pos, sq::Int, by::Int)::Bool
    g = geo(P.n)
    B = P.b
    code = Int8(by * PIECE_N)
    for t in g.knight_nb[sq+1]
        B[t+1] == code && return true
    end
    code = Int8(by * PIECE_K)
    for t in g.king_nb[sq+1]
        B[t+1] == code && return true
    end
    r4 = Int8(by * PIECE_R); q5 = Int8(by * PIECE_Q); b3 = Int8(by * PIECE_B)
    for d in 1:4                       # orthogonal sliders
        for t in g.rays[d][sq+1]
            p = B[t+1]
            p == 0 && continue
            (p == r4 || p == q5) && return true
            break
        end
    end
    for d in 5:8                       # diagonal sliders
        for t in g.rays[d][sq+1]
            p = B[t+1]
            p == 0 && continue
            (p == b3 || p == q5) && return true
            break
        end
    end
    return false
end

in_check(P::Pos, side::Int) = attacked_by(P, kingsq(P, side), -side)

# ── pseudo-move generation (no castling, no pawns — documented scope) ────────
function gen_pseudo!(P::Pos, out::Vector{Int})
    empty!(out)
    g = geo(P.n)
    B = P.b; n = P.n; s = P.side
    for sq in 0:(n * n - 1)
        p = B[sq+1]
        (p == 0 || (p > 0) != (s > 0)) && continue
        ap = abs(p)
        if ap == 6                                   # king
            for t in g.king_nb[sq+1]
                is_own(P, t, s) || push!(out, sq | (t << 14))
            end
        elseif ap == 2                               # knight
            for t in g.knight_nb[sq+1]
                is_own(P, t, s) || push!(out, sq | (t << 14))
            end
        else                                         # slider B/R/Q
            dset = ap == 3 ? (5:8) : ap == 4 ? (1:4) : (1:8)
            for d in dset
                for t in g.rays[d][sq+1]
                    q = B[t+1]
                    if q == 0
                        push!(out, sq | (t << 14))
                    else
                        ((q > 0) != (s > 0)) && push!(out, sq | (t << 14))
                        break
                    end
                end
            end
        end
    end
    return out
end

mfrom(m::Int) = m & 0x3FFF
mto(m::Int)   = m >> 14

function make!(P::Pos, m::Int)
    f, t = mfrom(m), mto(m)
    p = P.b[f+1]
    cap = P.b[t+1]
    put!(P, t, p)
    put!(P, f, Int8(0))
    flip_side!(P)
    return (p, cap)
end

function unmake!(P::Pos, m::Int, undo::Tuple{Int8,Int8})
    p, cap = undo
    f, t = mfrom(m), mto(m)
    flip_side!(P)
    put!(P, f, p)
    put!(P, t, cap)
    return P
end

function legal_moves(P::Pos)
    buf = Int[]
    gen_pseudo!(P, buf)
    out = Int[]
    s = P.side
    for m in buf
        u = make!(P, m)
        ok = !in_check(P, s)
        unmake!(P, m, u)
        ok && push!(out, m)
    end
    return out
end

# ── kinetic proxy: pseudo-mobility count (blocking honored, checks ignored) ──
function pseudo_mobility(P::Pos, side::Int)
    g = geo(P.n); B = P.b
    total = 0
    for sq in 0:(P.n * P.n - 1)
        p = B[sq+1]
        (p == 0 || (p > 0) != (side > 0)) && continue
        ap = abs(p)
        if ap == 6
            for t in g.king_nb[sq+1]
                is_own(P, t, side) || (total += 1)
            end
        elseif ap == 2
            total += length(g.knight_nb[sq+1])
        else
            dset = ap == 3 ? (5:8) : ap == 4 ? (1:4) : (1:8)
            for d in dset
                for t in g.rays[d][sq+1]
                    q = B[t+1]
                    if q == 0
                        total += 1
                    else
                        ((q > 0) != (side > 0)) && (total += 1)
                        break
                    end
                end
            end
        end
    end
    return total
end

function material_of(P::Pos, side::Int)
    s = 0
    for sq in 0:(P.n * P.n - 1)
        p = P.b[sq+1]
        p == 0 && continue
        ((p > 0) == (side > 0)) && (s += PVAL[abs(Int(p))])
    end
    return s
end

# ── Layer K3: threat field. Theta[c] = number of `side` pieces pressuring c ──
#    Sliders walk their ray until the first occupied square INCLUSIVE (attack
#    or defense pressure — the K3 field of Theorem T04, generalized to n x n).
function threat_field(P::Pos, side::Int)
    g = geo(P.n); B = P.b
    theta = zeros(Int32, P.n * P.n)
    for sq in 0:(P.n * P.n - 1)
        p = B[sq+1]
        (p == 0 || (p > 0) != (side > 0)) && continue
        ap = abs(p)
        if ap == 6
            for t in g.king_nb[sq+1]; theta[t+1] += 1; end
        elseif ap == 2
            for t in g.knight_nb[sq+1]; theta[t+1] += 1; end
        else
            dset = ap == 3 ? (5:8) : ap == 4 ? (1:4) : (1:8)
            for d in dset
                for t in g.rays[d][sq+1]
                    theta[t+1] += 1
                    B[t+1] != 0 && break
                end
            end
        end
    end
    return theta
end

# inverse probe: how many `by` pieces attack the single cell c
function attacks_on(P::Pos, c::Int, by::Int)
    g = geo(P.n); B = P.b
    cnt = 0
    code = Int8(by * PIECE_N)
    for t in g.knight_nb[c+1]; B[t+1] == code && (cnt += 1); end
    code = Int8(by * PIECE_K)
    for t in g.king_nb[c+1];  B[t+1] == code && (cnt += 1); end
    r4 = Int8(by * PIECE_R); q5 = Int8(by * PIECE_Q); b3 = Int8(by * PIECE_B)
    for d in 1:4
        for t in g.rays[d][c+1]
            p = B[t+1]
            p == 0 && continue
            (p == r4 || p == q5) && (cnt += 1)
            break
        end
    end
    for d in 5:8
        for t in g.rays[d][c+1]
            p = B[t+1]
            p == 0 && continue
            (p == b3 || p == q5) && (cnt += 1)
            break
        end
    end
    return cnt
end

# ──────────────────────────────────────────────────────────────────────────────
# PARTICLE SOLVER — three-layer greedy chooser (K3 + TORUS; KLEIN determinism)
#
#   score(m) = [material(s) - material(-s)]                    (potential)
#            + mu * [mobility(s) - mobility(-s)]               (kinetic, T05)
#            + lam * mean_{c ~ K(-s)} attacks_by(s, c)         (K3 pressure)
#
#   The pressure term is evaluated by the local inverse probe on the enemy
#   king ring (ek + its king-neighbourhood) — numerically identical to the
#   full K3 field restricted to those cells, at a fraction of the cost.
#   Tie-break: lexicographically smallest (from, to) — KLEIN determinism.
#   Cost per move: O(#candidates x n) = O(n^2) on n x n with k particles.
# ──────────────────────────────────────────────────────────────────────────────

struct Solver
    mu::Float64
    lam::Float64
end

score_after(P::Pos, S::Solver, m::Int) = begin
    s = P.side
    u = make!(P, m)
    mat = material_of(P, s) - material_of(P, -s)
    mob = pseudo_mobility(P, s) - pseudo_mobility(P, -s)
    ek = kingsq(P, -s)
    g = geo(P.n)
    press = 0.0
    for c in (ek, g.king_nb[ek+1]...)
        press += attacks_on(P, c, s)
    end
    press /= length(g.king_nb[ek+1]) + 1
    unmake!(P, m, u)
    Float64(mat) + S.mu * Float64(mob) + S.lam * press
end

function choose_move(P::Pos, S::Solver, counter::Union{Nothing,Vector{Int}} = nothing)
    moves = legal_moves(P)
    isempty(moves) && return -1
    counter !== nothing && (counter[1] += length(moves))
    best = -1; bsc = -Inf; bf = typemax(Int); bt = typemax(Int)
    for m in moves
        sc = score_after(P, S, m)
        f, t = mfrom(m), mto(m)
        if (sc > bsc) || (sc == bsc && (f < bf || (f == bf && t < bt)))
            best = m; bsc = sc; bf = f; bt = t
        end
    end
    return best
end

# ──────────────────────────────────────────────────────────────────────────────
# POLICY ENSEMBLE — named move-selection policies for the MAIN test T7.
#
#   Each policy is a complete mapping positions -> move (an "approximator"
#   in the language of complexity/SOLVING_CHESS.md).  T7 lets every enabled
#   policy play BOTH sides of paired playouts — identical sampled starts for
#   every policy (same position seed) — and merges the outcome statistics
#   into one PARTIAL POLICY VERDICT.  No single policy is trusted alone:
#   the verdict reports per-policy shares, a consensus class, and the
#   honest evidence level (partial policy, not a solution).
# ──────────────────────────────────────────────────────────────────────────────

struct PolicySpec
    name::Symbol
    mu::Float64
    lam::Float64
end

const POLICY_LABEL = Dict{Symbol,String}(:particle => "PARTICLE",
                                         :mobility => "MOBILITY",
                                         :pressure => "PRESSURE",
                                         :material => "MATERIAL",
                                         :random   => "RANDOM")

build_policy(name::Symbol, mu::Float64, lam::Float64) =
    name === :particle ? PolicySpec(:particle, mu, lam) :
    name === :mobility ? PolicySpec(:mobility, 1.0, 0.0) :
    name === :pressure ? PolicySpec(:pressure, 0.0, 1.0) :
    name === :material ? PolicySpec(:material, 0.0, 0.0) :
    name === :random   ? PolicySpec(:random, 0.0, 0.0) :
                         PolicySpec(:particle, mu, lam)

# policy move choice; RANDOM needs the playout rng, the rest are deterministic
function choose_move(P::Pos, ps::PolicySpec, g::Union{Nothing,SM64})
    moves = legal_moves(P)
    isempty(moves) && return -1
    if ps.name === :random
        g === nothing && error("RANDOM policy requires a playout rng")
        return moves[randint!(g, 1, length(moves))]
    end
    return choose_move(P, Solver(ps.mu, ps.lam))
end

# policy playout — same termination semantics as the solver playout above
function playout!(P::Pos, ps::PolicySpec, g::Union{Nothing,SM64}; max_plies::Int = 512)
    seen = Set{UInt64}([P.key])
    plies = 0
    while plies < max_plies
        moves = legal_moves(P)
        if isempty(moves)
            if in_check(P, P.side)
                winner = -P.side
                return plies, (winner > 0 ? :white : :black), "r_mate"
            end
            return plies, :draw, "r_stale"
        end
        has_decisive_piece(P) || return plies, :draw, "r_bare"
        m = choose_move(P, ps, g)
        m < 0 && return plies, :draw, "r_stale"
        make!(P, m)
        plies += 1
        if P.key in seen
            return plies, :draw, "r_rep"
        end
        push!(seen, P.key)
    end
    return plies, :draw, "r_cap"
end

# ── endgame material probe: any decisive piece left? ─────────────────────────
function has_decisive_piece(P::Pos)
    for sq in 0:(P.n * P.n - 1)
        p = abs(Int(P.b[sq+1]))
        (p in (2, 3, 4, 5)) && return true
    end
    return false
end

# ── one deterministic particle-vs-particle playout ───────────────────────────
#   returns (plies, outcome, reason) with outcome ∈ :white :black :draw
function playout!(P::Pos, S::Solver; max_plies::Int = 512)
    seen = Set{UInt64}([P.key])
    plies = 0
    while plies < max_plies
        moves = legal_moves(P)
        if isempty(moves)
            if in_check(P, P.side)
                winner = -P.side
                return plies, (winner > 0 ? :white : :black), "r_mate"
            end
            return plies, :draw, "r_stale"
        end
        has_decisive_piece(P) || return plies, :draw, "r_bare"
        m = choose_move(P, S)
        m < 0 && return plies, :draw, "r_stale"
        make!(P, m)
        plies += 1
        if P.key in seen
            return plies, :draw, "r_rep"
        end
        push!(seen, P.key)
    end
    return plies, :draw, "r_cap"
end

# ── random legal start positions (deterministic per seed) ────────────────────
function set_side!(P::Pos, s::Int)
    while P.side != s
        flip_side!(P)
    end
    return P
end

function setup_kxk!(P::Pos, g::SM64, piece::Int8, white_to_move::Bool)
    n = P.n
    while true
        fill!(P.b, Int8(0)); P.kw = -1; P.kb = -1; P.key = UInt64(0); P.side = 1
        wk = randint!(g, 0, n * n - 1)
        bk = randint!(g, 0, n * n - 1)
        ps = randint!(g, 0, n * n - 1)
        (wk == bk || wk == ps || bk == ps) && continue
        max(abs((wk ÷ n) - (bk ÷ n)), abs((wk % n) - (bk % n))) <= 1 && continue
        put!(P, wk, PIECE_K)
        put!(P, bk, -PIECE_K)
        put!(P, ps, piece)
        set_side!(P, white_to_move ? 1 : -1)
        # side NOT to move must not be en prise
        white_to_move && attacked_by(P, P.kb, 1) && continue
        return P
    end
end

function fresh_endgame(n::Int, piece::Int8, white_to_move::Bool, g::SM64)
    P = Pos(n)
    setup_kxk!(P, g, piece, white_to_move)
    isempty(legal_moves(P)) && return fresh_endgame(n, piece, white_to_move, g)
    return P
end

# ── rook-storm showcase position for the flow visualization ──────────────────
function fresh_battle(n::Int, rooks_per_side::Int, g::SM64)
    P = Pos(n)
    while true
        fill!(P.b, Int8(0)); P.kw = -1; P.kb = -1; P.key = UInt64(0); P.side = 1
        wk = randint!(g, 0, n ÷ 2 - 1) * n + randint!(g, 0, n ÷ 2 - 1)
        bk = (n - 1 - randint!(g, 0, n ÷ 2 - 1)) * n +
             (n - 1 - randint!(g, 0, n ÷ 2 - 1))
        max(abs((wk ÷ n) - (bk ÷ n)), abs((wk % n) - (bk % n))) <= n ÷ 3 && continue
        put!(P, wk, PIECE_K); put!(P, bk, -PIECE_K)
        used = Set{Int}([wk, bk])
        sqs = Int[]
        while length(sqs) < 2 * rooks_per_side
            sq = randint!(g, 0, n * n - 1)
            sq in used && continue
            push!(used, sq); push!(sqs, sq)
        end
        for (i, sq) in enumerate(sqs)
            side = i <= rooks_per_side ? 1 : -1
            put!(P, sq, Int8(side * PIECE_R))
        end
        set_side!(P, 1)
        attacked_by(P, P.kb, 1) && continue     # black king en prise: resample
        isempty(legal_moves(P)) && continue
        return P
    end
end

# column file letters only: a..z, aa, ab, ... (for heatmap axis labels)
function fileletter(c::Int)
    s = ""
    x = c
    while true
        s = string('a' + (x % 26)) * s
        x = x ÷ 26 - 1
        x < 0 && break
    end
    return s
end

# square name for logs: file letter (bijective beyond z) + rank number
function sqname(n::Int, sq::Int)
    r, c = sq ÷ n, sq % n
    file = ""
    x = c
    while true
        file = string('a' + (x % 26)) * file
        x = x ÷ 26 - 1
        x < 0 && break
    end
    return @sprintf("%s%d", file, r + 1)
end
mname(n::Int, m::Int) = sqname(n, mfrom(m)) * "-" * sqname(n, mto(m))

# ──────────────────────────────────────────────────────────────────────────────
# RETROGRADE ORACLE — exact DTM for K+R / K+Q vs K on n x n boards.
#   Bellman layered propagation over the packed state space (the generalized
#   dynamics.retro_dtm / complexity.retro_dtm_nxn algorithm).  For a FIXED
#   number of pieces k = 3 the state space is O(n^6) and polynomial in n —
#   the exponential wall lives in k, not in n (Theorem T14(ii)).
#   dtm[s] = -1 : illegal / unreachable / game-theoretically drawn
#   dtm[s] =  0 : checkmate (the mated side is to move)
#   dtm[s] =  d : White mates in d plies against any defence
# ──────────────────────────────────────────────────────────────────────────────

struct Oracle
    n::Int
    bits::Int
    piece::Int8              # PIECE_R or PIECE_Q
    dtm::Vector{Int32}
    stats::Dict{String,Int}
end

obits(n::Int) = (w = n * n; b = 1; while (1 << b) < w; b += 1; end; b)
opack(bits::Int, wk::Int, wq::Int, bk::Int, stm::Int) =
    wk | (wq << bits) | (bk << (2 * bits)) | (stm << (3 * bits))
ounpack(bits::Int, s::Int) =
    (s & ((1 << bits) - 1), (s >> bits) & ((1 << bits) - 1),
     (s >> (2 * bits)) & ((1 << bits) - 1), (s >> (3 * bits)) & 1)

function king_steps(n::Int, sq::Int)
    out = Int[]
    r, c = sq ÷ n, sq % n
    for (dr, dc) in DIRS
        rr, cc = r + dr, c + dc
        (0 <= rr < n && 0 <= cc < n) && push!(out, rr * n + cc)
    end
    return out
end

# sliding attacks of the strong piece on the scratch board (blocking honored;
# the walk stops at the first occupied square INCLUSIVE)
function strong_attacks!(b::Vector{Int8}, n::Int, from::Int, piece::Int8, out::Vector{Int})
    empty!(out)
    dset = piece == PIECE_B ? (5:8) : piece == PIECE_R ? (1:4) : (1:8)
    r, c = from ÷ n, from % n
    for d in dset
        dr, dc = DIRS[d]
        rr, cc = r + dr, c + dc
        while 0 <= rr < n && 0 <= cc < n
            sq = rr * n + cc
            push!(out, sq)
            b[sq+1] != 0 && break
            rr += dr; cc += dc
        end
    end
    return out
end

function retro_oracle(n::Int, piece::Int8; log::Function = (s -> nothing))
    n <= 13 || error("oracle supports n <= 13 (memory/state-space guard)")
    bits = obits(n)
    SIZE = 1 << (3 * bits + 1)
    dtm = fill(Int32(-1), SIZE)
    ptr = fill(Int32(0), SIZE)
    cnt = fill(Int32(0), SIZE)
    escape = fill(UInt8(0), SIZE)
    succ_flat = Int32[]
    sizehint!(succ_flat, 1 << 20)
    NSQ = n * n
    kn = [king_steps(n, sq) for sq in 0:(NSQ - 1)]
    kadj = [Set(king_steps(n, sq)) for sq in 0:(NSQ - 1)]
    b = zeros(Int8, NSQ)
    att = Int[]
    n_states = 0
    n_mates = 0
    code = piece

    # ── pass 1: enumerate states, build the flat successor list ──────────────
    for wk in 0:(NSQ - 1), wq in 0:(NSQ - 1)
        wq == wk && continue
        for bk in 0:(NSQ - 1)
            (bk == wk || bk == wq || bk in kadj[wk+1]) && continue
            fill!(b, Int8(0))
            b[wk+1] = PIECE_K; b[wq+1] = code; b[bk+1] = Int8(-PIECE_K)
            targets = strong_attacks!(b, n, wq, code, att)
            bk_t = bk in targets          # snapshot BEFORE att is reused below

            # white to move: legal only if the black king is not en prise
            if !bk_t
                s0 = opack(bits, wk, wq, bk, 0)
                c0 = 0
                for dest in kn[wk+1]                 # white king steps
                    (dest == wq || dest == bk || dest in kadj[bk+1]) && continue
                    push!(succ_flat, Int32(opack(bits, dest, wq, bk, 1)))
                    c0 += 1
                end
                for dest in targets                  # strong piece steps
                    (dest == wk || dest == bk) && continue
                    push!(succ_flat, Int32(opack(bits, wk, dest, bk, 1)))
                    c0 += 1
                end
                ptr[s0+1] = length(succ_flat) - c0 + 1
                cnt[s0+1] = c0
                n_states += 1
            end

            # black to move (always enumerated; captures recorded as escapes)
            s1 = opack(bits, wk, wq, bk, 1)
            c1 = 0
            captured = false
            for dest in kn[bk+1]
                dest == wk && continue
                dest in kadj[wk+1] && continue       # adjacent to White king
                if dest == wq
                    captured = true                  # undefended capture: draw
                    continue
                end
                b[bk+1] = Int8(0); b[dest+1] = Int8(-PIECE_K)
                hit = dest in strong_attacks!(b, n, wq, code, att)
                b[dest+1] = Int8(0); b[bk+1] = Int8(-PIECE_K)
                hit && continue                      # moving into check
                push!(succ_flat, Int32(opack(bits, wk, wq, dest, 0)))
                c1 += 1
            end
            ptr[s1+1] = length(succ_flat) - c1 + 1
            cnt[s1+1] = c1
            escape[s1+1] = captured ? UInt8(1) : UInt8(0)
            if c1 == 0 && !captured && bk_t
                dtm[s1+1] = Int32(0)                 # checkmate
                n_mates += 1
            end
            n_states += 1
        end
    end
    total_edges = length(succ_flat)
    log(@sprintf("   n=%2d %s: %d states, %d edges", n,
                 piece == PIECE_R ? "KRK" : "KQK", n_states, total_edges))

    # ── predecessor CSR (count + fill) ───────────────────────────────────────
    pred_cnt = fill(Int32(0), SIZE)
    for s in 0:(SIZE - 1)
        p0 = ptr[s+1]
        for k in p0:(p0 + cnt[s+1] - 1)
            pred_cnt[succ_flat[k]+1] += Int32(1)
        end
    end
    pred_ptr = fill(Int32(0), SIZE + 1)
    acc = Int32(0)
    for s in 1:SIZE
        pred_ptr[s] = acc + Int32(1)          # 1-based inclusive start
        acc += pred_cnt[s]
    end
    pred_ptr[SIZE+1] = acc + Int32(1)          # 1-based exclusive end
    pred_arr = Vector{Int32}(undef, acc)
    fill_pos = pred_ptr[1:SIZE]
    for s in 0:(SIZE - 1)
        p0 = ptr[s+1]
        for k in p0:(p0 + cnt[s+1] - 1)
            c = succ_flat[k]
            idx = fill_pos[c+1]
            pred_arr[idx] = Int32(s)
            fill_pos[c+1] = idx + Int32(1)
        end
    end

    # ── pass 2: layered retrograde propagation (Bellman induction) ───────────
    frontier = Int32[s - 1 for s in 1:SIZE if dtm[s] == Int32(0)]
    depth = 0
    max_plies = 0
    while !isempty(frontier)
        depth += 1
        nxt = Int32[]
        for node in frontier
            lo = pred_ptr[node+1]
            hi = pred_ptr[node+2] - Int32(1)
            for k in lo:hi
                parent = pred_arr[k]
                dtm[parent+1] >= 0 && continue
                if (parent >> (3 * bits)) == 0
                    # White to move: one move reaches the frontier node
                    dtm[parent+1] = Int32(depth)
                    depth > max_plies && (max_plies = depth)
                    push!(nxt, parent)
                else
                    # Black to move: ALL moves must be lost (and no recapture)
                    escape[parent+1] == 1 && continue
                    p0 = ptr[parent+1]
                    all_won = true
                    mx = Int32(0)
                    for k2 in p0:(p0 + cnt[parent+1] - 1)
                        dv = dtm[succ_flat[k2]+1]
                        if dv < 0
                            all_won = false
                            break
                        end
                        dv > mx && (mx = dv)
                    end
                    if all_won
                        d = mx + Int32(1)
                        dtm[parent+1] = d
                        d > max_plies && (max_plies = d)
                        push!(nxt, parent)
                    end
                end
            end
        end
        frontier = nxt
    end

    won = 0
    for s in 1:SIZE
        dtm[s] >= 0 && (won += 1)
    end
    stats = Dict{String,Int}(
        "n" => n, "piece" => piece == PIECE_R ? 82 : 81,
        "states" => n_states, "edges" => total_edges,
        "won" => won, "mates" => n_mates,
        "max_plies" => max_plies, "max_moves" => (max_plies + 1) ÷ 2)
    return Oracle(n, bits, code, dtm, stats)
end

# DTM of a KXK position (Pos), or -2 if the position left the K+piece vs K space
function oracle_query(o::Oracle, P::Pos)
    wk = -1; wq = -1; bk = -1
    for sq in 0:(P.n * P.n - 1)
        p = P.b[sq+1]
        p == 0 && continue
        if p == PIECE_K; wk == -1 || return -2; wk = sq
        elseif p == -PIECE_K; bk == -1 || return -2; bk = sq
        elseif p == o.piece; wq == -1 || return -2; wq = sq
        else return -2
        end
    end
    (wk >= 0 && wq >= 0 && bk >= 0) || return -2
    return Int(o.dtm[opack(o.bits, wk, wq, bk, P.side < 0 ? 1 : 0) + 1])
end

# ──────────────────────────────────────────────────────────────────────────────
# EMBEDDED BITMAP FONT (32x32 cells, 175 glyphs: printable ASCII + Cyrillic +
# scientific extras).  Rows are hex-encoded, 32 bits per row, MSB = leftmost
# pixel.  Glyphs were rasterized from DejaVu Sans / DejaVu Sans Bold
# (Bitstream Vera license) by scripts/gen_font.py — the only non-Base asset
# in this file.
# ──────────────────────────────────────────────────────────────────────────────
const FONT_HEX_REGULAR = """
U+0020 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
U+0021 00000000000000000000000000000000000000000003c0000003c0000003c0000003c0000003c0000003c0000003c0000003c0000003c0000003c0000003c0000001c0000001800000018000000180000000000000000000000000000003c0000003c0000003c0000003c0000000000000000000000000000000000000000000
U+0022 0000000000000000000000000000000000000000000c7000000c7000000c7000000c7000000c7000000c7000000c7000000c700000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
U+0023 000000000000000000000000000000000000000000030e0000070e0000070c0000061c0000061c00000e180001ffffc001ffffc001ffffc0001c3800001c3000001870000018700007ffff0007ffff0007ffff000030e0000070e0000070c0000060c0000061c00000e1c0000000000000000000000000000000000000000000
U+0024 000000000000000000000000000100000001000000010000000ff000003ff800007ff8000079180000f1000000e100000071000000710000003f8000001ff0000003f80000013c0000011e0000010e0000011e0000e13c0000fffc0000fff800003fe00000010000000100000001000000010000000000000000000000000000
U+0025 000000000000000000000000000000000000000007c006000fe00c001c701c001c3018001838380018387000183860001838e0001c30c0001c7180000fe38f8007c31fc000073ce0000e3870000c3070001c307000183070003030700070387000603ce000e01fc001c00f800000000000000000000000000000000000000000
U+0026 0000000000000000000000000000000000000000001fc000003fe000007fe0000078600000f0000000e00000007000000070000000780000007e000000ef018001c783800383c3800381e3800380f70003807f0003803e0003c01e0001f07f0000fff780007fe380003f83c00000000000000000000000000000000000000000
U+0027 0000000000000000000000000000000000000000000180000001800000018000000180000001800000018000000180000001800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
U+0028 0000000000000000000060000000e0000001c0000001c000000380000003800000038000000700000007000000070000000700000007000000070000000f00000007000000070000000700000007000000070000000700000003800000038000000380000001c0000001c0000000e00000006000000000000000000000000000
U+0029 000000000000000000060000000700000003000000038000000380000001c0000001c0000001c0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000001c0000001c0000001c0000003800000038000000300000007000000060000000000000000000000000000
U+002A 000000000000000000000000000000000000000000010000000100000001000000610c0000793c00001ff0000007c0000007c000001ff00000793c0000610c0000010000000100000001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
U+002B 00000000000000000000000000000000000000000000000000000000000380000003800000038000000380000003800000038000000380000003800003ffff8003ffff80000380000003800000038000000380000003800000038000000380000003800000000000000000000000000000000000000000000000000000000000
U+002C 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000003c0000003c0000003c0000003800000038000000300000007000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
U+002D 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001fe000001fe00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
U+002E 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000380000003800000038000000380000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
U+002F 0000000000000000000000000000700000007000000060000000e0000000e0000000e0000000c0000001c0000001c00000018000000380000003800000030000000700000007000000060000000e0000000e0000000e0000000c0000001c0000001c000000180000003800000038000000000000000000000000000000000000
U+0030 00000000000000000000000000000000000000000007c000001ff000003ff800007c7c0000781c0000701c0000f01e0000e00e0000e00e0000e00e0000e00e0000e00e0000e00e0000e00e0000e00e0000f01e0000701c0000781c00007c7c00003ff800001ff0000007c0000000000000000000000000000000000000000000
U+0031 0000000000000000000000000000000000000000001fc000007fc000007fc0000073c0000003c0000003c0000003c0000003c0000003c0000003c0000003c0000003c0000003c0000003c0000003c0000003c0000003c0000003c0000003c000003ffc00003ffc00003ffc000000000000000000000000000000000000000000
U+0032 0000000000000000000000000000000000000000003fc00000fff00000fff80000e07c0000003c0000001c0000001c0000001c0000003c0000003800000070000000e0000001c0000003800000070000000e0000001c0000003800000070000000fffc0000fffc0000fffc000000000000000000000000000000000000000000
U+0033 0000000000000000000000000000000000000000001fc000007ff000007ff80000607c0000001c0000001c0000001c0000001c0000007800000ff000000fe000000ff80000007c0000001c0000001e0000000e0000001e0000001c0000c07c0000fff80000fff000003fc0000000000000000000000000000000000000000000
U+0034 00000000000000000000000000000000000000000000f0000001f0000001f0000003f0000003700000077000000e7000000c7000001c700000387000003070000070700000e0700000c0700001ffff0001ffff0001ffff0000007000000070000000700000007000000070000000000000000000000000000000000000000000
U+0035 0000000000000000000000000000000000000000007ff800007ff800007ff8000070000000700000007000000070000000700000007fc000007ff000007ff80000607c0000003c0000001c0000001e0000001e0000001c0000003c0000e07c0000fff80000fff000003fc0000000000000000000000000000000000000000000
U+0036 00000000000000000000000000000000000000000003f800000ffc00001ffc00003e0c0000780000007800000070000000f0000000f3e00000eff80000fffc0000fc3e0000f01e0000f00e0000f00e0000f00e0000700e0000701e00003c3c00003ffc00001ff8000007e0000000000000000000000000000000000000000000
U+0037 000000000000000000000000000000000000000000fffe0000fffe0000fffc0000001c0000003800000038000000780000007000000070000000e0000000e0000000e0000001c0000001c0000003c00000038000000380000007000000070000000f0000000e0000000e00000000000000000000000000000000000000000000
U+0038 0000000000000000000000000000000000000000000fe000003ff800007ffc0000783c0000701e0000f01e0000701e0000701c0000783c00003ff800000fe000003ff80000783c0000f01e0000e00e0000e00e0000e00e0000f01e0000f83e00007ffc00003ff800000fe0000000000000000000000000000000000000000000
U+0039 0000000000000000000000000000000000000000000fc000003ff000007ff8000078780000f01c0000e01c0000e01e0000e01e0000e01e0000f01e0000787e00007ffe00003fee00000f8e0000001e0000001c0000003c0000003c000060f800007ff000007fe000001f80000000000000000000000000000000000000000000
U+003A 00000000000000000000000000000000000000000000000000000000000000000003c0000003c0000003c0000003c00000000000000000000000000000000000000000000000000000000000000000000003c0000003c0000003c0000003c0000000000000000000000000000000000000000000000000000000000000000000
U+003B 0000000000000000000000000000000000000000000000000003c0000003c0000003c0000003c00000000000000000000000000000000000000000000000000000000000000000000003c0000003c0000003c0000003800000038000000300000007000000000000000000000000000000000000000000000000000000000000
U+003C 00000000000000000000000000000000000000000000000000000000000001800000078000003f800001fe00000ff000007f800001fc000003f0000003f0000001fc0000007f8000000ff0000001fe0000003f8000000f8000000180000000000000000000000000000000000000000000000000000000000000000000000000
U+003D 00000000000000000000000000000000000000000000000000000000000000000000000003ffff8003ffff800000000000000000000000000000000003ffff8003ffff80000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
U+003E 000000000000000000000000000000000000000000000000000000000300000003e0000003f8000000ff0000001fe0000003fc0000007f0000000f8000000f8000007f000003fc00001fe00000ff000003f8000003e0000003000000000000000000000000000000000000000000000000000000000000000000000000000000
U+003F 00000000000000000000000000000000000000000007e000001ff000003ff80000387c0000203c0000001c0000001c0000003800000078000000f0000001e0000003c000000380000003800000038000000380000000000000000000000380000003800000038000000380000000000000000000000000000000000000000000
U+0040 000000000000000000000000000ff800003ffe0000ffff0001f80fc003e003e0078000e0070000700e07cc300c1fec381c1ffc181c3c3c1818381c1818300c3818300c3818381c701c3c3cf01c1fffe00c1fefc00e07cf00070000000780000003c0030001f81f0000ffff00003ffc00000ff000000000000000000000000000
U+0041 0000000000000000000000000000000000000000000780000007c0000007c000000fc000000ee000001ce000001cf000001c70000038700000383800007838000070380000701c0000f01c0000fffe0000fffe0001fffe0001c00f0003c007000380070003800780078003800000000000000000000000000000000000000000
U+0042 000000000000000000000000000000000000000000ffe00000fff80000fffc0000e03c0000e01e0000e01e0000e01e0000e01c0000e03c0000fff80000fff00000fff80000e03e0000e00e0000e00e0000e00f0000e00f0000e00e0000e03e0000fffc0000fff80000fff0000000000000000000000000000000000000000000
U+0043 00000000000000000000000000000000000000000007f800001fff00003fff00007e070000f8010000f0000001e0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001e0000000f0000000f80100007e0700003fff00001fff000007f8000000000000000000000000000000000000000000
U+0044 000000000000000000000000000000000000000001ffc00001fff80001fffc0001c07e0001c01f0001c00f0001c0078001c0038001c0038001c0038001c0038001c0038001c0038001c0038001c0038001c0078001c00f0001c01f0001c07e0001fffc0001fff80001ffc0000000000000000000000000000000000000000000
U+0045 0000000000000000000000000000000000000000007ffe00007ffe00007ffe00007000000070000000700000007000000070000000700000007ffc00007ffc00007ffc0000700000007000000070000000700000007000000070000000700000007ffe00007ffe00007ffe000000000000000000000000000000000000000000
U+0046 0000000000000000000000000000000000000000003ffe00003ffe00003ffe00003800000038000000380000003800000038000000380000003ffc00003ffc00003ffc00003800000038000000380000003800000038000000380000003800000038000000380000003800000000000000000000000000000000000000000000
U+0047 00000000000000000000000000000000000000000007f800003ffe00007fff0000fc0f0001f0010001e0000003c0000003800000038000000380000003807f8003807f8003807f80038003800380038003c0038001e0038001f0038000fc0f80007fff00003ffe00000ff0000000000000000000000000000000000000000000
U+0048 000000000000000000000000000000000000000001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c0070001ffff0001ffff0001ffff0001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c007000000000000000000000000000000000000000000
U+0049 0000000000000000000000000000000000000000000380000003800000038000000380000003800000038000000380000003800000038000000380000003800000038000000380000003800000038000000380000003800000038000000380000003800000038000000380000000000000000000000000000000000000000000
U+004A 00000000000000000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000003c00000078000003f8000003f0000003e00000000000000000000
U+004B 000000000000000000000000000000000000000000e00f0000e01e0000e03c0000e0780000e0f00000e1e00000e3c00000e7800000ef000000fe000000fc000000fe000000ef000000e7800000e3c00000e1e00000e0f00000e0780000e03c0000e01e0000e00f0000e007800000000000000000000000000000000000000000
U+004C 000000000000000000000000000000000000000000380000003800000038000000380000003800000038000000380000003800000038000000380000003800000038000000380000003800000038000000380000003800000038000000380000003fff00003fff00003fff000000000000000000000000000000000000000000
U+004D 000000000000000000000000000000000000000003e007c003e007c003e007c003f00fc003f00fc003b01dc003b81dc003b819c0039c39c0039c39c0038c31c0038e71c0038e71c00386e1c00387e1c00387c1c00383c1c00383c1c0038001c0038001c0038001c0038001c00000000000000000000000000000000000000000
U+004E 000000000000000000000000000000000000000000f0038000f8038000f8038000fc038000fc038000ee038000ee038000e7038000e7838000e3838000e3c38000e1c38000e1e38000e0e38000e0f38000e0738000e03b8000e03f8000e01f8000e01f8000e00f8000e00f800000000000000000000000000000000000000000
U+004F 0000000000000000000000000000000000000000000fe000003ff800007ffe0000f83f0001f00f0001e0078003c00380038003c0038003c0038001c0038001c0038001c0038001c0038003c0038003c003c0038001e0078001f00f0000f83f00007ffe00003ffc00000fe0000000000000000000000000000000000000000000
U+0050 0000000000000000000000000000000000000000003ff000003ffc00003ffe0000381f0000380f0000380700003807000038070000380f0000381f00003ffe00003ffc00003ff0000038000000380000003800000038000000380000003800000038000000380000003800000000000000000000000000000000000000000000
U+0051 000000000000000000000000000fe000003ffc00007ffe0000f83f0001f00f0001e0078003c00380038003c0038003c0038001c0038001c0038001c0038001c0038003c0038003c003c0038001e0078001f00f0000f83e00007ffc00003ff800000ff0000000780000003c0000001e0000000f00000000000000000000000000
U+0052 000000000000000000000000000000000000000000ffc00000fff00000fff80000e07c0000e03c0000e01c0000e01c0000e01c0000e03c0000e0780000fff80000ffe00000fff00000e0f80000e0380000e03c0000e01c0000e01e0000e00e0000e00f0000e0070000e007800000000000000000000000000000000000000000
U+0053 0000000000000000000000000000000000000000000ff000003ffc00007ffc0000f81c0000f0000000e0000000e0000000e0000000f80000007f8000003ff000000ffc000000fc0000001e0000000e0000000e0000000e0000000e0000e03e0000fffc0000fff800003fe0000000000000000000000000000000000000000000
U+0054 000000000000000000000000000000000000000001ffffc001ffffc001ffffc00001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000000000000000000000000000000000000000000
U+0055 000000000000000000000000000000000000000000e0070000e0070000e0070000e0070000e0070000e0070000e0070000e0070000e0070000e0070000e0070000e0070000e0070000e0070000e0070000e0070000e0070000f00f00007c3e00007ffc00003ff800000ff0000000000000000000000000000000000000000000
U+0056 000000000000000000000000000000000000000007800380038003800380070003c0070001c00f0001c00e0000e00e0000e01e0000f01c0000701c0000703800007838000038780000387000001c7000001cf000001ee000000ee000000fc0000007c0000007c000000780000000000000000000000000000000000000000000
U+0057 00000000000000000000000000000000000000003803c03c3803c0381c07c0381c07c0381c07e0781c06e0700e0e60700e0e60700e0e70f00e0c70e0071c30e0071c30e0071c39e0071839c007b819c003b819c003b81dc003f01f8003f00f8001f00f8001f00f8001e00f000000000000000000000000000000000000000000
U+0058 000000000000000000000000000000000000000001c0070000e00e0000f01e0000703c0000383800003c7000001cf000000ee000000fc0000007c000000380000007c000000fc000000ee000001cf000003c70000038380000703c0000f01c0001e00e0001c00f0003c007000000000000000000000000000000000000000000
U+0059 000000000000000000000000000000000000000001e0038000e0070000700f0000780e0000381c00001c3c00001e3800000e70000007f0000007e0000003c0000003c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000000000000000000000000000000000000000000
U+005A 000000000000000000000000000000000000000001ffff0001ffff0001ffff0000000e0000001c0000003800000070000000f0000000e0000001c0000003800000070000000f0000001e0000001c0000003800000070000000e0000001e0000003ffff0003ffff0003ffff000000000000000000000000000000000000000000
U+005B 0000000000000000000fe000000fe000000fe000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000fe000000fe000000fe000000000000000000000000000
U+005C 000000000000000000000000003800000038000000180000001c0000001c0000000c0000000e0000000e0000000e0000000600000007000000070000000300000003800000038000000180000001c0000001c0000000c0000000e0000000e0000000e00000006000000070000000700000000000000000000000000000000000
U+005D 00000000000000000007e0000007e0000007e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000007e0000007e0000007e000000000000000000000000000
U+005E 00000000000000000000000000000000000000000003c0000007e000000ff000001c780000383c0000701e0000e00f0001c0078000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
U+005F 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000fffe0000fffe0000fffe0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
U+0060 00000000000000000000000000000000001c0000000e0000000e000000070000000380000001800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
U+0061 0000000000000000000000000000000000000000000000000000000000000000000fe000003ff800003ff80000303c0000001c0000000e00000ffe00003ffe00007ffe0000780e0000700e0000701e0000787e00007ffe00003fee00001f8e000000000000000000000000000000000000000000000000000000000000000000
U+0062 00000000000000000000000000000000007000000070000000700000007000000070000000700000007000000073e0000077f800007ffc00007c3c0000781e0000700e0000700e0000700e0000700e0000700e0000700e0000781e00007c3c00007ffc000077f8000073e0000000000000000000000000000000000000000000
U+0063 00000000000000000000000000000000000000000000000000000000000000000007f000000ffc00003ffc00003e0c000078000000700000007000000070000000700000007000000070000000780000003e0c00003ffc00000ffc000007f0000000000000000000000000000000000000000000000000000000000000000000
U+0064 0000000000000000000000000000000000000c0000000c0000000c0000000c0000000c0000000c0000000c00000f8c00003fec00007ffc0000787c0000f03c0000e01c0000e01c0000e01c0000e01c0000e01c0000e01c0000f03c0000787c00007ffc00003fec00000f8c000000000000000000000000000000000000000000
U+0065 00000000000000000000000000000000000000000000000000000000000000000007f000000ffc00003ffc00003c1e000070070000700700007fff00007fff00007fff00007000000070000000780200003e0e00001ffe00000ffe000003f0000000000000000000000000000000000000000000000000000000000000000000
U+0066 000000000000000000000000000000000000f8000003f8000003f80000078000000700000007000000070000001ff800001ff800001ff800000700000007000000070000000700000007000000070000000700000007000000070000000700000007000000070000000700000000000000000000000000000000000000000000
U+0067 0000000000000000000000000000000000000000000f8c00003fec00007ffc0000787c0000f03c0000e01c0000e01c0000e01c0000e01c0000e01c0000e01c0000f03c0000787c00007ffc00003ffc00000f9c0000001c0000003c0000207800003ff800003ff000001fc0000000000000000000000000000000000000000000
U+0068 00000000000000000000000000000000007000000070000000700000007000000070000000700000007000000073f0000077f800007ffc00007c3c0000781c0000701c0000700e0000700e0000700e0000700e0000700e0000700e0000700e0000700e0000700e0000700e000000000000000000000000000000000000000000
U+0069 000000000000000000000000000000000001c0000001c0000001c000000000000000000000000000000000000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000000000000000000000000000000000000000000
U+006A 000000000001c0000001c0000001c000000000000000000000000000000000000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001800000038000001f8000001f0000001e00000000000000000000
U+006B 000000000000000000000000000000000038000000380000003800000038000000380000003800000038000000380e0000381c00003878000038f0000039e000003bc000003f0000003f0000003f0000003b80000039e0000038f0000038780000383c0000381e0000380f000000000000000000000000000000000000000000
U+006C 000000000000000000000000000000000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000000000000000000000000000000000000000000
U+006D 00000000000000000000000000000000000000000000000000000000000000000e7c0f800efe3fc00fff7fe00f87f1e00e03c0f00e03c0700e0380700e0380700e0380700e0380700e0380700e0380700e0380700e0380700e0380700e0380700000000000000000000000000000000000000000000000000000000000000000
U+006E 00000000000000000000000000000000000000000000000000000000000000000073f0000077f800007ffc00007c3c0000781c0000701c0000700e0000700e0000700e0000700e0000700e0000700e0000700e0000700e0000700e0000700e000000000000000000000000000000000000000000000000000000000000000000
U+006F 00000000000000000000000000000000000000000000000000000000000000000007e000001ff800003ffc00003c3e0000780e0000700f000070070000700700007007000070070000700f0000780e00003c3e00003ffc00001ff8000007e0000000000000000000000000000000000000000000000000000000000000000000
U+0070 00000000000000000000000000000000000000000073e0000077f800007ffc00007c3c0000781e0000700e0000700e0000700e0000700e0000700e0000700e0000781e00007c3c00007ffc000077f8000073e0000070000000700000007000000070000000700000007000000000000000000000000000000000000000000000
U+0071 0000000000000000000000000000000000000000000f8c00003fec00007ffc0000787c0000f03c0000e01c0000e01c0000e01c0000e01c0000e01c0000e01c0000f03c0000787c00007ffc00003fec00000f8c0000000c0000000c0000000c0000000c0000000c0000000c000000000000000000000000000000000000000000
U+0072 0000000000000000000000000000000000000000000000000000000000000000000e7800000ef800000ff800000f8000000f0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e00000000000000000000000000000000000000000000000000000000000000000000
U+0073 0000000000000000000000000000000000000000000000000000000000000000000ff000001ff800003ff800003c18000038000000380000003f0000000ff0000001f80000001c0000001c0000201c0000383c00003ffc00003ff800000fe0000000000000000000000000000000000000000000000000000000000000000000
U+0074 00000000000000000000000000000000000000000007000000070000000700000007000000070000001ff800001ff800001ff800000700000007000000070000000700000007000000070000000700000007000000070000000700000007f8000003f8000001f800000000000000000000000000000000000000000000000000
U+0075 000000000000000000000000000000000000000000000000000000000000000000e01c0000e01c0000e01c0000e01c0000e01c0000e01c0000e01c0000e01c0000e01c0000e01c0000701c0000701c0000787c00007ffc00003fdc00001f9c000000000000000000000000000000000000000000000000000000000000000000
U+0076 000000000000000000000000000000000000000000000000000000000000000000e0070000e00e0000700e0000700e0000381c0000381c0000383800001c3800001c3800001c7000000e7000000ef0000007e0000007e0000007c0000003c0000000000000000000000000000000000000000000000000000000000000000000
U+0077 00000000000000000000000000000000000000000000000000000000000000000e0781c0060781c00707c1c00707c180070ec380038ec380038ce380038ce700039c670001dc770001d8770001f87e0000f83e0000f83e0000f03c0000f01c000000000000000000000000000000000000000000000000000000000000000000
U+0078 000000000000000000000000000000000000000000000000000000000000000000700e0000781c00003c3c00001c3800000e70000007e0000007e0000003c0000007c0000007e000000ef000001e7000003c380000381c0000701e0000f00e000000000000000000000000000000000000000000000000000000000000000000
U+0079 000000000000000000000000000000000000000000e0070000e00e0000700e0000701c0000381c0000381c00001c3800001c3800001c7000000e7000000e60000007e0000007e0000003c0000003c00000038000000380000003000000070000007f0000007e0000007c00000000000000000000000000000000000000000000
U+007A 0000000000000000000000000000000000000000000000000000000000000000003ffe00003ffe00003ffc000000180000003000000060000000e0000001c0000003800000070000000e0000001c000000380000007ffe00007ffe00007ffe000000000000000000000000000000000000000000000000000000000000000000
U+007B 00000000000000000000f8000001f8000001f8000003c0000003800000038000000380000003800000038000000380000003800000078000003f0000003e0000003f00000007800000038000000380000003800000038000000380000003800000038000000380000003c0000001f8000001f800000078000000000000000000
U+007C 0000000000018000000180000001800000018000000180000001800000018000000180000001800000018000000180000001800000018000000180000001800000018000000180000001800000018000000180000001800000018000000180000001800000018000000180000001800000018000000180000001800000000000
U+007D 0000000000000000003e0000003f0000003f000000078000000380000003800000038000000380000003800000038000000380000003c0000001f8000000f8000001f8000003c000000380000003800000038000000380000003800000038000000380000003800000078000003f0000003f0000003e00000000000000000000
U+007E 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000007e008001ffc3800383ff000200fc000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
U+0410 0000000000000000000000000000000000000000000780000007c0000007c000000fc000000ee000001ce000001cf000001c70000038700000383800007838000070380000701c0000f01c0000fffe0000fffe0001fffe0001c00f0003c007000380070003800780078003800000000000000000000000000000000000000000
U+0411 000000000000000000000000000000000000000000fffc0000fffc0000fffc0000e0000000e0000000e0000000e0000000e0000000e0000000fff00000fff80000fffc0000e03e0000e00e0000e00e0000e00f0000e00e0000e00e0000e03e0000fffc0000fff80000fff0000000000000000000000000000000000000000000
U+0412 000000000000000000000000000000000000000000ffe00000fff80000fffc0000e03c0000e01e0000e01e0000e01e0000e01c0000e03c0000fff80000fff00000fff80000e03e0000e00e0000e00e0000e00f0000e00f0000e00e0000e03e0000fffc0000fff80000fff0000000000000000000000000000000000000000000
U+0413 0000000000000000000000000000000000000000003fff00003fff00003fff00003800000038000000380000003800000038000000380000003800000038000000380000003800000038000000380000003800000038000000380000003800000038000000380000003800000000000000000000000000000000000000000000
U+0414 0000000000000000003fff00003fff00003fff00003c0f00003c0f00003c0f0000380f0000380f0000380f0000380f0000380f0000380f0000380f0000380f0000780f0000700f0000700f0000f00f0001e00f0007ffffc007ffffc007ffffc0070001c0070001c0070001c0070001c0070001c0000000000000000000000000
U+0415 0000000000000000000000000000000000000000007ffe00007ffe00007ffe00007000000070000000700000007000000070000000700000007ffc00007ffc00007ffc0000700000007000000070000000700000007000000070000000700000007ffe00007ffe00007ffe000000000000000000000000000000000000000000
U+0416 00000000000000000000000000000000000000007801c01e3c01c03c1e01c0780f01c0f00781c1e003c1c3c001e1c38000f1c7000079cf0000fddf0000ffff8001cffb8001cff3c00387e1c00783c0e00701c0f00e01c0701e01c0381c01c03c3801c01c7801c00e7001c00f0000000000000000000000000000000000000000
U+0417 0000000000000000000000000000000000000000001fe000007ff80000fffc0000f03c0000801e0000000e0000000e0000001c0000003c00000ff800000ff000000ffc0000003e0000001e0000000e0000000e0000000e0000801e0000e03e0000fffc00007ff800001fc0000000000000000000000000000000000000000000
U+0418 000000000000000000000000000000000000000000e00f8000e00f8000e01f8000e01f8000e03f8000e03b8000e0738000e0f38000e0e38000e1e38000e1c38000e3c38000e3838000e7838000e7038000ee038000ee038000fc038000fc038000f8038000f8038000f003800000000000000000000000000000000000000000
U+0419 0000000000000000001c1800000c3000000ff0000003e000000000000000000000e00f8000e00f8000e01f8000e01f8000e03f8000e03b8000e0738000e0f38000e0e38000e1e38000e1c38000e3c38000e3838000e7838000e7038000ee038000ee038000fc038000fc038000f8038000f8038000f003800000000000000000
U+041A 000000000000000000000000000000000000000000e0078000e00f0000e01e0000e03c0000e0780000e0f00000e1e00000e3c00000e7800000ef800000ffc00000fde00000f8e00000f0700000e0780000e0380000e01c0000e01e0000e00e0000e0070000e0078000e003800000000000000000000000000000000000000000
U+041B 0000000000000000000000000000000000000000003fff00003fff00003fff00003c0700003c0700003c0700003c0700003c0700003c0700003c07000038070000380700003807000038070000380700007807000070070000f0070003f0070007e0070007c00700070007000000000000000000000000000000000000000000
U+041C 000000000000000000000000000000000000000003e007c003e007c003e007c003f00fc003f00fc003b01dc003b81dc003b819c0039c39c0039c39c0038c31c0038e71c0038e71c00386e1c00387e1c00387c1c00383c1c00383c1c0038001c0038001c0038001c0038001c00000000000000000000000000000000000000000
U+041D 000000000000000000000000000000000000000001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c0070001ffff0001ffff0001ffff0001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c007000000000000000000000000000000000000000000
U+041E 0000000000000000000000000000000000000000000fe000003ff800007ffe0000f83f0001f00f0001e0078003c00380038003c0038003c0038001c0038001c0038001c0038001c0038003c0038003c003c0038001e0078001f00f0000f83f00007ffe00003ffc00000fe0000000000000000000000000000000000000000000
U+041F 000000000000000000000000000000000000000001ffff0001ffff0001ffff0001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c007000000000000000000000000000000000000000000
U+0420 0000000000000000000000000000000000000000003ff000003ffc00003ffe0000381f0000380f0000380700003807000038070000380f0000381f00003ffe00003ffc00003ff0000038000000380000003800000038000000380000003800000038000000380000003800000000000000000000000000000000000000000000
U+0421 00000000000000000000000000000000000000000007f800001fff00003fff00007e070000f8010000f0000001e0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001e0000000f0000000f80100007e0700003fff00001fff000007f8000000000000000000000000000000000000000000
U+0422 000000000000000000000000000000000000000001ffffc001ffffc001ffffc00001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000000000000000000000000000000000000000000
U+0423 000000000000000000000000000000000000000000e0078000e0070000f00f0000700e0000780e0000381e00003c1c00001c3c00001c3800000e7800000e7000000f70000007f0000007e0000003e0000003c0000003c0000003800000078000003f8000003f0000003e00000000000000000000000000000000000000000000
U+0424 00000000000000000000000000000000000000000003c0000003c000001ff800007ffe0001ffff8003f3cfc003c3c3c00783c1e00703c1e00703c0e00703c0e00703c0e00703c0e00783c1e003c3c3c003e3c7c001ffff80007ffe00001ff8000003c0000003c0000003c0000000000000000000000000000000000000000000
U+0425 000000000000000000000000000000000000000001c0070000e00e0000f01e0000703c0000383800003c7000001cf000000ee000000fc0000007c000000380000007c000000fc000000ee000001cf000003c70000038380000703c0000f01c0001e00e0001c00f0003c007000000000000000000000000000000000000000000
U+0426 000000000000000001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c0070001c0070001ffffc001ffffc001ffffc0000000c0000000c0000000c0000000c0000000c0000000000000000000000000
U+0427 000000000000000000000000000000000000000001e00e0001e00e0001e00e0001e00e0001e00e0001e00e0001e00e0000e00e0000e00e0000e00e0000f00e00007ffe00007ffe00001ffe0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e000000000000000000000000000000000000000000
U+0428 00000000000000000000000000000000000000001c03c0381c03c0381c03c0381c03c0381c03c0381c03c0381c03c0381c03c0381c03c0381c03c0381c03c0381c03c0381c03c0381c03c0381c03c0381c03c0381c03c0381c03c0381c03c0381ffffff81ffffff81ffffff80000000000000000000000000000000000000000
U+0429 0000000000000000000000001c0380701c0380701c0380701c0380701c0380701c0380701c0380701c0380701c0380701c0380701c0380701c0380701c0380701c0380701c0380701c0380701c0380701c0380701ffffffe1ffffffe1ffffffe0000000e0000000e0000000e0000000e0000000e000000000000000000000000
U+042A 00000000000000000000000000000000000000000ff800000ff800000ff80000003800000038000000380000003800000038000000380000003ffc00003fff00003fff8000380780003803c0003803c0003801c0003803c0003803c000380780003fff80003fff00003ffc000000000000000000000000000000000000000000
U+042B 0000000000000000000000000000000000000000038001e0038001e0038001e0038001e0038001e0038001e0038001e0038001e0038001e003ffc1e003ffe1e003fff1e00380f9e0038039e0038039e003803de0038039e0038039e00380f9e003fff1e003ffe1e003ffc1e00000000000000000000000000000000000000000
U+042C 000000000000000000000000000000000000000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000e0000000fff00000fff80000fffc0000e03e0000e00e0000e00e0000e00f0000e00e0000e00e0000e03e0000fffc0000fff80000fff0000000000000000000000000000000000000000000
U+042D 0000000000000000000000000000000000000000003fc00001fff00001fff80001c07c0001001e0000000e0000000f000000070000000700007fff00007fff00007fff00000007000000070000000f0000000f0000001e0001003e0001c0fc0001fff80001fff000003fc0000000000000000000000000000000000000000000
U+042E 00000000000000000000000000000000000000001c007f001c01ffc01c03fff01c07c1f01c0f00781c0e003c1c1e003c1c1c001c1c1c001e1c3c001e1ffc001e1ffc001e1ffc001e1c3c001e1c1c001c1c1e003c1c1e003c1c0f00781c07c1f01c07fff01c01ffc01c007f000000000000000000000000000000000000000000
U+042F 0000000000000000000000000000000000000000000ffe00003ffe00007ffe0000f80e0000f00e0000e00e0000e00e0000e00e0000f00e0000f80e00007ffe00001ffe000007fe00000f0e00000e0e00001c0e00003c0e0000380e0000780e0000f00e0000e00e0001e00e000000000000000000000000000000000000000000
U+0430 0000000000000000000000000000000000000000000000000000000000000000000fe000003ff800003ff80000303c0000001c0000000e00000ffe00003ffe00007ffe0000780e0000700e0000701e0000787e00007ffe00003fee00001f8e000000000000000000000000000000000000000000000000000000000000000000
U+0431 00000000000000000000000000000000000000000003f800000ff800003ffc00007f00000078000000f0000000e0000000efe00000fff00000fff80000f87c0000f01c0000e01e0000e00e0000e00e0000e00e0000e00e0000e01e0000f01c0000787c00007ff800003ff000000fe00000000000000000000000000000000000
U+0432 0000000000000000000000000000000000000000000000000000000000000000003ff000003ff800003ffc0000383c0000381c0000383c00003ff800003ff000003ffc0000381c0000380e0000380e0000381e00003ffc00003ffc00003ff0000000000000000000000000000000000000000000000000000000000000000000
U+0433 0000000000000000000000000000000000000000000000000000000000000000001ffc00001ffc00001ffc00001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c0000001c00000000000000000000000000000000000000000000000000000000000000000000
U+0434 000000000000000000000000000000000000000000000000001ffc00001ffc00001ffc00001c1c00001c1c00001c1c00001c1c00001c1c0000381c0000381c0000381c0000701c0000f01c0003ffff0003ffff0003ffff0003800300038003000380030003800300000000000000000000000000000000000000000000000000
U+0435 00000000000000000000000000000000000000000000000000000000000000000007f000000ffc00003ffc00003c1e000070070000700700007fff00007fff00007fff00007000000070000000780200003e0e00001ffe00000ffe000003f0000000000000000000000000000000000000000000000000000000000000000000
U+0436 00000000000000000000000000000000000000000000000000000000000000000f0381e0078383c003c3838001c3870000e38e0000739c00007bbc00007ffc0000efee0001c7c70001c3870003838380070381c0070381c00e0380e01c0380700000000000000000000000000000000000000000000000000000000000000000
U+0437 0000000000000000000000000000000000000000000000000000000000000000000fe000003ff800003ff80000303c0000001c00000038000007f8000007e0000007f80000003c0000001c0000001c0000303c00003ffc00003ff800001fe0000000000000000000000000000000000000000000000000000000000000000000
U+0438 000000000000000000000000000000000000000000000000000000000000000000701e0000703e0000703e0000707e000070ee000070ee000071ce000071ce0000738e0000770e0000770e00007e0e00007c0e00007c0e0000780e0000780e000000000000000000000000000000000000000000000000000000000000000000
U+0439 0000000000000000000000000000000000183000001c7000000ff0000007c00000000000000000000000000000701e0000703e0000703e0000707e000070ee000070ee000071ce000071ce0000738e0000770e0000770e00007e0e00007c0e00007c0e0000780e0000780e000000000000000000000000000000000000000000
U+043A 000000000000000000000000000000000000000000000000000000000000000000381e0000383c00003878000038f0000039e000003bc000003f8000003fc000003ee000003cf000003870000038380000383c0000381c0000380e00003807000000000000000000000000000000000000000000000000000000000000000000
U+043B 0000000000000000000000000000000000000000000000000000000000000000001ffe00001ffe00001ffe00001c0e00001c0e00001c0e00001c0e00001c0e00001c0e00001c0e00001c0e00003c0e0000780e0001f80e0001f00e0001c00e000000000000000000000000000000000000000000000000000000000000000000
U+043C 000000000000000000000000000000000000000000000000000000000000000001e00f0001e01f0001f01f0001f03f0001f8370001d8770001dc770001dc670001cce70001cec70001c7c70001c7870001c3870001c0070001c0070001c007000000000000000000000000000000000000000000000000000000000000000000
U+043D 000000000000000000000000000000000000000000000000000000000000000000700e0000700e0000700e0000700e0000700e0000700e00007ffe00007ffe00007ffe0000700e0000700e0000700e0000700e0000700e0000700e0000700e000000000000000000000000000000000000000000000000000000000000000000
U+043E 00000000000000000000000000000000000000000000000000000000000000000007e000001ff800003ffc00003c3e0000780e0000700f000070070000700700007007000070070000700f0000780e00003c3e00003ffc00001ff8000007e0000000000000000000000000000000000000000000000000000000000000000000
U+043F 0000000000000000000000000000000000000000000000000000000000000000007ffe00007ffe00007ffe0000700e0000700e0000700e0000700e0000700e0000700e0000700e0000700e0000700e0000700e0000700e0000700e0000700e000000000000000000000000000000000000000000000000000000000000000000
U+0440 00000000000000000000000000000000000000000073e0000077f800007ffc00007c3c0000781e0000700e0000700e0000700e0000700e0000700e0000700e0000781e00007c3c00007ffc000077f8000073e0000070000000700000007000000070000000700000007000000000000000000000000000000000000000000000
U+0441 00000000000000000000000000000000000000000000000000000000000000000007f000000ffc00003ffc00003e0c000078000000700000007000000070000000700000007000000070000000780000003e0c00003ffc00000ffc000007f0000000000000000000000000000000000000000000000000000000000000000000
U+0442 000000000000000000000000000000000000000000000000000000000000000000ffff0000ffff0000ffff00000380000003800000038000000380000003800000038000000380000003800000038000000380000003800000038000000380000000000000000000000000000000000000000000000000000000000000000000
U+0443 000000000000000000000000000000000000000000e0070000e00e0000700e0000701c0000381c0000381c00001c3800001c3800001c7000000e7000000e60000007e0000007e0000003c0000003c00000038000000380000003000000070000007f0000007e0000007c00000000000000000000000000000000000000000000
U+0444 000000000003800000038000000380000003800000038000000380000003800000fb9e0001ffbf8003ffffc007c7e3c00703c1e0070380e0070380e0070380e0070380e0070380e0070380e00703c1e007c7e3c003ffffc001ffbf8000fb9f000003800000038000000380000003800000038000000380000000000000000000
U+0445 000000000000000000000000000000000000000000000000000000000000000000700e0000781c00003c3c00001c3800000e70000007e0000007e0000003c0000007c0000007e000000ef000001e7000003c380000381c0000701e0000f00e000000000000000000000000000000000000000000000000000000000000000000
U+0446 00000000000000000000000000000000000000000000000000700e0000700e0000700e0000700e0000700e0000700e0000700e0000700e0000700e0000700e0000700e0000700e0000700e00007fff80007fff80007fff8000000180000001800000018000000180000000000000000000000000000000000000000000000000
U+0447 000000000000000000000000000000000000000000000000000000000000000000701c0000701c0000701c0000701c0000701c0000701c0000781c00003ffc00003ffc00000ffc0000001c0000001c0000001c0000001c0000001c0000001c000000000000000000000000000000000000000000000000000000000000000000
U+0448 0000000000000000000000000000000000000000000000000000000000000000070380e0070380e0070380e0070380e0070380e0070380e0070380e0070380e0070380e0070380e0070380e0070380e0070380e007ffffe007ffffe007ffffe00000000000000000000000000000000000000000000000000000000000000000
U+0449 000000000000000000000000000000000000000000000000070380e0070380e0070380e0070380e0070380e0070380e0070380e0070380e0070380e0070380e0070380e0070380e0070380e007fffff807fffff807fffff800000018000000180000001800000018000000000000000000000000000000000000000000000000
U+044A 000000000000000000000000000000000000000000000000000000000000000003fc000003fc000003fc0000001c0000001c0000001c0000001ffc00001ffe00001fff00001c0f00001c0700001c0700001c0f00001fff00001ffe00001ffc000000000000000000000000000000000000000000000000000000000000000000
U+044B 000000000000000000000000000000000000000000000000000000000000000001c0038001c0038001c0038001c0038001c0038001c0038001ff838001ffe38001ffe38001c0f38001c0738001c0738001c0f38001ffe38001ffe38001ff83800000000000000000000000000000000000000000000000000000000000000000
U+044C 0000000000000000000000000000000000000000000000000000000000000000003800000038000000380000003800000038000000380000003ff000003ffc00003ffc0000381e0000380e0000380e0000381e00003ffc00003ffc00003ff0000000000000000000000000000000000000000000000000000000000000000000
U+044D 0000000000000000000000000000000000000000000000000000000000000000001fc000003ff000003ff80000307c0000001c0000001c00001ffe00001ffe00001ffe0000000e0000001c0000001c0000307c00003ff800003ff000001fc0000000000000000000000000000000000000000000000000000000000000000000
U+044E 00000000000000000000000000000000000000000000000000000000000000000380fc000383ff000387ff80038f87c0038f03c0038e01c003fe01e003fe00e003fe00e0038e01e0038e01c0038f03c0038f87c00387ff800383ff000380fc000000000000000000000000000000000000000000000000000000000000000000
U+044F 0000000000000000000000000000000000000000000000000000000000000000000ffe00001ffe00003ffe00003c0e0000380e0000380e00003c0e00001ffe00000ffe000007fe0000070e00000e0e00001e0e00003c0e0000380e0000700e000000000000000000000000000000000000000000000000000000000000000000
U+0401 0000000000000000001e7000001e7000001e70000000000000000000007ffe00007ffe00007ffe00007000000070000000700000007000000070000000700000007ffc00007ffc00007ffc0000700000007000000070000000700000007000000070000000700000007ffe00007ffe00007ffe00000000000000000000000000
U+0451 00000000000000000000000000000000000e3800000e3800000e3800000000000000000000000000000000000007f000000ffc00003ffc00003c1e000070070000700700007fff00007fff00007fff00007000000070000000780200003e0e00001ffe00000ffe000003f0000000000000000000000000000000000000000000
U+00B7 0000000000000000000000000000000000000000000000000000000000000000000000000000000000038000000380000003800000038000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
U+00D7 000000000000000000000000000000000000000000000000000000000080020001c0070000e00e0000701c0000383800001c7000000fe0000007c0000007c0000007c000000fe000001c70000038380000701c0000e00e0001c00700008002000000000000000000000000000000000000000000000000000000000000000000
U+00B1 00000000000000000000000000000000000000000000000000038000000380000003800000038000000380000003800003ffff8003ffff8000038000000380000003800000038000000380000003800000000000000000000000000003ffff8003ffff8000000000000000000000000000000000000000000000000000000000
U+2192 000000000000000000000000000000000000000000000000000000000000000000000c0000001e0000000f0000000780000003c007ffffe007ffffe0000003c00000078000000f0000001e0000000c00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
U+2248 000000000000000000000000000000000000000000000000000000000000000000000000007e008001ffc3800383ff000200fc0000000000007e008001ffc3800383ff000200fc000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
U+2264 000000000000000000000000000000000000000000000000000000000000018000001f800000ff80000ffc00007fc00003fe000003f0000003fe0000007fc000000ffc000000ff8000001f8000000180000000000000000003ffff8003ffff800000000000000000000000000000000000000000000000000000000000000000
U+2265 000000000000000000000000000000000000000000000000000000000300000003f0000003fe0000007fe0000007fe000000ff8000001f800000ff800007fe00007fe00003fe000003f0000003000000000000000000000003ffff8003ffff800000000000000000000000000000000000000000000000000000000000000000
U+221A 000000000000000000000000000003800000020000000600000006000000040000000c0000000c0000001800000018000000100000e0300001f030000070200000386000003860000038c000001cc000001cc000001d8000000f8000000f0000000f000000070000000600000006000000000000000000000000000000000000
U+0394 0000000000000000000000000000000000000000000780000007c0000007c000000fc000000ee000001ce000001cf000001c70000038700000383800007838000070380000701c0000e01c0000e01e0000e00e0001c00e0001c0070003c0070003ffff0003ffff8007ffff800000000000000000000000000000000000000000
U+03A9 0000000000000000000000000000000000000000000fe000003ff80000fffc0000f83e0001e00f0003c007800380078003800380078003c0078003c0078003c0078003c003800380038003800380078001c0070001e00f0000f01e0000783c0007fc7fc007fc7fc007fc7fc00000000000000000000000000000000000000000
U+03B1 0000000000000000000000000000000000000000000000000000000000000000000f8700003fe600007fee0000f8fe0000f07c0000e07c0000e03c0000e0380000e0380000e0380000e0380000f07c0000f8fc00007fff00003fff00001fc7000000000000000000000000000000000000000000000000000000000000000000
U+03B2 00000000000fc000003ff000003ff8000078780000703800007018000070180000703800007038000070f8000077f0000077f0000077f80000703c0000700e0000700e0000700e0000700e0000700e00007c3e00007ffc00007ff8000077e0000070000000700000007000000070000000700000007000000000000000000000
U+03C0 000000000000000000000000000000000000000000000000000000000000000000ffff0000ffff0000ffff0000381c0000381c0000381c0000381c0000381c0000381c0000381c0000381c0000381c0000381c0000381f0000381f0000380f000000000000000000000000000000000000000000000000000000000000000000
U+2013 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000007ffc00007ffc00007ffc00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
U+2014 00000000000000000000000000000000000000000000000000000000000000000000000000000000000000003ffffffc3ffffffc3ffffffc000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
"""
const FONT_HEX_BOLD = """
U+0020 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
U+0021 00000000000000000000000000000000000000000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007c0000007c0000007c0000003c0000003c0000003c00000000000000000000007e0000007e0000007e0000007e0000007e0000000000000000000000000000000000000000000
U+0022 0000000000000000000000000000000000000000001c7800001c7800001c7800001c7800001c7800001c7800001c7800001c780000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
U+0023 000000000000000000000000000000000000000000070e0000070e00000f0e00000f1e00000e1e00000e1c0001ffffc001ffffc001ffffc0001c3800003c3800003c78000038700007ffff8007ffff8007ffff800070e0000070e00000f0e00000f1e00000e1e00000e1c0000000000000000000000000000000000000000000
U+0024 000000000000000000000000000380000003800000038000001ff800007ffe0000fffe0000fb9e0001f3860001f3800001fb800000ff800000fff800007ffc00003ffe000003ff000003bf0000039f0001839f0001e3bf0001fffe0001fffc00007ff00000038000000380000003800000038000000000000000000000000000
U+0025 000000000000000000000000000000000000000007e007000ff00f001e780e003c781c003c3c3c003c3c38003c3c78003c3cf0003c78e0001e79e0000ff1c7e007e38ff000079e7800071e3c000f3c3c000e3c3c001c3c3c003c3c3c00381e3c00701e7800f00ff000e007e00000000000000000000000000000000000000000
U+0026 0000000000000000000000000000000000000000001fe000003ff800007ff80000fc380000f8080000fc000000fc0000007e0000007f000000ff03e003ff83e003ffc3e007e7e3c007c3f7c007c1ffc007c1ff8007c0ff8007e07f0003f0ff8001ffffc000ffffe0003fc7f00000000000000000000000000000000000000000
U+0027 0000000000000000000000000000000000000000000380000003800000038000000380000003800000038000000380000003800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
U+0028 00000000000000000000f0000001f0000003e0000003e0000007c0000007c0000007c000000f8000000f8000000f8000000f8000000f8000000f8000001f8000000f8000000f8000000f8000000f8000000f8000000f80000007c0000007c0000007c0000003e0000003e0000001f0000000f000000000000000000000000000
U+0029 0000000000000000000f0000000f8000000f80000007c0000007c0000003e0000003e0000003e0000003f0000001f0000001f0000001f0000001f0000001f0000001f0000001f0000001f0000001f0000003f0000003e0000003e0000003e0000007c0000007c000000f8000000f8000000f0000000000000000000000000000
U+002A 000000000000000000000000000000000000000000018000000180000061840000719e00007ffe00001ff800000fe000000fe000001ff800007ffe0000719e0000618400000180000001800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
U+002B 000000000000000000000000000000000000000000000000000380000003800000038000000380000003800000038000000380000003800003ffff8003ffff8003ffff80000380000003800000038000000380000003800000038000000380000003800000000000000000000000000000000000000000000000000000000000
U+002C 00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000007c0000007c0000007c0000007c0000007c0000007c000000f8000000f0000000f0000000e00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
U+002D 00000000000000000000000000000000000000000000000000000000000000000000000000000000000ff800000ff800000ff800000ff800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
U+002E 000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000007c0000007c0000007c0000007c0000007c0000007c00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
U+002F 000000000000000000000000000078000000780000007000000070000000f0000000e0000000e0000001e0000001c0000001c0000003c0000003c0000003800000078000000780000007000000070000000f0000000e0000000e0000001e0000001c0000001c0000003c00000038000000000000000000000000000000000000
U+0030 0000000000000000000000000000000000000000000fe000003ff800007ffc0000fffe0000fc7e0001f83f0001f83f0001f03f0003f01f0003f01f0003f01f8003f01f8003f01f0003f01f0001f03f0001f83f0001f83f0000fc7e0000fffe00007ffc00003ff800000fe0000000000000000000000000000000000000000000
U+0031 0000000000000000000000000000000000000000003fe00000ffe00000ffe00000ffe00000f7e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e00000ffff0000ffff0000ffff0000ffff000000000000000000000000000000000000000000
U+0032 0000000000000000000000000000000000000000007fe00001fff80001fffc0001fffe0001e1fe0001807e0000007e0000007e0000007e0000007c000000fc000001f8000007f000000fe000001fc000003f8000007e000000fc000001fffe0001fffe0001fffe0001fffe000000000000000000000000000000000000000000
U+0033 0000000000000000000000000000000000000000003fe00000fff80000fffc0000fffe0000c0fe0000007e0000007e0000007e000000fc00001ff800001ff000001ffc00001ffe000000fe0000007e0000003f0001007f0001e0fe0001fffe0001fffc0000fff800003fe0000000000000000000000000000000000000000000
U+0034 00000000000000000000000000000000000000000001f8000003f8000007f8000007f800000ff800001ff800001ef800003cf800007cf8000078f80000f0f80001f0f80001e0f80003c0f80003ffff8003ffff8003ffff8003ffff800000f8000000f8000000f8000000f8000000000000000000000000000000000000000000
U+0035 000000000000000000000000000000000000000000fffc0000fffc0000fffc0000fffc0000f8000000f8000000f8000000ffe00000fff80000fffc0000fffe0000f0fe0000807f0000003f0000003f0000003f0001807f0001e0fe0001fffe0001fffc0000fff800001fe0000000000000000000000000000000000000000000
U+0036 00000000000000000000000000000000000000000007f000001ffc00003ffe00007ffe0000fe0e0000fc020001f8000001fbf00001fffc0001fffe0001fffe0001fc7f0001f83f0001f81f0001f81f0001f81f0000f83f0000fc7f00007ffe00007ffc00003ff800000fe0000000000000000000000000000000000000000000
U+0037 000000000000000000000000000000000000000001ffff0001ffff0001ffff0001fffe0000007e0000007e000000fc000000fc000001f8000001f8000001f0000003f0000003e0000007e0000007c000000fc000000fc000001f8000001f8000003f0000003f0000003e00000000000000000000000000000000000000000000
U+0038 0000000000000000000000000000000000000000001ff000007ffc0000fffe0000fffe0001fc7f0001f83f0001f83e0000fc7e00007ffc00003ff800003ff80000fffe0001fc7e0001f83f0001f03f0001f03f0001f83f0001fc7f0001fffe0000fffe00007ffc00001ff0000000000000000000000000000000000000000000
U+0039 0000000000000000000000000000000000000000001fc000003ff00000fff80000fffc0001f8fe0001f87e0001f03f0003f03f0003f03f0001f87f0001f8ff0001ffff0000ffff00007fff00001fbf0000003e0000807e0000e0fc0000fffc0000fff800007ff000001f80000000000000000000000000000000000000000000
U+003A 00000000000000000000000000000000000000000000000000000000000000000007e0000007e0000007e0000007e0000007e0000007e000000000000000000000000000000000000007e0000007e0000007e0000007e0000007e0000007e0000000000000000000000000000000000000000000000000000000000000000000
U+003B 0000000000000000000000000000000000000000000000000007e0000007e0000007e0000007e0000007e0000007e000000000000000000000000000000000000007e0000007e0000007e0000007e0000007e0000007c00000078000000f8000000f0000000e0000000000000000000000000000000000000000000000000000
U+003C 00000000000000000000000000000000000000000000000000000000000001800000078000003f800001ff80000ffe00007ff00001ff800003fc000003f0000003fc000001ff8000007ff000000ffe000001ff8000003f8000000f80000001800000000000000000000000000000000000000000000000000000000000000000
U+003D 00000000000000000000000000000000000000000000000000000000000000000000000003ffff8003ffff8003ffff8000000000000000000000000003ffff8003ffff8003ffff800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
U+003E 000000000000000000000000000000000000000000000000000000000300000003e0000003f8000003ff000000ffe000001ffc000003ff0000007f8000001f8000007f800003ff00001ffc0000ffe00003ff000003f8000003e00000030000000000000000000000000000000000000000000000000000000000000000000000
U+003F 0000000000000000000000000000000000000000007fe000007ff800007ffc000070fc0000407c0000007e0000007c000000fc000001fc000003f8000007f0000007e000000fc000000fc000000f80000000000000000000000f8000000f8000000f8000000f8000000f80000000000000000000000000000000000000000000
U+0040 000000000000000000000000000ff000003ffe0000ffff8001f81fc003e003e0078001e0070000f00f07dc700e1ffc381c1ffc381c3e7c381c3c3c381c381c381c381c381c3c3c701c3e7cf01c1fffe00e1fffc00e07df00070000000780020003e0070001f81f0000ffff00003ffc00000ff000000000000000000000000000
U+0041 0000000000000000000000000000000000000000000fe000000ff000001ff000001ff000003ff800003ff800003ef800007efc00007e7c00007c7e0000fc7e0000fc3e0000f83f0001f83f0001ffff0003ffff8003ffff8003ffffc007e00fc007e00fc007c007e00fc007e00000000000000000000000000000000000000000
U+0042 000000000000000000000000000000000000000001fff00001fffc0001fffe0001fffe0001f07f0001f03f0001f03f0001f03f0001f07e0001fffe0001fffc0001fffe0001ffff0001f03f0001f01f8001f01f8001f01f8001f03f8001ffff0001ffff0001fffe0001fff8000000000000000000000000000000000000000000
U+0043 00000000000000000000000000000000000000000003fe00000fff80003fff80007fff8000ff038000fe008001fc000001f8000001f8000001f8000003f0000003f0000001f8000001f8000001f8000001fc000000fe008000ff0380007fff80003fff80000fff800003fe000000000000000000000000000000000000000000
U+0044 000000000000000000000000000000000000000003ffe00003fff80003fffe0003ffff0003e0ff8003e03f8003e01fc003e00fc003e00fc003e00fc003e00fc003e00fc003e00fc003e00fc003e00fc003e01fc003e03f8003e0ff8003ffff0003fffe0003fff80003ffe0000000000000000000000000000000000000000000
U+0045 000000000000000000000000000000000000000000fffe0000fffe0000fffe0000fffe0000f8000000f8000000f8000000f8000000f8000000fffe0000fffe0000fffe0000fffe0000f8000000f8000000f8000000f8000000f8000000fffe0000fffe0000fffe0000fffe000000000000000000000000000000000000000000
U+0046 000000000000000000000000000000000000000000fffe0000fffe0000fffe0000fffe0000f8000000f8000000f8000000f8000000f8000000fffe0000fffe0000fffe0000fffe0000f8000000f8000000f8000000f8000000f8000000f8000000f8000000f8000000f800000000000000000000000000000000000000000000
U+0047 0000000000000000000000000000000000000000000ffc00003fff0000ffff8001ffff8003fe0f8003f8018007f0000007e0000007e0000007e000000fc07fc00fc07fc007e07fc007e07fc007e00fc007f00fc003f80fc003fc0fc001ffffc000ffffc0003fff00000ff8000000000000000000000000000000000000000000
U+0048 000000000000000000000000000000000000000003e00f8003e00f8003e00f8003e00f8003e00f8003e00f8003e00f8003e00f8003e00f8003ffff8003ffff8003ffff8003ffff8003e00f8003e00f8003e00f8003e00f8003e00f8003e00f8003e00f8003e00f8003e00f800000000000000000000000000000000000000000
U+0049 00000000000000000000000000000000000000000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000000000000000000000000000000000000000000
U+004A 00000000000000000003e0000003e0000003e0000003e0000003e0000003e0000003e0000003e0000003e0000003e0000003e0000003e0000003e0000003e0000003e0000003e0000003e0000003e0000003e0000003e0000003e0000007e0000007e000000fe000007fc000007fc000007f8000007e00000000000000000000
U+004B 000000000000000000000000000000000000000003e01fc003e03f8003e07f0003e0fe0003e1fc0003e3f80003e7f00003ffe00003ffc00003ff800003ff000003ff800003ffc00003ffe00003eff00003e7f80003e3fc0003e1fe0003e0ff0003e07f8003e03fc003e01fe00000000000000000000000000000000000000000
U+004C 0000000000000000000000000000000000000000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007fff00007fff00007fff00007fff000000000000000000000000000000000000000000
U+004D 00000000000000000000000000000000000000000fe007f00ff00ff00ff00ff00ff81ff00ff81ff00ff83ff00ffc3ff00fbc3df00fbe7df00fbe79f00f9ef9f00f9ff9f00f8ff1f00f8ff1f00f87e1f00f87e1f00f87c1f00f83c1f00f8001f00f8001f00f8001f00f8001f00000000000000000000000000000000000000000
U+004E 000000000000000000000000000000000000000003f00f8003f80f8003f80f8003fc0f8003fe0f8003fe0f8003ff0f8003ff0f8003ef8f8003ef8f8003e7cf8003e7cf8003e3ef8003e3ef8003e1ff8003e0ff8003e0ff8003e07f8003e07f8003e03f8003e03f8003e01f800000000000000000000000000000000000000000
U+004F 0000000000000000000000000000000000000000000ff000007ffc0000ffff0001ffff8003fc3f8003f01fc007e00fc007e007e007e007e007e007e00fc007e00fc007e007e007e007e007e007e007e007e00fc003f01fc003fc3f8001ffff8000ffff00007ffc00000ff0000000000000000000000000000000000000000000
U+0050 000000000000000000000000000000000000000000fff80000fffe0000ffff0000ffff8000f83f8000f81fc000f80fc000f80fc000f81fc000f83f8000ffff8000ffff0000fffe0000fff80000f8000000f8000000f8000000f8000000f8000000f8000000f8000000f800000000000000000000000000000000000000000000
U+0051 000000000000000000000000000ff000007ffc0000ffff0001ffff8003fc3f8003f01fc007e00fc007e007e007e007e007e007e00fc007e00fc007e007e007e007e007e007e007e007e00fc003f01fc003fc3f8001ffff8000ffff00007ffc00000ff80000007c0000003e0000003f0000001f80000000000000000000000000
U+0052 000000000000000000000000000000000000000001fff00001fffc0001fffe0001fffe0001f07f0001f03f0001f03f0001f03f0001f03e0001f07e0001fffc0001fff80001fff80001fffc0001f0fe0001f07e0001f03f0001f03f0001f01f8001f01f8001f00fc001f00fc00000000000000000000000000000000000000000
U+0053 0000000000000000000000000000000000000000001ff800007ffe0000fffe0000fffe0001fc1e0001f8020001f0000001f8000001fe000000fff00000fffc00007ffe00001fff000001ff0000003f0000001f0001801f0001f03f0001ffff0001fffe0000fffc00001ff0000000000000000000000000000000000000000000
U+0054 000000000000000000000000000000000000000007ffff8007ffff8007ffff8007ffff80000fc000000fc000000fc000000fc000000fc000000fc000000fc000000fc000000fc000000fc000000fc000000fc000000fc000000fc000000fc000000fc000000fc000000fc0000000000000000000000000000000000000000000
U+0055 000000000000000000000000000000000000000001f00fc001f00fc001f00fc001f00fc001f00fc001f00fc001f00fc001f00fc001f00fc001f00fc001f00fc001f00fc001f00fc001f80fc001f80fc001f80f8001f81f8001fc3f8000ffff00007fff00003ffc00000ff0000000000000000000000000000000000000000000
U+0056 00000000000000000000000000000000000000000fc007e007c007e007e00fc007e00fc003f00fc003f01f8003f01f8001f81f0001f83f0000f83f0000fc3e0000fc7e00007c7e00007efc00007efc00003ff800003ff800003ff800001ff000001ff000000ff000000fe0000000000000000000000000000000000000000000
U+0057 00000000000000000000000000000000000000007c07e03e7e07e07e7e07e07e3e0ff07c3e0ff07c3f0ff0fc3f0ff0fc1f1ef8f81f1e78f81f1e78f81f9e79f80f9e79f00fbc3df00fbc3df00ffc3ff00ffc3ff007f81fe007f81fe007f81fe007f81fe003f00fc0000000000000000000000000000000000000000000000000
U+0058 000000000000000000000000000000000000000007e00fc003f01f8003f81f8001f83f0000fc7e0000fe7e00007efc00003ff800001ff800001ff000000fe000000ff000001ff000003ff800003ffc00007efc0000fc7e0000fc7f0001f83f0003f01f8007f00fc007e00fc00000000000000000000000000000000000000000
U+0059 000000000000000000000000000000000000000007e00fe003f00fc003f81f8001f81f8000fc3f0000fc7f00007e7e00003ffc00003ffc00001ff800001ff000000ff0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000000000000000000000000000000000000000000
U+005A 000000000000000000000000000000000000000001ffff8001ffff8001ffff8001ffff8000003f0000007f000000fe000001fc000003f8000003f0000007e000000fe000001fc000003f8000007f0000007e000000fe000001fc000003ffffc003ffffc003ffffc003ffffc00000000000000000000000000000000000000000
U+005B 0000000000000000001ff800001ff800001ff800001f8000001f8000001f8000001f8000001f8000001f8000001f8000001f8000001f8000001f8000001f8000001f8000001f8000001f8000001f8000001f8000001f8000001f8000001f8000001f8000001f8000001ff800001ff800001ff800000000000000000000000000
U+005C 00000000000000000000000000380000003c0000001c0000001c0000001e0000000e0000000e0000000f000000070000000700000007800000078000000380000003c0000003c0000001c0000001c0000001e0000000e0000000e0000000f0000000700000007000000078000000780000000000000000000000000000000000
U+005D 0000000000000000001ff000001ff000001ff0000001f0000001f0000001f0000001f0000001f0000001f0000001f0000001f0000001f0000001f0000001f0000001f0000001f0000001f0000001f0000001f0000001f0000001f0000001f0000001f0000001f000001ff000001ff000001ff000000000000000000000000000
U+005E 00000000000000000000000000000000000000000007c000000fe000001ff000003ff800007e7c0000f83e0001f01f0003c0078000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
U+005F 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000fffe0000fffe0000fffe0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
U+0060 00000000000000000000000000000000003c0000001e0000000e0000000f0000000780000003800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
U+0061 0000000000000000000000000000000000000000000000000000000000000000007ff000007ffc00007ffe0000607f0000003f00001fff00007fff0000ffff0000fc3f0001f83f0001f83f0001f83f0000fc7f0000ffff00007fbf00003f3f000000000000000000000000000000000000000000000000000000000000000000
U+0062 0000000000000000000000000000000001f8000001f8000001f8000001f8000001f8000001f8000001f8000001f8f80001fbfe0001fffe0001fe3f0001fc1f8001f81f8001f81f8001f80f8001f80f8001f81f8001f81f8001fc1f8001fe3f0001fffe0001fbfe0001f9f8000000000000000000000000000000000000000000
U+0063 00000000000000000000000000000000000000000000000000000000000000000003f800000ffe00003ffe00007f0e00007e0200007c000000fc000000fc000000fc000000fc0000007c0000007e0200007f0e00003ffe00000ffe000003f8000000000000000000000000000000000000000000000000000000000000000000
U+0064 0000000000000000000000000000000000001f0000001f0000001f0000001f0000001f0000001f0000001f00003f1f00007f9f0000ffff0001fc7f0001f83f0001f03f0003f03f0003f01f0003f01f0003f03f0001f03f0001f83f0001fc7f0000ffff00007f9f00003f1f000000000000000000000000000000000000000000
U+0065 0000000000000000000000000000000000000000000000000000000000000000000ff000003ffc00007ffe0000fe3f0000fc1f0000f81f8001f81f8001ffff8001ffff8001ffff8000f8000000f8010000fe0f00007fff00003fff000007fc000000000000000000000000000000000000000000000000000000000000000000
U+0066 000000000000000000000000000000000001fc000007fc000007fc00000fc000000fc000000fc000000fc000007ffc00007ffc00007ffc00000fc000000fc000000fc000000fc000000fc000000fc000000fc000000fc000000fc000000fc000000fc000000fc000000fc0000000000000000000000000000000000000000000
U+0067 0000000000000000000000000000000000000000001f1f00007f9f0000ffff0001fc7f0001f83f0001f03f0003f03f0003f01f0003f01f0003f03f0001f03f0001f83f0001fc7f0000ffff00007f9f00001f3f0000003f0000803e0000e0fe0000fffc0000fff800003fe0000000000000000000000000000000000000000000
U+0068 0000000000000000000000000000000001f8000001f8000001f8000001f8000001f8000001f8000001f8000001f8f80001fbfe0001fffe0001fe3f0001fc3f0001f81f0001f81f0001f81f0001f81f0001f81f0001f81f0001f81f0001f81f0001f81f0001f81f0001f81f000000000000000000000000000000000000000000
U+0069 000000000000000000000000000000000007e0000007e0000007e0000007e0000007e00000000000000000000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000000000000000000000000000000000000000000
U+006A 000000000007e0000007e0000007e0000007e0000007e00000000000000000000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007c000003fc000003f8000003f00000000000000000000
U+006B 0000000000000000000000000000000001f8000001f8000001f8000001f8000001f8000001f8000001f8000001f83f0001f87e0001f8fc0001f9f80001fbf00001ffe00001ffc00001ff800001ffc00001ffe00001fbf00001f9f80001f8fc0001f87e0001f83f0001f81f800000000000000000000000000000000000000000
U+006C 000000000000000000000000000000000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000007e0000000000000000000000000000000000000000000
U+006D 00000000000000000000000000000000000000000000000000000000000000003f3e0fc03f7f9fe03ffffff03fcff1f83f87e1f83f07e1f83f07e0f83f07c0f83f07c0f83f07c0f83f07c0f83f07c0f83f07c0f83f07c0f83f07c0f83f07c0f80000000000000000000000000000000000000000000000000000000000000000
U+006E 000000000000000000000000000000000000000000000000000000000000000001f8f80001fbfe0001fffe0001fe3f0001fc3f0001f81f0001f81f0001f81f0001f81f0001f81f0001f81f0001f81f0001f81f0001f81f0001f81f0001f81f000000000000000000000000000000000000000000000000000000000000000000
U+006F 0000000000000000000000000000000000000000000000000000000000000000001fe000007ff80000fffc0001fc7e0001f83f0001f03f0003f01f0003f01f0003f01f0003f01f0001f03f0001f83f0001fc7e0000fffc00007ff800001fe0000000000000000000000000000000000000000000000000000000000000000000
U+0070 000000000000000000000000000000000000000001f8f80001fbfe0001fffe0001fe3f0001fc1f8001f81f8001f81f8001f80f8001f80f8001f81f8001f81f8001fc1f8001fe3f0001fffe0001fbfe0001f9f80001f8000001f8000001f8000001f8000001f8000001f800000000000000000000000000000000000000000000
U+0071 0000000000000000000000000000000000000000003f1f00007f9f0000ffff0001fc7f0001f83f0001f03f0003f03f0003f01f0003f01f0003f03f0001f03f0001f83f0001fc7f0000ffff00007f9f00003f1f0000001f0000001f0000001f0000001f0000001f0000001f000000000000000000000000000000000000000000
U+0072 0000000000000000000000000000000000000000000000000000000000000000003f3e00003f7e00003ffe00003ffe00003fc200003f8000003f0000003f0000003f0000003f0000003f0000003f0000003f0000003f0000003f0000003f00000000000000000000000000000000000000000000000000000000000000000000
U+0073 0000000000000000000000000000000000000000000000000000000000000000000ff800003ffc00007ffc00007c1c0000f80400007c0000007fc000007ff800001ffe000003fe0000003e0000403f0000707e00007ffe00007ffc00001ff0000000000000000000000000000000000000000000000000000000000000000000
U+0074 0000000000000000000000000000000000000000000f8000000f8000000f8000000f8000000f8000007ffe00007ffe00007ffe00000f8000000f8000000f8000000f8000000f8000000f8000000f8000000f8000000f8000000fc000000ffc000007fc000003fc00000000000000000000000000000000000000000000000000
U+0075 000000000000000000000000000000000000000000000000000000000000000001f83f0001f83f0001f83f0001f83f0001f83f0001f83f0001f83f0001f83f0001f83f0001f83f0001f83f0001f83f0000fc7f0000ffff00007fbf00003f3f000000000000000000000000000000000000000000000000000000000000000000
U+0076 000000000000000000000000000000000000000000000000000000000000000001f00f8001f01f8001f81f0000f83f0000f83e00007c3e00007c7e00007e7c00003e7c00003ef800001ff800001ff800001ff000000ff000000fe0000007e0000000000000000000000000000000000000000000000000000000000000000000
U+0077 00000000000000000000000000000000000000000000000000000000000000001f07c1f81f87e1f00f87e1f00f87e1f00f8fe3f00fcff3e007cff3e007cef3e007de77c003fe7fc003fe7fc003fc7fc003fc3f8001fc3f8001fc3f8001f83f800000000000000000000000000000000000000000000000000000000000000000
U+0078 000000000000000000000000000000000000000000000000000000000000000001f81f0000f83f00007c7e00007efc00003ff800001ff800000ff000000fe000000fe000001ff000001ff800003efc00007e7c0000fc7e0001f83f0001f01f800000000000000000000000000000000000000000000000000000000000000000
U+0079 000000000000000000000000000000000000000003f01f8001f01f8001f81f0000f83f0000fc3e00007c3e00007c7e00003e7c00003e7c00003ff800001ff800001ff800000ff000000ff0000007e0000007e0000007e0000007c000000fc000007f8000007f0000007e00000000000000000000000000000000000000000000
U+007A 0000000000000000000000000000000000000000000000000000000000000000007ffe00007ffe00007ffe000000fe000001fc000001fc000003f8000007f000000fe000001fc000003f8000007f000000fe000000fffe0000fffe0000fffe000000000000000000000000000000000000000000000000000000000000000000
U+007B 00000000000000000000fe000003fe000003fe000007e0000007e0000007c0000007c0000007c0000007c0000007c0000007c0000007c000000fc000007f8000007f0000007f8000000fc0000007c0000007c0000007c0000007c0000007c0000007c0000007e0000007e0000003fe000003fe000000fe000000000000000000
U+007C 0000000000038000000380000003800000038000000380000003800000038000000380000003800000038000000380000003800000038000000380000003800000038000000380000003800000038000000380000003800000038000000380000003800000038000000380000003800000038000000380000003800000000000
U+007D 0000000000000000007e0000007f8000007fc000000fc0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007e0000007f0000003fe000001fe000003fe000007f0000007e0000007c0000007c0000007c0000007c0000007c0000007c000000fc000007fc000007f8000007e00000000000000000000
U+007E 00000000000000000000000000000000000000000000000000000000000000000000000000000000007e008001ffc38003ffff800383ff000200fc000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
U+0410 0000000000000000000000000000000000000000000fe000000ff000001ff000001ff000003ff800003ff800003ef800007efc00007e7c00007c7e0000fc7e0000fc3e0000f83f0001f83f0001ffff0003ffff8003ffff8003ffffc007e00fc007e00fc007c007e00fc007e00000000000000000000000000000000000000000
U+0411 000000000000000000000000000000000000000001fffe0001fffe0001fffe0001fffe0001f0000001f0000001f0000001f0000001f0000001fff00001fffc0001ffff0001ffff0001f03f8001f01f8001f01f8001f01f8001f03f8001ffff0001ffff0001fffc0001fff0000000000000000000000000000000000000000000
U+0412 000000000000000000000000000000000000000001fff00001fffc0001fffe0001fffe0001f07f0001f03f0001f03f0001f03f0001f07e0001fffe0001fffc0001fffe0001ffff0001f03f0001f01f8001f01f8001f01f8001f03f8001ffff0001ffff0001fffe0001fff8000000000000000000000000000000000000000000
U+0413 0000000000000000000000000000000000000000007fff00007fff00007fff00007fff00007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c00000000000000000000000000000000000000000000
U+0414 000000000000000000ffff0000ffff0000ffff0000ffff0000fc3f0000fc3f0000fc3f0000fc3f0000fc3f0000f83f0000f83f0000f83f0000f83f0000f83f0001f83f0001f83f0001f83f0003f03f000fffffe00fffffe00fffffe00fffffe00f0001e00f0001e00f0001e00f0001e00f0001e0000000000000000000000000
U+0415 000000000000000000000000000000000000000000fffe0000fffe0000fffe0000fffe0000f8000000f8000000f8000000f8000000f8000000fffe0000fffe0000fffe0000fffe0000f8000000f8000000f8000000f8000000f8000000fffe0000fffe0000fffe0000fffe000000000000000000000000000000000000000000
U+0416 0000000000000000000000000000000000000000000000003e07c07c3f07c0f81f87c1f00fc7c3f007e7c7e003e7cfc001f7df8000ffff0001ffff0001ffff8003ffffc007eff7c007cfe3e00fc7e3f01f87c1f01f07c0f83f07c0fc7e07c07e7c07c03e00000000000000000000000000000000000000000000000000000000
U+0417 0000000000000000000000000000000000000000007fe00001fffc0001fffe0001fffe0001c0ff0000003f0000003f0000003f0000007e00001ffc00001ff800001ffc00001ffe0000007f0000003f0000001f0001003f0001e07f0001ffff0001fffe0000fffc00003fe0000000000000000000000000000000000000000000
U+0418 000000000000000000000000000000000000000003e01f8003e03f8003e03f8003e07f8003e07f8003e0ff8003e1ff8003e1ff8003e3ef8003e3ef8003e7cf8003e7cf8003ef8f8003ef8f8003ff0f8003ff0f8003fe0f8003fe0f8003fc0f8003f80f8003f80f8003f00f800000000000000000000000000000000000000000
U+0419 000000000000000000383000003c7000001fe000000fc0000000000003e01f8003e03f8003e03f8003e07f8003e07f8003e0ff8003e1ff8003e1ff8003e3ef8003e3ef8003e7cf8003e7cf8003ef8f8003ef8f8003ff0f8003ff0f8003fe0f8003fe0f8003fc0f8003f80f8003f80f8003f00f80000000000000000000000000
U+041A 000000000000000000000000000000000000000003e00fc003e01f8003e03f0003e07e0003e0fc0003e1f80003e3f00003e7e00003ffc00003ffc00003ffe00003fff00003fff80003fdf80003f8fc0003f0fe0003e07e0003e03f0003e03f8003e01f8003e00fc003e00fe00000000000000000000000000000000000000000
U+041B 0000000000000000000000000000000000000000007fff80007fff80007fff80007fff80007e1f80007e1f80007e1f80007e1f80007e1f80007e1f80007e1f80007e1f80007e1f80007e1f80007e1f80007c1f8000fc1f8003fc1f800ff81f800ff01f800fe01f800f001f800000000000000000000000000000000000000000
U+041C 00000000000000000000000000000000000000000fe007f00ff00ff00ff00ff00ff81ff00ff81ff00ff83ff00ffc3ff00fbc3df00fbe7df00fbe79f00f9ef9f00f9ff9f00f8ff1f00f8ff1f00f87e1f00f87e1f00f87c1f00f83c1f00f8001f00f8001f00f8001f00f8001f00000000000000000000000000000000000000000
U+041D 000000000000000000000000000000000000000003e00f8003e00f8003e00f8003e00f8003e00f8003e00f8003e00f8003e00f8003e00f8003ffff8003ffff8003ffff8003ffff8003e00f8003e00f8003e00f8003e00f8003e00f8003e00f8003e00f8003e00f8003e00f800000000000000000000000000000000000000000
U+041E 0000000000000000000000000000000000000000000ff000007ffc0000ffff0001ffff8003fc3f8003f01fc007e00fc007e007e007e007e007e007e00fc007e00fc007e007e007e007e007e007e007e007e00fc003f01fc003fc3f8001ffff8000ffff00007ffc00000ff0000000000000000000000000000000000000000000
U+041F 000000000000000000000000000000000000000003ffff8003ffff8003ffff8003ffff8003e00f8003e00f8003e00f8003e00f8003e00f8003e00f8003e00f8003e00f8003e00f8003e00f8003e00f8003e00f8003e00f8003e00f8003e00f8003e00f8003e00f8003e00f800000000000000000000000000000000000000000
U+0420 000000000000000000000000000000000000000000fff80000fffe0000ffff0000ffff8000f83f8000f81fc000f80fc000f80fc000f81fc000f83f8000ffff8000ffff0000fffe0000fff80000f8000000f8000000f8000000f8000000f8000000f8000000f8000000f800000000000000000000000000000000000000000000
U+0421 00000000000000000000000000000000000000000003fe00000fff80003fff80007fff8000ff038000fe008001fc000001f8000001f8000001f8000003f0000003f0000001f8000001f8000001f8000001fc000000fe008000ff0380007fff80003fff80000fff800003fe000000000000000000000000000000000000000000
U+0422 000000000000000000000000000000000000000007ffff8007ffff8007ffff8007ffff80000fc000000fc000000fc000000fc000000fc000000fc000000fc000000fc000000fc000000fc000000fc000000fc000000fc000000fc000000fc000000fc000000fc000000fc0000000000000000000000000000000000000000000
U+0423 000000000000000000000000000000000000000007e00fc007f01fc003f01f8003f81f8001f83f0001fc3f0000fc7e0000fc7e00007efc00007ffc00003ff800003ff800001ff000001ff000000ff000000fe0000007e000000fc00000ffc00000ff800000ff000000fc00000000000000000000000000000000000000000000
U+0424 00000000000000000000000000000000000000000007e0000007e000007ffc0003ffff8007ffffe00ffffff01fe7e7f01f87e3f81f87e1f83f87e1f83f07e1f83f87e1f81f87e1f81f87e3f81fe7e7f00ffffff007ffffe003ffff80007ffc000007e0000007e0000007e0000000000000000000000000000000000000000000
U+0425 000000000000000000000000000000000000000007e00fc003f01f8003f81f8001f83f0000fc7e0000fe7e00007efc00003ff800001ff800001ff000000fe000000ff000001ff000003ff800003ffc00007efc0000fc7e0000fc7f0001f83f0003f01f8007f00fc007e00fc00000000000000000000000000000000000000000
U+0426 000000000000000007c01f0007c01f0007c01f0007c01f0007c01f0007c01f0007c01f0007c01f0007c01f0007c01f0007c01f0007c01f0007c01f0007c01f0007c01f0007c01f0007c01f0007c01f0007fffff007fffff007fffff007fffff0000000f0000000f0000000f0000000f0000000f0000000000000000000000000
U+0427 000000000000000000000000000000000000000003f00fc003f00fc003f00fc003f00fc003f00fc003f00fc003f00fc003f00fc001f80fc001ffffc001ffffc000ffffc0007fffc000000fc000000fc000000fc000000fc000000fc000000fc000000fc000000fc000000fc00000000000000000000000000000000000000000
U+0428 0000000000000000000000000000000000000000000000003e03e07c3e03e07c3e03e07c3e03e07c3e03e07c3e03e07c3e03e07c3e03e07c3e03e07c3e03e07c3e03e07c3e03e07c3e03e07c3e03e07c3e03e07c3e03e07c3ffffffc3ffffffc3ffffffc00000000000000000000000000000000000000000000000000000000
U+0429 00000000000000000000000000000000000000003e0f81f03e0f81f03e0f81f03e0f81f03e0f81f03e0f81f03e0f81f03e0f81f03e0f81f03e0f81f03e0f81f03e0f81f03e0f81f03e0f81f03e0f81f03ffffffc3ffffffc3ffffffc0000001c0000001c0000001c0000001c0000000000000000000000000000000000000000
U+042A 00000000000000000000000000000000000000001fff00001fff00001fff00001fff0000003f0000001f0000001f0000001f0000001ffc00001fffc0001fffe0001ffff0001ffff0001f03f8001f01f8001f01f8001f01f8001f03f0001ffff0001fffe0001fffc0001fff000000000000000000000000000000000000000000
U+042B 00000000000000000000000000000000000000001f0001f01f0001f01f0001f01f0001f01f0001f01f0001f01f0001f01f0001f01fff01f01fffc1f01fffe1f01ffff1f01f03f1f01f01f9f01f01f9f01f01f9f01f01f9f01f03f1f01ffff1f01fffe1f01fffc1f01fff01f00000000000000000000000000000000000000000
U+042C 000000000000000000000000000000000000000001f0000001f0000001f0000001f0000001f0000001f0000001f0000001f0000001fff00001fffc0001fffe0001ffff0001f03f0001f01f8001f01f8001f01f8001f01f8001f03f0001ffff0001fffe0001fffc0001fff0000000000000000000000000000000000000000000
U+042D 0000000000000000000000000000000000000000007fe00001fff80001fffc0001fffe0001c0ff0001003f0000003f8000001f8000001f80003fff80003fffc0003fffc0003fffc000001f8000001f8000003f8000003f000180ff0001fffe0001fffc0001fff80000ffe0000004000000000000000000000000000000000000
U+042E 0000000000000000000000000000000000000000000000003f00ff003f03ffc03f07ffe03f0fc3f03f1f81f83f1f00f83f3f00fc3f3f007c3ffe007c3ffe007c3ffe007c3f3e007c3f3f007c3f1f00fc3f1f00f83f1f81f83f0fc3f03f07ffe03f03ffc03f00ff00000000000000000000000000000000000000000000000000
U+042F 0000000000000000000000000000000000000000001fff00007fff0000ffff0001fc1f0001f81f0001f81f0001f81f0001f81f0001f81f0000f81f00007c1f00003fff00001fff00001fff00003f9f00003f1f00007e1f0000fe1f0000fc1f0001fc1f0001f81f0003f01f000000000000000000000000000000000000000000
U+0430 0000000000000000000000000000000000000000000000000000000000000000007ff000007ffc00007ffe0000607f0000003f00001fff00007fff0000ffff0000fc3f0001f83f0001f83f0001f83f0000fc7f0000ffff00007fbf00003f3f000000000000000000000000000000000000000000000000000000000000000000
U+0431 00000000000000000000000000000000000000000003fc00003ffc00007ffc0000fc000001f0000001e0000001e0000003cff00003fffc0003fffe0003fc7f0003f83f0003f81f0003f01f8001f01f8001f01f8001f01f8001f81f0001f83f0000fc7f00007ffe00003ffc00000ff00000000000000000000000000000000000
U+0432 000000000000000000000000000000000000000000000000000000000000000000fff00000fffc0000fffe0000fc3e0000fc3e0000fc3e0000fffc0000fff80000fffe0000fc3e0000fc1f0000fc1f0000fc3f0000fffe0000fffe0000fff8000000000000000000000000000000000000000000000000000000000000000000
U+0433 0000000000000000000000000000000000000000000000000000000000000000003ffe00003ffe00003ffe00003f0000003f0000003f0000003f0000003f0000003f0000003f0000003f0000003f0000003f0000003f0000003f0000003f00000000000000000000000000000000000000000000000000000000000000000000
U+0434 000000000000000000000000000000000000000000000000003fff00003fff00003fff00003e3f00003e3f00007e3f00007e3f00007e3f00007e3f00007e3f00007c3f0000fc3f0001fc3f0003ffffe003ffffe003ffffe003c001e003c001e003c001e003c001e0000000000000000000000000000000000000000000000000
U+0435 0000000000000000000000000000000000000000000000000000000000000000000ff000003ffc00007ffe0000fe3f0000fc1f0000f81f8001f81f8001ffff8001ffff8001ffff8000f8000000f8010000fe0f00007fff00003fff000007fc000000000000000000000000000000000000000000000000000000000000000000
U+0436 00000000000000000000000000000000000000000000000000000000000000003f07e1f81f87e3f007c7e7e003e7efc001f7ff8000ffff00007ffe0000ffff0001ffff8003ffff8003e7e7c007c7e7e00fc7e3f01f87e1f81f07e0f83e07e07c0000000000000000000000000000000000000000000000000000000000000000
U+0437 0000000000000000000000000000000000000000000000000000000000000000001ff000007ff800007ffc000070fc0000407c000000fc00001ff800001ff000001ff8000000fc0000007e0000c07e0000f0fc0000fffc0000fff800003fe0000000000000000000000000000000000000000000000000000000000000000000
U+0438 000000000000000000000000000000000000000000000000000000000000000001f83f0001f87f0001f8ff0001f8ff0001f9ff0001f9ff0001fbff0001ffff0001ffff0001ffbf0001ff3f0001ff3f0001fe3f0001fe3f0001fc3f0001f83f000000000000000000000000000000000000000000000000000000000000000000
U+0439 0000000000000000000000000000000000183000001c7000001ff0000007c00000000000000000000000000001f83f0001f87f0001f8ff0001f8ff0001f9ff0001f9ff0001fbff0001ffff0001ffff0001ffbf0001ff3f0001ff3f0001fe3f0001fe3f0001fc3f0001f83f000000000000000000000000000000000000000000
U+043A 000000000000000000000000000000000000000000000000000000000000000000fc1f8000fc3f0000fc7e0000fcfc0000fdf80000fff00000ffe00000ffe00000fff00000fff80000fcfc0000fc7c0000fc3e0000fc3f0000fc1f8000fc0fc00000000000000000000000000000000000000000000000000000000000000000
U+043B 0000000000000000000000000000000000000000000000000000000000000000003fff80003fff80003fff80003f1f80003f1f80003f1f80003f1f80003e1f80003e1f80003e1f80003e1f80007e1f8000fc1f8001fc1f8001f01f8001c01f800000000000000000000000000000000000000000000000000000000000000000
U+043C 000000000000000000000000000000000000000000000000000000000000000007f01f8007f03f8007f83f8007f87f8007fc7f8007fcff8007feff8007ffff8007ffef8007efef8007efcf8007e7cf8007e78f8007e00f8007e00f8007e00f800000000000000000000000000000000000000000000000000000000000000000
U+043D 000000000000000000000000000000000000000000000000000000000000000001f83e0001f83e0001f83e0001f83e0001f83e0001f83e0001fffe0001fffe0001fffe0001f83e0001f83e0001f83e0001f83e0001f83e0001f83e0001f83e000000000000000000000000000000000000000000000000000000000000000000
U+043E 0000000000000000000000000000000000000000000000000000000000000000001fe000007ff80000fffc0001fc7e0001f83f0001f03f0003f01f0003f01f0003f01f0003f01f0001f03f0001f83f0001fc7e0000fffc00007ff800001fe0000000000000000000000000000000000000000000000000000000000000000000
U+043F 000000000000000000000000000000000000000000000000000000000000000001fffe0001fffe0001fffe0001f83e0001f83e0001f83e0001f83e0001f83e0001f83e0001f83e0001f83e0001f83e0001f83e0001f83e0001f83e0001f83e000000000000000000000000000000000000000000000000000000000000000000
U+0440 000000000000000000000000000000000000000001f8f80001fbfe0001fffe0001fe3f0001fc1f8001f81f8001f81f8001f80f8001f80f8001f81f8001f81f8001fc1f8001fe3f0001fffe0001fbfe0001f9f80001f8000001f8000001f8000001f8000001f8000001f800000000000000000000000000000000000000000000
U+0441 00000000000000000000000000000000000000000000000000000000000000000003f800000ffe00003ffe00007f0e00007e0200007c000000fc000000fc000000fc000000fc0000007c0000007e0200007f0e00003ffe00000ffe000003f8000000000000000000000000000000000000000000000000000000000000000000
U+0442 000000000000000000000000000000000000000000000000000000000000000001ffff0001ffff0001ffff000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000007c0000000000000000000000000000000000000000000000000000000000000000000
U+0443 000000000000000000000000000000000000000003f01f8001f01f8001f81f0000f83f0000fc3e00007c3e00007c7e00003e7c00003e7c00003ff800001ff800001ff800000ff000000ff0000007e0000007e0000007e0000007c000000fc000007f8000007f0000007e00000000000000000000000000000000000000000000
U+0444 000000000007e0000007e0000007e0000007e0000007e0000007e0000007e00001e7ef8007f7ffc00fffffe00fcfe3f01f87e1f81f87e1f81f07e1f81f07e0f81f07e0f81f07e1f81f87e1f81f87e1f80fcfe3f00fffffe007f7ffc001e7ef800007e0000007e0000007e0000007e0000007e0000007e0000000000000000000
U+0445 000000000000000000000000000000000000000000000000000000000000000001f81f0000f83f00007c7e00007efc00003ff800001ff800000ff000000fe000000fe000001ff000001ff800003efc00007e7c0000fc7e0001f83f0001f01f800000000000000000000000000000000000000000000000000000000000000000
U+0446 00000000000000000000000000000000000000000000000001f83e0001f83e0001f83e0001f83e0001f83e0001f83e0001f83e0001f83e0001f83e0001f83e0001f83e0001f83e0001f83e0001ffffc001ffffc001ffffc0000003c0000003c0000003c0000003c0000000000000000000000000000000000000000000000000
U+0447 000000000000000000000000000000000000000000000000000000000000000001f07c0001f07c0001f07c0001f07c0001f07c0001f87c0001fffc0000fffc00007ffc0000007c0000007c0000007c0000007c0000007c0000007c0000007c000000000000000000000000000000000000000000000000000000000000000000
U+0448 00000000000000000000000000000000000000000000000000000000000000003f07e0f83f07e0f83f07e0f83f07e0f83f07e0f83f07e0f83f07e0f83f07e0f83f07e0f83f07e0f83f07e0f83f07e0f83f07e0f83ffffff83ffffff83ffffff80000000000000000000000000000000000000000000000000000000000000000
U+0449 0000000000000000000000000000000000000000000000003f07c1f03f07c1f03f07c1f03f07c1f03f07c1f03f07c1f03f07c1f03f07c1f03f07c1f03f07c1f03f07c1f03f07c1f03f07c1f03ffffffe3ffffffe3ffffffe0000001e0000001e0000001e0000001e000000000000000000000000000000000000000000000000
U+044A 0000000000000000000000000000000000000000000000000000000007fe00000fff00000fff000007ff0000003f0000003f0000003f0000003ffe00003fff00003fff80003f0f80003f0f80003f0f80003f1f80003fff80003fff00003ffc000000000000000000000000000000000000000000000000000000000000000000
U+044B 00000000000000000000000000000000000000000000000000000000000000000fc007e00fc007e00fc007e00fc007e00fc007e00fc007e00fff87e00fffc7e00fffe7e00fc3f7e00fc1f7e00fc1f7e00fc3f7e00fffe7e00fffc7e00fff87e00000000000000000000000000000000000000000000000000000000000000000
U+044C 000000000000000000000000000000000000000000000000000000000000000000fc000000fc000000fc000000fc000000fc000000fc000000fff80000fffc0000fffe0000fc3f0000fc1f0000fc1f0000fc3f0000fffe0000fffc0000fff8000000000000000000000000000000000000000000000000000000000000000000
U+044D 00000000000000000000000000000000000000000000000000000000001f8000007ff000007ff800007ffc000060fe0000007e0000007e00001ffe00001fff00001fff0000007e0000007e0000407e000073fc00007ffc00007ff800007fe0000000000000000000000000000000000000000000000000000000000000000000
U+044E 00000000000000000000000000000000000000000000000000000000000000001f80ff001f83ffc01f87ffe01f8fc7f01f9f83f01f9f81f81fbf01f81fff01f81fff01f81fff01f81f9f81f81f9f83f01f8fc7f01f87ffe01f83ffc01f80ff000000000000000000000000000000000000000000000000000000000000000000
U+044F 0000000000000000000000000000000000000000000000000000000000000000001ffe00007ffe0000fffe0000fc7e0000f87e0000f87e00007c7e00007ffe00003ffe00001ffe00003f7e00003e7e00007c7e0000fc7e0000f87e0001f07e000000000000000000000000000000000000000000000000000000000000000000
U+0401 0000000000000000003cf000003cf000003cf000003cf000000000000000000000fffe0000fffe0000fffe0000fffe0000f8000000f8000000f8000000f8000000f8000000fffe0000fffe0000fffe0000fffe0000f8000000f8000000f8000000f8000000f8000000fffe0000fffe0000fffe0000fffe000000000000000000
U+0451 00000000000000000000000000000000000e7800000e7800000e7800000e7800000000000000000000000000000ff000003ffc00007ffe0000fe3f0000fc1f0000f81f8001f81f8001ffff8001ffff8001ffff8000f8000000f8010000fe0f00007fff00003fff000007fc000000000000000000000000000000000000000000
U+00B7 0000000000000000000000000000000000000000000000000000000000000000000000000007c0000007c0000007c0000007c0000007c0000007c0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
U+00D7 000000000000000000000000000000000000000000000000000000000040060000e00f0001f01f0000f83f00007c7e00003efc00001ff800000ff000000fe0000007e000000ff000001ff800003efc00007c7e0000f83f0001f01f0000e00f000040060000000000000000000000000000000000000000000000000000000000
U+00B1 000000000000000000000000000000000000000000000000000380000003800000038000000380000003800003ffff8003ffff8003ffff80000380000003800000038000000380000003800000000000000000000000000003ffff8003ffff8003ffff8000000000000000000000000000000000000000000000000000000000
U+2192 000000000000000000000000000000000000000000000000000000000000000000000c0000001e0000001f0000000f80000007c007ffffe007ffffe007ffffe0000007c000000f8000001f0000001e0000000c000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
U+2248 000000000000000000000000000000000000000000000000000000000000000000000000007e008001ffc38003ffff800383ff000300fc0000000000007e008001ffc38003ffff800383ff000200fc00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
U+2264 000000000000000000000000000000000000000000000000000000000000018000001f800001ff80001fff8001fff80003ff800003f8000003ff800001fff800001fff800001ff8000001f80000001800000000003ffff8003ffff8003ffff800000000000000000000000000000000000000000000000000000000000000000
U+2265 000000000000000000000000000000000000000000000000000000000380000003f0000003ff000003fff000003fff000003ff8000003f800001ff80003fff0003fff00003ff000003f00000038000000000000003ffff8003ffff8003ffff800000000000000000000000000000000000000000000000000000000000000000
U+221A 0000000000000000000000000000038000000780000007000000060000000e0000000e0000001c0000001c0000001800000038000020380001f0300003f07000037870000078e0000078e000003ce000003dc000001dc000001f8000001f8000000f8000000f0000000f00000007000000060000000000000000000000000000
U+0394 0000000000000000000000000000000000000000000fe000000ff000001ff000001ff000003ff800003ff800003ef800007efc00007e7c00007c7e0000fc7e0000fc3e0000f83f0001f83f0001f81f0003f01f8003f01f8003f00fc007ffffc007ffffc007ffffe00fffffe00000000000000000000000000000000000000000
U+03A9 0000000000000000000000000000000000000000000ff000007ffc0000fffe0001ffff8003fc3f8003f01fc007f00fc007e00fe007e007e00fe007e00fc007e00fe007e007e007e007e007e007e00fc003f00fc003f81f8000fc3f000ffc3ff00ffc3ff00ffc3ff00ffc3ff00000000000000000000000000000000000000000
U+03B1 0000000000000000000000000000000000000000000000000000000000000000001fdf00007fff0000fffe0001f8fe0001f0fe0001f07c0003f07c0003f07c0003f0780003f0fc0001f0fc0001f0fc0001f9fe0000ffff00007fff00003fcf000000000000000000000000000000000000000000000000000000000000000000
U+03B2 000000000007e000001ff800003ffc00007c7c0000f83e0000f83e0000f83e0001f83e0001f87c0001f8fc0001fbf00001fbfc0001fbfe0001f87f0001f83f8001f81f8001f81f8001f81f8001fc1f8001fe3f8001ffff0001fbfe0001f9f80001f8000001f8000001f8000001f8000001f8000001f800000000000000000000
U+03C0 000000000000000000000000000000000000000000000000000000000000000007ffffc007ffffc007ffffc000f83e0000f83e0000f83e0000f83e0000f83e0000f83e0000f83e0000f83e0000f83e0000f83f0000f83fc000f83fc000f81fc00000000000000000000000000000000000000000000000000000000000000000
U+2013 00000000000000000000000000000000000000000000000000000000000000000000000000000000003ff800003ff800003ff800003ff800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
U+2014 000000000000000000000000000000000000000000000000000000000000000000000000000000001ffffff81ffffff81ffffff81ffffff8000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
"""

const FONT_CACHE = Dict{Char,Vector{UInt32}}()
const FONT_CACHE_B = Dict{Char,Vector{UInt32}}()

function font_glyph(ch::Char, bold::Bool = false)
    cache = bold ? FONT_CACHE_B : FONT_CACHE
    haskey(cache, ch) && return cache[ch]
    hexs = bold ? FONT_HEX_BOLD : FONT_HEX_REGULAR
    rows = fill(UInt32(0), 32)
    pat = @sprintf("U+%04X ", UInt32(ch))
    idx = findfirst(pat, hexs)
    if idx !== nothing
        start = nextind(hexs, idx[end])
        for r in 0:31
            sub = hexs[nextind(hexs, start, r * 8):nextind(hexs, start, r * 8 + 7)]
            rows[r+1] = UInt32(parse(UInt32, sub, base = 16))
        end
    else
        fb = findfirst("U+003F ", hexs)          # '?' as the fallback glyph
        if fb !== nothing
            st = nextind(hexs, fb[end])
            for r in 0:31
                sub = hexs[nextind(hexs, st, r * 8):nextind(hexs, st, r * 8 + 7)]
                rows[r+1] = UInt32(parse(UInt32, sub, base = 16))
            end
        end
    end
    cache[ch] = rows
    return rows
end

"""
big_text_line(P, str; fg) — headline rendered through the embedded bitmap
font into 8 terminal rows (vertical step 4, horizontal step chosen so the
line fits ~100 columns).  Colored with 256-color background runs.
"""
function big_text_line(P::Palette, str::AbstractString; fg::Int = 220)
    if !P.on
        return ""
    end
    chars = collect(uppercase(str))
    len = length(chars)
    step = len <= 6 ? 2 : (len <= 10 ? 3 : 4)
    samples = 32 ÷ step
    out = IOBuffer()
    for orow in 0:7
        rowi = orow * 4 + 2
        for ch in chars
            g = font_glyph(ch)
            bits = g[rowi]
            for sx in 1:step:32
                on = (bits >> (32 - sx)) & 1 == 1
                if on
                    write(out, "\x1b[48;5;$(fg)m \x1b[0m")
                else
                    write(out, " ")
                end
            end
        end
        write(out, "\n")
    end
    return String(take!(out))
end

# ──────────────────────────────────────────────────────────────────────────────
# PNG ENCODER — pure Julia, zero dependencies.
#   zlib wrapper + deflate with FIXED Huffman codes + greedy LZ77 hash-chain
#   matching + per-row filtering (None / Sub / Up, minimum absolute sum).
#   CRC32 and Adler-32 implemented below as well.
# ──────────────────────────────────────────────────────────────────────────────

const CRC_TBL = let t = Vector{UInt32}(undef, 256)
    for i in 0:255
        c = UInt32(i)
        for _ in 1:8
            c = (c & 0x1 == 0x1) ? (0xEDB88320 ⊻ (c >> 1)) : (c >> 1)
        end
        t[i+1] = c
    end
    t
end

function crc32(data::Vector{UInt8})::UInt32
    c = 0xFFFFFFFF
    @inbounds for b in data
        c = CRC_TBL[((c ⊻ UInt32(b)) & 0xFF) + 1] ⊻ (c >> 8)
    end
    return c ⊻ 0xFFFFFFFF
end

function adler32(data::Vector{UInt8})::UInt32
    a = UInt32(1); b = UInt32(0)
    @inbounds for x in data
        a += x
        a %= 65521
        b += a
        b %= 65521
    end
    return (b << 16) | a
end

mutable struct BitW
    out::Vector{UInt8}
    acc::UInt32
    nb::Int
end
BitW() = BitW(UInt8[], UInt32(0), 0)

putbits!(w::BitW, v::Integer, n::Int) = begin     # LSB-first
    uv = UInt32(v) & ((UInt32(1) << n) - UInt32(1))
    w.acc |= uv << w.nb
    w.nb += n
    while w.nb >= 8
        push!(w.out, UInt8(w.acc & 0xFF))
        w.acc >>= 8
        w.nb -= 8
    end
end

putcode!(w::BitW, code::UInt32, n::Int) = begin   # MSB-first (Huffman codes)
    r = UInt32(0)
    for k in 1:n
        r = (r << 1) | ((code >> (k - 1)) & 1)
    end
    putbits!(w, r, n)
end

flushbits!(w::BitW) = begin
    w.nb > 0 && push!(w.out, UInt8(w.acc & 0xFF))
    w.acc = UInt32(0); w.nb = 0
    return w.out
end

litcode!(w::BitW, v::Int) = begin
    if v < 144
        putcode!(w, UInt32(0x30 + v), 8)
    elseif v < 256
        putcode!(w, UInt32(0x190 + v - 144), 9)
    elseif v < 280
        putcode!(w, UInt32(v - 256), 7)
    else
        putcode!(w, UInt32(0xC0 + v - 280), 8)
    end
end

const LEN_BASE  = [3,4,5,6,7,8,9,10,11,13,15,17,19,23,27,31,35,43,51,59,67,83,99,115,131,163,195,227,258]
const LEN_EXTRA = [0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,0]
const DST_BASE  = [1,2,3,4,5,7,9,13,17,25,33,49,65,97,129,193,257,385,513,769,1025,1537,2049,3073,4097,6145,8193,12289,16385,24577]
const DST_EXTRA = [0,0,0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,13]

function deflate_fixed(data::Vector{UInt8})::Vector{UInt8}
    w = BitW()
    putbits!(w, UInt32(1), 1)                    # BFINAL
    putbits!(w, UInt32(1), 2)                    # BTYPE = 01 fixed Huffman
    N = length(data)
    head = fill(Int32(0), 1 << 15)               # hash heads (0 = none)
    prev = fill(Int32(0), 1 << 15)               # chain, indexed by (pos-1)&0x7FFF
    @inline function lzh(a::UInt8, b::UInt8, c::UInt8)
        x = (UInt32(a) << 16) ⊻ (UInt32(b) << 8) ⊻ UInt32(c)
        return Int((x * 0x9E3779B1) >> 17) & 0x7FFF
    end
    ins!(pos::Int) = begin
        pos + 2 <= N || return nothing
        h = lzh(data[pos], data[pos+1], data[pos+2])
        prev[((pos - 1) & 0x7FFF) + 1] = head[h+1]
        head[h+1] = Int32(pos)
        return nothing
    end
    i = 1
    while i <= N
        best = 0; bdist = 0
        if i + 2 <= N
            h = lzh(data[i], data[i+1], data[i+2])
            j = head[h+1]
            tries = 0
            maxm = min(258, N - i + 1)
            while j != 0 && tries < 24
                d = i - Int(j)
                if 0 < d <= 32768
                    ml = 0
                    @inbounds while ml < maxm && data[Int(j)+ml] == data[i+ml]
                        ml += 1
                    end
                    if ml > best
                        best = ml; bdist = d
                        ml >= maxm && break
                    end
                end
                j = prev[((Int(j) - 1) & 0x7FFF) + 1]
                tries += 1
            end
        end
        if best >= 3
            # length code
            k = 28
            while k >= 1 && best < LEN_BASE[k]; k -= 1; end
            best == 258 && (k = 29)               # the dedicated 258 code
            lc = 256 + k
            litcode!(w, lc)
            LEN_EXTRA[k] > 0 && putbits!(w, UInt32(best - LEN_BASE[k]), LEN_EXTRA[k])
            # distance code
            dk = 30
            while dk >= 2 && bdist < DST_BASE[dk]; dk -= 1; end
            putcode!(w, UInt32(dk - 1), 5)
            DST_EXTRA[dk] > 0 && putbits!(w, UInt32(bdist - DST_BASE[dk]), DST_EXTRA[dk])
            step = best >= 64 ? 4 : 1            # thin insertion on long runs
            for p in i:step:(i + best - 1)
                ins!(p)
            end
            ins!(i + best - 1)
            i += best
        else
            litcode!(w, Int(data[i]))
            ins!(i)
            i += 1
        end
    end
    litcode!(w, 256)                              # end of block
    flushbits!(w)
    return w.out
end

function zlib_compress(data::Vector{UInt8})::Vector{UInt8}
    out = UInt8[0x78, 0x01]
    append!(out, deflate_fixed(data))
    ad = adler32(data)
    push!(out, UInt8((ad >> 24) & 0xFF))
    push!(out, UInt8((ad >> 16) & 0xFF))
    push!(out, UInt8((ad >> 8) & 0xFF))
    push!(out, UInt8(ad & 0xFF))
    return out
end

function png_chunk(out::Vector{UInt8}, typ::String, payload::Vector{UInt8})
    len = UInt32(length(payload))
    append!(out, UInt8[UInt8((len >> 24) & 0xFF), UInt8((len >> 16) & 0xFF),
                       UInt8((len >> 8) & 0xFF), UInt8(len & 0xFF)])
    td = UInt8[]
    append!(td, codeunits(typ))
    append!(td, payload)
    crc = crc32(td)
    append!(out, td)
    append!(out, UInt8[UInt8((crc >> 24) & 0xFF), UInt8((crc >> 16) & 0xFF),
                       UInt8((crc >> 8) & 0xFF), UInt8(crc & 0xFF)])
    return out
end

# rgb: row-major, 3 bytes per pixel, width*height*3
function write_png(path::String, width::Int, height::Int, rgb::Vector{UInt8})
    raw = Vector{UInt8}(undef, (width * 3 + 1) * height)
    stride = width * 3
    prevrow = zeros(UInt8, stride)
    cur = Vector{UInt8}(undef, stride)
    sub = Vector{UInt8}(undef, stride)
    up = Vector{UInt8}(undef, stride)
    for y in 1:height
        off = (y - 1) * stride
        copyto!(cur, 1, rgb, off + 1, stride)
        c0 = 0; c1 = 0; c2 = 0
        @inbounds for x in 1:stride
            v = cur[x]
            l = x > 3 ? cur[x-3] : UInt8(0)
            u = prevrow[x]
            s = v - l; p = v - u
            c0 += abs(reinterpret(Int8, v))
            c1 += abs(reinterpret(Int8, s))
            c2 += abs(reinterpret(Int8, p))
            sub[x] = s; up[x] = p
        end
        best, frow, ftype = c0, cur, UInt8(0)
        if c1 < best
            best = c1; frow = sub; ftype = UInt8(1)
        end
        if c2 < best
            best = c2; frow = up; ftype = UInt8(2)
        end
        ro = (y - 1) * (stride + 1)
        raw[ro+1] = ftype
        copyto!(raw, ro + 2, frow, 1, stride)
        copyto!(prevrow, 1, cur, 1, stride)
    end
    comp = zlib_compress(raw)

    out = UInt8[0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]
    ihdr = Vector{UInt8}(undef, 13)
    w32 = UInt32(width); h32 = UInt32(height)
    ihdr[1] = UInt8((w32 >> 24) & 0xFF); ihdr[2] = UInt8((w32 >> 16) & 0xFF)
    ihdr[3] = UInt8((w32 >> 8) & 0xFF);  ihdr[4] = UInt8(w32 & 0xFF)
    ihdr[5] = UInt8((h32 >> 24) & 0xFF); ihdr[6] = UInt8((h32 >> 16) & 0xFF)
    ihdr[7] = UInt8((h32 >> 8) & 0xFF);  ihdr[8] = UInt8(h32 & 0xFF)
    ihdr[9] = UInt8(8); ihdr[10] = UInt8(2); ihdr[11] = UInt8(0)
    ihdr[12] = UInt8(0); ihdr[13] = UInt8(0)
    png_chunk(out, "IHDR", ihdr)
    png_chunk(out, "IDAT", comp)
    png_chunk(out, "IEND", UInt8[])
    open(path, "w") do f
        write(f, out)
    end
    return path
end

# ──────────────────────────────────────────────────────────────────────────────
# PLOT LAYER — two surfaces with the same primitives:
#   PCanvas  raster RGB (saved as 600-dpi PNG by the built-in encoder)
#   SCtx     SVG vector (saved as .svg)
# Charts are written once and rendered to both surfaces.
# ──────────────────────────────────────────────────────────────────────────────

hexc(s::String) = (parse(Int, s[2:3], base = 16),
                   parse(Int, s[4:5], base = 16),
                   parse(Int, s[6:7], base = 16))

const COL_BG     = "#FBFBF7"
const COL_FG     = "#2A2A28"
const COL_GRID   = "#DDDDD4"
const COL_AXIS   = "#55554E"
const COL_DIM    = "#8B8B82"
const COL_ACCENT = "#C8930A"
const COL_MEAS   = "#2C6BAA"
const COL_REF2   = "#7FA6C8"
const COL_REF4   = "#C4716B"
const COL_DRAW   = "#9A9A92"
const COL_WHITEP = "#E9E5D9"
const COL_BLACKP = "#2B2B2B"
const COL_PATHW  = "#D84315"
const COL_PATHB  = "#00695C"

const VIRIDIS = ["#440154", "#482878", "#3E4A89", "#31688E", "#26828E",
                 "#1F9E89", "#35B779", "#6DCD59", "#B4DE2C", "#FDE725"]

function viridis(t::Float64)
    t = clamp(t, 0.0, 1.0)
    x = t * (length(VIRIDIS) - 1)
    i = min(Int(floor(x)) + 1, length(VIRIDIS) - 1)
    f = x - (i - 1)
    a = hexc(VIRIDIS[i]); b = hexc(VIRIDIS[i+1])
    (round(Int, a[1] + (b[1] - a[1]) * f),
     round(Int, a[2] + (b[2] - a[2]) * f),
     round(Int, a[3] + (b[3] - a[3]) * f))
end

# ── raster surface ───────────────────────────────────────────────────────────
mutable struct PCanvas
    w::Int
    h::Int
    px::Vector{UInt8}
end

function PCanvas(w::Int, h::Int, bg::String = COL_BG)
    c = PCanvas(w, h, Vector{UInt8}(undef, w * h * 3))
    pfill!(c, hexc(bg))
    return c
end

function pfill!(C::PCanvas, col::Tuple{Int,Int,Int})
    fill!(C.px, UInt8(0))
    for i in 1:3:length(C.px)
        C.px[i] = UInt8(col[1]); C.px[i+1] = UInt8(col[2]); C.px[i+2] = UInt8(col[3])
    end
    return C
end

function pset!(C::PCanvas, x::Int, y::Int, col::Tuple{Int,Int,Int})
    (0 <= x < C.w && 0 <= y < C.h) || return C
    i = 3 * (y * C.w + x) + 1
    @inbounds begin
        C.px[i] = UInt8(col[1]); C.px[i+1] = UInt8(col[2]); C.px[i+2] = UInt8(col[3])
    end
    return C
end

function prect!(C::PCanvas, x::Int, y::Int, w::Int, h::Int, col::Tuple{Int,Int,Int})
    x2 = min(x + w - 1, C.w - 1); y2 = min(y + h - 1, C.h - 1)
    for yy in max(y, 0):y2, xx in max(x, 0):x2
        pset!(C, xx, yy, col)
    end
    return C
end

function pline!(C::PCanvas, x1::Int, y1::Int, x2::Int, y2::Int,
                col::Tuple{Int,Int,Int}, width::Int = 1)
    dx = abs(x2 - x1); dy = abs(y2 - y1)
    sx = x1 < x2 ? 1 : -1; sy = y1 < y2 ? 1 : -1
    err = dx - dy
    x, y = x1, y1
    t = max(0, width ÷ 2)
    while true
        if width <= 1
            pset!(C, x, y, col)
        else
            prect!(C, x - t, y - t, width, width, col)
        end
        (x == x2 && y == y2) && break
        e2 = 2 * err
        if e2 > -dy; err -= dy; x += sx; end
        if e2 < dx;  err += dx; y += sy; end
    end
    return C
end

function pdisc!(C::PCanvas, xc::Int, yc::Int, rad::Int, col::Tuple{Int,Int,Int})
    rad <= 0 && return pset!(C, xc, yc, col)
    for dy in -rad:rad, dx in -rad:rad
        dx * dx + dy * dy <= rad * rad && pset!(C, xc + dx, yc + dy, col)
    end
    return C
end

function ptext!(C::PCanvas, s::String, x::Int, y::Int, scale::Int,
                col::Tuple{Int,Int,Int}; bold::Bool = false, align::Symbol = :l)
    total = length(collect(s)) * 32 * scale
    x0 = align == :l ? x : (align == :c ? x - total ÷ 2 : x - total)
    for (k, ch) in enumerate(collect(s))
        g = font_glyph(ch, bold)
        gx0 = x0 + (k - 1) * 32 * scale
        for r in 0:31
            bits = g[r+1]
            bits == 0 && continue
            for cbit in 0:31
                (bits >> (31 - cbit)) & 1 == 1 || continue
                prect!(C, gx0 + cbit * scale, y + r * scale, scale, scale, col)
            end
        end
    end
    return C
end

# ── vector surface (SVG) ─────────────────────────────────────────────────────
mutable struct SCtx
    w::Int
    h::Int
    io::IOBuffer
end

function SCtx(w::Int, h::Int, bg::String = COL_BG)
    s = SCtx(w, h, IOBuffer())
    write(s.io, "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"$(w)\" height=\"$(h)\" viewBox=\"0 0 $(w) $(h)\">\n")
    r, g, b = hexc(bg)
    write(s.io, "<rect x=\"0\" y=\"0\" width=\"$(w)\" height=\"$(h)\" fill=\"rgb($(r),$(g),$(b))\"/>\n")
    return s
end

svgcol(col::Tuple{Int,Int,Int}) = "rgb($(col[1]),$(col[2]),$(col[3]))"

pfill!(S::SCtx, col::Tuple{Int,Int,Int}) = S

prect!(S::SCtx, x::Int, y::Int, w::Int, h::Int, col::Tuple{Int,Int,Int}) =
    (write(S.io, "<rect x=\"$(x)\" y=\"$(y)\" width=\"$(w)\" height=\"$(h)\" fill=\"$(svgcol(col))\"/>\n"); S)

function pline!(S::SCtx, x1::Int, y1::Int, x2::Int, y2::Int,
                col::Tuple{Int,Int,Int}, width::Int = 1)
    write(S.io, "<line x1=\"$(x1)\" y1=\"$(y1)\" x2=\"$(x2)\" y2=\"$(y2)\" stroke=\"$(svgcol(col))\" stroke-width=\"$(width)\"/>\n")
    return S
end

pdisc!(S::SCtx, x::Int, y::Int, rad::Int, col::Tuple{Int,Int,Int}) =
    (write(S.io, "<circle cx=\"$(x)\" cy=\"$(y)\" r=\"$(rad)\" fill=\"$(svgcol(col))\"/>\n"); S)

function ptext!(S::SCtx, s::String, x::Int, y::Int, scale::Int,
                col::Tuple{Int,Int,Int}; bold::Bool = false, align::Symbol = :l)
    fs = 30 * scale
    anchor = align == :l ? "start" : (align == :c ? "middle" : "end")
    w = "normal"; bold && (w = "bold")
    esc = replace(replace(s, "&" => "&amp;"), "<" => "&lt;")
    write(S.io, "<text x=\"$(x)\" y=\"$(y + 25 * scale)\" text-anchor=\"$(anchor)\" font-family=\"DejaVu Sans, Arial, sans-serif\" font-size=\"$(fs)\" font-weight=\"$(w)\" fill=\"$(svgcol(col))\">$(esc)</text>\n")
    return S
end

function save_svg(S::SCtx, path::String)
    write(S.io, "</svg>\n")
    open(path, "w") do f
        write(f, take!(S.io))
    end
    return path
end

# both surfaces render the same chart:
chart_targets(w::Int, h::Int) = (PCanvas(w, h), SCtx(w, h))

save_charts(C::PCanvas, S::SCtx, pngpath::String, svgpath::String) = begin
    write_png(pngpath, C.w, C.h, C.px)
    save_svg(S, svgpath)
end

# ── variable-width glyph metrics + text rendering ─────────────────────────────
const GLYPH_W = Dict{Tuple{Char,Bool},Int}()

function glyph_width(ch::Char, bold::Bool = false)
    k = (ch, bold)
    haskey(GLYPH_W, k) && return GLYPH_W[k]
    g = font_glyph(ch, bold)
    w = 0
    for r in 1:32
        bits = g[r]
        bits == 0 && continue
        w = max(w, 32 - leading_zeros(bits))
    end
    w = w == 0 ? 7 : w
    GLYPH_W[k] = w
    return w
end

text_width(s::AbstractString, scale::Int; bold::Bool = false) =
    sum(glyph_width(ch, bold) + 3 for ch in collect(s)) * scale

function ptext!(C::PCanvas, s::String, x::Int, y::Int, scale::Int,
                col::Tuple{Int,Int,Int}; bold::Bool = false, align::Symbol = :l)
    isempty(s) && return C
    total = text_width(s, scale; bold = bold)
    pen = align == :l ? x : (align == :c ? x - total ÷ 2 : x - total)
    for ch in collect(s)
        g = font_glyph(ch, bold)
        gw = glyph_width(ch, bold)
        for r in 0:31
            bits = g[r+1]
            bits == 0 && continue
            for cbit in 0:(gw - 1)
                (bits >> (31 - cbit)) & 1 == 1 || continue
                prect!(C, pen + cbit * scale, y + r * scale, scale, scale, col)
            end
        end
        pen += (gw + 3) * scale
    end
    return C
end

function ptext!(S::SCtx, s::String, x::Int, y::Int, scale::Int,
                col::Tuple{Int,Int,Int}; bold::Bool = false, align::Symbol = :l)
    isempty(s) && return S
    fs = 30 * scale
    w = "normal"; bold && (w = "bold")
    total = text_width(s, scale; bold = bold)
    pen = align == :l ? x : (align == :c ? x - total ÷ 2 : x - total)
    esc = replace(replace(s, "&" => "&amp;"), "<" => "&lt;")
    for ch in collect(s)
        gw = glyph_width(ch, bold)
        cx = pen + (gw * scale) ÷ 2
        c = string(ch)
        c == "&" && (c = "&amp;")
        c == "<" && (c = "&lt;")
        write(S.io, "<text x=\"$(cx)\" y=\"$(y + 25 * scale)\" text-anchor=\"middle\" font-family=\"DejaVu Sans, Arial, sans-serif\" font-size=\"$(fs)\" font-weight=\"$(w)\" fill=\"$(svgcol(col))\">$(c)</text>\n")
        pen += (gw + 3) * scale
    end
    return S
end

# ──────────────────────────────────────────────────────────────────────────────
# CHARTS — axes, frames and the four laboratory figures
# ──────────────────────────────────────────────────────────────────────────────

mutable struct RunData
    scaling::Vector{Tuple{Int,Float64,Float64,Float64,Int}}
    outcomes::Vector{Tuple{String,Float64,Float64,Float64,Float64,Float64,Float64}}
    policy_outcomes::Vector{Tuple{String,Float64,Float64,Float64,Float64,Float64,Float64}}
    chart2_note::String
    flow_n::Int
    flow_field::Vector{Int32}
    flow_pieces::Vector{Tuple{Int,Char,Int}}
    flow_paths::Vector{Tuple{Int,Vector{Int}}}
    dtmpts::Vector{Tuple{Int,Int,Int}}
    seed::Int
end
RunData() = RunData(Tuple{Int,Float64,Float64,Float64,Int}[],
                    Tuple{String,Float64,Float64,Float64,Float64,Float64,Float64}[],
                    Tuple{String,Float64,Float64,Float64,Float64,Float64,Float64}[],
                    "",
                    0, Int32[], Tuple{Int,Char,Int}[], Tuple{Int,Vector{Int}}[],
                    Tuple{Int,Int,Int}[], 0)

tr10(log::Bool, v::Float64) = log ? log10(max(v, 1e-12)) : v

struct Frame
    t::Union{PCanvas,SCtx}
    x0::Int; y0::Int; x1::Int; y1::Int
    xmin::Float64; xmax::Float64; ymin::Float64; ymax::Float64
    logx::Bool; logy::Bool
end

mapx(F::Frame, v::Float64) =
    F.x0 + round(Int, (tr10(F.logx, v) - tr10(F.logx, F.xmin)) /
        (tr10(F.logx, F.xmax) - tr10(F.logx, F.xmin)) * (F.x1 - F.x0))
mapy(F::Frame, v::Float64) =
    F.y1 - round(Int, (tr10(F.logy, v) - tr10(F.logy, F.ymin)) /
        (tr10(F.logy, F.ymax) - tr10(F.logy, F.ymin)) * (F.y1 - F.y0))

function nice_ticks(lo::Float64, hi::Float64, target::Int = 6)
    hi > lo || (hi = lo + 1)
    raw = (hi - lo) / target
    mag = 10.0 ^ floor(log10(raw))
    r = raw / mag
    step = r < 1.5 ? mag : r < 3.5 ? 2mag : r < 7.5 ? 5mag : 10mag
    out = Float64[]
    v = ceil(lo / step) * step
    while v <= hi + 1e-9
        push!(out, v)
        v += step
    end
    return out
end

function log_ticks(lo::Float64, hi::Float64)
    out = Float64[]
    d = 10.0 ^ floor(log10(max(lo, 1e-12)))
    while d <= hi * 10
        d >= lo && push!(out, d)
        d *= 10
    end
    return out
end

fmt_g(v::Float64) = @sprintf("%g", v)

function pdash!(t, x1::Int, y1::Int, x2::Int, y2::Int, col, width::Int = 2)
    if t isa SCtx
        write(t.io, "<line x1=\"$(x1)\" y1=\"$(y1)\" x2=\"$(x2)\" y2=\"$(y2)\" stroke=\"$(svgcol(col))\" stroke-width=\"$(width)\" stroke-dasharray=\"$(width*8),$(width*6)\"/>\n")
        return t
    end
    n = max(2, round(Int, hypot(x2 - x1, y2 - y1) / 30))
    on = true
    for k in 1:(n - 1)
        if on
            a = round(Int, x1 + (x2 - x1) * (k - 1) / n)
            b = round(Int, y1 + (y2 - y1) * (k - 1) / n)
            c = round(Int, x1 + (x2 - x1) * k / n)
            d = round(Int, y1 + (y2 - y1) * k / n)
            pline!(t, a, b, c, d, col, width)
        end
        on = !on
    end
    return t
end

function draw_frame!(F::Frame, title::String, subtitle::String,
                     xlabel::String, ylabel::String;
                     xticks::Vector{Float64}, yticks::Vector{Float64},
                     xlabels::Union{Nothing,Vector{String}} = nothing,
                     ylabels::Union{Nothing,Vector{String}} = nothing)
    t = F.t
    # grid
    for v in xticks
        x = mapx(F, v)
        pline!(t, x, F.y0, x, F.y1, hexc(COL_GRID), 1)
    end
    for v in yticks
        y = mapy(F, v)
        pline!(t, F.x0, y, F.x1, y, hexc(COL_GRID), 1)
    end
    # axes
    pline!(t, F.x0, F.y0, F.x0, F.y1, hexc(COL_AXIS), 3)
    pline!(t, F.x0, F.y1, F.x1, F.y1, hexc(COL_AXIS), 3)
    # titles
    ptext!(t, title, (F.x0 + F.x1) ÷ 2, 60, 3, hexc(COL_FG); bold = true, align = :c)
    isempty(subtitle) || ptext!(t, subtitle, (F.x0 + F.x1) ÷ 2, 175, 2, hexc(COL_DIM); align = :c)
    ptext!(t, xlabel, (F.x0 + F.x1) ÷ 2, F.y1 + 60, 2, hexc(COL_AXIS); align = :c)
    ptext!(t, ylabel, F.x0 - 30, F.y0 - 110, 2, hexc(COL_AXIS); align = :l)
    # ticks
    for (i, v) in enumerate(xticks)
        x = mapx(F, v)
        lab = xlabels === nothing ? fmt_g(v) : (i <= length(xlabels) ? xlabels[i] : fmt_g(v))
        ptext!(t, lab, x, F.y1 + 20, 2, hexc(COL_DIM); align = :c)
    end
    for (i, v) in enumerate(yticks)
        y = mapy(F, v)
        lab = ylabels === nothing ? fmt_g(v) : (i <= length(ylabels) ? ylabels[i] : fmt_g(v))
        ptext!(t, lab, F.x0 - 20, y - 32, 2, hexc(COL_DIM); align = :r)
    end
    return F
end

function draw_footer!(F::Frame, seed::Int)
    ptext!(F.t, "chess-dynamics-lab · large_board_lab.jl",
           F.x0, F.t.h - 90, 2, hexc(COL_DIM); align = :l)
    ptext!(F.t, "author: Isaev Iskhak Khamzatovich · seed $(seed) · $(Dates.format(Dates.now(), "yyyy-mm-dd"))",
           F.x1, F.t.h - 90, 2, hexc(COL_DIM); align = :r)
    return F
end

function draw_legend!(F::Frame, entries::Vector{Tuple{String,String,Int}};
                      pos::Symbol = :tr)
    t = F.t
    wmax = maximum(text_width(e[1], 2) for e in entries)
    bw = wmax + 320; bh = 80 * length(entries) + 40
    bx = pos == :tr ? F.x1 - bw - 40 :
         pos == :tl ? F.x0 + 40 :
         pos == :br ? F.x1 - bw - 40 : F.x0 + 40
    by = (pos == :tr || pos == :tl) ? F.y0 + 40 : F.y1 - bh - 40
    prect!(t, bx, by, bw, bh, hexc("#FFFFFF"))
    if t isa PCanvas
        for xx in bx:bx+bw-1
            pset!(t, xx, by, hexc(COL_AXIS)); pset!(t, xx, by + bh - 1, hexc(COL_AXIS))
        end
        for yy in by:by+bh-1
            pset!(t, bx, yy, hexc(COL_AXIS)); pset!(t, bx + bw - 1, yy, hexc(COL_AXIS))
        end
    else
        write(t.io, "<rect x=\"$(bx)\" y=\"$(by)\" width=\"$(bw)\" height=\"$(bh)\" fill=\"none\" stroke=\"$(COL_AXIS)\"/>\n")
    end
    for (i, (lab, color, style)) in enumerate(entries)
        y = by + 44 + (i - 1) * 80
        c = hexc(color)
        if style == 0
            pline!(t, bx + 30, y + 16, bx + 130, y + 16, c, 5)
        elseif style == 1
            pdash!(t, bx + 30, y + 16, bx + 130, y + 16, c, 5)
        else
            pdisc!(t, bx + 80, y + 16, 14, c)
        end
        ptext!(t, lab, bx + 160, y, 2, hexc(COL_FG); align = :l)
    end
    return F
end

# horizontal legend strip (used by the bar chart)
function draw_legend_h!(F::Frame, entries::Vector{Tuple{String,String,Int}}, y::Int)
    t = F.t
    pen = (F.x0 + F.x1) ÷ 2 -
          (sum(text_width(e[1], 2) + 260 for e in entries) - 120) ÷ 2
    for (lab, color, style) in entries
        c = hexc(color)
        if style == 0
            pline!(t, pen, y + 16, pen + 100, y + 16, c, 5)
        elseif style == 1
            pdash!(t, pen, y + 16, pen + 100, y + 16, c, 5)
        else
            pdisc!(t, pen + 50, y + 16, 14, c)
        end
        ptext!(t, lab, pen + 130, y, 2, hexc(COL_FG); align = :l)
        pen += text_width(lab, 2) + 260
    end
    return F
end

# ── chart 1: scaling (log-log) ───────────────────────────────────────────────
function chart_scaling(rd::RunData, cfg, dir::String, logf::Function)
    isempty(rd.scaling) && return nothing
    ns = [Float64(p[1]) for p in rd.scaling]
    ts = [max(p[2], 1e-7) for p in rd.scaling]
    n1, t1 = ns[1], ts[1]
    ref2 = [t1 * (v / n1)^2 for v in ns]
    ref4 = [t1 * (v / n1)^4 for v in ns]
    w = round(Int, cfg.fig_w * cfg.dpi); h = round(Int, cfg.fig_h * cfg.dpi)
    C, S = chart_targets(w, h)
    for sf in (C, S)
        xmin = ns[1] * 0.75; xmax = ns[end] * 1.35
        ymin = minimum(ts) / 4
        ymax = max(maximum(ts) * 4, maximum(ref4) * 1.6)
        F = Frame(sf, 800, 330, w - 180, h - 330, xmin, xmax, ymin, ymax, true, true)
        xtk = log_ticks(xmin, xmax); ytk = log_ticks(ymin, ymax)
        ylb = [v >= 1 ? @sprintf("%d", round(Int, v)) :
               (v >= 1e-3 ? @sprintf("%g", v) :
                "10^" * string(round(Int, log10(v)))) for v in ytk]
        draw_frame!(F, t("c1_title"),
                    "mu = $(cfg.mu) · lambda = $(cfg.lam) · KLEIN tie-break",
                    t("c1_xlabel"), t("c1_ylabel"); xticks = xtk, yticks = ytk,
                    ylabels = ylb)
        # measured polyline + markers
        xs = [mapx(F, v) for v in ns]; ys = [mapy(F, v) for v in ts]
        for k in 1:(length(xs)-1)
            pline!(sf, xs[k], ys[k], xs[k+1], ys[k+1], hexc(COL_MEAS), 6)
        end
        for k in eachindex(xs)
            pdisc!(sf, xs[k], ys[k], 18, hexc(COL_MEAS))
        end
        # references anchored at the first measured point
        for k in 1:(length(xs)-1)
            y2a = mapy(F, ref2[k]); y2b = mapy(F, ref2[k+1])
            pdash!(sf, xs[k], y2a, xs[k+1], y2b, hexc(COL_REF2), 4)
            y4a = mapy(F, ref4[k]); y4b = mapy(F, ref4[k+1])
            pdash!(sf, xs[k], y4a, xs[k+1], y4b, hexc(COL_REF4), 4)
        end
        draw_legend!(F, Tuple{String,String,Int}[
            (t("c1_meas"), COL_MEAS, 0), (t("c1_ref2"), COL_REF2, 1),
            (t("c1_ref4"), COL_REF4, 1)]; pos = :tl)
        draw_footer!(F, rd.seed)
    end
    p = joinpath(dir, "chart1_scaling")
    save_charts(C, S, p * ".png", p * ".svg")
    logf(t("rep_files") * ": chart1_scaling.png / .svg")
    return p
end

# ── chart 2: outcome distribution (grouped bars + Wilson CI whiskers) ────────
#   Categories: per-policy pooled verdicts when the policy ensemble ran
#   (the PARTIAL POLICY VERDICT view), otherwise per-scenario pooled rows.
function chart_outcomes(rd::RunData, cfg, dir::String, logf::Function)
    rows = isempty(rd.policy_outcomes) ? rd.outcomes : rd.policy_outcomes
    isempty(rows) && return nothing
    w = round(Int, cfg.fig_w * cfg.dpi); h = round(Int, cfg.fig_h * cfg.dpi)
    C, S = chart_targets(w, h)
    ncat = length(rows)
    note = isempty(rd.chart2_note) ?
           "n = $(cfg.n) · $(t("plays")): $(cfg.playouts_main) × $ncat" : rd.chart2_note
    for sf in (C, S)
        F = Frame(sf, 800, 330, w - 180, h - 330, 0.0, Float64(ncat), 0.0, 1.12,
                  false, false)
        ytk = collect(0.0:0.2:1.0)
        ylb = [@sprintf("%d%%", round(Int, v * 100)) for v in ytk]
        draw_frame!(F, t("c2_title"), note,
                    ncat >= 3 ? "" : t("policy"), t("c2_ylabel");
                    xticks = Float64[i - 0.5 for i in 1:ncat],
                    yticks = ytk,
                    xlabels = [o[1] for o in rows], ylabels = ylb)
        draw_legend_h!(F, Tuple{String,String,Int}[
            (t("out_draw"), COL_DRAW, 2), (t("out_white"), COL_WHITEP, 2),
            (t("out_black"), COL_BLACKP, 2)], F.y0 - 60)
        bw = (F.x1 - F.x0) / ncat * 0.20
        for (i, (label, pD, pW, pB, hD, hW, hB)) in enumerate(rows)
            cx = mapx(F, Float64(i - 0.5))
            bars = [(pD, hD, COL_DRAW), (pW, hW, COL_WHITEP), (pB, hB, COL_BLACKP)]
            for (j, (p, hw, colr)) in enumerate(bars)
                x = round(Int, cx - 1.5 * bw + (j - 1) * bw + 0.1 * bw)
                ytop = mapy(F, p); ybot = mapy(F, 0.0)
                prect!(sf, x, ytop, round(Int, bw * 0.8), ybot - ytop, hexc(colr))
                if sf isa PCanvas
                    pline!(sf, x, ytop, x + round(Int, bw * 0.8), ytop, hexc(COL_AXIS), 2)
                    pline!(sf, x, ybot, x, ytop, hexc(COL_AXIS), 2)
                    pline!(sf, x + round(Int, bw * 0.8), ybot, x + round(Int, bw * 0.8), ytop, hexc(COL_AXIS), 2)
                else
                    write(sf.io, "<rect x=\"$(x)\" y=\"$(ytop)\" width=\"$(round(Int, bw * 0.8))\" height=\"$(ybot - ytop)\" fill=\"$(colr)\" stroke=\"$(COL_AXIS)\"/>\n")
                end
                wx = x + round(Int, bw * 0.4)
                ya = mapy(F, min(1.0, p + hw)); yb = mapy(F, max(0.0, p - hw))
                pline!(sf, wx, ya, wx, yb, hexc(COL_FG), 3)
                pline!(sf, wx - 14, ya, wx + 14, ya, hexc(COL_FG), 3)
                pline!(sf, wx - 14, yb, wx + 14, yb, hexc(COL_FG), 3)
                ptext!(sf, @sprintf("%.0f%%", p * 100), wx, ya - 74, 2, hexc(COL_FG); align = :c)
            end
        end
        draw_footer!(F, rd.seed)
    end
    p = joinpath(dir, "chart2_outcomes")
    save_charts(C, S, p * ".png", p * ".svg")
    logf(t("rep_files") * ": chart2_outcomes.png / .svg")
    return p
end

# ── chart 3: K3 flow heatmap on the n x n board ──────────────────────────────
function chart_flow(rd::RunData, cfg, dir::String, logf::Function)
    rd.flow_n == 0 && return nothing
    n = rd.flow_n
    field = rd.flow_field
    w = round(Int, cfg.fig_w * cfg.dpi); h = round(Int, cfg.fig_h * cfg.dpi)
    C, S = chart_targets(w, h)
    side = min(w - 1150, h - 700)
    x0 = 830; y0 = 340
    cs = side / n
    vmax = max(1, maximum(field))
    for sf in (C, S)
        title = replace(t("c3_title"), "{N}" => string(n))
        ptext!(sf, title, x0, 70, 3, hexc(COL_FG); bold = true, align = :l)
        ptext!(sf, "T04 · K3 · $(t("c3_bar")) · $(t("board")) $(n)x$(n)",
               x0, 180, 2, hexc(COL_DIM); align = :l)
        for r in 0:(n-1), c in 0:(n-1)
            v = Float64(field[r * n + c + 1]) / vmax
            col = viridis(v)
            xa = x0 + round(Int, c * cs); xb = x0 + round(Int, (c + 1) * cs)
            ya = y0 + round(Int, r * cs); yb = y0 + round(Int, (r + 1) * cs)
            prect!(sf, xa, ya, xb - xa, yb - ya, col)
        end
        # board frame + coordinate labels every 16 lines
        pline!(sf, x0, y0, x0 + side, y0, hexc(COL_AXIS), 4)
        pline!(sf, x0 + side, y0, x0 + side, y0 + side, hexc(COL_AXIS), 4)
        pline!(sf, x0 + side, y0 + side, x0, y0 + side, hexc(COL_AXIS), 4)
        pline!(sf, x0, y0 + side, x0, y0, hexc(COL_AXIS), 4)
        for c in 0:16:(n - 1)
            x = x0 + round(Int, (c + 0.5) * cs)
            ptext!(sf, fileletter(c), x, y0 + side + 16, 2, hexc(COL_DIM); align = :c)
        end
        for r in 0:16:(n - 1)
            y = y0 + round(Int, (r + 0.5) * cs)
            ptext!(sf, string(r + 1), x0 - 70, y - 32, 2, hexc(COL_DIM); align = :r)
        end
        # particle trajectories
        for (cid, sqs) in rd.flow_paths
            col = cid > 0 ? hexc(COL_PATHW) : hexc(COL_PATHB)
            pts = [(x0 + round(Int, ((s % n) + 0.5) * cs),
                    y0 + round(Int, ((s ÷ n) + 0.5) * cs)) for s in sqs]
            for k in 1:(length(pts) - 1)
                pline!(sf, pts[k][1], pts[k][2], pts[k+1][1], pts[k+1][2], col, 5)
            end
            isempty(pts) || pdisc!(sf, pts[1][1], pts[1][2], 12, col)
        end
        # pieces on top
        for (sq, ch, sid) in rd.flow_pieces
            cx = x0 + round(Int, ((sq % n) + 0.5) * cs)
            cy = y0 + round(Int, ((sq ÷ n) + 0.5) * cs)
            rad = max(11, round(Int, cs * 0.52))
            pdisc!(sf, cx, cy, rad, sid > 0 ? hexc("#1B4F72") : hexc("#0E0E0E"))
            ptext!(sf, string(ch), cx, cy - rad + 2, 1, hexc("#FFFFFF"); bold = true, align = :c)
        end
        # colorbar
        cbx = x0 + side + 90; cbw = 54
        for yy in 0:(side - 1)
            col = viridis(1.0 - yy / side)
            prect!(sf, cbx, y0 + yy, cbw, 2, col)
        end
        for (frac, lab) in ((0.0, "0"), (0.5, fmt_g(vmax / 2)), (1.0, string(vmax)))
            y = y0 + round(Int, (1 - frac) * side)
            pline!(sf, cbx + cbw, y, cbx + cbw + 16, y, hexc(COL_AXIS), 3)
            ptext!(sf, lab, cbx + cbw + 26, y - 32, 2, hexc(COL_AXIS); align = :l)
        end
        ptext!(sf, "chess-dynamics-lab · large_board_lab.jl · author: Isaev Iskhak Khamzatovich · seed $(rd.seed)",
               x0, h - 90, 2, hexc(COL_DIM); align = :l)
    end
    p = joinpath(dir, "chart3_flow_$(n)x$(n)")
    save_charts(C, S, p * ".png", p * ".svg")
    logf(t("rep_files") * ": chart3_flow_$(n)x$(n).png / .svg")
    return p
end

# ── chart 4: exact oracle, longest mate vs n (power fit) ─────────────────────
function chart_dtm(rd::RunData, cfg, dir::String, logf::Function)
    length(rd.dtmpts) < 2 && return nothing
    ns = [Float64(p[1]) for p in rd.dtmpts]
    ys = [Float64(p[2]) for p in rd.dtmpts]
    xl = log10.(ns); yl = log10.(ys)
    mx = sum(xl) / length(xl); my = sum(yl) / length(yl)
    b = sum((xl .- mx) .* (yl .- my)) / sum((xl .- mx) .^ 2)
    a = 10^(my - b * mx)
    w = round(Int, cfg.fig_w * cfg.dpi); h = round(Int, cfg.fig_h * cfg.dpi)
    C, S = chart_targets(w, h)
    for sf in (C, S)
        xmin = ns[1] * 0.85; xmax = ns[end] * 1.25
        ymin = minimum(ys) * 0.8; ymax = maximum(ys) * 1.35
        F = Frame(sf, 800, 330, w - 180, h - 330, xmin, xmax, ymin, ymax, false, false)
        xtk = collect(floor(xmin):ceil(xmax))
        ytk = nice_ticks(ymin, ymax, 6)
        draw_frame!(F, t("c4_title"),
                    "DTM ≈ $(round(a, digits = 2))·n^$(round(b, digits = 3)) · K+piece vs K",
                    t("c4_xlabel"), t("c4_ylabel"); xticks = xtk, yticks = ytk)
        # fit curve
        np = 80
        prev = nothing
        for k in 0:np
            v = xmin * (xmax / xmin)^(k / np)
            yv = a * v^b
            pt = (mapx(F, v), mapy(F, yv))
            prev === nothing || pdash!(sf, prev[1], prev[2], pt[1], pt[2], hexc(COL_ACCENT), 4)
            prev = pt
        end
        # measured points + state annotations
        for (i, p) in enumerate(rd.dtmpts)
            x = mapx(F, Float64(p[1])); y = mapy(F, Float64(p[2]))
            pdisc!(sf, x, y, 18, hexc(COL_MEAS))
            ptext!(sf, @sprintf("%d", p[2]), x, y - 96, 2, hexc(COL_FG); align = :c)
            ptext!(sf, "$(t("c4_states")): $(p[3])", x, y + 34, 2, hexc(COL_DIM); align = :c)
        end
        draw_legend!(F, Tuple{String,String,Int}[
            (t("or_max"), COL_MEAS, 2), (t("c4_fit"), COL_ACCENT, 1)]; pos = :tl)
        draw_footer!(F, rd.seed)
    end
    p = joinpath(dir, "chart4_dtm_growth")
    save_charts(C, S, p * ".png", p * ".svg")
    logf(t("rep_files") * ": chart4_dtm_growth.png / .svg")
    return p
end

function render_charts(rd::RunData, cfg, dir::String, logf::Function)
    logf("── " * t("rep_files") * " " * "─"^40)
    mkpath(dir)
    chart_scaling(rd, cfg, dir, logf)
    chart_outcomes(rd, cfg, dir, logf)
    chart_flow(rd, cfg, dir, logf)
    chart_dtm(rd, cfg, dir, logf)
    return nothing
end

# ──────────────────────────────────────────────────────────────────────────────
# TERMINAL ART — banner, knight, panels, one-line progress bar, verdicts
# ──────────────────────────────────────────────────────────────────────────────

const W = 100

hr(P::Palette, ch::Char = '─') = P.on ? string(P.dim, repeat(string(ch), W), A_RESET) :
    repeat(string(ch), W)

section(P::Palette, title::AbstractString) = begin
    head = "▐ " * (P.on ? P.hl * title * A_RESET : title) * " "
    pad = max(W - ansi_len(head) - 2, 4)
    P.on ? string(head, P.dim, "▌", repeat("─", pad), A_RESET) : string("— ", title, " —")
end

# visible width without ANSI escapes
function ansi_len(s::AbstractString)
    n = 0; skip = false
    for ch in s
        if skip
            (isdigit(ch) || ch == ';') || (skip = false)
            continue
        end
        if ch == '\x1b'
            skip = true
            continue
        end
        n += 1
    end
    return n
end

function boxline(l::Char, m::Char, r::Char, inner::String)
    return string(l, m, inner, m, r)
end

function banner(P::Palette, cfg)
    art = P.on ? split("""
  ▄▄▄▄▄▄                    ╔═══════════════════════════╗
 ███▀▀███                   ║   ♞  ·  ✦  ·  ─ ─ →      ║
 ██    ██▄▄                 ║   PARTICLE FLOW  K3/TORUS ║
  ▀▄▄▄███▀█▄                ╚═══════════════════════════╝
   ▄██████▄ ██▄        ·  ─  ✦  ─  ·   ✦  ·  ─  ✦  ─ ·
  █████████▄▀██▄      ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·
  ███▀▀▀▀██▄ ██        ─  ─  ─  ─  ─  ─  ─  ─  ─  ─
   ██    ██▄▄█▌
   ▀▄    ▄▀▀▀                      ♜  ·  ─  ✦  ·  ─  ·
""", "\n") : String[]
    println()
    for ln in art
        println(P.on ? string(P.accent, ln, A_RESET) : "")
    end
    println(P.on ? string(P.title, "  ▛▀▀ " * t("prog") * " ▀▀▌", A_RESET) :
                   "  " * t("prog"))
    println(P.on ? string(P.dim, "  " * t("lab_title"), A_RESET) : "  " * t("lab_title"))
    println()
    println("  " * t("board") * ": n x n → " * P.hl * "$(cfg.n) x $(cfg.n)" * A_RESET *
            "  ($(cfg.n * cfg.n) " * t("cells") * ")")
    println("  " * t("threads") * ": $(Threads.nthreads()) · seed: $(cfg.seed) · " *
            "julia $(VERSION.major).$(VERSION.minor)")
    cfg.quick && println(P.warn * "  ⚡ " * t("quick_on") * A_RESET)
    println(hr(P, '═'))
    println()
end

# ── one-line progress bar ─────────────────────────────────────────────────────
mutable struct Bar
    total::Int
    label::String
    t0::Float64
    last::Float64
    P::Palette
    on::Bool
end

function Bar(total::Int, label::String, P::Palette)
    Bar(total, label, time(), 0.0, P, P.on)
end

function fmt_mmss(s::Float64)
    (isnan(s) || !isfinite(s)) && return "--:--"
    m = floor(Int, s / 60)
    ss = round(Int, s) % 60
    return @sprintf("%02d:%02d", m, ss)
end

function tick!(b::Bar, k::Int)
    now = time()
    if !(b.on)
        if now - b.last > 5 || k == b.total
            println(stderr, "  [$(k)/$(b.total)] $(b.label)")
            b.last = now
        end
        return b
    end
    (now - b.last > 0.12 || k == b.total) || return b
    b.last = now
    frac = clamp(k / max(b.total, 1), 0.0, 1.0)
    bw = 30
    filled = round(Int, frac * bw)
    bar = repeat("█", filled) * repeat("░", bw - filled)
    el = now - b.t0
    eta = k > 0 ? el / k * (b.total - k) : NaN
    line = @sprintf("  %s %s %s %5.1f%% · %d/%d · %s %s   ",
                    b.label, b.P.accent * "[$bar]" * A_RESET,
                    b.P.dim * "│" * A_RESET, frac * 100, k, b.total,
                    t("eta"), fmt_mmss(eta))
    print(stdout, "\x1b[2K\r", line)
    flush(stdout)
    return b
end

done!(b::Bar) = begin
    b.on && print(stdout, "\x1b[2K\r")
    flush(stdout)
    return b
end

# ── verdict art ───────────────────────────────────────────────────────────────
function verdict_art(P::Palette, headline::String, share::String, honest::Bool = true)
    println()
    big = big_text_line(P, headline; fg = 220)
    isempty(big) || print(big)
    sub = "  ★ " * share
    println(P.on ? string(P.accent, sub, A_RESET) : sub)
    honest && println(P.dim * "  ⚠ " * t("v_honest") * A_RESET)
    println()
end

# ── simple fixed-width tables ─────────────────────────────────────────────────
function thead(cols::Vector{String}, widths::Vector{Int})
    build = IOBuffer()
    write(build, "  ┌")
    for (i, wd) in enumerate(widths)
        i > 1 && write(build, "┬")
        write(build, repeat("─", wd + 2))
    end
    write(build, "┐\n  │")
    for (i, c) in enumerate(cols)
        pad = max(0, widths[i] - ansi_len(c))
        write(build, " " * c * repeat(" ", pad) * " │")
    end
    write(build, "\n  ├")
    for (i, wd) in enumerate(widths)
        i > 1 && write(build, "┼")
        write(build, repeat("─", wd + 2))
    end
    write(build, "┤")
    return String(take!(build))
end

function trow(cells::Vector{String}, widths::Vector{Int})
    b = IOBuffer()
    write(b, "\n  │")
    for (i, c) in enumerate(cells)
        pad = max(0, widths[i] - ansi_len(c))
        write(b, " " * c * repeat(" ", pad) * " │")
    end
    return String(take!(b))
end

tsep(widths::Vector{Int}) = begin
    b = IOBuffer()
    write(b, "\n  ├")
    for (i, wd) in enumerate(widths)
        i > 1 && write(b, "┼")
        write(b, repeat("─", wd + 2))
    end
    write(b, "┤")
    String(take!(b))
end

tfoot(widths::Vector{Int}) = begin
    b = IOBuffer()
    write(b, "\n  └")
    for (i, wd) in enumerate(widths)
        i > 1 && write(b, "┴")
        write(b, repeat("─", wd + 2))
    end
    write(b, "┘")
    String(take!(b))
end

wait_enter(P::Palette) = begin
    println()
    print(P.dim * "  " * t("m_press") * A_RESET)
    flush(stdout)
    try
        readline(stdin)
    catch
    end
end

# ──────────────────────────────────────────────────────────────────────────────
# LOGGING + REPORTS — TXT log, JSON, CSV, Markdown (all formats per run)
# ──────────────────────────────────────────────────────────────────────────────

mutable struct Logger
    lines::Vector{String}
    P::Palette
end
Logger(P::Palette) = Logger(String[], P)

function log(L::Logger, msg::AbstractString = "")
    println(msg)
    flush(stdout)
    push!(L.lines, replace(String(msg), "\x1b" => ""))
    return L
end

function logbox(L::Logger, msg::AbstractString)
    log(L, "  " * msg)
end

json_escape(s::AbstractString) = begin
    b = IOBuffer()
    for ch in s
        if ch == '"'; write(b, "\\\"")
        elseif ch == '\\'; write(b, "\\\\")
        elseif ch == '\n'; write(b, "\\n")
        elseif ch == '\r'; write(b, "\\r")
        elseif ch == '\t'; write(b, "\\t")
        else write(b, ch)
        end
    end
    String(take!(b))
end

json_val(x::Union{String,AbstractString}) = "\"" * json_escape(x) * "\""
json_val(x::Symbol) = "\"" * string(x) * "\""
json_val(x::Integer) = string(x)
json_val(x::AbstractFloat) = isfinite(x) ? @sprintf("%.10g", x) : "null"
json_val(x::Bool) = x ? "true" : "false"
json_val(x::Nothing) = "null"
json_val(v::Vector{<:Any}) = "[" * join(json_val.(v), ",") * "]"
json_val(d::Dict{String,Any}) = begin
    ks = sort(collect(keys(d)))
    "{" * join(["$(json_val(k)): $(json_val(d[k]))" for k in ks], ",") * "}"
end

function write_json(path::String, d::Dict{String,Any})
    open(path, "w") do f
        write(f, json_val(d))
    end
    return path
end

function write_csv(path::String, header::Vector{String}, rows::Vector{Vector{String}})
    open(path, "w") do f
        println(f, join(header, ","))
        for r in rows
            out = String[]
            for cell in r
                occursin(',', cell) || occursin('"', cell) ?
                push!(out, "\"" * replace(cell, "\"" => "\"\"") * "\"") :
                push!(out, cell)
            end
            println(f, join(out, ","))
        end
    end
    return path
end

function write_txt(path::String, lines::Vector{String}, cfg)
    open(path, "w") do f
        println(f, "═"^78)
        println(f, "  LARGE BOARD LABORATORY — full run log")
        println(f, "  chess-dynamics-lab · author: Isaev Iskhak Khamzatovich")
        println(f, "  generated: $(Dates.format(Dates.now(), "yyyy-mm-dd HH:MM:SS")) · julia $(VERSION)")
        println(f, "═"^78)
        for ln in lines
            println(f, ln)
        end
    end
    return path
end

function write_md(path::String, d::Dict{String,Any}, cfg, run_dir::String)
    open(path, "w") do f
        println(f, "# Large Board Laboratory — отчёт прогона / run report")
        println(f)
        println(f, "**chess-dynamics-lab** · автор программы: **Исаев Исхак Хамзатович** · " *
                "github.com/wild8highlander/chess-dynamics-lab")
        println(f)
        println(f, "*Дата / date:* $(Dates.format(Dates.now(), "yyyy-mm-dd HH:MM:SS")) · " *
                "*Julia:* $(VERSION) · *seed:* `$(cfg.seed)`")
        println(f)
        par = d["parameters"]
        println(f, "## Параметры прогона / run parameters")
        println(f)
        println(f, "| параметр / parameter | значение / value |")
        println(f, "|---|---|")
        for k in sort(collect(keys(par)))
            println(f, "| `$k` | `$(par[k])` |")
        end
        println(f)
        if haskey(d, "main_test") && haskey(d["main_test"], "verdict")
            mt = d["main_test"]
            println(f, "## Главный тест / MAIN TEST — T7 · вердикт частичной политики / partial policy verdict")
            println(f)
            println(f, "### Вердикт / verdict: **$(mt["verdict_title"])**")
            println(f)
            if haskey(mt, "consensus")
                println(f, "**Консенсус / consensus:** `$(mt["consensus"])` · " *
                        "**класс доказательности / evidence class:** " *
                        "`$(get(mt, "verdict_class", "partial_policy"))`")
                println(f)
            end
            println(f, "| сценарий | ничья | белые | чёрные | партий |")
            println(f, "|---|---|---|---|---|")
            for sc in mt["scenarios"]
                println(f, "| $(sc["scenario"]) | $(round(sc["p_draw"], digits = 3)) | " *
                        "$(round(sc["p_white"], digits = 3)) | $(round(sc["p_black"], digits = 3)) | " *
                        "$(sc["playouts"]) |")
            end
            println(f)
            if haskey(mt, "policies") && !isempty(mt["policies"])
                println(f, "### Ансамбль политик / policy ensemble")
                println(f)
                println(f, "| политика / policy | партий / games | ничья / draw | " *
                        "белые / white | чёрные / black | вердикт / verdict | уровень / tier |")
                println(f, "|---|---|---|---|---|---|---|")
                for pp in mt["policies"]
                    println(f, "| $(pp["policy"]) | $(pp["games"]) | " *
                            "$(round(pp["p_draw"], digits = 3)) | " *
                            "$(round(pp["p_white"], digits = 3)) | " *
                            "$(round(pp["p_black"], digits = 3)) | " *
                            "$(pp["verdict_sym"]) | $(pp["verdict_tier"]) |")
                end
                println(f)
                println(f, "Уровни вердикта политики / verdict tiers: " *
                        "`F` = форс (НИ ДИ > 50%) · `L` = склоняется (доля ≥ 75%) · " *
                        "`I` = неопределён / forced · leaning · inconclusive.")
                println(f)
                if haskey(mt, "coverage")
                    cv = mt["coverage"]
                    println(f, "**Покрытие / coverage:** " *
                            "стартов / starts `$(cv["unique_starts"])` · " *
                            "полуходов / plies `$(cv["plies_total"])` · " *
                            "пространство / states ≈`$(round(cv["states_estimate"], sigdigits = 4))` · " *
                            "доля / share `$(round(cv["coverage_share"], sigdigits = 3))`")
                    println(f)
                end
                println(f, "> " * get(mt, "evidence_ladder", t("v_ladder")))
                println(f)
            end
            println(f, "> " * t("v_honest"))
            println(f)
        end
        if haskey(d, "tests")
            println(f, "## Тесты / tests")
            println(f)
            println(f, "| тест | статус | ключевые значения |")
            println(f, "|---|---|---|")
            for tt in d["tests"]
                println(f, "| $(tt["name"]) | $(tt["status"]) | $(get(tt, "summary", "")) |")
            end
            println(f)
        end
        println(f, "## Графики / charts (PNG 600 dpi + SVG)")
        println(f)
        for ch in ("chart1_scaling", "chart2_outcomes", "chart3_flow", "chart4_dtm_growth")
            println(f, "- `charts/$(ch).png` / `.svg`")
        end
    end
    return path
end

# ──────────────────────────────────────────────────────────────────────────────
# TESTS — helpers, T1 census, T2 legality battery
# ──────────────────────────────────────────────────────────────────────────────

function wilson(k::Int, n::Int, z::Float64 = 1.959964)
    n == 0 && return (0.0, 0.0, 0.0)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2n)) / den
    h = z * sqrt(p * (1 - p) / n + z^4 / (4 * n * n)) / den
    return (p, max(0.0, c - h), min(1.0, c + h))
end

function recompute_key(P::Pos)
    Z, sk = zobrist(P.n)
    k = UInt64(0)
    for sq in 0:(P.n * P.n - 1)
        p = P.b[sq+1]
        p == 0 || (k ⊻= Z[zindex(p), sq+1])
    end
    P.side < 0 && (k ⊻= sk)
    return k
end

# cell-by-cell inverse K3 field (independent of threat_field's piece walk)
function field_by_cells(P::Pos, side::Int)
    f = zeros(Int32, P.n * P.n)
    for c in 0:(P.n * P.n - 1)
        f[c+1] = attacks_on(P, c, side)
    end
    return f
end

mark(ok::Bool) = ok ? "[PASS]" : "[FAIL]"

# ── T1 · board census: closed forms vs generated graphs ──────────────────────
function test_t1(cfg, P::Palette, L::Logger, rd::RunData)
    log(L, section(P, t("t1_title")))
    log(L, "  " * t("t1_note"))
    boards = sort(unique(vcat(cfg.scaling_ns, [8])))
    all_ok = true
    widths = [6, 12, 12, 12, 12, 12, 9]
    log(L, thead([t("board"), t("t1_rook"), t("t1_bishop"), t("t1_knight"),
                  t("t1_king"), t("t1_queen"), "status"], widths))
    for n in boards
        # closed forms (directed edge counts)
        f_rook = n * n * 2 * (n - 1)
        f_bishop = 2 * n * (n - 1) * (2 * n - 1) ÷ 3
        f_knight = 8 * (n - 1) * (n - 2)
        f_king = 8 * n * n - 12 * n + 4
        # geo-walk census: pseudo-mobility of a lone piece over every square
        g_rook = g_bishop = g_knight = g_king = 0
        for sq in 0:(n * n - 1)
            g_rook += length(geo(n).rays[1][sq+1]) + length(geo(n).rays[2][sq+1]) +
                      length(geo(n).rays[3][sq+1]) + length(geo(n).rays[4][sq+1])
            g_bishop += length(geo(n).rays[5][sq+1]) + length(geo(n).rays[6][sq+1]) +
                        length(geo(n).rays[7][sq+1]) + length(geo(n).rays[8][sq+1])
            g_king += length(geo(n).king_nb[sq+1])
            g_knight += length(geo(n).knight_nb[sq+1])
        end
        ok = (f_rook == g_rook) && (f_bishop == g_bishop) &&
             (f_knight == g_knight) && (f_king == g_king)
        all_ok &= ok
        st = ok ? P.ok * mark(true) * A_RESET : P.bad * mark(false) * A_RESET
        row = trow([string(n), string(f_rook), string(f_bishop), string(f_knight),
                    string(f_king), string(f_rook + f_bishop), st], widths)
        log(L, row)
    end
    log(L, tfoot(widths))
    # condition-based brute force on a small board (fully independent path)
    n = 8
    br = 0
    for a in 0:(n*n-1), b in 0:(n*n-1)
        a == b && continue
        ra, ca = a ÷ n, a % n
        rb, cb = b ÷ n, b % n
        dr = abs(ra - rb); dc = abs(ca - cb)
        if (ra == rb || ca == cb) || (dr == dc) ||
           ((dr == 1 && dc == 2) || (dr == 2 && dc == 1)) || (max(dr, dc) == 1)
            br += 1
        end
    end
    # king moves are a subset of rook moves, so the union is R + B + N
    ok = br == (n * n * 2 * (n - 1)) + (2 * n * (n - 1) * (2 * n - 1) ÷ 3) +
         (8 * (n - 1) * (n - 2))
    all_ok &= ok
    log(L, "  " * t("t1_queen") * ": n=8 brute-force union " * (ok ? "==" : "≠") *
            " R+B+N = $br " * mark(ok))
    log(L)
    return Dict{String,Any}("name" => "T1 census", "status" => all_ok ? "PASS" : "FAIL",
                            "summary" => "boards $(join(boards, ",")) · n=8 union check $br")
end

# ── T2 · legality battery on random playouts ──────────────────────────────────
function test_t2(cfg, P::Palette, L::Logger, rd::RunData)
    log(L, section(P, t("t2_title")))
    checks = ["moves∈legal", "king-safe", "kings-dist≥2", "pieces 2..3",
              "side-alternate", "zobrist==recompute", "mobility<n²",
              "K3 field identity", "outcome classified", "determinism"]
    fail = fill(false, length(checks))
    counts = fill(0, length(checks))
    S = Solver(cfg.mu, cfg.lam)
    boards = vcat(fill(8, 6), fill(16, 3), [cfg.n])
    for (bi, n) in enumerate(boards)
        g = SM64(UInt64(cfg.seed + 7000 + bi))
        P8 = Pos(n)
        for rep in 1:(n == cfg.n ? 2 : 4)
            wtm = isodd(rep)
            setup_kxk!(P8, g, PIECE_R, wtm)
            isempty(legal_moves(P8)) && continue
            prev_side = P8.side
            seen = Set{UInt64}([P8.key])
            plies = 0
            outcome = :none
            maxp = cfg.max_plies
            while plies < maxp
                legal = legal_moves(P8)
                if isempty(legal)
                    outcome = in_check(P8, P8.side) ?
                              (P8.side > 0 ? :black : :white) : :draw
                    break
                end
                has_decisive_piece(P8) || (outcome = :draw; break)
                m = choose_move(P8, S)
                m < 0 && (outcome = :draw; break)
                counts[1] += 1; m in legal || (fail[1] = true)
                u = make!(P8, m)
                counts[2] += 1; in_check(P8, prev_side > 0 ? 1 : -1) && (fail[2] = true)
                # (mover was prev_side; after make the mover must NOT be in check)
                counts[3] += 1; cheb(P8, P8.kw, P8.kb) <= 1 && (fail[3] = true)
                np = count(!iszero, P8.b)
                counts[4] += 1; (2 <= np <= 3) || (fail[4] = true)
                counts[5] += 1; P8.side == -prev_side || (fail[5] = true)
                if n <= 16
                    counts[6] += 1
                    P8.key == recompute_key(P8) || (fail[6] = true)
                    counts[7] += 1
                    mob = pseudo_mobility(P8, 1) + pseudo_mobility(P8, -1)
                    (0 <= mob < n * n * 4) || (fail[7] = true)
                    if rep == 1 && plies % 8 == 0
                        counts[8] += 1
                        fa = threat_field(P8, 1)
                        fb = field_by_cells(P8, 1)
                        fa == fb || (fail[8] = true)
                    end
                end
                counts[9] += 1
                P8.key in seen && (outcome = :draw; break)
                push!(seen, P8.key)
                prev_side = P8.side
                plies += 1
            end
            outcome === :none && (outcome = :draw)
            fail[9] |= (outcome in (:white, :black, :draw)) ? false : true
        end
    end
    # real determinism check: the same seeded start replayed twice must give
    # the identical game (plies, outcome)
    begin
        g = SM64(UInt64(cfg.seed + 7000 + 1))
        Pa = Pos(8); setup_kxk!(Pa, g, PIECE_R, true)
        isempty(legal_moves(Pa)) || begin
            Pb = Pos(8)
            copyto!(Pb.b, Pa.b); Pb.side = Pa.side; Pb.kw = Pa.kw; Pb.kb = Pa.kb
            Pb.key = Pa.key
            ra = playout!(Pa, S; max_plies = cfg.max_plies)
            rb = playout!(Pb, S; max_plies = cfg.max_plies)
            counts[10] += 1
            (ra[1] == rb[1] && ra[2] == rb[2] && ra[3] == rb[3]) || (fail[10] = true)
        end
    end
    widths = [26, 12]
    log(L, thead(["check", "status"], widths))
    for (i, c) in enumerate(checks)
        st = fail[i] ? P.bad * mark(false) * A_RESET : P.ok * mark(true) * A_RESET
        log(L, trow([c * " ×$(counts[i])", st], widths))
    end
    log(L, tfoot(widths))
    ok = !any(fail)
    log(L, "  " * (ok ? P.ok * t("t3_ok") * A_RESET : P.bad * "FAIL" * A_RESET))
    log(L)
    return Dict{String,Any}("name" => "T2 legality battery",
                            "status" => ok ? "PASS" : "FAIL",
                            "summary" => "boards 8/16/$(cfg.n) · checks ×$(sum(counts))")
end

# ── independent re-derivation of oracle children (used for verification) ─────
cheb_sq(n::Int, a::Int, b::Int) =
    max(abs((a ÷ n) - (b ÷ n)), abs((a % n) - (b % n)))

function oracle_children(o::Oracle, s::Int)
    bits = o.bits; n = o.n
    wk, wq, bk, stm = ounpack(bits, s)
    code = o.piece
    b = zeros(Int8, n * n)
    b[wk+1] = PIECE_K; b[wq+1] = code; b[bk+1] = Int8(-PIECE_K)
    ch = Int[]; captured = false; att = Int[]
    if stm == 0
        targets = strong_attacks!(b, n, wq, code, att)
        for dest in king_steps(n, wk)
            (dest == wq || dest == bk || cheb_sq(n, dest, bk) <= 1) && continue
            push!(ch, opack(bits, dest, wq, bk, 1))
        end
        for dest in targets
            (dest == wk || dest == bk) && continue
            push!(ch, opack(bits, wk, dest, bk, 1))
        end
    else
        for dest in king_steps(n, bk)
            dest == wk && continue
            cheb_sq(n, dest, wk) <= 1 && continue
            if dest == wq
                captured = true
                continue
            end
            b[bk+1] = Int8(0); b[dest+1] = Int8(-PIECE_K)
            hit = dest in strong_attacks!(b, n, wq, code, att)
            b[dest+1] = Int8(0); b[bk+1] = Int8(-PIECE_K)
            hit && continue
            push!(ch, opack(bits, wk, wq, dest, 0))
        end
    end
    return ch, captured
end

function pos_from_packed(o::Oracle, s::Int)
    bits = o.bits
    wk, wq, bk, stm = ounpack(bits, s)
    P = Pos(o.n)
    put!(P, wk, PIECE_K)
    put!(P, bk, Int8(-PIECE_K))
    put!(P, wq, o.piece)
    set_side!(P, stm == 0 ? 1 : -1)
    return P
end

# ── T3 · oracle self-verification ─────────────────────────────────────────────
function test_t3(cfg, P::Palette, L::Logger, rd::RunData)
    log(L, section(P, t("t3_title")))
    all_ok = true
    mono_krk = Tuple{Int,Int,Int}[]
    mono_kqk = Tuple{Int,Int,Int}[]
    widths = [8, 10, 12, 12, 12, 12, 14, 9]
    log(L, thead([t("board"), "piece", t("or_states"), t("or_edges"), t("or_won"),
                  t("or_mates"), t("or_max"), "status"], widths))
    pieces = Tuple{Int8,Char,Vector{Tuple{Int,Int,Int}}}[]
    cfg.krk && push!(pieces, (PIECE_R, 'R', mono_krk))
    cfg.kqk && push!(pieces, (PIECE_Q, 'Q', mono_kqk))
    for (code, sym, mono) in pieces
        prev_max = 0
        for n in sort(unique(cfg.oracle_ns))
            o = retro_oracle(n, code; log = (s -> log(L, s)))
            st = o.stats
            checks_ok = st["mates"] > 0 && st["won"] > 0
            push!(mono, (n, st["max_moves"], st["states"]))
            prev_max > st["max_moves"] && (checks_ok = false)
            prev_max = st["max_moves"]
            # structural sampling
            g = SM64(UInt64(cfg.seed + 3100 + n))
            NSQ = n * n
            samples = 0; tries = 0
            while samples < 400 && tries < 40000
                tries += 1
                wk = randint!(g, 0, NSQ - 1); wq = randint!(g, 0, NSQ - 1)
                bk = randint!(g, 0, NSQ - 1)
                (wk == wq || wk == bk || wq == bk) && continue
                cheb_sq(n, wk, bk) <= 1 && continue
                for (s, stm) in ((opack(o.bits, wk, wq, bk, 0), 0),
                                 (opack(o.bits, wk, wq, bk, 1), 1))
                    d = Int(o.dtm[s+1])
                    d < 0 && continue
                    ch, captured = oracle_children(o, s)
                    if d == 0
                        # must be a checkmate with Black to move
                        stm == 1 || (checks_ok = false; continue)
                        isempty(ch) || (checks_ok = false; continue)
                        Q = pos_from_packed(o, s)
                        (in_check(Q, -1) && isempty(legal_moves(Q))) ||
                            (checks_ok = false)
                    elseif d > 0 && stm == 0
                        found = false
                        for c in ch
                            Int(o.dtm[c+1]) == d - 1 && (found = true; break)
                        end
                        found || (checks_ok = false)
                    elseif d > 0 && stm == 1
                        captured && (checks_ok = false; continue)
                        isempty(ch) && (checks_ok = false; continue)
                        mx = 0
                        for c in ch
                            dv = Int(o.dtm[c+1])
                            dv < 0 && (mx = -1; break)
                            mx = max(mx, dv)
                        end
                        (mx == d - 1) || (checks_ok = false)
                    end
                end
                samples += 1
            end
            log(L, "  " * t("t3_struct") * " ($sym, n=$n): $samples " * mark(checks_ok))
            all_ok &= checks_ok
            stx = checks_ok ? P.ok * mark(true) * A_RESET : P.bad * mark(false) * A_RESET
            log(L, trow([string(n), string(sym), string(st["states"]),
                         string(st["edges"]), string(st["won"]), string(st["mates"]),
                         string(st["max_moves"]), stx], widths))
        end
    end
    log(L, tfoot(widths))
    # known landmark: KRK mate in 1 on the 8x8 board (bk a8, wk b6, R h1 → Rh8#)
    if 8 in cfg.oracle_ns && cfg.krk
        o8 = retro_oracle(8, PIECE_R)
        s = opack(o8.bits, 41, 7, 56, 0)     # wk b6 (41), Rh1 (7), bk a8 (56)
        lm = Int(o8.dtm[s+1]) == 1
        all_ok &= lm
        log(L, "  KRK landmark Rh8# (a8/b6/h1 → DTM 1): " * mark(lm))
    end
    log(L, "  " * t("t3_mono") * ": KRK " *
            join(["n=$(a): $(b)m" for (a, b, c) in mono_krk], ", ") *
            " · KQK " * join(["n=$(a): $(b)m" for (a, b, c) in mono_kqk], ", "))
    rd.dtmpts = isempty(mono_krk) ? mono_kqk : mono_krk
    log(L)
    return Dict{String,Any}("name" => "T3 oracle self-verification",
                            "status" => all_ok ? "PASS" : "FAIL",
                            "summary" => "max DTM: " *
                             join(["n=$(a): $(b)m" for (a, b) in rd.dtmpts], " · "))
end

# ── T4 · trap census: particle solver vs exact oracle (the E1 link) ───────────
function test_t4(cfg, P::Palette, L::Logger, rd::RunData)
    log(L, section(P, t("t4_title")))
    S = Solver(cfg.mu, cfg.lam)
    n = maximum(cfg.oracle_ns)
    n <= 13 || (n = 13)
    target = cfg.trap_positions
    csv = Vector{Vector{String}}()
    widths = [26, 12, 12, 12, 12]
    log(L, thead(["metric", "n", "count", "share", "status"], widths))
    all_ok = true
    for (code, sym) in ((PIECE_R, "KRK"), (PIECE_Q, "KQK"))
        cfg.krk || code != PIECE_R || continue
        cfg.kqk || code != PIECE_Q || continue
        o = retro_oracle(n, code)
        g = SM64(UInt64(cfg.seed + 4200 + (code == PIECE_R ? 1 : 2)))
        NSQ = n * n
        won_s = drawn_s = lost_s = 0
        correct = slow = blunder = 0
        maxres = shortened = escaped = 0
        res_loss = 0.0
        tries = 0
        while (won_s < target || lost_s < target) && tries < target * 80
            tries += 1
            wk = randint!(g, 0, NSQ - 1); wq = randint!(g, 0, NSQ - 1)
            bk = randint!(g, 0, NSQ - 1)
            (wk == wq || wk == bk || wq == bk) && continue
            cheb_sq(n, wk, bk) <= 1 && continue
            s0 = opack(o.bits, wk, wq, bk, 0)
            d = Int(o.dtm[s0+1])
            if d >= 1 && won_s < target
                Pq = pos_from_packed(o, s0)
                isempty(legal_moves(Pq)) && continue
                m = choose_move(Pq, S)
                m >= 0 || continue
                u = make!(Pq, m)
                d2 = oracle_query(o, Pq)
                won_s += 1
                cls = d2 == -1 ? (blunder += 1; "blunder") :
                      d2 == d - 1 ? (correct += 1; "correct") : (slow += 1; "slow")
                push!(csv, [sym, "won", string(d), string(d2), cls,
                            sqname(n, mfrom(m)), sqname(n, mto(m))])
            elseif d == -1 && lost_s < target
                s1 = opack(o.bits, wk, wq, bk, 1)
                d1 = Int(o.dtm[s1+1])
                d1 >= 1 || continue
                Pq = pos_from_packed(o, s1)
                isempty(legal_moves(Pq)) && continue
                m = choose_move(Pq, S)
                m >= 0 || continue
                u = make!(Pq, m)
                captured = u[2] != 0
                lost_s += 1
                if captured || oracle_query(o, Pq) == -1
                    escaped += 1
                    push!(csv, [sym, "lost", string(d1), "-1", "escape",
                                sqname(n, mfrom(m)), sqname(n, mto(m))])
                else
                    d2 = oracle_query(o, Pq)
                    loss = (d1 - 1) - d2
                    res_loss += loss
                    if d2 == d1 - 1
                        maxres += 1
                    else
                        shortened += 1
                    end
                    push!(csv, [sym, "lost", string(d1), string(d2),
                                loss == 0 ? "resist" : "shorten",
                                sqname(n, mfrom(m)), sqname(n, mto(m))])
                end
            end
        end
        brate = won_s > 0 ? blunder / won_s : 0.0
        row_ok = brate <= 0.30
        all_ok &= row_ok
        c1 = row_ok ? P.ok * mark(true) * A_RESET : P.warn * mark(false) * A_RESET
        log(L, trow(["$sym · " * t("t4_won"), string(n), string(won_s),
                     @sprintf("%.1f%%", 100 * correct / max(won_s, 1)) * " " * t("t4_correct"),
                     ""], widths))
        log(L, trow(["", "", string(slow), @sprintf("%.1f%%", 100 * slow / max(won_s, 1)) * " " * t("t4_slow"), ""], widths))
        log(L, trow(["", "", string(blunder), @sprintf("%.1f%%", 100 * brate) * " " * t("t4_blund"), c1], widths))
        log(L, trow(["$sym · " * t("t4_lost") * " (K side)", string(n), string(lost_s),
                     @sprintf("%.1f%%", lost_s > 0 ? 100 * maxres / lost_s : 0) * " " * "max-res",
                     ""], widths))
        log(L, trow(["", "", string(shortened),
                     @sprintf("%.2f", lost_s > 0 ? res_loss / lost_s : 0) * " " * "mean-loss", ""], widths))
        log(L, trow(["", "", string(escaped), @sprintf("%.1f%%", lost_s > 0 ? 100 * escaped / lost_s : 0) * " escape", ""], widths))
        log(L, tsep(widths))
    end
    log(L, tfoot(widths))
    log(L, "  " * t("t4_trate") * " → CSV: trap_census.csv")
    log(L)
    return Dict{String,Any}("name" => "T4 trap census", "status" => all_ok ? "PASS" : "WARN",
                            "summary" => "sample $((cfg.trap_positions))x2 per scenario",
                            "csv_rows" => csv)
end

# oracle cache (T3/T4 share the big tables)
const ORACLE_CACHE = Dict{Tuple{Int,Int8},Oracle}()

function get_oracle(n::Int, code::Int8)
    haskey(ORACLE_CACHE, (n, code)) && return ORACLE_CACHE[(n, code)]
    o = retro_oracle(n, code)
    ORACLE_CACHE[(n, code)] = o
    return o
end

# ── T5 · scaling benchmark ────────────────────────────────────────────────────
function test_t5(cfg, P::Palette, L::Logger, rd::RunData)
    log(L, section(P, t("t5_title")))
    S = Solver(cfg.mu, cfg.lam)
    widths = [8, 18, 18, 16]
    log(L, thead([t("board"), t("t5_move"), t("t5_ply"), t("t5_nodes")], widths))
    rd.scaling = Tuple{Int,Float64,Float64,Float64,Int}[]
    slopes = Float64[]
    for n in cfg.scaling_ns
        g = SM64(UInt64(cfg.seed + 5500 + n))
        times = Float64[]
        nodes = 0
        for rep in 1:cfg.scaling_pos
            Pq = fresh_endgame(n, PIECE_R, true, g)
            cnt = [0]
            REPS = n >= 64 ? 4 : 16
            t0 = time()
            for _ in 1:REPS
                choose_move(Pq, S, cnt)
            end
            push!(times, (time() - t0) / REPS)
            nodes += cnt[1] ÷ REPS
        end
        tmean = sum(times) / length(times)
        # one full playout for the per-ply number
        Pq = fresh_endgame(n, PIECE_R, true, g)
        tp = time()
        pl, _, _ = playout!(Pq, S; max_plies = min(cfg.max_plies, 256))
        tp = time() - tp
        per_ply = pl > 0 ? tp / pl : 0.0
        push!(rd.scaling, (n, tmean, tmean, tmean, max(1, nodes ÷ cfg.scaling_pos)))
        log(L, trow([string(n), @sprintf("%.3g s", tmean),
                     @sprintf("%.3g s", per_ply), @sprintf("%d", nodes ÷ cfg.scaling_pos)], widths))
        length(rd.scaling) > 1 && push!(slopes,
            Base.log(rd.scaling[end][2] / rd.scaling[end-1][2]) /
            Base.log(rd.scaling[end][1] / rd.scaling[end-1][1]))
    end
    log(L, tfoot(widths))
    slope = isempty(slopes) ? NaN : slopes[end]
    ok = isnan(slope) || (0.5 <= slope <= 4.0)
    log(L, "  " * t("t5_slope") * ": " * @sprintf("%.2f", slope) *
            "  (measured per-move cost is polynomial in n — T14(ii)) " *
            (ok ? P.ok * mark(true) * A_RESET : P.warn * mark(false) * A_RESET))
    log(L)
    return Dict{String,Any}("name" => "T5 scaling", "status" => ok ? "PASS" : "WARN",
                            "summary" => "slope ≈ $(round(slope, digits = 2)) · " *
                             "t(n=$(cfg.scaling_ns[end])) = $(@sprintf("%.3g", rd.scaling[end][2])) s")
end

# ── playout worker (used by T8; deterministic per index; particle policy) ─────
function playout_job(cfg, piece::Int8, idx::Int)
    g = SM64(UInt64(cfg.seed + 99000 + (piece == PIECE_R ? 0 : 500) + idx))
    Pq = fresh_endgame(cfg.n, piece, isodd(idx), g)
    S = Solver(cfg.mu, cfg.lam)
    pl, outcome, reason = playout!(Pq, S; max_plies = cfg.max_plies)
    wk = Pq.kw; wq = -1; bk = Pq.kb
    for sq in 0:(cfg.n * cfg.n - 1)
        abs(Int(Pq.b[sq+1])) in (4, 5) && (wq = sq; break)
    end
    return (idx = idx, stm0 = isodd(idx), plies = pl, outcome = outcome,
            reason = reason, wk = wk, wq = wq, bk = bk)
end

# ── paired policy worker: EVERY policy gets the SAME sampled starts ───────────
#   position seed depends only on (scenario, idx); the playout rng also folds
#   in the policy index, so deterministic policies face identical openings.
function policy_job(cfg, piece::Int8, scen_off::Int, idx::Int,
                    ps::PolicySpec, pidx::Int)
    g_pos = SM64(UInt64(cfg.seed + 99000 + scen_off + idx))
    g_play = SM64(UInt64(cfg.seed + 77013 + 1000 * pidx + scen_off + idx))
    Pq = fresh_endgame(cfg.n, piece, isodd(idx), g_pos)
    pl, outcome, reason = playout!(Pq, ps, g_play; max_plies = cfg.max_plies)
    wk = Pq.kw; wq = -1; bk = Pq.kb
    for sq in 0:(cfg.n * cfg.n - 1)
        abs(Int(Pq.b[sq+1])) in (4, 5) && (wq = sq; break)
    end
    return (idx = idx, stm0 = isodd(idx), plies = pl, outcome = outcome,
            reason = reason, wk = wk, wq = wq, bk = bk)
end

# policy verdict tier from its own plurality share and Wilson floor:
#   F = forced (CI floor > 50%), L = leaning (plurality >= 75%), I = other
verdict_tier(p::Float64, lo::Float64) = lo > 0.5 ? "F" : p >= 0.75 ? "L" : "I"

# ── T7 · MAIN TEST: the PARTIAL POLICY VERDICT ────────────────────────────────
#
#   An ensemble of named policies (each a complete approximator of the
#   dynamics) plays paired playouts on identical sampled starts, both sides.
#   Reported: per policy × scenario outcome shares, per-policy pooled
#   verdicts with tiers (F/L/I), a consensus class, the pooled verdict with
#   Wilson CI, and an honest coverage block (sampled starts and plies vs the
#   scenario state-space estimate).  The output is explicitly labelled a
#   PARTIAL POLICY VERDICT — evidence ladder: FULL > WEAK > ULTRA-WEAK >
#   PARTIAL POLICY; this test never claims more than the last rung.
# ──────────────────────────────────────────────────────────────────────────────
function test_t7(cfg, P::Palette, L::Logger, rd::RunData)
    log(L, section(P, t("t7_title")))
    scenarios = Tuple{Int8,String,Int}[]
    cfg.krk && push!(scenarios, (PIECE_R, "KRK", 0))
    cfg.kqk && push!(scenarios, (PIECE_Q, "KQK", 500))
    isempty(scenarios) && (log(L, "  no scenarios enabled"); return Dict{String,Any}())
    pols = isempty(cfg.policies) ? [:particle] : cfg.policies
    specs = [build_policy(pn, cfg.mu, cfg.lam) for pn in pols]
    labels = [POLICY_LABEL[ps.name] for ps in specs]
    geo(cfg.n); zobrist(cfg.n)     # pre-build shared caches before playouts
    G = length(specs) * length(scenarios) * cfg.playouts_main
    log(L, "  " * t("pol_ens") * ": " * P.accent * join(labels, " + ") * A_RESET *
            " · " * t("main_runs") * " $(cfg.playouts_main) × " *
            "$(length(scenarios)) × $(length(specs)) = $G")
    log(L, "  " * t("tier_legend"))
    log(L)
    bar = Bar(G, "T7", P)
    job = 0
    runs = Dict{Tuple{Symbol,Int8},Vector{NamedTuple}}()
    for (pidx, ps) in enumerate(specs)
        for (piece, sname, off) in scenarios
            out = Vector{NamedTuple}(undef, cfg.playouts_main)
            for i in 1:cfg.playouts_main
                out[i] = policy_job(cfg, piece, off, i, ps, pidx - 1)
                job += 1
                tick!(bar, job)
            end
            runs[(ps.name, piece)] = out
        end
    end
    done!(bar)
    println()
    # ── per policy × scenario table ───────────────────────────────────────────
    widths = [9, 9, 7, 7, 9, 9, 9, 3]
    log(L, thead([t("policy"), t("scenario"), t("plays"), t("out_draw"),
                  t("out_white"), t("out_black"), t("plies_hdr"), "V"], widths))
    pol_scen = Vector{Dict{String,Any}}()
    pol_csv = Vector{Vector{String}}()
    csv_rows = Vector{Vector{String}}()
    # pooled per outcome across EVERYTHING
    allw = allb = alld = 0
    # pooled per scenario (all policies) for chart2 fallback + JSON
    scen_w = Dict{Int8,Int}(); scen_b = Dict{Int8,Int}(); scen_d = Dict{Int8,Int}()
    scen_plies = Dict{Int8,Float64}()
    for (piece, sname, off) in scenarios
        scen_w[piece] = 0; scen_b[piece] = 0; scen_d[piece] = 0; scen_plies[piece] = 0.0
    end
    for (pidx, ps) in enumerate(specs)
        for (piece, sname, off) in scenarios
            out = runs[(ps.name, piece)]
            cw = count(r -> r.outcome == :white, out)
            cb = count(r -> r.outcome == :black, out)
            cd = count(r -> r.outcome == :draw, out)
            N = length(out)
            mean_plies = sum(r.plies for r in out) / max(N, 1)
            allw += cw; allb += cb; alld += cd
            scen_w[piece] += cw; scen_b[piece] += cb; scen_d[piece] += cd
            scen_plies[piece] += mean_plies
            # tier on the row's own plurality
            trio = [(cd, :draw), (cw, :white), (cb, :black)]
            sort!(trio, by = x -> -x[1])
            (_, lo_) = wilson(trio[1][1], N)
            tier = verdict_tier(trio[1][1] / N, lo_)
            log(L, trow([POLICY_LABEL[ps.name], sname, string(N),
                         @sprintf("%.1f%%", 100 * cd / N),
                         @sprintf("%.1f%%", 100 * cw / N),
                         @sprintf("%.1f%%", 100 * cb / N),
                         @sprintf("%.1f", mean_plies), tier], widths))
            push!(pol_scen, Dict{String,Any}(
                "policy" => POLICY_LABEL[ps.name], "scenario" => sname, "n" => cfg.n,
                "games" => N, "draw" => cd, "white" => cw, "black" => cb,
                "p_draw" => cd / N, "p_white" => cw / N, "p_black" => cb / N,
                "mean_plies" => mean_plies, "tier" => tier))
            push!(pol_csv, [POLICY_LABEL[ps.name], sname, string(cfg.n), string(N),
                            string(cd), string(cw), string(cb),
                            @sprintf("%.4f", cd / N), @sprintf("%.4f", cw / N),
                            @sprintf("%.4f", cb / N), @sprintf("%.2f", mean_plies),
                            tier])
            for r in out
                push!(csv_rows, [POLICY_LABEL[ps.name], sname, string(cfg.n),
                                 string(r.idx), r.stm0 ? "white" : "black",
                                 string(r.plies), string(r.outcome), r.reason,
                                 sqname(cfg.n, r.wk), r.wq >= 0 ? sqname(cfg.n, r.wq) : "-",
                                 sqname(cfg.n, r.bk)])
            end
        end
    end
    log(L, tfoot(widths))
    # ── per-policy pooled verdicts (both scenarios merged) ────────────────────
    log(L, "  " * t("pool") * " · " * t("policy") * " → " * t("verdict"))
    pol_pooled = Vector{Dict{String,Any}}()
    plurs = Symbol[]
    rd.policy_outcomes = Tuple{String,Float64,Float64,Float64,Float64,Float64,Float64}[]
    for (pidx, ps) in enumerate(specs)
        pw = pb = pd = 0; tpl = 0
        for (piece, sname, off) in scenarios
            out = runs[(ps.name, piece)]
            pw += count(r -> r.outcome == :white, out)
            pb += count(r -> r.outcome == :black, out)
            pd += count(r -> r.outcome == :draw, out)
            tpl += sum(r.plies for r in out)
        end
        N = pw + pb + pd
        trio = [(pd, :draw), (pw, :white), (pb, :black)]
        sort!(trio, by = x -> -x[1])
        (pp, plo, _) = wilson(trio[1][1], N)
        tier = verdict_tier(pp, plo)
        push!(plurs, trio[1][2])
        (pD, lD, uD) = wilson(pd, N); (pW, lW, uW) = wilson(pw, N)
        (pB, lB, uB) = wilson(pb, N)
        push!(pol_pooled, Dict{String,Any}(
            "policy" => POLICY_LABEL[ps.name], "games" => N, "mean_plies" => tpl / N,
            "p_draw" => pD, "ci_draw" => [lD, uD],
            "p_white" => pW, "ci_white" => [lW, uW],
            "p_black" => pB, "ci_black" => [lB, uB],
            "verdict_sym" => string(trio[1][2]), "verdict_tier" => tier))
        push!(rd.policy_outcomes, (POLICY_LABEL[ps.name], pD, pW, pB,
                                   (uD - lD) / 2, (uW - lW) / 2, (uB - lB) / 2))
        log(L, @sprintf("      %-9s N=%-4d %s: %5.1f%% (CI- %5.1f%%)  [%s]",
                        POLICY_LABEL[ps.name], N,
                        trio[1][2] == :draw ? t("out_draw") :
                        trio[1][2] == :white ? t("out_white") : t("out_black"),
                        100 * pp, 100 * plo, tier))
    end
    # ── pooled verdict + consensus ────────────────────────────────────────────
    Nall = allw + allb + alld
    (pD, lD, _) = wilson(alld, Nall)
    (pW, lW, _) = wilson(allw, Nall)
    (pB, lB, _) = wilson(allb, Nall)
    sc_rows = Vector{Dict{String,Any}}()
    for (piece, sname, off) in scenarios
        Ns = scen_w[piece] + scen_b[piece] + scen_d[piece]
        (sD, slD, suD) = wilson(scen_d[piece], Ns)
        (sW, slW, suW) = wilson(scen_w[piece], Ns)
        (sB, slB, suB) = wilson(scen_b[piece], Ns)
        push!(sc_rows, Dict{String,Any}(
            "scenario" => sname, "n" => cfg.n, "playouts" => Ns,
            "policies" => length(specs),
            "p_draw" => sD, "ci_draw" => [slD, suD],
            "p_white" => sW, "ci_white" => [slW, suW],
            "p_black" => sB, "ci_black" => [slB, suB],
            "mean_plies" => scen_plies[piece] / length(specs)))
    end
    cand = [(pD, lD, :draw), (pW, lW, :white), (pB, lB, :black)]
    sort!(cand, by = x -> -x[1])
    best = cand[1][3]; bestlo = cand[1][2]; bestp = cand[1][1]
    if bestlo > 0.5
        vkey = best == :draw ? "v_draw" : best == :white ? "v_white" : "v_black"
        vbig = best == :draw ? "DRAW" : best == :white ? "WHITE WINS" : "BLACK WINS"
    else
        vkey = "v_inconc"; vbig = "INCONCLUSIVE"
    end
    vtitle = t(vkey)
    agree = count(s -> s == best, plurs)
    cons_key = agree == length(plurs) ? "unanimous" :
               agree * 2 > length(plurs) ? "majority" : "split"
    cons_str = cons_key == "unanimous" ? t("cons_unan") :
               cons_key == "majority" ? t("cons_major") : t("cons_split")
    best_lab = best == :draw ? t("out_draw") :
               best == :white ? t("out_white") : t("out_black")
    # ── honest coverage block ─────────────────────────────────────────────────
    n = cfg.n
    states_est = Float64(n * n) * Float64(n * n - 1) * Float64(n * n - 2) * 2.0
    unique_starts = length(scenarios) * cfg.playouts_main    # paired design
    total_plies = sum(sum(r.plies for r in runs[(ps.name, piece)])
                       for ps in specs for (piece, sname, off) in scenarios)
    log(L)
    log(L, "  " * t("cov_starts") * ": $unique_starts · " * t("cov_plies") *
            ": $total_plies")
    log(L, "  " * t("cov_states") * " (KXK, n=$n): ≈" * @sprintf("%.3g", states_est) *
            " · " * t("cov_share") * ": " * @sprintf("%.2e", unique_starts / states_est))
    log(L, "  " * t("verdict") * ": " * P.hl * vtitle * A_RESET)
    log(L, "  " * t("consensus") * ": " * P.accent * cons_str * A_RESET *
            " · " * t("pol_ens") * ": " * join(labels, "+") *
            " · " * best_lab * " " * @sprintf("%.1f%% (CI- %.1f%%)", 100 * bestp, 100 * bestlo))
    log(L, "  " * P.dim * t("v_ladder") * A_RESET)
    println()
    verdict_art(P, vbig,
        t("pol_ens") * ": " * join(labels, "+") * " · " * t("consensus") * ": " *
        cons_str * " · " * best_lab * " " *
        @sprintf("%.1f%% (CI- %.1f%%)", 100 * bestp, 100 * bestlo))
    rd.outcomes = Tuple{String,Float64,Float64,Float64,Float64,Float64,Float64}[]
    for row in sc_rows
        (lD, uD) = row["ci_draw"]; (lW, uW) = row["ci_white"]; (lB, uB) = row["ci_black"]
        push!(rd.outcomes, (row["scenario"], row["p_draw"], row["p_white"],
                            row["p_black"], (uD - lD) / 2, (uW - lW) / 2, (uB - lB) / 2))
    end
    rd.chart2_note = "n = $(cfg.n) · $(length(specs)) " * t("policy") *
                     " × $(length(scenarios)) " * t("scenario") * " · $G " * t("plays")
    return Dict{String,Any}(
        "name" => "T7 MAIN partial-policy verdict",
        "status" => "PASS",
        "verdict_class" => "partial_policy",
        "verdict" => string(best), "verdict_title" => vtitle,
        "consensus" => cons_key,
        "evidence_ladder" => t("v_ladder"),
        "policies" => pol_pooled,
        "policy_scenarios" => pol_scen,
        "scenarios" => sc_rows,
        "coverage" => Dict{String,Any}(
            "unique_starts" => unique_starts, "games_total" => Nall,
            "plies_total" => total_plies, "states_estimate" => states_est,
            "coverage_share" => unique_starts / states_est),
        "policy_csv" => pol_csv, "csv_rows" => csv_rows)
end

# ── T8 · explicit outcome check ───────────────────────────────────────────────
function test_t8(cfg, P::Palette, L::Logger, rd::RunData)
    log(L, section(P, t("t8_title")))
    expect = cfg.expect
    expect === :none && (expect = :draw)
    piece = cfg.krk ? PIECE_R : PIECE_Q
    geo(cfg.n); zobrist(cfg.n)
    bar = Bar(cfg.playouts_check, "T8", P)
    out = Vector{NamedTuple}(undef, cfg.playouts_check)
    for i in 1:cfg.playouts_check
        out[i] = playout_job(cfg, piece, i)
        tick!(bar, i)
    end
    done!(bar)
    println()
    cw = count(r -> r.outcome == :white, out)
    cb = count(r -> r.outcome == :black, out)
    cd = count(r -> r.outcome == :draw, out)
    N = length(out)
    log(L, "  " * t("scenario") * ": KRK · n=$(cfg.n) · " * t("plays") * " $N · " *
            t("policy") * ": PARTICLE")
    log(L, "  " * t("t8_expect") * ": " * t(expect == :draw ? "out_draw" :
        expect == :white ? "out_white" : "out_black"))
    for (lab, k) in ((t("out_draw"), cd), (t("out_white"), cw), (t("out_black"), cb))
        (p, lo, hi) = wilson(k, N)
        log(L, @sprintf("      %-14s %3d  %5.1f%%  CI [%5.1f%%, %5.1f%%]",
                        lab, k, 100 * p, 100 * lo, 100 * hi))
    end
    pe, lo, hi = expect === :draw ? wilson(cd, N) :
                 expect === :white ? wilson(cw, N) : wilson(cb, N)
    others = expect === :draw ? (cw + cb) : expect === :white ? (cd + cb) : (cd + cw)
    if lo > 0.5
        verdict = "agree"; vbig = "AGREE"
        log(L, "  " * P.ok * t("t8_agree") * A_RESET)
    elseif pe > others / N
        verdict = "weak"; vbig = "WEAK +"
        log(L, "  " * P.warn * t("t8_weak") * A_RESET)
    else
        verdict = "disagree"; vbig = "DISAGREE"
        log(L, "  " * P.bad * t("t8_dis") * A_RESET)
    end
    println()
    verdict_art(P, vbig, @sprintf("%s: %.1f%%", t("share"), 100 * pe), false)
    println(P.dim * "  ⚠ " * t("v_honest_one") * A_RESET)
    println()
    return Dict{String,Any}("name" => "T8 explicit outcome check",
                            "status" => "PASS", "expect" => string(expect),
                            "verdict" => verdict, "p_expect" => pe,
                            "n" => N, "white" => cw, "black" => cb, "draw" => cd)
end

# ── T9 · flow showcase (K3 field + trajectories on the big board) ─────────────
function test_t9(cfg, P::Palette, L::Logger, rd::RunData)
    log(L, section(P, t("t9_title")))
    g = SM64(UInt64(cfg.seed + 61000))
    Pq = fresh_battle(cfg.n, cfg.flow_rooks, g)
    S = Solver(cfg.mu, cfg.lam)
    theta = threat_field(Pq, 1)
    # pieces for the chart
    pieces = Tuple{Int,Char,Int}[]
    tracks = Dict{Int8,Vector{Int}}()
    for sq in 0:(cfg.n * cfg.n - 1)
        p = Pq.b[sq+1]
        p == 0 && continue
        ap = abs(Int(p))
        ch = ap == 6 ? 'K' : ap == 4 ? 'R' : '?'
        push!(pieces, (sq, ch, Int(sign(p))))
        if p == PIECE_R || p == -PIECE_R
            haskey(tracks, p) || (tracks[p] = Int[sq])
        end
    end
    # trace trajectories of the first rook of each side
    plies = 0
    while plies < cfg.flow_plies
        moves = legal_moves(Pq)
        isempty(moves) && break
        m = choose_move(Pq, S)
        m < 0 && break
        f = mfrom(m); p = Pq.b[f+1]
        haskey(tracks, p) && push!(tracks[p], mto(m))
        make!(Pq, m)
        plies += 1
        has_decisive_piece(Pq) || break
    end
    paths = Tuple{Int,Vector{Int}}[]
    for (p, sqs) in tracks
        length(sqs) >= 1 && push!(paths, (p > 0 ? 1 : -1, sqs))
    end
    vmax = maximum(theta)
    mean_pressure = sum(theta) / (cfg.n * cfg.n)
    log(L, "  " * t("board") * ": $(cfg.n)x$(cfg.n) · " * t("c3_bar") *
            " max = $vmax · mean = $(round(mean_pressure, digits = 4))")
    log(L, "  " * t("main_plies") * ": $plies → charts/chart3_flow_$(cfg.n)x$(cfg.n).png")
    rd.flow_n = cfg.n
    rd.flow_field = theta
    rd.flow_pieces = pieces
    rd.flow_paths = paths
    log(L)
    return Dict{String,Any}("name" => "T9 flow showcase", "status" => "PASS",
                            "max_field" => vmax,
                            "mean_field" => mean_pressure, "plies" => plies)
end

# ──────────────────────────────────────────────────────────────────────────────
# INTERACTIVE MENU (RU/EN) + parameter editor
# ──────────────────────────────────────────────────────────────────────────────

function ask(P::Palette, prompt::String)
    print(P.accent * "  " * prompt * A_RESET)
    flush(stdout)
    s = try
        strip(readline(stdin))
    catch
        ""
    end
    return String(s)
end

function show_params(cfg, P::Palette)
    println(P.title * "  " * t("p_header") * A_RESET)
    items = [
        (1,  t("prm_n"),         "$(cfg.n)"),
        (2,  t("prm_oracle"),    join(cfg.oracle_ns, ",")),
        (3,  t("prm_play"),      string(cfg.playouts_main)),
        (4,  t("prm_check"),     string(cfg.playouts_check)),
        (5,  t("prm_maxplies"),  string(cfg.max_plies)),
        (6,  t("prm_mu"),        string(cfg.mu)),
        (7,  t("prm_lam"),       string(cfg.lam)),
        (8,  t("prm_seed"),      string(cfg.seed)),
        (9,  t("prm_dpi"),       string(cfg.dpi)),
        (10, t("prm_fig"),       "$(cfg.fig_w)x$(cfg.fig_h)"),
        (11, t("prm_scaling"),   join(cfg.scaling_ns, ",")),
        (12, t("prm_traps"),     string(cfg.trap_positions)),
        (13, t("prm_krk"),       cfg.krk ? t("c_on") : t("c_off")),
        (14, t("prm_kqk"),       cfg.kqk ? t("c_on") : t("c_off")),
        (15, t("prm_expect"),    string(cfg.expect)),
        (16, t("prm_flowr"),     string(cfg.flow_rooks)),
        (17, t("prm_outdir"),    cfg.outdir),
        (18, t("prm_lang"),      string(cfg.lang)),
        (19, t("prm_policies"),  join(string.(cfg.policies), ",")),
    ]
    for (k, name, val) in items
        println(@sprintf("   %s%2d%s │ %s%-38s%s %s= %s%s",
                        P.accent, k, A_RESET, P.dim, name, A_RESET,
                        P.dim, A_RESET, val))
    end
    println()
end

function edit_params(cfg, P::Palette)
    while true
        println()
        show_params(cfg, P)
        s = ask(P, "param> ")
        isempty(s) && return
        k = tryparse(Int, s)
        k === nothing && (println(P.bad * "  " * t("p_bad") * A_RESET); continue)
        if k == 1
            v = tryparse(Int, ask(P, "n = ")); v !== nothing && 4 <= v <= 127 && (cfg.n = v)
        elseif k == 2
            v = ask(P, "n,n,... = ")
            try cfg.oracle_ns = [clamp(parse(Int, x), 3, 13) for x in split(v, ",")] catch; println(P.bad * t("p_bad") * A_RESET) end
        elseif k == 3
            v = tryparse(Int, ask(P, "> ")); v !== nothing && v > 0 && (cfg.playouts_main = v)
        elseif k == 4
            v = tryparse(Int, ask(P, "> ")); v !== nothing && v > 0 && (cfg.playouts_check = v)
        elseif k == 5
            v = tryparse(Int, ask(P, "> ")); v !== nothing && v >= 8 && (cfg.max_plies = v)
        elseif k == 6
            v = tryparse(Float64, ask(P, "mu = ")); v !== nothing && (cfg.mu = v)
        elseif k == 7
            v = tryparse(Float64, ask(P, "lam = ")); v !== nothing && (cfg.lam = v)
        elseif k == 8
            v = tryparse(Int, ask(P, "seed = ")); v !== nothing && (cfg.seed = v)
        elseif k == 9
            v = tryparse(Int, ask(P, "dpi = ")); v !== nothing && v >= 72 && (cfg.dpi = v)
        elseif k == 10
            v = ask(P, "WxH = ")
            try p = split(v, "x"); cfg.fig_w = parse(Float64, p[1]); cfg.fig_h = parse(Float64, p[2]) catch; println(P.bad * t("p_bad") * A_RESET) end
        elseif k == 11
            v = ask(P, "n,n,... = ")
            try cfg.scaling_ns = [clamp(parse(Int, x), 4, 127) for x in split(v, ",")] catch; println(P.bad * t("p_bad") * A_RESET) end
        elseif k == 12
            v = tryparse(Int, ask(P, "> ")); v !== nothing && v >= 10 && (cfg.trap_positions = v)
        elseif k == 13
            cfg.krk = !cfg.krk
        elseif k == 14
            cfg.kqk = !cfg.kqk
        elseif k == 15
            v = Symbol(lowercase(ask(P, t("sel_exp"))))
            v in (:draw, :white, :black, :none) && (cfg.expect = v)
        elseif k == 16
            v = tryparse(Int, ask(P, "> ")); v !== nothing && 1 <= v <= 12 && (cfg.flow_rooks = v)
        elseif k == 17
            cfg.outdir = ask(P, "dir = ")
        elseif k == 18
            v = lowercase(ask(P, "ru/en = "))
            v in ("ru", "en") && (cfg.lang = Symbol(v))
        elseif k == 19
            cfg.policies = parse_policies(ask(P, t("sel_pol")))
        else
            println(P.bad * "  " * t("p_bad") * A_RESET)
        end
    end
end

function show_menu(cfg, P::Palette)
    println(hr(P, '─'))
    println(P.title * "  ▌ " * t("menu_title") * A_RESET * "  " *
            P.dim * "· " * t("menu_hint") * A_RESET)
    println(hr(P, '─'))
    items = [
        ("1", t("m_lab"), P.accent),
        ("2", t("m_t1"), P.dim), ("3", t("m_t2"), P.dim),
        ("4", t("m_t3"), P.dim), ("5", t("m_t4"), P.dim),
        ("6", t("m_t5"), P.dim), ("7", t("m_t7"), P.bad),
        ("8", t("m_t8"), P.dim), ("9", t("m_flow"), P.dim),
    ]
    for (k, s, c) in items
        println("   " * P.accent * k * A_RESET * " │ " * c * s * A_RESET)
    end
    println("   " * P.accent * "C" * A_RESET * " │ " * t("m_params"))
    println("   " * P.accent * "L" * A_RESET * " │ " * t("m_lang"))
    println("   " * P.accent * "Q" * A_RESET * " │ " * t("m_quit"))
    println(hr(P, '─'))
end

function menu_loop(cfg, P::Palette)
    while true
        println()
        banner(P, cfg)
        show_menu(cfg, P)
        s = uppercase(ask(P, t("m_prompt")))
        if s == "1"
            run_lab(cfg, P)
            wait_enter(P)
        elseif s == "2"
            single_test(cfg, P, "t1"); wait_enter(P)
        elseif s == "3"
            single_test(cfg, P, "t2"); wait_enter(P)
        elseif s == "4"
            single_test(cfg, P, "t3"); wait_enter(P)
        elseif s == "5"
            single_test(cfg, P, "t4"); wait_enter(P)
        elseif s == "6"
            single_test(cfg, P, "t5"); wait_enter(P)
        elseif s == "7"
            single_test(cfg, P, "t7"); wait_enter(P)
        elseif s == "8"
            single_test(cfg, P, "t8"); wait_enter(P)
        elseif s == "9"
            single_test(cfg, P, "t9"); wait_enter(P)
        elseif s == "C"
            edit_params(cfg, P)
        elseif s == "L"
            cfg.lang = cfg.lang === :ru ? :en : :ru
            println(P.ok * "  ✓ " * t("lang_set") * A_RESET)
        elseif s == "Q" || s == " Quit" || s == "Й"
            println(P.dim * "  " * t("m_bye") * A_RESET)
            break
        else
            println(P.bad * "  " * t("m_unknown") * A_RESET)
        end
    end
end

# ──────────────────────────────────────────────────────────────────────────────
# RUN ORCHESTRATION — full laboratory run, single tests, selftest, main
# ──────────────────────────────────────────────────────────────────────────────

function cfg_dict(cfg)
    Dict{String,Any}(
        "n" => cfg.n, "oracle_ns" => cfg.oracle_ns,
        "krk" => cfg.krk, "kqk" => cfg.kqk,
        "policies" => string.(cfg.policies),
        "playouts_main" => cfg.playouts_main,
        "playouts_check" => cfg.playouts_check,
        "max_plies" => cfg.max_plies, "mu" => cfg.mu, "lam" => cfg.lam,
        "seed" => cfg.seed, "dpi" => cfg.dpi,
        "fig" => "$(cfg.fig_w)x$(cfg.fig_h)",
        "scaling_ns" => cfg.scaling_ns, "trap_positions" => cfg.trap_positions,
        "expect" => string(cfg.expect), "lang" => string(cfg.lang),
        "outdir" => cfg.outdir, "flow_rooks" => cfg.flow_rooks)
end

function fresh_run_dir(cfg)
    stamp = Dates.format(Dates.now(), "yyyymmdd_HHMMSS")
    d = joinpath(cfg.outdir, "run_$stamp")
    mkpath(joinpath(d, "charts"))
    return d
end

function write_reports(run_dir::String, cfg, L::Logger, tests::Vector{Dict{String,Any}},
                       main_test::Union{Nothing,Dict{String,Any}}, charts::Vector{String})
    paths = String[]
    p = joinpath(run_dir, "log.txt")
    write_txt(p, L.lines, cfg); push!(paths, "log.txt")

    jd = Dict{String,Any}(
        "run" => Dict{String,Any}(
            "program" => "large_board_lab.jl",
            "repository" => "github.com/wild8highlander/chess-dynamics-lab",
            "author" => "Isaev Iskhak Khamzatovich",
            "generated" => Dates.format(Dates.now(), "yyyy-mm-dd HH:MM:SS"),
            "julia" => string(VERSION), "threads" => Threads.nthreads()),
        "parameters" => cfg_dict(cfg),
        "tests" => [Dict{String,Any}(k => v for (k, v) in d if k != "csv_rows")
                    for d in tests])
    if main_test !== nothing
        jd["main_test"] = Dict{String,Any}(k => v for (k, v) in main_test
                                           if !(k in ("csv_rows", "policy_csv")))
        jd["main_test"]["verdict_title"] = get(main_test, "verdict_title", "")
        jd["main_test"]["verdict"] = get(main_test, "verdict", "none")
        rows = get(main_test, "csv_rows", Vector{Vector{String}}())
        isempty(rows) || begin
            cp = joinpath(run_dir, "main_playouts.csv")
            write_csv(cp, ["policy", "scenario", "n", "playout", "stm_start",
                           "plies", "outcome", "reason", "wk", "wq", "bk"], rows)
            push!(paths, "main_playouts.csv")
        end
        prow = get(main_test, "policy_csv", Vector{Vector{String}}())
        isempty(prow) || begin
            cp = joinpath(run_dir, "policy_matrix.csv")
            write_csv(cp, ["policy", "scenario", "n", "games", "draw", "white",
                           "black", "p_draw", "p_white", "p_black", "mean_plies",
                           "tier"], prow)
            push!(paths, "policy_matrix.csv")
        end
    end
    for d in tests
        rows = get(d, "csv_rows", nothing)
        rows === nothing && continue
        if occursin("T4", d["name"])
            cp = joinpath(run_dir, "trap_census.csv")
            write_csv(cp, ["scenario", "kind", "dtm_before", "dtm_after",
                           "class", "from", "to"], rows)
            push!(paths, "trap_census.csv")
        end
    end
    p = joinpath(run_dir, "report.json")
    write_json(p, jd); push!(paths, "report.json")
    p = joinpath(run_dir, "summary.md")
    write_md(p, jd, cfg, run_dir); push!(paths, "summary.md")
    append!(paths, charts)
    return paths
end

function run_lab(cfg, P::Palette)
    L = Logger(P)
    rd = RunData()
    rd.seed = cfg.seed
    run_dir = fresh_run_dir(cfg)
    log(L, "  " * t("rep_dir") * ": " * run_dir)
    log(L)
    t1 = test_t1(cfg, P, L, rd)
    t2 = test_t2(cfg, P, L, rd)
    t3 = test_t3(cfg, P, L, rd)
    t4 = test_t4(cfg, P, L, rd)
    t5 = test_t5(cfg, P, L, rd)
    t7 = test_t7(cfg, P, L, rd)
    t8 = test_t8(cfg, P, L, rd)
    t9 = test_t9(cfg, P, L, rd)
    println()
    log(L, section(P, t("summary")))
    tests = [t1, t2, t3, t4, t5, t7, t8, t9]
    for d in tests
        c = d["status"] == "PASS" ? P.ok : d["status"] == "WARN" ? P.warn : P.bad
        log(L, "   " * rpad(d["name"], 30) * " " * c * d["status"] * A_RESET *
                "  " * P.dim * get(d, "summary", "") * A_RESET)
    end
    main_test = t7
    log(L)
    log(L, section(P, t("rep_files")))
    charts = String[]
    try
        cdir = joinpath(run_dir, "charts")
        render_charts(rd, cfg, cdir, (s -> log(L, s)))
        for (root, dirs, files) in walkdir(cdir)
            for f in files
                push!(charts, "charts/" * f)
            end
        end
    catch e
        log(L, P.bad * "  chart error: $(sprint(showerror, e))" * A_RESET)
    end
    paths = write_reports(run_dir, cfg, L, tests, main_test, charts)
    for p in paths
        log(L, "   · " * joinpath(run_dir, p))
    end
    log(L)
    return run_dir
end

const TEST_DISPATCH = Dict{String,Function}(
    "t1" => test_t1, "t2" => test_t2, "t3" => test_t3, "t4" => test_t4,
    "t5" => test_t5, "t7" => test_t7, "main" => test_t7,
    "t8" => test_t8, "check" => test_t8, "t9" => test_t9, "flow" => test_t9)

function single_test(cfg, P::Palette, name::String)
    f = get(TEST_DISPATCH, name, nothing)
    f === nothing && (println(P.bad * "  unknown test: $name" * A_RESET); return)
    L = Logger(P)
    rd = RunData()
    rd.seed = cfg.seed
    run_dir = fresh_run_dir(cfg)
    log(L, "  " * t("rep_dir") * ": " * run_dir)
    log(L)
    d = f(cfg, P, L, rd)
    c = d["status"] == "PASS" ? P.ok : d["status"] == "WARN" ? P.warn : P.bad
    log(L, "   " * rpad(d["name"], 30) * " " * c * d["status"] * A_RESET)
    log(L)
    charts = String[]
    try
        cdir = joinpath(run_dir, "charts")
        render_charts(rd, cfg, cdir, (s -> log(L, s)))
        for (root, dirs, files) in walkdir(cdir)
            for f2 in files
                push!(charts, "charts/" * f2)
            end
        end
    catch e
        log(L, P.bad * "  chart error: $(sprint(showerror, e))" * A_RESET)
    end
    paths = write_reports(run_dir, cfg, L, [d], name in ("t7", "main") ? d : nothing, charts)
    for p in paths
        log(L, "   · " * joinpath(run_dir, p))
    end
    return run_dir
end

# ── SELFTEST — quick headless battery ─────────────────────────────────────────
function selftest(cfg, P::Palette)
    println(P.title * "  " * t("selftest") * " · large_board_lab.jl" * A_RESET)
    println(hr(P))
    ok = true
    results = Tuple{String,Bool}[]

    # 1. PNG encoder round-trip (structure + CRC + IEND)
    C = PCanvas(96, 96)
    for y in 1:96, x in 1:96
        pset!(C, x - 1, y - 1, viridis(y / 96))
    end
    ptext!(C, "PNG selftest 123", 2, 40, 1, hexc("#FFFFFF"); bold = true)
    tmp = joinpath(tempdir(), "lbl_selftest.png")
    write_png(tmp, 96, 96, C.px)
    b = read(tmp)
    sig_ok = length(b) > 60 && b[1:8] == UInt8[0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]
    # IEND chunk: len=00000000 + type=IEND + crc=AE426082 (last 12 bytes)
    iend_ok = length(b) >= 12 && b[end-11:end] == UInt8[0x00, 0x00, 0x00, 0x00,
        0x49, 0x45, 0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82]
    st1 = sig_ok && iend_ok
    push!(results, (t("st_png"), st1)); ok &= st1

    # 2. engine invariants: make/unmake restores key; zobrist increment == recompute
    Pq = Pos(8)
    g = SM64(UInt64(cfg.seed + 1))
    setup_kxk!(Pq, g, PIECE_R, true)
    k0 = Pq.key
    legal = legal_moves(Pq)
    st2 = !isempty(legal)
    if st2
        m = legal[1]
        u = make!(Pq, m)
        k1 = Pq.key
        unmake!(Pq, m, u)
        st2 = (Pq.key == k0) && (k1 != k0) && (Pq.key == recompute_key(Pq))
    end
    push!(results, (t("st_engine"), st2)); ok &= st2

    # 3. solver legality on short playouts
    S = Solver(cfg.mu, cfg.lam)
    st3 = true
    for rep in 1:3
        Pq2 = Pos(8)
        g3 = SM64(UInt64(cfg.seed + 99 + rep))
        setup_kxk!(Pq2, g3, PIECE_R, isodd(rep))
        for ply in 1:24
            legal2 = legal_moves(Pq2)
            isempty(legal2) && break
            m = choose_move(Pq2, S)
            (m < 0 || !(m in legal2)) && (st3 = false; break)
            make!(Pq2, m)
        end
    end
    push!(results, (t("st_solver"), st3)); ok &= st3

    # 4. tiny oracle sanity
    o = retro_oracle(5, PIECE_R)
    st4 = o.stats["mates"] > 0 && o.stats["won"] > 0 && o.stats["max_plies"] > 0
    push!(results, ("oracle K+R vs K (n=5)", st4)); ok &= st4

    for (name, res) in results
        println("  " * rpad(name, 40) * " " *
                (res ? P.ok * mark(true) * A_RESET : P.bad * mark(false) * A_RESET))
    end
    println(hr(P))
    println(P.ok * "  " * t("st_all") * A_RESET)
    rm(tmp; force = true)
    return ok
end

# ── MAIN ──────────────────────────────────────────────────────────────────────
const CFG = Config()
parse_cli!(CFG)
CFG.n = clamp(CFG.n, 4, 127)
filter!(x -> 3 <= x <= 13, CFG.oracle_ns)
isempty(CFG.oracle_ns) && (CFG.oracle_ns = [4, 6])
const PALETTE = Palette(CFG.color && IS_TTY)

if "--selftest" in ARGS
    exit(selftest(CFG, PALETTE) ? 0 : 1)
end

if !isempty(CFG.headless_test)
    if lowercase(CFG.headless_test) in ("lab", "all")
        run_lab(CFG, PALETTE)
    else
        single_test(CFG, PALETTE, CFG.headless_test)
    end
elseif IS_TTY && !isempty(ARGS) && CFG.force_menu
    menu_loop(CFG, PALETTE)
elseif IS_TTY && isempty(ARGS)
    menu_loop(CFG, PALETTE)
elseif CFG.force_menu
    menu_loop(CFG, PALETTE)
else
    # piped/no-args invocation: straight into the full laboratory run
    run_lab(CFG, PALETTE)
end

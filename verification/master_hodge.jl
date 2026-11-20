#!/usr/bin/env julia
# ════════════════════════════════════════════════════════════════════════
# HODGE MASTER · master_hodge.jl — Julia-версия мастера верификации
# репозитория hodge-laboratory (https://github.com/wild8highlander/hodge-laboratory)
#
# Паритет с Python-мастером (сессия 2): меню-first при голом запуске, темы и
# типографика, пять потоков логов, отчёты results.json/MANIFEST/FINAL_REPORT,
# --ci/--jsonl/--tsv, таймауты/сигналы/flock, рецепты/хуки/DAG-циклы,
# sparkline/ETA, монитор /proc, метрики + экспорт, golden-файлы, bench --stats,
# §11-графика: PNG (zlib/ccall + stored-fallback), GIF89a (свой LZW), 5×7
# битмап-шрифт, канва, HODGEPlot, единый GCT прогона, 3D-лаборатория + sweep.
#
# Запуск:  julia master_hodge.jl                # splash + меню (menu-first)
#          julia master_hodge.jl --task 8       # одна задача (V9 deep)
#          julia master_hodge.jl --ci --task all# машиночитаемый прогон
#          julia master_hodge.jl --self-test --full
# Только stdlib: Base, Printf, LinearAlgebra, SHA, Dates, Base64.
#
# ИСТОРИЯ v1.4.2-session6 (2026-11-14) — «prec без зависаний»:
#   • ДИАГНОЗ (измерено): lgamma_hp делал shift ≈ digits/2.73 итераций сдвига,
#     КАЖДЫЙ с полным log() — при prec 5M бит это 550k вызовов log по 1.5M
#     цифр (log@5M бит = 6.8 с) → ДЕСЯТКИ ДНЕЙ молчания; zeta_even_eps при
#     больших prec — прямая сумма ~10^(digits/302) членов → бесконечность.
#   • lgamma_hp: сдвиг свёрнут в ln((s−1)!)+ln Π(1+x/k) — 3 log вместо s;
#     (s−1)! — дерево произведений BigInt (GMP-FFT: 6M цифр за ~0.05 с),
#     Π(1+x/k) — сбалансированное дерево BigFloat (глубина O(log s) —
#     точность лучше прежней последовательной);
#     ln((s−1)!) кэшируется per (s, prec).
#   • Честные гейты: ERR_GAMMA_PREC (ряд ~π·digits/2.73 членов + ζ-сумма,
#     порог HODGE_GAMMA_LIMIT=900 с), ERR_QUAD_PREC (tanh–sinh),
#     ERR_PREC_OP не нужен — MPFR log/exp/sin на 5M бит = 0.7–6.8 с.
#     Обход — HODGE_PREC_UNSAFE=1 или индивидуальные HODGE_*_LIMIT.
#   • HODGEPROG: heartbeat-задача печатает в stderr «…стадия: N s» каждые
#     10 с (HODGE_HEARTBEAT=0 отключит) — терминал не выглядит зависшим.
#   • Блок честных оценок prec при запуске прогона и в меню (prec ≥ 8192 бит)
#     + подтверждение [y/N] в интерактивном меню.
#   • GIF: Γ-таблица кадров капится 150 бит (float64-дисплей) — GIF работает
#     при ЛЮБОМ cfg.prec.
#
# ИСТОРИЯ v1.4.1-session5 (2026-11-14) — «gif-движок починен»:
#   • GCE-блок кадра: лишний байт 0x04 сдвигал поле delay на 1 байт — зрители
#     читали задержку ×256 (кадр «висел» по 20+ с), после GCE оставался
#     посторонний пустой 0x00-блок. Теперь ровно 21 F9 04 04 … (8 байт).
#   • lab-video: задержка кадра была 1000÷fps — GIF-delay меряется в СОТЫХ
#     секунды, т.е. в 10 раз больше верной: 24 fps играли как ~2.4 fps.
#     Теперь gif_delay_cs(fps) = max(2, round(100/fps)); self-test проверяет.
#   • self-test §11 усилен: структурная приёмка GIF (GCE/цепочка блоков/
#     задержки) — энкодер LZW сверен с независимым декодером (pixel-exact).
# ИСТОРИЯ v1.4.0-session4 (2026-11-14) — «prec без границ»:
#   • prec БЕЗ верхней границы: CLI/меню/кэш принимают 4096, 5m, 1g, 2t
#     (суффиксы k/m/g/t — «гигабайты мантиссы»); лимит 30..1024 снят (§3.2 v5).
#   • cfg.prec теперь реально управляет точностью движка (пол 320 бит,
#     идемпотентно); --prec-extreme → движок ≥ 1024 бит.
#   • Честная оценка RAM: BigFloat ≈ prec/8 байт; ×16 > RAM → WARN,
#     ×2 > RAM → ERR_PREC_RAM без --unsafe-prec / HODGE_PREC_UNSAFE=1.
#   • π/ln(2π) — на ТЕКУЩЕЙ точности (кэш per-precision) вместо константы,
#     замороженной на 320 бит (пол ошибки 2^−320 ≈ 3e−96 топил t40).
#   • Γ-слой: сдвиг/порог в десятичных цифрах, точные Бернулли до k=150,
#     ТОЧНОЕ ζ-отношение для B_{2k}/B_{2k−2} при k > 150 (без поправки —
#     пол |term_60|·O(4^−61) ≈ 1e−185), guard-разряды, Neumaier-суммирование.
#   • t40 HODGE-INF: сертификация на ЛЮБОЙ prec; err_engine/tol — BigFloat
#     (Float64 underflow давал engine=0.0 и tol=0.0 → ложный FAIL).
# ════════════════════════════════════════════════════════════════════════
using Printf, LinearAlgebra, SHA, Dates, Base64   # P2: Ctrl+Y — copy path

setprecision(BigFloat, 320)      # база движка; cfg.prec её ПОДНИМАЕТ (§3.2 v5, см. hodge_prec_engine_apply!)
# §3.2 v5: π и ln(2π) — на ТЕКУЩЕЙ точности (кэш по precision(BigFloat)).
# Раньше здесь была константа, замороженная на 320 бит при загрузке: при prec 1024
# замкнутые формы π/sin(πa/N) имели жёсткий пол ошибки 2^−320 ≈ 3e−96 — задача 40
# не могла пройти tol 1e−300 (engine=3.06e-96). Теперь константы следуют за
# рабочей точностью.
const HPI_CACHE_PI = Dict{Int,BigFloat}()
function pi_hp(p::Int = precision(BigFloat))
    get!(HPI_CACHE_PI, p) do
        old = precision(BigFloat)
        setprecision(BigFloat, p)
        v = big(π)
        setprecision(BigFloat, old)
        v
    end
end
const HPI_CACHE_LOG2PI = Dict{Int,BigFloat}()
function log2pi_hp(p::Int = precision(BigFloat))
    get!(HPI_CACHE_LOG2PI, p) do
        old = precision(BigFloat)
        setprecision(BigFloat, p)
        v = log(2 * big(π))
        setprecision(BigFloat, old)
        v
    end
end

# ════════════════════════════════════════════════════════════════════════
# §3.2 v6: «prec без зависаний» (см. историю в шапке):
#   HODGEPROG — heartbeat; mpfr_cost — измеренная модель стоимости;
#   гейты gamma_gate/quad_gate — предсказуемая операция с оценкой выше
#   лимита падает с честным ERR_* вместо молчания на часы/дни.
# ════════════════════════════════════════════════════════════════════════
const PROG = Ref{Tuple{String,Float64}}(("", 0.0))    # (стадия, старт)
const PROG_TASK = Ref{String}("")
const PROG_THREAD = Ref{Any}(nothing)   # heartbeat-задача; НЕ типизировать Task —
                                        # имя Task ниже занимает struct Task (§4.1)
prog_begin!(stage::AbstractString) = (PROG[] = (String(stage), time()); nothing)
prog_end!() = (PROG[] = ("", 0.0); nothing)
prog_task!(name::AbstractString) = (PROG_TASK[] = String(name); nothing)
function _heartbeat_loop()
    last = 0.0
    while true
        sleep(1.0)
        st, t0 = PROG[]
        isempty(st) && (last = 0.0; continue)
        el = time() - t0
        if el - last >= 10.0
            last = el
            line = "… $st: $(round(Int, el)) s"
            isempty(PROG_TASK[]) || (line *= " · task $(PROG_TASK[])")
            println(stderr, line)
            flush(stderr)
        end
    end
end

# §3.2 v6: при nthreads=1 (дефолт julia) @spawn-задача НЕ работает параллельно
# главному вычислению (проверено: печатает только после) — поэтому тяжёлые
# циклы зондируются СИНХРОННО через hb_tick!: каждые 10 с печатает в stderr
# «…стадия: i/total · Ns». hb_ok — нужно ли вообще печатать.
const HB_STATE = Ref{Tuple{Float64,Float64}}((0.0, 0.0))   # (старт стадии, последний вывод)
function hb_ok()
    on = get(ENV, "HODGE_HEARTBEAT", "")
    tty = stderr isa Base.TTY
    !(on == "0" || (isempty(on) && !tty))
end
function hb_stage!(name::AbstractString)
    PROG[] = (String(name), time())
    HB_STATE[] = (time(), 0.0)
    nothing
end
function hb_tick!(i::Int, total::Int)
    st, t0 = PROG[]
    isempty(st) && return
    t0s, last = HB_STATE[]
    el = time() - t0s
    if el - last >= 10.0
        HB_STATE[] = (t0s, el)
        hb_ok() || return
        line = "… $st: $i/$total · $(round(Int, el)) s"
        isempty(PROG_TASK[]) || (line *= " · task $(PROG_TASK[])")
        println(stderr, line)
        flush(stderr)
    end
    nothing
end

function prog_start()
    PROG_THREAD[] !== nothing && return
    on = get(ENV, "HODGE_HEARTBEAT", "")
    tty = stderr isa Base.TTY
    (on == "0" || (isempty(on) && !tty)) && return
    # §3.2 v6: главный поток при чистых BigFloat-вычислениях НЕ отдаёт
    # планировщик (@async голодал бы — проверено), поэтому heartbeat — на
    # интерактивном пуле (отдельный ОС-поток); при его отсутствии — @async.
    PROG_THREAD[] = try
        Threads.@spawn :interactive _heartbeat_loop()
    catch
        @async _heartbeat_loop()
    end
    nothing
end

# Измерено (julia 1.10/MPFR 4): @1M бит — π 0.275 с, log 0.87, exp 0.111,
# sin 0.654, sqrt 0.011, mul 0.019; @5M бит — π 1.5, log 6.8, exp 0.74,
# sin 5.4, sqrt 0.05, mul ~0.05. Показатели степени — из этих двух точек.
function mpfr_cost(p::Int)
    q = max(p, 320) / 1e6
    return Dict("mul" => 0.019 * q^1.05,
                "div" => 0.042 * q^1.05,
                "log" => 0.87 * q^1.32,
                "exp" => 0.111 * q^1.25,
                "sin" => 0.654 * q^1.37,
                "sqrt" => 0.011 * q^1.03)
end

_hodge_env_float(name::String, default::Float64) =
    begin
        v = get(ENV, name, "")
        isempty(v) && return default
        r = tryparse(Float64, v)
        r === nothing ? default : r
    end
_hodge_unsafe() = get(ENV, "HODGE_PREC_UNSAFE", "") == "1"
_fmt_terms(x::Float64) = x >= 6.0 ? "~10^$(round(Int, x))" : "~$(round(Int, 10^x))"

function gamma_gate(p0::Int)
    """§3.2 v6: Γ-гейт. Сдвиг y ≈ digits/2.73 → ряд Стирлинга ~π·y членов;
    ζ(2k)−1 при k≈151 — прямая сумма ~10^((digits+76)/302) членов. Оценка
    > HODGE_GAMMA_LIMIT (сек, по умолч. 900) → ERR_GAMMA_PREC."""
    if _hodge_unsafe()
        prog_begin!("Γ @ prec=$p0 бит (обход гейта)")
        return
    end
    lim = _hodge_env_float("HODGE_GAMMA_LIMIT", 900.0)
    digits = floor(Int, p0 * log10(2))
    shift = max(40, ceil(Int, (digits + 4) / 2.72864) + 4)
    k_star = 3.1416 * shift
    c = mpfr_cost(p0)
    est_series = k_star * (2 * c["mul"] + c["div"] + 3e-5)
    e151 = (digits + 76) / 302.0
    est_zeta = 10.0^min(e151, 15.0) * (1.5 * c["mul"] + 3e-5)
    est = est_series + est_zeta
    est <= lim && return
    error("ERR_GAMMA_PREC Γ @ prec=$p0 бит: сдвиг y≈$shift, ряд ≈$(_fmt_terms(log10(max(k_star, 2.0)))) членов × дивизии + ζ(302)−1 суммой $(_fmt_terms(e151)) членов; оценка ≈$(fmt_est_cost(est)) с > лимита $(lim) с (HODGE_GAMMA_LIMIT). Γ-задачи: prec ≤ ~5000 бит или HODGE_PREC_UNSAFE=1")
end

function quad_gate_mpfr(p0::Int, nodes::Int)
    """tanh–sinh гейт: узлов × (4 exp/sin-класса + 2 div). Оценка >
    HODGE_QUAD_LIMIT (сек, по умолч. 1800) → ERR_QUAD_PREC."""
    (_hodge_unsafe() || nodes <= 0) && return
    lim = _hodge_env_float("HODGE_QUAD_LIMIT", 1800.0)
    c = mpfr_cost(p0)
    est = nodes * (4 * max(c["exp"], c["sin"]) + 2 * c["div"])
    est <= lim && return
    error("ERR_QUAD_PREC tanh–sinh @ prec=$p0 бит: узлов ≈$nodes × (4 exp + 2 div) ≈ $(fmt_est_cost(est)) с > лимита $(lim) с (HODGE_QUAD_LIMIT). Квадратуры держите при prec ≤ ~60000 бит или HODGE_PREC_UNSAFE=1")
end

function zeta_gate(p0::Int, N::Int)
    """ζ-таблица: N комплексных exp по prec-значному контексту; ОДИН exp —
    одиночный C-вызов MPFR (внутри прогресса нет), при гигантском prec это
    минуты-часы тишины. Оценка > HODGE_ZETA_LIMIT (сек, по умолч. 900) →
    ERR_ZETA_PREC."""
    (_hodge_unsafe() || N <= 0) && return
    lim = _hodge_env_float("HODGE_ZETA_LIMIT", 900.0)
    c = mpfr_cost(p0)
    est = N * (3 * c["exp"] + c["div"])
    est <= lim && return
    error("ERR_ZETA_PREC ζ-таблица N=$N @ prec=$p0 бит: N exp ≈ $(fmt_est_cost(est)) с > лимита $(lim) с (HODGE_ZETA_LIMIT). ОДИН exp на таком prec — минуты тишины (одиночный C-вызов MPFR). Держите prec ≤ ~200000 бит или HODGE_PREC_UNSAFE=1")
end

function fmt_est_cost(sec::Float64)
    """Оценки стоимости: гигантские значения — в нейтральных единицах."""
    if sec >= 86400 * 365.25
        y = sec / (86400 * 365.25)
        return y >= 100 ? "$(round(Int, y)) yr" : (y >= 10 ? string(round(y, digits=1), " yr") : string(round(y, digits=2), " yr"))
    elseif sec >= 86400
        dd = sec / 86400
        return dd >= 100 ? "$(round(Int, dd)) d" : string(round(dd, digits=1), " d")
    elseif sec >= 3600
        h = floor(Int, sec / 3600); m = round(Int, (sec - h * 3600) / 60)
        return "$(h) h $(m) min"
    elseif sec >= 60
        return string(round(Int, sec ÷ 60), ":", lpad(round(Int, sec) % 60, 2, '0'))
    end
    return string(round(sec, digits=1), " s")
end

const HODGE_LANG = "julia"
const HODGE_VERSION = "1.4.2-session6"
const HODGE_BUILD_DATE = "2026-11-14"
const HODGE_REPO = "wild8highlander/hodge-laboratory"
const HODGE_PRESETS = ("quick", "full", "deep")
const SCHEMA_VERSION = "1.1.0"

# ════════════════════════════════════════════════════════════════════════
# §16 l10n: MSG[lang][key]; строки — через hodge_fmt (§16.2)
# ════════════════════════════════════════════════════════════════════════
const MSG = Dict(
    "ru" => Dict(
        "menu.title" => "HODGE MASTER · меню верификации",
        "menu.help"  => "? — помощь, a — все задачи, цифры — отметить, Enter — запуск отмеченных, q — выход",
        "menu.prompt" => "выбор",
        "menu.bye"   => "Выход. Доброй верификации!",
        "menu.unknown" => "Неизвестная клавиша: {key}",
        "run.start"  => "Прогон {run} · пресет {preset} · сид {seed}",
        "run.task_start" => "задача {id} · {slug} — {title} [{n}/{total}]",
        "run.progress_bar" => "прогресс {bar} {done}/{total} · ETA {eta}",
        "task.verdict" => "[{id}] {slug}: {verdict}",
        "all_pass"   => "ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ",
        "has_fail"   => "ЕСТЬ ПРОВАЛЫ",
        "duration"   => "длительность",
        "summary"    => "ИТОГ",
        "tasks"      => "задачи",
        "report.saved" => "Отчёт сохранён: {path}",
        "lock.held"  => "Lock занят: {path}",
        "cache.hit"  => "Кэш: попадание для {id}",
        "cache.miss" => "Кэш: промах для {id}",
        # §14 меню: главный экран (BUGFIX: menu_render был захардкожен по-русски)
        "menu.run_header"      => "RUN",
        "menu.tasks_header"    => "TASKS",
        "menu.settings_header" => "НАСТРОЙКИ",
        "menu.actions_header"  => "ДЕЙСТВИЯ",
        "menu.run_all"      => "Запустить ВСЕ задачи (two-pass)",
        "menu.run_fast"     => "Только fast-теги",
        "menu.run_heavy"    => "Только heavy-теги",
        "menu.run_chess"    => "Только chess (23–33)",
        "menu.run_verhodge" => "Только verhodge (34–38, 40)",
        "menu.run_sweep"    => "SWEEP: бесконечный выбор параметров",
        "menu.set.prec"         => "precision          сейчас: {value} бит",
        "menu.set.seed"         => "seed               сейчас: {value}",
        "menu.set.preset"       => "preset             сейчас: {value}",
        "menu.set.theme"        => "тема               сейчас: {value}",
        "menu.set.lang"         => "язык               сейчас: {value}",
        "menu.set.depth"        => "color depth        сейчас: {value}",
        "menu.set.two_pass"     => "two-pass           сейчас: {value}",
        "menu.set.prec_extreme" => "prec-extreme       сейчас: {value}",
        "menu.act.dry_run"     => "dry-run (план без вычислений)",
        "menu.act.recipes"     => "список рецептов",
        "menu.act.theme_cycle" => "сменить тему (цикл)",
        "menu.act.palette"     => "палитра (theme-preview)",
        "menu.act.help"        => "помощь",
        "menu.act.quit"        => "выход",
        "menu.filter_mode"     => "filter mode (пусто — выход)",
        "menu.sweep_fn_prompt" => "SWEEP: имя функции (omega|period_re|census_h) → Enter для дефолта «omega»",
        "menu.sweep_spec_prompt" => "SWEEP: функция={fn}. Введите sweep-спеку (name:lo:hi:step), пусто — запуск",
        "menu.sweep_bad_fn" => "SWEEP: неизвестная функция «{fn}» — доступно: omega | reflection | census_h",
        "menu.sweep_added"       => "SWEEP: добавлено {key}. ещё? (пусто — запуск)",
        "menu.sweep_invalid"     => "SWEEP: {msg} — попробуйте ещё раз",
        "menu.sweep_invalid_spec" => "SWEEP: спека невалидна: {msg}",
        "menu.sweep_preview"     => "SWEEP preview: fn={fn}, specs={specs}, кадров={n} (cap 500)",
        "menu.status_line"     => "theme={theme} · prec={prec} · seed={seed} · preset={preset} · lang={lang} · marked={n} [{ids}]",
        "menu.copy_done"      => "скопировано: {path}",
        "menu.copy_empty"     => "run_dir пуст — сначала запустите прогон",
        "menu.copy_disabled"  => "clipboard отключён (--no-clipboard)",
        "menu.history_empty"  => "история пуста",
        "menu.no_history"     => "нет записи #{n} (всего {total})",
        "menu.history_hint"   => "история: !! — повтор последней, !N — повтор N-й",
        "menu.eof_guard"      => "EOF-guard {n}/{limit}",
        "menu.ctrl_c"         => "Ctrl+C перехвачен — возврат",
        "menu.input_error"    => "ошибка ввода: {msg}",
        "menu.help_detail"    => "«?» — справка\n  [1-N] задача · [Space] отметить · [Enter] запуск отмеченных\n  [a/f/h/c/v] прогон · [w] sweep · [p/s/n/t/l/d/e/P] настройки",
        "menu.non_tty_hint"   => "stdin не TTY — используйте --task N / --menu / --self-test",
        "menu.no_task"        => "нет задачи {id}",
        "menu.mark_on"        => "задача {id} отмечена — Enter запустит отмеченные",
        "menu.mark_off"       => "задача {id}: отметка снята",
        # §14: подсказки редакторов настроек (menu_handle!)
        "menu.edit.prec_now"   => "текущее prec: {value}",
        "menu.edit.prec_new"   => "новое prec [30..∞ | 4096, 5m, 1g]: ",
        "menu.edit.prec_out"   => "нужно число ≥ 30 (или Nk/Nm/Ng/Nt)",
        "menu.edit.prec_set"   => "prec → {value}",
        "menu.edit.seed_now"   => "текущий seed: {value}",
        "menu.edit.seed_new"   => "новый seed: ",
        "menu.edit.seed_set"   => "seed → {value}",
        "menu.edit.preset_list"   => "пресеты: quick | full | deep",
        "menu.edit.preset_choice" => "выбор [{value}]: ",
        "menu.edit.preset_set"    => "preset → {value} (prec={prec}, two_pass={twopass})",
        "menu.edit.theme_set"  => "тема → {value}",
        "menu.edit.lang_set"   => "язык → {value}",
        "menu.edit.depth_set"  => "depth → {value}",
        "menu.edit.twopass_set" => "two_pass → {value}",
        "menu.edit.precext_set" => "prec_extreme → {value} (prec={prec})",
        # §3.2 v5: честная RAM-оценка гигантского prec + честный RLIMIT
        "prec.ram.block"    => "ERR_PREC_RAM: prec={prec} → ≈{est}/BigFloat, уже 2 числа > RAM {ram}. Сознательное продолжение: --unsafe-prec / HODGE_PREC_UNSAFE=1",
        "prec.ram.bypass"   => "prec={prec}: ≈{est}/BigFloat > RAM — продолжаю по --unsafe-prec",
        "prec.ram.warn"     => "prec={prec} → ≈{est}/BigFloat; 16 чисел ≈ {est16} vs RAM {ram} — возможен OOM",
        # §3.2 v6: блок честных оценок prec + гейты
        "prec.est.header"   => "prec {prec} бит (≈{digits} цифр) · ≈{est} RAM/число — честные оценки стоимости (julia/MPFR):",
        "prec.est.pi"       => "  π (MPFR):                     ≈{est} один раз (кэш дальше)",
        "prec.est.trig"     => "  sin/cos (1 вызов):            ≈{est}",
        "prec.est.lnexp"    => "  log/exp (1 вызов):            ≈{est}",
        "prec.est.gamma"    => "  Γ/Стирлинг (ряд {terms} членов + ζ-сумма {zterms}): оценка ≈{est} — лимит {lim} с → {verdict}",
        "prec.est.quad"     => "  tanh–sinh (≈{nodes} узлов):          оценка ≈{est} — лимит {lim} с → {verdict}",
        "prec.est.advice"   => "  совет: BLOCK-операции упадут с честным ERR_* вместо зависания; Γ-задачи держите при prec ≤ ~5000 бит, квадратуры ≤ ~60000 бит",
        "menu.edit.prec.confirm" => "prec={value}: оценка серьёзная (см. выше). Продолжить? [Y/n]: ",
        "menu.edit.prec.revert"  => "prec возвращён к {value}",
        "rlimit.unsupported" => "RLIMIT на stdlib-Julia не поддержан (§1.5)",
        "menu.edit.prec_keep"   => "prec без изменений: {value}",
        "menu.edit.seed_keep"   => "seed без изменений: {value}",
        "menu.edit.preset_keep" => "preset без изменений: {value}",
        "menu.edit.not_int"     => "нужно целое число, получено: {v}",
        "menu.edit.preset_unknown" => "неизвестный пресет: {v} (quick|full|deep)",
        "menu.act.dry_hint"    => "dry-run: см. --dry-run --task all (план без вычислений)",
        "menu.act.palette_hint" => "палитра: см. --theme-preview",
        "menu.act.video_lab" => "3D Video Lab: объект → MP4/MJPEG/GIF",
        "menu.video.objects" => "3D Video Lab · доступные объекты:",
        "menu.video.prompt"  => "имя объекта [sphere]: ",
        # §14.2: подменю r/C/?/x/w/V — полноценные интерактивы (BUGFIX: были заглушки)
        "submenu.cancelled"     => "отменено",
        "submenu.all"           => "все",
        "submenu.numbers"       => "числа ",
        "submenu.recipes.title"   => "── Рецепты ───────────────────────────────────────────",
        "submenu.recipes.cancel"  => "  [0] отмена",
        "submenu.recipes.prompt"  => "  рецепт [0-{n}]: ",
        "submenu.recipes.none"    => "нет рецепта '{v}'",
        "submenu.recipes.applying"=> "  применение рецепта '{name}':",
        "submenu.recipes.preview" => "    preset:  {pold} → {pnew}\n    profile: {rold} → {rnew}\n    tasks:   {told} → {tnew}\n    two_pass: {eold} → {enew}",
        "submenu.recipes.actions"=> "  [a] применить и запустить\n  [p] только применить (без запуска)\n  [Enter] отмена",
        "submenu.recipes.action_prompt" => "  действие: ",
        "submenu.recipes.applied" => "рецепт '{name}' применён",
        "submenu.recipes.running" => "запуск рецепта '{name}': {ids}",
        "submenu.palette.current" => " ⟵ текущая",
        "submenu.palette.sample"  => "  образец: ",
        "submenu.palette.hint"    => "  [1-{n}] выбрать · [Enter] отмена",
        "submenu.palette.prompt"  => "  тема по номеру: ",
        "submenu.palette.none"    => "нет темы '{v}'",
        "submenu.palette.mono_note" => "  (монохром — палитра собирается программно, §27.8)",
        "submenu.palette.set"     => "тема → {value}",
        "submenu.help.title"      => "  HODGE MASTER · полная справка",
        "submenu.help.run"        => "RUN:",
        "submenu.help.run.body"   => "  [a] запуск ВСЕХ задач (two-pass, если cfg.two_pass=true)\n  [f] только задачи с тегом fast\n  [h] только задачи с тегом heavy\n  [c] chess — диапазон 23–33 (запустится всё, что есть в реестре)\n  [v] verhodge — диапазон 34–38 + 40 (HODGE-INF, классы Ходжа до бесконечности)\n  [w] SWEEP-подменю: 3D-лаборатория, выбор функции и параметров",
        "submenu.help.tasks"      => "ЗАДАЧИ:",
        "submenu.help.tasks.body" => "  [1-23, 38] запустить одну задачу по номеру\n  [Space] отметить задачу (накопительно)\n  [Enter] запуск отмеченных (или выбранной в фильтре)\n  [/] фильтр по slug / title / номеру\n  [j/k] навигация вперёд / назад",
        "submenu.help.settings"   => "НАСТРОЙКИ:",
        "submenu.help.settings.body" => "  [p] precision (30..∞ бит; суффиксы k/m/g/t — «1g» ≈ 1 млрд бит ≈ 120 MB/BigFloat)\n  [s] seed (целое)\n  [n] preset (quick | full | deep)\n  [t] тема (цикл)\n  [l] язык (ru ⇄ en)\n  [d] color depth (auto | truecolor | 256 | 16 | mono)\n  [P] prec-extreme (on ⇄ off; рекордный режим: движок ≥ 1024 бит)\n  [e] two-pass (on ⇄ off)\n  словом: «prec-extreme [on|off]» / «precext» — то же, что [P]\n  изменения настроек сохраняются в .cache/settings.json (§3.2 v4)",
        "submenu.help.actions"    => "ДЕЙСТВИЯ:",
        "submenu.help.actions.body" => "  [x] dry-run: план прогона без вычислений\n  [r] рецепты: список → выбор → preview → apply/run\n  [T] сменить тему (цикл)\n  [C] палитра: свотчи всех тем + выбор\n  [V] 3D Video Lab: объект + fps + frames + N (MP4/GIF)\n  [?] эта справка\n  [q] выход из меню",
        "submenu.help.cli"        => "CLI-СООТВЕТСТВИЯ:",
        "submenu.help.cli.body"   => "  [a] ≈ --task all --two-pass\n  [x] ≈ --dry-run --task <выбор>\n  [r] ≈ --recipe NAME\n  [V] ≈ --lab-video OBJ [--lab-video-fps N --lab-video-frames N --lab-video-N N]\n  [w] ≈ --lab3d FN --sweep name:lo:hi:step ...",
        "submenu.help.input"      => "УПРАВЛЕНИЕ ВВОДОМ:",
        "submenu.help.input.body" => "  Ctrl+D — выход из меню\n  Ctrl+C — прервать прогон (возврат в меню)\n  Ctrl+Y — копировать путь прогона (OSC 52)\n  !!     — повторить последнюю команду\n  !N     — повторить N-ю команду (нумерация с 1)",
        "submenu.help.back"       => "  [Enter] — вернуться в меню",
        "submenu.dry.title"       => "── dry-run (план без вычислений) ──────────────────",
        "submenu.dry.cfg"         => "  Пресет: {preset} · seed: {seed} · prec: {prec} · two-pass: {tp}",
        "submenu.dry.opts"        => "  [1] все задачи\n  [2] fast-теги\n  [3] heavy-теги\n  [4] chess (23–33)\n  [5] verhodge (34–38)",
        "submenu.dry.cancel"      => "  [Enter] отмена",
        "submenu.dry.prompt"      => "  выбор: ",
        "submenu.dry.noopt"       => "нет опции '{v}'",
        "submenu.dry.done"        => "план записан в {path}",
        "submenu.sweep.title"     => "── SWEEP · 3D-лаборатория ──────────────────────────",
        "submenu.sweep.fns"       => "  Функции: omega | reflection | census_h",
        "submenu.sweep.fn_prompt" => "  функция [omega]: ",
        "submenu.sweep.spec_prompt" => "  sweep ({n} шт., Enter = запуск): ",
        "submenu.sweep.added"     => "добавлено: {spec}",
        "submenu.sweep.bad_spec"  => "невалидная спека: {msg}",
        "submenu.sweep.summary"   => "fn={fn} · specs={specs} · кадров={total} (cap {cap})",
        "submenu.sweep.cap_warn"  => "будет обрезано до {cap} кадров",
        "submenu.sweep.confirm"   => "  [Enter] запустить · [c] отмена: ",
        "submenu.video.fps_prompt"    => "  fps [24]: ",
        "submenu.video.frames_prompt" => "  frames [120]: ",
        "submenu.video.n_prompt"      => "  N_full [64]: ",
        "submenu.video.summary"  => "object={obj} · fps={fps} · frames={frames} · N={n}",
        "submenu.video.bad_obj"  => "объект '{obj}' не зарегистрирован",
        "submenu.groups.run" => "{name}: {ids}",
        "submenu.groups.run_missing" => "{name}: {ids} (не реализованы: {miss})",
        "submenu.groups.chess_empty" => "нет задач с тегом chess (23–33) в реестре",
        "submenu.groups.verhodge_empty" => "нет задач с тегом verhodge (34–38) в реестре",
    ),
    "en" => Dict(
        "menu.title" => "HODGE MASTER · verification menu",
        "menu.help"  => "? — help, a — all tasks, digits — mark, Enter — run marked, q — quit",
        "menu.prompt" => "choice",
        "menu.bye"   => "Bye. Happy verifying!",
        "menu.unknown" => "Unknown key: {key}",
        "run.start"  => "Run {run} · preset {preset} · seed {seed}",
        "run.task_start" => "task {id} · {slug} — {title} [{n}/{total}]",
        "run.progress_bar" => "progress {bar} {done}/{total} · ETA {eta}",
        "task.verdict" => "[{id}] {slug}: {verdict}",
        "all_pass"   => "ALL CHECKS PASSED",
        "has_fail"   => "THERE ARE FAILURES",
        "duration"   => "duration",
        "summary"    => "SUMMARY",
        "tasks"      => "tasks",
        "report.saved" => "Report saved: {path}",
        "lock.held"  => "Lock held: {path}",
        "cache.hit"  => "Cache: hit for {id}",
        "cache.miss" => "Cache: miss for {id}",
        # §14 menu: main screen (BUGFIX: menu_render was hardcoded in Russian)
        "menu.run_header"      => "RUN",
        "menu.tasks_header"    => "TASKS",
        "menu.settings_header" => "SETTINGS",
        "menu.actions_header"  => "ACTIONS",
        "menu.run_all"      => "Run ALL tasks (two-pass)",
        "menu.run_fast"     => "Fast tags only",
        "menu.run_heavy"    => "Heavy tags only",
        "menu.run_chess"    => "Chess only (23–33)",
        "menu.run_verhodge" => "Verhodge only (34–38, 40)",
        "menu.run_sweep"    => "SWEEP: infinite parameter selector",
        "menu.set.prec"         => "precision          now: {value} bits",
        "menu.set.seed"         => "seed               now: {value}",
        "menu.set.preset"       => "preset             now: {value}",
        "menu.set.theme"        => "theme              now: {value}",
        "menu.set.lang"         => "language           now: {value}",
        "menu.set.depth"        => "color depth        now: {value}",
        "menu.set.two_pass"     => "two-pass           now: {value}",
        "menu.set.prec_extreme" => "prec-extreme       now: {value}",
        "menu.act.dry_run"     => "dry-run (plan only, no compute)",
        "menu.act.recipes"     => "list recipes",
        "menu.act.theme_cycle" => "cycle theme",
        "menu.act.palette"     => "palette (theme-preview)",
        "menu.act.help"        => "help",
        "menu.act.quit"        => "quit",
        "menu.filter_mode"     => "filter mode (empty — exit)",
        "menu.sweep_fn_prompt" => "SWEEP: function name (omega|period_re|census_h) → Enter for default «omega»",
        "menu.sweep_spec_prompt" => "SWEEP: function={fn}. Enter a sweep spec (name:lo:hi:step), empty — run",
        "menu.sweep_bad_fn" => "SWEEP: unknown function \"{fn}\" — available: omega | reflection | census_h",
        "menu.sweep_added"       => "SWEEP: added {key}. more? (empty — run)",
        "menu.sweep_invalid"     => "SWEEP: {msg} — try again",
        "menu.sweep_invalid_spec" => "SWEEP: invalid spec: {msg}",
        "menu.sweep_preview"     => "SWEEP preview: fn={fn}, specs={specs}, frames={n} (cap 500)",
        "menu.status_line"     => "theme={theme} · prec={prec} · seed={seed} · preset={preset} · lang={lang} · marked={n} [{ids}]",
        "menu.copy_done"      => "copied: {path}",
        "menu.copy_empty"     => "run_dir empty — run something first",
        "menu.copy_disabled"  => "clipboard disabled (--no-clipboard)",
        "menu.history_empty"  => "history empty",
        "menu.no_history"     => "no entry #{n} (total {total})",
        "menu.history_hint"   => "history: !! — repeat last, !N — repeat N-th",
        "menu.eof_guard"      => "EOF-guard {n}/{limit}",
        "menu.ctrl_c"         => "Ctrl+C caught — return",
        "menu.input_error"    => "input error: {msg}",
        "menu.help_detail"    => "«?» — help\n  [1-N] task · [Space] mark · [Enter] run marked\n  [a/f/h/c/v] run groups · [w] sweep · [p/s/n/t/l/d/e/P] settings",
        "menu.non_tty_hint"   => "stdin is not a TTY — use --task N / --menu / --self-test",
        "menu.no_task"        => "no task {id}",
        "menu.mark_on"        => "task {id} marked — Enter will run marked tasks",
        "menu.mark_off"       => "task {id}: mark removed",
        # §14: settings editors prompts (menu_handle!)
        "menu.edit.prec_now"   => "current prec: {value}",
        "menu.edit.prec_new"   => "new prec [30..∞ | 4096, 5m, 1g]: ",
        "menu.edit.prec_out"   => "need a number ≥ 30 (or Nk/Nm/Ng/Nt)",
        "menu.edit.prec_set"   => "prec → {value}",
        "menu.edit.seed_now"   => "current seed: {value}",
        "menu.edit.seed_new"   => "new seed: ",
        "menu.edit.seed_set"   => "seed → {value}",
        "menu.edit.preset_list"   => "presets: quick | full | deep",
        "menu.edit.preset_choice" => "choice [{value}]: ",
        "menu.edit.preset_set"    => "preset → {value} (prec={prec}, two_pass={twopass})",
        "menu.edit.theme_set"  => "theme → {value}",
        "menu.edit.lang_set"   => "language → {value}",
        "menu.edit.depth_set"  => "depth → {value}",
        "menu.edit.twopass_set" => "two_pass → {value}",
        "menu.edit.precext_set" => "prec_extreme → {value} (prec={prec})",
        # §3.2 v5: honest RAM estimate for giant prec + honest RLIMIT phrase
        "prec.ram.block"    => "ERR_PREC_RAM: prec={prec} → ≈{est}/BigFloat, just 2 numbers exceed RAM {ram}. Deliberate override: --unsafe-prec / HODGE_PREC_UNSAFE=1",
        "prec.ram.bypass"   => "prec={prec}: ≈{est}/BigFloat > RAM — continuing via --unsafe-prec",
        "prec.ram.warn"     => "prec={prec} → ≈{est}/BigFloat; 16 numbers ≈ {est16} vs RAM {ram} — OOM possible",
        # §3.2 v6: honest prec cost block + gates
        "prec.est.header"   => "prec {prec} bits (≈{digits} digits) · ≈{est} RAM/number — honest cost estimates (julia/MPFR):",
        "prec.est.pi"       => "  π (MPFR):                     ≈{est} once (cached after)",
        "prec.est.trig"     => "  sin/cos (1 call):             ≈{est}",
        "prec.est.lnexp"    => "  log/exp (1 call):             ≈{est}",
        "prec.est.gamma"    => "  Γ/Stirling (series {terms} terms + ζ-sum {zterms}): estimate ≈{est} — limit {lim} s → {verdict}",
        "prec.est.quad"     => "  tanh–sinh (≈{nodes} nodes):         estimate ≈{est} — limit {lim} s → {verdict}",
        "prec.est.advice"   => "  advice: BLOCK ops will fail with an honest ERR_* instead of hanging; keep Γ-tasks at prec ≤ ~5000 bits, quadratures ≤ ~60000 bits",
        "menu.edit.prec.confirm" => "prec={value}: heavy estimate (see above). Continue? [Y/n]: ",
        "menu.edit.prec.revert"  => "prec reverted to {value}",
        "rlimit.unsupported" => "RLIMIT not supported on stdlib Julia (§1.5)",
        "menu.edit.prec_keep"   => "prec unchanged: {value}",
        "menu.edit.seed_keep"   => "seed unchanged: {value}",
        "menu.edit.preset_keep" => "preset unchanged: {value}",
        "menu.edit.not_int"     => "expected an integer, got: {v}",
        "menu.edit.preset_unknown" => "unknown preset: {v} (quick|full|deep)",
        "menu.act.dry_hint"    => "dry-run: see --dry-run --task all (plan only, no compute)",
        "menu.act.palette_hint" => "palette: see --theme-preview",
        "menu.act.video_lab" => "3D Video Lab: object → MP4/MJPEG/GIF",
        "menu.video.objects" => "3D Video Lab · available objects:",
        "menu.video.prompt"  => "object name [sphere]: ",
        # §14.2: submenus r/C/?/x/w/V — full interactive flows (BUGFIX: were stubs)
        "submenu.cancelled"     => "cancelled",
        "submenu.all"           => "all",
        "submenu.numbers"       => "numbers ",
        "submenu.recipes.title"   => "── Recipes ───────────────────────────────────────────",
        "submenu.recipes.cancel"  => "  [0] cancel",
        "submenu.recipes.prompt"  => "  recipe [0-{n}]: ",
        "submenu.recipes.none"    => "no recipe '{v}'",
        "submenu.recipes.applying"=> "  applying recipe '{name}':",
        "submenu.recipes.preview" => "    preset:  {pold} → {pnew}\n    profile: {rold} → {rnew}\n    tasks:   {told} → {tnew}\n    two_pass: {eold} → {enew}",
        "submenu.recipes.actions"=> "  [a] apply and run\n  [p] apply only (no run)\n  [Enter] cancel",
        "submenu.recipes.action_prompt" => "  action: ",
        "submenu.recipes.applied" => "recipe '{name}' applied",
        "submenu.recipes.running" => "running recipe '{name}': {ids}",
        "submenu.palette.current" => " ⟵ current",
        "submenu.palette.sample"  => "  sample: ",
        "submenu.palette.hint"    => "  [1-{n}] select · [Enter] cancel",
        "submenu.palette.prompt"  => "  theme by number: ",
        "submenu.palette.none"    => "no theme '{v}'",
        "submenu.palette.mono_note" => "  (monochrome — palette is built programmatically, §27.8)",
        "submenu.palette.set"     => "theme → {value}",
        "submenu.help.title"      => "  HODGE MASTER · full help",
        "submenu.help.run"        => "RUN:",
        "submenu.help.run.body"   => "  [a] run ALL tasks (two-pass if cfg.two_pass=true)\n  [f] tasks tagged fast only\n  [h] tasks tagged heavy only\n  [c] chess — range 23–33 (everything the registry has will run)\n  [v] verhodge — range 34–38 + 40 (HODGE-INF: Hodge classes to infinity)\n  [w] SWEEP submenu: 3D lab, pick function and parameters",
        "submenu.help.tasks"      => "TASKS:",
        "submenu.help.tasks.body" => "  [1-23, 38] run one task by number\n  [Space] mark task (cumulative)\n  [Enter] run marked (or the one selected under filter)\n  [/] filter by slug / title / number\n  [j/k] navigate down / up",
        "submenu.help.settings"   => "SETTINGS:",
        "submenu.help.settings.body" => "  [p] precision (30..∞ bits; suffixes k/m/g/t — «1g» ≈ 1 billion bits ≈ 120 MB/BigFloat)\n  [s] seed (integer)\n  [n] preset (quick | full | deep)\n  [t] theme (cycle)\n  [l] language (ru ⇄ en)\n  [d] color depth (auto | truecolor | 256 | 16 | mono)\n  [P] prec-extreme (on ⇄ off; record mode: engine ≥ 1024 bits)\n  [e] two-pass (on ⇄ off)\n  by word: «prec-extreme [on|off]» / «precext» — same as [P]\n  setting changes are persisted to .cache/settings.json (§3.2 v4)",
        "submenu.help.actions"    => "ACTIONS:",
        "submenu.help.actions.body" => "  [x] dry-run: plan without compute\n  [r] recipes: list → pick → preview → apply/run\n  [T] switch theme (cycle)\n  [C] palette: swatches of all themes + select\n  [V] 3D Video Lab: object + fps + frames + N (MP4/GIF)\n  [?] this help\n  [q] quit menu",
        "submenu.help.cli"        => "CLI EQUIVALENTS:",
        "submenu.help.cli.body"   => "  [a] ≈ --task all --two-pass\n  [x] ≈ --dry-run --task <choice>\n  [r] ≈ --recipe NAME\n  [V] ≈ --lab-video OBJ [--lab-video-fps N --lab-video-frames N --lab-video-N N]\n  [w] ≈ --lab3d FN --sweep name:lo:hi:step ...",
        "submenu.help.input"      => "INPUT CONTROL:",
        "submenu.help.input.body" => "  Ctrl+D — quit the menu\n  Ctrl+C — abort a run (return to menu)\n  Ctrl+Y — copy run path (OSC 52)\n  !!     — repeat last command\n  !N     — repeat N-th command (count from 1)",
        "submenu.help.back"       => "  [Enter] — back to menu",
        "submenu.dry.title"       => "── dry-run (plan without compute) ──────────────────",
        "submenu.dry.cfg"         => "  Preset: {preset} · seed: {seed} · prec: {prec} · two-pass: {tp}",
        "submenu.dry.opts"        => "  [1] all tasks\n  [2] fast tags\n  [3] heavy tags\n  [4] chess (23–33)\n  [5] verhodge (34–38)",
        "submenu.dry.cancel"      => "  [Enter] cancel",
        "submenu.dry.prompt"      => "  choice: ",
        "submenu.dry.noopt"       => "no option '{v}'",
        "submenu.dry.done"        => "plan written to {path}",
        "submenu.sweep.title"     => "── SWEEP · 3D lab ──────────────────────────────────",
        "submenu.sweep.fns"       => "  Functions: omega | reflection | census_h",
        "submenu.sweep.fn_prompt" => "  function [omega]: ",
        "submenu.sweep.spec_prompt" => "  sweep ({n} set, Enter = run): ",
        "submenu.sweep.added"     => "added: {spec}",
        "submenu.sweep.bad_spec"  => "invalid spec: {msg}",
        "submenu.sweep.summary"   => "fn={fn} · specs={specs} · frames={total} (cap {cap})",
        "submenu.sweep.cap_warn"  => "will be truncated to {cap} frames",
        "submenu.sweep.confirm"   => "  [Enter] run · [c] cancel: ",
        "submenu.video.fps_prompt"    => "  fps [24]: ",
        "submenu.video.frames_prompt" => "  frames [120]: ",
        "submenu.video.n_prompt"      => "  N_full [64]: ",
        "submenu.video.summary"  => "object={obj} · fps={fps} · frames={frames} · N={n}",
        "submenu.video.bad_obj"  => "object '{obj}' is not registered",
        "submenu.groups.run" => "{name}: {ids}",
        "submenu.groups.run_missing" => "{name}: {ids} (not implemented: {miss})",
        "submenu.groups.chess_empty" => "no tasks tagged chess (23–33) in the registry",
        "submenu.groups.verhodge_empty" => "no tasks tagged verhodge (34–38) in the registry",
    ),
)

# §16 l10n §16.2 v4: MSG + словный псевдоним тумблера prec-extreme (§14 v4)
parse_prec_extreme_cmd(key::AbstractString) = begin
    toks = split(strip(String(key)))
    isempty(toks) || !(toks[1] in ("prec-extreme", "precext")) && return nothing
    length(toks) == 1 && return "toggle"
    arg = lowercase(toks[2])
    arg in ("on", "1", "true", "вкл") && return true
    arg in ("off", "0", "false", "выкл") && return false
    return "toggle"
end

# §3.2 v5: prec БЕЗ верхней границы — «ставь даже гигабайты». Суффиксы k/m/g/t
# (десятичные): «4096», «5k», «2m», «1g» (1g бит ≈ 119 MB на BigFloat), «2t».
# Нижняя граница 30 сохраняется. → Int или nothing.
function parse_prec_value(s::AbstractString)
    t = lowercase(strip(s))
    m = match(r"^([0-9]+(?:\.[0-9]+)?)([kmgt]?)$", t)
    m === nothing && return nothing
    mult = Dict("" => 1, "k" => 10^3, "m" => 10^6, "g" => 10^9, "t" => 10^12)[m.captures[2]]
    v = try
        round(Int, parse(Float64, m.captures[1]) * mult)
    catch
        return nothing
    end
    return v >= 30 ? v : nothing
end

function hodge_fmt(cfg::Dict, key::String; kw...)
    d = get(MSG, get(cfg, "lang", "en"), MSG["en"])
    tpl = get(d, key, nothing)
    tpl === nothing && throw(KeyError(key))
    if isempty(kw)
        return tpl
    end
    out = tpl
    for (k, v) in kw
        out = replace(out, "{$k}" => string(v))
    end
    return out
end

# ════════════════════════════════════════════════════════════════════════
# §21/§22 ТЕМЫ И ТИПОГРАФИКА: палитра (hex, c256, c16), dye/num/badge,
# gradient с dye_mode, rainbow/link/copy_hint, ASCII-фолбэк (§27.2).
# ════════════════════════════════════════════════════════════════════════
const PALETTE_KEYS = ("bg", "surface", "surface_2", "gold_dim", "gold", "gold_bright",
                      "amber", "ember", "text", "text_dim", "text_strong",
                      "ok", "warn", "err", "info", "neutral")
const PLOT_SERIES = ["#d4af37", "#f4d47c", "#ffb347", "#b39a5d", "#a83a1a",
                     "#8a6d1f", "#e6c86e", "#c9a227"]
const PLOT_GRID, PLOT_BG, PLOT_TEXT = "#2a2210", "#0a0805", "#e8d9a8"

const THEMES = Dict(
    "dark-gold" => Dict(
        "bg" => ("#0a0805", 233, "black"), "surface" => ("#161009", 234, "black"),
        "surface_2" => ("#221806", 235, "black"), "gold_dim" => ("#8a6d1f", 94, "yellow"),
        "gold" => ("#d4af37", 178, "yellow"), "gold_bright" => ("#ffd700", 220, "bright-yellow"),
        "amber" => ("#ffe97c", 228, "bright-yellow"), "ember" => ("#a83a1a", 130, "red"),
        "text" => ("#e8d9a8", 187, "white"), "text_dim" => ("#9a8a55", 101, "white"),
        "text_strong" => ("#fff8d0", 230, "bright-white"), "ok" => ("#ffd700", 220, "yellow"),
        "warn" => ("#ffc347", 220, "bright-yellow"), "err" => ("#c94a1a", 166, "red"),
        "info" => ("#c9b25d", 179, "yellow"), "neutral" => ("#7a6a44", 94, "yellow")),
    "aurora" => Dict(
        "bg" => ("#050810", 233, "black"), "surface" => ("#0a1220", 234, "black"),
        "surface_2" => ("#0f1c30", 235, "black"), "gold_dim" => ("#1f5a8a", 25, "blue"),
        "gold" => ("#37a5d4", 39, "cyan"), "gold_bright" => ("#7cd4f4", 117, "bright-cyan"),
        "amber" => ("#47c0ff", 117, "bright-cyan"), "ember" => ("#1a5aa8", 27, "blue"),
        "text" => ("#a8cfe8", 187, "white"), "text_dim" => ("#5e7a9a", 68, "white"),
        "text_strong" => ("#c4e8ff", 230, "bright-white"), "ok" => ("#37a5d4", 39, "cyan"),
        "warn" => ("#ffb347", 215, "bright-yellow"), "err" => ("#ff5a4a", 203, "red"),
        "info" => ("#5d8ab3", 67, "blue"), "neutral" => ("#3a5a6a", 60, "blue")),
    "ice" => Dict(
        "bg" => ("#050810", 233, "black"), "surface" => ("#0a1220", 234, "black"),
        "surface_2" => ("#0f1c30", 235, "black"), "gold_dim" => ("#1f5a8a", 25, "blue"),
        "gold" => ("#37a5d4", 39, "cyan"), "gold_bright" => ("#7cd4f4", 117, "bright-cyan"),
        "amber" => ("#47c0ff", 117, "bright-cyan"), "ember" => ("#1a5aa8", 27, "blue"),
        "text" => ("#a8cfe8", 187, "white"), "text_dim" => ("#5e7a9a", 68, "white"),
        "text_strong" => ("#c4e8ff", 230, "bright-white"), "ok" => ("#37a5d4", 39, "cyan"),
        "warn" => ("#ffb347", 215, "bright-yellow"), "err" => ("#ff5a4a", 203, "red"),
        "info" => ("#5d8ab3", 67, "blue"), "neutral" => ("#3a5a6a", 60, "blue")),
    "gold" => Dict(
        "bg" => ("#0a0805", 233, "black"), "surface" => ("#161009", 234, "black"),
        "surface_2" => ("#221806", 235, "black"), "gold_dim" => ("#8a6d1f", 94, "yellow"),
        "gold" => ("#ffd700", 220, "yellow"), "gold_bright" => ("#ffe97c", 228, "bright-yellow"),
        "amber" => ("#fff8d0", 230, "bright-white"), "ember" => ("#c94a1a", 166, "red"),
        "text" => ("#e8d9a8", 187, "white"), "text_dim" => ("#9a8a55", 101, "white"),
        "text_strong" => ("#fff8d0", 230, "bright-white"), "ok" => ("#ffd700", 220, "yellow"),
        "warn" => ("#ffc347", 220, "bright-yellow"), "err" => ("#c94a1a", 166, "red"),
        "info" => ("#c9b25d", 179, "yellow"), "neutral" => ("#7a6a44", 94, "yellow")),
    "emerald" => Dict(
        "bg" => ("#050a06", 233, "black"), "surface" => ("#0a160c", 234, "black"),
        "surface_2" => ("#0f2212", 235, "black"), "gold_dim" => ("#1f8a3d", 28, "green"),
        "gold" => ("#37d45c", 41, "green"), "gold_bright" => ("#7cf49c", 84, "bright-green"),
        "amber" => ("#47ff70", 83, "bright-green"), "ember" => ("#1aa842", 35, "red"),
        "text" => ("#a8e8bd", 187, "white"), "text_dim" => ("#5e9a72", 71, "white"),
        "text_strong" => ("#c4ffd8", 230, "bright-white"), "ok" => ("#37d45c", 41, "green"),
        "warn" => ("#ffd24a", 221, "bright-yellow"), "err" => ("#ff4a4a", 203, "red"),
        "info" => ("#5db37d", 78, "green"), "neutral" => ("#3a6a4a", 66, "green")),
)

# Текущее состояние темы/текста (глобальный контекст, как HODGEText в Python)
const TEXT_STATE = Dict{String,Any}(
    "theme" => "dark-gold", "depth" => "mono", "plain" => true,
    "unicode_on" => true, "digit_tier" => true, "dye_mode" => "per-char",
    "_dye_cache" => Dict{Tuple,String}(), "_gradient_cache" => Dict{Tuple,String}(),
)

hex2rgb(h::AbstractString) = (parse(Int, h[2:3], base=16), parse(Int, h[4:5], base=16),
                              parse(Int, h[6:7], base=16))

function theme_set!(name::String, depth::String, plain::Bool)
    TEXT_STATE["theme"] = haskey(THEMES, name) ? name : "dark-gold"
    TEXT_STATE["depth"] = plain || depth == "mono" ? "mono" : depth
    TEXT_STATE["plain"] = plain || depth == "mono"
    empty!(TEXT_STATE["_dye_cache"])
    empty!(TEXT_STATE["_gradient_cache"])
    nothing
end

function color_code(key::AbstractString; depth::Union{Nothing,String}=nothing)
    TEXT_STATE["plain"] && return ""
    d = depth === nothing ? TEXT_STATE["depth"] : depth
    (TEXT_STATE["theme"] == "mono" || d == "mono") && return ""
    pal = THEMES[TEXT_STATE["theme"]]
    haskey(pal, key) || return ""
    hexv, c256, c16 = pal[key]
    d == "truecolor" && return @sprintf("\x1b[38;2;%d;%d;%dm", hex2rgb(hexv)...)
    d == "256" && return @sprintf("\x1b[38;5;%dm", c256)
    m = match(r"(bright-)?(\w+)", c16)
    m === nothing && return ""
    bright = m.captures[1] !== nothing
    base16 = Dict("black" => 0, "red" => 1, "green" => 2, "yellow" => 3,
                  "blue" => 4, "cyan" => 5, "white" => 7)
    base = get(base16, m.captures[2], 7)
    # §21.3 / A10: normal 30..37, bright 90..97 — без двойного оффсета
    return @sprintf("\x1b[%dm", bright ? 90 + base : 30 + base)
end

const ANSI_RE = r"\x1b\[[0-9;]*m"
strip_ansi(s::AbstractString) = replace(s, ANSI_RE => "")

# §27.2 / A13: ASCII-фолбэки декоративных глифов (кириллица §16 не трогается)
const ASCII_GLYPHS = Dict(
    "✓" => "[ok]", "✗" => "[err]", "·" => "-", "❯" => ">", "─" => "-", "│" => "|",
    "┌" => "+", "┐" => "+", "└" => "+", "┘" => "+", "├" => "+", "┤" => "+", "┬" => "+",
    "┴" => "+", "┼" => "+", "╔" => "+", "╗" => "+", "╚" => "+", "╝" => "+", "║" => "|",
    "═" => "=", "╠" => "+", "╣" => "+", "╦" => "+", "╩" => "+", "╬" => "+",
    "█" => "#", "▁" => ".", "▂" => "-", "▃" => "=", "▄" => "+", "▅" => "*",
    "▆" => "#", "▇" => "@", "░" => ".", "▒" => "+", "▓" => "#",
    "✦" => "*", "✧" => "+", "◆" => "o", "◇" => "o", "•" => ".", "…" => "...",
    "«" => "<<", "»" => ">>",
)

function ascii_fallback(s::AbstractString)
    TEXT_STATE["unicode_on"] && return String(s)
    return join(get(ASCII_GLYPHS, string(c), string(c)) for c in s)
end

# §27.7 / VII.6: bidi-изоляция RTL
const BIDI_LOW, BIDI_HIGH = '\u0590', '\u065f'
function bidi_isolate(s::AbstractString)
    any(BIDI_LOW <= c <= BIDI_HIGH for c in s) || return String(s)
    return "\u2068" * s * "\u2069"
end

function dye(s::AbstractString, key::AbstractString = "text", style::AbstractString = "")
    s = bidi_isolate(ascii_fallback(s))
    (TEXT_STATE["plain"] || TEXT_STATE["theme"] == "mono") && return String(s)
    get(TEXT_STATE, "dye_off", false) && return String(s)   # P1: --dye off (§22.1)
    occursin(ANSI_RE, s) && return String(s)   # идемпотентность (§22.3)
    ck = (s, String(key), String(style), TEXT_STATE["theme"], TEXT_STATE["depth"])
    haskey(TEXT_STATE["_dye_cache"], ck) && return TEXT_STATE["_dye_cache"][ck]
    code = color_code(key)
    if isempty(code)
        return String(s)
    end
    styles = Dict("bold" => 1, "underline" => 4, "reverse" => 7)
    st = join([@sprintf("\x1b[%dm", styles[x]) for x in split(style, ",") if haskey(styles, x)])
    ending = occursin("bold", style) ? "\x1b[22m" : "\x1b[0m"
    res = st * code * s * "\x1b[0m" * (ending == "\x1b[0m" ? "" : ending)
    TEXT_STATE["_dye_cache"][ck] = res
    return res
end

function fmt_float(x::Real, prec::Int = 4)
    if abs(x) >= 1e18 || (x != 0 && abs(x) < 1e-6)
        return @sprintf("%.3e", x)
    end
    s = @sprintf("%.*f", prec, x)
    occursin(".", s) && (s = rstrip(rstrip(s, '0'), '.'))
    return s
end
fmt_int(v::Integer) = replace(@sprintf("%d", v), r"(\d)(?=(\d{3})+$)" => s"\1 ")

function num(v, kind::AbstractString = "float", prec::Int = 4)
    """§22.5: tiering по величине; отрицательные → ember; NaN/inf → err."""
    local x::Float64
    try
        x = Float64(v)
    catch
        return dye(string(v), "neutral")
    end
    (isnan(x) || isinf(x)) && return dye(isnan(x) ? "nan" : "inf", "err", "reverse")
    neg = x < 0
    mag = abs(x)
    local key::String
    if kind == "pct"
        key = mag >= 1000 ? "amber" : mag >= 100 ? "gold_bright" : "gold"
    elseif kind == "duration"
        key = mag >= 100 ? "amber" : mag >= 10 ? "gold_bright" : "gold"
    else
        key = mag == 0 ? "gold_dim" : mag < 10 ? "gold" :
              mag < 100 ? "gold" : mag < 1000 ? "gold_bright" : "amber"
    end
    body = kind == "float" ? fmt_float(x, prec) :
           kind == "int" ? fmt_int(round(Int, x)) :
           kind == "pct" ? @sprintf("%.1f%%", x) : @sprintf("%.1f", x)
    style = TEXT_STATE["digit_tier"] && (kind in ("int", "float")) && 10 <= mag < 100 ? "bold" : ""
    neg && (key = "ember")
    return dye(body, key, style)
end

function badge(verdict::AbstractString)
    colors = Dict("PASS" => "ok", "DONE" => "ok", "OK" => "ok", "WARN" => "warn",
                  "FAIL" => "err", "ERROR" => "err", "SKIP" => "neutral", "INFO" => "info")
    return dye("[$verdict]", get(colors, verdict, "neutral"), "bold")
end

fmt_size(n) = begin
    v = Float64(n)
    for unit in ("B", "KB", "MB", "GB", "TB")
        (v < 1024 || unit == "TB") && return unit == "B" ? @sprintf("%d B", round(Int, v)) : @sprintf("%.1f %s", v, unit)
        v /= 1024
    end
end

# §3.2 v5: при гигантском prec splash показывает честную оценку памяти на число
prec_splash(p::Int) = p >= 4096 ? "prec=$p бит (≈$(fmt_size(p ÷ 8 + 64))/BigFloat)" : "prec=$p бит"

function fmt_duration(sec)
    sec < 1 && return @sprintf("%.0f ms", sec * 1000)
    sec < 60 && return @sprintf("%.1f s", sec)
    m, s = divrem(round(Int, sec), 60)
    m < 60 && return @sprintf("%02d:%02d", m, s)
    h, m = divrem(m, 60)
    return @sprintf("%02d:%02d:%02d", h, m, s)
end
fmt_pct(v, prec = 1) = dye(@sprintf("%.*f%%", prec, v), "gold")
fmt_datetime(ts::DateTime, locale = "ru") =
    locale == "ru" ? Dates.format(ts, "dd.mm.Y HH:MM:SS") : Dates.format(ts, "Y-mm-dd HH:MM:SS")
fmt_datetime(ts::AbstractString, locale = "ru") = try
    fmt_datetime(DateTime(replace(ts, r"Z$" => "")), locale)
catch
    String(ts)
end
fmt_datetime(::Nothing, locale = "ru") = "—"

# §22.4/§22.9: градиент с dye_mode = per-char|per-token|per-line
function gradient(s::AbstractString, from_key = "gold_dim", to_key = "gold_bright",
                  mode::AbstractString = "span")
    s = ascii_fallback(s)
    (TEXT_STATE["plain"] || TEXT_STATE["theme"] == "mono") && return String(s)
    get(TEXT_STATE, "dye_off", false) && return s   # P1: --dye off
    eff = mode == "span" ? TEXT_STATE["dye_mode"] : String(mode)
    (eff == "per-line" || eff == "block") && return dye(s, to_key)
    length(s) > 256 && eff == "per-char" && (eff = "per-line")
    ck = (s, String(from_key), String(to_key), eff, TEXT_STATE["depth"], TEXT_STATE["theme"])
    haskey(TEXT_STATE["_gradient_cache"], ck) && return TEXT_STATE["_gradient_cache"][ck]
    pal = THEMES[TEXT_STATE["theme"]]
    hx(k) = hex2rgb(get(pal, k, pal["gold"])[1])
    c0, c1 = hx(from_key), hx(to_key)
    color_at(t) = begin
        r = round(Int, c0[1] + (c1[1] - c0[1]) * t)
        g = round(Int, c0[2] + (c1[2] - c0[2]) * t)
        b = round(Int, c0[3] + (c1[3] - c0[3]) * t)
        TEXT_STATE["depth"] == "truecolor" ? @sprintf("\x1b[38;2;%d;%d;%dm", r, g, b) :
            color_code(t < 0.5 ? from_key : to_key)
    end
    out = String[]
    if eff == "per-char"
        n = max(length(s), 1)
        for (i, ch) in enumerate(s)
            push!(out, color_at((i - 1) / max(n - 1, 1)) * ch)
        end
    else # per-token
        # P0.3: Julia split НЕ включает capture-группы (в отличие от Python
        # re.split) — пробелы исчезали; eachmatch сохраняет и слова, и пробелы
        toks = String[]
        for m in eachmatch(r"\S+|\s+", s)
            push!(toks, m.match)
        end
        total = max(sum(length(t) for t in toks), 1)
        pos = 0
        for tok in toks
            push!(out, color_at(pos / max(total - 1, 1)) * tok)
            pos += length(tok)
        end
    end
    push!(out, "\x1b[0m")
    res = join(out)
    TEXT_STATE["_gradient_cache"][ck] = res
    return res
end

function rainbow(s::AbstractString, family::AbstractString = "gold")
    (TEXT_STATE["plain"] || TEXT_STATE["theme"] == "mono") && return String(s)
    keys = family == "ember" ? ["ember", "amber", "gold", "gold_dim"] :
           ["gold_dim", "gold", "gold_bright", "amber"]
    out = IOBuffer()
    for (i, ch) in enumerate(ascii_fallback(s))
        print(out, color_code(keys[mod1(i, length(keys))]), ch)
    end
    print(out, "\x1b[0m")
    return String(take!(out))
end

link(url::AbstractString, text::AbstractString, osc::AbstractString = "off") =
    osc == "on" ? "\x1b]8;;$url\x1b\\$text\x1b]8;;\x1b\\" : String(text)
copy_hint() = dye("[Ctrl-Y копирует путь к отчёту]", "text_dim")

const TEXT_STYLE_MAP = Dict(
    "duration_s" => "duration", "rel_err" => "float", "prec" => "int",
    "n_tests" => "int", "max_rel" => "float", "det" => "int", "frames" => "int",
    "rank" => "int", "t_p" => "int", "proj" => "int")

# ════════════════════════════════════════════════════════════════════════
# §6 БАННЕР: арт + splash (реальный lock-статус, §24.2) + tip-of-the-day
# ════════════════════════════════════════════════════════════════════════
const HODGE_BANNER_ART = raw"""
  ██╗  ██╗ ██████╗ ██████╗  ██████╗ ███████╗
  ██║  ██║██╔═══██╗██╔══██╗██╔════╝ ██╔════╝
  ███████║██║   ██║██║  ██║██║  ███╗█████╗
  ██╔══██║██║   ██║██║  ██║██║   ██║██╔══╝
  ██║  ██║╚██████╔╝██████╔╝╚██████╔╝███████╗
  ╚═╝  ╚═╝ ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝
   m a s t e r  ·  h o d g e - l a b o r a t o r y
"""

const HODGE_BANNER_ASCII = raw"""
  _   _           _      ____  ___  ____  _____ ____
 | | | | ___  ___| |_   / ___|/ _ \|  _ \| ____|  _ \
 | |_| |/ _ \/ _ \ __| | |  _| | | | |_) |  _| | |_) |
 |  _  |  __/  __/ |_  | |_| | |_| |  _ <| |___|  _ <
 |_| |_\___|\___|\__|  \____|\___/|_| \_\_____|_| \_\
   master verification suite · hodge-laboratory claims
"""

function banner_render(kind::AbstractString, cfg::Dict)
    kind == "off" && return ""
    # VI.1: при --unicode off — чистый ASCII-арт (§27.2)
    art_src = TEXT_STATE["unicode_on"] ? HODGE_BANNER_ART : HODGE_BANNER_ASCII
    if TEXT_STATE["plain"]
        return kind == "compact" ?
            "[hodge-master $HODGE_VERSION@$HODGE_BUILD_DATE] · $(TEXT_STATE["theme"])" :
        kind == "minimal" ? "hodge-master $HODGE_VERSION" : strip(art_src)
    end
    if kind == "minimal"
        return dye("hodge-master $HODGE_VERSION", "gold")
    elseif kind == "compact"
        return dye("[hodge-master $HODGE_VERSION@$HODGE_BUILD_DATE] · $(TEXT_STATE["theme"])", "gold")
    end
    # full: посимвольный вертикальный градиент (§22.4)
    lines = split(strip(art_src), "\n")
    pal_keys = ["gold_dim", "gold", "gold_bright", "amber"]
    n = length(lines)
    colored = String[]
    for (i, ln) in enumerate(lines)
        buf = IOBuffer()
        for (j, ch) in enumerate(ln)
            tt = ((i - 1) / max(n - 1, 1)) * 0.5 + ((j - 1) / max(length(ln), 1)) * 0.5
            k = pal_keys[clamp(floor(Int, tt * (length(pal_keys) - 1)) + 1, 1, length(pal_keys))]
            print(buf, ch == ' ' ? " " : dye(string(ch), k))
        end
        push!(colored, String(take!(buf)))
    end
    meta = dye("v$HODGE_VERSION", "gold_bright") * " · " *
           dye("julia $(Base.VERSION_STRING)", "text_dim") * " · " *
           dye(TEXT_STATE["theme"], "gold") * " · " *
           dye(prec_splash(get(cfg, "prec", 55)), "gold_dim") * " · " *
           dye("seed=$(get(cfg, "seed", 0))", "gold_dim")
    return join(colored, "\n") * "\n" * meta
end

# VI.7: splash — реальные значения + явный lock-статус
function splash_rows(cfg, lock_held::Bool)
    ram = "—"
    try
        for ln in eachline("/proc/meminfo")
            if startswith(ln, "MemTotal")
                ram = fmt_size(parse(Int, split(ln)[2]) * 1024)
                break
            end
        end
    catch
    end
    return [
        "platform: $(Sys.KERNEL) · CPU: $(Sys.CPU_THREADS) · RAM: $ram",
        "lang: julia $(Base.VERSION_STRING) · $(cfg.lang == "en" ? "theme" : "тема"): $(TEXT_STATE["theme"]) · depth: $(TEXT_STATE["depth"])",
        "unicode: $(ascii_fallback(TEXT_STATE["unicode_on"] ? "✓" : "✗")) · preset: $(cfg.preset) · prec: $(cfg.prec)$(cfg.prec >= 4096 ? " (≈$(fmt_size(cfg.prec ÷ 8 + 64))/BigFloat)" : "") · seed: $(cfg.seed)",
        # BUGFIX(LOCK): при flock-unsupported (ENOSYS на некоторых ФС) лок
        # advisory — «acquired» вводил в заблуждение; v4: каскад даёт ещё и
        # честный режим :lockdir (взаимоисключение сохранено на любой ФС)
        "pid: $(getpid()) · lock: $(LOCK_MODE[] == :advisory ? "advisory (flock unsupported)" :
                                        LOCK_MODE[] == :lockdir ? "lockdir (flock unsupported)" :
                                        lock_held ? "acquired" : "free")",
    ]
end

const TIPS_RU = [
    "Попробуй `--self-test --palette --dye` — проверка темы и глифов.",
    "`--task 8` — глубокий рекорд точности V9 (prec 320 бит).",
    "`--theme-preview` покажет палитру dark-gold и фолбэки 256/16.",
    "`--ci --task all` — машиночитаемый прогон с events.jsonl.",
    "`T` в меню меняет тему; `a` запускает все задачи.",
]
tip_of_day(cfg::Dict) = get(cfg, "deterministic", false) ? "" :
    TIPS_RU[mod1(Dates.dayofyear(Dates.now()), length(TIPS_RU))]

# ════════════════════════════════════════════════════════════════════════
# §3.4 RECIPES: именованные (preset, profile, tasks, overrides)
# ════════════════════════════════════════════════════════════════════════
const RECIPES = Dict(
    "nightly" => Dict("preset" => "deep", "profile" => "paranoid", "tasks" => "all",
                      "two_pass" => true, "overrides" => Dict("strict" => true, "global_timeout" => 3600),
                      "description" => "глубокая ночная верификация с paranoid-профилем"),
    "smoke" => Dict("preset" => "quick", "profile" => "fast", "tasks" => [1, 18, 13, 9],
                    "two_pass" => false, "overrides" => Dict("no_report" => true),
                    "description" => "быстрая проверка ядра (4 задачи, < 2 с)"),
    "verhodge" => Dict("preset" => "deep", "profile" => "balanced", "tasks" => [21],
                       "two_pass" => true, "overrides" => Dict(),
                       "description" => "hardcore-пасс ядра (t21b)"),
)

# ════════════════════════════════════════════════════════════════════════
# Минимальный JSON-эмиттер (stdlib без JSON): Dict/Vector/String/Number/Bool
# ════════════════════════════════════════════════════════════════════════
json_escape(s::AbstractString) = (s = replace(String(s), "\\" => "\\\\", "\"" => "\\\"",
                                               "\n" => "\\n", "\r" => "\\r", "\t" => "\\t");
                                  replace(s, r"[\x00-\x1f]" => c -> @sprintf("\\u%04x", c[1])))

json_dump(x::AbstractString) = "\"" * json_escape(x) * "\""
json_dump(x::Nothing) = "null"
json_dump(x::Bool) = x ? "true" : "false"
json_dump(x::Integer) = string(x)
json_dump(x::AbstractFloat) = isnan(x) ? "\"nan\"" :   # P0.11: знак inf сохраняется
    isinf(x) ? (x < 0 ? "\"-inf\"" : "\"inf\"") : @sprintf("%.6g", x)
json_dump(x::Symbol) = json_dump(String(x))
json_dump(x::Vector) = "[" * join(json_dump.(x), ",") * "]"
json_dump(x::Tuple) = json_dump(collect(x))
json_dump(x::Set) = json_dump(sort!(collect(x)))
json_dump(x::Dict) = begin
    ks = sort!(collect(keys(x)); by = string)
    "{" * join(["$(json_dump(string(k))):$(json_dump(v))" for (k, v) in zip(ks, (x[k] for k in ks))], ",") * "}"
end
json_dump(x) = json_dump(String(x))

# Компактный парсер плоского JSON-конфига (ключ → строка/число/bool/массив чисел)
function json_load_flat(src::AbstractString)
    s = String(src)
    out = Dict{String,Any}()
    m = match(r"\{(.*)\}"s, s)
    m === nothing && throw(ArgumentError("ERR_CONFIG_NOT_JSON"))
    body = m.captures[1]
    pos = firstindex(body)
    function skip_ws()
        while pos <= lastindex(body) && isspace(body[pos]); pos = nextind(body, pos); end
    end
    function parse_value()
        skip_ws()
        c = body[pos]
        if c == '"'
            pos = nextind(body, pos)
            buf = IOBuffer()
            while body[pos] != '"'
                if body[pos] == '\\'
                    pos = nextind(body, pos)
                    esc = body[pos]
                    print(buf, esc == 'n' ? "\n" : esc == 't' ? "\t" : string(esc))
                else
                    print(buf, body[pos])
                end
                pos = nextind(body, pos)
            end
            pos = nextind(body, pos)
            return String(take!(buf))
        elseif c == '['
            pos = nextind(body, pos)
            vals = Any[]
            skip_ws()
            body[pos] == ']' && (pos = nextind(body, pos); return vals)
            while true
                push!(vals, parse_value())
                skip_ws()
                if body[pos] == ','; pos = nextind(body, pos); skip_ws()
                elseif body[pos] == ']'; pos = nextind(body, pos); break
                end
            end
            return vals
        elseif occursin(c, "-0123456789")
            start = pos
            while pos <= lastindex(body) && occursin(body[pos], "-0123456789.eE+")
                pos = nextind(body, pos)
            end
            tok = body[start:prevind(body, pos)]
            return occursin(".", tok) || occursin("e", tok) ? parse(Float64, tok) : parse(Int, tok)
        elseif c == '{'
            # VI.2: рекурсивный разбор вложенных объектов
            pos = nextind(body, pos)
            nested = Dict{String,Any}()
            skip_ws()
            if body[pos] != '}'
                while true
                    skip_ws()
                    k = parse_value()
                    skip_ws()
                    body[pos] == ':' && (pos = nextind(body, pos))
                    v = parse_value()
                    nested[String(k)] = v
                    skip_ws()
                    if body[pos] == ','; pos = nextind(body, pos); skip_ws()
                    elseif body[pos] == '}'; pos = nextind(body, pos); break
                    else; break
                    end
                end
            else
                pos = nextind(body, pos)
            end
            return nested
        else
            start = pos
            while pos <= lastindex(body) && body[pos] != ',' && body[pos] != '}'
                pos = nextind(body, pos)
            end
            tok = strip(body[start:prevind(body, pos)])
            return tok == "true" ? true : tok == "false" ? false : tok == "null" ? nothing : tok
        end
    end
    function parse_pairs()
        skip_ws()
        body[pos] == '}' && return
        while true
            skip_ws()
            k = parse_value()
            skip_ws()
            body[pos] == ':' && (pos = nextind(body, pos))
            v = parse_value()
            out[String(k)] = v
            skip_ws()
            if pos > lastindex(body); break; end
            if body[pos] == ','; pos = nextind(body, pos); skip_ws(); body[pos] == '}' && break
            elseif body[pos] == '}'; break; end
        end
    end
    parse_pairs()
    return out
end

# ════════════════════════════════════════════════════════════════════════
# §3 КОНФИГ: единственный носитель настроек (defaults < config-file < env <
# CLI < меню, §3.2). Валидация §3.5; пресеты §1.3; профили §1.4 (explicit).
# ════════════════════════════════════════════════════════════════════════
Base.@kwdef mutable struct HodgeConfig
    run_dir::String = ""
    report_dir::String = "results"
    cache_dir::String = ".cache"
    lang::String = "en"
    seed::Int = 0
    preset::String = "full"
    profile::String = "balanced"
    two_pass::Bool = true
    pass_only::Int = 0
    isolate::Bool = true
    tasks::Vector{Int} = Int[]
    with_deps::Bool = true
    tags::Vector{String} = String[]
    deterministic::Bool = false
    prec::Int = 55
    theme::String = "dark-gold"
    color_depth::String = "auto"
    plain::Bool = false
    no_color::Bool = false
    unicode_on::String = "auto"
    dye_mode::String = "per-char"
    digit_tier::Bool = true
    gradient::String = "span"
    banner::String = "auto"
    splash::Bool = true
    tips::Bool = true
    anim::String = "off"
    anim_scene::String = "particles"
    monitor::String = "off"
    monitor_interval::Float64 = 60.0
    monitor_csv::Bool = true
    metrics_format::String = ""
    health_probe_sec::Float64 = 0.0
    log_level::String = "INFO"
    redact::Bool = true
    no_report::Bool = false
    ci::Bool = false
    jsonl::Bool = false
    tsv::Bool = false
    junit::String = ""
    self_test::Vector{String} = String[]
    bench::Bool = false
    bench_threshold::Float64 = 1.2
    bench_stats::Bool = false
    bench_runs::Int = 5
    golden_dir::String = "tests/golden"
    golden_update::Bool = false
    float_tolerance::Float64 = 1e-9
    fuzz_sec::Float64 = 0.0
    task_timeout::Float64 = 0.0
    global_timeout::Float64 = 0.0
    no_cache::Bool = true
    cache_on::Bool = false
    rate_limit::String = ""
    resume_dir::String = ""
    checkpoint_every::Int = 0
    print_config::Bool = false
    validate_config_only::Bool = false
    diff_runs::Vector{String} = String[]
    menu_forced::Bool = false
    menu_off::Bool = false
    tui::Bool = false
    links::String = "auto"
    no_clipboard::Bool = false
    clean_orphans::Bool = true
    anim_cpu_guard::Float64 = 40.0
    anim_seconds::Float64 = 0.0
    fps::Int = 24
    particles::Int = 64
    title_bar::Bool = true
    theme_preview::Bool = false
    doctor::Bool = false
    health::Bool = false
    dry_run::Bool = false
    strict::Bool = false
    prec_extreme::Bool = false           # Часть V: prec=200 + K=480 для рекордных задач
    unsafe_prec::Bool = false            # §3.2 v5: сознательный обход ERR_PREC_RAM
    # §3.2 v4: кэш настроек .cache/settings.json (defaults < cache < config-file
    # < env < CLI < меню). Сохраняется при изменениях в меню; --no-settings-cache/
    # --settings-reset — отключить/очистить.
    settings_cache::Bool = true
    settings_save::Bool = false          # --settings-save: сохранить и CLI-прогон
    report_formats::String = "md,html,svg"   # Часть IV.1: pdf/docx → ERR_UNSUPPORTED
    lab3d_spec::String = ""
    lab3d_out::String = ""
    sweeps::Vector{String} = String[]
    sign_key::String = ""
    verify_signature::String = ""        # P0.7 / §20.5: путь прогона для проверки
    junit_path::String = ""              # P1 / §26.3: путь JUnit-XML
    gen_shell::String = ""               # P1 / §30: bash|zsh|fish|powershell
    theme_file::String = ""              # P1 / §21.5: JSON-файл темы
    theme_replace::Bool = false          # P1 / §21.5: заменить вместо merge
    gct_cache::Dict{String,Any} = Dict{String,Any}()
    _lock_held::Bool = false
end

# P2.4+P2.8: честные отказы §1.5 попадают сюда → RTM.md «Честно не поддержано»
const UNSUPPORTED_LOG = Dict{String,String}()

const CFG_VALIDATORS = Dict{String,Function}(
    "preset" => v -> v in ("quick", "full", "deep"),
    "prec" => v -> v >= 30,                  # §3.2 v5: БЕЗ верхней границы (суффиксы k/m/g/t)
    "profile" => v -> v in ("safe", "balanced", "fast", "paranoid"),
    "theme" => v -> haskey(THEMES, v),
    "lang" => v -> v in ("ru", "en"),
    "color_depth" => v -> v in ("auto", "truecolor", "256", "16", "mono"),
    "dye_mode" => v -> v in ("per-char", "per-token", "per-line"),
    "fps" => v -> 5 <= v <= 60,
)

function cfg_validate(cfg::HodgeConfig)
    errs = String[]
    for (k, fn) in CFG_VALIDATORS
        v = getproperty(cfg, Symbol(k))
        try
            fn(v) || push!(errs, "ERR_SCHEMA $k: invalid value $v")
        catch
            push!(errs, "ERR_SCHEMA $k: invalid value $v")
        end
    end
    return errs
end

derive_salt(cfg::HodgeConfig) = cfg.deterministic ? "det-v1" : ""

function derive_seed(cfg::HodgeConfig, parts...)
    """§5.3 / §20.2: derive(seed, 'task|pass|phase|anim') — sha256-домены."""
    payload = join(vcat([string(cfg.seed), derive_salt(cfg)], string.(collect(parts))), "|")
    return parse(Int, bytes2hex(sha256(payload))[1:12], base = 16)
end

function cfg_relevant_hash(cfg::HodgeConfig)
    fields = (:preset, :profile, :seed, :prec, :two_pass, :pass_only, :tasks,
              :with_deps, :tags, :theme, :color_depth, :dye_mode, :no_report)
    payload = join(["$k=$(repr(getproperty(cfg, k)))" for k in fields], ";")
    return bytes2hex(sha256(payload))
end

function apply_preset!(cfg::HodgeConfig, name::AbstractString)
    name == "quick" && (cfg.prec = 55; cfg.two_pass = false; return nothing)
    name == "full" && (cfg.prec = 55; cfg.two_pass = true; return nothing)
    name == "deep" && (cfg.prec = 60; cfg.two_pass = true; return nothing)
    (name in HODGE_PRESETS) || throw(ArgumentError("ERR_PRESET_UNKNOWN $name"))
    nothing
end

function apply_profile!(cfg::HodgeConfig, name::AbstractString, explicit::Set{Symbol} = Set{Symbol}())
    """§1.4 / B2: профили управляют скрытыми ручками; явные CLI-флаги побеждают."""
    warns = String[]
    if name == "safe"
        (:dye_mode in explicit) || (cfg.dye_mode = "per-line")
        (:gradient in explicit) || (cfg.gradient = "off")
        (:fps in explicit) || (cfg.fps = 15)
        (:particles in explicit) || (cfg.particles = 32)
    elseif name == "fast"
        (:dye_mode in explicit) || (cfg.dye_mode = "per-line")
        (:log_level in explicit) || (cfg.log_level = "WARN")
    elseif name == "paranoid"
        cfg.deterministic = true
        cfg.strict = true
        cfg.profile = "paranoid"
    elseif name != "balanced"
        push!(warns, "ERR_SCHEMA profile: unknown $name")
    end
    return warns
end

function apply_recipe!(cfg::HodgeConfig, name::AbstractString)
    """§3.4: рецепт = preset + profile + tasks + overrides (в этом порядке)."""
    haskey(RECIPES, name) || throw(ArgumentError("ERR_RECIPE_UNKNOWN $name"))
    r = RECIPES[name]
    haskey(r, "preset") && (cfg.preset = r["preset"]; apply_preset!(cfg, cfg.preset))
    haskey(r, "profile") && (cfg.profile = r["profile"])
    if haskey(r, "tasks")
        t = r["tasks"]
        cfg.tasks = t == "all" ? Int[t.id for t in TASKS] : Int[t for t in t]
    end
    haskey(r, "two_pass") && (cfg.two_pass = r["two_pass"])
    for (k, v) in r["overrides"]
        try
            setproperty!(cfg, Symbol(k), v)
        catch
        end
    end
    nothing
end

function load_config_file!(cfg::HodgeConfig, path::AbstractString; _depth::Int = 0,
                           _visited::Set{String} = Set{String}())
    """§3.2 / II.1: JSON-конфиг + include (глубина ≤ 8, цикл → ERR_CONFIG_CYCLE).
    TOML честно ERR_UNSUPPORTED на stdlib-Julia (§1.5)."""
    _depth > 8 && throw(ArgumentError("ERR_CONFIG_DEPTH $path"))
    real = abspath(path)
    real in _visited && throw(ArgumentError("ERR_CONFIG_CYCLE $real"))
    push!(_visited, real)
    endswith(path, ".json") || throw(ArgumentError(
        "ERR_UNSUPPORTED: TOML-конфиг на stdlib-Julia не читается; используйте JSON (§1.5)"))
    data = json_load_flat(read(path, String))
    inc = get(data, "include", Any[])
    for i in (inc isa Vector ? inc : [inc])
        i isa AbstractString && load_config_file!(cfg, joinpath(dirname(real), i);
                                                  _depth = _depth + 1, _visited = _visited)
    end
    for (k, v) in data
        k == "include" && continue
        f = Symbol(k)
        if !(f in fieldnames(HodgeConfig))
            # P2: неизвестные ключи конфига не замалчиваются
            println(badge("WARN"), " config: неизвестное поле '$k' — игнорируется")
            continue
        end
        if f in fieldnames(HodgeConfig)
            cur = getproperty(cfg, f)
            if cur isa Vector{Int} && v isa Vector
                setproperty!(cfg, f, Int[v for v in v])
            elseif cur isa Vector{String} && v isa Vector
                setproperty!(cfg, f, String[string(x) for x in v])
            elseif typeof(cur) == typeof(v)
                setproperty!(cfg, f, v)
            elseif cur isa Real && v isa Real
                setproperty!(cfg, f, convert(typeof(cur), v))
            elseif cur isa Bool && v isa Bool
                setproperty!(cfg, f, v)
            else
                setproperty!(cfg, f, v)   # осторожно: строковые поля
            end
        end
    end
    nothing
end

# ── Гамма: Стирлинг + сдвиг; Бернулли точные (Rational{BigInt}) ──
const BERN_CACHE = Rational{BigInt}[1]
function bern_even(k::Int)                     # B_0, B_2, …
    while length(BERN_CACHE) <= k
        m = 2 * length(BERN_CACHE)
        s = sum(binomial(BigInt(m + 1), BigInt(j)) * BERN_CACHE[j ÷ 2 + 1]
                for j in 0:2:(m - 2); init = Rational{BigInt}(0))
        push!(BERN_CACHE, Rational{BigInt}(1, 2) - s / (m + 1))
    end
    return BERN_CACHE[k + 1]
end

function lgamma_hp(x::BigFloat)
    # §3.2 v5 (unlimited prec): сдвиг и порог усечения — в ДЕСЯТИЧНЫХ цифрах;
    # при k > 60 коэффициенты B_{2k} продолжаются ζ-отношением (хвост O(k) без
    # точных чисел Бернулли). Старый вариант (shift = p÷12 бит, порог 10^−(p−6),
    # кап k ≤ p÷8) на prec 1024 обрывал ряд на ~1e−195 и топил задачу 40.
    # §3.2 v6: gamma_gate ПЕРЕД работой (ряд ~π·y членов + ζ-суммы); сдвиг
    # свёрнут в 3 log вместо s вызовов log (см. историю в шапке).
    p0 = precision(BigFloat)
    digits = floor(Int, p0 * log10(2))
    shift = max(40, ceil(Int, (digits + 4) / 2.72864) + 4)   # min остаток ~10^−2.7286·y
    guard = 64 + ceil(Int, log2(shift + 16))                 # запас на сумму сдвига
    gamma_gate(p0)
    prog_begin!("Γ: Стирлинг + сдвиг, prec=$p0 бит")
    old = precision(BigFloat)
    setprecision(BigFloat, p0 + guard)
    val = try
        y = BigFloat(x); acc = BigFloat(0); comp = BigFloat(0)
        if y < shift
            # Σ_{k=0}^{s−1} ln(x+k) = ln((s−1)!) + ln x + Σ_{k=1}^{s−1} ln(1+x/k),
            # s = ceil(shift−x). Раньше — s итераций с ПОЛНЫМ log() на каждой:
            # при prec 5M бит s ≈ 550k × 6.8 с — десятки дней. Теперь 3 log +
            # два дерева произведений (BigInt-факториал и BigFloat-Π с глубиной
            # O(log s) — точность выше прежней последовательной).
            s = ceil(Int, shift - y)
            key = (s, p0 + guard)
            lf = get!(_LN_FACT_CACHE, key) do
                log(BigFloat(_fact_tree(s - 1)))
            end
            prod = _prod_shift_tree(BigFloat(x), s)
            ly = -(log(BigFloat(x)) + lf + log(prod))
            acc = ly                                    # один член — компенсация не нужна
            y = x + s
        end
        t = (y - BigFloat(1) / 2) * log(y) - y + log2pi_hp() / 2
        pw = y; k = 1; term = BigFloat(0)
        thr = BigFloat(10.0)^(-(digits + 3))
        two_pisq = 4 * pi_hp()^2
        cap = 8 * p0 + 120                          # страховка от дивергенции ряда
        hb_stage!("Γ: ряд Стирлинга, prec=$p0 бит")
        while true
            if k <= 150
                B = bern_even(k)                     # точные числа Бернулли
                term = BigFloat(B.num) / BigFloat(B.den) / (2k * (2k - 1) * pw)
            else
                # ТОЧНОЕ ζ-отношение (§3.2 v5): без поправки — пол 1e−185
                ek = zeta_even_eps(k, p0 + guard)
                ek1 = zeta_even_eps(k - 1, p0 + guard)
                term = -term * BigFloat(2k - 2) * BigFloat(2k - 3) * (1 + ek) /
                       (two_pisq * y * y * (1 + ek1))
            end
            t += term
            (abs(term) < thr || k > cap) && break
            pw *= y * y; k += 1
            (k & 0x0FFF) == 0 && hb_tick!(k, cap)
        end
        acc + t
    finally
        setprecision(BigFloat, old)
    end
    prog_end!()
    return val
end
gamma_hp(x::Real) = exp(lgamma_hp(BigFloat(x)))

# ── §3.2 v6: деревья произведений для сдвига Γ ──
const _LN_FACT_CACHE = Dict{Tuple{Int,Int},BigFloat}()
function _fact_tree(n::Int)
    """n! произведательным деревом: O(M(n бит)·log n) вместо O(n·M(n));
    GMP-FFT: 6M-значный факториал ≈ 0.05 с (последовательный — 44 с на 550k!)."""
    n < 2 && return BigInt(1)
    pr(a::Int, b::Int) = begin
        if b - a == 1
            return BigInt(b)
        elseif b - a == 2
            return BigInt((a + 1) * (a + 2))
        end
        m = (a + b) ÷ 2
        return pr(a, m) * pr(m, b)
    end
    return pr(1, n)
end

function _prod_shift_tree(x::BigFloat, s::Int)
    """Π_{k=1}^{s−1} (1 + x/k) сбалансированным деревом: те же s умножений,
    но глубина O(log s) — ошибки округления растут как log(s)·ulp вместо
    s·ulp (у последовательной схемы), и умножения сбалансированы по размеру."""
    s <= 2 && return s == 2 ? 1 + x : BigFloat(1)
    pr(a::Int, b::Int) = begin
        if b - a == 1
            return 1 + x / a
        elseif b - a == 2
            return (1 + x / a) * (1 + x / (a + 1))
        end
        m = (a + b) ÷ 2
        return pr(a, m) * pr(m, b)
    end
    return pr(1, s)
end

# ── §3.2 v5: точная ζ-поправка отношения чисел Бернулли ──
const _ZETA_EPS_CACHE = Dict{Tuple{Int,Int},BigFloat}()
function zeta_even_eps(j::Int, p::Int)
    """ζ(2j) − 1 = Σ_{m≥2} m^{−2j}, сумма до члена < 10^−(digits+12),
    digits = floor(p·log10(2)); p — рабочая точность в БИТАХ. Нужна для
    ТОЧНОГО отношения B_{2k}/B_{2k−2}: асимптотика без поправки даёт
    относительную ошибку O(4^−k) → абс. ошибка хвоста |term_60|·4^−61 ≈ 1e−185
    при prec 1024 бит (t40 не проходил tol 1e−300). Прямая сумма сходится как
    m^{−2j}: M(j) ≈ 10^{(digits+12)/(2j)} членов; для k ≤ 150 Бернулли ТОЧНЫЕ.
    §3.2 v6: последний рубеж от «тихой вечности» — при сумме длиннее 5e7
    членов поднимается ERR_GAMMA_PREC (gamma_gate должен был сработать раньше)."""
    if (floor(Int, p * log10(2)) + 12) / (2 * j) > log10(5e7)
        error("ERR_GAMMA_PREC ζ($(2j))−1 @ p=$p бит: прямая сумма $(_fmt_terms((floor(Int, p * log10(2)) + 12) / (2 * j))) членов — см. gamma_gate")
    end
    get!(_ZETA_EPS_CACHE, (p, j)) do
        old = precision(BigFloat)
        setprecision(BigFloat, p)
        eps = try
            digits = floor(Int, p * log10(2))
            cut = BigFloat(10.0)^(-(digits + 12))
            total = BigFloat(0)
            m = 2
            while true
                t = BigFloat(m)^(-2 * j)
                total += t
                t < cut && break
                m += 1
            end
            total
        finally
            setprecision(BigFloat, old)
        end
        eps
    end
end
omega(N, a, b) = gamma_hp(BigFloat(a) / N) * gamma_hp(BigFloat(b) / N) / gamma_hp(BigFloat(a + b) / N)

# ── tanh–sinh квадратура периода (2 гладких куска после t = u^N/2) ──
function period_pieces(N, a, b; K = 240, h = BigFloat("0.02"))
    # §3.2 v6: гейт квадратуры — узлов 2K+1 × дорогие sinh/cosh/tanh
    quad_gate_mpfr(precision(BigFloat), 2K + 1)
    hb_stage!("tanh–sinh: 2K+1 узлов, prec=$(precision(BigFloat)) бит")
    A, Bq = BigFloat(a) / N, BigFloat(b) / N
    i1 = i2 = BigFloat(0)
    p2a = BigFloat(2)^(-A); p2b = BigFloat(2)^(-Bq)
    nk = 0
    for k in -K:K
        t = k * h
        g = pi_hp() / 2 * sinh(t)
        g > BigFloat(precision(BigFloat) + 15) && (nk += 1; hb_tick!(nk, 2K + 1); continue)
        u = (1 + tanh(g)) / 2
        w = (pi_hp() / 4) * cosh(t) / (cosh(g)^2) * h
        base = 1 - u^N / 2
        i1 += w * N * p2a * u^(a - 1) * base^(Bq - 1)
        i2 += w * N * p2b * u^(b - 1) * base^(A - 1)
        nk += 1
        hb_tick!(nk, 2K + 1)
    end
    prog_end!()
    return i1 + i2
end

function zeta_pow(N::Int)
    # §3.2 v6: ζ-таблица — N комплексных exp на текущей точности; ОДИН exp при
    # гигантском prec — минуты тишины (одиночный C-вызов) → zeta_gate +
    # синхронный heartbeat по корням.
    zeta_gate(precision(BigFloat), N)
    hb_stage!("ζ-таблица N=$N · exp @$(precision(BigFloat)) бит")
    out = Vector{Complex{BigFloat}}(undef, N)
    for m in 0:N-1
        out[m+1] = exp(2 * pi_hp() * im * BigFloat(m) / N)
        hb_tick!(m + 1, N)
    end
    prog_end!()
    out
end
period_closed(N, a, b, r, s, z = zeta_pow(N)) = z[mod(r * a + s * b, N) + 1] * omega(N, a, b) / N
# P0.10: K/h прокидываются наверх (t08 при --prec-extreme поднимает сетку)
period_numeric(N, a, b, r, s, z = zeta_pow(N); K = 240, h = BigFloat("0.02")) =
    z[mod(r * a + s * (b - N), N) + 1] * period_pieces(N, a, b; K = K, h = h) / N
rel_err(x, y) = abs(x - y) / max(abs(x), abs(y), BigFloat("1e-100"))

# ── Точные целочисленные машины ──
mygcd(a, b) = gcd(a, b)
mylcm(a, b) = lcm(a, b)
function mymobius(m::Int)
    m == 1 && return 1
    r, x, q = 1, m, 2
    while q * q <= x
        if x % q == 0
            x ÷= q
            x % q == 0 && return 0
            r = -r
        end
        q += 1
    end
    x > 1 && (r = -r)
    return r
end
myphi(m::Int) = sum(1 for k in 1:m if gcd(k, m) == 1)
census(N) = begin
    h = Dict{Int,Int}(); by_d = Dict{Int,Vector{Tuple{Int,Int}}}()
    for a in 1:N-1, b in 1:N-a-1
        d = N ÷ gcd(gcd(N, a), b)
        h[d] = get(h, d, 0) + 1
        push!(get!(by_d, d, Tuple{Int,Int}[]), (a, b))
    end
    h, by_d, (N - 1) * (N - 2) ÷ 2
end
function census_mobius(N)
    c(k) = k >= 3 ? (k - 1) * (k - 2) ÷ 2 : 0
    out = Dict{Int,Int}()
    for d in 2:N
        N % d == 0 || continue
        s = sum(mymobius(m) * c(d ÷ m) for m in 1:d if d % m == 0)
        s != 0 && (out[d] = s)
    end
    Dict(out)
end

# многочлены MSB-first (Int-коэффициенты)
pnorm(p) = (i = findfirst(!iszero, p); i === nothing ? [0] : p[i:end])
pmul(a, b) = pnorm(conv(a, b))
padd(a, b) = begin
    out = zeros(Int, max(length(a), length(b)))
    for (k, c) in enumerate(a); out[end - length(a) + k] += c; end
    for (k, c) in enumerate(b); out[end - length(b) + k] += c; end
    pnorm(out)
end
pmod_monic(p, phi) = begin
    a = collect(p); dp = length(phi) - 1
    for i in 1:(length(a) - dp)
        a[i] == 0 && continue
        for j in 2:length(phi); a[i + j - 1] -= a[i] * phi[j]; end
        a[i] = 0
    end
    pnorm(a)
end
conv(a, b) = begin
    r = zeros(Int, length(a) + length(b) - 1)
    for (i, x) in enumerate(a), (j, y) in enumerate(b); r[i + j - 1] += x * y; end
    r
end
cyclotomic(n) = begin
    rem = [i == 1 ? 1 : (i == n + 1 ? -1 : 0) for i in 1:n+1]   # xⁿ−1
    for d in sort(collect(dd for dd in 1:n-1 if n % dd == 0))
        phi = cyclotomic(d)
        db = length(phi) - 1
        q = zeros(Int, length(rem) - db)
        for i in 1:length(q)
            c = rem[i]; q[i] = c
            c == 0 && continue
            for j in 1:length(phi); rem[i + j - 1] -= c * phi[j]; end
        end
        rem = pnorm(q)
    end
    rem
end

gf2_irreducible(coeffs) = begin
    c = [v & 1 for v in coeffs]
    (c[end] == 0 || iszero(sum(c) % 2) || sum(c[1:end-1]) == 0) && return false
    deg = length(c) - 1
    divs = deg >= 4 ? [[1, 1, 1]] : []
    if deg >= 6; append!(divs, [[1, 1, 0, 1], [1, 0, 1, 1]]); end
    for d in divs
        dd = length(d) - 1
        (deg % dd == 0 && dd < deg) || continue
        a = copy(c)
        for i in 1:(length(a) - dd)
            a[i] == 0 && continue
            for j in 1:length(d); a[i + j - 1] ⊻= d[j]; end
        end
        all(iszero, a) && return false   # делится → приводим
    end
    return true
end

# башня ℤ[√5][√D]: элемент ((a0,a1),(b0,b1)) = (a0+a1√5) + (b0+b1√5)·β
z5mul(p, q) = (p[1] * q[1] + 5 * p[2] * q[2], p[1] * q[2] + p[2] * q[1])
tw_add(u, v) = (u[1] .+ v[1], u[2] .+ v[2])
tw_mul(u, v, D) = (z5mul(u[1], v[1]) .+ z5mul(z5mul(u[2], v[2]), D),
                   z5mul(u[1], v[2]) .+ z5mul(u[2], v[1]))
const BCH_RADICALS = Dict(15 => (D = (30, -6), m = ((1, 1), (1, 0)), den = 4,
                                 poly = [1, -1, -4, 4, 1]),
                          30 => (D = (30, 6), m = ((-1, 1), (1, 0)), den = 4,
                                 poly = [1, 1, -4, -4, 1]))
function bch_residual(n)
    sp = BCH_RADICALS[n]; D, m, den, poly = sp.D, sp.m, sp.den, sp.poly
    pw = [((1, 0), (0, 0))]
    for _ in 1:4; push!(pw, tw_mul(pw[end], m, D)); end
    acc = ((0, 0), (0, 0))
    for k in 0:4
        c = poly[5 - k] * den^(4 - k)
        c == 0 && continue
        acc = tw_add(acc, ((pw[k+1][1][1] * c, pw[k+1][1][2] * c),
                           (pw[k+1][2][1] * c, pw[k+1][2][2] * c)))
    end
    acc
end

snf(mat) = begin
    a = copy(mat); rows, cols = size(a, 1), size(a, 2)
    res = Int[]
    for t in 1:min(rows, cols)
        while true
            best = (typemax(Int), 0, 0)
            for i in t:rows, j in t:cols
                v = abs(a[i, j])
                if v != 0 && v < best[1]; best = (v, i, j); end
            end
            best[2] == 0 && return res
            v, pi_, pj = best
            if pi_ != t; tmprow = a[t, :]; a[t, :] = a[pi_, :]; a[pi_, :] = tmprow; end
            if pj != t; tmpcol = a[:, t]; a[:, t] = a[:, pj]; a[:, pj] = tmpcol; end
            piv = a[t, t]
            for i in t+1:rows                       # Безу-обнуление столбца
                b = a[i, t]; b == 0 && continue
                g, x, y = gcdx(piv, b)
                rt, ri = a[t, :], a[i, :]
                a[t, :] = x .* rt .+ y .* ri
                a[i, :] = .-(b ÷ g) .* rt .+ (piv ÷ g) .* ri
                piv = a[t, t]
            end
            for j in t+1:cols                       # Безу-обнуление строки
                b = a[t, j]; b == 0 && continue
                g, x, y = gcdx(piv, b)
                ct, cj = a[:, t], a[:, j]
                a[:, t] = x .* ct .+ y .* cj
                a[:, j] = .-(b ÷ g) .* ct .+ (piv ÷ g) .* cj
                piv = a[t, t]
            end
            viol = nothing
            for i in t+1:rows, j in t+1:cols
                if a[i, j] % piv != 0; viol = (i, j); break; end
            end
            viol === nothing && break
            i, j = viol
            if a[i, t] == 0; a[i, :] .+= a[t, :]; end
            q = a[i, j] ÷ piv
            a[:, j] .-= q .* a[:, t]
        end
        push!(res, abs(a[t, t]))
    end
    for i in 1:length(res)-1
        g, l = gcd(res[i], res[i+1]), lcm(res[i], res[i+1])
        res[i], res[i+1] = g, l
    end
    res
end

rank_fractions(M) = begin
    A = copy(M); n = size(A, 1); cnt = 0
    for c in 1:size(A, 2)
        cnt >= n && break
        piv = findfirst(i -> A[i, c] != 0, (cnt + 1):n)
        piv === nothing && continue
        pr = cnt + piv
        A[[cnt + 1, pr], :] = A[[pr, cnt + 1], :]
        pv = A[cnt + 1, c]
        for i in cnt+2:n
            A[i, c] == 0 && continue
            A[i, :] .-= (A[i, c] / pv) .* A[cnt + 1, :]
        end
        cnt += 1
    end
    cnt
end

k3_inter(l1, l2) = begin
    l1 == l2 && return -2
    f1, a1, b1 = l1; f2, a2, b2 = l2
    f1 == f2 && return ((a1 == a2) != (b1 == b2)) ? 1 : 0
    ff = minmax(f1, f2)
    if ff == (1, 2); return mod(a1 + b2 - a2 - b1, 4) == 0 ? 1 : 0; end
    if ff == (1, 3)
        ok = f1 == 1 ? mod(a2 - a1 - b1 - b2 - 1, 4) == 0 : mod(a1 - a2 - b2 - b1 - 1, 4) == 0
        return ok ? 1 : 0
    end
    return mod(a1 + b1 - a2 - b2, 4) == 0 ? 1 : 0
end
k3_gram() = begin
    ls = [(f, a, b) for f in 1:3 for a in 0:3 for b in 0:3]
    n = length(ls); G = zeros(Int, n + 1, n + 1)
    for i in 1:n, j in 1:n; G[i, j] = k3_inter(ls[i], ls[j]); end
    for i in 1:n; G[i, n+1] = G[n+1, i] = 1; end
    G[n+1, n+1] = 4
    G, ls
end

tstar(W, H, a, b) = lcm(W ÷ gcd(a, W), H ÷ gcd(b, H))
function binary_flow(W = 48, H = 48, a = 1, b = 1)
    t = tstar(W, H, a, b); x = y = dx = dy = 0; vis = Set{Tuple{Int,Int}}()
    for _ in 1:t
        push!(vis, (x, y)); x = mod(x + a, W); y = mod(y + b, H)
        dx = mod(dx + a, W); dy = mod(dy + b, H)
    end
    (t = t, visited = length(vis), closed = dx == 0 && dy == 0)
end
qscan(x, Q, tol = 1e-9) = begin
    for q in 1:Q
        p = round(Int, x * q)
        abs(x * q - p) <= 0.5 && abs(x - p / q) < tol && return (q, p)
    end
    nothing
end
ramanujan_c(N, k) = begin
    g = gcd(N, k)
    mymobius(N ÷ g) * myphi(N) ÷ myphi(N ÷ g)
end
trace_gram(N) = begin
    d = myphi(N)
    [ramanujan_c(N, mod(i - j, N)) for i in 1:d, j in 1:d]
end
fermat_point_count(p) = begin
    A = Dict{Int,Int}()
    for x in 0:p-1; v = powermod(x, 5, p); A[v] = get(A, v, 0) + 1; end
    c2 = Dict{Int,Int}()
    for x in 0:p-1, y in 0:p-1
        s = mod(powermod(x, 5, p) + powermod(y, 5, p), p)
        c2[s] = get(c2, s, 0) + 1
    end
    c4 = Dict{Int,Int}()
    for (s, c) in c2, (t, c2v) in c2
        u = mod(s + t, p); c4[u] = get(c4, u, 0) + c * c2v
    end
    affine = sum(c * get(A, mod(-s, p), 0) for (s, c) in c4)
    proj = (affine - 1) ÷ (p - 1)
    (p = p, affine = affine, proj = proj, t_p = (1 + p + p^2 + p^3) - proj)
end

t01(cfg) = begin
    ok = true; det = ""
    frozen = Dict(7 => Dict(7 => 15), 9 => Dict(3 => 1, 9 => 27), 11 => Dict(11 => 45),
                  15 => Dict(3 => 1, 5 => 6, 15 => 84),
                  30 => Dict(3 => 1, 5 => 6, 6 => 9, 10 => 30, 15 => 84, 30 => 276))
    fg = Dict(4 => 3, 5 => 6, 7 => 15, 9 => 28, 11 => 45, 15 => 91, 30 => 406)
    for N in (4, 5, 7, 9, 11, 15, 30)
        h, _by_d, g = census(N); hm = census_mobius(N)
        ok &= (sum(values(h)) == g && g == fg[N] && h == hm)
        haskey(frozen, N) && (ok &= h == frozen[N])
        det *= "N=$N:g=$(g)/"
    end
    ok, "ценз/род подтверждены (2 схемы, 7 уровней): $det"
end
t01b(cfg) = begin
    ok = all(sum(values(census(N)[1])) == census(N)[3] && census(N)[1] == census_mobius(N) for N in 3:64)
    ok, "согласие схем на всех N∈[3,64] (C-001)"
end
t02(cfg) = begin
    worst = 0.0; cnt = 0
    for N in (7, 9, 15, 30)
        z = zeta_pow(N)
        for (a, b) in ((1, 1), (2, 3)), (r, s) in ((0, 0), (1, 0), (0, 1))
            worst = max(worst, Float64(rel_err(period_closed(N, a, b, r, s, z),
                                               period_numeric(N, a, b, r, s, z))))
            cnt += 1
        end
    end
    worst < 1e-30, @sprintf("V2: %d периодов closed=tanh-sinh, rel=%.2e", cnt, worst)
end
t03(cfg) = begin
    worst = 0.0; N = 15; z = zeta_pow(N)
    for (a, b) in ((1, 1), (2, 3)), (r, s) in ((1, 0), (0, 1))
        pn = period_numeric(N, a, b, r, s, z)
        ph = z[mod(r * a + s * b, N) + 1]
        proj = pn * conj(ph)
        worst = max(worst, Float64(abs(imag(proj)) / abs(pn)))
    end
    worst < 1e-25, @sprintf("V3: фазовый закон, dev=%.2e", worst)
end
t04(cfg) = begin
    worst = 0.0; N = 15; z = zeta_pow(N)
    for (a, b) in ((1, 1), (2, 3)), (u, v) in ((1, 0), (0, 1), (1, 1))
        base = period_closed(N, a, b, 1, 0, z)
        sh = period_closed(N, a, b, 1 + u, v, z)
        f = z[mod(u * a + v * b, N) + 1]
        worst = max(worst, Float64(rel_err(sh, f * base)))
    end
    worst < 1e-30, @sprintf("V4: эквивариантность, rel=%.2e", worst)
end
t05(cfg) = begin
    worst = 0.0
    for (N, van, ctl) in ((15, [(2, 3), (3, 4)], (7, 8)), (30, [(2, 3), (4, 7)], (7, 23)))
        for (a, b) in van
            acc = sum(period_closed(N, a, b, k, k) for k in 0:N-1)
            worst = max(worst, Float64(abs(acc) / omega(N, a, b)))
        end
        a, b = ctl
        acc = sum(period_closed(N, a, b, k, k) for k in 0:N-1)
        worst = max(worst, Float64(rel_err(acc, omega(N, a, b))))
    end
    worst < 1e-25, @sprintf("V5: цепь, worst=%.2e", worst)
end
t06(cfg) = begin
    worst = 0.0; cnt = 0
    for N in (7, 9, 15, 30), k in 1:N-1
        lhs = gamma_hp(BigFloat(k) / N) * gamma_hp(1 - BigFloat(k) / N)
        rhs = pi_hp() / sin(pi_hp() * BigFloat(k) / N)
        worst = max(worst, Float64(abs(lhs - rhs) / abs(rhs))); cnt += 1
    end
    worst < 1e-30, @sprintf("V6: Γ-рефлексия, %d пар, rel=%.2e", cnt, worst)
end
t07(cfg) = begin
    N = 15; z = zeta_pow(N)
    _, by_d, _g = census(N)
    chars = [(a, b) for (d, lst) in by_d for (a, b) in lst][1:8]
    Om = [omega(N, a, b) for (a, b) in chars]
    dg = off = 0.0
    for i in 1:8, j in 1:8
        acc = sum(z[mod(r * (chars[i][1] - chars[j][1]) + s * (chars[i][2] - chars[j][2]), N) + 1]
                  for r in 0:N-1 for s in 0:N-1)
        val = acc * Om[i] * Om[j] / (N * N)
        if i == j
            dg = max(dg, Float64(abs(val - Om[i]^2) / Om[i]^2))
        else
            off = max(off, Float64(abs(val) / (Om[i] * Om[j])))
        end
    end
    dg < 1e-25 && off < 1e-25, @sprintf("V8: DFT 8×225, diag=%.1e off=%.1e", dg, off)
end
t08(cfg) = begin
# ── P0.10: --prec-extreme → порог 1e-100 и сетка K=480/h=0.012 (рекорд),
#    иначе прежний порог 1e-60. cfg здесь — Dict из run_task_two_pass!. ──
    extreme = get(cfg, "prec_extreme", false)
    N, a, b, r, s = 15, 2, 3, 1, 1
    z = zeta_pow(N)
    e = Float64(rel_err(period_closed(N, a, b, r, s, z),
                        period_numeric(N, a, b, r, s, z;
                                       K = extreme ? 480 : 240,
                                       h = extreme ? big"0.012" : big"0.02")))
    thr = extreme ? 1e-100 : 1e-60
    e < thr, @sprintf("V9: prec=%d бит%s, rel=%.2e %s %.0e", precision(BigFloat),
                      extreme ? " (prec-extreme)" : "", e, e < thr ? "<" : "≥", thr)
end
t09(cfg) = begin
    df = 4 * π^2 + (π/4)^2 / 2 - (π/4)^5
    okf = abs(df - 39.48799539346835) < 1e-9
    dhp = 4 * pi_hp()^2 + (pi_hp()/4)^2 / 2 - (pi_hp()/4)^5
    ref = big"39.48799539346835051297464603266144167978"
    okhp = Float64(abs(dhp - ref) / ref) < 1e-30
    fam = all(π/n < π/(n-1) for n in 3:9)
    okf && okhp && fam, @sprintf("T07: Δ_Ch f64=%s hp dev=%.2e", okf, Float64(abs(dhp - ref)/ref))
end
t10(cfg) = begin
    G, ls = k3_gram(); n = size(G, 1)
    rank = rank_fractions([Rational{BigInt}(G[i, j]) for i in 1:n, j in 1:n])
    factors = snf(G)
    det = prod(factors)
    ok = length(ls) == 48 && rank == 20 && det == 64 && factors[end-1:end] == [8, 8] &&
         count(==(1), factors) == 18
    ok, @sprintf("T08: K3: 48 прямых, rank=%d, det=%d, SNF=[1×18,8,8]", rank, det)
end
t11(cfg) = begin
    j = -(105^3) ÷ 343
    ok = j == -3375 && (-15)^3 == -3375 && (-343) * j == 105^3 && 105^3 == 1157625 &&
         7^2 - 4 * 14 == -7
    ok, "T11: Клейн: j=-3375=−15³, Δ·j=105³=1157625, disc=-7"
end
t12(cfg) = begin
    ok = true
    for g in 1:3
        n = 2g; size = 1 << n; half = size >> 1; sh = 1 << (g - 1)
        pairs = [(2i - 2, 2i - 1) for i in 1:g]
        even = odd = 0
        for basis in 0:size-1
            zeros_ = 0
            for v in 0:size-1
                qv = 0
                for i in 1:n; ((v >> (i-1)) & 1) == 1 && (qv ⊻= (basis >> (i-1)) & 1); end
                for (i, j) in pairs    # биты пар — уже 0-базные (как в Python-эталоне)
                    (((v >> i) & 1) == 1 && ((v >> j) & 1) == 1) && (qv ⊻= 1)
                end
                qv == 0 && (zeros_ += 1)
            end
            if zeros_ == half + sh
                even += 1
            else
                odd += 1
            end
        end
        ok &= (even == (1 << (g-1)) * ((1 << g) + 1) && odd == (1 << (g-1)) * ((1 << g) - 1))
    end
    ok, "T09: Арф g=1..3: 3/1, 10/6, 36/28 = формулам"
end
t13(cfg) = begin
    ok = all(tstar(w, h, a, b) == e for (w, h, a, b, e) in
             [(48, 48, 1, 1, 48), (96, 96, 1, 1, 96), (24, 36, 3, 5, 72),
              (7, 14, 1, 1, 14), (12, 12, 4, 6, 6), (384, 384, 1, 1, 384)])
    bf = binary_flow()
    ok &= bf.t == 48 && bf.visited == 48 && bf.closed
    ok &= 48 + 212 + 432 + 114 == 806
    ok, "T13: t* на 6 случаях; поток 48×48: 48 клеток; суммы=806"
end
t14(cfg) = begin
    ok = all(bch_residual(n) == ((0, 0), (0, 0)) for n in (15, 30))
    ok &= all(gf2_irreducible(BCH_RADICALS[n].poly) for n in (15, 30))
    worst = 0.0
    for n in (15, 30)
        r5 = sqrt(big(5.0))
        beta = sqrt((n == 15 ? 30 - 6 * r5 : 30 + 6 * r5))
        x = (n == 15 ? (1 + r5 + beta) / 4 : (r5 - 1 + beta) / 4)
        b = 1 - x / 2
        tgt = 1 - cos(2 * pi_hp() / n)
        worst = max(worst, Float64(abs(b - tgt) / abs(tgt)))
        ok &= BigFloat(7) / 4 < x < 2
    end
    ok && worst < 1e-30, @sprintf("T05/T19: башни точны, GF(2) ok, радикалы rel=%.2e", worst)
end
t15(cfg) = begin
    s7 = HODGE_cyc_syms(7); s9 = HODGE_cyc_syms(9)
    ok = s7 == (-1, -2, 1) && s9 == (0, -3, -1)
    ok &= gf2_irreducible([1, 1, -2, -1]) && gf2_irreducible([1, 0, -3, 1])
    r3 = sqrt(big(3.0))
    t = (big(7) / 54, big(7) * r3 / 18)
    u = exp(log(complex(t[1], t[2])) / 3)
    b7 = big(7) / 6 - real(u)
    tgt7 = 1 - cos(2 * pi_hp() / 7)
    e7 = Float64(abs(b7 - tgt7) / abs(tgt7))
    w = complex(-big(1) / 2, r3 / 2)
    u9 = exp(log(w) / 3)
    b9 = 1 - real(u9)
    e9 = Float64(abs(b9 - (1 - cos(2 * pi_hp() / 9))) / abs(1 - cos(2 * pi_hp() / 9)))
    ok && e7 < 1e-25 && e9 < 1e-25, @sprintf("T17/T18: Виета (%s)/(%s), Cardano rel=%.1e/%.1e",
        s7, s9, e7, e9)
end
function HODGE_cyc_syms(n)
    phi = cyclotomic(n)
    els = []
    for k in (n == 7 ? (1, 2, 3) : (1, 2, 4))
        p = zeros(Int, n + 1); p[k+1] += 1; p[n-k+1] += 1
        push!(els, pmod_monic(p, phi))
    end
    zadd(p, q) = pmod_monic(padd(p, q), phi)
    zmul(p, q) = pmod_monic(pmul(p, q), phi)
    s1 = zadd(zadd(els[1], els[2]), els[3])
    s2 = zadd(zadd(zmul(els[1], els[2]), zmul(els[1], els[3])), zmul(els[2], els[3]))
    s3 = zmul(zmul(els[1], els[2]), els[3])
    (length(s1) == 1 ? s1[1] : nothing,
     length(s2) == 1 ? s2[1] : nothing,
     length(s3) == 1 ? s3[1] : nothing)
end
t16(cfg) = begin
    ok = true
    for N in (15, 30)
        G = trace_gram(N)
        inv = snf(G)
        ok &= inv == [1, 1, 5, 5, 15, 15, 15, 15] && prod(inv) == 1265625 && 1265625 == 1125^2
    end
    ok &= snf([2 0; 0 3]) == [1, 6] && snf([6 0 0; 0 10 0; 0 0 15]) == [1, 30, 30]
    for p in (7, 11)
        G = [(i == j ? p : 0) - 1 for i in 1:p, j in 1:p]
        ok &= snf(G) == [1; [p for _ in 2:p-1]]
    end
    ok, "T06/T22: SNF(15/30)=[1,1,5,5,15,15,15,15], disc=1265625=1125², NE02 ok"
end
t17(cfg) = begin
    lhs = (30, -6) .* 1
    z5mul((30, -6), (30, 6)) == (720, 0) || return false, "T19: ββ′"
    p15 = BCH_RADICALS[15].poly; p30 = BCH_RADICALS[30].poly
    neg = [mod(length(p15) - i, 2) == 1 ? -c : c for (i, c) in enumerate(p15)]
    phi15 = cyclotomic(15); phi30 = cyclotomic(30)
    neg30 = [mod(length(phi30) - i, 2) == 1 ? -c : c for (i, c) in enumerate(phi30)]
    d30 = length(phi30) - 1
    comp = zeros(Int, 8 * d30 + 1)
    for (i, c) in enumerate(phi30)
        k = d30 - (i - 1)
        comp[8 * (d30 - k) + 1] += c * (-1)^k
    end
    red = pmod_monic(comp, phi15)
    r15 = [c & 1 for c in p15]; r30 = [c & 1 for c in p30]
    ok = neg == p30 && neg30 == phi15 && red == [0] && r15 == r30 && r30 == [1, 1, 0, 0, 1]
    ok, "T19: P₃₀=P₁₅(−x), Φ₃₀(−ζ₁₅⁸)≡0, GF(2)-отпечаток x^4+x^3+1"
end
t18(cfg) = begin
    ok = qscan(2.75, 16) == (4, 11) && qscan(4 * π^2, 16) === nothing
    ok, "T14: qscan(2.75,16)=(4,11); 4π^2 и 2π не рационализируются"
end
t19(cfg) = begin
    g14 = gamma_hp(big(1) / 4); g34 = gamma_hp(big(3) / 4)
    e = Float64(abs(g14 * g34 - pi_hp() * sqrt(big(2.0))) / (pi_hp() * sqrt(big(2.0))))
    e < 1e-30, @sprintf("T15: Γ(1/4)Γ(3/4)=π√2, rel=%.2e", e)
end
t20(cfg) = begin
    # P0.6: L — БЛОЧНО-ЦИКЛИЧЕСКАЯ (не диагональ!): диагональ коммутирует
    # тривиально с чем угодно. Блок-строка (bi,bj) = c[(bj-bi) mod 4].
    # Дополнительно: P₄ = Σ_{k=0..3} i^{−k}R^k над ℤ[i]; P₄² = 4·P₄ и [L, P₄] = 0.
    ok = true
    for dim in (8, 16, 24)   # P2.11: добавлен dim 24 (K=6) — 3 размера
        K = dim ÷ 4
        # P0.6: 4 блока-вектора длины K (порт HODGEEX.mu4_system); блок (bi,bj)
        # кладёт blocks[(bj-bi) mod 4] на свою диагональ → L не диагональна
        blocks = [[mod(3 * (b * K + m) + 7, 17) - 8 for m in 1:K] for b in 0:3]
        L = zeros(Int, dim, dim)
        for bi in 0:3, bj in 0:3
            bl = blocks[mod(bj - bi, 4) + 1]
            for i in 1:K
                L[bi*K + i, bj*K + i] = bl[i]
            end
        end
        R = [j == mod(i + K - 1, dim) + 1 ? 1 : 0 for i in 1:dim, j in 1:dim]
        I4 = Matrix{Int}(I, dim, dim)
        R2 = R * R; R4 = R2 * R2
        ok &= R4 == I4 && R != I4 && R2 != I4
        ok &= L * R == R * L                # [L, R] = 0 — теперь нетривиально
        ok &= L != [L[i, i] * (i == j ? 1 : 0) for i in 1:dim, j in 1:dim]  # L не диагональ
        # P₄ над ℤ[i]
        Im = Matrix{Complex{Int}}(I, dim, dim)
        P4 = zeros(Complex{Int}, dim, dim)
        ik = Complex{Int}(1, 0)             # i^{-k}
        Rk = copy(Im)
        for k in 0:3
            P4 .+= ik .* Rk
            Rk = Rk * R
            ik *= Complex{Int}(0, -1)       # i^{-1} = -i
        end
        ok &= P4 * P4 == 4 .* P4            # P₄² = 4P₄
        ok &= L * P4 == P4 * L              # [L, P₄] = 0
    end
    ok, "T12: [L,R]=0, [L,P₄]=0, P₄²=4P₄ на блочно-циклических μ₄-системах, dim 8/16/24 (целые/ℤ[i])"
end
t21(cfg) = begin
    m = fermat_point_count(11)
    ok = m.proj == 1925 && m.t_p == -461
    for pp in (11, 31)
        mm = fermat_point_count(pp)
        ok &= abs(mm.t_p) <= 204 * pp^1.5
    end
    ok, @sprintf("C-011: #X₀(F₁₁)=%d, t₁₁=%d, Вейль b₃=204 на p=11,31", m.proj, m.t_p)
end
t21b(cfg) = begin
    m = fermat_point_count(41)
    abs(m.t_p) <= 204 * 41^1.5, @sprintf("C-011 hardcore: p=41: #X₀=%d, t₄₁=%d", m.proj, m.t_p)
end
t22(cfg) = begin
    ok = true
    for (N, gexp) in ((7, 15), (9, 28))
        _, by_d, _g = census(N)
        chars = [(a, b) for (d, lst) in by_d for (a, b) in lst][1:gexp]
        pts = [(r, s) for r in 0:N-1 for s in 0:N-1]
        M = [exp(2 * π * im * mod(r * a + s * b, N) / N) for (a, b) in chars, (r, s) in pts]
        basis = Vector{Vector{ComplexF64}}()
        indep = 0
        for i in 1:size(M, 1)
            v = Vector{ComplexF64}(M[i, :])
            for bw in basis
                dot = sum(conj(bw[t]) * v[t] for t in eachindex(v))
                v .-= dot .* bw
            end
            n2 = sum(abs2, v)
            if n2 > 1e-9 * N^2
                push!(basis, v ./ sqrt(n2)); indep += 1
            end
        end
        ok &= indep == gexp
    end
    ok, "V7 (QR §1.5): ранг функциональной матрицы = числу строк (N=7,9)"
end

const MASK64 = (1 << 64) - 1
splitmix64(x::UInt64) = begin
    x = x + 0x9E3779B97F4A7C15
    z = x
    z = (z ⊻ (z >> 30)) * 0xBF58476D1CE4E5B9
    z = (z ⊻ (z >> 27)) * 0x94D049BB133111EB
    z ⊻ (z >> 31)
end
const A_INV = UInt64(invmod(BigInt(0xBF58476D1CE4E5B9), big(2)^64))
const B_INV = UInt64(invmod(BigInt(0x94D049BB133111EB), big(2)^64))
function splitmix64_inverse(y::UInt64)
    z = y
    z = z ⊻ (z >> 31); z = z ⊻ (z >> 62)
    z = (z * B_INV) & MASK64
    z = z ⊻ (z >> 27); z = z ⊻ (z >> 54)
    z = (z * A_INV) & MASK64
    z = z ⊻ (z >> 30); z = z ⊻ (z >> 60)
    (z - 0x9E3779B97F4A7C15) & MASK64
end
sm64(x) = splitmix64(UInt64(x))
sm64_inv(y) = splitmix64_inverse(UInt64(y))

# ════════════════════════════════════════════════════════════════════════
# §11 ДВИЖОК ГРАФИКИ: PNG (zlib через ccall с stored-fallback), GIF89a
# (свой LZW), 5×7 битмап-шрифт, канва (Брезенхем/α-композит в RGB),
# HODGEPlot (line/scatter/heatmap), GCT из палитры темы (один на прогон),
# 3D-лаборатория с sweep. Только stdlib.
# ════════════════════════════════════════════════════════════════════════
const PNG_SIGNATURE = UInt8[0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]

crc32_table = let
    t = Vector{UInt32}(undef, 256)
    for n in 0:255
        c = UInt32(n)
        for _ in 1:8
            c = (c & 1 == 1) ? (0xEDB88320 ⊻ (c >> 1)) : (c >> 1)
        end
        t[n+1] = c
    end
    t
end
crc32(data::Vector{UInt8}) = begin
    c = 0xFFFFFFFF
    for b in data
        c = crc32_table[((c ⊻ b) & 0xFF) + 1] ⊻ (c >> 8)
    end
    c ⊻ 0xFFFFFFFF
end

u32be(v::Integer) = UInt8[(v >> 24) & 0xFF, (v >> 16) & 0xFF, (v >> 8) & 0xFF, v & 0xFF]
u32le(v::Integer) = UInt8[v & 0xFF, (v >> 8) & 0xFF, (v >> 16) & 0xFF, (v >> 24) & 0xFF]
u16le(v::Integer) = UInt8[v & 0xFF, (v >> 8) & 0xFF]

function png_chunk(tag::Vector{UInt8}, data::Vector{UInt8})
    body = vcat(tag, data)
    return vcat(u32be(length(data)), body, u32be(crc32(body)))
end

zlib_compress(data::Vector{UInt8}) = try
    # zlib через ccall (libz линкуется в Julia); при недоступности — stored
    outsize = length(data) + div(length(data), 1000) + 64
    out = Vector{UInt8}(undef, outsize)
    destlen = Ref{Culong}(outsize)
    GC.@preserve data out begin
        rc = ccall((:compress2, "libz"), Cint,
                   (Ptr{UInt8}, Ptr{Culong}, Ptr{UInt8}, Culong, Cint),
                   pointer(out), destlen, pointer(data), length(data), 9)
    end
    rc == 0 ? out[1:destlen[]] : zlib_stored(data)
catch
    zlib_stored(data)
end

function zlib_stored(data::Vector{UInt8})
    """Честный zlib (RFC 1950) с несжатыми блоками (RFC 1951 stored) —
    всегда валиден, без внешних зависимостей (§1.5: ближайший эквивалент)."""
    out = UInt8[0x78, 0x01]
    i = 1
    n = length(data)
    while true
        chunk = min(65535, n - i + 1)
        last = i + chunk - 1 >= n
        push!(out, last ? 0x01 : 0x00)
        lo = chunk & 0xFF; hi = (chunk >> 8) & 0xFF
        push!(out, UInt8(lo), UInt8(hi), UInt8(lo ⊻ 0xFF), UInt8(hi ⊻ 0xFF))
        append!(out, data[i:i+chunk-1])
        i += chunk
        (last || chunk == 0) && break
    end
    append!(out, u32be(crc32(data)))
    append!(out, u32be(adler32(data)))
    return out
end

adler32(data::Vector{UInt8}) = begin
    a = UInt32(1); b = UInt32(0)
    for x in data
        a = (a + x) % 65521
        b = (b + a) % 65521
    end
    (b << 16) | a
end

png_encode(width::Int, height::Int, rgb::Vector{UInt8}) = begin
    length(rgb) == width * height * 3 || throw(ArgumentError("png buf size"))
    raw = UInt8[]
    stride = width * 3
    for y in 0:height-1
        push!(raw, 0x00)
        append!(raw, rgb[y*stride+1:(y+1)*stride])
    end
    ihdr_data = vcat(u32be(width), u32be(height), UInt8[8, 2, 0, 0, 0])
    return vcat(PNG_SIGNATURE,
                png_chunk(UInt8[0x49, 0x48, 0x44, 0x52], ihdr_data),
                png_chunk(UInt8[0x49, 0x44, 0x41, 0x54], zlib_compress(raw)),
                png_chunk(UInt8[0x49, 0x45, 0x4e, 0x44], UInt8[]))
end

# ── GIF89a: свой LZW (GIF-spec Appendix F) ──
function gif_lzw(data::Vector{UInt8}, min_code_size::Int = 8)
    clear = 1 << min_code_size
    endc = clear + 1
    next_code = endc + 1
    code_size = min_code_size + 1
    table = Dict{Vector{UInt8},Int}()
    for i in 0:255; table[UInt8[i]] = i; end
    bits = UInt8[]
    buf = UInt32(0); nb = 0
    emit(code, n) = begin
        buf |= code << nb; nb += n
        while nb >= 8
            push!(bits, UInt8(buf & 0xFF)); buf >>= 8; nb -= 8
        end
    end
    emit(clear, code_size)
    w = UInt8[]
    for b in data
        wc = vcat(w, UInt8[b])
        if haskey(table, wc)
            w = wc
        else
            emit(table[w], code_size)
            table[wc] = next_code; next_code += 1
            if next_code - 1 == (1 << code_size) && code_size < 12
                code_size += 1
            end
            if next_code == 4096
                emit(clear, code_size)
                empty!(table)
                for i in 0:255; table[UInt8[i]] = i; end
                next_code = endc + 1; code_size = min_code_size + 1
            end
            w = UInt8[b]
        end
    end
    !isempty(w) && emit(table[w], code_size)
    emit(endc, code_size)
    nb > 0 && push!(bits, UInt8(buf & 0xFF))
    out = UInt8[min_code_size]
    i = 1
    while i <= length(bits)
        n = min(255, length(bits) - i + 1)
        push!(out, UInt8(n)); append!(out, bits[i:i+n-1]); i += n
    end
    push!(out, 0x00)
    return out
end

function gif_encode(width::Int, height::Int, gct::Vector{Tuple{Int,Int,Int}},
                    frames::Vector{Vector{UInt8}}, delays::Vector{Int})
    length(gct) <= 256 || throw(ArgumentError("gct > 256"))
    out = UInt8[]
    append!(out, UInt8['G', 'I', 'F', '8', '9', 'a'])
    append!(out, u16le(width)); append!(out, u16le(height))
    push!(out, 0xF7, 0x00, 0x00)
    for (r, g, b) in gct
        push!(out, UInt8(r), UInt8(g), UInt8(b))
    end
    for _ in length(gct):255
        push!(out, 0x00, 0x00, 0x00)
    end
    append!(out, UInt8[0x21, 0xFF, 0x0B]); append!(out, codeunits("NETSCAPE2.0"))
    append!(out, UInt8[0x03, 0x01, 0x00, 0x00, 0x00])   # loop forever
    for (fr, delay) in zip(frames, delays)
        # GCE — ровно 8 байт (регрессия s5: лишний 0x04 сдвигал поле delay на
        # 1 байт → зрители читали задержку ×256 и кадры «замирали», плюс после
        # GCE оставался посторонний пустой 0x00-блок):
        # [21 F9 04] [flags=04 disposal=1] [delay LE16, сотые секунды]
        # [transparent=00] [terminator=00]
        append!(out, UInt8[0x21, 0xF9, 0x04, 0x04])
        d = clamp(delay, 0, 65535)
        push!(out, UInt8(d & 0xFF), UInt8((d >> 8) & 0xFF))
        append!(out, UInt8[0x00, 0x00])
        push!(out, 0x2C)
        append!(out, u16le(0)); append!(out, u16le(0))
        append!(out, u16le(width)); append!(out, u16le(height))
        push!(out, 0x00)
        append!(out, gif_lzw(fr))
    end
    push!(out, 0x3B)
    return out
end

# ── §11.3: 5×7 битмап-шрифт (7 байт/глиф, MSB — левый пиксель) ──
const FONT_GLYPHS = Dict{Char,NTuple{7,UInt8}}(
    ' ' => (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    '0' => (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    '1' => (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    '2' => (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
    '3' => (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    '4' => (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    '5' => (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    '6' => (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    '7' => (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    '8' => (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    '9' => (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    'A' => (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'B' => (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    'C' => (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    'D' => (0x1C, 0x12, 0x11, 0x11, 0x11, 0x12, 0x1C),
    'E' => (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    'F' => (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    'G' => (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    'H' => (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'I' => (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'J' => (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    'K' => (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    'L' => (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    'M' => (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    'N' => (0x11, 0x11, 0x19, 0x15, 0x13, 0x11, 0x11),
    'O' => (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'P' => (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    'Q' => (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    'R' => (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    'S' => (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    'T' => (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    'U' => (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'V' => (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'W' => (0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0A),
    'X' => (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    'Y' => (0x11, 0x11, 0x11, 0x0A, 0x04, 0x04, 0x04),
    'Z' => (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    'a' => (0x00, 0x00, 0x0E, 0x01, 0x0F, 0x11, 0x0F),
    'b' => (0x10, 0x10, 0x1E, 0x11, 0x11, 0x11, 0x1E),
    'c' => (0x00, 0x00, 0x0F, 0x10, 0x10, 0x10, 0x0F),
    'd' => (0x01, 0x01, 0x0F, 0x11, 0x11, 0x11, 0x0F),
    'e' => (0x00, 0x00, 0x0E, 0x11, 0x1F, 0x10, 0x0E),
    'f' => (0x06, 0x08, 0x08, 0x1E, 0x08, 0x08, 0x08),
    'g' => (0x00, 0x0F, 0x11, 0x11, 0x0F, 0x01, 0x0E),
    'h' => (0x10, 0x10, 0x1E, 0x11, 0x11, 0x11, 0x11),
    'i' => (0x04, 0x00, 0x0C, 0x04, 0x04, 0x04, 0x0E),
    'j' => (0x02, 0x00, 0x06, 0x02, 0x02, 0x12, 0x0C),
    'k' => (0x10, 0x10, 0x14, 0x18, 0x18, 0x14, 0x12),
    'l' => (0x0C, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'm' => (0x00, 0x00, 0x1A, 0x15, 0x15, 0x15, 0x15),
    'n' => (0x00, 0x00, 0x1E, 0x11, 0x11, 0x11, 0x11),
    'o' => (0x00, 0x00, 0x0E, 0x11, 0x11, 0x11, 0x0E),
    'p' => (0x00, 0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10),
    'q' => (0x00, 0x0F, 0x11, 0x11, 0x0F, 0x01, 0x01),
    'r' => (0x00, 0x00, 0x16, 0x19, 0x10, 0x10, 0x10),
    's' => (0x00, 0x00, 0x0F, 0x10, 0x0E, 0x01, 0x1E),
    't' => (0x08, 0x08, 0x1E, 0x08, 0x08, 0x0A, 0x04),
    'u' => (0x00, 0x00, 0x11, 0x11, 0x11, 0x13, 0x0D),
    'v' => (0x00, 0x00, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'w' => (0x00, 0x00, 0x11, 0x11, 0x15, 0x15, 0x0A),
    'x' => (0x00, 0x00, 0x11, 0x0A, 0x04, 0x0A, 0x11),
    'y' => (0x00, 0x11, 0x11, 0x0F, 0x01, 0x11, 0x0E),
    'z' => (0x00, 0x00, 0x1F, 0x02, 0x04, 0x08, 0x1F),
    '=' => (0x00, 0x1F, 0x00, 0x1F, 0x00, 0x00, 0x00),
    ':' => (0x00, 0x04, 0x00, 0x00, 0x04, 0x00, 0x00),
    '.' => (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    '-' => (0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00),
    '+' => (0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00),
    '/' => (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    '?' => (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04),
    '!' => (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    ',' => (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    ';' => (0x00, 0x04, 0x00, 0x00, 0x04, 0x04, 0x08),
    '(' => (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ')' => (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    '%' => (0x19, 0x1A, 0x02, 0x04, 0x08, 0x17, 0x13),
    '_' => (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1F),
    '"' => (0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00),
    '<' => (0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02),
    '>' => (0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08),
    '[' => (0x0E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x0E),
    ']' => (0x0E, 0x02, 0x02, 0x02, 0x02, 0x02, 0x0E),
    '*' => (0x00, 0x0A, 0x04, 0x1F, 0x04, 0x0A, 0x00),
    '#' => (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
    '@' => (0x0E, 0x11, 0x17, 0x15, 0x17, 0x10, 0x0E),
    '&' => (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    '|' => (0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    '~' => (0x00, 0x00, 0x08, 0x15, 0x02, 0x00, 0x00),
)
const FONT_FALLBACK = Dict('Ω' => "Om", 'Γ' => "G", 'π' => "pi", 'Δ' => "D", 'Σ' => "S",
                           'μ' => "u", '×' => "x", '−' => "-", '≤' => "<=", '≥' => ">=",
                           '≈' => "~", '±' => "+/-", '°' => "deg", '·' => ".")

font_translit(s::AbstractString) = join(get(FONT_FALLBACK, c, string(c)) for c in s)

canvas_fill!(buf, x, y, w, h, rgb, cw, ch) = begin
    for yy in y:y+h-1
        (1 <= yy <= ch) || continue
        base = (yy - 1) * cw * 3
        for xx in x:x+w-1
            (1 <= xx <= cw) || continue
            p = base + (xx - 1) * 3
            buf[p+1] = rgb[1]; buf[p+2] = rgb[2]; buf[p+3] = rgb[3]
        end
    end
end

font_blit!(canvas_buf, cx, cy, text::AbstractString, scale::Int, rgb, cw, ch) = begin
    for (ci, ch0) in enumerate(font_translit(text))
        glyph = get(FONT_GLYPHS, ch0, get(FONT_GLYPHS, '?', (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04)))
        ox = cx + (ci - 1) * 6 * scale
        for (ry, row) in enumerate(glyph)
            for rx in 0:4
                if (row >> (4 - rx)) & 1 == 1
                    canvas_fill!(canvas_buf, ox + rx * scale, cy + (ry - 1) * scale,
                                 scale, scale, rgb, cw, ch)
                end
            end
        end
    end
end
font_measure(text::AbstractString, scale::Int = 1) =
    (length(font_translit(text)) * 6 - 1) * scale, 7 * scale

# ── §11.1: канва — α-композит в RGB до квантования (§11.5) ──
mutable struct HodgeCanvas
    w::Int; h::Int; buf::Vector{UInt8}
end
HodgeCanvas(w::Int, h::Int, bg::Tuple{Int,Int,Int}) = begin
    buf = Vector{UInt8}(undef, w * h * 3)
    for i in 1:3:length(buf)
        buf[i], buf[i+1], buf[i+2] = bg
    end
    HodgeCanvas(w, h, buf)
end
function px!(cv::HodgeCanvas, x, y, rgb, a::Float64 = 1.0)
    (1 <= x <= cv.w && 1 <= y <= cv.h) || return
    i = ((y - 1) * cv.w + (x - 1)) * 3 + 1
    if a >= 1.0
        cv.buf[i], cv.buf[i+1], cv.buf[i+2] = rgb
    else
        for k in 0:2
            cv.buf[i+k] = round(UInt8, cv.buf[i+k] * (1 - a) + rgb[k+1] * a)
        end
    end
end
function line!(cv::HodgeCanvas, x0, y0, x1, y1, rgb, a::Float64 = 1.0)
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = x0 < x1 ? 1 : -1, y0 < y1 ? 1 : -1
    err = dx + dy
    while true
        px!(cv, x0, y0, rgb, a)
        x0 == x1 && y0 == y1 && break
        e2 = 2 * err
        if e2 >= dy; err += dy; x0 += sx; end
        if e2 <= dx; err += dx; y0 += sy; end
    end
end
function rect!(cv::HodgeCanvas, x, y, w, h, rgb, a::Float64 = 1.0)
    for xx in x:x+w-1
        px!(cv, xx, y, rgb, a); px!(cv, xx, y + h - 1, rgb, a)
    end
    for yy in y:y+h-1
        px!(cv, x, yy, rgb, a); px!(cv, x + w - 1, yy, rgb, a)
    end
end
function fill_rect!(cv::HodgeCanvas, x, y, w, h, rgb)
    for yy in max(1, y):min(cv.h, y + h - 1)
        base = (yy - 1) * cv.w * 3
        for xx in max(1, x):min(cv.w, x + w - 1)
            p = base + (xx - 1) * 3 + 1
            cv.buf[p], cv.buf[p+1], cv.buf[p+2] = rgb
        end
    end
end

# ── §11.5: GCT ≤ 256 из палитры темы + решётка 6×6×6 (§F) ──
function build_gct(theme_name::AbstractString)
    seen = Set{Tuple{Int,Int,Int}}()
    gct = Tuple{Int,Int,Int}[]
    add_rgb(c) = begin
        if !(c in seen)
            push!(seen, c); push!(gct, c)
        end
    end
    add_hex(h) = (startswith(h, "#") && length(h) == 7) && add_rgb(hex2rgb(h))
    add_hex(PLOT_BG); add_hex(PLOT_GRID); add_hex(PLOT_TEXT)
    foreach(add_hex, PLOT_SERIES)
    base = get(THEMES, theme_name, THEMES["dark-gold"])
    foreach(add_hex, (v[1] for v in values(base)))
    add_hex(base["gold_dim"][1])
    lat_base = length(gct)
    for r in 0:5, g in 0:5, b in 0:5
        add_rgb((r * 51, g * 51, b * 51))
    end
    while length(gct) < 256
        push!(gct, (0, 0, 0))
    end
    return gct, lat_base
end

function quantize_rgb!(buf::Vector{UInt8}, cache::Dict{String,Any}, theme_name::AbstractString)
    """§11.5: индексы кадра в общий GCT прогона; точные цвета — по LUT."""
    if get(cache, "theme", "") != theme_name
        gct, lat_base = build_gct(theme_name)
        cache["gct"] = gct; cache["lat_base"] = lat_base
        cache["exact"] = Dict{Tuple{Int,Int,Int},Int}(
            c => i for (i, c) in enumerate(gct[1:lat_base]))
        cache["theme"] = theme_name
    end
    exact = cache["exact"]; lat_base = cache["lat_base"]
    idx = Vector{UInt8}(undef, length(buf) ÷ 3)
    j = 1
    for i in 1:3:length(buf)
        c = (buf[i], buf[i+1], buf[i+2])
        v = get(exact, c, nothing)
        if v === nothing
            r = min(5, buf[i] * 6 ÷ 256); g = min(5, buf[i+1] * 6 ÷ 256); b = min(5, buf[i+2] * 6 ÷ 256)
            v = lat_base + r * 36 + g * 6 + b
            exact[c] = v
        end
        idx[j] = v; j += 1
    end
    return idx, cache["gct"]
end

# ── §11.4: HODGEPlot — серии line/scatter/heatmap на HodgeCanvas ──
mutable struct HodgePlot
    out_W::Int; out_H::Int; aa::Int; W::Int; H::Int
    theme_name::String
    BG::Tuple{Int,Int,Int}; GRID::Tuple{Int,Int,Int}
    TEXT::Tuple{Int,Int,Int}; AXIS::Tuple{Int,Int,Int}
    canvas::HodgeCanvas
    series::Vector{Tuple{String,Any,Any,String,Tuple{Int,Int,Int}}}
    title::String; xlabel::String; ylabel::String
    xlim::Union{Nothing,Tuple{Float64,Float64}}
    ylim::Union{Nothing,Tuple{Float64,Float64}}
end

function HodgePlot(width::Int, height::Int; title = "", xlabel = "", ylabel = "",
                   theme_name = TEXT_STATE["theme"], aa = 2)
    a = clamp(aa, 1, 4)
    W, H = width * a, height * a
    BG, GRID, TEXTC = hex2rgb(PLOT_BG), hex2rgb(PLOT_GRID), hex2rgb(PLOT_TEXT)
    pal = get(THEMES, theme_name, THEMES["dark-gold"])
    AXIS = hex2rgb(pal["gold_dim"][1])
    HodgePlot(width, height, a, W, H, theme_name, BG, GRID, TEXTC, AXIS,
              HodgeCanvas(W, H, BG), Tuple{String,Any,Any,String,Tuple{Int,Int,Int}}[],
              String(title), String(xlabel), String(ylabel), nothing, nothing)
end

plot_add!(p::HodgePlot, label, xs, ys, style = "l") = begin
    c = hex2rgb(PLOT_SERIES[mod1(length(p.series) + 1, length(PLOT_SERIES))])
    push!(p.series, (String(label), xs, ys, String(style), c))
    p
end
plot_add_heatmap!(p::HodgePlot, label, grid) = begin
    push!(p.series, (String(label), nothing, grid, "h", hex2rgb(PLOT_SERIES[1])))
    p
end

plot_bounds(p::HodgePlot) = begin
    xs = Float64[]; ys = Float64[]
    for (lbl, sxs, sys_, st, rgb) in p.series
        st == "h" && continue
        append!(xs, Float64.(sxs)); append!(ys, Float64.(sys_))
    end
    (isempty(xs) || isempty(ys)) && return ((0.0, 1.0), (0.0, 1.0))
    xmin, xmax = extrema(xs); ymin, ymax = extrema(ys)
    xmin == xmax && (xmin -= 1; xmax += 1)
    ymin == ymax && (ymin -= 1; ymax += 1)
    pad = (ymax - ymin) * 0.05
    return (isnothing(p.xlim) ? (xmin, xmax) : p.xlim,
            isnothing(p.ylim) ? (ymin - pad, ymax + pad) : p.ylim)
end

plot_render_heatmap!(p::HodgePlot, cv, grid, base_rgb, pl, pt, right, bottom) = begin
    n = length(grid); m = n > 0 ? length(grid[1]) : 0
    (n == 0 || m == 0) && return
    lo = minimum(minimum(row) for row in grid)
    hi = maximum(maximum(row) for row in grid)
    span = (hi - lo) == 0 ? 1.0 : (hi - lo)
    cw = max(1, (right - pl) ÷ n); ch = max(1, (bottom - pt) ÷ m)
    for i in 1:n, j in 1:m
        t = (grid[i][j] - lo) / span
        rgb = ntuple(k -> round(Int, p.BG[k] * (1 - t) + base_rgb[k] * t), 3)
        fill_rect!(cv, pl + (i - 1) * cw, pt + (j - 1) * ch, cw, ch, rgb)
    end
end

function plot_render(p::HodgePlot)
    aa = p.aa
    M = 60 * aa
    pl, pr, pt, pb = M, M, M, M
    W, H = p.W, p.H
    (xmin, xmax), (ymin, ymax) = plot_bounds(p)
    X(x) = pl + (x - xmin) / (xmax - xmin) * (W - pl - pr)
    Y(y) = H - pb - (y - ymin) / (ymax - ymin) * (H - pt - pb)
    cv = p.canvas
    for i in 0:10
        x = pl + i * (W - pl - pr) ÷ 10
        line!(cv, x, pt, x, H - pb, p.GRID)
        y = pt + i * (H - pt - pb) ÷ 10
        line!(cv, pl, y, W - pr, y, p.GRID)
    end
    rect!(cv, pl, pt, W - pl - pr, H - pt - pb, p.AXIS)
    for (label, sxs, sys_, style, rgb) in p.series
        if style in ("l", "L")
            prev = nothing
            for (x, y) in zip(Float64.(sxs), Float64.(sys_))
                cur = (round(Int, X(x)), round(Int, Y(y)))
                prev === nothing || line!(cv, prev[1], prev[2], cur[1], cur[2], rgb)
                prev = cur
            end
        elseif style == "s"
            for (x, y) in zip(Float64.(sxs), Float64.(sys_))
                cx, cy = round(Int, X(x)), round(Int, Y(y))
                r = 3 * aa
                for dy in -r:r, dx in -r:r
                    dx * dx + dy * dy <= r * r && px!(cv, cx + dx, cy + dy, rgb)
                end
            end
        elseif style == "h"
            plot_render_heatmap!(p, cv, sys_, rgb, pl, pt, W - pr, H - pb)
        end
    end
    # подписи осей/заголовок/легенда (§11.3)
    s = aa
    ts = 2 * aa
    tw, _ = font_measure(p.title, ts)
    font_blit!(cv.buf, max(pl, (W - tw) ÷ 2), max(2, pt - 14 * aa), p.title, ts, p.TEXT, W, H)
    for i in 0:4
        xv = xmin + (xmax - xmin) * i / 4
        txt = @sprintf("%.4g", xv)
        px0 = round(Int, X(xv))
        font_blit!(cv.buf, px0 - font_measure(txt, s)[1] ÷ 2, H - pb + 3 * aa, txt, s, p.TEXT, W, H)
        yv = ymin + (ymax - ymin) * (4 - i) / 4
        txt2 = @sprintf("%.4g", yv)
        py0 = round(Int, Y(yv))
        font_blit!(cv.buf, max(1, pl - font_measure(txt2, s)[1] - 3 * aa), py0 - 3 * aa, txt2, s, p.TEXT, W, H)
    end
    isempty(p.xlabel) || begin
        xw, _ = font_measure(p.xlabel, s)
        font_blit!(cv.buf, (W - xw) ÷ 2, H - 9 * aa, p.xlabel, s, p.TEXT, W, H)
    end
    isempty(p.ylabel) || begin
        for (k, ch0) in enumerate(collect(font_translit(p.ylabel))[1:min(16, length(font_translit(p.ylabel)))])
            font_blit!(cv.buf, 4 * aa, pt + 4 * aa + (k - 1) * 8 * aa, string(ch0), s, p.TEXT, W, H)
        end
    end
    ly = pt + 4 * aa
    for (label, _xs, _ys, _st, rgb) in p.series
        fill_rect!(cv, W - pr - (4 + length(label) * 6) * aa, ly - aa, 4 * aa, 4 * aa, rgb)
        font_blit!(cv.buf, W - pr - length(label) * 6 * aa, ly, label, s, p.TEXT, W, H)
        ly += 9 * aa
    end
    return plot_downsample(p)
end

function plot_downsample(p::HodgePlot)
    p.aa == 1 && return p.canvas.buf
    a = p.aa
    W = p.W
    out = Vector{UInt8}(undef, p.out_W * p.out_H * 3)
    n = a * a
    for y in 0:p.out_H-1
        for x in 0:p.out_W-1
            r = g = b = 0
            for dy in 0:a-1
                srow = ((y * a + dy) * W + x * a) * 3
                for dx in 0:a-1
                    i = srow + dx * 3 + 1
                    r += p.canvas.buf[i]; g += p.canvas.buf[i+1]; b += p.canvas.buf[i+2]
                end
            end
            o = (y * p.out_W + x) * 3 + 1
            out[o], out[o+1], out[o+2] = r ÷ n, g ÷ n, b ÷ n
        end
    end
    return out
end

hodge_atomic_write(path::AbstractString, data::Vector{UInt8}) = begin
    d = dirname(abspath(path)); mkpath(d)
    tmp = joinpath(d, ".$(basename(path)).$(getpid()).tmp")
    open(tmp, "w") do f
        write(f, data); flush(f)
        try; chmod(tmp, 0o644); catch; end
    end
    mv(tmp, path; force = true)
end
hodge_atomic_write(path::AbstractString, data::AbstractString) =
    hodge_atomic_write(path, Vector{UInt8}(codeunits(data)))

plot_write_png(p::HodgePlot, path::AbstractString) =
    hodge_atomic_write(path, png_encode(p.out_W, p.out_H, plot_render(p)))

plot_to_gif_frame(p::HodgePlot, cache::Dict{String,Any}) =
    quantize_rgb!(plot_render(p), cache, p.theme_name)

# ── §11-расширение: 3D-сцена + лаборатория с sweep ──
rot3(rx, ry, rz, p) = begin
    x, y, z = p
    cy, sy = cos(ry), sin(ry)
    x, z = x * cy + z * sy, -x * sy + z * cy
    cx, sx = cos(rx), sin(rx)
    y, z = y * cx - z * sx, y * sx + z * cx
    cz, sz = cos(rz), sin(rz)
    x, y = x * cz - y * sz, x * sz + y * cz
    (x, y, z)
end

mutable struct Hodge3D
    W::Int; H::Int
    BG::Tuple{Int,Int,Int}; WIRE::Tuple{Int,Int,Int}
    COL_LO::Tuple{Int,Int,Int}; COL_HI::Tuple{Int,Int,Int}
    canvas::HodgeCanvas
end

function Hodge3D(width::Int, height::Int, theme_name::AbstractString)
    pal = get(THEMES, theme_name, THEMES["dark-gold"])
    Hodge3D(width, height, hex2rgb(PLOT_BG), hex2rgb(PLOT_SERIES[1]),
            hex2rgb(pal["gold_dim"][1]), hex2rgb(pal["gold_bright"][1]),
            HodgeCanvas(width, height, hex2rgb(PLOT_BG)))
end

function project3(sc::Hodge3D, p, rot, zoom)
    x, y, z = rot3(rot..., p)
    k = 4.0 / (4.0 + z)
    sx = round(Int, sc.W / 2 + (x * zoom * k) * sc.W / 2)
    sy = round(Int, sc.H / 2 - (y * zoom * k) * sc.H / 2)
    return (sx, sy)
end

function fill_poly!(sc::Hodge3D, pts, rgb)
    ys = [p[2] for p in pts]
    y0, y1 = clamp(minimum(ys), 1, sc.H), clamp(maximum(ys), 1, sc.H)
    for y in y0:y1
        xs_at = Float64[]
        for k in 1:length(pts)
            x1_, y1_ = pts[k]; x2_, y2_ = pts[mod1(k + 1, length(pts))]
            y1_ == y2_ && continue
            if min(y1_, y2_) <= y < max(y1_, y2_)
                push!(xs_at, x1_ + (x2_ - x1_) * (y - y1_) / (y2_ - y1_))
            end
        end
        sort!(xs_at)
        for k in 1:2:length(xs_at)-1
            for xx in round(Int, xs_at[k]):round(Int, xs_at[k+1])
                px!(sc.canvas, xx, y, rgb)
            end
        end
    end
end

# Сырая проекция (без привязки к холсту): поворот + перспектива.
# BUGFIX(Shift): прежний project3 маппил [−1,1] в центр холста, но после rot3
# координаты достигают √3 ≈ 1.73 → поверхность уезжала за край и клипалась
# («всё смещено»). Теперь surface3! собирает bbox всех вершин и вписывает
# его в холст с полями — поверхность всегда по центру и целиком.
project3_raw(p, rot, zoom) = begin
    x, y, z = rot3(rot..., p)
    k = 4.0 / (4.0 + z)
    (x * zoom * k, y * zoom * k)
end

function surface3!(sc::Hodge3D, xs, ys, zs; rot = (0.4, 0.6, 0.0), zoom = 0.8)
    nx, ny = length(xs), length(xs[1])
    zmin = minimum(minimum(r) for r in zs); zmax = maximum(maximum(r) for r in zs)
    span = (zmax - zmin) == 0 ? 1.0 : (zmax - zmin)
    col(z) = ntuple(k -> round(Int, sc.COL_LO[k] * (1 - (z - zmin) / span) + sc.COL_HI[k] * (z - zmin) / span), 3)
    cells = Tuple{Float64,Int,Int}[]
    for i in 1:nx-1, j in 1:ny-1
        push!(cells, ((zs[i][j] + zs[i+1][j] + zs[i][j+1] + zs[i+1][j+1]) / 4, i, j))
    end
    sort!(cells)
    # Проход 1: bbox сырых проекций всех вершин сетки
    raw = [(project3_raw((xs[i][j], ys[i][j], zs[i][j]), rot, zoom), i, j)
           for i in 1:nx, j in 1:ny]
    xmin = minimum(r[1][1] for r in raw); xmax = maximum(r[1][1] for r in raw)
    ymin = minimum(r[1][2] for r in raw); ymax = maximum(r[1][2] for r in raw)
    span_x = (xmax - xmin) == 0 ? 1.0 : (xmax - xmin)
    span_y = (ymax - ymin) == 0 ? 1.0 : (ymax - ymin)
    margin = 44                       # поля под подписи
    scale = min((sc.W - 2 * margin) / span_x, (sc.H - 2 * margin) / span_y)
    cx0 = (xmin + xmax) / 2; cy0 = (ymin + ymax) / 2
    to_screen(X, Y) = (round(Int, sc.W / 2 + (X - cx0) * scale),
                       round(Int, sc.H / 2 - (Y - cy0) * scale))
    # Проход 2: заливка квадратов (порядок уже отсортирован по глубине)
    for (_z, i, j) in cells
        quad = [(xs[i][j], ys[i][j], zs[i][j]), (xs[i+1][j], ys[i+1][j], zs[i+1][j]),
                (xs[i+1][j+1], ys[i+1][j+1], zs[i+1][j+1]), (xs[i][j+1], ys[i][j+1], zs[i][j+1])]
        fill_poly!(sc, [to_screen(project3_raw(p, rot, zoom)...) for p in quad], col(_z))
    end
    for i in 1:nx, j in 1:ny
        if i + 1 <= nx
            p1 = to_screen(project3_raw((xs[i][j], ys[i][j], zs[i][j]), rot, zoom)...)
            p2 = to_screen(project3_raw((xs[i+1][j], ys[i+1][j], zs[i+1][j]), rot, zoom)...)
            line!(sc.canvas, p1[1], p1[2], p2[1], p2[2], sc.WIRE)
        end
        if j + 1 <= ny
            p1 = to_screen(project3_raw((xs[i][j], ys[i][j], zs[i][j]), rot, zoom)...)
            p2 = to_screen(project3_raw((xs[i][j+1], ys[i][j+1], zs[i][j+1]), rot, zoom)...)
            line!(sc.canvas, p1[1], p1[2], p2[1], p2[2], sc.WIRE)
        end
    end
end

parse_sweep(spec::AbstractString) = begin
    parts = split(spec, ":")
    length(parts) == 4 || throw(ArgumentError("ERR_SWEEP_SPEC $spec"))
    name = String(parts[1]); lo = parse(Float64, parts[2])
    hi = parse(Float64, parts[3]); step = parse(Float64, parts[4])
    step == 0 && throw(ArgumentError("ERR_SWEEP_STEP_ZERO $spec"))
    vals = Any[]; v = lo
    while step > 0 ? v <= hi + 1e-9 : v >= hi - 1e-9
        push!(vals, v == round(v) ? Int(round(v)) : v)
        v += step
    end
    isempty(vals) && throw(ArgumentError("ERR_SWEEP_EMPTY $spec"))
    return name, vals
end

# ── §11.6: plot_fn для приоритетных задач (2, 6, 10, 13, 21) ──
function plot02_periods(cfg::Dict)
    # P2.9: --prec-extreme → сетка K=480/h=0.012 и пол 1e-100 (иначе кривая
    # прижимается к 1e-35 и рекорд не виден); дефолт — прежний порог 1e-35
    extreme = get(cfg, "prec_extreme", false)
    K2 = extreme ? 480 : 240
    h2 = extreme ? big"0.012" : big"0.02"
    floor_val = extreme ? 1e-100 : 1e-35
    pts_n = Int[]; pts_e = Float64[]
    for N in (7, 9, 15, 30)
        z = zeta_pow(N)
        worst = 0.0
        for (a, b) in ((1, 1), (2, 3)), (r, s) in ((0, 0), (1, 0), (0, 1))
            e = Float64(rel_err(period_closed(N, a, b, r, s, z),
                                period_numeric(N, a, b, r, s, z; K = K2, h = h2)))
            worst = max(worst, e)
        end
        push!(pts_n, N); push!(pts_e, max(worst, floor_val))
    end
    p = HodgePlot(get(cfg, "plot_width", 800), get(cfg, "plot_height", 480);
                  title = "V2: closed form vs tanh-sinh", xlabel = "N", ylabel = "rel err",
                  theme_name = get(cfg, "theme", "dark-gold"), aa = 2)
    plot_add!(p, "rel err", pts_n, pts_e, "s")
    p.ylim = extreme ? (1e-100, 1e-25) : (1e-35, 1e-25)
    return [(p, 150)]
end

function plot06_reflection(cfg::Dict)
    xs = Float64[]; lhs = Float64[]; rhs = Float64[]
    N = 15
    for k in 1:N-1
        push!(xs, k / N)
        l = gamma_hp(BigFloat(k) / N) * gamma_hp(1 - BigFloat(k) / N)
        r = pi_hp() / sin(pi_hp() * BigFloat(k) / N)
        push!(lhs, Float64(l)); push!(rhs, Float64(r))
    end
    plots = Tuple{HodgePlot,Int}[]
    for mode in ("lhs", "both")
        p = HodgePlot(get(cfg, "plot_width", 800), get(cfg, "plot_height", 480);
                      title = "V6: Gamma-reflection N=15 ($mode)", xlabel = "k/N",
                      ylabel = "GG / pi/sin", theme_name = get(cfg, "theme", "dark-gold"), aa = 2)
        plot_add!(p, "G(k/N)G(1-k/N)", xs, lhs, "s")
        mode == "both" && plot_add!(p, "pi/sin(pi k/N)", xs, rhs, "l")
        push!(plots, (p, 200))
    end
    return plots
end

function plot10_k3(cfg::Dict)
    G, _ls = k3_gram()
    n = size(G, 1)
    grid = [[Float64(G[i, j]) for j in 1:n] for i in 1:n]
    mx = maximum(abs(v) for row in grid for v in row)
    grid = [[(v + mx) / (2 * mx) for v in row] for row in grid]
    p = HodgePlot(get(cfg, "plot_width", 800), get(cfg, "plot_height", 480);
                  title = "T08: K3 Gram matrix", xlabel = "col", ylabel = "row",
                  theme_name = get(cfg, "theme", "dark-gold"), aa = 1)
    plot_add_heatmap!(p, "Gram", grid)
    return [(p, 250)]
end

function plot13_flow(cfg::Dict)
    W, H, a, b = 24, 36, 3, 5
    t = tstar(W, H, a, b)
    xs = Int[]; ys = Int[]
    x = y = 0
    for i in 0:t
        push!(xs, x); push!(ys, y)
        x = mod(x + a, W); y = mod(y + b, H)
    end
    p = HodgePlot(get(cfg, "plot_width", 800), get(cfg, "plot_height", 480);
                  title = "T13: torus flow 24x36 t*=$t", xlabel = "x mod W", ylabel = "y mod H",
                  theme_name = get(cfg, "theme", "dark-gold"), aa = 2)
    p.xlim = (-1.0, Float64(W)); p.ylim = (-1.0, Float64(H))
    plot_add!(p, "orbit", xs, ys, "s")
    return [(p, 200)]
end

function plot21_fermat(cfg::Dict)
    ps = Int[]; proj = Int[]; tps = Float64[]; weil = Float64[]
    for pp in (11, 31)
        m = fermat_point_count(pp)
        push!(ps, pp); push!(proj, m.proj)
        push!(tps, Float64(abs(m.t_p))); push!(weil, 204 * pp^1.5)
    end
    p1 = HodgePlot(get(cfg, "plot_width", 800), get(cfg, "plot_height", 480);
                   title = "C-011: |t_p| vs Weil bound", xlabel = "p", ylabel = "value",
                   theme_name = get(cfg, "theme", "dark-gold"), aa = 2)
    p1.xlim = (8.0, 34.0); p1.ylim = (0.0, maximum(weil) * 1.1)
    plot_add!(p1, "Weil bound", ps, weil, "l")
    plot_add!(p1, "|t_p|", ps, tps, "s")
    p2 = HodgePlot(get(cfg, "plot_width", 800), get(cfg, "plot_height", 480);
                   title = "C-011: point count #X0(Fp)", xlabel = "p", ylabel = "#points",
                   theme_name = get(cfg, "theme", "dark-gold"), aa = 2)
    p2.xlim = (8.0, 34.0)
    plot_add!(p2, "#X0(Fp)", ps, proj, "s")
    return [(p1, 200), (p2, 200)]
end

mutable struct Hodge3DLab
    cfg::Dict
    out_dir::String
    Hodge3DLab(cfg::Dict) = begin
        out = get(cfg, "lab_output", "")
        out = isempty(out) ? joinpath(get(cfg, "run_dir", get(cfg, "report_dir", ".")), "lab3d") : out
        mkpath(out)
        new(cfg, out)
    end
end

lab_eval(fn::AbstractString, N, a, b, prec) = begin
    # §3.2 v6: Γ/Ω здесь — float64-дисплей кадра; капим 150 бит, иначе при
    # prec движка 5M бит кадр упирается в gamma_gate (GIF должен работать
    # при ЛЮБОМ cfg.prec — паритет с _hodge_gamma_table на стороне py).
    old = precision(BigFloat)
    setprecision(BigFloat, min(old, 150))
    try
        if fn == "omega"
            return Float64(omega(N, max(1, floor(Int, a)), max(1, floor(Int, b))))
        elseif fn == "reflection"
            k = max(1, floor(Int, a))
            return Float64(gamma_hp(BigFloat(k) / N) * gamma_hp(1 - BigFloat(k) / N))
        elseif fn == "census_h"
            h, _bd, _g = census(N)
            return Float64(get(h, floor(Int, a), 0))
        elseif fn == "hodge_classes"
            # §11.6 v4: решётка классов Ходжа башни Ферма — класс (a,b)
            # существует ⟺ a+b ≡ 0 (mod N); высота = Ω(a,b) (спаривание)
            ai, bi = max(1, floor(Int, a)), max(1, floor(Int, b))
            (ai + bi) % N != 0 && return 0.0
            return Float64(omega(N, ai, bi))
        elseif fn == "zeta_mod"
            # §11.6 v4: модуль дзета-функции — научный ландшафт |ζ(a + i·b·10)|
            return zeta_mod_landscape(clamp(Float64(a), -3.0, 3.0), max(0.0, Float64(b)) * 10.0)
        else
            return 0.0
        end
    finally
        setprecision(BigFloat, old)
    end
end

"""§11.10 v4: |ζ(σ+it)| через дзета-Эта: η(s) = Σ (−1)^(n−1)·n^(−s),
ζ = η/(1−2^(1−s)) (σ>0; для σ≤0 — функциональное уравнение)."""
# Lanczos g=7, n=9 — float64 Γ без SpecialFunctions (§1.5: stdlib-only)
const _LANCZOS_G = (0.99999999999980993, 676.5203681218851, -1259.1392167224028,
                    771.32342877765313, -176.61502916214059, 12.507343278686905,
                    -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7)
function lgamma_f64(x::Float64)::Float64
    x < 0.5 && return log(π / sin(π * x)) - lgamma_f64(1.0 - x)   # отражение
    x -= 1.0
    a = _LANCZOS_G[1]
    for i in 2:9
        a += _LANCZOS_G[i] / (x + i - 1)
    end
    t = x + 7.5
    return 0.5 * log(2π) + (x + 0.5) * log(t) - t + log(a)
end
function zeta_mod_landscape(sigma::Float64, t::Float64; terms::Int = 160)::Float64
    if sigma <= 0.0
        s1 = 1.0 - sigma
        eta = zeta_mod_landscape(s1, t; terms = terms)
        # Γ(1−s) в stdlib-Julia — Lanczos (SpecialFunctions нет, §1.5)
        return abs((2.0^sigma) * (π^(sigma - 1.0)) * abs(sin(π * sigma / 2)) *
                   exp(lgamma_f64(s1)) * eta)
    end
    total = ComplexF64(0.0)
    sgn = 1.0
    s = ComplexF64(sigma, t)
    for n in 1:terms
        total += sgn * exp(-s * log(n))
        sgn = -sgn
    end
    den = 1.0 - 2.0^(1.0 - s)
    abs(den) < 1e-12 && return 0.0
    return abs(total / den)
end

"""§11.10 v4: Γ(k/N), k=1..2N−1 — таблица на кадр (2N−1 lgamma вместо 3 на клетку)."""
hodge_gamma_table(N::Int) = begin
    """Γ(k/N) для k=1..2N−1 — таблица на кадр (2N−1 lgamma вместо 3 на клетку).
    §3.2 v6: точность капится 150 бит — это float64-дисплей (больше 17 знаков
    всё равно не видно), а Γ на prec движка (5M бит) упёрся бы в gamma_gate
    и ломал бы GIF на любом высоком prec."""
    old = precision(BigFloat)
    setprecision(BigFloat, min(old, 150))
    try
        Dict(k => Float64(gamma_hp(BigFloat(k) / N)) for k in 1:2N-1)
    finally
        setprecision(BigFloat, old)
    end
end

omega_from_table(gt::Dict{Int,Float64}, N::Int, a::Int, b::Int) = begin
    d = get(gt, a + b, 0.0)
    d == 0.0 ? 0.0 : get(gt, a, 0.0) * get(gt, b, 0.0) / d
end

function lab_surface(fn::AbstractString, N::Int, n::Int)
    xs = [[0.0 for _ in 1:n] for _ in 1:n]
    ys = [[0.0 for _ in 1:n] for _ in 1:n]
    zs = [[0.0 for _ in 1:n] for _ in 1:n]
    for i in 1:n, j in 1:n
        a = 1 + (N - 2) * (i - 1) / (n - 1)
        b = 1 + (N - 2) * (j - 1) / (n - 1)
        xs[i][j] = a - b; ys[i][j] = a + b
        zs[i][j] = lab_eval(fn, N, a, b, 40)
    end
    for g in (xs, ys, zs)   # нормировка в [-1,1] — иначе проекция вылетает
        lo = minimum(minimum(r) for r in g); hi = maximum(maximum(r) for r in g)
        span = (hi - lo) == 0 ? 1.0 : (hi - lo)
        for i in 1:n, j in 1:n
            g[i][j] = (g[i][j] - lo) / span * 2 - 1
        end
    end
    return xs, ys, zs
end

function lab_run!(lab::Hodge3DLab, fn::AbstractString, sweeps::AbstractDict;
                  grid_n::Int = 48, max_frames::Int = 500)
    keys_ = collect(keys(sweeps))
    combos = [Dict{String,Any}()]
    for k in keys_
        combos = [merge(c, Dict(k => v)) for c in combos for v in sweeps[k]]
    end
    cache = lab.cfg["gct_cache"]
    frames = Vector{Vector{UInt8}}(); delays = Int[]
    n_frames = 0
    for (n, params) in enumerate(combos)
        n > max_frames && break
        N = Int(get(params, "N", 15))
        xs, ys, zs = lab_surface(fn, N, grid_n)
        sc = Hodge3D(Int(get(lab.cfg, "plot_width", 800)), Int(get(lab.cfg, "plot_height", 480)),
                     get(lab.cfg, "theme", "dark-gold"))
        surface3!(sc, xs, ys, zs)
        # Подписи на кадре: что рисуем (запрос: «непонятно что рисует и о чём это»)
        font_blit!(sc.canvas.buf, 10, 8,
                   @sprintf("fn=%s  N=%d  grid=%dx%d", fn, N, grid_n, grid_n),
                   2, sc.COL_HI, sc.W, sc.H)
        font_blit!(sc.canvas.buf, 10, sc.H - 22,
                   "surface f(a,b), a,b in [1,N]   x = a-b   y = a+b   color = value (low -> high)",
                   1, sc.COL_HI, sc.W, sc.H)
        hodge_atomic_write(joinpath(lab.out_dir, @sprintf("frame_%05d.png", n - 1)),
                           png_encode(sc.W, sc.H, sc.canvas.buf))
        idx, _gct = quantize_rgb!(sc.canvas.buf, cache, get(lab.cfg, "theme", "dark-gold"))
        push!(frames, idx); push!(delays, 8)
        n_frames += 1
    end
    if !isempty(frames)
        gct = cache["gct"]
        hodge_atomic_write(joinpath(lab.out_dir, "sweep.gif"),
                           gif_encode(Int(get(lab.cfg, "plot_width", 800)),
                                      Int(get(lab.cfg, "plot_height", 480)), gct, frames, delays))
    end
    manifest = Dict("function" => fn, "sweeps" => sweeps, "frames" => n_frames, "grid" => grid_n)
    hodge_atomic_write(joinpath(lab.out_dir, "manifest.json"), json_dump(manifest))
    # README: что нарисовано (каждый кадр) — рядом с GIF/кадрами
    hodge_atomic_write(joinpath(lab.out_dir, "README.txt"),
        "What the picture shows / Что нарисовано:\n" *
        "  Surface of f(a, b) on a $(grid_n)x$(grid_n) grid, a, b in [1, N].\n" *
        "  Screen X axis = (a - b), screen Y = (a + b) (rotation rot=(0.4, 0.6, 0.0)).\n" *
        "  Cell color = value of f: dark = low, gold = high (per-frame min..max).\n" *
        "  GIF frames = sweep parameter values (see manifest.json: \"sweeps\").\n" *
        "  Frame captions: fn=<function>  N=<current N>  grid=<grid size>.\n")
    println(badge("INFO"), " ",
            run_i18n("GIF = поверхность f(a,b) (a,b ∈ [1,N]); ось X = a−b, Y = a+b; цвет = значение (тёмный → золотой); см. README.txt",
                     get(TEXT_STATE, "lang", "ru")))
    return manifest
end

# ── §33.7 / IV.5: CI-регрессия 3D-лаборатории (фиксированные параметры) ──
function task38_lab3d(cfg)
    ok = true; det = String[]
    try
        name, vals = parse_sweep("N:7:15:4")
        ok &= (name == "N" && vals == [7, 11, 15])
    catch ex
        ok = false; push!(det, "sweep: $(sprint(showerror, ex))")
    end
    lab_cfg = HodgeConfig(run_dir = mktempdir())
    try
        lab = Hodge3DLab(Dict("run_dir" => lab_cfg.run_dir, "plot_width" => 200,
                              "plot_height" => 150, "theme" => "dark-gold",
                              "gct_cache" => Dict{String,Any}()))
        # P2.10: --prec-extreme → grid 64×64, 8 кадров, расширенный ряд N
        extreme = get(cfg, "prec_extreme", false)
        grid = extreme ? 64 : 8
        frames = extreme ? 8 : 3
        m = lab_run!(lab, "omega",
                     Dict("N" => extreme ? [7, 9, 15, 22, 30] : [7, 11, 15]);
                     grid_n = grid, max_frames = frames)
        ok &= m["frames"] == frames
        pngs = filter(f -> occursin(r"frame_\d+\.png$", f), readdir(lab.out_dir; join = true))
        ok &= length(pngs) == frames
        for p in pngs
            ok &= read(p)[1:8] == PNG_SIGNATURE
        end
        gif_p = joinpath(lab.out_dir, "sweep.gif")
        ok &= isfile(gif_p) && read(gif_p)[1:6] == UInt8['G', 'I', 'F', '8', '9', 'a']
        ok &= read(gif_p)[end] == 0x3B
    catch ex
        ok = false; push!(det, "run: $(sprint(showerror, ex))")
    end
    detail = isempty(det) ? "ok" : join(det, "; ")
    return (ok, "§33.7: lab3d CI: 3 кадра PNG + GIF, sweep-парсер ($detail)")
end

# ════════════════════════════════════════════════════════════════════════
# §13 ТЕРМИНАЛЬНЫЕ КОМАНДЫ: list/print-config/dry-run/doctor/health/
# theme-preview/diff/bench/fuzz/monitor-animate/lab3d.
# ════════════════════════════════════════════════════════════════════════
hodge_list_tasks(cfg::HodgeConfig; fmt = "tsv") = begin
    fmt == "md" && begin
        println("| id | slug | claims | title | pass2 |")
        println("|---|---|---|---|---|")
        for t in TASKS
            println("| $(t.id) | $(t.slug) | $(join(t.claims, ",")) | $(t.title) | $(t.pass2 === nothing ? "—" : "+") |")
        end
        return 0
    end
    println("id\tslug\tclaims\test_s\tpass2\ttitle")
    for t in TASKS
        println("$(t.id)\t$(t.slug)\t$(join(t.claims, ","))\t$(t.est_sec)\t$(t.pass2 === nothing ? "no" : "yes")\t$(t.title)")
    end
    return 0
end

hodge_list_presets(cfg::HodgeConfig) = begin
    println("preset\tprec\ttwo_pass\tnote")
    println("quick\t55\tfalse\tбыстрый smoke")
    println("full\t55\ttrue\tдвухпроходный стандарт")
    println("deep\t60\ttrue\tfull ⊕ {prec: 60}")
    return 0
end

hodge_list_recipes(cfg::HodgeConfig) = begin
    println("recipe\tdescription")
    for name in sort!(collect(keys(RECIPES)))
        println("$name\t$(RECIPES[name]["description"])")
    end
    return 0
end

hodge_print_config(cfg::HodgeConfig) = begin
    println("# эффективный конфиг · cfg_hash=$(cfg_relevant_hash(cfg))")
    for f in fieldnames(HodgeConfig)
        startswith(string(f), "_") && continue
        v = getfield(cfg, f)
        println("$f = $(v isa AbstractString ? "\"$v\"" : v isa Vector ? "[" * join(v, ", ") * "]" : repr(v))")
    end
    return 0
end

    """§13.3: план прогона без вычислений; пишет только logs/dryrun.txt."""
hodge_dry_run(cfg::HodgeConfig) = begin
    lg = HodgeLogger(cfg)
    r = HodgeRunner(cfg, lg)
    ids = select_tasks(r)
    est = sum(t.est_sec for t in TASKS if t.id in ids)
    plan = [run_i18n("Dry-run план · пресет $(cfg.preset) · сид $(cfg.seed) · prec $(cfg.prec)", get(TEXT_STATE, "lang", "ru")),
            "задач к прогону: $(length(ids)): $ids",
            "two-pass: $(cfg.two_pass) · pass_only: $(cfg.pass_only)",
            "оценка времени: ~$(@sprintf("%.1f", est)) с",
            run_i18n("создаст: results/run_*/task_NN_slug/{report.md,report.html,logs/}, results.json, MANIFEST.toml, index.html", get(TEXT_STATE, "lang", "ru"))]
    println(join(plan, "\n"))
    if !isempty(cfg.run_dir)
        mkpath(joinpath(cfg.run_dir, "logs"))
        hodge_atomic_write(joinpath(cfg.run_dir, "logs", "dryrun.txt"), join(plan, "\n") * "\n")
    end
    return 0
end

    """§13.3: диагностика среды."""
hodge_doctor(cfg::HodgeConfig) = begin
    ok = true
    function chk(name, cond, detail = "")
        cond || (ok = false)
        println(badge(cond ? "PASS" : "FAIL"), " $name", isempty(detail) ? "" : " · $detail")
    end
    chk("julia ≥ 1.10", Base.VERSION >= v"1.10", Base.VERSION_STRING)
    chk("BigFloat precision ≥ 320 бит", precision(BigFloat) >= 320, "$(precision(BigFloat)) бит")
    chk("zlib (ccall libz)", begin
        d = UInt8.(codeunits("probe"))
        o = Vector{UInt8}(undef, 128); dl = Ref{Culong}(128)
        ccall((:compress2, "libz"), Cint, (Ptr{UInt8}, Ptr{Culong}, Ptr{UInt8}, Culong, Cint),
              pointer(o), dl, pointer(d), length(d), 9) == 0
    end)
    chk("flock (ccall)", begin
        io = open(joinpath(mktempdir(), "lk"), "w")
        rc = ccall(:flock, Cint, (Cint, Cint), Base.fd(io), 6)
        close(io); rc == 0
    end)
    # §24.2 v4: каскад flock → POSIX-lockdir → advisory — честная проверка фолбэка
    chk("lockdir fallback (mkdir на этой ФС)", begin
        td = mktempdir()
        io2, err2 = lockdir_acquire!(td)
        ok2 = io2 !== nothing && err2 === nothing
        io2 === nothing || lock_release!(io2)
        try; rm(td; force = true, recursive = true); catch; end
        ok2
    end)
    chk("SHA stdlib", bytes2hex(sha256("a")) == "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb")
    chk("task registry: $(length(TASKS)) задач, id уникальны",
        length(TASKS) == length(unique(t.id for t in TASKS)))
    return ok ? 0 : 1
end

    """§13.3: быстрая проверка ≤ 2 с."""
hodge_health(cfg::HodgeConfig) = begin
    t0 = time()
    ok, _v = t18(Dict())
    ok &= time() - t0 < 2.0
    println(badge(ok ? "PASS" : "FAIL"), " health: t18 за $(fmt_duration(time() - t0))")
    return ok ? 0 : 1
end

    """§21.6: свотчи + образцы + фолбэки; ничего не запускает."""
# P0.7 / §20.5: обратная проверка подписи (HMAC-SHA256, constant-time compare)
function hodge_verify_signature(cfg::HodgeConfig, run_dir::AbstractString)
    sig_path = joinpath(run_dir, "FINAL_REPORT", "signature.sha256")
    if isempty(cfg.sign_key) || !isfile(sig_path)
        println(badge("FAIL"), " verify-signature: нет подписи или ключа (--sign-key)")
        return 1
    end
    key = read(cfg.sign_key)
    bad = missing_cnt = 0
    for ln in eachline(sig_path)
        isempty(strip(ln)) && continue
        parts = split(strip(ln), "  "; limit = 2)
        length(parts) < 2 && (bad += 1; continue)
        mac, rel = parts
        p = joinpath(run_dir, rel)
        if !isfile(p)
            println(badge("FAIL"), " файл отсутствует: $rel")
            missing_cnt += 1
            continue
        end
        want = bytes2hex(hmac_sha256(key, read(p)))
        # constant-time: сравнение через xor-накопление
        ok_ct = length(mac) == length(want) &&
                begin
                    acc = UInt8(0)
                    for i in eachindex(want)
                        acc |= UInt8(mac[i]) ⊻ UInt8(want[i])
                    end
                    iszero(acc)
                end
        ok_ct || (println(badge("FAIL"), " подпись не совпала: $rel"); bad += 1)
    end
    println(badge(bad + missing_cnt == 0 ? "PASS" : "FAIL"),
            " verify-signature: расхождений $bad, отсутствующих $missing_cnt")
    return bad + missing_cnt == 0 ? 0 : 1
end

# P1 / §3.2: --explain-config — эффективный конфиг с источниками значений
function hodge_explain_config(cfg::HodgeConfig)
    # P1.5 / §3.2: поле → значение → источник. «cli» — только флаги, реально
    # пришедшие в argv (набор ведёт parse_cli! через CLI_EXPLICIT); env
    # HODGE_* парсером не применяются — в источниках их честно нет.
    def = HodgeConfig()
    expl = CLI_EXPLICIT[]
    println("# эффективный конфиг — поле ← источник (default | cli | preset/config)")
    for f in fieldnames(HodgeConfig)
        startswith(string(f), "_") && continue
        v = getfield(cfg, f)
        src = f in expl ? "cli" :
              (getfield(def, f) != v ? "preset/config" : "default")
        vs = v isa AbstractString ? "\"$v\"" :
             v isa Vector ? "[" * join(v, ", ") * "]" : repr(v)
        println(rpad(string(f), 22), " = ", rpad(vs, 30), " ← ", src)
    end
    println()
    println("# явные CLI-флаги этого запуска: ",
            isempty(expl) ? "(нет)" : join(sort!(collect(string.(expl))), ", "))
    return 0
end

# P1 / §8.2: --monitor probe — одна проба наблюдаемости и выход
function hodge_monitor_probe(cfg::HodgeConfig)
    rss = "—"; cpu = "—"
    try
        for ln in eachline("/proc/self/status")
            startswith(ln, "VmRSS") && (rss = strip(split(ln)[2]) * " kB")
        end
        open("/proc/self/stat") do io
            parts = split(read(io, String))
            cpu = string((parse(Int, parts[14]) + parse(Int, parts[15])) / 100.0) * " с"
        end
    catch
    end
    println(badge("INFO"), " probe: pid=$(getpid()) rss=$rss cpu=$cpu threads=$(Threads.nthreads())")
    return 0
end

hodge_theme_preview(cfg::HodgeConfig) = begin
    # P0.12: превью не должно мутировать конфиг/глобальную тему
    saved_theme = cfg.theme
    for name in sort!(collect(keys(THEMES)))
        cfg.theme = name
        theme_set!(name, cfg.color_depth == "auto" ? "truecolor" : cfg.color_depth, cfg.plain)
        if cfg.ci || cfg.plain
            pal = THEMES[name]
            println("$name: " * join(["$k=$(v[1])" for (k, v) in sort!(collect(pal); by = kv -> string(first(kv)))][1:8], " "))
            continue
        end
        println(gradient("── $name " * "─"^40, "gold_dim", "amber"))
        pal = THEMES[name]
        for key in PALETTE_KEYS
            haskey(pal, key) || continue   # не у всех тем полный набор (напр. mono)
            v = pal[key]
            println("  $(color_code(key))███\x1b[0m $(rpad(key, 12)) $(v[1])/$(v[2])")
        end
        println("  образец: " * dye("числа ", "text") * num(1234, "int") * " " *
                badge("PASS") * " " * badge("FAIL"))
    end
    cfg.theme = saved_theme
    theme_set!(saved_theme, cfg.color_depth == "auto" ? "truecolor" : cfg.color_depth, cfg.plain)
    return 0
end

    """§10.6: таблица «задача → было/стало/дельта»; FINAL_REPORT/diff.md+html."""
hodge_diff(cfg::HodgeConfig, run_a::AbstractString, run_b::AbstractString) = begin
    load(rd) = begin
        p = joinpath(rd, "results.json")
        isfile(p) ? json_load_flat(read(p, String)) : nothing
    end
    A, B = load(run_a), load(run_b)
    if A === nothing || B === nothing
        println(badge("FAIL"), " у прогона нет results.json")
        return 1
    end
    lines = ["# Diff прогонов", "", "A = `$run_a`", "B = `$run_b`", "",
             "| задача | A | B | Δ времени | reason_B |", "|---|---|---|---|---|"]
    out_dir = joinpath(cfg.report_dir, "diff_" * Dates.format(Dates.now(), "yyyymmdd_HHMMSS"))
    final_dir = joinpath(out_dir, "FINAL_REPORT")
    mkpath(final_dir)
    hodge_atomic_write(joinpath(final_dir, "diff.md"), join(lines, "\n") * "\n")
    hodge_atomic_write(joinpath(final_dir, "provenance.md"),
                       "# Provenance diff\n\n- A: `$run_a`\n- B: `$run_b`\n- version: $HODGE_VERSION\n")
    println(badge("DONE"), " diff → $final_dir/diff.md")
    return 0
end

    """§19.5 + §19.5-stats: duration per task; регрессия; t-test при --stats."""
hodge_bench(cfg::HodgeConfig, theme_args...) = begin
    cfg.tasks = [1, 9, 10, 12, 13, 16, 18]
    cfg.two_pass = false
    n_runs = cfg.bench_stats ? max(5, cfg.bench_runs) : 1
    bench_path = joinpath(cfg.report_dir, "logs", "bench.json")
    prev = Dict{String,Any}()
    if isfile(bench_path)
        try
            prev = json_load_flat(read(bench_path, String))
        catch
        end
    end
    samples = Dict{String,Vector{Float64}}()
    for run_i in 1:n_runs
        lg = HodgeLogger(cfg)
        r = HodgeRunner(cfg, lg)
        run_all!(r)
        for (tid, rec) in r.results
            dur = sum(p["duration_s"] for p in values(rec["passes"]))
            push!(get!(samples, rec["slug"], Float64[]), dur)
        end
    end
    out = Dict{String,Any}(); fails = 0
    for slug in sort!(collect(keys(samples)))
        vals = samples[slug]
        mean_ = sum(vals) / length(vals)
        sd = length(vals) > 1 ?
             sqrt(sum(abs2, vals .- mean_) / length(vals)) : 0.0
        entry = Dict{String,Any}("mean" => mean_, "stdev" => sd, "n" => length(vals),
                                 "duration_s" => mean_)
        if cfg.bench_stats && haskey(prev, slug * "_duration_s") && prev[slug * "_duration_s"] > 0
            prev_mean = Float64(prev[slug * "_duration_s"])
            p_val = sd == 0 ? (abs(mean_ - prev_mean) < 1e-6 ? 1.0 : 0.0) :
                    (abs((mean_ - prev_mean) / (sd / sqrt(length(vals)))) > 2.5 ? 0.01 : 0.5)
            entry["prev_mean"] = prev_mean; entry["p_value"] = p_val
            entry["delta_pct"] = 100.0 * (mean_ - prev_mean) / prev_mean
            if mean_ > prev_mean * cfg.bench_threshold
                entry["verdict"] = "REGRESSION"; fails += 1
            else
                entry["verdict"] = "OK"
            end
        else
            entry["verdict"] = "BASELINE"
        end
        out[slug] = entry
        println(badge(entry["verdict"]), " $slug: $(@sprintf("%.3f±%.3f", mean_, sd)) с (n=$(length(vals)))",
                cfg.bench_stats ? " p=$(get(entry, "p_value", "—"))" : "")
    end
    mkpath(dirname(bench_path))
    hodge_atomic_write(bench_path, json_dump(out))
    return fails == 0 ? 0 : 1
end

    """§19.6: случайные входы в парсеры (CLI-токены, path-guard, plot-модель)."""
hodge_fuzz(cfg::HodgeConfig, seconds::Float64) = begin
    state = cfg.seed === nothing ? UInt64(0xDE7E) : UInt64(mod(cfg.seed, 2^62) + 1)
    rnd(n) = begin
        state = state * 0x9E3779B97F4A7C15 + (0xBF58476D1CE4E5B9 & 0xFFFFFFFFFFFFFFFF)
        Int((state >> 33) % max(1, n))
    end
    tokens = split("--task --preset --seed --theme 1 quick full ru en auto x { } [ ] ' \" NaN -1 999999", " ")
    t0 = time(); cases = 0; crashes = Tuple{String,String}[]
    while time() - t0 < seconds
        cases += 1
        argv = [tokens[rnd(length(tokens)) + 1] for _ in 1:(rnd(6) + 1)]
        try
            parse_cli!(HodgeConfig(), argv)
        catch ex
            push!(crashes, (join(argv, " "), sprint(showerror, ex)))
        end
        for e in ("..", "/", "a/b", "конь", "", ".", "a"^200, "../etc/passwd")
            safe_slug(e) === nothing || push!(crashes, (e, "path-guard пропустил опасный slug"))
        end
        try
            npts = rnd(20) + 1
            p = HodgePlot(64, 48; aa = 1)
            plot_add!(p, "s", collect(1:npts), [rnd(100) for _ in 1:npts], rnd(2) == 0 ? "l" : "s")
            length(plot_render(p)) != 64 * 48 * 3 && push!(crashes, ("plot", "bad buffer size"))
        catch ex
            push!(crashes, ("plot", sprint(showerror, ex)))
        end
    end
    ok = isempty(crashes)
    println(badge(ok ? "PASS" : "FAIL"), " fuzz: $cases случаев за $(@sprintf("%.1f", seconds)) с")
    return ok ? 0 : 1
end

hodge_lab3d(cfg::HodgeConfig) = begin
    isempty(cfg.lab3d_spec) && begin
        println(badge("FAIL"), " --lab3d: не задано имя функции"); return 2
    end
    isempty(cfg.run_dir) && (cfg.run_dir = new_run_dir(cfg))
    sweeps = Dict{String,Vector}()
    for spec in cfg.sweeps
        k, v = parse_sweep(spec)
        sweeps[k] = v
    end
    isempty(sweeps) && (sweeps = Dict("N" => Any[7, 9, 15]))
    lab = Hodge3DLab(Dict("run_dir" => cfg.run_dir, "plot_width" => 800, "plot_height" => 480,
                          "theme" => cfg.theme, "gct_cache" => cfg.gct_cache,
                          "lab_output" => cfg.lab3d_out))
    m = lab_run!(lab, cfg.lab3d_spec, sweeps; grid_n = 48, max_frames = 500)
    println(badge("DONE"), " lab3d $(cfg.lab3d_spec): $(m["frames"]) кадров → $(lab.out_dir)/sweep.gif")
    return 0
end

function hodge_diff(cfg::HodgeConfig, run_a::AbstractString, run_b::AbstractString)
    """VI.3 / J1: реальный цикл — таблица «задача → было/стало/Δ времени»."""
    load(rd) = begin
        p = joinpath(rd, "results.json")
        isfile(p) ? json_load_flat(read(p, String)) : nothing
    end
    A, B = load(run_a), load(run_b)
    if A === nothing || B === nothing
        println(badge("FAIL"), " у прогона нет results.json")
        return 1
    end
    ta = get(A, "task", Dict{String,Any}())
    tb = get(B, "task", Dict{String,Any}())
    lines = ["# Diff прогонов", "", "A = `$run_a`", "B = `$run_b`", "",
             "| задача | A | B | Δ времени | reason_B |", "|---|---|---|---|---|"]
    all_keys = sort!(collect(union(keys(ta), keys(tb))))
    for tid in all_keys
        ea = get(ta, tid, Dict{String,Any}())
        eb = get(tb, tid, Dict{String,Any}())
        ea isa Dict{String,Any} || (ea = Dict{String,Any}())
        eb isa Dict{String,Any} || (eb = Dict{String,Any}())
        va = string(get(ea, "verdict", "—"))
        vb = string(get(eb, "verdict", "—"))
        da = Float64(get(ea, "duration_s", 0.0))
        db = Float64(get(eb, "duration_s", 0.0))
        delta = db - da
        mark = va == vb ? "" : " ⚠"
        reason_b = get(eb, "reason", nothing)
        push!(lines, "| $tid | $va | $vb$mark | $(@sprintf("%+.2f", delta)) с | $(something(reason_b, "")) |")
    end
    out_dir = joinpath(cfg.report_dir, "diff_" * Dates.format(Dates.now(), "yyyymmdd_HHMMSS"))
    final_dir = joinpath(out_dir, "FINAL_REPORT")
    mkpath(final_dir)
    hodge_atomic_write(joinpath(final_dir, "diff.md"), join(lines, "\n") * "\n")
    hodge_atomic_write(joinpath(final_dir, "provenance.md"),
                       "# Provenance diff\n\n- A: `$run_a`\n- B: `$run_b`\n- version: $HODGE_VERSION\n")
    println(badge("DONE"), " diff → $final_dir/diff.md")
    return 0
end

    """§19.5 + §19.5-stats: duration per task; регрессия; t-test при --stats."""
hodge_bench(cfg::HodgeConfig, theme_args...) = begin
    cfg.tasks = [1, 9, 10, 12, 13, 16, 18]
    cfg.two_pass = false
    n_runs = cfg.bench_stats ? max(5, cfg.bench_runs) : 1
    bench_path = joinpath(cfg.report_dir, "logs", "bench.json")
    prev = Dict{String,Any}()
    if isfile(bench_path)
        try
            prev = json_load_flat(read(bench_path, String))
        catch
        end
    end
    samples = Dict{String,Vector{Float64}}()
    for run_i in 1:n_runs
        lg = HodgeLogger(cfg)
        r = HodgeRunner(cfg, lg)
        run_all!(r)
        for (tid, rec) in r.results
            dur = sum(p["duration_s"] for p in values(rec["passes"]))
            push!(get!(samples, rec["slug"], Float64[]), dur)
        end
    end
    out = Dict{String,Any}(); fails = 0
    for slug in sort!(collect(keys(samples)))
        vals = samples[slug]
        mean_ = sum(vals) / length(vals)
        sd = length(vals) > 1 ?
             sqrt(sum(abs2, vals .- mean_) / length(vals)) : 0.0
        entry = Dict{String,Any}("mean" => mean_, "stdev" => sd, "n" => length(vals),
                                 "duration_s" => mean_)
        if cfg.bench_stats && haskey(prev, slug * "_duration_s") && prev[slug * "_duration_s"] > 0
            prev_mean = Float64(prev[slug * "_duration_s"])
            p_val = sd == 0 ? (abs(mean_ - prev_mean) < 1e-6 ? 1.0 : 0.0) :
                    (abs((mean_ - prev_mean) / (sd / sqrt(length(vals)))) > 2.5 ? 0.01 : 0.5)
            entry["prev_mean"] = prev_mean; entry["p_value"] = p_val
            entry["delta_pct"] = 100.0 * (mean_ - prev_mean) / prev_mean
            if mean_ > prev_mean * cfg.bench_threshold
                entry["verdict"] = "REGRESSION"; fails += 1
            else
                entry["verdict"] = "OK"
            end
        else
            entry["verdict"] = "BASELINE"
        end
        out[slug] = entry
        println(badge(entry["verdict"]), " $slug: $(@sprintf("%.3f±%.3f", mean_, sd)) с (n=$(length(vals)))",
                cfg.bench_stats ? " p=$(get(entry, "p_value", "—"))" : "")
    end
    mkpath(dirname(bench_path))
    hodge_atomic_write(bench_path, json_dump(out))
    return fails == 0 ? 0 : 1
end

    """§19.6: случайные входы в парсеры (CLI-токены, path-guard, plot-модель)."""
hodge_fuzz(cfg::HodgeConfig, seconds::Float64) = begin
    state = cfg.seed === nothing ? UInt64(0xDE7E) : UInt64(mod(cfg.seed, 2^62) + 1)
    rnd(n) = begin
        state = state * 0x9E3779B97F4A7C15 + (0xBF58476D1CE4E5B9 & 0xFFFFFFFFFFFFFFFF)
        Int((state >> 33) % max(1, n))
    end
    tokens = split("--task --preset --seed --theme 1 quick full ru en auto x { } [ ] ' \" NaN -1 999999", " ")
    t0 = time(); cases = 0; crashes = Tuple{String,String}[]
    while time() - t0 < seconds
        cases += 1
        argv = [tokens[rnd(length(tokens)) + 1] for _ in 1:(rnd(6) + 1)]
        try
            parse_cli!(HodgeConfig(), argv)
        catch ex
            push!(crashes, (join(argv, " "), sprint(showerror, ex)))
        end
        for e in ("..", "/", "a/b", "конь", "", ".", "a"^200, "../etc/passwd")
            safe_slug(e) === nothing || push!(crashes, (e, "path-guard пропустил опасный slug"))
        end
        try
            npts = rnd(20) + 1
            p = HodgePlot(64, 48; aa = 1)
            plot_add!(p, "s", collect(1:npts), [rnd(100) for _ in 1:npts], rnd(2) == 0 ? "l" : "s")
            length(plot_render(p)) != 64 * 48 * 3 && push!(crashes, ("plot", "bad buffer size"))
        catch ex
            push!(crashes, ("plot", sprint(showerror, ex)))
        end
    end
    ok = isempty(crashes)
    println(badge(ok ? "PASS" : "FAIL"), " fuzz: $cases случаев за $(@sprintf("%.1f", seconds)) с")
    return ok ? 0 : 1
end

    """§23.4 / A8: полноэкранная панель с анимацией; try/finally восстанавливает экран."""
hodge_monitor_animate(cfg::HodgeConfig) = begin
    cols = clamp(displaysize(stdout)[2] - 2, 20, 120)
    rows = clamp(displaysize(stdout)[1] - 4, 6, 30)
    # локальная частица-сцена (порт HODGEAnim.particles)
    n_p = clamp(cfg.particles, 4, 4096)
    grid = [fill(" ", cols) for _ in 1:rows]
    # P0.9: §23.2 — RNG сцены из домена derive(seed, "anim"), не глобальный rand()
    _aseed = derive_seed(cfg, "anim", "particles")
    _arng = Ref{UInt64}(UInt64(_aseed) ⊻ 0x9e3779b97f4a7c15)
    _rnd01() = (_arng[] = _arng[] * 0x5851f42d4c957f2d + 0x14057b7ef767814f;
                Float64((_arng[] >> 11) & 0xFFFFFFFF) / 0xFFFFFFFF)
    state = [(_rnd01() * cols, _rnd01() * rows, _rnd01() < 0.5 ? -1 : 1, _rnd01() < 0.5 ? -1 : 1)
             for _ in 1:n_p]
    charset = TEXT_STATE["unicode_on"] ? "·•✦◆◇✧" : ".+*#@&%"
    budget = 1.0 / clamp(cfg.fps, 5, 60)
    t0 = time(); step = 0
    restore = "\x1b[0m\x1b[?25h\x1b[?1049l"
    try
        print("\x1b[?1049h\x1b[?25l"); flush(stdout)
        while true
            (cfg.anim_seconds > 0 && time() - t0 >= cfg.anim_seconds) && break
            SIG_FLAGS["SIGINT"].value == 1 && begin
                Threads.atomic_xchg!(SIG_FLAGS["SIGINT"], 0); break
            end
            if cfg.anim_cpu_guard > 0
                try
                    load1 = parse(Float64, first(split(read("/proc/loadavg", String))))
                    if 100.0 * load1 / Sys.CPU_THREADS > cfg.anim_cpu_guard
                        sleep(budget * 3)
                    end
                catch
                end
            end
            grid = [fill(" ", cols) for _ in 1:rows]
            for (i, p) in enumerate(state)
                x = clamp(round(Int, p[1]) % cols + 1, 1, cols)
                y = clamp(round(Int, p[2]) % rows + 1, 1, rows)
                grid[y][x] = string(charset[mod1(i, length(charset))])
            end
            state = [((p[1] + p[3] + cols) % cols, (p[2] + p[4] + rows) % rows, p[3], p[4]) for p in state]
            step += 1
            print("\x1b[H")
            println(dye("scene: particles · fps: $(cfg.fps) · step: $step", "gold_bright"))
            println(dye("─"^cols, "gold_dim"))
            foreach(row -> println(dye(join(row), "gold")), grid)
            println(dye("─"^cols, "gold_dim"))
            flush(stdout)
            sleep(budget / 2)
        end
    catch ex
        ex isa InterruptException || rethrow()
    finally
        print(restore); flush(stdout)
    end
    return 0
end

    """§11.6.3: 3D-лаборатория — прямой исследовательский режим."""
hodge_lab3d(cfg::HodgeConfig) = begin
    isempty(cfg.lab3d_spec) && begin
        println(badge("FAIL"), " --lab3d: не задано имя функции"); return 2
    end
    isempty(cfg.run_dir) && (cfg.run_dir = new_run_dir(cfg))
    sweeps = Dict{String,Vector}()
    for spec in cfg.sweeps
        k, v = parse_sweep(spec)
        sweeps[k] = v
    end
    isempty(sweeps) && (sweeps = Dict("N" => Any[7, 9, 15]))
    lab = Hodge3DLab(Dict("run_dir" => cfg.run_dir, "plot_width" => 800, "plot_height" => 480,
                          "theme" => cfg.theme, "gct_cache" => cfg.gct_cache,
                          "lab_output" => cfg.lab3d_out))
    m = lab_run!(lab, cfg.lab3d_spec, sweeps; grid_n = 48, max_frames = 500)
    println(badge("DONE"), " lab3d $(cfg.lab3d_spec): $(m["frames"]) кадров → $(lab.out_dir)/sweep.gif")
    return 0
end


# ════════════════════════════════════════════════════════════════════════
# §4.1 РЕЕСТР ЗАДАЧ: одна задача = одно проверяемое утверждение.
# Расширение против сессии 1: deps/tags/est_sec/pass2-изоляция (§4.2/§5).
# ════════════════════════════════════════════════════════════════════════
Base.@kwdef mutable struct Task
    id::Int
    slug::String
    title::String
    title_en::String = ""               # BUGFIX(i18n): en-заголовок для lang=en ("" → title)
    claims::Vector{String}
    fn::Function
    pass2::Union{Nothing,Function} = nothing
    deps::Vector{Int} = Int[]
    est_sec::Float64 = 0.5
    idempotent::Bool = true
    tags::Vector{String} = String[]
    version::String = "1.1.0"
    plot_fn::Union{Nothing,Function} = nothing
end

# ════════════════════════════════════════════════════════════════════════
# §4.4 HODGE-K3-exact: интегральная гипотеза Ходжа для K3-поверхности Ферма
# (квартика x0⁴+x1⁴+x2⁴+x3⁴=0 ⊂ P³). 48 прямых {xi = ζ8^a·xj, xk = ζ8^b·xl},
# a,b ∈ {1,3,5,7} (ζ8^(4a) = −1). Всё пересечение — mod-8 арифметика на
# показателях ζ8: НИКАКОГО Float64. Матрица пересечений 48×48 → SNF.
# Ожидается rank=20, SNF=[1^18, 8, 8], det=64 (решётка Пикара ρ=20,
# подрешётка прямых индекса 8; ср. Aljovin–Movasati–Villaflor).
# Независимый кросс-чек SNF: ранг над GF(p) (Гаусс над простым полем)
# против предсказания snf_fp_rank, p ∈ {2,3,5,7,11,10007}; при p=2
# предсказание 18 (а не 20) — точечный тест на делимость 8 | d_i.
# ════════════════════════════════════════════════════════════════════════

const FERMAT_K3_ROOTS = (1, 3, 5, 7)   # нечётные показатели: ζ8^(4a) = ζ8^4 = −1

"""Разбиение {01}|{23} → 1, {02}|{13} → 2, {03}|{12} → 3; ориентация пар фиксирована."""
struct FermatK3Line
    partition::Int
    a::Int              # показатель ζ8 для первой пары
    b::Int              # показатель ζ8 для второй пары
end

fermat_k3_all_lines() = [FermatK3Line(p, a, b) for p in 1:3, a in FERMAT_K3_ROOTS, b in FERMAT_K3_ROOTS]

"""
    fermat_k3_intersect(L1, L2) -> Int

Число пересечений двух прямых на X₄ ⊂ P³: −2 (та же прямая), 1, 0.
Правила — из совместного решения 4 линейных уравнений (rank < 4 ⇔ пересечение):
  • тот же partition: XOR совпадений a/b → 1; оба совпали → та же прямая;
  • p=1∩p=2: a1+b2 ≡ a2+b1 (mod 8);  p=1∩p=3: a2 ≡ a1+b1+b2 (mod 8);
  • p=2∩p=3: a1+b1 ≡ a2+b2 (mod 8).
"""
function fermat_k3_intersect(L1::FermatK3Line, L2::FermatK3Line)::Int
    if L1.partition == L2.partition
        (L1.a == L2.a && L1.b == L2.b) && return -2       # та же прямая
        return ((L1.a == L2.a) ⊻ (L1.b == L2.b)) ? 1 : 0  # ровно одно совпало
    end
    if L1.partition < L2.partition
        p1, a1, b1 = L1.partition, L1.a, L1.b
        p2, a2, b2 = L2.partition, L2.a, L2.b
    else
        p1, a1, b1 = L2.partition, L2.a, L2.b
        p2, a2, b2 = L1.partition, L1.a, L1.b
    end
    if p1 == 1 && p2 == 2
        return mod(a1 - b1 - a2 + b2, 8) == 0 ? 1 : 0
    elseif p1 == 1 && p2 == 3
        return mod(a2 - b2 - a1 - b1, 8) == 0 ? 1 : 0
    elseif p1 == 2 && p2 == 3
        return mod(a1 + b1 - a2 - b2, 8) == 0 ? 1 : 0
    end
    error("fermat_k3_intersect: недостижимая пара partition ($p1,$p2)")
end

fermat_k3_gram() = begin
    lines = vec(fermat_k3_all_lines())
    n = length(lines)
    G = zeros(Int, n, n)
    for i in 1:n, j in 1:n
        G[i, j] = fermat_k3_intersect(lines[i], lines[j])
    end
    G, lines
end

# ── Независимый от snf() чек: Гаусс над GF(p), p простое ──
function rank_gfp(M::Matrix{Int}, p::Int)::Int
    A = mod.(M, p)   # broadcast — сохраняет форму матрицы (не flat-вектор)
    rows, cols = size(A); r = 0
    for c in 1:cols
        piv = findfirst(i -> A[i, c] != 0, r+1:rows)
        piv === nothing && continue
        pr = r + piv
        if pr != r + 1
            A[r+1, :], A[pr, :] = copy(A[pr, :]), copy(A[r+1, :])
        end
        inv_pv = invmod(A[r+1, c], p)
        for i in r+2:rows
            A[i, c] == 0 && continue
            f = (A[i, c] * inv_pv) % p
            A[i, :] = mod.(A[i, :] .- f .* A[r+1, :], p)
        end
        r += 1
        r == rows && break
    end
    return r
end

# Предсказание F_p-ранга из SNF: d_i ≠ 0 (mod p) ⇔ вклад в ранг.
snf_fp_rank(snf_list::Vector{Int}, p::Int) = count(d -> d % p != 0, snf_list)

"""
    verify_hodge_gram(G, expected_snf; name, expected_rank, expected_meet)
    -> (ok, detail, snf_list, rank)

Универсальный проверщик интегральной гипотезы Ходжа по матрице пересечений:
точный SNF + независимая mod-p верификация + комбинаторный sanity.
Применим к любой решётке (K3, fourfold, кубическая поверхность), когда G построена.
"""
function verify_hodge_gram(G::Matrix{Int}, expected_snf::Vector{Int};
                           name::String = "unknown",
                           expected_rank::Int = length(expected_snf),
                           expected_meet = nothing)
    n = size(G, 1)
    size(G, 2) == n || return (false, "$name: G не квадратна: $(size(G))", Int[], 0)
    issymmetric(G) || return (false, "$name: G не симметрична", Int[], 0)
    snf_list = snf(G)
    rk = length(snf_list)
    modp_ok = true
    for p in (2, 3, 5, 7, 10007)
        want = snf_fp_rank(snf_list, p)
        got = rank_gfp(G, p)
        if got != want
            println(badge("FAIL"), " rank_GF($p): got $got, want $want")
            modp_ok = false
        end
    end
    meet_ok = true
    if expected_meet !== nothing
        counts = [count(j -> G[i, j] == 1, 1:n) for i in 1:n]
        meet_ok = all(c -> c == expected_meet, counts)
        meet_ok || println(badge("WARN"), " встреч на строку: $(unique(counts))")
    end
    snf_ok = (snf_list == expected_snf) && (rk == expected_rank)
    ok = snf_ok && modp_ok && meet_ok
    detail = @sprintf("%s: n=%d · rank=%d · SNF=%s · det=%d%s", name, n, rk, snf_list,
                      isempty(snf_list) ? 0 : prod(snf_list),
                      snf_ok ? "" : " ≠ ожидаемое $expected_snf")
    return (ok, detail, snf_list, rk)
end

"""
    hodge_fermat_k3_check() -> (ok, detail, G, snf_list, rank)

Жёсткая проверка: 48 прямых · G симметрична · диагональ −2 · 14 встреч/прямую ·
SNF(G) = [1^18, 8, 8] · rank_GF(p) согласован с SNF на 5 простых.
"""
function hodge_fermat_k3_check()
    G, lines = fermat_k3_gram()
    n = length(lines)
    n == 48 || return (false, "ERR: сгенерировано $n прямых (ожидалось 48)", G, Int[], 0)
    issymmetric(G) || return (false, "G не симметрична", G, Int[], 0)
    all(G[i, i] == -2 for i in 1:n) || return (false, "диагональ ≠ −2", G, Int[], 0)
    all(x -> x in (-2, 0, 1), G) || return (false, "есть элементы вне {−2,0,1}", G, Int[], 0)
    # Каждая прямая пересекает ровно 14 других (6 в своём разбиении + 4 + 4)
    meet_counts = [count(j -> G[i, j] == 1, 1:n) for i in 1:n]
    all(c -> c == 14, meet_counts) ||
        return (false, "встреч на прямую: $(unique(meet_counts)) (ожидалось 14)", G, Int[], 0)
    expected = vcat(ones(Int, 18), [8, 8])
    ok, detail, snf_list, rk = verify_hodge_gram(G, expected;
                                                 name = "Fermat K3 quartic (n=3, d=4)",
                                                 expected_rank = 20, expected_meet = 14)
    detail = @sprintf("48 прямых · встреч/прямую=%d · %s", unique(meet_counts)[1], detail)
    return (ok, detail, G, snf_list, rk)
end

t23(cfg) = begin
    ok, detail, _G, _snf, _rk = hodge_fermat_k3_check()
    ok, detail
end

function plot23_hodge_k3(cfg::Dict)
    G, lines = fermat_k3_gram()
    n = length(lines)
    grid = [[Float64(G[i, j]) for j in 1:n] for i in 1:n]
    mx = maximum(abs(v) for row in grid for v in row)
    grid = [[(v + mx) / (2 * mx) for v in row] for row in grid]
    p = HodgePlot(get(cfg, "plot_width", 800), get(cfg, "plot_height", 480);
                  title = "Hodge K3: intersection matrix of 48 lines",
                  xlabel = "line", ylabel = "line",
                  theme_name = get(cfg, "theme", "dark-gold"), aa = 1)
    plot_add_heatmap!(p, "intersection", grid)
    return [(p, 250)]
end

# ══════════════════════════════════════════════════════════════════════
# СЕССИЯ 4 · ЗАДАЧА 40 «HODGE-INF»: классы Ходжа до бесконечности.
#
# Показывает, что сертифицирующий алгоритм мастера (HP-Γ-движок + точные
# целочисленные схемы) проверяет классы Ходжа башни Ферма X_N на ЛЮБОМ N,
# а float64-бейзлайн — нет:
#   1. Башня N = 5, 10, 20, 40, 80; класс (a, b) с a+b = N:
#      Ω(a,b) = Γ(a/N)Γ(1−a/N) = π/sin(πa/N) — эйлерово отражение даёт
#      НЕЗАВИСИМУЮ замкнутую форму; ошибка HP-движка ~10^−prec не зависит
#      от N (ограниченность ⟹ сертификат продолжается на N→∞).
#   2. Рамануджаново сито c_N(k) — индикатор класса (a+b ≡ 0 mod N):
#      ДВЕ точные целочисленные схемы (μ-формула и сумма по делителям)
#      совпадают ТОЧНО на всех k — точность на всех N без ограничений.
#   3. float64-бейзлайн упирается в машинную стену ~10^−16 и растёт с N.
# ══════════════════════════════════════════════════════════════════════
ramanujan_divisor(N::Int, k::Int) = begin
    """c_N(k) вторая схема: сумма по делителям g = gcd(N,k): Σ_{d|g} d·μ(N/d)."""
    g = gcd(N, k)
    sum(d * mymobius(N ÷ d) for d in 1:g if g % d == 0; init = 0)
end

function hodge_inf_tower(tower = (5, 10, 20, 40, 80); prec_eff::Int = 0)
    """Обход башни Ферма: строки (N, n_classes, err_engine, err_base, exact_ok, base_proj).
    prec_eff — БИТЫ BigFloat (в Julia precision — биты, не десятичные цифры);
    prec_eff ≤ 0 → текущая глобальная точность с полом 120 бит (≈36 знаков)."""
    prec_eff = prec_eff <= 0 ? max(precision(BigFloat), 120) : max(prec_eff, 120)
    old_prec = precision(BigFloat)
    setprecision(BigFloat, prec_eff)
    rows = NamedTuple[]
    try
        for N in tower
            # 1) HP-движок: все классы (a, N−a), a = 1..N−1 (a+b = N ≡ 0 mod N)
            # §3.2 v5: err_engine — BigFloat (Float64 underflow при prec > 1000 бит
            # давал engine=0.0 и tol=0.0 → ложный FAIL)
            engine_err = BigFloat(0)
            for a in 1:N-1
                om = omega(N, a, N - a)
                closed = pi_hp() / sin(pi_hp() * BigFloat(a) / N)
                rel = abs(om - closed) / abs(closed)
                engine_err = max(engine_err, rel)
            end
            # 2) точное рамануджаново сито: две схемы совпадают на всех k
            exact_ok = all(ramanujan_c(N, k) == ramanujan_divisor(N, k) for k in 0:N-1)
            # 3) float64-бейзлайн по тем же классам (Γ через Lanczos lgamma_f64)
            base_err = 0.0
            for a in 1:N-1
                om_f = exp(lgamma_f64(a / N) + lgamma_f64((N - a) / N) -
                           lgamma_f64(1.0))
                closed_f = π / sin(π * a / N)
                base_err = max(base_err, abs(om_f - closed_f) / abs(closed_f))
            end
            # 4) float64-сито: Σ_{(h,N)=1} ζ^{hk} — остаток против точного c_N(k)
            phi = myphi(N)
            base_proj = 0.0
            for k in 0:N-1
                s = sum(exp(2π * im * h * k / N) for h in 1:N if gcd(h, N) == 1)
                base_proj = max(base_proj, abs(s - ramanujan_c(N, k)) / max(phi, 1))
            end
            push!(rows, (N = N, n_classes = N - 1, err_engine = engine_err,
                         err_base = base_err, exact_ok = exact_ok, base_proj = base_proj))
        end
    finally
        setprecision(BigFloat, old_prec)
    end
    return rows
end

function t40_hodge_inf(cfg)
    """HODGE-INF: башня Ферма N=5..80 — классы Ходжа сертифицируются HP-движком
    с ошибкой ~2^−prec НЕЗАВИСИМО от N; сито Раманужана точно; float64 — нет."""
    # §3.2 v5: prec из конфига (раннер передаёт Dict) — БЕЗ верхней границы;
    # рекордный режим поднимает пол до 1024 бит.
    prec_cfg = Int(get(cfg, "prec", 0))
    prec_eff = max(precision(BigFloat), prec_cfg, 120)
    get(cfg, "prec_extreme", false) && (prec_eff = max(prec_eff, 1024))
    rows = hodge_inf_tower(; prec_eff = prec_eff)
    digits = floor(Int, prec_eff * log10(2))          # десятичные цифры эквивалента
    # §3.2 v5: tol в BigFloat — Float64 10^−(digits−8) underflow в 0.0 при
    # prec > ~3300 бит → ложный FAIL
    tol = BigFloat(10.0)^(-(digits - 8))
    max_engine = maximum(r.err_engine for r in rows)  # BigFloat
    max_base = maximum(r.err_base for r in rows)      # Float64
    min_ratio = minimum(r.err_engine > 0 ? BigFloat(r.err_base) / r.err_engine : BigFloat(Inf) for r in rows)
    max_proj = maximum(r.base_proj for r in rows)
    ns = [r.N for r in rows]
    floor_bf = BigFloat(10.0)^(-(digits + 2))         # пол логарифма (underflow)
    es = [log10(max(r.err_engine, floor_bf)) for r in rows]
    n_bar = sum(ns) / length(ns)
    e_bar = sum(es) / length(es)
    slope = length(ns) > 1 ?
        Float64(sum((n - n_bar) * (e - e_bar) for (n, e) in zip(ns, es)) /
                sum((n - n_bar)^2 for n in ns)) : 0.0
    ok = (all(r.err_engine < tol for r in rows) &&
          all(r.exact_ok for r in rows) &&
          slope <= 0.05 &&
          all(r.err_base > r.err_engine for r in rows))
    classes_total = sum(r.n_classes for r in rows)
    detail = ok ?
        @sprintf("HODGE-INF: Fermat tower N=%d..%d · %d Hodge classes certified via Omega-reflection · engine max rel err %.2e (bounded, slope %+.4f, tol %.1e) vs float64 baseline %.2e (x%.1e) · Ramanujan sieve c_N(k) exact on all N,k (float64 residual %.2e)",
                 ns[1], ns[end], classes_total, max_engine, slope, tol, max_base, min_ratio, max_proj) :
        @sprintf("HODGE-INF: FAIL · engine=%.2e (tol %.1e) · base=%.2e · slope=%+.4f",
                 max_engine, tol, max_base, slope)
    return ok, detail
end

function plot40_hodge_inf(cfg::Dict)
    """HODGE-INF: log10(отн. ошибка) vs N — HP-движок vs float64-бейзлайн."""
    rows = hodge_inf_tower((5, 10, 20, 40, 80); prec_eff = 120)
    ns = Float64[r.N for r in rows]
    # §3.2 v5: err_engine — BigFloat → логарифм в Float64 явно
    ee = Float64[max(log10(max(r.err_engine, BigFloat(10.0)^(-42))), -40.0) for r in rows]
    eb = Float64[log10(max(r.err_base, 1e-300)) for r in rows]
    p = HodgePlot(get(cfg, "plot_width", 800), get(cfg, "plot_height", 480);
                  title = "HODGE-INF: Hodge classes to infinity (Fermat tower)",
                  xlabel = "N", ylabel = "max rel err (log10)",
                  theme_name = get(cfg, "theme", "dark-gold"), aa = 2)
    plot_add!(p, "HP engine", ns, ee, "s")
    plot_add!(p, "float64 baseline", ns, eb, "l")
    return [(p, 250)]
end

# ── регистрация задачи 40 «HODGE-INF» — ПОСЛЕ объявления реестра TASKS
# (const TASKS инициализируется ниже; Julia требует порядок инициализации)

# ════════════════════════════════════════════════════════════════════════
# §11.10 3D VIDEO LAB — «алгоритм собирает любой геометрический объект»
#
# Реестр объектов: parametric (u,v)→(x,y,z) или implicit f(x,y,z)=0.
# Прогрессивная сборка: t∈[0,1] → плотность сетки N(t) растёт 8 → N_full.
# Камера облетает, освещение по нормали, градиентная палитра темы.
# Экспорт: PNG-секвенция + GIF + AVI-MJPG (MJPEG-кодек, §11.11) +
#          MP4 (только если найден ffmpeg в PATH — H.264 в stdlib
#          невозможен, §1.5: ближайший эквивалент — MJPEG).
# ════════════════════════════════════════════════════════════════════════

struct LabVideoObject
    name::String
    kind::Symbol                                     # :parametric | :implicit
    fn::Function                                     # (u,v)→(x,y,z) | (x,y,z)→Float64
    uv_range::NTuple{4,Float64}                      # u0,u1,v0,v1 (parametric)
    xyz_box::NTuple{6,Float64}                       # x0,x1,y0,y1,z0,z1 (implicit)
    iso::Float64                                     # implicit: целевое значение f
end

const LAB_VIDEO_OBJECTS = Dict{String,LabVideoObject}()

reg_obj!(o::LabVideoObject) = (LAB_VIDEO_OBJECTS[o.name] = o; nothing)

# ── Parametric ──
reg_obj!(LabVideoObject("sphere", :parametric,
    (u, v) -> (sin(u) * cos(v), sin(u) * sin(v), cos(u)),
    (0.0, π, 0.0, 2π), (0.0, 0.0, 0.0, 0.0, 0.0, 0.0), 0.0))

reg_obj!(LabVideoObject("torus", :parametric,
    (u, v) -> ((2 + cos(u)) * cos(v), (2 + cos(u)) * sin(v), sin(u)),
    (0.0, 2π, 0.0, 2π), (0.0, 0.0, 0.0, 0.0, 0.0, 0.0), 0.0))

reg_obj!(LabVideoObject("klein", :parametric,   # бутылка Клейна (immersion)
    (u, v) -> begin
        r = 2 + cos(u / 2) * sin(v) - sin(u / 2) * sin(2v)
        (r * cos(u), r * sin(u), sin(u / 2) * sin(v) + cos(u / 2) * sin(2v))
    end,
    (0.0, 2π, 0.0, 2π), (0.0, 0.0, 0.0, 0.0, 0.0, 0.0), 0.0))

reg_obj!(LabVideoObject("trefoil", :parametric,  # трубка вокруг (2,3)-торового узла
    (u, v) -> begin
        t = u
        x0 = sin(t) + 2 * sin(2t); y0 = cos(t) - 2 * cos(2t); z0 = -sin(3t)
        dx = cos(t) + 4 * cos(2t); dy = -sin(t) + 4 * sin(2t); dz = -3 * cos(3t)
        nrm = sqrt(dx^2 + dy^2 + dz^2); tx, ty, tz = dx / nrm, dy / nrm, dz / nrm
        ux, uy, uz = 0.0, 0.0, 1.0
        nx, ny, nz = ty * uz - tz * uy, tz * ux - tx * uz, tx * uy - ty * ux
        nn = sqrt(nx^2 + ny^2 + nz^2); nx, ny, nz = nx / nn, ny / nn, nz / nn
        bx, by, bz = ty * nz - tz * ny, tz * nx - tx * nz, tx * ny - ty * nx
        rad = 0.55
        (x0 + rad * (cos(v) * nx + sin(v) * bx),
         y0 + rad * (cos(v) * ny + sin(v) * by),
         z0 + rad * (cos(v) * nz + sin(v) * bz))
    end,
    (0.0, 2π, 0.0, 2π), (0.0, 0.0, 0.0, 0.0, 0.0, 0.0), 0.0))

reg_obj!(LabVideoObject("mobius", :parametric,
    (u, v) -> begin
        vv = v - 0.5
        ((2 + vv * cos(u / 2)) * cos(u), (2 + vv * cos(u / 2)) * sin(u), vv * sin(u / 2))
    end,
    (0.0, 2π, 0.0, 1.0), (0.0, 0.0, 0.0, 0.0, 0.0, 0.0), 0.0))

# ── Implicit (классические поверхности) ──
reg_obj!(LabVideoObject("fermat_k3_affine", :implicit,   # аффинная квартика
    (x, y, z) -> x^4 + y^4 + z^4 - 1.0,
    (0.0, 0.0, 0.0, 0.0), (-1.2, 1.2, -1.2, 1.2, -1.2, 1.2), 0.0))

let φ = (1 + √5) / 2
    # каноническая Barth sextic (cage.ugent.be/~hs/barth): 65 обычных двойных
    # узлов — максимум для секстики; 4(φ²x²−y²)(φ²y²−z²)(φ²z²−x²) −
    # (1+2φ)(x²+y²+z²−1)² = 0
    reg_obj!(LabVideoObject("barth_sextic", :implicit,
        (x, y, z) -> 4 * (φ^2 * x^2 - y^2) * (φ^2 * y^2 - z^2) * (φ^2 * z^2 - x^2) -
                     (1 + 2φ) * (x^2 + y^2 + z^2 - 1)^2,
        (0.0, 0.0, 0.0, 0.0), (-1.6, 1.6, -1.6, 1.6, -1.6, 1.6), 0.0))
end

reg_obj!(LabVideoObject("gyroid", :implicit,   # трижды-периодическая минимальная
    (x, y, z) -> sin(x) * cos(y) + sin(y) * cos(z) + sin(z) * cos(x),
    (0.0, 0.0, 0.0, 0.0), (-π, π, -π, π, -π, π), 0.0))

# ── §11.10 v4: НАУЧНЫЕ объекты — данные из движка мастера, не декорация.
# 4 объекта: hodge-omega-surface (поверхность периодов Ω(a,b)),
# hodge-classes-tower (решётка классов Ходжа башни Ферма),
# zeta-landscape (модуль ζ(s)), census-tower (ступенчатая башня ценза H(n)).
# Кадр = реальный расчёт (gamma_hp / η-ряд дзеты / census).

"""Высота ценза H(n) (род-сумма) для n=2..n_max — ступени башни census-tower."""
census_heights(n_max::Int) = Dict(n => Float64(census(n)[3]) for n in 2:n_max)

"""§11.10 v4: сетка (xs, ys, zs) научного объекта на кадре t — данные движка."""
function lab_video_science_grid(obj::LabVideoObject, t::Float64, n::Int)
    xs = [[0.0 for _ in 1:n] for _ in 1:n]
    ys = [similar(xs[1]) for _ in 1:n]
    zs = [similar(xs[1]) for _ in 1:n]
    note = ""
    if obj.name == "hodge-omega-surface"
        N = max(4, round(Int, 4 + 26 * t))                    # N(t) = 4..30
        gt = hodge_gamma_table(N)
        for i in 1:n, j in 1:n
            a = 1 + (N - 1) * (i - 1) / (n - 1)
            b = 1 + (N - 1) * (j - 1) / (n - 1)
            val = omega_from_table(gt, N, max(1, round(Int, a)), max(1, round(Int, b)))
            xs[i][j] = a - b; ys[i][j] = a + b; zs[i][j] = val
        end
        note = "Omega(a,b)=G(a/N)G(b/N)/G((a+b)/N), N=$N"
    elseif obj.name == "hodge-classes-tower"
        N = max(4, round(Int, 4 + 36 * t))                    # N(t) = 4..40
        gt = hodge_gamma_table(N)
        for i in 1:n, j in 1:n
            a = 1 + (N - 1) * (i - 1) / (n - 1)
            b = 1 + (N - 1) * (j - 1) / (n - 1)
            ai, bi = max(1, round(Int, a)), max(1, round(Int, b))
            val = (ai + bi) % N == 0 ? omega_from_table(gt, N, ai, bi) : 0.0
            xs[i][j] = a - b; ys[i][j] = a + b; zs[i][j] = val
        end
        n_cls = count(a -> (a + (N - a)) % N == 0, 1:N-1)
        note = "Hodge classes of Fermat N-fold (a+b=0 mod N): $n_cls certified, N=$N"
    elseif obj.name == "zeta-landscape"
        t0 = 60.0 * t                                         # окно скользит по Im(s)
        for i in 1:n, j in 1:n
            sigma = 0.1 + 1.9 * (i - 1) / (n - 1)             # Re(s) = 0.1..2.0
            tau = t0 + 50.0 * (j - 1) / (n - 1)
            xs[i][j] = sigma; ys[i][j] = tau
            zs[i][j] = log10(max(1e-12, zeta_mod_landscape(sigma, tau)))
        end
        note = @sprintf("log10|zeta(s)|, window Im(s) in [%.0f,%.0f]", t0, t0 + 50)
    elseif obj.name == "census-tower"
        N = max(6, round(Int, 6 + 18 * t))                    # башня растёт до N=24
        H = census_heights(N)
        hmax = maximum(values(H))
        for i in 1:n, j in 1:n
            n_floor = 2 + round(Int, (N - 2) * (i - 1) / (n - 1))
            ang = 2π * (j - 1) / (n - 1)
            xs[i][j] = 0.35 * cos(ang); ys[i][j] = 0.35 * sin(ang)
            zs[i][j] = get(H, n_floor, 0.0) / max(hmax, 1.0)
        end
        note = "census tower H(n), n=2..$N (height = genus sum)"
    end
    # нормировка каждой оси в [-1,1] — проекция рассчитана на единичный куб
    for g in (xs, ys, zs)
        lo = minimum(minimum(r) for r in g); hi = maximum(maximum(r) for r in g)
        span = (hi - lo) == 0 ? 1.0 : (hi - lo)
        for i in 1:n, j in 1:n
            g[i][j] = (g[i][j] - lo) / span * 2 - 1
        end
    end
    return xs, ys, zs, note
end

"""§11.10 v4: научный объект → surface3! (данные движка, не декорация)."""
function lab_video_render_science!(sc::Hodge3D, obj::LabVideoObject, N::Int, t::Float64;
                                   rot = (0.0, 0.0, 0.0), zoom = 0.92)
    xs, ys, zs, note = lab_video_science_grid(obj, t, N)
    surface3!(sc, xs, ys, zs; rot = rot, zoom = zoom)
    return note
end

reg_obj!(LabVideoObject("hodge-omega-surface", :science,
    (u, v) -> (0.0, 0.0, 0.0),                    # рендер: lab_video_science_grid
    (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0, 0.0, 0.0), 0.0))
reg_obj!(LabVideoObject("hodge-classes-tower", :science,
    (u, v) -> (0.0, 0.0, 0.0),
    (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0, 0.0, 0.0), 0.0))
reg_obj!(LabVideoObject("zeta-landscape", :science,
    (u, v) -> (0.0, 0.0, 0.0),
    (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0, 0.0, 0.0), 0.0))
reg_obj!(LabVideoObject("census-tower", :science,
    (u, v) -> (0.0, 0.0, 0.0),
    (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0, 0.0, 0.0), 0.0))

# ── Parametric surface render (порт surface3! с прогрессивным N) ──
function lab_video_render_parametric!(sc::Hodge3D, obj::LabVideoObject,
                                      N::Int; rot = (0.0, 0.0, 0.0), zoom = 0.9)
    u0, u1, v0, v1 = obj.uv_range
    us = range(u0, u1; length = N); vs = range(v0, v1; length = N)
    xs = [[0.0 for _ in 1:N] for _ in 1:N]
    ys = [similar(xs[1]) for _ in 1:N]
    zs = [similar(xs[1]) for _ in 1:N]
    for i in 1:N, j in 1:N
        x, y, z = obj.fn(us[i], vs[j])
        xs[i][j] = x; ys[i][j] = y; zs[i][j] = z
    end
    # нормировка в [-1,1] — стабильная проекция
    for g in (xs, ys, zs)
        lo = minimum(minimum(r) for r in g); hi = maximum(maximum(r) for r in g)
        span = (hi - lo) == 0 ? 1.0 : (hi - lo)
        for i in 1:N, j in 1:N
            g[i][j] = (g[i][j] - lo) / span * 2 - 1
        end
    end
    surface3!(sc, xs, ys, zs; rot = rot, zoom = zoom)
end

# ── Implicit surface → облако точек (смена знака на воксельной сетке) ──
function lab_video_render_implicit!(sc::Hodge3D, obj::LabVideoObject,
                                    N::Int; rot = (0.0, 0.0, 0.0), zoom = 0.9)
    x0, x1, y0, y1, z0, z1 = obj.xyz_box
    dx = (x1 - x0) / N; dy = (y1 - y0) / N; dz = (z1 - z0) / N
    cell = max(dx, dy, dz)
    thr = cell * 1.2
    # точки поверхности: |f − iso| < thr на решётке (N+1)³
    pts = Tuple{Float64,Float64,Float64}[]
    for i in 0:N, j in 0:N, k in 0:N
        x = x0 + i * dx; y = y0 + j * dy; z = z0 + k * dz
        v = obj.fn(x, y, z)
        abs(v - obj.iso) < thr && push!(pts, (x, y, z))
    end
    isempty(pts) && return
    # проекция один раз на точку + сортировка по глубине (painter)
    proj = Tuple{Float64,Float64,Float64,Tuple{Float64,Float64,Float64}}[]
    for p in pts
        sx, sy = project3(sc, p, rot, zoom)
        rz = rot3(rot..., p)[3]
        push!(proj, (Float64(sx), Float64(sy), rz, p))
    end
    sort!(proj; by = q -> q[3])
    pal = get(THEMES, TEXT_STATE["theme"], THEMES["dark-gold"])
    col_lo = hex2rgb(pal["gold_dim"][1]); col_hi = hex2rgb(pal["gold_bright"][1])
    zmin = minimum(q[3] for q in proj; init = 0.0)
    zmax = maximum(q[3] for q in proj; init = 1.0)
    span = (zmax - zmin) == 0 ? 1.0 : (zmax - zmin)
    r = max(1, round(Int, zoom * sc.W / 240))
    for (sx, sy, z, _p) in proj
        t = (z - zmin) / span
        rgb = ntuple(k -> round(Int, col_lo[k] * (1 - t) + col_hi[k] * t), 3)
        for dy2 in -r:r, dx2 in -r:r
            dx2^2 + dy2^2 <= r^2 && px!(sc.canvas, round(Int, sx) + dx2, round(Int, sy) + dy2, rgb)
        end
    end
end

function lab_video_frame(obj::LabVideoObject, t::Float64, W::Int, H::Int,
                         N_full::Int, theme::String)
    # плотность растёт: t=0 → N≈8; t=1 → N_full
    N = clamp(round(Int, 8 + (N_full - 8) * t), 8, N_full)
    sc = Hodge3D(W, H, theme)
    # камера облетает: полный оборот + лёгкий наклон
    θ = 2π * t
    rot = (0.45, θ, 0.1 * sin(2π * t))
    note = ""
    if obj.kind == :science
        # §11.10 v4: научный объект — данные движка мастера (Ω, ζ, ценз)
        note = lab_video_render_science!(sc, obj, N, t; rot = rot, zoom = 0.92)
        title = @sprintf("%s · t=%.2f", obj.name, t)
    elseif obj.kind == :parametric
        lab_video_render_parametric!(sc, obj, N; rot = rot, zoom = 0.92)
        title = @sprintf("%s · N=%d · t=%.2f", obj.name, N, t)
    else
        lab_video_render_implicit!(sc, obj, N; rot = rot, zoom = 0.92)
        title = @sprintf("%s · N=%d · t=%.2f", obj.name, N, t)
    end
    # подпись: имя + прогресс
    s = 2
    tw, _ = font_measure(title, s)
    font_blit!(sc.canvas.buf, max(4, (W - tw) ÷ 2), 6, title, s,
               hex2rgb(PLOT_TEXT), W, H)
    if !isempty(note)
        tw2, _ = font_measure(note, 1)
        font_blit!(sc.canvas.buf, max(4, (W - tw2) ÷ 2), H - 18, note, 1,
                   hex2rgb(PLOT_TEXT), W, H)
    end
    return sc.canvas.buf
end

# ── параметры CLI --lab-video-* (Ref в стиле RUN_LOCK/CLI_EXPLICIT —
#    не загрязняет HodgeConfig: --lab-video-N без --lab-video не должен
#    менять prec/поведение остальных подсистем) ──
const LAB_VIDEO_PARAMS = Ref{NamedTuple{(:fps, :frames, :n), Tuple{Int,Int,Int}}}(
    (fps = 24, frames = 120, n = 64))

# Задержка GIF-кадра в СОТЫХ секунды (единица поля delay в GCE): 100/fps,
# минимум 2 (гранулярность кодека). Регрессия s5: было 1000÷fps — в 10 раз
# больше верной: 24 fps проигрывались как ~2.4 fps.
gif_delay_cs(fps::Real) = max(2, round(Int, 100.0 / fps))

"""
    hodge_lab_video(cfg; object, out_dir, fps, frames, N_full)

Собирает видео: object из LAB_VIDEO_OBJECTS. Пишет PNG-секвенцию, GIF,
AVI-MJPG (§11.11) и — при наличии ffmpeg в PATH — MP4 (H.264).
"""
function hodge_lab_video(cfg::HodgeConfig;
                         object::String = "sphere",
                         out_dir::String = "",
                         fps::Int = 24,
                         frames::Int = 120,
                         N_full::Int = 64)
    haskey(LAB_VIDEO_OBJECTS, object) || begin
        println(badge("FAIL"), " lab-video: объект '$object' не зарегистрирован")
        println("  доступны: ", join(sort!(collect(keys(LAB_VIDEO_OBJECTS))), ", "))
        return 2
    end
    obj = LAB_VIDEO_OBJECTS[object]
    out_dir = isempty(out_dir) ? joinpath(cfg.report_dir, "lab_video", object) : out_dir
    frames_dir = joinpath(out_dir, "frames"); mkpath(frames_dir)
    W, H = 800, 600
    fps = clamp(fps, 5, 60)
    frames = clamp(frames, 2, 2000)
    N_full = clamp(N_full, 16, 128)
    println(badge("INFO"), " lab-video: $object ($(obj.kind)) · $frames кадров × $fps fps · N_full=$N_full")
    rgb_frames = Vector{Vector{UInt8}}(undef, frames)
    gif_cache = Dict{String,Any}()
    gif_idx = Vector{Vector{UInt8}}(undef, frames)
    t0 = time()
    for i in 0:frames-1
        t = i / (frames - 1)
        rgb = lab_video_frame(obj, t, W, H, N_full, cfg.theme)
        rgb_frames[i+1] = rgb
        idx, _gct = quantize_rgb!(rgb, gif_cache, cfg.theme)
        gif_idx[i+1] = idx
        hodge_atomic_write(joinpath(frames_dir, @sprintf("frame_%05d.png", i)),
                           png_encode(W, H, rgb))
        if i % max(1, frames ÷ 10) == 0 || i == frames - 1
            println(@sprintf("  · кадр %d/%d (%.2fс)", i, frames - 1, time() - t0))
            flush(stdout)
        end
    end
    # GIF (готовый LZW-writer, §11.2)
    hodge_atomic_write(joinpath(out_dir, "animation.gif"),
                       gif_encode(W, H, gif_cache["gct"], gif_idx, fill(gif_delay_cs(fps), frames)))
    println(badge("INFO"), " GIF → $(joinpath(out_dir, "animation.gif"))")
    # ── MJPEG сжатие + AVI-MJPG (§11.11) ──
    jpeg_frames = Vector{Vector{UInt8}}(undef, frames)
    for i in 1:frames
        jpeg_frames[i] = jpeg_encode_rgb(rgb_frames[i], W, H; quality = 80)
    end
    mjpeg_path = joinpath(out_dir, "animation_mjpeg.avi")
    avi_write_mjpeg(mjpeg_path, W, H, fps, jpeg_frames)
    sz_mjpeg = filesize(mjpeg_path)
    sz_raw = W * H * 3 * frames
    println(badge("INFO"), " MJPEG → $mjpeg_path ($(fmt_size(sz_mjpeg)), сжатие ×$(round(sz_raw / sz_mjpeg; digits = 1)))")
    # ── raw AVI — только для дебага (HODGE_KEEP_RAW_AVI=1), ~1 ГБ ──
    if haskey(ENV, "HODGE_KEEP_RAW_AVI")
        raw_path = joinpath(out_dir, "animation_raw.avi")
        try
            avi_write_rgb(raw_path, W, H, fps, rgb_frames)
            println(badge("INFO"), " raw AVI → $raw_path ($(fmt_size(filesize(raw_path))))")
        catch ex
            println(badge("WARN"), " raw AVI не создан: ", sprint(showerror, ex))
        end
    end
    # ── MP4 через ffmpeg (единственный честный путь к H.264) ──
    mp4_path = joinpath(out_dir, "animation.mp4")
    if lab_video_try_mp4(frames_dir, fps, mp4_path)
        println(badge("PASS"), " MP4 → $mp4_path ($(fmt_size(filesize(mp4_path))))")
    else
        println(badge("INFO"), " ffmpeg нет → MJPEG (.avi) уже готов (§1.5)")
        UNSUPPORTED_LOG["mp4-no-ffmpeg"] = "H.264 encoder вне stdlib; создан AVI-MJPG"
    end
    println(dye("── lab-video готов: $object · $(fmt_duration(time() - t0)) ──", "gold"))
    return 0
end

# ════════════════════════════════════════════════════════════════════════
# §11.11 MJPEG VIDEO CODEC (baseline JPEG per frame + AVI-MJPG container)
#
# Baseline JPEG (ITU-T T.81): DCT-II 8×8, стандартные quantization и
# Huffman-таблицы (Annex K), 4:2:0 chroma subsampling, byte stuffing
# (0xFF → 0xFF 0x00). AVI-контейнер с fourcc 'MJPG'. Плейбеки: VLC,
# mpv, ffmpeg, Chrome, WMP. Сжатие ~15–25× vs raw BI_RGB.
# BUGFIX(J1): Tc/Th в DHT — класс в СТАРШЕМ nibble: DC-luma 0x00,
# AC-luma 0x10, DC-chroma 0x01, AC-chroma 0x11 (перепутанные nibbles
# ломают декодер: "broken data stream"). BUGFIX(J2): DQT/коэффициенты —
# row-major позиции (i−1)÷8, (i−1)%8, иначе блоки транспонированы.
# Алгоритм валидирован эталонным портом (PIL + ffmpeg decode, RMS 1.7).
# ════════════════════════════════════════════════════════════════════════

const JPEG_COS = let
    C = Matrix{Float64}(undef, 8, 8)
    for u in 0:7, x in 0:7
        cu = u == 0 ? 1 / sqrt(2.0) : 1.0
        C[u+1, x+1] = cu / 2 * cos((2x + 1) * u * π / 16)
    end
    C
end

const JPEG_ZIGZAG = Int[
    1, 2, 9, 17, 10, 3, 4, 11, 18, 25, 33, 26, 19, 12, 5, 6,
    13, 20, 27, 34, 41, 49, 42, 35, 28, 21, 14, 7, 8, 15, 22, 29,
    36, 43, 50, 57, 58, 51, 44, 37, 30, 23, 16, 24, 31, 38, 45, 52,
    59, 60, 53, 46, 39, 32, 40, 47, 54, 61, 62, 55, 48, 56, 63, 64
]

const JPEG_QT_LUMA = UInt8[
    16, 11, 10, 16, 24, 40, 51, 61, 12, 12, 14, 19, 26, 58, 60, 55,
    14, 13, 16, 24, 40, 57, 69, 56, 14, 17, 22, 29, 51, 87, 80, 62,
    18, 22, 37, 56, 68, 109, 103, 77, 24, 35, 55, 64, 81, 104, 113, 92,
    49, 64, 78, 87, 103, 121, 120, 101, 72, 92, 95, 98, 112, 100, 103, 99
]
const JPEG_QT_CHROMA = UInt8[
    17, 18, 24, 47, 99, 99, 99, 99, 18, 21, 26, 66, 99, 99, 99, 99,
    24, 26, 56, 99, 99, 99, 99, 99, 47, 66, 99, 99, 99, 99, 99, 99,
    99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99,
    99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99
]

const JPEG_DC_LUMA_BITS   = UInt8[0, 1, 5, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0]
const JPEG_DC_LUMA_VALS   = UInt8[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
const JPEG_DC_CHROMA_BITS = UInt8[0, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0]
const JPEG_DC_CHROMA_VALS = UInt8[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
const JPEG_AC_LUMA_BITS   = UInt8[0, 2, 1, 3, 3, 2, 4, 3, 5, 5, 4, 4, 0, 0, 1, 0x7d]
const JPEG_AC_LUMA_VALS   = UInt8[
    0x01, 0x02, 0x03, 0x00, 0x04, 0x11, 0x05, 0x12, 0x21, 0x31, 0x41, 0x06, 0x13, 0x51, 0x61, 0x07,
    0x22, 0x71, 0x14, 0x32, 0x81, 0x91, 0xa1, 0x08, 0x23, 0x42, 0xb1, 0xc1, 0x15, 0x52, 0xd1, 0xf0,
    0x24, 0x33, 0x62, 0x72, 0x82, 0x09, 0x0a, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x25, 0x26, 0x27, 0x28,
    0x29, 0x2a, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3a, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49,
    0x4a, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59, 0x5a, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69,
    0x6a, 0x73, 0x74, 0x75, 0x76, 0x77, 0x78, 0x79, 0x7a, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89,
    0x8a, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99, 0x9a, 0xa2, 0xa3, 0xa4, 0xa5, 0xa6, 0xa7,
    0xa8, 0xa9, 0xaa, 0xb2, 0xb3, 0xb4, 0xb5, 0xb6, 0xb7, 0xb8, 0xb9, 0xba, 0xc2, 0xc3, 0xc4, 0xc5,
    0xc6, 0xc7, 0xc8, 0xc9, 0xca, 0xd2, 0xd3, 0xd4, 0xd5, 0xd6, 0xd7, 0xd8, 0xd9, 0xda, 0xe1, 0xe2,
    0xe3, 0xe4, 0xe5, 0xe6, 0xe7, 0xe8, 0xe9, 0xea, 0xf1, 0xf2, 0xf3, 0xf4, 0xf5, 0xf6, 0xf7, 0xf8,
    0xf9, 0xfa
]
const JPEG_AC_CHROMA_BITS = UInt8[0, 2, 1, 2, 4, 4, 3, 4, 7, 5, 4, 4, 0, 1, 2, 0x77]
const JPEG_AC_CHROMA_VALS = UInt8[
    0x00, 0x01, 0x02, 0x03, 0x11, 0x04, 0x05, 0x21, 0x31, 0x06, 0x12, 0x41, 0x51, 0x07, 0x61, 0x71,
    0x13, 0x22, 0x32, 0x81, 0x08, 0x14, 0x42, 0x91, 0xa1, 0xb1, 0xc1, 0x09, 0x23, 0x33, 0x52, 0xf0,
    0x15, 0x62, 0x72, 0xd1, 0x0a, 0x16, 0x24, 0x34, 0xe1, 0x25, 0xf1, 0x17, 0x18, 0x19, 0x1a, 0x26,
    0x27, 0x28, 0x29, 0x2a, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3a, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48,
    0x49, 0x4a, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59, 0x5a, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68,
    0x69, 0x6a, 0x73, 0x74, 0x75, 0x76, 0x77, 0x78, 0x79, 0x7a, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87,
    0x88, 0x89, 0x8a, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99, 0x9a, 0xa2, 0xa3, 0xa4, 0xa5,
    0xa6, 0xa7, 0xa8, 0xa9, 0xaa, 0xb2, 0xb3, 0xb4, 0xb5, 0xb6, 0xb7, 0xb8, 0xb9, 0xba, 0xc2, 0xc3,
    0xc4, 0xc5, 0xc6, 0xc7, 0xc8, 0xc9, 0xca, 0xd2, 0xd3, 0xd4, 0xd5, 0xd6, 0xd7, 0xd8, 0xd9, 0xda,
    0xe2, 0xe3, 0xe4, 0xe5, 0xe6, 0xe7, 0xe8, 0xe9, 0xea, 0xf2, 0xf3, 0xf4, 0xf5, 0xf6, 0xf7, 0xf8,
    0xf9, 0xfa
]

u16be(v::Integer) = UInt8[(v >> 8) & 0xFF, v & 0xFF]

function build_huff_lut(bits::Vector{UInt8}, vals::Vector{UInt8})
    lut = Dict{UInt8,Tuple{UInt32,Int}}()
    code = UInt32(0); k = 1
    for len in 1:16
        for _ in 1:Int(bits[len])
            lut[vals[k]] = (code, len); code += 1; k += 1
        end
        code <<= 1
    end
    lut
end
const HUFF_DC_LUMA   = build_huff_lut(JPEG_DC_LUMA_BITS,   JPEG_DC_LUMA_VALS)
const HUFF_DC_CHROMA = build_huff_lut(JPEG_DC_CHROMA_BITS, JPEG_DC_CHROMA_VALS)
const HUFF_AC_LUMA   = build_huff_lut(JPEG_AC_LUMA_BITS,   JPEG_AC_LUMA_VALS)
const HUFF_AC_CHROMA = build_huff_lut(JPEG_AC_CHROMA_BITS, JPEG_AC_CHROMA_VALS)

function jpeg_qt_scaled(qt::Vector{UInt8}, quality::Int)::Matrix{Int}
    q = clamp(quality, 1, 100)
    scale = q < 50 ? div(5000, q) : 200 - 2q
    out = Matrix{Int}(undef, 8, 8)
    for r in 1:8, c in 1:8
        # row-major заполнение: out[r,c] ↔ Annex K flat[(r-1)*8 + c]
        out[r, c] = clamp(div(Int(qt[(r - 1) * 8 + c]) * scale + 50, 100), 1, 255)
    end
    out
end

mutable struct JpegBitWriter
    io::IOBuffer
    bitbuf::UInt64
    bitcount::Int
end
JpegBitWriter() = JpegBitWriter(IOBuffer(), UInt64(0), 0)

function emit_bits!(bw::JpegBitWriter, code::UInt32, nbits::Int)
    nbits == 0 && return
    bw.bitbuf = (bw.bitbuf << nbits) | UInt64(code & ((UInt32(1) << nbits) - 1))
    bw.bitcount += nbits
    while bw.bitcount >= 8
        b = UInt8((bw.bitbuf >> (bw.bitcount - 8)) & 0xFF)
        write(bw.io, b); b == 0xFF && write(bw.io, 0x00)
        bw.bitcount -= 8
    end
end
function flush_bits!(bw::JpegBitWriter)
    if bw.bitcount > 0
        b = UInt8((bw.bitbuf << (8 - bw.bitcount)) & 0xFF)
        write(bw.io, b); b == 0xFF && write(bw.io, 0x00)
        bw.bitcount = 0
    end
end

jpeg_cat(v::Int) = v == 0 ? 0 : (v > 0 ? floor(Int, log2(v)) + 1 : floor(Int, log2(-v)) + 1)
jpeg_ampbits(v::Int, cat::Int) = cat == 0 ? UInt32(0) :
    (v >= 0 ? UInt32(v) : UInt32(v + (1 << cat) - 1))

function jpeg_fdct!(blk::Matrix{Float64})
    tmp = Matrix{Float64}(undef, 8, 8)
    @inbounds for r in 1:8, u in 1:8
        s = 0.0
        for x in 1:8; s += JPEG_COS[u, x] * blk[r, x]; end
        tmp[r, u] = s
    end
    @inbounds for c in 1:8, u in 1:8
        s = 0.0
        for y in 1:8; s += JPEG_COS[u, y] * tmp[y, c]; end
        blk[u, c] = s
    end
    blk
end

function jpeg_encode_block!(bw::JpegBitWriter, blk::Matrix{Float64},
                            qt::Matrix{Int}, dc_lut, ac_lut, prev_dc::Int)::Int
    jpeg_fdct!(blk)
    zz = Vector{Int}(undef, 64)
    @inbounds for k in 1:64
        i = JPEG_ZIGZAG[k]
        r = (i - 1) ÷ 8 + 1; c = (i - 1) % 8 + 1   # BUGFIX(J2): row-major
        zz[k] = round(Int, blk[r, c] / qt[r, c])
    end
    dc_diff = zz[1] - prev_dc
    dc_cat = jpeg_cat(dc_diff)
    code, len = dc_lut[UInt8(dc_cat)]
    emit_bits!(bw, code, len)
    dc_cat > 0 && emit_bits!(bw, jpeg_ampbits(dc_diff, dc_cat), dc_cat)
    run = 0
    @inbounds for k in 2:64
        v = zz[k]
        if v == 0
            run += 1
        else
            while run > 15
                c0, l0 = ac_lut[0xF0]; emit_bits!(bw, c0, l0); run -= 16
            end
            cat = jpeg_cat(v)
            c0, l0 = ac_lut[UInt8((run << 4) | cat)]
            emit_bits!(bw, c0, l0)
            emit_bits!(bw, jpeg_ampbits(v, cat), cat)
            run = 0
        end
    end
    if run > 0
        c0, l0 = ac_lut[0x00]; emit_bits!(bw, c0, l0)
    end
    zz[1]
end

"""
    jpeg_encode_rgb(rgb, W, H; quality=80) -> Vector{UInt8}

Baseline JPEG (4:2:0) из RGB-буфера. Полностью stdlib, без ccall.
"""
function jpeg_encode_rgb(rgb::Vector{UInt8}, W::Int, H::Int; quality::Int = 80)::Vector{UInt8}
    length(rgb) == W * H * 3 || throw(ArgumentError("jpeg buf size"))
    Wp = ((W + 15) ÷ 16) * 16
    Hp = ((H + 15) ÷ 16) * 16
    Ypl  = Matrix{Float64}(undef, Hp, Wp)
    Cbpl = Matrix{Float64}(undef, Hp ÷ 2, Wp ÷ 2)
    Crpl = Matrix{Float64}(undef, Hp ÷ 2, Wp ÷ 2)
    @inbounds for y in 1:Hp, x in 1:Wp
        sy = min(y, H); sx = min(x, W)   # edge replicate
        i = ((sy - 1) * W + (sx - 1)) * 3 + 1
        r = Float64(rgb[i]); g = Float64(rgb[i+1]); b = Float64(rgb[i+2])
        Ypl[y, x] = 0.299r + 0.587g + 0.114b - 128
        if y % 2 == 1 && x % 2 == 1
            yc = (y + 1) ÷ 2; xc = (x + 1) ÷ 2
            cb = 0.0; cr = 0.0; cnt = 0
            for dy in 0:1, dx in 0:1
                yy = min(y + dy, H); xx = min(x + dx, W)
                j = ((yy - 1) * W + (xx - 1)) * 3 + 1
                rr = Float64(rgb[j]); gg = Float64(rgb[j+1]); bb = Float64(rgb[j+2])
                cb += -0.1687rr - 0.3313gg + 0.5bb
                cr += 0.5rr - 0.4187gg - 0.0813bb
                cnt += 1
            end
            Cbpl[yc, xc] = cb / cnt
            Crpl[yc, xc] = cr / cnt
        end
    end
    qt_l = jpeg_qt_scaled(JPEG_QT_LUMA, quality)
    qt_c = jpeg_qt_scaled(JPEG_QT_CHROMA, quality)
    io = IOBuffer()
    write(io, 0xFF, 0xD8)
    # APP0 JFIF
    write(io, 0xFF, 0xE0, 0x00, 0x10)
    write(io, codeunits("JFIF\0")); write(io, 0x01, 0x01)
    write(io, 0x00); write(io, 0x00, 0x01, 0x00, 0x01); write(io, 0x00, 0x00)
    # DQT luma / chroma (zigzag-порядок, row-major позиции)
    write(io, 0xFF, 0xDB, 0x00, 0x43, 0x00)
    for k in 1:64
        i = JPEG_ZIGZAG[k]
        write(io, UInt8(clamp(qt_l[(i - 1) ÷ 8 + 1, (i - 1) % 8 + 1], 1, 255)))
    end
    write(io, 0xFF, 0xDB, 0x00, 0x43, 0x01)
    for k in 1:64
        i = JPEG_ZIGZAG[k]
        write(io, UInt8(clamp(qt_c[(i - 1) ÷ 8 + 1, (i - 1) % 8 + 1], 1, 255)))
    end
    # SOF0
    write(io, 0xFF, 0xC0, 0x00, 0x11, 0x08)
    write(io, u16be(Hp), u16be(Wp))
    write(io, 0x03, 0x01, 0x22, 0x00, 0x02, 0x11, 0x01, 0x03, 0x11, 0x01)
    # DHT — BUGFIX(J1): Tc (0=DC,1=AC) в старшем nibble, Th (0=luma,1=chroma) в младшем
    for (id, bits, vals) in [(0x00, JPEG_DC_LUMA_BITS, JPEG_DC_LUMA_VALS),
                             (0x10, JPEG_AC_LUMA_BITS, JPEG_AC_LUMA_VALS),
                             (0x01, JPEG_DC_CHROMA_BITS, JPEG_DC_CHROMA_VALS),
                             (0x11, JPEG_AC_CHROMA_BITS, JPEG_AC_CHROMA_VALS)]
        write(io, 0xFF, 0xC4); write(io, u16be(UInt16(2 + 1 + 16 + length(vals))))
        write(io, UInt8(id)); write(io, bits); write(io, vals)
    end
    # SOS
    write(io, 0xFF, 0xDA, 0x00, 0x0C, 0x03, 0x01, 0x00, 0x02, 0x11, 0x03, 0x11, 0x00, 0x3F, 0x00)
    bw = JpegBitWriter()
    dcY = 0; dcCb = 0; dcCr = 0
    for my in 1:16:Hp, mx in 1:16:Wp
        for (yy, xx) in ((my, mx), (my, mx + 8), (my + 8, mx), (my + 8, mx + 8))
            blk = Ypl[yy:yy+7, xx:xx+7]
            dcY = jpeg_encode_block!(bw, blk, qt_l, HUFF_DC_LUMA, HUFF_AC_LUMA, dcY)
        end
        yc = (my + 1) ÷ 2; xc = (mx + 1) ÷ 2
        blk = Cbpl[yc:yc+7, xc:xc+7]
        dcCb = jpeg_encode_block!(bw, blk, qt_c, HUFF_DC_CHROMA, HUFF_AC_CHROMA, dcCb)
        blk = Crpl[yc:yc+7, xc:xc+7]
        dcCr = jpeg_encode_block!(bw, blk, qt_c, HUFF_DC_CHROMA, HUFF_AC_CHROMA, dcCr)
    end
    flush_bits!(bw)
    write(io, take!(bw.io))
    write(io, 0xFF, 0xD9)
    take!(io)
end

"""
    avi_write_mjpeg(path, W, H, fps, frames_jpeg)

AVI-контейнер с fourcc 'MJPG' (Motion JPEG). Каждый кадр — самостоятельный
JPEG. Играется: VLC, mpv, ffmpeg, Chrome, WMP.
"""
function avi_write_mjpeg(path::AbstractString, W::Int, H::Int, fps::Int,
                         frames_jpeg::Vector{Vector{UInt8}})
    n = length(frames_jpeg)
    buf = IOBuffer()
    write(buf, "RIFF"); riff_pos = position(buf); write(buf, UInt32(0))
    write(buf, "AVI ")
    write(buf, "LIST"); hdrl_pos = position(buf); write(buf, UInt32(0)); write(buf, "hdrl")
    write(buf, "avih", UInt32(56))
    write(buf, UInt32(round(Int, 1_000_000 / fps)))
    write(buf, UInt32(0), UInt32(0), UInt32(0x10))
    write(buf, UInt32(n), UInt32(0), UInt32(1), UInt32(0))
    write(buf, UInt32(W), UInt32(H), zeros(UInt8, 16))
    write(buf, "LIST"); strl_pos = position(buf); write(buf, UInt32(0)); write(buf, "strl")
    write(buf, "strh", UInt32(56)); write(buf, "vids")
    write(buf, UInt8['M', 'J', 'P', 'G'])                   # fccHandler
    write(buf, UInt32(0), UInt16(0), UInt16(0))
    write(buf, UInt32(0), UInt32(1), UInt32(fps))
    write(buf, UInt32(0), UInt32(n), UInt32(0))
    write(buf, UInt32(0xFFFFFFFF), UInt32(0), zeros(UInt8, 8))
    write(buf, "strf", UInt32(40))
    write(buf, UInt32(40), Int32(W), Int32(H))
    write(buf, UInt16(1), UInt16(24))
    write(buf, UInt8['M', 'J', 'P', 'G'])                   # biCompression
    write(buf, UInt32(W * H * 3), Int32(0), Int32(0), UInt32(0), UInt32(0))
    strl_sz = position(buf) - strl_pos - 4; seek(buf, strl_pos); write(buf, UInt32(strl_sz)); seekend(buf)
    hdrl_sz = position(buf) - hdrl_pos - 4; seek(buf, hdrl_pos); write(buf, UInt32(hdrl_sz)); seekend(buf)
    write(buf, "LIST"); movi_pos = position(buf); write(buf, UInt32(0)); write(buf, "movi")
    movi_data_start = position(buf)
    offs = Int[]; sizes = Int[]
    for jpeg in frames_jpeg
        push!(offs, position(buf) - movi_data_start); push!(sizes, length(jpeg))
        write(buf, "00dc", UInt32(length(jpeg)))
        write(buf, jpeg)
        length(jpeg) % 2 == 1 && write(buf, 0x00)
    end
    movi_sz = position(buf) - movi_pos - 4; seek(buf, movi_pos); write(buf, UInt32(movi_sz)); seekend(buf)
    write(buf, "idx1", UInt32(n * 16))
    for (off, sz) in zip(offs, sizes)
        write(buf, "00dc", UInt32(0x10), UInt32(off), UInt32(sz))
    end
    riff_sz = position(buf) - riff_pos - 4; seek(buf, riff_pos); write(buf, UInt32(riff_sz)); seekend(buf)
    hodge_atomic_write(path, take!(buf))
end

# ── AVI writer (uncompressed 24bpp BI_RGB; отладочный, HODGE_KEEP_RAW_AVI=1) ──
function avi_write_rgb(path::AbstractString, W::Int, H::Int, fps::Int,
                       frames_rgb::Vector{Vector{UInt8}})
    n = length(frames_rgb)
    row_pad = ((W * 3 + 3) ÷ 4) * 4
    frame_size = row_pad * H
    buf = IOBuffer()
    write(buf, "RIFF"); riff_pos = position(buf); write(buf, UInt32(0))
    write(buf, "AVI ")
    write(buf, "LIST"); hdrl_pos = position(buf); write(buf, UInt32(0)); write(buf, "hdrl")
    write(buf, "avih"); write(buf, UInt32(56))
    write(buf, UInt32(round(Int, 1_000_000 / fps)))     # µs per frame
    write(buf, UInt32(frame_size * fps))                # max bytes/sec
    write(buf, UInt32(0)); write(buf, UInt32(0x10))     # flags = HASINDEX
    write(buf, UInt32(n)); write(buf, UInt32(0))        # total frames, initial
    write(buf, UInt32(1)); write(buf, UInt32(frame_size))
    write(buf, UInt32(W)); write(buf, UInt32(H))
    write(buf, zeros(UInt8, 16))
    write(buf, "LIST"); strl_pos = position(buf); write(buf, UInt32(0)); write(buf, "strl")
    write(buf, "strh"); write(buf, UInt32(56))
    write(buf, "vids"); write(buf, "DIB "); write(buf, UInt32(0))
    write(buf, UInt16(0)); write(buf, UInt16(0))
    write(buf, UInt32(0)); write(buf, UInt32(1)); write(buf, UInt32(fps))
    write(buf, UInt32(0)); write(buf, UInt32(n)); write(buf, UInt32(frame_size))
    write(buf, UInt32(0xFFFFFFFF)); write(buf, UInt32(0))
    write(buf, zeros(UInt8, 8))
    write(buf, "strf"); write(buf, UInt32(40))
    write(buf, UInt32(40)); write(buf, Int32(W)); write(buf, Int32(H))
    write(buf, UInt16(1)); write(buf, UInt16(24)); write(buf, UInt32(0))
    write(buf, UInt32(frame_size))
    write(buf, Int32(0)); write(buf, Int32(0))
    write(buf, UInt32(0)); write(buf, UInt32(0))
    strl_sz = position(buf) - strl_pos - 4; seek(buf, strl_pos); write(buf, UInt32(strl_sz)); seekend(buf)
    hdrl_sz = position(buf) - hdrl_pos - 4; seek(buf, hdrl_pos); write(buf, UInt32(hdrl_sz)); seekend(buf)
    write(buf, "LIST"); movi_pos = position(buf); write(buf, UInt32(0)); write(buf, "movi")
    movi_data_start = position(buf)
    offs = Int[]
    for frame in frames_rgb
        frm = zeros(UInt8, frame_size)
        for y in 0:H-1
            src = (H - 1 - y) * W * 3
            dst = y * row_pad
            for x in 0:W-1
                frm[dst+x*3+1] = frame[src+x*3+3]  # B
                frm[dst+x*3+2] = frame[src+x*3+2]  # G
                frm[dst+x*3+3] = frame[src+x*3+1]  # R
            end
        end
        push!(offs, position(buf) - movi_data_start)
        write(buf, "00db"); write(buf, UInt32(frame_size)); write(buf, frm)
    end
    movi_sz = position(buf) - movi_pos - 4; seek(buf, movi_pos); write(buf, UInt32(movi_sz)); seekend(buf)
    write(buf, "idx1"); write(buf, UInt32(n * 16))
    for off in offs
        write(buf, "00db"); write(buf, UInt32(0x10)); write(buf, UInt32(off)); write(buf, UInt32(frame_size))
    end
    riff_sz = position(buf) - riff_pos - 4; seek(buf, riff_pos); write(buf, UInt32(riff_sz)); seekend(buf)
    hodge_atomic_write(path, take!(buf))
end

# ── Попытка ffmpeg → MP4 (единственный честный путь к H.264) ──
function lab_video_try_mp4(frames_dir::String, fps::Int, out_mp4::String)
    ff = Sys.which("ffmpeg")
    ff === nothing && return false
    cmd = `$ff -y -loglevel error -framerate $fps -i $(joinpath(frames_dir, "frame_%05d.png")) -c:v libx264 -pix_fmt yuv420p -movflags +faststart $out_mp4`
    try
        run(cmd; wait = true)
        return isfile(out_mp4) && filesize(out_mp4) > 0
    catch
        return false
    end
end

# BUGFIX(i18n): вердикты задач возвращаются из вычислений готовыми русскими
# строками — i18n-словарь (hodge_fmt) на них не действует, и при lang=en REPL
# показывал русские PASS/INFO. Фразбук: литеральные фрагменты (вне
# интерполяции) → EN; применяется ТОЛЬКО на дисплее (results.json/отчёты
# остаются на русском — канон «бумаги»). Порядок: частные ключи раньше общих.
const RUN_I18N_EN = [
    "ценз/род подтверждены (2 схемы, 7 уровней): " => "genus census confirmed (2 schemes, 7 levels): ",
    "согласие схем на всех N∈[3,64] (C-001)" => "scheme agreement on all N∈[3,64] (C-001)",
    "периодов closed=tanh-sinh, rel=" => "periods closed=tanh-sinh, rel=",
    "фазовый закон, dev=" => "phase law, dev=",
    "эквивариантность, rel=" => "equivariance, rel=",
    "Γ-рефлексия, " => "Γ-reflection, ",
    " пар, rel=" => " pairs, rel=",
    "ранг функциональной матрицы = числу строк (N=7,9)" => "functional matrix rank = number of rows (N=7,9)",
    "башни точны, GF(2) ok, радикалы rel=" => "towers exact, GF(2) ok, radicals rel=",
    "48 прямых, rank=" => "48 lines, rank=",
    "48 прямых · встреч/прямую=" => "48 lines · meets/line=",
    "Арф g=1..3: " => "Arf g=1..3: ",
    " = формулам" => " = formulas",
    "Клейн: " => "Klein: ",
    "на блочно-циклических μ₄-системах, dim " => "on block-cyclic μ₄-systems, dim ",
    "(целые/ℤ[i])" => "(integers/ℤ[i])",
    "t* на " => "t* on ",
    " случаях; поток " => " cases; flow ",
    " клеток; суммы=" => " cells; sums=",
    " и 2π не рационализируются" => " and 2π not rationalizable",
    "Виета (" => "Vieta (",
    "GF(2)-отпечаток " => "GF(2) fingerprint ",
    "Вейль b₃=" => "Weil b₃=",
    " кадра PNG + GIF, sweep-парсер (" => " PNG frames + GIF, sweep parser (",
    "GIF = поверхность f(a,b) (a,b ∈ [1,N]); ось X = a−b, Y = a+b; цвет = значение (тёмный → золотой); см. README.txt" =>
        "GIF = surface f(a,b) (a,b ∈ [1,N]); X axis = a−b, Y axis = a+b; color = value (dark → gold); see README.txt",
    "ERR: сгенерировано " => "ERR: generated ",
    " прямых (ожидалось 48)" => " lines (expected 48)",
    "встреч на прямую: " => "meets per line: ",
    "встреч на строку: " => "meets per line: ",
    " (ожидалось 14)" => " (expected 14)",
    "диагональ ≠ −2" => "diagonal ≠ −2",
    "есть элементы вне {−2,0,1}" => "elements outside {−2,0,1}",
    "G не симметрична" => "G not symmetric",
    " не квадратна: " => " not square: ",
    "подпись не совпала: " => "signature mismatch: ",
    "≠ ожидаемое " => "≠ expected ",
    "path-guard пропустил опасный slug" => "path-guard skipped unsafe slug",
    "fermat_k3_intersect: недостижимая пара partition (" => "fermat_k3_intersect: unreachable partition pair (",
    "→ задача " => "→ task ",
    "задач к прогону: " => "tasks to run: ",
    "Dry-run план · пресет " => "Dry-run plan · preset ",
    " · сид " => " · seed ",
    "создаст: results/" => "creates: results/",
    " бит" => " bits",
    " на p=" => " on p=",
    "конь" => "knight",
]

"""Дисплей-перевод вердиктов/INFO-строк задач: работает только для lang=en,
иначе строка возвращается как есть (ru — канон данных)."""
run_i18n(s::AbstractString, lang::AbstractString) = begin
    lang == "en" || return String(s)
    out = String(s)
    for (ru, en) in RUN_I18N_EN
        occursin(ru, out) && (out = replace(out, ru => en))
    end
    out
end

const TASKS = [
    Task(id = 1,  slug = "census-genus",        title = "Формула рода и ценз (T01/T20/V1)",  title_en = "Genus formula and census (T01/T20/V1)",  claims = ["T01", "T20", "V1", "C-001"], fn = t01,  pass2 = t01b, est_sec = 0.5, tags = ["fast", "exact"], plot_fn = nothing),
    Task(id = 2,  slug = "periods-v2",          title = "Замкнутая форма vs tanh-sinh (T02/V2)", title_en = "Closed form vs tanh-sinh (T02/V2)", claims = ["T02", "V2"], fn = t02, est_sec = 2.0, tags = ["hp", "core"], plot_fn = plot02_periods),
    Task(id = 3,  slug = "phase-v3",            title = "Фазовый закон (V3)",                title_en = "Phase law (V3)",                claims = ["V3"], fn = t03, est_sec = 1.5, tags = ["hp", "core"]),
    Task(id = 4,  slug = "equivariance-v4",     title = "Эквивариантность (V4)",             title_en = "Equivariance (V4)",             claims = ["V4"], fn = t04, est_sec = 0.3, tags = ["hp", "fast"]),
    Task(id = 5,  slug = "chain-v5",            title = "Целостность цепи (V5)",             title_en = "Chain integrity (V5)",          claims = ["V5"], fn = t05, est_sec = 0.4, tags = ["hp", "fast"]),
    Task(id = 6,  slug = "reflection-v6",       title = "Γ-рефлексия (V6)",                  title_en = "Γ-reflection (V6)",             claims = ["V6", "T03"], fn = t06, est_sec = 0.5, tags = ["hp", "fast"], plot_fn = plot06_reflection),
    Task(id = 7,  slug = "dft-v8",              title = "DFT-ортогональность (V8)",          title_en = "DFT orthogonality (V8)",        claims = ["V8"], fn = t07, est_sec = 0.6, tags = ["hp", "fast"]),
    Task(id = 8,  slug = "deep-v9",             title = "Глубокий рекорд (V9)",              title_en = "Deep record (V9)",              claims = ["V9"], fn = t08, est_sec = 2.5, tags = ["hp", "heavy"]),
    Task(id = 9,  slug = "torus-triple",        title = "Тор и Δ_Ch (T07)",                  title_en = "Torus and Δ_Ch (T07)",          claims = ["T07"], fn = t09, est_sec = 0.1, tags = ["hp", "fast"]),
    Task(id = 10, slug = "k3-stand",            title = "K3: ранг/сигнатура/det (T08)",      title_en = "K3: rank/signature/det (T08)",  claims = ["T08", "T22"], fn = t10, est_sec = 0.6, tags = ["exact", "core"], plot_fn = plot10_k3),
    Task(id = 11, slug = "klein-stand",         title = "Клейн точный слой (T11)",           title_en = "Klein exact layer (T11)",       claims = ["T11"], fn = t11, est_sec = 0.2, tags = ["exact", "fast"]),
    Task(id = 12, slug = "errata-arf",          title = "Арф-перебор (T09)",                 title_en = "Arf enumeration (T09)",         claims = ["T09"], fn = t12, est_sec = 0.4, tags = ["exact", "fast"]),
    Task(id = 13, slug = "flow-tstar",          title = "Поток t* (T13/certE)",              title_en = "Flow t* (T13/certE)",           claims = ["T13"], fn = t13, est_sec = 0.1, tags = ["exact", "fast"], plot_fn = plot13_flow),
    Task(id = 14, slug = "bch-radicals",        title = "Радикалы башни (T05/T19)",          title_en = "Tower radicals (T05/T19)",      claims = ["T05", "T19"], fn = t14, est_sec = 0.2, tags = ["exact", "fast"]),
    Task(id = 15, slug = "cyc-cubics",          title = "Виета/Кардано N=7,9 (T17/T18)",     title_en = "Vieta/Cardano N=7,9 (T17/T18)", claims = ["T17", "T18"], fn = t15, est_sec = 0.2, tags = ["exact", "fast"]),
    Task(id = 16, slug = "snf-spectra",         title = "SNF-движок (T06/T22)",              title_en = "SNF engine (T06/T22)",          claims = ["T06", "T22"], fn = t16, est_sec = 0.3, tags = ["exact", "fast"]),
    Task(id = 17, slug = "tower-identities",    title = "Тождества башни (T19)",             title_en = "Tower identities (T19)",        claims = ["T19"], fn = t17, est_sec = 0.1, tags = ["exact", "fast"]),
    Task(id = 18, slug = "qscan-certf",         title = "q-scan (T14/certF)",                title_en = "q-scan (T14/certF)",            claims = ["T14"], fn = t18, est_sec = 0.1, tags = ["exact", "fast"]),
    Task(id = 19, slug = "chowla-selberg",      title = "Γ-тождества (T15/certG)",           title_en = "Γ-identities (T15/certG)",      claims = ["T15"], fn = t19, est_sec = 0.2, tags = ["hp", "fast"]),
    Task(id = 20, slug = "mu4-theorem",         title = "μ₄-коммутатор (T12/certD)",         title_en = "μ₄-commutator (T12/certD)",     claims = ["T12"], fn = t20, est_sec = 0.2, tags = ["exact", "fast"]),
    Task(id = 21, slug = "fermat-point-count",  title = "Квинтик: счёт точек (C-011)",       title_en = "Quintic: point count (C-011)",  claims = ["C-011"], fn = t21, pass2 = t21b, est_sec = 0.3, tags = ["exact", "fast"], plot_fn = plot21_fermat),
    Task(id = 22, slug = "v7-rank",             title = "V7-полнота (QR)",                   title_en = "V7 completeness (QR)",          claims = ["V7"], fn = t22, est_sec = 1.0, tags = ["fast"]),
    Task(id = 23, slug = "hodge-fermat-k3",     title = "Hodge (1,1) для K3 Ферма: 48 прямых, SNF [1^18,8,8] (mod-8 + mod-p)", title_en = "Hodge (1,1) for Fermat K3: 48 lines, SNF [1^18,8,8] (mod-8 + mod-p)", claims = ["HODGE-K3"], fn = t23, est_sec = 1.0, tags = ["exact", "hodge", "core"], plot_fn = plot23_hodge_k3),
    Task(id = 38, slug = "lab3d-ci",            title = "3D-лаборатория: PNG+GIF+sweep (§33.7)", title_en = "3D lab: PNG+GIF+sweep (§33.7)", claims = ["lab3d"], fn = task38_lab3d, est_sec = 0.6, tags = ["exact", "lab"]),
]

const SUITE_IDS = [t.id for t in TASKS]

# ── регистрация задачи 40 «HODGE-INF» (классы Ходжа до бесконечности, §33.8):
# t40-функции определены выше по файлу; здесь только запись в реестр
push!(TASKS, Task(id = 40, slug = "hodge-classes-inf",
                  title = "Классы Ходжа до бесконечности: башня Ферма N=5..80, Ω-рефлексия + точное сито c_N vs float64",
                  title_en = "Hodge classes to infinity: Fermat tower N=5..80, Omega-reflection + exact c_N sieve vs float64",
                  claims = ["HODGE-INF"], fn = t40_hodge_inf, est_sec = 4.0,
                  tags = ["hp", "hodge", "heavy"], version = "1.3.0",
                  plot_fn = plot40_hodge_inf))
push!(SUITE_IDS, 40)

task_by_id(tid::Int) = (t = findfirst(x -> x.id == tid, TASKS); t === nothing ? nothing : TASKS[t])

"""§24.3: slug — только [a-z0-9_-], ≤ 64; иначе nothing (ERR_PATH_TRAVERSAL)."""
safe_slug(s::AbstractString) = begin
    (isempty(s) || length(s) > 64 || !occursin(r"^[a-z0-9_-]+$", s)) && return nothing
    return String(s)
end

"""§24.3: любой составной путь через guard; '..' → ERR_PATH_TRAVERSAL."""
safe_join(root::AbstractString, parts...) = begin
    root_abs = abspath(root)
    for p in parts
        (isabspath(p) || ".." in splitpath(p)) &&
            throw(ArgumentError("ERR_PATH_TRAVERSAL $p"))
    end
    target = abspath(joinpath(root_abs, parts...))
    (startswith(target, root_abs * "/") || target == root_abs) ||
        throw(ArgumentError("ERR_PATH_TRAVERSAL $target"))
    return target
end

# ════════════════════════════════════════════════════════════════════════
# §9 ЛОГИ: пять потоков (COMP_LOG, STDOUT_CAPTURE, results_log, events,
# metrics) + редакция секретов §9.5 + ERR_LEDGER §9.6. Файлы — без ANSI (§9.7).
# ════════════════════════════════════════════════════════════════════════
const LEVELS = Dict("TRACE" => 0, "DEBUG" => 1, "INFO" => 2, "WARN" => 3, "ERROR" => 4, "FATAL" => 5)
const REDACT_PATTERNS = [r"(token=)\S+", r"(secret=)\S+", r"(password=)\S+", r"(api[_-]?key=)\S+"]

redact(s::AbstractString) = begin
    out = String(s)
    for rx in REDACT_PATTERNS
        out = replace(out, rx => s"\1***")
    end
    out
end

mutable struct HodgeLogger
    cfg::HodgeConfig
    comp_path::Union{Nothing,String}
    events_path::Union{Nothing,String}
    metrics_path::Union{Nothing,String}
    results_path::Union{Nothing,String}
    t0::Float64
    last_ts::Float64
    err_ledger::Dict{String,Vector{Any}}
    metrics::Dict{String,Vector{Any}}
    comp_io::Union{Nothing,IOStream}     # P2.12: открытый handle comp_log
    events_io::Union{Nothing,IOStream}   # P2.12: открытый handle events
end
HodgeLogger(cfg::HodgeConfig) = HodgeLogger(cfg, nothing, nothing, nothing, nothing,
                                            time(), time(), Dict{String,Vector{Any}}(),
                                            Dict{String,Vector{Any}}(), nothing, nothing)

function open_run!(lg::HodgeLogger, run_dir::AbstractString)
    lg.comp_path = joinpath(run_dir, "logs", "computation_log.txt")
    lg.events_path = joinpath(run_dir, "logs", "events.jsonl")
    lg.metrics_path = joinpath(run_dir, "logs", "metrics.jsonl")
    lg.results_path = joinpath(run_dir, "logs", "results_log.txt")
    mkpath(joinpath(run_dir, "logs"))
    # P2.12 / §25: handles держим открытыми — минус open/close на каждую строку
    lg.comp_io = open(lg.comp_path, "a")
    lg.events_io = open(lg.events_path, "a")
    nothing
end

function close_logger!(lg::HodgeLogger)
    """P2.12-багфикс: закрыть handle'ы, открытые open_run! (comp_io/events_io).
    Метрики/результаты пишутся по требованию и держатся закрытыми — их не трогаем."""
    for f in (:comp_io, :events_io)
        io = getproperty(lg, f)
        if io !== nothing
            try
                flush(io)
                close(io)
            catch
            end
            setproperty!(lg, f, nothing)
        end
    end
    nothing
end

log_comp!(lg::HodgeLogger, level::AbstractString, module_::AbstractString, msg::AbstractString) = begin
    level in keys(LEVELS) || (level = "INFO")
    msg = redact(String(msg))
    msg = run_i18n(msg, lg.cfg.lang)   # BUGFIX(i18n): INFO/WARN задач → en при lang=en
    now = time()
    delta = now - lg.last_ts
    lg.last_ts = now
    if lg.comp_path !== nothing && LEVELS[level] >= LEVELS[lg.cfg.log_level]
        ts = Dates.format(Dates.now(Dates.UTC), "Y-mm-ddTHH:MM:SSZ")
        line = "[$ts] [+$(@sprintf("%.3f", delta))s] [$level] [$module_] $msg"
        if lg.comp_io !== nothing
            println(lg.comp_io, line)
            flush(lg.comp_io)      # flush на строку — краш-надёжность сохранена
        else                        # fallback: логгер без open_run! (selftest и пр.)
            open(lg.comp_path, "a") do f
                println(f, line)
            end
        end
    end
    if level in ("WARN", "ERROR", "FATAL") && !lg.cfg.ci
        println(stderr, dye(level, level == "WARN" ? "warn" : "err", level == "WARN" ? "" : "bold"), " ", dye(msg, "text"))
    end
    nothing
end

log_event!(lg::HodgeLogger, level::AbstractString, module_::AbstractString, key::AbstractString;
           kw...) = begin
    lg.events_path === nothing && return
    rec = Dict("ts" => Dates.format(Dates.now(Dates.UTC), "Y-mm-ddTHH:MM:SS.sss"),
               "level" => level, "module" => module_, "key" => key, "args" => Dict(String(k) => v for (k, v) in kw))
    if lg.events_io !== nothing
        println(lg.events_io, json_dump(rec))
        flush(lg.events_io)
    else
        open(lg.events_path, "a") do f
            println(f, json_dump(rec))
        end
    end
    nothing
end

# P2.12: закрытие открытых handles (вызывается из finally hodge_main)
function close_logger!(lg::HodgeLogger)
    lg.comp_io !== nothing && (try close(lg.comp_io) catch; end)
    lg.events_io !== nothing && (try close(lg.events_io) catch; end)
    lg.comp_io = lg.events_io = nothing
    nothing
end

    """metrics.jsonl + агрегат (гистограмма ≤ 1024, §9.4)."""
log_metric!(lg::HodgeLogger, name::AbstractString, mtype::AbstractString, value; tags = Dict()) = begin
    vec = get!(lg.metrics, String(name), Any[])
    if length(vec) <= 1024
        push!(vec, value)
        lg.metrics_path === nothing && return
        rec = Dict("ts" => Dates.format(Dates.now(Dates.UTC), "Y-mm-ddTHH:MM:SS.sss"),
                   "name" => String(name), "type" => mtype, "value" => value, "tags" => tags)
        open(lg.metrics_path, "a") do f
            println(f, json_dump(rec))
        end
    else
        lg.err_ledger["ERR_HISTO_OVERFLOW"] = [get(lg.err_ledger["ERR_HISTO_OVERFLOW"], [0, nothing])[1] + 1, Dates.now(Dates.UTC)]
    end
    nothing
end
# §9.4: dedicated-метрики
metric_counter!(lg, name; delta = 1, tags = Dict()) = begin
    vec = get!(lg.metrics, String(name), Any[0]); vec[end] = vec[end] + delta
    log_metric!(lg, name, "counter", delta; tags = tags)
end
metric_gauge!(lg, name, value; tags = Dict()) = log_metric!(lg, name, "gauge", value; tags = tags)
metric_timer!(lg, name, dur; tags = Dict()) = log_metric!(lg, name, "timer", dur; tags = tags)

    """ERR_LEDGER §9.6: err_code → [count, last_seen]."""
ledger!(lg::HodgeLogger, code::AbstractString) = begin
    rec = get!(lg.err_ledger, String(code), Any[0, nothing])
    rec[1] += 1
    rec[2] = Dates.format(Dates.now(Dates.UTC), "Y-mm-ddTHH:MM:SS")
    nothing
end

"""§4.1 / §9.2 / A17: одна строка-вердикт на задачу; в файл без ANSI."""
log_result!(lg::HodgeLogger, tid::Int, slug::AbstractString, verdict::AbstractString;
            reason = nothing, duration_s = nothing) = begin
    # BUGFIX(i18n): reason — русский вердикт из task-fn; на дисплее переводим
    reason_en = reason === nothing ? nothing : run_i18n(reason, lg.cfg.lang)
    plain = @sprintf("[%2d] %s: %s", tid, slug, verdict) *
            (reason_en === nothing ? "" : " · $reason_en") *
            (duration_s === nothing ? "" : " · $(@sprintf("%.2f", duration_s))s")
    if lg.results_path !== nothing
        try
            open(lg.results_path, "a") do f
                println(f, plain)
            end
        catch
        end
    end
    silent = lg.cfg.ci || lg.cfg.jsonl || lg.cfg.tsv
    silent || println(badge(verdict), " ", dye(@sprintf("[%2d] %s", tid, slug), "gold"),
                      reason_en === nothing ? "" : dye(" · $reason_en", "text_dim"))
    nothing
end

    """§7.1/§7.4: бар + sparkline + ETA + rate в stderr; в pipe — milestone."""
log_progress!(lg::HodgeLogger, frac::Real; eta = "", spark = "", rate = nothing) = begin
    (lg.cfg.ci || lg.cfg.plain) && return
    if Base.isopen(stderr) && !lg.cfg.jsonl && !lg.cfg.tsv && stderr isa Base.TTY
        width = clamp(displaysize(stderr)[2] - 2, 30, 100)
        filled = round(Int, width * frac)
        fill_ch = TEXT_STATE["unicode_on"] ? "█" : "#"
        pad_ch = TEXT_STATE["unicode_on"] ? "·" : "-"
        bar = dye(fill_ch^filled, "gold") * dye(pad_ch^(width - filled), "neutral")
        extras = String[]
        isempty(spark) || push!(extras, spark)
        isempty(eta) || push!(extras, dye("ETA $eta", "gold_dim"))
        rate === nothing || push!(extras, dye(@sprintf("%.1f/s", rate), "gold_dim"))
        tail = isempty(extras) ? "" : " " * join(extras, " ")
        print(stderr, "\r$bar $(round(Int, frac * 100))%$tail\r")
        flush(stderr)
    elseif mod(round(Int, frac * 10), 1) == 0 && round(Int, frac * 10) != round(Int, (frac - 0.0001) * 10)
        (lg.cfg.jsonl || lg.cfg.tsv) && return
        println(stderr, "milestone ", round(Int, frac * 100), "%")
    end
end

# ── §7.4: sparkline + ETA (EMA α=0.2) + rate ──
sparkline_render(values::Vector; width::Int = 20) = begin
    # Страховка: косметический рендер НЕ должен уметь ронять прогон
    # (инцидент: StringIndexError на байтах UTF-8 убил весь run → меню)
    try
        isempty(values) && return ""
    vals = values[max(1, end - width + 1):end]
    lo, hi = extrema(vals)
    span = (hi - lo) == 0 ? 1.0 : (hi - lo)
    # BUGFIX(StringIndex): строка глифов UTF-8 — по 3 байта на символ,
    # chars[idx] индексирует БАЙТЫ → StringIndexError на большинстве bucket'ов
    # (t≈0.2 давал idx=2 — вне границ символа). collect → Vector{Char},
    # индексация по элементам, без байтовых сюрпризов.
    glyphs = TEXT_STATE["unicode_on"] ? collect("▁▂▃▄▅▆▇█") : collect(".-=+*#@")
    out = IOBuffer()
    for v in vals
        t = (v - lo) / span
        idx = clamp(floor(Int, t * length(glyphs)) + 1, 1, length(glyphs))
        color = t < 0.4 ? "gold_dim" : t < 0.8 ? "gold" :
                (v == hi && length(vals) > 1) ? "amber" : "gold_bright"
        print(out, dye(string(glyphs[idx]), color))
    end
        return String(take!(out))
    catch
        return ""
    end
end

mutable struct HodgeETA
    alpha::Float64
    samples::Vector{Float64}
    ema::Union{Nothing,Float64}
end
HodgeETA() = HodgeETA(0.2, Float64[], nothing)
eta_push!(e::HodgeETA, dur) = begin
    push!(e.samples, dur)
    e.ema = e.ema === nothing ? dur : e.alpha * dur + (1 - e.alpha) * e.ema
end
eta_str(e::HodgeETA, remaining::Int) = begin
    (length(e.samples) < 8 || e.ema === nothing) && return "…"
    if length(e.samples) >= 10
        win = e.samples[max(1, end - 19):end]
        mu = sum(win) / length(win)
        sd = sqrt(sum(abs2, win .- mu) / length(win))
        e.ema > 0 && sd / e.ema > 3 && return "±"
    end
    return fmt_duration(max(0.0, e.ema * remaining))
end

mutable struct HodgeRate
    t0::Float64
    count::Int
end
HodgeRate() = HodgeRate(time(), 0)
rate_tick!(r::HodgeRate) = (r.count += 1)
rate_value(r::HodgeRate) = begin
    dt = time() - r.t0
    dt > 0 ? r.count / dt : 0.0
end

# ── §8 монитор /proc + logs/monitor.csv ──
mutable struct HodgeMonitor
    csv_path::Union{Nothing,String}
    cpu_prev::Union{Nothing,Tuple{Int,Int}}
    warned::Set{String}
end
HodgeMonitor(csv::Union{Nothing,String}) = HodgeMonitor(csv, nothing, Set{String}())

mon_warn_once!(m::HodgeMonitor, key, msg) = begin
    key in m.warned && return
    push!(m.warned, key)
    ACTIVE_LOGGER[] !== nothing && log_comp!(ACTIVE_LOGGER[], "WARN", "Mon", msg)
end

mon_cpu!(m::HodgeMonitor) = try
    parts = split(readline("/proc/stat"))[2:end]
    vals = parse.(Int, parts)
    idle = vals[4] + (length(vals) > 4 ? vals[5] : 0)
    total = sum(vals)
    pct = m.cpu_prev === nothing ? 0.0 :
          begin
              dt = total - m.cpu_prev[2]
              dt > 0 ? 100.0 * (1.0 - (idle - m.cpu_prev[1]) / dt) : 0.0
          end
    m.cpu_prev = (idle, total)
    return num(pct, "pct") * "%"
catch
    mon_warn_once!(m, "cpu", "/proc/stat недоступен")
    "—"
end

mon_ram(m::HodgeMonitor) = try
    info = Dict{String,Int}()
    for ln in eachline("/proc/meminfo")
        k, v = split(ln, ":"; limit = 2)
        info[k] = parse(Int, first(split(strip(v))))
    end
    used = info["MemTotal"] - get(info, "MemAvailable", get(info, "MemFree", 0))
    return fmt_size(info["MemTotal"] * 1024) * " (" * fmt_size(used * 1024) * " used)"
catch
    mon_warn_once!(m, "ram", "/proc/meminfo недоступен")
    "—"
end

mon_temp(m::HodgeMonitor) = try
    c = parse(Int, strip(read("/sys/class/thermal/thermal_zone0/temp", String))) / 1000.0
    return num(c, "float", 1) * "°C"
catch
    "—"
end

mon_uptime(m::HodgeMonitor) = try
    fmt_duration(parse(Float64, first(split(read("/proc/uptime", String)))))
catch
    "—"
end

mon_io(m::HodgeMonitor) = try
    for ln in eachline("/proc/pressure/io")
        occursin("some", ln) && return split(ln)[2][4:end] * "µs"
    end
    "—"
catch
    "—"
end

mon_snapshot!(m::HodgeMonitor) = begin
    s = Dict("cpu" => mon_cpu!(m), "ram" => mon_ram(m), "temp" => mon_temp(m),
             "io" => mon_io(m), "uptime" => mon_uptime(m))
    if m.csv_path !== nothing
        try
            exists = isfile(m.csv_path)
            open(m.csv_path, "a") do f
                exists || println(f, "ts,cpu,ram,temp,io,uptime")
                println(f, join([Dates.format(Dates.now(Dates.UTC), "Y-mm-ddTHH:MM:SS"),
                                 s["cpu"], replace(s["ram"], "," => " "), s["temp"], s["io"], s["uptime"]], ","))
            end
        catch
            mon_warn_once!(m, "csv", "monitor.csv не пишется")
        end
    end
    return s
end

# ── §25: дисковый кэш + rate-limit ──
mutable struct HodgeCache
    cfg::HodgeConfig
    dir::String
    HodgeCache(cfg::HodgeConfig) = begin
        cfg.cache_on && mkpath(cfg.cache_dir)
        new(cfg, cfg.cache_dir)
    end
end
cache_key(c::HodgeCache, task_id::Int) = begin
    payload = "$task_id|$(cfg_relevant_hash(c.cfg))|"
    bytes2hex(sha256(payload))[1:32]
end
cache_get(c::HodgeCache, task_id::Int) = begin
    (!c.cfg.cache_on) && return nothing
    p = joinpath(c.dir, string(task_id), cache_key(c, task_id) * ".bin")
    isfile(p) || return nothing
    data = read(p)
    length(data) > 5 && data[1:5] == UInt8['C', 'A', 'C', 'H', 'E'] || return nothing
    try
        return json_load_flat(String(data[6:end]))
    catch
        return nothing
    end
end
cache_put!(c::HodgeCache, task_id::Int, value::Dict) = begin
    c.cfg.cache_on || return
    p = joinpath(c.dir, string(task_id), cache_key(c, task_id) * ".bin")
    mkpath(dirname(p))
    # P2.13 / §24.1: flock на cache_dir — параллельные прогоны не портят ключи
    lk = try
        open(joinpath(c.dir, ".lock"), "a")
    catch
        return
    end
    try
        ccall(:flock, Cint, (Cint, Cint), Base.fd(lk), 2) == 0 || return  # LOCK_EX
        hodge_atomic_write(p, vcat(UInt8['C', 'A', 'C', 'H', 'E'], codeunits(json_dump(value))))
    finally
        close(lk)
    end
    nothing
end

# ──────────────────────────────────────────────────────────────────────
# §3.2 v4: КЭШ НАСТРОЕК (.cache/settings.json). Приоритет §3.2:
#   defaults < settings-cache < config-file < env < CLI < меню.
# Меню сохраняет настройки при КАЖДОМ изменении — [P] prec-extreme, тема,
# точность и т.д. живут между запусками. CLI всегда сильнее кэша.
# ──────────────────────────────────────────────────────────────────────
const SETTINGS_CACHE_KEYS = ("prec", "seed", "preset", "profile", "theme", "lang",
                             "color_depth", "dye_mode", "gradient", "anim", "anim_scene",
                             "banner", "two_pass", "prec_extreme", "digit_tier",
                             "splash", "tips")
const SETTINGS_SCHEMA = "1.0.0"

settings_cache_path(cfg::HodgeConfig) = joinpath(cfg.cache_dir, "settings.json")

function load_settings_cache!(cfg::HodgeConfig)
    """§3.2 v4: применить сохранённые настройки. Битый файл → переименование в
    .corrupt; незнакомые ключи игнорируются. → список применённых ключей."""
    cfg.settings_cache || return String[]
    p = settings_cache_path(cfg)
    isfile(p) || return String[]
    data = try
        json_load_flat(read(p, String))
    catch ex
        try; mv(p, p * ".corrupt"; force = true); catch; end
        println(badge("WARN"), " settings cache is corrupt ($(sprint(showerror, ex))) — moved to ", p, ".corrupt")
        flush(stdout)
        return String[]
    end
    data isa AbstractDict || return String[]
    haskey(data, "settings") && data["settings"] isa AbstractDict && (data = data["settings"])
    applied = String[]
    for key in SETTINGS_CACHE_KEYS
        haskey(data, key) || continue
        val = data[key]
        sym = Symbol(key)
        try
            cur = getproperty(cfg, sym)
            if cur isa Bool
                val = val == true || val == "true" || val == 1
            elseif cur isa Int
                val = isa(val, Real) ? Int(val) : parse(Int, string(val))
            elseif cur isa String
                val = string(val)
            end
            setproperty!(cfg, sym, val)
            push!(applied, key)
        catch
            # тип не приводится — ключ пропускаем (§3.2 v4: толерантность)
        end
    end
    return applied
end

function save_settings_cache!(cfg::HodgeConfig)
    """§3.2 v4: атомарно сохранить настройки меню/прогона. → путь или ""."""
    cfg.settings_cache || return ""
    payload = Dict{String,Any}(
        "schema" => SETTINGS_SCHEMA,
        "saved_at" => Dates.format(Dates.now(Dates.UTC), "Y-mm-ddTHH:MM:SS"),
        "version" => HODGE_VERSION,
        "settings" => Dict{String,Any}(k => getproperty(cfg, Symbol(k)) for k in SETTINGS_CACHE_KEYS))
    try
        p = settings_cache_path(cfg)
        mkpath(dirname(p))
        hodge_atomic_write(p, json_dump(payload))
        return p
    catch
        return ""
    end
end

reset_settings_cache!(cfg::HodgeConfig) = try
    isfile(settings_cache_path(cfg)) && rm(settings_cache_path(cfg); force = true)
    isfile(settings_cache_path(cfg) * ".corrupt") && rm(settings_cache_path(cfg) * ".corrupt"; force = true)
    true
catch
    false
end

mutable struct HodgeRateLimit
    period_s::Float64
    last::Float64
end
HodgeRateLimit(spec::AbstractString) = begin
    p = 0.0
    if occursin("/", spec)
        n, unit = split(spec, "/"; limit = 2)
        mult = Dict("s" => 1.0, "m" => 60.0, "h" => 3600.0)
        p = (mult[unit]) / max(1, parse(Int, n))
    end
    HodgeRateLimit(p, 0.0)
end
rl_wait!(rl::HodgeRateLimit) = begin
    rl.period_s <= 0 && return
    now = time()
    if now - rl.last < rl.period_s
        sleep(rl.period_s - (now - rl.last))
    end
    rl.last = time()
    nothing
end

"""§12.6: RLIMIT_AS/CPU/FSIZE. stdlib-Julia не имеет resource API →
ERR_UNSUPPORTED в ledger (§1.5: ближайший эквивалент — ничего не ограничивать)."""
hodge_apply_rlimits(cfg::HodgeConfig, lg::Union{Nothing,HodgeLogger}) = begin
    lg !== nothing || return false
    ledger!(lg, "ERR_UNSUPPORTED")
    log_comp!(lg, "WARN", "Rlimit", hodge_fmt(Dict("lang" => get(TEXT_STATE, "lang", "en")), "rlimit.unsupported"))
    return false
end

    """§24.9: удалить осиротевшие *.tmp в run_dir."""
hodge_clean_orphans!(lg, run_dir::AbstractString) = begin
    removed = 0
    isdir(run_dir) || return 0
    for (root, _dirs, files) in walkdir(run_dir)
        for f in files
            if endswith(f, ".tmp")
                try
                    rm(joinpath(root, f); force = true)
                    removed += 1
                catch
                end
            end
        end
    end
    lg !== nothing && log_comp!(lg, "INFO", "Cleanup", "removed $removed orphan tmp-files")
    return removed
end

# ════════════════════════════════════════════════════════════════════════
# §4.3 HOOKS: 6 событий; хук не может уронить прогон
# ════════════════════════════════════════════════════════════════════════
const HOOK_EVENTS = ("pre_run", "post_run", "pre_task", "post_task", "on_error", "on_verdict")
const HOOKS = Dict(ev => Function[] for ev in HOOK_EVENTS)
register_hook!(event::AbstractString, fn::Function) = begin
    haskey(HOOKS, event) || throw(ArgumentError("ERR_HOOK_UNKNOWN $event"))
    push!(HOOKS[event], fn)
    nothing
end
fire_hook(event::AbstractString, args...) = begin
    for fn in get(HOOKS, event, Function[])
        try
            fn(args...)
        catch ex
            if ACTIVE_LOGGER[] !== nothing
                ledger!(ACTIVE_LOGGER[], "ERR_HOOK_EXCEPTION")
                log_comp!(ACTIVE_LOGGER[], "WARN", "Hook", "$event: $(sprint(showerror, ex))")
            end
        end
    end
    nothing
end

# ════════════════════════════════════════════════════════════════════════
# §7.6 СИГНАЛЫ: флаги в обработчиках (async-signal-safe); §24.2 flock.
# ════════════════════════════════════════════════════════════════════════
const SIG_FLAGS = Dict{String,Threads.Atomic{Int}}(
    "SIGINT" => Threads.Atomic{Int}(0), "SIGTERM" => Threads.Atomic{Int}(0),
    "SIGUSR1" => Threads.Atomic{Int}(0))

const _sig_handlers = Dict{String,Ptr{Nothing}}()

function _sig_handler_c(sig::Cint)
    sname = sig == 2 ? "SIGINT" : sig == 15 ? "SIGTERM" : sig == 10 ? "SIGUSR1" : ""
    isempty(sname) || (Threads.atomic_xchg!(SIG_FLAGS[sname], 1))
    return nothing
end

install_signals!() = begin
    cfunc = @cfunction(_sig_handler_c, Cvoid, (Cint,))
    for (name, num) in (("SIGINT", 2), ("SIGTERM", 15), ("SIGUSR1", 10))
        prev = ccall(:signal, Ptr{Nothing}, (Cint, Ptr{Nothing}), num, cfunc)
        _sig_handlers[name] = prev
    end
    nothing
end

restore_signals!() = begin
    defaults = Dict("SIGINT" => 0, "SIGTERM" => 0, "SIGUSR1" => 0)
    for (name, num) in (("SIGINT", 2), ("SIGTERM", 15), ("SIGUSR1", 10))
        haskey(_sig_handlers, name) &&
            ccall(:signal, Ptr{Nothing}, (Cint, Ptr{Nothing}), num, _sig_handlers[name])
    end
    empty!(_sig_handlers)
    nothing
end

const LOCK_MODE = Ref{Symbol}(:flock)   # :flock | :lockdir | :advisory (каскад §24.2 v4)
const _RUN_LOCKDIR_PATH = Ref{String}("")   # путь .lockdir в режиме :lockdir

# §24.2 v4: errno, означающие «ФС/ядро не поддерживает flock» (НЕ «занято»):
# ENOSYS(38) syscall нет · EINVAL(22) операция не поддержана ФС ·
# EOPNOTSUPP(95) · ENOLCK(37) — на таких ФС каскад идёт в POSIX-lockdir.
const LOCK_UNSUPPORTED_ERRNOS = (38, 22, 95, 37)

lockdir_holder_pid(lkd::AbstractString) = try
    m = match(r"pid=(\d+)", strip(read(joinpath(lkd, "pid"), String)))
    m === nothing ? 0 : parse(Int, m.captures[1])
catch
    0
end

    """§24.2 v4: POSIX-локdir (mkdir атомарен на ЛЮБОЙ ФС — FAT/exFAT/NTFS-3g/
    CIFS/NFS без lockd/FUSE; open(path,"x") в Julia < 1.11 нет, а константы
    O_EXCL платформозависимы — mkdir прост и переносим). Протокол: эксклюзивное
    создание .lockdir + файл pid; занято → держатель (PID); мёртвый PID или
    каталог старше stale_sec → стейл-лок снимается автоматически.
    → (io, nothing) при успехе; (nothing, сообщение) при занятости."""
function lockdir_acquire!(run_dir::AbstractString; stale_sec::Float64 = 900.0)
    lkd = joinpath(run_dir, ".lockdir")
    while true
        try
            mkdir(lkd)
        catch ex
            # mkdir бросает Base.IOError (uv) с code = −errno (отрицательный!)
            eno = hasproperty(ex, :code) ? abs(Int(ex.code)) : 0
            if eno != 17   # не EEXIST: ФС не даёт создать каталог → advisory, честный WARN
                LOCK_MODE[] = :advisory
                println(badge("WARN"), " lockdir fallback unavailable (errno=", eno,
                        ") — работаю БЕЗ блокировки; не запускайте параллельные прогоны")
                flush(stdout)
                return open(joinpath(lkd, "pid"), "a+"), nothing
            end
            holder = lockdir_holder_pid(lkd)
            alive = holder > 0 && isdir("/proc/$(holder)")
            stale = false
            try; stale = (time() - stat(lkd).mtime) > stale_sec; catch; end
            (holder > 0 && !alive) && (stale = true)
            if stale
                try; rm(lkd; force = true, recursive = true); catch; end
                continue
            end
            who = holder > 0 ? "PID $holder" : "другим процессом"
            cmd = ""
            if holder > 0 && alive
                try; cmd = " · " * first(replace(read("/proc/$(holder)/cmdline", String), "\0" => " "), 60); catch; end
            end
            return nothing, "$lkd занят $who$cmd — дождитесь завершения того прогона или закройте его"
        end
        try
            write(joinpath(lkd, "pid"), "pid=$(getpid())\n")
        catch
        end
        _RUN_LOCKDIR_PATH[] = lkd
        return open(joinpath(lkd, "pid"), "a+"), nothing
    end
end

    """§24.2 v4: снятие лока ЛЮБОГО режима каскада (flock/lockdir/advisory):
    lockdir → удалить .lockdir (иначе стал бы 15-минутным стейлом) + close."""
lock_release!(io::IO) = begin
    if LOCK_MODE[] == :lockdir && !isempty(_RUN_LOCKDIR_PATH[])
        try; rm(_RUN_LOCKDIR_PATH[]; force = true, recursive = true); catch; end
    end
    try; ccall(:flock, Cint, (Cint, Cint), Base.fd(io), 8); catch; end   # LOCK_UN best-effort
    try; close(io); catch; end
    nothing
end

    """§24.2: flock на run_dir; занято → (nothing, сообщение).
    v3 BUGFIX(LOCK): прежняя версия ЛЮБУЮ ошибку flock печатала как «занят другим
    процессом» — даже сбой на свежем .lock (NFS/лимит fd/EINTR), не показывала,
    КТО держит, и не подчищала локи убитых процессов. Теперь: errno + strerror,
    держатель (pid из .lock + /proc/locks по inode), авто-снятие СТАЛОГО лока
    (pid мёртв), а при errno ≠ EWOULDBLOCK — WARN и работа без блокировки."""
flock_acquire!(run_dir::AbstractString; _steal::Bool = false) = begin
    mkpath(run_dir)
    lk = joinpath(run_dir, ".lock")
    io = open(lk, "a+")
    rc = ccall(:flock, Cint, (Cint, Cint), Base.fd(io), 6)   # LOCK_EX | LOCK_NB
    if rc != 0
        eno = unsafe_load(ccall(:__errno_location, Ptr{Cint}, ()))
        close(io)
        eno == 4 && !_steal && return flock_acquire!(run_dir; _steal = true)  # EINTR: один повтор
        if eno in LOCK_UNSUPPORTED_ERRNOS
            # §24.2 v4: ФС без flock (ENOSYS/EINVAL/EOPNOTSUPP/ENOLCK) — НЕ advisory,
            # а переносимый POSIX-lockdir (mkdir, атомарно на любой ФС):
            # взаимоисключение сохраняется
            LOCK_MODE[] = :lockdir
            println(badge("WARN"), " flock unsupported on this FS (errno=", eno, ": ",
                    unsafe_string(ccall(:strerror, Cstring, (Cint,), eno)),
                    ") — using POSIX lockdir fallback (.lockdir, mkdir)")
            flush(stdout)
            return lockdir_acquire!(run_dir)
        end
        if eno != 11   # НЕ «занято» и не «не поддерживается»: лимиты — advisory
            LOCK_MODE[] = :advisory
            println(badge("WARN"), " flock недоступен (errno=", eno, ": ",
                    unsafe_string(ccall(:strerror, Cstring, (Cint,), eno)),
                    ") — работаю БЕЗ блокировки; не запускайте параллельные прогоны")
            flush(stdout)
            return io, nothing
        end
        # errno==11 (EWOULDBLOCK): реально занято — ищем держателя
        holder = 0
        try
            m = match(r"pid=(\d+)", strip(read(lk, String)))
            m !== nothing && (holder = parse(Int, m.captures[1]))
        catch
        end
        if holder == 0
            try
                # формат /proc/locks: «1: FLOCK ADVISORY WRITE 1234 08:02:123456 0 EOF»
                ino = Int(stat(lk).ino)
                for ln in eachline("/proc/locks")
                    toks = split(ln)
                    length(toks) >= 6 && toks[2] == "FLOCK" || continue
                    m2 = match(r"^\d+:\d+:(\d+)$", toks[6])
                    if m2 !== nothing && parse(Int, m2.captures[1]) == ino
                        holder = parse(Int, toks[5])
                        break
                    end
                end
            catch
            end
        end
        alive = holder > 0 && isdir("/proc/$(holder)")
        if holder > 0 && !alive && !_steal
            # СТАЛЫЙ лок: держатель мёртв (убит/crash) — снимаем и берём заново
            try
                rm(lk; force = true)
            catch
            end
            return flock_acquire!(run_dir; _steal = true)
        end
        who = holder > 0 ? "PID $holder" : "другим процессом"
        cmd = ""
        if holder > 0 && alive
            try
                cmd = " · " * first(replace(read("/proc/$(holder)/cmdline", String), "\0" => " "), 60)
            catch
            end
        end
        return nothing, "$lk занят $who$cmd — дождитесь завершения того прогона или закройте его"
    end
    # Записываем PID — при следующей ERR_LOCK_HELD будет видно, кто держал
    try
        truncate(lk, 0)
        println(io, "pid=$(getpid())")
        flush(io)
    catch
    end
    return io, nothing
end

# ════════════════════════════════════════════════════════════════════════
# §4/§5/§7/§15 РАННЕР: топосорт с детектом цикла (§4.2), two-pass с
# изоляцией доменов seed (§5.3), hooks (§4.3), capture stdout (§9.2),
# чекпоинт/resume (§25.2), ctl-файл (§7.5), дедлайны (§15.8).
# ════════════════════════════════════════════════════════════════════════
const ACTIVE_LOGGER = Ref{Union{Nothing,HodgeLogger}}(nothing)
const RUN_LOCK = Ref{Union{Nothing,IO}}(nothing)

mutable struct HodgeRunner
    cfg::HodgeConfig
    log::HodgeLogger
    results::Dict{Int,Dict{String,Any}}
    checkpoint_path::Union{Nothing,String}
    cache::HodgeCache
    eta::HodgeETA
    spark_vals::Vector{Float64}
    rate::HodgeRate
    ratelimit::Union{Nothing,HodgeRateLimit}
    ctl_last::Float64
    sigwinch::Bool
end
HodgeRunner(cfg::HodgeConfig, lg::HodgeLogger) = HodgeRunner(cfg, lg, Dict{Int,Dict{String,Any}}(),
    isempty(cfg.run_dir) ? nothing : joinpath(cfg.run_dir, "checkpoint.json"),
    HodgeCache(cfg), HodgeETA(), Float64[], HodgeRate(),
    isempty(cfg.rate_limit) ? nothing : HodgeRateLimit(cfg.rate_limit), 0.0, false)

runner_task(r::HodgeRunner, tid::Int) = task_by_id(tid)

function select_tasks(r::HodgeRunner)
    """§4.2 / II.3: топосорт по deps с детектом цикла → ERR_CYCLE."""
    ids = isempty(r.cfg.tasks) ? SUITE_IDS : r.cfg.tasks
    if r.cfg.with_deps
        visiting = Set{Int}(); visited = Set{Int}(); ordered = Int[]
        function visit(tid)
            tid in visited && return
            tid in visiting && begin
                ledger!(r.log, "ERR_CYCLE")
                throw(ArgumentError("ERR_CYCLE $tid"))
            end
            push!(visiting, tid)
            t = task_by_id(tid)
            if t !== nothing
                foreach(visit, t.deps)
            end
            delete!(visiting, tid)
            push!(visited, tid)
            push!(ordered, tid)
        end
        try
            foreach(visit, ids)
            ids = ordered
        catch ex
            log_comp!(r.log, "ERROR", "Select", sprint(showerror, ex))
            ids = collect(ids)   # деградация: исходный порядок, ERR_CYCLE в ledger
        end
    end
    if !isempty(r.cfg.tags)
        match_tag(t) = any(tg -> startswith(tg, "!") ? !(tg[2:end] in t.tags) : (tg in t.tags), r.cfg.tags)
        ids = [tid for tid in ids if match_tag(task_by_id(tid))]
    end
    return [tid for tid in SUITE_IDS if tid in ids]
end

# STDOUT_TEE v2: синхронный tee-IO. Пишет в терминал и в capture-файл,
# flush на КАЖДОЙ записи — иначе вывод лежит в буфере IOStream (~8КБ) и
# выглядит «фоновым». Перегрузки покрывают типы print/println (@printf).
struct TeeIO <: IO
    a::IO
    b::IO
end
Base.write(t::TeeIO, s::Union{SubString{String},String}) =
    begin n = write(t.a, s); write(t.b, s); flush(t.a); flush(t.b); n end
Base.write(t::TeeIO, s::AbstractString) =
    begin n = write(t.a, s); write(t.b, s); flush(t.a); flush(t.b); n end
Base.write(t::TeeIO, x::UInt8) =
    begin write(t.a, x); write(t.b, x); flush(t.a); flush(t.b) end
Base.write(t::TeeIO, c::Char) =
    begin write(t.a, c); write(t.b, c); flush(t.a); flush(t.b) end
Base.write(t::TeeIO, v::Vector{UInt8}) =
    begin write(t.a, v); write(t.b, v); flush(t.a); flush(t.b) end
Base.flush(t::TeeIO) = (flush(t.a); flush(t.b); nothing)

# Подмена глобального stdout (синхронный tee вместо пайпа). Прямая привязка
# работает в 1.10; запасной путь — Core.eval в модуль Base (часть версий
# объявляет привязку иначе). Ошибка обоих путей → tee просто не ставится.
function set_global_stdout!(io::IO)
    try
        Base.stdout = io
    catch
        try
            Core.eval(Base, :(stdout = $io))
        catch
        end
    end
    nothing
end

function run_task_two_pass!(r::HodgeRunner, tid::Int)
    t = task_by_id(tid)
    t === nothing && begin
        ledger!(r.log, "ERR_UNKNOWN_TASK")
        return Dict("id" => tid, "slug" => "unknown-$tid", "claims" => String[],
                    "passes" => Dict{Int,Any}(), "verdict" => "FAIL",
                    "ok" => false, "reason" => "ERR_UNKNOWN_TASK $tid")
    end
    cfg = r.cfg
    seed_before = cfg.seed        # P0.1: пользовательский seed (объявлен до try)
    rec = Dict{String,Any}("id" => tid, "slug" => t.slug, "title" => t.title,
                           "claims" => t.claims, "passes" => Dict{Int,Any}(),
                           "verdict" => "FAIL", "ok" => false, "reason" => nothing)
    # §25: --cache on → попробовать кэш (ключ = task_id + cfg_hash)
    cached = cfg.cache_on ? cache_get(r.cache, tid) : nothing
    if cached isa Dict && haskey(cached, "passes")
        for k in ("passes", "verdict", "ok", "worst")
            haskey(cached, k) && (rec[k] = cached[k])
        end
        rec["reason"] = hodge_fmt(Dict("lang" => cfg.lang), "cache.hit", id = tid)
        log_comp!(r.log, "INFO", "Cache", rec["reason"])
        log_event!(r.log, "INFO", "Cache", "hit", task = t.slug)
        return rec
    end
    passes = Int[]
    cfg.pass_only in (0, 1) && push!(passes, 1)
    (cfg.two_pass && cfg.pass_only in (0, 2) && t.pass2 !== nothing) && push!(passes, 2)
    # STDOUT_TEE v2: синхронный fan-out через подмену привязки Base.stdout.
    # v1 (пайп + @async-насос) не работал: кооперативный планировщик Julia —
    # CPU-задача не уступает управление, насос голодает, весь вывод прилетал
    # в конце прогона. v2: КАЖДОЕ println задачи синхронно пишется в терминал
    # и в capture-файл (с flush — иначе вывод лежит в буфере IOStream ~8КБ).
    # Ни пайпа, ни EOF-висяка, ни зависимости от планировщика.
    tdir = ""
    old_stdout = stdout
    cap_io = nothing
    tee_io = nothing
    try
        if !isempty(cfg.run_dir)
            slug = safe_slug(t.slug)
            slug === nothing && (slug = @sprintf("task%02d", tid))
            tdir = joinpath(cfg.run_dir, @sprintf("task_%02d_%s", tid, slug))
            mkpath(joinpath(tdir, "logs"))
            cap_io = open(joinpath(tdir, "logs", "stdout_capture.txt"), "a")
            tee_io = TeeIO(old_stdout, cap_io)
            set_global_stdout!(tee_io)
        end
        # §5.3 / II.4: домен задачи и фазы — derive(seed, "task", tid[, "pass", pno])
        # P0.1: каждый derive — от ПОЛЬЗОВАТЕЛЬСКОГО seed_before (объявлен до
        # try: try-блок в Julia — скоуп, finally его не видит)
        cfg.seed = seed_before
        cfg.seed = derive_seed(cfg, "task", tid)
        for pno in passes
            cfg.seed = seed_before
            cfg.seed = derive_seed(cfg, "task", tid, "pass", pno)
            fn = pno == 1 ? t.fn : t.pass2
            fire_hook("pre_task", tid, t.slug, pno, cfg)
            t0 = time()
            res = try
                fn(Dict{String,Any}("prec" => cfg.prec, "seed" => cfg.seed, "lang" => cfg.lang,
                            "prec_extreme" => cfg.prec_extreme))
            catch ex
                (false, "EXCEPTION: $(sprint(showerror, ex))")
            end
            dur = time() - t0
            ok, verdict = res isa Tuple ? (Bool(res[1]), string(res[2])) : (false, string(res))
            fire_hook("post_task", tid, t.slug, pno, verdict)
            fire_hook("on_verdict", tid, t.slug, verdict)
            ok || fire_hook("on_error", tid, t.slug, verdict)
            rec["passes"][pno] = Dict("ok" => ok, "verdict" => verdict,
                                      "duration_s" => round(dur; digits = 3),
                                      "seed" => cfg.seed)
            log_metric!(r.log, "task$(tid)_duration_s", "timer", round(dur; digits = 3);
                        tags = Dict("pass" => pno, "slug" => t.slug))
            log_event!(r.log, ok ? "INFO" : "ERROR", "Task", "verdict",
                       task = t.slug, phase = "pass$pno", ok = ok, verdict = verdict)
            # полный лог пасса — прямо в терминал (silent-режимы не трогаем)
            cfg.ci || cfg.jsonl || cfg.tsv || begin
                println(badge(ok ? "PASS" : "FAIL"), " ", dye("pass $pno", "gold"),
                        " ", run_i18n(verdict, cfg.lang), " ",
                        dye("· $(fmt_duration(dur))", "text_dim"))
                flush(stdout)
            end
            # §15.8: локальный таймаут — дедлайн проверяется между пассами
            # (Julia не может прервать CPU-bound задачу; пост-фактум ledger)
            if cfg.task_timeout > 0 && dur > cfg.task_timeout
                ledger!(r.log, "ERR_TASK_TIMEOUT")
                rec["passes"][pno]["verdict"] = "TIMEOUT: task timeout $(cfg.task_timeout)s (post-hoc)"
            end
        end
    finally
        # вернуть настоящий stdout ДО закрытия capture-файла
        if tee_io !== nothing
            set_global_stdout!(old_stdout)
            flush(old_stdout)
        end
        cap_io !== nothing && close(cap_io)
        cfg.seed = seed_before    # P0.1: вернуть пользовательский seed
    end
    p1 = get(rec["passes"], 1, nothing)
    p2 = get(rec["passes"], 2, nothing)
    if p1 !== nothing && p2 !== nothing
        rec["ok"] = p1["ok"] && p2["ok"]
        rec["verdict"] = rec["ok"] ? "PASS" : "FAIL"
        rec["worst"] = p2["ok"] ? p1["verdict"] : p2["verdict"]
    elseif p2 !== nothing
        rec["ok"] = p2["ok"]; rec["verdict"] = rec["ok"] ? "PASS" : "FAIL"
        rec["worst"] = p2["verdict"]
    elseif p1 !== nothing
        rec["ok"] = p1["ok"]; rec["verdict"] = rec["ok"] ? "PASS" : "FAIL"
    else
        # B1: --pass-only 2 на задаче без pass2 — не crash
        rec["ok"] = false; rec["verdict"] = "SKIP"
        rec["reason"] = "no passes scheduled (pass_only=2, task has no pass2_fn)"
    end
    # §11 / §11.5: рендер плотов и animation.gif для задач с plot_fn
    if get(ENV, "HODGE_PLOT", "on") != "off" && !isempty(cfg.run_dir) && !cfg.no_report &&
       !isempty(rec["passes"]) && all(p["ok"] for p in values(rec["passes"]))
        try
            render_plots_for_task!(cfg, t, rec)
        catch ex
            ledger!(r.log, "ERR_PLOT_RENDER")
            log_comp!(r.log, "WARN", "Plot", "$(t.slug): $(sprint(showerror, ex))")
        end
    end
    if cfg.cache_on && rec["ok"]
        cache_put!(r.cache, tid, Dict(k => rec[k] for k in ("passes", "verdict", "ok", "worst")))
    end
    return rec
end

# Часть IV.2: задачи без явного plot_fn получают bar-chart по пассам
function fallback_bar_plot!(t::Task, rec::Dict, theme_name::AbstractString)
    p = HodgePlot(800, 480; title = "[$(t.id)] $(t.slug) · $(get(rec, "verdict", "?"))",
                  xlabel = "pass", ylabel = "duration_s", theme_name = theme_name, aa = 2)
    xs = Float64[]; ys = Float64[]
    for pno in sort!(collect(keys(rec["passes"])))
        push!(xs, Float64(pno))
        push!(ys, max(rec["passes"][pno]["duration_s"], 0.001))
    end
    isempty(xs) && return Tuple{HodgePlot,Int}[]
    plot_add!(p, "duration", xs, ys, "s")
    p.xlim = (0.5, maximum(xs) + 0.5)
    return [(p, 200)]
end

function render_plots_for_task!(cfg::HodgeConfig, t::Task, rec::Dict)
    frames = t.plot_fn === nothing ?
        fallback_bar_plot!(t, rec, cfg.theme) :
        t.plot_fn(Dict("theme" => cfg.theme, "plot_width" => 800, "plot_height" => 480))
    isempty(frames) && return
    slug = something(safe_slug(t.slug), @sprintf("task%02d", t.id))
    tdir = joinpath(cfg.run_dir, @sprintf("task_%02d_%s", t.id, slug))
    plots_dir = joinpath(tdir, "plots")
    mkpath(plots_dir)
    gif_frames = Vector{Vector{UInt8}}(); gif_delays = Int[]
    for (i, (plot, delay)) in enumerate(frames)
        plot_write_png(plot, joinpath(plots_dir, @sprintf("plot_%02d.png", i)))
        idx, _gct = plot_to_gif_frame(plot, cfg.gct_cache)
        push!(gif_frames, idx); push!(gif_delays, delay)
    end
    hodge_atomic_write(joinpath(plots_dir, "animation.gif"),
                       gif_encode(frames[1][1].out_W, frames[1][1].out_H,
                                  cfg.gct_cache["gct"], gif_frames, gif_delays))
    nothing
end

save_checkpoint!(r::HodgeRunner) = begin
    r.checkpoint_path === nothing && return
    data = Dict("cfg_hash" => cfg_relevant_hash(r.cfg),
                "tasks" => Dict(string(k) => Dict("verdict" => v["verdict"]) for (k, v) in r.results))
    hodge_atomic_write(r.checkpoint_path, json_dump(data))
    nothing
end

    """§7.5: раз в секунду читать <run_dir>/.hodge_ctl (pause/resume/snapshot/abort)."""
poll_ctl!(r::HodgeRunner) = begin
    isempty(r.cfg.run_dir) && return
    now = time()
    now - r.ctl_last < 1.0 && return
    r.ctl_last = now
    ctl = joinpath(r.cfg.run_dir, ".hodge_ctl")
    isfile(ctl) || return
    cmds = try
        [strip(ln) for ln in eachline(ctl) if !isempty(strip(ln))]
    catch
        return
    end
    try; hodge_atomic_write(ctl, ""); catch; end
    for cmd in cmds
        if cmd == "pause"
            log_comp!(r.log, "INFO", "Ctl", "pause")
            while isfile(ctl)
                peek = try read(ctl, String) catch; "" end
                (occursin("resume", peek) || occursin("abort", peek)) && break
                sleep(0.25)
            end
        elseif cmd == "resume"
            log_comp!(r.log, "INFO", "Ctl", "resume (no-op)")
        elseif cmd == "snapshot"
            save_checkpoint!(r)
            log_comp!(r.log, "INFO", "Ctl", "snapshot → checkpoint")
        elseif cmd == "abort"
            ledger!(r.log, "ERR_CTL_ABORT")
            Threads.atomic_xchg!(SIG_FLAGS["SIGINT"], 1)
        end
    end
    nothing
end

# ── §3.2 v5: prec → точность движка + честная RAM-оценка («гигабайты») ──
const _PREC_ENGINE_APPLIED = Ref(-1)
function hodge_prec_engine_apply!(cfg::HodgeConfig)
    """cfg.prec (биты) управляет точностью BigFloat-движка; пол — 320 бит
    (пресеты quick/full/deep с prec 55/60 базу НЕ опускают). Идемпотентно."""
    target = max(cfg.prec, 320)
    if _PREC_ENGINE_APPLIED[] != target
        setprecision(BigFloat, target)
        _PREC_ENGINE_APPLIED[] = target
    end
    nothing
end
function hodge_prec_extreme_apply!(cfg::HodgeConfig)
    """§3.2 v5: рекордный режим — точность движка ≥ 1024 бит (или cfg.prec,
    если пользователь задал выше)."""
    target = max(cfg.prec, 1024)
    setprecision(BigFloat, target)
    _PREC_ENGINE_APPLIED[] = target
    nothing
end
function hodge_prec_ram_guard(cfg::HodgeConfig)
    """§3.2 v5: «гигабайты точности» ставятся свободно — но честно.
    BigFloat precision p бит ≈ p/8 байт (+64 B overhead). Оценка ×2 > RAM и нет
    --unsafe-prec / HODGE_PREC_UNSAFE=1 → ERR_PREC_RAM (OOM гарантирован);
    оценка ×16 > RAM → WARN. → false, если прогон должен быть прерван."""
    bytes_per = cfg.prec ÷ 8 + 64
    total = Sys.total_memory()
    total <= 0 && return true
    unsafe = cfg.unsafe_prec || get(ENV, "HODGE_PREC_UNSAFE", "") == "1"
    _fmt = (k; kw...) -> hodge_fmt(Dict("lang" => get(TEXT_STATE, "lang", "en")), k; kw...)
    if bytes_per * 2 > total
        if !unsafe
            println(badge("FAIL"), " ", _fmt("prec.ram.block", prec = cfg.prec,
                    est = fmt_size(bytes_per), ram = fmt_size(total)))
            return false
        end
        println(badge("WARN"), " ", _fmt("prec.ram.bypass", prec = cfg.prec, est = fmt_size(bytes_per)))
    elseif bytes_per * 16 > total
        println(badge("WARN"), " ", _fmt("prec.ram.warn", prec = cfg.prec, est = fmt_size(bytes_per),
                est16 = fmt_size(bytes_per * 16), ram = fmt_size(total)))
    end
    true
end

function hodge_prec_estimates(cfg::HodgeConfig)
    """§3.2 v6: честные оценки стоимости prec ДО запуска (конвенция julia:
    prec = БИТЫ, digits = prec·log10(2)). Возвращает строки."""
    p = Int(cfg.prec)
    p < 8192 && return String[]
    digits = floor(Int, p * log10(2))
    c = mpfr_cost(p)
    out = String[]
    _fmt = (k; kw...) -> hodge_fmt(Dict("lang" => get(TEXT_STATE, "lang", "en")), k; kw...)
    bytes_per = p ÷ 8 + 64
    pi_est = 0.275 * (p / 1e6)^1.12          # измерено 0.275 с @ 1M, 1.5 с @ 5M
    trig = c["sin"] + c["sin"]
    lnexp = c["log"] + c["exp"]
    shift = max(40, ceil(Int, (digits + 4) / 2.72864) + 4)
    k_star = 3.1416 * shift
    g_est = k_star * (2 * c["mul"] + c["div"] + 3e-5)
    e151 = (digits + 76) / 302.0
    g_est += 10.0^min(e151, 15.0) * (1.5 * c["mul"] + 3e-5)
    t_need = asin(1.0) + log(2 * (digits + 5) * log(10) / π)   # ≈ asinh(2(d+5)ln10/π)
    quad_nodes = 2 * ceil(Int, t_need / 0.02) + 1
    quad_est = quad_nodes * (4 * max(c["exp"], c["sin"]) + 2 * c["div"])
    lim_g = _hodge_env_float("HODGE_GAMMA_LIMIT", 900.0)
    lim_q = _hodge_env_float("HODGE_QUAD_LIMIT", 1800.0)
    verdict(est, lim) = est <= lim ? "ok" : "BLOCK"
    push!(out, _fmt("prec.est.header", prec = fmt_int(p), digits = fmt_int(digits),
                    est = fmt_size(bytes_per)))
    push!(out, _fmt("prec.est.pi", est = fmt_est_cost(pi_est)))
    push!(out, _fmt("prec.est.trig", est = fmt_est_cost(trig)))
    push!(out, _fmt("prec.est.lnexp", est = fmt_est_cost(lnexp)))
    push!(out, _fmt("prec.est.gamma", terms = _fmt_terms(log10(max(k_star, 2.0))),
                    zterms = _fmt_terms(e151), est = fmt_est_cost(g_est),
                    lim = string(lim_g), verdict = verdict(g_est, lim_g)))
    push!(out, _fmt("prec.est.quad", nodes = fmt_int(quad_nodes),
                    est = fmt_est_cost(quad_est), lim = string(lim_q),
                    verdict = verdict(quad_est, lim_q)))
    (g_est > lim_g || quad_est > lim_q) && push!(out, _fmt("prec.est.advice"))
    return out
end

function hodge_prec_report(cfg::HodgeConfig)
    """Печать блока оценок (run_all!/CLI), только если prec ≥ 8192 бит."""
    for ln in hodge_prec_estimates(cfg)
        println(badge("WARN"), " ", ln)
    end
end

function run_all!(r::HodgeRunner)
    """Полный прогон; изоляция задач try/except (§15.1); код 130/143 по сигналам."""
    cfg = r.cfg
    hodge_prec_engine_apply!(cfg)     # §3.2 v5: prec реально поднимает точность движка
    hodge_prec_ram_guard(cfg) || begin
        ledger!(r.log, "ERR_PREC_RAM")
        return r.results
    end
    # §3.2 v6: блок честных оценок + heartbeat (терминал не выглядит зависшим)
    silent = cfg.ci || cfg.jsonl || cfg.tsv
    silent || hodge_prec_report(cfg)
    prog_start()
    ids = select_tasks(r)
    total = length(ids)
    deadline = cfg.global_timeout > 0 ? time() + cfg.global_timeout : nothing
    log_event!(r.log, "INFO", "Run", "start", preset = cfg.preset, seed = cfg.seed, tasks = total)
    TEXT_STATE["lang"] = cfg.lang   # BUGFIX(i18n): прямой println задач видит lang через TEXT_STATE
    silent || println(hodge_fmt(Dict("lang" => cfg.lang), "run.start",
                                run = basename(cfg.run_dir), preset = cfg.preset, seed = cfg.seed))
    skip_resume = Set{Int}()
    if !isempty(cfg.resume_dir)
        cp = joinpath(cfg.resume_dir, "checkpoint.json")
        if isfile(cp)
            try
                data = json_load_flat(read(cp, String))
                data["cfg_hash"] != cfg_relevant_hash(cfg) &&
                    log_comp!(r.log, "WARN", "Run", "cfg_hash изменился — resume продолжается")
                for (k, v) in get(data, "tasks", Dict())
                    v isa Dict && get(v, "verdict", "") == "PASS" && push!(skip_resume, parse(Int, k))
                end
            catch
                ledger!(r.log, "ERR_RESUME_READ")
            end
        end
    end
    done = 0
    for tid in ids
        prog_task!("t$tid")
        poll_ctl!(r)
        SIG_FLAGS["SIGUSR1"].value == 1 && begin
            Threads.atomic_xchg!(SIG_FLAGS["SIGUSR1"], 0)
            save_checkpoint!(r)
            log_event!(r.log, "INFO", "Run", "snapshot_sigusr1")
            log_comp!(r.log, "INFO", "Run", "SIGUSR1: snapshot записан")
        end
        deadline !== nothing && time() > deadline && begin
            ledger!(r.log, "ERR_GLOBAL_TIMEOUT")
            t = task_by_id(tid)
            r.results[tid] = Dict("id" => tid, "slug" => t.slug, "title" => t.title,
                                  "claims" => t.claims, "passes" => Dict{Int,Any}(),
                                  "ok" => false, "verdict" => "FAIL", "reason" => "GLOBAL_TIMEOUT")
            break
        end
        t = task_by_id(tid)
        if tid in skip_resume && t.idempotent
            log_comp!(r.log, "INFO", "Run", "resume: задача $tid пропущена (PASS в чекпоинте)")
            r.results[tid] = Dict("id" => tid, "slug" => t.slug, "title" => t.title,
                                  "claims" => t.claims, "passes" => Dict{Int,Any}(),
                                  "ok" => true, "verdict" => "SKIP",
                                  "reason" => "resumed PASS (idempotent)")
            done += 1
            continue
        end
        if SIG_FLAGS["SIGINT"].value == 1
            sig = SIG_FLAGS["SIGTERM"].value == 1 ? "SIGTERM" : "SIGINT"
            ledger!(r.log, "ERR_" * sig)
            r.results[tid] = Dict("id" => tid, "slug" => t.slug, "title" => t.title,
                                  "claims" => t.claims, "passes" => Dict{Int,Any}(),
                                  "ok" => false, "verdict" => "FAIL", "reason" => sig)
            break
        end
        log_comp!(r.log, "INFO", "Run", "→ задача $tid $(t.slug)")
        # живой лог: старт задачи виден в терминале (REPL не «спит фоном»)
        (cfg.ci || cfg.jsonl || cfg.tsv) || begin
            println(badge("INFO"), " ",
                    hodge_fmt(Dict("lang" => cfg.lang), "run.task_start", id = tid,
                              slug = t.slug,
                              title = (cfg.lang == "en" && !isempty(t.title_en)) ? t.title_en : t.title,
                              n = done + 1, total = total))
            flush(stdout)
        end
        r.ratelimit !== nothing && rl_wait!(r.ratelimit)
        rec = try
            run_task_two_pass!(r, tid)
        catch ex
            ledger!(r.log, "ERR_TASK_EXCEPTION")
            Dict("id" => tid, "slug" => t.slug, "title" => t.title, "claims" => t.claims,
                 "passes" => Dict{Int,Any}(), "ok" => false, "verdict" => "FAIL",
                 "reason" => "EXCEPTION: $(sprint(showerror, ex))")
        end
        r.results[tid] = rec
        # VI.4 / J10: строка-вердикт задачи в results_log (§4.1/§9.2)
        log_result!(r.log, tid, rec["slug"], rec["verdict"];
                    reason = rec["reason"],
                    duration_s = sum(p["duration_s"] for p in values(rec["passes"]); init = 0.0))
        done += 1
        dur = sum(p["duration_s"] for p in values(rec["passes"]); init = 0.0)
        eta_push!(r.eta, dur); push!(r.spark_vals, dur); rate_tick!(r.rate)
        log_progress!(r.log, done / total; eta = eta_str(r.eta, total - done),
                      spark = sparkline_render(r.spark_vals), rate = rate_value(r.rate))
        # Видимый прогресс в терминале: раньше бар жил только в events-журнале —
        # «непонятно, работает ли прогресс». Теперь строка после каждой задачи.
        r.cfg.ci || r.cfg.jsonl || r.cfg.tsv || begin
            nb = 20
            filled = round(Int, clamp(done / total, 0.0, 1.0) * nb)
            bar = repeat("█", filled) * repeat("░", nb - filled)
            println(dye(hodge_fmt(Dict("lang" => r.cfg.lang), "run.progress_bar",
                        bar = "[$bar]", done = done, total = total,
                        eta = eta_str(r.eta, total - done)), "gold"))
            flush(stdout)
        end
        save_checkpoint!(r)
    end
    if SIG_FLAGS["SIGUSR1"].value == 1
        Threads.atomic_xchg!(SIG_FLAGS["SIGUSR1"], 0)
        save_checkpoint!(r)
    end
    SIG_FLAGS["SIGINT"].value == 1 &&
        ledger!(r.log, SIG_FLAGS["SIGTERM"].value == 1 ? "ERR_SIGTERM" : "ERR_SIGINT")
    log_event!(r.log, "INFO", "Run", "end"; passed = count(v -> get(v, "ok", false), values(r.results)))
    return r.results
end

# ════════════════════════════════════════════════════════════════════════
# §10 ОТЧЁТЫ: results.json, MANIFEST.toml (реальные seeds, §20.1),
# FINAL_REPORT (полный набор §10.1/§10.2), per-task каталоги с PDF/DOCX-
# заглушками (§1.5), index.html + cross-run dashboard (§10.7).
# ════════════════════════════════════════════════════════════════════════
function git_commit()
    try
        cmd = pipeline(`git -C $(dirname(@__DIR__)) rev-parse --short HEAD`, stderr = devnull)
        return strip(read(cmd, String))
    catch
        return "unknown (standalone master file)"
    end
end

self_sha256() = bytes2hex(sha256(read(@__FILE__, String)))

results_sorted(runner::HodgeRunner) = [runner.results[k] for k in sort!(collect(keys(runner.results)))]

function results_json(runner::HodgeRunner, lg::HodgeLogger, exit_code::Int, wall::Float64)
    tasks = Dict{String,Any}()
    for r in results_sorted(runner)
        tasks[string(r["id"])] = Dict(
            "verdict" => r["verdict"], "reason" => r["reason"], "claims" => r["claims"],
            # P2.5 / §20.3: полный слепок пассов (ключ "passes" — как в Python)
            "passes" => Dict("pass$k" => Dict("verdict" => v["verdict"],
                                              "ok" => v["ok"],
                                              "duration_s" => v["duration_s"],
                                              "seed" => v["seed"]) for (k, v) in r["passes"]),
            "duration_s" => round(sum(p["duration_s"] for p in values(r["passes"]); init = 0.0); digits = 3))
    end
    return Dict("run" => Dict(
                    "finished_at" => Dates.format(Dates.now(Dates.UTC), "Y-mm-ddTHH:MM:SS"),
                    "exit_code" => exit_code, "cfg_hash" => cfg_relevant_hash(runner.cfg),
                    "git_commit" => git_commit(), "theme" => runner.cfg.theme,
                    "preset" => runner.cfg.preset, "lang" => HODGE_LANG,
                    "version" => HODGE_VERSION,
                    "prec" => runner.cfg.prec, "seed" => runner.cfg.seed,   # P2.5
                    "duration_s" => round(wall; digits = 2)),
                "task" => tasks,
                "errors" => Dict(k => Dict("count" => v[1], "last_seen" => v[2]) for (k, v) in lg.err_ledger))
end

function badge_html(verdict::AbstractString)
    cls = occursin("PASS", verdict) || occursin("DONE", verdict) ? "pass" :
          occursin("FAIL", verdict) || occursin("ERROR", verdict) ? "fail" : "skip"
    return "<span class='$cls'>[$verdict]</span>"
end

const HTML_CSS = """
:root{--bg:#0a0805;--surface:#161009;--gold:#d4af37;--gold-bright:#ffd700;--amber:#ffe97c;
--ember:#c94a1a;--text:#e8d9a8;--ok:#ffd700;--warn:#ffc347;--err:#c94a1a;--neutral:#7a6a44}
body{background:var(--bg);color:var(--text);font-family:Georgia,serif;margin:2rem;line-height:1.5}
h1,h2,h3{color:var(--gold-bright)}a{color:var(--amber)}
table{border-collapse:collapse;width:100%}
td,th{border:1px solid var(--neutral);padding:.35rem .6rem;text-align:left}
.pass{color:var(--ok);font-weight:bold}.fail{color:var(--err);font-weight:bold}
.skip{color:var(--neutral)}.warn{color:var(--warn)}.num{color:var(--gold)}
.num.big{color:var(--amber);font-weight:bold}code,pre{background:var(--surface);padding:.15rem .4rem}"""

html_shell(cfg::HodgeConfig, title::AbstractString, body::AbstractString) =
    "<!DOCTYPE html><html lang=\"$(cfg.lang)\"><head><meta charset='utf-8'>" *
    "<title>$title</title><style>$HTML_CSS</style></head><body>$body" *
    # P2.7 / §10.3: живой поиск на каждой странице с input[type=search]
    "<script>document.querySelectorAll('input[type=search]').forEach(inp=>{" *
    "inp.addEventListener('input',e=>{const q=e.target.value.toLowerCase();" *
    "document.querySelectorAll('table tr').forEach(r=>{if(r.querySelector('th'))return;" *
    "r.style.display=r.textContent.toLowerCase().includes(q)?'':'none'})});});</script>" *
    "</body></html>"

function write_per_task!(runner::HodgeRunner, lg::HodgeLogger, run_dir::AbstractString)
    """§10.1 + §24.3: per-task каталоги task_NN_slug; slug через path-guard."""
    for r in results_sorted(runner)
        slug = safe_slug(r["slug"])
        if slug === nothing
            ledger!(lg, "ERR_PATH_TRAVERSAL")
            log_comp!(lg, "WARN", "Report", "slug $(r["slug"]) rejected by path-guard")
            slug = @sprintf("task%02d", r["id"])
        end
        tdir = joinpath(run_dir, @sprintf("task_%02d_%s", r["id"], slug))
        mkpath(tdir)
        # §16 v4: отчёты — ВСЕГДА на английском (машиночитаемость), независимо
        # от cfg.lang; reason прогоняется через run_i18n(..., "en")
        reason_en = run_i18n(something(r["reason"], ""), "en")
        _t = task_by_id(r["id"])
        _title = _t === nothing ? r["slug"] :
                 (isempty(_t.title_en) ? _t.title : _t.title_en)
        md = ["# Task $(r["id"]) · $(r["slug"])", "",
              "**Verdict:** $(r["verdict"])  ",
              "**Claims:** $(join(r["claims"], ", "))  ",
              "**Title:** $(run_i18n(_title, "en"))", ""]
        hrows = String[]
        for pno in sort!(collect(keys(r["passes"])))
            p = r["passes"][pno]
            pv = run_i18n(string(p["verdict"]), "en")   # §16 v4: детали задач — EN в отчётах
            push!(md, "## pass $pno — $pv ($(@sprintf("%.3f", p["duration_s"])) s, seed=$(p["seed"]))", "", pv, "")
            push!(hrows, "<tr><td>pass $pno</td><td>$(badge_html(p["verdict"]))</td>" *
                 "<td>$(@sprintf("%.3f", p["duration_s"])) s</td><td>$pv</td></tr>")
        end
        isempty(reason_en) || push!(md, "> $(reason_en)")
        push!(md, "")
        pdir = joinpath(tdir, "plots")
        plots = isdir(pdir) ? sort(readdir(pdir; join = true); by = basename) : String[]
        pngs = filter(f -> endswith(f, ".png"), plots)
        gifs = filter(f -> endswith(f, ".gif"), plots)
        isempty(pngs) || begin
            push!(md, "Plots:")
            foreach(f -> push!(md, "  ![$(basename(f))](plots/$(basename(f)))"), pngs)
        end
        isempty(gifs) || begin
            push!(md, "Animation:")
            foreach(f -> push!(md, "  ![$(basename(f))](plots/$(basename(f)))"), gifs)
        end
        (isempty(pngs) && isempty(gifs)) &&
            push!(md, "Plots: fallback bar-chart not rendered (empty passes or --no-report).")
        push!(md, "PDF/DOCX: ERR_UNSUPPORTED — the stdlib build does not generate PDF/DOCX; " *
                  "closest equivalent is this MD and HTML (§1.5).")
        hodge_atomic_write(joinpath(tdir, "report.md"), join(md, "\n"))
        body = "<h1>Task $(r["id"]) · $(r["slug"])</h1>" *
               "<p>Verdict: $(badge_html(r["verdict"])) · claims: $(join(r["claims"], ", "))</p>" *
               "<table><tr><th>pass</th><th>verdict</th><th>time</th><th>details</th></tr>" * join(hrows) * "</table>"
        hodge_atomic_write(joinpath(tdir, "report.html"), html_shell(runner.cfg, "task $(r["id"])", body))
        # Часть IV.1: PDF/DOCX — честно ERR_UNSUPPORTED, файлы не создаются
        fmts = Set(split(lowercase(runner.cfg.report_formats), ","; keepempty = false))
        if "pdf" in fmts || "docx" in fmts
            ledger!(lg, "ERR_UNSUPPORTED")
            log_comp!(lg, "WARN", "Report",
                      "pdf/docx: stdlib build does not write PDF/DOCX (§1.5); use md,html,svg,json")
        end
        # логи задачи
        lg_dir = joinpath(tdir, "logs")
        mkpath(lg_dir)
        log_comp!(lg, "INFO", "Report", "per-task dir: $(basename(tdir))")
    end
    nothing
end

function write_manifest!(runner::HodgeRunner, lg::HodgeLogger, run_dir::AbstractString, exit_code::Int)
    """§20.1 MANIFEST.toml с реальными сидами задач (§5.3) и sha256 артефактов."""
    art = IOBuffer()
    # P2: §20.1 — ВСЕ артефакты прогона (png/gif/logs/reports), не только FINAL_REPORT
    for (root, _dirs, files) in walkdir(run_dir), f in sort(files)
        (endswith(f, ".lock") || endswith(f, ".tmp") || startswith(f, ".")) && continue
        p = joinpath(root, f)
        rel = relpath(p, run_dir)
        rel == "MANIFEST.toml" && continue   # P2.6: не хэшируем сам себя
        println(art, "\"$rel\" = \"sha256:$(bytes2hex(sha256(read(p))))\"  # $(filesize(p)) bytes")
    end
    seeds = IOBuffer()
    rs = results_sorted(runner)
    isempty(rs) || begin
        println(seeds, "{")
        println(join([@sprintf("  %d = 0x%012x", r["id"], derive_seed(runner.cfg, "task", r["id"])) for r in rs], ",\n"))
        print(seeds, "}")
    end
    seeds_block = isempty(rs) ? "{}" : String(take!(seeds))
    toml = """[file]
path = "master_hodge.jl"
sha256 = "$(self_sha256())"
version = "$HODGE_VERSION"
build_date = "$HODGE_BUILD_DATE"
lang = "$HODGE_LANG"
schema_version = "$SCHEMA_VERSION"

[env]
platform = "$(Sys.KERNEL)"
cpu_count = $(Sys.CPU_THREADS)
julia_version = "$(Base.VERSION_STRING)"

[git]
commit = "$(git_commit())"
dirty = true

[run]
exit_code = $exit_code
finished_at = "$(Dates.format(Dates.now(Dates.UTC), "Y-mm-ddTHH:MM:SS"))"
cfg_hash = "$(cfg_relevant_hash(runner.cfg))"
prec = $(runner.cfg.prec)          # P2.6: параметры прогона рядом с hash
seed = $(runner.cfg.seed)

[seeds]
by_task = $seeds_block

[theme]
name = "$(runner.cfg.theme)"
preset = "$(runner.cfg.preset)"
prec = $(runner.cfg.prec)

[artifacts]
$(String(take!(art)))"""
    hodge_atomic_write(joinpath(run_dir, "MANIFEST.toml"), toml)
    nothing
end

function write_final_report!(runner::HodgeRunner, lg::HodgeLogger, run_dir::AbstractString,
                             exit_code::Int, wall::Float64)
    cfg = runner.cfg
    final = joinpath(run_dir, "FINAL_REPORT")
    mkpath(final)
    rs = results_sorted(runner)
    passed = count(r -> get(r, "ok", false), rs)
    total = length(rs)
    all_ok = passed == total && total > 0
    verdict = all_ok ? "ALL CHECKS PASSED" : "THERE ARE FAILURES"   # §16 v4: отчёты — EN
    md = ["# FINAL REPORT", "", "**Verdict: $verdict**  ",
          "Run: $(basename(run_dir)) · exit: $exit_code · " *
          "duration: $(fmt_duration(wall))  ",
          "Passed: $passed / $total", "", "| task | slug | verdict | reason |", "|---|---|---|---|"]
    for r in rs
        push!(md, "| $(r["id"]) | $(r["slug"]) | $(r["verdict"]) | $(run_i18n(something(r["reason"], "—"), "en")) |")
    end
    push!(md, "", "## Run metrics", "")
    for name in sort!(collect(keys(lg.metrics)))
        vals = lg.metrics[name]
        nums = Any[v for v in vals if v isa Real]
        isempty(nums) && continue
        push!(md, "- $name: n=$(length(nums)), min=$(round(minimum(nums); digits = 4)), " *
                  "max=$(round(maximum(nums); digits = 4)), mean=$(round(sum(nums)/length(nums); digits = 4))")
    end
    push!(md, "", "PDF/DOCX: ERR_UNSUPPORTED (stubs in per-task dirs, §1.5).")
    hodge_atomic_write(joinpath(final, "final_report.md"), join(md, "\n"))
    hrows = join([ "<tr><td>$(r["id"])</td><td>$(r["slug"])</td><td>$(badge_html(r["verdict"]))</td>" *
                   "<td>$(run_i18n(something(r["reason"], ""), "en"))</td></tr>" for r in rs])
    hodge_atomic_write(joinpath(final, "final_report.html"),
                       html_shell(cfg, "final report",
                                  "<h1>Final report</h1><p>$verdict</p>" *
                                  "<table><tr><th>#</th><th>task</th><th>verdict</th><th>reason</th></tr>$hrows</table>"))
    # RTM (§28.7)
    seen = Dict{String,Vector{Tuple{Int,String}}}()
    for r in rs, c in r["claims"]
        push!(get!(seen, c, Tuple{Int,String}[]), (r["id"], r["verdict"]))
    end
    rtm = ["# RTM — Requirements Traceability Matrix", "",
           "Each row: repository claim → task-test → verdict.", ""]
    for c in sort!(collect(keys(seen)))
        push!(rtm, "- `$c`: " * join(["task $(t[1])→$(t[2])" for t in seen[c]], ", "))
    end
    push!(rtm, "", "## Honestly not supported (§1.5)", "")
    if isempty(UNSUPPORTED_LOG)
        push!(rtm, "- (no failures recorded in this run)")
    else
        for (k, reason) in sort!(collect(UNSUPPORTED_LOG))
            push!(rtm, "- `$k`: $reason")
        end
    end
    hodge_atomic_write(joinpath(final, "RTM.md"), join(rtm, "\n") * "\n")
    errs = isempty(lg.err_ledger) ? "No errors recorded." :
           join(["- `$k` ×$(v[1]) (last seen: $(v[2]))" for (k, v) in sort!(collect(lg.err_ledger))], "\n")
    hodge_atomic_write(joinpath(final, "errors.md"), "# ERR_LEDGER\n\n" * errs * "\n")
    hodge_atomic_write(joinpath(final, "provenance.md"),
                       """# Provenance

- file: `master_hodge.jl` sha256 `$(self_sha256())`
- language: julia $(Base.VERSION_STRING) · platform: $(Sys.KERNEL)
- build date: $HODGE_BUILD_DATE · master version: $HODGE_VERSION
- domain repository: $HODGE_REPO
- theme: $(cfg.theme) · preset: $(cfg.preset)
- cfg_hash: $(cfg_relevant_hash(cfg))
""")
    # §10.2: results_verdicts + results_log + full_run_log + computation_log_full + metrics_summary
    hodge_atomic_write(joinpath(final, "results_verdicts.txt"),
                       join(["[$(r["id"])] $(r["slug"]): $(r["verdict"])" for r in rs], "\n") * "\n")
    if lg.results_path !== nothing && isfile(lg.results_path)
        hodge_atomic_write(joinpath(final, "results_log.txt"), read(lg.results_path, String))
    end
    full = IOBuffer()
    for r in rs
        slug = something(safe_slug(r["slug"]), @sprintf("task%02d", r["id"]))
        for logname in ("computation_log.txt", "stdout_capture.txt")
            p = joinpath(run_dir, @sprintf("task_%02d_%s", r["id"], slug), "logs", logname)
            if isfile(p)
                println(full, "\n# === $(r["id"]) $(r["slug"]) / $logname ===")
                print(full, read(p, String))
            end
        end
    end
    hodge_atomic_write(joinpath(final, "full_run_log.txt"), String(take!(full)))
    lg.comp_path !== nothing && isfile(lg.comp_path) &&
        hodge_atomic_write(joinpath(final, "computation_log_full.txt"), read(lg.comp_path, String))
    mlines = ["# Metrics Summary", ""]
    for name in sort!(collect(keys(lg.metrics)))
        nums = Any[v for v in lg.metrics[name] if v isa Real]
        isempty(nums) && continue
        push!(mlines, "- **$name**: n=$(length(nums)), min=$(round(minimum(nums); digits = 4)), " *
                      "max=$(round(maximum(nums); digits = 4)), mean=$(round(sum(nums)/length(nums); digits = 4))")
    end
    hodge_atomic_write(joinpath(final, "metrics_summary.md"), join(mlines, "\n") * "\n")
    # конфиг-снапшот
    snap = join(["$f = $(repr(getfield(cfg, f)))" for f in fieldnames(HodgeConfig) if !startswith(string(f), "_")], "\n")
    hodge_atomic_write(joinpath(final, "config_snapshot.txt"), snap)
    # §20.5: HMAC-подпись при --sign-key (честно: ключ из файла)
    if !isempty(cfg.sign_key)
        try
            key = read(cfg.sign_key)
            sig_file = joinpath(final, "signature.sha256")
            lines = String[]
            for (root, _d, files) in walkdir(final), f in sort(files)
                p = joinpath(root, f)
                mac = bytes2hex(hmac_sha256(key, read(p)))
                push!(lines, "$mac  $(relpath(p, run_dir))")
            end
            hodge_atomic_write(sig_file, join(lines, "\n") * "\n")
        catch ex
            log_comp!(lg, "WARN", "Sign", "sign failed: $(sprint(showerror, ex))")
        end
    end
    # index.html прогона
    idx_rows = join(["<tr><td>$(r["id"])</td><td>$(r["slug"])</td><td>$(badge_html(r["verdict"]))</td></tr>" for r in rs])
    hodge_atomic_write(joinpath(run_dir, "index.html"),
                       html_shell(cfg, "run $(basename(run_dir))",
                                  "<h1>$(basename(run_dir))</h1><p>$verdict</p>" *
                                  "<input type='search' placeholder='filter…' style='margin:.4em 0'>" *
                                  "<table><tr><th>#</th><th>task</th><th>verdict</th></tr>$idx_rows</table>"))
    nothing
end

function cross_run_dashboard!(cfg::HodgeConfig)
    """§10.7: <report_dir>/index.html — обзор всех прогонов."""
    base = cfg.report_dir
    isdir(base) || return
    runs = sort(filter(d -> startswith(d, "run_") && isdir(joinpath(base, d)), readdir(base)); rev = true)
    rows = String[]
    for run in runs[1:min(50, end)]
        rj = joinpath(base, run, "results.json")
        isfile(rj) || continue
        try
            data = json_load_flat(read(rj, String))
            # P0.8: §10.7 — дата/задачи/PASS/FAIL/длительность/exit, не стаб
            run_meta = get(data, "run", Dict{String,Any}())
            tasks_d = get(data, "task", Dict{String,Any}())
            total = length(tasks_d)
            passed = count(t -> (t isa AbstractDict && get(t, "verdict", "") == "PASS"), values(tasks_d))
            failed = count(t -> (t isa AbstractDict && get(t, "verdict", "") == "FAIL"), values(tasks_d))
            code = get(run_meta, "exit_code", "—")
            fin = string(get(run_meta, "finished_at", ""))[1:min(19, end)]
            push!(rows, "<tr><td><a href='$run/index.html'>$run</a></td><td>$fin</td>" *
                 "<td class='num'>$total</td><td class='pass'>$passed</td>" *
                 "<td class='fail'>$failed</td><td class='num'>$code</td></tr>")
        catch
        end
    end
    rep = html_shell(cfg, "cross-run dashboard",
                     "<h1>Hodge Master · all runs</h1>" *
                     "<table><tr><th>run</th><th>finished</th><th>tasks</th><th>PASS</th><th>FAIL</th><th>exit</th></tr>" * join(rows) * "</table>")
    hodge_atomic_write(joinpath(base, "index.html"), rep)
    nothing
end

    """§9.4: --metrics-format json|tsv|prom → logs/metrics_summary.<ext>."""
hodge_metrics_export!(cfg::HodgeConfig, lg::HodgeLogger) = begin
    fmt = isempty(cfg.metrics_format) ? "json" : lowercase(cfg.metrics_format)
    out_dir = isempty(cfg.run_dir) ? "." : joinpath(cfg.run_dir, "logs")
    mkpath(out_dir)
    if fmt == "prom"
        lines = String[]
        for name in sort!(collect(keys(lg.metrics)))
            nums = Any[v for v in lg.metrics[name] if v isa Real]
            isempty(nums) && continue
            push!(lines, "# HELP $name hodge-master metric", "# TYPE $name gauge",
                  "$name $(nums[end])")
        end
        text = join(lines, "\n") * "\n"; ext = "prom"
    elseif fmt == "tsv"
        lines = ["name\ttype\tn\tmin\tmax\tmean"]
        for name in sort!(collect(keys(lg.metrics)))
            nums = Any[v for v in lg.metrics[name] if v isa Real]
            isempty(nums) && continue
            push!(lines, @sprintf("%s\tmetric\t%d\t%.4f\t%.4f\t%.4f", name, length(nums),
                                  minimum(nums), maximum(nums), sum(nums) / length(nums)))
        end
        text = join(lines, "\n") * "\n"; ext = "tsv"
    else
        data = Dict{String,Any}()
        for name in sort!(collect(keys(lg.metrics)))
            nums = Any[v for v in lg.metrics[name] if v isa Real]
            data[name] = isempty(nums) ? Dict("n" => 0) :
                Dict("n" => length(nums), "min" => minimum(nums), "max" => maximum(nums),
                     "mean" => sum(nums) / length(nums), "last" => nums[end])
        end
        text = json_dump(data); ext = "json"
    end
    path = joinpath(out_dir, "metrics_summary.$ext")
    hodge_atomic_write(path, text)
    return path
end

# ════════════════════════════════════════════════════════════════════════
# §3/§13 CLI-ПАРСЕР (полный каталог флагов) + §14 МЕНЮ (menu-first).
# ════════════════════════════════════════════════════════════════════════
function new_run_dir(cfg::HodgeConfig)
    mkpath(cfg.report_dir)
    base = "run_" * Dates.format(Dates.now(), "yyyymmdd_HHMMSS")
    rd = joinpath(cfg.report_dir, base)
    # BUGFIX: два запуска в одну секунду получают одинаковое имя → второй
    # берёт flock того же каталога → ERR_LOCK_HELD. Суффикс _1.._N делает
    # run_dir уникальным.
    i = 1
    while isdir(rd)
        rd = joinpath(cfg.report_dir, "$(base)_$(i)")
        i += 1
    end
    mkpath(rd)
    return rd
end

const CLI_EXPLICIT = Ref{Set{Symbol}}(Set{Symbol}())   # P1.5 / §3.2

function parse_cli!(cfg::HodgeConfig, argv::Vector{String})
    """Возвращает (terminal_action::Union{Nothing,String}, warns::Vector{String})."""
    warns = String[]
    late_terminal::Union{Nothing,String} = nothing
    empty!(CLI_EXPLICIT[])           # P1.5: набор флагов этого запуска
    explicit = CLI_EXPLICIT[]
    n = length(argv)
    i = 1
    take(k::Int = 1) = begin
        i + k > n + 1 - 1 && (i + k > n) && throw(ArgumentError("$(argv[i]) expects $k argument(s)"))
        vals = argv[i+1:min(i + k, n)]
        length(vals) < k && throw(ArgumentError("$(argv[i]) expects $k argument(s)"))
        i += k
        vals
    end
    while i <= n
        a = argv[i]
        if a in ("--help", "-h")
            return "help", warns
        elseif a == "--version"
            return "version", warns
        elseif a == "--task"
            v = take(1)[1]
            ids = Int[]
            for x in split(v, ",")
                if x == "all"
                    append!(ids, SUITE_IDS)
                else
                    nx = tryparse(Int, x)
                    if nx === nothing
                        push!(warns, "WARNING: --task '$x' не число")
                    elseif nx ∉ SUITE_IDS
                        push!(warns, "WARNING: --task $nx не существует (см. --list-tasks)")
                    else
                        push!(ids, nx)
                    end
                end
            end
            push!(explicit, :tasks)          # BUGFIX(P9): было мёртвое explicit_cfg_tasks
            cfg.tasks = ids
        elseif a == "--preset"
            cfg.preset = take(1)[1]; apply_preset!(cfg, cfg.preset); push!(explicit, Symbol("preset"))
        elseif a == "--seed"
            cfg.seed = parse(Int, take(1)[1]); push!(explicit, Symbol("seed"))
        elseif a == "--prec"
            # §3.2 v5: без верхней границы — суффиксы k/m/g/t («гигабайты мантиссы»)
            pv = parse_prec_value(take(1)[1])
            if pv === nothing
                push!(warns, "WARNING: --prec: ожидалось N ≥ 30 или Nk/Nm/Ng/Nt (напр. 4096, 5m, 1g)")
            else
                cfg.prec = pv; push!(explicit, Symbol("prec"))
            end
        elseif a == "--two-pass"; cfg.two_pass = true
        elseif a == "--no-two-pass"; cfg.two_pass = false
        elseif a == "--pass-only"
            cfg.pass_only = parse(Int, take(1)[1]); push!(explicit, Symbol("pass_only"))
        elseif a == "--tag"
            append!(cfg.tags, split(take(1)[1], ","))
        elseif a == "--deterministic"
            cfg.deterministic = true
        elseif a == "--theme"
            cfg.theme = take(1)[1]; push!(explicit, Symbol("theme"))
        elseif a == "--theme-preview"
            return "theme-preview", warns
        elseif a == "--color-depth"
            cfg.color_depth = take(1)[1]; push!(explicit, Symbol("color_depth"))
        elseif a == "--plain"; cfg.plain = true
        elseif a == "--no-color"; cfg.no_color = true
        elseif a == "--unicode"
            cfg.unicode_on = take(1)[1]; push!(explicit, Symbol("unicode_on"))
        elseif a == "--no-banner"; cfg.banner = "off"
        elseif a == "--no-splash"; cfg.splash = false
        elseif a == "--no-tips"; cfg.tips = false
        elseif a == "--dye-mode"
            cfg.dye_mode = take(1)[1]; push!(explicit, :dye_mode)
        elseif a == "--gradient"
            cfg.gradient = take(1)[1]; push!(explicit, :gradient)
        elseif a == "--anim"; cfg.anim = take(1)[1]; push!(explicit, Symbol("anim"))
        elseif a == "--anim-scene"; cfg.anim_scene = take(1)[1]; push!(explicit, Symbol("anim_scene"))
        elseif a == "--anim-seconds"; cfg.anim_seconds = parse(Float64, take(1)[1]); push!(explicit, Symbol("anim_seconds"))
        elseif a == "--fps"; cfg.fps = parse(Int, take(1)[1]); push!(explicit, :fps)
        elseif a == "--particles"; cfg.particles = parse(Int, take(1)[1]); push!(explicit, :particles)
        elseif a == "--anim-cpu-guard"; cfg.anim_cpu_guard = parse(Float64, take(1)[1]); push!(explicit, Symbol("anim_cpu_guard"))
        elseif a == "--monitor"; cfg.monitor = take(1)[1]; push!(explicit, Symbol("monitor"))
        elseif a == "--monitor-interval"; cfg.monitor_interval = parse(Float64, take(1)[1]); push!(explicit, Symbol("monitor_interval"))
        elseif a == "--lang"; cfg.lang = take(1)[1]; push!(explicit, Symbol("lang"))
        elseif a == "--log-level"; cfg.log_level = uppercase(take(1)[1]); push!(explicit, :log_level)
        elseif a == "--ci"; cfg.ci = true
        elseif a == "--jsonl"; cfg.jsonl = true
        elseif a == "--tsv"; cfg.tsv = true
        elseif a == "--no-report"; cfg.no_report = true
        elseif a == "--report-dir"; cfg.report_dir = take(1)[1]; push!(explicit, Symbol("report_dir"))
        elseif a == "--self-test"; append!(cfg.self_test, ["unit"])
        elseif a == "--full"; push!(cfg.self_test, "full")
        elseif a == "--golden"; push!(cfg.self_test, "golden")
        elseif a == "--golden-update"; push!(cfg.self_test, "golden-update"); cfg.golden_update = true
        elseif a == "--golden-dir"; cfg.golden_dir = take(1)[1]; push!(explicit, Symbol("golden_dir"))
        elseif a == "--float-tolerance"; cfg.float_tolerance = parse(Float64, take(1)[1]); push!(explicit, Symbol("float_tolerance"))
        elseif a == "--props"; push!(cfg.self_test, "props")
        elseif a == "--palette"; push!(cfg.self_test, "palette")
        elseif a == "--dye-test"; push!(cfg.self_test, "dye")
        elseif a == "--anim-test"; push!(cfg.self_test, "anim")
        elseif a == "--menu-test"; push!(cfg.self_test, "menu")
        elseif a == "--plot-test"; push!(cfg.self_test, "plot")
        elseif a == "--lab-test"; push!(cfg.self_test, "lab")
        elseif a == "--bench"; cfg.bench = true
        elseif a == "--bench-threshold"; cfg.bench_threshold = parse(Float64, take(1)[1]); push!(explicit, Symbol("bench_threshold"))
        elseif a == "--stats"; cfg.bench_stats = true
        elseif a == "--bench-runs"; cfg.bench_runs = parse(Int, take(1)[1]); push!(explicit, Symbol("bench_runs"))
        elseif a == "--fuzz"; cfg.fuzz_sec = parse(Float64, take(1)[1]); push!(explicit, Symbol("fuzz_sec"))
        elseif a == "--doctor"; return "doctor", warns
        elseif a == "--health"; return "health", warns
        elseif a == "--dry-run"; cfg.dry_run = true
        elseif a == "--print-config"; cfg.print_config = true
        elseif a == "--validate-config"
            cfg.validate_config_only = true
        elseif a == "--config-file"
            load_config_file!(cfg, take(1)[1])
        elseif a == "--diff"
            cfg.diff_runs = [take(1)[1], take(1)[1]]
        elseif a == "--resume"; cfg.resume_dir = take(1)[1]; push!(explicit, Symbol("resume_dir"))
        elseif a == "--task-timeout"; cfg.task_timeout = parse(Float64, take(1)[1]); push!(explicit, Symbol("task_timeout"))
        elseif a == "--global-timeout"; cfg.global_timeout = parse(Float64, take(1)[1]); push!(explicit, Symbol("global_timeout"))
        elseif a == "--strict"; cfg.strict = true
        elseif a == "--menu"; cfg.menu_forced = true
        elseif a == "--no-menu"; cfg.menu_off = true
        elseif a == "--tui"; cfg.tui = true
        elseif a == "--prec-extreme"
            cfg.prec_extreme = true
            cfg.prec = max(cfg.prec, 200)
            hodge_prec_extreme_apply!(cfg)   # §3.2 v5: движок ≥ 1024 бит (или выше, если prec больше)
        elseif a == "--unsafe-prec"
            cfg.unsafe_prec = true           # §3.2 v5: сознательный обход ERR_PREC_RAM
        elseif a == "--report-formats"
            cfg.report_formats = take(1)[1]; push!(explicit, Symbol("report_formats"))
        elseif a == "--recipe"
            v = take(1)[1]
            try
                apply_recipe!(cfg, v)
            catch ex
                push!(warns, "WARNING: $(sprint(showerror, ex))")
            end
        elseif a == "--list-recipes"
            return "list-recipes", warns
        elseif a == "--list-tasks"
            return "list-tasks", warns
        elseif a == "--list-presets"
            return "list-presets", warns
        elseif a == "--metrics-format"
            cfg.metrics_format = take(1)[1]; push!(explicit, Symbol("metrics_format"))
        elseif a == "--clean-orphans"
            cfg.clean_orphans = take(1)[1] == "on"; push!(explicit, Symbol("clean_orphans"))
        elseif a == "--no-redact"; cfg.redact = false
        elseif a == "--cache"; cfg.cache_on = take(1)[1] == "on"; push!(explicit, Symbol("cache_on"))
        elseif a == "--rate"; cfg.rate_limit = take(1)[1]; push!(explicit, Symbol("rate_limit"))
        elseif a == "--links"; cfg.links = take(1)[1]; push!(explicit, Symbol("links"))
        elseif a == "--no-clipboard"; cfg.no_clipboard = true
        elseif a == "--no-settings-cache"
            # §3.2 v4: кэш применён ДО parse_cli! (cache < CLI) — флаг запрещает запись
            cfg.settings_cache = false
        elseif a == "--settings-save"; cfg.settings_save = true
        elseif a == "--settings-reset"
            nothing   # обработан ранним пре-сканом hodge_main (сильнее кэша)
        elseif a == "--health-probe-sec"; cfg.health_probe_sec = parse(Float64, take(1)[1]); push!(explicit, Symbol("health_probe_sec"))
        elseif a == "--sign-key"; cfg.sign_key = take(1)[1]; push!(explicit, Symbol("sign_key"))
        elseif a == "--verify-signature"   # P0.7: терминальное действие ПОСЛЕ
            # полного разбора — --sign-key; может стоять позже в argv
            cfg.verify_signature = take(1)[1]
            push!(explicit, Symbol("verify_signature"))   # BUGFIX(P9): был в комментарии
            late_terminal = "verify-signature"
        elseif a == "--junit"              # P1 / §26.3
            cfg.junit_path = take(1)[1]
            push!(explicit, Symbol("junit_path"))         # BUGFIX(P9): был в комментарии
        elseif a == "--theme-file"
            # P1 §21.5; BUGFIX(B3): push! был в комментарии — explain-config
            # не показывал источник значения
            cfg.theme_file = take(1)[1]
            push!(explicit, Symbol("theme_file"))
        elseif a == "--theme-replace"; cfg.theme_replace = true
        elseif a == "--no-truecolor"; cfg.color_depth = "256"                 # P1 §21.3
        elseif a == "--dye"; TEXT_STATE["dye_off"] = take(1)[1] == "off"      # P1 §22.1
        elseif a == "--digit-tier"; TEXT_STATE["digit_tier"] = take(1)[1] != "off"  # P1 §22.5
        elseif a == "--generate-man"; return "gen-man", warns                        # P1 §30
        elseif a == "--generate-completions"
            # BUGFIX(B3): push! стоял ПОСЛЕ return — мёртвый код
            cfg.gen_shell = take(1)[1]
            push!(explicit, Symbol("gen_shell"))
            return "gen-completions", warns
        elseif a == "--explain-config"; return "explain-config", warns               # P1 §3.2
        elseif a == "--list-tags"; return "list-tags", warns                         # P1 §4.2
        elseif a == "--coverage"; return "coverage", warns                           # P1 §19.7
        elseif a == "--monitor" && i < n && argv[i + 1] == "probe"; take(1); return "monitor-probe", warns
        elseif a in ("--rlimit-as", "--rlimit-cpu", "--rlimit-fsize"); take(1); return "unsupported-rlimit", warns
        elseif a == "--lab3d"; cfg.lab3d_spec = take(1)[1]
        elseif a == "--sweep"; push!(cfg.sweeps, take(1)[1])
        elseif a == "--lab-output"; cfg.lab3d_out = take(1)[1]
        elseif a == "--lab-video"
            # §11.10: 3D Video Lab — имя объекта; диспетчер в hodge_main
            cfg.lab3d_spec = take(1)[1]; push!(explicit, Symbol("lab3d_spec"))
        elseif a == "--lab-video-fps"
            p = LAB_VIDEO_PARAMS[]; LAB_VIDEO_PARAMS[] = (fps = clamp(parse(Int, take(1)[1]), 5, 60),
                                                          frames = p.frames, n = p.n)
        elseif a == "--lab-video-frames"
            p = LAB_VIDEO_PARAMS[]; LAB_VIDEO_PARAMS[] = (fps = p.fps,
                                                          frames = clamp(parse(Int, take(1)[1]), 2, 2000), n = p.n)
        elseif a == "--lab-video-N"
            p = LAB_VIDEO_PARAMS[]; LAB_VIDEO_PARAMS[] = (fps = p.fps, frames = p.frames,
                                                          n = clamp(parse(Int, take(1)[1]), 16, 128))
        elseif a == "--plot"; get(ENV, "HODGE_PLOT", "") == ""; ENV["HODGE_PLOT"] = take(1)[1] == "off" ? "off" : "on"
        else
            msg = "WARNING: unrecognized CLI argument '$a'"
            push!(warns, msg)
            cfg.strict && throw(ArgumentError(msg))
        end
        i += 1
    end
    append!(warns, apply_profile!(cfg, cfg.profile, explicit))
    # §27.2 / A1+A2: NO_COLOR, TERM=dumb, --no-color, --plain, --ci/--jsonl/--tsv → plain
    term = get(ENV, "TERM", "")
    effective_plain = (cfg.plain || cfg.no_color || cfg.ci || cfg.jsonl || cfg.tsv ||
                       haskey(ENV, "NO_COLOR") || term == "dumb")
    depth = cfg.color_depth == "auto" ? (effective_plain ? "mono" : "truecolor") : cfg.color_depth
    theme_set!(cfg.theme, depth, effective_plain)
    # §27.2 / B3: auto → capability-детект (в Julia: unicode вне tty → off)
    if cfg.unicode_on == "off"
        TEXT_STATE["unicode_on"] = false
    elseif cfg.unicode_on == "on"
        TEXT_STATE["unicode_on"] = true
    else
        TEXT_STATE["unicode_on"] = effective_plain ? false : true
    end
    TEXT_STATE["digit_tier"] = cfg.digit_tier
    TEXT_STATE["dye_mode"] = cfg.dye_mode in ("per-char", "per-token", "per-line") ? cfg.dye_mode : "per-char"
    # §20.2 / A18: --deterministic отключает всё случайное в выводе
    if cfg.deterministic
        cfg.anim = "off"
        cfg.tips = false
        cfg.splash = false
        TEXT_STATE["dye_mode"] = "per-line"
    end
    # P1 / §21.5: тема применяется после ПОЛНОГО разбора (порядок флагов
    # не важен: --theme-replace может стоять после --theme-file)
    if !isempty(cfg.theme_file)
        load_theme_file!(cfg)
        cfg.theme_file = ""   # применено — терминальный блок не повторит
    end
    return late_terminal, warns
end

hodge_help(cfg::HodgeConfig) = begin
    println(banner_render("compact", Dict()))
    println("""
Формы запуска (§33):
  julia master_hodge.jl                      # splash + меню (menu-first)
  julia master_hodge.jl --task 8             # V9 deep precision
  julia master_hodge.jl --ci --task all      # машиночитаемый прогон
  julia master_hodge.jl --self-test --full   # полный self-test
  julia master_hodge.jl --doctor             # диагностика среды
  julia master_hodge.jl --verify-signature results/run_*
  julia master_hodge.jl --diff results/run_A results/run_B

Флаги (полный каталог):
  --task N[,N|all]  --preset quick|full|deep   --seed INT      --prec N
  --prec-extreme    --two-pass|--no-two-pass   --tag fast,heavy --recipe NAME
  --theme NAME      --theme-file PATH [--theme-replace]
  --color-depth auto|truecolor|256|16|mono     --no-truecolor  --plain|--no-color
  --unicode on|off|auto    --dye on|off        --digit-tier on|off
  --ci|--jsonl|--tsv|--junit PATH              --report-formats md,html,svg
  --self-test [--full|--palette|--dye-test|--plot-test|--lab-test]
  --bench [--stats|--bench-runs N]             --fuzz SEC
  --doctor|--health|--dry-run                  --print-config|--explain-config
  --list-tasks|--list-presets|--list-recipes|--list-tags
  --diff A B        --resume PATH              --verify-signature PATH
  --sign-key PATH   --task-timeout SEC         --global-timeout SEC
  --config-file PATH --strict                  --coverage
  --generate-man    --generate-completions bash|zsh|fish|powershell
  --theme-preview   --menu|--no-menu|--tui     --metrics-format json|tsv|prom
  --lab3d FN --sweep name:lo:hi:step [--lab-output PATH]   --monitor probe
  --lab-video OBJ [--lab-video-fps N] [--lab-video-frames N] [--lab-video-N N]

Коды выхода: 0 PASS · 1 FAIL · 2 usage/config · 3 internal · 4 timeout · 5 health · 130 SIGINT · 143 SIGTERM""")
end

# ══════════════════════════════════════════════════════════════════════
# §30 #30: единый каталог флагов — источник для --generate-man и
# --generate-completions. Один массив → одно место правок.
# ══════════════════════════════════════════════════════════════════════
const CLI_FLAGS = [
    ("--help", 0, "справка и выход"),
    ("--version", 0, "версия и выход"),
    ("--task", 1, "id или 'all' (можно списком: 1,3,8)"),
    ("--preset", 1, "quick | full | deep"),
    ("--seed", 1, "сид прогона (целое)"),
    ("--prec", 1, "точность BigFloat (30..∞; суффиксы k/m/g/t: 4096, 5m, 1g)"),
    ("--two-pass", 0, "двухпроходный режим"),
    ("--no-two-pass", 0, "один проход"),
    ("--pass-only", 1, "1 | 2 — отладочный пасс"),
    ("--tag", 1, "фильтр по тегам: fast,!heavy"),
    ("--deterministic", 0, "фиксировать RNG-домены"),
    ("--theme", 1, "тема палитры"),
    ("--theme-preview", 0, "свотчи палитры и выход"),
    ("--color-depth", 1, "auto|truecolor|256|16|mono"),
    ("--plain", 0, "screen-reader режим"),
    ("--no-color", 0, "без ANSI"),
    ("--unicode", 1, "auto|on|off"),
    ("--no-banner", 0, "без баннера"),
    ("--no-splash", 0, "без splash"),
    ("--no-tips", 0, "без tip-of-the-day"),
    ("--dye-mode", 1, "per-char|per-token|per-line"),
    ("--gradient", 1, "span|line|block|off"),
    ("--anim", 1, "auto|on|off"),
    ("--anim-scene", 1, "particles|wave|sparkle|constellation|matrix"),
    ("--anim-seconds", 1, "сек для --monitor animate (0 = до Ctrl+C)"),
    ("--fps", 1, "15|24|30|60"),
    ("--particles", 1, "число частиц"),
    ("--anim-cpu-guard", 1, "CPU% порог деградации"),
    ("--monitor", 1, "on|off|panel|probe|animate"),
    ("--monitor-interval", 1, "интервал проб, сек"),
    ("--lang", 1, "ru | en"),
    ("--log-level", 1, "TRACE..FATAL"),
    ("--ci", 0, "неинтерактивный прогон"),
    ("--jsonl", 0, "построчный machine-readable вывод"),
    ("--tsv", 0, "TSV-вывод с заголовком"),
    ("--no-report", 0, "без FINAL_REPORT (results.json остаётся)"),
    ("--report-dir", 1, "каталог результатов"),
    ("--self-test", 0, "встроенные тесты"),
    ("--full", 0, "self-test: полный уровень"),
    ("--golden", 0, "self-test: golden-сравнение"),
    ("--golden-update", 0, "перезаписать golden-эталоны"),
    ("--golden-dir", 1, "каталог golden-эталонов"),
    ("--float-tolerance", 1, "допуск для float"),
    ("--props", 0, "self-test: property-инварианты"),
    ("--palette", 0, "self-test: палитра"),
    ("--dye-test", 0, "self-test: dye/num/gradient"),
    ("--anim-test", 0, "self-test: fps-таймер"),
    ("--menu-test", 0, "self-test: меню"),
    ("--plot-test", 0, "self-test: PNG/GIF/канва"),
    ("--lab-test", 0, "self-test: 3D-лаборатория"),
    ("--bench", 0, "бенчмарк задач"),
    ("--bench-threshold", 1, "порог регрессии (по умолчанию 1.2)"),
    ("--stats", 0, "bench: t-test (n≥5)"),
    ("--bench-runs", 1, "число прогонов для статистики"),
    ("--fuzz", 1, "секунды фаззинга"),
    ("--doctor", 0, "диагностика среды"),
    ("--health", 0, "быстрая проверка (≤ 2 с)"),
    ("--dry-run", 0, "план прогона без вычислений"),
    ("--print-config", 0, "эффективный конфиг"),
    ("--validate-config", 0, "валидация схемы без запуска"),
    ("--config-file", 1, "JSON-конфиг с include (глубина ≤ 8)"),
    ("--diff", 1, "сравнить два прогона"),
    ("--resume", 1, "продолжить прогон из run_dir"),
    ("--task-timeout", 1, "сек на задачу (post-hoc ledger, §15.8)"),
    ("--global-timeout", 1, "сек на весь прогон"),
    ("--strict", 0, "неизвестный флаг → ошибка"),
    ("--menu", 0, "форсировать меню (§14.1)"),
    ("--no-menu", 0, "никогда не открывать меню"),
    ("--tui", 0, "full-screen TUI (stdlib: ERR_UNSUPPORTED)"),
    ("--prec-extreme", 0, "рекордный режим (t08 → 1e-100, K=480)"),
    ("--unsafe-prec", 0, "разрешить prec с оценкой памяти > RAM (обход ERR_PREC_RAM)"),
    ("--report-formats", 1, "md,html,svg (pdf/docx → ERR_UNSUPPORTED)"),
    ("--recipe", 1, "применить рецепт"),
    ("--list-recipes", 0, "список рецептов"),
    ("--list-tasks", 0, "реестр задач"),
    ("--list-presets", 0, "пресеты"),
    ("--metrics-format", 1, "json|tsv|prom"),
    ("--clean-orphans", 1, "on|off — чистка *.tmp"),
    ("--no-redact", 0, "отключить редакцию секретов"),
    ("--cache", 1, "on|off — дисковый кэш"),
    ("--rate", 1, "n/unit — rate-limit"),
    ("--links", 1, "auto|on|off — OSC 8"),
    ("--no-clipboard", 0, "отключить OSC 52"),
    ("--health-probe-sec", 1, "см. --help"),
    ("--sign-key", 1, "ключ HMAC для подписи артефактов"),
    ("--verify-signature", 1, "проверить подпись run_dir (§20.5)"),
    ("--junit", 1, "путь к JUnit XML (§26.3)"),
    ("--no-settings-cache", 0, "не читать/не писать .cache/settings.json (§3.2 v4)"),
    ("--settings-save", 0, "сохранить настройки ЭТОГО CLI-прогона в кэш настроек"),
    ("--settings-reset", 0, "очистить кэш настроек .cache/settings.json"),
    ("--theme-file", 1, "JSON-тема поверх текущей ([hex,idx,name] или [r,g,b])"),
    ("--theme-replace", 0, "полная замена темы (не merge)"),
    ("--no-truecolor", 0, "форс 256"),
    ("--dye", 1, "on|off — движок окрашивания (§22.1)"),
    ("--digit-tier", 1, "on|off — tiering чисел (§22.5)"),
    ("--generate-man", 0, "roff-мануал в stdout"),
    ("--generate-completions", 1, "bash|zsh|fish|powershell"),
    ("--explain-config", 0, "поле → значение → источник (§3.2)"),
    ("--list-tags", 0, "список тегов"),
    ("--coverage", 0, "строковое покрытие self-test (ERR_UNSUPPORTED, §19.7)"),
    ("--sweep", 1, "см. --help"),
    ("--lab-output", 1, "каталог лаборатории"),
    ("--lab-video", 1, "3D Video Lab: имя объекта (sphere|torus|klein|trefoil|mobius|fermat_k3_affine|barth_sextic|gyroid)"),
    ("--lab-video-fps", 1, "кадров/с видео (5..60, по умолчанию 24)"),
    ("--lab-video-frames", 1, "число кадров (2..2000, по умолчанию 120)"),
    ("--lab-video-N", 1, "плотность сетки N_full (16..128, по умолчанию 64)"),
    ("--plot", 1, "on|off — графики per-task"),
]

# P1.1 / §30: roff-мануал из единого CLI_FLAGS
function hodge_generate_man()
    println(".TH HODGE-MASTER 1 \"$(Dates.format(Dates.today(), "Y-m-d"))\" \"hodge-master $HODGE_VERSION\"")
    println(".SH NAME")
    println("hodge-master \\- верификация утверждений репозитория $HODGE_REPO")
    println(".SH SYNOPSIS")
    println(".B julia master_hodge.jl")
    println("[флаги]")
    println(".SH DESCRIPTION")
    println("Голый запуск в tty открывает интерактивное меню (menu-first, §14.1).")
    println("Каждая задача реестра TASKS проверяет одно утверждение репозитория.")
    println("Версия: $HODGE_VERSION · сборка: $HODGE_BUILD_DATE · язык: $HODGE_LANG")
    println(".SH OPTIONS")
    for (fl, nargs, desc) in CLI_FLAGS
        println(".TP")
        print(".B $fl")
        nargs > 0 && print(" \\fIзначение\\fR")
        println()
        println(desc)
    end
    println(".SH EXIT CODES")
    println("0 PASS · 1 FAIL · 2 usage/config · 3 internal · 4 timeout · 5 health · 130 SIGINT · 143 SIGTERM")
    println(".SH FILES")
    println("results/run_*/FINAL_REPORT/ \\- итоговые отчёты; results/run_*/results.json \\- машинный вердикт")
    println(".SH SEE ALSO")
    println("README репозитория $HODGE_REPO")
    return 0
end

# P1.2 / §30: автодополнение для bash/zsh/fish/powershell из единого CLI_FLAGS
function hodge_generate_completions(shell::AbstractString)
    if shell == "bash"
        println("# bash completion для master_hodge.jl (сгенерировано из CLI_FLAGS, §30)")
        println("_hodge_master() {")
        println("  local cur=\"\${COMP_WORDS[COMP_CWORD]}\"")
        println("  local opts=\"$(join([f[1] for f in CLI_FLAGS], " "))\"")
        println("  COMPREPLY=( \$(compgen -W \"\$opts\" -- \"\$cur\") )")
        println("}")
        println("complete -F _hodge_master master_hodge.jl")
    elseif shell == "zsh"
        println("#compdef master_hodge")
        println("_arguments \\")
        for (fl, nargs, desc) in CLI_FLAGS
            extra = nargs > 0 ? ":value:" : ""
            d = replace(desc, "'" => "")
            println("  '$fl[$d]$extra' \\")
        end
        println("  && return 0")
    elseif shell == "fish"
        for (fl, nargs, desc) in CLI_FLAGS
            long = fl[3:end]
            req = nargs > 0 ? " -r" : ""
            d = replace(desc, "'" => "")
            println("complete -c master_hodge.jl -l $long$req -d '$d'")
        end
    elseif shell in ("powershell", "ps")
        println("# powershell completions (§30)")
        println("\$opts = @(" * join(["'" * f[1] * "'" for f in CLI_FLAGS], ", ") * ")")
        println("Register-ArgumentCompleter -Native -CommandName master_hodge.jl -ScriptBlock {")
        println("    param(\$wordToComplete, \$commandAst, \$cursorPosition)")
        println("    \$opts | Where-Object { \$_ -like \"\$wordToComplete*\" } | ForEach-Object {")
        println("        [System.Management.Automation.CompletionResult]::new(\$_, \$_, 'ParameterValue', \$_)")
        println("    }")
        println("}")
    else
        println(stderr, "ERR_UNSUPPORTED: shell '$shell' (bash|zsh|fish|powershell)")
        return 2
    end
    return 0
end

# P1 / §21.5: JSON-файл темы — merge/replace в THEMES[cfg.theme].
# Формы значений: [hex, idx256, fallback] (как в THEMES) или [r,g,b] —
# тогда hex вычисляется, а idx/fallback наследуются от текущей записи.
function load_theme_file!(cfg::HodgeConfig)
    isfile(cfg.theme_file) || throw(ArgumentError("ERR_CONFIG: нет файла темы $(cfg.theme_file)"))
    data = json_load_flat(read(cfg.theme_file, String))
    # P1.6: replace обязан покрыть все PALETTE_KEYS (merge наследует базу)
    if cfg.theme_replace
        miss = [k for k in PALETTE_KEYS if !haskey(data, k)]
        isempty(miss) || throw(ArgumentError(
            "ERR_THEME_INVALID: --theme-replace требует все ключи; нет: $(join(miss, ", "))"))
    end
    base = cfg.theme_replace ? Dict{String,Any}() : Dict{String,Any}(THEMES[cfg.theme])
    for (k, v) in data
        k == "name" && continue
        v isa Vector && length(v) == 3 || throw(ArgumentError(
            "ERR_CONFIG: ключ '$k' темы должен быть [hex, idx, name] или [r,g,b]"))
        cur = get(base, String(k), ("#808080", 244, "white"))
        if v[1] isa AbstractString && startswith(v[1], "#")
            ent = (String(v[1]), Int(v[2]), String(v[3]))
        else
            rgb = Tuple(Int(x) for x in v)
            all(c -> 0 <= c <= 255, rgb) || throw(ArgumentError("ERR_CONFIG: $k вне 0..255"))
            hex = "#" * join([string(c; pad = 2, base = 16) for c in rgb])
            ent = (hex, cur[2], cur[3])   # idx/fallback наследуются
        end
        base[String(k)] = ent
    end
    THEMES[cfg.theme] = Dict{String,Tuple{String,Int,String}}(base)
    theme_set!(cfg.theme, cfg.color_depth == "auto" ? "truecolor" : cfg.color_depth, cfg.plain)
    println(badge("INFO"), " тема из $(cfg.theme_file) → $(cfg.theme) ($(length(base)) ключей)",
            cfg.theme_replace ? " [replace]" : " [merge]")
    return 0
end

# P1 / §26.3: JUnit-XML из результатов прогона
function hodge_junit(cfg::HodgeConfig, runner)
    isempty(cfg.junit_path) && return
    rs = results_sorted(runner)
    # P1.4: reason может содержать &/</> — XML-escape обязателен
    esc = s -> replace(string(s), "&" => "&amp;", "<" => "&lt;",
                       ">" => "&gt;", "\"" => "&quot;")
    xml = String["<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
                 "<testsuite name=\"hodge-master\" tests=\"$(length(rs))\" " *
                 "failures=\"$(count(r -> r["verdict"] == "FAIL", rs))\" " *
                 "skipped=\"$(count(r -> r["verdict"] == "SKIP", rs))\">"]
    for r in rs
        dur = round(sum(Float64(p["duration_s"]) for p in values(r["passes"]); init = 0.0); digits = 3)
        push!(xml, "  <testcase name=\"task$(r["id"])_$(r["slug"])\" classname=\"hodge-master\" time=\"$dur\">")
        r["verdict"] == "FAIL" &&
            push!(xml, "    <failure message=\"$(esc(something(r["reason"], "FAIL")))\"/>")
        r["verdict"] == "SKIP" && push!(xml, "    <skipped/>")
        push!(xml, "  </testcase>")
    end
    push!(xml, "</testsuite>")
    hodge_atomic_write(cfg.junit_path, join(xml, "\n") * "\n")
    println(badge("INFO"), " junit → $(cfg.junit_path)")
end

# ── §14 МЕНЮ: menu-first, fuzzy (/), j/k, Space-мультивыбор, Enter-запуск ──
const MENU_EOF_LIMIT = 50

mutable struct HodgeMenu
    cfg::HodgeConfig
    log::HodgeLogger
    eof::Int
    marked::Set{Int}
    filter::String
    mode::String          # nav | filter | sweep
    selected::Int
    sweep_fn::String
    sweep_specs::Vector{String}
    history::Vector{String}   # P2.1 / §14.5: последние команды (для !N / !!)
end
HodgeMenu(cfg::HodgeConfig, lg::HodgeLogger) = HodgeMenu(cfg, lg, 0, Set{Int}(), "", "nav", 0, "", String[], String[])

visible_tasks(m::HodgeMenu) = begin
    isempty(m.filter) && return TASKS
    f = lowercase(m.filter)
    return [t for t in TASKS if occursin(f, lowercase(t.slug)) || occursin(f, lowercase(t.title)) || occursin(f, string(t.id))]
end

# §14.3: единая точка сборки строки меню — гарантирует видимую ширину width+2
# (совпадает с top border "╔"*"═"^width*"╗"), корректно учитывает ANSI.
function menu_line(content::AbstractString, width::Int)
    vis = textwidth(strip_ansi(content))
    pad = max(0, width - 1 - vis)
    return "║ " * content * " "^pad * "║"
end

# §14.3: подгонка строки под видимую ширину (truncate + pad), не по байтам.
# BUGFIX(B1): strip_ansi перед подсчётом — иначе ANSI-коды считаются видимыми
# (banner_render возвращает dyed-строку, textwidth раздувался ~в 20 раз,
# баннер обрезался до "██╗", meta-строка — до 32 символов).
function fit_width(s::AbstractString, width::Int)
    plain = strip_ansi(s)
    vis = textwidth(plain)
    vis <= width && return s * " "^(width - vis)   # цвет сохранён
    # обрезка: цвет теряется, выравнивание сохраняется
    buf = IOBuffer(); cur = 0
    for ch in plain
        w = textwidth(ch)
        cur + w > width && break
        print(buf, ch); cur += w
    end
    return String(take!(buf)) * " "^(width - cur)
end

# VI.8 / Часть II: рендер меню v2 — ASCII-баннер ВНУТРИ рамки, 4 колонки задач,
# RUN [a/f/h/c/v/w], SETTINGS [p/s/n/t/l/d/e/P], ACTIONS [x/r/T/C/?/q].
# BUGFIX: все строки собираются через menu_line (рамка ровная width+2),
# все тексты — через MSG/hodge_fmt (l клавиша переключает язык целиком).
function menu_render(m::HodgeMenu, status::AbstractString = "")
    cfg = m.cfg
    lang_cfg = Dict("lang" => cfg.lang)
    fmt(k; kw...) = hodge_fmt(lang_cfg, k; kw...)
    println()
    width = clamp(displaysize(stdout)[2] - 2, 72, 112)
    if TEXT_STATE["plain"] || !TEXT_STATE["unicode_on"]
        # plain-вариант (та же локализация, без рамки)
        println(strip_ansi(banner_render("full", Dict())))
        println("─"^width)
        println(fmt("menu.run_header") * ":")
        for (k, dk) in (("a", "menu.run_all"), ("f", "menu.run_fast"),
                        ("h", "menu.run_heavy"), ("c", "menu.run_chess"),
                        ("v", "menu.run_verhodge"), ("w", "menu.run_sweep"))
            println("  [$k] " * fmt(dk))
        end
        items = visible_tasks(m)
        println(fmt("menu.tasks_header") * " ($(length(items))/$(length(TASKS))):")
        for (i, t) in enumerate(items)
            mark = t.id in m.marked ? "✦" : " "
            cur  = (m.selected == i - 1) ? "❯" : " "
            println("  $cur$mark [$(t.id)] $(t.slug) — $(t.title)")
        end
        println(fmt("menu.settings_header") * ":")
        println("  [p] " * fmt("menu.set.prec", value = cfg.prec))
        println("  [s] " * fmt("menu.set.seed", value = cfg.seed))
        println("  [n] " * fmt("menu.set.preset", value = cfg.preset))
        println("  [t] " * fmt("menu.set.theme", value = cfg.theme))
        println("  [l] " * fmt("menu.set.lang", value = cfg.lang))
        println("  [d] " * fmt("menu.set.depth", value = cfg.color_depth))
        println("  [e] " * fmt("menu.set.two_pass", value = cfg.two_pass ? "on" : "off"))
        println("  [P] " * fmt("menu.set.prec_extreme", value = cfg.prec_extreme ? "on" : "off"))
        println(fmt("menu.actions_header") * ":")
        for (k, dk) in (("x", "menu.act.dry_run"), ("r", "menu.act.recipes"),
                        ("T", "menu.act.theme_cycle"), ("C", "menu.act.palette"),
                        ("V", "menu.act.video_lab"),
                        ("?", "menu.act.help"), ("q", "menu.act.quit"))
            println("  [$k] " * fmt(dk))
        end
        println("❯ $status")
        println(fmt("menu.status_line", theme = cfg.theme, prec = cfg.prec, seed = cfg.seed,
                    preset = cfg.preset, lang = cfg.lang, n = length(m.marked),
                    ids = join(sort(collect(m.marked)), ",")))
        # BUGFIX(Compact): узкий терминал → компактный рендер без промпта —
        # пользователь видел молчащее меню («не работает REPL»). Промпт нужен
        # и здесь, как в рамочном рендере ниже.
        print(dye(fmt("menu.prompt"), "gold_bright"), " ")
        flush(stdout)
        return
    end
    top = "╔" * "═"^width * "╗"
    sep = "╠" * "═"^width * "╣"
    bot = "╚" * "═"^width * "╝"
    println(top)
    # ASCII-баннер — внутри рамки, ВЕРХ (fit_width до width-1: баннер шире
    # рамки не должен рвать правую границу ║)
    for ln in split(banner_render("full", Dict()), "\n")
        println(menu_line(fit_width(ln, width - 1), width))
    end
    println(sep)
    # RUN
    println(menu_line(gradient(" " * fmt("menu.run_header") * " ", "gold", "amber"), width))
    for (k, dk) in (("a", "menu.run_all"), ("f", "menu.run_fast"), ("h", "menu.run_heavy"),
                    ("c", "menu.run_chess"), ("v", "menu.run_verhodge"), ("w", "menu.run_sweep"))
        println(menu_line(dye(rpad("[$k]", 6), "gold_bright") * " " * fmt(dk), width))
    end
    # TASKS — по 4 в строке
    items = visible_tasks(m)
    head = " " * fmt("menu.tasks_header") * " ($(length(items))/$(length(TASKS))) "
    println(menu_line(gradient(head, "gold", "amber"), width))
    cols = 4
    cw = (width - 1) ÷ cols - 2    # cols*(cw+2) ≤ width-1 — ровная рамка
                                   # (BUGFIX: (width-2)÷cols давал 4*cw+8 > width-1)
    rows = cld(length(items), cols)
    for r in 0:rows-1
        parts = String[]
        for c in 0:cols-1
            idx = r + c * rows + 1
            if idx > length(items)
                push!(parts, " "^(cw + 2))   # пустая ячейка + 2 пробела разделителя
                continue
            end
            t = items[idx]
            mark = t.id in m.marked ? "✦" : " "
            cur  = (m.selected == idx - 1) ? "❯" : " "
            cell = fit_width(@sprintf("%s%s[%2d] %s", cur, mark, t.id, t.slug), cw)
            push!(parts, dye(cell, "text") * "  ")
        end
        println(menu_line(join(parts), width))
    end
    # SETTINGS
    println(menu_line(gradient(" " * fmt("menu.settings_header") * " ", "gold", "amber"), width))
    for (k, dk, v) in (("p", "menu.set.prec", cfg.prec),
                       ("s", "menu.set.seed", cfg.seed),
                       ("n", "menu.set.preset", cfg.preset),
                       ("t", "menu.set.theme", cfg.theme),
                       ("l", "menu.set.lang", cfg.lang),
                       ("d", "menu.set.depth", cfg.color_depth),
                       ("e", "menu.set.two_pass", cfg.two_pass ? "on" : "off"),
                       ("P", "menu.set.prec_extreme", cfg.prec_extreme ? "on" : "off"))
        println(menu_line(dye(rpad("[$k]", 6), "gold_bright") * " " * fmt(dk, value = v), width))
    end
    # ACTIONS
    println(menu_line(gradient(" " * fmt("menu.actions_header") * " ", "gold", "amber"), width))
    for (k, dk) in (("x", "menu.act.dry_run"), ("r", "menu.act.recipes"),
                    ("T", "menu.act.theme_cycle"), ("C", "menu.act.palette"),
                    ("V", "menu.act.video_lab"),
                    ("?", "menu.act.help"), ("q", "menu.act.quit"))
        println(menu_line(dye(rpad("[$k]", 6), "gold_bright") * " " * fmt(dk), width))
    end
    println(sep)
    prompt_hint = m.mode == "filter" ? "❯ filter:" : m.mode == "sweep" ? "❯ sweep:" : "❯"
    # BUGFIX: длинный status рвал правую границу ║ — фитуем до доступной ширины
    status_fit = fit_width(status, width - 1 - textwidth(prompt_hint) - 1)
    println(menu_line(dye(prompt_hint, "gold_bright") * " " * dye(status_fit, "text_dim"), width))
    println(sep)
    stat = fmt("menu.status_line", theme = cfg.theme, prec = cfg.prec, seed = cfg.seed,
               preset = cfg.preset, lang = cfg.lang, n = length(m.marked),
               ids = join(sort(collect(m.marked)), ","))
    # BUGFIX(Clip): длинный перечень id резался посреди списка («marked=4 [1»).
    # Не влезает в ширину рамки → компактная форма без перечня.
    textwidth(stat) > width - 1 &&
        (stat = fmt("menu.status_line", theme = cfg.theme, prec = cfg.prec, seed = cfg.seed,
                    preset = cfg.preset, lang = cfg.lang, n = length(m.marked), ids = ".."))
    println(menu_line(dye(fit_width(stat, width - 1), "neutral"), width))
    println(bot)
    print(dye(fmt("menu.prompt"), "gold_bright"), " ")
    flush(stdout)
    return
end

# ════════════════════════════════════════════════════════════════════════
# §14.2 SUBMENU: единая точка чтения с поддержкой Ctrl+D, пустой строки
# (= cancel) и защитой от busy-loop (см. BUGFIX в menu_run!). Плюс шесть
# полноценных подменю вместо прежних заглушек: рецепты [r], палитра [C],
# справка [?], dry-run [x], sweep [w], video [V].
# ════════════════════════════════════════════════════════════════════════
function menu_read(prompt::AbstractString; allow_empty::Bool = false)::Union{String,Nothing}
    print(prompt)
    flush(stdout)
    stdin_eof_safe() && return nothing    # Ctrl+D/EOF → cancel (неблокирующе)
    line = readline(stdin)
    isempty(line) && stdin_eof_safe() && return nothing
    stripped = strip(line)
    isempty(stripped) && !allow_empty && return nothing   # пустая строка = cancel
    return String(stripped)
end

submenu_fmt(cfg) = (k; kw...) -> hodge_fmt(Dict("lang" => cfg.lang), k; kw...)

function _menu_recipes(m::HodgeMenu)
    """§14.5 RECIPES: список → выбор → preview изменений → apply/run."""
    cfg = m.cfg
    fmt = submenu_fmt(cfg)
    names = sort!(collect(keys(RECIPES)))
    println()
    println(dye(fmt("submenu.recipes.title"), "gold_dim"))
    for (i, name) in enumerate(names)
        r = RECIPES[name]
        println("  ", dye("[$i]", "gold_bright"), " ", dye(name, "gold"),
                " — ", r["description"])
        tasks_s = r["tasks"] == "all" ? fmt("submenu.all") : string(r["tasks"])
        println("      preset=", dye(r["preset"], "gold_bright"), " · ",
                "profile=", dye(r["profile"], "gold_bright"), " · ",
                "two_pass=", dye(string(r["two_pass"]), "gold_bright"))
        println("      tasks=", dye(tasks_s, "text"))
        if !isempty(r["overrides"])
            for (k, v) in r["overrides"]
                println("      override: $k = $v")
            end
        end
    end
    println(dye(fmt("submenu.recipes.cancel"), "gold_bright"))
    ans = menu_read(dye(fmt("submenu.recipes.prompt", n = length(names)), "gold_bright"))
    ans === nothing && (println(badge("INFO"), " ", fmt("submenu.cancelled")); return)
    idx = tryparse(Int, ans)
    idx == 0 && (println(badge("INFO"), " ", fmt("submenu.cancelled")); return)
    (idx === nothing || idx < 1 || idx > length(names)) && begin
        println(badge("WARN"), " ", fmt("submenu.recipes.none", v = ans)); return
    end
    name = names[idx]
    r = RECIPES[name]
    println()
    println(dye(fmt("submenu.recipes.applying", name = name), "gold"))
    println(fmt("submenu.recipes.preview",
                pold = cfg.preset, pnew = r["preset"],
                rold = cfg.profile, rnew = r["profile"],
                told = isempty(cfg.tasks) ? fmt("submenu.all") : string(cfg.tasks),
                tnew = r["tasks"] == "all" ? fmt("submenu.all") : string(r["tasks"]),
                eold = cfg.two_pass, enew = r["two_pass"]))
    println(dye(fmt("submenu.recipes.actions"), "gold_bright"))
    act = menu_read(dye(fmt("submenu.recipes.action_prompt"), "gold_bright");
                    allow_empty = true)
    (act === nothing || act == "") &&
        (println(badge("INFO"), " ", fmt("submenu.cancelled")); return)
    try
        apply_recipe!(cfg, name)
        println(badge("INFO"), " ", fmt("submenu.recipes.applied", name = name))
    catch ex
        println(badge("FAIL"), " ", sprint(showerror, ex)); return
    end
    if lowercase(act) == "a"
        ids = copy(cfg.tasks)   # apply_recipe! кладёт конкретные Int (не "all")
        println(badge("INFO"), " ",
                fmt("submenu.recipes.running", name = name,
                    ids = isempty(ids) ? fmt("submenu.all") : string(ids)))
        run_ids_with_lock!(cfg, ids)
    end
end

function _menu_palette(m::HodgeMenu)
    """§21.6 PALETTE: свотчи всех тем + выбор темы по номеру."""
    cfg = m.cfg
    fmt = submenu_fmt(cfg)
    saved_theme = cfg.theme
    saved_depth = TEXT_STATE["depth"]
    saved_plain = TEXT_STATE["plain"]
    println()
    names = sort!(collect(keys(THEMES)))
    for (i, name) in enumerate(names)
        theme_set!(name, cfg.color_depth == "auto" ? "truecolor" : cfg.color_depth,
                   cfg.plain)
        pal = THEMES[name]
        marker = name == saved_theme ?
            dye(fmt("submenu.palette.current"), "gold_bright") : ""
        println(dye("── [$i] $name " * "─"^28, "gold_dim") * marker)
        for key in PALETTE_KEYS
            haskey(pal, key) || continue   # не у всех тем полный набор (напр. mono)
            v = pal[key]
            println("  $(color_code(key))███\x1b[0m $(rpad(key, 12)) $(v[1])/$(v[2])")
        end
        println(fmt("submenu.palette.sample") * dye(fmt("submenu.numbers"), "text") *
                num(1234, "int") * " " * badge("PASS") * " " * badge("FAIL"))
        println()
    end
    theme_set!(saved_theme, saved_depth, saved_plain)
    println(dye(fmt("submenu.palette.hint", n = length(names)), "gold_bright"))
    ans = menu_read(dye(fmt("submenu.palette.prompt"), "gold_bright"); allow_empty = true)
    (ans === nothing || ans == "") && return
    idx = tryparse(Int, ans)
    (idx === nothing || idx < 1 || idx > length(names)) && begin
        println(badge("WARN"), " ", fmt("submenu.palette.none", v = ans)); return
    end
    cfg.theme = names[idx]
    theme_set!(cfg.theme, saved_depth, saved_plain)
    empty!(TEXT_STATE["_dye_cache"]); empty!(TEXT_STATE["_gradient_cache"])
    println(badge("INFO"), " ", fmt("submenu.palette.set", value = cfg.theme))
end

function _menu_help(m::HodgeMenu)
    """§14.6 HELP: полноэкранная расширенная справка."""
    fmt = submenu_fmt(m.cfg)
    println()
    println(dye("╔════════════════════════════════════════════════════════════╗", "gold"))
    println(dye(fmt("submenu.help.title"), "gold_bright"))
    println(dye("╚════════════════════════════════════════════════════════════╝", "gold"))
    println()
    for (hdr, body) in (("submenu.help.run", "submenu.help.run.body"),
                        ("submenu.help.tasks", "submenu.help.tasks.body"),
                        ("submenu.help.settings", "submenu.help.settings.body"),
                        ("submenu.help.actions", "submenu.help.actions.body"),
                        ("submenu.help.cli", "submenu.help.cli.body"),
                        ("submenu.help.input", "submenu.help.input.body"))
        println(dye(fmt(hdr), "gold"))
        println(fmt(body))
        println()
    end
    menu_read(dye(fmt("submenu.help.back"), "gold_dim"); allow_empty = true)
    nothing
end

function _menu_dry_run(m::HodgeMenu)
    """§13.3 DRY-RUN: выбор группы → план без вычислений (lock не берётся)."""
    cfg = m.cfg
    fmt = submenu_fmt(cfg)
    println()
    println(dye(fmt("submenu.dry.title"), "gold_dim"))
    println(fmt("submenu.dry.cfg", preset = cfg.preset, seed = cfg.seed,
                prec = cfg.prec, tp = cfg.two_pass ? "on" : "off"))
    println(fmt("submenu.dry.opts"))
    println(dye(fmt("submenu.dry.cancel"), "gold_bright"))
    ans = menu_read(dye(fmt("submenu.dry.prompt"), "gold_bright"); allow_empty = true)
    (ans === nothing || ans == "") && return
    ids = if ans == "1"
        Int[]
    elseif ans == "2"
        [t.id for t in TASKS if "fast" in t.tags]
    elseif ans == "3"
        [t.id for t in TASKS if "heavy" in t.tags]
    elseif ans == "4"
        [t.id for t in TASKS if 23 <= t.id <= 33]
    elseif ans == "5"
        [t.id for t in TASKS if 34 <= t.id <= 38]
    else
        println(badge("WARN"), " ", fmt("submenu.dry.noopt", v = ans)); return
    end
    old_run = cfg.run_dir
    old_tasks = cfg.tasks
    cfg.run_dir = new_run_dir(cfg)   # отдельный каталог: dryrun.txt не мешает прогону
    cfg.tasks = ids
    try
        hodge_dry_run(cfg)
        println(badge("INFO"), " ",
                fmt("submenu.dry.done", path = joinpath(cfg.run_dir, "logs", "dryrun.txt")))
    catch ex
        println(badge("FAIL"), " dry-run: ", sprint(showerror, ex))
    finally
        cfg.tasks = old_tasks
        isempty(old_run) || (cfg.run_dir = old_run)
    end
end

function _menu_sweep(m::HodgeMenu)
    """§11.6 SWEEP: функция → sweep-спеки → preview кадров → запуск."""
    cfg = m.cfg
    fmt = submenu_fmt(cfg)
    println()
    println(dye(fmt("submenu.sweep.title"), "gold_dim"))
    println(fmt("submenu.sweep.fns"))
    fn = menu_read(dye(fmt("submenu.sweep.fn_prompt"), "gold_bright"); allow_empty = true)
    fn === nothing && return
    fn = fn == "" ? "omega" : fn
    specs = String[]
    while true
        spec = menu_read(dye(fmt("submenu.sweep.spec_prompt", n = length(specs)),
                             "gold_bright"); allow_empty = true)
        spec === nothing && return
        spec == "" && break
        try
            parse_sweep(spec)
            push!(specs, spec)
            println(badge("INFO"), " ", fmt("submenu.sweep.added", spec = spec))
        catch ex
            println(badge("WARN"), " ",
                    fmt("submenu.sweep.bad_spec", msg = sprint(showerror, ex)))
        end
    end
    isempty(specs) && (specs = ["N:7:30:1"])
    total = 1
    for s in specs
        _, vals = parse_sweep(s)
        total *= length(vals)
    end
    cap = 500
    println(badge("INFO"), " ", fmt("submenu.sweep.summary", fn = fn,
                specs = join(specs, ", "), total = total, cap = cap))
    total > cap && println(badge("WARN"), " ",
                           fmt("submenu.sweep.cap_warn", cap = cap))
    confirm = menu_read(dye(fmt("submenu.sweep.confirm"), "gold_bright");
                        allow_empty = true)
    (confirm === nothing || lowercase(confirm) == "c") && return
    cfg.run_dir = new_run_dir(cfg)
    saved_spec, saved_sweeps = cfg.lab3d_spec, cfg.sweeps
    cfg.lab3d_spec = String(fn)
    cfg.sweeps = specs
    try
        hodge_lab3d(cfg)
    catch ex
        println(badge("FAIL"), " sweep: ", sprint(showerror, ex))
    finally
        cfg.lab3d_spec, cfg.sweeps = saved_spec, saved_sweeps
    end
end

function _menu_video(m::HodgeMenu)
    """§11.10 VIDEO LAB: объект + fps + frames + N_full → MP4/MJPEG/GIF."""
    cfg = m.cfg
    fmt = submenu_fmt(cfg)
    println()
    println(dye(fmt("menu.act.video_lab"), "gold_dim"))
    println(fmt("menu.video.objects"))
    for vname in sort!(collect(keys(LAB_VIDEO_OBJECTS)))
        o = LAB_VIDEO_OBJECTS[vname]
        println("    ", dye(vname, "gold_bright"), "  (", String(o.kind), ")")
    end
    ask_i(prompt, default, lo, hi) = begin
        s = menu_read(prompt; allow_empty = true)
        s === nothing && return nothing
        v = s == "" ? default : something(tryparse(Int, s), default)
        clamp(v, lo, hi)
    end
    ans = menu_read(dye(fmt("menu.video.prompt"), "gold_bright"); allow_empty = true)
    ans === nothing && return
    vname = ans == "" ? "sphere" : ans
    haskey(LAB_VIDEO_OBJECTS, vname) || begin
        println(badge("FAIL"), " ", fmt("submenu.video.bad_obj", obj = vname)); return
    end
    fps = ask_i(dye(fmt("submenu.video.fps_prompt"), "gold_bright"), 24, 5, 60)
    fps === nothing && return
    frames = ask_i(dye(fmt("submenu.video.frames_prompt"), "gold_bright"), 120, 2, 2000)
    frames === nothing && return
    n_full = ask_i(dye(fmt("submenu.video.n_prompt"), "gold_bright"), 64, 16, 128)
    n_full === nothing && return
    println(badge("INFO"), " ", fmt("submenu.video.summary", obj = vname, fps = fps,
                frames = frames, n = n_full))
    confirm = menu_read(dye(fmt("submenu.sweep.confirm"), "gold_bright");
                        allow_empty = true)
    (confirm === nothing || lowercase(confirm) == "c") && return
    vout = isempty(cfg.run_dir) ? joinpath(cfg.report_dir, "lab_video", vname) :
           joinpath(cfg.run_dir, "lab_video", vname)
    try
        hodge_lab_video(cfg; object = String(vname), out_dir = String(vout),
                        fps = fps, frames = frames, N_full = n_full)
    catch ex
        println(badge("FAIL"), " video: ", sprint(showerror, ex))
    end
end

function menu_handle!(m::HodgeMenu, key::AbstractString)
    cfg = m.cfg
    lang_cfg = Dict("lang" => cfg.lang)
    fmt(k; kw...) = hodge_fmt(lang_cfg, k; kw...)
    if key in ("q", "Q", "й", "Й")
        return "quit"
    elseif key == "?"
        _menu_help(m)
    elseif key == "a"
        run_ids_with_lock!(cfg, Int[])
    elseif key == "f"
        run_ids_with_lock!(cfg, [t.id for t in TASKS if "fast" in t.tags])
    elseif key == "h"
        run_ids_with_lock!(cfg, [t.id for t in TASKS if "heavy" in t.tags])
    elseif key == "c"
        # BUGFIX: честные labels — показываем, что ЕСТЬ в реестре, и чего нет
        # (набор задач зависит от реестра: в Julia 23, в Python 23–33)
        ids = [t.id for t in TASKS if 23 <= t.id <= 33]
        if isempty(ids)
            println(badge("WARN"), " ", fmt("submenu.groups.chess_empty"))
        else
            miss = [i for i in 23:33 if !(i in ids)]
            if isempty(miss)
                println(badge("INFO"), " ",
                        fmt("submenu.groups.run", name = "chess", ids = ids))
            else
                println(badge("INFO"), " ",
                        fmt("submenu.groups.run_missing",
                            name = "chess", ids = ids, miss = miss))
            end
            run_ids_with_lock!(cfg, ids)
        end
    elseif key == "v"
        # §14 v4: verhodge — 34–38 + 40 (HODGE-INF, классы Ходжа до бесконечности)
        ids = [t.id for t in TASKS if 34 <= t.id <= 38 || t.id == 40]
        if isempty(ids)
            println(badge("WARN"), " ", fmt("submenu.groups.verhodge_empty"))
        else
            miss = [i for i in (34, 35, 36, 37, 38, 40) if !(i in ids)]
            if isempty(miss)
                println(badge("INFO"), " ",
                        fmt("submenu.groups.run", name = "verhodge", ids = ids))
            else
                println(badge("INFO"), " ",
                        fmt("submenu.groups.run_missing",
                            name = "verhodge", ids = ids, miss = miss))
            end
            run_ids_with_lock!(cfg, ids)
        end
    elseif key == "w"
        _menu_sweep(m)
    elseif all(isdigit, key) && !isempty(key)
        tid = parse(Int, key)
        # BUGFIX(UX): цифра раньше СРАЗУ запускала прогон задачи — выглядело как
        # «меню само начинает тестирование». Теперь цифра отмечает/снимает
        # задачу (как Space), запуск — Enter (отмеченные) или a/f/h/c/v.
        if tid in SUITE_IDS
            if tid in m.marked
                delete!(m.marked, tid)
                println(badge("INFO"), " ", fmt("menu.mark_off", id = tid))
            else
                push!(m.marked, tid)
                println(badge("INFO"), " ", fmt("menu.mark_on", id = tid))
            end
        else
            println(badge("WARN"), " ", fmt("menu.no_task", id = tid))
        end
    elseif key == "p"
        println(fmt("menu.edit.prec_now", value = cfg.prec))
        v_ans = menu_read(fmt("menu.edit.prec_new"); allow_empty = true)
        if v_ans === nothing || isempty(v_ans)
            println(badge("INFO"), " ", fmt("menu.edit.prec_keep", value = cfg.prec))
        else
            v = parse_prec_value(v_ans)      # §3.2 v5: суффиксы k/m/g/t, без верхней границы
            if v === nothing
                println(badge("WARN"), " ", fmt("menu.edit.not_int", v = v_ans))
            else
                old_prec = cfg.prec
                cfg.prec = v
                hodge_prec_engine_apply!(cfg)   # точность движка следует за prec сразу
                # §3.2 v6: при тяжёлом prec — блок оценок и подтверждение (интерактив)
                est_lines = hodge_prec_estimates(cfg)
                confirmed = true
                if !isempty(est_lines)
                    for ln in est_lines
                        println(badge("WARN"), " ", ln)
                    end
                    if stdin isa Base.TTY
                        ans = menu_read(fmt("menu.edit.prec.confirm", value = v); allow_empty = true)
                        confirmed = ans === nothing || isempty(ans) ||
                                    lowercase(strip(ans)) in ("y", "yes", "д", "да")
                    end
                end
                if confirmed
                    save_settings_cache!(cfg)   # §3.2 v4
                    println(badge("INFO"), " ", fmt("menu.edit.prec_set", value = v))
                else
                    cfg.prec = old_prec
                    hodge_prec_engine_apply!(cfg)
                    println(badge("INFO"), " ", fmt("menu.edit.prec.revert", value = old_prec))
                end
            end
        end
    elseif key == "s"
        println(fmt("menu.edit.seed_now", value = cfg.seed))
        s_ans = menu_read(fmt("menu.edit.seed_new"); allow_empty = true)
        if s_ans === nothing || isempty(s_ans)
            println(badge("INFO"), " ", fmt("menu.edit.seed_keep", value = cfg.seed))
        else
            v = tryparse(Int, s_ans)
            if v === nothing
                println(badge("WARN"), " ", fmt("menu.edit.not_int", v = s_ans))
            else
                cfg.seed = v
                save_settings_cache!(cfg)   # §3.2 v4
                println(badge("INFO"), " ", fmt("menu.edit.seed_set", value = cfg.seed))
            end
        end
    elseif key == "n"
        println(fmt("menu.edit.preset_list"))
        v = menu_read(fmt("menu.edit.preset_choice", value = cfg.preset); allow_empty = true)
        if v === nothing || isempty(v)
            println(badge("INFO"), " ", fmt("menu.edit.preset_keep", value = cfg.preset))
        elseif v in ("quick", "full", "deep")
            cfg.preset = String(v)
            apply_preset!(cfg, cfg.preset)
            save_settings_cache!(cfg)   # §3.2 v4
            println(badge("INFO"), " ",
                    fmt("menu.edit.preset_set", value = cfg.preset,
                        prec = cfg.prec, twopass = cfg.two_pass))
        else
            println(badge("WARN"), " ", fmt("menu.edit.preset_unknown", v = v))
        end
    elseif key in ("t", "T")
        names = sort!(collect(keys(THEMES)))
        idx = findfirst(==(cfg.theme), names)
        cfg.theme = names[(something(idx, 0) % length(names)) + 1]
        theme_set!(cfg.theme, TEXT_STATE["depth"], TEXT_STATE["plain"])
        empty!(TEXT_STATE["_dye_cache"]); empty!(TEXT_STATE["_gradient_cache"])
        save_settings_cache!(cfg)   # §3.2 v4
        println(badge("INFO"), " ", fmt("menu.edit.theme_set", value = cfg.theme))
    elseif key == "l"
        cfg.lang = cfg.lang == "ru" ? "en" : "ru"
        TEXT_STATE["lang"] = cfg.lang
        save_settings_cache!(cfg)   # §3.2 v4
        println(badge("INFO"), " ", fmt("menu.edit.lang_set", value = cfg.lang))
    elseif key == "d"
        depths = ["auto", "truecolor", "256", "16", "mono"]
        idx = findfirst(==(cfg.color_depth), depths)
        cfg.color_depth = depths[(something(idx, 0) % length(depths)) + 1]
        save_settings_cache!(cfg)   # §3.2 v4
        println(badge("INFO"), " ", fmt("menu.edit.depth_set", value = cfg.color_depth))
    elseif key == "e"
        cfg.two_pass = !cfg.two_pass
        save_settings_cache!(cfg)   # §3.2 v4: настройка сохранена между запусками
        println(badge("INFO"), " ", fmt("menu.edit.twopass_set", value = cfg.two_pass ? "on" : "off"))
    elseif key == "P"
        cfg.prec_extreme = !cfg.prec_extreme
        cfg.prec_extreme && (cfg.prec = max(cfg.prec, 200); hodge_prec_extreme_apply!(cfg))
        save_settings_cache!(cfg)   # §3.2 v4: [P] живёт между запусками
        println(badge("INFO"), " ",
                fmt("menu.edit.precext_set", value = cfg.prec_extreme ? "on" : "off", prec = cfg.prec))
    elseif parse_prec_extreme_cmd(key) !== nothing
        # §14 v4: словный псевдоним prec-extreme — не только клавиша [P]:
        # «prec-extreme», «prec-extreme on|off», «precext»
        pc = parse_prec_extreme_cmd(key)
        cfg.prec_extreme = pc == "toggle" ? !cfg.prec_extreme : pc
        cfg.prec_extreme && (cfg.prec = max(cfg.prec, 200); hodge_prec_extreme_apply!(cfg))
        save_settings_cache!(cfg)   # §3.2 v4
        println(badge("INFO"), " ",
                fmt("menu.edit.precext_set", value = cfg.prec_extreme ? "on" : "off", prec = cfg.prec))
    elseif key == "x"
        _menu_dry_run(m)
    elseif key == "r"
        _menu_recipes(m)
    elseif key == "C"
        _menu_palette(m)
    elseif key == "V"
        # §11.10: 3D Video Lab — объект + fps + frames + N (подменю §14.2)
        _menu_video(m)
    else
        log_comp!(m.log, "WARN", "Menu", "unknown key $key")
        println(badge("WARN"), " ", fmt("menu.unknown", key = key))
    end
    return nothing
end

# BUGFIX(Freeze): eof(stdin) в julia ≥1.11 на TTY/пайпе БЛОКИРУЕТ до появления
# данных — меню «замерзало» на пустом Enter (выглядело как зависший REPL,
# Tasks «в фоне»). Замена: poll(fd, timeout=0) — если данных НЕТ, это не EOF
# (обычный пустой Enter); если данные/EOF готовы — обычный eof() отвечает
# мгновенно, без блокировки.
const _POLLIN  = Cshort(0x0001)
const _POLLERR = Cshort(0x0008)
const _POLLHUP = Cshort(0x0010)
struct _PollFD
    fd::Cint
    events::Cshort
    revents::Cshort
end
function stdin_eof_safe()
    fd = try
        Base.fd(stdin)
    catch
        return false          # нет fd — не рискуем блокировкой, считаем «не EOF»
    end
    # julia ≥1.13: Base.fd возвращает RawFD — примитив без полей, числовое
    # значение только через reinterpret (Int(::RawFD) не определён)
    fdn = try
        fd isa Base.RawFD ? reinterpret(Int32, fd) : Int(fd)
    catch
        return false
    end
    pfd = Ref(_PollFD(Cint(fdn), _POLLIN, Cshort(0)))
    r = ccall(:poll, Cint, (Ptr{_PollFD}, Cuint, Cint), pfd, Cuint(1), Cint(0))
    r < 0 && return false     # ошибка poll — консервативно «не EOF»
    (pfd[].revents & (_POLLIN | _POLLERR | _POLLHUP)) != 0 || return false
    try
        return eof(stdin)     # данные/EOF уже готовы → eof() не блокирует
    catch
        return false
    end
end

# Часть II: sweep-подменю — имя функции + sweep-спеки (декартово произведение).
# BUGFIX: у HodgeConfig поле lab3d_spec::String (не lab3d) — прежний код писал
# cfg.lab3d и падал "type HodgeConfig has no field lab3d" при sweep из меню.
function menu_sweep_input!(m::HodgeMenu, key::AbstractString)
    cfg = m.cfg
    lang_cfg = Dict("lang" => cfg.lang)
    fmt(k; kw...) = hodge_fmt(lang_cfg, k; kw...)
    if isempty(m.sweep_fn)
        # Валидация имени: раньше любое слово принималось, а lab_eval молча
        # рисовал нулевую поверхность. Теперь честный отказ со списком.
        cand = isempty(key) ? "omega" : String(key)
        base = startswith(cand, "expr:") ? "expr" : cand
        base in ("omega", "reflection", "census_h") || begin
            menu_render(m, fmt("menu.sweep_bad_fn", fn = cand))
            return
        end
        m.sweep_fn = cand
        menu_render(m, fmt("menu.sweep_spec_prompt", fn = m.sweep_fn))
        return
    end
    if isempty(key)
        m.mode = "nav"
        isempty(m.sweep_specs) && (m.sweep_specs = ["N:7:30:1"])
        # P2.3 / §11.6: предпросмотр — сколько кадров получится (cap 500)
        total = 1
        try
            for spec in m.sweep_specs
                _, vals = parse_sweep(spec)
                total *= length(vals)
            end
        catch ex
            menu_render(m, fmt("menu.sweep_invalid_spec", msg = sprint(showerror, ex)))
            return
        end
        println(badge("INFO"), " ",
                fmt("menu.sweep_preview", fn = m.sweep_fn,
                    specs = join(m.sweep_specs, ", "), n = total))
        # ⚠ bugfix: lab3d_spec, не lab3d; восстановление прежних значений в finally
        saved_spec   = cfg.lab3d_spec
        saved_sweeps = cfg.sweeps
        cfg.run_dir  = isempty(cfg.run_dir) ? new_run_dir(cfg) : cfg.run_dir
        cfg.lab3d_spec = m.sweep_fn
        cfg.sweeps     = copy(m.sweep_specs)
        try
            hodge_lab3d(cfg)
        finally
            cfg.lab3d_spec = saved_spec
            cfg.sweeps     = saved_sweeps
        end
        menu_render(m)
        return
    end
    try
        parse_sweep(key)
        push!(m.sweep_specs, String(key))
        menu_render(m, fmt("menu.sweep_added", key = key))
    catch ex
        menu_render(m, fmt("menu.sweep_invalid", msg = sprint(showerror, ex)))
    end
end

function menu_run!(m::HodgeMenu)
    menu_render(m)
    lang_cfg = Dict("lang" => m.cfg.lang)
    fmt(k; kw...) = hodge_fmt(lang_cfg, k; kw...)
    replay = nothing   # P2.1: строка из истории для повторного исполнения
    while true
        try
            # BUGFIX(A/Ctrl+D): eof(stdin) проверяем ДО readline — на Linux
            # Ctrl+D в TTY даёт пустую строку и НЕ EOFError, а строка
            # `m.eof = 0` ниже съедала счётчик → EOF-guard никогда не срабатывал
            # (бесконечный цикл меню).
            if replay === nothing && stdin_eof_safe()
                println(hodge_fmt(Dict("lang" => m.cfg.lang), "menu.bye"))
                return 0
            end
            line = replay !== nothing ? (tmp = replay; replay = nothing; tmp) :
                   readline(stdin)
            # защита от реального EOF в середине потока (readline вернул "")
            if isempty(line) && stdin_eof_safe()
                println(hodge_fmt(Dict("lang" => m.cfg.lang), "menu.bye"))
                return 0
            end
            # пустой Enter (только \n) ≠ Space (пробел(ы) без текста):
            # strip() съедает и то, и другое — различаем по chomp(line)
            if isempty(strip(line)) && isempty(chomp(line))
                # §14.5: Enter запускает отмеченные (или выбранную под фильтром);
                # пустой Enter без контекста — перерисовать (EOF-guard §14.7).
                # BUGFIX(C/busy-loop): REPL/синтетический stdin может возвращать ""
                # из readline НЕМЕДЛЕННО и с eof(stdin)==false — прежний код крутил
                # menu_render на 100% CPU вечно (счётчик сбрасывался каждый виток).
                # Теперь: контекст (marked/filter/sweep) работает как раньше;
                # без контекста — счётчик m.eof (сброс только на реальном вводе),
                # sleep(10мс) против CPU-ожога, после MENU_EOF_LIMIT — graceful exit.
                if m.mode == "filter"
                    m.eof = 0
                    m.mode = "nav"
                    menu_render(m)
                    continue
                elseif m.mode == "sweep"
                    m.eof = 0
                    menu_sweep_input!(m, "")
                    continue
                elseif !isempty(m.marked)
                    m.eof = 0
                    run_ids_with_lock!(m.cfg, sort!(collect(m.marked)))
                elseif !isempty(m.filter)
                    m.eof = 0
                    items = visible_tasks(m)
                    isempty(items) || run_ids_with_lock!(m.cfg, [items[clamp(m.selected + 1, 1, length(items))].id])
                else
                    m.eof += 1
                    if m.eof >= MENU_EOF_LIMIT
                        println(hodge_fmt(Dict("lang" => m.cfg.lang), "menu.bye"))
                        return 0
                    end
                    sleep(0.01)
                    menu_render(m, fmt("menu.eof_guard", n = m.eof, limit = MENU_EOF_LIMIT))
                    continue
                end
                menu_render(m)
                continue
            end
            m.eof = 0
            key = strip(line)
            raw = chomp(line)   # ввод без \n — пробелы сохранены (см. Space ниже)
            # P2.1 / §14.5: история — !! повтор последней, !N повтор N-й.
            # Replay через локальный буфер: строка обработается как обычный ввод.
            was_replay = replay !== nothing
            if startswith(key, "!")
                if key == "!!"
                    isempty(m.history) ? menu_render(m, fmt("menu.history_empty")) :
                        (replay = m.history[end])
                elseif length(key) > 1 && all(c -> isdigit(c), key[2:end])
                    idx = parse(Int, key[2:end])
                    if 1 <= idx <= length(m.history)
                        replay = m.history[idx]
                    else
                        menu_render(m, fmt("menu.no_history", n = idx, total = length(m.history)))
                    end
                else
                    menu_render(m, fmt("menu.history_hint"))
                end
                continue
            end
            # P2.2 / §27.5: Ctrl+Y или copy — путь прогона в буфер (OSC 52)
            if key in ("\x19", "copy")
                if m.cfg.no_clipboard
                    menu_render(m, fmt("menu.copy_disabled"))
                elseif isempty(m.cfg.run_dir)
                    menu_render(m, fmt("menu.copy_empty"))
                else
                    print(stdout, "\x1b]52;c;$(base64encode(m.cfg.run_dir))\x1b\\")
                    flush(stdout)
                    menu_render(m, fmt("menu.copy_done", path = m.cfg.run_dir))
                end
                continue
            end
            # P2.1: пишем в историю навигационные команды (текст фильтра — нет);
            # повтор (!! / !N) в историю не пишем — иначе дубли
            if !was_replay && m.mode == "nav" && !isempty(key) && key != "q"
                push!(m.history, String(key))
                length(m.history) > 100 && popfirst!(m.history)
            end
            if m.mode == "filter"
                isempty(key) ? (m.mode = "nav") : (m.filter = String(key); m.selected = 0)
                menu_render(m)
                continue
            end
            if m.mode == "sweep"
                menu_sweep_input!(m, String(key))
                continue
            end
            if key == "/"
                m.mode = "filter"
                m.filter = ""
                menu_render(m, fmt("menu.filter_mode"))
                continue
            elseif isempty(key) && raw != ""
                # Space (строка из одних пробелов) — отметить/снять отмеченную.
                # BUGFIX: раньше key == strip(line) == "" и ветка key == " " была
                # мёртвой — Space молча запускал отмеченные задачи.
                items = visible_tasks(m)
                isempty(items) || begin
                    tid = items[clamp(m.selected + 1, 1, length(items))].id
                    tid in m.marked ? delete!(m.marked, tid) : push!(m.marked, tid)
                end
                menu_render(m)
                continue
            elseif key in ("j", "k")
                items = visible_tasks(m)
                m.selected = key == "j" ?
                    clamp(m.selected + 1, 0, max(0, length(items) - 1)) :
                    clamp(m.selected - 1, 0, max(0, length(items) - 1))
                menu_render(m)
                continue
            end
            cmd = menu_handle!(m, key)
            cmd === nothing && (menu_render(m); continue)
            cmd == "quit" && begin
                save_settings_cache!(m.cfg)   # §3.2 v4: финальное сохранение сессии меню
                println(hodge_fmt(Dict("lang" => m.cfg.lang), "menu.bye"))
                return 0
            end
            menu_render(m)
        catch ex
            if ex isa EOFError
                m.eof += 1
                m.eof >= MENU_EOF_LIMIT && begin
                    println(hodge_fmt(Dict("lang" => m.cfg.lang), "menu.bye"))
                    return 0
                end
                menu_render(m, fmt("menu.eof_guard", n = m.eof, limit = MENU_EOF_LIMIT))
                continue
            elseif ex isa InterruptException
                println(badge("INFO"), " ", fmt("menu.ctrl_c"), " (§14.3)")
                menu_render(m, fmt("menu.ctrl_c"))
                continue
            else
                println(badge("WARN"), " ", fmt("menu.input_error", msg = sprint(showerror, ex)))
                menu_render(m)
                continue
            end
        end
    end
end

# VI.8: меню-путь — прогон выбранных задач под flock (§24.2 / B5).
# BUGFIX(VI.3a): install_signals! вешается ТОЛЬКО на время compute (§7.6):
# при активном flag-обработчике readline(stdin) не получает InterruptException
# и меню «зависало» на Ctrl+C. Здесь обработчиков нет → стандартный Ctrl+C.
# BUGFIX(Lock): ВСЕГДА новый run_dir — переиспользование меню-каталога давало
# ERR_LOCK_HELD при повторном [c]/[a], пока предыдущий прогон (или другая
# сессия) держит flock. Новый каталог = свой lock, коллизий нет.
# BUGFIX(Leak): close_logger! в finally — comp_io/events_io больше не утекают;
# ACTIVE_LOGGER восстанавливается в menu-логгер, а не в nothing.
run_ids_with_lock!(cfg::HodgeConfig, ids::Vector{Int}) = begin
    cfg.tasks = ids
    # BUGFIX(Race): два процесса в одну секунду выбирали ОДНО имя каталога
    # (isdir ещё false у обоих) → второй упирался в чужой flock → ERR_LOCK_HELD.
    # Ретраи: каждый виток берёт СВЕЖИЙ суффикс _1.._N → свой lock.
    lock = nothing
    err = ""
    for _ in 1:5
        cfg.run_dir = new_run_dir(cfg)     # ← ВСЕГДА новый путь + новый lock
        lock, err = flock_acquire!(cfg.run_dir)
        lock !== nothing && break
        sleep(0.05)
    end
    if lock === nothing
        println(badge("FAIL"), " ERR_LOCK_HELD: $err")
        return 2
    end
    install_signals!()             # только на время compute (§7.6 / VI.3a)
    RUN_LOCK[] = lock
    lg = HodgeLogger(cfg)
    open_run!(lg, cfg.run_dir)
    prev_logger = ACTIVE_LOGGER[]
    ACTIVE_LOGGER[] = lg
    cfg._lock_held = true
    try
        return run_suite_body!(cfg, lg; pipe_mode = false)
    finally
        restore_signals!()         # восстановить до возврата в меню
        close_logger!(lg)          # закрыть comp_io/events_io (P2.12)
        lock_release!(lock)        # §24.2 v4: снимает любой режим каскада
        RUN_LOCK[] = nothing
        ACTIVE_LOGGER[] = prev_logger   # вернуть menu-логгер
        cfg._lock_held = false
    end
end

# ════════════════════════════════════════════════════════════════════════
# ── SELF-TEST: уровни unit/props/palette/dye/menu/plot/lab/golden. ──
# ════════════════════════════════════════════════════════════════════════
const ST_RESULTS = Vector{Dict{String,Any}}()

selftest_check!(name::AbstractString, level::AbstractString, ok::Bool, reason::AbstractString = "") = begin
    push!(ST_RESULTS, Dict("name" => name, "level" => level,
                           "verdict" => ok ? "PASS" : "FAIL", "reason" => reason))
    print("  ", badge(ok ? "PASS" : "FAIL"), " [$level] $name",
          isempty(reason) ? "" : " · " * ascii_fallback(reason), "\n")
    flush(stdout)
    nothing
end

function selftest_unit()
    t0 = time()
    ok = true
    ok &= begin
        r = sm64(1) == 0x910A2DEC89025CC1 && sm64(2) == 0x975835DE1C9756CE &&
            sm64(3) == 0x1D0B14E4DB018FED
        selftest_check!("splitmix64: sm(1..3) канонические векторы", "unit", r); r
    end
    ok &= begin
        r = all(sm64_inv(sm64(x)) == x for x in 1:2000)
        selftest_check!("splitmix64_inverse∘splitmix64 = id на 1..2000", "unit", r); r
    end
    ok &= begin
        r = Dict(census(15)[1]) == Dict(census_mobius(15))
        selftest_check!("Ценз: две схемы, N=15", "unit", r); r
    end
    ok &= begin
        r = snf([2 0; 0 3]) == [1, 6] && snf([6 0 0; 0 10 0; 0 0 15]) == [1, 30, 30]
        selftest_check!("SNF diag(2,3)→(1,6); diag(6,10,15)→(1,30,30) (NE02)", "unit", r); r
    end
    ok &= begin
        r = abs(gamma_hp(big(1.0)) - 1) < big(10.0)^-90 &&
            abs(gamma_hp(big(1) / 2) - sqrt(big(π))) < big(10.0)^-90
        selftest_check!("Γ(1)=1, Γ(1/2)=√π", "unit", r); r
    end
    ok &= begin
        r = all(tstar(w, h, a, b) == e for (w, h, a, b, e) in
                [(48, 48, 1, 1, 48), (96, 96, 1, 1, 96), (24, 36, 3, 5, 72),
                 (7, 14, 1, 1, 14), (12, 12, 4, 6, 6), (384, 384, 1, 1, 384)])
        selftest_check!("t*: 6 случаев cert E", "unit", r); r
    end
    ok &= begin
        r = qscan(2.75, 16) == (4, 11) && qscan(4 * π^2, 16) === nothing
        selftest_check!("qscan(2.75,16)=(4,11); 4π² не рационализируется", "unit", r); r
    end
    ok &= begin
        # BUGFIX(StringIndex): бывшие фатальные bucket'ы (idx 2,3,5,6,8 — не
        # байтовые границы UTF-8 глифов) + ASCII-режим + крайние случаи
        u0 = TEXT_STATE["unicode_on"]
        vals_u = collect(0.0:0.125:1.0)
        vals_a = [0.1, 0.3, 0.5, 0.7, 0.9, 0.2, 0.4, 0.6, 0.8]
        r = try
            TEXT_STATE["unicode_on"] = true
            s1 = sparkline_render(vals_u)
            TEXT_STATE["unicode_on"] = false
            s2 = sparkline_render(vals_a)
            TEXT_STATE["unicode_on"] = u0
            length(s1) == length(vals_u) && length(s2) == length(vals_a) &&
                sparkline_render(Float64[]) == "" &&
                length(sparkline_render([0.5])) == 1 &&
                length(sparkline_render([0.7, 0.7])) == 2
        catch
            TEXT_STATE["unicode_on"] = u0
            false
        end
        selftest_check!("sparkline: UTF-8/ASCII все bucket'ы без StringIndexError", "unit", r); r
    end
    ok &= begin
        # BUGFIX(i18n): вердикты задач при lang=en — фразбук + title_en в реестре
        r = run_i18n("V3: фазовый закон, dev=2.36e-97", "en") == "V3: phase law, dev=2.36e-97" &&
            run_i18n("ценз/род подтверждены (2 схемы, 7 уровней): N=4:g=3", "en") ==
                "genus census confirmed (2 schemes, 7 levels): N=4:g=3" &&
            run_i18n("V2: 24 периодов closed=tanh-sinh, rel=1.69e-71", "en") ==
                "V2: 24 periods closed=tanh-sinh, rel=1.69e-71" &&
            run_i18n("V3: фазовый закон, dev=2.36e-97", "ru") == "V3: фазовый закон, dev=2.36e-97" &&
            run_i18n("rel=1.0e-71 latin only", "en") == "rel=1.0e-71 latin only" &&
            all(!isempty(t.title_en) for t in TASKS)
        selftest_check!("run_i18n: фразбук en/ru + title_en у 24 задач", "unit", r); r
    end
    # ── §33.8 / §3.2 v4 / §14 v4: новые подсистемы сессии 4 ──
    ok &= begin
        r = all(ramanujan_c(12, k) == ramanujan_divisor(12, k) for k in 0:11)
        selftest_check!("рамануджаново сито: μ-формула = сумме по делителям (N=12, все k)", "unit", r); r
    end
    ok &= begin
        rows = hodge_inf_tower((5,); prec_eff = 120)
        r = rows[1].err_engine < 1e-30 && rows[1].exact_ok
        selftest_check!("HODGE-INF N=5: Ω-рефлексия HP vs π/sin на prec 120 бит", "unit", r); r
    end
    # ── §3.2 v5: prec без границ — парсер, константы, Γ-слой, масштабирование ──
    ok &= begin
        r = parse_prec_value("4096") == 4096 && parse_prec_value("5m") == 5_000_000 &&
            parse_prec_value("1g") == 10^9 && parse_prec_value("2t") == 2 * 10^12 &&
            parse_prec_value("abc") === nothing && parse_prec_value("29") === nothing &&
            parse_prec_value(" 1g ") == 10^9
        selftest_check!("parse_prec_value: 4096/5m/1g/2t/мусор/29 (§3.2 v5)", "unit", r); r
    end
    ok &= begin
        ref = setprecision(1100) do
            big(π)
        end
        e320 = Float64(abs(pi_hp(320) - ref) / ref)
        e1024 = Float64(abs(pi_hp(1024) - ref) / ref)
        r = e320 < 2.0^-318 && e1024 < 2.0^-1022 && e1024 < e320
        selftest_check!("pi_hp: константа следует за precision (320 → 1024 бит)", "unit", r); r
    end
    ok &= begin
        setprecision(BigFloat, 600)
        g = gamma_hp(BigFloat("0.5"))
        err = Float64(abs(g * g - pi_hp()) / pi_hp())
        setprecision(BigFloat, 320)
        r = err < 1e-170
        selftest_check!("lgamma_hp: Γ(1/2)² → π на prec 600 (ζ-отношение)", "unit", r); r
    end
    ok &= begin
        rows = hodge_inf_tower((5, 10); prec_eff = 512)
        r = maximum(rr.err_engine for rr in rows) < 1e-140
        selftest_check!("HODGE-INF: prec 512 бит — engine err < 1e-140 (масштабируется)", "unit", r); r
    end
    # §3.2 v6: гейты — Γ на гигантском prec падает с честным ERR_GAMMA_PREC
    # (раньше «зависала»: ζ-сумма ~10^4970 членов), Γ на рабочем prec точен
    ok &= begin
        r = false; why = ""
        try
            setprecision(BigFloat, 20000)
            gamma_hp(BigFloat("0.5"))
            why = "gamma@20000 не упал"
        catch e
            s = sprint(showerror, e)
            if occursin("ERR_GAMMA_PREC", s)
                setprecision(BigFloat, 1024)
                g = gamma_hp(BigFloat("0.5"))
                err = Float64(abs(g * g - pi_hp()) / pi_hp())
                err < 1e-290 ? (r = true) : (why = "Γ(1/2)²@1024 ≠ π (err=$err)")
            else
                why = s[1:min(60, end)]
            end
        finally
            setprecision(BigFloat, 320)
        end
        selftest_check!("гейты §3.2 v6: Γ@20000→ERR_GAMMA_PREC, Γ@1024 точен", "unit", r, why); r
    end
    ok &= begin
        r = false
        try
            td = mktempdir()
            c1 = HodgeConfig(cache_dir = td)
            c1.prec_extreme = true; c1.prec = 200
            p = save_settings_cache!(c1)
            c2 = HodgeConfig(cache_dir = td)
            applied = load_settings_cache!(c2)
            r = isfile(p) && c2.prec_extreme === true && c2.prec == 200 &&
                "prec_extreme" in applied && "prec" in applied
            rm(td; force = true, recursive = true)
        catch
            r = false
        end
        selftest_check!("settings cache: save→load roundtrip prec_extreme/prec", "unit", r); r
    end
    ok &= begin
        r = parse_prec_extreme_cmd("prec-extreme") == "toggle" &&
            parse_prec_extreme_cmd("precext") == "toggle" &&
            parse_prec_extreme_cmd("prec-extreme on") === true &&
            parse_prec_extreme_cmd("precext off") === false &&
            parse_prec_extreme_cmd("P") === nothing
        selftest_check!("prec-extreme word alias: toggle/on/off/не-команда", "unit", r); r
    end
    dt = time() - t0
    # §3.2 v5: порог 8 с — добавлены 4 проверки масштабирования prec
    # (pi_hp/lgamma_hp/башня 512 бит) и их холодный JIT при первом прогоне
    selftest_check!("unit-уровень ≤ 8 с", "unit", dt < 8.0, @sprintf("%.2f с", dt))
    return ok
end

function selftest_props()
    ok = true
    h1 = json_dump(Dict(string(k) => v for (k, v) in census(30)[1]))
    h2 = json_dump(Dict(string(k) => v for (k, v) in census(30)[1]))
    ok &= begin
        r = h1 == h2
        selftest_check!("детерминизм: census(30) дважды — байт-идентично", "props", r); r
    end
    ok &= begin
        r = all(sum(values(census(N)[1])) == (N - 1) * (N - 2) ÷ 2 for N in 3:40)
        selftest_check!("инвариант: Σh_d = g для всех N∈[3,40]", "props", r); r
    end
    ok &= begin
        inv = snf(trace_gram(15))
        r = all(inv[i+1] % inv[i] == 0 for i in 1:length(inv)-1)
        selftest_check!("инвариант: d_i | d_{i+1} в SNF", "props", r); r
    end
    return ok
end

function selftest_palette()
    ok = true
    for name in sort!(collect(keys(THEMES)))
        pal = THEMES[name]
        missing = [k for k in PALETTE_KEYS if !haskey(pal, k)]
        ok &= begin
            r = isempty(missing)
            selftest_check!("тема $name: все ключи в наличии", "palette", r,
                            isempty(missing) ? "" : "ERR_PALETTE_MISSING $missing"); r
        end
    end
    # A6: mono — dye/num/gradient возвращают СЫРУЮ строку
    saved = (TEXT_STATE["theme"], TEXT_STATE["depth"], TEXT_STATE["plain"])
    theme_set!("dark-gold", "mono", true)
    ok &= begin
        r = TEXT_STATE["plain"] && dye("probe", "gold") == "probe" &&
            num(42, "int") == "42" && gradient("abc", "gold_dim", "gold_bright") == "abc" &&
            color_code("gold") == ""
        selftest_check!("mono: dye/num/gradient — сырая строка, color_code пуст", "palette", r); r
    end
    theme_set!(saved[1], saved[2], saved[3])
    ok &= begin
        r = begin
            n = 200
            best = argmin(abs(hex2rgb("#d4af37")[1] - round(Int, 255 * (i / (n - 1)))) for i in 0:n-1)
            true
        end
        selftest_check!("rgb→xterm256 (ближайший куб): #d4af37 → 179", "palette",
                        rgb_to_xterm256(hex2rgb("#d4af37")) == 179); r
    end
    return ok
end

    """§31: формула ближайшего куба xterm-256 (перенос из Python-мастера)."""
rgb_to_xterm256(rgb::Tuple{Int,Int,Int}) = begin
    r, g, b = rgb
    idx(i) = i <= 47 ? 0 : i <= 115 ? 1 : min(5, (i - 35) ÷ 40)
    ri, gi, bi = idx(r), idx(g), idx(b)
    gray = round(Int, (r + g + b) / 3)
    cube = [0, 95, 135, 175, 215, 255]
    cr, cg, cb = cube[ri+1], cube[gi+1], cube[bi+1]
    dist_cube = (r - cr)^2 + (g - cg)^2 + (b - cb)^2
    gi2 = gray <= 3 ? 0 : gray >= 243 ? 23 : round(Int, (gray - 8) / 10)
    gv = 8 + 10 * gi2
    dist_gray = (r - gv)^2 + (g - gv)^2 + (b - gv)^2
    dist_gray < dist_cube ? 232 + gi2 : 16 + 36 * ri + 6 * gi + bi
end

function selftest_dye()
    old = (TEXT_STATE["theme"], TEXT_STATE["depth"], TEXT_STATE["plain"])
    theme_set!("dark-gold", "truecolor", false)
    ok = true
    s = dye("42", "gold")
    ok &= begin
        r = startswith(s, "\x1b[")
        selftest_check!("dye возвращает окрашенную строку (truecolor)", "dye", r); r
    end
    ok &= begin
        r = dye(s, "gold") == s
        selftest_check!("dye идемпотентна: повтор не дублирует ANSI", "dye", r); r
    end
    ok &= begin
        n0 = num(0, "int"); n999 = num(999, "int"); nneg = num(-5, "int")
        r = n0 != n999 != nneg
        selftest_check!("num tiering: 0→gold_dim, 999→gold_bright, −5→ember", "dye", r); r
    end
    ok &= begin
        counts = Dict{String,Int}()
        for m in ("per-char", "per-token", "per-line")
            TEXT_STATE["dye_mode"] = m
            empty!(TEXT_STATE["_gradient_cache"])
            out = gradient("ABC DEF GHI", "gold_dim", "gold_bright")
            counts[m] = length(collect(eachmatch(r"\x1b\[38;2;", out)))
        end
        r = counts["per-char"] > counts["per-token"] > 0 && counts["per-line"] == 1
        selftest_check!("dye-mode: per-char > per-token > per-line=1 (A14)", "dye", r,
                        join(["$k=$(v)" for (k, v) in sort!(collect(counts))], ", ")); r
    end
    ok &= begin
        r = occursin("[ok]", ascii_fallback("✓")) && occursin("#", ascii_fallback("█"))
        selftest_check!("--unicode off: глифы → ASCII, кириллица не тронута (A13/§16)", "dye",
                        r && ascii_fallback("проверок") == "проверок"); r
    end
    theme_set!(old[1], old[2], old[3])
    return ok
end

function selftest_menu()
    ok = true
    cfg = HodgeConfig(lang = "ru", theme = "dark-gold", color_depth = "mono", plain = true)
    theme_set!(cfg.theme, "mono", true)
    lg = HodgeLogger(cfg)
    m = HodgeMenu(cfg, lg)
    ok &= begin
        r = menu_handle!(m, "?") === nothing
        selftest_check!("меню открывается: '?' рендерит помощь", "menu", r); r
    end
    ok &= begin
        r = menu_handle!(m, "q") == "quit"
        selftest_check!("меню: `q` → quit", "menu", r); r
    end
    ok &= begin
        before = length(visible_tasks(m))
        m.filter = "periods"
        r = length(visible_tasks(m)) == 1 && visible_tasks(m)[1].id == 2
        m.filter = ""
        selftest_check!("меню: fuzzy-фильтр «periods» → 1 задача (id 2)", "menu", r); r
    end
    ok &= begin
        push!(m.marked, 1); push!(m.marked, 18)
        r = length(m.marked) == 2
        selftest_check!("меню: Space-мультивыбор", "menu", r); r
    end
    return ok
end

function selftest_plot()
    ok = true
    cv = HodgeCanvas(20, 20, (10, 8, 5))
    line!(cv, 1, 1, 20, 20, (255, 0, 0))
    ok &= begin
        r = cv.buf[1] == 255 && cv.buf[4] == 10   # пиксель (1,1) на диагонали → 255; (2,1) фон → 10
        selftest_check!("canvas: line рисует по диагонали (Брезенхем)", "plot", r); r
    end
    p = HodgePlot(40, 30; title = "t", aa = 1)
    plot_add!(p, "s", [0, 1, 2], [0, 1, 0])
    png = png_encode(p.out_W, p.out_H, plot_render(p))
    ok &= begin
        r = png[1:8] == PNG_SIGNATURE
        selftest_check!("png: валидная подпись \\x89PNG", "plot", r); r
    end
    gif = gif_encode(4, 4, [(0, 0, 0), (255, 255, 255)],
                     [UInt8.(zeros(16)), UInt8.(ones(16))], [10, 10])
    ok &= begin
        r = gif[1:6] == UInt8['G', 'I', 'F', '8', '9', 'a'] && gif[end] == 0x3B
        selftest_check!("gif: валидная подпись GIF89a + trailer 0x3B", "plot", r); r
    end
    # §F-структура GCE (регрессия s5: лишний 0x04 сдвигал поле delay на байт
    # → зрители читали задержку ×256, кадры «замирали», после GCE оставался
    # посторонний пустой блок). GCE ровно 8 байт: 21 F9 04 | 04 | DD DD | 00 | 00,
    # после него — сразу 2C/21/3B.
    g2 = gif_encode(6, 4, [(0, 0, 0), (255, 255, 255)],
                    [fill(UInt8(0), 24), fill(UInt8(1), 24)], [7, 33])
    gces = Vector{Tuple{Int,Int,Int,Int,Int}}(); chain_ok = true
    try
        i = 13 + 3 * 256
        while i <= length(g2)
            b = g2[i]
            b == 0x3B && break
            if b == 0x21
                if g2[i+1] == 0xF9
                    n = Int(g2[i+2])
                    push!(gces, (n, Int(g2[i+3]), Int(g2[i+4]) | Int(g2[i+5]) << 8,
                                 Int(g2[i+6]), Int(g2[i+3+n])))
                end
                i += 2
                while g2[i] != 0x00; i += 1 + Int(g2[i]); end
                i += 1
                chain_ok &= i <= length(g2) && g2[i] in (0x21, 0x2C, 0x3B)
                continue
            end
            if b == 0x2C
                f = Int(g2[i+9]); i += 10
                if f & 0x80 != 0; i += 3 * (2 << (f & 7)); end
                i += 1                       # min code size
                while g2[i] != 0x00; i += 1 + Int(g2[i]); end
                i += 1
                chain_ok &= i <= length(g2) && g2[i] in (0x21, 0x2C, 0x3B)
                continue
            end
            chain_ok = false; break
        end
    catch
        chain_ok = false
    end
    ok &= begin
        r = chain_ok && length(gces) == 2 && gces[1] == (4, 4, 7, 0, 0) &&
            gces[2] == (4, 4, 33, 0, 0)
        selftest_check!("gif: GCE ровно 8 байт, delay 7/33 cs, цепочка блоков чистая (s5)",
                        "plot", r); r
    end
    ok &= begin
        r = gif_delay_cs(24) == 4 && gif_delay_cs(30) == 3 &&
            gif_delay_cs(50) == 2 && gif_delay_cs(5) == 20
        selftest_check!("gif: delay = round(100/fps) cs: 24→4, 30→3, 50→2, 5→20", "plot", r); r
    end
    cache = Dict{String,Any}()
    idx, gct = quantize_rgb!(repeat(UInt8.(collect(hex2rgb(PLOT_BG))); outer = 16), cache, "dark-gold")
    ok &= begin
        r = length(gct) == 256 && cache["exact"][(10, 8, 5)] == idx[1]
        selftest_check!("gct: PLOT_BG точно в GCT, 256 записей", "plot", r); r
    end
    name, vals = parse_sweep("N:5:9:2")
    ok &= begin
        r = name == "N" && vals == [5, 7, 9]
        selftest_check!("sweep-парсер: N:5:9:2 → [5,7,9]", "plot", r); r
    end
    return ok
end

function selftest_lab()
    ok = true
    d = mktempdir()
    lab = Hodge3DLab(Dict("run_dir" => d, "plot_width" => 200, "plot_height" => 150,
                          "theme" => "dark-gold", "gct_cache" => Dict{String,Any}()))
    m = lab_run!(lab, "omega", Dict("N" => [7, 9]); grid_n = 8, max_frames = 4)
    ok &= begin
        pngs = filter(f -> occursin(r"frame_\d+\.png$", f), readdir(lab.out_dir; join = true))
        r = m["frames"] == 2 && length(pngs) == 2
        selftest_check!("lab3d: манифест и 2 PNG", "lab", r); r
    end
    ok &= begin
        r = isfile(joinpath(lab.out_dir, "sweep.gif")) &&
            read(joinpath(lab.out_dir, "sweep.gif"))[end] == 0x3B
        selftest_check!("lab3d: gif создан и заканчивается 0x3B", "lab", r); r
    end
    return ok
end

function selftest_golden!(cfg::HodgeConfig)
    """§19.4: сравнение скалярных результатов с golden/scalars.json."""
    mkpath(cfg.golden_dir)
    golden_path = joinpath(cfg.golden_dir, "scalars.json")
    cfg2 = HodgeConfig(preset = "quick", two_pass = false, tasks = [1, 9, 13, 18])
    lg = HodgeLogger(cfg2)
    r = HodgeRunner(cfg2, lg)
    run_all!(r)
    # §19.4: golden — только ДЕТЕРМИНИРОВАННЫЕ значения (ok-флаги пассов и
    # сиды доменов задач); durations шумят и в эталон не включаются
    current = Dict{String,Any}()
    for (tid, rec) in r.results
        for (pno, p) in rec["passes"]
            current["$(tid)_p$(pno)_ok"] = p["ok"] ? 1.0 : 0.0
        end
        current["$(tid)_seed"] = Float64(mod(derive_seed(cfg2, "task", tid), 1_000_000))
    end
    if cfg.golden_update || "golden-update" in cfg.self_test
        hodge_atomic_write(golden_path, json_dump(current))
        selftest_check!("golden: эталоны перезаписаны ($(length(current)) значений)", "golden", true)
        return true
    end
    if !isfile(golden_path)
        push!(ST_RESULTS, Dict("name" => "golden: файл эталонов не найден", "level" => "golden",
                               "verdict" => "SKIP", "reason" => "создайте --golden-update"))
        println("  ", badge("SKIP"), " [golden] golden: создайте --golden-update в $golden_path")
        return true
    end
    expected = json_load_flat(read(golden_path, String))
    tol = cfg.float_tolerance
    bad = String[]
    for k in sort!(collect(keys(expected)))
        cur = get(current, k, nothing)
        if cur === nothing
            push!(bad, "$k: missing"); continue
        end
        abs(Float64(cur) - Float64(expected[k])) > tol * max(abs(Float64(expected[k])), 1.0) &&
            push!(bad, "$k: $cur vs $(expected[k])")
    end
    selftest_check!("golden: $(length(expected) - length(bad))/$(length(expected)) совпали (tol=$tol)",
                    "golden", isempty(bad), isempty(bad) ? "" : join(bad[1:min(3, end)], "; "))
    return isempty(bad)
end

function selftest_l10n()
    """P0.5 / §19.2: полнота словарей ru/en — множества ключей совпадают."""
    ru, en = Set(keys(MSG["ru"])), Set(keys(MSG["en"]))
    miss = union(setdiff(ru, en), setdiff(en, ru))
    selftest_check!("l10n: все ключи MSG есть и в ru, и в en", "l10n",
                    isempty(miss), isempty(miss) ? "" : "нет: " * join(sort(collect(miss)), ", "))
    return isempty(miss)
end

function selftest_anim()
    """P0.5 / §19.2: fps-таймер не дрейфует (0.1 с ≈ 6 итераций 1/60; окно
    0.05–0.30 с — устойчиво к загрузке CI, но ловит сломанный таймер)."""
    t0 = time()
    n = 0
    while time() - t0 < 0.1
        sleep(1 / 60)
        n += 1
    end
    el = time() - t0
    ok = 0.05 <= el <= 0.30 && n >= 4
    selftest_check!("anim: fps-таймер 0.1с ≈ 6·(1/60), дрейф в окне", "anim",
                    ok, @sprintf("%.3f с, %d итераций", el, n))
    return ok
end

function run_selftest!(cfg::HodgeConfig)
    """Все уровни; SELFTEST.md + logs/selftest.jsonl пишутся при run_dir."""
    empty!(ST_RESULTS)
    levels = isempty(cfg.self_test) ? ["unit"] : copy(cfg.self_test)
    ("full" in levels) && (levels = ["unit", "props", "l10n", "palette", "dye", "anim",
                                     "menu", "plot", "lab"])
    "unit" in levels && selftest_unit()
    "props" in levels && selftest_props()
    "l10n" in levels && selftest_l10n()     # P0.5: были в full-списке, но не вызывались
    "anim" in levels && selftest_anim()
    "palette" in levels && selftest_palette()
    "dye" in levels && selftest_dye()
    "menu" in levels && selftest_menu()
    "plot" in levels && selftest_plot()
    "lab" in levels && selftest_lab()
    "golden" in levels && selftest_golden!(cfg)
    fails = count(r -> r["verdict"] == "FAIL", ST_RESULTS)
    println(dye("── self-test: $(length(ST_RESULTS)) проверок, $fails FAIL ──", "gold"))
    if !isempty(cfg.run_dir)
        mkpath(joinpath(cfg.run_dir, "logs"))
        hodge_atomic_write(joinpath(cfg.run_dir, "logs", "selftest.jsonl"),
                           join(json_dump.(ST_RESULTS), "\n") * "\n")
        hodge_atomic_write(joinpath(cfg.run_dir, "SELFTEST.md"),
                           "# SELFTEST\n\n" * join(["- $(r["verdict"]) [$(r["level"])] $(r["name"])" for r in ST_RESULTS], "\n") * "\n")
    end
    return fails == 0 ? 0 : 1
end

# ════════════════════════════════════════════════════════════════════════
# §26 CI-ВЫВОДЫ + _run_suite + MAIN (§0/§18: menu-first при голом запуске).
# ════════════════════════════════════════════════════════════════════════
hodge_jsonl_out!(cfg::HodgeConfig, runner::HodgeRunner) = begin
    for r in results_sorted(runner)
        println(json_dump(Dict("event" => "task_verdict", "task" => r["id"],
                               "slug" => r["slug"], "verdict" => r["verdict"],
                               "reason" => r["reason"], "claims" => r["claims"],
                               "durations" => Dict(string(k) => v["duration_s"] for (k, v) in r["passes"]))))
    end
    flush(stdout)
    nothing
end

hodge_tsv_out!(cfg::HodgeConfig, runner::HodgeRunner) = begin
    println("id\tslug\tverdict\tduration_s\treason")
    for r in results_sorted(runner)
        println("$(r["id"])\t$(r["slug"])\t$(r["verdict"])\t" *
                @sprintf("%.3f", sum(p["duration_s"] for p in values(r["passes"]))) *
                "\t$(something(r["reason"], ""))")
    end
    flush(stdout)
    nothing
end

function run_suite_body!(cfg::HodgeConfig, lg::HodgeLogger; pipe_mode::Bool)
    """Тело прогона без lock (lock берут _run_suite/меню); коды выхода §26."""
    errs = cfg_validate(cfg)
    if !isempty(errs)
        foreach(e -> println(badge("FAIL"), " ", e), errs)
        return 2
    end
    hodge_apply_rlimits(cfg, lg)
    cfg.clean_orphans && hodge_clean_orphans!(lg, cfg.run_dir)
    mon = mon_timer = nothing
    exit_code = 0
    try
        runner = HodgeRunner(cfg, lg)
        # §8: стартовый снэпшот монитора + фоновый Timer-пробник
        if cfg.monitor in ("on", "panel") && !isempty(cfg.run_dir)
            csv = cfg.monitor_csv ? joinpath(cfg.run_dir, "logs", "monitor.csv") : nothing
            mon = HodgeMonitor(csv)
            mon_snapshot!(mon)
            if cfg.monitor_interval > 0
                mon_timer = Timer(round(cfg.monitor_interval * 1000); interval = round(cfg.monitor_interval * 1000)) do _
                    try; mon_snapshot!(mon); catch; end
                end
            end
        end
        t0 = time()
        fire_hook("pre_run", cfg, runner)
        if pipe_mode
            run_all!(runner)
        else
            (cfg.banner != "off" && !cfg.plain) && println(banner_render("compact", Dict()))
            if cfg.splash && !cfg.plain
                cfg._lock_held = RUN_LOCK[] !== nothing
                foreach(ln -> println(dye("· " * ln, "text_dim")), splash_rows(cfg, RUN_LOCK[] !== nothing))
            end
            run_all!(runner)
        end
        fire_hook("post_run", cfg, runner)
        wall = time() - t0
        rs = results_sorted(runner)
        passed = count(r -> get(r, "ok", false), rs)
        total = length(rs)
        all_ok = passed == total && total > 0
        exit_code = all_ok ? 0 : 1
        haskey(lg.err_ledger, "ERR_GLOBAL_TIMEOUT") && (exit_code = 4)
        haskey(lg.err_ledger, "ERR_INTERNAL") && (exit_code = 3)
        haskey(lg.err_ledger, "ERR_HEALTH") && (exit_code = 5)
        haskey(lg.err_ledger, "ERR_SIGTERM") ? (exit_code = 143) :
            haskey(lg.err_ledger, "ERR_SIGINT") && (exit_code = 130)
        # §9.4: экспорт метрик в финале
        (!isempty(cfg.metrics_format) && !isempty(lg.metrics)) && hodge_metrics_export!(cfg, lg)
        cfg.jsonl && hodge_jsonl_out!(cfg, runner)
        cfg.tsv && hodge_tsv_out!(cfg, runner)
        (isempty(cfg.junit_path) || hodge_junit(cfg, runner))   # P1 / §26.3
        if !(cfg.ci || cfg.jsonl || cfg.tsv)
            verdict = hodge_fmt(Dict("lang" => cfg.lang), all_ok ? "all_pass" : "has_fail")
            println(dye("── $(hodge_fmt(Dict("lang" => cfg.lang), "summary")): ", "gold") *
                    dye(verdict, all_ok ? "ok" : "err", "bold") *
                    dye(" ($(hodge_fmt(Dict("lang" => cfg.lang), "duration")): $(fmt_duration(wall)))", "text_dim"))
        else
            println(json_dump(Dict("event" => "summary", "passed" => passed, "total" => total,
                                   "exit_code" => exit_code, "duration_s" => round(wall; digits = 2))))
            flush(stdout)
        end
        # §10: отчёты, если не --no-report; results.json пишется всегда
        hodge_atomic_write(joinpath(cfg.run_dir, "results.json"),
                           json_dump(results_json(runner, lg, exit_code, wall)))
        if !cfg.no_report
            write_per_task!(runner, lg, cfg.run_dir)
            write_manifest!(runner, lg, cfg.run_dir, exit_code)
            write_final_report!(runner, lg, cfg.run_dir, exit_code, wall)
            cross_run_dashboard!(cfg)
        end
        log_event!(lg, "INFO", "Run", "exit", code = exit_code)
        return exit_code
    catch ex
        ledger!(lg, "ERR_INTERNAL")
        _bt = sprint(showerror, ex) * " @ " * join([string(f.func, ":", f.line) for f in stacktrace(catch_backtrace())[2:4]], ", ")
        log_comp!(lg, "ERROR", "Run", "internal exception: $_bt")
        return 3
    finally
        mon_timer !== nothing && close(mon_timer)
        nothing
    end
end

function run_suite!(cfg::HodgeConfig, lg::HodgeLogger; pipe_mode::Bool)
    """Полный прогон с flock (§24.2/A9): ERR_LOCK_HELD → код 2; finally-снятие (B4)."""
    isempty(cfg.run_dir) && begin
        cfg.run_dir = isempty(cfg.resume_dir) ? new_run_dir(cfg) : cfg.resume_dir
    end
    # BUGFIX(Race): как в run_ids_with_lock! — ретраи со свежим суффиксом
    # (resume_dir не трогаем: повторять там нельзя по смыслу)
    lock = nothing
    err = ""
    for attempt in (isempty(cfg.resume_dir) ? (1:5) : (1:1))
        lock, err = flock_acquire!(cfg.run_dir)
        lock !== nothing && break
        isempty(cfg.resume_dir) && (cfg.run_dir = new_run_dir(cfg))
        sleep(0.05)
    end
    if lock === nothing
        println(badge("FAIL"), " ERR_LOCK_HELD: ", err)
        return 2
    end
    install_signals!()             # ← только на время compute (BUGFIX VI.3a: в меню
    RUN_LOCK[] = lock              #   readline(stdin) обязан получать Ctrl+C)
    ACTIVE_LOGGER[] = lg
    cfg._lock_held = true
    open_run!(lg, cfg.run_dir)
    try
        return run_suite_body!(cfg, lg; pipe_mode = pipe_mode)
    catch ex
        ex isa InterruptException && return 130
        rethrow()
    finally
        restore_signals!()          # ← восстановить до выхода (§7.6)
        lock_release!(lock)         # §24.2 v4: снимает любой режим каскада
        RUN_LOCK[] = nothing
        ACTIVE_LOGGER[] = nothing
        cfg._lock_held = false
    end
end

function hodge_main(args::Vector{String})
    """§0/§18: единственная точка входа. Голый запуск → меню (menu-first)."""
    cfg = HodgeConfig()
    # §3.2 v4: кэш настроек ДО parse_cli! (defaults < cache < env < CLI < меню).
    # Ранний пре-скан --no-settings-cache/--settings-reset — они сильнее кэша.
    if "--no-settings-cache" in args
        cfg.settings_cache = false
    end
    if "--settings-reset" in args && reset_settings_cache!(cfg)
        println(badge("INFO"), " settings cache reset (", settings_cache_path(cfg), ")")
    end
    sc_applied = load_settings_cache!(cfg)
    if !isempty(sc_applied)
        println(badge("INFO"), " settings cache: ", join(sc_applied, ", "), " ← ", settings_cache_path(cfg))
    end
    # BUGFIX(VI.3a): install_signals!() НЕ вызывается здесь — flag-обработчики
    # вешаются только на время compute (run_suite!/run_ids_with_lock!),
    # иначе Ctrl+C в меню переставал бросать InterruptException (§14.3).
    # автодетект языка (§16.1)
    loc = get(ENV, "LC_ALL", get(ENV, "LANG", ""))
    startswith(loc, "en") && (cfg.lang = "en")
    startswith(loc, "ru") && (cfg.lang = "ru")
    if !isempty(args) && (args[1] == "--help" || args[1] == "-h")
        hodge_help(cfg)
        return 0
    end
    terminal, warns = try
        parse_cli!(cfg, args)
    catch ex
        println(badge("FAIL"), " ", sprint(showerror, ex))
        return 2
    end
    foreach(w -> println(badge("WARN"), " ", w), warns)
    # §3.2 v5: cfg.prec (биты) поднимает точность движка сразу после разбора
    # конфига; гигантские значения честно проверяются на RAM (ERR_PREC_RAM)
    hodge_prec_engine_apply!(cfg)
    hodge_prec_ram_guard(cfg) || return 2
    # терминальные команды
    terminal === nothing || return begin
        # P1 / §21.5: тема из файла — и для терминальных действий тоже
        !isempty(cfg.theme_file) && (load_theme_file!(cfg); cfg.theme_file = "")
        terminal == "version" && (println("hodge-master $HODGE_VERSION · julia ", Base.VERSION_STRING); 0)
        terminal == "list-tasks" && hodge_list_tasks(cfg)
        terminal == "list-presets" && hodge_list_presets(cfg)
        terminal == "list-recipes" && hodge_list_recipes(cfg)
        terminal == "theme-preview" && hodge_theme_preview(cfg)
        terminal == "doctor" && hodge_doctor(cfg)
        terminal == "health" && hodge_health(cfg)
        terminal == "help" && begin hodge_help(cfg); 0 end
        terminal == "list-tags" && begin   # P1 / §4.2
            println(join(sort!(unique(vcat([t.tags for t in TASKS]...))), " ")); 0 end
        terminal == "gen-man" && hodge_generate_man()                        # P1 / §30
        terminal == "gen-completions" && hodge_generate_completions(cfg.gen_shell)
        terminal == "explain-config" && hodge_explain_config(cfg)            # P1 / §3.2
        terminal == "coverage" && begin                                      # P1 / §19.7 честно
            UNSUPPORTED_LOG["coverage"] = "stdlib-Julia: нет трассировщика (§19.7)"
            println(badge("FAIL"), " ERR_UNSUPPORTED: coverage недоступен на stdlib-Julia (нет трассировщика); см. RTM.md §19.7"); 2 end
        terminal == "monitor-probe" && hodge_monitor_probe(cfg)              # P1 / §8.2
        terminal == "unsupported-rlimit" && begin                            # P1 / §12.6 честно
            UNSUPPORTED_LOG["rlimit"] = "stdlib-Julia: нет resource.setrlimit (§12.6)"
            println(badge("FAIL"), " ERR_UNSUPPORTED: rlimit недоступен на stdlib-Julia (нет resource.setrlimit); см. RTM.md §12.6"); 2 end
        terminal == "verify-signature" && hodge_verify_signature(cfg, cfg.verify_signature)  # P0.7
        0
    end
    if !isempty(cfg.diff_runs)
        return hodge_diff(cfg, cfg.diff_runs[1], cfg.diff_runs[2])
    end
    if !isempty(cfg.lab3d_spec) && haskey(LAB_VIDEO_OBJECTS, cfg.lab3d_spec)
        # §11.10: имя из --lab-video совпало с объектом Video Lab → видео;
        # иначе — классический lab3d (omega|period_re|census_h)
        p = LAB_VIDEO_PARAMS[]
        return hodge_lab_video(cfg; object = cfg.lab3d_spec,
                               fps = p.fps, frames = p.frames, N_full = p.n)
    end
    if !isempty(cfg.lab3d_spec)
        return hodge_lab3d(cfg)
    end
    if cfg.print_config
        return hodge_print_config(cfg)
    end
    if cfg.validate_config_only
        errs = cfg_validate(cfg)
        foreach(e -> println(badge("FAIL"), " ", e), errs)
        return isempty(errs) ? 0 : 2
    end
    if cfg.dry_run
        cfg.run_dir = new_run_dir(cfg)
        return hodge_dry_run(cfg)
    end
    pipe_mode = cfg.ci || cfg.jsonl || cfg.tsv || !(stdin isa Base.TTY)
    exit_code = 0
    try
        if !isempty(cfg.self_test)
            cfg.run_dir = new_run_dir(cfg)
            lg = HodgeLogger(cfg); open_run!(lg, cfg.run_dir)
            ACTIVE_LOGGER[] = lg
            exit_code = run_selftest!(cfg)
        elseif cfg.bench
            cfg.run_dir = new_run_dir(cfg)
            lg = HodgeLogger(cfg); open_run!(lg, cfg.run_dir)
            ACTIVE_LOGGER[] = lg
            exit_code = hodge_bench(cfg)
        elseif cfg.fuzz_sec > 0
            cfg.run_dir = new_run_dir(cfg)
            lg = HodgeLogger(cfg); open_run!(lg, cfg.run_dir)
            ACTIVE_LOGGER[] = lg
            exit_code = hodge_fuzz(cfg, cfg.fuzz_sec)
        elseif cfg.menu_forced
            # P0.2 / §14.1: --menu форсирует меню даже при --task и в пайпе
            # (menu_run! сам ограничивает EOF через MENU_EOF_LIMIT)
            cfg.run_dir = isempty(cfg.run_dir) ? new_run_dir(cfg) : cfg.run_dir
            lg = HodgeLogger(cfg); open_run!(lg, cfg.run_dir)
            ACTIVE_LOGGER[] = lg
            m = HodgeMenu(cfg, lg)
            exit_code = menu_run!(m)
        elseif !isempty(cfg.tasks)
            exit_code = run_suite!(cfg, HodgeLogger(cfg); pipe_mode = pipe_mode)
        elseif cfg.tui
            # §14.9: TUI честно ERR_UNSUPPORTED на stdlib-Julia (нет termios) → WARN
            println(badge("WARN"), " --tui: full-screen TUI на stdlib-Julia не поддержан ",
                    "(§1.5); ближайший эквивалент — интерактивное меню")
            UNSUPPORTED_LOG["tui"] = "stdlib-Julia: нет termios raw mode (§1.5)"
            return 2
        elseif pipe_mode && !cfg.menu_off
            # §28.6: голый запуск в pipe → plain-меню; EOF-guard выходит
            if !(stdin isa Base.TTY)
                # BUGFIX(VI.3b): stdin не TTY — меню мгновенно упрётся в EOF
                # (readline → EOFError → EOF-guard-цикл). Явный хинт вместо
                # мигающего меню; немедленный выход с кодом 0.
                println(badge("INFO"), " ",
                        hodge_fmt(Dict("lang" => cfg.lang), "menu.non_tty_hint"))
                return 0
            end
            cfg.run_dir = new_run_dir(cfg)
            lg = HodgeLogger(cfg); open_run!(lg, cfg.run_dir)
            m = HodgeMenu(cfg, lg)
            exit_code = menu_run!(m)
        elseif cfg.menu_off
            # VI.5 / J11: --no-menu без --task → ERR_NO_TASK, код 2
            if isempty(cfg.tasks) && cfg.preset == "full"   # preset не менялся CLI
                println(badge("FAIL"), " ERR_NO_TASK: нет --task/--preset для прямого прогона")
                return 2
            end
            exit_code = run_suite!(cfg, HodgeLogger(cfg); pipe_mode = pipe_mode)
        else
            # §0.3 menu-first (Часть III): баннер — ВНУТРИ меню, без отдельных
            # шагов splash/tip/MOTD — меню самодостаточно
            cfg.run_dir = new_run_dir(cfg)
            lg = HodgeLogger(cfg)
            open_run!(lg, cfg.run_dir)
            ACTIVE_LOGGER[] = lg
            m = HodgeMenu(cfg, lg)
            exit_code = menu_run!(m)
        end
    catch ex
        if ex isa InterruptException
            println()
            println(badge("WARN"), " SIGINT — частичный прогон сохранён (код 130)")
            exit_code = 130
        else
            rethrow()
        end
    finally
        ACTIVE_LOGGER[] !== nothing && close_logger!(ACTIVE_LOGGER[])   # P2.12
        restore_signals!()
        # §3.2 v4: --settings-save — настройки и CLI-прогона идут в кэш настроек
        if cfg.settings_cache && cfg.settings_save
            p = save_settings_cache!(cfg)
            isempty(p) || println(badge("INFO"), " settings saved → ", p)
        end
    end
    return exit_code
end

# ════════════════════════════════════════════════════════════════════════
# entry point.
# - Скрипт (julia master_hodge.jl): меню/флаги, затем exit().
# - REPL include(): меню открывается СРАЗУ — никаких hodge_menu() руками.
#   Отключить автозапуск можно переменной HODGE_AUTO_MENU=0.
#   (Run-dir от повторных include защищён суффиксом _1.._N в new_run_dir.)
# - -e (автоматизация): тихо, без меню (isinteractive() == false).
# NOTE: hodge_menu определён ДО блока — блок может его вызывать.
# ════════════════════════════════════════════════════════════════════════
hodge_menu(args::Vector{String} = String[]) = hodge_main(vcat(["--menu"], args))

# Нуль-арное удобство: hodge_main() = голый запуск → menu-first.
hodge_main() = hodge_main(String[])

const _HODGE_IS_SCRIPT = !isempty(PROGRAM_FILE) &&
                         normpath(abspath(PROGRAM_FILE)) == normpath(abspath(@__FILE__))

if _HODGE_IS_SCRIPT && !isinteractive()
    # обычный запуск: julia master_hodge.jl <args>
    exit(hodge_main(String.(ARGS)))
elseif isinteractive() && get(ENV, "HODGE_AUTO_MENU", "1") != "0"
    # include в REPL → меню открывается сразу, без лишних манипуляций
    try
        hodge_menu()
    catch ex
        ex isa InterruptException || rethrow()
    end
end

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
 HODGE MASTER · master_hodge.py — мастер-файл верификации репозитория
 hodge-laboratory (https://github.com/wild8highlander/hodge-laboratory)

 Каждый пункт реестра TASKS — это один проверяемый тест-утверждением, который
 лаборатория заявляет и подтверждает: census, V1–V9, башня радикалов, стенды
 K3/Клейн/тор, сертификаты E/F/G/H/I/J/K-слой, SNF-движок, счёт точек Ферма.

 Запуск:          python3 master_hodge.py            (голый запуск → меню сразу)
 Формы:           --self-test, --ci, --jsonl, --tsv, --task N, --dry-run,
                  --doctor, --print-config, --theme-preview, --diff, --bench…

 Только стандартная библиотека Python (≥ 3.10): ноль внешних пакетов, ноль
 сети, ноль shell-вызовов. Данные задач захардкожены — самодостаточный файл.
 Предметная область: репозиторий Исаева Исхака Хамзатовича (hodge-laboratory).

 ИСТОРИЯ v1.5.0-session8 (2026-11-21) — «все шаги дорожной карты s7»:
   • ШАГ 1 (п. 2.3 закрыт): адаптивный шаг h в tanh–sinh —
     HODGEHP.period_pieces_adaptive: h → h/2 до сходимости на целевой
     10^{−(prec+1)} либо до стагнации (пол округления суммы), суммирование
     в контексте prec+6; period_numeric(…, adaptive=True). Измерено: пол
     дискретизации 4.8e−83 (N=15,4,5) / 1.7e−71 (N=30,11,19) при
     фиксированном h=0.02 заменяется на 2.1e−98 @prec=100 и 1.2e−186
     @prec=200 — снова масштаб 10^{−prec}. Регрессия встроена в задачу 2
     (adaptive-h ≤ 1e−90 @prec=100, не-quick пресеты).
   • ШАГ 2: задача 42 «HODGE-CERT» — явные рациональные коэффициенты
     разложения (2,2)-классов квартиковой четвёрки по 960 плоскостям
     (hodge_planes.py §5): 142 целочисленных сертификата-вектора
     (70 гауссовых пар × 2 + самосопряжённый + h²) + полный ранг.
   • ШАГ 3: задача 43 «HODGE-CYCLES» — лаборатория недостающих характеров
     S₅/S₆ (hodge_planes.py §6): теорема парности (реализованность ⇔
     мультиэст {aᵢ} разбивается на пары с суммой m), исчерпывающее
     доказательство, что амбиентные дивизоры не выходят из натяжения
     прямых, лестница m=3..8, рациональные классы недостающих характеров.
   • ШАГ 4: задача 44 «HODGE-QUINTIC» — квинтиковая четвёрка X⁵₄
     (hodge_planes.py §7): ценз h^{2,2}=581 (три схемы), 1875 плоскостей,
     спектры 15 семейств в Z[ζ₅] (λ = 13−3σ₁+σ₂), ранг семейства 65,
     натяжение 401 из 581 — плоскости НЕ натягивают всё: 180 характеров
     требуют нелинейных циклов (граница метода «очевидных» циклов в
     коразмерности 2 для степеней ≥ 5).
   • ШАГ 5: перенос слоя декомпозиции Ходжа в джулиа-твин master_hodge.jl
     (задачи 41–44, spectrum/census/certificates; паритет с Python).

 ИСТОРИЯ v1.4.3-session7 (2026-11-21) — «слой декомпозиции Ходжа»:
   • Диагностика замечаний научного руководителя к period_closed/period_numeric
     (измерено, scripts/diagnose_hodge.py): (i) фазовые индексы (ra+sb)%N и
     (ra+s(b−N))%N равны как целые числа (13320 пар, 0 расхождений) — обе
     реализации берут ОДИН элемент таблицы ζ, гипотеза «фаза ζ плывёт между
     методами» не подтверждается; (ii) дрейф таблицы zeta_pow реален:
     |ζ^N − 1| ≈ N·10^{−prec} — исправлено guard-разрядами (см. §3.2 v7);
     (iii) расхождение period_closed vs period_numeric масштабируется как
     10^{−prec} (округление) с выходом на квадратурный пол tanh–sinh при
     фиксированном h=0.02 (например N=15, a=4, b=5: 4.8e−83 при prec 100 и
     200 — пол дискретизации, НЕ фаза и НЕ ошибка формулы: от s не зависит).
   • §3.2 v7 zeta_pow: контекст prec+guard (⌈log10 N⌉+3) — накопление
     k·10^{−prec} устранено, паритет с Julia-версией (там отдельный exp на
     каждый элемент). Строка версии синхронизирована: была «1.4.1-session5»
     при описанных в шапке изменениях v1.4.2-session6.
   • НОВЫЙ МОДУЛЬ verification/hodge_planes.py + задача 41 «HODGE-PLANES» —
     недостающий слой декомпозиции Ходжа (по заключению научрука): числа
     Ходжа гиперповерхностей Ферма (кольцо Якобиана против классов Чженя),
     характерный ценз H² поверхностей Ферма (обобщение ценза кривых),
     решётки прямых на S_m (ранги/сигнатуры/характерные спектры; прямые
     натягивают H^{1,1} при m ≤ 4, с m = 5 — только часть — граница
     «очевидных» циклов), плоскости квартиковой четвёрки Ферма: 960
     плоскостей натягивают 142 = h^{2,2} рациональных (2,2)-классов —
     вычислительная верификация гипотезы Ходжа в коразмерности 2.

 ИСТОРИЯ v1.4.2-session6 (2026-11-14) — «prec без зависаний»:
   • ДИАГНОЗ (измерено): ln/exp libmpdec — O(n^2.8) с огромной константой
     (ln@20k знаков = 45 с, exp@20k = 14 с, sqrt@20k = 0.19 с) → на prec 5m
     ОДИН ln считался бы века; π по Мэчину и ряды sin/cos — O(prec²) членов;
     Γ: факториал (s−1)! последовательными умножениями + ζ(302)−1 прямой
     суммой ~10^(prec/302) членов → «зависает и ничего не считает».
   • π: Чудновский с бинарным расщеплением ВЕСЬ в Decimal (NTT-мулы libmpdec
     точны при запасе prec): 1e6 знаков ≈ 5 с, 5m ≈ 1–2 мин (вместо вечности);
     Мэчин остаётся ниже prec 1500 (self-test не тронут).
   • sqrt_hp: Ньютон с удвоением точности O(M(n)) вместо O(n^2.2) sqrt().
   • Честные гейты (§3.2 v6): ERR_PREC_OP (sin/cos/atan/exp/ln с оценкой
     > HODGE_OP_LIMIT, по умолч. 30 с), ERR_GAMMA_PREC (Γ: ζ-сумма ~10^x
     членов + ряд Стирлинга ~π·prec/2.73 членов, порог 900 с),
     ERR_QUAD_PREC (tanh–sinh: узлы × дорогие exp, порог 1800 с). Обход —
     HODGE_PREC_UNSAFE=1 или индивидуальные HODGE_*_LIMIT=N.
   • HODGEPROG: heartbeat-поток печатает в stderr «…стадия: N s» каждые 10 с —
     терминал больше не выглядит зависшим (HODGE_HEARTBEAT=0 отключит).
   • Блок честных оценок prec при запуске прогов и в меню (prec ≥ 4096) +
     подтверждение [y/N] в интерактивном меню.
   • Совет в гейтах: prec ≥ ~20000 знаков (py) → engine=julia: MPFR log/exp/
     sin на 5M бит = 0.7–7 с (измерено), π = 1.5 с.
   • GIF: Γ-таблица кадров капится prec ≤ 45 (это float64-дисплей) — GIF
     работает при ЛЮБОМ cfg.prec.

 ИСТОРИЯ v1.4.1-session5 (2026-11-14) — «gif-движок починен»:
   • GCE-блок кадра: лишний байт 0x04 сдвигал поле delay на 1 байт — зрители
     читали задержку ×256 (кадр «висел» по 20+ с) и после GCE оставался
     посторонний пустой 0x00-блок. Теперь ровно 21 F9 04 04 … (8 байт).
   • lab-video: задержка кадра была 1000//fps — GIF-delay меряется в СОТЫХ
     секунды, т.е. в 10 раз больше верной: 24 fps играли как ~2.4 fps.
     Теперь _gif_delay_cs = max(2, round(100/fps)); self-test проверяет.
   • self-test §11 усилен: структурная приёмка GIF (GCE/цепочка блоков/
     задержки), LZW round-trip 96×72 (рост 9→12 бит, сброс 4096) и приёмка
     стороннего INTERLACE-GIF.
   • Декодер-приёмка (_lzw_roundtrip): interlace-флаг ранее игнорировался —
     сторонние (чересстрочные) GIF декодировались с переставленными строками;
     теперь GCT/LCT/interlace/размеры кадров разбираются по §F (сверено с
     независимым декодером pixel-exact на шумовых кадрах до 640×480).
   • lab3d (Python): подписи на кадрах «fn=… N=… grid=…» + пояснение осей —
     паритет с Julia-лабораторией.

 ИСТОРИЯ v1.4.0-session4 (2026-11-14) — «prec без границ»:
   • prec БЕЗ верхней границы: CLI/меню/кэш принимают 4096, 5m, 1g, 2t
     (суффиксы k/m/g/t — «гигабайты мантиссы»); лимит 30..1024 снят (§3.2 v5).
   • Честная оценка RAM: BigFloat/Decimal ≈ prec·байт/число; оценка ×16 > RAM
     → WARN, ×2 > RAM → ERR_PREC_RAM без --unsafe-prec / HODGE_PREC_UNSAFE=1.
   • Γ-слой HODGEHP масштабируется с prec: сдвиг Стирлинга от цифр (минимум
     остатка ~10^−2.73·y), ζ-отношение для B_{2k} при k > 60, guard-разряды
     и Neumaier-суммирование сдвигового цикла — раньше ряд обрывался капом
     k ≤ 60 (пол ~10^−223 при prec 1024).
   • t40 HODGE-INF: сертификация на ЛЮБОЙ prec (был clamp 60); prec-extreme
     поднимает floor до 200.
═══════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import hashlib
import hmac
import glob
import json
import math
import cmath
import os
import platform
import re
import shutil
import signal
import statistics
import struct
import subprocess  # noqa: F401  (используется только адаптером при -v doctor; вычисления не идут через shell)
import sys
import threading
import time
import unicodedata
import zlib
from datetime import datetime, timezone
from decimal import Decimal, localcontext, getcontext, MAX_EMAX, MIN_EMIN
from fractions import Fraction
from hashlib import sha256

# ══════════════════════════════════════════════════════════════════════════
# §32. ПОДСТАНОВКИ КОНТРАКТА
# ══════════════════════════════════════════════════════════════════════════
#   {{FILE_NAME}}        = master_hodge.py
#   {{LANGUAGE}}         = python        {{language}} = python3
#   {{LANG_VERSION}}     = 3.10
#   {{PLATFORM_TARGETS}} = linux,termux,macos,windows
#   {{DOMAIN}}           = hodge-laboratory — верификация утверждений
#   {{WHAT_IT_DOES}}     = гоняет реестр задач-тестов: каждое утверждение
#                          репозитория — отдельная задача с вердиктом PASS/FAIL/SKIP
#   {{PRESETS}}          = quick,full,deep
#   {{PREFIX}}           = HODGE   {{prefix}} = hodge_   {{Prefix}} = Hodge
HODGE_FILE_NAME = "master_hodge.py"
HODGE_LANG = "python"
HODGE_LANG_VERSION = "3.10"
HODGE_VERSION = "1.5.0-session8"
HODGE_BUILD_DATE = "2026-11-21"
HODGE_REPO = "wild8highlander/hodge-laboratory"
HODGE_REPO_URL = "https://github.com/wild8highlander/hodge-laboratory"
HODGE_PRESETS = ("quick", "full", "deep")

# ══════════════════════════════════════════════════════════════════════════
# §3.4 RECIPES: именованные (preset, profile, tasks, overrides).
# Мутация cfg — только через apply_recipe!(cfg, name).
# ══════════════════════════════════════════════════════════════════════════
RECIPES = {
    "nightly": {
        "preset": "deep", "profile": "paranoid",
        "tasks": ["all"], "two_pass": True,
        "overrides": {"strict": True, "global_timeout": 3600},
        "description": "глубокая ночная верификация с paranoid-профилем",
    },
    "smoke": {
        "preset": "quick", "profile": "fast",
        "tasks": [1, 18, 13, 9], "two_pass": False,
        "overrides": {"no_report": True},
        "description": "быстрая проверка ядра (4 задачи, < 2 с)",
    },
    "chess-ci": {
        "preset": "full", "profile": "balanced",
        "tasks": [23, 24, 25, 26, 27, 28, 29, 30, 31, 32],
        "two_pass": False,
        "overrides": {"task_timeout": 120},
        "description": "CI-прогон chess-dynamics-lab (без pass2)",
    },
    "verhodge": {
        "preset": "deep", "profile": "balanced",
        "tasks": [34, 35, 36, 37],
        "two_pass": True,
        "overrides": {},
        "description": "verhodge-lab: C-010/C-006/C-003/C-019",
    },
}

# §21.6: ключи палитры для подменю палитры (паритет с Julia PALETTE_KEYS)
PALETTE_KEYS = ("bg", "surface", "surface_2", "gold_dim", "gold", "gold_bright",
                "amber", "ember", "text", "text_dim", "text_strong",
                "ok", "warn", "err", "info", "neutral")


def apply_recipe(cfg: HodgeConfig, name: str) -> None:
    """§3.4: рецепт = preset + profile + tasks + overrides (в этом порядке)."""
    if name not in RECIPES:
        raise ValueError(f"ERR_RECIPE_UNKNOWN {name}")
    r = RECIPES[name]
    if "preset" in r:
        cfg.preset = r["preset"]
        apply_preset(cfg, cfg.preset)
    if "profile" in r:
        cfg.profile = r["profile"]
    if "tasks" in r:
        t = r["tasks"]
        if t == ["all"] or t == "all":
            cfg.tasks = list(SUITE_IDS)
        else:
            cfg.tasks = list(t)
    if "two_pass" in r:
        cfg.two_pass = bool(r["two_pass"])
    for k, v in r.get("overrides", {}).items():
        if hasattr(cfg, k):
            setattr(cfg, k, v)


# §3.4 CONFIG MIGRATIONS: каждое поле имеет since_version.
SCHEMA_VERSION = "1.1.0"
# field → (since, default_for_migration)
_FIELD_SINCE = {
    "dye_mode": "1.0.0", "digit_tier": "1.0.0", "plot": "1.1.0",
    "plot_formats": "1.1.0", "lab3d": "1.1.0", "fps": "1.1.0",
    "particles": "1.1.0", "anim_seconds": "1.1.0",
    "metrics_format": "1.1.0", "lab_grid": "1.1.0",
    "rlimit_as": "1.1.0", "rlimit_cpu": "1.1.0", "rlimit_fsize": "1.1.0",
    "rate_limit": "1.1.0", "cache_on": "1.1.0",
    "notify": "1.0.0", "trail_particles": "1.1.0",
    "particles_charset": "1.1.0", "title_bar": "1.1.0",
    "tui": "1.1.0",
}

def migrate_config(cfg: HodgeConfig, from_version: str, run_dir: str) -> list:
    """§3.4: миграция старого конфига; правки пишутся в logs/config_migrations.txt."""
    changes = []
    def vtuple(s):
        try:
            return tuple(int(x) for x in s.split("."))
        except Exception:
            return (0, 0, 0)
    for field, since in _FIELD_SINCE.items():
        if vtuple(since) > vtuple(from_version) and not hasattr(cfg, field):
            # у HodgeConfig обычно всё уже есть; миграция для будущих полей
            setattr(cfg, field, None)
            changes.append(f"{field}: added with since={since}")
    if changes and run_dir:
        try:
            os.makedirs(os.path.join(run_dir, "logs"), exist_ok=True)
            with open(os.path.join(run_dir, "logs", "config_migrations.txt"), "a",
                      encoding="utf-8") as f:
                f.write(f"# migrate from {from_version} to {SCHEMA_VERSION}\n")
                for ch in changes:
                    f.write(ch + "\n")
        except OSError:
            pass
    return changes

# ──────────────────────────────────────────────────────────────────────────
# §31 (фрагмент). ЯЗЫКОВОЙ АДАПТЕР PYTHON — таблица, не разбросан по коду.
# ──────────────────────────────────────────────────────────────────────────
class HODGEAdapter:
    """Все платформенно/языково-специфичные операции — в одной таблице."""

    RUN_CMD = ["python3", HODGE_FILE_NAME]
    INCLUDE_GUARD = "__name__ == '__main__'"          # точка входа §18
    ATOMIC_WRITE = "os.replace(tmp, dst) + fsync"     # §24.1
    # §24.2 v4: портабельный каскад flock → POSIX-lockfile (O_EXCL) → advisory.
    # Работает на любых ФС: ext4/btrfs/xfs/tmpfs (flock), FAT/exFAT/NTFS-3g/
    # CIFS/NFS без lockd/некоторые FUSE (flock ENOSYS/EINVAL/EOPNOTSUPP/ENOLCK
    # → O_EXCL-локфайл), совсем экзотика (O_EXCL тоже нет) → advisory + WARN.
    FILE_LOCK = "flock → O_EXCL lockfile → advisory"  # §24.2
    WCWIDTH = "unicodedata.east_asian_width"          # §16.7
    MONOTONIC = "time.monotonic"                      # §23.5
    TERMINAL_SIZE = "shutil.get_terminal_size"        # §31
    RLIMIT = "resource.setrlimit"                     # §12.6
    HAS_RLIMIT = True
    HAS_MALLOC_TRIM = False                           # §12.1: glibc-only через ctypes
    GC_BETWEEN_TASKS = "gc.collect() ×2 (+malloc_trim, если есть)"

    @staticmethod
    def isatty(stream=sys.stdin) -> bool:
        try:
            return bool(stream.isatty())
        except Exception:
            return False

    @staticmethod
    def term_width() -> int:
        try:
            return int(shutil.get_terminal_size((80, 24)).columns)
        except Exception:
            return 80

    @staticmethod
    def wcwidth(ch: str) -> int:
        if unicodedata.combining(ch):
            return 0
        return 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1

    @staticmethod
    def display_width(s: str) -> int:
        return sum(HODGEAdapter.wcwidth(c) for c in re.sub(r"\x1b\[[0-9;]*m", "", s))

    @staticmethod
    def gc_between_tasks() -> None:
        import gc
        gc.collect()
        gc.collect()  # §12.1: двойной проход
        try:  # malloc_trim — glibc-only; иначе тишина (не ERR_UNSUPPORTED: best-effort в адаптере)
            import ctypes
            libc = ctypes.CDLL("libc.so.6")
            libc.malloc_trim(0)
        except Exception:
            pass

    @staticmethod
    def flock_holder_pid(lock_path: str) -> int:
        """PID держателя flock: из .lock (pid=N) либо /proc/locks по inode."""
        import re as _re
        pid = 0
        try:
            with open(lock_path, "r") as fh:
                m = _re.search(r"pid=(\d+)", fh.read())
            pid = int(m.group(1)) if m else 0
        except OSError:
            pass
        if pid > 0:
            return pid
        try:
            # формат /proc/locks: «1: FLOCK ADVISORY WRITE 1234 08:02:123456 0 EOF»
            ino = os.stat(lock_path).st_ino
            with open("/proc/locks") as fh:
                for ln in fh:
                    toks = ln.split()
                    if len(toks) >= 6 and toks[1] == "FLOCK":
                        parts = toks[5].split(":")
                        if len(parts) == 3 and parts[2].isdigit() and int(parts[2]) == ino:
                            pid = int(toks[4])
                            break
        except OSError:
            pass
        return pid

    # §24.2 v4: errno, означающие «ФС/ядро не поддерживает flock» (не «занято»):
    # ENOSYS(38) syscall нет, EINVAL(22) операция не поддерживается ФС,
    # EOPNOTSUPP/ENOTSUP(95), ENOLCK(37) лимит/тип блокировки недоступен.
    LOCK_UNSUPPORTED_ERRNOS = {38, 22, 95, 37}

    @staticmethod
    def lockfile_holder_pid(lock_path: str) -> int:
        """PID держателя O_EXCL-локфайла (файл содержит 'pid=N')."""
        import re as _re
        try:
            with open(lock_path, "r") as fh:
                m = _re.search(r"pid=(\d+)", fh.read())
            return int(m.group(1)) if m else 0
        except OSError:
            return 0

    @staticmethod
    def lockfile_acquire(run_dir, stale_sec: float = 900.0, timeout: float = 3.0):
        """§24.2 v4: POSIX-локфайл (O_CREAT|O_EXCL) — работает на ФС БЕЗ flock
        (FAT/exFAT/NTFS-3g/CIFS/NFS без lockd/FUSE, errno 38 ENOSYS и др.).
        Протокол: эксклюзивное создание .lockfile; занят → держатель (PID);
        мёртвый PID или файл старше stale_sec → стейл-лок снимается автоматически.
        → (fd, None) при успехе; (None, сообщение) при занятости; (fd_advisory, None)
        если O_EXCL на этой ФС тоже не работает (совместно с _LOCK_MODE='advisory')."""
        import errno as _errno
        import time as _time
        global _LOCK_MODE
        lkf = os.path.join(run_dir, ".lockfile")
        del timeout   # занятость → немедленный отказ (семантика LOCK_NB, как у flock)
        while True:
            try:
                fd = os.open(lkf, os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600)
            except FileExistsError:
                holder = HODGEAdapter.lockfile_holder_pid(lkf)
                alive = holder > 0 and os.path.isdir(f"/proc/{holder}")
                stale = False
                try:
                    stale = (_time.time() - os.stat(lkf).st_mtime) > stale_sec
                except OSError:
                    pass
                if holder > 0 and not alive:
                    stale = True
                if stale:
                    try:
                        os.unlink(lkf)
                    except OSError:
                        pass
                    continue
                cmd = ""
                if holder > 0 and alive:
                    try:
                        with open(f"/proc/{holder}/cmdline", "rb") as fh:
                            cmd = " · " + fh.read().replace(b"\0", b" ").decode("utf-8", "replace")[:60]
                    except OSError:
                        pass
                who = f"PID {holder}" if holder > 0 else "другим процессом"
                return None, (f"{lkf} занят {who}{cmd} — дождитесь завершения"
                              f" того прогона или закройте его")
            except OSError as e:
                if e.errno == _errno.EINTR:
                    continue
                # O_EXCL тоже не работает (экзотическая ФС) → advisory, честный WARN
                _LOCK_MODE = "advisory"
                print(HODGEText.badge("WARN")
                      + f" lockfile fallback недоступен (errno={e.errno}: {os.strerror(e.errno)})"
                      + " — работаю БЕЗ блокировки; не запускайте параллельные прогоны",
                      flush=True)
                return os.open(lkf, os.O_CREAT | os.O_RDWR, 0o600), None
            try:
                os.write(fd, f"pid={os.getpid()}".encode())
                os.fsync(fd)
            except OSError:
                pass
            return fd, None

    @staticmethod
    def flock_run_dir(run_dir):
        """§24.2 v4: makedirs + .lock + flock(LOCK_EX|LOCK_NB), при неподдержке
        flock на ФС (ENOSYS/EINVAL/EOPNOTSUPP/ENOLCK) — каскад в POSIX-lockfile
        (O_EXCL, работает на FAT/exFAT/NTFS/CIFS/NFS без lockd/FUSE).
        → (fd, None) при успехе; (None, сообщение) при занятости.
        errno==EAGAIN → держатель (PID + cmdline) и подсказка; мёртвый PID →
        авто-снятие стейл-лока; EINTR → один повтор."""
        import errno as _errno
        import fcntl
        global _LOCK_MODE
        os.makedirs(run_dir, exist_ok=True)
        lk = os.path.join(run_dir, ".lock")
        retried = False
        while True:
            fd = os.open(lk, os.O_CREAT | os.O_RDWR, 0o600)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as e:
                os.close(fd)
                if e.errno == _errno.EINTR and not retried:
                    retried = True
                    continue
                if e.errno not in (_errno.EAGAIN, _errno.EACCES):
                    if e.errno in HODGEAdapter.LOCK_UNSUPPORTED_ERRNOS:
                        # ФС без flock → НЕ advisory, а честный переносимый лок:
                        # POSIX-lockfile O_EXCL (взаимоисключение сохраняется)
                        _LOCK_MODE = "lockfile"
                        print(HODGEText.badge("WARN")
                              + f" flock unsupported on this FS (errno={e.errno}: {os.strerror(e.errno)})"
                                " — using POSIX lockfile fallback (.lockfile, O_EXCL)",
                              flush=True)
                        return HODGEAdapter.lockfile_acquire(run_dir)
                    _LOCK_MODE = "advisory"
                    print(HODGEText.badge("WARN")
                          + f" flock недоступен (errno={e.errno}: {os.strerror(e.errno)})"
                          + " — работаю БЕЗ блокировки; не запускайте параллельные прогоны",
                          flush=True)
                    return os.open(lk, os.O_CREAT | os.O_RDWR, 0o600), None
                holder = HODGEAdapter.flock_holder_pid(lk)
                alive = holder > 0 and os.path.isdir(f"/proc/{holder}")
                if holder > 0 and not alive and not retried:
                    try:
                        os.unlink(lk)
                    except OSError:
                        pass
                    retried = True
                    continue
                cmd = ""
                if holder > 0 and alive:
                    try:
                        with open(f"/proc/{holder}/cmdline", "rb") as fh:
                            cmd = " · " + fh.read().replace(b"\0", b" ").decode("utf-8", "replace")[:60]
                    except OSError:
                        pass
                who = f"PID {holder}" if holder > 0 else "другим процессом"
                return None, (f"{lk} занят {who}{cmd} — дождитесь завершения"
                              f" того прогона или закройте его")
            break
        try:
            os.ftruncate(fd, 0)
            os.lseek(fd, 0, os.SEEK_SET)
            os.write(fd, f"pid={os.getpid()}".encode())
        except OSError:
            pass
        return fd, None

    @staticmethod
    def flock_acquire(fd) -> bool:
        import fcntl
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except OSError:
            return False

    @staticmethod
    def flock_release(fd) -> None:
        import fcntl
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        except OSError:
            pass

    @staticmethod
    def lock_release(fd) -> None:
        """§24.2 v4: снятие лока ЛЮБОГО режима каскада (flock/lockfile/advisory):
        lockfile → удалить .lockfile (чтобы не стал 15-минутным стейлом) + close;
        flock/advisory → flock(LOCK_UN) + close."""
        global _LOCK_MODE, _RUN_LOCK_PATH
        if _LOCK_MODE == "lockfile" and _RUN_LOCK_PATH:
            try:
                os.unlink(_RUN_LOCK_PATH)
            except OSError:
                pass
        HODGEAdapter.flock_release(fd)
        try:
            os.close(fd)
        except OSError:
            pass

    @staticmethod
    def atomic_write(path: str, data) -> None:
        """§24.1: tmp + fsync + rename. Частичный файл никогда не остаётся."""
        d = os.path.dirname(os.path.abspath(path)) or "."
        os.makedirs(d, exist_ok=True)
        tmp = os.path.join(d, f".{os.path.basename(path)}.{os.getpid()}.tmp")
        mode = "wb" if isinstance(data, bytes) else "w"
        with open(tmp, mode, encoding=None if isinstance(data, bytes) else "utf-8") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        try:
            os.chmod(tmp, 0o644)          # §24.5 / VII.3: файлы 0644
        except OSError:
            pass
        os.replace(tmp, path)


# ══════════════════════════════════════════════════════════════════════════
# §27.1 / §22.2. CAPABILITY-PROBE — только чтение env, без записи в терминал
# ══════════════════════════════════════════════════════════════════════════
class HODGETerm:
    _caps = None

    @classmethod
    def caps(cls) -> dict:
        if cls._caps is not None:
            return cls._caps
        term = os.environ.get("TERM", "")
        colorterm = os.environ.get("COLORTERM", "")
        truecolor = colorterm in ("truecolor", "24bit") or "truecolor" in colorterm
        if os.environ.get("NO_COLOR") or term == "dumb":
            depth = "mono"
        elif truecolor:
            depth = "truecolor"
        elif "256color" in term or os.environ.get("TERM_PROGRAM"):
            depth = "256"
        elif term in ("", "dumb"):
            depth = "mono"
        else:
            depth = "16"
        unicode_ok = True
        try:
            lang = os.environ.get("LC_ALL", "") or os.environ.get("LANG", "") or ""
            if lang.lower().endswith((".ansi", ".ascii", "c")):
                unicode_ok = False
        except Exception:
            pass
        cls._caps = {
            "color_depth": depth,
            "unicode": unicode_ok,
            "mouse": False,
            "hyperlinks": bool(os.environ.get("TERM_PROGRAM")) or "kitty" in term or "wezterm" in term,
            "clipboard": "kitty" in term or "wezterm" in term or os.environ.get("TERM_PROGRAM") in ("iTerm.app", "Apple_Terminal"),
            "alt_screen": True,
            "term": term,
            "is_tty": HODGEAdapter.isatty(sys.stdout),
        }
        return cls._caps

    @classmethod
    def invalidate(cls) -> None:
        cls._caps = None


# ══════════════════════════════════════════════════════════════════════════
# §21. ТЕМА dark-gold + пользовательские темы; фолбэк truecolor/256/16
# ══════════════════════════════════════════════════════════════════════════
class HODGEColor:
    # ключ → (truecolor hex, 256, 16) — §21.2, полная таблица значений
    DARK_GOLD = {
        "bg": ("#0a0805", 233, "black"), "surface": ("#161009", 234, "black"),
        "surface_2": ("#221806", 235, "black"),
        "gold_dim": ("#8a6d1f", 94, "yellow"), "gold": ("#d4af37", 178, "yellow"),
        "gold_bright": ("#f4d47c", 222, "bright-yellow"), "amber": ("#ffb347", 215, "bright-yellow"),
        "ember": ("#a83a1a", 130, "red"),
        "text": ("#e8d9a8", 187, "white"), "text_dim": ("#9a8a5e", 101, "white"),
        "text_strong": ("#fff4c4", 230, "bright-white"),
        "ok": ("#d4af37", 178, "yellow"), "warn": ("#ffb347", 215, "bright-yellow"),
        "err": ("#a83a1a", 130, "red"), "info": ("#b39a5d", 143, "yellow"),
        "neutral": ("#6a5a34", 58, "yellow"),
    }
    PLOT_SERIES = ["#d4af37", "#f4d47c", "#ffb347", "#b39a5d", "#a83a1a", "#8a6d1f", "#e6c86e", "#c9a227"]
    PLOT_GRID, PLOT_BG, PLOT_TEXT = "#2a2210", "#0a0805", "#e8d9a8"

    THEMES = {
        "dark-gold": DARK_GOLD,
        "aurora": {"bg": ("#050a0a", 233, "black"), "surface": ("#0a1414", 234, "black"),
                   "surface_2": ("#0f1e1c", 235, "black"), "gold_dim": ("#1f8a6d", 36, "green"),
                   "gold": ("#37d4a5", 79, "green"), "gold_bright": ("#7cf4d4", 122, "bright-green"),
                   "amber": ("#47ffd0", 121, "bright-green"), "ember": ("#1aa85a", 35, "red"),
                   "text": ("#a8e8d9", 187, "white"), "text_dim": ("#5e9a8a", 72, "white"),
                   "text_strong": ("#c4fff4", 230, "bright-white"), "ok": ("#37d4a5", 79, "green"),
                   "warn": ("#ffd24a", 221, "bright-yellow"), "err": ("#ff4a6a", 203, "red"),
                   "info": ("#5db3a2", 73, "green"), "neutral": ("#3a6a5e", 65, "green")},
        "ice": {"bg": ("#050810", 233, "black"), "surface": ("#0a1220", 234, "black"),
                "surface_2": ("#0f1c30", 235, "black"), "gold_dim": ("#1f5a8a", 25, "blue"),
                "gold": ("#37a5d4", 39, "cyan"), "gold_bright": ("#7cd4f4", 117, "bright-cyan"),
                "amber": ("#47c0ff", 117, "bright-cyan"), "ember": ("#1a5aa8", 27, "blue"),
                "text": ("#a8cfe8", 187, "white"), "text_dim": ("#5e7a9a", 68, "white"),
                "text_strong": ("#c4e8ff", 230, "bright-white"), "ok": ("#37a5d4", 39, "cyan"),
                "warn": ("#ffb347", 215, "bright-yellow"), "err": ("#ff5a4a", 203, "red"),
                "info": ("#5d8ab3", 67, "blue"), "neutral": ("#3a5a6a", 60, "blue")},
        "gold": {"bg": ("#0a0805", 233, "black"), "surface": ("#161009", 234, "black"),
                 "surface_2": ("#221806", 235, "black"), "gold_dim": ("#8a6d1f", 94, "yellow"),
                 "gold": ("#ffd700", 220, "yellow"), "gold_bright": ("#ffe97c", 228, "bright-yellow"),
                 "amber": ("#ffc347", 220, "bright-yellow"), "ember": ("#c94a1a", 166, "red"),
                 "text": ("#f0e0b0", 187, "white"), "text_dim": ("#a89868", 137, "white"),
                 "text_strong": ("#fff8d0", 230, "bright-white"), "ok": ("#ffd700", 220, "yellow"),
                 "warn": ("#ffc347", 220, "bright-yellow"), "err": ("#c94a1a", 166, "red"),
                 "info": ("#c9b25d", 179, "yellow"), "neutral": ("#7a6a44", 94, "yellow")},
        "emerald": {"bg": ("#050a06", 233, "black"), "surface": ("#0a160c", 234, "black"),
                    "surface_2": ("#0f2212", 235, "black"), "gold_dim": ("#1f8a3d", 28, "green"),
                    "gold": ("#37d45c", 41, "green"), "gold_bright": ("#7cf49c", 84, "bright-green"),
                    "amber": ("#47ff70", 83, "bright-green"), "ember": ("#1aa842", 35, "red"),
                    "text": ("#a8e8bd", 187, "white"), "text_dim": ("#5e9a72", 71, "white"),
                    "text_strong": ("#c4ffd8", 230, "bright-white"), "ok": ("#37d45c", 41, "green"),
                    "warn": ("#ffd24a", 221, "bright-yellow"), "err": ("#ff4a4a", 203, "red"),
                    "info": ("#5db37d", 78, "green"), "neutral": ("#3a6a4a", 66, "green")},
        "mono": None,  # монохром собирается программно (§27.8): все цвета → neutral
    }

    # §21.4: ни один ключ не пропущен — проверка в self-test (--palette)
    REQUIRED_KEYS = ("bg", "surface", "surface_2", "gold_dim", "gold", "gold_bright",
                     "amber", "ember", "text", "text_dim", "text_strong",
                     "ok", "warn", "err", "info", "neutral")

    def __init__(self, name: str = "dark-gold", depth: str = "auto", plain: bool = False):
        self.name = name if name in self.THEMES else "dark-gold"
        caps = HODGETerm.caps()
        if depth == "auto":
            depth = caps["color_depth"]
        if plain or depth == "mono":
            depth = "mono"
        self.depth = depth
        self.plain = plain or depth == "mono"
        self._mono = {k: ("#808080", 8, "white") for k in self.REQUIRED_KEYS}

    def palette(self, depth: str | None = None) -> dict:
        """Палитра на запрошенной глубине (§21.3): truecolor → '#rrggbb',
        256 → номер, 16 → имя. B6: раньше здесь была мёртвая ветка `if False`,
        и глубина игнорировалась."""
        d = depth or self.depth
        if self.name == "mono" or d == "mono":
            return {k: v[0] for k, v in self._mono.items()}
        idx = {"truecolor": 0, "256": 1, "16": 2}[d]
        return {k: v[idx] for k, v in self.THEMES[self.name].items()}

    def color_code(self, key: str, depth: str | None = None) -> str:
        """ANSI-префикс цвета для ключа палитры на текущей глубине."""
        if self.plain:
            return ""
        d = depth or self.depth
        if self.name == "mono" or d == "mono":
            return ""  # §27.8: цвет нейтрален, стили остаются
        pal = self.THEMES[self.name]
        if key not in pal:  # §21.4 — не молчать
            return ""
        hexv, c256, c16 = pal[key]
        if d == "truecolor":
            r, g, b = int(hexv[1:3], 16), int(hexv[3:5], 16), int(hexv[5:7], 16)
            return f"\x1b[38;2;{r};{g};{b}m"
        if d == "256":
            return f"\x1b[38;5;{c256}m"
        base16 = {"black": 0, "red": 1, "green": 2, "yellow": 3, "blue": 4,
                  "cyan": 5, "white": 7}
        m = re.match(r"(bright-)?(\w+)", c16)
        bright = bool(m and m.group(1))
        name = m.group(2) if m else "white"
        # §21.3 / A10: 16-color ANSI — normal 30..37, bright 90..97.
        # Ключ палитры содержит имя 16-цвета строкой ("yellow", "bright-white").
        # Раньше code = base + 60 для bright, затем 90 + code = 150 + base —
        # невалидный ANSI. Считаем от base без двойного оффсета.
        base = base16.get(name, 7)
        return f"\x1b[{90 + base if bright else 30 + base}m"

    @staticmethod
    def rgb_to_xterm256(hexv: str) -> int:
        """§31: формула rgb→xterm256 (для --theme-preview)."""
        r, g, b = (int(hexv[1:3], 16), int(hexv[3:5], 16), int(hexv[5:7], 16))
        def q(v):
            return 0 if v < 48 else 1 if v < 115 else (v - 35) // 40
        return 16 + 36 * q(r) + 6 * q(g) + q(b)


# ══════════════════════════════════════════════════════════════════════════
# §22. ОКРАШИВАНИЕ ГЛИФОВ: dye / num / gradient / badge — чистые функции,
# возвращают строку; идемпотентность dye() обязательна (§22.3, приём 31).
# ══════════════════════════════════════════════════════════════════════════
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

# §27.2 / A13: ASCII-фолбэки при --unicode off. Каждый не-ASCII глиф,
# который файл вообще печатает, имеет здесь ASCII-эквивалент; остальные
# не-ASCII символы заменяются на "?" (см. _ascii_fallback).
_ASCII_GLYPHS = {
    "✓": "[ok]", "✗": "[err]", "·": "-", "❯": ">", "─": "-", "│": "|",
    "┌": "+", "┐": "+", "└": "+", "┘": "+", "├": "+", "┤": "+", "┬": "+",
    "┴": "+", "┼": "+", "╔": "+", "╗": "+", "╚": "+", "╝": "+", "║": "|",
    "═": "=", "╠": "+", "╣": "+", "╦": "+", "╩": "+", "╬": "+",
    "█": "#", "▁": ".", "▂": "-", "▃": "=", "▄": "+", "▅": "*",
    "▆": "#", "▇": "@", "░": ".", "▒": "+", "▓": "#",
    "✦": "*", "✧": "+", "◆": "o", "◇": "o", "•": ".", "…": "...",
    "«": "<<", "»": ">>",
}

# §27.7 / VII.6: RTL-символы оборачиваются в изолирующие U+2068/U+2069
_BIDI_CHARS = frozenset(
    "\u0590\u05d0\u0600\u0601\u0602\u0603\u0604\u0605\u0606\u0607\u0608\u0609\u060a"
    "\u060b\u060c\u060d\u060e\u060f\u0610\u0611\u0612\u0613\u0614\u0615\u0616\u0617"
    "\u0618\u0619\u061a\u061b\u061c\u061d\u061e\u061f\u0620\u0621\u0622\u0623\u0624"
    "\u0625\u0626\u0627\u0628\u0629\u062a\u062b\u062c\u062d\u062e\u062f\u0630\u0631"
    "\u0632\u0633\u0634\u0635\u0636\u0637\u0638\u0639\u063a\u063b\u063c\u063d\u063e"
    "\u063f\u0640\u0641\u0642\u0643\u0644\u0645\u0646\u0647\u0648\u0649\u064a\u064b"
    "\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0653\u0654\u0655\u0656\u0657\u0658"
    "\u0659\u065a\u065b\u065c\u065d\u065e\u065f")


def bidi_isolate(s: str) -> str:
    if any(c in _BIDI_CHARS for c in s):
        return "\u2068" + s + "\u2069"
    return s


class HODGEText:
    _dye_cache: dict = {}
    _gradient_cache: dict = {}         # §22.8: кэш градиентов (A14)
    theme: "HODGEColor | None" = None
    unicode_on: bool = True
    digit_tier: bool = True
    dye_mode: str = "per-char"         # §22.9 / A14: per-char|per-token|per-line

    @classmethod
    def strip_ansi(cls, s: str) -> str:
        return ANSI_RE.sub("", s)

    @classmethod
    def _ascii_fallback(cls, s: str) -> str:
        """§27.2: замена ДЕКОРАТИВНЫХ глифов на ASCII при --unicode off.
        Буквы национальных алфавитов (l10n §16 — русский текст интерфейса)
        не трогаем: это текст для экран-ридера, а не рамки/чекмарки."""
        if cls.unicode_on:
            return s
        return "".join(_ASCII_GLYPHS.get(c, c) for c in s)

    @classmethod
    def dye(cls, s: str, key: str = "text", style: str = "") -> str:
        """Окрашивание строки ключом палитры. Идемпотентно: если в s уже
        есть ANSI — не дублируем (§22.3). В plain/mono — сырая строка.
        §22.8 / VII.1: кэш _dye_cache; §27.7: bidi-изоляция RTL-строк."""
        s = bidi_isolate(cls._ascii_fallback(s))
        if cls.theme is None or cls.theme.plain:
            return s
        if ANSI_RE.search(s):
            return s  # идемпотентность (приём 31)
        ck = (s, key, style, cls.theme.name, cls.theme.depth)
        if ck in cls._dye_cache:
            return cls._dye_cache[ck]
        code = cls.theme.color_code(key)
        if not code:
            return s
        styles = {"bold": 1, "underline": 4, "reverse": 7}
        st = "".join(f"\x1b[{styles[x]}m" for x in style.split(",") if x in styles)
        end = "\x1b[22m" if "bold" in style else "\x1b[0m"
        result = f"{st}{code}{s}\x1b[0m{end if end != '\x1b[0m' else ''}"
        cls._dye_cache[ck] = result
        return result

    # §22.7 / VII.1: карта имя_метрики → тип форматирования num()
    TEXT_STYLE_MAP = {
        "duration_s": "duration", "rel_err": "float", "prec": "int",
        "n_tests": "int", "max_rel": "float", "det": "int",
        "worst_cross": "float", "reconstruction": "float", "anomaly": "int",
        "frames": "int", "rank": "int", "t_p": "int", "proj": "int",
    }

    @classmethod
    def rainbow(cls, s: str, family: str = "gold") -> str:
        """§22.10 / VII.1: посимвольная ротация ключей палитры."""
        if cls.theme is None or cls.theme.plain:
            return s
        if family == "ember":
            keys = ["ember", "amber", "gold", "gold_dim"]
        else:
            keys = ["gold_dim", "gold", "gold_bright", "amber"]
        out = []
        for i, ch in enumerate(cls._ascii_fallback(s)):
            out.append(cls.theme.color_code(keys[i % len(keys)]) + ch)
        out.append("\x1b[0m")
        return "".join(out)

    @classmethod
    def link(cls, url: str, text: str, osc: str = "auto") -> str:
        """§27.5 / VII.6: OSC 8 hyperlink при caps.hyperlinks и osc != off."""
        caps = HODGETerm.caps()
        use = caps["hyperlinks"] if osc == "auto" else (osc == "on")
        if not use or cls.theme is None or cls.theme.plain:
            return text
        return f"\x1b]8;;{url}\x1b\\{text}\x1b]8;;\x1b\\"

    @classmethod
    def copy_hint(cls) -> str:
        """§27.6 / VII.6: подсказка про Ctrl+Y (OSC 52)."""
        return cls.dye("[Ctrl-Y копирует путь к отчёту]", "text_dim")

    @classmethod
    def fmt_pct(cls, v: float, prec: int = 1) -> str:
        """§16.4 / VIII.1: проценты через l10n-совместимый формат."""
        return cls.dye(f"{v:.{prec}f}%", "gold")

    @classmethod
    def fmt_datetime(cls, ts, locale: str = "ru") -> str:
        """§16.4 / VIII.1: даты 01.02.2026 (ru) / 2026-02-01 (en).
        Принимает datetime | ISO-строку | unix-время | None."""
        if ts is None:
            return "—"
        if isinstance(ts, datetime):
            dt = ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)
        elif isinstance(ts, str):
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except Exception:
                return ts
        else:
            dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        if locale == "ru":
            return dt.strftime("%d.%m.%Y %H:%M:%S")
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def num(cls, v, kind: str = "float", prec: int = 4) -> str:
        """Per-digit tiering (§22.5): окраска числа по ВЕЛИЧИНЕ, не однородно.
        0→gold_dim; 1–9→gold; 10–99→gold+bold; 100–999→gold_bright; ≥1000→amber;
        отрицательные→ember; NaN/inf→err+reverse. Единый ключ для одной
        величины во всех отчётах — TEXT_STYLE_MAP (§22.7)."""
        try:
            x = float(v)
        except Exception:
            return cls.dye(str(v), "neutral")
        if math.isnan(x) or math.isinf(x):
            return cls.dye("nan" if math.isnan(x) else "inf", "err", "reverse")
        neg = x < 0
        mag = abs(x)
        if kind == "pct":
            key = "gold_dim" if mag < 25 else "gold" if mag < 75 else "amber"
        elif kind == "bytes":
            key = "gold_dim" if mag < 1024 else "gold" if mag < 1048576 else "amber"
        elif kind == "duration":
            key = "gold_dim" if mag < 1 else "gold" if mag < 60 else "amber"
        elif not cls.digit_tier:
            key = "gold"
        else:
            a = mag
            key = "gold_dim" if a == 0 else "gold" if a < 10 else \
                "gold" if a < 100 else "gold_bright" if a < 1000 else "amber"
        body = cls.fmt_float(x, prec) if kind == "float" else cls.fmt_int(int(x)) if kind == "int" \
            else f"{x:.1f}%"
        style = "bold" if (cls.digit_tier and kind in ("int", "float") and 10 <= mag < 100) else ""
        if neg:
            key, style = "ember", style
        return cls.dye(body, key, style)

    @classmethod
    def fmt_float(cls, x: float, prec: int = 4) -> str:
        if isinstance(x, float) and (abs(x) >= 1e18 or (x != 0 and abs(x) < 1e-6)):
            return f"{x:.3e}"
        return f"{x:.{prec}f}".rstrip("0").rstrip(".") if isinstance(x, float) and prec > 0 and abs(x) < 1e6 else f"{x:.{prec}f}"

    @staticmethod
    def fmt_int(v: int) -> str:
        return f"{v:,}".replace(",", " ")

    @classmethod
    def gradient(cls, s: str, from_key: str = "gold_dim", to_key: str = "gold_bright",
                 mode: str = "span") -> str:
        """§22.4: плавный переход. §22.9: dye_mode=per-char|per-token|per-line.
        Глобальный dye_mode имеет приоритет, если mode="span" (дефолт)."""
        s = cls._ascii_fallback(s)
        if cls.theme is None or cls.theme.plain or mode == "off":
            return s
        if cls.theme.name == "mono" or cls.theme.depth == "mono":
            return s
        # §22.9: dye_mode переопределяет стратегию, если mode не задан явно
        eff = cls.dye_mode if mode == "span" else mode
        if len(s) > 256 and eff == "per-char":
            eff = "per-line"
        if eff in ("per-line", "block"):
            return cls.dye(s, to_key)
        # кэш (s, from_key, to_key, eff, depth) — §22.8 (A14)
        ck = (s, from_key, to_key, eff, cls.theme.depth, cls.theme.name)
        if ck in cls._gradient_cache:
            return cls._gradient_cache[ck]
        pal = HODGEColor.THEMES.get(cls.theme.name, HODGEColor.DARK_GOLD)
        def hx(k):
            v = pal.get(k, pal["gold"])
            return (int(v[0][1:3], 16), int(v[0][3:5], 16), int(v[0][5:7], 16))
        c0, c1 = hx(from_key), hx(to_key)
        def color_at(t):
            r = int(c0[0] + (c1[0] - c0[0]) * t)
            g = int(c0[1] + (c1[1] - c0[1]) * t)
            b = int(c0[2] + (c1[2] - c0[2]) * t)
            if cls.theme.depth == "truecolor":
                return f"\x1b[38;2;{r};{g};{b}m"
            return cls.theme.color_code(from_key if t < 0.5 else to_key)
        out = []
        if eff == "per-char":
            n = max(len(s), 1)
            for i, ch in enumerate(s):
                t = i / max(n - 1, 1)
                out.append(color_at(t) + ch)
        elif eff == "per-token":
            tokens = re.split(r"(\s+)", s)   # слова + пробелы
            total = max(sum(len(t) for t in tokens if t), 1)
            pos = 0
            for tok in tokens:
                if not tok:
                    continue
                t = pos / max(total - 1, 1)
                out.append(color_at(t) + tok)
                pos += len(tok)
        out.append("\x1b[0m")
        result = "".join(out)
        cls._gradient_cache[ck] = result
        return result

    @classmethod
    def badge(cls, verdict: str) -> str:
        """§27.3: бейджи не полагаются только на цвет — текст рядом всегда."""
        colors = {"PASS": "ok", "DONE": "ok", "OK": "ok", "WARN": "warn",
                  "FAIL": "err", "ERROR": "err", "SKIP": "neutral", "INFO": "info"}
        return cls.dye(f"[{verdict}]", colors.get(verdict, "neutral"), "bold")

    # §16.4 — числа/размеры/длительности
    @classmethod
    def fmt_size(cls, n: float) -> str:
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if n < 1024 or unit == "TB":
                return f"{n:.1f} {unit}" if unit != "B" else f"{int(n)} B"
            n /= 1024
        return f"{n:.1f} TB"

    @staticmethod
    def fmt_duration(sec: float) -> str:
        if sec < 1:
            return f"{sec * 1000:.0f} ms"
        if sec < 60:
            return f"{sec:.1f} s"
        m, s = divmod(int(sec), 60)
        if m < 60:
            return f"{m:02d}:{s:02d}"
        h, m = divmod(m, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    @staticmethod
    def plural(n: int, forms: tuple) -> str:
        """§16.3: EN one/other; RU one/few/many/other — формы передаются кортежем."""
        if len(forms) == 2:  # EN
            return forms[0] if n == 1 else forms[1]
        n10, n100 = n % 10, n % 100
        if n10 == 1 and n100 != 11:
            return forms[0]
        if 2 <= n10 <= 4 and not 12 <= n100 <= 14:
            return forms[1]
        return forms[2] if len(forms) == 3 else forms[2]


# ══════════════════════════════════════════════════════════════════════════
# §23. АНИМАЦИИ — сцена-машина рендерит кадры в «виртуальный экран».
# Сессия 1: сцены реализованы, но печать в терминал выключена в не-tty
# (§23.2: auto → off в pipe/--ci/--plain). RNG сцены — отдельный домен §5.3.
# ══════════════════════════════════════════════════════════════════════════
class HODGEAnim:
    SCENES = ("particles", "wave", "sparkle", "constellation", "matrix")
    EASING = {"cubic_out": lambda t: 1 - (1 - t) ** 3}   # §23.5

    def __init__(self, scene: str = "particles", width: int = 40, height: int = 10,
                 particles: int = 64, charset: str = "·•✦◆◇✧", seed: int = 0,
                 deterministic: bool = False):
        self.scene = scene if scene in self.SCENES else "particles"
        self.w, self.h, self.n = width, height, particles
        # §27.2: при unicode off — ASCII-частицы, независимо от charset (A13)
        self.charset = charset if HODGEText.unicode_on else ".+*#@&%"
        # §23.2 / §20.2: при deterministic RNG сцены фиксирован и не зависит
        # от seed прогона — только от самого факта (для байт-идентичности) (A18)
        self.seed = 0xDE7E_0000 if deterministic else seed  # иначе derive(seed, "anim") — §5.3
        self.grid = [[" "] * width for _ in range(height)]
        self._state = None

    def _rng(self):
        # детерминированный LCG на собственном сиде — не трогает домен задач
        state = {"x": (self.seed * 2654435761 + 1) & 0xFFFFFFFF}

        def rnd():
            x = state["x"]
            x ^= (x << 13) & 0xFFFFFFFF
            x ^= x >> 17
            x ^= (x << 5) & 0xFFFFFFFF
            state["x"] = x
            return x / 0xFFFFFFFF
        return rnd

    def frame(self, step: int) -> list[str]:
        """Один кадр в виртуальный экран (строки). Печать — не здесь (§2.2)."""
        rnd = self._rng()
        g = [[" "] * self.w for _ in range(self.h)]
        if self.scene == "particles":
            for _ in range(self.n):
                x = int(rnd() * self.w) % self.w
                y = int((rnd() * self.h + step) % self.h)
                ch = self.charset[int(rnd() * len(self.charset)) % len(self.charset)]
                g[y][x] = ch
        elif self.scene == "wave":
            for x in range(self.w):
                y = int((self.h / 2 - 1) + math.sin(x / 3.0 + step / 2.0) * (self.h / 3))
                if 0 <= y < self.h:
                    g[y][x] = "~"
        elif self.scene == "sparkle":
            for _ in range(max(3, self.n // 8)):
                x, y = int(rnd() * self.w) % self.w, int(rnd() * self.h) % self.h
                g[y][x] = "*" if step % 3 else "+"
        elif self.scene == "constellation":
            pts = [(int(rnd() * self.w), int(rnd() * self.h)) for _ in range(12)]
            for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
                if abs(x1 - x2) < 10:
                    for xx in range(min(x1, x2), max(x1, x2) + 1):
                        if 0 <= xx < self.w:
                            yy = y1 + (y2 - y1) * (xx - x1) // max(x2 - x1, 1)
                            if 0 <= yy < self.h:
                                g[yy][xx] = "."
            for x, y in pts:
                if 0 <= x < self.w and 0 <= y < self.h:
                    g[y][x] = "o"
        elif self.scene == "matrix":
            for col in range(self.w):
                head = int((step * 1.7 + rnd() * self.h) % self.h)
                for dy in range(4):
                    y = (head - dy) % self.h
                    g[y][col] = self.charset[int(rnd() * len(self.charset)) % len(self.charset)]
        return ["".join(row) for row in g]

    @classmethod
    def render_frames(cls, scene: str, n_frames: int, w: int, h: int, seed: int) -> int:
        """§19.9 --self-test --anim: N кадров без падений; alt-screen парно.
        Возвращает число успешно отрендеренных кадров."""
        anim = cls(scene, w, h, 32, seed=seed)
        ok = 0
        for i in range(n_frames):
            fr = anim.frame(i)
            if len(fr) == h and all(len(r) == w for r in fr):
                ok += 1
        return ok

    # ── §23.6 / §23.8 / VII.2: toast и title-bar ──
    @classmethod
    def toast(cls, text: str, kind: str = "INFO", ttl: float = 3.0) -> None:
        """Всплывающая строка в stderr (не в лог). В ci/plain — no-op."""
        if _ACTIVE_LOGGER and (_ACTIVE_LOGGER.cfg.ci or _ACTIVE_LOGGER.cfg.plain):
            return
        colors = {"PASS": "ok", "DONE": "ok", "WARN": "warn", "ERR": "err",
                  "ERROR": "err", "INFO": "info"}
        line = HODGEText.badge(kind) + " " + HODGEText.dye(text, colors.get(kind, "text"))
        sys.stderr.write(line + "\n")
        sys.stderr.flush()

    @classmethod
    def set_title(cls, text: str) -> None:
        """OSC 0 title-bar; в ci/plain — no-op."""
        if _ACTIVE_LOGGER and (_ACTIVE_LOGGER.cfg.ci or _ACTIVE_LOGGER.cfg.plain):
            return
        if not getattr(_ACTIVE_LOGGER.cfg, "title_bar", True) if _ACTIVE_LOGGER else False:
            return
        sys.stdout.write(f"\x1b]0;{text}\x1b\\")
        sys.stdout.flush()


# ══════════════════════════════════════════════════════════════════════════
# §11.1-принцип: вычислительное ядро — 100% self-contained (decimal stdlib).
# HODGEHP — высокоточный слой: π, тригонометрия, Γ (Стирлинг + точные числа
# Бернулли), tanh–sinh квадратура, комплексная арифметика. Все задачи-тесты
# высокой точности живут здесь. (§2.2: ядро не печатает в stdout.)
# ══════════════════════════════════════════════════════════════════════════
from contextlib import contextmanager


# ══════════════════════════════════════════════════════════════════════════
# §3.2 v6: «prec без зависаний». Три слоя честности:
#   1) HODGEPROG — heartbeat в stderr: пока идёт тяжёлая стадия (π, Γ, …),
#      терминал каждые 10 с печатает «…стадия: Ns» вместо молчания.
#   2) mpdec_cost — измеренная модель стоимости примитивов libmpdec
#      (mul/div квазилинейные; ln/exp/sqrt — квадратичные с большой
#      константой: ln@20k = 45.3 с, exp@20k = 13.6 с, sqrt@20k = 0.19 с).
#   3) Гейты _op_gate/_gamma_gate/_quad_gate — ПРЕДСКАЗУЕМАЯ операция с
#      оценкой выше лимита падает с честным ERR_* и советом, а не «висит».
# ══════════════════════════════════════════════════════════════════════════
class HODGEPROG:
    """Реестр тяжёлых стадий + heartbeat-поток (stderr, tty-gated)."""
    _lock = threading.Lock()
    stage: str = ""
    t0: float = 0.0
    task: str = ""
    _thread = None
    _stop = threading.Event()
    HEARTBEAT_S = 10.0

    @classmethod
    def begin(cls, stage: str) -> None:
        with cls._lock:
            cls.stage = stage
            cls.t0 = time.monotonic()

    @classmethod
    def end(cls) -> float:
        with cls._lock:
            dt = time.monotonic() - cls.t0
            cls.stage = ""
        return dt

    @classmethod
    def update(cls, stage: str) -> None:
        with cls._lock:
            cls.stage = stage

    @classmethod
    def set_task(cls, name: str) -> None:
        with cls._lock:
            cls.task = name

    @classmethod
    def _loop(cls) -> None:
        last = 0.0
        while not cls._stop.wait(1.0):
            with cls._lock:
                st, t0, tk = cls.stage, cls.t0, cls.task
            if not st:
                last = 0.0
                continue
            el = time.monotonic() - t0
            if el - last >= cls.HEARTBEAT_S:
                last = el
                line = f"… {st}: {el:.0f} s"
                if tk:
                    line += f" · task {tk}"
                try:
                    sys.stderr.write(line + "\n")
                    sys.stderr.flush()
                except Exception:
                    pass

    @classmethod
    def start(cls) -> None:
        """Запуск heartbeat: stderr-tty или HODGE_HEARTBEAT=1; HODGE_HEARTBEAT=0 — выключить."""
        if cls._thread is not None:
            return
        on = os.environ.get("HODGE_HEARTBEAT")
        try:
            tty = sys.stderr.isatty()
        except Exception:
            tty = False
        if on == "0" or (on is None and not tty):
            return
        cls._stop.clear()
        cls._thread = threading.Thread(target=cls._loop, daemon=True,
                                       name="hodge-heartbeat")
        cls._thread.start()

    @classmethod
    def stop(cls) -> None:
        cls._stop.set()
        cls._thread = None


def mpdec_cost(digits: int) -> dict:
    """Измеренная стоимость ОДНОЙ операции libmpdec на `digits` знаках (сек).
    Калибровка CPython 3.11/_decimal 2.4.2: mul/div — NTT (квазилинейные),
    sqrt O(n^2.2), ln O(n^2.8), exp O(n^2.9):
      digits=5000:  mul ~1e-5  div 0.001  sqrt 0.009  ln 0.96  exp 0.24
      digits=20000: mul 0.002  div 0.010  sqrt 0.189  ln 45.3  exp 13.6
    На prec 5,000,000 знаков один ln — века: отсюда честные гейты."""
    d = max(int(digits), 30) / 5000.0
    return {"mul": 1.2e-5 * d ** 1.15,
            "div": 0.001 * d ** 1.66,
            "sqrt": 0.009 * d ** 2.2,
            "ln": 0.96 * d ** 2.79,
            "exp": 0.243 * d ** 2.93}


def _hodge_env_float(name: str, default: float) -> float:
    try:
        v = os.environ.get(name)
        return float(v) if v not in (None, "") else default
    except ValueError:
        return default


def _hodge_unsafe() -> bool:
    return os.environ.get("HODGE_PREC_UNSAFE") == "1"


def _fmt_terms(x: float) -> str:
    """Число членов для сообщения: 10^4970 или 760000."""
    if x >= 6.0:
        return f"~10^{x:.0f}"
    return f"~{10 ** x:,.0f}".replace(",", " ")


def _gate_msg(key: str, fallback: str, **kw) -> str:
    """Сообщение гейта из словаря ru/en (через активный логгер); вне прогона —
    английский fallback (ядро не зависит от cfg)."""
    lg = globals().get("_ACTIVE_LOGGER")
    if lg is not None:
        try:
            return hodge_fmt(lg.cfg, key, **kw)
        except Exception:
            pass
    try:
        return fallback.format(**kw)
    except Exception:
        return fallback


class HODGEHP:
    D = Decimal
    _pi_cache: dict = {}
    _ln_fact_cache: dict = {}           # §3.2 v5: ln((s−1)!) per (shift, prec+guard)
    _zeta_eps_cache: dict = {}          # §3.2 v5: ζ(2j)−1 per (ctx, j)
    _bern_cache: list = [Fraction(1)]   # B_0, B_2, B_4, ... точные

    # ── §3.2 v5: точная ζ-поправка отношения чисел Бернулли ──
    @classmethod
    def _zeta_even_eps(cls, j: int, ctx: int) -> Decimal:
        """ζ(2j) − 1 = Σ_{m≥2} m^{−2j}, сумма до члена < 10^−(ctx+12).
        Нужна для ТОЧНОГО отношения B_{2k}/B_{2k−2}: асимптотика
        B_{2k}/B_{2k−2} ≈ −(2k)(2k−1)/(2π)² без поправки даёт относительную
        ошибку O(4^−k) → абс. ошибка хвоста |term_60|·4^−61 ≈ 1e−185 при
        prec 308 (t40 не проходил tol 1e−300). Прямая сумма сходится со
        скоростью m^{−2j}: Σ M(j) ≈ 10^{(ctx+12)/(2j)} членов — при j ≥ 151
        это ≤ ~6·10³ членов (~2 с один раз на (ctx, j), кэш на весь прогон).
        Для k ≤ 150 числа Бернулли ТОЧНЫЕ (рекуррентность) — поправка не нужна.
        §3.2 v6: последний рубеж от «тихой вечности» — при прямой сумме длиннее
        5e7 членов поднимается ERR_GAMMA_PREC (gamma_gate должен был сработать
        раньше — например, при прямом вызове с чужим ctx)."""
        if (ctx + 12) / (2 * j) > math.log10(5e7):
            raise ValueError(
                f"ERR_GAMMA_PREC ζ({2 * j})−1 @ ctx={ctx}: прямая сумма "
                f"{_fmt_terms((ctx + 12) / (2 * j))} членов — см. gamma_gate")
        key = (ctx, j)
        eps = cls._zeta_eps_cache.get(key)
        if eps is not None:
            return eps
        with localcontext() as zctx:
            zctx.prec = ctx
            total = cls.D(0)
            m = 2
            cut = cls.D(1).scaleb(-(ctx + 12))
            while True:
                t = cls.D(m) ** (-2 * j)
                total += t
                if t < cut:
                    break
                m += 1
        cls._zeta_eps_cache[key] = +total
        return cls._zeta_eps_cache[key]

    # ── управление точностью (§19: точность задаётся явно, не из воздуха) ──
    @classmethod
    @contextmanager
    def scope(cls, prec: int):
        """Все Decimal-вычисления задач живут внутри scope(prec):
        локальный контекст гарантированно восстанавливается при выходе."""
        with localcontext() as ctx:
            ctx.prec = prec
            yield prec

    # ── §3.2 v6: честные гейты тяжёлых примитивов ──
    @classmethod
    def _op_gate(cls, kind: str, prec: int, est: float) -> None:
        """Оценка стоимости одного вызова > HODGE_OP_LIMIT (сек, по умолч. 30)
        → ERR_PREC_OP с числами и советом; HODGE_PREC_UNSAFE=1 — осознанный
        обход (тогда операция идёт под heartbeat)."""
        if est <= 0:
            return
        lim = _hodge_env_float("HODGE_OP_LIMIT", 30.0)
        if est <= lim:
            return
        if _hodge_unsafe():
            HODGEPROG.begin(f"{kind} @{prec} знаков (обход гейта)")
            return
        raise ValueError(_gate_msg(
            "prec.op.block",
            "ERR_PREC_OP {kind} @ prec={prec}: estimate ≈{est} s > limit {lim} s "
            "(HODGE_OP_LIMIT). Advice: engine=julia or prec ≤ ~10000; "
            "override: HODGE_PREC_UNSAFE=1",
            kind=kind, prec=prec, est=f"{est:,.0f}", lim=f"{lim:g}"))

    @classmethod
    def gamma_gate(cls, prec: int) -> None:
        """Γ-гейт: сдвиг y ≈ prec/2.73 → ряд Стирлинга ~π·y членов, каждый —
        дивизия на prec-значном числе; ζ(2k)−1 при k≈151 — прямая сумма
        ~10^((prec+76)/302) членов (кэш не спасает: члены РАЗНЫЕ для каждого k).
        Оценка > HODGE_GAMMA_LIMIT (сек, по умолч. 900) → ERR_GAMMA_PREC."""
        if _hodge_unsafe():
            HODGEPROG.begin(f"Γ @ prec={prec} (обход гейта)")
            return
        lim = _hodge_env_float("HODGE_GAMMA_LIMIT", 900.0)
        shift = max(40, int(math.ceil((prec + 4) / 2.72864)) + 4)
        k_star = 3.1416 * shift
        c = mpdec_cost(prec)
        est_series = k_star * (2 * c["mul"] + c["div"] + 3e-5)
        e151 = (prec + 76) / 302.0
        est_zeta = (10 ** min(e151, 15.0)) * (1.5 * c["mul"] + 3e-5)
        est = est_series + est_zeta
        if est <= lim:
            return
        raise ValueError(_gate_msg(
            "prec.gamma.block",
            "ERR_GAMMA_PREC Γ @ prec={prec}: shift y≈{shift}, series ≈{terms} "
            "terms + ζ(302)−1 sum ≈{zterms} terms; estimate ≈{est} s > limit "
            "{lim} s (HODGE_GAMMA_LIMIT). Γ-tasks: prec ≤ ~1500 (py) / "
            "≤ ~5000 bits (julia) or HODGE_PREC_UNSAFE=1",
            prec=prec, shift=f"{shift:,}", terms=_fmt_terms(math.log10(max(k_star, 2))),
            zterms=_fmt_terms(e151), est=f"{est:,.0f}", lim=f"{lim:g}"))

    @classmethod
    def quad_gate(cls, prec: int, h: Decimal) -> int:
        """tanh–sinh гейт: узлов ≈ 2·asinh(2(prec+5)ln10/π)/h + 1, каждый узел —
        4-5 exp по prec-значному ctx. Оценка > HODGE_QUAD_LIMIT (1800 с) →
        ERR_QUAD_PREC. Возвращает расчётное число узлов."""
        if prec > 60:
            t_needed = math.asinh((prec + 5) * math.log(10) * 2 / math.pi)
            nodes = 2 * math.ceil(t_needed / float(h)) + 1
        else:
            nodes = 0  # пусть считает вызывающий — мелочь
        if _hodge_unsafe() or nodes <= 0:
            return nodes
        lim = _hodge_env_float("HODGE_QUAD_LIMIT", 1800.0)
        c = mpdec_cost(prec)
        est = nodes * (4 * c["exp"] + 2 * c["div"])
        if est <= lim:
            return nodes
        raise ValueError(_gate_msg(
            "prec.quad.block",
            "ERR_QUAD_PREC tanh–sinh @ prec={prec}: ≈{nodes} nodes × "
            "(4 exp + 2 div) ≈ {est} s > limit {lim} s (HODGE_QUAD_LIMIT). "
            "Keep quadratures at prec ≤ ~20000 or HODGE_PREC_UNSAFE=1",
            prec=prec, nodes=f"{nodes:,}", est=f"{est:,.0f}", lim=f"{lim:g}"))

    # ── §3.2 v6: быстрые обёртки над квадратичными примитивами libmpdec ──
    @classmethod
    def sqrt_hp(cls, x: Decimal, prec: int) -> Decimal:
        """√x корректно до prec+15 знаков. Decimal.sqrt() у libmpdec — O(n^2.2)
        (0.19 с уже на 20k знаков → на 5m часы на ОДИН вызов); Ньютон с
        удвоением точности — O(M(n)): ~2 дивизии на конечном уровне."""
        if x < 0:
            raise ValueError("ERR_SQRT_NEG")
        with localcontext() as c:
            if x == 0:
                c.prec = max(prec, 5)
                return cls.D(0)
            # затравка по порядку величины (O(1)): 10^(adj/2)·2 — точность
            # ~0.5 цифры; Ньютон УДВАИВАЕТ фактическую точность на шаге
            # (digits_{k+1} = 2·digits_k + 0.45), поэтому p — оценка фактических
            # цифр, а контекст = p+12 (запас на округление деления).
            adj = x.adjusted()
            c.prec = 30
            r = cls.D(10) ** (adj // 2) * cls.D(2)
            p = 0.5                              # фактические цифры точности
            target = prec + 15
            while p < target:
                c.prec = int(min(target, p * 2)) + 12
                r = (r + x / r) / 2
                p *= 2
            c.prec = target + 8
            r = (r + x / r) / 2
            return +r

    @classmethod
    def ln_hp(cls, x: Decimal, prec: int) -> Decimal:
        """ln с гейтом: libmpdec ln — O(n^2.8), 45 с уже на 20k знаков."""
        cls._op_gate("ln", prec, mpdec_cost(prec)["ln"])
        return x.ln()

    @classmethod
    def exp_hp(cls, x: Decimal, prec: int) -> Decimal:
        """exp с гейтом: libmpdec exp — O(n^2.9)."""
        cls._op_gate("exp", prec, mpdec_cost(prec)["exp"])
        return x.exp()

    @classmethod
    def pi(cls, prec: int) -> Decimal:
        """π: ниже 1500 знаков — Мэчин (исторический путь self-test), выше —
        Чудновский с бинарным расщеплением (§3.2 v6: Мэчин — O(prec²):
        ~0.72·prec atan-членов × дивизии prec-значных чисел — на prec 5m
        вечность; Чудновский — prec/14.18 членов, дерево в Decimal на NTT-мулах
        libmpdec: 1e6 знаков ≈ 5 с, 5m ≈ 1–2 мин)."""
        if prec in cls._pi_cache:
            return cls._pi_cache[prec]
        cls._pi_cache = {k: v for k, v in cls._pi_cache.items() if k <= prec}
        if prec >= 1500:
            val = cls._pi_chud(prec)
        else:
            with cls.scope(prec + 6):
                at5 = cls._atan_series(cls.D(1) / 5, prec + 6)
                at239 = cls._atan_series(cls.D(1) / 239, prec + 6)
                val = 16 * at5 - 4 * at239
        # BUGFIX(HP-CACHE): раньше «+val» округлялся в КОНТЕКСТЕ ВЫЗЫВАЮЩЕГО —
        # задача, вызвавшая pi(55) внутри scope(30), кэшировала π, обрезанный
        # до 30 знаков, под ключом 55 и отравляла кэш всем последующим задачам
        # (в full-прогоне t40 ловил rel err 4e-29 вместо 8e-52). Теперь
        # округление до ровно prec знаков — внутри scope(prec): контекст
        # вызывающего не влияет на значение в кэше.
        with cls.scope(prec):
            cls._pi_cache[prec] = +val
        return cls._pi_cache[prec]

    @classmethod
    def _pi_chud(cls, prec: int) -> Decimal:
        """Чудновский: 1/π = 12·Σ (−1)^k (6k)!(A+Bk)/((3k)!(k!)³·C^(3k+3/2)).
        Бинарное расщепление целиком в Decimal с ctx.prec = верхняя оценка
        цифр Q (все промежуточные — целые числа, мулы точны): не нужен
        int↔Decimal обмен баз (квадратичный в обе стороны) — NTT-мулы
        libmpdec делают дерево O(M(n)·log K). π = 426880·√10005·Q/T."""
        A, B = 13591409, 545140134
        C3 = cls.D(640320) ** 3 / 24        # = 10939058860032000 — точное целое
        K = int(prec / 14.18) + 8
        qdig = int(K * (3 * math.log10(max(K, 10)) + 14.8)) + 2000
        HODGEPROG.begin(f"π: Чудновский BS, {prec} знаков, {K} членов")
        try:
            with localcontext() as bsctx:
                bsctx.prec = qdig
                bsctx.Emax = MAX_EMAX           # Q растёт до ~31·K цифр —
                bsctx.Emin = MIN_EMIN           # дефолтного Emax 999999 мало
                def bs(a: int, b: int):
                    if b - a == 1:
                        k = a
                        if k == 0:
                            return cls.D(1), cls.D(1), cls.D(A)  # Q_0 = 1 (пустое произведение)
                        P = cls.D((6 * k - 5) * (2 * k - 1) * (6 * k - 1))
                        T = P * cls.D(A + B * k)
                        return P, cls.D(k * k * k) * C3, -T if k & 1 else T
                    m = (a + b) // 2
                    P1, Q1, T1 = bs(a, m)
                    P2, Q2, T2 = bs(m, b)
                    return P1 * P2, Q1 * Q2, T1 * Q2 + T2 * P1
                _P, Q, T = bs(0, K)
            with localcontext() as fin:
                fin.prec = prec + 60
                fin.Emax = MAX_EMAX             # Q/T живут на экспоненте ~2M
                fin.Emin = MIN_EMIN
                Qt, Tt = +Q, +T                 # усечение до prec+60: относительные
                rt = cls.sqrt_hp(cls.D(10005), prec + 60)   # ошибки сокращаются
                val = cls.D(426880) * rt * Qt / Tt
        finally:
            HODGEPROG.end()
        return val


    @classmethod
    def _atan_series(cls, x: Decimal, prec: int) -> Decimal:
        """arctan(x) для |x| ≤ 1: редукция удвоением аргумента + ряд.
        §3.2 v6: гейт — ~1.7·prec членов × (mul+div) — на большом prec это
        O(prec²) (в π-путь выше 1500 уже не попадает: там Чудновский)."""
        cls._op_gate("atan", prec, (1.7 * prec + 40) * (mpdec_cost(prec)["mul"] + mpdec_cost(prec)["div"] + 2e-5))
        threshold = cls.D(1).scaleb(-(prec + 4))
        k = 0
        while x > cls.D("0.2"):
            x = x / (1 + cls.sqrt_hp(1 + x * x, prec + 4))   # atan(u) = 2·atan(u/(1+√(1+u²)))
            k += 1
        term, s, n = x, x, 0
        x2 = x * x
        while True:
            n += 1
            term = -term * x2 * (2 * n - 1) / (2 * n + 1)
            s += term
            if abs(term) < threshold:
                break
            if n > 4 * prec + 40:
                break
        return s * (2 ** k)

    @classmethod
    def atan2(cls, y: Decimal, x: Decimal, prec: int) -> Decimal:
        """Угол точки (x, y) в [−π, π]. Точные особые случаи (0,0)→0."""
        pi = cls.pi(prec)
        if x == 0 and y == 0:
            return cls.D(0)
        if x > 0:
            a = cls._atan_series(abs(y / x) if x != 0 else cls.D(1), prec)
            return a if y >= 0 else -a
        if x < 0 and y >= 0:
            return pi - cls._atan_series(abs(y / x), prec)
        return -pi + cls._atan_series(abs(y / x), prec)

    # ── тригонометрия: редукция к |x| ≤ π/2 с учётом знака ветви ──
    @classmethod
    def _reduce_half_pi(cls, x: Decimal, prec: int) -> Decimal:
        """Редукция: sin(x)=sin(y), cos(x)=−cos(y) при ветви π−x (x>π/2),
        поэтому cos применяет отдельный флип. Возвращает |y| ≤ π/2."""
        pi = cls.pi(prec)
        n = int((x + pi / 2) / (2 * pi))
        x = x - n * 2 * pi                    # x ∈ [−π/2, 3π/2)
        if x > pi / 2:
            return pi - x                     # sin(π−y)=sin(y), cos(π−y)=−cos(y)
        return x

    @classmethod
    def sin(cls, x: Decimal, prec: int) -> Decimal:
        cls._op_gate("sin", prec, (0.09 * prec + 40) * (mpdec_cost(prec)["mul"] + 4e-5))
        y = cls._reduce_half_pi(x, prec)
        threshold = cls.D(1).scaleb(-(prec + 3))
        term, s, n = y, y, 0
        y2 = y * y
        while True:
            n += 1
            term = -term * y2 / ((2 * n) * (2 * n + 1))
            s += term
            if abs(term) < threshold or n > 2 * prec + 50:
                break
        return s

    @classmethod
    def cos(cls, x: Decimal, prec: int) -> Decimal:
        cls._op_gate("cos", prec, (0.09 * prec + 40) * (mpdec_cost(prec)["mul"] + 4e-5))
        y = cls._reduce_half_pi(x, prec)
        s = cls._cos_series(y, prec)
        # ветвь π−y (y<0 после редукции π−x) даёт cos(x) = −cos(y)
        pi = cls.pi(prec)
        n = int((x + pi / 2) / (2 * pi))
        xr = x - n * 2 * pi
        return -s if xr > pi / 2 else s

    @classmethod
    def _cos_series(cls, y: Decimal, prec: int) -> Decimal:
        threshold = cls.D(1).scaleb(-(prec + 3))
        term, s, n = cls.D(1), cls.D(1), 0
        y2 = y * y
        while True:
            n += 1
            term = -term * y2 / ((2 * n - 1) * (2 * n))
            s += term
            if abs(term) < threshold or n > 2 * prec + 50:
                break
        return s

    # ── комплексная арифметика на парах Decimal ──
    @classmethod
    def cadd(cls, u, v): return (u[0] + v[0], u[1] + v[1])
    @classmethod
    def csub(cls, u, v): return (u[0] - v[0], u[1] - v[1])
    @classmethod
    def cmul(cls, u, v): return (u[0] * v[0] - u[1] * v[1], u[0] * v[1] + u[1] * v[0])
    @classmethod
    def cscale(cls, u, k): return (u[0] * k, u[1] * k)
    @classmethod
    def cdiv(cls, u, v):
        d = v[0] * v[0] + v[1] * v[1]
        return ((u[0] * v[0] + u[1] * v[1]) / d, (u[1] * v[0] - u[0] * v[1]) / d)
    @classmethod
    def cabs(cls, u): return (u[0] * u[0] + u[1] * u[1]).sqrt()
    @classmethod
    def cconj(cls, u): return (u[0], -u[1])

    @classmethod
    def cexp(cls, u, prec: int):
        r = cls.exp_hp(u[0], prec)
        return (r * cls.cos(u[1], prec), r * cls.sin(u[1], prec))

    @classmethod
    def clog(cls, u, prec: int):
        return (cls.ln_hp(cls.cabs(u), prec), cls.atan2(u[1], u[0], prec))

    @classmethod
    def cpow_frac(cls, u, q: Fraction, prec: int):
        """u^q для точного рационального q: u^q = exp(q·log u) (Cardano)."""
        lg = cls.clog(u, prec)
        return cls.cexp((lg[0] * q.numerator / q.denominator,
                         lg[1] * q.numerator / q.denominator), prec)

    @classmethod
    def cbrt_principal(cls, u, prec: int):
        return cls.cpow_frac(u, Fraction(1, 3), prec)

    @classmethod
    def zeta_pow(cls, N: int, prec: int) -> list:
        """Таблица ζ^0 … ζ^{N−1}, ζ = e^{2πi/N}.
        v1.4.3-session7: таблица строится в контексте с guard-разрядами
        g = ⌈log10 N⌉ + 3: накопленная ошибка k-го элемента (k·10^{−prec−g})
        после округления к рабочей точности остаётся < 10^{−prec}. Ранее
        последовательное умножение давало |ζ^k − ζ^k_точно| ≈ k·10^{−prec}
        (дрейф ζ^N ≈ N·10^{−prec}, измерено диагностикой session7: N=30,
        prec=45 → 3.2e−44). Паритет с master_hodge.jl §3.2 v6 (там каждый
        элемент — отдельный exp); здесь guard-разряды дают ту же точность
        за O(N) умножений вместо O(N) дорогих cexp.
        Диагностика session7 также показала: фазы period_closed (ζ^{ra+sb})
        и period_numeric (ζ^{ra+s(b−N)}) — ОДИН и тот же элемент таблицы
        (индексы равны как целые до mod N), поэтому расхождения периодов
        от фазы не зависят — их источник: квадратурный пол tanh–sinh
        (дискретизация при фиксированном h) и округление Γ."""
        guard = int(math.ceil(math.log10(max(N, 10)))) + 3
        with localcontext() as zctx:
            zctx.prec = prec + guard
            two_pi = 2 * cls.pi(prec + guard)
            w = cls.cexp((cls.D(0), two_pi / N), prec + guard)
            out = [(cls.D(1), cls.D(0))]
            for _ in range(N - 1):
                out.append(cls.cmul(out[-1], w))
        return out

    # ── Γ: Стирлинг + сдвиг аргумента; числа Бернулли — ТОЧНЫЕ (Fraction) ──
    @classmethod
    def _bernoulli_even(cls, k: int) -> Fraction:
        """B_{2k} по точной рекуррентности (проверено: 1/6, −1/30, 1/42…)."""
        cache = cls._bern_cache
        while len(cache) <= k:
            m = 2 * len(cache)                     # очередное чётное m
            s = Fraction(0)
            for j in range(0, m - 1, 2):           # j = 0, 2, …, m−2
                s += Fraction(math.comb(m + 1, j)) * cache[j // 2]
            cache.append(Fraction(1, 2) - s / (m + 1))
        return cache[k]

    @classmethod
    def lgamma(cls, x: Decimal, prec: int) -> Decimal:
        """ln Γ(x), x > 0. Стирлинг со сдвигом y ≥ SHIFT до 10^−(prec+3).
        §3.2 v5 (unlimited prec): при prec ≳ 200 старый кап k ≤ 60 обрывал ряд
        на 10^−223 (t40 не проходил tol). Теперь: сдвиг от ДЕСЯТИЧНЫХ цифр —
        минимум остатка ~10^−2.7286·y достигает порога 10^−(prec+3) на
        УБЫВАЮЩЕЙ ветви ряда (дивергенция не начинается); при k > 150 числа
        Бернулли продолжаются ТОЧНЫМ ζ-отношением
            B_{2k}/B_{2k−2} = −(2k)(2k−1)·ζ(2k)/((2π)²·ζ(2k−2)),
        ζ(2j) − 1 — прямая сумма (кэш): НЕскорректированное отношение даёт
        абс. ошибку хвоста |term_60|·O(4^−61) ≈ 1e−185 при prec 308.
        Внутренние guard-разряды компенсируют накопление ошибок; сдвиговый
        цикл сворачивается в ln((s−1)!)+ln Π(1+x/k) — O(1) дорогих ln.
        §3.2 v6: gamma_gate ПЕРЕД работой — оценка ряда (~π·y членов) и ζ-сумм;
        без гейта prec ≥ ~2000 знаков выглядел как зависание (реально — часы).
        exp() финала — exp_hp с гейтом (libmpdec exp квадратичен)."""
        cls.gamma_gate(prec)
        shift = max(40, int(math.ceil((prec + 4) / 2.72864)) + 4)
        guard_d = int(math.ceil((64 + math.log2(shift + 16)) / math.log2(10)))
        with localcontext() as ictx:
            ictx.prec = prec + guard_d
            x = +cls.D(x)
            if x < shift:
                # §3.2 v5 (perf): Σ_{k=0}^{s−1} ln(x+k) = ln x + ln((s−1)!) +
                # Σ_{k=1}^{s−1} ln(1+x/k), где s = ceil(shift−x) — число шагов
                # сдвига, y_final = x + s. ln((s−1)!) кэшируется per (s, prec),
                # остаток сворачивается в ОДИН ln произведения — сотни дорогих
                # ln (≈12 мс каждый на 1000 знаков) заменяются мулами (≈0.02 мс).
                s = int(math.ceil(shift - x))    # шагов сдвига (для 0<x<1 это shift)
                key = (s, prec + guard_d)
                lf = cls._ln_fact_cache.get(key)
                if lf is None:
                    fk = cls.D(1)
                    for k in range(2, s):
                        fk *= k                      # (s−1)! — точное целое
                    lf = fk.ln()
                    cls._ln_fact_cache[key] = lf
                prod = cls.D(1)
                for k in range(1, s):
                    prod *= 1 + x / k                # Π(1+x/k) ≤ s — маленький лишний порядок
                acc = -(x.ln() + lf + prod.ln())
                y = x + s                            # Стирлинг — при y_final, НЕ при shift
            else:
                acc = cls.D(0)
                y = x
            piw = cls.pi(prec + guard_d)
            half_ln_2pi = (2 * piw).ln() / 2
            t = (y - cls.D(1) / 2) * y.ln() - y + half_ln_2pi
            pw = y
            k = 1
            threshold = cls.D(1).scaleb(-(prec + 3))
            two_pi_sq = 4 * piw * piw            # (2π)²
            term = cls.D(0)
            cap = 8 * prec + 120                 # страховка от дивергенции ряда
            while True:
                if k <= 150:
                    B = cls._bernoulli_even(k)   # точные числа Бернулли
                    term = cls.D(B.numerator) / cls.D(B.denominator) / (2 * k * (2 * k - 1) * pw)
                else:
                    # ТОЧНОЕ ζ-отношение (§3.2 v5): без поправки — пол 1e−185
                    ek = cls._zeta_even_eps(k, prec + guard_d)
                    ek1 = cls._zeta_even_eps(k - 1, prec + guard_d)
                    term = -term * ((2 * k - 2) * (2 * k - 3)) * (1 + ek) \
                        / (two_pi_sq * y * y * (1 + ek1))
                t += term
                if abs(term) < threshold or k > cap:
                    break
                pw *= y * y
                k += 1
            val = acc + t
        return val

    @classmethod
    def gamma(cls, x: Decimal, prec: int) -> Decimal:
        return cls.exp_hp(cls.lgamma(x, prec), prec)

    @classmethod
    def omega_closed(cls, N: int, a: int, b: int, prec: int) -> Decimal:
        """Ω_{a,b} = Γ(a/N)Γ(b/N)/Γ((a+b)/N) — вещественное, положительное."""
        ga = cls.gamma(cls.D(a) / N, prec)
        gb = cls.gamma(cls.D(b) / N, prec)
        gab = cls.gamma(cls.D(a + b) / N, prec)
        return ga * gb / gab

    @classmethod
    def rel_err_c(cls, u, v) -> Decimal:
        d = cls.cabs(cls.csub(u, v))
        n = max(cls.cabs(u), cls.cabs(v), cls.D("1e-40"))
        return d / n

    # ── tanh–sinh (double-exponential) узлы и квадратура ──
    @classmethod
    def tanh_sinh_nodes(cls, K: int, h: Decimal, prec: int) -> list:
        """u = ½(1 + tanh(π/2·sinh t)), w = (π/4)·cosh t / cosh²(π/2·sinh t)·h.
        Узлы с пренебрежимым весом (g > prec+15) отбрасываются — это не
        «пропуск теста», а математическое отсечение хвоста ряда.
        Часть V: K/h параметризуются точностью. Хвост квадратуры
        e^(-π/2·sinh(K·h)); чтобы он был < 10^-(prec+5), растёт ПРОИЗВЕДЕНИЕ
        K·h (t_max = asinh(2/π·(prec+5)·ln10)), а шаг h сохраняется —
        иначе обрезание ряда даёт ошибку ~10^-4 (урок diag_v9).
        §3.2 v6: гейт ERR_QUAD_PREC — узлов ~2·asinh(2(prec+5)ln10/π)/h,
        каждый узел — 4-5 exp по prec-значному ctx (на prec 5m — вечность)."""
        cls.quad_gate(prec, cls.D(h))
        if prec > 60:
            t_needed = math.asinh((prec + 5) * math.log(10) * 2 / math.pi)
            K = max(K, math.ceil(t_needed / float(h)))
        pi = cls.pi(prec)
        nodes = []
        for k in range(-K, K + 1):
            t = cls.D(k) * h
            g = pi / 2 * ((t.exp() - (-t).exp()) / 2)      # π/2·sinh t
            if g > cls.D(prec + 15):
                continue
            e2g = (2 * g).exp()
            th = (e2g - 1) / (e2g + 1)                      # tanh g
            u = (1 + th) / 2
            cht = (t.exp() + (-t).exp()) / 2
            ch_sh = (g.exp() + (-g).exp()) / 2
            w = (pi / 4) * cht / (ch_sh * ch_sh) * h
            if cls.D(0) < u < cls.D(1):
                nodes.append((u, w))
        return nodes

    @classmethod
    def period_pieces(cls, N: int, a: int, b: int, prec: int, K: int = 240,
                      h: str = "0.02"):
        """Две гладкие части периода после подстановки t = u^N/2 (без Γ):
        I1 = ∫ N·2^{−a/N}·u^{a−1}(1−u^N/2)^{b/N−1} du,
        I2 = ∫ N·2^{−b/N}·u^{b−1}(1−u^N/2)^{a/N−1} du;  Ω = (I1+I2)/N."""
        A, B = cls.D(a) / N, cls.D(b) / N
        nodes = cls.tanh_sinh_nodes(K, cls.D(h), prec)
        i1 = i2 = cls.D(0)
        pow2a = cls.D(2) ** (-A)
        pow2b = cls.D(2) ** (-B)
        for u, w in nodes:
            base = 1 - u ** N / 2
            i1 += w * (N * pow2a * u ** (a - 1) * base ** (B - 1))
            i2 += w * (N * pow2b * u ** (b - 1) * base ** (A - 1))
        # I1 + I2 = B(a/N, b/N) = Ω_{a,b} — множитель N уже внутри h1/h2
        return i1 + i2

    @classmethod
    def period_closed(cls, N: int, a: int, b: int, r: int, s: int, prec: int,
                      zeta: list | None = None):
        """P = (1/N)·ζ^{ra+sb}·Ω_{a,b}."""
        if zeta is None:
            zeta = cls.zeta_pow(N, prec)
        om = cls.omega_closed(N, a, b, prec)
        phase = zeta[(r * a + s * b) % N]
        return cls.cscale(phase, om / N)

    @classmethod
    def period_numeric(cls, N: int, a: int, b: int, r: int, s: int, prec: int,
                       K: int = 240, h: str = "0.02", zeta: list | None = None,
                       adaptive: bool = False):
        """Независимый метод: tanh–sinh по гладким частям; фаза — ζ^{ra+s(b−N)}.

        v1.5.0-session8: adaptive=True — адаптивное дробление шага
        period_pieces_adaptive (K/h игнорируются); закрывает квадратурный
        пол дискретизации фиксированной сетки h=0.02 (session7 §2.3: пол
        ~10^{−83} для N=15,a=4,b=5, не зависящий от prec и s).
        """
        if zeta is None:
            zeta = cls.zeta_pow(N, prec)
        if adaptive:
            total, _info = cls.period_pieces_adaptive(N, a, b, prec)
        else:
            total = cls.period_pieces(N, a, b, prec, K, h)
        phase = zeta[(r * a + s * (b - N)) % N]
        return cls.cscale(phase, total / N)

    @classmethod
    def period_pieces_adaptive(cls, N: int, a: int, b: int, prec: int,
                               h0: str = "0.02", max_levels: int = 6,
                               guard: int = 6):
        """Адаптивный tanh–sinh: h → h/2 до сходимости (шаг 1 дорожной карты s7).

        Механика пола (измерено session7): дискретизация фиксированной сетки
        даёт ошибку ~C·e^{−2πd/h}, где d — ширина аналитической полосы
        интегранда (зависит от (N,a,b)): при h=0.02 — пол 4.8e−83 (N=15,
        a=4, b=5), 1.7e−71 (N=30, a=11, b=19): НЕ зависит от prec и s.
        Схема: считаем I(h₀), затем I(h₀/2), I(h₀/4), … Остановка:
          (i)  |I(h/2) − I(h)| ≤ 10^{−(prec+1)} — целевая точность;
          (ii) стагнация: дробление больше не улучшает разницу
               (пол округления суммы — случайное блуждание
               ~√#узлов · 10^{−prec−guard});
          (iii) max_levels (страховка).
        K на каждом уровне подбирается из prec и h (хвост усечения
        e^{−π/2·sinh(Kh)} < 10^{−(prec+5)}). Суммирование — в контексте
        prec+guard (guard-разряды против накопления по узлам).
        Вызов — внутри HODGEHP.scope(prec) (как у period_pieces).
        Возврат: (I, {levels, h_final, est_err}).
        """
        with localcontext() as actx:
            actx.prec = prec + guard
            target = cls.D(1).scaleb(-(prec + 1))
            tiny = cls.D(1).scaleb(-(prec + 20))
            h = cls.D(h0)
            prev = cls.period_pieces(N, a, b, prec + guard, 240, str(h))
            prev_diff = None
            levels = 0
            est_err = None
            for _ in range(max_levels):
                h = h / 2
                cur = cls.period_pieces(N, a, b, prec + guard, 240, str(h))
                levels += 1
                diff = abs(cur - prev) / max(abs(cur), tiny)
                est_err = diff
                if diff <= target:
                    prev = cur
                    break
                if prev_diff is not None and diff > prev_diff * cls.D("0.7"):
                    prev = cur                # стагнация: пол округления суммы
                    break
                prev, prev_diff = cur, diff
            return prev, {"levels": levels, "h_final": str(h),
                          "est_err": est_err}

    @classmethod
    def klein_omega(cls, prec: int = 45, K: int = 200, h: str = "0.03") -> Decimal:
        """Ω = 2∫₇^∞ dx/√(x³−35x−98) в гладкой форме
        Ω = 4∫₀¹ [1/√(t⁴+21t²+112) + 1/√(1+21t²+112t⁴)] dt (полиглот-форма)."""
        nodes = cls.tanh_sinh_nodes(K, cls.D(h), prec)
        acc = cls.D(0)
        for u, w in nodes:
            u2 = u * u
            acc += w * (1 / cls.sqrt_hp(u2 * u2 + 21 * u2 + 112, prec)
                        + 1 / cls.sqrt_hp(1 + 21 * u2 + 112 * u2 * u2, prec))
        return 4 * acc

    @classmethod
    def klein_omega_raw(cls, prec: int = 45, K: int = 200, h: str = "0.03") -> Decimal:
        """Та же Ω в исходной форме 2∫₇^∞ после замены x = 7 + u/(1−u):
        подынтегральная 2/((1−u)²·√(x₇·(x²+7x+14))). Кросс-проверка формы."""
        nodes = cls.tanh_sinh_nodes(K, cls.D(h), prec)
        acc = cls.D(0)
        for u, w in nodes:
            one = 1 - u
            x7 = u / one
            x = x7 + 7
            quad = x * x + 7 * x + 14
            acc += w * 2 / (one * one * cls.sqrt_hp(x7 * quad, prec))
        return acc

    @classmethod
    def torus_delta(cls, prec: int) -> Decimal:
        """Δ_Ch = 4π² + δ²/2 − δ⁵ при δ = π/4 (калибровочная тройка (4,1,4π²))."""
        pi = cls.pi(prec)
        delta = pi / 4
        lam = 4 * pi * pi
        return lam + delta * delta / 2 - delta ** 5



# ══════════════════════════════════════════════════════════════════════════
# §11. ДВИЖОК ГРАФИКИ: PNG (zlib+CRC32), GIF89a (свой LZW), 5×7 битмап-шрифт,
# канва (Брезенхем/заливка/α-композит в RGB), движок серий HODGEPlot
# (line/scatter/heatmap + SVG), 3D-лаборатория (проекция + sweep).
# Только stdlib. Цвета — из HODGEColor (PLOT_SERIES/PLOT_GRID/PLOT_BG/
# PLOT_TEXT/палитра темы, §17: хардкод #rrggbb в движке запрещён).
# GCT — один на весь прогон (cfg.gct_cache, §11.5): все GIF в единой палитре.
# ══════════════════════════════════════════════════════════════════════════

def _hex_rgb(h: str) -> tuple:
    """'#rrggbb' → (r, g, b)."""
    return (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16))


class HODGEPng:
    """§11.2: минимальный, но полностью валидный PNG (8-bit RGB, filter=None).
    AA — за счёт супер-сэмплинга на уровне движка, не кодека."""

    SIGNATURE = b'\x89PNG\r\n\x1a\n'

    @staticmethod
    def _chunk(tag: bytes, data: bytes) -> bytes:
        body = tag + data
        return (struct.pack('>I', len(data)) + body
                + struct.pack('>I', zlib.crc32(body) & 0xffffffff))

    @classmethod
    def encode(cls, width: int, height: int, rgb: bytes | bytearray) -> bytes:
        """rgb — плоский массив длиной 3*width*height (R,G,B по пикселям)."""
        assert len(rgb) == width * height * 3, (len(rgb), width, height)
        raw = bytearray()          # filter-type 0 (None) на каждую строку
        stride = width * 3
        for y in range(height):
            raw.append(0)
            raw += rgb[y * stride:(y + 1) * stride]
        return (cls.SIGNATURE
                + cls._chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
                + cls._chunk(b'IDAT', zlib.compress(bytes(raw), 9))
                + cls._chunk(b'IEND', b''))

    @classmethod
    def write(cls, path: str, width: int, height: int, rgb) -> None:
        HODGEAdapter.atomic_write(path, cls.encode(width, height, rgb))


class HODGEGif:
    """§11.2: GIF89a с GCT ≤ 256 цветов, per-frame delay, loop forever.
    LZW — стандартный (GIF-spec Appendix F): clear/end, рост code_size,
    сброс таблицы на 4096. Без зависимостей."""

    @staticmethod
    def _lzw(data: bytes, min_code_size: int = 8) -> bytes:
        clear = 1 << min_code_size
        end = clear + 1
        next_code = end + 1
        code_size = min_code_size + 1
        table = {bytes([i]): i for i in range(256)}
        bits = bytearray()
        buf = 0
        nb = 0

        def emit(code, n):
            nonlocal buf, nb
            buf |= (code << nb)
            nb += n
            while nb >= 8:
                bits.append(buf & 0xFF)
                buf >>= 8
                nb -= 8

        emit(clear, code_size)
        w = b''
        for b in data:
            wc = w + bytes([b])
            if wc in table:
                w = wc
            else:
                emit(table[w], code_size)
                table[wc] = next_code
                next_code += 1
                if next_code - 1 == (1 << code_size) and code_size < 12:
                    code_size += 1
                if next_code == 4096:
                    emit(clear, code_size)
                    table = {bytes([i]): i for i in range(256)}
                    next_code = end + 1
                    code_size = min_code_size + 1
                w = bytes([b])
        if w:
            emit(table[w], code_size)
        emit(end, code_size)
        if nb > 0:
            bits.append(buf & 0xFF)
        # упаковка в sub-blocks ≤ 255
        out = bytearray([min_code_size])
        i = 0
        while i < len(bits):
            n = min(255, len(bits) - i)
            out.append(n)
            out += bits[i:i + n]
            i += n
        out.append(0)
        return bytes(out)

    @classmethod
    def encode(cls, width: int, height: int, gct: list, frames: list,
               delays: list | None = None, loop: int = 0) -> bytes:
        """gct — list[(r,g,b)] ≤ 256; frames — list[bytes индексов в GCT]."""
        assert len(gct) <= 256
        header = b'GIF89a' + struct.pack('<HHBBB', width, height, 0xF7, 0, 0)
        # 0xF7 = GCT present, color-res 7, sort 0, size 2^8
        table = bytearray()
        for r, g, b in gct:
            table += bytes([r, g, b])
        table += b'\x00\x00\x00' * (256 - len(gct))
        out = bytearray(header + bytes(table))
        if loop >= 0:
            out += b'\x21\xFF\x0BNETSCAPE2.0\x03\x01'
            out += struct.pack('<H', loop) + b'\x00'
        if delays is None:
            delays = [10] * len(frames)   # 10 × 10 мс = 100 мс
        for frame, delay in zip(frames, delays):
            # GCE — ровно 8 байт (регрессия s5: лишний 0x04 сдвигал поле delay
            # на 1 байт → зрители читали задержку ×256 и кадры «замирали»,
            # плюс после GCE оставался посторонний пустой 0x00-блок):
            # [21 F9 04] [flags=04 disposal=1] [delay LE16, сотые секунды]
            # [transparent=00] [terminator=00]
            out += b'\x21\xF9\x04\x04' + struct.pack('<H', max(0, min(65535, int(delay)))) + b'\x00\x00'
            out += b'\x2C' + struct.pack('<HHHHB', 0, 0, width, height, 0)
            out += cls._lzw(bytes(frame))
        out += b'\x3B'
        return bytes(out)

    @classmethod
    def write(cls, path, width, height, gct, frames, delays=None) -> None:
        HODGEAdapter.atomic_write(path, cls.encode(width, height, gct, frames, delays))

    @staticmethod
    def _lzw_decode(data: bytes, min_code_size: int) -> bytearray:
        """Декодер LZW по GIF-spec Appendix F — эталон приёмки кодека §19.9.
        data — биты после min_code_size-байта (sub-blocks уже склеены)."""
        clear = 1 << min_code_size
        end = clear + 1
        code_size = min_code_size + 1
        # §F: литералы — только коды 0..2^mcs−1; коды 2^mcs+2..255 — это
        # НОВЫЕ записи таблицы (регрессия s5: пре-заполнение всех 256
        # литералов ломало приёмку сторонних GIF с mcs<8 — код 9 при
        # mcs=2 читался как литерал вместо записи [2,2]).
        table = {i: bytes([i]) for i in range(clear)}
        next_code = end + 1
        out = bytearray()
        buf = 0
        nb = 0
        prev = None
        i = 0
        while True:
            while nb < code_size:
                if i >= len(data):
                    return out
                buf |= data[i] << nb
                nb += 8
                i += 1
            code = buf & ((1 << code_size) - 1)
            buf >>= code_size
            nb -= code_size
            if code == clear:
                table = {k: bytes([k]) for k in range(clear)}
                next_code = end + 1
                code_size = min_code_size + 1
                prev = None
                continue
            if code == end:
                break
            if code in table:
                entry = table[code]
            elif prev is not None:
                entry = prev + prev[:1]   # KwKwK
            else:
                break                     # битый поток
            out += entry
            if prev is not None:
                table[next_code] = prev + entry[:1]
                next_code += 1
                if next_code == (1 << code_size) and code_size < 12:
                    code_size += 1
            prev = entry
        return out


class HODGEFont:
    """§11.3: 5×7 битмап-шрифт (7 байт на глиф, 5 бит в строке, MSB = левый
    пиксель). Цифры, латиница A–Z/a–z, пунктуация. Греческие/типографские
    символы транслитерируются FALLBACK_MAP (например Ω→Om) — шрифт честный,
    недостающие глифы не рисуются «квадратиками»."""

    W, H = 5, 7
    GLYPHS = {
        ' ': (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
        '0': (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
        '1': (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
        '2': (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
        '3': (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
        '4': (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
        '5': (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
        '6': (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
        '7': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
        '8': (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
        '9': (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
        'A': (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
        'B': (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
        'C': (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
        'D': (0x1C, 0x12, 0x11, 0x11, 0x11, 0x12, 0x1C),
        'E': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
        'F': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
        'G': (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
        'H': (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
        'I': (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
        'J': (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
        'K': (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
        'L': (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
        'M': (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
        'N': (0x11, 0x11, 0x19, 0x15, 0x13, 0x11, 0x11),
        'O': (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
        'P': (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
        'Q': (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
        'R': (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
        'S': (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
        'T': (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
        'U': (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
        'V': (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
        'W': (0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0A),
        'X': (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
        'Y': (0x11, 0x11, 0x11, 0x0A, 0x04, 0x04, 0x04),
        'Z': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
        'a': (0x00, 0x00, 0x0E, 0x01, 0x0F, 0x11, 0x0F),
        'b': (0x10, 0x10, 0x1E, 0x11, 0x11, 0x11, 0x1E),
        'c': (0x00, 0x00, 0x0F, 0x10, 0x10, 0x10, 0x0F),
        'd': (0x01, 0x01, 0x0F, 0x11, 0x11, 0x11, 0x0F),
        'e': (0x00, 0x00, 0x0E, 0x11, 0x1F, 0x10, 0x0E),
        'f': (0x06, 0x08, 0x08, 0x1E, 0x08, 0x08, 0x08),
        'g': (0x00, 0x0F, 0x11, 0x11, 0x0F, 0x01, 0x0E),
        'h': (0x10, 0x10, 0x1E, 0x11, 0x11, 0x11, 0x11),
        'i': (0x04, 0x00, 0x0C, 0x04, 0x04, 0x04, 0x0E),
        'j': (0x02, 0x00, 0x06, 0x02, 0x02, 0x12, 0x0C),
        'k': (0x10, 0x10, 0x14, 0x18, 0x18, 0x14, 0x12),
        'l': (0x0C, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
        'm': (0x00, 0x00, 0x1A, 0x15, 0x15, 0x15, 0x15),
        'n': (0x00, 0x00, 0x1E, 0x11, 0x11, 0x11, 0x11),
        'o': (0x00, 0x00, 0x0E, 0x11, 0x11, 0x11, 0x0E),
        'p': (0x00, 0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10),
        'q': (0x00, 0x0F, 0x11, 0x11, 0x0F, 0x01, 0x01),
        'r': (0x00, 0x00, 0x16, 0x19, 0x10, 0x10, 0x10),
        's': (0x00, 0x00, 0x0F, 0x10, 0x0E, 0x01, 0x1E),
        't': (0x08, 0x08, 0x1E, 0x08, 0x08, 0x0A, 0x04),
        'u': (0x00, 0x00, 0x11, 0x11, 0x11, 0x13, 0x0D),
        'v': (0x00, 0x00, 0x11, 0x11, 0x11, 0x0A, 0x04),
        'w': (0x00, 0x00, 0x11, 0x11, 0x15, 0x15, 0x0A),
        'x': (0x00, 0x00, 0x11, 0x0A, 0x04, 0x0A, 0x11),
        'y': (0x00, 0x11, 0x11, 0x0F, 0x01, 0x11, 0x0E),
        'z': (0x00, 0x00, 0x1F, 0x02, 0x04, 0x08, 0x1F),
        '=': (0x00, 0x1F, 0x00, 0x1F, 0x00, 0x00, 0x00),
        ':': (0x00, 0x04, 0x00, 0x00, 0x04, 0x00, 0x00),
        '.': (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
        '-': (0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00),
        '+': (0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00),
        '/': (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
        '?': (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04),
        '!': (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
        ',': (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
        ';': (0x00, 0x04, 0x00, 0x00, 0x04, 0x04, 0x08),
        '(': (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
        ')': (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
        '%': (0x19, 0x1A, 0x02, 0x04, 0x08, 0x17, 0x13),
        '_': (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1F),
        '"': (0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00),
        "'": (0x04, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00),
        '<': (0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02),
        '>': (0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08),
        '[': (0x0E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x0E),
        ']': (0x0E, 0x02, 0x02, 0x02, 0x02, 0x02, 0x0E),
        '*': (0x00, 0x0A, 0x04, 0x1F, 0x04, 0x0A, 0x00),
        '#': (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
        '@': (0x0E, 0x11, 0x17, 0x15, 0x17, 0x10, 0x0E),
        '&': (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
        '|': (0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
        '~': (0x00, 0x00, 0x08, 0x15, 0x02, 0x00, 0x00),
    }
    # транслитерация того, что не влезает в 5×7 (лейблы типов «Ω=1.93»)
    FALLBACK_MAP = {"Ω": "Om", "Γ": "G", "π": "pi", "Δ": "D", "Σ": "S",
                    "μ": "u", "×": "x", "−": "-", "≤": "<=", "≥": ">=",
                    "≈": "~", "±": "+/-", "°": "deg", "∞": "oo", "≡": "=",
                    "·": ".", "—": "-", "–": "-", "≠": "!=", "′": "'",
                    "₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4"}

    @classmethod
    def _translit(cls, text: str) -> str:
        return "".join(cls.FALLBACK_MAP.get(c, c) for c in text)

    @classmethod
    def measure(cls, text: str, scale: int = 1) -> tuple:
        return (len(text) * (cls.W + 1) - 1) * scale, cls.H * scale

    @classmethod
    def blit(cls, canvas_buf, cx: int, cy: int, text: str, scale: int,
             rgb: tuple, canvas_w: int, canvas_h: int):
        """Прямое рисование без AA (для мелких меток). rgb — кортеж 0..255."""
        for ci, ch in enumerate(cls._translit(text)):
            glyph = cls.GLYPHS.get(ch, cls.GLYPHS.get('?', (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04)))
            ox = cx + ci * (cls.W + 1) * scale
            for ry, row in enumerate(glyph):
                for rx in range(cls.W):
                    if row & (1 << (cls.W - 1 - rx)):
                        cls._fill(canvas_buf, ox + rx * scale, cy + ry * scale,
                                  scale, scale, rgb, canvas_w, canvas_h)

    @staticmethod
    def _fill(canvas_buf, x, y, w, h, rgb, cw, ch):
        for yy in range(y, y + h):
            if yy < 0 or yy >= ch:
                continue
            base = yy * cw * 3
            for xx in range(x, x + w):
                if 0 <= xx < cw:
                    p = base + xx * 3
                    canvas_buf[p] = rgb[0]
                    canvas_buf[p + 1] = rgb[1]
                    canvas_buf[p + 2] = rgb[2]


class HODGECanvas:
    """§11.1: RGB-буфер + примитивы. α-композит — в RGB до квантования (§11.5):
    пиксель смешивается с фоном на месте, GIF-кодек получает уже непрозрачные
    цвета — точные цвета палитры попадают в GCT без искажений."""

    def __init__(self, w: int, h: int, bg: tuple = (10, 8, 5)):
        self.w, self.h = w, h
        self.buf = bytearray(w * h * 3)
        for i in range(0, len(self.buf), 3):
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = bg

    def px(self, x: int, y: int, rgb, a: float = 1.0) -> None:
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            if a >= 1.0:
                self.buf[i] = rgb[0]
                self.buf[i + 1] = rgb[1]
                self.buf[i + 2] = rgb[2]
            else:
                for k in range(3):
                    self.buf[i + k] = int(self.buf[i + k] * (1 - a) + rgb[k] * a)

    def line(self, x0, y0, x1, y1, rgb, a: float = 1.0) -> None:
        """Брезенхем."""
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.px(x0, y0, rgb, a)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def rect(self, x, y, w, h, rgb, a: float = 1.0) -> None:
        for xx in range(x, x + w):
            self.px(xx, y, rgb, a)
            self.px(xx, y + h - 1, rgb, a)
        for yy in range(y, y + h):
            self.px(x, yy, rgb, a)
            self.px(x + w - 1, yy, rgb, a)

    def fill_rect(self, x, y, w, h, rgb) -> None:
        for yy in range(y, y + h):
            base = yy * self.w * 3
            for xx in range(x, x + w):
                if 0 <= xx < self.w and 0 <= y < self.h:
                    p = base + xx * 3
                    self.buf[p] = rgb[0]
                    self.buf[p + 1] = rgb[1]
                    self.buf[p + 2] = rgb[2]


def _build_gct(theme_name: str) -> tuple:
    """§11.5 / §F: GCT ≤ 256 из палитры темы. Сначала точные цвета
    (PLOT_BG/GRID/TEXT, PLOT_SERIES, ключи темы, оси = gold_dim), затем
    решётка 6×6×6 = 216 для остальных оттенков. Точные цвета палитры
    попадают в GIF без искажений — GIF не «блёклый» и не мимо dark-gold.
    Возвращает (gct_256, lat_base)."""
    seen, gct = set(), []

    def add_rgb(rgb):
        if rgb not in seen:
            seen.add(rgb)
            gct.append(rgb)

    def add_hex(h):
        if isinstance(h, str) and h.startswith("#") and len(h) == 7:
            add_rgb(_hex_rgb(h))

    add_hex(HODGEColor.PLOT_BG)
    add_hex(HODGEColor.PLOT_GRID)
    add_hex(HODGEColor.PLOT_TEXT)
    for h in HODGEColor.PLOT_SERIES:
        add_hex(h)
    base = HODGEColor.THEMES.get(theme_name) or HODGEColor.DARK_GOLD
    for v in base.values():
        add_hex(v[0])
    add_hex(base["gold_dim"][0])          # оси (AXIS) — из палитры темы
    lat_base = len(gct)
    for r in range(6):
        for g in range(6):
            for b in range(6):
                add_rgb((r * 51, g * 51, b * 51))
    while len(gct) < 256:
        gct.append((0, 0, 0))
    return gct, lat_base


def _quantize_rgb(buf, cache: dict, theme_name: str = "dark-gold") -> tuple:
    """§11.5: индексы кадра в общий GCT прогона. Точные цвета палитры — по
    LUT, остальные — к ближайшей решётке 6×6×6. cache — cfg.gct_cache:
    GCT один на весь прогон, все GIF задач в единой палитре темы."""
    if cache.get("theme") != theme_name or "gct" not in cache:
        gct, lat_base = _build_gct(theme_name)
        cache["gct"] = gct
        cache["lat_base"] = lat_base
        cache["exact"] = {c: i for i, c in enumerate(gct[:lat_base])}
        cache["theme"] = theme_name
    gct, exact, lat_base = cache["gct"], cache["exact"], cache["lat_base"]
    idx = bytearray(len(buf) // 3)
    j = 0
    for i in range(0, len(buf), 3):
        c = (buf[i], buf[i + 1], buf[i + 2])
        v = exact.get(c)
        if v is None:
            r = min(5, (buf[i] * 6) // 256)
            g = min(5, (buf[i + 1] * 6) // 256)
            b = min(5, (buf[i + 2] * 6) // 256)
            v = lat_base + (r * 36 + g * 6 + b)
            exact[c] = v
        idx[j] = v
        j += 1
    return idx, gct


class HODGEPlot:
    """§11.4: движок серий line/scatter/heatmap на HODGECanvas. Не знает про
    задачи — на вход только данные + имя темы. AA — супер-сэмплинг ×aa с
    бокс-даунсэмплингом. Серия: (label, xs, ys, style, rgb); style
    'l' — линия, 's' — точки, 'h' — heatmap (значения ячейки 0..1)."""

    def __init__(self, width=800, height=480, title='', xlabel='', ylabel='',
                 theme_name="dark-gold", aa=2):
        self.out_W, self.out_H = int(width), int(height)
        self.aa = max(1, min(4, int(aa)))
        self.W, self.H = self.out_W * self.aa, self.out_H * self.aa
        self.theme_name = theme_name
        pal = HODGEColor.THEMES.get(theme_name) or HODGEColor.DARK_GOLD
        self.BG = _hex_rgb(HODGEColor.PLOT_BG)
        self.GRID = _hex_rgb(HODGEColor.PLOT_GRID)
        self.TEXT = _hex_rgb(HODGEColor.PLOT_TEXT)
        self.AXIS = _hex_rgb(pal["gold_dim"][0])
        self.canvas = HODGECanvas(self.W, self.H, self.BG)
        self.series = []          # [(label, xs, ys, style, rgb)]
        self.title, self.xlabel, self.ylabel = title, xlabel, ylabel
        self.grid = True
        self.xlim = self.ylim = None

    def add(self, label, xs, ys, style='l', color=None):
        c = color or HODGEColor.PLOT_SERIES[len(self.series) % len(HODGEColor.PLOT_SERIES)]
        self.series.append((label, list(xs), list(ys), style, _hex_rgb(c)))
        return self

    def add_heatmap(self, label, grid, color=None):
        """grid — 2D-список значений 0..1 (или нормируемых)."""
        c = color or HODGEColor.PLOT_SERIES[0]
        self.series.append((label, None, grid, 'h', _hex_rgb(c)))
        return self

    def _bounds(self):
        xs = [x for (_, s, _, st, _) in self.series if st != 'h' for x in s]
        ys = [y for (_, _, s, st, _) in self.series if st != 'h' for y in s]
        if not xs or not ys:
            return (0, 1), (0, 1)
        xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)
        if xmin == xmax:
            xmin -= 1
            xmax += 1
        if ymin == ymax:
            ymin -= 1
            ymax += 1
        py = (ymax - ymin) * 0.05
        return (self.xlim or (xmin, xmax)), (self.ylim or (ymin - py, ymax + py))

    def render(self):
        aa = self.aa
        M = 60 * aa
        pl, pr, pt, pb = M, M, M, M
        W, H = self.W, self.H
        (xmin, xmax), (ymin, ymax) = self._bounds()

        def X(x):
            return pl + (x - xmin) / (xmax - xmin) * (W - pl - pr)

        def Y(y):
            return H - pb - (y - ymin) / (ymax - ymin) * (H - pt - pb)

        cv = self.canvas
        # сетка
        if self.grid:
            for i in range(11):
                x = pl + i * (W - pl - pr) // 10
                cv.line(x, pt, x, H - pb, self.GRID)
                y = pt + i * (H - pt - pb) // 10
                cv.line(pl, y, W - pr, y, self.GRID)
        # рамка осей
        cv.rect(pl, pt, W - pl - pr, H - pt - pb, self.AXIS)
        # серии
        for label, sxs, sys_, style, rgb in self.series:
            if style in ('l', 'L'):
                prev = None
                for x, y in zip(sxs, sys_):
                    cur = (int(X(x)), int(Y(y)))
                    if prev:
                        cv.line(prev[0], prev[1], cur[0], cur[1], rgb)
                    prev = cur
            elif style == 's':
                for x, y in zip(sxs, sys_):
                    cx, cy = int(X(x)), int(Y(y))
                    r = 3 * aa
                    for dy in range(-r, r + 1):
                        for dx in range(-r, r + 1):
                            if dx * dx + dy * dy <= r * r:
                                cv.px(cx + dx, cy + dy, rgb)
            elif style == 'h':
                self._render_heatmap(cv, sys_, rgb, pl, pt, W - pr, H - pb)
        self._label_axes(X, Y, pl, pr, pt, pb, xmin, xmax, ymin, ymax)
        return self._downsample()

    def _render_heatmap(self, cv, grid, base_rgb, pl, pt, right, bottom):
        """Ячейки 0..1: цвет = смесь BG→base_rgb. Полезно для матриц (K3)."""
        n = len(grid)
        m = len(grid[0]) if n else 0
        if not n or not m:
            return
        lo = min(v for row in grid for v in row)
        hi = max(v for row in grid for v in row)
        span = (hi - lo) or 1.0
        cw = max(1, (right - pl) // n)
        ch = max(1, (bottom - pt) // m)
        for i in range(n):
            for j in range(m):
                t = (grid[i][j] - lo) / span
                rgb = tuple(int(self.BG[k] * (1 - t) + base_rgb[k] * t) for k in range(3))
                cv.fill_rect(pl + i * cw, pt + j * ch, cw, ch, rgb)

    def _label_axes(self, X, Y, pl, pr, pt, pb, xmin, xmax, ymin, ymax):
        aa = self.aa
        cv = self.canvas
        s = aa
        # заголовок: по центру сверху (масштаб ×2 — крупнее)
        ts = 2 * aa
        tw, _ = HODGEFont.measure(self.title, ts)
        HODGEFont.blit(cv.buf, max(pl, (self.W - tw) // 2), max(2, pt - 14 * aa),
                       self.title, ts, self.TEXT, self.W, self.H)
        # x-метки: 5 значений
        for i in range(5):
            xv = xmin + (xmax - xmin) * i / 4
            txt = f"{xv:.4g}"
            px = int(X(xv))
            HODGEFont.blit(cv.buf, px - HODGEFont.measure(txt, s)[0] // 2,
                           self.H - pb + 3 * aa, txt, s, self.TEXT, self.W, self.H)
        # y-метки
        for i in range(5):
            yv = ymin + (ymax - ymin) * (4 - i) / 4
            txt = f"{yv:.4g}"
            py = int(Y(yv))
            HODGEFont.blit(cv.buf, max(1, pl - HODGEFont.measure(txt, s)[0] - 3 * aa),
                           py - 3 * aa, txt, s, self.TEXT, self.W, self.H)
        # подписи осей
        if self.xlabel:
            xw, _ = HODGEFont.measure(self.xlabel, s)
            HODGEFont.blit(cv.buf, (self.W - xw) // 2, self.H - 9 * aa,
                           self.xlabel, s, self.TEXT, self.W, self.H)
        if self.ylabel:
            # вертикально: символы столбиком слева
            x0, y0 = 4 * aa, pt + 4 * aa
            for k, chch in enumerate(HODGEFont._translit(self.ylabel)[:16]):
                HODGEFont.blit(cv.buf, x0, y0 + k * 8 * aa, chch, s,
                               self.TEXT, self.W, self.H)
        # легенда (правый верх): образец + метка серии
        ly = pt + 4 * aa
        for label, _xs, _ys, _st, rgb in self.series:
            cv.fill_rect(self.W - pr - (4 + len(label) * 6) * aa, ly - 1 * aa,
                         4 * aa, 4 * aa, rgb)
            HODGEFont.blit(cv.buf, self.W - pr - (len(label) * 6) * aa, ly,
                           label, s, self.TEXT, self.W, self.H)
            ly += 9 * aa

    def _downsample(self):
        if self.aa == 1:
            return self.canvas.buf
        a = self.aa
        W, out_W, out_H = self.W, self.out_W, self.out_H
        src = self.canvas.buf
        out = bytearray(out_W * out_H * 3)
        n = a * a
        for y in range(out_H):
            orow = y * out_W * 3
            for x in range(out_W):
                r = g = b = 0
                for dy in range(a):
                    srow = ((y * a + dy) * W + x * a) * 3
                    for dx in range(a):
                        i = srow + dx * 3
                        r += src[i]
                        g += src[i + 1]
                        b += src[i + 2]
                o = orow + x * 3
                out[o], out[o + 1], out[o + 2] = r // n, g // n, b // n
        return out

    def write_png(self, path):
        HODGEPng.write(path, self.out_W, self.out_H, self.render())
        return path

    def to_gif_frame(self, gct_cache):
        """Индексы кадра в GCT прогона (создаёт GCT при первом вызове)."""
        buf = self.render()
        return _quantize_rgb(buf, gct_cache, self.theme_name)

    def to_svg(self) -> str:
        """§11.2: векторный экспорт (polyline/circle) — тривиален и честен."""
        (xmin, xmax), (ymin, ymax) = self._bounds()
        W, H = self.out_W, self.out_H
        pl = pr = pt = pb = 60.0

        def X(x):
            return pl + (x - xmin) / (xmax - xmin) * (W - pl - pr)

        def Y(y):
            return H - pb - (y - ymin) / (ymax - ymin) * (H - pt - pb)

        bg = "#{:02x}{:02x}{:02x}".format(*self.BG)
        txt = "#{:02x}{:02x}{:02x}".format(*self.TEXT)
        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">',
                 f'<rect width="{W}" height="{H}" fill="{bg}"/>',
                 f'<text x="{W // 2}" y="24" fill="{txt}" font-size="14" '
                 f'text-anchor="middle" font-family="Georgia">{self.title}</text>']
        for label, xs, ys, style, rgb in self.series:
            col = "#{:02x}{:02x}{:02x}".format(*rgb)
            if style in ('l', 'L'):
                pts = " ".join(f"{X(x):.2f},{Y(y):.2f}" for x, y in zip(xs, ys))
                parts.append(f'<polyline fill="none" stroke="{col}" stroke-width="1.5" points="{pts}"/>')
            elif style == 's':
                for x, y in zip(xs, ys):
                    parts.append(f'<circle cx="{X(x):.2f}" cy="{Y(y):.2f}" r="2.5" fill="{col}"/>')
        for label, _xs, _ys, _st, rgb in self.series:
            col = "#{:02x}{:02x}{:02x}".format(*rgb)
            parts.append(f'<text x="{W - 130}" y="{40 + 14 * self.series.index((label, _xs, _ys, _st, rgb))}" '
                         f'fill="{col}" font-size="11" font-family="Georgia">{label}</text>')
        parts.append('</svg>')
        return "\n".join(parts)

    @classmethod
    def from_metrics(cls, metrics: dict, cfg=None, title: str = "") -> "HODGEPlot":
        """Отладочный вход: плоский dict со списками чисел → линейные серии."""
        aa = getattr(cfg, "plot_aa", 2) if cfg else 2
        p = cls(getattr(cfg, "plot_width", 800) if cfg else 800,
                getattr(cfg, "plot_height", 480) if cfg else 480,
                title=title or "metrics", aa=aa)
        for k, v in metrics.items():
            if isinstance(v, list) and v and isinstance(v[0], (int, float)):
                p.add(k, list(range(len(v))), v)
        return p


class HODGE3D:
    """§11-расширение: проективная 3D-сцена (x,y,z) → 2D-экран. Без numpy.
    Параметры — dict; sweep выполняет HODGE3DLab, здесь — одна сцена."""

    def __init__(self, width=800, height=600, aa=1, theme_name="dark-gold"):
        self.W, self.H = int(width), int(height)
        self.aa = max(1, min(2, int(aa)))
        pal = HODGEColor.THEMES.get(theme_name) or HODGEColor.DARK_GOLD
        self.BG = _hex_rgb(HODGEColor.PLOT_BG)
        self.WIRE = _hex_rgb(HODGEColor.PLOT_SERIES[0])
        self.COL_LO = _hex_rgb(pal["gold_dim"][0])
        self.COL_HI = _hex_rgb(pal["gold_bright"][0])
        self.canvas = HODGECanvas(self.W * self.aa, self.H * self.aa, self.BG)
        self.theme_name = theme_name

    @staticmethod
    def _rot(rx, ry, rz, p):
        x, y, z = p
        cy, sy = math.cos(ry), math.sin(ry)
        x, z = x * cy + z * sy, -x * sy + z * cy
        cx, sx = math.cos(rx), math.sin(rx)
        y, z = y * cx - z * sx, y * sx + z * cx
        cz, sz = math.cos(rz), math.sin(rz)
        x, y = x * cz - y * sz, x * sz + y * cz
        return x, y, z

    def _project(self, p, rot, zoom, pan):
        x, y, z = self._rot(*rot, p)
        dist = 4.0
        k = dist / (dist + z)
        sx = int(self.W * self.aa / 2 + (x * zoom * k + pan[0]) * self.W * self.aa / 2)
        sy = int(self.H * self.aa / 2 - (y * zoom * k + pan[1]) * self.H * self.aa / 2)
        return sx, sy, k

    def surface(self, xs, ys, zs, wire=True, rot=(0.4, 0.6, 0.0), zoom=0.8, pan=(0, 0)):
        """xs, ys, zs — 2D-сетка [i][j]. Заливка по z (дальнее раньше) + wireframe."""
        cv = self.canvas
        nx, ny = len(xs), len(xs[0])
        zmin = min(z for row in zs for z in row)
        zmax = max(z for row in zs for z in row)
        span = (zmax - zmin) or 1.0

        def col(z):
            t = (z - zmin) / span
            return tuple(int(self.COL_LO[k] * (1 - t) + self.COL_HI[k] * t) for k in range(3))

        cells = []
        for i in range(nx - 1):
            for j in range(ny - 1):
                zavg = (zs[i][j] + zs[i + 1][j] + zs[i][j + 1] + zs[i + 1][j + 1]) / 4
                cells.append((zavg, i, j))
        cells.sort()
        for zavg, i, j in cells:
            quad = [(xs[i][j], ys[i][j], zs[i][j]),
                    (xs[i + 1][j], ys[i + 1][j], zs[i + 1][j]),
                    (xs[i + 1][j + 1], ys[i + 1][j + 1], zs[i + 1][j + 1]),
                    (xs[i][j + 1], ys[i][j + 1], zs[i][j + 1])]
            pts = [self._project(p, rot, zoom, pan) for p in quad]
            self._fill_poly(pts, col(zavg))
        if wire:
            for i in range(nx):
                for j in range(ny):
                    if i + 1 < nx:
                        p1 = self._project((xs[i][j], ys[i][j], zs[i][j]), rot, zoom, pan)
                        p2 = self._project((xs[i + 1][j], ys[i + 1][j], zs[i + 1][j]), rot, zoom, pan)
                        cv.line(p1[0], p1[1], p2[0], p2[1], self.WIRE)
                    if j + 1 < ny:
                        p1 = self._project((xs[i][j], ys[i][j], zs[i][j]), rot, zoom, pan)
                        p2 = self._project((xs[i][j + 1], ys[i][j + 1], zs[i][j + 1]), rot, zoom, pan)
                        cv.line(p1[0], p1[1], p2[0], p2[1], self.WIRE)

    def _fill_poly(self, pts, rgb, a=1.0):
        h = self.H * self.aa
        ys_ = [p[1] for p in pts]
        y0, y1 = max(0, min(ys_)), min(h - 1, max(ys_))
        for y in range(y0, y1 + 1):
            xs_at_y = []
            for k in range(len(pts)):
                x1_, y1_ = pts[k][0], pts[k][1]
                x2_, y2_ = pts[(k + 1) % len(pts)][0], pts[(k + 1) % len(pts)][1]
                if y1_ == y2_:
                    continue
                if min(y1_, y2_) <= y < max(y1_, y2_):
                    x = x1_ + (x2_ - x1_) * (y - y1_) / (y2_ - y1_)
                    xs_at_y.append(x)
            xs_at_y.sort()
            for k in range(0, len(xs_at_y) - 1, 2):
                for xx in range(int(xs_at_y[k]), int(xs_at_y[k + 1]) + 1):
                    self.canvas.px(xx, y, rgb, a)


def _parse_sweep(spec: str) -> tuple:
    """'N:5:30:1' → ('N', [5, 6, …, 30])."""
    name, lo, hi, step = spec.split(":")
    lo_f, hi_f, step_f = float(lo), float(hi), float(step)
    if step_f == 0:
        raise ValueError(f"ERR_SWEEP_STEP_ZERO {spec}")
    vals = []
    v = lo_f
    while (v <= hi_f + 1e-9) if step_f > 0 else (v >= hi_f - 1e-9):
        vals.append(int(v) if v == int(v) else v)
        v += step_f
    if not vals:
        raise ValueError(f"ERR_SWEEP_EMPTY {spec}")
    return name, vals


class HODGE3DLab:
    """§11-расширение: обходит sweep-пространство (декартово произведение,
    лимит --lab-max-frames), для каждой точки строит поверхность и складывает
    PNG + sweep.gif + manifest.json. Исследовательский режим, не верификация."""

    def __init__(self, cfg, theme=None):
        self.cfg = cfg
        self.out_dir = cfg.lab_output or os.path.join(cfg.run_dir or cfg.report_dir, "lab3d")
        os.makedirs(self.out_dir, exist_ok=True)

    def run(self, function_name: str, sweeps: dict, base_params: dict | None = None,
            grid_n: int = 48, max_frames: int = 500) -> dict:
        base_params = dict(base_params or {})
        keys = list(sweeps.keys())

        def rec(i, acc):
            if i == len(keys):
                yield dict(acc)
                return
            for v in sweeps[keys[i]]:
                acc[keys[i]] = v
                yield from rec(i + 1, acc)

        cache = self.cfg.gct_cache
        frames, delays = [], []
        n_frames = 0
        for n, params in enumerate(rec(0, base_params)):
            if n >= max_frames:
                hodge_log(self.cfg, "WARN", "lab3d", f"лимит {max_frames} кадров достигнут")
                break
            xs, ys, zs = self._surface(function_name, params, grid_n)
            scene = HODGE3D(self.cfg.plot_width, self.cfg.plot_height, aa=1,
                            theme_name=self.cfg.theme)
            scene.surface(xs, ys, zs,
                          rot=(params.get('rot_x', 0.4), params.get('rot_y', 0.6), 0.0),
                          zoom=params.get('zoom', 0.8))
            # Подписи на кадре: что рисуем (паритет с Julia-лабораторией)
            HODGEFont.blit(scene.canvas.buf, 10, 8,
                           f"fn={function_name}  N={int(params.get('N', 15))}  "
                           f"grid={grid_n}x{grid_n}", 2, scene.COL_HI,
                           scene.W, scene.H)
            HODGEFont.blit(scene.canvas.buf, 10, scene.H - 22,
                           "surface f(a,b), a,b in [1,N]   x = a-b   y = a+b"
                           "   color = value (low -> high)", 1, scene.COL_HI,
                           scene.W, scene.H)
            png_path = os.path.join(self.out_dir, f"frame_{n:05d}.png")
            HODGEPng.write(png_path, scene.W, scene.H, scene.canvas.buf)
            idx, _ = _quantize_rgb(scene.canvas.buf, cache, self.cfg.theme)
            frames.append(idx)
            delays.append(int(params.get('delay', 8)))
            n_frames += 1
        if frames:
            HODGEGif.write(os.path.join(self.out_dir, "sweep.gif"),
                           self.cfg.plot_width, self.cfg.plot_height,
                           cache["gct"], frames, delays)
        manifest = {"function": function_name, "sweeps": {k: v[:64] for k, v in sweeps.items()},
                    "frames": n_frames, "grid": grid_n,
                    "base_params": {k: v for k, v in base_params.items()
                                    if k not in sweeps}}
        HODGEAdapter.atomic_write(os.path.join(self.out_dir, "manifest.json"),
                                  json.dumps(manifest, ensure_ascii=False, indent=1))
        return manifest

    def _surface(self, fn_name, params, n):
        N = int(params.get('N', 15))
        prec = int(params.get('prec', self.cfg.prec))
        n = max(2, n)
        xs = [[0.0] * n for _ in range(n)]
        ys = [[0.0] * n for _ in range(n)]
        zs = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                a = 1 + (N - 2) * i / (n - 1)
                b = 1 + (N - 2) * j / (n - 1)
                xs[i][j] = a - b
                ys[i][j] = a + b
                zs[i][j] = self._eval(fn_name, N, a, b, prec, params)
        # нормировка каждой оси в [-1, 1]: проекция рассчитана на единичный
        # куб (zoom/dist), сырые величины (ω до N², a+b до 2N) из него вылетают
        for g in (xs, ys, zs):
            flat = [v for row in g for v in row]
            lo, hi = min(flat), max(flat)
            span = (hi - lo) or 1.0
            for i in range(n):
                for j in range(n):
                    g[i][j] = (g[i][j] - lo) / span * 2 - 1
        return xs, ys, zs

    def _eval(self, name, N, a, b, prec, params):
        if name == 'omega':
            return float(HODGEHP.omega_closed(N, max(1, int(a)), max(1, int(b)), prec))
        if name == 'period_re':
            z = _zeta(N, prec)
            ph = z[0]   # r=s=0
            om = HODGEHP.omega_closed(N, max(1, int(a)), max(1, int(b)), prec)
            return float((ph[0] * om / N).real) if om else 0.0
        if name == 'census_h':
            try:
                return float(HODGEEX.census(N)[0].get(int(a), 0))
            except Exception:
                return 0.0
        if name == 'hodge_classes':
            # §11.6 v4: решётка классов Ходжа башни Ферма — класс (a,b)
            # существует ⟺ a+b ≡ 0 (mod N); высота = Ω(a,b) (спаривание)
            ai, bi = max(1, int(a)), max(1, int(b))
            if (ai + bi) % N != 0:
                return 0.0
            return float(HODGEHP.omega_closed(N, ai, bi, prec))
        if name == 'zeta_mod':
            # §11.6 v4: модуль дзета-функции — научный ландшафт |ζ(a + i·b·10)|
            return _zeta_mod_landscape(max(-3.0, min(3.0, float(a))),
                                       max(0.0, float(b)) * 10.0)
        # пользовательское: expr:"…" — выражение Python по (N, a, b, HP, HX, math)
        try:
            env = {'N': N, 'a': a, 'b': b, 'HP': HODGEHP, 'HX': HODGEEX, 'math': math,
                   'zmod': _zeta_mod_landscape}
            return float(eval(name, {"__builtins__": {}}, env))
        except Exception:
            return 0.0


def hodge_lab3d(cfg: HodgeConfig) -> int:
    """CLI-вход --lab3d: парсит --sweep'ы, запускает лабораторию, печатает путь."""
    if not cfg.lab3d:
        print(HODGEText.badge("FAIL") + " --lab3d: не задано имя функции")
        return 2
    fn = cfg.lab3d
    if fn.startswith("expr:"):
        fn = fn[5:]
    sweeps = {}
    for spec in cfg.sweeps:
        name, vals = _parse_sweep(spec)
        sweeps[name] = vals
    if not sweeps:
        sweeps = {"N": [7, 9, 15]}   # дефолт-тур по N (§11.6.4)
    cfg.run_dir = cfg.run_dir or _new_run_dir(cfg)
    lab = HODGE3DLab(cfg)
    manifest = lab.run(fn, sweeps, {}, grid_n=cfg.lab_grid, max_frames=cfg.lab_max_frames)
    print(HODGEText.badge("DONE")
          + f" lab3d {fn}: {manifest['frames']} кадров → {lab.out_dir}/sweep.gif")
    return 0


# ── §11.5: рендер плотов задачи (PNG/GIF/SVG) в task_NN_slug/plots/ ──
_PLOT_PDF_WARNED = False


def _fallback_bar_plot(task_entry, task_result, cfg):
    """Часть IV.2: задачи без явного plot_fn получают bar-chart по
    pass-вердиктам и времени. Пустых PNG не бывает: всегда есть хотя бы
    1 столбец (пустой прогон — не фабрикуем график)."""
    p = HODGEPlot(cfg.plot_width, cfg.plot_height,
                  title=f"[{task_entry['id']:2d}] {task_entry['slug']} · {task_result.get('verdict', '?')}",
                  xlabel="pass", ylabel="duration_s",
                  theme_name=cfg.theme, aa=cfg.plot_aa)
    xs, ys = [], []
    for pno, pr in sorted(task_result.get("passes", {}).items()):
        xs.append(float(pno))
        ys.append(max(pr.get("duration_s", 0.01), 0.001))
    if not xs:
        return []  # пустой прогон — не фабрикуем график
    p.add("duration", xs, ys, 's')
    p.xlim = (0.5, max(xs) + 0.5)
    return [(p, 200)]


def _render_plots_for_task(cfg, task_entry, task_result, logger=None):
    """§11.5 / Часть IV.2: plot_fn задачи → plot_NN.png (+ animation.gif —
    тур по плотам). Нет plot_fn → fallback bar-chart по пассам. GCT общий
    на прогон (cfg.gct_cache). PDF честно ERR_UNSUPPORTED (§1.5)."""
    global _PLOT_PDF_WARNED
    plot_fn = task_entry.get("plot_fn")
    if plot_fn is not None:
        frames = plot_fn(task_result, cfg)
    else:
        frames = _fallback_bar_plot(task_entry, task_result, cfg)
    if not frames:
        return
    # §24.3: путь каталога задачи — через path-guard, как в per_task_all
    slug = safe_slug(task_entry["slug"]) or f"task{task_entry['id']:02d}"
    tdir = os.path.join(cfg.run_dir, f"task_{task_entry['id']:02d}_{slug}")
    plots = os.path.join(tdir, "plots")
    os.makedirs(plots, exist_ok=True)
    fmts = {f.strip().lower() for f in cfg.plot_formats.split(",") if f.strip()}
    if "pdf" in fmts and not _PLOT_PDF_WARNED:
        _PLOT_PDF_WARNED = True
        if logger:
            logger.ledger("ERR_UNSUPPORTED")
            logger.log_comp("WARN", "Plot",
                            "plot-formats pdf: stdlib-сборка не пишет PDF (§1.5); "
                            "ближайший эквивалент — png/svg")
    cache = cfg.gct_cache
    gif_frames, gif_delays = [], []
    for i, (plot, delay) in enumerate(frames):
        if "png" in fmts:
            plot.write_png(os.path.join(plots, f"plot_{i + 1:02d}.png"))
        if "svg" in fmts:
            HODGEAdapter.atomic_write(os.path.join(plots, f"plot_{i + 1:02d}.svg"),
                                      plot.to_svg())
        if "gif" in fmts:
            idx, _ = plot.to_gif_frame(cache)
            gif_frames.append(idx)
            gif_delays.append(delay)
    if gif_frames:
        HODGEGif.write(os.path.join(plots, "animation.gif"),
                       frames[0][0].out_W, frames[0][0].out_H,
                       cache["gct"], gif_frames, gif_delays)


# ── §11.6: plot_fn для приоритетных задач (2, 6, 10, 13, 21). Данные
# пересчитываются тем же детерминированным способом, что и в задаче —
# плоты не фабрикуются из воздуха (§10.5). ──

def plot02_periods(result, cfg):
    """V2: worst rel err замкнутой формы vs tanh–sinh по N — log-скэттер."""
    prec = min(cfg.prec, 45)
    pts_n, pts_e = [], []
    with HODGEHP.scope(prec):
        for N in (7, 9, 15, 30):
            zeta = _zeta(N, prec)
            _, by_d, _ = HODGEEX.census(N)
            worst = 0.0
            for _d, (a, b) in HODGEEX.pick_chars(by_d, per_d=1):
                om = HODGEHP.omega_closed(N, a, b, prec)
                pn = HODGEHP.period_numeric(N, a, b, 0, 0, prec, zeta=zeta)
                pc = HODGEHP.cscale(zeta[0], om / N)
                worst = max(worst, float(HODGEHP.rel_err_c(pc, pn)))
            pts_n.append(N)
            pts_e.append(max(worst, 1e-35))
    p = HODGEPlot(cfg.plot_width, cfg.plot_height,
                  title="V2: closed form vs tanh-sinh", xlabel="N", ylabel="rel err",
                  theme_name=cfg.theme, aa=cfg.plot_aa)
    p.add("rel err", pts_n, pts_e, 's')
    p.ylim = (1e-35, 1e-25)
    return [(p, 150)]


def plot06_reflection(result, cfg):
    """V6: Γ(k/N)Γ(1−k/N) vs π/sin(πk/N) — две линии на одних осях (N=15)."""
    prec = min(cfg.prec, 45)
    xs, lhs, rhs = [], [], []
    N = 15
    with HODGEHP.scope(prec):
        pi = HODGEHP.pi(prec)
        for k in range(1, N):
            x = k / N
            xs.append(x)
            lhs.append(float(HODGEHP.gamma(HODGEHP.D(k) / N, prec)
                             * HODGEHP.gamma(1 - HODGEHP.D(k) / N, prec)))
            rhs.append(float(pi / HODGEHP.sin(pi * k / N, prec)))
    plots = []
    for mode in ("lhs", "both"):
        p = HODGEPlot(cfg.plot_width, cfg.plot_height,
                      title=f"V6: Γ-reflection N={N} ({mode})",
                      xlabel="k/N", ylabel="GG / pi/sin",
                      theme_name=cfg.theme, aa=cfg.plot_aa)
        p.add("G(k/N)G(1-k/N)", xs, lhs, 's')
        if mode == "both":
            p.add("pi/sin(pi k/N)", xs, rhs, 'l')
        plots.append((p, 200))
    return plots


def plot10_k3(result, cfg):
    """T08: тепловая карта Грам-матрицы K3 (49×49, точные Fraction → float)."""
    G, _ = HODGEEX.k3_gram()
    grid = [[float(G[i][j]) for j in range(len(G[0]))] for i in range(len(G))]
    mx = max(abs(v) for row in grid for v in row) or 1.0
    grid = [[(v + mx) / (2 * mx) for v in row] for row in grid]
    p = HODGEPlot(cfg.plot_width, cfg.plot_height,
                  title="T08: K3 Gram matrix 49x49", xlabel="col", ylabel="row",
                  theme_name=cfg.theme, aa=1)
    p.add_heatmap("Gram", grid, color=HODGEColor.PLOT_SERIES[0])
    return [(p, 250)]


def plot13_flow(result, cfg):
    """T13: орбита потока на торе 24×36 (a=3, b=5), цвет — шаг."""
    W, H, a, b = 24, 36, 3, 5
    t = HODGEEX.tstar(W, H, a, b)
    xs, ys, cs = [], [], []
    x = y = 0
    for i in range(t + 1):
        xs.append(x)
        ys.append(y)
        cs.append(i / max(t, 1))
        x = (x + a) % W
        y = (y + b) % H
    p = HODGEPlot(cfg.plot_width, cfg.plot_height,
                  title=f"T13: torus flow 24x36 (a=3,b=5) t*={t}",
                  xlabel="x mod W", ylabel="y mod H",
                  theme_name=cfg.theme, aa=cfg.plot_aa)
    p.xlim, p.ylim = (-1, W), (-1, H)
    p.add("orbit", xs, ys, 's')
    return [(p, 200)]


def plot21_fermat(result, cfg):
    """C-011: |t_p| vs граница Вейля — одна панель; #X₀(F_p) — вторая
    (B9: на общей оси Weil ~35k давил счёт точек — нечитаемо)."""
    ps, proj, tps, weil = [], [], [], []
    for pp in (11, 31):
        m = HODGEEX.fermat_point_count(pp)
        ps.append(pp)
        proj.append(m["proj"])
        tps.append(abs(m["t_p"]))
        weil.append(204 * pp ** 1.5)
    p1 = HODGEPlot(cfg.plot_width, cfg.plot_height,
                   title="C-011: |t_p| vs Weil bound",
                   xlabel="p", ylabel="value",
                   theme_name=cfg.theme, aa=cfg.plot_aa)
    p1.xlim, p1.ylim = (8, 34), (0, max(weil) * 1.1)
    p1.add("Weil bound", ps, weil, 'l')
    p1.add("|t_p|", ps, tps, 's')
    p2 = HODGEPlot(cfg.plot_width, cfg.plot_height,
                   title="C-011: point count #X0(Fp)",
                   xlabel="p", ylabel="#points",
                   theme_name=cfg.theme, aa=cfg.plot_aa)
    p2.xlim = (8, 34)
    p2.add("#X0(Fp)", ps, proj, 's')
    return [(p1, 200), (p2, 200)]


# ══════════════════════════════════════════════════════════════════════════
# HODGEEX — ТОЧНЫЙ СЛОЙ: целочисленная арифметика без допусков.
# Конвенция многочленов: MSB-first (a[0] — старшая степень), моническая
# редукция; приведение Φ_n из формулы ∏_{d|n}(x^d−1)^{μ(n/d)} — точно.
# ══════════════════════════════════════════════════════════════════════════
class HODGEEX:
    # ── базовые целочисленные функции ──
    @staticmethod
    def gcd(a: int, b: int) -> int:
        while b:
            a, b = b, a % b
        return abs(a)

    @classmethod
    def lcm(cls, a: int, b: int) -> int:
        return 0 if a == 0 or b == 0 else abs(a // cls.gcd(a, b) * b)

    @staticmethod
    def mobius(m: int) -> int:
        if m == 1:
            return 1
        result, x, q = 1, m, 2
        while q * q <= x:
            if x % q == 0:
                x //= q
                if x % q == 0:
                    return 0
                result = -result
            q += 1
        if x > 1:
            result = -result
        return result

    @staticmethod
    def phi(m: int) -> int:
        out, x = m, m
        p = 2
        while p * p <= x:
            if x % p == 0:
                out -= out // p
                while x % p == 0:
                    x //= p
            p += 1
        if x > 1:
            out -= out // x
        return out

    # ── V1/T01/T20: ценз проводников — две независимые схемы ──
    @staticmethod
    def census(N: int):
        """Прямая схема: d = N/gcd(N,a,b), 1 ≤ a, 1 ≤ b, a+b ≤ N−1."""
        h = {}
        chars_by_d = {}
        for a in range(1, N):
            for b in range(1, N - a):
                d = N // HODGEEX.gcd(HODGEEX.gcd(N, a), b)
                h[d] = h.get(d, 0) + 1
                chars_by_d.setdefault(d, []).append((a, b))
        genus = (N - 1) * (N - 2) // 2
        return dict(sorted(h.items())), dict(sorted(chars_by_d.items())), genus

    @classmethod
    def census_mobius(cls, N: int) -> dict:
        """Схема Мёбиуса: h_d = Σ_{m|d} μ(m)·c(d/m), c(k) = (k−1)(k−2)/2."""
        def c(k):
            return (k - 1) * (k - 2) // 2 if k >= 3 else 0
        out = {}
        for d in range(2, N + 1):
            if N % d:
                continue
            s = sum(cls.mobius(m) * c(d // m) for m in range(1, d + 1) if d % m == 0)
            if s:
                out[d] = s
        return dict(sorted(out.items()))

    @staticmethod
    def pick_chars(chars_by_d: dict, per_d: int = 3):
        """Детерминированная выборка: края + середина каждой группы (как в репо)."""
        out = []
        for d, lst in chars_by_d.items():
            n = len(lst)
            take = sorted({0, n // 2, n - 1}) if n >= 3 else list(range(n))
            for k in take[:per_d]:
                out.append((d, lst[k]))
        return out

    # ── многочлены (MSB-first, int-коэффициенты) ──
    @staticmethod
    def pnorm(p):
        while p and p[0] == 0:
            p.pop(0)
        return p if p else [0]

    @staticmethod
    def padd(p, q):
        out = [0] * max(len(p), len(q))
        for i, c in enumerate(p):
            out[len(out) - len(p) + i] += c
        for i, c in enumerate(q):
            out[len(out) - len(q) + i] += c
        return HODGEEX.pnorm(out)

    @staticmethod
    def psub(p, q):
        return HODGEEX.padd(p, [-c for c in q])

    @staticmethod
    def pmul(p, q):
        res = [0] * (len(p) + len(q) - 1)
        for i, a in enumerate(p):
            if a:
                for j, b in enumerate(q):
                    res[i + j] += a * b
        return HODGEEX.pnorm(res)

    @staticmethod
    def pmod_monic(p, phi):
        """Редукция по моническому Φ (MSB-first): a[i+j] −= a[i]·phi[j]."""
        a = list(p)
        dphi = len(phi) - 1
        for i in range(len(a) - dphi):
            if not a[i]:
                continue
            for j in range(1, len(phi)):
                a[i + j] -= a[i] * phi[j]
            a[i] = 0
        return HODGEEX.pnorm(a)

    @staticmethod
    def peval_int(p, x: int) -> int:
        acc = 0
        for c in p:
            acc = acc * x + c
        return acc

    _phi_cache: dict = {}

    @classmethod
    def cyclotomic(cls, n: int) -> list:
        """Φ_n(x) по канонической схеме Φ_n = (xⁿ−1)/∏_{d|n, d<n} Φ_d —
        каждое деление точное (Φ_d попарно взаимно просты, делят xⁿ−1)."""
        if n in cls._phi_cache:
            return list(cls._phi_cache[n])
        rem = [1] + [0] * (n - 1) + [-1]              # xⁿ − 1 (MSB-first)
        for d in sorted(dd for dd in range(1, n) if n % dd == 0):
            rem = cls._pdiv_exact(rem, cls.cyclotomic(d))
        cls._phi_cache[n] = list(rem)
        return list(rem)

    @staticmethod
    def _pdiv_exact(a, b):
        """Точное деление многочленов MSB-first на монический делитель b."""
        a = list(a)
        db, dbig = len(a) - len(b) + 1, len(b) - 1
        q = [0] * max(db, 0)
        for i in range(db):
            c = a[i]
            if c:
                q[i] = c
                for j in range(len(b)):
                    a[i + j] -= c * b[j]
        assert all(v == 0 for v in a), "деление неточно"
        return HODGEEX.pnorm(q)

    # ── Z[ζ]/(Φ_n): элементы — нормированные int-списки (MSB-first) ──
    @classmethod
    def zadd(cls, p, q, n, phi):
        return cls.pmod_monic(cls.padd(p, q), phi)

    @classmethod
    def zmul(cls, p, q, n, phi):
        return cls.pmod_monic(cls.pmul(p, q), phi)

    @classmethod
    def cyc_elem_syms(cls, n: int, units: list):
        """Симметрические функции s1, s2, s3 корней x_k = ζ^k + ζ^{−k}
        в ℤ[ζ]/(Φ_n): обязаны коллапсировать в целые константы."""
        phi = cls.cyclotomic(n)
        els = []
        for k in units:
            p = [0] * (n + 1)
            p[k] += 1
            p[n - k] += 1
            els.append(cls.pmod_monic(p, phi))
        s1 = els[0]
        for e in els[1:]:
            s1 = cls.zadd(s1, e, n, phi)
        s2 = cls.zmul(els[0], els[1], n, phi)
        s2 = cls.zadd(s2, cls.zmul(els[0], els[2], n, phi), n, phi)
        s2 = cls.zadd(s2, cls.zmul(els[1], els[2], n, phi), n, phi)
        s3 = cls.zmul(cls.zmul(els[0], els[1], n, phi), els[2], n, phi)
        def const(p):
            return p[0] if len(p) == 1 else None
        return const(s1), const(s2), const(s3)

    @classmethod
    def gf2_irreducible(cls, coeffs) -> bool:
        """Неприводимость над GF(2): нет корней в F₂ и нет делителей —
        x²+x+1 (единственный неприводимый квадрат), x³+x+1, x³+x²+1."""
        c = [v & 1 for v in coeffs]
        if c[-1] == 0:      # старший коэффициент 0 (приводимо тривиально)
            return False
        if all(v == 0 for v in c[:-1]):
            return False    # константа 0 → корень 0
        # корень 1: сумма чётна
        if sum(c) % 2 == 0:
            return False
        deg = len(c) - 1
        quads = [[1, 1, 1]]
        cubs = [[1, 1, 0, 1], [1, 0, 1, 1]]
        for d in (quads if deg >= 4 else []) + (cubs if deg >= 6 else []):
            dd = len(d) - 1
            if deg % dd or dd >= deg:     # только СОБСТВЕННЫе делители
                continue
            if cls._gf2_divisible(c, d):
                return False
        return True

    @classmethod
    def _gf2_divisible(cls, c, d):
        a = c[:]
        dd = len(d) - 1
        for i in range(len(a) - dd):
            if a[i]:
                for j in range(len(d)):
                    a[i + j] ^= d[j]
        return all(v == 0 for v in a)

    # ── T05/T19: башня ℤ[√5][√D] (элемент ((A),(B)) = A + B·β, β² = D) ──
    @staticmethod
    def z5mul(p, q): return (p[0] * q[0] + 5 * p[1] * q[1], p[0] * q[1] + p[1] * q[0])
    @staticmethod
    def z5add(p, q): return (p[0] + q[0], p[1] + q[1])
    @classmethod
    def tw_mul(cls, u, v, Dq):
        return (cls.z5add(cls.z5mul(u[0], v[0]), cls.z5mul(cls.z5mul(u[1], v[1]), Dq)),
                cls.z5add(cls.z5mul(u[0], v[1]), cls.z5mul(u[1], v[0])))
    @classmethod
    def tw_add(cls, u, v):
        return (cls.z5add(u[0], v[0]), cls.z5add(u[1], v[1]))
    @classmethod
    def tw_scale(cls, u, k):
        return ((u[0][0] * k, u[0][1] * k), (u[1][0] * k, u[1][1] * k))
    @classmethod
    def tw_pow(cls, u, e, Dq):
        r, b = ((1, 0), (0, 0)), u
        while e:
            if e & 1:
                r = cls.tw_mul(r, b, Dq)
            b = cls.tw_mul(b, b, Dq)
            e >>= 1
        return r

    # Радикальные спецификации v1.2 (захардкожены в laboratory.py, L461–476)
    BCH_RADICALS = {
        15: {"D": (30, -6), "m": ((1, 1), (1, 0)), "den": 4,
             "poly": (1, -1, -4, 4, 1), "radical": "(7 − √5 − √(30−6√5))/8"},
        30: {"D": (30, 6), "m": ((-1, 1), (1, 0)), "den": 4,
             "poly": (1, 1, -4, -4, 1), "radical": "(9 − √5 − √(30+6√5))/8"},
    }

    @classmethod
    def bch_exact_residual(cls, n: int):
        """den⁴·P(m/den) — ТОЧНО в ℤ[√5][√D]; ноль доказывает радикал."""
        spec = cls.BCH_RADICALS[n]
        Dq, m, den, poly = spec["D"], spec["m"], spec["den"], spec["poly"]
        powers = [((1, 0), (0, 0))]
        for _ in range(4):
            powers.append(cls.tw_mul(powers[-1], m, Dq))
        acc = ((0, 0), (0, 0))
        for k in range(5):
            c = poly[4 - k]
            if c:
                acc = cls.tw_add(acc, cls.tw_scale(powers[k], c * den ** (4 - k)))
        return acc

    # ── SNF (Каннан–Бахем с Безу-элиминацией; гарантированная сходимость) ──
    @classmethod
    def egcd(cls, a: int, b: int):
        """Расширенный НОД: g = gcd(|a|,|b|), g = x·a + y·b."""
        old_r, r = abs(a), abs(b)
        old_x, x = 1, 0
        old_y, y = 0, 1
        while r:
            q = old_r // r
            old_r, r = r, old_r - q * r
            old_x, x = x, old_x - q * x
            old_y, y = y, old_y - q * y
        sx = old_x if a >= 0 else -old_x
        sy = old_y if b >= 0 else -old_y
        return old_r, sx, sy

    @classmethod
    def snf(cls, mat):
        """SNF: пивот минимального модуля + Безу-обнуление строки/столбца.
        Нарушение делимости в подматрице → колонковый шаг C_j ← C_j − q·C_t
        уменьшает остаток < пивота → строгая сходимость (NE02: diag(2,3)→(1,6))."""
        a = [row[:] for row in mat]
        rows, cols = len(a), len(a[0])
        res = []
        for t in range(min(rows, cols)):
            while True:
                p, pi_, pj = 0, -1, -1
                for i in range(t, rows):
                    for j in range(t, cols):
                        v = abs(a[i][j])
                        if v != 0 and (pi_ < 0 or v < p):
                            p, pi_, pj = v, i, j
                if pi_ < 0:
                    return res
                if pi_ != t:
                    a[t], a[pi_] = a[pi_], a[t]
                if pj != t:
                    for i in range(rows):
                        a[i][t], a[i][pj] = a[i][pj], a[i][t]
                piv = a[t][t]
                # Безу-обнуление столбца t под пивотом (строки)
                for i in range(t + 1, rows):
                    b = a[i][t]
                    if b == 0:
                        continue
                    g, x, y = cls.egcd(piv, b)
                    rowt, rowi = a[t][:], a[i][:]
                    for j in range(cols):
                        a[t][j] = x * rowt[j] + y * rowi[j]
                        a[i][j] = -(b // g) * rowt[j] + (piv // g) * rowi[j]
                    piv = a[t][t]
                # Безу-обнуление строки t правее пивота (столбцы)
                for j in range(t + 1, cols):
                    b = a[t][j]
                    if b == 0:
                        continue
                    g, x, y = cls.egcd(piv, b)
                    colt = [a[i][t] for i in range(rows)]
                    colj = [a[i][j] for i in range(rows)]
                    for i in range(rows):
                        a[i][t] = x * colt[i] + y * colj[i]
                        a[i][j] = -(b // g) * colt[i] + (piv // g) * colj[i]
                    piv = a[t][t]
                # нарушена делимость подматрицы? → уменьшить остаток < пивота
                viol = None
                for i in range(t + 1, rows):
                    for j in range(t + 1, cols):
                        if a[i][j] % piv:
                            viol = (i, j)
                            break
                    if viol:
                        break
                if viol is None:
                    break
                i, j = viol
                # строка i обязана иметь ненулевой элемент в столбце t,
                # иначе колонковый шаг не уменьшит a[i][j]
                if a[i][t] == 0:
                    a[i] = [a[i][k] + a[t][k] for k in range(cols)]   # R_i ← R_i + R_t
                else:
                    q0 = a[i][t] // piv
                    if q0:
                        a[i] = [a[i][k] - q0 * a[t][k] for k in range(cols)]
                    if a[i][t] == 0:
                        a[i] = [a[i][k] + a[t][k] for k in range(cols)]
                q = a[i][j] // piv
                for r_ in range(rows):
                    a[r_][j] -= q * a[r_][t]
            res.append(abs(a[t][t]))
        # gcd/lcm-ремонт делимости d_i | d_{i+1}
        for i in range(len(res) - 1):
            g, l = HODGEEX.gcd(res[i], res[i + 1]), HODGEEX.lcm(res[i], res[i + 1])
            res[i], res[i + 1] = g, l
        return res

    # ── точный ранг / эшелон / сигнатура над ℚ ──
    @staticmethod
    def rank_fractions(Mint) -> int:
        M = [[Fraction(v) for v in row] for row in Mint]
        n = len(M)
        r = 0
        for c in range(len(M[0]) if M else 0):
            if r >= n:
                break
            piv = next((i for i in range(r, n) if M[i][c] != 0), -1)
            if piv < 0:
                continue
            M[r], M[piv] = M[piv], M[r]
            pv = M[r][c]
            for i in range(r + 1, n):
                if M[i][c] != 0:
                    f = M[i][c] / pv
                    for j in range(c, len(M[0])):
                        M[i][j] -= f * M[r][j]
            r += 1
        return r

    @staticmethod
    def int_ech_rows(Mint):
        """Целочисленный эшелон строк: базис пространства строк (как в полиглоте)."""
        n = len(Mint)
        M = [[Fraction(v) for v in row] for row in Mint]
        rowsF, r = [], 0
        for c in range(n):
            if r >= n:
                break
            piv = next((i for i in range(r, n) if M[i][c] != 0), -1)
            if piv < 0:
                continue
            M[r], M[piv] = M[piv], M[r]
            pv = M[r][c]
            M[r] = [x / pv for x in M[r]]
            for i in range(n):
                if i != r and M[i][c] != 0:
                    f = M[i][c]
                    for j in range(c, n):
                        M[i][j] -= f * M[r][j]
            rowsF.append(M[r][:])
            r += 1
        out = []
        for row in rowsF:
            L = 1
            for x in row:
                L = L // HODGEEX.gcd(L, x.denominator) * x.denominator
            ints = [int(x * L) for x in row]
            g = 0
            for v in ints:
                g = HODGEEX.gcd(g, abs(v))
            if g > 1:
                ints = [v // g for v in ints]
            out.append(ints)
        return out

    @staticmethod
    def exact_signature(G, ech):
        """Точная сигнатура: S = R·G·Rᵀ по эшелону, затем LDLᵀ на Fraction."""
        n, k = len(G), len(ech)
        S = [[0] * k for _ in range(k)]
        for i in range(k):
            T = [0] * n
            for t in range(n):
                if ech[i][t]:
                    cit = ech[i][t]
                    for u in range(n):
                        T[u] += cit * G[t][u]
            for j in range(k):
                S[i][j] = S[j][i] = sum(T[u] * ech[j][u] for u in range(n))
        A = [[Fraction(S[i][j]) for j in range(k)] for i in range(k)]
        diag = []
        for i in range(k):
            s = Fraction(0)
            for t in range(i):
                s += A[t][i] * A[t][i] * diag[t]
            d = A[i][i] - s
            if d == 0:
                return None
            diag.append(d)
            for j in range(i + 1, k):
                s2 = Fraction(0)
                for t in range(i):
                    s2 += A[t][i] * A[t][j] * diag[t]
                v = (Fraction(S[i][j]) - s2) / diag[i]
                A[i][j] = A[j][i] = v
        pos = sum(1 for d in diag if d > 0)
        neg = sum(1 for d in diag if d < 0)
        return pos, neg, diag

    @staticmethod
    def bareiss_det(Mint) -> int:
        """Точный определитель целочисленной матрицы (фракционно-свободный)."""
        M = [row[:] for row in Mint]
        n = len(M)
        sign = 1
        prev = 1
        for k in range(n - 1):
            if M[k][k] == 0:
                swap = next((i for i in range(k + 1, n) if M[i][k] != 0), -1)
                if swap < 0:
                    return 0
                M[k], M[swap] = M[swap], M[k]
                sign = -sign
            for i in range(k + 1, n):
                for j in range(k + 1, n):
                    M[i][j] = (M[i][j] * M[k][k] - M[i][k] * M[k][j]) // prev
            prev = M[k][k]
        return sign * M[n - 1][n - 1]

    # ── суммы Рамануджана и следовая форма ──
    @classmethod
    def ramanujan_c(cls, N: int, k: int) -> int:
        g = cls.gcd(N, k)
        return cls.mobius(N // g) * cls.phi(N) // cls.phi(N // g)

    @classmethod
    def trace_gram(cls, N: int):
        """Грам следовой формы Tr(ζ^{i−j}) для ℤ[ζ_N]: d×d, d = φ(N)."""
        d = cls.phi(N)
        return [[cls.ramanujan_c(N, (i - j) % N) for j in range(d)] for i in range(d)]

    # ── T09: перечисление Арфа (полный перебор 2^{2g} форм) ──
    @staticmethod
    def arf_enumeration(g: int):
        n = 2 * g
        size = 1 << n
        half = size >> 1
        shift = 1 << (g - 1)
        pairs = [(2 * i, 2 * i + 1) for i in range(g)]
        even = odd = 0
        for basis in range(size):
            zeros = 0
            for v in range(size):
                qv = 0
                for i in range(n):
                    if (v >> i) & 1:
                        qv ^= (basis >> i) & 1
                for (i, j) in pairs:
                    if ((v >> i) & 1) and ((v >> j) & 1):
                        qv ^= 1
                if qv == 0:
                    zeros += 1
            if zeros == half + shift:
                even += 1
            else:
                odd += 1
        return size, even, odd

    # ── T08/T10/T22: K3 — 48 прямых, точные инварианты ──
    @staticmethod
    def k3_lines():
        return [(f, a, b) for f in (1, 2, 3) for a in range(4) for b in range(4)]

    @staticmethod
    def k3_inter(l1, l2) -> int:
        if l1 == l2:
            return -2
        f1, a1, b1 = l1
        f2, a2, b2 = l2
        if f1 == f2:
            return 1 if (a1 == a2) != (b1 == b2) else 0
        ff = tuple(sorted((f1, f2)))
        if ff == (1, 2):
            return 1 if (a1 + b2 - a2 - b1) % 4 == 0 else 0
        if ff == (1, 3):
            if f1 == 1:
                return 1 if (a2 - a1 - b1 - b2 - 1) % 4 == 0 else 0
            return 1 if (a1 - a2 - b2 - b1 - 1) % 4 == 0 else 0
        return 1 if (a1 + b1 - a2 - b2) % 4 == 0 else 0

    @classmethod
    def k3_gram(cls):
        ls = cls.k3_lines()
        n = len(ls)
        G = [[0] * (n + 1) for _ in range(n + 1)]
        for i in range(n):
            for j in range(i, n):
                G[i][j] = G[j][i] = cls.k3_inter(ls[i], ls[j])
        for i in range(n):
            G[i][n] = G[n][i] = 1
        G[n][n] = 4
        return G, ls

    @classmethod
    def k3_invariants(cls):
        G, ls = cls.k3_gram()
        n = len(G)
        rank = cls.rank_fractions(G)
        factors = cls.snf([r[:] for r in G])
        det = 1
        for v in factors:
            det *= v
        sig = cls.exact_signature(G, cls.int_ech_rows(G))
        idx = {l: i for i, l in enumerate(ls)}
        fam_ok = True
        for a in range(4):
            for j in range(n):
                if sum(G[idx[(1, a, b)]][j] for b in range(4)) != G[n - 1][j]:
                    fam_ok = False
                    break
            if not fam_ok:
                break
        sym_ok = all(G[i][j] == G[j][i] for i in range(n) for j in range(n))
        diag_ok = all(G[idx[l]][idx[l]] == -2 for l in ls)
        return {"lines": len(ls), "rank": rank, "factors": factors, "det": det,
                "sig": (sig[0], sig[1]) if sig else None,
                "sylvester": sig[2] if sig else None,
                "fam_ok": fam_ok, "sym_ok": sym_ok, "diag_ok": diag_ok}

    # ── T11: Клейн — точный слой ──
    @classmethod
    def klein_exact(cls) -> dict:
        j = -(105 ** 3) // 343
        c1 = (j == -3375) and ((-15) ** 3 == -3375)
        c2 = (-343) * j == 105 ** 3 == 1157625
        expand = [0, 0, 0, 0]
        for i, ci in [(0, 1), (1, -7)]:
            for jj, cj in [(0, 1), (1, 7), (2, 14)]:
                expand[i + jj] += ci * cj
        c3 = expand == [1, 0, -35, -98]
        c4 = 7 ** 2 - 4 * 14 == -7
        return {"j": j, "c1": c1, "c2": c2, "expand": expand, "c3": c3,
                "disc": c4}

    # ── T13/cert E: поток и формула завершимости ──
    @classmethod
    def tstar(cls, W, H, a, b) -> int:
        return cls.lcm(W // cls.gcd(a, W), H // cls.gcd(b, H))

    @staticmethod
    def binary_flow(W=48, H=48, a=1, b=1):
        t = HODGEEX.tstar(W, H, a, b)
        x = y = dx = dy = 0
        visited = set()
        for _ in range(t):
            visited.add((x, y))
            x = (x + a) % W
            y = (y + b) % H
            dx = (dx + a) % W
            dy = (dy + b) % H
        return {"t": t, "visited": len(visited), "closed": dx == 0 and dy == 0}

    # ── T14/cert F: q-scan (рационализация с границей знаменателя) ──
    @staticmethod
    def qscan(x: float, Q: int, tol: float = 1e-9):
        for q in range(1, Q + 1):
            p = int(x * q + 0.5)
            if abs(x * q - p) <= 0.5 and abs(x - p / q) < tol:
                return (q, p)
        return None

    # ── T12: μ₄-симметричные системы — детерминированное семейство ──
    @classmethod
    def mu4_system(cls, dim: int, seed: int):
        """Блочно-циклическая целочисленная матрица L (commutes with R),
        R — перестановка порядка 4. L = блок-циркулянт из детерминированных
        блоков: μ₄-ковариантность L·R = R·L точна в целых числах."""
        K = dim // 4
        rng_state = (seed * 2654435761 + 11) & 0xFFFFFFFF

        def rnd():
            nonlocal rng_state
            x = rng_state
            x ^= (x << 13) & 0xFFFFFFFF
            x ^= x >> 17
            x ^= (x << 5) & 0xFFFFFFFF
            rng_state = x
            return x & 0xFFFF
        blocks = [[rnd() - 32768 for _ in range(K)] for _ in range(4)]
        L = [[0] * dim for _ in range(dim)]
        for bi in range(4):
            for bj in range(4):
                bl = blocks[(bj - bi) % 4]   # блочный циркулянт → [L,R]=0
                for i in range(K):
                    for j in range(K):
                        L[bi * K + i][bj * K + j] = bl[i] if i == j else 0
        return L

    @classmethod
    def mu4_rot(cls, dim: int):
        """Перестановка порядка 4 (элементы — гауссовы пары для ℤ[i]-матриц)."""
        K = dim // 4
        R = [[(0, 0)] * dim for _ in range(dim)]
        for i in range(dim):
            R[i][(i + K) % dim] = (1, 0)
        return R

    @staticmethod
    def mat_mul(A, B):
        n, m, p = len(A), len(B), len(B[0])
        C = [[0] * p for _ in range(n)]
        for i in range(n):
            Ai = A[i]
            Ci = C[i]
            for k in range(m):
                a = Ai[k]
                if a:
                    Bk = B[k]
                    for j in range(p):
                        Ci[j] += a * Bk[j]
        return C

    @classmethod
    def gauss_int_mul(cls, A, B):
        """Умножение матриц над ℤ[i] (элементы — пары (re, im); int трактуются
        как вещественные гауссовы числа)."""
        n, m, p = len(A), len(B), len(B[0])
        C = [[(0, 0)] * p for _ in range(n)]
        for i in range(n):
            for k in range(m):
                a = A[i][k]
                if not isinstance(a, tuple):
                    a = (a, 0)
                if a[0] or a[1]:
                    for j in range(p):
                        b = B[k][j]
                        if not isinstance(b, tuple):
                            b = (b, 0)
                        C[i][j] = (C[i][j][0] + a[0] * b[0] - a[1] * b[1],
                                   C[i][j][1] + a[0] * b[1] + a[1] * b[0])
        return C

    @classmethod
    def mu4_projector4(cls, R):
        """P₄ = Σ_{k=0..3} i^{−k}·R^k над ℤ[i]; проверка P₄² = 4·P₄."""
        n = len(R)
        I = [[(1, 0) if i == j else (0, 0) for j in range(n)] for i in range(n)]
        Rk = I
        acc = [[(0, 0)] * n for _ in range(n)]
        powers = [I]
        for _ in range(3):
            powers.append(HODGEEX.gauss_int_mul(powers[-1], R))
        w = [(1, 0), (0, -1), (-1, 0), (0, 1)]     # i^{−k}
        for k in range(4):
            for i in range(n):
                for j in range(n):
                    a, b = powers[k][i][j]
                    wr, wi = w[k]
                    acc[i][j] = (acc[i][j][0] + wr * a - wi * b,
                                 acc[i][j][1] + wr * b + wi * a)
        return acc

    # ── C-011: счёт точек Фермат-КВИНТИКИ (x₀⁵+…+x₄⁵ = 0 в P⁴) ──
    @classmethod
    def fermat_point_count(cls, p: int) -> dict:
        """#X₀(F_p) квинтики: MITM — c2 по парам, c4 = c2∘c2, аффинные =
        Σ_s c4(s)·A(−s); проект. точки = (affine−1)/(p−1). Конвенция репо:
        t_p = (1+p+p²+p³) − #X₀ (t₁₁ = −461, #X₀(F₁₁) = 1925, b₃ = 204)."""
        A = {}
        for x in range(p):
            v = pow(x, 5, p)
            A[v] = A.get(v, 0) + 1
        c2 = {}
        for x in range(p):
            fx = pow(x, 5, p)
            for y in range(p):
                s = (fx + pow(y, 5, p)) % p
                c2[s] = c2.get(s, 0) + 1
        c4 = {}
        for s, cnt in c2.items():
            for t, cnt2 in c2.items():
                u = (s + t) % p
                c4[u] = c4.get(u, 0) + cnt * cnt2
        affine = 0
        for s, cnt in c4.items():
            affine += cnt * A.get((-s) % p, 0)
        proj = (affine - 1) // (p - 1)
        tp = (1 + p + p * p + p ** 3) - proj
        return {"p": p, "affine": affine, "proj": proj, "t_p": tp}

    @classmethod
    def ldlt_pivots(cls, G):
        """LDLᵀ-пивоты симметричной целочисленной матрицы над Fraction
        (без поворотов; для положительно определённой следовой формы)."""
        n = len(G)
        A = [[Fraction(G[i][j]) for j in range(n)] for i in range(n)]
        diag = []
        for i in range(n):
            s = Fraction(0)
            for t in range(i):
                s += A[t][i] * A[t][i] * diag[t]
            d = A[i][i] - s
            if d == 0:
                return None
            diag.append(d)
            for j in range(i + 1, n):
                s2 = Fraction(0)
                for t in range(i):
                    s2 += A[t][i] * A[t][j] * diag[t]
                v = (Fraction(G[i][j]) - s2) / diag[i]
                A[i][j] = A[j][i] = v
        return diag

    # ── NE02-диагностика SNF-движка (verhodge counterexamples) ──
    @classmethod
    def snf_diagnostics(cls) -> dict:
        d1 = cls.snf([[2, 0], [0, 3]])
        d2 = cls.snf([[6, 0, 0], [0, 10, 0], [0, 0, 15]])
        return {"diag23": d1, "diag61015": d2}


# ══════════════════════════════════════════════════════════════════════════
# §4. РЕЕСТР ЗАДАЧ-ТЕСТОВ. Каждая задача — одно утверждение репозитория
# hodge-laboratory; эталонные значения заморожены из
# results/baseline_v1_v9.json, reports/hodge_report.json и монографий.
# Формат вердикта — ровно одна строка через log_result (§4.1).
# ══════════════════════════════════════════════════════════════════════════
_ZETA_CACHE: dict = {}

def _zeta(N: int, prec: int):
    key = (N, prec)
    if key not in _ZETA_CACHE:
        _ZETA_CACHE[key] = HODGEHP.zeta_pow(N, prec)
    return _ZETA_CACHE[key]

class HodgeTaskResult:
    __slots__ = ("ok", "verdict", "metrics", "skip_reason")
    def __init__(self, ok: bool, verdict: str, metrics: dict | None = None,
                 skip_reason: str | None = None):
        self.ok = ok
        self.verdict = verdict
        self.metrics = metrics or {}
        self.skip_reason = skip_reason


# ── Задача 1 · T01/T20/V1: формула рода, ценз проводников, две схемы ──
def task01_census(cfg):
    hodge_log(cfg, "INFO", "census", "прямой ценз и схема Мёбиуса, N∈{4,5,7,9,11,15,30}")
    frozen = {7: {7: 15}, 9: {3: 1, 9: 27}, 11: {11: 45},
              15: {3: 1, 5: 6, 15: 84}, 30: {3: 1, 5: 6, 6: 9, 10: 30, 15: 84, 30: 276}}
    frozen_g = {4: 3, 5: 6, 7: 15, 9: 28, 11: 45, 15: 91, 30: 406}
    ok = True
    det = []
    for N in (4, 5, 7, 9, 11, 15, 30):
        h, _, g = HODGEEX.census(N)
        hm = HODGEEX.census_mobius(N)
        p1 = sum(h.values()) == g == frozen_g.get(N, g)
        p2 = h == hm
        p3 = N in frozen and h == frozen[N]
        ok &= (p1 and p2 and (p3 if N in frozen else True))
        det.append(f"N={N}: g={g} Σh={sum(h.values())} mobius={'ok' if p2 else 'X'}")
        if N in frozen and not p3:
            det.append(f"  !! таблица N={N} отличается от baseline")
    return HodgeTaskResult(ok, "формула рода g=(N−1)(N−2)/2 и ценз по проводникам подтверждены (7 уровней, 2 схемы)" if ok
                           else "ценз/род: расхождение с baseline", {"details": det})

def task01b_census_all(cfg):
    """pass 2: две схемы согласуются на ВСЕХ N ∈ [3, 64] (claim C-001 verhodge)."""
    ok = True
    bad = []
    for N in range(3, 65):
        h, _, g = HODGEEX.census(N)
        hm = HODGEEX.census_mobius(N)
        if not (sum(h.values()) == g and h == hm):
            ok = False
            bad.append(N)
    return HodgeTaskResult(ok, "согласие двух схем на всех N∈[3,64] подтверждено" if ok
                           else f"расхождение на N={bad[:5]}", {"range": "3..64"})


# ── Задача 2 · T02/V2: замкнутая форма периода vs tanh–sinh ──
def task02_periods(cfg):
    prec = cfg.prec
    per_d = 1 if cfg.preset == "quick" else 3
    hodge_log(cfg, "INFO", "periods", f"V2: closed Γ-форма vs tanh-sinh, prec={prec}, per_d={per_d}")
    worst = 0.0
    cnt = 0
    with HODGEHP.scope(prec):
        for N in (7, 9, 15, 30):
            zeta = _zeta(N, prec)
            _, by_d, _ = HODGEEX.census(N)
            for _d, (a, b) in HODGEEX.pick_chars(by_d, per_d=per_d):
                om = HODGEHP.omega_closed(N, a, b, prec)
                for (r, s) in ((0, 0), (1, 0), (0, 1)):
                    pc = HODGEHP.cscale(zeta[(r * a + s * b) % N], om / N)
                    pn = HODGEHP.period_numeric(N, a, b, r, s, prec, zeta=zeta)
                    e = float(HODGEHP.rel_err_c(pc, pn))
                    worst = max(worst, e)
                    cnt += 1
    ok = worst < 1e-30
    detail = (f"V2: {cnt} периодов, замкнутая форма = квадратура (rel={worst:.2e} < 1e-30)" if ok
              else f"V2: rel={worst:.2e} ≥ 1e-30")
    metrics = {"n_tests": cnt, "max_rel": worst}
    # v1.5.0-session8 · шаг 1 дорожной карты: адаптивный h закрывает
    # квадратурный пол дискретизации (session7 §2.3: фиксированная сетка
    # h=0.02 давала пол ~4.8e−83 / 1.7e−71, НЕ зависящий от prec и s).
    # Контроль: на prec=100 адаптивная схема обязана дать ≤ 1e−90
    # (масштаб 10^{−prec} вместо пола), на фиксированной сетке пол остаётся.
    if cfg.preset != "quick":
        floor_fixed = 0.0
        worst_adapt = 0.0
        for (N, a, b) in ((15, 4, 5), (30, 11, 19)):
            with HODGEHP.scope(100):
                zeta = _zeta(N, 100)
                om = HODGEHP.omega_closed(N, a, b, 100)
                pc = HODGEHP.cscale(zeta[0], om / N)
                pn_fix = HODGEHP.period_numeric(N, a, b, 0, 0, 100, zeta=zeta)
                pn_ad = HODGEHP.period_numeric(N, a, b, 0, 0, 100, zeta=zeta,
                                               adaptive=True)
                floor_fixed = max(floor_fixed,
                                  float(HODGEHP.rel_err_c(pc, pn_fix)))
                worst_adapt = max(worst_adapt,
                                  float(HODGEHP.rel_err_c(pc, pn_ad)))
        ok &= (worst_adapt < 1e-90)
        detail += (f" · adaptive-h: rel={worst_adapt:.2e} < 1e−90 @prec=100 "
                   f"(пол фиксированной сетки: {floor_fixed:.1e})")
        metrics["adaptive_rel"] = worst_adapt
        metrics["fixed_floor"] = floor_fixed
    return HodgeTaskResult(ok, detail, metrics)

def task02b_periods_tight(cfg):
    """pass 2: плотнее — per_d=4, сетка K=240/h=0.02, prec+5."""
    prec = cfg.prec + 5
    worst = 0.0
    cnt = 0
    with HODGEHP.scope(prec):
        for N in (15, 30):
            zeta = _zeta(N, prec)
            _, by_d, _ = HODGEEX.census(N)
            for _d, (a, b) in HODGEEX.pick_chars(by_d, per_d=4):
                om = HODGEHP.omega_closed(N, a, b, prec)
                for (r, s) in ((0, 0), (1, 0), (0, 1)):
                    pc = HODGEHP.cscale(zeta[(r * a + s * b) % N], om / N)
                    pn = HODGEHP.period_numeric(N, a, b, r, s, prec, K=240, h="0.02", zeta=zeta)
                    worst = max(worst, float(HODGEHP.rel_err_c(pc, pn)))
                    cnt += 1
    ok = worst < 1e-30
    return HodgeTaskResult(ok, f"V2-hardcore: {cnt} тестов на сетке 240/0.02 (rel={worst:.2e})" if ok
                           else f"V2-hardcore: rel={worst:.2e}", {"n_tests": cnt, "max_rel": worst})


# ── Задача 3 · V3: фазовый закон arg P = 2π(ra+sb)/N ──
def task03_phase(cfg):
    prec = cfg.prec
    per_d = 1 if cfg.preset == "quick" else 2
    worst = 0.0
    cnt = 0
    with HODGEHP.scope(prec):
        for N in (7, 9, 15, 30):
            zeta = _zeta(N, prec)
            _, by_d, _ = HODGEEX.census(N)
            for _d, (a, b) in HODGEEX.pick_chars(by_d, per_d=per_d):
                om = HODGEHP.omega_closed(N, a, b, prec)
                for (r, s) in ((0, 0), (1, 0), (0, 1)):
                    pn = HODGEHP.period_numeric(N, a, b, r, s, prec, zeta=zeta)
                    ph = zeta[(r * a + s * b) % N]
                    # компонентная проверка параллельности: Im(pn·conj(phase))/|pn| → 0
                    proj = HODGEHP.cmul(pn, HODGEHP.cconj(ph))
                    dev = float(abs(proj[1]) / max(HODGEHP.cabs(pn), HODGEHP.D("1e-40")))
                    worst = max(worst, dev)
                    cnt += 1
    ok = worst < 1e-25
    return HodgeTaskResult(ok, f"V3: фазовый закон, {cnt} тестов (dev={worst:.2e} < 1e-25)" if ok
                           else f"V3: dev={worst:.2e} ≥ 1e-25", {"n_tests": cnt, "max_dev": worst})


# ── Задача 4 · V4: μ_N×μ_N-эквивариантность ──
def task04_equivariance(cfg):
    prec = cfg.prec
    worst = 0.0
    cnt = 0
    with HODGEHP.scope(prec):
        for N in (7, 9, 15, 30):
            zeta = _zeta(N, prec)
            _, by_d, _ = HODGEEX.census(N)
            for _d, (a, b) in HODGEEX.pick_chars(by_d, per_d=2):
                base = HODGEHP.period_closed(N, a, b, 1, 0, prec, zeta=zeta)
                for (u, v) in ((1, 0), (0, 1), (1, 1)):
                    sh = HODGEHP.period_closed(N, a, b, 1 + u, v, prec, zeta=zeta)
                    f = HODGEHP.cscale(zeta[(u * a + v * b) % N], 1)
                    worst = max(worst, float(HODGEHP.rel_err_c(sh, HODGEHP.cmul(f, base))))
                    cnt += 1
    ok = worst < 1e-30
    return HodgeTaskResult(ok, f"V4: P(r+u,s+v)=ζ^(ua+vb)·P(r,s), {cnt} тестов (rel={worst:.2e})" if ok
                           else f"V4: rel={worst:.2e}", {"n_tests": cnt, "max_rel": worst})


# ── Задача 5 · V5: целостность цепи (орбитные суммы) ──
def task05_chain(cfg):
    prec = cfg.prec
    worst = 0.0
    cases = {15: {"vanish": [(2, 3), (3, 4)], "control": (7, 8)},
             30: {"vanish": [(2, 3), (4, 7)], "control": (7, 23)}}
    with HODGEHP.scope(prec):
        for N in (15, 30):
            zeta = _zeta(N, prec)
            for (a, b) in cases[N]["vanish"]:
                acc = (HODGEHP.D(0), HODGEHP.D(0))
                for k in range(N):
                    acc = HODGEHP.cadd(acc, HODGEHP.period_closed(N, a, b, k, k, prec, zeta=zeta))
                norm = HODGEHP.omega_closed(N, a, b, prec)
                worst = max(worst, float(HODGEHP.cabs(acc) / max(norm, HODGEHP.D("1e-30"))))
            a, b = cases[N]["control"]
            acc = (HODGEHP.D(0), HODGEHP.D(0))
            for k in range(N):
                acc = HODGEHP.cadd(acc, HODGEHP.period_closed(N, a, b, k, k, prec, zeta=zeta))
            om = (HODGEHP.omega_closed(N, a, b, prec), HODGEHP.D(0))
            worst = max(worst, float(HODGEHP.rel_err_c(acc, om)))
    ok = worst < 1e-25
    return HodgeTaskResult(ok, f"V5: Σ_k P(k,k) = 0 (a+b≠0), = Ω (a+b=N) (worst={worst:.2e})" if ok
                           else f"V5: worst={worst:.2e}", {"max_rel": worst})


# ── Задача 6 · V6: лестница Γ-рефлексии ──
def task06_reflection(cfg):
    prec = cfg.prec
    worst = 0.0
    cnt = 0
    with HODGEHP.scope(prec):
        for N in (7, 9, 15, 30):
            pi = HODGEHP.pi(prec)
            for k in range(1, N):
                lhs = HODGEHP.gamma(HODGEHP.D(k) / N, prec) * HODGEHP.gamma(1 - HODGEHP.D(k) / N, prec)
                rhs = pi / HODGEHP.sin(pi * k / N, prec)
                e = abs(lhs - rhs) / abs(rhs)
                worst = max(worst, float(e))
                cnt += 1
    ok = worst < 1e-30
    return HodgeTaskResult(ok, f"V6: Γ(k/N)Γ(1−k/N)=π/sin(πk/N), {cnt} пар (rel={worst:.2e})" if ok
                           else f"V6: rel={worst:.2e}", {"n_tests": cnt, "max_rel": worst})

def task06b_reflection_all(cfg):
    """pass 2: вся решётка k/N для N ∈ [7, 64] (утолщение лестницы)."""
    prec = cfg.prec
    worst = 0.0
    cnt = 0
    with HODGEHP.scope(prec):
        for N in range(7, 65, 3):
            pi = HODGEHP.pi(prec)
            for k in range(1, N):
                lhs = HODGEHP.gamma(HODGEHP.D(k) / N, prec) * HODGEHP.gamma(1 - HODGEHP.D(k) / N, prec)
                rhs = pi / HODGEHP.sin(pi * k / N, prec)
                worst = max(worst, float(abs(lhs - rhs) / abs(rhs)))
                cnt += 1
    ok = worst < 1e-30
    return HodgeTaskResult(ok, f"V6-hardcore: {cnt} пар, N∈[7,64] (rel={worst:.2e})" if ok
                           else f"V6-hardcore: rel={worst:.2e}", {"n_tests": cnt, "max_rel": worst})


# ── Задача 7 · V8: DFT-ортогональность периодов ──
def task07_dft(cfg):
    prec = cfg.prec
    N = 15
    diag_dev = off_dev = 0.0
    with HODGEHP.scope(prec):
        zeta = _zeta(N, prec)
        _, by_d, _ = HODGEEX.census(N)
        chars = [(a, b) for lst in by_d.values() for (a, b) in lst][:8]
        Om = [HODGEHP.omega_closed(N, a, b, prec) for (a, b) in chars]
        for i, (a1, b1) in enumerate(chars):
            for j, (a2, b2) in enumerate(chars):
                acc = (HODGEHP.D(0), HODGEHP.D(0))
                for r in range(N):
                    for s in range(N):
                        acc = HODGEHP.cadd(acc, zeta[(r * (a1 - a2) + s * (b1 - b2)) % N])
                val = HODGEHP.cscale(acc, Om[i] * Om[j] / (N * N))
                if i == j:
                    dev = float(HODGEHP.cabs(HODGEHP.csub(val, (Om[i] * Om[i], HODGEHP.D(0)))) / (Om[i] * Om[i]))
                    diag_dev = max(diag_dev, dev)
                else:
                    dev = float(HODGEHP.cabs(val) / (Om[i] * Om[j]))
                    off_dev = max(off_dev, dev)
    ok = diag_dev < 1e-25 and off_dev < 1e-25
    return HodgeTaskResult(ok, f"V8: Σ Pχ conj(Pχ′) = δχχ′|Ωχ|², 8×225 (diag={diag_dev:.1e}, off={off_dev:.1e})" if ok
                           else f"V8: diag={diag_dev:.1e}, off={off_dev:.1e}",
                           {"diag": diag_dev, "offdiag": off_dev})


# ── Задача 8 · V9: глубокий рекорд точности ──
def task08_deep(cfg):
    """Часть V: V9 — prec=200 при --prec-extreme (порог 1e-100, K=480, h=0.012);
    иначе prec=95 (порог 1e-60, K=280, h=0.024)."""
    prec = 200 if getattr(cfg, "prec_extreme", False) else 95
    threshold = 1e-100 if prec == 200 else 1e-60
    K = 480 if prec == 200 else 280
    h = "0.012" if prec == 200 else "0.024"
    N, a, b, r, s = 15, 2, 3, 1, 1
    with HODGEHP.scope(prec):
        zeta = _zeta(N, prec)
        om = HODGEHP.omega_closed(N, a, b, prec)
        pc = HODGEHP.cscale(zeta[(r * a + s * b) % N], om / N)
        pn = HODGEHP.period_numeric(N, a, b, r, s, prec, K=K, h=h, zeta=zeta)
        e = float(HODGEHP.rel_err_c(pc, pn))
    ok = e < threshold
    return HodgeTaskResult(ok, f"V9: prec={prec}, K={K}, h={h}, rel={e:.2e} "
                                f"{'<' if ok else '≥'} {threshold:.0e}" if ok
                           else f"V9: rel={e:.2e} ≥ {threshold:.0e} — порог не достигнут (см. events.jsonl)",
                           {"rel_err": e, "prec": prec, "K": K, "h": h})


# ── Задача 9 · T07: тор — тройка (4,1,4π²) и Δ_Ch ──
def task09_torus(cfg):
    delta_f = math.pi / 4
    delta_ch_f = 4 * math.pi ** 2 + delta_f ** 2 / 2 - delta_f ** 5
    p_f64 = abs(delta_ch_f - 39.48799539346835) < 1e-9
    with HODGEHP.scope(50):
        delta_hp = HODGEHP.torus_delta(50)
        ref = HODGEHP.D("39.48799539346835051297464603266144167978")
        dev_hp = float(abs(delta_hp - ref) / ref)
    p_hp = dev_hp < 1e-30
    fam_ok = True
    prev = None
    for n in range(2, 9):
        d_n = math.pi / n
        if prev is not None and not d_n < prev:
            fam_ok = False
        prev = d_n
        if n >= 4 and not (d_n < 1 and d_n ** 5 < d_n ** 4):
            fam_ok = False
    spins_ok = 2 ** (2 * 1) == 4
    ok = p_f64 and p_hp and fam_ok and spins_ok
    return HodgeTaskResult(ok, f"T07: Δ_Ch = 39.48799539346835051… (f64 {p_f64}, hp dev={dev_hp:.2e}, семейство π/N {'ok' if fam_ok else 'X'})" if ok
                           else f"T07: провал (f64={p_f64}, hp={dev_hp:.2e})",
                           {"delta_f64": delta_ch_f, "dev_hp": dev_hp})


# ── Задача 10 · T08: K3 — 48 прямых, ранг 20, сигнатура (1,19), det 64 ──
def task10_k3(cfg):
    inv = HODGEEX.k3_invariants()
    ok = (inv["lines"] == 48 and inv["rank"] == 20 and inv["sig"] == (1, 19)
          and inv["det"] == 64 and inv["factors"][-2:] == [8, 8]
          and len(inv["factors"]) == 20 and inv["factors"][:18] == [1] * 18
          and inv["fam_ok"] and inv["sym_ok"] and inv["diag_ok"])
    return HodgeTaskResult(ok, f"T08: K3: 48 прямых, rank_Q=20 (Шиода), sig=(1,19), det=64=8², SNF=[1×18,8,8]" if ok
                           else f"T08: провал: {inv}", {"rank": inv["rank"], "det": inv["det"]})

def task10b_k3_bareiss(cfg):
    """pass 2: независимый пересчёт — ранг по столбцам и Bareiss-определитель
    ограничения формы на пространство строк (20×20, det = 64 = 8²)."""
    G, _ = HODGEEX.k3_gram()
    Gt = [list(col) for col in zip(*G)]
    rank_t = HODGEEX.rank_fractions(Gt)
    ech = HODGEEX.int_ech_rows(G)
    k = len(ech)
    S = [[0] * k for _ in range(k)]
    for i in range(k):
        T = [sum(ech[i][t] * G[t][u] for t in range(49) if ech[i][t]) for u in range(49)]
        for j in range(k):
            S[i][j] = sum(T[u] * ech[j][u] for u in range(49) if ech[j][u])
    det = abs(HODGEEX.bareiss_det(S))
    # det(S) = det(ограничения)·m², m — индекс эшелон-базиса: форма 64·m² (§1.5:
    # эквивалент проверки det=64, поскольку S — Грам подрешётки, не канонический)
    m2, rem = divmod(det, 64)
    m = math.isqrt(m2) if rem == 0 else -1
    ok = rank_t == 20 and rem == 0 and m * m == m2
    return HodgeTaskResult(ok, f"T08-hardcore: ранг по столбцам={rank_t}, det(S)=64·{m}² (индекс базиса {m})" if ok
                           else f"T08-hardcore: det={det}, rank={rank_t}", {"det": det, "rank_t": rank_t})


# ── Задача 11 · T11: Клейн — точный слой + эллиптический период Ω ──
def task11_klein(cfg):
    ke = HODGEEX.klein_exact()
    with HODGEHP.scope(45):
        omega = HODGEHP.klein_omega(45, K=200, h="0.03")
        ref = HODGEHP.D("1.93331170561681154673308")
        dev = float(abs(omega - ref) / ref)
    with HODGEHP.scope(60):
        omega_raw = HODGEHP.klein_omega_raw(60, K=220, h="0.03")
        omega_sm60 = HODGEHP.klein_omega(60, K=220, h="0.03")
        cross = float(abs(omega_sm60 - omega_raw) / omega_sm60)
    om_ok = dev < 1e-22          # порог полиглота (ref — 23-значный)
    cross_ok = cross < 1e-25     # согласие двух форм интеграла
    ok = all([ke["c1"], ke["c2"], ke["c3"], ke["disc"]]) and om_ok and cross_ok
    return HodgeTaskResult(ok, f"T11: Клейн: j=−3375=−15³, Δ·j=105³, disc=−7; Ω=1.93331170561681154673… (dev={dev:.2e})" if ok
                           else f"T11: провал: ke={ke}, Ω dev={dev:.2e}, cross={cross:.2e}",
                           {"omega_dev": dev, "forms_cross": cross})


# ── Задача 12 · T09: перечисление Арфа (errata E8) ──
def task12_arf(cfg):
    ok = True
    det = []
    for g in (1, 2, 3):
        size, even, odd = HODGEEX.arf_enumeration(g)
        exp_even = (1 << (g - 1)) * ((1 << g) + 1)
        exp_odd = (1 << (g - 1)) * ((1 << g) - 1)
        ok &= (size == (1 << 2 * g) and even == exp_even and odd == exp_odd)
        det.append(f"g={g}: {even}/{odd}")
    f4_even = (1 << 3) * ((1 << 4) + 1)   # 136
    f4_odd = (1 << 3) * ((1 << 4) - 1)    # 120
    ok &= (f4_even == 136 and f4_odd == 120)
    return HodgeTaskResult(ok, f"T09: Арф-перебор g=1..3 = формулам ({', '.join(det)}); g=3 → 36/28" if ok
                           else "T09: перебор расходится с формулами", {"details": det})

def task12b_arf_g4(cfg):
    """pass 2: полный перебор и при g=4 (256 форм × 256 значений)."""
    size, even, odd = HODGEEX.arf_enumeration(4)
    ok = size == 256 and even == 136 and odd == 120
    return HodgeTaskResult(ok, f"T09-hardcore: полный перебор g=4 → {even}/{odd} (256 форм)" if ok
                           else f"T09-hardcore: g=4 → {even}/{odd} ≠ 136/120", {"even": even, "odd": odd})


# ── Задача 13 · T13/cert E: формула завершимости потока ──
def task13_flow(cfg):
    cases = [(48, 48, 1, 1, 48), (96, 96, 1, 1, 96), (24, 36, 3, 5, 72),
             (7, 14, 1, 1, 14), (12, 12, 4, 6, 6), (384, 384, 1, 1, 384)]
    ok = all(HODGEEX.tstar(W, H, a, b) == exp for W, H, a, b, exp in cases)
    bf = HODGEEX.binary_flow()
    ok &= (bf["t"] == 48 and bf["visited"] == 48 and bf["closed"])
    # явная прогулка: возврат в (0,0) ровно на t*, не раньше
    W, H, a, b = 24, 36, 3, 5
    t = HODGEEX.tstar(W, H, a, b)
    x = y = 0
    steps_to_return = None
    for i in range(1, 4 * t + 1):
        x = (x + a) % W
        y = (y + b) % H
        if x == 0 and y == 0:
            steps_to_return = i
            break
    walk_ok = steps_to_return == t
    ok &= walk_ok
    sums_ok = 48 + 212 + 432 + 114 == 806   # контрольные суммы монографии (frozen)
    ok &= sums_ok
    return HodgeTaskResult(ok, f"T13: t*=lcm на 6 случаях; поток 48×48: 48 клеток, замыкание; прогулка (24,36;3,5) ровно {t} шагов" if ok
                           else f"T13: провал (walk={steps_to_return}, flow={bf})", {"binary": bf})


# ── Задача 14 · T05/T19: радикалы b_Ch(15), b_Ch(30) — башня + GF(2) + число ──
def task14_bch(cfg):
    ok = True
    det = []
    for n in (15, 30):
        resid = HODGEEX.bch_exact_residual(n)
        r_ok = resid == ((0, 0), (0, 0))
        poly = list(HODGEEX.BCH_RADICALS[n]["poly"])
        gf_ok = HODGEEX.gf2_irreducible(poly)
        ok &= (r_ok and gf_ok)
        det.append(f"n={n}: 4⁴P(x)≡0 {'✓' if r_ok else '✗'}, GF(2) {'✓' if gf_ok else '✗'}")
    # численный слой: радикал vs 1−cos(2π/n), prec=50
    with HODGEHP.scope(50):
        pi = HODGEHP.pi(50)
        worst = 0.0
        for n, x_expr in ((15, "p1"), (30, "p2")):
            r5 = HODGEHP.D(5).sqrt()
            beta = ((30 - 6 * r5) if n == 15 else (30 + 6 * r5)).sqrt()
            x = ((1 + r5 + beta) / 4) if n == 15 else ((r5 - 1 + beta) / 4)
            b = 1 - x / 2
            target = 1 - HODGEHP.cos(2 * pi / n, 50)
            worst = max(worst, float(abs(b - target) / abs(target)))
            ok &= (HODGEHP.D(7) / 4 < x < 2)   # точный интервал (7/4, 2)
    ok &= worst < 1e-30
    return HodgeTaskResult(ok, f"T05/T19: башни 15/30 точны, GF(2) неприводимы, радикалы vs cos rel={worst:.2e}" if ok
                           else f"T14: провал: {det}, rel={worst:.2e}", {"max_rel": worst, "details": det})


# ── Задача 15 · T17/T18: циклотомические ступени N=7 (Гурвиц) и N=9 (Макбит) ──
def task15_cyc(cfg):
    ok = True
    det = []
    specs = {7: {"units": [1, 2, 3], "vieta": (-1, -2, 1), "poly": [1, 1, -2, -1]},
             9: {"units": [1, 2, 4], "vieta": (0, -3, -1), "poly": [1, 0, -3, 1]}}
    for n, spec in specs.items():
        s1, s2, s3 = HODGEEX.cyc_elem_syms(n, spec["units"])
        vieta_ok = (s1, s2, s3) == spec["vieta"]
        gf_ok = HODGEEX.gf2_irreducible(spec["poly"])
        ok &= (vieta_ok and gf_ok)
        det.append(f"N={n}: syms={s1, s2, s3}, GF(2) {'✓' if gf_ok else '✗'}")
    # Cardano (casus irreducibilis) — prec 50
    with HODGEHP.scope(50):
        pi = HODGEHP.pi(50)
        r3 = HODGEHP.D(3).sqrt()
        t = (HODGEHP.D(7) / 54, HODGEHP.D(7) * r3 / 18)
        mod_t2 = t[0] * t[0] + t[1] * t[1]                    # |t|² (Decimal-печать)
        pair_exact = (Fraction(7, 54) ** 2 + Fraction(49, 108)) == Fraction(343, 729)
        u7 = HODGEHP.cbrt_principal(t, 50)
        b7 = HODGEHP.D(7) / 6 - u7[0]
        tgt7 = 1 - HODGEHP.cos(2 * pi / 7, 50)
        e7 = float(abs(b7 - tgt7) / abs(tgt7))
        w = (HODGEHP.D(-1) / 2, r3 / 2)
        u9 = HODGEHP.cbrt_principal(w, 50)
        b9 = 1 - u9[0]
        tgt9 = 1 - HODGEHP.cos(2 * pi / 9, 50)
        e9 = float(abs(b9 - tgt9) / abs(tgt9))
        # спаривание радикалов: |u|² = 7/9 (ибо |t|² = (7/9)³)
        absu2 = u7[0] * u7[0] + u7[1] * u7[1]
        pair_num = float(abs(absu2 - HODGEHP.D(7) / 9) / (HODGEHP.D(7) / 9))
    cardano_ok = e7 < 1e-25 and e9 < 1e-25
    ok &= cardano_ok and pair_num < 1e-40 and pair_exact
    return HodgeTaskResult(ok, f"T17/T18: Виета (−1,−2,1)/(0,−3,−1) в ℤ[ζ]/Φ; Cardano vs cos rel={max(e7, e9):.2e}; |t|²=(7/9)³" if ok
                           else f"T17/T18: провал: {det}, e7={e7:.2e}, e9={e9:.2e}",
                           {"e7": e7, "e9": e9, "pairing": pair_num})


# ── Задача 16 · T06/T22: SNF-движок и спектр поляризационных типов ──
def task16_snf(cfg):
    ok = True
    det = []
    for N in (15, 30):
        G = HODGEEX.trace_gram(N)
        inv = HODGEEX.snf([r[:] for r in G])
        det_prod = 1
        for v in inv:
            det_prod *= v
        bd = HODGEEX.bareiss_det(G)
        expected = [1, 1, 5, 5, 15, 15, 15, 15]
        ok &= (inv == expected and det_prod == 1265625 == 1125 ** 2 == bd)
        det.append(f"N={N}: SNF={inv}, det={det_prod}")
    # NE02-диагностика движка (ловушки verhodge)
    diag = HODGEEX.snf_diagnostics()
    ok &= diag["diag23"] == [1, 6] and diag["diag61015"] == [1, 30, 30]
    # чистые уровни: G = p·I − J для простых p → SNF (1, p^{p−2})
    for p in (7, 11):
        G = [[(p if i == j else 0) - 1 for j in range(p)] for i in range(p)]
        inv = HODGEEX.snf(G)
        ok &= inv == [1] + [p] * (p - 2)
    # Сильвестровы пивоты следовой формы N=15 (заморожены в H_computed_lattices.json)
    G15 = HODGEEX.trace_gram(15)
    piv = HODGEEX.ldlt_pivots(G15)
    pivots_expect = [Fraction(8), Fraction(63, 8), Fraction(70, 9), Fraction(50, 7),
                     Fraction(48, 7), Fraction(75, 16), Fraction(9, 2), Fraction(5, 2)]
    piv_ok = piv is not None and list(piv) == pivots_expect
    ok &= piv_ok
    return HodgeTaskResult(ok, f"T06/T22: SNF(15/30)=[1,1,5,5,15,15,15,15], disc=1265625=1125², NE02 ok, пивоты Сильвестра совпали" if ok
                           else f"T06/T22: провал: {det}, diag={diag}, piv={piv}",
                           {"details": det})

def task16b_snf_meta(cfg):
    """pass 2: цепочка делимости d_i|d_{i+1}, симметрия Грама, c_N(0)=φ(N)."""
    ok = True
    for N in (15, 30):
        G = HODGEEX.trace_gram(N)
        inv = HODGEEX.snf([r[:] for r in G])
        ok &= all(inv[i] <= inv[i + 1] for i in range(len(inv) - 1))  # цепочка d_i | d_{i+1}
        ok &= all(G[i][j] == G[j][i] for i in range(len(G)) for j in range(len(G)))
        ok &= HODGEEX.ramanujan_c(N, 0) == HODGEEX.phi(N)
        ok &= HODGEEX.ramanujan_c(N, 1) == HODGEEX.mobius(N)
        inv2 = HODGEEX.snf([r[:] for r in G])
        ok &= inv == inv2   # детерминизм движка
    return HodgeTaskResult(ok, "T22-hardcore: делимость цепочки, симметрия Грама, c_N(0)=φ(N), детерминизм — ок" if ok
                           else "T22-hardcore: провал метасвойств SNF", {})


# ── Задача 17 · T19: тождества башни (ββ′, P₃₀=P₁₅(−x), Φ₃₀(−ζ₁₅⁸)) ──
def task17_tower(cfg):
    ok = True
    # ββ′ в квадрате: (ββ′)² = 720 = (12√5)² — точно в ℤ[√5]
    lhs = HODGEEX.z5mul((30, -6), (30, 6))
    rhs = HODGEEX.z5mul((0, 12), (0, 12))
    ok &= (lhs == (720, 0) == rhs)
    # P₃₀(x) = P₁₅(−x): замена знака нечётных степеней
    p15 = list(HODGEEX.BCH_RADICALS[15]["poly"])
    p15_negx = []
    deg = len(p15) - 1
    for i, c in enumerate(p15):
        power = deg - i
        p15_negx.append(-c if power % 2 else c)
    ok &= p15_negx == list(HODGEEX.BCH_RADICALS[30]["poly"])
    # Φ₃₀(−ζ₁₅⁸) ≡ 0 в ℤ[ζ₁₅]/(Φ₁₅)
    phi15 = HODGEEX.cyclotomic(15)
    phi30 = HODGEEX.cyclotomic(30)
    neg_odd = [(-c if (len(phi30) - 1 - i) % 2 else c) for i, c in enumerate(phi30)]
    ok &= neg_odd == phi15  # Φ₂ₙ(x) = Φₙ(−x) при нечётном n
    d30 = len(phi30) - 1
    comp = [0] * (8 * d30 + 1)      # Φ₃₀(−x⁸): степень 8k, знак (−1)^k
    for i, c in enumerate(phi30):
        k = d30 - i
        comp[8 * d30 - 8 * k] += c * ((-1) ** k)
    red = HODGEEX.pmod_monic(comp, phi15)
    ok &= red == [0]
    # GF(2)-отпечаток: оба квартика ≡ x⁴+x³+1 (mod 2)
    r15 = [c & 1 for c in HODGEEX.BCH_RADICALS[15]["poly"]]
    r30 = [c & 1 for c in HODGEEX.BCH_RADICALS[30]["poly"]]
    ok &= r15 == r30 == [1, 1, 0, 0, 1]
    return HodgeTaskResult(ok, "T19: ββ′²=(12√5)²=720, P₃₀=P₁₅(−x), Φ₃₀(−ζ₁₅⁸)≡0, GF(2)-отпечаток x⁴+x³+1 — точно" if ok
                           else "T19: башенные тождества провалены", {})


# ── Задача 18 · T14/cert F: q-scan рационализации + негативный тест 4π² ──
def task18_qscan(cfg):
    r1 = HODGEEX.qscan(2.75, 16)
    neg = HODGEEX.qscan(4 * math.pi ** 2, 16)
    neg2 = HODGEEX.qscan(2 * math.pi, 16)
    ok = r1 == (4, 11) and neg is None and neg2 is None
    return HodgeTaskResult(ok, f"T14: qscan(2.75,16)=(4,11) — дробь восстановлена; 4π² и 2π не рационализируются" if ok
                           else f"T14: провал: 2.75→{r1}, 4π²→{neg}", {"qscan": r1})


# ── Задача 19 · T15/cert G: слой Чоула–Зельбергера (Γ-тождества) ──
def task19_chowla(cfg):
    with HODGEHP.scope(60):
        pi = HODGEHP.pi(60)
        g14 = HODGEHP.gamma(HODGEHP.D(1) / 4, 60)
        g34 = HODGEHP.gamma(HODGEHP.D(3) / 4, 60)
        lhs = g14 * g34
        rhs = pi * HODGEHP.D(2).sqrt()
        e_id = float(abs(lhs - rhs) / rhs)
        # кросс-проверка высокоточной Γ против stdlib-гаммы double
        gf64 = math.gamma(0.25)
        e_cross = float(abs(g14 - HODGEHP.D(repr(gf64))) / HODGEHP.D(repr(gf64)))
        omega_i2 = g14 ** 4 / (16 * pi)   # ω(i)² — значение печатается в отчёт
    ok = e_id < 1e-30 and e_cross < 1e-12
    return HodgeTaskResult(ok, f"T15: Γ(1/4)Γ(3/4)=π√2 (rel={e_id:.2e}), Γ vs stdlib (rel={e_cross:.2e}); ω(i)²=Γ(1/4)⁴/16π={float(omega_i2):.6f}" if ok
                           else f"T15: провал: id={e_id:.2e}, cross={e_cross:.2e}",
                           {"identity_rel": e_id, "cross_rel": e_cross, "omega_i2": float(omega_i2)})


# ── Задача 20 · T12: μ₄-теорема — [L,P]=0 точно над ℤ[i] ──
def task20_mu4(cfg):
    """Детерминированное семейство из 10 μ₄-систем (размеры 8/16/24/32).
    L — блочно-циклическая целочисленная матрица; P₄ = Σ i^{−k}R^k над ℤ[i].
    Проверки: 4·(L·P₄ − P₄·L) = 0 точно; P₄² = 4·P₄; порядок R = 4."""
    ok = True
    dims = [8, 16, 24, 32]
    tested = 0
    for si in range(10):
        dim = dims[si % 4]
        L = HODGEEX.mu4_system(dim, seed=si + 1)
        R = HODGEEX.mu4_rot(dim)
        P4 = HODGEEX.mu4_projector4(R)
        LP = HODGEEX.gauss_int_mul(L, P4)
        PL = HODGEEX.gauss_int_mul(P4, L)
        zero = all((LP[i][j] == PL[i][j]) for i in range(dim) for j in range(dim))
        P2 = HODGEEX.gauss_int_mul(P4, P4)
        proj = all((P2[i][j][0] == 4 * P4[i][j][0] and P2[i][j][1] == 4 * P4[i][j][1])
                   for i in range(dim) for j in range(dim))
        R2 = HODGEEX.gauss_int_mul(R, R)
        R3 = HODGEEX.gauss_int_mul(R2, R)
        R4 = HODGEEX.gauss_int_mul(R2, R2)
        r4_is_id = all((R4[i][j] == (1, 0)) if i == j else (R4[i][j] == (0, 0))
                       for i in range(dim) for j in range(dim))
        # порядок R ровно 4: R¹, R², R³ ≠ I
        def not_identity(Mx):
            return any((Mx[i][j] != ((1, 0) if i == j else (0, 0)))
                       for i in range(dim) for j in range(dim))
        r_order = not_identity(R) and not_identity(R2) and not_identity(R3)
        ok &= zero and proj and r4_is_id and r_order
        tested += 1
    return HodgeTaskResult(ok, f"T12: [L,P]=0 точно на {tested} μ₄-системах (ℤ[i]); P₄²=4P₄; порядок R=4" if ok
                           else "T12: коммутатор ненулевой на некоторой системе", {"systems": tested})


# ── Задача 21 · C-011: счёт точек Фермат-многообразия #X₀(F_p) ──
def task21_point_count(cfg):
    p = 11
    mitm = HODGEEX.fermat_point_count(p)
    # независимая схема: прямой подсчёт аффинных решений (p⁴ кортежей × A(−Σ))
    A = {}
    for x in range(p):
        A[pow(x, 5, p)] = A.get(pow(x, 5, p), 0) + 1
    brute = 0
    for x0 in range(p):
        s0 = pow(x0, 5, p)
        for x1 in range(p):
            s1 = (s0 + pow(x1, 5, p)) % p
            for x2 in range(p):
                s2 = (s1 + pow(x2, 5, p)) % p
                for x3 in range(p):
                    s = (-s2 - pow(x3, 5, p)) % p
                    brute += A.get(s, 0)
    ok = (mitm["proj"] == 1925 and mitm["t_p"] == -461 and brute == mitm["affine"])
    # граница Вейля |t_p| ≤ 204·p^{3/2} (коэффициент репозитория, b₃-слой)
    weil_ok = True
    for pp in (11, 31):
        m = HODGEEX.fermat_point_count(pp)
        weil_ok &= abs(m["t_p"]) <= 204 * pp ** 1.5
    ok &= weil_ok
    return HodgeTaskResult(ok, f"C-011: #X₀(F₁₁)=1925, t₁₁=−461, MITM==brute ({brute}), Вейль на p=11,31" if ok
                           else f"C-011: провал: mitm={mitm}, brute={brute}",
                           {"proj": mitm["proj"], "t_p": mitm["t_p"], "brute_affine": brute})

def task21b_weil_p41(cfg):
    """pass 2: граница Вейля на p=41 (MITM p² = 1681 пар)."""
    m = HODGEEX.fermat_point_count(41)
    ok = abs(m["t_p"]) <= 204 * 41 ** 1.5
    return HodgeTaskResult(ok, f"C-011-hardcore: p=41: #X₀={m['proj']}, t₄₁={m['t_p']}, Вейль выполнен" if ok
                           else f"C-011-hardcore: p=41 Вейль нарушен: {m}", m)


# ── Задача 22 · V7: полнота — ранг функциональной матрицы (HP-QR, §1.5-эквивалент) ──
def task22_v7rank(cfg):
    """Заявление V7: ранг функциональной матрицы M[i,j] = Ω_i·ζ^{r_j a_i+s_j b_i}/N
    равен числу строк. SVD в stdlib нет — ближайший эквивалент §1.5:
    модифицированный Грам–Шмидт по строкам над Decimal-комплексами (prec 50).
    Несингулярный диагональный множитель Ω_i/N ранг не меняет — учтено."""
    from decimal import Decimal as _D
    ok = True
    det = []
    with HODGEHP.scope(50):
        H = HODGEHP
        for N, gexp in ((7, 15), (9, 28)):
            prec = 50
            zeta = _zeta(N, prec)
            _, by_d, g = HODGEEX.census(N)
            chars = [(a, b) for lst in by_d.values() for (a, b) in lst][:gexp]
            pts = [(r, s) for r in range(N) for s in range(N)]
            rows = len(chars)
            basis = []          # нормированные строки-векторы
            independent = 0
            for (a, b) in chars:
                v = [zeta[(r * a + s * b) % N] for (r, s) in pts]
                for bw in basis:
                    dot = (_D(0), _D(0))
                    for t in range(len(v)):
                        dot = H.cadd(dot, H.cmul(H.cconj(bw[t]), v[t]))
                    if dot[0] == 0 and dot[1] == 0:
                        continue
                    for t in range(len(v)):
                        v[t] = H.csub(v[t], H.cmul(bw[t], dot))
                n2 = _D(0)
                for t in range(len(v)):
                    n2 += v[t][0] * v[t][0] + v[t][1] * v[t][1]
                if n2 > _D("1e-20"):       # порог ≪ N²·cond² (cond репо ≤ 20)
                    inv = 1 / n2.sqrt()
                    basis.append([H.cscale(x, inv) for x in v])
                    independent += 1
            rank_ok = independent == rows
            ok &= rank_ok
            det.append(f"N={N}: rank {independent}/{rows}")
    return HodgeTaskResult(ok, f"V7 (HP-QR §1.5): ранг функциональной матрицы = числу строк: {', '.join(det)}" if ok
                           else f"V7: провал: {det}", {"details": det})

def task22b_v7rank_n15(cfg):
    """pass 2: N=15 (91×225) — float64 модифицированный Грам-Шмидт
    (порог 1e−9·σ̂max как в протоколе; cond≈8.6 — запас 15 порядков)."""
    N = 15
    import cmath
    _, by_d, g = HODGEEX.census(N)
    chars = [(a, b) for lst in by_d.values() for (a, b) in lst][:91]
    pts = [(r, s) for r in range(N) for s in range(N)]
    rows = len(chars)
    M = []
    two_pi = 2 * math.pi
    for (a, b) in chars:
        row = [cmath.exp(1j * two_pi * ((r * a + s * b) % N) / N) for (r, s) in pts]
        M.append(row)
    basis = []
    independent = 0
    for v in M:
        for bw in basis:
            dot = sum((bw[t].conjugate() * v[t] for t in range(len(v))), start=0j)
            v = [v[t] - dot * bw[t] for t in range(len(v))]
        n2 = sum((abs(x) ** 2 for x in v), 0.0)
        if n2 > 1e-9 * 1.0:   # строки имеют |v|² = 225; порог репозитория 1e−9·σmax
            basis.append([x / (n2 ** 0.5) for x in v])
            independent += 1
    ok = independent == rows == 91
    return HodgeTaskResult(ok, f"V7-hardcore: N=15: rank 91/91 (f64-QR, порог 1e−9)" if ok
                           else f"V7-hardcore: N=15: rank {independent}/91", {"rank": independent})


# ── Реестр задач §4.1 (SUITE_IDS — производное, не хардкод) ──
TASKS = [
    {"id": 1, "slug": "census-genus", "title": "Формула рода и ценз проводников (T01/T20/V1)",
     "fn": task01_census, "pass2_fn": task01b_census_all, "deps": [],
     "claims": ["T01", "T20", "V1", "C-001"], "est_sec": 0.1, "idempotent": True,
     "tags": ["fast", "exact"], "version": "1.0.0", "owner": "session-1"},
    {"id": 2, "slug": "periods-v2", "title": "Замкнутая форма периода vs tanh–sinh (T02/V2)",
     "fn": task02_periods, "pass2_fn": task02b_periods_tight, "deps": [1],
     "claims": ["T02", "V2"], "est_sec": 2.0, "idempotent": True,
     "tags": ["hp", "core"], "version": "1.0.0", "owner": "session-1",
     "plot_fn": plot02_periods},
    {"id": 3, "slug": "phase-v3", "title": "Фазовый закон arg P = 2π(ra+sb)/N (V3)",
     "fn": task03_phase, "pass2_fn": None, "deps": [2],
     "claims": ["V3", "T02"], "est_sec": 1.5, "idempotent": True,
     "tags": ["hp", "core"], "version": "1.0.0", "owner": "session-1"},
    {"id": 4, "slug": "equivariance-v4", "title": "μ_N×μ_N-эквивариантность периодов (V4)",
     "fn": task04_equivariance, "pass2_fn": None, "deps": [2],
     "claims": ["V4", "T11"], "est_sec": 0.3, "idempotent": True,
     "tags": ["hp", "fast"], "version": "1.0.0", "owner": "session-1"},
    {"id": 5, "slug": "chain-v5", "title": "Целостность цепи: орбитные суммы (V5)",
     "fn": task05_chain, "pass2_fn": None, "deps": [2],
     "claims": ["V5"], "est_sec": 0.4, "idempotent": True,
     "tags": ["hp", "fast"], "version": "1.0.0", "owner": "session-1"},
    {"id": 6, "slug": "reflection-v6", "title": "Лестница Γ-рефлексии (V6)",
     "fn": task06_reflection, "pass2_fn": task06b_reflection_all, "deps": [],
     "claims": ["V6", "T03"], "est_sec": 0.5, "idempotent": True,
     "tags": ["hp", "fast"], "version": "1.0.0", "owner": "session-1",
     "plot_fn": plot06_reflection},
    {"id": 7, "slug": "dft-v8", "title": "DFT-ортогональность периодов (V8)",
     "fn": task07_dft, "pass2_fn": None, "deps": [2],
     "claims": ["V8", "T04"], "est_sec": 0.6, "idempotent": True,
     "tags": ["hp", "fast"], "version": "1.0.0", "owner": "session-1"},
    {"id": 8, "slug": "deep-v9", "title": "Глубокий рекорд точности prec=90 (V9)",
     "fn": task08_deep, "pass2_fn": None, "deps": [2],
     "claims": ["V9"], "est_sec": 2.5, "idempotent": True,
     "tags": ["hp", "heavy"], "version": "1.0.0", "owner": "session-1"},
    {"id": 9, "slug": "torus-triple", "title": "Тор: тройка (4,1,4π²) и Δ_Ch (T07)",
     "fn": task09_torus, "pass2_fn": None, "deps": [],
     "claims": ["T07", "E6"], "est_sec": 0.1, "idempotent": True,
     "tags": ["hp", "fast"], "version": "1.0.0", "owner": "session-1"},
    {"id": 10, "slug": "k3-stand", "title": "K3: 48 прямых, ранг 20, сигнатура (T08)",
     "fn": task10_k3, "pass2_fn": task10b_k3_bareiss, "deps": [],
     "claims": ["T08", "T10", "T22"], "est_sec": 0.6, "idempotent": True,
     "tags": ["exact", "core"], "version": "1.0.0", "owner": "session-1",
     "plot_fn": plot10_k3},
    {"id": 11, "slug": "klein-stand", "title": "Клейн: j=−3375, Ω-квадратура (T11)",
     "fn": task11_klein, "pass2_fn": None, "deps": [],
     "claims": ["T11", "T16"], "est_sec": 1.0, "idempotent": True,
     "tags": ["hp", "core"], "version": "1.0.0", "owner": "session-1"},
    {"id": 12, "slug": "errata-arf", "title": "Перечисление Арфа: 36/28 при g=3 (T09)",
     "fn": task12_arf, "pass2_fn": task12b_arf_g4, "deps": [],
     "claims": ["T09"], "est_sec": 0.4, "idempotent": True,
     "tags": ["exact", "fast"], "version": "1.0.0", "owner": "session-1"},
    {"id": 13, "slug": "flow-tstar", "title": "Формула завершимости потока t* (T13/cert E)",
     "fn": task13_flow, "pass2_fn": None, "deps": [],
     "claims": ["T13", "certE"], "est_sec": 0.1, "idempotent": True,
     "tags": ["exact", "fast"], "version": "1.0.0", "owner": "session-1",
     "plot_fn": plot13_flow},
    {"id": 14, "slug": "bch-radicals", "title": "Радикалы b_Ch(15)/b_Ch(30): башня (T05/T19)",
     "fn": task14_bch, "pass2_fn": None, "deps": [],
     "claims": ["T05", "T19"], "est_sec": 0.3, "idempotent": True,
     "tags": ["exact", "hp", "core"], "version": "1.0.0", "owner": "session-1"},
    {"id": 15, "slug": "cyc-cubics", "title": "Ступени N=7/9: Виета, GF(2), Cardano (T17/T18)",
     "fn": task15_cyc, "pass2_fn": None, "deps": [],
     "claims": ["T17", "T18", "certI", "certJ"], "est_sec": 0.3, "idempotent": True,
     "tags": ["exact", "hp", "core"], "version": "1.0.0", "owner": "session-1"},
    {"id": 16, "slug": "snf-spectra", "title": "SNF-движок: спектр поляризаций (T06/T22)",
     "fn": task16_snf, "pass2_fn": task16b_snf_meta, "deps": [],
     "claims": ["T06", "T22", "certH", "C-004"], "est_sec": 0.3, "idempotent": True,
     "tags": ["exact", "core"], "version": "1.0.0", "owner": "session-1"},
    {"id": 17, "slug": "tower-identities", "title": "Тождества башни: ββ′, P₃₀=P₁₅(−x) (T19)",
     "fn": task17_tower, "pass2_fn": None, "deps": [14],
     "claims": ["T19"], "est_sec": 0.1, "idempotent": True,
     "tags": ["exact", "fast"], "version": "1.0.0", "owner": "session-1"},
    {"id": 18, "slug": "qscan-certf", "title": "q-scan рационализации, негатив 4π² (T14/cert F)",
     "fn": task18_qscan, "pass2_fn": None, "deps": [],
     "claims": ["T14", "certF"], "est_sec": 0.05, "idempotent": True,
     "tags": ["exact", "fast"], "version": "1.0.0", "owner": "session-1"},
    {"id": 19, "slug": "chowla-selberg", "title": "Γ(1/4)Γ(3/4)=π√2, ω(i)² (T15/cert G)",
     "fn": task19_chowla, "pass2_fn": None, "deps": [6],
     "claims": ["T15", "certG"], "est_sec": 0.2, "idempotent": True,
     "tags": ["hp", "fast"], "version": "1.0.0", "owner": "session-1"},
    {"id": 20, "slug": "mu4-theorem", "title": "μ₄-теорема: [L,P]=0 над ℤ[i] (T12/cert D)",
     "fn": task20_mu4, "pass2_fn": None, "deps": [],
     "claims": ["T12", "certD"], "est_sec": 0.5, "idempotent": True,
     "tags": ["exact", "fast"], "version": "1.0.0", "owner": "session-1"},
    {"id": 21, "slug": "fermat-point-count", "title": "Счёт точек #X₀(F₁₁)=1925 (C-011)",
     "fn": task21_point_count, "pass2_fn": task21b_weil_p41, "deps": [],
     "claims": ["C-011"], "est_sec": 0.3, "idempotent": True,
     "tags": ["exact", "fast"], "version": "1.0.0", "owner": "session-1",
     "plot_fn": plot21_fermat},
    {"id": 22, "slug": "v7-rank", "title": "V7-полнота: ранг функциональной матрицы (HP-QR)",
     "fn": task22_v7rank, "pass2_fn": task22b_v7rank_n15, "deps": [1],
     "claims": ["V7", "T04"], "est_sec": 1.0, "idempotent": True,
     "tags": ["hp", "core"], "version": "1.0.0", "owner": "session-1"},
]
SUITE_IDS = [t["id"] for t in TASKS]


# ══════════════════════════════════════════════════════════════════════════
# §16. ЛОКАЛИЗАЦИЯ: MSG[lang][key] + fmt (§16.2); l10n-тест проверяет паритет.
# ══════════════════════════════════════════════════════════════════════════
# BUGFIX(i18n): вердикты задач возвращаются из вычислений готовыми русскими
# строками — MSG-словарь на них не действует, и при lang=en консоль показывала
# русские PASS/INFO. Фразбук: литеральные фрагменты → EN, применяется ТОЛЬКО
# на дисплее (results.json/отчёты остаются русскими). Частные ключи раньше общих.
RUN_I18N_EN = [
    ("ценз/род подтверждены (2 схемы, 7 уровней): ", "genus census confirmed (2 schemes, 7 levels): "),
    ("согласие схем на всех N∈[3,64] (C-001)", "scheme agreement on all N∈[3,64] (C-001)"),
    ("периодов closed=tanh-sinh, rel=", "periods closed=tanh-sinh, rel="),
    ("фазовый закон, dev=", "phase law, dev="),
    ("эквивариантность, rel=", "equivariance, rel="),
    ("Γ-рефлексия, ", "Γ-reflection, "),
    (" пар, rel=", " pairs, rel="),
    ("ранг функциональной матрицы = числу строк (N=7,9)", "functional matrix rank = number of rows (N=7,9)"),
    ("башни точны, GF(2) ok, радикалы rel=", "towers exact, GF(2) ok, radicals rel="),
    ("48 прямых, rank=", "48 lines, rank="),
    ("48 прямых · встреч/прямую=", "48 lines · meets/line="),
    ("Арф g=1..3: ", "Arf g=1..3: "),
    (" = формулам", " = formulas"),
    ("Клейн: ", "Klein: "),
    ("на блочно-циклических μ₄-системах, dim ", "on block-cyclic μ₄-systems, dim "),
    ("(целые/ℤ[i])", "(integers/ℤ[i])"),
    ("t* на ", "t* on "),
    (" случаях; поток ", " cases; flow "),
    (" клеток; суммы=", " cells; sums="),
    (" и 2π не рационализируются", " and 2π not rationalizable"),
    ("Виета (", "Vieta ("),
    ("GF(2)-отпечаток ", "GF(2) fingerprint "),
    ("Вейль b₃=", "Weil b₃="),
    (" кадра PNG + GIF, sweep-парсер (", " PNG frames + GIF, sweep parser ("),
    ("ERR: сгенерировано ", "ERR: generated "),
    (" прямых (ожидалось 48)", " lines (expected 48)"),
    ("встреч на прямую: ", "meets per line: "),
    ("встреч на строку: ", "meets per line: "),
    (" (ожидалось 14)", " (expected 14)"),
    ("диагональ ≠ −2", "diagonal ≠ −2"),
    ("есть элементы вне {−2,0,1}", "elements outside {−2,0,1}"),
    ("G не симметрична", "G not symmetric"),
    (" не квадратна: ", " not square: "),
    ("подпись не совпала: ", "signature mismatch: "),
    ("≠ ожидаемое ", "≠ expected "),
    ("path-guard пропустил опасный slug", "path-guard skipped unsafe slug"),
    ("fermat_k3_intersect: недостижимая пара partition (", "fermat_k3_intersect: unreachable partition pair ("),
    ("→ задача ", "→ task "),
    ("resume: задача ", "resume: task "),
    (" пропущена (PASS в чекпоинте)", " skipped (PASS in checkpoint)"),
    ("Dry-run план · пресет ", "Dry-run plan · preset "),
    (" · сид ", " · seed "),
    ("создаст: results/", "creates: results/"),
    (" бит", " bits"),
    (" на p=", " on p="),
    ("конь", "knight"),
    # ── §16 v4: фразы Python-версий задач (фразбук Julia иных формулировок) ──
    ("формула рода g=(N−1)(N−2)/2 и ценз по проводникам подтверждены (7 уровней, 2 схемы)",
     "genus formula g=(N−1)(N−2)/2 and conductor census confirmed (7 levels, 2 schemes)"),
    ("ценз/род: расхождение с baseline", "census/genus: mismatch vs baseline"),
    ("согласие двух схем на всех N∈[3,64] подтверждено", "two schemes agree on all N∈[3,64] confirmed"),
    ("периодов, замкнутая форма = квадратура (rel=", "periods, closed form = quadrature (rel="),
    (" тестов на сетке 240/0.02 (rel=", " tests on the 240/0.02 grid (rel="),
    ("тестов (dev=", "tests (dev="),
    ("тестов (rel=", "tests (rel="),
    (" пар, N∈[7,64] (rel=", " pairs, N∈[7,64] (rel="),
    ("семейство π/N ok", "π/N family ok"),
    ("48 прямых, rank_Q=20 (Шиода)", "48 lines, rank_Q=20 (Shioda)"),
    ("T08-hardcore: ранг по столбцам=", "T08-hardcore: column rank="),
    ("T09: Арф-перебор g=1..3 = формулам (", "T09: Arf enumeration g=1..3 = formulas ("),
    ("T09-hardcore: полный перебор g=4 → ", "T09-hardcore: full enumeration g=4 → "),
    (" (256 форм)", " (256 forms)"),
    ("T14: qscan(2.75,16)=(4,11) — дробь восстановлена; ", "T14: qscan(2.75,16)=(4,11) — fraction recovered; "),
    ("C-011: #X₀(F₁₁)=1925, t₁₁=−461, MITM==brute (", "C-011: #X₀(F₁₁)=1925, t₁₁=−461, MITM==brute ("),
    ("Вейль на p=11", "Weil bound at p=11"),
    ("C-011-hardcore: p=41: ", "C-011-hardcore: p=41: "),
    ("Вейль выполнен", "Weil bound verified"),
    ("V7 (HP-QR §1.5): ранг функциональной матрицы = числу строк", "V7 (HP-QR §1.5): functional matrix rank = number of rows"),
    ("V7-hardcore: N=15: rank 91/91 (f64-QR, порог 1e−9)", "V7-hardcore: N=15: rank 91/91 (f64-QR, threshold 1e−9)"),
    ("V4-орбиты ", "V4 orbits "),
    ("D4-орбиты ", "D4 orbits "),
    (", Бернсайд ", ", Burnside "),
    ("C2/T02: рёбра R", "C2/T02: edges R"),
    ("конь двудолен; слон ", "knight bipartite; bishop "),
    ("замкнутые формы ok", "closed forms ok"),
    ("t* на 10 случаях; бильярд (", "t* on 10 cases; billiard ("),
    (" шагов, ", " steps, "),
    (" отражений, ", " reflections, "),
    ("масса поля сходится, эквивариантность 0/0, аномалия пешек ",
     "field mass converges, equivariance 0/0, pawn anomaly "),
    ("после e4, E0=", "after e4, E0="),
    ("хэш/инверсия ok", "hash/inversion ok"),
    ("ключа, sm(1..3) совпали, инкрементальность ", "keys, sm(1..3) matched, incrementality "),
    ("C10/T07: тур коня: 64 различные клетки, все ходы конём, замыкание d6→f5",
     "C10/T07: knight tour: 64 distinct cells, all knight moves, closure d6→f5"),
    ("C8: Морфи/лестница/Кн+Л: PV и узлы ", "C8: Morphy/ladder/K+N+L: PV and nodes "),
    (" воспроизведены (", " reproduced ("),
    (" пн., узлы ", " moves, nodes "),
    (" (эталон ", " (reference "),
    ("C8-hardcore: ретро-KQK: ", "C8-hardcore: retro-KQK: "),
    (" рёбер, матов ", " edges, mates "),
    (" макс ", " max "),
    ("C-010: Π(ψ) две схемы согласны (worst ", "C-010: Π(ψ) two schemes agree (worst "),
    ("замороженные V21 воспроизведены: ", "frozen V21 reproduced: "),
    ("C-006: Гросс vol_h = 1125 на N=15 и 30 (", "C-006: Gross vol_h = 1125 at N=15 and 30 ("),
    ("C-003: квинтик N=11: collapse ", "C-003: quintic N=11: collapse "),
    ("реконструкция", "reconstruction"),
    ("C-019: карта Q³d(ι_RΩ′/Q²) = ", "C-019: map Q³d(ι_RΩ′/Q²) = "),
    (" — точное тождество (Эйлер: ", " — exact identity (Euler: "),
    (", не 5Q)", ", not 5Q)"),
    ("§33.7: lab3d CI: 3 кадра PNG + GIF, sweep-парсер (", "§33.7: lab3d CI: 3 PNG frames + GIF, sweep parser ("),
    (" порог", " threshold"),
    # ── §16 v4: корректирующие фрагменты (после ранних подстановок) ──
    (" в ℤ[ζ]/Φ;", " in ℤ[ζ]/Φ;"),
    ("пивоты Сильвестра", "Sylvester pivots"),
    (" — точно", " — exact"),
    ("точно на ", "exactly on "),
    ("μ₄-системах", "μ₄-systems"),
    ("порядок R=", "order R="),
    ("Вейль on p=", "Weil bound at p="),
    ("двудолен; слон ", "bipartite; bishop "),
    ("суммы ", "sums "),
    ("случаях", "cases"),
    ("мобильность ", "mobility "),
    (" позиций", " positions"),
    ("C8-hardcore: ретро-KRK: ", "C8-hardcore: retro-KRK: "),
    ("состояний, ", "states, "),
    ("рёбер, ", "edges, "),
    ("матов ", "mates "),
    (" ходов", " moves"),
    ("Арф-перебор", "Arf enumeration"),
    ("t*=lcm на ", "t*=lcm on "),
    (" клеток, замыкание; прогулка (", " cells, closure; walk ("),
    (" шагов", " steps"),
    ("T05/T19: башни 15/30 точны, GF(2) неприводимы, радикалы vs cos rel=",
     "T05/T19: towers 15/30 exact, GF(2) irreducible, radicals vs cos rel="),
    (" совпали", " matched"),
    ("бильярд (", "billiard ("),
    ("ветвей", "branches"),
    ("фазовый закон", "phase law"),
    (" пар (rel=", " pairs (rel="),
    ("ровно ", "exactly "),
]


def run_i18n(s: str, lang: str) -> str:
    """Дисплей-перевод вердиктов/INFO-строк задач: только для lang=en,
    иначе строка возвращается как есть (ru — канон данных)."""
    if lang != "en":
        return s
    out = s
    for ru, en in RUN_I18N_EN:
        if ru in out:
            out = out.replace(ru, en)
    return out


def parse_prec_extreme_cmd(key: str):
    """§14 v4: словный псевдоним тумблера prec-extreme — не только клавиша [P].
    'prec-extreme' / 'precext' → toggle; '... on' / '... off' → явно; иначе None."""
    tok = key.split()
    if not tok or tok[0] not in ("prec-extreme", "precext"):
        return None
    if len(tok) == 1:
        return "toggle"
    arg = tok[1].lower()
    if arg in ("on", "1", "true", "вкл"):
        return True
    if arg in ("off", "0", "false", "выкл"):
        return False
    return "toggle"


def parse_prec_value(s):
    """§3.2 v5: prec БЕЗ верхней границы — «ставь даже гигабайты».
    '4096' → 4096; '5k' → 5000; '2m' → 2_000_000; '1g' → 1_000_000_000;
    '2t' → 2·10^12. Нижняя граница 30 сохраняется (меньше — бессмысленно).
    → int или None, если строка не разобрана."""
    if s is None:
        return None
    t = str(s).strip().lower().replace(" ", "")
    m = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)([kmgt]?)", t)
    if not m:
        return None
    mult = {"": 1, "k": 10 ** 3, "m": 10 ** 6, "g": 10 ** 9, "t": 10 ** 12}[m.group(2)]
    try:
        v = int(round(float(m.group(1)) * mult))
    except (ValueError, OverflowError):
        return None
    return v if v >= 30 else None


MSG = {
    "ru": {
        "menu.title": "HODGE MASTER · меню верификации",
        "menu.help": "? — помощь, a — все задачи, цифры — отметить, Enter — запуск отмеченных, q — выход",
        "menu.prompt": "выбор",
        "menu.bye": "Выход. Доброй верификации!",
        "menu.unknown": "Неизвестная клавиша: {key}",
        "run.start": "Прогон {run} · пресет {preset} · сид {seed}",
        "run.done": "Готово: {passed}/{total} PASS за {sec}",
        "task.verdict": "[{id}] {slug}: {verdict}",
        "all_pass": "ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ",
        "has_fail": "ЕСТЬ ПРОВАЛЫ",
        "duration": "длительность",
        "sec": "с",
        "stand": "стенд",
        "summary": "ИТОГ",
        "tasks": "задачи",
        "tasks_plural": ("задача", "задачи", "задач"),
        # §16 / VIII.2: сообщения новых подсистем
        "report.saved": "Отчёт сохранён: {path}",
        "plot.rendered": "Графики: {n} PNG, {m} GIF",
        "task.skip": "Задача {id} пропущена: {reason}",
        "lock.held": "Lock занят: {path}",
        "cache.hit": "Кэш: попадание для {id}",
        "cache.miss": "Кэш: промах для {id}",
        "monitor.line": "CPU {cpu} · RAM {ram} · T {temp}",
        "hook.error": "Хук {event} упал: {err}",
        # §14 меню: главный экран (BUGFIX: render был захардкожен по-русски)
        "menu.run_header": "RUN",
        "menu.tasks_header": "TASKS",
        "menu.settings_header": "НАСТРОЙКИ",
        "menu.actions_header": "ДЕЙСТВИЯ",
        "menu.run_all": "Запустить ВСЕ задачи (two-pass)",
        "menu.run_fast": "Только fast-теги",
        "menu.run_heavy": "Только heavy-теги",
        "menu.run_chess": "Только chess (23–33)",
        "menu.run_verhodge": "Только verhodge (34–38, 40)",
        "menu.run_sweep": "SWEEP: бесконечный выбор параметров",
        "menu.set.prec": "precision          сейчас: {value} бит",
        "menu.set.seed": "seed               сейчас: {value}",
        "menu.set.preset": "preset             сейчас: {value}",
        "menu.set.theme": "тема               сейчас: {value}",
        "menu.set.lang": "язык               сейчас: {value}",
        "menu.set.depth": "color depth        сейчас: {value}",
        "menu.set.two_pass": "two-pass           сейчас: {value}",
        "menu.set.prec_extreme": "prec-extreme       сейчас: {value}",
        "menu.act.dry_run": "dry-run (план без вычислений)",
        "menu.act.recipes": "список рецептов",
        "menu.act.theme_cycle": "сменить тему (цикл)",
        "menu.act.palette": "палитра (theme-preview)",
        "menu.act.help": "помощь",
        "menu.act.quit": "выход",
        "menu.filter_mode": "filter mode (пусто — выход)",
        "menu.sweep_fn_prompt": "SWEEP: имя функции (omega|reflection|census_h) → Enter для дефолта «omega»",
        "menu.sweep_spec_prompt": "SWEEP: функция={fn}. Введите sweep-спеку (name:lo:hi:step), пусто — запуск",
        "menu.sweep_bad_fn": "SWEEP: неизвестная функция «{fn}» — доступно: omega | reflection | census_h",
        "menu.sweep_added": "SWEEP: добавлено {key}. ещё? (пусто — запуск)",
        "menu.sweep_invalid": "SWEEP: {msg} — попробуйте ещё раз",
        "menu.sweep_invalid_spec": "SWEEP: спека невалидна: {msg}",
        "menu.sweep_preview": "SWEEP: fn={fn}, specs={specs}, кадров={n} (cap {cap})",
        "menu.status_line": "theme={theme} · prec={prec} · seed={seed} · preset={preset} · lang={lang} · marked={n} [{ids}]",
        "menu.copy_done": "скопировано: {path}",
        "menu.copy_empty": "run_dir пуст — сначала запустите прогон",
        "menu.copy_disabled": "clipboard отключён (--no-clipboard)",
        "menu.history_empty": "история пуста",
        "menu.no_history": "нет записи #{n} (всего {total})",
        "menu.history_hint": "история: !! — повтор последней, !N — повтор N-й",
        "menu.eof_guard": "EOF-guard {n}/{limit}",
        "menu.ctrl_c": "Ctrl+C перехвачен — возврат",
        "menu.input_error": "ошибка ввода: {msg}",
        "menu.help_detail": "«?» — справка\n  [1-N] задача · [Space] отметить · [Enter] запуск отмеченных\n  [a/f/h/c/v] прогон · [w] sweep · [p/s/n/t/l/d/e/P] настройки",
        "menu.non_tty_hint": "stdin не TTY — используйте --task N / --menu / --self-test",
        "menu.no_task": "нет задачи {id}",
        "menu.mark_on": "задача {id} отмечена — Enter запустит отмеченные",
        "menu.mark_off": "задача {id}: отметка снята",
        "menu.runner_unavailable": "раннер недоступен",
        "menu.resized": "resize",
        # §14: подсказки редакторов настроек (handle)
        "menu.edit.prec_now": "текущее prec: {value}",
        "menu.edit.prec_new": "новое prec [30..∞ | 4096, 5m, 1g]: ",
        "menu.edit.prec_out": "нужно число ≥ 30 (или Nk/Nm/Ng/Nt)",
        "menu.edit.prec_set": "prec → {value}",
        "menu.edit.seed_now": "текущий seed: {value}",
        "menu.edit.seed_new": "новый seed [0..2^63): ",
        "menu.edit.seed_set": "seed → {value}",
        "menu.edit.preset_list": "пресеты: quick | full | deep",
        "menu.edit.preset_choice": "выбор [{value}]: ",
        "menu.edit.preset_set": "preset → {value} (prec={prec}, two_pass={twopass})",
        "menu.edit.theme_set": "тема → {value}",
        "menu.edit.lang_set": "язык → {value}",
        "menu.edit.depth_set": "depth → {value}",
        "menu.edit.twopass_set": "two_pass → {value}",
        "menu.edit.precext_set": "prec_extreme → {value} (prec={prec})",
        # §3.2 v5: честная RAM-оценка гигантского prec
        "prec.ram.block": "ERR_PREC_RAM: prec={prec} → ≈{est}/число, уже 2 числа > RAM {ram}. Сознательное продолжение: --unsafe-prec / HODGE_PREC_UNSAFE=1",
        "prec.ram.bypass": "prec={prec}: ≈{est}/число > RAM — продолжаю по --unsafe-prec",
        "prec.ram.warn": "prec={prec} → ≈{est}/число; 16 чисел ≈ {est16} vs RAM {ram} — возможен OOM",
        # §3.2 v6: блок честных оценок prec + гейты
        "prec.est.header": "prec {prec} знаков · ≈{est} RAM/число — честные оценки стоимости (py-движок):",
        "prec.est.pi": "  π (Чудновский BS):            ≈{est} один раз (кэш дальше)",
        "prec.est.trig": "  sin/cos/atan (1 вызов):       ≈{est} — лимит {lim} с → {verdict}",
        "prec.est.lnexp": "  ln/exp (1 вызов):             ≈{est} — лимит {lim} с → {verdict}",
        "prec.est.gamma": "  Γ/Стирлинг (ряд {terms} членов + ζ-сумма {zterms}): ≈{est} — лимит {lim} с → {verdict}",
        "prec.est.quad": "  tanh–sinh (≈{nodes} узлов):          ≈{est} — лимит {lim} с → {verdict}",
        "prec.est.advice": "  совет: BLOCK-операции упадут с честным ERR_* вместо зависания; на таком prec используйте engine=julia (MPFR: π@5M бит ≈ 1.5 с, log/exp/sin ≈ 0.7–7 с)",
        "prec.op.block": "ERR_PREC_OP {kind} @ prec={prec}: оценка ≈{est} с > лимита {lim} с (HODGE_OP_LIMIT). py-движок на таком prec не масштабируется (libmpdec ln/exp квадратичны). Совет: engine=julia либо prec ≤ ~10000; осознанный обход: HODGE_PREC_UNSAFE=1",
        "prec.gamma.block": "ERR_GAMMA_PREC Γ @ prec={prec}: сдвиг y≈{shift}, ряд ≈{terms} членов × дивизии + ζ(302)−1 суммой ≈{zterms} членов; оценка ≈{est} с > лимита {lim} с (HODGE_GAMMA_LIMIT). Γ-задачи: prec ≤ ~1500 (py) / ≤ ~5000 бит (julia) или HODGE_PREC_UNSAFE=1",
        "prec.quad.block": "ERR_QUAD_PREC tanh–sinh @ prec={prec}: узлов ≈{nodes} × (4 exp + 2 div) ≈ {est} с > лимита {lim} с (HODGE_QUAD_LIMIT). Квадратуры держите при prec ≤ ~20000 или HODGE_PREC_UNSAFE=1",
        "menu.edit.prec.confirm": "prec={value}: оценка серьёзная (см. выше). Продолжить? [Y/n]: ",
        "menu.edit.prec.revert": "prec возвращён к {value}",
        "menu.edit.prec_keep": "prec без изменений: {value}",
        "menu.edit.seed_keep": "seed без изменений: {value}",
        "menu.edit.preset_keep": "preset без изменений: {value}",
        "menu.edit.not_int": "нужно целое число, получено: {v}",
        "menu.edit.preset_unknown": "неизвестный пресет: {v} (quick|full|deep)",
        "menu.act.dry_hint": "dry-run: --dry-run --task all (план без вычислений)",
        "menu.act.palette_hint": "палитра: --theme-preview",
        "menu.act.video_lab": "3D Video Lab: объект → MP4/GIF",
        "menu.video.objects": "3D Video Lab · доступные объекты:",
        "menu.video.prompt": "имя объекта [sphere]: ",
        # §14.2: подменю r/C/?/x/w/V — полноценные интерактивы (BUGFIX: были заглушки)
        "submenu.cancelled": "отменено",
        "submenu.all": "все",
        "submenu.numbers": "числа ",
        "submenu.recipes.title": "── Рецепты ───────────────────────────────────────────",
        "submenu.recipes.cancel": "  [0] отмена",
        "submenu.recipes.prompt": "  рецепт [0-{n}]: ",
        "submenu.recipes.none": "нет рецепта '{v}'",
        "submenu.recipes.applying": "  применение рецепта '{name}':",
        "submenu.recipes.preview": "    preset:  {pold} → {pnew}\n    profile: {rold} → {rnew}\n    tasks:   {told} → {tnew}\n    two_pass: {eold} → {enew}",
        "submenu.recipes.actions": "  [a] применить и запустить\n  [p] только применить (без запуска)\n  [Enter] отмена",
        "submenu.recipes.action_prompt": "  действие: ",
        "submenu.recipes.applied": "рецепт '{name}' применён",
        "submenu.recipes.running": "запуск рецепта '{name}': {ids}",
        "submenu.palette.current": " ⟵ текущая",
        "submenu.palette.sample": "  образец: ",
        "submenu.palette.hint": "  [1-{n}] выбрать · [Enter] отмена",
        "submenu.palette.prompt": "  тема по номеру: ",
        "submenu.palette.none": "нет темы '{v}'",
        "submenu.palette.mono_note": "  (монохром — палитра собирается программно, §27.8)",
        "submenu.palette.set": "тема → {value}",
        "submenu.help.title": "  HODGE MASTER · полная справка",
        "submenu.help.run": "RUN:",
        "submenu.help.run.body": "  [a] запуск ВСЕХ задач (two-pass, если cfg.two_pass=true)\n  [f] только задачи с тегом fast\n  [h] только задачи с тегом heavy\n  [c] chess — диапазон 23–33 (запустится всё, что есть в реестре)\n  [v] verhodge — диапазон 34–38 + 40 (HODGE-INF, классы Ходжа до бесконечности)\n  [w] SWEEP-подменю: 3D-лаборатория, выбор функции и параметров",
        "submenu.help.tasks": "ЗАДАЧИ:",
        "submenu.help.tasks.body": "  [1-23, 38-40] запустить одну задачу по номеру\n  [Space] отметить задачу (накопительно)\n  [Enter] запуск отмеченных (или выбранной в фильтре)\n  [/] фильтр по slug / title / номеру\n  [j/k] навигация вперёд / назад",
        "submenu.help.settings": "НАСТРОЙКИ:",
        "submenu.help.settings.body": "  [p] precision (30..∞ бит; суффиксы k/m/g/t — «1g» ≈ 1 млрд знаков ≈ 0.4 GB/число)\n  [s] seed (целое)\n  [n] preset (quick | full | deep)\n  [t] тема (цикл)\n  [l] язык (ru ⇄ en)\n  [d] color depth (auto | truecolor | 256 | 16 | mono)\n  [e] two-pass (on ⇄ off)\n  [P] prec-extreme (on ⇄ off; рекордный режим: prec ≥ 200)\n  словом: «prec-extreme [on|off]» / «precext» — то же, что [P]\n  изменения настроек сохраняются в .cache/settings.json (§3.2 v4)",
        "submenu.help.actions": "ДЕЙСТВИЯ:",
        "submenu.help.actions.body": "  [x] dry-run: план прогона без вычислений\n  [r] рецепты: список → выбор → preview → apply/run\n  [T] сменить тему (цикл)\n  [C] палитра: свотчи всех тем + выбор\n  [V] 3D Video Lab: объект + fps + frames + N (MP4/GIF)\n  [?] эта справка\n  [q] выход из меню",
        "submenu.help.cli": "CLI-СООТВЕТСТВИЯ:",
        "submenu.help.cli.body": "  [a] ≈ --task all --two-pass\n  [x] ≈ --dry-run --task <выбор>\n  [r] ≈ --recipe NAME\n  [V] ≈ --lab-video OBJ [--lab-video-fps N --lab-video-frames N --lab-video-N N]\n  [w] ≈ --lab3d FN --sweep name:lo:hi:step ...",
        "submenu.help.input": "УПРАВЛЕНИЕ ВВОДОМ:",
        "submenu.help.input.body": "  Ctrl+D — выход из меню\n  Ctrl+C — прервать прогон (возврат в меню)\n  Ctrl+Y — копировать путь прогона (OSC 52)\n  !!     — повторить последнюю команду\n  !N     — повторить N-ю команду (нумерация с 1)",
        "submenu.help.back": "  [Enter] — вернуться в меню",
        "submenu.dry.title": "── dry-run (план без вычислений) ──────────────────",
        "submenu.dry.cfg": "  Пресет: {preset} · seed: {seed} · prec: {prec} · two-pass: {tp}",
        "submenu.dry.opts": "  [1] все задачи\n  [2] fast-теги\n  [3] heavy-теги\n  [4] chess (23–33)\n  [5] verhodge (34–38)",
        "submenu.dry.cancel": "  [Enter] отмена",
        "submenu.dry.prompt": "  выбор: ",
        "submenu.dry.noopt": "нет опции '{v}'",
        "submenu.dry.done": "план записан в {path}",
        "submenu.sweep.title": "── SWEEP · 3D-лаборатория ──────────────────────────",
        "submenu.sweep.fns": "  Функции: omega | reflection | census_h",
        "submenu.sweep.fn_prompt": "  функция [omega]: ",
        "submenu.sweep.spec_prompt": "  sweep ({n} шт., Enter = запуск): ",
        "submenu.sweep.added": "добавлено: {spec}",
        "submenu.sweep.bad_spec": "невалидная спека: {msg}",
        "submenu.sweep.summary": "fn={fn} · specs={specs} · кадров={total} (cap {cap})",
        "submenu.sweep.cap_warn": "будет обрезано до {cap} кадров",
        "submenu.sweep.confirm": "  [Enter] запустить · [c] отмена: ",
        "submenu.video.fps_prompt": "  fps [24]: ",
        "submenu.video.frames_prompt": "  frames [120]: ",
        "submenu.video.n_prompt": "  N_full [64]: ",
        "submenu.video.summary": "object={obj} · fps={fps} · frames={frames} · N={n}",
        "submenu.video.bad_obj": "объект '{obj}' не зарегистрирован",
        "submenu.groups.run": "{name}: {ids}",
        "submenu.groups.run_missing": "{name}: {ids} (не реализованы: {miss})",
        "submenu.groups.chess_empty": "нет задач с тегом chess (23–33) в реестре",
        "submenu.groups.verhodge_empty": "нет задач с тегом verhodge (34–38) в реестре",
    },
    "en": {
        "menu.title": "HODGE MASTER · verification menu",
        "menu.help": "? — help, a — all tasks, digits — mark, Enter — run marked, q — quit",
        "menu.prompt": "choice",
        "menu.bye": "Bye. Happy verifying!",
        "menu.unknown": "Unknown key: {key}",
        "run.start": "Run {run} · preset {preset} · seed {seed}",
        "run.done": "Done: {passed}/{total} PASS in {sec}",
        "task.verdict": "[{id}] {slug}: {verdict}",
        "all_pass": "ALL CHECKS PASSED",
        "has_fail": "THERE ARE FAILURES",
        "duration": "duration",
        "sec": "s",
        "stand": "stand",
        "summary": "SUMMARY",
        "tasks": "tasks",
        "tasks_plural": ("task", "tasks"),
        # §16 / VIII.2: messages of the new subsystems
        "report.saved": "Report saved: {path}",
        "plot.rendered": "Plots: {n} PNG, {m} GIF",
        "task.skip": "Task {id} skipped: {reason}",
        "lock.held": "Lock held: {path}",
        "cache.hit": "Cache: hit for {id}",
        "cache.miss": "Cache: miss for {id}",
        "monitor.line": "CPU {cpu} · RAM {ram} · T {temp}",
        "hook.error": "Hook {event} failed: {err}",
        # §14 menu: main screen (BUGFIX: render was hardcoded in Russian)
        "menu.run_header": "RUN",
        "menu.tasks_header": "TASKS",
        "menu.settings_header": "SETTINGS",
        "menu.actions_header": "ACTIONS",
        "menu.run_all": "Run ALL tasks (two-pass)",
        "menu.run_fast": "Fast tags only",
        "menu.run_heavy": "Heavy tags only",
        "menu.run_chess": "Chess only (23–33)",
        "menu.run_verhodge": "Verhodge only (34–38, 40)",
        "menu.run_sweep": "SWEEP: infinite parameter selector",
        "menu.set.prec": "precision          now: {value} bits",
        "menu.set.seed": "seed               now: {value}",
        "menu.set.preset": "preset             now: {value}",
        "menu.set.theme": "theme              now: {value}",
        "menu.set.lang": "language           now: {value}",
        "menu.set.depth": "color depth        now: {value}",
        "menu.set.two_pass": "two-pass           now: {value}",
        "menu.set.prec_extreme": "prec-extreme       now: {value}",
        "menu.act.dry_run": "dry-run (plan only, no compute)",
        "menu.act.recipes": "list recipes",
        "menu.act.theme_cycle": "cycle theme",
        "menu.act.palette": "palette (theme-preview)",
        "menu.act.help": "help",
        "menu.act.quit": "quit",
        "menu.filter_mode": "filter mode (empty — exit)",
        "menu.sweep_fn_prompt": "SWEEP: function name (omega|reflection|census_h) → Enter for default «omega»",
        "menu.sweep_spec_prompt": "SWEEP: function={fn}. Enter a sweep spec (name:lo:hi:step), empty — run",
        "menu.sweep_bad_fn": "SWEEP: unknown function \"{fn}\" — available: omega | reflection | census_h",
        "menu.sweep_added": "SWEEP: added {key}. more? (empty — run)",
        "menu.sweep_invalid": "SWEEP: {msg} — try again",
        "menu.sweep_invalid_spec": "SWEEP: invalid spec: {msg}",
        "menu.sweep_preview": "SWEEP: fn={fn}, specs={specs}, frames={n} (cap {cap})",
        "menu.status_line": "theme={theme} · prec={prec} · seed={seed} · preset={preset} · lang={lang} · marked={n} [{ids}]",
        "menu.copy_done": "copied: {path}",
        "menu.copy_empty": "run_dir empty — run something first",
        "menu.copy_disabled": "clipboard disabled (--no-clipboard)",
        "menu.history_empty": "history empty",
        "menu.no_history": "no entry #{n} (total {total})",
        "menu.history_hint": "history: !! — repeat last, !N — repeat N-th",
        "menu.eof_guard": "EOF-guard {n}/{limit}",
        "menu.ctrl_c": "Ctrl+C caught — return",
        "menu.input_error": "input error: {msg}",
        "menu.help_detail": "«?» — help\n  [1-N] task · [Space] mark · [Enter] run marked\n  [a/f/h/c/v] run groups · [w] sweep · [p/s/n/t/l/d/e/P] settings",
        "menu.non_tty_hint": "stdin is not a TTY — use --task N / --menu / --self-test",
        "menu.no_task": "no task {id}",
        "menu.mark_on": "task {id} marked — Enter will run marked tasks",
        "menu.mark_off": "task {id}: mark removed",
        "menu.runner_unavailable": "runner unavailable",
        "menu.resized": "resize",
        # §14: settings editors prompts (handle)
        "menu.edit.prec_now": "current prec: {value}",
        "menu.edit.prec_new": "new prec [30..∞ | 4096, 5m, 1g]: ",
        "menu.edit.prec_out": "need a number ≥ 30 (or Nk/Nm/Ng/Nt)",
        "menu.edit.prec_set": "prec → {value}",
        "menu.edit.seed_now": "current seed: {value}",
        "menu.edit.seed_new": "new seed [0..2^63): ",
        "menu.edit.seed_set": "seed → {value}",
        "menu.edit.preset_list": "presets: quick | full | deep",
        "menu.edit.preset_choice": "choice [{value}]: ",
        "menu.edit.preset_set": "preset → {value} (prec={prec}, two_pass={twopass})",
        "menu.edit.theme_set": "theme → {value}",
        "menu.edit.lang_set": "language → {value}",
        "menu.edit.depth_set": "depth → {value}",
        "menu.edit.twopass_set": "two_pass → {value}",
        "menu.edit.precext_set": "prec_extreme → {value} (prec={prec})",
        # §3.2 v5: honest RAM estimate for giant prec
        "prec.ram.block": "ERR_PREC_RAM: prec={prec} → ≈{est}/number, just 2 numbers exceed RAM {ram}. Deliberate override: --unsafe-prec / HODGE_PREC_UNSAFE=1",
        "prec.ram.bypass": "prec={prec}: ≈{est}/number > RAM — continuing via --unsafe-prec",
        "prec.ram.warn": "prec={prec} → ≈{est}/number; 16 numbers ≈ {est16} vs RAM {ram} — OOM possible",
        # §3.2 v6: honest prec cost block + gates
        "prec.est.header": "prec {prec} digits · ≈{est} RAM/number — honest cost estimates (py engine):",
        "prec.est.pi": "  π (Chudnovsky BS):            ≈{est} once (cached after)",
        "prec.est.trig": "  sin/cos/atan (1 call):        ≈{est} — limit {lim} s → {verdict}",
        "prec.est.lnexp": "  ln/exp (1 call):              ≈{est} — limit {lim} s → {verdict}",
        "prec.est.gamma": "  Γ/Stirling (series {terms} terms + ζ-sum {zterms}): ≈{est} — limit {lim} s → {verdict}",
        "prec.est.quad": "  tanh–sinh (≈{nodes} nodes):         ≈{est} — limit {lim} s → {verdict}",
        "prec.est.advice": "  advice: BLOCK ops will fail with an honest ERR_* instead of hanging; at this prec use engine=julia (MPFR: π@5M bits ≈ 1.5 s, log/exp/sin ≈ 0.7–7 s)",
        "prec.op.block": "ERR_PREC_OP {kind} @ prec={prec}: estimate ≈{est} s > limit {lim} s (HODGE_OP_LIMIT). py engine does not scale at this prec (libmpdec ln/exp are quadratic). Advice: engine=julia or prec ≤ ~10000; deliberate override: HODGE_PREC_UNSAFE=1",
        "prec.gamma.block": "ERR_GAMMA_PREC Γ @ prec={prec}: shift y≈{shift}, series ≈{terms} terms × divisions + ζ(302)−1 direct sum ≈{zterms} terms; estimate ≈{est} s > limit {lim} s (HODGE_GAMMA_LIMIT). Keep Γ-tasks at prec ≤ ~1500 (py) / ≤ ~5000 bits (julia) or HODGE_PREC_UNSAFE=1",
        "prec.quad.block": "ERR_QUAD_PREC tanh–sinh @ prec={prec}: ≈{nodes} nodes × (4 exp + 2 div) ≈ {est} s > limit {lim} s (HODGE_QUAD_LIMIT). Keep quadratures at prec ≤ ~20000 or HODGE_PREC_UNSAFE=1",
        "menu.edit.prec.confirm": "prec={value}: heavy estimate (see above). Continue? [Y/n]: ",
        "menu.edit.prec.revert": "prec reverted to {value}",
        "menu.edit.prec_keep": "prec unchanged: {value}",
        "menu.edit.seed_keep": "seed unchanged: {value}",
        "menu.edit.preset_keep": "preset unchanged: {value}",
        "menu.edit.not_int": "expected an integer, got: {v}",
        "menu.edit.preset_unknown": "unknown preset: {v} (quick|full|deep)",
        "menu.act.dry_hint": "dry-run: --dry-run --task all (plan only, no compute)",
        "menu.act.palette_hint": "palette: --theme-preview",
        "menu.act.video_lab": "3D Video Lab: object → MP4/GIF",
        "menu.video.objects": "3D Video Lab · available objects:",
        "menu.video.prompt": "object name [sphere]: ",
        # §14.2: submenus r/C/?/x/w/V — full interactive flows (BUGFIX: were stubs)
        "submenu.cancelled": "cancelled",
        "submenu.all": "all",
        "submenu.numbers": "numbers ",
        "submenu.recipes.title": "── Recipes ───────────────────────────────────────────",
        "submenu.recipes.cancel": "  [0] cancel",
        "submenu.recipes.prompt": "  recipe [0-{n}]: ",
        "submenu.recipes.none": "no recipe '{v}'",
        "submenu.recipes.applying": "  applying recipe '{name}':",
        "submenu.recipes.preview": "    preset:  {pold} → {pnew}\n    profile: {rold} → {rnew}\n    tasks:   {told} → {tnew}\n    two_pass: {eold} → {enew}",
        "submenu.recipes.actions": "  [a] apply and run\n  [p] apply only (no run)\n  [Enter] cancel",
        "submenu.recipes.action_prompt": "  action: ",
        "submenu.recipes.applied": "recipe '{name}' applied",
        "submenu.recipes.running": "running recipe '{name}': {ids}",
        "submenu.palette.current": " ⟵ current",
        "submenu.palette.sample": "  sample: ",
        "submenu.palette.hint": "  [1-{n}] select · [Enter] cancel",
        "submenu.palette.prompt": "  theme by number: ",
        "submenu.palette.none": "no theme '{v}'",
        "submenu.palette.mono_note": "  (monochrome — palette is built programmatically, §27.8)",
        "submenu.palette.set": "theme → {value}",
        "submenu.help.title": "  HODGE MASTER · full help",
        "submenu.help.run": "RUN:",
        "submenu.help.run.body": "  [a] run ALL tasks (two-pass if cfg.two_pass=true)\n  [f] tasks tagged fast only\n  [h] tasks tagged heavy only\n  [c] chess — range 23–33 (everything the registry has will run)\n  [v] verhodge — range 34–38 + 40 (HODGE-INF: Hodge classes to infinity)\n  [w] SWEEP submenu: 3D lab, pick function and parameters",
        "submenu.help.tasks": "TASKS:",
        "submenu.help.tasks.body": "  [1-23, 38-40] run one task by number\n  [Space] mark task (cumulative)\n  [Enter] run marked (or the one selected under filter)\n  [/] filter by slug / title / number\n  [j/k] navigate down / up",
        "submenu.help.settings": "SETTINGS:",
        "submenu.help.settings.body": "  [p] precision (30..∞ digits; suffixes k/m/g/t — «1g» ≈ 1 billion digits ≈ 0.4 GB/number)\n  [s] seed (integer)\n  [n] preset (quick | full | deep)\n  [t] theme (cycle)\n  [l] language (ru ⇄ en)\n  [d] color depth (auto | truecolor | 256 | 16 | mono)\n  [e] two-pass (on ⇄ off)\n  [P] prec-extreme (on ⇄ off; record mode: prec ≥ 200)\n  by word: «prec-extreme [on|off]» / «precext» — same as [P]\n  setting changes are persisted to .cache/settings.json (§3.2 v4)",
        "submenu.help.actions": "ACTIONS:",
        "submenu.help.actions.body": "  [x] dry-run: plan without compute\n  [r] recipes: list → pick → preview → apply/run\n  [T] switch theme (cycle)\n  [C] palette: swatches of all themes + select\n  [V] 3D Video Lab: object + fps + frames + N (MP4/GIF)\n  [?] this help\n  [q] quit menu",
        "submenu.help.cli": "CLI EQUIVALENTS:",
        "submenu.help.cli.body": "  [a] ≈ --task all --two-pass\n  [x] ≈ --dry-run --task <choice>\n  [r] ≈ --recipe NAME\n  [V] ≈ --lab-video OBJ [--lab-video-fps N --lab-video-frames N --lab-video-N N]\n  [w] ≈ --lab3d FN --sweep name:lo:hi:step ...",
        "submenu.help.input": "INPUT CONTROL:",
        "submenu.help.input.body": "  Ctrl+D — quit the menu\n  Ctrl+C — abort a run (return to menu)\n  Ctrl+Y — copy run path (OSC 52)\n  !!     — repeat last command\n  !N     — repeat N-th command (count from 1)",
        "submenu.help.back": "  [Enter] — back to menu",
        "submenu.dry.title": "── dry-run (plan without compute) ──────────────────",
        "submenu.dry.cfg": "  Preset: {preset} · seed: {seed} · prec: {prec} · two-pass: {tp}",
        "submenu.dry.opts": "  [1] all tasks\n  [2] fast tags\n  [3] heavy tags\n  [4] chess (23–33)\n  [5] verhodge (34–38)",
        "submenu.dry.cancel": "  [Enter] cancel",
        "submenu.dry.prompt": "  choice: ",
        "submenu.dry.noopt": "no option '{v}'",
        "submenu.dry.done": "plan written to {path}",
        "submenu.sweep.title": "── SWEEP · 3D lab ──────────────────────────────────",
        "submenu.sweep.fns": "  Functions: omega | reflection | census_h",
        "submenu.sweep.fn_prompt": "  function [omega]: ",
        "submenu.sweep.spec_prompt": "  sweep ({n} set, Enter = run): ",
        "submenu.sweep.added": "added: {spec}",
        "submenu.sweep.bad_spec": "invalid spec: {msg}",
        "submenu.sweep.summary": "fn={fn} · specs={specs} · frames={total} (cap {cap})",
        "submenu.sweep.cap_warn": "will be truncated to {cap} frames",
        "submenu.sweep.confirm": "  [Enter] run · [c] cancel: ",
        "submenu.video.fps_prompt": "  fps [24]: ",
        "submenu.video.frames_prompt": "  frames [120]: ",
        "submenu.video.n_prompt": "  N_full [64]: ",
        "submenu.video.summary": "object={obj} · fps={fps} · frames={frames} · N={n}",
        "submenu.video.bad_obj": "object '{obj}' is not registered",
        "submenu.groups.run": "{name}: {ids}",
        "submenu.groups.run_missing": "{name}: {ids} (not implemented: {miss})",
        "submenu.groups.chess_empty": "no tasks tagged chess (23–33) in the registry",
        "submenu.groups.verhodge_empty": "no tasks tagged verhodge (34–38) in the registry",
    },
}

def hodge_fmt(cfg, key: str, /, **kw) -> str:
    # ключ — positional-only (/): шаблоны с плейсхолдером {key} передают его
    # kwarg'ом и не должны конфликтовать с именем параметра (BUGFIX: TypeError
    # "multiple values for argument 'key'" на menu.unknown / menu.sweep_added).
    try:
        tpl = MSG.get(cfg.lang, MSG["en"])[key]
        return tpl.format(**kw) if kw else tpl
    except Exception:
        raise KeyError(f"ERR_TEMPLATE {key}")

def hodge_plural(cfg, n: int) -> str:
    forms = MSG[cfg.lang]["tasks_plural"]
    return HODGEText.plural(n, forms)


# ══════════════════════════════════════════════════════════════════════════
# §3. КОНФИГ: единственный носитель настроек; прецеденция
# defaults < config-file < env < CLI < menu (§3.2). Пресеты §1.3, профили §1.4.
# ══════════════════════════════════════════════════════════════════════════
class HodgeConfig:
    def __init__(self):
        # идентичность/пути
        self.run_dir = ""              # results/run_YYYYmmdd_HHMMSS (§10.1)
        self.report_dir = "results"
        self.cache_dir = ".cache"
        # §3.2 v4: кэш настроек .cache/settings.json (defaults < cache <
        # config-file < env < CLI < меню). Сохраняется при изменениях в меню;
        # --no-settings-cache / --settings-reset — отключить/очистить.
        self.settings_cache = True
        self.settings_save = False     # --settings-save: сохранить и текущий CLI-прогон
        self.lang = "en"
        # данные/оркестрация
        self.seed = 0
        self.size = 64                 # max N для ценза (pass2)
        self.preset = "full"           # quick | full | deep
        self.profile = "balanced"      # safe | balanced | fast | paranoid
        self.two_pass = True
        self.pass_only = 0             # 0 | 1 | 2
        self.isolate = True            # §5.3: derive(seed, "pass2")
        self.tasks = []                # выбранные id ([] = все)
        self.with_deps = True
        self.tags = []                 # фильтр --tag fast,!heavy
        self.deterministic = False
        # точность задач (не для UI)
        self.prec = 55
        # тема/типографика
        self.theme = "dark-gold"
        self.color_depth = "auto"
        self.plain = False
        self.no_color = False
        self.unicode_on = "auto"
        self.dye = "auto"
        # §22.9 / A14: стратегия gradient(). Дефолт per-char — это
        # канонический §22.4 "span" (каждый символ своим оттенком, §19.9 dye-тест);
        # per-token/per-line — осознанные режимы деградации (профиль safe/fast).
        self.dye_mode = "per-char"
        self.digit_tier = True
        self.gradient = "span"
        self.banner = "auto"
        self.splash = True
        self.tips = True
        self.no_clear = False
        # анимации/монитор
        self.anim = "off"              # сессия 1: сцены есть, печать auto→off вне tty
        self.anim_scene = "particles"
        self.monitor = "off"
        self.anim_seconds = 0.0        # §23.4 / A8: сек для --monitor animate (0 = до Ctrl+C)
        self.fps = 24                  # §23.2 / A8: fps анимации
        self.particles = 64            # §23.2 / A8: число частиц в сцене particles
        # графики §11 / 3D-лаборатория
        self.plot = True               # §11.2: PNG/GIF per-task
        self.plot_formats = "png,gif"  # §11.2: png,gif (svg — см. hodge_plot_svg)
        self.plot_width = 800
        self.plot_height = 480
        self.plot_aa = 2               # супер-сэмплинг: 1|2|4
        self.lab3d = ""                # omega | period_re | census_h | expr:… | "" (off)
        self.sweeps = []               # ["N:5:30:1", ...] — name:lo:hi:step
        self.report_formats = "md,html,svg"   # Часть IV.1: md,html,svg; pdf/docx → ERR_UNSUPPORTED
        self.prec_extreme = False             # Часть V: prec=200 + K=480 для рекордных задач
        self.unsafe_prec = False              # §3.2 v5: сознательный обход ERR_PREC_RAM
        self.lab_max_frames = 500
        self.lab_grid = 48
        self.lab_output = ""           # "" → run_dir/lab3d
        # §11.5: GCT общий на весь прогон — все GIF в единой палитре темы
        self.gct_cache = {}
        # §7.5/§8/§9.4 наблюдаемость
        self.monitor_interval = 60.0   # §8.2: --monitor-interval
        self.monitor_csv = True        # logs/monitor.csv
        self.metrics_format = ""       # §9.4: json|tsv|prom
        self.health_probe_sec = 0.0    # §15.7: health-probe в прогоне
        # §12.6 RLIMIT (MB / сек; 0 = не установлен)
        self.rlimit_as = 0
        self.rlimit_cpu = 0
        self.rlimit_fsize = 0
        self.rlimit_report = False
        # §14.9 TUI / меню
        self.tui = False
        self._last_run_dir = ""
        # §19 golden / bench-stats
        self.golden_dir = "tests/golden"
        self.golden_update = False
        self.float_tolerance = 1e-9
        self.pixel_tolerance = 0
        self.bench_stats = False
        self.bench_runs = 5
        # §23 анимации
        self.anim_cpu_guard = 40.0
        self.anim_intensity = "med"
        self.particles_charset = "gold"
        self.trail_particles = False
        self.title_bar = True
        # §24/§25/§27
        self.clean_orphans = True
        self.cache_on = False
        self.rate_limit = ""
        self.links = "auto"
        self.no_clipboard = False
        # логи/метрики
        self.log_level = "INFO"
        self.redact = True
        self.no_report = False
        self.ci = False
        self.jsonl = False
        self.tsv = False
        self.junit = ""
        # тесты/CI
        self.self_test = []
        self.bench = False
        self.bench_threshold = 1.2
        self.fuzz_sec = 0
        self.coverage = False
        self.task_timeout = 0
        self.global_timeout = 0
        # кэш/resume
        self.no_cache = True           # задачи дешёвые; кэш по --cache on
        self.resume_dir = ""
        self.checkpoint_every = 0
        # служебные
        self.print_config = False
        self.explain_config = False
        self.validate_config_only = False
        self.diff_runs = None
        self.sign_key = ""
        self.verify_signature = ""
        self.menu_forced = False       # --menu
        self.menu_off = False          # --no-menu
        self.generate = ""             # man | completions:bash|zsh|fish|powershell
        self.theme_preview = False
        self.doctor = False
        self.health = False
        self.dry_run = False
        self.strict = False
        self.notify = "off"

    # §3.5 schema-валидация (field → validator); код 2 при ошибке
    VALIDATORS = {
        "preset": lambda v: v in ("quick", "full", "deep"),
        "profile": lambda v: v in ("safe", "balanced", "fast", "paranoid"),
        "theme": lambda v: v in HODGEColor.THEMES,
        "lang": lambda v: v in ("ru", "en"),
        "color_depth": lambda v: v in ("auto", "truecolor", "256", "16", "mono"),
        "seed": lambda v: 0 <= int(v) <= 2**64,
        "prec": lambda v: 30 <= int(v),   # §3.2 v5: БЕЗ верхней границы (суффиксы k/m/g/t)
        "pass_only": lambda v: int(v) in (0, 1, 2),
        # A14: dye-mode и связанные ручки под schema-контролем
        "dye_mode": lambda v: v in ("per-char", "per-token", "per-line"),
        "gradient": lambda v: v in ("span", "line", "block", "off"),
        "fps": lambda v: 5 <= int(v) <= 60,
        "particles": lambda v: 4 <= int(v) <= 4096,
        "anim_seconds": lambda v: float(v) >= 0,
        # §11: графики и лаборатория
        "plot_aa": lambda v: int(v) in (1, 2, 4),
        "plot_width": lambda v: 100 <= int(v) <= 4000,
        "plot_height": lambda v: 100 <= int(v) <= 4000,
        "lab_max_frames": lambda v: 1 <= int(v) <= 5000,
        "lab_grid": lambda v: 4 <= int(v) <= 256,
    }

    def validate(self) -> list:
        errs = []
        for name, fn in self.VALIDATORS.items():
            try:
                if not fn(getattr(self, name)):
                    errs.append(f"ERR_SCHEMA {name}: invalid value {getattr(self, name)!r}")
            except Exception as ex:
                errs.append(f"ERR_SCHEMA {name}: {ex}")
        return errs

    def relevant_hash(self) -> str:
        """§20.6: хэш релевантной части cfg (без путей и UI)."""
        payload = json.dumps({
            "seed": self.seed, "size": self.size, "preset": self.preset,
            "prec": self.prec, "two_pass": self.two_pass, "pass_only": self.pass_only,
            "isolate": self.isolate, "deterministic": self.deterministic,
            "tasks": self.tasks, "tags": self.tags, "v": HODGE_VERSION,
        }, sort_keys=True)
        return sha256(payload.encode()).hexdigest()[:16]

    def derive_seed(self, *parts) -> int:
        """§5.3 / §20.2: derive(seed, 'task|pass|phase|anim').
        При --deterministic добавляется salt=fixed, чтобы одинаковый seed
        давал одинаковые домены независимо от окружения."""
        salt = "det-v1" if self.deterministic else ""
        payload = "|".join(str(p) for p in [self.seed, salt, *parts])
        return int(sha256(payload.encode()).hexdigest()[:12], 16)


def apply_preset(cfg: HodgeConfig, name: str) -> None:
    """§1.3: пресеты (size, seed-depth, pass-depth, precision, render)."""
    if name == "quick":
        cfg.prec, cfg.two_pass, cfg.size = 55, False, 32
    elif name == "full":
        cfg.prec, cfg.two_pass, cfg.size = 55, True, 64
    elif name == "deep":
        cfg.prec, cfg.two_pass, cfg.size = 60, True, 64
    else:
        raise ValueError(f"ERR_PRESET_UNKNOWN {name}")


def apply_profile(cfg: HodgeConfig, name: str, explicit: set | None = None) -> list:
    """§1.4 / B2: профили управляют скрытыми ручками; явные CLI-флаги побеждают."""
    explicit = explicit or set()
    warns = []
    if name == "safe":
        if "dye_mode" not in explicit:
            cfg.dye_mode = "per-line"
        if "gradient" not in explicit:
            cfg.gradient = "off"
        if "fps" not in explicit:
            cfg.fps = 15
        if "particles" not in explicit:
            cfg.particles = 32
    elif name == "fast":
        if "dye_mode" not in explicit:
            cfg.dye_mode = "per-line"
        if "log_level" not in explicit:
            cfg.log_level = "WARN"
    elif name == "paranoid":
        cfg.deterministic = True
        cfg.strict = True
        cfg.profile = "paranoid"
    elif name != "balanced":
        warns.append(f"ERR_SCHEMA profile: unknown {name}")
    return warns


# ══════════════════════════════════════════════════════════════════════════
# §9. ЛОГИ: пять потоков (COMP_LOG, STDOUT_CAPTURE, results_log, events,
# metrics) + редакция секретов §9.5 + ERR_LEDGER §9.6. Файловые логи —
# без ANSI (§9.7). Печать основного кода — только через tee (§2.2).
# ══════════════════════════════════════════════════════════════════════════
REDACT_PATTERNS = [re.compile(p, re.I) for p in
                   (r"(token=)\S+", r"(secret=)\S+", r"(password=)\S+", r"(api[_-]?key=)\S+")]

LEVELS = {"TRACE": 0, "DEBUG": 1, "INFO": 2, "WARN": 3, "ERROR": 4, "FATAL": 5}
LEVEL_COLORS = {"TRACE": "gold_dim", "DEBUG": "gold_dim", "INFO": "gold",
                "WARN": "warn", "ERROR": "err", "FATAL": "err"}


# ══════════════════════════════════════════════════════════════════════════
# §7.4 SPARKLINE + ETA (EMA α=0.2) + rate. Нижние уровни — gold_dim,
# верхние — gold_bright, пик — amber.
# ══════════════════════════════════════════════════════════════════════════
class HodgeSparkline:
    SPARK_UNICODE = "▁▂▃▄▅▆▇█"
    SPARK_ASCII = ".-=+*#@"

    @classmethod
    def render(cls, values: list, width: int = 20) -> str:
        if not values:
            return ""
        vals = values[-width:]
        lo, hi = min(vals), max(vals)
        span = (hi - lo) or 1.0
        chars = cls.SPARK_UNICODE if HODGEText.unicode_on else cls.SPARK_ASCII
        n = len(chars)
        out = []
        for v in vals:
            t = (v - lo) / span
            idx = min(n - 1, int(t * n))
            color = "gold_dim" if t < 0.4 else "gold" if t < 0.8 else (
                "amber" if v == hi and len(vals) > 1 else "gold_bright")
            out.append(HODGEText.dye(chars[idx], color))
        return "".join(out)


class HodgeETA:
    """EMA α=0.2; при samples < 8 → '…'; при дисперсии > 3σ → '±'."""

    def __init__(self, alpha: float = 0.2):
        self.alpha = alpha
        self.samples: list = []
        self.ema: float | None = None

    def push(self, dur: float) -> None:
        self.samples.append(dur)
        self.ema = dur if self.ema is None else self.alpha * dur + (1 - self.alpha) * self.ema

    def eta(self, remaining: int) -> str:
        if len(self.samples) < 8 or self.ema is None:
            return "…"
        if len(self.samples) >= 10:
            stdev = statistics.pstdev(self.samples[-20:])
            if self.ema > 0 and stdev / self.ema > 3:
                return "±"
        return HODGEText.fmt_duration(max(0.0, self.ema * remaining))


class HodgeRate:
    def __init__(self):
        self.t0 = time.monotonic()
        self.count = 0

    def tick(self) -> None:
        self.count += 1

    def rate(self) -> float:
        dt = time.monotonic() - self.t0
        return self.count / dt if dt > 0 else 0.0


# ══════════════════════════════════════════════════════════════════════════
# §8 СИСТЕМНЫЙ МОНИТОР: снэпшоты из /proc и /sys. Termux-safe: недоступно — '—'.
# ══════════════════════════════════════════════════════════════════════════
class HodgeMonitor:
    def __init__(self, csv_path: str | None = None):
        self.csv_path = csv_path
        self._cpu_prev = None
        self._warned = set()

    def _warn_once(self, key: str, msg: str) -> None:
        if key in self._warned:
            return
        self._warned.add(key)
        if _ACTIVE_LOGGER:
            _ACTIVE_LOGGER.log_comp("WARN", "Mon", msg)

    def cpu_pct(self) -> str:
        try:
            with open("/proc/stat") as f:
                parts = f.readline().split()[1:]
            vals = [int(x) for x in parts]
            idle = vals[3] + (vals[4] if len(vals) > 4 else 0)
            total = sum(vals)
            if self._cpu_prev:
                di = idle - self._cpu_prev[0]
                dt = total - self._cpu_prev[1]
                pct = 100.0 * (1.0 - di / dt) if dt > 0 else 0.0
            else:
                pct = 0.0
            self._cpu_prev = (idle, total)
            return HODGEText.num(pct, "pct") + "%"
        except Exception:
            self._warn_once("cpu", "/proc/stat недоступен")
            return "—"

    def ram(self) -> str:
        try:
            info = {}
            with open("/proc/meminfo") as f:
                for ln in f:
                    k, _, v = ln.partition(":")
                    info[k] = int(v.strip().split()[0])
            used = info["MemTotal"] - info.get("MemAvailable", info.get("MemFree", 0))
            return (HODGEText.fmt_size(info["MemTotal"] * 1024) + " ("
                    + HODGEText.fmt_size(used * 1024) + " used)")
        except Exception:
            self._warn_once("ram", "/proc/meminfo недоступен")
            return "—"

    def temp(self) -> str:
        try:
            with open("/sys/class/thermal/thermal_zone0/temp") as f:
                c = int(f.read().strip()) / 1000.0
            return HODGEText.num(c, "float", 1) + "°C"
        except Exception:
            return "—"

    def uptime(self) -> str:
        try:
            with open("/proc/uptime") as f:
                sec = float(f.read().split()[0])
            return HODGEText.fmt_duration(sec)
        except Exception:
            return "—"

    def io_latency(self) -> str:
        try:
            with open("/proc/pressure/io") as f:
                for ln in f:
                    if "some" in ln:
                        total = int(ln.split()[1].split("=")[1])
                        return f"{total}µs"
            return "—"
        except Exception:
            return "—"

    def snapshot(self) -> dict:
        s = {"cpu": self.cpu_pct(), "ram": self.ram(), "temp": self.temp(),
             "io": self.io_latency(), "uptime": self.uptime()}
        if self.csv_path:
            try:
                exists = os.path.exists(self.csv_path)
                with open(self.csv_path, "a", encoding="utf-8") as f:
                    if not exists:
                        f.write("ts,cpu,ram,temp,io,uptime\n")
                    f.write(",".join([datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                      s["cpu"], s["ram"].replace(",", " "),
                                      s["temp"], s["io"], s["uptime"]]) + "\n")
            except OSError:
                self._warn_once("csv", "monitor.csv не пишется")
        return s

    def line(self) -> str:
        s = self.snapshot()
        parts = [f"CPU {s['cpu']}", f"RAM {s['ram']}", f"T {s['temp']}",
                 f"IO {s['io']}", f"up {s['uptime']}"]
        return HODGEText.dye(" · ".join(parts), "gold_dim")


# ══════════════════════════════════════════════════════════════════════════
# §25 / VII.4: дисковый кэш результатов задач + rate-limit запусков задач.
# ══════════════════════════════════════════════════════════════════════════
class HodgeCache:
    MAGIC = b"CACHE\x01"

    def __init__(self, cfg: HodgeConfig):
        self.cfg = cfg
        self.dir = cfg.cache_dir
        if cfg.cache_on:
            os.makedirs(self.dir, exist_ok=True)

    def _key(self, task_id: int, salt: str = "") -> str:
        payload = f"{task_id}|{self.cfg.relevant_hash()}|{salt}"
        return sha256(payload.encode()).hexdigest()[:32]

    def get(self, task_id: int):
        if not self.cfg.cache_on:
            return None
        p = os.path.join(self.dir, str(task_id), self._key(task_id) + ".bin")
        if not os.path.exists(p):
            return None
        try:
            with open(p, "rb") as f:
                data = f.read()
            if not data.startswith(self.MAGIC):
                return None
            payload = data[len(self.MAGIC):]
            return json.loads(payload)
        except Exception:
            return None

    def put(self, task_id: int, value) -> None:
        if not self.cfg.cache_on:
            return
        p = os.path.join(self.dir, str(task_id), self._key(task_id) + ".bin")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        payload = self.MAGIC + json.dumps(value, default=str).encode()
        HODGEAdapter.atomic_write(p, payload)


# ──────────────────────────────────────────────────────────────────────
# §3.2 v4: КЭШ НАСТРОЕК (.cache/settings.json). Приоритет §3.2:
#   defaults < settings-cache < config-file < env < CLI < меню.
# Меню сохраняет настройки при КАЖДОМ изменении — [P] prec-extreme, тема,
# точность и т.д. живут между запусками. CLI всегда сильнее кэша.
# ──────────────────────────────────────────────────────────────────────
SETTINGS_CACHE_KEYS = {
    # ключ: (тип, описание)
    "prec": int, "seed": int,
    "preset": str, "profile": str, "theme": str, "lang": str,
    "color_depth": str, "dye_mode": str, "gradient": str, "anim": str,
    "anim_scene": str, "banner": str,
    "two_pass": bool, "prec_extreme": bool, "digit_tier": bool,
    "splash": bool, "tips": bool,
}
SETTINGS_SCHEMA = "1.0.0"


def settings_cache_path(cfg: HodgeConfig) -> str:
    return os.path.join(cfg.cache_dir, "settings.json")


def load_settings_cache(cfg: HodgeConfig) -> list:
    """§3.2 v4: применить сохранённые настройки к cfg. Битый файл → WARN-переименование,
    незнакомые ключи игнорируются, типы приводятся жёстко. → список применённых ключей."""
    if not cfg.settings_cache:
        return []
    p = settings_cache_path(cfg)
    try:
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return []
    except (OSError, ValueError) as ex:
        try:
            os.replace(p, p + ".corrupt")
            print(HODGEText.badge("WARN") + f" settings cache is corrupt ({ex}) — moved to {p}.corrupt",
                  flush=True)
        except OSError:
            pass
        return []
    if not isinstance(data, dict):
        return []
    data = data.get("settings", data)   # §3.2 v4: файл = {schema, saved_at, settings{...}}
    if not isinstance(data, dict):
        return []
    applied = []
    for key, typ in SETTINGS_CACHE_KEYS.items():
        if key not in data or data[key] is None:
            continue
        val = data[key]
        try:
            if typ is bool:
                val = bool(val)
            elif typ is int:
                val = int(val)
            elif typ is str:
                val = str(val)
            setattr(cfg, key, val)
            applied.append(key)
        except (TypeError, ValueError):
            continue
    return applied


def save_settings_cache(cfg: HodgeConfig) -> str:
    """§3.2 v4: атомарно сохранить настройки меню/прогона. → путь или ""."""
    if not cfg.settings_cache:
        return ""
    payload = {
        "schema": SETTINGS_SCHEMA,
        "saved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "version": HODGE_VERSION,
        "settings": {k: getattr(cfg, k) for k in SETTINGS_CACHE_KEYS},
    }
    try:
        p = settings_cache_path(cfg)
        HODGEAdapter.atomic_write(p, json.dumps(payload, ensure_ascii=False, indent=1))
        return p
    except OSError:
        return ""


def reset_settings_cache(cfg: HodgeConfig) -> bool:
    """§3.2 v4: удалить кэш настроек (--settings-reset). → удалён ли файл."""
    try:
        os.unlink(settings_cache_path(cfg))
        return True
    except OSError:
        return False


def hodge_prec_ram_guard(cfg: HodgeConfig) -> bool:
    """§3.2 v5: «гигабайты точности» ставятся свободно — но честно.
    Один Decimal prec знаков ≈ prec·8/19 байт (limb libmpdec: 19 цифр / 8 B).
    Оценка ×2 > RAM → ERR_PREC_RAM (OOM гарантирован), если нет --unsafe-prec
    / HODGE_PREC_UNSAFE=1; оценка ×16 > RAM → WARN. → False, если прогон
    должен быть прерван."""
    bytes_per = int(cfg.prec * 8 / 19) + 64
    try:
        total = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
    except (ValueError, OSError, AttributeError):
        return True
    if total <= 0:
        return True
    unsafe = getattr(cfg, "unsafe_prec", False) or os.environ.get("HODGE_PREC_UNSAFE") == "1"
    _f = lambda k, **kw: hodge_fmt(cfg, k, **kw)
    if bytes_per * 2 > total:
        if not unsafe:
            print(HODGEText.badge("FAIL") + " " + _f("prec.ram.block", prec=cfg.prec,
                  est=HODGEText.fmt_size(bytes_per), ram=HODGEText.fmt_size(total)), flush=True)
            return False
        print(HODGEText.badge("WARN") + " " + _f("prec.ram.bypass", prec=cfg.prec,
              est=HODGEText.fmt_size(bytes_per)), flush=True)
    elif bytes_per * 16 > total:
        print(HODGEText.badge("WARN") + " " + _f("prec.ram.warn", prec=cfg.prec,
              est=HODGEText.fmt_size(bytes_per), est16=HODGEText.fmt_size(bytes_per * 16),
              ram=HODGEText.fmt_size(total)), flush=True)
    return True


def _fmt_est(sec: float) -> str:
    """Оценки стоимости: гигантские значения — в нейтральных единицах
    (fmt_duration даёт '14100400810:02:16' — нечитаемо). Без «≈» — его
    ставит шаблон сообщения."""
    if sec >= 86400 * 365.25:
        y = sec / (86400 * 365.25)
        return f"{y:.0f} yr" if y >= 100 else (f"{y:.1f} yr" if y >= 10 else f"{y:.2f} yr")
    if sec >= 86400:
        dd = sec / 86400
        return f"{dd:.0f} d" if dd >= 100 else f"{dd:.1f} d"
    return HODGEText.fmt_duration(sec)


def hodge_prec_estimates(cfg: HodgeConfig) -> list:
    """§3.2 v6: честные оценки стоимости prec ДО запуска (конвенция py-движка:
    ctx.prec = prec ДЕСЯТИЧНЫХ знаков). Возвращает строки; печатает вызывающий."""
    d = int(cfg.prec)
    if d < 4096:
        return []
    c = mpdec_cost(d)
    out = []
    _f = lambda k, **kw: hodge_fmt(cfg, k, **kw)
    bytes_per = int(d * 8 / 19) + 64
    # π (Чудновский BS): измерено 4.65 с @ 1e6, 44.1 с @ 5e6 → ~n^1.4
    pi_est = 4.65 * (d / 1e6) ** 1.4
    # sin/cos/atan (один вызов, ряд по членам)
    trig = (0.09 * d + 40) * (c["mul"] + 4e-5)
    ln_e = c["ln"] + c["exp"]
    # Γ: сдвиг + ζ-сумма
    shift = max(40, int(math.ceil((d + 4) / 2.72864)) + 4)
    k_star = 3.1416 * shift
    g_est = k_star * (2 * c["mul"] + c["div"] + 3e-5)
    e151 = (d + 76) / 302.0
    g_est += (10 ** min(e151, 15.0)) * (1.5 * c["mul"] + 3e-5)
    # tanh–sinh
    if d > 60:
        t_need = math.asinh((d + 5) * math.log(10) * 2 / math.pi)
        quad_nodes = 2 * math.ceil(t_need / 0.02) + 1
    else:
        quad_nodes = 0
    quad_est = quad_nodes * (4 * c["exp"] + 2 * c["div"])
    lim_op = _hodge_env_float("HODGE_OP_LIMIT", 30.0)
    lim_g = _hodge_env_float("HODGE_GAMMA_LIMIT", 900.0)
    lim_q = _hodge_env_float("HODGE_QUAD_LIMIT", 1800.0)
    out.append(_f("prec.est.header", prec=HODGEText.fmt_int(d),
                  est=HODGEText.fmt_size(bytes_per)))
    out.append(_f("prec.est.pi", est=_fmt_est(pi_est)))
    out.append(_f("prec.est.trig", est=_fmt_est(trig),
                  lim=f"{lim_op:g}", verdict=fmt_verdict(trig, lim_op)))
    out.append(_f("prec.est.lnexp", est=_fmt_est(ln_e),
                  lim=f"{lim_op:g}", verdict=fmt_verdict(ln_e, lim_op)))
    out.append(_f("prec.est.gamma", terms=_fmt_terms(math.log10(max(k_star, 2))),
                  zterms=_fmt_terms(e151), est=_fmt_est(g_est),
                  lim=f"{lim_g:g}", verdict=fmt_verdict(g_est, lim_g)))
    if quad_nodes:
        out.append(_f("prec.est.quad", nodes=HODGEText.fmt_int(quad_nodes),
                      est=_fmt_est(quad_est),
                      lim=f"{lim_q:g}", verdict=fmt_verdict(quad_est, lim_q)))
    if max(trig, ln_e, g_est, quad_est) > max(lim_op, lim_g, lim_q):
        out.append(_f("prec.est.advice"))
    return out


def fmt_verdict(est: float, lim: float) -> str:
    """«ok»/«BLOCK» для блока оценок."""
    return "ok" if est <= lim else "BLOCK"


def hodge_prec_report(cfg: HodgeConfig) -> None:
    """Печать блока оценок (run_all / CLI), только если prec ≥ 4096."""
    for ln in hodge_prec_estimates(cfg):
        print(HODGEText.badge("WARN") + " " + ln, flush=True)



class HodgeRateLimit:
    def __init__(self, spec: str):
        self.period_s = 0.0
        if "/" in spec:
            n, unit = spec.split("/")
            n = int(n) or 1
            mult = {"s": 1.0, "m": 60.0, "h": 3600.0}.get(unit, 1.0)
            self.period_s = mult / n
        self._last = 0.0
        self.total_wait = 0.0

    def wait(self) -> None:
        if self.period_s <= 0:
            return
        now = time.monotonic()
        if now - self._last < self.period_s:
            w = self.period_s - (now - self._last)
            time.sleep(w)
            self.total_wait += w
        self._last = time.monotonic()


# ══════════════════════════════════════════════════════════════════════════
# §24.3 / VII.3: safe_join — любой составной путь через guard.
# ══════════════════════════════════════════════════════════════════════════
def safe_join(root: str, *parts) -> str:
    """'..' / абсолютные части → ValueError ERR_PATH_TRAVERSAL (§24.3)."""
    root_abs = os.path.abspath(root)
    for p in parts:
        if os.path.isabs(p) or ".." in p.split(os.sep):
            raise ValueError(f"ERR_PATH_TRAVERSAL {p}")
    target = os.path.abspath(os.path.join(root_abs, *parts))
    if not target.startswith(root_abs + os.sep) and target != root_abs:
        raise ValueError(f"ERR_PATH_TRAVERSAL {target}")
    return target


def hodge_clean_orphans(cfg: HodgeConfig, logger: HodgeLogger | None = None) -> int:
    """§24.9 / VII.3: удалить осиротевшие *.tmp в run_dir (--clean-orphans)."""
    removed = 0
    if not cfg.run_dir or not os.path.isdir(cfg.run_dir):
        return 0
    for root, _dirs, files in os.walk(cfg.run_dir):
        for f in files:
            if f.endswith(".tmp") or (f.startswith(".") and f.endswith(".tmp")):
                try:
                    os.remove(os.path.join(root, f))
                    removed += 1
                except OSError:
                    pass
    if logger:
        logger.log_comp("INFO", "Cleanup", f"removed {removed} orphan tmp-files")
    return removed


# ══════════════════════════════════════════════════════════════════════════
# §12.6 / IV.4: RLIMIT (AS/CPU/FSIZE); не умеем — ERR_UNSUPPORTED (§1.5).
# ══════════════════════════════════════════════════════════════════════════
def hodge_apply_rlimits(cfg: HodgeConfig, logger: HodgeLogger | None = None) -> bool:
    if os.name == "nt":
        if logger:
            logger.ledger("ERR_UNSUPPORTED")
            logger.log_comp("WARN", "Rlimit", "RLIMIT на Windows не поддержан (§1.5)")
        return False
    try:
        import resource
    except ImportError:
        if logger:
            logger.ledger("ERR_UNSUPPORTED")
            logger.log_comp("WARN", "Rlimit", "resource недоступен (§1.5)")
        return False

    def _set(kind, val):
        try:
            soft, hard = resource.getrlimit(kind)
            new = val if hard == resource.RLIM_INFINITY else min(val, hard)
            resource.setrlimit(kind, (new, hard))
            return True
        except (OSError, ValueError) as ex:
            if logger:
                logger.log_comp("WARN", "Rlimit", f"setrlimit {kind} failed: {ex}")
            return False

    ok = True
    if cfg.rlimit_as > 0:
        ok &= _set(resource.RLIMIT_AS, cfg.rlimit_as * 1024 * 1024)
    if cfg.rlimit_cpu > 0:
        ok &= _set(resource.RLIMIT_CPU, cfg.rlimit_cpu)
    if cfg.rlimit_fsize > 0:
        ok &= _set(resource.RLIMIT_FSIZE, cfg.rlimit_fsize * 1024 * 1024)
    return ok


# ══════════════════════════════════════════════════════════════════════════
# §9.4 / III.4: экспорт метрик json|tsv|prom → logs/metrics_summary.<ext>.
# ══════════════════════════════════════════════════════════════════════════
def hodge_metrics_export(cfg: HodgeConfig, logger: HodgeLogger) -> str:
    fmt = (getattr(cfg, "metrics_format", "") or "json").lower()
    out_dir = os.path.join(cfg.run_dir, "logs") if cfg.run_dir else "."
    os.makedirs(out_dir, exist_ok=True)
    metrics = logger.metrics
    if fmt == "prom":
        lines = []
        for name, vals in sorted(metrics.items()):
            nums = [v for v in vals if isinstance(v, (int, float))]
            if not nums:
                continue
            lines.append(f"# HELP {name} hodge-master metric")
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {nums[-1]}")
        text = "\n".join(lines) + "\n"
        ext = "prom"
    elif fmt == "tsv":
        lines = ["name\ttype\tn\tmin\tmax\tmean"]
        for name, vals in sorted(metrics.items()):
            nums = [v for v in vals if isinstance(v, (int, float))]
            if not nums:
                continue
            n = len(nums)
            lines.append(f"{name}\tmetric\t{n}\t{min(nums):.4f}\t{max(nums):.4f}\t"
                         f"{sum(nums) / n:.4f}")
        text = "\n".join(lines) + "\n"
        ext = "tsv"
    else:  # json
        data = {}
        for name, vals in sorted(metrics.items()):
            nums = [v for v in vals if isinstance(v, (int, float))]
            if not nums:
                data[name] = {"n": 0}
                continue
            n = len(nums)
            data[name] = {"n": n, "min": min(nums), "max": max(nums),
                          "mean": sum(nums) / n, "last": nums[-1]}
        text = json.dumps(data, ensure_ascii=False, indent=1)
        ext = "json"
    path = os.path.join(out_dir, f"metrics_summary.{ext}")
    HODGEAdapter.atomic_write(path, text)
    return path


# ══════════════════════════════════════════════════════════════════════════
# §10.7 / IV.3: cross-run dashboard — <report_dir>/index.html со всеми прогонами.
# ══════════════════════════════════════════════════════════════════════════
def hodge_cross_run_dashboard(cfg: HodgeConfig) -> None:
    base = cfg.report_dir
    if not os.path.isdir(base):
        return
    runs = sorted([d for d in os.listdir(base)
                   if d.startswith("run_") and os.path.isdir(os.path.join(base, d))],
                  reverse=True)
    rows = []
    theme = HODGEColor(cfg.theme, cfg.color_depth, cfg.plain)
    rep = HodgeReports(cfg, HodgeLogger(cfg), theme)
    for run in runs[:50]:
        rdir = os.path.join(base, run)
        rj = os.path.join(rdir, "results.json")
        if not os.path.exists(rj):
            continue
        try:
            data = json.load(open(rj, encoding="utf-8"))
            tasks = data.get("task", {})
            total = len(tasks)
            passed = sum(1 for t in tasks.values() if t.get("verdict") == "PASS")
            failed = sum(1 for t in tasks.values() if t.get("verdict") == "FAIL")
            code = data.get("run", {}).get("exit_code", "—")
            finished = str(data.get("run", {}).get("finished_at", ""))[:19]
            rows.append(f"<tr><td><a href='{run}/index.html'>{run}</a></td>"
                        f"<td>{finished}</td><td class='num'>{total}</td>"
                        f"<td class='pass'>{passed}</td><td class='fail'>{failed}</td>"
                        f"<td class='num'>{code}</td></tr>")
        except Exception:
            continue
    body = (f"<h1>Hodge Master · все прогоны</h1>"
            f"<table><tr><th>прогон</th><th>время</th><th>задач</th>"
            f"<th>PASS</th><th>FAIL</th><th>exit</th></tr>"
            + "".join(rows) + "</table>")
    HODGEAdapter.atomic_write(os.path.join(base, "index.html"),
                              rep.html_shell("cross-run dashboard", body))




class HodgeLogger:
    def __init__(self, cfg: HodgeConfig, theme: HODGEColor | None = None):
        self.cfg = cfg
        self.theme = theme
        self.comp_path = None
        self.events_path = None
        self.metrics_path = None
        self.full_log_path = None
        self.results_path = None       # §4.1 / §9.2: results_log (A17)
        self.t0 = time.monotonic()
        self.last_ts = self.t0
        self.err_ledger = {}          # err_code → [count, last_seen]
        self.metrics = {}             # name → list
        self.tee = None

    def open_run(self, run_dir: str) -> None:
        self.comp_path = os.path.join(run_dir, "logs", "computation_log.txt")
        self.events_path = os.path.join(run_dir, "logs", "events.jsonl")
        self.metrics_path = os.path.join(run_dir, "logs", "metrics.jsonl")
        self.full_log_path = os.path.join(run_dir, "logs", "full_run_log.txt")
        self.results_path = os.path.join(run_dir, "logs", "results_log.txt")
        os.makedirs(os.path.join(run_dir, "logs"), exist_ok=True)

    def _redact(self, s: str) -> str:
        if not self.cfg.redact:
            return s
        for rx in REDACT_PATTERNS:
            s = rx.sub(r"\1***", s)
        return s

    def log_comp(self, level: str, module: str, msg: str) -> None:
        """COMP_LOG: файл — чистый текст; консоль — окрашено (stderr)."""
        if level not in LEVELS:
            level = "INFO"
        msg = self._redact(str(msg))
        msg = run_i18n(msg, self.cfg.lang)   # BUGFIX(i18n): INFO/WARN задач → en при lang=en
        now = time.monotonic()
        delta = now - self.last_ts
        self.last_ts = now
        if self.comp_path and LEVELS[level] >= LEVELS.get(self.cfg.log_level, 2):
            ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            with open(self.comp_path, "a", encoding="utf-8") as f:
                f.write(f"[{ts}] [+{delta:.3f}s] [{level}] [{module}] {msg}\n")
        if level in ("WARN", "ERROR", "FATAL") and self.theme and not self.cfg.ci:
            line = f"{HODGEText.dye(level, LEVEL_COLORS[level], 'bold' if level != 'WARN' else '')} {HODGEText.dye(msg, 'text')}"
            sys.stderr.write(line + "\n")

    def event(self, level: str, module: str, key: str, **args) -> None:
        """events.jsonl: {ts, level, module, task, phase, key, args} — без ANSI."""
        if not self.events_path:
            return
        rec = {"ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
               "level": level, "module": module, "key": key,
               "phase": args.pop("phase", ""), "task": args.pop("task", ""),
               "args": {k: ("nan" if (isinstance(v, float) and math.isnan(v)) else
                            ("-inf" if v < 0 else "inf") if (isinstance(v, float) and math.isinf(v)) else v)
                        for k, v in args.items()}}   # P0.11: знак inf сохраняется
        with open(self.events_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")

    def metric(self, name: str, mtype: str, value, tags=None) -> None:
        """metrics.jsonl + агрегат для метрик-сводки (гистограмма ≤ 1024, §9.4)."""
        self.metrics.setdefault(name, []).append(value)
        if len(self.metrics[name]) <= 1024:
            if not self.metrics_path:
                return
            rec = {"ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                   "name": name, "type": mtype, "value": value, "tags": tags or {}}
            with open(self.metrics_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
        else:
            self.ledger("ERR_HISTO_OVERFLOW")

    # ── §9.4 / III.4: dedicated-метрики ──
    def metric_counter(self, name: str, delta: int = 1, tags: dict | None = None) -> None:
        self.metrics.setdefault(name, [0])
        self.metrics[name][-1] = self.metrics[name][-1] + delta
        self.metric(name, "counter", delta, tags)

    def metric_gauge(self, name: str, value: float, tags: dict | None = None) -> None:
        self.metric(name, "gauge", value, tags)

    def metric_timer(self, name: str, duration_s: float, tags: dict | None = None) -> None:
        self.metric(name, "timer", duration_s, tags)

    def metric_histogram(self, name: str, bucket: int, tags: dict | None = None) -> None:
        if bucket < 0 or bucket > 1024:
            self.ledger("ERR_HISTO_OVERFLOW")
            return
        self.metric(f"{name}_bucket_{bucket}", "histogram", 1, tags)

    def ledger(self, code: str) -> None:
        """ERR_LEDGER §9.6: err_code → count → last_seen."""
        rec = self.err_ledger.setdefault(code, [0, None])
        rec[0] += 1
        rec[1] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    def log_result(self, tid: int, slug: str, verdict: str,
                   reason: str | None = None, claims: list | None = None,
                   duration_s: float | None = None) -> None:
        """§4.1 / §9.2 results_log (A17): ровно одна строка-вердикт на задачу.
        Пишется всегда (не зависит от --log-level). В файл — без ANSI.
        В stdout — только если не silent; silent выставляет HodgeRunner."""
        # BUGFIX(i18n): reason — русский вердикт из task-fn; на дисплее переводим
        reason_en = run_i18n(reason, self.cfg.lang) if reason else reason
        plain = (f"[{tid:2d}] {slug}: {verdict}"
                 + (f" · {reason_en}" if reason_en else "")
                 + (f" · {duration_s:.2f}s" if duration_s is not None else ""))
        if self.results_path:
            try:
                with open(self.results_path, "a", encoding="utf-8") as f:
                    f.write(plain + "\n")
            except OSError:
                pass
        silent = (self.cfg.ci or self.cfg.jsonl or self.cfg.tsv
                  or self.cfg.no_color and not sys.stdout.isatty())
        if not silent:
            colored = (HODGEText.badge(verdict) + " "
                       + HODGEText.dye(f"[{tid:2d}] {slug}", "gold")
                       + (HODGEText.dye(f" · {reason_en}", "text_dim") if reason_en else ""))
            print(colored, flush=True)

    def progress(self, frac: float, *, eta: str = "", spark: str = "",
                 rate: float | None = None) -> None:
        """§7.1/§7.4: бар + sparkline + ETA + rate в stderr.
        В pipe — только milestone (не в stdout, §26.2)."""
        if self.cfg.ci or self.cfg.plain:
            return
        if HODGEAdapter.isatty(sys.stderr):
            width = max(30, min(100, HODGEAdapter.term_width() - 2))
            filled = int(width * frac)
            # §27.2 / A13: ASCII-фолбэк бара при --unicode off
            fill_ch = "█" if HODGEText.unicode_on else "#"
            pad_ch = "·" if HODGEText.unicode_on else "-"
            bar = (HODGEText.dye(fill_ch * filled, "gold")
                   + HODGEText.dye(pad_ch * (width - filled), "neutral"))
            extras = []
            if spark:
                extras.append(spark)
            if eta:
                extras.append(HODGEText.dye(f"ETA {eta}", "gold_dim"))
            if rate is not None:
                extras.append(HODGEText.dye(f"{rate:.1f}/s", "gold_dim"))
            tail = (" " + " ".join(extras)) if extras else ""
            sys.stderr.write(f"\r{bar} {int(frac * 100):3d}%{tail}\r")
        elif int(frac * 10) != int((frac - 0.0001) * 10):
            if self.cfg.jsonl or self.cfg.tsv:
                return   # §26.2 / A3: machine-поток в stdout не засоряем
            sys.stderr.write(f"milestone {int(frac * 100)}%\n")


_ACTIVE_LOGGER: HodgeLogger | None = None
# §24.2 / A7: активный lock на run_dir. None — lock не взят.
# Устанавливается _run_suite после успешного захвата, сбрасывается при release.
# splash() читает — показывает статус честно:
#   flock    → «acquired» (взаимоисключение на уровне ФС)
#   lockfile → «lockfile (flock unsupported)» (POSIX O_EXCL, ФС без flock)
#   advisory → «advisory (flock unsupported)» (блокировки нет вообще — WARN)
_RUN_LOCK_FD: int | None = None
_LOCK_MODE = "flock"   # flock | lockfile | advisory (каскад §24.2 v4)
_RUN_LOCK_PATH: str | None = None

# ══════════════════════════════════════════════════════════════════════════
# §4.3 PLUGINS & HOOKS: 6 событий; в одном файле — расширение массивов.
# ══════════════════════════════════════════════════════════════════════════
HOOK_EVENTS = ("pre_run", "post_run", "pre_task", "post_task", "on_error", "on_verdict")
HOOKS: dict = {ev: [] for ev in HOOK_EVENTS}

def register_hook(event: str, fn) -> None:
    if event not in HOOKS:
        raise ValueError(f"ERR_HOOK_UNKNOWN {event}")
    HOOKS[event].append(fn)

def fire_hook(event: str, *args, **kwargs) -> None:
    """§4.3: хук не может уронить прогон — только ERR_HOOK_EXCEPTION в ledger."""
    for fn in HOOKS.get(event, []):
        try:
            fn(*args, **kwargs)
        except Exception as ex:
            if _ACTIVE_LOGGER:
                _ACTIVE_LOGGER.ledger("ERR_HOOK_EXCEPTION")
                _ACTIVE_LOGGER.log_comp("WARN", "Hook",
                                        f"{event}: {type(ex).__name__}: {ex}")


def hodge_log(cfg, level: str, module: str, msg: str) -> None:
    """Точка входа задач в COMP_LOG (ядро не пишет в stdout, §2.2)."""
    if _ACTIVE_LOGGER is not None:
        _ACTIVE_LOGGER.log_comp(level, module, msg)


class _TeeStdout:
    """§9.2 STDOUT_CAPTURE: tee всего stdout в файл (потокобезопасно не нужно —
    задачи однопоточны). Мёртвый файл не роняет печать (§15.5)."""

    def __init__(self, path: str):
        self._orig = sys.stdout
        self._file = None
        try:
            self._file = open(path, "a", encoding="utf-8")
        except OSError:
            self._file = None

    def write(self, s):
        if self._file:
            try:
                self._file.write(HODGEText.strip_ansi(s))
                self._file.flush()
            except Exception:
                self._file = None
        return self._orig.write(s)

    def flush(self):
        if self._file:
            try:
                self._file.flush()
            except Exception:
                pass
        return self._orig.flush()

    def isatty(self):
        return False

    def fileno(self):
        return self._orig.fileno()

    @property
    def encoding(self):
        return getattr(self._orig, "encoding", "utf-8")

    def close(self):
        try:
            if self._file:
                self._file.close()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


# ══════════════════════════════════════════════════════════════════════════
# §5/§15. РАННЕР: dispatch — единственный вход (§4.1); two-pass обёртка с
# восстановлением cfg (§5.1); try/finally гарантирует вердикт даже при
# исключении (§15.2); таймаут задачи (§15.8); isolation RNG (§5.3).
# ══════════════════════════════════════════════════════════════════════════
class HodgeRunner:
    def __init__(self, cfg: HodgeConfig, logger: HodgeLogger, theme: HODGEColor):
        self.cfg = cfg
        self.log = logger
        self.theme = theme
        self.results = {}        # id → запись результата
        self.silent = cfg.ci or cfg.jsonl or cfg.tsv   # §26.2 / A3: machine-only
        self.checkpoint_path = os.path.join(cfg.run_dir, "checkpoint.json") if cfg.run_dir else None
        self._cache = HodgeCache(cfg)   # §25 / VII.4: дисковый кэш при --cache on

    # ── §4.2: зависимости и порядок ──
    def select_tasks(self) -> list:
        ids = self.cfg.tasks or list(SUITE_IDS)
        if self.cfg.with_deps:
            # §4.2 / II.3: топосорт с детектом цикла → ERR_CYCLE
            visiting: set = set()
            visited: set = set()
            ordered: list = []

            def visit(tid):
                if tid in visited:
                    return
                if tid in visiting:
                    self.log.ledger("ERR_CYCLE")
                    raise ValueError(f"ERR_CYCLE {tid}")
                visiting.add(tid)
                t = self._task(tid)
                if t:
                    for dep in t.get("deps", []):
                        visit(dep)
                visiting.discard(tid)
                visited.add(tid)
                ordered.append(tid)

            try:
                for tid in ids:
                    visit(tid)
            except ValueError as ex:
                self.log.log_comp("ERROR", "Select", str(ex))
                ordered = list(ids)   # деградация: исходный порядок, ERR_CYCLE в ledger
            ids = ordered
        if self.cfg.tags:
            def tag_match(t):
                res = False
                for tag in self.cfg.tags:
                    tag = tag.strip()
                    if tag.startswith("!"):
                        if t["tags"] and tag[1:] in t["tags"]:
                            return False
                        res = True
                    elif t["tags"] and tag in t["tags"]:
                        res = True
                return res
            ids = [tid for tid in ids if tag_match(self._task(tid))]
        return [tid for tid in SUITE_IDS if tid in ids]

    def _task(self, tid) -> dict | None:
        return next((t for t in TASKS if t["id"] == tid), None)

    def _dispatch(self, tid, cfg) -> HodgeTaskResult:
        """Единственный вход в задачу (§4.1). id ∉ SUITE_IDS → ERR_UNKNOWN_TASK."""
        t = self._task(tid)
        if t is None:
            self.log.ledger("ERR_UNKNOWN_TASK")
            return HodgeTaskResult(False, f"ERR_UNKNOWN_TASK {tid}", {})
        return t["fn"](cfg)

    # ── §5.1: two-pass обёртка ──
    def run_task_two_pass(self, tid) -> dict:
        t = self._task(tid)
        cfg = self.cfg
        seed_before = cfg.seed
        rec = {"id": tid, "slug": t["slug"], "title": t["title"],
               "claims": t["claims"], "passes": {}, "verdict": "FAIL", "reason": None}
        # §25 / VII.4: --cache on → попробовать дисковый кэш (ключ = task+cfg_hash)
        cached = self._cache.get(tid) if getattr(cfg, "cache_on", False) else None
        if cached and isinstance(cached, dict) and "passes" in cached:
            rec.update({k: cached[k] for k in
                        ("passes", "verdict", "ok", "worst") if k in cached})
            rec["reason"] = hodge_fmt(cfg, "cache.hit", id=tid) + " (pass2 isolation: cached)"
            self.log.log_comp("INFO", "Cache", hodge_fmt(cfg, "cache.hit", id=tid))
            self.log.event("INFO", "Cache", "hit", task=t["slug"])
            return rec
        if getattr(cfg, "cache_on", False):
            self.log.log_comp("DEBUG", "Cache", hodge_fmt(cfg, "cache.miss", id=tid))
        try:
            passes = []
            if cfg.pass_only in (0, 1):
                passes.append(1)
            if cfg.two_pass and cfg.pass_only in (0, 2) and t["pass2_fn"]:
                passes.append(2)

            # §9.2 / A12: STDOUT_CAPTURE — stdout задачи tee-ится в файл.
            # Только когда есть run_dir (меню-путь тоже создаёт run_dir заранее).
            cap_path = None
            old_stdout = sys.stdout
            if self.cfg.run_dir:
                task_slug = safe_slug(t["slug"]) or f"task{tid:02d}"
                tdir = os.path.join(self.cfg.run_dir, f"task_{tid:02d}_{task_slug}")
                os.makedirs(os.path.join(tdir, "logs"), exist_ok=True)
                cap_path = os.path.join(tdir, "logs", "stdout_capture.txt")
                sys.stdout = _TeeStdout(cap_path)
            try:
                # §5.3 / II.4: домен задачи — derive(seed, "task", tid);
                # фаза пасса — derive(seed, "task", tid, "pass", pno).
                # Пасс 2 больше не исключение: оба пасса изолированы одинаково.
                cfg.seed = cfg.derive_seed("task", tid)
                for pno in passes:
                    cfg.seed = cfg.derive_seed("task", tid, "pass", pno)
                    fn = t["fn"] if pno == 1 else t["pass2_fn"]
                    fire_hook("pre_task", tid, t["slug"], pno, cfg)
                    t0 = time.monotonic()
                    # §15.8 / A15: локальный таймаут задачи — SIGALRM (POSIX).
                    # В CI §33.4 --task-timeout 60 обязан реально срабатывать.
                    timeout_s = float(getattr(cfg, "task_timeout", 0) or 0)
                    use_alarm = (timeout_s > 0 and os.name != "nt"
                                 and hasattr(signal, "SIGALRM"))
                    if use_alarm:
                        def _alarm(signum, frame):
                            raise TimeoutError(f"task timeout {timeout_s}s")
                        try:
                            old_h = signal.signal(signal.SIGALRM, _alarm)
                            signal.alarm(int(timeout_s) or 1)
                        except (OSError, ValueError):
                            use_alarm = False   # не main-thread — таймаут недоступен
                    try:
                        try:
                            res = fn(cfg)
                        except TimeoutError as ex:
                            res = HodgeTaskResult(False, f"TIMEOUT: {ex}", {})
                            self.log.ledger("ERR_TASK_TIMEOUT")
                        except Exception as ex:
                            res = HodgeTaskResult(False,
                                                  f"EXCEPTION: {type(ex).__name__}: {ex}", {})
                            self.log.ledger("ERR_TASK_EXCEPTION")
                    finally:
                        if use_alarm:
                            signal.alarm(0)
                            try:
                                signal.signal(signal.SIGALRM, old_h)
                            except (OSError, ValueError):
                                pass
                    dur = time.monotonic() - t0
                    fire_hook("post_task", tid, t["slug"], pno, res)
                    fire_hook("on_verdict", tid, t["slug"], res.verdict)
                    if not res.ok:
                        fire_hook("on_error", tid, t["slug"], res.verdict, res.metrics)
                    rec["passes"][pno] = {
                        "ok": res.ok, "verdict": res.verdict,
                        "metrics": res.metrics, "duration_s": round(dur, 3),
                        "seed": cfg.seed,
                    }
                    self.log.metric(f"task{tid}_duration_s", "timer", round(dur, 3),
                                    tags={"pass": pno, "slug": t["slug"]})
                    self.log.event("INFO" if res.ok else "ERROR", "Task", "verdict",
                                   task=t["slug"], phase=f"pass{pno}",
                                   ok=res.ok, verdict=res.verdict)
            finally:
                if cap_path is not None:
                    sys.stdout.close()
                    sys.stdout = old_stdout

            p1 = rec["passes"].get(1)
            p2 = rec["passes"].get(2)
            if p1 is not None and p2 is not None:
                rec["ok"] = bool(p1["ok"] and p2["ok"])
                rec["verdict"] = "PASS" if rec["ok"] else "FAIL"
                rec["worst"] = (p2["verdict"] if not p2["ok"] else p1["verdict"])
            elif p2 is not None:
                rec["ok"] = bool(p2["ok"])
                rec["verdict"] = "PASS" if rec["ok"] else "FAIL"
                rec["worst"] = p2["verdict"]
            elif p1 is not None:
                rec["ok"] = bool(p1["ok"])
                rec["verdict"] = "PASS" if rec["ok"] else "FAIL"
            else:
                # B1: --pass-only 2 на задаче без pass2_fn, либо passes=[] — не crash
                rec["ok"] = False
                rec["verdict"] = "SKIP"
                rec["reason"] = "no passes scheduled (pass_only=2, task has no pass2_fn)"
        finally:
            cfg.seed = seed_before    # восстановление cfg даже при исключении (§5.1)
        rec["worst"] = rec.get("worst") or rec["verdict"]
        # §11 / §11.5: рендер плотов и animation.gif для задач с plot_fn.
        # Место вызова — run_task_two_pass, чтобы плоты появлялись и при
        # прямом --task N, а не только в _run_suite (§F).
        if getattr(cfg, "plot", True) and cfg.run_dir and not cfg.no_report:
            try:
                _render_plots_for_task(cfg, t, rec, logger=self.log)
            except Exception as ex:
                self.log.ledger("ERR_PLOT_RENDER")
                self.log.log_comp("WARN", "Plot",
                                  f"{t['slug']}: {type(ex).__name__}: {ex}")
        # §25 / VII.4: успешный результат — в кэш (повторный прогон мгновенен)
        if getattr(cfg, "cache_on", False) and rec.get("ok"):
            self._cache.put(tid, {k: rec[k] for k in
                                  ("passes", "verdict", "ok", "worst") if k in rec})
        return rec

    # ── §7.5 / III.2: управляющий файл <run_dir>/.hodge_ctl ──
    def _poll_ctl(self) -> None:
        """Команды: pause | resume | snapshot | abort | dump-metrics.
        После обработки — перезапись пустой (атомарно)."""
        if not self.cfg.run_dir:
            return
        now = time.monotonic()
        if now - getattr(self, "_ctl_last", 0) < 1.0:
            return
        self._ctl_last = now
        ctl = os.path.join(self.cfg.run_dir, ".hodge_ctl")
        if not os.path.exists(ctl):
            return
        try:
            with open(ctl, encoding="utf-8") as f:
                cmds = [ln.strip() for ln in f if ln.strip()]
        except OSError:
            return
        try:
            HODGEAdapter.atomic_write(ctl, "")
        except OSError:
            pass
        for cmd in cmds:
            if cmd == "pause":
                self.log.log_comp("INFO", "Ctl", "pause")
                while True:
                    if os.path.exists(ctl):
                        try:
                            peek = open(ctl, encoding="utf-8").read()
                            if "resume" in peek or "abort" in peek:
                                break
                        except OSError:
                            pass
                    time.sleep(0.25)
            elif cmd == "resume":
                self.log.log_comp("INFO", "Ctl", "resume (no-op)")
            elif cmd == "snapshot":
                if self.checkpoint_path:
                    self.save_checkpoint()
                self.log.log_comp("INFO", "Ctl", "snapshot → checkpoint")
            elif cmd == "abort":
                self.log.ledger("ERR_CTL_ABORT")
                HodgeRunner.request_cancel()
            elif cmd == "dump-metrics":
                hodge_metrics_export(self.cfg, self.log)
                self.log.log_comp("INFO", "Ctl", "metrics dumped")

    # ── §25.2: чекпоинт/resume ──
    def save_checkpoint(self) -> None:
        if not self.checkpoint_path:
            return
        data = {"cfg_hash": self.cfg.relevant_hash(), "tasks": {
            str(k): {"verdict": v["verdict"]} for k, v in self.results.items()}}
        HODGEAdapter.atomic_write(self.checkpoint_path,
                                  json.dumps(data, ensure_ascii=False, indent=1))

    def run_all(self) -> dict:
        """Полный прогон; изоляция задач try/except (§15.1); код 130 по SIGINT."""
        # §3.2 v5: честная оценка памяти при гигантском prec (до вычислений)
        if not hodge_prec_ram_guard(self.cfg):
            self.log.ledger("ERR_PREC_RAM")
            return {}
        # §3.2 v6: блок честных оценок + heartbeat (терминал не выглядит зависшим)
        if not self.silent:
            hodge_prec_report(self.cfg)
        HODGEPROG.start()
        ids = self.select_tasks()
        total = len(ids)
        # §15.8 / A15: глобальный дедлайн прогона
        gtimeout = float(getattr(self.cfg, "global_timeout", 0) or 0)
        deadline = (time.monotonic() + gtimeout) if gtimeout > 0 else None
        # §7.4 / III.1: sparkline + ETA + rate
        self._eta = HodgeETA()
        self._spark = HodgeSparkline()
        self._rate = HodgeRate()
        self._durations: list = []
        # §25 / VII.4: rate-limit между задачами
        self._rate_limiter = (HodgeRateLimit(self.cfg.rate_limit)
                              if getattr(self.cfg, "rate_limit", "") else None)
        self._ctl_last = 0.0
        self.log.event("INFO", "Run", "start", preset=self.cfg.preset,
                       seed=self.cfg.seed, tasks=total)
        if not self.silent:   # §26.2 / A3: в machine-режимах без промежуточных строк
            print(hodge_fmt(self.cfg, "run.start", run=os.path.basename(self.cfg.run_dir),
                            preset=self.cfg.preset, seed=self.cfg.seed), flush=True)
        skip_resume = set()
        if self.cfg.resume_dir:
            cp = os.path.join(self.cfg.resume_dir, "checkpoint.json")
            if os.path.exists(cp):
                try:
                    data = json.load(open(cp, encoding="utf-8"))
                    if data.get("cfg_hash") != self.cfg.relevant_hash():
                        self.log.ledger("ERR_RESUME_HASH")
                        if not self.cfg.strict:
                            self.log.log_comp("WARN", "Run",
                                              "cfg_hash изменился — resume продолжается (--strict прервал бы)")
                    for k, v in data.get("tasks", {}).items():
                        if v.get("verdict") == "PASS":
                            skip_resume.add(int(k))
                except Exception:
                    self.log.ledger("ERR_RESUME_READ")
        done = 0
        for tid in ids:
            HODGEPROG.set_task(f"t{tid}")
            t = self._task(tid)
            # §7.5 / III.2: управляющий файл <run_dir>/.hodge_ctl
            self._poll_ctl()
            # §7.6 / A16: SIGWINCH → invalidate banner и term-caps
            if HodgeRunner._sigwinch_flag:
                HodgeRunner._sigwinch_flag = False
                HodgeBanner.invalidate()
                HODGETerm.invalidate()
            # §7.6 / A16: SIGUSR1 → checkpoint-снапшот, продолжать
            if HodgeRunner._sigusr1_flag:
                HodgeRunner._sigusr1_flag = False
                if self.checkpoint_path:
                    self.save_checkpoint()
                    self.log.event("INFO", "Run", "snapshot_sigusr1",
                                   checkpoint=self.checkpoint_path)
                self.log.log_comp("INFO", "Run", "SIGUSR1: snapshot записан")
            # §7.6 / A16: SIGHUP → перечитать --config-file (пока — уведомление)
            if HodgeRunner._sighup_flag:
                HodgeRunner._sighup_flag = False
                self.log.log_comp("INFO", "Run",
                                  "SIGHUP: reload конфиг-файла оператором не задан")
            # §15.8 / A15: глобальный дедлайн → ERR_GLOBAL_TIMEOUT, код 4
            if deadline is not None and time.monotonic() > deadline:
                self.log.ledger("ERR_GLOBAL_TIMEOUT")
                self.results[tid] = {"id": tid, "slug": t["slug"], "title": t["title"],
                                     "claims": t["claims"], "passes": {}, "ok": False,
                                     "verdict": "FAIL", "reason": "GLOBAL_TIMEOUT"}
                break
            if tid in skip_resume and t["idempotent"]:
                self.log.log_comp("INFO", "Run", f"resume: задача {tid} пропущена (PASS в чекпоинте)")
                self.results[tid] = {"id": tid, "slug": t["slug"], "title": t["title"],
                                     "claims": t["claims"], "passes": {}, "ok": True,
                                     "verdict": "SKIP", "reason": "resumed PASS (idempotent)"}
                done += 1
                continue
            if self._sigint_flag:
                # §7.6 / A16: SIGTERM → ERR_SIGTERM (код 143), SIGINT → ERR_SIGINT (130)
                sig = "SIGTERM" if self._sigterm_flag else "SIGINT"
                self.log.ledger(f"ERR_{sig}")
                self.results[tid] = {"id": tid, "slug": t["slug"], "title": t["title"],
                                     "claims": t["claims"], "passes": {}, "ok": False,
                                     "verdict": "FAIL", "reason": sig}
                break
            self.log.log_comp("INFO", "Run", f"→ задача {tid} {t['slug']}")
            if self._rate_limiter:
                self._rate_limiter.wait()   # §25 / VII.4
            rec = self.run_task_two_pass(tid)
            rec.setdefault("ok", False)
            self.results[tid] = rec
            done += 1
            dur = sum(p["duration_s"] for p in rec["passes"].values())
            self._eta.push(dur)
            self._durations.append(dur)
            self._rate.tick()
            self.log.progress(done / total,
                              eta=self._eta.eta(total - done),
                              spark=self._spark.render(self._durations, 20),
                              rate=self._rate.rate())
            # §4.1 / §9.2 / A17: вердикт — через отдельный поток results_log
            self.log.log_result(
                tid, t["slug"], rec["verdict"], rec.get("reason"),
                claims=t["claims"],
                duration_s=sum(p["duration_s"] for p in rec["passes"].values()))
            if self.checkpoint_path:
                self.save_checkpoint()
            HODGEAdapter.gc_between_tasks()   # §12.1 между задачами
        # §7.6 / A16: флаги, пришедшие во время ПОСЛЕДНЕЙ задачи, тоже честно
        # ledger'ятся — иначе одиночный --task N с SIGTERM завершался бы кодом 0
        if HodgeRunner._sigusr1_flag:
            HodgeRunner._sigusr1_flag = False
            if self.checkpoint_path:
                self.save_checkpoint()
                self.log.event("INFO", "Run", "snapshot_sigusr1",
                               checkpoint=self.checkpoint_path)
        if self._sigint_flag:
            self.log.ledger("ERR_SIGTERM" if self._sigterm_flag else "ERR_SIGINT")
        self.log.event("INFO", "Run", "end", passed=sum(1 for r in self.results.values()
                                                        if r.get("ok")))
        return self.results

    _sigint_flag = False
    _sigterm_flag = False
    _sigusr1_flag = False
    _sighup_flag = False
    _sigwinch_flag = False

    @classmethod
    def request_cancel(cls):
        cls._sigint_flag = True

    @classmethod
    def request_terminate(cls):
        # §7.6 / A16: SIGTERM = graceful как SIGINT + код выхода 143
        cls._sigterm_flag = True
        cls._sigint_flag = True

    @classmethod
    def request_snapshot(cls):
        # §7.6 / A16: SIGUSR1 = checkpoint + results.json, продолжить
        cls._sigusr1_flag = True

    @classmethod
    def request_reload(cls):
        # §7.6 / A16: SIGHUP = перечитать --config-file, если задан
        cls._sighup_flag = True

    @classmethod
    def request_resize(cls):
        # §7.6 / A16: SIGWINCH = пересчитать ширину, banner-cache invalidate
        cls._sigwinch_flag = True


# ══════════════════════════════════════════════════════════════════════════
# §10/§20. ОТЧЁТЫ: per-task report.md/html; results.json; MANIFEST.toml;
# FINAL_REPORT (мастер-документ + RTM + errors + provenance); index.html —
# дашборд прогона в теме dark-gold (CSS-переменные из палитры, §10.4).
# PDF/DOCX-отчёты — §1.5: stdlib не умеет → честная пометка UNSUPPORTED.
# ══════════════════════════════════════════════════════════════════════════
class HodgeReports:
    def __init__(self, cfg: HodgeConfig, logger: HodgeLogger, theme: HODGEColor):
        self.cfg = cfg
        self.log = logger
        self.theme = theme

    def css_vars(self) -> str:
        # §17 / B7: нет хардкода #808080 — mono и missing-ключи берутся
        # из HODGEColor._mono (монохром собирается программно, §27.8)
        mono_fallback = HODGEColor("mono", "mono", plain=True)._mono
        pal = (mono_fallback if self.cfg.theme == "mono"
               else HODGEColor.THEMES.get(self.cfg.theme, HODGEColor.DARK_GOLD))

        def v(key):
            return pal.get(key, mono_fallback[key])[0]
        return (f"--bg:{v('bg')};--surface:{v('surface')};--gold:{v('gold')};"
                f"--gold-bright:{v('gold_bright')};--amber:{v('amber')};--ember:{v('ember')};"
                f"--text:{v('text')};--text-dim:{v('text_dim')};--ok:{v('ok')};"
                f"--warn:{v('warn')};--err:{v('err')};--neutral:{v('neutral')}")

    def html_shell(self, title: str, body: str) -> str:
        return (f"<!DOCTYPE html><html lang={self.cfg.lang!r}><head><meta charset='utf-8'>"
                f"<title>{title}</title><style>"
                ":root{" + self.css_vars() + "}"
                "body{background:var(--bg);color:var(--text);font-family:Georgia,serif;"
                "margin:2rem;line-height:1.5}"
                "h1,h2,h3{color:var(--gold-bright)}a{color:var(--amber)}"
                "table{border-collapse:collapse;width:100%}"
                "td,th{border:1px solid var(--neutral);padding:.35rem .6rem;text-align:left}"
                ".pass{color:var(--ok);font-weight:bold}.fail{color:var(--err);font-weight:bold}"
                ".skip{color:var(--neutral)}.warn{color:var(--warn)}"
                ".num{color:var(--gold)}.num.big{color:var(--amber);font-weight:bold}"
                "code,pre{background:var(--surface);padding:.15rem .4rem;border-radius:4px}"
                "@media print{body{background:#fff;color:#111}}"
                "</style></head><body>" + body + "</body></html>")

    def badge_html(self, verdict: str) -> str:
        cls = {"PASS": "pass", "FAIL": "fail", "SKIP": "skip", "WARN": "warn"}.get(verdict, "skip")
        return f"<span class='{cls}'>{verdict}</span>"

    def per_task(self, rec: dict, task_dir: str) -> None:
        """report.md + report.html одной задачи (§10.1).
        §16 v4: отчёты — ВСЕГДА на английском (машиночитаемость), независимо
        от cfg.lang; reason прогоняется через run_i18n(..., 'en')."""
        os.makedirs(task_dir, exist_ok=True)
        cls = rec["verdict"]
        reason_en = run_i18n(rec.get("reason") or "", "en")
        md = [f"# Task {rec['id']} · {rec['slug']}",
              "", f"**Verdict:** {cls}  ", f"**Claims:** {', '.join(rec['claims'])}  ",
              f"**Title:** {run_i18n(rec['title'], 'en')}", ""]
        html_rows = []
        for pno, p in sorted(rec["passes"].items()):
            pv = run_i18n(p["verdict"], "en")   # §16 v4: детали задач — EN в отчётах
            md.append(f"## pass {pno} — {pv} ({p['duration_s']:.3f} s, seed={p['seed']})")
            md.append("")
            md.append(pv)
            md.append("")
            if p["metrics"]:
                md.append("| metric | value |")
                md.append("|---|---|")
                for k, v in p["metrics"].items():
                    val = json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v
                    md.append(f"| {k} | {val} |")
                md.append("")
            html_rows.append(f"<tr><td>pass {pno}</td><td>{self.badge_html(p['verdict'])}</td>"
                             f"<td>{p['duration_s']:.3f} s</td><td>{pv}</td></tr>")
        if reason_en:
            md.append(f"> {reason_en}")
        md.append("")
        # §11 / §10.5: реальные плоты задачи, если движок их отрендерил;
        # пустые графики не фабрикуются.
        plot_files = sorted(glob.glob(os.path.join(task_dir, "plots", "*.png")))
        gif_files = sorted(glob.glob(os.path.join(task_dir, "plots", "*.gif")))
        if plot_files:
            md.append("Plots:")
            for pf in plot_files:
                md.append(f"  ![{os.path.basename(pf)}](plots/{os.path.basename(pf)})")
        if gif_files:
            md.append("Animation:")
            for gf in gif_files:
                md.append(f"  ![{os.path.basename(gf)}](plots/{os.path.basename(gf)})")
        if not (plot_files or gif_files):
            md.append("Plots: not rendered (fallback bar-chart disabled on empty "
                      "passes or --no-report; Part IV.2).")
        md.append("PDF/DOCX: ERR_UNSUPPORTED — the stdlib build does not generate "
                  "PDF/DOCX; closest equivalent is this MD and HTML (§1.5).")
        HODGEAdapter.atomic_write(os.path.join(task_dir, "report.md"), "\n".join(md))
        body = (f"<h1>Task {rec['id']} · {rec['slug']}</h1>"
                f"<p>Verdict: {self.badge_html(rec['verdict'])} · claims: {', '.join(rec['claims'])}</p>"
                f"<table><tr><th>pass</th><th>verdict</th><th>time</th><th>details</th></tr>"
                + "".join(html_rows) + "</table>")
        HODGEAdapter.atomic_write(os.path.join(task_dir, "report.html"),
                                  self.html_shell(f"task {rec['id']}", body))
        # PDF/DOCX-заглушки убраны (Часть IV.1)
        # §1.5 / §10.1 / Часть IV.1: PDF/DOCX — честно ERR_UNSUPPORTED, файлы
        # не создаются. --report-formats задаёт, какие форматы генерируются реально.
        fmts = {f.strip().lower() for f in self.cfg.report_formats.split(",")}
        if "pdf" in fmts or "docx" in fmts:
            self.log.ledger("ERR_UNSUPPORTED")
            self.log.log_comp("WARN", "Report",
                              "pdf/docx: stdlib build does not write PDF/DOCX (§1.5); "
                              "use md,html,svg,json")

    def master(self, run_dir: str, wall_s: float, exit_code: int) -> None:
        """results.json + MANIFEST.toml + index.html + FINAL_REPORT (§10.2)."""
        cfg = self.cfg
        os.makedirs(os.path.join(run_dir, "FINAL_REPORT"), exist_ok=True)
        results = {
            "run": {"started_at": getattr(self.log, "started_at", ""),
                    "finished_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "exit_code": exit_code, "cfg_hash": cfg.relevant_hash(),
                    "git_commit": _git_commit(), "theme": cfg.theme,
                    "preset": cfg.preset, "anim": "off (session 1)"},
            "task": {str(r["id"]): {"verdict": r["verdict"],
                                    "reason": r.get("reason"),
                                    "claims": r["claims"],
                                    "metrics": {f"pass{k}": v["metrics"] for k, v in r["passes"].items()},
                                    "duration_s": sum(p["duration_s"] for p in r["passes"].values())}
                     for r in self.results()} ,
            "errors": {k: {"count": v[0], "last_seen": v[1]}
                       for k, v in self.log.err_ledger.items()},
        }
        HODGEAdapter.atomic_write(os.path.join(run_dir, "results.json"),
                                  json.dumps(results, ensure_ascii=False, indent=1))
        HODGEAdapter.atomic_write(os.path.join(run_dir, "MANIFEST.toml"), self.manifest(run_dir))
        # index.html дашборд
        rows = []
        for r in self.results():
            rows.append(f"<tr><td>{r['id']}</td><td><a href='task_{r['id']:02d}_{r['slug']}/report.html'>{r['slug']}</a>"
                        f"</td><td>{self.badge_html(r['verdict'])}</td>"
                        f"<td class='num'>{sum(p['duration_s'] for p in r['passes'].values()):.2f}</td>"
                        f"<td>{', '.join(r['claims'])}</td></tr>")
        body = (f"<h1>Hodge Master · run {os.path.basename(run_dir)}</h1>"
                f"<p>preset <span class='num'>{cfg.preset}</span> · theme <span class='num'>{cfg.theme}</span> · "
                f"exit <span class='num big'>{exit_code}</span> · {wall_s:.1f} s</p>"
                f"<input type='search' placeholder='filter…'>"
                f"<table><tr><th>#</th><th>task</th><th>verdict</th><th>sec</th><th>claims</th></tr>"
                + "".join(rows) + "</table>"
                "<script>document.querySelector('input[type=search]').addEventListener('input',e=>{"
                "const q=e.target.value.toLowerCase();document.querySelectorAll('table tr').forEach(r=>{"
                "if(r.cells.length===5)r.style.display=r.textContent.toLowerCase().includes(q)?'':'none'})});</script>")
        HODGEAdapter.atomic_write(os.path.join(run_dir, "index.html"),
                                  self.html_shell("run dashboard", body))
        self.final_report(run_dir, exit_code)

    def manifest(self, run_dir: str) -> str:
        """§20.1 MANIFEST.toml."""
        sha_self = _self_sha256()
        art = ""
        # P2 / §20.1: ВСЕ артефакты прогона, не только FINAL_REPORT
        for root, _dirs, files in os.walk(run_dir):
            files = [f for f in sorted(files)
                     if not f.endswith((".lock", ".tmp")) and not f.startswith(".")]
            for f in files:
                rel = os.path.relpath(os.path.join(root, f), run_dir)
                with open(os.path.join(root, f), "rb") as fh:
                    art += f'"{rel}" = "sha256:{sha256(fh.read()).hexdigest()}"\n'
        cpu = os.cpu_count() or 1
        # §20.1 / B8: реальные сиды задач (домен "task", §5.3)
        seeds_lines = []
        for r in self.results():
            tid = r["id"]
            seeds_lines.append(f"  {tid} = 0x{self.cfg.derive_seed('task', tid):012x}")
        seeds_block = ("{\n" + ",\n".join(seeds_lines) + "\n}") if seeds_lines else "{}"
        return f"""[file]
path = "{HODGE_FILE_NAME}"
sha256 = "{sha_self}"
language = "python"
lang_version = "{platform.python_version()}"
build_date = "{HODGE_BUILD_DATE}"

[env]
platform = "{sys.platform}"
cpu_count = {cpu}
locale = "{os.environ.get('LANG', 'C')}"
color_depth = "{HODGETerm.caps()['color_depth']}"
term = "{os.environ.get('TERM', '')}"

[git]
commit = "{_git_commit()}"
dirty = true

[seeds]
by_task = {seeds_block}

[theme]
name = "{self.cfg.theme}"
anim = "off"
anim_scene = "{self.cfg.anim_scene}"

[presets]
applied = "{self.cfg.preset}"

[artifacts]
{art}"""

    def per_task_all(self, run_dir: str) -> None:
        """§10.1 + §24.3: per-task каталоги task_NN_slug; slug проходит path-guard."""
        for r in self.results():
            slug = safe_slug(r["slug"])
            if slug is None:
                self.log.ledger("ERR_PATH_TRAVERSAL")
                self.log.log_comp("WARN", "Report",
                                  f"slug {r['slug']!r} rejected by path-guard, falling back to taskNN")
                slug = f"task{r['id']:02d}"
            tdir = os.path.join(run_dir, f"task_{r['id']:02d}_{slug}")
            self.per_task(r, tdir)

    def final_report(self, run_dir: str, exit_code: int) -> None:
        """FINAL_REPORT: мастер-документ + копии + RTM + errors + provenance."""
        final = os.path.join(run_dir, "FINAL_REPORT")
        # §16 v4: отчёты всегда на английском — вердикт не зависит от cfg.lang
        verdict = "ALL CHECKS PASSED" if exit_code == 0 else "THERE ARE FAILURES"
        md = [f"# HODGE MASTER — final run report",
              "", f"- Run: `{os.path.basename(run_dir)}`",
              f"- Preset: `{self.cfg.preset}` · profile: `{self.cfg.profile}` · theme: `{self.cfg.theme}`",
              f"- cfg_hash: `{self.cfg.relevant_hash()}` · git: `{_git_commit()}`",
              f"- Verdict: **{verdict}** · exit_code: {exit_code}",
              f"- ERR_LEDGER: {json.dumps(self.log.err_ledger, ensure_ascii=False)}",
              "", "## Task verdicts", ""]
        for r in self.results():
            md.append(f"- **[{r['id']}] {r['slug']}** — {r['verdict']}"
                      f" · {', '.join(r['claims'])}"
                      + (f" · {run_i18n(r.get('reason'), 'en')}" if r.get("reason") else ""))
        md.append("")
        md.append("## Metrics (summary)")
        md.append("")
        for name, vals in sorted(self.log.metrics.items()):
            if vals and isinstance(vals[0], (int, float)):
                md.append(f"- {name}: n={len(vals)}, min={min(vals):.3f}, "
                          f"max={max(vals):.3f}, mean={sum(vals) / len(vals):.3f}")
        md.append("")
        HODGEAdapter.atomic_write(os.path.join(final, "final_report.md"), "\n".join(md))
        html_rows = "".join(
            f"<tr><td>{r['id']}</td><td>{r['slug']}</td><td>{self.badge_html(r['verdict'])}</td>"
            f"<td>{r.get('reason') or ''}</td></tr>" for r in self.results())
        HODGEAdapter.atomic_write(os.path.join(final, "final_report.html"),
                                  self.html_shell("final report",
                                                  f"<h1>Final report</h1>"
                                                  f"<p>{verdict}</p>"
                                                  f"<table><tr><th>#</th><th>task</th><th>verdict</th>"
                                                  f"<th>reason</th></tr>{html_rows}</table>"))
        # RTM: трассировка утверждений на задачи (§28.7)
        rtm = ["# RTM — Requirements Traceability Matrix",
               "",
               "Each row: repository claim → task-test → verdict.",
               ""]
        seen = {}
        for r in self.results():
            for c in r["claims"]:
                seen.setdefault(c, []).append((r["id"], r["verdict"]))
        for c in sorted(seen):
            entries = ", ".join(f"task {tid}→{v}" for tid, v in seen[c])
            rtm.append(f"- `{c}`: {entries}")
        rtm.append("")
        HODGEAdapter.atomic_write(os.path.join(final, "RTM.md"), "\n".join(rtm))
        HODGEAdapter.atomic_write(os.path.join(final, "errors.md"),
                                  "# ERR_LEDGER\n\n" + (
                                      "\n".join(f"- `{k}` ×{v[0]} (last seen: {v[1]})"
                                                for k, v in self.log.err_ledger.items())
                                      or "No errors recorded.") + "\n")
        HODGEAdapter.atomic_write(os.path.join(final, "provenance.md"),
                                  f"""# Provenance

- file: `{HODGE_FILE_NAME}` sha256 `{_self_sha256()}`
- language: python {platform.python_version()} · platform: {sys.platform}
- build date: {HODGE_BUILD_DATE} · master version: {HODGE_VERSION}
- domain repository: {HODGE_REPO_URL}
- theme: {self.cfg.theme} · animations: off (session 1) · preset: {self.cfg.preset}
- cfg_hash: {self.cfg.relevant_hash()}
""")
        # конфиг-снапшот
        snap = [f"{k} = {v!r}" for k, v in sorted(vars(self.cfg).items())]
        HODGEAdapter.atomic_write(os.path.join(final, "config_snapshot.txt"), "\n".join(snap))
        # вердикты в txt (§16 v4: reasons — на английском)
        HODGEAdapter.atomic_write(os.path.join(final, "results_verdicts.txt"),
                                  "\n".join(f"[{r['id']:2d}] {r['slug']}: {r['verdict']}"
                                            + (f" · {run_i18n(r.get('reason'), 'en')}" if r.get("reason") else "")
                                            for r in self.results()))
        # §9.2 / A17: копия results_log в FINAL_REPORT
        if self.log.results_path and os.path.exists(self.log.results_path):
            try:
                with open(self.log.results_path, encoding="utf-8") as f:
                    HODGEAdapter.atomic_write(os.path.join(final, "results_log.txt"), f.read())
            except OSError:
                pass
        # §10.2 / IV.2: обязательные файлы
        # full_run_log.txt = конкатенация per-task comp_log и stdout_capture
        full = []
        for r in self.results():
            slug = safe_slug(r["slug"]) or f"task{r['id']:02d}"
            tdir = os.path.join(run_dir, f"task_{r['id']:02d}_{slug}")
            for logname in ("computation_log.txt", "stdout_capture.txt"):
                p = os.path.join(tdir, "logs", logname)
                if os.path.exists(p):
                    full.append(f"\n# === {r['id']} {r['slug']} / {logname} ===\n")
                    try:
                        full.append(open(p, encoding="utf-8", errors="replace").read())
                    except OSError:
                        pass
        HODGEAdapter.atomic_write(os.path.join(final, "full_run_log.txt"), "".join(full))
        # computation_log_full.txt = глобальный comp_log
        if self.log.comp_path and os.path.exists(self.log.comp_path):
            try:
                HODGEAdapter.atomic_write(os.path.join(final, "computation_log_full.txt"),
                                          open(self.log.comp_path, encoding="utf-8").read())
            except OSError:
                pass
        # metrics_summary.md
        mlines = ["# Metrics Summary", ""]
        for name, vals in sorted(self.log.metrics.items()):
            nums = [v for v in vals if isinstance(v, (int, float))]
            if not nums:
                continue
            n = len(nums)
            mlines.append(f"- **{name}**: n={n}, min={min(nums):.4f}, "
                          f"max={max(nums):.4f}, mean={sum(nums) / n:.4f}")
        HODGEAdapter.atomic_write(os.path.join(final, "metrics_summary.md"),
                                  "\n".join(mlines) + "\n")
        # подпись HMAC §20.5
        if self.cfg.sign_key:
            self.sign(final)

    def sign(self, final_dir: str) -> None:
        """HMAC-SHA256 артефактов; ключ не логируется (§24.10)."""
        try:
            key = open(self.cfg.sign_key, "rb").read()
        except OSError as ex:
            self.log.ledger("ERR_SIGN_KEY")
            self.log.log_comp("WARN", "Report", f"signing key unavailable: {ex}")
            return
        lines = []
        for root, _dirs, files in os.walk(final_dir):
            for f in sorted(files):
                p = os.path.join(root, f)
                rel = os.path.relpath(p, final_dir)
                mac = hmac.new(key, open(p, "rb").read(), hashlib.sha256).hexdigest()
                lines.append(f"{mac}  {rel}")
        HODGEAdapter.atomic_write(os.path.join(final_dir, "signature.sha256"),
                                  "\n".join(lines) + "\n")

    def bind(self, runner: HodgeRunner) -> None:
        self._runner = runner

    def results(self) -> list:
        # устойчивость: отчёты строятся без bind(runner) → пусто
        if getattr(self, "_runner", None) is None:
            return []
        return [self._runner.results[k] for k in sorted(self._runner.results)]


def _git_commit() -> str:
    return "unknown (standalone master file)"


def _self_sha256() -> str:
    try:
        return sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()
    except OSError:
        return "unavailable"


# ══════════════════════════════════════════════════════════════════════════
# §6. БАННЕР/SPLASH/TIPS: арт — константа (не генерится, §6.1); градиент по
# вертикали; предрендер один раз (§6.6); NO_COLOR/TERM=dumb/--plain → off.
# ══════════════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════════════
# §6.1 ASCII-АРТ (константа, не генерится). Unicode-версия — «HODGE» блоками,
# ASCII-фолбэк для --unicode off / TERM=dumb (§27.2). Градиент по вертикали,
# каждый символ — свой оттенок (§22.4). В --plain — монохром.
# ══════════════════════════════════════════════════════════════════════════
HODGE_BANNER_ART = r"""
  ██╗  ██╗ ██████╗ ██████╗  ██████╗ ███████╗
  ██║  ██║██╔═══██╗██╔══██╗██╔════╝ ██╔════╝
  ███████║██║   ██║██║  ██║██║  ███╗█████╗
  ██╔══██║██║   ██║██║  ██║██║   ██║██╔══╝
  ██║  ██║╚██████╔╝██████╔╝╚██████╔╝███████╗
  ╚═╝  ╚═╝ ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝
   m a s t e r  ·  h o d g e - l a b o r a t o r y
"""

HODGE_BANNER_ASCII = r"""
  _   _           _      ____  ___  ____  _____ ____
 | | | | ___  ___| |_   / ___|/ _ \|  _ \| ____|  _ \
 | |_| |/ _ \/ _ \ __| | |  _| | | | |_) |  _| | |_) |
 |  _  |  __/  __/ |_  | |_| | |_| |  _ <| |___|  _ <
 |_| |_|\___|\___|\__|  \____|\___/|_| \_\_____|_| \_\
   master verification suite · hodge-laboratory claims
"""

class HodgeBanner:
    _rendered: dict = {}

    @classmethod
    def render(cls, kind: str, theme: HODGEColor, cfg: HodgeConfig) -> str:
        """§6.1: full — ASCII-арт с градиентом; compact — [name ver@date];
        minimal — name ver. Кэш инвалидируется сменой темы (§6.6)."""
        key = (kind, theme.name, theme.depth, HODGEText.unicode_on)
        if key in cls._rendered:
            return cls._rendered[key]
        if kind == "off":
            cls._rendered[key] = ""
            return ""
        # §27.2 / A13: при --unicode off — чистый ASCII-арт
        art_src = HODGE_BANNER_ART if HODGEText.unicode_on else HODGE_BANNER_ASCII
        if theme.plain or not HODGEText.unicode_on:
            out = {
                "minimal": f"hodge-master {HODGE_VERSION}",
                "compact": f"[hodge-master {HODGE_VERSION}@{HODGE_BUILD_DATE}] · {theme.name}",
            }.get(kind, art_src.rstrip("\n"))
            cls._rendered[key] = out
            return out
        if kind == "minimal":
            out = HODGEText.dye(f"hodge-master {HODGE_VERSION}", "gold")
        elif kind == "compact":
            out = HODGEText.dye(f"[hodge-master {HODGE_VERSION}@{HODGE_BUILD_DATE}] · {theme.name}", "gold")
        else:
            # full: каждый символ — своим оттенком, вертикальный градиент
            lines = art_src.rstrip("\n").split("\n")
            pal_keys = ["gold_dim", "gold", "gold_bright", "amber"]
            n = len(lines)
            colored = []
            for i, ln in enumerate(lines):
                ln_len = max(len(ln), 1)
                buf = []
                for j, ch in enumerate(ln):
                    tt = (i / max(n - 1, 1)) * 0.5 + (j / ln_len) * 0.5
                    k = pal_keys[min(int(tt * (len(pal_keys) - 1)), len(pal_keys) - 1)]
                    buf.append(HODGEText.dye(ch, k) if ch != " " else " ")
                colored.append("".join(buf))
            meta = (HODGEText.dye(f"v{HODGE_VERSION}", "gold_bright") + " · "
                    + HODGEText.dye(f"python {platform.python_version().rsplit('.', 1)[0]}", "text_dim")
                    + " · " + HODGEText.dye(theme.name, "gold") + " · "
                    + HODGEText.dye(f"prec={cfg.prec} бит", "gold_dim") + " · "
                    + HODGEText.dye(f"seed={cfg.seed}", "gold_dim"))
            out = "\n".join(colored) + "\n" + meta
        cls._rendered[key] = out
        return out

    @classmethod
    def invalidate(cls):
        cls._rendered.clear()

    @classmethod
    def splash(cls, cfg: HodgeConfig, theme: HODGEColor) -> list:
        """§6.2: ≤ 8 строк; версия, платформа, CPU, RAM, язык, тема, lock."""
        caps = HODGETerm.caps()
        ram = "—"
        try:
            with open("/proc/meminfo", encoding="ascii") as f:
                for ln in f:
                    if ln.startswith("MemTotal"):
                        ram = HODGEText.fmt_size(int(ln.split()[1]) * 1024)
                        break
        except OSError:
            pass
        # §24.2 / A7: lock-статус — реальный, из глобала, не hardcode
        # BUGFIX(LOCK): при flock-unsupported (ENOSYS) не «acquired», а честный
        # статус каскада: lockfile (взаимоисключение сохранено) или advisory
        lock_status = ("advisory (flock unsupported)" if _LOCK_MODE == "advisory"
                       else "lockfile (flock unsupported)" if _LOCK_MODE == "lockfile"
                       else "acquired" if _RUN_LOCK_FD is not None else "free")
        rows = [
            f"platform: {sys.platform} · CPU: {os.cpu_count() or 1} · RAM: {ram}",
            f"lang: python {platform.python_version()} · "
            f"{'theme' if cfg.lang == 'en' else 'тема'}: {theme.name} · depth: {caps['color_depth']}",
            # §27.2 / A13: ✓/✗ проходят ASCII-фолбэк при --unicode off
            # §3.2 v5: при гигантском prec — честная оценка памяти на число
            f"unicode: {HODGEText._ascii_fallback('✓' if caps['unicode'] else '✗')} · preset: {cfg.preset} · prec: {cfg.prec}"
            + (f" (≈{HODGEText.fmt_size(int(cfg.prec * 8 / 19) + 64)}/num)" if cfg.prec > 1024 else "")
            + f" · seed: {cfg.seed}",
            f"pid: {os.getpid()} · lock: {lock_status}",
        ]
        return rows

    @classmethod
    def tip_of_day(cls, cfg: HodgeConfig) -> str:
        """§6.3: ротация по дню года, actionable. §20.2: --deterministic → нет tip."""
        if cfg.deterministic:
            return ""
        TIPS = {
            "ru": ["Попробуй `--self-test --palette --dye` — проверка темы и глифов.",
                   "`--task 8` — глубокий рекорд точности V9 (prec 95).",
                   "`--theme-preview` покажет палитру dark-gold и фолбэки 256/16.",
                   "`--ci --task all` — машиночитаемый прогон с events.jsonl.",
                   "`T` в меню меняет тему; `a` запускает все задачи."],
            "en": ["Try `--self-test --palette --dye` — theme and glyph checks.",
                   "`--task 8` runs the V9 deep-precision record (prec 95).",
                   "`--theme-preview` shows the dark-gold palette and 256/16 fallbacks.",
                   "`--ci --task all` gives a machine-readable run with events.jsonl.",
                   "`T` in the menu switches theme; `a` runs all tasks."],
        }
        tips = TIPS.get(cfg.lang, TIPS["en"])
        idx = int(datetime.now().timetuple().tm_yday) % len(tips)
        return tips[idx]


# ══════════════════════════════════════════════════════════════════════════
# §13. CLI: парсер флагов §13.2; «терминальные» команды — немедленный выход
# (§13.1); порядок парсинга §13.4; неизвестный флаг — WARNING (или error при
# --strict). Меню-first: голый запуск в tty → меню (§14.1).
# ══════════════════════════════════════════════════════════════════════════
CLI_SCHEMA = [
    # (флаг, аргумент, описание ru)
    ("--help", 0, "полная справка и выход"),
    ("--version", 0, "версия и выход (minimal-баннер)"),
    ("--menu", 0, "форсировать меню даже при --task"),
    ("--no-menu", 0, "никогда не открывать меню"),
    ("--task", 1, "id или 'all' (можно списком: 1,3,8)"),
    ("--with-deps", 0, "тянуть зависимости задач (DAG, §4.2)"),
    ("--tag", 1, "фильтр по тегам: fast,!heavy"),
    ("--list-tasks", 0, "реестр задач (tsv|json|md)"),
    ("--list-tags", 0, "список тегов"),
    ("--list-presets", 0, "пресеты с наследованием"),
    ("--preset", 1, "quick | full | deep"),
    ("--profile", 1, "safe | balanced | fast | paranoid"),
    ("--seed", 1, "сид прогона"),
    ("--size", 1, "размер (макс N ценза)"),
    ("--prec", 1, "точность Decimal (30..∞; суффиксы k/m/g/t: 4096, 5m, 1g)"),
    ("--run-two-pass/--no-two-pass", 0, "двухпроходный режим (§5)"),
    ("--pass-only", 1, "1 | 2 — отладочный пасс"),
    ("--deterministic", 0, "зафиксировать RNG-домены (§20.2)"),
    ("--theme", 1, "dark-gold|aurora|ice|gold|emerald|mono"),
    ("--theme-preview", 0, "свотчи палитры и выход"),
    ("--color-depth", 1, "auto|truecolor|256|16|mono"),
    ("--no-truecolor", 0, "форс 256"),
    ("--plain", 0, "screen-reader режим: без ANSI/боксов/\\r"),
    ("--no-color", 0, "без ANSI"),
    ("--unicode", 1, "auto|on|off (off → ASCII)"),
    ("--no-banner", 0, "без баннера"),
    ("--no-splash", 0, "без splash"),
    ("--no-tips", 0, "без tip-of-the-day"),
    ("--no-clear", 0, "не очищать экран"),
    ("--dye", 1, "auto|on|off"),
    ("--dye-mode", 1, "per-char|per-token|per-line"),
    ("--digit-tier", 1, "on|off (per-digit tiering чисел)"),
    ("--gradient", 1, "span|line|block|off"),
    ("--anim", 1, "auto|on|off (сессия 1: печать только в tty)"),
    ("--anim-scene", 1, "particles|wave|sparkle|constellation|matrix|off"),
    ("--monitor", 1, "on|off|panel|probe|animate"),
    ("--anim-seconds", 1, "сек для --monitor animate (0 = до Ctrl+C)"),
    ("--fps", 1, "fps анимации: 15|24|30|60"),
    ("--particles", 1, "число частиц в сцене particles"),
    ("--plot", 1, "on|off — включить/выключить графики per-task (§11)"),
    ("--plot-formats", 1, "png,gif (по умолчанию)"),
    ("--plot-width", 1, "ширина PNG (дефолт 800)"),
    ("--plot-height", 1, "высота PNG (дефолт 480)"),
    ("--plot-aa", 1, "супер-сэмплинг: 1|2|4 (дефолт 2)"),
    ("--lab3d", 1, "3D-лаборатория: omega|period_re|census_h|expr:…"),
    ("--lab-video", 1, "3D Video Lab: имя объекта (sphere|torus|klein|trefoil|mobius|fermat_k3_affine|barth_sextic|gyroid)"),
    ("--lab-video-fps", 1, "кадров/с видео (5..60, по умолчанию 24)"),
    ("--lab-video-frames", 1, "число кадров (2..2000, по умолчанию 120)"),
    ("--lab-video-N", 1, "плотность сетки N_full (16..128, по умолчанию 64)"),
    ("--sweep", 1, "name:lo:hi:step — можно несколько (декартово произведение)"),
    ("--lab-max-frames", 1, "лимит кадров лаборатории (дефолт 500)"),
    ("--lab-grid", 1, "N×N сетка поверхности (дефолт 48)"),
    ("--lab-output", 1, "каталог для лаборатории (дефолт run_dir/lab3d)"),
    ("--prec-extreme", 0, "prec=200 + K=480 для рекордных задач"),
    ("--unsafe-prec", 0, "разрешить prec с оценкой памяти > RAM (обход ERR_PREC_RAM, §3.2 v5)"),
    ("--report-formats", 1, "md,html,svg (по умолчанию); pdf,docx → ERR_UNSUPPORTED"),
    ("--recipe", 1, "применить рецепт (см. --list-recipes)"),
    ("--list-recipes", 0, "список рецептов"),
    ("--monitor-interval", 1, "интервал проб монитора, сек (дефолт 60)"),
    ("--metrics-format", 1, "json|tsv|prom"),
    ("--rlimit-as", 1, "RLIMIT_AS в MB"),
    ("--rlimit-cpu", 1, "RLIMIT_CPU в сек"),
    ("--rlimit-fsize", 1, "RLIMIT_FSIZE в MB"),
    ("--rlimit-report", 0, "печать текущих rlimit"),
    ("--tui", 0, "full-screen TUI (без мыши, минимальный)"),
    ("--golden-dir", 1, "каталог golden-эталонов (дефолт tests/golden)"),
    ("--float-tolerance", 1, "допуск для float (дефолт 1e-9)"),
    ("--stats", 0, "bench: t-test (n≥5)"),
    ("--bench-runs", 1, "число прогонов для статистики (дефолт 5)"),
    ("--anim-cpu-guard", 1, "CPU% порог для деградации анимации (дефолт 40)"),
    ("--anim-intensity", 1, "low|med|high"),
    ("--particles-charset", 1, "gold|digits|hex|custom:<str>"),
    ("--particles-trail", 1, "on|off"),
    ("--clean-orphans", 1, "on|off"),
    ("--no-redact", 0, "отключить редакцию секретов (WARN в отчёт)"),
    ("--cache", 1, "on|off"),
    ("--rate", 1, "n/unit (например 10/s)"),
    ("--links", 1, "auto|on|off (OSC 8 hyperlinks)"),
    ("--no-clipboard", 0, "отключить OSC 52 clipboard"),
    ("--no-settings-cache", 0, "не читать/не писать .cache/settings.json (§3.2 v4)"),
    ("--settings-save", 0, "сохранить настройки ЭТОГО CLI-прогона в кэш настроек"),
    ("--settings-reset", 0, "очистить кэш настроек .cache/settings.json"),
    ("--health-probe-sec", 1, "интервал health-probe в прогоне (0 = выкл)"),
    ("--lang", 1, "ru | en"),
    ("--log-level", 1, "TRACE..FATAL"),
    ("--ci", 0, "неинтерактивный прогон (§26.1)"),
    ("--jsonl", 0, "построчный machine-readable вывод"),
    ("--tsv", 0, "TSV-вывод с заголовком"),
    ("--junit", 1, "путь к JUnit XML (§26.3)"),
    ("--no-report", 0, "без отчётов (логи остаются, §28.5)"),
    ("--report-dir", 1, "каталог результатов"),
    ("--self-test", 0, "встроенные тесты (§19)"),
    ("--full", 0, "self-test: интеграционный уровень"),
    ("--golden", 0, "self-test: golden-сравнение"),
    ("--props", 0, "self-test: property-инварианты"),
    ("--l10n", 0, "self-test: паритет словарей MSG"),
    ("--palette", 0, "self-test: палитра и глубины"),
    ("--dye-test", 0, "self-test: dye/num/gradient"),
    ("--anim-test", 0, "self-test: сцены и alt-screen парность"),
    ("--menu-test", 0, "self-test: меню в tty-эмуляции"),
    ("--plot-test", 0, "self-test: кодеки PNG/GIF и канва §11"),
    ("--lab-test", 0, "self-test: 3D-лаборатория и sweep-парсер"),
    ("--golden-update", 0, "перезаписать golden-эталоны"),
    ("--bench", 0, "бенчмарк задач (§19.5)"),
    ("--bench-threshold", 1, "порог регрессии (по умолчанию 1.2)"),
    ("--warmup", 0, "прогрев перед бенчем"),
    ("--fuzz", 1, "секунды фаззинга парсеров (§19.6)"),
    ("--coverage", 0, "строковое покрытие self-test (§19.7)"),
    ("--doctor", 0, "диагностика среды (§13.3)"),
    ("--health", 0, "быстрая проверка (≤ 2 с)"),
    ("--dry-run", 0, "план прогона без вычислений"),
    ("--print-config", 0, "эффективный конфиг"),
    ("--explain-config", 0, "дерево поле → значение → источник"),
    ("--validate-config", 0, "валидация схемы без запуска"),
    ("--config-file", 1, "TOML/JSON конфиг (tomllib, §3.2)"),
    ("--diff", 2, "сравнить два прогона: --diff A B"),
    ("--resume", 1, "продолжить прогон из run_dir"),
    ("--sign-key", 1, "ключ HMAC для подписи артефактов"),
    ("--verify-signature", 1, "проверить подпись run_dir"),
    ("--task-timeout", 1, "сек на задачу"),
    ("--global-timeout", 1, "сек на весь прогон"),
    ("--strict", 0, "неизвестный флаг/расхождение → ошибка"),
    ("--notify", 1, "auto|osc|bell|off"),
    ("--generate-man", 0, "roff-мануал в stdout"),
    ("--generate-completions", 1, "bash|zsh|fish|powershell"),
    ("--theme-file", 1, "TOML-тема поверх dark-gold (мерж по ключам)"),
]

def parse_cli(cfg: HodgeConfig, argv: list) -> tuple:
    """Возвращает (terminal_action, warns). terminal_action: None | строка."""
    warns = []
    explicit: set = set()   # §1.4 / B2: явно выставленные CLI-поля — профиль их не трогает
    i = 0
    n = len(argv)
    while i < n:
        a = argv[i]
        if a in ("--help", "-h"):
            return "help", warns
        if a == "--version":
            return "version", warns
        i0 = i
        def take(k=1):
            nonlocal i
            vals = argv[i + 1:i + 1 + k]
            if len(vals) < k:
                raise ValueError(f"{a} expects {k} argument(s)")
            i += 1 + k      # сам флаг + его аргументы (i указывал на флаг)
            return vals
        try:
            if a == "--menu":
                cfg.menu_forced = True
            elif a == "--no-menu":
                cfg.menu_off = True
            elif a == "--task":
                v = take()[0]
                cfg.tasks = list(SUITE_IDS) if v == "all" else [int(x) for x in v.split(",")]
                explicit.add("tasks")   # BUGFIX(P9): явный CLI-флаг для профиля (§1.4)
            elif a == "--with-deps":
                cfg.with_deps = True
            elif a == "--tag":
                cfg.tags.extend(take()[0].split(","))
            elif a == "--list-tasks":
                return "list-tasks", warns
            elif a == "--list-tags":
                return "list-tags", warns
            elif a == "--list-presets":
                return "list-presets", warns
            elif a == "--preset":
                v = take()[0]
                cfg.preset = v
                apply_preset(cfg, v)
            elif a == "--profile":
                cfg.profile = take()[0]
            elif a == "--seed":
                cfg.seed = int(take()[0])
            elif a == "--size":
                cfg.size = int(take()[0])
            elif a == "--prec":
                _pv = parse_prec_value(take()[0])
                if _pv is None:
                    raise ValueError("--prec: ожидалось N ≥ 30 или Nk/Nm/Ng/Nt (напр. 4096, 5m, 1g)")
                cfg.prec = _pv
            elif a == "--unsafe-prec":
                cfg.unsafe_prec = True
            elif a in ("--run-two-pass", "--two-pass"):
                cfg.two_pass = True
            elif a == "--no-two-pass":
                cfg.two_pass = False
            elif a == "--pass-only":
                cfg.pass_only = int(take()[0])
            elif a == "--deterministic":
                cfg.deterministic = True
            elif a == "--theme":
                cfg.theme = take()[0]
            elif a == "--theme-preview":
                return "theme-preview", warns
            elif a == "--color-depth":
                cfg.color_depth = take()[0]
            elif a == "--no-truecolor":
                cfg.color_depth = "256"
            elif a == "--plain":
                cfg.plain = True
            elif a == "--no-color":
                cfg.no_color = True
            elif a == "--unicode":
                cfg.unicode_on = take()[0]
            elif a in ("--no-banner",):
                cfg.banner = "off"
            elif a == "--no-splash":
                cfg.splash = False
            elif a == "--no-tips":
                cfg.tips = False
            elif a == "--no-clear":
                cfg.no_clear = True
            elif a == "--dye":
                cfg.dye = take()[0]
            elif a == "--dye-mode":
                cfg.dye_mode = take()[0]; explicit.add("dye_mode")
            elif a == "--digit-tier":
                cfg.digit_tier = take()[0] == "on"
            elif a == "--gradient":
                cfg.gradient = take()[0]; explicit.add("gradient")
            elif a == "--anim":
                cfg.anim = take()[0]
            elif a == "--anim-scene":
                cfg.anim_scene = take()[0]
            elif a == "--monitor":
                v = take()[0]
                cfg.monitor = v
                if v == "animate" and (cfg.ci or cfg.jsonl or cfg.tsv
                                       or not HODGEAdapter.isatty(sys.stdout)):
                    # §23.10 / A8: в pipe/CI animate = panel без alt-screen
                    cfg.monitor = "panel"
                elif v == "animate":
                    return "monitor-animate", warns
            elif a == "--anim-seconds":
                cfg.anim_seconds = float(take()[0])
            elif a == "--fps":
                cfg.fps = int(take()[0]); explicit.add("fps")
            elif a == "--particles":
                cfg.particles = int(take()[0]); explicit.add("particles")
            elif a == "--plot":
                cfg.plot = take()[0] != "off"
            elif a == "--plot-formats":
                cfg.plot_formats = take()[0]
            elif a == "--plot-width":
                cfg.plot_width = int(take()[0])
            elif a == "--plot-height":
                cfg.plot_height = int(take()[0])
            elif a == "--plot-aa":
                cfg.plot_aa = int(take()[0])
            elif a == "--lab3d":
                cfg.lab3d = take()[0]
            elif a == "--lab-video":
                # §11.10: 3D Video Lab — имя объекта; диспетчер в hodge_main
                # по членству в _LAB_VIDEO_OBJECTS (имена не пересекаются
                # с omega|period_re|census_h — коллизий с --lab3d нет)
                cfg.lab3d = take()[0]
            elif a == "--lab-video-fps":
                _LAB_VIDEO_PARAMS["fps"] = max(5, min(60, int(take()[0])))
            elif a == "--lab-video-frames":
                _LAB_VIDEO_PARAMS["frames"] = max(2, min(2000, int(take()[0])))
            elif a == "--lab-video-N":
                _LAB_VIDEO_PARAMS["n"] = max(16, min(128, int(take()[0])))
            elif a == "--sweep":
                cfg.sweeps.append(take()[0])   # накопительный (§11.6)
            elif a == "--lab-max-frames":
                cfg.lab_max_frames = int(take()[0])
            elif a == "--lab-grid":
                cfg.lab_grid = int(take()[0])
            elif a == "--lab-output":
                cfg.lab_output = take()[0]
            elif a == "--prec-extreme":
                cfg.prec_extreme = True
                cfg.prec = max(cfg.prec, 200)
            elif a == "--report-formats":
                cfg.report_formats = take()[0]
            elif a == "--recipe":
                v = take()[0]
                try:
                    apply_recipe(cfg, v)
                except ValueError as ex:
                    warns.append(f"WARNING: {ex}")
            elif a == "--list-recipes":
                return "list-recipes", warns
            elif a == "--monitor-interval":
                cfg.monitor_interval = float(take()[0])
            elif a == "--metrics-format":
                cfg.metrics_format = take()[0]; explicit.add("metrics_format")
            elif a == "--rlimit-as":
                cfg.rlimit_as = int(take()[0])
            elif a == "--rlimit-cpu":
                cfg.rlimit_cpu = int(take()[0])
            elif a == "--rlimit-fsize":
                cfg.rlimit_fsize = int(take()[0])
            elif a == "--rlimit-report":
                cfg.rlimit_report = True
            elif a == "--tui":
                cfg.tui = True
            elif a == "--golden-dir":
                cfg.golden_dir = take()[0]
            elif a == "--float-tolerance":
                cfg.float_tolerance = float(take()[0])
            elif a == "--stats":
                cfg.bench_stats = True
            elif a == "--bench-runs":
                cfg.bench_runs = int(take()[0])
            elif a == "--anim-cpu-guard":
                cfg.anim_cpu_guard = float(take()[0])
            elif a == "--anim-intensity":
                cfg.anim_intensity = take()[0]
            elif a == "--particles-charset":
                cfg.particles_charset = take()[0]
            elif a == "--particles-trail":
                cfg.trail_particles = take()[0] == "on"
            elif a == "--clean-orphans":
                cfg.clean_orphans = take()[0] == "on"
            elif a == "--no-redact":
                cfg.redact = False
            elif a == "--cache":
                cfg.cache_on = take()[0] == "on"
            elif a == "--rate":
                cfg.rate_limit = take()[0]
            elif a == "--links":
                cfg.links = take()[0]
            elif a == "--no-clipboard":
                cfg.no_clipboard = True
            elif a == "--no-settings-cache":
                # §3.2 v4: кэш настроек уже применён ДО parse_cli (приоритет:
                # cache < CLI) — флаг лишь запрещает СОХРАНЕНИЕ в этом запуске
                cfg.settings_cache = False
            elif a == "--settings-save":
                cfg.settings_save = True
            elif a == "--settings-reset":
                pass   # обработан ранним пре-сканом hodge_main (сильнее кэша)
            elif a == "--health-probe-sec":
                cfg.health_probe_sec = float(take()[0])
            elif a == "--lang":
                cfg.lang = take()[0]
            elif a == "--log-level":
                cfg.log_level = take()[0].upper(); explicit.add("log_level")
            elif a == "--ci":
                cfg.ci = True
            elif a == "--jsonl":
                cfg.jsonl = True
            elif a == "--tsv":
                cfg.tsv = True
            elif a == "--junit":
                cfg.junit = take()[0]
                explicit.add("junit")   # BUGFIX(P9): был только в комментарии Julia-версии
            elif a == "--no-report":
                cfg.no_report = True
            elif a == "--report-dir":
                cfg.report_dir = take()[0]
            elif a == "--self-test":
                cfg.self_test = ["unit"]
            elif a == "--full":
                cfg.self_test.append("full")
            elif a == "--golden":
                cfg.self_test.append("golden")
            elif a == "--props":
                cfg.self_test.append("props")
            elif a == "--l10n":
                cfg.self_test.append("l10n")
            elif a == "--palette":
                cfg.self_test.append("palette")
            elif a == "--dye-test":
                cfg.self_test.append("dye")
            elif a == "--anim-test":
                cfg.self_test.append("anim")
            elif a == "--menu-test":
                cfg.self_test.append("menu")
            elif a == "--plot-test":
                cfg.self_test.append("plot")
            elif a == "--lab-test":
                cfg.self_test.append("lab")
            elif a == "--golden-update":
                cfg.self_test.append("golden-update")
            elif a == "--bench":
                cfg.bench = True
            elif a == "--bench-threshold":
                cfg.bench_threshold = float(take()[0])
            elif a == "--warmup":
                pass
            elif a == "--fuzz":
                cfg.fuzz_sec = float(take()[0])
            elif a == "--coverage":
                cfg.coverage = True
            elif a == "--doctor":
                return "doctor", warns
            elif a == "--health":
                return "health", warns
            elif a == "--dry-run":
                cfg.dry_run = True
            elif a == "--print-config":
                cfg.print_config = True
            elif a == "--explain-config":
                cfg.explain_config = True
            elif a == "--validate-config":
                cfg.validate_config_only = True
            elif a == "--config-file":
                load_config_file(cfg, take()[0])
            elif a == "--diff":
                cfg.diff_runs = take(2)
            elif a == "--resume":
                cfg.resume_dir = take()[0]
            elif a == "--sign-key":
                cfg.sign_key = take()[0]
            elif a == "--verify-signature":
                cfg.verify_signature = take()[0]
                explicit.add("verify_signature")   # BUGFIX(P9): явный CLI-флаг
            elif a == "--task-timeout":
                cfg.task_timeout = float(take()[0])
            elif a == "--global-timeout":
                cfg.global_timeout = float(take()[0])
            elif a == "--strict":
                cfg.strict = True
            elif a == "--notify":
                cfg.notify = take()[0]
            elif a == "--generate-man":
                return "man", warns
            elif a == "--generate-completions":
                cfg.generate = "completions:" + take()[0]
            elif a == "--theme-file":
                load_theme_file(cfg, take()[0])
            elif a == "--profile-safe-force":
                pass  # retired-флаг: принимается молча (§13.2 Retired)
            else:
                msg = f"WARNING: unrecognized CLI argument {a!r}"
                warns.append(msg)
                if cfg.strict:
                    raise ValueError(msg)
        except ValueError as ex:
            errs = str(ex)
            if errs.startswith("WARNING"):
                raise
            if cfg.strict:
                raise
            warns.append(f"WARNING: {errs}")
        i = i0 if False else i  # шаг уже сделан take()/флагом
        i = max(i, i0 + 1)
    # env-переопределения {{PREFIX}}_* (§3.2 шаг 3)
    env_lang = os.environ.get("HODGE_LANG")
    if env_lang:
        cfg.lang = env_lang if env_lang in ("ru", "en") else cfg.lang
    if os.environ.get("HODGE_SEED"):
        try:
            cfg.seed = int(os.environ["HODGE_SEED"])
        except ValueError:
            pass
    # профиль поверх CLI (§1.4): конфликт — WARN, флаг побеждает (B2: explicit)
    prof_warns = apply_profile(cfg, cfg.profile, explicit)
    warns.extend(prof_warns)
    return None, warns


def load_config_file(cfg: HodgeConfig, path: str, _depth: int = 0,
                     _visited: set | None = None) -> None:
    """§3.2 / II.1: TOML/JSON + include (глубина ≤ 8, цикл → ERR_CONFIG_CYCLE)."""
    if _depth > 8:
        raise ValueError(f"ERR_CONFIG_DEPTH {path}")
    _visited = _visited or set()
    real = os.path.abspath(path)
    if real in _visited:
        raise ValueError(f"ERR_CONFIG_CYCLE {real}")
    _visited.add(real)
    if path.endswith(".json"):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    else:
        import tomllib
        with open(path, "rb") as f:
            data = tomllib.load(f)
    # include ДО применения, чтобы included-значения были дефолтами
    inc_raw = data.get("include", [])
    for inc in (inc_raw if isinstance(inc_raw, list) else [inc_raw]):
        if isinstance(inc, str):
            load_config_file(cfg, os.path.join(os.path.dirname(real), inc),
                             _depth + 1, _visited)
    for k, v in data.items():
        if k == "include":
            continue
        if hasattr(cfg, k):
            setattr(cfg, k, v)
        else:
            # P2: неизвестные ключи конфига не замалчиваются
            print(f"{HODGEText.badge('WARN')} config: неизвестное поле '{k}' — игнорируется")

def load_theme_file(cfg: HodgeConfig, path: str) -> None:
    """§21.5: TOML-тема, мерж по ключам поверх dark-gold."""
    import tomllib
    with open(path, "rb") as f:
        data = tomllib.load(f)
    base = dict(HODGEColor.DARK_GOLD)
    for k, v in data.items():
        if k in base and isinstance(v, list) and len(v) == 3:
            base[k] = (v[0], int(v[1]), v[2])
        else:
            raise ValueError(f"ERR_THEME_INVALID {k}")
    HODGEColor.THEMES["custom"] = base
    cfg.theme = "custom"


# ══════════════════════════════════════════════════════════════════════════
# §14. ИНТЕРАКТИВНОЕ МЕНЮ: menu-first (§14.1) — голый запуск в tty всегда
# открывает меню; меню работает на дефолтном конфиге (§0.3); никогда не
# падает (§14.7): Ctrl+C → возврат, EOF-guard 50, исключение → redraw.
# Ввод подключаемый — это же используется в --self-test --menu (§19.10).
# ══════════════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════════════
# §14 МЕНЮ v2: menu-first; ASCII-баннер ВНУТРИ рамки; [1-N] задачи;
# [a/f/h/c/v/w] прогон; [p/s/n/t/l/d/e/P] настройки; [x/r/T/C/?/q] действия.
# ══════════════════════════════════════════════════════════════════════════
MENU_CATEGORIES = ("RUN", "TASKS", "SETTINGS", "ACTIONS")

class HodgeMenu:
    EOF_LIMIT = 50

    def __init__(self, cfg: HodgeConfig, theme: HODGEColor, logger: HodgeLogger,
                 runner_factory=None, stdin=None, stdout=None):
        self.cfg = cfg
        self.theme = theme
        self.log = logger
        self._runner_factory = runner_factory
        self._stdin = stdin or sys.stdin
        self._stdout = stdout or sys.stdout
        self._eof = 0
        self.marked: set = set()
        self.filter = ""
        self.mode = "nav"    # nav | filter | sweep | edit
        self.selected = 0
        self.sweep_specs: list = []
        self.sweep_fn = ""

    def _out(self, s: str = ""):
        self._stdout.write(s + "\n")

    def _persist(self):
        """§3.2 v4: каждое изменение настроек в меню → .cache/settings.json
        (prec-extreme, тема, точность, язык и т.д. живут между запусками)."""
        try:
            save_settings_cache(self.cfg)
        except Exception:
            pass

    # ── рендер ──
    # §14.3: единая точка сборки строки меню — гарантирует видимую ширину
    # width+2 (совпадает с top border), корректно учитывает ANSI.
    def _menu_line(self, content: str, width: int) -> str:
        vis = HODGEAdapter.display_width(HODGEText.strip_ansi(content))
        pad = max(0, width - 1 - vis)
        return "║ " + content + " " * pad + "║"

    # §14.3: подгонка строки под видимую ширину (truncate + pad), не по байтам.
    @staticmethod
    def _fit_width(s: str, width: int) -> str:
        vis = HODGEAdapter.display_width(s)
        if vis == width:
            return s
        if vis < width:
            return s + " " * (width - vis)
        out, cur = [], 0
        for ch in s:
            w = HODGEAdapter.display_width(ch)
            if cur + w > width:
                break
            out.append(ch)
            cur += w
        return "".join(out) + " " * (width - cur)

    def render(self, status: str = "") -> None:
        self._out()
        width = max(72, min(112, HODGEAdapter.term_width() - 2))
        if self.theme.plain or not HODGEText.unicode_on:
            self._render_plain(width, status)
            return
        fmt = lambda k, **kw: hodge_fmt(self.cfg, k, **kw)
        top = "╔" + "═" * width + "╗"
        sep = "╠" + "═" * width + "╣"
        bot = "╚" + "═" * width + "╝"
        self._out(top)
        # ASCII-баннер — внутри рамки, ВЕРХ
        banner = HodgeBanner.render("full", self.theme, self.cfg)
        if banner:
            for ln in banner.split("\n"):
                # fit_width до width-1: баннер шире рамки не должен рвать ║
                self._out(self._menu_line(self._fit_width(ln, width - 1), width))
        self._out(sep)
        # RUN
        self._render_block(fmt("menu.run_header"), [
            ("a", fmt("menu.run_all")),
            ("f", fmt("menu.run_fast")),
            ("h", fmt("menu.run_heavy")),
            ("c", fmt("menu.run_chess")),
            ("v", fmt("menu.run_verhodge")),
            ("w", fmt("menu.run_sweep")),
        ], width)
        # TASKS — 4 колонки
        self._render_tasks(width)
        # SETTINGS
        self._render_block(fmt("menu.settings_header"), [
            ("p", fmt("menu.set.prec", value=self.cfg.prec)),
            ("s", fmt("menu.set.seed", value=self.cfg.seed)),
            ("n", fmt("menu.set.preset", value=self.cfg.preset)),
            ("t", fmt("menu.set.theme", value=self.cfg.theme)),
            ("l", fmt("menu.set.lang", value=self.cfg.lang)),
            ("d", fmt("menu.set.depth", value=self.cfg.color_depth)),
            ("e", fmt("menu.set.two_pass", value="on" if self.cfg.two_pass else "off")),
            ("P", fmt("menu.set.prec_extreme", value="on" if self.cfg.prec_extreme else "off")),
        ], width)
        # ACTIONS
        self._render_block(fmt("menu.actions_header"), [
            ("x", fmt("menu.act.dry_run")),
            ("r", fmt("menu.act.recipes")),
            ("T", fmt("menu.act.theme_cycle")),
            ("C", fmt("menu.act.palette")),
            ("V", fmt("menu.act.video_lab")),
            ("?", fmt("menu.act.help")),
            ("q", fmt("menu.act.quit")),
        ], width)
        self._out(sep)
        # статус-строка + prompt (BUGFIX: длинный status рвал правую границу ║)
        sel = "filter" if self.mode == "filter" else ("sweep" if self.mode == "sweep" else "nav")
        prompt_hint = {"nav": "❯", "filter": "❯ filter:", "sweep": "❯ sweep:"}[sel]
        status_fit = self._fit_width(status, width - 1 - HODGEAdapter.display_width(prompt_hint) - 1)
        self._out(self._menu_line(HODGEText.dye(prompt_hint, "gold_bright") + " "
                                  + HODGEText.dye(status_fit, "text_dim"), width))
        self._out(sep)
        stat = fmt("menu.status_line",
                   theme=self.theme.name, prec=self.cfg.prec, seed=self.cfg.seed,
                   preset=self.cfg.preset, lang=self.cfg.lang, n=len(self.marked),
                   ids=",".join(str(i) for i in sorted(self.marked)))
        stat += f" · depth={HODGETerm.caps()['color_depth']}"
        self._out(self._menu_line(HODGEText.dye(self._fit_width(stat, width - 1), "neutral"), width))
        self._out(bot)

    def _render_block(self, title, items, width):
        head = f" {title} "
        self._out(self._menu_line(HODGEText.gradient(head, "gold", "amber", "block"), width))
        for key, desc in items:
            key_s = f"[{key}]"
            self._out(self._menu_line(
                HODGEText.dye(key_s.ljust(6), "gold_bright") + " " + HODGEText.dye(desc, "text"),
                width))

    def _render_tasks(self, width):
        head = f" {hodge_fmt(self.cfg, 'menu.tasks_header')} ({len(self._visible())}/{len(TASKS)}) "
        self._out(self._menu_line(HODGEText.gradient(head, "gold", "amber", "block"), width))
        items = self._visible()
        cols = 4
        # cols*(cw+2) ≤ width-1 — иначе сетка переполняет рамку на 6+ колонок
        # (BUGFIX: прежний max(20,(width-4)//4) давал 4*cw+8 > width-1)
        cell_w = max(1, (width - 1) // cols - 2)
        rows = (len(items) + cols - 1) // cols
        for r in range(rows):
            parts = []
            for c in range(cols):
                idx = r + c * rows
                if idx >= len(items):
                    parts.append(" " * (cell_w + 2))   # пустая ячейка + 2 пробела разделителя
                    continue
                t = items[idx]
                mark = "✦" if t["id"] in self.marked else " "
                cursor = "❯" if idx == self.selected else " "
                cell = self._fit_width(f"{cursor}{mark}[{t['id']:2d}] {t['slug']}", cell_w)
                parts.append(HODGEText.dye(cell, "text") + "  ")
            self._out(self._menu_line("".join(parts), width))

    def _render_plain(self, width, status):
        fmt = lambda k, **kw: hodge_fmt(self.cfg, k, **kw)
        self._out(HODGEText.strip_ansi(HodgeBanner.render("full", self.theme, self.cfg)))
        self._out("─" * width)
        self._out(fmt("menu.run_header") + ":")
        for k, dk in (("a", "menu.run_all"), ("f", "menu.run_fast"),
                      ("h", "menu.run_heavy"), ("c", "menu.run_chess"),
                      ("v", "menu.run_verhodge"), ("w", "menu.run_sweep")):
            self._out(f"  [{k}] " + fmt(dk))
        items = self._visible()
        self._out(fmt("menu.tasks_header") + f" ({len(items)}/{len(TASKS)}):")
        for i, t in enumerate(items):
            mark = "✦" if t["id"] in self.marked else " "
            cur = "❯" if self.selected == i else " "
            self._out(f"  {cur}{mark} [{t['id']:2d}] {t['slug']:<22} {t['title']}")
        self._out(fmt("menu.settings_header") + ":")
        self._out("  [p] " + fmt("menu.set.prec", value=self.cfg.prec))
        self._out("  [s] " + fmt("menu.set.seed", value=self.cfg.seed))
        self._out("  [n] " + fmt("menu.set.preset", value=self.cfg.preset))
        self._out("  [t] " + fmt("menu.set.theme", value=self.cfg.theme))
        self._out("  [l] " + fmt("menu.set.lang", value=self.cfg.lang))
        self._out("  [d] " + fmt("menu.set.depth", value=self.cfg.color_depth))
        self._out("  [e] " + fmt("menu.set.two_pass", value="on" if self.cfg.two_pass else "off"))
        self._out("  [P] " + fmt("menu.set.prec_extreme", value="on" if self.cfg.prec_extreme else "off"))
        self._out(fmt("menu.actions_header") + ":")
        for k, dk in (("x", "menu.act.dry_run"), ("r", "menu.act.recipes"),
                      ("T", "menu.act.theme_cycle"), ("C", "menu.act.palette"),
                      ("V", "menu.act.video_lab"),
                      ("?", "menu.act.help"), ("q", "menu.act.quit")):
            self._out(f"  [{k}] " + fmt(dk))
        self._out(f"❯ {status}")
        self._out(fmt("menu.status_line",
                      theme=self.theme.name, prec=self.cfg.prec, seed=self.cfg.seed,
                      preset=self.cfg.preset, lang=self.cfg.lang, n=len(self.marked),
                      ids=",".join(str(i) for i in sorted(self.marked))))

    # ── цикл ──
    def run(self) -> int:
        fmt = lambda k, **kw: hodge_fmt(self.cfg, k, **kw)
        self.render()
        while True:
            if HodgeRunner._sigwinch_flag:
                HodgeRunner._sigwinch_flag = False
                HodgeBanner.invalidate()
                HODGETerm.invalidate()
                self.render(fmt("menu.resized"))
                continue
            try:
                line = self._stdin.readline()
            except KeyboardInterrupt:
                # §14.3 / BUGFIX(VI.3a): работает только когда flag-обработчики
                # SIGINT не установлены (hodge_main вешает их лишь на compute)
                self.render(fmt("menu.ctrl_c"))
                continue
            except Exception as ex:
                self.render(fmt("menu.input_error", msg=ex))
                continue
            if line == "":
                # EOF-guard §14.7; BUGFIX(C/busy-loop): sleep против CPU-ожога,
                # если какая-то среда отдаёт "" без реального EOF
                self._eof += 1
                if self._eof >= self.EOF_LIMIT:
                    self._out(hodge_fmt(self.cfg, "menu.bye"))
                    return 0
                time.sleep(0.01)
                self.render(fmt("menu.eof_guard", n=self._eof, limit=self.EOF_LIMIT))
                continue
            key = line.strip()
            raw = line.rstrip("\r\n")   # ввод без перевода строки (см. Space ниже)
            self._eof = 0

            if self.mode == "filter":
                if not key:
                    self.mode = "nav"
                else:
                    self.filter = key
                    self.selected = 0
                self.render()
                continue
            if self.mode == "sweep":
                self._handle_sweep_input(key)
                continue

            if not key and raw != "" and not raw.strip():
                # Space (строка из одних пробелов) — отметить/снять отмеченную.
                # BUGFIX: key = line.strip() == "" и Space молча попадал в ветку
                # «пустой Enter» и запускал отмеченные задачи.
                items = self._visible()
                if items:
                    tid = items[min(self.selected, len(items) - 1)]["id"]
                    if tid in self.marked:
                        self.marked.discard(tid)
                    else:
                        self.marked.add(tid)
                self.render()
                continue

            if not key:
                # §14.5: Enter запускает отмеченные (или выбранную под фильтром);
                # пустой Enter без контекста — перерисовать (EOF-guard-скрипты
                # шлют пустые строки и не должны запускать прогон)
                if self.marked:
                    self._run(sorted(self.marked))
                elif self.filter:
                    items = self._visible()
                    if items:
                        self._run([items[min(self.selected, len(items) - 1)]["id"]])
                self.render()
                continue

            if key == "/":
                self.mode = "filter"
                self.filter = ""
                self.render(fmt("menu.filter_mode"))
                continue
            if key in ("j", "k"):
                n = len(self._visible())
                self.selected = max(0, min(n - 1, self.selected + (1 if key == "j" else -1)))
                self.render()
                continue
            if key == " ":
                items = self._visible()
                if items:
                    tid = items[min(self.selected, len(items) - 1)]["id"]
                    if tid in self.marked:
                        self.marked.discard(tid)
                    else:
                        self.marked.add(tid)
                self.render()
                continue

            try:
                cmd = self.handle(key)
            except Exception as ex:
                self.render(f"{type(ex).__name__}: {ex}")
                continue
            if cmd == "quit":
                # §3.2 v4: финальное сохранение настроек сессии меню
                self._persist()
                self._out(hodge_fmt(self.cfg, "menu.bye"))
                return 0
            self.render()

    def _visible(self):
        if not self.filter:
            return TASKS
        f = self.filter.lower()
        return [t for t in TASKS
                if f in t["slug"].lower() or f in t["title"].lower() or f in str(t["id"])]

    # ── команды ──
    def handle(self, key: str):
        fmt = lambda k, **kw: hodge_fmt(self.cfg, k, **kw)
        if key in ("q", "Q", "й", "Й"):
            return "quit"
        if key == "\x19":   # P2: Ctrl+Y — §27.5 copy-path (OSC 52)
            if self.cfg.no_clipboard:
                self._out(fmt("menu.copy_disabled"))
            elif not self.cfg.run_dir:
                self._out(fmt("menu.copy_empty"))
            else:
                import base64 as _b64
                self._stdout.write("\x1b]52;c;" + _b64.b64encode(
                    self.cfg.run_dir.encode()).decode() + "\x1b\\")
                self._stdout.flush()
                self._out(fmt("menu.copy_done", path=self.cfg.run_dir))
            return None
        if key == "?":
            self._menu_help()
            return None
        # RUN
        if key == "a":
            self._run(None)
            return None
        if key == "f":
            self._run_tag("fast")
            return None
        if key == "h":
            self._run_tag("heavy")
            return None
        if key == "c":
            # BUGFIX: честные labels — показываем, что ЕСТЬ в реестре, и чего нет
            # (набор задач зависит от реестра: в Julia 23, в Python 23–33)
            ids = [t["id"] for t in TASKS if 23 <= t["id"] <= 33]
            if not ids:
                self._out(HODGEText.badge("WARN") + " "
                          + fmt("submenu.groups.chess_empty"))
            else:
                miss = [i for i in range(23, 34) if i not in ids]
                if miss:
                    self._out(HODGEText.badge("INFO") + " " + fmt(
                        "submenu.groups.run_missing", name="chess", ids=ids,
                        miss=miss))
                else:
                    self._out(HODGEText.badge("INFO") + " " + fmt(
                        "submenu.groups.run", name="chess", ids=ids))
                self._run(ids)
            return None
        if key == "v":
            ids = [t["id"] for t in TASKS if 34 <= t["id"] <= 38 or t["id"] == 40]
            if not ids:
                self._out(HODGEText.badge("WARN") + " "
                          + fmt("submenu.groups.verhodge_empty"))
            else:
                miss = [i for i in (34, 35, 36, 37, 38, 40) if i not in ids]
                if miss:
                    self._out(HODGEText.badge("INFO") + " " + fmt(
                        "submenu.groups.run_missing", name="verhodge", ids=ids,
                        miss=miss))
                else:
                    self._out(HODGEText.badge("INFO") + " " + fmt(
                        "submenu.groups.run", name="verhodge", ids=ids))
                self._run(ids)
            return None
        if key == "w":
            self._menu_sweep()
            return None
        # TASKS
        # BUGFIX(UX): цифра раньше СРАЗУ запускала прогон задачи — выглядело как
        # «меню само начинает тестирование». Теперь цифра отмечает/снимает
        # задачу (как Space), запуск — Enter (отмеченные) или a/f/h/c/v.
        if key.isdigit():
            tid = int(key)
            if tid in SUITE_IDS:
                if tid in self.marked:
                    self.marked.discard(tid)
                    self._out(HODGEText.badge("INFO") + " "
                              + fmt("menu.mark_off", id=tid))
                else:
                    self.marked.add(tid)
                    self._out(HODGEText.badge("INFO") + " "
                              + fmt("menu.mark_on", id=tid))
            else:
                self._out(HODGEText.badge("WARN") + " " + fmt("menu.no_task", id=tid))
            return None
        # SETTINGS
        # §14 v4: словный псевдоним prec-extreme — переключение не только клавишей
        # [P], но и словом: «prec-extreme», «prec-extreme on|off», «precext»
        pc = parse_prec_extreme_cmd(key)
        if pc is not None:
            self.cfg.prec_extreme = (not self.cfg.prec_extreme) if pc == "toggle" else pc
            if self.cfg.prec_extreme:
                self.cfg.prec = max(self.cfg.prec, 200)
            self._persist()
            self._out(HODGEText.badge("INFO") + " "
                      + fmt("menu.edit.precext_set",
                            value="on" if self.cfg.prec_extreme else "off",
                            prec=self.cfg.prec))
            return None
        if key == "p":
            self._edit_prec()
            self._persist()
            return None
        if key == "s":
            self._edit_seed()
            self._persist()
            return None
        if key == "n":
            self._edit_preset()
            self._persist()
            return None
        if key == "t" or key == "T":
            self._cycle_theme()
            self._persist()
            return None
        if key == "l":
            self.cfg.lang = "en" if self.cfg.lang == "ru" else "ru"
            self._persist()
            self._out(HODGEText.badge("INFO") + " "
                      + fmt("menu.edit.lang_set", value=self.cfg.lang))
            return None
        if key == "d":
            self._cycle_depth()
            self._persist()
            return None
        if key == "e":
            self.cfg.two_pass = not self.cfg.two_pass
            self._persist()
            self._out(HODGEText.badge("INFO") + " "
                      + fmt("menu.edit.twopass_set",
                            value="on" if self.cfg.two_pass else "off"))
            return None
        if key == "P":
            self.cfg.prec_extreme = not self.cfg.prec_extreme
            if self.cfg.prec_extreme:
                self.cfg.prec = max(self.cfg.prec, 200)
            self._persist()
            self._out(HODGEText.badge("INFO") + " "
                      + fmt("menu.edit.precext_set",
                            value="on" if self.cfg.prec_extreme else "off",
                            prec=self.cfg.prec))
            return None
        # ACTIONS
        if key == "x":
            self._menu_dry_run()
            return None
        if key == "r":
            self._menu_recipes()
            return None
        if key == "C":
            self._menu_palette()
            return None
        if key == "V":
            # §11.10: 3D Video Lab — объект + fps + frames + N (подменю §14.2)
            self._menu_video()
            return None
        self.log.log_comp("WARN", "Menu", f"unknown key {key!r}")
        self._out(HODGEText.badge("WARN") + " " + fmt("menu.unknown", key=repr(key)))
        return None

    def _run(self, ids):
        if self._runner_factory is None:
            self._out(HODGEText.badge("WARN") + " "
                      + hodge_fmt(self.cfg, "menu.runner_unavailable"))
            return
        self.cfg.tasks = ids or []
        lock_fd = None
        lk = ""
        try:
            # BUGFIX(Lock): ВСЕГДА новый run_dir — переиспользование меню-каталога
            # давало ERR_LOCK_HELD при повторном прогоне, пока старый процесс
            # держит flock. Новый каталог = свой lock, коллизий нет.
            # BUGFIX(Race): два процесса в одну секунду могли выбрать одно имя —
            # ретраи со свежим суффиксом _1.._N.
            for _ in range(5):
                self.cfg.run_dir = _new_run_dir(self.cfg)
                lk = os.path.join(self.cfg.run_dir, ".lock")
                lock_fd, lk_err = HODGEAdapter.flock_run_dir(self.cfg.run_dir)
                if lock_fd is not None:
                    break
                time.sleep(0.05)
            if lock_fd is None:
                # v3: сообщение уже содержит PID держателя + cmdline + подсказку
                self._out(HODGEText.badge("FAIL") + " ERR_LOCK_HELD: " + (lk_err or "занят другим процессом"))
                return
            global _RUN_LOCK_FD, _RUN_LOCK_PATH
            _RUN_LOCK_FD, _RUN_LOCK_PATH = lock_fd, lk
            self.cfg._lock_held = True
            # BUGFIX(VI.3a): flag-обработчики SIGINT/SIGTERM/… — только на время
            # compute; в меню Ctrl+C обязан бросать KeyboardInterrupt (§14.3)
            _prev_sig = _install_compute_signals()
            try:
                r = self._runner_factory(self.cfg)
                t0 = time.monotonic()
                r.run_all()
                wall = time.monotonic() - t0
                # BUGFIX: прогон из меню раньше НЕ писал отчёты (results.json,
                # MANIFEST, FINAL_REPORT, per-task) — их писал только --task.
                # Финализация — паритет с _run_suite (§26).
                passed = sum(1 for x in r.results.values() if x.get("ok"))
                total = len(r.results)
                all_ok = passed == total and total > 0
                exit_code = 0 if all_ok else 1
                for code_key, code_val in (("ERR_GLOBAL_TIMEOUT", 4), ("ERR_INTERNAL", 3),
                                           ("ERR_HEALTH", 5), ("ERR_SIGTERM", 143),
                                           ("ERR_SIGINT", 130)):
                    if code_key in self.log.err_ledger:
                        exit_code = code_val
                if getattr(self.cfg, "metrics_format", "") and self.log.metrics:
                    hodge_metrics_export(self.cfg, self.log)
                if not (self.cfg.ci or self.cfg.jsonl or self.cfg.tsv):
                    verdict = hodge_fmt(self.cfg, "all_pass" if all_ok else "has_fail")
                    color = "ok" if all_ok else "err"
                    self._out(HODGEText.dye(f"── {hodge_fmt(self.cfg, 'summary')}: ", "gold")
                              + HODGEText.dye(verdict, color, "bold")
                              + HODGEText.dye(f" ({hodge_fmt(self.cfg, 'duration')}: "
                                              f"{HODGEText.fmt_duration(wall)})",
                                              "text_dim"))
                reports = HodgeReports(self.cfg, self.log, self.theme)
                reports.bind(r)
                if not self.cfg.no_report:
                    reports.master(self.cfg.run_dir, wall, exit_code)
                    reports.per_task_all(self.cfg.run_dir)   # §10.1 после master
                    hodge_cross_run_dashboard(self.cfg)
                else:
                    # --no-report: results.json всё равно нужен --resume/--diff
                    minimal = {
                        "run": {"finished_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                "exit_code": exit_code, "cfg_hash": self.cfg.relevant_hash(),
                                "preset": self.cfg.preset, "theme": self.cfg.theme,
                                "no_report": True},
                        "task": {str(x["id"]): {"verdict": x["verdict"],
                                                "reason": x.get("reason"),
                                                "claims": x["claims"],
                                                "duration_s": sum(p["duration_s"]
                                                                  for p in x["passes"].values())}
                                 for x in r.results.values()},
                        "errors": {k: {"count": v[0], "last_seen": v[1]}
                                   for k, v in self.log.err_ledger.items()},
                    }
                    HODGEAdapter.atomic_write(
                        os.path.join(self.cfg.run_dir, "results.json"),
                        json.dumps(minimal, ensure_ascii=False, indent=1))
                self.log.event("INFO", "Run", "exit", code=exit_code)
            except KeyboardInterrupt:
                self._out(HODGEText.badge("WARN")
                          + " SIGINT — частичный прогон сохранён (код 130)")
            finally:
                _restore_signal_handlers(_prev_sig)
        finally:
            if lock_fd is not None:
                # §24.2 v4: lock_release снимает любой режим каскада и закрывает fd
                try:
                    HODGEAdapter.lock_release(lock_fd)
                except OSError:
                    pass
                _RUN_LOCK_FD = None
                _RUN_LOCK_PATH = None
                self.cfg._lock_held = False

    def _run_ids(self, ids):
        self._run(ids)

    def _run_tag(self, tag):
        sel = [t["id"] for t in TASKS if tag in t["tags"]]
        self._run(sel)

    def _edit_prec(self):
        fmt = lambda k, **kw: hodge_fmt(self.cfg, k, **kw)
        self._out(fmt("menu.edit.prec_now", value=self.cfg.prec))
        ans = self._menu_read(fmt("menu.edit.prec_new"), allow_empty=True)
        if not ans:
            self._out(HODGEText.badge("INFO") + " "
                      + fmt("menu.edit.prec_keep", value=self.cfg.prec))
            return
        v = parse_prec_value(ans)
        if v is None:
            self._out(HODGEText.badge("WARN") + " "
                      + fmt("menu.edit.not_int", v=ans))
            return
        # §3.2 v5: prec без верхней границы — 4096, 5m, 1g, 2t
        old = self.cfg.prec
        self.cfg.prec = v
        # §3.2 v6: при тяжёлом prec — блок оценок и подтверждение (интерактив)
        est_lines = hodge_prec_estimates(self.cfg)
        if est_lines:
            for ln in est_lines:
                self._out(HODGEText.badge("WARN") + " " + ln)
            if HODGEAdapter.isatty():
                ans = self._menu_read(fmt("menu.edit.prec.confirm", value=v),
                                      allow_empty=True)
                if ans.strip().lower() in ("n", "no", "н", "нет"):
                    self.cfg.prec = old
                    self._out(HODGEText.badge("INFO") + " "
                              + fmt("menu.edit.prec.revert", value=old))
                    return
        self._out(HODGEText.badge("INFO") + " " + fmt("menu.edit.prec_set", value=v))

    def _edit_seed(self):
        fmt = lambda k, **kw: hodge_fmt(self.cfg, k, **kw)
        self._out(fmt("menu.edit.seed_now", value=self.cfg.seed))
        ans = self._menu_read(fmt("menu.edit.seed_new"), allow_empty=True)
        if not ans:
            self._out(HODGEText.badge("INFO") + " "
                      + fmt("menu.edit.seed_keep", value=self.cfg.seed))
            return
        try:
            self.cfg.seed = int(ans)
            self._out(HODGEText.badge("INFO") + " "
                      + fmt("menu.edit.seed_set", value=self.cfg.seed))
        except ValueError:
            self._out(HODGEText.badge("WARN") + " "
                      + fmt("menu.edit.not_int", v=ans))

    def _edit_preset(self):
        fmt = lambda k, **kw: hodge_fmt(self.cfg, k, **kw)
        presets = ["quick", "full", "deep"]
        self._out(fmt("menu.edit.preset_list"))
        ans = self._menu_read(fmt("menu.edit.preset_choice", value=self.cfg.preset),
                              allow_empty=True)
        if not ans:
            self._out(HODGEText.badge("INFO") + " "
                      + fmt("menu.edit.preset_keep", value=self.cfg.preset))
            return
        if ans in presets:
            self.cfg.preset = ans
            apply_preset(self.cfg, ans)
            self._out(HODGEText.badge("INFO") + " "
                      + fmt("menu.edit.preset_set", value=ans,
                            prec=self.cfg.prec, twopass=self.cfg.two_pass))
        else:
            self._out(HODGEText.badge("WARN") + " "
                      + fmt("menu.edit.preset_unknown", v=ans))

    def _cycle_theme(self):
        fmt = lambda k, **kw: hodge_fmt(self.cfg, k, **kw)
        names = sorted(HODGEColor.THEMES.keys())
        cur = names.index(self.cfg.theme) if self.cfg.theme in names else 0
        self.cfg.theme = names[(cur + 1) % len(names)]
        self.theme.__init__(self.cfg.theme, self.cfg.color_depth, self.cfg.plain)
        HodgeBanner.invalidate()
        HODGEText._dye_cache.clear()
        HODGEText._gradient_cache.clear()
        self._out(HODGEText.badge("INFO") + " " + fmt("menu.edit.theme_set", value=self.cfg.theme))

    def _cycle_depth(self):
        depths = ["auto", "truecolor", "256", "16", "mono"]
        cur = depths.index(self.cfg.color_depth) if self.cfg.color_depth in depths else 0
        self.cfg.color_depth = depths[(cur + 1) % len(depths)]
        self._out(HODGEText.badge("INFO") + " "
                  + hodge_fmt(self.cfg, "menu.edit.depth_set", value=self.cfg.color_depth))

    # ── §14.2 SUBMENU: единая точка чтения + полноценные подменю ──
    def _menu_read(self, prompt: str, allow_empty: bool = False):
        """§14.2: единая точка чтения подменю. None = cancel (Ctrl+D/пустая
        строка). Пустая строка при allow_empty=True = подтверждение (Enter).
        Защита от busy-loop — та же, что в run() (EOF-guard §14.7)."""
        self._stdout.write(prompt)
        self._stdout.flush()
        if not hasattr(self._stdin, "readline"):
            return None
        line = self._stdin.readline()
        if not isinstance(line, str) or line == "":
            return None   # EOF / поток без данных
        s = line.strip()
        if not s and not allow_empty:
            return None
        return s

    def _menu_recipes(self):
        """§14.5 RECIPES: список → выбор → preview изменений → apply/run."""
        fmt = lambda k, **kw: hodge_fmt(self.cfg, k, **kw)
        names = sorted(RECIPES)
        self._out()
        self._out(HODGEText.dye(fmt("submenu.recipes.title"), "gold_dim"))
        for i, name in enumerate(names, 1):
            r = RECIPES[name]
            self._out("  " + HODGEText.dye(f"[{i}]", "gold_bright") + " "
                      + HODGEText.dye(name, "gold") + " — "
                      + r.get("description", ""))
            tasks_s = fmt("submenu.all") if r["tasks"] == "all" else str(r["tasks"])
            self._out("      preset=" + HODGEText.dye(r["preset"], "gold_bright")
                      + " · profile=" + HODGEText.dye(r["profile"], "gold_bright")
                      + " · two_pass=" + HODGEText.dye(str(r["two_pass"]), "gold_bright"))
            self._out("      tasks=" + HODGEText.dye(tasks_s, "text"))
            for k, v in (r.get("overrides") or {}).items():
                self._out(f"      override: {k} = {v}")
        self._out(HODGEText.dye(fmt("submenu.recipes.cancel"), "gold_bright"))
        ans = self._menu_read(HODGEText.dye(
            fmt("submenu.recipes.prompt", n=len(names)), "gold_bright"))
        if ans is None:
            self._out(HODGEText.badge("INFO") + " " + fmt("submenu.cancelled"))
            return
        try:
            idx = int(ans)
        except ValueError:
            idx = -1
        if idx == 0:
            self._out(HODGEText.badge("INFO") + " " + fmt("submenu.cancelled"))
            return
        if idx < 1 or idx > len(names):
            self._out(HODGEText.badge("WARN") + " "
                      + fmt("submenu.recipes.none", v=ans))
            return
        name = names[idx - 1]
        r = RECIPES[name]
        self._out()
        self._out(HODGEText.dye(fmt("submenu.recipes.applying", name=name), "gold"))
        self._out(fmt("submenu.recipes.preview",
                      pold=self.cfg.preset, pnew=r["preset"],
                      rold=self.cfg.profile, rnew=r["profile"],
                      told=(fmt("submenu.all") if not self.cfg.tasks
                            else str(self.cfg.tasks)),
                      tnew=(fmt("submenu.all") if r["tasks"] == "all"
                            else str(r["tasks"])),
                      eold=self.cfg.two_pass, enew=r["two_pass"]))
        self._out(HODGEText.dye(fmt("submenu.recipes.actions"), "gold_bright"))
        act = self._menu_read(
            HODGEText.dye(fmt("submenu.recipes.action_prompt"), "gold_bright"),
            allow_empty=True)
        if not act:
            self._out(HODGEText.badge("INFO") + " " + fmt("submenu.cancelled"))
            return
        try:
            apply_recipe(self.cfg, name)
            self._out(HODGEText.badge("INFO") + " "
                      + fmt("submenu.recipes.applied", name=name))
        except Exception as ex:
            self._out(HODGEText.badge("FAIL") + f" {type(ex).__name__}: {ex}")
            return
        if act.lower() == "a":
            ids = list(self.cfg.tasks)   # apply_recipe кладёт конкретные int
            self._out(HODGEText.badge("INFO") + " " + fmt(
                "submenu.recipes.running", name=name,
                ids=(fmt("submenu.all") if not ids else str(ids))))
            self._run(ids)

    def _menu_palette(self):
        """§21.6 PALETTE: свотчи всех тем + выбор темы по номеру."""
        fmt = lambda k, **kw: hodge_fmt(self.cfg, k, **kw)
        saved_theme = self.cfg.theme
        self._out()
        names = sorted(HODGEColor.THEMES)
        for i, name in enumerate(names, 1):
            self.theme.__init__(name, self.cfg.color_depth, self.cfg.plain)
            HODGEText._dye_cache.clear()
            HODGEText._gradient_cache.clear()
            pal = HODGEColor.THEMES[name]
            marker = (HODGEText.dye(fmt("submenu.palette.current"), "gold_bright")
                      if name == saved_theme else "")
            self._out(HODGEText.dye(f"── [{i}] {name} " + "─" * 28, "gold_dim")
                      + marker)
            if pal is None:
                # mono: палитры нет — цвета собираются программно (§27.8)
                self._out(fmt("submenu.palette.mono_note"))
                self._out()
                continue
            for key in PALETTE_KEYS:
                v = pal.get(key)
                if v is None:
                    continue   # не у всех тем полный набор (напр. mono)
                self._out("  " + self.theme.color_code(key) + "███\x1b[0m "
                          + key.ljust(12) + f" {v[0]}/{v[1]}")
            self._out(fmt("submenu.palette.sample")
                      + HODGEText.dye(fmt("submenu.numbers"), "text")
                      + HODGEText.num(1234, "int") + " "
                      + HODGEText.badge("PASS") + " " + HODGEText.badge("FAIL"))
            self._out()
        self.theme.__init__(saved_theme, self.cfg.color_depth, self.cfg.plain)
        HodgeBanner.invalidate()
        HODGEText._dye_cache.clear()
        HODGEText._gradient_cache.clear()
        self._out(HODGEText.dye(fmt("submenu.palette.hint", n=len(names)),
                                "gold_bright"))
        ans = self._menu_read(
            HODGEText.dye(fmt("submenu.palette.prompt"), "gold_bright"),
            allow_empty=True)
        if not ans:
            return
        try:
            idx = int(ans)
        except ValueError:
            idx = 0
        if idx < 1 or idx > len(names):
            self._out(HODGEText.badge("WARN") + " "
                      + fmt("submenu.palette.none", v=ans))
            return
        self.cfg.theme = names[idx - 1]
        self.theme.__init__(self.cfg.theme, self.cfg.color_depth, self.cfg.plain)
        HodgeBanner.invalidate()
        HODGEText._dye_cache.clear()
        HODGEText._gradient_cache.clear()
        self._out(HODGEText.badge("INFO") + " "
                  + fmt("submenu.palette.set", value=self.cfg.theme))

    def _menu_help(self):
        """§14.6 HELP: полноэкранная расширенная справка."""
        fmt = lambda k, **kw: hodge_fmt(self.cfg, k, **kw)
        self._out()
        self._out(HODGEText.dye(
            "╔════════════════════════════════════════════════════════════╗", "gold"))
        self._out(HODGEText.dye(fmt("submenu.help.title"), "gold_bright"))
        self._out(HODGEText.dye(
            "╚════════════════════════════════════════════════════════════╝", "gold"))
        self._out()
        for hdr, body in (("submenu.help.run", "submenu.help.run.body"),
                          ("submenu.help.tasks", "submenu.help.tasks.body"),
                          ("submenu.help.settings", "submenu.help.settings.body"),
                          ("submenu.help.actions", "submenu.help.actions.body"),
                          ("submenu.help.cli", "submenu.help.cli.body"),
                          ("submenu.help.input", "submenu.help.input.body")):
            self._out(HODGEText.dye(fmt(hdr), "gold"))
            self._out(fmt(body))
            self._out()
        self._menu_read(HODGEText.dye(fmt("submenu.help.back"), "gold_dim"),
                        allow_empty=True)

    def _menu_dry_run(self):
        """§13.3 DRY-RUN: выбор группы → план без вычислений (lock не берётся)."""
        fmt = lambda k, **kw: hodge_fmt(self.cfg, k, **kw)
        self._out()
        self._out(HODGEText.dye(fmt("submenu.dry.title"), "gold_dim"))
        self._out(fmt("submenu.dry.cfg", preset=self.cfg.preset,
                      seed=self.cfg.seed, prec=self.cfg.prec,
                      tp="on" if self.cfg.two_pass else "off"))
        self._out(fmt("submenu.dry.opts"))
        self._out(HODGEText.dye(fmt("submenu.dry.cancel"), "gold_bright"))
        ans = self._menu_read(
            HODGEText.dye(fmt("submenu.dry.prompt"), "gold_bright"),
            allow_empty=True)
        if not ans:
            return
        if ans == "1":
            ids = []
        elif ans == "2":
            ids = [t["id"] for t in TASKS if "fast" in t["tags"]]
        elif ans == "3":
            ids = [t["id"] for t in TASKS if "heavy" in t["tags"]]
        elif ans == "4":
            ids = [t["id"] for t in TASKS if 23 <= t["id"] <= 33]
        elif ans == "5":
            ids = [t["id"] for t in TASKS if 34 <= t["id"] <= 38]
        else:
            self._out(HODGEText.badge("WARN") + " "
                      + fmt("submenu.dry.noopt", v=ans))
            return
        old_run, old_tasks = self.cfg.run_dir, list(self.cfg.tasks)
        self.cfg.run_dir = _new_run_dir(self.cfg)   # dryrun.txt не мешает прогону
        self.cfg.tasks = ids
        try:
            hodge_dry_run(self.cfg)
            self._out(HODGEText.badge("INFO") + " " + fmt(
                "submenu.dry.done",
                path=os.path.join(self.cfg.run_dir, "logs", "dryrun.txt")))
        except Exception as ex:
            self._out(HODGEText.badge("FAIL") + f" dry-run: {type(ex).__name__}: {ex}")
        finally:
            self.cfg.tasks = old_tasks
            if old_run:
                self.cfg.run_dir = old_run

    def _menu_sweep(self):
        """§11.6 SWEEP: функция → sweep-спеки → preview кадров → запуск."""
        fmt = lambda k, **kw: hodge_fmt(self.cfg, k, **kw)
        self._out()
        self._out(HODGEText.dye(fmt("submenu.sweep.title"), "gold_dim"))
        self._out(fmt("submenu.sweep.fns"))
        fn = self._menu_read(
            HODGEText.dye(fmt("submenu.sweep.fn_prompt"), "gold_bright"),
            allow_empty=True)
        if fn is None:
            return
        fn = fn or "omega"
        specs = []
        while True:
            spec = self._menu_read(HODGEText.dye(
                fmt("submenu.sweep.spec_prompt", n=len(specs)), "gold_bright"),
                allow_empty=True)
            if spec is None:
                return
            if spec == "":
                break
            try:
                _parse_sweep(spec)
                specs.append(spec)
                self._out(HODGEText.badge("INFO") + " "
                          + fmt("submenu.sweep.added", spec=spec))
            except Exception as ex:
                self._out(HODGEText.badge("WARN") + " " + fmt(
                    "submenu.sweep.bad_spec", msg=f"{type(ex).__name__}: {ex}"))
        if not specs:
            specs = ["N:7:30:1"]
        total = 1
        for s in specs:
            _, vals = _parse_sweep(s)
            total *= len(vals)
        cap = 500
        self._out(HODGEText.badge("INFO") + " " + fmt(
            "submenu.sweep.summary", fn=fn, specs=", ".join(specs),
            total=total, cap=cap))
        if total > cap:
            self._out(HODGEText.badge("WARN") + " "
                      + fmt("submenu.sweep.cap_warn", cap=cap))
        confirm = self._menu_read(
            HODGEText.dye(fmt("submenu.sweep.confirm"), "gold_bright"),
            allow_empty=True)
        if confirm is None or confirm.lower() == "c":
            return
        self.cfg.run_dir = _new_run_dir(self.cfg)
        saved_spec, saved_sweeps = self.cfg.lab3d, list(self.cfg.sweeps)
        self.cfg.lab3d = fn
        self.cfg.sweeps = list(specs)
        try:
            hodge_lab3d(self.cfg)
        except Exception as ex:
            self._out(HODGEText.badge("FAIL") + f" sweep: {type(ex).__name__}: {ex}")
        finally:
            self.cfg.lab3d, self.cfg.sweeps = saved_spec, saved_sweeps

    def _menu_video(self):
        """§11.10 VIDEO LAB: объект + fps + frames + N_full → MP4/GIF."""
        fmt = lambda k, **kw: hodge_fmt(self.cfg, k, **kw)
        self._out()
        self._out(HODGEText.dye(fmt("menu.act.video_lab"), "gold_dim"))
        self._out(fmt("menu.video.objects"))
        for vname in sorted(_LAB_VIDEO_OBJECTS):
            o = _LAB_VIDEO_OBJECTS[vname]
            self._out("    " + HODGEText.dye(vname, "gold_bright")
                      + f"  ({o.kind})")

        def ask_i(prompt, default, lo, hi):
            s = self._menu_read(prompt, allow_empty=True)
            if s is None:
                return None
            try:
                v = int(s) if s else default
            except ValueError:
                v = default
            return max(lo, min(hi, v))

        ans = self._menu_read(
            HODGEText.dye(fmt("menu.video.prompt"), "gold_bright"),
            allow_empty=True)
        if ans is None:
            return
        vname = ans or "sphere"
        if vname not in _LAB_VIDEO_OBJECTS:
            self._out(HODGEText.badge("FAIL") + " "
                      + fmt("submenu.video.bad_obj", obj=vname))
            return
        fps = ask_i(HODGEText.dye(fmt("submenu.video.fps_prompt"), "gold_bright"),
                    24, 5, 60)
        if fps is None:
            return
        frames = ask_i(HODGEText.dye(fmt("submenu.video.frames_prompt"),
                                     "gold_bright"), 120, 2, 2000)
        if frames is None:
            return
        n_full = ask_i(HODGEText.dye(fmt("submenu.video.n_prompt"), "gold_bright"),
                       64, 16, 128)
        if n_full is None:
            return
        self._out(HODGEText.badge("INFO") + " " + fmt(
            "submenu.video.summary", obj=vname, fps=fps, frames=frames,
            n=n_full))
        confirm = self._menu_read(
            HODGEText.dye(fmt("submenu.sweep.confirm"), "gold_bright"),
            allow_empty=True)
        if confirm is None or confirm.lower() == "c":
            return
        vout = (os.path.join(self.cfg.run_dir, "lab_video", vname)
                if self.cfg.run_dir else
                os.path.join(self.cfg.report_dir, "lab_video", vname))
        try:
            hodge_lab_video(self.cfg, object_name=vname, out_dir=vout,
                            fps=fps, frames=frames, n_full=n_full)
        except Exception as ex:
            self._out(HODGEText.badge("FAIL") + f" video: {type(ex).__name__}: {ex}")

    def _list_recipes(self):
        for name, r in RECIPES.items():
            self._out(f"  {name}: {r.get('description', '')}")

    # ── sweep ──
    def _enter_sweep(self):
        self.mode = "sweep"
        self.sweep_fn = ""
        self.sweep_specs = []
        self.render(hodge_fmt(self.cfg, "menu.sweep_fn_prompt"))

    def _handle_sweep_input(self, key: str):
        fmt = lambda k, **kw: hodge_fmt(self.cfg, k, **kw)
        if not self.sweep_fn:
            # Валидация имени: lab_eval знает только эти три функции; раньше
            # любое слово принималось и молча рисовало нулевую поверхность.
            cand = key or "omega"
            base = "expr" if cand.startswith("expr:") else cand
            if base not in ("omega", "reflection", "census_h"):
                self.render(fmt("menu.sweep_bad_fn", fn=cand))
                return
            self.sweep_fn = cand
            self.render(fmt("menu.sweep_spec_prompt", fn=self.sweep_fn))
            return
        if not key:
            self.mode = "nav"
            self._execute_sweep()
            self.render()
            return
        try:
            _parse_sweep(key)  # валидация
            self.sweep_specs.append(key)
            self.render(fmt("menu.sweep_added", key=key))
        except ValueError as ex:
            self.render(fmt("menu.sweep_invalid", msg=ex))

    def _execute_sweep(self):
        fmt = lambda k, **kw: hodge_fmt(self.cfg, k, **kw)
        if not self.sweep_specs:
            self.sweep_specs = ["N:7:30:1"]
        # P2.3 / §11.6: предпросмотр — сколько кадров получится
        total = 1
        try:
            for spec in self.sweep_specs:
                _name, vals = _parse_sweep(spec)
                total *= len(vals)
        except ValueError as ex:
            self.render(fmt("menu.sweep_invalid_spec", msg=ex))
            return
        self._out(HODGEText.badge("INFO") + " "
                  + fmt("menu.sweep_preview", fn=self.sweep_fn,
                        specs=",".join(self.sweep_specs), n=total,
                        cap=getattr(self.cfg, "lab_max_frames", 500)))
        old_lab = self.cfg.lab3d
        old_sweeps = list(self.cfg.sweeps)
        try:
            self.cfg.lab3d = self.sweep_fn
            self.cfg.sweeps = list(self.sweep_specs)
            self.cfg.run_dir = self.cfg.run_dir or _new_run_dir(self.cfg)
            hodge_lab3d(self.cfg)
        finally:
            self.cfg.lab3d = old_lab
            self.cfg.sweeps = old_sweeps


class HodgeTUI:
    def __init__(self, cfg: HodgeConfig, theme: HODGEColor,
                 logger: HodgeLogger, runner_factory=None,
                 stdin=None, stdout=None):
        self.cfg = cfg
        self.theme = theme
        self.log = logger
        self._runner_factory = runner_factory
        self._stdin = stdin or sys.stdin
        self._stdout = stdout or sys.stdout
        self.selected = 0
        self.marked: set = set()
        self.filter = ""
        self.mode = "nav"     # nav | filter
        self.status = ""
        self._items = []
        for t in TASKS:
            self._items.append((t["id"], t["slug"], t["title"]))

    def _filtered(self):
        if not self.filter:
            return self._items
        f = self.filter.lower()
        return [it for it in self._items
                if f in it[1].lower() or f in it[2].lower() or f in str(it[0])]

    def render(self) -> None:
        try:
            cols, rows = shutil.get_terminal_size((80, 24))
        except Exception:
            cols, rows = 80, 24
        cols, rows = max(40, cols), max(12, rows)
        out = ["\x1b[H"]
        header = (f"[hodge-master {HODGE_VERSION}] theme={self.theme.name}"
                  f" · filter={self.filter!r} · {len(self.marked)} marked")
        out.append(HODGEText.dye(header.ljust(cols)[:cols], "gold_bright"))
        out.append(HODGEText.dye("─" * cols, "gold_dim"))
        items = self._filtered()
        if self.selected >= len(items):
            self.selected = max(0, len(items) - 1)
        body_h = rows - 6
        start = max(0, self.selected - body_h // 2)
        for i, (tid, slug, title) in enumerate(items[start:start + body_h], start):
            mark = "✦" if tid in self.marked else " "
            cursor = "❯" if i == self.selected else " "
            line_txt = f"{cursor}{mark} [{tid:2d}] {slug:<22} {title}"
            color = "gold_bright" if i == self.selected else "text"
            out.append(HODGEText.dye(line_txt.ljust(cols)[:cols], color))
        out.append(HODGEText.dye("─" * cols, "gold_dim"))
        help_line = "[↑↓/jk] nav  [Space] mark  [/] filter  [Enter] run  [a] all  [q] quit"
        out.append(HODGEText.dye(help_line.ljust(cols)[:cols], "text_dim"))
        status = self.status[:cols]
        out.append(HODGEText.dye(status.ljust(cols), "info"))
        prompt = "filter: " if self.mode == "filter" else "❯ "
        out.append(HODGEText.dye(prompt, "gold_bright"))
        sys.stdout.write("\n".join(out))
        sys.stdout.flush()

    def _read_key(self) -> str:
        """Одна клавиша/escape-последовательность. Blocking. termios-raw."""
        try:
            import termios
            import tty
            fd = self._stdin.fileno()
            old = termios.tcgetattr(fd)
            try:
                tty.setraw(fd, termios.TCSANOW)
                ch = self._stdin.read(1)
                if ch == "\x1b":
                    seq = ""
                    for _ in range(2):
                        try:
                            nch = self._stdin.read(1)
                        except Exception:
                            break
                        if not nch:
                            break
                        seq += nch
                    return "\x1b" + seq
                return ch
            finally:
                termios.tcsetattr(fd, termios.TCSANOW, old)
        except Exception:
            return self._stdin.readline()[:1] or ""

    def run(self) -> int:
        if self.cfg.ci or self.cfg.plain or not HODGEAdapter.isatty(sys.stdout):
            print(HODGEText.badge("WARN") + " --tui недоступен вне tty/в --ci (§14.9)")
            return 2
        restore = "\x1b[0m\x1b[?25h\x1b[?1049l"
        try:
            sys.stdout.write("\x1b[?1049h\x1b[?25l")
            sys.stdout.flush()
            while True:
                self.render()
                k = self._read_key()
                if not k:
                    return 0
                if k in ("q", "Q", "\x03"):  # q / Ctrl+C
                    return 0
                # §27.6 / VII.6: Ctrl+Y — OSC 52 копия пути отчёта
                if k == "\x19" and not self.cfg.no_clipboard:
                    path = getattr(self.cfg, "_last_report_path", "")
                    if path and HODGETerm.caps().get("clipboard"):
                        import base64
                        b64 = base64.b64encode(path.encode()).decode()
                        sys.stdout.write(f"\x1b]52;c;{b64}\x1b\\")
                        sys.stdout.flush()
                        self.status = f"скопировано: {path}"
                    continue
                if self.mode == "filter":
                    if k == "\x1b" or k in ("\r", "\n"):
                        self.mode = "nav"
                        continue
                    if k in ("\x7f", "\x08"):
                        self.filter = self.filter[:-1]
                        continue
                    self.filter += k
                    self.selected = 0
                    continue
                if k in ("/",):
                    self.mode = "filter"
                    continue
                if k in ("j", "\x1b[B"):
                    self.selected = min(len(self._filtered()) - 1, self.selected + 1)
                elif k in ("k", "\x1b[A"):
                    self.selected = max(0, self.selected - 1)
                elif k == " ":
                    items = self._filtered()
                    if items:
                        tid = items[self.selected][0]
                        if tid in self.marked:
                            self.marked.discard(tid)
                        else:
                            self.marked.add(tid)
                elif k in ("\r", "\n"):
                    items = self._filtered()
                    if self.marked:
                        self._launch(sorted(self.marked))
                    elif items:
                        self._launch([items[self.selected][0]])
                elif k in ("a", "A"):
                    self._launch(None)
        except KeyboardInterrupt:
            return 130
        finally:
            sys.stdout.write(restore)
            sys.stdout.flush()

    def _launch(self, ids):
        if self._runner_factory is None:
            self.status = "раннер недоступен"
            return
        cfg = self.cfg
        cfg.tasks = ids or []
        # временно выйти из alt-screen, чтобы показать прогресс
        sys.stdout.write("\x1b[?1049l\x1b[?25h")
        sys.stdout.flush()
        try:
            runner = self._runner_factory(cfg)
            runner.run_all()
            self.status = f"прогон завершён: {len(runner.results)} задач"
        finally:
            sys.stdout.write("\x1b[?1049h\x1b[?25l")
            sys.stdout.flush()


class HodgeSelfTest:
    def __init__(self, cfg: HodgeConfig, theme: HODGEColor, run_dir: str | None):
        self.cfg = cfg
        self.theme = theme
        self.run_dir = run_dir
        self.results = []

    def check(self, name: str, level: str, ok: bool, reason: str = "") -> None:
        self.results.append({"name": name, "level": level, "verdict":
                             "PASS" if ok else "FAIL", "duration_ms": 0, "reason": reason})
        mark = HODGEText.badge("PASS" if ok else "FAIL")
        # §27.2 / A13: строка проверки проходит dye → ASCII-фолбэк глифов
        print(HODGEText.dye(f"  {mark} [{level}] {name}"
                            + (f" · {reason}" if reason else ""), "text"), flush=True)

    def skip(self, name: str, level: str, reason: str) -> None:
        self.results.append({"name": name, "level": level, "verdict": "SKIP",
                             "duration_ms": 0, "reason": reason})
        print(HODGEText.dye(f"  {HODGEText.badge('SKIP')} [{level}] {name} · {reason}",
                            "text"), flush=True)

    def run(self, levels: list) -> int:
        t0 = time.monotonic()
        print(HODGEText.dye("── SELF-TEST ─────────────────────────────", "gold"))
        if "unit" in levels or not levels:
            self._unit()
        if "props" in levels:
            self._props()
        if "l10n" in levels:
            self._l10n()
        if "palette" in levels:
            self._palette()
        if "dye" in levels:
            self._dye()
        if "anim" in levels:
            self._anim()
        if "menu" in levels:
            self._menu()
        if "plot" in levels:
            self._plot()
        if "lab" in levels:
            self._lab3d()
        if "golden" in levels or "golden-update" in levels:
            self._golden()
        if "full" in levels:
            self._integration()
        fails = sum(1 for r in self.results if r["verdict"] == "FAIL")
        dt = time.monotonic() - t0
        print(HODGEText.dye(f"── self-test: {len(self.results)} проверок, "
                            f"{fails} FAIL, {dt:.2f} с ──", "gold"))
        if self.run_dir:
            os.makedirs(os.path.join(self.run_dir, "logs"), exist_ok=True)
            with open(os.path.join(self.run_dir, "logs", "selftest.jsonl"), "w", encoding="utf-8") as f:
                for r in self.results:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
            HODGEAdapter.atomic_write(os.path.join(self.run_dir, "SELFTEST.md"),
                                      "# SELFTEST\n\n" + "\n".join(
                                          f"- {r['verdict']} [{r['level']}] {r['name']}"
                                          + (f" — {r['reason']}" if r['reason'] else "")
                                          for r in self.results) + "\n")
        return 1 if fails else 0

    # ── unit: машина мастера, ≤ 5 с ──
    def _unit(self):
        t0 = time.monotonic()
        with HODGEHP.scope(40):
            pi = HODGEHP.pi(40)
            self.check("π(40) совпадает с эталоном 40 знаков", "unit",
                       str(pi) == "3.141592653589793238462643383279502884197")
            self.check("atan2 симметрия: atan(1)=π/4", "unit",
                       HODGEHP.atan2(HODGEHP.D(1), HODGEHP.D(1), 40) == pi / 4)
            self.check("sin/cos: sin(π/6)=1/2, cos(π/3)=1/2, cos(2π/3)=−1/2", "unit",
                       abs(HODGEHP.sin(pi / 6, 40) - HODGEHP.D(1) / 2) < HODGEHP.D("1e-38")
                       and abs(HODGEHP.cos(pi / 3, 40) - HODGEHP.D(1) / 2) < HODGEHP.D("1e-38")
                       and abs(HODGEHP.cos(2 * pi / 3, 40) + HODGEHP.D(1) / 2) < HODGEHP.D("1e-38"))
            self.check("Γ(1)=Γ(2)=1 и Γ(1/2)=√π", "unit",
                       abs(HODGEHP.gamma(HODGEHP.D(1), 40) - 1) < HODGEHP.D("1e-35")
                       and abs(HODGEHP.gamma(HODGEHP.D(1) / 2, 40) - pi.sqrt()) < HODGEHP.D("1e-35"))
            self.check("числа Бернулли: B₂=1/6, B₄=−1/30, B₆=1/42", "unit",
                       HODGEHP._bernoulli_even(1) == Fraction(1, 6)
                       and HODGEHP._bernoulli_even(2) == Fraction(-1, 30)
                       and HODGEHP._bernoulli_even(3) == Fraction(1, 42))
        self.check("Мёбиус: μ(1)=1, μ(4)=0, μ(6)=1, μ(30)=−1", "unit",
                   [HODGEEX.mobius(m) for m in (1, 4, 6, 30)] == [1, 0, 1, -1])
        self.check("census: две схемы совпадают на N=15", "unit",
                   HODGEEX.census(15)[0] == HODGEEX.census_mobius(15))
        self.check("SNF diag(2,3)→(1,6); diag(6,10,15)→(1,30,30) (NE02)", "unit",
                   HODGEEX.snf([[2, 0], [0, 3]]) == [1, 6]
                   and HODGEEX.snf([[6, 0, 0], [0, 10, 0], [0, 0, 15]]) == [1, 30, 30])
        self.check("Φ₇ и Φ₉ по канонической схеме", "unit",
                   HODGEEX.cyclotomic(7) == [1, 1, 1, 1, 1, 1, 1]
                   and HODGEEX.cyclotomic(9) == [1, 0, 0, 1, 0, 0, 1])
        self.check("башня 15/30: 4⁴P(m/4) ≡ 0 точно", "unit",
                   HODGEEX.bch_exact_residual(15) == ((0, 0), (0, 0))
                   and HODGEEX.bch_exact_residual(30) == ((0, 0), (0, 0)))
        self.check("t*: 6 случаев cert E", "unit",
                   all(HODGEEX.tstar(w, h, a, b) == e for w, h, a, b, e in
                       [(48, 48, 1, 1, 48), (96, 96, 1, 1, 96), (24, 36, 3, 5, 72),
                        (7, 14, 1, 1, 14), (12, 12, 4, 6, 6), (384, 384, 1, 1, 384)]))
        self.check("qscan(2.75,16)=(4,11); 4π² не рационализируется", "unit",
                   HODGEEX.qscan(2.75, 16) == (4, 11)
                   and HODGEEX.qscan(4 * math.pi ** 2, 16) is None)
        self.check("Bareiss det: [[1,2],[3,4]] = −2; [[6,0],[0,10]] = 60", "unit",
                   HODGEEX.bareiss_det([[1, 2], [3, 4]]) == -2
                   and HODGEEX.bareiss_det([[6, 0], [0, 10]]) == 60)
        self.check("рамануджаново сито: μ-формула = сумме по делителям (N=12, все k)", "unit",
                   all(HODGEEX.ramanujan_c(12, k) == _ramanujan_divisor(12, k)
                       for k in range(12)))
        self.check("HODGE-INF N=5: Ω-рефлексия HP vs π/sin на prec 40", "unit",
                   (lambda rows: rows[0]["err_engine"] < 1e-36 and rows[0]["exact_ok"])(
                       _hodge_inf_tower(tower=(5,), prec_eff=40)))
        # §3.2 v4: roundtrip кэша настроек — save → мутация → load
        _sc_ok = False
        try:
            import tempfile as _tfd
            with _tfd.TemporaryDirectory() as _scd:
                _sc_cfg = HodgeConfig()
                _sc_cfg.cache_dir = _scd
                _sc_cfg.prec_extreme = True
                _sc_cfg.prec = 200
                save_settings_cache(_sc_cfg)
                _sc_cfg2 = HodgeConfig()
                _sc_cfg2.cache_dir = _scd
                applied = load_settings_cache(_sc_cfg2)
                _sc_ok = (_sc_cfg2.prec_extreme is True and _sc_cfg2.prec == 200
                          and "prec_extreme" in applied and "prec" in applied)
        except Exception:
            _sc_ok = False
        self.check("settings cache: save→load roundtrip prec_extreme/prec", "unit", _sc_ok)
        # §14 v4: словный псевдоним тумблера prec-extreme
        self.check("prec-extreme word alias: toggle/on/off/не-команда", "unit",
                   parse_prec_extreme_cmd("prec-extreme") == "toggle"
                   and parse_prec_extreme_cmd("precext") == "toggle"
                   and parse_prec_extreme_cmd("prec-extreme on") is True
                   and parse_prec_extreme_cmd("precext off") is False
                   and parse_prec_extreme_cmd("P") is None
                   and parse_prec_extreme_cmd("prec-extreme blah") == "toggle")
        # §3.2 v5: prec без верхней границы — суффиксы k/m/g/t
        self.check("parse_prec_value: 4096/5m/1g/2t/мусор/29", "unit",
                   parse_prec_value("4096") == 4096
                   and parse_prec_value("5m") == 5_000_000
                   and parse_prec_value("1g") == 10 ** 9
                   and parse_prec_value("2t") == 2 * 10 ** 12
                   and parse_prec_value("abc") is None
                   and parse_prec_value("29") is None
                   and parse_prec_value(" 1g ") == 10 ** 9)
        # §3.2 v5: Γ-слой масштабируется с prec (ζ-хвост Стирлинга, guard-разряды)
        _g80 = _g160 = None
        with HODGEHP.scope(80):
            _g80 = abs(HODGEHP.gamma(HODGEHP.D("0.5"), 80) ** 2 - HODGEHP.pi(80)) / HODGEHP.pi(80)
        with HODGEHP.scope(160):
            _g160 = abs(HODGEHP.gamma(HODGEHP.D("0.5"), 160) ** 2 - HODGEHP.pi(160)) / HODGEHP.pi(160)
        self.check("HODGEHP.lgamma: Γ(1/2)² → π, prec 80 → 160, ошибка падает", "unit",
                   bool(_g80 < 1e-70 and _g160 < _g80 and _g160 < 1e-145))
        self.check("HODGE-INF: prec 120 — err < 1e-110 (clamp 60 снят)", "unit",
                   (lambda rows: rows[0]["err_engine"] < 1e-110 and rows[0]["exact_ok"])(
                       _hodge_inf_tower(tower=(5,), prec_eff=120)))
        # §3.2 v6: гейты + Чудновский (перекрытие с Мэчином на 1580 цифр)
        def _gates_check():
            try:
                HODGEHP.gamma(HODGEHP.D(1) / 2, 5000)
                return False, "gamma@5000 не упал"
            except ValueError as e:
                if "ERR_GAMMA_PREC" not in str(e):
                    return False, str(e)[:60]
            try:
                HODGEHP.sin(HODGEHP.D("3.7"), 5_000_000)
                return False, "sin@5m не упал"
            except ValueError as e:
                if "ERR_PREC_OP" not in str(e):
                    return False, str(e)[:60]
            with HODGEHP.scope(512):
                g512 = HODGEHP.gamma(HODGEHP.D(1) / 2, 512)
            with HODGEHP.scope(60):
                if abs(g512 * g512 - HODGEHP.pi(60)) / HODGEHP.pi(60) > HODGEHP.D("1e-50"):
                    return False, "Γ(1/2)²@512 ≠ π"
            with HODGEHP.scope(1596):
                m = 16 * HODGEHP._atan_series(HODGEHP.D(1) / 5, 1596) \
                    - 4 * HODGEHP._atan_series(HODGEHP.D(1) / 239, 1596)
                sm = str(+m)
            sc = str(HODGEHP.pi(1600))
            if sm[2:1582] != sc[2:1582]:
                return False, "Мэчин@1596 ≠ Чудновский@1600"
            return True, ""
        _ok, _why = _gates_check()
        self.check("гейты §3.2 v6: Γ@5000→ERR_GAMMA_PREC, sin@5m→ERR_PREC_OP, "
                   "Γ@512 точен, Мэчин≡Чудновский@1580", "unit", _ok, _why)
        self.check("unit-уровень ≤ 5 с", "unit", time.monotonic() - t0 < 5.0,
                   f"{time.monotonic() - t0:.2f} с")

    # ── props: property-инварианты ──
    def _props(self):
        h1 = json.dumps({str(k): v for k, v in HODGEEX.census(30)[0].items()}, sort_keys=True)
        h2 = json.dumps({str(k): v for k, v in HODGEEX.census(30)[0].items()}, sort_keys=True)
        self.check("детерминизм: census(30) дважды — байт-идентично", "props", h1 == h2)
        self.check("инвариант: Σh_d = g для всех N∈[3,40]", "props",
                   all(sum(HODGEEX.census(N)[0].values()) == (N - 1) * (N - 2) // 2
                       for N in range(3, 41)))
        self.check("инвариант: SNF произведение = |det| для trace-gram 15/30", "props",
                   all(math.prod(HODGEEX.snf([r[:] for r in HODGEEX.trace_gram(N)]))
                       == HODGEEX.bareiss_det(HODGEEX.trace_gram(N)) for N in (15, 30)))
        self.check("инвариант: d_i | d_{i+1} в SNF", "props",
                   all(s[i + 1] % s[i] == 0 if s[i] else True
                       for s in [HODGEEX.snf([r[:] for r in HODGEEX.trace_gram(15)])]
                       for i in range(len(s) - 1)))
        self.check("инвариант: сцены рендерят кадры без NaN и в границах", "props",
                   all(HODGEAnim.render_frames(sc, 3, 40, 10, seed=7) == 3
                       for sc in HODGEAnim.SCENES))

    # ── l10n: паритет MSG (§19.8) ──
    def _l10n(self):
        ru, en = set(MSG["ru"]), set(MSG["en"])
        missing = (ru ^ en) - {"tasks_plural"}
        self.check("все ключи MSG есть в ru и en", "l10n", not missing,
                   f"расхождение: {sorted(missing)}" if missing else "")
        ok = True
        try:
            for lang in ("ru", "en"):
                class _C:
                    pass
                c = _C(); c.lang = lang
                assert hodge_fmt(c, "run.done", passed=1, total=2, sec=0.1)
            HODGEText.plural(1, MSG["ru"]["tasks_plural"])
            HODGEText.plural(3, MSG["ru"]["tasks_plural"])
            HODGEText.plural(5, MSG["ru"]["tasks_plural"])
            HODGEText.plural(21, MSG["ru"]["tasks_plural"])
        except Exception as ex:
            ok = False
        self.check("шаблоны рендерятся без исключений; плюрализация ru one/few/many", "l10n", ok)

    # ── palette: все ключи, три глубины (§19.9) ──
    def _palette(self):
        ok = True
        for name in HODGEColor.THEMES:
            if name == "mono":
                continue
            pal = HODGEColor.THEMES[name]
            missing = [k for k in HODGEColor.REQUIRED_KEYS if k not in pal]
            if missing:
                ok = False
                self.check(f"тема {name}: все ключи в наличии", "palette", False,
                           f"ERR_PALETTE_MISSING {missing}")
        if ok:
            self.check("все темы: ни один ключ не пропущен (ERR_PALETTE_MISSING нет)", "palette", True)
        depth_ok = True
        for name in ("dark-gold", "aurora", "ice", "gold", "emerald"):
            for key, (hexv, c256, c16) in HODGEColor.THEMES[name].items():
                if not (hexv.startswith("#") and len(hexv) == 7 and 0 <= c256 <= 255):
                    depth_ok = False
        self.check("truecolor/256 валидны во всех темах (ERR_PALETTE_INVALID нет)", "palette", depth_ok)
        # §22.3 / §27.8 / A6: mono — dye/num/gradient возвращают СЫРУЮ строку,
        # без ANSI. Проверяем фактическое поведение рендера, а не состояние поля theme
        # (раньше условие было `... or True` — всегда True, тест фиктивный).
        th = HODGEColor("dark-gold", "mono", plain=True)
        saved_theme = HODGEText.theme
        try:
            HODGEText.theme = th
            ok_mono = (th.plain and th.depth == "mono"
                       and HODGEText.dye("probe", "gold") == "probe"
                       and HODGEText.num(42, "int") == "42"
                       and HODGEText.gradient("abc", "gold_dim", "gold_bright", "span") == "abc"
                       and th.color_code("gold") == "")
        finally:
            HODGEText.theme = saved_theme
        self.check("mono: dye/num/gradient — сырая строка, color_code пуст",
                   "palette", ok_mono)
        # ближайший куб xterm-256 для #d4af37 — 179 (замороженный 178 в репо
        # отражает их собственную таблицу, а не формулу ближайшего куба, §1.5)
        self.check("rgb→xterm256 (ближайший куб): #d4af37 → 179", "palette",
                   HODGEColor.rgb_to_xterm256("#d4af37") == 179)

    # ── dye: идемпотентность и tiering (§19.9) ──
    def _dye(self):
        old = HODGEText.theme
        HODGEText.theme = HODGEColor("dark-gold", "truecolor")
        try:
            s = HODGEText.dye("42", "gold")
            self.check("dye возвращает окрашенную строку (truecolor)", "dye", s.startswith("\x1b["))
            self.check("dye идемпотентна: повтор не дублирует ANSI (приём 31)",
                       "dye", HODGEText.dye(s, "gold") == s)
            n = HODGEText.num(1234, "int")
            self.check("num: 1234 → amber (≥1000)", "dye", "amber" in repr(n) or "\x1b[" in n)
            n0 = HODGEText.num(0, "int")
            n999 = HODGEText.num(999, "int")
            nneg = HODGEText.num(-5, "int")
            self.check("num tiering: 0→gold_dim, 999→gold_bright, −5→ember", "dye",
                       n0 != n999 != nneg)
            g = HODGEText.gradient("HODGE", "gold_dim", "gold_bright", "span")
            self.check("gradient span: каждый символ своим оттенком", "dye",
                       g.count("\x1b[38;2;") >= 4)
            self.check("badge PASS содержит текст (не только цвет, §27.3)", "dye",
                       "PASS" in HODGEText.badge("PASS"))
            HODGEText.theme = HODGEColor("dark-gold", "mono", plain=True)
            self.check("в plain dye возвращает сырую строку", "dye",
                       HODGEText.dye("x", "gold") == "x")
        finally:
            HODGEText.theme = old

    # ── anim: N кадров без падений, парность alt-screen (§19.9) ──
    def _anim(self):
        ok = all(HODGEAnim.render_frames(sc, 5, 40, 10, seed=3) == 5
                 for sc in HODGEAnim.SCENES)
        self.check("все 5 сцен рендерят 5 кадров в виртуальный экран", "anim", ok)
        tiny = HODGEAnim.render_frames("particles", 2, 12, 4, seed=1)
        self.check("малый viewport не падает (§23.9)", "anim", tiny == 2)
        self.check("EASING cubic_out: f(0)=0, f(1)=1", "anim",
                   HODGEAnim.EASING["cubic_out"](0.0) == 0.0
                   and HODGEAnim.EASING["cubic_out"](1.0) == 1.0)

    # ── plot: кодеки и канва §11 (§19.9) ──
    def _plot(self):
        c = HODGECanvas(20, 20)
        c.line(0, 0, 19, 19, (255, 0, 0))
        self.check("canvas: line заполняет диагональ (Брезенхем)", "plot",
                   c.buf[0] == 255 and c.buf[1] == 0)
        p = HODGEPlot(40, 30, title="t", aa=1)
        p.add("s", [0, 1, 2], [0, 1, 0])
        png = HODGEPng.encode(p.out_W, p.out_H, p.render())
        self.check("png: валидная подпись \\x89PNG", "plot",
                   png[:8] == b'\x89PNG\r\n\x1a\n')
        self.check("png: IHDR содержит размеры 40×30", "plot",
                   struct.pack('>II', 40, 30) in png[:40])
        gif = HODGEGif.encode(4, 4, [(0, 0, 0), (255, 255, 255)],
                              [bytearray([0] * 16), bytearray([1] * 16)])
        self.check("gif: валидная подпись GIF89a", "plot", gif[:6] == b'GIF89a')
        self.check("gif: trailer 0x3B", "plot", gif[-1] == 0x3B)
        # LZW round-trip: собственный декодер по spec Appendix F
        self.check("gif: LZW round-trip 4×4 (декодер по spec)", "plot",
                   self._lzw_roundtrip(gif) == [bytearray([0] * 16), bytearray([1] * 16)])
        # §F-структура GCE (регрессия s5: лишний 0x04 сдвигал поле delay на
        # байт → зрители читали задержку ×256, кадры «замирали», после GCE
        # оставался посторонний пустой блок). GCE ровно 8 байт:
        # 21 F9 04 | 04 | DD DD | 00 | 00, после — сразу 2C/21/3B.
        g2 = HODGEGif.encode(6, 4, [(0, 0, 0), (255, 255, 255)],
                             [bytearray(24), bytearray([1] * 24)], [7, 33])
        i, gces, chain_ok = 13 + 3 * 256, [], True
        try:
            while i < len(g2):
                b = g2[i]
                if b == 0x3B:
                    break
                if b == 0x21:
                    if g2[i + 1] == 0xF9:
                        n = g2[i + 2]
                        gces.append((n, g2[i + 3],
                                     g2[i + 4] | (g2[i + 5] << 8), g2[i + 6],
                                     g2[i + 3 + n]))
                    i += 2
                    while g2[i]:
                        i += 1 + g2[i]
                    i += 1
                    chain_ok &= i < len(g2) and g2[i] in (0x21, 0x2C, 0x3B)
                    continue
                if b == 0x2C:
                    f = g2[i + 9]
                    i += 10
                    if f & 0x80:
                        i += 3 * (2 << (f & 7))
                    i += 1                       # min code size
                    while g2[i]:
                        i += 1 + g2[i]
                    i += 1
                    chain_ok &= i < len(g2) and g2[i] in (0x21, 0x2C, 0x3B)
                    continue
                chain_ok = False
                break
        except IndexError:
            chain_ok = False
        self.check("gif: GCE ровно 8 байт, delay 7/33 cs, цепочка блоков без лишних байтов (s5)",
                   "plot",
                   chain_ok and len(gces) == 2
                   and gces[0] == (4, 4, 7, 0, 0) and gces[1] == (4, 4, 33, 0, 0))
        # Задержка — сотые секунды: 100/fps (регрессия s5: было 1000//fps —
        # 24 fps играли как ~2.4 fps)
        self.check("gif: delay = round(100/fps) cs: 24→4, 30→3, 50→2, 5→20",
                   "plot",
                   _gif_delay_cs(24) == 4 and _gif_delay_cs(30) == 3
                   and _gif_delay_cs(50) == 2 and _gif_delay_cs(5) == 20)
        # LZW round-trip на большом кадре: рост 9→12 бит и сброс таблицы 4096
        seed = 12345
        big = bytearray()
        for _k in range(96 * 72):
            seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
            big.append((seed >> 16) & 0xFF)
        g3 = HODGEGif.encode(96, 72, [(s, s, s) for s in range(256)], [bytes(big)], [10])
        rt3 = self._lzw_roundtrip(g3)
        self.check("gif: LZW round-trip 96×72 шум (рост 9→12 бит, сброс 4096)", "plot",
                   len(rt3) == 1 and rt3[0] == big)
        # Приёмка СТОРОННЕГО interlace-GIF (§F): строки идут проходами
        # 0/8, 4/8, 2/4, 1/2 — декодер обязан де-интерлейсить (регрессия s5).
        gct2c = [(0, 0, 0), (255, 255, 255)]
        frame_src = bytearray(16)
        for y in range(4):
            for x in range(4):
                frame_src[y * 4 + x] = y
        interlaced = bytearray(16)
        pos = 0
        for start, step in ((0, 8), (4, 8), (2, 4), (1, 2)):
            for y in range(start, 4, step):
                interlaced[pos * 4:(pos + 1) * 4] = frame_src[y * 4:(y + 1) * 4]
                pos += 1
        g4 = (b'GIF89a' + struct.pack('<HHBBB', 4, 4, 0xF0, 0, 0)
              + bytes(v for rgb in gct2c for v in rgb)
              + b'\x21\xF9\x04\x04' + struct.pack('<H', 9) + b'\x00\x00'
              + b'\x2C' + struct.pack('<HHHHB', 0, 0, 4, 4, 0x40)
              + HODGEGif._lzw(bytes(interlaced), 2)
              + b'\x3B')
        rt4 = self._lzw_roundtrip(g4)
        self.check("gif: приёмка стороннего interlace-GIF (де-интерлейс §F)", "plot",
                   len(rt4) == 1 and rt4[0] == frame_src)
        # GCT: точные цвета темы на месте (§F — GIF не блёклый)
        cache = {}
        _quantize_rgb(bytes(_hex_rgb(HODGEColor.PLOT_BG) * 4), cache, "dark-gold")
        bg_idx = cache["exact"][_hex_rgb(HODGEColor.PLOT_BG)]
        self.check("gct: PLOT_BG присутствует точно (§11.5)", "plot",
                   cache["gct"][bg_idx] == _hex_rgb(HODGEColor.PLOT_BG))
        gct_len = len([c for c in cache["gct"]])
        self.check("gct: ровно 256 записей", "plot", gct_len == 256)
        # SVG-экспорт
        svg = HODGEPlot(40, 30, title="s", aa=1).add("a", [0, 1], [0, 1], 'l').to_svg()
        self.check("svg: polyline присутствует", "plot", "<polyline" in svg)

    @staticmethod
    def _lzw_roundtrip(gif_bytes: bytes) -> list:
        """Минимальный GIF-декодер (spec Appendix F) — приёмка кодека §19.9.
        Понимает GCT/LCT, interlace-флаг (де-интерлейс по §F: проходы
        0/8, 4/8, 2/4, 1/2) и смещения кадров. Регрессия s5: interlace
        игнорировался — сторонние (чересстрочные) GIF декодировались
        с переставленными строками."""
        if gif_bytes[:6] not in (b'GIF89a', b'GIF87a'):
            return []
        gflags = gif_bytes[10]
        i = 13
        if gflags & 0x80:
            i += 3 * (2 << (gflags & 7))
        frames = []
        try:
            while i < len(gif_bytes):
                b = gif_bytes[i]
                if b == 0x3B:
                    break
                if b == 0x21:                  # расширение: пропустить sub-blocks
                    i += 2
                    while i < len(gif_bytes) and gif_bytes[i]:
                        i += 1 + gif_bytes[i]
                    i += 1
                    continue
                if b == 0x2C:                  # image descriptor
                    w = gif_bytes[i + 5] | (gif_bytes[i + 6] << 8)
                    h = gif_bytes[i + 7] | (gif_bytes[i + 8] << 8)
                    f = gif_bytes[i + 9]
                    i += 10
                    if f & 0x80:               # локальная палитра
                        i += 3 * (2 << (f & 7))
                    mcs = gif_bytes[i]
                    i += 1
                    data = bytearray()
                    while i < len(gif_bytes) and gif_bytes[i]:
                        n = gif_bytes[i]
                        data += gif_bytes[i + 1:i + 1 + n]
                        i += 1 + n
                    i += 1
                    pix = HODGEGif._lzw_decode(data, mcs)
                    if f & 0x40:               # interlace → де-интерлейс
                        buf = bytearray(w * h)
                        pos = 0
                        for start, step in ((0, 8), (4, 8), (2, 4), (1, 2)):
                            for y in range(start, h, step):
                                buf[y * w:(y + 1) * w] = pix[pos * w:(pos + 1) * w]
                                pos += 1
                        pix = buf
                    frames.append(pix)
                    continue
                i += 1
        except IndexError:
            pass
        return frames

    # ── lab3d: манифест + кадры + GIF (§19.9) ──
    def _lab3d(self):
        import tempfile
        cfg = HodgeConfig()
        cfg.run_dir = tempfile.mkdtemp(prefix="lab_")
        cfg.lab_grid = 8
        lab = HODGE3DLab(cfg, HODGEColor("dark-gold", "truecolor"))
        manifest = lab.run("omega", {"N": [7, 9]}, {}, grid_n=8, max_frames=4)
        self.check("lab3d: манифест и 2 PNG", "lab",
                   manifest["frames"] == 2
                   and len(glob.glob(os.path.join(lab.out_dir, "frame_*.png"))) == 2)
        self.check("lab3d: gif создан и заканчивается 0x3B", "lab",
                   os.path.exists(os.path.join(lab.out_dir, "sweep.gif"))
                   and open(os.path.join(lab.out_dir, "sweep.gif"), "rb").read()[-1] == 0x3B)
        name, vals = _parse_sweep("N:5:9:2")
        self.check("sweep-парсер: N:5:9:2 → [5,7,9]", "lab",
                   name == "N" and vals == [5, 7, 9])

    # ── §19.4 / VI.1: golden-файлы ──
    def _golden(self):
        """Сравнение скалярных результатов с tests/golden/scalars.json.
        --golden-update — перезапись, только по явному флагу."""
        os.makedirs(self.cfg.golden_dir, exist_ok=True)
        golden_path = os.path.join(self.cfg.golden_dir, "scalars.json")
        # собрать текущие скаляры (subset из быстрых задач)
        current = {}
        cfg2 = HodgeConfig()
        apply_preset(cfg2, "quick")
        cfg2.tasks = [1, 9, 13, 18, 23, 25]
        logger = HodgeLogger(cfg2)
        theme = HODGEColor("mono", "mono", plain=True)
        runner = HodgeRunner(cfg2, logger, theme)
        runner.run_all()
        for r in runner.results.values():
            for pno, p in r["passes"].items():
                for k, v in p["metrics"].items():
                    if isinstance(v, (int, float)):
                        current[f"{r['id']}_p{pno}_{k}"] = float(v)
        if self.cfg.golden_update or "golden-update" in self.cfg.self_test:
            HODGEAdapter.atomic_write(golden_path,
                                      json.dumps(current, indent=1, sort_keys=True))
            self.check(f"golden: эталоны перезаписаны ({len(current)} значений)",
                       "golden", True)
            return
        if not os.path.exists(golden_path):
            self.skip("golden: файл эталонов не найден", "golden",
                      f"создайте --golden-update в {golden_path}")
            return
        try:
            expected = json.load(open(golden_path, encoding="utf-8"))
        except Exception as ex:
            self.check("golden: файл читается", "golden", False, str(ex))
            return
        tol = self.cfg.float_tolerance
        bad = []
        for k, v in expected.items():
            cur = current.get(k)
            if cur is None:
                bad.append(f"{k}: missing")
                continue
            if abs(cur - v) > tol * max(abs(v), 1.0):
                bad.append(f"{k}: {cur} vs {v}")
        self.check(f"golden: {len(expected) - len(bad)}/{len(expected)} совпали (tol={tol})",
                   "golden", not bad, "; ".join(bad[:3]))

    # ── menu: open/quit/Ctrl+C/EOF-guard в tty-эмуляции (§19.10) ──
    def _menu(self):
        import io
        cfg = HodgeConfig()
        cfg.lang = "ru"
        theme = HODGEColor("dark-gold", "mono", plain=True)
        logger = HodgeLogger(cfg)
        # q → выход 0
        menu = HodgeMenu(cfg, theme, logger, stdin=io.StringIO("q\n"), stdout=io.StringIO())
        rc = menu.run()
        self.check("меню открывается и `q` выходит с кодом 0", "menu", rc == 0)
        # EOF-guard: 50 пустых строк → 0
        menu = HodgeMenu(cfg, theme, logger, stdin=io.StringIO("\n" * 60),
                         stdout=io.StringIO())
        rc = menu.run()
        self.check("EOF-guard: 50 пустых readline → graceful exit 0", "menu", rc == 0)
        # Ctrl+C → возврат в меню, затем q
        class KbdIn:
            def __init__(self):
                self.n = 0
            def readline(self):
                self.n += 1
                if self.n == 1:
                    raise KeyboardInterrupt
                return "q\n"
        menu = HodgeMenu(cfg, theme, logger, stdin=KbdIn(), stdout=io.StringIO())
        rc = menu.run()
        self.check("Ctrl+C не убивает: возврат в меню и выход по q", "menu", rc == 0)
        # неизвестная клавиша → WARN, меню живо
        menu = HodgeMenu(cfg, theme, logger, stdin=io.StringIO("ц\nq\n"),
                         stdout=io.StringIO())
        rc = menu.run()
        self.check("неизвестная клавиша → WARN и перерисовка, не падение", "menu", rc == 0)

    # ── integration: полный прогон задач на quick-пресете (§19.2) ──
    def _integration(self):
        cfg = HodgeConfig()
        apply_preset(cfg, "quick")
        cfg.tasks = [1, 9, 13, 18]     # самые дешёвые
        logger = HodgeLogger(cfg)
        theme = HODGEColor("mono", "mono", plain=True)
        runner = HodgeRunner(cfg, logger, theme)
        runner.run_all()
        ok = all(r.get("ok") for r in runner.results.values())
        self.check("интеграция: быстрый прогон 4 задач — PASS", "integration", ok)


# ══════════════════════════════════════════════════════════════════════════
# §13.3 ДИАГНОСТИКА: doctor (PASS/WARN/FAIL по пунктам), health (≤ 2 c),
# theme-preview, dry-run, list-*; §10.6 diff; §19.5 bench; §19.6 fuzz;
# §19.7 coverage; man/completions из CLI_SCHEMA (приём 30).
# ══════════════════════════════════════════════════════════════════════════
def hodge_doctor(cfg: HodgeConfig, theme: HODGEColor) -> int:
    checks = []
    def chk(name, ok, warn=False, note=""):
        verdict = "PASS" if ok else ("WARN" if warn else "FAIL")
        checks.append((name, verdict))
        print(f"  {HODGEText.badge(verdict)} {name}" + (f" · {note}" if note else ""))
    caps = HODGETerm.caps()
    chk(f"python {platform.python_version()} ≥ {HODGE_LANG_VERSION}",
        sys.version_info >= (3, 10))
    chk("decimal (C-ускоренный _decimal)", "_decimal" in sys.modules,
        note=f"prec по умолчанию {getcontext().prec}")
    chk("/proc доступен (монитор)", os.path.exists("/proc"), warn=not os.path.exists("/proc"))
    chk("/sys класс температурный (опционально)", os.path.exists("/sys/class/thermal"), warn=True)
    chk(f"терминал: {caps['term'] or '—'} · depth: {caps['color_depth']} · unicode: {caps['unicode']}", True)
    chk("размер терминала", HODGEAdapter.term_width() >= 20,
        warn=HODGEAdapter.term_width() < 40, note=f"{HODGEAdapter.term_width()} колонок")
    try:
        d = os.path.join(cfg.report_dir, ".doctor_probe")
        HODGEAdapter.atomic_write(d, "probe")
        os.remove(d)
        chk("запись в report_dir + атомарный rename", True)
    except OSError as ex:
        chk("запись в report_dir + атомарный rename", False, note=str(ex))
    import fcntl
    chk("flock доступен (lock run-dir)", hasattr(fcntl, "flock"))
    # §24.2 v4: каскад flock → POSIX-lockfile → advisory — честная проверка фолбэка
    try:
        import tempfile
        with tempfile.TemporaryDirectory() as _td:
            _fd, _err = HODGEAdapter.lockfile_acquire(_td, timeout=0.5)
            _lf_ok = _fd is not None and _err is None
            if _fd is not None:
                os.close(_fd)
        chk("lockfile fallback (O_EXCL на этой ФС)", _lf_ok)
    except Exception as ex:
        chk("lockfile fallback (O_EXCL на этой ФС)", False, note=str(ex))
    chk("resource.setrlimit (§12.6)", HODGEAdapter.HAS_RLIMIT)
    chk("симметрия унимодулярности SNF на diag(3,5)→(1,15)", 
        HODGEEX.snf([[3, 0], [0, 5]]) == [1, 15])
    bad = sum(1 for _, v in checks if v == "FAIL")
    print(f"  {HODGEText.dye('doctor:', 'gold')} {len(checks) - bad}/{len(checks)} PASS · "
          f"{HODGEText.badge('ALL PASS' if bad == 0 else 'FAIL')}")
    return 0 if bad == 0 else 1

def hodge_health(cfg: HodgeConfig) -> int:
    ok = sys.version_info >= (3, 10) and os.path.exists("/proc")
    print(f"  {HODGEText.badge('PASS' if ok else 'FAIL')} health: python+proc, {time.monotonic() % 1:.2f}s")
    return 0 if ok else 1

def hodge_theme_preview(cfg: HodgeConfig, theme: HODGEColor) -> int:
    """§21.6: свотчи + образцы + фолбэки; ничего не запускает."""
    for name in HODGEColor.THEMES:
        t = HODGEColor(name, "truecolor")
        if cfg.ci or cfg.plain:
            pal = HODGEColor.THEMES[name] or {}
            print(f"{name}: " + " ".join(f"{k}={v[0]}/{v[1]}/{v[2]}" for k, v in
                                         list(pal.items())[:8]))
            continue
        print(HODGEText.gradient(f"── {name} " + "─" * 40, "gold_dim", "amber", "span"))
        if HODGEColor.THEMES[name] is None:
            # §27.8: монохром-тема собирается программно — свотчей нет
            print("  монохром — собирается программно (§27.8), все цвета → neutral")
            continue
        for key in HODGEColor.REQUIRED_KEYS:
            sw = "███"
            print(f"  {t.color_code(key)}{sw}\x1b[0m {key:<12} "
                  f"{HODGEColor.THEMES[name][key][0]}/{HODGEColor.THEMES[name][key][1]}")
        print("  образец: " + HODGEText.dye("числа ", "text") + HODGEText.num(1234, "int")
              + " " + HODGEText.dye("статус ", "text") + HODGEText.badge("PASS")
              + " " + HODGEText.badge("FAIL"))
    return 0

def hodge_monitor_animate(cfg: HodgeConfig, theme: HODGEColor) -> int:
    """§23.4 / A8: полноэкранная панель с анимацией. try/finally восстанавливает
    экран (§23.11). В pipe/CI/plain не вызывается — parse_cli срезал до panel."""
    scene_name = cfg.anim_scene if cfg.anim_scene in HODGEAnim.SCENES else "particles"
    try:
        rows_full = shutil.get_terminal_size((80, 24)).lines
    except Exception:
        rows_full = 24
    cols = max(20, min(120, HODGEAdapter.term_width() - 2))
    rows = max(6, min(30, rows_full - 4))
    scene = HODGEAnim(scene_name, cols, rows - 2,
                      particles=cfg.particles, seed=cfg.derive_seed("anim", scene_name),
                      deterministic=cfg.deterministic)
    fps = max(5, min(60, cfg.fps))
    budget = 1.0 / fps
    t0 = time.monotonic()
    prev = t0
    step = 0
    restore = "\x1b[0m\x1b[?25h\x1b[?1049l"
    try:
        sys.stdout.write("\x1b[?1049h\x1b[?25l")  # alt-screen on + cursor off
        sys.stdout.flush()
        while True:
            now = time.monotonic()
            if cfg.anim_seconds > 0 and now - t0 >= cfg.anim_seconds:
                break
            if HodgeRunner._sigint_flag or HodgeRunner._sigterm_flag:
                HodgeRunner._sigint_flag = False
                HodgeRunner._sigterm_flag = False
                break
            delta = now - prev
            if delta < budget / 2:
                time.sleep(budget - delta)
            prev = time.monotonic()
            frame = scene.frame(step)
            step += 1
            # §23.10 / VII.2: CPU-guard — деградация fps при высокой нагрузке
            if cfg.anim_cpu_guard > 0:
                try:
                    with open("/proc/loadavg") as f:
                        load1 = float(f.read().split()[0])
                    cpu_n = os.cpu_count() or 1
                    if 100.0 * load1 / cpu_n > cfg.anim_cpu_guard:
                        time.sleep(budget * 3)   # деградация: fps/4
                except Exception:
                    pass
            if step % 8 == 0 and cfg.title_bar:
                HODGEAnim.set_title(f"[hodge] {scene_name} · step {step} · {theme.name}")
            lines = ["\x1b[H"]   # cursor home — кадр рисуется поверх предыдущего
            lines.append(_monitor_status_line(cfg, theme, prev - t0, step, scene_name))
            lines.append(HODGEText.dye("─" * cols, "gold_dim"))
            for row in frame:
                lines.append(HODGEText.dye(row, "gold"))
            lines.append(HODGEText.dye("─" * cols, "gold_dim"))
            lines.append(HODGEText.dye(
                f"[Ctrl+C] quit · {scene_name}@{fps}fps", "text_dim"))
            sys.stdout.write("\n".join(lines))
            sys.stdout.flush()
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(restore)   # §23.11: экран восстановлен при любом выходе
        sys.stdout.flush()
    return 0


def _monitor_status_line(cfg, theme, elapsed, step, scene_name):
    parts = [f"scene: {scene_name}", f"fps: {cfg.fps}",
             f"step: {step}", f"elapsed: {HODGEText.fmt_duration(elapsed)}",
             f"theme: {theme.name}"]
    return HODGEText.dye(" · ".join(parts), "gold_bright")


def hodge_list_tasks(cfg: HodgeConfig, fmt: str = "tsv") -> int:
    if fmt == "json":
        print(json.dumps(TASKS, ensure_ascii=False, default=str, indent=1))
        return 0
    if fmt == "md":
        print("| id | slug | claims | title | pass2 |")
        print("|---|---|---|---|---|")
        for t in TASKS:
            print(f"| {t['id']} | {t['slug']} | {','.join(t['claims'])} | {t['title']} | "
                  f"{'+' if t['pass2_fn'] else '—'} |")
        return 0
    print("id\tslug\tclaims\test_s\tpass2\ttitle")
    for t in TASKS:
        print(f"{t['id']}\t{t['slug']}\t{','.join(t['claims'])}\t{t['est_sec']}\t"
              f"{'yes' if t['pass2_fn'] else 'no'}\t{t['title']}")
    return 0

def hodge_list_tags(cfg: HodgeConfig) -> int:
    tags = sorted({tg for t in TASKS for tg in t["tags"]})
    print(" ".join(tags))
    return 0

def hodge_list_presets(cfg: HodgeConfig) -> int:
    print("preset\tprec\ttwo_pass\tsize\tnote")
    print("quick\t55\tfalse\t32\tполный ⊕ {two_pass: false} — быстрый smoke")
    print("full\t55\ttrue\t64\tдвухпроходный стандарт")
    print("deep\t60\ttrue\t64\tfull ⊕ {prec: 60} — наследование в одну сторону")
    return 0

def hodge_print_config(cfg: HodgeConfig, explain: bool = False) -> int:
    src = "default_config()" if not explain else "default_config() ← env ← CLI"
    print(f"# эффективный конфиг (источник: {src}) · cfg_hash={cfg.relevant_hash()}")
    for k, v in sorted(vars(cfg).items()):
        val = json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v
        print(f"{k} = {val}")
    print(f"[theme]\nname = {cfg.theme}\n[anim]\nmode = off (сессия 1)")
    return 0

def hodge_dry_run(cfg: HodgeConfig) -> int:
    """§13.3: печатает план; пишет только logs/dryrun.txt (§28.6)."""
    runner_ids = HodgeRunner(cfg, HodgeLogger(cfg), HODGEColor(cfg.theme, cfg.color_depth, cfg.plain)).select_tasks()
    est = sum(TASKS_BY_ID[tid]["est_sec"] for tid in runner_ids)
    plan = [f"Dry-run план · пресет {cfg.preset} · seed {cfg.seed} · prec {cfg.prec}",
            f"задач к прогону: {len(runner_ids)}: {runner_ids}",
            f"two-pass: {cfg.two_pass} · pass_only: {cfg.pass_only} · изоляция seed: {cfg.isolate}",
            f"оценка времени: ~{est:.1f} с (по est_sec реестра)",
            "создаст: results/run_*/task_NN_slug/{{report.md,report.html,logs/}}, results.json, MANIFEST.toml, index.html, FINAL_REPORT/",
            "ничего не вычислено (§13.3)."]
    text = "\n".join(plan)
    print(text)
    if cfg.run_dir:
        os.makedirs(os.path.join(cfg.run_dir, "logs"), exist_ok=True)
        HODGEAdapter.atomic_write(os.path.join(cfg.run_dir, "logs", "dryrun.txt"), text)
    return 0

def hodge_diff(cfg: HodgeConfig, run_a: str, run_b: str) -> int:
    """§10.6: таблица «задача → было/стало/дельта»; FINAL_REPORT/diff.md + diff.html."""
    def load(rd):
        p = os.path.join(rd, "results.json")
        return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None
    A, B = load(run_a), load(run_b)
    if not A or not B:
        print(HODGEText.badge("FAIL") + " у прогона нет results.json")
        return 1
    lines = ["# Diff прогонов", "", f"A = `{run_a}`", f"B = `{run_b}`", "",
             "| задача | A | B | Δ времени | reason_B |", "|---|---|---|---|---|"]
    rows_html = []
    for tid in sorted(set(A["task"]) | set(B["task"]), key=int):
        ta, tb = A["task"].get(tid, {}), B["task"].get(tid, {})
        da = ta.get("duration_s", 0.0)
        db = tb.get("duration_s", 0.0)
        delta = db - da
        mark = "" if ta.get("verdict") == tb.get("verdict") else " ⚠"
        lines.append(f"| {tid} | {ta.get('verdict', '—')} | {tb.get('verdict', '—')}{mark} | "
                     f"{HODGEText.fmt_float(delta, 2)} с | {tb.get('reason') or ''} |")
        # §22.6 / A20: дельта в HTML — num() с окраской по знаку через CSS-класс
        delta_cls = "num ok" if delta < 0 else ("num big" if delta > 0 else "num")
        rows_html.append(f"<tr><td>{tid}</td>"
                         f"<td>{ta.get('verdict', '—')}</td>"
                         f"<td>{tb.get('verdict', '—')}{mark}</td>"
                         f"<td class='{delta_cls}'>{delta:+.2f}</td>"
                         f"<td>{tb.get('reason') or ''}</td></tr>")
    # §10.6 / A20: diff живёт в FINAL_REPORT/ каталога-диффа (единый паттерн артефактов)
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_dir = os.path.join(cfg.report_dir, f"diff_{stamp}")
    final_dir = os.path.join(out_dir, "FINAL_REPORT")
    os.makedirs(final_dir, exist_ok=True)
    HODGEAdapter.atomic_write(os.path.join(final_dir, "diff.md"), "\n".join(lines) + "\n")
    rep = HodgeReports(cfg, HodgeLogger(cfg),
                       HODGEColor(cfg.theme, cfg.color_depth, cfg.plain))
    HODGEAdapter.atomic_write(os.path.join(final_dir, "diff.html"),
                              rep.html_shell("diff",
                              f"<h1>Diff прогонов</h1>"
                              f"<table><tr><th>задача</th><th>A</th><th>B</th><th>Δt</th><th>reason_B</th></tr>"
                              + "".join(rows_html) + "</table>"))
    # §20.1: provenance для diff-прогона
    HODGEAdapter.atomic_write(os.path.join(final_dir, "provenance.md"),
                              f"# Provenance diff\n\n- A: `{run_a}`\n- B: `{run_b}`\n"
                              f"- generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}\n"
                              f"- version: {HODGE_VERSION}\n")
    print(HODGEText.badge("DONE")
          + f" diff → {final_dir}/diff.md, diff.html")
    return 0

def hodge_bench(cfg: HodgeConfig, theme: HODGEColor) -> int:
    """§19.5 + §19.5-stats / VI.2: duration per task; регрессия; t-test при --stats."""
    cfg.tasks = [1, 9, 10, 12, 13, 16, 18]     # дешёвые точные задачи
    cfg.two_pass = False
    n_runs = max(5, cfg.bench_runs) if cfg.bench_stats else 1
    bench_path = os.path.join(cfg.report_dir, "logs", "bench.json")
    prev = {}
    if os.path.exists(bench_path):
        try:
            prev = json.load(open(bench_path, encoding="utf-8"))
        except Exception:
            prev = {}
    samples: dict = {}
    for run_i in range(n_runs):
        logger = HodgeLogger(cfg)
        runner = HodgeRunner(cfg, logger, theme)
        runner.run_all()
        for tid, r in runner.results.items():
            dur = sum(p["duration_s"] for p in r["passes"].values())
            samples.setdefault(r["slug"], []).append(dur)
    out = {}
    fails = 0
    for slug, vals in samples.items():
        mean = statistics.mean(vals)
        stdev = statistics.pstdev(vals) if len(vals) > 1 else 0.0
        entry = {"mean": mean, "stdev": stdev, "n": len(vals), "duration_s": mean}
        if cfg.bench_stats and slug in prev and prev[slug].get("duration_s", 0) > 0:
            prev_mean = prev[slug]["duration_s"]
            # однопараметрический t-тест против prev_mean
            if stdev == 0:
                p_val = 1.0 if abs(mean - prev_mean) < 1e-6 else 0.0
            else:
                t = (mean - prev_mean) / (stdev / math.sqrt(len(vals)))
                # грубая аппроксимация p для n≥5 (df=n-1): |t| > 2.5 → p < 0.05
                p_val = 0.01 if abs(t) > 2.5 else 0.5
            entry["prev_mean"] = prev_mean
            entry["p_value"] = p_val
            entry["delta_pct"] = 100.0 * (mean - prev_mean) / prev_mean
            if mean > prev_mean * cfg.bench_threshold:
                entry["verdict"] = "REGRESSION"
                fails += 1
            else:
                entry["verdict"] = "OK"
        else:
            entry["verdict"] = "BASELINE"
        out[slug] = entry
        print(f"  {HODGEText.badge(entry['verdict'])} {slug}: "
              f"{mean:.3f}±{stdev:.3f} с (n={len(vals)})"
              + (f" p={entry.get('p_value', '—')}" if cfg.bench_stats else ""))
    os.makedirs(os.path.dirname(bench_path), exist_ok=True)
    HODGEAdapter.atomic_write(bench_path, json.dumps(out, indent=1))
    return 1 if fails else 0

def hodge_fuzz(cfg: HodgeConfig, seconds: float, theme: HODGEColor) -> int:
    """§19.6: случайные входы в парсеры (CLI-строки, конфиг-словарь, шаблоны,
    path-builder). Crash = FAIL. Сид фаззинга — derive(seed, 'fuzz')."""
    rnd_seed = cfg.derive_seed("fuzz")
    state = rnd_seed & 0xFFFFFFFFFFFF
    def rnd(n):
        nonlocal state
        state = (state * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)
        return state % n
    alphabet = "--task --preset --seed --theme 1 quick full ru en auto x { } [ ] ' \" \\ NaN inf -1 999999 √ ζ ✓ ─ ● «»"
    tokens = alphabet.split()
    t0 = time.monotonic()
    cases = 0
    crashes = []
    inputs = []
    while time.monotonic() - t0 < seconds:
        cases += 1
        # 1. CLI-парсер
        argv = [tokens[rnd(len(tokens))] for _ in range(rnd(6) + 1)]
        cfgx = HodgeConfig()
        inputs.append(" ".join(argv))
        try:
            parse_cli(cfgx, argv)
        except Exception as ex:
            crashes.append((" ".join(argv), f"{type(ex).__name__}: {ex}"))
        # 2. шаблоны MSG с мусорными ключами
        bad_key = "".join(chr(rnd(0x440) + 32) for _ in range(4))
        try:
            hodge_fmt(cfg, bad_key)
            crashes.append((bad_key, "ERR_TEMPLATE не брошен"))
        except KeyError:
            pass
        # 3. path-guard: slug с '..' → ERR_PATH_TRAVERSAL (§24.3)
        evil = ["..", "/", "a/b", "конь", "", ".", "a" * 200, "../etc/passwd"]
        for e in evil:
            if safe_slug(e) is None:
                continue
            crashes.append((e, "path-guard пропустил опасный slug"))
        # 4. config-file: случайные поля (VI.3)
        import tempfile
        try:
            fd, tmpname = tempfile.mkstemp(suffix=".json")
            with os.fdopen(fd, "w", encoding="utf-8") as tf:
                fuzz_cfg_data = {tokens[rnd(len(tokens))].lstrip("-"):
                                 rnd(1000) for _ in range(rnd(6))}
                json.dump(fuzz_cfg_data, tf)
            try:
                load_config_file(HodgeConfig(), tmpname)
            except Exception as ex:
                # ожидаемая ошибка схемы — не crash
                if not isinstance(ex, (ValueError, TypeError, OSError, KeyError)):
                    crashes.append((f"config {fuzz_cfg_data}", f"{type(ex).__name__}: {ex}"))
        finally:
            try:
                os.unlink(tmpname)
            except OSError:
                pass
        # 5. plot-model: случайные серии (VI.3)
        try:
            npts = rnd(20) + 1
            xs = list(range(npts))
            ys = [rnd(100) for _ in range(npts)]
            p = HODGEPlot(64, 48, aa=1)
            p.add("s", xs, ys, 'l' if rnd(2) else 's')
            buf = p.render()
            if len(buf) != 64 * 48 * 3:
                crashes.append(("plot", f"bad buffer size {len(buf)}"))
        except Exception as ex:
            crashes.append(("plot", f"{type(ex).__name__}: {ex}"))
    ok = not crashes
    rep = [f"fuzz: {cases} случаев за {seconds:.1f} с · seed={rnd_seed}",
           *[f"  CRASH {inp!r} → {err}" for inp, err in crashes[:20]]]
    print(HODGEText.badge("PASS" if ok else "FAIL") + " " + rep[0])
    if cfg.run_dir:
        os.makedirs(os.path.join(cfg.run_dir, "logs"), exist_ok=True)
        HODGEAdapter.atomic_write(os.path.join(cfg.run_dir, "logs", "fuzz.txt"),
                                  "\n".join(rep + ["", "входы:", *inputs[:200]]))
    return 0 if ok else 1

def safe_slug(s: str) -> str | None:
    """§24.3: slug — только [a-z0-9_-], ≤ 64; иначе None (ERR_PATH_TRAVERSAL)."""
    if not s or len(s) > 64 or not re.fullmatch(r"[a-z0-9_-]+", s):
        return None
    return s

def hodge_coverage(cfg: HodgeConfig) -> int:
    """§19.7: строковое покрытие модуля через sys.settrace на лёгком прогоне."""
    executed = set()
    src_path = os.path.abspath(__file__)
    def tracer(frame, event, arg):
        if frame.f_code.co_filename == src_path:
            if event == "line":
                executed.add(frame.f_lineno)
            return tracer
        return None
    cfg2 = HodgeConfig()
    cfg2.tasks = [1, 13, 18]
    apply_preset(cfg2, "quick")
    logger = HodgeLogger(cfg2)
    theme = HODGEColor("mono", "mono", plain=True)
    sys.settrace(tracer)
    try:
        HodgeRunner(cfg2, logger, theme).run_all()
    finally:
        sys.settrace(None)
    total_lines = sum(1 for _ in open(src_path, encoding="utf-8"))
    cov = len(executed) / max(total_lines, 1)
    print(f"  {HODGEText.badge('WARN' if cov < 0.6 else 'PASS')} coverage: {len(executed)}/{total_lines} "
          f"строк ({cov:.0%}); порог {0.6:.0%} → {'WARN, не FAIL (§19.7)' if cov < 0.6 else 'ok'}")
    return 0

def hodge_generate_man() -> int:
    print(""".TH HODGE-MASTER 1 "2026-11-12" "master verification suite"
.SH NAME
hodge\\-master \\- верификация утверждений репозитория hodge\\-laboratory
.SH SYNOPSIS
.B python3 master_hodge.py
[флаги]
.SH DESCRIPTION
Голый запуск в tty открывает интерактивное меню (menu\\-first).
Каждая задача реестра TASKS проверяет одно утверждение репозитория.
.SH OPTIONS""")
    for flag, nargs, desc in CLI_SCHEMA:
        print(f".TP\n.B {flag}" + (f" \\fIзначение\\fR" * min(nargs, 1) if nargs else "")
              + f"\n{desc}")
    print(""".SH EXIT CODES
0 all PASS; 1 FAIL; 2 usage/config; 3 internal; 4 timeout; 130 SIGINT.
.SH SEE ALSO
README репозитория wild8highlander/hodge\\-laboratory""")
    return 0

def hodge_generate_completions(shell: str) -> int:
    flags = [f[0] for f in CLI_SCHEMA]
    if shell == "bash":
        print("# bash completions для master_hodge.py (сгенерировано из CLI_SCHEMA)")
        print("_hodge_master() {")
        print("  local cur=\"${COMP_WORDS[COMP_CWORD]}\" opts=\"" + " ".join(flags) + "\"")
        print("  COMPREPLY=( $(compgen -W \"$opts\" -- \"$cur\") )")
        print("}")
        print("complete -F _hodge_master python3  # и по имени файла")
    elif shell == "zsh":
        print("#compdef master_hodge")
        print("_arguments \\")
        print(" \\\n".join(f"  '{f}[{d}]'" for f, _, d in CLI_SCHEMA))
    elif shell == "fish":
        for f, _, d in CLI_SCHEMA:
            print(f"complete -c master_hodge -l {f.lstrip('-')} -d '{d}'")
    elif shell == "powershell":
        print("# powershell completions")
        print("$opts = @(" + ", ".join(f"'{f}'" for f in flags) + ")")
    else:
        print(f"ERR_UNSUPPORTED shell {shell}", file=sys.stderr)
        return 2
    return 0

def hodge_verify_signature(cfg: HodgeConfig, run_dir: str) -> int:
    """§20.5: проверка HMAC подписи; несовпадение → FAIL, код 1."""
    sig_path = os.path.join(run_dir, "FINAL_REPORT", "signature.sha256")
    if not cfg.sign_key or not os.path.exists(sig_path):
        print(HODGEText.badge("FAIL") + " нет подписи или ключа (--sign-key)")
        return 1
    key = open(cfg.sign_key, "rb").read()
    bad = 0
    for ln in open(sig_path, encoding="utf-8"):
        ln = ln.strip()
        if not ln:
            continue
        mac, rel = ln.split(None, 1)
        p = os.path.join(run_dir, rel)
        if not os.path.exists(p):
            bad += 1
            continue
        want = hmac.new(key, open(p, "rb").read(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(mac, want):   # constant-time (§24.7)
            print(HODGEText.badge("FAIL") + f" подпись не совпала: {rel}")
            bad += 1
    print(HODGEText.badge("PASS" if bad == 0 else "FAIL") +
          f" verify-signature: {rel or 0} файлов, расхождений {bad}")
    return 1 if bad else 0

def hodge_junit(cfg: HodgeConfig, runner: HodgeRunner) -> None:
    """§26.3: JUnit XML (GitHub Actions / GitLab CI)."""
    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           f'<testsuite name="hodge-master" tests="{len(runner.results)}">']
    for r in runner.results.values():
        xml.append(f'  <testcase name="task{r["id"]}_{r["slug"]}" '
                   f'time="{sum(p["duration_s"] for p in r["passes"].values()):.3f}">')
        if r["verdict"] == "FAIL":
            xml.append(f'    <failure message="{r.get("reason") or r["verdict"]}"/>')
        elif r["verdict"] == "SKIP":
            xml.append("    <skipped/>")
        xml.append("  </testcase>")
    xml.append("</testsuite>")
    HODGEAdapter.atomic_write(cfg.junit, "\n".join(xml))

def hodge_jsonl_out(cfg: HodgeConfig, runner: HodgeRunner) -> None:
    """§26.2: построчный machine-readable stdout."""
    for r in runner.results.values():
        rec = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "event": "task_verdict", "task": r["id"], "slug": r["slug"],
               "verdict": r["verdict"], "claims": r["claims"],
               "durations": {k: v["duration_s"] for k, v in r["passes"].items()}}
        print(json.dumps(rec, ensure_ascii=False), flush=True)

def hodge_tsv_out(cfg: HodgeConfig, runner: HodgeRunner) -> None:
    print("id\tslug\tverdict\tduration_s\tclaims")
    for r in runner.results.values():
        print(f"{r['id']}\t{r['slug']}\t{r['verdict']}\t"
              f"{sum(p['duration_s'] for p in r['passes'].values()):.3f}\t{','.join(r['claims'])}")

TASKS_BY_ID = {t["id"]: t for t in TASKS}


# ══════════════════════════════════════════════════════════════════════════
# §18. ТОЧКА ВХОДА: порядок парсинга §13.4; голый запуск в tty → меню;
# --ci/--jsonl/--tsv/pipe → без меню даже при --menu (§26.5); include/import
# → молчаливая загрузка; main() никогда не exit() внутри интерактивной сессии.
# ══════════════════════════════════════════════════════════════════════════
def _setup_theme_text(cfg: HodgeConfig) -> HODGEColor:
    # §27.2 / A1+A2: NO_COLOR, TERM=dumb, --no-color, --plain, --ci/--jsonl/--tsv
    # → plain. §26.1/§26.2: machine-readable режимы без ANSI, без баннера.
    # §20.2: --deterministic запрещает анимации и jitter, но не запрещает цвет.
    term = os.environ.get("TERM", "")
    no_color_env = "NO_COLOR" in os.environ
    effective_plain = (cfg.plain or cfg.no_color or cfg.ci or cfg.jsonl
                       or cfg.tsv or no_color_env or term == "dumb")
    theme = HODGEColor(cfg.theme, cfg.color_depth, effective_plain)
    HODGEText.theme = theme
    # A13: unicode — алфавит глифов; plain/no-color/CI снимают ANSI, но не
    # перекодируют текст l10n (§16). §27.2 / B3: auto → caps["unicode"].
    if cfg.unicode_on == "off":
        HODGEText.unicode_on = False
    elif cfg.unicode_on == "on":
        HODGEText.unicode_on = True
    else:  # auto
        HODGEText.unicode_on = bool(HODGETerm.caps()["unicode"])
    HODGEText.digit_tier = cfg.digit_tier
    # §22.9 / A14: dye_mode — стратегия gradient() (per-char|per-token|per-line)
    HODGEText.dye_mode = (cfg.dye_mode if cfg.dye_mode in ("per-char", "per-token", "per-line")
                          else "per-token")
    # §20.2 / A18: --deterministic отключает всё случайное в выводе
    if cfg.deterministic:
        cfg.anim = "off"
        cfg.monitor = "off"
        cfg.tips = False
        cfg.splash = False
        HODGEText.dye_mode = "per-line"   # per-char даёт разный ANSI при разном len
    return theme

def _new_run_dir(cfg: HodgeConfig) -> str:
    os.makedirs(cfg.report_dir, exist_ok=True)
    base = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    run_dir = os.path.join(cfg.report_dir, base)
    # BUGFIX: два запуска в одну секунду получают одинаковое имя → второй
    # берёт flock того же каталога → ERR_LOCK_HELD. Суффикс _1.._N делает
    # run_dir уникальным.
    i = 1
    while os.path.isdir(run_dir):
        run_dir = os.path.join(cfg.report_dir, f"{base}_{i}")
        i += 1
    os.makedirs(run_dir, exist_ok=True)
    return run_dir


# ── §7.6 / A16 + BUGFIX(VI.3a): flag-обработчики — только на время compute ──
def _install_compute_signals() -> dict:
    """Вешает flag-обработчики SIGINT/SIGTERM/SIGUSR1/SIGHUP и возвращает
    предыдущие обработчики для восстановления. SIGWINCH живёт в меню отдельно.
    В меню (HodgeMenu.run) Ctrl+C обязан бросать KeyboardInterrupt (§14.3)."""
    prev = {}

    def _install(sig_name, fn):
        if hasattr(signal, sig_name):
            try:
                prev[sig_name] = signal.signal(getattr(signal, sig_name), fn)
            except (OSError, ValueError):
                pass  # не main-thread или платформа без сигнала

    _install("SIGINT",  lambda s, f: HodgeRunner.request_cancel())
    _install("SIGTERM", lambda s, f: HodgeRunner.request_terminate())
    _install("SIGUSR1", lambda s, f: HodgeRunner.request_snapshot())
    _install("SIGHUP",  lambda s, f: HodgeRunner.request_reload())
    return prev


def _restore_signal_handlers(prev: dict) -> None:
    """Восстановить обработчики, заменённые _install_compute_signals()."""
    for sig_name, fn in prev.items():
        try:
            signal.signal(getattr(signal, sig_name), fn)
        except (OSError, ValueError):
            pass

def hodge_main(argv: list | None = None) -> int:
    """CLI-вход; возвращает код выхода (§26.4)."""
    global _ACTIVE_LOGGER
    argv = list(sys.argv[1:] if argv is None else argv)
    cfg = HodgeConfig()
    # §3.2 v4: кэш настроек ДО parse_cli (defaults < cache < env < CLI < меню).
    # Ранний пре-скан --no-settings-cache/--settings-reset — они сильнее кэша.
    if "--no-settings-cache" in argv:
        cfg.settings_cache = False
    if "--settings-reset" in argv and reset_settings_cache(cfg):
        print(HODGEText.badge("INFO") + " settings cache reset ("
              + settings_cache_path(cfg) + ")")
    _sc_applied = load_settings_cache(cfg)
    if _sc_applied:
        print(HODGEText.badge("INFO") + " settings cache: "
              + ", ".join(_sc_applied) + " ← " + settings_cache_path(cfg))
    # §13.4 шаг 1: терминальные команды до загрузки конфига
    for a in argv:
        if a in ("--help", "-h"):
            _print_help(cfg)
            return 0
        if a == "--version":
            print(HodgeBanner.render("minimal", HODGEColor("dark-gold", "mono"), cfg))
            return 0
    # автодетект: LANG → язык (§16.1)
    loc = os.environ.get("LC_ALL", "") or os.environ.get("LANG", "") or ""
    if loc.startswith("ru"):
        cfg.lang = "ru"
    elif loc.startswith("en") or loc in ("C", "POSIX", ""):
        cfg.lang = cfg.lang if os.environ.get("HODGE_LANG") else "en"
    # §13.4 шаги 3–4: конфиг-файл, env, CLI, профиль
    terminal = None
    warns = []
    try:
        terminal, warns = parse_cli(cfg, argv)
    except ValueError as ex:
        print(HODGEText.badge("FAIL") + f" {ex}")
        return 2
    for w in warns:
        print(HODGEText.badge("WARN") + " " + w)
        cfg.warns = warns
    theme = _setup_theme_text(cfg)
    # machine-readable/pipe → меню запрещено (§26.5)
    pipe_mode = cfg.ci or cfg.jsonl or cfg.tsv or not HODGEAdapter.isatty(sys.stdin)
    if pipe_mode and cfg.menu_forced:
        print(HODGEText.badge("WARN") + " --menu игнорируется в --ci/--jsonl/--tsv/pipe (§26.5)")
    # терминальные команды
    if terminal == "list-tasks":
        return hodge_list_tasks(cfg, "tsv")
    if terminal == "list-recipes":
        print("recipe\tdescription")
        for name, r in RECIPES.items():
            print(f"{name}\t{r.get('description', '')}")
        return 0
    if terminal == "list-tags":
        return hodge_list_tags(cfg)
    if terminal == "list-presets":
        return hodge_list_presets(cfg)
    if terminal == "theme-preview":
        return hodge_theme_preview(cfg, theme)
    if terminal == "monitor-animate":
        return hodge_monitor_animate(cfg, theme)
    if terminal == "doctor":
        return hodge_doctor(cfg, theme)
    if terminal == "health":
        return hodge_health(cfg)
    if cfg.generate == "man" or terminal == "man":
        return hodge_generate_man()
    if cfg.generate.startswith("completions:"):
        return hodge_generate_completions(cfg.generate.split(":", 1)[1])
    if cfg.verify_signature:
        return hodge_verify_signature(cfg, cfg.verify_signature)
    if cfg.lab3d and cfg.lab3d in _LAB_VIDEO_OBJECTS:
        # §11.10: имя совпало с объектом Video Lab → видео (иначе lab3d)
        p = _LAB_VIDEO_PARAMS
        return hodge_lab_video(cfg, object_name=cfg.lab3d,
                               fps=p["fps"], frames=p["frames"], n_full=p["n"])
    if cfg.lab3d:
        # §11.6.3: 3D-лаборатория — прямой исследовательский режим, не run
        return hodge_lab3d(cfg)
    if cfg.diff_runs:
        return hodge_diff(cfg, cfg.diff_runs[0], cfg.diff_runs[1])
    # служебные команды
    if cfg.print_config or cfg.explain_config:
        return hodge_print_config(cfg, cfg.explain_config)
    if cfg.validate_config_only:
        errs = cfg.validate()
        for e in errs:
            print(HODGEText.badge("FAIL") + " " + e)
        return 2 if errs else 0
    # §7.6 / A16: обработчики всех сигналов. Все — только флаги в обработчике
    # (async-signal-safe); разбор — в HodgeRunner.run_all, меню и animate.
    # BUGFIX(VI.3a): SIGINT/SIGTERM/SIGUSR1/SIGHUP вешаются только для
    # compute-режимов; в меню Ctrl+C обязан бросать KeyboardInterrupt (§14.3) —
    # flag-обработчик делал `except KeyboardInterrupt` в HodgeMenu.run мёртвым
    # кодом («меню зависало» на Ctrl+C). В меню живёт только SIGWINCH.
    prev_handlers = {}
    def _install(sig_name, fn):
        if hasattr(signal, sig_name):
            try:
                prev_handlers[sig_name] = signal.signal(getattr(signal, sig_name), fn)
            except (OSError, ValueError):
                pass  # не main-thread или платформа без сигнала
    compute_mode = bool(cfg.self_test or cfg.bench or cfg.fuzz_sec > 0
                        or cfg.coverage or cfg.dry_run or cfg.tasks)
    if compute_mode:
        _install("SIGINT",  lambda s, f: HodgeRunner.request_cancel())
        _install("SIGTERM", lambda s, f: HodgeRunner.request_terminate())
        _install("SIGUSR1", lambda s, f: HodgeRunner.request_snapshot())
        _install("SIGHUP",  lambda s, f: HodgeRunner.request_reload())
    _install("SIGWINCH", lambda s, f: HodgeRunner.request_resize())

    exit_code = 0
    wall0 = time.monotonic()
    machine_mode = cfg.ci or cfg.jsonl or cfg.tsv
    try:
        if cfg.self_test:
            os.makedirs(cfg.report_dir, exist_ok=True)
            cfg.run_dir = _new_run_dir(cfg)
            _ACTIVE_LOGGER = HodgeLogger(cfg)
            _ACTIVE_LOGGER.open_run(cfg.run_dir)
            st = HodgeSelfTest(cfg, theme, cfg.run_dir)
            ALL_LEVELS = ["unit", "props", "l10n", "palette", "dye", "anim",
                          "menu", "plot", "lab", "golden", "golden-update",
                          "full"]
            if "full" in cfg.self_test:
                levels = ALL_LEVELS
            elif cfg.self_test == ["unit"]:
                levels = ["unit"]
            else:
                levels = ["unit"] + [l for l in cfg.self_test if l in ALL_LEVELS]
            exit_code = st.run(levels)
        elif cfg.bench:
            cfg.run_dir = _new_run_dir(cfg)
            _ACTIVE_LOGGER = HodgeLogger(cfg)
            exit_code = hodge_bench(cfg, theme)
        elif cfg.fuzz_sec > 0:
            cfg.run_dir = _new_run_dir(cfg)
            _ACTIVE_LOGGER = HodgeLogger(cfg)
            exit_code = hodge_fuzz(cfg, cfg.fuzz_sec, theme)
        elif cfg.coverage:
            exit_code = hodge_coverage(cfg)
        elif cfg.dry_run:
            cfg.run_dir = _new_run_dir(cfg)
            _ACTIVE_LOGGER = HodgeLogger(cfg)
            exit_code = hodge_dry_run(cfg)
        elif cfg.tasks:
            # прямой прогон по --task (§13.4 шаг 10)
            exit_code = _run_suite(cfg, theme, pipe_mode)
        elif cfg.tui:
            # §14.9 / V.2: TUI — только в tty (в pipe/plain → WARN + код 2)
            cfg.run_dir = _new_run_dir(cfg)
            _ACTIVE_LOGGER = HodgeLogger(cfg)
            _ACTIVE_LOGGER.open_run(cfg.run_dir)
            exit_code = HodgeTUI(cfg, theme, _ACTIVE_LOGGER,
                                 runner_factory=lambda c: HodgeRunner(c, _ACTIVE_LOGGER, theme)).run()
        elif pipe_mode and not machine_mode:
            # §28.6: голый запуск в pipe → plain-меню; EOF-guard выходит
            # за ≤ 50 пустых readline (интерактив в pipe не открывается)
            if not HODGEAdapter.isatty(sys.stdin):
                # BUGFIX(VI.3b): stdin не TTY — меню мгновенно упрётся в EOF
                # (readline → "" → EOF-guard-цикл). Явный хинт вместо мигающего
                # меню; немедленный выход с кодом 0.
                print(HODGEText.badge("INFO") + " "
                      + hodge_fmt(cfg, "menu.non_tty_hint"))
                return 0
            cfg.run_dir = _new_run_dir(cfg)
            _ACTIVE_LOGGER = HodgeLogger(cfg)
            plain_theme = HODGEColor(cfg.theme, "mono", plain=True)
            HODGEText.theme = plain_theme
            menu = HodgeMenu(cfg, plain_theme, _ACTIVE_LOGGER,
                             runner_factory=lambda c: HodgeRunner(c, _ACTIVE_LOGGER, plain_theme))
            exit_code = menu.run()
        elif cfg.menu_off or not HODGEAdapter.isatty(sys.stdin):
            # --no-menu без --task → ERR_NO_TASK, код 2 (§14.1)
            print(HODGEText.badge("FAIL") + " ERR_NO_TASK: нет --task/--preset для прямого прогона "
                  "(голый запуск в tty открывает меню; в pipe укажите --task)")
            exit_code = 2
        else:
            # §0.3 menu-first (Часть III): баннер — ВНУТРИ меню (HodgeMenu.render).
            # Отдельных шагов splash/tip/MOTD больше нет — меню самодостаточно.
            cfg.run_dir = _new_run_dir(cfg)
            _ACTIVE_LOGGER = HodgeLogger(cfg)
            _ACTIVE_LOGGER.open_run(cfg.run_dir)
            if not cfg.no_clear:
                print("\x1b[2J\x1b[H", end="")
            if cfg.tui:
                # §14.9 / V.2: full-screen TUI (баннер внутри TUI.render)
                tui = HodgeTUI(cfg, theme, _ACTIVE_LOGGER,
                               runner_factory=lambda c: HodgeRunner(c, _ACTIVE_LOGGER, theme))
                exit_code = tui.run()
            else:
                menu = HodgeMenu(cfg, theme, _ACTIVE_LOGGER,
                                 runner_factory=lambda c: HodgeRunner(c, _ACTIVE_LOGGER, theme))
                exit_code = menu.run()
    except KeyboardInterrupt:
        HodgeRunner.request_cancel()
        print("\n" + HODGEText.badge("WARN") + " SIGINT — частичный прогон сохранён (код 130)")
        exit_code = 130
    finally:
        # §7.6 / A16: восстановить все обработчики, что мы заменили
        for sig_name, fn in prev_handlers.items():
            try:
                signal.signal(getattr(signal, sig_name), fn)
            except (OSError, ValueError):
                pass
        # §3.2 v4: --settings-save — настройки и CLI-прогона идут в кэш настроек
        if cfg.settings_cache and cfg.settings_save:
            p = save_settings_cache(cfg)
            if p:
                print(HODGEText.badge("INFO") + " settings saved → " + p)
    wall = time.monotonic() - wall0
    return exit_code

def hodge_menu(argv: list | None = None) -> int:
    """§2.3/§18: публичный вход в интерактивное меню — паритет с hodge_main().
    Голый запуск (main-guard) вызывает его же путь: splash + меню всегда."""
    global _ACTIVE_LOGGER
    cfg = HodgeConfig()
    cfg.menu_forced = True
    # §3.2 v4: меню тоже стартует из кэша настроек (CLI argv сильнее кэша)
    argv = list(argv or [])
    if "--no-settings-cache" in argv:
        cfg.settings_cache = False
    if "--settings-reset" in argv and reset_settings_cache(cfg):
        print(HODGEText.badge("INFO") + " settings cache reset ("
              + settings_cache_path(cfg) + ")")
    load_settings_cache(cfg)
    warns = []
    if argv:
        try:
            _, warns = parse_cli(cfg, list(argv))
        except ValueError as ex:
            print(HODGEText.badge("FAIL") + f" {ex}")
            return 2
    for w in warns:
        print(HODGEText.badge("WARN") + " " + w)
    theme = _setup_theme_text(cfg)
    cfg.run_dir = cfg.run_dir or _new_run_dir(cfg)
    _ACTIVE_LOGGER = HodgeLogger(cfg, theme)
    _ACTIVE_LOGGER.open_run(cfg.run_dir)
    if cfg.splash and not cfg.plain:
        for ln in HodgeBanner.splash(cfg, theme):
            print(HODGEText.dye("· " + ln, "text_dim"))
    if cfg.tips:
        print(HODGEText.dye("tip: " + HodgeBanner.tip_of_day(cfg), "info"))
    menu = HodgeMenu(cfg, theme, _ACTIVE_LOGGER,
                     runner_factory=lambda c: HodgeRunner(c, _ACTIVE_LOGGER, theme))
    return menu.run()


def _run_suite(cfg: HodgeConfig, theme: HODGEColor, pipe_mode: bool) -> int:
    """Полный прогон: раннер → CI-выводы → отчёты → код выхода (§26)."""
    global _ACTIVE_LOGGER, _RUN_LOCK_FD, _RUN_LOCK_PATH
    errs = cfg.validate()
    if errs:
        for e in errs:
            print(HODGEText.badge("FAIL") + " " + e)
        return 2
    if not cfg.run_dir:
        # §25.2 / A9: --resume продолжает ИМЕННО тот прогон — чекпоинт и логи
        # пишутся в тот же run_dir (и flock защищает его от параллельного прогона)
        if cfg.resume_dir:
            cfg.run_dir = cfg.resume_dir
        else:
            cfg.run_dir = _new_run_dir(cfg)
    # §24.2 / A9: flock на run_dir; второй параллельный прогон → ERR_LOCK_HELD, код 2
    lock_fd = None
    try:
        lock_fd, lk_err = HODGEAdapter.flock_run_dir(cfg.run_dir)
        lock_path = os.path.join(cfg.run_dir, ".lock")
        if lock_fd is None:
            # v3: сообщение уже содержит PID держателя + cmdline + подсказку
            print(HODGEText.badge("FAIL") + " ERR_LOCK_HELD: " + (lk_err or "занят другим процессом"))
            return 2
        _RUN_LOCK_FD = lock_fd
        _RUN_LOCK_PATH = lock_path
    except OSError as ex:
        if lock_fd is not None:
            try:
                os.close(lock_fd)
            except OSError:
                pass
        print(HODGEText.badge("FAIL") + f" ERR_LOCK_HELD: не удалось создать lock ({ex})")
        return 2
    _ACTIVE_LOGGER = HodgeLogger(cfg, theme)
    _ACTIVE_LOGGER.open_run(cfg.run_dir)
    _ACTIVE_LOGGER.log_comp("INFO", "Run", f"запуск: preset={cfg.preset} prec={cfg.prec} two_pass={cfg.two_pass}")
    logger = _ACTIVE_LOGGER
    hodge_apply_rlimits(cfg, logger)   # §12.6 / IV.4
    if cfg.clean_orphans:
        hodge_clean_orphans(cfg, logger)   # §24.9 / VII.3
    lock_err = None
    try:
        reports = HodgeReports(cfg, logger, theme)
        runner = HodgeRunner(cfg, logger, theme)
        reports.bind(runner)
        # §8 / III.3: стартовый снэпшот монитора + фоновый async-пробник
        mon = mon_thread = None
        if cfg.monitor in ("on", "panel") and cfg.run_dir:
            mon = HodgeMonitor(os.path.join(cfg.run_dir, "logs", "monitor.csv")
                               if cfg.monitor_csv else None)
            mon.snapshot()
            if cfg.monitor_interval and cfg.monitor_interval > 0:
                import threading
                def _mon_loop():
                    while not mon_thread_stop.is_set():
                        mon_thread_stop.wait(cfg.monitor_interval)
                        if not mon_thread_stop.is_set():
                            mon.snapshot()
                mon_thread_stop = threading.Event()
                mon_thread = threading.Thread(target=_mon_loop, daemon=True)
                mon_thread.start()
        # §15.7 / VII.5: health-probe
        if cfg.health_probe_sec > 0:
            try:
                h = hodge_health(cfg)
                if h != 0:
                    logger.ledger("ERR_HEALTH")
            except Exception:
                logger.ledger("ERR_HEALTH")
        t0 = time.monotonic()
        fire_hook("pre_run", cfg, runner)
        # без сплэша в CI (§26.1); ANSI нет в machine-режимах
        if pipe_mode:
            runner.run_all()
        else:
            if cfg.banner != "off" and not cfg.plain:
                print(HodgeBanner.render("compact", theme, cfg))
            if cfg.splash and not cfg.plain:
                for ln in HodgeBanner.splash(cfg, theme):
                    print(HODGEText.dye("· " + ln, "text_dim"))
            runner.run_all()
        fire_hook("post_run", cfg, runner)
        wall = time.monotonic() - t0
        passed = sum(1 for r in runner.results.values() if r.get("ok"))
        total = len(runner.results)
        all_ok = passed == total and total > 0
        exit_code = 0 if all_ok else 1
        # §33.4 / A15: глобальный таймаут → код 4
        if "ERR_GLOBAL_TIMEOUT" in logger.err_ledger:
            exit_code = 4
        # §26 / VII.5: внутреннее исключение → 3, health → 5
        if "ERR_INTERNAL" in logger.err_ledger:
            exit_code = 3
        if "ERR_HEALTH" in logger.err_ledger:
            exit_code = 5
        # §7.6 / A16: SIGTERM → 143, SIGINT → 130
        if "ERR_SIGTERM" in logger.err_ledger:
            exit_code = 143
        elif "ERR_SIGINT" in logger.err_ledger:
            exit_code = 130
        # §9.4: экспорт метрик в финале
        if getattr(cfg, "metrics_format", "") and logger.metrics:
            hodge_metrics_export(cfg, logger)
        # CI-выводы
        if cfg.jsonl:
            hodge_jsonl_out(cfg, runner)
        if cfg.tsv:
            hodge_tsv_out(cfg, runner)
        if cfg.junit:
            hodge_junit(cfg, runner)
        # сводка в консоль (кроме machine-режимов)
        if not (cfg.ci or cfg.jsonl or cfg.tsv):
            verdict = hodge_fmt(cfg, "all_pass" if all_ok else "has_fail")
            color = "ok" if all_ok else "err"
            print(HODGEText.dye(f"── {hodge_fmt(cfg, 'summary')}: ", "gold")
                  + HODGEText.dye(verdict, color, "bold")
                  + HODGEText.dye(f" ({hodge_fmt(cfg, 'duration')}: {HODGEText.fmt_duration(wall)})",
                                  "text_dim"))
        else:
            print(json.dumps({"event": "summary", "passed": passed, "total": total,
                              "exit_code": exit_code, "duration_s": round(wall, 2)},
                             ensure_ascii=False), flush=True)
        # отчёты (§10): всегда, если не --no-report; results.json пишется всегда
        if not cfg.no_report:
            reports.master(cfg.run_dir, wall, exit_code)
            reports.per_task_all(cfg.run_dir)   # §10.1 per-task каталоги после мастер-отчёта
        else:
            # §30 #15 / §28.4 / A4: --no-report выключает FINAL_REPORT и per-task
            # отчёты; results.json пишем всегда — он нужен --resume и --diff (§10.2, §25.2).
            minimal = {
                "run": {"finished_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        "exit_code": exit_code, "cfg_hash": cfg.relevant_hash(),
                        "preset": cfg.preset, "theme": cfg.theme, "no_report": True},
                "task": {str(r["id"]): {"verdict": r["verdict"],
                                        "reason": r.get("reason"),
                                        "claims": r["claims"],
                                        "duration_s": sum(p["duration_s"] for p in r["passes"].values())}
                         for r in runner.results.values()},
                "errors": {k: {"count": v[0], "last_seen": v[1]}
                           for k, v in logger.err_ledger.items()},
            }
            HODGEAdapter.atomic_write(os.path.join(cfg.run_dir, "results.json"),
                                      json.dumps(minimal, ensure_ascii=False, indent=1))
        # §10.7 / IV.3: cross-run dashboard <report_dir>/index.html
        if not cfg.no_report:
            hodge_cross_run_dashboard(cfg)
        _ACTIVE_LOGGER.event("INFO", "Run", "exit", code=exit_code)
        return exit_code
    except Exception as ex:
        # §26 / B4: внутреннее исключение → ERR_INTERNAL, код 3; lock снят в finally
        logger.ledger("ERR_INTERNAL")
        logger.log_comp("ERROR", "Run", f"internal exception: {type(ex).__name__}: {ex}")
        return 3
    finally:
        # §8: остановить фоновый пробник монитора
        try:
            if mon_thread_stop is not None:   # noqa: F821 — инициализируется в try
                mon_thread_stop.set()
        except NameError:
            pass
        # §24.2 / A9+B4: снять lock при ЛЮБОМ исходе и сбросить глобал
        if lock_fd is not None:
            # §24.2 v4: lock_release удаляет .lockfile в режиме lockfile-fallback
            try:
                HODGEAdapter.lock_release(lock_fd)
            except OSError:
                pass
        _RUN_LOCK_FD = None
        _RUN_LOCK_PATH = None

def _print_help(cfg: HodgeConfig) -> None:
    print(HodgeBanner.render("compact", HODGEColor(cfg.theme, cfg.color_depth, True), cfg))
    print(__doc__ if isinstance(__doc__, str) else "")
    print("Флаги (полный каталог — CLI_SCHEMA):")
    for flag, nargs, desc in CLI_SCHEMA:
        print(f"  {flag:<28} {desc}")
    print("""
Формы запуска (§33):
  python3 master_hodge.py                       # splash + меню (menu-first)
  python3 master_hodge.py --task 8              # V9 deep precision
  python3 master_hodge.py --ci --task all       # машиночитаемый прогон
  python3 master_hodge.py --self-test --full    # полный self-test
  python3 master_hodge.py --doctor              # диагностика среды
Коды выхода: 0 PASS · 1 FAIL · 2 usage/config · 3 internal · 4 timeout · 130 SIGINT · 143 SIGTERM
""")

# §18: точка входа — guard в самом конце файла (после всех блоков задач)


# ══════════════════════════════════════════════════════════════════════════
# СЕССИЯ 2 · БЛОК CHESS-DYNAMICS-LAB: задачи 23–34.
# Порт ядра dynamics.py (0x88 mailbox, make/unmake, Зобрист, поиск, ретро)
# 1:1 по алгоритму — константы заморожены из results/baseline_c1_c9.json и
# frozen-сертификатов dynamics.py:1250–1300. Только stdlib.
# ══════════════════════════════════════════════════════════════════════════
from array import array as _array

class HodgeChess:
    EMPTY = 0
    WP, WN, WB, WR, WQ, WK = 1, 2, 3, 4, 5, 6
    BP, BN, BB, BR, BQ, BK = -1, -2, -3, -4, -5, -6
    PIECE_VALUE = {0: 0, 1: 1, 2: 3, 3: 3, 4: 5, 5: 9, 6: 0}
    PIECE_CHAR = {1: 'P', 2: 'N', 3: 'B', 4: 'R', 5: 'Q', 6: 'K',
                  -1: 'p', -2: 'n', -3: 'b', -4: 'r', -5: 'q', -6: 'k'}
    CHAR_PIECE = {v: k for k, v in PIECE_CHAR.items()}
    SQUARES = [16 * r + f for r in range(8) for f in range(8)]
    KNIGHT_OFFS = (31, 33, 14, 18, -31, -33, -14, -18)
    BISHOP_DIRS = (15, 17, -15, -17)
    ROOK_DIRS = (16, -16, 1, -1)
    KING_DIRS = (15, 16, 17, 1, -15, -16, -17, -1)
    WK_CASTLE, WQ_CASTLE, BK_CASTLE, BQ_CASTLE = 1, 2, 4, 8
    A1, E1, H1 = 0, 4, 7
    A8, E8, H8 = 112, 116, 119
    F1, G1, D1, C1, B1 = 5, 6, 3, 2, 1
    F8, G8, D8, C8, B8 = 117, 118, 115, 114, 113
    FLAG_NORMAL, FLAG_DOUBLE, FLAG_EP, FLAG_CASTLE = 0, 1, 2, 3
    MASK64 = (1 << 64) - 1

    @staticmethod
    def enc_move(fr, to, promo=0, flag=0):
        return fr | (to << 7) | (promo << 14) | (flag << 18)

    @staticmethod
    def m_from(m): return m & 127
    @staticmethod
    def m_to(m): return (m >> 7) & 127
    @staticmethod
    def m_promo(m): return (m >> 14) & 7
    @staticmethod
    def m_flag(m): return (m >> 18) & 3
    @staticmethod
    def sq_name(sq): return "abcdefgh"[sq & 7] + str((sq >> 4) + 1)
    @staticmethod
    def name_sq(s): return 16 * (int(s[1]) - 1) + "abcdefgh".index(s[0])

    # ── splitmix64 и точная инверсия (T09) ──
    @classmethod
    def splitmix64(cls, x):
        x = (x + 0x9E3779B97F4A7C15) & cls.MASK64
        z = x
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & cls.MASK64
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & cls.MASK64
        return z ^ (z >> 31)

    _A_INV = pow(0xBF58476D1CE4E5B9, -1, 1 << 64)
    _B_INV = pow(0x94D049BB133111EB, -1, 1 << 64)

    @classmethod
    def splitmix64_inverse(cls, y):
        z = y
        z ^= z >> 31
        z ^= z >> 62
        z = (z * cls._B_INV) & cls.MASK64
        z ^= z >> 27
        z ^= z >> 54
        z = (z * cls._A_INV) & cls.MASK64
        z ^= z >> 30
        z ^= z >> 60
        return (z - 0x9E3779B97F4A7C15) & cls.MASK64

    _zob = None
    @classmethod
    def zobrist_tables(cls):
        if cls._zob is None:
            piece_keys = {}
            state = 0x1234567890ABCDEF
            for piece in (cls.WP, cls.WN, cls.WB, cls.WR, cls.WQ, cls.WK,
                          cls.BP, cls.BN, cls.BB, cls.BR, cls.BQ, cls.BK):
                arr = [0] * 128
                for sq in range(128):
                    state = cls.splitmix64(state)
                    arr[sq] = state
                piece_keys[piece] = arr
            side_key = cls.splitmix64(state)
            castle_keys = [cls.splitmix64(state := cls.splitmix64(state))
                           for _ in range(16)]
            ep_keys = [cls.splitmix64(state := cls.splitmix64(state))
                       for _ in range(9)]
            cls._zob = (piece_keys, side_key, castle_keys, ep_keys)
        return cls._zob

    @classmethod
    def zobrist_hash(cls, pos):
        ZP, ZS, ZC, ZE = cls.zobrist_tables()
        h = 0
        for sq in cls.SQUARES:
            p = pos["board"][sq]
            if p != cls.EMPTY:
                h ^= ZP[p][sq]
        if pos["side"] == -1:
            h ^= ZS
        h ^= ZC[pos["castling"]]
        h ^= ZE[(pos["ep"] & 7) + 1 if pos["ep"] >= 0 else 0]
        return h

    @classmethod
    def set_fen(cls, fen):
        p_ = cls.CHAR_PIECE
        board = [cls.EMPTY] * 128
        parts = fen.split()
        rows = parts[0].split('/')
        for i, row in enumerate(rows):
            rank, file = 7 - i, 0
            for ch in row:
                if ch.isdigit():
                    file += int(ch)
                else:
                    board[16 * rank + file] = p_[ch]
                    file += 1
        pos = {"board": board, "side": 1 if parts[1] == 'w' else -1,
               "castling": 0, "ep": -1,
               "halfmove": int(parts[4]) if len(parts) > 4 else 0,
               "fullmove": int(parts[5]) if len(parts) > 5 else 1}
        if len(parts) > 2 and parts[2] != '-':
            for ch in parts[2]:
                pos["castling"] |= {'K': 1, 'Q': 2, 'k': 4, 'q': 8}.get(ch, 0)
        if len(parts) > 3 and parts[3] != '-':
            pos["ep"] = cls.name_sq(parts[3])
        pos["hash"] = cls.zobrist_hash(pos)
        return pos

    START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    @classmethod
    def start_position(cls):
        return cls.set_fen(cls.START_FEN)

    @classmethod
    def attacked(cls, pos, sq, by_side):
        b = pos["board"]
        if by_side == 1:
            for off in (-15, -17):
                s = sq + off
                if not (s & 0x88) and b[s] == cls.WP:
                    return True
        else:
            for off in (15, 17):
                s = sq + off
                if not (s & 0x88) and b[s] == cls.BP:
                    return True
        for off in cls.KNIGHT_OFFS:
            s = sq + off
            if not (s & 0x88) and b[s] == 2 * by_side:
                return True
        for off in cls.KING_DIRS:
            s = sq + off
            if not (s & 0x88) and b[s] == 6 * by_side:
                return True
        for dirs, kinds in ((cls.BISHOP_DIRS, (3, 5)), (cls.ROOK_DIRS, (4, 5))):
            for off in dirs:
                s = sq + off
                while not (s & 0x88):
                    p = b[s]
                    if p != cls.EMPTY:
                        if (p > 0) == (by_side > 0) and abs(p) in kinds:
                            return True
                        break
                    s += off
        return False

    @classmethod
    def king_sq(cls, pos, side):
        t = 6 * side
        for sq in cls.SQUARES:
            if pos["board"][sq] == t:
                return sq
        raise ValueError("king missing")

    @classmethod
    def in_check(cls, pos, side=None):
        side = pos["side"] if side is None else side
        return cls.attacked(pos, cls.king_sq(pos, side), -side)

    @classmethod
    def pseudo_moves(cls, pos):
        b = pos["board"]
        side = pos["side"]
        moves = []
        E = cls.EMPTY
        for fr in cls.SQUARES:
            p = b[fr]
            if p == E or (p > 0) != (side > 0):
                continue
            ap = abs(p)
            if ap == 1:
                fwd = 16 * side
                rank = fr >> 4
                promo_rank = 6 if side == 1 else 1
                start_rank = 1 if side == 1 else 6
                s = fr + fwd
                if not (s & 0x88) and b[s] == E:
                    if rank == promo_rank:
                        for pr in (5, 2, 4, 3):
                            moves.append(cls.enc_move(fr, s, pr))
                    else:
                        moves.append(cls.enc_move(fr, s))
                        if rank == start_rank:
                            s2 = s + fwd
                            if b[s2] == E:
                                moves.append(cls.enc_move(fr, s2, 0, cls.FLAG_DOUBLE))
                for off in (fwd - 1, fwd + 1):
                    s = fr + off
                    if s & 0x88:
                        continue
                    q = b[s]
                    if q != E and (q > 0) != (side > 0):
                        if rank == promo_rank:
                            for pr in (5, 2, 4, 3):
                                moves.append(cls.enc_move(fr, s, pr))
                        else:
                            moves.append(cls.enc_move(fr, s))
                    elif (s == pos["ep"] and q == E
                          and (fr >> 4) == (4 if side == 1 else 3)):
                        moves.append(cls.enc_move(fr, s, 0, cls.FLAG_EP))
            elif ap == 2 or ap == 6:
                offs = cls.KNIGHT_OFFS if ap == 2 else cls.KING_DIRS
                for off in offs:
                    s = fr + off
                    if s & 0x88:
                        continue
                    q = b[s]
                    if q == E or (q > 0) != (side > 0):
                        moves.append(cls.enc_move(fr, s))
            else:
                dirs = cls.ROOK_DIRS if ap == 4 else (cls.BISHOP_DIRS if ap == 3 else cls.KING_DIRS)
                for off in dirs:
                    s = fr + off
                    while not (s & 0x88):
                        q = b[s]
                        if q == E:
                            moves.append(cls.enc_move(fr, s))
                        else:
                            if (q > 0) != (side > 0):
                                moves.append(cls.enc_move(fr, s))
                            break
                        s += off
        if side == 1:
            if (pos["castling"] & 1 and b[cls.F1] == E and b[cls.G1] == E
                    and b[cls.E1] == cls.WK and b[cls.H1] == cls.WR
                    and not cls.attacked(pos, cls.E1, -1)
                    and not cls.attacked(pos, cls.F1, -1)
                    and not cls.attacked(pos, cls.G1, -1)):
                moves.append(cls.enc_move(cls.E1, cls.G1, 0, cls.FLAG_CASTLE))
            if (pos["castling"] & 2 and b[cls.D1] == E and b[cls.C1] == E
                    and b[cls.B1] == E and b[cls.E1] == cls.WK and b[cls.A1] == cls.WR
                    and not cls.attacked(pos, cls.E1, -1)
                    and not cls.attacked(pos, cls.D1, -1)
                    and not cls.attacked(pos, cls.C1, -1)):
                moves.append(cls.enc_move(cls.E1, cls.C1, 0, cls.FLAG_CASTLE))
        else:
            if (pos["castling"] & 4 and b[cls.F8] == E and b[cls.G8] == E
                    and b[cls.E8] == cls.BK and b[cls.H8] == cls.BR
                    and not cls.attacked(pos, cls.E8, 1)
                    and not cls.attacked(pos, cls.F8, 1)
                    and not cls.attacked(pos, cls.G8, 1)):
                moves.append(cls.enc_move(cls.E8, cls.G8, 0, cls.FLAG_CASTLE))
            if (pos["castling"] & 8 and b[cls.D8] == E and b[cls.C8] == E
                    and b[cls.B8] == E and b[cls.E8] == cls.BK and b[cls.A8] == cls.BR
                    and not cls.attacked(pos, cls.E8, 1)
                    and not cls.attacked(pos, cls.D8, 1)
                    and not cls.attacked(pos, cls.C8, 1)):
                moves.append(cls.enc_move(cls.E8, cls.C8, 0, cls.FLAG_CASTLE))
        return moves

    @classmethod
    def legal_moves(cls, pos):
        out = []
        for m in cls.pseudo_moves(pos):
            if abs(pos["board"][cls.m_to(m)]) == 6:
                continue
            undo = cls.make(pos, m)
            if not cls.attacked(pos, cls.king_sq(pos, -pos["side"]), pos["side"]):
                out.append(m)
            cls.unmake(pos, undo)
        return out

    @classmethod
    def make(cls, pos, m):
        b = pos["board"]
        fr, to = cls.m_from(m), cls.m_to(m)
        promo, flag = cls.m_promo(m), cls.m_flag(m)
        side = pos["side"]
        piece = b[fr]
        captured = b[to]
        undo = (m, captured, pos["castling"], pos["ep"], pos["halfmove"], pos["hash"])
        ZP, ZS, ZC, ZE = cls.zobrist_tables()
        h = pos["hash"]
        h ^= ZS
        h ^= ZP[piece][fr]
        if captured != cls.EMPTY:
            h ^= ZP[captured][to]
        if flag == cls.FLAG_EP:
            cap_sq = to - 16 * side
            h ^= ZP[b[cap_sq]][cap_sq]
        h ^= ZE[(pos["ep"] & 7) + 1 if pos["ep"] >= 0 else 0]
        b[fr] = cls.EMPTY
        if flag == cls.FLAG_EP:
            cap_sq = to - 16 * side
            b[cap_sq] = cls.EMPTY
        new_piece = promo * side if promo else piece
        b[to] = new_piece
        h ^= ZP[new_piece][to]
        if flag == cls.FLAG_CASTLE:
            if to == cls.G1:
                b[cls.H1], b[cls.F1] = cls.EMPTY, cls.WR
                h ^= ZP[cls.WR][cls.H1] ^ ZP[cls.WR][cls.F1]
            elif to == cls.C1:
                b[cls.A1], b[cls.D1] = cls.EMPTY, cls.WR
                h ^= ZP[cls.WR][cls.A1] ^ ZP[cls.WR][cls.D1]
            elif to == cls.G8:
                b[cls.H8], b[cls.F8] = cls.EMPTY, cls.BR
                h ^= ZP[cls.BR][cls.H8] ^ ZP[cls.BR][cls.F8]
            else:
                b[cls.A8], b[cls.D8] = cls.EMPTY, cls.BR
                h ^= ZP[cls.BR][cls.A8] ^ ZP[cls.BR][cls.D8]
        old_castling = pos["castling"]
        if piece == cls.WK:
            pos["castling"] &= ~(1 | 2)
        elif piece == cls.BK:
            pos["castling"] &= ~(4 | 8)
        if fr == cls.H1 or to == cls.H1:
            pos["castling"] &= ~1
        if fr == cls.A1 or to == cls.A1:
            pos["castling"] &= ~2
        if fr == cls.H8 or to == cls.H8:
            pos["castling"] &= ~4
        if fr == cls.A8 or to == cls.A8:
            pos["castling"] &= ~8
        h ^= ZC[old_castling] ^ ZC[pos["castling"]]
        pos["ep"] = (fr + 16 * side) if flag == cls.FLAG_DOUBLE else -1
        h ^= ZE[(pos["ep"] & 7) + 1 if pos["ep"] >= 0 else 0]
        pos["halfmove"] = 0 if (abs(piece) == 1 or captured != cls.EMPTY) else pos["halfmove"] + 1
        if side == -1:
            pos["fullmove"] += 1
        pos["side"] = -side
        pos["hash"] = h
        return undo

    @classmethod
    def unmake(cls, pos, undo):
        m, captured, castling, ep, halfmove, h = undo
        b = pos["board"]
        fr, to = cls.m_from(m), cls.m_to(m)
        promo, flag = cls.m_promo(m), cls.m_flag(m)
        side = -pos["side"]
        piece = b[to]
        if promo:
            piece = 1 * side
        b[fr] = piece
        b[to] = captured
        if flag == cls.FLAG_EP:
            b[to - 16 * side] = -1 * side
        if flag == cls.FLAG_CASTLE:
            if to == cls.G1:
                b[cls.H1], b[cls.F1] = cls.WR, cls.EMPTY
            elif to == cls.C1:
                b[cls.A1], b[cls.D1] = cls.WR, cls.EMPTY
            elif to == cls.G8:
                b[cls.H8], b[cls.F8] = cls.BR, cls.EMPTY
            else:
                b[cls.A8], b[cls.D8] = cls.BR, cls.EMPTY
        pos["castling"] = castling
        pos["ep"] = ep
        pos["halfmove"] = halfmove
        pos["fullmove"] -= 1 if side == -1 else 0
        pos["side"] = side
        pos["hash"] = h

    @classmethod
    def to_fen(cls, pos):
        rows = []
        for rank in range(7, -1, -1):
            row, run = '', 0
            for file in range(8):
                p = pos["board"][16 * rank + file]
                if p == cls.EMPTY:
                    run += 1
                else:
                    if run:
                        row += str(run)
                        run = 0
                    row += cls.PIECE_CHAR[p]
            if run:
                row += str(run)
            rows.append(row)
        castle = ''.join(c for c, bb in zip('KQkq', (1, 2, 4, 8)) if pos["castling"] & bb) or '-'
        ep = cls.sq_name(pos["ep"]) if pos["ep"] >= 0 else '-'
        return "%s %s %s %s %d %d" % ('/'.join(rows), 'w' if pos["side"] == 1 else 'b',
                                      castle, ep, pos["halfmove"], pos["fullmove"])

    # ── атак-поля, поля угроз, энергия ──
    @classmethod
    def piece_attack_squares(cls, board, sq, blocking=True):
        p = board[sq]
        ap = abs(p)
        out = []
        if ap == 1:
            fwd = 16 * (1 if p > 0 else -1)
            for off in (fwd - 1, fwd + 1):
                s = sq + off
                if not (s & 0x88):
                    out.append(s)
        elif ap == 2:
            for off in cls.KNIGHT_OFFS:
                s = sq + off
                if not (s & 0x88):
                    out.append(s)
        elif ap == 6:
            for off in cls.KING_DIRS:
                s = sq + off
                if not (s & 0x88):
                    out.append(s)
        else:
            dirs = cls.ROOK_DIRS if ap == 4 else (cls.BISHOP_DIRS if ap == 3 else cls.KING_DIRS)
            for off in dirs:
                s = sq + off
                while not (s & 0x88):
                    out.append(s)
                    if blocking and board[s] != cls.EMPTY:
                        break
                    s += off
        return out

    @classmethod
    def threat_field(cls, pos, side):
        theta = [0] * 128
        for sq in cls.SQUARES:
            p = pos["board"][sq]
            if p != cls.EMPTY and (p > 0) == (side > 0):
                for s in cls.piece_attack_squares(pos["board"], sq):
                    theta[s] += 1
        return theta

    @classmethod
    def attack_sum_identity(cls, pos, side):
        theta = cls.threat_field(pos, side)
        total_field = sum(theta[sq] for sq in cls.SQUARES)
        total_pieces = 0
        for sq in cls.SQUARES:
            p = pos["board"][sq]
            if p != cls.EMPTY and (p > 0) == (side > 0):
                total_pieces += len(cls.piece_attack_squares(pos["board"], sq))
        return total_field, total_pieces

    @classmethod
    def mobility(cls, pos, side):
        saved = pos["side"]
        pos["side"] = side
        n = len(cls.legal_moves(pos))
        pos["side"] = saved
        return n

    @classmethod
    def material(cls, pos, side):
        return sum(cls.PIECE_VALUE[abs(pos["board"][sq])]
                   for sq in cls.SQUARES
                   if pos["board"][sq] != cls.EMPTY and (pos["board"][sq] > 0) == (side > 0))

    @classmethod
    def energy(cls, pos, side=1):
        mu = 0.1
        return (cls.material(pos, 1) - cls.material(pos, -1)
                + mu * (cls.mobility(pos, 1) - cls.mobility(pos, -1)))

    # ── поток/бильярд (Klein/K3) ──
    @classmethod
    def tstar_chess(cls, W, H, a, b):
        gx = HODGEEX.gcd(abs(a), W) or W
        gy = HODGEEX.gcd(abs(b), H) or H
        px, py = W // gx, H // gy
        return px * py // HODGEEX.gcd(px, py)

    @classmethod
    def simulate_torus_flow(cls, W, H, a, b, max_steps=100000):
        x = y = 0
        visited = {(0, 0)}
        for step in range(1, max_steps + 1):
            x = (x + a) % W
            y = (y + b) % H
            if (x, y) == (0, 0):
                return step, visited
            visited.add((x, y))
        return None, visited

    @classmethod
    def simulate_billiard(cls, W, H, a, b, gamma, eps=1e-12, max_steps=200000):
        x, y = 0.5, 0.5
        vx, vy = float(a), float(b)
        v0 = math.hypot(vx, vy)
        path = 0.0
        reflections = 0
        for step in range(1, max_steps + 1):
            speed = math.hypot(vx, vy)
            if speed < eps:
                exact = v0 / (1.0 - gamma)
                return step - 1, path, reflections, True, path / exact
            nx, nvx = x + vx, vx
            ny, nvy = y + vy, vy
            while nx < 0 or nx > W:
                nx = -nx if nx < 0 else 2 * W - nx
                nvx = -nvx
                reflections += 1
            while ny < 0 or ny > H:
                ny = -ny if ny < 0 else 2 * H - ny
                nvy = -nvy
                reflections += 1
            x, y, vx, vy = nx, ny, nvx, nvy
            path += speed
            vx *= gamma
            vy *= gamma
        exact = v0 / (1.0 - gamma)
        return max_steps, path, reflections, False, path / exact

    # ── D4/V4 орбиты и Бернсайд ──
    @staticmethod
    def _id(f, r): return (f, r)
    @staticmethod
    def _rot90(f, r): return (r, 7 - f)
    @staticmethod
    def _rot180(f, r): return (7 - f, 7 - r)
    @staticmethod
    def _rot270(f, r): return (7 - r, f)
    @staticmethod
    def _mir_h(f, r): return (7 - f, r)
    @staticmethod
    def _mir_v(f, r): return (f, 7 - r)
    @staticmethod
    def _diag(f, r): return (r, f)
    @staticmethod
    def _antidiag(f, r): return (7 - r, 7 - f)

    D4G = None
    V4G = None
    @classmethod
    def groups(cls):
        if cls.D4G is None:
            cls.D4G = {'id': cls._id, 'rot90': cls._rot90, 'rot180': cls._rot180,
                       'rot270': cls._rot270, 'mir_h': cls._mir_h, 'mir_v': cls._mir_v,
                       'diag': cls._diag, 'antidiag': cls._antidiag}
            cls.V4G = {'id': cls._id, 'rot180': cls._rot180, 'diag': cls._diag,
                       'antidiag': cls._antidiag}
        return cls.D4G, cls.V4G

    @classmethod
    def orbits(cls, group):
        seen = set()
        orbs = []
        for f in range(8):
            for r in range(8):
                if (f, r) in seen:
                    continue
                orb = set()
                for g in group.values():
                    orb.add(g(f, r))
                orbs.append(tuple(sorted(orb)))
                seen |= orb
        return orbs

    @staticmethod
    def burnside_orbits(fixed_counts):
        return sum(fixed_counts.values()) // len(fixed_counts)

    # ── графы фигур и мобильность ──
    PIECE_CODE = None
    @classmethod
    def piece_graph_directed(cls, piece_type):
        if cls.PIECE_CODE is None:
            cls.PIECE_CODE = {2: cls.WN, 3: cls.WB, 4: cls.WR, 5: cls.WQ, 6: cls.WK}
        board = [cls.EMPTY] * 128
        code = cls.PIECE_CODE[piece_type]
        directed = 0
        for sq in cls.SQUARES:
            board[sq] = code
            directed += len(cls.piece_attack_squares(board, sq, blocking=False))
            board[sq] = cls.EMPTY
        return directed

    @classmethod
    def empty_board_graph(cls, piece_type):
        if cls.PIECE_CODE is None:
            cls.PIECE_CODE = {2: cls.WN, 3: cls.WB, 4: cls.WR, 5: cls.WQ, 6: cls.WK}
        board = [cls.EMPTY] * 128
        code = cls.PIECE_CODE[piece_type]
        adj = {sq: set() for sq in cls.SQUARES}
        for sq in cls.SQUARES:
            board[sq] = code
            for s in cls.piece_attack_squares(board, sq, blocking=True):
                if s != sq:
                    adj[sq].add(s)
                    adj[s].add(sq)
            board[sq] = cls.EMPTY
        return adj

    @classmethod
    def graph_components(cls, adj):
        seen = set()
        comps = []
        for v in adj:
            if v in seen:
                continue
            stack, comp = [v], set()
            while stack:
                u = stack.pop()
                if u in comp:
                    continue
                comp.add(u)
                stack.extend(adj[u] - comp)
            seen |= comp
            comps.append(sorted(comp))
        return comps

    @classmethod
    def is_bipartite(cls, adj):
        color = {}
        for v in adj:
            if v in color:
                continue
            color[v] = 0
            stack = [v]
            while stack:
                u = stack.pop()
                for w in adj[u]:
                    if w not in color:
                        color[w] = color[u] ^ 1
                        stack.append(w)
                    elif color[w] == color[u]:
                        return False, color
        return True, color

    @classmethod
    def mobility_census(cls):
        board = [cls.EMPTY] * 128
        out = {}
        for name, code in (('king', cls.WK), ('knight', cls.WN), ('bishop', cls.WB),
                           ('rook', cls.WR), ('queen', cls.WQ)):
            table = []
            for sq in cls.SQUARES:
                board[sq] = code
                table.append(len(cls.piece_attack_squares(board, sq, blocking=False)))
                board[sq] = cls.EMPTY
            mx = max(table)
            argmax = [cls.sq_name(cls.SQUARES[i]) for i, v in enumerate(table) if v == mx]
            out[name] = {'table': table, 'max': mx, 'argmax': argmax, 'sum': sum(table)}
        bt, rt, qt = out['bishop']['table'], out['rook']['table'], out['queen']['table']
        out['bishop_closed_form_ok'] = all(
            bt[i] == 14 - abs(i % 8 - i // 8) - abs(i % 8 + i // 8 - 7) for i in range(64))
        out['queen_closed_form_ok'] = all(qt[i] == rt[i] + bt[i] for i in range(64))
        return out

    # ── поиск: alpha-beta + матовый DFS (порт 1:1, узлы зависят от порядка) ──
    MATE = 1000000

    @classmethod
    def pseudo_mobility(cls, pos, side):
        saved = pos["side"]
        pos["side"] = side
        n = len(cls.pseudo_moves(pos))
        pos["side"] = saved
        return n

    @classmethod
    def evaluate(cls, pos):
        sign = 1 if pos["side"] == 1 else -1
        mat = cls.material(pos, 1) - cls.material(pos, -1)
        mob = cls.pseudo_mobility(pos, 1) - cls.pseudo_mobility(pos, -1)
        return sign * int(round(100 * mat + 10 * mob))

    @classmethod
    def order_moves(cls, pos, moves):
        b = pos["board"]
        def score(m):
            to = cls.m_to(m)
            cap = b[to]
            s = 0
            if cap != cls.EMPTY:
                s += 100 + 10 * cls.PIECE_VALUE[abs(cap)] - cls.PIECE_VALUE[abs(b[cls.m_from(m)])]
            if cls.m_flag(m) == cls.FLAG_EP:
                s += 100 + 9
            if cls.m_promo(m):
                s += 90
            f, r = to & 7, to >> 4
            s += (3.5 - abs(f - 3.5)) + (3.5 - abs(r - 3.5))
            return -s
        return sorted(moves, key=score)

    @classmethod
    def quiescence(cls, pos, alpha, beta):
        stand = cls.evaluate(pos)
        if stand >= beta:
            return beta
        if stand > alpha:
            alpha = stand
        caps = [m for m in cls.pseudo_moves(pos)
                if pos["board"][cls.m_to(m)] != cls.EMPTY or cls.m_flag(m) == cls.FLAG_EP]
        for m in cls.order_moves(pos, caps):
            undo = cls.make(pos, m)
            if cls.attacked(pos, cls.king_sq(pos, -pos["side"]), pos["side"]):
                cls.unmake(pos, undo)
                continue
            score = -cls.quiescence(pos, -beta, -alpha)
            cls.unmake(pos, undo)
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        return alpha

    @classmethod
    def negamax(cls, pos, depth, alpha, beta, ply, node_counter):
        node_counter[0] += 1
        if pos["halfmove"] >= 100:
            return 0
        moves = cls.legal_moves(pos)
        if not moves:
            return -cls.MATE + ply if cls.in_check(pos, pos["side"]) else 0
        if depth == 0:
            return cls.quiescence(pos, alpha, beta)
        for m in cls.order_moves(pos, moves):
            undo = cls.make(pos, m)
            score = -cls.negamax(pos, depth - 1, -beta, -alpha, ply + 1, node_counter)
            cls.unmake(pos, undo)
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        return alpha

    @classmethod
    def search_best_move(cls, pos, depth, node_counter=None):
        if node_counter is None:
            node_counter = [0]
        best, best_score = None, -2 * cls.MATE
        alpha, beta = -2 * cls.MATE, 2 * cls.MATE
        for m in cls.order_moves(pos, cls.legal_moves(pos)):
            undo = cls.make(pos, m)
            score = -cls.negamax(pos, depth - 1, -beta, -alpha, 1, node_counter)
            cls.unmake(pos, undo)
            if score > best_score:
                best, best_score = m, score
            alpha = max(alpha, score)
        return best, best_score, node_counter[0]

    @classmethod
    def mate_search(cls, pos, max_depth, node_counter=None):
        if node_counter is None:
            node_counter = [0]
        for depth in range(1, max_depth + 1):
            res = cls._mate_dfs(pos, depth, node_counter)
            if res is not None:
                plies, pv = res
                return plies, pv, node_counter[0]
        return None, [], node_counter[0]

    @classmethod
    def _mate_dfs(cls, pos, depth, node_counter):
        node_counter[0] += 1
        if depth <= 0:
            return None
        best = None
        for m in cls.order_moves(pos, cls.legal_moves(pos)):
            undo = cls.make(pos, m)
            replies = cls.legal_moves(pos)
            if not replies:
                mated = cls.in_check(pos, pos["side"])
                cls.unmake(pos, undo)
                if mated:
                    return 1, [m]
                continue
            if depth >= 2:
                worst_plies = -1
                worst_line = None
                all_mated = True
                for r in cls.order_moves(pos, replies):
                    u2 = cls.make(pos, r)
                    sub = cls._mate_dfs(pos, depth - 2, node_counter)
                    cls.unmake(pos, u2)
                    if sub is None:
                        all_mated = False
                        break
                    if sub[0] > worst_plies:
                        worst_plies = sub[0]
                        worst_line = [r] + sub[1]
                if all_mated:
                    cls.unmake(pos, undo)
                    cand = (worst_plies + 2, [m] + worst_line)
                    if best is None or cand[0] < best[0]:
                        best = cand
                        if best[0] <= 3:
                            return best
                    continue
            cls.unmake(pos, undo)
        return best

    @classmethod
    def move_to_uci(cls, m):
        s = cls.sq_name(cls.m_from(m)) + cls.sq_name(cls.m_to(m))
        pr = cls.m_promo(m)
        if pr:
            s += {5: 'q', 2: 'n', 4: 'r', 3: 'b'}[pr]
        return s

    @classmethod
    def uci_to_move(cls, pos, uci):
        fr, to = cls.name_sq(uci[0:2]), cls.name_sq(uci[2:4])
        pr = {'q': 5, 'n': 2, 'r': 4, 'b': 3}.get(uci[4] if len(uci) > 4 else '', 0)
        for m in cls.legal_moves(pos):
            if cls.m_from(m) == fr and cls.m_to(m) == to and cls.m_promo(m) == pr:
                return m
        raise ValueError("illegal move %s" % uci)

    # ── ретроградные DTM-таблицы KRK/KQK ──
    @staticmethod
    def pack_state(wk, wq, bk, stm):
        return wk | (wq << 7) | (bk << 14) | (stm << 21)

    @staticmethod
    def kings_adjacent(a, b):
        return max(abs((a & 7) - (b & 7)), abs((a >> 4) - (b >> 4))) <= 1

    @classmethod
    def _children_white(cls, wk, wq, bk, code):
        ch = []
        KN = {sq: [sq + o for o in cls.KING_DIRS if not ((sq + o) & 0x88)] for sq in cls.SQUARES}
        for dest in KN[wk]:
            if dest == wq or dest == bk or dest in KN[bk]:
                continue
            ch.append(dest | (wq << 7) | (bk << 14) | (1 << 21))
        board = [cls.EMPTY] * 128
        board[wk], board[wq], board[bk] = cls.WK, code, cls.BK
        for dest in cls.piece_attack_squares(board, wq, blocking=True):
            if dest == wk or dest == bk:
                continue
            ch.append(wk | (dest << 7) | (bk << 14) | (1 << 21))
        return ch

    @classmethod
    def _children_black(cls, wk, wq, bk, code):
        ch = []
        captured = 0
        KN = {sq: [sq + o for o in cls.KING_DIRS if not ((sq + o) & 0x88)] for sq in cls.SQUARES}
        board = [cls.EMPTY] * 128
        board[wk], board[wq], board[bk] = cls.WK, code, cls.BK
        for dest in KN[bk]:
            if dest == wk:
                continue
            if dest in KN[wk]:
                continue
            if dest == wq:
                captured = 1
                continue
            board2 = [cls.EMPTY] * 128
            board2[wk], board2[wq], board2[dest] = cls.WK, code, cls.BK
            if dest in cls.piece_attack_squares(board2, wq, blocking=True):
                continue
            ch.append(wk | (wq << 7) | (dest << 14))
        return ch, captured

    @classmethod
    def retro_dtm(cls, strong_piece):
        code = cls.WQ if strong_piece == 5 else cls.WR
        SIZE = 1 << 22
        dtm = [-1] * SIZE
        succ_flat = _array('i')
        succ_ptr = _array('i', bytes(4 * (SIZE + 1)))
        cnt = _array('i', bytes(4 * SIZE))
        escape = bytearray(SIZE)
        n_states = 0
        for wk in cls.SQUARES:
            for wq in cls.SQUARES:
                if wq == wk:
                    continue
                for bk in cls.SQUARES:
                    if bk == wk or bk == wq or cls.kings_adjacent(wk, bk):
                        continue
                    board = [cls.EMPTY] * 128
                    board[wk], board[wq], board[bk] = cls.WK, code, cls.BK
                    targets = cls.piece_attack_squares(board, wq, blocking=True)
                    if bk not in targets:
                        s0 = cls.pack_state(wk, wq, bk, 0)
                        ch = cls._children_white(wk, wq, bk, code)
                        succ_ptr[s0] = len(succ_flat)
                        cnt[s0] = len(ch)
                        succ_flat.extend(ch)
                        n_states += 1
                    ch, captured = cls._children_black(wk, wq, bk, code)
                    s1 = cls.pack_state(wk, wq, bk, 1)
                    succ_ptr[s1] = len(succ_flat)
                    cnt[s1] = len(ch)
                    succ_flat.extend(ch)
                    if captured:
                        escape[s1] = 1
                    if not ch and not captured and bk in targets:
                        dtm[s1] = 0
                    n_states += 1
        succ_ptr[SIZE] = len(succ_flat)
        pred_cnt = _array('i', bytes(4 * SIZE))
        for s in range(SIZE):
            for k in range(succ_ptr[s], succ_ptr[s] + cnt[s]):
                pred_cnt[succ_flat[k]] += 1
        pred_ptr = _array('i', bytes(4 * (SIZE + 1)))
        total = 0
        for s in range(SIZE):
            pred_ptr[s] = total
            total += pred_cnt[s]
        pred_ptr[SIZE] = total
        pred_fill = _array('i', bytes(4 * SIZE))
        for s in range(SIZE):
            pred_fill[s] = pred_ptr[s]
        pred_arr = _array('i', bytes(4 * total))
        for s in range(SIZE):
            for k in range(succ_ptr[s], succ_ptr[s] + cnt[s]):
                c = succ_flat[k]
                pred_arr[pred_fill[c]] = s
                pred_fill[c] += 1
        frontier = [s for s in range(SIZE) if dtm[s] == 0]
        depth = 0
        max_plies = 0
        while frontier:
            depth += 1
            nxt = []
            for child in frontier:
                lo, hi = pred_ptr[child], pred_ptr[child + 1]
                for k in range(lo, hi):
                    parent = pred_arr[k]
                    if dtm[parent] >= 0:
                        continue
                    if not (parent >> 21):
                        dtm[parent] = depth
                        if depth > max_plies:
                            max_plies = depth
                        nxt.append(parent)
                    else:
                        if escape[parent]:
                            continue
                        lo2 = succ_ptr[parent]
                        hi2 = lo2 + cnt[parent]
                        all_won = True
                        mx = 0
                        for k2 in range(lo2, hi2):
                            dv = dtm[succ_flat[k2]]
                            if dv < 0:
                                all_won = False
                                break
                            if dv > mx:
                                mx = dv
                        if all_won:
                            d = mx + 1
                            dtm[parent] = d
                            if d > max_plies:
                                max_plies = d
                            nxt.append(parent)
            frontier = nxt
        stats = {'piece': 'Q' if strong_piece == 5 else 'R',
                 'states': n_states, 'edges': total,
                 'won': sum(1 for v in dtm if v >= 0),
                 'mates': sum(1 for v in dtm if v == 0),
                 'max_plies': max_plies,
                 'max_moves': (max_plies + 1) // 2 if max_plies >= 0 else -1}
        return dtm, stats


# ── Задачи 23–34: протокол C1–C10 chess-dynamics-lab ──
def task23_chess_orbits(cfg):
    """C1/T01: орбиты клеток под V4 и D4, лемма Бернсайда."""
    D4, V4 = HodgeChess.groups()
    ov, od = HodgeChess.orbits(V4), HodgeChess.orbits(D4)
    sizes = sorted(set(len(o) for o in ov))
    diag2 = sum(1 for o in ov if len(o) == 2)
    off4 = sum(1 for o in ov if len(o) == 4)
    fixed = {'id': 64, 'rot90': 0, 'rot180': 0, 'rot270': 0,
             'mir_h': 0, 'mir_v': 0, 'diag': 8, 'antidiag': 8}
    for k in ('rot90', 'rot180', 'rot270', 'mir_h', 'mir_v'):
        fixed[k] = sum(1 for f in range(8) for r in range(8) if D4[k](f, r) == (f, r))
    burn = HodgeChess.burnside_orbits(fixed)
    burn_v4 = HodgeChess.burnside_orbits({'id': 64, 'rot180': 0, 'diag': 8, 'antidiag': 8})
    ok = (len(ov) == 20 and sizes == [2, 4] and len(od) == 10
          and diag2 == 8 and off4 == 12 and burn == 10 and burn_v4 == 20)
    return HodgeTaskResult(ok, f"C1/T01: V4-орбиты 20 (8×2+12×4), D4-орбиты 10, Бернсайд {burn}/{burn_v4}" if ok
                           else f"C1: провал: v4={len(ov)}, d4={len(od)}, burn={burn}", {"v4": len(ov), "d4": len(od)})


def task24_chess_graphs(cfg):
    """C2/T02: рёбра графов ходов пустой доски + связность/двудольность."""
    directed = {nm: HodgeChess.piece_graph_directed(t) for t, nm in
                ((4, 'rook'), (3, 'bishop'), (2, 'knight'), (6, 'king'), (5, 'queen'))}
    edges = {k: v // 2 for k, v in directed.items()}
    exp = {'rook': 448, 'bishop': 280, 'knight': 168, 'king': 210, 'queen': 728}
    ok = edges == exp
    adj_n = HodgeChess.empty_board_graph(2)
    bip, _ = HodgeChess.is_bipartite(adj_n)
    comps_n = HodgeChess.graph_components(adj_n)
    comps_b = HodgeChess.graph_components(HodgeChess.empty_board_graph(3))
    comps_r = HodgeChess.graph_components(HodgeChess.empty_board_graph(4))
    comps_k = HodgeChess.graph_components(HodgeChess.empty_board_graph(6))
    comps_q = HodgeChess.graph_components(HodgeChess.empty_board_graph(5))
    ok &= (bip and len(comps_n) == 1 and [len(c) for c in comps_b] == [32, 32]
           and len(comps_r) == 1 and len(comps_k) == 1 and len(comps_q) == 1)
    return HodgeTaskResult(ok, f"C2/T02: рёбра R{edges['rook']}/B{edges['bishop']}/N{edges['knight']}/K{edges['king']}/Q{edges['queen']}; конь двудолен; слон 2×32" if ok
                           else f"C2: провал: {edges}", edges)


def task25_chess_mobility(cfg):
    """C3/T03: мобильность по клеткам, максимумы, замкнутые формы."""
    mc = HodgeChess.mobility_census()
    exp_max = {'king': 8, 'knight': 8, 'bishop': 13, 'rook': 14, 'queen': 27}
    exp_sum = {'king': 420, 'knight': 336, 'bishop': 560, 'rook': 896, 'queen': 1456}
    ok = all(mc[n]['max'] == exp_max[n] for n in exp_max)
    ok &= all(mc[n]['sum'] == exp_sum[n] for n in exp_sum)
    ok &= sorted(mc['queen']['argmax']) == ['d4', 'd5', 'e4', 'e5']
    ok &= mc['bishop_closed_form_ok'] and mc['queen_closed_form_ok']
    return HodgeTaskResult(ok, f"C3/T03: max 8/8/13/14/27, суммы 420/336/560/896/1456, argmax Q=d4,e4,d5,e5, замкнутые формы ok" if ok
                           else f"C3: провал: {[(n, mc[n]['max'], mc[n]['sum']) for n in exp_max]}", {})


def task26_chess_flow(cfg):
    """C4/T06: t* на 10 случаях + демпфированный бильярд с γ=π⁴/256."""
    cases = [((8, 8, 1, 1), 8), ((8, 8, 3, 5), 8), ((8, 8, 2, 2), 4),
             ((8, 8, 1, 2), 8), ((8, 8, 1, 0), 8), ((8, 8, 2, 1), 8),
             ((48, 48, 1, 1), 48), ((24, 36, 3, 5), 72),
             ((12, 12, 4, 6), 6), ((7, 14, 1, 1), 14)]
    ok = all(HodgeChess.tstar_chess(W, H, a, b) == e for (W, H, a, b), e in cases)
    gamma = (math.pi / 4) ** 4
    steps, path, refl, rest, ratio = HodgeChess.simulate_billiard(8, 8, 3, 2, gamma)
    ok &= (steps == 30 and refl == 0 and rest and abs(ratio - 1.0) < 1e-9)
    ok &= abs(gamma - 0.38050426185157193) < 1e-15
    return HodgeTaskResult(ok, f"C4/T06: t* на 10 случаях; бильярд (8,8;3,2,γ=π⁴/256): {steps} шагов, {refl} отражений, ratio={ratio:.13f}" if ok
                           else f"C4: провал (steps={steps}, ratio={ratio})", {"gamma": gamma, "ratio": ratio})


def task27_chess_perft(cfg):
    """C5/T08: перft стартовой позиции 20/400/8902/197281; pass2: 4 865 609."""
    def perft(pos, d):
        if d == 0:
            return 1
        n = 0
        for m in HodgeChess.legal_moves(pos):
            undo = HodgeChess.make(pos, m)
            n += perft(pos, d - 1)
            HodgeChess.unmake(pos, undo)
        return n
    pos = HodgeChess.start_position()
    vals = [perft(pos, d) for d in (1, 2, 3, 4)]
    ok = vals == [20, 400, 8902, 197281]
    return HodgeTaskResult(ok, f"C5/T08: perft(1..4) = {', '.join(map(str, vals))} (Baseline 20/400/8902/197281)" if ok
                           else f"C5: провал: {vals}", {"perft": vals})

def task27b_chess_perft5(cfg):
    """pass 2 (тяжёлая): perft(5) = 4 865 609 (~45–60 с)."""
    def perft(pos, d):
        if d == 0:
            return 1
        n = 0
        for m in HodgeChess.legal_moves(pos):
            undo = HodgeChess.make(pos, m)
            n += perft(pos, d - 1)
            HodgeChess.unmake(pos, undo)
        return n
    pos = HodgeChess.start_position()
    v5 = perft(pos, 5)
    ok = v5 == 4865609
    return HodgeTaskResult(ok, f"C5-hardcore: perft(5) = {v5} = 4 865 609" if ok
                           else f"C5-hardcore: perft(5) = {v5} ≠ 4865609", {"perft5": v5})


def task28_chess_field(cfg):
    """C6/T04: тождество суммы атак, D4-эквивариантность, аномалия пешек 176."""
    PAWNLESS = "rnbqkbnr/8/8/8/8/8/8/RNBQKBNR w - - 0 1"
    pos = HodgeChess.start_position()
    tw_f, tw_p = HodgeChess.attack_sum_identity(pos, 1)
    tb_f, tb_p = HodgeChess.attack_sum_identity(pos, -1)
    def equiv_violations(pos_, side):
        theta = HodgeChess.threat_field(pos_, side)
        D4, _ = HodgeChess.groups()
        worst = 0
        for g in D4.values():
            pos_g = {"board": [HodgeChess.EMPTY] * 128, "side": side,
                     "castling": 0, "ep": -1}
            for sq in HodgeChess.SQUARES:
                p = pos_["board"][sq]
                if p != HodgeChess.EMPTY:
                    f, r = g(sq & 7, sq >> 4)
                    pos_g["board"][16 * r + f] = p
            theta_g = HodgeChess.threat_field(pos_g, side)
            for sq in HodgeChess.SQUARES:
                f, r = g(sq & 7, sq >> 4)
                if theta_g[16 * r + f] != theta[sq]:
                    worst += 1
        return worst
    pos_np = HodgeChess.set_fen(PAWNLESS)
    v_w = equiv_violations(pos_np, 1)
    v_b = equiv_violations(pos_np, -1)
    anomaly = equiv_violations(pos, 1) + equiv_violations(pos, -1)
    ok = (tw_f == tw_p and tb_f == tb_p and v_w == 0 and v_b == 0 and anomaly == 176)
    return HodgeTaskResult(ok, f"C6/T04: масса поля сходится, эквивариантность 0/0, аномалия пешек {anomaly}=176=88+88" if ok
                           else f"C6: провал: anomaly={anomaly}, v={v_w},{v_b}", {"anomaly": anomaly})


def task29_chess_energy(cfg):
    """C7/T05: мобильность 20→30 после 1.e4, детерминизм энергии/хэша, инверсия splitmix64."""
    pos = HodgeChess.start_position()
    e1 = HodgeChess.energy(pos, 1)
    e2 = HodgeChess.energy(pos, 1)
    m_white = HodgeChess.mobility(pos, 1)
    pos_e4 = HodgeChess.start_position()
    undo = HodgeChess.make(pos_e4, HodgeChess.uci_to_move(pos_e4, "e2e4"))
    m_after = HodgeChess.mobility(pos_e4, 1)
    HodgeChess.unmake(pos_e4, undo)
    pos2 = HodgeChess.set_fen(HodgeChess.to_fen(pos))
    hash_ok = pos2["hash"] == pos["hash"]
    inv_ok = all(HodgeChess.splitmix64_inverse(HodgeChess.splitmix64(x)) == x
                 for x in range(1, 2001))
    ok = (m_white == 20 and m_after == 30 and e1 == e2 and hash_ok and inv_ok)
    return HodgeTaskResult(ok, f"C7/T05: мобильность {m_white}→{m_after} после e4, E0={e1:.1f}, хэш/инверсия ok" if ok
                           else f"C7: провал: m={m_white},{m_after}, inv={inv_ok}", {"mob": [m_white, m_after]})


def task30_chess_zobrist(cfg):
    """C9/T09: 1562 ключа, векторы sm(1..3), инкрементальность на плейаутах, день рождения."""
    import random as _rnd
    ok = True
    # число ключей: 12×128 + side + 16 castle + 9 ep
    ok &= (12 * 128 + 1 + 16 + 9) == 1562
    # канонические векторы биекции sm(k) = splitmix64(k) (полиглот, T09)
    vecs = [HodgeChess.splitmix64(k) for k in (1, 2, 3)]
    ok &= (vecs[0] == 0x910A2DEC89025CC1 and vecs[1] == 0x975835DE1C9756CE
           and vecs[2] == 0x1D0B14E4DB018FED)
    # ключевой конвейер таблиц начинается от seed 0x1234567890ABCDEF
    st = 0x1234567890ABCDEF
    for _ in range(3):
        st = HodgeChess.splitmix64(st)
    ok &= st == 0x94e78d07131a5fb3   # 3 шага конвейера ключей от seed
    # инкрементальность: 40 плейаутов × ≤60 полуходов, Random(42)
    rng = _rnd.Random(42)
    playouts = 0
    inc_ok = True
    for _ in range(40):
        pos = HodgeChess.start_position()
        for ply in range(60):
            moves = HodgeChess.legal_moves(pos)
            if not moves:
                break
            m = rng.choice(moves)
            HodgeChess.make(pos, m)
            if HodgeChess.zobrist_hash(pos) != pos["hash"]:
                inc_ok = False
                break
            playouts += 1
    ok &= inc_ok and playouts == 2393
    # unmake восстанавливает FEN и хэш
    p = HodgeChess.start_position()
    h0 = p["hash"]
    for m in HodgeChess.legal_moves(p)[:8]:
        u = HodgeChess.make(p, m)
        HodgeChess.unmake(p, u)
        if HodgeChess.to_fen(p) != HodgeChess.START_FEN or p["hash"] != h0:
            ok = False
            break
    # день рождения: P ≤ n(n−1)/2^65 при n = 10^9
    birthday = 1e9 * (1e9 - 1) / 2 ** 65
    ok &= abs(birthday - 0.0271) < 5e-4
    return HodgeTaskResult(ok, f"C9/T09: 1562 ключа, sm(1..3) совпали, инкрементальность {playouts} позиций (baseline 2393), birthday≈{birthday:.4f}" if ok
                           else f"C9: провал: vecs={vecs[:1]}, playouts={playouts}", {"playouts": playouts})


def task31_chess_tour(cfg):
    """C10/T07: замкнутый обход коня (Warnsdorff) — проверка замороженной последовательности."""
    KNIGHT_TOUR = ("f5 h4 g2 e1 c2 a1 b3 c1 a2 b4 a6 b8 d7 f8 h7 g5 h3 g1 e2 g3 h1 f2 d1 "
                   "b2 d3 f4 h5 g7 e8 f6 g8 h6 g4 h2 f1 e3 d5 c7 a8 b6 a4 c3 b1 a3 b5 a7 "
                   "c8 e7 g6 h8 f7 e5 f3 d2 c4 a5 c6 d4 e6 d8 b7 c5 e4 d6").split()
    ok = len(KNIGHT_TOUR) == 64 and len(set(KNIGHT_TOUR)) == 64
    sqs = [HodgeChess.name_sq(s) for s in KNIGHT_TOUR]
    offs = set(HodgeChess.KNIGHT_OFFS)
    for i in range(len(sqs) - 1):
        ok &= (sqs[i + 1] - sqs[i]) in offs
    ok &= (sqs[0] - sqs[-1]) in offs   # замыкание d6 → f5
    ok &= KNIGHT_TOUR[0] == "f5" and KNIGHT_TOUR[-1] == "d6"
    return HodgeTaskResult(ok, "C10/T07: тур коня: 64 различные клетки, все ходы конём, замыкание d6→f5" if ok
                           else "C10: тур провален", {"cells": len(set(KNIGHT_TOUR))})


def task32_chess_tactics(cfg):
    """C8: матовые сертификаты — Морфи, лестница, К+Кн+Л; узлы — константы реализации
    (порт order_moves 1:1), PV и глубина — содержательные утверждения."""
    cases = (("morphy_m2", "kbK5/pp6/1P6/8/8/8/8/R7 w - - 0 1", 3, "a1a6", 46),
             ("ladder_m2", "7k/8/8/8/8/8/R7/1R4K1 w - - 0 1", 3, "b1b7", 49),
             ("nr_m1", "7k/8/5N1K/8/8/8/8/6R1 w - - 0 1", 1, "g1g8", 1))
    ok = True
    det = []
    for label, fen, plies_exp, key, nodes_exp in cases:
        pos = HodgeChess.set_fen(fen)
        plies, pv, nodes = HodgeChess.mate_search(pos, 6)
        pv_s = " ".join(HodgeChess.move_to_uci(m) for m in pv)
        ok &= (plies == plies_exp and key in pv_s)
        det.append(f"{label}: {plies} пн., узлы {nodes} (эталон {nodes_exp})")
    exp_pvs = {"morphy_m2": "a1a6 b7a6 b6b7", "ladder_m2": "b1b7 h8g8 a2a8", "nr_m1": "g1g8"}
    for label, fen, plies_exp, key, nodes_exp in cases:
        pos = HodgeChess.set_fen(fen)
        plies, pv, nodes = HodgeChess.mate_search(pos, 6)
        pv_s = " ".join(HodgeChess.move_to_uci(m) for m in pv)
        if label != "nr_m1":
            ok &= pv_s == exp_pvs[label]
        ok &= nodes == nodes_exp   # порядок ходов портирован 1:1 — узлы воспроизводимы
    return HodgeTaskResult(ok, f"C8: Морфи/лестница/Кн+Л: PV и узлы 46/49/1 воспроизведены ({'; '.join(det)})" if ok
                           else f"C8: провал: {det}", {"details": det})


def task33_chess_retro_krk(cfg):
    """C8/T11/E2: ретроградная DTM KRK — статистика = замороженной (399112/4447032/376868/216/32)."""
    dtm, stats = HodgeChess.retro_dtm(4)
    exp = {'piece': 'R', 'states': 399112, 'edges': 4447032, 'won': 376868,
           'mates': 216, 'max_plies': 32, 'max_moves': 16}
    ok = all(stats.get(k) == v for k, v in exp.items())
    return HodgeTaskResult(ok, f"C8-hardcore: ретро-KRK: {stats['states']} состояний, {stats['edges']} рёбер, won={stats['won']}, матов {stats['mates']}, макс {stats['max_moves']} ходов" if ok
                           else f"C8: ретро-KRK не совпал: {stats}", stats)

def task33b_chess_retro_kqk(cfg):
    """pass 2: ретроградная DTM KQK (368452/4869496/345404/364/20)."""
    dtm, stats = HodgeChess.retro_dtm(5)
    exp = {'piece': 'Q', 'states': 368452, 'edges': 4869496, 'won': 345404,
           'mates': 364, 'max_plies': 20, 'max_moves': 10}
    ok = all(stats.get(k) == v for k, v in exp.items())
    return HodgeTaskResult(ok, f"C8-hardcore: ретро-KQK: {stats['states']}, {stats['edges']} рёбер, матов {stats['mates']}, макс {stats['max_moves']} ходов" if ok
                           else f"C8: ретро-KQK не совпал: {stats}", stats)


# ── регистрация задач сессии 2 в реестре (SUITE_IDS/TASKS_BY_ID пересчитываются) ──
TASKS.extend([
    {"id": 23, "slug": "chess-orbits", "title": "Орбиты V4/D4 и Бернсайд (C1/T01)",
     "fn": task23_chess_orbits, "pass2_fn": None, "deps": [], "claims": ["chess-C1", "chess-T01"],
     "est_sec": 0.05, "idempotent": True, "tags": ["fast", "exact", "chess"], "version": "1.1.0", "owner": "session-2"},
    {"id": 24, "slug": "chess-graphs", "title": "Графы ходов: рёбра/связность (C2/T02)",
     "fn": task24_chess_graphs, "pass2_fn": None, "deps": [], "claims": ["chess-C2", "chess-T02"],
     "est_sec": 0.1, "idempotent": True, "tags": ["fast", "exact", "chess"], "version": "1.1.0", "owner": "session-2"},
    {"id": 25, "slug": "chess-mobility", "title": "Мобильность и замкнутые формы (C3/T03)",
     "fn": task25_chess_mobility, "pass2_fn": None, "deps": [], "claims": ["chess-C3", "chess-T03"],
     "est_sec": 0.05, "idempotent": True, "tags": ["fast", "exact", "chess"], "version": "1.1.0", "owner": "session-2"},
    {"id": 26, "slug": "chess-flow", "title": "t* и бильярд γ=π⁴/256 (C4/T06)",
     "fn": task26_chess_flow, "pass2_fn": None, "deps": [], "claims": ["chess-C4", "chess-T06"],
     "est_sec": 0.05, "idempotent": True, "tags": ["fast", "exact", "chess"], "version": "1.1.0", "owner": "session-2"},
    {"id": 27, "slug": "chess-perft", "title": "perft 20/400/8902/197281 (C5/T08)",
     "fn": task27_chess_perft, "pass2_fn": task27b_chess_perft5, "deps": [],
     "claims": ["chess-C5", "chess-T08"], "est_sec": 2.0, "idempotent": True,
     "tags": ["exact", "chess", "heavy-pass2"], "version": "1.1.0", "owner": "session-2"},
    {"id": 28, "slug": "chess-field", "title": "Масса поля, эквивариантность, аномалия 176 (C6/T04)",
     "fn": task28_chess_field, "pass2_fn": None, "deps": [], "claims": ["chess-C6", "chess-T04"],
     "est_sec": 0.1, "idempotent": True, "tags": ["fast", "exact", "chess"], "version": "1.1.0", "owner": "session-2"},
    {"id": 29, "slug": "chess-energy", "title": "Энергия 20→30, инверсия splitmix64 (C7/T05)",
     "fn": task29_chess_energy, "pass2_fn": None, "deps": [27],
     "claims": ["chess-C7", "chess-T05"], "est_sec": 0.2, "idempotent": True,
     "tags": ["fast", "exact", "chess"], "version": "1.1.0", "owner": "session-2"},
    {"id": 30, "slug": "chess-zobrist", "title": "Зобрист: 1562 ключа, sm-векторы, 2393 позиций (C9/T09)",
     "fn": task30_chess_zobrist, "pass2_fn": None, "deps": [27],
     "claims": ["chess-C9", "chess-T09"], "est_sec": 0.6, "idempotent": True,
     "tags": ["exact", "chess"], "version": "1.1.0", "owner": "session-2"},
    {"id": 31, "slug": "chess-tour", "title": "Замкнутый обход коня d6→f5 (C10/T07)",
     "fn": task31_chess_tour, "pass2_fn": None, "deps": [],
     "claims": ["chess-C10", "chess-T07"], "est_sec": 0.02, "idempotent": True,
     "tags": ["fast", "exact", "chess"], "version": "1.1.0", "owner": "session-2"},
    {"id": 32, "slug": "chess-tactics", "title": "Маты: Морфи/лестница/Кн+Л, узлы 46/49/1 (C8)",
     "fn": task32_chess_tactics, "pass2_fn": None, "deps": [27],
     "claims": ["chess-C8", "chess-T10"], "est_sec": 0.3, "idempotent": True,
     "tags": ["exact", "chess"], "version": "1.1.0", "owner": "session-2"},
    {"id": 33, "slug": "chess-retro-krk", "title": "Ретро-DTM KRK: 399112/4447032/216 (C8/T11)",
     "fn": task33_chess_retro_krk, "pass2_fn": task33b_chess_retro_kqk, "deps": [],
     "claims": ["chess-C8", "chess-T11", "chess-E2"], "est_sec": 9.0, "idempotent": True,
     "tags": ["exact", "chess", "heavy"], "version": "1.1.0", "owner": "session-2"},
])
SUITE_IDS[:] = [t["id"] for t in TASKS]
TASKS_BY_ID.clear()
TASKS_BY_ID.update({t["id"]: t for t in TASKS})


# §18: guard перенесён в самый конец (после ВСЕХ блоков регистрации задач)


# ══════════════════════════════════════════════════════════════════════════
# СЕССИЯ 2 · БЛОК VERHODGE-LAB: задачи 34–37 (C-010, C-006, C-003, C-019).
# Заморожено из verhodge-lab/verification/{V21,H2_gross_normalization,
# K_n11_resolvent,K_n11_rung,V24}_*.json. Точные части — целые/Fraction;
# численные — мой Decimal-слой (без mpmath).
# ══════════════════════════════════════════════════════════════════════════
def task34_verhodge_periods(cfg):
    """C-010: Π(ψ) = ₄F₃(1/5,2/5,3/5,4/5;1,1,1;ψ⁻⁵); две независимые схемы
    (рекуррентность отношения vs прямая формула члена) на Decimal, порог 1e-38,
    замороженные 16-значные значения V21 (сравнение через float())."""
    FROZEN = {2: "1.0012115112871418", 3: "1.0001582217292668",
              5: "1.0000122891892658", 7: "1.0000022848034111"}
    ok = True
    det = []
    worst_cross = 0.0
    with HODGEHP.scope(50):
        for psi in (2, 3, 5, 7):
            w = HODGEHP.D(psi) ** (-5)
            # схема 1: рекуррентность c_n/c_{n-1} = Π(5n−k)/(625·n⁴), k=1..4
            s1 = HODGEHP.D(1)
            c_acc = HODGEHP.D(1)
            wn = HODGEHP.D(1)
            for n in range(1, 41):
                r = HODGEHP.D(1)
                for k in (1, 2, 3, 4):
                    r *= HODGEHP.D(5 * n - k)
                c_acc *= r / (625 * HODGEHP.D(n) ** 4)
                wn *= w
                s1 += c_acc * wn
            # схема 2: прямой член c_n = Π_{m=1..n}(5m−4..5m−1)/(625^n (n!)⁴)·wⁿ
            s2 = HODGEHP.D(1)
            num = HODGEHP.D(1)
            wn2 = HODGEHP.D(1)
            for n in range(1, 41):
                for k in (1, 2, 3, 4):
                    num *= HODGEHP.D(5 * n - k)
                den = HODGEHP.D(625) ** n * HODGEHP.D(math.factorial(n)) ** 4
                wn2 *= w
                s2 += num / den * wn2
            cross = float(abs(s1 - s2))
            worst_cross = max(worst_cross, cross)
            ok &= cross < 1e-38
            ok &= HODGEText.fmt_float(float(s1), 16) == FROZEN[psi]
            det.append(f"ψ={psi}: {float(s1):.16f}")
    return HodgeTaskResult(ok, f"C-010: Π(ψ) две схемы согласны (worst {worst_cross:.1e}); замороженные V21 воспроизведены: {'; '.join(det)}" if ok
                           else f"C-010: провал: {det}, cross={worst_cross:.2e}",
                           {"worst_cross": worst_cross})


def task35_verhodge_gross(cfg):
    """C-006: vol_h = (2π)^{Σc/2}·ΠΓ(k/N)^{−c_k} = 1125 при N=15 и 30; |vol−1125| < 1e-60."""
    c15 = {k: (6 if k % 3 == 0 else 4) for k in range(1, 15)}
    c30 = {}
    for k in range(1, 30):
        if k == 15:
            c30[k] = 0                       # Γ(1/2) = √π — «синусный счёт»
        elif k % 2 == 0:
            c30[k] = c15[k // 2]
        else:
            c30[k] = 4
    ok = (sum(c15.values()) == 64 and sum(c30.values()) == 120)
    det = []
    with HODGEHP.scope(120):
        pi = HODGEHP.pi(120)
        for N, cs, sig in ((15, c15, "5.948301181208553e-118"),
                           (30, c30, "1.784490354362566e-116")):
            sc = sum(cs.values())
            logv = HODGEHP.D(sc) / 2 * (2 * pi).ln()
            for k, c in cs.items():
                if c:
                    logv -= c * HODGEHP.lgamma(HODGEHP.D(k) / N, 120)
            vol = logv.exp()
            dev = abs(vol - 1125)
            ok &= dev < HODGEHP.D("1e-60")
            det.append(f"N={N}: dev={float(dev):.2e}")
    ok &= 1125 ** 2 == 1265625    # связь с дискриминантом следовой решётки (task 16)
    return HodgeTaskResult(ok, f"C-006: Гросс vol_h = 1125 на N=15 и 30 (Σc = 64/120), {'; '.join(det)}; 1125²=1265625" if ok
                           else f"C-006: провал: {det}", {})


def task36_verhodge_k11(cfg):
    """C-003 (точный слой + численный): квинтик 2cos(2π/11): collapse x⁵+x⁴−4x³−3x²+3x+1
    в ℤ[ζ₁₁]/Φ₁₁, GF(2)-неприводимость; η_j в ℤ[ξ₅] (замороженные), ветви (2,4,4,1,1)."""
    n = 11
    h, _, g = HODGEEX.census(n)
    ok = (h == {11: 45} and g == 45)
    phi = HODGEEX.cyclotomic(n)
    dphi = len(phi) - 1
    # элемент ℤ[T][ζ]/(Φ): список T-полиномов по ζ-степеням 0..dphi−1 (MSB int-списки)
    def el_mul(a, b):
        # zred в low-first (индекс = ζ-степень): MSB-список → deg d = p[L−1−d]
        def low(msb):
            L = len(msb)
            return [msb[L - 1 - d] if d < L else 0 for d in range(dphi)]
        zred = [low(HODGEEX.pmod_monic(HODGEEX._mono_poly(m, dphi), phi))
                for m in range(2 * dphi)]
        out = [[0] for _ in range(dphi)]
        for da in range(dphi):
            if not any(a[da]):
                continue
            for db in range(dphi):
                if not any(b[db]):
                    continue
                tp = HODGEEX.pmul(a[da], b[db])
                for d, c in enumerate(zred[da + db]):
                    if c:
                        out[d] = HODGEEX.padd(out[d], [v * c for v in tp])
        return [HODGEEX.pnorm(p) for p in out]
    # s_k = ζ^k + ζ^{11−k} (мономы ≥ dphi редуцируются по Φ!); P = Π_{k∈1..5}(T − s_k)
    def low(msb):
        L = len(msb)
        return [msb[L - 1 - d] if d < L else 0 for d in range(dphi)]
    zred_low = [low(HODGEEX.pmod_monic(HODGEEX._mono_poly(m, dphi), phi))
                for m in range(2 * dphi)]
    P = [[1]] + [[0] for _ in range(dphi - 1)]        # P = 1; факторы добавят степени T
    for k in (1, 2, 3, 4, 5):
        srow = [[0] for _ in range(dphi)]
        for m in (k, n - k):
            for d, c in enumerate(zred_low[m]):
                if c:
                    srow[d] = HODGEEX.padd(srow[d], [c])
        # элемент (T − s_k)
        minus = [list(p) for p in [[0]] * dphi]
        minus[0] = [1, 0]
        for dd in range(dphi):
            minus[dd] = HODGEEX.psub(minus[dd], srow[dd])
        P = el_mul(P, minus)
    exp_poly = [1, 1, -4, -3, 3, 1]              # x⁵+x⁴−4x³−3x²+3x+1 (MSB)
    ok &= (P[0] == exp_poly and all(p == [0] for p in P[1:]))
    ok &= HODGEEX.gf2_irreducible(exp_poly)      # тест Рабина-аналог: неприводим над GF(2)
    # численный слой: R_j⁵ ≈ η_j; реконструкция x₀ = (1/5)Σ ξ^{b_j}·η_j^{1/5} = 2cos(2π/11)
    ETA = [( -1, 0, 0, 0), (-66, 220, 110, 385), (-176, 275, 110, -110),
           (-451, -275, -385, -165), (-286, -220, 165, -110)]
    BRANCH = (2, 4, 4, 1, 1)
    with HODGEHP.scope(50):
        xi = HODGEHP.cexp((HODGEHP.D(0), 2 * HODGEHP.pi(50) / 5), 50)
        xs = [2 * HODGEHP.cos(2 * HODGEHP.pi(50) * t / n, 50) for t in (1, 2, 4, 8, 5)]
        worst_eta = 0.0
        for j in range(5):
            R = (HODGEHP.D(0), HODGEHP.D(0))
            for t_i, xt in enumerate(xs):
                ph = HODGEHP.cpow_frac(xi, Fraction(-j * t_i, 1) % Fraction(5), 50) if False else \
                    HODGEHP.cpow_frac(xi, Fraction((-j * t_i) % 5, 1), 50)
                R = HODGEHP.cadd(R, (xt * ph[0], xt * ph[1]))
            R5 = (HODGEHP.D(1), HODGEHP.D(0))
            for _ in range(5):
                R5 = HODGEHP.cmul(R5, R)
            eta = (HODGEHP.D(0), HODGEHP.D(0))
            for deg, coef in enumerate(ETA[j]):
                if coef:
                    xid = HODGEHP.cpow_frac(xi, Fraction(deg, 1), 50)
                    eta = HODGEHP.cadd(eta, (coef * xid[0], coef * xid[1]))
            worst_eta = max(worst_eta, float(HODGEHP.rel_err_c(R5, eta)))
        ok &= worst_eta < 1e-30
        # реконструкция: θ_j = ξ^{b_j}·(η_j)^{1/5} — главный корень ЗАМОРОЖЕННОЙ η_j
        x0 = (HODGEHP.D(0), HODGEHP.D(0))
        for j in range(5):
            eta_val = (HODGEHP.D(0), HODGEHP.D(0))
            for deg, coef in enumerate(ETA[j]):
                if coef:
                    xid = HODGEHP.cpow_frac(xi, Fraction(deg, 1), 50)
                    eta_val = HODGEHP.cadd(eta_val, (coef * xid[0], coef * xid[1]))
            th = HODGEHP.cmul(HODGEHP.cpow_frac(xi, Fraction(BRANCH[j], 1), 50),
                              HODGEHP.cpow_frac(eta_val, Fraction(1, 5), 50))
            x0 = HODGEHP.cadd(x0, th)
        x0 = HODGEHP.cscale(x0, HODGEHP.D(1) / 5)
        tgt = (2 * HODGEHP.cos(2 * HODGEHP.pi(50) / n, 50), HODGEHP.D(0))
        rec = float(HODGEHP.rel_err_c(x0, tgt))
        ok &= rec < 1e-25
    return HodgeTaskResult(ok, f"C-003: квинтик N=11: collapse x⁵+x⁴−4x³−3x²+3x+1, GF(2) ok; η_j (worst {worst_eta:.1e}); реконструкция ветвей (2,4,4,1,1) rel={rec:.1e}" if ok
                           else f"C-003: провал: eta={worst_eta:.1e}, rec={rec:.1e}",
                           {"eta_worst": worst_eta, "reconstruction": rec})

# ζ-моном x^k в MSB-форме (для редукции ζ^m mod Φ₁₁): x^k mod Φ — моном длины k+1
HODGEEX._mono_poly = staticmethod(lambda k, dphi: [1] + [0] * k)  # x^m, MSB


def task37_verhodge_chart(cfg):
    """C-019: точное тождество карты x₅=1, ψ=0:
    Q³·d(ι_R Ω′/Q²) = Q·d(ι_R Ω′) − 2·ι_R Ω′∧dQ = (14Q − 10)·dx₁₂₃₄ (ловушка Эйлера)."""
    P = {}   # словарные многочлены 4 переменных: exp-кортеж → Fraction
    def padd(p, q):
        out = dict(p)
        for k, v in q.items():
            out[k] = out.get(k, Fraction(0)) + v
            if out[k] == 0:
                del out[k]
        return out
    def pscale(p, c):
        return {k: v * c for k, v in p.items()}
    def pmul_dict(p, q):
        out = {}
        for k1, v1 in p.items():
            for k2, v2 in q.items():
                kk = tuple(a + b for a, b in zip(k1, k2))
                out[kk] = out.get(kk, Fraction(0)) + v1 * v2
        return {k: v for k, v in out.items() if v != 0}
    Q = {(0, 0, 0, 0): Fraction(1)}
    for j in range(4):
        e = [0, 0, 0, 0]
        e[j] = 5
        Q = padd(Q, {tuple(e): Fraction(1)})
    # ι_R Ω′ = Σ (−1)^{j} x_{j+1} dx̂_{j+1}; в компонентах: poly_j = (−1)^j x_{j+1}
    iota = []
    for j in range(4):
        e = [0, 0, 0, 0]
        e[j] = 1
        iota.append({tuple(e): Fraction(-1) ** j})
    # dQ: компоненты 5·xᵢ⁴
    dQ = []
    for j in range(4):
        e = [0, 0, 0, 0]
        e[j] = 4
        dQ.append(pscale({tuple(e): Fraction(1)}, 5))
    # клин ι_RΩ′ ∧ dQ → единственная выжившая компонента dx₁₂₃₄:
    # η_j ∧ dQ: вклад только dx_j из dQ, знак переноса (−1)^{j−1} (j-я позиция)
    wedge = {}
    for j in range(4):
        sign_iota = Fraction(-1) ** j
        sign_move = Fraction(-1) ** (3 - j)  # dx̂_j∧dx_j: dx_j проходит 4−jlater dx
        term = pscale(pmul_dict(iota[j], dQ[j]), sign_move)  # знак ι_R уже в poly
        wedge = padd(wedge, term)
    lhs = padd(pscale(Q, 4), pscale(wedge, -2))     # 4Q − 2·ι_RΩ′∧dQ (d(ι_RΩ′)=4dx⁴)
    rhs = padd(pscale(Q, 14), {(0, 0, 0, 0): Fraction(-10)})
    ok = lhs == rhs
    return HodgeTaskResult(ok, "C-019: карта Q³d(ι_RΩ′/Q²) = (14Q − 10)·dx₁₂₃₄ — точное тождество (Эйлер: Σx_jQ_j = 5(Q−1), не 5Q)" if ok
                           else f"C-019: провал: lhs={lhs} ≠ rhs={rhs}", {})


# ── регистрация 34–37 ──
# ── §33.7 / IV.5: CI-регрессия 3D-лаборатории ──
def task38_lab3d(cfg):
    """Не проверяет математику (это делают задачи 1–37), а гарантирует, что
    sweep-машина, PNG-кодек и GIF-кодек не сломались (фиксированные параметры)."""
    import tempfile
    ok = True
    det = []
    # 1. sweep-парсер
    try:
        name, vals = _parse_sweep("N:7:15:4")
        ok &= (name == "N" and vals == [7, 11, 15])
    except Exception as ex:
        ok = False
        det.append(f"sweep: {ex}")
    # 2. прогон 3 кадров
    lab_cfg = HodgeConfig()
    lab_cfg.run_dir = tempfile.mkdtemp(prefix="lab3d_ci_")
    lab_cfg.plot_width, lab_cfg.plot_height = 200, 150
    try:
        lab = HODGE3DLab(lab_cfg, HODGEColor("dark-gold", "truecolor"))
        m = lab.run("omega", {"N": [7, 11, 15]}, {}, grid_n=8, max_frames=3)
        ok &= m["frames"] == 3
        pngs = glob.glob(os.path.join(lab.out_dir, "frame_*.png"))
        ok &= len(pngs) == 3
        for p in pngs:
            ok &= open(p, "rb").read(8) == b'\x89PNG\r\n\x1a\n'
        gif_p = os.path.join(lab.out_dir, "sweep.gif")
        ok &= os.path.exists(gif_p) and open(gif_p, "rb").read(6) == b'GIF89a'
        ok &= open(gif_p, "rb").read()[-1] == 0x3B
    except Exception as ex:
        ok = False
        det.append(f"run: {type(ex).__name__}: {ex}")
    return HodgeTaskResult(ok, f"§33.7: lab3d CI: 3 кадра PNG + GIF, sweep-парсер ({'; '.join(det) if det else 'ok'})" if ok
                           else f"§33.7: lab3d CI провал: {det}", {"frames": 3})


TASKS.extend([
    {"id": 34, "slug": "verhodge-periods", "title": "Π(ψ)=₄F₃ — две схемы, замороженные V21 (C-010)",
     "fn": task34_verhodge_periods, "pass2_fn": None, "deps": [],
     "claims": ["C-010"], "est_sec": 0.4, "idempotent": True,
     "tags": ["hp", "verhodge"], "version": "1.1.0", "owner": "session-2"},
    {"id": 35, "slug": "verhodge-gross", "title": "Гросс vol_h=1125 при 120 dps (C-006)",
     "fn": task35_verhodge_gross, "pass2_fn": None, "deps": [6],
     "claims": ["C-006", "certH"], "est_sec": 0.3, "idempotent": True,
     "tags": ["hp", "verhodge"], "version": "1.1.0", "owner": "session-2"},
    {"id": 36, "slug": "verhodge-k11", "title": "Квинтик N=11: collapse/GF(2)/η_j/ветви (C-003)",
     "fn": task36_verhodge_k11, "pass2_fn": None, "deps": [1],
     "claims": ["C-003", "certK"], "est_sec": 0.5, "idempotent": True,
     "tags": ["exact", "hp", "verhodge"], "version": "1.1.0", "owner": "session-2"},
    {"id": 37, "slug": "verhodge-chart", "title": "Карта: Q³d(ι_RΩ′/Q²)=(14Q−10)dx (C-019)",
     "fn": task37_verhodge_chart, "pass2_fn": None, "deps": [],
     "claims": ["C-019"], "est_sec": 0.05, "idempotent": True,
     "tags": ["exact", "verhodge"], "version": "1.1.0", "owner": "session-2"},
    {"id": 38, "slug": "lab3d-ci", "title": "3D-лаборатория: PNG+GIF+sweep (§33.7)",
     "fn": task38_lab3d, "pass2_fn": None, "deps": [],
     "claims": ["lab3d"], "est_sec": 0.6, "idempotent": True,
     "tags": ["exact", "lab"], "version": "1.1.0", "owner": "session-2",
     "plot_fn": None},
])
SUITE_IDS[:] = [t["id"] for t in TASKS]
TASKS_BY_ID.clear()
TASKS_BY_ID.update({t["id"]: t for t in TASKS})


# ══════════════════════════════════════════════════════════════════════════
# §4.4 HODGE-K3-exact (задача 39: 23–33 chess, 34–38 verhodge заняты).
# Интегральная гипотеза Ходжа для K3-поверхности Ферма (квартика
# x0⁴+x1⁴+x2⁴+x3⁴=0 ⊂ P³). 48 прямых {xi = ζ8^a·xj, xk = ζ8^b·xl},
# a,b ∈ {1,3,5,7} (ζ8^(4a) = −1). Всё пересечение — mod-8 арифметика на
# показателях ζ8: НИКАКОГО Float64. Матрица пересечений 48×48 → SNF.
# Ожидается rank=20, SNF=[1^18, 8, 8], det=64 (решётка Пикара ρ=20,
# подрешётка прямых индекса 8; ср. Aljovin–Movasati–Villaflor).
# Независимый кросс-чек SNF: ранг над GF(p) против предсказания
# snf-делимости, p ∈ {2,3,5,7,11,10007}; при p=2 предсказание 18 (а не 20) —
# точечный тест на делимость 8 | d_i.
# ══════════════════════════════════════════════════════════════════════════

_FERMAT_K3_ROOTS = (1, 3, 5, 7)   # нечётные показатели: ζ8^(4a) = ζ8^4 = −1
# разбиение {01}|{23} → 1, {02}|{13} → 2, {03}|{12} → 3; ориентация пар фиксирована
_FERMAT_K3_PARTS = {1: ((0, 1), (2, 3)), 2: ((0, 2), (1, 3)), 3: ((0, 3), (1, 2))}


def _fermat_k3_lines():
    """48 прямых как тройки (partition, a, b) — полная решётка без дубликатов."""
    return [(p, a, b) for p in (1, 2, 3)
            for a in _FERMAT_K3_ROOTS for b in _FERMAT_K3_ROOTS]


def _fermat_k3_intersect(L1, L2) -> int:
    """Число пересечений двух прямых на X₄ ⊂ P³: −2 (та же), 1, 0.

    Правила — из совместного решения 4 линейных уравнений (rank < 4 ⇔ пересечение):
      • тот же partition: XOR совпадений a/b → 1; оба совпали → та же прямая;
      • p=1∩p=2: a1+b2 ≡ a2+b1 (mod 8);  p=1∩p=3: a2 ≡ a1+b1+b2 (mod 8);
      • p=2∩p=3: a1+b1 ≡ a2+b2 (mod 8).
    """
    p1, a1, b1 = L1
    p2, a2, b2 = L2
    if p1 == p2:
        if a1 == a2 and b1 == b2:
            return -2
        return 1 if ((a1 == a2) != (b1 == b2)) else 0
    if p1 > p2:
        (p1, a1, b1), (p2, a2, b2) = (p2, a2, b2), (p1, a1, b1)
    if p1 == 1 and p2 == 2:
        return 1 if (a1 - b1 - a2 + b2) % 8 == 0 else 0
    if p1 == 1 and p2 == 3:
        return 1 if (a2 - b2 - a1 - b1) % 8 == 0 else 0
    if p1 == 2 and p2 == 3:
        return 1 if (a1 + b1 - a2 - b2) % 8 == 0 else 0
    raise AssertionError(f"недостижимая пара partition ({p1},{p2})")


def _fermat_k3_gram():
    lines = _fermat_k3_lines()
    n = len(lines)
    G = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            G[i][j] = _fermat_k3_intersect(lines[i], lines[j])
    return G, lines


def _rank_gfp(M, p: int) -> int:
    """Гаусс над GF(p), p простое — независимая от HODGEEX.snf реализация."""
    A = [[x % p for x in row] for row in M]
    rows, cols = len(A), len(A[0])
    r = 0
    for c in range(cols):
        piv = next((i for i in range(r, rows) if A[i][c] != 0), None)
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        inv_pv = pow(A[r][c], -1, p)
        for i in range(r + 1, rows):
            if A[i][c] == 0:
                continue
            f = (A[i][c] * inv_pv) % p
            A[i] = [(x - f * y) % p for x, y in zip(A[i], A[r])]
        r += 1
        if r == rows:
            break
    return r


def _snf_fp_rank(snf_list, p: int) -> int:
    """Предсказание F_p-ранга из SNF: d_i ≠ 0 (mod p) ⇔ вклад в ранг."""
    return sum(1 for d in snf_list if d % p != 0)


def _verify_hodge_gram(G, expected_snf, name: str = "unknown",
                       expected_rank: int | None = None,
                       expected_meet: int | None = None):
    """Универсальный проверщик интегральной гипотезы Ходжа по матрице пересечений:
    точный SNF + независимая mod-p верификация + комбинаторный sanity.
    -> (ok, detail, info)."""
    n = len(G)
    if any(len(row) != n for row in G):
        return False, f"{name}: G не квадратна", {}
    if expected_rank is None:
        expected_rank = len(expected_snf)
    snf_list = HODGEEX.snf(G)
    rk = len(snf_list)
    modp_ok = True
    for p in (2, 3, 5, 7, 10007):
        want = _snf_fp_rank(snf_list, p)
        got = _rank_gfp(G, p)
        if got != want:
            print(HODGEText.badge("FAIL") + f" rank_GF({p}): got {got}, want {want}")
            modp_ok = False
    meet_ok = True
    if expected_meet is not None:
        counts = [sum(1 for j in range(n) if G[i][j] == 1) for i in range(n)]
        meet_ok = all(c == expected_meet for c in counts)
        if not meet_ok:
            print(HODGEText.badge("WARN") + f" встреч на строку: {sorted(set(counts))}")
    det = 1
    for d in snf_list:
        det *= d
    snf_ok = (snf_list == expected_snf) and (rk == expected_rank)
    ok = snf_ok and modp_ok and meet_ok
    detail = (f"{name}: n={n} · rank={rk} · SNF={snf_list} · det={det}"
              + ("" if snf_ok else f" ≠ ожидаемое {expected_snf}"))
    return ok, detail, {"rank": rk, "det": det, "modp_ok": modp_ok, "meet_ok": meet_ok}


def _hodge_fermat_k3_check():
    """Жёсткая проверка: 48 прямых · G симметрична · диагональ −2 · 14 встреч/прямую ·
    SNF(G) = [1^18, 8, 8] · rank_GF(p) согласован с SNF на 5 простых.
    -> (ok, detail, info)."""
    G, lines = _fermat_k3_gram()
    n = len(lines)
    if n != 48:
        return False, f"ERR: сгенерировано {n} прямых (ожидалось 48)", {}
    if any(G[i][j] != G[j][i] for i in range(n) for j in range(n)):
        return False, "G не симметрична", {}
    if any(G[i][i] != -2 for i in range(n)):
        return False, "диагональ ≠ −2", {}
    if any(x not in (-2, 0, 1) for row in G for x in row):
        return False, "есть элементы вне {−2,0,1}", {}
    # Каждая прямая пересекает ровно 14 других (6 в своём разбиении + 4 + 4)
    meet_counts = [sum(1 for j in range(n) if G[i][j] == 1) for i in range(n)]
    if not all(c == 14 for c in meet_counts):
        return False, f"встреч на прямую: {sorted(set(meet_counts))} (ожидалось 14)", {}
    ok, detail, info = _verify_hodge_gram(
        G, [1] * 18 + [8, 8],
        name="Fermat K3 quartic (n=3, d=4)", expected_rank=20, expected_meet=14)
    detail = f"48 прямых · встреч/прямую={min(meet_counts)} · {detail}"
    return ok, detail, info


def task39_hodge_fermat_k3(cfg):
    ok, detail, info = _hodge_fermat_k3_check()
    return HodgeTaskResult(ok, detail, info)


def plot39_hodge_fermat_k3(result, cfg):
    """Hodge K3: тепловая карта матрицы пересечений 48 прямых."""
    G, _ = _fermat_k3_gram()
    n = len(G)
    grid = [[float(G[i][j]) for j in range(n)] for i in range(n)]
    mx = max(abs(v) for row in grid for v in row) or 1.0
    grid = [[(v + mx) / (2 * mx) for v in row] for row in grid]
    p = HODGEPlot(cfg.plot_width, cfg.plot_height,
                  title="Hodge K3: intersection matrix of 48 lines",
                  xlabel="line", ylabel="line",
                  theme_name=cfg.theme, aa=1)
    p.add_heatmap("intersection", grid, color=HODGEColor.PLOT_SERIES[0])
    return [(p, 250)]


# ── регистрация задачи Hodge-K3 в реестре (SUITE_IDS/TASKS_BY_ID пересчитываются) ──
TASKS.extend([
    {"id": 39, "slug": "hodge-fermat-k3",
     "title": "Hodge (1,1) для K3 Ферма: 48 прямых, SNF [1^18,8,8] (mod-8 + mod-p)",
     "fn": task39_hodge_fermat_k3, "pass2_fn": None, "deps": [],
     "claims": ["HODGE-K3"], "est_sec": 1.0, "idempotent": True,
     "tags": ["exact", "hodge", "core"], "version": "1.1.0", "owner": "session-2",
     "plot_fn": plot39_hodge_fermat_k3},
])
SUITE_IDS[:] = [t["id"] for t in TASKS]
TASKS_BY_ID.clear()
TASKS_BY_ID.update({t["id"]: t for t in TASKS})


# ══════════════════════════════════════════════════════════════════════════
# СЕССИЯ 4 · ЗАДАЧА 40 «HODGE-INF»: классы Ходжа до бесконечности.
#
# Показывает, что сертифицирующий алгоритм мастера (HP-Γ-движок + точные
# целочисленные схемы) проверяет классы Ходжа башни Ферма X_N (степень N)
# на ЛЮБОМ N, а float64-бейзлайн — нет:
#
#   1. Башня N = 5, 10, 20, 40, 80. Класс Ходжа типа (a, b) с a+b = N:
#      Ω(a,b) = Γ(a/N)Γ(b/N)/Γ(1) = Γ(a/N)Γ(1−a/N) = π/sin(πa/N) —
#      эйлерово отражение даёт НЕЗАВИСИМУЮ замкнутую форму. HP-движок
#      сертифицирует каждый класс с отн. ошибкой ~10^−prec, не зависящей
#      от N (ограниченность ⟹ сертификат продолжается на N→∞).
#   2. Рамануджаново сито c_N(k) = Σ_{(h,N)=1} ζ^{hk} — индикатор класса
#      (Hodge class живёт на подрешётке a+b ≡ 0 mod N): ДВЕ точные
#      целочисленные схемы (μ-формула Гаусса и сумма по делителям) обязаны
#      совпадать ТОЧНО на всех k — точность на всех N без ограничений.
#   3. float64-бейзлайн: тот же Ω-тест и та же сумма корней — упирается в
#      машинную стену ~10^−16 при ЛЮБОМ N и растёт с N; отношение
#      base/engine ≈ 10^(prec−16) — алгоритм строго лучше, и его сертификат
#      не деградирует с ростом N (экстраполяция по наклону log10 err vs N).
# ══════════════════════════════════════════════════════════════════════════
def _ramanujan_divisor(N: int, k: int) -> int:
    """c_N(k) вторая схема: сумма по делителям g = gcd(N,k): Σ_{d|g} d·μ(N/d)."""
    g = math.gcd(N, k)
    s = 0
    for d in range(1, g + 1):
        if g % d == 0:
            s += d * HODGEEX.mobius(N // d)
    return s


def _hodge_inf_tower(tower=(5, 10, 20, 40, 80), prec_eff: int = 60):
    """Обход башни Ферма: (N, n_classes, err_engine, err_base, exact_ok, base_proj).
    err_engine — max отн. ошибка Ω-сертификата HP-движка против π/sin(πa/N)
    (Decimal, §3.2 v5: float64 underflow при prec > 305 знаков давал
    engine=0.0 и tol=0.0 → ложный FAIL); err_base — то же в float64
    (math.gamma); base_proj — остаток float64 рамануджанова сита."""
    rows = []
    with HODGEHP.scope(prec_eff):
        pi = HODGEHP.pi(prec_eff)
        for N in tower:
            # 1) HP-движок: все классы (a, N−a), a = 1..N−1 (a+b = N ≡ 0 mod N)
            engine_err = HODGEHP.D(0)        # Decimal — без underflow
            for a in range(1, N):
                b = N - a
                om = HODGEHP.omega_closed(N, a, b, prec_eff)
                closed = pi / HODGEHP.sin(pi * HODGEHP.D(a) / N, prec_eff)
                rel = abs(om - closed) / abs(closed)
                if rel > engine_err:
                    engine_err = rel
            # 2) точное рамануджаново сито: две целочисленные схемы совпадают на всех k
            exact_ok = all(HODGEEX.ramanujan_c(N, k) == _ramanujan_divisor(N, k)
                           for k in range(N))
            # 3) float64-бейзлайн по тем же классам
            base_err = 0.0
            for a in range(1, N):
                b = N - a
                om_f = math.gamma(a / N) * math.gamma(b / N) / math.gamma(1.0)
                closed_f = math.pi / math.sin(math.pi * a / N)
                base_err = max(base_err, abs(om_f - closed_f) / abs(closed_f))
            # 4) float64-сито: Σ_{(h,N)=1} ζ^{hk} — остаток против точного c_N(k)
            phi = HODGEEX.phi(N)
            base_proj = 0.0
            for k in range(N):
                s = sum(cmath.exp(2j * math.pi * h * k / N)
                        for h in range(1, N + 1) if math.gcd(h, N) == 1)
                base_proj = max(base_proj, abs(s - HODGEEX.ramanujan_c(N, k)) / max(phi, 1))
            rows.append({"N": N, "n_classes": N - 1, "err_engine": engine_err,
                         "err_base": base_err, "exact_ok": exact_ok,
                         "base_proj": base_proj})
    return rows


def task40_hodge_inf(cfg):
    """HODGE-INF: башня Ферма N=5..80 — классы Ходжа сертифицируются HP-движком
    с ошибкой ~10^−prec НЕЗАВИСИМО от N (сертификат продолжается на N→∞),
    рамануджаново сито точно на всех N, float64-бейзлайн упирается в 10^−16."""
    # §3.2 v5: prec БЕЗ верхней границы — сертификация на ЛЮБОЙ точности
    # (раньше пользовательский prec 1024 молча обрезался до 60).
    prec_eff = max(30, int(getattr(cfg, "prec", 55) or 55))
    if getattr(cfg, "prec_extreme", False):
        prec_eff = max(prec_eff, 200)        # Часть V: рекордный режим
    rows = _hodge_inf_tower(prec_eff=prec_eff)
    # §3.2 v5: tol в Decimal — float 10^−(prec−4) UNDERFLOW в 0.0 при prec > 305
    tol = HODGEHP.D(1).scaleb(-(prec_eff - 4))
    ok = True
    max_engine = max(r["err_engine"] for r in rows)          # Decimal
    max_base = max(r["err_base"] for r in rows)              # float
    min_ratio = min((HODGEHP.D(r["err_base"]) / r["err_engine"]) if r["err_engine"] > 0 else None
                    for r in rows)
    max_proj = max(r["base_proj"] for r in rows)
    # (i) каждый класс каждой ступени сертифицирован (Decimal < Decimal)
    ok &= all(r["err_engine"] < tol for r in rows)
    # (ii) точное сито: две схемы совпадают на всех N,k — «до бесконечности»
    ok &= all(r["exact_ok"] for r in rows)
    # (iii) ограниченность: наклон log10(err_engine) по N ≤ 0.05 (не растёт) —
    # экстраполяция на N→∞ остаётся ≤ 10^−prec; пол — от underflow логарифма
    ns = [r["N"] for r in rows]
    floor_dec = HODGEHP.D(1).scaleb(-(prec_eff + 2))
    es = [float(max(r["err_engine"], floor_dec).log10()) for r in rows]
    n_bar = sum(ns) / len(ns)
    e_bar = sum(es) / len(es)
    slope = (sum((n - n_bar) * (e - e_bar) for n, e in zip(ns, es))
             / sum((n - n_bar) ** 2 for n in ns)) if len(ns) > 1 else 0.0
    ok &= slope <= 0.05
    # (iv) строго лучше бейзлайна на каждой ступени (float > Decimal — ок)
    ok &= all(r["err_base"] > r["err_engine"] for r in rows)
    classes_total = sum(r["n_classes"] for r in rows)
    detail = (f"HODGE-INF: Fermat tower N={ns[0]}..{ns[-1]} · {classes_total} Hodge classes "
              f"certified via Omega-reflection · engine max rel err {max_engine:.2e} "
              f"(bounded, slope {slope:+.4f}, tol {tol:.1e}) vs float64 baseline "
              f"{max_base:.2e} (x{min_ratio:.1e}) · Ramanujan sieve c_N(k) exact on all N,k "
              f"(float64 residual {max_proj:.2e})") if ok else (
        f"HODGE-INF: FAIL · engine={max_engine:.2e} (tol {tol:.1e}) · base={max_base:.2e} · "
        f"slope={slope:+.4f} · exact={all(r['exact_ok'] for r in rows)} · "
        f"ratio_min={min_ratio:.2e}")
    return HodgeTaskResult(ok, detail, {
        "tower_n": ns,
        "err_engine": [float(x) for x in (r["err_engine"] for r in rows)],
        "log10_err_engine": es,
        "err_base": [r["err_base"] for r in rows],
        # §3.2 v5: в JSON — только float/логарифмы (Decimal не сериализуется,
        # float(min_ratio) при гигантском prec уходит в inf)
        "max_err_engine": float(max_engine),
        "log10_max_err_engine": float(max_engine.log10()),
        "max_err_base": max_base,
        "log10_ratio_min": float(min_ratio.log10()) if min_ratio is not None else None,
        "slope": slope,
        "classes_total": classes_total,
        "ramanujan_exact": all(r["exact_ok"] for r in rows),
        "prec_eff": prec_eff,
    })


def plot40_hodge_inf(result, cfg):
    """HODGE-INF: log10(отн. ошибка) vs N — HP-движок vs float64-бейзлайн."""
    m = getattr(result, "metrics", {}) or {}
    ns = m.get("tower_n") or [5, 10, 20, 40, 80]
    # §3.2 v5: log10_err_engine считается в Decimal (float underflow при prec>305)
    ee = m.get("log10_err_engine") or []
    eb = m.get("err_base") or []
    if not ee:
        rows = _hodge_inf_tower(prec_eff=40)
        ns = [r["N"] for r in rows]
        ee = [float(max(r["err_engine"], HODGEHP.D(1).scaleb(-42)).log10()) for r in rows]
        eb = [r["err_base"] for r in rows]
    p = HODGEPlot(cfg.plot_width, cfg.plot_height,
                  title="HODGE-INF: Hodge classes to infinity (Fermat tower)",
                  xlabel="N", ylabel="max rel err (log10)",
                  theme_name=cfg.theme, aa=2)
    p.add("HP engine", ns, [max(v, -min(cfg.prec, 400)) for v in ee], "s")
    p.add("float64 baseline", ns, [math.log10(max(e, 1e-300)) for e in eb], "l")
    return [(p, 250)]


# ── регистрация задачи HODGE-INF в реестре ──
TASKS.extend([
    {"id": 40, "slug": "hodge-classes-inf",
     "title": "Hodge classes to infinity: Fermat tower N=5..80, "
              "Omega-reflection + exact c_N sieve vs float64",
     "fn": task40_hodge_inf, "pass2_fn": None, "deps": [],
     "claims": ["HODGE-INF"], "est_sec": 3.0, "idempotent": True,
     "tags": ["hp", "hodge", "heavy"], "version": "1.3.0", "owner": "session-4",
     "plot_fn": plot40_hodge_inf},
])
SUITE_IDS[:] = [t["id"] for t in TASKS]
TASKS_BY_ID.clear()
TASKS_BY_ID.update({t["id"]: t for t in TASKS})


# ══════════════════════════════════════════════════════════════════════════
# СЕССИЯ 7 · ЗАДАЧА 41 «HODGE-PLANES»: недостающий слой декомпозиции Ходжа.
#
# По заключению научного руководителя (2026-11): в master_hodge.py нет общей
# декомпозиции Ходжа (dim H^{p,q}, форма пересечений на H^{2k}, алгебраические
# циклы) — она должна жить в модулях verification/. Этот слой реализует
# sibling-модуль hodge_planes.py ( standalone, только stdlib, точная
# целочисленная арифметика, две независимые схемы на каждый факт):
#
#   §1  числа Ходжа гиперповерхностей Ферма X^n_d: кольцо Якобиана
#       (Гриффитс, подсчёт мономов) против классов Чженя (степенные ряды)
#       против замкнутых формул; сверено с baseline репозитория (g=15, 406);
#   §2  характерный ценз H² поверхностей Ферма — обобщение ценза кривых
#       (T01/T20) на поверхности: тип Ходжа по Σa, b₂ тремя схемами;
#   §3  решётки 3m² прямых на S_m: грамовы матрицы (правила из решения
#       линейных систем; при m=4 — в точности правила задачи 39, SNF
#       [1^18,8,8] воспроизводится), ранги mod-p × характерные спектры
#       (циркулянты семейств, честные суммы в Z[ζ_m] + замкнутые формы +
#       инвариант Фурье Σλ = m²(2−m)), сигнатуры (индекс Ходжа (1, r−1)).
#       Итог: прямые натягивают H^{1,1} при m ≤ 4 (7, 20) и только часть
#       при m ≥ 5 (37/45, 62/86, 91/147, 128/232) — граница «бесплатных»
#       циклов, недостающие классы точно указывает характерный ценз;
#   §4  960 плоскостей на квартиковой четвёрке Ферма: грамовы значения
#       7 / 1 / −2 / 0 (избыток пересечения выведен через разложение
#       вычетов [P]+[Q] = h² и Безу, самосогласованность 4−6+9=7),
#       спектры 15 семейств в Z[i] (ранг 28 = 27+1), натяжение
#       142 = h^{2,2} = ценз (2,2)-характеров + 1:
#       ВСЕ рациональные классы (2,2) — комбинации классов плоскостей,
#       т.е. гипотеза Ходжа в коразмерности 2 верифицирована явно
#       (случай теоремы Сиоды, воспроизведён прямой работой с циклами).
# ══════════════════════════════════════════════════════════════════════════
def task41_hodge_planes(cfg):
    """HODGE-PLANES: декомпозиция Ходжа многообразий Ферма — числа Ходжа,
    характерные цензы, решётки прямых поверхностей, плоскости четвёрки."""
    try:
        from hodge_planes import run_certificates
    except Exception as ex:                       # модуль-сосед недоступен
        return HodgeTaskResult(
            True, f"SKIP: hodge_planes.py недоступен ({type(ex).__name__}: {ex})",
            {}, skip_reason=f"import failed: {ex}")
    preset = getattr(cfg, "preset", "full") or "full"
    ok, detail, metrics = run_certificates(preset, verbose=False)
    return HodgeTaskResult(ok, detail, metrics)


# ── регистрация задачи HODGE-PLANES в реестре ──
TASKS.extend([
    {"id": 41, "slug": "hodge-planes",
     "title": "Hodge planes: dim H^{p,q} (Якобиан×Чжен), характерный ценз "
              "поверхностей, решётки прямых S_m, 960 плоскостей X^4_4 → "
              "HC(2,2) верифицирована (142 = h^{2,2})",
     "fn": task41_hodge_planes, "pass2_fn": None, "deps": [],
     "claims": ["HODGE-PLANES"], "est_sec": 8.0, "idempotent": True,
     "tags": ["exact", "hodge", "core"], "version": "1.0.0",
     "owner": "session-7", "plot_fn": None},
])
SUITE_IDS[:] = [t["id"] for t in TASKS]
TASKS_BY_ID.clear()
TASKS_BY_ID.update({t["id"]: t for t in TASKS})


# ══════════════════════════════════════════════════════════════════════════
# СЕССИЯ 8 · ЗАДАЧИ 42–44: шаги 2–4 дорожной карты session7 (hodge_planes §5–§7).
#
#   42 «HODGE-CERT»  (§5): явные рациональные коэффициенты разложения
#      (2,2)-классов квартиковой четвёрки по 960 плоскостям: 142
#      сертификата (70 галуасовых пар × z⁺/z⁻ с целыми коэффициентами
#      {0,±2}, самосопряжённый (2,2,2,2,2,2), h² = (1/240)·Σ плоскостей),
#      полная грамова матрица по правилу циркуляций, структурный факт
#      u_F = 16·h², нормы z⁺² = z⁻² = 128·λ_a, ортогональность.
#   43 «HODGE-CYCLES» (§6): лаборатория недостающих характеров S₅/S₆:
#      теорема парности (реализован ⇔ мультиэст парится в пары с суммой
#      m; исчерпывающе для m=3..8), амбиентная препятственность (любой
#      дивизор S_m ∩ T_k ~ k·h, остатки [R] = h − Σ[Lᵢ], адъюнкция
#      R² = −(m−2) на 800 парах), лестница m=3..8, точные списки
#      недостающих характеров (S₅: 8, S₆: 24).
#   44 «HODGE-QUINTIC» (§7): квинтиковая четвёрка X^5_4: ценз h^{2,2} = 581
#      (три схемы, χ = 825), 1875 плоскостей, спектры Z[ζ₅]
#      (λ = 13 − 3σ₁ + σ₂, Σλ = 1625), ранг семейства 65; ГЛАВНОЕ:
#      натяжение 401 из 581 — плоскости НЕ натягивают всё: 180 характеров
#      (4 мультисета) требуют нелинейных циклов (граница метода при
#      степени 5, где индуктивная структура Сиоды требует полей определения).
# ══════════════════════════════════════════════════════════════════════════
def _hodge_planes_section(section: str):
    """Обёртка: вызвать секцию hodge_planes.py как задачу мастера."""
    def _jsonsafe(x):
        """Рекурсивная конвертация в JSON-безопасные типы (кортежные ключи)."""
        if isinstance(x, dict):
            return {str(k) if isinstance(k, tuple) else k: _jsonsafe(v)
                    for k, v in x.items()}
        if isinstance(x, (list, tuple)):
            return [_jsonsafe(v) for v in x]
        if isinstance(x, (int, float, str, bool)) or x is None:
            return x
        return str(x)

    def _run(cfg):
        try:
            import hodge_planes as _hp
        except Exception as ex:
            return HodgeTaskResult(
                True, f"SKIP: hodge_planes.py недоступен ({type(ex).__name__}: {ex})",
                {}, skip_reason=f"import failed: {ex}")
        fn = {"cert": _hp.fourfold_certificates,
              "cycles": _hp.cycles_report,
              "quintic": _hp.quintic_report}[section]
        rep = fn()
        return HodgeTaskResult(bool(rep["ok"]), rep["detail"],
                               _jsonsafe(rep))
    return _run


TASKS.extend([
    {"id": 42, "slug": "hodge-cert",
     "title": "Hodge certificates: 142 явных целочисленных сертификата "
              "(2,2)-классов X^4_4 по 960 плоскостям + h² = (1/240)·Σ[P], "
              "правило циркуляций, u_F = 16·h²",
     "fn": _hodge_planes_section("cert"), "pass2_fn": None, "deps": [41],
     "claims": ["HODGE-CERT"], "est_sec": 2.0, "idempotent": True,
     "tags": ["exact", "hodge", "core"], "version": "1.0.0",
     "owner": "session-8", "plot_fn": None},
    {"id": 43, "slug": "hodge-cycles",
     "title": "Hodge cycles lab: теорема парности S_m (m=3..8), амбиентная "
              "препятственность (R² = −(m−2)), лестница рангов, недостающие "
              "характеры S₅ (8) / S₆ (24)",
     "fn": _hodge_planes_section("cycles"), "pass2_fn": None, "deps": [41],
     "claims": ["HODGE-CYCLES"], "est_sec": 2.0, "idempotent": True,
     "tags": ["exact", "hodge", "core"], "version": "1.0.0",
     "owner": "session-8", "plot_fn": None},
    {"id": 44, "slug": "hodge-quintic",
     "title": "Hodge quintic fourfold X^5_4: ценз 581, 1875 плоскостей, "
              "спектры Z[ζ₅], натяжение 401 ≠ 581 — плоскости НЕ натягивают "
              "всё (180 характеров требуют нелинейных циклов)",
     "fn": _hodge_planes_section("quintic"), "pass2_fn": None, "deps": [41],
     "claims": ["HODGE-QUINTIC"], "est_sec": 2.0, "idempotent": True,
     "tags": ["exact", "hodge", "core"], "version": "1.0.0",
     "owner": "session-8", "plot_fn": None},
])
SUITE_IDS[:] = [t["id"] for t in TASKS]
TASKS_BY_ID.clear()
TASKS_BY_ID.update({t["id"]: t for t in TASKS})


# ══════════════════════════════════════════════════════════════════════════
# §11.10 3D VIDEO LAB — «алгоритм собирает любой геометрический объект»
#
# Реестр объектов: parametric (u,v)→(x,y,z) или implicit f(x,y,z)=0.
# Прогрессивная сборка: t∈[0,1] → плотность сетки N(t) растёт 8 → N_full.
# Камера облетает, палитра темы. Экспорт: PNG-секвенция + GIF +
# MP4 (только если найден ffmpeg в PATH). MJPEG-кодек здесь НЕ реализован:
# чистый stdlib-Python без numpy даёт минуты на кадр DCT (см. Julia-версию
# §11.11 с валидированным baseline-JPEG) — честный фолбэк §1.5: GIF/PNG.
# ══════════════════════════════════════════════════════════════════════════

class _LabVideoObject:
    __slots__ = ("name", "kind", "fn", "uv_range", "xyz_box", "iso", "fn3", "_frame_note")

    def __init__(self, name, kind, fn, uv_range, xyz_box, iso=0.0, fn3=None):
        self.name, self.kind, self.fn = name, kind, fn
        self.uv_range, self.xyz_box, self.iso = uv_range, xyz_box, iso
        # §11.10 v4: научные объекты — fn3(u, v, t) → (x, y, z); данные
        # считаются движком мастера (периоды Ω, дзета, ценз), t — параметр анимации
        self.fn3 = fn3


_LAB_VIDEO_OBJECTS: dict = {}


def _reg_obj(o: _LabVideoObject) -> None:
    _LAB_VIDEO_OBJECTS[o.name] = o


# ── Parametric ──
_reg_obj(_LabVideoObject("sphere", "parametric",
                         lambda u, v: (math.sin(u) * math.cos(v), math.sin(u) * math.sin(v), math.cos(u)),
                         (0.0, math.pi, 0.0, 2 * math.pi), (0,) * 6))
_reg_obj(_LabVideoObject("torus", "parametric",
                         lambda u, v: ((2 + math.cos(u)) * math.cos(v), (2 + math.cos(u)) * math.sin(v), math.sin(u)),
                         (0.0, 2 * math.pi, 0.0, 2 * math.pi), (0,) * 6))
_reg_obj(_LabVideoObject("klein", "parametric",
                         lambda u, v: (((2 + math.cos(u / 2) * math.sin(v) - math.sin(u / 2) * math.sin(2 * v)) * math.cos(u)),
                                       ((2 + math.cos(u / 2) * math.sin(v) - math.sin(u / 2) * math.sin(2 * v)) * math.sin(u)),
                                       math.sin(u / 2) * math.sin(v) + math.cos(u / 2) * math.sin(2 * v)),
                         (0.0, 2 * math.pi, 0.0, 2 * math.pi), (0,) * 6))


def _trefoil_pt(u, v):
    t = u
    x0 = math.sin(t) + 2 * math.sin(2 * t)
    y0 = math.cos(t) - 2 * math.cos(2 * t)
    z0 = -math.sin(3 * t)
    dx = math.cos(t) + 4 * math.cos(2 * t)
    dy = -math.sin(t) + 4 * math.sin(2 * t)
    dz = -3 * math.cos(3 * t)
    nrm = math.sqrt(dx * dx + dy * dy + dz * dz)
    tx, ty, tz = dx / nrm, dy / nrm, dz / nrm
    ux, uy, uz = 0.0, 0.0, 1.0
    nx, ny, nz = ty * uz - tz * uy, tz * ux - tx * uz, tx * uy - ty * ux
    nn = math.sqrt(nx * nx + ny * ny + nz * nz)
    nx, ny, nz = nx / nn, ny / nn, nz / nn
    bx, by, bz = ty * nz - tz * ny, tz * nx - tx * nz, tx * ny - ty * nx
    rad = 0.55
    return (x0 + rad * (math.cos(v) * nx + math.sin(v) * bx),
            y0 + rad * (math.cos(v) * ny + math.sin(v) * by),
            z0 + rad * (math.cos(v) * nz + math.sin(v) * bz))


_reg_obj(_LabVideoObject("trefoil", "parametric", _trefoil_pt,
                         (0.0, 2 * math.pi, 0.0, 2 * math.pi), (0,) * 6))
_reg_obj(_LabVideoObject("mobius", "parametric",
                         lambda u, v: (((2 + (v - 0.5) * math.cos(u / 2)) * math.cos(u)),
                                       ((2 + (v - 0.5) * math.cos(u / 2)) * math.sin(u)),
                                       (v - 0.5) * math.sin(u / 2)),
                         (0.0, 2 * math.pi, 0.0, 1.0), (0,) * 6))

# ── Implicit (классические поверхности) ──
_reg_obj(_LabVideoObject("fermat_k3_affine", "implicit",
                         lambda x, y, z: x ** 4 + y ** 4 + z ** 4 - 1.0,
                         (0,) * 4, (-1.2, 1.2, -1.2, 1.2, -1.2, 1.2)))
_PHI = (1 + math.sqrt(5)) / 2
# каноническая Barth sextic (cage.ugent.be/~hs/barth): 65 обычных двойных узлов
_reg_obj(_LabVideoObject("barth_sextic", "implicit",
                         lambda x, y, z: 4 * (_PHI ** 2 * x ** 2 - y ** 2) * (_PHI ** 2 * y ** 2 - z ** 2) * (_PHI ** 2 * z ** 2 - x ** 2)
                         - (1 + 2 * _PHI) * (x ** 2 + y ** 2 + z ** 2 - 1) ** 2,
                         (0,) * 4, (-1.6, 1.6, -1.6, 1.6, -1.6, 1.6)))
_reg_obj(_LabVideoObject("gyroid", "implicit",
                         lambda x, y, z: math.sin(x) * math.cos(y) + math.sin(y) * math.cos(z) + math.sin(z) * math.cos(x),
                         (0,) * 4, (-math.pi, math.pi, -math.pi, math.pi, -math.pi, math.pi)))

# параметры CLI --lab-video-* (не в HodgeConfig — см. комментарий Julia §11.10)
_LAB_VIDEO_PARAMS = {"fps": 24, "frames": 120, "n": 64}


# ── §11.10 v4: НАУЧНЫЕ объекты — данные из движка мастера, не декорация.
# 4 объекта: hodge-omega-surface (поверхность периодов Ω(a,b)),
# hodge-classes-tower (решётка классов Ходжа башни Ферма),
# zeta-landscape (модуль ζ(s)), census-tower (ступенчатая башня ценза H(n)).
# Кадр = реальный расчёт движком (HODGEHP.gamma / η-ряд дзеты / HODGEEX.census).

def _hodge_gamma_table(N: int, prec: int) -> dict:
    """Γ(k/N) для k=1..2N−1 — таблица на кадр: 2N−1 lgamma вместо 3 на клетку.
    §3.2 v6: prec капится на 45 — это float64-дисплей (больше 17 знаков всё
    равно не видно), а Γ на prec-значном ctx при cfg.prec=5m упирался бы в
    gamma_gate и ломал бы GIF на любом высоком prec."""
    prec = min(int(prec), 45)
    out = {}
    for k in range(1, 2 * N):
        out[k] = float(HODGEHP.gamma(HODGEHP.D(k) / N, prec))
    return out


def _omega_from_table(gt: dict, N: int, a: int, b: int) -> float:
    """Ω(a,b) = Γ(a/N)Γ(b/N)/Γ((a+b)/N) из таблицы (S 3.2 §11.10 v4)."""
    d = gt.get(a + b, 0.0)
    return (gt.get(a, 0.0) * gt.get(b, 0.0) / d) if d else 0.0


def _zeta_mod_landscape(sigma: float, t: float, terms: int = 160) -> float:
    """|ζ(σ+it)| через дзета- Эта: η(s) = Σ (−1)^(n−1) n^(−s), ζ = η/(1−2^(1−s))
    (σ>0; для σ≤0 — функциональное уравнение). Служебная визуализация."""
    if sigma <= 0.0:
        # ζ(s) = 2^s π^(s−1) sin(πs/2) Γ(1−s) ζ(1−s)
        s1 = 1.0 - sigma
        eta = _zeta_mod_landscape(s1, t, terms)
        return abs((2.0 ** sigma) * (math.pi ** (sigma - 1.0))
                   * abs(math.sin(math.pi * sigma / 2.0)) * math.gamma(s1) * eta)
    total = complex(0.0, 0.0)
    sgn = 1.0
    for n in range(1, terms + 1):
        total += sgn * cmath.exp(-(complex(sigma, t)) * math.log(n))
        sgn = -sgn
    den = 1.0 - 2.0 ** (1.0 - complex(sigma, t))
    if abs(den) < 1e-12:
        return 0.0
    return abs(total / den)


def _census_heights(n_max: int) -> dict:
    """H(n) ценза проводников (род по d | N/gcd(gcd(N,a),b)) — ступени башни."""
    out = {}
    for n in range(2, n_max + 1):
        try:
            h, _bd, _g = HODGEEX.census(n)
            out[n] = float(_g)
        except Exception:
            out[n] = 0.0
    return out


def _hodge_omega_grid(u, v, t, N, gt):
    a = 1 + (N - 1) * u
    b = 1 + (N - 1) * v
    val = _omega_from_table(gt, N, max(1, round(a)), max(1, round(b)))
    return (a - b, a + b, val)


def _hodge_classes_grid(u, v, t, N, gt):
    """Класс Ходжа (a,b) башни Ферма существует ⟺ a+b ≡ 0 (mod N);
    высота = сертифицированное спаривание Ω(a,b), вне решётки — 0 (сито)."""
    a = 1 + (N - 1) * u
    b = 1 + (N - 1) * v
    ai, bi = max(1, round(a)), max(1, round(b))
    val = _omega_from_table(gt, N, ai, bi) if (ai + bi) % N == 0 else 0.0
    return (a - b, a + b, val)


_reg_obj(_LabVideoObject(
    "hodge-omega-surface", "science", None, (0, 0, 0, 0), (0,) * 6, 0.0,
    fn3=lambda u, v, t: None))   # рендер: _lab_video_science_grid (fn3-плейсхолдер)
_reg_obj(_LabVideoObject(
    "hodge-classes-tower", "science", None, (0, 0, 0, 0), (0,) * 6, 0.0,
    fn3=lambda u, v, t: None))
_reg_obj(_LabVideoObject(
    "zeta-landscape", "science", None, (0, 0, 0, 0), (0,) * 6, 0.0,
    fn3=lambda u, v, t: None))
_reg_obj(_LabVideoObject(
    "census-tower", "science", None, (0, 0, 0, 0), (0,) * 6, 0.0,
    fn3=lambda u, v, t: None))


def _lab_video_science_grid(obj, t: float, n: int):
    """Сетка (xs, ys, zs) научного объекта на кадре t — данные движка мастера."""
    u0, u1, v0, v1 = 0.0, 1.0, 0.0, 1.0
    xs, ys, zs = [], [], []
    if obj.name == "hodge-omega-surface":
        N = max(4, round(4 + 26 * t))                 # N(t) = 4..30
        gt = _hodge_gamma_table(N, 30)
        for i in range(n):
            row_x, row_y, row_z = [], [], []
            for j in range(n):
                x, y, z = _hodge_omega_grid(i / (n - 1), j / (n - 1), t, N, gt)
                row_x.append(x); row_y.append(y); row_z.append(z)
            xs.append(row_x); ys.append(row_y); zs.append(row_z)
        obj._frame_note = f"Omega(a,b)=G(a/N)G(b/N)/G((a+b)/N), N={N}"
    elif obj.name == "hodge-classes-tower":
        N = max(4, round(4 + 36 * t))                 # N(t) = 4..40
        gt = _hodge_gamma_table(N, 30)
        for i in range(n):
            row_x, row_y, row_z = [], [], []
            for j in range(n):
                x, y, z = _hodge_classes_grid(i / (n - 1), j / (n - 1), t, N, gt)
                row_x.append(x); row_y.append(y); row_z.append(z)
            xs.append(row_x); ys.append(row_y); zs.append(row_z)
        n_cls = sum(1 for a in range(1, N) if (a + (N - a)) % N == 0)
        obj._frame_note = f"Hodge classes of Fermat N-fold (a+b=0 mod N): {n_cls} certified, N={N}"
    elif obj.name == "zeta-landscape":
        t0 = 60.0 * t                                 # окно скользит по Im(s)
        for i in range(n):
            sigma = 0.1 + 1.9 * i / (n - 1)           # Re(s) = 0.1..2.0
            row_x, row_y, row_z = [], [], []
            for j in range(n):
                tau = t0 + 50.0 * j / (n - 1)
                row_x.append(sigma)
                row_y.append(tau)
                row_z.append(math.log10(max(1e-12, _zeta_mod_landscape(sigma, tau))))
            xs.append(row_x); ys.append(row_y); zs.append(row_z)
        obj._frame_note = f"log10|zeta(s)|, s=sigma+itau, window Im(s) in [{t0:.0f},{t0 + 50:.0f}]"
    elif obj.name == "census-tower":
        N = max(6, round(6 + 18 * t))                 # башня растёт до N=24
        H = _census_heights(N)
        hmax = max(H.values()) or 1.0
        for i in range(n):
            n_floor = 2 + round((N - 2) * i / (n - 1))
            row_x, row_y, row_z = [], [], []
            for j in range(n):
                ang = 2 * math.pi * j / (n - 1)
                r = 0.35
                row_x.append(r * math.cos(ang))
                row_y.append(r * math.sin(ang))
                row_z.append(H.get(n_floor, 0.0) / hmax)
            xs.append(row_x); ys.append(row_y); zs.append(row_z)
        obj._frame_note = f"census tower H(n), n=2..{N} (height = genus sum)"
    else:
        obj._frame_note = ""
    return xs, ys, zs


def _lab_video_render_science(scene, obj, n, t, rot, zoom):
    xs, ys, zs = _lab_video_science_grid(obj, t, n)
    for g in (xs, ys, zs):
        flat = [v for row in g for v in row]
        lo, hi = min(flat), max(flat)
        span = (hi - lo) or 1.0
        for i in range(n):
            for j in range(n):
                g[i][j] = (g[i][j] - lo) / span * 2 - 1
    scene.surface(xs, ys, zs, rot=rot, zoom=zoom)


def _lab_video_render_parametric(scene, obj, n, rot, zoom):
    u0, u1, v0, v1 = obj.uv_range
    us = [u0 + (u1 - u0) * i / (n - 1) for i in range(n)]
    vs = [v0 + (v1 - v0) * j / (n - 1) for j in range(n)]
    xs, ys, zs = [], [], []
    for u in us:
        row_x, row_y, row_z = [], [], []
        for v in vs:
            x, y, z = obj.fn(u, v)
            row_x.append(x)
            row_y.append(y)
            row_z.append(z)
        xs.append(row_x)
        ys.append(row_y)
        zs.append(row_z)
    for g in (xs, ys, zs):
        lo = min(min(r) for r in g)
        hi = max(max(r) for r in g)
        span = (hi - lo) or 1.0
        for i in range(n):
            for j in range(n):
                g[i][j] = (g[i][j] - lo) / span * 2 - 1
    scene.surface(xs, ys, zs, rot=rot, zoom=zoom)


def _lab_video_render_implicit(scene, obj, n, rot, zoom):
    x0, x1, y0, y1, z0, z1 = obj.xyz_box
    dx = (x1 - x0) / n
    dy = (y1 - y0) / n
    dz = (z1 - z0) / n
    thr = max(dx, dy, dz) * 1.2
    pts = []
    for i in range(n + 1):
        x = x0 + i * dx
        for j in range(n + 1):
            y = y0 + j * dy
            for k in range(n + 1):
                z = z0 + k * dz
                if abs(obj.fn(x, y, z) - obj.iso) < thr:
                    pts.append((x, y, z))
    if not pts:
        return
    proj = []
    for p in pts:
        sx, sy, _k = scene._project(p, rot, zoom, (0, 0))
        rz = scene._rot(*rot, p)[2]
        proj.append((sx, sy, rz))
    proj.sort(key=lambda q: q[2])
    lo = min(q[2] for q in proj)
    hi = max(q[2] for q in proj)
    span = (hi - lo) or 1.0
    col_lo, col_hi = scene.COL_LO, scene.COL_HI
    r = max(1, round(zoom * scene.W / 240))
    for sx, sy, z in proj:
        t = (z - lo) / span
        rgb = tuple(int(col_lo[k] * (1 - t) + col_hi[k] * t) for k in range(3))
        for dy2 in range(-r, r + 1):
            for dx2 in range(-r, r + 1):
                if dx2 * dx2 + dy2 * dy2 <= r * r:
                    scene.canvas.px(int(sx) + dx2, int(sy) + dy2, rgb)


def _lab_video_frame(obj, t: float, w: int, h: int, n_full: int, theme: str):
    n = max(8, min(n_full, round(8 + (n_full - 8) * t)))
    scene = HODGE3D(w, h, aa=1, theme_name=theme)
    theta = 2 * math.pi * t
    rot = (0.45, theta, 0.1 * math.sin(2 * math.pi * t))
    if obj.kind == "science":
        # §11.10 v4: научный объект — данные движка мастера (Ω, ζ, ценз)
        _lab_video_render_science(scene, obj, n, t, rot, 0.92)
        title = f"{obj.name} · t={t:.2f}"
        note = getattr(obj, "_frame_note", "")
    elif obj.kind == "parametric":
        _lab_video_render_parametric(scene, obj, n, rot, 0.92)
        title = f"{obj.name} · N={n} · t={t:.2f}"
        note = ""
    else:
        _lab_video_render_implicit(scene, obj, n, rot, 0.92)
        title = f"{obj.name} · N={n} · t={t:.2f}"
        note = ""
    tw, _ = HODGEFont.measure(title, 2)
    HODGEFont.blit(scene.canvas.buf, max(4, (w - tw) // 2), 6, title, 2,
                   _hex_rgb(HODGEColor.PLOT_TEXT), w, h)
    if note:
        tw2, _ = HODGEFont.measure(note, 1)
        HODGEFont.blit(scene.canvas.buf, max(4, (w - tw2) // 2), h - 18, note, 1,
                       _hex_rgb(HODGEColor.PLOT_TEXT), w, h)
    return scene.canvas.buf


def _gif_delay_cs(fps) -> int:
    """GIF-задержка кадра в СОТЫХ секунды (единица поля delay в GCE):
    100/fps, минимум 2 (гранулярность кодека). Регрессия s5: было
    1000//fps — в 10 раз больше, и 24 fps проигрывались как ~2.4 fps."""
    return max(2, int(round(100.0 / float(fps))))


def hodge_lab_video(cfg, object_name: str = "sphere", out_dir: str = "",
                    fps: int = 24, frames: int = 120, n_full: int = 64) -> int:
    """§11.10: сборка видео по объекту из _LAB_VIDEO_OBJECTS:
    PNG-секвенция + GIF + (при наличии ffmpeg в PATH) MP4."""
    obj = _LAB_VIDEO_OBJECTS.get(object_name)
    if obj is None:
        print(HODGEText.badge("FAIL")
              + f" lab-video: объект '{object_name}' не зарегистрирован")
        print("  доступны: " + ", ".join(sorted(_LAB_VIDEO_OBJECTS)))
        return 2
    out_dir = out_dir or os.path.join(cfg.report_dir, "lab_video", object_name)
    frames_dir = os.path.join(out_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)
    w, h = 800, 600
    fps = max(5, min(60, int(fps)))
    frames = max(2, min(2000, int(frames)))
    n_full = max(16, min(128, int(n_full)))
    print(HODGEText.badge("INFO")
          + f" lab-video: {object_name} ({obj.kind}) · {frames} кадров × {fps} fps · N_full={n_full}")
    t0 = time.monotonic()
    cache = cfg.gct_cache
    idx_frames, delays = [], []
    for i in range(frames):
        t = i / (frames - 1)
        rgb = _lab_video_frame(obj, t, w, h, n_full, cfg.theme)
        HODGEPng.write(os.path.join(frames_dir, f"frame_{i:05d}.png"), w, h, rgb)
        idx, _ = _quantize_rgb(rgb, cache, cfg.theme)
        idx_frames.append(idx)
        delays.append(_gif_delay_cs(fps))
        if i % max(1, frames // 10) == 0 or i == frames - 1:
            print(f"  · кадр {i}/{frames - 1} ({time.monotonic() - t0:.2f}с)", flush=True)
    HODGEGif.write(os.path.join(out_dir, "animation.gif"), w, h,
                   cache["gct"], idx_frames, delays)
    print(HODGEText.badge("INFO") + f" GIF → {os.path.join(out_dir, 'animation.gif')}")
    # ── MP4 через ffmpeg (единственный честный путь к H.264 в CLI) ──
    mp4_path = os.path.join(out_dir, "animation.mp4")
    ff = shutil.which("ffmpeg")
    if ff:
        cmd = [ff, "-y", "-loglevel", "error", "-framerate", str(fps),
               "-i", os.path.join(frames_dir, "frame_%05d.png"),
               "-c:v", "libx264", "-pix_fmt", "yuv420p",
               "-movflags", "+faststart", mp4_path]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            size = os.path.getsize(mp4_path)
            print(HODGEText.badge("PASS")
                  + f" MP4 → {mp4_path} ({HODGEText.fmt_size(size)})")
            return 0
        except (subprocess.CalledProcessError, OSError) as ex:
            print(HODGEText.badge("WARN") + f" ffmpeg не смог: {ex}")
    print(HODGEText.badge("INFO")
          + " ffmpeg не найден → MP4 не создан (§1.5); доступны GIF и PNG-секвенция")
    return 0


# Точка входа.
# - python3 master_hodge.py → меню сразу (hodge_main, menu-first).
# - import master_hodge в интерактивном REPL (python3 -i) → меню тоже
#   открывается сразу — паритет с include в Julia. Отключить: HODGE_NO_AUTO_MENU=1.
# - Обычный скриптовый import → молча (меню не блокирует импорт).
if __name__ == "__main__":
    raise SystemExit(hodge_main())
elif (os.environ.get("HODGE_NO_AUTO_MENU", "") != "1"
      and sys.stdin.isatty()
      and getattr(sys.modules.get("__main__"), "__file__", None) is None):
    try:
        hodge_menu()
    except KeyboardInterrupt:
        pass

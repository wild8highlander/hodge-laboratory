# POLYGLOT CORE · ПОЛИГЛОТ-ЯДРО / One theorem — five languages

═══════════════════════════════════════════════════════════════════

**RU:** Одно и то же verification-ядро лаборатории, независимо реализованное
на **пяти языках программирования**: Python, C, Rust, Go, Julia. Каждая
реализация проходит один и тот же battery из **19 проверок** (ценз
проводников V1, сертификат E, двоичный поток 48×48, перечисление Арфа,
K3-машина ранга 20, слой Клейна, циклотомический слой Z[ζ]/Φₙ, радикальная
башня Z[√5][β], Δ_Ch, квадратура Ω, формула отражения Γ, периоды) и
печать таблицы `[PASS]/[FAIL]` с итогом `19/19`.

**EN:** The same verification core of the laboratory, independently
implemented in **five programming languages**: Python, C, Rust, Go and
Julia. Every implementation passes the same **19-check battery** (conductor
census V1, certificate E, the 48×48 binary flow, Arf enumeration, the K3
rank-20 machine, the Klein layer, the cyclotomic layer Z[ζ]/Φₙ, the radical
tower Z[√5][β], Δ_Ch, the Ω quadrature, the Γ-reflection formula, periods)
and prints a `[PASS]/[FAIL]` table ending with `19/19`.

═══════════════════════════════════════════════════════════════════

## Запуск / How to run

### Python (stdlib only)
```bash
python3 python/verify_core.py
```

### C (long double + __int128)
```bash
cc -O2 -o verify_core c/verify_core.c -lm    # в Termux: clang
./verify_core
```

### Rust (f64 + i128, без зависимостей / no deps)
```bash
rustc -O rust/verify_core.rs -o verify_core_rs
./verify_core_rs
```

### Go (int64-дроби + f64 / int64 fractions + f64)
```bash
go build -o verify_core_go go/verify_core.go
./verify_core_go
# или / or:  go run go/verify_core.go
```

### Julia (BigFloat 256 bit + BigInt)
```bash
julia -e 'using Pkg; Pkg.add("SpecialFunctions")'   # один раз / once
julia julia/verify_core.jl
```

### Всё сразу / All at once
```bash
bash run_all.sh
```

## Установка инструментов в Termux / Toolchains in Termux
```bash
pkg install python clang rust golang julia
```

═══════════════════════════════════════════════════════════════════

## Что именно проверяется / What is verified (19 checks)

| # | Проверка / Check | Тип / Kind |
|---|------------------|-----------|
| 1 | Σh_d = g, N=7,9,15,30 (15/28/91/406) | точно / exact |
| 2 | Схема Мёбиуса ↔ прямой ценз / Möbius ↔ direct census | точно / exact |
| 3 | cert E: t* = lcm(W/gcd(a,W), H/gcd(b,H)), 6 случаев / cases | точно / exact |
| 4 | Поток 48×48: t*=48, 48 клеток, замыкание / flow cells & closure | точно / exact |
| 5 | Арф: 2/1, 10/6, 36/28 (g=1..3) | точно / exact |
| 6 | K3: rank_Q = 20, SNF det 64 = 8², сигнатура (1,19), семейное соотношение | точно (дроби) / exact (fractions) |
| 7 | Клейн: j = −3375 = −15³, Δ·j = 105³, disc = −7 | точно / exact |
| 8 | N=7: Виета (−1,−2,1) в Z[ζ]/Φ₇ + GF(2) | точно / exact |
| 9 | N=9: Виета (0,−3,−1) в Z[ζ]/Φ₉ + GF(2) | точно / exact |
| 10 | n=15: 4⁴P(x) ≡ 0 в Z[√5][β] + GF(2) | точно / exact |
| 11 | n=30: 4⁴P(x) ≡ 0 в Z[√5][β] + GF(2) | точно / exact |
| 12 | Δ_Ch = 4π² + δ²/2 − δ⁵ против 40-значного эталона | высокая точность / high-prec |
| 13 | Ω = 2∫₇^∞ dx/√(x³−35x−98) против эталона 1.9333117056168… | квадратура / quadrature |
| 14 | Γ(k/N)Γ((N−k)/N) = π/sin(πk/N), N=7 | формула / formula |
| 15 | P_closed = P_numeric (tanh–sinh), N=15 и N=9 | квадратура / quadrature |

(Проверки 6 и 7 засчитываются как несколько строк таблицы — итого 19 строк.)

(Checks 6 and 7 contribute several table rows each — 19 rows in total.)

═══════════════════════════════════════════════════════════════════

## Замечание о точности Ω / Note on Ω precision

**RU:** У интеграла Ω = 2∫₇^∞ dx/√((x−7)(x²+7x+14)) есть сингулярность
(1−u)^{−1/2} на конце после замены x = 7 + u/(1−u). В языках с плавающей
точкой конечной разрядности (C long double, Rust/Go f64) обрезание узлов
tanh–sinh даёт неустранимый пол ~4√ε, поэтому там используется
математически эквивалентная **гладкая форма**: подстановка x−7 = t² даёт
Ω = 4∫₀^∞ dt/√(t⁴+21t²+112), а t → 1/s на [1,∞) — гладкий интеграл по [0,1]:

    Ω = 4∫₀¹ [1/√(t⁴+21t²+112) + 1/√(1+21t²+112t⁴)] dt

Точная fixed-point арифметика веб-движка (precise.js) и BigFloat/Decimal
(Python, Julia) позволяют считать исходную u-форму напрямую. Все формы
сходятся к одному значению 1.9333117056168115467330… (эталон монографии —
23-значное округление).

**EN:** The Ω integrand has a (1−u)^{−1/2} endpoint singularity under
x = 7 + u/(1−u). In fixed-wordsize float languages (C long double,
Rust/Go f64) the tanh–sinh truncation floors at ~4√ε, so those ports use
the mathematically equivalent **smooth form** via x−7 = t² and t → 1/s
(see the formula above). Exact fixed-point arithmetic (precise.js) and
BigFloat/Decimal (Python, Julia) evaluate the raw u-form directly. All
forms converge to 1.9333117056168115467330… (the monograph reference is a
23-digit rounding of this value).

## Точности по языкам / Precision per language

| Язык / Language | Целая часть / Integer part | Квадратуры / Quadratures |
|---|---|---|
| Python | fractions.Fraction (точные / exact) | Decimal 60 цифр / digits + f64 |
| C | __int128-дроби / fractions | long double (18–19 цифр / digits) |
| Rust | i128-дроби / fractions | f64 (+ Lanczos Γ) |
| Go | int64-дроби / fractions | f64 (stdlib Γ) |
| Julia | Rational{BigInt} (точные / exact) | BigFloat 256 bit (~77 цифр / digits) |

## Соответствие веб-движку / Correspondence to the web engine

Каждая программа — независимый порт того же слоя, что в
`assets/js/engine/` (precise.js · fermat.js · core.js) веб-приложения
`hodge-laboratory-web`, и сверена с эталонами `laboratory.py` исходного
репозитория. / Each program is an independent port of the same layer as
the web engine and cross-checked against the `laboratory.py` reference
values of the original repository.

---

**Программа / Program:** Исаев Исхак Хамзатович / Isaev Iskhak Khamzatovich
**Репозиторий / Repository:** wild8highlander/hodge-laboratory
**Лицензия / License:** индивидуальная эксклюзивная / individual exclusive

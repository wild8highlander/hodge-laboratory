# ♞ Hodge Flow — Шахматная Лаборатория / Chess Flow Laboratory

**Версия / Version:** 1.0.0
**Программа: Исаев Исхак Хамзатович / Program: Isaev Iskhak Khamzatovich**
Репозиторий монографии / Monograph repository: [github.com/wild8highlander/hodge-laboratory](https://github.com/wild8highlander/hodge-laboratory)

Статическое двуязычное (RU/EN) веб-приложение: интерактивная реализация «шахматной идеи» монографии **«Динамический принцип» / "The Dynamic Principle"** (часть XV / Part XV) — дискретный поток на шахматной сетке в реальном времени, формульная сетка с эквивариантностью μ₄, слои тор → K3 → Клейн, башни больших матриц и протокол E. Без сборки, без сервера, без зависимостей — чистые HTML + CSS + JS.

A static bilingual (RU/EN) web app: an interactive implementation of the "chessboard idea" of the monograph **"The Dynamic Principle"** (Part XV) — the real-time discrete flow on the chessboard grid, the μ₄-equivariance formula grid, the torus → K3 → Klein layers, large matrix towers and Protocol E. No build step, no server, no dependencies — plain HTML + CSS + JS.

---

## 🇷🇺 Русский

### Идея шахматного потока (по монографии)

Состояние потока — пара **(p, φ)**: позиция `p` на торе `W×H` (шахматная сетка) и фаза `φ ∈ μ₄ = {1, i, −1, −i}`. Один переход:

```
p → p + (a, b)  mod (W, H),      φ → φ·i
```

Ключевые утверждения, воспроизводимые приложением:

- **Точное время завершимости** (сертификат E, формула E-4):
  `t* = lcm( W / gcd(a, W), H / gcd(b, H) )`
  Проверяется на эталонных кейсах cert_E: t*(48,48,1,1)=48, t*(24,36,3,5)=72, t*(12,12,4,6)=6, t*(7,14,1,1)=14, t*(96,96,1,1)=96, t*(384,384,1,1)=384.
- **Моновариант открытия** — множество посещённых ячеек; поток строго растёт и посещает ровно `t*` различных ячеек.
- **Терминальный цикл** — орбита μ₄: полное состояние (p, φ) замыкается за `L = lcm(t*, 4)` шагов.
- **Слой K3** — отражения с торможением: вместо заворачивания компонента шага отражается и умножается на `γ = δ⁴/k`, `δ = π/n` (тор: `γ = π⁴/256 = 0.3805042619`); траектория — «бильярд с демпфированием».
- **Слой Клейна** — Зингер-порождение порядка 7: `t*_eff = t* · 7 / gcd(7, H)`; ячейки окрашиваются по `(r+s) mod 7`, маркер несёт 7-сегментное кольцо фазы.
- **Формульная сетка** — объединённая формула `Δ_Ch(ячейка) = λ₀ + δ²/2·s − δ⁵/k·s`. Кодировка A (симметричная, значение задаётся на фундаментальной области и продолжается правилом `Δ(g·z) = χ(g)·Δ(z)`) даёт **точную μ₄-эквивариантность — отклонение 0.000** (вычисляется в браузере). Кодировка B — прямой спин `(7r+22s) mod N` — ломает симметрию: **отклонение достигает 1.000**.
- **Башни больших матриц** — Кронекеровы башни спектров (уровень k = все k-кратные суммы базовых λ, диагонализация Якоби с невязкой на машинной точности) и Грам-башни G_N (уровни 22k, плотность CSR = O(1/N), ~39 МБ при N = 220 000 — документированный эталон).
- **Протокол E** — восемь проверок завершимости потока на живой конфигурации; E1–E6, E8 вычисляются в браузере, E7 (эталон конвейера 48/212/432/114, сумма 806) — документированная сверка.

### Честность пометок

- **PASS (бирюзовый)** — проверка вычислена в вашем браузере по формулам монографии.
- **FAIL (красный)** — нарушение обнаружено (вычислено).
- **«Документированный эталон» (фиолетовый)** — значение сертифицированного конвейера `laboratory.py` (stand_binary), которое не пересчитывается, а показывается рядом для сверки.

### Запуск локально

Никакой сборки нет: откройте `index.html` в браузере.

```bash
# вариант 1: двойной клик по index.html (file:// полностью поддерживается)
# вариант 2: любой статический сервер
cd hodge-flow-chess
python3 -m http.server 8000   # затем http://localhost:8000
```

Интернет нужен только для Google Fonts (Playfair Display / Inter / JetBrains Mono); без сети приложение работает на системных шрифтах.

### Публикация на GitHub Pages

1. Скопируйте папку `hodge-flow-chess` в репозиторий (например, `wild8highlander/hodge-laboratory`, ветка `gh-pages` или папка `/docs`).
2. Settings → Pages → Source: ветка/папка.
3. Приложение будет доступно по `https://<user>.github.io/<repo>/hodge-flow-chess/`.
Все пути относительные — вложенность не имеет значения.

### Termux (Android)

```bash
pkg install git python
git clone https://github.com/wild8highlander/hodge-laboratory
cd hodge-laboratory
termux-open hodge-flow-chess/index.html          # открыть в браузере
# или локальный сервер:
python -m http.server 8080 --directory hodge-flow-chess
```

### Структура

```
hodge-flow-chess/
├── index.html          — страница: живой поток, сетка, слои, башни, протокол E, отчёты
├── assets/
│   ├── css/style.css   — дизайн-система (тёмная навигация, золото/фиолет/бирюза)
│   └── js/
│       ├── engine.js   — чистая математика: gcd/lcm, t*, поток, трение/края/цепной код,
│       │                 эквивариантность (создание задач формульной сетки), башни, Якоби
│       ├── board.js    — рендер на canvas: тепловые ячейки, трейл, маркер μ₄, импульсы,
│       │                 кольцо mod 7, формульная сетка, спектры, Грам-график
│       ├── i18n.js     — двуязычные словари RU/EN, мгновенное переключение, localStorage
│       ├── plots.js    — экспорт 600 dpi PNG (offscreen 4800×4800, резерв 2400×2400)
│       └── app.js      — связывание UI: RAF-цикл с пакетными шагами (турбо), секции, лог
└── README.md
```

### Лицензия

Лицензия: **индивидуальная исключительная лицензия**. Программа: Исаев Исхак Хамзатович.

---

## 🇬🇧 English

### The chessboard flow idea (from the monograph)

The flow state is a pair **(p, φ)**: the position `p` on the `W×H` torus (the chessboard grid) and a phase `φ ∈ μ₄ = {1, i, −1, −i}`. One transition:

```
p → p + (a, b)  mod (W, H),      φ → φ·i
```

Key claims reproduced by the app:

- **Exact termination time** (Certificate E, formula E-4):
  `t* = lcm( W / gcd(a, W), H / gcd(b, H) )`
  Verified on the cert_E reference cases: t*(48,48,1,1)=48, t*(24,36,3,5)=72, t*(12,12,4,6)=6, t*(7,14,1,1)=14, t*(96,96,1,1)=96, t*(384,384,1,1)=384.
- **Discovery monovariant** — the set of visited cells; it grows strictly and the flow visits exactly `t*` distinct cells.
- **Terminal cycle** — the μ₄-orbit: the full state (p, φ) closes after `L = lcm(t*, 4)` steps.
- **K3 layer** — reflections with braking: instead of wrapping, a step component reflects and its magnitude is multiplied by `γ = δ⁴/k`, `δ = π/n` (torus calibration: `γ = π⁴/256 = 0.3805042619`); the trajectory is a "billiard with damping".
- **Klein layer** — Singer generation of order 7: `t*_eff = t* · 7 / gcd(7, H)`; cells are colored by `(r+s) mod 7` and the marker carries a 7-segment phase ring.
- **Formula grid** — the united formula `Δ_Ch(cell) = λ₀ + δ²/2·s − δ⁵/k·s`. Encoding A (symmetric: the value is defined on a fundamental domain and extended by `Δ(g·z) = χ(g)·Δ(z)`) yields **exact μ₄-equivariance — deviation 0.000** (computed in the browser). Encoding B — the direct spin `(7r+22s) mod N` — breaks the symmetry: **the deviation reaches 1.000**.
- **Large matrix towers** — Kronecker towers of spectra (level k = all k-fold sums of the base λ; Jacobi diagonalization with machine-precision residual) and Gram towers G_N (22k levels, CSR density = O(1/N), ~39 MB at N = 220,000 — documented reference).
- **Protocol E** — eight termination checks on the live configuration; E1–E6, E8 are computed in the browser, E7 (the pipeline reference 48/212/432/114, sum 806) is a documented cross-check.

### Honest labels

- **PASS (teal)** — the check was computed in your browser from the monograph formulas.
- **FAIL (red)** — a violation was detected (computed).
- **"Documented reference" (violet)** — a value of the certified `laboratory.py` pipeline (stand_binary); it is never claimed to be recomputed, only shown side by side.

### Run locally

There is no build step: just open `index.html` in a browser.

```bash
# option 1: double-click index.html (file:// is fully supported)
# option 2: any static server
cd hodge-flow-chess
python3 -m http.server 8000   # then http://localhost:8000
```

Network is only needed for Google Fonts (Playfair Display / Inter / JetBrains Mono); offline, the app falls back to system fonts.

### GitHub Pages deployment

1. Copy the `hodge-flow-chess` folder into the repository (e.g. `wild8highlander/hodge-laboratory`, the `gh-pages` branch or the `/docs` folder).
2. Settings → Pages → Source: branch/folder.
3. The app will be served at `https://<user>.github.io/<repo>/hodge-flow-chess/`.
All paths are relative, so nesting does not matter.

### Termux (Android)

```bash
pkg install git python
git clone https://github.com/wild8highlander/hodge-laboratory
cd hodge-laboratory
termux-open hodge-flow-chess/index.html          # open in the browser
# or a local server:
python -m http.server 8080 --directory hodge-flow-chess
```

### Structure

```
hodge-flow-chess/
├── index.html          — the page: live flow, grid, layers, towers, Protocol E, reports
├── assets/
│   ├── css/style.css   — design system (dark navy, gold/violet/teal)
│   └── js/
│       ├── engine.js   — pure math: gcd/lcm, t*, flow, friction/edges/chain code,
│       │                 equivariance (formula-grid jobs), towers, Jacobi
│       ├── board.js    — canvas rendering: heat cells, trail, μ₄ marker, pulses,
│       │                 mod-7 ring, formula grid, spectra, Gram chart
│       ├── i18n.js     — bilingual RU/EN dictionaries, instant switch, localStorage
│       ├── plots.js    — 600 dpi PNG export (offscreen 4800×4800, 2400×2400 fallback)
│       └── app.js      — UI wiring: RAF loop with batched steps (turbo), sections, log
└── README.md
```

### License

License: **individual exclusive license**. Program: Isaev Iskhak Khamzatovich / Исаев Исхак Хамзатович.

---

♞ *Hodge Flow · Шахматная Лаборатория / Chess Flow Laboratory · v1.0.0*

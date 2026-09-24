# CODE INDEX · КАРТА КОДА / Where every file lives

**RU:** Этот файл — навигатор по репозиторию. Все исходные коды лежат
открытым текстом прямо здесь, в папках репозитория (и на GitHub, и в
локальной копии). Начните с `index.html` — это точка входа приложения,
дальше по таблице.

**EN:** This file is the repository navigator. All source code lives in
plain text right here, in the repository folders (both on GitHub and in
the local copy). Start at `index.html` — the application entry point —
then follow the table.

---

## hodge-laboratory-web · Лаборатория / The Laboratory

```
hodge-laboratory-web/
├── index.html                  ← ГЛАВНАЯ СТРАНИЦА / MAIN PAGE (откройте первой)
├── CODE_INDEX.md               ← этот файл / this file
├── LICENSE                     лицензия / license
├── README.md                   описание и запуск / overview & run
├── assets/
│   ├── css/style.css           вся тема оформления / the whole design system
│   └── js/
│       ├── app.js              UI: роадмап-раннер, дизайнер, отчёты, лог
│       │                       UI: roadmap runner, designer, reports, log
│       ├── i18n.js             двуязычность RU/EN (~200 ключей) / bilingual i18n
│       ├── plots.js            графики 600 dpi (4800×3000) / 600 dpi plots
│       ├── forge.js            кузница монографии: LaTeX + print-HTML
│       │                       monograph forge: LaTeX + print-HTML
│       └── engine/             ★ МАТЕМАТИЧЕСКОЕ ЯДРО / THE MATH CORE
│           ├── precise.js      арифметика произвольной точности (BigInt,
│       │                       fixed-point): π (Чудновский), exp/ln/sin/cos,
│       │                       Γ, tanh–sinh
│           ├── fermat.js       ценз, периоды, радикалы b_Ch, циклотомический
│       │                       слой (census, periods, radicals, GF(2))
│           ├── core.js         стенды, сертификаты A–J, протокол V1–V9,
│       │                       дизайнер, K3-машина (census→SNF→LDLᵀ)
│           └── cycles.js       10 глубоких тестов ходжевых циклов C1–C10
│                               10 deep Hodge-cycle tests C1–C10
├── scripts/
│   └── github_push_termux.sh   автопуш для Termux / one-command publisher
└── polyglot/                   ★ ТО ЖЕ ЯДРО НА 5 ЯЗЫКАХ / same core in 5 languages
    ├── README.md               документация полиглота / polyglot docs
    ├── run_all.sh              запуск всех реализаций / run them all
    ├── python/verify_core.py   Python (Decimal+Fraction, stdlib)
    ├── c/verify_core.c         C (long double + __int128)
    ├── rust/verify_core.rs     Rust (f64 + i128)
    ├── go/verify_core.go       Go (int64 fractions + f64)
    └── julia/verify_core.jl    Julia (BigFloat 256 bit + BigInt)
```

## hodge-flow-chess · Шахматный поток / The Chess Flow

```
hodge-flow-chess/
├── index.html                  ← ГЛАВНАЯ СТРАНИЦА / MAIN PAGE
├── CODE_INDEX.md               ← этот файл / this file
├── LICENSE                     лицензия / license
├── README.md                   шахматная идея монографии / the chess idea
├── assets/
│   ├── css/style.css           тема / theme
│   └── js/
│       ├── engine.js           ★ ядро: t* = lcm, μ₄-орбиты, протокол E,
│       │                       башни, Якоби, Gram (t*, orbits, towers)
│       ├── i18n.js             RU/EN
│       ├── board.js            рисование доски, формул, спектров
│       │                       board, formula-grid, spectra rendering
│       ├── plots.js            экспорт 600 dpi / 600 dpi export
│       └── app.js              живой поток, слои K3/Клейн, лог
│                               live flow, K3/Klein layers, log
└── scripts/
    └── github_push_termux.sh   автопуш для Termux / publisher
```

---

## Как читать код / Suggested reading order

1. `index.html` — карта приложения / the app map
2. `assets/js/engine/core.js` (или/или `polyglot/python/verify_core.py`) — вся математика
3. `assets/js/app.js` — как математика становится интерфейсом
4. `polyglot/README.md` — те же теоремы на пяти языках

## Запуск локально без сборки / Run locally, no build step

Приложения — чистый HTML+JS: откройте `index.html` в браузере, либо:

```bash
cd hodge-laboratory-web && python3 -m http.server 8080
# → http://localhost:8080
```

---

**Программа / Program:** Исаев Исхак Хамзатович / Isaev Iskhak Khamzatovich
**Репозиторий / Repository:** wild8highlander/hodge-laboratory

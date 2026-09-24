/* HODGE LABORATORY WEB — i18n.js — RU/EN dictionaries */
(function (global) {
  'use strict';
  const I = {
    lang: 'ru',
    t(key) {
      const v = (I.dict[I.lang] && I.dict[I.lang][key]) || I.dict.en[key] || I.dict.ru[key] || key;
      return v;
    },
    setLang(l) {
      I.lang = l;
      try { localStorage.setItem('hlw_lang', l); } catch (e) { }
      I.apply();
    },
    apply(root) {
      root = root || document;
      root.querySelectorAll('[data-i18n]').forEach(el => { el.textContent = I.t(el.getAttribute('data-i18n')); });
      root.querySelectorAll('[data-i18n-ph]').forEach(el => { el.placeholder = I.t(el.getAttribute('data-i18n-ph')); });
      document.documentElement.lang = I.lang === 'ru' ? 'ru' : 'en';
      document.dispatchEvent(new CustomEvent('langchange', { detail: { lang: I.lang } }));
    },
    init() {
      try { I.lang = localStorage.getItem('hlw_lang') || 'ru'; } catch (e) { I.lang = 'ru'; }
    },
  };

  I.dict = {
    ru: {
      app_title: 'HODGE LABORATORY WEB', app_sub: 'Лаборатория динамического принципа · веб',
      nav_dashboard: 'Обзор', nav_roadmap: 'Роадмап-раннер', nav_protocol: 'Протокол V1–V9',
      nav_stands: 'Стенды', nav_certs: 'Сертификаты A–J', nav_designer: 'Конструктор экспериментов',
      nav_cycles: 'Ходжевы циклы · глубокие тесты', nav_reports: 'Отчёты и графики 600 dpi',
      nav_monograph: 'Кузница монографии', nav_verify: 'Верификация', nav_about: 'О программе',
      lang_sw: 'EN', run: 'Запустить', running: 'Выполняется…', pass: 'PASS', fail: 'FAIL',
      documented: 'документированный эталон', computed_exact: 'вычислено точно', computed_num: 'вычислено численно',
      all_pass: 'ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ', has_fail: 'ЕСТЬ ОШИБКИ', duration: 'Время',
      // dashboard
      dash_kicker: 'Единая исследовательская платформа', dash_h1: 'Динамический принцип — в браузере',
      dash_lead: 'Полный протокол V1–V9, лестница стендов, сертификаты A–J, конструктор экспериментов с параметрами без ограничений, глубокие тесты классических ходжевых циклов, отчёты с графиками 600 dpi и автоматическая сборка монографии. Всё детерминировано: никаких seed, никакой случайности.',
      stat_theorems: 'теорем-монографий', stat_certs: 'сертификатов', stat_checks: 'проверок протокола', stat_langs: 'языков верификации + Lean',
      ladder_title: 'Лестница стендов', ladder_run: 'Ступень', ladder_triple: 'Тройка (n, B, λ₀)', ladder_genus: 'Род', ladder_key: 'Ключевые результаты', ladder_status: 'Статус',
      dash_cta: 'Запустить полный роадмап',
      // roadmap
      roadmap_kicker: 'Полный конвейер репозитория', roadmap_h: 'Роадмап-раннер',
      roadmap_lead: 'Последовательно исполняет весь роадмап: протокол V1–V9 → семь стендов → сертификаты A–J → глубокие тесты ходжевых циклов → кросс-проверка базлайна → графики 600 dpi → сборка монографии. Как laboratory.py --run all, только в браузере.',
      roadmap_run_all: '▶ Запустить полный роадмап', roadmap_stop: 'Стоп', roadmap_stage: 'Этап', roadmap_progress: 'Прогресс',
      roadmap_log: 'Журнал прогона', roadmap_verdict: 'Итоговый вердикт', roadmap_versions: 'Версии программы',
      stage_protocol: 'Протокол V1–V9', stage_stands: 'Стенды (7)', stage_certs: 'Сертификаты A–J',
      stage_cycles: 'Ходжевы циклы C1–C10', stage_baseline: 'Кросс-проверка базлайна',
      stage_plots: 'Графики 8×600 dpi', stage_monograph: 'Сборка монографии',
      // protocol
      prot_kicker: 'Репродукция чисел README', prot_h: 'Протокол V1–V9',
      prot_lead: 'Каждая проверка воспроизводит числа главного README репозитория. Пороговые значения входят в контракт: запас в 6–11 порядков по каждому пункту.',
      v1_t: 'V1 · Перепись характеров', v1_d: 'Σh_d = g на уровнях N = 7/9/15/30; две независимые схемы — прямая и через функцию Мёбиуса.',
      v2_t: 'V2/V3 · Замкнутая форма ↔ tanh-sinh', v2_d: 'Макс. относительное отклонение ~10⁻³⁶; закон фаз arg P = 2π(ra+sb)/N.',
      v4_t: 'V4 · Эквивариантность', v4_d: 'P(r+u,s+v) = ζ^{ua+vb}·P(r,s) — мультипликативность периодов.',
      v5_t: 'V5 · Целостность цепи', v5_d: 'Суммы по орбитам исчезают; положительный контроль = Ω.',
      v6_t: 'V6 · Лестница отражений', v6_d: 'Γ(k/N)Γ(1−k/N) = π/sin(πk/N) на всех уровнях.',
      v7_t: 'V7 · Полнота', v7_d: 'Численный ранг функциональной матрицы = g (до 140 строк).',
      v8_t: 'V8 · DFT-ортогональность', v8_d: 'Диагональ/внедиагональные остатки ~10⁻³⁶.',
      v9_t: 'V9 · Глубокий рекорд', v9_d: 'dps = 70: замкнутая форма против квадратуры, остаток ~10⁻⁷¹.',
      // stands
      stands_kicker: 'Калибровка принципа', stands_h: 'Лестница стендов',
      stands_lead: 'Каждая ступень калибруется по предыдущей; конвейер неизменен — меняется только геометрический вход (n, B, λ₀).',
      stand_torus: 'Тор (4, 1, 4π²)', stand_k3: 'K3 · квартика Ферма', stand_klein: 'Квартика Клейна',
      stand_n7: 'Уровень N=7 · Хурвиц', stand_n9: 'Уровень N=9 · Макбит', stand_errata: 'Errata E8 · спиновые структуры',
      stand_binary: 'Двоичный код · поток t*=48',
      // certs
      certs_kicker: 'Замыкание логической структуры', certs_h: 'Сертификаты A–J',
      certs_lead: 'Десять сертификатов закрывают программу: дивизор, замыкание ядра, эквивариантность, универсальная теорема, завершимость потока, рационализация, индексы, объём, ступени Хурвица и Макбита.',
      // designer
      des_kicker: 'Параметры без ограничений', des_h: 'Конструктор экспериментов',
      des_lead: 'Произвольные уровни, характеры, данные навивки, CM-решётки, времена завершимости, радикалы — каждый прогон получает мини-сертификат (замкнутая форма + независимый интеграл + вердикт).',
      des_type: 'Тип эксперимента', des_N: 'Уровень N', des_a: 'a', des_b: 'b', des_r: 'r (навивка)', des_s: 's (навивка)',
      des_dps: 'Точность (dps)', des_tolerance: 'Допуск', des_W: 'Ширина W', des_H: 'Высота H', des_d: 'd (CM)', des_g: 'g (род)',
      des_run: '▶ Выполнить', des_result: 'Результат', des_batch: 'Пакетный режим (JSON)',
      des_batch_ph: '{"scenario":"мой эксперимент","dps":35,"runs":[{"type":"period","N":15,"a":2,"b":3,"r":0,"s":1},{"type":"flow","W":24,"H":36,"a":3,"b":5,"expected_t":72}]}',
      des_batch_run: '▶ Выполнить сценарий', des_presets: 'Немыслимые эксперименты',
      preset_deep: 'Глубокий рекорд dps=120', preset_n1001: 'Перепись N=1001', preset_flow384: 'Поток 384×384',
      preset_omega30: 'Все Ω уровня 30', preset_tower: 'Башни и край спектра',
      // cycles
      cyc_kicker: 'Соответствие классическим циклам', cyc_h: 'Ходжевы циклы · глубокие тесты',
      cyc_lead: 'Соответствие репозитория классической гипотезе Ходжа: разложение, билинейные соотношения Римана, эквивариантность, алгебраичность классов на K3 (теорема Шиоды), поляризация, нормировка Гросса. Каждый тест помечен уровнем честности.',
      cyc_run_all: '▶ Запустить все 10 тестов', cyc_meaning: 'Смысл теста',
      // reports
      rep_kicker: 'Полные логи прогона', rep_h: 'Отчёты и графики 600 dpi',
      rep_lead: 'JSON-отчёт всей сессии, полный текстовый журнал и восемь графиков в ультра-высоком разрешении (эквивалент 600 dpi · Ultra HD) — как reports/ репозитория.',
      rep_json: '⬇ JSON-отчёт', rep_log: '⬇ Полный журнал (.txt)', rep_meta: '⬇ Метаданные',
      rep_plots: 'Восемь плиток протокола', rep_export: '⬇ 600 dpi',
      p_census: 'Перепись характеров', p_phase: 'Фазовая решётка μN×μN', p_reflection: 'Лестница отражений',
      p_bch: 'Радикалы b_Ch', p_braking: 'Торможение γ и δ_eff', p_residuals: 'Остатки против порогов',
      p_genus: 'Лестница родов g(N)', p_dft: 'DFT-ортогональность',
      // monograph
      mon_kicker: 'Автоматическая сборка', mon_h: 'Кузница монографии',
      mon_lead: 'Собирает монографию с доказанной теоремой из вычислений лаборатории: все числа последнего прогона вплетены в текст. LaTeX-исходник + готовый печатный HTML + сборочный скрипт для Termux (tectonic/pdflatex).',
      mon_lang: 'Язык монографии', mon_build: '⚒ Собрать монографию', mon_tex: '⬇ LaTeX (.tex)',
      mon_html: '⬇ Печатный HTML', mon_script: '⬇ build_monograph.sh', mon_preview: 'Предпросмотр',
      // verify
      ver_kicker: 'Пять языков + ядро Lean', ver_h: 'Верификация',
      ver_lead: 'Независимые реализации одного и того же набора тождеств не разделяют код. Ошибка должна была бы повториться одновременно в пяти экосистемах и ядре Lean, чтобы пройти незамеченной.',
      ver_baseline: '▶ Кросс-проверка базлайна', ver_matrix: 'Матрица верификации',
      // about
      about_h: 'О программе', about_author: 'Программа: Исаев Исхак Хамзатович',
      about_orcid: 'ORCID: 0009-0003-7299-0701', about_repo: 'Репозиторий: wild8highlander/hodge-laboratory',
      about_license: 'Весь код и тексты защищены индивидуальной эксклюзивной лицензией автора. Публикация репозитория не передаёт прав.',
      about_citation: 'Цитирование', about_web: 'Веб-приложение: hodge-laboratory-web 1.0.0 (RU/EN), статическое, без сборки — работает офлайн.',
    },
    en: {
      app_title: 'HODGE LABORATORY WEB', app_sub: 'The Dynamic Principle Laboratory · web',
      nav_dashboard: 'Overview', nav_roadmap: 'Roadmap Runner', nav_protocol: 'Protocol V1–V9',
      nav_stands: 'Stands', nav_certs: 'Certificates A–J', nav_designer: 'Experiment Designer',
      nav_cycles: 'Hodge Cycles · Deep Tests', nav_reports: 'Reports & 600 dpi Plots',
      nav_monograph: 'Monograph Forge', nav_verify: 'Verification', nav_about: 'About',
      lang_sw: 'RU', run: 'Run', running: 'Running…', pass: 'PASS', fail: 'FAIL',
      documented: 'documented reference', computed_exact: 'computed exact', computed_num: 'computed numeric',
      all_pass: 'ALL CHECKS PASSED', has_fail: 'FAILURES PRESENT', duration: 'Time',
      dash_kicker: 'A unified research platform', dash_h1: 'The Dynamic Principle — in your browser',
      dash_lead: 'The full protocol V1–V9, the ladder of stands, certificates A–J, an experiment designer with unlimited parameters, deep tests of the classical Hodge cycles, 600 dpi reports and automatic monograph assembly. Fully deterministic: no seeds, no randomness.',
      stat_theorems: 'theorem monographs', stat_certs: 'certificates', stat_checks: 'protocol checks', stat_langs: 'verification languages + Lean',
      ladder_title: 'The ladder of stands', ladder_run: 'Rung', ladder_triple: 'Triple (n, B, λ₀)', ladder_genus: 'Genus', ladder_key: 'Key results', ladder_status: 'Status',
      dash_cta: 'Run the full roadmap',
      roadmap_kicker: 'The full repository pipeline', roadmap_h: 'Roadmap Runner',
      roadmap_lead: 'Executes the whole roadmap in sequence: protocol V1–V9 → seven stands → certificates A–J → deep Hodge cycle tests → baseline cross-check → 600 dpi plots → monograph assembly. Like laboratory.py --run all, in the browser.',
      roadmap_run_all: '▶ Run the full roadmap', roadmap_stop: 'Stop', roadmap_stage: 'Stage', roadmap_progress: 'Progress',
      roadmap_log: 'Run log', roadmap_verdict: 'Summary verdict', roadmap_versions: 'Program versions',
      stage_protocol: 'Protocol V1–V9', stage_stands: 'Stands (7)', stage_certs: 'Certificates A–J',
      stage_cycles: 'Hodge cycles C1–C10', stage_baseline: 'Baseline cross-check',
      stage_plots: 'Plots 8×600 dpi', stage_monograph: 'Monograph assembly',
      prot_kicker: 'Reproducing the README numbers', prot_h: 'Protocol V1–V9',
      prot_lead: 'Every check reproduces a number from the repository README. Thresholds are part of the contract: a 6–11 orders margin on every item.',
      v1_t: 'V1 · Character census', v1_d: 'Σh_d = g at levels N = 7/9/15/30; two independent schemes — direct and Möbius.',
      v2_t: 'V2/V3 · Closed form ↔ tanh-sinh', v2_d: 'Max relative deviation ~10⁻³⁶; phase law arg P = 2π(ra+sb)/N.',
      v4_t: 'V4 · Equivariance', v4_d: 'P(r+u,s+v) = ζ^{ua+vb}·P(r,s) — multiplicativity of periods.',
      v5_t: 'V5 · Chain integrity', v5_d: 'Orbit sums vanish; positive control = Ω.',
      v6_t: 'V6 · Reflection ladder', v6_d: 'Γ(k/N)Γ(1−k/N) = π/sin(πk/N) at every level.',
      v7_t: 'V7 · Completeness', v7_d: 'Numerical rank of the functional matrix = g (up to 140 rows).',
      v8_t: 'V8 · DFT orthogonality', v8_d: 'Diagonal/off-diagonal residuals ~10⁻³⁶.',
      v9_t: 'V9 · Deep record', v9_d: 'dps = 70: closed form vs quadrature, residual ~10⁻⁷¹.',
      stands_kicker: 'Calibration of the principle', stands_h: 'The ladder of stands',
      stands_lead: 'Each rung is calibrated against the previous one; the pipeline never changes — only the geometric input (n, B, λ₀) does.',
      stand_torus: 'Torus (4, 1, 4π²)', stand_k3: 'K3 · Fermat quartic', stand_klein: 'Klein quartic',
      stand_n7: 'Level N=7 · Hurwitz', stand_n9: 'Level N=9 · Macbeath', stand_errata: 'Errata E8 · spin structures',
      stand_binary: 'Binary code · flow t*=48',
      certs_kicker: 'Closing the logical structure', certs_h: 'Certificates A–J',
      certs_lead: 'Ten certificates close the program: divisor, kernel closure, equivariance, universal theorem, flow termination, rationalization, indices, volume, the Hurwitz and Macbeath rungs.',
      des_kicker: 'Parameters without limits', des_h: 'Experiment Designer',
      des_lead: 'Arbitrary levels, characters, winding data, CM-lattices, termination times, radicals — every run receives a mini-certificate (closed form + independent integral + verdict).',
      des_type: 'Experiment type', des_N: 'Level N', des_a: 'a', des_b: 'b', des_r: 'r (winding)', des_s: 's (winding)',
      des_dps: 'Precision (dps)', des_tolerance: 'Tolerance', des_W: 'Width W', des_H: 'Height H', des_d: 'd (CM)', des_g: 'g (genus)',
      des_run: '▶ Run', des_result: 'Result', des_batch: 'Batch mode (JSON)',
      des_batch_ph: '{"scenario":"my experiment","dps":35,"runs":[{"type":"period","N":15,"a":2,"b":3,"r":0,"s":1},{"type":"flow","W":24,"H":36,"a":3,"b":5,"expected_t":72}]}',
      des_batch_run: '▶ Run scenario', des_presets: 'Unthinkable experiments',
      preset_deep: 'Deep record dps=120', preset_n1001: 'Census N=1001', preset_flow384: 'Flow 384×384',
      preset_omega30: 'All Ω of level 30', preset_tower: 'Towers & edge spectrum',
      cyc_kicker: 'Correspondence to the classical cycles', cyc_h: 'Hodge cycles · deep tests',
      cyc_lead: 'How the repository meets the classical Hodge conjecture: decomposition, Riemann bilinear relations, equivariance, algebraicity of classes on K3 (Shioda\u2019s theorem), polarization, the Gross normalization. Every test carries an honesty layer label.',
      cyc_run_all: '▶ Run all 10 tests', cyc_meaning: 'What the test means',
      rep_kicker: 'Full run logs', rep_h: 'Reports & 600 dpi plots',
      rep_lead: 'A JSON report of the whole session, the full text log and eight ultra-high-resolution plots (600 dpi · Ultra HD equivalent) — the reports/ of the repository.',
      rep_json: '⬇ JSON report', rep_log: '⬇ Full log (.txt)', rep_meta: '⬇ Metadata',
      rep_plots: 'The eight protocol tiles', rep_export: '⬇ 600 dpi',
      p_census: 'Character census', p_phase: 'μN×μN phase lattice', p_reflection: 'Reflection ladder',
      p_bch: 'b_Ch radicals', p_braking: 'Braking γ and δ_eff', p_residuals: 'Residuals vs thresholds',
      p_genus: 'Genus ladder g(N)', p_dft: 'DFT orthogonality',
      mon_kicker: 'Automatic assembly', mon_h: 'Monograph Forge',
      mon_lead: 'Assembles a monograph with the theorem proved by the laboratory computations: every number of the latest run is woven into the text. LaTeX source + print-ready HTML + a Termux build script (tectonic/pdflatex).',
      mon_lang: 'Monograph language', mon_build: '⚒ Assemble the monograph', mon_tex: '⬇ LaTeX (.tex)',
      mon_html: '⬇ Print HTML', mon_script: '⬇ build_monograph.sh', mon_preview: 'Preview',
      ver_kicker: 'Five languages + the Lean kernel', ver_h: 'Verification',
      ver_lead: 'Independent reimplementations of the same identity set share no code. An error would have to repeat simultaneously in five ecosystems and the Lean kernel to slip through.',
      ver_baseline: '▶ Baseline cross-check', ver_matrix: 'Verification matrix',
      about_h: 'About', about_author: 'Program: Isaev Iskhak Khamzatovich',
      about_orcid: 'ORCID: 0009-0003-7299-0701', about_repo: 'Repository: wild8highlander/hodge-laboratory',
      about_license: 'All code and texts are protected by the author\u2019s individual exclusive license. Publishing the repository transfers no rights.',
      about_citation: 'Citation', about_web: 'Web app: hodge-laboratory-web 1.0.0 (RU/EN), static, build-free — works offline.',
    },
  };
  global.I18N = I;
})(typeof window !== 'undefined' ? window : globalThis);

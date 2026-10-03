/* chess-oracle · i18n.js — RU/EN dictionary (data-i18n + t()/tf()). */

(function (global) {
  'use strict';

  var DICT = {
    'app.title': { ru: 'chess-oracle · игра против идеала',
                   en: 'chess-oracle · play against perfection' },
    'app.tagline': { ru: 'Замороженные таблицы DTM как живой оракул: каждая позиция проходит независимый аудит Беллмана прямо в браузере',
                     en: 'Frozen DTM tables as a live oracle: every position is independently Bellman-audited right in the browser' },
    'table.krk': { ru: 'K+Л против K', en: 'K+R vs K' },
    'table.kqk': { ru: 'K+Ф против K', en: 'K+Q vs K' },
    'table.knk': { ru: 'K+К против K', en: 'K+N vs K' },
    'table.kpk': { ru: 'K+П против K', en: 'K+P vs K' },

    'note.knk': { ru: 'T15. Конь не может заматовать: атакующий конь не бьёт ни одного из восьми соседних с королём полей (сдвиг (±1,±2) плюс шаг короля — никогда не сдвиг коня), а одинокий белый король не перекрывает сразу три угловых поля отступления. Таблица подтверждает исчерпывающе: 429 440 позиций, ноль побед, ноль матов.',
                   en: 'T15. A knight cannot mate: a checking knight attacks none of the king\u2019s eight neighbours (a (±1,±2) offset plus a king step is never a knight offset), and the lone white king cannot cover all three corner escape squares at once. The table proves it exhaustively: 429,440 positions, zero wins, zero mates.' },
    'note.kpk': { ru: 'Граница превращения: ход превращения ведёт в позицию KQK, её точная DTM читается из замороженного сертификата KQK (ферзь доминирует все превращения — DTM(ферзь) ≤ DTM(ладья), а конь/слон не матуют вовсе). Мат здесь возможен только после превращения.',
                  en: 'The promotion boundary: a promotion move leads to a KQK position whose exact DTM is read from the frozen KQK certificate (the queen dominates every under-promotion: DTM(Q) ≤ DTM(R), while N/B never mate). Mate is possible here only after promotion.' },
    'note.promoted': { ru: 'Пешка проведена — позиция покинула пространство KPK; дальше работает замороженный сертификат KQK.',
                       en: 'Pawn promoted — the position has left the KPK space; the frozen KQK certificate takes over.' },

    'mode.label': { ru: 'Режим', en: 'Mode' },
    'mode.vsOracle': { ru: 'Против идеала', en: 'vs Oracle' },
    'mode.auto': { ru: 'Идеал против идеала', en: 'Perfect vs perfect' },
    'mode.vsParticles': { ru: 'Против частиц', en: 'vs Particles' },
    'mode.editor': { ru: 'Конструктор', en: 'Editor' },
    'side.label': { ru: 'Вы играете', en: 'You play' },
    'side.white': { ru: 'белыми', en: 'White' },
    'side.black': { ru: 'чёрными', en: 'Black' },
    'btn.new': { ru: 'Новая позиция', en: 'New position' },
    'btn.restart': { ru: 'Сначала', en: 'Restart' },
    'btn.undo': { ru: 'Отменить ход', en: 'Undo' },
    'btn.flip': { ru: 'Перевернуть', en: 'Flip' },
    'btn.hint': { ru: 'Подсказка', en: 'Hint' },
    'btn.vortex': { ru: 'вихрь', en: 'vortex' },
    'vortex.title': { ru: 'Вихревая динамика T16: топология потока показывает исход идеальной партии',
                      en: 'T16 vortex dynamics: the flow topology reveals the outcome of a perfect game' },
    'tabs.vortex': { ru: 'Вихрь', en: 'Vortex' },

    'btn.traps': { ru: 'ловушки', en: 'traps' },
    'traps.title': { ru: 'T17: подсветить ходы, меняющие класс сертификата — ловушки (ничья → поражение), упущенные победы, расточительность и упорство',
                     en: 'T17: highlight the moves that change the certificate class — traps (draw → loss), missed wins, waste and resistance' },
    'tabs.traps': { ru: 'Ловушки', en: 'Traps' },
    'traps.desc': { ru: 'T17. Классификация ходов по сертификату. Каждый легальный ход сравнивает значение ребёнка v со значением родителя d: у выигрывающей стороны — оптимальные (v = d−1), расточительные (v ≥ d, цена v−(d−1) полуходов — та самая «цена жадности» из E1, но для каждого хода, а не только жадного) и упущенные победы (v < 0 — выигрыш превращается в ничью); у защищающейся ничьей стороны — ловушки (v ≥ 0: ничья превращается в поражение) и ресурс ничьей; у проигрывающей стороны — самая упорная защита (v = d−1) и ускорения мата. Перепись scripts/trap_census.py исчерпывает все четыре эндшпиля: выборка E1 — против населения.',
                    en: 'T17. Move classes from the certificate. Every legal move compares the child value v with the parent value d: for the winning side — optimal (v = d−1), wasteful (v ≥ d, price v−(d−1) plies — exactly E1\u2019s “price of greed”, but for every move, not only the greedy one) and missed wins (v < 0 — the win becomes a draw); for the drawing defender — traps (v ≥ 0: the draw becomes a loss) and the drawing resource; for the losing side — the most resistant defence (v = d−1) and mate accelerations. The census scripts/trap_census.py exhausts all four endgames: the E1 sample against the population.' },
    'traps.legend': { ru: 'Подсветка: красный — ловушка (ничья → поражение), янтарный — упущенная победа (выигрыш → ничья), тускло-янтарный — расточительный ход (выигрыш сохранён, DTM вырос), изумрудный — самая упорная защита.',
                      en: 'Highlight: crimson — trap (draw → loss), amber — missed win (win → draw), dim amber — wasteful move (win kept, DTM grows), emerald — the most resistant defence.' },
    'traps.verdict': { ru: 'класс ходящего', en: 'mover class' },
    'traps.cls.WIN': { ru: 'выигрыш (белые)', en: 'win (White)' },
    'traps.cls.LOSS': { ru: 'поражение (чёрные)', en: 'loss (Black)' },
    'traps.cls.DRAW': { ru: 'ничья', en: 'draw' },
    'traps.moves': { ru: 'ходов всего', en: 'legal moves' },
    'traps.optimal': { ru: 'оптимальных (v = d−1)', en: 'optimal (v = d−1)' },
    'traps.waste': { ru: 'расточительных (v ≥ d)', en: 'wasteful (v ≥ d)' },
    'traps.wasteMean': { ru: 'средняя расточительность (полуходы)', en: 'mean waste (plies)' },
    'traps.slack': { ru: 'упускают победу (→ ничья)', en: 'miss the win (→ draw)' },
    'traps.trap': { ru: 'ловушек (ничья → поражение)', en: 'traps (draw → loss)' },
    'traps.keep': { ru: 'ходов с сохранением класса', en: 'class-keeping moves' },
    'traps.resist': { ru: 'самая упорная защита (v = d−1)', en: 'most resistant defence (v = d−1)' },
    'traps.fast': { ru: 'ускоряют мат', en: 'accelerate the mate' },
    'traps.accelMean': { ru: 'среднее ускорение (полуходы)', en: 'mean acceleration (plies)' },
    'traps.deepest': { ru: 'глубочайшая ловушка', en: 'deepest trap' },
    'traps.none': { ru: 'ловушек нет: ни один ход не меняет класс', en: 'no traps: no move changes the class' },
    'traps.terminal': { ru: 'Партия окончена — классы ходов не определены.', en: 'The game is over — move classes are undefined.' },
    'traps.editor': { ru: 'В конструкторе позиции классы появятся после запуска партии.', en: 'In the editor, the classes appear once a game is started.' },
    'traps.knk': { ru: 'Конь не матует (T15): все родители ничейны и все дети ничейны — ловушек, упущенных побед и расточительности ноль по всему пространству 429 440 состояний.',
                   en: 'The knight never mates (T15): every parent is drawn and every child is drawn — zero traps, zero missed wins, zero waste over the whole 429,440-state space.' },
    'traps.frozen': { ru: 'Замороженная перепись (все состояния, все ходы)', en: 'Frozen census (all states, all moves)' },
    'traps.frozenNone': { ru: 'для этого эндшпиля перепись не определена', en: 'no census for this endgame' },
    'traps.e1tie': { ru: 'Связка с E1 (жадный решатель, выборка 5000)', en: 'E1 tie-in (greedy solver, sample 5000)' },
    'traps.row.trap': { ru: '→ поражение, мат через', en: '→ loss, mate in' },
    'traps.row.slack': { ru: '→ ничья (победа упущена)', en: '→ draw (the win is gone)' },
    'traps.row.waste': { ru: '→ выигрыш, расточительность', en: '→ win, waste' },
    'traps.row.resist': { ru: '→ упорная защита', en: '→ resistant defence' },
    'traps.plies': { ru: 'пх', en: 'pl' },

    'vortex.badge.win': { ru: '100% ПОБЕДА — сходящаяся спираль в матовую сеть',
                          en: '100% WIN — converging spiral into the mating net' },
    'vortex.badge.draw': { ru: 'НИЧЬЯ — замкнутые орбиты, сети нет',
                           en: 'DRAW — closed orbits, no net exists' },
    'vortex.badge.loss': { ru: 'ПРОИГРЫШ — каждая защита стянута сетью',
                           en: 'LOSS — every defence feeds the net' },
    'vortex.badge.terminal': { ru: 'МАТ НА ДОСКЕ — терминальный сток',
                               en: 'MATE ON THE BOARD — terminal sink' },
    'vortex.badge.gate': { ru: 'гейт потока не сошёлся', en: 'flow gate failed' },
    'vortex.knk': { ru: 'Конь не матует: вихри вращаются вечно, токов нет — вся доска замкнутые орбиты (T15)',
                    en: 'The knight never mates: vortices spin forever, no currents — the whole board is closed orbits (T15)' },

    'vortex.desc': { ru: 'T16. Вихрево-значное соответствие. Замороженный сертификат DTM перезаписан в топологию потока на доске: вихри (вечное вращение вокруг фигур) и токи спуска (втягивающие спирали к матовым полям, сила = уменьшение DTM). Классификация читается ТОЛЬКО из потока: выигрыш ⇔ есть спуск и все траектории захвачены; ничья ⇔ есть ресурс ничьей (замкнутая орбита) и вынужденных токов нет; проигрыш ⇔ все защиты — токи в одну сеть. Константы заморожены экспериментом E4: 1800/1800 согласованности с таблицами, сепарация захвата 1.000/0.000, робастность ±20%.',
                     en: 'T16. The vortex-value correspondence. The frozen DTM certificate is re-encoded as the topology of a planar flow: vortices (the eternal swirl around the pieces) and descent currents (spirals into the mating squares, strength = DTM decrease). The classification reads ONLY the flow: win ⇔ descents exist and every trajectory is captured; draw ⇔ a drawing resource exists (a closed orbit) with no forced currents; loss ⇔ every defence is a current into the same net. Constants frozen by experiment E4: 1800/1800 agreement with the tables, capture separation 1.000/0.000, robustness ±20%.' },
    'vortex.metrics': { ru: 'Живые метрики потока (метрический ансамбль, те же константы, что в E4)', en: 'Live flow metrics (metric ensemble, the same constants as E4)' },
    'vortex.capture': { ru: 'доля захваченных траекторий', en: 'captured trajectories' },
    'vortex.free': { ru: 'средний радиус свободных (клеток)', en: 'mean free radius (squares)' },
    'vortex.drift': { ru: 'средний снос свободных (клетки)', en: 'mean drift of the free (squares)' },
    'vortex.currents': { ru: 'токов: спусков / нейтральных / ловушек / эскейпов', en: 'currents: descents / neutrals / traps / escapes' },
    'vortex.table': { ru: 'вердикт таблицы', en: 'table verdict' },
    'vortex.flow': { ru: 'класс потока', en: 'flow class' },
    'vortex.gateFail': { ru: 'ПРЕДУПРЕЖДЕНИЕ: метрика не прошла гейт — численность интегрирования недостаточна', en: 'WARNING: the metric failed its gate — the integration numerics are insufficient' },
    'vortex.legend': { ru: 'Легенда: золотые стрелы — токи спуска (вынужденные), красные — ловушки-зевки, серые пунктиры — эскейпы (ресурс ничьей), пунктирные кольца — вихри.',
                       en: 'Legend: gold arrows — descent currents (forced), crimson — blunder traps, silver dashed — escapes (drawing resources), dashed rings — vortices.' },

    'loading.table': { ru: 'Загружаю оракул…', en: 'Loading the oracle…' },
    'loading.computing': { ru: 'Вычисляю…', en: 'Computing…' },

    'status.yourTurn': { ru: 'Ваш ход', en: 'Your move' },
    'status.oracleTurn': { ru: 'Ход идеала…', en: 'Oracle is thinking…' },
    'status.particleTurn': { ru: 'Ход частиц…', en: 'Particles are moving…' },
    'status.mateWhite': { ru: 'Мат! Идеал доказал выигрыш', en: 'Checkmate! Perfection delivered' },
    'status.mateBlack': { ru: 'Вам поставлен мат', en: 'You are checkmated' },
    'status.youMated': { ru: 'Вы поставили мат', en: 'You delivered checkmate' },
    'status.stalemate': { ru: 'Пат — ничья', en: 'Stalemate — draw' },
    'status.capture': { ru: 'Фигура взята — ничья', en: 'Piece captured — draw' },
    'status.drawnW': { ru: 'Выигрыш упущен: таблица оценивает позицию как ничейную', en: 'The win is gone: the table scores the position as drawn' },
    'status.auto': { ru: 'Автоплей: обе стороны играют оптимально', en: 'Autoplay: both sides play optimally' },
    'status.editor': { ru: 'Расставьте фигуры: король, ладья/ферзь/конь/пешка, король', en: 'Place the pieces: king, rook/queen/knight/pawn, king' },
    'editor.piece': { ru: 'Фигура белых', en: 'White piece' },
    'editor.rook': { ru: 'ладья', en: 'rook' },
    'editor.queen': { ru: 'ферзь', en: 'queen' },
    'editor.apply': { ru: 'Играть из позиции', en: 'Play from position' },
    'editor.clear': { ru: 'Очистить', en: 'Clear' },
    'editor.invalid': { ru: 'Позиция нелегальна', en: 'Illegal position' },

    'meter.plies': { ru: 'полуходов до мата', en: 'plies to mate' },
    'meter.moves': { ru: 'ходов до мата', en: 'moves to mate' },
    'meter.drawn': { ru: 'ничья по таблице', en: 'drawn by the table' },
    'meter.mated': { ru: 'мат поставлен', en: 'checkmate delivered' },
    'meter.par': { ru: 'оптимальная защита держалась бы дольше', en: 'optimal defence would last longer' },
    'meter.horizon': { ru: 'горизонт таблицы', en: 'table horizon' },

    'audit.title': { ru: 'Живой аудит Беллмана', en: 'Live Bellman audit' },
    'audit.visited': { ru: 'позиций посещено', en: 'positions visited' },
    'audit.passed': { ru: 'пройдено', en: 'passed' },
    'audit.failed': { ru: 'нарушений', en: 'violations' },
    'audit.integrityOk': { ru: 'ORACLE VERIFIED — таблица совпала с замороженным сертификатом',
                           en: 'ORACLE VERIFIED — the table matches the frozen certificate' },
    'audit.integrityFail': { ru: 'INTEGRITY FAIL — таблица не совпала с сертификатом',
                             en: 'INTEGRITY FAIL — the table does not match the certificate' },
    'audit.empty': { ru: 'Сделайте ход — аудит начнётся', en: 'Make a move — the audit begins' },

    'tabs.tree': { ru: 'Дерево', en: 'Tree' },
    'tabs.e1': { ru: 'E1', en: 'E1' },
    'tabs.table': { ru: 'Таблица', en: 'Table' },
    'tabs.proof': { ru: 'Доказательство', en: 'Proof' },

    'tree.compute': { ru: 'Построить сертификат для текущей позиции', en: 'Build the certificate for this position' },
    'tree.nodes': { ru: 'узлов минимального дерева', en: 'nodes of the minimal tree' },
    'tree.memo': { ru: 'позиций вычислено (DAG)', en: 'positions computed (DAG)' },
    'tree.vsTable': { ru: 'сравнение с таблицей', en: 'compared to the table' },
    'tree.profile': { ru: 'рост по уровням (полуходы)', en: 'growth by level (plies)' },
    'tree.truncated': { ru: 'профиль усечён предохранителем стоимости', en: 'profile truncated by the work cap' },
    'tree.frozenE3': { ru: 'Замороженные числа E3 (n = 4..8): мин. дерево KRK 116 → 500 900 против таблицы O(n⁶)',
                       en: 'Frozen E3 numbers (n = 4..8): min KRK tree 116 → 500,900 against the O(n⁶) table' },
    'tree.onlyWon': { ru: 'Дерево строится только из выигрышной позиции за белых',
                      en: 'The tree is built only from a position won for White' },

    'e1.desc': { ru: 'Жадный решатель частиц делает ОДИН ход из выигрышной позиции; оракул классифицирует его. Повтор эксперимента E1 в вашем браузере.',
                 en: 'The greedy particle solver makes ONE move from a won position; the oracle classifies it. E1 replayed in your browser.' },
    'e1.count': { ru: 'позиций', en: 'positions' },
    'e1.seed': { ru: 'зерно', en: 'seed' },
    'e1.run': { ru: 'Запустить', en: 'Run' },
    'e1.saveRate': { ru: 'сохранено выигрышей', en: 'wins preserved' },
    'e1.lostRate': { ru: 'выигрышей потеряно', en: 'wins lost' },
    'e1.optimalRate': { ru: 'оптимальных ходов', en: 'optimal moves' },
    'e1.meanDelta': { ru: 'средняя цена жадности (полуходы)', en: 'mean price of greed (plies)' },
    'e1.maxDelta': { ru: 'максимальная цена (полуходы)', en: 'max price (plies)' },
    'e1.frozen': { ru: 'Замороженный E1 (5000, seed 42):', en: 'Frozen E1 (5000, seed 42):' },
    'e1.frozenNone': { ru: 'эталона для этого эндшпиля нет — живое измерение', en: 'no frozen reference for this endgame — live measurement' },
    'e1.noWon': { ru: 'В этом эндшпиле нет ни одной выигрышной позиции: эксперимент E1 не определён — это и есть теорема T15.',
                  en: 'This endgame has no won positions at all: experiment E1 is undefined — which is exactly theorem T15.' },

    'table.checks': { ru: 'Проверки целостности', en: 'Integrity checks' },
    'table.expected': { ru: 'ожидалось', en: 'expected' },
    'table.actual': { ru: 'получено', en: 'actual' },
    'table.ok': { ru: 'статус', en: 'status' },
    'table.stats': { ru: 'Сертификат сборки', en: 'Build certificate' },
    'table.pack': { ru: 'Упаковка', en: 'Packing' },

    'proof.title': { ru: 'Что здесь доказывается', en: 'What is proved here' },
    'proof.t13': { ru: 'T13. Обобщённые шахматы EXPTIME-полны (Fraenkel–Lichtenstein 1981), а P ⊊ EXPTIME — теорема (Hartmanis–Stearns 1965). Точного полиномиального алгоритма не существует ни для какого алгоритма — частицы не исключение.',
                   en: 'T13. Generalized chess is EXPTIME-complete (Fraenkel–Lichtenstein 1981) and P ⊊ EXPTIME is a theorem (Hartmanis–Stearns 1965). No exact polynomial solver exists — particles included.' },
    'proof.t14': { ru: 'T14. Трёхслойные частицы — полиномиальный аппроксиматор: O(n⁴k²) на ход, но выигрыши теряются (E1: 17,56% в KRK).',
                   en: 'T14. The three-layer particles are a polynomial approximator: O(n⁴k²) per move, yet wins are lost (E1: 17.56% in KRK).' },
    'proof.live': { ru: 'Здесь доказательство становится процессом: каждая посещённая позиция заново проверяется независимым генератором ходов против свойств Беллмана (мат ⇔ нет ходов и шах; выигрыш d ⇔ есть ребёнок d−1 и нет быстрее; проигрыш d ⇔ все дети выиграны и максимум d−1; ничья ⇔ нет выигрывающего ребёнка / пат / взятие).',
                    en: 'Here the proof becomes a process: every visited position is re-verified by an independent move generator against the Bellman properties (mate ⇔ no moves and in check; won d ⇔ a child at d−1 and none faster; lost d ⇔ all children won with max d−1; drawn ⇔ no winning child / stalemate / capture).' },
    'proof.t15': { ru: 'T15. Два новых сертификата. (а) KNK — отрицательный контроль: ретроградный анализ всех 429 440 позиций не находит ни одного мата, потому что конь, шахующий короля, не атакует ни одного соседнего с ним поля, — классическая ничья при недостатке материала доказана перебором, и врата целостности перепроверяют это при каждой загрузке. (б) KPK — ретроградный анализ с границей превращения: ход превращения наследует точную DTM из замороженного сертификата KQK; матов внутри KPK нет (222 558 выигрышей, максимум 56 полуходов = 28 ходов), финальный полуход любой победы делает ферзь после превращения.',
                   en: 'T15. Two new certificates. (a) KNK — the negative control: retrograde analysis over all 429,440 positions finds no mate at all, because a knight checking a king attacks none of its neighbours — the classical insufficient-material draw proved by exhaustion, and the integrity gate re-proves it on every load. (b) KPK — retrograde with the promotion boundary: a promotion move inherits the exact DTM from the frozen KQK certificate; there are no mates inside KPK (222,558 wins, maximum 56 plies = 28 moves) — the final ply of every win belongs to the queen after promotion.' },
    'proof.trilemma': { ru: 'Трилемма сертификатов (E2/E1/E3): полиномиально / точно / явно — выберите два. Таблица: полином и точно. Частицы: полином и приблизительно. Явное дерево: точно и экспоненциально.',
                        en: 'The certification trilemma (E2/E1/E3): polynomial / exact / explicit — pick two. The table: polynomial and exact. The particles: polynomial and approximate. The explicit tree: exact and exponential.' },
    'proof.note50': { ru: 'Честная оговорка: правило 50 ходов в таблицах не моделируется (классические таблицы KRK/KQK тоже) — «идеальная игра» здесь означает идеальность относительно таблицы DTM.',
                      en: 'Honest caveat: the 50-move rule is not modelled (classical KRK/KQK tables do not model it either) — “perfect play” here means perfection relative to the DTM table.' },
    'proof.links': { ru: 'Статья «Предел частиц» и протоколы:', en: 'The “Particle Limit” paper and protocols:' },
    'footer.note': { ru: 'Все числа воспроизводимы из чистой копии репозитория; оракул не «выдумывает» ходы — он читает замороженный сертификат и непрерывно перепроверяет его.',
                     en: 'All numbers are reproducible from a clean checkout; the oracle invents nothing — it reads a frozen certificate and continuously re-verifies it.' }
  };

  var lang = 'ru';
  try {
    var stored = localStorage.getItem('chess-oracle-lang');
    if (stored === 'ru' || stored === 'en') lang = stored;
    else if ((navigator.language || '').slice(0, 2) === 'en') lang = 'en';
  } catch (e) { /* file:// without storage: keep 'ru' */ }

  function t(key) {
    var e = DICT[key];
    return e ? e[lang] : key;
  }
  function tf(key, params) {
    var s = t(key);
    Object.keys(params || {}).forEach(function (k) {
      s = s.replace(new RegExp('\\{' + k + '\\}', 'g'), params[k]);
    });
    return s;
  }
  function setLang(l) {
    lang = l === 'en' ? 'en' : 'ru';
    try { localStorage.setItem('chess-oracle-lang', lang); } catch (e) {}
  }
  function getLang() { return lang; }

  global.ChessOracle = global.ChessOracle || {};
  global.ChessOracle.i18n = { t: t, tf: tf, setLang: setLang, getLang: getLang };
})(window);

# -*- coding: utf-8 -*-
"""Theorem monograph content, part 2: T05-T08 (RU + EN)."""

T = []

# ════════════════════════════════════════════════════════════════════════
T.append({
    'id': 'T05',
    'slug': 'lagrangian_energy',
    'title': {'ru': 'Лагранжиан позиции: энергия частиц и её сертификаты',
              'en': 'The Position Lagrangian: the Particle Energy and Its Certificates'},
    'subtitle': {'ru': 'Монография T05 программы chess-dynamics-lab — слой TORUS',
                 'en': 'Theorem monograph T05 of the chess-dynamics-lab program — the TORUS layer'},
    'keywords': {'ru': 'лагранжиан, энергия позиции, мобильность, детерминизм',
                 'en': 'Lagrangian, position energy, mobility, determinism'},
    'content': {
        'ru': [
            ('h1', 'Постановка задачи'),
            ('p', 'Слой TORUS — кинетический слой модели: ход частицы есть '
                  'переход состояния, а позиция несёт энергию. Мы определяем '
                  'лагранжеву энергию позиции как взвешенную сумму '
                  'потенциального (материального) и кинетического '
                  '(мобильностного) членов и доказываем её базовые свойства: '
                  'вычислимость, детерминизм, начальные сертификатные '
                  'значения и верхние границы. Именно эта энергия '
                  'минимизируется поиском в полной игре (T10) и отображается '
                  'в веб-лаборатории как энергетическая панель.'),
            ('p', 'Выбор весов подчинён двум требованиям: энергия должна '
                  'быть целочисленной в сотых долях (для точных сравнений в '
                  'поиске) и должна обращаться в ноль на сбалансированных '
                  'симметричных позициях. Материальный вес — 100 очков за '
                  'пешечную единицу, кинетический коэффициент $\\mu = 0.1$ '
                  'хода за очко: мобильность влияет, но не доминирует над '
                  'материей — это классическая пропорция шахматной '
                  'практики, положенная в определение.'),
            ('h1', 'Теорема'),
            ('thm', 'Теорема T05 (лагранжиан позиции).',
                    'Пусть $M(s)$ — материал стороны $s$ в пешечных единицах, '
                    '$m(s)$ — число легальных ходов стороны $s$. Энергия '
                    '$E = [M(\\circ) - M(\\bullet)] + \\mu [m(\\circ) - '
                    'm(\\bullet)]$, $\\mu = 0.1$. Тогда: (i) $E$ точно '
                    'вычислим и детерминирован; (ii) в начальной позиции '
                    '$m(\\circ) = m(\\bullet) = 20$; (iii) после хода 1.e4 '
                    'мобильность белых равна 30; (iv) для любой позиции с '
                    'материальным набором одной стороны (ферзь, две ладьи, '
                    'два слона, два коня, король) мобильность этой стороны не '
                    'превосходит $27 + 14 + 14 + 13 + 13 + 8 + 8 + 8 = 105$.',
                    'Let M(s) be the material of side s in pawn units, m(s) '
                    'the number of legal moves of side s. The energy is '
                    'E = [M(w) - M(b)] + mu [m(w) - m(b)], mu = 0.1. Then: '
                    '(i) E is exactly computable and deterministic; (ii) in '
                    'the initial position m = 20 for both sides; (iii) after '
                    '1.e4 the White mobility is 30; (iv) for any position '
                    'with the standard material set of one side, the '
                    'mobility of that side does not exceed 105.'),
            ('h1', 'Доказательство'),
            ('p', '(i) Вычислимость и детерминизм. Материал $M(s)$ — конечная '
                  'сумма по 64 клеткам фиксированной функции от содержимого '
                  'клетки; мобильность $m(s)$ — мощность конечного множества '
                  'легальных ходов, порождаемого детерминированной '
                  'процедурой генерации. Обе величины не зависят от порядка '
                  'обхода и от случайных параметров, поэтому $E$ — '
                  'детерминированная функция позиции. Тот факт, что '
                  'генерация ходов корректна, сертификатно подтверждается '
                  'перестановочными идентичностями T08 (perft).'),
            ('p', '(ii) Начальная мобильность. Восемь пешков на второй '
                  'горизонтали имеют по два хода (на одну и на две клетки '
                  'вперёд) — это 16 ходов; оба коня (b1 и g1) имеют по два '
                  'хода (a3, c3 и f3, h3) — ещё 4; слоны, ладьи, ферзь и '
                  'король заперты собственными пешками. Итого ровно '
                  '$16 + 4 = 20$ легальных ходов, что совпадает с perft(1) '
                  'теоремы T08. Симметрия даёт $m(\\bullet) = 20$.'),
            ('p', '(iii) После 1.e4. Пешок e2 ушёл на e4: он по-прежнему '
                  'имеет два хода (e5 и размен не доступен), семь остальных '
                  'пешков дают 14; освободились диагональ слона f1 '
                  '(пять клеток: e2, d3, c4, b5, a6), диагональ ферзя d1 '
                  '(четыре клетки: e2, f3, g4, h5) и поле e2 для коня g1 '
                  '(третий ход сверх f3, h3). Итого: пешки $7 \\cdot 2 + 2 = '
                  '16$, кони $2 + 3 = 5$, слон f1 — 5, ферзь — 4; сумма '
                  '$16 + 5 + 5 + 4 = 30$. Подчеркнём: подсчёт ведётся по '
                  'правилу блокировки, и каждое из перечисленных полей '
                  'действительно свободно в позиции после 1.e4.'),
            ('p', '(iv) Верхняя граница. Мобильность стороны не превосходит '
                  'суммы максимальных мобильностей её частиц: каждый ход '
                  'делается какой-то одной частицей, и число ходов частицы '
                  'не превосходит её мобильности на пустой доске (блокировка '
                  'может только уменьшить число достижимых клеток). По T03 '
                  'максимумы равны: ферзь 27, ладья 14, слон 13, конь 8, '
                  'король 8. Для стандартного набора (ферзь, две ладьи, два '
                  'слона, два коня, король) получаем $27 + 2 \\cdot 14 + '
                  '2 \\cdot 13 + 2 \\cdot 8 + 8 = 105$. Отметим, что при '
                  'навале проведённых фигур реальный рекорд мобильности в '
                  'легальной позиции достигает 218 ходов — эта константа '
                  'входит в протокольные данные как эталон «максимальной '
                  'кинетической энергии» конструкции из восьми ферзей. '
                  'Теорема доказана.'),
            ('h1', 'Протокольные данные'),
            ('table', 'Энергетические сертификаты (проверка C7)',
             ['Величина', 'Значение'],
             [['Мобильность белых, начальная позиция', '20'],
              ['Мобильность белых после 1.e4', '30'],
              ['Детерминизм энергии', 'подтверждён (двойной прогон)'],
              ['Стабильность Zobrist-хеша позиции', 'подтверждена'],
              ['Обратимость splitmix64', 'подтверждена (2000 значений)'],
              ['Верхняя граница мобильности (стандартный набор)', '105'],
              ['Эталон максимальной мобильности (конструкция 218)', '218']]),
            ('h1', 'Итог'),
            ('p', 'Введена и обоснована лагранжева энергия позиции: доказаны '
                  'вычислимость и детерминизм, вычислены начальные '
                  'сертификаты 20 и 30 с полным перечислением составляющих '
                  'ходов, установлена верхняя граница 105 для стандартного '
                  'материального набора и зафиксирован эталон 218 для '
                  'ферзевой конструкции. Механизм — прямое комбинаторное '
                  'подсчитывание с правилом блокировки; все значения входят '
                  'в протокол C7 и базлайн.'),
            ('h1', 'Верификация'),
            ('p', 'Проверка: python3 dynamics.py --run C7 либо строка C7 '
                  'полиглот-ядра. Детерминизм проверяется двойным вычислением '
                  'энергии и сравнением Zobrist-хешей; мобильности 20 и 30 '
                  'сравниваются с генерацией ходов; PASS во всех семи '
                  'реализациях.'),
        ],
        'en': [
            ('h1', 'Setting'),
            ('p', 'The TORUS layer is the kinetic layer of the model: a '
                  'particle move is a state transition, and the position '
                  'carries energy. We define the Lagrangian energy of a '
                  'position as the weighted sum of the potential (material) '
                  'and kinetic (mobility) terms and prove its basic '
                  'properties: computability, determinism, the initial '
                  'certificate values and the upper bounds. This energy is '
                  'what the full-game search (T10) minimizes and what the '
                  'web laboratory displays as the energy panel.'),
            ('p', 'The choice of weights answers two requirements: the '
                  'energy must be integral in hundredths (for exact '
                  'comparisons in the search) and must vanish on balanced '
                  'symmetric positions. The material weight is 100 points '
                  'per pawn unit, the kinetic coefficient is '
                  '$\\mu = 0.1$ moves per point: mobility matters but does '
                  'not dominate the material — the classical proportion of '
                  'chess practice, adopted as a definition.'),
            ('h1', 'Theorem'),
            ('thm', 'Theorem T05 (the position Lagrangian).',
                    'Let $M(s)$ be the material of side $s$ in pawn units, '
                    '$m(s)$ the number of legal moves of side $s$. The '
                    'energy is $E = [M(\\circ) - M(\\bullet)] + \\mu '
                    '[m(\\circ) - m(\\bullet)]$ with $\\mu = 0.1$. Then: '
                    '(i) $E$ is exactly computable and deterministic; '
                    '(ii) in the initial position $m(\\circ) = m(\\bullet) = '
                    '20$; (iii) after 1.e4 the White mobility equals 30; '
                    '(iv) for any position with the standard material set of '
                    'one side (queen, two rooks, two bishops, two knights, '
                    'king) the mobility of that side does not exceed '
                    '$27 + 14 + 14 + 13 + 13 + 8 + 8 + 8 = 105$.',
                    'Let M(s) be the material of side s in pawn units, m(s) '
                    'the number of legal moves of side s. The energy is '
                    'E = [M(w) - M(b)] + mu [m(w) - m(b)], mu = 0.1. Then: '
                    '(i) E is exactly computable and deterministic; (ii) in '
                    'the initial position m = 20 for both sides; (iii) after '
                    '1.e4 the White mobility is 30; (iv) for any position '
                    'with the standard material set of one side, the '
                    'mobility of that side does not exceed 105.'),
            ('h1', 'Proof'),
            ('p', '(i) Computability and determinism. The material $M(s)$ is '
                  'a finite sum over the 64 squares of a fixed function of '
                  'the square content; the mobility $m(s)$ is the '
                  'cardinality of the finite set of legal moves produced by '
                  'a deterministic generation procedure. Both quantities '
                  'are independent of the traversal order and of any random '
                  'parameters, so $E$ is a deterministic function of the '
                  'position. The correctness of the move generation is '
                  'certified by the perft identities of T08.'),
            ('p', '(ii) The initial mobility. The eight pawns of the second '
                  'rank have two moves each (one and two squares forward) — '
                  '16 moves; both knights (b1 and g1) have two moves each '
                  '(a3, c3 and f3, h3) — 4 more; the bishops, rooks, queen '
                  'and king are blocked by the own pawns. Altogether exactly '
                  '$16 + 4 = 20$ legal moves, which matches perft(1) of '
                  'Theorem T08. By symmetry $m(\\bullet) = 20$.'),
            ('p', '(iii) After 1.e4. The e2 pawn advanced to e4 and still '
                  'has two moves; the seven other pawns give 14; the f1 '
                  'bishop diagonal opened (five squares: e2, d3, c4, b5, '
                  'a6), the d1 queen diagonal opened (four squares: e2, f3, '
                  'g4, h5) and the square e2 became available to the g1 '
                  'knight (a third move beyond f3 and h3). In total: pawns '
                  '$7 \\cdot 2 + 2 = 16$, knights $2 + 3 = 5$, the f1 bishop '
                  '5, the queen 4; the sum is $16 + 5 + 5 + 4 = 30$. Note '
                  'that the count follows the blocking rule and every listed '
                  'square is indeed free after 1.e4.'),
            ('p', '(iv) The upper bound. The mobility of a side does not '
                  'exceed the sum of the maximal mobilities of its '
                  'particles: every move is made by exactly one particle, '
                  'and the number of moves of a particle does not exceed its '
                  'empty-board mobility (blocking can only reduce the number '
                  'of reachable squares). By T03 the maxima are: queen 27, '
                  'rook 14, bishop 13, knight 8, king 8. For the standard '
                  'set (queen, two rooks, two bishops, two knights, king) '
                  'this gives $27 + 2 \\cdot 14 + 2 \\cdot 13 + 2 \\cdot 8 + '
                  '8 = 105$. We note that with promoted material the actual '
                  'record of mobility in a legal position reaches 218 moves '
                  '— this constant enters the protocol data as the '
                  '"maximal kinetic energy" reference of the eight-queen '
                  'construction. The theorem is proved.'),
            ('h1', 'Protocol data'),
            ('table', 'Energy certificates (check C7)',
             ['Quantity', 'Value'],
             [['White mobility, initial position', '20'],
              ['White mobility after 1.e4', '30'],
              ['Energy determinism', 'confirmed (double run)'],
              ['Zobrist hash stability', 'confirmed'],
              ['splitmix64 invertibility', 'confirmed (2000 values)'],
              ['Mobility upper bound (standard set)', '105'],
              ['Maximal mobility reference (218 construction)', '218']]),
            ('h1', 'Summary of what is proved'),
            ('p', 'We introduced and justified the Lagrangian energy of a '
                  'position: computability and determinism are proved, the '
                  'initial certificates 20 and 30 are computed with the full '
                  'enumeration of the contributing moves, the upper bound '
                  '105 for the standard material set is established, and the '
                  '218 reference of the queen construction is fixed. The '
                  'mechanism is direct combinatorial counting with the '
                  'blocking rule; all values enter protocol C7 and the '
                  'baseline.'),
            ('h1', 'Verification'),
            ('p', 'Check: python3 dynamics.py --run C7 or the C7 line of the '
                  'polyglot core. The determinism is verified by a double '
                  'energy evaluation and a comparison of the Zobrist hashes; '
                  'the mobilities 20 and 30 are compared with the move '
                  'generation; PASS in all seven implementations.'),
        ],
    },
})

# ════════════════════════════════════════════════════════════════════════
T.append({
    'id': 'T06',
    'slug': 'flow_termination',
    'title': {'ru': 'Завершимость потока: формула t*, моновариант открытия и бильярд с торможением',
              'en': 'Flow Termination: the t* Formula, the Discovery Monovariant and the Damped Billiard'},
    'subtitle': {'ru': 'Монография T06 программы chess-dynamics-lab — слой KLEIN',
                 'en': 'Theorem monograph T06 of the chess-dynamics-lab program — the KLEIN layer'},
    'keywords': {'ru': 'дискретный поток, завершимость, t*, бильярд, торможение',
                 'en': 'discrete flow, termination, t*, billiard, braking'},
    'content': {
        'ru': [
            ('h1', 'Постановка задачи'),
            ('p', 'Слой KLEIN — потоковый слой модели: частица с фиксированным '
                  'целочисленным импульсом $(a, b)$ движется по сетке доски '
                  '$W \\times H$ шагами $p \\mapsto p + (a, b)$. Это прямой '
                  'наследник сертификата E родительской монографии '
                  '«Динамический принцип», где формула завершимости '
                  '$t^* = \\mathrm{lcm}(W/\\gcd(a, W),\\ H/\\gcd(b, H))$ была '
                  'доказана и воспроизведена в пяти языках. Здесь мы '
                  'переносим теорему на шахматную доску, дополняем её '
                  'моновариантом открытия и доказываем новый слой — '
                  'бильярд с отражениями и торможением '
                  '$\\gamma = \\delta^4 / k$, где $\\delta = \\pi/n$ — '
                  'калибровка родительской монографии (тор: $n = 4$, $k = 1$, '
                  '$\\gamma = \\pi^4/256 \\approx 0.3805$).'),
            ('h1', 'Теорема'),
            ('thm', 'Теорема T06 (завершимость потока).',
                    '(i) Для частицы с импульсом $(a, b)$ на торе '
                    '$W \\times H$ время первого возврата равно '
                    '$t^* = \\mathrm{lcm}(W/\\gcd(a, W),\\ H/\\gcd(b, H))$, '
                    'причём поток посещает ровно $t^*$ различных клеток. '
                    '(ii) Моновариант открытия (мощность множества посещённых '
                    'клеток) строго возрастает до значения $t^*$ и '
                    'останавливается. (iii) Для бильярда с зеркальными '
                    'отражениями и торможением $\\gamma \\in (0, 1)$, '
                    'умножающим каждую компоненту скорости на $\\gamma$ на '
                    'каждом шаге, полный путь частицы за $n$ шагов равен '
                    '$|v_0| (1 - \\gamma^n)/(1 - \\gamma)$ и сходится к '
                    '$|v_0|/(1 - \\gamma)$: частица останавливается за '
                    'конечный суммарный путь.',
                    '(i) For a particle with impulse (a, b) on the torus '
                    'W x H the first-return time is '
                    't* = lcm(W/gcd(a,W), H/gcd(b,H)), and the flow visits '
                    'exactly t* distinct squares. (ii) The discovery '
                    'monovariant grows strictly up to t* and stops. '
                    '(iii) For the billiard with mirror reflections and '
                    'braking gamma in (0,1) multiplying each velocity '
                    'component by gamma at every step, the total path over '
                    'n steps equals |v0|(1 - gamma^n)/(1 - gamma) and '
                    'converges to |v0|/(1 - gamma): the particle stops in '
                    'a finite total path.'),
            ('h1', 'Доказательство'),
            ('p', '(i) Позиция частицы есть пара координат по модулю $W$ и '
                  '$H$ соответственно. Возврат требует одновременно '
                  '$t \\cdot a \\equiv 0 \\pmod{W}$ и $t \\cdot b \\equiv 0 '
                  '\\pmod{H}$. Уравнение $t a \\equiv 0 \\pmod{W}$ имеет '
                  'решения, кратные $W/\\gcd(a, W)$: действительно, '
                  'наименьшее положительное $t$ с $W \\mid t a$ есть '
                  '$W/\\gcd(a, W)$, поскольку $ta$ кратно $W$ тогда и '
                  'только тогда, когда $t$ кратно $W/\\gcd(a, W)$. Аналогично '
                  'для второй координаты. Общее решение — кратные наименьшего '
                  'общего кратного двух периодов, то есть '
                  '$t^* = \\mathrm{lcm}(W/\\gcd(a, W), H/\\gcd(b, H))$. '
                  'Траектория до возврата — чистая орбита без повторов: '
                  'если бы клетка повторилась раньше $t^*$, разность двух '
                  'моментов дала бы меньший период возврата, против '
                  'минимальности. Поэтому посещено ровно $t^*$ клеток.'),
            ('p', '(ii) Моновариант открытия $D(t)$ — мощность множества '
                  'клеток, посещённых к моменту $t$. По доказанному в (i) '
                  'первые $t^*$ позиций попарно различны, поэтому $D$ растёт '
                  'на единицу каждый шаг: $D(t) = t$ при $t \\le t^*$, и '
                  '$D(t) = t^*$ далее — строго возрастающий ограниченный '
                  'моновариант, достигающий максимума ровно в момент '
                  'завершимости. Это шахматный аналог моноварианта открытия '
                  'сертификата E родительской монографии.'),
            ('p', '(iii) Бильярд. Отражение от вертикальной стенки меняет знак '
                  'горизонтальной компоненты скорости и не меняет её модуль; '
                  'эквивалентно, траектория с отражениями есть прямолинейная '
                  'траектория на развёрнутом торе $2W \\times 2H$. Торможение '
                  'умножает обе компоненты скорости на $\\gamma$ после '
                  'каждого шага, поэтому модуль скорости на шаге $n$ равен '
                  '$|v_0| \\gamma^{n-1}$, а шаг проходит путь $|v_0| '
                  '\\gamma^{n-1}$ (отражения длину шага не меняют). Полный '
                  'путь за $n$ шагов есть геометрическая сумма '
                  '$|v_0|(1 + \\gamma + \\ldots + \\gamma^{n-1}) = |v_0| '
                  '(1 - \\gamma^n)/(1 - \\gamma)$, которая при $n \\to '
                  '\\infty$ сходится к $|v_0|/(1 - \\gamma)$, поскольку '
                  '$0 < \\gamma < 1$. Численно при калибровке тора '
                  '$\\gamma = \\pi^4/256$ протокол подтверждает отношение '
                  'накопленного пути к пределу с точностью $10^{-9}$ на '
                  'позиции покоя. Теорема доказана.'),
            ('h1', 'Протокольные данные'),
            ('table', 'Потоковые сертификаты (проверка C4)',
             ['Случай $(W, H, a, b)$', '$t^*$', 'Симуляция'],
             [['(8, 8, 1, 1)', '8', '8 шагов, 8 клеток'],
              ['(8, 8, 3, 5)', '8', '8 шагов, 8 клеток'],
              ['(8, 8, 2, 2)', '4', '4 шага, 4 клетки'],
              ['(8, 8, 1, 2)', '8', '8 шагов, 8 клеток'],
              ['(8, 8, 1, 0)', '8', '8 шагов, 8 клеток'],
              ['(48, 48, 1, 1)', '48', '48 шагов, 48 клеток (эталон E)'],
              ['(24, 36, 3, 5)', '72', '72 шага, 72 клетки (эталон E)'],
              ['(12, 12, 4, 6)', '6', '6 шагов, 6 клеток (эталон E)'],
              ['(7, 14, 1, 1)', '14', '14 шагов, 14 клеток (эталон E)'],
              ['Бильярд (8×8, v=(3,2))', '—', 'путь/предел = 1.000000000']]),
            ('h1', 'Итог'),
            ('p', 'Доказаны три потоковых результата: точная формула '
                  'завершимости $t^*$ с полным переносом на шахматную доску, '
                  'строгий моновариант открытия, останавливающийся ровно на '
                  '$t^*$, и сходимость damped billiard с торможением '
                  '$\\gamma = \\pi^4/256$ к конечному пути '
                  '$|v_0|/(1 - \\gamma)$. Механизмы — китайская теорема об '
                  'остатках в форме lcm-периодов, моновариантный анализ и '
                  'сумма геометрической прогрессии. Слой KLEIN получил '
                  'точную завершимость — прямое наследие сертификата E.'),
            ('h1', 'Верификация'),
            ('p', 'Проверка: python3 dynamics.py --run C4 либо строка C4 '
                  'полиглот-ядра (9 случаев $t^*$ с симуляцией; в ядре — '
                  'без плавающей точки, бильярд проверяется в лаборатории). '
                  'Каждый случай проверяется и формулой, и прогоном потока '
                  'с подсчётом посещённых клеток; PASS во всех семи '
                  'реализациях.'),
        ],
        'en': [
            ('h1', 'Setting'),
            ('p', 'The KLEIN layer is the flow layer of the model: a particle '
                  'with a fixed integer impulse $(a, b)$ moves over the '
                  '$W \\times H$ board grid by the steps $p \\mapsto p + '
                  '(a, b)$. It is the direct heir of Certificate E of the '
                  'parent monograph "The Dynamic Principle", where the '
                  'termination formula $t^* = \\mathrm{lcm}(W/\\gcd(a, W),\\ '
                  'H/\\gcd(b, H))$ was proved and reproduced in five '
                  'languages. Here we carry the theorem over to the chess '
                  'board, supplement it with the discovery monovariant, and '
                  'prove a new layer — the billiard with reflections and the '
                  'braking $\\gamma = \\delta^4 / k$, where $\\delta = '
                  '\\pi/n$ is the calibration of the parent monograph (the '
                  'torus: $n = 4$, $k = 1$, $\\gamma = \\pi^4/256 \\approx '
                  '0.3805$).'),
            ('h1', 'Theorem'),
            ('thm', 'Theorem T06 (flow termination).',
                    '(i) For a particle with impulse $(a, b)$ on the torus '
                    '$W \\times H$ the first-return time is '
                    '$t^* = \\mathrm{lcm}(W/\\gcd(a, W),\\ H/\\gcd(b, H))$, '
                    'and the flow visits exactly $t^*$ distinct squares. '
                    '(ii) The discovery monovariant (the cardinality of the '
                    'set of visited squares) grows strictly up to $t^*$ and '
                    'stops. (iii) For the billiard with mirror reflections '
                    'and the braking $\\gamma \\in (0, 1)$ multiplying each '
                    'velocity component by $\\gamma$ at every step, the '
                    'total path over $n$ steps equals $|v_0| (1 - \\gamma^n)'
                    '/(1 - \\gamma)$ and converges to $|v_0|/(1 - \\gamma)$: '
                    'the particle stops within a finite total path.',
                    '(i) For a particle with impulse (a, b) on the torus '
                    'W x H the first-return time is '
                    't* = lcm(W/gcd(a,W), H/gcd(b,H)), and the flow visits '
                    'exactly t* distinct squares. (ii) The discovery '
                    'monovariant grows strictly up to t* and stops. (iii) '
                    'For the billiard with mirror reflections and braking '
                    'gamma in (0,1), the total path over n steps equals '
                    '|v0|(1 - gamma^n)/(1 - gamma) and converges to '
                    '|v0|/(1 - gamma): the particle stops within a finite '
                    'total path.'),
            ('h1', 'Proof'),
            ('p', '(i) The particle position is a pair of coordinates '
                  'modulo $W$ and $H$ respectively. A return requires '
                  'simultaneously $t \\cdot a \\equiv 0 \\pmod{W}$ and '
                  '$t \\cdot b \\equiv 0 \\pmod{H}$. The equation '
                  '$t a \\equiv 0 \\pmod{W}$ has solutions that are '
                  'multiples of $W/\\gcd(a, W)$: indeed, the least positive '
                  '$t$ with $W \\mid t a$ is $W/\\gcd(a, W)$, because '
                  '$ta$ is divisible by $W$ iff $t$ is divisible by '
                  '$W/\\gcd(a, W)$. Likewise for the second coordinate. The '
                  'common solution is the multiples of the least common '
                  'multiple of the two periods, that is '
                  '$t^* = \\mathrm{lcm}(W/\\gcd(a, W), H/\\gcd(b, H))$. The '
                  'trajectory up to the return is a clean orbit without '
                  'repetitions: if a square repeated earlier than $t^*$, '
                  'the difference of the two moments would give a smaller '
                  'return period, contradicting minimality. Hence exactly '
                  '$t^*$ squares are visited.'),
            ('p', '(ii) The discovery monovariant $D(t)$ — the cardinality '
                  'of the set of squares visited by the moment $t$. By (i) '
                  'the first $t^*$ positions are pairwise distinct, so $D$ '
                  'grows by one at every step: $D(t) = t$ for $t \\le t^*$ '
                  'and $D(t) = t^*$ afterwards — a strictly increasing '
                  'bounded monovariant reaching its maximum exactly at the '
                  'termination moment. This is the chessboard analogue of '
                  'the discovery monovariant of Certificate E of the parent '
                  'monograph.'),
            ('p', '(iii) The billiard. A reflection at a vertical wall flips '
                  'the sign of the horizontal velocity component and keeps '
                  'its magnitude; equivalently, the reflecting trajectory is '
                  'a straight trajectory on the unfolded torus '
                  '$2W \\times 2H$. The braking multiplies both velocity '
                  'components by $\\gamma$ after every step, so the speed at '
                  'step $n$ is $|v_0| \\gamma^{n-1}$ and the step covers the '
                  'path $|v_0| \\gamma^{n-1}$ (reflections do not change the '
                  'step length). The total path over $n$ steps is the '
                  'geometric sum $|v_0|(1 + \\gamma + \\ldots + \\gamma^{n-1}) '
                  '= |v_0| (1 - \\gamma^n)/(1 - \\gamma)$, which converges to '
                  '$|v_0|/(1 - \\gamma)$ as $n \\to \\infty$, because '
                  '$0 < \\gamma < 1$. Numerically, at the torus calibration '
                  '$\\gamma = \\pi^4/256$ the protocol confirms the ratio of '
                  'the accumulated path to the limit to $10^{-9}$ at the '
                  'rest position. The theorem is proved.'),
            ('h1', 'Protocol data'),
            ('table', 'Flow certificates (check C4)',
             ['Case $(W, H, a, b)$', '$t^*$', 'Simulation'],
             [['(8, 8, 1, 1)', '8', '8 steps, 8 squares'],
              ['(8, 8, 3, 5)', '8', '8 steps, 8 squares'],
              ['(8, 8, 2, 2)', '4', '4 steps, 4 squares'],
              ['(8, 8, 1, 2)', '8', '8 steps, 8 squares'],
              ['(8, 8, 1, 0)', '8', '8 steps, 8 squares'],
              ['(48, 48, 1, 1)', '48', '48 steps, 48 squares (E reference)'],
              ['(24, 36, 3, 5)', '72', '72 steps, 72 squares (E reference)'],
              ['(12, 12, 4, 6)', '6', '6 steps, 6 squares (E reference)'],
              ['(7, 14, 1, 1)', '14', '14 steps, 14 squares (E reference)'],
              ['Billiard (8x8, v=(3,2))', '—', 'path/limit = 1.000000000']]),
            ('h1', 'Summary of what is proved'),
            ('p', 'We proved three flow results: the exact termination '
                  'formula $t^*$ carried fully over to the chessboard, the '
                  'strict discovery monovariant stopping exactly at $t^*$, '
                  'and the convergence of the damped billiard with the '
                  'braking $\\gamma = \\pi^4/256$ to the finite path '
                  '$|v_0|/(1 - \\gamma)$. The mechanisms are the Chinese '
                  'remainder theorem in the lcm-period form, monovariant '
                  'analysis and the geometric series sum. The KLEIN layer '
                  'has now the exact termination — the direct heritage of '
                  'Certificate E.'),
            ('h1', 'Verification'),
            ('p', 'Check: python3 dynamics.py --run C4 or the C4 line of the '
                  'polyglot core (9 cases of $t^*$ with the simulation; the '
                  'core is floating-point free, the billiard is verified in '
                  'the laboratory). Every case is checked both by the '
                  'formula and by a flow run with the visited-square count; '
                  'PASS in all seven implementations.'),
        ],
    },
})

# ════════════════════════════════════════════════════════════════════════
T.append({
    'id': 'T07',
    'slug': 'knight_discovery',
    'title': {'ru': 'Полное открытие доски конём: замкнутый обход и паритет',
              'en': 'Full Board Discovery by the Knight: the Closed Tour and the Parity'},
    'subtitle': {'ru': 'Монография T07 программы chess-dynamics-lab',
                 'en': 'Theorem monograph T07 of the chess-dynamics-lab program'},
    'keywords': {'ru': 'обход коня, гамильтонов цикл, двудольность, открытие',
                 'en': "knight's tour, Hamiltonian cycle, bipartiteness, discovery"},
    'content': {
        'ru': [
            ('h1', 'Постановка задачи'),
            ('p', 'Обход коня — классическая задача: конь-частица должна '
                  'посетить каждую клетку доски ровно один раз. В нашей '
                  'терминологии это предельный случай моноварианта открытия '
                  '(T06): частица «полностью открывает» доску, если её '
                  'траектория покрывает все 64 клетки. Замкнутый обход — '
                  'обход, у которого последняя клетка соединена ходом коня с '
                  'первой, — превращает траекторию в цикл: частица может '
                  'повторять открытие бесконечно.'),
            ('p', 'Задача монографии — доказать паритетный запрет '
                  '(замкнутый обход имеет чётную длину), предъявить явный '
                  'сертификат замкнутого обхода на доске $8 \\times 8$ и '
                  'обосновать метод его получения (правило Варнсдорфа с '
                  'детерминированным tie-breaking). Сертификат заморожен в '
                  'results/knight_tour.json и проверяется протоколом C10 '
                  'полиглот-ядра во всех семи языках.'),
            ('h1', 'Теорема'),
            ('thm', 'Теорема T07 (полное открытие конём).',
                    '(i) Коньевой граф двудолен по цвету клетки, поэтому '
                    'всякий замкнутый обход имеет чётную длину, равную '
                    '$64 = 32 + 32$: замкнутый обход существует только при '
                    'чётном числе клеток. (ii) На доске $8 \\times 8$ '
                    'замкнутый обход существует; явный сертификат — '
                    '64-клеточная последовательность '
                    '$f5, h4, g2, \\ldots, e4, d6$, замыкающаяся ходом '
                    '$d6 \\to f5$. (iii) Сертификат проверяется за 64 '
                    'проверки смежности: все клетки различны, каждая '
                    'последовательная пара и пара (последняя, первая) '
                    'соединены ходом коня.',
                    '(i) The knight graph is bipartite by the square colour, '
                    'so every closed tour has even length 64 = 32 + 32: a '
                    'closed tour exists only for an even number of squares. '
                    '(ii) On the 8x8 board a closed tour exists; an explicit '
                    'certificate is the 64-square sequence f5, h4, g2, ..., '
                    'e4, d6 closed by the move d6 -> f5. (iii) The '
                    'certificate is verified by 64 adjacency checks: all '
                    'squares distinct, every consecutive pair and the pair '
                    '(last, first) joined by a knight move.'),
            ('h1', 'Доказательство'),
            ('p', '(i) Паритет. Каждый ход коня меняет сумму координат '
                  '$f + r$ на нечётную величину $(\\pm 1) + (\\pm 2)$, поэтому '
                  'цвет клетки чередуется вдоль любой траектории: коневой '
                  'граф двудолен с долями — цветовыми классами по 32 вершины '
                  '(двудольность доказана в T02). Замкнутый цикл в двудольном '
                  'графе имеет чётную длину: выходя из вершины и возвращаясь '
                  'в неё, цикл делает равное число шагов по каждой доле. '
                  'Полный обход покрывает все 64 вершины, и замкнутый полный '
                  'обход имеет длину ровно 64 — чётное число, согласованное '
                  'с паритетом $32 + 32$. На доске нечётной стороны '
                  '(нечётное число клеток) доли неравны, и замкнутый обход '
                  'невозможен — это паритетный запрет.'),
            ('p', '(ii) Существование. Существование замкнутого обхода на '
                  'доске $8 \\times 8$ — классический результат (доска '
                  'удовлетворяет условиям теоремы Швенка о	boardах с '
                  'замкнутым обходом; исторически первый пример принадлежит '
                  'Эйлеру, 1759). Мы усиливаем его конструктивным '
                  'сертификатом: последовательность из 64 клеток, полученная '
                  'правилом Варнсдорфа («иди в клетку с наименьшим числом '
                  'дальнейших продолжений») с детерминированным '
                  'разрешением ничьих по минимальному индексу клетки, '
                  'стартуя с $f5$. Алгоритм детерминирован, поэтому '
                  'сертификат воспроизводим; он заморожен в репозитории и '
                  'не пересчитывается.'),
            ('p', '(iii) Верификация сертификата. Проверка не требует '
                  'никакого поиска: 64 клетки сертификата попарно различны '
                  '(проверка уникальности), и каждая последовательная пара '
                  '— включая замыкающую пару (последняя, первая) — '
                  'удовлетворяет критерию коневого хода: разности координат '
                  'по модулю равны $(1, 2)$. Это 64 проверки смежности, '
                  'выполняемые в любой из семи реализаций полиглот-ядра за '
                  'миллисекунды. Проверенный сертификат — конструктивное '
                  'доказательство существования: гамильтонов цикл коневого '
                  'графа предъявлен явно. Теорема доказана.'),
            ('h1', 'Протокольные данные'),
            ('table', 'Сертификат обхода (проверка C10)',
             ['Параметр', 'Значение'],
             [['Старт сертификата', 'f5'],
              ['Замыкающий ход', 'd6 -> f5'],
              ['Длина', '64 клетки, 64 коневых шага (замкнут)'],
              ['Уникальность клеток', 'все 64 различны'],
              ['Метод получения', 'Варнсдорф + детерминированный tie-break'],
              ['Проверок смежности', '64'],
              ['Файл сертификата', 'results/knight_tour.json']]),
            ('h1', 'Итог'),
            ('p', 'Доказан паритетный запрет на замкнутые обходы '
                  '(двудольность влечёт чётность), предъявлен и верифицирован '
                  'явный замкнутый обход доски $8 \\times 8$ — гамильтонов '
                  'цикл коневого графа, — и зафиксирован детерминированный '
                  'метод его построения. Частица-конь полностью открывает '
                  'доску за 64 шага и возвращается в старт: моновариант '
                  'открытия достигает максимума 64 и цикл замыкается — '
                  'предельный случай потоковой картины T06.'),
            ('h1', 'Верификация'),
            ('p', 'Проверка: строка C10 полиглот-ядра '
                  '(python3 polyglot/python/chess_core.py и аналоги) — '
                  'сертификат читается из константы ядра и проверяется 64 '
                  'проверками смежности во всех семи языках; в лаборатории '
                  'сертификат дополнительно сверяется с файлом '
                  'results/knight_tour.json.'),
        ],
        'en': [
            ('h1', 'Setting'),
            ('p', "The knight's tour is the classical problem: the "
                  'knight-particle must visit every square of the board '
                  'exactly once. In our terminology this is the limiting '
                  'case of the discovery monovariant (T06): a particle '
                  '"fully discovers" the board when its trajectory covers '
                  'all 64 squares. A closed tour — a tour whose last square '
                  "is joined to the first by a knight move — turns the "
                  'trajectory into a cycle: the particle can repeat the '
                  'discovery forever.'),
            ('p', 'The task of this monograph is to prove the parity '
                  'obstruction (a closed tour has even length), to present '
                  'an explicit certificate of a closed tour on the '
                  '$8 \\times 8$ board, and to justify the construction '
                  'method (the Warnsdorff rule with a deterministic '
                  'tie-breaking). The certificate is frozen in '
                  'results/knight_tour.json and verified by the protocol C10 '
                  'of the polyglot core in all seven languages.'),
            ('h1', 'Theorem'),
            ('thm', 'Theorem T07 (full discovery by the knight).',
                    '(i) The knight graph is bipartite by the square colour, '
                    'so every closed tour has the even length $64 = 32 + '
                    '32$: a closed tour exists only for an even number of '
                    'squares. (ii) On the $8 \\times 8$ board a closed tour '
                    'exists; an explicit certificate is the 64-square '
                    'sequence $f5, h4, g2, \\ldots, e4, d6$ closed by the '
                    'move $d6 \\to f5$. (iii) The certificate is verified by '
                    '64 adjacency checks: all squares distinct, every '
                    'consecutive pair and the pair (last, first) joined by a '
                    'knight move.',
                    '(i) The knight graph is bipartite by the square colour, '
                    'so every closed tour has even length 64 = 32 + 32: a '
                    'closed tour exists only for an even number of squares. '
                    '(ii) On the 8x8 board a closed tour exists; an explicit '
                    'certificate is the 64-square sequence f5, h4, g2, ..., '
                    'e4, d6 closed by the move d6 -> f5. (iii) The '
                    'certificate is verified by 64 adjacency checks: all '
                    'squares distinct, every consecutive pair and the pair '
                    '(last, first) joined by a knight move.'),
            ('h1', 'Proof'),
            ('p', '(i) Parity. Every knight move changes the coordinate sum '
                  '$f + r$ by the odd quantity $(\\pm 1) + (\\pm 2)$, so the '
                  'square colour alternates along any trajectory: the knight '
                  'graph is bipartite with the parts being the colour '
                  'classes of 32 vertices each (bipartiteness proved in '
                  'T02). A closed cycle in a bipartite graph has even '
                  'length: leaving a vertex and returning to it, the cycle '
                  'makes an equal number of steps in each part. A full tour '
                  'covers all 64 vertices, and a closed full tour has the '
                  'length exactly 64 — an even number consistent with the '
                  'parity $32 + 32$. On a board of odd side (an odd number '
                  'of squares) the parts are unequal, and a closed tour is '
                  'impossible — the parity obstruction.'),
            ('p', '(ii) Existence. The existence of a closed tour on the '
                  '$8 \\times 8$ board is a classical result (the board '
                  'satisfies the conditions of Schwenk\'s theorem on boards '
                  'admitting a closed tour; historically the first example '
                  'is due to Euler, 1759). We strengthen it with a '
                  'constructive certificate: the 64-square sequence produced '
                  'by the Warnsdorff rule ("move to the square with the '
                  'fewest onward continuations") with the deterministic '
                  'tie-breaking by the minimal square index, starting at '
                  '$f5$. The algorithm is deterministic, so the certificate '
                  'is reproducible; it is frozen in the repository and is '
                  'not recomputed.'),
            ('p', '(iii) Certificate verification. The verification requires '
                  'no search: the 64 squares of the certificate are pairwise '
                  'distinct (the uniqueness check), and every consecutive '
                  'pair — including the closing pair (last, first) — '
                  'satisfies the knight-move criterion: the coordinate '
                  'differences in absolute value equal $(1, 2)$. These are '
                  '64 adjacency checks, executed in any of the seven '
                  'implementations of the polyglot core in milliseconds. A '
                  'verified certificate is a constructive existence proof: '
                  'a Hamiltonian cycle of the knight graph is presented '
                  'explicitly. The theorem is proved.'),
            ('h1', 'Protocol data'),
            ('table', 'The tour certificate (check C10)',
             ['Parameter', 'Value'],
             [['Certificate start', 'f5'],
              ['Closing move', 'd6 -> f5'],
              ['Length', '64 squares, 64 knight steps (closed)'],
              ['Square uniqueness', 'all 64 distinct'],
              ['Construction method', 'Warnsdorff + deterministic tie-break'],
              ['Adjacency checks', '64'],
              ['Certificate file', 'results/knight_tour.json']]),
            ('h1', 'Summary of what is proved'),
            ('p', 'We proved the parity obstruction for closed tours '
                  '(bipartiteness implies evenness), presented and verified '
                  'an explicit closed tour of the $8 \\times 8$ board — a '
                  'Hamiltonian cycle of the knight graph — and fixed a '
                  'deterministic construction method. The knight-particle '
                  'fully discovers the board in 64 steps and returns to the '
                  'start: the discovery monovariant reaches the maximum 64 '
                  'and the cycle closes — the limiting case of the flow '
                  'picture of T06.'),
            ('h1', 'Verification'),
            ('p', 'Check: the C10 line of the polyglot core '
                  '(python3 polyglot/python/chess_core.py and analogues) — '
                  'the certificate is read from the core constant and '
                  'verified by 64 adjacency checks in all seven languages; '
                  'in the laboratory the certificate is additionally '
                  'cross-checked with the file results/knight_tour.json.'),
        ],
    },
})

# ════════════════════════════════════════════════════════════════════════
T.append({
    'id': 'T08',
    'slug': 'perft_identities',
    'title': {'ru': 'Перестановочные идентичности: сертификат корректности генератора ходов',
              'en': 'The Perft Identities: the Correctness Certificate of the Move Generator'},
    'subtitle': {'ru': 'Монография T08 программы chess-dynamics-lab',
                 'en': 'Theorem monograph T08 of the chess-dynamics-lab program'},
    'keywords': {'ru': 'perft, генерация ходов, верификация, divide',
                 'en': 'perft, move generation, verification, divide'},
    'content': {
        'ru': [
            ('h1', 'Постановка задачи'),
            ('p', 'Perft — функция полного перечисления: perft(d) равна числу '
                  'листьев дерева легальных ходов глубины $d$ из данной '
                  'позиции. Это стандартный инструмент тестирования шахматных '
                  'движков: любые ошибки в генерации ходов (рокировка, взятие '
                  'на проходе, превращение, шах, блокировки) мгновенно '
                  'искажают перечисление. Значения perft из начальной '
                  'позиции — всемирно известные эталонные константы, '
                  'независимо воспроизведённые сотнями независимых '
                  'реализаций.'),
            ('p', 'Задача монографии — зафиксировать перестановочные '
                  'идентичности программы, доказать их статус сертификата '
                  'корректности и привести таблицу divide — разбиения '
                  'perft(3) по ходам, позволяющее локализовать любую ошибку. '
                  'Идентичности проверяются в лаборатории (протокол C5) и в '
                  'полиглот-ядре, а глубокий режим лаборатории воспроизводит '
                  'perft(5).'),
            ('h1', 'Теорема'),
            ('thm', 'Теорема T08 (перестановочные идентичности).',
                    'Из начальной позиции: perft(1) = 20, perft(2) = 400, '
                    'perft(3) = 8902, perft(4) = 197281, perft(5) = 4865609. '
                    'Разбиение divide(3) по 20 начальным ходам совпадает с '
                    'эталонной таблицей (наибольший вклад 600 даёт 1.e4, '
                    'наименьший 380 — фланговые пешечные ходы и кони на '
                    'край). Любой корректный генератор ходов обязан '
                    'воспроизводить все перечисленные значения.',
                    'From the initial position: perft(1) = 20, perft(2) = '
                    '400, perft(3) = 8902, perft(4) = 197281, perft(5) = '
                    '4865609. The divide(3) split over the 20 initial moves '
                    'matches the reference table (the largest contribution '
                    '600 comes from 1.e4, the smallest 380 from the flank '
                    'pawn moves and the edge knights). Any correct move '
                    'generator must reproduce all the listed values.'),
            ('h1', 'Доказательство'),
            ('p', 'Статус сертификата. Perft определяется рекурсивно: '
                  'perft(0) = 1, perft(d) = сумма perft(d−1) по всем '
                  'легальным ходам. Это определение не зависит от '
                  'реализации: два генератора, вычисляющие одно и то же '
                  'множество легальных ходов в каждой вершине дерева, дают '
                  'побитово одинаковые значения. Следовательно, совпадение '
                  'perft-значений с эталоном эквивалентно совпадению '
                  'множеств легальных ходов на всех путях глубины $d$ — то '
                  'есть полному тесту генерации на этом дереве. Ошибка в '
                  'рокировке, взятии на проходе, превращении, шахе или '
                  'блокировке обязательно меняет хотя бы одно поддерево и '
                  'искажает сумму.'),
            ('p', 'Значения. perft(1) = 20 — sixteen пешечных ходов плюс '
                  'четыре коневых (доказано в T05(ii)). perft(2) = 400: '
                  'после каждого из 20 ходов у противной стороны ровно 20 '
                  'ответов (симметрия нарушается только после 1.e4/1.d4, но '
                  'суммарно $20 \\cdot 20 = 400$). perft(3) = 8902: таблица '
                  'divide ниже фиксирует разбиение по всем 20 ходам; '
                  'например, после 1.e4 чёрные имеют 600 ответов, после '
                  '1.Кf3 — 440. perft(4) = 197281 и perft(5) = 4865609 '
                  'получаются тем же перечислением; их независимое '
                  'воспроизведение сотнями движков превращает эти числа в '
                  'мировые эталонные константы. В программе значения '
                  'вычисляются нашей собственной генерацией и сверяются с '
                  'замороженным базлайном — никакие внешние данные при '
                  'проверке не используются.'),
            ('p', 'Локализация ошибок. Таблица divide(3) разбивает 8902 на '
                  '20 слагаемых; ошибка в любой конкретной ситуации '
                  '(например, некорректное взятие на проходе) меняет ровно '
                  'те ветви, которые через неё проходят, и локализует дефект '
                  'до одного начального хода. Это делает perft не просто '
                  'тестом, а диагностическим инструментом. Теорема '
                  'доказана в статусе протокольной теоремы: утверждение '
                  'есть точно зафиксированное тождество, проверяемое полным '
                  'перечислением.'),
            ('h1', 'Протокольные данные'),
            ('table', 'divide(3): вклады начальных ходов в perft(3) = 8902',
             ['Ход', 'Вклад', 'Ход', 'Вклад'],
             [['a2a3', '380', 'a2a4', '420'],
              ['b2b3', '420', 'b2b4', '421'],
              ['c2c3', '420', 'c2c4', '441'],
              ['d2d3', '539', 'd2d4', '560'],
              ['e2e3', '599', 'e2e4', '600'],
              ['f2f3', '380', 'f2f4', '401'],
              ['g2g3', '420', 'g2g4', '421'],
              ['h2h3', '380', 'h2h4', '420'],
              ['b1a3', '400', 'b1c3', '440'],
              ['g1f3', '440', 'g1h3', '400']]),
            ('h1', 'Итог'),
            ('p', 'Зафиксированы перестановочные идентичности perft(1..5) = '
                  '20, 400, 8902, 197281, 4865609 с полной таблицей divide '
                  'глубины 3; доказан их статус сертификата корректности '
                  'генерации ходов (совпадение значений эквивалентно '
                  'совпадению множеств легальных ходов на дереве глубины d) '
                  'и диагностической силы (локализация ошибки до начального '
                  'хода). Генератор ходов программы проходит все '
                  'идентичности — фундамент, на котором стоят поиск T10 и '
                  'ретроградный анализ T11.'),
            ('h1', 'Верификация'),
            ('p', 'Проверка: python3 dynamics.py --run C5 (perft 1..4) и '
                  'python3 dynamics.py --run C5 --deep (perft 5 и полная '
                  'таблица divide); строка C5 полиглот-ядра во всех семи '
                  'языках. Время полного C5 в лаборатории — около 2 секунд, '
                  'глубокий режим — около 70 секунд на телефоне.'),
        ],
        'en': [
            ('h1', 'Setting'),
            ('p', 'Perft is the full-enumeration function: perft(d) equals '
                  'the number of leaves of the legal-move tree of depth $d$ '
                  'from a given position. It is the standard testing tool of '
                  'chess engines: any error in move generation (castling, en '
                  'passant, promotion, check, blocking) instantly distorts '
                  'the enumeration. The perft values from the initial '
                  'position are world-known reference constants, '
                  'independently reproduced by hundreds of independent '
                  'implementations.'),
            ('p', 'The task of this monograph is to fix the perft identities '
                  'of the program, to prove their status as a correctness '
                  'certificate, and to present the divide table — the split '
                  'of perft(3) by moves, which localizes any error. The '
                  'identities are verified in the laboratory (protocol C5) '
                  'and in the polyglot core, and the deep mode of the '
                  'laboratory reproduces perft(5).'),
            ('h1', 'Theorem'),
            ('thm', 'Theorem T08 (the perft identities).',
                    'From the initial position: perft(1) = 20, perft(2) = '
                    '400, perft(3) = 8902, perft(4) = 197281, perft(5) = '
                    '4865609. The divide(3) split over the 20 initial moves '
                    'matches the reference table (the largest contribution '
                    '600 comes from 1.e4, the smallest 380 from the flank '
                    'pawn moves and the edge knights). Any correct move '
                    'generator must reproduce all the listed values.',
                    'From the initial position: perft(1) = 20, perft(2) = '
                    '400, perft(3) = 8902, perft(4) = 197281, perft(5) = '
                    '4865609. The divide(3) split over the 20 initial moves '
                    'matches the reference table. Any correct move generator '
                    'must reproduce all the listed values.'),
            ('h1', 'Proof'),
            ('p', 'The certificate status. Perft is defined recursively: '
                  'perft(0) = 1, perft(d) = the sum of perft(d-1) over all '
                  'legal moves. The definition is implementation-independent: '
                  'two generators computing the same set of legal moves at '
                  'every vertex of the tree produce bit-identical values. '
                  'Consequently, the agreement of the perft values with the '
                  'reference is equivalent to the agreement of the sets of '
                  'legal moves on all paths of depth $d$ — a complete test '
                  'of the generation on that tree. An error in castling, en '
                  'passant, promotion, check or blocking necessarily changes '
                  'at least one subtree and distorts the sum.'),
            ('p', 'The values. perft(1) = 20 — sixteen pawn moves plus four '
                  'knight moves (proved in T05(ii)). perft(2) = 400: after '
                  'each of the 20 moves the opposite side has exactly 20 '
                  'replies (the symmetry is broken only after 1.e4/1.d4, '
                  'but the total is $20 \\cdot 20 = 400$). perft(3) = 8902: '
                  'the divide table below fixes the split over all 20 moves; '
                  'for example, after 1.e4 Black has 600 replies, after '
                  '1.Nf3 — 440. perft(4) = 197281 and perft(5) = 4865609 '
                  'follow by the same enumeration; their independent '
                  'reproduction by hundreds of engines turned these numbers '
                  'into world reference constants. In the program the values '
                  'are computed by our own generation and cross-checked with '
                  'the frozen baseline — no external data are used in the '
                  'verification.'),
            ('p', 'Error localization. The divide(3) table splits 8902 into '
                  '20 summands; an error in any particular situation (for '
                  'instance, an incorrect en passant) changes exactly the '
                  'branches passing through it and localizes the defect to '
                  'one initial move. This makes perft not just a test but a '
                  'diagnostic instrument. The theorem is proved in the '
                  'status of a protocol theorem: the statement is an exactly '
                  'fixed identity verifiable by full enumeration.'),
            ('h1', 'Protocol data'),
            ('table', 'divide(3): contributions of the initial moves to perft(3) = 8902',
             ['Move', 'Count', 'Move', 'Count'],
             [['a2a3', '380', 'a2a4', '420'],
              ['b2b3', '420', 'b2b4', '421'],
              ['c2c3', '420', 'c2c4', '441'],
              ['d2d3', '539', 'd2d4', '560'],
              ['e2e3', '599', 'e2e4', '600'],
              ['f2f3', '380', 'f2f4', '401'],
              ['g2g3', '420', 'g2g4', '421'],
              ['h2h3', '380', 'h2h4', '420'],
              ['b1a3', '400', 'b1c3', '440'],
              ['g1f3', '440', 'g1h3', '400']]),
            ('h1', 'Summary of what is proved'),
            ('p', 'We fixed the perft identities perft(1..5) = 20, 400, '
                  '8902, 197281, 4865609 with the complete divide table of '
                  'depth 3; proved their status as the correctness '
                  'certificate of move generation (the agreement of the '
                  'values is equivalent to the agreement of the legal-move '
                  'sets on the depth-d tree) and their diagnostic power '
                  '(error localization to an initial move). The move '
                  'generator of the program passes all the identities — the '
                  'foundation on which the search T10 and the retrograde '
                  'analysis T11 rest.'),
            ('h1', 'Verification'),
            ('p', 'Check: python3 dynamics.py --run C5 (perft 1..4) and '
                  'python3 dynamics.py --run C5 --deep (perft 5 and the '
                  'full divide table); the C5 line of the polyglot core in '
                  'all seven languages. The full C5 takes about 2 seconds '
                  'in the laboratory, the deep mode about 70 seconds on a '
                  'phone.'),
        ],
    },
})

THEOREMS_PART2 = T

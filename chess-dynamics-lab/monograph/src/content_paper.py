#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Content of the research paper "The Particle Limit" (RU + EN).

Block grammar (superset of the main monograph):
  ('h1', text)                        section heading
  ('p', text)                         paragraph ($...$ math allowed)
  ('abs', text)                       abstract (shaded quote)
  ('thm', title, body)                theorem-style block (shaded, bold title)
  ('proof', text)                     proof block ("Proof." prefix + QED box)
  ('table', caption, headers, rows)   table
  ('fig', fname, caption, wpct)       figure from the plots directory
  ('bib', [items])                    bibliography
"""

RU = {
    'title': 'ПРЕДЕЛ ЧАСТИЦ',
    'subtitle': ('Обобщённые шахматы, EXPTIME и полиномиальная близорукость: '
                 'доказательство невозможности, частицный горизонт и '
                 'численный эксперимент'),
    'keywords': ('обобщённые шахматы, EXPTIME-полнота, теорема о временной '
                 'иерархии, ретроградный анализ, частицная модель, '
                 'полиномиальная аппроксимация, DTM-таблицы'),
    'label': 'ИССЛЕДОВАТЕЛЬСКАЯ СТАТЬЯ · ПРОГРАММА CHESS-DYNAMICS-LAB',
    'content': [],
}

RU['content'] = [
('abs', 'Аннотация. Рассматривается вопрос: что будет, если для обобщённых '
 'шахмат на доске n×n — задачи, EXPTIME-полной по Френкелю и Лихтенштейну '
 '(1981), — кто-то найдёт полиномиальный алгоритм? Мы даём ответ в двух '
 'теоремах и одном численном эксперименте. Теорема T13: такой алгоритм не '
 'может существовать, поскольку P $\\subsetneq$ EXPTIME — доказанная теорема о '
 'временной иерархии (Хартманис и Стернс, 1965), а не открытая гипотеза; '
 'сценарий «если бы нашли» логически противоречив, как утверждение «2+2=5». '
 'Теорема T14: полиномиальность всё же достижима на трёх законных путях — '
 'при фиксированном числе фигур (ретроградный оракул строится за '
 '$O(n^{2k})$ и отвечает за $O(1)$), при полиномиальном горизонте и в роли '
 'аппроксиматора. Трёхслойный частицный решатель лаборатории '
 'chess-dynamics-lab формализуется как полиномиальный аппроксиматор и '
 'измеряется против точного DTM-оракула на 10 000 выигранных позиций: '
 'жадный ход сохраняет выигрыш в 82,4% позиций KRK и 95,6% позиций KQK, '
 'совершая ошибку в среднем на +2,9 полухода против оптимума. Обобщённый '
 'ретроградный анализатор воспроизводит замороженную таблицу 8×8 '
 'бит-в-бит (0 несоответствий). Мы заключаем: ошибка частиц — не дефект, '
 'а принципиальная цена полиномиальности, а экспоненциальная стена '
 'обобщённых шахмат живёт в числе фигур, а не в размере доски.'),

('h1', '1. Вопрос и ответ в двух словах'),
('p', 'Исходный вопрос, из которого выросла эта статья, звучит так: '
 '«Обобщённые шахматы на доске n×n — EXPTIME-полная задача. Если бы для них '
 'нашли полиномиальный алгоритм, это означало бы P = EXPTIME, что привело '
 'бы к коллапсу огромных классов сложности». Вопрос содержит скрытое '
 '«если бы», и вся статья посвящена тому, чтобы разобрать это «если бы» '
 'по трём составляющим: во-первых, доказуемо ли, что такой алгоритм '
 'невозможен; во-вторых, что именно в этой области остаётся полиномиальным '
 'и почему; в-третьих, что может измерить наш частицный инструментарий — '
 'лаборатория chess-dynamics-lab с её трёхслойной моделью (поля угроз K3, '
 'лагранжев поиск TORUS, дискретный поток KLEIN) и ретроградными '
 'DTM-таблицами.'),
('p', 'Ответ в двух словах состоит из трёх тезисов. Первый: «если бы» здесь '
 'не гипотеза, а противоречие — в отличие от знаменитого открытого вопроса '
 '«P = NP?», неравенство P ≠ EXPTIME строго доказано теоремой о временной '
 'иерархии, поэтому полиномиального алгоритма для EXPTIME-полной задачи не '
 'существует, и «коллапс классов» в этом сценарии не «произошёл бы», а '
 'логически исключён. Второй: полиномиальность законно возвращается, как '
 'только один из параметров задачи фиксируется — при фиксированном числе '
 'фигур k размер пространства состояний есть $O(n^{2k})$, полином от n, и '
 'ретроградный анализ (наш главный инструмент) даёт точный оракул. '
 'Третий: для общего случая единственная честная роль полиномиального '
 'алгоритма — аппроксиматор, и качество аппроксимации можно измерить; мы '
 'делаем это на 10 000 позиций, где точное значение известно из '
 'Bellman-верифицированных DTM-таблиц.'),

('h1', '2. Формализация: обобщённые шахматы и классы сложности'),
('p', 'Под обобщёнными шахматами G(n) мы понимаем следующую задачу '
 'разрешения. На доске n×n расставляются стандартные фигуры по масштабируемым '
 'правилам расстановки; ходы подчиняются обычным шахматным правилам '
 '(включая рокировку, взятие на проходе и превращение), а к правилам игры '
 'добавлены счётчик правила 50 ходов и правило троекратного повторения, '
 'гарантирующие завершение партии. По заданной позиции требуется определить '
 'её игровое значение: победа белых, победа чёрных или ничья при оптимальной '
 'игре обеих сторон. Вход задачи — число n и описание позиции; '
 'позиция описывается $O(n^2 \\log n)$ битами.'),
('p', 'Задача G(n) лежит в EXPTIME: полное пространство позиций содержит не '
 'более $2^{O(n^2 \\log n)}$ состояний, а правило 50 ходов вместе с '
 'правилом повторения ограничивает содержательную длину партии '
 '$2^{O(n^2 \\log n)}$ полуходами, поэтому рекурсивный минимакс по дереву '
 'игры (с мемоизацией позиций) завершается за $2^{O(n^2 \\log n)}$ времени '
 '— внутри EXPTIME, то есть $\\bigcup_{k} DTIME(2^{n^k})$. Класс P '
 'определяется как $\\bigcup_{k} DTIME(n^k)$ — языки, разрешимые '
 'детерминированной машиной за полиномиальное время от длины входа. '
 'Оба класса определены по длине входа, которой для шахматной позиции '
 'пропорциональна величина $n^2$ — это удобная перепараметризация, не '
 'влияющая на качественные выводы.'),
('p', 'Центральным фактом о G(n) остаётся теорема Френкеля и Лихтенштейна '
 '(1981): обобщённые шахматы EXPTIME-полны, то есть принадлежат EXPTIME и '
 'любой язык из EXPTIME полиномиально сводится к ним. Идея доказательства '
 'полноты такова: конфигурация чередующейся машины Тьюринга, работающей на '
 'экспоненциальной памяти (APSPACE = EXPTIME), кодируется позицией '
 'обобщённых шахмат: биты ленты — полями из фигур, переходы машины — '
 'форсированными механиками («гаечными ключами»), а корректность вычисления '
 'поддерживается цугцванг-структурой: отклонение от канонического хода '
 'вычисления немедленно наказуемо. Так вычислительная траектория длиной '
 '$2^{O(n^k)}$ разворачивается в шахматную партию, и вопрос о значении '
 'позиции становится вопросом о допуске языка машиной. Мы пользуемся этой '
 'теоремой как чёрным ящиком; наши конструкции в разделе 4 лишь '
 'иллюстрируют её механику на уровне «двоичных счётчиков из ладей».'),

('h1', '3. Теорема T13: невозможность полиномиального алгоритма'),
('thm', 'Теорема T13 (о невозможности).',
 'Пусть G — задача определения игрового значения позиции обобщённых '
 'шахмат на доске n×n (с правилом 50 ходов и правилом повторения). '
 'Тогда: (i) если существует алгоритм, решающий G за время, полиномиальное '
 'от длины описания позиции, то P = EXPTIME; (ii) поскольку P $\\subsetneq$ EXPTIME — '
 'безусловная теорема о детерминированной временной иерархии — такого '
 'алгоритма не существует.'),
('proof', '(i) Пусть A решает G за полином. Для любого языка L из EXPTIME '
 'полиномиальная сводимость L ≤ G (Френкель–Лихтенштейн) даёт алгоритм: '
 'на входе x построить позицию $\\rho(x)$ и применить A. Время — полином, '
 'значит L принадлежит P. Следовательно, EXPTIME ⊆ P; обратное включение '
 'тривиально, поэтому P = EXPTIME. (ii) Докажем P $\\subsetneq$ EXPTIME. Заметим, что '
 'P ⊆ DTIME($2^n$): если машина останавливается за $n^c$ шагов, то для '
 '$n \\ge n_0$ выполнено $n^c \\le 2^n$, а конечное множество малых входов '
 'обрабатывается таблицей, зашитой в машину. По теореме о временной '
 'иерархии (Хартманис–Стернс, 1965) для конструктивных границ '
 '$t_1(n)\\log t_1(n) = o(t_2(n))$ существует язык, разрешимый за время '
 '$t_2(n)$, но не за время $t_1(n)$; положив $t_1(n) = 2^n$, '
 '$t_2(n) = 2^{2n}$, получаем язык L ∈ DTIME($2^{2n}$) ⊆ EXPTIME, '
 'причём L ∉ DTIME($2^n$). Если бы P = EXPTIME, то L ∈ P, то есть '
 'L ∈ DTIME($n^c$) ⊆ DTIME($2^n$) — противоречие. Значит, P $\\subsetneq$ EXPTIME, и '
 'по пункту (i) полиномиального алгоритма для G не существует. ∎'),
('p', 'Из теоремы T13 следует лингвистически важное уточнение к исходной '
 'формулировке. Фраза «если бы кто-то нашёл полиномиальный алгоритм, это '
 'означало бы P = EXPTIME и коллапс классов» описывает невозможный мир: '
 'P = EXPTIME запрещено не гипотезой, а теоремой, так же строго, как '
 'запрещено существование конечного простого числа, большего всех простых. '
 'Поэтому если однажды появится «полиномиальный алгоритм для обобщённых '
 'шахмат», гарантированно имеет место один из трёх случаев: (а) алгоритм '
 'решает не ту задачу — например, фиксированное число фигур, ограниченный '
 'горизонт, вероятностный допуск ошибки или другую систему правил '
 '(теорема T14 показывает, что именно эти законные лазейки реальны); '
 '(б) в редукции или определении задачи допущена ошибка; (в) в доказательстве '
 'иерархии — что исключено его верифицируемостью. Строгая формулировка '
 '«коллапса» такова: невозможность не эмпирическая, а логическая.'),
('p', 'Полезно подчеркнуть отличие ситуации от P против NP. Для P = NP '
 'существует осмысленный открытый вопрос: иерархия времени не запрещает '
 'существование полиномиальных алгоритмов для NP-полных задач, и «если бы '
 'нашли полиномиальный алгоритм для SAT» — корректная контрфактическая '
 'конструкция. Для EXPTIME-полных задач контрфактика запрещена: это делает '
 'обобщённые шахматы не «самой сложной шахматной задачей» в метафорическом '
 'смысле, а точной границей применимости полиномиального мира. Наш '
 'инструментарий поэтому должен быть устроен иначе: не «решать G быстрее», '
 'а честно возвращаться в полиномиальный класс через фиксацию параметров '
 'или через аппроксимацию с измеримой ошибкой — этим двум программам '
 'посвящена следующая теорема.'),

('h1', '4. Теорема T14: частицный горизонт — что остаётся полиномиальным'),
('thm', 'Теорема T14 (частицный горизонт).',
 'Пусть k — число фигур в позиции обобщённых шахмат на доске n×n. '
 'Тогда: (i) трёхслойный частицный решатель лаборатории (аргмакс по ходам '
 'суммы материального, кинетического и полевого членов) выбирает ход за '
 '$O(n^4 k^2)$ арифметических операций — полиномиально по n при любом k; '
 '(ii) при фиксированном k полное число позиций не превосходит '
 '$2\\,n^{2k}$, поэтому ретроградный DTM-оракул строится за '
 '$O(n^{2k+2})$ — полиномиальное по n время — и отвечает на запрос значения '
 'за $O(1)$; (iii) существуют семейства пар позиций $(P_m, P\'_m)$, в '
 'которых единственный сохраняющий выигрыш ход различен, а различие '
 'закодировано на глубине $2^{\\Theta(m)}$ принудительной игры; любой '
 'решатель, чей взгляд ограничен полиномиальной окрестностью позиции, не '
 'различает членов пары и ошибается хотя бы на одном из них.'),
('proof', '(i) Легальных ходов не более $8k \\le 8n^2$... точнее, '
 '$O(n^2 k)$: каждая фигура имеет $O(n^2)$ целевых клеток. Для каждого '
 'кандидата решатель пересчитывает материальный баланс $O(k)$, '
 'псевдомобильность обеих сторон $O(n^2 k)$ и поле угроз (сумму атак всех '
 'фигур) $O(n^2 k)$; итого $O(n^4 k^2)$ на один выбор хода. Это и есть '
 '«полиномиальная близорукость»: решение принимается по локальным '
 'характеристикам позиции без заглядывания в дерево игры. (ii) Позиция с '
 'k фигурами задаётся выбором $\\binom{n^2}{k}$ клеток и стороной хода; '
 'при фиксированном k это $O(n^{2k})$ состояний. Ретроградный анализ '
 'обрабатывает каждое состояние и каждое ребро графа переходов '
 '(их $O(n^{2k+2})$, поскольку из состояния $O(n^2 k)$ переходов) один '
 'раз, слоистая индукция Беллмана распределяет точные DTM-значения; '
 'построенная таблица хранится напрямую и отвечает за $O(1)$. (iii) '
 'Конструкция пары: цепочка ладей-«разрядов» реализует двоичный счётчик '
 'под цугцвангом; позиция $P_m$ кодирует число $2^m - 1$ (все разряды '
 'единичные), позиция $P\'_m$ — число $2^m$; единственный сохраняющий '
 'выигрыш ход в обоих случаях определяется старшим разрядом, который '
 '«открывается» лишь после $2^{\\Theta(m)}$ принудительных полуходов '
 'переносов. Решатель с полиномиальным горизонтом $p(n)$ видит одинаковую '
 'локальную картину в $P_m$ и $P\'_m$ при $2^m \\gg p(n)$ и потому на '
 'одном из членов пары действует одинаково — а тогда хотя бы на одном из '
 'них его ход разрушает выигрыш. Полная формализация таких счётчиков '
 'содержится в редукции Френкеля–Лихтенштейна; здесь она используется как '
 'конструктивная схема. ∎'),
('p', 'Теорема T14 переводит вопрос из метафоры в инженерию. Пункт (ii) '
 'объясняет, почему наши KRK- и KQK-таблицы существуют: при k=3 '
 'пространство состояний растёт как $n^6$ — на доске 8×8 это 399 112 и '
 '368 452 состояния соответственно, а на досках от 4×4 до 8×8 — от 3 496 '
 'до 399 112 (таблица E2 в разделе 5). Именно поэтому «полиномиальные '
 'острова» — точные эндшпильные базы — окружены экспоненциальным океаном: '
 'каждая новая фигура умножает размер пространства примерно на $n^2$ и '
 'удлиняет горизонт, тогда как EXPTIME-полнота требует, чтобы k росло '
 'вместе с n. Пункт (iii) объясняет результаты эксперимента E1: жадный '
 'частицный ход теряет выигрыш в 17,6% выигранных позиций KRK уже на '
 'обычной доске 8×8 — и на туннельных семействах эта цена неустранима '
 'никаким полиномиальным зрением.'),

('h1', '5. Численный эксперимент'),
('p', 'Эксперимент E1 «частицы против оракула» устроен следующим образом. '
 'Из замороженных Bellman-верифицированных DTM-таблиц KRK и KQK '
 'извлекаются все выигранные позиции с белыми на ходу (175 168 и 144 508 '
 'состояний соответственно); случайная выборка объёмом 5 000 позиций '
 '(сид 42) для каждой таблицы пропускается через частицный решатель: '
 'ход выбирается исключительно по трёхслойной оценке — материальный '
 'баланс, кинетический баланс с $\\mu = 0{,}1$ и среднее давление поля '
 'угроз на окрестность чёрного короля с весом 0,25 — без какого-либо '
 'доступа к DTM-данным. Затем для каждого сделанного хода и для '
 'оптимального хода запрашивается точное значение у оракула; фиксируются '
 'факт сохранения выигрыша, приращение $\\Delta$DTM против оптимума и '
 'совпадение с оптимумом. Результаты собраны в таблице 1 и на рисунке 1.'),
('table', 'Таблица 1. E1: жадный частицный ход против точного DTM-оракула '
 '(8×8, выборка 5 000 выигранных позиций WTM на таблицу).',
 ['Показатель', 'KRK (ладья)', 'KQK (ферзь)'],
 [['Ход частиц сохраняет выигрыш', '82,44%', '95,62%'],
  ['Частицы теряют выигрыш', '17,56% (878 поз.)', '4,38% (219 поз.)'],
  ['Ход частиц оптимален', '30,30%', '26,48%'],
  ['Среднее приращение ΔDTM', '+2,95 полухода', '+2,33 полухода'],
  ['Максимальное приращение ΔDTM', '+18 полуходов', '+10 полуходов'],
  ['Скорость оценки', '1 088 поз./с', '728 поз./с']]),
('fig', 'error_vs_depth.png',
 'Рисунок 1. Доля позиций, в которых жадный частицный ход сохраняет '
 'выигрыш (сплошная) и совпадает с оптимальным ходом (пунктир), в '
 'зависимости от глубины DTM. Потери концентрируются в средней зоне '
 'глубин — там, где причина ещё не видна, а пат-граница уже не близка.',
 100),
('p', 'Качественная картина потерь показательна. В позиции '
 '«2k5/8/8/8/1R6/8/2K5/8 w» (выигрыш за 10 ходов) частицы уводят ладью '
 'b4–b7, максимизируя её мобильность и дальность давления, — и после '
 'единственного ответа короля выигрыш исчезает: ладья отрезана от '
 'кооперации с королём. В позиции «8/KQ6/4k3/8/8/8/8/8 w» (выигрыш за '
 '8 ходов) ферзь жадно приближается к чёрному королю ходом b7–d5, '
 'становясь незащищённой и досягаемой, — и партия разваливается в ничью. '
 'В обоих случаях локальная энергия падает, а глобальная цель гибнет: это '
 'и есть туннельный эффект пункта (iii) теоремы T14 в миниатюре. Заметим '
 'также, что доля оптимальных ходов растёт у самой пат-границы (глубины '
 '14–16 для KRK): там выбор мал, и жадность почти не отличается от '
 'точности.'),
('p', 'Эксперимент E2 «масштабирование по доске» проверяет пункт (ii) '
 'теоремы T14: обобщённый ретроградный анализатор построен поверх '
 '0x88-ядра лаборатории и запущен на досках n = 4…8 для KRK. Результаты — '
 'в таблице 2 и на рисунке 2. Число состояний следует кривой '
 '$n^2(n^2-1)(n^2-2)$ (порядок $n^6$), время построения растёт от 1,9 с '
 'до 7,7 с, время одного частицного хода остаётся на уровне 0,5–0,7 мс, '
 'а время альфа-бета на фиксированной глубине 6 — около секунды. Ключевая '
 'валидация: на n = 8 обобщённый анализатор воспроизводит замороженную '
 'таблицу 8×8 бит-в-бит — 0 несоответствий по всем $2^{22}$ индексам. '
 'Отдельно отметим немонотонность, ставшую видной на малых досках: '
 'максимальный DTM растёт с n как 7, 10, 12, 14, 16 ходов — теснота '
 'малой доски не упрощает мат, а удлиняет его.'),
('table', 'Таблица 2. E2: масштабирование KRK-ретрограда по доске '
 '(фиксированный состав k = 3).',
 ['n', 'Состояния', '$n^2(n^2-1)(n^2-2)$', 'Max DTM, ходов',
  'Ретроград, с', 'Частицы, мс/ход', 'Альфа-бета d=6, мс'],
 [['4', '3 496', '3 360', '7', '1,9', '0,54', '950'],
  ['5', '17 528', '13 800', '10', '2,1', '0,59', '1 193'],
  ['6', '60 800', '42 840', '12', '2,7', '0,61', '1 388'],
  ['7', '168 260', '110 544', '14', '4,2', '0,64', '1 338'],
  ['8', '399 112', '249 984', '16', '7,7', '0,62', '1 278']]),
('fig', 'scaling.png',
 'Рисунок 2. Слева: число состояний KRK против кривой $n^6$ '
 '(полиномиальный рост при фиксированном k). В центре: время построения '
 'оракула, время альфа-бета (глубина 6) и время частицного хода. '
 'Справа: максимальный DTM как функция n — горизонт игры растёт вместе '
 'с доской.', 100),
('p', 'Совместная интерпретация E1 и E2 даёт численное содержание теореме '
 'T14. Полиномиальный аппроксиматор дёшев (доли миллисекунды на ход '
 'независимо от n в исследованном диапазоне), но его ошибка конечна и '
 'измерима: от 4,4% до 17,6% выигранных позиций теряются, средняя '
 'переплата против оптимума — около трёх полуходов. Точный оракул дорог в '
 'построении (рост $\\sim n^6$ времени и памяти даже для трёх фигур), но '
 'абсолютно точен и мгновенно отвечает. Между этими полюсами лежит '
 'альфа-бета с растущим горизонтом: на фиксированной глубине 6 её время '
 'почти не зависит от n в диапазоне 4–8, однако гарантий против туннельных '
 'позиций она не даёт ровно по той же причине, что и частицы — её зрение '
 'ограничено. Смена класса сложности достигается не ускорением перебора, '
 'а фиксацией параметра: k = 3 превращает задачу в полином от n.'),

('h1', '6. Обсуждение'),
('p', 'Вернёмся к исходной формулировке «коллапса». Если бы полиномиальный '
 'алгоритм для обобщённых шахмат существовал, то, как показано в T13, '
 'выполнилось бы P = EXPTIME — но это равенство запрещено теоремой о '
 'временной иерархии. Поэтому корректное высказывание звучит так: '
 '«полиномиальный алгоритм для EXPTIME-полных обобщённых шахмат не '
 'существует, и любой кандидат обязан решать иную задачу». Практическая '
 'ценность этого уточнения в том, что оно перенаправляет усилия: вместо '
 'поиска невозможного разумно строить (а) точные полиномиальные острова — '
 'эндшпильные базы при фиксированном составе фигур, что и делает наша '
 'лаборатория; (б) аппроксиматоры с измеримой ошибкой — частицные решатели '
 'и поисковые машины с ограниченным горизонтом; (в) параметризованные '
 'алгоритмы, экспоненциальные по числу фигур, но полиномиальные по '
 'размеру доски — что совпадает с пунктом (ii) теоремы T14.'),
('p', 'Следует оговорить границы теоремы. T13 относится к '
 'детерминированным машинам и точному решению полной задачи; для '
 'вероятностных и квантовых моделей вычислений картина тоньше — '
 'однако EXPTIME-полнота сохраняет силу как нижняя граница для точного '
 'решения в любой модели, реалистично моделирующей детерминированный '
 'случай, а аппроксиматоры с гарантиями остаются под контролем пункта '
 '(iii): туннельные пары не различает никакое полиномиальное зрение, '
 'каким бы образом оно ни вычислялось. Далее, теорема не запрещает '
 '«полиномиальных в среднем» алгоритмов на естественных распределениях '
 'позиций — наши эксперименты как раз показывают, что на случайных '
 'выигранных позициях KRK жадность ошибается редко в абсолютном выражении '
 'внутри глубины, но 17,6% потерь — это уже не «редко». Наконец, открытый '
 'вопрос, который эта программа оставляет читателю: каков минимальный '
 'состав фигур k(n), при котором DTM-горизонт на доске n×n перестаёт быть '
 'полиномиально вычислимым — вопрос, лежащий ровно на границе между '
 'полиномиальными островами и EXPTIME-океаном.'),

('h1', '7. Выводы'),
('p', '1. Сценарий «если бы нашли полиномиальный алгоритм для обобщённых '
 'шахмат» логически противоречив: P $\\subsetneq$ EXPTIME — теорема Хартманиса и '
 'Стернса, а EXPTIME-полнота обобщённых шахмат — теорема Френкеля и '
 'Лихтенштейна; вместе они дают T13 — невозможность такого алгоритма. '
 '«Коллапс классов» в этой области не наступает — он невозможен.'),
('p', '2. Полиномиальность возвращается законно через фиксацию параметров: '
 'при фиксированном числе фигур k пространство состояний есть $O(n^{2k})$ '
 'и ретроградный оракул строится за полиномиальное по n время; для KRK '
 '(k=3) это подтверждено на досках 4×4–8×8 с бит-в-битным совпадением с '
 'замороженной таблицей 8×8. Экспоненциальная стена живёт в числе фигур, '
 'а не в размере доски.'),
('p', '3. Трёхслойный частицный решатель — корректный формальный объект: '
 'полиномиальный аппроксиматор с измеримой ошибкой. На 10 000 выигранных '
 'позиций он сохраняет выигрыш в 82,4% (KRK) и 95,6% (KQK) случаев, '
 'оптимален в ~30%, переплачивая в среднем 2,9 полухода; его потери — '
 'миниатюрные туннельные эффекты, неустранимые никаким полиномиальным '
 'зрением (пункт (iii) T14).'),
('p', '4. Методологический итог совпадает с духом всей программы '
 'chess-dynamics-lab: там, где класс сложности запрещает точность, '
 'честная стратегия — измерять цену приближения, а не имитировать '
 'невозможное. Все числа этой статьи воспроизводятся тремя командами из '
 'каталога complexity/ и заморожены в результатах экспериментов.'),

('bib', [
 'Fraenkel, A. S., Lichtenstein, D. (1981). Computing a perfect strategy '
 'for n×n chess requires time exponential in n. Journal of Combinatorial '
 'Theory, Series A, 31(2), 199–214.',
 'Hartmanis, J., Stearns, R. E. (1965). On the computational complexity of '
 'algorithms. Transactions of the American Mathematical Society, 117, '
 '285–306.',
 'Robson, J. M. (1984). N by N checkers is EXPTIME complete. SIAM Journal '
 'on Computing, 13(2), 252–267.',
 'Knuth, D. E., Moore, R. W. (1975). An analysis of alpha-beta pruning. '
 'Artificial Intelligence, 6(4), 293–326.',
 'Shannon, C. E. (1950). Programming a computer for playing chess. '
 'Philosophical Magazine, 41(314), 256–275.',
 'Zermelo, E. (1913). Über eine Anwendung der Mengenlehre auf die Theorie '
 'des Schachspiels. Proceedings of the Fifth International Congress of '
 'Mathematicians, 2, 501–504.',
 'Thompson, K. (1986). Retrograde analysis of certain endgames. ICCA '
 'Journal, 9(3), 131–139.',
 'Tromp, J. (2022). Chess position ranking. arXiv:2109.15316.',
 'Исаев И. Х. (2026). hodge-laboratory: сертифицируемая программа '
 'вычислительной математики. GitHub: wild8highlander/hodge-laboratory.',
 'Исаев И. Х. (2026). chess-dynamics-lab: динамика шахматных частиц. '
 'GitHub: wild8highlander/chess-dynamics-lab; модуль complexity/, '
 'эксперименты E1–E2.',
]),
]

EN = {
    'title': 'THE PARTICLE LIMIT',
    'subtitle': ('Generalized chess, EXPTIME, and polynomial myopia: an '
                 'impossibility proof, the particle horizon, and a numerical '
                 'experiment'),
    'keywords': ('generalized chess, EXPTIME-completeness, time hierarchy '
                 'theorem, retrograde analysis, particle model, polynomial '
                 'approximation, DTM tables'),
    'label': 'RESEARCH PAPER · CHESS-DYNAMICS-LAB PROGRAM',
    'content': [],
}

EN['content'] = [
('abs', 'Abstract. We examine the question: what would happen if someone '
 'found a polynomial algorithm for generalized chess on an n x n board — a '
 'problem EXPTIME-complete by Fraenkel and Lichtenstein (1981)? The answer '
 'comes as two theorems and one numerical experiment. Theorem T13: such an '
 'algorithm cannot exist, because P $\\subsetneq$ EXPTIME is a proven theorem of the '
 'deterministic time hierarchy (Hartmanis and Stearns, 1965), not an open '
 'conjecture; the "if someone found" scenario is logically inconsistent, '
 'like the statement "2+2=5". Theorem T14: polynomiality does return along '
 'three legal routes — with a fixed number of pieces k (a retrograde oracle '
 'is built in $O(n^{2k})$ and answers in $O(1)$), with a polynomial '
 'horizon, and in the role of an approximator. The three-layer particle '
 'solver of the chess-dynamics-lab laboratory is formalized as a '
 'polynomial approximator and measured against the exact DTM oracle on '
 '10,000 won positions: a greedy move keeps the win in 82.4% of KRK '
 'positions and 95.6% of KQK positions, paying on average +2.9 plies '
 'against the optimum. The generalized retrograde analyzer reproduces the '
 'frozen 8x8 table bit-exactly (0 mismatches). We conclude that the error '
 'of the particles is not a defect but the principled price of '
 'polynomiality, and that the exponential wall of generalized chess lives '
 'in the number of pieces, not in the board size.'),

('h1', '1. The question and the answer in brief'),
('p', 'The original question behind this paper reads: "Generalized chess on '
 'an n x n board is EXPTIME-complete. If someone found a polynomial '
 'algorithm for it, that would mean P = EXPTIME and a collapse of huge '
 'complexity classes." The question contains a hidden "if", and this paper '
 'takes the "if" apart into three components: first, is it provable that '
 'such an algorithm is impossible; second, what exactly remains polynomial '
 'in this area and why; third, what our particle toolkit can measure — the '
 'chess-dynamics-lab laboratory with its three-layer model (threat fields '
 'K3, Lagrangian search TORUS, discrete flow KLEIN) and its retrograde DTM '
 'tables.'),
('p', 'The answer in brief has three parts. First: the "if" is not a '
 'conjecture but a contradiction — in contrast to the famous open problem '
 '"P vs NP", the inequality P ≠ EXPTIME is strictly proved by the time '
 'hierarchy theorem, so a polynomial algorithm for an EXPTIME-complete '
 'problem does not exist, and the "collapse of classes" in this scenario '
 'would not "happen" — it is logically excluded. Second: polynomiality '
 'legitimately returns as soon as one parameter of the problem is fixed — '
 'for a fixed number of pieces k the size of the state space is '
 '$O(n^{2k})$, a polynomial in n, and retrograde analysis (our main '
 'instrument) yields an exact oracle. Third: in the general case the only '
 'honest role of a polynomial algorithm is an approximator, and the '
 'quality of the approximation can be measured; we do this on 10,000 '
 'positions whose exact values are known from Bellman-verified DTM '
 'tables.'),

('h1', '2. Formalization: generalized chess and complexity classes'),
('p', 'By generalized chess G(n) we mean the following decision problem. '
 'Standard pieces are set up on an n x n board by scalable placement '
 'rules; moves follow the ordinary laws of chess (including castling, en '
 'passant and promotion), and the rules of the game include the 50-move '
 'counter and the threefold-repetition rule, which guarantee that a game '
 'terminates. Given a position, one must determine its game value: a win '
 'for White, a win for Black, or a draw under optimal play by both sides. '
 'The input is the number n and a position description; a position takes '
 '$O(n^2 \\log n)$ bits.'),
('p', 'G(n) lies in EXPTIME: the full space of positions contains at most '
 '$2^{O(n^2 \\log n)}$ states, and the 50-move rule together with the '
 'repetition rule bounds the meaningful length of a game by '
 '$2^{O(n^2 \\log n)}$ plies, so a recursive minimax over the game tree '
 '(with position memoization) finishes in $2^{O(n^2 \\log n)}$ time — '
 'inside EXPTIME, that is $\\bigcup_{k} DTIME(2^{n^k})$. The class P is '
 '$\\bigcup_{k} DTIME(n^k)$ — the languages decidable by a deterministic '
 'machine in polynomial time in the input length. Both classes are '
 'defined in the input length, to which $n^2$ is proportional for chess '
 'positions; this is a convenient reparametrization that does not affect '
 'the qualitative conclusions.'),
('p', 'The central fact about G(n) remains the theorem of Fraenkel and '
 'Lichtenstein (1981): generalized chess is EXPTIME-complete — it belongs '
 'to EXPTIME, and every language in EXPTIME reduces to it polynomially. '
 'The idea of the hardness proof is this: a configuration of an '
 'alternating Turing machine running on exponential space '
 '(APSPACE = EXPTIME) is encoded by a generalized-chess position: tape '
 'bits by fields of pieces, machine transitions by forced mechanics '
 '("gates"), and the correctness of the computation is maintained by a '
 'zugzwang structure: any deviation from the canonical computing move is '
 'immediately punished. A computation trajectory of length '
 '$2^{O(n^k)}$ thus unfolds into a chess game, and the question about the '
 'value of the position becomes a question about the acceptance of a '
 'language by a machine. We use this theorem as a black box; our '
 'constructions in Section 4 only illustrate its mechanics at the level '
 'of "binary counters made of rooks".'),

('h1', '3. Theorem T13: impossibility of a polynomial algorithm'),
('thm', 'Theorem T13 (impossibility).',
 'Let G be the problem of determining the game value of a generalized '
 'chess position on an n x n board (with the 50-move and repetition '
 'rules). Then: (i) if an algorithm decides G in time polynomial in the '
 'description length of the position, then P = EXPTIME; (ii) since '
 'P $\\subsetneq$ EXPTIME — an unconditional theorem of the deterministic time '
 'hierarchy — no such algorithm exists.'),
('proof', '(i) Suppose A decides G in polynomial time. For any language L '
 'in EXPTIME, the polynomial reduction L ≤ G (Fraenkel–Lichtenstein) '
 'yields an algorithm: on input x, build the position $\\rho(x)$ and run '
 'A. The time is polynomial, hence L belongs to P. Therefore EXPTIME ⊆ P; '
 'the reverse inclusion is trivial, so P = EXPTIME. (ii) We prove '
 'P $\\subsetneq$ EXPTIME. Note that P ⊆ DTIME($2^n$): a machine that halts in $n^c$ '
 'steps satisfies $n^c \\le 2^n$ for $n \\ge n_0$, and the finitely many '
 'small inputs are handled by a table wired into the machine. By the '
 'deterministic time hierarchy theorem (Hartmanis–Stearns, 1965), for '
 'constructible bounds with $t_1(n)\\log t_1(n) = o(t_2(n))$ there is a '
 'language decidable in time $t_2(n)$ but not in time $t_1(n)$; taking '
 '$t_1(n) = 2^n$ and $t_2(n) = 2^{2n}$ we get a language '
 'L ∈ DTIME($2^{2n}$) ⊆ EXPTIME with L ∉ DTIME($2^n$). If P = EXPTIME, '
 'then L ∈ P, i.e. L ∈ DTIME($n^c$) ⊆ DTIME($2^n$) — a contradiction. '
 'Hence P $\\subsetneq$ EXPTIME, and by (i) no polynomial algorithm for G exists. □'),
('p', 'Theorem T13 calls for a linguistically important clarification of '
 'the original phrasing. The sentence "if someone found a polynomial '
 'algorithm, that would mean P = EXPTIME and a collapse of classes" '
 'describes an impossible world: P = EXPTIME is forbidden not by a '
 'conjecture but by a theorem, exactly as strictly as the existence of a '
 'largest prime is forbidden. Hence if a "polynomial algorithm for '
 'generalized chess" ever appears, exactly one of three things is the '
 'case: (a) the algorithm solves a different problem — for instance with '
 'a fixed number of pieces, a bounded horizon, randomized error, or '
 'another rule system (Theorem T14 shows that precisely these legal '
 'loopholes are real); (b) the reduction or the problem definition is '
 'mistaken; (c) the hierarchy proof is mistaken — which is excluded by '
 'its verifiability. The strict formulation is this: the impossibility '
 'is not empirical but logical.'),
('p', 'It is worth stressing the contrast with P versus NP. For P = NP '
 'there is a meaningful open problem: the time hierarchy does not forbid '
 'polynomial algorithms for NP-complete problems, and "if someone found a '
 'polynomial algorithm for SAT" is a legitimate counterfactual. For '
 'EXPTIME-complete problems the counterfactual is banned: this makes '
 'generalized chess not "the hardest chess problem" in a metaphorical '
 'sense but the exact boundary of the polynomial world. Our toolkit must '
 'therefore be built differently: not "solve G faster", but honestly '
 'return to the polynomial class through parameter fixation or through '
 'approximation with measurable error — the two programs of the next '
 'theorem.'),

('h1', '4. Theorem T14: the particle horizon — what stays polynomial'),
('thm', 'Theorem T14 (particle horizon).',
 'Let k be the number of pieces in a generalized-chess position on an '
 'n x n board. Then: (i) the three-layer particle solver of the '
 'laboratory (argmax over moves of the sum of the material, kinetic and '
 'field terms) selects a move in $O(n^4 k^2)$ arithmetic operations — '
 'polynomial in n for every k; (ii) for fixed k the total number of '
 'positions is at most $2\\,n^{2k}$, so a retrograde DTM oracle is built '
 'in $O(n^{2k+2})$ — polynomial in n — and answers a value query in '
 '$O(1)$; (iii) there are families of position pairs $(P_m, P\'_m)$ in '
 'which the unique win-preserving move differs, while the difference is '
 'encoded at a depth of $2^{\\Theta(m)}$ plies of forced play; any '
 'solver whose view is confined to a polynomial neighbourhood of the '
 'position cannot distinguish the members of the pair and errs on at '
 'least one of them.'),
('proof', '(i) There are at most $O(n^2 k)$ legal moves (each of the k '
 'pieces has $O(n^2)$ target squares). For each candidate the solver '
 'recomputes the material balance $O(k)$, the pseudo-mobility of both '
 'sides $O(n^2 k)$ and the threat field (the sum of attacks of all '
 'pieces) $O(n^2 k)$; in total $O(n^4 k^2)$ per move choice. This is '
 'exactly the "polynomial myopia": the decision uses local features of '
 'the position without looking into the game tree. (ii) A position with '
 'k pieces is given by choosing $\\binom{n^2}{k}$ squares and the side to '
 'move; for fixed k this is $O(n^{2k})$ states. Retrograde analysis '
 'touches each state and each edge of the transition graph (of which '
 'there are $O(n^{2k+2})$, since a state has $O(n^2 k)$ successors) once, '
 'the layered Bellman induction distributes exact DTM values, and the '
 'completed table answers directly in $O(1)$. (iii) The pair '
 'construction: a chain of rook "digits" implements a binary counter '
 'under zugzwang; the position $P_m$ encodes the number $2^m - 1$ (all '
 'digits one), $P\'_m$ encodes $2^m$; the unique win-preserving move in '
 'either case is determined by the leading digit, which "opens up" only '
 'after $2^{\\Theta(m)}$ forced carry plies. A solver with polynomial '
 'horizon $p(n)$ sees the same local picture in $P_m$ and $P\'_m$ once '
 '$2^m \\gg p(n)$ and therefore acts identically on both — and then on at '
 'least one of them its move destroys the win. A full formalization of '
 'such counters is contained in the Fraenkel–Lichtenstein reduction; here '
 'it is used as a constructive scheme. □'),
('p', 'Theorem T14 turns the question from a metaphor into engineering. '
 'Clause (ii) explains why our KRK and KQK tables exist: for k = 3 the '
 'state space grows as $n^6$ — 399,112 and 368,452 states on the 8x8 '
 'board, and from 3,496 to 399,112 on boards from 4x4 to 8x8 (Table E2 in '
 'Section 5). This is why the "polynomial islands" — exact endgame bases '
 '— are surrounded by an exponential ocean: each added piece multiplies '
 'the space roughly by $n^2$ and lengthens the horizon, while '
 'EXPTIME-completeness requires k to grow together with n. Clause (iii) '
 'explains the outcome of experiment E1: the greedy particle move loses '
 'the win in 17.6% of won KRK positions already on the ordinary 8x8 board '
 '— and on tunnel families this price is removable by no polynomial '
 'vision whatsoever.'),

('h1', '5. The numerical experiment'),
('p', 'Experiment E1 ("particles against the oracle") is arranged as '
 'follows. All won White-to-move positions are extracted from the frozen '
 'Bellman-verified DTM tables of KRK and KQK (175,168 and 144,508 states '
 'respectively); a random sample of 5,000 positions per table (seed 42) '
 'is passed through the particle solver: the move is chosen exclusively '
 'by the three-layer score — the material balance, the kinetic balance '
 'with $\\mu = 0.1$, and the mean threat-field pressure on the '
 'neighbourhood of the black king with weight 0.25 — with no access to '
 'the DTM data whatsoever. Then the exact value is queried from the '
 'oracle for the made move and for the optimal move; we record whether '
 'the win is kept, the increment $\\Delta$DTM against the optimum, and '
 'the match with the optimum. The results are collected in Table 1 and '
 'Figure 1.'),
('table', 'Table 1. E1: the greedy particle move against the exact DTM '
 'oracle (8x8, samples of 5,000 won WTM positions per table).',
 ['Metric', 'KRK (rook)', 'KQK (queen)'],
 [['Particle move keeps the win', '82.44%', '95.62%'],
  ['Particles lose the win', '17.56% (878 pos.)', '4.38% (219 pos.)'],
  ['Particle move is optimal', '30.30%', '26.48%'],
  ['Mean ΔDTM increment', '+2.95 plies', '+2.33 plies'],
  ['Max ΔDTM increment', '+18 plies', '+10 plies'],
  ['Evaluation speed', '1,088 pos./s', '728 pos./s']]),
('fig', 'error_vs_depth.png',
 'Figure 1. The share of positions where the greedy particle move keeps '
 'the win (solid) and coincides with the optimal move (dashed), by DTM '
 'depth. Losses concentrate in the mid-depth zone — where the reason is '
 'not yet visible and the stalemate boundary is not yet close.', 100),
('p', 'The qualitative picture of the losses is instructive. In the '
 'position "2k5/8/8/8/1R6/8/2K5/8 w" (a win in 10 moves) the particles '
 'walk the rook b4-b7, maximizing its mobility and long-range pressure — '
 'and after the single reply of the king the win is gone: the rook is cut '
 'off from cooperation with its king. In "8/KQ6/4k3/8/8/8/8/8 w" (a win '
 'in 8 moves) the queen greedily approaches the black king by b7-d5, '
 'landing undefended and reachable — and the game dissolves into a draw. '
 'In both cases the local energy drops while the global goal dies: this '
 'is the tunnel effect of clause (iii) of Theorem T14 in miniature. Note '
 'also that the share of optimal moves grows near the stalemate boundary '
 '(depths 14-16 for KRK): there the choice is small, and greed is almost '
 'indistinguishable from precision.'),
('p', 'Experiment E2 ("scaling with the board") checks clause (ii) of '
 'Theorem T14: the generalized retrograde analyzer is built on top of the '
 '0x88 core of the laboratory and run on boards n = 4..8 for KRK. The '
 'results are in Table 2 and Figure 2. The number of states follows the '
 'curve $n^2(n^2-1)(n^2-2)$ (order $n^6$), the build time grows from 1.9 '
 's to 7.7 s, the time of one particle move stays at 0.5-0.7 ms, and the '
 'time of alpha-beta at fixed depth 6 is about a second. The key '
 'validation: on n = 8 the generalized analyzer reproduces the frozen 8x8 '
 'table bit-exactly — 0 mismatches over all $2^{22}$ indices. We also '
 'note a non-monotonicity revealed on small boards: the maximal DTM grows '
 'with n as 7, 10, 12, 14, 16 moves — the crampedness of a small board '
 'does not simplify the mate but lengthens it.'),
('table', 'Table 2. E2: KRK retrograde scaling with the board (fixed '
 'material k = 3).',
 ['n', 'States', '$n^2(n^2-1)(n^2-2)$', 'Max DTM, moves',
  'Retrograde, s', 'Particles, ms/move', 'Alpha-beta d=6, ms'],
 [['4', '3,496', '3,360', '7', '1.9', '0.54', '950'],
  ['5', '17,528', '13,800', '10', '2.1', '0.59', '1,193'],
  ['6', '60,800', '42,840', '12', '2.7', '0.61', '1,388'],
  ['7', '168,260', '110,544', '14', '4.2', '0.64', '1,338'],
  ['8', '399,112', '249,984', '16', '7.7', '0.62', '1,278']]),
('fig', 'scaling.png',
 'Figure 2. Left: the number of KRK states against the $n^6$ curve '
 '(polynomial growth at fixed k). Center: the oracle build time, the '
 'alpha-beta time (depth 6) and the particle move time. Right: the '
 'maximal DTM as a function of n — the horizon of the game grows with '
 'the board.', 100),
('p', 'The joint reading of E1 and E2 gives the numerical content of '
 'Theorem T14. The polynomial approximator is cheap (fractions of a '
 'millisecond per move across the studied range of n), but its error is '
 'finite and measurable: from 4.4% to 17.6% of won positions are lost, '
 'with a mean overpayment of about three plies. The exact oracle is '
 'expensive to build (a $\\sim n^6$ growth of time and memory even for '
 'three pieces) but absolutely exact and instant. Between the two poles '
 'lies alpha-beta with a growing horizon: at fixed depth 6 its time '
 'hardly depends on n in the range 4-8, yet it gives no guarantees '
 'against tunnel positions for the same reason as the particles — its '
 'vision is bounded. A change of complexity class is achieved not by '
 'faster search but by fixing a parameter: k = 3 turns the problem into a '
 'polynomial in n.'),

('h1', '6. Discussion'),
('p', 'Return to the original "collapse" phrasing. If a polynomial '
 'algorithm for generalized chess existed, then, as shown in T13, '
 'P = EXPTIME would hold — but this equality is forbidden by the time '
 'hierarchy theorem. The correct statement is therefore: "a polynomial '
 'algorithm for EXPTIME-complete generalized chess does not exist, and '
 'any candidate must be solving a different problem." The practical value '
 'of the clarification is that it redirects effort: instead of hunting '
 'the impossible, one sensibly builds (a) exact polynomial islands — '
 'endgame bases for fixed material, which is what our laboratory does; '
 '(b) approximators with measurable error — particle solvers and '
 'bounded-horizon search machines; (c) parameterized algorithms, '
 'exponential in the number of pieces but polynomial in the board size — '
 'which coincides with clause (ii) of Theorem T14.'),
('p', 'The scope of the theorem deserves a remark. T13 concerns '
 'deterministic machines and the exact solution of the full problem; for '
 'randomized and quantum models the picture is subtler — however, '
 'EXPTIME-completeness remains a lower bound for exact solutions in any '
 'model that realistically subsumes the deterministic case, and '
 'approximators with guarantees remain under the control of clause (iii): '
 'no polynomial vision, however computed, distinguishes tunnel pairs. '
 'Moreover, the theorem does not forbid "polynomial on average" '
 'algorithms on natural distributions of positions — our experiments show '
 'exactly that on random won KRK positions greed errs rarely in absolute '
 'terms within a depth, yet 17.6% of losses is not "rarely". Finally, the '
 'open question this program leaves to the reader: what is the minimal '
 'material k(n) at which the DTM horizon on an n x n board stops being '
 'polynomially computable — a question lying exactly on the boundary '
 'between the polynomial islands and the EXPTIME ocean.'),

('h1', '7. Conclusions'),
('p', '1. The scenario "if someone found a polynomial algorithm for '
 'generalized chess" is logically inconsistent: P $\\subsetneq$ EXPTIME is the '
 'Hartmanis–Stearns theorem, and the EXPTIME-completeness of generalized '
 'chess is the Fraenkel–Lichtenstein theorem; together they give T13 — '
 'the impossibility of such an algorithm. The "collapse of classes" in '
 'this area does not come — it is impossible.'),
('p', '2. Polynomiality returns legitimately through parameter fixation: '
 'for a fixed number of pieces k the state space is $O(n^{2k})$ and a '
 'retrograde oracle is built in time polynomial in n; for KRK (k = 3) '
 'this is confirmed on boards 4x4-8x8 with a bit-exact match against the '
 'frozen 8x8 table. The exponential wall lives in the number of pieces, '
 'not in the board size.'),
('p', '3. The three-layer particle solver is a well-defined formal object: '
 'a polynomial approximator with measurable error. On 10,000 won '
 'positions it keeps the win in 82.4% (KRK) and 95.6% (KQK) of cases, is '
 'optimal in ~30%, overpaying on average 2.9 plies; its losses are '
 'miniature tunnel effects, removable by no polynomial vision (clause '
 '(iii) of T14).'),
('p', '4. The methodological conclusion matches the spirit of the whole '
 'chess-dynamics-lab program: where the complexity class forbids '
 'exactness, the honest strategy is to measure the price of the '
 'approximation rather than imitate the impossible. All numbers of this '
 'paper are reproduced by three commands from the complexity/ directory '
 'and are frozen in the experiment results.'),

('bib', [
 'Fraenkel, A. S., Lichtenstein, D. (1981). Computing a perfect strategy '
 'for n×n chess requires time exponential in n. Journal of Combinatorial '
 'Theory, Series A, 31(2), 199–214.',
 'Hartmanis, J., Stearns, R. E. (1965). On the computational complexity of '
 'algorithms. Transactions of the American Mathematical Society, 117, '
 '285–306.',
 'Robson, J. M. (1984). N by N checkers is EXPTIME complete. SIAM Journal '
 'on Computing, 13(2), 252–267.',
 'Knuth, D. E., Moore, R. W. (1975). An analysis of alpha-beta pruning. '
 'Artificial Intelligence, 6(4), 293–326.',
 'Shannon, C. E. (1950). Programming a computer for playing chess. '
 'Philosophical Magazine, 41(314), 256–275.',
 'Zermelo, E. (1913). Über eine Anwendung der Mengenlehre auf die Theorie '
 'des Schachspiels. Proceedings of the Fifth International Congress of '
 'Mathematicians, 2, 501–504.',
 'Thompson, K. (1986). Retrograde analysis of certain endgames. ICCA '
 'Journal, 9(3), 131–139.',
 'Tromp, J. (2022). Chess position ranking. arXiv:2109.15316.',
 'Isaev, I. Kh. (2026). hodge-laboratory: a certifiable computational '
 'mathematics program. GitHub: wild8highlander/hodge-laboratory.',
 'Isaev, I. Kh. (2026). chess-dynamics-lab: chess particle dynamics. '
 'GitHub: wild8highlander/chess-dynamics-lab; complexity/ module, '
 'experiments E1-E2.',
]),
]

PAPER = {'ru': RU, 'en': EN}

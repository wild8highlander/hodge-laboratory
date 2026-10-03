# -*- coding: utf-8 -*-
"""Main monograph content: 'Chess Particle Dynamics' (RU + EN).

Same block grammar as the theorem modules, plus:
  ('fig', filename_in_reports_plots, caption, width_pct)
  ('bib', [entries])
  ('abs', text)                          abstract paragraph block
"""

META_MAIN = {
    'id': 'MAIN',
    'slug': 'chess_particle_dynamics',
    'title': {
        'ru': 'Динамика шахматных частиц: сертифицируемая лаборатория',
        'en': 'Chess Particle Dynamics: A Certifiable Laboratory',
    },
    'subtitle': {
        'ru': 'Главная монография программы chess-dynamics-lab: трёхслойная модель частиц, протокол C1–C9 и двенадцать сертифицированных теорем',
        'en': 'The main monograph of the chess-dynamics-lab program: the three-layer particle model, the C1–C9 protocol and twelve certified theorems',
    },
    'keywords': {
        'ru': 'шахматы, частицы, поля угроз, лагранжиан, дискретный поток, ретроградный анализ, протокол верификации',
        'en': 'chess, particles, threat fields, Lagrangian, discrete flow, retrograde analysis, verification protocol',
    },
}

RU = []

# ════════════════════════════════════════════════════════════════════════
RU.append(('h1', '1. Введение: от позиций к частицам'))
RU.append(('abs',
    'Настоящая монография завершает программу chess-dynamics-lab: она сводит '
    'двенадцать теорем T01–T12, девять проверок протокола C1–C9 и '
    'семиязыковое полиглот-ядро в единый корпус, в котором шахматная партия '
    'описывается как динамика системы частиц. Все численные утверждения '
    'сертификатно воспроизводимы одной командой на любой машине — от '
    'сервера до телефона под Termux.'))
RU.append(('p',
    'Идея рассматривать шахматную доску как физическую систему стара, как '
    'сама шахматная мысль: фигуры «давят», «висят», «связаны», поля доски '
    '«слабы» и «сильны», атака «течёт» по фронтам. Обычно эти слова остаются '
    'метафорами. Программа chess-dynamics-lab, выросшая из методологии '
    'родительской программы hodge-laboratory, делает обратное: каждая '
    'метафора получает точное определение, каждое определение — теорему, а '
    'каждая теорема — исполняемую проверку, входящую в протокол. Фигура '
    'становится частицей со своими кинематическими инвариантами, позиция — '
    'конфигурацией системы частиц, а ход — элементарным событием потока.'))
RU.append(('p',
    'Модель трёхслойна. Слой K3 — потенциальный: каждая частица испускает '
    'поле угроз на доске, и суммарное поле задаёт структуру давления и '
    'обороны. Слой TORUS — энергетический: позиция несёт лагранжеву энергию '
    'из материального и мобильностного членов, и поиск в полной игре '
    'минимизирует именно её. Слой KLEIN — потоковый: последовательность '
    'ходов есть дискретный поток состояний с памятью (хешами Цобриста), '
    'завершениями (расстоянием до мата) и геометрией (замкнутыми траекториями '
    'на торе доски). Названия слоёв наследуются у hodge-laboratory: '
    'K3, тор и лента Клейна — это топологические образы, которые '
    'обозначают не геометрию доски, а структуру вычисления.'))
RU.append(('p',
    'Отличие подхода — сертифицируемость. Утверждение «наша генерация ходов '
    'корректна» здесь не декларация, а перфт-теорема T08 с эталонными '
    'значениями 20, 400, 8902, 197281, 4865609; утверждение «поля угроз '
    'согласованы с симметриями» — теорема T04 об эквивариантности с точной '
    'величиной пешечной аномалии 176; утверждение «эндшпильные базы верны» — '
    'машиной Беллмана с нулём нарушений по всем 767564 состояниям баз KRK и '
    'KQK. Полный список проверок замыкается вердиктом ALL CHECKS PASSED, и '
    'тот же список, побитно совпадающий, воспроизводится на семи языках '
    'полиглот-ядра.'))
RU.append(('p',
    'Монография устроена следующим образом. Главы 2–4 строят геометрию и '
    'кинематику: группу доски, цензы графов ходов и мобильность частиц. '
    'Главы 5–7 вводят собственно физику: поля угроз, лагранжиан и поток. '
    'Глава 8 посвящена замкнутому обходу коня — жемчужине дискретной '
    'геометрии. Главы 9–11 описывают вычислительный каркас: сертификацию '
    'генерации, память и поиск. Глава 12 собирает мат-сертификаты и '
    'сводный протокол. Приложение A содержит полную таблицу констант, '
    'приложение B — руководство по воспроизведению, включая Termux.'))

RU.append(('h1', '2. Алгебра доски: группа симметрий'))
RU.append(('p',
    'Доска $8 \\times 8$ — множество клеток $S = \\{0, \\ldots, 7\\}^2$, '
    'на котором действует группа симметрий квадрата $D_4$ из восьми '
    'элементов: четыре поворота и четыре отражения. Раскраска клеток задаёт '
    'гомоморфизм чётности $\\chi(f, r) = (f + r) \\bmod 2$, и его ядро '
    'выделяет цветосохраняющую подгруппу '
    '$V_4 = \\{\\mathrm{id}, \\rho_{180}, \\sigma_{d1}, \\sigma_{d2}\\}$. '
    'Теорема T01 фиксирует два ценза: действие $V_4$ на 64 клетках имеет '
    'ровно 20 орбит (восемь диагональных орбит мощности 2 и двенадцать '
    'орбит мощности 4), а полное действие $D_4$ — ровно 10 орбит по лемме '
    'Бернсайда.'))
RU.append(('p',
    'Эти числа — не курьёз, а рабочий инструмент. Слоны живут на одном '
    'цвете, поэтому их поля наследуют симметрии $V_4$; конь меняет цвет '
    'каждым ходом, и его граф двудолен; ферзь смешивает цвета, и его граф '
    'плотнее. Всякая инвариантная величина модели — энергия, масса поля, '
    'число нарушений эквивариантности — обязана быть постоянной на орбитах, '
    'и протокол C1 проверяет это согласование напрямую: цензы, вычисленные '
    'перечислением, совпадают с цензами, вычисленными леммой Бернсайда. '
    'Группа доски оказывается тем «пространством симметрий», в котором '
    'живут все последующие теоремы.'))
RU.append(('p',
    'С точки зрения физики частиц важна ещё одна роль группы: она задаёт, '
    'какие конфигурации частиц различимы. Позиция, повёрнутая на $180^\\circ$ '
    'с переменой цвета, для большинства инвариантов неотличима от исходной; '
    'позиция, отражённая относительно вертикали, различима, если сторона '
    'на ходу фиксирована. Редукция пространства состояний по симметриям '
    '(глава 12) экономит память эндшпильных баз примерно вчетверо — это '
    'прямое практическое следствие абстрактной теории групп.'))

RU.append(('h1', '3. Кинематика частиц: графы ходов и цензы'))
RU.append(('p',
    'Каждый тип частицы порождает на пустой доске граф ходов: вершины — '
    'клетки, рёбра — разрешённые перемещения. Теорема T02 фиксирует цензы '
    'рёбер: ладья $448$, слон $280$, конь $168$, король $210$, ферзь $728$. '
    'Вывод элементарен и показателен: ладья на каждой клетке имеет '
    '$14$ ходов, кроме случаев на границе, где лучи обрезаются; сумма '
    '$\\sum_{f,r} (7 - f) + (7 - r) + f + r$ по всем клеткам даёт '
    '$16 \\times 28 = 448$; слон ограничен своим цветом, и его '
    '$280 = 2 \\times 140$ рёбер распределяются по диагоналям; ферзь, '
    'как объединение ладьи и слона, даёт $448 + 280 = 728$.'))
RU.append(('p',
    'Цензы рёбер — первый нетривиальный сертификат кинематического слоя: '
    'они проверяются протоколом C2 во всех семи реализациях полиглот-ядра и '
    'мгновенно выявляют любую ошибку в таблицах направлений. Кроме того, '
    'они дают точную нормировку полей угроз: масса поля пустой доски от '
    'одной частицы равна степени её вершины, и энергетические тождества '
    'главы 5 опираются именно на эти числа.'))
RU.append(('p',
    'Граф ходов коня заслуживает отдельного слова: это единственный граф '
    'с ненаправленной геометрией смещений $(\\pm 1, \\pm 2)$, '
    '$(\\pm 2, \\pm 1)$, инвариантной относительно всех восьми элементов '
    '$D_4$. Двудольность по цвету и регулярность на внутреннем субдоске '
    '$6 \\times 6$ делают его идеальным объектом для теории обходов — '
    'тема главы 8 и теоремы T07.'))

RU.append(('h1', '4. Мобильность: кинетические инварианты'))
RU.append(('p',
    'Мобильность частицы на данной клетке — степень её вершины в графе '
    'ходов; мобильность стороны — число её легальных ходов. Теорема T03 '
    'суммирует мобильности по всем 64 клеткам пустой доски: король $420$, '
    'конь $336$, слон $560$, ладья $896$, ферзь $1456$, и фиксирует '
    'максимумы: ферзь $27$ (центр), ладья $14$, слон $13$, конь $8$, '
    'король $8$. Отсюда следует верхняя граница кинетической энергии '
    'стандартного набора: $27 + 2 \\cdot 14 + 2 \\cdot 13 + 2 \\cdot 8 + 8 '
    '= 105$ ходов.'))
RU.append(('p',
    'Начальная позиция даёт первый энергетический сертификат: обе стороны '
    'имеют ровно по $20$ легальных ходов ($16$ пешечных и $4$ коневых), '
    'а после $1.\\mathrm{e4}$ мобильность белых подскакивает до $30$ — '
    'пешка $\\mathrm{e2{-}e4}$ открыла диагональ слона $\\mathrm{f1}$, '
    'диагональ ферзя $\\mathrm{d1}$ и третье поле коня $\\mathrm{g1}$. '
    'Оба значения закреплены проверкой C7 и служат дымовым тестом всей '
    'генерации: любое отклонение в блокировках, рокировке или правах хода '
    'меняет эти числа.'))
RU.append(('fig', 'mobility_census.png',
    'Рис. 1. Суммарная мобильность частиц на пустой доске (теорема T03, проверка C3).', 78))
RU.append(('p',
    'Мобильность входит в модель дважды. Во-первых, как член лагранжиана '
    '(глава 6): кинетический коэффициент $\\mu = 0.1$ отражает шахматную '
    'практику — пространство стоит дорого, но дешевле материала. '
    'Во-вторых, как производящая функция для упорядочивания ходов в '
    'поиске (глава 11): централизация частицы коррелирует с её мобильностью, '
    'и потому кинетический бонус централизации в эвристике MVV-LVA — это '
    'не эмпирика, а прямое следствие устройства графов ходов.'))

RU.append(('h1', '5. Поля угроз: потенциальный слой K3'))
RU.append(('p',
    'Слой K3 — потенциальный слой модели. Каждая частица испускает поле '
    'угроз $\\Theta(c)$: для клетки $c$ поле равно числу частиц стороны $s$, '
    'атакующих $c$. Суммарная масса поля связана с мобильностями тождеством '
    'атаки: $\\sum_c \\Theta_s(c) = \\sum_\\pi a(\\pi)$ — дискретная теорема '
    'Фубини, меняющая порядок суммирования. В начальной позиции каждая '
    'сторона несёт поле массы $38$.'))
RU.append(('p',
    'Теорема T04 доказывает два структурных свойства поля. Аддитивность — '
    'поле системы частиц есть сумма полей отдельных частиц; это делает '
    'корректной саму картину «источников и потенциала». Эквивариантность — '
    'для позиций без пешек поле коммутирует с группой доски: '
    '$\\Theta_{g \\cdot p}(g \\cdot c) = \\Theta_p(c)$ для всех '
    '$g \\in D_4$; атака определяется относительной геометрией клеток, '
    'инвариантной относительно изометрий. Пешка — «ориентированная '
    'частица»: она атакует строго вперёд, и ни один неединичный элемент '
    '$D_4$ не сохраняет это направление. Точный дефект эквивариантности — '
    'пешечная аномалия $176 = 88 + 88$ нарушений в начальной позиции — '
    'фиксируется теоремой и проверкой C6 во всех семи языках.'))
RU.append(('fig', 'threat_heatmap.png',
    'Рис. 2. Поле угроз белых в начальной позиции (слой K3, проверка C6).', 66))
RU.append(('p',
    'Поле угроз — та величина, которая видна в веб-лаборатории как '
    'тепловая карта; здесь оно получает строгий статус дискретного '
    'потенциала с известной группой симметрий и известным дефектом. '
    'Именно поле, а не «интуиция», определяет защитные связи: клетка под '
    'одинарной атакой и без защиты — источник тактики, и все такие '
    'конструкции в поиске (глава 11) проявляются через квиесценцию, '
    'перебирающую взятия до успокоения поля.'))

RU.append(('h1', '6. Лагранжиан: энергия позиции'))
RU.append(('p',
    'Слой TORUS приписывает позиции энергию. Лагранжиан T05: '
    '$E = [M(\\circ) - M(\\bullet)] + \\mu [m(\\circ) - m(\\bullet)]$ при '
    '$\\mu = 0.1$, где $M$ — материал в пешечных единицах, $m$ — '
    'мобильность. Энергия целочисленна в сотых долях, детерминирована и '
    'обращается в ноль на симметричных позициях. Начальная позиция '
    'сбалансирована; после $1.\\mathrm{e4}$ белые получают '
    '$\\mu \\times 10 = +1.0$ кинетической энергии — первая «реальная» '
    'динамическая величина партии.'))
RU.append(('p',
    'Теорема T05 доказывает вычислимость (конечные суммы по клеткам и '
    'легальным ходам), детерминизм (независимость от порядка обхода) и '
    'границу кинетического члена: мобильность стандартного набора не '
    'превосходит $105$ по T03. Знак энергии выбран «от стороны на ходу» — '
    'это требование негамакс-поиска главы 11: родитель максимизирует '
    'минус ребёнка, и вся оценка автоматически согласована с '
    'чередованием сторон.'))
RU.append(('p',
    'Энергия — мост между физической метафорой и вычислением: поиск '
    'минимизирует её, веб-лаборатория отображает энергетическую панель, '
    'а протокол C7 фиксирует её сертификатные значения. Выбор весов '
    '$(100, \\mu = 0.1)$ — конвенция, положенная в определение и '
    'зафиксированная протоколом: теорема не утверждает, что эти веса '
    '«оптимальны», она утверждает, что при этих весах все свойства '
    'доказаны и все числа воспроизводимы.'))

RU.append(('h1', '7. Поток ходов: завершения и бильярд'))
RU.append(('p',
    'Слой KLEIN рассматривает партию как дискретный поток на торе доски. '
    'Первая теорема слоя T06 даёт точное время завершения: частица, '
    'стартующая из угла с вектором $(a, b)$ и отражающаяся от бортов, '
    'возвращается в угол за $t^* = \\mathrm{lcm}(W / \\gcd(a, W),\\, '
    'H / \\gcd(b, H))$ шагов. Это стандартный расчёт бильярда на торе, '
    'перенесённый на решётку: отражение эквивалентно разворачиванию доски, '
    'и траектория замыкается тогда, когда оба периода совместятся.'))
RU.append(('p',
    'Вторая часть теоремы — демпфированный бильярд: каждая отражённая '
    'скорость умножается на коэффициент $\\gamma = \\pi^4 / 256 \\approx '
    '0.38$, и суммарный путь до остановки равен $|v_0| / (1 - \\gamma)$ — '
    'геометрическая прогрессия, сходящаяся к точному пределу. Протокол C4 '
    'проверяет отношение «путь/предел» с точностью $10^{-9}$ — случай, '
    'когда непрерывная формула и дискретная симуляция сходятся бит в бит.'))
RU.append(('fig', 'billiard_flow.png',
    'Рис. 3. Демпфированная траектория частицы на доске ($\\gamma = \\pi^4/256$, проверка C4).', 62))
RU.append(('p',
    'Смысл слоя — каркас для «траекторий»: поток ходов получает геометрию '
    '(замыкания на торе), термодинамику (демпфирование) и память (глава 10). '
    'В веб-лаборатории этот слой виден как анимация частиц, повторяющих '
    'легальные ходы и гаснущих по закону $\\gamma$; здесь он — теорема '
    'с точными временами завершения и пределами пути.'))

RU.append(('h1', '8. Обход коня: открытие и сертификат Варнсдорфа'))
RU.append(('p',
    'Замкнутый обход коня — маршрут из 64 ходов, посещающий каждую клетку '
    'ровно один раз и возвращающийся в старт. Теорема T07 фиксирует '
    'результат лаборатории: эвристика Варнсдорфа («иди на клетку с '
    'минимальной степенью продолжения») строит замкнутый обход, стартуя с '
    '$\\mathrm{f5}$, с замыканием $\\mathrm{d6} \\to \\mathrm{f5}$, без '
    'возвратов — жадный локальный выбор ведёт к глобально совершенному '
    'маршруту.'))
RU.append(('p',
    'Тонкость, которую фиксирует теорема: эвристика Варнсдорфа не является '
    'теоремой о всегда-успехе — известны старты, с которых наивное '
    'применение срывается; классическая теорема Швенка описывает, какие '
    'доски вообще не имеют замкнутых обходов. Поэтому лаборатория '
    'сертифицирует конкретный результат: найденный тур сохраняется в '
    'results/knight_tour.json с полной проверкой свойств (64 различных '
    'клетки, все шаги конем, замыкание) — и проверка C10 полиглот-ядра '
    'воспроизводит его во всех семи языках.'))
RU.append(('p',
    'Для модели частиц обход коня — контрольный эксперимент слоя потока: '
    'он показывает, что жадная кинематика («минимальная следующая степень») '
    'может решать глобальные задачи перечисления без возвратов. Тот же '
    'принцип — локальный порядок вместо глобального перебора — работает в '
    'упорядочивании ходов поиска (глава 11) и в ретроградной индукции '
    '(глава 12).'))

RU.append(('h1', '9. Сертификация генерации: перфт-тождества'))
RU.append(('p',
    'Перфт — число листьев дерева легальных продолжений глубины $d$. '
    'Теорема T08 фиксирует мировые эталоны для начальной позиции: '
    'perft(1..5) $= 20, 400, 8902, 197281, 4865609$ — и полную таблицу '
    'divide(3) по всем двадцати начальным ходам (от $380$ у фланговых '
    'пешек до $600$ после $1.\\mathrm{e4}$). Совпадение с эталоном '
    'эквивалентно совпадению множеств легальных ходов на всём дереве '
    'глубины $d$: это исчерпывающий тест генерации, локализующий ошибку '
    'до конкретного начального хода.'))
RU.append(('fig', 'perft_growth.png',
    'Рис. 4. Рост дерева перфта: 20 → 400 → 8902 → 197281 → 4865609 (проверка C5).', 74))
RU.append(('p',
    'История разработки подтверждает диагностическую силу метода: ошибки '
    'индексации взятия на проходе и проверки ранга пешечного взятия '
    'обнаружились именно как расхождения отдельных ветвей divide(3), '
    'после чего значения сошлись и были заморожены в baseline. Весь '
    'последующий каркас — поиск главы 11, базы главы 12, полиглот-ядро — '
    'стоит на этом фундаменте: любой из семи языков обязан воспроизвести '
    'перфт-цепочку прежде, чем его результаты будут приняты.'))

RU.append(('h1', '10. Память потока: хеширование Цобриста'))
RU.append(('p',
    'Поток состояний нуждается в различении состояний. Теорема T09 строит '
    'память на хешах Цобриста: таблица из $1562$ ключей ($12 \\times 128$ '
    'фигурных, $1$ сторонний, $16$ рокировочных, $9$ проходных) порождается '
    'генератором splitmix64 из зерна $\\text{0x1234567890ABCDEF}$. '
    'Биективность генератора доказана с явной обратной функцией: нечётные '
    'множители обратимы по модулю $2^{64}$, а каскады сдвиг-ксор '
    'разворачиваются рядом с удвоением. Первые значения — '
    '$\\sigma(1) = \\text{0x910A2DEC89025CC1}$, $\\sigma(2) = '
    '\\text{0x975835DE1C9756CE}$ — фиксируют кросс-языковой эталон.'))
RU.append(('p',
    'Инкрементальное тождество $h(\\mathrm{make}(P, m)) = h(P) \\oplus '
    '\\Delta(m)$ доказано индукцией по ходам с явной дельтой — включая '
    'рокировки, взятия на проходе и превращения. Проверка C9 исполняет '
    '40 партий до 60 полуходов, сравнивая инкрементальный хеш с полным '
    'пересчётом на каждом шаге, и проверяет unmake-восстановление. '
    'Граница коллизий $n(n-1)/2^{65}$ даёт $0.027$ при миллиарде позиций — '
    'память потока надёжна во всех практических режимах лаборатории.'))

RU.append(('h1', '11. Поиск: альфа-бета и детерминизм'))
RU.append(('p',
    'Контур полной игры минимизирует лагранжиан T05 по дереву ходов. '
    'Теорема T10 доказывает корректность негамакса с окном '
    '$(\\alpha, \\beta)$ — классический аргумент Кнута–Мура в '
    'негамакс-форме, дополненный квиесценцией (перебор взятий до '
    'успокоения поля угроз) и кодированием мата $-\\mathrm{MATE} + ply$, '
    'предпочитающим кратчайшее форсирование. Границы: худший порядок даёт '
    '$b^d$ листьев, лучший — $b^{\\lceil d/2 \\rceil} + b^{\\lfloor d/2 '
    '\\rfloor} - 1$.'))
RU.append(('p',
    'Упорядочивание ходов — «кинематика поиска»: эвристика MVV-LVA с '
    'кинетическим бонусом централизации. Измеренные числа зафиксированы '
    'протоколом: на начальной позиции поиск посещает $79$ узлов на глубине '
    '2 против $421$ полного дерева, $731$ против $9323$ на глубине 3, '
    '$3345$ против $206604$ на глубине 4 и $19753$ против $5072213$ на '
    'глубине 5 — выигрыш растёт до $\\times 256.8$, приближаясь к '
    'квадратному корню из экспоненты. Тотальный порядок ходов (стабильная '
    'сортировка по тотальному ключу) делает поиск детерминированным: ход, '
    'оценка и число узлов воспроизводимы бит в бит на любой машине — '
    'условие сравнимости всех сертификатов программы.'))

RU.append(('h1', '12. Мат-сертификаты и сводный протокол'))
RU.append(('p',
    'Мат в N проверяется двумя независимыми инструментами. Прямой поиск — '
    'итеративное углубление с восстановлением полной главной вариации; '
    'обратный — ретроградный анализ, строящий расстояние до мата (DTM) для '
    'всего пространства трёхфигурных эндшпилей. Теорема T11 фиксирует '
    'статистику баз: KRK — $399112$ состояний, $4447032$ ребра, максимум '
    'DTM $32$ полухода ($16$ ходов); KQK — $368452$ состояния, $4869496$ '
    'рёбер, максимум $20$ полуходов ($10$ ходов). Оба максимума совпадают '
    'с классическими табличными значениями — внешняя сверка, недоступная '
    'самопроверке.'))
RU.append(('p',
    'Замыкает базу машина Беллмана: уравнение оптимальности проверено по '
    'всем состояниям обеих баз — ноль нарушений. Прямой поиск согласован с '
    'базами точечными проверками и тактическим эталоном: морфийский мат '
    '$\\mathrm{a1a6}$ (3 полухода, 46 узлов), двухладейная лестница '
    '$\\mathrm{b1b7}$ (3, 49), мат конём и ладьёй $\\mathrm{g1g8}$ (1, 1).'))
RU.append(('fig', 'dtm_histogram.png',
    'Рис. 5. Распределение DTM по состояниям эндшпильных баз (теорема T11, проверка C8).', 76))
RU.append(('p',
    'Теорема T12 сводит всё в протокол: девять проверок C1–C9 закрывают '
    'теоремы T01–T11 (C1 — алгебра, C2 — графы, C3 — мобильность, C4 — '
    'поток, C5 — перфт, C6 — поля, C7 — энергия, C8 — базы и тактика, '
    'C9 — память), отказ любого чека изолирован и не блокирует остальные, '
    'а вердикт ALL CHECKS PASSED воспроизводим одной командой. '
    'Полиглот-батарея C1–C10 выдаёт побитно совпадающий вердикт 10/10 на '
    'семи языках: Python, C и JavaScript верифицированы локально, Rust, '
    'Go, Julia и Java — в GitHub Actions при каждом пуше. Программа '
    'замкнута: каждая теорема имеет исполняемую форму.'))

RU.append(('h1', 'Приложение A. Сводная таблица констант'))
RU.append(('table', 'Протокольные константы программы chess-dynamics-lab',
 ['Константа', 'Значение', 'Теорема', 'Проверка'],
 [['орбиты $V_4$ / $D_4$', '20 / 10', 'T01', 'C1'],
  ['рёбра графов R/B/N/K/Q', '448/280/168/210/728', 'T02', 'C2'],
  ['суммы мобильности K/N/B/R/Q', '420/336/560/896/1456', 'T03', 'C3'],
  ['максимум мобильности ферзя', '27', 'T03', 'C3'],
  ['поле начальной позиции (сторона)', '38', 'T04', 'C6'],
  ['пешечная аномалия', '176 = 88 + 88', 'T04', 'C6'],
  ['энергия после 1.e4 (кинетический член)', '+1.0', 'T05', 'C7'],
  ['$t^*$, бильярд из угла (3, 2)', 'lcm(8/1, 8/2) = 8', 'T06', 'C4'],
  ['демпфирование', '$\\gamma = \\pi^4/256$, путь $|v_0|/(1-\\gamma)$', 'T06', 'C4'],
  ['замкнутый обход коня', '64 хода от f5, замыкание d6→f5', 'T07', 'C10'],
  ['perft(1..5)', '20/400/8902/197281/4865609', 'T08', 'C5'],
  ['таблица ключей Цобриста', '1562 слов, зерно 0x1234567890ABCDEF', 'T09', 'C9'],
  ['splitmix64(1)', '0x910A2DEC89025CC1', 'T09', 'C9'],
  ['граница коллизий при $n = 10^9$', '0.0271', 'T09', 'C9'],
  ['узлы альфа-бета, глубина 2–5', '79/731/3345/19753', 'T10', 'baseline'],
  ['KRK: состояния / рёбра / max DTM', '399112 / 4447032 / 32 полухода', 'T11', 'C8'],
  ['KQK: состояния / рёбра / max DTM', '368452 / 4869496 / 20 полуходов', 'T11', 'C8'],
  ['нарушения Беллмана', '0', 'T11', 'C8'],
  ['морфийский мат', 'a1a6, 3 полухода, 46 узлов', 'T11', 'C8']]))

RU.append(('h1', 'Приложение B. Руководство по воспроизведению'))
RU.append(('p',
    'Лаборатория разворачивается из репозитория без внешних зависимостей: '
    'ядро dynamics.py — один самодостаточный файл на стандартной библиотеке '
    'Python (matplotlib опционален, только для графиков). Полный протокол: '
    'python3 dynamics.py --report — печатает девять строк [PASS]/[FAIL] и '
    'вердикт; отдельные проверки — python3 dynamics.py --run C5 (для '
    'глубокого режима — флаг --deep, добавляющий perft(5) и полную таблицу '
    'divide). Анализ позиции: --analyze FEN --depth 4; форсированный мат: '
    '--mate FEN; самопартия: engine/game_player.py --selfplay --depth 4; '
    'графики: --plots reports/plots.'))
RU.append(('p',
    'Полиглот-ядро: bash polyglot/run_all.sh исполняет батарею C1–C10 во '
    'всех доступных языках и печатает сводную таблицу; в чистом окружении '
    'достаточно python3 polyglot/python/chess_core.py. Тесты: python3 -m '
    'pytest tests/ -q (36 тестов). Базы DTM поставляются сжатыми в '
    'results/ и проверяются машиной Беллмана при запуске C8.'))
RU.append(('p',
    'Android (Termux): pkg install python git; git clone репозитория; '
    'python3 dynamics.py --report. Полный --report на смартфоне занимает '
    'десятки секунд (доминирует C5), отдельные чеки — секунды. Для '
    'публикации форка см. INSTRUCTION.md: скрипт scripts/termux_push.sh '
    'создаёт ветку, коммитит и отправляет репозиторий в аккаунт GitHub '
    'одной командой. CI при каждом пуше запускает протокол и полиглот-'
    'батарею на матрице языков, поэтому вердикт репозитория всегда '
    'актуален.'))

RU.append(('h1', 'Библиография'))
RU.append(('bib', [
    'Shannon C. E. Programming a Computer for Playing Chess // Philosophical '
    'Magazine. 1950. Vol. 41, No. 314. P. 256–275.',
    'Zobrist A. L. A New Hashing Method with Application for Game Playing / '
    'Tech. Rep. 88. University of Wisconsin, 1970; переиздано: ICCA Journal. '
    '1990. Vol. 13, No. 2. P. 69–73.',
    'Knuth D. E., Moore R. W. An Analysis of Alpha-Beta Pruning // Artificial '
    'Intelligence. 1975. Vol. 6, No. 4. P. 293–326.',
    'Thompson K. Retrograde Analysis of Certain Endgames // ICCA Journal. '
    '1986. Vol. 9, No. 3. P. 131–139.',
    'Schwenk A. J. Which Rectangular Chessboards Have a Knight’s Tour? // '
    'Mathematics Magazine. 1991. Vol. 64, No. 5. P. 325–332.',
    'Tromp J. The Number of Legal Go Positions // ICGA Journal. 2016. '
    'Vol. 39, No. 1. P. 3–13; а также материалы J. Tromp по perft и '
    'подсчёту шахматных позиций (johntromp.github.io).',
    'Исаев И. Х. Динамический принцип: монады, слои и протоколы проверяемой '
    'математики. Программа hodge-laboratory, 2025. GitHub: '
    'wild8highlander/hodge-laboratory.',
    'Исаев И. Х. Динамика шахматных частиц: монографии T01–T12, протокол '
    'C1–C9 и полиглот-ядро. Программа chess-dynamics-lab, 2026. GitHub: '
    'wild8highlander/chess-dynamics-lab.',
]))

MAIN_RU = RU

EN = []

EN.append(('h1', '1. Introduction: from positions to particles'))
EN.append(('abs',
    'This monograph completes the chess-dynamics-lab program: it brings '
    'together the twelve theorems T01–T12, the nine protocol checks C1–C9 '
    'and the seven-language polyglot core into a single corpus in which a '
    'chess game is described as the dynamics of a system of particles. '
    'Every numerical claim is certificate-reproducible by one command on '
    'any machine — from a server to a Termux phone.'))
EN.append(('p',
    'The idea of viewing the chessboard as a physical system is as old as '
    'chess thought itself: pieces "press", "hang", are "pinned", squares '
    'are "weak" and "strong", an attack "flows" along the fronts. Usually '
    'these words remain metaphors. The chess-dynamics-lab program, grown '
    'from the methodology of the parent hodge-laboratory program, does the '
    'opposite: every metaphor receives an exact definition, every '
    'definition a theorem, and every theorem an executable check that is '
    'part of the protocol. A piece becomes a particle with its own '
    'kinematic invariants, a position a configuration of the particle '
    'system, and a move an elementary event of the flow.'))
EN.append(('p',
    'The model has three layers. Layer K3 is the potential layer: every '
    'particle emits a threat field on the board, and the total field '
    'defines the structure of pressure and defense. Layer TORUS is the '
    'energy layer: a position carries a Lagrangian energy made of a '
    'material and a mobility term, and the full-game search minimizes '
    'exactly it. Layer KLEIN is the flow layer: the sequence of moves is a '
    'discrete flow of states with memory (Zobrist hashes), terminations '
    '(distance to mate) and geometry (closed trajectories on the torus of '
    'the board). The layer names are inherited from hodge-laboratory: K3, '
    'the torus and the Klein bottle are topological images denoting not '
    'the geometry of the board but the structure of the computation.'))
EN.append(('p',
    'The distinguishing feature of the approach is certifiability. The '
    'statement "our move generation is correct" is not a declaration here '
    'but the perft theorem T08 with the reference values 20, 400, 8902, '
    '197281, 4865609; the statement "the threat fields agree with the '
    'symmetries" is theorem T04 on equivariance with the exact pawn '
    'anomaly 176; the statement "the endgame bases are correct" is the '
    'Bellman machine with zero violations over all 767564 states of the '
    'KRK and KQK bases. The full list of checks closes with the verdict '
    'ALL CHECKS PASSED, and the same list, bit-identical, is reproduced in '
    'the seven languages of the polyglot core.'))
EN.append(('p',
    'The monograph is organized as follows. Chapters 2–4 build the '
    'geometry and kinematics: the board group, the graph censuses and the '
    'mobility of particles. Chapters 5–7 introduce the physics proper: '
    'threat fields, the Lagrangian and the flow. Chapter 8 is devoted to '
    'the closed knight tour, a pearl of discrete geometry. Chapters 9–11 '
    'describe the computational frame: the certification of generation, '
    'the memory and the search. Chapter 12 assembles the mate certificates '
    'and the consolidated protocol. Appendix A contains the full table of '
    'constants, Appendix B the reproduction guide, including Termux.'))

EN.append(('h1', '2. The algebra of the board: the symmetry group'))
EN.append(('p',
    'The $8 \\times 8$ board is the set of squares '
    '$S = \\{0, \\ldots, 7\\}^2$ on which the square symmetry group $D_4$ '
    'of eight elements acts: four rotations and four reflections. The '
    'coloring of the squares defines the parity homomorphism '
    '$\\chi(f, r) = (f + r) \\bmod 2$, and its kernel selects the '
    'color-preserving subgroup '
    '$V_4 = \\{\\mathrm{id}, \\rho_{180}, \\sigma_{d1}, \\sigma_{d2}\\}$. '
    'Theorem T01 fixes two censuses: the action of $V_4$ on the 64 squares '
    'has exactly 20 orbits (eight diagonal orbits of size 2 and twelve '
    'orbits of size 4), while the full $D_4$ action has exactly 10 orbits '
    'by the Burnside lemma.'))
EN.append(('p',
    'These numbers are not a curiosity but a working tool. Bishops live on '
    'one color, so their fields inherit the $V_4$ symmetries; the knight '
    'changes color with every move and its graph is bipartite; the queen '
    'mixes the colors and her graph is denser. Every invariant quantity of '
    'the model — the energy, the field mass, the number of equivariance '
    'violations — must be constant on the orbits, and protocol C1 verifies '
    'this agreement directly: the censuses computed by enumeration coincide '
    'with the censuses computed by the Burnside lemma. The board group '
    'turns out to be the "space of symmetries" in which all subsequent '
    'theorems live.'))
EN.append(('p',
    'From the particle-physics viewpoint the group plays one more role: it '
    'specifies which particle configurations are distinguishable. A '
    'position rotated by $180^\\circ$ with a color swap is indistinguishable '
    'from the original for most invariants; a position reflected about the '
    'vertical is distinguishable when the side to move is fixed. The '
    'reduction of the state space by symmetries (chapter 12) saves roughly '
    'a quarter of the endgame base memory — a direct practical consequence '
    'of abstract group theory.'))

EN.append(('h1', '3. Particle kinematics: move graphs and censuses'))
EN.append(('p',
    'Each particle type generates a move graph on the empty board: the '
    'vertices are squares, the edges are permitted displacements. Theorem '
    'T02 fixes the edge censuses: rook 448, bishop 280, knight 168, king '
    '210, queen 728. The derivation is elementary and instructive: a rook '
    'has 14 moves on every square except on the border, where the rays are '
    'cut; the sum $\\sum_{f,r} (7 - f) + (7 - r) + f + r$ over all squares '
    'gives $16 \\times 28 = 448$; the bishop is confined to its color, and '
    'its $280 = 2 \\times 140$ edges are distributed along the diagonals; '
    'the queen, being the union of rook and bishop, yields $448 + 280 = '
    '728$.'))
EN.append(('p',
    'The edge censuses are the first nontrivial certificate of the '
    'kinematic layer: they are verified by protocol C2 in all seven '
    'implementations of the polyglot core and instantly expose any error '
    'in the direction tables. Moreover, they provide the exact '
    'normalization of the threat fields: the field mass of the empty board '
    'from a single particle equals the degree of its vertex, and the '
    'energy identities of chapter 5 rest precisely on these numbers.'))
EN.append(('p',
    'The knight move graph deserves a separate word: it is the only graph '
    'with a direction-free geometry of offsets $(\\pm 1, \\pm 2)$, '
    '$(\\pm 2, \\pm 1)$ invariant under all eight elements of $D_4$. '
    'Color bipartiteness and regularity on the inner $6 \\times 6$ subboard '
    'make it an ideal object for tour theory — the subject of chapter 8 '
    'and theorem T07.'))

EN.append(('h1', '4. Mobility: the kinetic invariants'))
EN.append(('p',
    'The mobility of a particle on a square is the degree of its vertex in '
    'the move graph; the mobility of a side is the number of its legal '
    'moves. Theorem T03 sums the mobilities over all 64 squares of the '
    'empty board: king 420, knight 336, bishop 560, rook 896, queen 1456, '
    'and fixes the maxima: queen 27 (center), rook 14, bishop 13, knight '
    '8, king 8. Hence the upper bound of the kinetic energy of the '
    'standard set: $27 + 2 \\cdot 14 + 2 \\cdot 13 + 2 \\cdot 8 + 8 = 105$ '
    'moves.'))
EN.append(('p',
    'The start position yields the first energy certificate: both sides '
    'have exactly 20 legal moves each (16 pawn moves and 4 knight moves), '
    'and after $1.\\mathrm{e4}$ the White mobility jumps to 30 — the pawn '
    '$\\mathrm{e2{-}e4}$ opened the bishop diagonal $\\mathrm{f1}$, the '
    'queen diagonal $\\mathrm{d1}$ and the third square of the knight '
    '$\\mathrm{g1}$. Both values are pinned by check C7 and serve as the '
    'smoke test of the whole generation: any deviation in blockings, '
    'castling or move rights changes these numbers.'))
EN.append(('fig', 'mobility_census.png',
    'Fig. 1. Total mobility of the particles on the empty board (theorem T03, check C3).', 78))
EN.append(('p',
    'Mobility enters the model twice. First, as a term of the Lagrangian '
    '(chapter 6): the kinetic coefficient $\\mu = 0.1$ reflects chess '
    'practice — space is expensive but cheaper than material. Second, as '
    'the generating function for move ordering in the search (chapter 11): '
    'the centralization of a particle correlates with its mobility, so the '
    'kinetic centralization bonus of the MVV-LVA heuristic is not '
    'empirics but a direct consequence of the structure of the move '
    'graphs.'))

EN.append(('h1', '5. Threat fields: the potential layer K3'))
EN.append(('p',
    'Layer K3 is the potential layer of the model. Each particle emits a '
    'threat field $\\Theta(c)$: for a square $c$ the field equals the '
    'number of particles of side $s$ attacking $c$. The total field mass '
    'is tied to the mobilities by the attack identity: '
    '$\\sum_c \\Theta_s(c) = \\sum_\\pi a(\\pi)$ — a discrete Fubini '
    'theorem interchanging the order of summation. In the start position '
    'each side carries a field of mass 38.'))
EN.append(('p',
    'Theorem T04 proves two structural properties of the field. '
    'Additivity — the field of a particle system is the sum of the fields '
    'of the individual particles; this is what makes the very picture of '
    '"sources and potential" correct. Equivariance — for positions without '
    'pawns the field commutes with the board group: '
    '$\\Theta_{g \\cdot p}(g \\cdot c) = \\Theta_p(c)$ for all '
    '$g \\in D_4$; the attack is defined by the relative geometry of '
    'squares, invariant under the isometries. The pawn is an "oriented '
    'particle": it attacks strictly forward, and no non-identity element '
    'of $D_4$ preserves this direction. The exact equivariance defect — '
    'the pawn anomaly $176 = 88 + 88$ violations in the start position — '
    'is fixed by the theorem and by check C6 in all seven languages.'))
EN.append(('fig', 'threat_heatmap.png',
    'Fig. 2. The White threat field in the start position (layer K3, check C6).', 66))
EN.append(('p',
    'The threat field is the quantity displayed as a heat map in the web '
    'laboratory; here it receives the strict status of a discrete '
    'potential with a known symmetry group and a known defect. It is the '
    'field, not "intuition", that defines the defensive links: a singly '
    'attacked undefended square is a source of tactics, and all such '
    'constructions appear in the search (chapter 11) through quiescence, '
    'which enumerates captures until the field calms down.'))

EN.append(('h1', '6. The Lagrangian: the energy of a position'))
EN.append(('p',
    'Layer TORUS assigns energy to a position. The Lagrangian of T05: '
    '$E = [M(\\circ) - M(\\bullet)] + \\mu [m(\\circ) - m(\\bullet)]$ with '
    '$\\mu = 0.1$, where $M$ is the material in pawn units and $m$ the '
    'mobility. The energy is integral in hundredths, deterministic and '
    'vanishes on symmetric positions. The start position is balanced; '
    'after $1.\\mathrm{e4}$ White gains $\\mu \\times 10 = +1.0$ of kinetic '
    'energy — the first "real" dynamic quantity of the game.'))
EN.append(('p',
    'Theorem T05 proves computability (finite sums over squares and legal '
    'moves), determinism (independence of the traversal order) and the '
    'bound of the kinetic term: the mobility of the standard set does not '
    'exceed 105 by T03. The sign of the energy is chosen "from the side to '
    'move" — the requirement of the negamax search of chapter 11: the '
    'parent maximizes the negated child, and the whole evaluation is '
    'automatically consistent with the alternation of sides.'))
EN.append(('p',
    'The energy is the bridge between the physical metaphor and the '
    'computation: the search minimizes it, the web laboratory displays the '
    'energy panel, and protocol C7 pins its certificate values. The choice '
    'of the weights $(100, \\mu = 0.1)$ is a convention laid into the '
    'definition and pinned by the protocol: the theorem does not claim '
    'that these weights are "optimal", it claims that under these weights '
    'all the properties are proved and all the numbers reproducible.'))

EN.append(('h1', '7. The flow of moves: terminations and billiards'))
EN.append(('p',
    'Layer KLEIN regards the game as a discrete flow on the torus of the '
    'board. The first theorem of the layer, T06, gives the exact '
    'termination time: a particle starting from a corner with the vector '
    '$(a, b)$ and reflecting off the rails returns to a corner after '
    '$t^* = \\mathrm{lcm}(W / \\gcd(a, W),\\, H / \\gcd(b, H))$ steps. This '
    'is the standard billiard computation on the torus transferred to the '
    'lattice: reflection is equivalent to unfolding the board, and the '
    'trajectory closes exactly when both periods meet.'))
EN.append(('p',
    'The second part of the theorem is the damped billiard: every '
    'reflected velocity is multiplied by the coefficient '
    '$\\gamma = \\pi^4 / 256 \\approx 0.38$, and the total path until rest '
    'equals $|v_0| / (1 - \\gamma)$ — a geometric progression converging to '
    'an exact limit. Protocol C4 verifies the "path/limit" ratio to '
    '$10^{-9}$ — a case where a continuous formula and a discrete '
    'simulation agree bit for bit.'))
EN.append(('fig', 'billiard_flow.png',
    'Fig. 3. The damped trajectory of a particle on the board ($\\gamma = \\pi^4/256$, check C4).', 62))
EN.append(('p',
    'The meaning of the layer is a frame for "trajectories": the flow of '
    'moves receives geometry (closures on the torus), thermodynamics '
    '(damping) and memory (chapter 10). In the web laboratory this layer '
    'is visible as the animation of particles repeating legal moves and '
    'fading according to the law $\\gamma$; here it is a theorem with '
    'exact termination times and path limits.'))

EN.append(('h1', '8. The knight tour: discovery and the Warnsdorff certificate'))
EN.append(('p',
    'A closed knight tour is a route of 64 moves visiting every square '
    'exactly once and returning to the start. Theorem T07 pins the '
    'laboratory result: the Warnsdorff heuristic ("move to the square with '
    'the minimal degree of continuation") builds a closed tour starting at '
    '$\\mathrm{f5}$, with the closure $\\mathrm{d6} \\to \\mathrm{f5}$, '
    'without backtracking — a greedy local choice leads to a globally '
    'perfect route.'))
EN.append(('p',
    'A subtlety fixed by the theorem: the Warnsdorff heuristic is not an '
    'always-succeeds theorem — there are known starts from which naive '
    'application derails; the classical Schwenk theorem describes which '
    'boards have no closed tours at all. The laboratory therefore '
    'certifies a concrete result: the found tour is stored in '
    'results/knight_tour.json with a full verification of the properties '
    '(64 distinct squares, all knight steps, the closure) — and check C10 '
    'of the polyglot core reproduces it in all seven languages.'))
EN.append(('p',
    'For the particle model the knight tour is the control experiment of '
    'the flow layer: it shows that greedy kinematics ("minimal next '
    'degree") can solve global enumeration problems without '
    'backtracking. The same principle — a local order instead of a global '
    'search — operates in the move ordering of the search (chapter 11) and '
    'in the retrograde induction (chapter 12).'))

EN.append(('h1', '9. Certifying the generation: perft identities'))
EN.append(('p',
    'Perft is the number of leaves of the tree of legal continuations of '
    'depth $d$. Theorem T08 pins the world references for the start '
    'position: perft(1..5) $= 20, 400, 8902, 197281, 4865609$ — and the '
    'complete divide(3) table over all twenty initial moves (from 380 for '
    'the flank pawns to 600 after $1.\\mathrm{e4}$). Agreement with the '
    'reference is equivalent to agreement of the sets of legal moves on '
    'the whole tree of depth $d$: it is an exhaustive test of the '
    'generation, localizing an error to a concrete initial move.'))
EN.append(('fig', 'perft_growth.png',
    'Fig. 4. Growth of the perft tree: 20 → 400 → 8902 → 197281 → 4865609 (check C5).', 74))
EN.append(('p',
    'The development history confirms the diagnostic power of the method: '
    'the errors of en-passant indexing and of the pawn-capture rank check '
    'were exposed exactly as mismatches of individual divide(3) branches, '
    'after which the values converged and were frozen in the baseline. The '
    'entire subsequent frame — the search of chapter 11, the bases of '
    'chapter 12, the polyglot core — stands on this foundation: each of '
    'the seven languages must reproduce the perft chain before its results '
    'are accepted.'))

EN.append(('h1', '10. The memory of the flow: Zobrist hashing'))
EN.append(('p',
    'A flow of states needs to distinguish states. Theorem T09 builds the '
    'memory on Zobrist hashes: the table of 1562 keys ($12 \\times 128$ '
    'piece keys, 1 side key, 16 castling keys, 9 en-passant keys) is '
    'generated by splitmix64 from the seed '
    '$\\text{0x1234567890ABCDEF}$. The bijectivity of the generator is '
    'proved with an explicit inverse: the odd multipliers are invertible '
    'modulo $2^{64}$, and the xorshift cascades are unwound by the '
    'doubling series. The first values — $\\sigma(1) = '
    '\\text{0x910A2DEC89025CC1}$, $\\sigma(2) = '
    '\\text{0x975835DE1C9756CE}$ — fix the cross-language reference.'))
EN.append(('p',
    'The incremental identity $h(\\mathrm{make}(P, m)) = h(P) \\oplus '
    '\\Delta(m)$ is proved by induction over moves with an explicit delta — '
    'including castling, en passant and promotions. Check C9 executes 40 '
    'games of up to 60 plies, comparing the incremental hash with the full '
    'recomputation at every step, and verifies the unmake restoration. The '
    'collision bound $n(n-1)/2^{65}$ gives 0.027 for a billion positions — '
    'the memory of the flow is reliable in all practical regimes of the '
    'laboratory.'))

EN.append(('h1', '11. The search: alpha-beta and determinism'))
EN.append(('p',
    'The full-game loop minimizes the Lagrangian of T05 over the move '
    'tree. Theorem T10 proves the correctness of the windowed negamax — '
    'the classical Knuth–Moore argument in negamax form, complemented by '
    'quiescence (an enumeration of captures until the threat field calms '
    'down) and the mate encoding $-\\mathrm{MATE} + ply$, which prefers '
    'the shortest forcing. The bounds: the worst order gives $b^d$ '
    'leaves, the best — $b^{\\lceil d/2 \\rceil} + b^{\\lfloor d/2 '
    '\\rfloor} - 1$.'))
EN.append(('p',
    'Move ordering is the "kinematics of the search": the MVV-LVA '
    'heuristic with a kinetic centralization bonus. The measured numbers '
    'are pinned by the protocol: on the start position the search visits '
    '79 nodes at depth 2 against 421 of the full tree, 731 against 9323 '
    'at depth 3, 3345 against 206604 at depth 4 and 19753 against 5072213 '
    'at depth 5 — the gain grows up to $\\times 256.8$, approaching the '
    'square root of the exponent. A total order on the moves (a stable '
    'sort over a total key) makes the search deterministic: the move, the '
    'score and the node count are bit-reproducible on any machine — the '
    'condition under which all the certificates of the program are '
    'comparable.'))

EN.append(('h1', '12. Mate certificates and the consolidated protocol'))
EN.append(('p',
    'Mate in N is verified by two independent instruments. The forward '
    'search — iterative deepening with the reconstruction of the full '
    'principal variation; the backward one — retrograde analysis, which '
    'builds the distance to mate (DTM) for the whole space of three-piece '
    'endgames. Theorem T11 pins the base statistics: KRK — 399112 states, '
    '4447032 edges, maximum DTM 32 plies (16 moves); KQK — 368452 states, '
    '4869496 edges, maximum 20 plies (10 moves). Both maxima coincide with '
    'the classical tablebase values — an external cross-check unavailable '
    'to self-verification.'))
EN.append(('p',
    'The base is closed by the Bellman machine: the optimality equation is '
    'verified over all states of both bases — zero violations. The forward '
    'search agrees with the bases by spot checks and the tactical '
    'reference: the Morphy mate $\\mathrm{a1a6}$ (3 plies, 46 nodes), the '
    'two-rook ladder $\\mathrm{b1b7}$ (3, 49), the knight-and-rook mate '
    '$\\mathrm{g1g8}$ (1, 1).'))
EN.append(('fig', 'dtm_histogram.png',
    'Fig. 5. The DTM distribution over the states of the endgame bases (theorem T11, check C8).', 76))
EN.append(('p',
    'Theorem T12 assembles everything into the protocol: the nine checks '
    'C1–C9 close the theorems T01–T11 (C1 — algebra, C2 — graphs, C3 — '
    'mobility, C4 — flow, C5 — perft, C6 — fields, C7 — energy, C8 — bases '
    'and tactics, C9 — memory), the failure of any check is isolated and '
    'does not block the others, and the verdict ALL CHECKS PASSED is '
    'reproducible by one command. The polyglot battery C1–C10 prints a '
    'bit-identical verdict 10/10 in seven languages: Python, C and '
    'JavaScript are verified locally, Rust, Go, Julia and Java in GitHub '
    'Actions on every push. The program is closed: every theorem has an '
    'executable form.'))

EN.append(('h1', 'Appendix A. The consolidated table of constants'))
EN.append(('table', 'Protocol constants of the chess-dynamics-lab program',
 ['Constant', 'Value', 'Theorem', 'Check'],
 [['$V_4$ / $D_4$ orbits', '20 / 10', 'T01', 'C1'],
  ['move graph edges R/B/N/K/Q', '448/280/168/210/728', 'T02', 'C2'],
  ['mobility sums K/N/B/R/Q', '420/336/560/896/1456', 'T03', 'C3'],
  ['maximum queen mobility', '27', 'T03', 'C3'],
  ['start-position field (one side)', '38', 'T04', 'C6'],
  ['pawn anomaly', '176 = 88 + 88', 'T04', 'C6'],
  ['energy after 1.e4 (kinetic term)', '+1.0', 'T05', 'C7'],
  ['$t^*$, corner billiard (3, 2)', 'lcm(8/1, 8/2) = 8', 'T06', 'C4'],
  ['damping', '$\\gamma = \\pi^4/256$, path $|v_0|/(1-\\gamma)$', 'T06', 'C4'],
  ['closed knight tour', '64 moves from f5, closure d6→f5', 'T07', 'C10'],
  ['perft(1..5)', '20/400/8902/197281/4865609', 'T08', 'C5'],
  ['Zobrist key table', '1562 words, seed 0x1234567890ABCDEF', 'T09', 'C9'],
  ['splitmix64(1)', '0x910A2DEC89025CC1', 'T09', 'C9'],
  ['collision bound at $n = 10^9$', '0.0271', 'T09', 'C9'],
  ['alpha-beta nodes, depth 2–5', '79/731/3345/19753', 'T10', 'baseline'],
  ['KRK: states / edges / max DTM', '399112 / 4447032 / 32 plies', 'T11', 'C8'],
  ['KQK: states / edges / max DTM', '368452 / 4869496 / 20 plies', 'T11', 'C8'],
  ['Bellman violations', '0', 'T11', 'C8'],
  ['Morphy mate', 'a1a6, 3 plies, 46 nodes', 'T11', 'C8']]))

EN.append(('h1', 'Appendix B. The reproduction guide'))
EN.append(('p',
    'The laboratory deploys from the repository without external '
    'dependencies: the dynamics.py core is a single self-contained file on '
    'the Python standard library (matplotlib is optional, only for the '
    'plots). The full protocol: python3 dynamics.py --report — prints nine '
    '[PASS]/[FAIL] lines and the verdict; individual checks — python3 '
    'dynamics.py --run C5 (the deep mode is the --deep flag adding '
    'perft(5) and the full divide table). Position analysis: --analyze '
    'FEN --depth 4; forced mate: --mate FEN; self-play: '
    'engine/game_player.py --selfplay --depth 4; plots: --plots '
    'reports/plots.'))
EN.append(('p',
    'The polyglot core: bash polyglot/run_all.sh runs the C1–C10 battery '
    'in all available languages and prints the summary table; in a clean '
    'environment python3 polyglot/python/chess_core.py suffices. Tests: '
    'python3 -m pytest tests/ -q (36 tests). The DTM bases ship compressed '
    'in results/ and are verified by the Bellman machine at every C8 run.'))
EN.append(('p',
    'Android (Termux): pkg install python git; git clone the repository; '
    'python3 dynamics.py --report. The full --report takes tens of seconds '
    'on a smartphone (dominated by C5), individual checks seconds. For '
    'publishing a fork see INSTRUCTION.md: the scripts/termux_push.sh '
    'script creates a branch, commits and pushes the repository to a '
    'GitHub account in one command. The CI runs the protocol and the '
    'polyglot battery on the language matrix at every push, so the '
    'repository verdict is always current.'))

EN.append(('h1', 'Bibliography'))
EN.append(('bib', [
    'Shannon C. E. Programming a Computer for Playing Chess // Philosophical '
    'Magazine. 1950. Vol. 41, No. 314. P. 256–275.',
    'Zobrist A. L. A New Hashing Method with Application for Game Playing / '
    'Tech. Rep. 88. University of Wisconsin, 1970; reprinted: ICCA Journal. '
    '1990. Vol. 13, No. 2. P. 69–73.',
    'Knuth D. E., Moore R. W. An Analysis of Alpha-Beta Pruning // Artificial '
    'Intelligence. 1975. Vol. 6, No. 4. P. 293–326.',
    'Thompson K. Retrograde Analysis of Certain Endgames // ICCA Journal. '
    '1986. Vol. 9, No. 3. P. 131–139.',
    'Schwenk A. J. Which Rectangular Chessboards Have a Knight’s Tour? // '
    'Mathematics Magazine. 1991. Vol. 64, No. 5. P. 325–332.',
    'Tromp J. The Number of Legal Go Positions // ICGA Journal. 2016. '
    'Vol. 39, No. 1. P. 3–13; see also J. Tromp’s materials on perft and '
    'chess position counting (johntromp.github.io).',
    'Isaev I. Kh. The Dynamic Principle: monads, layers and the protocols of '
    'verifiable mathematics. The hodge-laboratory program, 2025. GitHub: '
    'wild8highlander/hodge-laboratory.',
    'Isaev I. Kh. Chess Particle Dynamics: theorems T01–T12, the C1–C9 '
    'protocol and the polyglot core. The chess-dynamics-lab program, 2026. '
    'GitHub: wild8highlander/chess-dynamics-lab.',
]))

MAIN_EN = EN

MAIN = {
    'id': 'MAIN',
    'slug': 'chess_particle_dynamics',
    'title': META_MAIN['title'],
    'subtitle': META_MAIN['subtitle'],
    'keywords': META_MAIN['keywords'],
    'content': {'ru': MAIN_RU, 'en': MAIN_EN},
}


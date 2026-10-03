# -*- coding: utf-8 -*-
"""Theorem monograph content, part 3: T09-T12 (RU + EN).

Block grammar shared by the LaTeX and DOCX generators:
  ('h1', text)                    section heading
  ('p', text)                     paragraph; inline math in $...$
  ('f', latex, plain)             display formula: LaTeX and Unicode forms
  ('thm', label, latex, plain)    theorem environment body
  ('table', caption, headers, rows)
"""

T = []

# ════════════════════════════════════════════════════════════════════════
T.append({
    'id': 'T09',
    'slug': 'zobrist_incrementality',
    'title': {'ru': 'Хеширование Цобриста: биективность splitmix64 и инкрементальность',
              'en': 'Zobrist Hashing: the splitmix64 Bijection and Incrementality'},
    'subtitle': {'ru': 'Монография T09 программы chess-dynamics-lab — слой KLEIN, память потока',
                 'en': 'Theorem monograph T09 of the chess-dynamics-lab program — the KLEIN layer, memory of the flow'},
    'keywords': {'ru': 'хеш Цобриста, splitmix64, биекция, инкрементальность, граница дней рождения',
                 'en': 'Zobrist hashing, splitmix64, bijection, incrementality, birthday bound'},
    'content': {
        'ru': [
            ('h1', 'Постановка задачи'),
            ('p', 'Слой KLEIN — память модели: дискретный поток ходов должен '
                  'различать свои состояния, иначе таблицы транспозиций, '
                  'ретроградный анализ T11 и весь протокол верификации не имеют '
                  'общей системы координат. Классическое решение — хеширование '
                  'Цобриста (1970): каждой атомарной компоненте состояния '
                  'сопоставлен случайный 64-битный ключ, а хеш позиции есть XOR '
                  'ключей всех присутствующих компонент. Композиция по XOR дёшева '
                  'и инкрементальна, но её корректность держится на двух фактах, '
                  'которые необходимо доказывать: генератор ключей должен '
                  'порождать воспроизводимую и статистически добротную '
                  'последовательность без внешних источников энтропии, а '
                  'инкрементальное обновление должно в точности совпадать с '
                  'полным пересчётом на каждом шаге потока.'),
            ('p', 'Мы отвечаем на оба требования конструктивно. Генератор — '
                  'splitmix64, финализатор семейства FastHash: сложение с '
                  'золотой константой и два раунда «сдвиг-ксор, умножение». Он '
                  'компактный настолько, что одна и та же функция на семи языках '
                  'полиглот-ядра даёт бит-в-бит одинаковые таблицы: '
                  'кросс-языковая воспроизводимость становится частью теоремы, а '
                  'не надеждой на аккуратность портов. Инкрементальность '
                  'доказывается индукцией по последовательности ходов с явной '
                  'формулой дельты — включая рокировки, взятия на проходе и '
                  'превращения.'),
            ('p', 'Отдельный вопрос — безопасность 64-битного пространства: '
                  'достаточно ли его для таблицы транспозиций. Мы приводим '
                  'точную границу дней рождения и показываем, что даже при '
                  'миллиарде занесённых позиций вероятность хотя бы одной '
                  'коллизии остаётся ниже трёх процентов, а практические режимы '
                  'лаборатории находятся на много порядков глубже безопасной '
                  'зоны.'),
            ('h1', 'Теорема'),
            ('thm', 'Теорема T09 (биективность splitmix64 и инкрементальность хеша).',
                    'Отображение splitmix64: $x_0 = x + \\gamma$, '
                    '$\\gamma = \\text{0x9E3779B97F4A7C15}$; '
                    '$x_1 = (x_0 \\oplus (x_0 \\gg 30)) \\cdot '
                    '\\text{0xBF58476D1CE4E5B9}$; '
                    '$x_2 = (x_1 \\oplus (x_1 \\gg 27)) \\cdot '
                    '\\text{0x94D049BB133111EB}$; '
                    '$\\sigma(x) = x_2 \\oplus (x_2 \\gg 31)$; все операции '
                    'по модулю $2^{64}$. Тогда: (i) $\\sigma$ — биекция '
                    '$\\mathbb{Z}/2^{64}$ с явно выписываемой обратной; '
                    '(ii) таблица ключей из 1562 слов, порождённая зерном '
                    '$\\text{0x1234567890ABCDEF}$, состоит из $12 \\times 128$ '
                    'фигурных, одного стороннего, 16 рокировочных и 9 '
                    'проходных ключей; (iii) для любой позиции $P$ и хода $m$ '
                    'инкрементальный хеш равен полному пересчёту: '
                    '$h(\\mathrm{make}(P,m)) = h(P) \\oplus \\Delta(m)$, где '
                    '$\\Delta(m)$ зависит только от компонент, изменённых '
                    'ходом; (iv) при случайных ключах вероятность коллизии '
                    'для $n$ позиций не превосходит $n(n-1)/2^{65}$; при '
                    '$n = 10^9$ это $0.027$.',
                    'The splitmix64 map: x0 = x + gamma, gamma = '
                    '0x9E3779B97F4A7C15; x1 = (x0 ^ (x0 >> 30)) * '
                    '0xBF58476D1CE4E5B9; x2 = (x1 ^ (x1 >> 27)) * '
                    '0x94D049BB133111EB; sigma(x) = x2 ^ (x2 >> 31); all '
                    'operations modulo 2^64. Then: (i) sigma is a bijection of '
                    'Z/2^64 with an explicitly writable inverse; (ii) the key '
                    'table of 1562 words seeded by 0x1234567890ABCDEF consists '
                    'of 12 x 128 piece keys, one side key, 16 castling keys '
                    'and 9 en-passant keys; (iii) for any position P and move '
                    'm the incremental hash equals the full recomputation: '
                    'h(make(P,m)) = h(P) ^ Delta(m), where Delta(m) depends '
                    'only on the components changed by the move; (iv) under '
                    'random keys the collision probability for n positions is '
                    'at most n(n-1)/2^65; for n = 10^9 this is 0.027.'),
            ('h1', 'Доказательство'),
            ('p', '(i) Биективность. Все три ступени — биекции кольца '
                  '$\\mathbb{Z}/2^{64}$. Сложение с константой биективно '
                  'тривиально. Умножение на константу $u$ биективно тогда и '
                  'только тогда, когда $u$ нечётно: нечётное $u$ взаимно просто '
                  'с $2^{64}$, по теореме Безу существует $u^{-1} \\bmod '
                  '2^{64}$, и обе константы 0xBF58476D1CE4E5B9 и '
                  '0x94D049BB133111EB нечётны. Сдвиг-ксор $x \\mapsto x \\oplus '
                  '(x \\gg s)$ обращается бесконечным рядом '
                  '$y \\mapsto y \\oplus (y \\gg s) \\oplus (y \\gg 2s) \\oplus '
                  '\\cdots$: старшие биты $x$ восстанавливаются немедленно, '
                  'младшие — каскадом, и ряд обрывается, как только сдвиг '
                  'достигает ширины слова. Для $s \\in \\{30, 27, 31\\}$ '
                  'достаточно двух членов $s$ и $2s$: член $y \\gg 3s$ и все '
                  'последующие нулевые, поскольку $3s \\ge 64$. Обратная '
                  'функция реализована в лаборатории буквально: каскады '
                  'раскручиваются в обратном порядке, нечётные множители '
                  'заменяются модулярными обратными, затем вычитается '
                  '$\\gamma$.'),
            ('p', 'Биективность подтверждается конструктивно: round-trip '
                  '$\\sigma^{-1}(\\sigma(x)) = x$ исполнен для всех '
                  '$x \\in [1, 2000]$ в проверке C7 и для всех 1562 табличных '
                  'ключей в C9. Первые значения последовательности фиксируют '
                  'кросс-языковой эталон: $\\sigma(1) = '
                  '\\text{0x910A2DEC89025CC1}$, $\\sigma(2) = '
                  '\\text{0x975835DE1C9756CE}$, $\\sigma(3) = '
                  '\\text{0x1D0B14E4DB018FED}$. Каждый из семи бекендов '
                  'полиглот-ядра обязан воспроизвести их бит в бит; '
                  'расхождение означало бы дефект целочисленной арифметики — '
                  'знаковый сдвиг, потерю старших битов без 64-битных '
                  'беззнаковых типов или неверную эмуляцию переполнения.'),
            ('p', '(iii) Инкрементальность. Индукция по ходам. Определим '
                  '$h(P)$ как XOR ключей всех атомов позиции: по одному ключу '
                  'на каждую фигуру на клетке, плюс ключ стороны (если ход '
                  'чёрных), ключ рокировочного состояния (из 16) и ключ файла '
                  'взятия на проходе (индекс 0 = «нет»). Пусть $\\Delta(m)$ — '
                  'XOR ключей всех атомов, изменённых ходом $m$: ушедшая '
                  'фигура с поля-источника, пришедшая фигура на поле-цель, '
                  'взятая фигура, пешка, побитая на проходе, превращение, '
                  'ладьи при рокировке, старое и новое рокировочное '
                  'состояние, старый и новый ep-ключ, ключ стороны (дважды). '
                  'Каждый удалённый атом входит в $h(P) \\oplus \\Delta(m)$ '
                  'чётное число раз и исчезает, каждый добавленный — '
                  'нечётное и появляется; атомы, не затронутые ходом, в '
                  '$\\Delta$ не входят вовсе. Базис индукции — начальная '
                  'позиция, шаг — произвольный легальный ход; рокировки и '
                  'взятия на проходе обработаны отдельными ветвями (четыре '
                  'случая ладей, ep-индекс — файл плюс единица, а не клетка). '
                  'Следовательно, инкрементальный хеш после make совпадает с '
                  'полным пересчётом на каждом шаге.'),
            ('p', 'Проверка C9 исполняет 40 случайных партий до 60 полуходов '
                  '(фиксированное зерно 42): после каждого полухода '
                  'инкрементальный хеш сравнивается с пересчитанным с нуля — '
                  'расхождений нет; дополнительно unmake каждого из первых '
                  'восьми ходов восстанавливает и FEN, и хеш начальной '
                  'позиции точно. Отметим историческую деталь, зафиксированную '
                  'теоремой как часть определения: эпизод с индексацией '
                  'ep-ключа клеткой вместо файла дал бы ложные коллизии '
                  'внутри одного файла — индексация файлом исправлена и '
                  'закреплена протоколом.'),
            ('p', '(iv) Граница коллизий. Для $n$ независимо и равномерно '
                  'выбранных 64-битных значений вероятность хотя бы одной '
                  'коллизии не превосходит $\\binom{n}{2}/2^{64} = '
                  'n(n-1)/2^{65}$ по объединённой границе. При $n = 10^9$ '
                  'это $10^{18}/2^{65} \\approx 0.0271$; при $n = 10^6$ — '
                  '$2.7 \\times 10^{-8}$. Практические режимы лаборатории — '
                  'поиск до глубины 6 и ретроградные базы порядка $4 \\times '
                  '10^6$ состояний — лежат глубоко во втором режиме. Теорема '
                  'доказана.'),
            ('h1', 'Протокольные данные'),
            ('table', 'Эталонные значения splitmix64 (кросс-языковой сертификат)',
             ['Величина', 'Значение'],
             [['splitmix64(1)', '0x910A2DEC89025CC1'],
              ['splitmix64(2)', '0x975835DE1C9756CE'],
              ['splitmix64(3)', '0x1D0B14E4DB018FED'],
              ['зерно таблицы ключей', '0x1234567890ABCDEF'],
              ['золотая константа', '0x9E3779B97F4A7C15']]),
            ('table', 'Состав таблицы ключей (итого 1562 слова)',
             ['Группа', 'Число ключей', 'Индексация'],
             [['фигурные', '1536', 'тип-цвет × 0x88-клетка'],
              ['сторона', '1', 'XOR при ходе чёрных'],
              ['рокировка', '16', 'битовая маска прав'],
              ['взятие на проходе', '9', '0 = нет, 1..8 = файл + 1']]),
            ('table', 'Результаты проверки C9',
             ['Параметр', 'Результат'],
             [['инкрементальность (40 партий × ≤ 60 полуходов)',
               'полное совпадение с пересчётом'],
              ['unmake-восстановление', 'FEN и хеш точны после каждого хода'],
              ['round-trip обратной функции', 'x = 1..2000, без исключений'],
              ['граница коллизий при n = 10^9', '0.0271']]),
            ('h1', 'Итог доказанного'),
            ('p', 'Мы доказали биективность splitmix64 с явной обратной '
                  'функцией, зафиксировали состав и зерно таблицы из 1562 '
                  'ключей как кросс-языковой эталон, доказали инкрементальное '
                  'тождество $h(\\mathrm{make}(P,m)) = h(P) \\oplus '
                  '\\Delta(m)$ индукцией по ходам с явной дельтой и привели '
                  'точную границу коллизий. Тем самым слой KLEIN получил '
                  'надёжную память: таблицы транспозиций, ретроградные базы '
                  'T11 и детерминизм поиска T10 оперируют хешем, корректность '
                  'которого сертификатно проверена и воспроизводима на семи '
                  'языках.'),
            ('h1', 'Проверка'),
            ('p', 'python3 dynamics.py --run C9 (инкрементальность, unmake, '
                  'round-trip обратной функции); python3 dynamics.py --run C7 '
                  '(обратная функция на отрезке 1..2000); строка C9 '
                  'полиглот-ядра во всех семи языках обязана выдать [PASS] с '
                  'теми же эталонными константами. Время исполнения C9 — '
                  'доли секунды даже на телефоне.'),
        ],
        'en': [
            ('h1', 'Problem statement'),
            ('p', 'The KLEIN layer is the memory of the model: the discrete '
                  'flow of moves must distinguish its states, otherwise the '
                  'transposition tables, the retrograde analysis T11 and the '
                  'whole verification protocol lack a common coordinate '
                  'system. The classical solution is Zobrist hashing (1970): '
                  'each atomic component of the state receives a random '
                  '64-bit key, and the hash of a position is the XOR of the '
                  'keys of all components present. The XOR composition is '
                  'cheap and incremental, but its correctness rests on two '
                  'facts that must be proved: the key generator must produce '
                  'a reproducible and statistically sound sequence without '
                  'external entropy sources, and the incremental update must '
                  'coincide exactly with the full recomputation at every '
                  'step of the flow.'),
            ('p', 'We answer both requirements constructively. The generator '
                  'is splitmix64, the finalizer of the FastHash family: an '
                  'addition of the golden constant followed by two rounds of '
                  'xorshift-multiply. It is compact enough that the same '
                  'function in the seven languages of the polyglot core '
                  'produces bit-identical tables: cross-language '
                  'reproducibility becomes part of the theorem rather than a '
                  'hope for port accuracy. Incrementality is proved by '
                  'induction over the move sequence with an explicit delta '
                  'formula covering castling, en passant and promotion.'),
            ('p', 'A separate question is the safety of the 64-bit space: is '
                  'it sufficient for a transposition table. We give the '
                  'exact birthday bound and show that even with a billion '
                  'stored positions the probability of at least one '
                  'collision stays below three percent, while the practical '
                  'regimes of the laboratory are orders of magnitude deeper '
                  'inside the safe zone.'),
            ('h1', 'Theorem'),
            ('thm', 'Theorem T09 (splitmix64 bijectivity and hash incrementality).',
                    'The splitmix64 map: x0 = x + gamma, gamma = '
                    '0x9E3779B97F4A7C15; x1 = (x0 ^ (x0 >> 30)) * '
                    '0xBF58476D1CE4E5B9; x2 = (x1 ^ (x1 >> 27)) * '
                    '0x94D049BB133111EB; sigma(x) = x2 ^ (x2 >> 31); all '
                    'operations modulo 2^64. Then: (i) sigma is a bijection '
                    'of Z/2^64 with an explicitly writable inverse; (ii) the '
                    'key table of 1562 words seeded by 0x1234567890ABCDEF '
                    'consists of 12 x 128 piece keys, one side key, 16 '
                    'castling keys and 9 en-passant keys; (iii) for any '
                    'position P and move m the incremental hash equals the '
                    'full recomputation: h(make(P,m)) = h(P) ^ Delta(m), '
                    'where Delta(m) depends only on the components changed '
                    'by the move; (iv) under random keys the collision '
                    'probability for n positions is at most n(n-1)/2^65; '
                    'for n = 10^9 this is 0.027.',
                    'Same statement in plain words: splitmix64 is invertible '
                    'on 64-bit words; the 1562-key table seeded by '
                    '0x1234567890ABCDEF covers pieces, side, castling and en '
                    'passant; the incremental XOR update equals the full '
                    'recomputation for every legal move; the birthday bound '
                    'gives collision probability at most n(n-1)/2^65, equal '
                    'to 0.027 for a billion positions.'),
            ('h1', 'Proof'),
            ('p', '(i) Bijectivity. All three stages are bijections of the '
                  'ring Z/2^64. Addition of a constant is trivially '
                  'bijective. Multiplication by a constant u is bijective '
                  'exactly when u is odd: an odd u is coprime to 2^64, so by '
                  'Bezout there exists u^{-1} mod 2^64, and both constants '
                  '0xBF58476D1CE4E5B9 and 0x94D049BB133111EB are odd. The '
                  'xorshift x -> x ^ (x >> s) is inverted by the infinite '
                  'series y -> y ^ (y >> s) ^ (y >> 2s) ^ ...: the high bits '
                  'of x are recovered immediately, the low ones by cascade, '
                  'and the series terminates once the shift reaches the word '
                  'width. For s in {30, 27, 31} two terms s and 2s suffice: '
                  'the term y >> 3s and all later ones vanish since '
                  '3s >= 64. The inverse function is implemented literally: '
                  'the cascades are unwound in reverse order, the odd '
                  'multipliers are replaced by modular inverses, and finally '
                  'gamma is subtracted.'),
            ('p', 'Bijectivity is confirmed constructively: the round-trip '
                  'sigma^{-1}(sigma(x)) = x is executed for all x in '
                  '[1, 2000] in check C7 and for all 1562 table keys in C9. '
                  'The first values of the sequence fix the cross-language '
                  'reference: sigma(1) = 0x910A2DEC89025CC1, sigma(2) = '
                  '0x975835DE1C9756CE, sigma(3) = 0x1D0B14E4DB018FED. Each '
                  'of the seven polyglot backends must reproduce them bit '
                  'for bit; a mismatch would indicate a defect of integer '
                  'arithmetic — a signed shift, loss of high bits without '
                  '64-bit unsigned types, or wrong overflow emulation.'),
            ('p', '(iii) Incrementality. Induction over moves. Define h(P) '
                  'as the XOR of the keys of all atoms of the position: one '
                  'key per piece on a square, plus the side key (when Black '
                  'is to move), the castling-state key (out of 16) and the '
                  'en-passant file key (index 0 = none). Let Delta(m) be the '
                  'XOR of the keys of all atoms changed by the move m: the '
                  'piece leaving the source square, the piece arriving at '
                  'the target, the captured piece, the pawn captured en '
                  'passant, the promotion, the rooks in castling, the old '
                  'and new castling states, the old and new ep keys, and the '
                  'side key twice. Every removed atom enters h(P) ^ Delta(m) '
                  'an even number of times and disappears, every added one '
                  'enters an odd number of times and appears; atoms not '
                  'touched by the move do not enter Delta at all. The base '
                  'of the induction is the initial position, the step is an '
                  'arbitrary legal move; castling and en passant are handled '
                  'by separate branches (four rook cases, the ep index being '
                  'the file plus one rather than a square). Hence the '
                  'incremental hash after make coincides with the full '
                  'recomputation at every step.'),
            ('p', 'Check C9 executes 40 random games of up to 60 plies (the '
                  'fixed seed 42): after every ply the incremental hash is '
                  'compared with the recomputed one — no mismatches; '
                  'additionally, unmake of each of the first eight moves '
                  'restores both the FEN and the hash of the start position '
                  'exactly. Note a historical detail fixed by the theorem as '
                  'part of the definition: indexing the ep key by square '
                  'instead of file would produce false collisions inside one '
                  'file — the file indexing was corrected and pinned by the '
                  'protocol.'),
            ('p', '(iv) Collision bound. For n independently and uniformly '
                  'chosen 64-bit values the probability of at least one '
                  'collision is at most binom(n,2)/2^64 = n(n-1)/2^65 by the '
                  'union bound. For n = 10^9 this is 10^18/2^65 ≈ 0.0271; '
                  'for n = 10^6 it is 2.7e-8. The practical regimes of the '
                  'laboratory — search to depth 6 and retrograde bases of '
                  'about 4e6 states — lie far inside the second regime. The '
                  'theorem is proved.'),
            ('h1', 'Protocol data'),
            ('table', 'Reference values of splitmix64 (cross-language certificate)',
             ['Quantity', 'Value'],
             [['splitmix64(1)', '0x910A2DEC89025CC1'],
              ['splitmix64(2)', '0x975835DE1C9756CE'],
              ['splitmix64(3)', '0x1D0B14E4DB018FED'],
              ['key table seed', '0x1234567890ABCDEF'],
              ['golden constant', '0x9E3779B97F4A7C15']]),
            ('table', 'Composition of the key table (1562 words in total)',
             ['Group', 'Number of keys', 'Indexing'],
             [['piece', '1536', 'type-color × 0x88 square'],
              ['side', '1', 'XOR when Black is to move'],
              ['castling', '16', 'bitmask of rights'],
              ['en passant', '9', '0 = none, 1..8 = file + 1']]),
            ('table', 'Results of check C9',
             ['Parameter', 'Result'],
             [['incrementality (40 games × ≤ 60 plies)',
               'full agreement with recomputation'],
              ['unmake restoration', 'FEN and hash exact after every move'],
              ['inverse round-trip', 'x = 1..2000, no exceptions'],
              ['collision bound at n = 10^9', '0.0271']]),
            ('h1', 'Summary of what is proved'),
            ('p', 'We proved the bijectivity of splitmix64 with an explicit '
                  'inverse, fixed the composition and the seed of the '
                  '1562-key table as a cross-language reference, proved the '
                  'incremental identity h(make(P,m)) = h(P) ^ Delta(m) by '
                  'induction over moves with an explicit delta, and gave the '
                  'exact collision bound. The KLEIN layer thereby received a '
                  'reliable memory: transposition tables, the retrograde '
                  'bases of T11 and the determinism of the search T10 operate '
                  'on a hash whose correctness is certificate-verified and '
                  'reproducible in seven languages.'),
            ('h1', 'Verification'),
            ('p', 'python3 dynamics.py --run C9 (incrementality, unmake, the '
                  'inverse round-trip); python3 dynamics.py --run C7 (the '
                  'inverse function on the segment 1..2000); the C9 line of '
                  'the polyglot core in all seven languages must print '
                  '[PASS] with the same reference constants. The C9 runtime '
                  'is a fraction of a second even on a phone.'),
        ],
    },
})

# ════════════════════════════════════════════════════════════════════════
T.append({
    'id': 'T10',
    'slug': 'alphabeta_bounds',
    'title': {'ru': 'Границы альфа-бета: ветвление, упорядочивание частиц и детерминизм поиска',
              'en': 'The Alpha-Beta Bounds: Branching, Particle Ordering, and Search Determinism'},
    'subtitle': {'ru': 'Монография T10 программы chess-dynamics-lab — полная игра',
                 'en': 'Theorem monograph T10 of the chess-dynamics-lab program — the full game'},
    'keywords': {'ru': 'альфа-бета, негамакс, ветвление, упорядочивание ходов, детерминизм',
                 'en': 'alpha-beta, negamax, branching, move ordering, determinism'},
    'content': {
        'ru': [
            ('h1', 'Постановка задачи'),
            ('p', 'Полная игра — второй контур движка: поиск минимизирует '
                  'лагранжеву энергию T05 по дереву легальных ходов. Наивный '
                  'минимакс перебирает $b^d$ листьев, где $b$ — среднее '
                  'ветвление (для шахмат $b \\approx 30{-}35$), и уже при '
                  '$d = 6$ требует миллиардов узлов. Альфа-бета отсекает '
                  'ветви, которые заведомо не могут повлиять на выбор хода в '
                  'корне; масштаб выигрыша — от нуля до извлечения '
                  'квадратного корня из экспоненты — зависит исключительно от '
                  'порядка рассмотрения ходов.'),
            ('p', 'В модели частиц порядок ходов — это кинематика: первыми '
                  'рассматриваются ходы частиц с наибольшим ожидаемым '
                  'изменением энергии. Практический носитель идеи — эвристика '
                  'MVV-LVA (most valuable victim — least valuable aggressor) '
                  'с кинетическим бонусом централизации: взятие дорогой '
                  'фигуры дешёвой частицей — самый вероятный источник резкого '
                  'падения энергии, поэтому такие ходы идут первыми и '
                  'порождают отсечения раньше. Порядок не меняет значения '
                  'корня — только путь к нему и стоимость пути.'),
            ('p', 'Третье требование — детерминизм: одинаковый вход обязан '
                  'давать одинаковый ход, одинаковое число узлов и одинаковую '
                  'главную вариацию. Для сертифицируемой лаборатории это не '
                  'вопрос стиля, а условие воспроизводимости протокола: '
                  'сравнение узлов и линий между запусками, машинами и '
                  'языками имеет смысл только при полностью детерминированном '
                  'поиске.'),
            ('h1', 'Теорема'),
            ('thm', 'Теорема T10 (корректность, границы и детерминизм альфа-бета).',
                    'Пусть $T_d$ — дерево легальных продолжений глубины $d$ '
                    'из позиции $P$, $b$ — ветвление. Тогда: (i) негамакс с '
                    'окном $(\\alpha, \\beta)$ возвращает то же значение и '
                    'тот же лучший ход, что и полный минимакс; (ii) в '
                    'худшем порядке ходов число посещённых листьев равно '
                    '$b^d$, в лучшем — $b^{\\lceil d/2 \\rceil} + '
                    'b^{\\lfloor d/2 \\rfloor} - 1$; (iii) с упорядочиванием '
                    'MVV-LVA и централизацией на начальной позиции поиск '
                    'посещает: $d = 2$ — 79 узлов против 421 полного дерева, '
                    '$d = 3$ — 731 против 9323, $d = 4$ — 3345 против '
                    '206604, $d = 5$ — 19753 против 5072213 (выигрыш '
                    '$\\times 5.3$, $\\times 12.8$, $\\times 61.8$, '
                    '$\\times 256.8$ соответственно); (iv) при тотальном '
                    'порядке на множестве ходов поиск детерминирован: ход, '
                    'значение и число узлов воспроизводимы бит в бит.',
                    'Let T_d be the tree of legal continuations of depth d '
                    'from position P, b the branching factor. Then: (i) '
                    'negamax with the window (alpha, beta) returns the same '
                    'value and the same best move as full minimax; (ii) in '
                    'the worst move order the number of visited leaves is '
                    'b^d, in the best — b^ceil(d/2) + b^floor(d/2) - 1; '
                    '(iii) with MVV-LVA and centralization ordering on the '
                    'start position the search visits: d = 2 — 79 nodes '
                    'against 421 of the full tree, d = 3 — 731 against '
                    '9323, d = 4 — 3345 against 206604, d = 5 — 19753 '
                    'against 5072213 (gains 5.3x, 12.8x, 61.8x, 256.8x '
                    'respectively); (iv) under a total order on the move '
                    'set the search is deterministic: the move, the value '
                    'and the node count are bit-reproducible.'),
            ('h1', 'Доказательство'),
            ('p', '(i) Корректность. Негамакс-тождество '
                  '$\\mathrm{val}(P) = \\max_m [-\\mathrm{val}(P \\cdot m)]$ '
                  'сводит минимакс к единой форме для обеих сторон: оценка '
                  'всегда с точки зрения стороны на ходу, родитель '
                  'максимизирует минус ребёнка. Индукция по $d$: отсечение '
                  '$\\beta$-типа возвращает границу $\\beta$, а не точное '
                  'значение, но по индукционному предположению точное '
                  'значение отсечённого поддерева лежит вне окна, '
                  'необходимого родителю, и потому не может изменить ни '
                  'значение корня, ни аргумент максимума. Это классический '
                  'аргумент Кнута–Мура (1975) в негамакс-форме; добавления '
                  'лаборатории — квиесценция на листьях (перебор только '
                  'взятий до успокоения позиции) и кодирование мата '
                  '$-\\mathrm{MATE} + ply$, предпочитающее более короткий '
                  'мат, — не изменяют аргумент, поскольку сохраняют '
                  'монотонность оценки по дереву. Правило 50 ходов '
                  '(счётчик $\\ge 100$) возвращает ноль — ничью.'),
            ('p', '(ii) Границы. Худший порядок: ни одно отсечение не '
                  'срабатывает, дерево обходится целиком — $b^d$ листьев. '
                  'Лучший порядок (отсекающий ход всегда первым): после '
                  'первого хода корня окно сжимается, и каждое следующее '
                  'поддерево требует полного раскрытия лишь «половины» '
                  'своей глубины; подсчёт Кнута–Мура даёт '
                  '$b^{\\lceil d/2 \\rceil} + b^{\\lfloor d/2 \\rfloor} - 1$ '
                  'листьев — корень экспоненты вместо самой экспоненты. '
                  'Между границами качество эвристики порядка решает всё; '
                  'MVV-LVA — стандартный шахматный компромисс между '
                  'точностью предсказания отсечений и ценой сортировки.'),
            ('p', '(iii) Измерения. Счётчик узлов считает вызовы negamax, '
                  'включая узлы квиесценции; эталон полного дерева — сумма '
                  '$\\sum_{k=0}^{d} \\mathrm{perft}(k)$ с перфт-значениями, '
                  'сертифицированными в T08. Выигрыш растёт с глубиной, '
                  'сближаясь с предсказанием (ii): это согласуется с '
                  'качеством MVV-LVA в шахматных дебютах, где взятия '
                  'действительно концентрируются у вершины дерева '
                  'вариантов. Значения зафиксированы протоколом как '
                  'эталонные: любой регресс генерации или упорядочивания '
                  'меняет их и обнаруживается сравнением с базовой строкой '
                  'результатов.'),
            ('p', '(iv) Детерминизм. order_moves сортирует ходы стабильной '
                  'сортировкой по тотальному числовому ключу; входной '
                  'порядок детерминирован фиксированным обходом 0x88-доски '
                  'в генераторе; равные ключи сохраняют порядок генерации. '
                  'Все операции поиска чистые: make/unmake точно '
                  'восстанавливают состояние (проверено в T09). '
                  'Следовательно, траектория поиска — функция пары '
                  '(позиция, глубина), и одинаковые запуски дают бит-в-бит '
                  'одинаковые результаты на любой машине и в любом языке. '
                  'Теорема доказана.'),
            ('h1', 'Протокольные данные'),
            ('table', 'Узлы альфа-бета на начальной позиции (MVV-LVA + централизация)',
             ['Глубина', 'Узлы поиска', 'Полное дерево', 'Выигрыш'],
             [['2', '79', '421', '× 5.3'],
              ['3', '731', '9323', '× 12.8'],
              ['4', '3345', '206604', '× 61.8'],
              ['5', '19753', '5072213', '× 256.8']]),
            ('table', 'Служба поиска: компоненты, влияющие на границы',
             ['Компонент', 'Роль', 'Сертификат'],
             [['MVV-LVA + централизация', 'порядок ходов, ранние отсечения',
               'таблица узлов (iii)'],
              ['квиесценция', 'взятия на листьях, устранение горизонта',
               'самосогласованность самопартий'],
              ['код мата −MATE + ply', 'предпочтение кратчайшего мата',
               'тактический эталон T11(iv)'],
              ['правило 50 ходов', 'ничья при halfmove ≥ 100', 'тесты pytest'],
              ['стабильная сортировка', 'тотальный порядок ходов',
               'воспроизводимость (iv)']]),
            ('h1', 'Итог доказанного'),
            ('p', 'Мы доказали корректность негамакс-поиска с окном, '
                  'воспроизвели классические границы худшего и лучшего '
                  'порядков, зафиксировали протокольные измерения узлов '
                  '(до ×256.8 на глубине 5) и доказали детерминизм поиска. '
                  'Тем самым контур полной игры опирается на те же '
                  'сертифицированные фундаменты, что и ретроградный анализ: '
                  'генерация T08, память T09 и энергия T05.'),
            ('h1', 'Проверка'),
            ('p', 'python3 dynamics.py --analyze <FEN> --depth 4 (ход, '
                  'оценка, узлы); python3 engine/game_player.py --selfplay '
                  '--depth 4 (детерминированные самопартии); форсированные '
                  'проверки C8 исполняются тем же поисковым ядром. Сравнение '
                  'узлов с таблицей теоремы выполняется тестами pytest '
                  '(baseline_c1_c9.json).'),
        ],
        'en': [
            ('h1', 'Problem statement'),
            ('p', 'The full game is the second loop of the engine: the '
                  'search minimizes the Lagrangian energy of T05 over the '
                  'tree of legal moves. Naive minimax enumerates b^d leaves, '
                  'where b is the average branching factor (for chess b ≈ '
                  '30–35), and already at d = 6 demands billions of nodes. '
                  'Alpha-beta prunes branches that provably cannot affect '
                  'the choice of the root move; the scale of the gain — from '
                  'zero to the square root of the exponent — depends solely '
                  'on the order in which moves are examined.'),
            ('p', 'In the particle model the move order is kinematics: '
                  'moves of the particles with the largest expected energy '
                  'change are examined first. The practical carrier of the '
                  'idea is the MVV-LVA heuristic (most valuable victim — '
                  'least valuable aggressor) with a kinetic centralization '
                  'bonus: the capture of an expensive piece by a cheap '
                  'particle is the most likely source of a sharp energy '
                  'drop, so such moves come first and produce cutoffs '
                  'earlier. The ordering does not change the root value — '
                  'only the path to it and the cost of the path.'),
            ('p', 'The third requirement is determinism: the same input '
                  'must produce the same move, the same node count and the '
                  'same principal variation. For a certifiable laboratory '
                  'this is not a matter of style but a condition of '
                  'protocol reproducibility: comparing node counts and '
                  'lines across runs, machines and languages is meaningful '
                  'only under a fully deterministic search.'),
            ('h1', 'Theorem'),
            ('thm', 'Theorem T10 (alpha-beta correctness, bounds and determinism).',
                    'Let T_d be the tree of legal continuations of depth d '
                    'from position P, b the branching factor. Then: (i) '
                    'negamax with the window (alpha, beta) returns the same '
                    'value and the same best move as full minimax; (ii) in '
                    'the worst move order the number of visited leaves is '
                    'b^d, in the best — b^ceil(d/2) + b^floor(d/2) - 1; '
                    '(iii) with MVV-LVA and centralization ordering on the '
                    'start position the search visits: d = 2 — 79 nodes '
                    'against 421 of the full tree, d = 3 — 731 against '
                    '9323, d = 4 — 3345 against 206604, d = 5 — 19753 '
                    'against 5072213 (gains 5.3x, 12.8x, 61.8x, 256.8x '
                    'respectively); (iv) under a total order on the move '
                    'set the search is deterministic: the move, the value '
                    'and the node count are bit-reproducible.',
                    'Same statement in plain words: negamax is exact; the '
                    'leaf count lies between b^d and the Knuth–Moore bound '
                    'of the square-root scale; the measured node counts '
                    'with MVV-LVA ordering are 79, 731, 3345, 19753 for '
                    'depths 2–5; the search is fully deterministic under a '
                    'total move order.'),
            ('h1', 'Proof'),
            ('p', '(i) Correctness. The negamax identity val(P) = max_m '
                  '[-val(P·m)] reduces minimax to a single form for both '
                  'sides: the score is always from the point of view of the '
                  'side to move, and the parent maximizes the negated child. '
                  'Induction over d: a beta-cutoff returns the bound beta '
                  'rather than the exact value, but by the inductive '
                  'hypothesis the exact value of the pruned subtree lies '
                  'outside the window required by the parent and therefore '
                  'can change neither the root value nor the argument of '
                  'the maximum. This is the classical Knuth–Moore argument '
                  '(1975) in negamax form; the laboratory additions — '
                  'quiescence at the leaves (searching only captures until '
                  'the position calms down) and the mate encoding '
                  '-MATE + ply, which prefers the shorter mate — do not '
                  'alter the argument since they preserve the monotonicity '
                  'of the score over the tree. The 50-move rule (counter '
                  '≥ 100) returns zero — a draw.'),
            ('p', '(ii) Bounds. The worst order: no cutoff ever fires, the '
                  'tree is traversed entirely — b^d leaves. The best order '
                  '(the cutoff move always first): after the first root '
                  'move the window collapses, and every subsequent subtree '
                  'requires a full expansion of only half of its depth; the '
                  'Knuth–Moore count gives b^ceil(d/2) + b^floor(d/2) - 1 '
                  'leaves — the square root of the exponent instead of the '
                  'exponent itself. Between the bounds the quality of the '
                  'ordering heuristic decides everything; MVV-LVA is the '
                  'standard chess compromise between the accuracy of '
                  'cutoff prediction and the cost of sorting.'),
            ('p', '(iii) Measurements. The node counter counts negamax '
                  'calls, including quiescence nodes; the full-tree '
                  'reference is the sum of perft(0..d) with the perft '
                  'values certified in T08. The gain grows with depth, '
                  'approaching the prediction of (ii): this agrees with the '
                  'quality of MVV-LVA in chess openings, where captures '
                  'really do concentrate near the top of the tree of '
                  'variations. The values are pinned by the protocol as '
                  'reference: any regression of generation or ordering '
                  'changes them and is caught by comparison with the frozen '
                  'baseline.'),
            ('p', '(iv) Determinism. order_moves sorts the moves by a '
                  'stable sort over a total numeric key; the input order is '
                  'determined by the fixed 0x88 board traversal of the '
                  'generator; equal keys keep the generation order. All '
                  'search operations are pure: make/unmake restore the '
                  'state exactly (verified in T09). Hence the search '
                  'trajectory is a function of the pair (position, depth), '
                  'and identical runs produce bit-identical results on any '
                  'machine and in any language. The theorem is proved.'),
            ('h1', 'Protocol data'),
            ('table', 'Alpha-beta nodes on the start position (MVV-LVA + centralization)',
             ['Depth', 'Search nodes', 'Full tree', 'Gain'],
             [['2', '79', '421', '× 5.3'],
              ['3', '731', '9323', '× 12.8'],
              ['4', '3345', '206604', '× 61.8'],
              ['5', '19753', '5072213', '× 256.8']]),
            ('table', 'Search service: components affecting the bounds',
             ['Component', 'Role', 'Certificate'],
             [['MVV-LVA + centralization', 'move order, early cutoffs',
               'node table (iii)'],
              ['quiescence', 'captures at leaves, horizon removal',
               'selfplay self-consistency'],
              ['mate code −MATE + ply', 'preference of the shortest mate',
               'tactical reference T11(iv)'],
              ['50-move rule', 'draw at halfmove ≥ 100', 'pytest tests'],
              ['stable sort', 'total move order', 'reproducibility (iv)']]),
            ('h1', 'Summary of what is proved'),
            ('p', 'We proved the correctness of the windowed negamax '
                  'search, reproduced the classical worst- and best-case '
                  'bounds, pinned the protocol node measurements (up to '
                  '256.8x at depth 5) and proved the determinism of the '
                  'search. The full-game loop thereby rests on the same '
                  'certified foundations as the retrograde analysis: the '
                  'generation of T08, the memory of T09 and the energy of '
                  'T05.'),
            ('h1', 'Verification'),
            ('p', 'python3 dynamics.py --analyze <FEN> --depth 4 (move, '
                  'score, nodes); python3 engine/game_player.py --selfplay '
                  '--depth 4 (deterministic self-play); the forced checks '
                  'of C8 run on the same search core. The comparison of '
                  'node counts with the table of the theorem is performed '
                  'by the pytest tests (baseline_c1_c9.json).'),
        ],
    },
})

# ════════════════════════════════════════════════════════════════════════
T.append({
    'id': 'T11',
    'slug': 'mate_certificates',
    'title': {'ru': 'Сертификаты мата: ретроградные базы KQK/KRK и тактический эталон',
              'en': 'Mate Certificates: the Retrograde KQK/KRK Bases and the Tactical Reference'},
    'subtitle': {'ru': 'Монография T11 программы chess-dynamics-lab — мат в N',
                 'en': 'Theorem monograph T11 of the chess-dynamics-lab program — mate in N'},
    'keywords': {'ru': 'ретроградный анализ, DTM, KRK, KQK, сертификат мата, машина Беллмана',
                 'en': 'retrograde analysis, DTM, KRK, KQK, mate certificate, Bellman machine'},
    'content': {
        'ru': [
            ('h1', 'Постановка задачи'),
            ('p', 'Мат в N — самый жёсткий тест шахматного вычислителя: он '
                  'требует одновременно корректной генерации ходов (иначе '
                  '«мат» окажется нелегальным), точной семантики мата и пата '
                  'и способности доказывать форсированную линию. Матовая '
                  'функциональность лаборатории опирается на два независимых '
                  'инструмента: прямой поиск форсированного мата — '
                  'итеративное углубление с восстановлением полной главной '
                  'вариации — и ретроградный анализ, обратную индукцию от '
                  'всех матовых позиций эндшпиля. Инструменты устроены '
                  'по-разному (прямой ход времени против обратного, локальное '
                  'дерево против глобальной базы), и их согласование — '
                  'двусторонняя верификация, слабая к общим ошибкам обеих '
                  'сторон лишь в той мере, в какой они разделяют генератор '
                  'ходов, сертифицированный отдельно в T08.'),
            ('p', 'Ретроградный анализ строит расстояние до мата (DTM) для '
                  'всего пространства позиций трёх фигур: KRK (король и '
                  'ладья против короля) и KQK (король и ферзь против '
                  'короля). Эти две базы — классический материал теории '
                  'эндшпиля: их максимальные DTM известны десятилетиями — 16 '
                  'и 10 ходов соответственно — и опубликованы в табличных '
                  'базах, что даёт внешнюю сверку, недоступную '
                  'самопроверке.'),
            ('p', 'Замыкает конструкцию машина Беллмана: уравнение '
                  'оптимальности проверяется не на выборке, а по всем '
                  'состояниям обеих баз. Любое нарушение уравнения — сигнал '
                  'дефекта индукции, упаковки или генерации; ноль нарушений '
                  'по всем состояниям — сильнейшая форма сертификата, '
                  'доступная для конечного пространства.'),
            ('h1', 'Теорема'),
            ('thm', 'Теорема T11 (ретроградные базы и согласование с прямым поиском).',
                    '(i) Пространство KRK содержит 399112 состояний и '
                    '4447032 ребра; выигранных для сильной стороны 376868, '
                    'матовых 216; максимум DTM равен 32 полуходам, то есть '
                    '16 ходам. (ii) Пространство KQK содержит 368452 '
                    'состояния и 4869496 рёбер; выигранных 345404, матовых '
                    '364; максимум DTM равен 20 полуходам, то есть 10 '
                    'ходам. (iii) Уравнение Беллмана выполнено для каждого '
                    'состояния обеих баз: $\\mathrm{DTM}(s) = 1 + '
                    '\\min_{c} \\mathrm{DTM}(c)$ при ходе атакующей стороны '
                    'и $\\mathrm{DTM}(s) = 1 + \\max_{c} \\mathrm{DTM}(c)$ '
                    'при ходе защищающейся; число нарушений равно нулю. '
                    '(iv) Прямой поиск форсированного мата согласован с '
                    'базами и тактическим эталоном: Морфи (ключ a1a6, 3 '
                    'полухода, PV a1a6 b7a6 b6b7), лестница (b1b7 h8g8 '
                    'a2a8, 3), NR (g1g8, 1).',
                    '(i) The KRK space contains 399112 states and 4447032 '
                    'edges; 376868 are won for the strong side, 216 are '
                    'mates; the maximum DTM is 32 plies, i.e. 16 moves. '
                    '(ii) The KQK space contains 368452 states and 4869496 '
                    'edges; 345404 won, 364 mates; the maximum DTM is 20 '
                    'plies, i.e. 10 moves. (iii) The Bellman equation holds '
                    'for every state of both bases: DTM(s) = 1 + min_c '
                    'DTM(c) with the attacker to move and DTM(s) = 1 + '
                    'max_c DTM(c) with the defender to move; the number of '
                    'violations is zero. (iv) The forward forced-mate search '
                    'agrees with the bases and the tactical reference: '
                    'Morphy (key a1a6, 3 plies, PV a1a6 b7a6 b6b7), ladder '
                    '(b1b7 h8g8 a2a8, 3), NR (g1g8, 1).'),
            ('h1', 'Доказательство'),
            ('p', 'Упаковка пространства. Состояние трёх фигур упаковывается '
                  'в 22 бита: $wk \\,|\\, wq \\ll 7 \\,|\\, bk \\ll 14 \\,|\\, '
                  'stm \\ll 21$, где каждая клетка — 7-битный 0x88-код, а '
                  '$stm \\in \\{0, 1\\}$ — сторона на ходу. Всего $2^{22} = '
                  '4194304$ слота; реализуемых — с несмежными королями, '
                  'некоролём на клетке сильной фигуры и без взаимных '
                  'нападений — 399112 для KRK и 368452 для KQK. Упаковка '
                  'биективна на своём множестве: unpack(pack(s)) = s для '
                  'всех состояний, что подтверждено кросс-валидацией; '
                  'историческая поправка — расширение с 19 до 22 бит, когда '
                  '7-битные 0x88-коды вызвали коллизии в 19-битной '
                  'упаковке.'),
            ('p', 'Ретроградная индукция. Инициализация: матовые состояния '
                  '(сторона на ходу получает шах, не имея легальных ходов) '
                  'получают DTM = 0, остальные — бесконечность. Затем '
                  'проходы обратной индукции: для состояния с ходом '
                  'атакующей стороны ищется ход в уже решённое состояние с '
                  'меньшим DTM, для состояния с ходом защищающейся стороны '
                  'требуется, чтобы все ходы вели в решённые; предшественники '
                  'берутся из CSR-массива обратных рёбер, построенного '
                  'одновременно с перечислением прямых рёбер (указатели '
                  'записываются в порядке перечисления, а не числового '
                  'сортирования — дефект, исправленный при разработке). '
                  'Проходы повторяются до стабилизации; множество решённых '
                  'состояний монотонно растёт, и алгоритм завершается, '
                  'поскольку пространство конечно.'),
            ('p', '(iii) Машина Беллмана. После стабилизации выполняется '
                  'сквозная проверка по всем 399112 и 368452 состояниям: '
                  'для каждого выигранного состояния уравнение '
                  'оптимальности сверяется с фактическими DTM детей, '
                  'для проигранных — что все дети выиграны, для не '
                  'достижимых для выигрыша — что ни один ребёнок не '
                  'выигран. Результат: ноль нарушений в обеих базах. '
                  'Дополнительно прямой точечный контроль: mate_search на '
                  'выборке состояний возвращает то же число полуходов, что '
                  'и база (forward_spot_ok), и кросс-валидация ходов '
                  'ретрограда с perft-проверенным генератором на 299 '
                  'состояниях выявила ровно те «мисматчи», которые '
                  'оказались дефектом самой проверки (маппинг взятия ладьи '
                  'в невалидное состояние), а не баз.'),
            ('p', '(iv) Прямой поиск и эталон. Итеративное углубление с '
                  '_mate_dfs возвращает кратчайшее форсирование с полной '
                  'PV, содержащей самые упорные ответы защищающейся '
                  'стороны. Тактический эталон: морфийский мат в два хода '
                  '— единственный ключ a1a6 (46 узлов), двухладейная '
                  'лестница с ключом b1b7 (49 узлов), мат конём и ладьёй '
                  'в один ход g1g8 (1 узел). Совпадение длины, ключа и '
                  'полной PV сертифицирует прямой поиск; малые числа '
                  'узлов демонстрируют силу упорядочивания T10(iii). '
                  'Внешняя сверка: максимумы 16 и 10 ходов совпадают с '
                  'классическими табличными значениями; история разработки '
                  'даёт живую иллюстрацию чувствительности метода — дефект '
                  'обработки захвата защищённого ферзя давал ложный '
                  'максимум 11 ходов в KQK, и лишь исправление порядка '
                  'проверок в _children_black вернуло табличные 10. '
                  'Теорема доказана.'),
            ('h1', 'Протокольные данные'),
            ('table', 'Статистика ретроградных баз (проверка C8)',
             ['База', 'Состояния', 'Рёбра', 'Выигранных', 'Матов',
              'Max DTM, полуходов', 'Max DTM, ходов'],
             [['KRK', '399112', '4447032', '376868', '216', '32', '16'],
              ['KQK', '368452', '4869496', '345404', '364', '20', '10']]),
            ('table', 'Тактический эталон прямого поиска',
             ['Задача', 'FEN', 'Полуходов', 'PV', 'Узлы'],
             [['morphy_m2', 'kbK5/pp6/1P6/8/8/8/8/R7 w - - 0 1', '3',
               'a1a6 b7a6 b6b7', '46'],
              ['ladder_m2', '7k/8/8/8/8/8/R7/1R4K1 w - - 0 1', '3',
               'b1b7 h8g8 a2a8', '49'],
              ['nr_m1', '7k/8/5N1K/8/8/8/8/6R1 w - - 0 1', '1', 'g1g8',
               '1']]),
            ('h1', 'Итог доказанного'),
            ('p', 'Мы построили ретроградные базы DTM для KRK и KQK на '
                  '22-битной упаковке с CSR-предшественниками, проверили '
                  'уравнение Беллмана по всем состояниям (ноль нарушений), '
                  'согласовали обратную индукцию с прямым поиском точечными '
                  'проверками и тактическим эталоном и сверили максимумы с '
                  'классикой — 16 и 10 ходов. Мат в N в лаборатории — не '
                  'эвристика, а сертифицированная процедура с двусторонней '
                  'верификацией.'),
            ('h1', 'Проверка'),
            ('p', 'python3 dynamics.py --run C8 (базы, Беллман, тактика); '
                  'python3 dynamics.py --run C8 --deep (расширенные '
                  'точечные проверки); python3 dynamics.py --mate "<FEN>" '
                  '(форсированный мат с PV). Базы хранятся сжатыми в '
                  'results/dtm_krk.json.gz и results/dtm_kqk.json.gz; '
                  'время полной проверки C8 — секунды.'),
        ],
        'en': [
            ('h1', 'Problem statement'),
            ('p', 'Mate in N is the hardest test of a chess computer: it '
                  'demands simultaneously a correct move generator '
                  '(otherwise the "mate" turns out illegal), the exact '
                  'semantics of mate and stalemate, and the ability to '
                  'prove a forced line. The mate functionality of the '
                  'laboratory rests on two independent instruments: the '
                  'forward forced-mate search — iterative deepening with '
                  'the reconstruction of the full principal variation — and '
                  'the retrograde analysis, a backward induction from all '
                  'mated positions of the endgame. The instruments are '
                  'structured differently (forward versus backward time, a '
                  'local tree versus a global base), and their agreement is '
                  'a two-sided verification, vulnerable to common errors '
                  'only insofar as they share the move generator, which is '
                  'certified separately in T08.'),
            ('p', 'The retrograde analysis builds the distance to mate '
                  '(DTM) for the whole space of three-piece positions: KRK '
                  '(king and rook against king) and KQK (king and queen '
                  'against king). These two bases are the classical '
                  'material of endgame theory: their maximum DTM values '
                  'have been known for decades — 16 and 10 moves '
                  'respectively — and are published in tablebases, which '
                  'provides an external cross-check unavailable to '
                  'self-verification.'),
            ('p', 'The construction is closed by the Bellman machine: the '
                  'optimality equation is checked not on a sample but over '
                  'all states of both bases. Any violation of the equation '
                  'signals a defect of the induction, the packing or the '
                  'generation; zero violations over all states is the '
                  'strongest form of certificate available for a finite '
                  'space.'),
            ('h1', 'Theorem'),
            ('thm', 'Theorem T11 (retrograde bases and agreement with the forward search).',
                    '(i) The KRK space contains 399112 states and 4447032 '
                    'edges; 376868 are won for the strong side, 216 are '
                    'mates; the maximum DTM is 32 plies, i.e. 16 moves. '
                    '(ii) The KQK space contains 368452 states and 4869496 '
                    'edges; 345404 won, 364 mates; the maximum DTM is 20 '
                    'plies, i.e. 10 moves. (iii) The Bellman equation holds '
                    'for every state of both bases: DTM(s) = 1 + min_c '
                    'DTM(c) with the attacker to move and DTM(s) = 1 + '
                    'max_c DTM(c) with the defender to move; the number of '
                    'violations is zero. (iv) The forward forced-mate search '
                    'agrees with the bases and the tactical reference: '
                    'Morphy (key a1a6, 3 plies, PV a1a6 b7a6 b6b7), ladder '
                    '(b1b7 h8g8 a2a8, 3), NR (g1g8, 1).',
                    'Same statement in plain words: the KRK and KQK DTM '
                    'bases match the classical tablebase statistics, the '
                    'Bellman optimality equation holds over every state '
                    'with zero violations, and the forward mate search '
                    'reproduces the known solutions of the reference '
                    'problems.'),
            ('h1', 'Proof'),
            ('p', 'Packing the space. A three-piece state is packed into 22 '
                  'bits: wk | wq << 7 | bk << 14 | stm << 21, where each '
                  'square is a 7-bit 0x88 code and stm in {0, 1} is the '
                  'side to move. There are 2^22 = 4194304 slots in total; '
                  'the realizable ones — with non-adjacent kings, no piece '
                  'on a king square and no mutual attacks — number 399112 '
                  'for KRK and 368452 for KQK. The packing is bijective on '
                  'its set: unpack(pack(s)) = s for all states, confirmed '
                  'by cross-validation; a historical correction — the '
                  'extension from 19 to 22 bits when the 7-bit 0x88 codes '
                  'caused collisions in the 19-bit packing.'),
            ('p', 'Retrograde induction. Initialization: mated states (the '
                  'side to move is in check with no moves) receive DTM = 0, '
                  'the rest receive infinity. Then the backward passes: for '
                  'a state with the attacker to move a move into an already '
                  'solved state with a smaller DTM is sought; for a state '
                  'with the defender to move all moves must lead into '
                  'solved states; predecessors are taken from the CSR array '
                  'of reverse edges built simultaneously with the '
                  'enumeration of the forward edges (the pointers are '
                  'recorded in enumeration order rather than numeric sort '
                  'order — a defect fixed during development). The passes '
                  'repeat until stabilization; the set of solved states '
                  'grows monotonically and the algorithm terminates since '
                  'the space is finite.'),
            ('p', '(iii) The Bellman machine. After stabilization a '
                  'through check runs over all 399112 and 368452 states: '
                  'for every won state the optimality equation is verified '
                  'against the actual DTM values of the children; for lost '
                  'states — that all children are won; for draws — that no '
                  'child is won. The result: zero violations in both '
                  'bases. Additionally, a forward spot control: mate_search '
                  'on a sample of states returns the same ply count as the '
                  'base (forward_spot_ok), and the cross-validation of the '
                  'retrograde moves against the perft-verified generator on '
                  '299 states exposed exactly those "mismatches" that '
                  'turned out to be a defect of the test itself (mapping a '
                  'rook capture into an invalid state) rather than of the '
                  'bases.'),
            ('p', '(iv) The forward search and the reference. Iterative '
                  'deepening with _mate_dfs returns the shortest forcing '
                  'line with the full PV containing the most resistant '
                  'replies of the defender. The tactical reference: the '
                  'Morphy mate in two — the unique key a1a6 (46 nodes); '
                  'the two-rook ladder with the key b1b7 (49 nodes); the '
                  'knight-and-rook mate in one g1g8 (1 node). The agreement '
                  'of the length, the key and the full PV certifies the '
                  'forward search; the small node counts demonstrate the '
                  'power of the ordering of T10(iii). The external '
                  'cross-check: the maxima 16 and 10 moves coincide with '
                  'the classical tablebase values; the development history '
                  'gives a live illustration of the sensitivity of the '
                  'method — a defect in handling the capture of a defended '
                  'queen produced a false maximum of 11 moves in KQK, and '
                  'only fixing the check order in _children_black restored '
                  'the tabular 10. The theorem is proved.'),
            ('h1', 'Protocol data'),
            ('table', 'Statistics of the retrograde bases (check C8)',
             ['Base', 'States', 'Edges', 'Won', 'Mates',
              'Max DTM, plies', 'Max DTM, moves'],
             [['KRK', '399112', '4447032', '376868', '216', '32', '16'],
              ['KQK', '368452', '4869496', '345404', '364', '20', '10']]),
            ('table', 'Tactical reference of the forward search',
             ['Problem', 'FEN', 'Plies', 'PV', 'Nodes'],
             [['morphy_m2', 'kbK5/pp6/1P6/8/8/8/8/R7 w - - 0 1', '3',
               'a1a6 b7a6 b6b7', '46'],
              ['ladder_m2', '7k/8/8/8/8/8/R7/1R4K1 w - - 0 1', '3',
               'b1b7 h8g8 a2a8', '49'],
              ['nr_m1', '7k/8/5N1K/8/8/8/8/6R1 w - - 0 1', '1', 'g1g8',
               '1']]),
            ('h1', 'Summary of what is proved'),
            ('p', 'We built the DTM retrograde bases for KRK and KQK on the '
                  '22-bit packing with CSR predecessors, verified the '
                  'Bellman equation over all states (zero violations), '
                  'aligned the backward induction with the forward search '
                  'by spot checks and the tactical reference, and '
                  'cross-checked the maxima against the classical 16 and 10 '
                  'moves. Mate in N in the laboratory is not a heuristic '
                  'but a certified procedure with two-sided verification.'),
            ('h1', 'Verification'),
            ('p', 'python3 dynamics.py --run C8 (bases, Bellman, tactics); '
                  'python3 dynamics.py --run C8 --deep (extended spot '
                  'checks); python3 dynamics.py --mate "<FEN>" (forced mate '
                  'with the PV). The bases are stored compressed in '
                  'results/dtm_krk.json.gz and results/dtm_kqk.json.gz; the '
                  'full C8 check runs in seconds.'),
        ],
    },
})

# ════════════════════════════════════════════════════════════════════════
T.append({
    'id': 'T12',
    'slug': 'state_space_protocol',
    'title': {'ru': 'Пространство состояний и протокол C1–C9',
              'en': 'The State Space and the C1–C9 Protocol'},
    'subtitle': {'ru': 'Монография T12 программы chess-dynamics-lab — сводный протокол',
                 'en': 'Theorem monograph T12 of the chess-dynamics-lab program — the consolidated protocol'},
    'keywords': {'ru': 'пространство состояний, протокол, изоляция отказов, воспроизводимость',
                 'en': 'state space, protocol, failure isolation, reproducibility'},
    'content': {
        'ru': [
            ('h1', 'Постановка задачи'),
            ('p', 'Теоремы T01–T11 описывают отдельные слои модели частиц — '
                  'алгебру доски, кинематику графов, мобильность, поля '
                  'угроз, энергию, поток, генерацию, память и поиск. Но '
                  'физика имеет силу лишь тогда, когда все её слои живут в '
                  'одном точно специфицированном пространстве состояний и '
                  'проверяются единым протоколом. Это заключительное звено '
                  'теории программы: определить состояние, показать '
                  'устройство его пространства и зафиксировать протокол '
                  'C1–C9 — девять проверок, каждая из которых сертификатно '
                  'закрывает свою теорему.'),
            ('p', 'Принцип унаследован от родительской программы '
                  'hodge-laboratory: утверждение считается доказанным, если '
                  'оно воспроизводится протоколом одной командой на любой '
                  'машине — от сервера до телефона под Termux. Поэтому '
                  'протокол спроектирован как набор изолированных проверок: '
                  'отказ одной не блокирует остальные, каждая возвращает '
                  'булев вердикт и подробности, а суммарный вердикт ALL '
                  'CHECKS PASSED достижим только при полном согласии теории '
                  'и вычисления по всем девяти направлениям.'),
            ('p', 'Международный контекст: протокол опирается на классику '
                  'программирования шахмат — перфт-эталоны сообщества, '
                  'табличные значения эндшпильных баз, границу Кнута–Мура, '
                  'хеширование Цобриста — и добавляет собственный слой: '
                  'трёхчастичную модель (поля угроз, лагранжиан, поток) с '
                  'её собственными инвариантами, в первую очередь '
                  'эквивариантностью полей относительно группы доски T01.'),
            ('h1', 'Теорема'),
            ('thm', 'Теорема T12 (пространство состояний и полнота протокола).',
                    '(i) Состояние позиции — набор: доска '
                    '$\\in \\{\\mathrm{EMPTY}, \\ldots, \\mathrm{BK}\\}^{128}$ '
                    'в 0x88-представлении, сторона на ходу, права рокировки '
                    '$\\in 2^4$, ep-клетка, счётчик полуходов, номер хода; '
                    '0x88-кодировка даёт тесты границ и атак за $O(1)$. '
                    '(ii) Для трёхфигурных эндшпилей пространство упаковывается '
                    'в 22 бита; реализуемых состояний: KRK — 399112, KQK — '
                    '368452. (iii) Протокол C1–C9 закрывает теоремы T01–T11: '
                    'каждый чек — булев результат с подробностями; отказ '
                    'изолирован (исключение перехватывается, остальные чеки '
                    'продолжаются); вердикт ALL CHECKS PASSED означает '
                    'одновременный успех всех девяти. (iv) Полиглот-батарея '
                    'C1–C10 в семи языках выдаёт идентичный формат строк '
                    '[PASS]/[FAIL] и итоговый вердикт 10/10.',
                    '(i) A position state is the tuple: the board in {EMPTY, '
                    '..., BK}^128 in the 0x88 representation, the side to '
                    'move, the castling rights in 2^4, the ep square, the '
                    'halfmove clock, the move number; the 0x88 encoding '
                    'gives O(1) boundary and attack tests. (ii) For '
                    'three-piece endgames the space packs into 22 bits; the '
                    'realizable states: KRK — 399112, KQK — 368452. (iii) '
                    'The C1–C9 protocol closes theorems T01–T11: every check '
                    'is a boolean result with details; a failure is isolated '
                    '(the exception is caught, the remaining checks '
                    'continue); the ALL CHECKS PASSED verdict means the '
                    'simultaneous success of all nine. (iv) The polyglot '
                    'battery C1–C10 in seven languages prints an identical '
                    '[PASS]/[FAIL] line format and the final verdict 10/10.'),
            ('h1', 'Доказательство'),
            ('p', '(i) Спецификация. Состояние реализовано структурой '
                  'Position с полем board длины 128: индекс '
                  '$\\mathrm{sq} = r \\cdot 16 + f$ даёт тест '
                  '"вне доски" как $\\mathrm{sq} \\, \\& \\, 0x88 \\ne 0$ — '
                  'одна побитовая операция вместо двух сравнений; смещения '
                  'фигур — константные массивы, не выходящие за границы '
                  'массива. Инвариант круговорота состояния — '
                  'FEN-круговорот: set_fen(to_fen(P)) восстанавливает '
                  'позицию и хеш точно (проверено на всех позициях '
                  'протокола и в тестах pytest). Валидатор is_valid '
                  'проверяет согласованность: ровно по два короля, '
                  'отсутствие пешек на первой и последней горизонталях, '
                  'непротиворечивость прав рокировки и ep.'),
            ('p', '(ii) Редукции пространства. Три принципа сжатия. '
                  'Первый — упаковка трёхфигурных состояний в 22 бита '
                  '(T11): wk | wq<<7 | bk<<14 | stm<<21. Второй — '
                  'симметрийная редукция: группа $V_4$ цветосохраняющих '
                  'симметрий T01 действует свободно на почти всех '
                  'позициях, деля классы эквивалентности примерно на '
                  'четверо; базы хранят орбиты, протокол проверяет '
                  'эквивариантность. Третий — необратимость: счётчик '
                  'полуходов делит историю на деревья продолжений; в '
                  'таблицах транспозиций позиция различима только вместе '
                  'со счётчиком — иначе правило 50 ходов нарушит '
                  'детерминизм.'),
            ('p', '(iii) Соответствие чеков теоремам фиксируется таблицей '
                  'ниже; каждая строка — замкнутый контур «теорема → чек → '
                  'константы». Изоляция отказов реализована в run_protocol: '
                  'каждый чек исполняется в перехвате исключений; FAIL '
                  'возвращает подробности и не прерывает остальные; '
                  'суммарный вердикт — конъюнкция всех булевых результатов. '
                  'Детерминизм всех чеков (фиксированные зерна, тотальный '
                  'порядок ходов T10(iv)) даёт воспроизводимость вердикта '
                  'на любых машинах — x86-серверах и ARM-телефонах под '
                  'Termux.'),
            ('p', '(iv) Кросс-языковая согласованность. Полиглот-ядро '
                  'реализует батарею C1–C10 на семи языках с одинаковым '
                  'форматом вывода: строка «[PASS] Cn примечание» или '
                  '«[FAIL] Cn причина», в конце — «verdict: 10/10». '
                  'Бит-в-бит одинаковые эталонные константы (перфт, '
                  'орбиты, цензы, splitmix64) гарантируют, что расхождение '
                  'хотя бы одного бекенда обнаружится сравнением строк. '
                  'Локально верифицированы Python, C и JavaScript; Rust, '
                  'Go, Julia и Java верифицируются в GitHub Actions при '
                  'каждом пуше. Теорема доказана.'),
            ('h1', 'Протокольные данные'),
            ('table', 'Соответствие протокола и теорем',
             ['Чек', 'Содержание', 'Теорема', 'Ключевые константы'],
             [['C1', 'орбиты V4/D4, лемма Бернсайда', 'T01', '20 и 10 орбит'],
              ['C2', 'цензы рёбер графов ходов', 'T02',
               'R448/B280/N168/K210/Q728'],
              ['C3', 'мобильность: суммы и максимумы', 'T03',
               '896/560/336/420/1456; max 27'],
              ['C4', 'завершение потока t*, бильярд', 'T06',
               't* = lcm(W/gcd(a,W), H/gcd(b,H))'],
              ['C5', 'перфт-идентичности', 'T08',
               '20/400/8902/197281/4865609'],
              ['C6', 'эквивариантность полей угроз', 'T04',
               'коммутирование с D4'],
              ['C7', 'лагранжева энергия', 'T05', 'm = 20; после e4 m = 30'],
              ['C8', 'ретроградные базы + тактика', 'T10, T11',
               'KRK 16, KQK 10 ходов'],
              ['C9', 'цобрист, splitmix64', 'T09',
               '1562 ключей; граница 0.027']]),
            ('table', 'Свойства протокола как системы',
             ['Свойство', 'Механизм', 'Следствие'],
             [['изоляция отказов', 'перехват исключений в run_protocol',
               'FAIL одного чека не скрывает остальные'],
              ['воспроизводимость', 'детерминизм T10(iv), фиксированные зерна',
               'одинаковый вердикт на любой машине'],
              ['кросс-языковость', 'полиглот-батарея C1–C10, 7 языков',
               'verdict: 10/10 строкой-эталоном'],
              ['глубина', 'режим --deep: perft(5), расширенные проверки',
               'две ступени строгости']]),
            ('h1', 'Итог доказанного'),
            ('p', 'Мы специфицировали пространство состояний лаборатории, '
                  'его редукции и инварианты, зафиксировали взаимно '
                  'однозначное соответствие чеков C1–C9 теоремам T01–T11, '
                  'доказали изоляцию отказов и воспроизводимость вердикта, '
                  'а также кросс-языковую согласованность полиглот-батареи. '
                  'Программа тем самым замкнута: каждая теорема имеет '
                  'исполняемую форму, а вся теория — один вердикт, '
                  'проверяемый одной командой.'),
            ('h1', 'Проверка'),
            ('p', 'python3 dynamics.py --report — полный протокол с '
                  'вердиктом; python3 dynamics.py --run Ck — отдельный чек; '
                  'bash polyglot/run_all.sh — кросс-языковая батарея со '
                  'сводной таблицей. Время полного --report на телефоне — '
                  'десятки секунд (доминирует C5), на сервере — секунды.'),
        ],
        'en': [
            ('h1', 'Problem statement'),
            ('p', 'Theorems T01–T11 describe the individual layers of the '
                  'particle model — the board algebra, the kinematics of '
                  'graphs, mobility, threat fields, energy, the flow, the '
                  'generation, the memory and the search. But a physics is '
                  'valid only when all its layers live in one exactly '
                  'specified state space and are verified by a single '
                  'protocol. This is the closing link of the program '
                  'theory: to define the state, to show the structure of '
                  'its space and to fix the C1–C9 protocol — nine checks, '
                  'each of which certificate-closes its own theorem.'),
            ('p', 'The principle is inherited from the parent hodge-laboratory '
                  'program: a statement counts as proved when it is '
                  'reproduced by a one-command protocol on any machine — '
                  'from a server to a Termux phone. Therefore the protocol '
                  'is designed as a set of isolated checks: the failure of '
                  'one does not block the others, each returns a boolean '
                  'verdict and details, and the aggregate verdict ALL '
                  'CHECKS PASSED is attainable only under the full '
                  'agreement of theory and computation across all nine '
                  'directions.'),
            ('p', 'The international context: the protocol builds on the '
                  'classics of chess programming — the community perft '
                  'references, the endgame tablebase values, the '
                  'Knuth–Moore bound, Zobrist hashing — and adds its own '
                  'layer: the three-particle model (threat fields, the '
                  'Lagrangian, the flow) with its own invariants, above all '
                  'the equivariance of the fields under the board group of '
                  'T01.'),
            ('h1', 'Theorem'),
            ('thm', 'Theorem T12 (the state space and the completeness of the protocol).',
                    '(i) A position state is the tuple: the board in '
                    '$\\{\\mathrm{EMPTY}, \\ldots, \\mathrm{BK}\\}^{128}$ '
                    'in the 0x88 representation, the side to move, the '
                    'castling rights in $2^4$, the ep square, the halfmove '
                    'clock, the move number; the 0x88 encoding gives O(1) '
                    'boundary and attack tests. (ii) For '
                    'three-piece endgames the space packs into 22 bits; '
                    'the realizable states: KRK — 399112, KQK — 368452. '
                    '(iii) The C1–C9 protocol closes theorems T01–T11: '
                    'every check is a boolean result with details; a '
                    'failure is isolated (the exception is caught, the '
                    'remaining checks continue); the ALL CHECKS PASSED '
                    'verdict means the simultaneous success of all nine. '
                    '(iv) The polyglot battery C1–C10 in seven languages '
                    'prints an identical [PASS]/[FAIL] line format and the '
                    'final verdict 10/10.',
                    'Same statement in plain words: the state space is '
                    'exactly specified with O(1) 0x88 tests and a '
                    '22-bit endgame packing; the nine protocol checks map '
                    'one-to-one onto the theorems with failure isolation; '
                    'the seven-language battery produces byte-identical '
                    'verdicts.'),
            ('h1', 'Proof'),
            ('p', '(i) Specification. The state is realized by the Position '
                  'structure with a board field of length 128: the index '
                  'sq = r·16 + f turns the "off-board" test into '
                  'sq & 0x88 ≠ 0 — one bitwise operation instead of two '
                  'comparisons; the piece offsets are constant arrays that '
                  'never leave the array bounds. The state round-trip '
                  'invariant — the FEN cycle: set_fen(to_fen(P)) restores '
                  'the position and the hash exactly (verified on all '
                  'protocol positions and in the pytest tests). The '
                  'is_valid validator checks consistency: exactly two '
                  'kings, no pawns on the first and last ranks, the '
                  'consistency of the castling rights and the ep square.'),
            ('p', '(ii) Reductions of the space. Three compression '
                  'principles. First — the 22-bit packing of three-piece '
                  'states (T11): wk | wq<<7 | bk<<14 | stm<<21. Second — '
                  'the symmetry reduction: the group V4 of '
                  'color-preserving symmetries of T01 acts freely on '
                  'almost all positions, cutting the equivalence classes '
                  'roughly fourfold; the bases store orbits, and the '
                  'protocol verifies the equivariance. Third — '
                  'irreversibility: the halfmove clock splits the history '
                  'into continuation trees; in transposition tables a '
                  'position is distinguishable only together with the '
                  'clock — otherwise the 50-move rule would break the '
                  'determinism.'),
            ('p', '(iii) The mapping of the checks to the theorems is '
                  'pinned by the table below; every row is a closed loop '
                  '"theorem → check → constants". Failure isolation is '
                  'implemented in run_protocol: every check runs inside an '
                  'exception catch; a FAIL returns the details and does '
                  'not interrupt the rest; the aggregate verdict is the '
                  'conjunction of all boolean results. The determinism of '
                  'all checks (fixed seeds, the total move order of '
                  'T10(iv)) makes the verdict reproducible on any machine '
                  '— x86 servers and ARM Termux phones alike.'),
            ('p', '(iv) Cross-language consistency. The polyglot core '
                  'implements the C1–C10 battery in seven languages with '
                  'an identical output format: a line "[PASS] Cn note" or '
                  '"[FAIL] Cn reason", ending with "verdict: 10/10". '
                  'Bit-identical reference constants (perft, orbits, '
                  'censuses, splitmix64) guarantee that a mismatch of any '
                  'single backend is caught by comparing the lines. '
                  'Python, C and JavaScript are verified locally; Rust, '
                  'Go, Julia and Java are verified in GitHub Actions on '
                  'every push. The theorem is proved.'),
            ('h1', 'Protocol data'),
            ('table', 'The mapping of the protocol to the theorems',
             ['Check', 'Content', 'Theorem', 'Key constants'],
             [['C1', 'V4/D4 orbits, Burnside lemma', 'T01', '20 and 10 orbits'],
              ['C2', 'edge censuses of the move graphs', 'T02',
               'R448/B280/N168/K210/Q728'],
              ['C3', 'mobility: sums and maxima', 'T03',
               '896/560/336/420/1456; max 27'],
              ['C4', 'flow termination t*, billiard', 'T06',
               't* = lcm(W/gcd(a,W), H/gcd(b,H))'],
              ['C5', 'perft identities', 'T08',
               '20/400/8902/197281/4865609'],
              ['C6', 'equivariance of threat fields', 'T04',
               'commutation with D4'],
              ['C7', 'Lagrangian energy', 'T05', 'm = 20; after e4 m = 30'],
              ['C8', 'retrograde bases + tactics', 'T10, T11',
               'KRK 16, KQK 10 moves'],
              ['C9', 'Zobrist, splitmix64', 'T09',
               '1562 keys; bound 0.027']]),
            ('table', 'Properties of the protocol as a system',
             ['Property', 'Mechanism', 'Consequence'],
             [['failure isolation', 'exception catch in run_protocol',
               'one FAIL hides nothing'],
              ['reproducibility', 'determinism T10(iv), fixed seeds',
               'the same verdict on any machine'],
              ['cross-language reach', 'polyglot battery C1–C10, 7 languages',
               'the verdict: 10/10 reference line'],
              ['depth', 'the --deep mode: perft(5), extended checks',
               'two levels of rigor']]),
            ('h1', 'Summary of what is proved'),
            ('p', 'We specified the state space of the laboratory, its '
                  'reductions and invariants, pinned the one-to-one mapping '
                  'of the checks C1–C9 onto the theorems T01–T11, proved '
                  'the failure isolation and the reproducibility of the '
                  'verdict, and the cross-language consistency of the '
                  'polyglot battery. The program is thereby closed: every '
                  'theorem has an executable form, and the whole theory has '
                  'a single verdict verifiable by one command.'),
            ('h1', 'Verification'),
            ('p', 'python3 dynamics.py --report — the full protocol with '
                  'the verdict; python3 dynamics.py --run Ck — an '
                  'individual check; bash polyglot/run_all.sh — the '
                  'cross-language battery with the summary table. The full '
                  '--report takes tens of seconds on a phone (dominated by '
                  'C5) and seconds on a server.'),
        ],
    },
})

THEOREMS_PART3 = T

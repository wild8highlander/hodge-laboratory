#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
 HODGE PLANES · hodge_planes.py — слой декомпозиции Ходжа для hodge-laboratory

 Недостающий (по заключению научного руководителя, session 2026-11) модуль
 верификации: числа Ходжа, характерное разложение и решётки алгебраических
 циклов для многообразий Ферма — уровень, на котором гипотеза Ходжа
 становится проверяемым утверждением. Только стандартная библиотека.

 Слои (везде минимум ДВЕ независимые схемы — этос репозитория):

   §1  Числа Ходжа гиперповерхности Ферма X = X^n_d ⊂ P^{n+1}.
         схема A (Гриффитс): h^{n−q,q}_prim = dim R_{(q+1)d−(n+2)},
              R = C[x_0..x_{n+1}]/(x_i^{d−1}) — кольцо Якобиана формы
              Σ x_i^d; подсчёт мономов DP (точные целые);
         схема B (Чжен): χ_top = d·[H^n] (1+H)^{n+2}/(1+dH) — формальный
              степенной ряд, точные целые; сравнение Σ(−1)^k b_k;
         схема C: замкнутые формулы (род кривой, p_g и b₂ поверхности).
       Проверено: кривая Ферма d=7 (g=15, baseline репозитория), d=30
       (g=406); K3-квартика (1,20,1); кубическая поверхность (0,7,0);
       квинтика-трёхмерие (1,101,101,1); кубическая четвёрка b₄=23;
       квартиковая четвёрка h^{3,1}=21, h^{2,2}=142, χ=188.

   §2  Характерный ценз H² поверхности Ферма S_m — обобщение ценза кривых
       (T01/T20) с кривых на поверхности. H²(S_m) ⊗ C раскладывается по
       характерам группы G = μ_m⁴/Δ; примитивный характер a = (a_0..a_3),
       0 < a_i < m, Σa ≡ 0 (mod m), даёт одномерное пространство типа
             Σa = m  → H^{2,0},   Σa = 2m → H^{1,1},   Σa = 3m → H^{0,2},
       плюс одномерная тривиальная часть (класс гиперплоскости h).
       Сверяется с §1 (p_g, h^{1,1}) и с b₂ = m³−4m²+6m−2.

   §3  Решётка прямых на S_m: 3m² прямых
              L(π; k1, k2) = {x_i = η_{k1} x_j, x_k = η_{k2} x_l},
       η_t = exp(iπ(2t+1)/m) (η^m = −1), π — разбиение {0,1,2,3} на пары.
         схема A: грамова матрица пересечений — ТОЧНЫЕ целые:
              L·L = 2−m (адъюнкция: L² = −2 − K_S·L, K_S = O(m−4)),
              L·L' = 1 (встреча) / 0 (скрещивание). Правила встреч — из
              решения 4 линейных уравнений (rank < 4 ⇔ встреча); для
              m=4 совпадают с правилами задачи 39 (сравнения mod 8);
              проверены против классики: 27 прямых/10 встреч (m=3),
              48 прямых/14 встреч + SNF [1^18,8,8] (m=4, baseline task39).
         схема B: характерные спектры. Семейство фиксированного π — орбита
              G/H (|G/H| = m²); грамова матрица семейства — групповая
              циркулянта, диагонализуемая характерами: собственное число
              λ_a = Σ_z Φ(z)·χ_a(z)^{-1} — считается ЧЕСТНО в Z[ζ_m]
              (тест нуля — редукция многочлена mod Φ_m) и сверяется с
              замкнутой формой λ_a = m([a_i≡0]+[a_k≡0]−1).
              λ_a ≠ 0 ⇔ характер реализуется в натяжении прямых.
         ранг над Q: mod-p гауссово исключение, несколько простых
              (2,3,5,7,10007) — все должны совпасть со спектром.
         сигнатура: точная (Sylvester над Q) — индекс Ходжа (1, r−1).
       ИТОГ (главное содержательное открытие слоя): прямые натягивают ВСЁ
       H^{1,1}(S_m) при m ≤ 4 (ранги 7, 20) и ТОЛЬКО ЧАСТЬ при m ≥ 5
       (m=5: 37 из 45; m=6: 62 из 86; m=7: 91 из 147; m=8: 128 из 232) —
       честная граница, где «очевидные» циклы перестают натягивать
       пространство классов Ходжа; недостающие характеры §2 точно
       указывает. (По Лефшецу (1,1) все они алгебраичны — нужны ЦИКЛЫ,
       не прямые: на поверхностях гипотеза Ходжа решена, важно честно
       понимать ГДЕ заканчиваются «бесплатные» циклы.)

   §4  Плоскости на квартиковой четвёрке Ферма X = X^4_4 ⊂ P⁵:
       960 плоскостей P(π; k1,k2,k3) = {x_i = η x_j, x_k = η' x_l,
       x_p = η'' x_q}, η^4 = −1, π — разбиение {0..5} на 3 пары (15 шт).
         грамова матрица (внутри семейства, точные целые):
              P·P  = 7  (избыток самопересечения: ∫_P c₂(N_{P/X}),
                        c(N) = (1+H)³/(1+4H), c₂ = 7H²; сверено с
                        известным значением 3 для кубической четвёрки);
              P·P' = 1  (общая точка — трансверсальность автоматична);
              P·P' = −2 (общая прямая — избыток пересечения; вывод:
                        разложение вычетов [P]+[Q] = h² в P³ ∋ P, где Q —
                        остаточная кубика (для Ферма — объединение трёх
                        плоскостей!), [Q]·P' = deg(Q ∩ ℓ) = 3 по Безу в
                        P³, ⇒ [P]·P' = h²·P' − 3 = 1 − 3 = −2; тождество
                        [P]² = h⁴ − 2h²[Q] + [Q]² = 4 − 6 + 9 = 7 сходится);
              P·P' = 0  (пусто).
         характерные спектры 15 семейств: G = μ_4⁶/Δ, |G/H| = 64,
              λ_a считается в Z[i] и сверяется с замкнутой формой
              λ_a = 7 − 2σ₁ + σ₂,  u_t = 4[a_{j_t}≡0]−1;
              λ_a ≠ 0 ⇔ все три «вторых координаты» пар ненулевые
              (27 примитивных (2,2)-характеров + тривиальный = 28).
         размерность натяжения = #∪ характеров по 15 семействам + 1:
              141 примитивный (2,2)-характер реализуется + h² ⇒ 142.
       ИТОГ: 142 = h^{2,2}(X^4_4) — все рациональные классы (2,2) суть
       рациональные комбинации классов 960 плоскостей. Это вычислительная
       верификация гипотезы Ходжа для классов коразмерности 2 на
       квартиковой четвёрке Ферма (случай, покрываемый индуктивной
       структурой Сиоды; здесь он воспроизведён ПРЯМОЙ работой с
       циклами). Замечание: полнота СПИСКА плоскостей (что других
       плоскостей на X нет) — классическая классификация линейных
       подпространств гиперповерхностей Ферма; для самого утверждения
       «классы Ходжа натянутся на плоскости» она не нужна.

 Запуск:  python3 hodge_planes.py            (полный прогон с отчётом)
          python3 hodge_planes.py --quick    (ускоренный набор)
 Только stdlib. Всё — точная целочисленная/рациональная арифметика.
═══════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import math
import sys
from fractions import Fraction

# ────────────────────────────────────────────────────────────────────────────
# §1. ЧИСЛА ХОДЖА ГИПЕРПОВЕРХНОСТЕЙ ФЕРМА: КОЛЬЦО ЯКОБИАНА × ЧЖЕН × ФОРМУЛЫ
# ────────────────────────────────────────────────────────────────────────────

def monomial_count(nvars: int, total: int, maxdeg: int) -> int:
    """Число мономов от nvars переменных степени total с показателями ≤ maxdeg.

    DP по переменным: точные целые. Это dim R_total для
    R = C[x_0..x_{n+1}]/(x_i^{d−1}) при maxdeg = d−2 (частные формы Ферма).
    """
    if total < 0:
        return 0
    cur = [0] * (total + 1)
    cur[0] = 1
    for _ in range(nvars):
        nxt = [0] * (total + 1)
        for s, c in enumerate(cur):
            if c:
                for e in range(0, min(maxdeg, total - s) + 1):
                    nxt[s + e] += c
        cur = nxt
    return cur[total]


def hodge_middle_griffiths(d: int, n: int) -> dict:
    """Примитивные числа Ходжа средней когомологии X^n_d.

    Гриффитс: h^{n−q,q}_prim = dim R_{(q+1)d − (n+2)}, q = 0..n.
    """
    return {q: monomial_count(n + 2, (q + 1) * d - (n + 2), d - 2)
            for q in range(n + 1)}


def chern_euler(d: int, n: int) -> int:
    """χ_top(X^n_d) = d · [H^n] (1+H)^{n+2}/(1+dH) — ряд, точные целые.

    Независимая от Гриффитса схема: c(TX) = (1+H)^{n+2}/(1+dH)|_X,
    χ = ∫_X c_n(TX), ∫_X H^n = d.
    """
    N = n + 2
    num = [math.comb(N, k) for k in range(n + 1)]        # (1+H)^{n+2}
    inv = [(-d) ** k for k in range(n + 1)]              # 1/(1+dH)
    coeff = sum(num[i] * inv[n - i] for i in range(n + 1))
    return d * coeff


def hodge_diamond(d: int, n: int) -> dict:
    """Полный алмаз Ходжа X^n_d: {(p,q): dim}.

    Средняя строка — Гриффитс (+1 к (n/2,n/2) от гиперплоскости);
    ниже средней — Лефшец: h^{k,k} = 1 при 2k < n, прочее 0;
    выше средней — двойственность Пуанкаре.
    """
    mid = hodge_middle_griffiths(d, n)
    dia = {}
    for q in range(n + 1):
        p = n - q
        v = mid[q]
        if p == q:
            v += 1
        dia[(p, q)] = v
    for p in range(n + 1):
        for q in range(n + 1):
            if (p, q) in dia:
                continue
            if p + q < n:
                dia[(p, q)] = 1 if p == q else 0
            else:
                dia[(p, q)] = dia.get((n - p, n - q), 0)
    return dia


def verify_diamond(d: int, n: int) -> tuple:
    """Сверка трёх схем для X^n_d -> (ok, detail, info)."""
    dia = hodge_diamond(d, n)
    b = [sum(v for (p, q), v in dia.items() if p + q == k) for k in range(n + 1)]
    # двойственность Пуанкаре: b_{2n−k} = b_k → полная сумма знакопеременная
    full_b = list(b) + [b[2 * n - k] for k in range(n + 1, 2 * n + 1)]
    chi_hodge = sum((-1) ** k * full_b[k] for k in range(2 * n + 1))
    chi_chern = chern_euler(d, n)
    ok = chi_hodge == chi_chern
    # схема C: замкнутые формулы в известных размерностях
    closed = []
    if n == 1:
        closed.append(("g", dia[(1, 0)], (d - 1) * (d - 2) // 2))
    if n == 2:
        pg = dia[(2, 0)]
        closed.append(("p_g", pg, math.comb(d - 1, 3)))
        closed.append(("b2", b[2], d ** 3 - 4 * d ** 2 + 6 * d - 2))
        closed.append(("h11", dia[(1, 1)], b[2] - 2 * pg))
    for name, got, want in closed:
        ok &= (got == want)
    dia_s = " ".join(f"h^{n - q},{q}={dia[(n - q, q)]}" for q in range(n + 1))
    detail = (f"X^{n}_{d}: {dia_s} · b={b} · "
              f"χ(Ходж)={chi_hodge} = χ(Чжен)={chi_chern}"
              + ("" if not closed else " · формулы: "
                 + ", ".join(f"{nm}:{g}={w}" for nm, g, w in closed)))
    return ok, detail, {"betti": b, "chi": chi_hodge, "diamond": dia}


# ────────────────────────────────────────────────────────────────────────────
# §2. ХАРАКТЕРНЫЙ ЦЕНЗ H² ПОВЕРХНОСТЕЙ ФЕРМА (обобщение ценза кривых T01/T20)
# ────────────────────────────────────────────────────────────────────────────

def surface_characters(m: int) -> dict:
    """Ценз примитивных характеров a ∈ [1,m−1]^4, Σa ≡ 0 (mod m), по типам.

    Возвращает {'p': [(a...), ...] (Σa = m → H^{2,0}),
                '11': [...] (Σa = 2m → H^{1,1}_prim),
                'pp': [...] (Σa = 3m → H^{0,2})}.
    Тривиальная часть (h) одномерна и сюда не входит.
    """
    out = {"p": [], "11": [], "pp": []}
    r = range(1, m)
    for a0 in r:
        for a1 in r:
            for a2 in r:
                for a3 in r:
                    s = a0 + a1 + a2 + a3
                    if s % m:
                        continue
                    key = {m: "p", 2 * m: "11", 3 * m: "pp"}.get(s)
                    if key:
                        out[key].append((a0, a1, a2, a3))
    return out


def verify_surface_characters(m: int, dia: dict) -> tuple:
    """Сверка ценза с алмазом §1 и с b₂ = m³−4m²+6m−2."""
    cs = surface_characters(m)
    b2_char = 1 + len(cs["p"]) + len(cs["11"]) + len(cs["pp"])
    b2_closed = m ** 3 - 4 * m ** 2 + 6 * m - 2
    b2_dia = dia[(2, 0)] + dia[(1, 1)] + dia[(0, 2)]
    ok = (b2_char == b2_closed == b2_dia
          and len(cs["p"]) == dia[(2, 0)] == len(cs["pp"])
          and len(cs["11"]) == dia[(1, 1)] - 1)
    detail = (f"S_{m}: характеров H^2: 1 + {len(cs['p'])} + {len(cs['11'])} + "
              f"{len(cs['pp'])} = {b2_char} = b₂(формула) = {b2_closed} = "
              f"b₂(алмаз) = {b2_dia}; p_g = {len(cs['p'])}, h^11_prim = {len(cs['11'])}")
    return ok, detail, cs


# ────────────────────────────────────────────────────────────────────────────
# §3. РЕШЁТКА ПРЯМЫХ НА ПОВЕРХНОСТИ ФЕРМА S_m
# ────────────────────────────────────────────────────────────────────────────

# разбиения {0,1,2,3} на пары — та же нумерация, что в задаче 39:
# 1: {01}|{23},  2: {02}|{13},  3: {03}|{12}; пара (i,j): x_i = η·x_j
SURF_PARTS = {1: ((0, 1), (2, 3)), 2: ((0, 2), (1, 3)), 3: ((0, 3), (1, 2))}


def surf_lines(m: int) -> list:
    """3m² прямых: (π, k1, k2), η_t = exp(iπ(2t+1)/m), t ∈ [0, m)."""
    return [(p, k1, k2) for p in (1, 2, 3)
            for k1 in range(m) for k2 in range(m)]


def surf_intersect(m: int, L1, L2) -> int:
    """L·L' на S_m: 2−m (совпадение), 1 (встреча), 0 (скрещивание).

    Правила выведены из решения 4 линейных уравнений (rank < 4 ⇔ общая
    точка); для m=4 — в точности правила задачи 39 (сравнения mod 8).
    Экспоненты пар: e = 2k+1 (нечётные, mod 2m).
    """
    p1, a, b = L1
    p2, c, d = L2
    e1, e2 = 2 * a + 1, 2 * b + 1
    f1, f2 = 2 * c + 1, 2 * d + 1
    M = 2 * m
    if p1 == p2:
        if a == c and b == d:
            return 2 - m
        return 1 if ((a == c) != (b == d)) else 0
    if p1 > p2:
        (p1, e1, e2), (p2, f1, f2) = (p2, f1, f2), (p1, e1, e2)
    if p1 == 1 and p2 == 2:                      # вывод: det = η_a ν_d − η_b ν_c
        return 1 if (e1 + f2 - e2 - f1) % M == 0 else 0
    if p1 == 1 and p2 == 3:                      # вывод: det = η_a η_b ξ_d − ξ_c
        return 1 if (f1 - e1 - e2 - f2) % M == 0 else 0
    if p1 == 2 and p2 == 3:                      # вывод: det = ν_a ν_b − ξ_c ξ_d
        return 1 if (e1 + e2 - f1 - f2) % M == 0 else 0
    raise AssertionError(f"недостижимая пара разбиений ({p1},{p2})")


def surf_gram(m: int, with_h: bool = False):
    """Грамова матрица прямых (+ строка/столбец гиперплоскости h)."""
    lines = surf_lines(m)
    n = len(lines)
    size = n + (1 if with_h else 0)
    G = [[0] * size for _ in range(size)]
    for i in range(n):
        for j in range(i, n):
            G[i][j] = G[j][i] = surf_intersect(m, lines[i], lines[j])
    if with_h:
        for i in range(n):
            G[i][n] = G[n][i] = 1            # h·L = deg L = 1
        G[n][n] = m                          # h² = deg S_m = m
    return G, lines


def rank_mod_p(M, p: int) -> int:
    """Ранг над GF(p) — гауссово исключение (независимая схема)."""
    A = [[x % p for x in row] for row in M]
    rows, cols = len(A), len(A[0])
    r = 0
    for c in range(cols):
        piv = next((i for i in range(r, rows) if A[i][c]), None)
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        inv = pow(A[r][c], -1, p)
        for i in range(r + 1, rows):
            if A[i][c]:
                f = A[i][c] * inv % p
                A[i] = [(x - f * y) % p for x, y in zip(A[i], A[r])]
        r += 1
        if r == rows:
            break
    return r


def _ext_gcd(a: int, b: int):
    """Расширенный Евклид: (g, u, v), u·a + v·b = g."""
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
    return old_r, old_s, old_t


def smith_normal_form(M) -> list:
    """SNF целочисленной матрицы — унимодулярные 2×2 НОД-операции.

    На каждом шаге: (a) столбец ниже пивота зануляется парными
    строковыми операциями [[u,v],[b/g,−a/g]] (det = −1) по Безу;
    (b) строка правее — транспонированно; цикл (a)→(b) повторяется,
    пока пивот не станет делителем всей строки и столбца. Пивот
    каждый круг строго «улучшает» делимость (становится НОД большего
    набора) — завершение за O(log) кругов на шаг.
    """
    A = [row[:] for row in M]
    R, C = len(A), len(A[0])
    out = []
    r = c = 0
    while r < R and c < C:
        # пивот: минимальный по |·| ненулевой элемент подматрицы
        best = None
        for i in range(r, R):
            for j in range(c, C):
                if A[i][j] and (best is None
                                or abs(A[i][j]) < abs(A[best[0]][best[1]])):
                    best = (i, j)
        if best is None:
            break
        i0, j0 = best
        A[r], A[i0] = A[i0], A[r]
        for row in A:
            row[c], row[j0] = row[j0], row[c]
        while True:
            # (a) столбец c ниже пивота: при делимости — чистое вычитание
            #     (не трогает строку r), иначе — полный 2×2 НОД-шаг Безу
            #     (пивот строго убывает ⇒ грязь ограничена);
            for i in range(r + 1, R):
                if A[i][c]:
                    a, b = A[r][c], A[i][c]
                    if b % a == 0:
                        q = b // a
                        A[i] = [x - q * y for x, y in zip(A[i], A[r])]
                    else:
                        g, u, v = _ext_gcd(a, b)
                        s, t = b // g, -(a // g)   # det [[u,v],[s,t]] = −1
                        row_r, row_i = A[r][:], A[i][:]
                        A[r] = [u * x + v * y for x, y in zip(row_r, row_i)]
                        A[i] = [s * x + t * y for x, y in zip(row_r, row_i)]
            # (b) строка r правее пивота — симметрично для столбцов
            for j in range(c + 1, C):
                if A[r][j]:
                    a, b = A[r][c], A[r][j]
                    if b % a == 0:
                        q = b // a
                        for i in range(r, R):
                            A[i][j] -= q * A[i][c]
                    else:
                        g, u, v = _ext_gcd(a, b)
                        s, t = b // g, -(a // g)
                        for i in range(r, R):
                            x, y = A[i][c], A[i][j]
                            A[i][c] = u * x + v * y
                            A[i][j] = s * x + t * y
            # (c) готово, если пивот делит ВСЮ подматрицу (не только строку/
            #     столбец): иначе — подтянуть нарушителя в строку r и повторить
            if (all(A[i][c] == 0 for i in range(r + 1, R))
                    and all(A[r][j] == 0 for j in range(c + 1, C))):
                offender = None
                for i in range(r + 1, R):
                    for j in range(c + 1, C):
                        if A[i][j] % A[r][c]:
                            offender = (i, j)
                            break
                    if offender:
                        break
                if offender is None:
                    break
                # прибавляем строку нарушителя к строке r: (r, j) станет
                # ненулевым и не делящимся — цикл повторится с лучшим пивотом
                oi, _oj = offender
                A[r] = [x + y for x, y in zip(A[r], A[oi])]
        if A[r][c] < 0:
            A[r] = [-x for x in A[r]]
        out.append(A[r][c])
        r += 1
        c += 1
    return out


def signature_rational(M) -> tuple:
    """Сигнатура симметричной целочисленной матрицы (Sylvester над Q).

    Стандартный алгоритм: диагональный пивот → счёт знака → Шур-дополнение;
    при нулевой диагонали — 2×2-блок [0 a; a 0] с инерцией (+1, −1)
    (симметричная перестановка строк и столбцов приводит его на место).
    """
    n = len(M)
    A = [[Fraction(x) for x in row] for row in M]

    def swap_rows(i, j):
        A[i], A[j] = A[j], A[i]

    def swap_cols(i, j):
        for r in range(n):
            A[r][i], A[r][j] = A[r][j], A[r][i]

    pos = neg = 0
    k = 0
    while k < n:
        piv = next((i for i in range(k, n) if A[i][i] != 0), None)
        if piv is not None:
            if piv != k:
                swap_rows(piv, k)
                swap_cols(piv, k)
            d = A[k][k]
            if d > 0:
                pos += 1
            else:
                neg += 1
            for i in range(k + 1, n):
                if A[i][k]:
                    f = A[i][k] / d
                    A[i] = [x - f * y for x, y in zip(A[i], A[k])]
            k += 1
        else:
            # ищем внедиагональный элемент в подматрице [k:, k:]
            found = None
            for i in range(k, n):
                for j in range(i + 1, n):
                    if A[i][j] != 0:
                        found = (i, j)
                        break
                if found:
                    break
            if not found:
                break                      # остаток нулевой
            i, j = found
            # симметричная перестановка: строка/столбец i → k, j → k+1
            if i != k:
                swap_rows(i, k)
                swap_cols(i, k)
            if j != k + 1:
                swap_rows(j, k + 1)
                swap_cols(j, k + 1)
            if A[k][k + 1] != 0:
                pos += 1
                neg += 1
                # исключаем k, k+1 из остальных строк (блочный Шур)
                a = A[k][k + 1]
                for i in range(k + 2, n):
                    for jj in range(k + 2, n):
                        # [[0, a], [a, 0]]^{-1} = [[0, 1/a], [1/a, 0]]
                        A[i][jj] -= (A[i][k] * A[k + 1][jj]
                                     + A[i][k + 1] * A[k][jj]) / a
                k += 2
            else:
                k += 1
    return pos, neg


# ── характерные спектры семейств прямых (схема B) ──

# Φ_m(x), коэффициенты по возрастанию степени, СТАРШИЙ = 1 (моничен) —
# правильность деления с остатком в _zeta_zero_test требует моничности.
_cyclotomic_cache = {
    1: [-1, 1],                                    # x − 1
    2: [1, 1],                                     # x + 1
    3: [1, 1, 1],                                  # x² + x + 1
    4: [1, 0, 1],                                  # x² + 1
    5: [1, 1, 1, 1, 1],                            # x⁴ + x³ + x² + x + 1
    6: [1, -1, 1],                                 # x² − x + 1
    7: [1, 1, 1, 1, 1, 1, 1],                      # x⁶ + … + 1
    8: [1, 0, 0, 0, 1],                            # x⁴ + 1
    9: [1, 0, 0, 1, 0, 0, 1],                      # x⁶ + x³ + 1
    10: [1, -1, 1, -1, 1],                         # x⁴ − x³ + x² − x + 1
    11: [1] * 11,                                  # x¹⁰ + … + 1
    12: [1, 0, -1, 0, 1],                           # x⁴ − x² + 1
}


def _zeta_zero_test(coeffs, m: int) -> bool:
    """Σ c_j ζ_m^j = 0? Точно: редукция c(x) mod Φ_m(x) (Φ моничен)."""
    c = list(coeffs)
    while c and c[-1] == 0:
        c.pop()
    if not c:
        return True
    phi = _cyclotomic_cache[m]
    dphi = len(phi) - 1
    if len(c) - 1 < dphi:
        return all(x == 0 for x in c)
    # деление с остатком по убыванию степеней
    while len(c) - 1 >= dphi and any(c):
        lead = c[-1]
        if lead == 0:
            c.pop()
            continue
        shift = len(c) - 1 - dphi
        for i, p in enumerate(phi):
            c[shift + i] -= lead * p
        while c and c[-1] == 0:
            c.pop()
    return not c


def surf_family_spectrum(m: int) -> dict:
    """Спектры трёх семейств прямых: λ_a для всех характеров G, тривиальных на H.

    Семейство π: грамова функция Φ(k1,k2) = (2−m)[(0,0)] + 1 (ровно один
    ноль) + 0 (оба ненулевые); λ_a = Σ_{k1,k2} ζ_m^{−(k1·a_j1 + k2·a_j2)}·Φ.
    Возвращаются: честная сумма (тест нуля в Z[ζ_m]) + замкнутая форма
    λ = m([a_i1≡0] + [a_i2≡0] − 1) — вторая схема.
    """
    out = {}
    for pi, ((i1, j1), (i2, j2)) in SURF_PARTS.items():
        chars = []
        for t1 in range(m):
            for t2 in range(m):
                # a_i = t, a_j = −t (mod m) на каждой паре
                a = [0, 0, 0, 0]
                a[i1], a[j1] = t1 % m, (-t1) % m
                a[i2], a[j2] = t2 % m, (-t2) % m
                Aj = (a[j1], a[j2])                     # «вторые координаты»
                coeffs = [0] * m
                for k1 in range(m):
                    for k2 in range(m):
                        if k1 == 0 and k2 == 0:
                            phi_val = 2 - m
                        elif k1 == 0 or k2 == 0:
                            phi_val = 1
                        else:
                            phi_val = 0
                        if phi_val:
                            e = (k1 * Aj[0] + k2 * Aj[1]) % m
                            coeffs[(m - e) % m] += phi_val
                nonzero = not _zeta_zero_test(coeffs, m)
                closed = m * ((1 if t1 == 0 else 0) + (1 if t2 == 0 else 0) - 1)
                chars.append({"a": tuple(a), "lambda_nonzero": nonzero,
                              "closed": closed})
        out[pi] = chars
    return out


def surf_adapted_union(m: int) -> set:
    """∪ по 3 семействам реализованных примитивных характеров (как 4-кортежи)."""
    u = set()
    for pi, chars in surf_family_spectrum(m).items():
        for ch in chars:
            if ch["lambda_nonzero"] and all(x % m for x in ch["a"]):
                u.add(ch["a"])
    return u


# ────────────────────────────────────────────────────────────────────────────
# §4. ПЛОСКОСТИ КВАРТИКОВОЙ ЧЕТВЁРКИ ФЕРМА X^4_4 ⊂ P⁵: ГИПОТЕЗА ХОДЖА (2,2)
# ────────────────────────────────────────────────────────────────────────────

def perfect_matchings6() -> list:
    """15 разбиений {0..5} на 3 упорядоченные пары (i < j)."""
    def rec(items):
        if not items:
            yield []
            return
        first = items[0]
        for idx in range(1, len(items)):
            partner = items[idx]
            rest = items[1:idx] + items[idx + 1:]
            for tail in rec(rest):
                yield [(first, partner)] + tail
    return sorted(rec([0, 1, 2, 3, 4, 5]))


def fourfold_family_gram(matching) -> list:
    """64×64 грамова матрица семейства плоскостей фиксированного разбиения.

    Индексация (k1,k2,k3) ∈ [0,4)³; η_t = ζ_8^{2t+1} (η^4 = −1).
    Значения: 7 (совпадение), −2 (ровно 2 общих η — общая прямая),
    1 (ровно 1 — общая точка), 0 (ни одного).
    """
    def phi(k1, k2, k3):
        z = (k1 == 0) + (k2 == 0) + (k3 == 0)
        return {3: 7, 2: -2, 1: 1, 0: 0}[z]

    idx = [(k1, k2, k3) for k1 in range(4) for k2 in range(4) for k3 in range(4)]
    pos = {k: i for i, k in enumerate(idx)}
    G = [[0] * 64 for _ in range(64)]
    for i, (a1, a2, a3) in enumerate(idx):
        for j, (b1, b2, b3) in enumerate(idx):
            G[i][j] = phi((a1 - b1) % 4, (a2 - b2) % 4, (a3 - b3) % 4)
    return G, idx


def fourfold_spectrum(matching) -> list:
    """Спектр λ_a семейства: честная сумма в Z[i] + замкнутая форма.

    Характеры a ∈ (Z/4)^6 с суммами по парам ≡ 0 (mod 4) — тривиальные на
    стабилизаторе H (64 шт). χ_a(g(η)) = ζ_4^{k1·a_{j1} + k2·a_{j2} + k3·a_{j3}}.
    """
    (i1, j1), (i2, j2), (i3, j3) = matching
    pair_opts = [(0, 0), (1, 3), (2, 2), (3, 1)]
    out = []
    for o1 in pair_opts:
        for o2 in pair_opts:
            for o3 in pair_opts:
                a = [0] * 6
                a[i1], a[j1] = o1
                a[i2], a[j2] = o2
                a[i3], a[j3] = o3
                A = (a[j1], a[j2], a[j3])
                # честная сумма: λ = Σ_k ζ_4^{−(k·A)} Φ(k)
                re, im = 0, 0
                for k1 in range(4):
                    for k2 in range(4):
                        for k3 in range(4):
                            z = (k1 == 0) + (k2 == 0) + (k3 == 0)
                            phi_val = {3: 7, 2: -2, 1: 1, 0: 0}[z]
                            if not phi_val:
                                continue
                            e = (k1 * A[0] + k2 * A[1] + k3 * A[2]) % 4
                            # ζ_4^{−e}
                            w = [(1, 0), (0, 1), (-1, 0), (0, -1)][(4 - e) % 4]
                            re += phi_val * w[0]
                            im += phi_val * w[1]
                honest = (re != 0 or im != 0)
                # замкнутая форма: λ = 7 − 2σ₁ + σ₂, u_t = 4[A_t≡0] − 1
                u = [3 if A[t] % 4 == 0 else -1 for t in range(3)]
                closed = 7 - 2 * sum(u) + (u[0] * u[1] + u[0] * u[2] + u[1] * u[2])
                out.append({"a": tuple(a), "honest": honest, "closed": closed})
    return out


def fourfold_adapted_union() -> set:
    """∪ по 15 семействам реализованных примитивных (2,2)-характеров."""
    u = set()
    for matching in perfect_matchings6():
        for ch in fourfold_spectrum(matching):
            if ch["honest"] and all(x % 4 for x in ch["a"]):
                u.add(ch["a"])
    return u


# ────────────────────────────────────────────────────────────────────────────
# СБОРКА ОТЧЁТОВ
# ────────────────────────────────────────────────────────────────────────────

# классические (независимые) baseline'ы для заморозки
_SURF_FROZEN = {
    3: {"rank": 7, "meets": 10, "h11": 7},
    4: {"rank": 20, "meets": 14, "h11": 20, "snf": [1] * 18 + [8, 8]},
    5: {"h11": 45},                       # ρ(S₅) = 45 максимально (Сиода)
}


def surface_report(m: int, do_signature: bool = True, do_snf: bool = True) -> dict:
    """Полный отчёт по прямым S_m: две схемы ранга + сигнатура + ценз.

    Сертификаты:
      (i)   ранг mod 10007 (большое простое) = спектральному предсказанию;
      (ii)  для p ∈ {2,3,5,7}: ранг mod p = SNF-предсказанию #{dᵢ: p ∤ dᵢ}
            (законные падения при p | dᵢ — как в задаче 39: p=2 → 18);
      (iii) сигнатура (точный Sylvester над Q): (1, r−1) — индекс Ходжа,
            причём pos+neg = точный ранг над Q;
      (iv)  встречи/прямую = 4m−2; замороженные классические baseline'ы.
    """
    G, lines = surf_gram(m, with_h=True)
    n = len(lines)
    primes = (2, 3, 5, 7, 10007)
    ranks = {p: rank_mod_p(G, p) for p in primes}
    rank_a = max(ranks.values())
    # схема B: характерные спектры
    spec = surf_family_spectrum(m)
    adapted = surf_adapted_union(m)
    rank_b = len(adapted) + 1                     # + тривиальный (h)
    spec_closed_ok = all(
        (ch["lambda_nonzero"] == (ch["closed"] != 0))
        for chars in spec.values() for ch in chars)
    # инвариант Фурье: Σλ = m²(2−m) по каждому семейству
    fourier_ok = True
    for pi, chars in spec.items():
        if sum(ch["closed"] for ch in chars) != m * m * (2 - m):
            fourier_ok = False
    # встречи на прямую: 2(m−1) внутри семейства + 2m кросс = 4m−2
    meets = [sum(1 for j in range(n) if j != i and G[i][j] == 1) for i in range(n)]
    meets_ok = all(v == 4 * m - 2 for v in meets)
    # числа Ходжа §1/§2
    dia = hodge_diamond(m, 2)
    cs = surface_characters(m)
    h11 = dia[(1, 1)]
    ok_census = (len(cs["11"]) == h11 - 1)
    frozen = _SURF_FROZEN.get(m, {})
    ok = (rank_a == rank_b and spec_closed_ok and fourier_ok
          and meets_ok and ok_census
          and frozen.get("rank", rank_a) == rank_a
          and frozen.get("meets", 4 * m - 2) == 4 * m - 2)
    # сигнатура (индекс Ходжа: (1, r−1) для решётки с h) — точный ранг Q
    sig = None
    if do_signature and n + 1 <= 120:
        pos, neg = signature_rational(G)
        sig = (pos, neg)
        ok &= (pos == 1 and neg == rank_b - 1 and pos + neg == rank_b)
    # SNF для малых m: сверка mod-p падений (baseline m=4 = задача 39)
    snf = None
    if do_snf and m <= 5:
        G0, _ = surf_gram(m, with_h=False)
        snf = smith_normal_form(G0)
        for p in (2, 3, 5, 7):
            pred = sum(1 for d in snf if d % p)
            ok &= (ranks[p] == pred)
        if "snf" in frozen:
            ok &= (snf == frozen["snf"])
    return {
        "m": m, "lines": n, "rank_modp": rank_a, "ranks_by_p": ranks,
        "rank_spectrum": rank_b, "adapted": len(adapted), "h11": h11,
        "gap": h11 - rank_b, "meets": 4 * m - 2, "meets_ok": meets_ok,
        "sig": sig, "snf": snf, "ok": ok,
        "nonadapted_chars": [a for a in cs["11"]
                             if a not in adapted],
    }


def fourfold_report() -> dict:
    """Отчёт по плоскостям квартиковой четвёрки: спектры + натяжение."""
    matchings = perfect_matchings6()
    assert len(matchings) == 15
    fam_rank_preds = []
    spec_ok = True
    fourier_ok = True
    for matching in matchings:
        spec = fourfold_spectrum(matching)
        # замкнутая форма ↔ честная сумма
        spec_ok &= all(ch["honest"] == (ch["closed"] != 0) for ch in spec)
        # инвариант Фурье: Σ λ_a (по спектру) = |G/H|·Φ(0) = 64·7 = 448
        s = sum(ch["closed"] for ch in spec)
        fourier_ok &= (s == 448)
        # mod-p ранг 64×64 блока — третья схема
        G, _ = fourfold_family_gram(matching)
        r = max(rank_mod_p(G, p) for p in (3, 5, 10007))
        nz = sum(1 for ch in spec if ch["honest"])
        spec_ok &= (r == nz)
        fam_rank_preds.append((r, nz))
    adapted = fourfold_adapted_union()
    span = len(adapted) + 1
    dia = hodge_diamond(4, 4)
    h22 = dia[(2, 2)]
    # характерный ценз (2,2): примитивных характеров Σa = 12 в [1,3]^6
    chars22 = sum(1 for a0 in range(1, 4) for a1 in range(1, 4)
                  for a2 in range(1, 4) for a3 in range(1, 4)
                  for a4 in range(1, 4) for a5 in range(1, 4)
                  if a0 + a1 + a2 + a3 + a4 + a5 == 12)
    ok = (spec_ok and fourier_ok and len(adapted) == chars22
          and span == h22 and all(r == nz == 28 for r, nz in fam_rank_preds))
    return {"planes": 15 * 64, "families": 15, "fam_ranks": fam_rank_preds,
            "adapted": len(adapted), "chars22_prim": chars22, "span": span,
            "h22": h22, "h31": dia[(3, 1)], "chi": chern_euler(4, 4),
            "ok": ok}


_PRESETS = {
    "quick": {"m_range": (3, 5), "signature": False, "snf": True,
              "diamonds": ((7, 1), (4, 2), (4, 4))},
    "full": {"m_range": (3, 6), "signature": True, "snf": True,
             "diamonds": ((7, 1), (30, 1), (3, 2), (4, 2), (5, 2),
                          (5, 3), (3, 4), (4, 4))},
    "deep": {"m_range": (3, 8), "signature": True, "snf": True,
             "diamonds": ((7, 1), (30, 1), (3, 2), (4, 2), (5, 2), (6, 2),
                          (8, 2), (5, 3), (3, 4), (4, 4))},
}


def run_certificates(preset: str = "full", verbose: bool = True) -> tuple:
    """Прогон всех сертификатов -> (ok, detail, metrics)."""
    cfg = _PRESETS.get(preset, _PRESETS["full"])
    results = []
    metrics = {"diamonds": [], "surfaces": [], "fourfold": None, "preset": preset}

    def log(s):
        if verbose:
            print(s)

    # §1 числа Ходжа
    for (d, n) in cfg["diamonds"]:
        ok, detail, info = verify_diamond(d, n)
        results.append(ok)
        metrics["diamonds"].append({"d": d, "n": n, "ok": ok, "detail": detail})
        log(f"  [{'PASS' if ok else 'FAIL'}] {detail}")

    # §2+§3 поверхности
    lo, hi = cfg["m_range"]
    for m in range(lo, hi + 1):
        rep = surface_report(m, do_signature=cfg["signature"],
                             do_snf=cfg["snf"])
        results.append(rep["ok"])
        metrics["surfaces"].append(rep)
        gap_txt = (f"ПОЛНОЕ натяжение (ранг {rep['rank_spectrum']} = h^11)"
                   if rep["gap"] == 0 else
                   f"НЕПОЛНОЕ: {rep['rank_spectrum']} из {rep['h11']} "
                   f"(не хватает {rep['gap']} характеров — нужны не-прямые циклы)")
        sig_txt = f" · сигнатура {rep['sig']} = (1, r−1) ✓ индекс Ходжа" if rep["sig"] else ""
        snf_txt = f" · SNF {rep['snf']}" if rep["snf"] else ""
        log(f"  [{'PASS' if rep['ok'] else 'FAIL'}] S_{m}: {rep['lines']} прямых · "
            f"ранг mod-p {rep['rank_modp']} = спектр {rep['rank_spectrum']} · "
            f"{gap_txt} · встреч/прямую {rep['meets']}{sig_txt}{snf_txt}")

    # §4 четвёрка
    ff = fourfold_report()
    results.append(ff["ok"])
    metrics["fourfold"] = ff
    log(f"  [{'PASS' if ff['ok'] else 'FAIL'}] X^4_4: {ff['planes']} плоскостей · "
        f"15 семейств × ранг 28 · адаптировано (2,2)-характеров "
        f"{ff['adapted']} = ценз {ff['chars22_prim']} · натяжение "
        f"{ff['span']} = h^(2,2) {ff['h22']} (h^31 = {ff['h31']}, χ = {ff['chi']})")
    if ff["ok"]:
        log("  >>> ГИПОТЕЗА ХОДЖА (коразмерность 2, X^4_4): ВСЕ рациональные (2,2)-классы —")
        log("      рациональные комбинации классов 960 плоскостей. ВЕРИФИЦИРОВАНО.")

    ok = all(results)
    n_surf = len(metrics["surfaces"])
    full_spans = sum(1 for r in metrics["surfaces"] if r["gap"] == 0)
    detail = (f"HODGE-PLANES [{preset}]: алмазы {len(metrics['diamonds'])} шт · "
              f"поверхности S_{lo}..S_{hi}: {n_surf} прогонов, полное натяжение "
              f"прямых при m ≤ {max(r['m'] for r in metrics['surfaces'] if r['gap'] == 0)}, "
              f"четвёрка: {ff['span']} = h^(2,2) = {ff['h22']} — HC(2,2) верифицирована"
              if ok else
              f"HODGE-PLANES [{preset}]: FAIL — см. детали выше")
    return ok, detail, metrics


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    preset = "quick" if "--quick" in argv else "full"
    print("═" * 78)
    print(" HODGE PLANES — слой декомпозиции Ходжа (hodge-laboratory, session7)")
    print("═" * 78)
    ok, detail, _ = run_certificates(preset)
    print("─" * 78)
    print(f" ИТОГ: {'ALL PASS' if ok else 'FAIL'} · {detail}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

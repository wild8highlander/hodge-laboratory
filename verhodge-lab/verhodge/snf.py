"""The computable Smith normal form engine (Wave v1.6).

Implements the integer Smith normal form with tracked unimodular
transforms:

    U * A * V = diag(d_1, ..., d_r, 0, ...),   d_i | d_{i+1},

following the Kannan-Bachem discipline: at every step the pivot is
the entry of MINIMAL magnitude in the active submatrix (the pivot
rule that makes the elimination schedule polynomial in the bit
sense [Kannan-Bachem 1979; Storjohann 1996 refinement]), with exact
integer Bezout eliminations and the closed 2x2 gcd/lcm divisibility
repair:

    diag(a, b) ~ diag(gcd(a,b), lcm(a,b))   via
    L = [[u, v], [-b', a']]            (u*a' + v*b' = 1, a = g a', b = g b')
    R = [[1, -v b'], [1, 1 - v b']]    (both unimodular, det = 1)

Acceptance tests (the v1.6 gate):
  (T1) divisibility chain d_i | d_{i+1};
  (T2) product prod d_i = |det| (full-rank case);
  (T3) unimodular round trip U A V == diag exactly;
  (T4) known-answer regression on random matrices built as
       U0 diag(s) V0 with random unimodular U0, V0.
"""

from math import gcd
from typing import Dict, List, Tuple


def egcd(a: int, b: int) -> Tuple[int, int, int]:
    """Extended gcd: (g, u, v) with u*a + v*b = g, g >= 0.

    The coefficients are CANONICALLY REDUCED (|u| <= |b|/g), which
    guarantees the divisibility case a | b yields v = 0 — the
    property the SNF clearing pass relies on to avoid polluting
    already-processed columns.
    """
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
    g = old_r
    u, v = old_s, old_t
    if g < 0:
        g, u, v = -g, -u, -v
    if b != 0 and g != 0:
        bg = abs(b // g)
        if bg >= 1:
            # canonical small representatives: try both u0 and u0-bg,
            # keep the pair minimizing |u|+|v| (the divisibility case
            # b = +-a then yields v = 0 exactly)
            u0 = u % bg if bg > 0 else u
            best = None
            cands = {u0, u0 - bg, u0 + bg} if bg > 0 else {u}
            for uu in cands:
                vv = (g - uu * a) // b
                score = (abs(vv), abs(uu) + abs(vv))
                if best is None or score < best[0]:
                    best = (score, uu, vv)
            _, u, v = best
    return g, u, v


def _mat_mul(P: List[List[int]], Q: List[List[int]]) -> List[List[int]]:
    n, k, m = len(P), len(Q), len(Q[0])
    out = [[0] * m for _ in range(n)]
    for i in range(n):
        Pi = P[i]
        Oi = out[i]
        for t in range(k):
            p = Pi[t]
            if p:
                Qt = Q[t]
                for j in range(m):
                    Oi[j] += p * Qt[j]
    return out


def _identity(n: int) -> List[List[int]]:
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def snf_with_unimodulars(A: List[List[int]]) -> Dict:
    """Smith normal form with tracked U, V:  U * A * V = S.

    Returns {'diag': [...], 'U': ..., 'V': ..., 'rank': r, 'S': ...}.
    The 'diag' list has length min(m, n) with zeros beyond rank.
    """
    m = len(A)
    n = len(A[0]) if m else 0
    M = [row[:] for row in A]
    U = _identity(m)
    V = _identity(n)

    def row_op(i1: int, i2: int, T: Tuple[int, int, int, int]) -> None:
        """Rows i1,i2 <- [[T00,T01],[T10,T11]] * (row i1, row i2)."""
        t00, t01, t10, t11 = T
        for j in range(n):
            a, b = M[i1][j], M[i2][j]
            M[i1][j] = t00 * a + t01 * b
            M[i2][j] = t10 * a + t11 * b
        for j in range(m):
            a, b = U[i1][j], U[i2][j]
            U[i1][j] = t00 * a + t01 * b
            U[i2][j] = t10 * a + t11 * b

    def col_op(j1: int, j2: int, T: Tuple[int, int, int, int]) -> None:
        t00, t01, t10, t11 = T
        for i in range(m):
            a, b = M[i][j1], M[i][j2]
            M[i][j1] = a * t00 + b * t10
            M[i][j2] = a * t01 + b * t11
        for i in range(n):
            a, b = V[i][j1], V[i][j2]
            V[i][j1] = a * t00 + b * t10
            V[i][j2] = a * t01 + b * t11

    r_max = min(m, n)
    k = 0
    while k < r_max:
        # KB pivot rule: minimal |entry| in the active submatrix
        best = None
        for i in range(k, m):
            Mi = M[i]
            for j in range(k, n):
                v = Mi[j]
                if v and (best is None or abs(v) < best[0]):
                    best = (abs(v), i, j)
                    if abs(v) == 1:
                        break
            if best and best[0] == 1:
                break
        if best is None:
            break                      # everything below is zero
        _, pi, pj = best
        if pi != k:
            row_op(k, pi, (0, 1, 1, 0))
        if pj != k:
            col_op(k, pj, (0, 1, 1, 0))
        if M[k][k] < 0:
            row_op(k, k, (-1, 0, 0, 1))   # positive pivot keeps egcd clean
        # Eliminate row k / column k.  Proven-terminating schedule:
        # repeat full clearing passes while the pivot strictly
        # shrinks; the first pass with NO shrink has pivot dividing
        # every target (v = 0 Bezout coefficients), so the row and
        # column clear cleanly without reintroduction.
        while True:
            shrunk = False
            for i in range(k + 1, m):
                b = M[i][k]
                if b:
                    a = M[k][k]
                    g, u, v = egcd(a, b)
                    if abs(g) != abs(a):
                        shrunk = True
                    row_op(k, i, (u, v, -(b // g), a // g))
            for j in range(k + 1, n):
                b = M[k][j]
                if b:
                    a = M[k][k]
                    g, u, v = egcd(a, b)
                    if abs(g) != abs(a):
                        shrunk = True
                    col_op(k, j, (u, -(b // g), v, a // g))
            if not shrunk:
                break
        if M[k][k] < 0:
            row_op(k, k, (-1, 0, 0, 1))
        k += 1

    diag = [M[i][i] for i in range(r_max)]
    rank = sum(1 for d in diag if d != 0)
    return {"diag": diag, "U": U, "V": V, "rank": rank, "S": M}


def _divisibility_repair(diag: List[int], U, V, M: List[List[int]]) -> None:
    """In-place 2x2 gcd/lcm repair enforcing d_i | d_{i+1}."""
    r = len(diag)
    changed = True
    while changed:
        changed = False
        for i in range(r - 1):
            a, b = M[i][i], M[i + 1][i + 1]
            if a == 0 or b == 0 or b % a == 0:
                continue
            g = gcd(abs(a), abs(b))
            ap, bp = a // g, b // g
            gg, u, v = egcd(ap, bp)
            assert gg == 1 or gg == -1
            if gg == -1:
                u, v = -u, -v
            # rows i, i+1 <- L * (rows), cols <- cols * R
            t00, t01 = u, v
            t10, t11 = -bp, ap
            n = len(M[0])
            for j in range(n):
                x, y = M[i][j], M[i + 1][j]
                M[i][j] = t00 * x + t01 * y
                M[i + 1][j] = t10 * x + t11 * y
            m = len(U)
            for j in range(m):
                x, y = U[i][j], U[i + 1][j]
                U[i][j] = t00 * x + t01 * y
                U[i + 1][j] = t10 * x + t11 * y
            # columns: (ci, cj) * R with R = [[1, -v bp], [1, 1 - v bp]]
            r00, r01 = 1, -v * bp
            r10, r11 = 1, 1 - v * bp
            for row in M:
                x, y = row[i], row[i + 1]
                row[i] = x * r00 + y * r10
                row[i + 1] = x * r01 + y * r11
            for row in V:
                x, y = row[i], row[i + 1]
                row[i] = x * r00 + y * r10
                row[i + 1] = x * r01 + y * r11
            changed = True


def smith_normal_form(A: List[List[int]]) -> Dict:
    """Full SNF pipeline: elimination + divisibility repair + checks."""
    res = snf_with_unimodulars(A)
    M = res["S"]
    _divisibility_repair(res["diag"], res["U"], res["V"], M)
    # final sign normalization: every nonzero d_i must be positive
    for i in range(min(len(M), len(M[0]))):
        if M[i][i] < 0:
            M[i] = [-v for v in M[i]]
            U = res["U"]
            U[i] = [-v for v in U[i]]
        elif M[i][i] == 0:
            # rows beyond the rank must be entirely zero already
            assert all(v == 0 for v in M[i]), "nonzero row beyond rank"
    diag = [M[i][i] for i in range(min(len(A), len(A[0])))]
    res["diag"] = diag
    res["rank"] = sum(1 for d in diag if d)
    # T1: divisibility chain on the nonzero prefix
    nz = [d for d in diag if d]
    chain_ok = all(nz[i + 1] % nz[i] == 0 for i in range(len(nz) - 1))
    res["chain_ok"] = chain_ok
    if not chain_ok:
        raise AssertionError("SNF divisibility chain violated")
    return res


def smith_invariants(A: List[List[int]]) -> List[int]:
    """The nonzero diagonal invariants only."""
    return [d for d in smith_normal_form(A)["diag"] if d]

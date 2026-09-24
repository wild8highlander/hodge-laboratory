# ══════════════════════════════════════════════════════════════════════
#  HODGE LABORATORY — POLYGLOT CORE · JULIA (BigFloat 256 bit + BigInt)
#  Ядро лаборатории на Julia: точная целочисленная машина (Rational{BigInt}),
#  tanh–sinh квадратуры в BigFloat (~77 значащих цифр по умолчанию).
#  The laboratory core in Julia: exact integer machinery (Rational{BigInt}),
#  tanh–sinh quadratures in BigFloat (~77 significant digits by default).
#
#  Запуск / Run:  julia verify_core.jl
#
#  Автор программы / Program author:
#    Исаев Исхак Хамзатович / Isaev Iskhak Khamzatovich
#  Репозиторий / Repository: wild8highlander/hodge-laboratory
#  Лицензия / License: индивидуальная эксклюзивная / individual exclusive
# ══════════════════════════════════════════════════════════════════════

using LinearAlgebra  # noqa (symmetry intent)
using SpecialFunctions  # gamma(x::BigFloat) — один раз: julia -e 'using Pkg; Pkg.add("SpecialFunctions")'

const CHECKS = Ref{Tuple{Int,Int}}((0, 0))
snip(s::AbstractString, n::Int) = length(s) <= n ? String(s) : String(s[1:n])
function check(name::String, ok::Bool; detail::String = "")
    t, p = CHECKS[]
    CHECKS[] = (t + 1, p + (ok ? 1 : 0))
    mark = ok ? "PASS" : "FAIL"
    if isempty(detail)
        println("  [$mark] $name")
    else
        println("  [$mark] $name  ·  $detail")
    end
end

# ═══ 1–2. census ═══════════════════════════════════════════════════════
function census(N::Int)
    h = Dict{Int,Int}()
    for a in 1:(N-1), b in 1:(N-a-1)
        d = N ÷ gcd(gcd(N, a), b)
        h[d] = get(h, d, 0) + 1
    end
    genus = (N - 1) * (N - 2) ÷ 2
    return h, genus
end

function mobius(m::Int)
    m == 1 && return 1
    result, x = 1, m
    q = 2
    while q * q <= x
        if x % q == 0
            x ÷= q
            x % q == 0 && return 0
            result = -result
        end
        q += 1
    end
    x > 1 && (result = -result)
    return result
end

function censusMobius(N::Int)
    c(k) = k >= 3 ? (k - 1) * (k - 2) ÷ 2 : 0
    out = Dict{Int,Int}()
    for d in 2:N
        N % d == 0 || continue
        s = sum(mobius(m) * c(d ÷ m) for m in 1:d if d % m == 0; init = 0)
        s != 0 && (out[d] = s)
    end
    return out
end

# ═══ 3–4. cert E + binary flow ═════════════════════════════════════════
lcm64(a::Int, b::Int) = (a == 0 || b == 0) ? 0 : abs(a ÷ gcd(a, b) * b)
tstar(W, H, a, b) = lcm64(W ÷ gcd(a, W), H ÷ gcd(b, H))

function binaryFlow()
    W, H, a, b = 48, 48, 1, 1
    t = tstar(W, H, a, b)
    x = y = dx = dy = 0
    visited = Set{Tuple{Int,Int}}()
    for _ in 1:t
        push!(visited, (x, y))
        x = mod(x + a, W); y = mod(y + b, H)
        dx = mod(dx + a, W); dy = mod(dy + b, H)
    end
    return t, length(visited), dx == 0 && dy == 0
end

# ═══ 5. Arf enumeration ════════════════════════════════════════════════
function arfEnum(g::Int)
    n = 2g
    size = 1 << n
    half = size >> 1
    shift = 1 << (g - 1)
    pairs = [(2i, 2i + 1) for i in 0:(g-1)]
    even = odd = 0
    for basis in 0:(size-1)
        zeros = 0
        for v in 0:(size-1)
            qv = 0
            for i in 0:(n-1)
                if (v >> i) & 1 == 1
                    qv ⊻= (basis >> i) & 1
                end
            end
            for (i, j) in pairs
                if ((v >> i) & 1) & ((v >> j) & 1) == 1
                    qv ⊻= 1
                end
            end
            qv == 0 && (zeros += 1)
        end
        if zeros == half + shift
            even += 1
        else
            odd += 1
        end
    end
    return size, even, odd
end

# ═══ 6. K3: exact rank · SNF · signature (Rational{BigInt}) ════════════
k3Lines() = [(f, a, b) for f in 1:3 for a in 0:3 for b in 0:3]

function k3Inter(l1, l2)
    l1 == l2 && return -2
    f1, a1, b1 = l1
    f2, a2, b2 = l2
    f1 == f2 && return (a1 == a2) != (b1 == b2) ? 1 : 0
    lo, hi = minmax(f1, f2)
    if (lo, hi) == (1, 2)
        return mod(a1 + b2 - a2 - b1, 4) == 0 ? 1 : 0
    elseif (lo, hi) == (1, 3)
        t = f1 == 1 ? (a2 - a1 - b1 - b2 - 1) : (a1 - a2 - b2 - b1 - 1)
        return mod(t, 4) == 0 ? 1 : 0
    else
        return mod(a1 + b1 - a2 - b2, 4) == 0 ? 1 : 0
    end
end

function k3Gram()
    ls = k3Lines()
    n = length(ls)
    G = zeros(Int, n + 1, n + 1)
    for i in 1:n, j in i:n
        G[i, j] = G[j, i] = k3Inter(ls[i], ls[j])
    end
    for i in 1:n
        G[i, n+1] = G[n+1, i] = 1
    end
    G[n+1, n+1] = 4
    return G, ls
end

function rankFractions(Mint::Matrix{Int})
    n = size(Mint, 1)
    M = Matrix{Rational{BigInt}}(Mint)
    r = 1                                # 1-based search start
    pivots = 0
    for c in 1:n
        r >= n && break
        piv = findfirst(i -> M[i, c] != 0, r:n)   # returns POSITION in the range
        piv === nothing && continue
        piv += r - 1                              # convert to the actual row index
        M[r, :], M[piv, :] = M[piv, :], M[r, :]
        pv = M[r, c]
        for i in (r+1):n
            M[i, c] == 0 && continue
            f = M[i, c] / pv
            for j in c:n
                M[i, j] -= f * M[r, j]
            end
        end
        r += 1
        pivots += 1
    end
    return pivots
end

function snf(mat::Matrix{Int})
    a = BigInt.(mat)
    rows, cols = size(a)
    res = BigInt[]
    for t in 1:min(rows, cols)
        while true
            p = nothing; pi = pj = 0
            for i in t:rows, j in t:cols
                v = abs(a[i, j])
                if v != 0 && (p === nothing || v < p)
                    p, pi, pj = v, i, j
                end
            end
            p === nothing && return res
            if pi != t
                a[t, :], a[pi, :] = a[pi, :], a[t, :]
            end
            if pj != t
                a[:, t], a[:, pj] = a[:, pj], a[:, t]
            end
            piv = a[t, t]
            for i in (t+1):rows
                q = a[i, t] ÷ piv
                q != 0 && (a[i, t:cols] .-= q .* a[t, t:cols])
            end
            for j in (t+1):cols
                q = a[t, j] ÷ piv
                q != 0 && (a[:, j] .-= q .* a[:, t])
            end
            divisible = all(a[i, j] % piv == 0 for i in (t+1):rows, j in (t+1):cols)
            divisible && break
        end
        push!(res, abs(a[t, t]))
    end
    return res
end

function intEchRows(Mint::Matrix{Int})
    n = size(Mint, 1)
    M = Matrix{Rational{BigInt}}(Mint)
    rowsF = Vector{Vector{Rational{BigInt}}}()
    r = 1                                # 1-based search start
    for c in 1:n
        r >= n && break
        piv = findfirst(i -> M[i, c] != 0, r:n)   # returns POSITION in the range
        piv === nothing && continue
        piv += r - 1                              # convert to the actual row index
        M[r, :], M[piv, :] = M[piv, :], M[r, :]
        pv = M[r, c]
        M[r, :] ./= pv
        for i in 1:n
            i != r && M[i, c] != 0 || continue
            f = M[i, c]
            for j in c:n
                M[i, j] -= f * M[r, j]
            end
        end
        push!(rowsF, M[r, :])
        r += 1
    end
    out = Vector{Vector{BigInt}}()
    for row in rowsF
        L = BigInt(1)
        for x in row
            L = L ÷ gcd(L, denominator(x)) * denominator(x)
        end
        ints = [BigInt(numerator(x) * L ÷ denominator(x)) for x in row]
        g = reduce(gcd, ints; init = BigInt(0))
        g > 1 && (ints = [v ÷ g for v in ints])
        push!(out, ints)
    end
    return out
end

function exactSignature(G::Matrix{Int}, ech)
    n, k = size(G, 1), length(ech)
    S = zeros(BigInt, k, k)
    for i in 1:k
        T = zeros(BigInt, n)
        for t in 1:n
            ech[i][t] == 0 && continue
            cit = ech[i][t]
            for u in 1:n
                T[u] += cit * G[t, u]
            end
        end
        for j in 1:k
            s = sum(T[u] * ech[j][u] for u in 1:n; init = BigInt(0))
            S[i, j] = S[j, i] = s
        end
    end
    A = Matrix{Rational{BigInt}}(S)
    diag = Vector{Rational{BigInt}}()
    pos = neg = 0
    for i in 1:k
        s = Rational{BigInt}(0)
        for t in 1:(i-1)
            s += A[t, i] * A[t, i] * diag[t]
        end
        d = A[i, i] - s
        d == 0 && return nothing
        d > 0 ? pos += 1 : neg += 1
        push!(diag, d)
        for j in (i+1):k
            s2 = Rational{BigInt}(0)
            for t in 1:(i-1)
                s2 += A[t, i] * A[t, j] * diag[t]
            end
            v = (Rational{BigInt}(S[i, j]) - s2) / diag[i]
            A[i, j] = A[j, i] = v
        end
    end
    return pos, neg
end

function k3Invariants()
    G, ls = k3Gram()
    n = size(G, 1)
    rank = rankFractions(G)
    factors = snf(G)
    det = prod(factors; init = BigInt(1))
    sig = exactSignature(G, intEchRows(G))
    idx = Dict(l => i for (i, l) in enumerate(ls))
    famOk = true
    for a in 0:3, j in 1:n
        s = sum(G[idx[(1, a, b)], j] for b in 0:3; init = 0)
        if s != G[n, j]
            famOk = false
            break
        end
    end
    return rank, det, factors, sig, famOk, length(ls)
end

# ═══ 7. Klein exact layer ══════════════════════════════════════════════
function kleinExact()
    j = -(105^3) ÷ 343
    c1 = j == -3375 && (-15)^3 == -3375
    c2 = (-343) * j == 105^3 == 1157625
    expand = zeros(Int, 4)
    for (i, ci) in [(1, 1), (2, -7)], (jj, cj) in [(1, 1), (2, 7), (3, 14)]
        expand[i+jj-1] += ci * cj
    end
    c3 = expand == [1, 0, -35, -98]
    c4 = 7^2 - 4 * 14 == -7
    return c1 && c2 && c3 && c4
end

# ═══ 8–9. cyclotomic exact layer ═══════════════════════════════════════
function polyMul(a, b)
    res = zeros(Int, length(a) + length(b) - 1)
    for (i, ai) in enumerate(a), (j, bj) in enumerate(b)
        ai != 0 && (res[i+j-1] += ai * bj)
    end
    return res
end

function polyModPhi(a, phi)
    a = copy(a)
    dphi = length(phi) - 1
    for i in 1:(length(a)-dphi)
        a[i] == 0 && continue
        for j in 1:dphi
            a[i+j] -= a[i] * phi[j+1]
        end
        a[i] = 0
    end
    while length(a) > 1 && a[1] == 0
        popfirst!(a)
    end
    return a
end

function cycLayer(n::Int, units, vieta, poly)
    phi = ones(Int, n)            # Φ₇ = x⁶+…+1 (highest-first)
    if n == 9
        phi = [1, 0, 0, 1, 0, 0, 1]   # Φ₉ = x⁶+x³+1
    end
    els = []
    for k in units
        p = zeros(Int, n + 1)
        p[k+1] += 1
        p[n-k+1] += 1
        push!(els, polyModPhi(p, phi))
    end
    padd(p, q) = polyModPhi(begin
            out = zeros(Int, max(length(p), length(q)))
            for (i, x) in enumerate(p)
                out[end-length(p)+i] += x
            end
            for (i, x) in enumerate(q)
                out[end-length(q)+i] += x
            end
            out
        end, phi)
    pmul(p, q) = polyModPhi(polyMul(p, q), phi)
    norm(p) = (while length(p) > 1 && p[1] == 0
        popfirst!(p)
    end; p)
    e1 = norm(padd(els[1], padd(els[2], els[3])))
    e2 = norm(padd(padd(pmul(els[1], els[2]), pmul(els[1], els[3])), pmul(els[2], els[3])))
    e3 = norm(pmul(els[1], pmul(els[2], els[3])))
    vietaOk = length(e1) == 1 && length(e2) == 1 && length(e3) == 1 &&
              [e1[1], e2[1], e3[1]] == vieta
    ev0 = poly[end] & 1
    ev1 = sum(poly) & 1
    return vietaOk && ev0 == 1 && ev1 == 1
end

# ═══ 10–11. BCH radical tower Z[√5][β] ═════════════════════════════════
z5mul(p, q) = (p[1] * q[1] + 5 * p[2] * q[2], p[1] * q[2] + p[2] * q[1])
z5add(p, q) = (p[1] + q[1], p[2] + q[2])

function twMul(u, v, D)
    return (z5add(z5mul(u[1], v[1]), z5mul(z5mul(u[2], v[2]), D)),
            z5add(z5mul(u[1], v[2]), z5mul(u[2], v[1])))
end

function bchLayer(D, X, den, poly)
    deg = length(poly) - 1
    acc = ((0, 0), (0, 0))
    cur = ((1, 0), (0, 0))            # X⁰ = 1
    for j in 0:deg
        if j > 0
            cur = twMul(cur, X, D)
        end
        c = poly[deg - j + 1] * den^(deg - j)
        c == 0 && continue
        pw = (BigInt.(cur[1]), BigInt.(cur[2]))
        acc = (z5add(acc[1], z5mul(pw[1], (c, 0))),
               z5add(acc[2], z5mul(pw[2], (c, 0))))
    end
    residOk = acc == ((BigInt(0), BigInt(0)), (BigInt(0), BigInt(0)))
    ev0 = poly[end] & 1
    ev1 = sum(poly) & 1
    gf2 = false
    if ev0 != 0 && ev1 != 0
        rem = [v & 1 for v in poly]
        for dd in length(poly):-1:3
            if rem[dd] == 1
                rem[dd-2] ⊻= 1
                rem[dd-1] ⊻= 1
                rem[dd] = 0
            end
        end
        gf2 = !(rem[1] == 0 && rem[2] == 0)
    end
    return residOk, gf2
end

# ═══ 12–15. high-precision float checks (BigFloat ~77 digits) ══════════
const PI_B = BigFloat(pi)   # correctly rounded to current precision

function torusDelta()
    delta = PI_B / 4
    lam = 4 * PI_B * PI_B
    return lam + delta * delta / 2 - delta^5
end

function tanhSinhNodes(K::Int, h::BigFloat)
    nodes = Tuple{BigFloat,BigFloat}[]
    for k in -K:K
        t = BigFloat(k) * h
        sh = sinh(t)
        z = PI_B / 2 * sh
        u = (1 + tanh(z)) / 2
        w = (PI_B / 4) * cosh(t) / cosh(z)^2 * h
        0 < u < 1 && push!(nodes, (u, w))
    end
    return nodes
end

function kleinOmega(K::Int = 220, h::BigFloat = BigFloat("0.03"))
    nodes = tanhSinhNodes(K, h)
    total = BigFloat(0)
    for (u, w) in nodes
        one = 1 - u
        x7 = u / one
        x = x7 + 7
        quad = x * x + 7 * x + 14
        total += w * 2 / (one * one * sqrt(x7 * quad))
    end
    return total
end

function v6Reflection()
    worst = BigFloat(0)
    N = 7
    for k in 1:(N-1)
        lhs = gamma(BigFloat(k) / N) * gamma(BigFloat(N - k) / N)
        rhs = PI_B / sin(PI_B * k / N)
        worst = max(worst, abs(lhs - rhs) / abs(rhs))
    end
    return worst
end

function periodQuadrature(N::Int, a::Int, b::Int; K::Int = 220, h = BigFloat("0.03"))
    A, B = BigFloat(a) / N, BigFloat(b) / N
    nodes = tanhSinhNodes(K, h)
    i1 = i2 = BigFloat(0)
    for (u, w) in nodes
        i1 += N * w * 2^(-A) * u^(a - 1) * (1 - u^N / 2)^(B - 1)
        i2 += N * w * 2^(-B) * u^(b - 1) * (1 - u^N / 2)^(A - 1)
    end
    closed = gamma(BigFloat(a) / N) * gamma(BigFloat(b) / N) / gamma(BigFloat(a + b) / N)
    return abs((i1 + i2) - closed) / abs(closed)
end

# ═══════════════════════════════════════════════════════════════════════
function main()
    println("════════════════════════════════════════════════════════════")
    println(" HODGE LABORATORY · POLYGLOT CORE · JULIA (BigFloat + BigInt)")
    println(" Ядро лаборатории · целочисленная верификация / integer verification")
    println("════════════════════════════════════════════════════════════")

    println("\n[1-2] V1 · Census of conductors / Ценз проводников")
    expect = Dict(7 => 15, 9 => 28, 15 => 91, 30 => 406)
    ok1 = ok2 = true
    h30 = nothing
    for N in (7, 9, 15, 30)
        h, genus = census(N)
        hm = censusMobius(N)
        (sum(values(h)) == genus == expect[N]) || (ok1 = false)
        h == hm || (ok2 = false)
        N == 30 && (h30 = h)
    end
    check("Σh_d = g for N=7,9,15,30 · Σh_d = g", ok1; detail = "15/28/91/406 · N=30: $(sort(collect(h30)))")
    check("Möbius scheme agrees · схема Мёбиуса совпадает", ok2)

    println("\n[3] Certificate E · t* = lcm(W/gcd(a,W), H/gcd(b,H))")
    certE = [(48, 48, 1, 1, 48), (96, 96, 1, 1, 96), (24, 36, 3, 5, 72),
             (7, 14, 1, 1, 14), (12, 12, 4, 6, 6), (384, 384, 1, 1, 384)]
    ok3 = all(tstar(W, H, a, b) == e for (W, H, a, b, e) in certE)
    check("6 cert-E cases · 6 случаев cert E", ok3; detail = "t*(24,36;3,5)=72 …")

    println("\n[4] Binary flow 48×48 / Двоичный поток")
    t, vis, closed = binaryFlow()
    check("t*=48 · 48 cells · closure · замыкание", t == 48 && vis == 48 && closed;
          detail = "t*=$t, visited=$vis, closed=$closed · 48+212+432+114=806")

    println("\n[5] Arf enumeration / Перечисление Арфа")
    ok5 = true
    det5 = ""
    for g in 1:3
        size, even, odd = arfEnum(g)
        expEven = (1 << (g - 1)) * ((1 << g) + 1)
        expOdd = (1 << (g - 1)) * ((1 << g) - 1)
        (size == (1 << 2g) && even == expEven && odd == expOdd) || (ok5 = false)
        det5 *= "g=$g: $even/$odd "
    end
    check("even/odd forms g=1..3 · чётные/нечётные формы", ok5; detail = det5 * "(g=3: 36/28)")

    println("\n[6] K3 stand · exact integer machinery / точная машина")
    rank, det, factors, sig, famOk, nlines = k3Invariants()
    check("48 lines on the Fermat quartic · прямых", nlines == 48)
    check("rank_Q = 20 = ρ (Shioda · Шиода)", rank == 20; detail = "rank=$rank")
    check("signature (1,19) — Hodge index · сигнатура", sig == (1, 19); detail = "sig=$(sig)")
    check("SNF → det = 64 = 8²", det == 64 && factors[end-1:end] == [8, 8];
          detail = "factors=[1×18, 8, 8], det=$det")
    check("family relation Σ_b L1(a,b) ~ h · семейное соотношение", famOk)

    println("\n[7] Klein stand / Слой Клейна")
    check("j = −3375 = −15³ · Δ·j = 105³ · disc = −7", kleinExact();
          detail = "(v−7)(v²+7v+14) = v³−35v−98")

    println("\n[8-9] Cyclotomic layer N=7/9 · Z[ζ]/Φₙ (exact integer arithmetic)")
    ok7 = cycLayer(7, [1, 2, 3], [-1, -2, 1], [1, 1, -2, -1])
    check("N=7: Vieta s=(−1,−2,1) computed in Z[ζ]/Φ₇ + GF(2)", ok7;
          detail = "e1,e2,e3 exact integers · cubic irreducible over GF(2)")
    ok9 = cycLayer(9, [1, 2, 4], [0, -3, -1], [1, 0, -3, 1])
    check("N=9: Vieta s=(0,−3,−1) computed in Z[ζ]/Φ₉ + GF(2)", ok9;
          detail = "e1,e2,e3 exact integers · cubic irreducible over GF(2)")

    println("\n[10-11] BCH radical tower Z[√5][β] · Радикальная башня")
    r15, g15 = bchLayer((30, -6), ((1, 1), (1, 0)), 4, [1, -1, -4, 4, 1])
    check("n=15: 4⁴P(x) ≡ 0 in Z[√5][β] + GF(2)", r15 && g15;
          detail = "b_Ch(15) = (7 − √5 − √(30−6√5))/8")
    r30, g30 = bchLayer((30, 6), ((-1, 1), (1, 0)), 4, [1, 1, -4, -4, 1])
    check("n=30: 4⁴P(x) ≡ 0 in Z[√5][β] + GF(2)", r30 && g30;
          detail = "b_Ch(30) = (9 − √5 − √(30+6√5))/8")

    println("\n[12] Torus Δ_Ch (BigFloat ~77 digits)")
    delta = torusDelta()
    deltaRef = BigFloat("39.48799539346835051297464603266144167978")
    dev = abs(delta - deltaRef) / deltaRef
    check("Δ_Ch = 4π² + δ²/2 − δ⁵ (40-digit reference)", dev < BigFloat(10)^-37;
          detail = "Δ_Ch = $(snip(string(delta), 42))")

    println("\n[13] Klein Ω quadrature (BigFloat tanh–sinh)")
    omega = kleinOmega()
    omegaRef = BigFloat("1.93331170561681154673308")
    eom = abs(omega - omegaRef) / omegaRef
    check("Ω = 2∫₇^∞ dx/√(x³−35x−98)", eom < BigFloat(10)^-20;
          detail = "Ω = $(snip(string(omega), 26)), rel = $(snip(string(eom), 12)) (ref is 23-digit)")

    println("\n[14] V6 Γ-reflection (BigFloat)")
    e6 = v6Reflection()
    check("Γ(k/N)Γ((N−k)/N) = π/sin(πk/N), N=7", e6 < BigFloat(10)^-40;
          detail = "max rel = $(snip(string(e6), 9))")

    println("\n[15] Period closed vs tanh–sinh (BigFloat)")
    e15 = periodQuadrature(15, 2, 3)
    e9 = periodQuadrature(9, 1, 2)
    check("P_closed = P_numeric (N=15; N=9)", e15 < BigFloat(10)^-20 && e9 < BigFloat(10)^-20;
          detail = "rel = $(snip(string(e15), 9)) / $(snip(string(e9), 9))")

    total, passed = CHECKS[]
    println("\n════════════════════════════════════════════════════════════")
    println(" ИТОГ / RESULT: $passed/$total")
    if passed == total
        println(" ✔ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ · ALL CHECKS PASSED")
    else
        println(" ✘ ЕСТЬ ПРОВАЛЫ · THERE ARE FAILURES")
    end
    println(" Программа: Исаев Исхак Хамзатович / Program: Isaev Iskhak Khamzatovich")
    println("════════════════════════════════════════════════════════════")
    return passed == total

end

main() || exit(1)
exit(0)

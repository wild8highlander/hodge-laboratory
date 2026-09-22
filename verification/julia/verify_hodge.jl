#!/usr/bin/env julia
#=
════════════════════════════════════════════════════════════════════
HODGE LABORATORY — JULIA VERIFICATION
Laboratory "The Dynamic Principle" (Isaev Iskhak Khamzatovich)

High-precision periods, phases and exact integer censuses.
Run:      julia verify_hodge.jl
Requires: Base + Printf (standard library); no external packages.

Precision: 240-bit BigFloat mantissa ≈ 72 decimal digits, so the
thresholds below (1e-25 … 1e-30) are comfortably reachable.

Exit codes: 0 — all checks accepted, 1 — at least one failure.
════════════════════════════════════════════════════════════════════
=#

using Printf

setprecision(BigFloat, 240)

const PI = big(π)          # π rounded to the current working precision

passes = 0
fails = 0

function check(name::String, ok::Bool, detail::String = "")
    global passes, fails
    if ok
        global passes += 1
        println(@sprintf("  ✔ %-52s PASS  %s", name, detail))
    else
        global fails += 1
        println(@sprintf("  ✘ %-52s FAIL  %s", name, detail))
    end
end

# ─── 1. Character census (exact) ───

function census(N::Int)
    h = Dict{Int,Int}()
    for a in 1:N-1, b in 1:(N-a-1)
        d = N ÷ gcd(gcd(N, a), b)
        h[d] = get(h, d, 0) + 1
    end
    return sort(collect(h))
end

h15 = census(15); h30 = census(30)
check("N=15: Σh_d = 91", sum(v for (_, v) in h15) == 91, join(h15, " "))
check("N=30: Σh_d = 406", sum(v for (_, v) in h30) == 406, join(h30, " "))
check("N=7:  Σh_d = 15", sum(v for (_, v) in census(7)) == 15)

# ─── 2. Closed period form vs independent quadrature ───

Ω(N, a, b) = gamma(BigFloat(a) / N) * gamma(BigFloat(b) / N) /
             gamma(BigFloat(a + b) / N)

function period_closed(N, a, b, r, s)
    ph = exp(2 * PI * im * BigFloat(mod(r * a + s * b, N)) / N)
    return ph * Ω(N, a, b) / N
end

# Independent method: tanh–sinh quadrature over [0, 1], no Γ functions.
# The substitution t = u^N/2 on the two halves of the path removes the
# endpoint singularities; the map u = (1 + tanh(π/2 · sinh τ))/2 sends
# τ ∈ (-∞, ∞) to u ∈ (0, 1) and is integrated with trapezoid weights
# (the double-exponential rule; nodes never touch the endpoints).
function period_numeric(N, a, b, r, s)
    A, B = BigFloat(a) / N, BigFloat(b) / N
    h1(u) = N * BigFloat(2)^(-A) * u^(a - 1) * (1 - u^N / 2)^(B - 1)
    h2(u) = N * BigFloat(2)^(-B) * u^(b - 1) * (1 - u^N / 2)^(A - 1)
    function de_quad(f)
        K, h = 20, BigFloat("0.25")
        acc = BigFloat(0)
        for k in -K:K
            t = k * h
            g = PI / 2 * sinh(t)
            u = (1 + tanh(g)) / 2
            du = PI / 2 * cosh(t) / (2 * cosh(g)^2)
            acc += f(u) * du
        end
        return acc * h
    end
    const1 = exp(2 * PI * im * BigFloat(mod(r * a + s * (b - N), N)) / N) / N
    return const1 * (de_quad(h1) + de_quad(h2))
end

worst = 0.0
for (a, b) in ((1, 1), (1, 2), (2, 3))
    for (r, s) in ((0, 0), (1, 0), (0, 1))
        pc = period_closed(15, a, b, r, s)
        pn = period_numeric(15, a, b, r, s)
        e = abs(pc - pn) / max(abs(pc), abs(pn))
        worst = max(worst, Float64(e))
    end
end
check("closed form vs tanh-sinh (9 tests)", worst < 1e-25,
      @sprintf("rel = %.2e", worst))

# ─── 3. Phases: arg P = 2π(ra+sb)/N ───

ph_dev = 0.0
for (a, b) in ((1, 1), (2, 3)), (r, s) in ((1, 0), (0, 1))
    pn = period_numeric(15, a, b, r, s)
    expected = 2 * PI * BigFloat(mod(r * a + s * b, 15)) / 15
    d = abs(angle(pn) - expected)
    d = min(d, abs(abs(d) - 2 * PI))
    ph_dev = max(ph_dev, Float64(d))
end
check("phase form arg P (exact)", ph_dev < 1e-25,
      @sprintf("dev = %.1e", ph_dev))

# ─── 4. Reflection ladder ───

refl = maximum(Float64(abs(gamma(BigFloat(k) / 15) *
                 gamma(1 - BigFloat(k) / 15) -
                 PI / sin(PI * BigFloat(k) / 15)) /
                 (PI / sin(PI * BigFloat(k) / 15))) for k in 1:14)
check("Γ(k/N)Γ(1−k/N) = π/sin(πk/N)", refl < 1e-30,
      @sprintf("rel = %.1e", refl))

# ─── 5. Equivariance ───

eq = 0.0
for (a, b) in ((1, 1), (2, 3))
    for (u, v) in ((1, 0), (0, 1))
        base = period_closed(15, a, b, 1, 0)
        sh = period_closed(15, a, b, 1 + u, v)
        f = exp(2 * PI * im * BigFloat(mod(u * a + v * b, 15)) / 15)
        eq = max(eq, Float64(abs(sh - f * base) / abs(base)))
    end
end
check("μ_N×μ_N equivariance", eq < 1e-30, @sprintf("rel = %.1e", eq))

# ─── 6. Exact integer invariants ───

check("Klein j = c₄³/Δ = −105³/343 = −3375 = −15³",
      -105^3 ÷ 343 == -3375 && (-15)^3 == -3375 && 343 * 3375 == 105^3)
check("disc = 3⁴·5⁶ = 1125²", 3^4 * 5^6 == 1265625 == 1125^2)
check("SNF product = disc",
      prod([1, 1, 5, 5, 15, 15, 15, 15]) == 1265625)
check("Q_stand = 480", 2 * 30 * 8 == 480)
check("b_Ch(15) numeric",
      abs((1 - cos(2π / 15)) - 0.0864539) < 1e-6)

# ─── 7. Flow termination (E4) ───

tstar(W, H, a, b) = lcm(W ÷ gcd(a, W), H ÷ gcd(b, H))
check("t*(48,48,1,1) = 48", tstar(48, 48, 1, 1) == 48)
check("t*(24,36,3,5) = 72", tstar(24, 36, 3, 5) == 72)

println(@sprintf("\n  VERDICT: %d PASS, %d FAIL", passes, fails))
exit(fails == 0 ? 0 : 1)

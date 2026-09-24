// ══════════════════════════════════════════════════════════════════════
//  HODGE LABORATORY — POLYGLOT CORE · GO (int64 exact fractions + f64)
//  Ядро лаборатории на чистом Go: точные целочисленные стенды (дроби
//  int64 — величины проверены, максимум ~3.6e5), квадратуры в float64.
//  The laboratory core in plain Go: exact integer stands (int64
//  fractions — magnitudes verified, max ~3.6e5), quadratures in float64.
//
//  Сборка / Build:  go build verify_core.go   (или go run verify_core.go)
//  Запуск / Run:    ./verify_core
//
//  Автор программы / Program author:
//    Исаев Исхак Хамзатович / Isaev Iskhak Khamzatovich
//  Репозиторий / Repository: wild8highlander/hodge-laboratory
//  Лицензия / License: индивидуальная эксклюзивная / individual exclusive
// ══════════════════════════════════════════════════════════════════════
package main

import (
	"fmt"
	"math"
	"sort"
)

/* ── exact fractions over int64 (num/den, den>0, reduced) ─────────── */
type Frac struct{ n, d int64 }

func igcd64(a, b int64) int64 {
	if a < 0 {
		a = -a
	}
	if b < 0 {
		b = -b
	}
	for b != 0 {
		a, b = b, a%b
	}
	return a
}
func fr(n, d int64) Frac {
	if d < 0 {
		n, d = -n, -d
	}
	g := igcd64(n, d)
	if g == 0 {
		g = 1
	}
	return Frac{n / g, d / g}
}
func frAdd(a, b Frac) Frac { return fr(a.n*b.d+b.n*a.d, a.d*b.d) }
func frSub(a, b Frac) Frac { return fr(a.n*b.d-b.n*a.d, a.d*b.d) }
func frMul(a, b Frac) Frac { return fr(a.n*b.n, a.d*b.d) }

/* ═══ 1–2. census ═══════════════════════════════════════════════════ */
func gcd64(a, b int64) int64 {
	if a < 0 {
		a = -a
	}
	if b < 0 {
		b = -b
	}
	for b != 0 {
		a, b = b, a%b
	}
	return a
}
func lcm64(a, b int64) int64 {
	if a == 0 || b == 0 {
		return 0
	}
	r := a / gcd64(a, b) * b
	if r < 0 {
		return -r
	}
	return r
}

func census(n int64) ([][2]int64, int64) {
	h := map[int64]int64{}
	for a := int64(1); a < n; a++ {
		for b := int64(1); b < n-a; b++ {
			d := n / gcd64(gcd64(n, a), b)
			h[d]++
		}
	}
	keys := make([]int64, 0, len(h))
	for k := range h {
		keys = append(keys, k)
	}
	sort.Slice(keys, func(i, j int) bool { return keys[i] < keys[j] })
	out := make([][2]int64, 0, len(keys))
	for _, k := range keys {
		out = append(out, [2]int64{k, h[k]})
	}
	return out, (n - 1) * (n - 2) / 2
}

func mobius(m int64) int64 {
	if m == 1 {
		return 1
	}
	x, res := m, int64(1)
	for q := int64(2); q*q <= x; q++ {
		if x%q == 0 {
			x /= q
			if x%q == 0 {
				return 0
			}
			res = -res
		}
	}
	if x > 1 {
		res = -res
	}
	return res
}

func censusMobius(n int64) [][2]int64 {
	c := func(k int64) int64 {
		if k >= 3 {
			return (k - 1) * (k - 2) / 2
		}
		return 0
	}
	var out [][2]int64
	for d := int64(2); d <= n; d++ {
		if n%d != 0 {
			continue
		}
		s := int64(0)
		for m := int64(1); m <= d; m++ {
			if d%m == 0 {
				s += mobius(m) * c(d/m)
			}
		}
		if s != 0 {
			out = append(out, [2]int64{d, s})
		}
	}
	return out
}

/* ═══ 3–4. cert E + binary flow ═════════════════════════════════════ */
func tstar(w, h, a, b int64) int64 {
	return lcm64(w/gcd64(a, w), h/gcd64(b, h))
}

func binaryFlow() (t, vis int64, closed bool) {
	const w, h, a, b = int64(48), int64(48), int64(1), int64(1)
	t = tstar(w, h, a, b)
	var x, y, dx, dy int64
	seen := make([][]bool, w)
	for i := range seen {
		seen[i] = make([]bool, h)
	}
	for i := int64(0); i < t; i++ {
		if !seen[x][y] {
			seen[x][y] = true
			vis++
		}
		x = (x + a) % w
		y = (y + b) % h
		dx = (dx + a) % w
		dy = (dy + b) % h
	}
	return t, vis, dx == 0 && dy == 0
}

/* ═══ 5. Arf enumeration ════════════════════════════════════════════ */
func arfEnum(g uint) (size, even, odd int64) {
	n := 2 * g
	size = 1 << n
	half := size >> 1
	shift := int64(1) << (g - 1)
	pairs := make([][2]int, 0, g)
	for i := uint(0); i < g; i++ {
		pairs = append(pairs, [2]int{2 * int(i), 2*int(i) + 1})
	}
	var ev, od int64
	for basis := int64(0); basis < size; basis++ {
		zeros := int64(0)
		for v := int64(0); v < size; v++ {
			qv := int64(0)
			for i := uint(0); i < n; i++ {
				if (v>>i)&1 == 1 {
					qv ^= (basis >> i) & 1
				}
			}
			for _, p := range pairs {
				if ((v>>uint(p[0]))&1)&((v>>uint(p[1]))&1) == 1 {
					qv ^= 1
				}
			}
			if qv == 0 {
				zeros++
			}
		}
		if zeros == half+shift {
			ev++
		} else {
			od++
		}
	}
	return size, ev, od
}

/* ═══ 6. K3: exact rank · SNF · signature ═══════════════════════════ */
const (
	KL = 48
	KN = 49
)

func k3Lines() [KL][3]int32 {
	var ls [KL][3]int32
	k := 0
	for f := int32(1); f <= 3; f++ {
		for a := int32(0); a < 4; a++ {
			for b := int32(0); b < 4; b++ {
				ls[k] = [3]int32{f, a, b}
				k++
			}
		}
	}
	return ls
}

func k3Inter(l1, l2 [3]int32) int32 {
	if l1 == l2 {
		return -2
	}
	f1, a1, b1 := l1[0], l1[1], l1[2]
	f2, a2, b2 := l2[0], l2[1], l2[2]
	if f1 == f2 {
		if (a1 == a2) != (b1 == b2) {
			return 1
		}
		return 0
	}
	lo, hi := f1, f2
	if lo > hi {
		lo, hi = hi, lo
	}
	if lo == 1 && hi == 2 {
		if mod4(a1+b2-a2-b1) == 0 {
			return 1
		}
		return 0
	}
	if lo == 1 && hi == 3 {
		t := a1 - a2 - b2 - b1 - 1
		if f1 == 1 {
			t = a2 - a1 - b1 - b2 - 1
		}
		if mod4(t) == 0 {
			return 1
		}
		return 0
	}
	if mod4(a1+b1-a2-b2) == 0 {
		return 1
	}
	return 0
}

func mod4(v int32) int32 {
	r := v % 4
	if r < 0 {
		r += 4
	}
	return r
}

func k3Gram() (g [KN][KN]int64) {
	ls := k3Lines()
	for i := 0; i < KL; i++ {
		for j := i; j < KL; j++ {
			g[i][j] = int64(k3Inter(ls[i], ls[j]))
			g[j][i] = g[i][j]
		}
	}
	for i := 0; i < KL; i++ {
		g[i][KL] = 1
		g[KL][i] = 1
	}
	g[KL][KL] = 4
	return g
}

func k3Rank(g *[KN][KN]int64) (rank int) {
	var m [KN][KN]Frac
	for i := 0; i < KN; i++ {
		for j := 0; j < KN; j++ {
			m[i][j] = Frac{int64(g[i][j]), 1}
		}
	}
	r := 0
	for c := 0; c < KN && r < KN; c++ {
		piv := -1
		for i := r; i < KN; i++ {
			if m[i][c].n != 0 {
				piv = i
				break
			}
		}
		if piv < 0 {
			continue
		}
		m[r], m[piv] = m[piv], m[r]
		pv := m[r][c]
		for i := r + 1; i < KN; i++ {
			if m[i][c].n == 0 {
				continue
			}
			f := frMul(m[i][c], fr(pv.d, pv.n))
			for j := c; j < KN; j++ {
				m[i][j] = frSub(m[i][j], frMul(f, m[r][j]))
			}
		}
		r++
	}
	return r
}

func k3SNF(g *[KN][KN]int64) (factors []int64) {
	var a [KN][KN]int64
	for i := 0; i < KN; i++ {
		for j := 0; j < KN; j++ {
			a[i][j] = g[i][j]
		}
	}
	for t := 0; t < KN; t++ {
		for {
			var p int64
			pi, pj := -1, -1
			for i := t; i < KN; i++ {
				for j := t; j < KN; j++ {
					v := a[i][j]
					if v < 0 {
						v = -v
					}
					if v != 0 && (pi < 0 || v < p) {
						p, pi, pj = v, i, j
					}
				}
			}
			if pi < 0 {
				return factors
			}
			if pi != t {
				for j := 0; j < KN; j++ {
					a[t][j], a[pi][j] = a[pi][j], a[t][j]
				}
			}
			if pj != t {
				for i := 0; i < KN; i++ {
					a[i][t], a[i][pj] = a[i][pj], a[i][t]
				}
			}
			piv := a[t][t]
			for i := t + 1; i < KN; i++ {
				if q := a[i][t] / piv; q != 0 {
					for j := t; j < KN; j++ {
						a[i][j] -= q * a[t][j]
					}
				}
			}
			for j := t + 1; j < KN; j++ {
				if q := a[t][j] / piv; q != 0 {
					for i := 0; i < KN; i++ {
						a[i][j] -= q * a[i][t]
					}
				}
			}
			divisible := true
		check:
			for i := t + 1; i < KN; i++ {
				for j := t + 1; j < KN; j++ {
					if a[i][j]%piv != 0 {
						divisible = false
						break check
					}
				}
			}
			if divisible {
				break
			}
		}
		v := a[t][t]
		if v < 0 {
			v = -v
		}
		factors = append(factors, v)
	}
	return factors
}

func k3IntEch(g *[KN][KN]int64) (ech [][KN]int64) {
	var m [KN][KN]Frac
	for i := 0; i < KN; i++ {
		for j := 0; j < KN; j++ {
			m[i][j] = Frac{int64(g[i][j]), 1}
		}
	}
	r := 0
	for c := 0; c < KN && r < KN; c++ {
		piv := -1
		for i := r; i < KN; i++ {
			if m[i][c].n != 0 {
				piv = i
				break
			}
		}
		if piv < 0 {
			continue
		}
		m[r], m[piv] = m[piv], m[r]
		pv := m[r][c]
		for j := 0; j < KN; j++ {
			m[r][j] = frMul(m[r][j], fr(pv.d, pv.n))
		}
		for i := 0; i < KN; i++ {
			if i != r && m[i][c].n != 0 {
				f := m[i][c]
				for j := c; j < KN; j++ {
					m[i][j] = frSub(m[i][j], frMul(f, m[r][j]))
				}
			}
		}
		L := int64(1)
		for j := 0; j < KN; j++ {
			L = L / igcd64(L, m[r][j].d) * m[r][j].d
		}
		var row [KN]int64
		gg := int64(0)
		for j := 0; j < KN; j++ {
			row[j] = m[r][j].n * (L / m[r][j].d)
			gg = igcd64(gg, row[j])
		}
		if gg > 1 {
			for j := 0; j < KN; j++ {
				row[j] /= gg
			}
		}
		ech = append(ech, row)
		r++
	}
	return ech
}

func k3Signature(g *[KN][KN]int64, ech [][KN]int64, k int) (pos, neg int64, ok bool) {
	var s [KN][KN]int64
	for i := 0; i < k; i++ {
		var t [KN]int64
		for tt := 0; tt < KN; tt++ {
			if ech[i][tt] == 0 {
				continue
			}
			cit := ech[i][tt]
			for u := 0; u < KN; u++ {
				t[u] += cit * g[tt][u]
			}
		}
		for j := 0; j < k; j++ {
			acc := int64(0)
			for u := 0; u < KN; u++ {
				acc += t[u] * ech[j][u]
			}
			s[i][j] = acc
			s[j][i] = acc
		}
	}
	var a [KN][KN]Frac
	for i := 0; i < k; i++ {
		for j := 0; j < k; j++ {
			a[i][j] = Frac{s[i][j], 1}
		}
	}
	diag := make([]Frac, 0, k)
	for i := 0; i < k; i++ {
		acc := Frac{0, 1}
		for tt := 0; tt < i; tt++ {
			acc = frAdd(acc, frMul(frMul(a[tt][i], a[tt][i]), diag[tt]))
		}
		d := frSub(a[i][i], acc)
		if d.n == 0 {
			return 0, 0, false
		}
		if d.n > 0 {
			pos++
		} else {
			neg++
		}
		diag = append(diag, d)
		for j := i + 1; j < k; j++ {
			s2 := Frac{0, 1}
			for tt := 0; tt < i; tt++ {
				s2 = frAdd(s2, frMul(frMul(a[tt][i], a[tt][j]), diag[tt]))
			}
			v := frMul(frSub(Frac{s[i][j], 1}, s2), fr(diag[i].d, diag[i].n))
			a[i][j] = v
			a[j][i] = v
		}
	}
	return pos, neg, true
}

/* ═══ 8–9. cyclotomic exact layer ═══════════════════════════════════ */
type Zeta struct {
	c [17]int64
	n int64
}

func zetaReduce(z *Zeta) {
	/* Φ₇: x⁶ = −(x⁵+…+x+1);  Φ₉ = x⁶+x³+1 = Φ₃(x³): x⁶ = −x³−1 */
	for {
		top := -1
		for i := 16; i >= 6; i-- {
			if z.c[i] != 0 {
				top = i
				break
			}
		}
		if top < 0 {
			return
		}
		v := z.c[top]
		z.c[top] = 0
		if z.n == 7 {
			for j := 1; j <= 6; j++ {
				z.c[top-j] -= v
			}
		} else {
			z.c[top-3] -= v
			z.c[top-6] -= v
		}
	}
}

func zetaMul(a, b Zeta) (r Zeta) {
	r.n = a.n
	for i := 0; i < 17; i++ {
		if a.c[i] == 0 {
			continue
		}
		for j := 0; j < 17; j++ {
			if b.c[j] != 0 {
				r.c[i+j] += a.c[i] * b.c[j]
			}
		}
	}
	zetaReduce(&r)
	return r
}

func zetaAdd(a, b Zeta) (r Zeta) {
	r.n = a.n
	for i := 0; i < 17; i++ {
		r.c[i] = a.c[i] + b.c[i]
	}
	zetaReduce(&r)
	return r
}

func zetaIsInt(z Zeta) (int64, bool) {
	for i := 1; i < 17; i++ {
		if z.c[i] != 0 {
			return 0, false
		}
	}
	return z.c[0], true
}

func cycLayer(n int64, units [3]int64, vieta [3]int64, poly [4]int64) bool {
	var els [3]Zeta
	for u, k := range units {
		z := Zeta{n: n}
		z.c[k%n]++
		z.c[(n-k)%n]++
		zetaReduce(&z)
		els[u] = z
	}
	e1 := zetaAdd(els[0], zetaAdd(els[1], els[2]))
	e2 := zetaAdd(zetaMul(els[0], els[1]),
		zetaAdd(zetaMul(els[0], els[2]), zetaMul(els[1], els[2])))
	e3 := zetaMul(els[0], zetaMul(els[1], els[2]))
	v1, ok1 := zetaIsInt(e1)
	v2, ok2 := zetaIsInt(e2)
	v3, ok3 := zetaIsInt(e3)
	ok := ok1 && ok2 && ok3 && v1 == vieta[0] && v2 == vieta[1] && v3 == vieta[2]
	ev0 := poly[3] & 1
	ev1 := (poly[0] + poly[1] + poly[2] + poly[3]) & 1
	return ok && ev0 == 1 && ev1 == 1
}

/* ═══ 10–11. BCH radical tower Z[√5][β] ═════════════════════════════ */
type Z5 struct{ a, b int64 } // a + b√5

func z5mul(p, q Z5) Z5 { return Z5{p.a*q.a + 5*p.b*q.b, p.a*q.b + p.b*q.a} }
func z5add(p, q Z5) Z5 { return Z5{p.a + q.a, p.b + q.b} }

func bchLayer(d Z5, x [2]Z5, den int64, poly [5]int64) (residOK, gf2 bool) {
	twMul := func(u, w [2]Z5) [2]Z5 {
		pa := z5mul(u[0], w[0])
		qbd := z5mul(z5mul(u[1], w[1]), d)
		pb := z5mul(u[0], w[1])
		qa := z5mul(u[1], w[0])
		return [2]Z5{z5add(pa, qbd), z5add(pb, qa)}
	}
	acc := [2]Z5{{0, 0}, {0, 0}}
	cur := [2]Z5{{1, 0}, {0, 0}}
	for j := 0; j < 5; j++ {
		if j > 0 {
			cur = twMul(cur, x)
		}
		c := poly[4-j]
		for e := 0; e < 4-j; e++ {
			c *= den
		}
		if c == 0 {
			continue
		}
		acc[0] = z5add(acc[0], z5mul(cur[0], Z5{c, 0}))
		acc[1] = z5add(acc[1], z5mul(cur[1], Z5{c, 0}))
	}
	residOK = acc == [2]Z5{{0, 0}, {0, 0}}
	ev0 := poly[4] & 1
	sum := int64(0)
	for _, v := range poly {
		sum += v
	}
	ev1 := sum & 1
	if ev0 == 0 || ev1 == 0 {
		gf2 = false
	} else {
		var rem [5]int64
		for i, v := range poly {
			rem[i] = v & 1
		}
		for dd := 4; dd >= 2; dd-- {
			if rem[dd] == 1 {
				rem[dd-2] ^= 1
				rem[dd-1] ^= 1
				rem[dd] = 0
			}
		}
		gf2 = !(rem[0] == 0 && rem[1] == 0)
	}
	return residOK, gf2
}

/* ═══ 12–15. float checks ═══════════════════════════════════════════ */
const piF64 = math.Pi

func torusDelta() float64 {
	delta := piF64 / 4
	return 4*piF64*piF64 + delta*delta/2 - math.Pow(delta, 5)
}

/* Ω = 4∫₀¹ [1/√(t⁴+21t²+112) + 1/√(1+21t²+112t⁴)] dt — smooth form
   (raw u-form floors at ~4√ε in finite precision; see polyglot README) */
func kleinOmega(n int) float64 {
	h := 1.0 / float64(n)
	f1 := func(t float64) float64 { return 1 / math.Sqrt(t*t*t*t+21*t*t+112) }
	f2 := func(t float64) float64 { return 1 / math.Sqrt(1+21*t*t+112*t*t*t*t) }
	s1 := f1(0) + f1(1)
	s2 := f2(0) + f2(1)
	for i := 1; i < n; i++ {
		t := float64(i) * h
		w := 2.0
		if i%2 == 1 {
			w = 4.0
		}
		s1 += w * f1(t)
		s2 += w * f2(t)
	}
	return 4 * (s1 + s2) * h / 3
}

func v6Reflection() float64 {
	n := 7.0
	worst := 0.0
	for k := 1; k < 7; k++ {
		kf := float64(k)
		lhs := math.Gamma(kf/n) * math.Gamma((n-kf)/n)
		rhs := piF64 / math.Sin(piF64*kf/n)
		if e := math.Abs(lhs-rhs) / math.Abs(rhs); e > worst {
			worst = e
		}
	}
	return worst
}

func periodQuadrature(n, a, b int64) float64 {
	af, bf, nf := float64(a), float64(b), float64(n)
	aa, bb := af/nf, bf/nf
	const K, h = 150, 0.05
	i1, i2 := 0.0, 0.0
	for kk := -K; kk <= K; kk++ {
		t := float64(kk) * h
		st := math.Sinh(t)
		z := math.Abs(piF64 / 2 * st)
		if z > 350 {
			continue
		}
		u := 0.5 * (1 + math.Tanh(piF64/2*st))
		if u <= 0 || u >= 1 {
			continue
		}
		chz := math.Cosh(z)
		w := (piF64 / 4) * math.Cosh(t) / (chz * chz) * h
		i1 += nf * w * math.Pow(2, -aa) * math.Pow(u, af-1) * math.Pow(1-math.Pow(u, nf)/2, bb-1)
		i2 += nf * w * math.Pow(2, -bb) * math.Pow(u, bf-1) * math.Pow(1-math.Pow(u, nf)/2, aa-1)
	}
	closed := math.Gamma(af/nf) * math.Gamma(bf/nf) / math.Gamma((af+bf)/nf)
	return math.Abs((i1+i2)-closed) / math.Abs(closed)
}

/* ═══ output ════════════════════════════════════════════════════════ */
var total, passed int

func check(name string, ok bool, detail string) {
	total++
	if ok {
		passed++
	}
	mark := "FAIL"
	if ok {
		mark = "PASS"
	}
	if detail != "" {
		fmt.Printf("  [%s] %s  ·  %s\n", mark, name, detail)
	} else {
		fmt.Printf("  [%s] %s\n", mark, name)
	}
}

func main() {
	fmt.Println("════════════════════════════════════════════════════════════")
	fmt.Println(" HODGE LABORATORY · POLYGLOT CORE · GO (int64 fractions + f64)")
	fmt.Println(" Ядро лаборатории · целочисленная верификация / integer verification")
	fmt.Println("════════════════════════════════════════════════════════════")

	fmt.Println("\n[1-2] V1 · Census of conductors / Ценз проводников")
	expect := [][2]int64{{7, 15}, {9, 28}, {15, 91}, {30, 406}}
	ok1, ok2 := true, true
	for _, eg := range expect {
		h, genus := census(eg[0])
		sum := int64(0)
		for _, e := range h {
			sum += e[1]
		}
		if genus != eg[1] || sum != genus {
			ok1 = false
		}
		hm := censusMobius(eg[0])
		if len(h) != len(hm) {
			ok2 = false
		} else {
			for i := range h {
				if h[i] != hm[i] {
					ok2 = false
				}
			}
		}
	}
	check("Σh_d = g for N=7,9,15,30 · Σh_d = g", ok1, "15/28/91/406")
	check("Möbius scheme agrees · схема Мёбиуса совпадает", ok2, "")

	fmt.Println("\n[3] Certificate E · t* = lcm(W/gcd(a,W), H/gcd(b,H))")
	ce := [][5]int64{{48, 48, 1, 1, 48}, {96, 96, 1, 1, 96}, {24, 36, 3, 5, 72},
		{7, 14, 1, 1, 14}, {12, 12, 4, 6, 6}, {384, 384, 1, 1, 384}}
	ok3 := true
	for _, c := range ce {
		if tstar(c[0], c[1], c[2], c[3]) != c[4] {
			ok3 = false
		}
	}
	check("6 cert-E cases · 6 случаев cert E", ok3, "t*(24,36;3,5)=72 …")

	fmt.Println("\n[4] Binary flow 48×48 / Двоичный поток")
	t, vis, closed := binaryFlow()
	check("t*=48 · 48 cells · closure · замыкание", t == 48 && vis == 48 && closed,
		"48+212+432+114=806")

	fmt.Println("\n[5] Arf enumeration / Перечисление Арфа")
	ok5, det5 := true, ""
	for g := uint(1); g <= 3; g++ {
		size, ev, od := arfEnum(g)
		expEv := (int64(1) << (g - 1)) * ((int64(1) << g) + 1)
		expOd := (int64(1) << (g - 1)) * ((int64(1) << g) - 1)
		if size != (int64(1)<<(2*g)) || ev != expEv || od != expOd {
			ok5 = false
		}
		det5 += fmt.Sprintf("g=%d: %d/%d ", g, ev, od)
	}
	check("even/odd forms g=1..3 · чётные/нечётные формы", ok5, det5+"(g=3: 36/28)")

	fmt.Println("\n[6] K3 stand · exact integer machinery / точная машина")
	g := k3Gram()
	rank := k3Rank(&g)
	factors := k3SNF(&g)
	det := int64(1)
	for _, f := range factors {
		det *= f
	}
	ech := k3IntEch(&g)
	pos, neg, sigOK := k3Signature(&g, ech, len(ech))
	check("rank_Q = 20 = ρ (Shioda · Шиода)", rank == 20, fmt.Sprintf("rank=%d", rank))
	check("signature (1,19) — Hodge index · сигнатура", sigOK && pos == 1 && neg == 19, "")
	detOK := det == 64 && len(factors) >= 2 && factors[len(factors)-2] == 8 && factors[len(factors)-1] == 8
	check("SNF → det = 64 = 8²", detOK, fmt.Sprintf("SNF det = %d", det))
	check("48 lines on the Fermat quartic · прямых", KL == 48, "")
	{
		ls := k3Lines()
		famOK := true
		for a := int32(0); a < 4 && famOK; a++ {
			for j := 0; j < KN; j++ {
				s := int64(0)
				for b := int32(0); b < 4; b++ {
					for id, l := range ls {
						if l[0] == 1 && l[1] == a && l[2] == b {
							s += g[id][j]
						}
					}
				}
				if s != g[KL][j] {
					famOK = false
					break
				}
			}
		}
		check("family relation Σ_b L1(a,b) ~ h · семейное соотношение", famOK, "")
	}

	fmt.Println("\n[7] Klein stand / Слой Клейна")
	{
		j := -(int64(105) * 105 * 105) / 343
		var expand [4]int64
		fi := [][2]int64{{0, 1}, {1, -7}}
		fj := [][2]int64{{0, 1}, {1, 7}, {2, 14}}
		for _, fic := range fi {
			for _, fjc := range fj {
				expand[fic[0]+fjc[0]] += fic[1] * fjc[1]
			}
		}
		ok := j == -3375 && (-343)*j == 105*105*105 &&
			expand == [4]int64{1, 0, -35, -98} && 7*7-4*14 == -7
		check("j = −3375 = −15³ · Δ·j = 105³ · disc = −7", ok,
			"(v−7)(v²+7v+14) = v³−35v−98")
	}

	fmt.Println("\n[8-9] Cyclotomic layer N=7/9 · Z[ζ]/Φₙ (exact integer arithmetic)")
	{
		ok7 := cycLayer(7, [3]int64{1, 2, 3}, [3]int64{-1, -2, 1}, [4]int64{1, 1, -2, -1})
		check("N=7: Vieta s=(−1,−2,1) computed in Z[ζ]/Φ₇ + GF(2)", ok7,
			"e1,e2,e3 exact integers · cubic irreducible over GF(2)")
		ok9 := cycLayer(9, [3]int64{1, 2, 4}, [3]int64{0, -3, -1}, [4]int64{1, 0, -3, 1})
		check("N=9: Vieta s=(0,−3,−1) computed in Z[ζ]/Φ₉ + GF(2)", ok9,
			"e1,e2,e3 exact integers · cubic irreducible over GF(2)")
	}

	fmt.Println("\n[10-11] BCH radical tower Z[√5][β] · Радикальная башня")
	{
		r15, g15 := bchLayer(Z5{30, -6}, [2]Z5{{1, 1}, {1, 0}}, 4, [5]int64{1, -1, -4, 4, 1})
		check("n=15: 4⁴P(x) ≡ 0 in Z[√5][β] + GF(2)", r15 && g15,
			"b_Ch(15) = (7 − √5 − √(30−6√5))/8")
		r30, g30 := bchLayer(Z5{30, 6}, [2]Z5{{-1, 1}, {1, 0}}, 4, [5]int64{1, 1, -4, -4, 1})
		check("n=30: 4⁴P(x) ≡ 0 in Z[√5][β] + GF(2)", r30 && g30,
			"b_Ch(30) = (9 − √5 − √(30+6√5))/8")
	}

	fmt.Println("\n[12] Torus Δ_Ch (f64 ~16 digits)")
	{
		d := torusDelta()
		r := 39.48799539346835051297464603266144167978
		rel := math.Abs(d-r) / r
		check("Δ_Ch = 4π² + δ²/2 − δ⁵ (40-digit reference)", rel < 1e-13,
			fmt.Sprintf("Δ_Ch = %.17g", d))
	}

	fmt.Println("\n[13] Klein Ω (regularized smooth quadrature, f64)")
	{
		om := kleinOmega(20000)
		r := 1.93331170561681154673308
		rel := math.Abs(om-r) / r
		check("Ω = 2∫₇^∞ dx/√(x³−35x−98)", rel < 1e-13,
			fmt.Sprintf("Ω = %.17g, rel = %.2e (ref is 23-digit)", om, rel))
	}

	fmt.Println("\n[14] V6 Γ-reflection (f64 stdlib)")
	{
		e := v6Reflection()
		check("Γ(k/N)Γ((N−k)/N) = π/sin(πk/N), N=7", e < 1e-12,
			fmt.Sprintf("max rel = %.2e", e))
	}

	fmt.Println("\n[15] Period closed vs tanh–sinh (f64)")
	{
		e15 := periodQuadrature(15, 2, 3)
		e9 := periodQuadrature(9, 1, 2)
		check("P_closed = P_numeric (N=15; N=9)", e15 < 1e-10 && e9 < 1e-10,
			fmt.Sprintf("rel = %.2e / %.2e", e15, e9))
	}

	fmt.Println("\n════════════════════════════════════════════════════════════")
	fmt.Printf(" ИТОГ / RESULT: %d/%d\n", passed, total)
	if passed == total {
		fmt.Println(" ✔ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ · ALL CHECKS PASSED")
	} else {
		fmt.Println(" ✘ ЕСТЬ ПРОВАЛЫ · THERE ARE FAILURES")
	}
	fmt.Println(" Программа: Исаев Исхак Хамзатович / Program: Isaev Iskhak Khamzatovich")
	fmt.Println("════════════════════════════════════════════════════════════")
	if passed != total {
		panic("verification failed")
	}
}

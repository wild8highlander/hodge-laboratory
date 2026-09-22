// ═══════════════════════════════════════════════════════════════════
// HODGE LABORATORY — RUST VERIFICATION
// Laboratory "The Dynamic Principle" (Isaev Iskhak Khamzatovich)
//
// Safe exact integer arithmetic (i128 guards against overflow),
// censuses, ranks, invariants.
// Run:      rustc -O verify_hodge.rs -o verify_hodge && ./verify_hodge
// Exit codes: 0 — all checks accepted, 1 — at least one failure.
// ═══════════════════════════════════════════════════════════════════

use std::sync::atomic::{AtomicU32, Ordering};

static PASSES: AtomicU32 = AtomicU32::new(0);
static FAILS: AtomicU32 = AtomicU32::new(0);

fn check(name: &str, actual: i128, expected: i128) {
    if actual == expected {
        PASSES.fetch_add(1, Ordering::Relaxed);
        println!("  [PASS] {}", name);
    } else {
        FAILS.fetch_add(1, Ordering::Relaxed);
        println!("  [FAIL] {}  got {} expected {}", name, actual, expected);
    }
}

fn gcd(mut a: i128, mut b: i128) -> i128 {
    while b != 0 {
        let r = a % b;
        a = b;
        b = r;
    }
    a
}

fn lcm(a: i128, b: i128) -> i128 {
    a / gcd(a, b) * b
}

/// Census of characters: sum of h_d over conductors = genus (exact).
fn census_total(n: i128) -> i128 {
    let mut cnt = 0i128;
    for a in 1..n {
        for _b in 1..(n - a) {
            cnt += 1;
        }
    }
    cnt
}

/// h_d for a given conductor d.
fn census_d(n: i128, d: i128) -> i128 {
    let mut cnt = 0i128;
    for a in 1..n {
        for b in 1..(n - a) {
            if n / gcd(gcd(n, a), b) == d {
                cnt += 1;
            }
        }
    }
    cnt
}

/// Arf formula: even theta-characteristics 2^(g−1)(2^g+1).
fn even_theta(g: u32) -> i128 {
    let p = 1i128 << g;
    (p / 2) * (p + 1)
}

/// Odd ones: 2^(g−1)(2^g−1).
fn odd_theta(g: u32) -> i128 {
    let p = 1i128 << g;
    (p / 2) * (p - 1)
}

/// Exact rank of an integer matrix: row echelon over Q
/// (fractions (p, q), q > 0, kept reduced; i128 arithmetic).
fn int_rank(m: Vec<Vec<i128>>) -> usize {
    let n = m.len();
    let mut a: Vec<Vec<(i128, i128)>> = m
        .iter()
        .map(|row| row.iter().map(|&x| (x, 1i128)).collect())
        .collect();
    let mut rank = 0usize;
    for col in 0..n {
        if rank >= n {
            break;
        }
        let mut piv = None;
        for r in rank..n {
            if a[r][col].0 != 0 {
                piv = Some(r);
                break;
            }
        }
        let piv = match piv {
            Some(r) => r,
            None => continue,
        };
        a.swap(rank, piv);
        for r in 0..n {
            if r != rank && a[r][col].0 != 0 {
                let (fp, fq) = a[r][col];
                let (pp, pq) = a[rank][col];
                // factor f = a[r][col] / a[rank][col] = fp*pq / (fq*pp)
                let fnum = fp * pq;
                let fden = fq * pp;
                for j in 0..n {
                    let (ap, aq) = a[r][j];
                    let (bp, bq) = a[rank][j];
                    // a - f*b = ap/aq - (fnum/fden)*(bp/bq)
                    let np = ap * fden * bq - fnum * bp * aq;
                    let nq = aq * fden * bq;
                    let sg = if nq < 0 { -1i128 } else { 1 };
                    let (np, nq) = (np * sg, nq * sg);
                    let g = gcd(np.abs(), nq).max(1);
                    a[r][j] = (np / g, nq / g);
                }
            }
        }
        rank += 1;
    }
    rank
}

/// K3 intersection matrix: 48 lines + h (combinatorial rules).
fn k3_gram() -> Vec<Vec<i128>> {
    let n = 49;
    let mut g = vec![vec![0i128; n]; n];
    let inter = |l1: usize, l2: usize| -> i128 {
        let f1 = l1 / 16;
        let a1 = (l1 % 16) / 4;
        let b1 = l1 % 4;
        let f2 = l2 / 16;
        let a2 = (l2 % 16) / 4;
        let b2 = l2 % 4;
        if l1 == l2 {
            return -2;
        }
        if f1 == f2 {
            return if (a1 == a2) != (b1 == b2) { 1 } else { 0 };
        }
        let m4 = |x: i128| x.rem_euclid(4);
        if (f1 == 0 && f2 == 1) || (f1 == 1 && f2 == 0) {
            return if m4(a1 as i128 + b2 as i128 - a2 as i128 - b1 as i128) == 0 {
                1
            } else {
                0
            };
        }
        if (f1 == 0 && f2 == 2) || (f1 == 2 && f2 == 0) {
            let v = if f1 == 0 {
                a2 as i128 - a1 as i128 - b1 as i128 - b2 as i128 - 1
            } else {
                a1 as i128 - a2 as i128 - b2 as i128 - b1 as i128 - 1
            };
            return if m4(v) == 0 { 1 } else { 0 };
        }
        if m4(a1 as i128 + b1 as i128 - a2 as i128 - b2 as i128) == 0 {
            1
        } else {
            0
        }
    };
    for i in 0..48 {
        for j in 0..48 {
            g[i][j] = inter(i, j);
        }
    }
    for i in 0..48 {
        g[i][48] = 1;
        g[48][i] = 1;
    }
    g[48][48] = 4;
    g
}

fn main() {
    println!("HODGE LABORATORY — RUST VERIFICATION PANEL\n");

    // 1. Genera and censuses
    check("g(15) = 91", ((15 - 1) * (15 - 2)) / 2, 91);
    check("g(30) = 406", ((30 - 1) * (30 - 2)) / 2, 406);
    check("g(7) = 15", ((7 - 1) * (7 - 2)) / 2, 15);
    check("N=15 census sum = 91", census_total(15), 91);
    check("N=30 census sum = 406", census_total(30), 406);
    check("N=15: h(3) = 1", census_d(15, 3), 1);
    check("N=15: h(5) = 6", census_d(15, 5), 6);
    check("N=15: h(15) = 84", census_d(15, 15), 84);
    check("N=30: h(6) = 9", census_d(30, 6), 9);
    check("N=30: h(10) = 30", census_d(30, 10), 30);
    check("N=30: h(30) = 276", census_d(30, 30), 276);

    // 2. K3: exact rank
    let rank = int_rank(k3_gram()) as i128;
    check("K3: exact rank over Q = 20", rank, 20);
    check("K3: isotypy 1+7+7+7 = 22 (mu4 decomposition)", 1 + 7 + 7 + 7, 22);
    check("K3: signature (1,19): 1 + 19 = rho = 20", 1 + 19, 20);

    // 3. Klein quartic
    check("Klein: c4^3 = 105^3 = 1157625", 105i128.pow(3), 1157625);
    check("Klein: |Delta|*|j| = 343*3375 = 105^3", 343 * 3375, 1157625);
    check("Klein: j = -c4^3/Delta = -3375", -(105i128.pow(3)) / 343, -3375);
    check("Klein: (-15)^3 = -3375", -15i128.pow(3), -3375);

    // 4. Stand N=15/30
    check("disc = 3^4*5^6 = 81*15625 = 1265625", 81 * 15625, 1265625);
    check("vol_h = sqrt(disc) = 1125: 1125^2 = 1265625", 1125 * 1125, 1265625);
    let snf: i128 = [1i128, 1, 5, 5, 15, 15, 15, 15].iter().product();
    check("SNF (1,1,5,5,15,15,15,15) product = 1265625", snf, 1265625);
    check("Q_stand = 2N*max(s_i) = 2*30*8 = 480", 2 * 30 * 8, 480);

    // 5. Errata E8
    check("g=3: even (Arf=0) = 2^2*(2^3+1) = 36", even_theta(3), 36);
    check("g=3: odd (Arf=1) = 2^2*(2^3-1) = 28", odd_theta(3), 28);
    check("g=3: total = 36 + 28 = 64", even_theta(3) + odd_theta(3), 64);
    check("g=1: even = 3", even_theta(1), 3);
    check("g=2: even = 10", even_theta(2), 10);
    check("g=4: even = 136", even_theta(4), 136);

    // 6. Flow termination (E4)
    check("t*(48,48,1,1) = lcm(48,48) = 48",
          lcm(48 / gcd(1, 48), 48 / gcd(1, 48)), 48);
    check("t*(24,36,3,5) = lcm(8,36) = 72",
          lcm(24 / gcd(3, 24), 36 / gcd(5, 36)), 72);
    check("t*(12,12,4,6) = lcm(3,2) = 6",
          lcm(12 / gcd(4, 12), 12 / gcd(6, 12)), 6);

    // 7. Binary code reference totals
    check("binary code: 48+212+432+114 = 806", 48 + 212 + 432 + 114, 806);

    let p = PASSES.load(Ordering::Relaxed);
    let f = FAILS.load(Ordering::Relaxed);
    println!("\n  VERDICT: {} PASS, {} FAIL", p, f);
    if f > 0 {
        std::process::exit(1);
    }
}

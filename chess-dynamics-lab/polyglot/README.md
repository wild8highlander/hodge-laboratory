# polyglot/ — the C1–C10 battery in seven languages

The same verification battery is implemented **independently** in seven languages.
Each backend builds its own tables, recomputes its own censuses and prints the same
protocol lines; the final line of every run is `verdict: 10/10`.

This is the cross-language agreement certificate of theorem T12(iv): bit-identical
reference constants (perft chain, orbit censuses, edge censuses, splitmix64 vectors)
mean that a mismatch of any backend is caught by simply comparing the output lines.

## The battery

| Check | Content |
|---|---|
| C1 | V4 orbit census 20 (8 diag ×2 + 12 off-diag ×4); D4 orbits 10 by Burnside |
| C2 | move-graph edge censuses: rook 448, bishop 280, knight 168, king 210, queen 728 |
| C3 | mobility sums: king 420, knight 336, bishop 560, rook 896, queen 1456; queen max 27 |
| C4 | t\* = lcm(W/gcd(a,W), H/gcd(b,H)) — formula vs simulation over a case grid; the damped billiard path ratio → 1 (γ = π⁴/256) |
| C5 | perft(1..4) = 20 / 400 / 8902 / 197281 from the local generator |
| C6 | threat field: mass 38 per side (initial), D4-equivariance 0 violations (pawnless), pawn anomaly 176 |
| C7 | energy: mobility 20 → 30 after 1.e4; E deterministic |
| C8 | the Morphy mate by forced search: 3 plies, key a1a6 |
| C9 | splitmix64 vectors sm(1)=0x910A2DEC89025CC1, sm(2)=0x975835DE1C9756CE, sm(3)=0x1D0B14E4DB018FED; inverse round-trip |
| C10 | the closed Warnsdorff knight tour from f5: 64 unique squares, knight steps, closure d6→f5 |

## Files and verification status

| Language | File | Status |
|---|---|---|
| Python | `python/chess_core.py` | verified locally — 10/10 |
| C | `c/chess_core.c` | verified locally (gcc -O2 -std=c99) — 10/10 |
| JavaScript | `javascript/chess_core.js` | verified locally (node ≥ 18, BigInt) — 10/10 |
| Rust | `rust/chess_core.rs` | verified in GitHub Actions CI (rustc stable) |
| Go | `go/chess_core.go` | verified in CI (go 1.22, `go run`) |
| Julia | `julia/chess_core.jl` | verified in CI (julia 1.10) |
| Java | `java/ChessCore.java` | verified in CI (temurin 17, javac + java) |

## Running

```bash
bash polyglot/run_all.sh          # every backend available locally + summary table

# individually
python3 polyglot/python/chess_core.py
gcc -O2 -std=c99 -o /tmp/cc polyglot/c/chess_core.c -lm && /tmp/cc
node polyglot/javascript/chess_core.js
rustc -O polyglot/rust/chess_core.rs -o /tmp/cc_rs && /tmp/cc_rs
go run polyglot/go/chess_core.go
julia polyglot/julia/chess_core.jl
cd polyglot/java && javac ChessCore.java && java ChessCore
```

## Implementation notes

- The 64-bit arithmetic of splitmix64 uses unsigned wrapping semantics: explicit
  codes in C (the enum-continuation pitfall), BigInt in JavaScript, `u64` in Rust,
  `uint64`/`long` with masks in Java/Go/Julia.
- The slider directions differ per piece (4 rook dirs, 4 bishop dirs, 8 queen dirs) —
  the classic source of the "queen moves like a rook" bug; C6/C2 catch it.
- Every backend is self-contained: no shared files, no FFI, no JSON — the output is
  the protocol.

© 2026 Isaev Iskhak Khamzatovich. All rights reserved. See [../LICENSE](../LICENSE).

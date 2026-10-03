// chess_core.go — POLYGLOT VERIFICATION CORE (Go implementation)
//
// Program author: Isaev Iskhak Khamzatovich
// Repository: github.com/wild8highlander/chess-dynamics-lab
// License: individual exclusive license (see LICENSE)
//
// The same 10-check battery as polyglot/python/chess_core.py:
//
//   C1  board algebra      V4 orbits 20 (8x2 + 12x4), D4 orbits 10 (Burnside)
//   C2  move-graph census  edges R448 B280 N168 K210 Q728
//   C3  mobility census    sums R896 B560 N336 K420 Q1456, max 14/13/8/8/27
//   C4  flow termination   t* = lcm(W/gcd(a,W), H/gcd(b,H)) on 9 cases
//   C5  perft identities   20 / 400 / 8902 / 197281 from the initial position
//   C6  threat fields      D4-equivariance (pawnless) + pawn anomaly 176
//   C7  kinetic energy     initial mobility 20, after 1.e4 mobility 30
//   C8  mate certificates  Morphy m2 (a1a6), ladder m2, N+R m1 (g1g8)
//   C9  Zobrist hashing    incremental hash over a fixed playout + splitmix64
//   C10 knight tour        the frozen closed tour: 64 cells, closure move
//
// Build:  go build -o chess_core_go go/chess_core.go && ./chess_core_go
// (or:    go run go/chess_core.go)       (expects the verdict 10/10)
//
// No external modules beyond the Go standard library, no randomness,
// no floating point.  Piece codes are EXPLICIT constants (white 1..6,
// black -1..-6) — no auto-increment enums that would break on negatives.
// splitmix64 / Zobrist use native uint64 arithmetic (Go unsigned ops
// wrap by definition; shifts on unsigned values are logical).
// Classic perft pitfalls respected below: sliders use ALL their
// directions (queen 8, rook/bishop 4), en-passant capture is generated
// only from the correct pawn rank (4 for White, 3 for Black, 0-based),
// a move that would capture a king is never legal, and castling rights
// are updated when the king/rook moves or a rook square is captured.
package main

import (
	"fmt"
	"os"
	"strings"
)

// ── board (0x88): sq = 16*rank + file, off-board iff (sq & 0x88) != 0 ──

const (
	EMPTY = 0
	WP    = 1
	WN    = 2
	WB    = 3
	WR    = 4
	WQ    = 5
	WK    = 6
	BP    = -1
	BN    = -2
	BB    = -3
	BR    = -4
	BQ    = -5
	BK    = -6
)

const (
	WKCastle = 1
	WQCastle = 2
	BKCastle = 4
	BQCastle = 8

	FlagNormal = 0
	FlagDouble = 1
	FlagEP     = 2
	FlagCastle = 3

	A1 = 0
	E1 = 4
	H1 = 7
	A8 = 112
	E8 = 116
	H8 = 119
)

var knightOffs = [8]int{31, 33, 14, 18, -31, -33, -14, -18}
var bishopDirs = [4]int{15, 17, -15, -17}
var rookDirs   = [4]int{16, -16, 1, -1}
var kingDirs   = [8]int{15, 16, 17, 1, -15, -16, -17, -1}

// the frozen closed knight tour (from polyglot/python/chess_core.py)
var knightTour = [64]string{
	"f5", "h4", "g2", "e1", "c2", "a1", "b3", "c1", "a2", "b4", "a6", "b8",
	"d7", "f8", "h7", "g5", "h3", "g1", "e2", "g3", "h1", "f2", "d1", "b2",
	"d3", "f4", "h5", "g7", "e8", "f6", "g8", "h6", "g4", "h2", "f1", "e3",
	"d5", "c7", "a8", "b6", "a4", "c3", "b1", "a3", "b5", "a7", "c8", "e7",
	"g6", "h8", "f7", "e5", "f3", "d2", "c4", "a5", "c6", "d4", "e6", "d8",
	"b7", "c5", "e4", "d6",
}

type Move struct {
	fr, to, promo, flag int
}

type Position struct {
	board    [128]int
	side     int // 1 = White to move, -1 = Black to move
	castling int
	ep       int // en-passant target square or -1
}

type Undo struct {
	m        Move
	captured int
	castling int
	ep       int
}

func abs(x int) int {
	if x < 0 {
		return -x
	}
	return x
}

func nameSq(s string) int {
	f := int(s[0] - 'a')
	r := int(s[1] - '1')
	return 16*r + f
}

func charPiece(ch byte) int {
	switch ch {
	case 'P':
		return WP
	case 'N':
		return WN
	case 'B':
		return WB
	case 'R':
		return WR
	case 'Q':
		return WQ
	case 'K':
		return WK
	case 'p':
		return BP
	case 'n':
		return BN
	case 'b':
		return BB
	case 'r':
		return BR
	case 'q':
		return BQ
	case 'k':
		return BK
	}
	return EMPTY
}

func setFen(pos *Position, fen string) {
	parts := strings.Fields(fen)
	for i := 0; i < 128; i++ {
		pos.board[i] = EMPTY
	}
	pos.side, pos.castling, pos.ep = 1, 0, -1
	rank, file := 7, 0
	for i := 0; i < len(parts[0]); i++ {
		ch := parts[0][i]
		if ch == '/' {
			rank--
			file = 0
			continue
		}
		if ch >= '1' && ch <= '8' {
			file += int(ch - '0')
			continue
		}
		pos.board[16*rank+file] = charPiece(ch)
		file++
	}
	if len(parts) > 1 {
		if parts[1] == "w" {
			pos.side = 1
		} else {
			pos.side = -1
		}
	}
	if len(parts) > 2 && parts[2] != "-" {
		for i := 0; i < len(parts[2]); i++ {
			switch parts[2][i] {
			case 'K':
				pos.castling |= WKCastle
			case 'Q':
				pos.castling |= WQCastle
			case 'k':
				pos.castling |= BKCastle
			case 'q':
				pos.castling |= BQCastle
			}
		}
	}
	if len(parts) > 3 && parts[3] != "-" {
		pos.ep = nameSq(parts[3])
	}
}

func attacked(b *[128]int, sq, by int) bool {
	// pawns: a white pawn (by == 1) attacks sq from sq-15 / sq-17
	var pawnOff [2]int
	if by == 1 {
		pawnOff = [2]int{-15, -17}
	} else {
		pawnOff = [2]int{15, 17}
	}
	for i := 0; i < 2; i++ {
		s := sq + pawnOff[i]
		if s&0x88 == 0 && b[s] == by {
			return true
		}
	}
	for i := 0; i < 8; i++ {
		s := sq + knightOffs[i]
		if s&0x88 == 0 && b[s] == 2*by {
			return true
		}
	}
	for i := 0; i < 8; i++ {
		s := sq + kingDirs[i]
		if s&0x88 == 0 && b[s] == 6*by {
			return true
		}
	}
	for dset := 0; dset < 2; dset++ {
		var dirs [4]int
		var kinds [2]int
		if dset == 0 {
			dirs = bishopDirs
			kinds = [2]int{3, 5}
		} else {
			dirs = rookDirs
			kinds = [2]int{4, 5}
		}
		for i := 0; i < 4; i++ {
			s := sq + dirs[i]
			for s&0x88 == 0 {
				p := b[s]
				if p != EMPTY {
					if (p > 0) == (by > 0) && (abs(p) == kinds[0] || abs(p) == kinds[1]) {
						return true
					}
					break
				}
				s += dirs[i]
			}
		}
	}
	return false
}

func kingSq(pos *Position, side int) int {
	t := 6 * side
	for sq := 0; sq < 128; sq++ {
		if sq&0x88 != 0 {
			continue
		}
		if pos.board[sq] == t {
			return sq
		}
	}
	panic("king missing")
}

// epRank: en-passant capture is generated only from the correct pawn
// rank (rank index 4 for White, 3 for Black, 0-based).
func epRank(side int) int {
	if side == 1 {
		return 4
	}
	return 3
}

func pseudoMoves(pos *Position, out []Move) int {
	b := &pos.board
	side := pos.side
	n := 0
	for rank := 0; rank < 8; rank++ {
		for file := 0; file < 8; file++ {
			fr := 16*rank + file
			piece := b[fr]
			if piece == EMPTY || (piece > 0) != (side > 0) {
				continue
			}
			ap := abs(piece)
			if ap == 1 {
				fwd := 16 * side
				promoRank, startRank := 1, 6
				if side == 1 {
					promoRank, startRank = 6, 1
				}
				s := fr + fwd
				if s&0x88 == 0 && b[s] == EMPTY {
					if rank == promoRank {
						prs := [4]int{5, 2, 4, 3}
						for k := 0; k < 4; k++ {
							out[n] = Move{fr, s, prs[k], FlagNormal}
							n++
						}
					} else {
						out[n] = Move{fr, s, 0, FlagNormal}
						n++
						if rank == startRank && b[s+fwd] == EMPTY {
							out[n] = Move{fr, s + fwd, 0, FlagDouble}
							n++
						}
					}
				}
				for k := 0; k < 2; k++ {
					off := fwd - 1
					if k == 1 {
						off = fwd + 1
					}
					s = fr + off
					if s&0x88 != 0 {
						continue
					}
					q := b[s]
					if q != EMPTY && (q > 0) != (side > 0) {
						if rank == promoRank {
							prs := [4]int{5, 2, 4, 3}
							for j := 0; j < 4; j++ {
								out[n] = Move{fr, s, prs[j], FlagNormal}
								n++
							}
						} else {
							out[n] = Move{fr, s, 0, FlagNormal}
							n++
						}
					} else if s == pos.ep && q == EMPTY && rank == epRank(side) {
						out[n] = Move{fr, s, 0, FlagEP}
						n++
					}
				}
			} else if ap == 2 || ap == 6 {
				var offs []int
				if ap == 2 {
					offs = knightOffs[:]
				} else {
					offs = kingDirs[:]
				}
				for i := 0; i < 8; i++ {
					s := fr + offs[i]
					if s&0x88 != 0 {
						continue
					}
					q := b[s]
					if q == EMPTY || (q > 0) != (side > 0) {
						out[n] = Move{fr, s, 0, FlagNormal}
						n++
					}
				}
			} else {
				// sliders: rook 4 dirs, bishop 4 dirs, queen 8 dirs
				var dirs []int
				cnt := 4
				if ap == 4 {
					dirs = rookDirs[:]
				} else if ap == 3 {
					dirs = bishopDirs[:]
				} else {
					dirs = kingDirs[:]
					cnt = 8
				}
				for i := 0; i < cnt; i++ {
					off := dirs[i]
					s := fr + off
					for s&0x88 == 0 {
						q := b[s]
						if q == EMPTY {
							out[n] = Move{fr, s, 0, FlagNormal}
							n++
						} else {
							if (q > 0) != (side > 0) {
								out[n] = Move{fr, s, 0, FlagNormal}
								n++
							}
							break
						}
						s += off
					}
				}
			}
		}
	}
	// castling: rights present, path empty, rook in place,
	// king does not pass through or land on an attacked square
	if side == 1 {
		if pos.castling&WKCastle != 0 && b[5] == EMPTY && b[6] == EMPTY &&
			b[4] == WK && b[7] == WR &&
			!attacked(b, 4, -1) && !attacked(b, 5, -1) && !attacked(b, 6, -1) {
			out[n] = Move{E1, 6, 0, FlagCastle}
			n++
		}
		if pos.castling&WQCastle != 0 && b[3] == EMPTY && b[2] == EMPTY &&
			b[1] == EMPTY && b[4] == WK && b[0] == WR &&
			!attacked(b, 4, -1) && !attacked(b, 3, -1) && !attacked(b, 2, -1) {
			out[n] = Move{E1, 2, 0, FlagCastle}
			n++
		}
	} else {
		if pos.castling&BKCastle != 0 && b[117] == EMPTY && b[118] == EMPTY &&
			b[116] == BK && b[119] == BR &&
			!attacked(b, 116, 1) && !attacked(b, 117, 1) && !attacked(b, 118, 1) {
			out[n] = Move{E8, 118, 0, FlagCastle}
			n++
		}
		if pos.castling&BQCastle != 0 && b[115] == EMPTY && b[114] == EMPTY &&
			b[113] == EMPTY && b[116] == BK && b[112] == BR &&
			!attacked(b, 116, 1) && !attacked(b, 115, 1) && !attacked(b, 114, 1) {
			out[n] = Move{E8, 114, 0, FlagCastle}
			n++
		}
	}
	return n
}

func makeMove(pos *Position, m Move) Undo {
	b := &pos.board
	side := pos.side
	piece := b[m.fr]
	u := Undo{m, b[m.to], pos.castling, pos.ep}
	b[m.fr] = EMPTY
	if m.flag == FlagEP {
		b[m.to-16*side] = EMPTY
	}
	if m.promo != 0 {
		b[m.to] = m.promo * side
	} else {
		b[m.to] = piece
	}
	if m.flag == FlagCastle {
		if m.to == 6 {
			b[7], b[5] = EMPTY, WR
		} else if m.to == 2 {
			b[0], b[3] = EMPTY, WR
		} else if m.to == 118 {
			b[119], b[117] = EMPTY, BR
		} else {
			b[112], b[115] = EMPTY, BR
		}
	}
	// castling-rights updates (king move, rook move, rook captured)
	if piece == WK {
		pos.castling &^= WKCastle | WQCastle
	} else if piece == BK {
		pos.castling &^= BKCastle | BQCastle
	}
	if m.fr == H1 || m.to == H1 {
		pos.castling &^= WKCastle
	}
	if m.fr == A1 || m.to == A1 {
		pos.castling &^= WQCastle
	}
	if m.fr == H8 || m.to == H8 {
		pos.castling &^= BKCastle
	}
	if m.fr == A8 || m.to == A8 {
		pos.castling &^= BQCastle
	}
	if m.flag == FlagDouble {
		pos.ep = m.fr + 16*side
	} else {
		pos.ep = -1
	}
	pos.side = -side
	return u
}

func unmake(pos *Position, u Undo) {
	b := &pos.board
	m := u.m
	side := -pos.side // the side that made the move
	piece := b[m.to]
	if m.promo != 0 {
		piece = side // was a pawn before the promotion
	}
	b[m.fr] = piece
	b[m.to] = u.captured
	if m.flag == FlagEP {
		b[m.to-16*side] = -side
	}
	if m.flag == FlagCastle {
		if m.to == 6 {
			b[7], b[5] = WR, EMPTY
		} else if m.to == 2 {
			b[0], b[3] = WR, EMPTY
		} else if m.to == 118 {
			b[119], b[117] = BR, EMPTY
		} else {
			b[112], b[115] = BR, EMPTY
		}
	}
	pos.castling = u.castling
	pos.ep = u.ep
	pos.side = side
}

func legalMoves(pos *Position, out []Move) int {
	tmp := *pos
	var pm [256]Move
	np := pseudoMoves(&tmp, pm[:])
	k := 0
	for i := 0; i < np; i++ {
		m := pm[i]
		if abs(tmp.board[m.to]) == 6 {
			continue // a move that captures a king is never legal
		}
		u := makeMove(&tmp, m)
		if !attacked(&tmp.board, kingSq(&tmp, -tmp.side), tmp.side) {
			out[k] = m
			k++
		}
		unmake(&tmp, u)
	}
	return k
}

func perft(pos *Position, depth int) int64 {
	if depth == 0 {
		return 1
	}
	var mv [256]Move
	n := legalMoves(pos, mv[:])
	if depth == 1 {
		return int64(n)
	}
	var total int64
	for i := 0; i < n; i++ {
		u := makeMove(pos, mv[i])
		total += perft(pos, depth-1)
		unmake(pos, u)
	}
	return total
}

// ── splitmix64 (native wrapping uint64 arithmetic) ──────────────────────

func splitmix64(x uint64) uint64 {
	x += 0x9E3779B97F4A7C15
	z := x
	z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9
	z = (z ^ (z >> 27)) * 0x94D049BB133111EB
	return z ^ (z >> 31)
}

// ── t* flow termination ─────────────────────────────────────────────────

func gcdI(a, b int) int {
	for b != 0 {
		a, b = b, a%b
	}
	return a
}

func lcmI(a, b int) int {
	return a / gcdI(a, b) * b
}

func tstar(w, h, a, b int) int {
	gx := gcdI(abs(a), w)
	if gx == 0 {
		gx = w
	}
	gy := gcdI(abs(b), h)
	if gy == 0 {
		gy = h
	}
	return lcmI(w/gx, h/gy)
}

// ── attack squares (threat field kernel) ────────────────────────────────

// Squares attacked by the piece on `sq`; `blocking` stops sliders at
// the first occupied square (the target square itself is included).
func attackSquares(b *[128]int, sq int, blocking bool, out []int) int {
	p := b[sq]
	ap := abs(p)
	n := 0
	if ap == 1 {
		sign := 1
		if p < 0 {
			sign = -1
		}
		fwd := 16 * sign
		for k := 0; k < 2; k++ {
			off := fwd - 1
			if k == 1 {
				off = fwd + 1
			}
			s := sq + off
			if s&0x88 == 0 {
				out[n] = s
				n++
			}
		}
	} else if ap == 2 || ap == 6 {
		var offs []int
		if ap == 2 {
			offs = knightOffs[:]
		} else {
			offs = kingDirs[:]
		}
		for i := 0; i < 8; i++ {
			s := sq + offs[i]
			if s&0x88 == 0 {
				out[n] = s
				n++
			}
		}
	} else {
		var dirs []int
		cnt := 4
		if ap == 4 {
			dirs = rookDirs[:]
		} else if ap == 3 {
			dirs = bishopDirs[:]
		} else {
			dirs = kingDirs[:]
			cnt = 8
		}
		for i := 0; i < cnt; i++ {
			off := dirs[i]
			s := sq + off
			for s&0x88 == 0 {
				out[n] = s
				n++
				if blocking && b[s] != EMPTY {
					break
				}
				s += off
			}
		}
	}
	return n
}

// D4 group acting on (file, rank) pairs:
//   0 id, 1 rot90, 2 rot180, 3 rot270,
//   4 mirror-h, 5 mirror-v, 6 main diagonal, 7 anti diagonal.
func d4Apply(g, f, r int) (int, int) {
	switch g {
	case 0:
		return f, r
	case 1:
		return r, 7 - f
	case 2:
		return 7 - f, 7 - r
	case 3:
		return 7 - r, f
	case 4:
		return 7 - f, r
	case 5:
		return f, 7 - r
	case 6:
		return r, f
	default:
		return 7 - r, 7 - f
	}
}

func equivarianceViolations(board *[128]int, side int) int {
	// Theta(g.p, g.c) == Theta(p, c) must hold for every g in D4
	var theta [128]int
	var buf [64]int
	for sq := 0; sq < 128; sq++ {
		if sq&0x88 != 0 {
			continue
		}
		p := board[sq]
		if p != EMPTY && (p > 0) == (side > 0) {
			n := attackSquares(board, sq, true, buf[:])
			for k := 0; k < n; k++ {
				theta[buf[k]]++
			}
		}
	}
	bad := 0
	for gi := 0; gi < 8; gi++ {
		var bg [128]int
		for sq := 0; sq < 128; sq++ {
			if sq&0x88 != 0 {
				continue
			}
			p := board[sq]
			if p != EMPTY {
				f2, r2 := d4Apply(gi, sq&7, sq>>4)
				bg[16*r2+f2] = p
			}
		}
		var tg [128]int
		for sq := 0; sq < 128; sq++ {
			if sq&0x88 != 0 {
				continue
			}
			p := bg[sq]
			if p != EMPTY && (p > 0) == (side > 0) {
				n := attackSquares(&bg, sq, true, buf[:])
				for k := 0; k < n; k++ {
					tg[buf[k]]++
				}
			}
		}
		for sq := 0; sq < 128; sq++ {
			if sq&0x88 != 0 {
				continue
			}
			f2, r2 := d4Apply(gi, sq&7, sq>>4)
			if tg[16*r2+f2] != theta[sq] {
				bad++
			}
		}
	}
	return bad
}

func knightNeighbour(a, b int) bool {
	df := abs((a & 7) - (b & 7))
	dr := abs((a >> 4) - (b >> 4))
	return (df == 1 && dr == 2) || (df == 2 && dr == 1)
}

// ── forced-mate search (same algorithm as the references) ───────────────
// mateDFS returns the length in plies of the shortest forced mate for
// the side to move within `depth` plies, or 0 if there is none.  The
// defender must have ALL replies lose; iterative deepening 1..max_depth
// in mateSearchPlies; early return once best <= 3.

func mateDFS(pos *Position, depth int) int {
	if depth <= 0 {
		return 0
	}
	var mv [256]Move
	n := legalMoves(pos, mv[:])
	best := 0
	for i := 0; i < n; i++ {
		u := makeMove(pos, mv[i])
		var rep [256]Move
		rn := legalMoves(pos, rep[:])
		if rn == 0 {
			mated := attacked(&pos.board, kingSq(pos, pos.side), -pos.side)
			unmake(pos, u)
			if mated {
				return 1
			}
			continue
		}
		if depth >= 2 {
			allMated := true
			worst := 0
			for j := 0; j < rn; j++ {
				u2 := makeMove(pos, rep[j])
				sub := mateDFS(pos, depth-2)
				unmake(pos, u2)
				if sub == 0 {
					allMated = false
					break
				}
				if sub > worst {
					worst = sub
				}
			}
			if allMated {
				unmake(pos, u)
				cand := worst + 2
				if best == 0 || cand < best {
					best = cand
					if best <= 3 {
						return best
					}
				}
				continue
			}
		}
		unmake(pos, u)
	}
	return best
}

func mateSearchPlies(pos *Position, maxDepth int) int {
	for depth := 1; depth <= maxDepth; depth++ {
		res := mateDFS(pos, depth)
		if res != 0 {
			return res
		}
	}
	return 0
}

func uciToMove(pos *Position, uci string) Move {
	fr := nameSq(uci[0:2])
	to := nameSq(uci[2:4])
	pr := 0
	if len(uci) > 4 {
		switch uci[4] {
		case 'q':
			pr = 5
		case 'n':
			pr = 2
		case 'r':
			pr = 4
		case 'b':
			pr = 3
		}
	}
	var mv [256]Move
	n := legalMoves(pos, mv[:])
	for i := 0; i < n; i++ {
		if mv[i].fr == fr && mv[i].to == to && mv[i].promo == pr {
			return mv[i]
		}
	}
	panic("illegal move " + uci)
}

func keyMatesIn2(pos *Position, frSq, toSq int) bool {
	// after the key move, EVERY defender reply must lose to a mate in 1
	var mv [256]Move
	n := legalMoves(pos, mv[:])
	for i := 0; i < n; i++ {
		m := mv[i]
		if m.fr == frSq && m.to == toSq {
			u := makeMove(pos, m)
			okAll := true
			var rep [256]Move
			rn := legalMoves(pos, rep[:])
			for j := 0; j < rn; j++ {
				u2 := makeMove(pos, rep[j])
				sub := mateSearchPlies(pos, 1)
				unmake(pos, u2)
				if sub != 1 {
					okAll = false
					break
				}
			}
			unmake(pos, u)
			return okAll
		}
	}
	return false
}

// ── Zobrist tables (chained splitmix64, Python generation order) ────────

// rows 0..5 = white P,N,B,R,Q,K ; rows 6..11 = black P,N,B,R,Q,K
func zobRow(piece int) int {
	if piece > 0 {
		return piece - 1
	}
	return 5 - piece
}

func fullHash(board *[128]int, side int, zob *[12][128]uint64, sideKey uint64) uint64 {
	h := uint64(0)
	for sq := 0; sq < 128; sq++ {
		if sq&0x88 != 0 {
			continue
		}
		p := board[sq]
		if p != EMPTY {
			h ^= zob[zobRow(p)][sq]
		}
	}
	if side == -1 {
		h ^= sideKey
	}
	return h
}

func okStr(ok bool) string {
	if ok {
		return "ok"
	}
	return "BAD"
}

// ── the battery ─────────────────────────────────────────────────────────

var gPass, gTotal int

func check(code string, ok bool, note string) {
	gTotal++
	if ok {
		gPass++
	}
	status := "FAIL"
	if ok {
		status = "PASS"
	}
	fmt.Printf("[%s] %s  %s\n", status, code, note)
}

func main() {

	// ── 1 board algebra ─────────────────────────────────────────────
	{
		seen := [8][8]bool{}
		cnt, small, big := 0, 0, 0
		v4idx := [4]int{0, 2, 6, 7} // id, rot180, diag, anti
		for f := 0; f < 8; f++ {
			for r := 0; r < 8; r++ {
				if seen[f][r] {
					continue
				}
				sz := 0
				var orbs [8][2]int
				for k := 0; k < 4; k++ {
					tf, tr := d4Apply(v4idx[k], f, r)
					dup := false
					for j := 0; j < sz; j++ {
						if orbs[j][0] == tf && orbs[j][1] == tr {
							dup = true
						}
					}
					if !dup {
						orbs[sz][0], orbs[sz][1] = tf, tr
						sz++
					}
					seen[tf][tr] = true
				}
				cnt++
				if sz == 2 {
					small++
				} else if sz == 4 {
					big++
				}
			}
		}
		dseen := [8][8]bool{}
		dcnt := 0
		for f := 0; f < 8; f++ {
			for r := 0; r < 8; r++ {
				if dseen[f][r] {
					continue
				}
				for gi := 0; gi < 8; gi++ {
					tf, tr := d4Apply(gi, f, r)
					dseen[tf][tr] = true
				}
				dcnt++
			}
		}
		// Burnside fixed-point counts, hard-coded as in the reference:
		// D4 = [id, rot90, rot180, rot270, mirh, mirv, diag, anti]
		bd4 := (64 + 0 + 0 + 0 + 0 + 0 + 8 + 8) / 8
		// V4 = [id, rot180, diag, anti]
		bv4 := (64 + 0 + 8 + 8) / 4
		note := fmt.Sprintf("V4=%d(%d+%d) D4=%d burnside %d/%d",
			cnt, small, big, dcnt, bv4, bd4)
		check("C1", cnt == 20 && small == 8 && big == 12 && dcnt == 10 &&
			bd4 == 10 && bv4 == 20, note)
	}

	// ── 2 move-graph census ─────────────────────────────────────────
	{
		board := [128]int{}
		types := [5]int{WR, WB, WN, WK, WQ}
		directed := [5]int{}
		var buf [64]int
		for t := 0; t < 5; t++ {
			for sq := 0; sq < 128; sq++ {
				if sq&0x88 != 0 {
					continue
				}
				board[sq] = types[t]
				directed[t] += attackSquares(&board, sq, true, buf[:])
				board[sq] = EMPTY
			}
		}
		note := fmt.Sprintf("edges R%d B%d N%d K%d Q%d",
			directed[0]/2, directed[1]/2, directed[2]/2,
			directed[3]/2, directed[4]/2)
		check("C2", directed[0]/2 == 448 && directed[1]/2 == 280 &&
			directed[2]/2 == 168 && directed[3]/2 == 210 &&
			directed[4]/2 == 728, note)
	}

	// ── 3 mobility census ───────────────────────────────────────────
	{
		board := [128]int{}
		types := [5]int{WR, WB, WN, WK, WQ}
		sums := [5]int{}
		maxima := [5]int{}
		var buf [64]int
		for t := 0; t < 5; t++ {
			for sq := 0; sq < 128; sq++ {
				if sq&0x88 != 0 {
					continue
				}
				board[sq] = types[t]
				m := attackSquares(&board, sq, false, buf[:])
				sums[t] += m
				if m > maxima[t] {
					maxima[t] = m
				}
				board[sq] = EMPTY
			}
		}
		bishopOK := true
		for sq := 0; sq < 128; sq++ {
			if sq&0x88 != 0 {
				continue
			}
			f, r := sq&7, sq>>4
			board[sq] = WB
			m := attackSquares(&board, sq, false, buf[:])
			board[sq] = EMPTY
			if m != 14-abs(f-r)-abs(f+r-7) {
				bishopOK = false
			}
		}
		note := fmt.Sprintf("sums R%d B%d N%d K%d Q%d; max %d/%d/%d/%d/%d",
			sums[0], sums[1], sums[2], sums[3], sums[4],
			maxima[0], maxima[1], maxima[2], maxima[3], maxima[4])
		check("C3", sums == [5]int{896, 560, 336, 420, 1456} &&
			maxima == [5]int{14, 13, 8, 8, 27} && bishopOK, note)
	}

	// ── 4 flow termination ──────────────────────────────────────────
	{
		w9 := [9]int{8, 8, 8, 8, 8, 8, 48, 24, 12}
		h9 := [9]int{8, 8, 8, 8, 8, 8, 48, 36, 12}
		a9 := [9]int{1, 3, 2, 1, 1, 2, 1, 3, 4}
		b9 := [9]int{1, 5, 2, 2, 0, 1, 1, 5, 6}
		e9 := [9]int{8, 8, 4, 8, 8, 8, 48, 72, 6}
		got := [9]int{}
		ok := true
		for k := 0; k < 9; k++ {
			got[k] = tstar(w9[k], h9[k], a9[k], b9[k])
			if got[k] != e9[k] {
				ok = false
			}
		}
		note := fmt.Sprintf("9 t* cases: %d,%d,%d,%d,%d",
			got[0], got[1], got[2], got[3], got[4])
		check("C4", ok, note)
	}

	// ── 5 perft identities ──────────────────────────────────────────
	{
		p := &Position{}
		setFen(p, "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
		p1 := perft(p, 1)
		p2 := perft(p, 2)
		p3 := perft(p, 3)
		p4 := perft(p, 4)
		note := fmt.Sprintf("perft %d %d %d %d", p1, p2, p3, p4)
		check("C5", p1 == 20 && p2 == 400 && p3 == 8902 && p4 == 197281, note)
	}

	// ── 6 threat fields ─────────────────────────────────────────────
	{
		back := [8]int{WR, WN, WB, WQ, WK, WB, WN, WR}
		pl := [128]int{}
		for f := 0; f < 8; f++ {
			pl[f] = back[f]
			pl[112+f] = -back[f]
		}
		vw := equivarianceViolations(&pl, 1)
		vb := equivarianceViolations(&pl, -1)
		st := [128]int{}
		for f := 0; f < 8; f++ {
			st[f] = back[f]
			st[112+f] = -back[f]
			st[16+f] = WP
			st[96+f] = BP
		}
		anomaly := equivarianceViolations(&st, 1) +
			equivarianceViolations(&st, -1)
		note := fmt.Sprintf("pawnless violations %d/%d, pawn anomaly %d",
			vw, vb, anomaly)
		check("C6", vw == 0 && vb == 0 && anomaly == 176, note)
	}

	// ── 7 kinetic energy ────────────────────────────────────────────
	{
		p := &Position{}
		setFen(p, "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
		var mv [256]Move
		m0 := legalMoves(p, mv[:])
		key := uciToMove(p, "e2e4")
		u := makeMove(p, key)
		p.side = 1 // count White's mobility after 1.e4
		m1 := legalMoves(p, mv[:])
		p.side = -1
		unmake(p, u)
		note := fmt.Sprintf("White mobility %d -> %d after 1.e4", m0, m1)
		check("C7", m0 == 20 && m1 == 30, note)
	}

	// ── 8 mate certificates ─────────────────────────────────────────
	{
		p := &Position{}
		setFen(p, "kbK5/pp6/1P6/8/8/8/8/R7 w - - 0 1")
		pliesM := mateSearchPlies(p, 4)
		keyOK := keyMatesIn2(p, nameSq("a1"), nameSq("a6"))
		setFen(p, "7k/8/8/8/8/8/R7/1R4K1 w - - 0 1")
		pliesL := mateSearchPlies(p, 4)
		setFen(p, "7k/8/5N1K/8/8/8/8/6R1 w - - 0 1")
		pliesN := mateSearchPlies(p, 2)
		// N+R mate in 1 with key g1g8: after Rg8 there are no replies
		// and the black king is attacked
		nrKey := false
		{
			var mv [256]Move
			n := legalMoves(p, mv[:])
			g1, g8 := nameSq("g1"), nameSq("g8")
			for i := 0; i < n; i++ {
				if mv[i].fr == g1 && mv[i].to == g8 {
					u := makeMove(p, mv[i])
					var rep [256]Move
					rn := legalMoves(p, rep[:])
					mated := rn == 0 &&
						attacked(&p.board, kingSq(p, p.side), -p.side)
					unmake(p, u)
					nrKey = mated
					break
				}
			}
		}
		note := fmt.Sprintf("morphy %d(key a1a6) ladder %d nr %d(key g1g8)",
			pliesM, pliesL, pliesN)
		check("C8", pliesM == 3 && keyOK && pliesL == 3 && pliesN == 1 && nrKey, note)
	}

	// ── 9 zobrist incrementality (fixed playout) ─────────────────────
	{
		var zob [12][128]uint64
		state := uint64(1)
		for row := 0; row < 12; row++ {
			for sq := 0; sq < 128; sq++ {
				state = splitmix64(state)
				zob[row][sq] = state
			}
		}
		sideKey := splitmix64(state)
		p := &Position{}
		setFen(p, "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
		h := fullHash(&p.board, p.side, &zob, sideKey)
		incOK := h == fullHash(&p.board, 1, &zob, sideKey)
		playout := [10]string{"e2e4", "e7e5", "g1f3", "b8c6", "f1b5",
			"g8f6", "e1g1", "f8c5", "d2d3", "d7d6"}
		for k := 0; k < 10 && incOK; k++ {
			key := uciToMove(p, playout[k])
			piece := p.board[key.fr]
			captured := p.board[key.to]
			h ^= zob[zobRow(piece)][key.fr]
			if captured != EMPTY {
				h ^= zob[zobRow(captured)][key.to]
			}
			if key.promo != 0 {
				h ^= zob[zobRow(key.promo*p.side)][key.to] ^ zob[zobRow(piece)][key.to]
			} else {
				h ^= zob[zobRow(piece)][key.to]
			}
			side := p.side
			if key.flag == FlagEP {
				// en passant: remove the captured pawn from the hash
				capSq := key.to - 16*side
				h ^= zob[zobRow(p.board[capSq])][capSq]
			}
			if key.flag == FlagCastle {
				// castling: move the rook in the hash
				if key.to == 6 {
					h ^= zob[zobRow(WR)][7] ^ zob[zobRow(WR)][5]
				} else if key.to == 2 {
					h ^= zob[zobRow(WR)][0] ^ zob[zobRow(WR)][3]
				} else if key.to == 118 {
					h ^= zob[zobRow(BR)][119] ^ zob[zobRow(BR)][117]
				} else {
					h ^= zob[zobRow(BR)][112] ^ zob[zobRow(BR)][115]
				}
			}
			makeMove(p, key)
			h ^= sideKey
			if h != fullHash(&p.board, p.side, &zob, sideKey) {
				incOK = false
			}
		}
		smOK := splitmix64(1) == 0x910A2DEC89025CC1 &&
			splitmix64(2) == 0x975835DE1C9756CE &&
			splitmix64(3) == 0x1D0B14E4DB018FED
		note := fmt.Sprintf("incremental hash over 10 plies, splitmix vectors %s",
			okStr(smOK))
		check("C9", incOK && smOK, note)
	}

	// ── 10 knight tour certificate ──────────────────────────────────
	{
		var tour [64]int
		for i := 0; i < 64; i++ {
			tour[i] = nameSq(knightTour[i])
		}
		seenT := [128]bool{}
		distinct := true
		for i := 0; i < 64; i++ {
			if seenT[tour[i]] {
				distinct = false
			}
			seenT[tour[i]] = true
		}
		closed := true
		for i := 0; i < 64; i++ {
			if !knightNeighbour(tour[i], tour[(i+1)%64]) {
				closed = false
				break
			}
		}
		note := fmt.Sprintf("tour 64 distinct cells, closure %s", okStr(closed))
		check("C10", distinct && closed, note)
	}

	fmt.Printf("verdict: %d/%d\n", gPass, gTotal)
	if gPass != gTotal {
		os.Exit(1)
	}
}

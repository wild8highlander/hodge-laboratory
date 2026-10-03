/*
  ChessCore.java — POLYGLOT VERIFICATION CORE (Java implementation)

  Program author: Isaev Iskhak Khamzatovich
  Repository: github.com/wild8highlander/chess-dynamics-lab
  License: individual exclusive license (see LICENSE)

  One core, seven languages: Python, C, Rust, Go, Julia, JavaScript and
  Java (this file) implement the SAME 10-check battery and print the SAME
  [PASS]/[FAIL] table. Every check is exact and deterministic:

      1  board algebra        V4 orbits 20 (8x2 + 12x4), D4 orbits 10 (Burnside)
      2  move-graph census    edges R448 B280 N168 K210 Q728
      3  mobility census      sums R896 B560 N336 K420 Q1456, max 14/13/8/8/27
      4  flow termination     t* = lcm(W/gcd(a,W), H/gcd(b,H)) on 9 cases
      5  perft identities     20 / 400 / 8902 / 197281 from the initial position
      6  threat fields        D4-equivariance (pawnless) + pawn anomaly 176
      7  kinetic energy       initial mobility 20, after 1.e4 mobility 30
      8  mate certificates    Morphy m2 (a1a6), ladder m2, N+R m1 (g1g8)
      9  Zobrist hashing      incremental hash over a fixed playout + splitmix64
     10  knight tour          the frozen closed tour: 64 cells, closure move

  Pure JDK, single file, default package (java.util only). No randomness,
  no floating point.

  Pitfalls honored (see polyglot/c/chess_core.c and polyglot/python/chess_core.py):
    - piece codes are explicit constants: white 1..6, black -1..-6;
    - the queen slides in ALL 8 directions (KING_DIRS doubles as the queen
      direction set), rook/bishop in their 4, knights/kings 8 offsets;
    - en passant is generated only from the correct pawn rank (rank index 4
      for White, 3 for Black; rank 0 = White's first rank);
    - a pseudo move that would capture a king is never legal;
    - castling rights are updated when the king/rook moves or when a rook
      square is captured;
    - splitmix64 / Zobrist keys use native 64-bit long arithmetic: `long`
      multiplication wraps naturally and >>> is the logical right shift;
      all hash constants are long hex literals (high bit allowed).

  Build/run (from the repository root):
      javac java/ChessCore.java && java -cp java ChessCore
  (expects the verdict 10/10)
*/
import java.util.Arrays;
import java.util.HashSet;

public class ChessCore {

    // ── board (0x88) ──────────────────────────────────────────────────
    static final int EMPTY = 0;
    static final int WP = 1, WN = 2, WB = 3, WR = 4, WQ = 5, WK = 6;
    static final int BP = -1, BN = -2, BB = -3, BR = -4, BQ = -5, BK = -6;
    static final int[] KNIGHT_OFFS = {31, 33, 14, 18, -31, -33, -14, -18};
    static final int[] BISHOP_DIRS = {15, 17, -15, -17};
    static final int[] ROOK_DIRS = {16, -16, 1, -1};
    static final int[] KING_DIRS = {15, 16, 17, 1, -15, -16, -17, -1};  // queen uses all 8
    static final int[] PROMOS = {5, 2, 4, 3};
    static final int A1 = 0, E1 = 4, H1 = 7;
    static final int A8 = 112, E8 = 116, H8 = 119;
    static final int WK_CASTLE = 1, WQ_CASTLE = 2, BK_CASTLE = 4, BQ_CASTLE = 8;
    static final int FLAG_NORMAL = 0, FLAG_DOUBLE = 1, FLAG_EP = 2, FLAG_CASTLE = 3;
    static final String FILES = "abcdefgh";
    static final int[] SQUARES = new int[64];

    static {
        int k = 0;
        for (int r = 0; r < 8; r++)
            for (int f = 0; f < 8; f++)
                SQUARES[k++] = 16 * r + f;
    }

    static int charPiece(char ch) {
        switch (ch) {
            case 'P': return WP;
            case 'N': return WN;
            case 'B': return WB;
            case 'R': return WR;
            case 'Q': return WQ;
            case 'K': return WK;
            case 'p': return BP;
            case 'n': return BN;
            case 'b': return BB;
            case 'r': return BR;
            case 'q': return BQ;
            case 'k': return BK;
        }
        return EMPTY;
    }

    /* 0x88 square of a 2-char algebraic name like "e4" (rank 0 = White's 1st) */
    static int nameSq(String s) {
        return 16 * (s.charAt(1) - '1') + FILES.indexOf(s.charAt(0));
    }

    static class Pos {
        int[] board = new int[128];
        int side = 1;        // 1 = White, -1 = Black
        int castling = 0;
        int ep = -1;

        Pos() {}

        Pos(Pos other) {    // deep copy
            board = new int[128];
            System.arraycopy(other.board, 0, board, 0, 128);
            side = other.side;
            castling = other.castling;
            ep = other.ep;
        }
    }

    static Pos setFen(Pos p, String placement, String sideCh, String castling, String ep) {
        Arrays.fill(p.board, EMPTY);
        int rank = 7, file = 0;
        for (int i = 0; i < placement.length(); i++) {
            char ch = placement.charAt(i);
            if (ch == '/') { rank--; file = 0; continue; }
            if (ch >= '1' && ch <= '8') { file += ch - '0'; continue; }
            p.board[16 * rank + file] = charPiece(ch);
            file++;
        }
        p.side = sideCh.equals("w") ? 1 : -1;
        p.castling = 0;
        if (!castling.equals("-")) {
            for (int i = 0; i < castling.length(); i++) {
                char ch = castling.charAt(i);
                p.castling |= ch == 'K' ? WK_CASTLE : ch == 'Q' ? WQ_CASTLE
                            : ch == 'k' ? BK_CASTLE : BQ_CASTLE;
            }
        }
        p.ep = ep.equals("-") ? -1 : nameSq(ep);
        return p;
    }

    /* is `sq` attacked by side `by` (1 = White, -1 = Black)? */
    static boolean attacked(int[] b, int sq, int by) {
        int[] poffs = by == 1 ? new int[]{-15, -17} : new int[]{15, 17};
        for (int off : poffs) {
            int s = sq + off;
            if ((s & 0x88) == 0 && b[s] == by) return true;
        }
        for (int off : KNIGHT_OFFS) {
            int s = sq + off;
            if ((s & 0x88) == 0 && b[s] == 2 * by) return true;
        }
        for (int off : KING_DIRS) {
            int s = sq + off;
            if ((s & 0x88) == 0 && b[s] == 6 * by) return true;
        }
        int[][] dsets = {BISHOP_DIRS, ROOK_DIRS};
        int[][] kinds = {{3, 5}, {4, 5}};
        for (int d = 0; d < 2; d++) {
            for (int off : dsets[d]) {
                int s = sq + off;
                while ((s & 0x88) == 0) {
                    int p = b[s];
                    if (p != EMPTY) {
                        if ((p > 0) == (by > 0)
                                && (Math.abs(p) == kinds[d][0] || Math.abs(p) == kinds[d][1]))
                            return true;
                        break;
                    }
                    s += off;
                }
            }
        }
        return false;
    }

    static int kingSq(Pos p, int side) {
        int t = 6 * side;
        for (int sq : SQUARES)
            if (p.board[sq] == t) return sq;
        throw new RuntimeException("king missing");
    }

    /* move encoding: fr | to<<7 | promo<<14 | flag<<18 (same as the reference) */
    static int enc(int fr, int to, int promo, int flag) {
        return fr | (to << 7) | (promo << 14) | (flag << 18);
    }
    static int enc(int fr, int to) { return enc(fr, to, 0, 0); }
    static int mFrom(int m) { return m & 127; }
    static int mTo(int m) { return (m >> 7) & 127; }
    static int mPromo(int m) { return (m >> 14) & 7; }
    static int mFlag(int m) { return (m >> 18) & 3; }

    static int[] pseudoMoves(Pos p) {
        int[] b = p.board;
        int side = p.side;
        int[] moves = new int[256];
        int n = 0;
        for (int fr : SQUARES) {
            int piece = b[fr];
            if (piece == EMPTY || (piece > 0) != (side > 0)) continue;
            int ap = Math.abs(piece);
            if (ap == 1) {
                int fwd = 16 * side;
                int rank = fr >> 4;
                int promoRank = side == 1 ? 6 : 1;
                int startRank = side == 1 ? 1 : 6;
                int s = fr + fwd;
                if ((s & 0x88) == 0 && b[s] == EMPTY) {
                    if (rank == promoRank) {
                        for (int pr : PROMOS) moves[n++] = enc(fr, s, pr, 0);
                    } else {
                        moves[n++] = enc(fr, s);
                        if (rank == startRank && b[s + fwd] == EMPTY)
                            moves[n++] = enc(fr, s + fwd, 0, FLAG_DOUBLE);
                    }
                }
                for (int k = -1; k <= 1; k += 2) {
                    int s2 = fr + fwd + k;
                    if ((s2 & 0x88) != 0) continue;
                    int q = b[s2];
                    if (q != EMPTY && (q > 0) != (side > 0)) {
                        if (rank == promoRank) {
                            for (int pr : PROMOS) moves[n++] = enc(fr, s2, pr, 0);
                        } else {
                            moves[n++] = enc(fr, s2);
                        }
                    } else if (s2 == p.ep && q == EMPTY && rank == (side == 1 ? 4 : 3)) {
                        moves[n++] = enc(fr, s2, 0, FLAG_EP);
                    }
                }
            } else if (ap == 2 || ap == 6) {
                int[] offs = ap == 2 ? KNIGHT_OFFS : KING_DIRS;
                for (int off : offs) {
                    int s = fr + off;
                    if ((s & 0x88) != 0) continue;
                    int q = b[s];
                    if (q == EMPTY || (q > 0) != (side > 0))
                        moves[n++] = enc(fr, s);
                }
            } else {
                int[] dirs = ap == 4 ? ROOK_DIRS : ap == 3 ? BISHOP_DIRS : KING_DIRS;
                for (int off : dirs) {
                    int s = fr + off;
                    while ((s & 0x88) == 0) {
                        int q = b[s];
                        if (q == EMPTY) {
                            moves[n++] = enc(fr, s);
                        } else {
                            if ((q > 0) != (side > 0))
                                moves[n++] = enc(fr, s);
                            break;
                        }
                        s += off;
                    }
                }
            }
        }
        /* castling (king not in check, path squares empty and not attacked) */
        if (side == 1) {
            if ((p.castling & WK_CASTLE) != 0 && b[5] == EMPTY && b[6] == EMPTY
                    && b[4] == WK && b[7] == WR
                    && !attacked(b, 4, -1) && !attacked(b, 5, -1)
                    && !attacked(b, 6, -1))
                moves[n++] = enc(E1, 6, 0, FLAG_CASTLE);
            if ((p.castling & WQ_CASTLE) != 0 && b[3] == EMPTY && b[2] == EMPTY
                    && b[1] == EMPTY && b[4] == WK && b[0] == WR
                    && !attacked(b, 4, -1) && !attacked(b, 3, -1)
                    && !attacked(b, 2, -1))
                moves[n++] = enc(E1, 2, 0, FLAG_CASTLE);
        } else {
            if ((p.castling & BK_CASTLE) != 0 && b[117] == EMPTY && b[118] == EMPTY
                    && b[116] == BK && b[119] == BR
                    && !attacked(b, 116, 1) && !attacked(b, 117, 1)
                    && !attacked(b, 118, 1))
                moves[n++] = enc(E8, 118, 0, FLAG_CASTLE);
            if ((p.castling & BQ_CASTLE) != 0 && b[115] == EMPTY && b[114] == EMPTY
                    && b[113] == EMPTY && b[116] == BK && b[112] == BR
                    && !attacked(b, 116, 1) && !attacked(b, 115, 1)
                    && !attacked(b, 114, 1))
                moves[n++] = enc(E8, 114, 0, FLAG_CASTLE);
        }
        return Arrays.copyOf(moves, n);
    }

    static class Undo {
        int m, captured, castling, ep;
    }

    static void make(Pos p, int m, Undo u) {
        int[] b = p.board;
        int fr = mFrom(m), to = mTo(m);
        int promo = mPromo(m), flag = mFlag(m);
        int side = p.side;
        int piece = b[fr];
        u.m = m;
        u.captured = b[to];
        u.castling = p.castling;
        u.ep = p.ep;
        b[fr] = EMPTY;
        if (flag == FLAG_EP) b[to - 16 * side] = EMPTY;
        b[to] = promo != 0 ? promo * side : piece;
        if (flag == FLAG_CASTLE) {
            if (to == 6) { b[7] = EMPTY; b[5] = WR; }
            else if (to == 2) { b[0] = EMPTY; b[3] = WR; }
            else if (to == 118) { b[119] = EMPTY; b[117] = BR; }
            else { b[112] = EMPTY; b[115] = BR; }
        }
        if (piece == WK) p.castling &= ~(WK_CASTLE | WQ_CASTLE);
        else if (piece == BK) p.castling &= ~(BK_CASTLE | BQ_CASTLE);
        if (fr == H1 || to == H1) p.castling &= ~WK_CASTLE;
        if (fr == A1 || to == A1) p.castling &= ~WQ_CASTLE;
        if (fr == H8 || to == H8) p.castling &= ~BK_CASTLE;
        if (fr == A8 || to == A8) p.castling &= ~BQ_CASTLE;
        p.ep = flag == FLAG_DOUBLE ? fr + 16 * side : -1;
        p.side = -side;
    }

    static void unmake(Pos p, Undo u) {
        int[] b = p.board;
        int fr = mFrom(u.m), to = mTo(u.m);
        int promo = mPromo(u.m), flag = mFlag(u.m);
        int side = -p.side;
        int piece = b[to];
        if (promo != 0) piece = side;
        b[fr] = piece;
        b[to] = u.captured;
        if (flag == FLAG_EP) b[to - 16 * side] = -side;
        if (flag == FLAG_CASTLE) {
            if (to == 6) { b[7] = WR; b[5] = EMPTY; }
            else if (to == 2) { b[0] = WR; b[3] = EMPTY; }
            else if (to == 118) { b[119] = BR; b[117] = EMPTY; }
            else { b[112] = BR; b[115] = EMPTY; }
        }
        p.castling = u.castling;
        p.ep = u.ep;
        p.side = side;
    }

    static int[] legalMoves(Pos p) {
        Pos tmp = new Pos(p);
        int[] pseudo = pseudoMoves(tmp);
        int[] out = new int[pseudo.length];
        int n = 0;
        for (int m : pseudo) {
            if (Math.abs(tmp.board[mTo(m)]) == 6) continue;  // king capture is never legal
            Undo u = new Undo();
            make(tmp, m, u);
            if (!attacked(tmp.board, kingSq(tmp, -tmp.side), tmp.side))
                out[n++] = m;
            unmake(tmp, u);
        }
        return Arrays.copyOf(out, n);
    }

    static int uciToMove(Pos pos, String u) {
        int fr = nameSq(u.substring(0, 2));
        int to = nameSq(u.substring(2, 4));
        int pr = 0;
        if (u.length() >= 5) {
            char c = u.charAt(4);
            pr = c == 'q' ? 5 : c == 'n' ? 2 : c == 'r' ? 4 : c == 'b' ? 3 : 0;
        }
        for (int m : legalMoves(pos))
            if (mFrom(m) == fr && mTo(m) == to && mPromo(m) == pr) return m;
        throw new RuntimeException("illegal move " + u);
    }

    static long perft(Pos p, int d) {
        if (d == 0) return 1;
        long n = 0;
        for (int m : legalMoves(p)) {
            Undo u = new Undo();
            make(p, m, u);
            n += perft(p, d - 1);
            unmake(p, u);
        }
        return n;
    }

    // ── splitmix64 (native 64-bit arithmetic: * wraps, >>> is logical) ─
    static long splitmix64(long x) {
        x += 0x9E3779B97F4A7C15L;
        long z = x;
        z = (z ^ (z >>> 30)) * 0xBF58476D1CE4E5B9L;
        z = (z ^ (z >>> 27)) * 0x94D049BB133111EBL;
        return z ^ (z >>> 31);
    }

    // ── algebra helpers (D4 / V4 groups on (file, rank) pairs) ────────
    interface GFn {
        int[] apply(int f, int r);
    }

    static final GFn[] D4 = {
        (f, r) -> new int[]{f, r},
        (f, r) -> new int[]{r, 7 - f},
        (f, r) -> new int[]{7 - f, 7 - r},
        (f, r) -> new int[]{7 - r, f},
        (f, r) -> new int[]{7 - f, r},
        (f, r) -> new int[]{f, 7 - r},
        (f, r) -> new int[]{r, f},
        (f, r) -> new int[]{7 - r, 7 - f},
    };
    static final GFn[] V4 = {
        (f, r) -> new int[]{f, r},
        (f, r) -> new int[]{7 - f, 7 - r},
        (f, r) -> new int[]{r, f},
        (f, r) -> new int[]{7 - r, 7 - f},
    };

    /* returns {orbit count, count of size-2 orbits, count of size-4 orbits} */
    static int[] orbits(GFn[] group) {
        HashSet<Integer> seen = new HashSet<>();
        int cnt = 0, small = 0, big = 0;
        for (int f = 0; f < 8; f++) {
            for (int r = 0; r < 8; r++) {
                if (seen.contains(f * 8 + r)) continue;
                HashSet<Integer> orb = new HashSet<>();
                for (GFn g : group) {
                    int[] t = g.apply(f, r);
                    orb.add(t[0] * 8 + t[1]);
                }
                seen.addAll(orb);
                cnt++;
                if (orb.size() == 2) small++;
                else if (orb.size() == 4) big++;
            }
        }
        return new int[]{cnt, small, big};
    }

    static int gcdI(int a, int b) {
        while (b != 0) { int t = a % b; a = b; b = t; }
        return a;
    }

    static long lcmL(long a, long b) { return a / gcdI((int) a, (int) b) * b; }

    static long tstar(int W, int H, int a, int b) {
        int gx = gcdI(Math.abs(a), W); if (gx == 0) gx = W;
        int gy = gcdI(Math.abs(b), H); if (gy == 0) gy = H;
        return lcmL(W / gx, H / gy);
    }

    /* squares attacked by the piece on sq; blocking stops sliders at blockers */
    static int attackSquares(int[] b, int sq, boolean blocking, int[] out) {
        int p = b[sq], ap = Math.abs(p), n = 0;
        if (ap == 1) {
            int fwd = 16 * (p > 0 ? 1 : -1);
            for (int k = -1; k <= 1; k += 2) {
                int s = sq + fwd + k;
                if ((s & 0x88) == 0) out[n++] = s;
            }
        } else if (ap == 2 || ap == 6) {
            int[] offs = ap == 2 ? KNIGHT_OFFS : KING_DIRS;
            for (int off : offs) {
                int s = sq + off;
                if ((s & 0x88) == 0) out[n++] = s;
            }
        } else {
            int[] dirs = ap == 4 ? ROOK_DIRS : ap == 3 ? BISHOP_DIRS : KING_DIRS;
            for (int off : dirs) {
                int s = sq + off;
                while ((s & 0x88) == 0) {
                    out[n++] = s;
                    if (blocking && b[s] != EMPTY) break;
                    s += off;
                }
            }
        }
        return n;
    }

    /* violations of Theta(g.p, g.c) == Theta(p, c) over g in D4 */
    static int equivarianceViolations(int[] board, int side) {
        int[] theta = new int[128];
        int[] buf = new int[64];
        for (int sq : SQUARES) {
            int p = board[sq];
            if (p != EMPTY && (p > 0) == (side > 0)) {
                int n = attackSquares(board, sq, true, buf);
                for (int k = 0; k < n; k++) theta[buf[k]]++;
            }
        }
        int bad = 0;
        for (int gi = 0; gi < 8; gi++) {
            int[] bg = new int[128];
            for (int sq : SQUARES) {
                int p = board[sq];
                if (p != EMPTY) {
                    int[] t = D4[gi].apply(sq & 7, sq >> 4);
                    bg[16 * t[1] + t[0]] = p;
                }
            }
            int[] tg = new int[128];
            for (int sq : SQUARES) {
                int p = bg[sq];
                if (p != EMPTY && (p > 0) == (side > 0)) {
                    int n = attackSquares(bg, sq, true, buf);
                    for (int k = 0; k < n; k++) tg[buf[k]]++;
                }
            }
            for (int sq : SQUARES) {
                int[] t = D4[gi].apply(sq & 7, sq >> 4);
                if (tg[16 * t[1] + t[0]] != theta[sq]) bad++;
            }
        }
        return bad;
    }

    static final String[] KNIGHT_TOUR = {
        "f5", "h4", "g2", "e1", "c2", "a1", "b3", "c1",
        "a2", "b4", "a6", "b8", "d7", "f8", "h7", "g5",
        "h3", "g1", "e2", "g3", "h1", "f2", "d1", "b2",
        "d3", "f4", "h5", "g7", "e8", "f6", "g8", "h6",
        "g4", "h2", "f1", "e3", "d5", "c7", "a8", "b6",
        "a4", "c3", "b1", "a3", "b5", "a7", "c8", "e7",
        "g6", "h8", "f7", "e5", "f3", "d2", "c4", "a5",
        "c6", "d4", "e6", "d8", "b7", "c5", "e4", "d6"
    };

    static boolean knightNeighbour(int a, int b) {
        int df = Math.abs((a & 7) - (b & 7));
        int dr = Math.abs((a >> 4) - (b >> 4));
        return (df == 1 && dr == 2) || (df == 2 && dr == 1);
    }

    /* forced-mate search: shortest mate for the side to move, 0 = none */
    static int mateSearchPlies(Pos pos, int maxDepth) {
        for (int depth = 1; depth <= maxDepth; depth++) {
            int res = mateDfs(pos, depth);
            if (res != 0) return res;
        }
        return 0;
    }

    static int mateDfs(Pos pos, int depth) {
        if (depth <= 0) return 0;
        int best = 0;
        Undo u = new Undo();
        for (int m : legalMoves(pos)) {
            make(pos, m, u);
            int[] replies = legalMoves(pos);
            if (replies.length == 0) {
                boolean mated = attacked(pos.board, kingSq(pos, pos.side), -pos.side);
                unmake(pos, u);
                if (mated) return 1;
                continue;
            }
            if (depth >= 2) {
                boolean allMated = true;
                int worst = 0;
                for (int r : replies) {
                    Undo u2 = new Undo();
                    make(pos, r, u2);
                    int sub = mateDfs(pos, depth - 2);
                    unmake(pos, u2);
                    if (sub == 0) { allMated = false; break; }
                    if (sub > worst) worst = sub;
                }
                if (allMated) {
                    unmake(pos, u);
                    int cand = worst + 2;
                    if (best == 0 || cand < best) {
                        best = cand;
                        if (best <= 3) return best;
                    }
                    continue;
                }
            }
            unmake(pos, u);
        }
        return best;
    }

    /* every black reply to the key move must walk into a mate in 1 */
    static boolean keyMatesIn2(Pos pos, int frSq, int toSq) {
        for (int m : legalMoves(pos)) {
            if (mFrom(m) == frSq && mTo(m) == toSq) {
                Undo u = new Undo();
                make(pos, m, u);
                boolean okAll = true;
                for (int r : legalMoves(pos)) {
                    Undo u2 = new Undo();
                    make(pos, r, u2);
                    int sub = mateSearchPlies(pos, 1);
                    unmake(pos, u2);
                    if (sub != 1) { okAll = false; break; }
                }
                unmake(pos, u);
                return okAll;
            }
        }
        return false;
    }

    /* Zobrist table row for a piece code: 1..6 -> 0..5, -1..-6 -> 6..11 */
    static int zrow(int piece) {
        return piece > 0 ? piece - 1 : 5 - piece;
    }

    static long fullHash(int[] b, int side, long[][] zob, long sideKey) {
        long h = 0L;
        for (int sq : SQUARES)
            if (b[sq] != EMPTY) h ^= zob[zrow(b[sq])][sq];
        if (side == -1) h ^= sideKey;
        return h;
    }

    // ── the battery ───────────────────────────────────────────────────
    static int gPass = 0, gTotal = 0;

    static void check(String code, boolean ok, String note) {
        gTotal++;
        gPass += ok ? 1 : 0;
        System.out.println("[" + (ok ? "PASS" : "FAIL") + "] " + code + "  " + note);
    }

    public static void main(String[] args) {
        String note;

        /* 1 board algebra */
        {
            int[] v4 = orbits(V4);
            int cnt = v4[0], small = v4[1], big = v4[2];
            int dcnt = orbits(D4)[0];
            int bd4 = (64 + 0 + 0 + 0 + 0 + 0 + 8 + 8) / 8;
            int bv4 = (64 + 0 + 8 + 8) / 4;
            note = "V4=" + cnt + "(" + small + "+" + big + ") D4=" + dcnt
                 + " burnside " + bv4 + "/" + bd4;
            check("C1", cnt == 20 && small == 8 && big == 12 && dcnt == 10
                     && bd4 == 10 && bv4 == 20, note);
        }

        /* 2 move-graph census */
        int[] board = new int[128];
        int[] types = {WR, WB, WN, WK, WQ};
        int[] directed = new int[5];
        int[] buf = new int[64];
        {
            for (int i = 0; i < 5; i++)
                for (int sq : SQUARES) {
                    board[sq] = types[i];
                    directed[i] += attackSquares(board, sq, true, buf);
                    board[sq] = EMPTY;
                }
            note = "edges R" + (directed[0] / 2) + " B" + (directed[1] / 2)
                 + " N" + (directed[2] / 2) + " K" + (directed[3] / 2)
                 + " Q" + (directed[4] / 2);
            check("C2", directed[0] / 2 == 448 && directed[1] / 2 == 280
                     && directed[2] / 2 == 168 && directed[3] / 2 == 210
                     && directed[4] / 2 == 728, note);
        }

        /* 3 mobility census */
        {
            int[] sums = directed;   // single piece on an empty board: no blockers
            int[] maxima = new int[5];
            for (int i = 0; i < 5; i++)
                for (int sq : SQUARES) {
                    board[sq] = types[i];
                    int mm = attackSquares(board, sq, false, buf);
                    if (mm > maxima[i]) maxima[i] = mm;
                    board[sq] = EMPTY;
                }
            boolean bishopOk = true;
            for (int sq : SQUARES) {
                int f = sq & 7, r = sq >> 4;
                board[sq] = WB;
                int mm = attackSquares(board, sq, false, buf);
                board[sq] = EMPTY;
                if (mm != 14 - Math.abs(f - r) - Math.abs(f + r - 7)) bishopOk = false;
            }
            note = "sums R" + sums[0] + " B" + sums[1] + " N" + sums[2]
                 + " K" + sums[3] + " Q" + sums[4]
                 + "; max " + maxima[0] + "/" + maxima[1] + "/" + maxima[2]
                 + "/" + maxima[3] + "/" + maxima[4];
            check("C3", sums[0] == 896 && sums[1] == 560 && sums[2] == 336
                     && sums[3] == 420 && sums[4] == 1456
                     && maxima[0] == 14 && maxima[1] == 13 && maxima[2] == 8
                     && maxima[3] == 8 && maxima[4] == 27 && bishopOk, note);
        }

        /* 4 flow termination */
        {
            long[] got = new long[9];
            int[] W = {8, 8, 8, 8, 8, 8, 48, 24, 12};
            int[] H = {8, 8, 8, 8, 8, 8, 48, 36, 12};
            int[] A = {1, 3, 2, 1, 1, 2, 1, 3, 4};
            int[] B = {1, 5, 2, 2, 0, 1, 1, 5, 6};
            boolean ok = true;
            for (int k = 0; k < 9; k++) {
                got[k] = tstar(W[k], H[k], A[k], B[k]);
                long exp = k == 2 ? 4 : k == 6 ? 48 : k == 7 ? 72 : k == 8 ? 6 : 8;
                if (got[k] != exp) ok = false;
            }
            note = "9 t* cases: " + got[0] + "," + got[1] + "," + got[2]
                 + "," + got[3] + "," + got[4];
            check("C4", ok, note);
        }

        /* 5 perft identities */
        {
            Pos pos = setFen(new Pos(), "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
                             "w", "KQkq", "-");
            long p1 = perft(pos, 1), p2 = perft(pos, 2);
            long p3 = perft(pos, 3), p4 = perft(pos, 4);
            note = "perft " + p1 + " " + p2 + " " + p3 + " " + p4;
            check("C5", p1 == 20 && p2 == 400 && p3 == 8902 && p4 == 197281, note);
        }

        /* 6 threat fields */
        {
            int[] pawnless = new int[128];
            int[] backRank = {WR, WN, WB, WQ, WK, WB, WN, WR};
            for (int f = 0; f < 8; f++) {
                pawnless[f] = backRank[f];
                pawnless[112 + f] = -backRank[f];
            }
            int vw = equivarianceViolations(pawnless, 1);
            int vb = equivarianceViolations(pawnless, -1);
            int[] start = new int[128];
            for (int f = 0; f < 8; f++) {
                start[f] = backRank[f];
                start[112 + f] = -backRank[f];
                start[16 + f] = WP;
                start[96 + f] = BP;
            }
            int anomaly = equivarianceViolations(start, 1)
                        + equivarianceViolations(start, -1);
            note = "pawnless violations " + vw + "/" + vb + ", pawn anomaly " + anomaly;
            check("C6", vw == 0 && vb == 0 && anomaly == 176, note);
        }

        /* 7 kinetic energy */
        {
            Pos pos = setFen(new Pos(), "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
                             "w", "KQkq", "-");
            int m0 = legalMoves(pos).length;
            Undo u = new Undo();
            make(pos, uciToMove(pos, "e2e4"), u);
            pos.side = 1;                        // count White's mobility
            int m1 = legalMoves(pos).length;
            pos.side = -1;
            unmake(pos, u);
            note = "White mobility " + m0 + " -> " + m1 + " after 1.e4";
            check("C7", m0 == 20 && m1 == 30, note);
        }

        /* 8 mate certificates */
        {
            Pos morphy = setFen(new Pos(), "kbK5/pp6/1P6/8/8/8/8/R7", "w", "-", "-");
            boolean keyOk = keyMatesIn2(morphy, nameSq("a1"), nameSq("a6"));
            int pliesM = mateSearchPlies(morphy, 4);
            Pos ladder = setFen(new Pos(), "7k/8/8/8/8/8/R7/1R4K1", "w", "-", "-");
            int pliesL = mateSearchPlies(ladder, 4);
            Pos nr = setFen(new Pos(), "7k/8/5N1K/8/8/8/8/6R1", "w", "-", "-");
            int pliesN = mateSearchPlies(nr, 2);
            boolean nrKey = false;
            for (int m : legalMoves(nr)) {
                if (mFrom(m) == nameSq("g1") && mTo(m) == nameSq("g8")) {
                    Undo u2 = new Undo();
                    make(nr, m, u2);
                    int[] replies = legalMoves(nr);
                    boolean mated = replies.length == 0
                            && attacked(nr.board, kingSq(nr, nr.side), -nr.side);
                    unmake(nr, u2);
                    nrKey = mated;
                    break;
                }
            }
            note = "morphy " + pliesM + "(key a1a6) ladder " + pliesL
                 + " nr " + pliesN + "(key g1g8)";
            check("C8", pliesM == 3 && keyOk && pliesL == 3 && pliesN == 1
                     && nrKey, note);
        }

        /* 9 zobrist incrementality over a fixed playout */
        {
            long[][] zob = new long[12][128];
            long state = 1L;
            for (int pi = 0; pi < 12; pi++)
                for (int sq = 0; sq < 128; sq++) {
                    state = splitmix64(state);
                    zob[pi][sq] = state;
                }
            long sideKey = splitmix64(state);

            Pos pos = setFen(new Pos(), "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
                             "w", "KQkq", "-");
            long h = fullHash(pos.board, pos.side, zob, sideKey);
            boolean incOk = h == fullHash(pos.board, 1, zob, sideKey);
            String[] playout = {"e2e4", "e7e5", "g1f3", "b8c6", "f1b5",
                                "g8f6", "e1g1", "f8c5", "d2d3", "d7d6"};
            for (String ply : playout) {
                int m = uciToMove(pos, ply);
                int fr = mFrom(m), to = mTo(m);
                int piece = pos.board[fr];
                int captured = pos.board[to];
                h ^= zob[zrow(piece)][fr];
                if (captured != EMPTY) h ^= zob[zrow(captured)][to];
                int promo = mPromo(m);
                if (promo != 0)
                    h ^= zob[zrow(promo * pos.side)][to] ^ zob[zrow(piece)][to];
                else
                    h ^= zob[zrow(piece)][to];
                int side = pos.side;
                if (mFlag(m) == FLAG_EP) {              // en passant: captured pawn
                    int cap = to - 16 * side;
                    h ^= zob[zrow(pos.board[cap])][cap];
                }
                if (mFlag(m) == FLAG_CASTLE) {          // castling: rook relocation
                    if (to == 6) h ^= zob[zrow(WR)][7] ^ zob[zrow(WR)][5];
                    else if (to == 2) h ^= zob[zrow(WR)][0] ^ zob[zrow(WR)][3];
                    else if (to == 118) h ^= zob[zrow(BR)][119] ^ zob[zrow(BR)][117];
                    else h ^= zob[zrow(BR)][112] ^ zob[zrow(BR)][115];
                }
                make(pos, m, new Undo());
                h ^= sideKey;
                if (h != fullHash(pos.board, pos.side, zob, sideKey)) {
                    incOk = false;
                    break;
                }
            }
            boolean smOk = splitmix64(1L) == 0x910A2DEC89025CC1L
                        && splitmix64(2L) == 0x975835DE1C9756CEL
                        && splitmix64(3L) == 0x1D0B14E4DB018FEDL;
            note = "incremental hash over " + playout.length
                 + " plies, splitmix vectors " + (smOk ? "ok" : "BAD");
            check("C9", incOk && smOk, note);
        }

        /* 10 knight tour certificate */
        {
            int[] tour = new int[64];
            for (int i = 0; i < 64; i++) tour[i] = nameSq(KNIGHT_TOUR[i]);
            boolean distinct = true;
            for (int i = 0; i < 64 && distinct; i++)
                for (int j = i + 1; j < 64; j++)
                    if (tour[i] == tour[j]) { distinct = false; break; }
            boolean closed = true;
            for (int i = 0; i < 64; i++)
                if (!knightNeighbour(tour[i], tour[(i + 1) % 64])) {
                    closed = false;
                    break;
                }
            note = "tour 64 distinct cells, closure " + (closed ? "ok" : "BAD");
            check("C10", distinct && closed, note);
        }

        System.out.println("verdict: " + gPass + "/" + gTotal);
        System.exit(gPass == gTotal ? 0 : 1);
    }
}

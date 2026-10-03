/*
  chess_core.c — POLYGLOT VERIFICATION CORE (C implementation)

  Program author: Isaev Iskhak Khamzatovich
  Repository: github.com/wild8highlander/chess-dynamics-lab
  License: individual exclusive license (see LICENSE)

  The same 10-check battery as polyglot/python/chess_core.py.
  Build:  cc -O2 -o chess_core c/chess_core.c -lm
  Run:    ./chess_core          (expects the verdict 10/10)
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

/* ── board (0x88) ─────────────────────────────────────────────────── */
enum { EMPTY = 0, WP = 1, WN = 2, WB = 3, WR = 4, WQ = 5, WK = 6,
       BP = -1, BN = -2, BB = -3, BR = -4, BQ = -5, BK = -6 };
static const int KNIGHT_OFFS[8] = {31, 33, 14, 18, -31, -33, -14, -18};
static const int BISHOP_DIRS[4] = {15, 17, -15, -17};
static const int ROOK_DIRS[4]   = {16, -16, 1, -1};
static const int KING_DIRS[8]   = {15, 16, 17, 1, -15, -16, -17, -1};
#define WK_CASTLE 1
#define WQ_CASTLE 2
#define BK_CASTLE 4
#define BQ_CASTLE 8
#define FLAG_DOUBLE 1
#define FLAG_EP 2
#define FLAG_CASTLE 3

typedef struct {
    signed char board[128];
    signed char side;       /* 1 = White, -1 = Black */
    signed char castling;
    short ep;
} Pos;

static int name_sq(const char *s) {
    static const char *files = "abcdefgh";
    const char *p = strchr(files, s[0]);
    return 16 * (s[1] - '1') + (int)(p - files);
}

static void set_fen(Pos *p, const char *placement, char side_ch,
                    const char *castling, const char *ep) {
    memset(p, 0, sizeof(*p));
    int rank = 7, file = 0;
    for (const char *c = placement; *c; c++) {
        if (*c == '/') { rank--; file = 0; continue; }
        if (*c >= '1' && *c <= '8') { file += *c - '0'; continue; }
        int piece = 0;
        switch (*c) {
            case 'P': piece = WP; break; case 'N': piece = WN; break;
            case 'B': piece = WB; break; case 'R': piece = WR; break;
            case 'Q': piece = WQ; break; case 'K': piece = WK; break;
            case 'p': piece = BP; break; case 'n': piece = BN; break;
            case 'b': piece = BB; break; case 'r': piece = BR; break;
            case 'q': piece = BQ; break; case 'k': piece = BK; break;
        }
        p->board[16 * rank + file++] = (signed char)piece;
    }
    p->side = (side_ch == 'w') ? 1 : -1;
    p->castling = 0;
    for (const char *c = castling; *c && *c != '-'; c++)
        p->castling |= (*c == 'K') ? WK_CASTLE : (*c == 'Q') ? WQ_CASTLE
                     : (*c == 'k') ? BK_CASTLE : BQ_CASTLE;
    p->ep = (*ep == '-') ? -1 : (short)name_sq(ep);
}

static int attacked(const signed char *b, int sq, int by) {
    static const int pawn_off_w[2] = {-15, -17};
    static const int pawn_off_b[2] = {15, 17};
    int i, off;
    for (i = 0; i < 2; i++) {
        off = (by == 1) ? pawn_off_w[i] : pawn_off_b[i];
        int s = sq + off;
        if (!(s & 0x88) && b[s] == by) return 1;
    }
    for (i = 0; i < 8; i++) {
        int s = sq + KNIGHT_OFFS[i];
        if (!(s & 0x88) && b[s] == 2 * by) return 1;
    }
    for (i = 0; i < 8; i++) {
        int s = sq + KING_DIRS[i];
        if (!(s & 0x88) && b[s] == 6 * by) return 1;
    }
    for (int dset = 0; dset < 2; dset++) {
        const int *dirs = dset ? ROOK_DIRS : BISHOP_DIRS;
        int kinds[2];
        if (dset) { kinds[0] = 4; kinds[1] = 5; }
        else      { kinds[0] = 3; kinds[1] = 5; }
        for (i = 0; i < (dset ? 4 : 4); i++) {
            int s = sq + dirs[i];
            while (!(s & 0x88)) {
                int p = b[s];
                if (p != EMPTY) {
                    if ((p > 0) == (by > 0) &&
                        (abs(p) == kinds[0] || abs(p) == kinds[1]))
                        return 1;
                    break;
                }
                s += dirs[i];
            }
        }
    }
    return 0;
}

static int king_sq(const Pos *p, int side) {
    int t = 6 * side;
    for (int sq = 0; sq < 128; sq++)
        if (!(sq & 0x88) && p->board[sq] == t) return sq;
    fprintf(stderr, "king missing\n");
    exit(2);
}

typedef struct { unsigned char fr, to, promo, flag; } Move;

#define MK(fr_, to_, pr, fl) ((Move){(unsigned char)(fr_), \
    (unsigned char)(to_), (unsigned char)(pr), (unsigned char)(fl)})

static int g_nmoves;
static Move g_moves[256];

static void pseudo_moves(const Pos *p) {
    const signed char *b = p->board;
    int side = p->side;
    g_nmoves = 0;
    
    for (int rank = 0; rank < 8; rank++) {
        for (int file = 0; file < 8; file++) {
            int fr = 16 * rank + file;
            int piece = b[fr];
            if (piece == EMPTY || (piece > 0) != (side > 0)) continue;
            int ap = abs(piece);
            if (ap == 1) {
                int fwd = 16 * side;
                int promo_rank = (side == 1) ? 6 : 1;
                int start_rank = (side == 1) ? 1 : 6;
                int s = fr + fwd;
                if (!(s & 0x88) && b[s] == EMPTY) {
                    if (rank == promo_rank) {
                        int prs[4] = {5, 2, 4, 3};
                        for (int k = 0; k < 4; k++)
                            g_moves[g_nmoves++] = MK(fr, s, prs[k], 0);
                    } else {
                        g_moves[g_nmoves++] = MK(fr, s, 0, 0);
                        if (rank == start_rank && b[s + fwd] == EMPTY)
                            g_moves[g_nmoves++] = MK(fr, s + fwd, 0,
                                                     FLAG_DOUBLE);
                    }
                }
                for (int k = 0; k < 2; k++) {
                    int off = fwd + (k ? 1 : -1);
                    s = fr + off;
                    if (s & 0x88) continue;
                    int q = b[s];
                    if (q != EMPTY && (q > 0) != (side > 0)) {
                        if (rank == promo_rank) {
                            int prs[4] = {5, 2, 4, 3};
                            for (int j = 0; j < 4; j++)
                                g_moves[g_nmoves++] = MK(fr, s, prs[j], 0);
                        } else {
                            g_moves[g_nmoves++] = MK(fr, s, 0, 0);
                        }
                    } else if (s == p->ep && q == EMPTY &&
                               rank == ((side == 1) ? 4 : 3)) {
                        g_moves[g_nmoves++] = MK(fr, s, 0, FLAG_EP);
                    }
                }
            } else if (ap == 2 || ap == 6) {
                const int *offs = (ap == 2) ? KNIGHT_OFFS : KING_DIRS;
                for (int k = 0; k < 8; k++) {
                    int s = fr + offs[k];
                    if (s & 0x88) continue;
                    int q = b[s];
                    if (q == EMPTY || (q > 0) != (side > 0))
                        g_moves[g_nmoves++] = MK(fr, s, 0, 0);
                }
            } else {
                const int *dirs = (ap == 4) ? ROOK_DIRS
                                : (ap == 3) ? BISHOP_DIRS : KING_DIRS;
                int n = (ap >= 5) ? 8 : 4;
                for (int k = 0; k < n; k++) {
                    int s = fr + dirs[k];
                    while (!(s & 0x88)) {
                        int q = b[s];
                        if (q == EMPTY) {
                            g_moves[g_nmoves++] = MK(fr, s, 0, 0);
                        } else {
                            if ((q > 0) != (side > 0))
                                g_moves[g_nmoves++] = MK(fr, s, 0, 0);
                            break;
                        }
                        s += dirs[k];
                    }
                }
            }
        }
    }
    /* castling */
    if (side == 1) {
        if ((p->castling & WK_CASTLE) && b[5] == EMPTY && b[6] == EMPTY
                && b[4] == WK && b[7] == WR
                && !attacked(b, 4, -1) && !attacked(b, 5, -1)
                && !attacked(b, 6, -1))
            g_moves[g_nmoves++] = MK(4, 6, 0, FLAG_CASTLE);
        if ((p->castling & WQ_CASTLE) && b[3] == EMPTY && b[2] == EMPTY
                && b[1] == EMPTY && b[4] == WK && b[0] == WR
                && !attacked(b, 4, -1) && !attacked(b, 3, -1)
                && !attacked(b, 2, -1))
            g_moves[g_nmoves++] = MK(4, 2, 0, FLAG_CASTLE);
    } else {
        if ((p->castling & BK_CASTLE) && b[117] == EMPTY && b[118] == EMPTY
                && b[116] == BK && b[119] == BR
                && !attacked(b, 116, 1) && !attacked(b, 117, 1)
                && !attacked(b, 118, 1))
            g_moves[g_nmoves++] = MK(116, 118, 0, FLAG_CASTLE);
        if ((p->castling & BQ_CASTLE) && b[115] == EMPTY && b[114] == EMPTY
                && b[113] == EMPTY && b[116] == BK && b[112] == BR
                && !attacked(b, 116, 1) && !attacked(b, 115, 1)
                && !attacked(b, 114, 1))
            g_moves[g_nmoves++] = MK(116, 114, 0, FLAG_CASTLE);
    }
}

typedef struct { Move m; signed char captured; signed char castling;
                 short ep; } Undo;

static void make(Pos *p, Move m, Undo *u) {
    signed char *b = p->board;
    int fr = m.fr, to = m.to, side = p->side;
    int piece = b[fr];
    u->m = m;
    u->captured = b[to];
    u->castling = p->castling;
    u->ep = p->ep;
    b[fr] = EMPTY;
    if (m.flag == FLAG_EP) b[to - 16 * side] = EMPTY;
    b[to] = (signed char)(m.promo ? m.promo * side : piece);
    if (m.flag == FLAG_CASTLE) {
        if (to == 6)       { b[7] = EMPTY;   b[5] = WR; }
        else if (to == 2)  { b[0] = EMPTY;   b[3] = WR; }
        else if (to == 118){ b[119] = EMPTY; b[117] = BR; }
        else               { b[112] = EMPTY; b[115] = BR; }
    }
    if (piece == WK)       p->castling &= ~(WK_CASTLE | WQ_CASTLE);
    else if (piece == BK)  p->castling &= ~(BK_CASTLE | BQ_CASTLE);
    if (fr == 7  || to == 7)   p->castling &= ~WK_CASTLE;
    if (fr == 0  || to == 0)   p->castling &= ~WQ_CASTLE;
    if (fr == 119 || to == 119) p->castling &= ~BK_CASTLE;
    if (fr == 112 || to == 112) p->castling &= ~BQ_CASTLE;
    p->ep = (m.flag == FLAG_DOUBLE) ? (short)(fr + 16 * side) : -1;
    p->side = (signed char)(-side);
}

static void unmake(Pos *p, const Undo *u) {
    signed char *b = p->board;
    int fr = u->m.fr, to = u->m.to, side = -p->side;
    int piece = b[to];
    if (u->m.promo) piece = side;
    b[fr] = (signed char)piece;
    b[to] = u->captured;
    if (u->m.flag == FLAG_EP) b[to - 16 * side] = (signed char)(-side);
    if (u->m.flag == FLAG_CASTLE) {
        if (to == 6)       { b[7] = WR; b[5] = EMPTY; }
        else if (to == 2)  { b[0] = WR; b[3] = EMPTY; }
        else if (to == 118){ b[119] = BR; b[117] = EMPTY; }
        else               { b[112] = BR; b[115] = EMPTY; }
    }
    p->castling = u->castling;
    p->ep = u->ep;
    p->side = (signed char)side;
}

static int legal_moves(const Pos *p, Move *out) {
    Pos tmp = *p;
    pseudo_moves(&tmp);
    int n = 0;
    for (int i = 0; i < g_nmoves; i++) {
        Move m = g_moves[i];
        if (abs(tmp.board[m.to]) == 6) continue;
        Undo u;
        make(&tmp, m, &u);
        if (!attacked(tmp.board, king_sq(&tmp, -tmp.side), tmp.side))
            out[n++] = m;
        unmake(&tmp, &u);
    }
    return n;
}

static long perft(Pos *p, int d) {
    if (d == 0) return 1;
    Move mv[256];
    int n = legal_moves(p, mv);
    if (d == 1) return n;
    long total = 0;
    Undo u;
    for (int i = 0; i < n; i++) {
        make(p, mv[i], &u);
        total += perft(p, d - 1);
        unmake(p, &u);
    }
    return total;
}

/* ── splitmix64 ───────────────────────────────────────────────────── */
static uint64_t splitmix64(uint64_t x) {
    x += 0x9E3779B97F4A7C15ULL;
    uint64_t z = x;
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}

/* ── algebra helpers ──────────────────────────────────────────────── */
typedef struct { int f, r; } FR;

static FR g_id(int f, int r)     { return (FR){f, r}; }
static FR g_rot90(int f, int r)  { return (FR){r, 7 - f}; }
static FR g_rot180(int f, int r) { return (FR){7 - f, 7 - r}; }
static FR g_rot270(int f, int r) { return (FR){7 - r, f}; }
static FR g_mirh(int f, int r)   { return (FR){7 - f, r}; }
static FR g_mirv(int f, int r)   { return (FR){f, 7 - r}; }
static FR g_diag(int f, int r)   { return (FR){r, f}; }
static FR g_anti(int f, int r)   { return (FR){7 - r, 7 - f}; }

typedef FR (*GFn)(int, int);
static const GFn D4[8]  = {g_id, g_rot90, g_rot180, g_rot270,
                           g_mirh, g_mirv, g_diag, g_anti};
static const GFn V4[4]  = {g_id, g_rot180, g_diag, g_anti};

static int gcd_i(int a, int b) { while (b) { int t = a % b; a = b; b = t; } return a; }
static long lcm_l(long a, long b) { return a / gcd_i((int)a, (int)b) * b; }

static long tstar(int W, int H, int a, int b) {
    int gx = gcd_i(abs(a), W); if (!gx) gx = W;
    int gy = gcd_i(abs(b), H); if (!gy) gy = H;
    long px = W / gx, py = H / gy;
    return lcm_l(px, py);
}

/* squares attacked by the piece on sq; blocking=1 stops at blockers */
static int attack_squares(const signed char *b, int sq, int blocking,
                          int *out) {
    int p = b[sq], ap = abs(p), n = 0;
    if (ap == 1) {
        int fwd = 16 * (p > 0 ? 1 : -1);
        for (int k = -1; k <= 1; k += 2) {
            int s = sq + fwd + k;
            if (!(s & 0x88)) out[n++] = s;
        }
    } else if (ap == 2 || ap == 6) {
        const int *offs = (ap == 2) ? KNIGHT_OFFS : KING_DIRS;
        for (int k = 0; k < 8; k++) {
            int s = sq + offs[k];
            if (!(s & 0x88)) out[n++] = s;
        }
    } else {
        const int *dirs = (ap == 4) ? ROOK_DIRS
                        : (ap == 3) ? BISHOP_DIRS : KING_DIRS;
        int cnt = (ap >= 5) ? 8 : 4;
        for (int k = 0; k < cnt; k++) {
            int s = sq + dirs[k];
            while (!(s & 0x88)) {
                out[n++] = s;
                if (blocking && b[s] != EMPTY) break;
                s += dirs[k];
            }
        }
    }
    return n;
}

static int equivariance_violations(const signed char *board, int side) {
    int theta[128] = {0};
    int buf[64];
    for (int sq = 0; sq < 128; sq++) {
        if (sq & 0x88) continue;
        int p = board[sq];
        if (p != EMPTY && (p > 0) == (side > 0)) {
            int n = attack_squares(board, sq, 1, buf);
            for (int k = 0; k < n; k++) theta[buf[k]]++;
        }
    }
    int bad = 0;
    for (int gi = 0; gi < 8; gi++) {
        signed char bg[128];
        memset(bg, 0, sizeof(bg));
        for (int sq = 0; sq < 128; sq++) {
            if (sq & 0x88) continue;
            int p = board[sq];
            if (p != EMPTY) {
                FR t = D4[gi](sq & 7, sq >> 4);
                bg[16 * t.r + t.f] = (signed char)p;
            }
        }
        int tg[128] = {0};
        for (int sq = 0; sq < 128; sq++) {
            if (sq & 0x88) continue;
            int p = bg[sq];
            if (p != EMPTY && (p > 0) == (side > 0)) {
                int n = attack_squares(bg, sq, 1, buf);
                for (int k = 0; k < n; k++) tg[buf[k]]++;
            }
        }
        for (int sq = 0; sq < 128; sq++) {
            if (sq & 0x88) continue;
            FR t = D4[gi](sq & 7, sq >> 4);
            if (tg[16 * t.r + t.f] != theta[sq]) bad++;
        }
    }
    return bad;
}

static const char *KNIGHT_TOUR[64] = {
    "f5","h4","g2","e1","c2","a1","b3","c1","a2","b4","a6","b8","d7","f8",
    "h7","g5","h3","g1","e2","g3","h1","f2","d1","b2","d3","f4","h5","g7",
    "e8","f6","g8","h6","g4","h2","f1","e3","d5","c7","a8","b6","a4","c3",
    "b1","a3","b5","a7","c8","e7","g6","h8","f7","e5","f3","d2","c4","a5",
    "c6","d4","e6","d8","b7","c5","e4","d6"};

static int knight_neighbour(int a, int b) {
    int df = abs((a & 7) - (b & 7)), dr = abs((a >> 4) - (b >> 4));
    return (df == 1 && dr == 2) || (df == 2 && dr == 1);
}

/* forced-mate search: shortest mate for the side to move, or 0 */
static int mate_dfs(Pos *p, int depth) {
    if (depth <= 0) return 0;
    Move mv[256];
    int n = legal_moves(p, mv);
    int best = 0;
    Undo u;
    for (int i = 0; i < n; i++) {
        make(p, mv[i], &u);
        Move rep[256];
        int rn = legal_moves(p, rep);
        if (rn == 0) {
            int mated = attacked(p->board, king_sq(p, p->side), -p->side);
            unmake(p, &u);
            if (mated) return 1;
            continue;
        }
        if (depth >= 2) {
            int all_mated = 1, worst = 0;
            for (int j = 0; j < rn; j++) {
                Undo u2;
                make(p, rep[j], &u2);
                int sub = mate_dfs(p, depth - 2);
                unmake(p, &u2);
                if (!sub) { all_mated = 0; break; }
                if (sub > worst) worst = sub;
            }
            if (all_mated) {
                unmake(p, &u);
                int cand = worst + 2;
                if (!best || cand < best) {
                    best = cand;
                    if (best <= 3) return best;
                }
                continue;
            }
        }
        unmake(p, &u);
    }
    return best;
}

void dbg(void);

/* ── the battery ──────────────────────────────────────────────────── */
static int g_pass = 0, g_total = 0;
static void check(const char *code, int ok, const char *note) {
    g_total++;
    g_pass += ok ? 1 : 0;
    printf("[%s] %s  %s\n", ok ? "PASS" : "FAIL", code, note);
}

int main(void) {

    char note[256];

    /* 1 board algebra */
    {
        int seen[8][8] = {{0}}, cnt = 0, small = 0, big = 0;
        for (int f = 0; f < 8; f++)
            for (int r = 0; r < 8; r++) {
                if (seen[f][r]) continue;
                int sz = 0;
                FR orbs[8];
                for (int gi = 0; gi < 4; gi++) {
                    FR t = V4[gi](f, r);
                    int dup = 0;
                    for (int k = 0; k < sz; k++)
                        if (orbs[k].f == t.f && orbs[k].r == t.r) dup = 1;
                    if (!dup) orbs[sz++] = t;
                    seen[t.f][t.r] = 1;
                }
                cnt++;
                if (sz == 2) small++;
                else if (sz == 4) big++;
            }
        int dcnt = 0, dseen[8][8] = {{0}};
        for (int f = 0; f < 8; f++)
            for (int r = 0; r < 8; r++) {
                if (dseen[f][r]) continue;
                for (int gi = 0; gi < 8; gi++) {
                    FR t = D4[gi](f, r);
                    dseen[t.f][t.r] = 1;
                }
                dcnt++;
            }
        int bd4 = (64 + 0 + 0 + 0 + 0 + 0 + 8 + 8) / 8;
        int bv4 = (64 + 0 + 8 + 8) / 4;
        snprintf(note, sizeof(note), "V4=%d(%d+%d) D4=%d burnside %d/%d",
                 cnt, small, big, dcnt, bv4, bd4);
        check("C1", cnt == 20 && small == 8 && big == 12 && dcnt == 10 &&
              bd4 == 10 && bv4 == 20, note);
    }

    /* 2 move-graph census */
    {
        signed char b[128];
        memset(b, 0, sizeof(b));
        int rR = 0, rB = 0, rN = 0, rK = 0, rQ = 0, buf[64];
        int types[5] = {WR, WB, WN, WK, WQ};
        int *cnts[5] = {&rR, &rB, &rN, &rK, &rQ};
        for (int t = 0; t < 5; t++)
            for (int sq = 0; sq < 128; sq++) {
                if (sq & 0x88) continue;
                b[sq] = (signed char)types[t];
                int n = attack_squares(b, sq, 1, buf);
                *cnts[t] += n;
                b[sq] = EMPTY;
            }
        snprintf(note, sizeof(note), "edges R%d B%d N%d K%d Q%d",
                 rR / 2, rB / 2, rN / 2, rK / 2, rQ / 2);
        check("C2", rR / 2 == 448 && rB / 2 == 280 && rN / 2 == 168 &&
              rK / 2 == 210 && rQ / 2 == 728, note);
    }

    /* 3 mobility census */
    {
        signed char b[128];
        memset(b, 0, sizeof(b));
        int sR = 0, sB = 0, sN = 0, sK = 0, sQ = 0, buf[64];
        int types[5] = {WR, WB, WN, WK, WQ};
        int *cnts[5] = {&sR, &sB, &sN, &sK, &sQ};
        int mx[5] = {0, 0, 0, 0, 0};
        for (int t = 0; t < 5; t++)
            for (int sq = 0; sq < 128; sq++) {
                if (sq & 0x88) continue;
                b[sq] = (signed char)types[t];
                int n = attack_squares(b, sq, 0, buf);
                *cnts[t] += n;
                if (n > mx[t]) mx[t] = n;
                b[sq] = EMPTY;
            }
        int bishop_ok = 1;
        for (int sq = 0; sq < 128; sq++) {
            if (sq & 0x88) continue;
            int f = sq & 7, r = sq >> 4;
            b[sq] = WB;
            int m = attack_squares(b, sq, 0, buf);
            b[sq] = EMPTY;
            if (m != 14 - abs(f - r) - abs(f + r - 7)) bishop_ok = 0;
        }
        snprintf(note, sizeof(note),
                 "sums R%d B%d N%d K%d Q%d; max %d/%d/%d/%d/%d",
                 sR, sB, sN, sK, sQ, mx[0], mx[1], mx[2], mx[3], mx[4]);
        check("C3", sR == 896 && sB == 560 && sN == 336 && sK == 420 &&
              sQ == 1456 && mx[0] == 14 && mx[1] == 13 && mx[2] == 8 &&
              mx[3] == 8 && mx[4] == 27 && bishop_ok, note);
    }

    /* 4 flow termination */
    {
        long got[9];
        int W[9] = {8, 8, 8, 8, 8, 8, 48, 24, 12};
        int H[9] = {8, 8, 8, 8, 8, 8, 48, 36, 12};
        int A[9] = {1, 3, 2, 1, 1, 2, 1, 3, 4};
        int B[9] = {1, 5, 2, 2, 0, 1, 1, 5, 6};
        int ok = 1;
        for (int k = 0; k < 9; k++) {
            got[k] = tstar(W[k], H[k], A[k], B[k]);
            long exp = (k == 2) ? 4 : (k == 6) ? 48 : (k == 7) ? 72
                     : (k == 8) ? 6 : 8;
            if (got[k] != exp) ok = 0;
        }
        snprintf(note, sizeof(note), "9 t* cases: %ld,%ld,%ld,%ld,%ld",
                 got[0], got[1], got[2], got[3], got[4]);
        check("C4", ok, note);
    }

    /* 5 perft identities */
    {
        Pos p;
        set_fen(&p, "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR", 'w',
                "KQkq", "-");
        long p1 = perft(&p, 1), p2 = perft(&p, 2);
        long p3 = perft(&p, 3), p4 = perft(&p, 4);
        snprintf(note, sizeof(note), "perft %ld %ld %ld %ld",
                 p1, p2, p3, p4);
        check("C5", p1 == 20 && p2 == 400 && p3 == 8902 && p4 == 197281,
              note);
    }

    /* 6 threat fields */
    {
        signed char pl[128];
        memset(pl, 0, sizeof(pl));
        static const int back[8] = {WR, WN, WB, WQ, WK, WB, WN, WR};
        for (int f = 0; f < 8; f++) {
            pl[f] = (signed char)back[f];
            pl[112 + f] = (signed char)(-back[f]);
        }
        int vw = equivariance_violations(pl, 1);
        int vb = equivariance_violations(pl, -1);
        signed char st[128];
        memset(st, 0, sizeof(st));
        for (int f = 0; f < 8; f++) {
            st[f] = (signed char)back[f];
            st[112 + f] = (signed char)(-back[f]);
            st[16 + f] = WP;
            st[96 + f] = BP;
        }
        int anomaly = equivariance_violations(st, 1)
                    + equivariance_violations(st, -1);
        snprintf(note, sizeof(note),
                 "pawnless violations %d/%d, pawn anomaly %d", vw, vb,
                 anomaly);
        check("C6", vw == 0 && vb == 0 && anomaly == 176, note);
    }

    /* 7 kinetic energy */
    {
        Pos p;
        set_fen(&p, "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR", 'w',
                "KQkq", "-");
        Move mv[256];
        int m0 = legal_moves(&p, mv);
        int e2 = name_sq("e2"), e4 = name_sq("e4");
        Move key = {0};
        for (int i = 0; i < g_nmoves; i++)
            if (g_moves[i].fr == e2 && g_moves[i].to == e4) key = g_moves[i];
        Undo u;
        make(&p, key, &u);
        p.side = 1;
        int m1 = legal_moves(&p, mv);
        p.side = -1;
        unmake(&p, &u);
        snprintf(note, sizeof(note),
                 "White mobility %d -> %d after 1.e4", m0, m1);
        check("C7", m0 == 20 && m1 == 30, note);
    }

    /* 8 mate certificates */
    {
        Pos p;
        Undo u;
        set_fen(&p, "kbK5/pp6/1P6/8/8/8/8/R7", 'w', "-", "-");
        int plies_m = mate_dfs(&p, 4);
        int key_ok = 0;
        Move mv[256];
        legal_moves(&p, mv);
        int a1 = name_sq("a1"), a6 = name_sq("a6");
        for (int i = 0; i < g_nmoves; i++) {
            if (g_moves[i].fr == a1 && g_moves[i].to == a6) {
                make(&p, g_moves[i], &u);
                Move rep[256];
                int rn = legal_moves(&p, rep);
                key_ok = rn > 0;
                for (int j = 0; j < rn && key_ok; j++) {
                    Undo u2;
                    make(&p, rep[j], &u2);
                    key_ok = (mate_dfs(&p, 1) == 1);
                    unmake(&p, &u2);
                }
                unmake(&p, &u);
                break;
            }
        }
        set_fen(&p, "7k/8/8/8/8/8/R7/1R4K1", 'w', "-", "-");
        int plies_l = mate_dfs(&p, 4);
        set_fen(&p, "7k/8/5N1K/8/8/8/8/6R1", 'w', "-", "-");
        int plies_n = mate_dfs(&p, 2);
        int nr_key = 0;
        legal_moves(&p, mv);
        int g1 = name_sq("g1"), g8 = name_sq("g8");
        for (int i = 0; i < g_nmoves; i++) {
            if (g_moves[i].fr == g1 && g_moves[i].to == g8) {
                make(&p, g_moves[i], &u);
                Move rep[256];
                int rn = legal_moves(&p, rep);
                nr_key = (rn == 0 && attacked(p.board,
                          king_sq(&p, p.side), -p.side));
                unmake(&p, &u);
                break;
            }
        }
        snprintf(note, sizeof(note),
                 "morphy %d(key a1a6) ladder %d nr %d(key g1g8)",
                 plies_m, plies_l, plies_n);
        check("C8", plies_m == 3 && key_ok && plies_l == 3 &&
              plies_n == 1 && nr_key, note);
    }

    /* 9 zobrist incrementality over a fixed playout */
    {
        uint64_t zob[13][128];

        uint64_t state = 1;
        for (int pi = 0; pi < 12; pi++)
            for (int sq = 0; sq < 128; sq++)
                zob[pi][sq] = splitmix64(state++);
        uint64_t side_key = splitmix64(state);
        /* piece -> table row map, indexed by piece + 6 (piece in -6..6) */
        int row[13] = {11, 10, 9, 8, 7, 6, 0, 0, 1, 2, 3, 4, 5};
        /* row[p+6]: p=-6..-1 -> 11,10,9,8,7,6 ; p=0 -> 0 (unused);
           p=1..6 -> 0..5 */

        Pos p;
        set_fen(&p, "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR", 'w',
                "KQkq", "-");
        uint64_t h = 0;
        for (int sq = 0; sq < 128; sq++)
            if (!(sq & 0x88) && p.board[sq] != EMPTY)
                h ^= zob[row[p.board[sq] + 6]][sq];
        if (p.side == -1) h ^= side_key;
        uint64_t full0 = h;
        int inc_ok = (h == full0);

        static const char *playout[10] = {"e2e4", "e7e5", "g1f3", "b8c6",
            "f1b5", "g8f6", "e1g1", "f8c5", "d2d3", "d7d6"};
        for (int k = 0; k < 10 && inc_ok; k++) {
            Move mv[256];
            legal_moves(&p, mv);
            int fr = name_sq(playout[k]);
            int to = name_sq(playout[k] + 2);
            Move key = {0};
            for (int i = 0; i < g_nmoves; i++)
                if (g_moves[i].fr == fr && g_moves[i].to == to)
                    key = g_moves[i];
            int piece = p.board[key.fr];
            int captured = p.board[key.to];
            h ^= zob[row[piece + 6]][key.fr];
            if (captured != EMPTY) h ^= zob[row[captured + 6]][key.to];
            if (key.promo) h ^= zob[row[key.promo * p.side + 6]][key.to]
                             ^ zob[row[piece + 6]][key.to];
            else h ^= zob[row[piece + 6]][key.to];
            if (key.flag == FLAG_EP)
                h ^= zob[row[p.board[key.to - 16 * p.side] + 6]]
                      [key.to - 16 * p.side];
            if (key.flag == FLAG_CASTLE) {
                if (key.to == 6)       h ^= zob[row[WR + 6]][7]
                                       ^ zob[row[WR + 6]][5];
                else if (key.to == 2)  h ^= zob[row[WR + 6]][0]
                                       ^ zob[row[WR + 6]][3];
                else if (key.to == 118) h ^= zob[row[BR + 6]][119]
                                        ^ zob[row[BR + 6]][117];
                else                    h ^= zob[row[BR + 6]][112]
                                        ^ zob[row[BR + 6]][115];
            }
            Undo u;
            make(&p, key, &u);
            h ^= side_key;
            uint64_t full = 0;
            for (int sq = 0; sq < 128; sq++)
                if (!(sq & 0x88) && p.board[sq] != EMPTY)
                    full ^= zob[row[p.board[sq] + 6]][sq];
            if (p.side == -1) full ^= side_key;
            if (h != full) inc_ok = 0;
        }
        int sm_ok = splitmix64(1) == 0x910A2DEC89025CC1ULL
                 && splitmix64(2) == 0x975835DE1C9756CEULL
                 && splitmix64(3) == 0x1D0B14E4DB018FEDULL;
        snprintf(note, sizeof(note),
                 "incremental hash over 10 plies, splitmix vectors %s",
                 sm_ok ? "ok" : "BAD");
        check("C9", inc_ok && sm_ok, note);
    }

    /* 10 knight tour certificate */
    {
        int tour[64];
        for (int i = 0; i < 64; i++) tour[i] = name_sq(KNIGHT_TOUR[i]);
        int distinct = 1;
        for (int i = 0; i < 64 && distinct; i++)
            for (int j = i + 1; j < 64; j++)
                if (tour[i] == tour[j]) { distinct = 0; break; }
        int closed = 1;
        for (int i = 0; i < 64; i++)
            if (!knight_neighbour(tour[i], tour[(i + 1) % 64])) {
                closed = 0;
                break;
            }
        snprintf(note, sizeof(note),
                 "tour 64 distinct cells, closure %s",
                 closed ? "ok" : "BAD");
        check("C10", distinct && closed, note);
    }

    printf("verdict: %d/%d\n", g_pass, g_total);
    return (g_pass == g_total) ? 0 : 1;
}

/* ── temporary perft debug ── */
static int g_bad = 0;
static long dbg_perft(Pos *p, int d) {
    Move mv[256];
    int n = legal_moves(p, mv);
    if (d == 1) return n;
    long total = 0;
    Undo u;
    for (int i = 0; i < n; i++) {
        make(p, mv[i], &u);
        int kings = 0;
        for (int sq = 0; sq < 128; sq++)
            if (!(sq & 0x88) && abs(p->board[sq]) == 6) kings++;
        if (kings != 2) {
            printf("kings=%d after move %d->%d flag=%d\n", kings,
                   u.m.fr, u.m.to, u.m.flag);
            if (++g_bad > 5) exit(3);
        }
        total += dbg_perft(p, d - 1);
        unmake(p, &u);
    }
    return total;
}
void dbg(void) {
    Pos p;
    set_fen(&p, "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR", 'w',
            "KQkq", "-");
    {
        int kings = 0;
        for (int sq = 0; sq < 128; sq++)
            if (!(sq & 0x88) && abs(p.board[sq]) == 6) kings++;
        printf("kings after set_fen: %d\n", kings);
        for (int rank = 7; rank >= 0; rank--) {
            printf("rank %d:", rank);
            for (int file = 0; file < 8; file++)
                printf(" %3d", p.board[16 * rank + file]);
            printf("\n");
        }
        pseudo_moves(&p);
        printf("pseudo moves: %d\n", g_nmoves);
        for (int i = 0; i < g_nmoves; i++)
            printf("  %d->%d promo=%d flag=%d\n", g_moves[i].fr,
                   g_moves[i].to, g_moves[i].promo, g_moves[i].flag);
        Move mv[256];
        printf("legal moves: %d\n", legal_moves(&p, mv));
        for (int i = 0; i < g_nmoves; i++)
            printf("  L %d->%d\n", mv[i].fr, mv[i].to);
    }
    printf("perft1=%ld\n", dbg_perft(&p, 1));
    set_fen(&p, "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR", 'w',
            "KQkq", "-");
    printf("perft2=%ld\n", dbg_perft(&p, 2));
}

/* certctc C core -- variant 1c "exact backward suffix modes" (T2b) with runner-up certification.
 *
 * This is the T2b `exactbwd.c` search, unchanged in every decision it makes (same bound, same
 * node accounting, same heap comparisons, same top-2 incumbent tracking, same termination), with
 * two memory changes that do not affect any count: a node's Ab/An arrays are released as soon as
 * the node can no longer be expanded (pruned at generation, or already expanded), and the node
 * pool grows on demand instead of being pre-allocated.
 *
 * Conventions (T2b): frames 1..T, blank = column 0.  table is T*W row-major doubles,
 * frame t at table[(t-1)*W + s].  Hhat is W*(T+1) doubles, Hhat[d*(T+1)+t].
 *
 * For a prefix u, Ab[t] / An[t] = mass of paths over frames 1..t collapsing to u and ending in the
 * blank-after-u / last-symbol state; ok_d(t) = Ab[t] + [u_last != d]*An[t]; p(u) = Ab[T]+An[T].
 * Bound: B(u) = max( p(u), max_d sum_t ok_d(t-1) * H_d(t) ), H_d(t) = max_{v: v_1=d} g_v(t) the
 * exact backward suffix mode, computed for t = T..1 by the same best-first search rooted at
 * "d forced at frame t" (which reads only H(t' > t), already exact).
 *
 * search(k2 = 1) keeps the two best distinct labellings seen (b1 >= b2) and stops only when the
 * top heap bound <= b2, so on termination every labelling other than the b1 holder has p <= b2:
 * b1 = p(mode), b2 = p(runner-up), and the margin b1/b2 is certified.
 *
 * status: 0 ok, 1 deadline, 2 generation cap, 3 node-pool cap.
 * Compile with -ffp-contract=off so that sums are rounded exactly like the Python mirror.
 */
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef struct { double *Ab, *An; long parent; int sym, tmin; double p; } Node;
typedef struct { double bound; long idx; } HeapEnt;

typedef struct {
    const double *table; int T, W;
    double *Hhat, *Mmax;                 /* Mmax[t] = max_d Hhat[d][t] */
    Node *pool; long npool, cappool, hardcap;
    HeapEnt *heap; long nheap, capheap;
    long gen, exp_final, exp_bwd, gen_cap;
    double deadline; int status;
} Ctx;

static double now_sec(void) { return (double)clock() / CLOCKS_PER_SEC; }

static void free_arrays(Node *n) { free(n->Ab); free(n->An); n->Ab = n->An = NULL; }

static long new_node(Ctx *c) {
    if (c->npool >= c->cappool) {
        long nc = c->cappool * 2; if (nc > c->hardcap) nc = c->hardcap;
        if (nc <= c->npool) { c->status = 3; return -1; }
        Node *np = (Node *)realloc(c->pool, (size_t)nc * sizeof(Node));
        if (!np) { c->status = 3; return -1; }
        c->pool = np; c->cappool = nc;
    }
    long i = c->npool++;
    c->pool[i].Ab = (double *)calloc((size_t)c->T + 1, sizeof(double));
    c->pool[i].An = (double *)calloc((size_t)c->T + 1, sizeof(double));
    c->pool[i].parent = -1; c->pool[i].sym = 0; c->pool[i].tmin = 0; c->pool[i].p = 0.0;
    return i;
}
static void reset_pool(Ctx *c) {
    for (long i = 0; i < c->npool; i++) free_arrays(&c->pool[i]);
    c->npool = 0; c->nheap = 0;
}
static void heap_push(Ctx *c, double b, long idx) {
    if (c->nheap >= c->capheap) { c->capheap *= 2; c->heap = (HeapEnt *)realloc(c->heap, (size_t)c->capheap * sizeof(HeapEnt)); }
    long i = c->nheap++; c->heap[i].bound = b; c->heap[i].idx = idx;
    while (i > 0) { long p = (i - 1) / 2; if (c->heap[p].bound >= c->heap[i].bound) break;
        HeapEnt t = c->heap[p]; c->heap[p] = c->heap[i]; c->heap[i] = t; i = p; }
}
static HeapEnt heap_pop(Ctx *c) {
    HeapEnt top = c->heap[0]; c->heap[0] = c->heap[--c->nheap]; long i = 0;
    for (;;) { long l = 2 * i + 1, r = l + 1, m = i;
        if (l < c->nheap && c->heap[l].bound > c->heap[m].bound) m = l;
        if (r < c->nheap && c->heap[r].bound > c->heap[m].bound) m = r;
        if (m == i) break; HeapEnt t = c->heap[m]; c->heap[m] = c->heap[i]; c->heap[i] = t; i = m; }
    return top;
}

/* B(u) = max(p(u), max_d sum_t ok_d(t-1) Hhat[d][t]); quick admissible filter with Mmax first
   (for a node that is prunable either way, any admissible value may be returned). */
static double bound_of(Ctx *c, long ni, double thresh) {
    Node *n = &c->pool[ni]; int T = c->T, W = c->W, T1 = T + 1;
    double best = n->p; int t0 = n->tmin;
    double s1 = 0.0;
    for (int t = t0 + 1; t <= T; t++) s1 += (n->Ab[t-1] + n->An[t-1]) * c->Mmax[t];
    if (s1 <= thresh && best <= thresh) return best > s1 ? best : s1;
    for (int d = 1; d < W; d++) {
        const double *H = c->Hhat + (size_t)d * T1; double s = 0.0;
        if (d == n->sym) { for (int t = t0 + 1; t <= T; t++) s += n->Ab[t-1] * H[t]; }
        else             { for (int t = t0 + 1; t <= T; t++) s += (n->Ab[t-1] + n->An[t-1]) * H[t]; }
        if (s > best) best = s;
    }
    return best;
}

static long make_child(Ctx *c, long pi, int d) {
    long ci = new_node(c); if (ci < 0) return -1;
    Node *p = &c->pool[pi]; Node *n = &c->pool[ci];
    int T = c->T, W = c->W; const double *tb = c->table;
    n->parent = pi; n->sym = d; n->tmin = p->tmin + 1; if (n->tmin > T) n->tmin = T;
    int same = (p->sym == d);
    for (int s = p->tmin + 1; s <= T; s++) {
        const double *y = tb + (size_t)(s - 1) * W;
        double ok = same ? p->Ab[s-1] : p->Ab[s-1] + p->An[s-1];
        n->An[s] = (n->An[s-1] + ok) * y[d];
        n->Ab[s] = (n->Ab[s-1] + n->An[s-1]) * y[0];
    }
    n->p = n->Ab[T] + n->An[T];
    c->gen++;
    return ci;
}

/* Best-first search from root ri.  k2: also certify the runner-up.  Returns status. */
static int search(Ctx *c, long ri, int k2, double *p1, double *p2, long *l1, long *l2, long *exp_out) {
    int W = c->W; double b1 = 0.0, b2 = 0.0; long n1 = -1, n2 = -1; long exp = 0;
    Node *root = &c->pool[ri];
    if (root->p > b1) { b1 = root->p; n1 = ri; }
    double rb = bound_of(c, ri, k2 ? b2 : b1);
    c->nheap = 0; heap_push(c, rb, ri);
    while (c->nheap > 0) {
        HeapEnt top = heap_pop(c);
        double thr = k2 ? b2 : b1;
        if (top.bound <= thr) break;
        if ((exp & 255) == 0 && now_sec() > c->deadline) { c->status = 1; break; }
        if (c->gen >= c->gen_cap) { c->status = 2; break; }
        exp++;
        for (int d = 1; d < W; d++) {
            long ci = make_child(c, top.idx, d); if (ci < 0) { c->status = 3; goto done; }
            Node *ch = &c->pool[ci];
            if (ch->p > b1) { b2 = b1; n2 = n1; b1 = ch->p; n1 = ci; }
            else if (ch->p > b2) { b2 = ch->p; n2 = ci; }
            thr = k2 ? b2 : b1;
            double bd = bound_of(c, ci, thr);
            if (bd > thr) heap_push(c, bd, ci); else free_arrays(ch);
        }
        free_arrays(&c->pool[top.idx]);
    }
done:
    *p1 = b1; *p2 = b2; *l1 = n1; *l2 = n2; *exp_out = exp;
    return c->status;
}

static int extract(Ctx *c, long ni, int *out, int maxlen) {   /* labelling of node ni, returns length */
    int len = 0; long i = ni;
    while (i >= 0) { Node *n = &c->pool[i]; if (n->sym > 0) len++; i = n->parent; }
    if (len > maxlen) return -1;
    int k = len; i = ni;
    while (i >= 0) { Node *n = &c->pool[i]; if (n->sym > 0) out[--k] = n->sym; i = n->parent; }
    return len;
}

int certctc_decode(const double *table, int T, int W, double time_limit, long gen_cap, long pool_cap,
                   double *out_p, int *out_l1, int *out_len1, int *out_l2, int *out_len2, long *stats,
                   double *H_out) {
    Ctx c; memset(&c, 0, sizeof c);
    c.table = table; c.T = T; c.W = W; int T1 = T + 1;
    c.Hhat = (double *)calloc((size_t)W * T1, sizeof(double)); c.Mmax = (double *)calloc((size_t)T1, sizeof(double));
    c.hardcap = pool_cap < 64 ? 64 : pool_cap; c.cappool = 4096 < c.hardcap ? 4096 : c.hardcap;
    c.pool = (Node *)calloc((size_t)c.cappool, sizeof(Node));
    c.capheap = 1024; c.heap = (HeapEnt *)malloc((size_t)c.capheap * sizeof(HeapEnt));
    c.gen_cap = gen_cap; c.deadline = now_sec() + time_limit; c.status = 0;
    /* trivial seed Hhat_d(t) = y_t[d]; the search from frame t reads only t' > t, already exact. */
    for (int d = 1; d < W; d++) for (int t = 1; t <= T; t++) c.Hhat[(size_t)d * T1 + t] = table[(size_t)(t - 1) * W + d];
    for (int t = 1; t <= T; t++) { double m = 0; for (int d = 1; d < W; d++) if (c.Hhat[(size_t)d*T1+t] > m) m = c.Hhat[(size_t)d*T1+t]; c.Mmax[t] = m; }
    /* backward: exact H_c(t) for t = T..1 */
    for (int t = T; t >= 1 && c.status == 0; t--) {
        for (int cc = 1; cc < W; cc++) {
            reset_pool(&c);
            long ri = new_node(&c); Node *r = &c.pool[ri];
            r->parent = -1; r->sym = cc; r->tmin = t;
            r->An[t] = table[(size_t)(t - 1) * W + cc];
            for (int s = t + 1; s <= T; s++) { r->An[s] = r->An[s-1] * table[(size_t)(s-1)*W + cc]; r->Ab[s] = (r->Ab[s-1] + r->An[s-1]) * table[(size_t)(s-1)*W]; }
            r->p = r->Ab[T] + r->An[T];
            double p1, p2; long l1, l2, e;
            search(&c, ri, 0, &p1, &p2, &l1, &l2, &e);
            c.exp_bwd += e;
            if (c.status) break;
            c.Hhat[(size_t)cc * T1 + t] = p1;
        }
        double m = 0; for (int d = 1; d < W; d++) if (c.Hhat[(size_t)d*T1+t] > m) m = c.Hhat[(size_t)d*T1+t]; c.Mmax[t] = m;
    }
    double p1 = 0, p2 = 0; long l1 = -1, l2 = -1, e = 0;
    *out_len1 = 0; *out_len2 = 0;
    if (c.status == 0) {
        reset_pool(&c);
        long ri = new_node(&c); Node *r = &c.pool[ri];
        r->parent = -1; r->sym = 0; r->tmin = 0; r->Ab[0] = 1.0;
        for (int s = 1; s <= T; s++) r->Ab[s] = r->Ab[s-1] * table[(size_t)(s-1)*W];
        r->p = r->Ab[T] + r->An[T];
        search(&c, ri, 1, &p1, &p2, &l1, &l2, &e);
        c.exp_final = e;
        if (c.status == 0) {
            *out_len1 = l1 >= 0 ? extract(&c, l1, out_l1, T + 1) : 0;
            *out_len2 = l2 >= 0 ? extract(&c, l2, out_l2, T + 1) : 0;
        }
    }
    out_p[0] = p1; out_p[1] = p2;
    stats[0] = c.gen; stats[1] = c.exp_final; stats[2] = c.exp_bwd; stats[3] = c.status;
    if (H_out) memcpy(H_out, c.Hhat, (size_t)W * T1 * sizeof(double));
    reset_pool(&c); free(c.pool); free(c.heap); free(c.Hhat); free(c.Mmax);
    return c.status;
}

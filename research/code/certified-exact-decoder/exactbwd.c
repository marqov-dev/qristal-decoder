/* C port of decode_exact_backward (variant 1c) from bounds.py.  Same algorithm, same node
   accounting: gen = child() calls, exp = heap pops that were expanded.
   table: T*W doubles, row-major, blank = 0.  Frames 1..T map to table[(t-1)*W + s].
   Hhat: W*(T+1) doubles, Hhat[d*(T+1)+t].
   status: 0 ok, 1 deadline, 2 generation cap, 3 node-pool cap. */
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

typedef struct { double *Ab, *An; int parent, sym, tmin; double p, bound; } Node;
typedef struct { double bound; int idx; } HeapEnt;

typedef struct {
    const double *table; int T, W;
    double *Hhat, *Mmax;            /* Mmax[t] = max_d Hhat[d][t] */
    Node *pool; int npool, cappool;
    HeapEnt *heap; int nheap, capheap;
    long gen, exp_final, exp_bwd, gen_cap;
    double deadline; int status;
} Ctx;

static double now_sec(void) { return (double)clock() / CLOCKS_PER_SEC; }

static int new_node(Ctx *c) {
    if (c->npool >= c->cappool) { c->status = 3; return -1; }
    int i = c->npool++;
    c->pool[i].Ab = (double *)calloc(c->T + 1, sizeof(double));
    c->pool[i].An = (double *)calloc(c->T + 1, sizeof(double));
    return i;
}
static void reset_pool(Ctx *c) {
    for (int i = 0; i < c->npool; i++) { free(c->pool[i].Ab); free(c->pool[i].An); }
    c->npool = 0; c->nheap = 0;
}
static void heap_push(Ctx *c, double b, int idx) {
    if (c->nheap >= c->capheap) { c->capheap *= 2; c->heap = (HeapEnt *)realloc(c->heap, c->capheap * sizeof(HeapEnt)); }
    int i = c->nheap++; c->heap[i].bound = b; c->heap[i].idx = idx;
    while (i > 0) { int p = (i - 1) / 2; if (c->heap[p].bound >= c->heap[i].bound) break;
        HeapEnt t = c->heap[p]; c->heap[p] = c->heap[i]; c->heap[i] = t; i = p; }
}
static HeapEnt heap_pop(Ctx *c) {
    HeapEnt top = c->heap[0]; c->heap[0] = c->heap[--c->nheap]; int i = 0;
    for (;;) { int l = 2 * i + 1, r = l + 1, m = i;
        if (l < c->nheap && c->heap[l].bound > c->heap[m].bound) m = l;
        if (r < c->nheap && c->heap[r].bound > c->heap[m].bound) m = r;
        if (m == i) break; HeapEnt t = c->heap[m]; c->heap[m] = c->heap[i]; c->heap[i] = t; i = m; }
    return top;
}

/* B(u) = max(p(u), max_d sum_t ok_d(t-1) Hhat[d][t]); quick admissible filter with Mmax first. */
static double bound_of(Ctx *c, int ni, double thresh) {
    Node *n = &c->pool[ni]; int T = c->T, W = c->W, T1 = T + 1;
    double best = n->p; int t0 = n->tmin < 0 ? 0 : n->tmin;
    double s1 = 0.0;
    for (int t = t0 + 1; t <= T; t++) s1 += (n->Ab[t-1] + n->An[t-1]) * c->Mmax[t];
    if (s1 <= thresh && best <= thresh) return best > s1 ? best : s1;   /* prunable; any admissible value */
    for (int d = 1; d < W; d++) {
        const double *H = c->Hhat + d * T1; double s = 0.0;
        if (d == n->sym) { for (int t = t0 + 1; t <= T; t++) s += n->Ab[t-1] * H[t]; }
        else             { for (int t = t0 + 1; t <= T; t++) s += (n->Ab[t-1] + n->An[t-1]) * H[t]; }
        if (s > best) best = s;
    }
    return best;
}

static int make_child(Ctx *c, int pi, int d) {
    int ci = new_node(c); if (ci < 0) return -1;
    Node *p = &c->pool[pi]; Node *n = &c->pool[ci];
    int T = c->T, W = c->W; const double *tb = c->table;
    n->parent = pi; n->sym = d; n->tmin = p->tmin + 1; if (n->tmin > T) n->tmin = T;
    int same = (p->sym == d);
    int s0 = p->tmin < 0 ? 1 : p->tmin + 1;
    for (int s = s0; s <= T; s++) {
        const double *y = tb + (s - 1) * W;
        double ok = same ? p->Ab[s-1] : p->Ab[s-1] + p->An[s-1];
        n->An[s] = (n->An[s-1] + ok) * y[d];
        n->Ab[s] = (n->Ab[s-1] + n->An[s-1]) * y[0];
    }
    n->p = n->Ab[T] + n->An[T];
    c->gen++;
    return ci;
}

/* Best-first search from root node ri.  k2: also certify the runner-up.  Returns status.
   Outputs p1,p2 and node indices l1,l2 (-1 if none). */
static int search(Ctx *c, int ri, int k2, double *p1, double *p2, int *l1, int *l2, long *exp_out) {
    int W = c->W; double b1 = 0.0, b2 = 0.0; int n1 = -1, n2 = -1; long exp = 0;
    Node *root = &c->pool[ri];
    if (root->p > b1) { b1 = root->p; n1 = ri; }
    root->bound = bound_of(c, ri, k2 ? b2 : b1);
    c->nheap = 0; heap_push(c, root->bound, ri);
    while (c->nheap > 0) {
        HeapEnt top = heap_pop(c);
        double thr = k2 ? b2 : b1;
        if (top.bound <= thr) break;
        if ((exp & 255) == 0 && now_sec() > c->deadline) { c->status = 1; break; }
        if (c->gen >= c->gen_cap) { c->status = 2; break; }
        exp++;
        for (int d = 1; d < W; d++) {
            int ci = make_child(c, top.idx, d); if (ci < 0) { c->status = 3; goto done; }
            Node *ch = &c->pool[ci];
            if (ch->p > b1) { b2 = b1; n2 = n1; b1 = ch->p; n1 = ci; }
            else if (ch->p > b2) { b2 = ch->p; n2 = ci; }
            thr = k2 ? b2 : b1;
            ch->bound = bound_of(c, ci, thr);
            if (ch->bound > thr) heap_push(c, ch->bound, ci);
        }
    }
done:
    *p1 = b1; *p2 = b2; *l1 = n1; *l2 = n2; *exp_out = exp;
    return c->status;
}

static int extract(Ctx *c, int ni, int *out) {   /* labelling of node ni, returns length */
    int len = 0, i = ni; int tmp[4096];
    while (i >= 0 && len < 4096) { Node *n = &c->pool[i]; if (n->sym > 0) tmp[len++] = n->sym; i = n->parent; }
    for (int k = 0; k < len; k++) out[k] = tmp[len - 1 - k];
    return len;
}

int ctc_exact_backward(const double *table, int T, int W, double time_limit, long gen_cap, int pool_cap,
                       double *out_p, int *out_l1, int *out_len1, int *out_l2, int *out_len2, long *stats,
                       double *H_out) {
    Ctx c; memset(&c, 0, sizeof c);
    c.table = table; c.T = T; c.W = W; int T1 = T + 1;
    c.Hhat = (double *)calloc((size_t)W * T1, sizeof(double)); c.Mmax = (double *)calloc(T1, sizeof(double));
    c.cappool = pool_cap; c.pool = (Node *)calloc(pool_cap, sizeof(Node));
    c.capheap = 1024; c.heap = (HeapEnt *)malloc(c.capheap * sizeof(HeapEnt));
    c.gen_cap = gen_cap; c.deadline = now_sec() + time_limit; c.status = 0;
    /* trivial seed Hhat_d(t) = y_t[d]; only t' > t is read by the search from t, and those are exact. */
    for (int d = 1; d < W; d++) for (int t = 1; t <= T; t++) c.Hhat[d * T1 + t] = table[(t - 1) * W + d];
    for (int t = 1; t <= T; t++) { double m = 0; for (int d = 1; d < W; d++) if (c.Hhat[d*T1+t] > m) m = c.Hhat[d*T1+t]; c.Mmax[t] = m; }
    /* backward: exact H_c(t) for t = T..1 */
    for (int t = T; t >= 1 && c.status == 0; t--) {
        for (int cc = 1; cc < W; cc++) {
            reset_pool(&c);
            int ri = new_node(&c); Node *r = &c.pool[ri];
            r->parent = -1; r->sym = cc; r->tmin = t;
            r->An[t] = table[(t - 1) * W + cc];
            for (int s = t + 1; s <= T; s++) { r->An[s] = r->An[s-1] * table[(s-1)*W + cc]; r->Ab[s] = (r->Ab[s-1] + r->An[s-1]) * table[(s-1)*W]; }
            r->p = r->Ab[T] + r->An[T];
            double p1, p2; int l1, l2; long e;
            search(&c, ri, 0, &p1, &p2, &l1, &l2, &e);
            c.exp_bwd += e;
            if (c.status) break;
            c.Hhat[cc * T1 + t] = p1;
        }
        double m = 0; for (int d = 1; d < W; d++) if (c.Hhat[d*T1+t] > m) m = c.Hhat[d*T1+t]; c.Mmax[t] = m;
    }
    double p1 = 0, p2 = 0; int l1 = -1, l2 = -1; long e = 0;
    if (c.status == 0) {
        reset_pool(&c);
        int ri = new_node(&c); Node *r = &c.pool[ri];
        r->parent = -1; r->sym = 0; r->tmin = 0; r->Ab[0] = 1.0;
        for (int s = 1; s <= T; s++) r->Ab[s] = r->Ab[s-1] * table[(s-1)*W];
        r->p = r->Ab[T] + r->An[T];
        search(&c, ri, 1, &p1, &p2, &l1, &l2, &e);
        c.exp_final = e;
        *out_len1 = l1 >= 0 ? extract(&c, l1, out_l1) : 0;
        *out_len2 = l2 >= 0 ? extract(&c, l2, out_l2) : 0;
    }
    out_p[0] = p1; out_p[1] = p2;
    stats[0] = c.gen; stats[1] = c.exp_final; stats[2] = c.exp_bwd; stats[3] = c.status;
    if (H_out) memcpy(H_out, c.Hhat, (size_t)W * T1 * sizeof(double));
    reset_pool(&c); free(c.pool); free(c.heap); free(c.Hhat); free(c.Mmax);
    return c.status;
}

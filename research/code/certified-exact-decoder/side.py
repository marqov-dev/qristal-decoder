"""Direction 2/3 (Viterbi-collapse / beam incumbents, DFS B&B) and theta sensitivity of the suffix-tree bound."""
import sys, os, math, random, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bounds import *
def gmean(xs): return math.exp(sum(math.log(max(x, 1e-300)) for x in xs)/len(xs))
CAP = 100000
print("== D2/D3: incumbent quality vs expansions (Graves bound).  'exp p*' = incumbent is the exact mode (perfect incumbent) ==")
print(f"{'T':>4} {'W':>2} {'conf':>5} {'n':>3} {'vit==mode':>9} {'beam32==mode':>12} {'p_vit/p*':>9} | {'exp none':>9} {'exp vit':>9} {'exp beam':>9} {'exp p*':>9} {'dfsBB beam':>10} {'dfsBB p*':>9}")
for T, W, conf in [(24,5,0.8),(32,5,0.8),(48,5,0.8),(64,5,0.8),(64,5,0.7)]:
    rng = random.Random(77+T); hits_v = hits_b = 0; ratios = []; e0 = []; ev = []; eb = []; es = []; db = []; ds = []; n = 0
    for _ in range(4):
        tb = peaky_table(T, W, rng, conf)
        ref = decode_exact_backward(tb, cap=CAP)
        if ref[4]: continue
        ps, ls = ref[0], ref[1]
        lv, pv = viterbi_collapse(tb); lb, pb = beam_incumbent(tb, 32)
        r0 = decode_graves(tb, cap=CAP)
        if r0[4]: continue
        n += 1; hits_v += (lv == ls); hits_b += (lb == ls); ratios.append(pv/ps)
        rv = decode_graves(tb, pv, lv, cap=CAP); rb = decode_graves(tb, pb, lb, cap=CAP); rs = decode_graves(tb, ps, ls, cap=CAP)
        bb = dfs_bb(tb, lambda nd: graves_F(nd, tb), pb, lb, cap=CAP); bs = dfs_bb(tb, lambda nd: graves_F(nd, tb), ps, ls, cap=CAP)
        e0.append(r0[2]); ev.append(rv[2]); eb.append(rb[2]); es.append(rs[2]); db.append(bb[2]); ds.append(bs[2])
    if n:
        print(f"{T:>4} {W:>2} {conf:>5} {n:>3} {hits_v:>5}/{n:<3} {hits_b:>7}/{n:<4} {gmean(ratios):>9.3f} | {gmean(e0):>9.1f} {gmean(ev):>9.1f} {gmean(eb):>9.1f} {gmean(es):>9.1f} {gmean(db):>10.1f} {gmean(ds):>9.1f}", flush=True)

print("\n== D1a theta sensitivity: theta = p_hat^alpha (p_hat = beam-32 incumbent).  cells: expansions / generated (incl. suffix tree) / |S| ==")
alphas = (0.25, 0.4, 0.5, 0.6, 0.75)
print(f"{'T':>4} {'W':>2} {'conf':>5} {'p*':>9} | " + " ".join(f"{'a='+str(a):>18}" for a in alphas) + " | graves gen")
for T, W, conf in [(48,5,0.8),(64,5,0.8),(64,5,0.7),(100,5,0.8)]:
    rng = random.Random(99+T); cols = {a: [] for a in alphas}; gg = []; ps = []
    for _ in range(3):
        tb = peaky_table(T, W, rng, conf)
        ref = decode_exact_backward(tb, cap=CAP)
        if ref[4]: continue
        ps.append(ref[0]); lb, pb = beam_incumbent(tb, 32)
        for a in alphas:
            cnt = Counter(); r = decode_bidir(tb, pb**a, cap=300000, cnt=cnt); cols[a].append((r[2] if not r[4] else 300000, cnt.gen, r[5]))
        cnt = Counter(); r = decode_graves(tb, cap=CAP, cnt=cnt); gg.append(cnt.gen)
    if ps:
        print(f"{T:>4} {W:>2} {conf:>5} {gmean(ps):>9.2e} | " + " ".join(f"{gmean([x[0] for x in cols[a]]):>6.0f}/{gmean([x[1] for x in cols[a]]):>7.0f}/{gmean([x[2] for x in cols[a]]):>3.0f}" for a in alphas) + f" | {gmean(gg):>9.0f}", flush=True)
print("(cells: expansions / generated / |S|; graves gen capped at 4e5)")

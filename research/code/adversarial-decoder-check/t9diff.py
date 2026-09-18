"""Behavioural diff: T2b decode_exact_backward vs T9 decode_exactbwd on identical instances."""
import sys, random, time
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'certified-exact-decoder'))
import bounds as T2B
from t9core import decode_exactbwd, decode_graves
import t9bench as B
rng = random.Random(99)
cases = [('peaky.8', 32, 5, lambda T, W: B.fam_peaky(T, W, rng, 0.8)), ('peaky.8', 64, 5, lambda T, W: B.fam_peaky(T, W, rng, 0.8)),
         ('peaky.5', 32, 5, lambda T, W: B.fam_peaky(T, W, rng, 0.5)), ('random', 16, 5, lambda T, W: B.fam_uniform_random(T, W, rng)),
         ('random', 20, 8, lambda T, W: B.fam_uniform_random(T, W, rng)), ('flat', 12, 5, lambda T, W: B.fam_flat(T, W, rng)),
         ('flat', 16, 4, lambda T, W: B.fam_flat(T, W, rng)), ('neartie3', 48, 3, lambda T, W: B.fam_neartie(T, W, rng, spread=3)),
         ('spreadpair', 48, 5, lambda T, W: B.fam_spread_pair(T, W, rng)), ('degenerate', 48, 5, lambda T, W: B.fam_degenerate(T, W, rng))]
same_exp = same_gen = same_ans = n = 0
for name, T, W, g in cases:
    for i in range(2):
        tbl = g(T, W)
        c = T2B.Counter(); t0 = time.time(); r = T2B.decode_exact_backward(tbl, cnt=c); t2b = time.time()-t0
        t0 = time.time(); m = decode_exactbwd(tbl, W); t9 = time.time()-t0
        n += 1
        e_ok = (r[2] == m['exp_final'] and r[5] == m['exp_back']); g_ok = (c.gen == m['gen'])
        a_ok = (r[1] == m['mode'] and abs(r[0]-m['p']) <= 1e-12*r[0])
        same_exp += e_ok; same_gen += g_ok; same_ans += a_ok
        print(f"{name:<10} T={T:>3} W={W} | T2b: expF={r[2]:>6} expB={r[5]:>7} gen={c.gen:>8} p={r[0]:.6e} {t2b:6.2f}s | T9: expF={m['exp_final']:>6} expB={m['exp_back']:>7} gen={m['gen']:>8} p={m['p']:.6e} {t9:6.2f}s | same exp={e_ok} gen={g_ok} ans={a_ok}")
print(f"GATE T2b vs T9 on {n} identical instances: same expansions {same_exp}/{n}, same generations {same_gen}/{n}, same (mode, p*) {same_ans}/{n}")

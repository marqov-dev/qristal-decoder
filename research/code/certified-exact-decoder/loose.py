"""Looseness of the policy-DP bound: ratio Hhat^pol_c(t) / H_c(t) (exact backward) vs remaining frames T-t."""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bounds import *
print(f"{'W':>2} {'conf':>5} {'T':>4} | ratio at T-t = " + " ".join(f"{k:>8}" for k in (10, 25, 50, 100, 200)) + " | base = ratio^(1/(T-t)) at T-t=T-1")
for W, conf in [(5,0.8),(5,0.9),(10,0.9),(5,0.7)]:
    for T in (101, 201):
        rng = random.Random(5+T+W); tb = peaky_table(T, W, rng, conf)
        Hp = H_policy(tb); He, _ = H_exact_backward(tb, Hp)
        def ratio(rem):
            t = T - rem
            if t < 1: return float('nan')
            return max(Hp[c][t]/He[c][t] for c in range(1, W) if He[c][t] > 0)
        rs = [ratio(k) for k in (10, 25, 50, 100, 200)]
        print(f"{W:>2} {conf:>5} {T:>4} | " + " "*15 + " ".join(f"{r:>8.2e}" for r in rs) + f" | {ratio(T-1)**(1/(T-1)):.4f}")

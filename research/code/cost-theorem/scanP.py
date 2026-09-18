"""70%-blank peaky generator (T2b/T9's family): the insertion-pressure picture. For each (conf, T, W): max blank-run
length n_b, pressure = n_b q/rho (q = (1-conf)/(W-1)), whether the mode is the greedy collapse, exp_final/D, gen/(T^2 W^2)."""
import random, math
from a2core import *
from ctc import collapse
rng = random.Random(21); rows = []
for W in (5,):
    for conf in (0.5, 0.55, 0.6, 0.65, 0.7, 0.8, 0.9):
        for T in (32, 48, 64):
            for rep in range(2):
                tbl = peaky_table(T, W, rng, conf); q = (1 - conf) / (W - 1)
                runs = []; cur = 0
                for row in tbl:
                    if row.index(max(row)) == 0: cur += 1
                    else:
                        if cur: runs.append(cur)
                        cur = 0
                if cur: runs.append(cur)
                nb = max(runs) if runs else 0
                greedy = collapse(tuple(row.index(max(row)) for row in tbl))
                r = decode_exactbwd(tbl, W, cap=600_000)
                if r['capped']:
                    rows.append((conf, T, nb, nb * q / conf, sum(x * q / conf for x in runs), None, None, None, r['gen'])); continue
                rows.append((conf, T, nb, nb * q / conf, sum(x * q / conf for x in runs), r['mode'] == greedy, len(r['mode']), r['exp_final'] / max(len(r['mode']), 1), r['gen'] / (T * T * W * W)))
for row in rows:
    print("  conf=%.2f T=%d max_blank_run=%d pressure_max=%.2f pressure_sum=%.2f mode==greedy=%s D=%s exp_final/D=%s gen/(T^2W^2)=%s" % tuple(x if not isinstance(x, float) else round(x, 3) for x in row))

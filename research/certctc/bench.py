"""Synthetic scaling bench: reproduces the T2b law (peaky) and the T9 worst case (flat rows).

    python -m certctc bench [--gen-cap N] [--time-limit S] [--W 5,32] [--T 16,32,64,128] [--seed 7] [--out FILE]

Families: peaky conf in {0.5, 0.6, 0.8, 0.9} (toolkit `peaky_table`: ~70 % blank frames, one winner
per frame with mass conf, the rest uniform) and flat (every row 1/W).  One instance per cell.
Columns: gen = all node generations (T*(W-1) backward searches + final), law = gen / (0.1 T^2 W^2),
expF = final-search expansions, expF/D, predicted flat expansions ~ c (W-2)^{T/2}.
"""
import json, math, random, sys, time

from .decoder import decode, BudgetExceeded
from ._toolkit_ctc import peaky_table


def flat_table(T, W): return [[1.0 / W] * W for _ in range(T)]


def cells(Ws, Ts):
    for fam in ('peaky0.5', 'peaky0.6', 'peaky0.8', 'peaky0.9', 'flat'):
        for W in Ws:
            for T in Ts:
                yield fam, W, T


def make(fam, T, W, rng):
    if fam == 'flat': return flat_table(T, W)
    return peaky_table(T, W, rng, float(fam[5:]))


def run(args):
    Ws = [int(x) for x in args.W.split(',')]; Ts = [int(x) for x in args.T.split(',')]
    rng = random.Random(args.seed)
    out = open(args.out, 'a') if args.out else None
    print('| family | W | T | status | D | p* | p2 | margin | expF | expF/D | gen | gen/(0.1 T²W²) | (W-2)^(T/2) | sec | backend |')
    print('|---|--:|--:|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|')
    for fam, W, T in cells(Ws, Ts):
        tb = make(fam, T, W, rng)
        law = 0.1 * T * T * W * W; pred = (W - 2) ** (T / 2.0)
        try:
            c = decode(tb, backend=args.backend, time_limit=args.time_limit, max_generations=args.gen_cap)
            row = dict(family=fam, W=W, T=T, status='ok', D=c.D, p1=c.p_mode, p2=c.p_runner_up, margin=c.margin,
                       expF=c.expansions_final, gen=c.generations_total, sec=c.wall_seconds, backend=c.backend)
            print('| %s | %d | %d | ok | %d | %.3e | %.3e | %.4g | %d | %.2f | %d | %.2f | %.3g | %.2f | %s |' % (
                fam, W, T, c.D, c.p_mode, c.p_runner_up, c.margin, c.expansions_final,
                c.expansions_final / max(c.D, 1), c.generations_total, c.generations_total / law, pred, c.wall_seconds, c.backend), flush=True)
        except BudgetExceeded as e:
            p = e.partial
            row = dict(family=fam, W=W, T=T, status=e.status, gen=p['gen'], sec=p['wall_seconds'], backend=p['backend'])
            print('| %s | %d | %d | CAP (%s) | - | - | - | - | - | - | >%d | >%.2f | %.3g | %.2f | %s |' % (
                fam, W, T, e.status, p['gen'], p['gen'] / law, pred, p['wall_seconds'], p['backend']), flush=True)
        if out: out.write(json.dumps(row) + '\n'); out.flush()
    return 0

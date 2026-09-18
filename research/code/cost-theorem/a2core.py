"""A2 theory harness: families, exact brute force helpers, and the per-search bound checks.
Uses T9's independent implementation (read-only import) as the decoder under test."""
import sys, random, math
sys.dont_write_bytecode = True
from fractions import Fraction
from itertools import product
import os
T9 = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'adversarial-decoder-check')
TK = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'certified-exact-decoder')
sys.path.insert(0, T9); sys.path.insert(0, TK)
from t9core import (decode_exactbwd, brute_all, brute_suffix_masses, prob, suffix_g, root_empty, root_forced,
                    child, bound_H, best_first, Stats, compute_H, BLANK)
from ctc import peaky_table, ctc_forward

# ---------------- families ----------------
def fam_blankdom(T, W, rho, F=Fraction):
    """every frame: blank with mass rho, uniform residual q=(1-rho)/(W-1) on the W-1 symbols. k=0 ambiguous frames at any threshold <= rho."""
    rho = F(rho); q = (1 - rho) / (W - 1)
    return [[rho] + [q] * (W - 1) for _ in range(T)]

def fam_flat(T, W, F=Fraction):
    return [[F(1, W)] * W for _ in range(T)]

def fam_alt(T, W, rho, F=Fraction):
    """odd frames: symbol 1 with mass rho, symbol 2 with 1-rho, blank 0; even frames: deterministic blank.
    Labellings = {1,2}^(T/2) with p = rho^#1 (1-rho)^#2; N(p*/F) is quasi-polynomial, decoder expands D+1."""
    rho = F(rho); rows = []
    for t in range(T):
        if t % 2 == 0:
            r = [F(0)] * W; r[1] = rho; r[2] = 1 - rho
        else:
            r = [F(0)] * W; r[0] = F(1)
        rows.append(r)
    return rows

def fam_padded_flat(T, k, W, F=Fraction):
    """k flat frames followed by T-k deterministic-blank frames (k ambiguous, zero deviation mass elsewhere)."""
    rows = [[F(1, W)] * W for _ in range(k)]
    for _ in range(T - k):
        r = [F(0)] * W; r[0] = F(1); rows.append(r)
    return rows

def fam_strict_k(T, W, k, rng, F=Fraction):
    """k random-Dirichlet-ish frames at random positions; other frames are point masses (blank w.p. 0.6)."""
    amb = set(rng.sample(range(T), k)); rows = []
    for t in range(T):
        if t in amb:
            r = [F(rng.randint(1, 20)) for _ in range(W)]; s = sum(r); rows.append([v / s for v in r])
        else:
            win = 0 if rng.random() < 0.6 else rng.randrange(1, W)
            r = [F(0)] * W; r[win] = F(1); rows.append(r)
    return rows

def fam_peaky(T, W, rng, conf, F=Fraction):
    return [[F(v).limit_denominator(10**9) for v in row] for row in peaky_table(T, W, rng, conf)]

def to_float(tbl): return [[float(v) for v in r] for r in tbl]

# ---------------- exact helpers ----------------
def greedy_mass(tbl):
    P = 1
    for r in tbl: P = P * max(r)
    return P

def near_mode_prefix_count(ex, ps, F):
    """|{prefixes u of labellings l with p(l) >= ps/F}| and N(F) = #labellings"""
    prefixes = set(); N = 0
    for l, p in ex.items():
        if p * F >= ps:
            N += 1
            for k in range(len(l) + 1): prefixes.add(l[:k])
    return len(prefixes), N

def norepeat_count(W, n):
    return 1 if n == 0 else (W - 1) * (W - 2) ** (n - 1)

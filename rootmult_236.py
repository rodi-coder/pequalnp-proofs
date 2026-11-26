#!/usr/bin/env python3
"""Study: max multiplicity of a positive real root of
   P = s1*g1^3 + s2*g2^3 + s3*g3^3, each g_i a trinomial (<=3 terms), P != 0.
Goal: understand the ceiling (claimed <= 14) and how tight it is.
"""
import numpy as np
from itertools import combinations
import sys, time

rng = np.random.default_rng(12345)

def poly_coeffs(g):
    # g given as list of (exp, coeff)
    out = {}
    for e, c in g:
        out[e] = out.get(e, 0.0) + c
    return out

def poly_mul(a, b):
    out = {}
    for ea, ca in a.items():
        for eb, cb in b.items():
            out[ea+eb] = out.get(ea+eb, 0.0) + ca*cb
    return out

def poly_cube(g):
    return poly_mul(poly_mul(g, g), g)

def coeff_vector(poly, maxdeg):
    v = np.zeros(maxdeg+1)
    for e, c in poly.items():
        if 0 <= e <= maxdeg:
            v[e] = c
    return v

def max_mult_positive_roots(coeffs):
    """coeffs low-to-high. Return max multiplicity of a positive real root (via clustering)."""
    c = coeffs[::-1]  # high-to-low for numpy.roots
    if not any(abs(x) > 1e-14 for x in c[1:]):
        return 0
    try:
        rts = np.roots(c)
    except Exception:
        return 0
    pos = rts[(rts.real > 1e-7) & (np.abs(rts.imag) < 1e-3 * np.maximum(1.0, np.abs(rts.real)))]
    # cluster positive real roots
    if len(pos) == 0:
        return 0
    pos_sorted = np.sort(pos.real)
    maxc = 1
    cur = 1
    for i in range(1, len(pos_sorted)):
        if pos_sorted[i] - pos_sorted[i-1] < 1e-3 * max(1.0, abs(pos_sorted[i])):
            cur += 1
        else:
            cur = 1
        maxc = max(maxc, cur)
    return maxc

def one_sample(maxdeg=12):
    gs = []
    for _ in range(3):
        exps = rng.choice(maxdeg+1, size=3, replace=False)
        coefs = rng.uniform(-2, 2, size=3)
        g = dict(zip(exps, coefs))
        gs.append(g)
    signs = rng.choice([1.0, -1.0], size=3)
    P = {}
    for s, g in zip(signs, gs):
        c3 = poly_cube(g)
        for e, c in c3.items():
            P[e] = P.get(e, 0.0) + s*c
    # drop ~zero
    P = {e: c for e, c in P.items() if abs(c) > 1e-12}
    if not P:
        return 0
    maxdeg = max(P.keys())
    coeffs = coeff_vector(P, maxdeg)
    return max_mult_positive_roots(coeffs)

N = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
t0 = time.time()
hist = {}
mx = 0
for _ in range(N):
    m = one_sample()
    hist[m] = hist.get(m, 0) + 1
    mx = max(mx, m)
print("samples=%d  time=%.1fs  max multiplicity seen=%d" % (N, time.time()-t0, mx))
print("hist (mult: count):")
for k in sorted(hist):
    print("  %d : %d" % (k, hist[k]))

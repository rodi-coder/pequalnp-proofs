#!/usr/bin/env python3
"""Exact minimum circuit sizes (fan-in <= 2, AND/OR/NOT) for the 7-vertex edge function."""
import sys, time

N = 7
MASK = (1 << (1 << N)) - 1
EDGES = [(0,3),(0,4),(1,4),(0,5),(2,5),(4,5),(0,6),(1,6),(2,6),(3,6)]

f_t = 0
for v in range(1 << N):
    if any(((v >> a) & 1) and ((v >> b) & 1) for a, b in EDGES):
        f_t |= 1 << v

inp = [sum(1 << v for v in range(1 << N) if v & (1 << i)) for i in range(N)]
ZERO, ONE = 0, MASK

t0 = time.time()
c0 = {x: 0 for x in inp}; c0[ZERO] = 0; c0[ONE] = 1
best0 = {}
c1 = dict(c0); best1 = {}

def relax(c, best, h, cost, op, g1, g2):
    old = c.get(h)
    if old is None or cost < old:
        c[h] = cost
        best[h] = (op, g1, g2, cost)
        return True
    return False

def closure(c, best):
    changed = True
    nround = 0
    while changed:
        changed = False
        nround += 1
        keys = list(c)
        for i, f in enumerate(keys):
            cf = c[f]
            for g in keys[i:]:
                cg = c[g]
                if relax(c, best, f & g, cf + cg + 1, 'AND', f, g): changed = True
                if relax(c, best, f | g, cf + cg + 1, 'OR', f, g): changed = True
    return nround

r0 = closure(c0, best0)
changed = True
nround = 0
while changed:
    changed = False
    nround += 1
    for f in list(c1):
        cf = c1[f]
        for g in c0:
            cg = c0[g]
            if relax(c1, best1, f & g, cf + cg + 1, 'AND', f, g): changed = True
            if relax(c1, best1, f | g, cf + cg + 1, 'OR', f, g): changed = True
    for f in c0:
        if relax(c1, best1, (~f) & MASK, c0[f] + 1, 'NOT', f, None): changed = True
print("rounds c0=%d c1=%d |c0|=%d |c1|=%d time=%.1fs" % (r0, nround, len(c0), len(c1), time.time()-t0), file=sys.stderr)
M_mono = c0.get(f_t)
M_1not = c1.get(f_t)
print("M_mono (NOT-free min size) =", M_mono)
print("M_1not (<=1 NOT min size)  =", M_1not)
print("REFUTABLE (M_1not < M_mono):", M_1not is not None and M_mono is not None and M_1not < M_mono)

def build_circuit(best, f_t, inp):
    wire_of = {}
    gates = []
    def assign(f):
        if f in wire_of: return wire_of[f]
        for i, x in enumerate(inp):
            if f == x: return i
        if f == ZERO:
            # wire that does not exist yet when the referencing gate is evaluated reads false;
            # use the referencing gate's own future wire index (>= current wire count)
            return 7 + len(gates)
        op, g1, g2, cost = best[f]
        if op == 'NOT':
            w = assign(g1)
            ins = [w]
        else:
            w1 = assign(g1); w2 = assign(g2)
            ins = [w1, w2]
        idx = len(gates)
        gates.append((op, ins))
        wire_of[f] = 7 + idx
        return wire_of[f]
    root = assign(f_t)
    return gates, root

def sim(gates, root, x):
    wires = list(x)
    for op, ins in gates:
        vals = [wires[i] if 0 <= i < len(wires) else False for i in ins]
        if op == 'AND': v = all(vals) if vals else True
        elif op == 'OR': v = any(vals) if vals else False
        else: v = (not vals[0]) if vals else True
        wires.append(v)
    return (wires[root] if 0 <= root < len(wires) else False)

def show(best, label):
    gates, root = build_circuit(best, f_t, inp)
    nnot = sum(1 for op, _ in gates if op == 'NOT')
    ok = all(sim(gates, root, [(v >> i) & 1 for i in range(N)]) == bool((f_t >> v) & 1) for v in range(1 << N))
    print("\n%s: %d gates, output wire %s, NOT gates: %d, verify: %s" % (label, len(gates), root, nnot, "OK" if ok else "MISMATCH"))
    for k, (op, ins) in enumerate(gates):
        print("  gate %d (wire %d): %s %s" % (k, 7+k, op, ins))

if M_mono is not None:
    show(best0, "NOT-free optimum")
if M_1not is not None:
    show(best1, "<=1 NOT optimum")

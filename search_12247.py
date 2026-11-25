#!/usr/bin/env python3
"""Exact minimum circuit size (fan-in <= 2, AND/OR/NOT, any NOTs) for the 6-input function
of L-meta-12247, plus the NOT-free minimum. c[f] = min size with any NOTs is exact:
root-gate decomposition, combine minimum subcircuits."""
import sys, time, json

N = 6
MASK = (1 << (1 << N)) - 1
TABLE = 4269834240 * 2**32 + 2147516416
f_t = TABLE & MASK

inp = [sum(1 << v for v in range(1 << N) if v & (1 << i)) for i in range(N)]
ZERO, ONE = 0, MASK

def relax(c, best, h, cost, op, g1, g2):
    old = c.get(h)
    if old is None or cost < old:
        c[h] = cost
        best[h] = (op, g1, g2, cost)
        return True
    return False

def closure(c, best, allow_not):
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
        if allow_not:
            for f in keys:
                if relax(c, best, (~f) & MASK, c[f] + 1, 'NOT', f, None): changed = True
    return nround

t0 = time.time()
c0 = {x: 0 for x in inp}; c0[ZERO] = 0; c0[ONE] = 1
b0 = {}
r0 = closure(c0, b0, False)
c1 = {x: 0 for x in inp}; c1[ZERO] = 0; c1[ONE] = 1
b1 = {}
r1 = closure(c1, b1, True)
print("rounds: noNOT=%d anyNOT=%d |noNOT|=%d |anyNOT|=%d time=%.1fs" % (r0, r1, len(c0), len(c1), time.time()-t0), file=sys.stderr)
M_mono = c0.get(f_t)
M_any = c1.get(f_t)
print("M_mono (NOT-free min size) =", M_mono)
print("M_any  (any-NOT min size)  =", M_any)
print("PROVABLE (M_any < M_mono):", M_any is not None and M_mono is not None and M_any < M_mono)

def build_circuit(best, target):
    wire_of = {}
    gates = []
    def assign(f):
        if f in wire_of: return wire_of[f]
        for i, x in enumerate(inp):
            if f == x: return i
        if f == ZERO:
            return 7 + len(gates)
        op, g1, g2, cost = best[f]
        if op == 'NOT':
            w = assign(g1); ins = [w]
        else:
            w1 = assign(g1); w2 = assign(g2); ins = [w1, w2]
        idx = len(gates)
        gates.append((op, ins))
        wire_of[f] = 6 + 1 + idx
        return wire_of[f]
    root = assign(target)
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
    gates, root = build_circuit(best, f_t)
    nnot = sum(1 for op, _ in gates if op == 'NOT')
    ok = all(sim(gates, root, [(v >> i) & 1 for i in range(N)]) == bool((f_t >> v) & 1) for v in range(1 << N))
    print("\n%s: %d gates, output wire %s, NOT gates: %d, verify: %s" % (label, len(gates), root, nnot, "OK" if ok else "MISMATCH"))
    for k, (op, ins) in enumerate(gates):
        print("  gate %d (wire %d): %s %s" % (k, 7+k, op, ins))

if M_mono is not None:
    show(b0, "NOT-free optimum")
if M_any is not None:
    show(b1, "any-NOT optimum")
# also: is the any-NOT optimum actually using NOTs?
if M_any is not None:
    gates, root = build_circuit(b1, f_t)
    nnot = sum(1 for op, _ in gates if op == 'NOT')
    print("\nany-NOT optimum uses %d NOT gates" % nnot)

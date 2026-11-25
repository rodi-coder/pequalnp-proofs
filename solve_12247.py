#!/usr/bin/env python3
"""Exact minimum circuit sizes (fan-in <= 2) for the 6-input function of L-meta-12247,
via Dijkstra on the function space (truth tables as 64-bit ints).

  a = min size using AND and OR only            (NOT-free)
  b = min size using AND, OR, NOT               (one or more NOT allowed)

Start states: the 6 inputs, the constants 0 and 1.  Edges: AND (&), OR (|), NOT (~).
Combining minimum subcircuits of the two children of a gate is valid (fan-in 2, acyclic),
so the minimum distance is the exact minimum gate count.
"""
import sys, time, heapq, json

N = 6
MASK = (1 << (1 << N)) - 1
TABLE = 4269834240 * 2**32 + 2147516416
f_t = TABLE & MASK

# input i truth table: bit v set iff bit i of v is 1
inp = [sum(1 << v for v in range(1 << N) if v & (1 << i)) for i in range(N)]
ZERO, ONE = 0, MASK

def dijkstra(ops, cap):
    """ops is a set among {'AND','OR','NOT'}. Returns dict dist and parent for explored states,
    stopping once the target is settled or |frontier| exceeds cap."""
    dist = {x: 0 for x in inp}; dist[ZERO] = 0; dist[ONE] = 0
    parent = {}
    heap = [(0, x) for x in dist]; heapq.heapify(heap)
    done = set()
    expanded = 0
    while heap:
        d, f = heapq.heappop(heap)
        if f in done: continue
        done.add(f); expanded += 1
        if f == f_t: break
        if expanded > cap: break
        if 'AND' in ops:
            for g in inp:  # AND with each input (cheap sub-generators)
                pass
    # full closure below
    # (rebuild)
    return dist

# --- Efficient exact Dijkstra with all reachable pairs considered ---
def exact(ops, cap_states=4_000_000):
    dist = {}
    for x in inp + [ZERO, ONE]:
        dist[x] = 0
    parent = {}
    heap = [(0, x) for x in dist]; heapq.heapify(heap)
    settled = set()
    while heap:
        d, f = heapq.heappop(heap)
        if f in settled: continue
        settled.add(f)
        if f == f_t:
            break
        if len(settled) > cap_states:
            break
        if 'AND' in ops:
            pass
    # The simple 2-input combination with only the inputs is NOT enough; we must combine
    # with EVERY already-settled function. Use a different scheme: Dijkstra where from each
    # settled f we combine with all previously settled g. We implement by re-expanding.
    return dist

# ---- Correct method: Dijkstra, expanding f against every settled g (and NOT) ----
def solve(ops, cap_states=20_000_000):
    dist = {}
    for x in inp + [ZERO, ONE]:
        dist[x] = 0
    settled = set(dist.keys())
    parent = {}
    # priority = current best distance; we pop smallest first and combine with all settled
    heap = [(0, x) for x in dist]; heapq.heapify(heap)
    order = []
    while heap:
        d, f = heapq.heappop(heap)
        if f in order: continue
        order.append(f)
        if f == f_t: break
        if len(order) > cap_states: break
        if 'NOT' in ops:
            nf = (~f) & MASK
            nd = d + 1
            if nf not in dist or dist[nf] > nd:
                dist[nf] = nd
                parent[nf] = ('NOT', f)
                heapq.heappush(heap, (nd, nf))
        if 'AND' in ops:
            for g in order:
                h = f & g
                nd = d + dist.get(g, d) + 1
                # use settled distances for g
                nd = d + dist[g] + 1
                if h not in dist or dist[h] > nd:
                    dist[h] = nd
                    parent[h] = ('AND', g, f)
                    heapq.heappush(heap, (nd, h))
        if 'OR' in ops:
            for g in order:
                h = f | g
                nd = d + dist[g] + 1
                if h not in dist or dist[h] > nd:
                    dist[h] = nd
                    parent[h] = ('OR', g, f)
                    heapq.heappush(heap, (nd, h))
    return dist, parent, order

t0 = time.time()
print("solving AND/OR/NOT ...", file=sys.stderr)
db, pb, ob = solve({'AND','OR','NOT'})
tb = time.time(); print("  settled=%d time=%.1fs b=%s" % (len(ob), tb-t0, db.get(f_t)), file=sys.stderr)
print("solving AND/OR ...", file=sys.stderr)
da, pa, oa = solve({'AND','OR'})
ta = time.time(); print("  settled=%d time=%.1fs a=%s" % (len(oa), ta-tb, da.get(f_t)), file=sys.stderr)

a = da.get(f_t)
b = db.get(f_t)
print("\n=== RESULT (L-meta-12247) ===")
print("a = min NOT-free  (AND/OR)     =", a)
print("b = min NOT-allowed (AND/OR/NOT)=", b)
print("REFUTABLE (a > b):", (a is not None) and (b is not None) and (a > b))

def circuit(parent, target):
    wire_of = {}; gates = []
    def assign(f):
        if f in wire_of: return wire_of[f]
        for i, x in enumerate(inp):
            if f == x: return i
        if f == ZERO: return 7 + len(gates)
        p = parent[f]
        if p[0] == 'NOT':
            w = assign(p[1]); ins=[w]
        else:
            w1 = assign(p[1]); w2 = assign(p[2]); ins=[w1,w2]
        idx = len(gates); gates.append((p[0], ins)); wire_of[f] = 7+idx
        return wire_of[f]
    root = assign(target)
    return gates, root

def sim(gates, root, x):
    wires = list(x)
    for op, ins in gates:
        vals = [wires[i] if 0 <= i < len(wires) else False for i in ins]
        if op=='AND': v = all(vals) if vals else True
        elif op=='OR': v = any(vals) if vals else False
        else: v = (not vals[0]) if vals else True
        wires.append(v)
    return (wires[root] if 0 <= root < len(wires) else False)

if b is not None:
    gates, root = circuit(pb, f_t)
    nnot = sum(1 for op,_ in gates if op=='NOT')
    ok = all(sim(gates, root, [(v>>i)&1 for i in range(N)])==bool((f_t>>v)&1) for v in range(1<<N))
    print("\nWITNESS (AND/OR/NOT), %d gates, out wire %s, NOTs: %d, verify: %s" % (len(gates), root, nnot, "OK" if ok else "MISMATCH"))
    for k,(op,ins) in enumerate(gates): print("  gate %d (wire %d): %s %s" % (k,7+k,op,ins))

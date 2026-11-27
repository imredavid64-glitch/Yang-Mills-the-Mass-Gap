r"""
Numerical test of the Dobrushin-type induction proved in proof/THEOREM.md (Theorem A),
on a toy polymer gas where Z can be computed exactly.

Toy gas: polymers = intervals of 1..3 consecutive sites on a chain of N sites, two
polymers incompatible iff they share a site, real weights with RANDOM SIGNS (so no
positivity is available), scaled so that condition (C_delta) holds:

   u(g) := |zeta(g)| e^{alpha |g|} <= 1/2           for all g,
   sum_{g' ~ g0, g' != g0} u(g') e^{delta |g'|} / (1 - u(g'))  <=  alpha |g0| / 2   for all g0.

Claims tested on random sub-gases Theta (arbitrary subsets of polymers):
  T1  Z_Theta != 0 and |R(Theta, g)| <= e^{alpha |g|}   where  R = Z_{Theta \\ N[g]} / Z_{Theta \\ g}.
  T2  decay: if Theta, Theta' differ only at a polymer eta with D(g, eta) = d, then
      |R(Theta,g) - R(Theta',g)| <= 2 e^{alpha |g|} e^{-delta (d-1)},
      D(g, eta) = min over chains g = h_0, h_1, ..., h_m = eta (consecutive incompatible)
      of  sum_{i>=1} |h_i|.
  T3  Lemma D (two-set comparison).  With Phi(H) = Z_{Gamma \ H} / Z_Gamma, J = H2 \ H1, K = H1 & H2:
      |Phi(H1 u H2) - Phi(H1) Phi(H2)|  <=  |Phi(H1)| e^{U(J)} [ 2 e^{mu} sum_{eta in J} u_eta e^{-mu D(eta,H1)}/(1-u_eta)
                                                               + (e^{U(K)} - 1) ],     U(H) = sum_{eta in H} u/(1-u).
"""
from __future__ import annotations

import heapq
import random
import sys
from math import exp


def build(N=14, maxlen=3):
    polys = [(i, i + n) for n in range(1, maxlen + 1) for i in range(N - n + 1)]
    return polys


def overlap(a, b):
    return a[0] < b[1] and b[0] < a[1]


def Zsum(theta, zeta, N):
    """Sum over families of pairwise-disjoint intervals from theta of prod zeta."""
    by_start = {}
    for g in theta:
        by_start.setdefault(g[0], []).append(g)
    g_ = [0.0] * (N + 2)
    g_[N] = 1.0
    for k in range(N - 1, -1, -1):
        v = g_[k + 1]
        for g in by_start.get(k, []):
            v += zeta[g] * g_[g[1]]
        g_[k] = v
    return g_[0]


def R(theta, g, zeta, N):
    """R(Theta, g) = Z_{Theta \\ N[g]} / Z_{Theta \\ g}, for g in Theta."""
    rest = [h for h in theta if h != g]
    comp = [h for h in rest if not overlap(h, g)]
    return Zsum(comp, zeta, N) / Zsum(rest, zeta, N)


def Dmetric(polys, g0):
    dist = {g0: 0}
    pq = [(0, g0)]
    while pq:
        d, g = heapq.heappop(pq)
        if d > dist[g]:
            continue
        for h in polys:
            if h != g and overlap(h, g):
                nd = d + (h[1] - h[0])
                if nd < dist.get(h, 1e18):
                    dist[h] = nd
                    heapq.heappush(pq, (nd, h))
    return dist


def run(seed=7, trials=4000) -> bool:
    rnd = random.Random(seed)
    N = 14
    polys = build(N)
    alpha, delta = 1.0, 0.6
    sign = {g: rnd.choice((-1, 1)) for g in polys}
    mag = {g: rnd.uniform(0.5, 1.0) for g in polys}

    def weights(w):
        return {g: sign[g] * mag[g] * w ** (g[1] - g[0]) for g in polys}

    def cond_ratio(zeta):
        worst = 0.0
        for g0 in polys:
            s = 0.0
            for h in polys:
                if h != g0 and overlap(h, g0):
                    u = abs(zeta[h]) * exp(alpha * (h[1] - h[0]))
                    if u > 0.5:
                        return 1e9
                    s += u * exp(delta * (h[1] - h[0])) / (1 - u)
            worst = max(worst, s / (alpha * (g0[1] - g0[0]) / 2))
        return worst

    lo, hi = 1e-6, 1.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if cond_ratio(weights(mid)) <= 1.0:
            lo = mid
        else:
            hi = mid
    w = lo * 0.999
    zeta = weights(w)
    cr = cond_ratio(zeta)
    print(f"toy gas: {len(polys)} polymers, weight scale w = {w:.4f}, condition ratio = {cr:.4f} (<= 1 required)")

    ok = True
    # T1
    worst1 = 0.0
    nz_ok = True
    for _ in range(trials):
        theta = [g for g in polys if rnd.random() < 0.75]
        if not theta:
            continue
        if abs(Zsum(theta, zeta, N)) < 1e-12:
            nz_ok = False
        g = rnd.choice(theta)
        r = abs(R(theta, g, zeta, N))
        worst1 = max(worst1, r / exp(alpha * (g[1] - g[0])))
    print(f"[{'PASS' if nz_ok and worst1 <= 1 else 'FAIL'}] T1 Z != 0 and |R| <= e^(alpha|g|): "
          f"max |R| e^(-alpha|g|) = {worst1:.4f} (<= 1)")
    ok &= nz_ok and worst1 <= 1

    # T2
    worst2 = 0.0
    tested = 0
    for _ in range(trials):
        theta = [g for g in polys if rnd.random() < 0.75]
        if len(theta) < 3:
            continue
        g0 = rnd.choice(theta)
        dist = Dmetric(polys, g0)
        eta = rnd.choice([h for h in polys if h != g0])
        d = dist.get(eta, None)
        if d is None or d < 2:
            continue
        theta2 = [h for h in theta if h != eta] if eta in theta else theta + [eta]
        diff = abs(R(theta, g0, zeta, N) - R(theta2, g0, zeta, N))
        bound = 2 * exp(alpha * (g0[1] - g0[0])) * exp(-delta * (d - 1))
        worst2 = max(worst2, diff / bound)
        tested += 1
    print(f"[{'PASS' if worst2 <= 1 else 'FAIL'}] T2 decay |R - R'| <= 2 e^(alpha|g|) e^(-delta (d-1)): "
          f"max ratio {worst2:.4f} over {tested} tests (<= 1)")
    ok &= worst2 <= 1
    # T3: Lemma D on the full toy gas Gamma = all polymers
    def Phi(H):
        keep = [g for g in polys if g not in H]
        return Zsum(keep, zeta, N) / Zsum(polys, zeta, N)

    uu = {g: abs(zeta[g]) * exp(alpha * (g[1] - g[0])) for g in polys}
    Ufun = lambda H: sum(uu[g] / (1 - uu[g]) for g in H)
    Dall = {g: Dmetric(polys, g) for g in polys}
    worst3 = 0.0
    tested3 = 0
    for _ in range(trials):
        H1 = set(rnd.sample(polys, rnd.randint(1, 6)))
        H2 = set(rnd.sample(polys, rnd.randint(1, 6)))
        J, K = H2 - H1, H1 & H2
        lhs = abs(Phi(H1 | H2) - Phi(H1) * Phi(H2))
        s_term = 0.0
        for eta in J:
            d = min(Dall[eta][z] for z in H1)
            s_term += uu[eta] * exp(-delta * d) / (1 - uu[eta])
        rhs = abs(Phi(H1)) * exp(Ufun(J)) * (2 * exp(delta) * s_term + (exp(Ufun(K)) - 1))
        if rhs > 0:
            worst3 = max(worst3, lhs / rhs)
            tested3 += 1
    print(f"[{'PASS' if worst3 <= 1 else 'FAIL'}] T3 Lemma D two-set comparison: max lhs/rhs = {worst3:.4f} "
          f"over {tested3} random (H1,H2) (<= 1)")
    ok &= worst3 <= 1
    print("DOBRUSHIN TOY TEST:", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    sys.exit(0 if run() else 1)

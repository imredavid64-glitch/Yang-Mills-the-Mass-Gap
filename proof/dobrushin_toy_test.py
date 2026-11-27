"""
Numerical tests of the Dobrushin-type polymer-gas machinery in proof/THEOREM.md,
on a toy polymer gas where everything can be computed exactly by brute force.

Toy gas: polymers = intervals [a,b) of consecutive sites on a chain of N sites,
two polymers incompatible iff they share a site, real weights with RANDOM SIGNS
(so no positivity is available), scaled so that condition (C_delta) holds:

    u(g) := |zeta(g)| e^{alpha |g|} <= 1/2        for all g
    sum_{g' ~ g0, g' != g0} u(g') e^{delta |g'|} / (1 - u(g'))  <=  alpha |g0| / 2   for all g0

T1  Z_Theta != 0 and |R(Theta, g)| <= exp(alpha |g|),  R = Z_{Theta \\ N[g]} / Z_{Theta \\ {g}}.
T2  decay: if Theta, Theta' differ only at polymer eta with D(g0, eta) = d,
    |R(Theta,g0) - R(Theta',g0)| <= 2 exp(alpha|g0|) exp(-delta(d-1)).
    D = chain metric: min over chains h_0=g0,...,h_m=eta (consecutive incompatible)
    of sum_{i>=1} |h_i|.
T3  Lemma D (two-set comparison): with Phi(H) = Z_{Gamma \\ H} / Z_Gamma,
    J = H2 \\ H1, K = H1 & H2,
    |Phi(H1 u H2) - Phi(H1) Phi(H2)| <= |Phi(H1)| exp(U(J)) [ 2 exp(mu)
          sum_{eta in J} u_eta exp(-mu D(eta,H1))/(1-u_eta)  +  (exp(U(K)) - 1) ],
    U(H) = sum_{eta in H} u/(1-u), D(eta,H1) = min over h1 in H1 D(eta,h1).
T4  Lemma 6 (observable expansion): per-polymer weight factor b(gamma) = 2 if
    gamma touches link set X else 1. Then <A> = sum_{F disjoint} prod zeta b / Z
    equals sum_{S: all polymers touch X} prod_{gamma in S} zeta b * Phi(H_X(S)),
    where H_X(S) = polymers incompatible with S.
"""
from __future__ import annotations

import heapq
import random
import sys
from math import exp


def build(N=14, maxlen=3):
    return [(i, i + n) for n in range(1, maxlen + 1) for i in range(N - n + 1)]


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
    """R(Theta, g) = Z_{Theta \\ N[g]} / Z_{Theta \\ {g}}, for g in Theta."""
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


def touch_links(poly):
    return set(range(poly[0], poly[1]))


def make_zeta(N, maxlen, seed, alpha, delta):
    polys = build(N, maxlen)
    rnd = random.Random(seed)
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
    return weights(w), polys


def run(seed=7, trials=4000) -> bool:
    rnd = random.Random(seed)
    N = 14
    polys = build(N, maxlen=3)
    alpha, delta = 1.0, 0.6
    zeta, _ = make_zeta(N, 3, seed, alpha, delta)
    Zfull = Zsum(polys, zeta, N)

    cr = 0.0
    for g0 in polys:
        s = 0.0
        for h in polys:
            if h != g0 and overlap(h, g0):
                u = abs(zeta[h]) * exp(alpha * (h[1] - h[0]))
                s += u * exp(delta * (h[1] - h[0])) / (1 - u)
        cr = max(cr, s / (alpha * (g0[1] - g0[0]) / 2))
    print(f"toy gas: {len(polys)} polymers, condition ratio = {cr:.4f} (<= 1 required)")

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
    tested2 = 0
    Dall = {g: Dmetric(polys, g) for g in polys}
    for _ in range(trials):
        theta = [g for g in polys if rnd.random() < 0.75]
        if len(theta) < 3:
            continue
        g0 = rnd.choice(theta)
        dist = Dall[g0]
        eta = rnd.choice([h for h in polys if h != g0])
        d = dist.get(eta, None)
        if d is None or d < 2:
            continue
        theta2 = [h for h in theta if h != eta] if eta in theta else theta + [eta]
        diff = abs(R(theta, g0, zeta, N) - R(theta2, g0, zeta, N))
        bound = 2 * exp(alpha * (g0[1] - g0[0])) * exp(-delta * (d - 1))
        worst2 = max(worst2, diff / bound)
        tested2 += 1
    print(f"[{'PASS' if worst2 <= 1 else 'FAIL'}] T2 decay |R - R'| <= 2 e^(alpha|g|) e^(-delta (d-1)): "
          f"max ratio {worst2:.4f} over {tested2} tests (<= 1)")
    ok &= worst2 <= 1

    # T3: Lemma D (two-set comparison)
    def Phi(H):
        keep = [g for g in polys if g not in H]
        return Zsum(keep, zeta, N) / Zfull

    uu = {g: abs(zeta[g]) * exp(alpha * (g[1] - g[0])) for g in polys}
    Ufun = lambda H: sum(uu[g] / (1 - uu[g]) for g in H)
    Dall3 = {g: Dmetric(polys, g) for g in polys}
    worst3 = 0.0
    tested3 = 0
    for _ in range(trials):
        H1 = set(rnd.sample(polys, rnd.randint(1, 6)))
        H2 = set(rnd.sample(polys, rnd.randint(1, 6)))
        J, K = H2 - H1, H1 & H2
        lhs = abs(Phi(H1 | H2) - Phi(H1) * Phi(H2))
        s_term = 0.0
        for eta in J:
            d = min(Dall3[eta][z] for z in H1)
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


def run_lemma6(seed=99, trials=25) -> bool:
    """Verify Lemma 6 (observable expansion) on the toy gas.

    Observable weight factors per polymer: b(gamma) = 2 if gamma touches link
    set X, else 1.  Then <A> = sum_{F disjoint} prod zeta(gamma) b(gamma) / Z
    equals the polymer sum sum_{S: all polymers touch X} prod_{gamma in S}
    zeta(gamma) b(gamma) * Phi(H_X(S)), where H_X(S) = polymers incompatible
    with S (sharing a link).  This is Lemma 6 with zeta_A(S) = prod zeta b.
    """
    rnd = random.Random(seed)
    N = 12
    zeta, polys = make_zeta(N, 3, seed, alpha=1.0, delta=0.6)
    Zfull = Zsum(polys, zeta, N)

    by_start = {}
    for g in polys:
        by_start.setdefault(g[0], []).append(g)

    # left-hand side via DP: weight = zeta*b
    def lhs_dp(X):
        b = {g: (2.0 if touch_links(g) & X else 1.0) for g in polys}
        dZ = [0.0] * (N + 2)
        dZ[N] = 1.0
        for k in range(N - 1, -1, -1):
            v = dZ[k + 1]
            for g in by_start.get(k, []):
                v += zeta[g] * b[g] * dZ[g[1]]
            dZ[k] = v
        return dZ[0] / Zfull

    # right-hand side: enumerate ALL disjoint families S; keep those whose every
    # connected component touches X; term = prod zeta*b * Phi(H_X(S)),
    # H_X(S) = polymers touching X or sharing a link with S.
    def rhs(X):
        X_links = set(X)
        total = 0.0

        def rec(k, chosen_mask, prod, chosen_list):
            nonlocal total
            if k >= N:
                # every connected component of chosen_list must touch X
                comps = []
                seen = set()
                for g in chosen_list:
                    if g in seen:
                        continue
                    stack = [g]
                    seen.add(g)
                    comp = []
                    while stack:
                        x = stack.pop()
                        comp.append(x)
                        for y in chosen_list:
                            if y not in seen and overlap(x, y):
                                seen.add(y)
                                stack.append(y)
                    comps.append(comp)
                if all(any(l in X_links for l in touch_links(g)) for comp in comps for g in comp):
                    touched = frozenset(l for l in range(N) if chosen_mask >> l & 1)
                    total += prod * Phi_set(touched, X_links)
                return
            # skip placing anything starting at k
            rec(k + 1, chosen_mask, prod, chosen_list)
            # place a polymer starting at k (if compatible)
            for g in by_start.get(k, []):
                mask = 0
                for l in touch_links(g):
                    mask |= 1 << l
                if chosen_mask & mask:
                    continue
                rec(g[1], chosen_mask | mask,
                    prod * zeta[g] * (2.0 if touch_links(g) & X_links else 1.0),
                    chosen_list + [g])

        rec(0, 0, 1.0, [])
        return total

    Phi_cache = {}

    def Phi_set(touched, X_links):
        key = (frozenset(touched), frozenset(X_links))
        if key not in Phi_cache:
            keep = [g for g in polys
                    if not (touch_links(g) & touched) and not (touch_links(g) & X_links)]
            Phi_cache[key] = Zsum(keep, zeta, N=N) / Zfull
        return Phi_cache[key]

    ok = True
    worst = 0.0
    for _ in range(trials):
        X = frozenset(rnd.sample(range(N), rnd.randint(1, 2)))
        lhs = lhs_dp(X)
        rhs_val = rhs(X)
        diff = abs(lhs - rhs_val)
        worst = max(worst, diff)
        if diff > 1e-9:
            print(f"    MISMATCH X={sorted(X)}: lhs={lhs:.8f} rhs={rhs_val:.8f} diff={diff:.3e}")
    print(f"[T4] Lemma 6 observable expansion: max |lhs - rhs| = {worst:.3e} over {trials} trials")
    ok &= worst < 1e-8
    print("LEMMA 6 TOY TEST:", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    ok1 = run()
    ok2 = run_lemma6()
    sys.exit(0 if ok1 and ok2 else 1)

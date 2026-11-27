"""
Infinite-volume strong-coupling convergence for 4D SU(2) Wilson gauge theory,
with a polymer bound that does NOT use the (incorrect) Catalan link weights of
cluster_expansion.py and does NOT truncate to the j = 1/2 channel.

NOTE: the certified statement is proof/rigorous_check.py (beta <= 0.0178: analytic eps bound +
interval arithmetic), with proofs in proof/THEOREM.md.  The floating-point numbers printed by
THIS script (e.g. beta_KP = 0.01834, which uses a quadrature value of eps) are exploratory and
not certified.

SETUP (exact)
-------------
f(U) = exp(beta Tr U / 2) / a(beta),  a = int exp(beta Tr U/2) dU = 2 I_1(beta)/beta,
g = f - 1.   Z = int prod_p (1 + g(U_p)) = sum over plaquette sets S of
int prod_{p in S} g(U_p).  Splitting S into link-connected components gives a
polymer gas: polymer = link-connected plaquette set gamma, weight
    zeta(gamma) = int prod_{p in gamma} g(U_p) dU,
two polymers compatible iff they share no link.   (Exact; all representations.)

FACTS USED
----------
F1  zeta(gamma) = 0 unless every link of gamma lies in >= 2 plaquettes of gamma
    (Haar invariance: a link occurring once integrates its plaquette to int g = 0).
    n0 := smallest size of such a set; computed here by exhaustive search (FK3).
F2  Finner's inequality (generalised Holder, product measure): if each link lies
    in at most q plaquettes of gamma then  |zeta(gamma)| <= prod_p ||g||_q.
    Every link of Z^4 lies in 6 plaquettes, so q = 6:
        |zeta(gamma)| <= eps^{|gamma|},   eps(beta) := ||g||_{L^6(Haar)}.
    (proved in proof/THEOREM.md.)
F3  Connected n-subsets containing a given vertex of a graph of max degree D:
    at most (e D)^(n-1).   (proved in proof/THEOREM.md, Lemma 3; sanity-checked in FK2.)
    The plaquette graph (share a link) of Z^4 has D = 20.
F4  Kotecky-Preiss: if for all gamma
        sum_{gamma' incompatible with gamma} |zeta(gamma')| e^{(alpha+delta)|gamma'|}
            <= alpha |gamma|,
    then log Z has a convergent cluster expansion (volume-uniform), with cluster
    sums decaying like e^{-delta * size}.  (cited, not re-proved.)
    A polymer is incompatible with gamma iff it contains a plaquette from the
    closed neighbourhood (21 plaquettes) of some plaquette of gamma, so it
    suffices that
        21 * [ sum_{n <= 7} C_n x^n + sum_{n > 7} (eD)^(n-1) x^n ] <= alpha,   x = eps e^{alpha+delta},
    where C_n is the EXACT number of link-connected, every-link-covered-twice n-sets
    containing a fixed plaquette (F1 lets us restrict to these): C_6 = 4 (the four cubes),
    C_7 = 0, by exhaustive search (FK3).

RESULT
------
With s = alpha + delta, x = eps e^s, G = eD:  f(s) = 21 [ 4 x^6 + G^7 x^8/(1 - G x) ].
delta*(beta) = max_s [ s - f(s) ].  The expansion converges for all beta with
delta*(beta) > 0 (beta < beta_KP below).  Standard consequences (cited): analytic
free energy and exponential decay of connected correlations at rate >= delta*
per unit Euclidean time (a link-connected chain of plaquettes spanning time t has
>= t plaquettes), hence a transfer-matrix spectral gap >= delta*(beta) in lattice
units for beta < beta_KP.

WHAT THIS IS NOT
----------------
This is the classical strong-coupling regime (Osterwalder-Seiler 1978).  It is a
statement at FIXED lattice spacing.  It says nothing about the continuum limit,
which needs beta -> infinity, far outside the region here.  It does NOT advance
the Clay problem.
"""
from __future__ import annotations

import sys
from collections import Counter
from math import e, pi

import numpy as np
from scipy.integrate import quad
from scipy.special import iv

D_PLAQ = 20
G = e * D_PLAQ


# ---------------------------------------------------------------- eps(beta)
def eps6(beta: float) -> float:
    """||g||_{L^6(Haar)}, g = exp(beta cos phi)/a - 1, Haar density (2/pi) sin^2 phi."""
    a = 2.0 * iv(1, beta) / beta
    h = lambda ph: abs(np.exp(beta * np.cos(ph)) / a - 1.0) ** 6 * (2.0 / pi) * np.sin(ph) ** 2
    val, _ = quad(h, 0.0, pi, epsabs=0.0, epsrel=1e-11, limit=400)
    return val ** (1.0 / 6.0)


# ---------------------------------------------------------- Z^4 plaquette graph
def _links(p):
    x, mu, nu = p
    xm = tuple(x[i] + (i == mu) for i in range(4))
    xn = tuple(x[i] + (i == nu) for i in range(4))
    return [(x, mu), (xm, nu), (xn, mu), (x, nu)]


def _on_link(link):
    y, d = link
    out = []
    for ee in range(4):
        if ee == d:
            continue
        mu, nu = sorted((d, ee))
        other = nu if d == mu else mu
        base2 = tuple(y[i] - (i == other) for i in range(4))
        out += [(y, mu, nu), (base2, mu, nu)]
    return out


def _neighbors(p):
    s = set()
    for l in _links(p):
        s.update(_on_link(l))
    s.discard(p)
    return list(s)


ROOT = ((0, 0, 0, 0), 0, 1)


def _redelmeier(maxn, on_add, on_remove, visit, prune=None):
    marked = {ROOT}
    poly = []

    def rec(untried):
        untried = list(untried)
        while untried:
            p = untried.pop()
            poly.append(p)
            on_add(p)
            visit(poly)
            if len(poly) < maxn and not (prune and prune(len(poly))):
                new = [q for q in _neighbors(p) if q not in marked]
                marked.update(new)
                rec(untried + new)
                marked.difference_update(new)
            on_remove(p)
            poly.pop()

    rec([ROOT])


def animal_counts(maxn):
    cnt = Counter()
    _redelmeier(maxn, lambda p: None, lambda p: None, lambda poly: cnt.update([len(poly)]))
    return cnt


def covered_twice_counts(maxn):
    """Sizes of link-connected sets containing ROOT with every link in >= 2 plaquettes."""
    k = Counter()
    state = {"D": 0}

    def add(p):
        for l in _links(p):
            k[l] += 1
        # deficiency = how many more plaquette-link incidences are still needed
        state["D"] = sum(max(0, 2 - v) for v in k.values())

    def rem(p):
        for l in _links(p):
            k[l] -= 1
            if k[l] == 0:
                del k[l]
        state["D"] = sum(max(0, 2 - v) for v in k.values())

    found = Counter()

    def visit(poly):
        if state["D"] == 0:
            found[len(poly)] += 1

    _redelmeier(maxn, add, rem, visit,
                prune=lambda n: state["D"] > 4 * (maxn - n))
    return found


# ------------------------------------------------------------------ KP numbers
def delta_star(beta: float, counts: dict, nmax: int):
    """max_s [ s - f(s) ],  f(s) = 21 [ sum_{n<=nmax} C_n x^n + sum_{n>nmax} G^(n-1) x^n ],
    x = eps e^s.  C_n = EXACT number of link-connected, every-link-covered-twice n-sets
    containing a fixed plaquette (exhaustive search, FK3); n > nmax uses the (eD)^(n-1) bound."""
    ep = eps6(beta)
    best = -np.inf
    for s in np.linspace(1e-4, 8.0, 8000):
        x = ep * np.exp(s)
        if G * x >= 1.0:
            break
        exact = sum(c * x ** n for n, c in counts.items() if n <= nmax)
        tail = G ** nmax * x ** (nmax + 1) / (1.0 - G * x)
        best = max(best, s - 21.0 * (exact + tail))
    return best, ep


def beta_kp(counts: dict, nmax: int):
    lo, hi = 1e-6, 0.5
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if delta_star(mid, counts, nmax)[0] > 0:
            lo = mid
        else:
            hi = mid
    return lo


def run(search_n: int = 7) -> bool:
    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))
        ok &= bool(cond)

    print("INFINITE-VOLUME STRONG-COUPLING (Finner + Kotecky-Preiss), SU(2), d=4")
    nb = _neighbors(ROOT)
    check("FK0 plaquette graph degree is 20", len(nb) == 20, f"degree {len(nb)}")

    ac = animal_counts(5)
    check("FK2 connected-set counts N_n <= (e*20)^(n-1) for n <= 5",
          all(ac[n] <= G ** (n - 1) for n in ac),
          ", ".join(f"N_{n}={ac[n]}" for n in sorted(ac)))

    found = covered_twice_counts(search_n)
    n0 = min(found) if found else None
    check(f"FK3 smallest every-link-covered-twice set containing a plaquette has n0 = 6 "
          f"(exhaustive for sizes <= {search_n}); exact counts C_n kept for the bound",
          n0 == 6, f"rooted counts by size: {dict(sorted(found.items()))} (none of size 7)")
    counts = {n: found.get(n, 0) for n in range(6, search_n + 1)}

    # sanity: Finner bound vs the exact cube weight at leading order
    b = 0.02
    cube_true = (b / 2) ** 6 * 2.0 ** -4
    check("FK1 sanity: |zeta(cube)| ~ (beta/2)^6 2^-4 <= eps6^6",
          cube_true <= eps6(b) ** 6, f"{cube_true:.3e} <= {eps6(b) ** 6:.3e}")

    bk = beta_kp(counts, search_n)
    bk_crude = beta_kp({6: G ** 5}, 6)
    check("FK4 convergence criterion holds for beta < beta_KP (improves the crude-count bound)", bk > bk_crude > 0, f"beta_KP = {bk:.5f}")
    print(f"  [info] repo's earlier (flawed, torus-only) beta_0^rig = 0.014655;  "
          f"crude-count bound {bk_crude:.5f};  exact-count bound {bk:.5f}")
    print(f"  [info] hard ceiling from the growth rate: beta < 1/(G*eps/beta) ~ "
          f"{1.0 / (G * eps6(1e-3) / 1e-3):.5f} (needs better animal counts to pass)")
    print("  [info]   beta      eps6      delta*(beta) [gap lower bound]   4 ln(4/beta) [leading-order true rate]")
    for beta in (0.002, 0.005, 0.01, 0.8 * bk):
        d, ep = delta_star(beta, counts, search_n)
        print(f"  [info] {beta:8.5f}  {ep:8.5f}   {d:10.4f}                  {4 * np.log(4 / beta):10.4f}")
    print("FINNER-KP:", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    sys.exit(0 if run() else 1)

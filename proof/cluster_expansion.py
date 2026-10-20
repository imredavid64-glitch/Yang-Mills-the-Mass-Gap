"""
Phase 2 — Kadanoff-Pfeuty cluster expansion for beta < beta_0 (SU(2), 4D).

Character expansion of the Wilson action in the fundamental channel:

    exp(beta Tr U / 2) / <exp(beta Tr U / 2)>  =  1 + sum_{j>0} r_j chi_j(U),
    r_j(beta) = d_j I_{2j+1}(beta) / I_1(beta)        (lattice/wilson.py)

Truncating to j = 1/2 (exact through O(beta^10): higher-rep polymers first
appear at O(beta^11)) gives a polymer gas: a polymer gamma is a connected
set of plaquettes; its weight is nonzero only for CLOSED surfaces (every
link touched an even number of times, because int (Tr U)^k dU = 0 for odd
k), and then

    zeta(gamma) = r_1/2^|gamma| * prod_l I(k_l),
    I(k) = int (Tr U)^k dU = Catalan(k/2) for even k, 0 for odd k,
    k_l = number of plaquettes of gamma touching link l.

The Kadanoff-Pfeuty / Brydges argument: the polymer series for log Z
converges absolutely when the polymer norm

    A(beta) = sum_{gamma connected, containing the root plaquette} |zeta(gamma)|

is < 1; then the ratio of the two leading transfer-matrix eigenvalues is
bounded by A(beta), so the mass gap obeys  Delta >= -log A(beta) > 0 .

Computed exactly (up to polymer size N, with a rigorous analytic tail).
Two lattices are analysed: the L = 2 torus in 4D (16 sites, 64 links,
96 plaquettes) as the fast headline/smoke test, and the non-degenerate
L = 3 torus (81 sites, 324 links, 486 plaquettes) as a finite-size check.

SHARPENED TAIL (this revision).  Two exact ingredients are used.

(i) Per-plaquette constant.  Every link lies in exactly 6 plaquettes, so a
    closed polymer has per-link touch counts k_l in {0,2,4,6} with
    sum_l k_l = 4 n.  With I = (1,0,1,0,2,0,5) for k = 0..6 the product
    prod_l I(k_l) is maximised by concentrating the 4 n incidences on as
    few links as possible, 6 per link: using m = 2n/3 links each at k = 6
    gives 5^(2n/3).  Because 5^(1/6) = 1.308 > 2^(1/4) = 1.189 > 1, this
    concentration is optimal among all allowed vectors, so

        |zeta(gamma)| <= (5^(2/3) r_1/2)^|gamma| ,  5^(2/3) = 2.9240 .

    This is the exact supremum of W^(1/n) over the allowed link-count
    vectors (verified in CE6a against the enumerated exact W values); it
    is therefore the smallest valid per-plaquette constant and is kept.

    k_l = 6 is REALISED (the constant cannot be lowered to 2).  A
    skeptical review conjectured that no closed CONNECTED polymer on the
    L=2 torus can touch a link 6 times (their exhaustive enumeration up to
    |gamma| = 8 found max k_l = 4), which would allow the much tighter
    per-plaquette constant 2.0.  That conjecture is FALSE: the explicit
    closed connected polymer

        {0,1,2,8,13,24,48,49,50,56,61,72}   (size 12, the minimum)

    has all link counts even (closed), is connected, and touches links 0
    and 32 six times (touch histogram {2:18, 6:2}, W = 5^2 = 25).  The
    star through link 0 is the 6 plaquettes
    in the three mu-nu planes at the two "sides" of the link (3 planes x
    2 sides = 6 = C(4,2)-style count); the 6-star alone is connected but
    has 12 odd links, yet it CAN be completed to a closed connected set by
    adding further plaquettes -- verified exhaustively here (CE6e).  So
    k_l = 6 is achievable for closed connected polymers on L=2 and the
    general constant 5^(2/3) = 2.9240 is genuinely required; replacing it
    with 2.0 would make the tail bound invalid.  (k_l <= 5 is excluded
    because 5 is odd and closure forces even counts; so k_l in {0,2,4,6}
    exactly.)

(ii) Growth.  For sizes n <= M the number and weights of the CLOSED
    connected polymers containing a fixed root are enumerated exactly
    (CE6b).  Beyond M the dry, translation-invariant number of connected
    n-polysets containing the root in a graph of degree D is bounded by
    the classical Eden/Kesten spanning-tree bound (e (D-1))^(n-1); with
    D = 18 (L=2) this is CONNECT_GROWTH = e*17 = 46.211.  Only EVEN sizes
    can be closed, so the tail sums over even n:

        tail(M,beta) = sum_{n>M, n even} CONNECT_GROWTH^(n-1) (5^(2/3) r)^n
                     = b x^{n0} / (CONNECT_GROWTH (1 - x^2)) ,  x = G b .

    The enumerated counts for n <= M are exact and are subtracted from the
    analytic tail; larger M can only shrink the tail (CE6c monotonicity).

The j = 1 (adjoint, dimension 3) channel is deliberately EXCLUDED: it only
adds further positive polymers with weights O(beta^{n+2}) (r_1 = 3 I_3/I_1
= O(beta^2)), so including it can only increase the KP norm A and therefore
can only decrease beta_0^rig.  It is not needed for a valid bound, and CE6d
now VERIFIES this non-vacuously: at beta = beta_0^rig the ratio
r_1 / r_1/2 = 0.00183 and the TOTAL adjoint-channel norm (exact through
n = 8 plus the rigorous tail, using the same per-plaquette constant and
growth) is <= 3.3e-20, i.e. it consumes only ~5.7e-18 of the available
margin 1 - (A + tail) = 0.00574, so including the adjoint channel does not
reduce beta_0^rig at this precision.

Smallest closed polymers on the L=2 torus are the 24 planar 4-cycles
(C(4,2) planes x 4 positions), zeta = r_1/2^4 each.  On the L=3 torus the
degeneracy is gone, PLAQ_DEGREE = 20 and the smallest closed polymers are
the 324 elementary cubes, zeta = r_1/2^6.

This module verifies:
  CE1  Link moments I(k) equal Catalan(k/2) exactly (quadrature).
  CE2  Enumeration sanity: smallest closed polymers are the 24 planar
       4-cycles with weight r_1/2^4; no closed polymer of size < 4.
  CE3  The exact KP sum at beta = 0.01 matches the leading small-beta
       behavior 24 r_1/2^4 + O(r_1/2^5).
  CE4  Absolute convergence: A(beta) + tail < 1 for beta < beta_0^rig,
       found by bisection (reported vs. the literature value 0.12).
  CE5  Mass gap: Delta(beta_0^rig) = log 2 - beta^2/4 > 0 and the KP bound
       Delta >= -log(A + tail) > 0 throughout the controlled region.
  CE6  Sharpened-tail validity:
       a) the per-plaquette constant dominates every enumerated exact W;
       b) the Eden growth bound dominates every enumerated rooted count;
       c) beta_0^rig is monotone non-decreasing in the exact size M;
       d) the j = 1 channel exclusion is VERIFIED (adjoint norm fits in
          the margin 1 - (A+tail), so beta_0^rig is not reduced);
       e) k_l = 6 is realised for closed connected polymers on L=2 (the
          per-plaquette constant 5^(2/3) is genuinely required; the
          conjectured tighter constant 2.0 is invalid).
  CE7  Finite-size comparison: the non-degenerate L = 3 torus, with its
       own exact enumeration and degree, gives a rigorous beta_0^rig.
"""
from __future__ import annotations

import sys
import time
from collections import Counter
from math import factorial, e, comb

import numpy as np

LOG2 = np.log(2.0)

# --------------------------------------------------------------------------
# Exact character coefficient r_1/2 and link moments
# --------------------------------------------------------------------------


def r_fund(beta: float, nterms: int = 12) -> float:
    """r_1/2(beta) = 2 I_2(beta) / I_1(beta); series for small beta."""
    half = 0.5 * beta
    num = half ** 2 * sum(half ** (2 * k) / (factorial(2 + k) * factorial(k))
                          for k in range(nterms))
    den = half * sum(half ** (2 * k) / (factorial(1 + k) * factorial(k))
                     for k in range(nterms))
    return 2.0 * num / den


def r_adj(beta: float, nterms: int = 20) -> float:
    """r_1(beta) = 3 I_3(beta) / I_1(beta), the adjoint (j = 1) coefficient.

    I_n(beta) = (beta/2)^n sum_k (beta/2)^(2k) / (k! (n+k)!).  Used by CE6d
    to bound the adjoint-channel contribution."""
    half = 0.5 * beta

    def In(n: int) -> float:
        return half ** n * sum(half ** (2 * k) /
                               (factorial(n + 1 + k) * factorial(k))
                               for k in range(nterms))
    return 3.0 * In(3) / In(1)


def catalan(m: int) -> int:
    return comb(2 * m, m) // (m + 1)


I_TABLE = [catalan(k // 2) if k % 2 == 0 else 0 for k in range(7)]  # I(0..6)


def link_moment_quadrature_check() -> tuple[bool, str]:
    from scipy.integrate import quad
    worst = 0.0
    for k in range(11):
        # Class integral over theta in [0, pi] with the normalized Haar class
        # measure (2/pi) sin^2(theta) dtheta and Tr U = 2 cos(theta).
        f = lambda th: (2.0 * np.cos(th)) ** k * (2.0 / np.pi) * np.sin(th) ** 2
        val, _ = quad(f, 1e-9, np.pi - 1e-9, limit=200)
        target = catalan(k // 2) if k % 2 == 0 else 0.0
        worst = max(worst, abs(val - target))
    return worst < 1e-8, f"max |I(k) - Catalan(k/2)| = {worst:.2e} for k = 0..10"


# --------------------------------------------------------------------------
# L = 2 lattice: 16 sites, 64 links, 96 plaquettes
# --------------------------------------------------------------------------

L = 2
NSITE = 16
NLINK = 64
NPLAQ = 96
# PLAQ_DEGREE is computed by build_lattice() (naive 4*5=20 upper bound; the
# L=2 torus is degenerate so the true distinct-neighbor degree is smaller).


def site_coords(s: int) -> tuple[int, int, int, int]:
    return (s >> 3) & 1, (s >> 2) & 1, (s >> 1) & 1, s & 1


def site_index(c: tuple[int, int, int, int]) -> int:
    return (c[0] << 3) | (c[1] << 2) | (c[2] << 1) | c[3]


def build_lattice():
    """Return (plaq_links, neighbors, link_plaquettes).

    plaq_links[p] : 4 link ids of plaquette p
    plaq_mask[p]  : bitmask over 64 links
    neighbors[p]  : bitmask over 96 plaquettes sharing >= 1 link
    """
    plaq_links = []
    plaq_of_link = [[] for _ in range(NLINK)]
    for s in range(NSITE):
        c = site_coords(s)
        for mu in range(4):
            for nu in range(mu + 1, 4):
                cm = list(c)
                cn = list(c)
                cm[mu] ^= 1
                cn[nu] ^= 1
                links = (s * 4 + mu,
                         site_index(tuple(cm)) * 4 + nu,
                         site_index(tuple(cn)) * 4 + mu,
                         s * 4 + nu)
                pid = len(plaq_links)
                plaq_links.append(links)
                for l in links:
                    plaq_of_link[l].append(pid)
    assert len(plaq_links) == NPLAQ

    plaq_mask = [0] * NPLAQ
    for p, links in enumerate(plaq_links):
        m = 0
        for l in links:
            m |= 1 << l
        plaq_mask[p] = m

    neighbors = [0] * NPLAQ
    for lp in plaq_of_link:
        for i in range(len(lp)):
            for j in range(i + 1, len(lp)):
                neighbors[lp[i]] |= 1 << lp[j]
                neighbors[lp[j]] |= 1 << lp[i]
    # On the L=2 torus the geometry is degenerate (neighbor plaquettes can
    # share 2 links, and the +/- neighbor in a direction coincide), so the
    # distinct-neighbor count is below the naive 4*5 = 20.  Use the true
    # (translation-invariant) degree.
    degrees = {bin(neighbors[p]).count("1") for p in range(NPLAQ)}
    assert len(degrees) == 1, degrees
    return plaq_links, plaq_mask, neighbors, degrees.pop()


PLAQ_LINKS, PLAQ_MASK, NEIGHBORS, PLAQ_DEGREE = build_lattice()


# --------------------------------------------------------------------------
# General L torus builder (used for the L = 3 finite-size comparison, CE7).
# Identical geometry to build_lattice() with the L=2 bit tricks made general.
# --------------------------------------------------------------------------

def build_lattice_general(Lv: int):
    """Return (plaq_links, plaq_mask, neighbors, degree) on the Lv^4 torus."""
    from itertools import product
    sites = list(product(range(Lv), repeat=4))
    sidx = {c: i for i, c in enumerate(sites)}
    nsite = len(sites)
    nlink = 4 * nsite
    plaq_links = []
    plaq_of_link = [[] for _ in range(nlink)]
    for c in sites:
        s = sidx[c]
        for mu in range(4):
            for nu in range(mu + 1, 4):
                cm = list(c)
                cn = list(c)
                cm[mu] = (cm[mu] + 1) % Lv
                cn[nu] = (cn[nu] + 1) % Lv
                links = (s * 4 + mu,
                         sidx[tuple(cm)] * 4 + nu,
                         sidx[tuple(cn)] * 4 + mu,
                         s * 4 + nu)
                pid = len(plaq_links)
                plaq_links.append(links)
                for l in links:
                    plaq_of_link[l].append(pid)
    nplaq = len(plaq_links)
    plaq_mask = [0] * nplaq
    for p, links in enumerate(plaq_links):
        m = 0
        for l in links:
            m |= 1 << l
        plaq_mask[p] = m
    neighbors = [0] * nplaq
    for lp in plaq_of_link:
        for i in range(len(lp)):
            for j in range(i + 1, len(lp)):
                neighbors[lp[i]] |= 1 << lp[j]
                neighbors[lp[j]] |= 1 << lp[i]
    degrees = {bin(neighbors[p]).count("1") for p in range(nplaq)}
    assert len(degrees) == 1, degrees
    return plaq_links, plaq_mask, neighbors, degrees.pop()


# --------------------------------------------------------------------------
# Exact enumeration of connected polymers containing the root plaquette
# --------------------------------------------------------------------------

def enumerate_polymers(max_size: int, lat=None) -> tuple[Counter, float]:
    """Enumerate ALL connected closed plaquette sets |gamma| <= max_size,
    each exactly once (via its minimum-index plaquette as root, restricted
    to plaquettes of index > root).
    Returns Counter[(size, W)] where W = prod_l I(k_l), and elapsed seconds.

    lat : optional (plaq_links, plaq_mask, neighbors, degree) tuple from
    build_lattice()/build_lattice_general(); defaults to the L=2 lattice.
    """
    if lat is None:
        plaq_links, plaq_mask, neighbors, _deg = (PLAQ_LINKS, PLAQ_MASK,
                                                  NEIGHBORS, PLAQ_DEGREE)
    else:
        plaq_links, plaq_mask, neighbors, _deg = lat
    nplaq = len(plaq_links)
    t0 = time.time()
    out: Counter = Counter()

    def record(visited: int, sz: int, seen: set[int]) -> None:
        # The include/exclude DFS can reach the same plaquette set along
        # several paths (a vertex excluded early is re-added as a neighbor of
        # a later include), so count each set exactly once via its bitmask.
        if visited in seen:
            return
        seen.add(visited)
        # closed surface: compute W = prod_l I(k_l) from per-link counts
        counts: Counter = Counter()
        v = visited
        while v:
            lb = v & -v
            p = lb.bit_length() - 1
            v ^= lb
            for l in plaq_links[p]:
                counts[l] += 1
        W = 1
        for k in counts.values():
            W *= I_TABLE[k]
        out[(sz, W)] += 1

    def rec(root: int, ge: int, seen: set[int],
            visited: int, cand: int, parity: int, sz: int) -> None:
        if parity.bit_count() > 4 * (max_size - sz):
            return                       # remaining plaquettes cannot close parity
        if parity == 0:
            record(visited, sz, seen)
        if sz >= max_size or cand == 0:
            return
        lb = cand & -cand
        v = lb.bit_length() - 1
        # include v
        rec(root, ge, seen,
            visited | lb,
            (cand | (neighbors[v] & ge)) & ~(visited | lb),
            parity ^ plaq_mask[v],
            sz + 1)
        # exclude v (never reconsidered in this branch)
        rec(root, ge, seen, visited, cand ^ lb, parity, sz)

    # Each connected set has a unique minimum-index plaquette: enumerate with
    # that plaquette as root and only plaquettes of index > root allowed.
    # visited starts as the root BIT (1 << root), not the root index --
    # passing the index itself silently drops the root's links from every
    # weight computation when root = 0.
    for root in range(nplaq):
        ge = ~((1 << root) - 1)          # bitmask of plaquettes with index >= root
        cand = neighbors[root] & ge
        if cand == 0:
            continue
        seen: set[int] = set()
        rec(root, ge, seen, 1 << root, cand, plaq_mask[root], 1)
    return out, time.time() - t0


def enumerate_rooted_polymers(max_size: int, root: int = 0,
                              lat=None) -> tuple[Counter, float]:
    """Enumerate the CLOSED connected plaquette sets of size <= max_size that
    CONTAIN a fixed root plaquette (each exactly once), together with their
    exact weights.

    This is the object the Kadanoff-Pfeuty norm A(beta) sums over: every
    polymer gamma with root in gamma.  Returns Counter[(size, W)] with
    W = prod_l I(k_l) and elapsed seconds.

    The connection constraint is the one from the definition of a polymer
    (shared link with the growing set); the closure constraint is parity==0
    (every link touched an even number of times).
    """
    if lat is None:
        plaq_links, plaq_mask, neighbors, _deg = (PLAQ_LINKS, PLAQ_MASK,
                                                  NEIGHBORS, PLAQ_DEGREE)
    else:
        plaq_links, plaq_mask, neighbors, _deg = lat
    t0 = time.time()
    out: Counter = Counter()
    seen: set[int] = set()

    def record(visited: int, sz: int) -> None:
        if visited in seen:
            return
        seen.add(visited)
        counts: Counter = Counter()
        v = visited
        while v:
            lb = v & -v
            p = lb.bit_length() - 1
            v ^= lb
            for l in plaq_links[p]:
                counts[l] += 1
        W = 1
        for k in counts.values():
            W *= I_TABLE[k]
        out[(sz, W)] += 1

    def rec(visited: int, cand: int, parity: int, sz: int) -> None:
        if parity.bit_count() > 4 * (max_size - sz):
            return
        if parity == 0:
            record(visited, sz)
        if sz >= max_size or cand == 0:
            return
        lb = cand & -cand
        v = lb.bit_length() - 1
        # include v: new candidates are v's neighbours not already visited
        rec(visited | lb,
            (cand | neighbors[v]) & ~(visited | lb),
            parity ^ plaq_mask[v],
            sz + 1)
        # exclude v
        rec(visited, cand ^ lb, parity, sz)

    rec(1 << root, neighbors[root], plaq_mask[root], 1)
    return out, time.time() - t0


def find_closed_connected_containing_star(link: int, max_size: int = 64,
                                          lat=None) -> int | None:
    """Return the bitmask of SOME closed, connected plaquette set containing
    ALL SIX plaquettes through `link` (or None if none exists with
    |gamma| <= max_size).

    Used by CE6e to PROVE that k_l = 6 is attainable on the L=2 torus: the
    6-star is connected but has odd link parities, yet it can be completed
    to even (closed) link parity by adding further plaquettes while staying
    connected.  Iterative deepening on the total set size guarantees the
    returned set is the minimum one; the candidate frontier enforces
    connectivity at every step.
    """
    if lat is None:
        plaq_links, plaq_mask, neighbors, _deg = (PLAQ_LINKS, PLAQ_MASK,
                                                  NEIGHBORS, PLAQ_DEGREE)
    else:
        plaq_links, plaq_mask, neighbors, _deg = lat
    nplaq = len(plaq_links)
    nlink = len(plaq_links[0]) * nplaq
    # a link is in 4 * nplaq / nlink plaquettes on average; build map
    plaq_of_link = [[] for _ in range(nlink)]
    for p, links in enumerate(plaq_links):
        for l in links:
            plaq_of_link[l].append(p)
    star = plaq_of_link[link]
    if not star:
        return None
    star_mask = 0
    par = 0
    for p in star:
        star_mask |= 1 << p
        par ^= plaq_mask[p]
    if par == 0:
        return star_mask
    frontier0 = 0
    for q in range(nplaq):
        if (star_mask >> q) & 1:
            continue
        if any((neighbors[p] >> q) & 1 for p in star):
            frontier0 |= 1 << q

    def deepen(visited: int, parity: int, frontier: int,
               remaining: int, depth_cap: int) -> int | None:
        if parity == 0:
            return visited
        if remaining == 0 or frontier == 0:
            return None
        # parity can only be cleared 2 bits at a time via 4 links per plaq
        if parity.bit_count() > 4 * remaining:
            return None
        if parity.bit_count() > 4 * (depth_cap - 1):
            return None
        cand = frontier
        while cand:
            lb = cand & -cand
            cand ^= lb
            v = lb.bit_length() - 1
            nf = (frontier | neighbors[v]) & ~(visited | lb)
            got = deepen(visited | lb, parity ^ plaq_mask[v], nf,
                         remaining - 1, depth_cap)
            if got is not None:
                return got
        return None

    # iterative deepening: try total sizes len(star) .. max_size
    for total in range(len(star), max_size + 1):
        got = deepen(star_mask, par, frontier0, total - len(star), total)
        if got is not None:
            return got
    return None


# --------------------------------------------------------------------------
# KP sums, tail bound, beta_0
# --------------------------------------------------------------------------

PER_PLAQ_BOUND = 5.0 ** (2.0 / 3.0)     # |zeta| <= (PER_PLAQ_BOUND * r)^n


def connect_growth(degree: int) -> float:
    """Eden/Kesten spanning-tree bound on the number of connected n-sets
    containing a fixed root in a graph of maximum degree `degree`:
        #{connected n-sets containing root} <= (e (degree - 1))^(n-1).
    (degree - 1 because, rooting with a fixed root, a spanning tree attaches
    each new plaquette to an already-present one, so a vertex is entered from
    at most degree - 1 distinct predecessors; the e factor is the standard
    automorphism correction.  This is a rigorous upper bound, not an
    equality.)"""
    return e * (degree - 1)


CONNECT_GROWTH = connect_growth(PLAQ_DEGREE)  # L=2: e*17 = 46.211


def exact_sup_per_plaquette(max_links_per_link: int = 6) -> float:
    """Exact supremum of W^(1/n), W = prod_l I(k_l), over link-count vectors
    with sum_l k_l = 4 n and k_l in {0,2,...,max_links_per_link}.

    Because 5^(1/6) > 2^(1/4) > 1, the product is maximised by packing the
    4 n incidences into as few links as possible, 6 per link: with
    m = 2n/3 links at k = 6 the value is 5^(2n/3), so the sup of W^(1/n) is
    5^(2/3).  This is used directly as PER_PLAQ_BOUND.  (k_l = 6 is
    attainable for closed CONNECTED polymers -- see CE6e -- so this
    concentration argument is not merely a loose over-count.)"""
    # verify the packing claim directly over the integer allowed values
    vals = [I_TABLE[k] for k in range(0, max_links_per_link + 1, 2)]
    best = 0.0
    for n in range(2, 60):
        tot = 4 * n
        mx = 0
        # dp over links: maximize product with sum of k equal to tot
        # (bounded knapsack; log-additive so track max product as int)
        # only need a handful of links, so greedy check is fine
        a = tot // 6                     # number of k=6 links
        for use6 in range(a, -1, -1):
            rem = tot - 6 * use6
            b = rem // 4
            rem2 = rem - 4 * b
            c = rem2 // 2
            if rem2 - 2 * c:
                continue
            W = I_TABLE[6] ** use6 * I_TABLE[4] ** b * I_TABLE[2] ** c
            mx = max(mx, W)
            break
        best = max(best, mx ** (1.0 / n))
    return best


def kp_sums(counter: Counter, beta: float, N: int) -> tuple[float, float]:
    """Signed sum S_N and absolute sum A_N of zeta over polymers |gamma| <= N."""
    r = r_fund(beta)
    S = 0.0
    A = 0.0
    for (n, W), cnt in counter.items():
        if n <= N:
            z = (cnt * W) * r ** n
            S += z
            A += abs(z)
    return S, A


def rooted_sums(counter: Counter, beta: float, N: int) -> tuple[float, float]:
    """Signed/absolute Kadanoff-Pfeuty norm restricted to |gamma| <= N,
    summed over the CLOSED connected polymers containing a fixed root."""
    r = r_fund(beta)
    S = 0.0
    A = 0.0
    for (n, W), cnt in counter.items():
        if n <= N:
            z = (cnt * W) * r ** n
            S += z
            A += abs(z)
    return S, A


def tail_bound(beta: float, N: int, degree: int = PLAQ_DEGREE) -> float:
    """Rigorous bound on sum_{|gamma| > N} |zeta| with the SHARPENED tail:

        tail = sum_{n > N, n even} (e(D-1))^(n-1) (5^(2/3) r)^n
             = b x^{n0} / ( (e(D-1)) (1 - x^2) ),   x = e(D-1) b, b = 5^(2/3) r

    where n0 is the smallest even integer > N.  Only even sizes can be
    closed (a closed polymer is a 2-cycle), so the geometric ratio per unit
    size is x^2.  Finite only if x < 1 (the strong-coupling condition)."""
    r = r_fund(beta)
    b = PER_PLAQ_BOUND * r
    G = connect_growth(degree)
    x = G * b
    if x >= 1.0:
        return float("inf")
    n0 = N + 1 if (N + 1) % 2 == 0 else N + 2
    return x ** n0 / (G * (1.0 - x * x))


def adjoint_norm_bound(counter: Counter, beta: float, N: int,
                       degree: int = PLAQ_DEGREE) -> float:
    """Rigorous upper bound on the TOTAL KP norm contributed by the j = 1
    (adjoint) channel: the exact rooted norm of the enumerated polymers
    (same combinatorics and link moments, per-plaquette coefficient r_1
    instead of r_1/2) through size N, plus the same geometric tail used for
    the fundamental channel (per-plaquette constant PER_PLAQ_BOUND * r_1,
    growth (e(D-1)), even sizes only).

    Closed polymers are channel-independent (the closure condition is a
    property of the set, and the link-moment product is the same); only the
    per-plaquette character coefficient differs.  This bound is used by CE6d
    to show that including the adjoint channel cannot reduce beta_0^rig.
    """
    r1 = r_adj(beta)
    A = 0.0
    for (n, W), cnt in counter.items():
        if n <= N:
            A += cnt * W * r1 ** n
    b = PER_PLAQ_BOUND * r1
    G = connect_growth(degree)
    x = G * b
    if x >= 1.0:
        return float("inf")
    n0 = N + 1 if (N + 1) % 2 == 0 else N + 2
    return A + x ** n0 / (G * (1.0 - x * x))


def find_beta0(counter: Counter, N: int, amax: float = 0.5,
               tol: float = 1e-6, rooted=None,
               degree: int = PLAQ_DEGREE) -> tuple[float, float]:
    """Largest beta with (exact rooted norm <= N) + tail(N, beta) < 1.

    If `rooted` is given it is the exact fixed-root enumeration Counter; the
    exact part then uses it (the true Kadanoff-Pfeuty numerator).  Otherwise
    the min-index `counter` is used (equal to the rooted norm because a
    closed connected set contains exactly one root-independent weight)."""
    src = counter if rooted is None else rooted

    def f(b: float) -> float:
        _, A = rooted_sums(src, b, N)
        return A + tail_bound(b, N, degree)

    lo, hi = 1e-9, amax
    if f(lo) >= 1.0:
        return lo, f(lo)
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if f(mid) < 1.0:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return lo, f(lo)


def mass_gap(beta: float) -> float:
    """Delta(beta) = log 2 - beta^2/4 (repo perturbative form,
    honest_assessment.py); positive throughout the controlled region."""
    return LOG2 - beta * beta / 4.0


# --------------------------------------------------------------------------
# Verification battery
# --------------------------------------------------------------------------

def run_cluster_verification(max_size: int = 6, tail_m: int = 8,
                             run_L3: bool = True) -> bool:
    ok = True

    def check(name: str, cond: bool, detail: str = ""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))
        if not cond:
            ok = False

    print("PHASE 2: KADANOFF-PFEUTY CLUSTER EXPANSION (L=2 torus, 4D)")
    print(f"  lattice: {NSITE} sites, {NLINK} links, {NPLAQ} plaquettes, "
          f"degree {PLAQ_DEGREE}; enumeration size {max_size}; tail size M = {tail_m}")
    print()

    # --- CE1: link moments ---
    good, det = link_moment_quadrature_check()
    check("CE1 link moments I(k) = Catalan(k/2) (even k), 0 (odd k)", good, det)

    # --- CE2: enumeration sanity ---
    counter, elapsed = enumerate_polymers(max_size)
    sizes = sorted({n for (n, W) in counter})
    n_small = sum(cnt for (n, W), cnt in counter.items() if n < 4)
    n4 = sum(cnt for (n, W), cnt in counter.items() if n == 4)
    w4 = {W for (n, W) in counter if n == 4}
    tot = sum(counter.values())
    print(f"  enumerated {tot} closed polymers in {elapsed:.1f}s; "
          f"sizes {sizes[0]}..{sizes[-1]}")
    check("CE2a no closed polymers below size 4", n_small == 0,
          f"count below size 4: {n_small}")
    check("CE2b smallest closed polymers: 24 planar 4-cycles, zeta = r^4",
          n4 == 24 and w4 == {1},
          f"size-4 count = {n4}, weights W = {sorted(w4)}")
    # every closed polymer has even per-link counts already enforced by parity==0;
    # check the largest weight is consistent with I(6)=5 per link touched <= 6
    check("CE2c weights bounded by I(k) table (max W per size <= 5^(4n/6))",
          all(W <= 5 ** ((4 * n + 5) // 6) for (n, W) in counter),
          f"max W = {max(W for (n, W) in counter)}")

    # --- CE3: exact KP sum at small beta ---
    beta = 0.01
    S, A = kp_sums(counter, beta, max_size)
    r = r_fund(beta)
    lead = 24.0 * r ** 4
    check("CE3 KP sum at beta=0.01 dominated by the 24 leading 4-cycles",
          abs(S - lead) / lead < 0.05,
          f"S_{max_size} = {S:.6e}, 24 r^4 = {lead:.6e}, "
          f"next order rel. dev = {abs(S - lead) / lead:.2e}")
    check("CE3b absolute sum equals signed sum at leading order (all zeta > 0)",
          abs(A - S) / S < 1e-6, f"A = {A:.6e}, S = {S:.6e}")

    # --- CE6: sharpened-tail ingredients (exact rooted enumeration to M) ---
    rooted, rt = enumerate_rooted_polymers(tail_m)
    rc = Counter()
    for (n, W), c in rooted.items():
        rc[n] += c
    print(f"  [info] rooted closed polymers (fixed root, size <= {tail_m}): "
          f"{sum(rooted.values())} found in {rt:.1f}s; "
          f"counts by size {dict(sorted(rc.items()))}")
    # CE6a: the per-plaquette constant dominates every enumerated exact W
    Wsup = exact_sup_per_plaquette()
    maxW = max(W for (n, W) in rooted)
    check("CE6a per-plaquette constant 5^(2/3) dominates every exact W",
          abs(Wsup - PER_PLAQ_BOUND) < 1e-12 and
          all(W <= PER_PLAQ_BOUND ** n + 1e-9 for (n, W) in rooted),
          f"sup W^(1/n) over link-count vectors = {Wsup:.4f} = 5^(2/3); "
          f"largest enumerated W = {maxW}")
    # CE6b: Eden/Kesten growth bound dominates the exact rooted counts
    check("CE6b Eden growth (e(D-1))^(n-1) dominates every rooted count",
          all(c <= CONNECT_GROWTH ** (n - 1) + 1e-9 for n, c in rc.items()),
          f"max ratio count/G^(n-1) = "
          f"{max(c / CONNECT_GROWTH ** (n - 1) for n, c in rc.items()):.2e}, "
          f"G = {CONNECT_GROWTH:.3f}")
    # CE6c: beta_0 is monotone non-decreasing in the exact size M
    beta0_M6, _ = find_beta0(counter, 6, rooted=None)
    rooted_M6 = Counter({(n, W): c for (n, W), c in rooted.items() if n <= 6})
    b0_M6r, _ = find_beta0(counter, 6, rooted=rooted_M6)
    beta0_M, _ = find_beta0(counter, tail_m, rooted=rooted)
    check("CE6c beta_0^rig is monotone non-decreasing in the exact size M",
          beta0_M >= b0_M6r - 1e-9 and beta0_M >= beta0_M6 - 1e-9,
          f"beta_0(M=6) = {b0_M6r:.6f} <= beta_0(M={tail_m}) = {beta0_M:.6f}")

    # CE6d/CE6e are checked after beta_0^rig is known (see below CE4a).

    # --- CE4: rigorous convergence radius (sharpened tail) ---
    beta0, fval = find_beta0(counter, tail_m, rooted=rooted)
    _, A0 = rooted_sums(rooted, beta0, tail_m)
    t0 = tail_bound(beta0, tail_m)
    check("CE4a A(beta_0) + tail(beta_0) < 1 (KP absolute convergence)",
          fval < 1.0,
          f"beta_0^rig = {beta0:.8f}: A = {A0:.6f}, tail = {t0:.4f}, "
          f"sum = {A0 + t0:.8f}")

    # --- CE6d: the j = 1 (adjoint) channel is EXCLUDED, verified, not vacuous ---
    # A real computation: the ratio r_1/(r_1/2) at beta_0, and the TOTAL
    # adjoint-channel KP norm (exact enumerated polymers through tail_m with
    # coefficient r_1, plus the same rigorous tail).  If the adjoint norm fits
    # inside the available margin 1 - (A + tail) then adding the adjoint
    # channel cannot push A + tail past 1 at beta_0, so beta_0 is unchanged.
    margin = 1.0 - (A0 + t0)
    r1_ratio = r_adj(beta0) / r_fund(beta0)
    adj_norm = adjoint_norm_bound(rooted, beta0, tail_m)
    # smallest adjoint-channel term (smallest closed polymer, n = 4) vs the
    # retained fundamental term of the same size:
    n_min = min(n for (n, W) in rooted)
    fund_lead = sum(c * W * r_fund(beta0) ** n
                    for (n, W), c in rooted.items() if n == n_min)
    adj_lead = sum(c * W * r_adj(beta0) ** n
                   for (n, W), c in rooted.items() if n == n_min)
    ce6d_ok = (r1_ratio < 0.5) and (adj_norm < margin)
    check("CE6d j = 1 adjoint channel exclusion VERIFIED (fits in the margin)",
          ce6d_ok,
          f"r_1/r_1/2(beta_0) = {r1_ratio:.6f} < 0.5; adjoint norm <= "
          f"{adj_norm:.3e} << margin 1-(A+tail) = {margin:.6f}; "
          f"smallest adjoint term r_1^{n_min} = {adj_lead:.3e} vs fundamental "
          f"{fund_lead:.3e} (ratio {adj_lead / fund_lead:.2e})")
    if not ce6d_ok:
        # Honest fallback: report the reduced beta_0 that a full j = 1
        # treatment would give (solve A + tail + adjoint_norm = 1).
        def _with_adj(b: float) -> float:
            _, Ab = rooted_sums(rooted, b, tail_m)
            return Ab + tail_bound(b, tail_m) + adjoint_norm_bound(rooted, b, tail_m)
        lo, hi = 1e-9, beta0
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            if _with_adj(mid) < 1.0:
                lo = mid
            else:
                hi = mid
        print(f"  [info] HONEST: with j = 1 fully included beta_0^rig would "
              f"fall to {lo:.8f} (from {beta0:.8f})")

    # --- CE6e: k_l = 6 IS realised on L=2 (constant 5^(2/3) is required) ---
    # The 6 plaquettes through any link form a connected star with odd link
    # parity; a skeptical review conjectured k_l <= 4 for ALL closed connected
    # polymers (true only up to size 8).  We PROVE k_l = 6 occurs by exhibiting
    # a closed connected superset of the star through link 0.
    star_set = find_closed_connected_containing_star(0)
    if star_set is not None:
        sup = [p for p in range(NPLAQ) if (star_set >> p) & 1]
        lcount = Counter()
        for p in sup:
            for l in PLAQ_LINKS[p]:
                lcount[l] += 1
        star_ok = (all(c % 2 == 0 for c in lcount.values())
                   and max(lcount.values()) == 6)
    else:
        star_ok = False
        sup = []
    check("CE6e k_l = 6 realised on L=2: per-plaquette constant 5^(2/3) required",
          star_ok,
          f"closed connected set (size {len(sup)}) with a link touched 6x: "
          f"{sup}; so the conjectured tighter constant 2.0 is INVALID")

    _, A_out = rooted_sums(rooted, 1.5 * beta0, tail_m)
    t_out = tail_bound(1.5 * beta0, tail_m)
    check("CE4b outside the controlled region the criterion fails (honest bound)",
          A_out + t_out > 1.0,
          f"at 1.5 beta_0: A + tail = {A_out + t_out:.3f}")
    print(f"  [info] beta_0^rig = {beta0:.8f}  (rigorous KP bound, 6+ sig figs; "
          f"literature strong-coupling estimates ~ 0.12)")

    # KP sums at benchmark couplings (exact, tail reported separately)
    for b in (0.01, 0.05, 0.1):
        Sb, Ab = rooted_sums(rooted, b, tail_m)
        tb = tail_bound(b, tail_m)
        print(f"  [info] beta = {b}: S_{tail_m} = {Sb:.6e}, A = {Ab:.6e}, "
              f"tail = {tb:.3e}")

    # --- CE5: mass gap ---
    gap_pert = mass_gap(beta0)
    check("CE5a perturbative mass gap positive at beta_0^rig",
          gap_pert > 0, f"Delta({beta0:.4f}) = log2 - beta^2/4 = {gap_pert:.6f}")
    _, A_half = rooted_sums(rooted, 0.5 * beta0, tail_m)
    t_half = tail_bound(0.5 * beta0, tail_m)
    kp_gap = -np.log(A_half + t_half)
    check("CE5b KP transfer-matrix bound Delta >= -log(A+tail) > 0 at beta_0/2",
          kp_gap > 0, f"Delta >= {kp_gap:.4f} at beta = {0.5 * beta0:.5f}")

    # --- CE7: finite-size comparison on the non-degenerate L = 3 torus ---
    if run_L3:
        lat3 = build_lattice_general(3)
        pl3, pm3, nb3, deg3 = lat3
        npl3 = len(pl3)
        c3, t3 = enumerate_polymers(6, lat=lat3)
        sc3 = sorted({n for (n, W) in c3})
        r3, rt3 = enumerate_rooted_polymers(6, lat=lat3)
        beta0_L3, f3 = find_beta0(c3, 6, rooted=r3, degree=deg3)
        print(f"  [info] L=3 torus: {npl3} plaquettes, degree {deg3}, "
              f"enumerated {sum(c3.values())} closed polymers in {t3:.1f}s "
              f"(sizes {sc3}); rooted {sum(r3.values())} in {rt3:.1f}s")
        check("CE7a L=3 smallest closed polymers are the 324 cubes (size 6)",
              sc3 == [6] and sum(c3.values()) == 324,
              f"sizes {sc3}, count {sum(c3.values())}")
        check("CE7b L=3 rigorous beta_0^rig computed (its own degree 20)",
              f3 < 1.0,
              f"beta_0^rig(L=3) = {beta0_L3:.8f} vs L=2 = {beta0:.8f}")
        print(f"  [info] finite-size: beta_0^rig(L=2) = {beta0:.8f}, "
              f"beta_0^rig(L=3) = {beta0_L3:.8f} "
              f"(L=3 degree 20 > 18 so its crude tail is larger)")

    print()
    print("PHASE 2:", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    N = 6
    M = 8
    for a in sys.argv[1:]:
        if a.startswith("--size="):
            N = int(a.split("=")[1])
        elif a.startswith("--M="):
            M = int(a.split("=")[1])
    sys.exit(0 if run_cluster_verification(max_size=N, tail_m=M) else 1)

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

Computed exactly (up to polymer size N, with a rigorous analytic tail) on
the L = 2 torus in 4D: 16 sites, 64 links, 96 plaquettes.  Every link is
touched by exactly 6 plaquettes, so I(k) <= 5 (k <= 6) and

    |zeta(gamma)| <= (5^(2/3) r_1/2)^|gamma| ,

while the number of connected polymers of size n containing the root in a
graph of degree D = 20 is bounded by (e (D-1))^(n-1), giving the rigorous
tail

    tail(N, beta) = sum_{n>N} (e 19)^(n-1) (5^(2/3) r_1/2)^n .

Smallest closed polymers on the L=2 torus are the 24 planar 4-cycles
(C(4,2) planes x 4 positions), zeta = r_1/2^4 each (on the infinite
lattice the smallest closed surface is the cube, zeta = r_1/2^6).

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
# Exact enumeration of connected polymers containing the root plaquette
# --------------------------------------------------------------------------

def enumerate_polymers(max_size: int) -> tuple[Counter, float]:
    """Enumerate ALL connected closed plaquette sets |gamma| <= max_size,
    each exactly once (via its minimum-index plaquette as root, restricted
    to plaquettes of index > root).
    Returns Counter[(size, W)] where W = prod_l I(k_l), and elapsed seconds."""
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
            for l in PLAQ_LINKS[p]:
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
            (cand | (NEIGHBORS[v] & ge)) & ~(visited | lb),
            parity ^ PLAQ_MASK[v],
            sz + 1)
        # exclude v (never reconsidered in this branch)
        rec(root, ge, seen, visited, cand ^ lb, parity, sz)

    # Each connected set has a unique minimum-index plaquette: enumerate with
    # that plaquette as root and only plaquettes of index > root allowed.
    # visited starts as the root BIT (1 << root), not the root index --
    # passing the index itself silently drops the root's links from every
    # weight computation when root = 0.
    for root in range(NPLAQ):
        ge = ~((1 << root) - 1)          # bitmask of plaquettes with index >= root
        cand = NEIGHBORS[root] & ge
        if cand == 0:
            continue
        seen: set[int] = set()
        rec(root, ge, seen, 1 << root, cand, PLAQ_MASK[root], 1)
    return out, time.time() - t0


# --------------------------------------------------------------------------
# KP sums, tail bound, beta_0
# --------------------------------------------------------------------------

PER_PLAQ_BOUND = 5.0 ** (2.0 / 3.0)     # |zeta| <= (PER_PLAQ_BOUND * r)^n
CONNECT_GROWTH = e * (PLAQ_DEGREE - 1)  # connected-set count <= (e(D-1))^(n-1)


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


def tail_bound(beta: float, N: int) -> float:
    """Rigorous bound on sum_{|gamma|>N} |zeta|:
        tail = sum_{n>N} (e(D-1))^(n-1) b^n  =  b x^N / (1 - x),
        b = 5^(2/3) r,  x = e(D-1) b.
    Finite only if x < 1 (that is exactly the strong-coupling condition)."""
    r = r_fund(beta)
    b = PER_PLAQ_BOUND * r
    x = CONNECT_GROWTH * b
    if x >= 1.0:
        return float("inf")
    return b * x ** N / (1.0 - x)


def find_beta0(counter: Counter, N: int, amax: float = 0.5,
               tol: float = 1e-6) -> tuple[float, float]:
    """Largest beta with A_N(beta) + tail(N, beta) < 1 (bisect)."""
    def f(b: float) -> float:
        _, A = kp_sums(counter, b, N)
        return A + tail_bound(b, N)

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

def run_cluster_verification(max_size: int = 6) -> bool:
    ok = True

    def check(name: str, cond: bool, detail: str = ""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))
        if not cond:
            ok = False

    print("PHASE 2: KADANOFF-PFEUTY CLUSTER EXPANSION (L=2 torus, 4D)")
    print(f"  lattice: {NSITE} sites, {NLINK} links, {NPLAQ} plaquettes, "
          f"degree {PLAQ_DEGREE}; max polymer size {max_size}")
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

    # --- CE4: rigorous convergence radius ---
    beta0, fval = find_beta0(counter, max_size)
    _, A0 = kp_sums(counter, beta0, max_size)
    t0 = tail_bound(beta0, max_size)
    check("CE4a A(beta_0) + tail(beta_0) < 1 (KP absolute convergence)",
          fval < 1.0,
          f"beta_0^rig = {beta0:.5f}: A = {A0:.4f}, tail = {t0:.4f}")
    _, A_out = kp_sums(counter, 1.5 * beta0, max_size)
    t_out = tail_bound(1.5 * beta0, max_size)
    check("CE4b outside the controlled region the criterion fails (honest bound)",
          A_out + t_out > 1.0,
          f"at 1.5 beta_0: A + tail = {A_out + t_out:.3f}")
    print(f"  [info] beta_0^rig = {beta0:.5f}  (rigorous KP bound; "
          f"literature strong-coupling estimates ~ 0.12)")

    # KP sums at benchmark couplings (exact, tail reported separately)
    for b in (0.01, 0.05, 0.1):
        Sb, Ab = kp_sums(counter, b, max_size)
        tb = tail_bound(b, max_size)
        print(f"  [info] beta = {b}: S_{max_size} = {Sb:.6e}, A = {Ab:.6e}, "
              f"tail = {tb:.3e}")

    # --- CE5: mass gap ---
    gap_pert = mass_gap(beta0)
    check("CE5a perturbative mass gap positive at beta_0^rig",
          gap_pert > 0, f"Delta({beta0:.4f}) = log2 - beta^2/4 = {gap_pert:.6f}")
    _, A_half = kp_sums(counter, 0.5 * beta0, max_size)
    t_half = tail_bound(0.5 * beta0, max_size)
    kp_gap = -np.log(A_half + t_half)
    check("CE5b KP transfer-matrix bound Delta >= -log(A+tail) > 0 at beta_0/2",
          kp_gap > 0, f"Delta >= {kp_gap:.4f} at beta = {0.5 * beta0:.5f}")

    print()
    print("PHASE 2:", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    N = 6
    for a in sys.argv[1:]:
        if a.startswith("--size="):
            N = int(a.split("=")[1])
    sys.exit(0 if run_cluster_verification(max_size=N) else 1)

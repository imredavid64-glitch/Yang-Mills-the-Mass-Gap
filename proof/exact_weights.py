"""
Exact SU(2) Haar integrals of products of plaquette traces (no Monte Carlo).

WHY THIS MODULE EXISTS
----------------------
proof/cluster_expansion.py weights a closed plaquette set gamma by
    W(gamma) = prod_l I(k_l),   I(k) = int (Tr U)^k dU = Catalan(k/2),
i.e. it treats each link as the moment of ONE trace.  The correct quantity is
    J(gamma) = int prod_{p in gamma} Tr(U_p) dU
in which the link integrals contract indices ACROSS plaquettes.  Catalan(k/2)
is only the DIMENSION of the SU(2)-invariant subspace of V^{(x)k}; it is not
the value of the trace network.

METHOD (exact, linear algebra only)
-----------------------------------
* int U^{(x)k} dU = P_k, the orthogonal projector onto SU(2)-invariants of
  V^{(x)k}.  Invariants are spanned by pairings eps_{i_a i_b}, so
      P_k = V^T G^+ V   with V rows of pairing vectors, G = V V^T.
* For det U = 1: U^{-1} = eps U^T eps^{-1}.
* The integral over all links is a finite tensor-network contraction.

LEMMA (closed oriented surfaces; proved here, machine-checked below)
--------------------------------------------------------------------
Let gamma be a set of plaquettes such that every link lies in exactly two of
them and the plaquettes can be oriented so that each link is traversed once in
each direction (Tr U = Tr U^-1 for SU(2), so orientation is free).  Then
        int prod_p Tr(U_p) dU  =  2^(C - E),
E = number of links, C = number of "corner cycles" (components of the graph on
(plaquette, vertex) corners joined across shared links).
Proof.  A link carries U in one plaquette and U^-1 in the other, and Schur
orthogonality gives  int U_ab (U^-1)_cd dU = (1/2) delta_ad delta_bc.  Each link
contributes 1/2 and a pair of Kronecker deltas joining the index labels at its
two ends; the labels are the corners, so the index graph is a disjoint union of
closed loops, one per corner cycle, each evaluating to delta_aa = 2.  QED
Consequence: the 1 x 1 x t box (V = 4t+4, E = 8t+4, C = V) has J = 2^(-4t).

Checks (run this file):
  EW1  tr P_k = Catalan(k/2)                 (where the old formula came from)
  EW2  elementary cube  J = 2^-4             (old code: W = 1)
  EW4  all size-4 closed polymers on the L=2 torus: J = 2^-4 (old code: W = 1)
  EW5  lemma 2^(C-E) equals the tensor-contraction value (cube, torus 4-cycle)
  EW6  lemma gives J(1x1xt box) = 2^(-4t) for t = 1..10
"""
from __future__ import annotations

import itertools
import sys
from functools import lru_cache
from math import comb

import numpy as np

EPS = np.array([[0.0, 1.0], [-1.0, 0.0]])
EPSINV = EPS.T


@lru_cache(maxsize=None)
def haar_moment_tensor(k: int) -> np.ndarray:
    """E[i_1..i_k, j_1..j_k] = int U_{i1 j1} ... U_{ik jk} dU  (SU(2))."""
    if k == 0:
        return np.array(1.0)
    if k % 2:
        return np.zeros((2,) * (2 * k))

    def _pairings(idx):
        if not idx:
            yield []
            return
        a = idx[0]
        for i in range(1, len(idx)):
            rest = idx[1:i] + idx[i + 1:]
            for m in _pairings(rest):
                yield [(a, idx[i])] + m

    vecs = []
    for m in _pairings(list(range(k))):
        t = np.zeros((2,) * k)
        for idx in itertools.product((0, 1), repeat=k):
            v = 1.0
            for a, b in m:
                v *= EPS[idx[a], idx[b]]
            t[idx] = v
        vecs.append(t.reshape(-1))
    V = np.array(vecs)
    P = V.T @ np.linalg.pinv(V @ V.T) @ V
    return P.reshape((2,) * (2 * k))


def _inverse_slot(E: np.ndarray, k: int, s: int) -> np.ndarray:
    """Turn slot s of the moment tensor from U into U^{-1} = eps U^T eps^-1."""
    n = E.ndim
    lab = list(range(n))
    a, b = n, n + 1
    out = lab.copy()
    out[s], out[k + s] = a, b
    return np.einsum(E, lab, EPS, [a, lab[k + s]], EPSINV, [lab[s], b], out)


def polymer_integral(plaquettes) -> float:
    """int prod_p Tr(U_p) dU.  `plaquettes` = list of plaquettes, each a list of
    four (link_id, sign) pairs in cyclic order (sign -1 means U^{-1})."""
    slots = {}
    for p, plaq in enumerate(plaquettes):
        for m, (l, sg) in enumerate(plaq):
            slots.setdefault(l, []).append((p, m, sg))
    ops = []
    for l, lst in slots.items():
        k = len(lst)
        E = haar_moment_tensor(k)
        if k % 2:
            return 0.0
        for s, (_, _, sg) in enumerate(lst):
            if sg < 0:
                E = _inverse_slot(E, k, s)
        rows = [4 * p + m for (p, m, _) in lst]
        cols = [4 * p + (m + 1) % 4 for (p, m, _) in lst]
        ops += [E, rows + cols]
    return float(np.einsum(*ops, [], optimize="greedy"))


# --------------------------------------------------------------------------
# Z^4 geometry helpers
# --------------------------------------------------------------------------

def plaq_Z4(x, mu, nu):
    """Plaquette (x; mu<nu) as [(link, sign)]*4, link = (site, dir)."""
    x = tuple(x)
    xm = tuple(x[i] + (i == mu) for i in range(4))
    xn = tuple(x[i] + (i == nu) for i in range(4))
    return [((x, mu), 1), ((xm, nu), 1), ((xn, mu), -1), ((x, nu), -1)]


def box_plaquettes(t: int):
    """Surface of the 1 x 1 x t box (long axis = direction 3): 2 + 4t plaquettes."""
    P = [plaq_Z4((0, 0, 0, 0), 0, 1), plaq_Z4((0, 0, 0, t), 0, 1)]
    for z in range(t):
        for y in (0, 1):
            P.append(plaq_Z4((0, y, 0, z), 0, 3))
        for x in (0, 1):
            P.append(plaq_Z4((x, 0, 0, z), 1, 3))
    return P


def surface_integral(plaquettes, endpoints):
    """Lemma value 2^(C-E) for a closed coherently-orientable surface in which every
    link lies in exactly two plaquettes; None if the hypotheses fail.
    `plaquettes`: [[(link, sign)]*4] with sign = direction relative to the link's
    canonical direction; `endpoints(link)` -> (vertex0, vertex1)."""
    slots = {}
    for p, plaq in enumerate(plaquettes):
        for l, sg in plaq:
            slots.setdefault(l, []).append((p, sg))
    if any(len(v) != 2 for v in slots.values()):
        return None
    # coherent orientation: sigma_q = - sigma_p * d_p * d_q across every link
    sigma = {0: 1}
    todo = [0]
    adj = {}
    for l, ((p, dp), (q, dq)) in slots.items():
        adj.setdefault(p, []).append((q, -dp * dq))
        adj.setdefault(q, []).append((p, -dp * dq))
    while todo:
        p = todo.pop()
        for q, rel in adj.get(p, []):
            want = sigma[p] * rel
            if q in sigma:
                if sigma[q] != want:
                    return None
            else:
                sigma[q] = want
                todo.append(q)
    if len(sigma) != len(plaquettes):
        return None                       # not link-connected
    parent = {}

    def find(a):
        parent.setdefault(a, a)
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for l, ((p, _), (q, _)) in slots.items():
        for v in endpoints(l):
            parent[find((p, v))] = find((q, v))
    C = len({find(a) for a in list(parent)})
    return 2.0 ** (C - len(slots))


def endpoints_Z4(link):
    x, mu = link
    return x, tuple(x[i] + (i == mu) for i in range(4))


def run() -> bool:
    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))
        ok &= bool(cond)

    print("EXACT SU(2) HAAR POLYMER INTEGRALS (tensor contraction)")
    cat = lambda m: comb(2 * m, m) // (m + 1)
    for k in (2, 4, 6):
        tr = float(np.trace(haar_moment_tensor(k).reshape(2 ** k, 2 ** k)))
        check(f"EW1 tr P_{k} = Catalan({k // 2}) = {cat(k // 2)}",
              abs(tr - cat(k // 2)) < 1e-9, f"{tr:.6f}")

    J = polymer_integral([plaq_Z4((0, 0, 0, 0), 0, 1)])
    check("EW0 single plaquette integrates to 0", abs(J) < 1e-12, f"J = {J:.2e}")

    J = polymer_integral(box_plaquettes(1))
    check("EW2 elementary cube (6 plaquettes): J = 2^-4  (old code W = 1)",
          abs(J - 2.0 ** -4) < 1e-12, f"J = {J:.10f}")

    # The 4-cycles on the L=2 torus: 4-sets containing plaquette 0 with every
    # link covered an even number of times (the diagonal plaquette of a 4-cycle
    # shares no link with plaquette 0, so search all other plaquettes).
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))
    import proof.cluster_expansion as ce
    others = range(1, ce.NPLAQ)
    SG = (1, 1, -1, -1)
    vals, n4 = set(), 0
    for trio in itertools.combinations(others, 3):
        m = ce.PLAQ_MASK[0]
        for p in trio:
            m ^= ce.PLAQ_MASK[p]
        if m == 0:
            n4 += 1
            faces = [[(l, s) for l, s in zip(ce.PLAQ_LINKS[p], SG)] for p in (0,) + trio]
            vals.add(round(polymer_integral(faces), 12))
    check("EW4 closed 4-sets through plaquette 0 on the L=2 torus: J = 2^-4  (old code W = 1)",
          n4 >= 1 and vals == {2.0 ** -4}, f"found {n4}, distinct exact values {sorted(vals)}")

    # EW5: the lemma against the tensor contraction
    Jc = polymer_integral(box_plaquettes(1))
    Lc = surface_integral(box_plaquettes(1), endpoints_Z4)
    ep_torus = lambda l: (l // 4, (l // 4) ^ (1 << (3 - l % 4)))
    lemma_t = []
    for trio in itertools.combinations(range(1, ce.NPLAQ), 3):
        m = ce.PLAQ_MASK[0]
        for q in trio:
            m ^= ce.PLAQ_MASK[q]
        if m == 0:
            faces = [[(l, sg) for l, sg in zip(ce.PLAQ_LINKS[q], (1, 1, -1, -1))]
                     for q in (0,) + trio]
            lemma_t.append(surface_integral(faces, ep_torus))
    check("EW5 lemma 2^(C-E) == tensor contraction (cube, and the L=2 torus 4-cycle)",
          Lc is not None and abs(Lc - Jc) < 1e-12 and lemma_t == [2.0 ** -4],
          f"cube lemma {Lc} vs exact {Jc}; torus 4-cycle lemma {lemma_t}")
    vals_box = [surface_integral(box_plaquettes(t), endpoints_Z4) for t in range(1, 11)]
    check("EW6 lemma: J(1x1xt box) = 2^(-4t), t = 1..10",
          all(v == 2.0 ** (-4 * t) for t, v in zip(range(1, 11), vals_box)),
          f"t=1..10 -> 2^-4, 2^-8, ..., 2^-40 ; t=2 Monte Carlo (scratch): 0.00439 +- 0.00041")
    print("EXACT WEIGHTS:", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    sys.exit(0 if run() else 1)

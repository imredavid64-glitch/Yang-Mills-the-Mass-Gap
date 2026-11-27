"""
Independent cross-check of Lemma 5 in proof/THEOREM.md: the exact numbers
C_n of link-connected plaquette sets in Z^4 that contain a fixed plaquette and in which
every link lies in >= 2 plaquettes  (claim: C_n = 0 for n < 6, C_6 = 4, C_7 = 0).

proof/finner_kp.py computes these with a Redelmeier enumeration and hand-written
adjacency.  This module uses a DIFFERENT algorithm and independently derived geometry:
  * plaquette-link incidence is taken from exact_weights.plaq_Z4 and plaquettes through
    a link are found by testing candidate base points against that incidence
    (no formula for the neighbours is shared with finner_kp.py);
  * sets are grown level by level (all connected k-sets containing the root, deduplicated
    as frozensets), pruning a set only when it provably cannot be completed:
    deficiency(S) = sum_l max(0, 2 - k_l(S)) > 4 * (N - |S|), since one added plaquette
    can supply at most 4 link incidences.
"""
from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from proof.exact_weights import plaq_Z4  # noqa: E402


def links_of(p):
    x, mu, nu = p
    return [l for (l, _s) in plaq_Z4(x, mu, nu)]


def plaquettes_through(link):
    """All plaquettes containing `link`, found by testing candidates against the incidence."""
    y, d = link
    out = []
    for mu in range(4):
        for nu in range(mu + 1, 4):
            if d not in (mu, nu):
                continue
            for shift in range(4):
                for sgn in (0, 1):
                    x = tuple(y[i] - (sgn if i == shift else 0) for i in range(4))
                    p = (x, mu, nu)
                    if link in links_of(p) and p not in out:
                        out.append(p)
    return out


_nb_cache: dict = {}


def neighbours(p):
    if p not in _nb_cache:
        s = set()
        for l in links_of(p):
            s.update(plaquettes_through(l))
        s.discard(p)
        _nb_cache[p] = frozenset(s)
    return _nb_cache[p]


def deficiency(S):
    cnt = Counter()
    for p in S:
        for l in links_of(p):
            cnt[l] += 1
    return sum(max(0, 2 - v) for v in cnt.values())


def covered_twice_by_levels(N, root=((0, 0, 0, 0), 0, 1)):
    level = {frozenset([root])}
    found = Counter()
    for k in range(1, N + 1):
        if k >= 2:
            pass
        nxt = set()
        for S in level:
            d = deficiency(S)
            if d == 0:
                found[k] += 1
            if k == N:
                continue
            if d > 4 * (N - k):
                continue                       # cannot be completed within N plaquettes
            cand = set()
            for p in S:
                cand |= neighbours(p)
            cand -= S
            for q in cand:
                nxt.add(S | {q})
        level = nxt
    return found, len(level)


def run(N: int = 7) -> bool:
    print(f"INDEPENDENT CROSS-CHECK OF LEMMA 5 (level-by-level growth, N = {N})")
    nb0 = neighbours(((0, 0, 0, 0), 0, 1))
    ok = len(nb0) == 20
    print(f"  [{'PASS' if len(nb0) == 20 else 'FAIL'}] plaquette degree is 20 (independently derived adjacency): {len(nb0)}")
    per_link = defaultdict(set)
    for p in nb0 | {((0, 0, 0, 0), 0, 1)}:
        for l in links_of(p):
            per_link[l].add(p)
    six = all(len(plaquettes_through(l)) == 6 for l in links_of(((0, 0, 0, 0), 0, 1)))
    print(f"  [{'PASS' if six else 'FAIL'}] every link lies in exactly 6 plaquettes")
    ok &= six
    found, _last = covered_twice_by_levels(N)
    good = dict(found) == {6: 4}
    print(f"  [{'PASS' if good else 'FAIL'}] sets with every link covered >= 2 times, by size: {dict(sorted(found.items()))}"
          f"  (expected {{6: 4}}: none below 6, four cubes, none of size 7)")
    ok &= good
    print("COUNT CROSS-CHECK:", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    sys.exit(0 if run() else 1)

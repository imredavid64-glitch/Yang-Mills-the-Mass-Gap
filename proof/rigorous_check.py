"""
Computer-assisted certificate for proof/THEOREM.md  (interval arithmetic, mpmath.iv).

It certifies, for beta <= BETA_STAR, condition (C_delta) of Theorem A in THEOREM.md in the form

    42 * [ C_6 X^6 + C_7 X^7 + G^7 X^8 / (1 - G X) ] / (1 - X^6)  <=  alpha ,
                                                      X = eps_up(beta) e^s,  s = alpha + delta,

(the factor 42 = 21 * 2 comes from the slack alpha|g|/2 in (C_delta); 1/(1 - X^6) bounds
1/(1-u) because u <= X^n <= X^6 for n >= 6), and reports the certified delta > 0.
It also certifies condition (K2)  G * eps_up * exp(12 alpha/7 + mu) < 1  needed by Theorem C
(exponential clustering at rate mu), with mu the certified rate.

Ingredients (all proved in THEOREM.md; the one cited black box there, B2, is not used by this check):
  * eps_up(beta) = beta e^beta 5^(1/6)/2 + (cosh beta - 1)/4   >= ||g||_{L^6(Haar)}   (Lemma 4)
  * G = e * 20                                                   (Lemma 3, plaquette graph degree 20)
  * C_6 = 4, C_7 = 0: exhaustive search (recomputed here, ~15 s)  (Lemma 5, computer-assisted)

Monotonicity: eps_up is increasing in beta and the left side is increasing in x,
so a certificate at BETA_STAR with a fixed (alpha, s) holds for every beta <= BETA_STAR.
Interval arithmetic gives outward-rounded bounds, so the printed delta is a valid
lower bound (modulo the correctness of mpmath's interval implementation).
"""
from __future__ import annotations

import sys
from pathlib import Path

from mpmath import iv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from proof.finner_kp import covered_twice_counts, animal_counts  # noqa: E402

iv.dps = 40
E = iv.e
G = E * 20
COUNTS = {6: 4, 7: 0}


def eps_up(beta):
    five_sixth_root = iv.exp(iv.log(5) / 6)
    cosh = (iv.exp(beta) + iv.exp(-beta)) / 2
    return beta * iv.exp(beta) * five_sixth_root / 2 + (cosh - 1) / 4


def lhs(beta, s):
    """Interval enclosure of 42 [ C6 X^6 + C7 X^7 + G^7 X^8/(1-GX) ] / (1 - X^6), X = eps_up e^s."""
    x = eps_up(beta) * iv.exp(s)
    gx = G * x
    if not (gx.b < 1):
        return None
    exact = sum(c * x ** n for n, c in COUNTS.items())
    return 42 * (exact + G ** 7 * x ** 8 / (1 - gx)) / (1 - x ** 6)


def best_s_float(beta_f):
    """Float search for a good s (any s the certificate accepts is fine)."""
    best = (-1.0, 0.001)
    for k in range(1, 4000):
        s = k * 0.001
        r = lhs(iv.mpf(beta_f), iv.mpf(s))
        if r is None:
            break
        d = s - float(r.b)
        if d > best[0]:
            best = (d, s)
    return best


def certify(beta_f, s_f):
    """Return (alpha, mu, k2_ok).  alpha = upper endpoint of the left side of (K1); mu = lower
    endpoint of s - alpha, so alpha + mu <= s and (C_mu) holds with this alpha (monotone in X).
    k2_ok certifies (K2):  G * eps_up(beta) * exp(12 alpha / 7 + mu) < 1  (Theorem C)."""
    beta, s = iv.mpf(beta_f), iv.mpf(s_f)
    r = lhs(beta, s)
    assert r is not None, "G*x >= 1"
    alpha = iv.mpf(r.b)              # upper endpoint: alpha >= LHS
    mu = iv.mpf((s - alpha).a)       # certified lower bound for the decay rate
    k2 = G * eps_up(beta) * iv.exp(12 * alpha / 7 + mu)
    return alpha, mu, bool(k2.b < 1)


def run() -> bool:
    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))
        ok &= bool(cond)

    print("CERTIFIED STRONG-COUPLING CONVERGENCE (interval arithmetic)")
    found = covered_twice_counts(7)
    check("C6 = 4, C7 = 0 (exhaustive search, every-link-covered-twice sets containing a plaquette; none below 6)",
          dict(found) == {6: 4}, f"{dict(sorted(found.items()))}")
    ac = animal_counts(5)
    from math import comb
    check("Lemma 3 sanity: N_n <= (1/n) C(20 n, n-1) <= (e 20)^(n-1) for n <= 5",
          all(ac[n] <= comb(20 * n, n - 1) / n <= (2.718281828459045 * 20) ** (n - 1) for n in ac),
          ", ".join(f"N_{n}={ac[n]}" for n in sorted(ac)))

    # largest beta (on a 1e-4 grid) for which some s certifies delta > 0
    lo = 0.0
    for k in range(100, 400):
        b = k * 1e-4
        d, s = best_s_float(b)
        if d > 0:
            lo = b
        else:
            break
    print(f"  [info] float scan: certificate possible up to beta ~ {lo:.4f}")
    BETA_STAR = round(lo - 1e-4, 4)          # stay one grid step inside
    d, s = best_s_float(BETA_STAR)
    s = round(s, 3)
    alpha, delta_cert, k2_ok = certify(BETA_STAR, s)
    check(f"CERT beta <= {BETA_STAR}: (C_mu) holds with s = {s}, alpha = {float(alpha):.6f}; "
          f"certified mu >= {float(delta_cert):.6f} > 0",
          delta_cert > 0)
    check(f"CERT (K2) G*eps*exp(12 alpha/7 + mu) < 1 at beta = {BETA_STAR}", k2_ok)
    print(f"\n  >>> BETA_STAR = {BETA_STAR},  certified decay rate mu_min = {float(delta_cert):.6f}")
    for b in (0.002, 0.005, 0.01, BETA_STAR):
        d, s = best_s_float(b)
        a, dc, k2b = certify(b, round(s, 3))
        print(f"  [info] beta = {b:<7} decay rate mu >= {float(dc):.4f}   alpha = {float(a):.4f}   "
              f"(K2 {'ok' if k2b else 'FAILS'})")
        ok &= k2b
    print("RIGOROUS CHECK:", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    sys.exit(0 if run() else 1)

"""
What can honestly be said about the SU(2) Wilson-action gap near beta = 0.

This replaces the claim in proof/transfer.py that "Delta(0) = log 2", which is
hard-coded there (`return math.log(2)`) and "verified" against a hand-built
spectrum [1.0] + [0.5]*n.  An earlier draft of THIS file offered "4 log 2" as a
replacement; that was not derived and is withdrawn.

ESTABLISHED
-----------
(a) At beta = 0 the links are independent Haar variables, so every connected
    correlator of gauge-invariant local observables at separated points is
    exactly 0 (the repo's own check OS1c shows the same numerically).  The
    correlation length is therefore 0 and the gap, in lattice units, is
    formally +infinity.  There is no finite "Delta(0) = log 2" for the Wilson
    action; log 2 = -log(1/d) is a single-link eigenvalue ratio of a
    different (heat-kernel-type) kernel and is not a physical excitation
    (a lone j=1/2 link violates Gauss's law).

(b) Exact Haar integrals (proof/exact_weights.py): the elementary cube and
    the 1x1x1 box have  int prod_p Tr U_p dU = 2^-4.

LEADING-ORDER STRONG-COUPLING DECAY RATE (heuristic, not a theorem here)
------------------------------------------------------------------------
Connecting two plaquette operators at Euclidean separation t needs a closed
surface (a 1x1xt box): 4t side plaquettes, each carrying the character
coefficient r = beta/2 + O(beta^3), with Haar weight 2^(V-E) = 2^(-4t).  That
gives <P(0);P(t)> ~ (beta/4)^(4t), i.e. a decay rate

        m(beta) ~ 4 ln(4/beta)  -> infinity as beta -> 0.

The weight 2^(-4t) of that minimal surface is now PROVED for every t (lemma in
proof/exact_weights.py: closed coherently oriented surfaces have
int prod Tr U_p = 2^(C-E); for the box C = V = 4t+4, E = 8t+4) and machine-checked
against the exact tensor contraction (t = 1) and, for t = 2, against a Monte Carlo
estimate 0.00439 +- 0.00041 vs 2^-8 = 0.00391 (scratch run).  What is NOT proved:
that this minimal surface dominates the correlator, i.e. control of the
O(beta) corrections from larger surfaces and other representations.  So the
rate 4 ln(4/beta) is a leading-order result, not a theorem.  It agrees with the
familiar strong-coupling form
m = -4 ln u, u = I_2/I_1 ~ beta/4, as I recall it from the literature.
"""
import math


def strong_coupling_decay_rate(beta: float) -> float:
    """Leading-order glueball-type decay rate 4 ln(4/beta) (heuristic)."""
    if beta <= 0:
        return math.inf
    return 4.0 * math.log(4.0 / beta)


if __name__ == "__main__":
    for b in (0.5, 0.1, 0.0147, 0.0):
        print(f"beta = {b:<7} leading-order rate 4 ln(4/beta) = "
              f"{strong_coupling_decay_rate(b):.4f}   (repo's claimed Delta = log 2 = {math.log(2):.4f})")

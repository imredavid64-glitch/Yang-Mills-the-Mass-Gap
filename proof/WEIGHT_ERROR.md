# Phase 2 polymer weights: what is wrong, and what is not shown

`proof/cluster_expansion.py` weights a closed plaquette set `gamma` by
`W = prod_l I(k_l)` with `I(k) = Catalan(k/2)`, treating every link as the
moment of a single trace. The quantity that actually appears is

    J(gamma) = integral of prod_{p in gamma} Tr(U_p) dU

where link integrals contract indices across different plaquettes.
`Catalan(k/2)` is only the *dimension* of the SU(2)-invariant subspace of
`V^(x)k` (it equals `tr P_k`, checked in `exact_weights.py`).

## Verified by exact tensor contraction (`proof/exact_weights.py`)

| polymer | code `W` | exact `J` |
|---|---|---|
| elementary cube (6 plaquettes, 12 links) | 1 | 2^-4 |
| 1x1x1 box (same set) | 1 | 2^-4 |
| planar 4-cycles on the L=2 torus (3 spot-checked by Monte Carlo, 0.060-0.063) | 1 | ~2^-4 |

One size-8 polymer on the L=2 torus (`[0,1,3,12,25,63,75,87]`) gave
`J = 2^-8` after ~16 minutes of contraction. I did **not** compare it with the
code's `W`, and the run was too slow to cover the other 76 rooted polymers.

## What this does and does not show

- The code's weights are wrong, so "exact" / "rigorous" labels on Phase 2 are
  unjustified.
- For the polymers tested the code *over*-states the weight (by 16x). That is
  the conservative direction, so I have **not** shown the old bound is invalid.
  I have not checked links touched 4 or 6 times.
- The "exact supremum 5^(2/3)" per-plaquette constant was derived for the wrong
  `W`. It is also weaker than the trivial bound `|Tr U| <= 2`.
- At `beta_0` the old output reads `A = 0.000000, tail = 0.9943`: the result is
  carried entirely by the Eden-type tail estimate, not by the enumeration.

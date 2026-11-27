# Strong-coupling clustering for 4D SU(2) lattice gauge theory: statement and proofs

**Scope.** This is the classical strong-coupling regime (Osterwalder–Seiler 1978) at a *fixed*
lattice spacing. It says nothing about the continuum limit (β → ∞) and does not address the Clay
Millennium problem. Its value is that the argument is written out and the cited parts are isolated.

**What is proved here, what is computer-assisted, what is cited**

| Part | Status |
|---|---|
| Theorem A (Dobrushin-type convergence + decay for abstract polymer gases) | proved below; sanity-tested in `proof/dobrushin_toy_test.py` |
| Lemmas 1–4 (polymer representation, vanishing, animal bound, Finner, analytic bound on ε) | proved below |
| Lemma 5 (exact polymer counts C₆=4, C₇=0) | computer-assisted exhaustive search |
| Final numerical inequality | interval arithmetic (`proof/rigorous_check.py`) |
| **B1**: from the polymer-gas bounds to decay of correlations of local gauge-invariant observables | **cited** (standard cluster-expansion corollary; NOT proved here) |
| **B2**: reflection positivity + exponential clustering ⇒ transfer-matrix gap (OS reconstruction) | **cited** |

## Setting

Wilson action on Z⁴, gauge group SU(2), Haar measure `dU` (probability). With `q = ½ Tr U ∈ [-1,1]`:

    f(U) = e^{β q} / a(β),   a(β) = ∫ e^{β q} dU,   g = f − 1,   ∫ g dU = 0.

`Z = ∫ ∏_p f(U_p) dU`. Plaquettes are adjacent iff they share a link; every plaquette has exactly
**D = 20** neighbours and every link lies in exactly **6** plaquettes.

## Theorem A (abstract polymer gas)

Let Γ be a set of "polymers" with integer sizes `|γ| ≥ 1`, a symmetric incompatibility relation `≁`
with `γ ≁ γ`, and weights `ζ: Γ → ℂ`. Write `N[γ] = {γ' : γ' ≁ γ}`, `N*(γ) = N[γ] ∖ {γ}`, and for finite
Θ ⊂ Γ let `Z_Θ = Σ ∏ ζ` over families of pairwise compatible polymers in Θ (`Z_∅ = 1`). For
`γ ∈ Θ` put `R(Θ,γ) = Z_{Θ∖N[γ]} / Z_{Θ∖{γ}}`. Define the chain metric
`D(γ,γ') = min Σ_{i≥1} |h_i|` over chains `γ = h_0, h_1, …, h_m = γ'` with `h_i ≁ h_{i−1}`.

**Condition (C_δ).** There are `α > 0, δ ≥ 0` such that, with `u(γ) = |ζ(γ)| e^{α|γ|}`, we have
`u(γ) ≤ 1/2` for all γ and, for all γ₀,

    Σ_{γ' ∈ N*(γ₀)}  u(γ') e^{δ|γ'|} / (1 − u(γ'))   ≤   α|γ₀| / 2.

**Theorem A.** Under (C_δ), for every finite Θ ⊂ Γ:
1. `Z_Θ ≠ 0`;
2. `|R(Θ,γ)| ≤ e^{α|γ|}` for all γ ∈ Θ;
3. if γ ∈ Θ ∩ Θ' and Θ, Θ' contain the same polymers in the ball `B_ℓ(γ) = {γ' : D(γ,γ') ≤ ℓ}`, then
   `|R(Θ,γ) − R(Θ',γ)| ≤ 2 e^{α|γ|} e^{−δℓ}`  (any integer ℓ).

*Proof.* Identities. For γ ∈ Θ, splitting families by whether they contain γ gives
`Z_Θ = Z_{Θ∖γ} + ζ(γ) Z_{Θ∖N[γ]}`, i.e. `Z_Θ / Z_{Θ∖γ} = 1 + ζ(γ) R(Θ,γ)`. (I1)
Fix a global order on Γ. For γ₀ ∈ Θ let `γ_1 < … < γ_k` be the elements of `N*(γ₀) ∩ Θ`,
`Θ_0 = Θ ∖ N[γ₀]`, `Θ_j = Θ_{j−1} ∪ {γ_j}`; then `Θ_k = Θ ∖ γ₀` and `Θ_j ∖ γ_j = Θ_{j−1}`. By (I1),
`Z_{Θ_j} / Z_{Θ_{j−1}} = 1 + ζ_j R_j`, `R_j = R(Θ_j, γ_j)`, so, when all factors are nonzero,

    R(Θ,γ₀) = Z_{Θ_0} / Z_{Θ_k} = ∏_{j=1}^k (1 + ζ_j R_j)^{-1}.          (I2)

*(1),(2) by induction on |Θ|.* Claim H_n: for |Θ| ≤ n, `Z_Θ ≠ 0` and `|R(Θ,γ)| ≤ ρ(γ) := e^{α|γ|}`.
H_0 holds (`Z_∅ = 1`). Assume H_n, let |Θ| = n+1 and γ₀ ∈ Θ. Every Θ_j ⊂ Θ ∖ γ₀ has ≤ n elements, so
`Z_{Θ_j} ≠ 0` and `|R_j| ≤ ρ_j`, hence `|ζ_j R_j| ≤ u_j ≤ 1/2` and `|1 + ζ_j R_j| ≥ 1 − u_j > 0`. By (I2)

    |R(Θ,γ₀)| ≤ ∏_j (1 − u_j)^{-1} = exp Σ_j −ln(1 − u_j) ≤ exp Σ_j u_j/(1 − u_j) ≤ e^{α|γ₀|/2} ≤ ρ(γ₀),

using (C_δ). Also `Z_Θ = Z_{Θ_k}(1 + ζ₀ R(Θ,γ₀))` with `|ζ₀ R| ≤ u₀ ≤ 1/2`, and `Z_{Θ_k} ≠ 0`, so
`Z_Θ ≠ 0`. As γ₀ was arbitrary, H_{n+1} holds. ∎

*(3).* Let `Δ_ℓ(γ₀)` be the supremum of `|R(Θ,γ₀) − R(Θ',γ₀)|` over finite Θ, Θ' ∋ γ₀ that agree on
`B_ℓ(γ₀)`. Claim `Δ_ℓ(γ₀) ≤ 2ρ(γ₀) e^{−δℓ}` for all integers ℓ. For ℓ < 0 this is `|R|+|R'| ≤ 2ρ`.
For ℓ ≥ 0 induct on ℓ. Let `I = N*(γ₀) ∩ (Θ ∪ Θ')`, ordered. By (I2), `R(Θ,γ₀) = ∏_{γ∈I} a_γ`
with `a_γ = (1 + ζ_γ R(Θ_γ, γ))^{-1}` if γ ∈ Θ and `a_γ = 1` otherwise; likewise `a'_γ`.
* If γ ∈ Θ ∩ Θ': any γ'' ∈ B_{ℓ−|γ|}(γ) has `D(γ₀,γ'') ≤ |γ| + D(γ,γ'') ≤ ℓ`, so Θ, Θ' agree on it, and
  membership of γ'' in Θ_γ is determined by membership in Θ (and the order); hence Θ_γ, Θ'_γ agree on
  `B_{ℓ−|γ|}(γ)` and `|a_γ − a'_γ| ≤ |ζ_γ| Δ_{ℓ−|γ|}(γ)/(1 − u_γ)²`, with `Δ ≤ 2ρ_γ e^{−δ(ℓ−|γ|)}` by the
  induction hypothesis (since |γ| ≥ 1) or the trivial bound.
* If γ lies in exactly one of Θ, Θ': then γ ∉ B_ℓ(γ₀); as `D(γ₀,γ) ≤ |γ|` this forces |γ| > ℓ, and
  `|a_γ − 1| ≤ u_γ/(1 − u_γ) ≤ 2u_γ e^{δ(|γ|−ℓ)}/(1 − u_γ)`.
Use `|∏a − ∏a'| ≤ Σ_i |a_i − a'_i| ∏_{j≠i} max(|a_j|,|a'_j|)` and `|a_j|,|a'_j| ≤ (1 − u_j)^{-1}`; with
`r = ∏_{j∈I}(1 − u_j)^{-1} ≤ e^{y}`, `y = α|γ₀|/2`, we get

    Δ_ℓ(γ₀) ≤ 2 e^{−δℓ} r Σ_{j∈I} u_j e^{δ|γ_j|}/(1 − u_j) ≤ 2 e^{−δℓ} e^{y} y ≤ 2 e^{−δℓ} e^{2y} = 2ρ(γ₀)e^{−δℓ},

by (C_δ) and `y ≤ e^y`. ∎

*Remark.* (C_δ) implies the Kotecký–Preiss condition `Σ_{γ'≁γ} |ζ(γ')| e^{(α+δ)|γ'|} ≤ α|γ|` (the extra
term γ' = γ is ≤ X⁶ ≪ α|γ|/2), so the cited corollary B1 applies with the same α, δ.

## Application to SU(2) Wilson theory

**Lemma 1 (polymer representation).** `Z = Σ_{compatible families} ∏ ζ(γ)`, polymers γ = link-connected
plaquette sets, `ζ(γ) = ∫ ∏_{p∈γ} g(U_p) dU`, `|γ|` = number of plaquettes, compatible iff link-disjoint.
*Proof.* Expand `∏_p (1+g_p) = Σ_S ∏_{p∈S} g_p`. Split S into link-connected components; components share
no link, so the Haar integral factorises. Conversely a family of pairwise link-disjoint polymers is a set S
whose components are exactly those polymers. ∎

**Lemma 2 (vanishing).** If some link lies in exactly one plaquette of γ then `ζ(γ) = 0`.
*Proof.* Integrate that link first: only one factor depends on it and `∫ g(U_l W) dU_l = ∫ g dU = 0`. ∎

**Lemma 3 (animal bound).** In a graph of maximum degree D the number `N_n` of connected n-vertex sets
containing a fixed vertex satisfies `N_n ≤ (1/n) C(Dn, n−1) ≤ (eD)^{n−1}`.
*Proof.* Number the neighbours of each vertex 1..D. For connected S ∋ root take a canonical spanning tree
(BFS from the root, ties broken by neighbour number) and record the neighbour index used on each tree edge.
This embeds S into a rooted tree in which every node has D labelled child slots; S is recovered by walking
the labels from the root, so the map is injective. The number of such n-node trees is the Fuss–Catalan number
`C(Dn,n)/((D−1)n+1) = (1/n)C(Dn,n−1)`. With `C(N,k) ≤ (eN/k)^k`, N=Dn, k=n−1:
`≤ (1/n)(eD)^{n−1}(1+1/(n−1))^{n−1} ≤ (e/n)(eD)^{n−1} ≤ (eD)^{n−1}` for n ≥ 3; n=1,2 directly. ∎

**Lemma (Finner's inequality).** On a product probability space, let `f_j ≥ 0` depend only on the coordinates in
`S_j`, and `p_j ≥ 1` with `Σ_{j: i∈S_j} 1/p_j ≤ 1` for every coordinate i. Then `∫ ∏ f_j ≤ ∏ ‖f_j‖_{p_j}`.
*Proof.* Induction on the number of coordinates. Integrate over the last coordinate n: for the j with n ∈ S_j,
Hölder with exponents p_j (padding with the constant 1) gives `∫ ∏_{j∋n} f_j dμ_n ≤ ∏_{j∋n} F_j`,
`F_j = (∫ f_j^{p_j} dμ_n)^{1/p_j}`. The F_j depend on `S_j∖{n}`, the exponent condition still holds, and
`‖F_j‖_{p_j}^{p_j} = ∫ f_j^{p_j}`; apply the induction hypothesis. ∎

*Application.* Every link lies in ≤ 6 plaquettes, so with all `p_j = 6`: `|ζ(γ)| ≤ ε^{|γ|}`, `ε := ‖g‖_{L⁶(dU)}`.

**Lemma 4 (analytic bound).** `ε ≤ ε_up(β) := β e^β 5^{1/6}/2 + (cosh β − 1)/4`.
*Proof.* `a ≥ 1` (all terms of `a = Σ_k β^{2k} E q^{2k}/(2k)!` are ≥ 0, k=0 term is 1), so
`|g| ≤ |e^{βq} − 1| + (a − 1)`. Minkowski and `|e^y − 1| ≤ |y|e^{|y|}`, `|q| ≤ 1` give
`‖g‖₆ ≤ β e^β ‖q‖₆ + (a−1)`. `E q⁶ = Cat(3)/2⁶ = 5/64` so `‖q‖₆ = 5^{1/6}/2`, and `E q^{2k} ≤ E q² = 1/4`
gives `a − 1 ≤ (cosh β − 1)/4`. ∎

**Lemma 5 (computer-assisted).** Let `C_n` be the number of link-connected plaquette sets of size n containing
a fixed plaquette in which every link lies in ≥ 2 plaquettes. Then `C_n = 0` for n < 6, `C_6 = 4` (the four
cubes), `C_7 = 0`. Exhaustive search with deficiency pruning (`finner_kp.py: covered_twice_counts(7)`, re-run
by `rigorous_check.py`); the same for every plaquette by hypercubic symmetry.

**Theorem B (proved + computer-assisted).** For all `β ≤ 0.0167` the polymer gas of Lemma 1 satisfies (C_δ)
with `α = 0.099749`, `s = α + δ = 0.106`, i.e. `δ = 0.006251 > 0` (uniformly in the box). Hence Theorem A
applies: ratio bounds `|R(Θ,γ)| ≤ e^{α|γ|}` and environment decay hold uniformly in the volume.
Certified values of the best δ: 2.146 (β=0.002), 1.226 (0.005), 0.527 (0.01), 0.0063 (0.0167).
*Proof.* By Lemma 2 only polymers counted by `C_n` matter; by Lemmas 3, 5, and Finner, with
`X = ε_up e^{α+δ}`, `G = 20e`, for γ₀ and each plaquette p ∈ γ₀ (the polymers in `N*(γ₀)` contain a plaquette
from the 21-element closed neighbourhood of some p ∈ γ₀):

    Σ_{γ'∈N*(γ₀)} u e^{δ|γ'|}/(1−u) ≤ |γ₀| · 21 · [ 4X⁶ + G⁷X⁸/(1 − GX) ] / (1 − X⁶),

since `u(γ') e^{δ|γ'|} ≤ X^{|γ'|}` and `u ≤ X⁶`. This is ≤ α|γ₀|/2 iff
`42 [4X⁶ + G⁷X⁸/(1−GX)]/(1−X⁶) ≤ α`, which `rigorous_check.py` certifies in interval arithmetic; it is
monotone in β (ε_up increases with β), so it covers every β ≤ 0.0167. ∎

## Consequences (with the cited black boxes)

* **Proved (Theorems A, B):** uniform-in-volume bounds on the polymer ratios and exponential decay of their
  dependence on distant polymers. E.g. the probability that a given polymer occurs in the (signed) gas on any
  finite Θ is at most `u/(1−u)`.
* **Cited, not proved here (B1):** (C_δ) ⇒ the Kotecký–Preiss condition ⇒ (standard corollary) absolutely
  convergent cluster expansion and decay at rate ≥ δ of connected correlations of local gauge-invariant
  observables. Passing from the ratio bounds above to observables needs expanding the observables into the
  polymer gas and comparing environments with Theorem A(3); I did not write that argument out.
* **Cited (B2):** Wilson action reflection positivity (Osterwalder–Seiler) and OS reconstruction: such
  exponential clustering gives a transfer-matrix gap ≥ δ(β) in lattice units.

## Appendix: exact weights (not needed above)

For a closed plaquette surface with every link in exactly two plaquettes and a coherent orientation,
`∫ ∏ Tr U_p dU = 2^{C−E}` (Schur orthogonality, proof in `proof/exact_weights.py`). For the 1×1×t box this is
`2^{−4t}`, which is why the leading strong-coupling decay rate is ≈ 4 ln(4/β) — a heuristic, because control
of corrections from larger surfaces is not proved.

## What remains open

The continuum limit, infinite-volume OS reconstruction in 4D at weak coupling, and the mass gap of the
continuum theory. Nothing here approaches them: β ≤ 0.0167 is the deep strong-coupling end; the continuum
limit is β → ∞.

# Strong-coupling clustering for 4D SU(2) lattice gauge theory: statement and proof

**Scope.** This is the classical strong-coupling regime (Osterwalder–Seiler 1978) at a
*fixed* lattice spacing. It says nothing about the continuum limit (β → ∞) and does not
address the Clay Millennium problem. Its value is that every step is written out, with the
cited parts isolated.

## Setting

Wilson action on Z⁴, gauge group SU(2), Haar measure `dU` (probability). With
`q = ½ Tr U ∈ [-1,1]` put

    f(U) = e^{β q} / a(β),   a(β) = ∫ e^{β q} dU,   g = f − 1,   ∫ g dU = 0.

`Z = ∫ ∏_p f(U_p) dU` (any finite box). Plaquette graph: plaquettes adjacent iff they share a
link; every plaquette has exactly **D = 20** neighbours, every link lies in exactly **6**
plaquettes.

## Theorem

Let `β ≤ β* = 0.0178`. With `G = 20e`, `ε = ε_up(β)` (Lemma 4), `x = ε e^s`, the inequality

    21 · [ 4 x⁶ + G⁷ x⁸ / (1 − G x) ]  ≤  α,        s = α + δ

holds with `s = 0.104, α = 0.095422`, i.e. **δ ≥ 0.008578 > 0**, uniformly in the box
(certified by `proof/rigorous_check.py`, interval arithmetic). Consequently, assuming
black boxes **B1** and **B2** below: log Z has an absolutely convergent cluster expansion
uniformly in the volume, connected correlations of local gauge-invariant observables decay
exponentially at rate ≥ δ(β) per unit Euclidean time, and the transfer matrix has spectral gap
≥ δ(β) in lattice units. Certified values: δ ≥ 2.21 (β=0.002), 1.29 (0.005), 0.59 (0.01), 0.0086 (0.0178).

## Black boxes (cited, NOT proved here)

* **B1 (Kotecký–Preiss 1986 + standard corollaries).** For a polymer gas with hard-core
  compatibility, if `Σ_{γ'≁γ} |ζ(γ')| e^{(α+δ)|γ'|} ≤ α|γ|` for all γ, then the cluster
  expansion of log Z converges absolutely, uniformly in the volume, and truncated correlation
  functions of local observables decay like `e^{−δ·(size of a connecting polymer)}`.
* **B2 (Osterwalder–Seiler; OS reconstruction).** The Wilson action is reflection positive;
  exponential decay at rate δ of connected correlations of all local gauge-invariant
  observables gives a transfer-matrix gap ≥ δ on the orthocomplement of the vacuum. A
  link-connected chain of plaquettes joining times 0 and t has ≥ t plaquettes.

## Proofs

**Lemma 1 (polymer representation).** `Z = Σ_{compatible families} ∏ ζ(γ)`, polymers γ =
link-connected plaquette sets, `ζ(γ) = ∫ ∏_{p∈γ} g(U_p) dU`, compatible iff link-disjoint.
*Proof.* Expand `∏_p (1+g_p) = Σ_S ∏_{p∈S} g_p`. Split S into link-connected components; distinct
components share no link, so the Haar integral factorises over them. Conversely a family of
pairwise link-disjoint polymers is a set S whose components are exactly those polymers. ∎

**Lemma 2 (vanishing).** If some link lies in exactly one plaquette of γ then `ζ(γ)=0`.
*Proof.* Integrate that link first; only one factor `g(U_p)` depends on it, and by left
invariance `∫ g(U_l W) dU_l = ∫ g dU = 0`. ∎
So only polymers in which every link is covered ≥ 2 times matter.

**Lemma 3 (animal bound).** In a graph of maximum degree D, the number `N_n` of connected
n-vertex sets containing a fixed vertex satisfies `N_n ≤ (1/n) C(Dn, n−1) ≤ (eD)^{n−1}`.
*Proof.* Number the neighbours of each vertex 1..D. For connected S ∋ root choose a canonical
spanning tree (BFS from the root, ties broken by neighbour number) and record, for each tree
edge, the neighbour index used. This embeds S into a rooted tree in which every node has D
labelled child slots; S is recovered by walking the labels from the root, so the map is
injective. The number of such n-node trees is the Fuss–Catalan number
`C(Dn,n)/((D−1)n+1) = (1/n)C(Dn,n−1)`. Using `C(N,k) ≤ (eN/k)^k` with N=Dn, k=n−1:
`≤ (1/n)(eDn/(n−1))^{n−1} = (1/n)(eD)^{n−1}(1+1/(n−1))^{n−1} ≤ (e/n)(eD)^{n−1} ≤ (eD)^{n−1}`
for n ≥ 3; n=1,2 are checked directly (1 and ≤ D). ∎

**Lemma (Finner's inequality).** On a product probability space `Ω = ∏_{i} Ω_i`, let `f_j ≥ 0`
depend only on the coordinates in `S_j`, and `p_j ≥ 1` with `Σ_{j: i∈S_j} 1/p_j ≤ 1` for every i.
Then `∫ ∏_j f_j ≤ ∏_j ‖f_j‖_{p_j}`.
*Proof.* Induction on the number n of coordinates; n=0 is trivial. Integrate over the last
coordinate. For the j with n∈S_j, Hölder with exponents p_j (padding with the constant 1 since
`Σ 1/p_j ≤ 1`) gives `∫ ∏_{j∋n} f_j dμ_n ≤ ∏_{j∋n} F_j`, `F_j = (∫ f_j^{p_j} dμ_n)^{1/p_j}`.
The F_j depend on `S_j∖{n}`, the other f_j are unchanged, and the exponent condition still holds
on the remaining coordinates. Apply the induction hypothesis and note
`‖F_j‖_{p_j}^{p_j} = ∫ f_j^{p_j}`. ∎

*Application.* Every link lies in ≤ 6 plaquettes of any γ, so with all `p_j = 6` the condition
holds; hence `|ζ(γ)| ≤ ∫ ∏ |g(U_p)| ≤ ε^{|γ|}`, `ε := ‖g‖_{L⁶(dU)}`.

**Lemma 4 (analytic bound on ε).** `ε ≤ ε_up(β) := β e^β 5^{1/6}/2 + (cosh β − 1)/4`.
*Proof.* `a ≥ 1` (all terms of `a = Σ_k β^{2k} E q^{2k}/(2k)!` are ≥ 0 and the k=0 term is 1).
So `|g| = |e^{βq} − a|/a ≤ |e^{βq} − 1| + (a−1)`. By Minkowski, and `|e^y − 1| ≤ |y| e^{|y|}`
with `|q| ≤ 1`: `‖g‖₆ ≤ β e^β ‖q‖₆ + (a−1)`. Here `E q⁶ = Cat(3)/2⁶ = 5/64`, so
`‖q‖₆ = 5^{1/6}/2`, and since `E q^{2k} ≤ E q² = 1/4`, `a − 1 ≤ (cosh β − 1)/4`. ∎

**Lemma 5 (computer-assisted counts).** Let `C_n` be the number of link-connected plaquette sets
of size n containing a fixed plaquette in which every link lies in ≥ 2 plaquettes. Then
`C_n = 0` for n < 6, `C_6 = 4` (the four cubes through the plaquette), `C_7 = 0`.
*Proof.* Exhaustive search with deficiency pruning (`proof/finner_kp.py`, `covered_twice_counts(7)`),
re-run by `proof/rigorous_check.py`. By hypercubic symmetry the count is the same for every
plaquette. This is a finite computation, not a hand proof. ∎

**Proof of the Theorem.** A polymer is incompatible with γ iff it shares a link with γ, i.e.
contains a plaquette of the closed neighbourhood (21 plaquettes) of some `p ∈ γ`. By Lemma 2
only polymers counted by `C_n` matter; by Lemmas 3, 5 and the Finner bound,

    Σ_{γ'≁γ} |ζ(γ')| e^{(α+δ)|γ'|} ≤ |γ| · 21 · [ 4x⁶ + 0·x⁷ + Σ_{n≥8} G^{n−1} x^n ],

with `x = ε e^{α+δ}` and `G x < 1`; the geometric tail is `G⁷x⁸/(1−Gx)`. The right side is
≤ α|γ| by the interval-arithmetic certificate, which is monotone in β (ε_up increases with β,
the bracket increases with x), so it covers every β ≤ β*. B1 and B2 give the consequences. ∎

## Appendix: exact weights (not needed for the Theorem)

For a closed plaquette surface with every link in exactly two plaquettes and a coherent
orientation, `∫ ∏ Tr U_p dU = 2^{C−E}` (Schur orthogonality, proof in `proof/exact_weights.py`).
For the 1×1×t box this is `2^{−4t}`, which is why the leading strong-coupling decay rate is
≈ 4 ln(4/β) — a heuristic, because control of corrections from larger surfaces is not proved.

## What remains open

The continuum limit, infinite-volume OS reconstruction in 4D at weak coupling, and the mass
gap of the continuum theory. Nothing here approaches them: the region β ≤ 0.0178 is the deep
strong-coupling end, the continuum limit is β → ∞.

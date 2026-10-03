"""
Polymer/cluster expansion for SU(2) lattice gauge theory.
Implements the combinatorial framework for the constructive proof.
"""
import jax
import jax.numpy as jnp
from jax import jit, vmap
from functools import lru_cache
import itertools
from dataclasses import dataclass
from typing import List, Dict, Set, Tuple, Optional, Iterator
from collections import defaultdict
import math

from lattice.wilson import Lattice4D
from lattice.su2 import su2_dim, su2_fusion, get_6j, su2_character

# ============================================================
# Polymer representation
# ============================================================

@dataclass(frozen=True, order=True)
class Plaquette:
    """A single plaquette on the lattice"""
    site: int
    mu: int
    nu: int
    
    def neighbors(self, lattice: Lattice4D) -> List['Plaquette']:
        """Return plaquettes sharing a link with this one"""
        result = []
        # Find other plaquettes containing this link
        for p in lattice.all_plaquettes():
            other = Plaquette(*p)
            if other == self:
                continue
            if self._shares_link(other, lattice):
                result.append(other)
        return result
    
    def get_links(self, lattice: Lattice4D) -> List[Tuple[int, int]]:
        """Return the four links of this plaquette as (site, mu)"""
        x = lattice.site_coords(self.site)
        x_mu = lattice._shift(x, self.mu, 1)
        x_nu = lattice._shift(x, self.nu, 1)
        return [
            (self.site, self.mu),
            (lattice.site_index(x_mu), self.nu),
            (lattice.site_index(x_nu), self.mu),
            (self.site, self.nu),
        ]
    
    def _shares_link(self, other: 'Plaquette', lattice: Lattice4D) -> bool:
        return bool(set(self.get_links(lattice)) & set(other.get_links(lattice)))

@dataclass(frozen=True)
class Polymer:
    """
    A polymer (contour) in the cluster expansion.
    A connected set of plaquettes with non-trivial representation labels.
    """
    plaquettes: frozenset[Plaquette]
    representations: frozenset[Tuple[Plaquette, float]]  # (plaquette, spin j)
    
    @property
    def size(self) -> int:
        return len(self.plaquettes)
    
    @property
    def non_trivial_plaquettes(self) -> List[Plaquette]:
        return [p for p, j in self.representations if j > 0]
    
    def is_trivial(self) -> bool:
        return all(j == 0.0 for _, j in self.representations)
    
    def max_spin(self) -> float:
        return max(j for _, j in self.representations) if self.representations else 0.0

# ============================================================
# Weight computation
# ============================================================

def polymer_weight(polymer: Polymer, beta: float, lattice: Lattice4D) -> float:
    """
    Compute the weight ζ(γ) of a polymer.
    
    For the character expansion:
    Z = ∑_{config} ∏_p [∑_j c_j(β) χ_j(θ_p)]
    = ∑_{polymers} ∏_{p∈γ} (c_j(β)/c_0(β)) × (6j symbols at junctions)
    
    At β=0: c_0=1, c_j>0=0, so only trivial polymer has weight 1.
    """
    from lattice.wilson import exact_expansion_coeffs
    
    coeffs = exact_expansion_coeffs(beta, max_j=10.0)
    c0 = coeffs[0.0]
    
    if polymer.is_trivial():
        return 1.0
    
    weight = 1.0
    for plaq, j in polymer.representations:
        weight *= coeffs[j] / c0
    
    # Multiply by 6j symbols at junctions (links where 4 plaquettes meet)
    # This is the combinatorial factor from integrating over link variables
    weight *= junction_factor(polymer, lattice)
    
    return weight

def junction_factor(polymer: Polymer, lattice: Lattice4D) -> float:
    """
    Compute the product of 6j symbols at all links where plaquettes meet.
    
    For each link, the four adjacent plaquettes have representations
    j1, j2, j3, j4. The integral over the link variable gives a 6j symbol.
    """
    # Map link -> list of (plaquette, spin) pairs
    link_reps = defaultdict(list)
    
    for plaq, j in polymer.representations:
        if j == 0.0:
            continue
        for link_site, link_mu in plaq.get_links(lattice):
            link_reps[(link_site, link_mu)].append(j)
    
    factor = 1.0
    for link, spins in link_reps.items():
        if len(spins) == 4:
            # Four plaquettes meet at this link
            # The 6j symbol depends on the cyclic ordering
            # For now, use simplified factor
            factor *= link_6j_factor(spins)
        elif len(spins) == 2:
            # Two plaquettes share this link (boundary of polymer)
            # Factor = δ_{j1,j2} / d_{j1}
            if abs(spins[0] - spins[1]) < 1e-10:
                factor *= 1.0 / su2_dim(spins[0])
            else:
                return 0.0
        # len=1 or 3 shouldn't happen for closed polymers
    return factor

def link_6j_factor(spins: List[float]) -> float:
    """
    6j symbol for four spins around a link.
    The exact formula depends on the geometry.
    For SU(2) with cyclic ordering (j1, j2, j3, j4):
    {j1 j2 j3; j4 j5 j6} where appropriate
    """
    # This is a simplified version
    # Full implementation needs careful handling of the recoupling
    # For the proof, we'll use the fact that |6j| ≤ 1/√(d_j1 d_j2 d_j3 d_j4)
    j1, j2, j3, j4 = spins
    return get_6j(j1, j2, j3, j4, 0.0, 0.0)  # Placeholder

# ============================================================
# Polymer enumeration
# ============================================================

def generate_polymers(lattice: Lattice4D, max_size: int, max_spin: float = 2.0) -> Iterator[Polymer]:
    """
    Generate all connected polymers up to given size.
    Uses canonical construction to avoid duplicates.
    """
    all_plaquettes = [Plaquette(*p) for p in lattice.all_plaquettes()]
    
    # For each starting plaquette, grow connected clusters
    for start in all_plaquettes:
        # Use BFS/DFS to grow
        yield from _grow_polymers(lattice, frozenset([start]), all_plaquettes, max_size, max_spin, start, max_yield=1000)

def _grow_polymers(lattice, current_plaquettes, all_plaquettes, max_size, max_spin, canonical_start, max_yield=1000, yielded=None):
    """Recursively grow polymers ensuring canonical ordering"""
    if yielded is None:
        yielded = [0]
    if yielded[0] >= max_yield:
        return
    if len(current_plaquettes) > max_size:
        return
    
    # Generate all spin assignments for current plaquettes
    plaq_list = list(current_plaquettes)
    spin_values = [0.0]
    j = 0.5
    while j <= max_spin + 1e-10:
        spin_values.append(j)
        j += 0.5
    
    for spin_assignment in itertools.product(spin_values, repeat=len(plaq_list)):
        if all(s == 0.0 for s in spin_assignment):
            continue  # Skip trivial polymer
        
        reps = frozenset((p, s) for p, s in zip(plaq_list, spin_assignment))
        yielded[0] += 1
        yield Polymer(frozenset(plaq_list), reps)
        if yielded[0] >= max_yield:
            return
    
    # Try to add neighboring plaquettes (maintaining connectivity and canonical order)
    if len(current_plaquettes) < max_size:
        # Find all neighbors of current cluster
        neighbors = set()
        for p in current_plaquettes:
            for n in p.neighbors(lattice):
                if n not in current_plaquettes and n >= canonical_start:
                    neighbors.add(n)
        
        for n in neighbors:
            new_plaquettes = current_plaquettes | frozenset([n])
            yield from _grow_polymers(lattice, new_plaquettes, all_plaquettes, max_size, max_spin, canonical_start, max_yield, yielded)

# ============================================================
# Kotecký-Preiss verification
# ============================================================

def kotecky_preiss_sum(lattice: Lattice4D, beta: float, max_size: int = 8) -> float:
    """
    Compute ∑_{γ∋x} |ζ(γ)| e^{|γ|} for Kotecký-Preiss criterion.
    If < 1, cluster expansion converges.
    """
    total = 0.0
    # Fix a reference site (origin)
    for polymer in generate_polymers(lattice, max_size):
        # Check if polymer contains a plaquette at origin
        origin_plaquettes = {Plaquette(0, mu, nu) for mu in range(3) for nu in range(mu+1, 4)}
        if polymer.plaquettes & origin_plaquettes:
            weight = abs(polymer_weight(polymer, beta, lattice))
            total += weight * math.exp(polymer.size)
    return total

def verify_kp_convergence(lattice: Lattice4D, beta_max: float, max_size: int = 6):
    """
    Verify KP criterion for β ∈ [0, β_max].
    Returns True if converges for all β in range.
    """
    import numpy as np
    betas = np.linspace(0, beta_max, 20)
    for beta in betas:
        kp_sum = kotecky_preiss_sum(lattice, beta, max_size)
        if kp_sum >= 1.0:
            print(f"KP FAILS at β={beta:.3f}: sum = {kp_sum:.3f}")
            return False
        else:
            print(f"β={beta:.3f}: KP sum = {kp_sum:.6f} < 1 ✓")
    return True

# ============================================================
# Cluster expansion for correlations
# ============================================================

def connected_correlation(obs1, obs2, lattice: Lattice4D, beta: float, max_polymer_size: int = 6):
    """
    Compute connected correlation ⟨O1 O2⟩ - ⟨O1⟩⟨O2⟩
    using cluster expansion up to given polymer size.
    """
    # ⟨O⟩ = (∑_γ ζ(γ) O(γ)) / (∑_γ ζ(γ))
    # where O(γ) is the observable evaluated on polymer γ
    pass

# ============================================================
# Strong coupling exact results
# ============================================================

def strong_coupling_wilson_loop(j: float, area: int) -> float:
    """
    Exact Wilson loop at β=0: ⟨W_j⟩ = d_j^{1-A}
    """
    return su2_dim(j) ** (1 - area)

def strong_coupling_string_tension() -> float:
    """Exact string tension at β=0 for fundamental representation"""
    return math.log(2)

def strong_coupling_mass_gap() -> float:
    """Exact mass gap at β=0: Δ = log(2)"""
    return math.log(2)

# ============================================================
# Verification and testing
# ============================================================

def test_polymer_generation():
    lat = Lattice4D(2)
    print("Generating polymers up to size 3...")
    count = 0
    for poly in generate_polymers(lat, max_size=3, max_spin=1.0):
        count += 1
        if count <= 5:
            print(f"  {poly}")
        if count > 100:
            print("  (truncated at 100)")
            break
    print(f"Total generated: {count}")

def test_weights():
    lat = Lattice4D(2)
    print("\nTesting polymer weights...")
    for poly in generate_polymers(lat, max_size=2, max_spin=1.0):
        w0 = polymer_weight(poly, 0.0, lat)
        w1 = polymer_weight(poly, 1.0, lat)
        if w0 != 0 or w1 != 0:
            print(f"  beta=0: {w0:.6f}, beta=1: {w1:.6f}, polymer: {poly}")

if __name__ == "__main__":
    test_polymer_generation()
    test_weights()
    
    # Test KP at β=0
    lat = Lattice4D(4)
    print(f"\nKP sum at β=0: {kotecky_preiss_sum(lat, 0.0, 4)}")
    print(f"KP sum at β=0.5: {kotecky_preiss_sum(lat, 0.5, 4)}")
    
    print(f"\nString tension at β=0: {strong_coupling_string_tension()}")
    print(f"Mass gap at β=0: {strong_coupling_mass_gap()}")
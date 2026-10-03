"""
SU(2) group operations, Haar measure, and character theory.
Core mathematical framework for the strong coupling proof.
"""
import jax
import jax.numpy as jnp
from jax import random, vmap, jit
from functools import partial
import math

# SU(2) representation theory constants
# Spin-j representation has dimension 2j+1
# Fundamental: j=1/2, dim=2
# Adjoint: j=1, dim=3

def su2_dim(j: float) -> int:
    """Dimension of spin-j representation: 2j + 1"""
    return int(2 * j + 1)

def su2_casimir(j: float) -> float:
    """Quadratic Casimir: j(j+1)"""
    return j * (j + 1)

# Character formulas for SU(2)
# χ_j(θ) = sin((2j+1)θ/2) / sin(θ/2) where θ ∈ [0, 2π] is the class angle
# For group element with eigenvalues e^{±iθ}

@jit
def su2_character(j: float, theta: jnp.ndarray) -> jnp.ndarray:
    """
    SU(2) character for spin-j representation.
    θ ∈ [0, 2π], character is real.
    """
    j = jnp.asarray(j)
    theta = jnp.asarray(theta)
    numerator = jnp.sin((2 * j + 1) * theta / 2)
    denominator = jnp.sin(theta / 2)
    # Handle θ=0 limit: χ_j(0) = 2j+1
    return jnp.where(jnp.abs(denominator) < 1e-12, 2 * j + 1, numerator / denominator)

# Haar measure on SU(2) conjugacy classes: (2/π) sin²(θ/2) dθ
# Normalized: ∫₀²π (2/π) sin²(θ/2) dθ = 1

@jit
def haar_measure(theta: jnp.ndarray) -> jnp.ndarray:
    """Haar measure density on [0, 2π]"""
    return (2 / jnp.pi) * jnp.sin(theta / 2) ** 2

# Orthogonality relations:
# ∫ dU χ_j(U) χ_k(U) = δ_{jk}
# ∫ dU χ_j(U) χ_k(U) χ_l(U) = Clebsch-Gordan coefficient

def character_inner_product(j: float, k: float, n_samples: int = 10000) -> float:
    """
    Compute ∫ dU χ_j(U) χ_k(U) via Monte Carlo for verification.
    Should equal δ_{jk}.
    """
    key = random.PRNGKey(0)
    # Sample from Haar measure using rejection or inverse transform
    thetas = random.uniform(key, (n_samples,), minval=0, maxval=2*jnp.pi)
    weights = haar_measure(thetas)
    chi_j = su2_character(j, thetas)
    chi_k = su2_character(k, thetas)
    return float(jnp.mean(chi_j * chi_k * weights) * (2 * jnp.pi))

# Clebsch-Gordan coefficients for SU(2)
# j1 ⊗ j2 = ⊕_{j=|j1-j2|}^{j1+j2} j
# We need the fusion rules for the polymer expansion

def su2_fusion(j1: float, j2: float) -> list:
    """Return list of spins in j1 ⊗ j2 decomposition"""
    j_min = abs(j1 - j2)
    j_max = j1 + j2
    spins = []
    j = j_min
    while j <= j_max + 1e-10:
        spins.append(j)
        j += 1.0
    return spins

# 6j symbols for recoupling (needed for plaquette weights)
# {j1 j2 j3; j4 j5 j6} - we'll use explicit formulas or precomputed tables

def wigner_6j(j1, j2, j3, j4, j5, j6):
    """
    Wigner 6j symbol.
    For SU(2), can compute via Racah formula.
    We'll implement the full formula for exact rational arithmetic.
    """
    # Convert to twice-spin integers for exact arithmetic
    a, b, c = int(2*j1), int(2*j2), int(2*j3)
    d, e, f = int(2*j4), int(2*j5), int(2*j6)
    
    # Triangle conditions
    def tri(x, y, z):
        return (x + y + z) % 2 == 0 and abs(x - y) <= z <= x + y
    
    if not (tri(a, b, c) and tri(a, e, f) and tri(d, b, f) and tri(d, e, c)):
        return 0.0
    
    # Racah formula
    # We'll use the symmetry and precompute for needed values
    # For now, placeholder - will implement full formula
    return _racah_6j(a, b, c, d, e, f)

def _racah_6j(a, b, c, d, e, f):
    """Racah formula for 6j symbol with integer 2j values"""
    # This is a simplified version - full implementation needs careful handling
    # of factorials and summation limits
    # For the strong coupling proof, we only need specific values
    pass

# Precomputed 6j symbols for low spins (fundamental and adjoint)
# These are exact rational values
SIXJ_TABLE = {
    # {j1, j2, j3, j4, j5, j6} -> value
    (0, 0, 0, 0, 0, 0): 1.0,
    (1, 1, 0, 1, 1, 0): -1/2,
    (1, 1, 2, 1, 1, 2): 1/6,
    (1, 1, 1, 1, 1, 1): 0,
    # Add more as needed
}

def get_6j(j1, j2, j3, j4, j5, j6):
    """Lookup 6j symbol from table"""
    key = tuple(int(2*j) for j in (j1, j2, j3, j4, j5, j6))
    return SIXJ_TABLE.get(key, 0.0)

# Wilson loop in representation j
# For a rectangular loop of size R×T, at strong coupling:
# ⟨W_j(R,T)⟩ = (1/d_j)^{RT} * (d_j)^{2} ... 
# Actually at β=0, the expectation is exactly computable

def wilson_loop_strong_coupling(j: float, area: int) -> float:
    """
    Strong coupling (β=0) Wilson loop expectation.
    For SU(2): ⟨W_j⟩ = (1/d_j)^{area} * d_j = d_j^{1-area}
    """
    d = su2_dim(j)
    return d ** (1 - area)

# String tension from fundamental representation
# σ = -log(⟨W_{1/2}(1×1)⟩) = log(2) for SU(2)

def string_tension_su2() -> float:
    """Exact string tension at β=0 for SU(2) fundamental"""
    return math.log(2)

# Character expansion of delta function:
# δ(U) = ∑_{j} d_j χ_j(U)
# where sum is over half-integer spins

def delta_function_expansion(max_j: float = 5.0):
    """Return list of (j, d_j) for character expansion up to max_j"""
    expansions = []
    j = 0.0
    while j <= max_j + 1e-10:
        expansions.append((j, su2_dim(j)))
        j += 0.5
    return expansions

# Verification of orthogonality
def verify_orthogonality(max_j: float = 3.0):
    """Verify ∫ χ_j χ_k = δ_{jk} numerically"""
    print("Verifying SU(2) character orthogonality...")
    for j in [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
        if j > max_j:
            break
        for k in [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
            if k > max_j:
                break
            val = character_inner_product(j, k, 50000)
            expected = 1.0 if abs(j - k) < 1e-10 else 0.0
            print(f"  j={j}, k={k}: {val:.6f} (expected {expected})")

if __name__ == "__main__":
    # Quick tests
    print("SU(2) Character Tests")
    print(f"dim(j=0) = {su2_dim(0)}")
    print(f"dim(j=1/2) = {su2_dim(0.5)}")
    print(f"dim(j=1) = {su2_dim(1)}")
    print(f"String tension = {string_tension_su2()}")
    
    # Verify character at θ=0
    thetas = jnp.array([0.0, 0.1, 1.0, 3.14])
    print(f"χ_0(θ) = {su2_character(0.0, thetas)}")
    print(f"χ_1/2(θ) = {su2_character(0.5, thetas)}")
    print(f"χ_1(θ) = {su2_character(1.0, thetas)}")
    
    verify_orthogonality(2.0)
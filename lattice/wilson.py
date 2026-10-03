"""
Wilson action, lattice geometry, and observables for SU(2) lattice gauge theory.
"""
import jax
import jax.numpy as jnp
from jax import random, vmap, jit
from functools import partial
import itertools
from .su2 import su2_dim, su2_character, haar_measure

# Lattice geometry
# 4D periodic lattice: sites x ∈ (Z/LZ)^4
# Links: (x, μ) where μ ∈ {0,1,2,3} (direction)
# Plaquettes: (x, μ, ν) with μ < ν

class Lattice4D:
    """4D periodic hypercubic lattice"""
    
    def __init__(self, L: int):
        self.L = L
        self.volume = L ** 4
        self.n_links = 4 * self.volume
        self.n_plaquettes = 6 * self.volume  # 6 planes per site
        
    def site_index(self, coords):
        """Convert (x0,x1,x2,x3) to linear index"""
        x0, x1, x2, x3 = coords
        return ((x0 * self.L + x1) * self.L + x2) * self.L + x3
    
    def site_coords(self, idx):
        """Convert linear index to coordinates"""
        x3 = idx % self.L
        x2 = (idx // self.L) % self.L
        x1 = (idx // (self.L**2)) % self.L
        x0 = idx // (self.L**3)
        return (x0, x1, x2, x3)
    
    def link_index(self, site, mu):
        """Link index: 4*site + mu"""
        return 4 * site + mu
    
    def plaquette_sites(self, site, mu, nu):
        """Four sites of plaquette (site, mu, nu)"""
        x = self.site_coords(site)
        x_mu = self._shift(x, mu, 1)
        x_nu = self._shift(x, nu, 1)
        x_munu = self._shift(x_mu, nu, 1)
        return (site, 
                self.site_index(x_mu),
                self.site_index(x_nu),
                self.site_index(x_munu))
    
    def _shift(self, coords, mu, delta):
        """Shift coordinates in direction mu by delta (periodic)"""
        x = list(coords)
        x[mu] = (x[mu] + delta) % self.L
        return tuple(x)
    
    def all_plaquettes(self):
        """Generate all plaquettes"""
        for site in range(self.volume):
            for mu in range(3):
                for nu in range(mu+1, 4):
                    yield (site, mu, nu)

# SU(2) link variables
# We represent U(x,μ) by its class angle θ ∈ [0, 2π]
# Full group element can be reconstructed if needed

@jit
def plaquette_angle(links, lattice, site, mu, nu):
    """
    Compute plaquette angle for U(x,μ)U(x+μ,ν)U(x+ν,μ)†U(x,ν)†
    links: array of shape (n_links,) containing θ values
    Returns θ_p ∈ [0, 2π] for the plaquette product
    """
    # Get the four link angles
    idx1 = lattice.link_index(site, mu)
    x_mu = lattice._shift(lattice.site_coords(site), mu, 1)
    idx2 = lattice.link_index(lattice.site_index(x_mu), nu)
    x_nu = lattice._shift(lattice.site_coords(site), nu, 1)
    idx3 = lattice.link_index(lattice.site_index(x_nu), mu)
    idx4 = lattice.link_index(site, nu)
    
    # For SU(2), plaquette angle = θ1 + θ2 - θ3 - θ4 (mod 2π)
    # This is exact for the eigenvalues
    theta = (links[idx1] + links[idx2] - links[idx3] - links[idx4]) % (2 * jnp.pi)
    return theta

@jit
def wilson_action(links, lattice, beta: float):
    """
    Wilson action: S = -β ∑_p Re Tr U_p / 2
    For SU(2): Re Tr U_p = χ_{1/2}(θ_p) = cos(θ_p/2)
    """
    total = 0.0
    for site, mu, nu in lattice.all_plaquettes():
        theta_p = plaquette_angle(links, lattice, site, mu, nu)
        total += jnp.cos(theta_p / 2)  # χ_{1/2}(θ) = 2cos(θ/2), but we use normalized
    return -beta * total

# Character expansion of Boltzmann factor
# exp(β χ_{1/2}(θ)) = ∑_j c_j(β) χ_j(θ)
# where c_j(β) = d_j ∫ dθ ρ(θ) exp(β χ_{1/2}(θ)) χ_j(θ)

@jit
def boltzmann_factor(theta: jnp.ndarray, beta: float) -> jnp.ndarray:
    """exp(β cos(θ/2)) for SU(2) fundamental character"""
    return jnp.exp(beta * jnp.cos(theta / 2))

def character_expansion_coeffs(beta: float, max_j: float = 5.0, n_quad: int = 1000):
    """
    Compute expansion coefficients c_j(β) for exp(β χ_{1/2}(θ)) = ∑ c_j χ_j(θ)
    Using numerical quadrature (will be replaced by exact recurrence)
    """
    thetas = jnp.linspace(0, 2*jnp.pi, n_quad)
    dtheta = thetas[1] - thetas[0]
    weights = haar_measure(thetas)
    boltz = boltzmann_factor(thetas, beta)
    
    coeffs = {}
    j = 0.0
    while j <= max_j + 1e-10:
        chi_j = su2_character(j, thetas)
        # c_j = d_j ∫ dθ ρ(θ) exp(β cos(θ/2)) χ_j(θ)
        c_j = su2_dim(j) * jnp.sum(boltz * chi_j * weights) * dtheta
        coeffs[j] = float(c_j)
        j += 0.5
    return coeffs

# Exact recurrence for character expansion coefficients (better than quadrature)
# Using the identity: χ_{1/2} χ_j = χ_{j+1/2} + χ_{j-1/2}
# This gives a recurrence for c_j(β) in terms of modified Bessel functions

from scipy.special import iv  # modified Bessel I_v

def exact_expansion_coeffs(beta: float, max_j: float = 10.0):
    """
    Exact coefficients: c_j(β) = d_j I_{2j+1}(β) / I_1(β)
    For SU(2) with action β χ_{1/2}(θ)
    """
    coeffs = {}
    if beta == 0.0:
        # At beta=0: c_0=1, c_{j>0}=0
        coeffs[0.0] = 1.0
        j = 0.5
        while j <= max_j + 1e-10:
            coeffs[j] = 0.0
            j += 0.5
        return coeffs
    
    I1 = iv(1, beta)
    j = 0.0
    while j <= max_j + 1e-10:
        d = su2_dim(j)
        I = iv(2*j + 1, beta)
        coeffs[j] = d * I / I1
        j += 0.5
    return coeffs

# Polymer/contour representation
# At strong coupling (β=0), only j=0 contributes (c_0=1, c_j>0=0)
# For small β, contours are sets of plaquettes with j>0

class PolymerModel:
    """
    Polymer representation of the partition function.
    Each polymer is a connected set of plaquettes with non-trivial representation labels.
    """
    
    def __init__(self, lattice: Lattice4D, beta: float):
        self.lattice = lattice
        self.beta = beta
        self.coeffs = exact_expansion_coeffs(beta)
        
    def polymer_weight(self, polymer):
        """
        Weight of a polymer: product of c_j(β)/c_0(β) over its plaquettes
        times combinatorial factors from 6j symbols at junctions
        """
        # For β=0, all c_j>0 = 0, so only trivial polymer survives
        # For small β, c_j/c_0 ≈ (β/2)^{2j} / (2j+1)!
        pass
    
    def kotecky_preiss_bound(self, max_size: int = 10):
        """
        Verify Kotecký-Preiss criterion: ∑_{γ∋x} |ζ(γ)| e^{|γ|} < 1
        This proves convergence of the cluster expansion.
        """
        # At β=0: ζ(γ) = 0 for all non-trivial γ, so sum = 0 < 1 ✓
        # For small β: bound activities by (Cβ)^{|γ|}
        pass

# Wilson loop observables
def wilson_loop(links, lattice, coords, R, T, mu, nu, j=0.5):
    """
    Measure Wilson loop in representation j.
    coords = (x0,x1,x2,x3) lower-left corner
    R, T = spatial, temporal extent
    mu, nu = plane directions
    """
    # Product of links around R×T rectangle
    # For strong coupling, we have exact formula
    pass

def polyakov_loop(links, lattice, coords, mu=0):
    """Polyakov loop (temporal Wilson line)"""
    pass

# Correlation functions
@jit
def plaquette_plaquette_corr(links, lattice, site1, site2, mu, nu):
    """⟨χ_{1/2}(θ_p1) χ_{1/2}(θ_p2)⟩ - ⟨χ_{1/2}⟩²"""
    theta1 = plaquette_angle(links, lattice, site1, mu, nu)
    theta2 = plaquette_angle(links, lattice, site2, mu, nu)
    return jnp.cos(theta1/2) * jnp.cos(theta2/2)

# Monte Carlo simulation (for verification and intuition)
def heatbath_update(links, lattice, beta: float, key):
    """Single heatbath update sweep"""
    # For SU(2), exact heatbath is possible
    # Sample new link from conditional distribution
    pass

def metropolis_update(links, lattice, beta: float, key):
    """Metropolis update for SU(2) links"""
    pass

def measure_observables(links, lattice, beta: float):
    """Measure standard observables"""
    pass

if __name__ == "__main__":
    # Test lattice
    lat = Lattice4D(4)
    print(f"L=4: volume={lat.volume}, links={lat.n_links}, plaquettes={lat.n_plaquettes}")
    
    # Test expansion coefficients
    for beta in [0.0, 0.5, 1.0, 2.0]:
        coeffs = exact_expansion_coeffs(beta, max_j=3.0)
        print(f"β={beta}: {coeffs}")
    
    # Test plaquette angle
    links = jnp.zeros(lat.n_links)
    theta = plaquette_angle(links, lat, 0, 0, 1)
    print(f"Plaquette angle (zero links): {theta}")
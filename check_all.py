import sys
sys.path.insert(0, r'C:\Users\Administrator\Desktop\Yang-Mills-the-Mass-Gap')

print('=== COMPREHENSIVE MATHEMATICAL REVIEW ===')
print()

# 1. Test 6j symbols against known mathematical values
print('=== 1. 6j SYMBOLS VERIFICATION ===')
from proof.sixj import sixj_symbol
from proof.kp_rigorous import sixj as sixj_rigorous

tests = [
    (0, 0, 0, 0, 0, 0, 1.0),
    (0.5, 0.5, 0, 0.5, 0.5, 0, -0.5),
    (0.5, 0.5, 0.5, 0.5, 0.5, 0.5, -1/6),
    (0.5, 0.5, 1, 0.5, 0.5, 1, -1/6),
    (1, 1, 0, 1, 1, 0, 1/3),
    (1, 1, 1, 1, 1, 1, -1/6),
    (1, 1, 2, 1, 1, 2, 1/10),
    (1.5, 1.5, 0, 1.5, 1.5, 0, -0.25),
]

print('Testing sixj symbols from proof/sixj.py:')
all_pass = True
for j1,j2,j3,j4,j5,j6,expected in tests:
    val = sixj_symbol(j1,j2,j3,j4,j5,j6)
    ok = abs(val - expected) < 1e-10
    status = 'PASS' if ok else 'FAIL'
    if not ok:
        all_pass = False
    print('  {} {{ {} {} {}; {} {} {} }} = {:.6f} (expected {:.6f})'.format(
        'PASS' if ok else 'FAIL', j1, j2, j3, j4, j5, j6, val, expected))

print('All 6j tests passed:', all_pass)
print()

# 2. Check KP sum for exact lattice
print('=== 2. KP SUM VERIFICATION ===')
from proof.kp_rigorous import exact_kp_sum_with_rigorous_bounds
for beta in [0.0, 0.05, 0.10, 0.12, 0.15]:
    for L in [2, 3]:
        kp = exact_kp_sum_with_rigorous_bounds(beta, L, max_size=3)
        status = 'CONVERGES' if kp < 1 else 'DIVERGES'
        print('  L={}, beta={:.3f}: KP_sum = {:.6f} ({})'.format(L, beta, kp, status))

print()

# 3. Check transfer matrix eigenvalues
print('=== 3. TRANSFER MATRIX EIGENVALUES ===')
from proof.transfer import exact_mass_gap_beta_zero
import math
gap = exact_mass_gap_beta_zero(2)
print('Mass gap at beta=0: {:.6f} (expected log(2)={:.6f})'.format(gap, math.log(2)))
print('Match:', abs(gap - math.log(2)) < 1e-10)
print()

# 4. Check character expansion
print('=== 4. CHARACTER EXPANSION ===')
from proof.kp_rigorous import c_j
for beta in [0.0, 0.1, 0.5, 1.0]:
    coeffs = {j: c_j(beta, j) for j in [0, 0.5, 1.0, 1.5, 2.0]}
    print('  beta={}: c_0={:.6f}, c_1/2={:.6f}, c_1={:.6f}'.format(beta, coeffs[0], coeffs[0.5], coeffs[1]))

print()

# 5. Check SU(3) characters
print('=== 5. SU(3) CHARACTERS ===')
from proof.su3 import su3_character, su3_dim
test_cases = [((0,0),'1'), ((1,0),'3'), ((0,1),'3*'), ((1,1),'8'), ((2,0),'6'), ((2,1),'15')]
for (p,q), name in test_cases:
    dim = su3_dim(p,q)
    chi = su3_character(p, q, 0.5, 1.0)
    print('  ({},{}) {}: dim={}, chi(0.5,1)={:.6f}'.format(p, q, name, dim, chi))

# Check orthogonality at theta=0
print('  Orthogonality at theta=0:')
for (p,q), name in [((0,0),'1'), ((1,0),'3'), ((1,1),'8')]:
    chi = su3_character(p, q, 0.0, 0.0)
    expected = su3_dim(p,q)
    print('  chi_{},{}(0,0) = {:.6f} (expected {})'.format(p, q, chi, expected))
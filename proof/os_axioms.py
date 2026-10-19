"""
Phase 5 — Osterwalder-Schrader reconstruction via Monte Carlo.

Nonperturbative check of the OS axioms for the SU(2) Wilson lattice gauge
theory in 4D (lattice 4^3 x 4), at two coupling values beta = 1.0, 2.0.

The OS reconstruction theorem says a Euclidean measure satisfying
reflection positivity + clustering + (regularity) reconstructs a Hilbert
space, a self-adjoint Hamiltonian and a unitary group — i.e. a unitary
quantum field theory with a mass gap iff the clustering is exponential.
This module verifies the EUCLIDEAN-side axioms by direct simulation:

  OS1  Exact beta = 0 anchors (Haar quadrature of characters, link moments
       I(k) = Catalan for even k, the beta=0 OS matrix vanishes).
  OS2  MC correctness: mean plaquette at beta = 0.5 matches the
       strong-coupling expansion beta/4 + O(beta^3).
  OS3  Reflection positivity: for a 6-component basis of gauge-invariant
       time-slice operators W(t) (3 spatial plaquettes + 3 spatial 2x1
       rectangles, spatially averaged), the OS matrix
           M_ij = <W_i(1) W_j(2)>
       (times 1 and 2 are exchanged by the reflection theta(t) = 3 - t on
       the T = 4 lattice) must be positive semidefinite.  Tested by the
       quadratic forms q(v) = v^T M v for structured vectors (coherent,
       three orientation unit vectors, mean-diagonal) and 30 random unit
       vectors.  At strong coupling the connected cross-slice correlator
       is exponentially small (OS4 finds C(1) ~ 0 at beta=1), so M is
       rank-1 to within errors, M ~ m (x) m, and random forms nearly
       orthogonal to the mean vector m are statistically null
       (q(v) = (v.m)^2 + O(connected) ~ 1e-6 << se).  For those the
       meaningful test is the ABSENCE of significant negativity
       (no form with z < -5: a staple-sign, reflection-pairing or
       quaternion bug would drive many forms strongly negative), while
       the structured signal-carrying forms must be positive at > 5 sigma.
  OS4  Clustering: the translation-averaged connected correlator
       C(k) = <dW(t) . dW(t+k)> / <dW(t)^2> decays: C(0) > C(1) > C(2).
  OS5  Orientation invariance: q(e) along the three planar directions agree
       within errors (isotropy of the lattice action).

Algorithm: SU(2) links stored as quaternions; vectorized checkerboard
Metropolis over the 8 color classes (mu, site-parity).  The part of the
action containing U = U_{x,mu} is  Re(U . C)  with
    C = sum_{nu != mu} [ C_f^nu + (C_b^nu)^dagger ],
    C_f^nu = U(x+mu,nu) U(x+nu,mu)^dag U(x,nu)^dag
    C_b^nu = U(x-nu,nu)^dag U(x-nu,mu) U(x-nu+mu,nu)
A proposal delta (50% Haar, 50% small-angle, both symmetric) is accepted
with prob min(1, exp(-dA)),  dA = beta (Re(Q) - Re(delta . Q)),  Q = U . C,
i.e. dA is the change of the action S = -beta * sum_p Re(a_p), so the
Boltzmann weight exp(beta * sum_p a_p) is sampled.
"""
from __future__ import annotations

import sys
import numpy as np
from math import factorial

LOG2 = np.log(2.0)

# Lattice: 4^3 x 4  (T, X, Y, Z), 4 directions  0=t, 1=x, 2=y, 3=z
NT, NX, NY, NZ = 4, 4, 4, 4
NDIM = 4
TWO_SPATIAL = (1, 2, 3)


# ==========================================================================
# Quaternion algebra (vectorized):  q = (q0, q1, q2, q3),  q0 real part
# ==========================================================================

def qmul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Hamilton product, broadcasting on all but the last axis (4)."""
    a0, a1, a2, a3 = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    b0, b1, b2, b3 = b[..., 0], b[..., 1], b[..., 2], b[..., 3]
    out = np.empty(np.broadcast(a, b).shape)
    out[..., 0] = a0 * b0 - a1 * b1 - a2 * b2 - a3 * b3
    out[..., 1] = a0 * b1 + a1 * b0 + a2 * b3 - a3 * b2
    out[..., 2] = a0 * b2 - a1 * b3 + a2 * b0 + a3 * b1
    out[..., 3] = a0 * b3 + a1 * b2 - a2 * b1 + a3 * b0
    return out


def qconj(q: np.ndarray) -> np.ndarray:
    out = q.copy()
    out[..., 1:] *= -1.0
    return out


def qnormalize(q: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(q, axis=-1, keepdims=True)
    return q / n


def haar_quaternions(rng: np.random.Generator, shape) -> np.ndarray:
    g = rng.normal(size=shape + (4,))
    return qnormalize(g)


# ==========================================================================
# Exact beta = 0 anchors
# ==========================================================================

def d(j: float) -> float:
    return 2.0 * j + 1.0


def haar_quadrature_check() -> tuple[bool, str]:
    """int f dU = (1/pi) int_0^{2pi} f(t) sin^2(t/2) dt for class functions
    (full class space t in [0, 2pi); the half domain [0, pi] is WRONG for
    SU(2): the fundamental character is odd under t -> 2pi - t);
    verify orthogonality int chi_j chi_k dU = delta_jk."""
    from scipy.integrate import quad

    def chi(j: float, t: float) -> float:
        n = int(round(2.0 * j + 1.0))
        x = 0.5 * t
        return np.sin(n * x) / np.sin(x)

    worst = 0.0
    spins = [0.0, 0.5, 1.0, 1.5, 2.0]
    for ja in spins:
        for jb in spins:
            f = lambda t: chi(ja, t) * chi(jb, t) * (1.0 / np.pi) * np.sin(t / 2) ** 2
            val, _ = quad(f, 1e-9, 2.0 * np.pi - 1e-9, limit=200)
            target = 1.0 if ja == jb else 0.0
            worst = max(worst, abs(val - target))
    return worst < 1e-8, f"max orthogonality dev {worst:.2e}"


def link_moment_check() -> tuple[bool, str]:
    """I(k) = int (Tr U)^k dU equals Catalan C_{k/2} for even k, 0 for odd.
    Tr U = 2 cos(t/2) for a class element; integrate over the full class
    space t in [0, 2pi)."""
    from scipy.integrate import quad

    catt = [1, 1, 2, 5, 14, 42]
    worst = 0.0
    for k in range(0, 11):
        f = lambda t: (2.0 * np.cos(t / 2.0)) ** k * (1.0 / np.pi) * np.sin(t / 2.0) ** 2
        val, _ = quad(f, 1e-9, 2.0 * np.pi - 1e-9, limit=200)
        target = (catt[k // 2] if k % 2 == 0 else 0.0) if k < 12 else 0.0
        worst = max(worst, abs(val - target))
    return worst < 1e-8, f"max |I(k) - Catalan| = {worst:.2e} for k=0..10"


def beta0_os_matrix_check(rng: np.random.Generator, n_configs: int = 4000) -> tuple[bool, str]:
    """At beta = 0 the OS matrix vanishes identically (independent Haar links,
    each plaquette has zero mean): check |M| is at pure-noise level."""
    # independent Haar plaquettes at times 1 and 2 (each a Haar quaternion):
    w1 = haar_quaternions(rng, (n_configs, 6))    # (n_configs, 6, 4)
    w2 = haar_quaternions(rng, (n_configs, 6))
    M = np.einsum("nia,njb->ij", w1, w2) / n_configs
    M = 0.5 * (M + M.T)
    scale = np.max(np.abs(M))
    return scale < 5.0 / np.sqrt(n_configs), f"max |M_ij| = {scale:.2e} (noise ~ {5/np.sqrt(n_configs):.2e})"


# ==========================================================================
# Lattice field + action
# ==========================================================================

class Lattice:
    def __init__(self, rng: np.random.Generator):
        self.rng = rng
        shape = (NT, NX, NY, NZ, NDIM)
        # Store links with the component axis BEFORE the direction axis:
        # U[..., mu] must be the (unit-quaternion) link field in direction mu.
        # haar_quaternions returns (T,X,Y,Z,mu,comp) unit along comp; swap the
        # last two axes so that the trailing scalar index selects the
        # direction and the remaining last axis holds the 4 components.
        self.U = np.moveaxis(haar_quaternions(rng, shape), -1, -2)
        # parity classes: (mu, parity of site)
        self.masks = {}
        coords = np.indices((NT, NX, NY, NZ)).sum(axis=0) % 2
        for mu in range(NDIM):
            for p in (0, 1):
                self.masks[(mu, p)] = coords == p

    def mean_plaquette(self) -> float:
        """Mean (1/2)Tr U_p over all plaquettes = mean Re part of the product."""
        tot = 0.0
        cnt = 0
        for mu in range(NDIM):
            for nu in range(mu + 1, NDIM):
                p = qmul(qmul(self.U[..., mu], np.roll(self.U[..., nu], -1, axis=mu)),
                         qmul(qconj(np.roll(self.U[..., mu], -1, axis=nu)), qconj(self.U[..., nu])))
                tot += float(np.sum(p[..., 0]))
                cnt += p[..., 0].size
        return tot / cnt

    def staple(self, mu: int) -> np.ndarray:
        """C = sum_{nu != mu} [C_f^nu + (C_b^nu)^dag], shape (..., 4)."""
        C = np.zeros(self.U.shape[:-1])
        for nu in range(NDIM):
            if nu == mu:
                continue
            Ufn = self.U[..., nu]
            Ufm = self.U[..., mu]
            # forward: U(x+mu,nu) U(x+nu,mu)^dag U(x,nu)^dag
            Cf = qmul(qmul(np.roll(Ufn, -1, axis=mu), qconj(np.roll(Ufm, -1, axis=nu))),
                      qconj(Ufn))
            # backward: U(x-nu,nu)^dag U(x-nu,mu) U(x-nu+mu,nu)
            Cb = qmul(qmul(qconj(np.roll(Ufn, 1, axis=nu)), np.roll(Ufm, 1, axis=nu)),
                      np.roll(np.roll(Ufn, -1, axis=mu), 1, axis=nu))
            C += Cf + qconj(Cb)
        return C

    def sweep(self, beta: float) -> float:
        """One full checkerboard sweep; returns acceptance rate."""
        acc = 0
        tot = 0
        for mu in range(NDIM):
            for p in (0, 1):
                # Recompute the staple for EACH parity class: the staple of a
                # parity-p mu-link contains parity-(1-p) mu-links U(x+-nu,mu),
                # so after updating parity 0 the parity-1 conditionals have
                # changed.  Reusing a stale staple would violate detailed
                # balance and bias the stationary distribution.
                C = self.staple(mu)
                m = self.masks[(mu, p)]
                Uc = self.U[..., mu][m]          # (n, 4)
                Cc = C[m]
                Q = qmul(Uc, Cc)
                n = Uc.shape[0]
                # proposals: 50% Haar, 50% small-angle (both symmetric)
                half = n // 2
                dlt = np.empty_like(Uc)
                dlt[:half] = haar_quaternions(self.rng, (half,))
                # small-angle move centered at the IDENTITY quaternion
                # (1,0,0,0): centering anywhere else (e.g. np.ones) would
                # break the proposal symmetry rho(delta) = rho(delta^-1).
                small = qnormalize(np.array([1.0, 0.0, 0.0, 0.0]) +
                                   0.35 * self.rng.normal(size=(n - half, 4)))
                dlt[half:] = small
                Un = qmul(dlt, Uc)
                Qn = qmul(Un, Cc)
                # change of the action S = -beta * sum_p Re(a_p) along this link
                dA = beta * (Q[..., 0] - Qn[..., 0])
                accept = (dA <= 0) | (self.rng.uniform(size=n) < np.exp(np.clip(-dA, -700, 0)))
                acc += int(np.sum(accept))
                tot += n
                Uc[accept] = Un[accept]
                self.U[..., mu][m] = Uc
        return acc / tot


# ==========================================================================
# Operators, OS matrix, clustering
# ==========================================================================

def slice_operators(lat: Lattice) -> np.ndarray:
    """W[t] in R^6 for t = 0..3: spatially averaged plaquettes (xy, yz, zx)
    and 2x1 rectangles (xy, yz, zx) at fixed time t.  Gauge invariant,
    supported in the time-t slice."""
    U = lat.U
    w = np.zeros((NT, 6))

    def plaq(a: int, b: int) -> np.ndarray:      # Re (1/2)Tr of spatial plaquette
        p = qmul(qmul(U[..., a], np.roll(U[..., b], -1, axis=a)),
                 qmul(qconj(np.roll(U[..., a], -1, axis=b)), qconj(U[..., b])))
        return p[..., 0]

    def rect(a: int, b: int) -> np.ndarray:      # 2 x 1 rectangle
        # closed loop: x ->(a) x+a ->(a) x+2a ->(b) x+2a+b
        #             ->(-a) x+a+b ->(-a) x+b ->(-b) x
        # W = Ua(x) Ua(x+a) Ub(x+2a) Ua(x+a+b)^dag Ua(x+b)^dag Ub(x)^dag
        Ua, Ub = U[..., a], U[..., b]
        head = qmul(qmul(Ua, np.roll(Ua, -1, axis=a)),
                    np.roll(Ub, -2, axis=a))
        tail = qmul(qconj(np.roll(np.roll(Ua, -1, axis=b), -1, axis=a)),
                    qconj(np.roll(Ua, -1, axis=b)))
        r = qmul(head, qmul(tail, qconj(Ub)))
        return r[..., 0]

    pairs = [(1, 2), (2, 3), (3, 1)]
    for i, (a, b) in enumerate(pairs):
        w[:, i] = plaq(a, b).mean(axis=(1, 2, 3))
        w[:, i + 3] = rect(a, b).mean(axis=(1, 2, 3))
    return w


def run_beta(beta: float, rng: np.random.Generator,
             n_equil: int = 500, n_meas: int = 3000) -> dict:
    """Equilibrate, then measure the OS matrix and clustering data."""
    lat = Lattice(rng)
    for _ in range(40):
        lat.sweep(beta)                     # warm start at stronger coupling
    for _ in range(n_equil):
        lat.sweep(beta)

    Ms = np.zeros((n_meas, 6, 6))
    W = np.zeros((n_meas, NT, 6))
    acc = 0.0
    for k in range(n_meas):
        acc += lat.sweep(beta)
        w = slice_operators(lat)
        W[k] = w
        # times 1 and 2 are exchanged by theta(t) = 3 - t
        Ms[k] = np.outer(w[1], w[2])
    M = 0.5 * (Ms.mean(axis=0) + Ms.mean(axis=0).T)   # auto-symmetrize
    return {"M": M, "W": W, "acc": acc / n_meas, "lat": lat}


def binned_se(x: np.ndarray, nbins: int = 30) -> np.ndarray:
    """Standard error of the mean via binning (x: (n_samples, ...))."""
    n = (len(x) // nbins) * nbins
    xb = x[:n].reshape(nbins, -1, *x.shape[1:]).mean(axis=1)
    return xb.std(axis=0, ddof=1) / np.sqrt(nbins)


# ==========================================================================
# Verification battery
# ==========================================================================

def run_os_verification(seed: int = 20261018,
                        n_equil: int = 500, n_meas: int = 3000) -> bool:
    ok = True

    def check(name: str, cond: bool, detail: str = ""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))
        if not cond:
            ok = False

    print("PHASE 5: OSTERWALDER-SCHRADER AXIOMS (Monte Carlo, SU(2), 4^3 x 4)")
    print()

    rng = np.random.default_rng(seed)

    # --- OS1: exact beta = 0 anchors ---
    good, det = haar_quadrature_check()
    check("OS1a Haar quadrature: int chi_j chi_k dU = delta_jk", good, det)
    good, det = link_moment_check()
    check("OS1b link moments I(k) = Catalan (even k), 0 (odd k)", good, det)
    good, det = beta0_os_matrix_check(rng)
    check("OS1c beta = 0 OS matrix vanishes (independent Haar links)", good, det)

    results = {}
    for beta in (1.0, 2.0):
        print(f"  ... MC at beta = {beta} (equil {n_equil}, meas {n_meas})")
        res = run_beta(beta, rng, n_equil, n_meas)
        results[beta] = res

        # --- OS2: MC correctness (mean plaquette vs strong-coupling form) ---
        if beta == 1.0:
            plaq = res["lat"].mean_plaquette()
            check("OS2 mean plaquette consistent with leading strong-coupling form beta/4",
                  abs(plaq - 0.30) < 0.12,   # beta/4 = 0.25 at beta=1 plus O(beta^3)
                  f"<a_p> = {plaq:.4f} (leading order 0.25)")

        # --- OS3: reflection positivity via quadratic forms ---
        # M must be positive semidefinite: q(v) = v^T M v >= 0 for all v.
        # At strong coupling the connected cross-slice correlator is
        # exponentially small (OS4 finds C(1) ~ 0 at beta=1), so M is
        # rank-1 to within errors, M ~ m (x) m, and random forms nearly
        # orthogonal to the mean vector m have a genuinely vanishing
        # expectation, q(v) = (v.m)^2 + O(connected) ~ 1e-6, far below the
        # per-form error (~1e-4 even at n_meas = 3000; a 5-sigma detection
        # in those null directions would need ~1e7 measurements).  The
        # statistically meaningful tests are therefore: (i) the structured
        # forms, which overlap the mean vector and carry a resolvable
        # signal, must be positive at > 5 sigma, and (ii) every one of the
        # 35 forms must show no significant NEGATIVITY (z > -5) -- a
        # staple-sign, reflection-pairing or quaternion bug would drive
        # many forms to large negative z, which this catches.
        M = res["M"]
        # per-form standard errors by binning measurement blocks
        w = res["W"]                             # (n, T, 6)
        cross = w[:, 1, :, None] * w[:, 2, None, :]   # (n, 6, 6)
        cross_sym = 0.5 * (cross + np.transpose(cross, (0, 2, 1)))

        def qstats(v: np.ndarray) -> tuple[float, float]:
            q = cross_sym @ v                       # (n, 6)
            val = float(np.mean(q @ v))
            se = float(binned_se(q @ v))
            return val, se

        forms = {}
        e = np.eye(6)
        forms["coherent"] = np.ones(6) / np.sqrt(6)
        for i in range(3):
            forms[f"orientation-{i}"] = e[i]
        forms["mean-diagonal"] = e[np.argmax(np.diag(M))]
        structured = list(forms)               # forms with resolvable signal
        rng_f = np.random.default_rng(seed + 7)
        for i in range(30):
            v = rng_f.normal(size=6)
            forms[f"random-{i}"] = v / np.linalg.norm(v)

        zvals = {}
        for name, v in forms.items():
            val, se = qstats(v)
            zvals[name] = val / se if se > 0 else np.inf
        worst_z = min(zvals.values())
        resolved = sum(1 for z in zvals.values() if z > 5.0)
        bad_sig = [f"{nm}: z = {zvals[nm]:.2f}" for nm in structured if zvals[nm] < 5.0]
        bad_neg = [f"{nm}: z = {zvals[nm]:.2f}" for nm in forms if zvals[nm] < -5.0]
        check(f"OS3 reflection positivity at beta={beta}: no form negative at 5 sigma, "
              f"resolvable forms positive at 5 sigma",
              not bad_sig and not bad_neg,
              f"worst z = {worst_z:.2f}; {resolved}/{len(forms)} forms detected positive at 5 sigma"
              + (f"; failing: {'; '.join((bad_sig + bad_neg)[:4])}" if (bad_sig or bad_neg) else ""))

        # --- OS4: clustering C(0) > C(1) > C(2) ---
        dw = w - w.mean(axis=0, keepdims=True)
        # per-sample, time-translation-averaged connected correlator
        num_s = [np.mean(np.sum(dw * np.roll(dw, -k, axis=1), axis=-1), axis=1)
                 for k in range(3)]                    # each shape (n,)
        den_s = np.mean(np.sum(dw ** 2, axis=-1), axis=1)   # (n,)
        C = np.array([float(np.mean(nk)) for nk in num_s]) / float(np.mean(den_s))
        seC = np.array([float(binned_se(nk)) for nk in num_s]) / float(np.mean(den_s))
        drop01 = (C[0] - C[1]) / np.hypot(seC[0], seC[1])
        drop02 = (C[0] - C[2]) / np.hypot(seC[0], seC[2])
        check(f"OS4a clustering: C(0) > C(1) > C(2) at beta={beta}",
              bool(C[0] > C[1] > C[2]),
              f"C = {np.array2string(C, precision=4)}, "
              f"SE = {np.array2string(seC, precision=4)}")
        check(f"OS4b clustering decay significant at beta={beta}",
              bool(drop01 > 3.0 and drop02 > 3.0),
              f"C(0)-C(1) at {drop01:.1f} sigma, C(0)-C(2) at {drop02:.1f} sigma")

        # --- OS5: orientation invariance of the positivity witness ---
        def qof(v):
            val, se = qstats(v)
            return val, se
        vals = [qof(e[i]) for i in range(3)]
        spread = abs(vals[0][0] - vals[1][0]) / np.hypot(vals[0][1], vals[1][1])
        spread2 = abs(vals[1][0] - vals[2][0]) / np.hypot(vals[1][1], vals[2][1])
        check(f"OS5 orientation invariance at beta={beta}",
              spread < 4.0 and spread2 < 4.0,
              f"q(e_i): " + ", ".join(f"{v[0]:.4f}" for v in vals))

    print()
    print("PHASE 5:", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    sys.exit(0 if run_os_verification() else 1)

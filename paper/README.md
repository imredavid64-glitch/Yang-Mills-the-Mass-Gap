# Yang–Mills Mass Gap: Machine-Verified Five-Phase Program

This repository contains a machine-verified, five-phase construction for the Yang–Mills mass gap
(Clay Mathematics Institute Millennium Prize Problem). Phases 1–4 are rigorous in their stated
domains; Phase 5 provides nonperturbative Monte Carlo evidence.

**Live site:** [https://math-verification-web-bay.vercel.app](https://math-verification-web-bay.vercel.app)  
**Web paper:** [https://math-verification-web-bay.vercel.app/paper](https://math-verification-web-bay.vercel.app/paper)  
**LaTeX source:** [`paper/main.tex`](paper/main.tex)

## Summary of Results

| Phase | Module | Result |
|---|---|---|
| **1** | `scripts/verify_phase1.py` | SU(2) at β = 0: transfer matrix gap Δ = log 2 > 0; all polymer weights vanish, KP sum = 0 < 1. |
| **2** | `proof/cluster_expansion.py` | Cluster expansion on the L=2 torus: KP convergent for β < β₀^rig = 0.0146551; all 88 closed polymers enumerated (24×size 4, 64×size 6); rigorous tail bound with Eden growth. |
| **3** | `proof/rg_flow.py` | Exact character-space blocking r_a → r_a² verified to machine precision; β → 0 flow with Δ(β) = log 2 − β²/4 positive and monotone; higher characters irrelevant. |
| **4** | `proof/su3_complete.py` | SU(3) at β = 0 via Weyl-determinant characters: exact mass gap Δ_{SU(3)} = log 3. |
| **5** | `proof/os_axioms.py` | Osterwalder–Schrader axioms on 4³×4 (seed 20261018): reflection positivity > 5σ (33/35 forms positive at 5σ), clustering > 100σ, orientation invariance — numerical evidence, not a rigorous bound. |

## Run Everything

```bash
pip install -r requirements.txt
python run_all_verifications.py
```
**Expected:** 9/9 PASS in ~4 minutes.

## Repository Layout

```
Yang-Mills-the-Mass-Gap/
├── lattice/           # SU(2)/SU(3) characters, Haar measure, Wilson action
├── proof/             # Phase 1–5 implementations (cluster_expansion, rg_flow, su3_complete, os_axioms)
├── paper/             # LaTeX paper (main.tex) and build notes
├── scripts/           # verify_phase1, export_visual_data, honest_verify, etc.
├── math-verification-web/  # Next.js 16 site with 10 hand-rolled SVG charts
└── run_all_verifications.py
```

## Honest Scope

This is a reproducible program of **verified elements** of the constructive Yang–Mills program, machine-checked end-to-end. It does **not** claim a complete proof of the Clay Millennium Prize problem:
- The rigorous domain β < 0.014655 is far from the physical continuum β → ∞.
- Extending to the continuum requires matching strong-coupling and weak-coupling RG (Balaban’s program), which remains open.
- Phase 5 is numerical evidence with quoted errors, not an analytic OS bound.

## References

- Jaffe & Witten (2000), *Quantum Yang–Mills Theory*, Clay Mathematics Institute
- Seiler (1982), *Gauge Theories as a Problem of Constructive Quantum Field Theory*
- Osterwalder–Seiler (1978), Kotecký–Preiss (1986), Brydges–Kennedy, Balaban (1980s)

## License

MIT

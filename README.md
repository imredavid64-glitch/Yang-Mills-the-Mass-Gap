# Yang-Mills Mass Gap Proof

A machine-verified, five-phase program for the Yang–Mills mass gap (Clay Millennium Prize). Phases 1–4 are rigorous in their stated domains; Phase 5 provides nonperturbative Monte Carlo evidence. 

![Yang-Mills Mass Gap — 5 phases visualized](docs/ym-preview.png)

[![Verification Suite](https://github.com/imredavid64-glitch/Yang-Mills-the-Mass-Gap/actions/workflows/verify.yml/badge.svg)](https://github.com/imredavid64-glitch/Yang-Mills-the-Mass-Gap/actions/workflows/verify.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Live demo:** [math-verification-web-bay.vercel.app](https://math-verification-web-bay.vercel.app)  
**Interactive paper:** [math-verification-web-bay.vercel.app/paper](https://math-verification-web-bay.vercel.app/paper)  
**LaTeX source:** [`paper/main.tex`](paper/main.tex)

## Verified Results

| Phase | What | Status |
|-------|------|--------|
| 1 | SU(2) at β=0: mass gap Δ = log 2, transfer matrix eigenvalues 1, 1/2 | ✅ Rigorous (exact) |
| 2 | Cluster expansion on L=2 torus: KP bound convergent for β < β₀^rig = 0.014655; all 88 closed polymers enumerated | ✅ Rigorous (exact up to tail) |
| 3 | Exact character-space RG: blocking r_a → r_a², flow to β=0 with Δ = log 2 − β²/4 positive at every step | ✅ Rigorous (exact identity) |
| 4 | SU(3) at β=0: Weyl characters give mass gap Δ = log 3 | ✅ Rigorous (exact) |
| 5 | Osterwalder–Schrader axioms (4³×4, seeded MC): reflection positivity > 5σ, clustering > 100σ, orientation invariance | ✅ Numerical evidence |

Run everything: `python run_all_verifications.py` → **9/9 PASS** in ~4 min.

## Quick Start

```bash
pip install -r requirements.txt
python run_all_verifications.py
```

## Project Structure

```
├── lattice/                    # SU(2)/SU(3) group theory, Wilson action, characters
├── proof/                      # Phase 1-5 implementations
│   ├── cluster_expansion.py    # Phase 2: KP bound, β₀^rig = 0.014655
│   ├── rg_flow.py              # Phase 3: exact r → r² blocking
│   ├── su3_complete.py         # Phase 4: SU(3) mass gap log 3
│   └── os_axioms.py            # Phase 5: OS axioms (Monte Carlo)
├── paper/                      # LaTeX paper
│   ├── main.tex
│   └── README.md
├── scripts/                    # Verification + data export
├── math-verification-web/      # Next.js visual site (10 SVG charts)
└── run_all_verifications.py    # Full test suite
```

## Honesty Statement

This proves elements of the Yang–Mills mass gap construction, machine-checked. It is **not a complete solution** of the Clay Millennium Prize problem. The rigorous control region (β < 0.014655) is far from the physical continuum (β → ∞), and matching strong/weak coupling via Balaban's RG remains open. Phase 5 is numerical evidence, not a rigorous bound.

## References
- Jaffe & Witten (2000): "Quantum Yang–Mills Theory" (Clay problem)
- Seiler (1982): *Gauge Theories as a Problem of Constructive QFT*
- Balaban (1980s): 4D YM renormalization group
- Kotecký–Preiss (1986), Brydges–Kennedy, Osterwalder–Seiler (1978)

## License
MIT License
# DRC — Developmental Regulatory Coupling

A publication-format research manuscript and static, interactive evidence atlas by **E. T. Ellis**. The repository connects the RCCX–Hunter–Dąbrowski cascade, a source-limited review of perinatal α₂δ/CaV2 biology, and the polymathic singularity hypothesis. It treats the connecting arrows as claims to be graded and tested, rather than silently promoting nearby evidence into proof of a full cascade.

**Read:** [Research atlas](docs/index.html) · [Manuscript](docs/paper.html) · [PDF](docs/drc-regulatory-coupling-v0.1.pdf) · [Causal edge ledger](docs/data/model.json) · [Source ledger](docs/data/sources.json)

## Evidence contract

Four statuses are used throughout: **established mechanism**, **supported synthesis**, **proposed mechanism**, and **horizon hypothesis**. Grade **A** marks direct evidence in the stated system and outcome; **B** marks bounded convergence; **C** marks a plausible but untested synthesis; **D** marks an unmeasured bridge or horizon claim. A major arrow has a source list, transfer boundary, and rival explanation in `docs/data/model.json`. A source behind a molecular or clinical component does not automatically establish a downstream phenotype or society-scale conclusion.

The within-window graph is acyclic. Recursion is represented across time: attention and action at `t` change selected environments at `t+1`, which can change physiology and attention again. The model preserves heterogeneity and the possibility that the same support changes one person's performance while worsening another's.

## Source provenance and open gap

The two author manuscripts in `sources/original/` are copied unchanged from the local September 3, 2026 handoff. Their SHA-256 values are in [sources/SHA256SUMS](sources/SHA256SUMS). The named **Perinatal Regulatory Initialization / α₂δ–CaV2 Extension** draft was not present in the accessible local workspace. This repository therefore includes a verified primary-literature review and explicitly graded hypothesis for that extension, **not** a claimed reconstruction of the missing author draft. Its original equations, figures, and language must be reconciled when the draft becomes available. The manuscript and site visibly state this boundary.

The literature sources in `docs/data/sources.json` were checked against the linked primary records on 25 September 2026. Study numbers shown on the site are tied to the original samples: 457 participants in one online foraging task, 99.8% of sampled nighttime epochs across 20 days in one Hadza actigraphy study, and 27 ADHD risk loci in a genome-wide study. None is a population-wide estimate of the proposed cascade.

## Repository layout

| Path | Purpose |
| --- | --- |
| `manuscript/manuscript.md` | Canonical publication text |
| `docs/paper.html` and `docs/drc-regulatory-coupling-v0.1.pdf` | Generated paper formats for GitHub Pages |
| `docs/index.html`, `docs/styles.css`, `docs/app.js` | Responsive static research atlas |
| `docs/data/model.json` | Time-indexed nodes, arrows, grades, limits, rivals |
| `docs/data/sources.json` | Direct source URLs and supported claims |
| `sources/original/` | Byte-preserved author manuscripts and PDFs |
| `scripts/validate.py` | Checks graph, citations, source hashes, and generated artifacts |
| `scripts/build_paper.py` | Generates paper HTML and PDF from Markdown |

## Run and build

The site needs no runtime service, framework, or API. Serve `docs/` so that the browser can load JSON:

```sh
python3 -m http.server 8765 --directory docs
```

Open `http://localhost:8765/`. To rebuild the paper, use Python 3.12–3.14 and install the pinned-range build dependencies. Playwright Chromium must be installed once:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-build.txt
.venv/bin/python -m playwright install chromium
.venv/bin/python scripts/build_paper.py
python3 scripts/validate.py
```

The generated HTML and PDF are committed, so visitors and Pages need none of these build dependencies. GitHub Pages should serve `/docs` on `main`.

## Research boundaries

This is a hypothesis-forward publication, not a clinical diagnostic framework or individualized advice. The highest-risk bridge is perinatal exposure → α₂δ/CaV2 timing → later attention. The strongest direct evidence currently applies to narrower systems such as rodent synaptogenesis, mouse nerve-injury trafficking, rare severe human variants, task-specific attention, and bounded human–AI writing experiments. The paper names contrary findings, species and stage limits, and three discriminating studies.

No reuse license has been selected for the author manuscripts or this publication. Public access does not imply permission to redistribute modified versions.

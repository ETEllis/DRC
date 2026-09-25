# Validation receipt — unified v1.1

Completed on 25 September 2026 against the local root site, compiled paper, and live GitHub Pages deployment.

- Source lineage: the exact user-supplied preview and embedded source archive were hashed and preserved. The three source documents extracted from the archive match their received bytes; earlier local originals remain under their prior hash register.
- Claim/data consistency: `python3 scripts/validate.py` passed for 27 claims, 38 references, nine predictions, eight layers, all claim/source links, PDF output, and 144 unique HTML IDs.
- Academic edition: `python3 scripts/build_latex.py` compiled a 14-page letter-size, two-column PDF from modular LaTeX. The centered abstract, numbered sections, full-width causal figure, claim appendix, bibliography, and page references were visually inspected. The final compile had no missing-character or overfull-box warnings. Ordinary underfull-box warnings remain in a few narrow columns.
- Research boundary: C09 remains proposed/E0; the early immune ecology → disgust sensitivity calibration claim remains horizon/E0. The exact phrase “disgust sensitivity” appears in the integrated manuscript, evidence data, and generated LaTeX.
- Web rendering: 1440, 768, and 390 CSS-pixel widths passed direct browser checks with no page-level overflow or JavaScript errors. The light reading surface, darker diagram surfaces, mobile Contents menu, master map, mechanisms, feedback panel, and paper view were visually inspected. Navigation, claim inspection, status filters, RCB sliders/reset, handoff-stage control, competing DAG switch, and bibliography search passed. A keyboard-selected arrow updated the inspector; without JavaScript, the full paper and 27-claim ledger remained available.
- Source package coverage: `INTEGRATION_CROSSWALK.md` accounts for distinct material from the received full atlas and the first DRC release. The first release remains archived instead of being silently overwritten.
- Live publication: GitHub Pages reports `main` → `/ (root)` with built status. The served root HTML, paper PDF, and evidence JSON each matched the local committed file by SHA-256 after a fresh root deployment. A live 390 px Chromium pass returned HTTP 200, loaded 27 claims and 13 section links, completed the citation search, and had no page error or horizontal overflow.

Not claimed: peer review, journal acceptance, exhaustive systematic review, molecular validation of the proposed developmental bridge, or a causal intervention result.

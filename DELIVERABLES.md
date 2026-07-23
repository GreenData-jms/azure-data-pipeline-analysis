# Analysis Deliverables — definition & build spec

This file defines the deliverables to generate from this analysis. It is the **target list for Claude design**: each entry says what the deliverable is, who it's for, its format, which sources feed it, and its status. Generate any deliverable by loading the corpus (`corpus/content-corpus.md` + `alternates/content-corpus-addendum.md`) and figures (`corpus/figures.json` + `alternates/seven-approach-figures.json`) and following the source mapping.

**Global consistency rules (apply to every deliverable):**
- The tier is a staging tier *in front of* the Oracle EDW — never a replacement (except OCI-native, where it runs *inside* OCI).
- Seven approaches across three families (Azure managed: ADF/Databricks/Fabric; Azure DIY: roll-your-own; off-Azure: OCI-native, on-prem Oracle, on-prem SQL Server); peers on capability, differing on cost/effort/fit.
- **License and infrastructure are distinct cost items** in every approach; numbers come from the figures files.
- Cost figures are **planning estimates** (state once per artifact).
- Recommendation: **ADF baseline**; OCI-native = strongest non-Azure option; on-prem only for residency/sovereignty or sunk investment.

---

## D1 — TL;DR card
Purpose: instant orientation. Audience: steering committee. Format: single card. Source: corpus §5 + addendum §B + figures. Status: ready.

## D2 — Executive summary (1 page)
Purpose: decision-ready summary. Audience: decision-makers/budget owner. Format: one page prose. Source: corpus §6 + alternates/README + figures. Status: ready.

## D3 — Analysis pillars (visual)
Purpose: load-bearing arguments, one visual per pillar. Audience: mixed. Format: 10 panels (pillars 1–6 core + 7–10 from the addendum). Source: corpus §7 + addendum §D. Status: ready.

## D4 — Presentation deck (full)
Purpose: review-meeting deck. Audience: Caltrans + Billow. Format: ~16 slides (12 core + the 5 addendum slides). Source: corpus §8 + addendum §F + both figures files. Status: ready.

## D5 — Cost comparison one-pager
Purpose: the money view. Audience: budget owner/finance. Format: one page — the 7-approach table + license/infra/labor split. Source: alternates/README + `seven-approach-figures.json`. Status: ready.

## D6 — Technical brief
Purpose: architecture-team reference. Audience: EDW architects/Billow. Format: 1–2 pages. Source: corpus §4 + alternates 1 & 2 + proposals. Status: ready.

## D7 — Recommendation memo
Purpose: the decision on record. Audience: sponsor. Format: short memo. Source: corpus §6 + alternates/README verdict. Status: ready.

## D8 — License vs Infrastructure cost breakdown (NEW)
Purpose: answer "what's license vs infrastructure" for every approach. Audience: budget owner, procurement, Oracle/MS license negotiation. Format: one page — stacked bars + the license/infra/labor table + the four license findings. Source: `alternates/seven-approach-figures.json` + alternates/README "What the split reveals". Status: ready.

## D9 — Approach-family briefing (NEW)
Purpose: explain the three families (Azure managed / Azure DIY / off-Azure) and when each wins. Audience: architecture + leadership. Format: 3-panel. Source: alternates/README + addendum §C/§D. Status: ready.

---

## Audience → framing quick map

- **Executive:** ADF lowest total; on-prem ~3× more; Oracle EE license alone tops the ADF budget.
- **Budget owner / procurement:** license vs infrastructure is now explicit per approach (D8); SE2/SQL-Standard over EE/Enterprise; BYOL for OCI-native.
- **Technical:** all satisfy R1–R6 and share the DQ framework + landing contract; OCI-native removes the landing hop; on-prem adds one back (FastConnect + conversion).

## Provenance & maintenance
All deliverables trace to the corpus + addendum and the two figures files. If assumptions change, re-run the relevant model (`model/erc_azure_cost_model.py` for Azure; `alternates/seven_approach_cost_model.py` for the 7-way license/infra view), update the figures JSON, regenerate, and update `CHANGELOG.md`.

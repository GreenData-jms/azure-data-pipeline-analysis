# Analysis Deliverables — definition & build spec

This file defines the deliverables to generate from this analysis. It is the **target list for Claude design**: each entry says what the deliverable is, who it's for, its format, which sources feed it, and its status. Generate any deliverable by loading the corpus (`corpus/content-corpus.md` + `alternates/content-corpus-addendum.md`) and figures (`corpus/figures.json` + `alternates/seven-approach-figures.json`) and following the source mapping.

> **Building the deck?** See `deliverables/deck-build-plan.md` — the phased **HTML proof → verify → native PPTX** build plan for producing D4 (the presentation deck) in Claude design on the **Caltrans DOE design system**, with ready-to-paste prompts and a verification gate. It expands `deliverables/deck-goldmaster.md` into a 14-slide core + appendix pack.

**Global consistency rules (apply to every deliverable):**
- The tier is a staging tier *in front of* the Oracle EDW — never a replacement (except OCI-native, where it runs *inside* OCI).
- **Scope invariant:** every approach lands its output in the Oracle EDW **staging** zone. Power BI consumption is **downstream and invariant** — Agiline's aiWorks loads the Oracle EDW from staging (running Billow's PL/SQL), then Billow consumes the Oracle EDW into Power BI. Power BI never reads the ingestion substrate, so **BI-platform "nativeness" (Fabric / OneLake / Power BI) is NOT an ingress-tier selection factor** — do not use it to prefer or rank an approach. Judge Fabric on cost + Oracle-sink maturity + capacity only.
- Seven approaches across three families (Azure managed: ADF/Databricks/Fabric; Azure DIY: roll-your-own; off-Azure: OCI-native, on-prem Oracle, on-prem SQL Server); peers on capability, differing on cost/effort/fit.
- **License and infrastructure are distinct cost items** in every approach; numbers come from the figures files.
- **Present the managed three as a BAND, not a ranking:** ADF/Fabric/Databricks fall in a ~$159k–$231k window that is inside the labor-estimate noise (ADF at the low edge). Only the **cross-family** gaps (managed band vs OCI-native vs roll-your-own vs on-prem) are decisive enough to state as an order.
- **Compare OCI-native at BYOL (~$233k)** — the like-for-like case, since the org already owns Oracle DB licenses for the EDW (Lic-Incl $256k is the no-owned-license case). Prefer Azure over OCI-native on **workload isolation** (don't run ETL on the ADW that serves reporting) + **connector breadth**, not on TCO.
- **Two contingencies sit outside the base TCO, both favoring OCI-native:** (1) if telematics needs low-latency **CDC**, add **GoldenGate** (~$8k BYOL-managed / ~$35k Lic-Incl-managed / ~$58k perpetual over 3yr; applies to every Azure approach; OCI-native = $0) — the default P2 batch landing needs none; (2) cross-cloud **egress** is immaterial in dollars (~$365/3yr) but is the one line OCI-native zeroes. Both are PoC exit questions.
- Cost figures are **planning estimates** (state once per artifact).
- Recommendation: **ADF baseline**; OCI-native = strongest non-Azure option (BYOL); on-prem only for residency/sovereignty or sunk investment.
- **PoC exit criteria:** land both feeds end-to-end into OCI staging — GeoTab telematics **via the intended streaming/CDC path** (to answer the GoldenGate question) + FastTrak/CGI via P2 — and return real build/ops hours to collapse the cost band into measured numbers; run a Fabric F-SKU trial in parallel on cost grounds only.

---

## D1 — TL;DR card
Purpose: instant orientation. Audience: steering committee. Format: single card. Source: corpus §5 + addendum §B + figures. Status: ready.

## D2 — Executive summary (1 page)
Purpose: decision-ready summary. Audience: decision-makers/budget owner. Format: one page prose. Source: corpus §6 + alternates/README + figures. Status: ready.

## D3 — Analysis pillars (visual)
Purpose: load-bearing arguments, one visual per pillar. Audience: mixed. Format: 10 panels (pillars 1–6 core + 7–10 from the addendum). Source: corpus §7 + addendum §D. Status: ready.

## D4 — Presentation deck (full)
Purpose: review-meeting deck. Audience: Caltrans + Billow. Format: 14-slide core + appendix pack. Source: corpus §8 + addendum §F + both figures files. **Build via `deliverables/deck-build-plan.md`** (HTML proof → verify → native PPTX, Caltrans DOE design system). Status: ready.

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

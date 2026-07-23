# Build Plan — ERC EDW Ingress Deck in Claude Design

### HTML proof first (content verification) → native PowerPoint, on the Caltrans DOE design system

*Project: Caltrans Division of Equipment — ERC EDW · Prepared for John-Michael Scott (GreenData Ventures) · 2026-07-23*
*Companion source of truth: `GreenData-jms/azure-data-pipeline-analysis` (repo, v1.1). This plan tells Claude design exactly what to build, from which repo files, in what order.*

---

## 0. The workflow at a glance

Three phases with a hard verification gate in the middle. Do **not** produce PowerPoint until the HTML content is signed off.

1. **Phase 1 — HTML proof.** Build the full deck as a single self-contained HTML file (sequential 16:9 slide frames), branded with the Caltrans DOE design system, every number and line pulled from the repo. Purpose: *verify content and brand look before committing to PPTX.*
2. **Phase 2 — Verification gate.** Walk the HTML against the checklist in §6. Fix content/framing in the HTML, re-render, and only pass the gate when every box is checked.
3. **Phase 3 — PowerPoint.** Convert the verified HTML into a **native, editable** `.pptx` on the Caltrans DOE theme — native charts (not images), native text, real slides. QA, then deliver.

**Deck shape (this build):** a **14-slide core deck** followed by a **labeled Appendix pack** (~8 detail slides). Core carries the decision; appendix holds the license/infra breakdown, family briefing, contingencies, sensitivity, ops decomposition, the full figures table, risks, and glossary.

---

## 1. Inputs — the single source of truth (do not re-derive)

Everything below already exists in the repo. Claude design should read these, not invent content or numbers.

| Need | File | Use |
|---|---|---|
| **Slide spec (core)** | `deliverables/deck-goldmaster.md` | The 14-slide blueprint, already corrected to v1.1. This plan's §4 is the authoritative expansion of it. |
| **Numbers (machine-readable)** | `alternates/seven-approach-figures.json` | Every TCO/license/infra/labor figure, the contingencies (GoldenGate, egress), ops decomposition, and the presentation/scope rules. **All chart data comes from here.** |
| **Numbers (Azure 4-option)** | `corpus/figures.json` | Run-cost, elasticity/sensitivity, unit prices for the Azure-only slides. |
| **Prose / framing** | `corpus/content-corpus.md` + `alternates/content-corpus-addendum.md` | Headlines, positioning statements, pillars, soundbites, glossary. Reuse verbatim where marked. |
| **Deliverable targets** | `DELIVERABLES.md` | Audience, format, and the **global consistency rules** — the content invariants in §3 below are drawn from here. |
| **Assumptions & basis** | `model/ASSUMPTIONS.md` (Azure) + `alternates/ASSUMPTIONS.md` (OCI-native & on-prem) | Every volume/compute/storage/bandwidth/labor/license assumption behind the numbers. **Source for the basis slide (14) and the appendix (A5 ops decomposition / A7 risks & assumptions).** |
| **Depth (only if a claim needs backing)** | `proposals/`, `alternates/alternate-*.md`, `alternates/README.md` | Reference only; not slide content. |

**Rule:** if a number on a slide can't be traced to a line in one of the two `figures.json` files, it does not go on the slide.

---

## 2. Brand — apply the Caltrans DOE design system (already built)

The Caltrans DOE design system already exists in Claude design. **Apply it as the active theme; take every visual token from it and introduce nothing off-brand.**

- **Colors:** use the DOE system's primary / secondary / accent / neutral roles. Map deck roles to DOE tokens: dark backgrounds for **title, section dividers, and closing/"reveal" slides** (slides 1, 8, 10, 12); light backgrounds for **content** slides (the sandwich). Section-header accents, callout chips, and card fills all resolve to DOE tokens.
- **Family accent colors (for the three approach families):** assign three distinct DOE-palette hues to **Azure**, **OCI-native**, and **On-premise** and use them consistently on every chart, table row, and legend so a reader learns the color = family mapping once. (In the working draft these were Azure teal / OCI clay / on-prem slate — replace with the DOE equivalents.)
- **Typography:** DOE display face for titles/section heads, DOE body face for content. Respect the DOE type scale (title / section / body / caption). Do not substitute fonts.
- **Charts / data-viz:** use the DOE design system's data-visualization palette for series colors; keep gridlines/axes quiet per the DOE neutrals. One color per approach-family across the whole deck.
- **Logo, footer, spacing, corner treatments:** from the DOE system. Every slide carries the DOE footer lockup (Caltrans Division of Equipment · GreenData Ventures · July 2026 · DRAFT) if the DOE system defines a footer zone.
- **Motif:** commit to one DOE-consistent motif (e.g. the DOE card/chip style) and repeat it; no ad-hoc decoration, no accent stripes or underlines that aren't part of the DOE system.

*If any DOE token is genuinely absent for a needed role (e.g. a third chart-series color), pick the nearest DOE-palette value and flag it in the HTML as a comment for JMS to confirm — never invent a new brand color silently.*

---

## 3. Content invariants — the v1.1 corrections that MUST survive into the deck

These come from the oppositional analysis and JMS's scope clarification. They are already baked into the repo text; the deck must not regress them. Put this list in front of Claude design and check it in Phase 2.

1. **Managed three = a BAND, not a ranking.** Present ADF / Fabric / Databricks ($159k / $203k / $231k) as a band (~$159k–$231k) with ADF at the low edge. Never render them as a clean 1-2-3 ordinal. Only **cross-family** gaps (managed band « OCI-native « roll-your-own « on-prem) are stated as ordered.
2. **OCI-native is compared at BYOL ($233k)** — the like-for-like figure (owned Oracle licenses) — not Lic-Incl ($256k). Show BYOL first.
3. **Azure-over-OCI-native rests on workload isolation + connector breadth, not cost.** The ~$30k gap is not decisive; the decision is architectural (don't run ETL on the ADW that serves reporting).
4. **Scope invariant — BI-platform nativeness is NOT a selection factor.** Every approach lands in Oracle EDW **staging**; Power BI consumes the Oracle EDW downstream of Agiline's aiWorks, invariant across approaches. **Do not present Fabric's Power BI nativeness as a reason to choose it.** Fabric is a cost-only contender.
5. **Two contingencies sit outside the base TCO, both favoring OCI-native:** conditional **GoldenGate** if telematics needs low-latency CDC (~$8k–58k/3yr; every Azure approach; $0 for OCI-native; default P2 batch needs none) and cross-cloud **egress** (~$365/3yr, immaterial in dollars; $0 for OCI-native).
6. **Role chain (keep exact):** Billow lands staging → Agiline's aiWorks loads the EDW running Billow's PL/SQL → Billow consumes the EDW into Power BI. aiWorks is Agiline's product; never say Billow completes the EDW load.
7. **Figures are planning estimates** (state once, on the basis/caveats slide) — enterprise discounts and reservations not applied.

---

## 4. Deck blueprint

Layout patterns referenced below (all realized with DOE tokens): **DARK-TITLE** (full-bleed dark, oversized title), **FLOW** (left-to-right stepped diagram), **CARDS** (2×2 or row of chips), **TABLE**, **BARS** (horizontal), **STACKED** (stacked column), **STAT** (big-number callouts), **SPLIT** (two-column text/visual).

### 4A. Main deck — 14 core slides

| # | Slide | Layout | Headline | Body / data (source) |
|---|---|---|---|---|
| 1 | **Title** | DARK-TITLE | *Feeding the Warehouse* | Sub: "Seven ways to build the data-ingress tier — priced and compared." Family chips (Azure · 4 / OCI-native / On-prem · 2). Accent line: *Recommendation: build on ADF — low edge of the managed cost band, lowest build and labor risk.* |
| 2 | **Positioning** | FLOW | *Azure sits in front of the Oracle EDW — not beside it* | 4-step flow: SOURCES (~30, 3 lanes) → INGEST·CLEANSE·ETL·STAGE (this tier — Billow) → OCI EDW STAGING → AGILINE aiWORKS → EDW → POWER BI. Sub-callout (invariant #4): *BI consumption is downstream and invariant — BI-platform nativeness is not a platform-selection factor.* |
| 3 | **Three lanes** | CARDS (3) | *~30 sources, three connection profiles* | Lane 1 API (ChargePoint·Tesla·GeoTab·AssetWorks·NEE); Lane 2 Internal SSOR (FA+M5·VHSP·Access·SmartSheets·XREF); Lane 3 Other-Dept/CA (CGI·InfoAdvantage·FastTrak·CARB·US Bank·WEX·EJ Ward). Tag: different reach, one clean-and-land pattern. |
| 4 | **Landing contract** | SPLIT | *EDW-ready tables, not raw dumps* | Left: `*_RAW`, `{TYPE}_STG`, `QUAR_`, `XREF_`. Right (dark card): P1 JDBC · P2 Parquet→Object Storage+DBMS_CLOUD (default) · P3 GoldenGate/Data Pump CDC. ERC v3.0 naming. |
| 5 | **Seven approaches** | TABLE | *Seven ways, three families* | Cols: Alt · Approach · Family · Engine · Storage. 7 rows (`seven-approach-figures.json` → approaches). Legend: Alt 0 Azure · 1 OCI-native · 2 on-prem. Family colors. |
| 6 | **3-yr TCO — band, then gaps** | BARS | *A band, not a ranking* | Shade ADF 159 / Fabric 203 / Databricks 231 as ONE band (low→high, ADF at low edge). Then cross-family bars: OCI-native **233 (BYOL)** / 256 (Lic-Incl) · Roll-your-own 388 · On-prem 506 / 506. Callouts (invariants #1, #2): *managed = band, order within it isn't a measurement* · *use OCI-native BYOL for like-for-like.* |
| 7 | **License vs Infra vs Labor** | STACKED | *Where the money actually goes* | Stacked License / Infra / Labor per approach ($k, from figures). Side table: share-of-TCO %. Note: Fabric ≈41% license; roll-your-own ≈2% (90% labor). |
| 8 | **What the split reveals** | CARDS (4, DARK) | *Four things the split shows* | (1) Cloud bundles license, off-cloud itemizes it. (2) On-prem is hardware + people, not license. (3) Oracle EE is the budget hazard. (4) Roll-your-own converts license into payroll. |
| 9 | **The on-prem premium** | STAT | *~3× ADF — and it's not the license* | ADF $159k (Lic $27k / Infra $33k / Labor $99k) ▶ On-prem $506k: Infra/hardware $210k · Labor $237k · License ~$60k (smallest). *License is the smaller part — until Oracle EE.* |
| 10 | **The Oracle EE cliff** | STAT (DARK) | *A single license bigger than the whole cheapest option* | Oracle EE license alone **$315k** > entire ADF option **$159k**. If on-prem Oracle at all, SE2 near-mandatory. |
| 11 | **OCI-native — closer than the headline** | SPLIT | *Why we still choose Azure* | Lead **BYOL $233k** (~$30k above ADF, level with Fabric, below Databricks/roll-your-own). No egress · no landing step · no GoldenGate · one cloud. **Why Azure anyway (invariant #3):** (1) workload isolation — don't run ETL on the ADW that serves reporting; (2) connector breadth for ~30 drifting sources; (3) decoupling + reversibility. A decision on architecture, not cost. |
| 12 | **Recommendation** | CARDS (4, DARK) | *Baseline ADF, graduate, validate, reserve* | Baseline: **ADF** (low edge of band; lightest build; near-zero engine upkeep). Graduate: **Databricks** (telematics/high-volume; incremental). Validate: **Fabric** — PoC on **cost grounds only** (F8-reserved cheapest *if* it tunes; Power BI nativeness not a factor). Reserve: **On-prem** (residency/sovereignty) or revisit **OCI-native BYOL** if single-cloud/data-gravity dominates. |
| 13 | **Next step** | SPLIT | *A 2–3 week, two-feed PoC* | GeoTab telematics (Lane 1) **via the streaming/CDC path — to settle whether GoldenGate is required** + FastTrak/CGI (Lane 3) via P2 → OCI staging, QUAR_/manifest hand-off to Agiline's aiWorks (runs Billow's PL/SQL). Buys: telematics landing cost, real build/ops hours (collapses the band), validated hand-off, parallel Fabric F-SKU trial. |
| 14 | **Basis & caveats** | SPLIT | *What's under the numbers* | Cost basis (live Azure Retail West US 2026-07-22 + 2026 license list). Read managed three as a band. **Contingencies (both favor OCI-native):** GoldenGate if telematics CDC (~$8k–58k/3yr; $0 OCI-native) + egress (~$365/3yr, immaterial). Not applied: enterprise discounts 50–80%, reservations 30–41%. Planning estimates. Reproduce: `seven_approach_cost_model.py`; full assumptions & basis: `model/ASSUMPTIONS.md` (Azure) + `alternates/ASSUMPTIONS.md` (OCI-native & on-prem). |

### 4B. Appendix pack (labeled "Appendix" — after slide 12/13; place the divider before A1)

| # | Slide | Layout | Content (source) |
|---|---|---|---|
| A0 | **Appendix divider** | DARK-TITLE | "Appendix — detail & backup." |
| A1 | **License vs Infrastructure — full breakdown** (D8) | STACKED + TABLE | All 7 approaches stacked License/Infra/Labor + the license/infra/labor 3-yr table + share-of-TCO table + the four findings. Source: `seven-approach-figures.json` + `alternates/README.md` "What the split reveals." |
| A2 | **Approach-family briefing** (D9) | CARDS (3) | The three families — Azure managed / Azure DIY / off-Azure — and when each wins. Source: addendum §C/§D. |
| A3 | **Contingencies — GoldenGate & egress** | TABLE | The two-row contingency table (when it applies · 3-yr cost · OCI-native = $0) + the "only GoldenGate can move a budget" note. Source: `deliverables/cost-onepager.md` Contingencies section + figures `contingencies`. |
| A4 | **Cost elasticity / sensitivity** | BARS | Run cost at 0.5× / 1× / 2× for A/B/C; note pay-per-use scales gently, Fabric capacity in step-functions. Source: `corpus/figures.json` → `sensitivity_run_month`. |
| A5 | **Ops-labor decomposition** | SPLIT | Shared connector-drift (~10 h/mo, constant across approaches) vs engine-upkeep (ADF ~0 / Databricks ~6 / RYO ~30). ADF's edge = "near-zero *engine* upkeep," not lowest total ops. Source: figures `ops_decomposition` + `model/ASSUMPTIONS.md` §6. |
| A6 | **Full seven-approach figures** | TABLE | Every approach: License / Infra / Labor / Capex / Monthly / 3-yr TCO + reference variants (OCI BYOL $233k, Oracle EE $763k, SQL Ent $662k). Source: `seven-approach-figures.json`. |
| A7 | **Risks & assumptions** | CARDS | Azure↔OCI connectivity · landing ownership boundary · VHSP PII · CB-03 · AssetWorks REST limits · Fabric sizing swings ~$60k · telematics volume drives the model · reservations not applied. Source: corpus §11 + `model/ASSUMPTIONS.md` §8 + `alternates/ASSUMPTIONS.md` (load-bearing vs rounding error). |
| A8 | **Glossary & role chain** | SPLIT | Role chain (Billow → Agiline aiWorks → Billow/Power BI) + key terms (aiWorks, Agiline, `*_RAW`/`{TYPE}_STG`/`QUAR_`, DBU, F-SKU, DBMS_CLOUD, GoldenGate). Source: corpus §12 glossary. |

*Speaker notes:* for every slide, add a one-line talking-track note in the notes pane (Phase 3), drawn from the corpus §8 "talk" lines and §9 audience framings.

---

## 5. Phase 1 — HTML proof (content verification)

**Goal:** one self-contained HTML file that renders the whole deck (main + appendix) as sequential 16:9 frames, branded with the DOE design system, so JMS can verify content and look before any PPTX work.

**Instructions to Claude design:**
- Apply the **Caltrans DOE design system** as the active theme (see §2). Pull all colors, type, logo, spacing from it.
- Build **one HTML document**, all CSS/JS inline, no external assets except the DOE logo as a `data:` URI. **No `localStorage`/`sessionStorage`.**
- Render each slide as a **1280×720 (16:9) frame**, stacked vertically with a light gutter, each labeled with its slide number/title so JMS can reference them. A simple sticky mini-nav (jump to slide) is welcome but optional.
- Populate **every** slide from §4 using the repo files in §1. Numbers must match `figures.json` exactly.
- Charts: render as **HTML/SVG** (bars, stacked columns) using the DOE data-viz palette and the family colors. These are a *content proof*, not the final chart — but they must show the right values and the right encoding (band vs ordinal; BYOL vs Lic-Incl).
- Honor **every content invariant in §3.** In particular: slide 6 shows a band (not a 1-2-3 podium); slide 11 leads with BYOL; nothing anywhere sells Fabric on Power BI.
- Where a DOE token had to be approximated, leave an HTML comment `<!-- DOE-CONFIRM: ... -->` so JMS can spot it.

**Ready-to-paste prompt for Phase 1:**
> "Using the Caltrans DOE design system as the active theme, build a single self-contained HTML file that renders this deck as sequential 16:9 slide frames. Follow the build plan's §4 blueprint for every slide (14 core + appendix A0–A8). Pull all copy and numbers from the repo files in §1 — numbers must match `alternates/seven-approach-figures.json` and `corpus/figures.json` exactly. Render charts as inline SVG using the DOE data-viz palette with one consistent color per approach-family. Enforce every content invariant in §3 — especially: the three managed options are a BAND not a ranking (slide 6), OCI-native leads with BYOL $233k (slides 6 & 11), and nothing presents Fabric's Power BI nativeness as a selection reason. No external assets, no browser storage. Add a mini-nav to jump between slides."

**Deliverable of Phase 1:** `ERC_Ingress_Deck_PROOF.html` — JMS opens it and reviews against §6.

---

## 6. Phase 2 — Verification gate (JMS signs off before PPTX)

Do not proceed to PowerPoint until every item passes. Fix in the HTML, re-render, re-check.

**Content & numbers**
- [ ] Every TCO/license/infra/labor figure matches `seven-approach-figures.json`; every run-cost/sensitivity figure matches `corpus/figures.json`.
- [ ] Slide 6 renders the managed three as a **band** (ADF at low edge), not an ordinal podium; cross-family gaps are the only ordered comparison.
- [ ] OCI-native leads with **BYOL $233k** on slides 6 and 11; Lic-Incl $256k shown only as the secondary/no-owned-license case.
- [ ] Slide 11 gives the Azure-over-OCI-native reason as **workload isolation + connector breadth**, not cost.
- [ ] **No slide** presents Fabric's Power BI nativeness as a selection factor; Fabric is framed cost-only.
- [ ] GoldenGate + egress contingencies appear (slide 14 + A3), both marked $0 for OCI-native, GoldenGate flagged as the only budget-mover.
- [ ] Role chain is exact everywhere (Billow stages → Agiline aiWorks loads EDW → Billow → Power BI); Billow never "completes" the EDW load.
- [ ] "Planning estimates; discounts/reservations not applied" stated once (slide 14).

**Brand & layout**
- [ ] Every slide uses DOE tokens only; family colors consistent across all charts/tables; no off-brand color.
- [ ] Dark/light sandwich correct (title/section/reveal dark; content light).
- [ ] No text overflow; ≥ safe margins; no overlapping elements; captions/footers not colliding.
- [ ] All `<!-- DOE-CONFIRM -->` comments resolved.

**Structure**
- [ ] 14 core slides in order, then a labeled Appendix (A0 divider + A1–A8).
- [ ] Speaker-note line drafted for each slide (can be finalized in Phase 3).

---

## 7. Phase 3 — Native PowerPoint production

Once the HTML passes the gate, produce the `.pptx`. **Native, editable — not a screenshot of the HTML.**

**Instructions to Claude design:**
- Build a real `.pptx` on **16:9 (13.33"×7.5")** using the **Caltrans DOE theme** (theme colors/fonts mapped to DOE tokens so the whole deck is restylable from the theme).
- **Charts are native PowerPoint charts** (`addChart` / editable chart objects), one per slide 6, 7, A1, A4 — never rasterized images. Data typed from the figures files. Family colors from the DOE data-viz palette. Titles on, data labels on where it aids reading, quiet gridlines.
- **Text is native text** in real placeholders (editable), not images. Tables are native tables.
- Preserve the exact content that passed Phase 2 — the HTML is the content contract; the PPTX re-expresses it natively, it does not re-write it.
- Put the one-line talking track in each slide's **speaker-notes** pane (not on the slide).
- Footer lockup on every slide per the DOE footer zone.

**Production notes (fidelity — from the pptx skill):**
- Use DOE fonts if they ship with Office; otherwise pair a metric-safe fallback (Calibri/Cambria/Arial) and size containers with ~10% slack so real-PowerPoint rendering doesn't overflow.
- Stacked-column data labels: position `ctr`/`inEnd`/`inBase` only (never `outEnd`).
- No gradient fills via the library (use a DOE solid or a background image); hex colors 6-digit, no `#`, no alpha baked in.
- After generating, validate the file and **render every slide to an image for a visual QA pass** — check overflow, overlaps, contrast, and that charts rendered.

**Ready-to-paste prompt for Phase 3:**
> "Convert the approved HTML proof into a native, editable PowerPoint (16:9) on the Caltrans DOE theme. Map theme colors and fonts to the DOE design-system tokens so the deck is restylable from the theme. Every chart must be a **native PowerPoint chart** (not an image) with data typed from the figures files and family colors from the DOE data-viz palette; all text native and editable; tables native. Keep the content identical to the approved HTML — do not rewrite copy or numbers. Add the one-line talking track to each slide's speaker notes. Then validate the file and render every slide to an image for a visual QA pass, and fix any overflow/overlap/contrast issues in the generator."

---

## 8. QA (before delivery)

- **Content QA:** dump the deck text and re-run the §6 content checklist against the PPTX (numbers can drift in a rebuild).
- **File QA:** validate the `.pptx` (schema/relationships/charts); fix any faults in the generator, not by hand-editing XML.
- **Visual QA:** render all slides to images and inspect each for overflow, overlap, low contrast, misalignment, and that native charts actually rendered. A fresh pair of eyes (or a subagent) reviews the renders.
- **Brand QA:** confirm only DOE tokens are used and family colors are consistent slide-to-slide.

---

## 9. Deliverables & naming

- Phase 1: `ERC_Ingress_Deck_PROOF.html`
- Phase 3: `ERC_Ingress_Deck_v1.pptx` (native, DOE-themed, editable)
- Keep `deliverables/deck-goldmaster.md` as the version-controllable spec; if the deck's content changes during build, update that spec and note it in `CHANGELOG.md`.

---

## 10. One-screen summary for Claude design

1. Theme = **Caltrans DOE design system** (already built) — apply it, use only its tokens.
2. Content + numbers = the **repo** (§1); nothing invented; numbers trace to `figures.json`.
3. Honor the **seven content invariants** (§3) — band-not-ranking, BYOL, workload-isolation, no-Power-BI-selection, GoldenGate/egress, role chain, planning-estimates.
4. Build **HTML proof first** (§5) → **verify** (§6) → **native PPTX** (§7) with native charts and editable text.
5. **QA** (§8), deliver (§9).

*Build plan v1 — 2026-07-23 — John-Michael Scott / GreenData Ventures. Assumes the Caltrans DOE design system is already built in Claude design. Scope: 14-slide core + appendix pack.*

# Azure Data Pipeline Analysis — ERC EDW Ingress

Analysis and proposal for the data-ingress, cleanse, and staging tier that feeds the Caltrans **Equipment Reporting Center (ERC) Enterprise Data Warehouse** (Oracle Autonomous Data Warehouse on OCI). Single source of truth for the analysis and the **connection point for Claude design** to generate downstream deliverables (TL;DRs, executive summaries, analysis pillars, presentations).

> **In one line:** ingest ~30 sources across three lanes, clean them, ETL them into the structures the ERC logical model expects, and land the finished tables into the OCI EDW staging zone — from where Agiline's aiWorks platform loads them into the EDW running Billow's PL/SQL, and Billow then consumes the result into Power BI. This repo evaluates **seven ways to build that tier** (source → staging landing) and prices each with **license and infrastructure as distinct cost items**.

---

## ⭐ Start here

| Alt | Strategy | Approaches | Best 3-yr TCO | Write-up |
|---|---|---|---|---|
| **0** | **Azure** — dedicated tier in front of the EDW | ADF · Databricks · Fabric · Roll-your-own | **$158,994** (ADF) | [`alternates/alternate-0-azure.md`](alternates/alternate-0-azure.md) |
| **1** | **Oracle OCI-native** — API inbound + in-DB ETL | OCI-native | **$232,716** (BYOL) | [`alternates/alternate-1-oci-native.md`](alternates/alternate-1-oci-native.md) |
| **2** | **On-premise** — owned stack, ships to OCI | Oracle DB · SQL Server | **$505,580** | [`alternates/alternate-2-on-premise.md`](alternates/alternate-2-on-premise.md) |

**Recommendation: build on ADF (alt 0).** One-glance map → [`alternates/INDEX.md`](alternates/INDEX.md). Ready-to-use outputs (deck spec, exec summary, cost one-pager, memo, TL;DR) → [`deliverables/`](deliverables). Connecting Claude design? Jump to [How to connect](#how-to-connect-this-repo-from-claude-design).

---

## The seven approaches (three families / three alternate write-ups)

| Alt | # | Approach | Family | 3-yr TCO |
|---|---|---|---|---|
| 0 | 1 | **ADF** | Azure managed | **$158,994** |
| 0 | 3 | **Fabric** | Azure managed | $203,106 |
| 0 | 2 | **Databricks** | Azure managed | $231,072 |
| 1 | 5 | **Oracle OCI-native** | OCI (single-cloud) | $255,900 *(BYOL $232,716)* |
| 0 | 4 | **Roll-your-own** | Azure DIY | $388,152 |
| 2 | 6 | **On-prem Oracle DB (SE2)** | On-premise | $505,580 *(EE $762,856)* |
| 2 | 7 | **On-prem SQL Server (Std)** | On-premise | $505,971 *(Ent $662,487)* |

*Alternate 0 = the Azure family (approaches 1–4); alternate 1 = Oracle OCI-native; alternate 2 = on-premise. Cloud: live Azure Retail (West US, 2026-07-22) + published OCI list. License list prices 2026. Planning estimates; enterprise discounts & reservations not applied. Model: `alternates/seven_approach_cost_model.py`.*

> **Read the numbers as a band, not a ranking.** The three managed options (ADF/Fabric/Databricks) sit in a **~$159k–$231k window that is inside the labor-estimate noise** — ADF is at the low edge, but the order within the trio is not a measurement. Only the **cross-family** gaps (managed band vs OCI-native vs roll-your-own vs on-prem) are decisive. For OCI-native, the like-for-like comparator is **BYOL ~$233k** (you already own Oracle DB licenses for the EDW), not the Lic-Incl $256k. Two contingencies sit *outside* these figures and both favor OCI-native: a conditional **GoldenGate** line if telematics needs CDC (~$8k–58k/3yr; $0 for OCI-native) and cross-cloud **egress** (immaterial in dollars, but zero for OCI-native).

## License vs Infrastructure vs Labor — the requested split

| Approach | License 3yr | Infra 3yr | Labor 3yr | License % |
|---|---|---|---|---|
| 1. ADF | $26,964 | $32,580 | $99,450 | 17% |
| 2. Databricks | $19,512 | $42,660 | $168,900 | 8% |
| 3. Fabric | $84,096 | $12,060 | $106,950 | 41% |
| 4. Roll-your-own | $7,128 | $30,024 | $351,000 | 2% |
| 5. OCI-native (Lic-Incl) | $114,300 | $35,100 | $106,500 | 45% |
| 6. On-prem Oracle SE2 | $58,112 | $210,468 | $237,000 | 11% |
| 7. On-prem SQL Server Std | $66,003 | $210,468 | $229,500 | 13% |

**What it reveals:** license is an explicit SKU off-cloud but bundled into hyperscaler rates (Fabric ≈ all license; roll-your-own trades license for labor). On-prem cost is dominated by hardware + labor, not license — *unless* Oracle Enterprise Edition, whose license alone (~$315k/3yr) exceeds the entire ADF TCO.

> **Scope invariant (important):** whichever approach builds it, this tier's output is **Oracle EDW staging tables**. Power BI consumption is **downstream and invariant** — Agiline's aiWorks loads the Oracle EDW from staging (running Billow's PL/SQL), then Billow consumes the Oracle EDW into Power BI. So **BI-platform "nativeness" (Fabric/OneLake/Power BI) is not an ingress-tier selection factor**; Fabric is judged on cost + Oracle-sink maturity + capacity only.

**Recommendation (unchanged, now with 7 analyses behind it):** build on **ADF** — lowest total cost and lowest labor risk. **OCI-native** is the strongest non-Azure option (data gravity + zero cross-cloud egress, especially BYOL). **On-premise** is justified only by a residency/sovereignty mandate or existing on-prem investment.

---

## Repository map

```
.
├── README.md                        ← overview + index + Claude design connection guide
├── DELIVERABLES.md                  ← spec for the analysis deliverables to build in Claude design
├── CHANGELOG.md                     ← version history (v0.1 → v0.3 → corpus → alternates → deliverables)
├── corpus/
│   ├── content-corpus.md            ← FEED-READY content source of truth (the 4 Azure options)
│   └── figures.json                 ← machine-readable numbers (Azure options)
├── alternates/                      ← three parallel strategy write-ups + the full 7-approach view
│   ├── INDEX.md                     ← one-glance alternate → approaches → TCO map (start here)
│   ├── alternate-0-azure.md         ← Azure family (approaches 1–4): ADF/Databricks/Fabric/Roll-your-own
│   ├── alternate-1-oci-native.md    ← Oracle OCI-native ingress + in-database ETL
│   ├── alternate-2-on-premise.md    ← on-prem stack (SQL Server or Oracle DB); license vs hardware
│   ├── README.md                    ← full 7-approach comparison with license/infra split
│   ├── seven_approach_cost_model.py ← reproducible 7-approach model (license/infra/labor)
│   ├── seven-approach-figures.json  ← machine-readable 7-approach figures
│   └── content-corpus-addendum.md   ← feed-ready content for the 2 new approaches + 7-way view
├── deliverables/                    ← ready-to-use outputs (gold masters for Claude design)
│   ├── deck-goldmaster.md           ← slide-by-slide spec of the 14-slide deck
│   ├── executive-summary.md         ├─ cost-onepager.md
│   ├── recommendation-memo.md       └─ tldr-card.md
├── proposals/
│   ├── proposal-v0.1.md             ← architecture, 3-lane ingress, DQ, OCI landing
│   ├── proposal-v0.2.md             ← three Azure peer pipelines + live-priced cost model
│   └── proposal-v0.3.md             ← roll-your-own + ops-labor verdict
└── model/
    ├── erc_azure_cost_model.py       ← Azure-only bottoms-up model (approaches 1–4)
    └── README.md                     ← how to run and reprice
```

*(The native `ERC_Ingress_GoldMaster_Deck.pptx` is delivered directly, not committed — see `deliverables/README.md`.)*

---

## How to connect this repo from Claude design

1. **Content:** `corpus/content-corpus.md` (Azure options) + `alternates/content-corpus-addendum.md` (OCI-native, on-prem, 7-way).
2. **Numbers:** `corpus/figures.json` + `alternates/seven-approach-figures.json` (includes the license/infra split).
3. **Gold masters to re-skin:** `deliverables/` (deck spec, exec summary, cost one-pager, memo, TL;DR).
4. **Targets:** `DELIVERABLES.md` defines each deliverable's audience, format, and source sections.
5. **Depth / reprice:** `proposals/` + `model/` + `alternates/seven_approach_cost_model.py`.

Rule of thumb: **corpus + addendum for content, the two figures.json for numbers, deliverables for gold masters, proposals/alternates for depth, DELIVERABLES.md for the target.**

---

## What this tier is (and isn't)

An **ingest → cleanse → ETL → stage** tier that lands clean, conformed `*_RAW` + `{TYPE}_STG` + `QUAR_` tables (ERC Naming Standards v3.0) into the OCI EDW staging zone. From there, **Agiline's aiWorks** picks up the staged data and loads it into the EDW, executing **Billow's PL/SQL** scripts; **Billow** then consumes the EDW into Power BI. This tier owns everything up to and including the staging landing — the staging→EDW load is Agiline's job, not Billow's. The landing contract is identical across approaches, so the platform choice is **reversible** — except OCI-native, where ingestion runs *inside* the EDW's cloud and the landing step disappears entirely.

*(aiWorks is Agiline Software's platform; the staging→EDW load is Agiline's job — aiWorks is not a Billow product.)*

---

## Sources

Whimsical "API & SSOR Data Ingress" board; ERC Logical Data Model v1; ERC EDW Unified Logical Architecture v1. Cloud costs from the Azure Retail Prices API; Oracle/Microsoft license figures from 2026 published list prices.

*Maintained by John-Michael Scott (GreenData Ventures). All cost figures are planning estimates pending a PoC.*

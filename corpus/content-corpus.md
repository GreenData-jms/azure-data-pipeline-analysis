# ERC EDW — Azure Data Ingress: Content Corpus

### A single, structured source pack for generating TL;DRs, executive summaries, analysis pillars, and presentation content in Claude design

*Project: Caltrans Division of Equipment — ERC EDW · Consolidates proposal v0.1–v0.3 + live-priced cost model · July 2026 · John-Michael Scott*

---

## 0. How to use this corpus (read me first)

This file is a **content source of truth**, not a finished artifact. It is organized so you can feed the whole thing (or one section) into Claude design and ask for a specific output. Everything downstream should trace back to a block here so figures and framing stay consistent.

**Companion file:** `figures.json` — every number in machine-readable form. Feed it alongside this corpus when you want exact figures.

**Suggested prompts once this corpus is loaded:**
- *"Using the corpus, write a 1-slide TL;DR for the steering committee."* → pull §5 + §6.
- *"Build a 5-slide executive summary deck."* → pull §6 + §8 + §9-exec.
- *"Draft the 'analysis pillars' section — one visual per pillar."* → pull §7.
- *"Write a 1-page technical brief for the EDW architecture team."* → pull §4 + §7 + §9-technical.
- *"Make a cost-comparison slide with the four-way table."* → pull §4.5 + figures.json.

**Consistency rules for any generated artifact:** cost figures are *planning estimates* (state it once); Azure is a *staging tier in front of* the Oracle EDW (never a replacement); the four options are *peers* on capability and differ on cost/effort/fit; the DIY verdict is *cheapest to run, most expensive to own*. **Role chain (keep exact): Billow lands staging → Agiline's aiWorks loads the EDW running Billow's PL/SQL → Billow consumes into Power BI. aiWorks is Agiline's product; never say Billow completes the EDW load.**

**Scope invariant (keep exact):** every approach lands in the Oracle EDW **staging** zone; Power BI consumption is **downstream and invariant** (aiWorks loads the Oracle EDW from staging; Billow consumes the Oracle EDW into Power BI). So **BI-platform "nativeness" (Fabric/OneLake/Power BI) is NOT a selection factor** — never present it as a reason to prefer or rank an approach; judge Fabric on cost + Oracle-sink maturity + capacity only.

**Cost-framing rules (keep exact):** (a) present the three managed options as a **BAND ~$159k–$231k** (ADF at the low edge), *not* an ordinal ranking — the order within the trio is inside the labor-estimate noise; only cross-family gaps are decisive. (b) Compare **OCI-native at BYOL ~$233k** (owned Oracle licenses), not Lic-Incl $256k; prefer Azure over it on **workload isolation + connector breadth**, not TCO. (c) Two contingencies sit **outside** the base TCO and both favor OCI-native: conditional **GoldenGate** if telematics needs CDC (~$8k–58k/3yr; every Azure approach; $0 for OCI-native) and cross-cloud **egress** (immaterial dollars; $0 for OCI-native).

---

## 1. One-paragraph project context

The ERC Enterprise Data Warehouse is an Oracle Autonomous Data Warehouse on OCI, built as a four-workstream medallion (Bronze → Silver → Gold). Billow lands the staged data (this proposal's tier); then **Agiline's aiWorks** picks it up and loads it into the EDW (Silver/Gold), executing Billow's PL/SQL scripts; Billow then consumes the EDW into Power BI. This work designs the **upstream half** of the Whimsical "API & SSOR Data Ingress" board: an **Azure platform that ingests ~30 heterogeneous sources across three lanes, cleans them, ETLs them into the structures the logical model expects, and lands the finished table set into the OCI EDW Bronze/landing (staging) zone** where Agiline's aiWorks takes over. The proposal evaluates four ways to build that Azure tier and prices them bottoms-up on live Azure retail rates.

---

## 2. The core framing (positioning statements — reuse verbatim)

- **Azure is an ingestion, quality, and staging tier that sits *in front of* the Oracle EDW — not a competing warehouse.** Its job (Billow's, via this tier) is to land clean, conformed tables in the OCI staging zone — from which Agiline's aiWorks loads them into the EDW using Billow's PL/SQL, before Billow consumes the EDW into Power BI.
- **One contract line divides the world:** everything from source to the OCI Bronze landing is Azure's responsibility (this proposal); after that, Agiline's aiWorks loads staging into the EDW (Silver/Gold) running Billow's PL/SQL, and Billow consumes the EDW into Power BI. Because the contract is identical across every option, the platform choice is **reversible**.
- **The board asked two governing questions** we treat as first-class: *"Clarity of Reasoning"* (every choice justified) and *"Evaluate the cost profile of each approach — 3 to 5 best choices we can all look at."* This corpus answers both.
- **The decision is not "which is cheapest to run."** At this scale the managed options run within a narrow band; what separates them is build effort, operating model, cost elasticity, and — for roll-your-own — the labor you permanently absorb. (Note: BI-platform fit is *not* a separator — every approach lands in Oracle staging and Power BI consumes the Oracle EDW downstream, invariant across approaches.)

---

## 3. The requirement, in one table (traceability)

| # | Requirement | How it is met (all options) |
|---|---|---|
| R1 | Ingest External API + Internal + External-CA-Dept data | Three-lane ingress design |
| R2 | A pipeline platform + 2 other ingress techniques | Each option names a pipeline engine + 2 techniques |
| R3 | Fit-for-purpose storage (SQL or document) | Relational-by-default; NoSQL/JSON only where payloads drift |
| R4 | Data cleanup / DQ | Shared validate→dedup→XREF→rules→quarantine framework |
| R5 | ETL to the logical-model table set | Produce `*_RAW` + `{TYPE}_STG` per ERC Naming Standards v3.0 |
| R6 | Land into the OCI EDW staging/landing zone | Three landing patterns to `ERC_*_BRZ` |
| R7 | Cost profile of 3–5 approaches | Live-priced bottoms-up model, four variants |
| R8 | Clarity of reasoning | "Why" behind every choice; decision matrix |

---

## 4. Master fact base (single source of truth)

### 4.1 The three ingress lanes and their sources

- **Lane 1 — External API** (internet REST/JSON-RPC/OAuth; needs custom connectors): ChargePoint EV API, Tesla REST API, GeoTab JSON-RPC, AssetWorks REST API v25.4 (IAsset, IWorkOrder, IPurchaseOrder, IAccident…), NEE App API.
- **Lane 2 — Internal SSOR** (Caltrans-internal/on-prem; needs private reach): FA raw tables (EQ_MAIN, EQ_COST_DATA, JOB_MAIN…), M5 ODS VX_ views (VX_ASSET, VX_BILLING, VX_ACCIDENT), VHSP MySQL, Access FAP DB, Access Hardware DB, SmartSheets + MS Project, 6 XREF bridge tables.
- **Lane 3 — Other-Dept / External California SSOR** (inter-agency batch/file/SFTP): CGI Advantage (encumbrances/GL), InfoAdvantage OE/PS xlsb, FastTrak toll extract (CSV + Access), CARB DB extract, US Bank SFTP, WEX SFTP, EJ Ward / AGWorks XLSX.
- **Why the split matters:** the three lanes have different connection and trust profiles (custom API auth vs. private-network reach vs. scheduled inter-agency file pickup + code reconciliation). Every option handles all three; they differ only in the tooling per lane.

### 4.2 The landing target (what "EDW-ready" means)

Azure output slots into the Oracle **Bronze** layer: `*_RAW` (immutable, append-only source extracts, no business logic) and `{TYPE}_STG` (validated, typed, deduplicated staging — e.g. `F_FUEL_TRANSACTION_STG`, `D_ASSET_STG`), plus `QUAR_` quarantine (rejected rows with `REJECT_REASON`) and `XREF_` code bridges (CGI Advantage ↔ AssetWorks). Naming follows **ERC Naming Convention Standards v3.0**: `_KEY` surrogate PK/FK, `_IDENTIF` degenerate natural key, `_CODE` lookup natural key, layer conveyed by *schema name only*, ≤30-char Oracle-safe identifiers.

### 4.3 The three OCI landing patterns (one contract)

- **P1 — Direct JDBC/Oracle sink:** write rows straight into `ERC_*_BRZ`. Best for small–medium batch; native in ADF.
- **P2 — Object Storage + external tables:** write Parquet/CSV to OCI Object Storage; Oracle `DBMS_CLOUD`/external tables ingest. Best for bulk, replayability, decoupled cadence. *Recommended default for most feeds.*
- **P3 — GoldenGate / Data Pump CDC:** stream changes. Reserve for telematics-class volume. **Cost caveat:** GoldenGate is separately licensed and is *not* in the base TCO — if the telematics lane truly needs low-latency CDC, add ~$8k (OCI-managed BYOL) / ~$35k (OCI-managed Lic-Incl) / ~$58k (perpetual) over 3yr. It applies to every Azure approach equally and is **$0** for OCI-native (in-database CDC). The default for most feeds is P2, which needs no GoldenGate. "Does telematics require P3?" is a PoC exit question.
- **Connectivity:** prefer the Azure–OCI Interconnect / Oracle Database@Azure for private, egress-optimized transfer; else private endpoint + wallet over TLS.

### 4.4 The four variants (capsule specs)

| | **A — ADF** | **B — Databricks** | **C — Fabric** | **D — Roll-your-own** |
|---|---|---|---|---|
| One-liner | Managed PaaS pipeline, lowest ops | Medallion mirrored in Azure with Spark | Unified SaaS, single capacity bill | Build ADF's job from raw primitives |
| Pipeline engine | Azure Data Factory | Databricks Workflows (+ADF copy) | Fabric Data Factory | Azure Durable Functions |
| Technique #2 | Azure Functions | Event Hubs | Dataflows Gen2 | Per-source Function handlers |
| Technique #3 | Logic Apps | Auto Loader / notebooks | Fabric Notebooks | Container Apps Jobs |
| Cleanse/ETL engine | Mapping Data Flows + SQL | PySpark / Delta Live Tables | Power Query + Notebooks | Python in Container Apps |
| Conformed store | Azure SQL (+Cosmos for JSON) | ADLS Gen2 Delta (+thin SQL) | Fabric Warehouse/Lakehouse | Azure SQL + ADLS |
| Commercial model | Pay-per-use | DBU consumption | Fixed capacity (F-SKU) | Serverless primitives |
| Strategic role | **Baseline** | Graduation target (heavy/streaming) | PoC option (cost-only; F8 if tuned) | Cautionary comparator |

### 4.5 The cost numbers (all from the live-priced model)

**Steady-state monthly run cost:** A $1,654 · B $1,728 · C $2,670 (F16 PAYG) / $1,024 (F8 reserved) · **D $1,032 (cheapest to run).**

**Four-way total (the honest view, incl. ongoing ops labor @ $150/hr):**

| Option | Run $/mo | Ops labor $/mo | Run+Ops $/mo | One-time build | 3-yr TCO (w/ ops) |
|---|---|---|---|---|---|
| A — ADF | $1,654 | $1,200 (8 h/mo) | **$2,854** | ~$56k (375 h) | **~$159k** |
| B — Databricks | $1,728 | $2,400 (16 h/mo) | $4,128 | ~$83k (550 h) | ~$231k |
| C — Fabric (F16) | $2,670 | $1,200 (8 h/mo) | $3,870 | ~$64k (425 h) | ~$203k |
| D — Roll-your-own | **$1,032** | $6,000 (40 h/mo) | $7,032 | ~$135k (900 h) | **~$388k (~2.4× ADF)** |

**Cost elasticity (run cost at 0.5× / 1× / 2× volume):** A $1,488 / $1,654 / $1,989 · B $1,583 / $1,728 / $2,021 · C $1,496 (F8) / $2,670 (F16) / $5,023 (F32). *Pay-per-use (A, B) scales gently; capacity (C) scales in step-function jumps.*

**Cost basis:** live Azure Retail Prices, West US, PAYG, pulled 2026-07-22. Planning estimates on documented volumes; reservations (−30–41%) not in baseline. Model: `erc_azure_cost_model.py` (edit assumptions, re-run to reprice).

### 4.6 Key unit prices (illustrative, live)

ADF Mapping Data Flow $0.26975/vCore-hr · Databricks Jobs (Premium/Photon) $0.30/DBU-hr (on top of VM D4s_v5 $0.224/hr) · Fabric $0.20/CU-hr (F16 PAYG $2,336/mo; reserved ×0.59) · Azure SQL GP 4-vCore $0.67/hr · Container Apps $0.000024/vCPU-s (~$0.086/vCPU-hr) · Functions Consumption $0.20/M exec · ADLS Gen2 hot $0.021/GB-mo · egress $0.08/GB.

### 4.7 The data-quality / cleanup framework (identical across options)

Validate (schema/type/range, API drift) → dedup & canonical-record selection (e.g. multi-source fuel WEX+US Bank+EJ Ward → one canonical row) → reference/XREF reconciliation (CGI↔AssetWorks codes) → business-rule DQ → route rejects to `QUAR_*` with `REJECT_REASON` (non-blocking gate) → SCD2 change-detection prep (D_ASSET ⚠CB-03, D_VEHICLE, D_EV_STATION…) → PII masking (VHSP names, pending IT Security) → name/type to ERC v3.0.

---

## 5. TL;DR blocks (ready to drop in)

**One-liner:** *Build the Azure ingest-and-staging tier on ADF — it isn't the cheapest to run, but it's the cheapest to own, and it's the lowest-risk path to landing clean data in the OCI EDW.*

**Tweet-length (~40 words):** *Four ways to feed the ERC EDW from Azure. At our scale the managed options run within ~$1.5–2.7k/mo, so effort and fit decide. Roll-your-own is cheapest to run but ~2.4× the 3-yr cost once you count the maintenance labor. Recommendation: ADF.*

**Three-sentence:** *Azure will ingest ~30 sources across three lanes, clean them, and land EDW-ready tables into the OCI staging zone, from which Agiline's aiWorks (running Billow's PL/SQL) loads the EDW. We priced four build options on live Azure rates: ADF, Databricks, Fabric, and roll-your-own — and found the managed three cost about the same to run, so the decision turns on build effort, operations, and fit, not the monthly bill. We recommend ADF as the baseline (lowest ops, most mature Oracle sink), graduating heavy workstreams to Databricks where volume warrants and validating Fabric via a short PoC.*

**One-paragraph:** *This proposal designs the Azure half of the ERC data-ingress model: a tier that sits in front of the Oracle OCI EDW, ingesting External-API, internal, and other-department California data across three lanes, cleaning it, and landing conformed `*_RAW`/`{TYPE}_STG` tables into the EDW's staging zone, from which Agiline's aiWorks loads the EDW using Billow's PL/SQL. We evaluated four build options against a live-priced, reproducible cost model. The headline: at documented mid-size volume the three managed platforms (ADF, Databricks, Fabric) run within roughly $1,500–$2,700/mo of each other, so run cost is not the differentiator — build effort, operating model, and cost elasticity are (BI-platform fit is not, since BI consumes the Oracle EDW downstream, invariant across approaches). Rolling your own from serverless primitives is the cheapest to run (~$1,032/mo) but the most expensive to own (~$388k over three years, ~2.4× ADF) once you price the ~900-hour build and ~40 hrs/month of permanent maintenance. Recommendation: build on ADF, keep the landing contract designed so heavy/streaming workstreams can graduate to Databricks without re-platforming, and run a scoped Fabric PoC before any capacity commitment.*

---

## 6. Executive summary (ready-to-use, ~1 page)

**Situation.** The ERC EDW (Oracle ADW on OCI, four-workstream medallion) needs a reliable upstream tier that turns ~30 heterogeneous sources — vendor APIs, internal databases, and other California department systems — into clean, conformed, EDW-ready tables and lands them in the OCI staging zone. From there, Agiline's aiWorks loads them into the EDW executing Billow's PL/SQL scripts, and Billow consumes the EDW into Power BI. This is the Azure "ingest → cleanse → ETL → stage" platform from the API & SSOR Data Ingress concept.

**What we evaluated.** Four ways to build it, each independently capable of the full job: **(A) Azure Data Factory** (managed PaaS pipeline), **(B) Azure Databricks** (Spark lakehouse), **(C) Microsoft Fabric** (unified SaaS), and **(D) roll-your-own** (the same capabilities hand-assembled from Azure Functions and Container Apps). Every option ingests the three lanes, cleans the data, ETLs it to the logical model, and lands to Oracle through the same contract — so the choice is reversible.

**What we found.** Costs were built bottoms-up from live Azure retail prices. At the documented workload, the three managed platforms run within a narrow band (~$1,500–$2,700/mo), so the differentiator is build effort, operations, and fit — not the monthly bill. Roll-your-own is the cheapest to run (~$1,032/mo) but the most expensive to own: once the ~900-hour build and ~40 hrs/month of ongoing maintenance are counted, its three-year total (~$388k) is roughly 2.4× ADF's (~$159k). Managed platforms convert that permanent labor liability into a small, supported run cost.

**Recommendation.** Build on **ADF** — lowest ops, most mature Oracle sink, gentlest cost elasticity if volumes grow. Design the landing contract and lake so heavy/streaming workstreams (telematics, high-volume ops) can **graduate to Databricks** patterns incrementally. Keep **Fabric** as a cost-only option — its F8-reserved total is the lowest of all *if* the workload tunes to fit — validated by a short PoC (not chosen for Power BI fit: BI consumption is downstream of aiWorks on the Oracle EDW and invariant across approaches). Where a single step is expensively served by a Data Flow, drop a Function or Container Apps Job under ADF's orchestration to capture roll-your-own's serverless savings without owning a framework.

**Next step.** A 2–3 week PoC landing two contrasting feeds end-to-end into OCI Bronze — GeoTab telematics (Lane 1: custom auth + streaming) and FastTrak or CGI Advantage (Lane 3: SFTP + XREF reconciliation) — with the `QUAR_`/manifest handoff to Agiline's aiWorks (which loads the EDW with Billow's PL/SQL). This converts every estimate to a committed number and de-risks the platform choice with data.

---

## 7. Analysis pillars (the load-bearing arguments — one per section/visual)

Each pillar = a claim + the evidence + the "so what." Use these as the backbone of a deck or an analysis doc.

**Pillar 1 — Azure is a staging tier, not a second warehouse.**
Claim: Azure's role is bounded — ingest, clean, stage, land — and stops at the OCI Bronze contract line.
Evidence: the medallion target is Oracle; Agiline's aiWorks (running Billow's PL/SQL) loads Silver→Gold and Billow consumes into Power BI; the landing contract (`*_RAW`/`{TYPE}_STG`/`QUAR_`, ERC v3.0 naming) is identical across all options.
So what: keeps scope crisp, avoids duplicating the warehouse, and makes the platform choice reversible.

**Pillar 2 — Three lanes, one contract.**
Claim: the ~30 sources cluster into three lanes with distinct connection/trust profiles, but all converge on one clean-and-land pattern.
Evidence: Lane 1 API (custom auth), Lane 2 internal (private reach), Lane 3 other-dept (scheduled file + code reconciliation); all → validate/dedup/quarantine → OCI Bronze.
So what: one reusable framework covers everything; per-lane tooling is a detail, not a re-architecture.

**Pillar 3 — At this scale, managed run costs converge.**
Claim: ADF, Databricks, and Fabric run within ~$1,500–$2,700/mo — the "Spark premium" and "capacity bill" mostly evaporate when sized lean.
Evidence: A $1,654 · B $1,728 · C $1,024–$2,670 (sizing-dependent).
So what: don't pick on run cost; pick on build effort, ops, and fit.

**Pillar 4 — Roll-your-own is cheapest to run, most expensive to own.**
Claim: DIY wins the Azure bill and loses the total by a wide margin.
Evidence: run $1,032/mo (cheapest) but +$6,000/mo ops labor and $135k build → ~$388k 3-yr TCO (~2.4× ADF). The ~$7.5k/yr compute saving is erased ~8× over by ~$57.6k/yr of maintenance.
So what: managed platforms convert a permanent labor liability into a supported run cost; DIY only wins if that labor is free/sunk and sources are stable — unlikely at Caltrans scale.

**Pillar 5 — Cost elasticity differs by commercial model.**
Claim: how each option's bill responds to growth matters more than today's number if volumes are uncertain.
Evidence: at 2× load, A/B rise ~20–30% (pay-per-use) while Fabric triples via step-function capacity jumps (F16→F32).
So what: pay-per-use is safer under volume uncertainty; capacity is cheapest only when tuned to fit a small SKU.

**Pillar 6 — The recommended path is layered, not monolithic.**
Claim: baseline + graduation + PoC + a serverless middle path beats a single all-or-nothing bet.
Evidence: A and B share ADLS Gen2 and an identical landing contract (incremental graduation); Fabric F8-reserved is lowest-TCO *if* validated; ADF can orchestrate Functions/Container Apps for cheap serverless on expensive steps.
So what: capture each option's genuine strength while keeping ADF's low ops and reversibility.

---

## 8. Presentation outline (slide-by-slide raw content)

Matches the Caltrans ERC unified-architecture deck style. Each slide: **title · headline assertion · body content · data · talking-track note.**

1. **Title** — *Azure Data Ingress for the ERC EDW* / "Four ways to feed the warehouse — priced and compared" / Caltrans Division of Equipment · July 2026 · Draft.
2. **The picture** — *Azure sits in front of the Oracle EDW.* Body: the source→Azure (Billow staging)→OCI staging→Agiline aiWorks→EDW→Billow Power BI flow diagram. Talk: one contract line; everything left is this proposal.
3. **The three lanes** — *~30 sources, three connection profiles.* Body: Lane 1 API / Lane 2 internal / Lane 3 other-dept with example sources. Data: the source list. Talk: different reach, same clean-and-land pattern.
4. **The landing contract** — *We deliver EDW-ready tables, not raw dumps.* Body: `*_RAW`/`{TYPE}_STG`/`QUAR_`; three landing patterns P1/P2/P3; ERC v3.0 naming. Talk: this is what makes the platform choice reversible.
5. **Four ways to build it** — *All capable; they differ on model.* Body: the §4.4 capsule table. Talk: peers on capability, not on cost/effort.
6. **What each costs to run** — *Managed options run close together.* Data: run-cost bar (A $1,654 / B $1,728 / C $1,024–2,670 / D $1,032). Talk: run cost is not the differentiator.
7. **The honest total** — *Cheapest to run ≠ cheapest to own.* Data: the four-way run+ops+build+TCO table (§4.5). Talk: DIY flips from cheapest to most expensive.
8. **Why DIY loses** — *You become the pipeline vendor.* Data: $7.5k/yr saved vs $57.6k/yr maintenance + $79k build. Talk: paying an engineer to rebuild and forever maintain what Microsoft runs for a few hundred a month.
9. **Cost elasticity** — *How the bill grows matters.* Data: the 0.5×/1×/2× sensitivity table. Talk: pay-per-use scales gently; capacity jumps in steps.
10. **Recommendation** — *ADF baseline, graduate to Databricks, PoC Fabric.* Body: the layered path + the serverless middle option. Talk: capture each strength, keep low ops + reversibility.
11. **Next step** — *A 2–3 week, two-feed PoC.* Body: GeoTab telematics + FastTrak/CGI Advantage → OCI Bronze with QUAR_/manifest handoff. Talk: converts estimates to committed numbers.
12. **Appendix** — cost basis, unit prices, assumptions, risks (VHSP PII, CB-03, connectivity, Fabric sizing).

---

## 9. Audience-tailored framings of the core message

- **Executive / stakeholder:** *"Four options; the managed three cost about the same to run, so we pick on risk and effort. Recommendation: ADF — lowest operating burden, cleanest path to the Oracle warehouse, and it keeps our options open. Building it ourselves would be cheaper on the Azure bill but roughly 2.4× the total once you count the engineering to maintain it."*
- **Decision-maker / budget owner:** *"Run cost lands ~$1.5–2.7k/mo across the managed options; the real spread is in build (375–900 hrs) and ongoing ops (8–40 hrs/mo). ADF minimizes both. Roll-your-own's 3-yr TCO is ~$388k vs ADF's ~$159k — the difference is labor, not cloud."*
- **Technical / architecture team:** *"All four satisfy R1–R6 and share the DQ framework and the OCI landing contract. ADF: Mapping Data Flows + Functions + Logic Apps + SHIR, native Oracle sink. Graduation to Databricks (Event Hubs + Structured Streaming + DLT) is incremental because A and B share ADLS Gen2 and the contract. DIY (Durable Functions + Container Apps) is architecturally clean and cheap to run but concentrates maintenance and key-person risk."*

---

## 10. Quotable lines & analogies (soundbites)

- "Cheapest to run, most expensive to own."
- "Managed platforms convert a permanent labor liability into a supported run cost."
- "You'd be paying a senior engineer to rebuild — and then forever maintain — a product Microsoft already operates for a few hundred dollars a month."
- "Run cost is not the differentiator at this scale; effort, operations, and fit are."
- "One contract line makes the whole choice reversible."
- "Pay-per-use scales gently; capacity scales in cliffs."
- "We deliver EDW-ready tables, not raw dumps."
- "The ~$7,500/year you'd save on compute is erased about eight times over by the ~$57,600/year of engineering you'd absorb."

---

## 11. Risks & open items (carry into any deliverable)

Azure↔OCI connectivity (Interconnect / Oracle Database@Azure vs private endpoint) — affects egress + latency · Landing ownership boundary (does Billow want `{TYPE}_STG` or only `*_RAW`?) · VHSP PII masking (pending IT Security) · CB-03 (D_ASSET AcquisitionDate from VX_ASSET/REST, not FA EQ_MAIN) · AssetWorks REST rate limits/pagination · Access DB (FAP/Hardware) reachability + cadence · XREF pre-loads (D_UNIT_SHOP) · Fabric capacity sizing (F8 vs F16 swings 3-yr TCO ~$60k) · Cost figures are planning estimates pending PoC · Ops-labor hours are the load-bearing DIY assumption — adjustable in the model.

---

## 12. Glossary

**SSOR** (Source) System of Record · **Medallion** Bronze/Silver/Gold layering · **SCD2** history-preserving dimension · **`*_RAW`** immutable source extract (Bronze) · **`{TYPE}_STG`** validated staging table · **`QUAR_`** quarantine (rejected rows + reason) · **`XREF_`** code-reconciliation bridge · **aiWorks** Agiline Software's platform that picks up the staged data and loads it into the EDW, executing Billow's PL/SQL scripts (this staging→EDW load is Agiline's job) · **Agiline** the party that completes the staging→EDW load via aiWorks · **Billow** lands data in staging (this proposal's tier), provides the PL/SQL scripts aiWorks runs, and consumes the EDW into Power BI · **SHIR** Self-Hosted Integration Runtime (ADF private connector host) · **DIU** Data Integration Unit (ADF copy compute) · **DBU** Databricks Unit (consumption) · **F-SKU / CU** Fabric capacity SKU / Capacity Unit · **`DBMS_CLOUD`** Oracle package to load from object storage · **Durable Functions** Azure serverless orchestration · **Container Apps Jobs** serverless container batch compute · **GoldenGate** Oracle change-data-capture (CDC) replication — separately licensed; only needed for a low-latency telematics landing (P3), not the default batch path; $0 for OCI-native (in-database).

---

## 13. Provenance

Consolidates: proposal v0.1 (architecture, lanes, DQ, landing patterns), v0.2 (peer pipelines, capability parity, live-priced cost model, sensitivity), v0.3 (Variant D roll-your-own, ops-labor TCO lens, verdict). Sources: Whimsical "API & SSOR Data Ingress" board; ERC Logical Data Model v1; ERC EDW Unified Logical Architecture v1. Cost: Azure Retail Prices API, West US, PAYG, 2026-07-22; reproducible via `erc_azure_cost_model.py`. Numbers mirror `figures.json`.

---

*ERC Azure Data Ingress — Content Corpus v1 — July 2026 — John-Michael Scott. Feed with `figures.json`. All figures are planning estimates pending PoC.*

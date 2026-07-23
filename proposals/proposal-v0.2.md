# Azure Data Ingress, Cleanse & Staging Platform for the ERC EDW

### v0.2 — Three peer data-flow pipeline platforms, evaluated head-to-head, with a live-priced bottoms-up cost model

*Prepared for: Caltrans Division of Equipment — ERC EDW Project · Audience: EDW architecture team + program decision-makers*

---

## 1. What changed in v0.2 and why

v0.1 treated ADF as the anchor with two supporting *techniques*. v0.2 reframes the decision as a choice among three *peer pipeline platforms* — each independently and equally capable of the full job (ingest three lanes, clean, ETL to the logical model, land into OCI Bronze). v0.2 replaces v0.1's relative cost tiers with a **reproducible, live-priced bottoms-up cost model** (Azure Retail Prices, West US, pulled 2026-07-22).

**The three peers:** **ADF** (managed PaaS pipeline; pay-per-use), **Databricks** (Spark lakehouse; DBU consumption), **Fabric** (unified SaaS; fixed capacity). Co-equal on capability; they differ on commercial model, build effort, and operating fit.

### 1.1 Headline finding

At the documented mid-size Caltrans volume, steady-state monthly run costs land in a narrow band (~$1,500–$2,700/mo) because the workload is batch-dominated and modest.

| Peer | Steady-state run (PAYG) | Optimized | One-time build | 3-yr TCO (run + build) |
|---|---|---|---|---|
| A — ADF | ~$1,650/mo | ~$1,500 (no Cosmos) | ~375 hrs / ~$56k | ~$116k |
| B — Databricks | ~$1,730/mo | lower w/ spot + DBCU commit | ~550 hrs / ~$83k | ~$145k |
| C — Fabric | ~$2,670/mo (F16 PAYG) | ~$1,024/mo (F8 reserved) | ~425 hrs / ~$64k | ~$100k–160k |

The decision is not "which is cheapest to run" — they're close. It's build effort and Spark skill (ADF lowest, Databricks highest), Fabric's flat capacity + Power BI fit, and future scale.

---

## 2. Scope recap (condensed; see v0.1)

Azure is an ingest → cleanse → ETL → stage tier in front of the Oracle OCI EDW. Three lanes (External API / Internal SSOR / Other-Dept SSOR), ~30 sources. Landing contract identical across peers: `*_RAW` + `{TYPE}_STG` + `QUAR_` to `ERC_*_BRZ`, ERC v3.0 naming, via P1 (JDBC) / P2 (Object Storage + `DBMS_CLOUD`) / P3 (GoldenGate). Identical contract → reversible choice. (Downstream of the landing, Agiline's aiWorks loads the EDW running Billow's PL/SQL, and Billow consumes the EDW into Power BI.)

---

## 3. The three peer pipeline platforms

| Responsibility | A — ADF | B — Databricks | C — Fabric |
|---|---|---|---|
| Orchestration | ADF pipelines | Databricks Workflows (+ADF copy) | Fabric Data Factory |
| Lane-1 API | Azure Functions | Auto Loader + notebooks | Fabric Notebooks |
| Lane-2 private | Self-Hosted IR | Self-Hosted IR | On-Prem/VNet Gateway |
| Lane-3 file/SFTP | Logic Apps | Auto Loader / ADF | Dataflows Gen2 |
| Streaming | (batch; EH optional) | Event Hubs + Structured Streaming | Eventstream |
| Cleanse/ETL | Mapping Data Flows + SQL procs | PySpark / DLT | Dataflows Gen2 (Power Query) + Notebooks |
| Conformed store | Azure SQL DB/MI (+Cosmos) | ADLS Gen2 Delta (+thin SQL) | Fabric Warehouse/Lakehouse |
| Land to OCI | ADF Oracle sink (P1/P2) | Spark JDBC / Parquet (P1/P2/P3) | Fabric Copy / Parquet (P1/P2) |
| Commercial model | Pay-per-use | DBU consumption | Fixed capacity (F-SKU) |

**3.1 Why these three (price-vs-objective):** ADF = floor on build/ops + mature Oracle sink (low-effort/low-cost anchor); Databricks = max capability (SCD2, streaming, ML runway); Fabric = best ecosystem fit for a Power BI-first shop + predictable capacity bill. Rejected: Synapse (same engine as ADF), Airflow+dbt (OSS labor cost), Matillion/Fivetran (license + less control). Note: Fabric's pipeline engine descends from ADF; it earns peer status on commercial model, OneLake, and Power BI nativeness.

---

## 4. Capability parity — all three meet every requirement

| Requirement | A | B | C |
|---|:--:|:--:|:--:|
| R1 Ingest 3 lanes | ✓ | ✓ | ✓ |
| R2 Pipeline + 2 techniques | ✓ | ✓ | ✓ |
| R3 Storage (SQL/doc) | ✓ | ✓ | ✓ |
| R4 Cleanup/DQ/quarantine | ✓ | ✓ | ✓ |
| R5 ETL to model | ✓ | ✓ | ✓ |
| R6 Land to OCI Bronze | ✓ (native sink) | ✓ | ✓ (validate in PoC) |
| SCD2/complex | good | best | good |
| Streaming | optional | native | Eventstream |
| Low-code/analyst | ◐ | ○ | ✓ Power Query |
| Power BI fit | ◐ | ◐ | ✓ native |

DQ framework identical (validate→dedup→XREF→rules→`QUAR_`→SCD2 prep→PII→ERC v3.0); only the engine differs.

---

## 5. Comparable cost model (live-priced, bottoms-up)

**5.1 Method.** Bottoms-up from Azure Retail unit prices (West US, PAYG, 2026-07-22) applied to explicit editable volume assumptions. Full model: `erc_azure_cost_model.py`.

**5.2 Live unit prices (illustrative):** ADF orchestration $1/1k runs · ADF cloud copy $0.25/DIU-hr · ADF Mapping Data Flow GP $0.26975/vCore-hr · Databricks Jobs Premium/Photon $0.30/DBU-hr · VM D4s_v5 $0.224/hr · Fabric $0.20/CU-hr (F8 $1,168/F16 $2,336 PAYG; reserved ×0.59) · Azure SQL GP 4-vCore $0.6698/hr · ADLS Gen2 hot $0.021/GB-mo · OneLake hot $0.026/GB-mo · egress $0.08/GB · Event Hubs TU $0.03/hr.

**5.3 Volume assumptions.** ~30 sources; ~3,000 activity runs/mo; ~75 GB/mo steady ingest; ~500 GB resident lake; ~50 GB staging; ~30M telematics events/mo; ~120 transform cluster-hours/mo; ~1.5 TB one-time backfill. Build: ADF 375h · Databricks 550h · Fabric 425h @ $150/hr.

**5.4 Per-peer monthly.** A ~$1,654/mo ($1,504 without Cosmos); B ~$1,728/mo; C ~$2,670/mo (F16 PAYG) or ~$1,024/mo (F8 reserved).

**5.5 Build & 3-yr TCO (run+build only).** A ~$56k build → ~$116k; B ~$83k → ~$145k; C ~$64k → ~$160k (F16) / ~$101k (F8 reserved).

**5.6 Sensitivity (run cost 0.5×/1×/2×):** A $1,488/$1,654/$1,989 · B $1,583/$1,728/$2,021 · C $1,496(F8)/$2,670(F16)/$5,023(F32). **Pay-per-use scales gently; Fabric capacity scales in step-function jumps** — at 2×, Fabric roughly triples while A/B rise ~20–30%.

**5.7 Cost drivers & levers.** Transform/compute is the swing factor; storage/orchestration/egress are rounding error. Levers: right-size clusters + TTL + spot workers (Databricks D4s_v5 Spot ~$0.075/hr vs $0.224); serverless auto-pause SQL; reserve the right Fabric SKU (−41%); reservations/savings plans cut compute 30–41%.

---

## 6. Decision matrix & recommendation

Because run cost is close, decide on effort, ops, and fit. **Recommendation:** adopt **Variant A (ADF)** as the delivery baseline, architected so heavy workstreams graduate to **Variant B (Databricks)** patterns without re-platforming (A and B share ADLS Gen2 + the landing contract); keep **Variant C (Fabric)** as the strategic consolidation option, validated by a scoped PoC (its F8-reserved 3-yr TCO ~$101k is the lowest of all *if* it tunes to fit).

**Next step:** a 2–3 week PoC landing two contrasting feeds end-to-end into OCI Bronze — GeoTab telematics (Lane-1 API) + FastTrak/CGI Advantage (Lane-3 file) — with the `QUAR_`/manifest handoff to Agiline's aiWorks load (running Billow's PL/SQL). Run the same feeds through a Fabric F-SKU trial to measure real CU burn and validate the Oracle sink.

---

## 7. Risks & assumptions

Cost figures are planning estimates ($150/hr build labor); reservations (−30–41%) not in baseline · Fabric capacity sizing (F8 vs F16 swings 3-yr TCO ~$60k) · Azure↔OCI connectivity · landing ownership boundary · VHSP PII / CB-03 / AssetWorks REST limits / Access DB reachability / XREF pre-loads · telematics volume (~30M events/mo) is the assumption most likely to move the model.

*ERC Azure Data Ingress Proposal v0.2 — July 2026 — John-Michael Scott. Three peer pipelines + live-priced bottoms-up cost model. Planning estimates pending PoC.*

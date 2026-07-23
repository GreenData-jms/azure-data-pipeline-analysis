# Alternate 0 — Azure Ingress, Cleanse & Staging

### The in-Azure family: a dedicated Azure tier in front of the Oracle OCI EDW (approaches 1–4 of 7)

*Consolidates the core Azure analysis (`../proposals/proposal-v0.1/0.2/0.3.md`) into the alternates framing so all three strategies sit in parallel: **alternate 0 = Azure**, alternate 1 = Oracle OCI-native, alternate 2 = on-premise. Cost accounted with **license and infrastructure as distinct items**. Companion: `README.md` (7-way comparison), `seven_approach_cost_model.py`.*

---

## 1. The idea

Stand up a **dedicated Azure tier that sits in front of the Oracle OCI EDW**: it ingests ~30 sources across three lanes, cleans them, ETLs them into the structures the ERC logical model expects, and lands the finished `*_RAW` + `{TYPE}_STG` + `QUAR_` tables into the OCI Bronze zone — where Billow/aiWorks promotes them to Silver/Gold. Azure is an ingest/quality/staging engine, **not** a competing warehouse.

Unlike alternates 1 and 2, this is a *family* of four interchangeable build options that share one architecture, one data-quality framework, and one landing contract, differing only in the pipeline engine and storage substrate:

| # | Approach | Pipeline engine | Cleanse/ETL | Storage | Commercial model |
|---|---|---|---|---|---|
| 1 | **ADF** | Azure Data Factory | Mapping Data Flows + SQL | Azure SQL (+Cosmos) | pay-per-use |
| 2 | **Databricks** | Databricks Workflows/Spark | PySpark / Delta Live Tables | ADLS Delta (+thin SQL) | DBU consumption |
| 3 | **Fabric** | Fabric Data Factory | Dataflows Gen2 + Notebooks | OneLake / Warehouse | fixed capacity (F-SKU) |
| 4 | **Roll-your-own** | Durable Functions | Python in Container Apps | Azure SQL + ADLS | serverless primitives |

Because they share the landing contract, **the choice among them is reversible** — you can start on one and graduate specific workstreams to another without re-platforming.

---

## 2. Shared architecture & componentry (all four)

### 2.1 Three-lane ingress
- **Lane 1 — External API** (ChargePoint, Tesla, GeoTab JSON-RPC, AssetWorks REST v25.4, NEE): custom auth/pagination via Azure Functions (approaches 1/2/4) or Fabric Notebooks (3).
- **Lane 2 — Internal SSOR** (FA/M5 ODS, VHSP MySQL, Access FAP/Hardware, SmartSheets, XREF): private reach via Self-Hosted Integration Runtime (1/2/4) or On-Prem/VNet Data Gateway (3).
- **Lane 3 — Other-Dept / External CA** (CGI Advantage, InfoAdvantage xlsb, FastTrak, CARB, US Bank/WEX SFTP, EJ Ward XLSX): scheduled SFTP/file pickup + `XREF_` code reconciliation.

### 2.2 Raw landing zone
Immutable raw payloads land first in **ADLS Gen2** (1/2/4) or **OneLake** (3), partitioned `source/entity/yyyy/mm/dd` — the Azure analog of Bronze `*_RAW`; replayable and audit-friendly.

### 2.3 Storage medium (SQL vs document)
Relational-by-default for the conformed `{TYPE}_STG` output; NoSQL/JSON (Cosmos, Delta/JSON) only where a source is genuinely semi-structured (GeoTab telematics, NEE, nested AssetWorks). Flatten in Azure and land relational — don't push flattening across the OCI boundary onto Billow.

### 2.4 Data-quality / cleanup framework (identical across all four)
Validate → dedup & canonical-record (e.g. multi-source fuel WEX+US Bank+EJ Ward → one canonical row) → `XREF` reconcile (CGI↔AssetWorks) → business-rule DQ → route rejects to `QUAR_*` with `REJECT_REASON` (non-blocking) → SCD2 change-detection prep → PII masking (VHSP) → ERC v3.0 naming. Only the *engine* differs (Data Flows / PySpark / Power Query / Python).

### 2.5 Landing to OCI (one contract, three patterns)
- **P1** direct JDBC / Oracle sink into `ERC_*_BRZ` (native in ADF).
- **P2** Parquet to OCI Object Storage + Oracle `DBMS_CLOUD` external tables (recommended default; replayable).
- **P3** GoldenGate / Data Pump CDC (telematics-class volume).
Prefer the Azure–OCI Interconnect / Oracle Database@Azure for private, egress-optimized transfer.

### 2.6 Cross-cutting
Key Vault (secrets), Managed Identity, private endpoints/VNet, Purview/Fabric catalog + lineage, centralized run logging + DQ metrics, watermark incremental loads, schema-drift alerts on Lane-1 APIs.

---

## 3. The four in-Azure approaches (capsules)

**1 — ADF (baseline).** Most literal realization of the Whimsical board. ADF pipelines + Azure Functions (Lane-1) + Logic Apps (Lane-3) + SHIR; Mapping Data Flows + SQL procs for cleanse/ETL; Azure SQL storage; native Oracle sink. Lowest ops, cheapest to stand up, fastest to first landing. Limit: Data Flows get awkward for very complex SCD2/large scale.

**2 — Databricks (scale/streaming).** ADF (batch) + Event Hubs (telematics streaming) + Auto Loader; PySpark/DLT cleanse; ADLS Delta mirror + thin SQL. Best transform power, cleanest SCD2, real streaming lane, ML runway. Limit: highest run cost + biggest Spark skills ask.

**3 — Fabric (Power BI-native).** Fabric Data Factory + Dataflows Gen2 (Power Query) + Notebooks; OneLake + Warehouse. One SaaS platform, predictable F-SKU capacity, low-code fit for a Power BI shop. Limit: newest; Oracle sink maturity to validate; capacity sizing needs tuning (step-function cost).

**4 — Roll-your-own (DIY).** Durable Functions orchestrator + per-source Function handlers + Container Apps Jobs for cleanse/ETL; Azure SQL + ADLS. Cheapest to *run* (serverless strips managed markup) but you become the pipeline vendor. Limit: highest build + maintenance labor; key-person risk. (Full verdict in `../proposals/proposal-v0.3.md`.)

---

## 4. Cost — license vs infrastructure (the four Azure approaches)

*Live Azure Retail (West US, 2026-07-22). License here = managed-service/software portion (ADF Data Flow engine, Databricks DBU, Fabric capacity subscription, embedded Azure SQL license); Infrastructure = raw compute/storage/network. On PaaS the split is an allocation — that it's blurred, versus the explicit SKU on-prem/Oracle, is itself the finding. 3-yr TCO = capex + 36×monthly; labor at $150/hr.*

| Approach | License 3yr | Infra 3yr | Labor 3yr | Monthly run | **3-yr TCO** | License % |
|---|---|---|---|---|---|---|
| 1. ADF | $26,964 | $32,580 | $99,450 | ~$1,654 | **$158,994** | 17% |
| 2. Databricks | $19,512 | $42,660 | $168,900 | ~$1,728 | **$231,072** | 8% |
| 3. Fabric | $84,096 | $12,060 | $106,950 | ~$2,670 (F16) / ~$1,024 (F8 res.) | **$203,106** | 41% |
| 4. Roll-your-own | $7,128 | $30,024 | $351,000 | ~$1,032 | **$388,152** | 2% |

**What the split shows within Azure:** **Fabric is ~41% license** (a pure capacity subscription — Microsoft runs the infra); **Databricks DBU is a software license on rented VM infrastructure**; **roll-your-own is only 2% license** because it replaces software with a 90%-labor bill. ADF sits in the middle and carries the lowest total. Monthly run costs converge in a narrow band (~$1,000–$2,700/mo) — at this scale, **build effort and operating fit decide, not run cost.**

---

## 5. Internal recommendation (within Azure)

Build on **ADF** as the delivery baseline — lowest total cost, lowest ops, most mature Oracle sink, gentlest cost elasticity if volumes grow. Design the landing contract and lake so heavy/streaming workstreams (telematics, high-volume ops) can **graduate to Databricks** patterns incrementally (ADF and Databricks share ADLS Gen2 and the contract). Keep **Fabric** as a strategic option given ERC's Power BI orientation, validated by a scoped PoC (its F8-reserved total is competitive *if* the workload tunes to fit). Treat **roll-your-own** as the cautionary comparator: cheapest to run, most expensive to own — but its cheap serverless primitives (Functions, Container Apps Jobs) can be dropped *under* ADF orchestration for the few steps a Data Flow prices expensively.

**Next step:** a 2–3 week PoC landing two contrasting feeds end-to-end into OCI Bronze — GeoTab telematics (Lane 1) + FastTrak/CGI Advantage (Lane 3) — with the `QUAR_`/manifest handoff to aiWorks.

---

## 6. Why Azure (vs alternates 1 & 2)

**Strengths.** Best-of-breed flexibility for ~30 heterogeneous, drifting external sources; mature managed services with low ops; a clear reversible path across four engines; strong Power BI story (Fabric); lowest overall TCO in the whole 7-approach comparison (ADF $159k). Decouples ingestion from the EDW so the warehouse isn't loaded by ETL.

**Trade-offs vs the others.** Introduces a **second cloud** and therefore a **cross-cloud egress + landing hop** that alternate 1 (OCI-native) eliminates by keeping ingestion where the EDW already lives. Less single-vendor coherence than OCI-native; more managed-service dependency than on-premise. If single-cloud/data-gravity or data-residency mandates dominate, alternates 1 or 2 respectively become the better fit — otherwise Azure (ADF) is the recommended choice.

---

## 7. Risks & assumptions

Azure↔OCI connectivity (Interconnect / Oracle Database@Azure vs private endpoint) affects egress + latency · landing ownership boundary (does Billow want `{TYPE}_STG` or only `*_RAW`?) · VHSP PII masking (pending IT Security) · CB-03 (D_ASSET AcquisitionDate from VX_ASSET/REST, not FA EQ_MAIN) · AssetWorks REST rate limits · Access DB reachability · XREF pre-loads · Fabric capacity sizing (F8 vs F16 swings 3-yr TCO ~$60k) · telematics volume (~30M events/mo) drives Databricks streaming + Fabric capacity · cost figures are planning estimates; reservations (−30–41%) not applied. Full detail in `../proposals/` and `../model/`.

# Azure Data Ingress, Cleanse & Staging Platform for the ERC EDW

### A three-variant architecture proposal for landing External API, Internal, and External California Department data into the Oracle OCI EDW landing zone

*Prepared for: Caltrans Division of Equipment — Equipment Reporting Center (ERC) EDW Project*
*Reference concept: Whimsical "API & SSOR Data Ingress" · Target model: ERC Logical Data Model v1 / Unified Logical Architecture v1*
*Audience: EDW architecture team + program decision-makers*

---

## 1. Executive summary

The ERC Enterprise Data Warehouse is an Oracle Autonomous Data Warehouse on OCI, organized as a four-workstream medallion (Bronze → Silver → Gold). The **in-EDW** load is Agiline's job: the Agiline aiWorks platform picks up the staged data and executes Billow-provided PL/SQL to land it into the physical model; Billow then consumes the EDW into Power BI. What this proposal covers is the **upstream half** of your Whimsical "API & SSOR Data Ingress" board — the Azure platform that **ingests, cleans, ETLs, and stages** the origin data into the exact structures the EDW expects, then **lands the final table set into the OCI staging/landing zone** where Agiline's aiWorks load (running Billow's PL/SQL) takes over.

Azure is deliberately positioned as an **ingestion, quality, and staging tier that sits in front of the Oracle EDW** — not a competing warehouse. Its job is to turn ~30 heterogeneous sources across three lanes (External API, Internal SSORs, Other-Department SSORs) into clean, conformed, EDW-ready `*_RAW` and `{TYPE}_STG` table sets, and to hand them to OCI on a predictable cadence.

All three variants satisfy the same non-negotiables: **Azure Data Factory plus two additional ingress techniques**, a **fit-for-purpose storage medium** (relational SQL where the model is relational, document/NoSQL only where payloads are genuinely semi-structured), **first-class data cleanup**, **ETL that produces the logical-model table set**, and a **clean landing handoff into the OCI EDW staging area**. They differ in the *engine* that does the cleanup/ETL and the *shape* of the intermediate store: Variant A (ADF-Centric PaaS), Variant B (Lakehouse/Databricks), Variant C (Microsoft Fabric).

**Recommendation:** Start with **Variant A** as the delivery baseline — the most direct realization of the board, lowest-risk path to a working OCI landing, cheapest to stand up. Graduate heavy workstreams to **Variant B** patterns where telematics volume/SCD2 complexity warrant (A and B share ADLS Gen2 and the same landing contract). Keep **Variant C (Fabric)** on the table because ERC is already a Power BI shop.

*(Note: v0.2 supersedes this framing — the three are re-cast as co-equal peer pipelines with a live-priced cost model; v0.3 adds a fourth roll-your-own variant. This document is retained for the architecture, DQ, and landing detail. aiWorks is Agiline Software's platform; the staging→EDW load is Agiline's job — not a Billow product. Scope invariant: every approach lands in Oracle EDW staging and Power BI consumes the Oracle EDW downstream of aiWorks, invariant across approaches — so BI-platform "nativeness" is not a platform-selection factor.)*

---

## 2. What the sources tell us

### 2.1 The Whimsical "API & SSOR Data Ingress" essential concepts

Two ETL execution locations were sketched side by side: **ETL in EDW using aiWorks** (Billow provides the PL/SQL; Agiline's aiWorks platform picks up staging and executes it to land per the Physical Data Model — Agiline's job, out of scope for Azure but defines our handoff) and **ETL in Azure using Data Factory** ("we do it however we do it": staging in Azure Data Factory Custom Functions & Data Flows, Clean Data, then ETL & Stage origin data into the structures expected in EDW — exactly what this proposal designs). Three ingress lanes feed the cleanse step: **External API**, **Internal SSORs**, **Other Department SSORs**, each → Clean Data → Staging. Two governing asks: **"Clarity of Reasoning"** and **"Evaluate Cost Profile of Each Approach — 3 to 5 best choices."**

### 2.2 The landing target — what "EDW-ready" means

Azure's output slots into the **Bronze** layer of the Oracle medallion schemas: **`*_RAW`** (immutable, append-only source extracts, no business logic), **`{TYPE}_STG`** (validated, typed, deduplicated, pre-transformed staging, e.g. `F_FUEL_TRANSACTION_STG`, `D_ASSET_STG`), **`QUAR_`** (quarantine, invalid rows + `REJECT_REASON`, non-blocking), **`XREF_`** (code reconciliation, CGI Advantage ↔ AssetWorks). Naming per ERC Naming Convention Standards v3.0 (`_KEY` surrogate, `_IDENTIF` degenerate natural key, `_CODE` lookup, layer via schema name only, ≤30-char). **Contract:** Azure guarantees clean, conformed staging tables in the OCI landing zone; Agiline's aiWorks then loads them into the EDW (running Billow's PL/SQL), and Billow consumes the EDW into Power BI.

### 2.3 Source inventory — the three lanes

**Lane 1 — External API:** ChargePoint EV API, Tesla REST API, GeoTab JSON-RPC, AssetWorks REST API v25.4, NEE App API.
**Lane 2 — Internal SSORs:** FA raw tables (EQ_MAIN, EQ_COST_DATA, JOB_MAIN, TSK_MAIN, ACD_MAIN, LOC_MAIN), M5 ODS VX_ views (VX_ASSET, VX_BILLING, VX_ACCIDENT), VHSP MySQL, Access FAP DB, Access Hardware DB, SmartSheets + MS Project, 6 XREF bridge tables.
**Lane 3 — Other-Dept / External California SSORs:** CGI Advantage, InfoAdvantage OE/PS xlsb, FastTrak CSV + Access, CARB DB extract, US Bank SFTP, WEX SFTP, EJ Ward / AGWorks XLSX.

---

## 3. Positioning — where Azure sits relative to the OCI EDW

Azure is the ingest → land-raw → cleanse+ETL → stage tier; the contract line is the handoff from Azure "STAGE" to the OCI EDW Bronze landing zone (ERC_*_BRZ). Everything left of it is Azure's responsibility (this proposal); everything right is Agiline's aiWorks load (running Billow's PL/SQL) → Silver → Gold → Billow → Power BI/OAC.

---

## 4. Common reference architecture (shared by all variants)

**4.1 Three-lane ingress pattern.** Lane 1 (API): token/OAuth, pagination, watermarking as code (Functions/Notebooks), ADF orchestrates. Lane 2 (internal): private reach via Self-Hosted IR / On-Prem Data Gateway. Lane 3 (other-dept): scheduled SFTP/file pickup + `XREF_` code reconciliation.

**4.2 Raw landing zone.** Every variant lands immutable raw payloads first into a lake (ADLS Gen2 / OneLake), partitioned source/entity/yyyy/mm/dd — the Azure analog of Bronze `*_RAW`; replayable, audit-friendly.

**4.3 Storage medium (R3).** Relational SQL by default for conformed `{TYPE}_STG`; document/NoSQL only where payloads are genuinely semi-structured (GeoTab JSON, NEE, nested AssetWorks). We flatten in Azure and land relational — not push the flattening across the OCI boundary onto the in-EDW load.

**4.4 Data cleanup & quality (R4).** validate → dedup & canonical-record → XREF reconcile → business-rule DQ → `QUAR_` rejects → SCD2 prep → PII masking (VHSP) → ERC v3.0 naming.

**4.5 Landing to OCI (R6).** P1 direct JDBC/Oracle sink; P2 Parquet to OCI Object Storage + `DBMS_CLOUD` external tables; P3 GoldenGate/Data Pump CDC. Prefer Azure–OCI Interconnect / Oracle Database@Azure for private transfer.

**4.6 Cross-cutting.** Key Vault, Managed Identity, private endpoints/VNet, Purview catalog/lineage, centralized run logging + DQ metrics, watermark incremental loads, schema-drift alerts.

---

## 5. Variant A — ADF-Centric PaaS

Most literal realization of the board. **Ingress:** ADF (orchestrator + Copy + SHIR) + Azure Functions (Lane-1 custom API) + Logic Apps (Lane-3 SFTP/file). **Storage:** Azure SQL DB/MI for `*_RAW`+`{TYPE}_STG`; Cosmos DB optional for API JSON; ADLS Gen2 for raw files. **Cleanse+ETL:** ADF Mapping Data Flows + SQL stored procs. **Landing:** ADF Oracle sink (P1) / Parquet to OCI (P2). **Strengths:** lowest ops/cost, native Oracle sink, smallest skills ask, fastest to first landing. **Limits:** Data Flows awkward for very complex SCD2/large scale.

## 6. Variant B — Lakehouse (Databricks medallion)

Mirror the medallion in Azure with Delta. **Ingress:** ADF (batch) + Event Hubs (telematics streaming) + Databricks Auto Loader/notebooks (API). **Storage:** ADLS Gen2 + Delta (Bronze/Silver mirror) + thin Azure SQL. **Cleanse+ETL:** Databricks PySpark, Delta MERGE for SCD2. **Landing:** Spark JDBC / Parquet to OCI / GoldenGate. **Strengths:** best scalability + transform power, cleanest SCD2, streaming lane, ML runway. **Limits:** highest run cost + biggest skills ask.

## 7. Variant C — Microsoft Fabric (unified SaaS)

One SaaS platform, Power BI-native, capacity billing. **Ingress:** Fabric Data Factory + Dataflows Gen2 (Power Query) + Fabric Notebooks. **Storage:** Fabric Lakehouse (OneLake) + Warehouse (T-SQL). **Cleanse+ETL:** Dataflows Gen2 + Notebooks. **Landing:** Fabric Copy → Oracle / Parquet to OCI. **Strengths:** one platform/bill, predictable F-SKU capacity, low-code Power Query fit, tightest Power BI integration. **Limits:** newest; Oracle sink maturity to validate; capacity sizing needs tuning. *(Per the scope invariant added in v1.1, Power BI integration is not an ingress-tier selection factor — BI consumes the Oracle EDW downstream of aiWorks; judge Fabric on cost + Oracle-sink maturity + capacity. This section is retained as the original v0.1 architecture detail.)*

---

## 8. Landing into the OCI EDW staging zone (R6)

| Pattern | How | Best for |
|---|---|---|
| P1 Direct JDBC | ADF/Spark Oracle sink writes into `ERC_*_BRZ` | small–medium batch |
| P2 Object Storage + external tables | Parquet/CSV to OCI Object Storage + `DBMS_CLOUD` | bulk, replayable — recommended default |
| P3 GoldenGate / Data Pump | CDC stream | high-volume/near-real-time |

Contract artifacts per feed: table DDL (ERC v3.0), load manifest (row counts, watermark, batch id), `QUAR_` reject set, completion signal Agiline's aiWorks load polls.

## 9. Data cleanup & quality framework (R4/R5)

Structural validation → dedup & canonical record (multi-source fuel WEX+US Bank+EJ Ward) → reference/XREF reconciliation → business-rule DQ (VHSP delinquency, PS/OE classification, IS_MISCHARGE) → quarantine to `QUAR_*` → SCD2 change-detection prep (D_ASSET ⚠CB-03 needs VX_ASSET/REST not FA EQ_MAIN; D_VEHICLE, D_EV_STATION, D_FUEL_SITE, D_GEOTAB_DEVICE, D_PROJECT, D_FAP_PROJECT, D_BOM_PART) → PII masking (VHSP) → naming/typing to ERC v3.0.

## 10. Risks & open items

Azure↔OCI connectivity · landing ownership boundary (STG vs RAW) · VHSP PII · CB-03 · AssetWorks REST rate limits · Access DB reachability · XREF pre-loads · cost figures representative pending PoC.

## Appendix — Source → recommended ingress technique (Variant A baseline)

ChargePoint/Tesla/GeoTab/AssetWorks/NEE → Azure Functions; FA/M5/VHSP/Access FAP/Access Hardware → ADF Copy via SHIR; SmartSheets → Logic Apps; CGI Advantage/InfoAdvantage/FastTrak/CARB/US Bank/WEX/EJ Ward → Logic Apps SFTP + Data Flow parse + XREF reconcile.

*ERC Azure Data Ingress Proposal v0.1 — July 2026 — John-Michael Scott. Superseded in framing by v0.2/v0.3; retained for architecture, DQ, and landing detail.*

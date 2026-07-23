# Alternate 1 — Oracle OCI-Native Ingress & In-Database ETL

### API inbound to OCI staging, ETL run inside OCI using Oracle orchestration and API management

*Part of the ERC EDW ingress analysis (approach #5 of 7). Cost accounted with **license and infrastructure as distinct items**. Companion: `alternate-2-on-premise.md`, `README.md` (7-way comparison), `seven_approach_cost_model.py`.*

---

## 1. The idea

Instead of standing up a separate Azure tier in front of the Oracle EDW, do the ingestion, cleansing, and ETL **inside OCI itself**, using Oracle's own integration and orchestration stack, and land straight into the EDW's Bronze staging schema. The EDW already lives on Oracle Autonomous Data Warehouse in OCI — so this approach keeps everything in one cloud, one vendor, and eliminates the cross-cloud hop entirely.

The defining move: **the data never leaves OCI between ingestion and the warehouse.** External APIs and files come *into* OCI; ETL runs *in* OCI (much of it inside the ADW itself); the result is already in the EDW's landing zone. There is no Azure, no second platform, and effectively **no cross-cloud egress**.

---

## 2. Architecture & componentry

| Layer | OCI component | Role |
|---|---|---|
| **API management / inbound** | **OCI API Gateway** | Publishes managed inbound endpoints; auth, throttling, routing for partners pushing data in |
| **Orchestration + adapters** | **Oracle Integration Cloud (OIC)** | The iPaaS: orchestrates flows, hosts prebuilt adapters (REST, SOAP, SFTP, DB, FTP), schedules, maps, error-handles. This is the "Oracle orchestration and API management" layer |
| **Custom API pulls** | **OCI Functions** (serverless) | Lane-1 handlers where an adapter isn't enough (GeoTab JSON-RPC, Tesla/ChargePoint OAuth, AssetWorks paging) |
| **Raw landing** | **OCI Object Storage** | Immutable raw payloads (`source/entity/yyyy/mm/dd`) — the Bronze `*_RAW` analog |
| **Staging + ETL engine** | **Autonomous Data Warehouse (ADW)** + **Oracle Data Transforms** (ODI-based, included with ADW) + **PL/SQL** + **`DBMS_CLOUD`** | Loads from Object Storage; runs cleanse/dedup/SCD2/`XREF` **in-database**; produces `{TYPE}_STG` directly in the EDW landing schema |
| **Secrets / identity** | **OCI Vault** + IAM | Credentials, OAuth secrets, instance principals |
| **Observability** | **OCI Monitoring / Logging / Events** | Run metrics, DQ counters, alerting |

### 2.1 Per-lane ingestion

- **Lane 1 — External API:** OIC REST adapters for well-behaved APIs; **OCI Functions** for the awkward ones (GeoTab JSON-RPC, OAuth token dances, AssetWorks pagination). Payloads land in Object Storage, then `DBMS_CLOUD` ingests to ADW external/staging tables.
- **Lane 2 — Internal SSOR:** OIC connectivity agent (on-prem agent) reaches private sources (FA/M5, VHSP MySQL, Access DBs) over a secure tunnel — the OCI analog of a self-hosted runtime. FastConnect/VPN for network reach.
- **Lane 3 — Other-Dept / External California:** OIC SFTP/file adapters (US Bank, WEX, FastTrak, EJ Ward, InfoAdvantage xlsb); `XREF_` code reconciliation (CGI Advantage ↔ AssetWorks) applied **in-database** during transform.

### 2.2 In-database ETL (the differentiator)

Because staging lives in the same ADW as the EDW, cleanse and ETL run as **set-based SQL / PL/SQL and Oracle Data Transforms mappings right where the data lands** — no data movement to a separate compute tier. Validate → dedup/canonical → `XREF` reconcile → business rules → `QUAR_` → SCD2 (`MERGE`) → `{TYPE}_STG`, all inside ADW, all in the ERC v3.0 naming. The "landing to OCI" step other approaches worry about **disappears** — the output is already in the target database's Bronze schema.

---

## 3. Cost — license vs infrastructure (distinct items)

*Live/published OCI list prices (2026): ADW OCPU **$4.0288/hr License-Included**, **$1.3441/hr BYOL**; ADW storage $118.40/TB-mo; Object Storage $0.0255/GB-mo; OIC ~$943/mo per message pack (Enterprise, 5,000 msgs/hr); OCI egress 10 TB/mo free then ~$0.0085/GB. Planning estimates on the standard workload.*

### 3.1 License-Included (no owned Oracle license)

| Stream | Monthly | What's in it |
|---|---|---|
| **License / software** | **~$3,175** | OIC (2 message packs, ~$1,886) + ADW OCPU **license premium** (~$1,289 = the $2.6847/OCPU-hr delta of License-Included over BYOL, on ~480 OCPU-hr/mo of ETL) |
| **Infrastructure** | **~$975** | ADW compute **infra portion** (BYOL-rate equivalent, ~$645) + ADW staging storage (~$237) + API Gateway (~$50) + Functions (~$30) + Object Storage (~$13) |
| **Labor (ops)** | ~$1,500/mo (10 h) + build ~$52,500 (350 h) | OIC/ODI/PL-SQL development; low ongoing ops (managed OCI) |
| **Cross-cloud egress** | **$0** | Ingestion runs where the EDW lives — no Azure→OCI transfer |

**3-yr TCO (License-Included): ~$255,900** — License $114,300 · Infrastructure $35,100 · Labor $106,500.

### 3.2 BYOL (you already own Oracle DB licenses — very likely for the EDW)

Under Bring-Your-Own-License the ADW compute drops to the $1.3441/OCPU-hr rate, so the ADW cost moves almost entirely to **infrastructure** and the software license reduces to **OIC only**:

| Stream | Monthly |
|---|---|
| License / software | **~$1,886** (OIC only) |
| Infrastructure | **~$1,620** (ADW BYOL compute + storage + gateway + functions + object storage) |
| Labor (ops) | ~$1,500/mo + build ~$52,500 |

**3-yr TCO (BYOL): ~$232,700** — and the Oracle DB license you "bring" is a capex you likely already carry for the EDW itself. **This BYOL figure, not the Lic-Incl $256k, is the like-for-like comparator to the Azure family** (Azure bundles no separately-owned license): at ~$233k it is only ~$30k above ADF, level with Fabric, and *below* Databricks and roll-your-own. It also carries **no GoldenGate and no cross-cloud egress** — two lines every Azure approach may pay (GoldenGate ~$8k–58k/3yr if telematics needs CDC; egress immaterial in dollars). So on cost the Azure-vs-OCI-native gap is not decisive; the case for Azure rests elsewhere (see below).

---

## 4. Why choose it — and why not

**Strengths.** Single vendor, single cloud — no second platform to run, secure, or reconcile. **Zero cross-cloud egress** and no data-gravity fight: ingestion happens where the warehouse already is. ETL runs **in-database** (set-based, fast, no movement tier). Oracle-native orchestration (OIC) with prebuilt adapters. Operationally the simplest to reason about because there is one place data lives.

**Limits.** Ties ingestion tightly to Oracle and to OIC's per-message commercial model. Under **License-Included**, ADW OCPU carries a real software premium (the biggest single "license" line of any managed approach here). OIC is less flexible than code for the most irregular external APIs (still need Functions). Deeper Oracle/OIC/ODI skill concentration; more Oracle lock-in. **Workload isolation is the decisive limit and the strongest single argument for the Azure family:** ETL runs in the *same* Autonomous DW that serves Power BI reporting, so ingestion OCPU competes with the reporting workload — you must size/isolate a separate OCPU pool or a second ADW instance, and autoscaling must be watched so ingestion doesn't inflate the EDW bill. An external Azure tier keeps that load off the reporting warehouse entirely.

**Best when:** the organization is already all-in on OCI/Oracle for the EDW (it is), values single-vendor operational simplicity and data gravity over best-of-breed flexibility, and can **BYOL** to neutralize the ADW license premium. In that BYOL case this is arguably the most *architecturally coherent* option — the ingestion lives inside the warehouse's own cloud and the "landing" problem vanishes.

---

## 5. Risks & assumptions

OIC message-pack sizing (1 vs 2 packs roughly halves/doubles the OIC line) · ADW OCPU autoscaling governance so ingestion doesn't inflate the EDW's own consumption · Lane-2 private reach via OIC connectivity agent + FastConnect · License-Included vs BYOL is the single biggest cost lever (~$1,300/mo swing) · in-database ETL concentrates load on the same ADW that serves reporting — size/isolate accordingly (separate OCPU pool or ADW instance) · Oracle publishes indicative, not fixed, OIC pricing — confirm with Oracle. All figures are planning estimates.

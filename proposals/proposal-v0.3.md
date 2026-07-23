# Azure Data Ingress, Cleanse & Staging Platform for the ERC EDW

### v0.3 — Adds Variant D (roll-your-own) and answers: *is ADF actually the optimal-priced choice?*

*Builds on v0.2 (ADF vs Databricks vs Fabric). Cost basis: live Azure Retail Prices (West US, pulled 2026-07-22); reproducible model `erc_azure_cost_model.py`.*

---

## 1. The question

> "A 4th strategy if we essentially rolled our own — built what Data Factory does as a series of handlers/functions plus all the component parts. I think Data Factory is the optimal-priced choice, but maybe I'm wrong?"

Short answer: **your instinct is right — but on the *Azure bill alone* you're arguably wrong.** Roll-your-own is genuinely *cheaper to run*. It is ADF's **total** cost — build plus run plus the maintenance labor you permanently absorb — that makes ADF optimal.

---

## 2. Variant D — roll-your-own (what it actually is)

Rebuild the seven things ADF gives you for free from raw Azure primitives:

| ADF gives you… | In Variant D you build/run… |
|---|---|
| Pipeline orchestration engine | Azure Durable Functions (orchestrator + fan-out/fan-in + timers) |
| Per-source connectors | One Azure Function "handler" per source (OAuth/pagination, SFTP, DB extract) |
| Copy activity / data movement | Custom extract code + Container Apps Jobs |
| Mapping Data Flow (transform) | Container Apps Jobs running Python (Polars/DuckDB/pandas or single-node Spark) |
| Metadata-driven control | A control/metadata schema you design in Azure SQL |
| Retry / checkpoint / watermark / idempotency | Code you write and test in every handler |
| Monitoring, alerting, lineage | App Insights + custom dashboards you build |
| Managed Oracle connectors | `python-oracledb` client writing to OCI Bronze (P1/P2) |

Storage, DQ/quarantine, and the OCI landing contract are identical to the other variants. What changes: **you become the pipeline vendor** — the framework is yours to build, secure, patch, and keep working as 30 external sources drift.

**2.1 Why the run cost is genuinely low.** Container Apps active compute is ~$0.000024/vCPU-second (~$0.086/vCPU-hour) and Functions Consumption is $0.20/M exec + $0.000016/GB-s. Running cleanse/ETL as a 4-vCPU Container Apps Job ~120 hrs/month is ~$52/mo — vs ADF Mapping Data Flows ~$259/mo or Databricks ~$600/mo. You strip out the managed markup.

---

## 3. Variant D monthly run cost (live-priced)

| Line item | $/mo |
|---|---|
| Functions Premium EP1 (orchestrator + handlers, VNet to Lane-2) | 155 |
| Functions Consumption (Lane-1 API handler bursts) | 30 |
| Container Apps Jobs (cleanse / ETL / landing) | 52 |
| Azure SQL (staging + control/metadata, 4 vCore GP) | 495 |
| ADLS Gen2 (raw lake) | 10 |
| Egress to OCI | 10 |
| Baseline (Key Vault / App Insights / Durable storage) | 280 |
| **Monthly run total** | **~$1,032** |

**Variant D runs for ~$1,032/mo — the cheapest of the four, ~$620/mo (~$7.5k/yr) below ADF.** On the Azure invoice, D wins.

---

## 4. The lens that flips it: ongoing ops labor

A managed platform's price *includes* the engineering that keeps the pipeline engine alive. Roll-your-own moves that onto your payroll, forever.

| Peer | Ops labor | Why |
|---|---|---|
| ADF | ~8 hrs/mo | Managed; connector updates are Microsoft's |
| Databricks | ~16 hrs/mo | Cluster tuning + runtime upkeep |
| Fabric | ~8 hrs/mo | Managed SaaS |
| Roll-your-own | ~40 hrs/mo | You own the framework: connector drift, patching, security, custom monitoring, on-call — no vendor support |

**Decompose the hours — connector-drift (shared) vs engine upkeep (differs).** A large slice of ops is maintaining ~30 bespoke source handlers as external APIs drift (GeoTab, Tesla/ChargePoint OAuth, AssetWorks REST versioning, other-dept file schemas). At a planning rate of ~2 breaking changes/source/yr × 2 h, that shared **connector-drift slice is ~10 h/mo and is roughly constant across all four** approaches — nobody but you maintains your GeoTab handler, ADF included. What actually *differs* is the **engine-upkeep** slice: ADF ~0, Fabric ~0, Databricks ~6 (cluster/runtime), roll-your-own ~30 (the whole framework). So ADF's advantage is precisely **"near-zero *engine* upkeep,"** not "lowest *total* ops" — and if connector volatility is high, the realized ops of all four converge upward while roll-your-own still carries its extra ~30 h/mo. This *narrows* the ADF-vs-Databricks/Fabric ops gap but leaves the ADF-vs-roll-your-own gap intact (the point of §5). The connector-volatility rate is an editable lever in `../alternates/seven_approach_cost_model.py`.

---

## 5. Four-way comparison — the honest total

| Peer | Run $/mo | + Ops labor $/mo | Run+Ops $/mo | One-time build | 3-yr TCO |
|---|---|---|---|---|---|
| A — ADF | $1,654 | $1,200 | **$2,854** | ~$56k (375 hrs) | **~$159k** |
| B — Databricks | $1,728 | $2,400 | $4,128 | ~$83k (550 hrs) | ~$231k |
| C — Fabric (F16) | $2,670 | $1,200 | $3,870 | ~$64k (425 hrs) | ~$203k |
| D — Roll-your-own | **$1,032** | $6,000 | $7,032 | ~$135k (900 hrs) | **~$388k** |

D has the **lowest run cost** and the **highest total cost** — about **2.4× ADF over three years**. Build: ~900 hrs vs ADF's ~375 (~$79k more). Maintenance: ~40 vs ~8 hrs/mo — a ~$4,800/mo (~$57.6k/yr) swing that dwarfs D's ~$7.5k/yr run saving ~8×.

---

## 6. Verdict — is ADF the optimal-priced choice?

**Yes on total cost of ownership, by a wide margin. No, it is not the cheapest to run; roll-your-own is.** Say it this way:

> ADF isn't the smallest Azure bill. It's the smallest *total* bill, because it converts a large, permanent labor liability — building and forever maintaining a pipeline engine — into a small managed run cost. The ~$7.5k/yr you'd save on compute by rolling your own is erased many times over by the ~$57.6k/yr of engineering you'd absorb, plus ~$79k more to build it.

**6.1 The honest exception — when roll-your-own wins.** Only if the maintenance labor is effectively free/sunk (spare senior engineering capacity), the ~30 sources are stable (low connector drift), you value zero lock-in, and the framework is long-lived enough to amortize the build. At Caltrans scale (~30 heterogeneous, externally-owned, drifting sources) those conditions are unlikely to hold.

**6.2 A pragmatic middle path.** ADF already orchestrates **Azure Functions** and can invoke **Container Apps Jobs** for a heavy transform where a Data Flow is pricey — capturing D's serverless run-cost wins while keeping ADF's managed orchestration, monitoring, Oracle sink, and low maintenance.

---

## 7. Updated recommendation (v0.1→v0.3)

Reinforced: **build on ADF.** v0.2 showed the three managed peers run within a narrow band, so build effort and fit decide. v0.3 adds that rolling your own lowers the Azure bill but roughly doubles-to-triples the three-year TCO through labor — strengthening the ADF baseline. Drop serverless (Functions/Container Apps) under ADF's orchestration on expensive steps; graduate heavy/streaming workstreams to Databricks where volume warrants; keep Fabric as the PoC-validated strategic option.

---

## 8. Caveats specific to v0.3

Ops-labor hours are the load-bearing assumption — editable in the model; even at DIY = 20 hrs/mo, D stays well above ADF. Build-hour estimates assume production-grade (retry/idempotency/observability), not a prototype. Key-person/operational risk is not monetized but favors ADF. All §3–§5 numbers are generated by the model.

*ERC Azure Data Ingress Proposal v0.3 — July 2026 — John-Michael Scott. Adds Variant D + ops-labor TCO lens. Verdict: ADF optimal on total cost, not run cost. Planning estimates pending PoC.*

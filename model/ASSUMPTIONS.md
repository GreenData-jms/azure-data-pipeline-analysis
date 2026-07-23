# Assumptions & Basis — ERC EDW Ingress cost model

*What every number in this analysis rests on. Companion to `erc_azure_cost_model.py` (Azure bottoms-up, variants A–D) and `../alternates/seven_approach_cost_model.py` (7-approach license/infra/labor). Feeds the deck's **Basis & caveats** (slide 14) and **appendix** slides. Edit the assumptions and re-run either model to reprice.*

**Cost basis:** live **Azure Retail Prices, region West US, PAYG Consumption**, pulled via the Azure pricing API **2026-07-22**; Oracle/Microsoft license figures from **2026 published list prices**; OCI from published list; on-prem hardware/labor are documented planning estimates. `HRS = 730` avg hours/month. 3-yr TCO = capex + 36 × monthly. **All figures are planning estimates — enterprise discounts (50–80% off list) and cloud reservations (30–41% off) are not applied.**

---

## 1. Data-volume assumptions (the drivers)

Mid-size Caltrans-scale workload. These are the editable `ASSUMPTIONS` in the model.

| Assumption | Value | Notes |
|---|---|---|
| Sources | **30** | across the three ingress lanes |
| Orchestration / copy activity runs | **~3,000 / mo** | ~30 feeds + AssetWorks sub-entities |
| — of which via self-hosted IR (Lane-2 private) | **~1,000 / mo** | |
| Cloud copy | **~150 DIU-hours / mo** | Lane-1/Lane-3 movement |
| Self-hosted copy | **~200 hours / mo** | Lane-2 private extract |
| Steady-state ingest volume | **~75 GB / mo** | telematics-dominated |
| Raw-lake resident footprint | **~500 GB** | ~13 months retained, compressed |
| Relational staging footprint | **~50 GB** | transient (truncate/reload) |
| Telematics events | **~30,000,000 / mo** | near-real-time |
| Active transform cluster-hours | **~120 / mo** | batch cleanse/ETL |
| One-time historical backfill | **~1.5 TB** | |

---

## 2. Live unit prices (West US, PAYG, 2026-07-22)

**ADF:** orchestration $1.00/1k runs (cloud) · $1.50/1k (SHIR) · copy $0.25/DIU-hr (cloud) · $0.10/hr (SHIR) · Mapping Data Flow **General Purpose $0.26975/vCore-hr**.
**Databricks (DBU is on top of the VM):** Jobs $0.15/DBU · Jobs Premium/Photon $0.30/DBU · DLT Core $0.30/DBU.
**Fabric:** **$0.20/CU-hr** · 1-yr reserved factor **×0.59** (~41% off) · OneLake hot $0.026/GB-mo.
**Azure SQL DB GP Gen5 (compute/hr):** 2 vCore $0.334878 · 4 vCore $0.669756 · 8 vCore $1.339512 · storage $0.115/GB-mo.
**Storage:** ADLS Gen2 Hot LRS $0.021/GB-mo.
**VMs (Linux PAYG):** D4s_v5 $0.224/hr · D2s_v5 $0.112/hr · D4s_v5 **Windows** $0.408/hr · D4s_v5 Spot $0.075/hr.
**Event Hubs Standard:** $0.03/TU-hr · $0.028 per million events.
**Egress (internet data-transfer-out, tier 1):** **$0.08/GB, first 100 GB/mo free** (the v1.1 seven-approach model uses $0.087/GB; same conclusion).
**Roll-your-own serverless:** Functions Premium $0.17/vCPU-hr + $0.0122/GiB-hr · Consumption $0.20/M exec + $0.000016/GB-s · Container Apps $0.000024/vCPU-s + $0.000003/GiB-s.

---

## 3. Compute — component sizing per variant (with the SKUs chosen)

**Variant A — ADF:** Mapping Data Flows on an **8-vCore General Purpose** cluster × 120 hrs/mo; **Azure SQL GP Gen5 4-vCore** staging; Azure Functions (Lane-1) and Logic Apps (Lane-3) carried as small flat lines (~$40 / ~$80); **self-hosted IR = a pair of D4s_v5 Windows VMs, HA, sized ~50%**; Cosmos DB an optional ~$150/mo JSON buffer.

**Variant B — Databricks:** ADF kept for batch orchestration + copy; **Event Hubs at 4 TU** for the telematics stream; batch ETL on **4× D4s_v5 nodes** where node-hr = VM $0.224 + 0.75 × $0.30 DBU (Premium/Photon) = **$0.449/node-hr** × 120 hrs; a **2-node streaming cluster always-on, autoscale-tempered to ~60%**; **Azure SQL GP 2-vCore** serving DB; same SHIR VM pair.

**Variant C — Fabric:** **F16 capacity** PAYG ($0.20/CU-hr × 16 × 730 = $2,336/mo) as the base, or **F8 reserved** (× 0.59 ≈ $689/mo) tuned; capacity assumed to **step F8→F16→F32**, not scale smoothly; On-Prem/VNet Data Gateway on one D4s_v5-Windows sized ~50%.

**Variant D — roll-your-own:** Functions **Premium EP1 always-ready** (1 vCPU + 3.5 GiB) for orchestrator/private handlers; Consumption bursts (~$30) for Lane-1; **Container Apps Jobs at 4 vCPU / 8 GiB** × 120 transform-hours; Azure SQL GP 4-vCore for staging + control/metadata.

### Worked example — Variant A monthly build-up (so the total is fully traceable)

| Line | Sizing | $/mo |
|---|---|---|
| ADF orchestration | 3,000/1k×$1.00 + 1,000/1k×$1.50 | ~$5 |
| ADF data movement | 150 DIU-hr×$0.25 + 200 hr×$0.10 | ~$58 |
| **ADF Mapping Data Flows** | 120 hr × 8 vCore × $0.26975 | **~$259** |
| Azure Functions (Lane-1) | flat | ~$40 |
| Logic Apps (Lane-3) | flat | ~$80 |
| **Azure SQL staging** | 4-vCore GP $0.669756 × 730 + 50 GB × $0.115 | **~$495** |
| Cosmos DB (optional) | JSON buffer | ~$150 |
| ADLS Gen2 raw lake | 500 GB × $0.021 | ~$11 |
| Self-hosted IR VM pair (HA) | 2 × $0.408 × 730 × 0.5 | ~$298 |
| Egress to OCI | (75−100 free)×$0.08 + $10 buffer | ~$10 |
| Baseline (Key Vault/PE/monitoring) | flat | ~$250 |
| **Monthly total** | | **~$1,654** (~$1,504 without Cosmos) |

The other variants build up the same way — see `erc_azure_cost_model.py`, functions `variant_adf` / `variant_dbx` / `variant_fabric` / `variant_diy`.

---

## 4. Storage assumptions

ADLS Gen2 Hot LRS $0.021/GB-mo × ~500 GB raw lake; Azure SQL storage $0.115/GB-mo × ~50 GB staging; OneLake hot $0.026/GB-mo (Fabric); optional Cosmos ~$150/mo (ADF JSON buffer). **Storage is a rounding error in every option.**

---

## 5. Bandwidth / egress assumptions

Egress to OCI priced as **internet tier-1 outbound $0.08/GB with the first 100 GB/month free**. Because steady-state ingest (~75 GB/mo) sits *under* the free tier, steady egress is effectively **$0/mo**; a flat ~$10/mo buffer is carried. The **1.5 TB one-time backfill** is ~$120 (1,500 GB × $0.08). This is why the oppositional analysis found egress immaterial in dollars — it is, however, the one line **OCI-native zeroes entirely**, which is a qualitative point in its favor, not a budget-mover. Private connectivity (Azure–OCI Interconnect / Oracle Database@Azure) is assumed available; a dedicated FastConnect/Interconnect port charge is *not* separately modeled on the Azure side (it is on-prem).

---

## 6. Labor — the assumptions that actually decide the outcome

Cloud compute/storage/bandwidth is **not** what drives the ranking; **labor is 63–90% of every option's 3-year TCO.** These are the softest and largest inputs:

| | ADF | Databricks | Fabric | Roll-your-own |
|---|---|---|---|---|
| Build hours (one-time) | 375 | 550 | 425 | 900 |
| Ongoing ops hours / month | 8 | 16 | 8 | 40 |

Blended rate **$150/hr** (state-adjustable; a two-rate senior/standard lever exists in the seven-approach model). **Ops-labor decomposition (v1.1):** of the monthly ops hours, a **shared connector-drift slice (~10 h/mo)** — maintaining ~30 bespoke source handlers as external APIs drift — is roughly constant across ADF/Databricks/Fabric/roll-your-own; only the **engine-upkeep slice** differs (ADF ~0, Databricks ~6, roll-your-own ~30). So ADF's edge is "near-zero *engine* upkeep," not "lowest total ops."

---

## 7. Off-Azure sizing (for the 7-approach comparison)

> **Full detail:** [`../alternates/ASSUMPTIONS.md`](../alternates/ASSUMPTIONS.md) — the OCI-native and on-premise basis with unit prices, sizing tables, worked build-ups, and the license breakdown. Summary below.

**OCI-native (approach 5):** ~480 ETL OCPU-hours/mo on ADW; **2 OIC message packs** (~$1,886/mo); API Gateway ~$50, Functions ~$30, Object Storage ~$13; Lic-Incl carries an ADW OCPU software premium (~$1,289/mo = the $2.6847/OCPU-hr delta of Lic-Incl over BYOL); **zero cross-cloud egress; no GoldenGate.** BYOL drops ADW to the $1.3441/OCPU-hr rate.

**On-premise (approaches 6 & 7):** 2× HA DB servers + SAN + network + backup = **~$120k capex**; monthly colo ~$1,200 + FastConnect to OCI ~$1,013 + maintenance ~$300; DBA+sysadmin **~30 h/mo**; database license per tier (Oracle SE2 ~$35k perpetual + 22%/yr support; SQL 2022 Standard 16-core + Windows Datacenter; EE/Enterprise variants far higher). ETL via PL/SQL or bundled SSIS (no separate ETL license modeled).

**GoldenGate contingency (telematics CDC, both models, outside base TCO):** a **2-OCPU** OCI GoldenGate managed deployment at $0.6721/OCPU-hr (Lic-Incl) or $0.1613 (BYOL) × 730, or **$17,500/processor perpetual** + 22%/yr support → ~$8k (BYOL managed) / ~$35k (Lic-Incl managed) / ~$58k (perpetual) over 3 years. **$0 for OCI-native.**

---

## 8. Which assumptions are load-bearing vs. rounding error

- **Softest and biggest — the labor hours** (build + ops). They dominate every total and are pure planning estimates; this is why the three managed options collapse into a **band (~$159k–$231k)** within the noise, and why the PoC exists to return *real* hours.
- **Most likely to move the model — telematics volume (30M events/mo).** It drives the Databricks streaming cluster, the Fabric capacity tier, and whether the landing needs CDC/GoldenGate at all.
- **The compute swing factor — the 120 transform cluster-hours** and the **Fabric F8-vs-F16 choice** (that alone swings 3-yr TCO ~$60k).
- **Rounding error — storage, egress/bandwidth, orchestration runs,** and the small flat lines (Functions / Logic Apps / baseline).

---

## 9. What the PoC replaces (turns assumptions into measurements)

The 2–3 week two-feed PoC is scoped to retire the softest inputs above: **real build + ops hours** for two contrasting feeds (collapsing the labor band into measured numbers), the **actual telematics landing cost** — settling whether GoldenGate is required — and a **Fabric F-SKU trial** measuring real CU burn and Oracle-sink behavior. Everything else in this document is either robust or immaterial.

---

## Provenance & how to reprice

- **Azure bottoms-up (variants A–D):** `erc_azure_cost_model.py` — edit the `P` (unit prices) and `A` (assumptions) blocks, re-run.
- **Seven-approach license/infra/labor + contingencies:** `../alternates/seven_approach_cost_model.py`.
- **Machine-readable figures:** `../corpus/figures.json` (Azure options, `unit_prices` + `volume_assumptions`) and `../alternates/seven-approach-figures.json` (7-approach + contingencies + ops decomposition).

*Assumptions & Basis v1 — 2026-07-23 — John-Michael Scott / GreenData Ventures. Planning estimates pending PoC.*

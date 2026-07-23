# Assumptions & Basis — OCI-native & On-premise (off-Azure approaches)

*The off-Azure companion to `../model/ASSUMPTIONS.md` (which covers the Azure variants A–D). Documents the sizing, unit prices, worked build-ups, and license basis behind **approach 5 (Oracle OCI-native)** and **approaches 6 & 7 (on-premise Oracle DB / SQL Server)** in `seven_approach_cost_model.py`. Edit the model and re-run to reprice.*

**Cost basis:** OCI from **published OCI list prices (2026)**; database/OS licenses from **2026 published list prices**; on-prem hardware, facilities, and labor are **documented planning estimates** (not live-metered like the cloud unit prices). `HRS = 730` avg hours/month. 3-yr TCO = capex + 36 × monthly. **Planning estimates — enterprise license discounts (Oracle/Microsoft routinely 50–80% off list) and any negotiated colo/carrier rates are not applied.**

Both off-Azure approaches still **land their output in the OCI EDW staging zone** (on-prem ships to OCI over FastConnect; OCI-native lands in-database) — the scope is identical to the Azure options; only the substrate differs.

---

# Part 1 — Oracle OCI-native (approach 5)

API inbound to OCI, ETL run **in-database** in the Autonomous DW, using Oracle's own integration stack. The data never leaves OCI, so there is **no cross-cloud egress and no GoldenGate**.

## 1.1 Published OCI unit prices (2026 list)

- **ADW OCPU:** **$4.0288/OCPU-hr License-Included** · **$1.3441/OCPU-hr BYOL** (the $2.6847/OCPU-hr difference is the "software premium").
- **ADW storage:** $118.40/TB-month.
- **OCI Object Storage:** $0.0255/GB-month.
- **Oracle Integration Cloud (OIC):** ~$943/month per message pack (Enterprise, 5,000 msgs/hr).
- **OCI egress:** first 10 TB/month free, then ~$0.0085/GB → **$0 at this workload**.
- **OCI API Gateway / Functions / Vault / Monitoring:** small metered lines.
- **OCI FastConnect:** 1 Gbps port $0.018/hr (relevant to on-prem, Part 2).

## 1.2 Sizing assumptions

| Assumption | Value | Notes |
|---|---|---|
| ETL compute | **~480 OCPU-hours / month** | on a **dedicated/isolated ADW OCPU pool** so ingestion ETL does not compete with the reporting warehouse (the workload-isolation point) |
| ADW staging storage | **~2 TB** | in-database staging + external tables |
| Object Storage (raw landing) | **~500 GB** | Bronze `*_RAW` analog |
| OIC message packs | **2** | orchestration + adapters for ~30 sources |
| API Gateway / Functions / other | small | inbound endpoints + Lane-1 custom pulls |
| Build labor | **~350 hours** | OIC/ODI/PL-SQL development |
| Ongoing ops labor | **~10 hours / month** | low — managed OCI |
| Cross-cloud egress | **$0** | data stays in OCI |
| GoldenGate | **$0** | in-database CDC; no cross-cloud replication |

## 1.3 Worked build-up — License-Included (monthly)

| Stream | Line | $/mo |
|---|---|---|
| **License / software** | OIC (2 packs × $943) | $1,886 |
| | ADW OCPU **license premium** ($2.6847 × 480) | $1,289 |
| | **License subtotal** | **$3,175** |
| **Infrastructure** | ADW OCPU base ($1.3441 × 480) | $645 |
| | ADW storage (2 TB × $118.40) | $237 |
| | API Gateway | ~$50 |
| | Functions | ~$30 |
| | Object Storage (500 GB × $0.0255) | ~$13 |
| | **Infrastructure subtotal** | **$975** |
| **Labor (ops)** | 10 h/mo × $150 | $1,500 |
| | **Monthly total** | **$5,650** |

**3-yr TCO (License-Included):** $5,650 × 36 + build ($52,500) = **$255,900** — License $114,300 · Infrastructure $35,100 · Labor $106,500.

## 1.4 BYOL — the like-for-like comparator

Under **Bring-Your-Own-License** (you already own Oracle DB licenses for the EDW — very likely), the ADW **license premium disappears** and the ADW compute is billed at the BYOL rate. License collapses to **OIC only (~$1,886/mo)**; the ADW compute sits in Infrastructure. Net:

**3-yr TCO (BYOL): ~$232,716** — License $67,896 · Infrastructure $58,320 · Labor $106,500.

This BYOL figure (**~$233k**), not the Lic-Incl $256k, is the **like-for-like comparator to the Azure family** (Azure bundles no separately-owned license): ~$30k above ADF, level with Fabric, below Databricks/roll-your-own.

*Transparency note:* the model carries the full ADW compute in the BYOL **Infrastructure** line rather than netting it against the peeled-out Lic-Incl base, which makes BYOL infrastructure look higher than Lic-Incl infrastructure even though total TCO is lower. This is **conservative** — a fully-netted BYOL could come in modestly below $233k, so the headline is not overstated in Azure's favor.

## 1.5 What's load-bearing here

- **License-Included vs BYOL** is the single biggest lever (~$1,289/mo ≈ $46k/3yr). Assume BYOL for the real comparison.
- **OIC message-pack sizing** (1 vs 2 packs roughly halves/doubles ~$1,886/mo).
- **ADW OCPU-hours (480/mo)** — must be an isolated pool; if ingestion shares the reporting warehouse's OCPUs, autoscaling can inflate the EDW's own bill (the reason to prefer an external Azure tier).
- Storage, Object Storage, API Gateway, Functions — rounding error. Egress and GoldenGate are **$0** by construction.

---

# Part 2 — On-premise (approaches 6 & 7)

A full owned stack that still ships the staged tables to the OCI EDW over FastConnect. Two storage engines: **Oracle DB (approach 6)** and **SQL Server (approach 7)**; each with a Standard/SE2 base case and an Enterprise/EE reference variant. **License is accounted distinctly from hardware/infrastructure** throughout.

## 2.1 License list prices (2026) & how they're sized

| License | List basis | Modeled config | Perpetual capex | Recurring (support/SA) |
|---|---|---|---|---|
| **Oracle DB SE2** (approach 6 base) | ~$17,500 per **socket** (2-socket max) | 2 sockets | **$35,000** | 22%/yr = ~$642/mo |
| **Oracle DB EE** (6b reference) | $47,500 per **processor** | 8 cores × 0.5 x86 core-factor = **4 proc** | **$190,000** | 22%/yr = ~$3,483/mo |
| **SQL Server 2022 Standard** (approach 7 base) | $3,944 per **2-core pack** | 16 cores = 8 packs = $31,552; + Windows Server Datacenter $6,155 (16-core) | **$37,707** | ~25%/yr SA = ~$786/mo |
| **SQL Server 2022 Enterprise** (7b reference) | $15,122 per **2-core pack** | 16 cores = 8 packs = $121,000; + Windows $6,155 | **$127,155** | ~25%/yr SA = ~$2,649/mo |

ETL engine: **PL/SQL** (Oracle, no ODI license) or **SSIS** (bundled with SQL Server) — no separate ETL license modeled.

## 2.2 Infrastructure (hardware) assumptions — a planning estimate, not live-priced

| Item | Value | Notes |
|---|---|---|
| Hardware capex | **~$120,000** | 2× HA database servers + shared SAN/flash array + redundant network + backup/DR target + rack/PDU. Illustrative planning estimate. |
| Facilities / colo | **~$1,200 / mo** | rack, power, cooling |
| **FastConnect to OCI** | **~$1,013 / mo** | OCI 1 Gbps port (~$13) + carrier/cross-connect circuit (~$1,000). *This is the on-prem analog of egress — a real recurring line the cloud options don't carry, because the staged tables must still reach the OCI EDW.* |
| Hardware maintenance/support | **~$300 / mo** | |
| **Infrastructure monthly** | **~$2,513 / mo** | colo + FastConnect + maintenance |

Storage sits on the SAN (part of the $120k) — ~2 TB usable is trivial for an HA array sized for IOPS/redundancy, so it is not a separate line. Bandwidth = the FastConnect circuit above.

## 2.3 Labor assumptions

- **Build:** Oracle ~500 hours ($75,000) · SQL Server ~450 hours ($67,500) @ $150/hr blended.
- **Ongoing ops:** **~30 hours/month** DBA + sysadmin ($4,500/mo) — the largest recurring line after hardware amortization, and the reason on-prem is labor-heavy.

## 2.4 Worked 3-yr TCO (license · infrastructure · labor)

| Approach | License 3yr | Infrastructure 3yr | Labor 3yr | **3-yr TCO** |
|---|---|---|---|---|
| **6. On-prem Oracle SE2** | $35,000 + $642×36 = **$58,112** | $120,000 + $2,513×36 = **$210,468** | $75,000 + $4,500×36 = **$237,000** | **$505,580** |
| **7. On-prem SQL Server Std** | $37,707 + $786×36 = **$66,003** | **$210,468** | $67,500 + $4,500×36 = **$229,500** | **$505,971** |
| *6b. On-prem Oracle EE (ref)* | $190,000 + $3,483×36 = **$315,388** | $210,468 | $237,000 | **$762,856** |
| *7b. On-prem SQL Enterprise (ref)* | $127,155 + $2,649×36 = **$222,519** | $210,468 | $229,500 | **$662,487** |

## 2.5 What the on-prem numbers show

- **On-prem is ~3× ADF** (~$506k vs ~$159k), and for the Standard/SE2 tiers it is **dominated by infrastructure (~$210k/3yr) + labor (~$237k/3yr), not license** (~$58–66k, ~11–13% of TCO).
- **The Oracle EE cliff:** Enterprise Edition **license alone (~$315k/3yr) exceeds the entire ADF option (~$159k)** — the single most expensive line item in the whole comparison is a *license*, not hardware. If on-prem Oracle is chosen at all, **SE2 is near-mandatory** for a staging tier.
- On-prem **still ships to OCI** — the FastConnect circuit (~$1,013/mo) is a permanent line the cloud options don't have, and it adds a landing hop back that OCI-native removes.

## 2.6 What's load-bearing here

- **License tier** (SE2↔EE, Std↔Ent) — the only lever big enough to move the answer, and it moves it a lot (Oracle EE nearly doubles the TCO).
- **Hardware capex ($120k)** and **ops hours (30/mo)** — the two largest streams; both planning estimates.
- **Enterprise discounts (50–80% off Oracle/MS list) are NOT applied** — the single biggest caveat on the license figures; a negotiated deal would compress the EE/Enterprise gap.
- Storage is not a separate line; FastConnect is the bandwidth line.

---

## Provenance & how to reprice

- **Model:** `seven_approach_cost_model.py` — edit the `A` (headline approaches) and `VARIANTS` (reference license paths) dicts, plus the `GG` / `EGRESS` contingency blocks, and re-run.
- **Machine-readable figures:** `seven-approach-figures.json` (approaches, reference variants, contingencies, ops decomposition, license list prices).
- **Azure variants A–D basis:** `../model/ASSUMPTIONS.md`.
- **GoldenGate contingency** (telematics CDC; applies to Azure approaches, $0 for OCI-native): see `../model/ASSUMPTIONS.md` §7 and `seven-approach-figures.json` → `contingencies`.

*Off-Azure Assumptions & Basis v1 — 2026-07-23 — John-Michael Scott / GreenData Ventures. Planning estimates pending confirmation with Oracle/Microsoft (discounts) and a colo/carrier quote.*

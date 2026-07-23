# Alternates — full 7-approach comparison with License vs Infrastructure split

This folder extends the core Azure analysis (`../proposals/`) with two additional architectural strategies and re-costs **all seven approaches** with **license cost and infrastructure cost as distinct line items** (plus labor), per requirement.

**Contents**
- `alternate-1-oci-native.md` — Oracle OCI-native ingress + in-database ETL (approach 5)
- `alternate-2-on-premise.md` — on-premise stack with SQL Server or Oracle DB storage (approaches 6 & 7)
- `seven_approach_cost_model.py` — reproducible model; license/infra/labor, capex + monthly, 3-yr TCO
- `seven-approach-figures.json` — machine-readable figures for Claude design
- `content-corpus-addendum.md` — feed-ready content for the two new approaches + the 7-way view

---

## The seven approaches

| # | Approach | Family | Pipeline / engine | Storage container |
|---|---|---|---|---|
| 1 | **ADF** | Azure managed | Azure Data Factory | Azure SQL |
| 2 | **Databricks** | Azure managed | Databricks Workflows/Spark | ADLS Delta + SQL |
| 3 | **Fabric** | Azure managed | Fabric Data Factory | OneLake / Warehouse |
| 4 | **Roll-your-own** | Azure DIY | Durable Functions + Container Apps | Azure SQL |
| 5 | **Oracle OCI-native** | OCI | OIC + API Gateway + Data Transforms | Autonomous DW (in-DB) |
| 6 | **On-prem Oracle DB** | On-premise | PL/SQL (or ODI) | Oracle SE2/EE |
| 7 | **On-prem SQL Server** | On-premise | SSIS | SQL Server Std/Ent |

---

## License vs Infrastructure vs Labor — 3-year totals

*Cloud unit prices: live Azure Retail (West US, 2026-07-22) + published OCI list. License list prices (2026): Oracle DB EE $47,500/proc, SE2 ~$17,500/socket (+22%/yr support); SQL 2022 Std $3,944 / Ent $15,122 per 2-core pack (+~25%/yr SA); OIC ~$943/mo/pack; ADW OCPU $4.0288 Lic-Incl / $1.3441 BYOL. On-prem hardware/labor are documented planning estimates. 3-yr TCO = capex + 36×monthly.*

| Approach | License (3yr) | Infrastructure (3yr) | Labor (3yr) | Capex | Monthly recurring | **3-yr TCO** |
|---|---|---|---|---|---|---|
| 1. ADF | $26,964 | $32,580 | $99,450 | $56,250 | $2,854 | **$158,994** |
| 2. Databricks | $19,512 | $42,660 | $168,900 | $82,500 | $4,127 | **$231,072** |
| 3. Fabric | $84,096 | $12,060 | $106,950 | $63,750 | $3,871 | **$203,106** |
| 4. Roll-your-own | $7,128 | $30,024 | $351,000 | $135,000 | $7,032 | **$388,152** |
| 5. Oracle OCI-native (Lic-Incl) | $114,300 | $35,100 | $106,500 | $52,500 | $5,650 | **$255,900** |
| 6. On-prem Oracle SE2 | $58,112 | $210,468 | $237,000 | $230,000 | $7,655 | **$505,580** |
| 7. On-prem SQL Server Std | $66,003 | $210,468 | $229,500 | $225,207 | $7,799 | **$505,971** |

**Reference variants (license extremes):** OCI-native BYOL → **$232,716** (license drops to OIC-only); On-prem Oracle **EE** → **$762,856** (license alone ~$315k/3yr); On-prem SQL **Enterprise** → **$662,487**.

### License / Infrastructure / Labor as a share of TCO

| Approach | License | Infra | Labor |
|---|---|---|---|
| 1. ADF | 17% | 20% | 63% |
| 2. Databricks | 8% | 18% | 73% |
| 3. Fabric | 41% | 6% | 53% |
| 4. Roll-your-own | 2% | 8% | 90% |
| 5. OCI-native (Lic-Incl) | 45% | 14% | 42% |
| 6. On-prem Oracle SE2 | 11% | 42% | 47% |
| 7. On-prem SQL Server Std | 13% | 42% | 45% |

---

## What the license/infrastructure split reveals

1. **License is an explicit, separable SKU on-prem and in Oracle OCI; the hyperscalers bundle it into the service rate.** That's exactly why you asked to separate it: only when it's pulled out can you see that **Fabric is ~41% license** (a pure capacity subscription), **Databricks DBU is a software license on rented infrastructure**, and **OCI License-Included is 45% license** — versus **roll-your-own at 2%**, which trades license away for labor.

2. **On-prem cost is dominated by infrastructure (hardware) + labor, not license — for the Standard/SE2 tiers.** Hardware (~$120k capex → ~$210k/3yr with facilities + FastConnect) and DBA/sysadmin labor (~$162k/3yr) are the real on-prem premium. The database license is the *smaller* part — until you choose Oracle Enterprise Edition.

3. **Oracle Enterprise Edition license alone (~$315k over 3 yr) exceeds the entire Azure-managed (ADF) TCO (~$159k).** The single most expensive line item in the whole comparison is a *license*, not hardware and not cloud. This is the headline argument for SE2 / SQL Standard if on-prem is chosen at all.

4. **Roll-your-own converts license into payroll.** Lowest license (2%), highest labor (90%). You stop paying Microsoft/Oracle for software and start paying engineers to build and forever maintain it.

5. **OCI-native's data gravity is its real edge.** Its License-Included headline looks expensive, but **BYOL** (you almost certainly already own Oracle licenses for the EDW) plus **zero cross-cloud egress** and **no separate platform** make it the most architecturally coherent non-Azure option (~$233k BYOL).

---

## Ranking & recommendation (unchanged, now with 6 more analyses behind it)

**3-yr TCO:** ADF $159k < Fabric $203k < Databricks $231k < OCI-native $256k < Roll-your-own $388k < On-prem SE2 $506k ≈ On-prem SQL $506k (< Oracle EE $763k).

**Recommendation stands: build on ADF.** It is the lowest total cost *and* the lowest labor-risk. The two new alternates sharpen, rather than change, that conclusion:
- **OCI-native** is the option to take seriously **if the program prioritizes single-vendor/single-cloud coherence and data gravity** — especially under BYOL. It is the strongest non-Azure choice.
- **On-premise** is justified **only by a hard data-residency/sovereignty mandate or a large existing on-prem investment to amortize** — it is ~3× the cost of ADF and concentrates hardware + operational risk on the team.
- The **license/infrastructure split** is now a permanent lens in the model: change a license tier (SE2↔EE, Std↔Ent, Lic-Incl↔BYOL) or a hardware/facilities assumption and re-run to see each lever move independently.

*Reproduce or reprice: `python3 seven_approach_cost_model.py`. All figures are planning estimates; enterprise license discounts (50–80% off list) and reservations are not applied — model both.*

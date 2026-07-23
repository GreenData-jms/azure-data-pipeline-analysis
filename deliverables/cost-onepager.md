# Cost One-Pager — Seven Approaches, License vs Infrastructure vs Labor

*3-yr TCO = capex + 36 × monthly. Cloud = live Azure Retail (West US, PAYG, 22 Jul 2026); off-cloud = published OCI list + 2026 Oracle/Microsoft license list prices. Planning estimates; enterprise discounts (50–80%) and cloud reservations (30–41%) not applied. Blended labor $150/hr (a single blended rate; senior Spark/platform work would price above it — a two-rate lever is in the model).*

> **Read the managed three as a band, not a ranking.** ADF/Fabric/Databricks ($159k/$203k/$231k) fall inside the labor-estimate noise (labor is 63–90% of each); ADF is at the low edge but the order within the trio is not a measurement. Only the **cross-family** gaps below are decisive. For **OCI-native use the BYOL figure ($233k)** as the like-for-like comparator (owned Oracle DB licenses) — it is ~$30k above ADF and level with Fabric.

| Approach | Alt | License 3yr | Infrastructure 3yr | Labor 3yr | Capex | Monthly | **3-yr TCO** |
|---|---|---|---|---|---|---|---|
| **ADF** | 0 | $26,964 | $32,580 | $99,450 | $56,250 | $2,854 | **$158,994** |
| **Fabric** | 0 | $84,096 | $12,060 | $106,950 | $63,750 | $3,871 | **$203,106** |
| **Databricks** | 0 | $19,512 | $42,660 | $168,900 | $82,500 | $4,127 | **$231,072** |
| **Oracle OCI-native** (Lic-Incl) | 1 | $114,300 | $35,100 | $106,500 | $52,500 | $5,650 | **$255,900** |
| **Roll-your-own** | 0 | $7,128 | $30,024 | $351,000 | $135,000 | $7,032 | **$388,152** |
| **On-prem Oracle DB** (SE2) | 2 | $58,112 | $210,468 | $237,000 | $230,000 | $7,655 | **$505,580** |
| **On-prem SQL Server** (Std) | 2 | $66,003 | $210,468 | $229,500 | $225,207 | $7,799 | **$505,971** |

**License extremes (reference):** OCI-native **BYOL $232,716** (license → OIC only) · On-prem Oracle **EE $762,856** (license alone ~$315k) · On-prem SQL **Enterprise $662,487**.

## Share of 3-yr TCO

| Approach | License | Infrastructure | Labor |
|---|---|---|---|
| ADF | 17% | 20% | 63% |
| Databricks | 8% | 18% | 73% |
| Fabric | 41% | 6% | 53% |
| Roll-your-own | 2% | 8% | 90% |
| OCI-native (Lic-Incl) | 45% | 14% | 42% |
| On-prem Oracle SE2 | 11% | 42% | 47% |
| On-prem SQL Server Std | 13% | 42% | 45% |

## Contingencies (outside the base TCO — both favor OCI-native)

| Contingency | When it applies | 3-yr cost | OCI-native |
|---|---|---|---|
| **GoldenGate** (telematics CDC) | only if the telematics lane needs low-latency CDC — default P2 batch needs none | ~$8k (OCI-mgd BYOL) / ~$35k (OCI-mgd Lic-Incl) / ~$58k (perpetual); applies to **every** Azure approach | **$0** (in-DB CDC) |
| **Cross-cloud egress** (Azure→OCI) | always, for any Azure approach | ~$365 (immaterial in dollars) | **$0** |

*Both are PoC exit questions. GoldenGate is the only one that could move a budget — if telematics requires it, every Azure option's license line rises and the gap to OCI-native narrows further.*

## The four things the split reveals

1. **License is explicit off-cloud, bundled in-cloud.** Fabric ≈ 41% license (capacity subscription); Databricks DBU is license on rented infra; roll-your-own only 2% (traded for labor).
2. **On-prem is hardware + people, not license** — ~85% of on-prem TCO is infrastructure + labor for the Standard/SE2 tiers.
3. **Oracle Enterprise Edition license alone (~$315k/3yr) exceeds the entire ADF TCO (~$159k).**
4. **Roll-your-own converts license into payroll** — lowest license, highest labor.

**Key list prices used:** Oracle DB EE $47,500/proc · SE2 ~$17,500/socket (+22%/yr support) · SQL 2022 Std $3,944 / Ent $15,122 per 2-core pack (+~25%/yr SA) · Windows Datacenter ~$6,155/16-core · OIC ~$943/mo/pack · ADW OCPU $4.0288 Lic-Incl / $1.3441 BYOL.

*Reproduce or reprice: `../alternates/seven_approach_cost_model.py`.*

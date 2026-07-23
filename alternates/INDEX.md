# Alternates INDEX — one-glance map

Three parallel strategy write-ups cover seven approaches. This is the fastest way in.

| Alternate | Strategy | Approaches | 3-yr TCO (range) | Write-up |
|---|---|---|---|---|
| **0** | **Azure** — dedicated tier in front of the EDW | 1 ADF · 2 Databricks · 3 Fabric · 4 Roll-your-own | **$159k – $388k** | [`alternate-0-azure.md`](alternate-0-azure.md) |
| **1** | **Oracle OCI-native** — API inbound + in-DB ETL | 5 OCI-native | **$233k (BYOL) – $256k** | [`alternate-1-oci-native.md`](alternate-1-oci-native.md) |
| **2** | **On-premise** — owned stack, ships to OCI | 6 Oracle DB · 7 SQL Server | **$506k – $763k** | [`alternate-2-on-premise.md`](alternate-2-on-premise.md) |

## Every approach at a glance (ranked by 3-yr TCO)

| Rank | # | Approach | Alt | License 3yr | Infra 3yr | Labor 3yr | **3-yr TCO** |
|---|---|---|---|---|---|---|---|
| 1 | 1 | ADF | 0 | $26,964 | $32,580 | $99,450 | **$158,994** |
| 2 | 3 | Fabric | 0 | $84,096 | $12,060 | $106,950 | **$203,106** |
| 3 | 2 | Databricks | 0 | $19,512 | $42,660 | $168,900 | **$231,072** |
| 4 | 5 | Oracle OCI-native (Lic-Incl) | 1 | $114,300 | $35,100 | $106,500 | **$255,900** |
| 5 | 4 | Roll-your-own | 0 | $7,128 | $30,024 | $351,000 | **$388,152** |
| 6 | 6 | On-prem Oracle SE2 | 2 | $58,112 | $210,468 | $237,000 | **$505,580** |
| 7 | 7 | On-prem SQL Server Std | 2 | $66,003 | $210,468 | $229,500 | **$505,971** |

*Reference variants: OCI-native BYOL $232,716 · On-prem Oracle EE $762,856 · On-prem SQL Enterprise $662,487.*

> **Ranks 1–3 are a BAND, not an order.** ADF/Fabric/Databricks ($159k/$203k/$231k) sit inside the labor-estimate noise — ADF at the low edge, but the sequence within the trio is not a measurement. Only the cross-family gaps (managed band vs OCI-native vs roll-your-own vs on-prem) are decisive. For OCI-native, **BYOL $233k** is the like-for-like comparator (owned Oracle licenses), ~$30k above ADF and level with Fabric.

## The one-line verdict

**Build on ADF (alternate 0)** — low edge of the managed cost band, lightest build, lowest labor risk. **OCI-native (alt 1)** is the strongest non-Azure option and closer than the ranking implies (BYOL ~$233k) — data gravity + zero cross-cloud egress + no GoldenGate; prefer Azure over it on **workload isolation + connector breadth**, not cost. **On-premise (alt 2)** is justified only by a data-residency/sovereignty mandate or existing on-prem investment; it runs ~3× ADF, and Oracle Enterprise Edition's license alone exceeds the entire ADF TCO. *Scope invariant: every approach lands in Oracle staging and Power BI consumes the Oracle EDW downstream — BI-platform nativeness is not a selection factor.*

## Where things live

- **Numbers (machine-readable):** [`seven-approach-figures.json`](seven-approach-figures.json) · reprice with [`seven_approach_cost_model.py`](seven_approach_cost_model.py)
- **Full 7-way comparison + license/infra findings:** [`README.md`](README.md)
- **Feed-ready content for Claude design:** [`content-corpus-addendum.md`](content-corpus-addendum.md) (+ `../corpus/`)
- **Azure depth:** [`../proposals/`](../proposals) · [`../model/`](../model)

*All figures are planning estimates (2026 list/live prices); enterprise discounts and cloud reservations not applied.*

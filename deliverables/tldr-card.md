# TL;DR — ERC EDW Ingress: seven ways, priced

**Build on ADF.** We costed seven ways to build the tier that feeds the ERC EDW — three Azure managed (ADF, Databricks, Fabric), Azure roll-your-own, Oracle OCI-native, and two on-prem (Oracle DB, SQL Server) — with **license, infrastructure, and labor as separate line items**.

- **3-yr TCO:** ADF **$159k** < Fabric $203k < Databricks $231k < OCI-native $256k < roll-your-own $388k < on-prem ~$506k (Oracle EE $763k).
- **ADF is lowest total cost and lowest labor risk** → recommended baseline; graduate heavy workstreams to Databricks; PoC Fabric.
- **License is explicit off-cloud, bundled in-cloud:** Fabric ≈ 41% license; roll-your-own trades license for a 90% labor bill.
- **On-prem is hardware + people, not license** — ~3× ADF — and **Oracle Enterprise Edition's license alone (~$315k) tops the entire ADF budget.**
- **OCI-native** removes the cross-cloud hop (ingest where the EDW already lives); **~$233k under BYOL** — the strongest non-Azure option.

*Next: a 2–3 week two-feed PoC into OCI Bronze. Planning estimates; discounts/reservations not applied. Repo: `GreenData-jms/azure-data-pipeline-analysis`.*

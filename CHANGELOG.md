# Changelog

All notable changes to the Azure Data Pipeline Analysis project.

## [alternates-v1] — 2026-07
- Added `alternates/` folder extending the analysis from 4 Azure options to **all 7 approaches**.
- **Alternate 1 — Oracle OCI-native** (approach 5): API inbound to OCI, in-database ETL via OIC + OCI API Gateway + Oracle Data Transforms/PL-SQL; zero cross-cloud egress; License-Included vs BYOL.
- **Alternate 2 — On-premise** (approaches 6 & 7): full owned stack with SQL Server or Oracle DB storage; complete componentry; license cost accounted **distinctly from hardware/infrastructure**.
- Added `seven_approach_cost_model.py` + `seven-approach-figures.json`: **license / infrastructure / labor** as distinct streams (capex + monthly) across all 7 approaches, with 3-yr TCO.
- Added `content-corpus-addendum.md` (feed-ready for Claude design) and new analysis pillars 7–10.
- Key finding: ADF lowest TCO ($159k); on-premise ~$506k (hardware+labor driven); Oracle EE license alone (~$315k/3yr) exceeds the entire ADF TCO. License is explicit off-cloud, bundled in hyperscaler rates.

## [corpus-v1] — 2026-07
- Added `corpus/content-corpus.md` (feed-ready content source of truth) and `corpus/figures.json` (machine-readable numbers).
- Added `DELIVERABLES.md` (analysis-deliverable definitions for Claude design).
- Initialized GitHub repo `GreenData-jms/azure-data-pipeline-analysis` and synced all artifacts.

## [v0.3] — 2026-07
- Added Variant D — roll-your-own (Durable Functions + handlers + Container Apps Jobs) + ongoing-ops-labor dimension.
- Verdict: ADF optimal on total cost, not run cost. DIY cheapest to run (~$1,032/mo) but highest 3-yr TCO among the Azure four (~$388k).

## [v0.2] — 2026-07
- Reframed as three peer pipeline platforms (ADF vs Databricks vs Fabric) + live-priced bottoms-up cost model (Azure Retail, West US, 2026-07-22).
- Capability-parity matrix, per-option cost buildups, 3-yr TCO, sensitivity. Finding: managed run costs converge; fit and effort decide.

## [v0.1] — 2026-07
- Initial proposal: Azure ingest→cleanse→ETL→stage tier in front of the Oracle OCI EDW.
- Three-lane ingress (External API / Internal SSOR / Other-Dept SSOR); DQ/quarantine framework (ERC v3.0); three OCI landing patterns; source-to-technique mapping.

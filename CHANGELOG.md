# Changelog

All notable changes to the Azure Data Pipeline Analysis project.

## [corpus-v1] — 2026-07
- Added `corpus/content-corpus.md`: feed-ready content source of truth (context, master fact base, six analysis pillars, TL;DR blocks, executive summary, 12-slide presentation outline, audience framings, soundbites, glossary).
- Added `corpus/figures.json`: machine-readable single source of truth for all numbers.
- Added `DELIVERABLES.md`: analysis-deliverable definitions for Claude design.
- Initialized GitHub repo `GreenData-jms/azure-data-pipeline-analysis` and synced all artifacts.

## [v0.3] — 2026-07
- Added **Variant D — roll-your-own** (Durable Functions + per-source handlers + Container Apps Jobs).
- Added the **ongoing-ops-labor** dimension to the cost model (hrs/month per option).
- Verdict on "is ADF the optimal-priced choice?": ADF optimal on **total** cost, not on run cost. DIY is cheapest to run (~$1,032/mo) but highest 3-yr TCO (~$388k, ~2.4× ADF).
- Live-priced Functions (Consumption + Premium) and Container Apps meters.

## [v0.2] — 2026-07
- Reframed as **three peer pipeline platforms** (ADF vs Databricks vs Fabric), each equally capable, replacing the v0.1 "ADF + supporting techniques" framing.
- Added the **live-priced bottoms-up cost model** (`erc_azure_cost_model.py`) using Azure Retail Prices (West US, PAYG, 2026-07-22) on documented volume assumptions.
- Added capability-parity matrix, per-option cost buildups, 3-yr TCO, and 0.5×/1×/2× sensitivity.
- Key finding: at this scale, managed run costs converge (~$1.5–2.7k/mo); fit and effort decide.

## [v0.1] — 2026-07
- Initial proposal: Azure ingest→cleanse→ETL→stage tier in front of the Oracle OCI EDW.
- Three-lane ingress model (External API / Internal SSOR / Other-Dept SSOR) mapped to ~30 sources.
- Data-quality/quarantine framework aligned to ERC Naming Standards v3.0.
- Three OCI landing patterns (direct JDBC · Object Storage + `DBMS_CLOUD` · GoldenGate/Data Pump).
- Source-to-technique mapping appendix.

# Changelog

All notable changes to the Azure Data Pipeline Analysis project.

## [deliverables-v1] — 2026-07
- Added `deliverables/`: content-accurate gold masters for Claude design — `deck-goldmaster.md` (14-slide spec), `executive-summary.md`, `cost-onepager.md`, `recommendation-memo.md`, `tldr-card.md`, and a handoff README.
- Built the native **gold-master deck** (`ERC_Ingress_GoldMaster_Deck.pptx`, 14 slides) from the seven-approach figures — delivered directly (not committed); `deck-goldmaster.md` is its version-controllable source.
- Next phase: re-skin/polish in Claude design from these gold masters + the figures files.

## [alternates-v1] — 2026-07
- Added `alternates/` extending the analysis from 4 Azure options to **all 7 approaches**, grouped as alternate 0 (Azure family), 1 (Oracle OCI-native), 2 (on-premise). Added `INDEX.md`.
- **Alternate 0 — Azure** (approaches 1–4): consolidated Azure family write-up.
- **Alternate 1 — Oracle OCI-native** (approach 5): API inbound + in-database ETL; zero cross-cloud egress; Lic-Incl vs BYOL.
- **Alternate 2 — On-premise** (approaches 6 & 7): full owned stack, SQL Server or Oracle DB; license accounted **distinctly from hardware/infrastructure**.
- Added `seven_approach_cost_model.py` + `seven-approach-figures.json`: license / infrastructure / labor as distinct streams (capex + monthly), 3-yr TCO. Finding: ADF lowest TCO ($159k); on-prem ~$506k (hardware+labor driven); Oracle EE license alone (~$315k/3yr) exceeds the entire ADF TCO.

## [corpus-v1] — 2026-07
- Added `corpus/content-corpus.md` + `corpus/figures.json` + `DELIVERABLES.md`. Initialized the GitHub repo and synced all artifacts.

## [v0.3] — 2026-07
- Added Variant D — roll-your-own + ongoing-ops-labor dimension. Verdict: ADF optimal on total cost, not run cost.

## [v0.2] — 2026-07
- Three peer pipeline platforms (ADF vs Databricks vs Fabric) + live-priced bottoms-up cost model + sensitivity. Finding: managed run costs converge; fit and effort decide.

## [v0.1] — 2026-07
- Initial proposal: Azure ingest→cleanse→ETL→stage tier in front of the Oracle OCI EDW. Three-lane ingress, DQ/quarantine framework (ERC v3.0), three OCI landing patterns.

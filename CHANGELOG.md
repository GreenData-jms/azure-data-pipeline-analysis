# Changelog

All notable changes to the Azure Data Pipeline Analysis project.

## [oa-fold-in v1.1] — 2026-07-23
Folded the five-pass oppositional analysis + JMS's scope clarification into every document and the model. The recommendation (ADF baseline) is unchanged and reinforced; the *justification* is corrected.
- **Scope invariant added everywhere:** every approach lands in Oracle EDW **staging**; Power BI consumes the Oracle EDW downstream of Agiline's aiWorks, invariant across approaches — so **BI-platform "nativeness" (Fabric/OneLake/Power BI) is NOT an ingress-tier selection factor.** Stripped all "Fabric = Power BI fit" *selection* framing from proposal-v0.2, alternate-0, and the corpus/deck.
- **Managed trio presented as a BAND (~$159k–$231k), not an ordinal ranking** (labor is 63–90% of each; within noise). Only cross-family gaps are stated as ordered.
- **OCI-native compared at BYOL (~$233k)**, the like-for-like case (owned Oracle licenses); Azure-over-OCI-native now rests on **workload isolation + connector breadth**, not TCO. Added the decision record to the memo.
- **Two contingencies surfaced (outside base TCO, both favor OCI-native):** conditional **GoldenGate** if telematics needs CDC (~$8k OCI-mgd BYOL / ~$35k Lic-Incl / ~$58k perpetual per 3yr; $0 for OCI-native) and cross-cloud **egress** (~$365/3yr, immaterial; $0 for OCI-native). GoldenGate/egress rates web-verified (Oracle GoldenGate $17,500/proc perpetual; OCI GoldenGate managed $0.6721/$0.1613 OCPU-hr; Azure egress ~$0.087/GB).
- **Ops-labor decomposed** into a shared connector-drift slice (~10 h/mo, constant across approaches) and engine-upkeep (differs); ADF's edge restated as "near-zero *engine* upkeep."
- **Model:** `seven_approach_cost_model.py` + `seven-approach-figures.json` gain GoldenGate/egress contingencies, ops decomposition, connector-volatility + two-rate levers, and a presentation (band) rule — base TCO figures unchanged. **PoC exit criteria re-scoped:** telematics via streaming/CDC path to settle the GoldenGate question; return real build/ops hours to collapse the band.
- Full five-pass analysis (`ERC_Ingress_Approach_OA_v1.md`) delivered to chat.

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

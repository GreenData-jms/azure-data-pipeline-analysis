# Recommendation Memo — ERC EDW Data-Ingress Tier

**To:** ERC EDW Project sponsor · **From:** John-Michael Scott (GreenData Ventures) · **Re:** Which way to build the ingress tier · **Date:** July 2026

## Recommendation

**Build the ingress tier on Azure Data Factory (ADF).** Across seven fully-costed approaches, ADF has the lowest three-year total cost (~$159k) *and* the lowest labor/operational risk. Nothing in the six alternatives changes that; they sharpen it.

## Why

- **At this workload's scale the managed platforms run close together** — the differentiator is build effort and operating fit, not the monthly bill. ADF minimizes both (lowest ops, most mature Oracle sink, fastest to a working landing).
- **Rolling our own is cheapest to run but most expensive to own** (~$388k/3yr): it trades a 2% software license for a 90% labor bill and permanent maintenance. Not worth it at this scale.
- **On-premise is ~3× ADF** (~$506k) and dominated by hardware + DBA labor, not license — and it still has to ship to OCI anyway. Oracle **Enterprise Edition** licensing alone (~$315k/3yr) exceeds the entire ADF option; if on-prem Oracle is ever chosen, Standard Edition 2 is near-mandatory.
- **Oracle OCI-native is the strongest non-Azure option** — it removes the cross-cloud hop and the landing step because ingestion runs inside the EDW's own cloud, and under BYOL lands at ~$233k. Worth keeping on the table if single-vendor coherence or data gravity becomes a priority.

## The path

1. **Baseline on ADF.** Design the landing contract and ADLS lake so nothing locks us in.
2. **Graduate heavy/streaming workstreams to Databricks** only where telematics/volume warrant — incremental, since it shares the lake and the contract.
3. **PoC Fabric** given our Power BI orientation; adopt only if it tunes to an F8-reserved capacity.
4. **Reserve on-premise / OCI-native** for a data-residency mandate (on-prem) or a single-cloud/data-gravity decision (OCI-native).

## Decision needed / next step

Approve a **2–3 week proof of concept** landing two contrasting feeds end-to-end into the OCI Bronze zone — GeoTab telematics (Lane 1) and FastTrak or CGI Advantage (Lane 3) — with the QUAR_/manifest hand-off to Billow's aiWorks (Agiline) load, run in parallel through a Fabric F-SKU trial. This converts the estimates in this memo into committed numbers and validates the landing contract with Billow before the full build.

*All figures are planning estimates (live Azure retail + 2026 license list prices); enterprise discounts and reservations not applied. Full analysis: `GreenData-jms/azure-data-pipeline-analysis`.*

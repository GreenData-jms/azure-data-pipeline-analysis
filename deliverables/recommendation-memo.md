# Recommendation Memo — ERC EDW Data-Ingress Tier

**To:** ERC EDW Project sponsor · **From:** John-Michael Scott (GreenData Ventures) · **Re:** Which way to build the ingress tier · **Date:** July 2026

## Recommendation

**Build the ingress tier on Azure Data Factory (ADF).** Across seven fully-costed approaches, ADF sits at the low edge of the managed-Azure cost band with the lowest build and labor/operational risk. The recommendation is robust; the specific dollar *ranking* is not the reason for it (see below).

## Why

- **At this workload's scale the managed platforms are a band, not a ranking.** ADF (~$159k), Fabric (~$203k), and Databricks (~$231k) fall inside the labor-estimate noise — labor is 63–90% of each, and it's assumed hours × $150/hr. Don't defend the order within the trio; defend ADF's *position* (lightest build, near-zero engine upkeep, most mature Oracle sink, fastest to a working landing). The decisive gaps are cross-family, below.
- **Rolling our own is cheapest to run but most expensive to own** (~$388k/3yr): it trades a 2% software license for a 90% labor bill and permanent maintenance. Not worth it at this scale.
- **On-premise is ~3× ADF** (~$506k) and dominated by hardware + DBA labor, not license — and it still has to ship to OCI anyway. Oracle **Enterprise Edition** licensing alone (~$315k/3yr) exceeds the entire ADF option; if on-prem Oracle is ever chosen, Standard Edition 2 is near-mandatory.
- **Oracle OCI-native is the strongest non-Azure option — and closer than the headline suggests.** Compared like-for-like at **BYOL (~$233k)** — the org already owns Oracle DB licenses for the EDW — it is only ~$30k above ADF, level with Fabric, and *below* Databricks and roll-your-own. It also removes the cross-cloud hop and the landing step entirely.

## Why Azure over OCI-native (the decision record)

Because on corrected cost the gap is not decisive, the choice rests on **qualitative** grounds, not TCO:

1. **Workload isolation** — OCI-native runs cleanse/ETL *in the same Autonomous DW that serves Power BI reporting*. An external Azure tier keeps ingestion OCPU off the reporting warehouse. This is the strongest single argument and it is a technical, not a cost, one.
2. **Connector breadth** — best-of-breed managed connectors and serverless handlers for ~30 heterogeneous, externally-owned, drifting sources; OIC is less flexible for the most irregular APIs.
3. **Decoupling** — the warehouse isn't loaded by ETL, and the platform choice stays reversible behind the landing contract.

*(If single-vendor/single-cloud coherence or data gravity later dominates, OCI-native BYOL is the option to revisit — it is genuinely competitive.)*

## Two contingencies to price before committing

Both sit outside the base TCO and both favor OCI-native, so name them now: (1) if the telematics lane needs low-latency **CDC**, add **GoldenGate** — ~$8k (OCI-managed BYOL) / ~$35k (OCI-managed Lic-Incl) / ~$58k (perpetual) over three years; it applies to *every* Azure approach and is **$0** for OCI-native (in-database CDC). The default batch landing (Parquet → Object Storage + `DBMS_CLOUD`) needs none. (2) Cross-cloud **egress** is immaterial in dollars (~$365/3yr) but is the one line OCI-native zeroes. Both are PoC exit questions.

## The path

1. **Baseline on ADF.** Design the landing contract and ADLS lake so nothing locks us in.
2. **Graduate heavy/streaming workstreams to Databricks** only where telematics/volume warrant — incremental, since it shares the lake and the contract.
3. **PoC Fabric on cost grounds only** — its F8-reserved best case is the cheapest of all *if* it tunes to capacity; adopt only if the PoC clears its Oracle sink and capacity fit. (Its Power BI nativeness is **not** a factor: every approach lands in Oracle staging and Power BI consumes the Oracle EDW downstream of aiWorks, invariant across approaches.)
4. **Reserve on-premise / OCI-native** for a data-residency mandate (on-prem) or a single-cloud/data-gravity decision (OCI-native BYOL).

## Decision needed / next step

Approve a **2–3 week proof of concept** landing two contrasting feeds end-to-end into the OCI staging zone — GeoTab telematics (Lane 1) **via the intended streaming/CDC path, to settle the GoldenGate question** + FastTrak or CGI Advantage (Lane 3) via P2 — with the QUAR_/manifest hand-off to Agiline's aiWorks load (which runs Billow's PL/SQL), run in parallel through a Fabric F-SKU trial. It must return the telematics landing cost and real build/ops hours, converting the estimates in this memo into committed numbers and validating the landing contract with Billow before the full build.

*All figures are planning estimates (live Azure retail + 2026 license list prices); enterprise discounts and reservations not applied. Full analysis: `GreenData-jms/azure-data-pipeline-analysis`.*

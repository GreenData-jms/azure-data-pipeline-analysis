# Azure Data Pipeline Analysis — ERC EDW Ingress

Analysis and proposal for the **Azure data-ingress, cleanse, and staging tier** that feeds the Caltrans **Equipment Reporting Center (ERC) Enterprise Data Warehouse** (Oracle Autonomous Data Warehouse on OCI). This repo is the single source of truth for the analysis and the **connection point for Claude design** to generate downstream deliverables (TL;DRs, executive summaries, analysis pillars, presentations).

> **In one line:** Azure ingests ~30 sources across three lanes, cleans them, ETLs them into the structures the ERC logical model expects, and lands the finished tables into the OCI EDW Bronze zone — where Billow/aiWorks promotes them to Silver/Gold. This repo evaluates **four ways to build that tier** and prices them on **live Azure retail rates**.

---

## The headline finding

At the documented mid-size workload, the three managed platforms run within a **narrow cost band (~$1,500–$2,700/mo)** — so run cost is *not* the differentiator; build effort, operations, and fit are. **Roll-your-own is the cheapest to run (~$1,032/mo) but the most expensive to own (~$388k over 3 years, ~2.4× ADF)** once build and ongoing maintenance labor are counted.

**Recommendation:** build on **ADF** (lowest ops, most mature Oracle sink), graduate heavy/streaming workstreams to **Databricks** without re-platforming, and validate **Fabric** via a scoped PoC.

| Option | Run $/mo | + Ops labor | Run+Ops $/mo | Build | 3-yr TCO |
|---|---|---|---|---|---|
| **A — ADF** | $1,654 | $1,200 | **$2,854** | ~$56k | **~$159k** |
| **B — Databricks** | $1,728 | $2,400 | $4,128 | ~$83k | ~$231k |
| **C — Fabric (F16)** | $2,670 | $1,200 | $3,870 | ~$64k | ~$203k |
| **D — Roll-your-own** | **$1,032** | $6,000 | $7,032 | ~$135k | **~$388k** |

*Live Azure Retail Prices, West US, PAYG, pulled 2026-07-22. Planning estimates; see `model/`.*

---

## Repository map

```
.
├── README.md                        ← you are here (overview + index)
├── DELIVERABLES.md                  ← spec for the analysis deliverables to build in Claude design
├── CHANGELOG.md                     ← version history (v0.1 → v0.3 → corpus)
├── corpus/
│   ├── content-corpus.md            ← FEED-READY content source of truth (facts, pillars, blocks, slides)
│   └── figures.json                 ← machine-readable numbers (unit prices, per-variant run/ops/build/TCO)
├── proposals/
│   ├── proposal-v0.1.md             ← architecture, 3-lane ingress, DQ framework, OCI landing patterns
│   ├── proposal-v0.2.md             ← three peer pipelines (ADF/Databricks/Fabric) + live-priced cost model
│   └── proposal-v0.3.md             ← Variant D (roll-your-own) + ops-labor TCO lens + verdict
└── model/
    ├── erc_azure_cost_model.py       ← reproducible bottoms-up cost model (edit assumptions, re-run)
    └── README.md                     ← how to run and reprice
```

---

## How to connect this repo from Claude design

The repo is structured so Claude design can pull the right layer for whatever you're building:

1. **Point at `corpus/content-corpus.md` + `corpus/figures.json`** — these are the feed-ready inputs. The corpus §0 has copy-paste prompt patterns for each output type; the JSON keeps every figure consistent.
2. **Read `DELIVERABLES.md`** to pick which deliverable to generate — it defines each one's audience, format, source sections, and status.
3. **Cite from `proposals/` and `model/`** when you need the full technical detail or want to re-run the numbers.

Rule of thumb: **corpus for content, figures.json for numbers, proposals for depth, DELIVERABLES.md for the target.**

---

## What Azure is (and isn't) here

Azure is an **ingest → cleanse → ETL → stage tier in front of** the Oracle EDW — not a competing warehouse. It delivers clean, conformed `*_RAW` + `{TYPE}_STG` + `QUAR_` tables (ERC Naming Standards v3.0) to the OCI Bronze landing zone via one of three patterns (direct JDBC sink · Object Storage + `DBMS_CLOUD` external tables · GoldenGate/Data Pump CDC). Billow/aiWorks owns everything after that line. Because the landing contract is identical across all four options, the platform choice is **reversible**.

---

## Sources

Consolidates the Whimsical "API & SSOR Data Ingress" board, the ERC Logical Data Model v1, and the ERC EDW Unified Logical Architecture v1. Cost model uses the Azure Retail Prices API (West US, PAYG, 2026-07-22).

*Maintained by John-Michael Scott (GreenData Ventures). All cost figures are planning estimates pending a PoC.*

# Analysis Deliverables — definition & build spec

This file defines the deliverables to generate from this analysis. It is the **target list for Claude design**: each entry says what the deliverable is, who it's for, its format, which corpus sections feed it, and its status. Generate any deliverable by loading `corpus/content-corpus.md` + `corpus/figures.json` and following the source mapping below.

**Global consistency rules (apply to every deliverable):**
- Azure is a staging tier *in front of* the Oracle EDW — never a replacement.
- The four options are **peers on capability**; they differ on cost, effort, and fit.
- Cost figures are **planning estimates** (state once per artifact); numbers come from `figures.json`.
- The DIY verdict is **"cheapest to run, most expensive to own."**
- Recommendation is **ADF baseline → graduate to Databricks → PoC Fabric.**

---

## D1 — TL;DR card

- **Purpose:** instant orientation for anyone new to the decision.
- **Audience:** steering committee, execs skimming.
- **Format:** single card / half-slide / Slack-length. 1 headline + 3–4 lines.
- **Source:** corpus §5 (TL;DR blocks) + §4.5 (cost snapshot).
- **Key content:** the recommendation + the one-sentence "cheapest to run ≠ cheapest to own."
- **Status:** ready to generate.

## D2 — Executive summary (1 page)

- **Purpose:** decision-ready summary with recommendation and next step.
- **Audience:** program decision-makers, budget owner.
- **Format:** one page, prose (Situation / What we evaluated / What we found / Recommendation / Next step).
- **Source:** corpus §6 (ready-to-use exec summary) + §4.5 (cost table).
- **Status:** ready to generate.

## D3 — Analysis pillars (visual)

- **Purpose:** the load-bearing arguments, one visual per pillar.
- **Audience:** mixed technical + decision-maker.
- **Format:** 6 panels/slides — each: claim → evidence → so-what.
- **Source:** corpus §7 (the six pillars) + supporting figures from `figures.json`.
- **Pillars:** (1) staging tier not a warehouse · (2) three lanes one contract · (3) managed run costs converge · (4) DIY cheapest to run, most expensive to own · (5) cost elasticity differs by model · (6) layered recommendation.
- **Status:** ready to generate.

## D4 — Presentation deck (full)

- **Purpose:** the review-meeting deck.
- **Audience:** Caltrans review + Billow.
- **Format:** ~12 slides, matches the ERC Unified Logical Architecture deck style.
- **Source:** corpus §8 (slide-by-slide outline) + §4 (fact base) + §7 (pillars) + `figures.json` for charts.
- **Suggested charts:** run-cost bar (4 options), four-way run+ops+TCO table, 0.5×/1×/2× elasticity table.
- **Status:** outline ready in §8; generate visuals from figures.json.

## D5 — Cost comparison one-pager

- **Purpose:** the money view on a single sheet.
- **Audience:** budget owner, finance.
- **Format:** one page — the four-way table + sensitivity + basis/caveats.
- **Source:** corpus §4.5 + §4.6 (unit prices) + `figures.json` (all).
- **Status:** ready to generate.

## D6 — Technical brief

- **Purpose:** architecture-team reference.
- **Audience:** EDW architects, Billow engineers.
- **Format:** 1–2 pages — lanes, DQ framework, landing patterns, per-option architecture.
- **Source:** corpus §4 + §7 + §9-technical; proposals v0.1 (architecture/DQ/landing) + v0.2 (parity).
- **Status:** ready to generate.

## D7 — Recommendation memo

- **Purpose:** the decision and its rationale, on the record.
- **Audience:** project sponsor.
- **Format:** short memo — recommendation, why, the DIY verdict, the PoC next step.
- **Source:** corpus §6 + §7 (pillars 4 & 6) + §10 (soundbites).
- **Status:** ready to generate.

---

## Audience → framing quick map (from corpus §9)

- **Executive / stakeholder:** pick on risk and effort; ADF; DIY cheaper on the bill but ~2.4× total.
- **Decision-maker / budget owner:** run ~$1.5–2.7k/mo; the spread is build (375–900 h) + ops (8–40 h/mo).
- **Technical / architecture:** all satisfy R1–R6, share DQ framework + landing contract; graduation to Databricks is incremental.

## Provenance & maintenance

All deliverables trace to `corpus/content-corpus.md` (§13 provenance) and `corpus/figures.json`. If the cost assumptions change, re-run `model/erc_azure_cost_model.py`, update `figures.json`, then regenerate affected deliverables. Keep `CHANGELOG.md` current.

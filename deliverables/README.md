# Deliverables — ready-to-use outputs

Content-accurate deliverables built from the analysis. Every figure traces to `../alternates/seven-approach-figures.json` and `../corpus/figures.json`. These are the **gold masters**: correct content, ready to take into Claude design for visual build/polish.

| File | What it is | Best for |
|---|---|---|
| `deck-goldmaster.md` | Slide-by-slide spec of the 14-slide deck (the native `.pptx` is delivered separately) | Re-skinning the deck in Claude design |
| `deck-build-plan.md` | **Phased build plan** for producing the deck in Claude design: HTML proof → verify → native PPTX, on the Caltrans DOE design system (14-slide core + appendix pack; ready-to-paste prompts) | Actually building the deck |
| `executive-summary.md` | One-page decision summary | Decision-makers / budget owner |
| `cost-onepager.md` | The 7-approach license/infra/labor table + findings + contingencies | Finance / procurement |
| `recommendation-memo.md` | The decision on record, with the "why Azure over OCI-native" record | Project sponsor |
| `tldr-card.md` | Half-page orientation | Steering committee / skim |

## Building the deck

Start with **`deck-build-plan.md`** — it drives Claude design through three phases with a verification gate in the middle:

1. **Phase 1 — HTML proof.** A single self-contained HTML deck (16:9 frames) on the Caltrans DOE design system, every number from the figures files — so you can verify content and brand look before any PowerPoint work.
2. **Phase 2 — Verification gate.** A checklist you sign off (numbers, framing invariants, brand) before proceeding.
3. **Phase 3 — Native PPTX.** Convert the approved HTML into an editable PowerPoint on the DOE theme — native charts (not images), native text.

`deck-goldmaster.md` remains the version-controllable slide *content* spec; `deck-build-plan.md` is the *how to build it* plan that expands it into the core + appendix structure.

## The native deck

`ERC_Ingress_GoldMaster_Deck.pptx` — a 14-slide, content-accurate, editable PowerPoint — is delivered directly (chat + the local project folder). It is **not** committed here because binary decks belong with the user and in the working folder, not in version control; `deck-goldmaster.md` is the version-controllable source of its content.

## How to use with Claude design

1. Open Claude design and attach the two figures files (`../alternates/seven-approach-figures.json`, `../corpus/figures.json`) so numbers stay exact.
2. Attach the relevant content: the corpus (`../corpus/content-corpus.md` + `../alternates/content-corpus-addendum.md`) and the deliverable spec here.
3. For the deck, follow `deck-build-plan.md`. For other deliverables (one-pager, pillar visuals), point Claude design at `../DELIVERABLES.md` for the full target spec (D1–D9).

**Consistency rules (keep the pretty version honest):** the tier sits *in front of* the Oracle EDW; seven approaches, peers on capability; license and infrastructure are distinct items; cost figures are planning estimates. Plus the v1.1 corrections — **present the managed three (ADF/Fabric/Databricks) as a BAND ~$159k–$231k, not a ranking**; compare **OCI-native at BYOL ~$233k** (not Lic-Incl $256k); prefer Azure over OCI-native on **workload isolation + connector breadth, not cost**; **BI-platform "nativeness" (Fabric/Power BI) is NOT a selection factor** (every approach lands in Oracle staging; Power BI consumes the Oracle EDW downstream of aiWorks, invariant); surface the **GoldenGate + egress contingencies** ($0 for OCI-native); keep the role chain exact (Billow stages → Agiline's aiWorks loads the EDW → Billow consumes Power BI). Recommendation: **ADF baseline** → graduate to Databricks → PoC Fabric on cost grounds; OCI-native strongest non-Azure (BYOL); on-prem only for residency/sovereignty.

## Headline numbers (for quick reference)

3-yr TCO — a band, then cross-family gaps: **ADF $159k / Fabric $203k / Databricks $231k** (managed band, ADF at low edge) « **OCI-native BYOL $233k** (Lic-Incl $256k) « roll-your-own $388k « on-prem SE2/SQL ~$506k (Oracle EE $763k). Contingencies outside the base TCO, both $0 for OCI-native: GoldenGate if telematics CDC (~$8k–58k/3yr) + egress (~$365/3yr).

*All figures are planning estimates; enterprise discounts and cloud reservations not applied. Reproduce: `../alternates/seven_approach_cost_model.py`.*

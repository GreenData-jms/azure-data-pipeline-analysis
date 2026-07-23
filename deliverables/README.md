# Deliverables — ready-to-use outputs

Content-accurate deliverables built from the analysis. Every figure traces to `../alternates/seven-approach-figures.json` and `../corpus/figures.json`. These are the **gold masters**: correct content, ready to take into Claude design for visual build/polish.

| File | What it is | Best for |
|---|---|---|
| `deck-goldmaster.md` | Slide-by-slide spec of the 14-slide deck (the native `.pptx` is delivered separately) | Re-skinning the deck in Claude design |
| `executive-summary.md` | One-page decision summary | Decision-makers / budget owner |
| `cost-onepager.md` | The 7-approach license/infra/labor table + findings | Finance / procurement |
| `recommendation-memo.md` | The decision on record, with rationale | Project sponsor |
| `tldr-card.md` | Half-page orientation | Steering committee / skim |

## The native deck

`ERC_Ingress_GoldMaster_Deck.pptx` — a 14-slide, content-accurate, editable PowerPoint — is delivered directly (chat + the local project folder). It is **not** committed here because binary decks belong with the user and in the working folder, not in version control; `deck-goldmaster.md` is the version-controllable source of its content. Take the `.pptx` into Claude design to re-skin to your visual standard, or rebuild from the spec.

## How to use with Claude design

1. Open Claude design and attach the two figures files (`../alternates/seven-approach-figures.json`, `../corpus/figures.json`) so numbers stay exact.
2. Attach the relevant content: the corpus (`../corpus/content-corpus.md` + `../alternates/content-corpus-addendum.md`) and the deliverable spec here.
3. Ask for the visual build (deck re-skin, one-pager, pillar visuals). Point it at `../DELIVERABLES.md` for the full target spec (D1–D9).

**Consistency rules (keep the pretty version honest):** the tier sits *in front of* the Oracle EDW; seven approaches, peers on capability; license and infrastructure are distinct items; cost figures are planning estimates; recommendation is ADF baseline → graduate to Databricks → PoC Fabric; OCI-native strongest non-Azure; on-prem only for residency/sovereignty.

## Headline numbers (for quick reference)

3-yr TCO: **ADF $159k** < Fabric $203k < Databricks $231k < OCI-native $256k (BYOL $233k) < roll-your-own $388k < on-prem SE2/SQL ~$506k (Oracle EE $763k).

*All figures are planning estimates; enterprise discounts and cloud reservations not applied. Reproduce: `../alternates/seven_approach_cost_model.py`.*

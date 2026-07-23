# Content Corpus Addendum — the two alternates + the 7-approach license/infra view

*Feeds Claude design alongside `../corpus/content-corpus.md` and `seven-approach-figures.json`. Extends the core corpus from 4 Azure options to all 7 approaches, adding the license-vs-infrastructure lens. Same consistency rules apply.*

---

## A. New framing statements (reuse verbatim)

- **We now evaluate seven approaches across three families:** Azure managed (ADF, Databricks, Fabric), Azure DIY (roll-your-own), and off-Azure (Oracle OCI-native, on-prem Oracle, on-prem SQL Server).
- **License and infrastructure are accounted as distinct items in every approach.** This matters because on-prem and Oracle expose license as an explicit SKU, while the hyperscalers bundle it into the consumption rate — the split is the only way to compare them honestly.
- **The cheapest total is still ADF (~$159k / 3yr); the most expensive is on-premise (~$506k, or ~$763k with Oracle Enterprise Edition).**

## B. TL;DR blocks (7-approach)

**One-liner:** *Across all seven ways to build this — three Azure managed, Azure DIY, Oracle OCI-native, and two on-prem — ADF is still the lowest total cost; on-premise runs ~3× more and Oracle Enterprise licensing alone can exceed the entire ADF budget.*

**Three-sentence:** *We priced seven ingress approaches with license, infrastructure, and labor as separate streams. The managed Azure options cluster at the low end ($159k–$231k over three years), OCI-native sits in the middle ($256k, or $233k BYOL with zero cross-cloud egress), roll-your-own is $388k (labor-heavy), and on-premise is ~$506k+ — driven by hardware and operations, not license, unless you choose Oracle Enterprise Edition, whose license alone tops $315k. ADF remains the recommendation; OCI-native is the strongest non-Azure option on data-gravity grounds.*

## C. The two new approaches (capsule)

**Oracle OCI-native (approach 5).** API inbound to OCI, ETL run *in-database* in the Autonomous DW using Oracle Integration Cloud (orchestration + API management), OCI API Gateway, OCI Functions, and Oracle Data Transforms/PL-SQL. The data never leaves OCI, so the "landing" step disappears and cross-cloud egress is zero. License-Included carries an ADW software premium (45% of TCO is license); BYOL neutralizes it. Best when the program values single-vendor/single-cloud coherence and data gravity.

**On-premise (approaches 6 & 7).** A full owned stack: HA database servers, SAN, network, backup, facilities/colo, FastConnect to OCI, plus the database license (Oracle SE2/EE or SQL Server Std/Ent), the ETL engine (PL/SQL or ODI; SSIS bundled with SQL Server), the OS (Windows for SQL Server), and DBA/sysadmin labor. Highest TCO (~$506k+), dominated by hardware and labor; still has to ship to OCI anyway. Justified only by a hard residency/sovereignty mandate or existing on-prem investment.

## D. Analysis pillars (new / extended)

**Pillar 7 — License is bundled in cloud, explicit off-cloud.** Pulling it out shows Fabric is ~41% license (a pure subscription), Databricks DBU is license on rented infra, OCI Lic-Incl is 45% license — while roll-your-own is 2% license (traded for 90% labor). Evidence: the license-share table. So-what: the "license vs infrastructure" question only has a crisp answer off-cloud; on-cloud it's an allocation, and that itself is the insight.

**Pillar 8 — On-prem's premium is hardware + people, not the database license.** For SE2 / SQL Standard, license is 11–13% of TCO; infrastructure and labor are ~85%. Evidence: on-prem TCO ~$506k = $210k infra + $230k labor + ~$60k license. So-what: "we'll just run it ourselves" mostly buys hardware and headcount, not software.

**Pillar 9 — Oracle Enterprise Edition is the budget hazard.** EE license alone (~$315k/3yr) exceeds the entire ADF TCO (~$159k). Evidence: EE variant. So-what: if on-prem Oracle is chosen at all, SE2 is almost mandatory for a staging tier.

**Pillar 10 — Data gravity favors OCI-native.** The EDW already lives in OCI; ingesting there removes the cross-cloud hop and the landing problem. Evidence: zero egress; BYOL TCO ~$233k. So-what: the strongest non-cost argument in the whole comparison, and the reason OCI-native belongs on the shortlist.

## E. Soundbites

- "License is bundled in the cloud and itemized on-prem — separating it is the only way to compare them."
- "On-prem mostly buys hardware and headcount, not software."
- "Oracle Enterprise Edition's license alone costs more than the entire cheapest cloud option."
- "Roll-your-own trades a 2% license for a 90% labor bill."
- "The warehouse is already in OCI — ingesting there makes the landing problem disappear."

## F. Presentation slides (add to the deck)

- **Slide: Seven approaches, three families** — the approach table (family / engine / storage).
- **Slide: License vs Infrastructure vs Labor** — stacked bars per approach (from figures) — the visual that answers the brief.
- **Slide: The on-prem premium** — waterfall: hardware + labor + license → $506k, vs ADF $159k.
- **Slide: The Oracle EE cliff** — EE license alone vs entire ADF TCO.
- **Slide: OCI-native data gravity** — same-cloud diagram, zero egress, BYOL $233k.

## G. Provenance

Model: `seven_approach_cost_model.py`. Figures: `seven-approach-figures.json`. License prices: Oracle/Microsoft 2026 list (web-sourced) + published OCI list; cloud from live Azure Retail. All planning estimates; enterprise discounts and reservations not applied.

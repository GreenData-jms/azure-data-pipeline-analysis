# Gold-Master Deck — slide-by-slide spec

*The content spec behind `ERC_Ingress_GoldMaster_Deck.pptx` (delivered separately as a native, editable file). This markdown is the version-controllable source Claude design re-skins from. Every number traces to `../alternates/seven-approach-figures.json`. 14 slides.*

**Palette used (swap for your brand):** deep navy `15213B`, navy `1E2761`, teal `1C7293`, ice `CADCFC`, amber accent `E8A33D`; family colors — Azure teal `1C7293`, OCI clay `C0603A`, on-prem slate `6B5B95`. Serif headers (Cambria), sans body (Calibri). Dark title/section/closing slides, light content (sandwich).

> **Attribution note:** aiWorks is **Agiline Software's** platform. The staging→EDW load is **Agiline's** job: aiWorks picks up the staged data and loads the EDW, executing **Billow's PL/SQL** scripts. Billow lands the staging (this tier) and later consumes the EDW into Power BI. aiWorks is **not** a Billow product.

---

**1 · Title (dark).** Kicker: ERC ENTERPRISE DATA WAREHOUSE. Title: *Feeding the Warehouse.* Subtitle: *Seven ways to build the data-ingress tier — priced and compared.* Three family chips (Azure · 4 approaches / Oracle OCI-native / On-premise · 2 approaches). Accent line: *Recommendation: build on ADF — low edge of the managed cost band, lowest build and labor risk.* Footer: Caltrans Division of Equipment · GreenData Ventures · July 2026 · DRAFT.

**2 · Positioning (light).** Title: *Azure sits in front of the Oracle EDW — not beside it.* Four-step flow: SOURCES (~30 feeds, 3 lanes) → INGEST·CLEANSE·ETL·STAGE (the tier this deck evaluates — Billow, ends at the staging landing) → OCI EDW STAGING (clean *_RAW / {TYPE}_STG lands here) → AGILINE aiWORKS → EDW → POWER BI (aiWorks loads the EDW running Billow's PL/SQL; Billow then consumes into Power BI). Callout: the contract line — reversible except OCI-native. Sub-callout: *BI consumption is downstream of aiWorks on the Oracle EDW and invariant across all seven approaches — so BI-platform "nativeness" (Fabric/Power BI) is not a platform-selection factor.*

**3 · Three lanes (light).** Title: *~30 sources, three connection profiles.* Three cards: Lane 1 External API (ChargePoint · Tesla · GeoTab · AssetWorks REST · NEE); Lane 2 Internal SSOR (FA + M5 · VHSP MySQL · Access · SmartSheets · XREF); Lane 3 Other-Dept / External CA (CGI Advantage · InfoAdvantage · FastTrak · CARB · US Bank · WEX · EJ Ward). Tagline: different reach, one clean-and-land pattern.

**4 · Landing contract (light).** Title: *EDW-ready tables, not raw dumps.* Left: `*_RAW`, `{TYPE}_STG`, `QUAR_`, `XREF_`. Right (dark card): P1 direct JDBC sink · P2 Parquet → Object Storage + DBMS_CLOUD (default) · P3 GoldenGate/Data Pump CDC. Naming per ERC v3.0.

**5 · Seven approaches (light, table).** Columns: Alt · Approach · Family · Pipeline/engine · Storage container. Seven rows (see figures). Legend: Alt 0 = Azure family; Alt 1 = OCI-native; Alt 2 = on-premise.

**6 · 3-yr TCO — a band, then cross-family gaps (light, horizontal bar chart).** Shade the three managed options as ONE band: ADF 159 / Fabric 203 / Databricks 231 ($k) — inside the labor-estimate noise, ADF at the low edge. Then the decisive cross-family bars: OCI-native **233 (BYOL)** / 256 (Lic-Incl) · Roll-your-own 388 · On-prem Oracle 506 · On-prem SQL 506. Callouts: *managed = a band, not a ranking; the order within it isn't a measurement.* · *use OCI-native BYOL $233k for like-for-like.* · on-premise ~3× (EE reaches $763k).

**7 · License vs Infrastructure vs Labor (light, stacked column chart).** Per approach, stacked License / Infrastructure / Labor ($k). Side table: share-of-TCO %. Note: Fabric ≈ 41% license; roll-your-own ≈ 2% license (90% labor).

**8 · What the split reveals (dark, 4 cards).** (1) Cloud bundles it, off-cloud itemizes it. (2) On-prem is hardware + people, not license. (3) Oracle Enterprise Edition is the budget hazard. (4) Roll-your-own converts license into payroll.

**9 · The on-prem premium (light).** ADF $159k (License $27k / Infra $33k / Labor $99k) ▶ On-premise $506k (~3×): Infrastructure/hardware $210k · Labor $237k · License ~$60k (smallest stream). *License is the smaller part — until Oracle EE.*

**10 · The Oracle EE cliff (dark).** Oracle EE license alone **$315k** > entire ADF option **$159k**. If on-prem Oracle at all, SE2 near-mandatory.

**11 · OCI-native: closer than the headline, and why we still choose Azure (light).** Lead with **BYOL $233k** (owned Oracle licenses) — ~$30k above ADF, level with Fabric, below Databricks/roll-your-own. No cross-cloud egress · no landing step · no GoldenGate · one vendor/one cloud. **Why Azure anyway:** (1) *workload isolation* — don't run ETL on the same ADW that serves Power BI reporting; (2) connector breadth for ~30 drifting sources; (3) decoupling + reversibility. Framed as a decision resting on architecture, **not** cost. Trade-off if chosen: Oracle/OIC lock-in.

**12 · Recommendation (dark, 4 cards).** Baseline: ADF (low edge of the band; lightest build; near-zero engine upkeep). Graduate: Databricks (telematics/high-volume; incremental). Validate: Fabric — **PoC on cost grounds only** (F8-reserved cheapest *if* it tunes; Power BI nativeness is not a factor — BI is downstream on Oracle). Only if mandated: On-premise (residency/sovereignty or sunk investment) — or revisit OCI-native BYOL if single-cloud/data-gravity dominates.

**13 · Next step (light).** A 2–3 week two-feed PoC: GeoTab telematics (Lane 1) **via the intended streaming/CDC path — to settle whether GoldenGate is required** + FastTrak/CGI Advantage (Lane 3) via P2 → OCI staging with QUAR_/manifest hand-off to Agiline's aiWorks load (which runs Billow's PL/SQL). What it buys: the telematics landing cost, real build/ops hours (collapsing the cost band into measured numbers), validated staging→EDW hand-off, parallel Fabric F-SKU trial.

**14 · Basis & caveats (light).** Cost basis; key license prices; not applied (enterprise discounts 50–80%, reservations 30–41%). **Read the managed three as a band** (order within it is inside labor-estimate noise). **Contingencies outside the base TCO, both favoring OCI-native:** conditional **GoldenGate** if telematics needs CDC (~$8k–58k/3yr; applies to every Azure approach; $0 for OCI-native — default P2 batch needs none) and cross-cloud **egress** (~$365/3yr, immaterial but zero for OCI-native). Labor is a single blended $150/hr (two-rate lever in the model). Load-bearing assumptions; open risks. Reproduce: `alternates/seven_approach_cost_model.py`.

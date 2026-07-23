# Gold-Master Deck — slide-by-slide spec

*The content spec behind `ERC_Ingress_GoldMaster_Deck.pptx` (delivered separately as a native, editable file). This markdown is the version-controllable source Claude design re-skins from. Every number traces to `../alternates/seven-approach-figures.json`. 14 slides.*

**Palette used (swap for your brand):** deep navy `15213B`, navy `1E2761`, teal `1C7293`, ice `CADCFC`, amber accent `E8A33D`; family colors — Azure teal `1C7293`, OCI clay `C0603A`, on-prem slate `6B5B95`. Serif headers (Cambria), sans body (Calibri). Dark title/section/closing slides, light content (sandwich).

> **Attribution note:** aiWorks is **Agiline Software's** aiWorks platform, which **Billow uses** (with Billow-provided PL/SQL) for the in-EDW load. It is **not** a Billow product.

---

**1 · Title (dark).** Kicker: ERC ENTERPRISE DATA WAREHOUSE. Title: *Feeding the Warehouse.* Subtitle: *Seven ways to build the data-ingress tier — priced and compared.* Three family chips (Azure · 4 approaches / Oracle OCI-native / On-premise · 2 approaches). Accent line: *Recommendation: build on ADF — lowest total cost, lowest labor risk.* Footer: Caltrans Division of Equipment · GreenData Ventures · July 2026 · DRAFT.

**2 · Positioning (light).** Title: *Azure sits in front of the Oracle EDW — not beside it.* Four-step flow: SOURCES (~30 feeds, 3 lanes) → INGEST·CLEANSE·ETL·STAGE (the tier this deck evaluates) → OCI EDW BRONZE (clean *_RAW / {TYPE}_STG lands here) → BILLOW + aiWORKS → SILVER·GOLD (Agiline aiWorks platform + Billow-provided PL/SQL → Power BI). Callout: the contract line — reversible except OCI-native.

**3 · Three lanes (light).** Title: *~30 sources, three connection profiles.* Three cards: Lane 1 External API (ChargePoint · Tesla · GeoTab · AssetWorks REST · NEE); Lane 2 Internal SSOR (FA + M5 · VHSP MySQL · Access · SmartSheets · XREF); Lane 3 Other-Dept / External CA (CGI Advantage · InfoAdvantage · FastTrak · CARB · US Bank · WEX · EJ Ward). Tagline: different reach, one clean-and-land pattern.

**4 · Landing contract (light).** Title: *EDW-ready tables, not raw dumps.* Left: `*_RAW`, `{TYPE}_STG`, `QUAR_`, `XREF_`. Right (dark card): P1 direct JDBC sink · P2 Parquet → Object Storage + DBMS_CLOUD (default) · P3 GoldenGate/Data Pump CDC. Naming per ERC v3.0.

**5 · Seven approaches (light, table).** Columns: Alt · Approach · Family · Pipeline/engine · Storage container. Seven rows (see figures). Legend: Alt 0 = Azure family; Alt 1 = OCI-native; Alt 2 = on-premise.

**6 · 3-yr TCO ranking (light, horizontal bar chart).** ADF 159 · Fabric 203 · Databricks 231 · OCI-native 256 · Roll-your-own 388 · On-prem Oracle 506 · On-prem SQL 506 ($k). Callouts: $159k ADF lowest; on-premise ~3× (EE reaches $763k).

**7 · License vs Infrastructure vs Labor (light, stacked column chart).** Per approach, stacked License / Infrastructure / Labor ($k). Side table: share-of-TCO %. Note: Fabric ≈ 41% license; roll-your-own ≈ 2% license (90% labor).

**8 · What the split reveals (dark, 4 cards).** (1) Cloud bundles it, off-cloud itemizes it. (2) On-prem is hardware + people, not license. (3) Oracle Enterprise Edition is the budget hazard. (4) Roll-your-own converts license into payroll.

**9 · The on-prem premium (light).** ADF $159k (License $27k / Infra $33k / Labor $99k) ▶ On-premise $506k (~3×): Infrastructure/hardware $210k · Labor $237k · License ~$60k (smallest stream). *License is the smaller part — until Oracle EE.*

**10 · The Oracle EE cliff (dark).** Oracle EE license alone **$315k** > entire ADF option **$159k**. If on-prem Oracle at all, SE2 near-mandatory.

**11 · OCI-native data gravity (light).** No cross-cloud egress · no landing step · one vendor/one cloud. BYOL **$233k** (you likely already own Oracle licenses). Trade-off: Oracle/OIC lock-in.

**12 · Recommendation (dark, 4 cards).** Baseline: ADF. Graduate: Databricks (telematics/high-volume; incremental). Validate: Fabric (PoC; F8-reserved competitive if tuned). Only if mandated: On-premise (residency/sovereignty or sunk investment).

**13 · Next step (light).** A 2–3 week two-feed PoC: GeoTab telematics (Lane 1) + FastTrak/CGI Advantage (Lane 3) → OCI Bronze with QUAR_/manifest hand-off to Billow's aiWorks (Agiline) load. What it buys: committed numbers, validated contract, de-risked choice, parallel Fabric F-SKU trial.

**14 · Basis & caveats (light).** Cost basis; key license prices; not applied (enterprise discounts 50–80%, reservations 30–41%); load-bearing assumptions; open risks. Reproduce: `alternates/seven_approach_cost_model.py`.

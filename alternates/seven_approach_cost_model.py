#!/usr/bin/env python3
"""
ERC EDW ingress — SEVEN-APPROACH cost model with LICENSE vs INFRASTRUCTURE split.

Approaches: 1 ADF | 2 Databricks | 3 Fabric | 4 Roll-your-own |
            5 Oracle OCI-native | 6 On-prem Oracle DB | 7 On-prem SQL Server

Each approach is decomposed into THREE distinct streams, each with a one-time
(capex) and a recurring (monthly) component:
  * LICENSE / SOFTWARE  - perpetual license (capex) + support/SA or subscription (monthly)
  * INFRASTRUCTURE      - hardware (capex) + facilities/network/consumption (monthly)
  * LABOR               - build (capex) + ongoing ops (monthly)

Cloud unit prices: live Azure Retail (West US, 2026-07-22) + published OCI list.
Oracle/MS license list prices (2026): Oracle DB EE $47,500/proc, SE2 ~$17,500/socket,
22% support; SQL 2022 Std $3,944 / Ent $15,122 per 2-core pack; OIC ~$943/mo/pack;
ADW OCPU $4.0288 Lic-Incl / $1.3441 BYOL. On-prem hardware/labor are documented
planning estimates. 3-yr TCO = capex + 36 * monthly. Edit and re-run to reprice.

NOTE ON THE SPLIT: on-prem and Oracle expose license as an explicit, separate SKU.
Hyperscaler PaaS BUNDLES license into the consumption rate; the "license" figures for
approaches 1-4 are indicative allocations of the managed-service/software portion
(ADF Data Flow engine, Databricks DBU, Fabric capacity subscription, embedded Azure
SQL license) vs the raw compute/storage/network you'd pay regardless.

------------------------------------------------------------------------------------
v1.1 (2026-07-23) — oppositional-analysis fold-in. Added, WITHOUT changing the base
TCO figures (which remain the central planning estimates):
  * SCOPE INVARIANT: every approach lands in Oracle EDW STAGING. Power BI consumes the
    Oracle EDW DOWNSTREAM of Agiline's aiWorks load (which runs Billow's PL/SQL) and is
    INVARIANT across all seven approaches -> BI-platform "nativeness" is NOT a
    differentiator for this tier.
  * CONTINGENCIES: a conditional GoldenGate line (only if the telematics lane needs
    low-latency CDC; the DEFAULT batch landing = P2 Object Storage + DBMS_CLOUD needs
    none) and an explicit cross-cloud EGRESS line (small in dollars; the one line
    OCI-native zeroes -> qualitative, not a budget-mover).
  * OPS DECOMPOSITION: ops-labor split into a SHARED connector-drift slice (roughly
    constant across approaches, driven by ~30 external sources) and an ENGINE-upkeep
    slice (the part that actually differs). ADF's advantage is "near-zero ENGINE
    upkeep," not "lowest TOTAL ops."
  * LEVERS: CONNECTOR_CHANGES_PER_SOURCE_YR and a two-rate labor option, both editable.
  * PRESENTATION: the three managed options (ADF/Fabric/Databricks) sit within the
    labor-estimate NOISE BAND (~$160k-$230k). Present them as a BAND with ADF at the
    low edge, NOT as an ordinal ranking. The decisive gaps are CROSS-FAMILY (managed
    vs roll-your-own vs OCI-native vs on-prem), which DO survive the assumptions.
------------------------------------------------------------------------------------
"""

M = 36  # months

A = {
 "1. ADF (Azure managed)": {
    "capex":   {"license": 0,      "infra": 0,      "build": 56250},
    "monthly": {"license": 749,    "infra": 905,    "ops": 1200},
    "note": "License = ADF orchestration+copy+Data Flows (managed-service software) + Logic Apps + Azure SQL license portion + Cosmos. Infra = Functions, Azure SQL compute portion, ADLS, SHIR VMs, egress, monitoring.",
 },
 "2. Databricks (Azure managed)": {
    "capex":   {"license": 0,      "infra": 0,      "build": 82500},
    "monthly": {"license": 542,    "infra": 1185,   "ops": 2400},
    "note": "License = ADF copy + Databricks DBU (software) + Azure SQL license portion. Infra = the VM half of every Databricks cluster + Event Hubs + ADLS + SQL compute + SHIR + egress + monitoring.",
 },
 "3. Fabric (Azure managed)": {
    "capex":   {"license": 0,      "infra": 0,      "build": 63750},
    "monthly": {"license": 2336,   "infra": 335,    "ops": 1200},
    "note": "License = Fabric F16 capacity (a pure software subscription — Microsoft runs the infra). Infra = OneLake storage + on-prem/VNet gateway VM + egress + monitoring. Fabric is almost ALL license. (Power BI nativeness is NOT a selection advantage here — see SCOPE INVARIANT: BI consumes the Oracle EDW downstream, invariant across approaches.)",
 },
 "4. Roll-your-own (Azure)": {
    "capex":   {"license": 0,      "infra": 0,      "build": 135000},
    "monthly": {"license": 198,    "infra": 834,    "ops": 6000},
    "note": "Serverless primitives => almost no software license (only the Azure SQL license portion). You replace license with LABOR: 900h build + 40h/mo ops.",
 },
 "5. Oracle OCI-native (Lic-Incl)": {
    "capex":   {"license": 0,      "infra": 0,      "build": 52500},
    "monthly": {"license": 3175,   "infra": 975,    "ops": 1500},
    "note": "License = OIC (2 msg packs ~$1,886) + ADW OCPU license premium (~$1,289 = the $2.6847/OCPU-hr delta of Lic-Incl over BYOL). Infra = ADW BYOL-rate compute portion + ADW/Object storage + API Gateway + Functions. NO cross-cloud egress AND NO GoldenGate — ingestion runs where the EDW already lives.",
 },
 "6. On-prem Oracle DB (SE2)": {
    "capex":   {"license": 35000,  "infra": 120000, "build": 75000},
    "monthly": {"license": 642,    "infra": 2513,   "ops": 4500},
    "note": "License capex = SE2 perpetual $35k (per-socket, 2-socket max) + 22%/yr support ($642/mo). Infra capex = 2x DB servers + SAN + network + backup ($120k); monthly = colo ($1,200) + FastConnect to OCI ($1,013) + maint ($300). Ops = DBA+sysadmin 30h/mo. ETL via PL/SQL (no ODI license). Oracle EE variant far higher (see VARIANTS).",
 },
 "7. On-prem SQL Server (Std)": {
    "capex":   {"license": 37707,  "infra": 120000, "build": 67500},
    "monthly": {"license": 786,    "infra": 2513,   "ops": 4500},
    "note": "License capex = SQL 2022 Standard 16-core ($31,552) + Windows Server Datacenter ($6,155) perpetual; +~25%/yr SA ($786/mo). SSIS bundled (no separate ETL license). Infra/ops same on-prem basis as (6). Enterprise edition variant far higher (see VARIANTS).",
 },
}

VARIANTS = {
 "5b. OCI-native (BYOL)": {
    "capex":   {"license": 0,      "infra": 0,      "build": 52500},
    "monthly": {"license": 1886,   "infra": 1620,   "ops": 1500},
    "note": "BYOL: ADW at $1.3441 vs $4.0288/OCPU-hr => ADW compute moves to Infra; license = OIC only. Assumes you already own Oracle DB licenses for the EDW (very likely). THIS ($233k), not Lic-Incl ($256k), is the like-for-like comparator to Azure (which bundles no separately-owned license).",
 },
 "6b. On-prem Oracle EE": {
    "capex":   {"license": 190000, "infra": 120000, "build": 75000},
    "monthly": {"license": 3483,   "infra": 2513,   "ops": 4500},
    "note": "Enterprise Edition $47,500/proc x 4 proc (8 cores x0.5 factor) = $190k perpetual + 22%/yr support ($3,483/mo). Partitioning/Diagnostics options extra. The Oracle-license worst case.",
 },
 "7b. On-prem SQL Server (Ent)": {
    "capex":   {"license": 127155, "infra": 120000, "build": 67500},
    "monthly": {"license": 2649,   "infra": 2513,   "ops": 4500},
    "note": "SQL 2022 Enterprise 16-core ($121,000) + Windows Datacenter ($6,155) = $127k perpetual + ~25%/yr SA ($2,649/mo).",
 },
}

# ---------------------------------------------------------------------------------
# CONTINGENCIES (v1.1) — conditional lines NOT in the base TCO. Toggle per PoC finding.
# ---------------------------------------------------------------------------------
GG_OCPU = 2          # OCPUs for a telematics CDC GoldenGate deployment (planning)
GG_HRS  = 730        # hours/month (continuous)
GG = {
  "oci_managed_lic_incl_ocpu_hr": 0.6721,   # OCI GoldenGate managed service, License-Included
  "oci_managed_byol_ocpu_hr":     0.1613,   # OCI GoldenGate managed service, BYOL
  "perpetual_per_processor":      17500,    # Oracle GoldenGate perpetual list, + 22%/yr support
  "support_pct_per_year":         22,
}
def goldengate_3yr():
    li  = GG_OCPU*GG["oci_managed_lic_incl_ocpu_hr"]*GG_HRS       # $/mo Lic-Incl managed
    byo = GG_OCPU*GG["oci_managed_byol_ocpu_hr"]*GG_HRS           # $/mo BYOL managed
    perp_cap = GG_OCPU*GG["perpetual_per_processor"]              # perpetual capex
    perp_sup = perp_cap*GG["support_pct_per_year"]/100.0          # $/yr support
    return {
      "oci_managed_lic_incl": M*li,                 # ~$35.3k / 3yr  (CENTRAL conditional)
      "oci_managed_byol":     M*byo,                # ~$8.5k  / 3yr
      "perpetual":            perp_cap + 3*perp_sup # ~$58.1k / 3yr
    }

# Cross-cloud egress (Azure -> OCI). Azure outbound ~$0.087/GB (first 100 GB/mo free).
EGRESS = {"azure_gb": 0.087, "steady_gb_mo": 75, "backfill_gb": 1500}
def egress_3yr():
    steady_billed = EGRESS["steady_gb_mo"]*EGRESS["azure_gb"]       # ~$6.5/mo if all billed
    onetime = EGRESS["backfill_gb"]*EGRESS["azure_gb"]              # ~$130 one-time
    return {"steady_mo_billed": steady_billed, "backfill_onetime": onetime, "three_yr_upper": M*steady_billed+onetime}

# ---------------------------------------------------------------------------------
# OPS DECOMPOSITION (v1.1) — connector-drift (shared) vs engine upkeep (differs).
# ---------------------------------------------------------------------------------
SOURCES = 30
CONNECTOR_CHANGES_PER_SOURCE_YR = 2      # editable lever: breaking changes / source / year
HOURS_PER_CHANGE = 2
def connector_drift_hrs_mo():
    return SOURCES*CONNECTOR_CHANGES_PER_SOURCE_YR*HOURS_PER_CHANGE/12.0   # ~10 h/mo
# Assumed TOTAL ops h/mo per approach (base): ADF 8, Databricks 16, Fabric 8, RYO 40.
OPS_HRS = {"1. ADF": 8, "2. Databricks": 16, "3. Fabric": 8, "4. Roll-your-own": 40}

# Two-rate labor lever (default model uses a single blended $150/hr).
LABOR_RATE_BLENDED = 150
LABOR_RATE_SENIOR  = 200   # Spark/platform engineering (Databricks, roll-your-own)
LABOR_RATE_STD     = 130   # low-code/config (ADF, Fabric)

def money(x): return f"${x:,.0f}"

def rollup(a):
    c, m = a["capex"], a["monthly"]
    lic   = c["license"] + M*m["license"]
    infra = c["infra"]   + M*m["infra"]
    labor = c["build"]   + M*m["ops"]
    return lic, infra, labor, lic+infra+labor, (m["license"]+m["infra"]+m["ops"]), (c["license"]+c["infra"]+c["build"])

def report(title, d):
    print("\n"+"="*100); print(title); print("="*100)
    print(f"{'Approach':<31}{'License 3yr':>13}{'Infra 3yr':>12}{'Labor 3yr':>12}{'Capex':>12}{'Mo.recur':>11}{'3yr TCO':>13}")
    print("-"*100)
    for name,a in d.items():
        lic,infra,labor,tco,mrec,capex = rollup(a)
        print(f"{name:<31}{money(lic):>13}{money(infra):>12}{money(labor):>12}{money(capex):>12}{money(mrec):>11}{money(tco):>13}")

report("SEVEN HEADLINE APPROACHES — license vs infrastructure vs labor (3-yr)", A)
report("REFERENCE VARIANTS (worst/best-case license paths)", VARIANTS)

print("\n"+"="*100)
print("LICENSE vs INFRASTRUCTURE vs LABOR — share of 3-yr TCO")
print("="*100)
print(f"{'Approach':<31}{'License':>10}{'Infra':>9}{'Labor':>9}{'3yr TCO':>13}")
print("-"*100)
for name,a in A.items():
    lic,infra,labor,tco,_,_ = rollup(a)
    print(f"{name:<31}{lic/tco*100:>9.0f}%{infra/tco*100:>8.0f}%{labor/tco*100:>8.0f}%{money(tco):>13}")

print("\n"+"-"*100); print("PRESENTATION — managed BAND vs cross-family ranking"); print("-"*100)
managed = {n:rollup(a)[3] for n,a in A.items() if "managed" in n}
lo, hi = min(managed.values()), max(managed.values())
print(f"  MANAGED trio (ADF/Fabric/Databricks) sit in a BAND {money(lo)}-{money(hi)} — inside the labor-")
print(f"  estimate noise. Present as a band with ADF at the low edge, NOT an ordinal ranking.")
print(f"  Decisive gaps are CROSS-FAMILY (below), which survive the assumptions:")
for name,tco in sorted(((n,rollup(a)[3]) for n,a in A.items()), key=lambda x:x[1]):
    tag = "  [managed band]" if "managed" in name else ""
    print(f"    {name:<31} {money(tco)}{tag}")

print("\n"+"-"*100); print("CONTINGENCIES (NOT in base TCO — toggle per PoC finding)"); print("-"*100)
gg = goldengate_3yr(); eg = egress_3yr()
print(f"  GoldenGate (ONLY if telematics needs low-latency CDC; DEFAULT P2 batch needs none):")
print(f"     OCI GoldenGate managed Lic-Incl  ~{money(gg['oci_managed_lic_incl'])}/3yr  (central conditional)")
print(f"     OCI GoldenGate managed BYOL      ~{money(gg['oci_managed_byol'])}/3yr")
print(f"     Perpetual ($17.5k/proc + 22%/yr) ~{money(gg['perpetual'])}/3yr")
print(f"     -> If required, this line applies to EVERY Azure approach equally and is a specific")
print(f"        point in OCI-native's favor (in-DB, no cross-cloud CDC). PoC exit question.")
print(f"  Cross-cloud egress (Azure->OCI): ~{money(eg['steady_mo_billed'])}/mo billed + ~{money(eg['backfill_onetime'])} one-time backfill")
print(f"     ~= {money(eg['three_yr_upper'])} over 3yr — IMMATERIAL to TCO, but the one line OCI-native zeroes (qualitative).")

print("\n"+"-"*100); print("OPS DECOMPOSITION — connector-drift (shared) vs engine upkeep (differs)"); print("-"*100)
cd = connector_drift_hrs_mo()
print(f"  Shared connector-drift maintenance ~{cd:.0f} h/mo ({SOURCES} sources x {CONNECTOR_CHANGES_PER_SOURCE_YR} breaking")
print(f"  changes/yr x {HOURS_PER_CHANGE}h) is roughly CONSTANT across ADF/Databricks/Fabric/roll-your-own.")
print(f"  Per-approach ENGINE-upkeep slice = assumed total ops - shared drift:")
for n,tot in OPS_HRS.items():
    print(f"    {n:<20} total {tot:>2} h/mo  ->  engine-upkeep ~{max(0,tot-cd):>4.0f} h/mo")
print(f"  READOUT: at {CONNECTOR_CHANGES_PER_SOURCE_YR} changes/source/yr the shared slice (~{cd:.0f}h/mo) already")
print(f"  approaches/exceeds ADF's assumed 8h/mo TOTAL — so ADF's advantage is 'near-zero ENGINE upkeep',")
print(f"  not 'lowest TOTAL ops'; and if connector volatility is high, all four converge upward.")

print("\n"+"-"*100); print("KEY READOUTS"); print("-"*100)
print("  * SCOPE INVARIANT: every approach lands in Oracle EDW STAGING; Power BI consumes the Oracle")
print("    EDW downstream of Agiline's aiWorks load and is INVARIANT -> BI-platform nativeness")
print("    (Fabric/OneLake/Power BI) is NOT an ingress-tier differentiator.")
print("  * LICENSE is an explicit, separate SKU on-prem and in Oracle OCI; the hyperscalers BUNDLE it")
print("    into the service rate (Fabric = ~all license; Databricks DBU = license on rented infra).")
print("  * The three MANAGED options sit in a ~$160k-$230k BAND (labor-estimate noise); ADF at the low")
print("    edge. The DECISIVE gaps are cross-family (roll-your-own ~$388k, OCI-native, on-prem ~$506k).")
print("  * On-prem TCO (~$506k) is dominated by INFRASTRUCTURE (hardware $120k) + LABOR (ops ~$162k/3yr),")
print("    NOT license — unless Oracle Enterprise Edition, whose license alone (~$315k/3yr) exceeds the")
print("    ENTIRE Azure Managed (ADF) TCO.")
print("  * OCI-native: compare at BYOL (~$233k), the like-for-like case (you already own Oracle DB")
print("    licenses for the EDW). Prefer Azure over it on WORKLOAD ISOLATION (don't run ETL on the ADW")
print("    that serves reporting) + connector breadth — NOT on TCO, where the gap (~$30k) is not decisive.")

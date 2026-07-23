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
    "note": "License = Fabric F16 capacity (a pure software subscription — Microsoft runs the infra). Infra = OneLake storage + on-prem/VNet gateway VM + egress + monitoring. Fabric is almost ALL license.",
 },
 "4. Roll-your-own (Azure)": {
    "capex":   {"license": 0,      "infra": 0,      "build": 135000},
    "monthly": {"license": 198,    "infra": 834,    "ops": 6000},
    "note": "Serverless primitives => almost no software license (only the Azure SQL license portion). You replace license with LABOR: 900h build + 40h/mo ops.",
 },
 "5. Oracle OCI-native (Lic-Incl)": {
    "capex":   {"license": 0,      "infra": 0,      "build": 52500},
    "monthly": {"license": 3175,   "infra": 975,    "ops": 1500},
    "note": "License = OIC (2 msg packs ~$1,886) + ADW OCPU license premium (~$1,289 = the $2.6847/OCPU-hr delta of Lic-Incl over BYOL). Infra = ADW BYOL-rate compute portion + ADW/Object storage + API Gateway + Functions. NO cross-cloud egress — ingestion runs where the EDW already lives.",
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
    "note": "BYOL: ADW at $1.3441 vs $4.0288/OCPU-hr => ADW compute moves to Infra; license = OIC only. Assumes you already own Oracle DB licenses for the EDW (very likely).",
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

print("\n"+"-"*100); print("RANKING by 3-yr TCO"); print("-"*100)
for name,tco in sorted(((n,rollup(a)[3]) for n,a in A.items()), key=lambda x:x[1]):
    print(f"  {name:<31} {money(tco)}")

print("\n"+"-"*100); print("KEY READOUTS"); print("-"*100)
print("  * LICENSE is an explicit, separate SKU on-prem and in Oracle OCI; the hyperscalers BUNDLE it")
print("    into the service rate (Fabric = ~all license; Databricks DBU = license on rented infra).")
print("  * On-prem TCO (~$506k) is dominated by INFRASTRUCTURE (hardware $120k) + LABOR (ops ~$162k/3yr),")
print("    NOT license — unless Oracle Enterprise Edition, whose license alone (~$315k/3yr) exceeds the")
print("    ENTIRE Azure Managed (ADF) TCO.")
print("  * Roll-your-own has the LOWEST license (~$7k) and the HIGHEST labor (~$351k): you convert")
print("    software license into permanent payroll.")
print("  * OCI-native's headline license looks high under License-Included, but BYOL (you already own")
print("    Oracle DB licenses for the EDW) plus ZERO cross-cloud egress makes it the strongest")
print("    single-vendor / data-gravity play.")

#!/usr/bin/env python3
"""
ERC EDW — Azure Ingress/Cleanse/Staging: bottoms-up cost model (v0.2)
Peer pipelines: ADF vs Azure Databricks vs Microsoft Fabric.

Unit prices are LIVE Azure Retail Prices (region: West US / US West, PAYG
Consumption), pulled via the Azure pricing API on 2026-07-22. Volume figures
are DOCUMENTED ASSUMPTIONS (editable below) for a mid-size Caltrans-scale
workload. Edit the ASSUMPTIONS block and re-run to reprice.
"""

HRS = 730  # avg hours/month

# ----------------------------------------------------------------------
# LIVE UNIT PRICES (USD, West US, PAYG Consumption) — Azure Retail Prices API
# ----------------------------------------------------------------------
P = {
    # ADF
    "adf_orch_cloud_per1k":      1.00,     # Cloud Orchestration Activity Run / 1,000
    "adf_orch_shir_per1k":       1.50,     # Self-Hosted Orchestration Activity Run / 1,000
    "adf_copy_diu_hr":           0.25,     # Cloud Data Movement / DIU-hour
    "adf_copy_shir_hr":          0.10,     # Self-Hosted Data Movement / hour
    "adf_dataflow_gp_vcore_hr":  0.26975,  # Mapping Data Flow General Purpose / vCore-hour
    "adf_inactive_pipeline_mo":  0.80,
    # Databricks (DBU is ON TOP of the underlying VM)
    "dbx_jobs_dbu":              0.15,     # Standard Jobs Compute DBU
    "dbx_jobs_premium_dbu":      0.30,     # Premium Jobs Compute (Photon) DBU
    "dbx_dlt_core_dbu":          0.30,     # Premium DLT Core DBU
    "dbx_allpurpose_prem_dbu":   0.55,
    # Fabric capacity — every workload meter is $0.20 / CU-hour (PAYG)
    "fabric_cu_hr":              0.20,
    "fabric_reserve_factor":     0.59,     # ~41% off with 1-yr reservation
    "onelake_hot_gb_mo":         0.026,
    # Storage
    "adls_hot_gb_mo":            0.021,    # ADLS Gen2 (HNS) Hot LRS / GB-month
    # Azure SQL DB General Purpose Gen5 (compute, PAYG) — per-hour by vCore
    "sql_gp_2vcore_hr":          0.334878,
    "sql_gp_4vcore_hr":          0.669756,
    "sql_gp_8vcore_hr":          1.339512,
    "sql_storage_gb_mo":         0.115,
    # VMs (Linux PAYG)
    "vm_d4s_v5_hr":              0.224,
    "vm_d2s_v5_hr":              0.112,
    "vm_d4s_v5_win_hr":          0.408,    # SHIR often Windows
    # Event Hubs Standard
    "eh_tu_hr":                  0.03,
    "eh_ingress_per_million":    0.028,
    # Egress (internet data transfer out, tier 1; first 100 GB/mo free)
    "egress_gb":                 0.08,
    # Variant D — roll-your-own serverless primitives
    "func_premium_vcpu_hr":      0.17,     # Premium Functions vCPU (always-ready, VNet)
    "func_premium_mem_gib_hr":   0.0122,   # Premium Functions memory
    "func_cons_gb_s":            0.000016, # Consumption execution time / GB-second
    "func_exec_per_million":     0.20,     # Consumption executions
    "aca_vcpu_s":                0.000024, # Container Apps active vCPU-second
    "aca_mem_gib_s":             0.000003, # Container Apps active memory GiB-second
}

# ----------------------------------------------------------------------
# ASSUMPTIONS (documented; edit to reprice) — mid-size Caltrans workload
# ----------------------------------------------------------------------
A = {
    "sources": 30,
    "activity_runs_mo": 3000,      # orchestration/copy activity runs across ~30 feeds + AW sub-entities
    "shir_runs_mo": 1000,          # of which run through the self-hosted IR (Lane 2 private)
    "copy_diu_hr_cloud_mo": 150,   # cloud copy DIU-hours
    "copy_shir_hr_mo": 200,        # self-hosted copy hours (Lane 2)
    "steady_ingest_gb_mo": 75,     # steady-state monthly ingested volume (telematics-dominated)
    "lake_resident_gb": 500,       # raw lake footprint retained (~13 months, compressed)
    "sql_staging_gb": 50,          # relational staging footprint (transient truncate/reload)
    "telematics_events_mo": 30_000_000,  # near-real-time telematics events/month
    "transform_cluster_hours_mo": 120,   # active cleanse/ETL cluster hours/month (batch)
    "backfill_tb_onetime": 1.5,    # one-time historical backfill volume (TB)
    # build-effort (labor) assumptions — blended rate, hours per variant
    "blended_rate": 150,           # USD/hour blended build rate (STATE-adjust as needed)
    "build_hours": {"ADF": 375, "Databricks": 550, "Fabric": 425, "RollYourOwn": 900},
    # ONGOING ops/maintenance labor (hrs/month) — the decisive dimension for DIY.
    # Managed platforms need little; a hand-built framework you must maintain yourself.
    "ops_hours_mo": {"ADF": 8, "Databricks": 16, "Fabric": 8, "RollYourOwn": 40},
}

def money(x): return f"${x:,.0f}"

# ----------------------------------------------------------------------
# VARIANT A — ADF-centric PaaS
# ----------------------------------------------------------------------
def variant_adf(cosmos=True):
    li = {}
    li["ADF orchestration (activity runs)"] = (A["activity_runs_mo"]/1000*P["adf_orch_cloud_per1k"]
        + A["shir_runs_mo"]/1000*P["adf_orch_shir_per1k"])
    li["ADF data movement (copy DIU/SHIR)"] = (A["copy_diu_hr_cloud_mo"]*P["adf_copy_diu_hr"]
        + A["copy_shir_hr_mo"]*P["adf_copy_shir_hr"])
    # Mapping Data Flow: 8-vCore GP cluster, transform_cluster_hours/mo
    li["ADF Mapping Data Flows (cleanse/ETL)"] = A["transform_cluster_hours_mo"]*8*P["adf_dataflow_gp_vcore_hr"]
    li["Azure Functions (Lane-1 API pulls)"] = 40
    li["Logic Apps (Lane-3 SFTP/file)"] = 80
    li["Azure SQL staging (4 vCore GP + storage)"] = P["sql_gp_4vcore_hr"]*HRS + A["sql_staging_gb"]*P["sql_storage_gb_mo"]
    if cosmos:
        li["Cosmos DB (JSON buffer, optional)"] = 150
    li["ADLS Gen2 (raw lake)"] = A["lake_resident_gb"]*P["adls_hot_gb_mo"]
    li["Self-hosted IR VM pair (HA)"] = 2*P["vm_d4s_v5_win_hr"]*HRS*0.5  # ~1.0 FTE-equiv sized down
    li["Egress to OCI"] = max(0,(A["steady_ingest_gb_mo"]-100))*P["egress_gb"] + 10
    li["Baseline (KeyVault/PE/monitoring)"] = 250
    return li

# ----------------------------------------------------------------------
# VARIANT B — Databricks lakehouse
# ----------------------------------------------------------------------
def variant_dbx(serving_sql=True):
    li = {}
    # keep ADF for batch orchestration + copy + SHIR
    li["ADF orchestration + copy (batch)"] = (A["activity_runs_mo"]/1000*P["adf_orch_cloud_per1k"]
        + A["shir_runs_mo"]/1000*P["adf_orch_shir_per1k"]
        + A["copy_diu_hr_cloud_mo"]*P["adf_copy_diu_hr"] + A["copy_shir_hr_mo"]*P["adf_copy_shir_hr"])
    li["Event Hubs (telematics streaming)"] = 4*P["eh_tu_hr"]*HRS + A["telematics_events_mo"]/1e6*P["eh_ingress_per_million"]
    # Batch ETL jobs cluster: 4x D4s_v5 Photon jobs; all-in node-hr = VM + ~0.75 DBU*premium
    node_hr = P["vm_d4s_v5_hr"] + 0.75*P["dbx_jobs_premium_dbu"]
    li["Databricks batch ETL (jobs cluster)"] = A["transform_cluster_hours_mo"]*4*node_hr
    # Streaming cluster ~2 nodes always-on (autoscale-tempered ~60%)
    li["Databricks streaming cluster (telematics)"] = 2*node_hr*HRS*0.6
    li["Databricks API/Auto Loader notebooks"] = 150
    li["ADLS Gen2 Delta (raw+silver)"] = A["lake_resident_gb"]*P["adls_hot_gb_mo"]
    if serving_sql:
        li["Azure SQL serving (2 vCore GP)"] = P["sql_gp_2vcore_hr"]*HRS + A["sql_staging_gb"]*P["sql_storage_gb_mo"]
    li["Self-hosted IR VM pair (HA)"] = 2*P["vm_d4s_v5_win_hr"]*HRS*0.5
    li["Egress to OCI"] = max(0,(A["steady_ingest_gb_mo"]-100))*P["egress_gb"] + 10
    li["Baseline (KeyVault/PE/monitoring)"] = 250
    return li

# ----------------------------------------------------------------------
# VARIANT C — Microsoft Fabric
# ----------------------------------------------------------------------
def variant_fabric(cu=16, reserved=False):
    li = {}
    cap = cu*P["fabric_cu_hr"]*HRS
    if reserved: cap *= P["fabric_reserve_factor"]
    label = f"Fabric capacity F{cu} ({'reserved 1-yr' if reserved else 'PAYG'})"
    li[label] = cap
    li["OneLake storage (raw + warehouse)"] = A["lake_resident_gb"]*P["onelake_hot_gb_mo"] + A["sql_staging_gb"]*0.25
    li["On-Prem/VNet Data Gateway VM"] = P["vm_d4s_v5_win_hr"]*HRS*0.5
    li["Egress to OCI"] = max(0,(A["steady_ingest_gb_mo"]-100))*P["egress_gb"] + 10
    li["Baseline (KeyVault/monitoring)"] = 150
    return li

# ----------------------------------------------------------------------
# VARIANT D — roll-your-own (Durable Functions + handlers + Container Apps)
# ----------------------------------------------------------------------
def variant_diy():
    li = {}
    # Orchestration + private-reach handlers on 1x Premium EP1 always-ready (VNet to Lane-2)
    li["Functions Premium EP1 (orchestrator+handlers, VNet)"] = (
        P["func_premium_vcpu_hr"]*HRS + 3.5*P["func_premium_mem_gib_hr"]*HRS)
    # Bursty Lane-1 API handlers on Consumption (approx GB-s + executions, net of free grant)
    li["Functions Consumption (API handler bursts)"] = 30
    # Container Apps Jobs for cleanse/ETL/landing: 4 vCPU / 8 GiB x transform hours
    hrs = A["transform_cluster_hours_mo"]*3600
    li["Container Apps Jobs (cleanse/ETL/land)"] = (4*hrs*P["aca_vcpu_s"] + 8*hrs*P["aca_mem_gib_s"])
    li["Azure SQL (staging + control/metadata, 4 vCore GP)"] = P["sql_gp_4vcore_hr"]*HRS + A["sql_staging_gb"]*P["sql_storage_gb_mo"]
    li["ADLS Gen2 (raw lake)"] = A["lake_resident_gb"]*P["adls_hot_gb_mo"]
    li["Egress to OCI"] = max(0,(A["steady_ingest_gb_mo"]-100))*P["egress_gb"] + 10
    # DIY needs MORE self-built observability (App Insights ingestion + Durable storage)
    li["Baseline (KeyVault/AppInsights/Durable storage)"] = 280
    return li

def show(name, li):
    print(f"\n=== {name} ===")
    tot = 0
    for k,v in li.items():
        print(f"  {k:<44} {money(v):>10}/mo")
        tot += v
    print(f"  {'-'*44} {'-'*10}")
    print(f"  {'MONTHLY TOTAL':<44} {money(tot):>10}/mo")
    return tot

def build_cost(v): return A["build_hours"][v]*A["blended_rate"]

print("="*66)
print("ERC AZURE INGRESS — BOTTOMS-UP COST MODEL (v0.2)")
print("Live West US retail unit prices; documented volume assumptions")
print("="*66)

a = show("VARIANT A — ADF-centric PaaS (with Cosmos)", variant_adf(True))
a_nc = sum(variant_adf(False).values())
b = show("VARIANT B — Databricks lakehouse", variant_dbx(True))
c16 = show("VARIANT C — Microsoft Fabric (F16 PAYG)", variant_fabric(16, False))
c8r = show("VARIANT C — Microsoft Fabric (F8 reserved, tuned)", variant_fabric(8, True))

print("\n" + "="*66)
print("SUMMARY — steady-state monthly run cost")
print("="*66)
rows = [
    ("A — ADF-centric PaaS", a, "A w/o Cosmos", a_nc),
    ("B — Databricks lakehouse", b, "", None),
    ("C — Fabric F16 PAYG", c16, "C F8 reserved", c8r),
]
for name, val, alt, altv in rows:
    line = f"  {name:<28} {money(val):>9}/mo"
    if alt: line += f"   ({alt}: {money(altv)}/mo)"
    print(line)

print("\n" + "="*66)
print("ONE-TIME BUILD (labor) @ ${}/hr blended".format(A["blended_rate"]))
print("="*66)
for v in ["ADF","Databricks","Fabric"]:
    print(f"  {v:<12} {A['build_hours'][v]:>4} hrs -> {money(build_cost(v))}")
print(f"  One-time historical backfill egress ~{A['backfill_tb_onetime']}TB -> "
      f"{money(A['backfill_tb_onetime']*1000*P['egress_gb'])}")

print("\n" + "="*66)
print("3-YEAR TCO (run x36 + build), PAYG / no reservation")
print("="*66)
tco = {"A — ADF": a*36+build_cost("ADF"),
       "B — Databricks": b*36+build_cost("Databricks"),
       "C — Fabric F16": c16*36+build_cost("Fabric"),
       "C — Fabric F8 reserved": c8r*36+build_cost("Fabric")}
for k,v in tco.items():
    print(f"  {k:<26} {money(v)}")

print("\n" + "="*66)
print("SENSITIVITY — monthly run cost at 0.5x and 2x volume drivers")
print("="*66)
def scaled(factor):
    # scale the volume-driven components; capacity/fixed less elastic
    base = dict(A)
    for k in ["activity_runs_mo","shir_runs_mo","copy_diu_hr_cloud_mo","copy_shir_hr_mo",
              "steady_ingest_gb_mo","lake_resident_gb","telematics_events_mo","transform_cluster_hours_mo"]:
        A[k] = base[k]*factor
    aa = sum(variant_adf(True).values())
    bb = sum(variant_dbx(True).values())
    # Fabric: capacity steps with load — approximate F8->F16->F32
    cu = 8 if factor<=0.5 else (16 if factor<=1 else 32)
    cc = sum(variant_fabric(cu, False).values())
    A.update(base)
    return aa, bb, cc, cu
for f in [0.5, 1.0, 2.0]:
    aa,bb,cc,cu = scaled(f)
    print(f"  {f:>3}x load:  A {money(aa):>8}/mo   B {money(bb):>8}/mo   C(F{cu}) {money(cc):>8}/mo")

# ======================================================================
# v0.3 ADDENDUM — Variant D (roll-your-own) + ongoing-ops-labor lens
# ======================================================================
print("\n\n" + "#"*66)
print("# v0.3 ADDENDUM — VARIANT D (ROLL-YOUR-OWN) + OPS-LABOR LENS")
print("#"*66)

d = show("VARIANT D — Roll-your-own (Durable Functions + Container Apps)", variant_diy())

# recompute A/B/C run totals for a clean 4-way table
a_run = sum(variant_adf(True).values())
b_run = sum(variant_dbx(True).values())
c16_run = sum(variant_fabric(16, False).values())
c8r_run = sum(variant_fabric(8, True).values())
d_run  = sum(variant_diy().values())

R = A["blended_rate"]
ops = {k: v*R for k,v in A["ops_hours_mo"].items()}   # $/mo ongoing ops labor
bld = {k: A["build_hours"][k]*R for k in A["build_hours"]}

print("\n" + "="*74)
print("FOUR-WAY COMPARISON — run cost vs. run+ops (the honest total)")
print("="*74)
print(f"  {'Peer':<26}{'Run $/mo':>10}{'Ops labor $/mo':>16}{'Run+Ops $/mo':>15}")
rows = [
    ("A — ADF",            a_run,   ops["ADF"]),
    ("B — Databricks",     b_run,   ops["Databricks"]),
    ("C — Fabric (F16)",   c16_run, ops["Fabric"]),
    ("D — Roll-your-own",  d_run,   ops["RollYourOwn"]),
]
for name, run, opsm in rows:
    print(f"  {name:<26}{money(run):>10}{money(opsm):>16}{money(run+opsm):>15}")

print("\n" + "="*74)
print("3-YEAR TCO — build + (run + ops)x36   [the number that decides it]")
print("="*74)
tco = {
    "A — ADF":           bld["ADF"]        + (a_run  + ops["ADF"])*36,
    "B — Databricks":    bld["Databricks"] + (b_run  + ops["Databricks"])*36,
    "C — Fabric (F16)":  bld["Fabric"]     + (c16_run+ ops["Fabric"])*36,
    "D — Roll-your-own": bld["RollYourOwn"]+ (d_run  + ops["RollYourOwn"])*36,
}
for k,v in tco.items():
    print(f"  {k:<26} 3yr {money(v)}")

print("\n" + "-"*74)
print("VERDICT ON 'IS ADF THE OPTIMAL PRICED CHOICE?'")
print("-"*74)
print(f"  Run cost alone:  D (${d_run:,.0f}/mo) BEATS A (${a_run:,.0f}/mo) by ${a_run-d_run:,.0f}/mo "
      f"(~${(a_run-d_run)*12:,.0f}/yr).")
print(f"  Add ops labor:   D (+${ops['RollYourOwn']:,.0f}/mo) vs A (+${ops['ADF']:,.0f}/mo) "
      f"= ${ops['RollYourOwn']-ops['ADF']:,.0f}/mo swing AGAINST D (~${(ops['RollYourOwn']-ops['ADF'])*12:,.0f}/yr).")
print(f"  Add build:       D ${bld['RollYourOwn']:,.0f} vs A ${bld['ADF']:,.0f} = ${bld['RollYourOwn']-bld['ADF']:,.0f} more up front.")
print(f"  => 3-yr TCO:     A {money(tco['A — ADF'])}  vs  D {money(tco['D — Roll-your-own'])}  "
      f"(D costs {tco['D — Roll-your-own']/tco['A — ADF']:.1f}x A).")
print("  => ADF is optimal on TOTAL price, NOT on the Azure bill. DIY's cheap run cost is")
print("     swamped by the maintenance labor you permanently absorb. DIY only wins if that")
print("     labor is effectively free/sunk AND sources are very stable.")

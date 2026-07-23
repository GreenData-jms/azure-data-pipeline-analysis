# Alternate 2 — On-Premise System Integration & Data Ingress

### A fully on-premise ingress/ETL stack with SQL Server or Oracle DB as the storage container, landing into the OCI EDW

*Part of the ERC EDW ingress analysis (approaches #6 and #7 of 7). Cost accounted with **license cost distinct from hardware/infrastructure**, per requirement. Companion: `alternate-1-oci-native.md`, `README.md` (7-way comparison), `seven_approach_cost_model.py`.*

---

## 1. The idea

Run the entire ingress and ETL stack **on hardware you own and operate**, with an on-premise relational database as the staging container, then ship the finished `{TYPE}_STG` tables **up to the OCI EDW Bronze zone** over a private circuit. Two storage-container options are priced separately because their licensing differs dramatically: **on-prem Oracle DB** and **on-prem SQL Server**.

This is the maximum-control, maximum-ownership option — and the one where the **license-versus-infrastructure distinction matters most**, because on-prem you buy (and separately support) the database license, the ETL engine license, and the operating-system license, *and* you buy, house, power, and refresh the physical hardware. Nothing is bundled.

---

## 2. Full componentry (work through everything)

A production on-prem system-integration ingress capability needs all of the following. Items are tagged **[L]** license/software or **[I]** infrastructure/hardware so the two streams stay distinct.

### 2.1 Compute & facilities [I]
- **Database servers** — a 2-node HA pair (e.g., dual-socket, 16 physical cores, 256–512 GB RAM, NVMe) so a node can fail without an outage.
- **Storage** — local NVMe or a shared SAN/flash array for staging volumes, redo/logs, and landing files; sized for peak batch + retention.
- **Networking** — redundant switches, firewall, load balancer; VLAN/segmentation for the integration zone.
- **Backup & DR** — backup appliance/target + offsite or second-site replication.
- **Facilities** — rack space, redundant power (UPS/PDU), cooling — owned data-center or **colocation** (~$1,000–1,500/mo/rack).
- **Private link to OCI** — **OCI FastConnect** port (~$0.018/hr for 1 Gbps) + a carrier circuit (~$500–1,500/mo) so staged data can reach the EDW.

### 2.2 Database / storage container [L]
- **Option A — Oracle Database.** SE2 (per-socket, 2-socket max, ~$17,500/socket list) or Enterprise Edition (~$47,500/processor; processor = cores × 0.5 core-factor on x86) **+ 22%/yr support**. EE options (Partitioning $11,500/proc, Diagnostics $7,500/proc) extra if needed.
- **Option B — SQL Server 2022.** Standard (~$3,944 per 2-core pack ≈ $1,972/core, min 4 cores) or Enterprise (~$15,122 per 2-core pack ≈ $7,561/core) **+ ~25%/yr Software Assurance**.

### 2.3 ETL / integration engine [L] (mostly)
- **Oracle path:** **Oracle Data Integrator (ODI)** (separately licensed, ~$30k/processor) *or* native **PL/SQL** (included with the DB — no extra license). PL/SQL keeps license down; ODI adds graphical ELT at a license cost.
- **SQL Server path:** **SSIS (SQL Server Integration Services)** — **bundled with the SQL Server license** (no separate ETL license). This is a real cost advantage of the SQL Server path.

### 2.4 API ingestion & orchestration
- **API/handler services [L/I]** — custom .NET/Java services or SSIS Script Tasks to pull Lane-1 external APIs (OAuth, pagination, JSON-RPC); an on-prem API gateway if partners push inbound.
- **Scheduler/orchestration** — SQL Agent (bundled with SQL Server) or Oracle Scheduler (bundled with Oracle DB); enterprise schedulers (Control-M/AutoSys) are extra license if required.
- **SFTP / file intake [I]** — an SFTP endpoint + landing filesystem for Lane-3 (US Bank, WEX, FastTrak, EJ Ward, InfoAdvantage).

### 2.5 Operating system [L]
- **Oracle path:** Oracle Linux (free) or RHEL (~$800/socket/yr).
- **SQL Server path:** **Windows Server** (Datacenter ~$6,155/16-core or Standard ~$1,069/16-core) — an additional license line the Oracle-on-Linux path avoids.

### 2.6 People [labor]
- **DBAs + sysadmins** for patching, backups, HA failover testing, capacity, security hardening, hardware lifecycle — materially higher than any managed-cloud option (~30 h/mo modeled).

### 2.7 Landing to the OCI EDW
- **Oracle → OCI:** Data Pump export/import or **Oracle GoldenGate** replication, or SQL*Net over FastConnect, into `ERC_*_BRZ`. Homogeneous Oracle-to-Oracle is clean.
- **SQL Server → OCI:** heterogeneous — export to flat/Parquet → OCI Object Storage → `DBMS_CLOUD` into Bronze (an extra conversion hop the Oracle path avoids).

---

## 3. Cost — license vs hardware/infrastructure (distinct items)

*License list prices (2026): Oracle SE2 ~$17,500/socket & EE $47,500/proc (+22%/yr support); SQL 2022 Std $3,944 / Ent $15,122 per 2-core pack (+~25%/yr SA); Windows Datacenter ~$6,155/16-core. Hardware & facilities are documented planning estimates. Capex amortization is shown via the 3-yr TCO (capex + 36×monthly).*

### 3.1 On-prem Oracle DB — Standard Edition 2 (the sane Oracle choice)

| Stream | Capex (one-time) | Monthly recurring | 3-yr total |
|---|---|---|---|
| **License / software** | $35,000 (SE2 perpetual, 2-socket; PL/SQL ETL, no ODI) | $642 (22%/yr support) | **$58,112** |
| **Infrastructure / hardware** | $120,000 (servers + SAN + network + backup) | $2,513 (colo $1,200 + FastConnect $1,013 + maint $300) | **$210,468** |
| **Labor** | $75,000 (build, 500 h) | $4,500 (ops, 30 h/mo) | $237,000 |
| **Total** | | | **~$505,580** |

### 3.2 On-prem SQL Server — Standard Edition (SSIS bundled)

| Stream | Capex (one-time) | Monthly recurring | 3-yr total |
|---|---|---|---|
| **License / software** | $37,707 (SQL Std 16-core $31,552 + Windows Datacenter $6,155) | $786 (~25%/yr SA) | **$66,003** |
| **Infrastructure / hardware** | $120,000 | $2,513 | **$210,468** |
| **Labor** | $67,500 (build, 450 h — SSIS is productive) | $4,500 | $229,500 |
| **Total** | | | **~$505,971** |

### 3.3 The license extremes (reference variants)

- **Oracle Enterprise Edition:** license capex ~$190,000 (4 proc) + $3,483/mo support → **license alone ~$315k over 3 yr** and total TCO **~$763k**. Oracle EE license by itself exceeds the *entire* Azure-managed (ADF) 3-yr TCO.
- **SQL Server Enterprise:** license capex ~$127,155 + $2,649/mo SA → license ~$223k / total **~$662k**.

**Read:** on-prem TCO (~$506k for the Standard/SE2 tiers) is **~3× the lowest cloud option**, and it is driven by **hardware (~$210k) + labor (~$230k), not license** — for the Standard tiers. Move to Oracle EE and *license* becomes the dominant line. Either way, the license and infrastructure costs are now visible as separate, controllable levers.

---

## 4. Why choose it — and why not

**Strengths.** Total control and data sovereignty (all data stays on owned hardware until it ships to OCI); no hyperscaler dependency; predictable, owned assets; can satisfy regulatory/residency constraints a cloud can't; SQL Server + SSIS is a genuinely economical, well-understood stack.

**Limits.** Highest TCO by a wide margin (~$506k+ over 3 yr) driven by hardware capex and ops labor; you own patching, HA, backups, DR, refresh, and security; slowest to stand up; still must ship to OCI anyway (FastConnect + a landing hop), so it doesn't remove the cloud dependency it appears to — it just adds an on-prem tier in front of it. Oracle EE licensing is a budget hazard.

**Best when:** there is a hard data-residency/sovereignty or existing-datacenter mandate, or a large sunk investment in on-prem infrastructure and DBA staff to amortize. Absent those, it is the most expensive way to solve this problem — and the analysis exists precisely so the license and infrastructure premiums are explicit rather than hidden.

---

## 5. Risks & assumptions

Hardware sizing/refresh cadence (5-yr amortization assumed) · colo vs owned-DC facilities cost · FastConnect circuit pricing varies by carrier · DBA/sysadmin labor is the largest recurring line and the easiest to under-budget · Oracle EE licensing (core-factor, options, audit exposure) is a major risk — SE2 or SQL Standard strongly preferred for a staging tier · SQL Server → Oracle landing adds a heterogeneous conversion hop · HA/DR design materially changes hardware count and license (passive-node rules differ by vendor). All figures are planning estimates; license list prices typically discount 50–80% in enterprise agreements — model both list and expected-discount.

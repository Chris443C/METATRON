# 🔱 METATRON
### AI-Powered Professional Penetration Testing Platform

<p align="center">
  <img src="screenshots/banner.png" alt="Metatron Banner" width="800"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python"/>
  <img src="https://img.shields.io/badge/OS-Parrot%20Linux-green?style=for-the-badge&logo=linux"/>
  <img src="https://img.shields.io/badge/AI-metatron--qwen-red?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/DB-MariaDB-orange?style=for-the-badge&logo=mariadb"/>
  <img src="https://img.shields.io/badge/PCI%20DSS-11.4.5-purple?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge"/>
</p>

---

## 📌 What is METATRON?

**METATRON** is a CLI-based AI penetration testing platform that runs entirely on your local machine — no cloud, no API keys, no subscriptions.

It covers the **full professional pentest lifecycle** across 10 phases: from pre-engagement scope management through reconnaissance, enumeration, vulnerability analysis, exploitation planning, post-exploitation, cloud assessment (AWS/Azure/GCP), PCI DSS 11.4.5 segmentation testing, and professional PDF reporting.

The local AI model (`metatron-qwen` via Ollama) acts as your analyst — it analyzes tool output, chains vulnerabilities into attack paths, generates executive summaries, and suggests exploitation steps. You execute; METATRON advises.

---

## ✨ Features

### Core
- 🤖 **Local AI Analysis** — powered by `metatron-qwen` via Ollama, runs 100% offline
- 🔍 **12 Recon & Enum Tools** — nmap, whois, whatweb, curl, dig, nikto, sublist3r, theHarvester, gobuster, dirb, masscan, ffuf
- 🌐 **Web Search** — DuckDuckGo + CVE lookup (no API key needed)
- 🗄️ **MariaDB Backend** — 13 linked tables with full scan and engagement history
- 🔁 **Agentic Tool Loop** — AI requests additional tool runs mid-analysis

### 10-Phase Methodology
| Phase | Name | What METATRON Does |
|-------|------|--------------------|
| 1 | Pre-Engagement | Scope wizard, RoE, test type, out-of-scope enforcement |
| 2 | Reconnaissance | 12 tools + AI recon analysis with scope checking |
| 3 | Enumeration | SMB, web dirs, API discovery, LDAP + AI enum analysis |
| 4 | Vulnerability Analysis | Attack path chaining, CVSS scoring, false positive filtering |
| 5 | Exploitation | Human-led; AI generates exact commands and payloads |
| 6 | Post-Exploitation | Technique recording, Empire safe enumeration, impact scoring |
| 7 | Reporting | Executive summary, professional PDF with evidence appendix |
| 8 | Retest | Before/after comparison, remediation score, retest PDF |
| 9 | Cloud Assessment | AWS, Azure, GCP CLI assessment + AI cloud analysis |
| 10 | Segmentation Testing | PCI DSS 11.4.5 ncat/nc/socket testing with evidence table |

### Cloud & Compliance
- ☁️ **AWS / Azure / GCP** — CLI-based assessment with AI finding analysis
- 🛡️ **PowerShell** — Az, Microsoft Graph, AWS PowerShell wrappers
- 📋 **PCI DSS 11.4.5** — Segmentation testing with chain-of-custody evidence table
- 🎯 **Empire Integration** — Read-only enumeration via REST API (SAFE_MODULES whitelist enforced)

### Reporting
- 📄 **Professional PDF** — cover page, exec summary, scope, findings, attack paths, post-exploit, cloud findings, PCI segmentation table, evidence appendix
- 🌐 **HTML Reports** — browser-viewable scan results
- 🔁 **Retest Reports** — remediation score, FIXED/NOT FIXED comparison table

---

## 🖥️ Screenshots

<p align="center">
  <img src="screenshots/main_menu.png" alt="Main Menu" width="700"/>
  <br><i>Main Menu</i>
</p>

<p align="center">
  <img src="screenshots/scan_running.png" alt="Scan Running" width="700"/>
  <br><i>Recon tools running on target</i>
</p>

<p align="center">
  <img src="screenshots/ai_analysis.png" alt="AI Analysis" width="700"/>
  <br><i>metatron-qwen analyzing scan results</i>
</p>

<p align="center">
  <img src="screenshots/results.png" alt="Results" width="700"/>
  <br><i>Vulnerabilities saved to database</i>
</p>

<p align="center">
  <img src="screenshots/export_menu.png" alt="Export Menu" width="700"/>
  <br><i>Export scan results as PDF or HTML</i>
</p>

---

## 🧱 Tech Stack

| Component  | Technology                          |
|------------|-------------------------------------|
| Language   | Python 3                            |
| AI Model   | metatron-qwen (fine-tuned Qwen 3.5) |
| Base Model | huihui_ai/qwen3.5-abliterated:9b    |
| LLM Runner | Ollama                              |
| Database   | MariaDB                             |
| OS         | Parrot OS (Debian-based)            |
| Search     | DuckDuckGo (free, no key)           |
| Reporting  | ReportLab (PDF generation)          |

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/Chris443C/METATRON.git
cd METATRON
```

### 2. Create and activate virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Install system tools

```bash
# Core tools
sudo apt install nmap whois whatweb curl dnsutils nikto

# Phase 3 enumeration tools
sudo apt install gobuster dirb masscan

# Segmentation testing
sudo apt install ncat netcat-openbsd

# Optional: subdomain and OSINT tools
sudo apt install sublist3r theharvester
```

> **Note:** `enum4linux` is not in the Ubuntu/Debian apt repos. METATRON automatically falls back to nmap SMB scripts if it is not found. To install it manually:
> ```bash
> cd /opt && sudo git clone https://github.com/CiscoCXSecurity/enum4linux.git
> sudo ln -s /opt/enum4linux/enum4linux.pl /usr/local/bin/enum4linux
> ```

> **Note:** `ffuf` is not in the standard apt repos. Install via the GitHub release binary:
> ```bash
> wget -q https://github.com/ffuf/ffuf/releases/latest/download/ffuf_2.1.0_linux_amd64.tar.gz -O /tmp/ffuf.tar.gz
> tar -xzf /tmp/ffuf.tar.gz -C /tmp && sudo mv /tmp/ffuf /usr/local/bin/ffuf
> ```

### 5. Allow masscan to run without a password prompt

`masscan` requires root privileges. Grant your user passwordless sudo for masscan only (replace `chris` with your username):

```bash
# Find the exact binary path
which masscan

# Create the sudoers rule (opens editor — add the line below, save and exit)
sudo visudo -f /etc/sudoers.d/metatron-masscan
```

Add this line (use the path from `which masscan` above):
```
chris ALL=(ALL) NOPASSWD: /usr/bin/masscan
```

Verify it works without a password prompt:
```bash
sudo masscan --version
```

---

## 🤖 AI Model Setup

### Step 1 — Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Step 2 — Download the base model

```bash
ollama pull huihui_ai/qwen3.5-abliterated:9b
```

> ⚠️ This model requires at least 8.4 GB of RAM. If your system has less, use the 4b variant:
> ```bash
> ollama pull huihui_ai/qwen3.5-abliterated:4b
> ```
> Then edit `Modelfile` and change the FROM line to the 4b model.

### Step 3 — Build the custom metatron-qwen model

```bash
ollama create metatron-qwen -f Modelfile
```

This creates your local `metatron-qwen` model with:
- 16,384 token context window
- Temperature: 0.7 / Top-k: 10 / Top-p: 0.9

### Step 4 — Verify the model exists

```bash
ollama list
# You should see metatron-qwen in the list
```

---

## 🗄️ Database Setup

### Step 1 — Start MariaDB

```bash
sudo systemctl start mariadb
sudo systemctl enable mariadb
```

### Step 2 — Create the database and user

```bash
mysql -u root
```

```sql
CREATE DATABASE metatron;
CREATE USER 'metatron'@'localhost' IDENTIFIED BY '123';
GRANT ALL PRIVILEGES ON metatron.* TO 'metatron'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 3 — Run the migration script

METATRON includes an idempotent migration runner that creates all required tables automatically. Run it once after setup (and again safely after any update):

```bash
python db_migrate.py
```

Expected output:
```
  [ok]   Migration 1 applied: Add engagements, scope_items, evidence tables
  [ok]   Migration 2 applied: Add post_exploitation, attack_paths, retest_sessions tables
  [ok]   Migration 3 applied: Extend history table with engagement_id and phase columns
  [ok]   Migration 4 applied: Add cloud_findings table
  [ok]   Migration 5 applied: Add segmentation_tests table

Migration complete.
```

Re-running `db_migrate.py` is safe — applied migrations show `[skip]` instead of `[ok]`.

---

## 🚀 Usage

METATRON needs **two terminal tabs** to run.

### Terminal 1 — Load the AI model

```bash
ollama run metatron-qwen
```

Wait until you see the `>>>` prompt, then leave this terminal running.

### Terminal 2 — Launch METATRON

```bash
cd ~/METATRON
source venv/bin/activate
python metatron.py
```

---

### Main Menu

```
  [1]  New Engagement  (10-phase methodology)
  [2]  Quick Scan      (legacy, no engagement)
  [3]  View History
  [4]  Engagements
  [5]  Retest
  [6]  Cloud Assessment
  [7]  Segmentation Testing  (PCI 11.4.5)
  [8]  Export Report
  [9]  Exit
```

### Quick Scan (Legacy)

Select `[2]` for a fast single-target scan — identical to the original METATRON behavior. No engagement required.

### Full Engagement Workflow

Select `[1]` to start a professional engagement:

1. **Pre-Engagement** — enter client name, test type (black/grey/white box), dates, and define in-scope/out-of-scope targets
2. **Reconnaissance** — METATRON scope-checks your target, runs selected tools, AI generates recon findings
3. **Enumeration** — web directory brute force, SMB enum, API discovery, LDAP — AI maps attack surface
4. **Vulnerability Analysis** — AI chains findings into attack paths with CVSS scores
5. **Exploitation** — AI suggests exact commands; you execute and record results
6. **Post-Exploitation** — record techniques, get AI privesc/lateral movement suggestions, optional Empire integration
7. **Reporting** — AI generates executive summary; export professional PDF
8. **Retest** — compare before/after findings, get remediation score

### Cloud Assessment

Select `[6]` or run Phase 9 within an engagement. Pre-configure credentials externally:

```bash
aws configure              # AWS
az login                   # Azure
gcloud auth login          # GCP
```

METATRON validates credentials, runs CLI assessment tools, and feeds results to the AI for finding analysis.

### Segmentation Testing (PCI DSS 11.4.5)

Select `[7]` or run Phase 10 within an engagement. The interactive wizard collects source/destination/port pairs and runs connectivity tests using the `ncat → nc → python socket` fallback chain.

Results are formatted as a PCI 11.4.5 evidence table with PASS/FAIL status, tester name, and timestamp — ready for QSA submission.

---

## 📁 Project Structure

```
METATRON/
├── metatron.py           ← main CLI entry point (9-item menu)
├── db.py                 ← MariaDB CRUD for all 13 tables
├── db_migrate.py         ← idempotent schema migration runner
├── tools.py              ← 12 recon/enum tool runners
├── llm.py                ← Ollama interface, 12 phase prompts, agentic loop
├── search.py             ← DuckDuckGo search and CVE lookup
├── engagement.py         ← pre-engagement wizard and scope management
├── enum_tools.py         ← structured enumeration (SMB, web, API, LDAP)
├── methodology.py        ← 10-phase orchestrator
├── post_exploit.py       ← post-exploitation workflow and Empire menu
├── cloud_tools.py        ← AWS / Azure / GCP CLI wrappers
├── powershell_tools.py   ← Az / Graph / AWS PowerShell + Test-NetConnection
├── segmentation_tools.py ← ncat/nc/socket segmentation testing, PCI evidence
├── empire_client.py      ← Empire REST API (SAFE_MODULES whitelist only)
├── export.py             ← PDF, HTML, professional report, retest report
├── Modelfile             ← custom model config for metatron-qwen
├── requirements.txt      ← Python dependencies
├── docs/                 ← methodology docs and segmentation playbooks
├── screenshots/          ← terminal screenshots for documentation
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🗃️ Database Schema

All tables are linked by `sl_no` (session number) from the `history` table:

```
history                   ← one row per scan session (sl_no is the spine)
    │
    ├── vulnerabilities       ← vulns found, linked by sl_no
    │       └── fixes         ← fixes per vuln, linked by vuln_id + sl_no
    ├── exploits_attempted    ← exploits tried, linked by sl_no
    ├── summary               ← full AI analysis dump, linked by sl_no
    │
    ├── engagements           ← client, dates, test type, status
    │       └── scope_items   ← in-scope / out-of-scope targets
    │
    ├── evidence              ← screenshots, command output, notes
    ├── attack_paths          ← chained attack paths with CVSS scores
    ├── post_exploitation     ← technique records with impact classification
    ├── retest_sessions       ← before/after comparison records
    ├── cloud_findings        ← AWS/Azure/GCP findings with severity
    └── segmentation_tests    ← PCI 11.4.5 connectivity test results
```

---

## 🔒 Security Notes

- **Empire integration** is restricted to read-only enumeration modules via `SAFE_MODULES` whitelist. No persistence, credential dumping, or lateral movement modules can be tasked through METATRON.
- **Cloud credentials** are never stored or managed by METATRON — configure them externally using the provider's own CLI tools.
- **Scope enforcement** — METATRON checks targets against the defined engagement scope before running any tools and warns on out-of-scope targets.

---

## ⚠️ Disclaimer

This tool is intended for **educational purposes and authorized penetration testing only**.

- Only use METATRON on systems you own or have **explicit written permission** to test.
- Unauthorized scanning or exploitation of systems is **illegal**.
- The author is not responsible for any misuse of this tool.

---

## 👤 Author

**Chris443C**
- GitHub: [@Chris443C](https://github.com/Chris443C)

Based on original work by [@sooryathejas](https://github.com/sooryathejas)

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

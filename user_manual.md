# Supply Chain Dependency Risk Scorer (SCDS) & Orchestrator
## Comprehensive User Manual & Operational Playbook

**Author:** Debayan Dutta (Registration No: 23BCE0815)  
**System:** Supply Chain Dependency Risk Scorer (SCDS)  
**Version:** 1.0.0  
**Target Manifests:** npm (`package.json`), Python/PyPI (`requirements*.txt`), Java/Maven (`pom.xml`)

---

## Table of Contents

1. [Introduction & Purpose](#1-introduction--purpose)
2. [Architecture & The SCDS Risk Model](#2-architecture--the-scds-risk-model)
   - [Multi-Vector Scoring Formula](#multi-vector-scoring-formula)
   - [Risk Classification Tiers](#risk-classification-tiers)
   - [Critical Threat Override Mechanism](#critical-threat-override-mechanism)
3. [Installation & Setup](#3-installation--setup)
   - [Prerequisites](#prerequisites)
   - [Environment Setup](#environment-setup)
   - [Verifying Installation](#verifying-installation)
4. [Command Line Interface (CLI) Guide](#4-command-line-interface-cli-guide)
   - [CLI Overview & Help](#cli-overview--help)
   - [`scds scan`: Manifest Security Auditing](#1-scds-scan-manifest-security-auditing)
   - [Exit Codes & CI/CD Gating](#exit-codes--cicd-gating)
   - [`scds check`: Pre-Installation Single Package Audit](#2-scds-check-pre-installation-single-package-audit)
   - [`scds dashboard`: Interactive Web Server](#3-scds-dashboard-interactive-web-server)
5. [Interactive Web Dashboard User Guide](#5-interactive-web-dashboard-user-guide)
   - [Launching and Navigating](#launching-and-navigating)
   - [Manifest Scanner Tab](#manifest-scanner-tab)
   - [Single Package Audit Tab](#single-package-audit-tab)
   - [Interpreting KPIs, Badges & Accordions](#interpreting-kpis-badges--accordions)
   - [Exporting Reports](#exporting-reports)
6. [Repository Orchestrator Layer](#6-repository-orchestrator-layer)
   - [Purpose of the Orchestrator](#purpose-of-the-orchestrator)
   - [Full Repository Scanning](#full-repository-scanning)
   - [Pull-Request / Incremental Scanning](#pull-request--incremental-scanning)
   - [Configuring Policy Thresholds](#configuring-policy-thresholds)
7. [CI/CD Pipeline Integration Playbooks](#7-cicd-pipeline-integration-playbooks)
   - [GitHub Actions Integration](#github-actions-integration)
   - [GitLab CI/CD Pipeline](#gitlab-cicd-pipeline)
   - [Local Pre-Commit Hook](#local-pre-commit-hook)
8. [Caching, Offline Resilience & Performance](#8-caching-offline-resilience--performance)
   - [Local SQLite Cache Architecture](#local-sqlite-cache-architecture)
   - [Cache Invalidation & Direct Lookup](#cache-invalidation--direct-lookup)
9. [Remediation Playbook](#9-remediation-playbook)
   - [Resolving Typosquatting Alerts](#resolving-typosquatting-alerts)
   - [Resolving Known CVE / GHSA Vulnerabilities](#resolving-known-cve--ghsa-vulnerabilities)
   - [Resolving Maintainer Hygiene & Pinning Flags](#resolving-maintainer-hygiene--pinning-flags)
10. [Troubleshooting & FAQs](#10-troubleshooting--faqs)

---

## 1. Introduction & Purpose

Open-source package ecosystems (npm, PyPI, Maven Central) are prime targets for software supply chain attacks. Malicious actors leverage techniques such as **typosquatting**, **brand-jacking**, **dependency confusion**, **compromised maintainer accounts**, and **unpatched known vulnerabilities (CVEs/GHSAs)** to compromise development environments, production servers, and end users.

Traditional academic and commercial scanners often suffer from:
- **Excessive Latency:** Dynamic sandboxes and multi-agent LLM inference take minutes or hours.
- **High False Positive Rates:** Heuristics without contextual calibration generate noise that developers ignore.
- **Pipeline Failure:** Rate-limiting from upstream API services can stall CI/CD builds.

The **Supply Chain Dependency Risk Scorer (SCDS)** solves these challenges by providing a **fast (< 0.5s execution)**, **deterministic**, and **explainable** supply chain threat evaluation framework. Powered by native string distance algorithms, OSV.dev vulnerability queries, registry metadata analysis, and a local SQLite caching engine, SCDS gives developers and security engineers immediate visibility and automated policy gating.

---

## 2. Architecture & The SCDS Risk Model

SCDS evaluates dependencies through a three-vector analyzer managed by [`scds.engine.RiskEngine`](file:///Users/debayan/Documents/projects/project_for_cyber/scds/engine.py#L110):

```
                        ┌─────────────────────────┐
                        │ Manifest Parsing Subsys │
                        │  (npm / PyPI / Maven)   │
                        └────────────┬────────────┘
                                     │
             ┌───────────────────────┼───────────────────────┐
             ▼                       ▼                       ▼
    ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
    │  Typosquatting   │    │  Vulnerability   │    │ Maintainer Trust │
    │     Analyzer     │    │     Analyzer     │    │     Analyzer     │
    │  (Levenshtein &  │    │  (OSV.dev + Disk │    │  (Registry Age,  │
    │   Jaro-Winkler)  │    │     Caching)     │    │ Pinning & Flags) │
    └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘
             │ (Weight: 35%)         │ (Weight: 45%)         │ (Weight: 20%)
             └───────────────────────┼───────────────────────┘
                                     ▼
                        ┌─────────────────────────┐
                        │ Deterministic Risk      │
                        │ Engine & Override Logic │
                        └────────────┬────────────┘
                                     │
                     ┌───────────────┴───────────────┐
                     ▼                               ▼
           ┌──────────────────┐            ┌──────────────────┐
           │ Developer CLI    │            │ Web Dashboard    │
           │ (Exit Code Gate) │            │ (Interactive UI) │
           └──────────────────┘            └──────────────────┘
```

### Multi-Vector Scoring Formula

The base risk score is mathematically computed via weighted linear aggregation:

$$\text{Raw Risk Score} = (0.45 \times \text{VulnScore}) + (0.35 \times \text{TypoScore}) + (0.20 \times \text{MaintainerScore})$$

- **Vulnerability Vector (45% Weight):** Evaluated by [`VulnerabilityAnalyzer`](file:///Users/debayan/Documents/projects/project_for_cyber/scds/analyzers/vulnerability.py#L31). Queries OSV.dev for known CVEs, GHSAs, and PyPA advisories, scaling according to maximum CVSS score and total vulnerability count.
- **Typosquatting Vector (35% Weight):** Evaluated by [`TyposquattingAnalyzer`](file:///Users/debayan/Documents/projects/project_for_cyber/scds/analyzers/typosquatting.py#L23). Measures Levenshtein edit distance and Jaro-Winkler similarity against curated catalogs of top-tier legitimate packages (defined in [`scds.config.POPULAR_PACKAGES`](file:///Users/debayan/Documents/projects/project_for_cyber/scds/config.py#L27)).
- **Maintainer Trust Vector (20% Weight):** Evaluated by [`MaintainerTrustAnalyzer`](file:///Users/debayan/Documents/projects/project_for_cyber/scds/analyzers/maintainer.py#L26). Inspects package release age, days since last release, presence of public source code repository links, and manifest version pinning posture.

### Risk Classification Tiers

Every evaluated dependency and overall manifest receives a standardized rating:

| Tier | Score Range | Badge Color | Interpretation | Recommended Action |
|:---|:---:|:---:|:---|:---|
| **SAFE** | `0.0 – 2.9` | Green | Verified legitimate package, no active CVEs, pinned version. | Approved for production. |
| **LOW** | `3.0 – 5.4` | Cyan | Minor findings (e.g., low-severity CVE or unpinned wildcard). | Review and pin version. |
| **MEDIUM** | `5.5 – 7.4` | Yellow | Moderate risk (e.g., moderate CVE or inactive maintainer). | Update or investigate alternatives. |
| **HIGH** | `7.5 – 8.9` | Magenta | High-severity vulnerability (CVSS 7.0–8.9) or near-match typosquat. | Immediate patching or verification. |
| **CRITICAL** | `9.0 – 10.0` | White on Red | Critical threat (CVSS 9.0+, Log4Shell, or confirmed 1-edit typosquat). | **Block build / Purge package**. |

### Critical Threat Override Mechanism

In standard linear weighting, a lethal package (e.g., brand-new typosquat `lodsh` or critical RCE `log4j-core 2.14.1`) could hypothetically be diluted down to a Medium rating if maintainer metadata looks acceptable. 

To prevent this fatal flaw, [`RiskEngine.evaluate_dependency()`](file:///Users/debayan/Documents/projects/project_for_cyber/scds/engine.py#L145-L153) applies a non-linear override:
- If $\max(\text{VulnScore}, \text{TypoScore}) \ge 9.0$: $\text{FinalScore} \ge \max(\text{RawScore}, \text{MaxVector} \times 0.95)$
- If $\max(\text{VulnScore}, \text{TypoScore}) \ge 7.5$: $\text{FinalScore} \ge \max(\text{RawScore}, \text{MaxVector} \times 0.90)$

This guarantees that an active zero-day or clear typosquat always triggers **HIGH** or **CRITICAL** gating.

---

## 3. Installation & Setup

### Prerequisites

- **Python:** Version 3.10 or higher.
- **Operating System:** Linux, macOS, or Windows (WSL/cmd/PowerShell).
- **Network Access:** (Optional during runtime due to cache) Initial access to `api.osv.dev`, `pypi.org`, and `registry.npmjs.org`.

### Environment Setup

1. **Clone or Navigate to the Workspace:**
   ```bash
   cd /Users/debayan/Documents/projects/project_for_cyber
   ```

2. **Create and Activate a Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Required Dependencies:**
   ```bash
   pip install click rich fastapi uvicorn requests pydantic
   ```

### Verifying Installation

Execute the automated test suite to ensure all parsers, algorithms, and engines are functioning deterministically:

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

Expected output:
```text
test_changed_files_filters_deleted_and_unsupported_paths ... ok
test_discovers_only_supported_source_manifests ... ok
test_policy_warns_and_blocks_at_configured_levels ... ok
test_scanner_delegates_to_the_existing_risk_engine ... ok
test_cli_check_single ... ok
test_cli_scan_sample_and_exit_code ... ok
test_cache_set_get_and_expiration ... ok
test_maven_parser ... ok
test_npm_parser ... ok
test_pypi_parser ... ok
test_ci_fail_policy ... ok
test_clean_dependency ... ok
test_typosquat_escalation ... ok
test_jaro_winkler ... ok
test_levenshtein ... ok
...
Ran 19 tests in 0.45s
OK
```

---

## 4. Command Line Interface (CLI) Guide

SCDS provides a unified CLI entry point via Python's module syntax: `python3 -m scds [COMMAND] [OPTIONS]`.

### CLI Overview & Help

To view the main help screen and available commands:

```bash
python3 -m scds --help
```

Output:
```text
Usage: python3 -m scds [OPTIONS] COMMAND [ARGS]...

  Supply Chain Dependency Risk Scorer (SCDS) CLI.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  check      Quickly checks a single package for typosquatting, vulnerabilities...
  dashboard  Launches the interactive Web Dashboard.
  scan       Scans a dependency manifest (package.json, requirements.txt, pom.xml).
```

---

### 1. `scds scan`: Manifest Security Auditing

The `scan` command parses a manifest file, queries threat feeds (with cache acceleration), computes multi-vector scores, displays an interactive Rich console table, and enforces CI/CD build gates.

#### Syntax
```bash
python3 -m scds scan [MANIFEST_PATH] [OPTIONS]
```

#### Available Options
| Option | Type | Default | Description |
|:---|:---:|:---:|:---|
| `--fail-on` | Choice (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) | *None* | Fail build and return exit code 1 if any package meets or exceeds this risk tier. |
| `--threshold` | Float (`0.0` - `10.0`) | *None* | Fail build and return exit code 1 if any package's score reaches or exceeds this number. |
| `--format` | Choice (`table`, `json`) | `table` | Console output format: human-readable Rich table or raw machine-readable JSON. |
| `--output` | File path | *None* | Write the full JSON assessment report to the specified file. |
| `--no-cache` | Flag | `False` | Bypass SQLite local cache and force direct upstream network queries. |

#### Usage Examples

**Example 1: Scan a Python Requirements File with a Policy Gate**
```bash
python3 -m scds scan samples/requirements.txt --fail-on HIGH
```
*Behavior:* Scans all dependencies in `samples/requirements.txt`. If any package is rated HIGH (7.5+) or CRITICAL (9.0+), it prints a red failure banner and exits with code `1`.

**Example 2: Scan an npm Manifest and Save JSON Report**
```bash
python3 -m scds scan samples/package.json --format json --output npm_audit.json
```
*Behavior:* Emits the complete JSON assessment to the console and simultaneously writes it to `npm_audit.json`.

**Example 3: Scan a Maven `pom.xml` with Strict Numerical Threshold**
```bash
python3 -m scds scan samples/pom.xml --threshold 8.0
```
*Behavior:* Scans Java dependencies in `pom.xml`. If any package (e.g., vulnerable `log4j-core`) scores 8.0 or higher, the build gate fails.

---

### Exit Codes & CI/CD Gating

SCDS uses standardized POSIX exit codes so pipeline runners can reliably gate pull requests:

| Exit Code | Meaning | Cause |
|:---:|:---|:---|
| **`0`** | **PASS** | Scan completed successfully; no package violated `--fail-on` or `--threshold`. |
| **`1`** | **POLICY BREACH** | One or more packages breached the specified `--fail-on` risk tier or `--threshold` score. |
| **`2`** | **EXECUTION ERROR** | Manifest file does not exist, syntax is corrupt, or an unhandled parse error occurred. |

---

### 2. `scds check`: Pre-Installation Single Package Audit

Before running `pip install <package>` or `npm install <package>`, developers can run `check` to perform instant real-time risk triage on a single dependency.

#### Syntax
```bash
python3 -m scds check [PACKAGE_NAME] [OPTIONS]
```

#### Available Options
| Option | Short | Type | Default | Description |
|:---|:---:|:---:|:---:|:---|
| `--version` | `-v` | String | *None (latest)* | Specific package version to evaluate for known CVEs. |
| `--ecosystem` | `-e` | Choice (`PyPI`, `npm`, `Maven`) | `PyPI` | Target ecosystem registry. |
| `--json` | | Flag | `False` | Print output as clean machine-readable JSON. |

#### Usage Examples

**Check a Suspicious PyPI Package (Typosquatting Check):**
```bash
python3 -m scds check reqeusts
```
*Sample Output:*
```text
╭────────────────── SCDS Single Package Audit: reqeusts ──────────────────╮
│ Package: reqeusts | Version: latest | Ecosystem: PyPI                   │
│ Score: 6.8/10 (MEDIUM)                                                  │
│                                                                         │
│ Findings:                                                               │
│ • [TYPOSQUATTING] Moderate typosquatting risk: 'reqeusts' closely       │
│   mimics popular package 'requests' (Levenshtein: 2, similarity: 97.1%) │
│                                                                         │
│ Recommendations:                                                        │
│ → Replace 'reqeusts' with verified legitimate package 'requests'.       │
╰─────────────────────────────────────────────────────────────────────────╯
```

**Check an Outdated Version for Known CVEs:**
```bash
python3 -m scds check requests --version 2.20.0
```
*Sample Output:*
```text
╭────────────────── SCDS Single Package Audit: requests ──────────────────╮
│ Package: requests | Version: 2.20.0 | Ecosystem: PyPI                   │
│ Score: 7.7/10 (HIGH)                                                    │
│                                                                         │
│ Findings:                                                               │
│ • [VULNERABILITY] Found 8 known vulnerabilities (CVE-2024-47081,       │
│   CVE-2024-35195). Peak CVSS: 7.5.                                     │
│                                                                         │
│ Recommendations:                                                        │
│ → Upgrade dependency to a patched non-vulnerable release.               │
╰─────────────────────────────────────────────────────────────────────────╯
```

**Check an npm Package as JSON:**
```bash
python3 -m scds check lodsh --ecosystem npm --json
```

---

### 3. `scds dashboard`: Interactive Web Server

Starts the FastAPI-based web application and serves the dark-mode cyber risk dashboard:

```bash
python3 -m scds dashboard --host 127.0.0.1 --port 8000
```

#### Options:
- `--host`: Host IP address to bind to (default: `127.0.0.1`).
- `--port`: Port number to listen on (default: `8000`).

Once launched, open your web browser at: **`http://127.0.0.1:8000`**

---

## 5. Interactive Web Dashboard User Guide

The SCDS Web Dashboard provides a visual interface for development teams, security auditors, and release managers.

```
+-------------------------------------------------------------------------+
| SCDS                                              [Manifest]  [Package] |
+-------------------------------------------------------------------------+
| Target: package.json   [Upload]   [NPM Sample] [PyPI Sample] [Maven]    |
| +---------------------------------------------------------------------+ |
| | { "dependencies": { "express": "^4.19.2", "lodsh": "0.0.1" } }     | |
| +---------------------------------------------------------------------+ |
| Fail on: [HIGH (7.5+) v]   Threshold: [    ]          [  Scan Manifest ]|
+-------------------------------------------------------------------------+
| [FAILED CI/CD GATE: Found CRITICAL risk package 'lodsh']  [Export JSON] |
| Scanned: 6 | Critical: 1 | High: 1 | Typosquats: 1 | Avg Score: 5.6     |
+-------------------------------------------------------------------------+
| [All (6)] [Critical (1)] [High (1)] [Medium (1)] [Low (0)] [Safe (3)]   |
| Search: [ lodsh                                                      ]  |
| > lodsh     0.0.1    npm    9.5   CRITICAL   [TYPOSQUATTING] Edit dist 1|
+-------------------------------------------------------------------------+
```

### Launching and Navigating

1. Start the server:
   ```bash
   python3 -m scds dashboard --port 8765
   ```
2. Navigate to `http://localhost:8765` in any modern web browser.
3. Use the top navigation bar to toggle between:
   - **Manifest Tab:** Full manifest inspection, policy threshold tuning, and multi-vector breakdowns.
   - **Package Tab:** Single package quick audit prior to installation.

---

### Manifest Scanner Tab

#### 1. Inputting Dependencies
- **One-Click Presets:** Click **NPM Sample**, **PyPI Sample**, or **Maven Sample** to immediately load built-in real-world attack scenarios (including typosquatting `lodsh`, `coloramaa`, and Log4Shell `log4j-core 2.14.1`).
- **File Upload:** Click **Upload** to select an existing `package.json`, `requirements.txt`, or `pom.xml` directly from your file system.
- **Direct Paste / Edit:** Paste manifest text directly into the code editor textarea. You can edit version numbers or add dependencies on the fly.

#### 2. Setting Policy Controls
- **Fail on:** Dropdown selector to choose your gating tier:
  - `None`: Information only; does not fail the gate.
  - `CRITICAL`: Fails on score $\ge 9.0$.
  - `HIGH`: Fails on score $\ge 7.5$ (Recommended for production).
  - `MEDIUM`: Fails on score $\ge 5.5$ (Strict security profile).
- **Threshold:** (Optional) Set a precise numerical boundary between `0.0` and `10.0`.

#### 3. Executing the Scan
- Click the **Scan** button. Scan completion typically takes **under 0.5 seconds**.

---

### Interpreting KPIs, Badges & Accordions

When a scan finishes, the results dashboard activates:

1. **CI/CD Gate Banner:**
   - **Green Banner (`✓ PASSED`):** All packages comply with the configured risk policy.
   - **Red Banner (`✗ FAILED`):** Indicates the specific dependency that breached policy (e.g., `Found CRITICAL risk package 'lodsh'`).
2. **KPI Summary Cards:**
   - **Scanned:** Total count of unique dependencies identified.
   - **Critical / High:** Count of high-risk components requiring attention.
   - **Typosquats:** Number of detected brand-jacking or typosquatting attempts.
   - **Avg Score:** Overall supply chain hygiene posture.
3. **Filter & Search Controls:**
   - Filter chips allow instant sorting by risk level (`All`, `Critical`, `High`, `Medium`, `Low`, `Safe`).
   - The search box provides real-time client-side substring filtering across package names and findings.
4. **Interactive Accordion Table:**
   - Click anywhere on a dependency row to expand the **Accordion Inspector**:
     - **Vector Score Bars:** Visual breakdown of Vulnerability Score (45%), Typosquatting Score (35%), and Maintainer Score (20%).
     - **Vulnerability Section:** List of matching CVEs, GHSAs, CVSS severity ratings, and vulnerability summaries.
     - **Typosquatting Section:** Identifies the legitimate target package, Levenshtein edit distance, and Jaro-Winkler similarity percentage.
     - **Maintainer Hygiene Section:** Registry age, days since last release, and version pinning flags.
     - **Actionable Recommendations:** Direct instructions (e.g., `"Replace 'lodsh' with verified legitimate package 'lodash'"`).

---

### Single Package Audit Tab

Click the **Package** tab in the top header to evaluate a package before adding it to a project:

1. **Enter Package Name:** e.g., `reqeusts` or `express`.
2. **Enter Version (Optional):** e.g., `2.20.0` (leave blank to evaluate latest metadata).
3. **Select Ecosystem:** Choose `PyPI`, `npm`, or `Maven`.
4. **Click Audit:** An instant card displays the risk badge, score breakdown, specific findings, and remediation instructions.

---

### Exporting Reports

Click the **Export JSON** button in the gate banner to download the complete, structured audit report as a standard `.json` file. This file can be archived as a compliance artifact or passed to downstream security reporting pipelines.

---

## 6. Repository Orchestrator Layer

The [`orchestrator/`](file:///Users/debayan/Documents/projects/project_for_cyber/orchestrator) module is an automation wrapper built around the SCDS engine. It automatically discovers all supported manifests across a project tree, delegates evaluation to SCDS, and returns aggregated PASS/WARN/BLOCK decisions.

### Purpose of the Orchestrator

While `scds scan` targets a single manifest file, `orchestrator` operates at the **repository level**:
- Recursively discovers `package.json`, `requirements*.txt`, and `pom.xml`.
- Automatically ignores vendor and runtime directories: `.git`, `node_modules`, `venv`, `.venv`, and `vendor`.
- Separates policy into **Warn** and **Block** levels for progressive security rollout.

---

### Full Repository Scanning

Scan an entire repository tree from root:

```bash
python3 -m orchestrator . --warn-on MEDIUM --block-on HIGH
```

#### CLI Options:
| Flag | Default | Description |
|:---|:---:|:---|
| `[REPOSITORY_PATH]` | `.` | Root directory of the repository to discover manifests. |
| `--warn-on` | `MEDIUM` | Lowest risk level that triggers a `WARN` decision. |
| `--block-on` | `CRITICAL` | Lowest risk level that triggers a `BLOCK` decision (exits with code 1). |
| `--no-cache` | `False` | Query upstream services directly instead of using the SCDS disk cache. |
| `--changed` | *None* | Path to a changed manifest (can be repeated for multiple files). |

#### Sample JSON Output:
```json
{
  "scanned_manifests": [
    "samples/package.json",
    "samples/requirements.txt",
    "samples/pom.xml"
  ],
  "decision": {
    "status": "BLOCK",
    "highest_level": "CRITICAL",
    "message": "Blocked: highest dependency risk is CRITICAL."
  },
  "manifest_results": [ ... ]
}
```

---

### Pull-Request / Incremental Scanning

In CI/CD pull-request builds, scanning the entire repository can be wasteful. The `--changed` parameter restricts evaluation strictly to files modified in the pull request:

```bash
python3 -m orchestrator . \
  --changed requirements.txt \
  --changed frontend/package.json \
  --warn-on MEDIUM \
  --block-on HIGH
```

If a modified file is not a supported manifest (e.g. `README.md` or `app.py`), the orchestrator safely skips it without error.

---

### Configuring Policy Thresholds

The orchestrator supports progressive adoption:
- **Phase 1 (Monitoring Mode):** Run with `--warn-on LOW --block-on CRITICAL` to observe supply chain posture without failing builds on moderate findings.
- **Phase 2 (Strict Policy Gate):** Run with `--warn-on MEDIUM --block-on HIGH` to ensure no high-risk typosquats or exploitable CVEs enter production.

---

## 7. CI/CD Pipeline Integration Playbooks

### GitHub Actions Integration

Create `.github/workflows/scds-gate.yml` in your repository:

```yaml
name: "Supply Chain Security Gate (SCDS)"

on:
  push:
    branches: [ "main", "master" ]
  pull_request:
    branches: [ "main", "master" ]

jobs:
  scds-audit:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4
        with:
          fetch-depth: 2  # To inspect changed files if needed

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install SCDS Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install click rich fastapi uvicorn requests pydantic

      - name: Run Repository Orchestrator Policy Gate
        run: |
          python3 -m orchestrator . --warn-on MEDIUM --block-on HIGH
```

---

### GitLab CI/CD Pipeline

Add the following job to your `.gitlab-ci.yml`:

```yaml
stages:
  - security

scds_dependency_scan:
  stage: security
  image: python:3.11-slim
  before_script:
    - pip install click rich fastapi uvicorn requests pydantic
  script:
    - python3 -m orchestrator . --warn-on MEDIUM --block-on HIGH
  artifacts:
    when: always
    reports:
      junit: scds-report.xml
    paths:
      - "*.json"
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'
```

---

### Local Pre-Commit Hook

Prevent vulnerable dependencies or typosquats from ever being committed:

1. Add a custom hook in `.git/hooks/pre-commit`:
   ```bash
   #!/usr/bin/env bash
   echo "[SCDS] Checking staged manifests for supply chain threats..."
   
   # Identify staged dependency manifests
   STAGED_MANIFESTS=$(git diff --cached --name-only | grep -E '(package\.json|requirements.*\.txt|pom\.xml)' || true)
   
   if [ -z "$STAGED_MANIFESTS" ]; then
       exit 0
   fi
   
   CMD="python3 -m orchestrator ."
   for file in $STAGED_MANIFESTS; do
       CMD="$CMD --changed $file"
   done
   CMD="$CMD --block-on HIGH"
   
   eval $CMD
   STATUS=$?
   
   if [ $STATUS -ne 0 ]; then
       echo "❌ [SCDS] Pre-commit blocked: Supply chain policy gate breached!"
       exit 1
   fi
   
   echo "✓ [SCDS] Manifest check passed."
   exit 0
   ```
2. Make the script executable:
   ```bash
   chmod +x .git/hooks/pre-commit
   ```

---

## 8. Caching, Offline Resilience & Performance

SCDS is engineered specifically to eliminate CI/CD pipeline bottlenecks caused by external network flakiness or registry API rate-limiting.

### Local SQLite Cache Architecture

- **Engine:** Implemented in [`scds.cache.CacheManager`](file:///Users/debayan/Documents/projects/project_for_cyber/scds/cache.py#L16).
- **Default Storage Location:** `~/.cache/scds/scds_cache.db`
- **Concurrency Mode:** Write-Ahead Logging (`PRAGMA journal_mode=WAL;`) enabled for high-speed concurrent access across parallel scans.
- **Default TTL:** **86,400 seconds (24 Hours)** as defined in [`DEFAULT_CACHE_TTL`](file:///Users/debayan/Documents/projects/project_for_cyber/scds/config.py#L24).
- **Cached Data:**
  - OSV.dev batch vulnerability queries.
  - PyPI JSON metadata (release timestamps, project URLs).
  - npm registry package metadata.

### Offline Resilience

If your build runner has restricted internet access or upstream registries experience temporary downtime:
- **Cached Queries:** Return instantaneously from local disk.
- **Cache Misses under Network Failure:** SCDS gracefully falls back to static heuristic models and logs an explanatory finding:
  ```text
  [MAINTAINER] REGISTRY_LOOKUP_OFFLINE: Package metadata verified using static heuristics.
  ```
  This ensures that CI/CD pipelines never crash due to network drops.

### Cache Invalidation & Direct Lookup

To force SCDS to refresh all upstream vulnerability definitions and registry records, supply the `--no-cache` flag:

```bash
# Force fresh lookup in single scan
python3 -m scds scan samples/requirements.txt --no-cache

# Force fresh lookup in orchestrator
python3 -m orchestrator . --no-cache
```

Alternatively, to completely wipe the local cache:
```bash
rm -rf ~/.cache/scds/scds_cache.db*
```

---

## 9. Remediation Playbook

When SCDS reports a `HIGH` or `CRITICAL` finding, follow this step-by-step remediation guide:

### Resolving Typosquatting Alerts

- **Alert Example:**
  ```text
  [TYPOSQUATTING] HIGH-CONFIDENCE TYPOSQUATTING: 'lodsh' differs by only 1 character edit from popular package 'lodash' (similarity: 98.2%).
  ```
- **Root Cause:** A developer made a typographical error in the manifest, or a malicious actor pushed a typosquatted package to the registry.
- **Remediation Steps:**
  1. Inspect the expanded accordion in the Dashboard or the CLI recommendation.
  2. Confirm the legitimate package target (e.g. `lodash` instead of `lodsh`, `requests` instead of `reqeusts`, `react-dom` instead of `react_dom`).
  3. Edit your manifest file and replace the misspelled name with the verified package.
  4. Re-run `python3 -m scds scan <manifest>`.

---

### Resolving Known CVE / GHSA Vulnerabilities

- **Alert Example:**
  ```text
  [VULNERABILITY] Found 8 known vulnerabilities (CVE-2024-47081, CVE-2024-35195). Peak CVSS: 7.5.
  ```
- **Root Cause:** The manifest pins an obsolete package version containing published vulnerabilities.
- **Remediation Steps:**
  1. Identify the matching CVE IDs in the SCDS report.
  2. Check the vulnerability advisory on OSV.dev (`https://osv.dev/vulnerability/<CVE-ID>`) or GitHub Advisory Database.
  3. Determine the minimum fixed version.
  4. Update the manifest version pin (e.g., bump `requests==2.20.0` to `requests==2.32.0`).
  5. Re-run the scan to verify that `VULNERABILITY` risk returns to `0.0` or `SAFE`.

---

### Resolving Maintainer Hygiene & Pinning Flags

- **Alert Example:**
  ```text
  [MAINTAINER] UNPINNED_VERSION: Manifest specifies wildcard or unpinned version.
  [MAINTAINER] BRAND_NEW_PACKAGE: Published only 4 days ago (high supply chain vector).
  ```
- **Root Cause:**
  - Wildcard or floating version specifications (`*`, `latest`, or omitted version numbers) allow attackers to introduce malicious minor/patch releases automatically.
  - Brand-new packages have not undergone community scrutiny.
- **Remediation Steps:**
  1. Pin exact versions in your manifest (e.g., use `==` in `requirements.txt`, exact SemVer in `package.json`, or a strict release tag in `pom.xml`).
  2. For brand-new packages, verify the publisher identity and inspect repository commit activity before deploying to production.

---

## 10. Troubleshooting & FAQs

### Frequently Asked Questions

**Q1: How does SCDS differ from `pip audit` or `npm audit`?**  
*Answer:* `pip audit` and `npm audit` only check for known CVEs after packages are installed. SCDS evaluates the entire pre-installation supply chain vector: it detects **typosquatting** (which has no CVE), **unmaintained abandonware**, **brand-new package registration**, and **unpinned versions**, and works uniformly across npm, PyPI, and Maven.

**Q2: Can SCDS scan private internal packages without reporting false typosquats?**  
*Answer:* Yes. SCDS compares package names against public baseline catalogs of high-reputation packages (`POPULAR_PACKAGES`). If your internal package has a unique naming prefix (e.g., `@mycompany/auth-service`), it will not conflict with the baseline catalog.

**Q3: How do I customize the risk score threshold for my organization?**  
*Answer:* Use the `--threshold` flag in the CLI (e.g., `--threshold 6.5`) or adjust `--fail-on` / `--block-on` between `LOW`, `MEDIUM`, `HIGH`, and `CRITICAL`.

---

### Common Error Messages & Solutions

| Error Message | Probable Cause | Solution |
|:---|:---|:---|
| `Error parsing manifest: [Errno 2] No such file or directory` | The provided manifest path does not exist. | Verify the relative or absolute path passed to `scds scan`. |
| `Unsupported manifest format` | File extension or structure is not recognized. | Ensure file is named `package.json`, `requirements*.txt`, or `pom.xml`. |
| `Address already in use` when launching dashboard | Another process is occupying port 8000. | Specify a different port using `--port` (e.g., `python3 -m scds dashboard --port 8765`). |
| `Blocked: highest dependency risk is CRITICAL` | Build broke due to policy gate failure. | Inspect the JSON or terminal table to locate the critical dependency and apply the remediation steps. |

---

## 11. Module & Source Code Reference

For developers extending SCDS, refer to the following codebase modules:

- **CLI Interface:** [`scds/cli.py`](file:///Users/debayan/Documents/projects/project_for_cyber/scds/cli.py)
- **Central Risk Engine:** [`scds/engine.py`](file:///Users/debayan/Documents/projects/project_for_cyber/scds/engine.py)
- **Configuration & Baselines:** [`scds/config.py`](file:///Users/debayan/Documents/projects/project_for_cyber/scds/config.py)
- **Distance Algorithms:** [`scds/algorithms/distance.py`](file:///Users/debayan/Documents/projects/project_for_cyber/scds/algorithms/distance.py)
- **Typosquatting Analyzer:** [`scds/analyzers/typosquatting.py`](file:///Users/debayan/Documents/projects/project_for_cyber/scds/analyzers/typosquatting.py)
- **Vulnerability Analyzer:** [`scds/analyzers/vulnerability.py`](file:///Users/debayan/Documents/projects/project_for_cyber/scds/analyzers/vulnerability.py)
- **Maintainer Trust Analyzer:** [`scds/analyzers/maintainer.py`](file:///Users/debayan/Documents/projects/project_for_cyber/scds/analyzers/maintainer.py)
- **Manifest Parsers:** [`scds/parsers/`](file:///Users/debayan/Documents/projects/project_for_cyber/scds/parsers)
- **Disk Cache Layer:** [`scds/cache.py`](file:///Users/debayan/Documents/projects/project_for_cyber/scds/cache.py)
- **Web Dashboard & API:** [`scds/web/app.py`](file:///Users/debayan/Documents/projects/project_for_cyber/scds/web/app.py)
- **Repository Orchestrator:** [`orchestrator/service.py`](file:///Users/debayan/Documents/projects/project_for_cyber/orchestrator/service.py)

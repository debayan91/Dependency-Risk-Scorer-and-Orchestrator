# Supply Chain Dependency Risk Scorer (SCDS)

**Author:** Debayan Dutta (Registration No: 23BCE0815)  
**Project:** Comprehensive Dependency Risk Project Review & Literature Survey Implementation  
**Version:** 1.0.0 (Functional Prototype)

---

## 1. Overview & Problem Understanding

Modern software development relies on open-source package registries (NPM, PyPI, Maven), exposing pipelines to supply chain threats such as **typosquatting**, **dependency confusion**, **known CVEs/GHSAs**, and **maintainer account compromise**.

Academic tools typically rely on heavy dynamic sandboxing (DONAPI, OSCAR) or opaque LLMs (IntelGuard), introducing extreme latency and rate-limiting failures in CI/CD. The **Supply Chain Dependency Risk Scorer (SCDS)** provides a **fast, deterministic, and explainable** alternative combining multi-vector analysis with a rate-limit-resistant local cache.

---

## 2. Architecture & Modules

```
                    ┌─────────────────────────┐
                    │ Manifest Parsing Module │
                    │ (NPM / PyPI / Maven)    │
                    └────────────┬────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Typosquatting   │    │  Vulnerability   │    │ Maintainer Trust │
│     Analyzer     │    │     Analyzer     │    │     Analyzer     │
│  (Levenshtein /  │    │  (OSV.dev Batch  │    │  (Registry Age / │
│   Jaro-Winkler)  │    │  + Local Cache)  │    │ Hygiene Signals) │
└────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘
         │ (Weight: 35%)         │ (Weight: 45%)         │ (Weight: 20%)
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │ Deterministic Risk      │
                    │ Engine & Scoring Matrix │
                    └────────────┬────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
       ┌──────────────────┐            ┌──────────────────┐
       │  Developer CLI   │            │  Web Dashboard   │
       │ (CI/CD Exit Code)│            │ (Real-time UI)   │
       └──────────────────┘            └──────────────────┘
```

### Risk Calculation Formula
$$\text{Total Risk Score} = (0.45 \times \text{VulnScore}) + (0.35 \times \text{TypoScore}) + (0.20 \times \text{MaintainerScore})$$

- **SAFE:** `0.0 – 2.9`
- **LOW:** `3.0 – 5.4`
- **MEDIUM:** `5.5 – 7.4`
- **HIGH:** `7.5 – 8.9`
- **CRITICAL:** `9.0 – 10.0`
- *Critical Threat Override:* High-confidence typosquats or critical CVEs (CVSS 9.0+) automatically escalate to prevent dilution by benign maintainer metadata.

---

## 3. Quickstart Guide

### Prerequisites
Python 3.10+ (Standard library + `rich`, `fastapi`, `uvicorn`, `click`, `requests`).

---

### Command Line Interface (CLI)

#### 1. Scan a Manifest (with CI/CD Policy Gate)
```bash
# Scan npm package.json and fail build on HIGH or CRITICAL risk
python3 -m scds scan samples/package.json --fail-on HIGH

# Scan PyPI requirements.txt
python3 -m scds scan samples/requirements.txt --fail-on HIGH

# Scan Maven pom.xml
python3 -m scds scan samples/pom.xml --fail-on CRITICAL
```

*Exit Codes for CI/CD Gates:*
- `0`: Scan passed policy gate.
- `1`: Risk threshold breached (breaks pipeline build).
- `2`: Manifest parsing / file error.

#### 2. Quick Audit a Single Package
```bash
# Check PyPI package for typosquatting / CVEs
python3 -m scds check reqeusts

# Check npm package
python3 -m scds check lodsh --ecosystem npm

# Check known vulnerable package
python3 -m scds check requests --version 2.20.0
```

#### 3. Output Machine-Readable JSON
```bash
python3 -m scds scan samples/requirements.txt --format json --output report.json
```

---

### Interactive Web Dashboard

Launch the local web dashboard:
```bash
python3 -m scds dashboard --port 8765
```

Open your browser at:
```
http://127.0.0.1:8765
```

**Dashboard Features:**
- **Pre-loaded Test Scenarios:** Instant 1-click testing for NPM (compromised), PyPI (vulnerable), and Maven (Log4Shell).
- **Interactive Drag & Drop:** Upload any `package.json`, `requirements.txt`, or `pom.xml`.
- **Multi-Vector Score Attribution:** Visual breakdown of Vulnerability, Typosquatting, and Maintainer components.
- **Accordion Inspector:** Expand any dependency to see CVE IDs, Levenshtein distance, Jaro-Winkler %, and remediation advice.
- **Single Package Auditor:** Inspect any package prior to installation.
- **Export:** 1-click JSON report generation.

---

## 4. Running Automated Tests

Run the full unit and integration test suite:
```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

All 15 tests execute deterministically in **< 0.5 seconds**.

---

## 5. Repository Structure

```
project_for_cyber/
├── scds/
│   ├── __init__.py
│   ├── __main__.py               # CLI entrypoint (`python -m scds ...`)
│   ├── config.py                 # Risk weights, thresholds, popular baselines
│   ├── cache.py                  # Rate-limit-resistant SQLite disk cache
│   ├── parsers/
│   │   ├── __init__.py           # Unified Dependency model & ecosystem detector
│   │   ├── npm.py                # package.json parser
│   │   ├── pypi.py               # requirements.txt parser
│   │   └── maven.py              # pom.xml parser
│   ├── algorithms/
│   │   ├── __init__.py
│   │   └── distance.py           # Native Levenshtein & Jaro-Winkler implementations
│   ├── analyzers/
│   │   ├── __init__.py
│   │   ├── typosquatting.py      # TypoSmart-style typosquatting & confusion detector
│   │   ├── vulnerability.py      # Google OSV.dev REST API client + caching
│   │   └── maintainer.py         # Registry metadata, age, and version hygiene analyzer
│   ├── engine.py                 # Weighted, deterministic, explainable risk calculation
│   ├── cli.py                    # Rich terminal UI, color-coded badges, CI/CD exit codes
│   └── web/
│       ├── __init__.py
│       ├── app.py                # FastAPI dashboard server & scan REST API
│       └── static/
│           ├── index.html        # Modern responsive dark-mode cyber dashboard
│           ├── app.css           # Glassmorphism, cyber risk badges, responsive layout
│           └── app.js            # Live scanning, sample presets, interactive charts & tables
├── samples/
│   ├── package.json              # Sample npm manifest with typosquat & CVE test cases
│   ├── requirements.txt          # Sample PyPI manifest with typosquat & CVE test cases
│   └── pom.xml                   # Sample Maven manifest
├── tests/
│   ├── __init__.py
│   └── test_scds.py              # Automated unit and integration tests
└── README.md
```

## 6. Repository Automation Layer

The separate [`orchestrator/`](orchestrator/README.md) module provides the
product-facing automation layer without changing the SCDS scanner. It discovers
supported manifests in a repository, delegates analysis to `scds`, and returns
PASS/WARN/BLOCK policy decisions for CI, scheduled scans, or future Git-provider
webhooks.

```bash
python3 -m orchestrator . --warn-on MEDIUM --block-on HIGH
```
# Dependency-Risk-Scorer-and-Orchestrator

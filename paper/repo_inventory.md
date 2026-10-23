# Repository Inventory: Supply Chain Dependency Risk Scorer (SCDS)

**Project Name:** Supply Chain Dependency Risk Scorer (SCDS) & Orchestrator Automation Layer  
**Repository Root:** `/Users/debayan/Documents/projects/project_for_cyber`  
**Primary Author:** Debayan Dutta (Registration No: 23BCE0815)  
**Evaluated Date:** October 2026  
**Language & Runtime:** Python 3.10+ (Standard Library, `click`, `rich`, `fastapi`, `requests`, `uvicorn`)

---

## 1. High-Level System Architecture and Modules

The repository contains a fully implemented software supply chain risk assessment framework designed for local developer terminals, automated CI/CD security gates, and interactive enterprise auditing. It comprises two principal packages:

1. `scds`: Core dependency risk engine, distance algorithms, multi-ecosystem manifest parsers, SQLite disk caching layer, CLI, and FastAPI web dashboard.
2. `orchestrator`: Repository-level discovery and policy automation layer that identifies manifests across project trees and enforces configurable `PASS`/`WARN`/`BLOCK` decisions without mutating `scds`.

```
project_for_cyber/
├── scds/
│   ├── config.py                 # Configuration, risk thresholds, weights, catalogs
│   ├── cache.py                  # Disk-backed SQLite cache with WAL journal mode
│   ├── algorithms/
│   │   └── distance.py           # Native Levenshtein and Jaro-Winkler implementations
│   ├── parsers/
│   │   ├── __init__.py           # Dependency dataclass & ecosystem detection
│   │   ├── npm.py                # package.json parser
│   │   ├── pypi.py               # requirements.txt parser
│   │   └── maven.py              # pom.xml parser
│   ├── analyzers/
│   │   ├── typosquatting.py      # String distance & normalization confusion analyzer
│   │   ├── vulnerability.py      # Google OSV.dev REST client & compound CVSS scoring
│   │   └── maintainer.py         # PyPI/npm registry metadata & hygiene analyzer
│   ├── engine.py                 # Deterministic weighted risk engine & override shield
│   ├── cli.py                    # Click CLI with rich terminal tables and exit gates
│   └── web/                      # FastAPI web server and responsive dashboard
├── orchestrator/
│   ├── discovery.py              # Recursive manifest scanner with exclusion filters
│   ├── policy.py                 # Policy rule evaluation (PASS / WARN / BLOCK)
│   ├── service.py                # RepositoryScanner coordinator
│   └── cli.py                    # CI/CD repository audit CLI
├── tests/
│   ├── test_scds.py              # 15 unit and integration tests
│   └── test_orchestrator.py      # 4 unit tests
└── samples/                      # Multi-ecosystem test manifests (PyPI, npm, Maven)
```

---

## 2. Detailed Component Inventory

### 2.1 Configuration and Baseline Catalogs (`scds/config.py`)
- **Symbol Constants:**
  - `WEIGHT_VULNERABILITY = 0.45`
  - `WEIGHT_TYPOSQUATTING = 0.35`
  - `WEIGHT_MAINTAINER = 0.20`
  - Severity Thresholds: `SAFE <= 2.9`, `LOW <= 5.4`, `MEDIUM <= 7.4`, `HIGH <= 8.9`, `CRITICAL 9.0–10.0`
  - `DEFAULT_CACHE_TTL = 86400` seconds (24 hours)
  - `OSV_BATCH_URL`, `OSV_QUERY_URL`: Official Google OSV.dev REST endpoints
- **Curated Baselines:**
  - `POPULAR_PACKAGES`: Pre-compiled sets of high-reputation packages across PyPI (55 packages), npm (50 packages), and Maven (12 packages).

### 2.2 Native Distance Algorithms (`scds/algorithms/distance.py`)
- **`levenshtein_distance(s1: str, s2: str) -> int`**:
  - Computes minimum single-character edit operations (insertions, deletions, substitutions).
  - Implements two alternating rows to maintain $O(\min(m, n))$ space complexity instead of full $(m+1) \times (n+1)$ matrix allocation.
- **`jaro_similarity(s1: str, s2: str) -> float`**:
  - Computes character matches within matching distance window $\lfloor \max(|s_1|, |s_2|) / 2 \rfloor - 1$ and calculates half-transpositions.
- **`jaro_winkler_similarity(s1: str, s2: str, prefix_weight=0.1, max_prefix_len=4) -> float`**:
  - Adds prefix scaling bonus when Jaro similarity exceeds $0.70$.

### 2.3 Resilient Caching Subsystem (`scds/cache.py`)
- **`CacheManager`**:
  - Disk-backed SQLite database located at `~/.cache/scds/scds_cache.db`.
  - Enables SQLite Write-Ahead Logging (`PRAGMA journal_mode=WAL;`) for concurrent read access during parallel CI runs.
  - Schema: `(namespace TEXT, cache_key TEXT, data TEXT, expires_at REAL, PRIMARY KEY (namespace, cache_key))`.
  - Lazy eviction on expired records during `get()`.

### 2.4 Multi-Ecosystem Parsers (`scds/parsers/`)
- **`Dependency` Dataclass:** `(name: str, version: Optional[str], ecosystem: str, is_dev: bool)`.
- **`detect_ecosystem(file_path: str) -> str`**: Detects `"npm"`, `"Maven"`, or `"PyPI"`.
- **`npm.py: parse_package_json`**: Extracts direct, development, and peer dependencies; strips semver prefixes (`^`, `~`, `>=`, `<=`, `v`).
- **`pypi.py: parse_requirements_txt`**: Strips comments, parses version constraints (`==`, `>=`, `<=`, `~=`), ignores pip flags (`-r`, `-i`, `--extra-index-url`).
- **`maven.py: parse_pom_xml`**: Parses XML document tree using standard `xml.etree.ElementTree`, extracts `<groupId>:<artifactId>` and `<version>`.

### 2.5 Multi-Vector Threat Analyzers (`scds/analyzers/`)
- **`TyposquattingAnalyzer` (`scds/analyzers/typosquatting.py`):**
  - Evaluates requested dependency names against curated popular packages in `POPULAR_PACKAGES`.
  - Exact match: Risk score $0.0$.
  - Normalization confusion check: Hyphen versus underscore variance (`react_dom` vs `react-dom`) triggers high-confidence flag (score $9.5$).
  - Distance evaluation: Levenshtein distance 1 and Jaro-Winkler $\ge 0.88$ assigns $9.5$; Levenshtein 2 and JW $\ge 0.85$ assigns $7.5$; JW $\ge 0.90$ assigns $6.0$.
- **`VulnerabilityAnalyzer` (`scds/analyzers/vulnerability.py`):**
  - Dispatches queries to OSV.dev REST API.
  - Extracts CVSS 3.x vectors, numeric scores, and ecosystem severity tiers.
  - Implements compound scoring: $S_{compound} = \min(10.0, \max(\text{CVSS}) + \min(1.0, 0.2 \times (n - 1)))$.
  - Caches results under `osv` namespace in SQLite cache.
- **`MaintainerTrustAnalyzer` (`scds/analyzers/maintainer.py`):**
  - Version pinning check: Unpinned versions add $+2.0$ penalty.
  - Queries PyPI JSON API / npm registry API.
  - Flags: `BRAND_NEW_PACKAGE` ($<14$ days: $+5.0$, $<45$ days: $+2.5$), `ABANDONED_MAINTAINER` ($>1100$ days: $+3.5$, $>730$ days: $+1.5$), `MISSING_SOURCE_REPO` ($+2.0$).

### 2.6 Deterministic Risk Engine (`scds/engine.py`)
- **`RiskEngine`**:
  - Calculates raw weighted score:
    $$S_{raw} = (0.45 \times S_{vuln}) + (0.35 \times S_{typo}) + (0.20 \times S_{maint})$$
  - **Critical Threat Override Shield:**
    - If $\max(S_{vuln}, S_{typo}) \ge 9.0$: $S_{final} \ge \max(S_{raw}, \max \times 0.95)$
    - If $\max(S_{vuln}, S_{typo}) \ge 7.5$: $S_{final} \ge \max(S_{raw}, \max \times 0.90)$
  - Maps to categorical levels: `SAFE` ($[0.0, 2.9]$), `LOW` ($[3.0, 5.4]$), `MEDIUM` ($[5.5, 7.4]$), `HIGH` ($[7.5, 8.9]$), `CRITICAL` ($[9.0, 10.0]$).
  - Emits human-readable findings and remediation recommendations.

### 2.7 Orchestrator Automation Layer (`orchestrator/`)
- Recursively traverses repository paths while pruning non-source directories (`.git`, `node_modules`, `venv`, `target`, `dist`).
- Maps discovered manifests to `scds` parser and evaluation engine.
- Implements `Policy` evaluations: `PASS`, `WARN`, `BLOCK` based on user-specified threshold boundaries.

---

## 3. Test Suites and Existing Results

- **Automated Test Suite:**
  - `tests/test_scds.py`: 15 tests.
  - `tests/test_orchestrator.py`: 4 tests.
  - **Execution Outcome:** 19/19 passing tests in $0.91$ seconds.
- **Sample Datasets:**
  - `samples/package.json`: 7 npm dependencies (includes `lodsh` typosquat, `react_dom` confusion, `lodash` 4.17.15 CVEs, `axios` 1.6.8 CVEs).
  - `samples/requirements.txt`: 7 PyPI dependencies (includes `requests` 2.20.0 CVEs, `reqeusts` transposition typosquat, `coloramaa` typosquat, `urllib3` 1.24.2 CVEs, unpinned `pydantic`).
  - `samples/pom.xml`: 3 Maven dependencies (includes `log4j-core` 2.14.1 Log4Shell CVSS 9.8).
  - `novice_test_suite.txt`: Curated benchmark file spanning all 5 risk tiers for controlled pedagogical verification.

---

## 4. Unresolved Questions & Paper Positioning Gaps

1. **Absence of Empirical False-Positive Ground Truth at Registry Scale:** While unit tests demonstrate 100% precision on curated samples, the system has not been benchmarked across a random sample of $100{,}000+$ live registry packages.
2. **Dynamic / Transitive Resolution Limit:** The parsers currently inspect direct declared dependencies in root manifests; transitive resolution requires local lockfile parsing or deep dependency graph explosion.
3. **Registry Rate-Limit Mitigation vs. Staleness Tradeoff:** SQLite caching guarantees sub-second execution, but a 24-hour TTL implies zero-day advisories published within that window may remain uncached until cache expiry.

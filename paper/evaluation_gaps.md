# Evaluation Gaps and Proposed Empirical Validation Plan

## 1. Current Empirical Coverage vs. Experimental Boundaries

The current repository provides concrete, reproducible validation for:
- Deterministic string distance algorithm correctness (Levenshtein edit distance, Jaro and Jaro-Winkler similarity).
- Multi-ecosystem manifest parsing accuracy across npm (`package.json`), PyPI (`requirements.txt`), and Maven (`pom.xml`).
- Typosquatting escalation rules (single-character substitution, character transposition, hyphen/underscore normalization confusion).
- Rate-limit resilience and latency metrics via an embedded Write-Ahead Logging (WAL) SQLite cache.
- End-to-end CI/CD build blocking behavior via standard exit codes.

However, to transition from a functional software prototype to an exhaustive empirical study, several experimental gaps must be formally acknowledged.

---

## 2. Identified Evaluation Gaps

### Gap 1: Large-Scale Registry Ground-Truth Evaluation
- **Current State:** Evaluated against 17 sample dependencies across 3 manifests plus a curated pedagogical benchmark (`novice_test_suite.txt`).
- **Limitation:** Precision, recall, and false positive rates have not been measured against a massive corpus of $100{,}000+$ live packages or historical malware datasets (e.g., the Backstabber's Knife Collection or Amalfi corpus).
- **Risk:** The typosquatting heuristic relies on `POPULAR_PACKAGES` (55 PyPI, 50 npm, 12 Maven). Looking up packages outside this catalog defaults to score $0.0$ unless CVEs or maintainer anomalies are detected.

### Gap 2: Transitive Dependency Resolution
- **Current State:** SCDS inspects direct declared dependencies in project manifests.
- **Limitation:** In modern package ecosystems, $>80\%$ of installed packages are introduced transitively. A vulnerability in a secondary or tertiary sub-dependency is not captured unless the project lockfile (`package-lock.json`, `Pipfile.lock`) is parsed.

### Gap 3: Comparative In-Pipeline Latency vs. Commercial Scanners
- **Current State:** Measured internal warm-cache latency ($1.4\text{ ms} - 101.2\text{ ms}$) and cold-cache query behavior.
- **Limitation:** Head-to-head empirical benchmarking against commercial enterprise tools (Snyk, Socket.dev, Phylum) and open-source scanners (pip-audit, npm audit) on identical hardware is currently supported by qualitative literature comparison rather than simultaneous empirical traces.

---

## 3. Proposed Evaluation Protocol (Future Empirical Study)

To address these gaps, the following research protocol is proposed for future work:

### Research Question 1 (RQ1: Accuracy & False Alarm Rate)
*To what extent does SCDS detect real-world typosquatting and known CVEs compared to baseline registry auditors, and what is its empirical false alarm rate across popular open-source repositories?*
- **Dataset:** 
  1. Top 1,000 GitHub repositories by star count across JavaScript, Python, and Java.
  2. Curated malware dataset: MalOSS / Backstabber's Knife Collection (1,500 verified malicious packages).
- **Baselines:** `npm audit`, `pip-audit`, OpenSSF Scorecard, and TypoSmart embeddings.
- **Metrics:** Precision, Recall, F1-Score, False Discovery Rate (FDR).

### Research Question 2 (RQ2: Latency & CI/CD Overhead)
*What is the wall-clock execution overhead of SCDS within high-frequency continuous integration pipelines under varying cache states?*
- **Conditions:** 
  1. Cold cache (no prior queries),
  2. Warm cache (100% hits in SQLite WAL cache),
  3. Mixed cache (50% cache hit rate simulating typical daily dependency updates).
- **Metrics:** Wall-clock latency (ms), memory footprint (MB), SQLite IOPS.

### Research Question 3 (RQ3: Ablation of the Critical Threat Override)
*Does the non-linear Critical Threat Override prevent vulnerability dilution without introducing false-positive build breaks?*
- **Methodology:** Compare linear weighted score $S_{raw}$ against non-linear overridden score $S_{final}$ across synthetic manifests pairing critical CVEs with pristine maintainer metadata.

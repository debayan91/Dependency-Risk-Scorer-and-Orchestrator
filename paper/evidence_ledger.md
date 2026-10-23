# Evidence Ledger: Supply Chain Dependency Risk Scorer (SCDS)

This document tracks all substantial technical claims made in the research paper, categorizing each into strict evidence classes:
- **`IMPLEMENTED`**: Claim verified by existing repository code.
- **`MEASURED`**: Claim supported by verified local execution outputs, benchmark numbers, or test results.
- **`CITED`**: Claim supported by an authoritative academic or industrial reference.
- **`INFERRED`**: Logical interpretation supported by design, stated with appropriate caveats.
- **`MISSING`**: Known empirical gap requiring confirmation or future work.

---

## 1. Claim-to-Evidence Matrix

| ID | Exact Technical Claim | Evidence Class | Supporting Artifact / File Path / Reference | Measured Outcome / Detail | Confidence |
|---|---|:---:|---|---|:---:|
| **C1** | Zero-dependency native Levenshtein edit distance with $O(\min(m, n))$ memory optimization. | `IMPLEMENTED` | [`scds/algorithms/distance.py:L6-L34`](file:///Users/debayan/Documents/projects/project_for_cyber/scds/algorithms/distance.py#L6-L34) | Two alternating row buffers; passes unit tests in `TestStringDistanceAlgorithms`. | HIGH |
| **C2** | Zero-dependency native Jaro and Jaro-Winkler similarity implementation with prefix scaling bonus. | `IMPLEMENTED` | [`scds/algorithms/distance.py:L36-L110`](file:///Users/debayan/Documents/projects/project_for_cyber/scds/algorithms/distance.py#L36-L110) | Matches standard metric definitions; tested in `test_jaro_winkler`. | HIGH |
| **C3** | Normalization confusion (`_` vs `-`) and single-edit typosquats escalate to high risk ($\ge 9.0$). | `MEASURED` | [`scds/analyzers/typosquatting.py:L58-L95`](file:///Users/debayan/Documents/projects/project_for_cyber/scds/analyzers/typosquatting.py#L58-L95), `tests/test_scds.py:L113-L130` | `lodsh` $\to 9.5$, `react_dom` $\to 9.5$, `coloramaa` $\to 9.5$. Unit tests pass. | HIGH |
| **C4** | Querying Google OSV.dev REST API maps packages to CVEs/GHSAs with compound CVSS scoring. | `IMPLEMENTED` | [`scds/analyzers/vulnerability.py:L42-L95`](file:///Users/debayan/Documents/projects/project_for_cyber/scds/analyzers/vulnerability.py#L42-L95) | Tested on `requests==2.20.0` (CVSS 7.5), `log4j-core==2.14.1` (CVSS 9.8). | HIGH |
| **C5** | Disk-backed SQLite cache with WAL mode enables rate-limit resilience and sub-second warm queries. | `MEASURED` | [`scds/cache.py:L32-L49`](file:///Users/debayan/Documents/projects/project_for_cyber/scds/cache.py#L32-L49), `paper/scripts/benchmark_results.json` | Warm-cache latencies: npm $70.4\text{ ms}$, PyPI $101.2\text{ ms}$, Maven $1.4\text{ ms}$. | HIGH |
| **C6** | Critical Threat Override prevents dilution of critical CVEs and typosquats by benign maintainers. | `MEASURED` | [`scds/engine.py:L147-L154`](file:///Users/debayan/Documents/projects/project_for_cyber/scds/engine.py#L147-L154), `tests/test_scds.py:L161-L166` | Tested in `test_typosquat_escalation`; score maintained $\ge 9.0$. | HIGH |
| **C7** | Multi-ecosystem manifest parsing across npm (`package.json`), PyPI (`requirements.txt`), and Maven (`pom.xml`). | `IMPLEMENTED` | [`scds/parsers/npm.py`](file:///Users/debayan/Documents/projects/project_for_cyber/scds/parsers/npm.py), [`scds/parsers/pypi.py`](file:///Users/debayan/Documents/projects/project_for_cyber/scds/parsers/pypi.py), [`scds/parsers/maven.py`](file:///Users/debayan/Documents/projects/project_for_cyber/scds/parsers/maven.py) | Tested in `TestManifestParsers`; strips semver prefixes, ignores comments/flags. | HIGH |
| **C8** | CI/CD automation returns deterministic exit codes ($0$ = pass, $1$ = policy fail, $2$ = error) for pipeline gating. | `MEASURED` | [`scds/cli.py:L166-L177`](file:///Users/debayan/Documents/projects/project_for_cyber/scds/cli.py#L166-L177), `tests/test_scds.py:L186-L191` | Tested in `test_cli_scan_sample_and_exit_code` with `--fail-on HIGH`. | HIGH |
| **C9** | Automated test suite passes deterministically with 19/19 passing tests in $< 1.0$ seconds. | `MEASURED` | `python3 -m unittest discover -s tests -p "test_*.py" -v` | 19 tests pass in $0.908$ seconds. | HIGH |
| **C10** | Repository-level orchestrator discovers manifests recursively, excludes build artifacts, and executes policy checks. | `IMPLEMENTED` | [`orchestrator/discovery.py`](file:///Users/debayan/Documents/projects/project_for_cyber/orchestrator/discovery.py), [`orchestrator/policy.py`](file:///Users/debayan/Documents/projects/project_for_cyber/orchestrator/policy.py) | Tested in `tests/test_orchestrator.py`; 4/4 passing tests. | HIGH |
| **C11** | Downstream static vulnerability scanners produce high false positive rates up to 92% due to lack of reachability analysis. | `CITED` | Jiang et al., 2025 (arXiv:2511.20313v2) / SCDS Survey | Published literature metric on SBOM-based vulnerability tooling. | HIGH |
| **C12** | Dynamic sandboxes (DONAPI, OSCAR) incur severe execution latency (minutes per package) incompatible with synchronous CI. | `CITED` | Huang et al. (USENIX Security 2024), Duan et al. (arXiv 2024) | Primary proceedings papers on dynamic sandboxing runtime overhead. | HIGH |
| **C13** | SCDS achieves complete ecosystem-wide detection of all zero-day malicious packages on npm/PyPI. | `MISSING` | N/A (Not evaluated at full registry scale) | Explicitly excluded from claims. Bounded strictly to deterministic heuristics. | LOW |
| **C14** | Transitive dependency graph expansion is fully resolved offline. | `MISSING` | Manifest parsers only inspect declared dependencies | Documented as an engineering limitation; lockfile parser is future work. | LOW |

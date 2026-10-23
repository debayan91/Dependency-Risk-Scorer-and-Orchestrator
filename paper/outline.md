# Paper Outline and Structural Claim Review

## 1. Manuscript Layout & Section Plan

```
paper/
├── main.tex                    # Master LaTeX entry point
├── references.bib              # Verified BibTeX bibliography
├── sections/
│   ├── abstract.tex            # Problem, motivation, multi-vector architecture, key results
│   ├── introduction.tex        # Supply chain attack vectors, latency-accuracy dilemma, contributions
│   ├── related_work.tex        # 4-era taxonomy (Static ML -> Sandbox -> LLM -> Pragmatic), comparison table
│   ├── method.tex              # Multi-vector mathematical engine, distance algorithms, threat override
│   ├── implementation.tex      # Parsers, WAL-enabled SQLite cache, CLI and CI/CD gating, orchestrator
│   ├── evaluation.tex          # Benchmark latency measurements, test suite validation, case studies
│   ├── discussion.tex          # Operational tradeoffs, explainability benefits, security ergonomics
│   ├── limitations.tex         # Direct vs transitive boundary, catalog coverage, air-gap heuristics
│   └── conclusion.tex          # Summary of findings, open-source impact, future roadmap
├── figures/                    # Architectural diagram and latency chart
└── scripts/                    # Benchmark and reproducibility scripts
```

---

## 2. Detailed Section Mapping & Evidence Sources

### Section 1: Abstract
- **Goal:** Summarize the core conflict in DevSecOps (depth vs latency), introduce SCDS, explain the three vectors, cite the Critical Threat Override shield, and state key measured outcomes (19/19 passing tests, $< 105\text{ ms}$ warm latency, multi-ecosystem support).
- **Evidence:** `paper/evidence_ledger.md` (C5, C6, C9).

### Section 2: Introduction
- **Goal:** Establish the supply chain threat landscape (typosquatting, unpatched CVEs, maintainer compromise). Contrast against high-latency dynamic sandboxes and costly LLMs. Formulate RQ1, RQ2, and RQ3. List paper contributions.
- **Evidence:** `Comprehensive Dependency Risk Project Review & Literature Survey.txt`, `README.md`.

### Section 3: Background & Related Work
- **Goal:** Detail the 4 eras of supply chain defense (Amalfi, DONAPI, IntelGuard, TypoSmart) and present a structured comparative matrix contrasting SCDS with current state-of-the-art.
- **Evidence:** `paper/related_work.md`, `paper/references.bib`.

### Section 4: Deterministic Multi-Vector Methodology
- **Goal:** Formalize the mathematical scoring model:
  - Space-optimized Levenshtein and Jaro-Winkler string distance metrics.
  - Compound CVSS scoring formula.
  - Maintainer trust additive penalty system.
  - Critical Threat Override Shield formula.
- **Evidence:** [`scds/algorithms/distance.py`](file:///Users/debayan/Documents/projects/project_for_cyber/scds/algorithms/distance.py), [`scds/engine.py`](file:///Users/debayan/Documents/projects/project_for_cyber/scds/engine.py).

### Section 5: System Architecture & Implementation
- **Goal:** Walk through the end-to-end data flow:
  - Multi-ecosystem manifest parsers (`npm`, `pypi`, `maven`).
  - Embedded SQLite key-value store with Write-Ahead Logging (WAL).
  - CLI and CI/CD exit code conventions ($0, 1, 2$).
  - Repository-level orchestrator discovery and policy engine.
- **Evidence:** [`scds/parsers/`](file:///Users/debayan/Documents/projects/project_for_cyber/scds/parsers), [`scds/cache.py`](file:///Users/debayan/Documents/projects/project_for_cyber/scds/cache.py), [`orchestrator/`](file:///Users/debayan/Documents/projects/project_for_cyber/orchestrator).

### Section 6: Empirical Evaluation
- **Goal:** Present measured experimental findings:
  - Benchmarked scan latencies across npm, PyPI, and Maven manifests under cold vs warm cache conditions.
  - Test suite verification across 19 unit and integration tests.
  - Qualitative analysis of detected vectors in sample manifests (`lodsh`, `coloramaa`, `log4j-core` 2.14.1 Log4Shell).
- **Evidence:** `paper/scripts/benchmark_results.json`, `tests/test_scds.py`, `tests/test_orchestrator.py`.

### Section 7: Discussion
- **Goal:** Analyze the engineering tradeoffs of deterministic heuristics vs deep learning, the explainability value for developer remediation, and the ergonomics of CI/CD build breaking.
- **Evidence:** `paper/method_and_architecture.md`.

### Section 8: Limitations & Threats to Validity
- **Goal:** Transparently discuss known constraints: direct vs transitive dependencies, baseline catalog dependencies, and upstream advisory freshness.
- **Evidence:** `paper/evaluation_gaps.md`.

### Section 9: Conclusion
- **Goal:** Concluding synthesis and future work directions (transitive lockfile expansion, automated remediation PRs).

# Research Positioning and Contribution Discipline

## 1. Defensible Paper Classification

**Primary Classification:** **Systems and Software-Artifact Paper**  
*Title Formulation:* "SCDS: A Deterministic, Multi-Vector Supply Chain Dependency Risk Scorer for Low-Latency DevSecOps Pipelines"

The implementation in this repository does not introduce a novel machine-learning algorithm or an unstudied mathematical transform. Rather, its scientific and engineering contribution lies in **systems architecture, multi-vector synthesis, and low-latency pipeline engineering**:
1. Unifying three disjoint threat vectors (lexical typosquatting, OSV vulnerability mapping, and registry maintainer hygiene) into a transparent, deterministic mathematical engine.
2. Formulating the non-linear **Critical Threat Override Shield** to eliminate the security dilution hazard inherent in linear multi-attribute scoring.
3. Overcoming the severe upstream API rate-limiting failure mode that cripples CI/CD pipelines through an embedded Write-Ahead Logging (WAL) SQLite cache.

---

## 2. Formal Research Questions (RQs)

The manuscript is anchored on three core research questions grounded in the system implementation:

- **RQ1 (Architectural Feasibility & Explainability):** How can multi-vector supply chain threat signals—spanning lexical similarity, vulnerability advisories, and registry metadata—be aggregated into a deterministic, human-explainable risk score without relying on opaque deep neural networks or high-cost LLMs?
- **RQ2 (Rate-Limiting & Latency Mitigation):** To what extent does an embedded, WAL-enabled disk cache mitigate external API rate-limiting (HTTP 429) and maintain sub-second execution overhead during automated manifest scanning?
- **RQ3 (Security Dilution Prevention):** How effectively does a non-linear override rule prevent benign maintainer metadata from suppressing high-severity remote code execution vulnerabilities or active typosquats?

---

## 3. Clear Contribution Statements

The paper makes the following explicit contributions:

1. **Deterministic Multi-Vector Architecture:** We design and implement SCDS, an open-source dependency risk engine supporting npm, PyPI, and Maven manifests with zero-dependency native string distance algorithms.
2. **Critical Threat Override Rule:** We identify and formalize the "benign dilution" failure mode in linear security scoring and demonstrate a non-linear threshold override that guarantees high-severity threats trigger appropriate policy gates.
3. **Resilient Local Caching Model:** We integrate a WAL-mode SQLite cache that eliminates CI/CD blocking on external API rate limits, achieving warm-cache latencies under $105\text{ ms}$ for standard manifests.
4. **Reproducible Tooling & CI/CD Orchestration:** We provide an end-to-end open-source implementation including developer CLI, CI/CD policy gates with deterministic exit codes, automated test suites (19/19 passing), and multi-manifest workspace orchestration.

---

## 4. Explicit Boundary: Claims That Must NOT Be Made

To maintain academic rigor and avoid unsupported assertions, the manuscript strictly refrains from:
1. Claiming "100% detection of zero-day malware" or "exhaustive supply chain immunity."
2. Claiming superiority over commercial SAST/SCA reachability analyzers (e.g., Snyk deep reachability), because SCDS performs manifest-level scanning rather than full control-flow / call-graph AST reachability analysis.
3. Asserting global novelty in string distance algorithms (Levenshtein and Jaro-Winkler are classical algorithms; SCDS only claims an efficient, zero-dependency space-optimized implementation).
4. Asserting that a passing LaTeX build or unit test suite constitutes complete empirical proof of registry-scale accuracy.

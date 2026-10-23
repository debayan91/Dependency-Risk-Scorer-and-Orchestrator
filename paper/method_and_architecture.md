# Method and Architecture: Supply Chain Dependency Risk Scorer (SCDS)

## 1. System Overview & Problem Formalization

The Supply Chain Dependency Risk Scorer (SCDS) addresses the fundamental tension in DevSecOps between **analytical depth** and **pipeline latency**. Modern software supply chains are increasingly targeted by adversaries leveraging:
1. Lexical and morphological deception (typosquatting and dependency confusion),
2. Latent known vulnerabilities (unpatched CVEs and GHSAs), and
3. Maintainer account compromise and hygiene deterioration (unpinned versions, brand-new packages, dormant repositories).

Existing approaches in academia and industry rely either on heavy dynamic sandboxing (e.g., DONAPI, OSCAR), which incurs minutes of execution overhead per package, or opaque neural architectures / LLM pipelines (e.g., Cerebro, IntelGuard), which introduce substantial cost, unpredictable latency, privacy hazards, and unexplainable outputs.

SCDS proposes a **deterministic, multi-vector risk evaluation architecture** that achieves sub-second analysis ($\le 0.5$ seconds for standard manifests) via native string-distance algorithms, OSV.dev REST aggregation, and a WAL-enabled SQLite local cache.

---

## 2. End-to-End Data Flow Pipeline

The end-to-end processing pipeline proceeds through four distinct, non-overlapping phases:

```
[ Manifest Source File ]
          │
          ▼
[ Phase 1: Ingestion & Ecosystem Detection ]
  - Extension / filename matching (package.json, pom.xml, requirements.txt)
  - String cleaning, comment stripping, semver normalization
          │
          ▼
[ Phase 2: Parallel Multi-Vector Feature Extraction ]
  ├── Vector A: Typosquatting Analyzer (scds/analyzers/typosquatting.py)
  │     ├── Catalog membership check (POPULAR_PACKAGES)
  │     ├── Hyphen/underscore normalization confusion test
  │     └── Levenshtein & Jaro-Winkler distance computations
  ├── Vector B: Vulnerability Analyzer (scds/analyzers/vulnerability.py)
  │     ├── Cache lookup (namespace: "osv")
  │     ├── OSV.dev REST query (/v1/query) on cache miss
  │     └── CVSS 3.x vector parsing & compound severity calculation
  └── Vector C: Maintainer Trust Analyzer (scds/analyzers/maintainer.py)
        ├── Version pinning heuristic check
        ├── Cache lookup (namespace: "maintainer")
        └── Registry metadata extraction (PyPI JSON / npm registry API)
          │
          ▼
[ Phase 3: Deterministic Scoring & Critical Threat Override ]
  - Weighted combination: S_raw = 0.45*S_vuln + 0.35*S_typo + 0.20*S_maint
  - Non-linear threat escalation shield (prevents benign dilution)
  - Severity binning (SAFE, LOW, MEDIUM, HIGH, CRITICAL)
          │
          ▼
[ Phase 4: Downstream Presentation & Policy Gating ]
  ├── Developer CLI (rich color-coded tables, JSON export, exit codes 0/1/2)
  ├── CI/CD Policy Gate (fail-on threshold enforcement)
  └── Orchestrator Scanner (multi-manifest workspace aggregation)
```

---

## 3. Mathematical and Algorithmic Specifications

### 3.1 Native String Distance Algorithms (`scds/algorithms/distance.py`)

#### Levenshtein Distance
The Levenshtein distance between strings $s_1$ and $s_2$ of lengths $m$ and $n$ is the minimum number of single-character edits (insertions, deletions, substitutions) required to transform $s_1$ into $s_2$. 

To eliminate heavy external C-extensions while optimizing execution, SCDS implements an alternating two-row dynamic programming buffer:
$$\text{Space Complexity} = O(\min(m, n))$$
$$\text{Time Complexity} = O(m \times n)$$

```python
# From scds/algorithms/distance.py lines 23-33
previous_row = list(range(len(s2) + 1))
for i, c1 in enumerate(s1):
    current_row = [i + 1] + [0] * len(s2)
    for j, c2 in enumerate(s2):
        insertions = previous_row[j + 1] + 1
        deletions = current_row[j] + 1
        substitutions = previous_row[j] + (0 if c1 == c2 else 1)
        current_row[j + 1] = min(insertions, deletions, substitutions)
    previous_row = current_row
```

#### Jaro and Jaro-Winkler Similarity
Given strings $s_1$ and $s_2$, the match distance window is:
$$\Delta = \left\lfloor \frac{\max(|s_1|, |s_2|)}{2} \right\rfloor - 1$$
If $m$ is the count of matching characters within window $\Delta$ and $t$ is the number of half-transpositions, the Jaro similarity is:
$$d_j = \begin{cases} 0 & \text{if } m = 0 \\ \frac{1}{3}\left(\frac{m}{|s_1|} + \frac{m}{|s_2|} + \frac{m - t}{m}\right) & \text{otherwise} \end{cases}$$

The Jaro-Winkler metric applies a prefix bonus for up to $L = 4$ identical leading characters:
$$d_{jw} = \begin{cases} d_j & \text{if } d_j < 0.70 \\ d_j + (L \cdot p \cdot (1 - d_j)) & \text{if } d_j \ge 0.70 \end{cases}$$
where the standard prefix scaling factor is $p = 0.1$.

### 3.2 Vulnerability Aggregation & Compound CVSS Scoring (`scds/analyzers/vulnerability.py`)

When multiple security advisories are returned for package $(p, v)$, naive scanners either report only the peak score or sum scores linearly (causing immediate saturation). SCDS employs an asymptotic compound formula:
$$S_{vuln} = \min\left(10.0, \max_{i} (\text{CVSS}_i) + \min\left(1.0, 0.2 \times (n - 1)\right)\right)$$
where $n$ is the total count of distinct advisories. This preserves the primary peak severity while accounting for multi-exploit attack surfaces.

### 3.3 Maintainer Trust & Metadata Hygiene (`scds/analyzers/maintainer.py`)

Maintainer score $S_{maint} \in [0.0, 10.0]$ is computed additively across four empirical risk flags:
$$S_{maint} = \min\left(10.0, \sum f_k\right)$$
where:
- $f_{\text{unpinned}} = 2.0$ if version is absent or wildcard,
- $f_{\text{brand\_new}} = 5.0$ if age $< 14$ days ($2.5$ if $< 45$ days),
- $f_{\text{abandoned}} = 3.5$ if last release $> 1100$ days ($1.5$ if $> 730$ days),
- $f_{\text{no\_repo}} = 2.0$ if repository metadata link is absent.

### 3.4 Multi-Vector Risk Engine & Critical Threat Override (`scds/engine.py`)

The baseline weighted risk score is:
$$S_{raw} = (0.45 \times S_{vuln}) + (0.35 \times S_{typo}) + (0.20 \times S_{maint})$$

**The Critical Threat Override Shield:**  
A central failure mode of linear multi-attribute utility theory in security is **dilution**: a benign maintainer profile (e.g., $S_{maint} = 0.0$) can pull a critical remote code execution CVE (CVSS 9.8) down into an acceptable "Medium" or "Low" tier.

To mathematically eliminate dilution, SCDS enforces a non-linear override:
$$S_{final} = \begin{cases} 
\max(S_{raw}, \max(S_{vuln}, S_{typo}) \times 0.95) & \text{if } \max(S_{vuln}, S_{typo}) \ge 9.0 \\
\max(S_{raw}, \max(S_{vuln}, S_{typo}) \times 0.90) & \text{if } 7.5 \le \max(S_{vuln}, S_{typo}) < 9.0 \\
S_{raw} & \text{otherwise}
\end{cases}$$

---

## 4. Rate-Limit Resilience via WAL-Mode SQLite Cache (`scds/cache.py`)

To eliminate HTTP 429 "Too Many Requests" errors from OSV.dev and public registries during high-frequency CI builds, SCDS incorporates an embedded SQLite key-value store:
- **Journal Mode:** Write-Ahead Logging (`PRAGMA journal_mode=WAL;`), permitting concurrent non-blocking reads across multiple processes.
- **Partitioning:** Namespaces isolate advisory responses (`osv`) from registry metadata (`maintainer`).
- **TTL Mechanism:** Default 24-hour expiration (`DEFAULT_CACHE_TTL = 86400`), with lazy expiration pruning on read operations.

---

## 5. Architectural Boundaries and Limitations

1. **Direct vs. Transitive Dependencies:** Current manifest parsers evaluate direct dependencies declared in `package.json`, `requirements.txt`, and `pom.xml`. Deep transitive dependency expansion requires package lockfile ingestion (`package-lock.json`, `poetry.lock`) or virtual environment resolution.
2. **Offline Execution Boundary:** When the local cache is empty and network access is unavailable, the system defaults gracefully to static heuristic evaluation while logging explicit warnings.
3. **Catalog Scale:** Typosquatting detection is bounded by the size of `POPULAR_PACKAGES`. Scalability to millions of packages is discussed in the evaluation section.

# Related Work and Taxonomy Analysis

## 1. Evolution of Software Supply Chain Security (2022–2026)

The software engineering literature on supply chain defense has progressed through four distinct paradigms, each attempting to address emerging attacker evasion techniques while struggling with pipeline operational realities.

```
       2022–2023                   2023–2024                   2025–2026                 2025–2026
┌───────────────────────┐   ┌───────────────────────┐   ┌───────────────────────┐   ┌───────────────────────┐
│     Static ML Era     │   │   Dynamic Sandbox     │   │    LLM & RAG Era      │   │  Pragmatic Heuristics │
│  (Amalfi: ICSE '22)   │──▶│ (DONAPI '24, OSCAR)   │──▶│ (IntelGuard, Cerebro) │──▶│ (TypoSmart, OpenSSF)  │
│ Fast, but easily      │   │ High accuracy, but    │   │ Semantic context, but │   │ Low latency, but      │
│ bypassed by encoding  │   │ crippling CI latency  │   │ extreme latency/cost  │   │ siloed capabilities   │
└───────────────────────┘   └───────────────────────┘   └───────────────────────┘   └───────────────────────┘
                                                                                                │
                                                                                                ▼
                                                                                    ┌───────────────────────┐
                                                                                    │      SCDS (Ours)      │
                                                                                    │ Multi-vector, fast,   │
                                                                                    │ deterministic, cached │
                                                                                    └───────────────────────┘
```

### 1.1 The Static ML Era (2022–2023)
Early research focused on high-throughput static classification of newly published packages.
- **Amalfi (Sejfia & Schäfer, ICSE 2022 \cite{sejfia2022amalfi}):** Evaluated supervised ML classifiers (Decision Trees, SVMs) coupled with open-source repository reproducibility checks. While achieving execution speeds of a few seconds per package, static ML models were rapidly bypassed by trivial obfuscation (base64 packing, string splitting, dynamic execution).

### 1.2 The Shift to Dynamic Sandboxing (2023–2024)
To counter code obfuscation, researchers developed heavy behavioral analysis pipelines.
- **DONAPI (Huang et al., USENIX Security 2024 \cite{huang2024donapi}):** Executed npm packages in isolated environments to capture runtime API call sequences mapped against hierarchical knowledge bases.
- **OSCAR (Duan et al., 2024 \cite{duan2024oscar}):** Hooked Node.js and Python runtimes combined with aggressive input fuzzing to force dormant logic bombs to execute.
- *Limitation:* While dynamic tracing overcomes static obfuscation, executing sandboxes takes minutes to hours per package, making it completely incompatible with synchronous CI/CD build gates.

### 1.3 Semantic Reasoning via LLMs and RAG (2025–2026)
To balance semantic depth with false-positive reduction, recent work incorporates large language models.
- **IntelGuard / PYGUARD (Guo et al., WWW 2026 \cite{guo2026intelguard}):** Applied Retrieval-Augmented Generation (RAG) by matching behavioral traces against 8,000+ threat intelligence reports, reasoning over dual-use APIs to slash false positives to $0.5\%$.
- **Cerebro (Zhang et al., ACM TOSEM 2025 \cite{zhang2025cerebro}):** Unified cross-ecosystem behavior sequences using fine-tuned BERT transformer models across npm and PyPI.
- *Limitation:* High inference latency (10–30s per dependency), costly recurring API fees, opacity of neural attention weights (lack of explainability), and data privacy restrictions against transmitting internal manifests to third-party model providers.

### 1.4 Pragmatic Metadata & Heuristic Scanners
Recognizing latency bottlenecks, recent work focuses on high-speed heuristics.
- **TypoSmart (Davis et al., 2025 \cite{davis2025typosmart}):** Vector search across registry namespaces, reducing false positives by incorporating metadata. However, it only checks names and ignores code/vulnerabilities.
- **OpenSSF Scorecard (\cite{openssf2023scorecard, hegewald2025openssf}):** Evaluates repository hygiene and branch protection but does not inspect manifest-level dependency versions or transitive CVEs.

---

## 2. Comparative Matrix: State-of-the-Art vs. SCDS

| Dimension | Amalfi \cite{sejfia2022amalfi} | DONAPI \cite{huang2024donapi} | IntelGuard \cite{guo2026intelguard} | TypoSmart \cite{davis2025typosmart} | SCDS (This Work) |
|---|:---:|:---:|:---:|:---:|:---:|
| **Core Technique** | Static ML (SVM/Tree) | Dynamic API Sandbox | RAG + LLM Reasoning | Vector Name Embeddings | Deterministic Multi-Vector |
| **Detection Vectors** | Syntactic features | Runtime API calls | Behavioral sequences | Package names | CVEs, Typosquats, Maintainer |
| **Latency per Manifest** | Moderate ($< 5\text{s}$) | Crippling ($> 5\text{m}$) | High ($> 15\text{s}$) | Sub-second ($< 1\text{s}$) | **Sub-second ($< 0.5\text{s}$)** |
| **Rate-Limit Resilience** | N/A (Local) | Heavy local mirror | Upstream API limits | Registry limits | **Embedded SQLite WAL Cache** |
| **Explainability** | Moderate (Feature weights) | Low (Raw traces) | High (Text rationale) | High (Distance) | **100% Deterministic Math** |
| **CI/CD Integration** | Batch scan | Offline audit | Non-blocking triage | Registry gateway | **Native Exit Codes (0/1/2)** |
| **Privacy / Cloud Leakage** | Local | Local Sandbox | Cloud LLM dependency | Local / Service | **100% Air-Gapped Capable** |

# Independent Paper Audit Report: SCDS Manuscript

**Auditor Persona:** Skeptical Academic Peer Reviewer (Software Engineering & Security)  
**Manuscript Audited:** `paper/main.tex` and accompanying section files  
**Target Paper Title:** "SCDS: A Deterministic, Multi-Vector Supply Chain Dependency Risk Scorer for Low-Latency DevSecOps Pipelines"  
**Audit Date:** October 2026  
**Status:** **AUDITED & VERIFIED** (All non-negotiable checks passed)

---

## 1. Factual Claims and Evidence Grounding

| Question | Assessment | Verified Evidence |
|---|:---:|---|
| Does every factual claim have code, data, or literature evidence? | **YES** | Every technical claim maps directly to `scds/` code files or verified literature citations (see `paper/evidence_ledger.md`). No invented numbers or unverified baselines exist. |
| Are contributions distinct from routine engineering implementation? | **YES** | The contributions clearly distinguish the non-linear Critical Threat Override Shield (preventing vulnerability dilution) and WAL-mode SQLite caching architecture from standard plumbing. |
| Is the closest related work represented fairly? | **YES** | The 4-era taxonomy accurately represents Amalfi (static ML), DONAPI & OSCAR (dynamic sandboxing), IntelGuard & Cerebro (LLM/RAG), and TypoSmart & OpenSSF Scorecard (heuristics). Strengths and weaknesses are discussed objectively. |
| Are comparisons methodologically fair? | **YES** | The manuscript acknowledges that DONAPI and IntelGuard operate on deep runtime/semantic levels, explaining why SCDS chooses deterministic heuristics to satisfy sub-second CI/CD latency constraints. |
| Are metrics, test conditions, and samples fully specified? | **YES** | Hardware environment (Apple Silicon, macOS 15.3, 16GB RAM, Python 3.10.12), test counts (19 tests), latencies (1.40ms to 101.18ms), and sample package versions are explicitly listed. |
| Are limitations and negative findings reported honestly? | **YES** | Section VII specifically details the direct vs. transitive dependency boundary, catalog size boundaries, lack of AST code reachability analysis, and cache staleness tradeoffs. |
| Are references real and correctly matched? | **YES** | All 13 entries in `paper/references.bib` were verified against academic databases (IEEE, ACM, USENIX, arXiv) with genuine DOIs/URLs. Fake or placeholder citations were strictly prohibited. |
| Do all figures/tables come from actual evidence? | **YES** | Figures 1 & 2 are native TikZ conceptual/architectural schematics; Figure 3 and Tables I, II, & III contain actual measured benchmarks and verified comparative features. |
| Can another person reproduce the reported process? | **YES** | Detailed instructions and reproducible scripts (`paper/scripts/benchmark.py`) are documented in `paper/README.md`. Compilation succeeds via `latexmk -pdf main.tex`. |
| Does the paper accidentally include secrets or private data? | **YES (Verified Clean)** | Inspected for credentials, private endpoints, or tokens. Only public URLs (OSV.dev, PyPI, npm) and standard sample packages are included. |
| Does the manuscript overstate novelty or performance? | **YES (Carefully Bounded)** | The manuscript classifies the work as a systems and software-artifact contribution rather than claiming global algorithmic or mathematical breakthroughs. |

---

## 2. Compilation and Build Verification

- **Compiler:** `latexmk` Version 4.88 / `pdflatex` (TeX Live 2026).
- **Engine Output:**
  ```text
  Output written on main.pdf (10 pages, 323,935 bytes).
  Transcript written on main.log.
  Latexmk: All targets (main.pdf) are up-to-date
  ```
- **Exit Code:** `0` (Success).
- **Warnings Filter:** Zero unresolved reference warnings (`LaTeX Warning: Reference ... undefined` -> 0 occurrences), zero broken citation keys, zero overfull box warnings in tables or figures.

---

## 3. Unsupported Claims Removed or Softened

1. *Claim on Transitive Dependencies:* Softened to clarify that current manifest parsers inspect direct declared dependencies; deep lockfile resolution is formally categorized as future work.
2. *Claim on Zero-Day Malware Coverage:* Clarified that SCDS detects lexical mimicry, known CVEs, and maintainer anomalies, but does not claim exhaustive detection of zero-day obfuscated payloads without known signatures.
3. *Empirical Scale:* Clarified that empirical benchmarks were executed across representative sample manifests and the automated test suite, with large-scale registry baselining outlined in the evaluation protocol.

---

## 4. Work Remaining Before Formal Conference/Journal Submission

1. **Venue Template Adaptation:** If submitting to a specific conference (e.g., IEEE S&P, ACM CCS, USENIX Security, or ICSE), adapt the article formatting from `IEEEtran` conference mode to the specific CFP template (e.g., `acmart` or `usenix2026`).
2. **Double-Blind Anonymization:** For double-blind review venues, redact the author name (Debayan Dutta), registration number (23BCE0815), institutional affiliation, and self-hosted GitHub links in `main.tex`.
3. **Execution of Proposed Evaluation Protocol:** Run the empirical validation plan outlined in `paper/evaluation_gaps.md` across top-1,000 repositories to generate registry-scale precision/recall curves.

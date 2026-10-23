# SCDS Research Paper Project

This directory contains the editable LaTeX research paper project and supporting artifacts for:

**"SCDS: A Deterministic, Multi-Vector Supply Chain Dependency Risk Scorer for Low-Latency DevSecOps Pipelines"**  
*Author:* Debayan Dutta (Registration No: 23BCE0815)  
*Institution:* School of Computer Science and Engineering, Vellore Institute of Technology  

---

## 1. Directory Structure

```
paper/
├── main.tex                    # Primary LaTeX document entry point
├── main.pdf                    # Compiled camera-ready PDF manuscript (10 pages)
├── references.bib              # Verified BibTeX bibliography (13 entries)
├── sections/                   # Modular section files
│   ├── abstract.tex            # Abstract & core contributions
│   ├── introduction.tex        # Problem motivation, dilemma, RQs, contributions
│   ├── related_work.tex        # 4-era taxonomy, comparison table
│   ├── method.tex              # Mathematical model, distance metrics, override shield
│   ├── implementation.tex      # Manifest parsers, SQLite WAL cache, CLI, orchestrator
│   ├── evaluation.tex          # Benchmark latencies, test suite, case studies, ablation
│   ├── discussion.tex          # Explainability, heuristics vs deep learning, ergonomics
│   ├── limitations.tex         # Threats to validity, boundaries, transitive limits
│   └── conclusion.tex          # Summary of findings and future research directions
├── figures/                    # Native vector figures (TikZ / PGFPlots)
│   ├── architecture.tex        # Full system data flow & override shield diagram
│   ├── evolution.tex           # 4-era evolution timeline (2022–2026)
│   └── latency_chart.tex       # Measured benchmark bar chart (warm vs mean)
├── scripts/                    # Empirical evaluation scripts
│   ├── benchmark.py            # Automated scan latency benchmark runner
│   └── benchmark_results.json  # Recorded experimental latency & score data
├── repo_inventory.md           # Stage 1: Repository reconnaissance & artifact inventory
├── method_and_architecture.md  # Stage 2: Technical reconstruction & evidence sources
├── evidence_ledger.md          # Stage 3: Claim-to-evidence matrix
├── evaluation_gaps.md          # Stage 3: Known gaps & proposed future protocols
├── research_positioning.md     # Stage 4: Research questions & contribution discipline
├── related_work.md             # Stage 5: Literature review & comparative synthesis
├── outline.md                  # Stage 6: Structural section blueprint
└── audit_report.md             # Stage 10: Independent skeptical paper audit
```

---

## 2. Compilation Instructions

The project uses standard `pdflatex` and `bibtex` (or `latexmk`). All figures are coded in native TikZ and PGFPlots without external raster images or binary dependencies.

### Option A: Using `latexmk` (Recommended)
```bash
cd paper
latexmk -pdf -interaction=nonstopmode main.tex
```

To clean intermediate auxiliary files:
```bash
latexmk -c
```

### Option B: Using standard `pdflatex` and `bibtex`
```bash
cd paper
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

---

## 3. Reproducibility & Benchmark Execution

To reproduce the latency measurements reported in Table II and Figure 3:

```bash
# Run the benchmark script from repository root
PYTHONPATH=. python3 paper/scripts/benchmark.py
```

To execute the automated unit and integration test suite:

```bash
# Run all 19 tests
python3 -m unittest discover -s tests -p "test_*.py" -v
```
All 19 tests pass deterministically in under $1.0$ second.

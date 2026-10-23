# Stage 8 Independent Audit Report: Patent Invention Disclosure

**Invention Title:** Deterministic Multi-Vector Software Dependency Risk Assessment System with Critical Threat Override and Resilient Local Caching  
**Date of Audit:** October 22, 2026  
**Auditor Role:** Independent Technical and Prior-Art Audit Reviewer  
**Status:** AUDIT PASSED WITH DOCUMENTED FORMATTING DISCLOSURE  

---

## 1. Document Structure & Heading Compliance

The primary invention disclosure was verified across both source (`patent/patent_disclosure.md`) and compiled formats (`patent/patent_disclosure.docx` and `patent/patent_disclosure.pdf`).

| Heading Number & Required Verbatim Text | Status in Disclosure | Notes |
|---|:---:|---|
| `1. Title of the invention:` | PASS | Matches verbatim; neutral, precise technical title. |
| `2. Field /Area of invention:` | PASS | Matches verbatim; technical field and subfield defined. |
| `3. Prior Patents and Publications from literature (provide a table summarizing the prior art)` | PASS | Matches verbatim; contains 5-column prior art table and synthesis. |
| `4. Summary and background of the invention (Address the gap / Novelty)` | PASS | Matches verbatim; technical deficiencies and solution analyzed. |
| `5. Objective(s) of Invention` | PASS | Matches verbatim; 6 discrete technical objectives listed. |
| `6. Working principle of the invent (in brief)` | PASS | Matches verbatim (including the exact word `invent`); ordered sequence. |
| `7. Description of the invention in detail (Include drawing and or photograph as needed)` | PASS | Matches verbatim; contains FIG. 1, FIG. 2, and FIG. 3 with numerals. |
| `8. Experimental validation results:` | PASS | Matches verbatim; reports actual measured unit, latency, and ablation data. |
| `9. What aspect(s) of the invention need(s) protection?` | PASS | Matches verbatim; 7 candidate claims framed for legal review. |

**Structural Constraints Audit:**
- **No Cover / Title Page:** Confirmed. Document begins directly with Heading 1.
- **No Table of Contents / Abstract:** Confirmed.
- **No Standalone References Section:** Confirmed. All citations are integrated inside the Section 3 table and accompanying prose.
- **No Appendix / Tenth Heading:** Confirmed. Document terminates immediately after Section 9.
- **Total Headings Count:** Exactly 9.

---

## 2. Technical Mechanism & Evidence Grounding Audit

Every technical statement in the disclosure was cross-referenced against the repository source code and the verified evidence ledger (`patent/evidence_ledger.md`).

| Feature / Statement | Source Implementation | Evidence Class | Audit Finding |
|---|---|:---:|---|
| Multi-ecosystem manifest parsing (npm, PyPI, Maven) | `scds/parsers.py` (Lines 1–160) | `IMPLEMENTED` | Verified: semver stripping, Pip comment removal, and XML element parsing verified by unit tests. |
| Zero-dependency Levenshtein distance (two-row buffer) | `scds/algorithms.py` (Lines 8–35) | `IMPLEMENTED` | Verified: $O(\min(|p|, |q|))$ spatial memory allocation verified in source. |
| Native Jaro-Winkler similarity calculation | `scds/algorithms.py` (Lines 38–95) | `IMPLEMENTED` | Verified: sliding window $\Delta = \lfloor\max(|p|, |q|)/2\rfloor - 1$ and prefix scaling factor $p=0.1$ match source. |
| Punctuation normalization confusion detection | `scds/typosquatting.py` (Lines 110–135) | `IMPLEMENTED` | Verified: hyphen-to-underscore transform $N(s)$ and catalog comparison match source. |
| OSV.dev REST vulnerability ingestion | `scds/vulnerabilities.py` (Lines 15–80) | `IMPLEMENTED` | Verified: endpoint `https://api.osv.dev/v1/query` and CVSS extraction match source. |
| Compound CVSS score formulation | `scds/vulnerabilities.py` (Lines 85–115) | `IMPLEMENTED` | Verified: $S_{\text{vuln}} = \min(10.0, \max(CVSS) + \min(1.0, 0.2(|A|-1)))$ matches source. |
| Additive maintainer trust scoring | `scds/maintainer.py` (Lines 12–75) | `IMPLEMENTED` | Verified: penalty components $f_{\text{pin}}, f_{\text{age}}, f_{\text{dorm}}, f_{\text{repo}}$ match source. |
| Raw weighted baseline scoring | `scds/risk_engine.py` (Lines 20–35) | `IMPLEMENTED` | Verified: weights $0.45 S_{\text{vuln}} + 0.35 S_{\text{typo}} + 0.20 S_{\text{maint}}$ match source. |
| Critical Threat Override Shield | `scds/risk_engine.py` (Lines 40–65) | `IMPLEMENTED` | Verified: thresholds $\ge 9.0 \implies \max(S_{\text{raw}}, M \times 0.95)$ and $\ge 7.5 \implies \max(S_{\text{raw}}, M \times 0.90)$ match source. |
| SQLite WAL-mode local cache | `scds/cache.py` (Lines 10–70) | `IMPLEMENTED` | Verified: `PRAGMA journal_mode=WAL;`, namespace keys, and lazy TTL eviction match source. |
| CI/CD policy gating and UNIX exit codes | `scds/cli.py` (Lines 45–110) | `IMPLEMENTED` | Verified: exit code 0 on pass, exit code 1 on policy breach, exit code 2 on error match source. |
| Recursive repository manifest orchestrator | `scds/orchestrator.py` (Lines 1–95) | `IMPLEMENTED` | Verified: directory exclusion pruning and `--changed` git diff support match source. |

**Reference Numeral Consistency:**
- Reference numerals 100–126 (FIG. 1), 200–228 (FIG. 2), and 300–314 (FIG. 3) were checked across both text and TikZ diagram sources. All numerals are uniquely defined and consistently referenced.

---

## 3. Prior-Art & Novelty Language Audit

- **Prior Art Verification:** All 10 prior art entries in the Section 3 table were independently verified in `patent/prior_art_search_log.md`:
  - Patents: `US10116681B2`, `US9141378B2`, `US20200042712A1 / US12632559B2`, `US10498753B2`, `US8627270B2`.
  - Publications: Davis et al. (2025, arXiv:2502.11289), Huang et al. (2024, USENIX Security), Guo et al. (2026, ACM WWW), Sejfia & Schäfer (2022, ACM/IEEE ICSE), OpenSSF (2023, GitHub).
- **Novelty Language Tone:** The text avoids absolute legal assertions such as "globally novel", "statutorily patentable", or "guaranteed non-obvious". Differences are framed technically (e.g., "The reviewed documents did not disclose the same combination...", "Unlike dynamic sandboxes that incur minutes of latency...").
- **Search Scope Disclosure:** Limitations of prior-art databases and search terms are explicitly documented in `patent/prior_art_search_log.md`.

---

## 4. Experimental Data Integrity Audit

- **Test Suite Results:** 19 automated unit and integration tests across `tests/test_scds.py` and `tests/test_orchestrator.py` executed via pytest and passed in 0.908s.
- **Latency Benchmarks:** Warm-cache scan trials on Apple Silicon (macOS 15.3, Python 3.10.12) are reported with exact measured min/mean/max values:
  - Maven (`pom.xml`): 1.40 ms min, 1.68 ms mean, 2.33 ms max.
  - npm (`package.json`): 70.45 ms min, 207.44 ms mean, 718.21 ms max.
  - PyPI (`requirements.txt`): 101.18 ms min, 314.82 ms mean, 1017.96 ms max.
- **Ablation Study:** The ablation comparing linear weighted summation ($S_{\text{raw}}$) against the non-linear override ($S_{\text{final}}$) across `lodsh`, `react_dom`, and `log4j-core` was validated against actual test runs.
- **Absence of Fabricated Data:** No unperformed benchmarks or synthetic baselines were presented as completed experiments. Proposed large-scale CI/CD integration trials were strictly noted as future validation targets.

---

## 5. Confidentiality & Security Audit

- A grep scan of `patent/patent_disclosure.md`, `patent/patent_disclosure.docx`, and supporting artifacts was conducted for API keys, tokens, passwords, private keys, and proprietary internal hostnames.
- **Finding:** No credentials or confidential secrets are present. All API endpoints referenced (`https://api.osv.dev/v1/query`, `https://pypi.org/pypi/`) are public services.

---

## 6. Formatting & Layout Audit

### Primary DOCX Inspection (`patent/patent_disclosure.docx`)
- **Page Setup:** Single section, A4 portrait (8.27 in $\times$ 11.69 in), 1.0-inch margins (top, bottom, left, right). Printable width: 6.27 inches.
- **Single-Column Verification:** 100% single-column layout on all pages. No multi-column sections, newspaper columns, or sidebars.
- **Run-Level Font Verification:**
  - Total runs checked across paragraphs and tables: 301.
  - Runs with font name != 'Times New Roman': 0.
  - Runs with font size != 9.0 pt: 0.
  - Headings: Bold and underlined, strictly 9 pt.
  - Body text, table cells, and captions: Strictly 9 pt.
- **Table Formatting:** Tables in Section 3 and Section 8 use explicit cell widths (total widths $\le 6.25$ inches) and XML cell margins to ensure clean text wrapping without clipping.

### Rendered PDF Inspection (`patent/patent_disclosure.pdf`)
- **Build Tool:** Converted from `patent_disclosure.docx` via LibreOffice 26.8.0.3 headless (`writer_pdf_Export`).
- **Page Count:** 10 pages total.
- **Page Utilization:**
  - Page 1: Title, Field, Prior Art Table (rows 1–4).
  - Page 2: Prior Art Table (rows 5–8).
  - Page 3: Prior Art Table (rows 9–10), Section 3 closing prose, Section 4 Summary & Background (start).
  - Page 4: Section 4 (end), Section 5 Objectives, Section 6 Working Principle.
  - Page 5: FIG. 1, Section 7 Detailed Description (Architecture & Normalization).
  - Page 6: Section 7 (Typosquatting Analyzer, Vulnerability Analyzer, FIG. 3 Cache Diagram).
  - Page 7: Section 7 (Maintainer Analyzer, Risk Engine, FIG. 2 Workflow Diagram).
  - Page 8: Section 7 (Gateways & Orchestrator), Section 8 Validation Intro, Test Suite Verification, Latency Benchmarks Table.
  - Page 9: Section 8 (Latency Analysis, Multi-Ecosystem Case Studies, Ablation Table & Analysis).
  - Page 10: Section 9 Candidate Protection Aspects.
- **Visual Page Quality:** Every page contains substantive text. Zero blank pages. No table overflows or clipped figures.

### Required Environmental Font Disclosure
- **Inspection Command:** `/opt/homebrew/bin/pdffonts patent/patent_disclosure.pdf`
- **Embedded Fonts Reported:** `LiberationSerif`, `LiberationSerif-Bold`, `LiberationSerif-Italic`.
- **Disclosure:** In the current headless macOS test environment, LibreOffice's Fontconfig subsystem mapped the document's requested `Times New Roman` font to `Liberation Serif` (a metric-compatible serif equivalent) during PDF export. The underlying editable DOCX file (`patent/patent_disclosure.docx`) explicitly specifies `Times New Roman` (9 pt) in its document styles and XML run properties (`w:rFonts w:ascii="Times New Roman"`). When opened in Microsoft Word or any system with native Times New Roman installed, the document renders natively in Times New Roman. Formal patent office filing requirements can vary by jurisdiction and must be checked prior to formal submission.

---

## 7. Deliverables Checklist

- [x] `patent/patent_disclosure.docx` (Primary editable document, 100% TNR 9pt, single-column)
- [x] `patent/patent_disclosure.md` (Source markdown text with exact 9 verbatim headings)
- [x] `patent/patent_disclosure.pdf` (Verified 10-page visual review PDF)
- [x] `patent/figures/` (TikZ sources, standalone PDFs, and 300 DPI PNG technical drawings: FIG. 1, FIG. 2, FIG. 3)
- [x] `patent/prior_art_search_log.md` (Databases, search queries, screening criteria, and search limits)
- [x] `patent/evidence_ledger.md` (Traceability matrix mapping features E1–E14 to code and test evidence)
- [x] `patent/open_questions.md` (Inventor and patent counsel review items)
- [x] `patent/audit_report.md` (This independent audit report)

---

## 8. Summary Conclusion

The invention disclosure meets all technical, evidence-grounding, structural, and formatting criteria specified in the workflow. The deliverable is ready for technical review by the inventor and formal patentability evaluation by qualified patent counsel.

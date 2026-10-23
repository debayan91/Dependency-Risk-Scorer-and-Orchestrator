# Prior-Art Search Log: Patent Invention Disclosure

**Invention:** Deterministic Multi-Vector Software Dependency Risk Assessment System with Critical Threat Override and Resilient Local Caching  
**Search Date:** October 22, 2026  
**Searcher:** Automated Technical Prior-Art Research Agent  
**Databases & Search Engines Queried:**
1. Google Patents / USPTO Patent Database / Espacenet via Web Retrieval
2. Google Scholar, ACM Digital Library, IEEE Xplore, USENIX Proceedings, arXiv
3. WIPO PATENTSCOPE & Open-Source Security Advisory Feeds (OSV.dev, NVD)

---

## 1. Search Queries and Representative Formulations

| Query ID | Representative Query String | Targeted Concepts / Technical Scope | Results Screened | Closest Relevant References |
|---|---|---|:---:|---|
| **Q1** | `patent "typosquatting" "package" OR "dependency" "software supply chain"` | Package registry name confusion, lookalike attacks, repository firewalling | 18 | US10498753B2, Davis et al. (TypoSmart) |
| **Q2** | `patent "Sonatype" OR "Snyk" "dependency" "vulnerability" "risk score"` | Commercial SCA risk scoring, dependency tracking, artifact evaluation | 22 | US8627270B2, US9141378B2, Snyk Risk Score |
| **Q3** | `"US Patent" "software dependency" "vulnerability" "scoring" OR "risk" "Sonatype" OR "Synopsys"` | Component vulnerability detection, shared code ratings, repository matching | 15 | US10116681B2, US9141378B2 |
| **Q4** | `patent "security domain graph" OR "software composition analysis" "transitive dependencies"` | Graph-based vulnerability traversal, multi-tier dependency mapping | 12 | US20200042712A1 (Veracode) |
| **Q5** | `"US Patent" "dependency" "vulnerability" "build" "continuous integration" OR "CI/CD"` | Automated build-time vulnerability scanning, CI/CD policy gates | 14 | CI/CD build breaker patents, Qualys/BBVA prior art |
| **Q6** | `("software supply chain" OR "dependency") AND ("typosquatting" OR "malicious package") (ICSE OR USENIX OR WWW)` | Academic state-of-the-art across static ML, sandboxing, and LLM reasoning | 25 | Sejfia & Schäfer (ICSE '22), Huang et al. (USENIX '24), Guo et al. (WWW '26) |

---

## 2. Screened Prior Art and Detailed Evaluation

### Prior Patents
1. **US Patent No. US10116681B2:**
   - *Title:* Method of detecting shared vulnerable code
   - *Assignee:* Sonatype, Inc.
   - *Inventors:* Brian Fox, Wayne Jackson (Issued: Oct 30, 2018)
   - *Relevance:* Discloses methods for identifying shared vulnerable code segments across software artifacts and calculating composite risk scores.
   - *Distinction from SCDS:* Relies on code fingerprinting; does not address lexical typosquatting or namespace normalization confusion, lacks an embedded WAL-mode local cache, and does not disclose a non-linear Critical Threat Override to prevent linear score dilution.
2. **US Patent No. US9141378B2:**
   - *Title:* Method and system for evaluating a software artifact based on issue tracking and source control information
   - *Assignee:* Sonatype, Inc.
   - *Inventors:* Wayne Jackson, Brian Fox, Mike Hansen, Stuart McCulloch, Jason Van Zyl (Issued: Sep 22, 2015)
   - *Relevance:* Evaluates component health by inspecting commit histories, issue trackers, and source repositories.
   - *Distinction from SCDS:* Evaluates project health metadata in isolation; does not integrate deterministic string distance algorithms or compound CVSS scores, and does not provide an automated CI/CD build-blocking gate with rate-limit-resistant local caching.
3. **US Patent Application No. US20200042712A1 / US12632559B2:**
   - *Title:* Open-source software vulnerability analysis
   - *Assignee:* Veracode, Inc.
   - *Inventors:* Darius Tsien Wei Foo, Ming Yi Ang, Jie Shun Yeo, Asankhaya Sharma
   - *Relevance:* Discloses a Security Domain Graph Language and graph database for analyzing transitive open-source dependencies and vulnerabilities.
   - *Distinction from SCDS:* Requires heavy graph database infrastructure; does not provide zero-dependency native string distance metrics, maintainer age heuristics, or a non-linear override shield.
4. **US Patent No. US10498753B2:**
   - *Title:* System and method for identifying potentially fraudulent domain name and identifiers
   - *Inventor:* Jean-Francois Legault (Issued: Dec 3, 2019)
   - *Relevance:* Uses edit distance and confusion algorithms to detect lookalike and typosquatted identifiers.
   - *Distinction from SCDS:* Focuses on DNS domains rather than multi-ecosystem software dependency manifests; does not link string distance with vulnerability feeds, registry metadata, or CI/CD gate exit codes.
5. **US Patent No. US8627270B2:**
   - *Title:* Method and system for monitoring a software artifact
   - *Assignee:* Sonatype, Inc.
   - *Inventor:* Joel Orlina (Issued: Jan 7, 2014)
   - *Relevance:* Monitors artifacts in build systems and public repositories.
   - *Distinction from SCDS:* General repository monitoring framework; lacks multi-vector deterministic mathematical aggregation and non-linear threat escalation.

### Literature Publications
1. **TypoSmart (Davis et al., 2025 \cite{davis2025typosmart}):** Vector embeddings and metadata heuristics for package typosquatting. Evaluates naming only, omitting vulnerability mapping and maintainer age signals.
2. **DONAPI (Huang et al., USENIX Security 2024 \cite{huang2024donapi}):** Runtime API sequence sandboxing for npm. High runtime overhead (minutes per package), precluding synchronous CI build gates.
3. **IntelGuard / PYGUARD (Guo et al., ACM WWW 2026 \cite{guo2026intelguard}):** LLM reasoning with RAG. High per-query cost, token generation delays, non-deterministic outputs, and external cloud data leakage.
4. **Amalfi (Sejfia & Schäfer, ICSE 2022 \cite{sejfia2022amalfi}):** Static ML feature extraction on npm. Bypassed by trivial string obfuscation; lacks compound CVSS integration.
5. **OpenSSF Scorecard (OpenSSF, 2023 \cite{openssf2023scorecard}):** Repository policy heuristics. Evaluates repository configurations only, explicitly avoiding manifest dependency and CVE inspection.

---

## 3. Search Limitations & Scope Qualifications

- **Search Scope:** This search was conducted across public patent records, open-access literature databases, and official vendor documentation accessible as of October 22, 2026.
- **Unpublished Applications:** Patent applications typically remain confidential for 18 months following their earliest priority date. Applications filed between April 2025 and October 2026 may exist that are not yet publicly discoverable.
- **Legal Non-Opinion:** This search log documents technical research and does not constitute a formal legal opinion on novelty, non-obviousness, patentability, or freedom-to-operate.

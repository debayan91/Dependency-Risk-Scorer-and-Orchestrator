# Open Questions and Patentability Considerations

**Invention:** Deterministic Multi-Vector Software Dependency Risk Assessment System with Critical Threat Override and Resilient Local Caching  
**Inventor / Source:** Debayan Dutta (Registration No: 23BCE0815)  
**Date:** October 2026  

---

## 1. Questions for the Inventor

1. **Date and Scope of Public Disclosures:**
   - *Issue:* Has the repository code, README, project report (`report.md`, `report2.md`), or research paper draft been made publicly available on GitHub, arXiv, conference presentations, institutional repositories, or external websites prior to filing?
   - *Why it matters:* In many jurisdictions (including EPC member states, China, and India), an unreserved public disclosure prior to filing creates an absolute novelty bar under patent law. The US provides a 1-year inventor grace period (35 U.S.C. § 102(b)), but relying on grace periods limits international filing rights.
2. **Catalog Scaling and Dynamic Baseline Ingestion:**
   - *Issue:* The prototype relies on a static in-memory catalog (`POPULAR_PACKAGES`) containing 55 PyPI, 50 npm, and 12 Maven packages. Has a dynamic registry download crawling pipeline or automated top-$N$ synchronization mechanism been implemented or tested?
   - *Why it matters:* Explaining how the baseline updates dynamically broadens the defensible scope of dependent claims beyond static lists.
3. **Hardware / Deployment Specifics:**
   - *Issue:* Are there specific client-server distributed arrangements, hardware appliance embodiments, or edge gateway deployments envisioned beyond the local CLI and FastAPI server?
4. **Inventorship Confirmation:**
   - *Issue:* Confirm whether Debayan Dutta is the sole inventor or if project supervisors, academic collaborators, or co-authors contributed to the conception of the Critical Threat Override rule or caching architecture.

---

## 2. Questions for the Qualified Patent Professional

1. **Patent-Eligibility of Algorithmic / Mathematical Rules (35 U.S.C. § 101 / EPC Art. 52):**
   - *Analysis:* The Critical Threat Override Shield and compound CVSS scoring rely on mathematical and logic formulations. To satisfy the *Alice/Mayo* framework in the US or European technical effect doctrines, the disclosure must emphasize the concrete technological improvement: preventing automated CI/CD pipeline crashes, mitigating network rate-limiting failures, and stopping malicious software deployment at the OS/process level via automated exit code policy gates.
2. **Prior-Art Boundary on Typosquatting:**
   - *Analysis:* Prior patents (e.g., US Patent 10,812,504 by Snyk, US Patent 11,438,367 by Microsoft, US Patent 10,652,267 by Phylum) address aspects of package dependency security and lookalike package detection. The patent attorney should evaluate how narrowly the claims should tie the string distance metrics to the multi-vector override engine and embedded cache.
3. **Formulation of Independent Claims:**
   - *Recommendation:* Draft independent claims directed to:
     - A computer-implemented method for automated software dependency risk scoring in a continuous integration environment.
     - A system / computing apparatus comprising memory and processors configured to execute the multi-vector pipeline and non-linear threat escalation.
     - A non-transitory computer-readable storage medium storing executable instructions.

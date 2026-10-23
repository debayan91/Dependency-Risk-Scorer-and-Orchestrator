---
name: patent-invention-disclosure
description: Prepare a fact-grounded patent invention disclosure from a repository, technical notes, diagrams, test results, and inventor-provided information. Research patents and publications, compare prior art, describe the technical gap and embodiments, report only verified validation results, and produce an editable, single-column document using Times New Roman 9 pt under exactly nine prescribed headings.
---

# Patent Invention Disclosure Workflow

## Objective

Prepare a technically precise, evidence-grounded invention disclosure for review by the inventor and a qualified patent professional. The document must explain the invention, position it against relevant prior patents and publications, describe how it works, report actual validation, and identify aspects that may warrant protection.

The primary document must use **exactly the nine required headings listed below, in the exact order and wording provided**. Do not add a cover page, abstract, table of contents, standalone references section, appendix heading, or any tenth section. Supporting research notes and audit files may be created separately and must not become additional sections of the primary document.

This workflow supports technical drafting and prior-art research. It is not a legal opinion, a patentability guarantee, a freedom-to-operate analysis, or a substitute for review by a qualified patent professional. Do not represent the document as filing-ready or compliant with a particular patent office unless the applicable requirements have actually been checked.

## Required headings — reproduce verbatim

1. `1. Title of the invention:`
2. `2. Field /Area of invention:`
3. `3. Prior Patents and Publications from literature (provide a table summarizing the prior art)`
4. `4. Summary and background of the invention (Address the gap / Novelty)`
5. `5. Objective(s) of Invention`
6. `6. Working principle of the invent (in brief)`
7. `7. Description of the invention in detail (Include drawing and or photograph as needed)`
8. `8. Experimental validation results:`
9. `9. What aspect(s) of the invention need(s) protection?`

Do not silently correct, shorten, rename, reorder, or replace these headings, including the wording `invent` in heading 6. The main document may contain paragraphs, enumerated steps, tables, equations, and figure captions within these sections, but must not introduce additional section headings. Minor inline labels may be used sparingly inside a section only when necessary to make a technical description intelligible; do not format them as new document sections.

## Required output and document formatting

Create the primary document in an editable Word-compatible format and preserve a source copy:

- `patent/patent_disclosure.docx` — primary editable document.
- `patent/patent_disclosure.md` — source text, preserving the exact nine headings and substantive content.
- `patent/patent_disclosure.pdf` — visual review copy, only if conversion succeeds and the rendered file is inspected.
- `patent/figures/` — original, editable or reproducible drawings/diagrams created for this disclosure.
- `patent/prior_art_search_log.md` — search terms, databases, dates, and search limitations.
- `patent/evidence_ledger.md` — traceability from important statements to source code, inventor-supplied information, tests, measurements, or external references.
- `patent/open_questions.md` — missing facts the inventor or patent professional needs to resolve.
- `patent/audit_report.md` — final content, evidence, formatting, build, and uncertainty audit.

Do not overwrite an existing `patent/` directory or any files within it until you have inspected them. Preserve useful existing material and create versioned or non-conflicting output names where needed.

### Strict formatting specification

The primary DOCX and any PDF generated from it must follow all of these constraints:

- **Font:** Times New Roman throughout.
- **Font size:** exactly **9 pt for all document text**, including section headings, body text, table contents, figure captions, headers, footers, notes, labels, and any displayed references. Use bold and/or underline to distinguish headings if needed; do not increase font size.
- **Layout:** strictly **single-column** on every page. Do not use newspaper columns, sidebars, multi-column sections, or text boxes arranged as a second column.
- Use portrait pages and A4 paper by default unless an existing required institutional template specifies a different page size.
- Use consistent, readable margins and paragraph spacing. Do not shrink the font below 9 pt to force a table or figure to fit; instead wrap text, adjust column widths, move the table/figure, or simplify its presentation without removing material information.
- Tables are allowed inside section 3 and other relevant sections. They must remain inside the page's text area, use 9 pt Times New Roman, wrap content, and not make the page into a multi-column layout. A table with multiple cells does not count as a multi-column page layout.
- All figures must be sized to fit within the single text column and have legible labels. Use 9 pt Times New Roman for text labels when they are generated as part of a figure, to the extent the toolchain permits.
- Do not add a decorative title page. The title of the invention belongs under heading 1.
- Set font properties explicitly in all relevant document styles and runs, including table cells, captions, headers, and footers; do not rely only on a default theme.
- Inspect the generated DOCX/PDF or rendered pages to verify font consistency, page layout, table wrapping, figure legibility, and the absence of unintended columns. If exact font rendering cannot be confirmed in the environment, disclose that limitation in `patent/audit_report.md`.

Use `python-docx` or an equivalent DOCX authoring tool when available. If DOCX generation is unavailable, create a compilable source that enforces the same formatting. For a LaTeX fallback, use a 9 pt-capable class such as `extarticle`, set Times New Roman with `fontspec`, compile with XeLaTeX or LuaLaTeX, and retain a single-column page layout. Do not claim Times New Roman is in use if the font is missing or substituted without disclosure. Follow the user's requested 9 pt formatting, but separately flag that formal filing requirements can vary by jurisdiction and must be checked before submission.

## Non-negotiable evidence and integrity rules

1. **Inspect source material before drafting.** Examine the actual repository implementation, architecture, interfaces, configuration, tests, experiment scripts, outputs, diagrams, technical notes, and inventor-supplied facts where available. Do not base the description only on a README or a high-level product pitch.
2. **Do not invent technical facts.** Never fabricate components, operating steps, formulas, design dimensions, data sources, inventors, dates, results, test environments, performance numbers, baselines, citations, patent identifiers, assignees, priority dates, legal status, or details about ownership.
3. **Keep evidence classes distinct.** Track whether each key statement is `IMPLEMENTED` (confirmed from code/design artifacts), `INVENTOR-SUPPLIED`, `MEASURED` (supported by actual results), `CITED` (supported by a verified external source), `INFERRED` (clearly qualified interpretation), or `UNKNOWN` (not established by available evidence).
4. **No unsupported novelty claims.** Describe a technically specific difference from identified prior art, but do not state that an invention is novel, non-obvious, patentable, or globally first unless the relevant legal and factual assessment supports that conclusion. Prefer cautious language such as “the reviewed documents did not disclose the same combination under the searched terms” and explain the search scope and limitations.
5. **Do not convert routine implementation choices into a purported invention without analysis.** Identify the technical problem and the specific mechanism or combination said to address it. Separate the invention's potentially distinguishing features from standard components, known techniques, and optional features.
6. **No unverified citations.** Verify the title, inventor/author, publication or patent number, date, assignee or venue, and source link against a reliable record. Check the relevant portion of the source rather than relying only on a search snippet. Never fabricate BibTeX or patent records.
7. **Report experiments honestly.** A test passing is not automatically evidence of performance advantage. Do not invent measured results, claim unrun experiments were performed, or use proposed validation as if it were completed.
8. **Preserve the disclosed invention.** Do not refactor or alter the product implementation to improve the disclosure. Do not introduce unsupported features as if already implemented. Suggested extensions must be explicitly marked as possible embodiments or open questions and included only when technically supported or confirmed by the inventor.
9. **Respect confidentiality.** Exclude credentials, tokens, private keys, personal data, proprietary information unrelated to the invention, and sensitive system details that are not needed for disclosure. Do not reproduce secrets found in source files.
10. **Preserve prior work and Git state.** Do not delete files, reset the repository, rewrite history, push commits, or make destructive changes. Do not commit unless explicitly instructed.
11. **Track disclosure timing.** Where known, record relevant dates of demonstrations, publication, sales, public use, presentations, or other public disclosures in the separate open-questions/evidence notes. Never assume a disclosure is harmless or legally irrelevant; flag timing for professional review.
12. **Do not claim completion merely because a document was generated.** Confirm the required sections, evidence checks, formatting constraints, and output files individually.

## Required workflow

### Stage 1 — Identify the invention and inventory available evidence

- Inspect the repository tree, project-specific instructions, README, relevant source files, architecture, APIs, data flow, tests, benchmark scripts, test outputs, existing documentation, prior diagrams, related papers/patents already mentioned, and Git status.
- Exclude generated dependencies and build artifacts from broad scans, but inspect directories that may contain useful evidence before excluding them.
- Identify what the system demonstrably does, what is claimed but unverified, which design features are central, which are routine, and which facts are missing.
- Create `patent/evidence_ledger.md` with: statement or candidate feature; evidence class; exact file paths/symbols/line ranges or source reference; what the evidence establishes; confidence; and unresolved issue.
- Create `patent/open_questions.md` early. Continue without asking routine questions; distinguish missing inventor-confirmation items from information recoverable through inspection or research.

### Stage 2 — Reconstruct the technical mechanism

- Trace the invention from inputs through components, processing/decision steps, state changes, interfaces, and outputs.
- Identify the technical problem being solved, the mechanism used, relevant preconditions, boundaries, failure modes, dependencies, and alternative embodiments that are actually disclosed or reasonably supported.
- Separate the implemented embodiment from proposed variants. Do not assert an alternative implementation has been built or tested unless evidence shows it.
- Record important technical details in the evidence ledger before using them in the primary document.

### Stage 3 — Conduct prior-art research

Use available web, patent-search, and scholarly-search tools. Search broadly with multiple query formulations derived from:

- the technical problem and intended application;
- the core mechanism, algorithm, system architecture, or physical arrangement;
- synonyms, abbreviations, and alternative terminology;
- important inputs, outputs, components, operating steps, and combinations;
- the claimed differentiator and adjacent technical domains;
- relevant patent classifications and citations of the closest references, where available.

Use patent-office or established patent sources when available, such as WIPO PATENTSCOPE, EPO Espacenet, USPTO resources, the relevant national patent office, and Google Patents as a discovery/indexing aid. Use primary scholarly publications, publishers, conference proceedings, institutional repositories, and DOI/arXiv records for publications. Search official sources first when a source's legal status or bibliographic accuracy matters.

For every selected item, verify as many of the following as applicable: title; inventors/authors; publication/patent/application number; publication date; priority/application date when listed; assignee/applicant; jurisdiction or venue; source URL/DOI; relevant abstract, claims, figures, or passages; and current status only where a reliable status source is available. Distinguish publication date from priority date. Patent status can be jurisdiction- and family-specific; do not describe a patent as active, expired, granted, or abandoned without a dated and suitable source.

Create `patent/prior_art_search_log.md` documenting databases/tools used, search date, exact representative queries, useful classification/citation-following steps, sources screened, closest items identified, and known search limitations. Never describe a search as exhaustive if the sources and scope do not support that description. If search tools or databases are unavailable, document the limitation and do not fabricate search results.

#### Prior-art summary table requirements

Inside heading 3 of the main document, include a table of the closest relevant, verified patents and publications. Select references for technical relevance, not merely quantity. Use clear columns such as:

- Type and verified identifier;
- Title, inventor/author, assignee or venue, and date;
- Relevant disclosed mechanism or teaching;
- Relationship to this invention / apparent difference;
- Source link and verification note.

Adapt the columns to fit the page while keeping all text Times New Roman 9 pt and the document single-column. If a legal/status field is included, state jurisdiction and verification date; omit the field when reliable status evidence is unavailable. Cite the source within the table, for example using compact IDs such as `[P1]` and `[L1]`, and resolve each ID to a complete verified record in the same table or its source cell. Do not place a separate references heading after section 9. Include only prior art that was actually checked, and represent conflicting or uncertain information accurately.

### Stage 4 — Assess the gap without overstating novelty

- Compare the invention with the closest references along comparable dimensions: problem, inputs, mechanism, system components, process steps, outputs, assumptions, effects, and validation.
- Distinguish: (a) features clearly present in prior art, (b) features not located in the reviewed sources, (c) the specific combination believed to be different, and (d) questions requiring a patent professional's legal assessment.
- Explain why any difference is technically meaningful only where evidence supports the explanation.
- Do not confuse “not found in this search” with “does not exist.” Do not confuse a technical difference with legal novelty or non-obviousness.
- Ensure each proposed contribution is supported by the described mechanism and has a basis in the disclosure; flag inventorship, ownership, or priority questions rather than deciding them yourself.

### Stage 5 — Draft content under the nine required headings

Write the main document with these exact headings and content expectations:

**Heading 1 — Title of the invention:** Use a precise, neutral title. Avoid marketing terms, absolute superiority claims, and unnecessarily broad labels. Do not add a subtitle as another heading.

**Heading 2 — Field /Area of invention:** State the technical field and, if supported, the narrower technical subfield. Avoid claiming an entire broad field as the invention.

**Heading 3 — Prior Patents and Publications from literature (provide a table summarizing the prior art):** Include the prior-art summary table described above. Follow it with concise prose, still within this section, identifying the closest references and their relevant teachings. Do not assert that a reference lacks a feature until the relevant source has been checked.

**Heading 4 — Summary and background of the invention (Address the gap / Novelty):** Explain the context and technical problem, the limitations relevant to the closest prior art, the disclosed solution's key mechanism, and the specific differences that appear supported. Distinguish observed differences from a legal conclusion about novelty. Avoid background claims that are unsupported or unnecessarily disparaging of existing systems.

**Heading 5 — Objective(s) of Invention:** List concise technical objectives derived from the actual disclosure. Separate the main objective from secondary objectives when useful. Do not promise objectives such as lower latency, higher accuracy, lower cost, greater security, or reduced energy unless the design and evidence support them; otherwise frame them as intended goals, not proven outcomes.

**Heading 6 — Working principle of the invent (in brief):** Give a short, ordered end-to-end explanation. Cover the starting input or condition, core operations, important decisions/transitions, and output/result. Define essential technical terms. Ensure the sequence agrees with the implementation and the detailed description.

**Heading 7 — Description of the invention in detail (Include drawing and or photograph as needed):** Provide enough technical detail for a technically competent reader to understand and reproduce the disclosed embodiment, subject to the evidence available. Describe components/modules, interfaces, data flow or physical arrangement, process steps, relevant data structures/formulas/parameters, interactions, failure handling, and supported variants. Define any reference numerals and use them consistently across the text and figures. Place original drawings or diagrams in this section and give them figure numbers and captions; refer to each figure in the text. Prefer original block diagrams, flowcharts, component schematics, or sequence diagrams grounded in the actual system. Do not use decorative images or screenshots of source code as substitutes for technical drawings. Do not include third-party images without a clear need and appropriate permission. If a figure is conceptual, label it as conceptual. If no drawing can be supported, do not invent one; state the limitation and list what drawing needs remain in `open_questions.md`.

**Heading 8 — Experimental validation results:** State the validation actually performed and evidence available. Where results exist, identify environment/hardware, software versions, dataset or sample source, sample count, baseline and comparison conditions, parameter settings, metrics, command or procedure, repeats/uncertainty where applicable, raw result locations, numerical outcomes, and limitations. Use a table for results when it improves clarity. Distinguish functional tests, simulations, demonstrations, and controlled experiments. Report failures or mixed results where relevant. If no experimental or measured results are available, explicitly state that no validated experimental results were found in the examined materials; do not fabricate values. A proposed test plan belongs in a clearly labelled future-validation paragraph in this section only if useful, and must never be described as a completed result. Also capture a more detailed proposed protocol in `open_questions.md` or the audit files.

**Heading 9 — What aspect(s) of the invention need(s) protection?:** Identify technically specific candidates for review, such as the core mechanism, a particular combination of steps/components, an interaction or control flow, a data transformation, a physical arrangement, or a supported variant. For each candidate, state the technical feature, the disclosed support, the distinction to relevant reviewed prior art, and what needs confirmation. Prioritize the apparent core concept and then supported secondary variations. Do not present the list as final patent claims or conclude that any feature is legally protectable. Do not add a separate “claims” section because the requested document must have exactly nine headings.

### Stage 6 — Create drawings and supporting evidence

- Generate figures only from verified code, architecture, inventor-provided diagrams, or explicitly labelled conceptual explanations.
- Use stable figure numbers and reference numerals; make sure every numbered element described in the text appears in the relevant figure and vice versa.
- Save reproducible diagram source when practical, as well as rendered image assets under `patent/figures/`.
- Check that all figures are legible at the actual 9 pt document scale and fit within the text column.
- Keep detailed source URLs, query history, long technical traces, and unresolved issues in separate supporting files, not as extra sections in the primary document.

### Stage 7 — Produce and format the primary document

- Build the content first in `patent/patent_disclosure.md`, using exactly the nine headings and no other headings.
- Generate `patent/patent_disclosure.docx` from that source or from a structured representation of the same text. Use one continuous page column and apply Times New Roman 9 pt to every text-bearing component, including table cells and captions.
- Where feasible, set document-wide styles explicitly and inspect raw style/run properties to catch inherited font substitutions or non-9 pt text.
- Preserve the exact heading text, order, and numbering. Do not add a separate cover page or an automatic table of contents.
- If creating a PDF, convert from the validated DOCX or compile the formatting-controlled LaTeX source. Verify that the PDF exists and inspect all pages, not only the first one.
- Never call a PDF a successful output if conversion failed or its final state is unverified.

### Stage 8 — Independent audit

Review the primary document as a skeptical technical and prior-art reviewer. At minimum, verify:

- The body contains the exact nine specified headings, in exact order, with no extra section headings.
- All technical statements match source evidence or are explicitly qualified.
- The prior-art table only contains references that were verified and includes meaningful technical comparisons.
- The gap/novelty language is cautious and does not purport to make a legal finding.
- No fabricated identifiers, inventors, dates, citations, performance values, or experiments appear.
- Working principle and detailed description describe the same mechanism.
- Figure numbers, reference numerals, captions, and in-text references are consistent.
- Experimental validation is separated from proposed validation; missing results are disclosed.
- Protection candidates are supported by the text and are not presented as final legal claims.
- Confidential or unrelated sensitive information has not leaked into the document.
- Every page is single-column and all text is Times New Roman 9 pt, including tables, labels, and captions to the extent verifiable.
- Tables/figures are not clipped; page breaks and line wrapping are acceptable; no content is cut off.
- The DOCX/PDF files open and the PDF visually matches the intended layout.

Record the audit result in `patent/audit_report.md`, including checks performed, the exact files examined, relevant build/inspection commands and outcomes, failed checks, formatting uncertainties, search limitations, and remaining inventor/legal-review questions. Do not silently patch evidence gaps with assumptions during the audit.

## Completion criteria

Do not declare completion until:

1. Repository/material inspection has been performed to the extent the available project permits.
2. The evidence ledger, prior-art search log, open-questions file, and audit report exist.
3. The primary disclosure uses exactly the nine required headings and no extra sections.
4. The editable DOCX exists, uses Times New Roman 9 pt, and is single-column, or the precise blocker is documented.
5. Prior-art entries have been verified as far as the available sources permit, with search limits disclosed.
6. Experimental results are supported by actual evidence or explicitly identified as unavailable.
7. Figures and tables are consistent, legible, and traceable to the source material.
8. A PDF is delivered only if successfully generated and inspected; otherwise state why it could not be generated.
9. The final response summarizes deliverables, prior-art research coverage, what validation is evidenced, formatting/build checks, and open questions. Never claim “patentable,” “guaranteed novel,” “filing-ready,” or “publication-ready” without a valid basis and appropriate review.

## Working style

Work autonomously through the stages that can be completed with available information and tools. Do not stop after planning or outlining. Prefer short, precise technical prose. Use source paths and verified citations rather than promotional language. When an essential fact is missing, continue with the safest evidence-based wording and record the missing fact in `patent/open_questions.md`; do not ask the user to repeat information already present in the repository or conversation. Keep a persistent progress note if execution may span multiple agent turns.

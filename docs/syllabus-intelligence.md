# Syllabus Intelligence Engine — Deferred Research Specification

**Status:** Deferred. Not present in the active StudySprint interface. Do not implement until PYQ Intelligence has a validated V1 and real student usage.

## Objective
Convert an official syllabus into a structured, editable and traceable curriculum graph. Identify units, topics, subtopics, learning outcomes, contact hours and assessment weightage only when explicitly present. Preserve source-page and text-span references. Never invent missing topics or claim complete coverage after partial extraction.

## Inputs
Support PDF, DOCX, TXT and HTML. Capture user-confirmed institution, program, course, semester, syllabus version, academic year, language and source file. Store file hash, extraction method, page count and warnings.

## Proposed algorithm
1. **Extraction:** text-native PDF/DOCX parsers first; OCR as a separate capability; preserve page number, hierarchy, tables and reading order; detect missing/duplicated pages.
2. **Structure detection:** combine layout/typography, Unit/Module/Chapter headings, numbering hierarchy and table structure. Classify blocks as heading, topic, outcome, reference, note or assessment. Route uncertain blocks to review.
3. **Topic hierarchy:** represent course → unit/module → topic → subtopic. Link learning outcomes and assessment components to topics. Do not assume every numbered paragraph is a topic.
4. **Semantic normalization:** preserve original wording; suggest canonical labels without replacing source text; merge synonyms only with evidence and approval.
5. **Coverage and traceability:** show extracted/reviewed/unresolved sections; support edits, split/merge, reparenting and exclusions; every node points to a source page/section.

## Candidate algorithm stack
- Layout-aware extraction and deterministic heading rules.
- Document-block classifier evaluated on labelled syllabus blocks.
- Structured LLM extraction into a strict schema requiring source spans.
- Deterministic hierarchy, duplicate, page-coverage and schema validation.
- Human review for low-confidence structures.

LLMs may propose structure but cannot silently change source text or fabricate content. Validate every output against schema and source spans.

## Evaluation
Build a labelled dataset across institutions, languages and document styles. Measure heading and topic extraction precision/recall/F1, hierarchy accuracy, source traceability, table extraction accuracy, correction rate, page coverage and abstention quality. Split by institution and syllabus version to prevent leakage.

## Future API boundary
- POST /api/v1/syllabi
- GET /api/v1/syllabi/{syllabus_id}
- GET /api/v1/syllabi/{syllabus_id}/structure
- PATCH /api/v1/syllabus-nodes/{node_id}
- POST /api/v1/syllabus-analyses

Keep this a separate bounded module. Any future mapping from PYQ concepts to syllabus nodes must show evidence for both sides.

## Reactivation gate
Reactivate only after PYQ V1 passes its benchmark and source-evidence release gates, students validate the second problem, a legally usable labelled dataset exists, and scope/quality targets are agreed. Until then, this is a parked research specification.

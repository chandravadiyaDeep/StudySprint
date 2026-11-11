# PYQ Intelligence Engine — Research & Engineering Specification

**Status:** Active engine. **Rule:** Evidence before interpretation. Never fabricate topics, frequencies, marks or predictions.

## Objective and product boundary
Analyze a confirmed set of previous-year papers from the same course, subject, institution/board and exam family. Report extracted questions, exact repeats, near-duplicates and related concepts as separate categories; recurrence across distinct papers and confirmed years; marks only when explicitly and reliably extracted; evidence quality and extraction coverage. Historical recurrence is descriptive evidence, never a probability of future appearance.

V1 excludes syllabus parsing, syllabus coverage, invented topic names, invented marks, exam predictions, unsupported “most important” claims and custom model training before a labelled benchmark exists.

## Input contract
Each paper retains a stable ID, original filename, SHA-256 hash, user-confirmed subject/course, institution/board, exam type and year, page count, extraction method and warnings. Never silently infer a year from a filename. Preserve page-level text and source coordinates. Do not compare unrelated subjects or exam families without a visible warning.

## Engine pipeline

### A. Ingestion
Validate type, size and page count. Extract page-level text in reading order. Detect scanned/image-only pages. OCR is a separately versioned capability. Never silently drop pages or return a complete-looking report after partial extraction.

### B. Question segmentation
Use layout-aware PDF blocks first, explicit numbering patterns second, section headers and marks as supporting signals, and paragraph fallback only when needed. Preserve subparts as children of parent questions. Provide a correction interface to split, merge, delete and renumber candidates. Store raw text, normalized text, page range, question number and segmentation confidence.

### C. Normalization and duplicate detection
Normalize Unicode and whitespace conservatively. Preserve mathematical symbols, code, formulae and meaningful numbers. Detect exact duplicates using normalized hashes. Detect near-duplicates separately and never irreversibly merge them. Keep original text available.

### D. Similarity and pattern grouping
Evaluate a layered approach:
1. Baseline: TF-IDF word and character n-grams with cosine similarity.
2. Semantic candidate retrieval: versioned sentence embeddings.
3. Optional reranking: cross-encoder or LLM pairwise judgement for ambiguous pairs.
4. Clustering: constrained agglomerative or graph clustering, with calibrated thresholds and cluster-diameter checks.
5. Human review: same concept, different, or uncertain.

Keep labels distinct: exact repeat, near duplicate, same concept, related but distinct, unresolved. Semantic similarity is not proof of question equivalence.

### E. Concept naming
For V1, use a representative question as the cluster label. An LLM may later propose a short concept label, but it must be marked as generated, retain source examples, cite evidence and allow correction. If evidence is weak, show “Unclassified question group”.

### F. Frequency and evidence
Calculate descriptive values only: question occurrence count, distinct-paper count, distinct confirmed-year count, first/last confirmed year, and marks statistics only when extraction is validated. Missing years are not zero-frequency years. Every result links to source paper, page, question number and extracted text. Never call occurrence count divided by papers a probability.

### G. Abstention
Return insufficient evidence when too few papers are supplied, extraction coverage is low, segmentation is uncertain, a cluster is unstable, papers mix subjects/exam types, or a claim cannot cite its source question. Keep separate confidence values for extraction, segmentation, similarity and label generation.

## Baseline and algorithm priorities
The current website baseline uses question-number segmentation with paragraph fallback, normalized token sets, Jaccard similarity and source-paper examples. It is transparent but can miss paraphrases, split multi-part questions and falsely merge questions sharing vocabulary. It is not semantic AI.

Next candidates: TF-IDF word/character n-gram cosine similarity; sentence-transformer embeddings; embedding retrieval plus cross-encoder reranking; LLM-assisted concept labels with strict source-grounded output. Select from benchmark results, not demos.

## Proposed backend/API architecture
GitHub Pages must never contain private API keys. Suggested Python/FastAPI endpoints:
- POST /api/v1/papers — upload and create ingestion job.
- GET /api/v1/papers/{paper_id} — metadata and extraction status.
- GET /api/v1/papers/{paper_id}/questions — extracted candidates.
- POST /api/v1/analyses — analyze a confirmed paper set and algorithm version.
- GET /api/v1/analyses/{analysis_id} — report and status.
- GET /api/v1/analyses/{analysis_id}/evidence — source evidence.
- PATCH /api/v1/questions/{question_id} — human correction.
- POST /api/v1/feedback — false-merge, missed-match and extraction feedback.

Architecture: static frontend; FastAPI backend; background queue for OCR/embeddings; object storage for originals; relational DB for metadata/results; vector index only when justified; provider-neutral model adapter; server-side environment variables for keys. Record request ID, algorithm/model version, latency, cost, errors and stage confidence.

Do not send full papers to third-party models by default. Obtain consent and provide retention/deletion controls before external model processing.

## Evaluation and release gates
Build a human-labelled benchmark from legally usable papers. Label question boundaries, subparts, exact duplicates, near duplicates, same-concept pairs, distinct pairs, marks and page locations. Split by paper/year, not random question rows.

Measure extraction character/page coverage and OCR error; segmentation boundary precision/recall/F1; pairwise similarity precision/recall/F1 and precision at K; clustering B-cubed F1 or adjusted Rand index and cluster purity; evidence/page correctness and unsupported-claim rate; user correction rate, time saved and trust.

Prioritize precision for student-facing claims. A missed match is preferable to a false “frequently repeated” claim. Every displayed claim must link to evidence; extraction coverage must be visible; no prediction language; regression tests for every algorithm version.

## Experiment log
For each experiment record ID/date, dataset version and paper count, algorithm/model version, parameters, labelled metrics, false merges, missed matches, latency, cost, decision and rationale. Never overwrite prior results.

## Implementation status
- [x] PYQ-first UI direction; syllabus removed from active UI.
- [x] Browser-only question segmentation and lexical grouping baseline.
- [x] Pattern examples and source paper names displayed.
- [ ] Page-aware PDF extraction and OCR.
- [ ] Human question-boundary correction.
- [ ] TF-IDF baseline and labelled benchmark.
- [ ] Embeddings and calibrated semantic grouping.
- [ ] Backend API, authentication, storage and job queue.
- [ ] Marks extraction and multi-institution validation.

**Current truth:** the browser implementation is a prototype baseline, not an API-connected reasoning engine. Do not market it as one until the evaluation and release gates are met.

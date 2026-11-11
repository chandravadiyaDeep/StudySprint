# StudySprint — PYQ Intelligence Engine (V1)

**Status:** Active V1 engine specification  
**Scope:** Previous-year question papers only. Syllabus Intelligence is deliberately excluded from the V1 product UI and workflow. Its future research notes are kept separately in `SYLLABUS_INTELLIGENCE.md`.

## 1. Product promise

Turn a student's uploaded previous-year question papers into a traceable evidence report that answers:

1. What questions were extracted from each paper?
2. Which academic topics and subtopics do those questions test?
3. Which topics recur across the uploaded papers?
4. What exact questions support each topic's frequency?
5. What kinds of questions are repeatedly asked (definition, explanation, comparison, derivation, numerical, coding, proof, etc.)?
6. How should a student understand and practise the concepts behind those questions?

The engine must describe **the uploaded dataset**, not claim to predict a future examination.

## 2. Truth and evidence contract

- A paper counts only if it was actually uploaded and successfully parsed.
- A question occurrence is counted from an extracted question record, never from an LLM-generated summary.
- Topic labels, concept explanations and question-type classifications are AI interpretations and must be labelled as such.
- Every reported count must link to its source question records and source paper names.
- Do not silently discard uncertain or malformed extraction. Report extraction warnings and let the user inspect the extracted text.
- Do not claim that a topic is "important", "sure-shot", or "likely to appear" from frequency alone.
- Synthetic examples must always be labelled synthetic and must never enter real-user statistics.
- If the evidence is insufficient, say so. Never fill gaps with invented questions, papers, dates or counts.

## 3. V1 processing architecture

### Stage A — Ingestion and provenance
1. Accept PDF, TXT and MD documents.
2. Extract selectable PDF text with PDF.js in the browser for the first prototype; scanned PDFs require a later OCR stage.
3. Send extracted text and file names to the FastAPI backend over HTTPS.
4. Validate file count, per-paper text length, total request size and allowed file extensions.
5. Assign a stable request-local paper ID and retain source file name and extraction warnings.

### Stage B — Deterministic question segmentation
- Normalize line endings, whitespace and Unicode punctuation without changing the stored original text.
- Detect common numbering patterns: `Q1`, `1.`, `1)`, `(a)`, section labels and marks indicators.
- Split only when a defensible question boundary exists.
- Keep original question text verbatim (trimmed only at edges).
- Flag low-confidence segments for manual review.
- Do not treat every paragraph or heading as a question.

### Stage C — Gemini reasoning
Use the official Google Gen AI Python SDK from the backend. V1 default model is configurable through `GEMINI_MODEL`; the current initial default is `gemini-3.8-flash`. Model IDs can change, so keep this setting outside source code.

Gemini receives the segmented question records, their IDs and paper names. It returns structured JSON for each question:
- canonical topic and optional subtopic
- concise concept being tested
- question intent/type
- difficulty estimate with rationale
- classification confidence
- related question IDs, only when the relationship is defensible

Gemini is an interpretation layer. It is not allowed to invent or rewrite source question text.

### Stage D — Deterministic aggregation
The backend, not Gemini, calculates:
- total papers parsed
- total question candidates extracted
- questions per canonical topic
- distinct papers containing each topic
- paper coverage percentage
- question-type distribution
- repeated / related question groups

Aggregation uses returned question IDs and validated source records. Topic normalization and clustering rules must be versioned and tested. A topic frequency is a count of classified extracted records, not a probability of appearing in a future exam.

### Stage E — Evidence report
Each topic card must show:
- topic name and AI classification label
- number of extracted question occurrences
- number and names of distinct source papers
- coverage percentage with denominator (e.g. 3 of 5 uploaded papers)
- supporting question text and source paper for every occurrence
- AI explanation of the concept and suggested study direction
- confidence / review warning where relevant

## 4. General algorithms — V1 baseline

| Problem | Initial algorithm | Why it is the baseline | Known limitation |
|---|---|---|---|
| PDF text extraction | PDF.js text layer | Runs in browser; no PDF upload storage needed | No OCR for scanned pages; reading order can be imperfect |
| Text normalization | Unicode NFKC + whitespace normalization | Stable comparison without changing displayed source text | Must preserve math and symbols carefully |
| Question segmentation | Rule-based boundary detection | Deterministic, testable, cheap | Different universities format papers differently |
| Question understanding | Gemini structured classification | Handles paraphrases and conceptual interpretation better than keyword matching | Can misclassify; requires validation |
| Topic frequency | Python aggregation over classified question IDs | Exact, reproducible counts | Depends on segmentation and topic consistency |
| Similar-question grouping | Gemini relation suggestions + deterministic validation | Finds paraphrased questions | Must not merge merely related but distinct questions |
| Topic ranking | Sort by distinct-paper coverage, then occurrence count | Exposes recurring evidence | Not an exam prediction or guarantee |
| Study explanation | Gemini grounded only in extracted question set | Gives a student-friendly conceptual explanation | Explanation quality must be tested against expert review |

## 5. Confidence and abstention

- High confidence: clear question text and a specific canonical topic.
- Medium confidence: topic is plausible but wording is broad or context is missing.
- Low confidence: incomplete extraction, ambiguous question, or multiple plausible topics.
- Low-confidence records must remain visible and excluded from strong claims until reviewed.
- Confidence is a model estimate, not a calibrated probability, until evaluated on a labelled dataset.

## 6. Evaluation plan

Create a labelled benchmark from real papers with permission:
- manually verified question boundaries
- canonical topic and subtopic
- question type
- repeated-question relationships
- paper metadata

Track:
- question extraction precision / recall
- topic classification accuracy and macro-F1
- question-type accuracy
- related-question precision / recall
- exact agreement of deterministic topic counts against manually labelled records
- hallucination rate (AI claims without source question IDs)
- latency and cost per paper set

Do not optimize a metric in isolation. A lower coverage report with fewer false positives is preferable to a confident but misleading report.

## 7. Testing priorities

1. Different PDF layouts and numbering schemes.
2. Multi-part questions and sub-questions.
3. Mathematical notation, code blocks, tables and diagrams.
4. Paraphrased questions testing the same concept.
5. Similar wording testing different concepts.
6. Papers from different years and different paper versions.
7. Poor extraction and scanned PDFs.
8. Mixed-language papers (later phase).

## 8. Versioning and change control

Every run should record:
- engine version
- segmentation version
- prompt version
- Gemini model ID
- timestamp
- paper names and content hashes (hashing is a later backend enhancement)
- warnings and excluded records

Change one algorithm at a time against the benchmark. Record the reason, expected improvement, measured result and regressions before promoting it.

## 9. Security and operational guardrails

- The API key is loaded only by the backend process.
- The API applies a basic per-IP request limit; this is not a substitute for authentication or account quotas.
- Keep provider spend limits and monitoring enabled. Do not expose an unrestricted public endpoint before authentication and abuse controls are ready.
- CORS is a browser policy, not an API access-control mechanism.

## 10. V1 exclusions

- Syllabus ingestion and syllabus-topic mapping
- Exam prediction or guaranteed question forecasts
- OCR for scanned PDFs
- Cross-user paper sharing or cloud history
- Fine-tuned models and custom embeddings
- Automatic web scraping of question papers

## 10. Acceptance criteria

A report is acceptable only when a user can open every topic frequency and inspect the exact source questions that contributed to it. Counts must be reproducible from the stored extracted-question records. If Gemini is unavailable, the API must return a clear error rather than silently falling back to a fake AI report.

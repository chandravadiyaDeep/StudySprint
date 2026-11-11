# StudySprint — PYQ Intelligence Engine

**Document status:** Initial engineering specification (v0.1)  
**Implementation status:** Proposed; not yet validated against a labelled multi-year question-paper dataset.  
**Core promise:** Analyse actual previous-year question papers (PYQs), map questions to a reviewed syllabus, and report transparent historical patterns. Never present historical frequency as a guarantee of future exam questions.

---

## 1. Problem and user outcome

Students have multiple previous-year papers and want to know:
- What questions and concepts appeared in each paper.
- Which syllabus topics each question assesses.
- How often a topic appeared, in which years, and in which papers.
- Whether a pattern is stable, increasing, decreasing, or too sparse to interpret.
- Which questions need manual review because the mapping is uncertain.

The engine reports **historical evidence**, not future certainty. It must not claim “sure-shot”, “guaranteed”, “most expected”, or exact future marks.

## 2. Input contract

Initial supported inputs:
- Digital PDF with selectable text.
- TXT and Markdown exports.
- Multiple papers with user-supplied subject, institution, exam/session, and year metadata.

Later:
- Scanned PDFs via OCR.
- DOCX and image inputs.
- University-specific paper templates.

Each paper should store:
- Original filename and SHA-256 hash.
- Subject/course and institution (user-provided or verified).
- Exam/session and year (never guess silently).
- Source page and question number.
- Extraction method and warnings.
- Duplicate/near-duplicate relationships, with review status.

Do not combine papers from different subjects, universities, syllabi, or exam patterns unless the user explicitly chooses to compare them.

## 3. Output contract

Return question-level records plus topic-level aggregation. Suggested shape:

```json
{
  "paper": {
    "filename": "paper-2025.pdf",
    "subject": "Subject name",
    "institution": null,
    "exam_session": "Winter",
    "year": 2025,
    "pages_processed": 6
  },
  "questions": [
    {
      "id": "q1",
      "question_number": "Q1(a)",
      "text": "Verbatim extracted question text",
      "page": 1,
      "marks": null,
      "question_type": "unknown",
      "topic_matches": [
        {
          "syllabus_topic_id": "topic-1",
          "method": "lexical_baseline",
          "score": null,
          "review_status": "needs_review",
          "evidence": ["Matched terms or source excerpt"]
        }
      ]
    }
  ],
  "topic_statistics": []
}
```

The sample is a schema illustration only. Unknown marks, year, and question type remain null/unknown. A similarity score is not a probability that a question will appear in a future exam.

## 4. Proposed algorithm pipeline

### Stage A — Paper ingestion and metadata
1. Validate file and calculate hash.
2. Extract text page-by-page while retaining page markers.
3. Capture user-provided institution, subject, exam session, year, and maximum marks.
4. Detect missing metadata and ask the user; do not infer year from a filename without confirmation.
5. Detect exact duplicate files by hash.

### Stage B — Question segmentation
- Detect question numbers (Q1, 1(a), Section A, etc.), marks patterns, and section headings.
- Use layout/line structure to avoid splitting a question from its subparts.
- Preserve original question text and page references.
- Flag uncertain segmentation for review.
- Keep sub-questions distinct when they test different concepts.

### Stage C — Syllabus alignment
The reviewed Syllabus Intelligence output is the topic catalogue. Each question may map to:
- One topic.
- Multiple topics when genuinely interdisciplinary.
- No confident match (unmapped).

Use a staged retrieval/ranking system:

1. **Lexical baseline:** normalized token overlap and TF-IDF cosine similarity; fast and explainable.
2. **BM25 retrieval:** rank candidate syllabus topics based on question terms and topic descriptions.
3. **Semantic embeddings:** compare question and topic embeddings to retrieve paraphrases; evaluate model choice on local labelled data.
4. **Cross-encoder reranking (optional):** rerank a small candidate set for better relevance.
5. **LLM-assisted explanation (optional):** propose why a question maps to a topic, quoting evidence from the question and syllabus.
6. **Decision threshold + abstention:** if evidence is weak or top candidates are too close, return “needs review” or “unmapped”; do not force a topic assignment.

The first implementation should establish a transparent lexical/BM25 baseline before introducing embeddings or an LLM. More complex does not automatically mean more accurate.

### Stage D — Human-in-the-loop labels
- Show question text, candidate topics, and matching evidence.
- Allow user to accept, change, multi-map, or mark unmapped.
- Store corrected labels for evaluation.
- Do not train or tune on test papers.

### Stage E — Historical statistics
For each topic, calculate:
- Number of distinct papers in which it appeared.
- Total matched question count.
- Years/sessions observed.
- Marks total only where marks were explicitly extracted and verified.
- Recency and time gaps.
- Mapping coverage and uncertainty.

Use distinct-paper frequency as a primary measure so repeated subparts in one paper do not misleadingly count as independent appearances.

Potential descriptive metrics:
- Paper frequency = distinct papers containing a reviewed match / eligible papers processed.
- Question frequency = reviewed matched questions / eligible questions processed.
- Marks share = verified marks mapped to topic / total verified marks in eligible papers.

Always show numerator and denominator, date range, number of papers, and missing-data warnings. Do not mix unknown marks into marks-share calculations.

### Stage F — Trend analysis (descriptive only)
- Show yearly/session counts.
- Compare only comparable exam sessions and syllabus versions.
- Use rolling windows only when enough papers exist.
- Mark sparse data as “insufficient history”.
- Show changes as historical observations, not predictions.

A future ranking can be named “historical revision priority” only if its formula is visible and it clearly says it is not an exam forecast.

## 5. Scoring and recommendation policy

Do not ship a magic “importance score” with hidden weights.

If a composite revision-priority score is later tested, document:
- Each component and formula.
- Normalization method.
- Weights and why they were chosen.
- Minimum sample requirements.
- Sensitivity to changing weights.
- Validation against student/reviewer judgments or learning outcomes.

Until validated, show raw descriptive statistics instead of a composite score. Never convert a similarity score or frequency count into a probability of future appearance.

## 6. Evaluation plan

Build a gold dataset with manually labelled questions and topic mappings. Split train/dev/test by whole paper and, where possible, by year to prevent leakage.

Measure:
- Question segmentation precision, recall, and F1.
- Topic mapping precision, recall, and F1.
- Top-1 and top-3 accuracy on questions with a valid syllabus mapping.
- Coverage versus accuracy at different abstention thresholds.
- Unmapped-question rate.
- Human agreement (e.g., inter-annotator agreement) on ambiguous mappings.
- Duplicate detection precision/recall.
- Marks extraction exact-match accuracy.
- Per-university, per-subject, and per-format performance.

Report confidence intervals where sample sizes allow. Never publish an accuracy percentage without dataset size, label definition, and test split details.

## 7. Initial algorithm choices and priority

| Priority | Method | Purpose | Limitation |
|---|---|---|---|
| P0 | PyMuPDF/pdfplumber | Extract text with page provenance | Scans/layout complexity |
| P0 | Regex + layout-aware segmentation | Identify questions and subparts | Paper formats vary |
| P0 | TF-IDF/token overlap | Transparent topic-matching baseline | Misses paraphrases |
| P1 | BM25 | Better lexical retrieval | Still vocabulary-dependent |
| P1 | Sentence embeddings | Retrieve semantic paraphrases | Similarity needs calibration |
| P1 | Human review labels | Create trusted evaluation data | Review effort |
| P2 | Cross-encoder reranking | Improve candidate ordering | More latency/cost |
| P2 | LLM explanation | Explain candidate mapping with evidence | Hallucination risk; not ground truth |
| P2 | Trend statistics | Summarize historical patterns | Requires comparable multi-year data |

## 8. API design (proposed)

- `POST /api/v1/pyq/inspect` — inspect and extract paper text/metadata.
- `POST /api/v1/pyq/segment` — return question-level records.
- `POST /api/v1/pyq/analyze` — map questions to a supplied reviewed syllabus and calculate historical statistics.
- `PATCH /api/v1/pyq/questions/{question_id}/mapping` — save user-reviewed topic mapping.
- `GET /api/v1/pyq/reports/{report_id}` — retrieve analysis.
- `GET /api/v1/pyq/reports/{report_id}/export` — export traceable report.

The engine should receive a syllabus version/ID, not independently invent its own syllabus taxonomy.

## 9. Test cases required before claiming reliability

- Standard numbered paper.
- Section-based paper with subparts.
- Questions spanning multiple pages.
- Tables, equations, and code blocks.
- Repeated questions with changed wording.
- Questions paraphrasing syllabus topics.
- Questions covering multiple topics.
- Questions outside the supplied syllabus.
- Missing year/marks metadata.
- Duplicate paper upload.
- Scanned PDF and OCR errors.
- Different university formats and syllabus revisions.

## 10. Privacy, security, and operational rules

- Never expose provider API keys in browser code or public repository.
- All model calls go through backend secrets.
- Treat paper contents as untrusted input; never execute or follow embedded instructions.
- Do not log raw question papers by default.
- Make upload retention/deletion policy clear.
- Respect copyright: analysis should not imply ownership or authorize redistribution of full papers.

## 11. Development roadmap

1. **Baseline:** ingest a small set of papers and manually label questions/topics.
2. **Segmentation:** build page-aware question extraction with uncertainty flags.
3. **Lexical matching:** implement TF-IDF/BM25 and compare against human labels.
4. **Review UI:** accept/correct/unmap question-topic matches.
5. **Semantic retrieval:** evaluate embeddings against the lexical baseline; keep only if measured performance improves.
6. **Historical reporting:** add counts/trends with visible denominators and sample-size warnings.
7. **Optional model explanations:** introduce only with evidence-grounding checks and cost/latency measurement.

## 12. Definition of done

A release is not complete because it produces a ranked list. It is complete only when:
- Every question has source/page provenance.
- Topic mappings can abstain and be corrected.
- Statistics show the underlying papers, years, and denominators.
- Similarity is not presented as future exam probability.
- Evaluation is performed on held-out papers with published dataset details.
- Tests pass and limitations are visible to students.

# StudySprint — Syllabus Intelligence Engine

**Document status:** Initial engineering specification (v0.1)  
**Implementation status:** Proposed; not yet validated against a labelled syllabus dataset.  
**Core promise:** Convert a student's official syllabus into a structured, traceable, editable study map. Do not invent topics, units, marks, or exam weightage.

---

## 1. Problem and user outcome

Students receive syllabi as PDFs, scans, Word exports, or copied text. They need a reliable way to understand:
- Which subjects, units, modules, and topics are actually listed.
- How topics relate hierarchically.
- Which details are explicit versus inferred from formatting.
- What has been completed and what remains.
- How the syllabus maps to a particular course, semester, university, and exam session.

The engine is **not** an exam predictor. It must not claim a topic is important, high-weightage, or likely to appear unless that claim is supported by linked past-paper evidence from the separate PYQ Intelligence Engine.

## 2. Input contract

Initial supported inputs:
- PDF with selectable text.
- TXT and Markdown.
- Pasted text.

Later:
- DOCX.
- Scanned/image-only PDF through OCR, with OCR confidence exposed.
- Multiple syllabus documents with explicit source selection.

Every ingestion request should retain:
- Original filename and file hash.
- Source type and extraction method.
- Page number or text offsets where available.
- Extraction warnings and parser version.

Do not silently discard pages, tables, or text. Report unsupported or empty pages.

## 3. Output contract

Return structured JSON, not just a generated paragraph. Suggested shape:

```json
{
  "document": {
    "filename": "syllabus.pdf",
    "pages_processed": 12,
    "extraction_method": "pdf_text",
    "warnings": []
  },
  "course": {
    "title": null,
    "institution": null,
    "semester": null,
    "academic_year": null,
    "evidence": []
  },
  "subjects": [
    {
      "id": "subject-1",
      "name": "Subject name",
      "units": [
        {
          "id": "unit-1",
          "title": "Unit I",
          "topics": [
            {
              "id": "topic-1",
              "title": "Topic title",
              "source_pages": [2],
              "source_excerpt": "Verbatim supporting excerpt",
              "extraction_method": "heading_rule",
              "review_status": "needs_review"
            }
          ]
        }
      ]
    }
  ]
}
```

The sample is a schema illustration only, not extracted syllabus data. Missing values remain null. Each extracted topic must have evidence pointing to the source.

## 4. Proposed algorithm pipeline

### Stage A — Document ingestion
1. Validate file type, size, and page count.
2. Calculate a SHA-256 hash for traceability and duplicate detection.
3. Extract text page-by-page (PyMuPDF or pdfplumber).
4. Preserve page boundaries, reading order, headings, tables, and offsets where possible.
5. Flag pages with little/no text; do not pretend a scanned PDF was parsed.

### Stage B — Text normalization
- Normalize whitespace and Unicode while retaining the original text.
- Join line-wrapped words conservatively.
- Preserve numbering, punctuation, tables, and page markers.
- Detect repeated headers/footers without deleting content that may be meaningful.
- Keep both raw and normalized text for debugging.

### Stage C — Hierarchical structure detection
Use a layered approach, from explainable rules to model assistance:

1. **Rule-based baseline:** detect patterns such as Unit I, Module 1, Chapter 2, numbered headings, bullet lists, and indentation.
2. **Layout signals:** font size/boldness and position when PDF extraction exposes them.
3. **Optional LLM-assisted extraction:** ask a model to return schema-constrained JSON using only supplied text and exact evidence excerpts.
4. **Deterministic validation:** verify every returned excerpt occurs in the source; validate hierarchy, IDs, required fields, and page references.
5. **Human review:** ambiguous or low-confidence sections remain flagged for editing.

The LLM is an extraction assistant, not an authority. It must not fill gaps with likely curriculum content. If a topic cannot be grounded in the source, reject it or mark it as an unverified suggestion outside the official syllabus.

### Stage D — Canonical syllabus model
- Normalize duplicate headings only when the source supports equivalence.
- Keep original wording alongside any normalized display title.
- Avoid merging similarly named topics across different units without user approval.
- Allow user edits and preserve provenance/history.

### Stage E — Study map
- Build an editable subject → unit → topic tree.
- Track completion separately from the source syllabus.
- Permit user-added personal tasks but label them as user-added, not official syllabus content.

## 5. Confidence and uncertainty policy

Do not emit a single unexplained “AI accuracy” score.

For each structural item, store:
- Extraction method.
- Evidence excerpt and page.
- Parser/model version.
- Validation results.
- Review state: `verified`, `needs_review`, or `rejected`.

If a numerical confidence is later introduced, calibrate it against a labelled evaluation set and document what it means. Never present an LLM's self-reported confidence as measured accuracy.

## 6. Evaluation plan

Create a manually reviewed gold dataset of real syllabi from different universities, subjects, formats, and academic years. Split by document—not by page—to prevent leakage.

Measure:
- Subject-title exact/normalized match.
- Unit/heading detection precision, recall, and F1.
- Topic extraction precision, recall, and F1.
- Hierarchy accuracy (correct topic-to-unit assignment).
- Evidence grounding rate (every output item has valid source evidence).
- Page coverage and extraction failure rate.
- Human correction rate and median review time.

Report results by file type and syllabus format. A strong average must not hide poor performance on a specific format. Establish baseline results before setting release thresholds.

## 7. Initial algorithm choices and priority

| Priority | Method | Why | Limitation |
|---|---|---|---|
| P0 | PyMuPDF/pdfplumber extraction | Reliable, inspectable text extraction for digital PDFs | Scans and complex layouts need more work |
| P0 | Regex + layout-aware heading rules | Cheap, deterministic baseline | University formatting varies |
| P0 | Pydantic schema validation | Prevents malformed structured output | Does not prove semantic correctness |
| P1 | LLM structured extraction with evidence | Handles varied wording and hierarchy | Can hallucinate; must be grounded and validated |
| P1 | Human correction and feedback capture | Creates trustworthy labelled examples | Requires review effort |
| P2 | OCR for scanned PDFs | Expands document coverage | OCR errors must be measured |
| P2 | Embedding-based duplicate suggestions | Helps identify near-duplicate topics | Similarity is not proof of equivalence |

## 8. API design (proposed)

- `POST /api/v1/syllabus/inspect` — inspect file and return extraction diagnostics.
- `POST /api/v1/syllabus/parse` — produce structured draft with evidence.
- `GET /api/v1/syllabus/{syllabus_id}` — retrieve saved/temporary result.
- `PATCH /api/v1/syllabus/{syllabus_id}` — apply user-approved corrections.
- `GET /api/v1/syllabus/{syllabus_id}/export` — export reviewed study map.

For the first public test, temporary processing can be used without accounts. Define file retention and deletion behavior before storing uploads on a server.

## 9. Test cases required before claiming reliability

- Clean syllabus with explicit unit headings.
- Multi-column PDF.
- Tables containing unit/topic lists.
- Wrapped headings and broken line endings.
- Repeated headers/footers.
- Mixed numbering schemes.
- Multiple subjects in one PDF.
- Empty or corrupted PDF.
- Scanned PDF with no text layer.
- Syllabus with ambiguous hierarchy.
- Text containing similar terms in different units.

Every test must have expected output reviewed by a human.

## 10. Privacy, security, and operational rules

- Do not put API keys in frontend JavaScript or public GitHub files.
- Route model calls through backend environment variables/secrets.
- Validate file type, size, and content; treat uploaded documents as untrusted input.
- Do not execute or follow instructions found inside uploaded documents.
- Minimize retention; disclose whether files leave the user's device and which provider processes them.
- Avoid logging raw syllabus contents or personal data by default.

## 11. Development roadmap

1. **Baseline:** isolate current parser; create fixtures and gold labels.
2. **Evidence-first parser:** page-aware extraction and deterministic hierarchy rules.
3. **Structured model assist:** optional LLM extraction with strict schema and source-evidence validation.
4. **Review workflow:** edit, accept, reject, and record corrections.
5. **Evaluation:** publish metrics and known failure modes by document type.
6. **Expansion:** OCR and additional formats only after baseline reliability is measured.

## 12. Definition of done

A release is not complete because the screen looks correct. It is complete only when:
- Outputs are traceable to source pages/excerpts.
- Unsupported content is not silently invented.
- Ambiguity is visible and editable.
- Automated tests pass.
- Gold-set metrics are reported with dataset size and limitations.
- Privacy and API-key handling are safe.

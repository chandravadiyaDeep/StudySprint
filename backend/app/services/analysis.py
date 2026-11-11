"""Orchestrates extraction, Gemini classification and deterministic evidence aggregation."""
from collections import defaultdict
from app.config import get_settings
from app.schemas import AnalyzeRequest, AnalyzeResponse, EvidenceQuestion, TopicEvidence
from app.services.gemini import classify_questions, PROMPT_VERSION
from app.services.segmentation import segment_paper

ENGINE_VERSION = "pyq-engine-0.1.0"


def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    settings = get_settings()
    total_chars = sum(len(paper.text) for paper in request.papers)
    if len(request.papers) > settings.max_papers_per_request:
        raise ValueError(f"A maximum of {settings.max_papers_per_request} papers is allowed per analysis.")
    if any(len(paper.text) > settings.max_chars_per_paper for paper in request.papers):
        raise ValueError("One paper exceeds the configured text limit.")
    if total_chars > settings.max_total_chars:
        raise ValueError("The combined paper text exceeds the configured request limit.")

    candidates = []
    warnings = []
    for paper_index, paper in enumerate(request.papers):
        found, paper_warnings = segment_paper(paper.name, paper.text, paper_index)
        candidates.extend(found)
        warnings.extend(paper_warnings)

    if not candidates:
        raise ValueError("No numbered question candidates were confidently extracted. Review the PDF text or use a clearer text-based paper.")

    records = [{"question_id": q.question_id, "paper_name": q.paper_name, "question_text": q.text} for q in candidates]
    draft, model_name = classify_questions(records)
    candidate_by_id = {q.question_id: q for q in candidates}
    seen_ids = set()
    grouped = defaultdict(list)
    unclassified = []

    # Reject unknown/duplicate model IDs so generated output cannot fabricate evidence rows.
    for item in draft.classifications:
        if item.question_id not in candidate_by_id or item.question_id in seen_ids:
            continue
        seen_ids.add(item.question_id)
        source = candidate_by_id[item.question_id]
        # Collapse trivial casing/spacing variants while preserving the first readable label.
        canonical_label = " ".join(item.canonical_topic.split())
        topic_key = canonical_label.casefold()
        if topic_key not in grouped:
            grouped[topic_key] = {"label": canonical_label, "entries": []}
        grouped[topic_key]["entries"].append((source, item))

    for candidate in candidates:
        if candidate.question_id not in seen_ids:
            unclassified.append({"question_id": candidate.question_id, "paper_name": candidate.paper_name,
                                 "question_text": candidate.text, "reason": "No valid classification returned; excluded from topic counts."})

    topics = []
    for topic_data in grouped.values():
        topic = topic_data["label"]
        entries = topic_data["entries"]
        # Counts are computed from verified source records, never requested from Gemini.
        paper_names = sorted({source.paper_name for source, _ in entries})
        questions = [EvidenceQuestion(
            question_id=source.question_id,
            paper_name=source.paper_name,
            question_text=source.text,
            subtopic=classification.subtopic,
            question_type=classification.question_type,
            difficulty=classification.difficulty,
            confidence=classification.confidence,
        ) for source, classification in entries]
        summaries = [classification.concept_summary for _, classification in entries]
        topics.append(TopicEvidence(
            topic=topic,
            question_count=len(entries),
            paper_count=len(paper_names),
            paper_coverage_percent=round(100 * len(paper_names) / len(request.papers), 1),
            papers=paper_names,
            concept_summary=summaries[0],
            questions=questions,
            confidence_note="AI topic labels; frequency and paper coverage are deterministic counts of the listed source questions.",
        ))

    # Rank by number of distinct source papers first, then number of question occurrences.
    topics.sort(key=lambda item: (item.paper_count, item.question_count), reverse=True)
    warnings.extend(draft.overall_notes)
    if unclassified:
        warnings.append(f"{len(unclassified)} extracted question(s) were not classified and are excluded from topic frequencies.")

    return AnalyzeResponse(
        engine_version=ENGINE_VERSION,
        prompt_version=PROMPT_VERSION,
        model=model_name,
        subject=request.subject,
        papers_received=len(request.papers),
        questions_extracted=len(candidates),
        topics=topics,
        unclassified_questions=unclassified,
        warnings=warnings,
        evidence_notice="Historical observations only. Topic frequency is counted from the uploaded papers shown here; it is not a prediction or guarantee about a future exam.",
    )

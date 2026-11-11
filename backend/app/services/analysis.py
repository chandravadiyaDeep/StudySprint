"""Orchestrates extraction, Gemini classification and deterministic evidence aggregation."""
from collections import defaultdict
from app.config import get_settings
from app.schemas import AnalyzeRequest, AnalyzeResponse, EvidenceQuestion, TopicEvidence, SimilarQuestionGroup
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

    # Build a lookup so similar-question links can only reference real classified records.
    classification_by_id = {item.question_id: item for item in draft.classifications if item.question_id in seen_ids}
    topic_key_by_id = {
        item.question_id: " ".join(item.canonical_topic.split()).casefold()
        for item in draft.classifications if item.question_id in seen_ids
    }

    def evidence_question(source, classification):
        # Preserve source text and only expose related IDs that exist in this analysis.
        valid_related = sorted({
            related_id for related_id in classification.related_question_ids
            if related_id in candidate_by_id and related_id in seen_ids and related_id != source.question_id
        })
        return EvidenceQuestion(
            question_id=source.question_id,
            paper_name=source.paper_name,
            question_text=source.text,
            subtopic=classification.subtopic,
            question_type=classification.question_type,
            difficulty=classification.difficulty,
            confidence=classification.confidence,
            related_question_ids=valid_related,
        )

    topics = []
    for topic_data in grouped.values():
        topic = topic_data["label"]
        entries = topic_data["entries"]
        # Counts are computed from verified source records, never requested from Gemini.
        paper_names = sorted({source.paper_name for source, _ in entries})
        questions = [evidence_question(source, classification) for source, classification in entries]
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

    # Keep only reciprocal AI similarity suggestions within the same topic; this reduces weak merges.
    adjacency = {question_id: set() for question_id in seen_ids}
    for question_id, classification in classification_by_id.items():
        for related_id in classification.related_question_ids:
            related_classification = classification_by_id.get(related_id)
            if not related_classification:
                continue
            reciprocal = question_id in related_classification.related_question_ids
            same_topic = topic_key_by_id.get(question_id) == topic_key_by_id.get(related_id)
            if reciprocal and same_topic:
                adjacency[question_id].add(related_id)
                adjacency[related_id].add(question_id)

    similar_question_groups = []
    visited = set()
    for question_id in sorted(adjacency):
        if question_id in visited or not adjacency[question_id]:
            continue
        stack, component = [question_id], []
        visited.add(question_id)
        while stack:
            current = stack.pop()
            component.append(current)
            for neighbour in adjacency[current]:
                if neighbour not in visited:
                    visited.add(neighbour)
                    stack.append(neighbour)
        if len(component) < 2:
            continue
        component_sources = [candidate_by_id[item_id] for item_id in component]
        component_questions = [
            evidence_question(source, classification_by_id[source.question_id])
            for source in component_sources
        ]
        component_papers = sorted({source.paper_name for source in component_sources})
        topic_label = next((data["label"] for data in grouped.values()
                            if " ".join(data["label"].split()).casefold() == topic_key_by_id[component[0]]), "Related questions")
        similar_question_groups.append(SimilarQuestionGroup(
            group_id=f"similar-{len(similar_question_groups) + 1}",
            topic=topic_label,
            question_count=len(component_questions),
            paper_count=len(component_papers),
            papers=component_papers,
            questions=component_questions,
        ))

    # Rank by number of distinct source papers first, then number of question occurrences.
    topics.sort(key=lambda item: (item.paper_count, item.question_count), reverse=True)
    similar_question_groups.sort(key=lambda item: (item.paper_count, item.question_count), reverse=True)
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
        similar_question_groups=similar_question_groups,
        unclassified_questions=unclassified,
        warnings=warnings,
        evidence_notice="Historical observations only. Topic frequency is counted from the uploaded papers shown here; it is not a prediction or guarantee about a future exam.",
    )

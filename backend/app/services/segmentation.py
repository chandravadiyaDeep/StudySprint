"""Deterministic question candidate segmentation (baseline v1)."""
import re
import unicodedata
from dataclasses import dataclass

# Recognize common exam question numbering; this is deliberately conservative.
BOUNDARY = re.compile(r"(?im)^\\s*(?:Q(?:uestion)?\\s*)?\\d{1,2}\\s*[.)]\\s+|^\\s*Q\\s*\\d{1,2}\\s*[:.)-]\\s+")

@dataclass
class QuestionCandidate:
    question_id: str
    paper_name: str
    text: str
    extraction_confidence: str


def normalize_for_detection(text: str) -> str:
    # Normalize only for boundary detection; preserve original text in each candidate.
    return unicodedata.normalize("NFKC", text).replace("\\r\\n", "\\n").replace("\\r", "\\n")


def segment_paper(paper_name: str, text: str, paper_index: int) -> tuple[list[QuestionCandidate], list[str]]:
    normalized = normalize_for_detection(text)
    lines = normalized.split("\\n")
    starts: list[int] = []
    for index, line in enumerate(lines):
        if BOUNDARY.match(line):
            starts.append(index)

    warnings: list[str] = []
    if not starts:
        # Do not hallucinate question boundaries when the document format is unknown.
        warnings.append(f"{paper_name}: no confident numbered question boundaries found; review extraction format.")
        return [], warnings

    candidates: list[QuestionCandidate] = []
    for position, start in enumerate(starts):
        end = starts[position + 1] if position + 1 < len(starts) else len(lines)
        raw = "\\n".join(lines[start:end]).strip()
        # Remove leading question number from the stored text only when it is a boundary marker.
        raw = re.sub(r"^\\s*(?:Q(?:uestion)?\\s*)?\\d{1,2}\\s*[.)][: -]?\\s*", "", raw, count=1, flags=re.I)
        raw = re.sub(r"\\s+", " ", raw).strip()
        if len(raw) < 12:
            warnings.append(f"{paper_name}: skipped a very short candidate at extracted question {position + 1}.")
            continue
        candidates.append(QuestionCandidate(
            question_id=f"p{paper_index + 1}_q{len(candidates) + 1}",
            paper_name=paper_name,
            text=raw,
            extraction_confidence="medium" if len(starts) >= 2 else "low",
        ))
    return candidates, warnings

"""Validated API contracts for PYQ analysis."""
from typing import Literal
from pydantic import BaseModel, Field, field_validator


class PaperInput(BaseModel):
    # The browser extracts selectable text; original file bytes are not stored by this API.
    name: str = Field(min_length=1, max_length=180)
    text: str = Field(min_length=30, max_length=120_000)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        return value.replace("\\", "/").split("/")[-1].strip()


class AnalyzeRequest(BaseModel):
    subject: str = Field(default="", max_length=180)
    papers: list[PaperInput] = Field(min_length=1, max_length=10)


class QuestionClassification(BaseModel):
    question_id: str
    canonical_topic: str = Field(min_length=1, max_length=120)
    subtopic: str = Field(default="", max_length=120)
    concept_summary: str = Field(min_length=1, max_length=500)
    question_type: Literal[\"definition\", \"explanation\", \"comparison\", \"derivation\", \"numerical\", \"problem_solving\", \"coding\", \"proof\", \"diagram\", \"short_note\", \"application\", \"mixed\", \"uncertain\"]
    difficulty: str = Field(pattern="^(easy|moderate|challenging|uncertain)$")
    rationale: str = Field(min_length=1, max_length=400)
    confidence: str = Field(pattern="^(high|medium|low)$")
    related_question_ids: list[str] = Field(default_factory=list)


class GeminiDraft(BaseModel):
    classifications: list[QuestionClassification]
    overall_notes: list[str] = Field(default_factory=list)


class EvidenceQuestion(BaseModel):
    question_id: str
    paper_name: str
    question_text: str
    subtopic: str
    question_type: str
    difficulty: str
    confidence: str
    related_question_ids: list[str] = Field(default_factory=list)


class TopicEvidence(BaseModel):
    topic: str
    question_count: int
    paper_count: int
    paper_coverage_percent: float
    papers: list[str]
    concept_summary: str
    questions: list[EvidenceQuestion]
    confidence_note: str


class SimilarQuestionGroup(BaseModel):
    group_id: str
    topic: str
    question_count: int
    paper_count: int
    papers: list[str]
    questions: list[EvidenceQuestion]


class AnalyzeResponse(BaseModel):
    engine_version: str
    prompt_version: str
    model: str
    subject: str
    papers_received: int
    questions_extracted: int
    topics: list[TopicEvidence]
    similar_question_groups: list[SimilarQuestionGroup] = Field(default_factory=list)
    unclassified_questions: list[dict]
    warnings: list[str]
    evidence_notice: str

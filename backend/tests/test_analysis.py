"""Tests that reported topic counts are derived from source question records."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.schemas import AnalyzeRequest, PaperInput, GeminiDraft, QuestionClassification
from app.services.analysis import analyze


class AnalysisAggregationTests(unittest.TestCase):
    @patch("app.services.analysis.get_settings")
    @patch("app.services.analysis.classify_questions")
    def test_topic_frequency_counts_uploaded_source_questions(self, mock_classify, mock_settings):
        mock_settings.return_value = SimpleNamespace(
            max_papers_per_request=10, max_chars_per_paper=120000, max_total_chars=500000
        )
        mock_classify.return_value = (GeminiDraft(classifications=[
            QuestionClassification(question_id="p1_q1", canonical_topic="Linked Lists",
                concept_summary="Linked list operations", question_type="explanation",
                difficulty="moderate", rationale="Asks about list operations", confidence="high",
                related_question_ids=["p2_q1"]),
            QuestionClassification(question_id="p2_q1", canonical_topic="linked lists",
                concept_summary="Linked list insertion", question_type="application",
                difficulty="moderate", rationale="Asks about insertion", confidence="medium",
                related_question_ids=["p1_q1"]),
        ]), "test-model")
        request = AnalyzeRequest(subject="Data Structures", papers=[
            PaperInput(name="paper-2023.txt", text="Q1. Explain linked list operations in detail."),
            PaperInput(name="paper-2024.txt", text="Q1. Explain insertion in a linked list with an example."),
        ])
        result = analyze(request)
        self.assertEqual(result.questions_extracted, 2)
        self.assertEqual(len(result.topics), 1)
        self.assertEqual(result.topics[0].question_count, 2)
        self.assertEqual(result.topics[0].paper_count, 2)
        self.assertEqual(result.topics[0].paper_coverage_percent, 100.0)
        self.assertEqual(len(result.topics[0].questions), 2)
        self.assertEqual(len(result.similar_question_groups), 1)
        self.assertEqual(result.similar_question_groups[0].question_count, 2)


if __name__ == "__main__":
    unittest.main()

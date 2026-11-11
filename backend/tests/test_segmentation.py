"""Unit tests for deterministic question segmentation."""
import unittest
from app.services.segmentation import segment_paper


class SegmentationTests(unittest.TestCase):
    def test_extracts_numbered_questions_and_preserves_question_text(self):
        text = "Data Structures\nQ1. Explain linked lists with an example.\nQ2. Compare stack and queue data structures.\n3) Define time complexity."
        questions, warnings = segment_paper("paper-2024.txt", text, 0)
        self.assertEqual(len(questions), 3)
        self.assertIn("Explain linked lists", questions[0].text)
        self.assertEqual(questions[0].question_id, "p1_q1")
        self.assertEqual(warnings, [])

    def test_does_not_invent_boundaries(self):
        questions, warnings = segment_paper("unstructured.txt", "A paragraph without numbered question markers.", 0)
        self.assertEqual(questions, [])
        self.assertTrue(warnings)


if __name__ == "__main__":
    unittest.main()

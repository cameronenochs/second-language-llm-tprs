import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from format_dialogue import format_dialogue


class FormatDialogueTests(unittest.TestCase):
    def test_either_or_gets_pause(self):
        self.assertEqual(
            format_dialogue("Teacher: Venditne Albinus gemmas an libros?", or_word="an"),
            "Teacher: Venditne Albinus gemmas, [pause] an libros?",
        )

    def test_idempotent(self):
        once = format_dialogue("Teacher: Venditne gemmas, an libros?", or_word="an")
        self.assertEqual(format_dialogue(once, or_word="an"), once)

    def test_or_word_only_in_questions(self):
        line = "Teacher: Ita! Albinus an amicus est."
        self.assertEqual(format_dialogue(line, or_word="an"), line)

    def test_unknown_marker_removed(self):
        self.assertEqual(format_dialogue("Learner: Mmm [laughs] novi!"), "Learner: Mmm novi!")

    def test_marker_case_and_duplicates(self):
        self.assertEqual(format_dialogue("Teacher: a [PAUSE] [pause] b"), "Teacher: a [pause] b")

    def test_non_dialogue_lines_untouched(self):
        self.assertEqual(format_dialogue("# Title\n\n"), "# Title\n\n")

    def test_no_or_word_no_rewrite(self):
        line = "Teacher: gemmas an libros?"
        self.assertEqual(format_dialogue(line), line)

    def test_crlf_input(self):
        self.assertEqual(format_dialogue("Teacher: a\r\nLearner: b\r\n"), "Teacher: a\nLearner: b\n")


if __name__ == "__main__":
    unittest.main()

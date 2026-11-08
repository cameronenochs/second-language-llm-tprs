import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import tprs_config as c


class ConfigTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.path = os.path.join(self.dir.name, "tprs.config.json")

    def test_missing_file_returns_empty(self):
        self.assertEqual(c.load_language_config(self.path, "latin"), {})

    def test_language_key_case_insensitive(self):
        c.save_language_config(self.path, "Latin", {"teacher_voice_id": "t"})
        self.assertEqual(c.load_language_config(self.path, " latin "), {"teacher_voice_id": "t"})

    def test_save_preserves_other_languages(self):
        c.save_language_config(self.path, "latin", {"teacher_voice_id": "L"})
        c.save_language_config(self.path, "italian", {"teacher_voice_id": "I"})
        self.assertEqual(c.load_language_config(self.path, "latin"), {"teacher_voice_id": "L"})
        self.assertEqual(c.load_language_config(self.path, "italian"), {"teacher_voice_id": "I"})

    def test_save_merges_fields(self):
        c.save_language_config(self.path, "latin", {"teacher_voice_id": "t"})
        c.save_language_config(self.path, "latin", {"learner_voice_id": "l"})
        self.assertEqual(
            c.load_language_config(self.path, "latin"),
            {"teacher_voice_id": "t", "learner_voice_id": "l"},
        )

    def test_missing_fields_partial(self):
        self.assertEqual(
            c.missing_fields({"teacher_voice_id": "x"}),
            ["learner_voice_id", "default_model_id"],
        )

    def test_invalid_json_raises(self):
        with open(self.path, "w") as f:
            f.write("{")
        with self.assertRaises(c.ConfigError) as cm:
            c.load_language_config(self.path, "latin")
        self.assertIn(self.path, str(cm.exception))

    def test_rejects_api_key_field(self):
        with self.assertRaises(c.ConfigError):
            c.save_language_config(self.path, "latin", {"api_key": "x"})


class ReadingFieldsTests(unittest.TestCase):
    def test_reading_requires_only_narrator_and_model(self):
        self.assertEqual(c.missing_fields({"teacher_voice_id": "x"}, c.READING_FIELDS),
                         ["narrator_voice_id", "default_model_id"])


if __name__ == "__main__":
    unittest.main()

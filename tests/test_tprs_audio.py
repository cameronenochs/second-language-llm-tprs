import io
import os
import sys
import tempfile
import unittest
import urllib.error
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import tprs_audio as a
import tprs_config as c


class PureFunctionTests(unittest.TestCase):
    def test_markers_known_and_unknown(self):
        out = a.markers_to_breaks("a [pause] b [laughs] c")
        self.assertNotIn("[", out)
        self.assertEqual(out.count("<break"), 1)
        self.assertIn('<break time="0.5s"/>', out)

    def test_parse_skips_noise(self):
        text = "Teacher: Salve\r\n\r\nrandom text\r\nTeacher: [pause]\r\nLearner: Salve [slowly] magister\r\n"
        turns = a.parse_dialogue(text)
        self.assertEqual([s for s, _ in turns], ["Teacher", "Learner"])
        self.assertIn("<break", turns[1][1])

    def test_parse_empty_returns_empty_list(self):
        self.assertEqual(a.parse_dialogue("nothing here\n"), [])

    def test_select_turns(self):
        turns = [("Teacher", str(i)) for i in range(10)]
        self.assertEqual(len(a.select_turns(turns, 4)), 4)
        self.assertEqual(len(a.select_turns(turns, 50)), 10)
        self.assertEqual(len(a.select_turns(turns, None)), 10)

    def test_build_payload_omits_none(self):
        p = a.build_payload("hi", "eleven_v4", {"stability": 0.4}, language_code="la")
        self.assertNotIn("previous_text", p)
        self.assertNotIn("next_text", p)
        self.assertEqual(p["language_code"], "la")
        self.assertNotIn("language_code", a.build_payload("hi", "m", {}))

    def test_resolve_voices_env_overrides_config(self):
        entry = {"teacher_voice_id": "T", "learner_voice_id": "L"}
        v = a.resolve_voices(entry, {"TEACHER_VOICE_ID": "T2"})
        self.assertEqual(v, {"Teacher": "T2", "Learner": "L"})

    def test_resolve_voices_missing_names_fields(self):
        with self.assertRaises(c.ConfigError) as cm:
            a.resolve_voices({"teacher_voice_id": "T"}, {})
        self.assertIn("learner_voice_id", str(cm.exception))


class MainAndErrorTests(unittest.TestCase):
    def test_main_missing_api_key_exits_before_network(self):
        with tempfile.TemporaryDirectory() as d:
            cfg = os.path.join(d, "cfg.json")
            c.save_language_config(
                cfg, "latin",
                {"teacher_voice_id": "T", "learner_voice_id": "L", "default_model_id": "eleven_v4"},
            )
            inp = os.path.join(d, "in.txt")
            with open(inp, "w") as f:
                f.write("Teacher: Salve\n")
            with mock.patch.dict(os.environ, {}, clear=True), \
                 mock.patch("urllib.request.urlopen", side_effect=AssertionError("network")):
                with self.assertRaises(SystemExit) as cm:
                    a.main([inp, os.path.join(d, "o.mp3"), "--language", "latin", "--config", cfg])
            self.assertIn("ELEVENLABS_API_KEY", str(cm.exception))

    def test_tts_401_and_402_messages(self):
        for code, text in ((401, "rejected the API key (401)"), (402, "plan/credits issue (402)")):
            err = urllib.error.HTTPError("u", code, "x", {}, io.BytesIO(b""))
            with mock.patch("urllib.request.urlopen", side_effect=err):
                with self.assertRaises(a.TTSError) as cm:
                    a.tts("hi", "V", "k", "/dev/null", "eleven_v4", {})
            self.assertIn(text, str(cm.exception))


if __name__ == "__main__":
    unittest.main()

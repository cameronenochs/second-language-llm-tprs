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


class FinalReviewFixTests(unittest.TestCase):
    def _setup(self, d, dialogue="Teacher: Salve\nLearner: Ave\n"):
        cfg = os.path.join(d, "cfg.json")
        c.save_language_config(
            cfg, "latin",
            {"teacher_voice_id": "T", "learner_voice_id": "L", "default_model_id": "eleven_v4"},
        )
        inp = os.path.join(d, "in.txt")
        with open(inp, "w") as f:
            f.write(dialogue)
        out = os.path.join(d, "o.mp3")
        return ["main", inp, out, "--language", "latin", "--config", cfg][1:], out

    def test_tts_other_http_error_includes_body(self):
        err = urllib.error.HTTPError("u", 400, "x", {}, io.BytesIO(b'{"detail":"bad voice id"}'))
        with mock.patch("urllib.request.urlopen", side_effect=err):
            with self.assertRaises(a.TTSError) as cm:
                a.tts("hi", "V", "k", "/dev/null", "eleven_v4", {})
        self.assertIn("400", str(cm.exception))
        self.assertIn("bad voice id", str(cm.exception))

    def test_tts_network_error_is_ttserror_and_has_timeout(self):
        with mock.patch("urllib.request.urlopen", side_effect=urllib.error.URLError("offline")) as m:
            with self.assertRaises(a.TTSError) as cm:
                a.tts("hi", "V", "k", "/dev/null", "eleven_v4", {})
        self.assertIn("network error", str(cm.exception))
        self.assertIn("timeout", m.call_args.kwargs)

    def test_missing_ffmpeg_is_clear_error(self):
        with tempfile.TemporaryDirectory() as d:
            argv, _ = self._setup(d)
            with mock.patch.dict(os.environ, {"ELEVENLABS_API_KEY": "k"}, clear=True), \
                 mock.patch("subprocess.run", side_effect=FileNotFoundError()):
                with self.assertRaises(SystemExit) as cm:
                    a.main(argv)
        self.assertIn("ffmpeg not found", str(cm.exception))

    def test_failure_keeps_rendered_clips_and_rerun_skips_them(self):
        calls = []
        fail = [True]

        def flaky(text, voice, key, path, *rest, **kw):
            calls.append(text)
            if fail[0] and len(calls) == 2:
                raise a.TTSError("ElevenLabs plan/credits issue (402)")
            with open(path, "wb") as f:
                f.write(b"x")

        env = {"ELEVENLABS_API_KEY": "k"}
        with tempfile.TemporaryDirectory() as d:
            argv, out = self._setup(d)
            with mock.patch.dict(os.environ, env, clear=True), \
                 mock.patch.object(a, "run_ffmpeg"), mock.patch.object(a, "tts", side_effect=flaky):
                with self.assertRaises(SystemExit):
                    a.main(argv)
                self.assertEqual(len(os.listdir(out + ".parts")), 1)
                calls.clear()
                fail[0] = False
                a.main(argv)
            self.assertEqual(calls, ["Ave"])
            self.assertFalse(os.path.exists(out + ".parts"))

    def test_unusual_markers_are_not_spoken(self):
        out = a.markers_to_breaks("a [pause-long] b [ride!] c [1] d")
        self.assertNotIn("[", out)


class ReadingModeTests(unittest.TestCase):
    def test_parse_reading_one_turn_per_line(self):
        turns = a.parse_reading("Gallia est [pause] omnis.\n\n  \n[pause]\nDivisa est.\n")
        self.assertEqual(turns, [("Narrator", 'Gallia est <break time="0.5s"/> omnis.'), ("Narrator", "Divisa est.")])

    def test_resolve_narrator(self):
        self.assertEqual(a.resolve_narrator({"narrator_voice_id": "n1"}, {}), {"Narrator": "n1"})
        self.assertEqual(a.resolve_narrator({}, {"NARRATOR_VOICE_ID": "e"}), {"Narrator": "e"})
        with self.assertRaises(c.ConfigError):
            a.resolve_narrator({}, {})


class CourseModeTests(unittest.TestCase):
    SCRIPT = (
        '{"id": "L1-01-01-1", "text": "Puella."}\n'
        '{"id": "L1-01-01-2", "text": "Puella."}\n\n'
        '{"id": "L1-01-01-3", "text": "Puer."}\n'
        '{"id": "L1-01-01-4", "text": "Rosa est."}\n'
    )

    def test_parse_course_keeps_ids_and_rejects_bad_rows(self):
        self.assertEqual(a.parse_course(self.SCRIPT)[1], ("L1-01-01-2", "Puella."))
        with self.assertRaises(ValueError):
            a.parse_course('{"text": "no id"}\n')

    def test_render_dedupes_names_opaquely_and_limits_distinct_texts(self):
        items = a.parse_course(self.SCRIPT)
        calls = []
        with tempfile.TemporaryDirectory() as d, \
             mock.patch.object(a, "tts", side_effect=lambda t, v, k, out, *rest: (calls.append(t), open(out, "wb").write(b"x"))):
            clips = a.render_course(items, d, "v", "k", "m", {}, None, limit=2)
            with open(os.path.join(d, "index.json"), encoding="utf-8") as f:
                index = __import__("json").load(f)
        self.assertEqual(calls, ["Puella.", "Puer."])
        self.assertEqual(len(clips), 2)
        self.assertEqual(index["L1-01-01-1"], index["L1-01-01-2"])
        self.assertNotIn("L1-01-01-4", index)
        self.assertNotIn("Puella", index["L1-01-01-1"])

    def test_main_course_join_writes_test_clip(self):
        with tempfile.TemporaryDirectory() as d:
            script = os.path.join(d, "script.jsonl")
            with open(script, "w", encoding="utf-8") as f:
                f.write(self.SCRIPT)
            env = {"ELEVENLABS_API_KEY": "k", "NARRATOR_VOICE_ID": "n"}
            with mock.patch.dict(os.environ, env, clear=True), \
                 mock.patch.object(a, "tts", side_effect=lambda t, v, k, out, *rest: open(out, "wb").write(b"x")), \
                 mock.patch.object(a, "run_ffmpeg"), mock.patch.object(a, "join_clips") as join:
                a.main([script, os.path.join(d, "audio"), "--language", "latin", "--mode", "course",
                        "--limit", "4", "--join", os.path.join(d, "test-4lines.mp3"),
                        "--config", os.path.join(d, "none.json")])
            self.assertEqual(len(join.call_args[0][0]), 3)
            self.assertEqual(len(os.listdir(os.path.join(d, "audio"))), 4)  # 3 clips + index.json


    def test_join_clips_lists_absolute_paths(self):
        seen = []

        def capture(args):
            if "concat" in args:
                with open(args[args.index("-i") + 1]) as f:
                    seen.append(f.read())

        with mock.patch.object(a, "run_ffmpeg", side_effect=capture):
            a.join_clips(["audio/x.mp3"], "out.mp3")
        self.assertIn(f"file '{os.path.abspath('audio/x.mp3')}'", seen[0])


if __name__ == "__main__":
    unittest.main()

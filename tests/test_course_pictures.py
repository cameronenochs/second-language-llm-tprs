import base64
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import course_pictures as cp


def items(scenes):
    return [{"id": f"i{n}", "scene": s} for n, s in enumerate(scenes, 1)]


class PlanTests(unittest.TestCase):
    def test_same_scene_shares_picture_and_sheets_hold_six(self):
        scenes = ["A car.", "a car", "A boy"] + [f"thing {n}" for n in range(6)]
        out = cp.plan(items(scenes))
        self.assertEqual(out["sheets"], 2)
        first = out["pictures"][0]
        self.assertEqual(first["items"], ["i1", "i2"])
        self.assertEqual((first["sheet"], first["tile"]), (1, 1))
        last = out["pictures"][-1]
        self.assertEqual((last["id"], last["sheet"], last["tile"]), ("p008", 2, 2))

    def test_sheet_prompt_fills_empty_panels(self):
        prompt = cp.sheet_prompt("Line art.", ["a dog", "a cat"])
        self.assertIn("1. a dog", prompt)
        self.assertIn("6. Leave this panel empty white.", prompt)

    def test_read_script_rejects_missing_scene(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "s.jsonl")
            with open(path, "w") as f:
                f.write('{"id": "x", "text": "t"}\n')
            with self.assertRaises(ValueError):
                cp.read_script(path)


class ProviderTests(unittest.TestCase):
    def test_detection_order(self):
        self.assertEqual(cp.detect_provider({"GEMINI_API_KEY": "g", "XAI_API_KEY": "x"}), "gemini")
        self.assertEqual(cp.detect_provider({"XAI_API_KEY": "x"}), "grok")
        self.assertEqual(cp.detect_provider({}), "manual")

    def test_manual_render_writes_prompts_and_exits(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "pictures.json"), "w") as f:
                json.dump(cp.plan(items(["a dog"])), f)
            with open(os.path.join(d, "style.md"), "w") as f:
                f.write("Line art.")
            with mock.patch.dict(os.environ, {}, clear=True), self.assertRaises(SystemExit) as cm:
                cp.main(["render", d, "--sheet", "1"])
            self.assertEqual(cm.exception.code, cp.MANUAL_EXIT)
            with open(os.path.join(d, "sheets", "prompts.md")) as f:
                self.assertIn("## sheet-01.png", f.read())

    def test_gemini_sends_refs_and_decodes_image(self):
        sent = {}

        def fake(url, payload, headers):
            sent.update(url=url, payload=payload, headers=headers)
            return {"candidates": [{"content": {"parts": [{"inlineData": {"data": base64.b64encode(b"IMG").decode()}}]}}]}

        with tempfile.TemporaryDirectory() as d:
            ref = os.path.join(d, "cast.png")
            with open(ref, "wb") as f:
                f.write(b"\x89PNG")
            with mock.patch.object(cp, "post_json", side_effect=fake):
                data = cp.gemini_image("draw", [ref], {"GEMINI_API_KEY": "k"})
        self.assertEqual(data, b"IMG")
        self.assertEqual(sent["headers"], {"x-goog-api-key": "k"})
        self.assertEqual(len(sent["payload"]["contents"][0]["parts"]), 2)


@unittest.skipUnless(shutil.which("ffmpeg"), "ffmpeg not on PATH")
class CutTests(unittest.TestCase):
    def test_cut_makes_six_tiles_of_one_sixth(self):
        with tempfile.TemporaryDirectory() as d:
            sheet = os.path.join(d, "sheet.png")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "color=white:s=600x400",
                            "-frames:v", "1", sheet], check=True)
            out = os.path.join(d, "pictures")
            cp.cut_sheet(sheet, [(t, f"p{t}") for t in range(1, 7)], out)
            self.assertEqual(len(os.listdir(out)), 6)
            with open(os.path.join(out, "p6.png"), "rb") as f:
                w, h = struct.unpack(">II", f.read(24)[16:24])
            self.assertEqual((w, h), (184, 184))


if __name__ == "__main__":
    unittest.main()

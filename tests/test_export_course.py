import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import export_course as ex


def lesson(d):
    rows = [("a", "Puella."), ("b", "Puella."), ("c", "Puer."), ("d", "Puella est.")]
    with open(os.path.join(d, "script.jsonl"), "w", encoding="utf-8") as f:
        for i, t in rows:
            f.write(json.dumps({"id": i, "text": t, "scene": "x"}) + "\n")
    pictures = {"sheets": 1, "pictures": [
        {"id": "p001", "items": ["a", "b", "d"], "sheet": 1, "tile": 1},
        {"id": "p002", "items": ["c"], "sheet": 1, "tile": 2},
    ]}
    with open(os.path.join(d, "pictures.json"), "w") as f:
        json.dump(pictures, f)
    os.makedirs(os.path.join(d, "pictures"))
    os.makedirs(os.path.join(d, "audio"))
    for pid in ("p001", "p002"):
        open(os.path.join(d, "pictures", f"{pid}.png"), "wb").close()
    index = {"a": "aaa.mp3", "b": "aaa.mp3", "c": "ccc.mp3", "d": "ddd.mp3"}
    for clip in set(index.values()):
        open(os.path.join(d, "audio", clip), "wb").close()
    with open(os.path.join(d, "audio", "index.json"), "w") as f:
        json.dump(index, f)


class ExportTests(unittest.TestCase):
    def test_manifest_dedupes_plates_and_keeps_item_order(self):
        with tempfile.TemporaryDirectory() as d:
            out_dir, app = os.path.join(d, "out"), os.path.join(d, "app")
            os.makedirs(out_dir)
            lesson(out_dir)
            path = ex.export(out_dir, "latin", 1, "1", app)
            with open(path) as f:
                m = json.load(f)
            self.assertTrue(path.endswith("latin-L1-01.json"))
            self.assertEqual(m["rounds"], [0, 0, 1, 2])
            self.assertEqual(m["plates"][2], {"image": "/courses/latin/L1-01/img/p001.png",
                                              "audio": "/courses/latin/L1-01/audio/ddd.mp3"})
            self.assertNotIn("Puella", json.dumps(m))
            self.assertTrue(os.path.exists(os.path.join(app, "public", "courses", "latin", "L1-01", "audio", "ccc.mp3")))

    def test_missing_clip_and_bad_language_fail(self):
        with self.assertRaises(ex.ExportError):
            ex.build_manifest(["a"], {"pictures": [{"id": "p1", "items": ["a"]}]}, {}, "/x", "latin", "1", 1)
        with self.assertRaises(ex.ExportError):
            ex.export("/nowhere", "../etc", 1, "1", "/tmp")


if __name__ == "__main__":
    unittest.main()

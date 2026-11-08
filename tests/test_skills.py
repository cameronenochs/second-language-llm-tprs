import glob
import os
import re
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")
SKILL_FILES = sorted(glob.glob(os.path.join(ROOT, ".agents", "skills", "*", "SKILL.md")))


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return dict(l.split(":", 1) for l in m.group(1).splitlines() if ":" in l) if m else {}


class SkillLintTests(unittest.TestCase):
    def test_skills_exist(self):
        self.assertTrue(SKILL_FILES, "no skills found")

    def test_claude_skills_symlink(self):
        link = os.path.join(ROOT, ".claude", "skills")
        self.assertTrue(os.path.islink(link), link)
        self.assertEqual(
            os.path.realpath(link),
            os.path.realpath(os.path.join(ROOT, ".agents", "skills")),
        )

    def test_frontmatter_matches_directory(self):
        for path in SKILL_FILES:
            fm = frontmatter(read(path))
            self.assertEqual(fm.get("name", "").strip(), os.path.basename(os.path.dirname(path)), path)
            self.assertTrue(fm.get("description", "").strip().startswith("Use when"), path)

    def test_no_secrets(self):
        for path in SKILL_FILES:
            text = read(path)
            self.assertIsNone(re.search(r"sk_[0-9a-f]{20,}|xi-api-key:\s*\S+", text), path)


def skill_text(name):
    return read(os.path.join(ROOT, ".agents", "skills", name, "SKILL.md"))


class StageGateTests(unittest.TestCase):
    def test_all_six_skills_present(self):
        names = {os.path.basename(os.path.dirname(p)) for p in SKILL_FILES}
        self.assertEqual(names, {
            "clean-source-text", "tprs-expand", "proofread-dialogue",
            "format-for-elevenlabs", "generate-dialogue-audio", "tprs-pipeline",
        })

    def test_audio_skill_gates(self):
        text = skill_text("generate-dialogue-audio")
        for needle in ("ELEVENLABS_API_KEY", "--limit 4", "test-4lines.mp3", "confirm"):
            self.assertIn(needle, text)
        self.assertNotIn("--api-key", text)

    def test_pipeline_collects_stage_questions_up_front(self):
        text = skill_text("tprs-pipeline")
        setup = text[text.index("## Setup"):text.index("## Stages")]
        self.assertIn("ACTFL", setup)
        self.assertIn("or-word", setup)

    def test_pipeline_gates(self):
        text = skill_text("tprs-pipeline")
        self.assertIn("Do I go full auto, or do you want to approve each stage?", text)
        for stage in ("clean-source-text", "tprs-expand", "proofread-dialogue",
                      "format-for-elevenlabs", "generate-dialogue-audio"):
            self.assertIn(stage, text)


if __name__ == "__main__":
    unittest.main()

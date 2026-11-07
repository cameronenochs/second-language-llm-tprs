import glob
import os
import re
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")
SKILL_FILES = sorted(glob.glob(os.path.join(ROOT, ".claude", "skills", "*", "SKILL.md")))


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return dict(l.split(":", 1) for l in m.group(1).splitlines() if ":" in l) if m else {}


class SkillLintTests(unittest.TestCase):
    def test_skills_exist(self):
        self.assertTrue(SKILL_FILES, "no skills found")

    def test_frontmatter_matches_directory(self):
        for path in SKILL_FILES:
            fm = frontmatter(read(path))
            self.assertEqual(fm.get("name", "").strip(), os.path.basename(os.path.dirname(path)), path)
            self.assertTrue(fm.get("description", "").strip().startswith("Use when"), path)

    def test_no_secrets(self):
        for path in SKILL_FILES:
            text = read(path)
            self.assertIsNone(re.search(r"sk_[0-9a-f]{20,}|xi-api-key:\s*\S+", text), path)


if __name__ == "__main__":
    unittest.main()

import glob
import json
import os
import re
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")
SECRET = re.compile(r"sk_[0-9a-f]{20,}|xi-api-key:\s*\S+")
SCAN_SUFFIXES = {".py", ".md", ".json", ".yml", ".yaml", ".txt"}


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


class RepoHygieneTests(unittest.TestCase):
    def test_gitignore_covers_secrets_and_output(self):
        text = read(os.path.join(ROOT, ".gitignore"))
        for needle in ("tprs.config.json", "output/", ".env", "*.pem", "*.key", "credentials.json"):
            self.assertIn(needle, text)

    def test_example_config_has_no_secret_fields(self):
        with open(os.path.join(ROOT, "tprs.config.example.json"), encoding="utf-8") as f:
            data = json.load(f)
        allowed = {"teacher_voice_id", "learner_voice_id", "narrator_voice_id", "default_model_id"}
        self.assertEqual(set(data), {"languages"})
        for entry in data["languages"].values():
            self.assertTrue(set(entry) <= allowed)
            self.assertNotIn("api_key", entry)

    def test_scripts_avoid_shell_and_api_key_flags(self):
        paths = glob.glob(os.path.join(ROOT, "scripts", "*.py"))
        self.assertTrue(paths)
        for path in paths:
            text = read(path)
            self.assertNotIn("shell=True", text, path)
            self.assertNotIn("eval(", text, path)
            self.assertNotIn("exec(", text, path)
            self.assertNotIn("--api-key", text, path)

    def test_tracked_text_has_no_secret_literals(self):
        hits = []
        for dirpath, dirnames, filenames in os.walk(ROOT):
            dirnames[:] = [
                d for d in dirnames
                if d not in {".git", "worktrees", "__pycache__", "output", "docs", "node_modules", ".vercel"}
            ]
            if os.path.basename(dirpath) == "tests":
                continue
            for name in filenames:
                if os.path.splitext(name)[1] not in SCAN_SUFFIXES:
                    continue
                path = os.path.join(dirpath, name)
                if SECRET.search(read(path)):
                    hits.append(path)
        self.assertEqual(hits, [])

    def test_security_policy_and_dependabot_exist(self):
        policy = read(os.path.join(ROOT, "SECURITY.md"))
        self.assertIn("security/advisories/new", policy)
        self.assertIn("ELEVENLABS_API_KEY", policy)
        dependabot = read(os.path.join(ROOT, ".github", "dependabot.yml"))
        self.assertIn("package-ecosystem: github-actions", dependabot)


class WorkflowSecurityTests(unittest.TestCase):
    def test_workflows_pin_actions_and_limit_permissions(self):
        files = sorted(glob.glob(os.path.join(ROOT, ".github", "workflows", "*.yml")))
        self.assertGreaterEqual(len(files), 3)
        names = set()
        for path in files:
            text = read(path)
            self.assertNotIn("pull_request_target", text, path)
            self.assertNotIn("contents: write", text, path)
            self.assertIn("permissions:", text, path)
            self.assertRegex(text, r"(?m)^permissions:\n  contents: read$", path)
            self.assertEqual(text.count("runs-on:"), text.count("timeout-minutes:"), path)
            for use in re.findall(r"^\s*uses:\s*(\S+)", text, re.M):
                self.assertRegex(use, r"@[0-9a-f]{40}$", f"{path}: {use}")
            self.assertIn("persist-credentials: false", text, path)
            names.add(os.path.basename(path))
        self.assertEqual(names, {"ci.yml", "codeql.yml", "dependency-review.yml"})

    def test_required_check_jobs_are_present(self):
        ci = read(os.path.join(ROOT, ".github", "workflows", "ci.yml"))
        self.assertIn("name: tests", ci)
        self.assertIn("name: gitleaks", ci)
        self.assertIn('python -m unittest discover -s tests -v', ci)
        self.assertIn("working-directory: app", ci)
        self.assertIn("needs: [unit, app]", ci)
        codeql = read(os.path.join(ROOT, ".github", "workflows", "codeql.yml"))
        self.assertIn("name: codeql", codeql)
        self.assertIn("queries: security-extended", codeql)
        review = read(os.path.join(ROOT, ".github", "workflows", "dependency-review.yml"))
        self.assertIn("name: dependency-review", review)


if __name__ == "__main__":
    unittest.main()

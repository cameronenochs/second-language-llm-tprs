# Second Language LLM TPRS Generator

This set of skills and tools allows you to turn a target language resource (a textbook chapter, a magazine article, etc.) into a spoken TPRS (Teaching Proficiency through Reading and Storytelling) circling dialogue. It produces a finished mp3.

## Prerequisites

- Python 3 (stdlib only, no pip installs)
- `ffmpeg` on PATH
- A subscription to Eleven Labs and an `ELEVENLABS_API_KEY` set as a variable in your shell.

## Skills

Project skills live in `.agents/skills/`. Codex, Grok, and Gemini CLI load that directory. Claude Code loads the same folders through the `.claude/skills` symlink. Shared rules are in `AGENTS.md`.

- `clean-source-text`: clean OCR noise from pasted text into `original.txt`.
- `tprs-expand`: expand the original into a Teacher/Learner circling dialogue at a chosen ACTFL level.
- `proofread-dialogue`: check grammar and circling rules, fixing the dialogue in place.
- `format-for-elevenlabs`: normalize delivery markers into `dialogue.elevenlabs.txt`.
- `generate-dialogue-audio`: render a 4-line test clip, then (after your confirmation) the full mp3.
- `tprs-pipeline`: run all five in order, in full-auto or approve-each-stage mode. The audio test clip always waits for you.

## Config

Copy `tprs.config.example.json` to `tprs.config.json` (gitignored) and fill in voice IDs per language, or let `generate-dialogue-audio` ask and save them. The file holds voice IDs and default model only, never the API key.

## Output layout

```
output/<source-slug>/<chapter-slug>/
  original.txt
  dialogue.txt
  dialogue.elevenlabs.txt
  test-4lines.mp3
  dialogue.mp3
```

`output/` is gitignored.

## Scripts

```bash
python3 scripts/tprs_config.py show --language latin
python3 scripts/format_dialogue.py IN OUT --or-word an
python3 scripts/tprs_audio.py IN.txt OUT.mp3 --language latin --limit 4
```

## Tests

```bash
python3 -m unittest discover -s tests -v
```

Pull requests into `main` must pass the `tests`, `gitleaks`, `codeql`, and `dependency-review` checks. Report vulnerabilities through [Security Advisories](https://github.com/cameronenochs/second-language-llm-tprs/security/advisories/new), not public issues.

## Not built yet

Cross-lesson vocabulary and grammar tracking (so later chapters can circle on earlier vocabulary) is a deferred v2 idea.

## License

MIT

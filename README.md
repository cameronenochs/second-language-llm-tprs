# Second Language LLM TPRS Generator

This set of skills and tools allows you to turn a target language resource (a textbook chapter, a magazine article, etc.) into a spoken TPRS (Teaching Proficiency through Reading and Storytelling) circling dialogue. It produces a finished mp3.

## Prerequisites

- Python 3 (stdlib only, no pip installs)
- `ffmpeg` on PATH
- A subscription to Eleven Labs and an `ELEVENLABS_API_KEY` set as a variable in your shell.
- An AI coding agent that reads `AGENTS.md` and skill folders: Claude Code, Codex, Gemini CLI, or Grok.

## Getting started

There is no input folder and no command to run. The skills are instructions for an AI agent, so you drive the pipeline by talking to the agent from the repo root.

1. Fork and clone the repo, then `cd` into it.
2. Export your key in the shell you will start the agent from: `export ELEVENLABS_API_KEY=...`. Do not paste the key into the chat.
3. Pick two ElevenLabs voices (teacher and learner) and note their voice IDs. You can put them in `tprs.config.json` now (see [Config](#config)), or give them to the agent when it asks.
4. Get your chapter as text. Either copy it so you can paste it, or save it as a `.txt` file. Put the file outside the repo or under `output/` (gitignored), so it is not committed. A PDF also works if your agent can read PDFs (Claude Code can). For a scanned PDF with no text layer, run OCR first.
5. Start the agent in the repo root (for example `claude`, `codex`, or `gemini`).
6. Ask it to run the pipeline, for example:

   > Run the tprs-pipeline on ~/Downloads/chapter3.txt. Latin, source slug `wheelock`, chapter slug `ch03-taberna`.

7. Answer its setup questions: full auto or approve each stage, the ACTFL level, and the language's word for "or" (for example `an` in Latin).
8. Listen to `test-4lines.mp3` when the agent stops. Confirm, and it renders `dialogue.mp3`. The test clip exists so you can check the voices before you pay for the full render.

All files land in `output/<source-slug>/<chapter-slug>/`. To resume later, ask the agent to run the next stage on that folder. You can also run any single stage by name, for example "proofread `output/wheelock/ch03-taberna/dialogue.txt`".

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

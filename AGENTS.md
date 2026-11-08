# Second Language LLM TPRS

Turn a source-language chapter into a spoken TPRS circling dialogue and a finished mp3.

## Skills

Procedures live in `.agents/skills/`. Run the matching skill. Do not improvise a stage the skill already defines. The working directory is the repo root.

- `clean-source-text` writes `original.txt`.
- `tprs-expand` writes `dialogue.txt` at a chosen ACTFL level.
- `proofread-dialogue` edits `dialogue.txt` in place.
- `format-for-elevenlabs` writes `dialogue.elevenlabs.txt`.
- `generate-dialogue-audio` writes `test-4lines.mp3`, then `dialogue.mp3` only after the user confirms the clip.
- `tprs-pipeline` runs the five in order. Ask full-auto or approve-each-stage first. The 4-line audio clip still waits for confirmation.

## Output

```
output/<source-slug>/<chapter-slug>/
  original.txt
  dialogue.txt
  dialogue.elevenlabs.txt
  test-4lines.mp3
  dialogue.mp3
```

## Secrets

Read `ELEVENLABS_API_KEY` from the environment only. Never ask for it in chat, and never write it into `tprs.config.json` or the repo. If a key appears in chat, tell the user to rotate it.

## Tools

Python 3 stdlib only. `ffmpeg` must be on `PATH`. Voice IDs live in gitignored `tprs.config.json` (see `tprs.config.example.json`).

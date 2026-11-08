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

Audiobook pipeline (straight single-voice reading, no expansion):

- `adapt-reading-level` writes `adapted.txt`, only if the user wants a level change.
- `format-for-narration` writes `reading.elevenlabs.txt`.
- `generate-reading-audio` writes `test-4lines.mp3`, then `reading.mp3` only after the user confirms the clip.
- `audiobook-pipeline` runs `clean-source-text` (skipped for reliable text) and the three above in order. Ask full-auto or approve-each-stage first.

Course pipeline (Winitz/Buth picture course, one sentence per picture, built from `../Course-Builder-Kit` or `$COURSE_BUILDER_KIT`):

- `write-course-script` writes `script.jsonl`, `plan.md`, `lexicon.csv`, `deviations.md`, gated by the kit's `check_course.py`.
- `proofread-course-script` edits `script.jsonl` in place.
- `design-course-pictures` writes `pictures.json` and `style.md`.
- `generate-course-images` writes `cast.png` and `sheets/sheet-01.png`, then the other sheets only after the user confirms sheet 1, then cuts `pictures/`. Gemini if `GEMINI_API_KEY`, else Grok if `XAI_API_KEY`, else manual paste-in.
- `generate-course-audio` writes `test-4lines.mp3`, then `audio/` only after the user confirms the clip.
- `export-course-to-app` copies the lesson into `app/` (the web player).
- `course-pipeline` runs the six in order. Ask full-auto or approve-each-stage first. Sheet 1 and the 4-line clip still wait for confirmation.

## Output

```
output/<source-slug>/<chapter-slug>/
  original.txt
  dialogue.txt
  dialogue.elevenlabs.txt
  test-4lines.mp3
  dialogue.mp3
  adapted.txt            (audiobook, optional)
  reading.elevenlabs.txt (audiobook)
  reading.mp3            (audiobook)

output/course-<language>/L<level>-<NN>/
  script.jsonl plan.md lexicon.csv deviations.md
  pictures.json style.md cast.png
  sheets/sheet-NN.png sheets/prompts.md
  pictures/<picture-id>.png
  audio/<hash>.mp3 audio/index.json
  test-4lines.mp3
```

## Secrets

Read `ELEVENLABS_API_KEY`, `GEMINI_API_KEY`, and `XAI_API_KEY` from the environment only. Never ask for it in chat, and never write it into `tprs.config.json` or the repo. If a key appears in chat, tell the user to rotate it.

## Tools

Python 3 stdlib only, except `app/` (Node 22 web player). `ffmpeg` must be on `PATH`. Voice IDs live in gitignored `tprs.config.json` (see `tprs.config.example.json`).

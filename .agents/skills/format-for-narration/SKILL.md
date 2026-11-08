---
name: format-for-narration
description: Use when original.txt (or adapted.txt) must become reading.elevenlabs.txt, a single-narrator ElevenLabs script with pause and expression markers.
---

# Format for Narration

Turn the text into `reading.elevenlabs.txt` for one narrator. Assumes the working directory is the repo root.

## Input

`adapted.txt` if it exists in the chapter directory, otherwise `original.txt`.

## Steps

1. Get the language (ask if unknown). Run `python3 scripts/tprs_config.py show --language <language> --mode reading`. Read `entry.default_model_id`; if empty, use `eleven_v4`.
2. Copy the input to `<chapter-dir>/reading.elevenlabs.txt`, one paragraph per line, and insert markers:
   - `[pause]` at clause and sentence boundaries where a reader would breathe, and a longer beat (`[pause] [pause]`) between paragraphs of different topic.
   - `[slowly]` before a hard or important phrase, sparingly.
3. Normalize in place:
   `python3 scripts/format_dialogue.py <chapter-dir>/reading.elevenlabs.txt <chapter-dir>/reading.elevenlabs.txt --reading --model <model_id>`
4. Check: with markers stripped, the words equal the input. Report the marker counts.

## Rules

- Never change, add, or drop a word. Only add markers.
- No `Teacher:` or `Learner:` prefixes. Keep each line short; the audio stage sends one line per request.

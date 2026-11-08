---
name: format-for-elevenlabs
description: Use when a proofread Teacher/Learner dialogue.txt must be normalized into dialogue.elevenlabs.txt for the ElevenLabs audio script.
---

# Format for ElevenLabs

Mechanical transform from `dialogue.txt` to `dialogue.elevenlabs.txt`. Assumes the working directory is the repo root.

This stage is separate from `tprs-expand` on purpose: ElevenLabs delivery conventions change independently of the pedagogy, so a convention change never means re-touching dialogue content.

## Steps

1. Get the active language (ask if unknown). Run:
   `python3 scripts/tprs_config.py show --language <language>`
   Read `entry.default_model_id`. If empty, use `eleven_v4`.
2. Get the language's or-word (Latin `an`, Italian `o`, and so on). Reuse the one `tprs-expand` reported; otherwise ask.
3. Run:
   `python3 scripts/format_dialogue.py <chapter-dir>/dialogue.txt <chapter-dir>/dialogue.elevenlabs.txt --or-word <word> --model <model_id>`
4. Report line count and which markers were removed (compare marker sets in the two files).

## Rules

- Do not hand-edit dialogue content. If the script's output looks wrong, report the problem and stop; do not patch the output by hand.
- The script keeps `[pause]` and `[slowly]`, removes other bracket markers, puts `, [pause]` before the or-word in questions, and normalizes whitespace.
- If the audio stage later runs with a different model than this stage used, `generate-dialogue-audio` warns; it does not force a re-run of this stage.

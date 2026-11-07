---
name: generate-dialogue-audio
description: Use when a formatted dialogue.elevenlabs.txt must be rendered to mp3 with ElevenLabs, including the mandatory 4-line test clip before the full render.
---

# Generate Dialogue Audio

Render `dialogue.elevenlabs.txt` to `dialogue.mp3`. Assumes the working directory is the repo root. The full render spends real ElevenLabs quota, so the test-clip pause below is never skipped, in any mode, including full auto.

## Steps

1. **Language and config.** Get the language key (ask if unknown). Run `python3 scripts/tprs_config.py show --language <language>`. If `missing` is not empty, ask the user for exactly those values and offer to save them with `python3 scripts/tprs_config.py set --language <language> teacher_voice_id=<id> learner_voice_id=<id> default_model_id=<model>`. Never ask for, accept, or save an API key.
2. **API key check.** Run `[ -n "$ELEVENLABS_API_KEY" ] && echo set || echo unset`. Never print the value. If unset, tell the user to export `ELEVENLABS_API_KEY` in their own shell and stop. If a string that looks like a key appears in chat, tell the user to rotate that key, and do not use it.
3. **Model.** Defaults to the config's `default_model_id` (`eleven_v4`). A per-run override is allowed with `--model <id>`; the script warns when it differs from the default the dialogue was formatted for.
4. **Test clip, always.** Run:
   `python3 scripts/tprs_audio.py <chapter-dir>/dialogue.elevenlabs.txt <chapter-dir>/test-4lines.mp3 --language <language> --limit 4`
   Ask the user to listen to `test-4lines.mp3` and explicitly confirm before continuing. No confirmation means no full render.
5. **Full render, only after confirm.** Run:
   `python3 scripts/tprs_audio.py <chapter-dir>/dialogue.elevenlabs.txt <chapter-dir>/dialogue.mp3 --language <language>`
   Report the script's error text verbatim on failure (401 means the key was rejected, 402 means a plan or credits issue). Do not retry in a loop.

## Redo

To regenerate after hand-editing the dialogue, run steps 4-5 again; no earlier stage needs to re-run.

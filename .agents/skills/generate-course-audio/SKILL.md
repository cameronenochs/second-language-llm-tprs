---
name: generate-course-audio
description: Use when a course script.jsonl must be rendered to one ElevenLabs clip per item, including the mandatory 4-line test clip before the full render.
---

# Generate Course Audio

Render every distinct item text to its own mp3 in `<lesson-dir>/audio/`, plus `audio/index.json` mapping item ids to clips. Assumes the working directory is the repo root. The full render spends real ElevenLabs quota, so the test-clip pause is never skipped, in any mode.

## Steps

1. **Language and config.** Run `python3 scripts/tprs_config.py show --language <language> --mode course`. If `missing` is not empty, ask the user for exactly those values and offer to save them with `python3 scripts/tprs_config.py set --language <language> narrator_voice_id=<id> default_model_id=<model>`. Never ask for, accept, or save an API key.
2. **API key check.** Run `[ -n "$ELEVENLABS_API_KEY" ] && echo set || echo unset`. Never print the value. If unset, tell the user to export `ELEVENLABS_API_KEY` in their own shell and stop. If a string that looks like a key appears in chat, tell the user to rotate it and do not use it.
3. **Test clip, always.** Run:
   `python3 scripts/tprs_audio.py <lesson-dir>/script.jsonl <lesson-dir>/audio --mode course --language <language> --limit 4 --join <lesson-dir>/test-4lines.mp3`
   This renders the first 4 distinct sentences. Ask the user to listen to `test-4lines.mp3` and explicitly confirm before continuing. No confirmation means no full render. If they change voice or model, delete `<lesson-dir>/audio/` first.
4. **Full render, only after confirm.** Run:
   `python3 scripts/tprs_audio.py <lesson-dir>/script.jsonl <lesson-dir>/audio --mode course --language <language>`
   Report the script's error text verbatim on failure (401 key rejected, 402 plan or credits). Do not retry in a loop. Re-running reuses clips already rendered.

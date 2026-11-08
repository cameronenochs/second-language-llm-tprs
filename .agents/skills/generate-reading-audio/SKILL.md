---
name: generate-reading-audio
description: Use when a formatted reading.elevenlabs.txt must be rendered to mp3 by one ElevenLabs narrator voice, including the mandatory 4-line test clip before the full render.
---

# Generate Reading Audio

Render `reading.elevenlabs.txt` to `reading.mp3`. Assumes the working directory is the repo root. The full render spends real ElevenLabs quota, so the test-clip pause is never skipped, in any mode.

## Steps

1. **Language and config.** Get the language key (ask if unknown). Run `python3 scripts/tprs_config.py show --language <language> --mode reading`. If `missing` is not empty, ask the user for exactly those values and offer to save them with `python3 scripts/tprs_config.py set --language <language> narrator_voice_id=<id> default_model_id=<model>`. Never ask for, accept, or save an API key.
2. **API key check.** Run `[ -n "$ELEVENLABS_API_KEY" ] && echo set || echo unset`. Never print the value. If unset, tell the user to export `ELEVENLABS_API_KEY` in their own shell and stop. If a string that looks like a key appears in chat, tell the user to rotate it and do not use it.
3. **Model.** Defaults to the config's `default_model_id` (`eleven_v4`). Offer the user a different model; pass it with `--model <id>`.
4. **Test clip, always.** Run:
   `python3 scripts/tprs_audio.py <chapter-dir>/reading.elevenlabs.txt <chapter-dir>/test-4lines.mp3 --mode reading --language <language> --limit 4`
   Ask the user to listen and explicitly confirm before continuing. No confirmation means no full render.
5. **Full render, only after confirm.** Run:
   `python3 scripts/tprs_audio.py <chapter-dir>/reading.elevenlabs.txt <chapter-dir>/reading.mp3 --mode reading --language <language>`
   Report the script's error text verbatim on failure (401 key rejected, 402 plan or credits). Do not retry in a loop.

Failed renders keep clips in `<output>.parts/`; re-running the same command reuses unchanged clips.

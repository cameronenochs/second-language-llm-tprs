---
name: audiobook-pipeline
description: Use when turning a source-language chapter into a straight single-narrator mp3 reading (an audiobook), with no dialogue or expansion.
---

# Audiobook Pipeline

Orchestrates the reading stages for one chapter. Assumes the working directory is the repo root. The text is read as written, by one voice.

## First question

Ask the user, verbatim: **Do I go full auto, or do you want to approve each stage?**

## Setup

1. Get the source: pasted text, typed text, or a file path. Get the source language, a source slug, and a chapter slug.
2. Ask whether the text is already reliable (a clean file). If yes, copy it to `original.txt` and skip stage 1.
3. Ask now, once: should the reading be simplified to a different ACTFL level, and which level? Also ask which ElevenLabs model (default `eleven_v4`).
4. Create `output/<source-slug>/<chapter-slug>/`.

## Stages

1. `clean-source-text` produces `original.txt` (skipped for reliable text).
2. `adapt-reading-level` produces `adapted.txt`, only if the user wants a level change.
3. `format-for-narration` produces `reading.elevenlabs.txt`.
4. `generate-reading-audio` produces `test-4lines.mp3`, then `reading.mp3`.

## Modes

- **Approve mode.** After stages 1-3, show the result and ask: approve, reject with feedback, or abort. On reject, re-run the stage with the feedback.
- **Full auto mode.** Run stages 1-3 without stopping. Stage 4 still stops at the 4-line test clip and waits for explicit confirmation before the full render.

## Secrets

The ElevenLabs key is read from `ELEVENLABS_API_KEY` in the environment only. Never ask for it in chat.

---
name: tprs-pipeline
description: Use when turning a fresh source-language chapter into a finished TPRS dialogue mp3 end to end, chaining cleaning, expansion, proofreading, formatting, and audio generation.
---

# TPRS Pipeline

Orchestrates the five stage skills for one chapter. Assumes the working directory is the repo root.

## First question

Before anything else, ask the user, verbatim:

**Do I go full auto, or do you want to approve each stage?**

## Setup

1. Get the source text (pasted or a file path), the source language, a source slug (one per book/course), and a chapter slug.
2. Ask now, once, the questions later stages would otherwise stop to ask: the target ACTFL level (for `tprs-expand`) and the language's or-word (for `format-for-elevenlabs`). Pass the answers to those stages so full auto does not pause mid-run.
3. Create `output/<source-slug>/<chapter-slug>/`. Every artifact from this run goes inside it: `original.txt`, `dialogue.txt`, `dialogue.elevenlabs.txt`, `test-4lines.mp3`, `dialogue.mp3`.

## Stages

Run these skills in order. Pass the chapter directory to each one:

1. `clean-source-text` produces `original.txt`.
2. `tprs-expand` produces `dialogue.txt` (it asks for the ACTFL level).
3. `proofread-dialogue` edits `dialogue.txt` in place.
4. `format-for-elevenlabs` produces `dialogue.elevenlabs.txt`.
5. `generate-dialogue-audio` produces `test-4lines.mp3`, then `dialogue.mp3`.

## Modes

- **Approve mode.** After each of stages 1-4, show the result and ask: approve, reject with feedback, or abort. On reject, re-run the same stage with the user's correction notes as extra input (for example "make this Intermediate-Mid, not Novice-High"), show it again, and repeat. On abort, stop and leave the files as they are.
- **Full auto mode.** Run stages 1-4 without stopping. Stage 5 still stops at the 4-line test clip and waits for the user's explicit confirmation before the full render. Say so when the run reaches it. Audio spend is the one pause that never goes away.

## Resuming

There is no state file. Each stage's output is already on disk in the chapter directory. To resume in a later session, point the next stage's skill at the existing file.

## Secrets

The ElevenLabs key is read from `ELEVENLABS_API_KEY` in the environment only. Never ask for it in chat. If one appears in chat, tell the user to rotate it.

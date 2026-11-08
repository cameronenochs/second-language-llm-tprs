---
name: course-pipeline
description: Use when building a Comprehension Method picture-and-audio course lesson end to end, from script to pictures, audio, and the app/ web player.
---

# Course Pipeline

Orchestrates one lesson of a Winitz/Buth-style picture course. Assumes the working directory is the repo root.

## First question

Ask the user, verbatim: **Do I go full auto, or do you want to approve each stage?**

## Setup

1. Ask for the target language, plus its variety, period, and spelling convention. Ask for the level and lesson (default Level 1, lesson 1).
2. Ask for an optional source text to shape the world and vocabulary.
3. Check that the kit is present at `${COURSE_BUILDER_KIT:-../Course-Builder-Kit}`.
4. Run `python3 scripts/course_pictures.py provider` and tell the user which image provider will be used. Run `python3 scripts/tprs_config.py show --language <language> --mode course` and collect any missing voice values now.
5. Create `output/course-<language>/L<level>-<NN>/`.

## Stages

1. `write-course-script` produces `script.jsonl`, `plan.md`, `lexicon.csv`, `deviations.md`.
2. `proofread-course-script` fixes `script.jsonl` in place.
3. `design-course-pictures` produces `pictures.json` and `style.md`.
4. `generate-course-images` produces `cast.png`, `sheets/sheet-01.png`, then the remaining sheets and `pictures/`.
5. `generate-course-audio` produces `test-4lines.mp3`, then `audio/`.
6. `export-course-to-app` copies the lesson into `app/`.

## Modes

- **Approve mode.** After stages 1-3 and 6, show the result and ask: approve, reject with feedback, or abort. On reject, re-run the stage with the feedback.
- **Full auto mode.** Run stages 1-3 and 6 without stopping. Stage 4 still stops at `sheet-01.png`, and stage 5 still stops at the 4-line test clip. Both wait for explicit confirmation.

## Secrets

Keys are read from the environment only: `ELEVENLABS_API_KEY`, `GEMINI_API_KEY`, `XAI_API_KEY`. Never ask for them in chat.

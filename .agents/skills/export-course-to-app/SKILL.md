---
name: export-course-to-app
description: Use when a lesson folder with tiles in pictures/ and clips in audio/ must be copied into the app/ web player and checked there.
---

# Export Course to App

Copy one finished lesson into `app/` and play it. Assumes the working directory is the repo root.

## Steps

1. Run `python3 scripts/export_course.py <lesson-dir> --language <language> --lesson <N>`. It copies the used pictures and clips into `app/public/courses/<language>/L1-<NN>/` and writes `app/src/lesson/content/<language>-L1-<NN>.json`. Both are gitignored.
2. In `app/`, run `npm install` once, then `npm test`.
3. Start the player with `npm run dev` in `app/` (port 8080). Open the new step under its level, play a few rounds, and use the round grid to spot-check the middle and the end. Every round must show a picture and play audio.
4. Report the step's name and any round that failed.

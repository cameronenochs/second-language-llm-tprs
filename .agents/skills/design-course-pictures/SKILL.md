---
name: design-course-pictures
description: Use when a proofread course script.jsonl needs its distinct pictures grouped into 3x2 sheets and a fixed drawing style and cast written, before any images are generated.
---

# Design Course Pictures

Turn the script's scenes into a picture plan and a style guide. Assumes the working directory is the repo root.

## Steps

1. Run `python3 scripts/course_pictures.py plan <lesson-dir>/script.jsonl <lesson-dir>`. This writes `pictures.json`: one picture per distinct `scene`, six per sheet, in order of first appearance. Report the picture and sheet counts.
2. Write `<lesson-dir>/style.md`, a block that goes at the top of every image prompt:
   - The style: simple black line drawing on a plain white background, clean outlines, no shading or only light flat grey, no text, letters, or numbers anywhere in the picture.
   - The world and period of the course (from `plan.md` and `deviations.md`).
   - **Cast.** One fixed line per recurring person or animal: age, build, hair, clothing, one distinguishing item. Use the same wording every time. Later lessons reuse the first lesson's `style.md` unchanged and only add new cast lines.
3. Read every `scene` in `pictures.json`. A scene that one drawing cannot show unambiguously goes back to `proofread-course-script` for a fix. Do not edit `pictures.json` by hand.

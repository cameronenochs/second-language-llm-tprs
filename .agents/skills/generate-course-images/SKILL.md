---
name: generate-course-images
description: Use when a lesson's pictures.json and style.md must become picture tiles, through Gemini, Grok, or manual paste-in, including the mandatory sheet-01.png style check before the rest.
---

# Generate Course Images

Produce `cast.png`, the sheets, and the cut tiles in `pictures/`. Assumes the working directory is the repo root. Image calls spend real quota, so the sheet-1 pause is never skipped, in any mode.

## Steps

1. **Provider.** Run `python3 scripts/course_pictures.py provider`. It prints `gemini` if `GEMINI_API_KEY` is set, else `grok` if `XAI_API_KEY` is set, else `manual`. Never print, ask for, or accept a key in chat. If a key appears in chat, tell the user to rotate it. The user may force one with `--provider`.
2. **Manual provider.** Run `python3 scripts/course_pictures.py prompts <lesson-dir>`. Tell the user to open `<lesson-dir>/sheets/prompts.md`, generate each image in their tool, and save it under the name in its heading (`cast.png` in the lesson folder, `sheet-01.png` and so on in `sheets/`). Attach `cast.png`, and `sheet-01.png` once approved, as reference images where the tool allows. Wait until the user says the files are there, then continue at step 5.
3. **Cast and sheet 1.** Run `python3 scripts/course_pictures.py render <lesson-dir> --cast`, then `python3 scripts/course_pictures.py render <lesson-dir> --sheet 1`, then `python3 scripts/course_pictures.py cut <lesson-dir> --sheet 1`.
4. **Style check, always.** Show the user `cast.png`, `sheets/sheet-01.png`, and the tiles from sheet 1. Ask them to explicitly confirm the style, cast, and cut before continuing. On rejection, edit `style.md` with their feedback and redo step 3. No confirmation means no further sheets.
5. **The rest, only after confirm.** Run `python3 scripts/course_pictures.py render <lesson-dir> --rest` (API providers), then `python3 scripts/course_pictures.py cut <lesson-dir>`.
6. **Review.** Look at every tile. For a wrong picture, a picture with text in it, or a bad cut, delete that sheet's png and run `render <lesson-dir> --sheet N` and `cut <lesson-dir> --sheet N` again. Report the script's error text verbatim on failure. Do not retry in a loop.

Model overrides: `GEMINI_IMAGE_MODEL`, `XAI_IMAGE_MODEL`.

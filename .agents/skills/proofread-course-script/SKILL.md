---
name: proofread-course-script
description: Use when a course script.jsonl needs a second pass for target-language correctness and picture consistency, right after write-course-script or on any existing lesson.
---

# Proofread Course Script

Check `script.jsonl` in a lesson folder and fix it in place. Assumes the working directory is the repo root.

## Checks

1. **Language correctness.** Grammar, agreement, spelling convention, and natural word choice for the stated variety and period.
2. **Picturable.** Every `text` can be shown by the single drawing its `scene` describes. Meaning must come from the picture, never from a translation.
3. **Scene consistency.** Items meant to share a picture have identical `scene` strings. Different pictures never share a `scene`. Exact repeats of `text` share a `scene`.
4. **Lemmas.** Every word in `text` has its dictionary form in `lemmas`, spelled the same way everywhere.
5. **Pages.** Each page has slots 1 to 6 once, and its six items belong together (naming set, minimal pairs, frame drill, or story strip).

## Limits

Make the minimum change that fixes each problem. List every change as `id: before -> after (reason)`. Then re-run `python3 "${COURSE_BUILDER_KIT:-../Course-Builder-Kit}/tools/check_course.py" <lesson-dir>/script.jsonl --level 1 --partial` and show the result.

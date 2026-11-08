---
name: write-course-script
description: Use when a Comprehension Method picture course lesson needs its target-language script written from the Course-Builder-Kit scaffold, before any pictures or audio.
---

# Write Course Script

Write one lesson of a Comprehension Approach picture course: one sentence per picture, six items per page. Assumes the working directory is the repo root. Works for any language the model knows well.

## Inputs

- **Kit.** The Course-Builder-Kit folder: `$COURSE_BUILDER_KIT`, default `../Course-Builder-Kit`. Stop if `PROMPT.md` is not there.
- **Language** and its variety, period, and spelling convention (the kit's `PROMPT.md` parameters). Ask if unknown.
- **Level and lesson.** Default: Level 1, lesson 1.
- **Optional source text.** It shapes the world and vocabulary through the kit's "world substitution" rule (keep picture roles, change the objects). It never adds items.

Write to `output/course-<language>/L<level>-<NN>/` (for example `output/course-latin/L1-01/`).

## Steps

1. Read, in full: the kit's `PROMPT.md`, `BRIEF.md`, `FEATURE_MAP.md`, then lesson 1 of `transcripts/learnables_L1.txt`. For later lessons, also read the lessons before it in this repo's `output/course-<language>/`, so vocabulary carries over.
2. Follow `PROMPT.md` method A for this lesson only. Take the lesson's rows from `data/scaffold_level1.jsonl`, in order, and keep each scaffold `id`.
3. Write `script.jsonl`. Each line is one item with `id`, `lesson`, `page`, `slot`, `text`, `lemmas`, `constructions`, `scene`.
   - `text` is in the target language only.
   - `scene` is English, at most 12 words, and drawable as one simple line drawing.
   - Items that reuse a picture get **exactly the same** `scene` text. This is what groups them onto one picture.
   - An item with `repeats_item` in the scaffold gets the same `text` and the same `scene` as that item.
4. **Vocabulary rule.** For each meaning, use the most frequent standard lemma. If `python3 scripts/core_vocab.py fetch --language <language>` has a source for the language, pick the highest-ranked word on that list. Never prefer a late, regional, or Romance-ancestor form over its core word: for Latin, domus not casa, malum not pomum, edo not manduco, equus not caballus. A concrete object the list lacks may use the plainest standard word for it. Write sentences in plain, conversational style (for Latin: the everyday speech of Plautus, Terence, or Petronius's freedmen), never periodic or oratorical prose.
5. Write `plan.md` (from `examples/plan_template.md`), `lexicon.csv`, and `deviations.md`, as `PROMPT.md` describes.
6. **Gate.** Run `python3 "$COURSE_BUILDER_KIT/tools/check_course.py" <lesson-dir>/script.jsonl --level 1 --partial`. Fix every FAIL and as many WARN lines as the language allows, then re-run. Show the final output to the user.
7. **Core-list gate**, when the language has a list. Run `python3 scripts/core_vocab.py check <lesson-dir>/script.jsonl --language <language>`. For each OFF-LIST lemma, swap in a listed word with the same picture meaning. If none exists, keep the word and log it in `deviations.md` with the reason.

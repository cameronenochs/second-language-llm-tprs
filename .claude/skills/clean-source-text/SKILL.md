---
name: clean-source-text
description: Use when the user has pasted or typed a source-language chapter, possibly with OCR noise, and it needs to be cleaned and proofread into original.txt before TPRS expansion.
---

# Clean Source Text

Turn raw source text into a clean, proofread `original.txt`. Assumes the working directory is the repo root.

## Input

Pasted text or a file path. If not already known, ask for: the source language, a source slug (one per book/course, e.g. `wheelock`), and a chapter slug (e.g. `ch03-taberna`).

## Output

`output/<source-slug>/<chapter-slug>/original.txt` (create the directories). Save the cleaned text only, no commentary inside the file.

## What to fix

- Line-number remnants (stray digits at line starts or ends, margin numbering).
- Hyphenated line-break artifacts: rejoin `ambu-\nlare` as `ambulare`.
- Obviously scan-garbled words (wrong glyphs such as `rn` for `m`, `l` for `I`, dropped diacritics where the language uses them).
- Broken paragraph breaks and doubled whitespace.

## What never to change

Do not modernize spelling, paraphrase, shorten, add content, or "improve" the author's wording. Cleaning restores the text; it does not rewrite it.

## Process

1. Fix in place, then write the file.
2. After writing, list every non-trivial correction (garbled-word fixes, rejoined hyphenations that were ambiguous) as `before -> after` so the user can veto any of them.
3. If a garbled word has more than one plausible reading, do not guess: ask the user which is right before saving.

Next stage: `tprs-expand`, pointed at the same chapter directory.

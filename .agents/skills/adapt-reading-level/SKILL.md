---
name: adapt-reading-level
description: Use when an audiobook reading of original.txt should be simplified to a chosen ACTFL level; skipped unless the user says yes.
---

# Adapt Reading Level

Optionally rewrite `original.txt` at a lower ACTFL level for a straight reading. Assumes the working directory is the repo root.

## First action

Ask the user, verbatim: **Should the reading be simplified to a different ACTFL level? If yes, which level?** If the answer is no, write nothing and stop; the next stage reads `original.txt`.

## Steps

1. Read `actfl-levels.md` in `../tprs-expand/` and apply the chosen row to sentence length, grammar, and vocabulary.
2. Write `output/<source-slug>/<chapter-slug>/adapted.txt`.

## Rules

- Keep the order, content, and paragraphs of the original. No added explanation, no dialogue, no expansion. Length stays close to the original.
- Simplify only wording and syntax. Every fact in `original.txt` appears in `adapted.txt`.
- After writing, list the non-trivial rewrites as `before -> after`.

Next stage: `format-for-narration`.

---
name: tprs-expand
description: Use when a cleaned source-language chapter (original.txt) needs to be expanded into a TPRS circling Teacher/Learner dialogue at a chosen ACTFL level.
---

# TPRS Expand

Rewrite `original.txt` as a spoken TPRS circling dialogue in the source language. Assumes the working directory is the repo root.

## Input and output

- Input: `output/<source-slug>/<chapter-slug>/original.txt`.
- Output: `dialogue.txt` in the same directory.

## First action

Ask the user which ACTFL level to target (Novice Low/Mid/High, Intermediate Low/Mid/High). Do not write anything before the answer. Then read `.claude/skills/tprs-expand/actfl-levels.md` and apply that row to sentence length, grammar, vocabulary load, question types, and restatement.

## Requirements

- Length: roughly 2-3 times `original.txt`. Every fact in the original must appear in the dialogue.
- Format: lines start with `Teacher:` or `Learner:`. Two speakers only. Write `[pause]` and `[slowly]` markers while expanding, not afterward.
- Use the source language's own words for "or", fillers, confirmation, and "I don't understand". Do not borrow Latin words for another language.

## TPRS circling rules

1. A question testing content just narrated in the same breath must be either/or, giving both options aloud, because audio-only learners cannot glance at text. Example: `Teacher: Venditne Albinus gemmas, [pause] an libros?`
2. A question about content established earlier (not the immediately preceding sentence) may be plain yes/no or an open wh-question. Example: `Teacher: Quid in taberna est?` The listener is recalling, not parsing cold.
3. Do not force an either/or where there is no natural second option, such as pure presence or absence facts. Example: `Teacher: Suntne lacrimae in oculis eius?` Leave these as yes/no.
4. Give Learner lines occasional fillers (`Mmm...`, `Ahh...`, `Ummm`), `[pause]` markers, and confident-recognition tags (`Novi!`). Add a handful of "Non intellego" or clarification-request moments at genuinely hard spots (new grammatical case, unfamiliar verb), each followed by the Teacher re-explaining more simply before the Learner gets it right.
5. Teacher confirms a correct answer before restating. Example: `Teacher: Ita! Haec taberna Romana est...` Never re-assert the fact cold.
6. Put `[pause]` before the or-word in every either/or question, every time.
7. Learner answers are full-verb phrases, not bare nouns. Write `Vendit gemmas, non libros`, not `Gemmas`.

## Finish

Save `dialogue.txt`. In the final chat message, state the or-word you used (for example `an`) so `format-for-elevenlabs` can reuse it.

## Redo with feedback

If invoked again with correction notes (for example "make this Intermediate-Mid, not Novice-High"), regenerate `dialogue.txt` from `original.txt` honoring the notes.

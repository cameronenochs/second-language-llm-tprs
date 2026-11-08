---
name: proofread-dialogue
description: Use when a TPRS Teacher/Learner dialogue file needs a second pass for source-language correctness and circling-rule compliance, either right after tprs-expand or standalone on any existing dialogue file.
---

# Proofread Dialogue

Check a dialogue file and fix it in place. Assumes the working directory is the repo root.

## Input and output

Input: a dialogue file path. Default: `dialogue.txt` in the current chapter directory (`output/<source-slug>/<chapter-slug>/`). If `original.txt` sits beside it, read it too.

Edit the file in place, then list every change you made as `line: before -> after (reason)`.

## Checks

For each item, find violations and fix them:

1. **Language correctness.** Grammar, agreement, vocabulary, and spelling in the source language.
2. **Real either/or.** Every either/or question offers two real, distinguishable options. Replace a distractor that is absurd, synonymous, or identical to the answer.
3. **No cold open questions.** A question that immediately follows brand-new information must be either/or. An open wh-question or bare yes/no right after new information is a violation: rewrite it as either/or.
4. **No forced either/or.** Where there is no natural second option (presence or absence facts), the question stays yes/no. Remove invented distractors.
5. **Pause before the or-word.** Every either/or has `[pause]` immediately before the or-word.
6. **Teacher confirms first.** After a correct Learner answer, the Teacher confirms (for example `Ita!`) before restating the fact.
7. **Full-verb answers.** Learner answers are full-verb phrases, not bare nouns.
8. **Natural fillers.** Fillers, recognition tags (`Novi!`), and clarification requests (`Non intellego`) feel natural. Flag and vary runs of the same filler; each clarification request must sit at a genuinely hard spot and be followed by a simpler Teacher re-explanation.
9. **Level consistency.** If the ACTFL level is known, sentence length and grammar match `.agents/skills/tprs-expand/actfl-levels.md`.

## Limits

Make the minimum change that fixes each problem. Fix a word, not a whole turn, when a word is enough. Never alter facts from `original.txt`. Never add or remove speakers. Keep `[pause]` and `[slowly]` markers intact.

# TPRS Dialogue Pipeline — Design

## Intent and why

Turning a textbook chapter into a spoken TPRS (Teaching Proficiency through
Reading and Storytelling) practice dialogue is currently a manual, multi-hour
chat session: clean the source text, expand it into a circling Q&A dialogue,
reformat it with TTS delivery markers, then call the ElevenLabs API and stitch
the result into one audio file. This was done once by hand (for a Latin
chapter, "Taberna Romana") in a prior session and worked well, but repeating
it from scratch each time wastes tokens and loses hard-won judgment calls
(what makes a good either/or comprehension question, how to mark pauses,
how to avoid spoiling the ElevenLabs API key in chat, etc).

This project captures that workflow as a set of Claude Code skills so it is
repeatable, inspectable, and partially or fully automatable for any source
language, not just Latin.

## Goals

- Turn a pasted/typed source-language chapter into a finished TPRS dialogue
  mp3 with minimal manual steps.
- Make each pipeline stage usable on its own (e.g. regenerate audio after
  hand-editing a dialogue file, without re-running the whole pipeline).
- Encode the TPRS circling discipline worked out in the prior session
  (see "TPRS dialogue rules" below) so dialogue quality doesn't regress
  to generic Q&A.
- Keep secrets out of persisted files. The ElevenLabs API key is never
  written to disk by any skill; it is read from an env var at call time.
- Work for any target/source language, not just Latin — nothing
  language-specific should be hardcoded into the skills.

## Non-goals

- Cross-lesson vocabulary/grammar tracking (remembering what was taught in
  earlier chapters so later circling can build on it). Explicitly deferred —
  noted below as a v2 idea, not built now.
- A GUI or web front-end. This is a CLI/Claude-Code-skill workflow.
- Multi-speaker (3+ voice) dialogues. Teacher/Learner, two voices, is the
  only shape supported.
- Managing ElevenLabs billing/quota. The user handles plan/credits
  themselves; the skill only reports API errors clearly (e.g. 402, 401).

## Anti-goals (would be failure even if "working")

- A pipeline that silently produces flat, non-idiomatic circling questions
  (e.g. open "Quid...?" right after new information was just spoken, with
  no either/or test) — this was the central quality bar established in the
  prior session and must not be lost.
- A pipeline that requires the API key to be pasted into chat or written to
  a file to run.
- An orchestrator that barrels through all five stages with no way to stop
  and review before expensive/irreversible steps (the ElevenLabs API calls
  cost real quota).

## Constraints

- Audio generation must test on a small slice (4 lines) and get explicit
  user confirmation before running the full dialogue through the API.
- Repo: public GitHub repo `second-language-llm-tprs`, created under
  `/Users/prime/code/ai/second-language-llm-tprs`.
- Voice IDs and default model persist in a **project-local** config file
  (not under `~/.claude`) so they survive across sessions without being
  re-typed. The ElevenLabs **API key never goes in that file** — it is
  always read from the `ELEVENLABS_API_KEY` env var at call time.
- No hardcoded dependency beyond Python stdlib + `ffmpeg` on PATH (matches
  the working script from the prior session, which deliberately avoided
  `requests`/`pydub` since they weren't already installed).

## Decided design

### Six skills

1. **`clean-source-text`** — Takes pasted/typed source text (possibly with
   OCR noise: line-number remnants, hyphenated line-break artifacts, obvious
   scan-garbled words) and produces a clean, proofread version in the
   source language. This becomes the "original" artifact, kept as-is.
2. **`tprs-expand`** — Takes the cleaned original and rewrites/expands it
   (roughly 2-3x length) into a TPRS circling dialogue in the source
   language. Asks the user which ACTFL level to target (Novice Low/Mid/High,
   Intermediate Low/Mid/High, ...) before writing, since sentence length,
   vocabulary load, and question complexity all scale with level. Produces
   a `Teacher:`/`Learner:` script with `[pause]`, `[slowly]`, etc. markers
   already present (see "TPRS dialogue rules" below) — these are written
   at expansion time, not bolted on later.
3. **`proofread-dialogue`** — A second pass over the expanded dialogue,
   checking grammar/vocabulary correctness and circling-rule compliance
   (every either/or question has two real, distinguishable options; every
   question that immediately follows brand-new information is either/or,
   not open or bare yes/no; filler/`Novi!`/`Non intellego` usage feels
   natural, not mechanical). Can be run standalone against any existing
   dialogue file.
4. **`format-for-elevenlabs`** — A mechanical transform: takes a
   Teacher/Learner script and normalizes it to what the audio-generation
   script expects (consistent `[pause]`/`[slowly]` placement, `an`-pause
   convention, strips anything the target TTS model can't render). Kept
   separate from `tprs-expand` deliberately — the ElevenLabs delivery
   conventions will keep changing independently of the pedagogy (as they
   did today, three times), and conflating them would mean re-touching
   dialogue content every time a formatting convention changes.
5. **`generate-dialogue-audio`** — Wraps the audio-generation script.
   - Reads `teacher_voice_id`, `learner_voice_id`, default `model_id` from
     the project-local config file (see schema below). If the config file
     is missing or incomplete, asks the user for the missing values and
     offers to save them.
   - Model is selectable per run but defaults to `eleven_v4`.
   - Always renders a 4-line test clip first and asks the user to confirm
     before rendering the full dialogue (never skips this, even in
     "full auto" mode for the orchestrator — audio spend is the one place
     a pause is non-negotiable, since it's the irreversible-money step).
   - Reads `ELEVENLABS_API_KEY` from the environment; never accepts it as
     a parameter that could be echoed into a transcript or file, and warns
     the user if a key appears in chat text so they know to rotate it.
6. **`tprs-pipeline`** (orchestrator) — Chains 1→5 for a fresh source text.
   - First question to the user: **"Do I go full auto, or do you want to
     approve each stage?"**
   - Creates one directory per source chapter (named from the source file
     or a user-given slug) and puts every artifact from that run inside it:
     cleaned original, expanded dialogue, ElevenLabs-formatted dialogue,
     the 4-line test mp3, and the final mp3.
   - In "approve" mode, stops after each of stages 1-4 and shows the user
     the result before continuing; always stops at the 4-line audio test
     regardless of mode (per the constraint above).

### TPRS dialogue rules (encoded in `tprs-expand` and checked by
`proofread-dialogue`)

Worked out empirically in the prior session; this is the actual pedagogical
content the skills must encode, not just plumbing:

- A question testing content **just narrated in the same breath** must be
  either/or ("Venditne Albinus gemmas, [pause] an libros?"), giving the
  listener both options aloud — critical for audio-only learners who can't
  glance at text.
- A question about content established **earlier** (not the immediately
  preceding sentence) may be plain yes/no or an open wh-question
  ("Quid in taberna est?") — the listener is recalling, not parsing cold.
- Don't force an either/or where there's no natural second option (e.g.
  pure presence/absence facts like "Suntne lacrimae in oculis eius?") —
  leave those as yes/no rather than inventing an awkward distractor.
- Learner lines get occasional fillers ("Mmm...", "Ahh...", "Ummm"),
  `[pause]` markers, confident-recognition tags ("Novi!"), and a handful of
  "Non intellego" / clarification-request moments at genuinely hard spots
  (new grammatical case, unfamiliar verb) followed by the Teacher
  re-explaining more simply before the Learner gets it right.
- Teacher lines confirm a correct answer before restating
  ("Ita! Haec taberna Romana est...") rather than just re-asserting the
  fact cold.
- Every either/or question uses `[pause]` before `an`, consistently.
- Learner answers are full-verb phrases ("Gemmas, non libros" / better yet
  "Vendit gemmas, non libros"), not bare telegraphic nouns.

### Config file schema

Project-local, not under `~/.claude`. Exact filename left to the builder
(something like `tprs.config.json` at the repo root is the obvious choice).
Holds only non-secret, reusable-across-chapters settings, **keyed by
language** — voice IDs are language-specific (confirmed: switching source
language must not clobber a previously-saved language's voice IDs):

```json
{
  "languages": {
    "latin": {
      "teacher_voice_id": "...",
      "learner_voice_id": "...",
      "default_model_id": "eleven_v4"
    },
    "italian": {
      "teacher_voice_id": "...",
      "learner_voice_id": "...",
      "default_model_id": "eleven_v4"
    }
  }
}
```

No API key field, in any language entry. `generate-dialogue-audio` reads/
writes this file (asking which language key applies, or inferring it from
the ElevenLabs `language_code` used earlier in the run) and always sources
the key from `ELEVENLABS_API_KEY`.

### Resolved from builder-check

- `proofread-dialogue` edits the dialogue file in place (same auto-fix
  contract as `clean-source-text`), rather than only reporting findings.
- No persisted pipeline-resume-state file. Each stage's output is already
  saved to disk in the chapter directory, so resuming in a later session
  just means pointing the next stage's skill at the existing file —
  no separate state machine needed.
- In "approve" mode, rejecting a stage's output supports redo-with-feedback
  (the user gives correction notes, e.g. "make this Intermediate-Mid, not
  Novice-High," and the same stage re-runs with that input), not just
  abort. This mirrors how the prior session's manual iteration actually
  worked.
- `format-for-elevenlabs` reads the config's `default_model_id` for the
  active language so its stripping rules match the target model. If
  `generate-dialogue-audio` is later run with a different model override,
  it warns rather than forcing a stage-4 re-run.

### Output layout

Two levels: a source directory (one per book/course, e.g. a textbook) holds
one chapter directory per chapter run, so a single source with many
chapters doesn't scatter its output across the repo:

```
<source-dir>/
  <chapter-dir>/
    original.txt            # cleaned source text (clean-source-text)
    dialogue.txt             # TPRS-expanded Teacher/Learner script (tprs-expand, proofread-dialogue)
    dialogue.elevenlabs.txt  # formatted for the audio script (format-for-elevenlabs)
    test-4lines.mp3          # confirmation clip (generate-dialogue-audio)
    dialogue.mp3             # final stitched audio (generate-dialogue-audio)
  <chapter-dir>/
    ...
```

Exact filenames, and exact source-dir/chapter-dir naming/slugging, are the
builder's call; the two-level grouping and "everything from one run lives
together" principle are not.

### Existing code to carry over

`elevenlabs_dialogue_tts.py` (written and tested in the prior session,
currently in `/Users/prime/Downloads/`) is the working core of
`generate-dialogue-audio` — stdlib-only, handles `previous_text`/
`next_text` continuity, `[pause]`/`[slowly]` → SSML `<break>` conversion,
silence-gap stitching via `ffmpeg`, and an optional `ELEVENLABS_LANGUAGE_CODE`.
It should move into this repo and be adapted to read voice IDs/model from
the config file (env vars still work as an override) rather than requiring
them as env vars every run.

## Deferred (v2 idea, not built now)

Cross-lesson vocabulary/grammar tracking: a persistent record of what's
already been taught (by chapter) so that `tprs-expand` can build later
chapters' circling on earlier vocabulary instead of re-teaching cold. Needs
its own design pass (what counts as "taught", how it's stored, how much
`tprs-expand` should lean on it vs. the chapter's own new content) — not
specified further here.

## What's left to the builder

- Exact SKILL.md names/frontmatter, directory layout within the repo
  (e.g. `skills/<name>/SKILL.md` per Claude Code convention).
- Exact config filename and field validation behavior (what happens on a
  partially-filled config).
- ACTFL-level-specific calibration specifics beyond "ask which level" —
  i.e., how Novice-Low circling concretely differs from Intermediate-Mid
  (sentence length caps, grammar scope, etc.) — use reasonable judgment
  per standard ACTFL proficiency descriptors.
- Exact prompts/wording inside each SKILL.md.
- Whether `tprs-pipeline` invokes the other five skills via the `Skill`
  tool or inlines their instructions — whichever composes more reliably
  in practice.
- README / repo scaffolding (license, etc.) — public repo, no license
  preference stated; builder may pick a permissive default (e.g. MIT) or
  leave unlicensed and flag it.

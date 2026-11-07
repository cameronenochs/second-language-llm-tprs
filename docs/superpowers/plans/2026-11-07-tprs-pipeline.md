# TPRS Dialogue Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship six Claude Code skills plus three small stdlib Python scripts that turn a source-language chapter into a finished TPRS dialogue mp3.

**Architecture:** Skills hold the judgment (cleaning, TPRS expansion, proofreading, orchestration) as SKILL.md prose. Everything mechanical and testable (config read/write, delivery-marker formatting, ElevenLabs calls and stitching) lives in `scripts/`, called by the skills. Each stage reads and writes files in a per-chapter directory, so any stage can be re-run alone.

**Tech Stack:** Python 3 stdlib only (`unittest`, `urllib`, `json`, `re`), `ffmpeg` on PATH, Claude Code project skills.

**Spec:** `docs/superpowers/specs/2026-11-07-tprs-pipeline-design.md`

## Global Constraints

- Python stdlib + `ffmpeg` only. No `requests`, no `pydub`, no pip installs.
- `ELEVENLABS_API_KEY` is read from the environment at call time. It is never a CLI flag, never written to any file, never echoed. No config field for it, in any language entry.
- Config file is project-local (repo root `tprs.config.json`), keyed by language under `"languages"`. Fields per language: `teacher_voice_id`, `learner_voice_id`, `default_model_id` (default `eleven_v4`). Saving one language never changes another.
- Env vars `TEACHER_VOICE_ID`, `LEARNER_VOICE_ID`, `ELEVENLABS_MODEL_ID`, `ELEVENLABS_LANGUAGE_CODE` override config values.
- Audio generation always renders a 4-line test clip first and waits for explicit user confirmation before the full render, in every mode including full auto.
- Nothing language-specific is hardcoded into skills or scripts. Latin appears only as an example.
- Dialogue format: lines `Teacher: ...` / `Learner: ...`; markers `[pause]`, `[slowly]`; two speakers only.
- Output layout: `output/<source-slug>/<chapter-slug>/` containing `original.txt`, `dialogue.txt`, `dialogue.elevenlabs.txt`, `test-4lines.mp3`, `dialogue.mp3`.
- Skills live at `.claude/skills/<name>/SKILL.md`. Skills assume the working directory is the repo root.
- Commit messages end with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.

## Review Focus

- Config file exists but is partially filled, or is invalid JSON: error names the missing fields or the parse failure; saving a language never drops other languages' entries.
- Language key typed `Latin` vs `latin`: both resolve to the same entry.
- Dialogue file with CRLF endings, blank lines, stray non-speaker lines, or a turn that is only markers: parsed without crashing; empty turns are skipped; zero turns is a clear error.
- Unknown marker such as `[laughs]` in a dialogue: removed, never spoken literally, never a `KeyError`.
- ElevenLabs 401 / 402 or missing `ELEVENLABS_API_KEY`: one-line readable error naming the cause, no traceback, and a missing key fails before any network call.

## File Structure

- `scripts/tprs_config.py` — read/merge/save per-language config; small CLI the skills call.
- `scripts/format_dialogue.py` — mechanical marker/either-or normalizer used by `format-for-elevenlabs`.
- `scripts/tprs_audio.py` — dialogue parse, ElevenLabs calls, ffmpeg stitching, `--limit` test clip.
- `tests/test_tprs_config.py`, `tests/test_format_dialogue.py`, `tests/test_tprs_audio.py`, `tests/test_skills.py`
- `.claude/skills/{clean-source-text,tprs-expand,proofread-dialogue,format-for-elevenlabs,generate-dialogue-audio,tprs-pipeline}/SKILL.md`
- `.claude/skills/tprs-expand/actfl-levels.md` — per-level calibration table.
- `tprs.config.example.json`, `.gitignore` (ignores `tprs.config.json`, `output/`), `README.md`, `LICENSE` (MIT).

Decisions the spec left open: `output/` is gitignored (textbook text in a public repo); real config is gitignored, example is committed; MIT license.

Run all tests with: `python3 -m unittest discover -s tests -v`

---

### Task 1: Config module

**Files:**
- Create: `scripts/tprs_config.py`, `tests/test_tprs_config.py`, `tprs.config.example.json`, `.gitignore`, `LICENSE`

**Interfaces:**
- Produces (`scripts/tprs_config.py`):
  - `CONFIG_FIELDS = ("teacher_voice_id", "learner_voice_id", "default_model_id")`
  - `DEFAULT_MODEL_ID = "eleven_v4"`
  - `class ConfigError(Exception)`
  - `load_language_config(path: str, language: str) -> dict` — fields present for that language; `{}` if file or language absent; `ConfigError` on invalid JSON. Language lowercased and stripped.
  - `missing_fields(entry: dict) -> list[str]` — entries of `CONFIG_FIELDS` not present or empty, in order.
  - `save_language_config(path: str, language: str, values: dict) -> None` — merges into that language only, creates the file if absent, `ConfigError` if `values` has a key outside `CONFIG_FIELDS`.
  - CLI: `python3 scripts/tprs_config.py show --language L [--config P]` prints `{"entry": {...}, "missing": [...]}` as JSON; `set --language L key=value ... [--config P]`. Default config path is `tprs.config.json` at the repo root (`Path(__file__).parent.parent`).

- [ ] **Step 1: Write failing tests** in `tests/test_tprs_config.py` using a `tempfile` dir:
  - `test_missing_file_returns_empty`: `load_language_config(nonexistent, "latin") == {}`
  - `test_language_key_case_insensitive`: save as `"Latin"`, load as `"latin"` returns the values.
  - `test_save_preserves_other_languages`: save latin, then italian; latin entry unchanged.
  - `test_save_merges_fields`: save `teacher_voice_id`, then `learner_voice_id`; both present.
  - `test_missing_fields_partial`: `missing_fields({"teacher_voice_id": "x"}) == ["learner_voice_id", "default_model_id"]`
  - `test_invalid_json_raises`: file containing `{` → `ConfigError`, message contains the path.
  - `test_rejects_api_key_field`: `save_language_config(p, "latin", {"api_key": "x"})` raises `ConfigError`.
- [ ] **Step 2: Run** `python3 -m unittest tests.test_tprs_config -v`. Expected: FAIL (module missing).
- [ ] **Step 3: Implement** the interface above in `scripts/tprs_config.py`; write JSON with `indent=2`, `ensure_ascii=False`.
- [ ] **Step 4: Add scaffolding.** `tprs.config.example.json` = the spec's two-language schema with placeholder `"..."` values. `.gitignore` lists `tprs.config.json`, `output/`, `__pycache__/`. `LICENSE` is MIT, holder `cameronenochs`, year 2026.
- [ ] **Step 5: Run** `python3 -m unittest tests.test_tprs_config -v`. Expected: all PASS.
- [ ] **Step 6: Commit** `feat: add per-language config module`.

---

### Task 2: Dialogue formatter script

**Files:**
- Create: `scripts/format_dialogue.py`, `tests/test_format_dialogue.py`

**Interfaces:**
- Produces:
  - `DEFAULT_MARKERS = frozenset({"pause", "slowly"})`
  - `MODEL_MARKERS: dict[str, frozenset[str]] = {"eleven_v4": DEFAULT_MARKERS}`; unknown model falls back to `DEFAULT_MARKERS`.
  - `format_dialogue(text: str, allowed_markers: frozenset = DEFAULT_MARKERS, or_word: str | None = None) -> str`
  - CLI: `python3 scripts/format_dialogue.py IN OUT [--or-word WORD] [--model MODEL_ID]`

Behavior of `format_dialogue`, applied only to lines starting `Teacher:` or `Learner:` (all other lines pass through unchanged):
1. Marker names lowercased; markers not in `allowed_markers` removed; two adjacent identical markers collapse to one.
2. Runs of whitespace collapse to a single space; no space before `?`, `,`, `.`, `!`.
3. If `or_word` is given and the line ends in `?`, the last whole-word occurrence of `or_word` is rewritten as `, [pause] <or_word>` (existing comma and/or `[pause]` there are absorbed, so the rewrite is idempotent).

- [ ] **Step 1: Write failing tests:**
  - `test_either_or_gets_pause`: `"Teacher: Venditne Albinus gemmas an libros?"` with `or_word="an"` → `"Teacher: Venditne Albinus gemmas, [pause] an libros?"`
  - `test_idempotent`: formatting twice equals formatting once.
  - `test_or_word_only_in_questions`: a statement line containing `an` is unchanged.
  - `test_unknown_marker_removed`: `"Learner: Mmm [laughs] novi!"` → `"Learner: Mmm novi!"`
  - `test_marker_case_and_duplicates`: `"[PAUSE] [pause]"` → `"[pause]"`
  - `test_non_dialogue_lines_untouched`: `"# Title\n\n"` round-trips.
  - `test_no_or_word_no_rewrite`: with `or_word=None`, `an` is untouched.
  - `test_crlf_input`: `"Teacher: a\r\nLearner: b\r\n"` yields `\n` endings.
- [ ] **Step 2: Run** `python3 -m unittest tests.test_format_dialogue -v`. Expected: FAIL.
- [ ] **Step 3: Implement** `format_dialogue` and the CLI (reads/writes UTF-8; `--model` picks markers via `MODEL_MARKERS`).
- [ ] **Step 4: Run** the same command. Expected: PASS.
- [ ] **Step 5: Commit** `feat: add dialogue formatter script`.

---

### Task 3: Audio script

**Files:**
- Create: `scripts/tprs_audio.py` (adapted from `/Users/prime/Downloads/elevenlabs_dialogue_tts.py`), `tests/test_tprs_audio.py`

**Interfaces:**
- Consumes: `tprs_config.load_language_config`, `missing_fields`, `ConfigError`, `DEFAULT_MODEL_ID`.
- Produces (`scripts/tprs_audio.py`):
  - `PAUSE_MARKERS = {"pause": "0.5s", "slowly": "0.3s"}`
  - `markers_to_breaks(text: str) -> str` — `[pause]`/`[slowly]` → `<break time="…"/>`; any other `[marker]` removed; result stripped.
  - `parse_dialogue(text: str) -> list[tuple[str, str]]` — `(speaker, text_with_breaks)`; skips blank lines, non-speaker lines, and turns empty after marker conversion; handles CRLF.
  - `select_turns(turns: list, limit: int | None) -> list` — first `limit` turns; `None` or larger than len returns all.
  - `build_payload(text: str, model_id: str, voice_settings: dict, language_code: str | None = None, previous_text: str | None = None, next_text: str | None = None) -> dict` — omits keys whose value is `None`.
  - `resolve_voices(entry: dict, env: Mapping[str, str]) -> dict[str, str]` — `{"Teacher": …, "Learner": …}`; `TEACHER_VOICE_ID`/`LEARNER_VOICE_ID` in `env` override `entry`; `ConfigError` naming the missing fields otherwise.
  - `class TTSError(Exception)`; `tts(...)` raises it on `urllib.error.HTTPError`: 401 → "ElevenLabs rejected the API key (401)", 402 → "ElevenLabs plan/credits issue (402)", other → "ElevenLabs error <code>".
  - CLI: `python3 scripts/tprs_audio.py INPUT OUTPUT --language L [--model M] [--limit N] [--config P]`. Voice settings keep the existing env-driven stability 0.4 / style 0.3. Order in `main`: parse args → load config → resolve voices → check `ELEVENLABS_API_KEY` (clear `sys.exit` message if absent) → parse dialogue (zero turns is a clear exit) → create output parent dir → render. If `--model` differs from the config's `default_model_id`, print a warning to stderr and continue.

- [ ] **Step 1: Write failing tests** (no network):
  - `test_markers_known_and_unknown`: `"a [pause] b [laughs] c"` → `'a <break time="0.5s"/> b  c'`-equivalent after whitespace; assert no `[` remains and one `<break`.
  - `test_parse_skips_noise`: input with CRLF, blank line, `"random text"`, `"Teacher: [pause]"` yields only real turns, in order.
  - `test_parse_empty_returns_empty_list`
  - `test_select_turns`: limit 4 of 10 → 4; limit 50 of 10 → 10; `None` → 10.
  - `test_build_payload_omits_none`: no `previous_text` key when `None`; `language_code` present when given.
  - `test_resolve_voices_env_overrides_config`
  - `test_resolve_voices_missing_names_fields`: message contains `learner_voice_id`.
  - `test_main_missing_api_key_exits_before_network`: patch `urllib.request.urlopen` to raise `AssertionError`; run `main([...])` with `ELEVENLABS_API_KEY` unset via `mock.patch.dict(os.environ, clear=True)`; expect `SystemExit` whose message mentions `ELEVENLABS_API_KEY`.
  - `test_tts_401_and_402_messages`: patch `urlopen` to raise `HTTPError(code=401/402)`; `TTSError` messages match the strings above.
- [ ] **Step 2: Run** `python3 -m unittest tests.test_tprs_audio -v`. Expected: FAIL.
- [ ] **Step 3: Implement** by copying the Downloads script, then: remove import-time `os.environ[...]` reads (move into `main`), add the functions above, add argparse. Keep `make_silence` and the ffmpeg concat stitching unchanged.
- [ ] **Step 4: Run** the same command. Expected: PASS.
- [ ] **Step 5: Smoke check with real ffmpeg, no API:** `python3 -c "import sys; sys.path.insert(0,'scripts'); import tprs_audio, tempfile, os; p=os.path.join(tempfile.mkdtemp(),'s.mp3'); tprs_audio.make_silence(p); print(os.path.getsize(p)>0)"`. Expected: `True`.
- [ ] **Step 6: Commit** `feat: add config-driven ElevenLabs audio script`.

---

### Task 4: Skill lint test + `clean-source-text`

**Files:**
- Create: `tests/test_skills.py`, `.claude/skills/clean-source-text/SKILL.md`

**Interfaces:**
- Produces: `tests/test_skills.py` globs `.claude/skills/*/SKILL.md` and asserts, per skill: frontmatter has `name` equal to the directory name and a non-empty `description` starting with "Use when"; body contains no match for `sk_[0-9a-f]{20,}` or `xi-api-key:\s*\S+`.
- Convention for every skill: frontmatter `name`, `description`; body states its input file(s), output file(s), and that it assumes cwd = repo root.

- [ ] **Step 1: Write `tests/test_skills.py`** with `test_frontmatter_matches_directory` and `test_no_secrets` (loop over discovered skills; fail if zero found).
- [ ] **Step 2: Run** `python3 -m unittest tests.test_skills -v`. Expected: FAIL (no skills).
- [ ] **Step 3: Write `clean-source-text/SKILL.md`.** Input: pasted text or a file path; asks for source-language name, source slug, chapter slug if not given. Output: `output/<source-slug>/<chapter-slug>/original.txt`. Must state: remove line-number remnants, rejoin hyphenated line breaks, fix only obvious scan-garbled words, never modernize or paraphrase; auto-fix in place, then list every non-trivial correction made so the user can veto; ask rather than guess when a garbled word has more than one plausible reading.
- [ ] **Step 4: Run** the lint test. Expected: PASS.
- [ ] **Step 5: Commit** `feat: add clean-source-text skill and skill lint test`.

---

### Task 5: `tprs-expand` skill

**Files:**
- Create: `.claude/skills/tprs-expand/SKILL.md`, `.claude/skills/tprs-expand/actfl-levels.md`

**Interfaces:**
- Consumes: `original.txt` in a chapter directory. Produces `dialogue.txt` there.

- [ ] **Step 1: Write `actfl-levels.md`:** a table for Novice Low/Mid/High and Intermediate Low/Mid/High giving maximum words per sentence, grammar scope, vocabulary load (new items per paragraph), question types allowed, ratio of Teacher restatement to new content. Values follow ACTFL proficiency descriptors; mark them as starting points the user can override.
- [ ] **Step 2: Write `SKILL.md`.** Required content:
  - First action: ask which ACTFL level; read `actfl-levels.md`; do not write before the answer.
  - Target length 2–3× `original.txt`; every fact in the original must appear.
  - Output format `Teacher:`/`Learner:` with `[pause]`, `[slowly]` written at expansion time.
  - The seven rules from the spec's "TPRS dialogue rules", each stated as an imperative with the spec's example sentence: either/or for just-narrated content; yes/no or wh- for earlier content; no forced either/or on presence/absence facts; Learner fillers, `[pause]`, "Novi!" tags, and a few "Non intellego" moments at genuinely hard spots followed by simpler Teacher re-explanation; Teacher confirms before restating ("Ita! …"); `[pause]` before the or-word in every either/or; Learner answers as full-verb phrases.
  - Language-neutral: tell the skill to use the source language's own or-word, filler, and confirmation words, and to state the chosen or-word in its final chat message so `format-for-elevenlabs` can reuse it.
  - Redo-with-feedback: if invoked again with correction notes, regenerate `dialogue.txt` honoring them.
- [ ] **Step 3: Run** `python3 -m unittest tests.test_skills -v`. Expected: PASS.
- [ ] **Step 4: Commit** `feat: add tprs-expand skill with ACTFL calibration`.

---

### Task 6: `proofread-dialogue` skill

**Files:**
- Create: `.claude/skills/proofread-dialogue/SKILL.md`

- [ ] **Step 1: Write the skill.** Input: any dialogue file path (default `dialogue.txt` in the current chapter directory). Edits the file in place, then lists every change. Checklist, each item stated as a check with its fix:
  - grammar/vocabulary correctness for the source language;
  - every either/or has two real, distinguishable options;
  - every question right after new information is either/or, never open or bare yes/no (the anti-goal in the spec);
  - no forced either/or on presence/absence facts;
  - `[pause]` before the or-word in each either/or;
  - Teacher confirms before restating; Learner answers are full-verb phrases;
  - fillers, "Novi!", "Non intellego" feel natural, not mechanical (flag runs of the same filler);
  - ACTFL level consistency if the level is known.
  Must say: change the minimum needed, never alter facts from `original.txt` when it is present, and never rewrite whole turns when a word fix suffices.
- [ ] **Step 2: Run** the lint test. Expected: PASS.
- [ ] **Step 3: Commit** `feat: add proofread-dialogue skill`.

---

### Task 7: `format-for-elevenlabs` skill

**Files:**
- Create: `.claude/skills/format-for-elevenlabs/SKILL.md`

- [ ] **Step 1: Write the skill.** Steps it must contain, in order:
  1. Get the active language (ask if unknown) and run `python3 scripts/tprs_config.py show --language <L>` to read `default_model_id` (fall back to `eleven_v4` if empty).
  2. Ask for the language's or-word if not already known from `tprs-expand`.
  3. Run `python3 scripts/format_dialogue.py <chapter>/dialogue.txt <chapter>/dialogue.elevenlabs.txt --or-word <W> --model <M>`.
  4. Show a diff summary (line count, markers removed). Do not hand-edit dialogue content; if the script's output looks wrong, report it rather than patching by hand.
  Also state why this stage is separate from `tprs-expand` (delivery conventions change independently of pedagogy).
- [ ] **Step 2: Run** the lint test. Expected: PASS.
- [ ] **Step 3: Commit** `feat: add format-for-elevenlabs skill`.

---

### Task 8: `generate-dialogue-audio` skill

**Files:**
- Create: `.claude/skills/generate-dialogue-audio/SKILL.md`
- Modify: `tests/test_skills.py` (add `test_audio_skill_gates`)

- [ ] **Step 1: Add failing test** `test_audio_skill_gates`: the skill file contains `ELEVENLABS_API_KEY`, `--limit 4`, `test-4lines.mp3`, and `confirm`, and does not contain the literal `--api-key`.
- [ ] **Step 2: Run** the lint test. Expected: FAIL.
- [ ] **Step 3: Write the skill.** Steps it must contain:
  1. Determine the language key; run `tprs_config.py show`. If `missing` is non-empty, ask the user for exactly those values and offer to save them with `tprs_config.py set` (never ask for or save a key).
  2. Check `ELEVENLABS_API_KEY` is set with `[ -n "$ELEVENLABS_API_KEY" ]` (never print it). If unset, tell the user to export it in their own shell and stop. If a key-looking string appears in chat, tell the user to rotate it and do not use it.
  3. Model defaults to config `default_model_id`; accept a per-run override via `--model`; the script warns when it differs from the default.
  4. Always run the test clip: `python3 scripts/tprs_audio.py <chapter>/dialogue.elevenlabs.txt <chapter>/test-4lines.mp3 --language <L> --limit 4`, then ask the user to listen and explicitly confirm. Never skip, in any mode.
  5. Only after confirmation, run the full render to `<chapter>/dialogue.mp3`. Report 401/402 errors verbatim from the script.
- [ ] **Step 4: Run** the lint test. Expected: PASS.
- [ ] **Step 5: Commit** `feat: add generate-dialogue-audio skill`.

---

### Task 9: `tprs-pipeline` orchestrator skill

**Files:**
- Create: `.claude/skills/tprs-pipeline/SKILL.md`
- Modify: `tests/test_skills.py` (add `test_pipeline_gates`)

- [ ] **Step 1: Add failing test** `test_pipeline_gates`: the file contains `Do I go full auto, or do you want to approve each stage?` verbatim, and names all five stage skills (`clean-source-text`, `tprs-expand`, `proofread-dialogue`, `format-for-elevenlabs`, `generate-dialogue-audio`).
- [ ] **Step 2: Run** the lint test. Expected: FAIL.
- [ ] **Step 3: Write the skill.** Required content:
  - First question to the user, verbatim: "Do I go full auto, or do you want to approve each stage?"
  - Then gather source text (paste or file), language, source slug, chapter slug; create `output/<source-slug>/<chapter-slug>/`.
  - Invoke the five skills in order via the `Skill` tool, passing the chapter directory.
  - Approve mode: stop after stages 1–4, show the result, accept approve / reject-with-feedback (re-run the same stage with the feedback) / abort.
  - Full-auto mode still stops at the generate-dialogue-audio test clip; say so explicitly.
  - Resume: no state file; to resume, the user points the next stage at the existing file in the chapter directory.
- [ ] **Step 4: Run** the lint test. Expected: PASS.
- [ ] **Step 5: Commit** `feat: add tprs-pipeline orchestrator skill`.

---

### Task 10: README and final verification

**Files:**
- Create: `README.md`
- Modify: `tests/test_skills.py` (add `test_all_six_skills_present`)

- [ ] **Step 1: Add test** `test_all_six_skills_present`: the set of skill directory names equals the six names in the spec.
- [ ] **Step 2: Write `README.md`:** what the project does; prerequisites (Python 3, `ffmpeg`, `ELEVENLABS_API_KEY` exported in the shell); the six skills in one line each; config file setup from `tprs.config.example.json`; output layout; how to run each script standalone; how to run tests; the v2 deferred idea in one line.
- [ ] **Step 3: Run full suite** `python3 -m unittest discover -s tests -v`. Expected: all PASS.
- [ ] **Step 4: Secret scan** `git grep -nE 'sk_[0-9a-f]{20,}|xi-api-key: *[A-Za-z0-9]' -- . ':!tests'`. Expected: no output.
- [ ] **Step 5: Commit** `docs: add README and skill-set check`.

---

## Self-review notes

- Spec coverage: six skills (Tasks 4–9), TPRS rules (5, 6), config schema and language keying (1), key handling (3, 8), 4-line gate in all modes (8, 9), output layout (Global Constraints, 4, 9), carry-over script (3), approve-mode redo-with-feedback (9), in-place proofread (6), model-mismatch warning (3), no resume file (9), v2 deferred (10, README only).
- Not covered by automated tests: the quality of skill prose and real ElevenLabs output. Verify the first end-to-end run by hand on a short chapter.

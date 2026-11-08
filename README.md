# Hear the chapter you are studying

![Listen, in Spanish, Arabic, Russian, Hindi, Chinese, and Korean](docs/header.png)

You already have the chapter. This turns it into a conversation you can listen to.

## 1. The problem

You want a new language to make sense when someone speaks it. The chapter in front of you has this week's story and the words that carry it. Reading the page once leaves those words on the page.

Understanding grows when you hear the same ideas spoken, simply, more than once. A teacher asks a short question. You answer. They ask again from another angle. The new words come back until your ear knows them. Teachers call this TPRS: Teaching Proficiency through Reading and Storytelling. Asking about one idea several ways is called circling.

A class might circle a story once, out loud, and then move on. Building that same spoken practice for the exact chapter on your desk, matched to how far along you are, usually means writing the questions and recording them yourself.

## 2. The solution

Hand over the chapter you are already reading. Get back a short spoken dialogue.

One voice is the teacher. One voice is the learner. They tell the story from your chapter in short lines, then circle it: the same facts return as easy choices, so you can follow when a word is still new. The result is one audio file. Play it on a walk, in the car, or with the book open beside you.

Any language the chapter is written in can be the language you hear.

## 3. How this gets you there

You talk to an AI assistant the way you would ask a person for help. Claude, Codex, Gemini, and Grok can all follow the steps in this project. You give it the chapter. It does five things:

1. Cleans up the text, including a messy scan.
2. Writes the teacher-and-learner dialogue at your level, from brand new to advanced.
3. Checks the language, and checks that the questions really circle.
4. Prepares the script so it can be spoken aloud.
5. Records two voices and saves an mp3.

You hear a few lines before the full recording. If the voices sound right, the rest is made. That sample is there so you can pick different voices while the recording is still short.

You answer a few plain questions along the way: go straight through, or pause so you can read each step; how far along you are; and the word your language uses for "or" (Latin uses *an*).

When it finishes, you have a folder with the cleaned chapter, the written dialogue, and the audio.

## 4. Technical details

The sections above are the whole idea. Everything below is how to set it up, and how the pieces fit if you want to change them.

The project name is Second Language LLM TPRS. The steps are instructions an assistant reads from this repo. Shared rules live in `AGENTS.md`.

### What you need

- Python 3. The scripts use the standard library only.
- `ffmpeg` on your `PATH`.
- An ElevenLabs subscription. Set `ELEVENLABS_API_KEY` in the shell you start the assistant from. Keep the key out of the chat. If it shows up there, rotate it.
- An assistant that reads `AGENTS.md` and skill folders: Claude Code, Codex, Gemini CLI, or Grok.

### Getting started

You bring the chapter: paste it into the chat, or point the assistant at a text file.

1. Fork and clone the repo, then open a terminal in the project folder.
2. In that same terminal, set your key: `export ELEVENLABS_API_KEY=...`
3. Pick two ElevenLabs voices, teacher and learner, and note their voice IDs. Save them in `tprs.config.json` (see [Config](#config)), or give them to the assistant when it asks.
4. Have the chapter as text you can paste, or as a `.txt` file outside the repo or under `output/` (that folder is gitignored). A PDF works when your assistant can read PDFs. A scanned PDF needs OCR first, so the words are real text.
5. Start the assistant in the project folder.
6. Ask it to run the pipeline. For example:

   > Run the tprs-pipeline on ~/Downloads/chapter3.txt. Latin, source slug `wheelock`, chapter slug `ch03-taberna`.

   The source slug is a short name for the book. The chapter slug is a short name for this chapter. They become the folder names.

7. Answer the setup questions: full auto or approve each stage, your [ACTFL](https://www.actfl.org/educator-resources/actfl-proficiency-guidelines) level (Novice, Intermediate, or Advanced, and Low / Mid / High inside those), and the language's word for "or".
8. Listen to `test-4lines.mp3` when the assistant stops. Confirm, and it writes `dialogue.mp3`. Full-auto mode still waits on this clip, because the full recording spends ElevenLabs credits.

Files land in `output/<source-slug>/<chapter-slug>/`. To continue later, ask the assistant to run the next stage on that folder. You can also name one stage, for example: proofread `output/wheelock/ch03-taberna/dialogue.txt`.

### Skills

Project skills live in `.agents/skills/`. Codex, Grok, and Gemini CLI load that directory. Claude Code loads the same folders through the `.claude/skills` symlink.

| Skill | What it writes |
| --- | --- |
| `clean-source-text` | `original.txt` |
| `tprs-expand` | `dialogue.txt`, at the ACTFL level you chose |
| `proofread-dialogue` | edits `dialogue.txt` in place |
| `format-for-elevenlabs` | `dialogue.elevenlabs.txt` |
| `generate-dialogue-audio` | `test-4lines.mp3`, then `dialogue.mp3` after you confirm |
| `tprs-pipeline` | runs the five in order |

### Config

Copy `tprs.config.example.json` to `tprs.config.json` (gitignored). Fill in voice IDs per language, or let the audio step ask and save them. The file holds voice IDs and the default voice model (`eleven_v4`). The API key stays in the environment.

### Output

```
output/<source-slug>/<chapter-slug>/
  original.txt
  dialogue.txt
  dialogue.elevenlabs.txt
  test-4lines.mp3
  dialogue.mp3
```

### Scripts

```bash
python3 scripts/tprs_config.py show --language latin
python3 scripts/format_dialogue.py IN OUT --or-word an
python3 scripts/tprs_audio.py IN.txt OUT.mp3 --language latin --limit 4
```

### Tests

```bash
python3 -m unittest discover -s tests -v
```

Pull requests into `main` must pass the `tests`, `gitleaks`, `codeql`, and `dependency-review` checks. Report vulnerabilities through [Security Advisories](https://github.com/cameronenochs/second-language-llm-tprs/security/advisories/new).

### Later

Remembering words and grammar across chapters, so a later lesson can circle what an earlier one taught, is left for a later version.

## License

MIT

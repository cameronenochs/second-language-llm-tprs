#!/usr/bin/env python3
"""
Turn a Teacher:/Learner: dialogue .txt into one stitched mp3 via ElevenLabs TTS.

Voice IDs and default model come from the project config (tprs_config.py);
TEACHER_VOICE_ID / LEARNER_VOICE_ID / ELEVENLABS_MODEL_ID env vars override.
The API key comes only from ELEVENLABS_API_KEY.
Optional env: ELEVENLABS_LANGUAGE_CODE, ELEVENLABS_STABILITY, ELEVENLABS_STYLE.

With --mode reading, every non-blank line is read by one narrator voice
(narrator_voice_id / NARRATOR_VOICE_ID) and the line is the unit of --limit.

With --mode course, INPUT is a course script.jsonl and OUTPUT is a folder.
Each distinct item text becomes one kept clip with an opaque name, and
OUTPUT/index.json maps every item id to its clip. Nothing is joined unless
--join PATH is given (used for the test clip). --limit counts distinct texts.

Usage:
  tprs_audio.py INPUT OUTPUT --language L [--mode dialogue|reading|course] [--model M] [--limit N]
                [--join PATH] [--config P]
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tprs_config import (  # noqa: E402
    DEFAULT_CONFIG_PATH,
    DEFAULT_MODEL_ID,
    ConfigError,
    load_language_config,
    missing_fields,
)

# Only pause-like markers become real <break> SSML; any other [marker] is dropped.
PAUSE_MARKERS = {"pause": "0.5s", "slowly": "0.3s"}
MARKER_RE = re.compile(r"\[([^\]]+)\]")
BREAK_RE = re.compile(r"<break [^>]*/>")
TURN_RE =re.compile(r"^(Teacher|Learner):\s*(.*)$")


class TTSError(Exception):
    pass


class FFmpegError(Exception):
    pass


def run_ffmpeg(args):
    try:
        subprocess.run(["ffmpeg", *args], check=True, capture_output=True)
    except FileNotFoundError:
        raise FFmpegError("ffmpeg not found on PATH")
    except subprocess.CalledProcessError as e:
        raise FFmpegError(f"ffmpeg failed: {e.stderr.decode(errors='replace')[-500:]}")


def markers_to_breaks(text: str) -> str:
    def repl(m):
        tag = m.group(1).strip().lower()
        return f'<break time="{PAUSE_MARKERS[tag]}"/>' if tag in PAUSE_MARKERS else ""
    return MARKER_RE.sub(repl, text).strip()


def parse_dialogue(text: str) -> list:
    turns = []
    for line in text.splitlines():
        m = TURN_RE.match(line.strip())
        if m:
            body = markers_to_breaks(m.group(2))
            if BREAK_RE.sub("", body).strip():
                turns.append((m.group(1), body))
    return turns


def parse_reading(text: str) -> list:
    # shortcut: one TTS request per line; a line over the model's character limit fails, so keep paragraphs short.
    turns = []
    for line in text.splitlines():
        body = markers_to_breaks(line)
        if BREAK_RE.sub("", body).strip():
            turns.append(("Narrator", body))
    return turns


def parse_course(text: str) -> list:
    """Return (item_id, text) for every item of a course script.jsonl."""
    items = []
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            item_id, body = row["id"], markers_to_breaks(row["text"])
        except (ValueError, KeyError, TypeError):
            raise ValueError(f"line {n}: not a script item with id and text")
        if BREAK_RE.sub("", body).strip():
            items.append((item_id, body))
    return items


def clip_name(voice_id: str, model_id: str, text: str) -> str:
    return hashlib.sha1(f"{voice_id}|{model_id}|{text}".encode()).hexdigest()[:10] + ".mp3"


def join_clips(clips: list, output: str):
    with tempfile.TemporaryDirectory() as tmp:
        silence = os.path.join(tmp, "silence.mp3")
        make_silence(silence)
        concat_list = os.path.join(tmp, "list.txt")
        with open(concat_list, "w") as list_f:
            for i, clip in enumerate(clips):
                # ffmpeg resolves relative paths against the list file's folder, so pass absolute ones.
                list_f.write(f"file '{os.path.abspath(clip)}'\n")
                if i < len(clips) - 1:
                    list_f.write(f"file '{silence}'\n")
        run_ffmpeg(["-y", "-f", "concat", "-safe", "0", "-i", concat_list, "-c", "copy", output])


def render_course(items, outdir, voice_id, api_key, model_id, voice_settings, lang_code, limit=None):
    """Render each distinct text once into outdir; write outdir/index.json. Returns the rendered clip paths."""
    os.makedirs(outdir, exist_ok=True)
    names, order = {}, []
    for _, text in items:
        if text not in names:
            names[text] = clip_name(voice_id, model_id, text)
            order.append(text)
    order = select_turns(order, limit)
    clips = []
    for i, text in enumerate(order):
        clip = os.path.join(outdir, names[text])
        print(f"[{i+1}/{len(order)}] {text[:60]}")
        if not (os.path.exists(clip) and os.path.getsize(clip) > 0):
            # Items are independent sentences, so no previous_text/next_text.
            tts(text, voice_id, api_key, clip, model_id, voice_settings, lang_code)
        clips.append(clip)
    rendered = set(order)
    index = {item_id: names[text] for item_id, text in items if text in rendered}
    with open(os.path.join(outdir, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    return clips


def select_turns(turns: list, limit) -> list:
    return turns if limit is None else turns[:limit]


def build_payload(text, model_id, voice_settings, language_code=None, previous_text=None, next_text=None) -> dict:
    payload = {"text": text, "model_id": model_id, "voice_settings": voice_settings}
    for key, value in (("language_code", language_code), ("previous_text", previous_text), ("next_text", next_text)):
        if value is not None:
            payload[key] = value
    return payload


def resolve_voices(entry: dict, env) -> dict:
    teacher = env.get("TEACHER_VOICE_ID") or entry.get("teacher_voice_id")
    learner = env.get("LEARNER_VOICE_ID") or entry.get("learner_voice_id")
    missing = [n for n, v in (("teacher_voice_id", teacher), ("learner_voice_id", learner)) if not v]
    if missing:
        raise ConfigError(f"missing voice config: {', '.join(missing)}")
    return {"Teacher": teacher, "Learner": learner}


def resolve_narrator(entry: dict, env) -> dict:
    narrator = env.get("NARRATOR_VOICE_ID") or entry.get("narrator_voice_id")
    if not narrator:
        raise ConfigError("missing voice config: narrator_voice_id")
    return {"Narrator": narrator}


def tts(text, voice_id, api_key, out_path, model_id, voice_settings,
        language_code=None, previous_text=None, next_text=None):
    payload = build_payload(text, model_id, voice_settings, language_code, previous_text, next_text)
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        data=json.dumps(payload).encode(), method="POST",
        headers={"xi-api-key": api_key, "Content-Type": "application/json", "Accept": "audio/mpeg"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp, open(out_path, "wb") as f:
            shutil.copyfileobj(resp, f)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            raise TTSError("ElevenLabs rejected the API key (401)")
        if e.code == 402:
            raise TTSError("ElevenLabs plan/credits issue (402)")
        detail = e.read(2000).decode(errors="replace").strip() if e.fp else ""
        raise TTSError(f"ElevenLabs error {e.code}: {detail}" if detail else f"ElevenLabs error {e.code}")
    except (urllib.error.URLError, TimeoutError) as e:
        raise TTSError(f"network error: {getattr(e, 'reason', e)}")


def make_silence(out_path: str, seconds: float = 0.4):
    run_ffmpeg(["-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                "-t", str(seconds), "-q:a", "9", out_path])


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("input")
    p.add_argument("output")
    p.add_argument("--language", required=True)
    p.add_argument("--mode", choices=["dialogue", "reading", "course"], default="dialogue")
    p.add_argument("--model")
    p.add_argument("--limit", type=int)
    p.add_argument("--join", help="course mode: also join the rendered clips into this mp3")
    p.add_argument("--config", default=DEFAULT_CONFIG_PATH)
    args = p.parse_args(argv)

    try:
        entry = load_language_config(args.config, args.language)
        voices = (resolve_voices if args.mode == "dialogue" else resolve_narrator)(entry, os.environ)
    except ConfigError as e:
        sys.exit(f"error: {e}")

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        sys.exit("error: ELEVENLABS_API_KEY is not set; export it in your shell")

    default_model = entry.get("default_model_id") or DEFAULT_MODEL_ID
    model_id = args.model or os.environ.get("ELEVENLABS_MODEL_ID") or default_model
    if model_id != default_model:
        print(f"warning: model {model_id} differs from configured default {default_model}; "
              "the formatted dialogue was prepared for the default", file=sys.stderr)

    voice_settings = {
        "stability": float(os.environ.get("ELEVENLABS_STABILITY", 0.4)),
        "style": float(os.environ.get("ELEVENLABS_STYLE", 0.3)),
    }
    lang_code = os.environ.get("ELEVENLABS_LANGUAGE_CODE")

    # Fail on a missing ffmpeg before any TTS quota is spent.
    if args.mode != "course" or args.join:
        try:
            run_ffmpeg(["-version"])
        except FFmpegError as e:
            sys.exit(f"error: {e}")

    with open(args.input, encoding="utf-8") as f:
        text = f.read()
    if args.mode == "course":
        try:
            items = parse_course(text)
        except ValueError as e:
            sys.exit(f"error: {e}")
        if not items:
            sys.exit("error: no script items found")
        try:
            clips = render_course(items, args.output, voices["Narrator"], api_key, model_id,
                                  voice_settings, lang_code, args.limit)
            if args.join:
                join_clips(clips, args.join)
        except (TTSError, FFmpegError) as e:
            sys.exit(f"error: {e}")
        print(f"done -> {args.output}" + (f" and {args.join}" if args.join else ""))
        return

    parse = parse_reading if args.mode == "reading" else parse_dialogue
    turns = select_turns(parse(text), args.limit)
    if not turns:
        sys.exit("error: no text lines found" if args.mode == "reading" else "error: no Teacher:/Learner: lines found")
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    # Clips live beside the output so a mid-run failure (402, network) keeps the
    # quota already spent; the name hashes voice+model+text so edits never reuse stale audio.
    parts = os.path.abspath(args.output) + ".parts"
    os.makedirs(parts, exist_ok=True)

    try:
        clips = []
        for i, (speaker, text) in enumerate(turns):
            clip = os.path.join(parts, f"{i:04d}-{clip_name(voices[speaker], model_id, text)}")
            print(f"[{i+1}/{len(turns)}] {speaker}: {text[:60]}")
            if not (os.path.exists(clip) and os.path.getsize(clip) > 0):
                tts(text, voices[speaker], api_key, clip, model_id, voice_settings, lang_code,
                    turns[i - 1][1] if i > 0 else None,
                    turns[i + 1][1] if i < len(turns) - 1 else None)
            clips.append(clip)
        join_clips(clips, args.output)
    except (TTSError, FFmpegError) as e:
        sys.exit(f"error: {e}")
    shutil.rmtree(parts, ignore_errors=True)

    print(f"done -> {args.output}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Turn a Teacher:/Learner: dialogue .txt into one stitched mp3 via ElevenLabs TTS.

Voice IDs and default model come from the project config (tprs_config.py);
TEACHER_VOICE_ID / LEARNER_VOICE_ID / ELEVENLABS_MODEL_ID env vars override.
The API key comes only from ELEVENLABS_API_KEY.
Optional env: ELEVENLABS_LANGUAGE_CODE, ELEVENLABS_STABILITY, ELEVENLABS_STYLE.

Usage:
  tprs_audio.py INPUT OUTPUT --language L [--model M] [--limit N] [--config P]
"""
import argparse
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
MARKER_RE = re.compile(r"\[([a-zA-Z ]+)\]")
BREAK_RE = re.compile(r"<break [^>]*/>")
TURN_RE =re.compile(r"^(Teacher|Learner):\s*(.*)$")


class TTSError(Exception):
    pass


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


def tts(text, voice_id, api_key, out_path, model_id, voice_settings,
        language_code=None, previous_text=None, next_text=None):
    payload = build_payload(text, model_id, voice_settings, language_code, previous_text, next_text)
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        data=json.dumps(payload).encode(), method="POST",
        headers={"xi-api-key": api_key, "Content-Type": "application/json", "Accept": "audio/mpeg"},
    )
    try:
        with urllib.request.urlopen(req) as resp, open(out_path, "wb") as f:
            shutil.copyfileobj(resp, f)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            raise TTSError("ElevenLabs rejected the API key (401)")
        if e.code == 402:
            raise TTSError("ElevenLabs plan/credits issue (402)")
        raise TTSError(f"ElevenLabs error {e.code}")


def make_silence(out_path: str, seconds: float = 0.4):
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
        "-t", str(seconds), "-q:a", "9", out_path,
    ], check=True, capture_output=True)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("input")
    p.add_argument("output")
    p.add_argument("--language", required=True)
    p.add_argument("--model")
    p.add_argument("--limit", type=int)
    p.add_argument("--config", default=DEFAULT_CONFIG_PATH)
    args = p.parse_args(argv)

    try:
        entry = load_language_config(args.config, args.language)
        voices = resolve_voices(entry, os.environ)
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

    with open(args.input, encoding="utf-8") as f:
        turns = select_turns(parse_dialogue(f.read()), args.limit)
    if not turns:
        sys.exit("error: no Teacher:/Learner: lines found")

    voice_settings = {
        "stability": float(os.environ.get("ELEVENLABS_STABILITY", 0.4)),
        "style": float(os.environ.get("ELEVENLABS_STYLE", 0.3)),
    }
    lang_code = os.environ.get("ELEVENLABS_LANGUAGE_CODE")
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

    try:
        with tempfile.TemporaryDirectory() as tmp:
            silence = os.path.join(tmp, "silence.mp3")
            make_silence(silence)
            concat_list = os.path.join(tmp, "list.txt")
            with open(concat_list, "w") as list_f:
                for i, (speaker, text) in enumerate(turns):
                    clip = os.path.join(tmp, f"{i:04d}.mp3")
                    print(f"[{i+1}/{len(turns)}] {speaker}: {text[:60]}")
                    tts(text, voices[speaker], api_key, clip, model_id, voice_settings, lang_code,
                        turns[i - 1][1] if i > 0 else None,
                        turns[i + 1][1] if i < len(turns) - 1 else None)
                    list_f.write(f"file '{clip}'\n")
                    if i < len(turns) - 1:
                        list_f.write(f"file '{silence}'\n")
            subprocess.run([
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", concat_list, "-c", "copy", args.output,
            ], check=True, capture_output=True)
    except TTSError as e:
        sys.exit(f"error: {e}")

    print(f"done -> {args.output}")


if __name__ == "__main__":
    main()

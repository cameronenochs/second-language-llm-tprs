#!/usr/bin/env python3
"""Read and write the project-local, per-language TPRS config.

The config holds only non-secret settings. The ElevenLabs API key is never
stored here; it comes from the ELEVENLABS_API_KEY env var.

Usage:
  tprs_config.py show --language latin [--mode dialogue|reading] [--config PATH]
  tprs_config.py set  --language latin key=value ... [--config PATH]
"""
import argparse
import json
import os
import sys
from pathlib import Path

CONFIG_FIELDS = ("teacher_voice_id", "learner_voice_id", "narrator_voice_id", "default_model_id")
DIALOGUE_FIELDS = ("teacher_voice_id", "learner_voice_id", "default_model_id")
READING_FIELDS = ("narrator_voice_id", "default_model_id")
DEFAULT_MODEL_ID = "eleven_v4"
DEFAULT_CONFIG_PATH = str(Path(__file__).resolve().parent.parent / "tprs.config.json")


class ConfigError(Exception):
    pass


def _norm(language: str) -> str:
    return language.strip().lower()


def _read(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigError(f"{path}: invalid JSON ({e})")
    if not isinstance(data, dict):
        raise ConfigError(f"{path}: top level must be a JSON object")
    return data


def load_language_config(path: str, language: str) -> dict:
    entry = _read(path).get("languages", {}).get(_norm(language), {})
    return {k: v for k, v in entry.items() if k in CONFIG_FIELDS}


def missing_fields(entry: dict, required=DIALOGUE_FIELDS) -> list:
    return [f for f in required if not entry.get(f)]


def save_language_config(path: str, language: str, values: dict) -> None:
    bad = sorted(set(values) - set(CONFIG_FIELDS))
    if bad:
        raise ConfigError(f"unknown config field(s): {', '.join(bad)}; allowed: {', '.join(CONFIG_FIELDS)}")
    data = _read(path)
    entry = data.setdefault("languages", {}).setdefault(_norm(language), {})
    entry.update(values)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["show", "set"])
    p.add_argument("pairs", nargs="*", help="key=value (set only)")
    p.add_argument("--language", required=True)
    p.add_argument("--mode", choices=["dialogue", "reading"], default="dialogue")
    p.add_argument("--config", default=DEFAULT_CONFIG_PATH)
    args = p.parse_args(argv)
    required = READING_FIELDS if args.mode == "reading" else DIALOGUE_FIELDS
    try:
        if args.command == "show":
            entry = load_language_config(args.config, args.language)
            print(json.dumps({"entry": entry, "missing": missing_fields(entry, required)}, indent=2))
        else:
            values = dict(pair.split("=", 1) for pair in args.pairs)
            save_language_config(args.config, args.language, values)
            print(f"saved {', '.join(values)} for {_norm(args.language)}")
    except (ConfigError, ValueError) as e:
        sys.exit(f"error: {e}")


if __name__ == "__main__":
    main()

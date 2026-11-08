#!/usr/bin/env python3
"""
Copy a finished course lesson into the app/ web player.

  export_course.py OUTDIR --language L --lesson N [--level 1] [--app APP]

Reads OUTDIR/script.jsonl, OUTDIR/pictures.json, OUTDIR/pictures/*.png and
OUTDIR/audio/index.json. Writes media to APP/public/courses/<lang>/L<level>-<NN>/
and the manifest to APP/src/lesson/content/<lang>-L<level>-<NN>.json.
A plate is one (picture, clip) pair; rounds follow the script's item order.
No text goes into the manifest.
"""
import argparse
import json
import os
import re
import shutil
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SLUG = re.compile(r"^[a-z][a-z0-9-]*$")


class ExportError(Exception):
    pass


def build_manifest(item_ids: list, pictures: dict, audio_index: dict, base_url: str,
                   language: str, level: str, lesson: int) -> tuple:
    """Return (manifest, [(picture_id, clip)]) for the plates used."""
    pic_of = {i: p["id"] for p in pictures["pictures"] for i in p["items"]}
    plates, slot, rounds = [], {}, []
    for item_id in item_ids:
        if item_id not in pic_of:
            raise ExportError(f"item {item_id} has no picture in pictures.json")
        if item_id not in audio_index:
            raise ExportError(f"item {item_id} has no clip in audio/index.json")
        key = (pic_of[item_id], audio_index[item_id])
        if key not in slot:
            slot[key] = len(plates)
            plates.append(key)
        rounds.append(slot[key])
    manifest = {
        "language": language, "level": level, "lesson": lesson,
        "plates": [{"image": f"{base_url}/img/{pid}.png", "audio": f"{base_url}/audio/{clip}"} for pid, clip in plates],
        "rounds": rounds,
    }
    return manifest, plates


def read_json(path: str):
    if not os.path.exists(path):
        raise ExportError(f"missing {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def export(outdir: str, language: str, lesson: int, level: str, app: str) -> str:
    if not SLUG.match(language):
        raise ExportError("language must be a lowercase slug like 'latin'")
    name = f"L{level}-{lesson:02d}"
    script = os.path.join(outdir, "script.jsonl")
    if not os.path.exists(script):
        raise ExportError(f"missing {script}")
    with open(script, encoding="utf-8") as f:
        item_ids = [json.loads(line)["id"] for line in f if line.strip()]
    pictures = read_json(os.path.join(outdir, "pictures.json"))
    audio_index = read_json(os.path.join(outdir, "audio", "index.json"))
    manifest, plates = build_manifest(item_ids, pictures, audio_index,
                                      f"/courses/{language}/{name}", language, level, lesson)

    media = os.path.join(app, "public", "courses", language, name)
    for sub in ("img", "audio"):
        os.makedirs(os.path.join(media, sub), exist_ok=True)
    for pid, clip in plates:
        for src, dst in ((os.path.join(outdir, "pictures", f"{pid}.png"), os.path.join(media, "img", f"{pid}.png")),
                         (os.path.join(outdir, "audio", clip), os.path.join(media, "audio", clip))):
            if not os.path.exists(src):
                raise ExportError(f"missing {src}")
            shutil.copyfile(src, dst)

    out = os.path.join(app, "src", "lesson", "content", f"{language}-{name}.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")
    return out


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("outdir")
    p.add_argument("--language", required=True)
    p.add_argument("--lesson", type=int, required=True)
    p.add_argument("--level", default="1")
    p.add_argument("--app", default=os.path.join(ROOT, "app"))
    args = p.parse_args(argv)
    try:
        out = export(args.outdir, args.language.strip().lower(), args.lesson, args.level, args.app)
    except (ExportError, ValueError, KeyError, OSError) as e:
        sys.exit(f"error: {e}")
    print(f"done -> {out}")


if __name__ == "__main__":
    main()

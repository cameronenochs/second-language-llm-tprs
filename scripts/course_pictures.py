#!/usr/bin/env python3
"""
Pictures for a Comprehension Method course lesson.

Items that share a `scene` share one picture. Pictures are drawn six at a
time on a 3x2 sheet, then cut into tiles.

  course_pictures.py plan SCRIPT OUTDIR      write OUTDIR/pictures.json
  course_pictures.py prompts OUTDIR          write OUTDIR/sheets/prompts.md (needs OUTDIR/style.md)
  course_pictures.py provider                print gemini, grok or manual
  course_pictures.py render OUTDIR (--cast | --sheet N | --rest) [--provider P]
  course_pictures.py cut OUTDIR [--sheet N]  cut sheets into OUTDIR/pictures/<id>.png

Keys come only from GEMINI_API_KEY or XAI_API_KEY. Model overrides:
GEMINI_IMAGE_MODEL, XAI_IMAGE_MODEL.
"""
import argparse
import base64
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

PER_SHEET = 6
INSET = 0.04  # fraction of a tile trimmed on each side to drop gutters
GEMINI_MODEL = "gemini-3.1-flash-image-preview"
XAI_MODEL = "grok-imagine-image"
MANUAL_EXIT = 3


class ImageError(Exception):
    pass


def norm_scene(scene: str) -> str:
    return re.sub(r"\s+", " ", scene.strip().lower().rstrip("."))


def plan(items: list) -> dict:
    """Group items by scene, in first-appearance order, six pictures per sheet."""
    pictures, by_scene = [], {}
    for item in items:
        key = norm_scene(item["scene"])
        if key not in by_scene:
            n = len(pictures)
            by_scene[key] = {"id": f"p{n + 1:03d}", "scene": item["scene"].strip(), "items": [],
                             "sheet": n // PER_SHEET + 1, "tile": n % PER_SHEET + 1}
            pictures.append(by_scene[key])
        by_scene[key]["items"].append(item["id"])
    sheets = pictures[-1]["sheet"] if pictures else 0
    return {"sheets": sheets, "pictures": pictures}


def read_script(path: str) -> list:
    items = []
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
                if not (row["id"] and row["scene"].strip()):
                    raise ValueError
            except (ValueError, KeyError, TypeError, AttributeError):
                raise ValueError(f"{path} line {n}: item needs id and scene")
            items.append(row)
    return items


def sheet_path(outdir: str, n: int) -> str:
    return os.path.join(outdir, "sheets", f"sheet-{n:02d}.png")


def cast_prompt(style: str) -> str:
    return (f"{style.strip()}\n\nCharacter reference sheet: draw every recurring cast member described "
            "above, full body, standing side by side on a white background. No text, no labels.")


def sheet_prompt(style: str, scenes: list) -> str:
    lines = [f"{i}. {s}" for i, s in enumerate(scenes, 1)]
    lines += [f"{i}. Leave this panel empty white." for i in range(len(scenes) + 1, PER_SHEET + 1)]
    return (f"{style.strip()}\n\nDraw a grid of 6 equal panels: 3 across, 2 down, separated by wide white "
            "gutters. No borders, no text, no numbers, no speech bubbles. Panels in reading order, "
            "top row left to right, then bottom row:\n" + "\n".join(lines))


def sheet_scenes(pictures: dict, n: int) -> list:
    return [p["scene"] for p in pictures["pictures"] if p["sheet"] == n]


def detect_provider(env) -> str:
    if env.get("GEMINI_API_KEY"):
        return "gemini"
    if env.get("XAI_API_KEY"):
        return "grok"
    return "manual"


def post_json(url: str, payload: dict, headers: dict) -> dict:
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST",
                                 headers={"Content-Type": "application/json", **headers})
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        detail = e.read(2000).decode(errors="replace").strip() if e.fp else ""
        raise ImageError(f"image API error {e.code}: {detail}" if detail else f"image API error {e.code}")
    except (urllib.error.URLError, TimeoutError) as e:
        raise ImageError(f"network error: {getattr(e, 'reason', e)}")


def gemini_image(prompt: str, refs: list, env) -> bytes:
    model = env.get("GEMINI_IMAGE_MODEL") or GEMINI_MODEL
    parts = [{"text": prompt}]
    for ref in refs:
        with open(ref, "rb") as f:
            raw = f.read()
        mime = "image/jpeg" if raw[:2] == b"\xff\xd8" else "image/png"
        parts.append({"inline_data": {"mime_type": mime, "data": base64.b64encode(raw).decode()}})
    body = post_json(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        {"contents": [{"parts": parts}],
         "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "3:2"}}},
        {"x-goog-api-key": env["GEMINI_API_KEY"]},
    )
    for cand in body.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            data = (part.get("inlineData") or part.get("inline_data") or {}).get("data")
            if data:
                return base64.b64decode(data)
    raise ImageError("Gemini returned no image (it may have refused the prompt)")


def grok_image(prompt: str, env) -> bytes:
    body = post_json(
        "https://api.x.ai/v1/images/generations",
        {"model": env.get("XAI_IMAGE_MODEL") or XAI_MODEL, "prompt": prompt, "n": 1,
         "response_format": "b64_json"},
        {"Authorization": f"Bearer {env['XAI_API_KEY']}"},
    )
    try:
        return base64.b64decode(body["data"][0]["b64_json"])
    except (KeyError, IndexError, TypeError):
        raise ImageError("xAI returned no image")


def generate(provider: str, prompt: str, refs: list, out_path: str, env):
    data = gemini_image(prompt, refs, env) if provider == "gemini" else grok_image(prompt, env)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(data)


def write_prompts(outdir: str, pictures: dict, style: str) -> str:
    path = os.path.join(outdir, "sheets", "prompts.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    blocks = ["# Picture prompts", "",
              "Generate each image, then save it with the name in its heading, in this folder.",
              "Attach cast.png (and sheet-01.png once approved) as reference images if the tool allows.", "",
              "## cast.png (save in the lesson folder, one level up)", "", "```", cast_prompt(style), "```", ""]
    for n in range(1, pictures["sheets"] + 1):
        blocks += [f"## sheet-{n:02d}.png", "", "```", sheet_prompt(style, sheet_scenes(pictures, n)), "```", ""]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(blocks))
    return path


def cut_sheet(sheet: str, tiles: list, outdir: str):
    """tiles: [(tile_number 1-6, picture_id)]. Equal split with a small inset."""
    # shortcut: assumes an equal 3x2 grid, add gutter detection if sheets drift.
    os.makedirs(outdir, exist_ok=True)
    for tile, pid in tiles:
        row, col = divmod(tile - 1, 3)
        w, h = f"iw/3*{1 - 2 * INSET}", f"ih/2*{1 - 2 * INSET}"
        x, y = f"iw/3*{col + INSET}", f"ih/2*{row + INSET}"
        try:
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", sheet,
                            "-vf", f"crop={w}:{h}:{x}:{y}", "-frames:v", "1",
                            os.path.join(outdir, f"{pid}.png")], check=True, capture_output=True)
        except FileNotFoundError:
            raise ImageError("ffmpeg not found on PATH")
        except subprocess.CalledProcessError as e:
            raise ImageError(f"ffmpeg failed on {sheet}: {e.stderr.decode(errors='replace')[-300:]}")


def load(outdir: str, name: str) -> str:
    path = os.path.join(outdir, name)
    if not os.path.exists(path):
        raise ImageError(f"missing {path}")
    with open(path, encoding="utf-8") as f:
        return f.read()


def main(argv=None):
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("plan"); s.add_argument("script"); s.add_argument("outdir")
    s = sub.add_parser("prompts"); s.add_argument("outdir")
    sub.add_parser("provider")
    s = sub.add_parser("render"); s.add_argument("outdir")
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--cast", action="store_true")
    g.add_argument("--sheet", type=int)
    g.add_argument("--rest", action="store_true", help="every sheet after 1 that has no image yet")
    s.add_argument("--provider", choices=["gemini", "grok", "manual"])
    s = sub.add_parser("cut"); s.add_argument("outdir"); s.add_argument("--sheet", type=int)
    args = p.parse_args(argv)
    env = os.environ

    try:
        if args.cmd == "provider":
            print(detect_provider(env))
            return
        if args.cmd == "plan":
            pictures = plan(read_script(args.script))
            os.makedirs(args.outdir, exist_ok=True)
            with open(os.path.join(args.outdir, "pictures.json"), "w", encoding="utf-8") as f:
                json.dump(pictures, f, indent=2, ensure_ascii=False)
            print(f"{len(pictures['pictures'])} pictures on {pictures['sheets']} sheets")
            return

        pictures = json.loads(load(args.outdir, "pictures.json"))
        if args.cmd == "prompts":
            print(write_prompts(args.outdir, pictures, load(args.outdir, "style.md")))
            return

        if args.cmd == "cut":
            sheets = [args.sheet] if args.sheet else range(1, pictures["sheets"] + 1)
            for n in sheets:
                path = sheet_path(args.outdir, n)
                if not os.path.exists(path):
                    raise ImageError(f"missing {path}")
                tiles = [(pic["tile"], pic["id"]) for pic in pictures["pictures"] if pic["sheet"] == n]
                cut_sheet(path, tiles, os.path.join(args.outdir, "pictures"))
                print(f"cut sheet {n}: {len(tiles)} pictures")
            return

        # render
        style = load(args.outdir, "style.md")
        provider = args.provider or detect_provider(env)
        if provider == "manual":
            path = write_prompts(args.outdir, pictures, style)
            print(f"manual: no GEMINI_API_KEY or XAI_API_KEY. Generate the images from {path}")
            sys.exit(MANUAL_EXIT)
        cast = os.path.join(args.outdir, "cast.png")
        if args.cast:
            generate(provider, cast_prompt(style), [], cast, env)
            print(f"done -> {cast}")
            return
        if args.sheet:
            todo = [args.sheet]
        else:
            todo = [n for n in range(2, pictures["sheets"] + 1) if not os.path.exists(sheet_path(args.outdir, n))]
        for n in todo:
            if not 1 <= n <= pictures["sheets"]:
                raise ImageError(f"sheet {n} out of range 1..{pictures['sheets']}")
            refs = [r for r in (cast, sheet_path(args.outdir, 1)) if os.path.exists(r) and
                    os.path.abspath(r) != os.path.abspath(sheet_path(args.outdir, n))]
            generate(provider, sheet_prompt(style, sheet_scenes(pictures, n)), refs, sheet_path(args.outdir, n), env)
            print(f"done -> {sheet_path(args.outdir, n)}")
    except (ImageError, ValueError, OSError) as e:
        sys.exit(f"error: {e}")


if __name__ == "__main__":
    main()

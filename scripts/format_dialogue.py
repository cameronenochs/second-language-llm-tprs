#!/usr/bin/env python3
"""Normalize a Teacher:/Learner: dialogue for the ElevenLabs audio script.

Usage:
  format_dialogue.py IN OUT [--or-word WORD] [--model MODEL_ID]
"""
import argparse
import re

DEFAULT_MARKERS = frozenset({"pause", "slowly"})
MODEL_MARKERS = {"eleven_v4": DEFAULT_MARKERS}

_SPEAKER_RE = re.compile(r"^(Teacher|Learner):")
_MARKER_RE = re.compile(r"\[([^\]]+)\]")
_DUP_RE = re.compile(r"(\[\w+\])(?:\s+\1)+")


def _format_line(line: str, allowed_markers, or_word) -> str:
    def keep(m):
        name = m.group(1).strip().lower()
        return f"[{name}]" if name in allowed_markers else ""

    line = _MARKER_RE.sub(keep, line)
    line = re.sub(r"\s+", " ", line).strip()
    line = re.sub(r"\s+([?,.!])", r"\1", line)
    line = _DUP_RE.sub(r"\1", line)
    if or_word and line.endswith("?"):
        pat = re.compile(rf"(?:\s*,)?(?:\s*\[pause\])?\s+{re.escape(or_word)}\b")
        matches = list(pat.finditer(line))
        if matches:
            m = matches[-1]
            pause = "[pause] " if "pause" in allowed_markers else ""
            line = f"{line[:m.start()]}, {pause}{or_word}{line[m.end():]}"
    return line


def format_dialogue(text: str, allowed_markers: frozenset = DEFAULT_MARKERS, or_word=None) -> str:
    text = text.replace("\r\n", "\n")
    return "\n".join(
        _format_line(l, allowed_markers, or_word) if _SPEAKER_RE.match(l) else l
        for l in text.split("\n")
    )


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("input")
    p.add_argument("output")
    p.add_argument("--or-word")
    p.add_argument("--model", default="eleven_v4")
    args = p.parse_args(argv)
    markers = MODEL_MARKERS.get(args.model, DEFAULT_MARKERS)
    with open(args.input, encoding="utf-8") as f:
        out = format_dialogue(f.read(), markers, args.or_word)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

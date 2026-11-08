#!/usr/bin/env python3
"""
Check a course script's lemmas against a core frequency list.

  core_vocab.py fetch --language L          download the list to data/core-vocab/<L>.tsv (gitignored)
  core_vocab.py check SCRIPT --language L   print every lemma not on the list, with its first item id

The list is fetched, not committed, because its source states no licence.
Lemmas are compared lowercase with macrons and other diacritics removed.
Exit status: 0 when every lemma is on the list, 1 when some are not (log each in deviations.md).
"""
import argparse
import html
import json
import os
import re
import sys
import unicodedata
import urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
LIST_DIR = os.path.join(ROOT, "data", "core-vocab")
SOURCES = {
    # Dickinson College Commentaries Latin Core Vocabulary (about 1,000 most frequent lemmas).
    "latin": "https://dcc.dickinson.edu/latin-core-list1",
}
# Parts of speech whose headword lists spelling variants rather than principal parts or endings.
VARIANT_POS = ("Preposition", "Conjunction", "Adverb", "Interjection", "Particle")


def key(word: str) -> str:
    plain = unicodedata.normalize("NFD", word.strip().lower())
    return "".join(c for c in plain if not unicodedata.combining(c))


def parse_dcc(page: str) -> list:
    """Return (lemma_key, rank, headword, pos) rows from the DCC table."""
    def cell(row, name):
        m = re.search(r'views-field-field-' + name + r'"[^>]*>(.*?)</td>', row, re.S)
        return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", m.group(1))).split()) if m else ""

    rows = []
    for row in re.findall(r"<tr.*?</tr>", page, re.S):
        head = cell(row, "display-headwords")
        if not head:
            continue
        pos, rank = cell(row, "part-of-speech"), cell(row, "frequency-rank")
        tokens = [t.strip(",;") for t in head.split()]
        forms = tokens if pos.startswith(VARIANT_POS) else tokens[:1]
        for form in forms:
            if form and not form.startswith("-") and not form.endswith("."):
                rows.append((key(form), rank, head, pos))
    return rows


def fetch(language: str) -> str:
    if language not in SOURCES:
        raise SystemExit(f"error: no core list known for {language}; known: {', '.join(SOURCES)}")
    req = urllib.request.Request(SOURCES[language], headers={"User-Agent": "course-builder"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        rows = parse_dcc(resp.read().decode("utf-8", errors="replace"))
    if len(rows) < 500:
        raise SystemExit(f"error: parsed only {len(rows)} rows; the source page may have changed")
    os.makedirs(LIST_DIR, exist_ok=True)
    path = os.path.join(LIST_DIR, f"{language}.tsv")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# source: {SOURCES[language]}\n# lemma\trank\theadword\tpos\n")
        for r in rows:
            f.write("\t".join(r) + "\n")
    return path


def load_list(language: str) -> set:
    path = os.path.join(LIST_DIR, f"{language}.tsv")
    if not os.path.exists(path):
        raise SystemExit(f"error: {path} missing; run: python3 scripts/core_vocab.py fetch --language {language}")
    with open(path, encoding="utf-8") as f:
        return {line.split("\t", 1)[0] for line in f if line.strip() and not line.startswith("#")}


def off_list(items: list, core: set) -> dict:
    """Map each lemma not in core to the first item id that uses it, in script order."""
    out = {}
    for item in items:
        for lemma in item.get("lemmas", []):
            if key(lemma) not in core:
                out.setdefault(lemma, item["id"])
    return out


def main(argv=None):
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("fetch"); s.add_argument("--language", required=True)
    s = sub.add_parser("check"); s.add_argument("script"); s.add_argument("--language", required=True)
    args = p.parse_args(argv)
    language = args.language.strip().lower()
    if args.cmd == "fetch":
        print(f"done -> {fetch(language)}")
        return
    with open(args.script, encoding="utf-8") as f:
        items = [json.loads(line) for line in f if line.strip()]
    missing = off_list(items, load_list(language))
    for lemma, item_id in missing.items():
        print(f"OFF-LIST  {lemma}  (first used {item_id})")
    print(f"{len(missing)} lemma(s) off the {language} core list")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()

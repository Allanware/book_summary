#!/usr/bin/env python3
"""Validate generated keyword cards in book-data.js against candidate and coverage rules."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Set

CANONICAL_LABEL = {
    "slave labor": "slavery",
}

VALID_GROUPS = {"mechanisms", "institutions-actors", "places-regions"}


def parse_candidates(path: Path) -> Dict[str, Set[int]]:
    out: Dict[str, Set[int]] = {}
    row_re = re.compile(r"- `([^`]+)` — chapters: ([0-9, ]+) \(n=(\d+)\) —")

    for line in path.read_text().splitlines():
        match = row_re.match(line)
        if not match:
            continue
        label = match.group(1).strip()
        chapters = {int(value.strip()) for value in match.group(2).split(",") if value.strip()}

        canonical = CANONICAL_LABEL.get(label, label)
        out.setdefault(canonical, set()).update(chapters)

    if not out:
        raise ValueError("No keyword candidates parsed")

    return out


def load_book_data(book_data_path: Path) -> Dict:
    script = (
        "import { pathToFileURL } from 'node:url';"
        "const mod = await import(pathToFileURL(process.argv[1]).href);"
        "console.log(JSON.stringify(mod.default));"
    )

    proc = subprocess.run(
        ["node", "--input-type=module", "-e", script, str(book_data_path.resolve())],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout)


def validate(data: Dict, candidate_hits: Dict[str, Set[int]]) -> List[str]:
    errors: List[str] = []

    themes = data.get("themes", [])
    if not isinstance(themes, list):
        return ["BOOK_DATA.themes is not a list"]

    label_index: Dict[str, Dict] = {}
    alias_set: Set[str] = set()

    for theme in themes:
        label = theme.get("label")
        if not isinstance(label, str):
            errors.append("Theme with non-string label found")
            continue
        key = label.lower()
        if key in label_index:
            errors.append(f"Duplicate theme label: {label}")
        label_index[key] = theme

        group = theme.get("group")
        if group not in VALID_GROUPS:
            errors.append(f"Theme '{label}' has invalid group: {group}")

        aliases = theme.get("aliases", [])
        if not isinstance(aliases, list):
            errors.append(f"Theme '{label}' aliases is not a list")
            aliases = []
        for alias in aliases:
            if isinstance(alias, str):
                alias_set.add(alias.lower())
            else:
                errors.append(f"Theme '{label}' has non-string alias")

    # Candidate representation check.
    for canonical in candidate_hits:
        if canonical.lower() not in label_index and canonical.lower() not in alias_set:
            errors.append(f"Candidate keyword not represented: {canonical}")

    # Candidate chapter-hit coverage + application shape.
    for canonical_label, chapters in candidate_hits.items():
        theme = label_index.get(canonical_label.lower())
        if not theme:
            continue

        applications = theme.get("applications", [])
        if not isinstance(applications, list):
            errors.append(f"Theme '{canonical_label}' applications is not a list")
            continue

        chapter_counts: Dict[int, int] = {}
        for app in applications:
            chapter = app.get("chapter")
            if not isinstance(chapter, int):
                errors.append(f"Theme '{canonical_label}' has application with non-integer chapter")
                continue
            chapter_counts[chapter] = chapter_counts.get(chapter, 0) + 1

            for key in ("setting", "time", "point"):
                value = app.get(key)
                if not isinstance(value, str) or not value.strip():
                    errors.append(f"Theme '{canonical_label}' chapter {chapter} has empty {key}")

            evidence = app.get("evidence")
            if not isinstance(evidence, list) or not evidence:
                errors.append(f"Theme '{canonical_label}' chapter {chapter} has empty evidence[]")
            else:
                for item in evidence:
                    if not isinstance(item, str) or not item.strip():
                        errors.append(f"Theme '{canonical_label}' chapter {chapter} has blank evidence item")
                        continue
                    if re.search(r"\(p\.\s*\d+", item) is None:
                        errors.append(
                            f"Theme '{canonical_label}' chapter {chapter} evidence missing page citation"
                        )

        for chapter in chapters:
            if chapter_counts.get(chapter, 0) < 1:
                errors.append(
                    f"Theme '{canonical_label}' expected at least one application for chapter {chapter}; "
                    f"found {chapter_counts.get(chapter, 0)}"
                )

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate keyword cards")
    parser.add_argument("--book-data", default="book-data.js")
    parser.add_argument("--keyword-candidates", default="keyword_candidates.md")
    args = parser.parse_args()

    candidate_hits = parse_candidates(Path(args.keyword_candidates))
    data = load_book_data(Path(args.book_data))
    errors = validate(data, candidate_hits)

    if errors:
        print("Validation failed:")
        for err in errors:
            print(f"- {err}")
        raise SystemExit(1)

    print("Validation passed")


if __name__ == "__main__":
    main()

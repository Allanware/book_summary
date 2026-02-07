#!/usr/bin/env python3
"""Check that AGENTS.md still reflects the live website structure."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import List, Tuple


def load_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    return path.read_text()


def require_phrase(agents_text: str, phrase: str, errors: List[str]) -> None:
    if phrase not in agents_text:
        errors.append(f"AGENTS.md missing required phrase: {phrase}")


def require_if_present(
    source_text: str,
    source_regex: str,
    agents_text: str,
    required_phrase: str,
    errors: List[str],
) -> None:
    if re.search(source_regex, source_text, re.MULTILINE):
        require_phrase(agents_text, required_phrase, errors)


def validate(
    agents_text: str,
    index_text: str,
    script_text: str,
    styles_text: str,
) -> List[str]:
    errors: List[str] = []

    # Always-required core references.
    for phrase in (
        "index.html",
        "script.js",
        "styles.css",
        "book-data.js",
        "book-data.zh.js",
        "chapters/index.js",
        "chapters/index.zh.js",
        "scripts/keyword_candidates.py",
        "scripts/build_keyword_cards.py",
        "scripts/validate_keyword_cards.py",
    ):
        require_phrase(agents_text, phrase, errors)

    # Feature-linked requirements.
    feature_checks: Tuple[Tuple[str, str], ...] = (
        (r"language-switch", "language switch"),
        (r"book-data\.zh\.js", "book-data.zh.js"),
        (r"index\.zh\.js", "chapters/index.zh.js"),
        (r"flowSections", "flowSections"),
        (r"chapter\.flow", "legacy `flow` path"),
        (r"chapter\.argument", "legacy `argument` + `evidence` path"),
        (r"buildThemeDefinition", "Current renderer fallback"),
        (r"setLanguage", "Bilingual parity requirements"),
        (r"collapseAllThreadGroups", "Groups are collapsible and collapsed by default"),
    )
    for source_regex, required_phrase in feature_checks:
        require_if_present(script_text, source_regex, agents_text, required_phrase, errors)

    # UI styles confirm grouped keyword structure still exists.
    require_if_present(styles_text, r"thread-group", agents_text, "Keyword UI contract", errors)
    require_if_present(styles_text, r"thread-group-list", agents_text, "two columns", errors)

    # Validation workflow command coverage.
    for phrase in (
        "python3 scripts/keyword_candidates.py",
        "python3 scripts/build_keyword_cards.py",
        "python3 scripts/validate_keyword_cards.py",
    ):
        require_phrase(agents_text, phrase, errors)

    # If language switch exists in index, AGENTS must mention bilingual parity.
    require_if_present(index_text, r"id=\"languageSwitch\"", agents_text, "Bilingual parity requirements", errors)

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Check AGENTS.md sync with site structure")
    parser.add_argument("--agents", default="AGENTS.md")
    parser.add_argument("--index", default="index.html")
    parser.add_argument("--script", default="script.js")
    parser.add_argument("--styles", default="styles.css")
    args = parser.parse_args()

    agents_path = Path(args.agents)
    index_path = Path(args.index)
    script_path = Path(args.script)
    styles_path = Path(args.styles)

    agents_text = load_text(agents_path)
    index_text = load_text(index_path)
    script_text = load_text(script_path)
    styles_text = load_text(styles_path)

    errors = validate(agents_text, index_text, script_text, styles_text)
    if errors:
        print("AGENTS sync check failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("AGENTS sync check passed")


if __name__ == "__main__":
    main()

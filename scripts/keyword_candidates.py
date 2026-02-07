#!/usr/bin/env python3
"""Generate keyword candidates from extracted chapter text (book-agnostic)."""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Set, Tuple

SECTION_TO_GROUP = (
    ("Mechanisms", "mechanisms"),
    ("Institutions & Actors", "institutions-actors"),
    ("Places & Regions", "places-regions"),
)

WORD_RE = re.compile(r"[A-Za-z][A-Za-z'/-]*")
CAP_PHRASE_RE = re.compile(r"\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b")
CHAPTER_FILE_RE = re.compile(r"chap(\d+)\.txt$")
CHAPTER_HEADER_RE = re.compile(r"^\s*chapter\s+\w+", re.I)
PAGE_RE = re.compile(r"^\s*\d+\s*$")
SAMPLE_MARKER_RE = re.compile(r"^\s*-{2,}\s*\[(?:middle|end|begin)\s+sample\]\s*-{2,}\s*$", re.I)

ABSTRACT_SUFFIX_RE = re.compile(
    r"(?:tion|sion|ment|ism|ity|ness|ship|ization|isation|ality|ence|ance|hood|dom|tions|sions|ments|isms|ities)$"
)
ACTOR_SUFFIX_RE = re.compile(r"(?:ers|ors|ists|ants|ees|men|women)$")
DEMONYM_SUFFIX_RE = re.compile(r"(?:ian|ese|ish)$")

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "been",
    "being",
    "but",
    "by",
    "can",
    "could",
    "did",
    "do",
    "does",
    "done",
    "for",
    "from",
    "had",
    "has",
    "have",
    "he",
    "her",
    "hers",
    "him",
    "his",
    "i",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "itself",
    "just",
    "may",
    "might",
    "more",
    "most",
    "no",
    "not",
    "of",
    "on",
    "or",
    "our",
    "ours",
    "ourselves",
    "out",
    "over",
    "own",
    "same",
    "shall",
    "she",
    "should",
    "so",
    "some",
    "such",
    "than",
    "that",
    "the",
    "their",
    "theirs",
    "them",
    "themselves",
    "then",
    "there",
    "these",
    "they",
    "this",
    "those",
    "through",
    "to",
    "too",
    "under",
    "until",
    "up",
    "very",
    "was",
    "we",
    "were",
    "what",
    "when",
    "where",
    "which",
    "while",
    "who",
    "whom",
    "why",
    "will",
    "with",
    "would",
    "you",
    "your",
    "yours",
    "yourself",
    "yourselves",
    "also",
    "however",
    "therefore",
    "thus",
    "hence",
    "yet",
    "still",
    "even",
    "only",
    "once",
    "again",
    "almost",
    "across",
    "around",
    "during",
    "before",
    "after",
    "within",
    "without",
    "because",
    "among",
    "between",
    "upon",
    "amid",
    "amidst",
    "throughout",
    "near",
    "far",
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
    "twenty",
}

GENERIC_DROP_WORDS = {
    "important",
    "significant",
    "major",
    "small",
    "large",
    "ability",
    "conditions",
    "early",
    "late",
    "another",
    "others",
    "question",
    "thanks",
    "indeed",
    "furthermore",
    "business",
    "city",
    "cities",
    "quality",
    "quantities",
}

DIRECTION_WORDS = {"north", "south", "east", "west", "central"}
LOCATIVE_PREPOSITIONS = {
    "in",
    "at",
    "from",
    "to",
    "into",
    "within",
    "across",
    "between",
    "near",
    "around",
    "through",
}


@dataclass
class PhraseStat:
    chapters: Set[int]
    count: int = 0
    locative_prefix_hits: int = 0
    left_contexts: Set[str] = field(default_factory=set)
    right_contexts: Set[str] = field(default_factory=set)


@dataclass
class Candidate:
    label: str
    chapters: List[int]
    group: str
    score: int


def tokenize(text: str) -> List[str]:
    tokens: List[str] = []
    for match in WORD_RE.finditer(text):
        token = match.group(0).lower().strip("'")
        if token:
            tokens.append(token)
    return tokens


def normalize_line(line: str) -> str:
    lowered = line.lower().strip()
    lowered = re.sub(r"\d+", " ", lowered)
    lowered = re.sub(r"[^a-z ]+", " ", lowered)
    return re.sub(r"\s+", " ", lowered).strip()


def discover_boilerplate_lines(chapter_lines: Dict[int, List[str]]) -> Set[str]:
    chapter_count = len(chapter_lines)
    if chapter_count < 3:
        return set()

    line_hits: Dict[str, Set[int]] = defaultdict(set)
    for chapter_id, lines in chapter_lines.items():
        seen: Set[str] = set()
        for line in lines:
            normalized = normalize_line(line)
            if not normalized:
                continue
            word_count = len(normalized.split())
            if word_count == 0 or word_count > 10:
                continue
            seen.add(normalized)
        for normalized in seen:
            line_hits[normalized].add(chapter_id)

    threshold = max(3, int(chapter_count * 0.6))
    return {
        line
        for line, chapters in line_hits.items()
        if len(chapters) >= threshold
    }


def load_chapters(tmp_dir: Path) -> Dict[int, str]:
    chapter_files = sorted(tmp_dir.glob("chap[0-9][0-9].txt"))
    raw_lines_by_chapter: Dict[int, List[str]] = {}

    for chapter_file in chapter_files:
        match = CHAPTER_FILE_RE.search(chapter_file.name)
        if not match:
            continue
        chapter_id = int(match.group(1))

        lines = chapter_file.read_text(errors="ignore").splitlines()
        cleaned_lines: List[str] = []
        for line in lines:
            if PAGE_RE.match(line):
                continue
            if CHAPTER_HEADER_RE.match(line):
                continue
            if SAMPLE_MARKER_RE.match(line):
                continue
            if not line.strip():
                continue
            cleaned_lines.append(line)

        if cleaned_lines:
            raw_lines_by_chapter[chapter_id] = cleaned_lines

    if not raw_lines_by_chapter:
        raise SystemExit(f"No chapter files found in {tmp_dir}. Expected chap01.txt..chapNN.txt")

    boilerplate_lines = discover_boilerplate_lines(raw_lines_by_chapter)
    chapters: Dict[int, str] = {}

    for chapter_id, lines in raw_lines_by_chapter.items():
        filtered_lines: List[str] = []
        for line in lines:
            if normalize_line(line) in boilerplate_lines:
                continue
            filtered_lines.append(line)

        text = "\n".join(filtered_lines)
        text = re.sub(r"-\n", "", text)
        text = text.replace("\n", " ")
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            chapters[chapter_id] = text

    return chapters


def valid_word(word: str) -> bool:
    if len(word) < 3:
        return False
    if word in STOPWORDS or word in GENERIC_DROP_WORDS:
        return False
    if word.isdigit():
        return False
    if re.fullmatch(r"[ivxlcdm]+", word):
        return False
    return True


def extract_proper_phrase_hits(chapters: Dict[int, str], min_chapters: int) -> Dict[str, Set[int]]:
    hits: Dict[str, Set[int]] = defaultdict(set)

    for chapter_id, text in chapters.items():
        for match in CAP_PHRASE_RE.finditer(text):
            phrase = match.group(0).lower().strip()
            if not phrase:
                continue
            words = phrase.split()
            if any(word in STOPWORDS for word in words):
                continue
            hits[phrase].add(chapter_id)

    return {phrase: chapter_set for phrase, chapter_set in hits.items() if len(chapter_set) >= min_chapters}


def extract_phrase_stats(chapters: Dict[int, str], min_chapters: int, max_ngram: int) -> Dict[str, PhraseStat]:
    stats: Dict[str, PhraseStat] = defaultdict(lambda: PhraseStat(chapters=set(), count=0))
    total_chapters = len(chapters)

    for chapter_id, text in chapters.items():
        tokens = tokenize(text)
        seen_in_chapter: Set[str] = set()

        for index in range(len(tokens)):
            for ngram_size in range(1, max_ngram + 1):
                end_index = index + ngram_size
                if end_index > len(tokens):
                    break

                words = tokens[index:end_index]
                if any(not valid_word(word) for word in words):
                    continue

                phrase = " ".join(words)
                if len(phrase) > 48:
                    continue

                stat = stats[phrase]
                stat.count += 1
                if phrase not in seen_in_chapter:
                    stat.chapters.add(chapter_id)
                    seen_in_chapter.add(phrase)

                left = tokens[index - 1] if index > 0 else ""
                right = tokens[end_index] if end_index < len(tokens) else ""
                if left and valid_word(left):
                    stat.left_contexts.add(left)
                if right and valid_word(right):
                    stat.right_contexts.add(right)
                if left in LOCATIVE_PREPOSITIONS:
                    stat.locative_prefix_hits += 1

    filtered: Dict[str, PhraseStat] = {}
    for phrase, stat in stats.items():
        chapter_count = len(stat.chapters)
        if chapter_count < min_chapters:
            continue
        if len(phrase.split()) == 1 and stat.count < chapter_count + 1:
            continue
        context_richness = len(stat.left_contexts) + len(stat.right_contexts)
        if chapter_count == total_chapters and stat.count <= chapter_count + 2 and context_richness <= 2:
            continue
        filtered[phrase] = stat

    return filtered


def is_abstract_word(word: str) -> bool:
    return bool(ABSTRACT_SUFFIX_RE.search(word))


def singularize_token(word: str) -> str:
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"
    if word.endswith("ches") or word.endswith("shes"):
        return word[:-2]
    if word.endswith(("ses", "xes", "zes")) and len(word) > 4:
        return word[:-2]
    if word.endswith("s") and len(word) > 3 and not word.endswith("ss"):
        return word[:-1]
    return word


def infer_role_terms(
    phrase_stats: Dict[str, PhraseStat],
    min_chapters: int,
    total_chapters: int,
) -> Set[str]:
    head_modifiers: Dict[str, Set[str]] = defaultdict(set)
    head_chapter_hits: Dict[str, Set[int]] = defaultdict(set)

    for phrase, stat in phrase_stats.items():
        words = phrase.split()
        if len(words) < 2:
            continue
        head = words[-1]
        modifier = words[-2]
        if not valid_word(head) or not valid_word(modifier):
            continue
        head_modifiers[head].add(modifier)
        head_chapter_hits[head].update(stat.chapters)

    role_terms: Set[str] = set()
    for head, modifiers in head_modifiers.items():
        chapter_count = len(head_chapter_hits[head])
        if chapter_count < min_chapters:
            continue
        if chapter_count >= total_chapters:
            continue
        if is_abstract_word(head):
            continue

        if ACTOR_SUFFIX_RE.search(head):
            role_terms.add(head)
            continue

        if len(modifiers) >= 4:
            role_terms.add(head)

    expanded_terms: Set[str] = set(role_terms)
    for term in list(role_terms):
        singular = singularize_token(term)
        if singular != term and valid_word(singular):
            expanded_terms.add(singular)
        plural = f"{term}s"
        if plural in head_modifiers or plural in role_terms:
            expanded_terms.add(plural)

    return expanded_terms


def is_actor_word(word: str, role_terms: Set[str]) -> bool:
    return word in role_terms or bool(ACTOR_SUFFIX_RE.search(word))


def looks_like_place_phrase(phrase: str, stat: PhraseStat, is_proper_phrase: bool, role_terms: Set[str]) -> bool:
    words = phrase.split()
    if any(word in DIRECTION_WORDS for word in words) and len(words) >= 2:
        return True

    if not is_proper_phrase:
        return False

    if len(words) >= 2:
        if any(is_actor_word(word, role_terms) for word in words):
            return False
        return stat.locative_prefix_hits >= 1 or len(stat.chapters) >= 4

    single_word = words[0]
    if is_actor_word(single_word, role_terms):
        return False
    if DEMONYM_SUFFIX_RE.search(single_word):
        return stat.locative_prefix_hits >= 4
    return stat.locative_prefix_hits >= 2


def is_interesting_phrase(
    phrase: str,
    stat: PhraseStat,
    is_proper_phrase: bool,
    role_terms: Set[str],
) -> bool:
    words = phrase.split()

    if any(word in GENERIC_DROP_WORDS for word in words):
        return False

    if len(words) == 1:
        word = words[0]
        if word in DIRECTION_WORDS:
            return False
        if word.endswith("'s"):
            return False
        if DEMONYM_SUFFIX_RE.search(word) and not is_proper_phrase:
            return False

    if looks_like_place_phrase(phrase, stat, is_proper_phrase, role_terms):
        return True
    if any(is_actor_word(word, role_terms) for word in words):
        return True
    if any(is_abstract_word(word) for word in words):
        return True
    if is_proper_phrase and len(words) >= 2:
        return True

    context_richness = len(stat.left_contexts) + len(stat.right_contexts)
    if len(words) >= 2 and context_richness >= 4:
        return True

    return False


def classify_group(
    phrase: str,
    stat: PhraseStat,
    is_proper_phrase: bool,
    role_terms: Set[str],
) -> str:
    words = phrase.split()
    if looks_like_place_phrase(phrase, stat, is_proper_phrase, role_terms):
        return "places-regions"
    if any(is_actor_word(word, role_terms) for word in words):
        return "institutions-actors"
    return "mechanisms"


def score_phrase(
    phrase: str,
    stat: PhraseStat,
    is_proper_phrase: bool,
    group: str,
    role_terms: Set[str],
) -> int:
    words = phrase.split()
    chapter_count = len(stat.chapters)

    score = chapter_count * 6 + min(stat.count, 30)
    if len(words) > 1:
        score += 5
    if is_proper_phrase:
        score += 4
    if any(is_abstract_word(word) for word in words):
        score += 4
    if any(is_actor_word(word, role_terms) for word in words):
        score += 3
    if group == "places-regions":
        score += min(stat.locative_prefix_hits, 4)
    return score


def rationale_for_group(group: str) -> str:
    if group == "mechanisms":
        return "recurring mechanism term in the book's political economy"
    if group == "institutions-actors":
        return "recurring institution or actor in the book's argument"
    return "recurring geographic node or regional context in the book"


def collect_candidates(
    chapters: Dict[int, str],
    min_chapters: int,
    max_ngram: int,
    max_per_group: int,
) -> Dict[str, List[Candidate]]:
    proper_phrase_hits = extract_proper_phrase_hits(chapters, min_chapters)
    phrase_stats = extract_phrase_stats(chapters, min_chapters, max_ngram)
    role_terms = infer_role_terms(phrase_stats, min_chapters=min_chapters, total_chapters=len(chapters))

    grouped: Dict[str, List[Candidate]] = {
        "mechanisms": [],
        "institutions-actors": [],
        "places-regions": [],
    }

    for phrase, stat in phrase_stats.items():
        is_proper_phrase = phrase in proper_phrase_hits
        if not is_interesting_phrase(phrase, stat, is_proper_phrase, role_terms):
            continue

        group = classify_group(phrase, stat, is_proper_phrase, role_terms)
        score = score_phrase(phrase, stat, is_proper_phrase, group, role_terms)

        grouped[group].append(
            Candidate(
                label=phrase,
                chapters=sorted(stat.chapters),
                group=group,
                score=score,
            )
        )

    for group in grouped:
        grouped[group].sort(
            key=lambda candidate: (
                -candidate.score,
                -len(candidate.chapters),
                -len(candidate.label.split()),
                candidate.label,
            )
        )
        grouped[group] = grouped[group][:max_per_group]

    return grouped


def format_list(label: str, hits: Sequence[int], rationale: str) -> str:
    chapter_text = ", ".join(str(chapter) for chapter in hits)
    return f"- `{label}` — chapters: {chapter_text} (n={len(hits)}) — {rationale}"


def parse_candidate_labels(path: Path) -> Set[str]:
    labels: Set[str] = set()
    row_re = re.compile(r"- `([^`]+)` — chapters: ([0-9, ]+) \(n=(\d+)\) —")
    for line in path.read_text().splitlines():
        match = row_re.match(line)
        if match:
            labels.add(match.group(1).strip())
    return labels


def maybe_print_overlap(compare_path: Path, grouped_candidates: Dict[str, List[Candidate]]) -> None:
    if not compare_path.exists():
        print(f"Compare file not found: {compare_path}")
        return

    baseline = parse_candidate_labels(compare_path)
    generated = {
        candidate.label
        for candidates in grouped_candidates.values()
        for candidate in candidates
    }
    if not baseline:
        print(f"No baseline labels parsed from: {compare_path}")
        return

    overlap = baseline & generated
    union = baseline | generated
    recall = len(overlap) / len(baseline)
    jaccard = len(overlap) / len(union) if union else 0.0

    print(
        "Overlap summary: "
        f"baseline={len(baseline)} generated={len(generated)} overlap={len(overlap)} "
        f"recall={recall:.3f} jaccard={jaccard:.3f}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate keyword candidate list from chapter text (book-agnostic)."
    )
    parser.add_argument(
        "--tmp-dir",
        default="tmp/chapters",
        help="Directory containing chap01.txt..chapNN.txt",
    )
    parser.add_argument(
        "--min-chapters",
        type=int,
        default=3,
        help="Minimum chapter count to include a candidate",
    )
    parser.add_argument(
        "--max-ngram",
        type=int,
        default=3,
        help="Maximum n-gram length for candidate mining",
    )
    parser.add_argument(
        "--max-per-group",
        type=int,
        default=22,
        help="Maximum candidates to emit per group",
    )
    parser.add_argument(
        "--compare-file",
        default="",
        help="Optional markdown candidate file for overlap reporting",
    )
    parser.add_argument(
        "--out",
        default="keyword_candidates.md",
        help="Output markdown file",
    )
    args = parser.parse_args()

    tmp_dir = Path(args.tmp_dir)
    chapters = load_chapters(tmp_dir)
    grouped_candidates = collect_candidates(
        chapters=chapters,
        min_chapters=args.min_chapters,
        max_ngram=args.max_ngram,
        max_per_group=args.max_per_group,
    )

    lines: List[str] = []
    lines.append("# Keyword Candidates")
    lines.append("")
    lines.append(f"Source: `{tmp_dir}/chap01.txt` … `chapNN.txt`")
    lines.append(f"Minimum chapters: {args.min_chapters}")
    lines.append("")

    for section_title, group in SECTION_TO_GROUP:
        lines.append(f"## {section_title}")
        candidates = grouped_candidates[group]
        if not candidates:
            lines.append("- (no items meet threshold)")
            lines.append("")
            continue
        rationale = rationale_for_group(group)
        for candidate in candidates:
            lines.append(format_list(candidate.label, candidate.chapters, rationale))
        lines.append("")

    out_path = Path(args.out)
    out_path.write_text("\n".join(lines))
    print(f"Wrote {out_path}")

    if args.compare_file:
        maybe_print_overlap(Path(args.compare_file), grouped_candidates)


if __name__ == "__main__":
    main()

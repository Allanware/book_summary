#!/usr/bin/env python3
"""Generate keyword cards from keyword_candidates.md and extracted chapter text.

This script builds BOOK_DATA.themes[] content and can patch book-data.js in place.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

SECTION_TO_GROUP = {
    "Mechanisms": "mechanisms",
    "Institutions & Actors": "institutions-actors",
    "Places & Regions": "places-regions",
}

GROUP_ORDER = ["mechanisms", "institutions-actors", "places-regions"]

CANONICAL_LABEL = {
    "slave labor": "slavery",
}

CANDIDATE_PATTERN_OVERRIDES = {
    "credit": r"\bcredit\b",
    "industrial capitalism": r"\bindustrial\s+capitalism\b",
    "mechanization": r"\bmechaniz\w*|\bmachinery\b|\bmachine\w*",
    "war capitalism": r"\bwar\s+capitalism\b",
    "mobilization": r"\bmobiliz\w*",
    "price signals": r"\bprice\w*",
    "slavery": r"\bslaver\w*",
    "capital accumulation": r"\baccumul\w*",
    "colonial rule": r"\bcolonial\w*",
    "market integration": r"\bintegrat\w*",
    "productivity": r"\bproductiv\w*",
    "coercion": r"\bcoerc\w*",
    "commodification": r"\bcommodif\w*|\bcommodity\b",
    "expropriation": r"\bexpropriat\w*|\bdispossess\w*|\bseiz\w+\b",
    "imperialism": r"\bimperial\w*",
    "industrialization": r"\bindustrializ\w*",
    "protectionism (tariff policy)": r"\bprotect\w*",
    "global capitalism": r"\bglobal\s+capitalism\b",
    "political economy": r"\bpolitical\s+economy\b",
    "slave labor": r"\bslave\s+labor\b|\bslave\s+labour\b",
    "wage labor": r"\bwage\s+labor\b|\bwage\s+labour\b",
    "discipline": r"\bdisciplin\w*",
    "merchants": r"\bmerchants?\b",
    "state": r"\bstate\b|\bstates\b",
    "empire": r"\bempire\b|\bempires\b",
    "manufacturers": r"\bmanufacturers?\b",
    "workers": r"\bworkers?\b|\blaborers?\b",
    "slaves/enslaved": r"\bslaves?\b|\benslaved\b",
    "capitalists": r"\bcapitalists?\b",
    "planters": r"\bplanters?\b",
    "growers/cultivators": r"\bgrowers?\b|\bcultivators?\b",
    "spinners": r"\bspinners?\b",
    "weavers": r"\bweavers?\b",
    "peasants": r"\bpeasants?\b",
    "exchange": r"\bexchange\b|\bexchanges\b",
    "bank": r"\bbank\b|\bbanks\b|\bbanking\b",
    "chamber of commerce": r"\bchamber\s+of\s+commerce\b|\bchamber\s+commerce\b",
    "britain/england": r"\bbritain\b|\bbritish\b|\bengland\b|\bgreat\s+britain\b",
    "europe": r"\beurope\b|\beuropean\b",
    "india": r"\bindia\b|\bindian\b",
    "americas": r"\bamerica\b|\bamerican\b|\bamericas\b",
    "united states": r"\bunited\s+states\b",
    "american south": r"\bamerican\s+south\b|\bthe\s+south\b",
    "china": r"\bchina\b|\bchinese\b",
    "brazil": r"\bbrazil\b|\bbrazilian\b",
    "africa": r"\bafrica\b|\bafrican\b",
    "atlantic": r"\batlantic\b",
    "north america": r"\bnorth\s+america\b",
    "liverpool": r"\bliverpool\b",
    "manchester": r"\bmanchester\b",
    "lancashire": r"\blancashire\b",
    "egypt": r"\begypt\b|\begyptian\b",
    "new york": r"\bnew\s+york\b",
    "west africa": r"\bwest\s+africa\b",
    "central asia": r"\bcentral\s+asia\b",
}

CORE_THEMES = [
    {
        "id": "labor-regimes",
        "label": "labor-regimes",
        "description": "How labor is organized, disciplined, and coerced across cotton production.",
        "definition": "Labor regimes names how states, merchants, planters, and manufacturers organized work through household labor, slavery, wage labor, sharecropping, and migration across cotton regions from premodern economies to modern supply chains.",
        "group": "mechanisms",
        "chapters": [1, 2, 3, 4, 5, 7, 9, 10, 12, 13, 14],
        "pattern": r"\blabor\w*|\blabour\w*|\bworker\w*|\bslave\w*|\benslav\w*|\bwage\w*|\bsharecrop\w*|\btenant\w*|\bdisciplin\w*|\bcoerc\w*",
    },
    {
        "id": "state-power",
        "label": "state-power",
        "description": "How law, coercion, and policy structure cotton frontiers and markets.",
        "definition": "State power tracks how empires, colonial administrations, and nation-states used law, policing, taxation, tariffs, military force, and infrastructure to secure labor, land, and market access in cotton economies.",
        "group": "institutions-actors",
        "chapters": [2, 3, 4, 6, 7, 8, 9, 10, 11, 12],
        "pattern": r"\bstate\w*|\bgovernment\w*|\bcolonial\w*|\blaw\w*|\bact\b|\bempire\w*|\bimperial\w*|\btariff\w*|\bsubsid\w*|\bboard\s+of\s+trade\b",
    },
    {
        "id": "market-infrastructure",
        "label": "market-infrastructure",
        "description": "How exchanges, standards, credit, and logistics coordinate cotton trade.",
        "definition": "Market infrastructure identifies the merchant, exchange, finance, shipping, and information systems that made cotton prices, grades, and contracts comparable across regions and linked growers, mills, and retailers.",
        "group": "mechanisms",
        "chapters": [1, 5, 6, 8, 11, 13, 14],
        "pattern": r"\bmarket\w*|\bexchange\w*|\bmerchant\w*|\bcredit\w*|\bprice\w*|\bfutures\b|\bbroker\w*|\bshipping\b|\bnetwork\w*|\bgrade\w*|\bstandard\w*",
    },
]

CHAPTER_PAGE_RANGES = {
    1: (23, 50),
    2: (51, 81),
    3: (82, 112),
    4: (113, 130),
    5: (131, 174),
    6: (175, 222),
    7: (223, 252),
    8: (253, 303),
    9: (304, 341),
    10: (342, 384),
    11: (385, 419),
    12: (420, 465),
    13: (466, 524),
    14: (524, 544),
}

CHAPTER_PERIODS = {
    1: "5000 BCE-1500s",
    2: "late 1400s-1850s",
    3: "late 1400s-1850s",
    4: "late 1400s-1850s",
    5: "late 1400s-1850s",
    6: "1780s-1860s",
    7: "1780s-1860s",
    8: "1780s-1860s",
    9: "1860s-1910s",
    10: "1860s-1910s",
    11: "1860s-1910s",
    12: "1900s-1930s (into mid-century)",
    13: "1900s-1930s (into mid-century)",
    14: "1950s-2010s",
}

CHAPTER_SETTINGS = {
    1: "premodern household cotton zones across Asia, Africa, and the Americas",
    2: "chartered-company ports in India and Atlantic slave-trade circuits",
    3: "British mill districts and Atlantic input chains",
    4: "Caribbean and South American plantation frontiers",
    5: "the U.S. Deep South cotton frontier",
    6: "new industrial centers across Europe and the Americas",
    7: "factory districts in Britain and continental Europe",
    8: "Liverpool-centered merchant and exchange networks",
    9: "wartime Atlantic and imperial supply rerouting",
    10: "post-emancipation cotton districts in the U.S. South and empire",
    11: "imperial exchanges and colonial market zones",
    12: "colonial cotton projects in Africa, Korea, and Central Asia",
    13: "industrial cotton centers in India, Japan, and China",
    14: "retailer-led global supply chains and subsidized cotton regions",
}

SETTING_PATTERNS = [
    ("Liverpool exchange networks", r"\bliverpool\b"),
    ("Manchester mill districts", r"\bmanchester\b"),
    ("Lancashire factory region", r"\blancashire\b"),
    ("the U.S. South", r"\bdeep\s+south\b|\bamerican\s+south\b|\bthe\s+south\b"),
    ("the United States", r"\bunited\s+states\b"),
    ("India", r"\bindia\b|\bindian\b"),
    ("China", r"\bchina\b|\bchinese\b"),
    ("Brazil", r"\bbrazil\b|\bbrazilian\b"),
    ("West Africa", r"\bwest\s+africa\b"),
    ("Africa", r"\bafrica\b|\bafrican\b"),
    ("Central Asia", r"\bcentral\s+asia\b"),
    ("Egypt", r"\begypt\b|\begyptian\b"),
    ("the Atlantic economy", r"\batlantic\b"),
    ("Europe", r"\beurope\b|\beuropean\b"),
    ("East India Company procurement", r"\beast\s+india\s+company\b"),
    ("cotton exchanges and futures markets", r"\bexchange\w*\b|\bfutures\b"),
    ("merchant credit networks", r"\bmerchant\w*\b|\bcredit\w*\b"),
]

WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'/-]*")
YEAR_RANGE_RE = re.compile(r"\b\d{3,4}\s*[-–]\s*\d{2,4}\b")
YEAR_RE = re.compile(r"\b(1[0-9]{3}|20[0-9]{2}|[5-9][0-9]{2})\b")
DECADE_RE = re.compile(r"\b(1[0-9]{3}s|[12][0-9]{3}s|[0-9]{3}s)\b")
CENTURY_RE = re.compile(
    r"\b(?:fifteenth|sixteenth|seventeenth|eighteenth|nineteenth|twentieth|twenty-first)\s+century\b",
    re.I,
)
BCE_RE = re.compile(r"\b\d+\s*BCE\b", re.I)


@dataclass
class Candidate:
    label: str
    chapters: List[int]
    rationale: str
    group: str


@dataclass
class KeyLineEntry:
    point: str
    evidence: List[str]


def slugify(label: str) -> str:
    token = label.lower().strip()
    token = token.replace("/", "-")
    token = re.sub(r"[^a-z0-9]+", "-", token)
    token = re.sub(r"-{2,}", "-", token).strip("-")
    return token


def normalize_spaces(text: str) -> str:
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def title_case_label(label: str) -> str:
    if label == "labor-regimes":
        return "labor-regimes"
    if label == "state-power":
        return "state-power"
    if label == "market-infrastructure":
        return "market-infrastructure"
    if "/" in label:
        return "/".join(part.title() for part in label.split("/"))
    return label.title()


def parse_keyword_candidates(path: Path) -> List[Candidate]:
    lines = path.read_text().splitlines()
    current_section = None
    parsed: List[Candidate] = []

    row_re = re.compile(r"- `([^`]+)` — chapters: ([0-9, ]+) \(n=(\d+)\) — (.+)")
    for line in lines:
        if line.startswith("## "):
            current_section = line[3:].strip()
            continue
        match = row_re.match(line)
        if not match:
            continue
        if current_section not in SECTION_TO_GROUP:
            raise ValueError(f"Unexpected section for candidate row: {current_section}")
        label = match.group(1).strip()
        chapters = [int(value.strip()) for value in match.group(2).split(",") if value.strip()]
        rationale = match.group(4).strip()
        parsed.append(
            Candidate(
                label=label,
                chapters=chapters,
                rationale=rationale,
                group=SECTION_TO_GROUP[current_section],
            )
        )
    if not parsed:
        raise ValueError("No candidates parsed from keyword_candidates.md")
    return parsed


def compile_pattern_for_label(label: str) -> re.Pattern[str]:
    if label in CANDIDATE_PATTERN_OVERRIDES:
        return re.compile(CANDIDATE_PATTERN_OVERRIDES[label], re.I)

    token = label.lower()
    token = re.sub(r"\([^)]*\)", "", token)
    token = token.replace("/", " ")
    token = re.sub(r"[^a-z0-9 ]+", " ", token)
    token = re.sub(r"\s+", " ", token).strip()
    if not token:
        return re.compile(re.escape(label), re.I)
    if " " in token:
        return re.compile(r"\b" + r"\s+".join(re.escape(word) for word in token.split()) + r"\b", re.I)
    return re.compile(rf"\b{re.escape(token)}\w*\b", re.I)


def parse_chapter_key_lines(path: Path) -> Dict[int, List[KeyLineEntry]]:
    chapter_re = re.compile(r"^## CHAPTER\s+(\d+)\b", re.I)
    point_re = re.compile(r"^- POINT:\s*(.+)$")
    evidence_re = re.compile(r"^\s*EVIDENCE:\s*(.+)$")

    by_chapter: Dict[int, List[KeyLineEntry]] = {}
    chapter = None
    current_point = ""
    current_evidence: List[str] = []

    def flush_point() -> None:
        nonlocal current_point, current_evidence, chapter
        if chapter is None or not current_point:
            return
        by_chapter.setdefault(chapter, []).append(
            KeyLineEntry(point=normalize_spaces(current_point), evidence=[normalize_spaces(item) for item in current_evidence if normalize_spaces(item)])
        )
        current_point = ""
        current_evidence = []

    for line in path.read_text().splitlines():
        chapter_match = chapter_re.match(line)
        if chapter_match:
            flush_point()
            chapter = int(chapter_match.group(1))
            by_chapter.setdefault(chapter, [])
            continue

        point_match = point_re.match(line)
        if point_match:
            flush_point()
            current_point = point_match.group(1).strip()
            current_evidence = []
            continue

        evidence_match = evidence_re.match(line)
        if evidence_match and current_point:
            current_evidence.append(evidence_match.group(1).strip())

    flush_point()
    return by_chapter


def load_chapter_pages(chapter: int, chapter_path: Path) -> Dict[int, str]:
    lines = chapter_path.read_text(errors="ignore").splitlines()
    page = None
    pages: Dict[int, List[str]] = {}
    min_page, max_page = CHAPTER_PAGE_RANGES[chapter]

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if re.fullmatch(r"\d{1,3}", line):
            page = int(line)
            if page < min_page or page > max_page:
                page = None
                continue
            pages.setdefault(page, [])
            continue

        if line.lower().startswith("pages "):
            continue
        if line.lower().startswith("chapter ") and len(line.split()) <= 6:
            continue
        if "illustration credit" in line.lower():
            continue

        if page is None:
            continue

        pages.setdefault(page, []).append(line)

    cleaned: Dict[int, str] = {}
    for key, page_lines in pages.items():
        text = " ".join(page_lines)
        text = re.sub(r"(\w)-\s+(\w)", r"\1\2", text)
        text = normalize_spaces(text)
        cleaned[key] = text

    if not cleaned:
        raise ValueError(f"No page content parsed from {chapter_path}")

    return cleaned


def split_sentences(text: str) -> List[str]:
    text = normalize_spaces(text)
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+", text)
    sentences = [normalize_spaces(part) for part in parts if normalize_spaces(part)]
    if sentences:
        return sentences
    return [text]


def score_sentence(sentence: str) -> int:
    score = 0
    word_count = len(WORD_RE.findall(sentence))
    if 10 <= word_count <= 45:
        score += 2
    if YEAR_RE.search(sentence) or YEAR_RANGE_RE.search(sentence) or CENTURY_RE.search(sentence) or DECADE_RE.search(sentence):
        score += 3
    if re.search(r"\b(?:merchants?|states?|workers?|manufacturers?|planters?|enslaved|slavery|credit|exchange|tariff|subsid)\b", sentence, re.I):
        score += 2
    if re.search(r"\b(?:india|britain|liverpool|manchester|atlantic|africa|china|united\s+states|brazil|egypt|korea|central\s+asia)\b", sentence, re.I):
        score += 2
    if re.search(r"\b\d+(?:\.\d+)?\b", sentence):
        score += 1
    return score


def choose_sentence_for_keyword(chapter_pages: Dict[int, str], pattern: re.Pattern[str]) -> Tuple[int, str, str]:
    best_score = -1
    best_page = None
    best_sentence = None
    best_support = None

    for page in sorted(chapter_pages.keys()):
        page_text = chapter_pages[page]
        if not pattern.search(page_text):
            continue

        sentences = split_sentences(page_text)
        for idx, sentence in enumerate(sentences):
            if not pattern.search(sentence):
                continue
            score = score_sentence(sentence)
            support = sentence
            if idx + 1 < len(sentences):
                next_sentence = sentences[idx + 1]
                if score_sentence(next_sentence) >= 3:
                    support = f"{sentence} {next_sentence}"
                    score += 1
            if score > best_score:
                best_score = score
                best_page = page
                best_sentence = sentence
                best_support = support

    if best_page is not None and best_sentence is not None and best_support is not None:
        return best_page, best_sentence, best_support

    # Fallback: choose strongest sentence from the chapter even without a direct pattern hit.
    fallback_candidates: List[Tuple[int, int, str]] = []
    for page in sorted(chapter_pages.keys()):
        for sentence in split_sentences(chapter_pages[page]):
            fallback_candidates.append((score_sentence(sentence), page, sentence))

    if not fallback_candidates:
        return 0, "", ""

    fallback_candidates.sort(key=lambda item: (-item[0], item[1]))
    _, page, sentence = fallback_candidates[0]
    return page, sentence, sentence


def score_key_line_entry(entry: KeyLineEntry) -> int:
    text = f"{entry.point} {' '.join(entry.evidence)}"
    return score_sentence(text)


def choose_key_line_entry(entries: Sequence[KeyLineEntry], pattern: re.Pattern[str]) -> KeyLineEntry | None:
    if not entries:
        return None

    matches: List[Tuple[int, KeyLineEntry]] = []
    for entry in entries:
        entry_text = f"{entry.point} {' '.join(entry.evidence)}"
        if pattern.search(entry_text):
            matches.append((score_key_line_entry(entry), entry))

    if matches:
        matches.sort(key=lambda item: -item[0])
        return matches[0][1]

    ranked = sorted(entries, key=score_key_line_entry, reverse=True)
    return ranked[0] if ranked else None


def extract_page_from_text(text: str) -> int | None:
    match = re.search(r"\(p\.\s*(\d+)", text)
    if match:
        return int(match.group(1))
    return None


def choose_entry_evidence(entry: KeyLineEntry, pattern: re.Pattern[str], chapter: int) -> str:
    if not entry.evidence:
        return ""
    min_page, max_page = CHAPTER_PAGE_RANGES[chapter]
    valid_evidence: List[str] = []
    for evidence in entry.evidence:
        page = extract_page_from_text(evidence)
        if page is None or (min_page <= page <= max_page):
            valid_evidence.append(evidence)

    pool = valid_evidence if valid_evidence else entry.evidence
    for evidence in pool:
        if pattern.search(evidence):
            return evidence
    return pool[0]


def lower_first(text: str) -> str:
    if not text:
        return text
    return text[0].lower() + text[1:]


def trim_words(text: str, limit: int) -> str:
    words = WORD_RE.findall(text)
    if not words:
        return ""
    trimmed = words[:limit]
    out = " ".join(trimmed)
    return out


def infer_setting(theme_label: str, group: str, sentence: str, chapter: int) -> str:
    if group == "places-regions":
        return title_case_label(theme_label)

    for setting, pattern in SETTING_PATTERNS:
        if re.search(pattern, sentence, re.I):
            return setting

    return CHAPTER_SETTINGS[chapter]


def infer_time(sentence: str, chapter: int) -> str:
    for regex in (YEAR_RANGE_RE, BCE_RE, CENTURY_RE, DECADE_RE, YEAR_RE):
        match = regex.search(sentence)
        if match:
            return normalize_spaces(match.group(0))
    return CHAPTER_PERIODS[chapter]


def build_point(label: str, setting: str, time: str, sentence: str) -> str:
    phrase = trim_words(sentence, 24)
    phrase = re.sub(r"\s+", " ", phrase).strip()
    if not phrase:
        phrase = "cotton production and trade were reorganized through this mechanism"
    phrase = lower_first(phrase)
    return f"In {setting}, {label} is visible as {phrase} ({time})."


def build_evidence(support: str, page: int, preferred: str = "") -> List[str]:
    if preferred and re.search(r"\(p\.\s*\d+", preferred):
        return [normalize_spaces(preferred)]

    clause = trim_words(support, 36)
    clause = clause.strip()
    clause = lower_first(clause)
    if not clause:
        clause = "the chapter ties this keyword to concrete shifts in labor, trade, and institutions"
    return [f"The chapter records that {clause}. (p. {page})"]


def scope_from_hits(chapters: Sequence[int]) -> str:
    ordered = sorted(chapters)
    start = CHAPTER_PERIODS.get(ordered[0], "early modern era")
    end = CHAPTER_PERIODS.get(ordered[-1], "modern era")
    if ordered[0] == ordered[-1]:
        return f"chapter {ordered[0]} ({start})"
    return f"chapters {ordered[0]}-{ordered[-1]} ({start} to {end})"


def build_definition(label: str, group: str, rationale: str, chapters: Sequence[int]) -> str:
    scope = scope_from_hits(chapters)

    if group == "mechanisms":
        return (
            f"As used in this book, {label} refers to {rationale}. "
            f"It operates through merchants, manufacturers, growers, workers, and states across {scope}."
        )

    if group == "institutions-actors":
        return (
            f"As used in this book, {label} identifies {rationale}. "
            f"These actors and institutions organize labor, land access, pricing, and governance across {scope}."
        )

    return (
        f"As used in this book, {label} marks {rationale}. "
        f"In this regional node, states, merchants, and workers reshape cotton production and exchange across {scope}."
    )


def build_description(rationale: str) -> str:
    text = rationale[0].upper() + rationale[1:] if rationale else ""
    text = normalize_spaces(text)
    if len(text) <= 96:
        return text
    return text[:93].rstrip() + "..."


def merge_candidates(candidates: Sequence[Candidate]) -> Tuple[List[Dict], Dict[str, List[str]]]:
    by_label: Dict[str, Dict] = {}
    aliases_by_label: Dict[str, List[str]] = {}

    for candidate in candidates:
        canonical_label = CANONICAL_LABEL.get(candidate.label, candidate.label)
        target = by_label.get(canonical_label)

        if target is None:
            target = {
                "label": canonical_label,
                "group": candidate.group,
                "rationale": candidate.rationale,
                "chapters": sorted(set(candidate.chapters)),
            }
            by_label[canonical_label] = target
            aliases_by_label[canonical_label] = []
        else:
            target["chapters"] = sorted(set(target["chapters"]).union(candidate.chapters))
            if target["group"] != candidate.group:
                raise ValueError(
                    f"Conflicting groups for canonical label '{canonical_label}': "
                    f"{target['group']} vs {candidate.group}"
                )

        if candidate.label != canonical_label:
            aliases_by_label[canonical_label].append(candidate.label)

    rows = list(by_label.values())
    rows.sort(key=lambda item: (GROUP_ORDER.index(item["group"]), item["label"]))
    return rows, aliases_by_label


def build_theme_entry(
    theme_id: str,
    label: str,
    description: str,
    definition: str,
    group: str,
    aliases: Sequence[str],
    chapters: Sequence[int],
    pattern: re.Pattern[str],
    chapter_pages: Dict[int, Dict[int, str]],
    chapter_key_lines: Dict[int, List[KeyLineEntry]],
) -> Dict:
    applications = []

    for chapter in sorted(chapters):
        page, sentence, support = choose_sentence_for_keyword(chapter_pages[chapter], pattern)

        entry = choose_key_line_entry(chapter_key_lines.get(chapter, []), pattern)
        if entry:
            evidence_text = choose_entry_evidence(entry, pattern, chapter)
            entry_page = extract_page_from_text(evidence_text)
            min_page, max_page = CHAPTER_PAGE_RANGES[chapter]
            preferred_evidence = ""
            if entry_page is not None and min_page <= entry_page <= max_page:
                page = entry_page
                preferred_evidence = evidence_text

            source_text = f"{entry.point} {evidence_text}".strip()
            setting = infer_setting(label, group, source_text, chapter)
            time = infer_time(source_text, chapter)
            point = build_point(label, setting, time, entry.point)
            evidence = build_evidence(support, page, preferred=preferred_evidence)
        else:
            setting = infer_setting(label, group, sentence, chapter)
            time = infer_time(sentence, chapter)
            point = build_point(label, setting, time, sentence)
            evidence = build_evidence(support, page)

        applications.append(
            {
                "chapter": chapter,
                "setting": setting,
                "time": time,
                "point": point,
                "evidence": evidence,
            }
        )

    return {
        "id": theme_id,
        "label": label,
        "description": description,
        "definition": definition,
        "group": group,
        "aliases": list(aliases),
        "applications": applications,
    }


def build_themes(keyword_candidates_path: Path, chapters_dir: Path, chapter_key_lines_path: Path) -> List[Dict]:
    candidates = parse_keyword_candidates(keyword_candidates_path)
    merged_candidates, aliases_by_label = merge_candidates(candidates)

    chapter_pages: Dict[int, Dict[int, str]] = {}
    for chapter in range(1, 15):
        chapter_path = chapters_dir / f"chap{chapter:02d}.txt"
        if not chapter_path.exists():
            raise FileNotFoundError(f"Missing chapter text: {chapter_path}")
        chapter_pages[chapter] = load_chapter_pages(chapter, chapter_path)

    chapter_key_lines = parse_chapter_key_lines(chapter_key_lines_path)

    themes: List[Dict] = []

    for core in CORE_THEMES:
        entry = build_theme_entry(
            theme_id=core["id"],
            label=core["label"],
            description=core["description"],
            definition=core["definition"],
            group=core["group"],
            aliases=[],
            chapters=core["chapters"],
            pattern=re.compile(core["pattern"], re.I),
            chapter_pages=chapter_pages,
            chapter_key_lines=chapter_key_lines,
        )
        themes.append(entry)

    for candidate in merged_candidates:
        label = candidate["label"]
        group = candidate["group"]
        chapters = candidate["chapters"]
        rationale = candidate["rationale"]
        aliases = aliases_by_label.get(label, [])

        entry = build_theme_entry(
            theme_id=slugify(label),
            label=label,
            description=build_description(rationale),
            definition=build_definition(label, group, rationale, chapters),
            group=group,
            aliases=aliases,
            chapters=chapters,
            pattern=compile_pattern_for_label(label),
            chapter_pages=chapter_pages,
            chapter_key_lines=chapter_key_lines,
        )
        themes.append(entry)

    core_ids = {core["id"] for core in CORE_THEMES}
    themes.sort(
        key=lambda item: (
            GROUP_ORDER.index(item["group"]),
            0 if item["id"] in core_ids else 1,
            item["label"],
        )
    )

    return themes


def patch_book_data(book_data_path: Path, themes: Sequence[Dict]) -> None:
    book_data = book_data_path.read_text()
    themes_json = json.dumps(themes, ensure_ascii=False, indent=4)

    replacement = f"themes: {themes_json},\n  flow:"
    updated, count = re.subn(
        r"themes:\s*\[.*?\],\n\s*flow:",
        replacement,
        book_data,
        flags=re.S,
    )
    if count != 1:
        raise ValueError("Could not uniquely locate themes block in book-data.js")

    book_data_path.write_text(updated)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build keyword cards and patch book-data.js")
    parser.add_argument(
        "--keyword-candidates",
        default="keyword_candidates.md",
        help="Path to keyword_candidates.md",
    )
    parser.add_argument(
        "--chapters-dir",
        default="tmp/chapters",
        help="Directory containing chap01.txt ... chap14.txt",
    )
    parser.add_argument(
        "--book-data",
        default="book-data.js",
        help="Path to book-data.js",
    )
    parser.add_argument(
        "--chapter-key-lines",
        default="tmp/chapter_key_lines.txt",
        help="Path to chapter_key_lines.txt",
    )
    parser.add_argument(
        "--out-json",
        default="",
        help="Optional path to write generated themes JSON",
    )
    parser.add_argument(
        "--no-patch",
        action="store_true",
        help="Do not patch book-data.js; only print/write JSON output",
    )

    args = parser.parse_args()

    themes = build_themes(
        keyword_candidates_path=Path(args.keyword_candidates),
        chapters_dir=Path(args.chapters_dir),
        chapter_key_lines_path=Path(args.chapter_key_lines),
    )

    if args.out_json:
        Path(args.out_json).write_text(json.dumps(themes, ensure_ascii=False, indent=2))

    if not args.no_patch:
        patch_book_data(Path(args.book_data), themes)

    print(f"Generated {len(themes)} themes")


if __name__ == "__main__":
    main()

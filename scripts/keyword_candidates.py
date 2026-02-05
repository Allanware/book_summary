#!/usr/bin/env python3
import argparse
import glob
import re
from pathlib import Path
from typing import Dict, List, Tuple

CHAPTER_NAME_LINES = {
    "chapter one",
    "chapter two",
    "chapter three",
    "chapter four",
    "chapter five",
    "chapter six",
    "chapter seven",
    "chapter eight",
    "chapter nine",
    "chapter ten",
    "chapter eleven",
    "chapter twelve",
    "chapter thirteen",
    "chapter fourteen",
}


def load_chapters(tmp_dir: str) -> Dict[int, str]:
    chapter_files = sorted(glob.glob(str(Path(tmp_dir) / "chap[0-9][0-9].txt")))
    chapters: Dict[int, str] = {}
    header_re = re.compile(r"^\s*chapter\s+\w+", re.I)
    page_re = re.compile(r"^\s*\d+\s*$")

    for f in chapter_files:
        chap_num = int(re.search(r"chap(\d+)", f).group(1))
        lines = Path(f).read_text(errors="ignore").splitlines()
        cleaned_lines: List[str] = []
        for line in lines:
            if page_re.match(line):
                continue
            if header_re.match(line):
                continue
            if line.strip().lower() in CHAPTER_NAME_LINES:
                continue
            cleaned_lines.append(line)

        text = "\n".join(cleaned_lines)
        # de-hyphenate line breaks
        text = re.sub(r"-\n", "", text)
        text = text.replace("\n", " ")
        text = re.sub(r"\s+", " ", text)
        chapters[chap_num] = text.lower()

    if not chapters:
        raise SystemExit("No chapter files found in tmp/chapters. Expected chap01.txt..chap14.txt")

    return chapters


def chapter_hits(chapters: Dict[int, str], pattern: str) -> List[int]:
    regex = re.compile(pattern)
    hits = [chap for chap, text in chapters.items() if regex.search(text)]
    return sorted(hits)


def format_list(label: str, hits: List[int], rationale: str) -> str:
    return f"- `{label}` — chapters: {', '.join(map(str, hits))} (n={len(hits)}) — {rationale}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate keyword candidate list from original chapter text.")
    parser.add_argument("--tmp-dir", default="tmp/chapters", help="Directory containing chap01.txt..chap14.txt")
    parser.add_argument("--min-chapters", type=int, default=3, help="Minimum chapter count to include")
    parser.add_argument("--out", default="keyword_candidates.md", help="Output markdown file")
    args = parser.parse_args()

    chapters = load_chapters(args.tmp_dir)

    mechanisms: Dict[str, Tuple[str, str]] = {
        "credit": (r"\bcredit\b", "financing/advance systems organizing production and trade"),
        "industrial capitalism": (r"\bindustrial\s+capitalism\b", "factory-centered capitalism scaling output via wage labor and machinery"),
        "mechanization": (r"\bmechaniz\w*|\bmachinery\b|\bmachine\w*", "machines raising output and centralizing production"),
        "war capitalism": (r"\bwar\s+capitalism\b", "state‑backed violence and conquest to secure cotton and labor"),
        "mobilization": (r"\bmobiliz\w*", "organized movement of labor, capital, and resources"),
        "price signals": (r"\bprice\w*", "prices coordinating supply across distances"),
        "slavery": (r"\bslaver\w*", "coerced labor regime central to expansion"),
        "capital accumulation": (r"\baccumul\w*", "reinvestment driving scale and infrastructure"),
        "colonial rule": (r"\bcolonial\w*", "imperial governance reshaping land and labor"),
        "market integration": (r"\bintegrat\w*", "linking regions into a single market"),
        "productivity": (r"\bproductiv\w*", "output gains per labor/time shifting production locations"),
        "coercion": (r"\bcoerc\w*", "compulsion securing labor or land"),
        "commodification": (r"\bcommodif\w*|\bcommodity\b", "turning cotton/land/labor into tradable commodities"),
        "expropriation": (r"\bexpropriat\w*|\bdispossess\w*|\bseiz\w+\b", "land seizure to open frontiers"),
        "imperialism": (r"\bimperial\w*", "territorial expansion to secure resources and markets"),
        "industrialization": (r"\bindustrializ\w*", "diffusion of factory production centers"),
        "protectionism (tariff policy)": (r"\bprotect\w*", "state protection shaping industrial geography"),
        "global capitalism": (r"\bglobal\s+capitalism\b", "late‑stage global coordination of production and retail"),
        "political economy": (r"\bpolitical\s+economy\b", "state policy and market outcomes entwined"),
        "slave labor": (r"\bslave\s+labor\b|\bslave\s+labour\b", "explicit forced labor regime"),
        "wage labor": (r"\bwage\s+labor\b|\bwage\s+labour\b", "factory wage regimes replacing household/forced labor"),
        "discipline": (r"\bdisciplin\w*", "factory discipline as labor control"),
    }

    institutions_actors: Dict[str, Tuple[str, str]] = {
        "merchants": (r"\bmerchants?\b", "trade coordinators and credit brokers"),
        "state": (r"\bstate\b|\bstates\b", "policy and coercive authority shaping cotton systems"),
        "empire": (r"\bempire\b|\bempires\b", "imperial structures binding production and markets"),
        "manufacturers": (r"\bmanufacturers?\b", "industrial producers driving demand"),
        "workers": (r"\bworkers?\b|\blaborers?\b", "labor force in mills and fields"),
        "slaves/enslaved": (r"\bslaves?\b|\benslaved\b", "coerced labor base of expansion"),
        "capitalists": (r"\bcapitalists?\b", "owners/investors directing accumulation"),
        "planters": (r"\bplanters?\b", "plantation owners organizing production"),
        "growers/cultivators": (r"\bgrowers?\b|\bcultivators?\b", "agricultural producers across empires"),
        "spinners": (r"\bspinners?\b", "textile labor group in yarn production"),
        "weavers": (r"\bweavers?\b", "textile labor group in cloth production"),
        "peasants": (r"\bpeasants?\b", "rural producers under coercive systems"),
        "exchange": (r"\bexchange\b|\bexchanges\b", "institutional market nodes coordinating prices"),
        "bank": (r"\bbank\b|\bbanks\b|\bbanking\b", "finance institutions enabling credit flows"),
        "chamber of commerce": (r"\bchamber\s+of\s+commerce\b|\bchamber\s+commerce\b", "formal trade governance bodies"),
    }

    places_regions: Dict[str, Tuple[str, str]] = {
        "britain/england": (r"\bbritain\b|\bbritish\b|\bengland\b|\bgreat\s+britain\b", "core industrial and imperial node"),
        "europe": (r"\beurope\b|\beuropean\b", "manufacturing and market region across eras"),
        "india": (r"\bindia\b|\bindian\b", "early textile center and colonial supply zone"),
        "americas": (r"\bamerica\b|\bamerican\b|\bamericas\b", "major cotton frontier and consumer region"),
        "united states": (r"\bunited\s+states\b", "dominant producer/industrial/retail power"),
        "american south": (r"\bamerican\s+south\b|\bthe\s+south\b", "plantation core and later agricultural region"),
        "china": (r"\bchina\b|\bchinese\b", "major production/manufacturing region"),
        "brazil": (r"\bbrazil\b|\bbrazilian\b", "recurring cotton region in the Americas"),
        "africa": (r"\bafrica\b|\bafrican\b", "source region in trade and colonial programs"),
        "atlantic": (r"\batlantic\b", "trade and labor circuits tying continents"),
        "north america": (r"\bnorth\s+america\b", "regional production/industry zone"),
        "liverpool": (r"\bliverpool\b", "major exchange and merchant hub"),
        "manchester": (r"\bmanchester\b", "industrial manufacturing center"),
        "lancashire": (r"\blancashire\b", "core British textile district"),
        "egypt": (r"\begypt\b|\begyptian\b", "key cotton production region"),
        "new york": (r"\bnew\s+york\b", "finance and market node"),
        "west africa": (r"\bwest\s+africa\b", "trade and production region"),
        "central asia": (r"\bcentral\s+asia\b", "imperial cotton development region"),
    }

    sections = [
        ("Mechanisms", mechanisms),
        ("Institutions & Actors", institutions_actors),
        ("Places & Regions", places_regions),
    ]

    lines: List[str] = []
    lines.append("# Keyword Candidates")
    lines.append("")
    lines.append("Source: `tmp/chapters/chap01.txt` … `chap14.txt`")
    lines.append(f"Minimum chapters: {args.min_chapters}")
    lines.append("")

    for title, mapping in sections:
        lines.append(f"## {title}")
        items: List[Tuple[str, List[int], str]] = []
        for label, (pattern, rationale) in mapping.items():
            hits = chapter_hits(chapters, pattern)
            if len(hits) >= args.min_chapters:
                items.append((label, hits, rationale))
        items.sort(key=lambda x: (-len(x[1]), x[0]))
        if not items:
            lines.append("- (no items meet threshold)")
            lines.append("")
            continue
        for label, hits, rationale in items:
            lines.append(format_list(label, hits, rationale))
        lines.append("")

    out_path = Path(args.out)
    out_path.write_text("\n".join(lines))
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()

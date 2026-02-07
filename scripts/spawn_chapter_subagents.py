#!/usr/bin/env python3
"""Spawn parallel Codex subagents to rewrite chapter summaries."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import textwrap
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import pdfplumber

ROOT = Path(__file__).resolve().parent.parent
PDF_PATH = ROOT / "Empire of Cotton.pdf"


def load_chapter_page_ranges() -> List[Tuple[int, str]]:
    script = (
        "const {chapters}=await import('./chapters/index.js');"
        "process.stdout.write(JSON.stringify(chapters.map(c=>({id:c.id,pages:c.pages}))));"
    )
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    out: List[Tuple[int, str]] = []
    for item in payload:
        chapter_id = int(item["id"])
        pages = str(item["pages"]).strip()
        if not re.fullmatch(r"\d+-\d+", pages):
            raise ValueError(f"Unsupported pages format for chapter {chapter_id}: {pages}")
        out.append((chapter_id, pages))
    return sorted(out, key=lambda pair: pair[0])


def extract_full_chapter_text(chapter_id: int, pages: str, out_dir: Path) -> Path:
    start_s, end_s = pages.split("-", 1)
    start = int(start_s)
    end = int(end_s)

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"chapter-{chapter_id:02d}_{pages}.full.txt"

    parts: List[str] = []
    with pdfplumber.open(str(PDF_PATH)) as pdf:
        for pno in range(start, end + 1):
            text = (pdf.pages[pno - 1].extract_text() or "").strip()
            parts.append(f"\n\n===== PDF_PAGE_{pno} =====\n")
            parts.append(text)

    out_path.write_text("".join(parts))
    return out_path


def build_prompt(chapter_id: int, pages: str, source_path: Path) -> str:
    chapter_file = f"chapters/chapter-{chapter_id:02d}.js"
    chapter_num = chapter_id
    return textwrap.dedent(
        f"""
        You are a focused subagent for one chapter rewrite in /Users/allan/Downloads/Empire_of_Cotton.

        Task:
        Rewrite only `{chapter_file}` using AGENTS.md Stage B requirements.

        Required inputs:
        - Read `AGENTS.md`.
        - Read full chapter source text from `{source_path}` (PDF pages {pages}).
        - Read existing `{chapter_file}`.

        Hard requirements:
        - Keep module shape: `export default {{ ... }}` with `id`, `title`, `pages`, `thesis`, `flowSections`, `themes`.
        - Keep `themes` unchanged from the existing file.
        - Use `thesis` + `flowSections` only (no legacy fallback fields).
        - Thesis must include superscript links to section anchors:
          `<sup><a href="#chapter-{chapter_num}-section-1">1</a></sup>` etc.
        - Subarguments must be semantically grouped by mechanism/actors/processes, not page adjacency.
        - Evidence in each section can and should cite non-contiguous pages where relevant.
        - Cover the full chapter range, including early/middle/late pages.
        - Keep points concrete and evidence-led with page citations like `(p. X)`.
        - Avoid generic filler language.
        - Use 4-7 flowSections unless the chapter forces a different count.

        Constraints:
        - Edit only `{chapter_file}`.
        - Do not edit any other files.

        Validation before finishing:
        - Run: `node --input-type=module -e "import('./{chapter_file}').then(m=>console.log(m.default.id,m.default.flowSections.length))"`
        - Ensure the command succeeds.

        Return a brief summary of what you changed.
        """
    ).strip() + "\n"


def run_subagent(
    chapter_id: int,
    pages: str,
    source_path: Path,
    log_dir: Path,
    model: str,
    reasoning_effort: str,
) -> Dict[str, str]:
    prompt = build_prompt(chapter_id, pages, source_path)
    log_path = log_dir / f"chapter-{chapter_id:02d}.log"

    cmd = [
        "codex",
        "exec",
        "-m",
        model,
        "-c",
        f'model_reasoning_effort="{reasoning_effort}"',
        "--dangerously-bypass-approvals-and-sandbox",
        "-C",
        str(ROOT),
        "--ephemeral",
        "-",
    ]

    with log_path.open("w", encoding="utf-8") as log_file:
        log_file.write(f"# chapter {chapter_id:02d} pages {pages}\n")
        log_file.write(f"# source {source_path}\n\n")
        proc = subprocess.run(
            cmd,
            input=prompt,
            text=True,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            cwd=ROOT,
        )

    return {
        "chapter": f"{chapter_id:02d}",
        "pages": pages,
        "source": str(source_path),
        "log": str(log_path),
        "status": "ok" if proc.returncode == 0 else "failed",
        "code": str(proc.returncode),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Spawn Codex subagents for chapter rewrites")
    parser.add_argument(
        "--chapters",
        default="2-14",
        help="Chapter range/list, e.g. 2-14 or 2,3,4,8",
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=4,
        help="Max concurrent subagents",
    )
    parser.add_argument(
        "--model",
        default="gpt-5.2",
        help="Model to use for subagents",
    )
    parser.add_argument(
        "--reasoning-effort",
        default="high",
        choices=["low", "medium", "high"],
        help="Reasoning effort for each subagent",
    )
    return parser.parse_args()


def parse_chapter_selector(selector: str) -> List[int]:
    selector = selector.strip()
    out: List[int] = []
    for part in selector.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a_s, b_s = part.split("-", 1)
            a, b = int(a_s), int(b_s)
            lo, hi = sorted((a, b))
            out.extend(range(lo, hi + 1))
        else:
            out.append(int(part))
    return sorted(set(out))


def main() -> None:
    args = parse_args()
    selected = set(parse_chapter_selector(args.chapters))

    all_ranges = load_chapter_page_ranges()
    targets = [(cid, pages) for cid, pages in all_ranges if cid in selected and cid != 1]
    if not targets:
        raise SystemExit("No target chapters selected (excluding chapter 1).")

    if not PDF_PATH.exists():
        raise SystemExit(f"Missing PDF: {PDF_PATH}")

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = ROOT / "tmp" / "subagents" / f"chapter-rewrite-{stamp}"
    src_dir = run_dir / "sources"
    log_dir = run_dir / "logs"
    run_dir.mkdir(parents=True, exist_ok=True)
    src_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    source_map: Dict[int, Path] = {}
    for cid, pages in targets:
        source_map[cid] = extract_full_chapter_text(cid, pages, src_dir)

    print(f"Run directory: {run_dir}")
    print(
        f"Spawning {len(targets)} chapter subagents with parallel={args.parallel} "
        f"model={args.model} reasoning={args.reasoning_effort}"
    )

    results: List[Dict[str, str]] = []
    with ThreadPoolExecutor(max_workers=max(1, args.parallel)) as pool:
        future_map = {
            pool.submit(
                run_subagent,
                cid,
                pages,
                source_map[cid],
                log_dir,
                args.model,
                args.reasoning_effort,
            ): (cid, pages)
            for cid, pages in targets
        }
        for future in as_completed(future_map):
            cid, pages = future_map[future]
            try:
                result = future.result()
            except Exception as exc:  # noqa: BLE001
                result = {
                    "chapter": f"{cid:02d}",
                    "pages": pages,
                    "source": str(source_map[cid]),
                    "log": str(log_dir / f"chapter-{cid:02d}.log"),
                    "status": "failed",
                    "code": "exception",
                    "error": str(exc),
                }
            results.append(result)
            print(f"chapter {result['chapter']}: {result['status']} (log: {result['log']})")

    results = sorted(results, key=lambda row: int(row["chapter"]))
    summary_path = run_dir / "summary.json"
    summary_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    ok = sum(1 for row in results if row["status"] == "ok")
    failed = len(results) - ok
    print(f"Completed. ok={ok} failed={failed}")
    print(f"Summary: {summary_path}")


if __name__ == "__main__":
    main()

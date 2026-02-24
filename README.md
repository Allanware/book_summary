# Book Summary — Argument Atlas

A collection-based website for interactive book argument maps, keyword cards, and synthesis flows.

`AGENTS.md` is the canonical spec for data schema and renderer compatibility.

## Directory structure

```
book_summary/
├── input/{collection}/{book}/       ← raw source files (PDF/EPUB); gitignored
├── extracted/{collection}/{book}/   ← per-chapter markdown; gitignored
├── site/                            ← output website
│   ├── index.html                   ← landing page (lists collections)
│   ├── renderer.js                  ← shared rendering module
│   ├── styles.css                   ← shared styles
│   └── {collection}/{book}/         ← one book site
│       ├── index.html
│       ├── book-data.js / .zh.js
│       └── chapters/
├── scripts/                         ← helper scripts
├── tmp/                             ← throwaway extraction artifacts
└── AGENTS.md
```

## 1) What is versioned vs generated

Versioned source of truth:
- `site/{collection}/{book}/book-data.js`
- `site/{collection}/{book}/book-data.zh.js` (or your selected L2 equivalent file)
- `site/{collection}/{book}/chapters/chapter-XX.js`
- `site/{collection}/{book}/chapters/chapter-XX.zh.js` (or your selected L2 equivalent files)
- `site/{collection}/{book}/chapters/index.js`
- `site/{collection}/{book}/chapters/index.zh.js` (or your selected L2 equivalent index)
- `site/{collection}/{book}/index.html`
- `site/renderer.js`, `site/styles.css`, `site/index.html`
- `AGENTS.md`

Generated/intermediate artifacts (do not track):
- `input/**`
- `extracted/**`
- `tmp/**`
- `keyword_candidates.md`

## 2) Reproducing

Run LLM agents with the specifications in `AGENTS.md`.

## 3) Serving locally

```bash
python3 -m http.server -d site
# Open http://localhost:8000/
```

## 4) Notes for adapting to another book

- Create a new `input/{collection}/{book}/` directory with the source PDF/EPUB.
- Run the pipeline (see `AGENTS.md`) to populate `extracted/` and `site/`.
- Keep pipeline logic corpus-driven; do not hardcode book-specific theme/actor/place lists in scripts.
- Keep chapter file naming stable (`chapNN.txt`) so scripts rerun without reconfiguration.
- Keep IDs and ordering aligned across languages when bilingual mode is enabled.
- If helper-script output conflicts with chapter evidence, chapter evidence wins.

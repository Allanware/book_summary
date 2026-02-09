# Empire of Cotton Website Data Pipeline

This repository contains a reusable pipeline for building chapter summaries, keyword cards, and synthesis flow for a book website.

`AGENTS.md` is the canonical spec for data schema and renderer compatibility.

## 1) What is versioned vs generated

Versioned source of truth:
- `book-data.js`
- `book-data.zh.js` (or your selected L2 equivalent file)
- `chapters/chapter-XX.js`
- `chapters/chapter-XX.zh.js` (or your selected L2 equivalent files)
- `chapters/index.js`
- `chapters/index.zh.js` (or your selected L2 equivalent index)
- `index.html`, `script.js`, `styles.css`
- `AGENTS.md`

Generated/intermediate artifacts (do not track):
- `tmp/**`
- `keyword_candidates.md`

## 2) Reproducing

Run LLM agents with the specifications in `AGENTS.md`.

## 3) Notes for adapting to another book

- Keep pipeline logic corpus-driven; do not hardcode book-specific theme/actor/place lists in scripts.
- Keep chapter file naming stable (`chapNN.txt`) so scripts rerun without reconfiguration.
- Keep IDs and ordering aligned across languages when bilingual mode is enabled.
- If helper-script output conflicts with chapter evidence, chapter evidence wins.

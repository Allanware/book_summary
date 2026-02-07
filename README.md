# Empire of Cotton Website Data Pipeline

This repository contains a reusable pipeline for building chapter summaries, keyword cards, and synthesis flow for a book website.

`AGENTS.md` is the canonical spec for data schema and renderer compatibility. Use this README as the execution guide.

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

## 2) Prerequisites

- Python 3.9+
- Node.js 18+

Optional (for bilingual generation):
- `codex` CLI (for `scripts/generate_zh_data_codex.py`)

## 3) Repeatable workflow for any book

1. Choose language mode first:
- `English only`
- `English + L2` (user-selected second language)

2. Run one-time chapter extraction from the source PDF into:
- `tmp/chapters/chap01.txt ... tmp/chapters/chapNN.txt`

3. Normalize extracted chapter text while preserving page references.

4. Build chapter argument mindmaps (`chapters/chapter-XX.js`, plus L2 files if enabled) using:
- `thesis`
- `flowSections[]`

5. Run keyword candidate discovery from the normalized corpus:
```bash
python3 scripts/keyword_candidates.py --tmp-dir tmp/chapters --min-chapters 3 --out keyword_candidates.md
```

6. Build keyword cards into book data:
```bash
python3 scripts/build_keyword_cards.py --keyword-candidates keyword_candidates.md --chapters-dir tmp/chapters --chapter-key-lines tmp/chapter_key_lines.txt --book-data book-data.js
```

7. Validate keyword cards:
```bash
python3 scripts/validate_keyword_cards.py --book-data book-data.js --keyword-candidates keyword_candidates.md
```

8. Validate AGENTS spec stays in sync with UI/runtime files:
```bash
python3 scripts/check_agents_sync.py --agents AGENTS.md --index index.html --script script.js --styles styles.css
```

9. If bilingual mode is enabled, run module parse checks and quote-escape repair for JS files:
```bash
node --input-type=module -e "await import('./chapters/index.zh.js'); await import('./book-data.zh.js'); console.log('ok')"
for f in chapters/chapter-*.zh.js book-data.zh.js; do python3 scripts/fix_zh_quotes.py "$f"; done
node --input-type=module -e "await import('./chapters/index.zh.js'); await import('./book-data.zh.js'); console.log('ok')"
```

## 4) Script sanity checks

```bash
python3 -m py_compile scripts/keyword_candidates.py scripts/build_keyword_cards.py scripts/validate_keyword_cards.py scripts/check_agents_sync.py scripts/fix_zh_quotes.py
```

## 5) Notes for adapting to another book

- Keep pipeline logic corpus-driven; do not hardcode book-specific theme/actor/place lists in scripts.
- Keep chapter file naming stable (`chapNN.txt`) so scripts rerun without reconfiguration.
- Keep IDs and ordering aligned across languages when bilingual mode is enabled.
- If helper-script output conflicts with chapter evidence, chapter evidence wins.

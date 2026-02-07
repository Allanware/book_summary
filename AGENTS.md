# Book Website Spec (Current Structure + Reusable Pipeline)

Use this file when updating chapter content, keyword data, or synthesis flow for this site.
This spec is synced to the current implementation in `index.html`, `script.js`, `styles.css`, chapter modules, and book data modules.

## 1 Source of truth

### 1.1 UI and rendering files
- `index.html`: page structure and language switch controls.
- `script.js`: all runtime rendering, interactions, filtering, and language switching.
- `styles.css`: layout and interaction styling (including keyword group collapse behavior and section toggles).

### 1.2 Data files
- English book data: `book-data.js`
- Current second-language book data (Chinese in this repo): `book-data.zh.js`
- English chapter modules: `chapters/chapter-XX.js`
- Current second-language chapter modules (Chinese in this repo): `chapters/chapter-XX.zh.js`
- English chapter index: `chapters/index.js`
- Current second-language chapter index (Chinese in this repo): `chapters/index.zh.js`

## 2 Operating principles

### 2.1 Priority order
1. Evidence fidelity to source pages.
2. Full chapter-range coverage.
3. Schema/UI compatibility with current renderer.
4. Concise, concrete argument writing.

### 2.2 Cross-book portability rule (hard requirement)
- Do not hardcode book-specific theme lists, actor lists, place lists, or chapter-name lists in workflow logic.
- Use corpus-derived discovery first (frequency, spread across chapters, context diversity), then human review/merge.
- If any script contains lexical heuristics, keep them language-level and generic (for example, tokenization, stopwords, suffix patterns), not title/book dependent.
- Manual reviewer decisions must be captured in data outputs (`book-data*.js`), not buried as hidden constants in scripts.

### 2.3 Script role
- Scripts are helpers, not the source of truth.
- Final source of truth is the data modules consumed by `script.js`.
- If helper-script output conflicts with chapter evidence, chapter evidence wins.

### 2.4 Language-scope decision (required)
- Before running the pipeline, explicitly ask the user which language mode they want:
  - `English only`
  - `English + one second language` (user-selected; not required to be Chinese)
- Do not assume bilingual output by default for a new book.
- For this current repo, the implemented second language is Chinese (`*.zh.*` files); for a different second language in a new project, use the same schema/parity rules with that language's file set.

### 2.5 Parallel multi-agent execution rule (required)
- After Stage A, run chapter summary extraction (Stage B) and keyword candidate discovery (Stage C) in parallel.
- For chapter summaries, split work across multiple agents by chapter or chapter ranges, then merge through one coordinator pass for schema consistency.
- For keyword extraction, allow separate agents for candidate mining, alias/canonicalization review, and evidence coverage checks.
- Do not let parallelization change evidence quality requirements: all outputs must still pass the same citation, coverage, and schema gates.

## 3 Reusable book pipeline

Use this pipeline for any new book.

### Stage -1: Confirm language mode with the user
Input:
- User preference.

Output:
- One of:
  - `English only`
  - `English + L2` (where L2 is user-selected)

Rules:
- If `English only`, complete all stages in English data files only.
- If `English + L2`, run each content stage in both languages and enforce parity checks in Stage F.

### Stage 0: One-time PDF to chapter-text extraction
Input:
- Full book PDF.

Output:
- Raw per-chapter text files at `tmp/chapters/chap01.txt` ... `tmp/chapters/chapNN.txt`.

Requirements:
- Run this stage once per source book edition, then reuse the extracted chapter files for all later stages.
- Keep page-number markers in chapter files so downstream evidence can cite exact pages.
- Keep file naming stable (`chapNN.txt`) so every downstream script can be re-run without reconfiguration.
- Regenerate extraction only when one of these changes:
  - source PDF file/version
  - chapter boundary decisions
  - extraction quality fixes that affect text fidelity

### Stage A: Normalize extracted chapter text
Input:
- `tmp/chapters/chapNN.txt` from Stage 0.

Output:
- Cleaned chapter corpus (artifact-filtered text) with page references preserved.

Requirements:
- Remove extraction artifacts (headers/footers/page counters/repeated boilerplate) using repeat-pattern detection across chapters.
- Preserve page boundaries or page references so evidence citations can point to exact pages.

### Stage B: Build chapter argument mindmaps
Input:
- Full chapter text.

Output:
- `chapters/chapter-XX.js` (and `.zh.js` if bilingual) using:
  - `thesis`
  - `flowSections[]` with `title`, `note`, `steps[]`, `evidence[]`

Requirements:
- Cover early/middle/late pages of each chapter.
- Keep steps non-duplicative.
- Group subarguments semantically (mechanism/actor/process/theme), not by page adjacency.
- It is valid and expected for one subargument to cite evidence from non-contiguous pages across the chapter.
- Do not structure `flowSections` as a linear page walk; section boundaries should reflect argument logic.
- Use concrete actor + mechanism + setting + time + outcome language.
- Keep evidence page-cited (`(p. X)`).
- Add thesis superscript anchors to key sections.

### Stage C: Discover keyword candidates
Input:
- Chapter corpus from Stage A.

Output:
- Candidate list with chapter coverage and rationale.

Method requirements:
- Use corpus statistics (n-gram recurrence, chapter spread, context diversity).
- Canonicalize near duplicates (plural/singular, hyphen variants, alias merges).
- No pre-curated book-specific candidate inventories.
- Run in parallel with Stage B once Stage A is complete.

### Stage D: Curate final keyword cards
Input:
- Candidate list + chapter mindmaps.

Output:
- `BOOK_DATA.themes[]` entries in `book-data.js` (and mirrored in `book-data.zh.js` when bilingual).

Required schema per theme:
- `id`, `label`, `description`, `definition`, `group`, `aliases[]`, `applications[]`
- `applications[]` item: `{ chapter, setting, time, point, evidence[] }`

Rules:
- Every chapter referenced by a theme must appear in at least one application.
- Each application must be a distinct context.
- Definition should use clause-local superscript citations to application anchors.

### Stage E: Build synthesis flow
Input:
- Chapter theses + flow sections.

Output:
- `BOOK_DATA.coreArgument`
- `BOOK_DATA.flow[]` with `thesisLinks[]`

Rules:
- Flow steps must be chronological and non-overlapping.
- Every chapter must appear in at least one flow step.
- Every chapter listed in a step must appear in that step's `thesisLinks[]`.

### Stage F: Bilingual parity requirements (if enabled)
- Keep IDs stable across languages:
  - chapter section anchors: `chapter-{id}-section-{n}`
  - theme application anchors: `theme-{themeId}-application-{n}`
- Keep theme IDs and flow IDs aligned across `book-data.js` and the selected second-language book data file (Chinese in this repo: `book-data.zh.js`).
- Keep chapter index ordering aligned across `chapters/index.js` and the selected second-language chapter index (Chinese in this repo: `chapters/index.zh.js`).

## 4 Chapter renderer compatibility

### Current renderer fallback

`script.js` renders chapter body in this order:
1. `flowSections` path (`thesis` + collapsible sections)
2. legacy `flow` path
3. legacy `argument` + `evidence` path

Preferred schema is `thesis + flowSections[]`; preserve legacy compatibility unless explicitly migrating.

## 5 Keyword renderer compatibility

### 5.1 Theme schema (`BOOK_DATA.themes[]`)
Each theme must include:
- `id`
- `label`
- `description`
- `definition`
- `group`: one of `mechanisms`, `institutions-actors`, `places-regions`
- `aliases[]`
- `applications[]` with:
  - `chapter` (integer)
  - `setting`
  - `time`
  - `point`
  - `evidence[]`

### 5.2 Keyword UI contract
- Group order:
  1. Mechanisms
  2. Institutions & Actors
  3. Places & Regions
- Groups are collapsible and collapsed by default.
- Each group renders keyword tiles in two columns.
- Clicking a keyword:
  - auto-expands its group
  - hides non-active keyword tiles
  - renders one keyword detail card
  - highlights relevant chapters and flow nodes
- Applications render as independent collapsible sections.
- Application header format is label + chapter superscript (for example `Application<sup>8</sup>`).

### 5.3 Citation behavior
- Preferred: embed citation anchors directly inside `definition` at the exact clause being evidenced.
- Renderer fallback exists in `buildThemeDefinition`, but do not rely on fallback when authoring high-quality definitions.

## 6 Validation gates

### 6.1 Content/data gates
- Full chapter coverage for each chapter summary.
- Theme applications cover all chapter references for each theme.
- Flow coverage includes all chapters.
- Anchor links resolve 1:1 to existing sections/applications.
- Chapter subarguments are semantically grouped; evidence can span distant pages and is not constrained to page-order grouping.

### 6.2 Structural gates
Run before finalizing:
1. Confirm chapter extraction artifacts exist and are reusable: `tmp/chapters/chap01.txt` ... `tmp/chapters/chapNN.txt`
2. `python3 scripts/keyword_candidates.py --tmp-dir tmp/chapters --min-chapters 3 --out keyword_candidates.md`
3. `python3 scripts/build_keyword_cards.py --keyword-candidates keyword_candidates.md --chapters-dir tmp/chapters --chapter-key-lines tmp/chapter_key_lines.txt --book-data book-data.js`
4. `python3 scripts/validate_keyword_cards.py --book-data book-data.js --keyword-candidates keyword_candidates.md`
5. `python3 scripts/check_agents_sync.py --agents AGENTS.md --index index.html --script script.js --styles styles.css`

For script-only sanity checks:
- `python3 -m py_compile scripts/keyword_candidates.py scripts/build_keyword_cards.py scripts/validate_keyword_cards.py scripts/check_agents_sync.py`

## 7 AGENTS maintenance rule

When website structure changes, immediately update this file to match:
- data file locations
- renderer field usage
- fallback behavior
- UI interactions (toggles, grouping, language behavior)
- validation commands and assumptions

Do not leave AGENTS describing behavior that no longer exists in `script.js`.

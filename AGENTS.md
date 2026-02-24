# Book Website Spec (Current Structure + Reusable Pipeline)

Use this file when updating chapter content, keyword data, or synthesis flow for this site.
This spec is synced to the current implementation in `site/`, chapter modules, and book data modules.

## 0 Directory layout

```
book_summary/
├── input/{collection}/{book}/       ← raw source files (PDF/EPUB); gitignored
├── extracted/{collection}/{book}/   ← per-chapter markdown; gitignored
│   └── chapter-XX.md
├── site/                            ← output website
│   ├── index.html                   ← site landing (lists collections)
│   ├── renderer.js                  ← shared rendering module
│   ├── styles.css                   ← shared styles
│   └── {collection}/{book}/         ← one book site
│       ├── index.html               ← book page (imports renderer.js)
│       ├── book-data.js             ← L1 book data
│       ├── book-data.zh.js          ← L2 book data
│       └── chapters/                ← chapter JS modules
├── scripts/                         ← helper scripts
├── tmp/                             ← throwaway extraction artifacts
└── AGENTS.md
```

## 1 Source of truth

### 1.1 UI and rendering files
- `site/{collection}/{book}/index.html`: book page structure and language switch controls.
- `site/renderer.js`: shared rendering module (UI text, interactions, filtering, language switching). Exports `initBook(data)`.
- `site/styles.css`: layout and interaction styling (including keyword group collapse behavior and section toggles).
- `site/index.html`: site landing page listing collections and books.

### 1.2 Data files (per book, under `site/{collection}/{book}/`)
- Primary (L1) book data: `book-data.js`
- Secondary (L2) book data (e.g. Chinese: `book-data.zh.js`)
- Primary (L1) chapter modules: `chapters/chapter-XX.js`
- Secondary (L2) chapter modules (e.g. Chinese: `chapters/chapter-XX.zh.js`)
- Primary (L1) chapter index: `chapters/index.js`
- Secondary (L2) chapter index (e.g. Chinese: `chapters/index.zh.js`)

### 1.3 Raw inputs and extracted text (gitignored)
- `input/{collection}/{book}/`: source PDF/EPUB files. Never committed.
- `extracted/{collection}/{book}/chapter-XX.md`: per-chapter markdown extracted from source. Never committed. Stable paths for scripts.

## 2 Operating principles

### 2.1 Priority order
1. Evidence fidelity to source pages.
2. Full chapter-range coverage.
3. Schema/UI compatibility with current renderer.
4. Concise, concrete argument writing.

### 2.2 Cross-book portability rule (hard requirement)
- Do not hardcode book-specific keyword lists, actor lists, place lists, or chapter-name lists in workflow logic.
- Use corpus-derived discovery first (frequency, spread across chapters, context diversity), then human review/merge.
- If any script contains lexical heuristics, keep them language-level and generic (for example, tokenization, stopwords, suffix patterns), not title/book dependent.
- Manual reviewer decisions must be captured in data outputs (`book-data*.js`), not buried as hidden constants in scripts.

### 2.3 Script role
- Scripts are helpers, not the source of truth.
- Final source of truth is the data modules consumed by `site/renderer.js`.
- If helper-script output conflicts with chapter evidence, chapter evidence wins.

### 2.4 Language-scope decision (required)
- Before running the pipeline, explicitly ask the user which language mode they want:
  - `Primary Language (L1) only`
  - `Primary (L1) + Secondary (L2)` (where L2 is user-selected)
- If the book's original language is not English, treat the original language as Primary (L1).
- Do not assume bilingual output by default for a new book.
- For example, if the L2 is Chinese, use `*.zh.*` files; for a different L2, use the same schema/parity rules with that language's ISO code.
- When producing translations, use the latest ChatGPT/Claude model for the translation pass.
- When writing chapter summaries, use a model with high reasoning capability.

### 2.5 Parallel multi-agent execution rule (required)
- After Stage A, run chapter summary extraction (Stage B) and keyword candidate discovery (Stage C) in parallel.
- For chapter summaries, split work across multiple agents by chapter or chapter ranges, then merge through one coordinator pass for schema consistency.
- For keyword extraction, allow separate agents for candidate mining, alias/canonicalization review, and evidence coverage checks.
- Do not let parallelization change evidence quality requirements: all outputs must still pass the same citation, coverage, and schema gates.

## 3 Reusable book pipeline

Use this pipeline for any new book.

### Stage -1: Confirm language
Input:
- User preference for Language Mode.

Output:
- One of:
  - `L1 only`
  - `L1 + L2` (where L2 is user-selected)

Rules:
- If `L1 only`, complete all stages in Primary language data files only.
- If `L1 + L2`, run each content stage in both languages and enforce parity checks in Stage F.

### Stage 0: One-time PDF to chapter-text extraction
Input:
- Full book PDF at `input/{collection}/{book}/`.

Output:
- Raw per-chapter text files at `tmp/chapters/chap01.txt` ... `tmp/chapters/chapNN.txt`.
- Stable extracted markdown at `extracted/{collection}/{book}/chapter-XX.md` (copied from tmp after extraction).

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
- `site/{collection}/{book}/chapters/chapter-XX.js` (and `.zh.js` if the L2 language is Chinese) using:
  - `thesis`
  - `flowSections[]` with `title`, `note`, `steps[]`, `evidence[]`

Requirements:
- Cover early/middle/late pages of each chapter.
- Keep steps non-duplicative.
- Group subarguments semantically (mechanism/actor/process/context), not by page adjacency.
- It is valid and expected for one subargument to cite evidence from non-contiguous pages across the chapter.
- Do not structure `flowSections` as a linear page walk; section boundaries should reflect argument logic.
- Use concrete actor + mechanism + setting + time/context + outcome language.
- Keep evidence page-cited (`(p. X)`).
- Add thesis superscript anchors to key sections.
- The thesis must be a high-level conceptual summary of the chapter's argument arc; it must not repeat subarguments or their evidence verbatim.
- The thesis must NOT contain specific numbers, percentages, dates, dollar amounts, population counts, or verbatim evidence quotes—all quantitative detail and direct quotes belong in flowSection steps and evidence.
- Every flowSection must be referenced by at least one superscript anchor in the thesis; distribute anchors after the clause most closely associated with each section's argument.

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
- `BOOK_DATA.keywords[]` entries in `site/{collection}/{book}/book-data.js` (and mirrored in the L2 data file when bilingual, e.g. `book-data.zh.js` if the L2 language is Chinese).

#### Keyword card fields

- `id` (string): URL-safe identifier. Lowercase, hyphenated if it is not a single word (e.g., `"colonial-rule"`).
- `label` (string): Display name. Human-readable, may include spaces (e.g., `"colonial rule"`).
- `description` (string): One-line summary capturing the keyword's essence.
- `definition` (string): 1-2 sentences explaining how the book uses this term; include superscript citations to applications.
- `group` (string): Category. One of: `"mechanisms"`, `"actors"`, `"concepts"`, or other domain-specific groups.
- `aliases[]` (array): Alternative names the author uses. Empty array `[]` if none.
- `applications[]` (array): Chapter appearances. See application fields below.

#### Application fields (each `applications[]` item)

- `chapters[]` (array): Chapter numbers where this application appears (e.g., `[5, 9]`).
- `setting` (string): Use relevant context (place, time, etc.), separated by ` • `.
- `point` (string): One sentence summarizing what this application demonstrates about the keyword.
- `evidence[]` (array): Direct textual evidence with page citations (e.g., `"Quote text here. (p. 170-171)"`).

#### Rules

- Every chapter referenced by a keyword must appear in at least one application.
- Each application must be a distinct context; merge applications sharing the same setting.
- Definition should use clause-local superscript citations to application anchors.

### Stage E: Build synthesis flow
Input:
- Chapter theses + flow sections.

Output:
- `BOOK_DATA.coreArgument`
- `BOOK_DATA.flow[]` with `thesisLinks[]`

Rules:
- Flow steps must follow the book's primary structure and be non-overlapping.
- Every chapter must appear in at least one flow step.
- Every chapter listed in a step must appear in that step's `thesisLinks[]`.

### Stage F: Bilingual parity requirements (if enabled)
- Keep IDs stable across languages:
  - chapter section anchors: `chapter-{id}-section-{n}`
  - keyword application anchors: `keyword-{keywordId}-application-{n}`
- Keep keyword IDs and flow IDs aligned across `site/{collection}/{book}/book-data.js` (L1) and the selected L2 book data file (e.g. `book-data.zh.js`).
- Keep chapter index ordering aligned across `site/{collection}/{book}/chapters/index.js` (L1) and the selected L2 chapter index (e.g. `chapters/index.zh.js`).

## 4 Chapter renderer compatibility

`site/renderer.js` renders chapter body using the `thesis + flowSections[]` schema.

## 5 Keyword renderer compatibility

### 5.1 Keyword schema (`BOOK_DATA.keywords[]`)
Each keyword must include:
- `id`
- `label`
- `description`
- `definition`
- `group`: one of `mechanisms`, `institutions-actors`, `places-regions`
- `aliases[]`
- `applications[]` with:
  - `chapter` (integer)
  - `setting`
  - `time_context`
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
- Renderer fallback exists in `buildKeywordDefinition`, but do not rely on fallback when authoring high-quality definitions.

## 6 Validation gates

### 6.1 Content/data gates
- Full chapter coverage for each chapter summary.
- Keyword applications cover all chapter references for each keyword.
- Flow coverage includes all chapters.
- Anchor links resolve 1:1 to existing sections/applications.
- Chapter subarguments are semantically grouped; evidence can span distant pages and is not constrained to page-order grouping.

### 6.2 Structural gates
Run before finalizing:
1. Confirm chapter extraction artifacts exist and are reusable (e.g., standard chapter text files).
2. Validate keyword candidates:
   - Ensure candidates appear in a minimum number of chapters (e.g., 3+).
   - Filter for meaningful distribution and context.
3. Validate keyword cards against book data:
   - Ensure all keywords found in candidates are represented or deliberately excluded.
   - Verify citation integrity and schema compliance.
4. Verify synchronization between documentation and implementation:
   - Ensure `AGENTS.md` rules match the current codebase behavior.
   - Check that `site/renderer.js`, `site/styles.css`, and book `index.html` files create the UI described in specs.
5. Quote-escape validation:
   - Ensure all string content in data files is properly escaped for valid JavaScript parsing in all target languages.
   - Verify that data modules import correctly in a Node.js environment without syntax errors.

## 7 AGENTS maintenance rule

When website structure changes, immediately update this file to match:
- data file locations
- renderer field usage
- fallback behavior
- UI interactions (toggles, grouping, language behavior)
- validation logic and assumptions

Do not leave AGENTS describing behavior that no longer exists in the runtime code.

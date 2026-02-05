# Summarization rules

Use this file when updating chapter content in `chapters/chapter-XX.js` and book-level data in `book-data.js`.
These rules are organized by the three website sections: Chapter Argument Mindmap, Keywords, and Book Synthesis Flow.

## Chapter Argument Mindmap
### Content goals
- Read the full chapter text from `Empire of Cotton.pdf` and cover the entire page range.
- Build paragraph-level notes first, then synthesize them into structured argument steps so no part of the chapter is skipped.
- **Subarguments and their supporting evidence do not need to be introduced in strict page order; group evidence by mechanism/actors and merge overlapping subarguments even when the supporting pages are far apart.**
- Build a concrete, evidence-led logical progression for each chapter (no generic language unless immediately tied to specific evidence).
- Each claim should be anchored to specific evidence with page numbers like `(p. 34)`.
- Prefer paraphrase plus page numbers, not long quotes.
- Avoid vague words (for example: "important," "significant," "major," "big") unless you immediately show what that means with evidence.
- Avoid abstract nouns without concrete definition (for example: "coercion," "credit," "reconfiguration") unless you immediately specify the concrete mechanism, actor, and evidence that define the term in that context.

### Structure in `chapters/chapter-XX.js`
- Each chapter summary must live in its own standalone module: `chapters/chapter-01.js` ... `chapters/chapter-14.js`.
- Do not add or edit chapter summaries in `script.js` (UI logic only) or inline inside `book-data.js`.
- Use `thesis` and `flowSections` for updated chapters.
- `thesis` must be concrete and specific (time, place, actors, mechanisms, and outcomes where applicable).
- Add hyperlink(s) in each `thesis` that point to the relevant subarguments below (flow sections) using in-page anchors.
- Use superscript numeric links (e.g., `<sup><a href="#chapter-1-section-1">1</a></sup>`) and keep a small space between adjacent superscripts (via CSS or a literal space).
- If a subargument cannot fit in the thesis without bloating it, keep it only in the steps (it is too detailed for the thesis).
- `flowSections` is an array of grouped subsections to make the argument structure explicit:
  - `title`: short, descriptive label of the subsection.
  - `note`: one-sentence subtitle explaining the relationship among the steps in that subsection; write it as a lowercase fragment (do not start with "This section...").
  - `steps`: ordered list of points; each step includes `point` and `evidence[]`.
- Keep subsection titles informative by combining `title` + `note` in the UI.

### UI behavior
- Each subsection has its own show/hide toggle for its steps.
- Do not use a single global toggle for the entire chapter.

### Quality checks
- Make sure the flow spans the whole chapter, including early, middle, and late pages.
- Keep the number of steps proportional to the chapter length.
- Ensure no step is a duplicate of another step; each should add a new part of the argument.
- Co-design check: the thesis should cite most flow sections (ideally all). If there are too many sections to cite cleanly, merge sections until the thesis can reference them without bloating (target ~4-7 sections unless the chapter absolutely requires more).

## Keywords
### Content goals
- Find recurring keywords (abstract terms repeated across chapters) and show their lineage by placing **each unique context where they occur** into `applications[]`.
- The goal is to define keywords by use: track how meanings shift or stretch across time and place by naming actors, mechanisms, and settings each time the keyword appears in a distinct context.
- Each keyword needs a concrete definition that names the actor(s), mechanism(s), and scope (where/when it applies).
- For every chapter that lists a theme id in `chapter.themes`, add one or more `applications[]` entries for that keyword when the contexts differ (including multiple entries within the same chapter if needed).
- Each `applications[]` entry must include:
  - `chapter`: chapter number.
  - `setting`: specific place or institutional context.
  - `time`: specific period or dated marker.
  - `point`: one concrete sentence tying the keyword to chapter evidence.
  - `evidence[]`: paraphrased facts with page citations like `(p. 34)`.

### Discovery workflow
- Scan each chapter for abstract terms that recur (maybe build a frequency counter for abstract words related to the book's themes and arguments); canonicalize minor variants (plural/hyphenation).
- Prefer terms that appear across multiple chapters (default threshold: ≥3 chapters, or fewer if central to the core argument).

### Structure in `book-data.js`
- Extend each item in `BOOK_DATA.themes[]` (keywords) with:
  - `definition`: string.
  - `applications[]`: array of `{ chapter, setting, time, point, evidence[] }`.
- Keywords are stored in `BOOK_DATA.themes[]` and referenced via `chapter.themes` (reader-facing term is "keyword").

### UI behavior
- Clicking a keyword should render a large keyword detail card below the keyword list and hide other keyword tiles.
- The keyword detail card should display the keyword label, description/definition, and all `applications[]` entries (including setting, time, point, and evidence).
- Clicking a keyword should also highlight the relevant chapters.

### Quality checks
- Every chapter that includes a theme id must be represented at least once in that keyword’s `applications[]`.
- Add multiple entries per chapter when the keyword appears in distinct contexts (different setting/time/actors/mechanism).
- Do not repeat the same application across chapters; each entry must add new evidence.
- Each `applications[]` entry must specify setting and time explicitly.
- Avoid vague terms; if used, immediately define them with concrete actors, mechanisms, and evidence.

## Book Synthesis Flow
### Content goals
- The Book Synthesis Flow subtitle (the text under the "Book Synthesis Flow" heading) must state the book’s **main argument** and provide a **whole-book summary** in evidence-led sentences (actors + mechanisms + chronology; no chapter-by-chapter list).
- Each flow step must synthesize the main arguments from the chapter theses it covers, naming actors, mechanisms, and chronology explicitly.
- Use page-cited evidence drawn from those chapters’ theses and flow steps.
- Avoid generic summaries; every sentence should tie to concrete evidence.

### Structure in `book-data.js`
- Store the Book Synthesis Flow subtitle in `BOOK_DATA.coreArgument` (rendered into the `#coreArgument` element by `script.js`).
- Extend each item in `BOOK_DATA.flow[]` with:
  - `thesisLinks[]`: array of `{ chapter, point, evidence[] }`.

### Quality checks
- Every chapter listed in a flow step’s `chapters` array must appear at least once in that step’s `thesisLinks[]`.
- Each `thesisLinks[]` entry must include page citations in `evidence[]`.
- Every chapter in the book must appear in at least one flow step’s `thesisLinks[]`.
- Flow steps must remain non-overlapping and chronologically ordered.

## Context handling
- After a chapter summary is complete, write it into the appropriate `chapters/chapter-XX.js` file and do not paste the full summary into the response.
- Do not keep intermediate notes or draft summaries in ongoing context; once written to the chapter file, avoid repeating the chapter summary in chat.

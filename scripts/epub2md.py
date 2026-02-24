#!/usr/bin/env python3
"""
epub2md - Convert EPUB files to clean Markdown.

Handles Calibre-generated EPUBs with proper:
- Heading hierarchy from TOC
- Image extraction and references
- Italic/bold formatting
- Globally-numbered footnotes with definitions
- Blockquotes

Usage:
    python3 epub2md.py "Book Title.epub"
    python3 epub2md.py "Book Title.epub" -o output.md

Output files are named based on the EPUB filename:
    "Book Title.epub" -> "Book Title.md" + "Book Title_images/"
"""

import argparse
import os
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from html.parser import HTMLParser
from pathlib import Path


# ---------------------------------------------------------------------------
# EPUB structure parsing
# ---------------------------------------------------------------------------

def extract_epub(epub_path, dest_dir):
    """Unzip EPUB into dest_dir."""
    with zipfile.ZipFile(epub_path, "r") as zf:
        zf.extractall(dest_dir)


def find_opf(epub_dir):
    """Find the .opf file (content manifest) inside the EPUB."""
    container_xml = os.path.join(epub_dir, "META-INF", "container.xml")
    if os.path.exists(container_xml):
        tree = ET.parse(container_xml)
        root = tree.getroot()
        ns = {"c": "urn:oasis:names:tc:opendocument:xmlns:container"}
        rootfile = root.find(".//c:rootfile", ns)
        if rootfile is not None:
            return os.path.join(epub_dir, rootfile.attrib["full-path"])
    # Fallback: look for .opf files
    for f in Path(epub_dir).rglob("*.opf"):
        return str(f)
    return None


def parse_opf(opf_path):
    """Parse .opf to get spine order, manifest, and metadata."""
    tree = ET.parse(opf_path)
    root = tree.getroot()
    opf_dir = os.path.dirname(opf_path)

    # Namespace handling
    ns_map = {"opf": "http://www.idpf.org/2007/opf", "dc": "http://purl.org/dc/elements/1.1/"}

    # Metadata
    title = ""
    author = ""
    for t in root.findall(".//{http://purl.org/dc/elements/1.1/}title"):
        title = t.text or ""
    for c in root.findall(".//{http://purl.org/dc/elements/1.1/}creator"):
        author = c.text or ""

    # Manifest: id -> href
    manifest = {}
    for item in root.findall(".//{http://www.idpf.org/2007/opf}item"):
        manifest[item.attrib["id"]] = item.attrib["href"]

    # Spine order
    spine_files = []
    for itemref in root.findall(".//{http://www.idpf.org/2007/opf}itemref"):
        idref = itemref.attrib["idref"]
        if idref in manifest:
            href = manifest[idref]
            if href.endswith((".html", ".xhtml", ".htm")):
                spine_files.append(href)

    return title, author, spine_files, opf_dir


def find_ncx(epub_dir):
    """Find the .ncx table of contents file."""
    for f in Path(epub_dir).rglob("*.ncx"):
        return str(f)
    return None


def parse_toc(ncx_path):
    """Parse toc.ncx to get chapter titles mapped to filenames."""
    tree = ET.parse(ncx_path)
    root = tree.getroot()
    ns = {"ncx": "http://www.daisy.org/z3986/2005/ncx/"}
    toc = []
    for nav in root.findall(".//ncx:navPoint", ns):
        label = nav.find("ncx:navLabel/ncx:text", ns)
        content = nav.find("ncx:content", ns)
        if label is not None and content is not None:
            src = content.attrib["src"].split("#")[0]
            toc.append({"label": label.text or "", "src": src})
    return toc


# ---------------------------------------------------------------------------
# Auto-detect notes files and chapter structure
# ---------------------------------------------------------------------------

FRONT_MATTER_LABELS = {
    "cover", "other books by this author", "also by", "title page",
    "copyright", "epigraph", "contents", "table of contents",
    "dedication", "preface", "foreword", "introduction",
    "half title", "halftitle", "frontispiece",
}

BACK_MATTER_LABELS = {
    "appendix", "acknowledgments", "acknowledgements", "about the author",
    "notes", "endnotes", "bibliography", "references", "index",
    "glossary", "afterword", "epilogue", "colophon",
    "further reading", "selected bibliography", "credits",
    "illustration credits", "photo credits", "permissions",
}


def classify_toc_entries(toc):
    """Classify TOC entries as front matter, chapter, or back matter."""
    classified = []
    for entry in toc:
        label_lower = entry["label"].lower().strip()
        # Check if it's a numbered chapter (e.g., "1. Title", "Chapter 1", etc.)
        is_chapter = bool(re.match(r'^(\d+[\.\):]?\s*\S|chapter\s+\d)', label_lower))
        is_front = any(label_lower.startswith(fm) for fm in FRONT_MATTER_LABELS)
        is_back = any(label_lower.startswith(bm) for bm in BACK_MATTER_LABELS)

        if is_chapter:
            kind = "chapter"
        elif is_front:
            kind = "front"
        elif is_back:
            kind = "back"
        else:
            # If not clearly front/back, treat as chapter
            kind = "chapter"

        classified.append({**entry, "kind": kind})
    return classified


def detect_notes_files(epub_dir, spine_files, toc):
    """Auto-detect which spine files contain endnotes/footnotes."""
    notes_files = set()
    notes_start = None

    # Find "Notes" or "Endnotes" in TOC
    for entry in toc:
        if entry["label"].lower().strip() in ("notes", "endnotes"):
            notes_start = entry["src"]
            break

    if not notes_start:
        return notes_files

    # All files from notes_start until the next non-notes back matter section
    in_notes = False
    next_section_labels = BACK_MATTER_LABELS - {"notes", "endnotes"}
    toc_srcs = {e["src"] for e in toc if e["label"].lower().strip() in next_section_labels}

    for f in spine_files:
        if f == notes_start:
            in_notes = True
        if in_notes:
            if f in toc_srcs:
                break
            notes_files.add(f)

    return notes_files


def get_numbered_chapters(classified_toc):
    """Get only the top-level numbered chapters (not sub-sections).

    Identifies entries that start with a number (e.g. "1. Title", "Chapter 2")
    and deduplicates by source file to handle TOCs with sub-entries.
    """
    seen_files = set()
    chapters = []
    for entry in classified_toc:
        if entry["kind"] != "chapter":
            continue
        label_lower = entry["label"].lower().strip()
        is_numbered = bool(re.match(r'^(\d+[\.\):]?\s*\S|chapter\s+\d)', label_lower))
        if is_numbered and entry["src"] not in seen_files:
            chapters.append(entry)
            seen_files.add(entry["src"])
    return chapters


def build_chapter_file_map(classified_toc, spine_files):
    """Map each spine file to its numbered chapter name for footnote grouping."""
    chapters = get_numbered_chapters(classified_toc)
    file_to_chapter = {}

    for i, ch in enumerate(chapters):
        ch_src = ch["src"]
        next_src = chapters[i + 1]["src"] if i + 1 < len(chapters) else None

        in_chapter = False
        for f in spine_files:
            if f == ch_src:
                in_chapter = True
            if in_chapter:
                if next_src and f == next_src:
                    break
                file_to_chapter[f] = ch["label"]

    return file_to_chapter


# ---------------------------------------------------------------------------
# HTML to Markdown converters
# ---------------------------------------------------------------------------

def detect_heading_classes(css_content):
    """Detect CSS classes likely used for section headings.

    Heuristic: block-level classes with text-align: center and margin-top >= 2em.
    """
    heading_classes = set()
    # Parse simple CSS class definitions
    for match in re.finditer(r'\.(\w+)\s*\{([^}]+)\}', css_content):
        cls_name = match.group(1)
        props = match.group(2)
        if "text-align: center" in props and re.search(r'margin-top:\s*[2-9]', props):
            heading_classes.add(cls_name)
    return heading_classes


class ContentConverter(HTMLParser):
    """Convert EPUB content HTML to markdown."""

    def __init__(self, fn_offset=0, heading_classes=None, sup_classes=None,
                 notes_filenames=None):
        super().__init__()
        self.result = []
        self.current_text = []
        self.in_italic = False
        self.in_bold = False
        self.in_sup = False
        self.in_fn_link = False  # inside <a> that links to notes
        self.in_blockquote = 0
        self.skip_svg = False
        self.fn_offset = fn_offset
        self.max_fn = 0
        self.heading_classes = heading_classes or set()
        self.sup_classes = sup_classes or set()
        self.notes_filenames = notes_filenames or set()  # basenames of notes files
        self.img_dir = ""

    def _is_note_link(self, href):
        """Check if an <a> href points to a notes/endnotes file."""
        if not href:
            return False
        # Extract the filename from the href (before #)
        target = href.split("#")[0]
        basename = os.path.basename(target)
        return basename in self.notes_filenames

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get("class", "")

        if tag == "svg":
            self.skip_svg = True
            return
        if self.skip_svg:
            return

        if tag == "img":
            src = attrs_dict.get("src", "")
            if src:
                self._flush_text()
                basename = os.path.basename(src)
                self.result.append(f"\n![]({self.img_dir}{basename})\n")
            return

        # Detect footnote ref links: <a href="Notes.xhtml#fn1">1</a>
        if tag == "a":
            href = attrs_dict.get("href", "")
            if self._is_note_link(href):
                self.in_fn_link = True
            return

        if tag == "span":
            if "italic" in cls:
                self.in_italic = True
                self.current_text.append("*")
            elif "bold" in cls:
                self.in_bold = True
                self.current_text.append("**")

        if tag == "i":
            self.in_italic = True
            self.current_text.append("*")

        if tag == "b":
            self.in_bold = True
            self.current_text.append("**")

        if tag == "sup" or (tag == "span" and self._is_superscript(cls)):
            self.in_sup = True

        if tag == "blockquote":
            self.in_blockquote += 1

        if tag == "br":
            self.current_text.append("\n")

        if tag == "p":
            self._flush_text()
            if any(c in cls for c in self.heading_classes):
                self.current_text.append("\n### ")

    def handle_endtag(self, tag):
        if tag == "svg":
            self.skip_svg = False
            return
        if self.skip_svg:
            return

        if tag == "a":
            self.in_fn_link = False
            return

        if tag == "span":
            if self.in_italic:
                self.current_text.append("*")
                self.in_italic = False
            elif self.in_bold:
                self.current_text.append("**")
                self.in_bold = False

        if tag == "i":
            if self.in_italic:
                self.current_text.append("*")
                self.in_italic = False

        if tag == "b":
            if self.in_bold:
                self.current_text.append("**")
                self.in_bold = False

        if tag == "sup" or (self.in_sup and tag == "span"):
            self.in_sup = False

        if tag == "blockquote":
            self.in_blockquote = max(0, self.in_blockquote - 1)

        if tag == "p":
            self._flush_text()
            self.result.append("\n")

    def handle_data(self, data):
        if self.skip_svg:
            return
        # Footnote ref: either in <sup> or in <a> linking to notes file
        if self.in_sup or self.in_fn_link:
            text = data.strip()
            # Only treat as footnote if text is a bare number (with optional period)
            # Reject things like "ref3n20", "page_272", etc.
            if re.match(r'^\d+\.?$', text):
                num = re.sub(r'[^0-9]', '', text)
                global_num = int(num) + self.fn_offset
                self.max_fn = max(self.max_fn, int(num))
                self.current_text.append(f"[^{global_num}]")
            else:
                # Not a footnote number — output the text normally
                self.current_text.append(data)
            return
        self.current_text.append(data)

    def _flush_text(self):
        if self.current_text:
            text = "".join(self.current_text).strip()
            if text:
                if self.in_blockquote > 0:
                    lines = text.split("\n")
                    text = "\n".join("> " + line for line in lines)
                self.result.append(text)
            self.current_text = []

    def _is_superscript(self, cls):
        """Detect superscript classes (used for footnote refs)."""
        if self.sup_classes and any(c in cls for c in self.sup_classes):
            return True
        return any(c in cls for c in ("calibre22", "sup", "superscript", "footnote"))

    def get_markdown(self):
        self._flush_text()
        return "\n".join(self.result)


class NotesParser(HTMLParser):
    """Extract footnotes from endnotes HTML.

    Handles multiple EPUB patterns:
    - Calibre: <blockquote><blockquote><a>N</a> text</blockquote></blockquote>
    - Publisher A: <p class="note"><span class="note"><b><a>N</a></b></span> text</p>
    - Publisher B: <p class="nlist2"><span class="list1"><a>N.</a></span> text</p>
    """

    def __init__(self, fn_offset=0):
        super().__init__()
        self.footnotes = {}
        self.fn_offset = fn_offset
        self.current_num = None
        self.current_text = []
        self.in_note_link = False  # inside <a> that links back to content
        self.in_italic = False
        self.in_bold = False
        self.in_heading = False
        self.in_note_p = False  # inside a <p> that contains a note
        self.in_blockquote = 0

    def _is_chapter_heading(self, tag, cls):
        """Detect chapter heading elements in the notes section."""
        # Various patterns: "note-h3", "chaptitleh3", calibre large-font classes
        heading_hints = ("note-h3", "chaptitle", "calibre17", "calibre65",
                         "bmtitle", "chaptitlea")
        return any(h in cls for h in heading_hints)

    def _is_note_paragraph(self, cls):
        """Detect paragraph elements that contain individual footnotes."""
        note_hints = ("note", "nlist", "endnote", "footnote")
        return any(h in cls for h in note_hints)

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get("class", "")
        href = attrs_dict.get("href", "")

        if tag == "blockquote":
            self.in_blockquote += 1
            return

        # Detect heading paragraphs (chapter titles within notes)
        if tag == "p":
            if self._is_chapter_heading(tag, cls):
                self.in_heading = True
                return
            if self._is_note_paragraph(cls):
                self.in_note_p = True
            # For Calibre pattern, blockquote depth >= 2 acts as note container
            if self.in_blockquote >= 2:
                self.in_note_p = True

        # <a> tags that link back to content = footnote number
        if tag == "a" and (self.in_note_p or self.in_blockquote >= 2):
            if href and not href.startswith("http"):
                self.in_note_link = True
            elif href.startswith("http"):
                # URL in footnote text — include it
                self.current_text.append(href)
            return

        if tag == "span":
            if "italic" in cls:
                self.in_italic = True
                self.current_text.append("*")
            elif "bold" in cls:
                self.in_bold = True
                self.current_text.append("**")
            elif self._is_chapter_heading(tag, cls):
                self.in_heading = True

        if tag == "i":
            self.in_italic = True
            self.current_text.append("*")

        if tag == "b":
            # Bold inside a note heading = chapter title, skip
            if self.in_heading:
                return
            self.in_bold = True
            self.current_text.append("**")

    def handle_endtag(self, tag):
        if tag == "blockquote":
            self.in_blockquote = max(0, self.in_blockquote - 1)
            return

        if tag == "a":
            self.in_note_link = False
            return

        if tag == "p":
            if self.in_heading:
                self.in_heading = False
                return
            if self.in_note_p:
                self.in_note_p = False
            return

        if tag == "span":
            if self.in_italic:
                self.current_text.append("*")
                self.in_italic = False
            elif self.in_bold:
                self.current_text.append("**")
                self.in_bold = False
            elif self.in_heading:
                self.in_heading = False

        if tag == "i":
            if self.in_italic:
                self.current_text.append("*")
                self.in_italic = False

        if tag == "b":
            if self.in_bold:
                self.current_text.append("**")
                self.in_bold = False

    def handle_data(self, data):
        if self.in_heading:
            return

        # Footnote number link text
        if self.in_note_link:
            num = re.sub(r'[^0-9]', '', data.strip())  # "1." -> "1"
            if num:
                if self.current_num is not None:
                    self._save()
                self.current_num = num
                self.current_text = []
            self.in_note_link = False
            return

        # Collect note text
        if (self.in_note_p or self.in_blockquote >= 2) and self.current_num is not None:
            self.current_text.append(data)

    def _save(self):
        if self.current_num and self.current_text:
            text = "".join(self.current_text).strip()
            if text:
                global_num = int(self.current_num) + self.fn_offset
                self.footnotes[global_num] = text
        self.current_num = None
        self.current_text = []

    def finish(self):
        self._save()
        return self.footnotes


# ---------------------------------------------------------------------------
# Detect superscript class from CSS
# ---------------------------------------------------------------------------

def detect_superscript_classes(css_content):
    """Find CSS classes that represent superscript (footnote refs)."""
    classes = set()
    for match in re.finditer(r'\.(\w+)\s*\{([^}]+)\}', css_content):
        cls_name = match.group(1)
        props = match.group(2)
        if "vertical-align: super" in props or "vertical-align:super" in props:
            classes.add(cls_name)
    return classes


# ---------------------------------------------------------------------------
# Count footnotes per notes file (for offset calculation)
# ---------------------------------------------------------------------------

def _match_chapter(heading_text, chapter_labels):
    """Fuzzy-match a heading from notes to a chapter label."""
    h_lower = heading_text.lower().strip()
    h_stripped = re.sub(r'^\d+[\.\):]?\s*', '', h_lower)

    for ch_label in chapter_labels:
        ch_lower = ch_label.lower().strip()
        ch_stripped = re.sub(r'^\d+[\.\):]?\s*', '', ch_lower)
        if (ch_stripped and h_stripped and
            (ch_stripped in h_stripped or h_stripped in ch_stripped)):
            return ch_label
        if ch_lower == h_lower:
            return ch_label
    return None


def extract_notes_single_file(html, chapter_labels, chapter_offsets):
    """Extract footnotes from a single notes file with multiple chapter sections.

    Splits the HTML at chapter headings, then parses each section with the
    appropriate offset.
    """
    # Split at chapter headings
    heading_pattern = re.compile(
        r'<p[^>]*class="[^"]*(?:note-h3|chaptitle|bmtitle)[^"]*"[^>]*>.*?</p>',
        re.DOTALL
    )

    # Find all heading positions and their text
    headings = []
    for m in heading_pattern.finditer(html):
        text = re.sub(r'<[^>]+>', '', m.group(0)).strip()
        headings.append((m.start(), m.end(), text))

    all_footnotes = {}

    for i, (start, end, heading_text) in enumerate(headings):
        # Get the chunk from after this heading to before the next heading
        chunk_start = end
        chunk_end = headings[i + 1][0] if i + 1 < len(headings) else len(html)
        chunk = html[chunk_start:chunk_end]

        # Match heading to chapter
        ch_label = _match_chapter(heading_text, chapter_labels)
        fn_offset = chapter_offsets.get(ch_label, 0) if ch_label else 0

        # Parse this chunk
        parser = NotesParser(fn_offset=fn_offset)
        parser.feed(chunk)
        fns = parser.finish()
        all_footnotes.update(fns)

    return all_footnotes


def count_per_chapter_footnotes(filepath, chapter_labels):
    """For a single notes file with multiple chapters, count footnotes per chapter.

    Detects chapter headings like "1. Chapter Title" or "Introduction" and counts
    how many footnotes follow each heading before the next one.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    # Find chapter headings and footnote numbers with their positions
    # Headings: <p class="note-h3"> or <p class="chaptitleh3">
    heading_pattern = re.compile(
        r'<p[^>]*class="[^"]*(?:note-h3|chaptitle|bmtitle)[^"]*"[^>]*>(.*?)</p>',
        re.DOTALL
    )
    # Footnote numbers: <a ...>N</a> or <a ...>N.</a>
    fn_pattern = re.compile(r'<a[^>]*>\s*(\d+)\.?\s*</a>')

    # Build list of (position, type, value) events
    events = []
    for m in heading_pattern.finditer(html):
        # Extract text from heading (strip tags)
        heading_text = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        events.append((m.start(), 'heading', heading_text))
    for m in fn_pattern.finditer(html):
        events.append((m.start(), 'fn', int(m.group(1))))
    events.sort(key=lambda x: x[0])

    # Group footnotes under headings
    chapter_counts = {}
    current_heading = None
    current_max = 0

    for pos, etype, value in events:
        if etype == 'heading':
            if current_heading is not None:
                chapter_counts[current_heading] = current_max
            current_heading = value
            current_max = 0
        elif etype == 'fn':
            current_max = max(current_max, value)

    if current_heading is not None:
        chapter_counts[current_heading] = current_max

    # Map heading text to chapter labels (fuzzy match)
    result = {}
    for ch_label in chapter_labels:
        # Try direct match first
        if ch_label in chapter_counts:
            result[ch_label] = chapter_counts[ch_label]
            continue
        # Try partial match: heading text contained in chapter label or vice versa
        ch_lower = ch_label.lower().strip()
        # Strip leading number: "1. Title" -> "title"
        ch_stripped = re.sub(r'^\d+[\.\):]?\s*', '', ch_lower)
        for heading, count in chapter_counts.items():
            h_lower = heading.lower().strip()
            h_stripped = re.sub(r'^\d+[\.\):]?\s*', '', h_lower)
            if (ch_stripped and h_stripped and
                (ch_stripped in h_stripped or h_stripped in ch_stripped)):
                result[ch_label] = count
                break

    return result


def count_footnotes_in_file(filepath):
    """Count the highest footnote number in a notes HTML file.

    Handles various patterns:
    - <span>N</span></a>  (Calibre)
    - <a ...>N</a>        (Publisher links)
    - <a ...>N.</a>       (Numbered with period)
    """
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()
    # Match footnote numbers inside <a> tags (with optional trailing period)
    nums = re.findall(r'<a[^>]*>\s*(\d+)\.?\s*</a>', html)
    nums = [int(n) for n in nums]
    # Also match Calibre pattern: <span>N</span></a>
    nums += [int(n) for n in re.findall(r'<span[^>]*>\s*(\d+)\s*</span>\s*</a>', html)]
    return max(nums) if nums else 0


# ---------------------------------------------------------------------------
# Main conversion pipeline
# ---------------------------------------------------------------------------

def clean_markdown(text):
    """Post-process markdown for cleanliness."""
    # Normalize section breaks
    text = re.sub(r'\n### \*\*\*   \*   \*\*\*', '\n---', text)
    text = re.sub(r'\n### \*\*\*\*\*   \*   \*\*\*\*', '\n---', text)
    # Clean heading formatting: ### **HEADING** -> ### HEADING
    text = re.sub(r'### \*\*(.+?)\*\*', r'### \1', text)
    # Collapse excessive blank lines
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    return text.strip()


def convert_epub(epub_path, output_path=None):
    """Convert an EPUB file to clean markdown.

    Args:
        epub_path: Path to the .epub file.
        output_path: Output .md file path. Defaults to same name as epub.
    """
    epub_path = os.path.abspath(epub_path)
    if not os.path.exists(epub_path):
        print(f"Error: {epub_path} not found", file=sys.stderr)
        sys.exit(1)

    # Derive names from EPUB filename
    epub_stem = os.path.splitext(os.path.basename(epub_path))[0]
    if output_path is None:
        output_path = os.path.join(os.path.dirname(epub_path), f"{epub_stem}.md")
    output_path = os.path.abspath(output_path)
    output_dir = os.path.dirname(output_path)

    # Image dir is always based on the epub stem for uniqueness
    img_dir_name = f"{epub_stem}_images"

    # Extract EPUB to temp directory
    tmp_dir = tempfile.mkdtemp(prefix="epub2md_")
    try:
        print(f"Extracting EPUB...")
        extract_epub(epub_path, tmp_dir)

        # Find and parse OPF
        opf_path = find_opf(tmp_dir)
        if not opf_path:
            print("Error: Could not find .opf manifest", file=sys.stderr)
            sys.exit(1)

        title, author, spine_files, opf_dir = parse_opf(opf_path)
        print(f"Book: {title}")
        if author:
            print(f"Author: {author}")
        print(f"Spine files: {len(spine_files)}")

        # Parse TOC
        ncx_path = find_ncx(tmp_dir)
        toc = parse_toc(ncx_path) if ncx_path else []
        toc_map = {e["src"]: e["label"] for e in toc}
        classified = classify_toc_entries(toc)

        # Detect notes files
        notes_files = detect_notes_files(opf_dir, spine_files, toc)
        print(f"Notes files detected: {len(notes_files)}")

        # Build chapter -> files mapping
        file_to_chapter = build_chapter_file_map(classified, spine_files)

        # Read CSS for class detection
        css_content = ""
        for css_file in Path(opf_dir).rglob("*.css"):
            with open(css_file) as f:
                css_content += f.read()

        heading_classes = detect_heading_classes(css_content)
        sup_classes = detect_superscript_classes(css_content)

        # Copy images
        img_dest = os.path.join(output_dir, img_dir_name)
        img_src_dirs = list(Path(opf_dir).rglob("*.jpg")) + list(Path(opf_dir).rglob("*.png")) + list(Path(opf_dir).rglob("*.gif")) + list(Path(opf_dir).rglob("*.svg"))
        if img_src_dirs:
            os.makedirs(img_dest, exist_ok=True)
            for img_file in img_src_dirs:
                dest = os.path.join(img_dest, img_file.name)
                if not os.path.exists(dest):
                    shutil.copy2(str(img_file), dest)
            print(f"Images extracted: {len(img_src_dirs)} -> {img_dir_name}/")

        # Calculate footnote offsets per chapter
        numbered_chapters = get_numbered_chapters(classified)
        chapters_with_content = [ch["label"] for ch in numbered_chapters]

        # Count footnotes per notes file
        notes_file_chapters = []
        for nf in sorted(notes_files):
            fpath = os.path.join(opf_dir, nf)
            if not os.path.exists(fpath):
                continue
            count = count_footnotes_in_file(fpath)
            if count > 0:
                notes_file_chapters.append((nf, count))

        # Determine if notes are split across files (one per chapter)
        # or in a single file with chapter headings
        chapter_offsets = {}
        if len(notes_file_chapters) > 1:
            # Multiple notes files: one per chapter (Calibre pattern)
            offset = 0
            for i, ch_label in enumerate(chapters_with_content):
                chapter_offsets[ch_label] = offset
                if i < len(notes_file_chapters):
                    offset += notes_file_chapters[i][1]
        elif len(notes_file_chapters) == 1:
            # Single notes file: count per-chapter footnotes by parsing headings
            nf_path = os.path.join(opf_dir, notes_file_chapters[0][0])
            chapter_counts = count_per_chapter_footnotes(nf_path, chapters_with_content)
            offset = 0
            for ch_label in chapters_with_content:
                chapter_offsets[ch_label] = offset
                offset += chapter_counts.get(ch_label, 0)
        else:
            offset = 0

        print(f"Total footnotes: {offset}")

        # --- Convert content ---
        parts = []
        img_prefix = f"{img_dir_name}/"

        for filename in spine_files:
            filepath = os.path.join(opf_dir, filename)
            if not os.path.exists(filepath):
                continue

            # Skip notes files (we'll generate footnote defs separately)
            if filename in notes_files:
                continue

            # Add TOC heading
            if filename in toc_map:
                label = toc_map[filename]
                label_lower = label.lower().strip()

                if label_lower == "cover":
                    continue

                is_chapter = bool(re.match(r'^(\d+[\.\):]?\s*\S|chapter\s+\d)', label_lower))
                is_back = any(label_lower.startswith(bm) for bm in BACK_MATTER_LABELS)

                if is_chapter or is_back:
                    parts.append(f"\n# {label}\n")
                else:
                    parts.append(f"\n## {label}\n")

            # Determine footnote offset
            chapter = file_to_chapter.get(filename)
            fn_offset = chapter_offsets.get(chapter, 0) if chapter else 0

            # Convert HTML
            with open(filepath, "r", encoding="utf-8") as f:
                html = f.read()
            html = re.sub(r'<\?xml[^>]*\?>', '', html)
            html = re.sub(r'<head>.*?</head>', '', html, flags=re.DOTALL)

            notes_basenames = {os.path.basename(nf) for nf in notes_files}
            converter = ContentConverter(
                fn_offset=fn_offset,
                heading_classes=heading_classes,
                sup_classes=sup_classes,
                notes_filenames=notes_basenames,
            )
            converter.img_dir = img_prefix
            converter.feed(html)
            md = converter.get_markdown()

            if md.strip():
                parts.append(md)

        # --- Extract footnotes ---
        all_footnotes = {}
        if len(notes_file_chapters) > 1:
            # Multiple notes files: one per chapter
            for i, (nf, count) in enumerate(notes_file_chapters):
                if i < len(chapters_with_content):
                    ch_label = chapters_with_content[i]
                    fn_offset = chapter_offsets.get(ch_label, 0)
                else:
                    fn_offset = 0

                fpath = os.path.join(opf_dir, nf)
                with open(fpath, "r", encoding="utf-8") as f:
                    html = f.read()

                parser = NotesParser(fn_offset=fn_offset)
                parser.feed(html)
                fns = parser.finish()
                all_footnotes.update(fns)
        elif len(notes_file_chapters) == 1:
            # Single notes file: need to parse chapter-by-chapter
            nf_path = os.path.join(opf_dir, notes_file_chapters[0][0])
            with open(nf_path, "r", encoding="utf-8") as f:
                html = f.read()
            all_footnotes = extract_notes_single_file(
                html, chapters_with_content, chapter_offsets
            )

        # --- Assemble output ---
        result = "".join(parts)
        result = clean_markdown(result)

        # Add title
        header = f"# {title}\n\n"
        if author:
            header += f"**{author}**\n\n"
        result = header + result

        # Remove empty Notes heading (we regenerate it)
        result = re.sub(r'\n# Notes\s*\n*$', '', result)

        # Append footnote definitions
        if all_footnotes:
            result += "\n\n# Notes\n\n"
            for num in sorted(all_footnotes.keys()):
                result += f"[^{num}]: {all_footnotes[num]}\n\n"

        # Write output
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)

        # --- Report ---
        ref_count = len(re.findall(r'\[\^(\d+)\](?!:)', result))
        def_count = len(re.findall(r'^\[\^\d+\]:', result, re.MULTILINE))
        img_count = len(re.findall(r'!\[\]', result))
        heading_count = len(re.findall(r'^#{1,3} ', result, re.MULTILINE))
        line_count = result.count("\n") + 1

        print(f"\nOutput: {output_path}")
        print(f"  Lines: {line_count}")
        print(f"  Size: {len(result):,} bytes")
        print(f"  Images: {img_count}")
        print(f"  Headings: {heading_count}")
        print(f"  Footnotes: {ref_count} refs, {def_count} definitions")

        # Warn about unmatched footnotes
        refs = set(int(m) for m in re.findall(r'\[\^(\d+)\](?!:)', result))
        defs = set(int(m) for m in re.findall(r'^\[\^(\d+)\]:', result, re.MULTILINE))
        unmatched = refs - defs
        if unmatched:
            print(f"  WARNING: {len(unmatched)} footnote refs without definitions")

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(
        description="Convert EPUB to clean Markdown with images and footnotes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "My Book.epub"              # -> "My Book.md" + "My Book_images/"
  %(prog)s "My Book.epub" -o book.md   # -> "book.md" + "My Book_images/"
        """,
    )
    parser.add_argument("epub", help="Path to the .epub file")
    parser.add_argument("-o", "--output", help="Output .md file path (default: same name as epub)")

    args = parser.parse_args()
    convert_epub(args.epub, args.output)


if __name__ == "__main__":
    main()

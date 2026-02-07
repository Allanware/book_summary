#!/usr/bin/env python3
import json
import re
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE_PATH = ROOT / "tmp" / "translation-cache-zh-codex.json"
CHAPTER_DIR = ROOT / "chapters"

TAG_PATTERN = re.compile(r"<[^>]+>")
LETTER_PATTERN = re.compile(r"[A-Za-z]")

BATCH_CHAR_LIMIT = 8000
PAUSE_SECONDS = 0.2


def load_source_data():
    script = (
        "const book=(await import('./book-data.js')).default;"
        "const {chapters}=await import('./chapters/index.js');"
        "process.stdout.write(JSON.stringify({book,chapters}));"
    )
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def load_cache():
    if not CACHE_PATH.exists():
        return {}
    try:
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_cache(cache):
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def has_translatable_text(value):
    return isinstance(value, str) and LETTER_PATTERN.search(value)


def push_if_string(bucket, value):
    if has_translatable_text(value):
        bucket.append(value)


def collect_book_strings(book):
    strings = []

    push_if_string(strings, book.get("title"))
    push_if_string(strings, book.get("coreArgument"))

    for theme in book.get("themes", []):
        push_if_string(strings, theme.get("label"))
        push_if_string(strings, theme.get("description"))
        push_if_string(strings, theme.get("definition"))

        for application in theme.get("applications", []):
            push_if_string(strings, application.get("setting"))
            push_if_string(strings, application.get("time"))
            push_if_string(strings, application.get("point"))
            for item in application.get("evidence", []):
                push_if_string(strings, item)

    for step in book.get("flow", []):
        push_if_string(strings, step.get("title"))
        push_if_string(strings, step.get("summary"))
        push_if_string(strings, step.get("mechanism"))
        push_if_string(strings, step.get("period"))

        for link in step.get("thesisLinks", []):
            push_if_string(strings, link.get("point"))
            for item in link.get("evidence", []):
                push_if_string(strings, item)

    return strings


def collect_chapter_strings(chapter):
    strings = []

    push_if_string(strings, chapter.get("title"))
    push_if_string(strings, chapter.get("thesis"))
    push_if_string(strings, chapter.get("argument"))

    for item in chapter.get("evidence", []):
        push_if_string(strings, item)

    for section in chapter.get("flowSections", []):
        push_if_string(strings, section.get("title"))
        push_if_string(strings, section.get("note"))

        for step in section.get("steps", []):
            push_if_string(strings, step.get("point"))
            for item in step.get("evidence", []):
                push_if_string(strings, item)

    for step in chapter.get("flow", []):
        push_if_string(strings, step.get("point"))
        for item in step.get("evidence", []):
            push_if_string(strings, item)

    return strings


def mask_tags(text):
    tags = []

    def replacer(match):
        token = f"¤¤TAG_{len(tags)}¤¤"
        tags.append((token, match.group(0)))
        return token

    masked = TAG_PATTERN.sub(replacer, text)
    return masked, tags


def restore_tags(text, tags):
    output = text
    for token, tag in tags:
        output = output.replace(token, tag)
    return output


def chunk_records(records, char_limit):
    batches = []
    current = []
    total = 0

    for record in records:
        size = len(record["masked"])
        if current and total + size > char_limit:
            batches.append(current)
            current = []
            total = 0

        current.append(record)
        total += size

    if current:
        batches.append(current)

    return batches


def build_prompt(masked_texts):
    input_json = json.dumps(masked_texts, ensure_ascii=False)
    return (
        "Translate the following English strings into fluent, natural Simplified Chinese.\n"
        "Rules:\n"
        "- Return JSON only with key \"translations\".\n"
        "- Keep item order exactly the same.\n"
        "- Keep placeholder tokens like ¤¤TAG_0¤¤ unchanged.\n"
        "- Preserve page citations like (p. 34), numerals, and punctuation semantics.\n"
        "- Keep any HTML markup exactly unchanged when present.\n"
        "- Do not add or remove facts.\n\n"
        "Input JSON:\n"
        f"{input_json}\n"
    )


def call_codex_translate(masked_texts):
    schema = {
        "type": "object",
        "properties": {
            "translations": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": len(masked_texts),
                "maxItems": len(masked_texts),
            }
        },
        "required": ["translations"],
        "additionalProperties": False,
    }

    prompt = build_prompt(masked_texts)

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as sf:
        sf.write(json.dumps(schema, ensure_ascii=False))
        schema_path = Path(sf.name)

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as of:
        out_path = Path(of.name)

    cmd = [
        "codex",
        "exec",
        "-m",
        "gpt-5.2",
        "-c",
        "model_reasoning_effort=\"low\"",
        "--ephemeral",
        "--sandbox",
        "read-only",
        "--output-schema",
        str(schema_path),
        "--output-last-message",
        str(out_path),
        "-",
    ]

    try:
        result = subprocess.run(
            cmd,
            input=prompt,
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=120,
        )

        if result.returncode != 0:
            raise RuntimeError(f"codex exec failed ({result.returncode})")

        raw = out_path.read_text(encoding="utf-8").strip()
        payload = json.loads(raw)
        translations = payload.get("translations")
        if not isinstance(translations, list) or len(translations) != len(masked_texts):
            raise RuntimeError("Invalid translation payload")
        if not all(isinstance(item, str) for item in translations):
            raise RuntimeError("Translation payload contains non-string items")

        return translations
    finally:
        try:
            schema_path.unlink(missing_ok=True)
        except Exception:
            pass
        try:
            out_path.unlink(missing_ok=True)
        except Exception:
            pass


def build_translation_map(strings, cache):
    translation_map = {}

    for value in strings:
        cached = cache.get(value)
        if isinstance(cached, str) and cached:
            translation_map[value] = cached

    missing = [value for value in strings if value not in translation_map]
    if not missing:
        return translation_map

    records = []
    for source in missing:
        masked, tags = mask_tags(source)
        records.append({"source": source, "masked": masked, "tags": tags})

    batches = chunk_records(records, BATCH_CHAR_LIMIT)
    print(f"Translating {len(missing)} new strings with gpt-5.2 in {len(batches)} batches...")

    for idx, batch in enumerate(batches, start=1):
        masked_items = [item["masked"] for item in batch]
        translated_items = None

        for attempt in range(3):
            try:
                translated_items = call_codex_translate(masked_items)
                break
            except Exception:
                if attempt == 2:
                    translated_items = None
                else:
                    time.sleep(1.2 * (attempt + 1))

        if translated_items is None:
            translated_items = []
            for item in batch:
                try:
                    one = call_codex_translate([item["masked"]])[0]
                except Exception:
                    one = item["source"]
                translated_items.append(one)
                time.sleep(0.2)

        for item, translated in zip(batch, translated_items):
            restored = restore_tags(translated, item["tags"])
            translation_map[item["source"]] = restored
            cache[item["source"]] = restored

        if idx % 2 == 0 or idx == len(batches):
            save_cache(cache)

        print(f"Batch {idx}/{len(batches)} complete")
        time.sleep(PAUSE_SECONDS)

    return translation_map


def make_translator(translation_map):
    def t(value):
        if not has_translatable_text(value):
            return value
        return translation_map.get(value, value)

    return t


def translate_book(book, t):
    return {
        "title": t(book.get("title")),
        "coreArgument": t(book.get("coreArgument")),
        "themes": [
            {
                "id": theme.get("id"),
                "label": t(theme.get("label")),
                "description": t(theme.get("description")),
                "definition": t(theme.get("definition")),
                "group": theme.get("group"),
                "aliases": list(theme.get("aliases", [])),
                "applications": [
                    {
                        "chapter": app.get("chapter"),
                        "setting": t(app.get("setting")),
                        "time": t(app.get("time")),
                        "point": t(app.get("point")),
                        "evidence": [t(item) for item in app.get("evidence", [])],
                    }
                    for app in theme.get("applications", [])
                ],
            }
            for theme in book.get("themes", [])
        ],
        "flow": [
            {
                "id": step.get("id"),
                "title": t(step.get("title")),
                "summary": t(step.get("summary")),
                "mechanism": t(step.get("mechanism")),
                "period": t(step.get("period")),
                "chapters": list(step.get("chapters", [])),
                "themes": list(step.get("themes", [])),
                "thesisLinks": [
                    {
                        "chapter": link.get("chapter"),
                        "point": t(link.get("point")),
                        "evidence": [t(item) for item in link.get("evidence", [])],
                    }
                    for link in step.get("thesisLinks", [])
                ],
            }
            for step in book.get("flow", [])
        ],
    }


def translate_chapter(chapter, t):
    translated = {
        "id": chapter.get("id"),
        "title": t(chapter.get("title")),
        "pages": chapter.get("pages"),
        "themes": list(chapter.get("themes", [])),
    }

    thesis = chapter.get("thesis")
    if thesis:
        translated["thesis"] = t(thesis)

    flow_sections = chapter.get("flowSections") or []
    if flow_sections:
        translated["flowSections"] = [
            {
                "title": t(section.get("title")),
                "note": t(section.get("note")),
                "steps": [
                    {
                        "point": t(step.get("point")),
                        "evidence": [t(item) for item in step.get("evidence", [])],
                    }
                    for step in section.get("steps", [])
                ],
            }
            for section in flow_sections
        ]

    flow = chapter.get("flow") or []
    if flow:
        translated["flow"] = [
            {
                "point": t(step.get("point")),
                "evidence": [t(item) for item in step.get("evidence", [])],
            }
            for step in flow
        ]

    argument = chapter.get("argument")
    if argument:
        translated["argument"] = t(argument)

    evidence = chapter.get("evidence") or []
    if evidence:
        translated["evidence"] = [t(item) for item in evidence]

    return translated


def write_js_modules(book, chapters):
    book_content = (
        "const BOOK_DATA = "
        + json.dumps(book, ensure_ascii=False, indent=2)
        + ";\n\nexport default BOOK_DATA;\n"
    )
    (ROOT / "book-data.zh.js").write_text(book_content, encoding="utf-8")

    imports = []
    refs = []
    for chapter in chapters:
        chapter_id = str(chapter["id"]).zfill(2)
        filename = f"chapter-{chapter_id}.zh.js"
        var_name = f"chapter{chapter_id}"
        file_path = CHAPTER_DIR / filename
        file_path.write_text(
            "export default " + json.dumps(chapter, ensure_ascii=False, indent=2) + ";\n",
            encoding="utf-8",
        )

        imports.append(f'import {var_name} from "./{filename}";')
        refs.append(var_name)

    index_lines = imports + ["", "export const chapters = [", "  " + ",\n  ".join(refs), "];", ""]
    (CHAPTER_DIR / "index.zh.js").write_text("\n".join(index_lines), encoding="utf-8")


def main():
    source = load_source_data()
    book = source["book"]
    chapters = source["chapters"]

    book_strings = collect_book_strings(book)
    chapter_strings = []
    for chapter in chapters:
        chapter_strings.extend(collect_chapter_strings(chapter))

    unique_strings = sorted(set(book_strings + chapter_strings))
    print(f"Discovered {len(unique_strings)} unique translatable strings.")

    cache = load_cache()
    translation_map = build_translation_map(unique_strings, cache)
    translator = make_translator(translation_map)

    translated_book = translate_book(book, translator)
    translated_chapters = [translate_chapter(chapter, translator) for chapter in chapters]

    write_js_modules(translated_book, translated_chapters)
    save_cache(cache)

    print("Generated Chinese data modules with gpt-5.2 successfully.")


if __name__ == "__main__":
    main()

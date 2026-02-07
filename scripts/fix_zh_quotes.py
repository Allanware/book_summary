#!/usr/bin/env python3
"""Escape inner double-quotes in a single chapter .zh.js file."""
import re
import sys
from pathlib import Path


def escape_value_quotes(content: str) -> str:
    """
    In JS object literal, escape every " that lies inside a string value.
    We detect value start by ": " and then escape any " not followed by \s*[,}\]).
    """
    out = []
    i = 0
    n = len(content)
    in_double_quoted_value = False

    while i < n:
        if content[i : i + 2] == '\\"':
            out.append(content[i : i + 2])
            i += 2
            continue
        if content[i] == '\\' and i + 1 < n:
            out.append(content[i : i + 2])
            i += 2
            continue
        if content[i] == '"':
            if not in_double_quoted_value:
                # Check if this opens a value: look for ": " or ": [" before this (may have newline + indent)
                back = "".join(out)[-200:]
                if re.search(r'":\s*$', back) or re.search(r'":\s*\[\s*$', back):
                    in_double_quoted_value = True
                out.append('"')
                i += 1
                continue
            # We're in a value. Is this the closing "?
            j = i + 1
            while j < n and content[j] in ' \t':
                j += 1
            if j >= n:
                in_double_quoted_value = False
                out.append('"')
                i += 1
                continue
            if content[j] in ',}])\n\r':
                in_double_quoted_value = False
                out.append('"')
                i += 1
                continue
            # Inner quote - escape it
            out.append('\\"')
            i += 1
            continue
        # When we see : outside value, we might be about to start a value
        if content[i] == ':' and not in_double_quoted_value:
            out.append(content[i])
            i += 1
            continue
        # End of value on newline without comma (next line has key)
        if content[i] in '\n\r' and in_double_quoted_value:
            # Peek: next non-empty line might start with "key"
            rest = content[i + 1 :].lstrip()
            if rest.startswith('"'):
                in_double_quoted_value = False
        out.append(content[i])
        i += 1

    return "".join(out)


def main():
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "").resolve()
    if not path.is_file():
        print("Usage: fix_zh_quotes.py <path to chapter-10.zh.js>", file=sys.stderr)
        sys.exit(1)
    s = path.read_text(encoding="utf-8")
    new_s = escape_value_quotes(s)
    if new_s != s:
        path.write_text(new_s, encoding="utf-8")
        print(f"Updated {path}")
    else:
        print("No changes")


if __name__ == "__main__":
    main()

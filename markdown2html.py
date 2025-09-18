#!/usr/bin/env python3
"""
markdown2html.py
Convert Markdown into HTML with simplified rules.
"""

import sys
import os
import hashlib
import re


def apply_inline_formatting(text: str) -> str:
    """Apply inline replacements: bold, italic, MD5, remove 'c'/'C'."""
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"__(.+?)__", r"<em>\1</em>", text)
    text = re.sub(r"\[\[(.+?)\]\]", lambda m: hashlib.md5(m.group(1).encode()).hexdigest(), text)
    text = re.sub(r"\(\((.+?)\)\)", lambda m: re.sub(r"[cC]", "", m.group(1)), text)
    return text


def convert_markdown(lines):
    """Convert Markdown lines to HTML lines."""
    html_lines = []
    in_ul = False
    in_ol = False
    in_p = False

    for line in lines:
        line = line.rstrip("\n")

        match = re.match(r"^(#{1,6}) (.*)", line)
        if match:
            level = len(match.group(1))
            content = apply_inline_formatting(match.group(2).strip())
            html_lines.append(f"<h{level}>{content}</h{level}>")
            continue

        if line.startswith("- "):
            if not in_ul:
                html_lines.append("<ul>")
                in_ul = True
            content = apply_inline_formatting(line[2:].strip())
            html_lines.append(f"<li>{content}</li>")
            continue
        elif in_ul:
            html_lines.append("</ul>")
            in_ul = False

        if line.startswith("* "):
            if not in_ol:
                html_lines.append("<ol>")
                in_ol = True
            content = apply_inline_formatting(line[2:].strip())
            html_lines.append(f"<li>{content}</li>")
            continue
        elif in_ol:
            html_lines.append("</ol>")
            in_ol = False

        if line.strip() == "":
            if in_p:
                html_lines.append("</p>")
                in_p = False
            continue
        else:
            if not in_p:
                html_lines.append("<p>")
                in_p = True
            content = apply_inline_formatting(line.strip())
            if html_lines[-1] != "<p>":
                html_lines.append("<br/>")
            html_lines.append(content)

    if in_ul:
        html_lines.append("</ul>")
    if in_ol:
        html_lines.append("</ol>")
    if in_p:
        html_lines.append("</p>")

    return html_lines


def main():
    if len(sys.argv) < 3:
        sys.stderr.write("Usage: ./markdown2html.py README.md README.html\n")
        sys.exit(1)

    md_file = sys.argv[1]
    out_file = sys.argv[2]

    if not os.path.isfile(md_file):
        sys.stderr.write(f"Missing {md_file}\n")
        sys.exit(1)

    with open(md_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    html_lines = convert_markdown(lines)

    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))

    sys.exit(0)


if __name__ == "__main__":
    main()

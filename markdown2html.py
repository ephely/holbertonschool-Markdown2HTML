#!/usr/bin/python3
"""
markdown2html.py
Convert Markdown into HTML with simplified rules.
"""

import sys
import os
import re
import hashlib


def parse_bold_emphasis(text):
    """
    Apply inline replacements: bold, italic, MD5, remove 'c'/'C'.
    """
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__', r'<em>\1</em>', text)
    return text


def parse_special_syntax(text):
    """
    Fix special syntax
    """
    def md5_replace(match):
        """Replace [[...]] with its MD5 hash."""
        content = match.group(1)
        md5_hash = hashlib.md5(content.encode()).hexdigest()
        return md5_hash

    def remove_c(match):
        """Remove 'c' and 'C' characters inside ((...))."""
        content = match.group(1)
        return re.sub(r'[cC]', '', content)

    text = re.sub(r'\[\[(.+?)\]\]', md5_replace, text)
    text = re.sub(r'\(\((.+?)\)\)', remove_c, text)
    return text


def process_line_formatting(text):
    """
    Apply all inline formatting rules to a line of text.
    """
    text = parse_special_syntax(text)
    text = parse_bold_emphasis(text)
    return text


def markdown_to_html(input_file, output_file):
    """
    Convert a Markdown file into an HTML file.
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    html_lines = []
    i = 0

    while i < len(lines):
        line = lines[i].rstrip('\n')

        if line.startswith('#'):
            match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if match:
                level = len(match.group(1))
                content = process_line_formatting(match.group(2))
                html_lines.append(f'<h{level}>{content}</h{level}>')
            i += 1

        elif line.startswith('- '):
            ul_items = []
            while i < len(lines) and lines[i].startswith('- '):
                item_content = process_line_formatting(
                    lines[i][2:].rstrip('\n')
                )
                ul_items.append(f'<li>{item_content}</li>')
                i += 1
            if ul_items:
                html_lines.append('<ul>')
                html_lines.extend(ul_items)
                html_lines.append('</ul>')

        elif line.startswith('* '):
            ol_items = []
            while i < len(lines) and lines[i].startswith('* '):
                item_content = process_line_formatting(
                    lines[i][2:].rstrip('\n')
                )
                ol_items.append(f'<li>{item_content}</li>')
                i += 1
            if ol_items:
                html_lines.append('<ol>')
                html_lines.extend(ol_items)
                html_lines.append('</ol>')

        elif line.strip():
            paragraph_lines = []
            while (
                i < len(lines)
                and lines[i].strip()
                and not lines[i].startswith('#')
                and not lines[i].startswith('- ')
                and not lines[i].startswith('* ')
            ):
                paragraph_lines.append(lines[i].rstrip('\n'))
                i += 1

            if paragraph_lines:
                html_lines.append('<p>')
                for j, p_line in enumerate(paragraph_lines):
                    formatted_line = process_line_formatting(p_line)
                    if j < len(paragraph_lines) - 1:
                        html_lines.append(formatted_line)
                        html_lines.append('<br/>')
                    else:
                        html_lines.append(formatted_line)
                html_lines.append('</p>')
        else:
            i += 1

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_lines) + '\n')


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "Usage: ./markdown2html.py README.md README.html",
            file=sys.stderr
        )
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if not os.path.exists(input_file):
        print(f"Missing {input_file}", file=sys.stderr)
        sys.exit(1)

    markdown_to_html(input_file, output_file)
    sys.exit(0)

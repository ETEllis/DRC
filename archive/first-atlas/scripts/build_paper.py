#!/usr/bin/env python3
"""Build the publication HTML and PDF from the canonical Markdown manuscript."""
from __future__ import annotations

import re
from pathlib import Path

from markdown_it import MarkdownIt
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "manuscript" / "manuscript.md"
HTML = ROOT / "docs" / "paper.html"
PDF = ROOT / "output" / "pdf" / "drc-regulatory-coupling-v0.1.pdf"
SITE_PDF = ROOT / "docs" / "drc-regulatory-coupling-v0.1.pdf"


def slug(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text).lower()
    text = re.sub(r"^\d+\.\s*", "", text)
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    return re.sub(r"\s+", "-", text.strip())


def main() -> None:
    md = MarkdownIt("commonmark", {"html": False}).enable("table")
    body = md.render(SOURCE.read_text(encoding="utf-8"))

    def add_id(match: re.Match[str]) -> str:
        level, contents = match.groups()
        return f'<h{level} id="{slug(contents)}">{contents}</h{level}>'

    body = re.sub(r"<h([1-6])>(.*?)</h\1>", add_id, body)
    body = body.replace('href="../docs/data/', 'href="data/')
    html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Publication manuscript for the DRC developmental regulatory coupling research program.">
<title>Regulatory coupling across development and technological change — E. T. Ellis</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600&family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="paper.css"></head><body>
<header class="paper-nav"><a href="index.html">← DRC atlas</a><span>PUBLICATION MANUSCRIPT · v0.1</span><a href="drc-regulatory-coupling-v0.1.pdf">Download PDF ↓</a></header>
<main class="paper-shell"><aside class="rail"><span>CONTENTS</span><a href="#abstract">Abstract</a><a href="#scope-and-claim-grammar">Claim grammar</a><a href="#the-bounded-molecular-and-developmental-starting-points">Starting points</a><a href="#a-time-indexed-causal-model">Causal model</a><a href="#contrary-evidence-and-boundaries-that-change-the-conclusion">Contrary evidence</a><a href="#minimum-discriminating-studies">Studies</a><a href="#references">References</a></aside><article class="paper-body">{body}</article></main>
<footer class="paper-footer">E. T. Ellis · DRC · 25 September 2026</footer></body></html>'''
    HTML.write_text(html, encoding="utf-8")
    PDF.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900}, device_scale_factor=1)
        page.goto(HTML.as_uri(), wait_until="networkidle")
        page.emulate_media(media="print")
        page.pdf(path=str(PDF), format="Letter", print_background=True, display_header_footer=True,
                 header_template="<span></span>",
                 footer_template="<div style='width:100%;font:8px Arial;color:#68776c;text-align:center'>E. T. ELLIS  ·  DRC  /  <span class='pageNumber'></span></div>",
                 margin={"top": "0.65in", "bottom": "0.65in", "left": "0.75in", "right": "0.75in"})
        browser.close()
    SITE_PDF.write_bytes(PDF.read_bytes())
    print(f"Built {HTML.relative_to(ROOT)} and {PDF.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

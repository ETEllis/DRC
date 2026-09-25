#!/usr/bin/env python3
"""Validate the unified static research artifact using only Python's standard library."""
from __future__ import annotations

import hashlib
import json
import re
import zipfile
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
read = lambda name: json.loads((DATA / name).read_text(encoding='utf-8'))
claims = read('evidence.json')
refs = read('citations.json')
mechanisms = read('mechanisms.json')
predictions = read('predictions.json')
config = read('config.json')
claim_ids = [c['id'] for c in claims]
ref_ids = [r['id'] for r in refs]
layer_ids = [l['id'] for l in mechanisms['layers']]
assert len(claim_ids) == len(set(claim_ids)), 'duplicate claim ID'
assert len(ref_ids) == len(set(ref_ids)), 'duplicate reference ID'
assert len(layer_ids) == len(set(layer_ids)), 'duplicate layer ID'
assert config['repository_url'] == 'https://github.com/ETEllis/DRC'

for claim in claims:
    assert claim['status'] in {'established', 'supported', 'proposed', 'horizon'}, claim['id']
    assert claim['grade'] in {'E0','E1','E2','E3','E4','E5'}, claim['id']
    assert claim['citations'] and set(claim['citations']) <= set(ref_ids), claim['id']
    assert all(claim.get(key) for key in ('scope','mechanism','uncertainty','falsifier','rival')), claim['id']
for source in refs:
    url = source['url']
    if url.startswith(('https://','http://')):
        assert url.startswith('https://'), source['id']
    else:
        assert (ROOT / url).is_file(), source['id']
for layer in mechanisms['layers']:
    assert set(layer['claims']) <= set(claim_ids), layer['id']
for edge in mechanisms['edges']:
    assert edge['from'] in layer_ids and edge['to'] in layer_ids, edge
    assert edge['claim'] in claim_ids, edge
for prediction in predictions:
    assert prediction['study'] in {'A','B','C','D'}
    assert prediction['title'] and prediction['falsifier']
assert next(c for c in claims if c['id']=='C09')['status']=='proposed'
assert next(c for c in claims if c['id']=='C09')['grade']=='E0'

for manifest in (ROOT/'sources/SHA256SUMS', ROOT/'sources/received/SHA256SUMS'):
    for line in manifest.read_text().splitlines():
        digest, name = line.split('  ', 1)
        file = ROOT / name
        assert file.is_file(), name
        assert hashlib.sha256(file.read_bytes()).hexdigest() == digest, name
with zipfile.ZipFile(ROOT/'sources/received/research-source.zip') as archive:
    for name in ('papers/perinatal-extension-source.md','papers/rccx-hunter-dabrowski-v3.2.pdf','papers/polymathic-singularity-v0.1.pdf'):
        assert archive.read(name) == (ROOT/name).read_bytes(), name

paper = (ROOT/'papers/integrated-paper.md').read_text(encoding='utf-8')
assert all(f'[{ref}]' in paper for ref in ref_ids if ref[0].isdigit()), 'bibliography not generated'
assert (ROOT/'papers/integrated-paper.pdf').read_bytes().startswith(b'%PDF-')
latex = (ROOT/'papers/latex/main.tex').read_text(encoding='utf-8')
assert r'\documentclass[10pt,letterpaper,twocolumn]' in latex
assert r'\begin{center}\normalsize\sffamily\bfseries Abstract\end{center}' in latex
assert 'disgust sensitivity' in paper.lower()
assert 'disgust sensitivity' in (ROOT/'papers/latex/sections/03-perinatal.tex').read_text().lower()
assert (ROOT/'papers/latex/references.tex').read_text().count(r'\bibitem{') == len(refs)
assert (ROOT/'papers/latex/claim-ledger.tex').read_text().count(r'\subsection*{C') == len(claims)
assert len((ROOT/'papers/integrated-paper.pdf').read_bytes()) > 100_000

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=[]; self.hrefs=[]; self.assets=[]
    def handle_starttag(self, tag, pairs):
        attr=dict(pairs)
        if 'id' in attr: self.ids.append(attr['id'])
        if tag=='a' and 'href' in attr: self.hrefs.append(attr['href'])
        if tag in {'script','link','img'}:
            for key in ('src','href'):
                if key in attr: self.assets.append(attr[key])
page=Page();page.feed((ROOT/'index.html').read_text(encoding='utf-8'))
assert len(page.ids)==len(set(page.ids)), 'duplicate HTML ID'
for href in page.hrefs:
    if href.startswith('#'): assert href[1:] in page.ids, href
    elif href and not href.startswith(('https:','http:','data:','mailto:')):
        local = href.split('#', 1)[0].split('?', 1)[0]
        assert (ROOT/local).is_file(), href
for path in page.assets:
    if path.startswith(('http:','https:','data:','#')):continue
    assert (ROOT/path).is_file(), path
for anchor in ('atlas','mechanisms','social','channel','recursion','closure','alternatives','predictions','experiments','ledger','downloads','manuscript','bibliography'):
    assert anchor in page.ids, anchor
assert (ROOT/'src/light.css').is_file()
print(f"Validated {len(claims)} claims, {len(refs)} references, {len(predictions)} predictions, {len(layer_ids)} layers, source hashes, root links, two-column LaTeX/PDF, and {len(page.ids)} unique HTML IDs.")

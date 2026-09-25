#!/usr/bin/env python3
"""Check the source-linked research artifact without third-party dependencies."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
model = json.loads((ROOT / "docs/data/model.json").read_text())
sources = json.loads((ROOT / "docs/data/sources.json").read_text())
source_ids = {source["id"] for source in sources}
node_ids = {node["id"] for node in model["nodes"]}
assert len(source_ids) == len(sources), "Duplicate source ID"
assert len(node_ids) == len(model["nodes"]), "Duplicate node ID"
assert len({edge["id"] for edge in model["edges"]}) == len(model["edges"]), "Duplicate edge ID"
for source in sources:
    assert source["url"].startswith("https://"), source["id"]
    assert source["supports"], source["id"]
for edge in model["edges"]:
    assert edge["from"] in node_ids and edge["to"] in node_ids, edge["id"]
    assert edge["grade"] in model["grades"], edge["id"]
    assert edge["status"] in model["statuses"], edge["id"]
    assert edge["sources"] and set(edge["sources"]) <= source_ids, edge["id"]
    assert edge["boundary"] and edge["rival"], edge["id"]

manuscript = (ROOT / "manuscript/manuscript.md").read_text()
cited = set(re.findall(r"\[S\d{2}\]", manuscript))
assert cited == {f"[{id}]" for id in source_ids}, "Manuscript and source ledger differ"

for line in (ROOT / "sources/SHA256SUMS").read_text().splitlines():
    digest, name = line.split("  ", 1)
    path = ROOT / name
    assert path.is_file(), name
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, name

for relative in ["docs/index.html", "docs/app.js", "docs/paper.html", "docs/drc-regulatory-coupling-v0.1.pdf", "docs/.nojekyll"]:
    assert (ROOT / relative).is_file(), relative
assert (ROOT / "docs/SHA256SUMS").read_bytes() == (ROOT / "sources/SHA256SUMS").read_bytes()
print(f"Validated {len(model['nodes'])} nodes, {len(model['edges'])} edges, {len(sources)} sources, source hashes, and generated artifacts.")

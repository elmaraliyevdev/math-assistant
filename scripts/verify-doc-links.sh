#!/usr/bin/env bash
# Verify internal markdown links in docs/ resolve to existing files.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

python3 - "$ROOT" <<'PY'
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
docs = root / "docs"
fail = 0
pattern = re.compile(r"\[[^\]]*\]\(([^)]+)\)")

for path in sorted(docs.rglob("*.md")):
    text = path.read_text(encoding="utf-8")
    for match in pattern.finditer(text):
        link = match.group(1).strip()
        if not link or link.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = link.split("#", 1)[0]
        if not target:
            continue
        resolved = (path.parent / target).resolve()
        if not resolved.exists():
            rel = path.relative_to(root)
            print(f"BROKEN: {rel} -> {link}")
            fail = 1

if fail:
    sys.exit(1)
print("All docs/ internal links OK")
PY

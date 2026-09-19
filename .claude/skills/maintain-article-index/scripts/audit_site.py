#!/usr/bin/env python3
"""Audit the repo for anything that breaks when served as a GitHub Pages site.

The site is served from a subpath (https://<user>.github.io/Articles/ for the
project-page form, or / for a custom domain), so any URL that assumes it sits at
the server root will 404. This checks for those, plus the other hazards that
only surface once the files are served over HTTP instead of opened via file://.

Usage:
    python3 audit_site.py            # report
    python3 audit_site.py --strict   # exit 1 on any finding
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

def find_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "index.html").is_file() or (p / ".git").exists():
            return p
    return start


ROOT = find_root(Path(__file__).resolve().parent)
PAGES = sorted(ROOT.glob("index.html")) + sorted(ROOT.glob("*/*.zh-Hant.html"))

# Paths that only resolve if the site is served from the domain root.
ROOT_RELATIVE = re.compile(r'(?:href|src)\s*=\s*"(/[^/"][^"]*)"')
# Jekyll would try to interpret these when rendering the site.
LIQUID = re.compile(r"\{\{|\{%")
# Absolute local filesystem paths that would leak the author's machine.
LOCAL_PATH = re.compile(r'"/Users/|"file://|C:\\\\')


def audit() -> list[tuple[str, str, str]]:
    findings: list[tuple[str, str, str]] = []

    for f in PAGES:
        rel = f.relative_to(ROOT)
        text = f.read_text(encoding="utf-8")
        where = lambda m: f"{rel}:{text.count(chr(10), 0, m.start()) + 1}"
        for m in ROOT_RELATIVE.finditer(text):
            findings.append(
                ("high", where(m), f'root-relative URL {m.group(1)!r} — 404s under a Pages subpath')
            )
        for m in LIQUID.finditer(text):
            findings.append(
                ("high", where(m), f"Liquid syntax {m.group(0)!r} — Jekyll will try to render it")
            )
        for m in LOCAL_PATH.finditer(text):
            findings.append(("medium", where(m), f"local filesystem path {m.group(0)!r}"))

        # Every relative href/src must resolve on disk.
        for m in re.finditer(r'(?:href|src)\s*=\s*"([^"]+)"', text):
            url = m.group(1)
            if url.startswith(("http://", "https://", "mailto:", "#", "data:")):
                continue
            path = url.split("#")[0].split("?")[0]
            if not path:
                continue  # pure fragment (e.g. href="#section")
            target = (f.parent / path).resolve()
            if not target.exists():
                findings.append(
                    ("high", where(m), f"broken relative link {url!r} — no such file")
                )

        # A page that will be served must carry a charset and a viewport.
        if not re.search(r'<meta\s+charset=', text):
            findings.append(("medium", str(rel), "no <meta charset>"))
        if not re.search(r'name="viewport"', text):
            findings.append(("medium", str(rel), "no viewport meta — will not scale on mobile"))
        if "assets/" in text and not (f.parent / "assets").is_dir():
            findings.append(("high", str(rel), "references assets/ but no assets/ directory"))

    # .nojekyll stops GitHub Pages from running the files through Jekyll.
    if not (ROOT / ".nojekyll").exists():
        findings.append(
            ("medium", ".nojekyll", "missing — GitHub Pages will run Jekyll (files starting with _ are skipped)")
        )

    return findings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    findings = audit()
    for sev, where, what in findings:
        print(f"{sev:6} {where}: {what}")

    counts = {s: sum(1 for f in findings if f[0] == s) for s in ("high", "medium")}
    print(f"\n{len(findings)} findings (high: {counts['high']}, medium: {counts['medium']})")
    if not findings:
        print("site audit clean")
    return 1 if args.strict and counts["high"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

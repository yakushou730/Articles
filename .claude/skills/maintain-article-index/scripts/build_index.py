#!/usr/bin/env python3
"""Regenerate the <ol id="entries"> block of the article index.

Scans every <slug>/<slug>.zh-Hant.html under the repo root, pulls each page's
title / kicker / description / source URL / source date straight out of the
file, merges in any tags already recorded in index.html, and rewrites the index
entries sorted by add time (newest first).

Usage:
    python3 build_index.py                 # update index.html in place
    python3 build_index.py --dry-run       # print the plan, write nothing
    python3 build_index.py --check         # exit 1 if index.html is stale
    python3 build_index.py --tag slug=a,b  # set tags for one slug (repeatable)

Add time = the article folder's creation time (st_birthtime), falling back to
the mtime of its HTML file. Override with --added slug=YYYY-MM-DDTHH:MM:SS.
"""

from __future__ import annotations

import argparse
import datetime
import html
import os
import re
import sys
from pathlib import Path


def find_root(start: Path) -> Path:
    """Walk up from the script until we find the repo holding index.html."""
    for p in [start, *start.parents]:
        if (p / "index.html").is_file() or (p / ".git").exists():
            return p
    return start


ROOT = find_root(Path(__file__).resolve().parent)
INDEX = ROOT / "index.html"
SKIP_DIRS = {".git", ".claude", "node_modules", "assets"}

# Keyword -> tag, applied only to entries that have no tags yet. These are
# starting suggestions for a freshly added article; review them in the diff.
TAG_RULES = [
    (r"agentic|agent|代理", "代理"),
    (r"workflow|工作流", "工作流"),
    (r"context|memory|脈絡|記憶|AGENTS\.md", "記憶與脈絡"),
    (r"repo\s?map|tree-sitter|retriev|檢索", "程式碼檢索"),
    (r"claude code|amp|cursor|ide|cli|tool|工具", "工具鏈"),
    (r"prompt|提示", "提示工程"),
    (r"test|quality|maintain|review|審查|品質|可維護", "程式碼品質"),
    (r"pattern|architect|架構|模式", "架構模式"),
    (r"loop|automation|自動", "自動化迴路"),
    (r"oversight|supervis|human|人為", "人為監督"),
]

TAG_ORDER = [
    "Addy Osmani", "Martin Fowler", "Anthropic", "Claude Code", "aider",
    "Simon Willison", "代理", "工作流", "記憶與脈絡", "工具鏈", "提示工程",
    "程式碼品質", "架構模式", "自動化迴路", "程式碼檢索", "實務技巧", "人為監督",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def grab(pattern: str, text: str, default: str = "") -> str:
    m = re.search(pattern, text, re.S)
    return html.unescape(m.group(1)).strip() if m else default


def article_files() -> list[Path]:
    found = []
    for slug_dir in sorted(ROOT.iterdir()):
        if not slug_dir.is_dir() or slug_dir.name.startswith("."):
            continue
        if slug_dir.name in SKIP_DIRS:
            continue
        for f in sorted(slug_dir.glob("*.zh-Hant.html")):
            found.append(f)
    return found


def added_time(f: Path) -> str:
    st = os.stat(f.parent)
    ts = getattr(st, "st_birthtime", None) or st.st_mtime
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%dT%H:%M:%S")


def declared_tags(text: str) -> list[str]:
    """Tags the article declares for itself, via <meta name="tags" content="a,b">.

    This is the source of truth when present: editing the article updates the
    index, instead of the index guessing from keywords.
    """
    raw = grab(r'<meta\s+name="tags"\s+content="([^"]*)"', text)
    return [t.strip() for t in raw.split(",") if t.strip()]


def suggest_tags(slug: str, title: str, desc: str, kicker: str) -> list[str]:
    hay = f"{slug} {title} {desc} {kicker}".lower()
    out = []
    for pat, tag in TAG_RULES:
        if re.search(pat, hay, re.I) and tag not in out:
            out.append(tag)
    return out


KICKERS_AS_TAGS = {
    "addyosmani.com": "Addy Osmani",
    "engineering at anthropic": "Anthropic",
    "claude code 文件": "Claude Code",
    "exploring gen ai": "Martin Fowler",
}


def fallback_tag(kicker: str) -> str:
    """A source-based tag so no new entry lands completely untagged."""
    return KICKERS_AS_TAGS.get(kicker.strip().lower(), kicker.strip())


def existing_entries(text: str) -> dict[str, dict]:
    """slug -> {tags, added} from the current index, so hand edits survive."""
    out = {}
    for block in re.findall(
        r'<li data-added="([^"]*)" data-tags="([^"]*)">(.*?)</li>', text, re.S
    ):
        added, tags, body = block
        href = grab(r'<a href="([^"]+)"', body)
        if not href:
            continue
        slug = href.split("/")[0]
        out[slug] = {"added": added, "tags": [t for t in tags.split("|") if t]}
    return out


def collect(existing: dict, overrides: dict, added_overrides: dict) -> list[dict]:
    rows = []
    for f in article_files():
        slug = f.parent.name
        text = read_text(f)
        title = grab(r"<h1[^>]*>(.*?)</h1>", text)
        kicker = grab(r'<p class="kicker">(.*?)</p>', text)
        pubdate = grab(r'<p class="pubdate">(.*?)</p>', text)
        desc = grab(r'<meta name="description" content="(.*?)"', text)
        src_match = re.search(
            r'本文為\s*<a href="([^"]+)"[^>]*>(.*?)</a>（(.*?)）', text, re.S
        )
        src_url, src_date = "", ""
        if src_match:
            src_url = html.unescape(src_match.group(1)).strip()
            src_date = grab(r"(\d{4}-\d{2}-\d{2})", src_match.group(3))

        prev = existing.get(slug, {})
        # Priority: --tag on the CLI > the article's own <meta name="tags"> >
        # whatever index.html already records > keyword suggestions. Explicit
        # and recorded tags keep their order verbatim; only freshly suggested
        # ones get sorted, so rebuilds never churn the page.
        chosen = (
            overrides.get(slug)
            or declared_tags(text)
            or prev.get("tags")
        )
        if chosen:
            tags = [t for t in chosen if t]
        else:
            tags = suggest_tags(slug, title, desc, kicker)
            if not tags:
                src_tag = fallback_tag(kicker)
                if src_tag:
                    tags = [src_tag]
            tags.sort(key=lambda t: (TAG_ORDER.index(t) if t in TAG_ORDER else 99, t))

        rows.append(
            {
                "slug": slug,
                "path": f"{slug}/{f.name}",
                "title": title,
                "kicker": kicker or pubdate,
                "desc": desc,
                "src_url": src_url,
                "src_date": src_date,
                "added": added_overrides.get(slug) or prev.get("added") or added_time(f),
                "tags": tags,
                "is_new": slug not in existing,
            }
        )

    rows.sort(key=lambda r: r["added"], reverse=True)
    return rows


def render(rows: list[dict]) -> str:
    out = []
    for r in rows:
        tag_spans = "".join(f'<span class="tag">{t}</span>' for t in r["tags"])
        out.append(
            f'  <li data-added="{r["added"]}" data-tags="{"|".join(r["tags"])}">\n'
            '    <div class="entry-head">\n'
            f'      <h2 class="entry-title"><a href="{r["path"]}">{r["title"]}</a></h2>\n'
            f'      <span class="entry-date">{r["added"][:10]} 上架</span>\n'
            "    </div>\n"
            f'    <p class="entry-desc">{r["desc"]}</p>\n'
            '    <div class="entry-meta">\n'
            f'      <span>{r["kicker"]}</span>\n'
            f'      <span>原文 {r["src_date"]}</span>\n'
            f'      <span class="entry-tags">{tag_spans}</span>\n'
            "    </div>\n"
            "  </li>\n"
        )
    return "\n" + "\n".join(out).rstrip("\n") + "\n\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--check", action="store_true", help="exit 1 if index is stale")
    ap.add_argument("--tag", action="append", default=[], metavar="SLUG=TAG1,TAG2")
    ap.add_argument("--added", action="append", default=[], metavar="SLUG=ISO")
    args = ap.parse_args()

    overrides: dict[str, list[str]] = {}
    added_overrides: dict[str, str] = {}
    for spec in args.tag:
        slug, _, tags = spec.partition("=")
        overrides[slug.strip()] = [t.strip() for t in tags.split(",") if t.strip()]
    for spec in args.added:
        slug, _, iso = spec.partition("=")
        added_overrides[slug.strip()] = iso.strip()

    text = read_text(INDEX)
    m = re.search(r'(<ol class="entries" id="entries">\n)(.*?)(</ol>)', text, re.S)
    if not m:
        print("index.html: could not find <ol class=\"entries\" id=\"entries\">", file=sys.stderr)
        return 1

    rows = collect(existing_entries(text), overrides, added_overrides)
    new_text = text[: m.start(2)] + render(rows) + text[m.end(2) :]

    news = [r for r in rows if r["is_new"]]
    for r in news:
        print(f"+ {r['slug']}  [{r['added'][:10]}]  tags: {'、'.join(r['tags'])}")
        if len(r["tags"]) < 2:
            print(
                f"  ! only {len(r['tags'])} suggested tag — review and set the rest with "
                f"--tag {r['slug']}=tag1,tag2",
                file=sys.stderr,
            )
    for r in rows:
        if not r["is_new"] and overrides.get(r["slug"]):
            print(f"~ {r['slug']}  tags -> {'、'.join(r['tags'])}")
    print(f"{len(rows)} entries ({len(news)} new)")

    if new_text == text:
        print("index.html is up to date")
        return 0 if not args.check else 0
    if args.check:
        print("index.html is STALE — run build_index.py", file=sys.stderr)
        return 1
    if args.dry_run:
        print("dry run: nothing written")
        return 0
    INDEX.write_text(new_text, encoding="utf-8")
    print("index.html updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

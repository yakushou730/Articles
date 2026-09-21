#!/usr/bin/env python3
"""Reject a source URL that already has a translated article in this repo."""

from __future__ import annotations

import argparse
import html
import re
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


def find_root(start: Path) -> Path:
    for path in (start, *start.parents):
        if (path / "index.html").is_file():
            return path
    return start


ROOT = find_root(Path(__file__).resolve().parent)


def article_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.glob("*/*.zh-Hant.html")
        if path.parent.name not in {".git", ".claude", "assets"}
    )


def source_url(text: str) -> str:
    match = re.search(r'本文為\s*<a href="([^"]+)"', text)
    return html.unescape(match.group(1)).strip() if match else ""


def title(text: str) -> str:
    match = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.S)
    return re.sub(r"<[^>]+>", "", match.group(1)).strip() if match else ""


def normalize_url(url: str) -> str:
    """Normalize only URL syntax that cannot identify a different article."""
    parsed = urlsplit(url.strip())
    scheme = parsed.scheme.lower()
    hostname = (parsed.hostname or "").lower()
    try:
        port = parsed.port
    except ValueError:
        port = None
    default_port = (scheme == "http" and port == 80) or (
        scheme == "https" and port == 443
    )
    netloc = hostname
    if parsed.username or parsed.password:
        userinfo = parsed.username or ""
        if parsed.password is not None:
            userinfo += ":" + parsed.password
        netloc = f"{userinfo}@{netloc}"
    if port is not None and not default_port:
        netloc += f":{port}"
    path = parsed.path.rstrip("/") or "/"
    return urlunsplit((scheme, netloc, path, parsed.query, ""))


def entries() -> list[dict[str, str]]:
    found = []
    for path in article_files():
        text = path.read_text(encoding="utf-8")
        url = source_url(text)
        if url:
            found.append(
                {
                    "path": str(path.relative_to(ROOT)),
                    "title": title(text),
                    "url": url,
                    "normalized": normalize_url(url),
                }
            )
    return found


def duplicate_groups(rows: list[dict[str, str]]) -> list[list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["normalized"]].append(row)
    return [group for group in grouped.values() if len(group) > 1]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check whether a source URL already has a translated article."
    )
    parser.add_argument("url", nargs="?", help="source URL to check")
    parser.add_argument(
        "--all",
        action="store_true",
        help="check existing articles for duplicate source URLs",
    )
    args = parser.parse_args()

    if args.all == bool(args.url):
        parser.error("provide a URL or use --all")

    rows = entries()
    if args.all:
        groups = duplicate_groups(rows)
        if not groups:
            print(f"source URL check clean ({len(rows)} articles)")
            return 0
        for group in groups:
            print(f"duplicate source URL: {group[0]['normalized']}", file=sys.stderr)
            for row in group:
                print(f"  - {row['path']}: {row['title']} ({row['url']})", file=sys.stderr)
        return 1

    requested = normalize_url(args.url)
    matches = [row for row in rows if row["normalized"] == requested]
    if matches:
        print(
            f"source URL already exists: {args.url}\n"
            + "\n".join(
                f"  - {row['path']}: {row['title']} ({row['url']})" for row in matches
            ),
            file=sys.stderr,
        )
        return 1

    print(f"source URL available: {args.url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

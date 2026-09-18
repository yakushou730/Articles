---
name: maintain-article-index
description: Regenerate the root article index (index.html) after adding, removing, or renaming a translated article. Use when the user wants to update / rebuild / refresh the 文章目錄, add a new article to the index, fix its tags or add-time, or check whether the index is stale after a translation was produced by the generate-traditional-chinese-web-content skill.
---

# maintain-article-index

`index.html` at the repo root lists every translated article, sorted by add
time (newest first), with a tag filter. Every entry is one `<li>` inside
`<ol class="entries" id="entries">`.

The filter chips are generated at runtime from each `<li data-tags="A|B|C">`,
so adding an article never requires touching the page's CSS or JavaScript.
Only the `<ol>` body changes.

## Procedure

### 1. Run the builder

```bash
python3 .claude/skills/maintain-article-index/scripts/build_index.py
```

The script scans every `<slug>/<slug>.zh-Hant.html` and rebuilds the entry list.
It reads each article's own metadata — `<h1>`, `.kicker`, `meta[name=description]`,
and the footer line `本文為 <a href="…">…</a>（YYYY-MM-DD）` — so a translation
produced by `generate-traditional-chinese-web-content` needs no manual data entry.

Safe order: write the article first, then run the builder. Running it earlier
just omits the new article.

### 2. Review and fix the tags

Tags are the only judgement call. Precedence:

1. `--tag slug=a,b` on the command line (explicit, always wins)
2. tags already in `index.html` (hand edits survive every rebuild)
3. keyword suggestions from `TAG_RULES` in the script (new articles only)

New entries get suggested tags and are printed with a `+` prefix. Read them
against the article and correct anything wrong:

```bash
python3 .claude/skills/maintain-article-index/scripts/build_index.py \
    --tag my-new-article=代理,工具鏈
```

Keep the tag vocabulary small and topical — reuse an existing tag instead of
coining a near-synonym. Adding a brand-new tag is fine; the chip appears
automatically. `TAG_ORDER` in the script controls chip order only.

### 3. Check add time

Add time defaults to the article folder's creation time (`st_birthtime`), then
the HTML file's mtime. If neither reflects when the article actually went up,
pin it explicitly:

```bash
python3 .claude/skills/maintain-article-index/scripts/build_index.py \
    --added my-new-article=2026-09-20T08:30:00
```

An add time already recorded in `index.html` is never overwritten.

### 4. Verify in the browser

Never report success from the script's stdout alone. Open `index.html` and
confirm, with observed facts:

- entries are in descending `data-added` order;
- the new article's link resolves to a real file;
- its tags appear as chips and that a click filters to it;
- `document.documentElement.scrollWidth <= window.innerWidth`;
- the status line counts match the number of visible `<li>`.

### 5. Health checks

```bash
python3 .claude/skills/maintain-article-index/scripts/build_index.py --dry-run
python3 .claude/skills/maintain-article-index/scripts/build_index.py --check
```

`--dry-run` prints what would change, writes nothing. `--check` exits 1 when
`index.html` disagrees with the files on disk — use it before committing or in
a pre-commit hook.

## Rules

- One `<li>` per article. Never leave an entry pointing at a deleted folder.
- `data-added` and `data-tags` are the only machine-read attributes; keep them
  intact if you hand-edit. `data-tags` uses `|` as the separator — never spaces,
  because tags like `Martin Fowler` and `Claude Code` contain spaces.
- Do not add per-article JavaScript or CSS to `index.html`; the tag filter is
  deliberately generic.
- Report the entry count, the new-tag decisions, and the browser checks — not a
  play-by-play.

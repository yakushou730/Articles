---
description: Rebuild the article index (文章目錄) after adding, removing, or renaming a translated article
argument-hint: "[slug] [tags]"
---

Follow the `maintain-article-index` skill (`skill://maintain-article-index`).

$ARGUMENTS

Steps:

1. Run the builder:
   `python3 .claude/skills/maintain-article-index/scripts/build_index.py`
2. Read the `+` lines it prints. If a new article's suggested tags look wrong,
   re-run with `--tag <slug>=<tag1>,<tag2>` using the existing vocabulary where
   one already fits.
3. Open `index.html` in a browser tab and verify the ordering, the new entry's
   tags and link, and that there is no horizontal overflow. Report only what
   you observed.
4. If nothing changed, say so briefly instead of restating the whole index.

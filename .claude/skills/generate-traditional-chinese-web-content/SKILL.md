---
name: generate-traditional-chinese-web-content
description: >
  Convert a web article into a locally readable Traditional Chinese (zh-Hant)
  HTML page while preserving the original English keywords in parentheses.
  Use when the user supplies a URL and asks for a 繁體中文 / Traditional Chinese
  version, a local offline copy, a translated article page, or a Chinese
  translation of a blog post, docs page, or whitepaper that must stay readable
  without a network connection.
---

# generate-traditional-chinese-web-content

Given one source URL, produce a self-contained Traditional Chinese HTML page
plus locally downloaded images, then have a subagent review the translation.

## Inputs

- **Required:** source URL.
- **Optional:** output directory, output filename, translation style notes
  (e.g. 台灣用語, 精簡, 保留更多原文), scope restriction (only one section).

If output location is unspecified, write into the current working directory in
a folder named after the source slug, as
`<slug>/<slug>.zh-Hant.html` with images in `<slug>/assets/`.

Every newly produced page MUST live in its own `<slug>/` folder — never a bare
`.zh-Hant.html` at the working-directory root. The folder keeps the page and
its downloaded images together and lets multiple translations sit side by side.
Example: `claude-code-best-practices/claude-code-best-practices.zh-Hant.html`
with `claude-code-best-practices/assets/`.

## Procedure

### 0. Reject duplicate source URLs

Before fetching or translating anything, run the repository check with the exact
source URL:

```bash
python3 .claude/skills/generate-traditional-chinese-web-content/scripts/check_source_url.py '<SOURCE_URL>'
```

If it exits non-zero, stop the workflow. Report that the source URL already has
a translated article and include the existing article path and title from the
command output. Do not fetch the page, create a folder, or overwrite an
existing article. The check treats host names as case-insensitive, removes a
trailing slash, ignores URL fragments, and preserves query strings because a
query can identify a different source document.

To audit the repository itself for duplicate source URLs, run:

```bash
python3 .claude/skills/generate-traditional-chinese-web-content/scripts/check_source_url.py --all
```

### 1. Fetch the source

Only after the duplicate check succeeds, read the URL with the `read` tool. Do
not use the browser for reading — `read` returns clean text. Open a browser tab
only if `read` returns navigation chrome, a paywall stub, or missing body
content.

Capture the full source text. The translation MUST cover the whole document,
including appendices, notes, captions, and acknowledgements. Never summarize,
truncate, or "skip the boring parts" — the deliverable is a complete
translation.

Record from the source: exact title, publisher/section kicker (e.g.
`Engineering at Anthropic`), publication date, meta description, and every
image URL in document order.

### 2. Translate

Translate every prose block into Traditional Chinese. Rules:

- **Bilingual keyword convention.** On first meaningful use, render each
  domain term as `繁中（English original）`, e.g. 代理（agents）、
  提示鏈接（prompt chaining）、護欄（guardrails）、評估者－最佳化者
  （evaluator-optimizer）。Repeat the bracket only where it aids scanning;
  do not bracket the same term in every sentence.
- **Headings are bilingual too**, following the source structure:
  `工作流：協調者－工作者（Workflow: Orchestrator-workers）`.
- **Keep in English:** acronyms and proper nouns already used as-is in the
  source (LLM, API, SDK, JSON, MCP, Claude, Anthropic, SWE-bench, GitHub),
  identifiers, code, and model names.
- **Preserve every hyperlink.** Keep the original `href`; the link text is
  translated with the keyword convention.
- **Preserve emphasis.** Strong and italic markers from the source map to
  `<strong>` / `<em>`; do not flatten them.
- Do not add content, examples, opinions, or "clarifications" absent from the
  source. Do not soften claims. Translate faithfully.
- Use a consistent register: technical prose, 繁體中文, full-width punctuation
  （，。「」）with half-width punctuation inside English spans.

Check `references/glossary.md` for established renderings before inventing new
ones, and extend that file when you settle a new term.

### 3. De-AI and de-translationese pass

A faithful draft still reads as machine output. Run a second pass over every
paragraph using `references/de-ai-patterns.md`.

Two distinct defects, and both must be fixed:

- **AI flavor** — 破折號 overuse (`——`, the strongest tell), copula avoidance
  (`作為`／`代表`／`標誌著` for 是), AI vocabulary (此外、至關重要、突顯、彰顯,
  abstract 佈局／生態／格局), negative parallelism, triads you created by
  splitting one idea, bold-label vertical lists, emoji.
- **Translationese** — calqued pronouns (`其`／`它的` where the referent is
  obvious), `當…時` for `when`, light verbs (`進行`／`做出`／`加以` + noun),
  `被` passives, two `的` in a short span, English clause order, bottom-heavy
  sentences.

This pass is **subtractive and reshaping only**. It never adds facts, examples,
opinions, or first-person voice, and it never drops a claim to make a sentence
flow better. Where the source hedges, hedge; where it is blunt, be blunt.
Fidelity outranks naturalness — if a faithful phrasing is stiff, reshape the
syntax, do not cut the content.

Also vary sentence length and paragraph endings; three consecutive sentences of
similar length read as generated.

### 4. Render with the shipped template

Copy `assets/template.html` from this skill and substitute the placeholders:

| Placeholder | Value |
|---|---|
| `{{TITLE}}` | translated title, `繁中（English）` form |
| `{{DOC_TITLE}}` | short page title for the tab, `繁中（English）` |
| `{{KICKER}}` | source section label, e.g. `Engineering at Anthropic` |
| `{{PUBDATE}}` | translated publication date line |
| `{{META_DESCRIPTION}}` | one-sentence Chinese summary |
| `{{CONTENT}}` | the translated body markup |
| `{{SOURCE_URL}}` | source URL |
| `{{SOURCE_TITLE}}` | original English title |
| `{{SOURCE_DATE}}` | ISO date `YYYY-MM-DD` |
| `{{TAGS}}` | comma-separated index tags, e.g. `代理,工具鏈` — reuse existing tags where one fits |

Body markup inside `{{CONTENT}}`:

- `<h2>` for top-level sections, `<h3>` for subsections — mirror the source
  hierarchy exactly.
- `<figure><img src="assets/…" alt="繁中（English）"><figcaption>繁中（English）
  </figcaption></figure>` for every image, in source order.
- `<blockquote>` for editor notes and callouts.
- `<ul>` / `<ol>` for lists, nested where the source nests them.

Keep the template's inline `<style>` untouched — that CSS is the approved theme
(Anthropic-toned palette, serif body, automatic dark mode, print rules).

### 5. Localize images and go offline

Download every source image into `<slug>/assets/`, beside the output HTML, then
rewrite the `<img src>` to the relative `assets/<filename>` path. The page MUST
render fully with the network disconnected; a CDN hotlink is a defect. Skip this
only if the user explicitly asks for remote images.

### 6. Verify the render

Open the generated file in a browser tab and confirm, with observed facts:

- every `<img>` has `complete === true` and `naturalWidth > 0`;
- `document.documentElement.scrollWidth <= window.innerWidth` (no horizontal
  overflow);
- section and figure counts match the source.

Fix any failure before proceeding. Do not report success from inspection alone.

### 7. Review with a subagent

Spawn a `reviewer` subagent in the same turn the file is finished. The reviewer
checks **fidelity and readability separately** — a translation can be accurate
and still read as machine output, and those are different findings.

Give it the source URL, the generated file path, and this brief:

```
# Target
Source: <URL>
Translation: <path to generated html>
Non-goals: do not rewrite or restyle; do not edit files.

# Check, section by section against the source
1. Omission — every heading, paragraph, list item, caption, note, and appendix
   is present. Report anything dropped or summarized.
2. Addition — any sentence, example, or claim not in the source.
3. Mistranslation — wrong meaning, wrong technical sense, or wrong
   cause/effect. Quote the Chinese and the English it should match.
4. Terminology — consistency across the document and agreement with
   references/glossary.md.
5. Keyword convention — domain terms carry the（English）bracket; acronyms and
   proper nouns are left in English.
6. Links — every href preserved and still pointing at the source target.
7. Markup fidelity — heading levels mirror the source; emphasis preserved;
   lists nested as in the source.
8. Register — Traditional Chinese, no Simplified characters, no untranslated
   leftover English paragraphs.
9. AI flavor — count the em dashes (`——`); there should be at most one in the
   document. Then look for copula avoidance (作為／代表／標誌著 where 是 fits),
   AI vocabulary (此外、至關重要、突顯、彰顯、佈局、生態、格局), negative
   parallelism (不僅……而是……), bold-label-then-colon lists, and emoji.
10. Translationese — calqued pronouns (其／它的 with an obvious referent),
   當…時 for "when", light verbs (進行／做出／加以 + noun), 被 passives,
   two 的 in a short span. Quote each instance.
11. Readability — read the prose as a native reader would. Flag any sentence
   that must be re-read to parse, any paragraph where three consecutive
   sentences have similar length, and any passage that reads like a translated
   English sentence rather than a Chinese one. Judge this against
   `references/de-ai-patterns.md`.

# Acceptance
Output a findings list. Each finding: severity (high/medium/low), location
(quote or heading), the problem, and the concrete fix. For AI-flavor and
translationese findings, quote the offending text verbatim. State explicitly
if a category is clean. For the fidelity categories (1-8), verify against the
source; for 9-11, judge the Chinese as prose. Do not restate the document.
```

Apply every high and medium finding yourself, then re-run the render check
(step 5) if markup or images changed. Report the reviewer's findings and your
resolution in the final answer.

### 8. Commit and push

After the translation, render verification, and reviewer resolution all pass,
automatically commit and push the completed work. Do not commit or push when
the duplicate-source check rejects the URL or when any required verification
fails.

1. Check the working tree and identify only the files changed by this
   translation workflow. This normally includes the new `<slug>/` article
   folder and any glossary or index files explicitly updated by the workflow.
2. Stage those explicit paths only. Never use `git add -A` or stage unrelated
   user changes.
3. If there are no staged changes, report that there is nothing to commit and
   do not create an empty commit.
4. Create a commit using this message format:

   ```text
   Add Traditional Chinese translation: <slug>
   ```

5. Push the current branch to its configured upstream with `git push`.
6. Report the commit hash and push result. If commit or push fails, report the
   exact command failure and do not claim completion.

The commit and push are part of the successful workflow, not an optional
follow-up. Perform them only after all article files, local images, glossary
updates, index updates, and review fixes are complete.

## Rules

- Never translate a page you could not fetch — report the failure instead of
  inventing content.
- Never drop a section because it is long or seems unimportant.
- Never leave the page dependent on the source CDN for images.
- Never let the de-AI pass add facts or drop claims. It removes machine flavor
  and translationese; it does not editorialize, and it does not invent a voice.
- Never machine-translate and ship. A draft that mirrors English sentence
  structure is unfinished work, not a translation.
- The reviewer reviews; it does not edit. The main agent owns all edits.
- Report the deliverable paths, the verification evidence, and the reviewer's
  verdict — not a play-by-play of the translation.

## Attribution

`references/de-ai-patterns.md` sections A and C adapt
[Humanizer-zh-TW](https://github.com/kevintsai1202/Humanizer-zh-TW) (MIT License,
Copyright (c) 2026 歸藏), which localizes
[blader/humanizer](https://github.com/blader/humanizer) and draws on
[Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing).
Section B (translationese) is authored for this skill.

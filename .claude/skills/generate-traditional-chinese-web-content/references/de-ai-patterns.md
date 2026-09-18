# 去 AI 味與去翻譯腔（De-AI / De-translationese）

Two different problems get conflated. Fix both.

- **AI flavor** — patterns that mark text as machine-written in Chinese,
  regardless of source. Adapted from
  [Humanizer-zh-TW](https://github.com/kevintsai1202/Humanizer-zh-TW) (MIT),
  itself from [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing).
- **Translationese** — patterns that mark text as *translated* from English.
  The upstream humanizer does not cover these, because it assumes natively
  written Chinese. A translated article needs both passes.

Both passes are **subtractive and reshaping only**. They never add facts,
examples, opinions, or first-person experience. The hard constraint from
SKILL.md stands: fidelity to the source outranks naturalness. If a phrase is
awkward but faithful, keep the meaning and reshape the syntax — never drop the
claim.

## Protected spans — do not touch

Code, URLs, hrefs, file paths, API and tool names, numbers, benchmark names,
product names, direct quotations, the `繁中（English）` keyword brackets, and
`<strong>` / `<em>` emphasis the source carries. Restore any of these you
accidentally alter.

## A. AI flavor — the high-yield checks

Ordered by how often they actually fire in translated technical prose.

### A1. Em dash overuse（破折號過度使用）

The single most reliable tell. English uses `—` for apposition; Chinese prose
does not, and calquing it produces 中文 that reads like a translated sales deck.

- Before: `我們會從最基礎的積木——增強型 LLM——開始`
- After: `我們會從最基礎的元件講起：增強型 LLM`

Use `：`、`，`、`（ ）`, or split the sentence. Keep at most one em dash in the
whole document, and only where a parenthetical genuinely interrupts. Note:
`－` (U+FF0D) inside a compound term such as 協調者－工作者 is part of the term,
not punctuation — leave it.

### A2. Copula avoidance（繫詞迴避）

Prefer 是 / 有 over 作為、代表、象徵著、標誌著、充當、擁有、設有.

- Before: `這些框架作為讓代理系統更容易實作的工具`
- After: `這些框架讓代理系統更容易實作`

### A3. AI vocabulary（AI 詞彙）

High-frequency offenders: 此外、至關重要、深入探討、突顯、彰顯、賦能、佈局、
織錦、證明、寶貴的、充滿活力的、持久的、培養、獲得、關鍵（形容詞濫用）、
以及抽象的「生態」「格局」「版圖」。

Delete or replace with the concrete thing. Most of these can simply vanish.

### A4. Negative parallelism and triads（否定式排比與三段式）

`不僅……而是……`、`不只是……更是……` — allow at most one per long document.
Three-item lists where the source has three items are fine (faithfulness wins);
three-item lists that *you* created by splitting a single idea are not.

### A5. Meaning inflation（誇大意義）

`見證了`、`是……的體現`、`象徵著`、`為……奠定基礎`、`標誌著一個轉折點`.
When the source says a thing exists or happened, say that. Do not promote it.

### A6. Vague attribution（模糊歸因）

`業界專家認為`、`觀察者指出`、`多數人相信`. If the source names the source,
keep the name. If the source is vague, stay vague — do not manufacture a name.

### A7. Outline sections and generic optimism（提綱式結尾與通用樂觀）

Formulaic `挑戰與未來展望` and closing lines like `未來值得期待`. Report what
the source reports; do not add a hopeful coda.

### A8. Formatting tells

Emoji in headings or bullets; bold-label-then-colon vertical lists
(`- **效能：** 效能獲得提升`) unless the source is itself such a list; bold
scattered over ordinary nouns. All three are common LLM output and absent from
human technical writing.

### A9. Padding and over-hedging（填充與過度限定）

`為了達到……的目的` → `為了`；`在……的情況下` → `如果／當`；
`值得注意的是` → delete；`可以潛在地可能` → `可能`.
One hedge per claim, matching the source's own hedge strength.

## B. Translationese — the pass the upstream humanizer lacks

### B1. Pronoun calque（代詞照搬）

English needs a possessive; Chinese often does not.

- Before: `代理能處理精密的任務，但其實作往往相當直接`
- After: `代理能處理精密的任務，但實作往往相當直接`

Drop 其／它的／他們的 wherever the referent is already unambiguous. Same for
reflexive 自己 and 他們 when the subject is clear.

### B2. `當…時` calque（"when" 句型照搬）

English `When X, Y` becomes 當X時, which is grammatical but stiff and repetitive.

- Before: `當確實需要更多複雜度時，工作流提供了可預測性`
- After: `需要更多複雜度時，工作流提供可預測性`  or  `如果需要更多複雜度，工作流提供可預測性`

Also: 在……方面、就……而言、對於……來說 used as mechanical sentence openers.

### B3. Light-verb calque（輕動詞照搬）

`進行`、`做出`、`加以`、`予以` + noun calques `do/make/perform + noun`.

- Before: `對輸入進行分類` → After: `把輸入分類`
- Before: `做出決定` → After: `決定`
- Before: `對其進行最佳化` → After: `最佳化它`／`調整它`

### B4. Noun-stack calque（名詞堆疊）

`X 的 Y 的 Z` chains and `……性`／`……化`／`……度` coinages.
Break with 動詞 or 的 only once: `模型驅動的決策` ✓，`由模型驅動的決策過程` ✗.

### B5. Passive calque（被字句照搬）

English passive → 被 in Chinese reads as translated or as misfortune.
Prefer topic-comment or 由／透過／經.

- Before: `這個工作流被用於處理複雜任務`
- After: `這個工作流用來處理複雜任務`

### B6. Clause-order calque（語序照搬）

English front-loads subordinate clauses and trails the main point; Chinese
often reads better with the condition or topic first and a shorter predicate
second. Re-order when it makes the sentence land — but never re-order causal
claims, which would alter meaning.

### B7. `的` accumulation（的字堆疊）

Two `的` within a short span almost always signals a literal translation.
Recast with a verb: `提升準確度的取捨` → `用延遲換取準確度`.

### B8. Bottom-heavy sentences（句尾沉重）

English permits long trailing `, which …` chains. Chinese prefers the weight
earlier. Split, or promote the trailing clause to its own sentence.

## C. Rhythm — what makes the result not read as machine output

- **Vary sentence length.** Three consecutive sentences of similar length read
  as generated. Break one.
- **Vary paragraph endings.** Do not end every paragraph on a one-line summary.
- **Do not explain the metaphor.** If a figure of speech is clear, stop.
- **Keep the source's own texture.** Where the source hedges, hedges
  parenthetically, or leaves something unresolved, the translation should too.
  Do not smooth a real qualification into an assertion, and do not add
  qualifiers the source lacks.

## D. Checklist before rendering

- [ ] Em dashes: at most one; all others recast as `：`、`，`、`（ ）`
- [ ] `其` / `它的` removed where the referent is obvious
- [ ] `當…時` reduced to plain conditionals
- [ ] `進行` / `做出` / `加以` / `予以` replaced with real verbs
- [ ] 是 / 有 used instead of 作為 / 代表 / 象徵著 / 標誌著
- [ ] AI 詞彙 list scanned and cut
- [ ] No sentence-length run of three
- [ ] No `不僅……而是……` unless the source has the same contrast
- [ ] Keyword brackets intact; English terms still in English
- [ ] Code, URLs, hrefs, numbers, names unchanged
- [ ] No fact, example, or opinion added
- [ ] Traditional Chinese throughout; full-width punctuation in Chinese prose

## Attribution

Sections A and C adapt
[Humanizer-zh-TW](https://github.com/kevintsai1202/Humanizer-zh-TW)
(MIT License, Copyright (c) 2026 歸藏), which localizes
[blader/humanizer](https://github.com/blader/humanizer) and draws on
[Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing).
Section B is written for this skill to cover translation-specific artifacts.

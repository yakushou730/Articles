# Articles

英文技術文章的繁體中文翻譯，離線可讀的靜態網站。

**線上網址：<https://blog.yakushou.com/Articles/>**

（`https://yakushou730.github.io/Articles/` 也通，同一個站。這是 GitHub Pages 的
project site，子路徑取自 repo 名稱。**repo 不能改名**，改了網址就變。）

---

## 需要重新部署嗎？

**不用。** 推上 `main` 就自動部署，沒有手動步驟。

```
push to main  →  GitHub Actions「Deploy to GitHub Pages」  →  網站更新
```

通常 30～60 秒上線。想看進度或哪一步掛掉：

```bash
gh run list --repo yakushou730/Articles --limit 5
gh run watch --repo yakushou730/Articles
```

也可以到 repo 的 **Actions** 頁籤，或手動觸發一次（`workflow_dispatch`）：

```bash
gh workflow run pages.yml --repo yakushou730/Articles --ref main
```

> 部署前會先跑兩道關卡：網站健檢（`audit_site.py --strict`）與 index 一致性
> 檢查（`build_index.py --check`）。**任一失敗就不會發布**，網站維持在上一版，
> 你不會因為忘記更新 index 而推出壞站。

---

## 新增一篇文章

### 步驟 1：產生翻譯

用 `/generate-traditional-chinese-web-content` skill，給它原文網址，它會產出：

```
<slug>/<slug>.zh-Hant.html      # 文章本體
<slug>/assets/…                 # 圖片（若有）
```

`<slug>` 是文章資料夾名稱，用英文短名，例如 `self-improving-agents`。

**這一步不用做任何設定。** 資料夾放對位置就好，index 會自己去讀。

### 步驟 2：更新 index

```bash
/update-index
```

或在終端機直接跑：

```bash
python3 .claude/skills/maintain-article-index/scripts/build_index.py
```

它會掃描所有 `<slug>/<slug>.zh-Hant.html`，從每篇自己的 `<h1>`、kicker、
`meta description`、頁尾的原文來源行讀出標題與日期，重建 `index.html`。

新文章會以 `+` 開頭印出來，並附上建議標籤（依關鍵字）。

### 步驟 3：確認標籤

標籤是唯一需要人判斷的地方。新文章拿到的是關鍵字猜測，讀一下、不對就改：

```bash
python3 .claude/skills/maintain-article-index/scripts/build_index.py \
    --tag my-new-article=代理,工具鏈
```

**盡量沿用既有詞彙**，別為同義詞另開新標籤。目前使用的標籤：

| 主題 | 來源 |
|---|---|
| 代理、工作流、記憶與脈絡、工具鏈、提示工程、程式碼品質、架構模式、自動化迴路、程式碼檢索、實務技巧、人為監督 | Addy Osmani、Martin Fowler、Anthropic、Claude Code、aider |

加了沒用過的新標籤也可以，chip 會自動長出來，不必改任何程式。

### 步驟 4：確認上架時間（通常不用管）

預設抓資料夾的建立時間。如果那時間不對（例如資料夾是很久以前建的），
就明確指定：

```bash
python3 .claude/skills/maintain-article-index/scripts/build_index.py \
    --added my-new-article=2026-09-20T08:30:00
```

一旦寫進 `index.html` 就不會被之後的重建覆蓋掉。

### 步驟 5：本機檢查

用瀏覽器打開 `index.html`，確認：

- 排序是新的在前
- 新文章連得到、標籤點下去篩得到它
- 沒有橫向滾動條

### 步驟 6：推送

```bash
git add -A
git commit -m "docs: add Traditional Chinese translation of <原文標題>"
git push
```

推完就自動部署，不用再做任何事。

---

## 一次看完的流程

```bash
# 1. 翻譯（用 skill 產生 <slug>/ 資料夾）
# 2. 更新 index
python3 .claude/skills/maintain-article-index/scripts/build_index.py

# 3. 標籤不對就覆寫
python3 .claude/skills/maintain-article-index/scripts/build_index.py \
    --tag <slug>=標籤1,標籤2

# 4. 推送（自動部署）
git add -A && git commit -m "docs: add <title>" && git push
```

---

## 目錄

| 路徑 | 用途 |
|---|---|
| `index.html` | 文章目錄首頁，依上架時間排序，可依標籤篩選 |
| `<slug>/<slug>.zh-Hant.html` | 單篇文章（一篇文章一個資料夾） |
| `.github/workflows/pages.yml` | 部署流程 |
| `.claude/skills/maintain-article-index/` | index 維護 skill 與腳本 |
| `.claude/skills/generate-traditional-chinese-web-content/` | 翻譯 skill |
| `.claude/commands/update-index.md` | `/update-index` 指令 |

---

## 兩個會讓部署失敗的規則

網站是掛在子路徑 `/Articles/` 下，而且沒有經過 Jekyll 處理，所以：

**1. 不能有 root-relative 連結**

`href="/foo/bar"` 會被解讀成網域根目錄（`blog.yakushou.com/foo/bar`），不是
`/Articles/foo/bar`，結果 404。要嘛用相對路徑，要嘛用完整 `https://` 網址。

> 從上游網站複製內容時特別容易踩到這點：對方的 `/agentic-engineering/x/`
> 是在**他們的**網域根目錄下有效的連結，搬過來就壞了。目前 repo 裡這類連結
> 都已改成指向 `addyosmani.com` 的絕對網址。

**2. 不能有 `{{ … }}` 或 `{% … %}`**

repo 根目錄有 `.nojekyll`，GitHub Pages 才不會拿 Jekyll 去渲染檔案。**不要刪掉它。**

推送前先自己檢查：

```bash
python3 .claude/skills/maintain-article-index/scripts/audit_site.py --strict
```

沒問題會印 `site audit clean`；有問題會列出檔案、行號與原因，並以 exit code 1 結束。
CI 跑的就是同一支腳本。

---

## 這個 repo 跟 Hugo 部落格的關係

`blog.yakushou.com` 這個網域是綁在 **user site**（`yakushou730.github.io` repo）
上的 Hugo 部落格。GitHub Pages 的 project site 會自動繼承同帳號的網域，
掛在 `/Articles/` 底下。所以：

- Hugo 站仍然在 `/`（`/posts/`、`/tags/` 等），沒有任何影響
- 本 repo **不需要也不該**放 `CNAME` 檔，那會跟 user site 搶設定
- 兩站路徑完全不重疊

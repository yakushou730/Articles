# Articles

英文技術文章的繁體中文翻譯，離線可讀的靜態網站。

**線上網址：<https://blog.yakushou.com/Articles/>**

（`https://yakushou730.github.io/Articles/` 也通，同一個站。這是 GitHub Pages 的
project site，子路徑取自 repo 名稱。**repo 不能改名**，改了網址就變。）

---

## 需要重新部署嗎？

**不用，而且 index 也不用自己更新。** 推上 `main` 就全部自動完成。

```
push to main
  ├─ Update article index   →  重建 index.html 並自動 commit
  └─ Deploy to GitHub Pages →  稽核後發布網站
```

兩件事都在 CI 做完，你只要負責寫文章。通常 30～60 秒上線。

### 那 index 是怎麼被更新的

`Update article index` 這個 workflow 會在你 push 動到任何文章時觸發，跑
`build_index.py` 重建 `index.html`，如果內容有變就以 `github-actions[bot]`
身分自動 commit 並 push（訊息是 `chore: rebuild article index`）。

它不會無限迴圈：用 `GITHUB_TOKEN` 推的 commit 本來就不會再觸發 workflow，
workflow 裡另外加了 `if: github.actor != 'github-actions[bot]'` 當第二層保險。

### 你會遇到的唯一狀況：本機落後一個 commit

bot 推了 index 之後，你本機會落後。下次要推之前先同步：

```bash
git pull --rebase
```

忘了的話 `git push` 會被你拒絕（non-fast-forward），照著做 `git pull --rebase`
再推就好。

### 看部署狀態

```bash
gh run list --repo yakushou730/Articles --limit 5
gh run watch --repo yakushou730/Articles
```

也可以到 repo 的 **Actions** 頁籤，或手動觸發：

```bash
gh workflow run pages.yml --repo yakushou730/Articles --ref main
```

> 部署前有一道關卡：網站健檢（`audit_site.py --strict`）。它會擋掉在
> `/Articles/` 子路徑下會 404 的 root-relative 連結，以及會被 Jekyll 吃掉的
> `{{ … }}` 語法。**失敗就不發布**，網站維持在上一版。

---

## 新增一篇文章

### 步驟 0：先檢查原文連結

翻譯前先確認這個來源尚未製作過文章：

```bash
python3 .claude/skills/generate-traditional-chinese-web-content/scripts/check_source_url.py '<原文網址>'
```

如果連結已存在，指令會以失敗結束，列出既有文章的路徑與標題；此時停止流程，
不要抓取原文、建立新資料夾或覆蓋既有文章。檢查會忽略網址片段（`#...`）、
移除結尾斜線，並保留 query string，避免把不同文件誤判成同一篇。

### 步驟 1：產生翻譯

用 `/generate-traditional-chinese-web-content` skill，給它原文網址。skill 會在
抓取原文前自動執行上述檢查；遇到重複連結會直接擋下流程。

它會產出：

```
<slug>/<slug>.zh-Hant.html      # 文章本體
<slug>/assets/…                 # 圖片（若有）
```

`<slug>` 是資料夾名稱，用英文短名，例如 `self-improving-agents`。

### 步驟 2：在文章裡宣告標籤

在 `<head>` 加一行：

```html
<meta name="tags" content="代理,工具鏈">
```

**這一行就是標籤的唯一來源。** 之後要改標籤，改這裡、push，index 會跟著更新，
不需要碰 `index.html`。（新版的翻譯模板已經有 `{{TAGS}}` 佔位符，產生時就填好。）

盡量沿用既有詞彙，別為同義詞另開新標籤：

| 主題標籤 | 來源標籤 |
|---|---|
| 代理、工作流、記憶與脈絡、工具鏈、提示工程、程式碼品質、架構模式、自動化迴路、程式碼檢索、實務技巧、人為監督 | Addy Osmani、Martin Fowler、Anthropic、Claude Code、aider |

加了沒用過的標籤也可以，chip 會自動長出來，不必改任何程式。

> 沒有宣告 `meta name="tags"` 也不會壞：index 會退回到關鍵字猜測，再不行就用
> 來源站名當標籤。但那樣就得人工複查，**建議還是自己宣告。**

### 步驟 3：推送

```bash
git add -A
git commit -m "docs: add Traditional Chinese translation of <原文標題>"
git push
```

**沒了。** index 由 CI 重建並 commit，網站重新部署。不需要跑本機指令。

### 想先在本機看結果（可選）

```bash
python3 .claude/skills/maintain-article-index/scripts/build_index.py --dry-run
```

只印出會有什麼改變，不寫檔。

### 需要人工判斷的少數情況

- **上架時間。** 預設抓資料夾建立時間。若那時間不對（例如資料夾很久以前就建好），
  在 CI 自動 commit 之後手動改 `index.html` 的 `data-added` 即可，往後重建不會覆蓋它。
  或本機指定：`build_index.py --added <slug>=2026-09-20T08:30:00`。
- **關鍵字猜出來的標籤。** 只在你沒宣告 `meta name="tags"` 時才會發生。

---

## 一次看完的流程

```bash
# 1. 翻譯（用 skill 產生 <slug>/ 資料夾）
# 2. 在文章 <head> 宣告 <meta name="tags" content="標籤1,標籤2">
# 3. 推送（index 與部署都由 CI 自動完成）
git add -A && git commit -m "docs: add <title>" && git push
```

之後要同步本機：`git pull --rebase`

---

## 目錄

| 路徑 | 用途 |
|---|---|
| `index.html` | 文章目錄首頁，依上架時間排序，可依標籤篩選 |
| `<slug>/<slug>.zh-Hant.html` | 單篇文章（一篇文章一個資料夾） |
| `.github/workflows/update-index.yml` | 自動重建 index 並 commit |
| `.github/workflows/pages.yml` | 部署網站 |
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

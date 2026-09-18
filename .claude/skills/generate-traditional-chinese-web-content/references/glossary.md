# Glossary — Traditional Chinese renderings

Established renderings. Reuse these; add new rows when you settle a term.
Format: `繁中（English）`. Terms already identical in both are listed because
they are frequently mistranslated.

## Agentic systems

| English | 繁中 |
|---|---|
| agent | 代理 |
| agentic system | 代理系統 |
| workflow | 工作流 |
| augmented LLM | 增強型 LLM |
| autonomous agent | 自主代理 |
| prompt chaining | 提示鏈接 |
| routing | 路由 |
| parallelization | 平行化 |
| sectioning | 分段 |
| voting | 投票 |
| orchestrator-workers | 協調者－工作者 |
| orchestrator | 協調者 |
| worker LLM | 工作者 LLM |
| evaluator-optimizer | 評估者－最佳化者 |
| code path (predefined) | 程式碼路徑（預先定義的） |
| orchestrate | 編排 |

## Engineering practice

| English | 繁中 |
|---|---|
| framework | 框架 |
| abstraction layer | 抽象層 |
| composable pattern | 可組合的模式 |
| guardrail | 護欄 |
| eval / evaluation | 評估 |
| latency | 延遲 |
| tradeoff | 取捨 |
| retrieval | 檢索 |
| in-context example | 脈絡內範例 |
| prompt engineering | 提示工程 |
| tool use block | 工具使用區塊 |
| toolset | 工具集 |
| structured output | 結構化輸出 |
| Poka-yoke | 防呆 |
| edge case | 邊界情況 |
| escaping (string) | 跳脫處理 |
| overhead | 額外負擔 |
| chunk header | 區塊標頭 |
| false positive | 偽陽性 |
| false negative | 偽陰性 |
| docstring | docstring（保留原文） |
| ACI (agent-computer interface) | 代理－電腦介面 |
| HCI (human-computer interface) | 人機介面 |
| ground truth | 真實依據 |
| stopping condition | 停止條件 |
| compounding error | 錯誤層層累積 |
| sandboxed environment | 沙箱環境 |
| human oversight | 人為監督 |
| human review | 人為審查 |
| feedback loop | 回饋迴路 |
| resolution (support) | 解決結果 |
| usage-based pricing | 以用量為基礎的定價模式 |
| code completion | 程式碼補全 |
| separation of concerns | 關注點分離 |
| model-driven decision-making | 由模型驅動的決策 |
| cookie-cutter / prescriptive | 規範性的 |
| reference implementation | 參考實作 |
| workbench | workbench（保留原文） |
| managed agent | 託管代理 |
| Claude Managed Agents | Claude 託管代理 |

## Claude Code product surface

| English | 繁中 |
|---|---|
| session | 工作階段 |
| context window | 脈絡視窗 |
| context | 脈絡 |
| compaction (user-facing /compact) | 壓縮 |
| plan mode | 規劃模式 |
| permission mode | 權限模式 |
| permission allowlist | 權限允許清單 |
| sandboxing | 沙箱 |
| subagent | 子代理 |
| checkpoint | 檢查點 |
| rewind | 回溯 |
| non-interactive mode | 非互動模式 |
| fan-out | 扇出 |
| worktree | worktree（保留原文） |
| hook | hook（保留原文） |
| skill | skill（保留原文） |
| plugin | 外掛 |
| slash command | 斜線指令 |
| prompt | 提示 |
| spec | 規格 |
| agentic loop | 代理迴路 |
| verification loop | 驗證迴路 |
| adversarial review | 對抗式審查 |
| status line | 狀態列 |

## Kept in English

Acronyms and product or project names: LLM, API, SDK, CLI, JSON, HTML, CSS,
URL, MCP, ACI, HCI, GUI, SWE-bench, Claude, Claude Haiku, Claude Sonnet,
Anthropic, AWS, GitHub, Rivet, Vellum, Model Context Protocol, Strands Agents SDK,
Claude Agent SDK.

## Style rules

- Full-width punctuation in Chinese prose（，。「」：；？）, half-width inside
  English spans and code.
- Chinese–English boundary: no space around the full-width bracket
  （like this）, one space around half-width English tokens when embedded in
  Chinese text is optional and should be applied consistently within a document.
- 台灣用語 preferred：最佳化（not 优化）、資訊（not 信息）、網路（not 网络）、
  專案（not 项目）、品質（not 质量）。Never emit Simplified characters.
- Do not use 「你」/「您」 inconsistently: pick one and hold it. Technical
  articles default to 你.

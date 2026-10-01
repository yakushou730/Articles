#!/usr/bin/env python3
"""Catch register drift and over-chopped prose in a generated zh-Hant article.

The de-AI / de-translationese pass (SKILL.md step 3) is subtractive, and that
is exactly what makes it hazardous: a purely subtractive pass has no floor, so
it can sand a technical article down toward conversational Chinese and chop
well-formed sentences into fragments. Both regressions are mechanical enough
to check, which is better than trusting a reviewer pass that runs afterwards.

Design rule for this linter: **a hard finding must be mechanically wrong.**
Anything requiring taste (light verbs, 此外, 其實, fragment stats) is reported
as soft and never fails the run. Rules in HARD_RULES were each measured
against the 26 published articles in this repo; rules that fired mostly on
legitimate prose were demoted to SOFT_RULES rather than shipped as gates.

Usage:
    python3 check_register.py <article.html> [more.html ...]
    python3 check_register.py --all
    python3 check_register.py --all --soft
"""

from __future__ import annotations

import argparse
import glob
import re
import sys
from pathlib import Path

CJK = r"\u4e00-\u9fff"

EM_DASH_LIMIT = 1

# 當 is often not temporal. Guard both sides: 相當/當然/當下… start with 當,
# and 相當/不當/恰當/妥當… end with it (相**當**比例 must not match).
WHEN_LEAD = r"(?!相當|當然|當下|當初|當場|當地|當今|當事|當作|當成|當選|當兵|當差)"
WHEN_TAIL = r"(?<!相|不|恰|適|妥|得|失|正|過|抵|典|獨)"
BARE_WHEN = rf"{WHEN_TAIL}當{WHEN_LEAD}[^，。；：]{{1,30}}時"

# Words that essentially never survive a careful technical rewrite.
AI_VOCAB = r"至關重要|突顯|彰顯|賦能|深入探討|重中之重|不可或缺"

# Fires space-separated particles only; 吧/喔/啦/囉/咧/嘛 as sentence enders.
CASUAL_PARTICLE = r"[。！？][^。！？]{0,40}[吧喔囉咧嘛][。！？]"

HARD_RULES: list[tuple[str, str, str]] = [
    ("em-dash", r"——", f"破折號 ——（全文上限 {EM_DASH_LIMIT} 個）"),
    ("when-calque", BARE_WHEN, "翻譯腔：當…時（改為條件句）"),
    ("ai-vocab", AI_VOCAB, "AI 詞彙（幾乎不會出現在認真的技術中文）"),
]

SOFT_RULES: list[tuple[str, str, str]] = [
    # A casual particle can be a faithful rendering of the source's own voice
    # (e.g. a rhetorical "…, right?"), so this is context, not a defect.
    ("casual-particle", CASUAL_PARTICLE, "口語語尾助詞（吧／喔／囉／咧／嘛）——確認原文本身是否同樣隨性"),
    ("ai-vocab-soft", r"此外|佈局|格局|產業生態", "AI 詞彙候選（先確認原文有對應詞）"),
    ("light-verb", rf"(?:進行|做出|加以|予以)[{CJK}]{{2}}", "輕動詞：進行／做出／加以／予以 + 名詞"),
    ("calque-particle", r"其實", "口語：其實（原文為 actually 才保留）"),
    ("casual", r"你也可以|試試|很棒|搞定|弄好", "口語詞"),
    ("passive", rf"被[^，。；：]{{1,14}}", "被字句（可改主題－評論句）"),
    ("pronoun", rf"其[{CJK}]{{1,4}}", "代詞照搬：其（指涉明確時可省）"),
]

SKIP_BLOCK = re.compile(r"<(script|style|pre|code)\b.*?</\1\s*>", re.S | re.I)
TAG = re.compile(r"<[^>]+>")
MAIN = re.compile(r"<main\b[^>]*>(.*?)</main\s*>", re.S | re.I)
PARA = re.compile(r"<p\b[^>]*>(.*?)</p\s*>", re.S | re.I)
SENTENCE = re.compile(r"[^。！？]*[。！？]")
VERBATIM = re.compile(r"<(pre|code|script|style)\b", re.I)


def repo_root(start: Path) -> Path:
    for path in (start, *start.parents):
        if (path / ".git").exists():
            return path
    return start


ROOT = repo_root(Path(__file__).resolve().parent)


class Finding:
    __slots__ = ("rule", "line", "message", "excerpt")

    def __init__(self, rule: str, line: int, message: str, excerpt: str) -> None:
        self.rule = rule
        self.line = line
        self.message = message
        self.excerpt = excerpt


def visible_text(source: str, start: int, end: int) -> tuple[str, list[int]]:
    """Text of a slice with tags removed, plus char -> source-offset map."""
    segment = source[start:end]
    dead = bytearray(len(segment))
    for match in SKIP_BLOCK.finditer(segment):
        dead[match.start() : match.end()] = b"\x01" * (match.end() - match.start())
    for match in TAG.finditer(segment):
        dead[match.start() : match.end()] = b"\x01" * (match.end() - match.start())

    chars: list[str] = []
    offsets: list[int] = []
    for index, char in enumerate(segment):
        if not dead[index]:
            chars.append(char)
            offsets.append(start + index)
    return "".join(chars), offsets


def cjk_len(text: str) -> int:
    return len(re.findall(rf"[{CJK}]", text))


def snippet(text: str, position: int, width: int = 40) -> str:
    low = max(0, position - width // 2)
    high = min(len(text), position + width)
    return ("…" if low else "") + text[low:high].replace("\n", " ").strip() + ("…" if high < len(text) else "")


def lint(path: Path) -> tuple[list[Finding], list[Finding], dict[str, int]]:
    source = path.read_text(encoding="utf-8")
    line_starts: list[int] = []
    total = 0
    for line in source.split("\n"):
        line_starts.append(total)
        total += len(line) + 1

    def line_of(offset: int) -> int:
        low, high = 0, len(line_starts) - 1
        while low < high:
            mid = (low + high + 1) // 2
            if line_starts[mid] <= offset:
                low = mid
            else:
                high = mid - 1
        return low + 1

    main = MAIN.search(source)
    if not main:
        raise ValueError(f"{path}: no <main> block")

    body_text, body_offsets = visible_text(source, main.start(1), main.end(1))

    hard: list[Finding] = []
    soft: list[Finding] = []
    counts: dict[str, int] = {}

    for rule, pattern, message in HARD_RULES:
        seen = 0
        for match in re.finditer(pattern, body_text):
            seen += 1
            counts[rule] = seen
            if rule == "em-dash" and seen <= EM_DASH_LIMIT:
                continue
            hard.append(Finding(rule, line_of(body_offsets[match.start()]), message, snippet(body_text, match.start())))

    for rule, pattern, message in SOFT_RULES:
        seen = 0
        for match in re.finditer(pattern, body_text):
            seen += 1
            counts[rule] = seen
            soft.append(Finding(rule, line_of(body_offsets[match.start()]), message, snippet(body_text, match.start())))

    # Chopped-paragraph statistics. Reported, never failed: a short sentence is
    # a legitimate rhetorical move, so only the aggregate signals a problem.
    chopped = 0
    paragraphs = 0
    for para in PARA.finditer(source):
        text, _ = visible_text(source, para.start(1), para.end(1))
        if VERBATIM.search(para.group(1)):
            continue
        text = text.strip()
        if cjk_len(text) < 60:
            continue
        sentences = [s.strip() for s in SENTENCE.findall(text) if s.strip()]
        if len(sentences) < 3:
            continue
        paragraphs += 1
        short = sum(1 for s in sentences if cjk_len(s) <= 12 and not s.rstrip().endswith("："))
        if short >= 2:
            chopped += 1
            soft.append(
                Finding(
                    "chopped-paragraph",
                    line_of(para.start(1)),
                    f"段落偏碎：{short}/{len(sentences)} 句 ≤12 字，考慮把相鄰短句接起來",
                    " / ".join(s for s in sentences if cjk_len(s) <= 12)[:80],
                )
            )
        if chopped == 0 and len(sentences) >= 3 and cjk_len(sentences[-1]) <= 14:
            soft.append(
                Finding("chopped-tail", line_of(para.start(1)), "段落以極短句收尾（≤14 字）", sentences[-1])
            )

    counts["paragraphs"] = paragraphs
    counts["chopped"] = chopped
    return hard, soft, counts


def targets(raw: list[str], all_flag: bool) -> list[Path]:
    if all_flag:
        return [Path(p) for p in sorted(glob.glob(str(ROOT / "*" / "*.zh-Hant.html")))]
    out: list[Path] = []
    for item in raw:
        matches = sorted(glob.glob(item))
        out.extend(Path(m) for m in matches)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="zh-Hant article register linter")
    parser.add_argument("articles", nargs="*", help="generated .zh-Hant.html files")
    parser.add_argument("--all", action="store_true", help="lint every */ *.zh-Hant.html under the repo root")
    parser.add_argument("--soft", action="store_true", help="also print soft (judgment-call) findings")
    parser.add_argument("--quiet", action="store_true", help="only print files with hard findings")
    args = parser.parse_args()

    files = targets(args.articles, args.all)
    if not files:
        parser.error("no article files given (use --all or pass paths)")

    failures = 0
    hard_total = 0
    for path in files:
        if not path.exists():
            print(f"missing: {path}", file=sys.stderr)
            failures += 1
            continue
        try:
            hard, soft, counts = lint(path)
        except ValueError as error:
            print(f"skip: {error}", file=sys.stderr)
            continue

        hard_total += len(hard)
        if hard:
            failures += 1
        if args.quiet and not hard:
            continue

        label = path.name if ROOT not in path.parents else str(path.relative_to(ROOT))
        print(f"\n[{'FAIL' if hard else 'ok'}] {label}")
        for finding in hard:
            print(f"  L{finding.line} {finding.rule}: {finding.message}\n        {finding.excerpt}")
        if args.soft:
            for finding in soft:
                print(f"  L{finding.line} (soft) {finding.rule}: {finding.message}\n        {finding.excerpt}")
        if hard and counts:
            print("  counts: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))

    print(f"\n{len(files)} file(s), {hard_total} hard finding(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

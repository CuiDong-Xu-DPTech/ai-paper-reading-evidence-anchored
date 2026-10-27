#!/usr/bin/env python3
"""校验精读报告中的页码锚点与引文是否真实存在。

用法:
  python3 verify_anchors.py report.md paper.txt            # 校验页码锚点
  python3 verify_anchors.py report.md paper.txt --quotes   # 同时校验引文(若报告含引号引用)

页码锚点格式: (p3) / (p3-4) / （第 3 页） / [第 3 页]
paper.txt 须含 [第 N 页] 标记（由 export_pdf_text.py 生成）。
退出码: 0=全部通过; 1=存在无效锚点。
"""
import re
import sys
import unicodedata


def load_paper_pages(path: str) -> dict:
    text = open(path, encoding="utf-8").read()
    parts = re.split(r"\[第 (\d+) 页\]", text)
    pages = {}
    for i in range(1, len(parts), 2):
        pages[int(parts[i])] = parts[i + 1]
    return pages


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    return re.sub(r"\s+", "", s)


ANCHOR = re.compile(
    r"(?:(?<=\()|(?<=（)|(?<![A-Za-z]))"          # 前置: ( 或 （ 或非字母
    r"(?:p{1,2}|P{1,2}|第\s*)\.?\s*"             # p/pp/P/第
    r"(\d{1,3})"
    r"(?:\s*[-−~–]\s*(\d{1,3}))?"
    r"\s*(?:页|页\)|\)|）)?"                       # 后置: 页/) 或空
)


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    report = open(sys.argv[1], encoding="utf-8").read()
    pages = load_paper_pages(sys.argv[2])
    npages = norm(report)
    anchors = ANCHOR.findall(report)
    bad, ok = [], 0
    for a, b in anchors:
        lo = int(a)
        hi = int(b) if b else lo
        if lo not in pages or hi not in pages or lo > hi:
            bad.append((a, b, "页码越界"))
            continue
        ok += 1
    print(f"锚点总数(含区间展开): {len(anchors)}; 有效: {ok}; 无效: {len(bad)}")
    for a, b, why in bad:
        print(f"  无效锚点 (p{a}{b and '-' + b}): {why}")
    if "--quotes" in sys.argv:
        quotes = re.findall(r"[“\"]([^“”\"]{20,120})[”\"]", report)
        miss = 0
        for q in quotes:
            nq = norm(q)
            found = any(nq[:40] and nq[:40] in norm(t) for t in pages.values())
            if not found:
                miss += 1
                print(f"  引文未命中: {q[:50]}...")
        print(f"引文抽查: {len(quotes)} 条, 未命中 {miss}")
        return 1 if (bad or miss) else 0
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

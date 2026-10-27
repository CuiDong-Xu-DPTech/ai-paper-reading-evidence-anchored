#!/usr/bin/env python3
"""按运行前锁定的 gold checklist 对精读报告做关键事实点自动预检。

用法: python3 checklist_scorer.py report.md checklist.json
checklist.json 格式: [{"id":"G1","patterns":["正则1","正则2",...]}, ...]
某点命中 = 任一 pattern 在报告中匹配(NFKC+去空白后)。
输出: 每点命中状态 + 总分; 退出码 0。
"""
import json
import re
import sys
import unicodedata


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    return re.sub(r"\s+", "", s).lower()


def main() -> int:
    report = norm(open(sys.argv[1], encoding="utf-8").read())
    items = json.load(open(sys.argv[2], encoding="utf-8"))
    total = hit_n = 0
    for it in items:
        total += 1
        hit = any(re.search(p, report, re.IGNORECASE) for p in it["patterns"])
        mark = "HIT " if hit else "MISS"
        if hit:
            hit_n += 1
        print(f"[{mark}] {it['id']}")
    print(f"---- checklist 命中: {hit_n}/{total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

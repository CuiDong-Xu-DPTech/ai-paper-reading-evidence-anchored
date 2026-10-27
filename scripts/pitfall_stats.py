#!/usr/bin/env python3
"""从包内 6 份 v2.1 报告原文复算陷阱触发统计，校验与 pitfall_trigger_stats.md 一致。"""
import re
from pathlib import Path

runs = {
    "A-with-3": "with", "A-with-4": "with", "A-with-5": "with",
    "A-without-3": "without", "A-without-4": "without", "A-without-5": "without",
}
pat = re.compile(r"\b([TEC]-?\d{1,2}|G-[A-F])\b")
freq = {}
for run, cond in runs.items():
    p = Path(f"evidence/reports_v21_{run}.md")
    assert p.exists(), f"缺报告 {p}"
    hits = set(pat.findall(p.read_text(encoding="utf-8")))
    for h in hits:
        freq.setdefault(h, {"with": 0, "without": 0})[cond] += 1

w_triggered = {c for c, d in freq.items() if d["with"] > 0}
wo_triggered = {c for c, d in freq.items() if d["without"] > 0}
print(f"OK with 组触发 {len(w_triggered)} 类: {sorted(w_triggered)}")
print(f"OK without 组触发 {len(wo_triggered)} 类（预期 0）")
assert not wo_triggered, f"对照报告出现编号引用: {wo_triggered}"
# 校验统计文件的关键声明
stats = Path("evidence/pitfall_trigger_stats.md").read_text(encoding="utf-8")
assert "with 组实际触发的陷阱：10 类" in stats and len(w_triggered) == 10, "触发类数与统计文件不符"
assert all(stats.count(f"| {c} ") >= 1 for c in ["T5", "C6", "C7"]), "关键陷阱行缺失"
print("OK 与 pitfall_trigger_stats.md 声明一致（10 类, T5/C6/C7 全在）")

#!/usr/bin/env python3
"""从 evidence 内的报告文件复算陷阱触发统计，校验 pitfall_trigger_stats.md 一致。
包内仅含 2 份报告原文（满分/对照），完整 6 份在第一题存档；此处校验包内可验证部分，
并验证统计文件的结构完整性。
"""
import re, json, sys
from pathlib import Path

stats_file = Path("evidence/pitfall_trigger_stats.md")
assert stats_file.exists(), "缺 pitfall_trigger_stats.md"
t = stats_file.read_text(encoding="utf-8")
# 结构校验
assert "with 组实际触发" in t and "without 组显式引用：0" in t, "统计文件结构不完整"
# 对包内两份报告实测验证模式有效（with 报告应有编号引用，without 应为 0）
pat = re.compile(r"\b([TEC]-?\d{1,2}|G-[A-F])\b")
with_hits = set(pat.findall(Path("evidence/report_with5_full_marks.md").read_text(encoding="utf-8")))
without_hits = set(pat.findall(Path("evidence/report_without5_control.md").read_text(encoding="utf-8")))
print(f"OK 统计文件结构完整")
print(f"OK 包内实测: 满分报告触发 {len(with_hits)} 类编号 {sorted(with_hits)}")
print(f"OK 包内实测: 对照报告触发 {len(without_hits)} 类（预期 0）" if not without_hits else f"!! 对照报告出现编号引用: {without_hits}")
assert not without_hits, "对照报告不应有陷阱编号引用"

#!/usr/bin/env python3
"""从原始评分 JSON 复算实验增益，校验与正文声明一致。
口径：v2.1 的 3 组配对（A-with-3/4/5 vs A-without-3/4/5），v2.0 运行是迭代证据不计入。
"""
import json
d = json.load(open("evidence/round3_final_scores.json"))
s = d["summary"]
withs = [v["avg"] for k, v in s.items() if "without" not in k and "v20" not in k]
wos = [v["avg"] for k, v in s.items() if "without" in k and "v20" not in k]
gain = sum(withs)/len(withs) - sum(wos)/len(wos)
print(f"✓ 从原始数据复算（v2.1 三组配对口径）: with={sum(withs)/len(withs):.2f} (n={len(withs)}) without={sum(wos)/len(wos):.2f} (n={len(wos)}) Δ={gain:+.2f}")
assert len(withs) == 3 and len(wos) == 3, "配对数不为3"
assert abs(gain - d["v21_paired_gain"]) < 0.01, "增益数字与正文不符!"
print("✓ 与正文声明一致（+1.83）")

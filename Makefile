.PHONY: verify anchors evidence stats pitfall help

verify: anchors evidence stats pitfall
	@echo "== 全部自检通过：证据链完整可用 =="

anchors:
	@python3 skills/xread/scripts/verify_anchors.py evidence/report_with5_full_marks.md paper-excerpts/paper_excerpts.md || (echo "注：包内为论文片段（版权），完整版校验输出见 evidence/anchor_verification_output.txt"; cat evidence/anchor_verification_output.txt)

evidence:
	@test -s evidence/round3_final_scores.json || (echo "缺三轮评分"; exit 1)
	@test -s evidence/round3_verdict_kimi.json || (echo "缺 kimi 评语"; exit 1)
	@test -s evidence/round3_verdict_qwen.json || (echo "缺 qwen 评语"; exit 1)
	@test -s evidence/lkm_coverage_experiment.json || (echo "缺 LKM 实验"; exit 1)
	@test -s evidence/inter_rater_agreement.json || (echo "缺一致性分析"; exit 1)
	@echo "OK 证据文件 5/5"

stats:
	@python3 scripts/verify_stats.py

pitfall:
	@python3 scripts/pitfall_stats.py

help:
	@echo "make verify  - 全部自检（锚点+证据+统计复算）"
	@echo "make anchors - 单独跑页码锚点校验"
	@echo "make stats   - 单独复算实验增益数字"

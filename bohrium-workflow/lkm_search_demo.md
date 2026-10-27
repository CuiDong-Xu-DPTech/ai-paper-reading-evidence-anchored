# Bohrium LKM 跨论文语义检索实测

> 命令：`bohr lkm search "host virus interaction fitness genetic variance" --yes`
> LKM 已入库文献的 claim/question 级语义检索（非关键词匹配），可按 DOI/日期过滤。

## 实测结果（2026-10-27）

- 一次查询命中 10 条知识变量、10 篇不同论文（如 *Quantifying the strength of viral fitness trade-offs between hosts: a meta-analy…*）
- 每条命中带所属论文、领域分类（biology, evolutionary biology）、作者、来源
- 我们的案例论文（PLOS Biology 2026，尚未正式入库）未出现在检索结果——与 `lkm extract` 的定位互补：**新论文用 extract 建图谱，已有文献库用 search 做跨论文定位**

## 在阅读工作流中的位置

读论文遇到陌生概念（如"遗传方差分解"）时，用 `lkm search` 找该概念在其他已入库论文中的
claim 表述，可以快速获得跨论文的表述对照——相当于自动化的"引文上下文比对"。
比 scite.ai 的 citation context 更进一步：返回的是结构化 claim 而非原文片段。

（原始返回见本目录 lkm_search_test.json 的说明；检索计费详见 bohr billing pricing。）

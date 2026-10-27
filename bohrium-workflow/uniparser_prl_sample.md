# Uni-Parser 解析样例（PRL 论文）

> 命令：`bohr pdf parse --file PRL论文.pdf --yes`（0.3 元/6页=0.05元/页）→ `bohr pdf result <token> --formatted markdown`
> 与 PyMuPDF 纯文本导出相比：保留 LaTeX 公式与表格结构。

```markdown
# Entangling ions with engineered light gradients

Tommaso Faorlin,1 Lorenz Panzl,1 Phoebe Grosser,1 Pablo Vinas,2 Alan Kahan,2 Walter Joseph Hörmann,1 Yannick Weiser,1 Giovanni Cerchiari,1, 3 Thomas Feldker,4 Alexander Erhard,4 Georg Jacob,4 Juris Ulmanis,4 Rainer Blatt,1, 4, 5 Alejandro Bermudez,2 and Thomas Monz1, 4

1 Universitat Innsbruck, Institut für Experimentalphysik, Technikerstraβe 25/4, 6020 Innsbruck, Austria*

²Instituto de Física Teórica (UAM-CSIC), Universidad Autónoma de Madrid, Cantoblanco, 28094 Madrid, Spa:

Naturwissenschaftlich-Technische Fakultat, Universitat Siegen, Walter-Flex-StraBe 3, 57068 Siegen, Germany

4Alpine Quantum Technologies, Technikerstraβe 17, 6020 Innsbruck, Austria

5 Institute for Quantum Optics and Quantum Information of the Austrian Academy of Sciences, Technikerstraβe 21a, 6020 Innsbruck, Austria

(Dated: March 24, 2026)

Spectral crowding of collective motional modes limits the fidelity of entangling interactions in trapped-ion quantum processors by inducing off-resonant coupling to spectator modes. We introduce a geometric-phase entangling interaction driven by a transverse, time-dependent structured-light force. By applying the force in a plane orthogonal to the optical propagation direction, we reduce the effects of spectral crowding while preserving single-ion addressing. The scheme is compatible with arbitrary qubit encodings, provided that the qubit states experience a differential AC Stark shift. We experimentally realise high-fidelity two-qubit gates with error rates below 5 × 10-3 in ion crystals containing up to 12 ions confined within a single potential well. These results establish gradient-field light-shift gates as a scalable approach to high-fidelity entanglement generation in spectrally crowded trapped-ion systems.

Introduction.— The ability to selectively drive well-defined transitions while suppressing unwanted couplings is a central challenge in the coherent control of quan-tum systems. As quantum processors scale in size and complexity, spectral crowding and parasitic interactions increasingly limit achievable gate fidelities. This issue arises across multiple platforms, including silicon quan-tum dots [1], nitrogen-vacancy centres in diamond [2] and superconducting transmon processors [3, 4], where off-resonant excitation of unwanted transitions can de-grade performance. Dynamical decoupling (DD) tech-niques [5, 6] provide a powerful method to mitigate such effects [7–11], but typically at the expense of increased con-trol complexity and experimental overhead. Trapped-ion systems offer a leading architecture for quantum infor-mation processing due to their long coherence times and high-fidelity operations. In these systems, ions are con-fined by static and radio-frequency electric fields, forming linear crystals whose collective motion can be described in terms of quantised normal modes. Selected motional modes serve as a quantum data bus that mediates en-tangling interactions b
```

（实测观察：markdown 输出保留了科学记数法的数字精度（"7.4 × 10-2"、"5 × 10"等），正文段落结构完整；但本次 6 页 PRL 未输出结构化表格与 LaTeX 公式块——Table I 的内容以行文形式存在。对页码锚定阅读而言，PyMuPDF 纯文本已够用；Uni-Parser 的增量价值在公式密集的长文与跨页表格，选型建议见正文第 8 章。）

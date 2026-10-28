# 玻尔科学空间 + bohr CLI 文献阅读教程（零基础版）

> **写给谁**：会用终端、有一个 Bohrium（玻尔）账号、想让 AI 帮你读论文但怕被 AI 骗的科研人。不需要任何编程背景——所有命令都可以直接复制。
> **本教程的承诺**：每一个命令、价格、字段名、task_id、耗时都来自真实运行记录（实测环境见下表）。没跑通的地方，明确写「未实测」或「宣传未兑现」，不编。
> **总花费**：跑完整套教程 ≈ **2.3 元人民币**（LKM extract 1 元 ×1 篇 + Uni-Parser 0.3 元 + LKM search 走月度免费额度），另加模型网关按 token 计费（一篇论文精读量级约几毛到几元）。

| 实测环境指纹 | 值 |
|---|---|
| bohr CLI 版本 | `2.8.3`（commit `6aa0b66fa5e80d4ebd8cf34bc01395a353ca297d`，built `2026-10-23`，darwin/arm64） |
| npm 包 | `@dptech-corp/bohr-cli`（包版本 2.7.1，实际二进制由包管理器下载并自更新到 2.8.3） |
| Agent 宿主 | pi-coding-agent `1.3.0` |
| 实测日期 | 2026-10-27（LKM/Uni-Parser）、2026-10-28（CLI 帮助与内嵌指南复核） |
| 案例论文 A | Belyi et al., *Host–virus interactions dominate fitness and conceal additive genetic variation*, PLOS Biology 2026，**29 页** |
| 案例论文 B | Faorlin et al., *Entangling ions with engineered light gradients*, PRL（Dated: March 24, 2026），**6 页** |
| 案例论文 C（被拒） | Adamczewski & Faverjon, *Mahler's Method in Several Variables and Finite Automata*, Annals of Mathematics，**52 页** |

---

## 0. 五分钟看懂：四个产品各干什么、各花多少钱

玻尔（Bohrium）是深势科技的科研云平台总品牌。**玻尔·科学空间**（bohrium.com/bohrscience）是面向"人类对话"的统一前台：你提研究问题，SciMaster / BioMaster / MatMaster / PharmMaster 帮你检索、拆解、执行、写作、审查。而 **bohr CLI 与 OpenAPI 是同一套底座的"程序化开放层"**——UI 里能做的事，命令行里能复现、能量化、能写进脚本。

本教程走的是命令行这条路，用到四个产品：

| 阶段 | 产品 | 一句话职责 | 单价（内嵌价目表口径） | 本教程实测花费 |
|---|---|---|---|---|
| 读前解析 | **Uni-Parser**（`bohr pdf parse`） | PDF → 结构化文本/表格/公式 | **0.05 元/页**（成功解析才计费，取结果免费） | 0.30 元（6 页 PRL） |
| 读中推理 | **模型网关**（`open.bohrium.com/openapi/model-gateway/v1`） | 一个 OpenAI 兼容端点接入多个大模型 | 按 token（见 §5.6 价目） | 视用量 |
| 读后核查 | **LKM extract**（`bohr lkm extract`） | 把论文拆成「主张—前提—推理链」图，并自动标注每条主张**什么时候会失效** | **1.00 元/篇**（命中缓存 0.10 元） | 1.00 元 ×2 篇 |
| 跨文献定位 | **LKM search**（`bohr lkm search`） | 在已入库文献里做 claim/question 级**语义**检索 | **0.05 元/次**，个人每月 **1000 次免费额度**优先抵扣 | 0 元（走额度） |

> 价格核对命令（版本匹配的权威口径，见 §1.6）：
> ```bash
> bohr billing pricing --resource lkm -o json
> bohr billing pricing --resource pdf -o json
> ```

**为什么值得花这几块钱**：AI 读论文最大的风险不是"说错"，而是"漏掉"——一份结构完整、页码齐备的简报，可能整段跳过证明主体，而你对"没读"零感知。LKM 的 `failure_mode`（失效条件）字段提供了一个**与你的阅读流程原理完全独立**的第二意见：它逐条主张回答"这条断言在什么情况下不成立"。两套独立方法在同一批主张上报警，交集就是高置信度的误读风险点。

---

## 1. 安装与登录 bohr CLI

### 1.1 我做了什么（真实数据）

在 macOS（arm64）上用 npm 全局安装，`bohr version` 返回 2.8.3；随后 `bohr auth login` 走浏览器 SSO 完成登录，`bohr auth whoami` 可查身份。本教程所有后续命令都在这个登录态下运行，返回 JSON 的 `meta.cli_version` 字段均为 `2.8.3`（可用于你自查是否与我同一版本契约）。

### 1.2 你的复现命令

```bash
# ① 安装（需要 Node.js；npm 会顺带下载对应平台的二进制）
npm install -g @dptech-corp/bohr-cli

# ② 验证
bohr --version          # 人读版
bohr version -o json    # 机器读版，含 commit 与构建时间

# ③ 登录：三选一
bohr auth login                          # A. 默认：复用会话或打开浏览器 SSO（本机最省事）
bohr auth login --ak <你的AccessKey>      # B. 用 AccessKey 直接换凭证（脚本/CI 常用）
bohr auth login --device                 # C. 设备码流程（SSH、Codespaces、无显示器的 Linux）

# ④ 确认登录态
bohr auth status -o json
bohr auth whoami -o json

# ⑤ 环境体检（出问题先跑这个）
bohr doctor
```

AccessKey 在 Bohrium 网页端「用户设置 → 账号」页生成：https://www.bohrium.com/settings/account

无头环境（agent runner / 纯 SSH）推荐两步设备码流程，不会把浏览器卡死：

```bash
bohr auth login --device --no-wait --json   # 返回 verification URL 与 device_code
bohr auth login --resume                    # 在浏览器完成授权后，恢复这条挂起的登录
```

多账号/多环境用 profile 隔离（每个 profile 各自持有 AccessKey 与会话）：

```bash
bohr profile use <name>        # 切换默认 profile
bohr lkm search "..." -p <name> --yes   # 或只对单次调用覆盖
```

如果你还要用官方 Agent Skills（Claude Code / OpenClaw 等）或直接打 OpenAPI，沿用同一个环境变量名，一把 Key 驱动全部：

```bash
export BOHR_ACCESS_KEY="你的 AccessKey"   # 官方 bohrium-skills 生态的约定变量名
```

### 1.3 预期输出样例

```console
$ bohr --version
bohr version 2.8.3

$ bohr version -o json
{
  "ok": true,
  "data": {
    "arch": "arm64",
    "built": "2026-10-23T12:23:17Z",
    "commit": "6aa0b66fa5e80d4ebd8cf34bc01395a353ca297d",
    "go": "go1.26.0",
    "modified": false,
    "os": "darwin",
    "version": "2.8.3"
  },
  "meta": { "cli_version": "2.8.3", "command": "bohr version", "duration_ms": 0 }
}
```

登录后，**每个返回体都带这三层信封**，后面各章都靠它自查：

```json
{ "ok": true, "data": { ... }, "notice": { "billing": {...} }, "meta": { "request_id": "...", "cli_version": "2.8.3", "command": "...", "duration_ms": 708, "timestamp": 1793110934 } }
```

- `ok` / `data`：成功与否与业务数据；
- `notice.billing`：**这次调用怎么扣的钱**（`channel` 为 `photon` 光子 / `balance` 余额 / `quota` 免费额度）；
- `meta.request_id`：报障时给官方的唯一凭据；`meta.command`：确认这条记录是哪条命令产生的。

### 1.4 花钱前必看：计费、配额与"确认门"

bohr 把会花钱的命令标记为 `[write]`，交互模式下会先弹确认；脚本/agent 里要显式加 `--yes` 才执行（否则会拿到 `CONFIRMATION_REQUIRED`）。**`--yes` 只是"我确认执行"，不等于授权换扣费渠道。**

扣费渠道规则（内嵌指南原文口径）：

- 不加 `--payment-source`：**光子优先，光子明确不足时才回落余额**；
- `--payment-source photon`：只花光子，不足即停（`BILLING_INSUFFICIENT`，`retryable: false`）；
- `--payment-source balance`：只花余额，不足即停，不会偷偷去扣光子；
- 多步工作流里，**上一次的选项不会被记住**，每条计费命令都要重新带上。

自查钱包与价目：

```bash
bohr billing balance -o json       # 余额
bohr billing photon -o json        # 光子余额与消耗历史
bohr billing ledger -o json        # 账单流水（对账用）
bohr billing pricing --resource lkm -o json
bohr billing pricing --resource pdf -o json
bohr billing recharge              # 浏览器打开充值页
```

LKM 查询类命令（`search` / `reasoning` / `graph` / `reference` / `variables batch` / `claim reasoning`）各 **0.05 元/次**，但**个人每月 1000 次额度优先抵扣**——所以日常做文献检索基本是免费的。实测证据（§3.2 那次 search 的 `notice`）：

```json
"notice": { "billing": { "channel": "quota", "resource": "lkm", "remaining": 997 } }
```

而 **extract 不吃这个月度额度**：1.00 元/篇（缓存命中 0.10 元），实测走的是光子：

```json
"notice": { "billing": { "channel": "photon" } }
```

> 省钱的两个真实机制：①同一篇 PDF 重复提交不会重复扣费（`cache_hit=true` 时只收 0.10 元，`cache_source` 会告诉你是 `lkm` 语料库已有还是 `local` 你之前提交过）；②`extract result` 只对**每个 task_id 的第一次成功取回**计费。

### 1.5 想少花钱先空跑：`--dry-run`

`--dry-run` 只校验输入、不发请求、不产生费用，也会绕过计费确认门：

```bash
bohr pdf parse --file ./paper.pdf --dry-run          # 只打印将要走的输入路径
bohr lkm extract submit ./paper.pdf --dry-run
```

### 1.6 CLI 自带权威文档：`bohr guide`（强烈建议零基础用户先读）

CLI 二进制里**内嵌了与自身版本匹配的操作指南**（比网上任何第三方教程都准，因为它随版本一起发布）：

```bash
bohr guide list                                   # 列出内嵌技能（24 个，含 bohr-lkm / bohr-pdf-parse）
bohr guide read bohr-lkm                          # LKM 总纲：命令选型、计费、状态机
bohr guide read bohr-lkm references/commands.md   # LKM 逐命令字段级参考
bohr guide read bohr-pdf-parse                    # Uni-Parser 总纲
bohr guide read bohr-pdf-parse references/commands.md
```

本教程的价格、页数上限、状态名、错误码全部与 `bohr guide`（2.8.3）逐条对齐。你也可以随时用 `bohr <命令> --help` 看当前版本的 flag。

### 1.7 安装登录常见坑

| 现象 | 原因 | 修法 |
|---|---|---|
| `bohr: command not found` | npm 全局 bin 不在 PATH | `npm bin -g` / `npm prefix -g` 查路径并加入 PATH |
| 版本号与教程不符 | 二进制未更新 | `bohr update`，再 `bohr version` |
| `CONFIRMATION_REQUIRED` | 计费命令未确认 | 确认花费后加 `--yes`；或先 `--dry-run` |
| `BILLING_INSUFFICIENT`（`retryable:false`） | 指定渠道钱不够 | 充值，或**在获得授权后**换 `--payment-source`；不要重复提交任务 |
| SSH 里登录卡住 | 无浏览器 | `bohr auth login --device --no-wait --json` → `bohr auth login --resume` |
| 命令能跑但结果诡异 | 版本与文档不匹配 | 用 `bohr guide read <skill>` 读**本机版本**的指南，而不是网上的旧文 |

---

## 2. LKM extract：把一篇论文拆成「主张 + 失效条件」

### 2.1 它是什么

LKM = Large Knowledge Model（大知识模型）。`extract` 接收一个**本地 PDF**，异步跑一条流水线，产出一张可寻址的知识图：研究问题（question）、主张（claim）、推理链（factor）、动机（motivation），并且——这是最值钱的部分——为脆弱主张自动标注 **`failure_mode`：这条断言在什么条件下不成立**，外加 `weak_types`（弱点类型）与 `refs`（主张挂靠在哪些公式/图/表上）。

`bohr lkm` 官方选型提示（`bohr lkm --help` 原文摘要）：

```
a local PDF that may not be in LKM  →  extract
search is not bohr paper search (keyword papers).
extract is not bohr pdf parse (Uni-Parser layout, text, tables, formulas).
```

一句话：**要"论文的版面内容"用 `bohr pdf parse`；要"论文的知识结构"用 `bohr lkm extract`。**

### 2.2 我做了什么（真实数据）

2026-10-27 对两篇论文各跑一次 extract，两次都 `status=succeeded`、`cache_hit=false`：

| | 论文 A：PLOS Biology（宿主—病毒互作，29 页） | 论文 B：PRL（离子阱光梯度纠缠，6 页） |
|---|---|---|
| `task_id` | `fdf24d62-f293-48d2-8fe5-dda9bd5c16de` | `3ad2e06c-9f20-4c53-a10d-019ff0ffd18d` |
| 主张 claim | **60** | **27** |
| 研究问题 question | **35** | **20** |
| 推理链 factors | **26** | **9** |
| 动机 motivations | **26** | **9** |
| `variables_total` | **95** | **47** |
| 带 `failure_mode` 的主张 | **25 / 60** | **13 / 27** |
| 全流程耗时 | **12.65 分钟** | **12.26 分钟** |
| 计费渠道 | photon（1.00 元/篇） | photon（1.00 元/篇） |
| `meta.request_id` | `90404d92-b24a-444f-840e-b679a71699fd` | — |

耗时不是我掐表估的，是返回体里 `step_durations` 逐步记录的（论文 A 原文）：

```json
"step_durations": [
  { "step": "ocr",    "duration_ms": 50264  },
  { "step": "step0",  "duration_ms": 4708   },
  { "step": "step1",  "duration_ms": 173340 },
  { "step": "step2",  "duration_ms": 181486 },
  { "step": "step3",  "duration_ms": 259676 },
  { "step": "step4",  "duration_ms": 89245  },
  { "step": "graph",  "duration_ms": 374    }
]
```

即 **OCR 预处理 → step0–step4 五段抽取 → graph 图构建**，合计 759.9 秒 ≈ 12.7 分钟。官方口径是"约 10 分钟量级"，两篇实测都略高于 10 分钟——**做批量脚本时请把超时设到 30 分钟**（`--timeout` 默认值就是 30m）。

最有价值的一条主张长这样（论文 A 的 `variables[0]`，字段有删节）：

```json
{
  "local_id": "paper:6649::P1",
  "type": "claim",
  "title": "Single sex-symmetric transmission rate in the full model",
  "content": "... each infected parent transmits the pathogen to a fraction $t$ of its gametes ... giving an effective transmission rate $t(1-r)$ ... Eq. (1) Fig. 9",
  "metadata": {
    "failure_mode": "If sexual asymmetry in transmission is functionally important for the partition of fitness variance, the model's central prediction that host×virus interaction variance dominates is established for an averaged transmission trait that corresponds to neither the maternal nor the paternal route ...",
    "weak_types": ["model", "measurement"],
    "refs": [ { "type": "equation", "text": "Eq. (1)" }, { "type": "figure", "text": "Fig. 9" } ]
  },
  "global_id": null,
  "ingest_status": "local",
  "content_hash": "1415fc19...",
  "created_at": "2026-10-27T13:46:02Z",
  "version": "2.0.0",
  "visibility": "public"
}
```

译成人话：全模型假设病毒经卵与经精液的传播速率相同（单一参数 *t*），而论文自己的实测是母传约 85%、父传约 26%、跨性遗传相关仅 0.34。**若这个对称假设在功能上重要，"互作方差主导"的核心预测就挂在一条既非卵路也非精路的平均性状上。** 结论未必错，但适用范围有裂缝——这正是人工精读要抓的东西，LKM 自动帮你标出来了。

论文 B（PRL）同类的一条，直接决定结论能不能外推：

```
local_id: paper:6650::P5
title:    Error budget pertains to an eight-ion crystal
weak_types: ["measurement", "generalization"]
refs:     [{ "type": "figure", "text": "Table I" }]
failure_mode: If the budget in fact corresponds to a two-ion crystal, then extrapolating its
  spectator-mode and heating figures to the eight-ion operating point overstates the favorable
  regime, and the axial-versus-radial comparison is demonstrated at the wrong chain length,
  narrowing the claim that the advantage holds at the roughly twelve-ion operating point.
```

论文 A 的 25 条 `failure_mode` 按 `weak_types` 统计（真实分布，一条主张可带多个标签）：

| weak_type | 条数 | 读法 |
|---|---|---|
| `statistical` | 12 | 统计口径/样本/检验层面的弱点 |
| `model` | 8 | 模型假设层面的弱点 |
| `measurement` | 7 | 测量与仪器层面 |
| `generalization` | 4 | 结论外推范围 |
| `causal` | 4 | 因果推断 |
| `external` | 3 | 外部效度 |
| `computational` | 1 | 计算/数值层面 |

**这张分布表本身就是一份"该往哪儿追问"的地图**：这篇论文的软肋集中在统计口径与模型假设，而不是计算实现。

### 2.3 你的复现命令

```bash
# ① 提交（--wait 会阻塞轮询到终态；不加则立刻返回 task_id）
bohr lkm extract submit ./host-virus-plos-bio.pdf --yes -o json
bohr lkm extract submit ./paper.pdf --wait --interval 5s --timeout 30m -o json

# ② 查状态（拿到 task_id 后随时查，可反复查，免费）
bohr lkm extract status <task_id> -o json

# ③ 等它跑完（本地轮询，不影响远端任务）
bohr lkm extract wait <task_id> --interval 5s --timeout 30m -o json

# ④ 取结果（默认扁平图：variables / factors / motivations / stats）
bohr lkm extract result <task_id> --yes -o json > lkm.json

# ⑤ 或者取"图"形态（nodes/edges + addressed_problems + open_questions）
bohr lkm extract result <task_id> --format graph --yes -o json > lkm_graph.json

# ⑥ 只看统计（-q 是 CLI 内置的 jq 风格路径过滤，不是完整 jq）
bohr lkm extract result <task_id> --yes -q data.stats -o json
```

**输入约束**（超限直接被拒，见 §2.7）：必须是常规非空文件、`.pdf` 扩展名、`%PDF` 文件头、**≤ 64 MiB**、**≤ 50 页**。提交本身可能要花到 5 分钟（上传 + 排队）。

### 2.4 预期输出样例

提交成功（示意结构，字段名来自 2.8.3 内嵌参考）：

```json
{ "ok": true,
  "data": { "task_id": "fdf24d62-f293-48d2-8fe5-dda9bd5c16de",
            "status": "queued", "pdf_md5": "...",
            "cache_hit": false, "cache_source": null } }
```

`status` 运行中：

```json
{ "data": { "task_id": "fdf24d62-.

---

*（完整教程见 GitHub 仓库 bohrium-workflow/bohrium_tutorial.md，此处保留安装与核心命令段）*

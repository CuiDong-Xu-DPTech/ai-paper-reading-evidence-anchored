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
{ "data": { "task_id": "fdf24d62-...", "status": "running", "stage": "step2",
            "step_durations": [ { "step": "ocr", "duration_ms": 50264 }, ... ] } }
```

`result` 成功（论文 A 实测，节选）：

```json
{
  "ok": true,
  "data": {
    "task_id": "fdf24d62-f293-48d2-8fe5-dda9bd5c16de",
    "status": "succeeded",
    "cache_hit": false,
    "stats": {
      "factors_total": 26,
      "motivations_total": 26,
      "type_counts": { "claim": 60, "question": 35 },
      "variables_total": 95
    },
    "step_durations": [ ... 见 §2.2 ... ],
    "variables":    [ ... 95 条（60 claim + 35 question） ... ],
    "factors":      [ ... 26 条推理链 ... ],
    "motivations":  [ ... 26 条动机 ... ]
  },
  "notice": { "billing": { "channel": "photon" } },
  "meta": { "request_id": "90404d92-b24a-444f-840e-b679a71699fd",
            "cli_version": "2.8.3", "command": "bohr lkm extract result",
            "duration_ms": 609, "timestamp": 1793109019 }
}
```

### 2.5 结果字段解读（三张表看懂 lkm.json）

**顶层 `data`**：

| 字段 | 含义 | 你该怎么用 |
|---|---|---|
| `task_id` | 任务 ID（不透明字符串） | 唯一凭据，存下来；`status`/`wait`/`result` 都靠它 |
| `status` | `queued`/`running`/`succeeded`/`partial`/`failed` | 只有后三个是终态，见 §2.6 |
| `cache_hit` | 是否复用了已有抽取 | `true` 时只扣 0.10 元；仍要按 `status` 分支处理 |
| `cache_source` | `lkm`=语料库已有；`local`=你之前提交过同一文件 | 判断"这篇是不是早被别人抽过" |
| `pdf_md5` | 提交文件的指纹 | 确认抽的是你以为的那份 PDF |
| `step_durations` | 各阶段耗时（ms） | 性能可复查；批量任务用来估算等待预算 |
| `stats` | `type_counts` / `variables_total` / `factors_total` / `motivations_total` | 一眼看规模，也是你写报告时的引用数字 |
| `variables` | 主张 + 问题的扁平列表 | **主战场**，见下表 |
| `factors` | 推理链（含 `background`/`premises`/`steps`/`conclusion`/`factor_type`/`subtype`） | 想看"怎么推出来的"看这里 |
| `motivations` | 动机（`question_content` + `targets`，指向 `question_local_id`） | 想看"为什么要做"看这里 |

**`variables[]` 每条**：

| 字段 | 含义 | 注意 |
|---|---|---|
| `local_id` | 形如 `paper:6649::P1` 的**本次抽取内**局部 ID | 只在这份结果里有效；`factors`/`motivations` 用它做交叉引用 |
| `global_id` | 全局 ID（`gcn_...`），**可能为 null** | 实测两篇都是 `null`（`ingest_status: "local"`）——**只有非 null 才能拿去 `variables batch` / `claim reasoning`** |
| `type` | `claim`（主张）或 `question`（研究问题） | 论文 A：60 / 35 |
| `title` | 一句话主张标题 | 做清单时最好用的字段 |
| `content` | 主张全文，**含 LaTeX 数学**（如 `$t_{i,G}=t_i(1-r\cdot 1_{i,G})$`），末尾附证据锚（`Eq. (1)`、`Fig. 9`） | 直接可喂给模型；也是与原文对账的对象 |
| `content_hash` | 内容指纹 | 跨运行去重/对账 |
| `metadata` | **JSON 字符串**（不是对象！），内含 `failure_mode` / `weak_types` / `weakness_reason` / `refs` | 需要二次 `json.loads()`，这是最容易踩的坑 |
| `ingest_status` | `local` = 仅本次抽取，未入全局语料库 | 解释为什么 `global_id` 是 null |
| `version` / `visibility` / `created_at` | 抽取器版本（实测 `2.0.0`）、可见性、时间戳 | 复现声明用 |

**`metadata`（解析后）**：

| 字段 | 含义 | 阅读工作流里的用法 |
|---|---|---|
| `failure_mode` | **失效条件**：满足什么条件时这条主张不成立 | 逐条对照 AI 报告：报告有没有把这个限定说出来？ |
| `weak_types` | 弱点类型数组（`statistical`/`model`/`measurement`/`generalization`/`causal`/`external`/`computational`/`comparative`/`formal`） | 决定"该用哪张学科检查单去追问" |
| `weakness_reason` | 弱点理由 | 比 `failure_mode` 更短的诊断 |
| `refs` | 证据锚：`{type: equation/figure/table, text: "Eq. (1)"}` | 回原文核对时的定位器 |

### 2.6 状态机与错误码（照着分支写脚本）

| `status` | 终态？ | 动作 |
|---|---|---|
| `queued` | 否 | 留好 task_id，继续等 |
| `running` | 否 | 看 `stage` 与已完成的 `step_durations`，继续等 |
| `succeeded` | **是** | 读结果（第一次成功取回才计费） |
| `partial` | **是** | 业务性终态，**不可重试**：看失败原因/中间文件，**不要把同一 PDF 再提交一遍** |
| `failed` | **是** | 技术性终态：查原因后**可以**重新提交 |

| 错误/信号 | 含义 | 动作 |
|---|---|---|
| `290017` / `LKM_PARSE_RESULT_NOT_READY` | 结果还没好 | 继续等**同一个** task_id，别重新提交 |
| `290020` | 同一文件已有任务在跑 | 返回体里带既有 task_id，接着轮询它；**重复提交不会加速** |
| `LKM_PARSE_WAIT_TIMEOUT` / `LKM_PARSE_WAIT_CANCELLED` | 只是**本地**轮询停了 | 远端任务没被取消，用同一 task_id 继续 `status`/`wait`/`result` |
| `7002` 且 `retryable: true` | 首次取回计费撞并发 | 延迟后用**同一 task_id、同一支付渠道**重试 |
| `BILLING_INSUFFICIENT`（`retryable:false`，可能带 subtype 7002） | 光子不足 | 停下充值或改授权渠道；**不要为绕过计费而重新提交 PDF** |
| `partial`/`failed` 结果里的 `files` URL | 中间产物，**带过期凭证** | 只用于本次恢复，**不要贴进聊天记录或日志** |

### 2.7 真实边界：52 页论文被拒（这条一定要看）

把 52 页的 Annals of Mathematics 长文（Adamczewski & Faverjon, *Mahler's Method in Several Variables and Finite Automata*）提交 LKM extract，**被拒：超出 50 页上限**。CLI 内嵌指南与 `--help` 都写明了这个限制：

```
bohr lkm extract submit --help:
  Upload a PDF and queue it for LKM knowledge extraction. The file must be a PDF
  of at most 64 MiB; the service also limits a paper to 50 pages.
```

这不是事故，是**方法的适用边界**，必须和收益一起公布：

- **LKM extract 适用于 ≤50 页的论文**；超长文（数学专著式论文、含大量附录的 preprint）请改走本地路线：PyMuPDF 导出带页码文本（无页数限制、零成本，见 §4.6）+ 分段精读 + 锚点程序校验；
- 也可以**先切分**：把主文（≤50 页）单独导出提交，附录另行处理——但要清楚你抽的是"半个论文"，`stats` 的规模会偏小，交叉验证结论也要相应限定；
- 反过来，6 页的 PRL 短文抽取质量并不打折（27 主张 / 13 失效模式，比例甚至高于 29 页的生物论文）——**页数不是质量的决定因素，50 页是硬闸门。**

> 顺带一个诚实提醒：这次被拒的 52 页论文，恰好也是我们观察到 AI"跳读证明主体"最严重的那篇（模型只读了 3 个行区间，第 30–38 页的证明主体从未进入上下文，报告却照常输出结论）。**LKM 帮不了你这种情况**——超长文的质量门只能靠本地分页导出 + 覆盖率自查（§4.6）。

### 2.8 抽完之后怎么用：把 60 条主张当"追问清单"，而不是当分数

拿到 `lkm.json` 后最自然的想法是"数一数 AI 报告覆盖了多少条主张"。我们真做了这个实验，结果反直觉：

| 报告 | 人工双盲评估（30 分制） | LKM 主张覆盖 | 高危主张覆盖（25 条带 failure_mode） |
|---|---|---|---|
| 加载了阅读流程的报告 | **30/30（满分）** | 21/60（35%） | 5/25 |
| 裸跑对照报告 | 27/30 | **24/60（40%）** | **7/25** |

**对照组在"覆盖广度"上反而略高。** 结论：LKM 覆盖测的是**广度**（撒到了多少主张上），人工评估测的是**关键事实命中 + 论证规范 + 结构纪律**。裸跑报告像广撒网：触及更多主张但浅、缺边界讨论。

所以正确用法有两条：

1. **不要用"覆盖了多少条主张"单独评价一份 AI 审读报告**（会奖励广撒网）；
2. **把主张清单反过来当阅读/追问清单**：读完 AI 报告，把**未覆盖的高危主张**（带 `failure_mode` 的那些，例如 "Sharp sensitivity of the dynamical regime to parameter values" 的参数敏感性失效条件）作为追问清单丢回给 AI 补查。这是 LKM 在日常文献阅读里性价比最高的用法。

> 该覆盖判定实验的局限也要说清：判定模型与被评报告的运行模型同为 glm-5.3（非盲）、n=1 对报告，属**观察性发现**而非统计结论。

### 2.9 一段可复制的脚本：导出"高危主张追问清单"

注意 `metadata` 是 **JSON 字符串**，必须二次解析（这是最常见的报错来源）：

```python
#!/usr/bin/env python3
"""从 bohr lkm extract result 的 JSON 里导出带 failure_mode 的主张清单。"""
import json, sys, collections

d = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "lkm.json"))["data"]
print(f"task_id={d['task_id']}  status={d['status']}  cache_hit={d['cache_hit']}")
print("stats:", json.dumps(d["stats"], ensure_ascii=False))
print("耗时(分):", round(sum(s["duration_ms"] for s in d["step_durations"]) / 60000, 2))

wt = collections.Counter()
rows = []
for v in d["variables"]:
    md = json.loads(v["metadata"] or "{}")        # ← metadata 是字符串！
    for t in md.get("weak_types") or []:
        wt[t] += 1
    if v["type"] == "claim" and md.get("failure_mode"):
        refs = ", ".join(r["text"] for r in md.get("refs") or [])
        rows.append((v["local_id"], v["title"], ",".join(md.get("weak_types") or []), refs,
                     md["failure_mode"]))

print(f"\n带 failure_mode 的主张：{len(rows)} 条；weak_types 分布：{dict(wt)}\n")
for lid, title, wts, refs, fm in rows:
    print(f"- [{lid}] {title}\n    弱点类型: {wts} | 证据锚: {refs}\n    失效条件: {fm}\n")
```

```bash
python3 dump_failure_modes.py lkm.json > failure_modes.md
# 预期输出（论文 A 实测）：带 failure_mode 的主张：25 条；
# weak_types 分布：{'statistical': 12, 'model': 8, 'measurement': 7,
#                   'generalization': 4, 'causal': 4, 'external': 3, 'computational': 1}
```

---

## 3. LKM search：跨文献语义检索已入库论文的主张

### 3.1 它和"搜论文"有什么不同

`bohr lkm search` 搜的不是论文标题/摘要关键词，而是**已入库文献里的知识单元**（claim / premise / conclusion / question / abstract / reasoning_chain）。返回的是**结构化的主张文本**，不是原文片段——相当于自动化的"引文上下文比对"，但比 scite.ai 那类 citation context 更进一步：你拿到的是可寻址的 claim（带 `gcn_` 全局 ID，可继续往下钻推理链）。

官方明确区分（`bohr lkm search --help`）：`This is not bohr paper search.`
- 想找论文/专利本身 → `bohr paper search`
- 想找"某概念在别人论文里是怎么被断言的" → `bohr lkm search`
- 想找"类似的推导/实验过程" → `bohr lkm reasoning`

### 3.2 我做了什么（真实数据）

2026-10-27 跑了一次跨文献检索：

```bash
bohr lkm search "host virus interaction fitness genetic variance" --yes -o json
```

实测结果（`meta` 原文可查）：

| 指标 | 实测值 |
|---|---|
| `ok` | `true` |
| 命中知识变量 `data.variables` | **10 条** |
| 涉及论文 `data.papers` | **10 篇**（每篇一条代表命中） |
| `data.has_more` | **`true`**（还有下一页，`--offset` 翻页，上限 2000） |
| 耗时 `meta.duration_ms` | **708 ms** |
| `meta.request_id` | `6f68c449-7301-4acd-b73c-336fbb4e410c` |
| 计费 `notice.billing` | `{"channel":"quota","resource":"lkm","remaining":997}` → **本次走月度免费额度，实付 0 元** |

### 3.3 你的复现命令

```bash
# 最简：自然语言查询（默认 mode=hybrid、sort=comprehensive、top-k=10、scopes=conclusion+abstract）
bohr lkm search "host virus interaction fitness genetic variance" --yes -o json

# 只搜"结论型主张"（下一步想追推理链时选这个，因为只有 conclusion 可能带 reasoning）
bohr lkm search "遗传方差分解" --scopes conclusion --top-k 20 --yes -o json

# 语义 + 关键词混合，按时间新到旧
bohr lkm search "trapped-ion entangling gate infidelity" \
  --keywords "spectator mode,axial,radial" --mode hybrid --sort recent --yes -o json

# 按 DOI / 论文 ID / 日期窗过滤（三类过滤器之间是 AND）
bohr lkm search "solid-state battery" \
  --doi 10.1038/s41586-021-03381-x \
  --publication-date-start 2020-01-01 --publication-date-end 2026-12-31 \
  --yes -o json

# 翻页
bohr lkm search "..." --top-k 50 --offset 50 --yes -o json

# 免费空跑（不发请求、不计费、不需 --yes）
bohr lkm search "..." --dry-run
```

常用 flag 速查（默认值来自 2.8.3 `--help`）：

| flag | 默认 | 说明 |
|---|---|---|
| `--scopes` | 服务默认 = `conclusion,abstract` | 可选 `abstract\|claim\|premise\|conclusion\|question\|problem\|open_question\|subproblem\|reasoning_chain`；`claim` 含 premise+conclusion，`question` 含 problem/open_question/subproblem |
| `--mode` | `hybrid` | `semantic` / `lexical` / `hybrid` |
| `--sort` | `comprehensive` | `relevance` / `recent` / `journal` |
| `--top-k` | 10 | 1–100 |
| `--offset` | 0 | ≤2000 |
| `--keywords` | 空 | 逗号分隔，≤10 个、每个 ≤100 字节；**别把整句查询塞进来** |
| `--paper-id` / `--doi` / `--title` | 空 | 可重复（各 ≤50），三者 AND；`--paper-id` 是纯数字，**不带 `paper:` 前缀** |
| `--publication-date-start/end` | 空 | `YYYY-MM-DD` |
| `--limit-publication-date` | `true` | 设 `false` 才包含无日期的论文 |
| `--include-paper-enrich` | 关 | 需要更富的论文元数据时打开 |
| `--visibility` | `public` | 可见性过滤 |

### 3.4 预期输出样例（真实命中，未改标题）

人读版摘要（10 条命中，按返回顺序）：

| # | kind / role | 命中标题 | rerank_score | has_reasoning | 所属论文（DOI） |
|---|---|---|---|---|---|
| 1 | conclusion / conclusion | Explanatory features explain little pleiotropic variance | 0.908 | ✅ | *Quantifying the strength of viral fitness trade-offs between hosts: a meta-analysis of pleiotropic fitness effects*（10.1093/evlett/qrae038，2024，中科院 1 区） |
| 2 | weak_point / premise | Generality of target-vs-non-target variance differential | 0.873 | ❌ | *Evolution of Phenotypic Plasticity under Host-Parasite Interactions*（10.1101/2021.01.20.427416） |
| 3 | conclusion / conclusion | Genotype-by-host interaction explains majority of fitness variance | **0.967** | ✅ | *Effect of Host Species on the Distribution of Mutational Fitness Effects for an RNA Virus*（10.1371/journal.pgen.1002378，2011） |
| 4 | abstract 级命中 | Do Coinfections Maintain Genetic Variation in Parasites? | 0.864 | — | 10.1016/j.pt.2016.08.010（2016） |
| 5 | abstract 级命中 | Plant RNA virus fitness predictability: contribution of genetic and environmental factors | 0.961 | — | 10.1111/ppa.12102（2013） |
| 6 | abstract 级命中 | Evolution of phenotypic fluctuation under host-parasite interactions | 0.858 | — | 10.1371/journal.pcbi.1008694（2021） |
| 7 | abstract 级命中 | Cucumber mosaic virus infection as a potential selective pressure on *Arabidopsis thaliana* populations | 0.868 | — | 10.1371/journal.ppat.1007810（2019） |
| 8 | conclusion / conclusion | Genotype explains most fitness variance; host main effect is small but genotype×host interaction is large | 0.943 | ✅ | *Effect of Host Species on Topography of the Fitness Landscape for a Plant RNA Virus*（10.1128/jvi.01243-16，2016） |
| 9 | conclusion / conclusion | The nested infection pattern … supports a gene-for-gene model | 0.918 | ✅ | 10.1098/rstb.2014.0292（2015） |
| 10 | abstract 级命中 | Genotype-specific interactions and the trade-off between host and parasite fitness | 0.932 | — | 10.1186/1471-2148-7-189（2007） |

第 1 条命中的原始 JSON（字段全貌，内容略缩）：

```json
{
  "id": "gcn_49df19dda13f4e6b",
  "type": "claim", "kind": "conclusion", "role": "conclusion",
  "title": "Explanatory features explain little pleiotropic variance",
  "content": "After controlling for study-level random effects in mixed-effect models, the considered explanatory features, including mutation type, viral genome type, protein class, envelope status, and divergence time interactions, collectively explained a small fraction of variance in pleiotropic magnitude (fixed effects marginal $R^2 \\approx 10.2\\%$) ...",
  "score": 0.015873015873015872,
  "rerank_score": 0.908319637431946,
  "has_reasoning": true, "has_evidence": true,
  "provenance": {
    "representative_lcn": { "local_id": "paper:1039382379048730664::conclusion_5",
                            "package_id": "paper:1039382379048730664", "version": "2.0.0" },
    "source_packages": ["paper:1039382379048730664"]
  },
  "related": [ { "id": "gcn_fd9f6f3639724162", "kind": "conclusion",
                 "title": "Bacteriophage host type and genome size predict single-host fitness",
                 "content": "... estimated coefficient for bacteria host = -1.761, p = 0.024 ...",
                 "has_reasoning": true, "score": 0.013888888888888888 } ],
  "visibility": "public"
}
```

对应的论文元数据（`data.papers["paper:1039382379048730664"]`）：

```json
{ "area": "biology, evolutionary biology",
  "authors": "Xuechun ‘May’ Wang | Julia Muller | Mya McDowell | David A Rasmussen",
  "doi": "10.1093/evlett/qrae038", "cas_zone": "1",
  "cover_date_start": "2024-07-29", "available_online": "2024-7-29",
  "en_title": "Quantifying the strength of viral fitness trade-offs between hosts: ..." }
```

### 3.5 字段解读

| 字段 | 含义 | 关键注意 |
|---|---|---|
| `data.variables[]` | 每篇论文一条**代表命中** | 不是"全部命中"，是分组后的代表 |
| `id` | 全局 ID：claim 类为 `gcn_...`；abstract 级命中直接是**数字论文 ID** | 两种 ID 用途完全不同，见下 |
| `kind` / `role` | `conclusion`（结论）/ `premise`（前提）/ `weak_point`（局限）/ `subproblem`（动机问题） | **三者不可互换**：`weak_point` 是局限，不是结论 |
| `type` | `claim` 等大类 | abstract 级命中可能没有 `kind`/`role`（实测第 4–7、10 条为空）——解析要防御式 |
| `score` / `rerank_score` | 检索排序信号 | **不是置信度、不是真实性概率、不是证据强度**（官方指南反复强调）。实测 `score` 都在 0.01 量级、`rerank_score` 在 0.86–0.97，两套数值不可比 |
| `has_reasoning` | 该 conclusion 是否有可追的推理链 | `true` 才能喂给 `claim reasoning` |
| `has_evidence` | 是否有证据挂载 | 决定能不能做"证据核对" |
| `content` | 主张全文，**含 LaTeX**（如 `$R^2 \approx 10.2\%$`） | 可直接作为跨论文表述对照 |
| `provenance` | 来源包（`paper:<digits>`）+ 代表局部 ID + 版本 | 溯源用；`paper:` 前缀只在 `graph --package-id` 时用 |
| `related[]` | **同篇论文**的其他上下文 | 官方明确：不是跨论文推荐，也不是完整论文图 |
| `data.papers` | 权威论文元数据（按 source package 键索引） | 含 `area`/`authors`/`doi`/`cas_zone`/日期 |
| `data.has_more` | 是否还有下一页 | 实测 `true` → 需要时 `--offset` 翻页 |

### 3.6 命中之后往下钻（ID 流转，别猜 ID）

```bash
# ① conclusion + has_reasoning=true → 追它的完整推理链
bohr lkm claim reasoning gcn_f9f369db5d034bb3 --format graph --yes -o json

# ② 数字论文 ID → 整篇论文的知识图（nodes/edges）
bohr lkm graph --paper-id 813359644108914688 --yes -o json
bohr lkm graph --doi 10.1371/journal.pgen.1002378 --yes -o json
bohr lkm graph --package-id paper:1039382379048730664 --yes -o json
bohr lkm graph --title "Effect of Host Species on the Distribution of Mutational Fitness Effects for an RNA Virus" --yes -o json

# ③ 看这篇论文引了谁 / 被谁引（返回论文卡片，不是图）
bohr lkm reference --paper-id 813359644108914688 --yes -o json

# ④ 批量水合全局 ID（1–100 个，先去 null 去重）
bohr lkm variables batch gcn_49df19dda13f4e6b gcn_f9f369db5d034bb3 --yes -o json

# ⑤ 想找"类似的推导/实验过程"而不是主张
bohr lkm reasoning --query "partition fitness variance into host, virus and interaction components" --top-k 10 --yes -o json
```

图的节点/边语义（读图必备）：`conclusion`=结论，`reasoning_steps`=推导/计算/实验，`highlight`=正面支撑，`weak_point`=局限或削弱性假设，`subproblem`=动机问题；边 `concludes`（推理步→结论）、`highlight_of`、`weakpoint_of`、`subproblem_of`。**总结时不要把 highlight / weak_point / subproblem 混成 conclusion。**

ID 使用红线（官方原文口径）：

- **不要从标题猜 ID**；只从结构化结果里取。
- `paper:` 前缀只有在 CLI 打印出规范化数字 Paper ID 时才可去掉。
- 图内局部 ID（如 `paper:...::conclusion_3`）只在那张图里有意义，**不能当全局 ID 用**。
- extract 产出的 `local_id` 只在那份结果里有效（这也是 §2.2 里 `global_id: null` 时不能跨命令使用的原因）。
- `reference` 里 `references`/`cited_by` 为 `null` = 没查这个列表；为 `[]` = 查了但空。**两者不是一回事。**

### 3.7 边界：只覆盖已入库文献

实测中，我们的案例论文（PLOS Biology 2026，尚未正式入库）**没有出现在检索结果里**。这就是 extract 与 search 的分工：

- **新论文 / 手头 PDF / 未入库文献** → `bohr lkm extract`（自己建图谱，1 元/篇）
- **已有文献库里的跨论文定位** → `bohr lkm search`（0.05 元/次，月度 1000 次免费额度）

另外三条使用纪律：①`abstract` 命中当**背景**用，不要当科学主张引用；②`score`/`rerank_score` 只排序，**不代表可信度**；③命中主题相关性高不等于结论可迁移——上表第 3、8 条都讲"基因型×宿主互作解释大部分适合度方差"，但对象分别是 RNA 病毒与植物 RNA 病毒，跨物种外推前要回原文核对口径。

---

## 4. Uni-Parser：PDF 结构化解析（`bohr pdf parse`）

### 4.1 我做了什么（真实数据）

用 `bohr pdf parse --file` 解析 6 页的 PRL 论文（*Entangling ions with engineered light gradients*），再用 `bohr pdf result <token> --formatted markdown` 取回 markdown。

- **费用**：0.3 元（6 页 × 0.05 元/页），取结果免费；
- **成功的部分**：标题、14 位作者、5 条单位信息、日期（Dated: March 24, 2026）、摘要与引言段落结构完整；**科学记数法的数字精度保留**（如 `5 × 10-3`、`7.4 × 10-2`）；
- **没兑现的部分（如实记录）**：这次 6 页 PRL **没有输出结构化表格，也没有独立的 LaTeX 公式块**——Table I 的内容以行文形式存在。也就是说，官方宣传的"文本/公式/表格三类结构化准确率 >98%"在这个样例上没有体现为"给我一张可用的表"。

### 4.2 你的复现命令

```bash
# ① 提交本地 PDF（--file 会把文件上传到 Bohrium，先确认这份文件可以外发）
bohr pdf parse --file ./PRL_paper.pdf --yes -o json
#   → 记下 data.token（这是后续取结果的唯一凭据，不是 LKM 的 task_id，两者不可互换）

# ② 需要更高精度/更多语义模式时显式打开（默认只开 textual=1、table=1）
bohr pdf parse --file ./paper.pdf \
  --textual 2 --table 2 --equation 2 --chart 1 --figure 0 --molecule 0 \
  --yes -o json

# ③ 远端 URL 提交（服务端自己去下载，要求 URL 可直连）
bohr pdf parse --url "https://example.org/paper.pdf" --yes -o json

# ④ 同步等待（仍在提交调用里等，token 照样要留着）
bohr pdf parse --file ./paper.pdf --sync --yes -o json

# ⑤ 轮询取结果（3–5 秒一次，别打紧循环）
bohr pdf result <token> -o json                                   # 看 data.status
bohr pdf result <token> --formatted markdown -o json > parsed.json # 要 markdown
bohr pdf result <token> --content --objects -o json                # 全文 + 扁平语义块（默认两者都开）
bohr pdf result <token> --content=false --objects=false --pages-tree -o json   # 只要页级层次版面
bohr pdf result <token> --return-half -o json                      # 解析未完也要先看已完成部分

# ⑥ 只想确认要上传哪个文件、不真上传
bohr pdf parse --file ./paper.pdf --dry-run
```

抽取档位（默认值与取值范围来自 2.8.3 `--help` 与内嵌参考）：

| flag | 默认 | 取值与含义 |
|---|---:|---|
| `--textual` | `1` | `0` 关 / `1` 快速 / `2` 高精度 / `3` 数字版 PDF 直接提取 |
| `--table` | `1` | `0` 关 / `1` 快速 / `2` 高精度 |
| `--equation` | `0` | `0` 关 / `1` 快速 / `2` 高精度 |
| `--chart` | `0` | `0` 关 / `1` 开 |
| `--figure` | `0` | `-1` 返回原图（Base64）/ `0` 关 / `1` 开 |
| `--molecule` | `0` | `0` 关 / `1` 开（分子结构） |
| `--sync` | 关 | 提交时同步等待 |
| `--file` / `--url` | — | **二选一，必填其一** |

> 省钱建议：**只开你真正需要的档位**。默认（textual=1 + table=1）对多数"要文本"的场景已够；`equation=2`/`figure=-1` 会显著增大返回体。计费按**成功解析的页数**算，与档位无关（0.05 元/页），但别为用不到的字段付传输与解析时间。

### 4.3 预期输出样例

提交成功：

```json
{ "ok": true, "data": { "token": "<parse-token>", "status": "processing", "page_count": 6 } }
```

轮询状态（`data.status`）：

| 状态 | 含义 | 动作 |
|---|---|---|
| `undefined` | 排队/尚未产出 | 继续有界轮询 |
| `processing` | 解析中 | 继续有界轮询（看 `proc_page`/`total_page`） |
| `success` | 终态成功 | 取你要的字段 |
| `PARSE_FAILED` | 终态失败 | 停下，读 `data.description` / `data.error` |

markdown 输出开头（**真实样例，PRL 6 页论文，节选**）：

```markdown
# Entangling ions with engineered light gradients

Tommaso Faorlin,1 Lorenz Panzl,1 Phoebe Grosser,1 Pablo Vinas,2 Alan Kahan,2 Walter Joseph Hörmann,1
Yannick Weiser,1 Giovanni Cerchiari,1,3 Thomas Feldker,4 Alexander Erhard,4 Georg Jacob,4 Juris Ulmanis,4
Rainer Blatt,1,4,5 Alejandro Bermudez,2 and Thomas Monz,1,4

1 Universitat Innsbruck, Institut für Experimentalphysik, Technikerstraβe 25/4, 6020 Innsbruck, Austria
2 Instituto de Física Teórica (UAM-CSIC), Universidad Autónoma de Madrid, Cantoblanco, 28094 Madrid, Spain
...
(Dated: March 24, 2026)

Spectral crowding of collective motional modes limits the fidelity of entangling interactions in
trapped-ion quantum processors by inducing off-resonant coupling to spectator modes. ... We
experimentally realise high-fidelity two-qubit gates with error rates below 5 × 10-3 in ion crystals
containing up to 12 ions confined within a single potential well. ...
```

结果字段（`data.*`，官方参考口径）：

| 字段 | 含义 |
|---|---|
| `token` | 解析令牌，后续所有 `result` 调用都用它 |
| `status` | 见上表 |
| `content` | 全文文本/标记（`--content`，默认开） |
| `objects` | 扁平语义块（text/table/chart/legend/equation，带类别与坐标，`--objects` 默认开） |
| `pages_dict` / `pages_tree` | 页级扁平 / 层次版面（**名字像 dict，实际是数组**） |
| `proc_page` / `total_page` | 进度：**用这两个字段判进度，不要用数组长度** |
| `description` / `error` | 失败详情 |
| `cost` | 本次费用（对账用） |

`--formatted` 可选 `plain` / `markup` / `markdown` / `latex` / `html`；它只改变语义内容的**表示形式**，**不校验抽取值是否正确**。

> **一条重要的使用纪律（官方原文）**：把 chart/table 的识别结果当作"已抽取的证据"，**不是已验证的数值真值**——关键数字在进入计算或录入前，务必回原 PDF 对照。我们的实测正好印证了这一点：数字精度虽好，但表格结构没有以可用的形式给出。

### 4.4 计费与支付渠道

- 价目：**0.05 元/页**（`pdf.parse`，**成功解析才触发**），`bohr pdf result` **免费**；
- 最终费用取决于**成功解析的页数**，所以不要在服务报告文档大小或账单结果之前自己编一个总价；
- 不加 `--payment-source` 时：**光子优先，光子明确不足才回落余额**；`--yes` 只确认执行，不授权换渠道；
- 多步流程里选项不继承，每条计费命令都要重新带。

```bash
bohr billing pricing --resource pdf -o json     # 版本匹配的价目
bohr billing ledger -o json                     # 事后对账：这 0.3 元扣在哪
```

### 4.5 选型对比：Uni-Parser vs 本地 PyMuPDF

| 维度 | **Uni-Parser**（`bohr pdf parse`） | **PyMuPDF 本地导出** |
|---|---|---|
| 成本 | 0.05 元/页（6 页 = 0.3 元；50 页 = 2.5 元） | 0 元 |
| 页数限制 | 无 50 页硬闸门（LKM extract 才有），但**按页计费**，长文成本线性上升 | 无限制 |
| 数据出网 | **PDF 会上传到 Bohrium** | 全程本地，不出网 |
| 版面/结构 | 语义块（text/table/chart/legend/equation）+ 页级版面树 + 坐标 | 只有文本流（可选提取图片/表格需自己写逻辑） |
| 公式 | 支持 `equation=1/2`；**本次 6 页 PRL 样例未输出独立 LaTeX 公式块**（宣传未兑现，如实记录） | 公式会被拆成乱序字符，基本不可用 |
| 表格 | 支持 `table=1/2`；**本次样例 Table I 以行文形式存在，未给结构化表** | 需自己按坐标重建，容易错列 |
| 图表/分子式 | `chart`/`figure`（可返回原图 Base64）/`molecule`/反应式 | 无 |
| 页码锚点（`[第 N 页]`） | 有 `pages_dict`/`pages_tree`，但要自己转成锚点标记 | **天然逐页导出，锚点最直接**（§4.6 十行脚本） |
| 数字精度 | 实测保留科学记数法（`5 × 10-3`、`7.4 × 10-2`） | 同样保留（数字版 PDF） |
| 扫描版/OCR | 服务侧有 OCR 能力 | 需另配 OCR（如 ocrmypdf） |
| 延迟 | 异步，需轮询（秒到分钟级） | 秒级 |
| 可复现性 | 依赖服务版本与档位；结果可能随服务升级变化 | 完全可复现（锁 PyMuPDF 版本即可） |

**选型决策树（我们的实测结论）**：

1. 目标是**页码锚定精读 + 锚点程序校验**（本教程主线）→ **用 PyMuPDF**。免费、无页数限制、逐页标记天然对齐校验脚本，52 页长文也不心疼。
2. 论文**公式密集**、或含**跨页大表**、或你需要**图/分子式/反应式**结构 → **用 Uni-Parser**，并且：
   - **先拿 2–3 页试算**（`--textual 2 --table 2 --equation 2`），确认它真的给出了你要的结构，再全篇提交；
   - 把关键数字**回原 PDF 对照**（官方也这么要求）；
   - 扫描版/影印版优先 Uni-Parser（有 OCR），PyMuPDF 会导出空文本。
3. 目标是**知识结构（主张/失效条件/推理链）** → 两者都不是，用 `bohr lkm extract`（§2），并注意它的 **50 页上限**。
4. **数据不能出网**（未发表稿件、涉密合作数据）→ 只用 PyMuPDF；`--file` 提交前想清楚这份 PDF 可以外发。

### 4.6 本地路线：十行 PyMuPDF 导出 + 锚点校验

页码锚点是"AI 有没有真读"的地基。导出成带 `[第 N 页]` 标记的文本伴侣：

```bash
pip install pymupdf        # 实测 PyMuPDF 1.26.x
```

```python
#!/usr/bin/env python3
"""export_pdf_text.py：把 PDF 导出为带 [第 N 页] 标记的文本伴侣。"""
import sys, fitz                       # pip install pymupdf

doc = fitz.open(sys.argv[1])
for i, page in enumerate(doc, start=1):
    print(f"[第 {i} 页]")
    print(page.get_text("text"))
print(f"# 总页数: {len(doc)}", file=sys.stderr)
```

```bash
python3 export_pdf_text.py PDF/paper.pdf > paper.txt
head -n 5 paper.txt
# 预期输出：第一行是 [第 1 页]，其后是该页正文
```

有了 `paper.txt`，就能对 AI 报告里的**每一个页码锚点**做程序校验（`verify_anchors.py`：识别 `(p3)` / `(p3-4)` / `（第 3 页）` / `[第 3 页]` 四种写法，退出码 0=全过、1=有无效锚点；加 `--quotes` 可同时抽查引文是否逐字存在于原文）：

```bash
python3 verify_anchors.py report.md paper.txt
# 实测输出（某轮 with 组）：锚点总数(含区间展开): 70; 有效: 70; 无效: 0
python3 verify_anchors.py report.md paper.txt --quotes
```

配套一条覆盖率自查规则（阈值来自 52 页论文那次教训）：**长文（≥20 页）统计覆盖率 = 报告实际引用页码数 ÷ 全文页数，低于 50% 必须输出盲区警告清单**（哪些页段从未被引用）。它不判失败，只把"你没读的地方"摆到桌面上。

---

## 5. Bohrium 模型网关接入 pi agent

### 5.1 我做了什么（真实数据）

把 Bohrium 模型网关当作一个 **OpenAI completions 兼容 provider** 写进 pi agent 的 `~/.pi/agent/models.json`，实测宿主 pi-coding-agent **1.3.0**，端点 `https://open.bohrium.com/openapi/model-gateway/v1`，接入 **4 个模型**：`glm-5.3`、`kimi-k3`、`qwen3.8-max`、`deepseek-v4.1-flash`（全部 `reasoning: true`、1M 上下文、64K maxTokens）。

用途做了**角色分离**（这是整个实验设计的关键，不是可选项）：

- **运行模型（读论文的）**：`glm-5.3`（thinking=max）——跑完全部精读运行；
- **盲评模型（打分的）**：`kimi-k3` 与 `qwen3.8-max`——两名独立审读代理，对去标识后的报告盲评。

**为什么要分离**：同一个模型既当运动员又当裁判会系统性偏袒自己的输出。分离后得到的对照结果：加载阅读流程组 vs 裸跑组，3 组配对增益 +1.5 / +1.0 / +3.0（30 分制），**均差 +1.83，三组同向无翻转**（with=29.17，without=27.33，n=3）。

一条基线实测值得记下：强模型在 thinking=max 下，38 条页码锚点抽查 37 条精确命中、0 编造。**所以流程校验防的不是"这一次运行"，而是"另一次运行翻车"。**

> **诚实标注**：端点 `https://open.bohrium.com/openapi/model-gateway/v1` 在官方 Apifox 文档（open.bohrium.com）、bohrium-skills 仓库、第三方 API 汇总中**均未收录**。下面的配置以**本机实际生效的配置 + 平台实际返回**为实证（OpenAI completions 兼容协议），不是抄自官方文档；`cost` 字段也无法与任何公开价格页对照。使用前请自行确认当前可用性与计价。

### 5.2 你的复现命令：完整 `models.json`（四模型）

写入 `~/.pi/agent/models.json`（Windows 为 `%USERPROFILE%\.pi\agent\models.json`）：

```json
{
  "$schema": "https://pi.dev/schemas/models.schema.json",
  "providers": {
    "bohrium": {
      "name": "Bohrium Model Gateway",
      "baseUrl": "https://open.bohrium.com/openapi/model-gateway/v1",
      "api": "openai-completions",
      "compat": {
        "supportsReasoningEffort": true,
        "thinkingFormat": "openai"
      },
      "models": [
        {
          "id": "glm-5.3",
          "name": "GLM 5.3",
          "reasoning": true,
          "input": ["text"],
          "contextWindow": 1000000,
          "maxTokens": 65536,
          "cost": { "input": 1.12, "output": 3.92, "cacheRead": 0.28, "cacheWrite": 1.12 }
        },
        {
          "id": "kimi-k3",
          "name": "Kimi K3",
          "reasoning": true,
          "input": ["text", "image"],
          "contextWindow": 1000000,
          "maxTokens": 65536,
          "cost": { "input": 1.68, "output": 5.04, "cacheRead": 0.21, "cacheWrite": 2.1 }
        },
        {
          "id": "qwen3.8-max",
          "name": "Qwen 3.8 Max",
          "reasoning": true,
          "input": ["text", "image"],
          "contextWindow": 1000000,
          "maxTokens": 65536,
          "cost": { "input": 1.68, "output": 5.04, "cacheRead": 0.21, "cacheWrite": 2.1 },
          "compat": { "supportsDeveloperRole": false }
        },
        {
          "id": "deepseek-v4.1-flash",
          "name": "DeepSeek V4.1 Flash",
          "reasoning": true,
          "input": ["text"],
          "contextWindow": 1000000,
          "maxTokens": 65536,
          "cost": { "input": 0.28, "output": 1.12, "cacheRead": 0.0056, "cacheWrite": 0.28 }
        }
      ]
    }
  }
}
```

> 你要求的是"glm-5.3 / kimi-k3 / qwen3.8-max 四模型"——实测本机生效的第四个是 `deepseek-v4.1-flash`，已一并写入（它也是最便宜的那个，适合先拿它跑通链路）。若你的账号下模型 ID 不同，以网关实际返回为准；**加/删模型只改 `models` 数组即可，同 ID 条目会覆盖。**

字段怎么填（零基础对照）：

| 字段 | 作用 | 填错的后果 |
|---|---|---|
| `api: "openai-completions"` | 告诉 pi 用 OpenAI Chat Completions 协议说话 | 协议不对 → 请求 4xx/解析失败 |
| `baseUrl` | 网关端点（**不要**自己加 `/chat/completions`，pi 会拼） | 404 |
| `compat.supportsReasoningEffort` | 声明该端点接受推理力度参数 → pi 的 `/thinking` 档位可下发 | 开了但服务端不支持 → 请求被拒（官方提醒：**不要只因端点自称兼容就打开 compat 开关，要对着真实服务端验证**） |
| `compat.thinkingFormat: "openai"` | 思考内容的封装格式 | 思考流解析异常 |
| 模型级 `compat.supportsDeveloperRole: false` | qwen3.8-max **不支持 `developer` 角色**，pi 会用 `system` 代替 | 该模型报角色错误 |
| `reasoning: true` | 声明是推理模型（`/thinking` 才可选档） | 无法调 thinking |
| `input: ["text","image"]` | 支持图片输入（kimi-k3 / qwen3.8-max 支持；glm-5.3 / deepseek 仅 text） | 发图给纯文本模型会失败 |
| `contextWindow` / `maxTokens` | 上下文窗口 / 单次最大输出 | 影响 pi 的压缩与截断策略 |
| `cost.*` | $/M token，**仅用于 pi 本地账单统计**，不参与真实扣费 | 只影响你看到的成本估算 |

### 5.3 鉴权：两种方式，选一种

**方式 A（推荐，pi 原生存凭证）**：在 pi 里运行 `/login`，选 `bohrium`，粘贴 AccessKey。凭证存进 `~/.pi/agent/auth.json`（**该文件与 models.json 都要保密**，不要提交进 git）。实测本机 `auth.json` 里就有 `bohrium` 条目。

**方式 B（写进 models.json，用环境变量插值）**：在 provider 块里加一行，pi 支持 `$NAME` / `${NAME}` 环境变量插值，也支持 `!command` 动态取值：

```json
"providers": {
  "bohrium": {
    "apiKey": "$BOHR_ACCESS_KEY",
    "baseUrl": "https://open.bohrium.com/openapi/model-gateway/v1",
    "api": "openai-completions",
    "...": "..."
  }
}
```

```bash
export BOHR_ACCESS_KEY="你的 AccessKey"   # 与 bohr CLI / 官方 skills 共用同一把 Key
```

pi 的凭证优先级（多来源共存时）：运行时 `--api-key` → `auth.json` 存储的凭证 → `models.json` 里的 `apiKey` → provider 环境变量。

### 5.4 预期输出样例：验证接入

```bash
# ① 列出 pi 看到的模型（能搜到 bohrium/* 说明配置被读到了）
pi --list-models bohrium
# 预期输出：bohrium/glm-5.3、bohrium/kimi-k3、bohrium/qwen3.8-max、bohrium/deepseek-v4.1-flash

# ② 冒烟测试（最便宜的一档先跑通）
pi --model bohrium/deepseek-v4.1-flash "只回复 ok"
# 预期输出：ok

# ③ 正式跑：带思考档位的精读（thinking 档位用 :max / :high 简写）
pi --model bohrium/glm-5.3:max "精读 paper.txt，输出组会级审读报告，每条论断括注页码"

# ④ 加载 Skill 的对照实验（--skill 与 --no-skills 构成唯一差异变量）
pi --skill skills/xread --model bohrium/glm-5.3:max "精读 paper.txt，按流程输出审读报告" > report_with.md
pi --no-skills            --model bohrium/glm-5.3:max "精读 paper.txt，输出审读报告"     > report_without.md
```

（在 pi 交互界面里也可以用 `/model` 选模型、`/thinking` 选调思考档、`Ctrl+P` 循环切换；`/model` 会**重新加载** models.json，改完配置不用重启。）

不用 pi、直接打端点也可以（curl 冒烟测试）：

```bash
export BOHR_ACCESS_KEY="你的 AccessKey"
curl https://open.bohrium.com/openapi/model-gateway/v1/chat/completions \
  -H "Authorization: Bearer $BOHR_ACCESS_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-5.3",
    "messages": [
      {"role": "system", "content": "你是严谨的论文阅读助手，所有结论必须标注原文页码/章节；原文找不到依据时必须明确说「原文未找到依据」。"},
      {"role": "user", "content": "这篇论文的核心贡献是什么？请分点回答并给出证据位置。"}
    ],
    "temperature": 0.2
  }'
# 预期输出：标准 OpenAI Chat Completions JSON（choices[0].message.content 为回答）
```

Python（OpenAI SDK）多模型轮询骨架——做"同一问题问四个模型"的对照实验时用：

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["BOHR_ACCESS_KEY"],
    base_url="https://open.bohrium.com/openapi/model-gateway/v1",
)
MODELS = ["glm-5.3", "kimi-k3", "qwen3.8-max", "deepseek-v4.1-flash"]

SYS = ("你是论文精读助手。只依据给定原文回答；无法从原文找到依据时明确说"
       "『原文未找到依据』。每个论断后括注页码。")

def ask(model: str, paper_text: str, question: str) -> str:
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": SYS},
                  {"role": "user", "content": f"【论文原文】\n{paper_text}\n\n【问题】{question}"}],
        temperature=0.2,
    )
    return resp.choices[0].message.content

if __name__ == "__main__":
    text = open("paper.txt", encoding="utf-8").read()
    for m in MODELS:
        open(f"answer_{m}.md", "w", encoding="utf-8").write(ask(m, text, "本文的核心主张及其适用边界？"))
```

> **盲评纪律**（我们实测用的做法）：把 model id 映射成 A/B/C/D 标签后再落盘评估表，评估时不知道模型身份，防止品牌先验污染打分；映射表密封，评完再开封对回。

### 5.5 价格与选型（本机 models.json 的 cost 字段口径，$/M token）

| 模型 | 输入模态 | input | output | cacheRead | cacheWrite | 本教程里的角色 |
|---|---|---:|---:|---:|---:|---|
| `deepseek-v4.1-flash` | text | **0.28** | **1.12** | 0.0056 | 0.28 | 便宜档：跑通链路、批量粗筛 |
| `glm-5.3` | text | 1.12 | 3.92 | 0.28 | 1.12 | **运行模型**（精读，thinking=max） |
| `kimi-k3` | text+image | 1.68 | 5.04 | 0.21 | 2.1 | **盲评审读代理 1**（支持图片，可核图表） |
| `qwen3.8-max` | text+image | 1.68 | 5.04 | 0.21 | 2.1 | **盲评审读代理 2**（不支持 developer role） |

三点实用推论：

1. **最贵与最便宜差 6 倍**（input 0.28 vs 1.68）→ 对照实验顺手就能产出一条"质量/价格"帕累托曲线：先用 flash 档跑 20 个问题，只在分歧题上升级到贵档。
2. **cacheRead 远低于 input**（glm-5.3：0.28 vs 1.12）→ 精读同一篇论文时**保持同一会话连续追问**，别每问一次就重开上下文，能省下大部分重复的原文 token。
3. **审读代理选带 image 的**（kimi-k3 / qwen3.8-max）→ 图表误读类失败模式只有它们能看图核对；纯 text 模型（glm-5.3 / deepseek）无法验证"图 3 是不是被读错了"。

### 5.6 网关接入常见问题

| 现象 | 排查 |
|---|---|
| `pi --list-models bohrium` 搜不到 | models.json 语法错误（用 `$schema` 让编辑器报错）；或路径不对（`~/.pi/agent/models.json`） |
| 401 / 鉴权失败 | AccessKey 失效或未生成（https://www.bohrium.com/settings/account）；`/login` 重登或检查 `$BOHR_ACCESS_KEY` 是否导出 |
| 404 | `baseUrl` 多写了 `/chat/completions`（pi 自己拼路径） |
| 报角色相关错误（qwen） | 缺 `"compat": { "supportsDeveloperRole": false }` |
| `/thinking` 不可用 | 模型条目缺 `"reasoning": true`，或 provider 缺 `compat.supportsReasoningEffort` |
| 发图失败 | 该模型 `input` 里没有 `"image"`（glm-5.3 / deepseek-v4.1-flash 为纯文本） |
| 请求被拒但配置看着没问题 | compat 开关是"已验证差异"声明，**不要仅凭端点自称兼容就打开**；对着真实响应逐个关掉试 |
| 成本对不上 | `cost` 只影响 pi 本地统计；真实扣费以 Bohrium 账单为准（`bohr billing ledger`） |

---

## 6. 四个产品在文献阅读工作流中的分工

### 6.1 分工表（本教程的核心一张表）

| 阶段 | 产品 / 命令 | 输入 | 产出 | 单价 | 什么时候**跳过**它 | 本教程实测要点 |
|---|---|---|---|---|---|---|
| **① 读前解析** | Uni-Parser<br>`bohr pdf parse --file` → `bohr pdf result <token> --formatted markdown` | 论文 PDF | 结构化 markdown（文本/表格/公式/图表/分子式）+ 页级版面 | **0.05 元/页**（result 免费） | 只做页码锚定精读时——**PyMuPDF 免费且无页数限制**；数据不能出网时 | 6 页 PRL 花 0.3 元；数字精度完好（`5 × 10-3`），但**本次未输出结构化表格与 LaTeX 公式块**（Table I 以行文存在）→ 先拿 2–3 页试算再全篇提交 |
| **①' 读前解析（本地替代）** | PyMuPDF `export_pdf_text.py` | 论文 PDF | 带 `[第 N 页]` 标记的文本伴侣 | 0 元 | 需要公式/表格/图表结构、或扫描版需 OCR 时 | 52 页 Annals 长文（`Annals_10.4007_annals.2026.204.2.1.pdf`）经 PyMuPDF 1.26.5 照常导出 130,052 字符，锚点校验的地基 |
| **② 读中推理** | 模型网关<br>pi `--model bohrium/glm-5.3:max` | 文本伴侣 + 阅读流程 Skill | 带页码锚点的审读报告 | 按 token（§5.5） | 无（这是执行主体） | glm-5.3 跑精读、kimi-k3 + qwen3.8-max 双盲评估——**运行/评估模型分离**避免自评偏倚；配对增益 +1.83/30，三组同向无翻转 |
| **③ 读后核查（外部第二意见）** | LKM extract<br>`bohr lkm extract submit` → `result <task_id>` | 论文 PDF（**≤50 页、≤64 MiB**） | 主张/问题/推理链图 + `failure_mode` + `weak_types` + `refs` | **1.00 元/篇**（缓存 0.10 元） | 论文 >50 页（52 页 Annals **实测被拒**）；只需要版面文本时（那是 Uni-Parser 的活） | 论文 A：60 主张/35 问题/26 推理链，**25 条带 failure_mode**，12.65 分钟；论文 B（6 页 PRL）：27 主张/**13 条 failure_mode**，12.26 分钟 |
| **③' 读后核查（自证层）** | `verify_anchors.py` + 覆盖率自查 | 报告 + 文本伴侣 | 锚点有效性 + 盲区警告清单 | 0 元 | 无（这是质量门） | 实测 `锚点总数(含区间展开): 70; 有效: 70; 无效: 0`；覆盖率 <50% 触发盲区清单（阈值来自 52 页论文跳读第 30–38 页的教训） |
| **④ 跨文献定位** | LKM search<br>`bohr lkm search "<概念>" --scopes conclusion` | 陌生概念/主张表述 | 跨论文的结构化 claim（带 `gcn_` ID，可续追推理链） | **0.05 元/次**，月度 **1000 次免费额度**优先 | 论文不在 LKM 语料库时（实测案例论文未命中）→ 改用 extract | 一次查询 **10 条命中 / 10 篇不同论文**，`has_more=true`，708 ms，本次走额度（`remaining: 997`）**实付 0 元** |
| **④' 深钻** | `bohr lkm claim reasoning` / `graph` / `reference` / `variables batch` | `gcn_` ID / 数字论文 ID / DOI | 推理链、论文知识图、引文与被引卡片 | 各 0.05 元/次（同额度） | 只需要主张文本时 | `has_reasoning=true` 的 conclusion 才能追链；三类节点语义（highlight/weak_point/subproblem）不可混用 |

**一张图记住分工**：

```
PDF ──① Uni-Parser（要结构：公式/表格/图）──┐
    └─①' PyMuPDF（要页码锚点，免费无限制）──┤
                                            ├─→ ② 模型网关（pi + glm-5.3 精读）
                                            │        ↓ 审读报告
    ──③ LKM extract（主张+失效条件）────────┼─→ ③' verify_anchors（锚点/覆盖率质量门）
                                            │        ↓ 交叉验证：两套独立方法报警的交集
    ──④ LKM search（跨论文定位陌生概念）────┘        ↓
                                              ④' claim reasoning / graph / reference 深钻
```

**为什么这套组合拳值得**：文献阅读的"读前解析 → 读中推理 → 读后核查 → 跨文献定位"全链条都有可编程接口，因此**整个流程可以被别人用几块钱复现**，而不是"我在 UI 里点了一遍，你信我"。UI（玻尔·科学空间）与 CLI/OpenAPI 用的是同一套底座——Uni-Parser、Science Navigator、LKM——所以"UI 里能复现，API 里能量化"。

### 6.2 全链路命令（可整段复制）

```bash
# ── 0. 一次性准备 ────────────────────────────────────────────
npm install -g @dptech-corp/bohr-cli
bohr auth login && bohr auth status -o json
export BOHR_ACCESS_KEY="你的 AccessKey"        # 供 pi / OpenAPI / 官方 skills 共用
pip install pymupdf
bohr billing pricing --resource lkm -o json    # 花钱前先看价
bohr billing pricing --resource pdf -o json

# ── 1. 读前：本地文本伴侣（免费，锚点地基）──────────────────
python3 export_pdf_text.py PDF/paper.pdf > paper.txt
head -n 3 paper.txt                            # 应看到 [第 1 页]

# ── 1b. 读前（可选）：公式/表格密集才用 Uni-Parser（0.05 元/页）
bohr pdf parse --file PDF/paper.pdf --textual 2 --table 2 --equation 2 --yes -o json
#    → 复制返回里的 data.token
bohr pdf result <token> -o json -q data.status          # 轮询到 success
bohr pdf result <token> --formatted markdown -o json > paper_parsed.json

# ── 2. 读中：网关模型精读（配置见 §5.2）────────────────────
pi --model bohrium/glm-5.3:max "精读 paper.txt，每条论断括注页码，输出审读报告" > report.md

# ── 3. 读后：锚点质量门（免费）──────────────────────────────
python3 verify_anchors.py report.md paper.txt            # 退出码必须为 0
python3 verify_anchors.py report.md paper.txt --quotes

# ── 4. 读后：LKM 外部第二意见（1 元/篇，≤50 页）────────────
bohr lkm extract submit PDF/paper.pdf --wait --timeout 30m --yes -o json
#    → 复制 task_id
bohr lkm extract result <task_id> --yes -o json > lkm.json
python3 dump_failure_modes.py lkm.json > failure_modes.md   # §2.9 的脚本
#    → 把报告未覆盖的高危主张当追问清单，回炉补查

# ── 5. 跨文献：陌生概念放到全库定位（月度额度内免费）────────
bohr lkm search "你的概念关键词" --scopes conclusion --top-k 20 --yes -o json > hits.json
bohr lkm claim reasoning <gcn_id> --format graph --yes -o json   # 对最相关的命中追推理链

# ── 6. 对账 ─────────────────────────────────────────────────
bohr billing ledger -o json                              # 这套流程到底花了多少
```

### 6.3 端到端实测账单

| 项目 | 数量 | 单价 | 小计 |
|---|---|---|---|
| LKM extract（论文 A 29 页 + 论文 B 6 页） | 2 篇 | 1.00 元/篇 | **2.00 元** |
| Uni-Parser（PRL 6 页） | 6 页 | 0.05 元/页 | **0.30 元** |
| LKM search | 1 次 | 0.05 元/次，**月度 1000 次额度抵扣** | **0.00 元**（`remaining: 997`） |
| PyMuPDF 导出 + 锚点校验 | — | 本地 | 0.00 元 |
| 模型网关 token | 视用量 | 见 §5.5 | 数毛到数元 |
| **合计（不含模型 token）** | | | **≈ 2.30 元** |

> 如果你只跑一遍最小闭环（1 篇 ≤50 页论文 + 1 次 search + PyMuPDF），**成本是 1 元**——search 在额度内免费，PDF 解析走本地。

### 6.4 常见失败与修法（全流程）

| 症状 | 归因层 | 修法 |
|---|---|---|
| 报告页码看着齐，但整段证明/方法缺席 | **流程层**（跳读） | 分页读取 + 覆盖率自查（≥20 页必须算，<50% 输出盲区清单） |
| `verify_anchors.py` 报"页码越界" | 模型层（幻觉页码） | 该论断降级为 `[不确定]` 或删除，回炉重写；不要手工改页码 |
| 锚点全过但结论挂错页 | 流程层（归位错误） | 加 `--quotes` 抽查引文 + 人工抽查关键构造（脚本只验"页码存在"，不验"归位正确"） |
| LKM extract 被拒 | **输入层**（52 页 > 50 页上限） | 改走 PyMuPDF 本地路线，或切出主文 ≤50 页再提交（并声明只抽了部分） |
| `LKM_PARSE_RESULT_NOT_READY` / 290017 | 时序 | 继续等同一 task_id，**不要重新提交** |
| 重复提交后收到 290020 | 时序 | 用返回的既有 task_id 继续轮询；重复提交不加速 |
| `partial` 终态 | 业务性失败 | **不可重试**：查原因；重提同一 PDF 只会再拿一个 partial |
| `BILLING_INSUFFICIENT`（retryable:false） | 计费 | 充值或在获授权后换 `--payment-source`；保留 task_id，别为绕计费重提 |
| Uni-Parser 没给出表格/公式结构 | 服务/档位 | 提高档位（`--table 2 --equation 2`）重试；仍不行就回退 PyMuPDF + 人工核表；**关键数字必须回原 PDF 对照** |
| search 命中很多但没有你的目标论文 | 语料覆盖 | LKM 只覆盖已入库文献 → 新论文用 `extract` 自建图谱 |
| search 结果"相关但不可用" | 误读 score | `score`/`rerank_score` 只排序，**不是置信度**；abstract 级命中只当背景 |
| `CONFIRMATION_REQUIRED` | CLI 确认门 | 确认花费后加 `--yes`（`--yes` ≠ 授权换支付渠道） |
| pi 里 `/thinking` 不能调 | 配置 | 模型缺 `reasoning: true` 或 provider 缺 `compat.supportsReasoningEffort` |

---

## 7. 复现清单（照着打勾）

```
□ npm install -g @dptech-corp/bohr-cli && bohr --version   → 2.8.3+
□ bohr auth login && bohr auth whoami -o json              → 身份正确
□ bohr doctor                                              → 体检通过
□ bohr billing pricing --resource lkm -o json              → 确认 0.05/次、1.00/篇
□ bohr billing pricing --resource pdf -o json              → 确认 0.05/页
□ bohr guide read bohr-lkm                                 → 读一遍本机版本的官方指南
□ pip install pymupdf && python3 export_pdf_text.py ...    → paper.txt 首行是 [第 1 页]
□ 论文 ≤50 页？                                            → 否则跳过 extract，走本地路线
□ bohr lkm extract submit paper.pdf --wait --yes -o json   → 拿到 task_id
□ bohr lkm extract result <task_id> --yes -o json > lkm.json
□ python3 dump_failure_modes.py lkm.json                   → 得到高危主张清单（metadata 需二次 json.loads）
□ bohr lkm search "<概念>" --scopes conclusion --yes -o json → 检查 notice.billing.remaining
□ （可选）bohr pdf parse --file ... --textual 2 --table 2 --equation 2 --yes -o json → data.token
□ （可选）bohr pdf result <token> --formatted markdown -o json → data.status == success
□ 写 ~/.pi/agent/models.json（§5.2 四模型）+ /login 或 apiKey: "$BOHR_ACCESS_KEY"
□ pi --list-models bohrium                                 → 四个模型都在
□ pi --model bohrium/deepseek-v4.1-flash "只回复 ok"        → ok
□ pi --model bohrium/glm-5.3:max "精读 paper.txt ..." > report.md
□ python3 verify_anchors.py report.md paper.txt            → 无效: 0，退出码 0
□ 用 failure_modes.md 逐条对账报告，未覆盖的高危主张回炉追问
□ bohr billing ledger -o json                              → 对账（本教程 ≈2.3 元）
```

---

## 8. 事实边界与信息来源（诚实声明）

**本教程中经过真实运行验证的**：

1. `bohr` CLI 2.8.3 的安装、`version`、`auth login/status/whoami`、`billing`、`guide` 命令面（本机实测）；
2. LKM extract 两次成功运行：task_id `fdf24d62-f293-48d2-8fe5-dda9bd5c16de`（PLOS Biology，60/35/26/26，25 条 failure_mode，12.65 分钟，request_id `90404d92-…`）与 `3ad2e06c-9f20-4c53-a10d-019ff0ffd18d`（PRL，27/20/9/9，13 条 failure_mode，12.26 分钟），`step_durations` 原始记录可查；
3. 52 页 Annals 论文提交 extract **被拒（50 页上限）**，与 CLI `--help`/内嵌指南的限制条款一致；
4. LKM search 一次真实查询：10 条命中 / 10 篇论文 / `has_more=true` / 708 ms / request_id `6f68c449-…` / `notice.billing` 显示走月度额度（`remaining: 997`）；
5. Uni-Parser 一次真实解析：6 页 PRL、0.3 元、markdown 输出样例（含"未输出结构化表格与 LaTeX 公式块"这一负面观察）；
6. pi agent `~/.pi/agent/models.json` 中 Bohrium provider 的实际生效配置（四模型、compat 开关、cost 字段），以及 pi 1.3.0 的 `--model` / `--skill` / `--no-skills` / `--list-models` 参数。

**本教程中未找到公开资料、按实证如实标注的**：

1. 模型网关端点 `open.bohrium.com/openapi/model-gateway/v1` 的**官方 API 文档**——Apifox 文档、bohrium-skills 仓库、第三方 API 汇总均未收录；配置以本机实际生效 + 平台实际返回为准；
2. 模型网关的**官方模型目录与价格页**——`cost` 字段无法与公开页面对照，只影响 pi 本地成本统计；
3. 玻尔·科学空间 **UI 内可切换的模型清单**及各 Master（SciMaster/BioMaster/MatMaster/PharmMaster）底层所用模型；
4. 科学空间的**公开定价/光子消耗规则**（机构版有赠送光子的宣传，具体计费表未检索到）；
5. 科学空间的**独立帮助文档站**（bohrium-doc.dp.tech 主要覆盖经典科研空间站与计算平台）。

**价格与限制的权威核对方式**（不要信任何二手教程，包括本文——自己跑一遍）：

```bash
bohr billing pricing --resource lkm -o json
bohr billing pricing --resource pdf -o json
bohr guide read bohr-lkm references/commands.md
bohr guide read bohr-pdf-parse references/commands.md
bohr lkm extract submit --help
bohr pdf parse --help
```

**配套阅读**（玻尔生态官方入口）：

- 玻尔·科学空间产品页：https://www.bohrium.com/en/bohrscience
- bohr CLI 介绍：https://www.bohrium.com/bohr-cli/intro
- Bohrium OpenAPI：https://open.bohrium.com/
- 官方 Agent Skills 仓库（17 个 SKILL.md）：https://github.com/dptech-corp/bohrium-skills
- 官方平台文档：https://bohrium-doc.dp.tech/docs/
- 官方博客《How to Read a Research Paper More Efficiently》（点名的两个 AI 读论文失败模式："用 AI 替代而非辅助阅读原文"、"不核对证据就相信结论"）：https://www.bohrium.com/en/blog/how-to-read-a-research-paper/
- AccessKey 生成页：https://www.bohrium.com/settings/account

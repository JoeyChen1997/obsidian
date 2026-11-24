---
tags:
  - research
  - research/agent
aliases:
  - Paperlist Research Agent
  - Paperlist 研究助手
---

# Paperlist Research Agent

这是一个在当前 Obsidian 仓库里工作的**单 Agent**。对话模型负责理解问题、决定怎么查和综合证据；本地工具负责检索、追踪关系和返回可核对的 PDF 页。无需另开 API、批量上传论文、安装数据库服务或训练模型。索引和图谱保存在本机；提交给当前对话模型的是任务所需的检索结果或选读页。Agent 不会后台阅读或自动把未读论文标成已精读。

## 直接使用

- **Codex**：在这个 vault 的会话里，用 `$paperlist-research` 加上研究问题。若当前客户端未显示新入口，可直接说「读取 `.agents/skills/paperlist-research/SKILL.md`，用 Paperlist 研究 Agent 处理下面的问题」。
- **Claudian 的 Claude 后端**：同一个工作流有 `/paperlist-research` 入口；若菜单还没显示，打开新会话后用上面的完整请求也可以。Codex 后端可用上面的技能或明文入口。

例如：「用 Paperlist 研究 Agent 追溯定向广告和定向定价。为什么 Iyer 等（2005）和 Moorthy 与 Shahrokhi Tehrani（2023）的联合利润结果不同？请按信息结构、投放技术、时序来对照；再找后文怎样加入平台、隐私或不完美定向，区分已核原文和待核候选。」

| 你要做什么 | Agent 会用什么 | 应输出什么 |
| --- | --- | --- |
| 找同机制论文 | 多组英文短词／词组并行布局，融合标题和正文排名；再逐篇筛查 | 候选、最接近的论文、纳入／排除理由和检索范围 |
| 追历史或两篇之间的联系 | 先查方向、年份和带证据的关系，再补搜跨分支的全文，以及向前、向后引用 | 基准、扩展、结论边界、仅引用与未核节点 |
| 比模型或写 related literature | 对齐模型设定，核对 PDF 的模型、证明和发表信息 | 哪个原语变了，哪个命题随之改变；来源可回溯的精简综述 |

## 工具与首版覆盖

以下命令从 vault 根目录运行。参数里的 `--term` 把多个词按 AND 查询，`--phrase` 查整个词组；两者都可重复。全文仍来自已有的 47,568 份 PDF 索引。图谱是独立、可维护的小层，目前种下的是**定向广告与定向定价**和**广告平台与隐私**，不代表各领域都已有谱系。

```powershell
$paperPython = "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$researchTool = '.\Marketing Paper\research_agent.py'
& $paperPython -B $researchTool topics
& $paperPython -B $researchTool brief '定向广告与定向定价的研究脉络' --intent lineage --anchor targeting
& $paperPython -B $researchTool brief '卖家为何选择代理模式' --intent discover --term 'agency selling platform' --phrase 'reselling versus agency selling' --phrase 'revenue sharing' --journal MKSC --journal MS
& $paperPython -B $researchTool trace --anchor moorthy-2023 --direction past
& $paperPython -B $researchTool path iyer-2005 zhu-2025 --include-screened
& $paperPython -B $researchTool evidence moorthy-2023 --section proof --page 21 --chars 12000
& $paperPython -B $researchTool validate
```

- `brief` 融合标题及逐页全文 BM25；排名不是结论，特别可能命中参考文献。日期和期刊筛选仅作用于候选检索，日期采用文件名提示。图谱使用另行核对的发表年，保留历史前驱。
- `trace` 返回已核关系和待查关系两组。`path` 默认只沿已核查的语义边走；`--include-screened` 可查看带暂定环节的链。仅引用边不支持链路推导，路径也不等于因果证明。
- `evidence` 支持稳定的图谱论文 ID 或索引数字 ID。未知章节明确报错，仍可手动指定 PDF 页；章节定位目前仅为已核对论文的页范围，页与页之间可能跨节。公式、印刷页码和引文要查 PDF 原页。
- 本版不是向量检索，没有全库章节自动识别、全库引文图、外部引文服务或模型微调。对图谱覆盖外的问题仍可检索全文与人工追读；以后是否加本地向量重排，应看真实问题中哪些关键论文被漏掉，再量化比较。

## 维护证据图谱

`Marketing Paper/research_graph.json` 是可版本管理的事实层。论文节点保存稳定 ID、正式发表年、题目、来源和阅读状态；章节映射是可选的闭区间 PDF 物理页。关系从较早论文指向后续论文：`extends_component`、`limits_result`、`contrasts_assumptions`、`endogenizes` 等用来说明模型或结论具体怎样变；`cites` 仅表明引用。每条关系写 `claim`、`changed`、`limit`、审核状态及 `evidence` 中具体论文和物理页。未读原件或只看摘要／引用语境的关系标 `screened` 或 `candidate`；只依据参考文献出现不得标为模型继承。`validate` 检查结构、目录与页存在，不会替代人或 Agent 审核主张。三张独立卡的缺失会单列，不遮蔽其 PDF 证据，也不会自动恢复文件。

配套笔记：[[Marketing Paper/Paperlist 研究知识库|底层文献库]]、[[Marketing Paper/精读台账与研究流程|精读台账]]、[[Marketing Paper/研究谱系/定向广告与定向定价 - 研究谱系|首条研究谱系]]。

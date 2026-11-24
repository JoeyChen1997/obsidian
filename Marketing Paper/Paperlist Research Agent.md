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

## 全库 RAG 和研究谱系

**全文 RAG** 融合标题／逐页全文、分章节的 BM25 段落和本地论文级向量。命中段落带 PDF 物理页及推断章节。论文向量编码标题和摘要，缺摘要时用开篇文字。**引用网络**从参考文献用题名、相邻作者和年份识别本地原件，支持向前、向后、多跳和共同引用检索。

**时序语义图谱**从检索得到的论文出发，按年份展开引文中的模型沿用、扩展、假设差异、结论对比、支持和适用条件。自动候选同时保存正文语境、参考文献页码和抽取依据。概念由 43 个词表主题识别，假设和命题由显式表述或编号识别。**已审核图谱**保存原文核读后确认的具体变化和适用条件。

已有两组专题可直接查[[Marketing Paper/研究谱系/Paperlist 首批命题对照|首批命题对照]]。主题入口是 `trace --anchor privacy-platforms` 与 `trace --anchor channel-quality`。读到图谱论文提供的可用文献卡后，可用 `evidence` 回到指定物理页。已审核边指与原文核过的比较，不代表每条边都建立了整体模型嵌套。

此次全库自动索引：**47,568 份 PDF**，**918,124 个可检索来源页**，切成 **3,530,738 个正文段落**；生成 **47,567 个论文级向量**，剩下一件无可检索正文。识别 **219,911 条参考文献区内候选引用**和 **1,890 条未定位参考文献标题时的尾页候选**。有 30,643 个来源文件至少匹配到一条本地引用。仍不是逐篇精读。检测到章节标题的文档有 37,890 份；检测不到时正文仍可搜，不要依赖严格章节过滤做穷尽排查。

两项规则扫描均覆盖 **47,568 份 PDF**。时序语义层有 **963 条关系候选，涉及 947 对论文**，包括 63 条根据跨句上下文定位的关系；另有 **3,059 条引用归因，涉及 2,983 对论文**，指后文明确描述前文的假设、模型或结果，不表示理论继承。两类有 50 对重叠，合计 **3,880 对有正文线索的论文**。概念和陈述索引仍有 **156,364 组论文—概念**及 **144,083 条陈述候选**。这些数字是自动扫描结果，不是精读覆盖。

跨句关系要求可定位的引用及明确的语境，例如前句列出两篇、下句的 “The first” 指回第一篇，或 “These papers” 指回上一句明确列出的论文。它仍会漏掉跨页或需要对照模型、符号及证明才看得出的联系。遇到无直接引用索引的论文，模型比较另外给出双侧原文，作为待核对照，不写入时序图。

以下命令从 vault 根目录运行。`--term` 把多个词按 AND 查询；`--phrase` 查整个词组；`--semantic` 写一句英文描述来补候选。从图谱未覆盖的主题也可以直接开始。

```powershell
$paperPython = "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$researchTool = '.\Marketing Paper\research_agent.py'
& $paperPython -B $researchTool brief '定向广告与定向定价的研究脉络' --intent lineage --anchor targeting --semantic 'How firms jointly choose targeted advertising and personalized prices'
& $paperPython -B $researchTool brief '卖家为何选择代理模式' --intent lineage --term 'agency selling platform' --phrase 'revenue sharing' --semantic 'When online retail platforms let sellers set prices versus buy goods and resell them' --journal MKSC --journal MS
& $paperPython -B $researchTool trace --anchor moorthy-2023 --direction past
& $paperPython -B $researchTool path iyer-2005 zhu-2025 --include-screened
& $paperPython -B $researchTool evidence moorthy-2023 --section proof --page 21 --chars 12000
$corpusTool = '.\Marketing Paper\corpus_rag.py'
& $paperPython -B $corpusTool status
& $paperPython -B $corpusTool citations 24726 --direction future --depth 2
& $paperPython -B $corpusTool context 24726 24343
& $paperPython -B $corpusTool related 24726
& $paperPython -B '.\Marketing Paper\corpus_vectors.py' status
$semanticsTool = '.\Marketing Paper\corpus_semantics.py'
& $paperPython -B $semanticsTool status
& $paperPython -B $semanticsTool path 44977 43712
& $paperPython -B $semanticsTool path 23839 24931
& $paperPython -B '.\Marketing Paper\citation_claims.py' status
& $paperPython -B $researchTool brief '广告费率外生还是内生' --intent compare --phrase 'advertising rates' --phrase 'advertising exposure' --citation-seed 24931 --semantic 'When a platform sets advertising rates in the model and when those rates are taken as given'
& $paperPython -B $researchTool brief '分销渠道与价格内生性' --intent lineage --phrase 'distribution channel' --phrase 'price endogeneity' --term 'jeuland shugan channel profits' --semantic 'Pricing and product quality in a manufacturer retailer distribution channel when retail prices are endogenous'
```

- `brief` 中 `corpus_rag.ranked_candidates` 列出融合排名和命中渠道；`passages` 提供候选篇章和原页；`dense` 披露实际向量覆盖，未启用或不可用会明确标记。`lineage`、`compare`、`write` 模式围绕候选和手动 `--citation-seed` 展开自动网络。日期和期刊筛选限制检索候选，不限制追溯前驱；自动层的年份来自文件名，不是正式引文年份。
- `corpus_rag.py context` 给出参考文献证据和正文作者-年份命中。`related` 用共享参考文献找没有直接相互引用的近邻。两者都需要回原文才能判断理论关系。自动引用会漏掉题名异译、短题名、作者或年份不一致及未收录论文，并可能误连；默认不查低置信尾页，确有需要再加 `--include-tail`。
- `brief` 的 `corpus_rag.semantic_graph` 返回当前检索邻域的时间线、概念命中、假设／命题线索，以及带证据页的关系候选。用 `--citation-seed` 加入已知论文的数字 ID，再用 `corpus_semantics.py path` 查两个数字 ID 之间的多跳候选路径。时间线使用文件名年份，引用写作时以原刊为准。查不到路径时，结合全文、引用上下文和同义词继续检索。
- `citation_attributions` 给出后文怎样描述前文及其原页；若有 `cited_source_leads`，同时给出在前文中检索到的相关页，不能据此认定原命题成立。
- `model_comparison_leads` 在 `lineage` 和 `compare` 模式下自动补搜同一模型要素，例如 `advertising rates`、`advertising exposure` 或 `wholesale prices`。结果给出两篇的原句、页码和差异维度，区分条件陈述和模型设定候选。它只说明本地索引未检出直接引用，不能证明两篇互不引用或存在继承。词表以外的要素仍可走全文和向量搜索。
- `trace`/`path` 只查审核图谱，与全库候选引用分开。`path --include-screened` 可以查看带暂定环节的审核图谱链。引用路径不等于因果证明或模型继承。
- `evidence` 支持稳定的图谱论文 ID 或索引数字 ID。未知章节明确报错，仍可手动指定 PDF 页；章节定位目前仅为已核对论文的页范围，页与页之间可能跨节。公式、印刷页码和引文要查 PDF 原页。

### 原页抽核

- **分销渠道**的查询在没有已审核主题节点时，找到了 Jeuland 与 Shugan（1983）至 Xu（2009）的假设对比。Xu 的 PDF 第 6 页（刊页 1351）引入价格内生性，并在命题 2 区分质量不足、相等或过度提供的情形。三种情况取决于需求弹性结构。数字 ID 为 `24379 → 35942`。
- **信息商品捆绑**的查询找到了 Hitt 与 Chen（2005）至 Wu 等（2008）的扩展。Wu 等在 PDF 第 4 页（刊页 610）说明如何用非线性混合整数规划研究定制捆绑，以容纳更多估值及消费者异质性设定。数字 ID 为 `30628 → 35885`。
- **定向广告**：Moorthy 与 Shahrokhi Tehrani（2023）PDF 第 3 页（刊页 1059）明确说明 Chen 与 Iyer（2002）的可触达性设定如何对应其顺序博弈中的局部定价情形，也对比了 Iyer 等（2005）的确定性曝光与其概率性曝光。Zhu 等（2025）PDF 第 16 页（刊页 1396）把 Moorthy 与 Shahrokhi Tehrani 的设定放在无平台、广告费率外生的组内作对比，再讨论设定费率的中间平台。现在能返回 `23839 → 24726 → 24931` 的候选路径。
- **跨分支对照**：同一查询在无直接引用索引的例子中找到 Wang、Zhou 与 Joshi（2024）PDF 第 17 页（刊页 174）的外生广告费率假设，与 Zhu 等（2025）PDF 第 2 页（刊页 1382）将广告费率对隐私制度的响应作为其消费者隐私获益的必要条件相对照。两篇研究的结果变量和制度设定不同，这不是同一个福利命题。

## 更新本机索引

新增文件后先按底层文献库说明跑 `paperlist.py build` 和 `ocr`，再跑 `corpus_rag.py build`。最后运行 `corpus_vectors.py build`、`corpus_semantics.py build` 和 `citation_claims.py build`。各层可续跑。`corpus_rag.py build --refresh` 会重扫旧论文的参考文献，发现以新入库论文为目标的旧引用。语义层和归因层基于正文及候选引用变化增量更新。修改概念词表后可用 `corpus_semantics.py --db <新文件> build` 重建，并给 `research_agent.py` 指定同一 `--semantic-db`。派生索引和本地模型保存在 `%LOCALAPPDATA%\PaperlistResearch`。[[Marketing Paper/Paperlist 研究知识库|底层文献库]]

在新机器上重建需要 Python 3.10+、SQLite FTS5，以及 `pyahocorasick`（构建引用网络）、`numpy`／`onnxruntime`／`tokenizers`（向量层）。这些依赖可装在环境中或放到 `%LOCALAPPDATA%\PaperlistResearch\rag-deps`。将 [固定版本的 MiniLM](https://huggingface.co/Xenova/all-MiniLM-L6-v2/tree/751bff37182d3f1213fa05d7196b954e230abad9) 的 `tokenizer.json` 和 `onnx/model_quantized.onnx` 放进同目录下的 `minilm-v1`，保留两个文件名。只有模型权重下载需要联网，构建与检索在本机运行。

## 维护证据图谱

`Marketing Paper/research_graph.json` 是可版本管理的事实层。论文节点保存稳定 ID、正式发表年、题目、来源和阅读状态；章节映射是可选的闭区间 PDF 物理页。关系从较早论文指向后续论文：`extends_component`、`limits_result`、`contrasts_assumptions`、`endogenizes` 等用来说明模型或结论具体怎样变；`cites` 仅表明引用。每条关系写 `claim`、`changed`、`limit`、审核状态及 `evidence` 中具体论文和物理页。未读原件或只看摘要／引用语境的关系标 `screened` 或 `candidate`；只依据参考文献出现不得标为模型继承。`validate` 检查结构、目录与页存在，不会替代人或 Agent 审核主张。三张独立卡的缺失会单列，不遮蔽其 PDF 证据，也不会自动恢复文件。

配套笔记：[[Marketing Paper/Paperlist 研究知识库|底层文献库]]、[[Marketing Paper/精读台账与研究流程|精读台账]]、[[Marketing Paper/研究谱系/定向广告与定向定价 - 研究谱系|首条研究谱系]]。

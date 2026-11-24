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

第一层是可重建的**自动索引**：全文段落带 PDF 物理页及推断的章节；标题／逐页全文、章节段落 BM25 和本地论文向量合并排序。向量编码标题和识别出的摘要，没识别到摘要则用开篇文字；它负责找候选论文，不直接定位命题。第二层是**自动引用网络**：从参考文献用题名、相邻作者和年份识别本地原件，支持向前、向后、多跳和共同引用检索。第三层是**已审核研究图谱**：只记录 Agent 实际核了正文、知道改了什么假设和哪条结果改变的连接。这三层的覆盖率不能互相替代。

此次全库自动索引：**47,568 份 PDF**，**918,124 个可检索来源页**，切成 **3,530,738 个正文段落**；生成 **47,567 个论文级向量**，剩下一件无可检索正文。识别 **219,911 条参考文献区内候选引用**和 **1,890 条未定位参考文献标题时的尾页候选**。有 30,643 个来源文件至少匹配到一条本地引用。仍不是逐篇精读。检测到章节标题的文档有 37,890 份；检测不到时正文仍可搜，不要依赖严格章节过滤做穷尽排查。

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
```

- `brief` 中 `corpus_rag.ranked_candidates` 列出融合排名和命中渠道；`passages` 提供候选篇章和原页；`dense` 披露实际向量覆盖，未启用或不可用会明确标记。`lineage`、`compare`、`write` 模式围绕候选和手动 `--citation-seed` 展开自动网络。日期和期刊筛选限制检索候选，不限制追溯前驱；自动层的年份来自文件名，不是正式引文年份。
- `corpus_rag.py context` 给出参考文献证据和正文作者-年份命中。`related` 用共享参考文献找没有直接相互引用的近邻。两者都需要回原文才能判断理论关系。自动引用会漏掉题名异译、短题名、作者或年份不一致及未收录论文，并可能误连；默认不查低置信尾页，确有需要再加 `--include-tail`。
- `trace`/`path` 只查审核图谱，与全库候选引用分开。`path --include-screened` 可以查看带暂定环节的审核图谱链。引用路径不等于因果证明或模型继承。
- `evidence` 支持稳定的图谱论文 ID 或索引数字 ID。未知章节明确报错，仍可手动指定 PDF 页；章节定位目前仅为已核对论文的页范围，页与页之间可能跨节。公式、印刷页码和引文要查 PDF 原页。

## 更新本机索引

新增文件后先按 [[Marketing Paper/Paperlist 研究知识库|底层文献库]] 的说明跑 `paperlist.py build` 和 `ocr`，再跑 `corpus_rag.py build` 及 `corpus_vectors.py build`。它们可续跑。普通构建处理新增和变化的文件；新论文也可能是过去的引用目标，运行 `corpus_rag.py build --refresh` 才会重扫旧 PDF 的参考文献。派生索引和本地模型在 `%LOCALAPPDATA%\PaperlistResearch`，无需放进 Git。原件不改动；未使用外部引文服务，也未上传或微调论文语料。

在新机器上重建需要 Python 3.10+、SQLite FTS5，以及 `pyahocorasick`（构建引用网络）、`numpy`／`onnxruntime`／`tokenizers`（向量层）。这些依赖可装在环境中或放到 `%LOCALAPPDATA%\PaperlistResearch\rag-deps`。将 [固定版本的 MiniLM](https://huggingface.co/Xenova/all-MiniLM-L6-v2/tree/751bff37182d3f1213fa05d7196b954e230abad9) 的 `tokenizer.json` 和 `onnx/model_quantized.onnx` 放进同目录下的 `minilm-v1`，保留两个文件名。只有模型权重下载需要联网，构建与检索在本机运行。

## 维护证据图谱

`Marketing Paper/research_graph.json` 是可版本管理的事实层。论文节点保存稳定 ID、正式发表年、题目、来源和阅读状态；章节映射是可选的闭区间 PDF 物理页。关系从较早论文指向后续论文：`extends_component`、`limits_result`、`contrasts_assumptions`、`endogenizes` 等用来说明模型或结论具体怎样变；`cites` 仅表明引用。每条关系写 `claim`、`changed`、`limit`、审核状态及 `evidence` 中具体论文和物理页。未读原件或只看摘要／引用语境的关系标 `screened` 或 `candidate`；只依据参考文献出现不得标为模型继承。`validate` 检查结构、目录与页存在，不会替代人或 Agent 审核主张。三张独立卡的缺失会单列，不遮蔽其 PDF 证据，也不会自动恢复文件。

配套笔记：[[Marketing Paper/Paperlist 研究知识库|底层文献库]]、[[Marketing Paper/精读台账与研究流程|精读台账]]、[[Marketing Paper/研究谱系/定向广告与定向定价 - 研究谱系|首条研究谱系]]。

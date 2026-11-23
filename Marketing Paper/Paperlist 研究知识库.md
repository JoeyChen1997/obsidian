---
tags:
  - research
  - quantitative-marketing
  - analytical-modeling
aliases:
  - Paperlist
  - Theory 文献库
---

# Paperlist 研究知识库

用于 quantitative marketing 的 analytical modeling（theory）研究。原件位于 `C:\paperlist`，保持只读；这个 vault 保存检索工具和研究笔记，机器上的可重建全文索引在 `%LOCALAPPDATA%\PaperlistResearch\papers.sqlite3`。这是一个可以按需查询、逐页复核的本地语料库，不是对模型权重的训练，也不是已经逐篇审读的综述。

2026-11-23 首次建库：12 个期刊目录、47,568 个 PDF 均已编目；918,188 页中有 918,124 页可检索（其中 10,007 页来自 OCR）。47,526 件每页均有可检索文字，41 件部分页有文字，1 件仅有目录条目。后者为 JMR 的 `Oliver_1980_A Cognitive Model of the Antecedents and Consequences of Satisfaction Decisions.pdf`：本地这份文件的 11 页均渲染为空白，PDF 解析还报告了对象引用异常，建议补入一份可读副本。实际覆盖以 `status` 为准。

## 精读知识层

[[Marketing Paper/精读台账与研究流程|精读台账与研究流程]]区分「已编目」「已初筛」「正文与核心证明已读」。[[Marketing Paper/研究谱系/定向广告与定向定价 - 研究谱系|定向广告与定向定价：首个研究谱系]]示范如何把前驱、模型继承、结论反转和前向扩展接起来，并给出原文证据。后续回答研究问题时，同时用精读卡做综合、用全库索引找漏网近邻；未读原文的节点保持待核。

## 怎么用

可以直接问：「用 Paperlist 找与我的模型最相近的 theory 文献。我的设定是两家差异化卖家、平台先选抽成、卖家再选定价。请比较博弈时序、信息结构、均衡和结论反转的条件，并附 PDF 页码。」

- **找 nearest neighbors**：按主题查标题，也按模型词查正文；分别找相同商业情境和相同机制的论文。例如，「平台抽成」也应搜 `commission rate`、`revenue sharing`、`agency selling` 和 `two-sided market`。
- **提炼 benchmark**：记录参与者、效用与利润、动作、时序、信息集、均衡概念、关键参数区间；区分作者已证明的命题、自己的推论和未验算的扩展。
- **写 related literature**：按机制组织，不按期刊罗列；对最接近的论文写清「共享设定 → 实质差异 → 哪个预测改变」，不要把「用了另一个情境」误当理论贡献。写 novelty claim 前，检索向前和向后扩展；本库无结果不等于没有先例。
- **复核公式和引用**：全文命中只是线索。回看 PDF 原页和 appendix，核对不等号方向、上标下标、命题适用条件和 off-equilibrium deviations；正式引用前核对完整作者、发表年份、期刊、卷期、印刷页码和 DOI。工具返回的是从 1 开始的 **PDF 物理页**。

精读示例：[[Marketing Paper/文献卡/Moorthy 与 Shahrokhi Tehrani 2023 - Hotelling 定向投放与定价|Hotelling 定向投放与定价]]，含命题、证明骨架、数值复算和原文口径差异。后续用 [[Marketing Paper/Theory 文献卡模板|Theory 文献卡模板]] 记录模型指纹和关系证据。

## 检索范围与关键词

首轮通常看 **Marketing Science（MKSC）**、**Journal of Marketing Research（JMR）** 和 **Management Science（MS）**；机制检索不要局限于营销期刊。库中还包括 RAND Journal of Economics（RAND）、AEJ: Microeconomics（AEJ_Micro）、Journal of Political Economy Microeconomics（JPE_MICRO）、AER: Insights（AER_insight）、Econometrica（ECMA）、Journal of Political Economy（JPE）、Quarterly Journal of Economics（QJE）、Review of Economic Studies（RES）、American Economic Review（AER）。缩写取自目录，论文级期刊信息仍应以原文首页为准。

| 理论主题 | 英文检索词示例 |
| --- | --- |
| 产品差异化与定价 | `Hotelling`、`spatial competition`、`behavior-based pricing`、`price discrimination` |
| 渠道与纵向关系 | `double marginalization`、`wholesale price`、`vertical restraints`、`resale price maintenance` |
| 平台定价与进入 | `agency selling`、`self-preferencing`、`multi-homing`、`platform encroachment` |
| 广告、曝光与搜索 | `informative advertising`、`consideration set`、`consumer search`、`sponsored search` |
| 信号与信息设计 | `signaling`、`screening`、`Bayesian persuasion`、`strategic disclosure` |
| 动态博弈与学习 | `strategic consumers`、`switching costs`、`commitment`、`experimentation` |

## 本机命令

从 Obsidian vault 根目录运行。当前机器可用 Codex 自带的 Python；也可以换成任意带有 SQLite FTS5 和 `pypdfium2` 的 Python 3.10+。

```powershell
$paperPython = "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$paperTool = '.\Marketing Paper\paperlist.py'
& $paperPython $paperTool status --journals
& $paperPython $paperTool catalog 'vertical restraints' --limit 15
& $paperPython $paperTool search 'Hotelling targeting' --journal MKSC --from-year 2015 --limit 10
& $paperPython $paperTool search 'informational differentiation' --phrase --paper 24726 --limit 3 --per-paper 3
& $paperPython $paperTool page 24726 4
& $paperPython $paperTool issues --limit 30
```

`catalog` 查文件名推断出的标题和首作者，不是正式引文数据库。`search` 按 PDF 页匹配，默认所有输入词要出现在同一页，每篇只返回排名最高的一页；可用 `--phrase` 匹配词组、`--paper` 限制到一篇、`--per-paper 3` 多看几页，或多次传入 `--journal`。检索会命中参考文献、书评和封面，要主动检查文章类型及命中位置。词法搜索不会自动联想同义词，也不等于语义搜索；建议并行换词。`source` 标明命中来自 PDF 文字层（`pdf_text`）还是本机 OCR（`ocr`）。`page` 的纯文本用于跳转及预览，不适合直接转抄公式。示例 ID 适用于当前数据库；完整重建后先用 `catalog` 查新 ID。

新增论文后运行 `& $paperPython $paperTool build`，再运行 `& $paperPython $paperTool ocr` 补查无文本页。原件与全文不会上传。首次构建或中断后可续跑；`status --journals` 给出当前真实覆盖，`issues` 列出仅部分页有文字、全件无可检索文字、或打开失败的文件。`indexed` 表示各物理页都有可检索文字，不代表每页文本完整或数学公式无损。文件名推断结果有重复、年份偏差或非论文条目的可能，统计单位是本地 PDF 文件，非去重论文数，也不代表期刊历年出版物齐全。

首次在另一台 Windows 机器上设置本地英文 OCR（本机已配置）：

```powershell
$paperOcrDeps = Join-Path $env:LOCALAPPDATA 'PaperlistResearch\ocr-deps'
& $paperPython -m pip install --target $paperOcrDeps winrt-Windows.Media.Ocr winrt-Windows.Globalization winrt-Windows.Graphics.Imaging winrt-Windows.Storage.Streams
```

需要 Windows 的英语（美国）OCR 语言包和 Python 的 Pillow。OCR 只用于没有抽取到文字的页；已有少量但残缺文字层的页不会自动重识别。未获得可检索文字的页可能是空白、纯图或识别失败，仍可查看原件。

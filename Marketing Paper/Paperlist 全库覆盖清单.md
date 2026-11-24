---
tags: [research, research/reading-ledger]
---

# Paperlist 全库覆盖清单

这是来源级可审计清单的入口，不是已去重的论文总表。清单从本机 `papers.sqlite3` 的所有来源记录生成，逐条关联审核图谱中的作品 ID、阅读状态及可用文献卡。原件保持只读。只见自动检索、题名或向量命中的来源仍显示 `not_reviewed`。

第六批结账：**47,568 个来源记录**，20 个来源关联到 **19 个有本地来源的图谱作品**（16 篇核心核读，3 篇初筛）；**47,548 个来源的作品身份待核**。另有 2 个图谱作品尚未定位本地来源。现有索引有 41 个来源仅部分页有文本、1 个无文本；读取状态与文本质量是两个字段。42 组（84 份文件）规范化题名相同；1 组已核为同一作品，其他不自动合并。3 张历史文献卡缺文件，原 PDF 页仍可查。

第七批结账：22 个来源关联到 **21 个有本地来源的图谱作品**（18 篇核心核读，3 篇初筛）；**47,546 个来源的作品身份待核**。既有版次、图谱来源缺口及历史文献卡缺口数量未变。未把第八批候选计入核心核读。

第八批结账：24 个来源关联到 **23 个有本地来源的图谱作品**（20 篇核心核读，3 篇初筛）；**47,544 个来源的作品身份待核**。Zou–Zhou 的文件名标 2024 在线年，按 2025 卷期存作品年。既有重刊分组与其余缺口数未变。

第九批结账：26 个来源关联到 **25 个有本地来源的图谱作品**（22 篇核心核读，3 篇初筛）；**47,542 个来源的作品身份待核**。新增 5594 的经核作品身份和可见核心证据，不把该 PDF 的索引状态改为全页可读。

第十批结账：28 个来源关联到 **27 个有本地来源的图谱作品**（24 篇核心核读，3 篇初筛）；**47,540 个来源的作品身份待核**。两个既有来源缺口重查：Thisse–Vives（1988，*On the Strategic Choice of Spatial Price Policy*）、Ben Elhadj-Brahim 等（2011，*Is Targeted Advertising Always Beneficial?*）。按作者及精确题名查本地目录和全文检索均未定位独立原件；检索只见相关或引述材料，不能把后文引述当原文。未核外部可得性，不标作确定不可得。

第十一批结账：30 个来源关联到 **29 个有本地来源的图谱作品**（26 篇核心核读，3 篇初筛）；**47,538 个来源的作品身份待核**。来源 47479 与 41833 是同作者、不同发表与不同模型的独立作品。来源 7082 的独立补证没有在本地同题名或 DOI 路径下定位；该缺口与已核主文、既有两项完整论文来源缺口分开。

来源缺口核查：唯一完全无索引文本的来源 14679（JMR，文件名为 Oliver 1980 *A Cognitive Model of the Antecedents and Consequences of Satisfaction Decisions*）确实存在且未加密。Poppler 提取不到首页正文、渲染首页为空白，扫描图像对象时报内容流语法错误；独立 PDFium 逐页检查 11 页均无提取文本且未渲出可读正文。留作本地不可读；不把文件名当作已核作品身份，不把失败归成等候 OCR 的正常扫描件。下一步找可读取的同刊副本并核身份；原件未修改。

部分文本抽核：来源 5594（AER: Insights，Armstrong–Vickers 2019，DOI 10.1257/aeri.20180581）的索引有 15/16 页文本。PDF 15（刊页 271）包含结尾与参考文献；PDF 16 的证据接口无文本、Poppler 渲染为空白。首页刊期范围写 257–272，未用其他版本确认刊页 272 是否本应空白。第九批核读了可见正文和核心证明，保留末页的来源问题，并未把它计入已核内容。

从 vault 根目录运行：

```powershell
$paperPython = "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$coverageTool = '.\Marketing Paper\reading_coverage.py'
& $paperPython -B $coverageTool status
& $paperPython -B $coverageTool queue --journal MKSC --state not_reviewed --limit 20
& $paperPython -B $coverageTool queue --issues-only
& $paperPython -B $coverageTool versions 34637
& $paperPython -B $coverageTool versions 24382
```

`queue` 可分页遍历全部来源，包括目录中曾存在但已缺失的文件；把返回的 `next_after` 传给下一页的 `--after`。题名候选组号只对当次目录有效，跨批使用稳定来源 ID。`versions` 同时展示规范化题名相同的候选和已核同作品的来源。已核版次要有同一作品的原页证据；不同 DOI 不必然是不同作品（Jeuland 2008 重刊即如此）。重刊有独立原页和来源级阅读状态，不继承原版的已读状态。

[[Marketing Paper/Paperlist 持续研究总纲|研究总纲]] · [[Marketing Paper/精读台账与研究流程|精读台账]]

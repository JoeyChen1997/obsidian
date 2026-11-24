---
tags: [research, research/reading-ledger]
---

# Paperlist 全库覆盖清单

这是来源级可审计清单的入口，不是已去重的论文总表。清单从本机 `papers.sqlite3` 的所有来源记录生成，逐条关联审核图谱中的作品 ID、阅读状态及可用文献卡。原件保持只读。只见自动检索、题名或向量命中的来源仍显示 `not_reviewed`。

第六批结账：**47,568 个来源记录**，20 个来源关联到 **19 个有本地来源的图谱作品**（16 篇核心核读，3 篇初筛）；**47,548 个来源的作品身份待核**。另有 2 个图谱作品尚未定位本地来源。现有索引有 41 个来源仅部分页有文本、1 个无文本；读取状态与文本质量是两个字段。42 组（84 份文件）规范化题名相同；1 组已核为同一作品，其他不自动合并。3 张历史文献卡缺文件，原 PDF 页仍可查。

第七批阶段核验：Berman–Katona 已入库。21 个来源关联到 **20 个有本地来源的图谱作品**（17 篇核心核读，3 篇初筛）；**47,547 个来源的作品身份待核**。既有版次、来源及文献卡缺口数量未变。第七批仍在进行，未把其余两篇首页核对计入核心核读。

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

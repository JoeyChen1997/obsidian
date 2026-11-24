---
tags: [research, research/reading-ledger]
---

# Paperlist 全库覆盖清单

这是来源级可审计清单的入口，不是已去重的论文总表。清单从本机 `papers.sqlite3` 的所有来源记录生成，逐条关联审核图谱中的作品 ID、阅读状态及可用文献卡。原件保持只读。只见自动检索、题名或向量命中的来源仍显示 `not_reviewed`。

第二批结账：**47,568 个来源记录**，其中 **12 个已关联图谱作品**（8 个正文与核心证明已读、3 个初筛、1 个排队），**47,556 个来源的作品身份待核**。另有 2 个图谱作品尚未定位本地来源。现有索引有 41 个来源仅部分页有文本、1 个无文本；读取状态与文本质量是两个字段。42 组（84 份文件）规范化题名相同，仅排入版次核查，不自动合并。3 张历史文献卡缺文件，原 PDF 页仍可查。

从 vault 根目录运行：

```powershell
$paperPython = "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$coverageTool = '.\Marketing Paper\reading_coverage.py'
& $paperPython -B $coverageTool status
& $paperPython -B $coverageTool queue --journal MKSC --state not_reviewed --limit 20
& $paperPython -B $coverageTool queue --issues-only
& $paperPython -B $coverageTool versions 34637
```

`queue` 可分页遍历全部来源，包括目录中曾存在但已缺失的文件；把返回的 `next_after` 传给下一页的 `--after`。题名候选组号只对当次目录有效，跨批使用稳定来源 ID。`versions` 只查规范化题名完全相同的本地候选，未命中不能证明没有工作稿、重刊或单独附录。下一步核对正式 DOI、卷期、作者与正文／附录，逐步把临时来源记录归入持久作品身份。

[[Marketing Paper/Paperlist 持续研究总纲|研究总纲]] · [[Marketing Paper/精读台账与研究流程|精读台账]]

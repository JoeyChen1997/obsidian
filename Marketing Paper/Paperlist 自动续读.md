# Paperlist 自动续读

## 推荐：使用已登录的 Codex 桌面版

在 Codex 桌面版打开 **Automations**，新建本地任务 `Paperlist · 自动精读与文献卡`。项目选择当前 Obsidian vault：`C:\Users\Joey Cheun\Documents\Obsidian Vault`，直接在原项目目录运行，不选 Git worktree。若可选每 30 分钟，则沿用原节奏；否则先选每小时。无需为了这条路径登录 npm 版 CLI。见 [OpenAI 官方的 Automations 说明](https://openai.com/index/introducing-the-codex-app/#delegate-repetitive-work-with-automations)。

任务指令直接粘贴：

```text
在 Windows 本机的原 Obsidian vault 项目中续读 Paperlist。项目根目录必须是 C:\Users\Joey Cheun\Documents\Obsidian Vault；若在其他目录或临时 worktree，则停止，并报告路径问题。先完整读取 Marketing Paper/automation/reading-prompt.md 并执行其中的核读规则；那份指令按 Marketing Paper 子目录书写，执行它时以该子目录为工作基准，从 vault 根读取 .agents/skills/paperlist-research/SKILL.md。以逐篇核读批次队列的当前入口为准，不固定来源编号。只读 C:\paperlist；不要修改、上传 PDF、开外网检索或改调度配置。每次直接核读并写回原 vault 的卡片、图谱和续读记录；书评、重刊和勘误不计新论文。不能访问源目录、不能写回原 vault 或发现另一核读任务正在写入时，停止且不要推进游标。最后报告本轮处理的来源、更新后的已核论文数和下一入口。
```

保存后在桌面版手动运行一次（如果界面提供 **Run now**）。验收看原 vault 的[[Marketing Paper/逐篇核读批次队列|续读队列]]是否推进，并确认新增论文有文献卡、图谱校验通过。起点可能是书评：如果只核到书评，独立论文数不变，图谱的排除记录和队列应当更新。若只看到任务报告、原 vault 没变化，不算试跑成功。两种调度器不要同时写同一个台账；切换前核对下方旧任务状态，确认旧任务未在写入。桌面任务验证成功后，停用旧任务，不必删除。

## 备用：Windows 任务计划程序

Windows 任务计划程序中的任务名是 `Paperlist Research - Continue Reading`。它以当前 Windows 用户的普通权限运行，不保存 Windows 密码；每 30 分钟启动一次，同一时间只运行一份，每次上限 25 分钟、最多处理 3 个来源（其中最多 2 篇独立论文）。电脑须开机并保持 Windows 用户登录，锁屏可以；计划采用系统默认的交流供电条件，不主动唤醒电脑。

旧脚本调用 `%APPDATA%\npm\codex.cmd`。只有这个独立启动入口能认证时，旧任务才会开始；这和桌面版或 Obsidian 插件会话的登录状态不同。未登录时，旧任务只记录阻塞状态，不改台账。账号额度适用于每次模型调用。PDF 不做文件上传；核读所需的提取文本会作为模型上下文处理。

看进度：[[Marketing Paper/精读台账与研究流程|精读台账]]及[[Marketing Paper/逐篇核读批次队列|续读队列]]。运行状态在 `%LOCALAPPDATA%\PaperlistResearch\automation\reading.log`，日志不保存论文原文。`blocked Codex CLI not signed in` 表示触发正常、未启动模型；`finished` 同时列出 CLI 退出码和经校验的已核数，没有新增不等同于读完。

从 PowerShell 立即试跑：`Start-ScheduledTask -TaskName 'Paperlist Research - Continue Reading'`。暂停后续触发：`Disable-ScheduledTask -TaskName 'Paperlist Research - Continue Reading'`；已在跑的这一轮如需立即停，用 `Stop-ScheduledTask -TaskName 'Paperlist Research - Continue Reading'`。恢复：`Enable-ScheduledTask -TaskName 'Paperlist Research - Continue Reading'`。手工推进同一份队列前请先暂停自动任务，避免双方同时改台账。

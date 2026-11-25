# Paperlist 自动续读

Windows 任务计划程序中的任务名是 `Paperlist Research - Continue Reading`。它以当前 Windows 用户的普通权限运行，不保存 Windows 密码；每 30 分钟启动一次，同一时间只运行一份，每次上限 25 分钟、最多处理 3 个来源（其中最多 2 篇独立论文）。电脑须开机并保持 Windows 用户登录，锁屏可以；计划采用系统默认的交流供电条件，不主动唤醒电脑。

本机 Codex CLI 需要登录一次。在 PowerShell 运行 `codex login`，完成浏览器登录，再用 `codex login status` 确认；不要把密钥发到聊天。未登录时，任务只记录阻塞状态，不改台账。账号额度适用于每次模型调用。PDF 文件不会被上传；核读会与当前对话中的 Codex 一样，将所需的提取文本作为模型上下文处理。

看进度：[[Marketing Paper/精读台账与研究流程|精读台账]]及[[Marketing Paper/逐篇核读批次队列|续读队列]]。运行状态在 `%LOCALAPPDATA%\PaperlistResearch\automation\reading.log`，日志不保存论文原文。`blocked Codex CLI not signed in` 表示触发正常、未启动模型；`finished` 同时列出 CLI 退出码和经校验的已核数，没有新增不等同于读完。

从 PowerShell 立即试跑：`Start-ScheduledTask -TaskName 'Paperlist Research - Continue Reading'`。暂停后续触发：`Disable-ScheduledTask -TaskName 'Paperlist Research - Continue Reading'`；已在跑的这一轮如需立即停，用 `Stop-ScheduledTask -TaskName 'Paperlist Research - Continue Reading'`。恢复：`Enable-ScheduledTask -TaskName 'Paperlist Research - Continue Reading'`。手工推进同一份队列前请先暂停自动任务，避免双方同时改台账。

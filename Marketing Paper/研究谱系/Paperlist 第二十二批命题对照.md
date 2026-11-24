---
tags: [research/theory, research/lineage]
batch: paperlist-22
---

# Paperlist 第二十二批命题对照

## 轮流行动如何改变“算法合谋”的含义

| 论文 | 时序／策略 | 核心结论和边界 |
| --- | --- | --- |
| [[Marketing Paper/文献卡/Maskin 与 Tirole 1988 - 动态寡头与 Edgeworth 周期|Maskin–Tirole（1988）]]（本地正文） | 轮流报价，状态是对手当前价，允许 Markov 混合反应 | 细格点、$\delta$ 近 1 时存在固定焦点和 Edgeworth 周期 MPE；周期重置在低价处混合。Propositions 7–9，PDF 18–22。 |
| [[Marketing Paper/文献卡/Klein 2021 - 序贯定价与算法周期|Klein（2021）]] | 轮流报价，同一状态，但 Q-learning 纯策略、$\varepsilon$-greedy | $k=6$ 时常达到高利润近似 Nash；$k=24$ 时出现确定性非对称锯齿周期。作者明确说这不是理论随机周期，因为纯策略不能学到沿路径混合。PDF 9–15。 |
| [[Marketing Paper/文献卡/Calvano 等 2020 - 重复定价与 Q-learning|Calvano 等（2020）]] | 同时报价、差异化 logit、价格历史状态 | 高利润及偏离—恢复来自同时行动的学习路径；不可把其惩罚图直接当作轮流报价的反应函数。PDF 7–16。 |

**最重要的关系：** Maskin–Tirole 的 $V/W$ 两个方程合并后正是 Klein 的两期 Bellman；这是继承的时序结构。另一个可核的继承是 Calvano 强制偏离的事后诊断，但两篇不是只改时序：需求与状态也变了。应分开（i）固定焦点上的一次性偏离—恢复，（ii）长期的确定性重启路径，（iii）Table II 里经过全状态最优性要求的随机重启。Calvano 的稳定策略也可能出现价格周期（PDF 10–11），不能把所有同时定价运行都说成固定价格。

复核：Table II 低价处的等待概率可由零价无差异式独立推出；$\delta=.95$ 和 $.99$ 时，对七个状态枚举所有一次偏离均未发现正改进（数值容差 $10^{-10}$）。相反，Klein 的 Fig. 3 仅对 241 个达联合利润最大化的 Nash 运行检验偏离，Fig. 7 仅展示细网格模拟最初三次的锯齿示例；$\Gamma_i$ 使用估计的 Q 值，不能把图形与比值都当成 MPE 证明。

## 审计

检索词：`sequential pricing price cycles`、`alternating price setting learning`、`markov perfect edgeworth cycles`；语义问句 `How do alternating price commitments produce Edgeworth cycles, and do reinforcement learners recover the dynamic equilibria rather than grid artifacts?`，以 Klein 42925、Calvano 1959 为种子。融合候选前三为 Klein（42925）、Wang（22960）、Maskin–Tirole（9708）；三者均进入自动邻域时间线。Wang 先核首页，不在本批升为经核关系。另用目录精确题名找到 9709，原 PDF 2 确认为 1989 erratum，登记为同研究的关联勘误，不是独立研究或重刊。

三张旧卡状态：Chen–Iyer（2002）、Iyer 等（2005）、Moorthy–Shahrokhi Tehrani（2023）的原 PDF 仍在 `C:/paperlist`，三张 Markdown 卡在 Git 备份提交 `a4eab3a...` 有内容、在后续备份 `1fe9a7a...` 被删除。为保护当前工作区，本批不自动恢复；这属于可恢复历史，不是来源缺失。JMR Oliver（14679）仍是本地不可读 PDF，另列来源缺口。

下一批已核 Wang PDF 1，第一项工作是核正文对“同步改价”与“全日承诺”的区分、混合重启检验及样本分母；另回查 Maskin–Tirole Part I（9707）对行动时序的原始构造，不把同年同作者的价格篇和数量篇误合并。

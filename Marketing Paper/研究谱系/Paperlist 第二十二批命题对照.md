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

**最重要的关系：** Klein 不是简单“把 Calvano 的 Q-learning 换成另一个市场”。他把同时移动改为 Maskin–Tirole 的轮流移动，结果的周期形状从 Calvano 的短期偏离后恢复，变成细格点下由一方确定性重置的长期 Edgeworth 型循环。Maskin–Tirole 提供的是可混合的 Markov-perfect 均衡；Klein 的 $\Gamma_i$ 和 Nash 比例是模拟后的诊断，不是算法有理论收敛保证。

## 审计

检索词：`sequential pricing price cycles`、`alternating price setting learning`、`markov perfect edgeworth cycles`；语义问句 `How do alternating price commitments produce Edgeworth cycles, and do reinforcement learners recover the dynamic equilibria rather than grid artifacts?`，以 Klein 42925、Calvano 1959 为种子。自动候选含 Maskin 9708、Noel 22960 和 Klein；本批只把 Maskin 9708 的原 PDF 核入关系。9709 是 1989 erratum，记录为版本修正，不是新独立作品。

三张旧卡状态：Chen–Iyer（2002）、Iyer 等（2005）、Moorthy–Shahrokhi Tehrani（2023）的原 PDF 仍在 `C:/paperlist`，三张 Markdown 卡在 Git 备份提交 `a4eab3a...` 有内容、在后续备份 `1fe9a7a...` 被删除。为保护当前工作区，本批不自动恢复；这属于可恢复历史，不是来源缺失。JMR Oliver（14679）仍是本地不可读 PDF，另列来源缺口。

下一批优先核 Klein 的“自身价格进状态”与 Calvano 一期记忆的真正可比维度，再处理三张卡是否恢复的台账决策。不要把 1989 erratum 重复计入论文，也不要把 Klein 的确定性周期写成 Maskin–Tirole 的随机均衡。

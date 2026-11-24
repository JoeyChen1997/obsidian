---
tags: [research/theory-paper, research/empirical-paper]
paper_id: derakhshan-et-al-2022-product-ranking
reading_status: core_read
doi: 10.1287/mnsc.2021.4044
---

# Derakhshan 等（2022）：平台产品排序与逐位筛选

Mahsa Derakhshan, Negin Golrezaei, Vahideh Manshadi, Vahab Mirrokni. *Product Ranking on Online Platforms*. Management Science 68(6), 4024–4041；2022 在线与卷期。来源 28554；PDF 页 = 刊页 − 4023。核摘要、经验动机、两阶段模型、Theorem 1、Theorems 2–5、Props. 1–2 和数值部分；详细证明在 e-companion，未独立核。

## 两阶段搜索：这里确实是按页面向下看

平台展示位置排名。消费者第一阶段逐位观察 preference weight，形成 consideration set；第二阶段才观察每个入选品的 idiosyncratic utility，并在其中选最高者。位置越靠后，screening cost 越高。消费者并非先看完整排序后自由择序，而是在给定位置成本下由最优策略逐步向下筛选。Theorem 1 证明 index-based policy：从顶部向下，直到已筛选权重之和超过所有未筛选位置的 reservation price。PDF 3–5、10。

高权重品放在顶部会给低位品施加外部性：它提高当前考虑集的总权重，却让消费者更早停止，从而可能缩小 consideration set。经验图 1 显示平台排序下前 5 位购买概率更高，但低于第 13 位的位置购买概率比随机排序更低；双品种对照中，把更受欢迎品放在顶部可能使总购买率下降。PDF 2–3。

## 平台目标与算法边界

按 preference weight 排序很直观，却不必最大化市场份额或消费者福利。市场份额和福利排序问题均 NP-complete；w-ordered 排序有强保证：市场份额至少达到最优的一半，亦有约 0.1716 的加性保证；消费者福利至少比最优低 $\log 2\approx0.6931$。论文提出近似算法／PTAS，模型估计只在数值部分展示，完整证明在 e-companion。PDF 10–16。

与 [[Marketing Paper/文献卡/Compiani 等 2024 - 在线搜索与最优产品排序|Compiani 等（2024）]] 不同，本篇把“按页面位置逐位筛选”作为由位置相关成本推出的最优行为；Compiani 允许消费者任意选择下一个商品。与 [[Marketing Paper/文献卡/Weitzman 1979 - 潘多拉规则与保留值|Weitzman（1979）]] 也不同：本篇筛选后只观察权重，之后还要在 consideration set 中支付／揭示 idiosyncratic utility，因此原 Pandora 证明不能直接套用。

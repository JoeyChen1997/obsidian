---
tags: [research/theory, research/lineage]
batch: paperlist-18
---

# Paperlist 第十八批命题对照

组合大小和排序位置是两个不同的干预。前者改变可得选项集合；后者改变消费者先看到什么、愿意查什么，以及平台是否把“高质量但不显眼”的品放到前面。

| 作品 | 识别／模型 | 可迁移结论与边界 |
| --- | --- | --- |
| [[Marketing Paper/文献卡/Ursu 2018 - 排名与在线搜索购买|Ursu（2018）]] | Expedia 随机排名实验；点击代表搜索，购买代表最终成交；用 Weitzman 顺序搜索联合估计。 | 排名显著改变搜索对象，但条件于已搜索不显著改变购买；位置效应约 $0.55$–$3.19$。排名因果效应与排名内生性分开。PDF 3、17–20。 |
| [[Marketing Paper/文献卡/Compiani 等 2024 - 在线搜索与最优产品排序\|Compiani 等（2024）]] | 延用 Weitzman 型搜索，但分开 search index 与 utility index；随机排名训练、Expedia 算法测试，用 exploded logit 估计后做排序反事实。 | 消费者剩余排序偏向“diamond in the rough”，静态收入排序偏向高利润品；OPT3G-CS 相对 Expedia 同时提高剩余和收入，但这是模型反事实，不是长期留存估计。PDF 1–4、8、14、18–19。 |
| [[Marketing Paper/文献卡/Natan 2025 - 大型组合的选择摩擦|Natan（2025）]] | 配送边界局部准实验和 rational inattention；没有具体排名、推荐和单个 impression。 | 组合变大提高新客采用、降低老客频率；不能由此识别排序展示效应。Natan 的排序不可观测正是 Compiani／Ursu 这条分支的来源缺口。PDF 7–15。 |

## 关系与缺口

- 已核 3 条关系：Weitzman → Compiani 是搜索组件扩展；Choi–Dai–Kim → Compiani 是有效指数组件；Ursu → Compiani 是同 Expedia 随机排名数据从因果位置效应到最优排序的推进。均有原文讨论和双侧页码；不把 Compiani 的排序反事实当成 Natan 的平台组合识别。
- Compiani 的关键假设是消费者可以任意择序搜索，排名改变 search index，而非强制按页面顺序搜索；文中说明超过 80% 的训练印象不符合“按页面顺序搜索”。因此它和只把位置当作强制序列的模型不是同一机制。
- Natan OA1–OA6、数据文件和平台实际排名未在 `C:/paperlist` 定位；Compiani Online Appendix A–H、数据和代码也未定位。正文中的页码、表和识别假设已核，补充材料不继承核心读状态。
- 无题名、以 `optimal product rankings`、`ranking position search cost`、`random ranking booking conversion` 和 “How do randomized rankings identify the causal effect of product position on search and purchase, and how can a platform optimize ranking under search costs?” 检索，Ursu（25165）排第 1，Compiani（23911）进入候选；Compiani 的语义图回溯到 Choi 等、Weitzman。检索排名不是全库召回率。

下一批优先核 Donnelly（23990）的个性化排序与福利目标，再核 Derakhshan（28554）是否强制按页面顺序搜索，以裁决排序呈现、个性化和动态留存之间的边界。

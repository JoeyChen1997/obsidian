---
tags: [research/empirical-paper, research/theory-paper]
paper_id: compiani-et-al-2024-optimal-rankings
reading_status: core_read
doi: 10.1287/mksc.2022.0071
---

# Compiani 等（2024）：在线搜索与最优产品排序

Giovanni Compiani, Gregory Lewis, Sida Peng, Peichun Wang. *Online Search and Optimal Product Rankings: An Empirical Framework*. Marketing Science 43(3), 615–636；2023-12-21 在线，2024 卷期。来源 23911；PDF 页 = 刊页 − 614。核 §§1–4.5、Lemma 1、Props. 1–3、算法保证、Expedia 训练／测试设计、表 5–8；Online Appendix A–H、原始数据和完整模拟代码未独立核对。

## 平台改变的是搜索指数，不只是展示顺序

平台为一个查询选择产品排列。消费者可按任意顺序搜索，搜索揭示个体匹配，也可能揭示原先看不到的垂直质量；消费者因此对每个产品形成 search index（保留值）和 utility index。给定产品 $j$ 的搜索排名 $r_j$，排名函数 $f(r_j)$ 改变搜索指数。外部选项的搜索指数为 $+\infty$。这保留 Weitzman 的独立收益与可择序搜索框架，但允许平台掌握消费者看不到的平均质量信息。PDF 1–3、8，刊页 615–617、622。

- **Lemma 1（最终购买）**：产品的 effective index 是 $v_{ij}=\min\{s_{ij},u_{ij}\}$；消费者最终买 effective index 最高的产品。高平均效用但低 search index 的产品不一定成交，高 search index 但低效用的 clickbait 也不应占据高位。PDF 8，刊页 622。
- **潜力与排序**：潜力约为平均 utility 减去经排名调整的 search index。连续 ranking-budget 松弛下，消费者剩余最大化趋向于均衡不同产品的潜力，即优先推广“diamond in the rough”——预期质量高但不显眼的产品；静态收入最大化则偏向高利润产品。直接按 utility 排序不是一般最优。PDF 2–3，刊页 616–617。
- **离散算法**：对前 $K$ 位穷举、其余位置贪心；误差界随 $K$ 位之后的合计选择概率增加。模拟中算法获得可用消费者剩余／收入增益的 98% 以上，但这是相对给定模型的近似保证，不是全局最优的经验事实。PDF 4、11–13，刊页 618、625–627。

## 识别、估计和实证结果

Expedia 训练数据中的排名随机分配，测试数据使用 Expedia 算法；只用训练数据估计，再用测试数据外推验证。点击揭示搜索顺序，购买揭示最终选择，二者共同约束 search／utility index 的排序；exploded logit 似然避免把点击和成交混成单一结果。模型拟合了随机排名下前几位的点击概率，并解释算法排名下后位点击更少。PDF 14–19、22，刊页 628–632。

在测试样本中，OPT3G-CS 相对 Expedia 平均提高消费者剩余约 $1.205$、收入约 $0.084$，平均搜索次数只增加 0.0048；OPT3G-Rev 平均提高收入约 $0.558$，但消费者剩余下降约 $0.383$。按 utility 直接排序提高消费者剩余约 $0.594$，收入下降约 $0.152$。这些是 impression-level 模型反事实；论文提醒购买样本被过度代表，不能把数值直接解释为每位购买者的无条件福利。PDF 22–23，刊页 632–633。

## 与前后研究的边界

[[Marketing Paper/文献卡/Weitzman 1979 - 潘多拉规则与保留值|Weitzman（1979）]] 提供独立收益下的搜索顺序和停止；本篇把平台排名作为改变 search index 的控制变量。[[Marketing Paper/文献卡/Choi 等 2018 - 顺序搜索与有效估值|Choi 等（2018）]] 提供有效值／最终成交的组件，本篇明确以其结果为基础并扩展到平台排序和垂直质量。[[Marketing Paper/文献卡/Ursu 2018 - 排名与在线搜索购买|Ursu（2018）]] 使用同一 Expedia 排名随机化环境，但主要估计排名的因果位置效应；本篇用随机训练样本估计双指数后再优化排名。它不能直接识别 [[Marketing Paper/文献卡/Natan 2025 - 大型组合的选择摩擦|Natan（2025）]] 所说的组合大小效应，因为 Natan 看不到具体排名和单个 impression。

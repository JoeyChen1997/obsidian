---
tags: [research/theory-paper]
paper_id: bergemann-bonatti-2011
reading_status: core_read
doi: 10.1111/j.1756-2171.2011.00143.x
---

# Bergemann 与 Bonatti（2011）：广告市场的定向与费率

Dirk Bergemann and Alessandro Bonatti. *Targeting in Advertising Markets: Implications for Offline versus Online Media*. RAND Journal of Economics 42(3), 417–443. 本地来源：RAND/Bergemann_2011_Targeting in advertising markets implications for offline versus online media.pdf；刊页为 PDF 页 + 416。核读模型、核心竞争市场结果与印刷证明（重点 §§2–4、Appendix 对 Props. 1–5）；§§5–6 已定位，未逐条复算多媒体均衡。

## 模型

连续体的广告商各卖一种产品；买家只对一种产品感兴趣，分布在不同广告市场。产品价格与特征给定，成功触达匹配者的收益归一化。市场 $a$ 的受众量为 $s_a$，其中想买 $x$ 的量为 $s_{a,x}$。广告商在该市场购买 $m$ 条信息，独立随机曝光使匹配数为 $s_{a,x}(1-e^{-m/s_a})$。广告商按给定广告价 $p_a$ 买入；总供给为 $s_aM$，$p_a$ 由供需出清，而非媒体垄断利润最优（PDF 4–8、11–12）。

## 关键结果及复算

| 定位 | 命题 | 机制 |
| --- | --- | --- |
| PDF 9，Prop. 1；24，证明 | 单一广告市场中，产品市场集中度升高提高匹配量 | 将广告份额向高匹配概率的广告商集中。 |
| PDF 12，Prop. 3；24，证明 | 多市场中，定向精度 $\gamma$ 越高，总匹配量越高 | 在作者的分布和固定广告供给下，细分提高匹配效率；竞争出清分配有效。 |
| PDF 13，Prop. 5；25，证明 | 活跃广告商数随 $\gamma$ 下降；出清价仅当 $\lambda+\gamma<2/M$ 随 $\gamma$ 上升 | 高精度提高核心广告商对曝光的价值，但减少边际广告商；不能用匹配量推断价格或媒体收入。 |

独立复算（PDF 12，Eqs. 13–16）：令 $\kappa=\lambda+\gamma$，归一化广告强度 $(\ln(\kappa/p_a)-\kappa(x-a))_+$。在活跃范围积分得 $M=\ln^2(\kappa/p_a)/(2\kappa)$；故 $p_a=\kappa e^{-\sqrt{2M\kappa}}$，且 $\partial_\gamma\log p_a=(1-\sqrt{M\kappa/2})/\kappa$。若阈值不在可行参数区间，就不会观察到完整的先升后降。

与 [[Marketing Paper/文献卡/Zhu 等 2025 - 广告平台与隐私|Zhu 等（2025）]] 的可比组件是随机触达。两篇都让广告价内生，但一篇由市场出清且商品价给定，另一篇由垄断平台预见商品市场反应后选择费率，且商品价格一起调整。前文的匹配量不是后文的消费者剩余；没有把两个结果合成普适福利命题。见 [[Marketing Paper/研究谱系/Paperlist 第二批命题对照]]。

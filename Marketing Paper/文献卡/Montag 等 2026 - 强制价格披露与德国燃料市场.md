---
tags: [research/empirical, research/price-transparency]
reading_status: core_read
source_id: 23553
---

# Montag 等（2026）：强制价格披露与德国燃料市场

Felix Montag, Alina Sagimuldina, and Christoph Winter, *When Does Mandatory Price Disclosure Lower Prices? Evidence from the German Fuel Market*, Journal of Political Economy: Microeconomics 4(1), February 2026（在线 2025-12-15）。[DOI](https://doi.org/10.1086/734145)。本地 PDF 物理 1 为封面，正文页 2–41；文件名写 2024，不采用文件名年份。

## 模型与识别

- **模型**（PDF 7–12）：同质商品、$N$ 个卖家，原先只有份额 $\lambda$ 的 shoppers 知道全部价格，其余消费者随机遇一家后决定购买或支付 clearinghouse access cost 成为 informed；信息价值 VOI 是随机首家价与全市场最低价的期望差。均衡中卖家按 Varian 型混合策略定价，最低支持价、$F(p)$、$E[p]$ 和 $E[p_{min}]$ 依赖 informed share $\mu$。MPD 被建模为对所有信息获取成本的平行下移，不直接改变卖家成本或消费者估值。
- **比较静态**：Prediction 1，降低信息成本提高 $\mu^*$；Prediction 2，MPD 后 VOI 上升意味着事前 $\mu_0$ 在使 VOI 最大的 $\hat\mu$ 左侧；Prediction 3，$\mu_0<\hat\mu$ 时平均价下降幅度超过最低价，说明未充分知情者得到更大收益；Prediction 4，成本下移越大，$\mu^*$ 和价格下降越大。均衡可能有多个信息获取交点，作者用唯一性条件、模拟和数据映射，不把每个参数都证明为唯一根。
- **制度与样本**（PDF 13–18、23–29）：德国 MTU 于 2013-09-12 开始；对照是法国站点。主 SDID 用 2012-09-01 至 2013-08-31 的 pre-period 和 2013-10-01 至 2014-12-31 的 post-period，平衡面板只保留德国 47%、法国 94% 站点；另用全样本 DiD 和欧盟 Weekly Oil Bulletin 国家聚合数据。MPD 前德国价格报告是用户／站点混合来源，作者用报告强度、燃料种类和市场地理作描述性排查，不能把 SDID 当随机处理。

## 实证结果与证据边界

| 原 PDF | 结果 | 限制 |
| --- | --- | --- |
| PDF 30–31，Table 2、Figure 10 | 日对数价格：汽油主样本 MPD −0.027（SE .0004），柴油 −0.018；France 控制规格约 −0.030／−0.019。动态效应最初较大，数月后约减半但仍负。 | 这是价格处理效应，不直接等于消费者福利；平衡面板选择、报告频率及法国平行趋势仍是识别条件。 |
| PDF 32–34，Tables 3–5 | 5 km 重叠 driving-distance market：汽油平均价 −0.030、最低价 −0.024；柴油 −0.024、−0.018。竞争者越多，MPD 降价更强；垄断站也受同一路线上远站竞争影响。Radio Arabella 的价格报告额外降低价格，Extra-Radio 不显著。 | 市场重叠，不是互斥市场；广播接收区并非随机。最低价与平均价差异支持模型机制，但不识别每一位消费者的真实 $\mu$。 |
| PDF 35–38、41–44 | 德国 MPD 能降低价格，原因是卖家在 MPD 前已经高频观察对手，而消费者信息不足；高消费者采用、更多卖家和低 app 进入壁垒增强效果。与 Byrne 等（2025）的相对卖家信息退出不同。 | 这些是机制解释与分组证据，不是单独的结构参数识别；作者明确讨论信息共享既可能软化也可能强化竞争。 |

独立核读：Table 3 的汽油平均价 −.030 相比最低价 −.024，平均价多下降 .006 log 点，方向符合 Prediction 3；Table 4 中 MPD×5+ rivals 为 −.003，基准 −.022，不能直接相加解释为一般线性“每个竞争者效应”，因为是交互项规格。报告 2013-09-12 制度起点、2013-10-01 post 样本起点和 2014 年后动态结果，避免把文件名年份或电子发表年当处理日期。

补件：主文与印刷表、附录入口已核；Dataverse 与独立附录未重跑。下一轮按[[Marketing Paper/逐篇核读批次队列|逐篇核读队列]]进入 MKSC 23575；本批不新增谱系边。

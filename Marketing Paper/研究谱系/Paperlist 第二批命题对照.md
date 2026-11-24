---
tags: [research/theory, research/lineage]
batch: paperlist-02
---

# Paperlist 第二批命题对照

本批核读 [[Marketing Paper/文献卡/Bergemann 与 Bonatti 2011 - 广告市场的定向与费率|Bergemann–Bonatti（2011）]] 和 [[Marketing Paper/文献卡/Jerath 等 2017 - 库存风险与渠道质量|Jerath–Kim–Swinney（2017）]]。与[[Marketing Paper/研究谱系/Paperlist 首批命题对照|首批]]中的两篇逐项对照。

| 共同问题 | 旧模型 | 新模型 | 能比到哪一步 |
| --- | --- | --- | --- |
| 什么决定每条广告的价格？ | Bergemann–Bonatti：商品价给定，广告市场固定供给并竞争出清；定向提高匹配效率，但出清价的方向取决于 $M(\lambda+\gamma)$。PDF 12–13。 | Zhu 等：平台选费率；产品厂商在随后子博弈选广告和商品价；隐私改变能否按类型触达。PDF 3、6、9–11。 | 随机触达是共同组件；费率内生的方式不同，不能把匹配数、广告收入和消费者剩余当作同一结果。 |
| 分权为何可能提高质量？ | Shi 等：纯纵向均匀基准不能给出升质；非均匀支付意愿或纵横联合异质可改变排序。PDF 5–8。 | Jerath 等：仍用均匀纵向估值；引入随机市场规模、事前订货和事后定价，常数批发价把滞销风险交给零售商。PDF 3、6–7。 | 这给出另一种反转机制，而非扩展同一个需求特例。独立复算得到分权库存约 0.07450（直营 0.17934），但分权质量约 0.14183（直营 0.13678）。 |

## 检索核验

- 广告组：`brief --intent lineage`，种子 42104、24931，英文检索词 targeting advertising market / ad rates / competitive equilibrium，语义查询为 “How media competition and targetability determine equilibrium advertising prices”。引用归因找回该论文对，自动时序层未判定定价机制的对比。核两边原页后用审核路径补入。
- 渠道组：种子 34637、24377，检索 inventory risk / product quality / channel decentralization 加语义扩展。无稳定自动语义边；原页 PDF 7 有明确对照。两组都是有种子的查漏，不是召回率统计。
- 第 03 批留出检验（尚无审核边）：无种子 `brief --intent lineage --phrase 'inventory risk' --phrase 'advance purchase discount' --term 'push pull contract' --semantic 'Retailer or supplier bears unsold inventory risk before demand uncertainty resolves' --limit 10` 中，Cachon 排第 1，Jerath 未入前 10，自动图无这条边。下一步继续用双边原文区分建模借鉴、引用与平行机制。

## 待核与续跑点

广告组：先对照 Butters 的随机投递和最低所见报价机制，再追 Stegeman 的估值异质；分清推出价格分散与推出广告投入福利排序所需的不同假设。渠道组：从 Cachon 的 push/pull/advance-purchase 风险归属开始；确定性需求极限涉及分布条件与定价时序，不能直接令方差为零套用 IGFR 内点公式。Jerath 等独立在线附录中的协调契约详证尚未核。

---
tags: [research/theory, research/lineage]
batch: paperlist-20
---

# Paperlist 第二十批命题对照

同是首位增加成交，**改商品价格**和**为位置申报每售收益**不是同一动作。给定价格的最优排序和报价激励，不会自动在卖家能先改价的模型里成立。

| 论文 | 排序改变哪一步 | 能据此说什么 |
| --- | --- | --- |
| [[Marketing Paper/文献卡/Weitzman 1979 - 潘多拉规则与保留值|Weitzman（1979）]] | 搜索者按照未查选项各自的保留值决定下一步 | 同分布同成本的盒子共享停止阈值，谁先查不由保留值分出；不是平台排序目标。PDF 7–8。 |
| [[Marketing Paper/文献卡/Dinerstein 等 2018 - 搜索改版与价格竞争|Dinerstein 等（2018）]] | 价格可以影响出现于考虑集的概率，也影响给定考察集合后的选择 | $D=AQ$ 的弹性分解与定价一阶条件区分两条渠道；该式不是公共名次跳变点上的可微保证。PDF 23。 |
| [[Marketing Paper/文献卡/Chu 等 2020 - 排序与位置拍卖|Chu 等（2020）]] | 给定价格，平台分配位置、卖家报私有每售收益；消费者主观 i.i.d.，循公共列表搜索 | 即时成交有上游位置外部性，查完整列再回选不受排序影响。这个分解支持排序交换和前 $k$ 位收费机制，性能界只比较期望即时成交加权剩余。先行本 PDF 6–9、11–13、18。 |
| [[Marketing Paper/文献卡/Donnelly 等 2023 - 个性化排序与福利|Donnelly 等（2024）]] | 用户随机看到不同的现有零售排序，选查验集合；实验不另设卖家重新定价制度 | 行为差异是实验结果；结构模拟的福利估计每人 +$4.02（约 +18%），并非随机实验直接观察福利。PDF 6、8、17。 |
| [[Marketing Paper/文献卡/Qiu 等 2025 - 个性化排序与算法定价|Qiu 等（2025）]] | 卖家先公开报价，然后排序；买家可顺序查验，每期更换队列 | 同价反事实下，价格跨公共得分门槛可改变所有人的首位；个体名单只改变一部分。基准重复模拟中，个性化稳定价格更高、消费者剩余更低。PDF 4–9、14–16。 |

## 经核谱系与不应串成的因果链

- **Weitzman → Chu**：明确引入保留值组件，止搜用主观共同先验，实际不同位置的卖家仍有异质性。不能据此说平台排序是搜索者的 Pandora 择序，也不能据此推出拍卖性质。
- **Dinerstein → Qiu**：Qiu 明引其为统一质量–价格排名的文献依据。可连的是价格影响被看见或被考虑的渠道。Dinerstein 的 Eq. (14) 是可微处的弹性分解；Qiu 图 6 还包含公共名单离散换位，不能把表 3 的有限差分当作局部导数。
- **Chu → Qiu、Donnelly → Qiu**：以上两条是独立机制对照，箭头表示对照顺序，不声称后者继承前者。第一条辨认竞价与商品公开报价的差别；第二条辨认所见价格下的排序比较和含重复定价反馈的比较。不同搜索、平台和处理使福利符号不可直接归因给单一假设。

**独立核算。** Chu 交换相邻两卖家时，到达前缀的概率和通过二者后继续的概率不变，差额只由两家的跨阈概率与净得分差决定。Qiu 统一排序在高质量价 3.91 换位；基准 Gumbel 匹配下个性化首位比例在 3.92 和 3.82 分别约为 49.75% 和 52.25%。两项复算均不外推为一般福利定理。具体式子与主文印刷差异见模型卡。

## 检索审计与下批

`brief --intent lineage` 使用 `ranking mediated price elasticity`、`position ranking auctions net surplus`、`personalized ranking seller pricing`，另用语义问句 `When do lower seller prices improve ranking and induce more consumer search, and how does this compare with allocating premium slots by surplus-ordered auctions?`。以 `corpus_rag.ranked_candidates` 为口径，无种子和加 24867、27945 种子的运行均返回 Chu 第 1、Qiu 第 2，并进入自动时间线；这不是全库召回率。Du–Ning（28784）和 Zou–Zhou（36240）是邻近候选，本轮不把共同出现的“个性化”自动记为研究继承。

已回查审核路径 `weitzman-1979-pandora` → `qiu-et-al-2025-personalized-pricing`，中段包含 `chu-nazerzadeh-zhang-2020-position-auctions`；前边为组件继承，后边为机制对照。Qiu PDF 16 和 Chu PDF 13 可从 `evidence` 定位，再回原页看图表、公式。两篇补件未在本地目录定位：Qiu 的线上附录／数据和 Chu 的 e-companion 分开记录，不能写作已读。

第二十一批先对齐 Qiu 明引的 Calvano 等（2020）原文：核需求、状态、探索、稳定判据和强制偏离，把学习算法沿用与收益函数变化分开。再找一篇能检验 Qiu 换位机制的独立理论：优先比对个性化所改变的是商品集合、价格还是顺序。独立补件继续留队列，不阻塞正文工作。

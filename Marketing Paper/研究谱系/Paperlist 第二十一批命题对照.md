---
tags: [research/theory, research/lineage]
batch: paperlist-21
---

# Paperlist 第二十一批命题对照

这一支谱系分开两个问题：**当期需求能否化成同一个模型**，以及**训练后的反应能否辨识维持高利润的机制**。前者可以在限定条件下给出精确等价；后者不能只凭一次偏离失败作判断。

| 论文 | 行动、状态与反应 | 利润或福利证据的口径 |
| --- | --- | --- |
| [[Marketing Paper/文献卡/Calvano 等 2020 - 重复定价与 Q-learning|Calvano 等（2020）]] | 无限期同时报价、全选择 logit；观察最近各家的价格。稳定后冻结对手策略检验最优响应；另试一期降价。 | 代表模拟 50.5% 路径上 Nash；$\Delta=0.849$ 是利润由单期 Nash 到联合利润最大化的间距比例，不是价格涨幅。PDF 7–13、16、18。 |
| [[Marketing Paper/文献卡/Abada 与 Lambin 2023 - 储能学习与表观合谋|Abada–Lambin（2023）]] | 充放电改变未来可行性；看市场价格，不直接看竞对行动。24 小时内强制单边双向偏离，另比较训练时强化探索。 | 基准对比为全日开放环路 Cournot；两个方向的偏离都可能亏损，强化探索改善模拟福利。不能只用原策略轨迹恢复来识别定向惩罚。PDF 4–8、11–13、17–19。 |
| [[Marketing Paper/文献卡/Qiu 等 2025 - 个性化排序与算法定价|Qiu 等（2025）]] | 保留重复报价和有限记忆，但报价先经平台排序再进入顺序搜索需求。全选择是完美个性化且首件免费时的特殊需求，不是统一排序的需求。 | 对比两套排序的当期 Nash 和训练模拟结果；同价偏离说明换位动机，不等价于 Calvano 的冻结对手后求全备选最优响应。PDF 4–9、10–16。 |

## 条件等价：只涵盖当期需求

令 $v_j=a_j-\phi p_j$、$v_0=a_0$。若 $\epsilon_k$（包括外部选项）相互独立且都为标准 Gumbel，且完美排序与免费首件让买家实现所有商品和外部选项中的最大效用，则 Qiu Eq. (13) 给出

$$D_j=\Pr(v_j+\mu\epsilon_j=\max_{k\ge0}(v_k+\mu\epsilon_k))=\frac{e^{v_j/\mu}}{\sum_{k\ge0}e^{v_k/\mu}}.$$

右式是独立 Gumbel 最大值选择概率；令 $\phi=1$ 正是 Calvano Eq. (5) 的函数形式。Qiu PDF 4 明写外部选项 $a_0+\mu\epsilon_{i0}$，PDF 8 又有外部选项归零的文字；用 PDF 15 表 2 回查：以 $a_0=0$ 且保留随机项，低／高质量份额在降价前为 0.393023／0.389113，降价后为 0.377572／0.413130，均与表三位小数相符。此核算支持随机外部选项的读法，不是代码复现，不能把外部效用常数设为零后仍直接套用分母。

**限定范围：** 统一排序时昂贵的第二次查验改变可选集合，不能套同一个全选择式；噪声排名亦不能无条件套用。两个模拟在参数、价网格与训练细节上不同；方程同形不等于学习轨迹、静态数字或福利结论等价。

## 已核关系与候选

- **Calvano → Qiu（组件延伸）**：Qiu §3.3 明引重复定价 Q-learning；分开作者的沿用说明与上面的独立条件等价。主要新增是排序及搜索决定的奖励函数。
- **Calvano → Abada–Lambin（组件延伸）**：§5.1 明引 AER 2020a 的训练后强制偏离方法，并将测试扩至动态库存、双向动作与不完全监控。该文参考文献的 2020b 是 *Science*，不能把每处 2020b 也挂到 AER。
- **Abada–Lambin → Qiu（证据边界对照）**：Qiu 的文献节引用此文，但两篇主实验并不等同。Qiu 识别模拟中的公共排名换位收益，不测试 Abada–Lambin 的双向动作与离路径访问频率。阿巴达等的解释提醒我们不能从短期响应直接断言策略性质，不证明 Qiu 的训练结果全由探索不足造成。Qiu 文献节关于“过度算法复杂性”的一句概述不替代原文对欠探索的数值证据。

检索审计：`brief --intent lineage`，词组 `algorithmic pricing collusion`、`reinforcement learning forced deviation`、`q learning pricing memory discrete prices`，语义问句 `How does repeated Bertrand algorithmic pricing with logit demand change with platform product ranking versus consumer search?`，加入 24867、1959 种子。本轮 `corpus_rag.ranked_candidates` 前三为 Qiu、Abada–Lambin、Calvano，三者都在自动时间线。Klein（42925）和加油站实证（16273）另列候选，不算本批经核新增；Du–Ning（28784）仍留在个性化工具分支。

下一批第一步：查 Klein 的同时与轮流调价是否只变了监控、承诺时序或可学的响应映射。另用报价时序做反向期刊检索，把论文中的价格周期与 Calvano 的离散格点周期比较。只在原文区分机制后连边；Abada 和 Calvano 的外置复件继续留缺口。

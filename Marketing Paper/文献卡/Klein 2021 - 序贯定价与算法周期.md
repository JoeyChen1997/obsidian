---
tags: [research/theory, research/algorithmic-pricing]
reading_status: core_read
source_id: 42925
---

# Klein（2021）：序贯定价与算法周期

Timo Klein, *Autonomous Algorithmic Collusion: Q-learning under Sequential Pricing*, RAND Journal of Economics 52(3), 538–558（在线 2021-08-09）。DOI `10.1111/1756-2171.12383`。本地是先行本 `RAND/Klein_2021_Autonomous algorithmic collusion Qlearning under sequential pricing.pdf`，PDF 1–21；本卡不把先行本页码替成正式刊页。

## 模型与时序

- PDF 6，Eqs. (1)–(4)：同质品、线性需求 $D_i=1-p_i$（低价者独占、同价平分），价格格点 $P=\{0,1/k,\ldots,1\}$；两家无限期轮流改价，奇数期 1 家、偶数期 2 家，自己价格在对方下一次行动前保持不变。利润 $p_iD_i$，折现 $\delta$；Markov 状态只含对方上一期价格。静态联合利润最大化价为 $p^C=.5$、每家 .125。
- PDF 7–8，Eqs. (5)–(6)：序贯 Q-learning 的状态—动作值包含当前利润、对方下一期改价而自己维持报价时的利润（折现 $\delta$）及轮回自己行动的最优值（折现 $\delta^2$）；按 $\varepsilon_t$-greedy 选择。探索时随机报价，训练后比较的是纯贪心策略，无法表达沿路径混合。
- PDF 9：盈利按最后约 1,000 期平均；竞争基准不是静态 Nash，而是作者用触底即跳价构造的 **近似** Edgeworth 基准：逐格降价，触底后一方重置到高于垄断价一格，再由对手降价。$\Gamma_i$ 的分子为所学 Q 表中最终状态／报价的估计值，分母为冻结对手后计算的最优值；两家都在容差内才列为 Nash。分母可准确求，分子是否准确仍取决于学习，不是逐状态 MPE 证明。

## 经典动态理论对照

[[Marketing Paper/文献卡/Maskin 与 Tirole 1988 - 动态寡头与 Edgeworth 周期|Maskin–Tirole（1988）]] 的正式正文 PDF 4–8 与 Klein PDF 6–7 用同一轮流改价状态。经典 Table II 的七价例低价处混合重启；作者也在更细网格下给出纯策略焦点例，故不把 Klein PDF 8 对混合局限的讨论读成所有焦点 MPE 都必须混合。

## Klein 的数值结果与边界

| 原页 | 结果 | 证据边界 |
| --- | --- | --- |
| Klein PDF 10–12，Figures 1–3 | 基准 $k=6,\alpha=.3,\delta=.95$，1,000 次运行平均利润高于竞争基准、最优性指标约 0.97。$T=500{,}000$ 时 667 次达作者定义的合谋均衡，241 次达联合利润最大化；图 3 只对这 241 次强制偏离后求平均。 | 各次价格跳回时间不同，平均图平滑不等于单次渐进恢复；不外推到全部 1,000 次。 |
| Klein PDF 12–15，Figures 4–7 | $k$ 从 6 增到 24 后平均利润仍高于竞争基准，但最优性和 Nash 比例下降；$k=24$ 出现确定性非对称周期：双方轮流压价，同一家在每轮承担跳价重启。 | 不是经典 Table II 的随机混合均衡；该模拟在有限训练期上不能单独分离“更多可选价”和“更多状态动作要学习”。 |
| Klein PDF 15–18，Figures 9–10 | 折现率极高会降低学习质量；将自身上一期价格也放入状态略增平均利润，但更难学习、降低最优性指标和 Nash 比例。 | 多一项记忆并不是无条件改善；与 Calvano 的差异不只是记忆，行动时序和需求也不同。 |

独立复核：将 Maskin–Tirole 的 $V_i/W_i$ 交替递推消去 $W_i$，可得到 Klein Eq. (4) 中当前利润、反应期利润及 $\delta^2V_i$ 三项；Eq. (5) 用实际对手反应替代对反应分布求期望。另以 k=6 的 7 个行动和状态核算：每家 Q 表 49 项，扩为双价状态后变成 343 项；k=24 时对应 625 和 15,625 项。正式卷期书目信息由 Crossref 核对；正文证据仍以本地先行 PDF 为准。

补件：本轮核读 §§2–6，未复跑原训练或核发布的复现代码；同名独立补件未在本地目录定位。见 [[Marketing Paper/研究谱系/Paperlist 第二十二批命题对照]]。

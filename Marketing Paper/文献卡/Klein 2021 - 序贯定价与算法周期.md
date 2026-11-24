---
tags: [research/theory, research/algorithmic-pricing]
reading_status: core_read
source_id: 42925
---

# Klein（2021）：序贯定价与算法周期

Timo Klein, *Autonomous Algorithmic Collusion: Q-learning under Sequential Pricing*, RAND Journal of Economics 52(3), 538–558（在线 2021-08-09）。DOI `10.1111/1756-2171.12383`。本地是先行本 `RAND/Klein_2021_Autonomous algorithmic collusion Qlearning under sequential pricing.pdf`，PDF 1–21；本卡不把先行本页码替成正式刊页。

## 模型与时序

- PDF 6，Eqs. (1)–(4)：同质品、线性需求 $D_i=1-p_i$（低价者独占、同价平分），价格格点 $P=\{0,1/k,\ldots,1\}$；两家无限期轮流改价，奇数期 1 家、偶数期 2 家，自己价格在对方下一次行动前保持不变。利润 $p_iD_i$，折现 $\delta$；Markov 状态只含对方上一期价格。静态联合利润最大化价为 $p^C=.5$、每家 .125。
- PDF 7–8，Eqs. (5)–(6)：序贯 Q-learning 的状态—动作值包含当前利润、对方尚未改价的一期利润和两期后的最优值；按 $\varepsilon_t$-greedy 选择，随机报价的概率随时间衰减。算法只走纯策略。
- PDF 9：盈利按最后 1,000 期平均；最有利的“竞争”基准不是静态 Nash，而是 Maskin–Tirole 最低价格 Edgeworth 周期：连续降一格，触底后一方重置到略高于垄断价。最优性 $\Gamma_i$ 是保持对手策略后，所学 Q 值与真正最优 Q 值之比；两家都为 1 才称 Nash，且利润高于竞争基准才称 collusive equilibrium。

## 经典动态理论对照

Maskin–Tirole（1988）先行本 PDF 3–4、7–8、11–12、15–19 建立同一轮流改价框架：有限价格格点、Markov 策略依赖对手当前价、$\delta$ 近 1 时既有固定焦点 MPE 也有 Edgeworth 周期 MPE；周期在价格触底处使用混合重置。Proposition 7（PDF 18，刊页 587）给出细格点和高折现下周期存在；Proposition 8（PDF 19，刊页 588）给出对称周期下每家平均利润至少接近垄断利润的四分之一。Proposition 9（PDF 22，刊页 591）说明，在一种内生承诺时序中，对称轮流行动 MPE 可由同时行动切换而来。1989 PDF 只是该论文的 erratum（物理 PDF 2，刊页 1501），补回 Section 10 漏行，不是新模型。

## Klein 的数值结果与边界

| 原页 | 结果 | 证据边界 |
| --- | --- | --- |
| Klein PDF 10–12，Figures 1–3 | 基准 $k=6,\alpha=.3,\delta=.95$，1,000 次运行平均利润高于竞争基准、约 97% 最优性，约 67% 运行是 Nash；强制一期偏离后价格恢复，图 3 的暂时性响应看似惩罚。 | 是数值分布而非收敛定理；百分比随运行长度、判定容差和格点改变。 |
| Klein PDF 12–15，Figures 4–7 | $k$ 从 6 增到 24 后平均利润仍高于竞争基准，但最优性和 Nash 比例下降；$k=24$ 出现确定性非对称周期：一方逐格降价，另一方偶尔跳高重启。 | 这不是 Maskin–Tirole 的随机混合 MPE：纯策略 Q-learning 无法沿路径学习理论要求的混合；作者明确将其称为 deterministic Edgeworth price cycles。 |
| Klein PDF 15，Figure 9–10 | 折现率过高会降低学习质量；把自身上一期价格也放入状态不提高表现，反而增加状态空间、降低最优性。 | 不能把“增加记忆”解释成一定增强合谋；在这里它改变访问量和学习难度。 |

独立复核：$k=6$ 的竞争基准约 $0.0611$，随格点变细趋向 $0.0833$；Maskin–Tirole 的 Proposition 8 是一般 MPE 的利润下界，Klein 以该周期作可计算比较线。两者都存在周期，不表示相同均衡：前者允许混合且要求动态最优，后者是纯策略学习路径，并用事后 $\Gamma$ 检验其是否接近最优。正式版本与先行本的卷期元数据由 Crossref 核对；正文证据仍以本地先行 PDF 为准。

补件：Klein 的在线补充材料没有在本地目录定位；Maskin–Tirole 1989 本地仅为 erratum，已单独记作版本校正。历史卡恢复线索：三张被 Git 备份删除的卡在 `a4eab3a02250464db75db8ef17026a4be29e86ee` 可恢复，但本批不擅自复原工作区历史删除。

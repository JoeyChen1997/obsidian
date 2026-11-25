---
tags: [research/econometrics, research/causal-inference, research/bootstrap, research/matching]
reading_status: core_read
source_id: 5793
---

# Abadie 与 Imbens（2008）：近邻匹配的 Bootstrap 失效

Alberto Abadie and Guido W. Imbens, *On the Failure of the Bootstrap for Matching Estimators*, Econometrica 76(6), 1537–1557. [DOI](https://doi.org/10.3982/ecta6474)。PDF 1–21 = 刊页 1537–1557。

## 对象、反例与复算（PDF 2–10）

- ATT，处理和对照分样本；每个处理单位找 1 个对照近邻，允许同一对照被重复使用。通常的 bootstrap 在两组内各抽原样本量（有放回），并**重做匹配**。两种方差分别围绕原估计与 bootstrap 条件均值。反例取标量均匀协变量、常数倾向、$N_1/N_0=\alpha>0$，处理结果恒为 $\tau$、对照结果正态均值零方差一。可忽略性、overlap、无匹配偏差和根号样本量正态性都不排除 bootstrap 失败。
- $K_i$ 为某对照被用次数。给定 $(X,W)$，条件方差 $\sum_iK_i^2/N_1^2$；若给定对照的区间覆盖概率 $P_i$，$K_i$ 为二项分布。用均匀次序统计量间距的二阶矩推得 $N_1\operatorname{Var}(\hat\tau)\to1+1.5\alpha$。普通 bootstrap 中一个原对照不出现的概率 $(1-1/N_0)^{N_0}\to e^{-1}$，因此留下的不同对照比例不趋于 1；两组重采样会改变匹配区间和重复次数。不是简单把观测舍弃固定比例就能得出新方差，还要计原匹配和重抽匹配的交叉项。
- 按 Lemma 3.2，围绕原估计的 bootstrap 归一化无条件期望趋于 $1+1.5\alpha c+2q$，其中 $q=e^{-1}$、$c=(5q-2q^2)/(3(1-q))\approx.82723$。复算两者相等的比例 $2q/[1.5(1-c)]\approx2.8391$；$\alpha=1$ 时真方差极限 2.50、bootstrap 均值 2.9766；$\alpha=5$ 时 8.50 对 7.9400。均值恰好相等不证明条件一致。大 $\alpha$ 时 bootstrap 的非负二阶矩均值下穿真值，用 Portmanteau 得到矛盾，同时较小的居中版本也不能一致；同类论证用于分布，不是从二阶矩这个无界泛函的失败直接推出弱收敛失败。

## 适用范围（PDF 10–21）

- 给定协变量和处理，权重固定，作者讨论用 wild bootstrap 估**条件**分布；它不是重做匹配的无条件 bootstrap，也不自动纳入效应异质性造成的样本构成风险。作者建议适用条件下的分析方差或替代抽样，未用该反例否定所有配对估计；有限离散协变量的完全分层与邻居数随样本增长是不同统计量，应单独检查。
- 印刷附录核次序统计量、覆盖几何、样本缺席和主式展开。Lemma A.6(ii) 的 $E[K_{b,i}K_i\mid W_i=0]$ 长证明转指工作稿，未独立核。可用作者列示矩自行复算 (7)，但不当作该交叉矩证明的复现。

**核读范围**：PDF 1–11 主文、11–20 印刷附录、20–21 引文，回查 PDF 8、10 原页。2006a 是作者明确所用的分析方差基准；本轮只记可回查的候选，不新增经核边。未取 2006b 长详证或外做模拟。

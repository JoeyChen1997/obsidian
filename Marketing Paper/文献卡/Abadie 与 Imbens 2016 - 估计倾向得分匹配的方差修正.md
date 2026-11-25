---
tags: [research/methods, research/causal-inference, research/matching]
reading_status: core_read
source_id: 5794
---

# Abadie 与 Imbens（2016）：估计倾向得分匹配的方差修正

Alberto Abadie and Guido W. Imbens，*Matching on the Estimated Propensity Score*，Econometrica 84(2), 781–807。[DOI](https://doi.org/10.3982/ECTA11293)。物理 PDF 页 = 刊页 − 780。

## 估计对象与假设（PDF 3–10，Assumptions 1–5，Prop. 1）

- 二元处理、i.i.d.，给定 $X$ 的潜在结果可忽略性，$p(X)=P(W=1\mid X)$ 严格远离 0、1。论文并不要求得分的**密度**也远离 0：得分连续且有区间支撑、结果条件均值 Lipschitz、方差连续、有 $2+\delta$ 阶矩。没有可忽略性时，估计量至多有协变量调整后的描述性比较解释。
- 用同一样本估计正确设定的参数化倾向得分（基准 MLE），再按一维得分做固定 $M$、有放回、异处理组最近邻匹配。ATE 两组都补反事实，ATET 只给处理组补对照（虽然后者归一化为 $N_1$，所报 CLT 仍按 $\sqrt N$）。不涵盖增长 $M$、核平滑、一般机器学习评分或忽视平衡的错设模型。纯离散协变量章节建议对完全相同得分使用全组匹配，此时是分层估计，不是相同的连续固定-$M$ 极限。
- 真得分匹配的方差（Prop. 1）含得分处条件均值差的异质性、组内结果方差，以及因有限匹配数出现的 $1/M$ 项；具体公式不可以有效影响函数的方差直接代替。第一阶段信息矩阵记 $I$，得分方向用 $f=F'$；$c$ 是真得分 ATE 统计量与参数得分的极限协方差，取决于得分保持不变时 $X$ 与条件结果均值的协变。

## 修正、证明与独立复核（PDF 11–19、20–26，Thms. 1–2）

- ATE 方差 $V_{\mathrm{adj}}=V-c'I^{-1}c$，所以把估计得分当真得分的区间在这一规范下一般偏保守。直觉是剔除与第一阶段得分相关的投影，不是把匹配映射光滑化；证明沿 $\theta_N=\theta^*+h/\sqrt N$ 做局部实验，以 martingale CLT 联合处理匹配波动与得分，再用 Le Cam 第三引理及边长 $d/\sqrt N$ 的网格。定理正式陈述对离散化 $\bar\theta_N$，先 $N\to\infty$ 后 $d\downarrow0$；不能直接对一个概率为零的连续事件套弱收敛，也不把它当作普通配对 bootstrap 的有效性结果。
- ATET 方差 $V_{t,\mathrm{adj}}=V_t-c_t'I^{-1}c_t+g'I^{-1}g$。复推：令 $\Delta(X)=\mu(1,X)-\mu(0,X)$，$\tau_t(\theta)=E[F(X'\theta)\Delta(X)]/E[F(X'\theta)]$，因此 $g=E[X f(X'\theta^*)(\Delta(X)-\tau_t)]/E[p(X)]$。正项来自处理者构成随参数变化；常数 ATE 不存在此项，不能把 ATE 的修正符号移植到 ATET。
- **原文举例的边界疑点**（PDF 13–14、19）：若得分对 $X$ 一一对应，Theorem 2 的得分内协方差项归零，但 $c_t$ 的首项一般等于 $g$、并非零，故公式里的正负项相消。不能照抄 PDF 14 的「不降维所以 $c_t=0$」来构造正修正。**独立正例**：$X=(1,Z,U)$，$Z,U$ 独立、连续且紧支撑，$E[U]=0$，$p=F(Z)$（logit）；取 $\mu(1,X)=pU,\mu(0,X)=-(1-p)U$，两组加有界独立均值零扰动。$\Delta=U$，得分内均值差为零，且 $c_t$ 两协方差正好抵消；$g$ 的 $U$ 分量为 $E[f]\operatorname{Var}(U)/E[p]>0$，所以确为正。负例可令两组共享均值 $U$ 并加常数处理效应：$g=0$，$c_t$ 的 $U$ 分量非零。
- 方差实现需要单独估真得分方差、信息矩阵和局部协方差；固定小邻域的局部方差不逐点一致，文中使用其聚合量。ATET 的 $c_{t,1}$ 用得分邻居预测并在同臂排除自身；$g$ 的插件回到原 $X$ 空间计算条件结果差，不能把两个对象都按得分匹配。第 4 节是方差实现描述，不是授权对原样本拟合结果直接套系数修正。

**核读范围**：PDF 1–27 主文、印刷附录与参考文献；原图回查 12–14；独立复推商数导数和符号例。线上补件的 Prop. 1、Lemma 1、Assumption 5 原始条件和 Theorem 2 详证未核。候选（未入经核图）：[[Marketing Paper/文献卡/Abadie 与 Imbens 2006 - 固定近邻匹配的偏差与方差|2006]] 的真匹配变量推断基准、[[Marketing Paper/文献卡/Abadie 与 Imbens 2008 - 近邻匹配的 Bootstrap 失效|2008]] 的重抽样失效、2012 的 martingale 表示与 2016 的同样本第一阶段修正，分别标注为不同对象，不以共同作者代替核证。

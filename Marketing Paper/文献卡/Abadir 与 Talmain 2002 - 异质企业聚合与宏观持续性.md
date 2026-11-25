---
tags: [research/theory, research/heterogeneity, research/dynamic-models, research/time-series]
reading_status: core_read
source_id: 43606
---

# Abadir 与 Talmain（2002）：异质企业聚合与宏观持续性

Karim Abadir and Gabriel Talmain, *Aggregation, Persistence and Volatility in a Macro Model*, Review of Economic Studies 69(4), 749–779. [DOI](https://doi.org/10.1111/1467-937x.00225)。PDF 1–31 = 刊页 749–779。

## 一般均衡如何改变聚合（PDF 3–10，Eqs. 2–19）

- $N$ 种差异化中间品各由厂商以 $q_n=\theta_n k_n^\gamma\ell_n^{1-\gamma}$ 生产，厂商在竞争要素市场租资本劳动，逐期定价；竞争性最终品生产采用带归一化的 CES。代表家庭对数效用、固定劳动、持有资本与股票。共同的需求弹性绝对值 $1/(1-\rho)$ 给出价格/成本 $1/\rho$，净加成 $(1-\rho)/\rho=1/\nu$，$\nu=\rho/(1-\rho)$。同一参数同时改变替代性／互补性与市场势力，不能分别归因。
- 所有厂商用相同资本劳动比；相对价格 $p/\widetilde p_n=\theta_n/\theta$，投入份额 $\ell_n=k_n/k=\theta_n^\nu/\sum_j\theta_j^\nu$。正向企业冲击降低其相对成本并内生提高份额；这不是固定份额地平均每一家增长路径。市场清算给出 $y_t=\theta_t k_t^\gamma$，$\theta_t=(N^{-1}\sum_n\theta_{n,t}^\nu)^{1/\nu}$。相同加成不使静态要素**相对分配**偏离最大产量的配置，但不代表动态储蓄或收入分配无扭曲。
- **独立复算（Eqs. 15–18）**：完全折旧、横截性条件和对数偏好下，$s^*=\delta\gamma\rho$，$k_t=s^*y_{t-1}$，故 $\log y_t=\nu^{-1}\log X_t+\gamma\log y_{t-1}+\gamma\log s^*$，$X_t=N^{-1}\sum_n\theta_{n,t}^\nu$。把 $\log\theta_{n,t}$ 先线性平均，一般不等于 $\log X_t/\nu$；仅在极限 $\nu\to0$（或无横截面差异）可得到几何聚合。

## 随机过程、定理及原页复算（PDF 10–18、23–30）

- 微观为 $\log\theta_{n,t}=\mu+\alpha_n\log\theta_{n,t-1}+u_{n,t}+\beta_n e_t$。各企业 $0<\alpha_n<1$，但横截面 beta 分布允许任意接近 1（$h_\alpha\in(0,1]$）；$u$ 独立于标准正态共同冲击 $e$，$\omega_n,\beta_n$ 服从指定广义 gamma 族，形状 $\lambda>2$。因此“每家稳定”并不等于统一远离单位根；“由聚合产生”也不等于无共同冲击。大 $N$ 推导保留不同企业之间由 $e_t$ 产生的交叉协方差（Appendix Eq. A.2）；这些项约为 $N(N-1)$，不能套独立截面平均的消噪逻辑。
- **Theorem 1**：$X_t$ 的领先项相关同时依赖 $t,\tau$，不是平稳 ARFIMA 的相关函数。PDF 14 原式可写为 $[e^{b\sqrt{t^3(t+\tau)}}-1]/\sqrt{[e^{bt^2}-1][e^{b(t+\tau)^2}-1]}$，$b=\nu^4/[2(4h_\beta^2)^{2/\lambda}]$。固定 $t,\tau$ 对此表达式作 $b\to0$ 展开，得 $\sqrt{t/(t+\tau)}$（Remark 6）；是近似相关形状与随机游走相同，不是证明微观出现单位根。共同冲击载荷参数 $h_\beta$ 进入领先项相关；纯个体冲击散布 $h_\omega$ 在该领先项中消去，却仍进入协方差。
- **Cor. 1–2**：在论文的渐近近似和较小噪声扩展中，$\log X_t$ 与 $\log y_t$ 的相关领先项一致；资本存量的稳定滤波不主导长期相关。折旧扩展用乘积型资本积累且储蓄有严格正下界，不是对任意折旧规则的推广。附录用正态指数矩拆成同厂与跨厂项，再用广义 gamma 的积分展开及接近 1 的根的 Laplace／Watson 近似；未独立验证所有高阶余项。

## 示例数据和不可越过的边界（PDF 18–22）

- 约化拟合 $(1+b_1|\tau|^{b_2})^{-b_3}$，英/美人均 GDP 的样本 ACF 拟合 $R^2=.82,.83$，作者比较的 AR(2) 为 $.56,.50$。这是对同一批样本 ACF 的描述性拟合，不识别微观参数、不是样本外预测比较。**独立复算**：对正滞后，$b_2>1$ 时拐点满足 $\tau^{b_2}=(b_2-1)/[b_1(1+b_2b_3)]$，才有先缓后陡的下降；不能说任何正参数都给 S 形。该曲线是作者的简化拟合，不与有限 $t$ 的 Theorem 1 式混用。
- 模型机制是“企业异质性 × 内生份额 × 非线性水平聚合”，适合后续比较异质产品采用、品类需求和宏观截面聚合。所谓较长记忆、波动放大与垄断力/互补性比较都在指定分布、时间尺度和比较基准下成立；不把它升级为任意 CES 或任意市场势力变动的结论。

**核读范围**：PDF 1–22 正文、23–30 印刷数学附录的核心推导，回查 PDF 14 原式；复算稳态节约、随机游走相关极限与约化拐点。未重估历史 GDP 或微观分布，不新增经核边。

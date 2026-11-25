---
tags: [research/theory, research/technology-adoption, research/dynamic-choice, research/regulation]
reading_status: core_read
source_id: 5567
---

# Acemoglu 与 Lensman（2024）：变革技术的逐步采用与监管

Daron Acemoglu and Todd Lensman，*Regulating Transformative Technologies*，AER: Insights 6(3), 359–376。[DOI](https://doi.org/10.1257/aeri.20230353)。物理 PDF 1–18 对应刊页 359–376。

## 原语与采用阈值（PDF 3–8，Eqs. 1–8）

- 连续时间、连续部门 $i\in[0,1]$、风险中性代表家庭，贴现 $\rho>g_N>g_O\ge0$。旧技术流产出 $Q_O$，新技术 $\alpha_iQ_N$；若灾损实现，使用新技术另有社会流损失 $\delta_iQ_N$。只有灾时已经使用新技术的部门可能以概率 $\eta_i$ 被永久锁定；并非一采用便永久锁定，也不是每期独立重复灾损事件。
- 以先验 $m=\mu(0)$ 存在未来灾损；若会发生，条件到达时间服从强度 $\lambda$ 的指数分布。**复推**：无事发生条件下 $\mu(t)=me^{-\lambda t}/(1-m+me^{-\lambda t})$，到达强度为 $\lambda\mu(t)$。学习是被动、与采用独立；推迟是等待信息，不是主动试点提升学习率。产出与损失均随技术潜在质量增长，不由总采用反推 $g_N$。
- 规划者比较当前流量增益 $\alpha_iQ_N-Q_O$ 与 $\mu\lambda\eta_i$ 乘以灾后被锁与能回退的价值差。在 $\delta_i\ge\alpha_i$ 时，未锁定者灾后总回旧技术，两状态增量损失为 $Q_O/(\rho-g_O)-(\alpha_i-\delta_i)Q_N/(\rho-g_N)$。令 $q=\log(Q_N/Q_O)$，若 $\alpha,\eta$ 常数，则采用当且仅当 $\delta_i<L=\alpha+(\rho-g_N)[(\alpha-e^{-q})/(\mu\lambda\eta)-e^{-q}/(\rho-g_O)]$。采用率 $F_\delta(L)$ 截为 0–1，阈值的曲率不等同于截断曲线全程凸；若损害分布不均匀，另有密度斜率项。

## 速度、排序与政策（PDF 7–16，Props. 1–9）

- 固定 $(\mu,q)$ 的大损失区间内，$g_N$ 上升会降低阈值；沿时间路径比较则还加上 $q(t)=q(0)+(g_N-g_O)t$ 的正项，可能早期促进、较晚抑制。复算 Figure 1 参数：$g_N=2.6\%$ 时首次进入约 18.11 年、全覆盖约 43.13 年；$3.8\%$ 时约 8.86、58.93 年。图中高增长可以**更早开始但更晚完成**，不是所有时点或每个部门都推迟。固定有限时点、连续损害且 $\delta_i\ge\alpha$ 时 $g_N\uparrow\rho$ 推出采用份额趋 0；不能与先取 $t\to\infty$ 混用。小损害边界 $L<\alpha$ 时 Prop. 4 报告沿路径对 $g_N$ 的效应反转；灾后等到质量差够大可以再采用，非永久净损失。
- 私人仅负担 $\gamma_i\le\delta_i$，且 §III 假定 $\gamma_i\ge\alpha_i$；企业用相同阈值比较 $\gamma_i$，私人损失不足会导致过早采用，也可能颠倒部门顺序。若 $\gamma_i=\kappa(\delta_i)$ 严格递增，则社会损害口径的市场阈值 $\widetilde L=\kappa^{-1}(L)$。**复核 Prop. 6(iii) PDF 13**：链式法则给 $\ddot{\widetilde L}/\dot{\widetilde L}=\ddot L/\dot L-(\kappa''/\kappa')(\widetilde L)\dot{\widetilde L}$；原页末因子印成 $\dot L$。局部凹的 $\kappa$ 提升此归一化曲率的方向仍成立，不能照印刷式做数值比较。Figure 2 的 $\kappa(\delta)=\sqrt{\delta}$ 下全覆盖点约 30.53/40.36 年，分别早于相应规划阈值。
- 灾前部门使用税 $\tau_i=\mu\lambda\eta_i(\delta_i-\gamma_i)Q_N/(\rho-g_N)$ 补齐预期流量边际外部性；对正税 $d\log\tau_i/dt=g_N-\lambda(1-\mu)$，二阶导 $\lambda\dot\mu<0$。税趋零需 $\lambda>g_N$，相等时有正极限（若外部性为正），不能只因灾损概率降低便推税降为零。统一税能改边际进入点，不能改变以 $\gamma_i$ 排序；同质 $\alpha,\eta$ 且两种损害同序时可取边际统一税，排序错位时不能普遍实施最优。作者的 sandbox 是按社会风险给高损害部门设等待期，而非让低风险试点内生获得数据；Prop. 9 的严格福利改进须结合其适用条件和实际存在的过采纳空间，详证在外置附录。

**核读范围**：PDF 1–17 主文和核心推导，17–18 参考文献；回查 9、13 原图并用原参数求根，未复跑复制代码或取得线上附录 A–D。候选（未入经核图）：将「试验本身生成信息」与本模型「无消息的公共更新」作为不同原语；跨部门损害排序与市场排序不能仅比较总扩散曲线。此卡为经济模型阅读，不把参数化例子当真实政策预测。

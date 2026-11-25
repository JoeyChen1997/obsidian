---
tags: [research/empirical, research/discrete-choice, research/instrumental-variables, research/health-insurance]
reading_status: core_read
source_id: 36382
---

# Abaluck 等（2021）：医保计划死亡率与退出后的替代选择

Jason Abaluck, Mauricio Caceres Bravo, Peter Hull, and Amanda Starc, *Mortality Effects and Choice Across Private Health Insurance Plans*, Quarterly Journal of Economics 136(3), 1557–1610. [DOI](https://doi.org/10.1093/qje/qjab017)。本地是 advance-article 未编辑稿加在线附录，因此以下仅报物理 PDF 页码，不套正式刊页。正文 PDF 1–41、参考文献 42–46、附录 47–77。

## 估计对象与识别（PDF 7–24）

- **对象**：有多个计划的美国 65 岁及以上 Medicare 市场，按县×年构造选择集，同一保险计划在不同县视为不一样的备选项；主 IV 以 2008–2011 年、上一年末在 MA 的受益人为样本。风险调整并以经验 Bayes 缩减估计噪声得到计划的观测死亡指标 $\mu_j^*$；模型的 $\mu_j$ 是潜在观测均值，仍可能包含未观测健康排序。主效果 $\beta_j$ 是投保某计划的一年死亡效应，相对于共同基准。
- **作者的 estimand 不是逐计划质量**：中心化后 $\beta_j=\lambda\mu_j+\eta_j$、$\operatorname{Cov}(\eta_j,\mu_j)=0$，$\lambda$ 是当前市场排序下的跨计划预测斜率。即使 $\lambda=1$，$\eta_j$ 也可普遍非零。由于 $\operatorname{Var}(\beta_j)=\lambda^2\operatorname{Var}(\mu_j)+\operatorname{Var}(\eta_j)$，只用第一项是下界，不是把每个观测死亡率都认作因果。
- **工具变量（Eq. 6）**：$Z_{it}=\mu_{i,t-1}T_{i,t-1}$，即过去计划观测死亡率乘退出指标（实际以观测死亡率后验实现），控制两项主效应、县×年、县和年份特定退出效应及滞后计划特征交互。非退出组多续保；退出组被迫重选、所选计划死亡率向常态回归，产生负第一阶段。排除限制分别要求 $\operatorname{Cov}(\widetilde Z,\epsilon_{it})=0$（受益人未观测健康平衡）和 $\operatorname{Cov}(\widetilde Z,\eta_{it})=0$（fallback，重选计划的未预测质量残差不随工具系统变化）。健康平衡允许退出有直接扰动，只要扰动不沿被退出计划的观测死亡率系统变化。
- **复算识别失效（PDF 16–21）**：三计划等份额，死亡代理为 5%、5%、3%，真效应为 3%、7%、3%，则真实预测斜率是 1。第三个计划退出后，若都去第一个，IV 比率为 $0/2=0$；若都去第二个则 $4/2=2$。随机退出不随机分配备选计划。充分条件的离散选择构造允许计划固定不可观测质量，但持续、异质的偏好需由控制覆盖；退出本身若改变偏好，或人按未观测比较优势择保，则需额外限制（Appendix C.4–C.6，PDF 67–72）。

## 证据与可迁移边界

| PDF 页 | 核读结果 |
| --- | --- |
| 8、10、26–29，Tables I–III | MA 样本一年期死亡率均值约 4.7%，同县计划调整后观测死亡率的估计横截面 SD 1.1 个百分点。主 IV $N=11{,}441{,}205$ **人年**，非退出组只有 11.6% 换计划。含人口特征线性规格的第一阶段 −.724，简约式 −.745，原表 1.029（SE .098），复算 $.745/.724=1.0290$；其他规格 1.056、1.130、1.073。取表值的 SD 下界约 1.13 个百分点，非每份计划的效果。 |
| 26–31，Tables II–III、A.VI | 人口预测死亡率的安慰剂较小；备选残差代理在线性规格为 .010（SE .001），精确非零但量级较小，二分工具约零，不能称“所有平衡检验通过”。PFFS 政策退出限制较接近外生、但精度降低；剔除转去传统 Medicare 的人是对处理后选择的敏感性检查。 |
| 32–36，Table IV | 一星的预测效应 −.0011（.0012），未显示精确联系；每月保费每 $100 的单特征 IV 斜率 −.0058（.0019），相对观测 OLS +.0043 翻转。估计的是有不同特征的计划在**因果死亡效应**上的预测关联，不是对同一计划提高保费或改变网络的因果实验。药品缺口覆盖的系数在联合规格衰减；财务特征联合规格的预测 $R^2$ 上界仅 .0302。 |
| 37–39，Table V | logit 份额反演得到 $\xi_j=\log(s_j/s_0)-\alpha p_j$，以其重新构造退出 IV 得到 $\kappa=\operatorname{Cov}(\beta,\xi)/\operatorname{Var}(\xi)$。将 $\tau=\kappa\operatorname{Var}(\xi)/\operatorname{Var}(\beta)$ 与方差下界结合；当 $\kappa,\alpha<0$，$\tau$ 的下界除以 $100\alpha$ 给 WTP 上界。校准不同保费弹性得到约 $275–416／一年死亡风险少 1 个百分点；不是心理价值，也不是无需模型的点估计。 |
| 40–41、61、73–75，Appendix D | 从高到低死亡率四分位的重配，受影响者模拟少约 .6 个百分点，全样本无条件约 .25 个百分点；不含容量、保费、计划供给反应，公开指标还可能诱导健康筛选。 |

**阅读边界**：核本地正文与随件附录的核心结果、C.4–C.6 识别扩展和 D 模拟，回查 Table III 原图；未重跑 CMS 和复现包（[Dataverse](https://doi.org/10.7910/DVN/HTDG7I)）。与教师增值、医院/工厂关闭、产品退出后转移的识别相似性留作候选，未新增经核边。

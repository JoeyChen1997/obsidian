---
tags: [research/theory-paper]
paper_id: jerath-kim-swinney-2017
reading_status: core_read
doi: 10.1287/mksc.2017.1041
---

# Jerath、Kim 与 Swinney（2017）：库存风险与渠道质量

Kinshuk Jerath, Sang-Hyun Kim, Robert Swinney. *Product Quality in a Distribution Channel with Inventory Risk*. Marketing Science 36(5), 747–761. 本地来源：MKSC/Jerath_2017_Product Quality in a Distribution Channel with Inventory Risk.pdf；刊页为 PDF 页 + 746。核读 §§2–4、主文 Props. 1–3、印刷附录中零售定价及最优库存／质量的关键步骤。独立在线附录中的契约详证等未读。

## 模型

一个季节性产品；制造商先决定质量 $\theta$，分权下同时决定批发价 $w$，零售商随后订货 $q$。直营下制造商决定 $q$。三项决定都在潜在市场规模 $X$ 揭晓之前；看见 $X$ 后定零售价 $p$，不能补货，滞销品没有残值。消费者估值 $v\sim U[0,1]$，净效用 $v\theta-p$。批发价合同下厂商从订单而非零售实际销量获取利润；零售商承担库存风险（PDF 3–4）。对市场规模分布施加 IGFR 等条件；单位制造成本 $c(\theta)$ 严格凸，成本弹性 $\epsilon(\theta)=\theta c'(\theta)/c(\theta)>1$ 且不降（PDF 3）。

## 结果

- **零售响应**（Lemma 2，PDF 4、12–13）：若 $X\le 2q$ 则 $p=\theta/2$；若 $X>2q$ 则 $p=\theta(1-q/X)$。质量影响报价，每提高质量并非每生产一件都兑现销售收益。
- **最优条件**（Props. 1–2，PDF 5–6、13–14）：记 $y=2q$、$S(y)=S_1(y)+S_2(y)$，最优定价后期望零售收入 $\theta S(y)/4$。直营为 $\epsilon(\theta^c)\eta(y^c)=1$，其中 $\eta=yS'/S$；分权为 $\epsilon(\theta^d)\eta_2(y^d)=1$，其中 $\eta_2=yS_2'/S_2$。零售商库存一阶条件可反解为 $w=\theta S'(y)/2$；代回后厂家最大化 $-c(\theta)q+\theta qS'(y)/2$。两种渠道最优库存与质量都是策略替代。
- **质量反转**（Prop. 3，PDF 6–7；附录 PDF 14 指回主文）：分权可能提高、维持或降低最优质量。式 (12) 把两种力量分开：质量提高可增加订货，制造商获得 $(w-c(\theta))\,dq/d\theta$；但厂商不直接取得提高质量所增加的零售收入，少了 $S(2q)/4$。在零售最优内点，单独令 $w=c(\theta)$ 能消除库存方向的加价偏差，却仍不能协调质量。不要把质量较高写成渠道已协调。

## 独立算例

取 $X\sim U[0,1]$、$c(\theta)=2\theta^2$（按文中幂成本例的口径；分权参与约束不绑定）。式 (4) 给出 $S_1(y)=y-y^2/2$、$S_2(y)=y+y^2(\ln y-1)$，$S'=2S_2/y$。二分解 $\eta(y^c)=\eta_2(y^d)=1/2$，分别得 $y^c\simeq0.358684,\ y^d\simeq0.148999$。由两渠道一阶条件得 $q^c\simeq0.179342>q^d\simeq0.074500$，但 $\theta^c=S'(y^c)/4\simeq0.136776<\theta^d=S'(y^d)/8\simeq0.141833$。这是一个反转见证，不是对任意分布或合同的外推。

与 [[Marketing Paper/文献卡/Shi 等 2013 - 消费者异质性与渠道质量|Shi 等（2013）]] 的连接在 PDF 2、7：两篇都能得到分权升质，但此处允许**仅纵向均匀估值**；驱动力来自订货、需求揭晓与风险归属，不是 Shi 的非均匀估值或纵横联合异质。见 [[Marketing Paper/研究谱系/Paperlist 第二批命题对照]]。

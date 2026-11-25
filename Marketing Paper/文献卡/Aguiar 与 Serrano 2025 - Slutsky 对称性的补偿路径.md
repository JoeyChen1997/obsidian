---
tags: [research/theory, research/demand, research/revealed-preference]
reading_status: core_read
source_id: 23453
---

# Aguiar 与 Serrano（2025）：Slutsky 对称性的补偿路径

Victor H. Aguiar and Roberto Serrano, *A New Look at the Symmetry of the Slutsky Matrix*, Journal of Political Economy Microeconomics 3(2), 289–302. [DOI](https://doi.org/10.1086/732650)。正式出版为 2025 年 5 月，在线 2025-03-07；本地文件名写 2024。PDF 1–14 = 刊页 289–302。

## 环境与命题（PDF 3–7）

- 对连续可微、满足 Walras 定律和价格财富共同零次齐次的需求 $x(p,w)$，$S=D_px+D_wx\, x^\top$。固定财富 $w$，利用 $D_wx=-D_px\,p/w$，得到 $S=D_px(I-px^\top/w)$。这里只限制局部比较静态的对称性，不要求效用最大化。
- 对给定 $p$，使原消费束恰好可负担的归一化补偿价格集合是 $B_w(p)=\{q:q^\top x(p,w)=w\}$；$q(p),r(p)$ 是它的可微选择。归一化把名义财富固定为 $w$，保留同一预算集；此处恒定的是 Slutsky 购买力，不声称全程保持 Hicks 效用。EMVASES 令交换补偿方向的边际货币差 $m_{q,r}$ 对所有这类选择为零。不是对任意两个远离价格向量直接要求有限金额相等。
- **Lemma 1、Proposition 1**：$m_{q,r}=q^\top(S^\top-S)r$；选择集合足够丰富时，EMVASES 当且仅当 Slutsky 矩阵对称。与 Ville 轴的区别是：后者考察实际收入上升的闭合消费回路，这里比较保持 Slutsky 购买力的两条边际补偿路径（PDF 12–13）。

## 证明核查（PDF 10–12，Appendices A1–A2）

1. 对 $q^\top x=w$ 求导得 $x^\top D_pq=-q^\top D_px$，代入 $m=x^\top D_pq(r-p)-x^\top D_pr(q-p)$，两项应用 $x^\top q=x^\top r=w$，即得 Lemma 1 的反对称双线性式。矩阵对称推出 EMVASES。
2. **反向的独立核算**：齐次性与 Walras 定律分别给出 $Sp=0$ 与 $p^\top S=0$，故令 $A=S^\top-S$ 后可把 $q,r$ 换成 $q-p,r-p$。若内部点附近的可行选择实现整个 $x^\perp$ 的小位移，则 $m=0$ 令 $A$ 在该切空间上为零；再用 $p^\top x=w>0$，有 $\operatorname{span}(p)\oplus x^\perp=\mathbb R^L$，推出 $A=0$。A1 的构造用一件需求非零的商品调整补偿价格，其他价格可选；复用时注意可行价格域要允许这些方向，不能只凭一条路径、任意紧集或边界孤点断言反向。

## 反例与原页疑点（PDF 7–10）

- Cobb–Douglas 满足 EMVASES；异质价格注意力的三商品例在默认价格处一般打破对称。PDF 8 把附例的 $E$ 写作 $S-S^\top$ 却将 $m$ 写成 $q^\top E r$，与 Lemma 1 的符号相反；不影响“是否为零”，引用有符号数值应以定义复算。
- 例 3：$x=wp/(p^\top p)$。直接求导得 $S=\frac{w}{p^\top p}(I-pp^\top/(p^\top p))$，对称却在横向为正，故对称不能替代负半定性或完整理性。
- 例 4：PDF 10 印出 $m(c)$ 含因子 $Kp_3-1$；同页的示例 $p=(1,2,1),K=1$ 却报告非零，按显示公式和所写路径不能复现。**独立局部见证**：仍取 $p=(1,2,1),w=1,c=1/2$，有 $x=(1/3,1/6,1/3)$。取 $u=(1,-2,0),v=(0,-2,1)$，两者属于 $x^\perp$，计算 $u^\top(S^\top-S)v=-1/3$；对称部分在该基下对角为 $-2/3,-5/6$、非对角为 $-1/2$，行列式 $11/36>0$。故该点保有负半定而破坏对称；这里不是复证作者所报 $7/24$ 或全域参数分类。

**阅读边界**：正文 PDF 1–10，印刷附录 A1–A3（10–13），回查例 2 和例 4 原图；未实现有限数据检验，作者也把实用检验留给未来工作（PDF 11）。Slutsky、Ville、Gabaix 和 Shafer 留作后续谱系候选，不新增经核边。

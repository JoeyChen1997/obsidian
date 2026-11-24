---
tags: [research/theory, research/algorithmic-pricing]
reading_status: core_read
source_id: 25363
---

# Abada 与 Lambin（2023）：储能学习与表观合谋

Ibrahim Abada and Xavier Lambin, *Artificial Intelligence: Can Seemingly Collusive Outcomes Be Avoided?*, Management Science 69(9), 5042–5065（2023-01-12 在线）。[DOI](https://doi.org/10.1287/mnsc.2022.4623)。本地 PDF 1 对应刊页 5042，PDF 16–22 含正文附录。

## 模型与证据设计

- PDF 4–5，Eqs. (1)–(8)：聚合储能商竞争选择每小时充放电量 $a_i^t$（正为卖电），市场统一出清，即给定竞争性边缘供给后的残余逆需求 $p^t=\widetilde p^t-\beta^t\sum_i a_i^t$。状态中电量满足 $l_i^{t+1}=l_i^t-a_i^t$，受容量／功率约束；当日利润为 $\sum_t p^t a_i^t$。与重复 Bertrand 不同，即使冻住竞对反应，本期操作也会改写未来可行集。
- PDF 6–8、17–18，§§3.3–4.1、Appendix C：各自只监测公开价格及自己的动作、利润和电量，不直接看竞对动作。每天从空电池开始，反复训练这个 24 小时的合成法国日前市场（按 2018-02-01 输入校准，不是该市场实测有合谋）。每时段独立维护 Q 表，以价格和电量离散状态、温度随训练降低的概率规则探索。主文 Eq. (13)／附录 C.1–C.3 有小时间继续价值及跨 episode 项，不等同 Calvano 的一个 Q 表。数值上以 Q 表 $L^1$ 相对容差来记录稳定；基本三家对称情形 100 次，若干敏感性和干预只 10 次。
- PDF 5、16–17，Appendices A–B：用价格接受者的福利最大化、同时规划全日动作路径的 Cournot，以及共同利润最大化作三个基准。Cournot 是全日开放环路基准，不能自动当作动态反馈均衡（PDF 18–19，Appendix D）。

## 结果、偏离与适用边界

| 原页 | 核读结果 | 证据边界 |
| --- | --- | --- |
| PDF 9–10，Eq. (16)、Figures 1–3 | 基准 Q-learning 的合计利润高于 Cournot，福利低于 Cournot；归一化福利损失 $\gamma=(W^{Cournot}-W^{Q})/(W^{Cournot}-W^{Cartel})$ 平均 0.42。 | 0.42 是与 Cournot–卡特尔差距相比的比例，不是总福利降 42%。图 1 以图例为准：黑为 cartel、红为完全竞争；正文稍后的色名把 cartel 写成红色。 |
| PDF 11–12、19，Figure 4、Appendix E | 训练后冻结 Q 表，只强制一方在某一小时改变充放电；把当日总利润与无偏离轨迹相比。从图 4 的均值看，两方向都可能亏损；Appendix E 检查第 4 小时偏离后的轨迹，访问次数常远低于通常策略轨迹。 | 继续损失可来自库存约束或缺乏探索的低质量反应，非只能解释成有意惩罚；带不确定性区间的平均图不支持“每个个体每次都亏”。不反证 Calvano 的特定模型。 |
| PDF 12–15、19–21，Figures 5–8 | 在部分训练 episode 强化对竞争动作的探索，平均 $\gamma$ 从 0.42 降至 0.25；保持总容量、两／三／四家模型对应损失 0.50／0.42／0.30。监管者直接用福利作 Q 目标没有改善该试验，有条件的市场参与规则改善结果，仍未达 Cournot 福利。 | 区分训练过程改变探索与训练后测试；有限校准的数值证据，不是通用监管证明或电网实测效应。 |

核账说明：Appendix A 的 Bellman 递推可从本次操作利润加下期可行库存的延续价值写出，跟价格反应无关；比较偏离时必须控制这个物理渠道。Appendix C.3 明确把 Q 表稳定、动作是否循环、是否均衡分开。本文没有适用于这里的多智能体理论收敛证明；没有复跑仿真。出版首页列数据文件，印刷 Appendix H 给部分校准表；独立数据文件未在本地定位。见 [[Marketing Paper/研究谱系/Paperlist 第二十一批命题对照]]。

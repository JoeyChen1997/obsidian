---
tags: [research/empirical, research/education, research/lottery, research/instrumental-variables]
reading_status: core_read
source_id: 36385
---

# Abdulkadiroğlu 等（2011）：波士顿特许学校与试点学校的录取抽签

Atila Abdulkadiroğlu、Joshua D. Angrist、Susan M. Dynarski、Thomas J. Kane、Parag A. Pathak，*Accountability and Flexibility in Public Schools: Evidence from Boston’s Charters and Pilots*，QJE 126(2), 699–748。[DOI](https://doi.org/10.1093/qje/qjr017)。PDF 从刊页 699 开始（刊页 = PDF 页 + 698）。

## 分配制度、样本与识别（PDF 6–23，Tables I–III）

- 两类学校都可改变课程和部分运营政策，但 charter 是独立学区、面对州续期审查，pilot 留在 Boston Public Schools（BPS），保留多项工会合约规则。抽签识别的是就读整套学校安排的效应，**不是**将自治、问责、工会或教学时长单独随机化。
- Charter 由学校各自独立办超额申请抽签；风险组是同入学年级与年度中、进入研究的申请学校组合。排除兄弟姐妹优先及有保证的续读。工具为初始获得任一相关 offer，或计入候补的 ever offer；作者偏好记录更完整、在有后测样本中平衡也较好的后者。Pilot 用集中 BPS 分配，只取第一志愿为 pilot 的申请人，以第一轮第一志愿 offer 为工具；风险组按第一志愿、walk zone 和入学 cohort 划分，剔除保证入学和手足优先。不同风险组的中签率不必相等。
- 5 所 charter 初中、3 所高中进入抽签研究，无 charter 小学估计；pilot 有小学、初中和高中，只有两所 pilot 高中使用集中分配。剔除基线明显不平衡的 HCA。用州 SIMS 构造截至考试的累计就读年数，计入留级及研究抽签集合外同类型学校；MCAS 按全州公校年级×年份×科目标准化。例：charter 初中有后测 1,386 名学生（Table II），平衡表广样本 1,521（Table III），主数学回归 3,317 条人×年级后测记录（Table IV），不能当作同一分母。
- Eq. (1)–(2) 控制风险组、考试年及年级等，以 offer 移动实际就读年数。除组内随机、相关性和排除限制外，把比率解释为就读剂量的加权因果响应还依赖相应单调性；它不是所有学生、所有学校的平均收益。小学、初中重复成绩按学生和校×年级×年双向聚类，高中按校×年聚类。

## 主要结果与独立复算（PDF 23–35，Tables IV–VI，Figures I–III）

- Table IV 基本控制下，charter 初中数学的第一阶段 .967 年、offer 的 ITT .401σ，复算 .401/.967≈.415σ/年；初中 ELA 为 .253/1.000=.253σ/年。加人口特征与基线成绩后分别为 .359、.198σ/年；高中的数学 .364、ELA .265σ/年。不能互换每次 offer 的作用和每年剂量的作用。
- Pilot 小学 ELA .071σ/年（基本控制），数学无清楚证据；初中和高中 ELA/数学大多不显著，高中写作主题正向。初中数学加入基线后为 −.223（SE .090）；同变的是样本，作者称主要因 K–8 pilot 不再入样，不能归因为基线控制消除同一批人的遗漏偏误。**原表疑点**：PDF 25 的 pilot 高中数学 col. (8) 确印 `0.10`，但同规范 .007/.680≈.0103，正文亦描述近零；保留印刷值和复算值，不默默覆盖。
- 初始 offer 结果总体方向一致但有差异（高中写作 composition 接近零）；potential years 工具结果大体相近，不能把其第一阶段当作单纯留存率。Figure I 的分 cohort 数学 ITT 多数随年级增加，但有噪音，2002 cohort 的七年级数学为插值。Figure III 中以风险组为点的无权斜率 .458（charter）与 −.009（pilot），不等同于以 offer×风险组为工具的 2SLS .446 与 −.007。

## 缺失、机制与外推（PDF 36–49，Tables VII–X）

- 州内公校跟踪能保留转校者；但未有 MCAS 则不进入成绩回归。Charter 初中获 offer 的后测可得率约高 3–4 个百分点；pilot 高中 ELA 加基线控制时高 6.1 个百分点（SE 2.4）。作者报告剔除最不平衡 cohort 后主结果相近；非零缺失差异不能由统计不显著自动消除。排除常规年级过渡和考试学校转学，charter 初中转校差由 −14.6 个百分点缩至 −1.8 个百分点（Table VIII 基础人口控制）。
- Charter 初中成绩提升在基线较弱的申请人较大；Table IX 自身基线交互对 ELA/数学为 −.123/−.146，低 .2σ 对应额外 .025/.029σ。风险组剔除自身的平均基线只是同伴质量代理；负交互不代表把低成绩同伴随机放进课堂会提高成绩。
- 可比较的 lottery 学校中，带基线 OLS 对 charter 初中数学为 .316σ/年，对应 IV .359；未进抽签研究的 charter OLS .148。两种方法在部分学校接近不能证明对其他学校也无选择偏差；pilot 高中两设计的 ELA/数学就明显不同。结论主要适用于运行中、热门、记录可用且相当多采用 No Excuses 做法的学校及其申请群体；不能分离特定办学机制，也无充分长期毕业/大学结果。

**核读范围**：PDF 1–49 主文与印刷表图、50 参考文献末页；回查 PDF 24–25 原图并复算 Wald 比率。未核线上附录的 lottery audit、平衡筛选重估和单 cohort 毕业分析，未重跑行政数据。候选（未入经核图）：集中分配的优先组如何定义可比样本；与[[Marketing Paper/文献卡/Abdulkadiroğlu 等 2015 - 择校中的定向抽签与偏好强度|定向抽签]]的设计目标区分——随机规则既可作为分配工具，也可作为因果识别来源。

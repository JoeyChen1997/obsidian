---
tags: [量化交易, alpha, WorldQuant, 公式化alpha]
source: "101 Formulaic Alphas - arXiv.org.pdf"
authors: "Zura Kakushadze"
date: 2015-12-09
---

# 101 公式化 Alpha — 概述

> 本文由 Zura Kakushadze（Quantigic Solutions LLC / 第比利斯自由大学）于 2015 年发表，首次公开披露了 101 个真实生产环境中使用的量化交易 Alpha 信号公式。

## 核心摘要

- 提供 **101 个真实量化交易 Alpha** 的显式公式（同时也是可执行代码）
- 平均持仓周期约 **0.6 ~ 6.4 天**（短线）
- Alpha 之间的平均两两相关性较低：**15.9%**
- 收益与波动率强相关，与换手率无显著相关性
- 80 个 Alpha 在撰文时已在生产环境中运行

## 两大交易逻辑

| 类型 | 逻辑 | 示例 |
|------|------|------|
| **均值回归 (Mean-Reversion)** | 信号方向与收益方向相反，押注价格回归 | `-ln(今日开盘 / 昨日收盘)` |
| **动量 (Momentum)** | 信号方向与收益方向相同，押注趋势延续 | `ln(昨日收盘 / 昨日开盘)` |

- **Delay-0 Alpha**：信号数据时间与交易时间重合（如用今日开盘价，在开盘时交易）
- **Delay-1 Alpha**：用昨日数据，今日交易

## 实证发现

1. **收益 ~ 波动率**：年化平均日收益与日收益波动率满足幂律关系 `μ ~ σ^0.76`
2. **换手率解释力弱**：换手率对 Alpha 两两相关性的解释力很差（R² ≈ 1.27%）
3. **换手率与波动率有一定相关性**：`ln(σ) ≈ -6.174 + 0.368 × ln(τ)`

## 输入数据说明

| 变量 | 含义 |
|------|------|
| `open, close, high, low` | 日度开/收/高/低价 |
| `volume` | 日成交量 |
| `vwap` | 成交量加权平均价（VWAP） |
| `returns` | 日度收盘到收盘收益率 |
| `cap` | 市值 |
| `adv{d}` | 过去 d 天的平均日成交额 |
| `IndClass` | 行业分类（GICS/BICS/NAICS/SIC 等） |

## 常用函数/算子速查

| 函数 | 含义 |
|------|------|
| `rank(x)` | 截面排名（升序） |
| `delay(x, d)` | x 在 d 天前的值 |
| `delta(x, d)` | 今日 x 减去 d 天前的 x |
| `correlation(x, y, d)` | 过去 d 天 x 与 y 的时序相关系数 |
| `covariance(x, y, d)` | 过去 d 天 x 与 y 的时序协方差 |
| `ts_rank(x, d)` | 过去 d 天的时序排名 |
| `ts_min/ts_max(x, d)` | 过去 d 天的时序最小/最大值 |
| `ts_argmin/ts_argmax(x, d)` | 时序最小/最大值出现在第几天 |
| `stddev(x, d)` | 过去 d 天的移动标准差 |
| `sum(x, d)` | 过去 d 天的时序求和 |
| `product(x, d)` | 过去 d 天的时序连乘 |
| `decay_linear(x, d)` | 线性衰减加权移动平均（权重 d, d-1, …, 1，归一化） |
| `scale(x, a)` | 缩放 x 使得 `sum(abs(x)) = a`（默认 a=1） |
| `indneutralize(x, g)` | 在行业组 g 内对 x 做截面去均值（行业中性化） |
| `sign(x)` | 符号函数：x>0 返回 1，x<0 返回 -1，x=0 返回 0 |
| `signedpower(x, a)` | x 的 a 次方（保留符号） |

## Alpha 列表导航

- [[101公式化Alpha - Alpha#1到#25]]
- [[101公式化Alpha - Alpha#26到#50]]
- [[101公式化Alpha - Alpha#51到#75]]
- [[101公式化Alpha - Alpha#76到#101]]

## 参考资料

- 原文：[SSRN 2701346](https://ssrn.com/abstract=2701346)
- 相关：[[量化交易学习/量化交易索引]]

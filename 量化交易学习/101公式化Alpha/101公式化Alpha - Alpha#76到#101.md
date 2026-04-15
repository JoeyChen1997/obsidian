---
tags: [量化交易, alpha, WorldQuant]
---

# 101 公式化 Alpha — #76 到 #101

> 函数定义见 [[101公式化Alpha - 概述]]

---

## Alpha#76
```
(max(rank(decay_linear(delta(vwap, 1.24), 11.83)),
Ts_Rank(decay_linear(Ts_Rank(correlation(IndNeutralize(low, IndClass.sector), adv81, 8.15), 19.57), 17.15), 19.38)) * -1)
```
**逻辑**：VWAP 变化线性衰减排名 与 行业中性化低价与 81 日均量相关性时序排名的线性衰减时序排名，取最大值后取负。
**类型**：行业中性化 + 量价

---

## Alpha#77
```
min(rank(decay_linear(((((high + low) / 2) + high) - (vwap + high)), 20.05)),
rank(decay_linear(correlation(((high + low) / 2), adv40, 3.16), 5.64)))
```
**逻辑**：两个线性衰减排名取最小值：中间价+高价偏离 VWAP+高价，以及中间价与 40 日均量相关性。
**类型**：价格结构 + 量价

---

## Alpha#78
```
(rank(correlation(sum(((low * 0.352) + (vwap * 0.648)), 19.74),
sum(adv40, 19.74), 6.83))^rank(correlation(rank(vwap), rank(volume), 5.77)))
```
**逻辑**：加权价格与 40 日均量的相关性排名，以 VWAP 排名与成交量排名相关性排名为指数。
**类型**：量价关系

---

## Alpha#79
```
rank(delta(IndNeutralize(((close * 0.607) + (open * 0.393)), IndClass.sector), 1.23))
< rank(correlation(Ts_Rank(vwap, 3.61), Ts_Rank(adv150, 9.19), 14.66))
```
**逻辑**：行业中性化加权价格 1 日变化排名 < VWAP 时序排名与 150 日均量时序排名相关性排名，返回布尔值。
**类型**：行业中性化 + 量价

---

## Alpha#80
```
((rank(Sign(delta(IndNeutralize(((open * 0.868) + (high * 0.132)), IndClass.industry), 4.05)))
^Ts_Rank(correlation(high, adv10, 5.11), 5.54)) * -1)
```
**逻辑**：行业中性化加权价格变化符号排名，以最高价与 10 日均量相关性时序排名为指数，取负。
**类型**：行业中性化 + 量价

---

## Alpha#81
```
((rank(Log(product(rank((rank(correlation(vwap, sum(adv10, 49.61), 8.48))^4)), 14.97)))
< rank(correlation(rank(vwap), rank(volume), 5.08))) * -1)
```
**逻辑**：VWAP 与 10 日均量相关性排名四次方的乘积对数排名 < VWAP 排名与成交量排名相关性排名，取负。
**类型**：量价关系

---

## Alpha#82
```
(min(rank(decay_linear(delta(open, 1.46), 14.87)),
Ts_Rank(decay_linear(correlation(IndNeutralize(volume, IndClass.sector),
((open * 0.634) + (open * 0.366)), 17.48), 6.92), 13.43)) * -1)
```
**逻辑**：开盘价变化线性衰减排名 与 行业中性化成交量与开盘价相关性线性衰减时序排名，取最小值后取负。
**类型**：行业中性化 + 量价

---

## Alpha#83
```
((rank(delay(((high - low) / (sum(close, 5) / 5)), 2)) * rank(rank(volume)))
/ (((high - low) / (sum(close, 5) / 5)) / (vwap - close)))
```
**逻辑**：2 日前日内振幅/5 日均价的排名 $\times$ 成交量排名的平方，除以当前日内振幅/5 日均价与 VWAP-收盘价之比。
**类型**：量价结构

---

## Alpha#84
```
SignedPower(Ts_Rank((vwap - ts_max(vwap, 15.32)), 20.71), delta(close, 4.97))
```
**逻辑**：VWAP 偏离 15 日最高 VWAP 的 20 日时序排名，以 5 日价格变化为指数（保留符号）。
**类型**：价格偏离 + 动量

---

## Alpha#85
```
(rank(correlation(((high * 0.877) + (close * 0.123)), adv30, 9.61))
^rank(correlation(Ts_Rank(((high + low) / 2), 3.71), Ts_Rank(volume, 10.16), 7.11)))
```
**逻辑**：加权价格与 30 日均量相关性排名，以中间价时序排名与成交量时序排名相关性排名为指数。
**类型**：量价关系

---

## Alpha#86
```
((Ts_Rank(correlation(close, sum(adv20, 14.74), 6.00), 20.42)
< rank(((open + close) - (vwap + open)))) * -1)
```
**逻辑**：收盘价与 20 日均量相关性时序排名 < 收盘价偏离 VWAP 排名，取负。
**类型**：量价关系

---

## Alpha#87
```
(max(rank(decay_linear(delta(((close * 0.370) + (vwap * 0.630)), 1.91), 2.65)),
Ts_Rank(decay_linear(abs(correlation(IndNeutralize(adv81, IndClass.industry), close, 13.41)), 4.90), 14.45)) * -1)
```
**逻辑**：加权价格变化线性衰减排名 与 行业中性化 81 日均量与收盘价相关性绝对值线性衰减时序排名，取最大值后取负。
**类型**：行业中性化 + 量价

---

## Alpha#88
```
min(rank(decay_linear(((rank(open) + rank(low)) - (rank(high) + rank(close))), 8.07)),
Ts_Rank(decay_linear(correlation(Ts_Rank(close, 8.45), Ts_Rank(adv60, 20.70), 8.01), 6.65), 2.62))
```
**逻辑**：开盘+低价排名之和减去高价+收盘排名之和的线性衰减排名，与收盘时序排名和 60 日均量时序排名相关性线性衰减时序排名，取最小值。
**类型**：价格结构 + 量价

---

## Alpha#89
```
Ts_Rank(decay_linear(correlation(((low * 0.967) + (low * 0.033)), adv10, 6.94), 5.52), 3.80)
- Ts_Rank(decay_linear(delta(IndNeutralize(vwap, IndClass.industry), 3.48), 10.15), 15.30)
```
**逻辑**：低价与 10 日均量相关性线性衰减时序排名，减去行业中性化 VWAP 变化线性衰减时序排名。
**类型**：行业中性化 + 量价

---

## Alpha#90
```
((rank((close - ts_max(close, 4.67)))^Ts_Rank(correlation(IndNeutralize(adv40, IndClass.subindustry), low, 5.38), 3.22)) * -1)
```
**逻辑**：收盘价偏离 5 日最高收盘价排名，以行业中性化 40 日均量与低价相关性时序排名为指数，取负。
**类型**：行业中性化 + 均值回归

---

## Alpha#91
```
((Ts_Rank(decay_linear(decay_linear(correlation(IndNeutralize(close, IndClass.industry), volume, 9.75), 16.40), 3.83), 4.87)
- rank(decay_linear(correlation(vwap, adv30, 4.01), 2.68))) * -1)
```
**逻辑**：行业中性化收盘价与成交量相关性双重线性衰减时序排名，减去 VWAP 与 30 日均量相关性线性衰减排名，取负。
**类型**：行业中性化 + 量价

---

## Alpha#92
```
min(Ts_Rank(decay_linear(((((high + low) / 2) + close) < (low + open)), 14.72), 18.87),
Ts_Rank(decay_linear(correlation(rank(low), rank(adv30), 7.59), 6.94), 6.81))
```
**逻辑**：中间价+收盘价 < 低价+开盘价的布尔值线性衰减时序排名，与低价排名和 30 日均量排名相关性线性衰减时序排名，取最小值。
**类型**：价格结构 + 量价

---

## Alpha#93
```
Ts_Rank(decay_linear(correlation(IndNeutralize(vwap, IndClass.industry), adv81, 17.42), 19.85), 7.54)
/ rank(decay_linear(delta(((close * 0.524) + (vwap * 0.476)), 2.77), 16.27))
```
**逻辑**：行业中性化 VWAP 与 81 日均量相关性线性衰减时序排名，除以加权价格变化线性衰减排名。
**类型**：行业中性化 + 量价

---

## Alpha#94
```
((rank((vwap - ts_min(vwap, 11.58)))^Ts_Rank(correlation(Ts_Rank(vwap, 19.65), Ts_Rank(adv60, 4.03), 18.09), 2.71)) * -1)
```
**逻辑**：VWAP 偏离 12 日低点排名，以 VWAP 时序排名与 60 日均量时序排名相关性时序排名为指数，取负。
**类型**：量价关系

---

## Alpha#95
```
rank((open - ts_min(open, 12.41)))
< Ts_Rank((rank(correlation(sum(((high + low) / 2), 19.14), sum(adv40, 19.14), 12.87))^5), 11.76)
```
**逻辑**：开盘价偏离 12 日低点排名 < 中间价与 40 日均量相关性排名五次方的时序排名，返回布尔值。
**类型**：量价关系

---

## Alpha#96
```
(max(Ts_Rank(decay_linear(correlation(rank(vwap), rank(volume), 3.84), 4.17), 8.38),
Ts_Rank(decay_linear(Ts_ArgMax(correlation(Ts_Rank(close, 7.45), Ts_Rank(adv60, 4.13), 3.65), 12.66), 14.04), 13.41)) * -1)
```
**逻辑**：VWAP 排名与成交量排名相关性线性衰减时序排名，与收盘时序排名和 60 日均量时序排名相关性最大值出现时间线性衰减时序排名，取最大值后取负。
**类型**：量价关系

---

## Alpha#97
```
((rank(decay_linear(delta(IndNeutralize(((low * 0.721) + (vwap * 0.279)), IndClass.industry), 3.37), 20.45))
- Ts_Rank(decay_linear(Ts_Rank(correlation(Ts_Rank(low, 7.88), Ts_Rank(adv60, 17.26), 4.98), 18.59), 15.72), 6.72)) * -1)
```
**逻辑**：行业中性化加权价格变化线性衰减排名，减去低价时序排名与 60 日均量时序排名相关性时序排名的线性衰减时序排名，取负。
**类型**：行业中性化 + 量价

---

## Alpha#98
```
rank(decay_linear(correlation(vwap, sum(adv5, 26.47), 4.58), 7.18))
- rank(decay_linear(Ts_Rank(Ts_ArgMin(correlation(rank(open), rank(adv15), 20.82), 8.63), 6.96), 8.07))
```
**逻辑**：VWAP 与 5 日均量相关性线性衰减排名，减去开盘价排名与 15 日均量排名相关性最小值出现时间时序排名的线性衰减排名。
**类型**：量价关系

---

## Alpha#99
```
((rank(correlation(sum(((high + low) / 2), 19.90), sum(adv60, 19.90), 8.81))
< rank(correlation(low, volume, 6.28))) * -1)
```
**逻辑**：中间价与 60 日均量相关性排名 < 低价与成交量相关性排名，取负。
**类型**：量价关系

---

## Alpha#100
```
0 - (1 * (((1.5 * scale(indneutralize(indneutralize(rank(((((close - low) - (high - close)) / (high - low)) * volume)),
IndClass.subindustry), IndClass.subindustry)))
- scale(indneutralize((correlation(close, rank(adv20), 5) - rank(ts_argmin(close, 30))),
IndClass.subindustry))) * (volume / adv20)))
```
**逻辑**：日内位置加权成交量的双重行业中性化缩放（$\times 1.5$），减去收盘价与均量相关性减去 30 日最低收盘价出现时间的行业中性化缩放，乘以相对成交量，取负。
**类型**：行业中性化 + 量价结构

---

## Alpha#101
```
(close - open) / ((high - low) + 0.001)
```
**逻辑**：日内涨跌幅除以日内振幅（加小量 $0.001$ 防除零）。即收盘价在日内区间的相对位置，正值表示收盘偏高（动量），负值表示收盘偏低（均值回归）。
**类型**：Delay-1 动量（最简洁的 Alpha）

> 这是 101 个 Alpha 中最简单的一个，也是 Delay-1 动量 Alpha 的典型代表。

---

← [[101公式化Alpha - Alpha#51到#75]] | [[101公式化Alpha - 概述]] →

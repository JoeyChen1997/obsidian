---
tags: [量化交易, alpha, WorldQuant]
---

# 101 公式化 Alpha — #1 到 #25

> 函数定义见 [[101公式化Alpha - 概述]]

---

## Alpha#1
```
rank(Ts_ArgMax(SignedPower(((returns < 0) ? stddev(returns, 20) : close), 2.), 5)) - 0.5
```
**逻辑**：若收益为负，用近 20 日收益标准差的平方；否则用收盘价的平方。找出过去 5 天该值最大的那天，对其排名后减去 $0.5$。
**类型**：均值回归 + 波动率条件

---

## Alpha#2
```
-1 * correlation(rank(delta(log(volume), 2)), rank(((close - open) / open)), 6)
```
**逻辑**：成交量对数变化的排名 与 日内涨跌幅排名 之间的 6 日相关性，取负。
**类型**：量价背离

---

## Alpha#3
```
-1 * correlation(rank(open), rank(volume), 10)
```
**逻辑**：开盘价排名与成交量排名的 10 日相关性，取负。
**类型**：量价关系

---

## Alpha#4
```
-1 * Ts_Rank(rank(low), 9)
```
**逻辑**：最低价截面排名的 9 日时序排名，取负。
**类型**：均值回归

---

## Alpha#5
```
rank((open - (sum(vwap, 10) / 10))) * (-1 * abs(rank((close - vwap))))
```
**逻辑**：开盘价偏离 10 日 VWAP 均值的排名，乘以收盘价偏离 VWAP 绝对排名的负值。
**类型**：价格偏离 VWAP

---

## Alpha#6
```
-1 * correlation(open, volume, 10)
```
**逻辑**：开盘价与成交量的 10 日相关性，取负。
**类型**：量价关系

---

## Alpha#7
```
(adv20 < volume) ? ((-1 * ts_rank(abs(delta(close, 7)), 60)) * sign(delta(close, 7))) : (-1 * 1)
```
**逻辑**：若当日成交量大于 20 日均量，则用 7 日价格变化的方向乘以其绝对变化的 60 日时序排名（取负）；否则直接返回 -1。
**类型**：成交量条件 + 动量

---

## Alpha#8
```
-1 * rank(((sum(open, 5) * sum(returns, 5)) - delay((sum(open, 5) * sum(returns, 5)), 10)))
```
**逻辑**：5 日开盘价之和与 5 日收益之和的乘积，减去 10 天前的同一乘积，对差值排名取负。
**类型**：动量

---

## Alpha#9
```
(0 < ts_min(delta(close, 1), 5)) ? delta(close, 1) :
((ts_max(delta(close, 1), 5) < 0) ? delta(close, 1) : (-1 * delta(close, 1)))
```
**逻辑**：
- 若过去 5 天日涨跌均为正 → 顺势（动量）
- 若过去 5 天日涨跌均为负 → 顺势（动量）
- 否则 → 逆势（均值回归）

**类型**：条件动量/均值回归

---

## Alpha#10
```
rank(((0 < ts_min(delta(close, 1), 4)) ? delta(close, 1) :
((ts_max(delta(close, 1), 4) < 0) ? delta(close, 1) : (-1 * delta(close, 1)))))
```
**逻辑**：与 Alpha#9 类似，但用 4 天窗口，并对结果做截面排名。
**类型**：条件动量/均值回归

---

## Alpha#11
```
(rank(ts_max((vwap - close), 3)) + rank(ts_min((vwap - close), 3))) * rank(delta(volume, 3))
```
**逻辑**：VWAP 与收盘价差值的 3 日最大/最小排名之和，乘以 3 日成交量变化排名。
**类型**：量价关系

---

## Alpha#12
```
sign(delta(volume, 1)) * (-1 * delta(close, 1))
```
**逻辑**：成交量变化方向 $\times$ 价格变化的负值。成交量增加时做空，成交量减少时做多（均值回归）。
**类型**：均值回归

---

## Alpha#13
```
-1 * rank(covariance(rank(close), rank(volume), 5))
```
**逻辑**：收盘价排名与成交量排名的 5 日协方差，排名后取负。
**类型**：量价协方差

---

## Alpha#14
```
(-1 * rank(delta(returns, 3))) * correlation(open, volume, 10)
```
**逻辑**：3 日收益变化排名（取负）$\times$ 开盘价与成交量的 10 日相关性。
**类型**：动量 + 量价

---

## Alpha#15
```
-1 * sum(rank(correlation(rank(high), rank(volume), 3)), 3)
```
**逻辑**：最高价排名与成交量排名的 3 日相关性，对其排名后求 3 日累加，取负。
**类型**：量价关系

---

## Alpha#16
```
-1 * rank(covariance(rank(high), rank(volume), 5))
```
**逻辑**：最高价排名与成交量排名的 5 日协方差，排名后取负。
**类型**：量价协方差

---

## Alpha#17
```
((-1 * rank(ts_rank(close, 10))) * rank(delta(delta(close, 1), 1))) *
rank(ts_rank((volume / adv20), 5))
```
**逻辑**：收盘价 10 日时序排名（取负）$\times$ 价格二阶差分排名 $\times$ 相对成交量 5 日时序排名。
**类型**：多因子组合

---

## Alpha#18
```
-1 * rank(((stddev(abs((close - open)), 5) + (close - open)) + correlation(close, open, 10)))
```
**逻辑**：日内振幅标准差 + 日内涨跌 + 收盘/开盘 10 日相关性，三者之和排名取负。
**类型**：波动率 + 价格关系

---

## Alpha#19
```
(-1 * sign(((close - delay(close, 7)) + delta(close, 7)))) * (1 + rank((1 + sum(returns, 250))))
```
**逻辑**：7 日价格变化方向取负，乘以 250 日累计收益排名的放大因子。
**类型**：长期动量调整的短期均值回归

---

## Alpha#20
```
((-1 * rank((open - delay(high, 1)))) * rank((open - delay(close, 1)))) *
rank((open - delay(low, 1)))
```
**逻辑**：今日开盘价相对昨日高/收/低价的偏离排名之积，取负。
**类型**：隔夜跳空

---

## Alpha#21
```
(((sum(close, 8) / 8) + stddev(close, 8)) < (sum(close, 2) / 2)) ? (-1 * 1) :
(((sum(close, 2) / 2) < ((sum(close, 8) / 8) - stddev(close, 8))) ? 1 :
(((1 < (volume / adv20)) || ((volume / adv20) == 1)) ? 1 : (-1 * 1)))
```
**逻辑**：
- 近期均价 $>$ 长期均价 $+$ 标准差 → 做空（$-1$）
- 近期均价 $<$ 长期均价 $-$ 标准差 → 做多（$+1$）
- 否则看成交量：量大做多，量小做空

**类型**：均值回归 + 成交量确认

---

## Alpha#22
```
-1 * (delta(correlation(high, volume, 5), 5) * rank(stddev(close, 20)))
```
**逻辑**：最高价与成交量 5 日相关性的 5 日变化，乘以 20 日收盘价波动率排名，取负。
**类型**：量价相关性变化

---

## Alpha#23
```
(((sum(high, 20) / 20) < high) ? (-1 * delta(high, 2)) : 0)
```
**逻辑**：若当日最高价高于 20 日均值，则做空（取 2 日最高价变化的负值）；否则为 0。
**类型**：均值回归

---

## Alpha#24
```
((((delta((sum(close, 100) / 100), 100) / delay(close, 100)) < 0.05) ||
((delta((sum(close, 100) / 100), 100) / delay(close, 100)) == 0.05)) ?
(-1 * (close - ts_min(close, 100))) : (-1 * delta(close, 3)))
```
**逻辑**：
- 若 100 日均价变化率 $\leq 5\%$（趋势平缓）→ 做空偏离 100 日低点的幅度
- 否则 → 做空 3 日价格变化

**类型**：条件均值回归

---

## Alpha#25
```
rank(((((-1 * returns) * adv20) * vwap) * (high - close)))
```
**逻辑**：收益率取负 $\times$ 20 日均量 $\times$ VWAP $\times$ 日内振幅（高-收），对乘积排名。
**类型**：多因子组合

---

← [[101公式化Alpha - 概述]] | [[101公式化Alpha - Alpha#26到#50]] →

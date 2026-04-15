---
tags: [量化交易, alpha, WorldQuant]
---

# 101 公式化 Alpha — #26 到 #50

> 函数定义见 [[101公式化Alpha - 概述]]

---

## Alpha#26
```
-1 * ts_max(correlation(ts_rank(volume, 5), ts_rank(high, 5), 5), 3)
```
**逻辑**：成交量 5 日时序排名与最高价 5 日时序排名的 5 日相关性，取过去 3 天最大值，取负。
**类型**：量价关系

---

## Alpha#27
```
(0.5 < rank((sum(correlation(rank(volume), rank(vwap), 6), 2) / 2.0))) ? (-1 * 1) : 1
```
**逻辑**：成交量排名与 VWAP 排名的 6 日相关性，2 日均值排名超过 0.5 则做空，否则做多。
**类型**：量价相关性

---

## Alpha#28
```
scale(((correlation(adv20, low, 5) + ((high + low) / 2)) - close))
```
**逻辑**：20 日均量与最低价的 5 日相关性，加上中间价，减去收盘价，缩放归一化。
**类型**：量价偏离

---

## Alpha#29
```
min(product(rank(rank(scale(log(sum(ts_min(rank(rank((-1 * rank(delta((close - 1), 5))))), 2), 1))))), 1), 5)
+ ts_rank(delay((-1 * returns), 6), 5)
```
**逻辑**：复合嵌套因子，结合价格变化排名的对数变换与 6 日前收益的时序排名。
**类型**：复合动量

---

## Alpha#30
```
(((1.0 - rank(((sign((close - delay(close, 1))) + sign((delay(close, 1) - delay(close, 2)))) +
sign((delay(close, 2) - delay(close, 3)))))) * sum(volume, 5)) / sum(volume, 20))
```
**逻辑**：近 3 日价格方向符号之和的排名（取 1 减），乘以 5 日成交量，除以 20 日成交量。
**类型**：短期动量 + 成交量

---

## Alpha#31
```
rank(rank(rank(decay_linear((-1 * rank(rank(delta(close, 10)))), 10))))
+ rank((-1 * delta(close, 3)))
+ sign(scale(correlation(adv20, low, 12)))
```
**逻辑**：三部分之和：10 日价格变化排名的线性衰减加权、3 日价格变化取负排名、均量与低价 12 日相关性的符号。
**类型**：多因子组合

---

## Alpha#32
```
scale(((sum(close, 7) / 7) - close)) + (20 * scale(correlation(vwap, delay(close, 5), 230)))
```
**逻辑**：7 日均价偏离当前收盘价（均值回归项）+ 20 倍的 VWAP 与 5 日前收盘价 230 日相关性（长期动量项）。
**类型**：均值回归 + 长期动量

---

## Alpha#33
```
rank((-1 * ((1 - (open / close))^1)))
```
**逻辑**：1 减去开收比，取负，排名。即收盘价相对开盘价涨幅越大，信号越负（均值回归）。
**类型**：日内均值回归

---

## Alpha#34
```
rank(((1 - rank((stddev(returns, 2) / stddev(returns, 5)))) + (1 - rank(delta(close, 1)))))
```
**逻辑**：短期波动率相对长期波动率的排名（取 1 减）+ 1 日价格变化排名（取 1 减），两者之和排名。
**类型**：波动率 + 均值回归

---

## Alpha#35
```
(Ts_Rank(volume, 32) * (1 - Ts_Rank(((close + high) - low), 16))) *
(1 - Ts_Rank(returns, 32))
```
**逻辑**：成交量 32 日时序排名 × (1 - 价格区间 16 日时序排名) × (1 - 收益 32 日时序排名)。
**类型**：量价组合

---

## Alpha#36
```
(((((2.21 * rank(correlation((close - open), delay(volume, 1), 15)))
+ (0.7 * rank((open - close))))
+ (0.73 * rank(Ts_Rank(delay((-1 * returns), 6), 5))))
+ rank(abs(correlation(vwap, adv20, 6))))
+ (0.6 * rank((((sum(close, 200) / 200) - open) * (close - open)))))
```
**逻辑**：五个加权因子之和：日内涨跌与昨日量的相关性、日内涨跌、6 日前收益时序排名、VWAP 与均量相关性、长期均价偏离与日内涨跌的乘积。
**类型**：多因子加权组合

---

## Alpha#37
```
rank(correlation(delay((open - close), 1), close, 200)) + rank((open - close))
```
**逻辑**：昨日日内涨跌与收盘价的 200 日相关性排名 + 今日日内涨跌排名。
**类型**：长期相关性 + 日内动量

---

## Alpha#38
```
(-1 * rank(Ts_Rank(close, 10))) * rank((close / open))
```
**逻辑**：收盘价 10 日时序排名（取负）× 收盘/开盘比排名。
**类型**：均值回归 + 日内动量

---

## Alpha#39
```
(-1 * rank((delta(close, 7) * (1 - rank(decay_linear((volume / adv20), 9)))))) *
(1 + rank(sum(returns, 250)))
```
**逻辑**：7 日价格变化 × (1 - 相对成交量线性衰减排名)，取负，再乘以 250 日累计收益排名的放大因子。
**类型**：动量 + 成交量调整

---

## Alpha#40
```
(-1 * rank(stddev(high, 10))) * correlation(high, volume, 10)
```
**逻辑**：最高价 10 日波动率排名（取负）× 最高价与成交量的 10 日相关性。
**类型**：波动率 + 量价

---

## Alpha#41
```
((high * low)^0.5) - vwap
```
**逻辑**：高低价几何均值减去 VWAP。若几何均值高于 VWAP，信号为正（做多）。
**类型**：价格偏离 VWAP

---

## Alpha#42
```
rank((vwap - close)) / rank((vwap + close))
```
**逻辑**：VWAP 超过收盘价的排名，除以两者之和的排名。
**类型**：价格偏离 VWAP

---

## Alpha#43
```
ts_rank((volume / adv20), 20) * ts_rank((-1 * delta(close, 7)), 8)
```
**逻辑**：相对成交量 20 日时序排名 × 7 日价格变化取负的 8 日时序排名。
**类型**：量价组合（均值回归）

---

## Alpha#44
```
-1 * correlation(high, rank(volume), 5)
```
**逻辑**：最高价与成交量排名的 5 日相关性，取负。
**类型**：量价关系

---

## Alpha#45
```
-1 * ((rank((sum(delay(close, 5), 20) / 20)) * correlation(close, volume, 2)) *
rank(correlation(sum(close, 5), sum(close, 20), 2)))
```
**逻辑**：5 日前收盘价 20 日均值排名 × 收盘价与成交量 2 日相关性 × 短期/长期收盘价相关性排名，取负。
**类型**：多因子组合

---

## Alpha#46
```
(0.25 < (((delay(close, 20) - delay(close, 10)) / 10) - ((delay(close, 10) - close) / 10))) ?
(-1 * 1) :
(((((delay(close, 20) - delay(close, 10)) / 10) - ((delay(close, 10) - close) / 10)) < 0) ? 1 :
((-1 * 1) * (close - delay(close, 1))))
```
**逻辑**：比较 20-10 日前与 10-0 日前的价格变化速率：
- 加速上涨（差值 $> 0.25$）→ 做空
- 加速下跌（差值 $< 0$）→ 做多
- 否则 → 均值回归

**类型**：加速度动量

---

## Alpha#47
```
((((rank((1 / close)) * volume) / adv20) * ((high * rank((high - close))) / (sum(high, 5) / 5)))
- rank((vwap - delay(vwap, 5))))
```
**逻辑**：价格倒数排名 × 相对成交量 × 最高价偏离 5 日均值的加权，减去 VWAP 5 日变化排名。
**类型**：多因子组合

---

## Alpha#48
```
indneutralize(((correlation(delta(close, 1), delta(delay(close, 1), 1), 250) *
delta(close, 1)) / close), IndClass.subindustry)
/ sum(((delta(close, 1) / delay(close, 1))^2), 250)
```
**逻辑**：日收益与昨日收益的 250 日相关性 × 日收益，行业中性化后，除以 250 日收益平方和。
**类型**：行业中性化动量

---

## Alpha#49
```
(((((delay(close, 20) - delay(close, 10)) / 10) - ((delay(close, 10) - close) / 10)) < (-1 * 0.1)) ?
1 : ((-1 * 1) * (close - delay(close, 1))))
```
**逻辑**：若价格加速度 $< -0.1$（加速下跌）→ 做多；否则 → 均值回归。
**类型**：条件动量

---

## Alpha#50
```
-1 * ts_max(rank(correlation(rank(volume), rank(vwap), 5)), 5)
```
**逻辑**：成交量排名与 VWAP 排名的 5 日相关性，对其排名后取 5 日最大值，取负。
**类型**：量价相关性

---

← [[101公式化Alpha - Alpha#1到#25]] | [[101公式化Alpha - Alpha#51到#75]] →

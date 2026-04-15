---
tags: [量化交易, alpha, WorldQuant]
---

# 101 公式化 Alpha — #51 到 #75

> 函数定义见 [[101公式化Alpha - 概述]]

---

## Alpha#51
```
(((((delay(close, 20) - delay(close, 10)) / 10) - ((delay(close, 10) - close) / 10)) < (-1 * 0.05)) ?
1 : ((-1 * 1) * (close - delay(close, 1))))
```
**逻辑**：与 Alpha#49 类似，阈值改为 $-0.05$（更宽松的加速下跌条件）→ 做多；否则均值回归。
**类型**：条件动量

---

## Alpha#52
```
((((-1 * ts_min(low, 5)) + delay(ts_min(low, 5), 5)) * rank(((sum(returns, 240) - sum(returns, 20)) / 220)))
* ts_rank(volume, 5))
```
**逻辑**：5 日最低价的 5 日变化（取负）× 长期收益减短期收益的排名 × 成交量 5 日时序排名。
**类型**：动量 + 成交量

---

## Alpha#53
```
-1 * delta((((close - low) - (high - close)) / (close - low)), 9)
```
**逻辑**：收盘价在日内区间位置（类似 RSI 日内版）的 9 日变化，取负。
**类型**：均值回归

---

## Alpha#54
```
((-1 * ((low - close) * (open^5))) / ((low - high) * (close^5)))
```
**逻辑**：低价与收盘价之差（通常为负）× 开盘价五次方，除以日内振幅 × 收盘价五次方，取负。
**类型**：价格结构

---

## Alpha#55
```
-1 * correlation(rank(((close - ts_min(low, 12)) / (ts_max(high, 12) - ts_min(low, 12)))),
rank(volume), 6)
```
**逻辑**：收盘价在 12 日高低区间内的相对位置排名，与成交量排名的 6 日相关性，取负。
**类型**：量价关系

---

## Alpha#56
```
0 - (1 * (rank((sum(returns, 10) / sum(sum(returns, 2), 3))) * rank((returns * cap))))
```
**逻辑**：10 日收益与短期收益之比的排名 × 收益与市值乘积的排名，取负。
**类型**：动量 + 市值

---

## Alpha#57
```
0 - (1 * ((close - vwap) / decay_linear(rank(ts_argmax(close, 30)), 2)))
```
**逻辑**：收盘价偏离 VWAP，除以 30 日最高收盘价出现时间的线性衰减排名，取负。
**类型**：价格偏离 VWAP

---

## Alpha#58
```
-1 * Ts_Rank(decay_linear(correlation(IndNeutralize(vwap, IndClass.sector), volume, 3.93), 7.89), 5.50)
```
**逻辑**：行业中性化 VWAP 与成交量的相关性，线性衰减加权后的时序排名，取负。
**类型**：行业中性化量价

---

## Alpha#59
```
-1 * Ts_Rank(decay_linear(correlation(IndNeutralize(((vwap * 0.728) + (vwap * 0.272)),
IndClass.industry), volume, 4.25), 16.23), 8.20)
```
**逻辑**：行业中性化 VWAP（加权平均，实际等于 VWAP）与成交量相关性的线性衰减时序排名，取负。
**类型**：行业中性化量价

---

## Alpha#60
```
0 - (1 * ((2 * scale(rank(((((close - low) - (high - close)) / (high - low)) * volume))))
- scale(rank(ts_argmax(close, 10)))))
```
**逻辑**：2 × 日内位置加权成交量的缩放排名，减去 10 日最高收盘价出现时间的缩放排名，取负。
**类型**：量价结构

---

## Alpha#61
```
rank((vwap - ts_min(vwap, 16.12))) < rank(correlation(vwap, adv180, 17.93))
```
**逻辑**：VWAP 偏离 16 日低点的排名 < VWAP 与 180 日均量相关性的排名，返回布尔值（0/1）。
**类型**：量价关系

---

## Alpha#62
```
((rank(correlation(vwap, sum(adv20, 22.41), 9.91)) <
rank(((rank(open) + rank(open)) < (rank(((high + low) / 2)) + rank(high))))) * -1)
```
**逻辑**：VWAP 与均量相关性排名 < 开盘价排名组合与中间价/高价排名组合的比较，取负。
**类型**：多因子比较

---

## Alpha#63
```
((rank(decay_linear(delta(IndNeutralize(close, IndClass.industry), 2.25), 8.22))
- rank(decay_linear(correlation(((vwap * 0.318) + (open * 0.682)), sum(adv180, 37.25), 13.56), 12.29))) * -1)
```
**逻辑**：行业中性化收盘价变化的线性衰减排名，减去价格加权均量相关性的线性衰减排名，取负。
**类型**：行业中性化 + 量价

---

## Alpha#64
```
((rank(correlation(sum(((open * 0.178) + (low * 0.822)), 12.71), sum(adv120, 12.71), 16.62))
< rank(delta(((((high + low) / 2) * 0.178) + (vwap * 0.822)), 3.70))) * -1)
```
**逻辑**：加权价格与 120 日均量的相关性排名 < 加权中间价变化排名，取负。
**类型**：量价关系

---

## Alpha#65
```
((rank(correlation(((open * 0.00817) + (vwap * 0.99183)), sum(adv60, 8.69), 6.40))
< rank((open - ts_min(open, 13.64)))) * -1)
```
**逻辑**：加权价格与 60 日均量相关性排名 < 开盘价偏离 13 日低点排名，取负。
**类型**：量价关系

---

## Alpha#66
```
((rank(decay_linear(delta(vwap, 3.51), 7.23))
+ Ts_Rank(decay_linear(((((low * 0.966) + (low * 0.034)) - vwap) / (open - ((high + low) / 2))), 11.42), 6.73)) * -1)
```
**逻辑**：VWAP 变化的线性衰减排名 + 低价偏离 VWAP 与日内振幅之比的时序排名，取负。
**类型**：价格结构

---

## Alpha#67
```
((rank((high - ts_min(high, 2.15)))^rank(correlation(IndNeutralize(vwap, IndClass.sector),
IndNeutralize(adv20, IndClass.subindustry), 6.03))) * -1)
```
**逻辑**：最高价偏离 2 日低点的排名，以行业中性化 VWAP 与均量相关性排名为指数，取负。
**类型**：行业中性化 + 价格结构

---

## Alpha#68
```
((Ts_Rank(correlation(rank(high), rank(adv15), 8.92), 13.93)
< rank(delta(((close * 0.518) + (low * 0.482)), 1.06))) * -1)
```
**逻辑**：最高价排名与 15 日均量排名相关性的时序排名 < 加权价格 1 日变化排名，取负。
**类型**：量价关系

---

## Alpha#69
```
((rank(ts_max(delta(IndNeutralize(vwap, IndClass.industry), 2.72), 4.79))
^Ts_Rank(correlation(((close * 0.491) + (vwap * 0.509)), adv20, 4.92), 9.06)) * -1)
```
**逻辑**：行业中性化 VWAP 变化最大值排名，以加权价格与均量相关性时序排名为指数，取负。
**类型**：行业中性化 + 量价

---

## Alpha#70
```
((rank(delta(vwap, 1.29))^Ts_Rank(correlation(IndNeutralize(close, IndClass.industry), adv50, 17.83), 17.92)) * -1)
```
**逻辑**：VWAP 变化排名，以行业中性化收盘价与 50 日均量相关性时序排名为指数，取负。
**类型**：行业中性化 + 量价

---

## Alpha#71
```
max(Ts_Rank(decay_linear(correlation(Ts_Rank(close, 3.44), Ts_Rank(adv180, 12.06), 18.02), 4.21), 15.69),
Ts_Rank(decay_linear((rank(((low + open) - (vwap + vwap)))^2), 16.47), 4.44))
```
**逻辑**：两个时序排名取最大值：收盘价时序排名与均量时序排名相关性的线性衰减，以及低价+开盘价偏离 $2\times VWAP$ 的平方线性衰减。
**类型**：多因子最大值

---

## Alpha#72
```
rank(decay_linear(correlation(((high + low) / 2), adv40, 8.93), 10.15))
/ rank(decay_linear(correlation(Ts_Rank(vwap, 3.72), Ts_Rank(volume, 18.52), 6.87), 2.95))
```
**逻辑**：中间价与 40 日均量相关性的线性衰减排名，除以 VWAP 时序排名与成交量时序排名相关性的线性衰减排名。
**类型**：量价比率

---

## Alpha#73
```
(max(rank(decay_linear(delta(vwap, 4.73), 2.92)),
Ts_Rank(decay_linear(((delta(((open * 0.147) + (low * 0.853)), 2.04) /
((open * 0.147) + (low * 0.853))) * -1), 3.34), 16.74)) * -1)
```
**逻辑**：VWAP 变化线性衰减排名 与 加权价格变化率取负的线性衰减时序排名，取最大值后取负。
**类型**：价格变化

---

## Alpha#74
```
((rank(correlation(close, sum(adv30, 37.48), 15.14))
< rank(correlation(rank(((high * 0.0262) + (vwap * 0.9738))), rank(volume), 11.48))) * -1)
```
**逻辑**：收盘价与 30 日均量相关性排名 < 加权价格排名与成交量排名相关性排名，取负。
**类型**：量价关系

---

## Alpha#75
```
rank(correlation(vwap, volume, 4.24)) < rank(correlation(rank(low), rank(adv50), 12.44))
```
**逻辑**：VWAP 与成交量 4 日相关性排名 < 最低价排名与 50 日均量排名 12 日相关性排名，返回布尔值。
**类型**：量价关系

---

← [[101公式化Alpha - Alpha#26到#50]] | [[101公式化Alpha - Alpha#76到#101]] →

# 00-67 执行记录

## 1. 当前状态

- 已基于 `00-66` 明确当前问题不是颜色字段未保存，而是颜色语义与主题事实源未对齐
- 本轮尚未开始实现，先固化修复边界

## 2. 本轮执行入口

- 优先确定公开页主题事实源是否直接收口到 `/api/card/personalization.theme`
- 再调整 `pages/actor-profile/detail` 与 `pkg-card/actor-card/index` 的颜色消费

## 3. 待补证据

- `/api/card/config` 保存样本
- `/api/card/personalization` 聚合样本
- 修复前后公开页对比图

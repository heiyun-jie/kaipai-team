# 00-87 设计说明

## 1. 设计目标

`00-87` 只解决 `operate/actions` 下方治理动态区：

1. **ledger shell**：从厚卡片收成更轻的台账壳层
2. **row semantics**：让真实 `recentItems` 有更明确的列式表达
3. **empty discipline**：空态也保持 ledger 感，不回退为大空盒

## 2. 已核实的事实

### 2.1 当前问题集中在治理动态区

真实浏览器量化：

- 截图：`D:\XM\kaipai-team\output\playwright\00-87\operate-actions-governance-before.png`
- 整卡尺寸：`1134 × 279`
- 标题顶部：`y ≈ 805`
- 空态高度：`158px`
- 当前 `recentItems` 为空

### 2.2 不能照搬 reference campaign 字段

reference 下半区使用了：

- 活动名
- 状态
- 触达
- 增长率
- 时间范围
- 报告按钮

当前真实 `recentItems` 只有：

- `bizLine`
- `itemType`
- `title`
- `status`
- `occurredAt`
- `referenceNo`
- `userId`

因此本轮只能借 reference 的“轻量台账结构”，不能伪造 campaign 字段。

## 3. 设计策略

### 3.1 改为 ledger 容器

在当前 `table-card` 内部改为：

- 轻量表头
- ledger 列头
- ledger 行
- 或 ledger 空态行

### 3.2 列定义

优先列：

1. 动态
2. 业务线
3. 状态
4. 发生时间
5. 处理

其中：

- 动态列承接标题 + 参考号 / 用户号摘要
- 处理列继续保留真实跳转按钮

### 3.3 空态

空态不再用大块 `table-empty` 盒子，而改为：

- 保留列头
- 一条跨列空态行
- 更轻的高度与间距

## 4. 风险与边界

### 4.1 已确认

- 当前是 `ActionsView.vue` 的区块级问题
- 不需要改共享 `table-card` 基线
- 不应扩到动作推荐区

### 4.2 待验证

- 空态改为 ledger 行后是否仍足够可读
- 将来 `recentItems` 非空时是否仍能稳定表达

因此本轮必须结合：

- 浏览器截图
- 运行态量化
- `type-check / build`

一起验证。

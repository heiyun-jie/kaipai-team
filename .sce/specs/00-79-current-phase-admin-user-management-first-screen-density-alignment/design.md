# 00-79 设计说明

## 1. 设计目标

`00-79` 只解决 `users/index` 首屏本身：

1. **overview row**：恢复单行 4 KPI
2. **segment density**：压缩 segment + 快筛区
3. **filter density**：压缩高级筛选区，但不改变真实筛选能力

## 2. 已核实的事实

### 2.1 当前问题仍然是 page-level

已通过真实浏览器 computed style 核实：

- `.user-overview` 当前仍是 3 列
- 这和 dashboard 在 `00-76` 开始前的情况一致

这意味着：

- `UserCenterView.vue` 当前同样被共享 `page-overview` 规则压住
- 但当前证据只覆盖用户管理页
- 所以不能直接修改全局 `page-overview`

### 2.2 当前筛选区仍偏厚

当前运行态截图已确认：

- segment / 快筛是独立厚卡
- `FilterPanel` 的 header、间距和控件高度使首屏占高偏大

但这些问题仍然只需要用户管理页局部覆盖，不需要去动全局 `FilterPanel.vue`。

## 3. 设计策略

### 3.1 只改 `UserCenterView.vue`

本轮只允许修改：

- `D:\XM\kaipai-team\kaipai-admin\src\views\user\UserCenterView.vue`

不改：

- `src/styles/index.scss`
- `src/components/business/FilterPanel.vue`
- 共享顶控

### 3.2 KPI 区

对 `.user-overview` 做本地高优先级覆盖：

- 桌面下改成 4 列
- gap 收紧
- 概览卡高度和 padding 收紧

### 3.3 segment / 快筛区

对 `.user-shell-card` 做局部压缩：

- toolbar gap 收紧
- segment 按钮高度、padding 收紧
- 快筛输入与按钮尺寸收紧

### 3.4 筛选区

为 `FilterPanel` 增加用户页局部 class 覆盖：

- card body padding 收紧
- header margin / padding-bottom 收紧
- 表单 gap 收紧
- 输入框最小高度收紧

但：

- 字段、交互、筛选能力保持不变

## 4. 风险与边界

### 4.1 已确认

- 当前改动只涉及用户管理页局部结构与样式
- 风险低、可逆
- 不影响后端与事实源

### 4.2 待验证

- KPI 收成 4 列后，说明文案是否会再次把卡片拉高
- 筛选区压缩后，控件可读性是否仍足够

因此本轮必须通过真实浏览器再复核一次。

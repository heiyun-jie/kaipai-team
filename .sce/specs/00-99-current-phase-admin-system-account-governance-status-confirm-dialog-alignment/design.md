# 00-99 设计说明

## 1. 设计目标

`00-99` 只解决 `system/admin-users` 的启用 / 禁用确认弹窗密度：

1. **dialog shell**：收紧 header、body、footer 与关闭按钮
2. **intro and meta**：收紧引导说明区与 meta 列表
3. **reason area**：收紧 textarea 与底部 tip，但保持必填原因可读

## 2. 已核实的事实

### 2.1 当前剩余问题已收窄到状态确认弹窗

真实运行态截图：

- current：`D:\XM\kaipai-team\output\playwright\00-99\admin-users-status-before.png`

当前量化：

- 弹窗：`520 × 716`
- header：`67px`
- body：`540px`
- footer：`75px`
- intro：`117px`
- meta：`434 × 204`
- meta item：`45px`
- textarea：`434 × 96`

这说明当前 residual 已不在首屏、主表、详情抽屉和维护弹窗，而在 `AuditConfirmDialog` 的当前页呈现。

### 2.2 当前厚度主要来自三处

1. 共享 `AuditConfirmDialog` 的 dialog-content gap 偏大
2. `dialog-intro` 与 `dialog-meta` 节奏偏厚
3. textarea 与 footer 占高偏大

### 2.3 当前组件有多处复用

`AuditConfirmDialog` 已被 `verify / refund / referral / content / recruit / system` 多处复用。

因此本轮不能直接把所有页面都一起改薄；必须：

- 为组件增加**可选**局部扩展入口
- 只在 `AdminUsersView.vue` 当前调用点启用

## 3. 设计策略

### 3.1 为组件增加可选局部 class / width

在 `AuditConfirmDialog.vue` 中增加可选参数：

- `dialogClass`
- `width`

默认值保持当前行为不变，避免影响其它页面。

### 3.2 当前页调用点局部启用

在 `AdminUsersView.vue` 的启停用确认弹窗调用点补本地 class：

- `admin-users-status-dialog`

并使用本地 scoped `:deep()` 只覆盖当前页的：

- `el-dialog__header`
- `el-dialog__body`
- `el-dialog__footer`
- `dialog-intro`
- `dialog-meta`
- `dialog-tip`
- `el-textarea__inner`

### 3.3 只做视觉密度

本轮不改：

- meta 字段集合
- reason 必填逻辑
- 提交与关闭行为

## 4. 风险与边界

### 4.1 已确认

- 当前改动只涉及 `AdminUsersView.vue` 的状态确认弹窗视觉密度
- 对其它使用 `AuditConfirmDialog` 的页面默认行为无影响
- 风险低、可逆

### 4.2 待验证

- 收紧后 meta 区是否仍清晰
- textarea 高度收紧后是否仍可填写较长原因
- 局部 class 是否稳定作用于 teleport 后的弹窗

因此本轮必须结合：

- 运行态量化
- 浏览器截图
- `type-check / build`

一起验证。
